#!/usr/bin/env python3
"""Video Editing Agent CLI - AI-powered vlog editor"""

import os
import sys
import click
import yaml
from pathlib import Path

from src.protocol.style_profile import StyleProfile
from src.protocol.material_lib import MaterialLib, MaterialClip
from src.analyzer.frame_extractor import FrameExtractor
from src.analyzer.style_analyzer import StyleAnalyzer
from src.evaluator.scene_splitter import SceneSplitter
from src.evaluator.quality_assessor import QualityAssessor
from src.evaluator.tag_extractor import TagExtractor
from src.rule_engine.loader import RuleLoader
from src.rule_engine.sync import RuleSync
from src.orchestrator.editor import Editor
from src.renderer.composer import Composer


def load_config():
    """加载配置文件 config.yaml，不存在则返回空字典"""
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.yaml"
    )
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f.read()) or {}
    return {}


def get_api_key():
    config = load_config()
    api_cfg = config.get("api", {})
    return api_cfg.get("key") or os.environ.get("ANTHROPIC_API_KEY", "")


def get_base_url():
    config = load_config()
    api_cfg = config.get("api", {})
    return api_cfg.get("base_url") or os.environ.get("ANTHROPIC_BASE_URL", "")


def get_model():
    config = load_config()
    api_cfg = config.get("api", {})
    return api_cfg.get("model") or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def get_rules_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules")


def get_rules_md_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules_md")


@click.group()
def cli():
    """Video Editing Agent - AI-powered vlog editor"""
    pass


# ═══ Phase 1: Analyze ═══

@cli.command()
@click.option("--input", "-i", required=True, help="Reference vlog path (.mp4)")
@click.option("--output", "-o", required=True, help="Output style profile path (.yaml)")
def analyze(input, output):
    """Analyze a reference vlog and extract its editing style profile."""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: Set ANTHROPIC_API_KEY environment variable", err=True)
        sys.exit(1)

    extractor = FrameExtractor(sample_frames_per_scene=10)
    analyzer = StyleAnalyzer(api_key=api_key, base_url=get_base_url(), model=get_model())

    click.echo(f"Analyzing: {input}")
    profile = analyzer.analyze(input, extractor)

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(profile.to_yaml())

    click.echo(f"Style profile saved: {output}")
    click.echo(f"  Style: {profile.meta.style_type}")
    click.echo(f"  Summary: {profile.meta.style_summary}")
    click.echo(f"  Avg shot: {profile.shot_pattern.avg_duration}s")
    click.echo(f"  Transition density: {profile.transitions.density}")


@cli.command()
@click.option("--input-dir", "-i", required=True, help="Directory of reference vlogs")
@click.option("--output-dir", "-o", required=True, help="Output directory for style profiles")
def analyze_batch(input_dir, output_dir):
    """Batch analyze multiple reference vlogs in a directory."""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: Set ANTHROPIC_API_KEY environment variable", err=True)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    extractor = FrameExtractor()
    analyzer = StyleAnalyzer(api_key=api_key, base_url=get_base_url(), model=get_model())

    video_exts = {".mp4", ".mov", ".avi", ".mkv"}
    videos = sorted(f for f in os.listdir(input_dir)
                    if os.path.splitext(f)[1].lower() in video_exts)

    if not videos:
        click.echo(f"No video files found in {input_dir}")
        return

    for video in videos:
        input_path = os.path.join(input_dir, video)
        output_name = os.path.splitext(video)[0] + ".yaml"
        output_path = os.path.join(output_dir, output_name)
        click.echo(f"Analyzing: {video}")
        try:
            profile = analyzer.analyze(input_path, extractor)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(profile.to_yaml())
            click.echo(f"  -> {output_path}")
        except Exception as e:
            click.echo(f"  Error: {e}", err=True)


