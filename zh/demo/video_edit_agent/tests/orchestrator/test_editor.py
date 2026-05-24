from src.orchestrator.editor import Editor
from src.protocol.material_lib import MaterialLib, MaterialClip
from src.protocol.clip_instruction import ClipInstruction

class TestEditor:
    def test_match_materials_by_type(self):
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
        matches = editor._match_materials(lib, ["drone_wide"], [])
        assert len(matches) == 1
        assert matches[0].clip_id == "m1"

    def test_match_materials_by_content(self):
        editor = Editor(api_key="fake-key")
        material = MaterialClip(
            clip_id="m1",
            source="test.mp4",
            shot_type="handheld",
            content_tags=["food"],
            usable=True,
        )
        lib = MaterialLib(clips=[material])
        matches = editor._match_materials(lib, [], ["food"])
        assert len(matches) == 1

    def test_match_materials_fallback(self):
        editor = Editor(api_key="fake-key")
        material = MaterialClip(
            clip_id="m1",
            source="test.mp4",
            shot_type="handheld",
            content_tags=["food"],
            usable=True,
        )
        lib = MaterialLib(clips=[material])
        matches = editor._match_materials(lib, ["drone_wide"], ["scenery"])
        assert len(matches) == 1  # fallback: return all usable

    def test_build_orchestration_prompt(self):
        editor = Editor(api_key="fake-key")
        prompt = editor._build_orchestration_prompt("test style", 3)
        assert "test style" in prompt
        assert "3" in prompt

    def test_parse_valid_response(self):
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
        assert instruction.sections[0].id == "sec_01"
        assert len(instruction.precise_clips) == 1
        assert instruction.precise_clips[0].clip_id == "c_001"

    def test_parse_invalid_response(self):
        editor = Editor(api_key="fake-key")
        result = editor._parse_response("not yaml at all")
        assert result is None

    def test_summarize_materials(self):
        editor = Editor(api_key="fake-key")
        materials = [
            MaterialClip(clip_id="m1", source="a.mp4", shot_type="drone", content_tags=["scenery"], quality_score=8, duration=3.0),
        ]
        summary = editor._summarize_materials(materials)
        assert "m1" in summary
        assert "drone" in summary
