# shared/context_ledger.md — 项目锚点台账（唯一状态源）

> Skill v1.5.2 共享服务。跨任务、跨模块、跨镜/跨条继承状态统一存放于此。模块只登记与读取，不私存第二份状态。

## LED-01 台账记录类型

| 记录 | 关键字段 | 写入者 |
|---|---|---|
| `project` | 四件套（图片模型/画幅/视频模型/补充说明）、`project_aspect`、`style_gene`、版本 | 开工确认、01 |
| `character` | 身份名、锁定描述、音色锚点、Want/Need、弧光、头身 N、资产地址 | 01、03 |
| `scene` | 场景名、时代/时刻+光线、空间结构、资产地址 | 01、04 |
| `prop` | 道具名、七形态、R 值、尺度、挂载人/位置 | 01、06 |
| `costume` | 服装清单、材质档 M6、所属人物 | 05 |
| `shot` | 镜号、首尾状态、站位、轴线、时长、转场 | 02、08 |
| `asset_registry` | 资产 ID、验收状态（`pending/accepted/rejected`）、验收人、哈希 | 03–06 |
| `state` | `base_anchor + state_delta → terminal_state` | 02、08、CON |

## LED-02 快照模型

- 每镜/每条/每张卡：`base_anchor + state_delta → terminal_state`。
- 下一镜/下一条默认以 `terminal_state` 为 `base_anchor`。
- 台账只保存差异（delta），完整状态由 `base + delta` 推导，避免整表复制。

## LED-03 站位与重置

- 首镜（或显式重置后）使用项目初始站位图。
- 时间跳跃/重新调度必须写 `state_reset`：`{reason, effective_shot}`；无记录的重置非法。

## LED-04 道具挂载与双手占用

- 持械手、随身件位置、双手占用逐镜登记；占用冲突（同时插袋与持物）由 `scripts/validate_workflow.py` 拦截。
- 掉落/拾取/交换必须登记去向。

## LED-05 伤痕与状态增量

- 伤痕：位置、程度、安全分级（FIG-04）、生效镜号。
- 状态（倒地/眩晕/受限）：默认持续到条末，恢复必须显式登记。

## LED-06 资产验收登记（故事板/视频前置条件）

- 人物/场景/道具/服装资产必须 `accepted` 才能被 07/08 引用。
- 生成模型无法保证 100% 还原：验收记录实际结果与失败重试轮次；三轮失败进入 HITL。

## LED-07 变更与继承

- 用户参数变更写入 `changes` 日志：旧值→新值、时间、影响范围。
- 跨任务沿用既有参数；新项目必须重新确认四件套，禁止直接套用上一项目。

## LED-08 消费接口

- `modules/01_script.md` 写入 `project_meta / characters[] / scenes[] / motifs[]`（SCRIPT_FACTS）。
- `modules/02_storyboard.md` 写入 `shots[]`（SHOTS），07/08 只读消费。
- 持久化格式：JSON；字段校验由 `scripts/validate_workflow.py` 与 `scripts/validate_prompt.py` 执行。
