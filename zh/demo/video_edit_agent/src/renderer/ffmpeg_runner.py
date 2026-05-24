import subprocess
import os
from typing import Optional


class FFmpegRunner:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def trim_clip(self, input_path: str, output_path: str, start: float, duration: float, speed: float = 1.0):
        filters = []
        if speed != 1.0:
            setpts = 1.0 / speed
            filters.append(f"setpts={setpts}*PTS")

        cmd = [self.ffmpeg_path, "-y", "-ss", str(start), "-i", input_path, "-t", str(duration)]
        if filters:
            cmd.extend(["-vf", ",".join(filters)])
        cmd.extend(["-an", output_path])
        subprocess.run(cmd, check=True, capture_output=True)

    def concat_clips(self, clip_list_path: str, output_path: str):
        cmd = [
            self.ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
            "-i", clip_list_path, "-c", "copy", output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def add_audio(self, video_path: str, audio_path: str, output_path: str, volume: float = 1.0):
        cmd = [
            self.ffmpeg_path, "-y", "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac",
            "-filter:a", f"volume={volume}",
            "-shortest", output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def get_duration(self, file_path: str) -> float:
        cmd = [self.ffmpeg_path, "-i", file_path, "-f", "null", "-"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return 0.0
