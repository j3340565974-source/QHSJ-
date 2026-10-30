#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_assets.py — 图片资产哈希、INDEX 与引用校验。

校验项：
  1. assets/ 下恰好 15 张预期 PNG，SHA256 与原压缩包逐字节一致（无损）；
  2. assets/INDEX.md 存在且覆盖全部 15 个英文文件名；
  3. 仓库全部 Markdown 图片链接指向的文件真实存在；
  4. 每张预期图片至少被一处引用（INDEX 或模块）。
退出码：0 通过；1 校验失败。
"""
import hashlib
import json
import os
import re
import sys

# 英文文件名 -> 原始 SHA256（由原压缩包计算，只读比对）
EXPECTED = {
    "scene_sheet_21x9.png":
        "0eb16e913b1dede4e97882495682a77b21cb17a4f32d15bafea546a9dc187f61",
    "scene_sheet_9x16.png":
        "8b9c3f8470d268486808b1d7693270a138a11ca7e544822bb21dd327e10f13d9",
    "prop_sheet_white.png":
        "284d1725d22de7668928a58142930e057cef9a1c845eecee8e34ed14dbacad29",
    "costume_sheet_white.png":
        "8794097e6b7623850a1f82ce0589f2c30d86e8e08224bf391ad4ceea5e64d0df",
    "storyboard_white_model_16x9.png":
        "7876e9b9b4fad21d67c18d13d47058bacb1fac7388ef31f7ac579920b41beedd",
    "storyboard_white_model_9x16.png":
        "9099a3f5ec4c1052640625daeb010493f8f602397592fcaada7226813b94a976",
    "aspect_ratio_adaptation.png":
        "f7082b7154d0857abbf107298c2056b0c2b92989f69505e0ae5d0893b214582f",
    "universal_layout_engine.png":
        "ccf54881d4a9eb5d5392357a8f8e34d8f61eed6961d1d203e0a6b1105a4989c8",
    "grid_modes_nine_grid.png":
        "ef8790747ad246329051d9772f6ad8cf9d1134ae87ef5d5c5e9381d78fe721f6",
    "interior_direction_sheet.png":
        "4cb0a0f42b3e9d9d288e68ba83d46a0c65bd61ab43db94e174e07d5070989326",
    "material_modes_m1_m5.png":
        "7f79c35c387a925671733aa10dbbdb26d1f91e644d9b72802d26fc2896e785ed",
    "exterior_panorama_sheet.png":
        "11163a7be3ebe703aace9f3d99a633f2880ee4b1d63b5366b3e9df435d307db0",
    "universal_style_formula.png":
        "bb7d8a3bdff836a96ccb4a6fbd2b4899e0751104ff5aad7fb2e0d51fe17680a6",
    "scene_formula_horizontal.png":
        "b98ef601493fce0e563912928b5f26cffa7071dede67b850cd2f095e606f3cd4",
    "scene_formula_vertical.png":
        "f3a02c53623714f292e8870440c406af8b6a5d6d7bc614a3d61b669b9d61712b",
}

IMG_RE = re.compile(r"\]\(([^)\s]+\.png)\)")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    errors = []
    asset_dir = os.path.join(root, "assets")

    pngs = sorted(f for f in os.listdir(asset_dir)
                  if f.lower().endswith(".png")) if os.path.isdir(asset_dir) else []
    extra = [f for f in pngs if f not in EXPECTED]
    missing_names = [f for f in EXPECTED if f not in pngs]
    hash_mismatch = []
    for name in EXPECTED:
        path = os.path.join(asset_dir, name)
        if os.path.exists(path) and sha256(path) != EXPECTED[name]:
            hash_mismatch.append(name)
    if extra:
        errors.append(f"多余图片: {extra}")
    if missing_names:
        errors.append(f"缺失图片: {missing_names}")
    if hash_mismatch:
        errors.append(f"SHA256 不一致（非无损复制）: {hash_mismatch}")

    index_path = os.path.join(asset_dir, "INDEX.md")
    index_ok = False
    if os.path.exists(index_path):
        text = open(index_path, encoding="utf-8").read()
        uncovered = [name for name in EXPECTED if name not in text]
        if uncovered:
            errors.append(f"INDEX.md 未覆盖: {uncovered}")
        else:
            index_ok = True
    else:
        errors.append("assets/INDEX.md 不存在")

    referenced = set()
    broken = []
    for dirpath, _dirs, filenames in os.walk(root):
        if ".git" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8").read()
            for target in IMG_RE.findall(text):
                resolved = os.path.normpath(os.path.join(dirpath, target))
                if not os.path.exists(resolved):
                    broken.append({"file": os.path.relpath(path, root), "target": target})
                else:
                    referenced.add(os.path.basename(resolved))
    unreferenced = [name for name in EXPECTED if name not in referenced]
    if broken:
        errors.append(f"失效图片链接: {broken}")
    if unreferenced:
        errors.append(f"未被任何文档引用的图片: {unreferenced}")

    report = {
        "expected": len(EXPECTED),
        "found": len(pngs),
        "extra": extra,
        "missing": missing_names,
        "hash_mismatch": hash_mismatch,
        "index_ok": index_ok,
        "unreferenced": unreferenced,
        "broken_links": broken,
        "errors": errors,
        "pass": not errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
