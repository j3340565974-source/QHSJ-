# 08 配套视频提示词

> 输出：与文字分镜/视觉故事板一一对应的视频生成提示词（文生视频/图生视频请求），不是剪辑脚本。
> 依赖：`modules/02_storyboard.md`、`modules/07_storyboard_gen.md`、`shared/standard_specs.md`、`shared/aesthetic_system.md`、`shared/context_ledger.md`、`shared/negative_words.md`、`engines/camera_engine.md`、`engines/continuity_engine.md`、`engines/audio_engine.md`、`engines/model_adapter.md`。

## 08-01 强制数据流

```
modules/02_storyboard.md SHOTS + modules/07_storyboard_gen.md 镜号 + 03/04/05/06 已验收资产 → 08 装配 → 模型适配 → 视频请求
```

- 镜号、数量、动作与故事板一致；视频定“怎么动”，故事板定“什么”。
- 首帧必须来自已登记资产（图生视频）；文生视频需声明无首帧参考。

## 08-02 单镜装配结构

`镜号 → 画面锚点（角色外观/场景/道具）→ 动作与状态增量 → 运镜 → 光影氛围 → 时长 → 音频/转场 → 负向`

- 角色外观使用台账 `{{CHAR_A_LOOK}}`，与图片阶段确定的质感、画风、色彩系统逐字沿用。
- 运镜一个主运镜＋可选辅助；情绪等抽象字段作内部元数据，不直接写入不支持该语法的模型。

## 08-03 首尾帧与连续性

- 每条/每镜：`base_anchor + state_delta → terminal_state`；下条继承（CON-01/CON-02）。
- 首条或显式重置使用初始站位；时间跳跃必须写 `state_reset` 原因与生效镜号。
- 道具挂载、持械手、伤痕、服装在连续时间线内一致。

## 08-04 时间轴与时长

- 编辑时间轴零缝隙：`shot[i].start == shot[i-1].end`；台词/停顿/动作秒点量化。
- 生成档与剪辑档分离：模型时长档（3s/5s/10s 等）只约束生成段，不约束整条剪辑镜头；拆段方案由 `engines/model_adapter.md` 决定。
- 快切连续 ≤8 镜；升格降格全片 ≤30%；速度突变必须写精确秒点。

## 08-05 音频与转场

- 每镜携带四层混音标记（对白/环境/音效/BGM cue）与 J/L-cut 转场，由 `engines/audio_engine.md` 规则生成。
- 慢镜必须写 fps 与起止秒点；音效与画面动作点对齐。

## 08-06 负向与安全

- 负向由 `shared/negative_words.md` 按媒介/卡种/意图动态装配；硬字幕走白名单。
- 打斗/危险内容按 FIG-04 安全分级写入负向与备注。

## 08-07 输出契约

```json
{
  "video_id": "VID_01",
  "project_aspect": "16:9",
  "fps": 24,
  "shots": [
    {
      "id": "P01",
      "source_board_cell": "P01",
      "first_frame_asset": "CHAR_A",
      "action": "...",
      "camera": {"movement": "...", "falloff": "..."},
      "state": {"base": "...", "delta": "...", "terminal": "..."},
      "editorial_duration_s": 3.0,
      "generation_segments": [{"model_duration_s": 3, "prompt": "..."}],
      "audio": {"dialogue": "...", "sfx": "...", "bgm_cue": "..."},
      "transition": "cut"
    }
  ],
  "validated_by": ["scripts/validate_duration.py", "scripts/validate_prompt.py", "scripts/validate_workflow.py"]
}
```

## 08-08 校验

- `scripts/validate_duration.py`：零缝隙、台词秒长、模型档、fps 量化。
- `scripts/validate_workflow.py`：镜号与 02/07 一致、资产登记。
- `scripts/validate_prompt.py`：美学/运镜调用标记、负向装配、模型字段。
- 失败修正至多三轮，仍失败进入 HITL 暂停。
