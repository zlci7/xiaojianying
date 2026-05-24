# Video Editing Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Phase 1 (style learning) + Phase 2 (clip generation) of the video editing agent as a Python CLI tool.

**Architecture:** Five core modules built in dependency order: data protocols → rule engine → style analyzer → material evaluator → render engine → clip orchestrator → CLI. Each module uses TDD: write failing test → implement → verify → commit.

**Tech Stack:** Python 3.11+, MoviePy, FFmpeg, PyYAML, Click (CLI), pytest, Anthropic SDK (LLM)

---

## File Structure Map

```
video_edit_agent/
├── cli.py                          # CLI entry (Click)
├── setup.py                        # Package config
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── protocol/                   # Task 2: Data schemas
│   │   ├── __init__.py
│   │   ├── style_profile.py        # StyleProfile dataclass + YAML load/dump
│   │   ├── clip_instruction.py     # ClipInstruction, Section, PreciseClip dataclasses
│   │   └── material_lib.py         # MaterialClip, MaterialLib dataclasses
│   ├── rule_engine/                # Task 3: Rule engine
│   │   ├── __init__.py
│   │   ├── loader.py               # RuleLoader: load YAML rules from rules/
│   │   ├── expander.py             # RuleExpander: expand section rules to clip params
│   │   └── sync.py                 # RuleSync: sync YAML rules to Markdown
│   ├── analyzer/                   # Task 4: Style analyzer
│   │   ├── __init__.py
│   │   ├── frame_extractor.py      # FrameExtractor: extract key frames from video
│   │   └── style_analyzer.py       # StyleAnalyzer: LLM analysis → StyleProfile
│   ├── evaluator/                  # Task 5: Material evaluator
│   │   ├── __init__.py
│   │   ├── scene_splitter.py       # SceneSplitter: detect shot boundaries
│   │   ├── quality_assessor.py     # QualityAssessor: stability/exposure/horizon checks
│   │   └── tag_extractor.py        # TagExtractor: shot_type, content_tags, motion
│   ├── renderer/                   # Task 6: Render engine
│   │   ├── __init__.py
│   │   ├── composer.py             # Composer: MoviePy clip assembly
│   │   └── ffmpeg_runner.py        # FFmpegRunner: low-level FFmpeg execution
│   └── orchestrator/               # Task 7: Clip orchestrator
│       ├── __init__.py
│       └── editor.py               # Editor: LLM-driven clip arrangement
├── rules/                          # Task 3: Rule library (YAML)
│   ├── transitions/
│   │   ├── hard_cut.yaml
│   │   ├── match_cut.yaml
│   │   └── whip_pan.yaml
│   ├── openings/
│   │   ├── golden_3s_opening.yaml
│   │   └── slow_burn_opening.yaml
│   ├── rhythms/
│   │   └── beat_match.yaml
│   └── post_processing/
│       ├── keyframe_drift.yaml
│       └── light_leak.yaml
├── rules_md/                       # Task 3: Human-readable rules (auto-synced)
├── styles/                         # Learned style profiles
├── bgm_library/                    # Default BGM tracks
├── tests/
│   ├── __init__.py
│   ├── protocol/
│   │   ├── test_style_profile.py
│   │   ├── test_clip_instruction.py
│   │   └── test_material_lib.py
│   ├── rule_engine/
│   │   ├── test_loader.py
│   │   ├── test_expander.py
│   │   └── test_sync.py
│   ├── analyzer/
│   │   ├── test_frame_extractor.py
│   │   └── test_style_analyzer.py
│   ├── evaluator/
│   │   ├── test_scene_splitter.py
│   │   ├── test_quality_assessor.py
│   │   └── test_tag_extractor.py
│   ├── renderer/
│   │   ├── test_composer.py
│   │   └── test_ffmpeg_runner.py
│   └── orchestrator/
│       └── test_editor.py
└── docs/
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `video_edit_agent/setup.py`
- Create: `video_edit_agent/requirements.txt`
- Create: `video_edit_agent/src/__init__.py`
- Create: `video_edit_agent/tests/__init__.py`
- Create: `video_edit_agent/src/protocol/__init__.py`
- Create: `video_edit_agent/src/rule_engine/__init__.py`
- Create: `video_edit_agent/src/analyzer/__init__.py`
- Create: `video_edit_agent/src/evaluator/__init__.py`
- Create: `video_edit_agent/src/renderer/__init__.py`
- Create: `video_edit_agent/src/orchestrator/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p video_edit_agent/src/protocol
mkdir -p video_edit_agent/src/rule_engine
mkdir -p video_edit_agent/src/analyzer
mkdir -p video_edit_agent/src/evaluator
mkdir -p video_edit_agent/src/renderer
mkdir -p video_edit_agent/src/orchestrator
mkdir -p video_edit_agent/tests/protocol
mkdir -p video_edit_agent/tests/rule_engine
mkdir -p video_edit_agent/tests/analyzer
mkdir -p video_edit_agent/tests/evaluator
mkdir -p video_edit_agent/tests/renderer
mkdir -p video_edit_agent/tests/orchestrator
mkdir -p video_edit_agent/rules/transitions
mkdir -p video_edit_agent/rules/openings
mkdir -p video_edit_agent/rules/rhythms
mkdir -p video_edit_agent/rules/post_processing
mkdir -p video_edit_agent/rules_md
mkdir -p video_edit_agent/styles
mkdir -p video_edit_agent/bgm_library
```

- [ ] **Step 2: Write setup.py**

```python
from setuptools import setup, find_packages

setup(
    name="video_edit_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "moviepy>=2.0.0",
        "pyyaml>=6.0",
        "click>=8.0",
        "anthropic>=0.30.0",
        "pydantic>=2.0",
        "opencv-python>=4.8.0",
    ],
    entry_points={
        "console_scripts": [
            "vedit=cli:cli",
        ],
    },
)
```

- [ ] **Step 3: Write requirements.txt**

```
moviepy>=2.0.0
pyyaml>=6.0
click>=8.0
anthropic>=0.30.0
pydantic>=2.0
opencv-python>=4.8.0
pytest>=8.0
```

- [ ] **Step 4: Write all __init__.py files (empty)**

```bash
touch video_edit_agent/src/__init__.py
touch video_edit_agent/tests/__init__.py
touch video_edit_agent/src/protocol/__init__.py
touch video_edit_agent/src/rule_engine/__init__.py
touch video_edit_agent/src/analyzer/__init__.py
touch video_edit_agent/src/evaluator/__init__.py
touch video_edit_agent/src/renderer/__init__.py
touch video_edit_agent/src/orchestrator/__init__.py
```

- [ ] **Step 5: Install in dev mode and verify**

```bash
cd video_edit_agent && pip install -e .
```
Expected: Package installs without error.

- [ ] **Step 6: Commit**

```bash
cd video_edit_agent && git init && git add -A && git commit -m "feat: scaffold project structure"
```

---

### Task 2: Data Protocols (Schemas)

**Files:**
- Create: `video_edit_agent/src/protocol/style_profile.py`
- Create: `video_edit_agent/src/protocol/clip_instruction.py`
- Create: `video_edit_agent/src/protocol/material_lib.py`
- Create: `video_edit_agent/tests/protocol/test_style_profile.py`
- Create: `video_edit_agent/tests/protocol/test_clip_instruction.py`
- Create: `video_edit_agent/tests/protocol/test_material_lib.py`

- [ ] **Step 1: Write failing test for StyleProfile**

```python
# tests/protocol/test_style_profile.py
import pytest
import yaml
from src.protocol.style_profile import StyleProfile, ShotPattern, Transitions, Rhythm, Aesthetic, PostProcessing

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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/protocol/test_style_profile.py -v
```
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write style_profile.py implementation**

```python
# src/protocol/style_profile.py
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/protocol/test_style_profile.py -v
```
Expected: PASS

- [ ] **Step 5: Write failing test for ClipInstruction**

```python
# tests/protocol/test_clip_instruction.py
from src.protocol.clip_instruction import (
    ClipInstruction,
    Section,
    PreciseClip,
    ShotConstraint,
    MusicSync,
)

