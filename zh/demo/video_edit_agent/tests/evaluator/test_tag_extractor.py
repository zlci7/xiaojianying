import numpy as np
from src.evaluator.tag_extractor import TagExtractor

class TestTagExtractor:
    def test_extract_tags(self):
        extractor = TagExtractor()
        frames = [np.ones((240, 320, 3), dtype=np.uint8) * 120 for _ in range(5)]
        metadata = {"duration": 5.0, "fps": 24}
        tags = extractor.extract(frames, metadata)
        assert "shot_type" in tags
        assert "content_tags" in tags
        assert "motion" in tags
        assert isinstance(tags["content_tags"], list)

    def test_detect_motion_static(self):
        extractor = TagExtractor()
        static_frames = [np.ones((240, 320, 3), dtype=np.uint8) * 100 for _ in range(5)]
        motion = extractor._detect_motion(static_frames)
        assert motion["speed"] == "static"
