import numpy as np
from src.evaluator.quality_assessor import QualityAssessor

class TestQualityAssessor:
    def test_assess_stability_stable(self):
        assessor = QualityAssessor()
        stable_frames = [np.ones((240, 320, 3), dtype=np.uint8) * 100 for _ in range(5)]
        result = assessor.assess_stability(stable_frames)
        assert result["level"] == "low"

    def test_assess_exposure_normal(self):
        assessor = QualityAssessor()
        frame = np.ones((240, 320, 3), dtype=np.uint8) * 120
        result = assessor.assess_exposure(frame)
        assert result["level"] == "low"

    def test_assess_exposure_dark(self):
        assessor = QualityAssessor()
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        result = assessor.assess_exposure(frame)
        assert result["level"] == "high"
        assert result["suggested_fix"] == "exposure_correct"

    def test_full_assessment(self):
        assessor = QualityAssessor()
        frames = [np.ones((240, 320, 3), dtype=np.uint8) * 120 for _ in range(10)]
        result = assessor.assess(frames)
        assert "stability" in result
        assert "exposure" in result
        assert "quality_score" in result
        assert 1 <= result["quality_score"] <= 10
