import os
import numpy as np

try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip


class FrameExtractor:
    def __init__(self, sample_frames_per_scene: int = 10):
        self.sample_frames_per_scene = sample_frames_per_scene

    def extract_scene_frames(self, video_path: str) -> list:
        clip = None
        frames = []
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            interval = max(0.5, duration / (self.sample_frames_per_scene * 2))

            t = 0.0
            while t < duration:
                frame = clip.get_frame(t)
                frames.append(frame)
                t += interval

            return frames
        finally:
            if clip:
                clip.close()

    def get_metadata(self, video_path: str) -> dict:
        clip = None
        try:
            clip = VideoFileClip(video_path)
            return {
                "duration": clip.duration,
                "fps": clip.fps,
                "width": clip.w,
                "height": clip.h,
                "filename": os.path.basename(video_path),
            }
        finally:
            if clip:
                clip.close()

    def extract_keyframe_at_time(self, video_path: str, time_sec: float):
        clip = None
        try:
            clip = VideoFileClip(video_path)
            return clip.get_frame(time_sec)
        finally:
            if clip:
                clip.close()
