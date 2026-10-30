#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_workflow.py — 全流程闭环与交叉引用校验。

只读扫描仓库根目录（本脚本上一级）：
  1. 必需文件存在性（SKILL/README/shared/modules/engines/assets/scripts）；
  2. 根 SKILL 六节点主线顺序引用；
  3. 07 强依赖 01/02，08 依赖 02/07；
  4. 每个模块的依赖矩阵（shared/engines/scripts）全部命中；
  5. 每个引擎必须引用至少一个校验脚本；
  6. 所有 Markdown 相对链接目标存在。
退出码：0 通过；1 校验失败。
"""
import json
import os
import re
import sys

REQUIRED_FILES = [
    "SKILL.md", "README.md", "ROUTING_CHECK.md",
    "shared/standard_specs.md", "shared/aesthetic_system.md",
    "shared/originality_system.md", "shared/context_ledger.md", "shared/negative_words.md",
    "modules/01_script.md", "modules/02_storyboard.md", "modules/03_asset_character.md",
    "modules/04_asset_scene.md", "modules/05_asset_costume.md",
    "modules/06_asset_prop.md", "modules/07_storyboard_gen.md", "modules/08_video_prompt.md",
    "engines/camera_engine.md", "engines/fight_engine.md", "engines/reverse_engine.md",
    "engines/layout_engine.md", "engines/continuity_engine.md", "engines/audio_engine.md",
    "engines/specialty_engine.md", "engines/model_adapter.md",
    "assets/INDEX.md",
    "scripts/calc_ratio.py", "scripts/calc_head_body.py",
    "scripts/validate_duration.py", "scripts/validate_layout.py",
    "scripts/validate_workflow.py", "scripts/validate_prompt.py",
    "scripts/validate_assets.py", "scripts/run_checks.py",
]

MAIN_FLOW = [
    "modules/01_script.md", "modules/02_storyboard.md", "modules/03_asset_character.md",
    "modules/04_asset_scene.md", "modules/07_storyboard_gen.md", "modules/08_video_prompt.md",
]

DEPENDENCY_MATRIX = {
    "modules/01_script.md": [
        "shared/standard_specs.md", "shared/context_ledger.md",
        "scripts/validate_duration.py", "scripts/validate_workflow.py",
        "scripts/validate_prompt.py"],
    "modules/02_storyboard.md": [
        "shared/standard_specs.md", "shared/context_ledger.md",
        "engines/camera_engine.md", "engines/continuity_engine.md", "engines/audio_engine.md",
        "scripts/validate_duration.py", "scripts/validate_workflow.py"],
    "modules/03_asset_character.md": [
        "shared/standard_specs.md", "shared/aesthetic_system.md",
        "shared/context_ledger.md", "shared/negative_words.md",
        "engines/camera_engine.md",
        "scripts/calc_head_body.py", "scripts/validate_layout.py", "scripts/validate_prompt.py"],
    "modules/04_asset_scene.md": [
        "shared/standard_specs.md", "shared/aesthetic_system.md",
        "shared/context_ledger.md", "shared/negative_words.md",
        "engines/camera_engine.md", "engines/layout_engine.md",
        "scripts/calc_ratio.py", "scripts/validate_layout.py", "scripts/validate_prompt.py"],
    "modules/05_asset_costume.md": [
        "shared/standard_specs.md", "shared/aesthetic_system.md",
        "shared/context_ledger.md", "shared/negative_words.md",
        "engines/camera_engine.md", "engines/layout_engine.md",
        "scripts/calc_head_body.py", "scripts/validate_layout.py", "scripts/validate_assets.py"],
    "modules/06_asset_prop.md": [
        "shared/standard_specs.md", "shared/aesthetic_system.md",
        "shared/context_ledger.md", "shared/negative_words.md",
        "engines/layout_engine.md",
        "scripts/calc_ratio.py", "scripts/validate_layout.py", "scripts/validate_assets.py"],
    "modules/07_storyboard_gen.md": [
        "modules/01_script.md", "modules/02_storyboard.md",
        "shared/standard_specs.md", "shared/aesthetic_system.md",
        "shared/context_ledger.md", "shared/negative_words.md",
        "engines/camera_engine.md", "engines/layout_engine.md",
        "scripts/validate_layout.py", "scripts/validate_workflow.py", "scripts/validate_prompt.py"],
    "modules/08_video_prompt.md": [
        "shared/standard_specs.md", "shared/aesthetic_system.md",
        "shared/context_ledger.md", "shared/negative_words.md",
        "engines/camera_engine.md", "engines/continuity_engine.md",
        "engines/audio_engine.md", "engines/model_adapter.md",
        "scripts/validate_duration.py", "scripts/validate_prompt.py", "scripts/validate_workflow.py"],
}

LINK_RE = re.compile(r"\]\(([^)]+)\)")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main(argv=None):
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    errors, checks = [], {}

    missing = [f for f in REQUIRED_FILES if not os.path.exists(os.path.join(root, f))]
    checks["required_files"] = {"missing": missing, "total": len(REQUIRED_FILES)}
    if missing:
        errors.append(f"缺失文件: {missing}")

    skill = os.path.join(root, "SKILL.md")
    chain_ok = False
    if os.path.exists(skill):
        text = read(skill)
        pos = -1
        chain_ok = True
        for ref in MAIN_FLOW:
            idx = text.find(ref, pos + 1)
            if idx == -1:
                chain_ok = False
                errors.append(f"SKILL.md 六节点主线缺失或乱序: {ref}")
            else:
                pos = idx
    else:
        errors.append("SKILL.md 不存在，无法校验主线")
    checks["main_flow"] = {"ok": chain_ok, "flow": MAIN_FLOW}

    hard_deps = []
    m7 = os.path.join(root, "modules/07_storyboard_gen.md")
    m8 = os.path.join(root, "modules/08_video_prompt.md")
    for path, refs, label in [
        (m7, ["modules/01_script.md", "modules/02_storyboard.md"], "07 强依赖 01/02"),
        (m8, ["modules/02_storyboard.md", "modules/07_storyboard_gen.md"], "08 依赖 02/07"),
    ]:
        if os.path.exists(path):
            text = read(path)
            for ref in refs:
                if ref not in text:
                    hard_deps.append(f"{label}: {ref} 未引用")
                    errors.append(f"{label}: {ref} 未引用")
        else:
            hard_deps.append(f"{label}: {path} 不存在")
    checks["hard_dependencies"] = {"missing": hard_deps, "ok": not hard_deps}

    matrix_report = []
    for rel, deps in DEPENDENCY_MATRIX.items():
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            matrix_report.append({"module": rel, "missing": deps, "error": "文件不存在"})
            continue
        text = read(path)
        absent = [d for d in deps if d not in text]
        matrix_report.append({"module": rel, "required": len(deps),
                              "missing": absent, "ok": not absent})
        if absent:
            errors.append(f"{rel} 依赖缺失: {absent}")
    checks["dependency_matrix"] = matrix_report

    engine_report = []
    for rel in ["engines/camera_engine.md", "engines/fight_engine.md",
                "engines/reverse_engine.md", "engines/layout_engine.md",
                "engines/continuity_engine.md", "engines/audio_engine.md",
                "engines/specialty_engine.md", "engines/model_adapter.md"]:
        path = os.path.join(root, rel)
        text = read(path) if os.path.exists(path) else ""
        scripts = [s for s in ["validate_duration.py", "validate_layout.py",
                               "validate_workflow.py", "validate_prompt.py",
                               "validate_assets.py", "calc_ratio.py", "calc_head_body.py"]
                   if s in text]
        engine_report.append({"engine": rel, "script_refs": scripts,
                              "ok": bool(scripts)})
        if not scripts:
            errors.append(f"{rel} 未引用任何校验脚本")
    checks["engine_script_refs"] = engine_report

    broken_links = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if ".git" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            text = read(path)
            for target in LINK_RE.findall(text):
                target = target.strip().split()[0]
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                resolved = os.path.normpath(os.path.join(dirpath, target))
                if not os.path.exists(resolved):
                    broken_links.append({"file": os.path.relpath(path, root), "target": target})
    checks["markdown_links"] = {"broken": broken_links, "ok": not broken_links}
    if broken_links:
        errors.append(f"失效相对链接: {broken_links}")

    report = {
        "repo_root": root,
        "checks": checks,
        "errors": errors,
        "pass": not errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
