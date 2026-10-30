#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_duration.py — 时长/时间轴/快切/模型档校验（JSON）。

输入：一个 JSON 文件（schema 见 tests/fixtures/duration_valid.json）。
校验项：
  1. shots 非空、id 唯一、时间轴从 0 开始且零缝隙；
  2. 末尾不超出 editorial_duration_s；
  3. fps>0 且每镜帧数近似整数；
  4. 台词 speech+pause <= 镜长（动作可与台词重叠，不重复计时）；
  5. 连续快切（<=1s）不超过 8 镜；
  6. 升格/降格段 fps 合法且总时长 <= 全片 30%；
  7. 生成段时长属于 generation_duration_options（若提供）。
退出码：0 通过；1 校验失败；2 用法/文件错误。
"""
import json
import math
import sys

FPS_TOL = 0.05
TIME_TOL = 0.001
FAST_CUT_MAX = 8
RAMP_MAX_RATIO = 0.30


def errs(messages):
    sys.stderr.write(json.dumps({"errors": messages}, ensure_ascii=False) + "\n")
    return 1


def validate(data):
    errors, warnings = [], []
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        return errs(["shots 必须为非空列表"])

    editorial = data.get("editorial_duration_s")
    if not (isinstance(editorial, (int, float)) and editorial > 0):
        return errs(["editorial_duration_s 必须为正数"])
    fps = data.get("fps")
    if not (isinstance(fps, (int, float)) and fps > 0):
        return errs(["fps 必须为正数"])

    ids, prev_end = set(), 0.0
    fast_run = 0
    ramp_total = 0.0
    options = data.get("generation_duration_options")
    if options is not None and (not isinstance(options, list) or any(
            not isinstance(x, (int, float)) or x <= 0 for x in options)):
        errors.append("generation_duration_options 必须为正数列表")

    for i, shot in enumerate(shots):
        sid = shot.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"shot[{i}].id 缺失")
            continue
        if sid in ids:
            errors.append(f"镜号重复: {sid}")
        ids.add(sid)
        start, end = shot.get("start"), shot.get("end")
        if not (isinstance(start, (int, float)) and isinstance(end, (int, float))):
            errors.append(f"{sid}: start/end 必须为数值")
            continue
        if i == 0 and abs(start - 0.0) > TIME_TOL:
            errors.append(f"{sid}: 首镜必须从 0 开始，实际 {start}")
        if i > 0 and abs(start - prev_end) > TIME_TOL:
            errors.append(f"{sid}: 时间轴缝隙 start={start} != prev_end={prev_end}")
        if end <= start:
            errors.append(f"{sid}: end({end}) <= start({start})")
        dur = end - start
        prev_end = end
        frames = dur * fps
        if abs(frames - round(frames)) > FPS_TOL:
            warnings.append(f"{sid}: 帧数非整数 frames={round(frames,3)}")
        dialogue = shot.get("dialogue")
        if isinstance(dialogue, dict):
            sp = dialogue.get("speech_seconds", 0)
            pa = dialogue.get("pause_seconds", 0)
            if not (isinstance(sp, (int, float)) and isinstance(pa, (int, float))
                    and sp >= 0 and pa >= 0):
                errors.append(f"{sid}: 台词/停顿秒数必须为非负数")
            elif sp + pa > dur + TIME_TOL:
                errors.append(f"{sid}: speech({sp})+pause({pa}) 超过镜长 {dur}")
        segments = shot.get("generation_segments", [])
        for seg in segments:
            md = seg.get("model_duration_s")
            if not (isinstance(md, (int, float)) and md > 0):
                errors.append(f"{sid}: 生成段 model_duration_s 非法")
            elif options is not None and not any(abs(md - x) <= 0.05 for x in options):
                errors.append(f"{sid}: 生成段 {md}s 不在模型档 {options}")

        if dur <= 1.0:
            fast_run += 1
            if fast_run > FAST_CUT_MAX:
                errors.append(f"{sid}: 连续快切超过 {FAST_CUT_MAX} 镜")
        else:
            fast_run = 0

        for ramp in shot.get("speed_ramps", []):
            rfps, rs, re = ramp.get("fps"), ramp.get("start_s"), ramp.get("end_s")
            if not (isinstance(rfps, (int, float)) and rfps > 0
                    and isinstance(rs, (int, float)) and isinstance(re, (int, float))
                    and 0 <= rs < re <= editorial + TIME_TOL):
                errors.append(f"{sid}: 变速段参数非法 {ramp}")
            else:
                ramp_total += re - rs

    if prev_end > editorial + TIME_TOL:
        errors.append(f"时间轴末尾 {prev_end}s 超出总长 {editorial}s")
    if ramp_total > editorial * RAMP_MAX_RATIO + TIME_TOL:
        errors.append(f"变速总时长 {round(ramp_total,2)}s 超过全片 30%")

    report = {
        "file": None,
        "shots": len(shots),
        "editorial_duration_s": editorial,
        "fps": fps,
        "fast_cut_max": FAST_CUT_MAX,
        "generation_options": options,
        "errors": errors,
        "warnings": warnings,
        "pass": not errors,
    }
    return report


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        sys.stderr.write("用法: validate_duration.py <duration.json>\n")
        return 2
    path = argv[0]
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(json.dumps({"error": f"读取失败: {e}"}, ensure_ascii=False) + "\n")
        return 2
    result = validate(data)
    if isinstance(result, int):
        return result
    result["file"] = path
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
