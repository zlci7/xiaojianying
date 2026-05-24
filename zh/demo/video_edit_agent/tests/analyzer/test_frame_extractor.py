import os
import pytest
import numpy as np
from src.analyzer.frame_extractor import FrameExtractor


class TestFrameExtractor:
    @pytest.fixture
    def sample_video(self, tmp_path):
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip

        video_path = str(tmp_path / "test.mp4")
        try:
            clip = VideoClip(frame_function=lambda t: np.zeros((240, 320, 3), dtype=np.uint8), duration=3)
            clip.write_videofile(video_path, fps=24, logger=None)
            clip.close()
        except Exception:
            pytest.skip("FFmpeg not available")
        return video_path

    def test_extract_scene_frames(self, sample_video):
        extractor = FrameExtractor(sample_frames_per_scene=5)
        frames = extractor.extract_scene_frames(sample_video)
        assert len(frames) > 0
        for frame in frames:
            assert isinstance(frame, np.ndarray)

    def test_get_video_metadata(self, sample_video):
        extractor = FrameExtractor()
        meta = extractor.get_metadata(sample_video)
        assert "duration" in meta
        assert "fps" in meta
        assert meta["duration"] > 0
