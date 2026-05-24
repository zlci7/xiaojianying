import pytest
import numpy as np
from src.evaluator.scene_splitter import SceneSplitter

class TestSceneSplitter:
    @pytest.fixture
    def sample_video(self, tmp_path):
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip
        video_path = str(tmp_path / "test_scene.mp4")
        try:
            clip = VideoClip(frame_function=lambda t: np.zeros((240, 320, 3), dtype=np.uint8), duration=2)
            clip.write_videofile(video_path, fps=24, logger=None)
            clip.close()
        except Exception:
            pytest.skip("FFmpeg not available")
        return video_path

    def test_split_scenes(self, sample_video):
        splitter = SceneSplitter(threshold=30.0, min_scene_duration=0.5)
        scenes = splitter.split(sample_video)
        assert len(scenes) >= 1
        for scene in scenes:
            assert "start" in scene
            assert "end" in scene
            assert "duration" in scene
            assert scene["duration"] > 0
