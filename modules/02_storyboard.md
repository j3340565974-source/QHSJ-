# 02 分镜表引擎（文字分镜）

> 本模块只产出**文字分镜表**，不产出图片。视觉故事板由 `modules/07_storyboard_gen.md` 消费本模块输出，视频提示词由 `modules/08_video_prompt.md` 消费。
> 依赖：`shared/standard_specs.md`、`shared/context_ledger.md`、`engines/camera_engine.md`、`engines/continuity_engine.md`、`engines/audio_engine.md`。

## 02-01 输入与前置

- 输入：`modules/01_script.md` 的物理剧本（世界与时间档案、人物事实、场次因果、对白）。
- 前置：项目四件套（模型/画幅/视频模型/补充说明）已写入台账；画幅作用域使用 `project_aspect`。
- 若剧本缺失或未登记，先补剧本；禁止凭空生成分镜。

## 02-02 剧本覆盖率（硬约束）

- 每个场次必须被至少一个镜覆盖；动作、对白、情绪、空间转换、关键道具五类元素逐项映射到镜号。
- 输出覆盖矩阵：`场次 × [镜号列表]`，未覆盖即缺镜诊断（缺定场/缺反应/缺插入/缺意象/缺呼吸/缺越轴处理/缺表演颗粒度）。

## 02-03 镜号字段（18 字段模板）

`镜号、场次、景别、机位、运镜、主体、动作、对白/台词、情绪、时长、转场、音效/BGM、道具挂载、站位、轴线、首尾帧状态、连续性增量、备注`

- 镜头语法走 `engines/camera_engine.md`：一个主运镜 + 可选辅助效果；禁止只写“推/摇”。
- 首尾帧状态写 `state_delta`（见 `shared/context_ledger.md`），供 08 做跨条继承。

## 02-04 时长与节奏

- 情绪越平镜头越少越长，情绪越烈镜头越多越短。
- 快切双约束（整改后）：单镜 0.5–1s、连续快切 ≤8 镜；**废止“连续快切总时长≤0.5s”**；快切后接长镜。
- 每场四件套：定场(1) + 主镜头(1) + 反应(≥1) + 钩子(末尾1)；每场至少 1 个插入镜头。
- 时长由 `scripts/validate_duration.py` 校验：台词、停顿、动作、转场秒点量化，时间轴零缝隙。

## 02-05 竖屏规范

- `project_aspect=9:16` 时：主体垂直构图，上下留调度空间；避免横移长镜为主，优先纵移/升降。
- 机位与景别按竖画幅重新选择，不照抄横屏方案。

## 02-06 打斗/专项段落

- 命中/动作段落调用 `engines/fight_engine.md`；巨物/赛车/蒙太奇/舞蹈/VFX 调用 `engines/specialty_engine.md`。
- 安全分级（默认 G1）写入分镜备注。

## 02-07 输出契约（给 07/08 的接口）

```json
{
  "project_aspect": "16:9",
  "fps": 24,
  "editorial_duration_s": 30.0,
  "shots": [
    {
      "id": "P01",
      "scene": "S01",
      "shot_size": "WS",
      "camera": {"position": "...", "movement": "...", "falloff": "..."},
      "subject": "...",
      "action": "...",
      "dialogue": {"text": "...", "speech_seconds": 2.0, "pause_seconds": 0.5},
      "emotion": "...",
      "duration_s": 3.0,
      "transition": "cut",
      "audio": {"sfx": "...", "bgm_cue": "..."},
      "props": ["..."],
      "stance": "inherit|reset",
      "state_delta": "...",
      "frame_end": "..."
    }
  ]
}
```

- `07` 只允许引用 `id/action/shot_size/camera` 等已存在镜号；未写动作不得进故事板（见 07-02）。

## 02-08 质检与校验

- `scripts/validate_workflow.py`：覆盖矩阵完整、镜号唯一、接口字段齐全。
- `scripts/validate_duration.py`：时间轴零缝隙、台词可辨识、fps 量化。
- 校验失败修正至多三轮，仍失败列出冲突并进入 HITL 暂停，禁止无限重写。
