#!/usr/bin/env python3
"""Demo script: generates test videos and runs the full editing pipeline.

Usage:
    python demo.py

This creates synthetic test videos, evaluates them, builds a clip instruction,
and renders the final output — all without needing an LLM API key.
"""

import os
import sys
import yaml
import tempfile
import numpy as np


def generate_test_videos(output_dir: str, count: int = 5):
    """Generate synthetic test videos with moviepy."""
    try:
        from moviepy import VideoClip
    except ImportError:
        from moviepy.video.VideoClip import VideoClip

    os.makedirs(output_dir, exist_ok=True)
    paths = []

    for i in range(count):
        path = os.path.join(output_dir, f"demo_clip_{i:03d}.mp4")
        if os.path.exists(path):
            paths.append(path)
            continue

        # Create a clip with varying color/brightness to simulate different scenes
        base_color = 80 + i * 30
        clip = VideoClip(
            frame_function=lambda t, c=base_color: np.ones((360, 640, 3), dtype=np.uint8) * c,
            duration=2 + i * 0.5,  # varying durations: 2s, 2.5s, 3s, 3.5s, 4s
        )
        try:
            clip.write_videofile(path, fps=24, logger=None)
            paths.append(path)
        except Exception as e:
            print(f"  Warning: Could not create {path}: {e}")
        finally:
            clip.close()

    return paths


def main():
    print("=" * 60)
    print("  Video Editing Agent — Demo")
    print("=" * 60)

    work_dir = os.path.join(tempfile.gettempdir(), "vedit_demo")
    source_dir = os.path.join(work_dir, "sources")
    material_dir = os.path.join(work_dir, "materials")
    output_dir = os.path.join(work_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Generate test videos
    print("\n[1/4] Generating test videos...")
    video_paths = generate_test_videos(source_dir, count=5)
    print(f"  Created {len(video_paths)} test videos in {source_dir}")

    # Step 2: Evaluate materials
    print("\n[2/4] Evaluating materials...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from src.evaluator.scene_splitter import SceneSplitter
    from src.evaluator.quality_assessor import QualityAssessor
    from src.evaluator.tag_extractor import TagExtractor
    from src.analyzer.frame_extractor import FrameExtractor
    from src.protocol.material_lib import MaterialLib, MaterialClip

    splitter = SceneSplitter()
    assessor = QualityAssessor()
    tagger = TagExtractor()
    extractor = FrameExtractor()

    all_clips = []
    for vp in video_paths:
        scenes = [{"index": 0, "start": 0.0, "end": 1.5, "duration": 1.5}]
        for scene in scenes:
            try:
                frames = extractor.extract_scene_frames(vp)[:5]
            except Exception:
                frames = [np.zeros((360, 640, 3), dtype=np.uint8)]

            quality = assessor.assess(frames)
            tags = tagger.extract(frames, {"duration": scene["duration"], "fps": 24})

            clip = MaterialClip(
                clip_id=os.path.splitext(os.path.basename(vp))[0],
                source=os.path.abspath(vp),
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
    os.makedirs(material_dir, exist_ok=True)
    lib_path = os.path.join(material_dir, "material_lib.yaml")
    with open(lib_path, "w", encoding="utf-8") as f:
        yaml.dump(lib.to_dict_list(), f, allow_unicode=True)
    print(f"  Evaluated {len(all_clips)} clips -> {lib_path}")

    # Step 3: Build clip instruction (no LLM — manual assembly)
    print("\n[3/4] Building clip instruction...")
    from src.protocol.clip_instruction import ClipInstruction, PreciseClip

    instruction = ClipInstruction()
    for i, clip in enumerate(all_clips):
        instruction.precise_clips.append(
            PreciseClip(
                clip_id=f"c_{i:03d}",
                source_file=clip.source,
                in_point=clip.in_point,
                out_point=clip.out_point,
                speed=0.8 + i * 0.1,  # slight speed variations
                transition_in="cut" if i == 0 else "whip_pan_right",
                transition_out="cut" if i == len(all_clips) - 1 else "whip_pan_right",
            )
        )
    print(f"  Created {len(instruction.precise_clips)} clips in instruction")

    # Step 4: Render
    print("\n[4/4] Rendering final video...")
    output_path = os.path.join(output_dir, "demo_vlog.mp4")
    instruction.output_path = output_path

    from src.renderer.composer import Composer
    composer = Composer(work_dir=os.path.join(work_dir, "temp"))
    composer.compose(instruction)

    file_size = os.path.getsize(output_path)
    print(f"  Output: {output_path}")
    print(f"  Size: {file_size / 1024:.1f} KB")
    print("\n" + "=" * 60)
    print("  DEMO COMPLETE!")
    print(f"  Open {output_path} to view the result.")
    print("=" * 60)


if __name__ == "__main__":
    main()
