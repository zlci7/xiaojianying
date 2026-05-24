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
    source_file: "filename.mp4"
    in: "00:00.0"
    out: "00:01.0"
    speed: 1.0
    transition_in: "cut"
    transition_out: "cut"
```"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", base_url: str = ""):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = Anthropic(**kwargs)
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

    def _build_orchestration_prompt(self, style_summary: str, material_count: int) -> str:
        return f"""请根据以下信息编排视频剪辑：

风格摘要: {style_summary}
素材数量: {material_count} 个可用片段

请生成合适的section和precise_clips编排方案。"""

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
