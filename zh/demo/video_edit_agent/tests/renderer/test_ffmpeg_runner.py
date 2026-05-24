from src.renderer.ffmpeg_runner import FFmpegRunner

class TestFFmpegRunner:
    def test_init(self):
        runner = FFmpegRunner()
        assert runner.ffmpeg_path == "ffmpeg"

    def test_custom_path(self):
        runner = FFmpegRunner(ffmpeg_path="/usr/local/bin/ffmpeg")
        assert runner.ffmpeg_path == "/usr/local/bin/ffmpeg"
