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
""", encoding="utf-8")

        loader = RuleLoader(str(rules_dir))
        syncer = RuleSync(loader, str(md_dir))
        syncer.sync_all()

        md_file = md_dir / "transitions" / "hard_cut.md"
        assert md_file.exists()
        content = md_file.read_text(encoding="utf-8")
        assert "# 硬切" in content
        assert "直接切换" in content
