#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calc_head_body.py — 头身公式计算与锚点输出（JSON）。

公式（唯一式，见 shared/standard_specs.md SP-07）：
  head_length = height / head_count

优先级：显式 N（head-count）> 显式头长（head-length）> 身高估算（约 20cm）。
同时给出 head-count 与 head-length 时校验一致性（容差 0.5cm）。

用法：
  python3 calc_head_body.py --height-cm 180 [--head-length-cm 20 | --head-count 9]
退出码：0 成功；2 参数非法或一致性失败。
"""
import argparse
import json
import math
import sys

ESTIMATED_HEAD_LENGTH_CM = 20.0
TOLERANCE_CM = 0.5


def parse_args(argv):
    p = argparse.ArgumentParser(description="头身公式计算")
    p.add_argument("--height-cm", required=True, type=float)
    p.add_argument("--head-length-cm", type=float, default=None)
    p.add_argument("--head-count", type=float, default=None)
    return p.parse_args(argv)


def anchors(n):
    return {
        "shoulder_line": 1.35,
        "chest_line": 2.0,
        "waist_elbow_line": 3.0,
        "hip_line": round(n / 2, 3),
        "knee_line": round(n * 0.75, 3),
        "ankle_line": round(n * 0.93, 3),
        "fingertip_line": round(n * 0.4, 3),
        "unit": "head_length",
    }


def main(argv=None):
    args = parse_args(argv)
    h = args.height_cm
    hl = args.head_length_cm
    n = args.head_count
    if not (math.isfinite(h) and h > 0):
        sys.stderr.write(json.dumps(
            {"error": "--height-cm 必须为正数"}, ensure_ascii=False) + "\n")
        return 2
    if hl is not None and not (math.isfinite(hl) and hl > 0):
        sys.stderr.write(json.dumps(
            {"error": "--head-length-cm 必须为正数"}, ensure_ascii=False) + "\n")
        return 2
    if n is not None and not (math.isfinite(n) and 0 < n <= 20):
        sys.stderr.write(json.dumps(
            {"error": "--head-count 必须在 (0,20] 区间"}, ensure_ascii=False) + "\n")
        return 2

    basis = None
    if hl is not None and n is not None:
        if abs(hl - h / n) > TOLERANCE_CM:
            sys.stderr.write(json.dumps({
                "error": "一致性失败",
                "detail": f"head_length={hl}cm 与 height/head_count={round(h/n,3)}cm 偏差超过容差 {TOLERANCE_CM}cm",
            }, ensure_ascii=False) + "\n")
            return 2
        basis = "both_provided"
    elif hl is not None:
        n = h / hl
        basis = "head_length_provided"
    elif n is not None:
        hl = h / n
        basis = "head_count_provided"
    else:
        hl = ESTIMATED_HEAD_LENGTH_CM
        n = h / hl
        basis = "height_only_estimate_20cm"

    n = round(n, 4)
    hl = round(hl, 4)
    warnings = []
    if not (2.0 <= n <= 12.0):
        warnings.append("head_count 超出常用区间 [2,12]，请确认设定")
    if basis == "height_only_estimate_20cm":
        warnings.append("仅身高：按成年人约 20cm 头长估算；默认 N=9 不反推固定 20cm")

    print(json.dumps({
        "input": {"height_cm": h, "head_length_cm": args.head_length_cm,
                  "head_count": args.head_count},
        "result": {
            "head_count": n,
            "head_length_cm": hl,
            "basis": basis,
            "anchors": anchors(n),
        },
        "warnings": warnings,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
