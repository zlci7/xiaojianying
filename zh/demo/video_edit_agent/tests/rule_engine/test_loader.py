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
""", encoding="utf-8")
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
