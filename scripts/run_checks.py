#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_checks.py — 统一回归入口：运行全部校验脚本与正/反例夹具。

用法：python3 run_checks.py [--quiet]
退出码：0 全部通过；1 任一项失败或退出码不符合预期。
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
PY = sys.executable


def run(args, expect):
    proc = subprocess.run([PY, *args], cwd=ROOT, capture_output=True, text=True)
    ok = proc.returncode == expect
    return {
        "command": " ".join(args),
        "expected_exit": expect,
        "actual_exit": proc.returncode,
        "ok": ok,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
    }


def main():
    cases = [
        # calc_ratio.py
        (["scripts/calc_ratio.py", "--width", "1920", "--height", "1080"], 0),
        (["scripts/calc_ratio.py", "--width", "90", "--height", "20", "--kind", "object"], 0),
        (["scripts/calc_ratio.py", "--width", "16", "--height", "9", "--rows", "3", "--columns", "3"], 0),
        (["scripts/calc_ratio.py", "--width", "-1", "--height", "1080"], 2),
        (["scripts/calc_ratio.py", "--width", "16", "--height", "9", "--rows", "3"], 2),
        # calc_head_body.py
        (["scripts/calc_head_body.py", "--height-cm", "180"], 0),
        (["scripts/calc_head_body.py", "--height-cm", "172", "--head-count", "9"], 0),
        (["scripts/calc_head_body.py", "--height-cm", "180", "--head-length-cm", "20", "--head-count", "9"], 0),
        (["scripts/calc_head_body.py", "--height-cm", "180", "--head-length-cm", "20", "--head-count", "10"], 2),
        # validate_duration.py
        (["scripts/validate_duration.py", "tests/fixtures/duration_valid.json"], 0),
        (["scripts/validate_duration.py", "tests/fixtures/duration_invalid.json"], 1),
        # validate_layout.py
        (["scripts/validate_layout.py", "tests/fixtures/layout_valid.json"], 0),
        (["scripts/validate_layout.py", "tests/fixtures/layout_invalid.json"], 1),
        # validate_prompt.py
        (["scripts/validate_prompt.py", "tests/fixtures/prompt_valid.json"], 0),
        (["scripts/validate_prompt.py", "tests/fixtures/prompt_invalid.json"], 1),
        # 全仓库扫描
        (["scripts/validate_workflow.py"], 0),
        (["scripts/validate_assets.py"], 0),
    ]

    results = [run(args, expect) for args, expect in cases]
    failed = [r for r in results if not r["ok"]]
    report = {
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
        "pass": not failed,
    }
    if "--quiet" not in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
