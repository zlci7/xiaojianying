import pytest
from src.analyzer.style_analyzer import StyleAnalyzer


class TestStyleAnalyzer:
    def test_build_analysis_prompt(self):
        analyzer = StyleAnalyzer(api_key="fake-key")
        prompt = analyzer._build_analysis_prompt({"duration": 120, "fps": 30})
        assert "120" in prompt or "duration" in prompt.lower()
        assert "fast_flash" in prompt.lower() or "vlog" in prompt.lower()

    def test_parse_valid_yaml_response(self):
        analyzer = StyleAnalyzer(api_key="fake-key")
        sample_response = """
```yaml
meta:
  source_vlog: "test.mp4"
  source_duration: 150
  style_type: fast_flash
  style_summary: "test"

shot_pattern:
  avg_duration: 1.8
  duration_range: [0.5, 4.0]
  speed_variation:
    speed_ramp_ratio: 0.3
    common_modes: ["fast_forward"]

transitions:
  density: high
  types:
    hard_cut: 0.35
    match_cut: 0.20
  avg_transition_duration: 0.3

rhythm:
  bpm_sync: true
  beat_alignment: on_beat
  pace_curve: [high, high, high]

aesthetic:
  color_temp: warm
  saturation: 15
  contrast: high
  dominant_colors: ["#FF8C42"]

post_processing:
  keyframe_animation:
    scale_zoom: true
    position_drift: true
    rotation_minor: false
  effects:
    light_leak: {frequency: medium}
```
"""
        profile = analyzer._parse_response(sample_response)
        assert profile is not None
        assert profile.meta.style_type == "fast_flash"
        assert profile.transitions.density == "high"

    def test_parse_invalid_response_returns_none(self):
        analyzer = StyleAnalyzer(api_key="fake-key")
        result = analyzer._parse_response("not a valid yaml response at all")
        assert result is None