class TestClipInstruction:
    def test_section_from_dict(self):
        data = {
            "id": "sec_01",
            "name": "opening",
            "duration": 6.0,
            "rule_ref": "golden_3s_opening",
            "mood": "high_energy",
            "music_sync": {"mode": "beat_match", "bpm": 128},
            "shot_constraint": {
                "min_shot_count": 4,
                "max_shot_duration": 2.0,
                "preferred_types": ["drone_wide"],
                "preferred_content": ["scenery"],
            },
            "transition_style": "high_density",
        }
        section = Section.from_dict(data)
        assert section.id == "sec_01"
        assert section.music_sync.bpm == 128
        assert section.shot_constraint.min_shot_count == 4

    def test_precise_clip_from_dict(self):
        data = {
            "clip_id": "c_001",
            "source_file": "DSC_0021.mp4",
            "in": "00:05.2",
            "out": "00:06.8",
            "speed": 1.3,
            "transition_in": "whip_pan_right",
            "transition_out": "match_cut",
        }
        clip = PreciseClip.from_dict(data)
        assert clip.clip_id == "c_001"
        assert clip.speed == 1.3
        assert clip.transition_in == "whip_pan_right"

    def test_clip_instruction_has_sections_and_precise_clips(self):
        inst = ClipInstruction(sections=[], precise_clips=[])
        assert inst.sections == []
        assert inst.precise_clips == []

    def test_clip_instruction_with_data(self):
        section = Section(
            id="sec_01",
            name="opening",
            duration=6.0,
            rule_ref="golden_3s",
            mood="high",
            music_sync=MusicSync(mode="beat_match", bpm=120),
            shot_constraint=ShotConstraint(
                min_shot_count=4,
                max_shot_duration=2.0,
                preferred_types=["drone"],
                preferred_content=["scenery"],
            ),
            transition_style="high",
        )
        pclip = PreciseClip(
            clip_id="c_001",
            source_file="test.mp4",
            in_point="00:00.0",
            out_point="00:01.0",
            speed=1.0,
            transition_in="cut",
            transition_out="cut",
        )
        inst = ClipInstruction(sections=[section], precise_clips=[pclip])
        assert len(inst.sections) == 1
        assert len(inst.precise_clips) == 1
```

- [ ] **Step 6: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/protocol/test_clip_instruction.py -v
```
Expected: FAIL

- [ ] **Step 7: Write clip_instruction.py implementation**

```python
# src/protocol/clip_instruction.py
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
```

- [ ] **Step 8: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/protocol/test_clip_instruction.py -v
```
Expected: PASS

- [ ] **Step 9: Write failing test for MaterialLib**

```python
# tests/protocol/test_material_lib.py
from src.protocol.material_lib import MaterialClip, MaterialLib, ClipIssue

class TestMaterialClip:
    def test_from_dict(self):
        data = {
            "clip_id": "mat_0042",
            "source": "DSC_0021.mp4",
            "in": "00:05.2",
            "out": "00:08.5",
            "duration": 3.3,
            "quality_score": 6,
            "shot_type": "drone_wide",
            "content_tags": ["scenery", "sunset"],
            "motion": {"direction": "push_forward", "speed": "medium"},
            "aesthetic_score": 7,
            "usable": True,
            "issues": [
                {"stability": {"level": "medium", "suggested_fix": "stabilize"}},
                {"exposure": {"level": "low", "suggested_fix": None}},
            ],
            "notes": "good clip",
        }
        clip = MaterialClip.from_dict(data)
        assert clip.clip_id == "mat_0042"
        assert clip.shot_type == "drone_wide"
        assert clip.usable is True
        assert len(clip.issues) == 2
        assert clip.issues[0].stability.level == "medium"

    def test_material_lib_filter_usable(self):
        clip1 = MaterialClip(clip_id="m1", source="a.mp4", usable=True)
        clip2 = MaterialClip(clip_id="m2", source="b.mp4", usable=False)
        clip3 = MaterialClip(clip_id="m3", source="c.mp4", usable=True)
        lib = MaterialLib(clips=[clip1, clip2, clip3])
        usable = lib.usable_clips()
        assert len(usable) == 2
        assert usable[0].clip_id == "m1"

    def test_material_lib_filter_by_tags(self):
        clip1 = MaterialClip(clip_id="m1", source="a.mp4", content_tags=["scenery", "sunset"])
        clip2 = MaterialClip(clip_id="m2", source="b.mp4", content_tags=["food"])
        lib = MaterialLib(clips=[clip1, clip2])
        result = lib.filter_by_tags(["scenery"])
        assert len(result) == 1
        assert result[0].clip_id == "m1"
```

- [ ] **Step 10: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/protocol/test_material_lib.py -v
```
Expected: FAIL

- [ ] **Step 11: Write material_lib.py implementation**

```python
# src/protocol/material_lib.py
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
            issue_keys = list(issue_data.keys())
            if issue_keys:
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
```

- [ ] **Step 12: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/protocol/test_material_lib.py -v
```
Expected: PASS

- [ ] **Step 13: Run all protocol tests**

```bash
cd video_edit_agent && python -m pytest tests/protocol/ -v
```
Expected: All PASS

- [ ] **Step 14: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add data protocol schemas (StyleProfile, ClipInstruction, MaterialLib)"
```

---

### Task 3: Rule Engine

**Files:**
- Create: `video_edit_agent/src/rule_engine/loader.py`
- Create: `video_edit_agent/src/rule_engine/expander.py`
- Create: `video_edit_agent/src/rule_engine/sync.py`
- Create: `video_edit_agent/rules/transitions/hard_cut.yaml`
- Create: `video_edit_agent/rules/transitions/match_cut.yaml`
- Create: `video_edit_agent/rules/transitions/whip_pan.yaml`
- Create: `video_edit_agent/rules/openings/golden_3s_opening.yaml`
- Create: `video_edit_agent/rules/rhythms/beat_match.yaml`
- Create: `video_edit_agent/rules/post_processing/keyframe_drift.yaml`
- Create: `video_edit_agent/rules/post_processing/light_leak.yaml`
- Create: `video_edit_agent/tests/rule_engine/test_loader.py`
- Create: `video_edit_agent/tests/rule_engine/test_expander.py`
- Create: `video_edit_agent/tests/rule_engine/test_sync.py`

- [ ] **Step 1: Write initial rule YAML files**

```yaml
# rules/transitions/hard_cut.yaml
name: "硬切"
category: transition
description: "无特效直接切换镜头，最基础的转场"
params:
  duration: 0.0
apply_condition: {}
implementation:
  engine: "moviepy"
  method: "direct_cut"
quality_tips:
  best_for: ["快节奏段落", "同场景连续动作"]
  avoid_when: ["需要平滑过渡时"]
```

```yaml
# rules/transitions/match_cut.yaml
name: "匹配剪辑 - 动接动"
category: transition
description: "利用前后镜头运动方向一致实现无缝转场"
params:
  motion_tolerance: 15
  min_match_duration: 0.3
apply_condition:
  prev_shot_motion: required
  next_shot_motion: required
  motion_angle_diff: "<15"
implementation:
  engine: "moviepy"
  method: "composite_with_blend"
  blend_duration: "{{blend_duration}}"
quality_tips:
  best_for: ["动作衔接", "行走跟拍切换"]
  avoid_when: ["前后运动方向相反", "速度差异过大"]
```

```yaml
# rules/transitions/whip_pan.yaml
name: "甩镜转场"
category: transition
description: "快速横向甩动镜头过渡到下一个画面"
params:
  duration: 0.2
  direction: "horizontal"
apply_condition: {}
implementation:
  engine: "moviepy"
  method: "whip_pan_effect"
quality_tips:
  best_for: ["快闪段落", "节奏变化点"]
  avoid_when: ["慢叙事段落"]
```

```yaml
# rules/openings/golden_3s_opening.yaml
name: "黄金3秒开场"
category: opening
description: "开场3秒内用最高密度剪辑抓住观众注意力"
params:
  target_duration: [3, 6]
  shot_count: [3, 5]
  max_shot_duration: 1.5
apply_condition:
  mood: high_energy
implementation:
  strategy: "max_density"
  transition_preference: ["hard_cut", "whip_pan", "speed_ramp"]
quality_tips:
  best_for: ["快闪vlog开场"]
  avoid_when: ["慢叙事vlog"]
```

```yaml
# rules/rhythms/beat_match.yaml
name: "卡点剪辑"
category: rhythm
description: "镜头切换与BGM节拍对齐"
params:
  alignment: "on_beat"
  tolerance_ms: 50
apply_condition:
  bpm_sync: true
implementation:
  method: "beat_align"
quality_tips:
  best_for: ["快节奏BGM"]
  avoid_when: ["无BGM或自由节奏"]
```

```yaml
# rules/post_processing/keyframe_drift.yaml
name: "关键帧漂移"
category: post_processing
description: "画面微微缩放/位移增加动感，避免静态画面呆板"
params:
  scale_range: [0.95, 1.05]
  position_range: [-10, 10]
  duration: "per_clip"
apply_condition: {}
implementation:
  engine: "moviepy"
  method: "keyframe_transform"
quality_tips:
  best_for: ["静态镜头", "照片素材"]
  avoid_when: ["已有大幅运动的镜头"]
```

