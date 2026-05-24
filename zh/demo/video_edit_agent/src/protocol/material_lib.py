from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClipIssue:
    stability: dict = field(default_factory=dict)
    exposure: dict = field(default_factory=dict)
    horizon: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "ClipIssue":
        return cls(
            stability=data.get("stability", {}),
            exposure=data.get("exposure", {}),
            horizon=data.get("horizon", {}),
        )


@dataclass
class MaterialClip:
    clip_id: str = ""
    source: str = ""
    in_point: str = "00:00.0"
    out_point: str = "00:00.0"
    duration: float = 0.0
    quality_score: int = 0
    shot_type: str = ""
    content_tags: list = field(default_factory=list)
    motion: dict = field(default_factory=dict)
    aesthetic_score: int = 0
    usable: bool = True
    issues: list = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "MaterialClip":
        issues_raw = data.get("issues", [])
        issues = []
        for issue_data in issues_raw:
            issues.append(ClipIssue.from_dict(issue_data))
        return cls(
            clip_id=data.get("clip_id", ""),
            source=data.get("source", ""),
            in_point=data.get("in", "00:00.0"),
            out_point=data.get("out", "00:00.0"),
            duration=data.get("duration", 0.0),
            quality_score=data.get("quality_score", 0),
            shot_type=data.get("shot_type", ""),
            content_tags=data.get("content_tags", []),
            motion=data.get("motion", {}),
            aesthetic_score=data.get("aesthetic_score", 0),
            usable=data.get("usable", True),
            issues=issues,
            notes=data.get("notes", ""),
        )


@dataclass
class MaterialLib:
    clips: list = field(default_factory=list)

    def usable_clips(self) -> list:
        return [c for c in self.clips if c.usable]

    def filter_by_tags(self, tags: list) -> list:
        return [c for c in self.clips if any(t in c.content_tags for t in tags)]

    def filter_by_shot_type(self, shot_type: str) -> list:
        return [c for c in self.clips if c.shot_type == shot_type]

    def to_dict_list(self) -> list:
        result = []
        for c in self.clips:
            issues_data = []
            for issue in c.issues:
                issues_data.append({
                    "stability": issue.stability,
                    "exposure": issue.exposure,
                    "horizon": issue.horizon,
                })
            result.append({
                "clip_id": c.clip_id,
                "source": c.source,
                "in": c.in_point,
                "out": c.out_point,
                "duration": c.duration,
                "quality_score": c.quality_score,
                "shot_type": c.shot_type,
                "content_tags": c.content_tags,
                "motion": c.motion,
                "aesthetic_score": c.aesthetic_score,
                "usable": c.usable,
                "issues": issues_data,
                "notes": c.notes,
            })
        return result
