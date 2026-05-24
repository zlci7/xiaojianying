import os
import pytest
import numpy as np
from src.renderer.composer import Composer
from src.protocol.clip_instruction import ClipInstruction, PreciseClip

class TestComposer:
    @pytest.fixture
    def sample_video(self, tmp_path):
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip
        video_path = str(tmp_path / "source.mp4")
        try:
            clip = VideoClip(frame_function=lambda t: np.zeros((240, 320, 3), dtype=np.uint8), duration=3)
            clip.write_videofile(video_path, fps=24, logger=None)
            clip.close()
        except Exception:
            pytest.skip("FFmpeg not available")
        return video_path

    def test_time_to_seconds(self):
        assert Composer._time_to_seconds("00:01.5") == 1.5
        assert Composer._time_to_seconds("1.5") == 1.5
        assert Composer._time_to_seconds("00:01:00.0") == 60.0

    def test_build_clip_list(self, sample_video):
        composer = Composer()
        instruction = ClipInstruction(
            precise_clips=[
                PreciseClip(
                    clip_id="c_001",
                    source_file=sample_video,
                    in_point="00:00.0",
                    out_point="00:01.0",
                    speed=1.0,
                    transition_in="cut",
                    transition_out="cut",
                )
            ],
        )
        clip_list = composer._build_clip_list(instruction)
        assert len(clip_list) == 1
        assert clip_list[0]["source"] == sample_video

    def test_compose_creates_output(self, sample_video, tmp_path):
        composer = Composer(work_dir=str(tmp_path))
        output_path = str(tmp_path / "output.mp4")
        instruction = ClipInstruction(
            precise_clips=[
                PreciseClip(
                    clip_id="c_001",
                    source_file=sample_video,
                    in_point="00:00.0",
                    out_point="00:00.5",
                    speed=1.0,
                    transition_in="cut",
                    transition_out="cut",
                )
            ],
            output_path=output_path,
        )
        composer.compose(instruction)
        assert os.path.exists(output_path)
