from src.rule_engine.expander import RuleExpander
from src.protocol.clip_instruction import Section, ShotConstraint, MusicSync

class TestRuleExpander:
    def test_expand_section_without_loader(self):
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
        assert params["max_shot_duration"] == 1.5
        assert params["total_duration"] == 5.0
        assert params["preferred_types"] == ["drone_wide"]

    def test_expand_returns_defaults(self):
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

    def test_expand_beat_params(self):
        expander = RuleExpander()
        params = expander.expand_beat_params(bpm=128, duration=4.0)
        assert "beat_interval" in params
        assert params["bpm"] == 128
        assert params["beat_count"] > 0
