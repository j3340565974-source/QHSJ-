# ROUTING_CHECK.md — 依赖闭环核对清单

> 用途：证明每个模块/引擎的依赖（shared/engines/scripts/assets）全部闭环，不存在孤岛。静态矩阵与 `scripts/validate_workflow.py` 的依赖矩阵逐字一致；实测结果见文末。

## 1. 模块依赖矩阵（蓝图：stage1-audit.md §5.2）

| 模块 | shared 依赖 | engines 依赖 | scripts 校验 | assets 引用 | 闭环 |
|---|---|---|---|---|---|
| modules/01_script.md | standard_specs、context_ledger | —（文字交付，不受美学门） | validate_duration、validate_workflow、validate_prompt | — | 见实测 |
| modules/02_storyboard.md | standard_specs、context_ledger | camera、continuity、audio | validate_duration、validate_workflow | — | 见实测 |
| modules/03_asset_character.md | aesthetic、standard_specs、ledger、negative | camera | calc_head_body、validate_layout、validate_prompt | 无专属图（明示禁止冒用） | 见实测 |
| modules/04_asset_scene.md | aesthetic、standard_specs、ledger、negative | camera、layout | calc_ratio、validate_layout、validate_prompt | 6 张场景/方位/全景/公式图 | 见实测 |
| modules/05_asset_costume.md | aesthetic、standard_specs、ledger、negative | camera、layout | calc_head_body、validate_layout、validate_assets | costume_sheet_white.png | 见实测 |
| modules/06_asset_prop.md | aesthetic、standard_specs、ledger、negative | layout | calc_ratio、validate_layout、validate_assets | prop_sheet_white.png | 见实测 |
| modules/07_storyboard_gen.md | 01+02 输出、aesthetic、standard_specs、ledger、negative | camera、layout | validate_layout、validate_workflow、validate_prompt | 4 张故事板/网格/材质图 | 见实测 |
| modules/08_video_prompt.md | aesthetic、standard_specs、ledger、negative | camera、continuity、audio、model_adapter | validate_duration、validate_prompt、validate_workflow | — | 见实测 |

## 2. 引擎脚本引用（蓝图：stage1-audit.md §5.3/5.4）

| 引擎 | 引用校验脚本 | 闭环 |
|---|---|---|
| engines/camera_engine.md | validate_prompt | 见实测 |
| engines/fight_engine.md | validate_workflow、validate_duration | 见实测 |
| engines/reverse_engine.md | validate_prompt | 见实测 |
| engines/layout_engine.md | validate_layout | 见实测 |
| engines/continuity_engine.md | validate_workflow、validate_duration | 见实测 |
| engines/audio_engine.md | validate_duration、validate_prompt | 见实测 |
| engines/specialty_engine.md | validate_prompt、validate_duration | 见实测 |
| engines/model_adapter.md | validate_prompt | 见实测 |

## 3. 主线与硬依赖

- 六节点主线：`01 → 02 → 03 → 04 → 07 → 08`（SKILL.md 顺序引用）。
- 07 强依赖 01/02；08 依赖 02/07。
- 所有提示词模块 AE（美学）+ CAM（运镜）强制调用。
- 资产验收登记（context_ledger）后才可被 07/08 引用。

## 4. 自动校验证据

> 由 `scripts/run_checks.py` + `scripts/validate_workflow.py` + `scripts/validate_assets.py` 实测生成（2026-10-30）。

| 检查 | 结果 |
|---|---|
| run_checks.py 全量回归（正反例夹具 + 全仓扫描） | **17/17 通过，exit=0** |
| 必需文件存在性 | 33/33 存在，缺失 0 |
| 六节点主线顺序引用（SKILL.md） | 通过（01→02→03→04→07→08 顺序完整） |
| 07 强依赖 01/02；08 依赖 02/07 | 通过，缺失 0 |
| 八模块依赖矩阵（shared/engines/scripts 全命中） | 通过，缺失 0（01:5、02:7、03:8、04:9、05:9、06:8、07:11、08:11） |
| 八引擎校验脚本引用 | 通过（每个引擎至少引用 1 个脚本） |
| Markdown 相对链接 | 通过，失效链接 0 |
| 15 图 SHA256 与原压缩包一致（无损） | 15/15 一致，多余 0、缺失 0 |
| assets/INDEX.md 覆盖 | 覆盖 15/15 |
| 图片引用完整性 | 15/15 被引用，失效图片链接 0 |
| 反例夹具（快切>8、空格、AE 缺失/残留变量） | 全部按预期失败（exit=1），校验逻辑有效 |
| 正例夹具（时长/版式/提示词） | 全部通过（exit=0） |

**结论：所有模块与引擎的依赖闭环成立，无孤岛文件。**

