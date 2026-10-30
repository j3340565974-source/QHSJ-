#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_layout.py — 版式/网格/几何校验（JSON）。

校验项（依据 shared/standard_specs.md 与 engines/layout_engine.md）：
  1. 网格公式 cell_r = canvas_r * rows / columns（gap=0 时）；
  2. 故事板空白策略 G9_NO_BLANK：filled_cells=rows*columns、empty_cells=0；
  3. 外边距 <=1.5%、模块间距 <=1.5%；
  4. 面积配比归一化（areas_normalized=true 时合计 100）且主视觉为最大板块；
  5. 服装几何：一个 1:1 区域纵分三个 1:3；
  6. 全景 2:1 / 360°×180°。
退出码：0 通过；1 校验失败；2 用法/文件错误。
"""
import json
import sys

CELL_TOL = 1e-4
AREA_TOL = 1.0


def fail(messages):
    sys.stderr.write(json.dumps({"errors": messages}, ensure_ascii=False) + "\n")
    return 1


def validate(data):
    errors = []
    canvas = data.get("canvas") or {}
    cw, ch = canvas.get("width"), canvas.get("height")
    if not (isinstance(cw, (int, float)) and isinstance(ch, (int, float))
            and cw > 0 and ch > 0):
        errors.append("canvas.width/height 必须为正数")
        cw = ch = None

    grid = data.get("grid") or {}
    rows, cols = grid.get("rows"), grid.get("columns")
    if not (isinstance(rows, int) and isinstance(cols, int) and rows > 0 and cols > 0):
        errors.append("grid.rows/columns 必须为正整数")
    else:
        if cw is not None:
            expected = (cw / ch) * rows / cols
            got = grid.get("cell_aspect_r")
            if not isinstance(got, (int, float)) or abs(got - expected) > CELL_TOL:
                errors.append(
                    f"网格公式不成立: cell_aspect_r={got}, 期望 {round(expected,6)} "
                    f"(cell_r = canvas_r * rows / columns)")
        blank = grid.get("blank_policy", "")
        filled = grid.get("filled_cells")
        empty = grid.get("empty_cells")
        if blank == "G9_NO_BLANK" or grid.get("name") == "G9":
            if rows != 3 or cols != 3:
                errors.append("G9 网格必须为 3×3")
            if filled != rows * cols:
                errors.append(f"G9_NO_BLANK: filled_cells={filled} != 9")
            if empty != 0:
                errors.append(f"G9_NO_BLANK: empty_cells={empty} != 0")
        if grid.get("outer_blank"):
            errors.append("故事板禁止装饰性外留白（outer_blank=true）")

    margins = data.get("margins") or {}
    outer = margins.get("outer_margin_pct")
    gap = margins.get("module_gap_pct")
    if isinstance(outer, (int, float)) and outer > 1.5 + 1e-9:
        errors.append(f"outer_margin_pct={outer} 超过 1.5%")
    if isinstance(gap, (int, float)) and gap > 1.5 + 1e-9:
        errors.append(f"module_gap_pct={gap} 超过默认 1.5%")

    areas = data.get("areas")
    if areas is not None:
        if not isinstance(areas, list) or not areas:
            errors.append("areas 必须为非空列表")
        elif data.get("areas_normalized", False):
            total = sum(a.get("area_pct", 0) for a in areas)
            if abs(total - 100) > AREA_TOL:
                errors.append(f"面积配比未归一化: 合计 {total}% != 100%")
            values = [a.get("area_pct", 0) for a in areas]
            main = areas[0]
            if areas[0].get("name") != "main":
                errors.append("第一块面积必须命名为 main（主视觉）")
            if any(v > main.get("area_pct", 0) + 1e-9 for v in values[1:]):
                errors.append("主视觉必须是全卡最大单一板块")

    costume = data.get("costume")
    if costume:
        split = costume.get("split") or {}
        if split.get("direction") != "vertical" or split.get("parts") != 3 \
                or split.get("each") != "1:3":
            errors.append("服装几何必须是：一个 1:1 区域纵分三个 1:3（废止旧三 1:1 格）")
        mh = costume.get("mannequin_height_pct")
        if isinstance(mh, (int, float)) and not (80 <= mh <= 100):
            errors.append(f"人台占格高度 {mh}% 超出 80–100 区间（默认 92%）")

    prop = data.get("prop")
    if prop and isinstance(prop.get("elongation_r"), (int, float)) and prop["elongation_r"] < 1:
        errors.append("elongation_r 必须 >=1（max/min）")

    panorama = data.get("panorama")
    if panorama:
        if panorama.get("aspect") != "2:1":
            errors.append("全景必须 2:1（equirectangular）")
        if panorama.get("fov_h") != 360 or panorama.get("fov_v") != 180:
            errors.append("全景视场必须为水平 360°×垂直 180°（720° 只作产品名）")

    report = {
        "file": None,
        "checks": {
            "grid_formula": "pass" if not any("网格公式" in e for e in errors) else "fail",
            "blank_policy": "pass" if not any("G9_NO_BLANK" in e or "outer_blank" in e for e in errors) else "fail",
            "margins": "pass" if not any("outer_margin" in e or "module_gap" in e for e in errors) else "fail",
            "areas": "pass" if not any("面积" in e or "main" in e for e in errors) else "fail",
            "costume": "pass" if not any("服装" in e or "人台" in e for e in errors) else "fail",
            "panorama": "pass" if not any("全景" in e for e in errors) else "fail",
        },
        "errors": errors,
        "pass": not errors,
    }
    return report


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        sys.stderr.write("用法: validate_layout.py <layout.json>\n")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(json.dumps({"error": f"读取失败: {e}"}, ensure_ascii=False) + "\n")
        return 2
    result = validate(data)
    if isinstance(result, int):
        return result
    result["file"] = argv[0]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
