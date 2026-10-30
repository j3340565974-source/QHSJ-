#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calc_ratio.py — 接收长宽参数，计算比例与 R 值，输出 JSON 版式推荐。

用法：
  python3 calc_ratio.py --width 1920 --height 1080 [--kind canvas|object] [--rows N --columns M]

退出码：0 成功；2 参数或数值非法。
"""
import argparse
import json
import math
import sys

# 常用标称比例（用于命名与误差计算）
NAMED_RATIOS = {
    "21:9": 21 / 9,
    "16:9": 16 / 9,
    "3:2": 3 / 2,
    "4:3": 4 / 3,
    "5:4": 5 / 4,
    "2:1": 2 / 1,
    "1:1": 1 / 1,
    "4:5": 4 / 5,
    "3:4": 3 / 4,
    "2:3": 2 / 3,
    "9:16": 9 / 16,
}

NAMED_TOLERANCE = 0.01


def nearest_named(ratio: float):
    best, best_err = None, None
    for name, value in NAMED_RATIOS.items():
        err = abs(ratio - value) / value
        if best_err is None or err < best_err:
            best, best_err = name, err
    if best_err is not None and best_err <= NAMED_TOLERANCE:
        return best, round(best_err * 100, 4)
    return None, None


def parse_args(argv):
    p = argparse.ArgumentParser(description="比例与 R 值计算 / 版式推荐")
    p.add_argument("--width", required=True, type=float, help="宽（或长边）")
    p.add_argument("--height", required=True, type=float, help="高（或短边）")
    p.add_argument("--kind", choices=["canvas", "object"], default="canvas",
                   help="canvas=画幅比例；object=道具长宽 R 值")
    p.add_argument("--rows", type=int, default=None, help="故事板行数（可选）")
    p.add_argument("--columns", type=int, default=None, help="故事板列数（可选）")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    w, h = args.width, args.height
    if not (math.isfinite(w) and math.isfinite(h) and w > 0 and h > 0):
        sys.stderr.write(json.dumps(
            {"error": "width/height 必须为正的有限数值"}, ensure_ascii=False) + "\n")
        return 2

    ratio = w / h
    elongation = max(w, h) / min(w, h)
    orientation = "landscape" if w > h else ("portrait" if h > w else "square")
    named, rel_err = nearest_named(ratio)

    out = {
        "input": {"width": w, "height": h, "kind": args.kind},
        "geometry": {
            "aspect_r": round(ratio, 6),
            "orientation": orientation,
            "named_ratio": named,
            "relative_error_pct": rel_err,
            "note": "相对误差仅在命名比例容差 1% 内给出；参考图不作像素真值",
        },
        "object": {
            "elongation_r": round(elongation, 6),
            "form_candidate": (
                "L1_L2_long (R>=3)" if elongation >= 3 else "B1_B2_block_or_thin (1<=R<3)"),
            "note": "薄片判定需厚度（见 modules/06_asset_prop.md 06-02）",
        },
    }

    if args.kind == "object":
        out["layout_recommendation"] = (
            "横向三层（正/背/侧），长物体禁止竖放斜置" if elongation >= 3
            else "居中主图 + 右侧正/侧/顶视图")
    else:
        rec = {
            "landscape": "横版：板块多/细节多优先 16:9、3:2、21:9",
            "portrait": "竖版：站姿全身主体或信息流优先 9:16、2:3、3:4",
            "square": "方形：单主体极简 1:1",
        }[orientation]
        out["layout_recommendation"] = rec

    if args.rows is not None or args.columns is not None:
        if args.rows is None or args.columns is None or args.rows <= 0 or args.columns <= 0:
            sys.stderr.write(json.dumps(
                {"error": "--rows 与 --columns 必须同时给出且为正整数"},
                ensure_ascii=False) + "\n")
            return 2
        cell_r = ratio * args.rows / args.columns
        out["grid"] = {
            "rows": args.rows,
            "columns": args.columns,
            "formula": "cell_r = canvas_r * rows / columns",
            "cell_aspect_r": round(cell_r, 6),
            "blank_policy": (
                "G9_NO_BLANK（3×3 九格全填、无装饰性外留白）"
                if args.rows == 3 and args.columns == 3 else None),
        }

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