@cli.command()
@click.option("--style", "-s", required=True, help="Style profile YAML path")
def style_show(style):
    """Display a style profile in human-readable format."""
    with open(style, "r", encoding="utf-8") as f:
        profile = StyleProfile.from_yaml(f.read())

    click.echo(f"Source: {profile.meta.source_vlog}")
    click.echo(f"Style: {profile.meta.style_type}")
    click.echo(f"Summary: {profile.meta.style_summary}")
    click.echo(f"Duration: {profile.meta.source_duration}s")
    click.echo(f"Avg shot: {profile.shot_pattern.avg_duration}s")
    click.echo(f"Transition density: {profile.transitions.density}")
    click.echo(f"BPM sync: {profile.rhythm.bpm_sync}")
    click.echo(f"Color: {profile.aesthetic.color_temp}, saturation: {profile.aesthetic.saturation:+d}%")
    click.echo("Transitions:")
    for ttype, ratio in profile.transitions.types.items():
        click.echo(f"  {ttype}: {ratio*100:.0f}%")


# ═══ Phase 2: Edit ═══

@cli.command()
@click.option("--input-dir", "-i", required=True, help="Directory of user video clips")
@click.option("--output", "-o", required=True, help="Output material library directory")
def evaluate(input_dir, output):
    """Evaluate and tag user video clips, producing a material library."""
    os.makedirs(output, exist_ok=True)

    splitter = SceneSplitter()
    assessor = QualityAssessor()
    tagger = TagExtractor()
    extractor = FrameExtractor()

    video_exts = {".mp4", ".mov", ".avi", ".mkv"}
    videos = sorted(f for f in os.listdir(input_dir)
                    if os.path.splitext(f)[1].lower() in video_exts)

    if not videos:
        click.echo(f"No video files found in {input_dir}")
        return

    all_clips = []
    for video in videos:
        video_path = os.path.join(input_dir, video)
        click.echo(f"Evaluating: {video}")

        try:
            scenes = splitter.split(video_path)
        except Exception:
            scenes = [{"index": 0, "start": 0.0, "end": 1.0, "duration": 1.0}]

        for scene in scenes:
            try:
                frames = extractor.extract_scene_frames(video_path)
                frames = frames[:10]
            except Exception:
                frames = []

            if not frames:
                import numpy as np
                frames = [np.zeros((240, 320, 3), dtype=np.uint8)]

            quality = assessor.assess(frames)
            tags = tagger.extract(frames, {"duration": scene["duration"], "fps": 24})

            clip = MaterialClip(
                clip_id=f"{os.path.splitext(video)[0]}_s{scene['index']:03d}",
                source=os.path.abspath(video_path),
                in_point=f"{scene['start']:.1f}",
                out_point=f"{scene['end']:.1f}",
                duration=scene["duration"],
                quality_score=quality["quality_score"],
                shot_type=tags["shot_type"],
                content_tags=tags["content_tags"],
                motion=tags["motion"],
                aesthetic_score=tags["aesthetic_score"],
                usable=quality["quality_score"] >= 3,
                notes="Auto-evaluated",
            )
            all_clips.append(clip)

    lib = MaterialLib(clips=all_clips)
    output_file = os.path.join(output, "material_lib.yaml")
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(lib.to_dict_list(), f, allow_unicode=True, default_flow_style=False)

    click.echo(f"Material library saved: {output_file}")
    click.echo(f"Total clips: {len(all_clips)}")
    click.echo(f"Usable: {len(lib.usable_clips())}")