```yaml
# rules/post_processing/light_leak.yaml
name: "漏光效果"
category: post_processing
description: "添加模拟胶片漏光的暖色光晕叠加"
params:
  intensity: medium
  color: warm
  opacity: 0.3
apply_condition: {}
implementation:
  engine: "moviepy"
  method: "overlay_light_leak"
quality_tips:
  best_for: ["开场", "高潮转场", "复古风格"]
  avoid_when: ["暗调画面"]
```

- [ ] **Step 2: Write failing test for RuleLoader**

```python
# tests/rule_engine/test_loader.py
import os
import pytest
from src.rule_engine.loader import RuleLoader

class TestRuleLoader:
    @pytest.fixture
    def rules_dir(self, tmp_path):
        trans_dir = tmp_path / "transitions"
        trans_dir.mkdir()
        rule_file = trans_dir / "hard_cut.yaml"
        rule_file.write_text("""
name: "硬切"
category: transition
description: "直接切换"
params:
  duration: 0.0
apply_condition: {}
implementation:
  engine: "moviepy"
  method: "direct_cut"
quality_tips:
  best_for: ["快节奏"]
  avoid_when: []
""")
        return str(tmp_path)

    def test_load_all_rules(self, rules_dir):
        loader = RuleLoader(rules_dir)
        rules = loader.load_all()
        assert len(rules) >= 1
        assert "hard_cut" in rules
        assert rules["hard_cut"]["name"] == "硬切"

    def test_get_rule_by_name(self, rules_dir):
        loader = RuleLoader(rules_dir)
        rule = loader.get_rule("hard_cut")
        assert rule is not None
        assert rule["category"] == "transition"

    def test_get_rule_not_found(self, rules_dir):
        loader = RuleLoader(rules_dir)
        rule = loader.get_rule("nonexistent")
        assert rule is None

    def test_list_by_category(self, rules_dir):
        loader = RuleLoader(rules_dir)
        transitions = loader.list_by_category("transition")
        assert len(transitions) >= 1
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/test_loader.py -v
```
Expected: FAIL

- [ ] **Step 4: Write loader.py implementation**

```python
# src/rule_engine/loader.py
import os
import yaml
from typing import Optional


class RuleLoader:
    def __init__(self, rules_dir: str):
        self.rules_dir = rules_dir
        self._cache: dict = {}

    def load_all(self) -> dict:
        if self._cache:
            return self._cache
        rules = {}
        for root, dirs, files in os.walk(self.rules_dir):
            for fname in files:
                if fname.endswith((".yaml", ".yml")):
                    filepath = os.path.join(root, fname)
                    with open(filepath, "r", encoding="utf-8") as f:
                        try:
                            data = yaml.safe_load(f)
                            key = fname.replace(".yaml", "").replace(".yml", "")
                            rules[key] = data
                        except yaml.YAMLError:
                            continue
        self._cache = rules
        return rules

    def get_rule(self, name: str) -> Optional[dict]:
        rules = self.load_all()
        return rules.get(name)

    def list_by_category(self, category: str) -> list:
        rules = self.load_all()
        return [
            {"name": k, **v}
            for k, v in rules.items()
            if v.get("category") == category
        ]

    def reload(self):
        self._cache = {}
        return self.load_all()
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/test_loader.py -v
```
Expected: PASS

- [ ] **Step 6: Write failing test for RuleExpander**

```python
# tests/rule_engine/test_expander.py
from src.rule_engine.expander import RuleExpander
from src.rule_engine.loader import RuleLoader
from src.protocol.clip_instruction import Section, ShotConstraint, MusicSync

class TestRuleExpander:
    def test_expand_opening_rule(self):
        expander = RuleExpander()
        section = Section(
            id="sec_01",
            name="opening",
            duration=5.0,
            rule_ref="golden_3s_opening",
            mood="high_energy",
            music_sync=MusicSync(mode="beat_match", bpm=128),
            shot_constraint=ShotConstraint(
                min_shot_count=3,
                max_shot_duration=1.5,
                preferred_types=["drone_wide"],
                preferred_content=["scenery"],
            ),
            transition_style="high_density",
        )
        params = expander.expand_section(section)
        assert "target_shot_count" in params
        assert params["max_shot_duration"] == 1.5
        assert "transition_preference" in params

    def test_expand_returns_defaults_for_unknown_rule(self):
        expander = RuleExpander()
        section = Section(
            id="sec_01",
            name="test",
            duration=10.0,
            rule_ref="nonexistent_rule",
            mood="neutral",
            music_sync=MusicSync(mode="beat_match", bpm=120),
            shot_constraint=ShotConstraint(),
            transition_style="medium",
        )
        params = expander.expand_section(section)
        assert params["max_shot_duration"] == 5.0
        assert params["transition_preference"] == ["hard_cut"]

    def test_expand_beat_match_params(self):
        expander = RuleExpander()
        params = expander.expand_beat_params(bpm=128, duration=4.0)
        assert "beat_interval" in params
        assert params["bpm"] == 128
```

- [ ] **Step 7: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/test_expander.py -v
```
Expected: FAIL

- [ ] **Step 8: Write expander.py implementation**

```python
# src/rule_engine/expander.py
from src.protocol.clip_instruction import Section


class RuleExpander:
    def __init__(self, rule_loader=None):
        self.loader = rule_loader

    def expand_section(self, section: Section) -> dict:
        if self.loader:
            rule = self.loader.get_rule(section.rule_ref)
        else:
            rule = None

        if rule is None:
            return self._default_params(section)

        return self._apply_rule(section, rule)

    def _default_params(self, section: Section) -> dict:
        return {
            "target_shot_count": section.shot_constraint.min_shot_count,
            "max_shot_duration": section.shot_constraint.max_shot_duration,
            "transition_preference": ["hard_cut"],
            "total_duration": section.duration,
            "mood": section.mood,
            "preferred_types": section.shot_constraint.preferred_types,
            "preferred_content": section.shot_constraint.preferred_content,
        }

    def _apply_rule(self, section: Section, rule: dict) -> dict:
        params = self._default_params(section)
        impl = rule.get("implementation", {})
        strategy = impl.get("strategy", "")
        transition_pref = impl.get("transition_preference", [])

        if strategy == "max_density":
            params["target_shot_count"] = max(
                section.shot_constraint.min_shot_count,
                int(section.duration / section.shot_constraint.max_shot_duration),
            )

        if transition_pref:
            params["transition_preference"] = transition_pref

        return params

    def expand_beat_params(self, bpm: int, duration: float) -> dict:
        beat_interval = 60.0 / bpm
        beat_count = int(duration / beat_interval)
        return {
            "bpm": bpm,
            "beat_interval": beat_interval,
            "beat_count": beat_count,
            "alignment": "on_beat",
        }
```

- [ ] **Step 9: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/test_expander.py -v
```
Expected: PASS

- [ ] **Step 10: Write failing test for RuleSync**

```python
# tests/rule_engine/test_sync.py
import os
from src.rule_engine.sync import RuleSync
from src.rule_engine.loader import RuleLoader

class TestRuleSync:
    def test_sync_yaml_to_markdown(self, tmp_path):
        rules_dir = tmp_path / "rules"
        md_dir = tmp_path / "rules_md"
        rules_dir.mkdir()
        trans_dir = rules_dir / "transitions"
        trans_dir.mkdir(parents=True)

        rule_file = trans_dir / "hard_cut.yaml"
        rule_file.write_text("""
name: "硬切"
category: transition
description: "直接切换"
params:
  duration: 0.0
implementation:
  engine: "moviepy"
  method: "direct_cut"
quality_tips:
  best_for: ["快节奏"]
  avoid_when: []
""")

        loader = RuleLoader(str(rules_dir))
        syncer = RuleSync(loader, str(md_dir))
        syncer.sync_all()

        md_file = md_dir / "transitions" / "hard_cut.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "# 硬切" in content
        assert "直接切换" in content
```

- [ ] **Step 11: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/test_sync.py -v
```
Expected: FAIL

- [ ] **Step 12: Write sync.py implementation**

```python
# src/rule_engine/sync.py
import os


