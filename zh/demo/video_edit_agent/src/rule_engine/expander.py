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
                int(section.duration / max(section.shot_constraint.max_shot_duration, 0.1)),
            )

        if transition_pref:
            params["transition_preference"] = transition_pref

        return params

    def expand_beat_params(self, bpm: int, duration: float) -> dict:
        beat_interval = 60.0 / max(bpm, 1)
        beat_count = int(duration / beat_interval) if beat_interval > 0 else 0
        return {
            "bpm": bpm,
            "beat_interval": beat_interval,
            "beat_count": beat_count,
            "alignment": "on_beat",
        }
