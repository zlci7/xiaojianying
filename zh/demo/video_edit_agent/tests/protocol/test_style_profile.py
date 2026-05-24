import pytest
from src.protocol.style_profile import StyleProfile

SAMPLE_YAML = """
meta:
  source_vlog: "test.mp4"
  source_duration: 150
  style_type: fast_flash
  style_summary: "test style"

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
"""


class TestStyleProfile:
    def test_load_from_yaml(self):
        profile = StyleProfile.from_yaml(SAMPLE_YAML)
        assert profile.meta.source_vlog == "test.mp4"
        assert profile.meta.style_type == "fast_flash"
        assert profile.shot_pattern.avg_duration == 1.8
        assert profile.transitions.density == "high"
        assert profile.transitions.types["hard_cut"] == 0.35
        assert profile.rhythm.bpm_sync is True
        assert profile.aesthetic.color_temp == "warm"
        assert profile.post_processing.keyframe_animation.scale_zoom is True

    def test_to_yaml_roundtrip(self):
        profile = StyleProfile.from_yaml(SAMPLE_YAML)
        exported = profile.to_yaml()
        reimported = StyleProfile.from_yaml(exported)
        assert reimported.meta.source_vlog == profile.meta.source_vlog
        assert reimported.transitions.types == profile.transitions.types
