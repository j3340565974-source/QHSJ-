# 连续性引擎（CON）

> 用途：跨镜、跨条、跨卡的站位、轴线、道具、伤痕与状态继承。数据唯一存放在 `shared/context_ledger.md`，本文件定义校验规则。

## CON-01 快照模型

- 每镜/每条：`base_anchor + state_delta → terminal_state`。
- `base_anchor`：初始站位图、初始伤态、道具挂载、外观、天气/时间。
- `state_delta`：本镜发生的状态变化（位移、伤、掉落、更换）。
- 下一镜/下一条默认以 `terminal_state` 为 `base_anchor`。

## CON-02 站位继承

- 首镜（或显式重置后）使用项目初始站位。
- 后续镜/条继承上一终态站位；时间跳跃或重新调度必须写 `state_reset`：原因 + 生效镜号。
- 四方位/三视图资产按卡种独立，不参与叙事站位继承。

## CON-03 轴线与朝向

- 对话与对峙维持 180° 轴线；屏幕方向用 `screen_angle = normalize(character_facing - camera_view_direction + 180°)`。
- 越轴必须声明理由；重置后重定场。

## CON-04 道具挂载与双手占用

- 持械手、随身件位置、双手占用写入台账；禁止同一镜双手占用冲突（如同时插袋与持物）。
- 武器/道具掉落、拾取、交换必须登记去向；`BENIGN` 接触不产生伤害链（见 FIG）。

## CON-05 伤痕与状态增量

- 伤痕按安全分级登记：位置、程度、后续镜号生效。
- 状态（倒地、眩晕、受限）必须明确恢复/持续；无恢复记录则默认持续到条末。

## CON-06 服装与外观锁定

- 同一场/连续时间线内：服装、发型、妆容、随身道具与上一终态一致。
- 服装三视图清单必须完全一致（`modules/05_asset_costume.md`）；视频沿用图片阶段确定的质感与色彩系统。

## CON-07 时间与天气

- 时间线单调：`start ≤ end`，相邻镜 `start == prev_end`（容差由时长校验脚本定义）。
- 天气/光照突变必须显式声明时间跳跃或转场动机。

## CON-08 校验

`scripts/validate_workflow.py` 校验站位/道具/伤痕记录完整性与 `state_reset` 合法性；`scripts/validate_duration.py` 校验时间轴单调与零缝隙。
