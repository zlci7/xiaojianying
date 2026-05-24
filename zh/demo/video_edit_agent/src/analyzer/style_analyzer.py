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

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", base_url: str = ""):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = Anthropic(**kwargs)
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
