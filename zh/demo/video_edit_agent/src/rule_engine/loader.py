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
