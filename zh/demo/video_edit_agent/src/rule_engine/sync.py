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
