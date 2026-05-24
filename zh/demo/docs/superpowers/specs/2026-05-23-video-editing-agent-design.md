# 视频剪辑Agent — 系统架构设计文档

> 版本: v1.0 | 日期: 2026-05-23 | 状态: 设计评审通过

---

## 1. 项目概述

### 1.1 产品目标

构建一个AI驱动的视频剪辑Agent，核心能力：
- 输入参考vlog成品 → 学习其剪辑风格
- 输入用户多段旅游视频素材 → 将风格应用到素材上
- 输出风格类似但有独特特点的vlog成片

### 1.2 当前聚焦

**短快闪vlog**（2-3分钟），特点：高密度转场、卡BPM节奏、画面冲击力强。
长时间叙事型vlog列为后期TODO。

### 1.3 三阶段路线

| 阶段 | 目标 | 形态 |
|------|------|------|
| Phase 1 | 输入大量vlog成品，学习市场火爆风格，沉淀剪辑技巧到规则库 | CLI |
| Phase 2 | 输入参考vlog+用户旅游素材，输出成片，对话式微调 | CLI |
| Phase 3 | 产品化展示 | Web应用 |

---

## 2. 核心技术决策

| 维度 | 决策 |
|------|------|
| 风格理解 | 多模态LLM视觉分析（抽帧理解） |
| 成片生成 | LLM生成剪辑脚本 → 传统引擎执行（非端到端AI生成） |
| AI辅助增强 | 后期优化（补帧/调色/防抖），非主流程 |
| 剪辑技巧沉淀 | 结构化规则库，YAML+Markdown双层，可观测可人工修改 |
| 产品形态 | Phase 1-2 CLI验证 → Phase 3 Web化 |
| 技术栈 | Python + MoviePy + FFmpeg |
| 剪辑指令 | 双层协议（段落级粗粒度 + 镜头级细粒度可选覆盖） |
| Phase 1沉淀策略 | 人工审核 → 半自动 → 全自动，渐进过渡 |
| Phase 2微调 | CLI对话式反馈 → Web可视化时间线编辑 |

---

## 3. 系统架构

```
                     Video Editing Agent 架构
─────────────────────────────────────────────────────────────
                          
  输入层               分析层                编排层             输出层
┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────┐
│ 参考vlog  │──▶│  风格分析器   │   │  剪辑编排器   │   │  渲染引擎   │
│ (参考片)  │   │  (LLM视觉)   │──▶│  (LLM生成)   │──▶│ (FFmpeg/   │
└──────────┘   └──────┬───────┘   └──────┬───────┘   │  MoviePy)  │
                      │                  │           └─────┬──────┘
                ┌─────▼──────┐   ┌──────▼───────┐        │
                │  风格配置   │   │   规则引擎    │        │
                │  (YAML)    │◀─▶│ (YAML+MD)    │        │
                └────────────┘   └──────────────┘        │
                                                         │
┌──────────┐   ┌──────────────┐                  ┌───────▼──────┐
│ 用户素材  │──▶│  素材评估器   │                  │   输出成片    │
│ (多段视频)│   │ (评估→按需修复)│─────────────────▶│   (mp4)     │
└──────────┘   └──────────────┘                  └──────────────┘
```

### 3.1 五大核心模块

| 模块 | 职责 | 核心技术 |
|------|------|---------|
| **风格分析器** | 输入参考vlog → 输出结构化风格配置 | 多模态LLM抽帧分析 |
| **素材评估器** | 输入用户视频 → 先评估 → 按需修复 → 输出带标签素材库 | CV + LLM评估 |
| **规则引擎** | 管理沉淀的剪辑技巧，将粗粒度指令展开为具体操作 | Python + YAML规则库 |
| **剪辑编排器** | 匹配风格+素材 → 生成双层剪辑指令 | LLM编排 |
| **渲染引擎** | 执行剪辑指令 → 输出成片mp4 | FFmpeg + MoviePy |

### 3.2 数据流

```
Phase 1 (学习沉淀):
  参考vlog → 风格分析器 → 风格配置(YAML) → 人工审核提炼 → 规则入库

Phase 2 (剪辑生成):
  参考vlog → 风格分析器 → 风格配置
  用户素材 → 素材评估器(评估→按需修复) → 素材库(带标签)
  风格配置 + 素材库 + 规则引擎 → 剪辑编排器 → 双层剪辑指令 → 渲染引擎 → 成片
```