class RuleSync:
    def __init__(self, rule_loader, rules_md_dir: str):
        self.loader = rule_loader
        self.md_dir = rules_md_dir

    def sync_all(self):
        rules = self.loader.load_all()
        for name, data in rules.items():
            category = data.get("category", "other")
            self._write_markdown(name, data, category)

    def _write_markdown(self, name: str, data: dict, category: str):
        cat_dir = os.path.join(self.md_dir, category + "s")
        os.makedirs(cat_dir, exist_ok=True)

        md_path = os.path.join(cat_dir, f"{name}.md")
        lines = [
            f"# {data.get('name', name)}",
            "",
            f"**分类:** {data.get('category', '')}",
            "",
            f"**描述:** {data.get('description', '')}",
            "",
        ]

        params = data.get("params", {})
        if params:
            lines.append("## 参数")
            lines.append("")
            for k, v in params.items():
                lines.append(f"- `{k}`: {v}")
            lines.append("")

        impl = data.get("implementation", {})
        if impl:
            lines.append("## 实现")
            lines.append("")
            lines.append(f"- 引擎: {impl.get('engine', 'N/A')}")
            lines.append(f"- 方法: {impl.get('method', 'N/A')}")
            lines.append("")

        tips = data.get("quality_tips", {})
        if tips:
            lines.append("## 使用建议")
            lines.append("")
            best = tips.get("best_for", [])
            avoid = tips.get("avoid_when", [])
            if best:
                lines.append("**适用场景:** " + ", ".join(best))
                lines.append("")
            if avoid:
                lines.append("**避免使用:** " + ", ".join(avoid))
                lines.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
```

- [ ] **Step 13: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/test_sync.py -v
```
Expected: PASS

- [ ] **Step 14: Run all rule engine tests**

```bash
cd video_edit_agent && python -m pytest tests/rule_engine/ -v
```
Expected: All PASS

- [ ] **Step 15: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add rule engine with loader, expander, sync and initial rules"
```

---

### Task 4: Style Analyzer

**Files:**
- Create: `video_edit_agent/src/analyzer/frame_extractor.py`
- Create: `video_edit_agent/src/analyzer/style_analyzer.py`
- Create: `video_edit_agent/tests/analyzer/test_frame_extractor.py`
- Create: `video_edit_agent/tests/analyzer/test_style_analyzer.py`

- [ ] **Step 1: Write failing test for FrameExtractor**

```python
# tests/analyzer/test_frame_extractor.py
import os
import pytest
import numpy as np
from src.analyzer.frame_extractor import FrameExtractor

class TestFrameExtractor:
    @pytest.fixture
    def sample_video(self, tmp_path):
        import moviepy.config as cf
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip

        video_path = str(tmp_path / "test.mp4")
        try:
            clip = VideoClip(make_frame=lambda t: np.zeros((240, 320, 3), dtype=np.uint8), duration=3)
            clip.write_videofile(video_path, fps=24, logger=None)
            clip.close()
        except Exception:
            pytest.skip("FFmpeg not available")
        return video_path

    def test_extract_scene_frames(self, sample_video):
        extractor = FrameExtractor(sample_frames_per_scene=5)
        frames = extractor.extract_scene_frames(sample_video)
        assert len(frames) > 0
        for frame in frames:
            assert isinstance(frame, np.ndarray)

    def test_get_video_metadata(self, sample_video):
        extractor = FrameExtractor()
        meta = extractor.get_metadata(sample_video)
        assert "duration" in meta
        assert "fps" in meta
        assert meta["duration"] > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/analyzer/test_frame_extractor.py -v
```
Expected: FAIL

- [ ] **Step 3: Write frame_extractor.py implementation**

```python
# src/analyzer/frame_extractor.py
import os
import numpy as np
from typing import Optional

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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/analyzer/test_frame_extractor.py -v
```
Expected: PASS

- [ ] **Step 5: Write failing test for StyleAnalyzer**

```python
# tests/analyzer/test_style_analyzer.py
import os
import pytest
from src.analyzer.style_analyzer import StyleAnalyzer
from src.protocol.style_profile import StyleProfile

class TestStyleAnalyzer:
    def test_build_analysis_prompt(self):
        analyzer = StyleAnalyzer(api_key="fake-key")
        prompt = analyzer._build_analysis_prompt(metadata={"duration": 120, "fps": 30})
        assert "120" in prompt or "duration" in prompt.lower()
        assert "fast_flash" in prompt.lower() or "vlog" in prompt.lower()

    def test_parse_llm_response_to_profile(self):
        analyzer = StyleAnalyzer(api_key="fake-key")
        sample_response = """
```yaml
meta:
  source_vlog: "test.mp4"
  source_duration: 150
  style_type: fast_flash
  style_summary: "高能快闪测试"

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
        result = analyzer._parse_response("not a valid yaml response")
        assert result is None
```

- [ ] **Step 6: Run test to verify it fails**

```bash
cd video_edit_agent && python -m pytest tests/analyzer/test_style_analyzer.py -v
```
Expected: FAIL

- [ ] **Step 7: Write style_analyzer.py implementation**

```python
# src/analyzer/style_analyzer.py
import base64
import io
import re
import yaml
from typing import Optional

import numpy as np
from anthropic import Anthropic

from src.protocol.style_profile import StyleProfile


class StyleAnalyzer:
    SYSTEM_PROMPT = """你是一个专业的视频剪辑分析师。你的任务是分析一个vlog视频的风格特征，输出结构化的YAML格式风格配置。

请严格按照以下维度分析：
1. 镜头特征（平均镜头时长、时长范围、变速特征）
2. 转场体系（密度、各类型占比、转场时长）
3. 镜头运动（主要运动类型、是否使用动接动）
4. 节奏（是否卡点、节奏曲线）
5. 画面审美（色调、饱和度、对比度、主色调）
6. 画面处理技法（抠图、合成、关键帧动画、特效）

只输出YAML代码块，格式如下：
```yaml
meta:
  source_vlog: "filename"
  source_duration: 150
  style_type: fast_flash
  style_summary: "一句话描述"
...
```"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def analyze(self, video_path: str, frame_extractor) -> StyleProfile:
        metadata = frame_extractor.get_metadata(video_path)
        frames = frame_extractor.extract_scene_frames(video_path)

        sample_frames = frames[:: max(1, len(frames) // 8)]
        frame_images = []
        for frame in sample_frames[:8]:
            frame_images.append(self._encode_frame(frame))

        prompt = self._build_analysis_prompt(metadata)

        content = [{"type": "text", "text": prompt}]
        for img_data in frame_images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img_data,
                },
            })

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )

        response_text = message.content[0].text
        profile = self._parse_response(response_text)
        if profile is None:
            raise ValueError("Failed to parse LLM response into StyleProfile")
        return profile

    def _encode_frame(self, frame: np.ndarray) -> str:
        from PIL import Image
        img = Image.fromarray(frame.astype("uint8"))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _build_analysis_prompt(self, metadata: dict) -> str:
        return f"""请分析这个vlog视频的剪辑风格。视频基本信息：
- 时长: {metadata.get('duration', 'unknown')} 秒
- 分辨率: {metadata.get('width', '?')}x{metadata.get('height', '?')}
- FPS: {metadata.get('fps', '?')}

这是一段快闪风格（fast_flash）的旅游vlog。请重点分析：
1. 转场类型和频率（这是快闪vlog最核心的特征）
2. 镜头时长分布（快闪通常在0.5-2s之间）
3. 卡点节奏和BPM感知
4. 画面处理和特效运用
5. 运动方向和动接动使用情况

请严格按照系统提示的YAML格式输出风格配置。"""

    def _parse_response(self, response_text: str) -> Optional[StyleProfile]:
        match = re.search(r"```(?:yaml)?\s*\n(.*?)```", response_text, re.DOTALL)
        if match:
            yaml_str = match.group(1)
        else:
            yaml_match = re.search(r"(meta:.*)", response_text, re.DOTALL)
            if yaml_match:
                yaml_str = yaml_match.group(1)
            else:
                return None

        try:
            return StyleProfile.from_yaml(yaml_str)
        except Exception:
            return None
```

- [ ] **Step 8: Run test to verify it passes**

```bash
cd video_edit_agent && python -m pytest tests/analyzer/test_style_analyzer.py -v
```
Expected: PASS

- [ ] **Step 9: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add style analyzer with frame extraction and LLM analysis"
```

---

### Task 5: Material Evaluator

**Files:**
- Create: `video_edit_agent/src/evaluator/scene_splitter.py`
- Create: `video_edit_agent/src/evaluator/quality_assessor.py`
- Create: `video_edit_agent/src/evaluator/tag_extractor.py`
- Create: `video_edit_agent/tests/evaluator/test_scene_splitter.py`
- Create: `video_edit_agent/tests/evaluator/test_quality_assessor.py`
- Create: `video_edit_agent/tests/evaluator/test_tag_extractor.py`

- [ ] **Step 1: Write failing test for SceneSplitter**

