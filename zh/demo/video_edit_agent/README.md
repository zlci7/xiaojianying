# Video Editing Agent

AI-powered vlog editor — learn editing styles from reference vlogs and apply them to your travel footage.

## Quick Start

### 1. 安装依赖

```bash
cd video_edit_agent
pip install -e .
```

### 2. 配置API（需要LLM功能时）

**方式一：配置文件（推荐）**

```bash
# 复制模板
cp config.template.yaml config.yaml

# 编辑 config.yaml，填入真实值
# config.yaml 已加入 .gitignore，不会提交到 git
```

```yaml
# config.yaml
api:
  key: "sk-ant-xxx"                    # API密钥
  base_url: "https://api.anthropic.com"  # API地址，支持代理/中转
  model: "claude-sonnet-4-20250514"      # 模型（可选）
```

**方式二：环境变量（config.yaml 不存在时自动使用）**

Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY="your_api_key"
$env:ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

Linux/Mac:
```bash
export ANTHROPIC_API_KEY=your_api_key
export ANTHROPIC_BASE_URL=https://api.anthropic.com
```

优先级：`config.yaml` > 环境变量

### 3. 无API Key演示（验证安装）

```bash
python demo.py
# 生成测试视频 → 评估素材 → 编排剪辑 → 渲染输出
# 输出目录: %TEMP%\vedit_demo\output\demo_vlog.mp4
```

### 4. 完整流水线（需要API Key）

```bash
# Phase 1: 分析参考vlog，提取风格
python cli.py analyze -i reference_vlog.mp4 -o styles/my_style.yaml

# 查看提取的风格
python cli.py style-show -s styles/my_style.yaml

# Phase 2: 评估你的旅游视频素材
python cli.py evaluate -i ./my_travel_clips/ -o ./materials/

# Phase 2: 生成剪辑
python cli.py edit -s styles/my_style.yaml -m ./materials/ -o my_vlog.mp4

# 微调（对话式反馈, Phase 2后期完善）
python cli.py refine -p ./output/ -f "开场节奏再快一点"
```

### 5. 规则库管理

```bash
python cli.py rules list              # 查看所有剪辑规则
python cli.py rules add -f rule.yaml  # 添加新规则
python cli.py rules sync              # 同步到Markdown（rules_md/目录）
```

### 6. 批量分析（Phase 1进阶）

```bash
python cli.py analyze-batch -i ./ref_vlogs/ -o ./styles/
```

## API 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `ANTHROPIC_API_KEY` | Anthropic API 密钥（必填） | 无 |
| `ANTHROPIC_BASE_URL` | API 地址，支持代理/中转 | `https://api.anthropic.com` |

代码中 API 初始化位置：
- `src/analyzer/style_analyzer.py:37` — 风格分析（Phase 1）
- `src/orchestrator/editor.py:48` — 剪辑编排（Phase 2）

## 项目结构

```
video_edit_agent/
├── cli.py              # CLI 入口（Click, 8个子命令）
├── demo.py             # 演示脚本（无需API Key）
├── setup.py            # 包配置
├── requirements.txt    # 依赖
├── src/
│   ├── analyzer/       # 风格分析器（多模态LLM抽帧分析）
│   ├── evaluator/      # 素材评估器（分割+质量+标签）
│   ├── orchestrator/   # 剪辑编排器（LLM生成剪辑指令）
│   ├── renderer/       # 渲染引擎（FFmpeg+MoviePy）
│   ├── rule_engine/    # 规则引擎（沉淀剪辑技巧）
│   └── protocol/       # 数据协议（风格配置/双层指令/素材库）
├── rules/              # 剪辑规则库（YAML, 7条初始规则）
├── rules_md/           # 规则库人类可读版（自动同步）
├── styles/             # 已学习的风格配置
├── bgm_library/        # 默认BGM曲库
└── tests/              # 43个测试，全部通过
```

## 要求

- Python 3.11+
- FFmpeg（视频处理必需）
- Anthropic API Key（LLM功能必需）
