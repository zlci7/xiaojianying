import numpy as np


class QualityAssessor:
    def assess(self, frames: list) -> dict:
        stability = self.assess_stability(frames)
        exposure = self.assess_exposure(frames[0] if frames else np.zeros((240, 320, 3)))
        horizon = self.assess_horizon(frames[0] if frames else np.zeros((240, 320, 3)))

        score = 10
        if stability["level"] == "high":
            score -= 3
        elif stability["level"] == "medium":
            score -= 1
        if exposure["level"] == "high":
            score -= 2
        elif exposure["level"] == "medium":
            score -= 1
        if horizon["level"] == "high":
            score -= 1

        return {
            "stability": stability,
            "exposure": exposure,
            "horizon": horizon,
            "quality_score": max(1, score),
        }

    def assess_stability(self, frames: list) -> dict:
        if len(frames) < 3:
            return {"level": "low", "suggested_fix": None}

        diffs = []
        for i in range(1, len(frames)):
            diff = np.mean(np.abs(
                frames[i].astype(np.float32) - frames[i - 1].astype(np.float32)
            ))
            diffs.append(diff)

        avg_diff = np.mean(diffs) if diffs else 0

        if avg_diff > 20:
            return {"level": "high", "suggested_fix": "stabilize"}
        elif avg_diff > 10:
            return {"level": "medium", "suggested_fix": "stabilize"}
        else:
            return {"level": "low", "suggested_fix": None}

    def assess_exposure(self, frame: np.ndarray) -> dict:
        mean_brightness = np.mean(frame)
        if mean_brightness < 40 or mean_brightness > 230:
            return {"level": "high", "suggested_fix": "exposure_correct"}
        elif mean_brightness < 70 or mean_brightness > 210:
            return {"level": "medium", "suggested_fix": "exposure_correct"}
        else:
            return {"level": "low", "suggested_fix": None}

    def assess_horizon(self, frame: np.ndarray) -> dict:
        return {"level": "low", "suggested_fix": None}