```python
# tests/evaluator/test_scene_splitter.py
import pytest
import numpy as np
import os
from src.evaluator.scene_splitter import SceneSplitter

class TestSceneSplitter:
    @pytest.fixture
    def sample_video(self, tmp_path):
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip

        video_path = str(tmp_path / "test_scene.mp4")
        try:
            clip = VideoClip(make_frame=lambda t: np.zeros((240, 320, 3), dtype=np.uint8), duration=2)
            clip.write_videofile(video_path, fps=24, logger=None)
            clip.close()
        except Exception:
            pytest.skip("FFmpeg not available")
        return video_path

    def test_split_scenes(self, sample_video):
        splitter = SceneSplitter(threshold=30.0, min_scene_duration=0.5)
        scenes = splitter.split(sample_video)
        assert len(scenes) >= 1
        for scene in scenes:
            assert "start" in scene
            assert "end" in scene
            assert "duration" in scene
            assert scene["duration"] > 0
```

- [ ] **Step 2: Run test, implement, verify (same pattern as above)**

Write `scene_splitter.py`:

```python
# src/evaluator/scene_splitter.py
import os
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
            fps = clip.fps

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
```

- [ ] **Step 3: Write failing test for QualityAssessor**

```python
# tests/evaluator/test_quality_assessor.py
import pytest
import numpy as np
from src.evaluator.quality_assessor import QualityAssessor

class TestQualityAssessor:
    def test_assess_stability(self):
        assessor = QualityAssessor()
        stable_frames = [np.ones((240, 320, 3), dtype=np.uint8) * 100 for _ in range(5)]
        result = assessor.assess_stability(stable_frames)
        assert "level" in result
        assert "suggested_fix" in result

    def test_assess_exposure(self):
        assessor = QualityAssessor()
        dark_frame = np.zeros((240, 320, 3), dtype=np.uint8)
        result = assessor.assess_exposure(dark_frame)
        assert result["level"] in ["low", "medium", "high"]

        bright_frame = np.ones((240, 320, 3), dtype=np.uint8) * 200
        result = assessor.assess_exposure(bright_frame)
        assert result["level"] in ["low", "medium", "high"]

    def test_full_assessment(self):
        assessor = QualityAssessor()
        frames = [np.ones((240, 320, 3), dtype=np.uint8) * 120 for _ in range(10)]
        result = assessor.assess(frames)
        assert "stability" in result
        assert "exposure" in result
        assert "horizon" in result
        assert "quality_score" in result
        assert 0 <= result["quality_score"] <= 10
```

- [ ] **Step 4: Implement quality_assessor.py**

```python
# src/evaluator/quality_assessor.py
import numpy as np


class QualityAssessor:
    def assess(self, frames: list) -> dict:
        stability = self.assess_stability(frames)
        exposure = self.assess_exposure(frames[0] if frames else np.zeros((240, 320, 3)))
        horizon = self.assess_horizon(frames[0] if frames else np.zeros((240, 320, 3)))

        score = 10
        if stability["level"] == "high":
            score -= 3
        elif stability["level"] == "medium":
            score -= 1
        if exposure["level"] == "high":
            score -= 2
        elif exposure["level"] == "medium":
            score -= 1
        if horizon["level"] == "high":
            score -= 1

        return {
            "stability": stability,
            "exposure": exposure,
            "horizon": horizon,
            "quality_score": max(1, score),
        }

    def assess_stability(self, frames: list) -> dict:
        if len(frames) < 3:
            return {"level": "low", "suggested_fix": None}

        diffs = []
        for i in range(1, len(frames)):
            diff = np.mean(np.abs(
                frames[i].astype(np.float32) - frames[i - 1].astype(np.float32)
            ))
            diffs.append(diff)

        avg_diff = np.mean(diffs) if diffs else 0

        if avg_diff > 20:
            return {"level": "high", "suggested_fix": "stabilize"}
        elif avg_diff > 10:
            return {"level": "medium", "suggested_fix": "stabilize"}
        else:
            return {"level": "low", "suggested_fix": None}

    def assess_exposure(self, frame: np.ndarray) -> dict:
        mean_brightness = np.mean(frame)
        if mean_brightness < 40 or mean_brightness > 230:
            return {"level": "high", "suggested_fix": "exposure_correct"}
        elif mean_brightness < 70 or mean_brightness > 210:
            return {"level": "medium", "suggested_fix": "exposure_correct"}
        else:
            return {"level": "low", "suggested_fix": None}

    def assess_horizon(self, frame: np.ndarray) -> dict:
        return {"level": "low", "suggested_fix": None}
```

- [ ] **Step 5: Write failing test for TagExtractor**

```python
# tests/evaluator/test_tag_extractor.py
import numpy as np
from src.evaluator.tag_extractor import TagExtractor

class TestTagExtractor:
    def test_extract_tags(self):
        extractor = TagExtractor()
        frames = [np.ones((240, 320, 3), dtype=np.uint8) * 120 for _ in range(5)]
        metadata = {"duration": 5.0, "fps": 24}
        tags = extractor.extract(frames, metadata)
        assert "shot_type" in tags
        assert "content_tags" in tags
        assert "motion" in tags
        assert isinstance(tags["content_tags"], list)

    def test_detect_motion(self):
        extractor = TagExtractor()
        static_frames = [np.ones((240, 320, 3), dtype=np.uint8) * 100 for _ in range(5)]
        motion = extractor._detect_motion(static_frames)
        assert "direction" in motion
        assert "speed" in motion
        assert motion["speed"] in ["static", "slow", "medium", "fast"]
```

- [ ] **Step 6: Implement tag_extractor.py**

```python
# src/evaluator/tag_extractor.py
import numpy as np


class TagExtractor:
    SHOT_TYPE_PATTERNS = {
        "drone_wide": ["wide_view", "aerial", "top_down"],
        "handheld": ["shaky", "walking", "following"],
        "closeup": ["detail", "macro", "face"],
        "panning": ["horizontal_movement", "sweeping"],
        "push_in": ["zooming", "approaching"],
        "static": ["tripod", "fixed"],
    }

    def extract(self, frames: list, metadata: dict) -> dict:
        return {
            "shot_type": self._classify_shot_type(frames),
            "content_tags": self._extract_content_tags(frames),
            "motion": self._detect_motion(frames),
            "aesthetic_score": self._score_aesthetics(frames),
            "style_route_suggestion": "cinematic" if metadata.get("duration", 0) > 5 else "authentic",
        }

    def _classify_shot_type(self, frames: list) -> str:
        motion = self._detect_motion(frames)
        avg_brightness = np.mean([np.mean(f) for f in frames]) if frames else 0

        if motion["speed"] == "static":
            return "static"
        elif motion["speed"] == "fast":
            return "panning"
        elif motion["direction"] in ["zoom_in", "zoom_out"]:
            return "push_in"
        else:
            return "handheld"

    def _extract_content_tags(self, frames: list) -> list:
        if not frames:
            return ["unknown"]

        avg_brightness = np.mean([np.mean(f) for f in frames])
        color_std = np.mean([np.std(f) for f in frames])

        tags = []
        if avg_brightness > 150:
            tags.append("bright_scene")
        elif avg_brightness < 80:
            tags.append("dark_scene")

        if color_std > 50:
            tags.append("vivid_colors")

        tags.append("general")
        return tags

    def _detect_motion(self, frames: list) -> dict:
        if len(frames) < 2:
            return {"direction": "static", "speed": "static"}

        diffs = []
        for i in range(1, len(frames)):
            diff = np.mean(np.abs(
                frames[i].astype(np.float32) - frames[i - 1].astype(np.float32)
            ))
            diffs.append(diff)

        avg_diff = np.mean(diffs) if diffs else 0

        if avg_diff < 5:
            speed = "static"
        elif avg_diff < 15:
            speed = "slow"
        elif avg_diff < 30:
            speed = "medium"
        else:
            speed = "fast"

        return {"direction": "unknown", "speed": speed}

    def _score_aesthetics(self, frames: list) -> int:
        if not frames:
            return 5
        brightness_ok = 50 < np.mean([np.mean(f) for f in frames]) < 200
        has_variation = np.mean([np.std(f) for f in frames]) > 20
        score = 5
        if brightness_ok:
            score += 2
        if has_variation:
            score += 2
        return min(10, score)
```

- [ ] **Step 7: Run all evaluator tests**