---

## 4. 核心数据协议

### 4.1 风格配置文件 (style_profile.yaml)

由风格分析器从参考vlog生成，是Phase 1和Phase 2之间的核心接口契约。

```yaml
meta:
  source_vlog: "xxx_reference.mp4"
  source_duration: 150s
  style_type: fast_flash
  style_summary: "高能快闪，卡点转场，暖色调电影感"

# 镜头特征
shot_pattern:
  avg_duration: 1.8s
  duration_range: [0.5, 4.0]
  speed_variation:
    speed_ramp_ratio: 0.3
    common_modes: ["fast_forward", "slow_mo_punch"]

# 转场体系（核心）
transitions:
  density: high
  types:
    hard_cut: 0.35
    match_cut: 0.20            # 动接动/形接形
    speed_ramp_transition: 0.15
    zoom_transition: 0.10
    whip_pan: 0.10
    glitch: 0.05
    light_leak: 0.05
    mask_wipe: 0.05            # 遮罩擦除
    object_pass: 0.05          # 物体遮挡转场
  avg_transition_duration: 0.3s

# 镜头运动
camera_motion:
  dominant_types: ["push_in", "pan_right", "drone_rise"]
  motion_match: true

# 节奏
rhythm:
  bpm_sync: true
  beat_alignment: "on_beat"
  pace_curve: [high, high, mid_peak, high]

# 画面审美
aesthetic:
  color_temp: warm
  saturation: +15%
  contrast: high
  dominant_colors: ["#FF8C42", "#1A1A2E"]

# 画面处理技法
post_processing:
  keying:
    frequency: medium
    common_uses: ["主体突出", "场景置换"]
  composite:
    overlay_texture: true
    picture_in_picture: false
    split_screen: false
  keyframe_animation:
    scale_zoom: true
    position_drift: true
    rotation_minor: true
  effects:
    glitch: {frequency: low}
    light_leak: {frequency: medium}
    freeze_frame: {frequency: low}
    reverse: {frequency: low}

# 画面风格路线
style_route: "cinematic"       # cinematic / authentic（根据素材水平自动选择）

# 素材匹配要求
material_requirements:
  preferred_shot_types: ["无人机大景", "手持跟拍", "特写"]
  preferred_content: ["风景高光", "人物情绪", "细节纹理"]
```

### 4.2 双层剪辑指令协议

编排器输出给渲染引擎的执行指令。

**Layer 1 — 段落级（粗，必须）：**

```yaml
sections:
  - id: sec_01
    name: "炸裂开场"
    duration: 6s
    rule_ref: "opening_high_energy"
    mood: high_energy
    music_sync:
      mode: beat_match
      bpm: 128
    shot_constraint:
      min_shot_count: 4
      max_shot_duration: 2s
      preferred_types: ["无人机大景", "快速推镜"]
      preferred_content: ["壮丽风景", "光影"]
    transition_style: "high_density"
    post_processing:
      keyframe_drift: true
```

**Layer 2 — 镜头级（细，可选覆盖）：**

```yaml
  precise_clips:               # 可选，精确覆盖自动编排
    - clip_id: c_001
      source_file: "DSC_0021.mp4"
      in: "00:05.2"
      out: "00:06.8"
      speed: 1.3x
      transition_in: "whip_pan_right"
      transition_out: "match_cut"
      post_processing:
        keying: {type: "shape_mask", shape: "circle_wipe"}
```

**执行优先级：** Layer 2 precise_clips > Layer 1 section规则 > 规则引擎默认值

### 4.3 素材库格式

素材评估器输出的带标签素材库：

```yaml
clip_id: mat_0042
source: "DSC_0021.mp4"
in: "00:05.2"
out: "00:08.5"
duration: 3.3s
quality_score: 6/10
shot_type: "无人机大景"
content_tags: ["风景", "日落", "水面"]
motion:
  direction: "push_forward"
  speed: medium
aesthetic_score: 7/10
style_route_suggestion: "cinematic"
usable: true
issues:
  stability: {level: medium, suggested_fix: "stabilize"}
  exposure: {level: low, suggested_fix: null}
  horizon: {level: high, suggested_fix: "level_correct"}
notes: "构图优秀，轻微抖动，建议防抖后用于开场"
```

