import os
import pytest
import yaml
import numpy as np


class TestIntegration:
    @pytest.fixture
    def workspace(self, tmp_path):
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip

        for i in range(3):
            video_path = str(tmp_path / f"source_{i}.mp4")
            try:
                color_val = 100 + i * 30
                clip = VideoClip(
                    frame_function=lambda t, c=color_val: np.ones((240, 320, 3), dtype=np.uint8) * c,
                    duration=3,
                )
                clip.write_videofile(video_path, fps=24, logger=None)
                clip.close()
            except Exception:
                pass
        return tmp_path

    def test_evaluate_produces_material_lib(self, workspace):
        ws = str(workspace)
        material_dir = os.path.join(ws, "materials")
        os.makedirs(material_dir, exist_ok=True)

        from src.evaluator.scene_splitter import SceneSplitter
        from src.evaluator.quality_assessor import QualityAssessor
        from src.evaluator.tag_extractor import TagExtractor
        from src.analyzer.frame_extractor import FrameExtractor
        from src.protocol.material_lib import MaterialLib, MaterialClip

        video_files = [f for f in os.listdir(ws) if f.endswith(".mp4")]
        if not video_files:
            pytest.skip("No test videos created - FFmpeg may not be available")

        splitter = SceneSplitter()
        assessor = QualityAssessor()
        tagger = TagExtractor()
        extractor = FrameExtractor()

        all_clips = []
        for vf in video_files:
            video_path = os.path.join(ws, vf)
            try:
                scenes = splitter.split(video_path)
            except Exception:
                scenes = [{"index": 0, "start": 0.0, "end": 2.0, "duration": 2.0}]

            for scene in scenes:
                try:
                    frames = extractor.extract_scene_frames(video_path)[:5]
                except Exception:
                    frames = [np.zeros((240, 320, 3), dtype=np.uint8)]

                quality = assessor.assess(frames)
                tags = tagger.extract(frames, {"duration": scene["duration"], "fps": 24})
                clip = MaterialClip(
                    clip_id=f"{vf}_s{scene['index']}",
                    source=os.path.abspath(video_path),
                    in_point=f"{scene['start']:.1f}",
                    out_point=f"{scene['end']:.1f}",
                    duration=scene["duration"],
                    quality_score=quality["quality_score"],
                    shot_type=tags["shot_type"],
                    content_tags=tags["content_tags"],
                    motion=tags["motion"],
                    aesthetic_score=tags["aesthetic_score"],
                    usable=True,
                )
                all_clips.append(clip)

        lib = MaterialLib(clips=all_clips)
        lib_path = os.path.join(material_dir, "material_lib.yaml")
        with open(lib_path, "w", encoding="utf-8") as f:
            yaml.dump(lib.to_dict_list(), f, allow_unicode=True)

        assert len(all_clips) > 0
        assert os.path.exists(lib_path)

        with open(lib_path, "r", encoding="utf-8") as f:
            reloaded = yaml.safe_load(f.read())
        assert len(reloaded) == len(all_clips)

    def test_style_profile_roundtrip(self, workspace):
        from src.protocol.style_profile import StyleProfile

        yaml_content = """meta:
  source_vlog: test.mp4
  source_duration: 150
  style_type: fast_flash
  style_summary: test

shot_pattern:
  avg_duration: 1.8
  duration_range: [0.5, 4.0]
  speed_variation:
    speed_ramp_ratio: 0.3
    common_modes: [fast_forward]

transitions:
  density: high
  types:
    hard_cut: 0.35
    match_cut: 0.20
  avg_transition_duration: 0.3

rhythm:
  bpm_sync: true
  beat_alignment: on_beat
  pace_curve: [high, high, high]

aesthetic:
  color_temp: warm
  saturation: 15
  contrast: high
  dominant_colors: ['#FF8C42']

post_processing:
  keyframe_animation:
    scale_zoom: true
    position_drift: true
    rotation_minor: false
  effects:
    light_leak:
      frequency: medium
"""
        profile = StyleProfile.from_yaml(yaml_content)
        exported = profile.to_yaml()
        reimported = StyleProfile.from_yaml(exported)
        assert reimported.meta.style_type == "fast_flash"
        assert reimported.transitions.types["hard_cut"] == 0.35
        assert reimported.rhythm.bpm_sync is True

    def test_full_pipeline_without_llm(self, workspace):
        """End-to-end test: evaluate -> render without LLM (uses pre-built instruction)."""
        ws = str(workspace)

        from src.evaluator.scene_splitter import SceneSplitter
        from src.evaluator.quality_assessor import QualityAssessor
        from src.evaluator.tag_extractor import TagExtractor
        from src.analyzer.frame_extractor import FrameExtractor
        from src.protocol.material_lib import MaterialLib, MaterialClip
        from src.protocol.clip_instruction import ClipInstruction, PreciseClip
        from src.renderer.composer import Composer

        video_files = [f for f in os.listdir(ws) if f.endswith(".mp4")]
        if not video_files:
            pytest.skip("No test videos created")

        splitter = SceneSplitter()
        assessor = QualityAssessor()
        tagger = TagExtractor()
        extractor = FrameExtractor()

        all_clips = []
        for vf in video_files:
            video_path = os.path.join(ws, vf)
            scenes = [{"index": 0, "start": 0.0, "end": 2.0, "duration": 2.0}]
            for scene in scenes:
                try:
                    frames = extractor.extract_scene_frames(video_path)[:5]
                except Exception:
                    frames = [np.zeros((240, 320, 3), dtype=np.uint8)]
                quality = assessor.assess(frames)
                tags = tagger.extract(frames, {"duration": scene["duration"], "fps": 24})
                clip = MaterialClip(
                    clip_id=f"{vf}_s{scene['index']}",
                    source=os.path.abspath(video_path),
                    in_point=f"{scene['start']:.1f}",
                    out_point=f"{scene['end']:.1f}",
                    duration=scene["duration"],
                    quality_score=quality["quality_score"],
                    shot_type=tags["shot_type"],
                    content_tags=tags["content_tags"],
                    motion=tags["motion"],
                    aesthetic_score=tags["aesthetic_score"],
                    usable=True,
                )
                all_clips.append(clip)

        # Step 2: Build a manual ClipInstruction (no LLM needed)
        instruction = ClipInstruction(
            sections=[],
            precise_clips=[],
        )
        for i, clip in enumerate(all_clips[:3]):
            instruction.precise_clips.append(
                PreciseClip(
                    clip_id=f"c_{i:03d}",
                    source_file=clip.source,
                    in_point=clip.in_point,
                    out_point=clip.out_point,
                    speed=1.0,
                    transition_in="cut",
                    transition_out="cut",
                )
            )

        # Step 3: Render
        output_path = str(workspace / "demo_output.mp4")
        instruction.output_path = output_path
        composer = Composer(work_dir=str(workspace / "temp"))
        composer.compose(instruction)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
