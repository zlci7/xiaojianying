import numpy as np

try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip


class SceneSplitter:
    def __init__(self, threshold: float = 30.0, min_scene_duration: float = 0.5):
        self.threshold = threshold
        self.min_scene_duration = min_scene_duration

    def split(self, video_path: str) -> list:
        clip = None
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration

            prev_frame = None
            cuts = [0.0]
            sample_interval = 0.5

            t = sample_interval
            while t < duration - self.min_scene_duration:
                frame = clip.get_frame(t)
                if prev_frame is not None:
                    diff = np.mean(np.abs(frame.astype(np.float32) - prev_frame.astype(np.float32)))
                    if diff > self.threshold:
                        if t - cuts[-1] >= self.min_scene_duration:
                            cuts.append(t)
                prev_frame = frame
                t += sample_interval

            cuts.append(duration)
            scenes = []
            for i in range(len(cuts) - 1):
                scenes.append({
                    "index": i,
                    "start": round(cuts[i], 2),
                    "end": round(cuts[i + 1], 2),
                    "duration": round(cuts[i + 1] - cuts[i], 2),
                })

            return scenes
        finally:
            if clip:
                clip.close()