---

## 5. 模块详细设计

### 5.1 风格分析器

```
输入: 参考vlog (.mp4)
输出: style_profile.yaml

流程:
  参考vlog → 抽帧(按镜头边界+关键帧) → 多模态LLM分析 → 结构化风格配置

LLM分析维度:
  - 叙事结构识别（开头-发展-高潮-结尾）
  - 转场类型识别和频率统计
  - 镜头时长分布
  - 镜头运动方向识别
  - 节奏曲线感知
  - 色彩/影调分析
  - 画面处理技法识别
```

### 5.2 素材评估器

```
输入: 用户多段旅游视频
输出: 素材库(带统一标签体系)

流水线:
  原始视频 → 场景分割 → 片段提取 → 多维评估 → 按需修复标记 → 标签化入库

评估维度（与风格配置标签体系统一）:
┌──────────────┬────────────────────────────────────┐
│ 技术质量      │ 清晰度、曝光、稳定性、噪声、水平线    │
│ 镜头类型      │ 无人机大景/手持跟拍/特写/摇移/推镜... │
│ 内容标签      │ 风景/美食/人文/人物/建筑/细节纹理     │
│ 运动特征      │ 运动方向、运动速度、动接动可行性       │
│ 画面美感      │ 构图、色彩、光影（LLM打分）           │
│ 风格路线建议   │ cinematic / authentic              │
└──────────────┴────────────────────────────────────┘

修复策略:
  先评估 → 标记issues → 编排阶段按镜头"叙事价值"决定是否修复
  - 高价值镜头（开场/高潮）→ 执行修复
  - 填充型镜头 → 可能不修复，加速掠过
  避免对所有素材盲目跑修复流程
```

### 5.3 规则引擎

管理沉淀的剪辑技巧。核心职责：将粗粒度指令展开为具体操作参数。

**双层存储：**
```
rules/           ← 结构化YAML，程序读取
rules_md/        ← 人类可读Markdown，自动同步，可人工修改
```

**单条规则示例 (match_cut.yaml)：**
```yaml
name: "匹配剪辑 - 动接动"
category: transition
description: "利用前后镜头运动方向一致实现无缝转场"
params:
  motion_tolerance: 15°
  min_match_duration: 0.3s
apply_condition:
  prev_shot_motion: required
  next_shot_motion: required
  motion_angle_diff: "<15°"
implementation:
  engine: "moviepy"
  method: "composite_with_blend"
  blend_duration: "{{blend_duration}}"
quality_tips:
  best_for: ["动作衔接", "行走跟拍切换"]
  avoid_when: ["前后运动方向相反", "速度差异过大"]
```

**展开逻辑：** 编排器指定"用match_cut" → 引擎检查前后素材运动标签 → 角度匹配则展开为FFmpeg参数 → 不匹配则降级为hard_cut或通知编排器重选。

### 5.4 剪辑编排器

```
输入: 风格配置 + 素材库(+标签) + 规则引擎
输出: 双层剪辑指令

流程:
  风格配置 + 素材库 
    → 匹配（"这个位置需要push_forward方向无人机大景，素材库有没有？"）
    → 规则引擎展开粗指令
    → LLM编排：决定每个位置的素材选择、精确时长、转场组合
    → 输出双层指令
```

### 5.5 渲染引擎

```
输入: 双层剪辑指令 + BGM
输出: 成片 .mp4

Layer 2 precise_clips → 直接执行
Layer 1 sections → 调用规则引擎展开 → 执行
BGM → 按beat_alignment做卡点对齐

技术: FFmpeg + MoviePy
后续增强: AI补帧/调色/防抖（后期优化角度）
```

---

## 6. 技术栈

| 组件 | 技术 |
|------|------|
| 核心语言 | Python 3.11+ |
| LLM集成 | Anthropic SDK / OpenAI SDK（多模态视觉分析） |
| 视频处理 | MoviePy + FFmpeg |
| 配置管理 | PyYAML |
| CLI | Click / Typer |
| Web后端(Phase 3) | FastAPI |
| Web前端(Phase 3) | React + 时间线组件 |
| 规则管理 | YAML ↔ Markdown 双向同步 |

---

