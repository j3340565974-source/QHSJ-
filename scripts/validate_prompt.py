#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_prompt.py — 提示词装配契约校验（JSON）。

校验项（依据 shared/standard_specs.md SP-11 与 aesthetic_system.md AE-06）：
  1. aesthetic_called 与 camera_called 必须为 true（AE/CAM 强制调用）；
  2. negative_source 必须指向 shared/negative_words.md；
  3. canvas_aspect 属于合法画幅集合；
  4. 模型字段 provider/model 非空；
  5. segments 非空且文本无残留未替换变量 {{}}；
  6. 白名单命中必须带 reason；
  7. text_len <= char_limit（若提供）。
退出码：0 通过；1 校验失败；2 用法/文件错误。
"""
import json
import os
import sys

VALID_ASPECTS = {"1:1", "4:3", "3:2", "16:9", "21:9", "3:4", "2:3", "4:5", "9:16", "2:1", "custom"}
NEGATIVE_SOURCE = "shared/negative_words.md"


def walk_strings(obj):
    """递归遍历所有字符串值。"""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_strings(v)


def validate(data, repo_root=None):
    errors = []
    module = data.get("module")
    if not isinstance(module, str) or not module:
        errors.append("module 字段缺失")
    if data.get("aesthetic_called") is not True:
        errors.append("aesthetic_called 必须为 true（强制调用 shared/aesthetic_system.md）")
    if data.get("camera_called") is not True:
        errors.append("camera_called 必须为 true（强制调用 engines/camera_engine.md 运镜设计）")
    ns = data.get("negative_source")
    if ns != NEGATIVE_SOURCE:
        errors.append(f"negative_source 必须为 {NEGATIVE_SOURCE}，实际 {ns!r}")
    elif repo_root and not os.path.exists(os.path.join(repo_root, NEGATIVE_SOURCE)):
        errors.append(f"负向装配来源文件不存在: {NEGATIVE_SOURCE}")
    aspect = data.get("canvas_aspect")
    if aspect not in VALID_ASPECTS:
        errors.append(f"canvas_aspect={aspect!r} 不在合法集合 {sorted(VALID_ASPECTS)}")
    model = data.get("model") or {}
    if not model.get("provider") or not model.get("model"):
        errors.append("model.provider / model.model 必须非空")
    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        errors.append("segments 必须为非空列表")
    else:
        for i, seg in enumerate(segments):
            text = seg.get("text") if isinstance(seg, dict) else None
            if not text:
                errors.append(f"segments[{i}].text 缺失")
            elif "{{" in text or "}}" in text:
                errors.append(f"segments[{i}] 存在未替换变量")
    for entry in data.get("whitelist", []):
        if isinstance(entry, dict) and not entry.get("reason"):
            errors.append(f"白名单条目缺少 reason: {entry}")
    if "char_limit" in data and "text_len" in data:
        if not (isinstance(data["char_limit"], int) and isinstance(data["text_len"], int)
                and data["text_len"] >= 0):
            errors.append("char_limit/text_len 必须为非负整数")
        elif data["text_len"] > data["char_limit"]:
            errors.append(f"text_len={data['text_len']} 超过 char_limit={data['char_limit']}")

    report = {
        "file": None,
        "module": module,
        "aesthetic_called": data.get("aesthetic_called"),
        "camera_called": data.get("camera_called"),
        "negative_source": ns,
        "canvas_aspect": aspect,
        "errors": errors,
        "pass": not errors,
    }
    return report


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        sys.stderr.write("用法: validate_prompt.py <prompt.json>\n")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(json.dumps({"error": f"读取失败: {e}"}, ensure_ascii=False) + "\n")
        return 2
    repo_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    result = validate(data, repo_root)
    if isinstance(result, int):
        return result
    result["file"] = argv[0]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