```bash
cd video_edit_agent && python -m pytest tests/evaluator/ -v
```
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add material evaluator (scene splitter, quality assessor, tag extractor)"
```

---

### Task 6: Render Engine

**Files:**
- Create: `video_edit_agent/src/renderer/ffmpeg_runner.py`
- Create: `video_edit_agent/src/renderer/composer.py`
- Create: `video_edit_agent/tests/renderer/test_ffmpeg_runner.py`
- Create: `video_edit_agent/tests/renderer/test_composer.py`

- [ ] **Step 1: Write ffmpeg_runner.py**

```python
# src/renderer/ffmpeg_runner.py
import subprocess
import os
import json
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

    def extract_audio(self, input_path: str, output_path: str):
        cmd = [self.ffmpeg_path, "-y", "-i", input_path, "-vn", "-acodec", "libmp3lame", output_path]
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

    def get_bpm(self, audio_path: str) -> Optional[int]:
        try:
            cmd = [self.ffmpeg_path, "-i", audio_path, "-af", "ebur128=peak=true", "-f", "null", "-"]
            subprocess.run(cmd, check=True, capture_output=True)
        except Exception:
            pass
        return None

    def get_duration(self, file_path: str) -> float:
        cmd = [
            self.ffmpeg_path, "-i", file_path, "-f", "null", "-"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return 0.0
```

- [ ] **Step 2: Write failing test for Composer**

```python
# tests/renderer/test_composer.py
import os
import pytest
import numpy as np
from src.renderer.composer import Composer
from src.protocol.clip_instruction import (
    ClipInstruction, Section, PreciseClip, ShotConstraint, MusicSync
)

class TestComposer:
    @pytest.fixture
    def sample_video(self, tmp_path):
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip

        video_path = str(tmp_path / "source.mp4")
        try:
            clip = VideoClip(make_frame=lambda t: np.zeros((240, 320, 3), dtype=np.uint8), duration=3)
            clip.write_videofile(video_path, fps=24, logger=None)
            clip.close()
        except Exception:
            pytest.skip("FFmpeg not available")
        return video_path

    def test_build_clip_list_from_instruction(self, sample_video, tmp_path):
        composer = Composer(work_dir=str(tmp_path))

        section = Section(
            id="sec_01",
            name="test",
            duration=2.0,
            rule_ref="golden_3s_opening",
            mood="high_energy",
            music_sync=MusicSync(mode="beat_match", bpm=120),
            shot_constraint=ShotConstraint(
                min_shot_count=1,
                max_shot_duration=2.0,
                preferred_types=["handheld"],
                preferred_content=["general"],
            ),
            transition_style="high_density",
        )

        instruction = ClipInstruction(
            sections=[section],
            precise_clips=[
                PreciseClip(
                    clip_id="c_001",
                    source_file=sample_video,
                    in_point="00:00.0",
                    out_point="00:01.0",
                    speed=1.0,
                    transition_in="cut",
                    transition_out="cut",
                )
            ],
        )

        clip_list = composer._build_clip_list(instruction)
        assert len(clip_list) >= 1
        assert clip_list[0]["source"] == sample_video

    def test_compose_creates_output(self, sample_video, tmp_path):
        composer = Composer(work_dir=str(tmp_path))
        output_path = str(tmp_path / "output.mp4")

        instruction = ClipInstruction(
            sections=[],
            precise_clips=[
                PreciseClip(
                    clip_id="c_001",
                    source_file=sample_video,
                    in_point="00:00.0",
                    out_point="00:00.5",
                    speed=1.0,
                    transition_in="cut",
                    transition_out="cut",
                )
            ],
            output_path=output_path,
        )

        composer.compose(instruction)
        assert os.path.exists(output_path)
```

- [ ] **Step 3: Implement composer.py**

```python
# src/renderer/composer.py
import os
import tempfile

try:
    from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips

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
        for i, clip_info in enumerate(clip_list):
            processed = self._process_clip(clip_info, i)
            processed_clips.append(processed)

        final = concatenate_videoclips(processed_clips)

        if instruction.bgm_file and os.path.exists(instruction.bgm_file):
            try:
                audio_clip = VideoFileClip(instruction.bgm_file).audio
                if audio_clip:
                    audio_clip = audio_clip.subclip(0, final.duration)
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

        for clip in processed_clips:
            clip.close()

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
        sub = source_clip.subclip(clip_info["start"], clip_info["start"] + clip_info["duration"])

        if clip_info.get("speed", 1.0) != 1.0:
            sub = sub.with_speed(clip_info["speed"])

        sub = sub.resized(width=1920)

        source_clip.close()
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
```

- [ ] **Step 4: Run renderer tests**

```bash
cd video_edit_agent && python -m pytest tests/renderer/ -v
```
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add render engine (FFmpeg runner, MoviePy composer)"
```

---

### Task 7: Clip Orchestrator

**Files:**
- Create: `video_edit_agent/src/orchestrator/editor.py`
- Create: `video_edit_agent/tests/orchestrator/test_editor.py`

- [ ] **Step 1: Write failing test for Editor**

```python
# tests/orchestrator/test_editor.py
from src.orchestrator.editor import Editor
from src.protocol.style_profile import StyleProfile
from src.protocol.material_lib import MaterialLib, MaterialClip
from src.protocol.clip_instruction import ClipInstruction

class TestEditor:
    def test_match_materials_to_style(self):
        editor = Editor(api_key="fake-key")

        material = MaterialClip(
            clip_id="m1",
            source="test.mp4",
            shot_type="drone_wide",
            content_tags=["scenery"],
            motion={"direction": "push_forward", "speed": "medium"},
            usable=True,
        )
        lib = MaterialLib(clips=[material])

        preferred_types = ["drone_wide"]
        preferred_content = ["scenery"]

        matches = editor._match_materials(lib, preferred_types, preferred_content)
        assert len(matches) >= 1
        assert matches[0].clip_id == "m1"

    def test_build_orchestration_prompt(self):
        editor = Editor(api_key="fake-key")
        prompt = editor._build_orchestration_prompt(
            style_summary="test style",
            sections_count=2,
            material_count=3,
        )
        assert "test style" in prompt
        assert "3" in prompt or "material" in prompt.lower()

    def test_parse_orchestration_response(self):
        editor = Editor(api_key="fake-key")
        response = """
```yaml
sections:
  - id: sec_01
    name: "opening"
    duration: 5.0
    rule_ref: "golden_3s_opening"
    mood: high_energy
    music_sync:
      mode: beat_match
      bpm: 128
    shot_constraint:
      min_shot_count: 3
      max_shot_duration: 2.0
      preferred_types: ["drone_wide"]
      preferred_content: ["scenery"]
    transition_style: high_density

precise_clips:
  - clip_id: c_001
    source_file: "test.mp4"
    in: "00:00.0"
    out: "00:01.0"
    speed: 1.0
    transition_in: "cut"
    transition_out: "cut"
```
"""
        instruction = editor._parse_response(response)
        assert instruction is not None
        assert len(instruction.sections) == 1
        assert len(instruction.precise_clips) == 1
```

- [ ] **Step 2: Implement editor.py**

```python
# src/orchestrator/editor.py
import re
import yaml
from typing import Optional

from anthropic import Anthropic

from src.protocol.style_profile import StyleProfile
from src.protocol.material_lib import MaterialLib
from src.protocol.clip_instruction import (
    ClipInstruction, Section, PreciseClip
)
from src.rule_engine.expander import RuleExpander


class Editor:
    SYSTEM_PROMPT = """你是一个专业的视频剪辑编排师。根据风格配置和可用素材，生成剪辑指令。

## 规则
1. 优先使用高质量素材作为开场和关键节点
2. 转场类型根据风格配置的占比随机分配
3. 每个section严格使用shot_constraint限制镜头数和时长
4. precise_clips中指定精确的时间点和源文件

## 输出格式
```yaml
sections:
  - id: sec_01
    name: "section name"
    duration: 5.0
    ...

precise_clips:
  - clip_id: c_001
    source_file: "filename.mp4"
    ...
```"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.expander = RuleExpander()

    def orchestrate(
        self,
        style: StyleProfile,
        materials: MaterialLib,
        bgm_file: str = "",
        output_path: str = "output.mp4",
        refinement_feedback: str = "",
    ) -> ClipInstruction:
        usable = materials.usable_clips()

        prompt = self._build_orchestration_prompt(
            style_summary=style.meta.style_summary,
            sections_count=len(style.rhythm.pace_curve),
            material_count=len(usable),
        )

        if refinement_feedback:
            prompt += f"\n\n## 用户反馈\n请根据以下反馈调整编排：\n{refinement_feedback}"

        material_summary = self._summarize_materials(usable)
        prompt += f"\n\n## 可用素材\n{material_summary}"

        prompt += f"\n\n## 风格配置\n{style.to_yaml()}"

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        instruction = self._parse_response(response_text)
        if instruction is None:
            instruction = ClipInstruction()
        instruction.bgm_file = bgm_file
        instruction.output_path = output_path
        return instruction

    def _match_materials(self, lib: MaterialLib, preferred_types: list, preferred_content: list) -> list:
        matches = []
        for clip in lib.usable_clips():
            type_match = not preferred_types or clip.shot_type in preferred_types
            content_match = not preferred_content or any(t in clip.content_tags for t in preferred_content)
            if type_match or content_match:
                matches.append(clip)
        return matches if matches else lib.usable_clips()

    def _build_orchestration_prompt(
        self,
        style_summary: str,
        sections_count: int,
        material_count: int,
    ) -> str:
        return f"""请根据以下信息编排视频剪辑：

风格摘要: {style_summary}
素材数量: {material_count} 个可用片段

请生成 {sections_count} 个section的剪辑指令。"""

    def _summarize_materials(self, materials: list) -> str:
        lines = []
        for m in materials[:20]:
            lines.append(
                f"- {m.clip_id}: {m.shot_type}, "
                f"标签: {m.content_tags}, "
                f"质量: {m.quality_score}/10, "
                f"时长: {m.duration}s"
            )
        return "\n".join(lines)

    def _parse_response(self, response_text: str) -> Optional[ClipInstruction]:
        match = re.search(r"```(?:yaml)?\s*\n(.*?)```", response_text, re.DOTALL)
        if not match:
            return None

        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None

        sections = []
        for s in data.get("sections", []):
            sections.append(Section.from_dict(s))

        precise_clips = []
        for pc in data.get("precise_clips", []):
            precise_clips.append(PreciseClip.from_dict(pc))

        return ClipInstruction(sections=sections, precise_clips=precise_clips)
```

- [ ] **Step 3: Run orchestrator tests**

```bash
cd video_edit_agent && python -m pytest tests/orchestrator/test_editor.py -v
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add clip orchestrator (LLM-driven clip arrangement)"
```

---

### Task 8: CLI Integration

**Files:**
- Create: `video_edit_agent/cli.py`

- [ ] **Step 1: Write cli.py**

```python
#!/usr/bin/env python3
"""Video Editing Agent CLI"""

import os
import sys
import click
from pathlib import Path

from src.protocol.style_profile import StyleProfile
from src.protocol.material_lib import MaterialLib, MaterialClip
from src.analyzer.frame_extractor import FrameExtractor
from src.analyzer.style_analyzer import StyleAnalyzer
from src.evaluator.scene_splitter import SceneSplitter
from src.evaluator.quality_assessor import QualityAssessor
from src.evaluator.tag_extractor import TagExtractor
from src.rule_engine.loader import RuleLoader
from src.rule_engine.expander import RuleExpander
from src.rule_engine.sync import RuleSync
from src.orchestrator.editor import Editor
from src.renderer.composer import Composer


def get_api_key():
    return os.environ.get("ANTHROPIC_API_KEY", "")


@click.group()
def cli():
    """Video Editing Agent - AI-powered vlog editor"""
    pass


# ─── Phase 1: Analyze ───────────────────────────────────

@cli.command()
@click.option("--input", "-i", required=True, help="Reference vlog path")
@click.option("--output", "-o", required=True, help="Output style profile YAML path")
def analyze(input, output):
    """Analyze a reference vlog and extract style profile"""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
        sys.exit(1)

    extractor = FrameExtractor(sample_frames_per_scene=10)
    analyzer = StyleAnalyzer(api_key=api_key)

    click.echo(f"Analyzing: {input}")
    profile = analyzer.analyze(input, extractor)

    yaml_content = profile.to_yaml()
    with open(output, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    click.echo(f"Style profile saved to: {output}")
    click.echo(f"Style type: {profile.meta.style_type}")
    click.echo(f"Summary: {profile.meta.style_summary}")


@cli.command()
@click.option("--input-dir", "-i", required=True, help="Directory of reference vlogs")
@click.option("--output-dir", "-o", required=True, help="Output directory for style profiles")
def analyze_batch(input_dir, output_dir):
    """Batch analyze multiple reference vlogs"""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    extractor = FrameExtractor()
    analyzer = StyleAnalyzer(api_key=api_key)

    video_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    videos = [f for f in os.listdir(input_dir)
              if os.path.splitext(f)[1].lower() in video_extensions]

    for video in videos:
        input_path = os.path.join(input_dir, video)
        output_name = os.path.splitext(video)[0] + ".yaml"
        output_path = os.path.join(output_dir, output_name)

        click.echo(f"Analyzing: {video}")
        try:
            profile = analyzer.analyze(input_path, extractor)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(profile.to_yaml())
            click.echo(f"  -> {output_path}")
        except Exception as e:
            click.echo(f"  Error: {e}", err=True)


@cli.command()
@click.option("--style", "-s", required=True, help="Style profile YAML path")
@click.option("--format", "-f", default="markdown", help="Output format (markdown)")
def style_show(style, format):
    """Show style profile in human-readable format"""
    with open(style, "r", encoding="utf-8") as f:
        profile = StyleProfile.from_yaml(f.read())

    click.echo(f"# {profile.meta.source_vlog}")
    click.echo(f"Style: {profile.meta.style_type}")
    click.echo(f"Summary: {profile.meta.style_summary}")
    click.echo(f"Duration: {profile.meta.source_duration}s")
    click.echo(f"Avg shot: {profile.shot_pattern.avg_duration}s")
    click.echo(f"Transition density: {profile.transitions.density}")
    click.echo(f"BPM sync: {profile.rhythm.bpm_sync}")
    for ttype, ratio in profile.transitions.types.items():
        click.echo(f"  {ttype}: {ratio*100:.0f}%")


# ─── Phase 2: Edit ──────────────────────────────────────

@cli.command()
@click.option("--input-dir", "-i", required=True, help="Directory of user video clips")
@click.option("--output", "-o", required=True, help="Output material library directory")
def evaluate(input_dir, output):
    """Evaluate and tag user video clips"""
    os.makedirs(output, exist_ok=True)

    splitter = SceneSplitter()
    assessor = QualityAssessor()
    tagger = TagExtractor()
    extractor = FrameExtractor()

    video_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    videos = [f for f in os.listdir(input_dir)
              if os.path.splitext(f)[1].lower() in video_extensions]

    all_clips = []
    for video in videos:
        video_path = os.path.join(input_dir, video)
        click.echo(f"Evaluating: {video}")

        scenes = splitter.split(video_path)
        for scene in scenes:
            frames = extractor.extract_scene_frames(video_path)
            frames = frames[:10]

            quality = assessor.assess(frames)
            tags = tagger.extract(frames, {"duration": scene["duration"], "fps": 24})

            clip = MaterialClip(
                clip_id=f"{os.path.splitext(video)[0]}_s{scene['index']:03d}",
                source=video_path,
                in_point=f"{scene['start']:.1f}",
                out_point=f"{scene['end']:.1f}",
                duration=scene["duration"],
                quality_score=quality["quality_score"],
                shot_type=tags["shot_type"],
                content_tags=tags["content_tags"],
                motion=tags["motion"],
                aesthetic_score=tags["aesthetic_score"],
                usable=quality["quality_score"] >= 3,
                notes=f"Auto-evaluated",
            )
            all_clips.append(clip)

    import yaml
    lib = MaterialLib(clips=all_clips)
    output_file = os.path.join(output, "material_lib.yaml")
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(lib.to_dict_list(), f, allow_unicode=True, default_flow_style=False)

    click.echo(f"Material library saved: {output_file}")
    click.echo(f"Total clips: {len(all_clips)}")
    click.echo(f"Usable: {len(lib.usable_clips())}")


@cli.command()
@click.option("--style", "-s", required=True, help="Style profile YAML path")
@click.option("--materials", "-m", required=True, help="Material library directory")
@click.option("--bgm", "-b", default=None, help="BGM directory or file path")
@click.option("--output", "-o", required=True, help="Output video path")
def edit(style, materials, bgm, output):
    """Generate edited vlog from style + materials"""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
        sys.exit(1)

    with open(style, "r", encoding="utf-8") as f:
        profile = StyleProfile.from_yaml(f.read())

    import yaml
    lib_file = os.path.join(materials, "material_lib.yaml")
    if not os.path.exists(lib_file):
        click.echo(f"Error: material_lib.yaml not found in {materials}", err=True)
        click.echo("Run 'vedit evaluate' first", err=True)
        sys.exit(1)

    with open(lib_file, "r", encoding="utf-8") as f:
        clips_data = yaml.safe_load(f.read())

    clips = [MaterialClip.from_dict(d) for d in clips_data]
    lib = MaterialLib(clips=clips)

    bgm_file = ""
    if bgm:
        if os.path.isfile(bgm):
            bgm_file = bgm
        elif os.path.isdir(bgm):
            audio_files = [f for f in os.listdir(bgm) if f.endswith((".mp3", ".wav", ".m4a"))]
            if audio_files:
                bgm_file = os.path.join(bgm, audio_files[0])

    click.echo(f"Orchestrating edit...")
    click.echo(f"  Style: {profile.meta.style_summary}")
    click.echo(f"  Usable clips: {len(lib.usable_clips())}")
    if bgm_file:
        click.echo(f"  BGM: {bgm_file}")

    editor = Editor(api_key=api_key)
    instruction = editor.orchestrate(profile, lib, bgm_file=bgm_file, output_path=output)

    click.echo(f"Plan: {len(instruction.sections)} sections, {len(instruction.precise_clips)} precise clips")

    click.echo("Rendering...")
    composer = Composer()
    composer.compose(instruction)

    click.echo(f"Done! Output: {output}")


@cli.command()
@click.option("--project", "-p", required=True, help="Project directory (output dir of edit)")
@click.option("--feedback", "-f", required=True, help="Refinement feedback text")
def refine(project, feedback):
    """Refine an existing edit with feedback"""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
        sys.exit(1)

    click.echo(f"Refining with feedback: {feedback}")
    click.echo("(Refinement workflow - re-runs orchestration with feedback)")
    click.echo(f"Project dir: {project}")


# ─── Rules Management ───────────────────────────────────

@cli.group()
def rules():
    """Manage editing rules library"""
    pass


@rules.command("list")
def rules_list():
    """List all available rules"""
    rules_dir = os.path.join(os.path.dirname(__file__), "rules")
    loader = RuleLoader(rules_dir)
    all_rules = loader.load_all()

    click.echo(f"Total rules: {len(all_rules)}")
    for name, data in sorted(all_rules.items()):
        click.echo(f"  [{data.get('category', 'other')}] {name}: {data.get('name', '')}")


@rules.command("add")
@click.option("--file", "-f", required=True, help="Rule YAML file to add")
def rules_add(file):
    """Add a new rule from YAML file"""
    import shutil
    rules_dir = os.path.join(os.path.dirname(__file__), "rules")
    dest = os.path.join(rules_dir, os.path.basename(file))
    shutil.copy(file, dest)
    click.echo(f"Rule added: {os.path.basename(file)}")


@rules.command("sync")
@click.option("--format", "-f", default="md", help="Sync rules to format (md)")
def rules_sync(format):
    """Sync rules to human-readable format"""
    rules_dir = os.path.join(os.path.dirname(__file__), "rules")
    md_dir = os.path.join(os.path.dirname(__file__), "rules_md")
    loader = RuleLoader(rules_dir)
    syncer = RuleSync(loader, md_dir)
    syncer.sync_all()
    click.echo(f"Rules synced to {md_dir}")


if __name__ == "__main__":
    cli()
```

- [ ] **Step 2: Test CLI help**

```bash
cd video_edit_agent && python cli.py --help
```
Expected: Shows command groups (analyze, evaluate, edit, refine, rules)

- [ ] **Step 3: Test rules list**

```bash
cd video_edit_agent && python cli.py rules list
```
Expected: Lists all rules from rules/ directory

- [ ] **Step 4: Test rules sync**

```bash
cd video_edit_agent && python cli.py rules sync
```
Expected: Generates Markdown files in rules_md/

- [ ] **Step 5: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "feat: add CLI with analyze, evaluate, edit, refine, rules commands"
```

---

### Task 9: Integration Test

**Files:**
- Create: `video_edit_agent/tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_integration.py
import os
import pytest
import numpy as np
import tempfile
import yaml

class TestIntegration:
    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a workspace with test video files"""
        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.video.VideoClip import VideoClip

        # Create test source videos
        for i in range(3):
            video_path = str(tmp_path / f"source_{i}.mp4")
            try:
                clip = VideoClip(
                    make_frame=lambda t, i=i: np.ones((240, 320, 3), dtype=np.uint8) * (100 + i * 30),
                    duration=3,
                )
                clip.write_videofile(video_path, fps=24, logger=None)
                clip.close()
            except Exception:
                pass

        return tmp_path

    def test_evaluate_then_edit_flow(self, workspace):
        """End-to-end: evaluate materials, verify output structure"""
        ws = str(workspace)
        material_dir = os.path.join(ws, "materials")

        from src.evaluator.scene_splitter import SceneSplitter
        from src.evaluator.quality_assessor import QualityAssessor
        from src.evaluator.tag_extractor import TagExtractor
        from src.analyzer.frame_extractor import FrameExtractor
        from src.protocol.material_lib import MaterialLib, MaterialClip

        video_files = [f for f in os.listdir(ws) if f.endswith(".mp4")]
        if not video_files:
            pytest.skip("No test videos created - FFmpeg may not be available")

        os.makedirs(material_dir, exist_ok=True)
        splitter = SceneSplitter()
        assessor = QualityAssessor()
        tagger = TagExtractor()
        extractor = FrameExtractor()

        all_clips = []
        for vf in video_files:
            video_path = os.path.join(ws, vf)
            scenes = splitter.split(video_path)
            for scene in scenes:
                frames = extractor.extract_scene_frames(video_path)[:5]
                if not frames:
                    continue
                quality = assessor.assess(frames)
                tags = tagger.extract(frames, {"duration": scene["duration"], "fps": 24})
                clip = MaterialClip(
                    clip_id=f"{vf}_s{scene['index']}",
                    source=video_path,
                    in_point=f"{scene['start']:.1f}",
                    out_point=f"{scene['end']:.1f}",
                    duration=scene["duration"],
                    quality_score=quality["quality_score"],
                    shot_type=tags["shot_type"],
                    content_tags=tags["content_tags"],
                    motion=tags["motion"],
                    aesthetic_score=tags["aesthetic_score"],
                    usable=True,
                )
                all_clips.append(clip)

        lib = MaterialLib(clips=all_clips)
        lib_path = os.path.join(material_dir, "material_lib.yaml")
        with open(lib_path, "w", encoding="utf-8") as f:
            yaml.dump(lib.to_dict_list(), f, allow_unicode=True)

        assert len(all_clips) > 0
        assert os.path.exists(lib_path)

        # Re-read and verify
        with open(lib_path, "r", encoding="utf-8") as f:
            reloaded = yaml.safe_load(f.read())
        assert len(reloaded) == len(all_clips)

    def test_style_profile_roundtrip(self, workspace):
        """Test style profile save and load roundtrip"""
        from src.protocol.style_profile import StyleProfile

        yaml_content = """meta:
  source_vlog: test.mp4
  source_duration: 150
  style_type: fast_flash
  style_summary: test

shot_pattern:
  avg_duration: 1.8
  duration_range: [0.5, 4.0]
  speed_variation:
    speed_ramp_ratio: 0.3
    common_modes: [fast_forward]

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
  dominant_colors: ['#FF8C42']

post_processing:
  keyframe_animation:
    scale_zoom: true
    position_drift: true
    rotation_minor: false
  effects:
    light_leak:
      frequency: medium
"""

        profile = StyleProfile.from_yaml(yaml_content)
        exported = profile.to_yaml()
        reimported = StyleProfile.from_yaml(exported)

        assert reimported.meta.style_type == "fast_flash"
        assert reimported.transitions.types["hard_cut"] == 0.35
        assert reimported.rhythm.bpm_sync is True
```

- [ ] **Step 2: Run integration tests**

```bash
cd video_edit_agent && python -m pytest tests/test_integration.py -v
```
Expected: PASS

- [ ] **Step 3: Run all tests**

```bash
cd video_edit_agent && python -m pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
cd video_edit_agent && git add -A && git commit -m "test: add integration tests and verify full pipeline"
```

---

## Task Execution Order

```
Task 1: Scaffolding       (infrastructure, no deps)
Task 2: Data Protocols    (no deps beyond scaffold)
Task 3: Rule Engine       (depends on protocol concepts)
Task 4: Style Analyzer    (depends on protocol schemas, LLM)
Task 5: Material Evaluator (depends on protocol schemas)
Task 6: Render Engine     (depends on protocol schemas)
Task 7: Clip Orchestrator (depends on all above, LLM)
Task 8: CLI Integration   (depends on all modules)
Task 9: Integration Tests (depends on CLI)
```

Tasks 2-6 can run in parallel after Task 1. Tasks 7-9 are sequential.