@cli.command()
@click.option("--style", "-s", required=True, help="Style profile YAML path")
@click.option("--materials", "-m", required=True, help="Material library directory")
@click.option("--bgm", "-b", default=None, help="BGM file or directory path")
@click.option("--output", "-o", required=True, help="Output video path (.mp4)")
def edit(style, materials, bgm, output):
    """Generate an edited vlog from style profile and user materials."""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: Set ANTHROPIC_API_KEY environment variable", err=True)
        sys.exit(1)

    with open(style, "r", encoding="utf-8") as f:
        profile = StyleProfile.from_yaml(f.read())

    lib_file = os.path.join(materials, "material_lib.yaml")
    if not os.path.exists(lib_file):
        click.echo(f"Error: material_lib.yaml not found in {materials}", err=True)
        click.echo("Run 'python cli.py evaluate' first", err=True)
        sys.exit(1)

    with open(lib_file, "r", encoding="utf-8") as f:
        clips_data = yaml.safe_load(f.read())

    clips = [MaterialClip.from_dict(d) for d in clips_data]
    lib = MaterialLib(clips=clips)

    bgm_file = ""
    if bgm:
        if os.path.isfile(bgm):
            bgm_file = bgm
        elif os.path.isdir(bgm):
            audio_exts = {".mp3", ".wav", ".m4a", ".aac"}
            audio_files = sorted(f for f in os.listdir(bgm)
                                 if os.path.splitext(f)[1].lower() in audio_exts)
            if audio_files:
                bgm_file = os.path.join(bgm, audio_files[0])

    click.echo("Orchestrating edit...")
    click.echo(f"  Style: {profile.meta.style_summary}")
    click.echo(f"  Usable clips: {len(lib.usable_clips())}")
    if bgm_file:
        click.echo(f"  BGM: {bgm_file}")

    editor = Editor(api_key=api_key, base_url=get_base_url(), model=get_model())
    instruction = editor.orchestrate(
        profile, lib, bgm_file=bgm_file, output_path=output
    )

    click.echo(f"Plan: {len(instruction.sections)} sections, {len(instruction.precise_clips)} precise clips")

    click.echo("Rendering...")
    composer = Composer()
    try:
        composer.compose(instruction)
        click.echo(f"Done! Output: {output}")
    except Exception as e:
        click.echo(f"Render error: {e}", err=True)
        click.echo("The clip instruction was generated but rendering failed.")
        click.echo("Check that FFmpeg is installed and source files exist.")
        sys.exit(1)


@cli.command()
@click.option("--project", "-p", required=True, help="Project directory (output dir of edit)")
@click.option("--feedback", "-f", required=True, help="Refinement feedback text")
def refine(project, feedback):
    """Refine an existing edit with natural language feedback."""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: Set ANTHROPIC_API_KEY environment variable", err=True)
        sys.exit(1)

    click.echo(f"Feedback: {feedback}")
    click.echo("(Refinement re-runs orchestration with feedback applied)")
    click.echo("Not yet implemented - coming in Phase 2")


# ═══ Rules Management ═══

@cli.group()
def rules():
    """Manage the editing rules library."""
    pass


@rules.command("list")
def rules_list():
    """List all available editing rules."""
    rules_dir = get_rules_dir()
    loader = RuleLoader(rules_dir)
    all_rules = loader.load_all()

    click.echo(f"Total rules: {len(all_rules)}\n")
    for name, data in sorted(all_rules.items()):
        cat = data.get("category", "other")
        display = data.get("name", name)
        desc = data.get("description", "")
        click.echo(f"  [{cat}] {name}")
        click.echo(f"       {display}: {desc}")


@rules.command("add")
@click.option("--file", "-f", required=True, help="Rule YAML file to add")
def rules_add(file):
    """Add a new rule from a YAML file."""
    import shutil
    rules_dir = get_rules_dir()
    dest = os.path.join(rules_dir, os.path.basename(file))
    shutil.copy(file, dest)
    click.echo(f"Rule added: {os.path.basename(file)}")


@rules.command("sync")
def rules_sync():
    """Sync YAML rules to human-readable Markdown files."""
    rules_dir = get_rules_dir()
    md_dir = get_rules_md_dir()
    loader = RuleLoader(rules_dir)
    syncer = RuleSync(loader, md_dir)
    syncer.sync_all()
    click.echo(f"Rules synced to {md_dir}")
    for root, dirs, files in os.walk(md_dir):
        for f in sorted(files):
            click.echo(f"  {os.path.relpath(os.path.join(root, f), md_dir)}")


@cli.command()
def version():
    """Show version information."""
    click.echo("Video Editing Agent v0.1.0")
    click.echo("AI-powered vlog editor")


if __name__ == "__main__":
    cli()
