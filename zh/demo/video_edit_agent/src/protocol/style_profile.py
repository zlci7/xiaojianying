from dataclasses import dataclass, field, asdict
from typing import Optional
import yaml


@dataclass
class SpeedVariation:
    speed_ramp_ratio: float = 0.0
    common_modes: list = field(default_factory=list)


@dataclass
class ShotPattern:
    avg_duration: float = 0.0
    duration_range: list = field(default_factory=lambda: [1.0, 4.0])
    speed_variation: SpeedVariation = field(default_factory=SpeedVariation)


@dataclass
class Transitions:
    density: str = "medium"
    types: dict = field(default_factory=dict)
    avg_transition_duration: float = 0.3


@dataclass
class Rhythm:
    bpm_sync: bool = False
    beat_alignment: str = "on_beat"
    pace_curve: list = field(default_factory=list)


@dataclass
class Aesthetic:
    color_temp: str = "neutral"
    saturation: int = 0
    contrast: str = "medium"
    dominant_colors: list = field(default_factory=list)


@dataclass
class KeyframeAnimation:
    scale_zoom: bool = False
    position_drift: bool = False
    rotation_minor: bool = False


@dataclass
class PostProcessing:
    keyframe_animation: KeyframeAnimation = field(default_factory=KeyframeAnimation)
    effects: dict = field(default_factory=dict)


@dataclass
class Meta:
    source_vlog: str = ""
    source_duration: int = 0
    style_type: str = ""
    style_summary: str = ""


@dataclass
class StyleProfile:
    meta: Meta = field(default_factory=Meta)
    shot_pattern: ShotPattern = field(default_factory=ShotPattern)
    transitions: Transitions = field(default_factory=Transitions)
    rhythm: Rhythm = field(default_factory=Rhythm)
    aesthetic: Aesthetic = field(default_factory=Aesthetic)
    post_processing: PostProcessing = field(default_factory=PostProcessing)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "StyleProfile":
        data = yaml.safe_load(yaml_str)
        return cls._from_dict(data)

    def to_yaml(self) -> str:
        return yaml.dump(self._to_dict(), default_flow_style=False, allow_unicode=True)

    @classmethod
    def _from_dict(cls, data: dict) -> "StyleProfile":
        meta_data = data.get("meta", {})
        meta = Meta(
            source_vlog=meta_data.get("source_vlog", ""),
            source_duration=meta_data.get("source_duration", 0),
            style_type=meta_data.get("style_type", ""),
            style_summary=meta_data.get("style_summary", ""),
        )

        sp = data.get("shot_pattern", {})
        sv = sp.get("speed_variation", {})
        shot_pattern = ShotPattern(
            avg_duration=sp.get("avg_duration", 0.0),
            duration_range=sp.get("duration_range", [1.0, 4.0]),
            speed_variation=SpeedVariation(
                speed_ramp_ratio=sv.get("speed_ramp_ratio", 0.0),
                common_modes=sv.get("common_modes", []),
            ),
        )

        trans_data = data.get("transitions", {})
        transitions = Transitions(
            density=trans_data.get("density", "medium"),
            types=trans_data.get("types", {}),
            avg_transition_duration=trans_data.get("avg_transition_duration", 0.3),
        )

        rhythm_data = data.get("rhythm", {})
        rhythm = Rhythm(
            bpm_sync=rhythm_data.get("bpm_sync", False),
            beat_alignment=rhythm_data.get("beat_alignment", "on_beat"),
            pace_curve=rhythm_data.get("pace_curve", []),
        )

        aesthetic_data = data.get("aesthetic", {})
        aesthetic = Aesthetic(
            color_temp=aesthetic_data.get("color_temp", "neutral"),
            saturation=aesthetic_data.get("saturation", 0),
            contrast=aesthetic_data.get("contrast", "medium"),
            dominant_colors=aesthetic_data.get("dominant_colors", []),
        )

        pp = data.get("post_processing", {})
        kf = pp.get("keyframe_animation", {})
        post_processing = PostProcessing(
            keyframe_animation=KeyframeAnimation(
                scale_zoom=kf.get("scale_zoom", False),
                position_drift=kf.get("position_drift", False),
                rotation_minor=kf.get("rotation_minor", False),
            ),
            effects=pp.get("effects", {}),
        )

        return cls(
            meta=meta,
            shot_pattern=shot_pattern,
            transitions=transitions,
            rhythm=rhythm,
            aesthetic=aesthetic,
            post_processing=post_processing,
        )

    def _to_dict(self) -> dict:
        return {
            "meta": asdict(self.meta),
            "shot_pattern": {
                "avg_duration": self.shot_pattern.avg_duration,
                "duration_range": self.shot_pattern.duration_range,
                "speed_variation": asdict(self.shot_pattern.speed_variation),
            },
            "transitions": asdict(self.transitions),
            "rhythm": asdict(self.rhythm),
            "aesthetic": asdict(self.aesthetic),
            "post_processing": {
                "keyframe_animation": asdict(self.post_processing.keyframe_animation),
                "effects": self.post_processing.effects,
            },
        }
