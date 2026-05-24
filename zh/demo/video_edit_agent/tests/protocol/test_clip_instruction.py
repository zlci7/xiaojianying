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
