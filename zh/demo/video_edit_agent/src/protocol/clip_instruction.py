from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MusicSync:
    mode: str = "beat_match"
    bpm: int = 120


@dataclass
class ShotConstraint:
    min_shot_count: int = 1
    max_shot_duration: float = 5.0
    preferred_types: list = field(default_factory=list)
    preferred_content: list = field(default_factory=list)


@dataclass
class Section:
    id: str = ""
    name: str = ""
    duration: float = 0.0
    rule_ref: str = ""
    mood: str = "neutral"
    music_sync: MusicSync = field(default_factory=MusicSync)
    shot_constraint: ShotConstraint = field(default_factory=ShotConstraint)
    transition_style: str = "medium"
    post_processing: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Section":
        ms = data.get("music_sync", {})
        sc = data.get("shot_constraint", {})
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            duration=data.get("duration", 0.0),
            rule_ref=data.get("rule_ref", ""),
            mood=data.get("mood", "neutral"),
            music_sync=MusicSync(
                mode=ms.get("mode", "beat_match"),
                bpm=ms.get("bpm", 120),
            ),
            shot_constraint=ShotConstraint(
                min_shot_count=sc.get("min_shot_count", 1),
                max_shot_duration=sc.get("max_shot_duration", 5.0),
                preferred_types=sc.get("preferred_types", []),
                preferred_content=sc.get("preferred_content", []),
            ),
            transition_style=data.get("transition_style", "medium"),
            post_processing=data.get("post_processing", {}),
        )


@dataclass
class PreciseClip:
    clip_id: str = ""
    source_file: str = ""
    in_point: str = "00:00.0"
    out_point: str = "00:00.0"
    speed: float = 1.0
    transition_in: str = "cut"
    transition_out: str = "cut"
    post_processing: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "PreciseClip":
        return cls(
            clip_id=data.get("clip_id", ""),
            source_file=data.get("source_file", ""),
            in_point=data.get("in", "00:00.0"),
            out_point=data.get("out", "00:00.0"),
            speed=data.get("speed", 1.0),
            transition_in=data.get("transition_in", "cut"),
            transition_out=data.get("transition_out", "cut"),
            post_processing=data.get("post_processing", {}),
        )


@dataclass
class ClipInstruction:
    sections: list = field(default_factory=list)
    precise_clips: list = field(default_factory=list)
    bgm_file: str = ""
    output_path: str = "output.mp4"