## 7. CLI接口设计

### Phase 1 — 风格学习

```bash
# 分析单个参考vlog
python cli.py analyze --input ref_vlog.mp4 --output styles/beach_vibe.yaml

# 批量分析
python cli.py analyze-batch --input-dir ./ref_vlogs/ --output-dir ./styles/

# 查看风格配置（人类可读）
python cli.py style-show --style styles/beach_vibe.yaml --format markdown

# 规则库管理
python cli.py rules list
python cli.py rules add --file my_rule.yaml
python cli.py rules export --format md
```

### Phase 2 — 剪辑生成

```bash
# 评估素材
python cli.py evaluate --input-dir ./my_travel_videos/ --output ./material_lib/

# 生成剪辑
python cli.py edit \
  --style styles/beach_vibe.yaml \
  --materials ./material_lib/ \
  --bgm bgm_library/ \
  --output ./output/final_vlog.mp4

# 微调（对话式）
python cli.py refine --project ./output/final_vlog/ \
  --feedback "开场节奏再快一点，第3个转场换成匹配剪辑"
```

---

## 8. 项目目录结构

```
video_edit_agent/
├── cli.py                     # CLI入口
├── src/
│   ├── analyzer/              # 风格分析器
│   │   ├── __init__.py
│   │   ├── frame_extractor.py     # 视频抽帧
│   │   └── style_analyzer.py      # LLM风格分析
│   ├── evaluator/             # 素材评估器
│   │   ├── __init__.py
│   │   ├── scene_splitter.py      # 场景分割
│   │   ├── quality_assessor.py    # 质量评估
│   │   └── tag_extractor.py       # 标签提取
│   ├── orchestrator/          # 剪辑编排器
│   │   ├── __init__.py
│   │   └── editor.py              # LLM编排
│   ├── rule_engine/           # 规则引擎
│   │   ├── __init__.py
│   │   ├── loader.py              # 规则加载
│   │   ├── expander.py            # 指令展开
│   │   └── sync.py                # YAML↔MD同步
│   ├── renderer/              # 渲染引擎
│   │   ├── __init__.py
│   │   ├── composer.py            # MoviePy组装
│   │   └── ffmpeg_runner.py       # FFmpeg底层
│   └── protocol/              # 数据协议
│       ├── __init__.py
│       ├── style_profile.py       # 风格配置schema
│       ├── clip_instruction.py    # 双层指令schema
│       └── material_lib.py        # 素材库schema
├── rules/                     # 规则库(YAML)
│   ├── transitions/
│   ├── openings/
│   ├── rhythms/
│   └── post_processing/
├── rules_md/                  # 规则库(Markdown, 自动同步)
├── styles/                    # 已学习的风格配置
├── bgm_library/               # 默认BGM曲库
└── docs/                      # 设计文档
```

---

## 9. TODO / 后续迭代

| 优先级 | 条目 | 阶段 |
|--------|------|------|
| P1 | AI主体分割抠图（SAM/RMBG集成） | Phase 2后期 |
| P1 | 素材自动防抖/调色修复（当前仅评估+标记） | Phase 2后期 |
| P2 | 字幕/文字叠加风格学习与应用 | Phase 2后期 |
| P2 | 用户自定义BGM上传+识别后编排 | Phase 2后期 |
| P2 | 长时间叙事型vlog支持 | Phase 3 |
| P2 | Phase 1 规则半自动审核 → 全自动入库 | Phase 3 |
| P3 | Web时间线可视化编辑 | Phase 3 |
| P3 | AI补帧/调色/防抖增强 | Phase 3 |
| P3 | BGM智能推荐 | Phase 3 |

---

## 附录：术语表

| 术语 | 定义 |
|------|------|
| 风格配置文件 | 从参考vlog提取的结构化剪辑风格描述，分析器和编排器之间的契约 |
| 双层指令 | 段落级(粗)+镜头级(细)的剪辑执行指令协议 |
| 规则引擎 | 管理沉淀的复用剪辑技巧，将粗指令展开为具体参数 |
| 素材库 | 经评估器处理后带统一标签的用户视频片段集合 |
| 动接动 | 利用前后镜头运动方向一致实现无缝转场的技巧 |
| 风格路线 | 根据素材水平自动选择的画面风格方向（精致感/真实感） |
