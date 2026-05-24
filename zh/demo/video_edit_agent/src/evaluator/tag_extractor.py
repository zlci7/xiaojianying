import numpy as np


class TagExtractor:
    def extract(self, frames: list, metadata: dict) -> dict:
        return {
            "shot_type": self._classify_shot_type(frames),
            "content_tags": self._extract_content_tags(frames),
            "motion": self._detect_motion(frames),
            "aesthetic_score": self._score_aesthetics(frames),
            "style_route_suggestion": "cinematic" if metadata.get("duration", 0) > 5 else "authentic",
        }

    def _classify_shot_type(self, frames: list) -> str:
        motion = self._detect_motion(frames)
        if motion["speed"] == "static":
            return "static"
        elif motion["speed"] == "fast":
            return "panning"
        elif motion["direction"] in ["zoom_in", "zoom_out"]:
            return "push_in"
        else:
            return "handheld"

    def _extract_content_tags(self, frames: list) -> list:
        if not frames:
            return ["unknown"]
        avg_brightness = np.mean([np.mean(f) for f in frames])
        color_std = np.mean([np.std(f) for f in frames])
        tags = []
        if avg_brightness > 150:
            tags.append("bright_scene")
        elif avg_brightness < 80:
            tags.append("dark_scene")
        if color_std > 50:
            tags.append("vivid_colors")
        tags.append("general")
        return tags

    def _detect_motion(self, frames: list) -> dict:
        if len(frames) < 2:
            return {"direction": "static", "speed": "static"}
        diffs = []
        for i in range(1, len(frames)):
            diff = np.mean(np.abs(
                frames[i].astype(np.float32) - frames[i - 1].astype(np.float32)
            ))
            diffs.append(diff)
        avg_diff = np.mean(diffs) if diffs else 0
        if avg_diff < 5:
            speed = "static"
        elif avg_diff < 15:
            speed = "slow"
        elif avg_diff < 30:
            speed = "medium"
        else:
            speed = "fast"
        return {"direction": "unknown", "speed": speed}

    def _score_aesthetics(self, frames: list) -> int:
        if not frames:
            return 5
        brightness_ok = 50 < np.mean([np.mean(f) for f in frames]) < 200
        has_variation = np.mean([np.std(f) for f in frames]) > 20
        score = 5
        if brightness_ok:
            score += 2
        if has_variation:
            score += 2
        return min(10, score)
