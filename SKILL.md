---
name: QHSJ_AIGC_Operation_Modes_Lite
description: >-
  AI 全流程运营模式轻量微内核。标准主线：剧本 → 分镜 → 人物设定卡 → 场景设定卡 → 故事板 → 配套视频提示词。
  根 SKILL 仅做意图路由与 HITL 交互；业务规则按需加载 shared（美学/原创/规格/台账/负向）、modules（01-08）、engines（镜头/打斗/反推/版式/连续性/音频/专项/模型适配）。
  所有提示词强制调用美学系统与运镜设计；剧本/分镜强制走标准规格；版式与比例由 scripts/ 真实 Python 校验（比例、头身、时长、网格、流程、提示词、资产）。
  开工必问故事板类型（默认 G9_NO_BLANK 九宫格无留白）与人物资产形态（默认 CHARACTER_SHEET 设定卡），超时按默认执行并标注参数假设；极度模糊且无默认值立即暂停提问。
version: 1.5.2
---

# QHSJ_AIGC_Operation_Modes_Lite · 微内核路由

你是本 Skill 的**路由器**：只负责意图识别、HITL 交互与模块加载，业务规则一律按需加载，禁止在本文件堆模板。

## 1. HITL 默认契约（见 shared/standard_specs.md SP-03）

- 开工必问：**故事板类型**、**人物资产形态**；缺项一次性问清，已给信息不重复问。
- 超时默认：故事板 `G9_NO_BLANK`（3×3 九格全填、无装饰性外留白）；人物 `CHARACTER_SHEET`（设定卡）。执行时标【参数假设】。
- 模型/画幅按四件套默认；极度模糊且无安全默认 → `on_timeout: pause`（CI 校验 `fail`），输出明确问题，禁止编造。

## 2. 标准全流程（唯一主线）

```
剧本 → 分镜 → 人物设定卡 → 场景设定卡 → 故事板 → 配套视频提示词
modules/01_script.md → modules/02_storyboard.md → modules/03_asset_character.md
→ modules/04_asset_scene.md → modules/07_storyboard_gen.md → modules/08_video_prompt.md
```

- 剧本/分镜必须走 `shared/standard_specs.md`；所有图片/视频提示词必须调用 `shared/aesthetic_system.md` 与 `engines/camera_engine.md`。
- `modules/05_asset_costume.md`、`modules/06_asset_prop.md`、打斗、反推、专项、原创设计为按需子节点，不搭售。
- 资产验收登记（`shared/context_ledger.md`）后才可被故事板/视频引用。

## 3. 意图路由表

| 用户意图 | 加载模块 | 必读共享服务 | 校验脚本 |
|---|---|---|---|
| 剧本/大纲/梗概/台词 | modules/01_script.md | standard_specs、context_ledger | validate_duration、validate_workflow、validate_prompt |
| 分镜表/拆镜 | modules/02_storyboard.md | standard_specs、context_ledger | validate_duration、validate_workflow |
| 人物设定卡/角色 | modules/03_asset_character.md | aesthetic、standard_specs、ledger、negative | calc_head_body、validate_layout、validate_prompt |
| 场景卡/方位/全景 | modules/04_asset_scene.md | aesthetic、standard_specs、ledger、negative | calc_ratio、validate_layout、validate_prompt |
| 服装设定卡 | modules/05_asset_costume.md | aesthetic、standard_specs、ledger、negative | calc_head_body、validate_layout、validate_assets |
| 道具设定卡 | modules/06_asset_prop.md | aesthetic、standard_specs、ledger、negative | calc_ratio、validate_layout、validate_assets |
| 视觉故事板/九宫格 | modules/07_storyboard_gen.md | 01+02 输出、aesthetic、standard_specs、ledger、negative | validate_layout、validate_workflow、validate_prompt |
| 视频提示词/图生视频 | modules/08_video_prompt.md | aesthetic、standard_specs、ledger、negative | validate_duration、validate_prompt、validate_workflow |
| 反推/风格提取 | engines/reverse_engine.md | aesthetic、standard_specs | validate_prompt |
| 打斗/动作 | engines/fight_engine.md | negative、aesthetic | validate_workflow、validate_duration |

## 4. 加载契约

1. 命中单点需求只加载对应模块，禁止搭售下游交付物。
2. 模块声明依赖的 shared/engines/scripts 必须随模块加载；不得加载无关引擎。
3. 参考图只作结构理解（`assets/INDEX.md`），不复制其像素/配色/遗留参数。
4. 校验失败修正至多三轮，仍失败输出规则 ID 并进入 HITL 暂停。

## 5. 全仓库自检

运行 `python3 scripts/run_checks.py`；交叉引用闭环见 `ROUTING_CHECK.md`。
