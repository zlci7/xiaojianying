import os
import tempfile

try:
    from moviepy import VideoFileClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import VideoFileClip, concatenate_videoclips

from src.protocol.clip_instruction import ClipInstruction
from src.renderer.ffmpeg_runner import FFmpegRunner


class Composer:
    def __init__(self, work_dir: str = None):
        self.work_dir = work_dir or tempfile.mkdtemp()
        self.ffmpeg = FFmpegRunner()
        os.makedirs(self.work_dir, exist_ok=True)

    def compose(self, instruction: ClipInstruction):
        clip_list = self._build_clip_list(instruction)
        if not clip_list:
            raise ValueError("No clips to compose")

        processed_clips = []
        try:
            for i, clip_info in enumerate(clip_list):
                processed = self._process_clip(clip_info, i)
                processed_clips.append(processed)

            if not processed_clips:
                raise ValueError("No clips could be processed")

            final = concatenate_videoclips(processed_clips)

            if instruction.bgm_file and os.path.exists(instruction.bgm_file):
                try:
                    from moviepy import AudioFileClip
                    audio_clip = AudioFileClip(instruction.bgm_file)
                    if audio_clip.duration > final.duration:
                        audio_clip = audio_clip.subclipped(0, final.duration)
                    final = final.with_audio(audio_clip)
                except Exception:
                    pass

            final.write_videofile(
                instruction.output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None,
            )
        finally:
            for clip in processed_clips:
                try:
                    clip.close()
                except Exception:
                    pass
            try:
                final.close()
            except Exception:
                pass

    def _build_clip_list(self, instruction: ClipInstruction) -> list:
        clips = []
        for pclip in instruction.precise_clips:
            in_sec = self._time_to_seconds(pclip.in_point)
            out_sec = self._time_to_seconds(pclip.out_point)
            clips.append({
                "source": pclip.source_file,
                "start": in_sec,
                "duration": out_sec - in_sec,
                "speed": pclip.speed,
                "transition_in": pclip.transition_in,
                "transition_out": pclip.transition_out,
            })
        return clips

    def _process_clip(self, clip_info: dict, index: int):
        source_clip = VideoFileClip(clip_info["source"])
        sub = source_clip.subclipped(clip_info["start"], clip_info["start"] + clip_info["duration"])

        if clip_info.get("speed", 1.0) != 1.0:
            sub = sub.with_speed_scaled(clip_info["speed"])

        sub = sub.resized(width=1920)
        return sub

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        parts = time_str.split(":")
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(parts[0])
