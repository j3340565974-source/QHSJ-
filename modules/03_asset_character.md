# 03 人物资产：人物设定卡

> 输出：一张 16:9 横版人物设定卡（默认形态 `CHARACTER_SHEET`）。本模块只产出提示词，不产出图片文件。
> 依赖：`shared/standard_specs.md`、`shared/aesthetic_system.md`、`shared/context_ledger.md`、`shared/negative_words.md`、`engines/camera_engine.md`。
> 注意：人物卡**没有专属参考图**。禁止把 `../assets/material_modes_m1_m5.png` 等材质图冒充人物卡骨架。

## 03-01 输入与前置

- 人物事实来自 `modules/01_script.md` / 用户设定：姓名、性别、年龄、身份、性格、外观、服装、标志物。
- 开工必问（缺省时）：故事板类型（默认 G9_NO_BLANK）、人物资产形态（默认 `CHARACTER_SHEET`）；模型/画幅按四件套默认，超时标【参数假设】。
- 已登记的人物与场景写入台账后，故事板/视频才可引用。

## 03-02 主体分工（硬约束）

- 人物设定卡：**角色本人露脸**、有表情、有发型妆容；与服装卡白膜人台分工，禁止互相套用规则。
- 卡面禁写：抽象词作画面主语、半身替全身、标签叠写、未穿戴物件堆叠。

## 03-03 头身与比例公式（整改后唯一式）

```
head_length = height / head_count
```

- 优先级：用户/风格档显式 N > 剧本设定 > 默认 N=9。
- 只有身高且无 N：以成年人约 20cm 头长估算 `N = height / 20`。
- **默认 N=9 不再反推固定 20cm**；同一人物全卡用同一 N。

关键锚点（N 头身）：肩线 1.35、胸线 2、腰/肘 3、髋线 N/2、膝线 0.75N、脚踝 0.93N、指尖 0.4N；肩宽男 2.1–2.3 头、女 1.9–2.1 头，头宽 0.72 头。

## 03-04 状态锚点八项

`站姿、双脚位置、视线方向、左右臂动作、持物手、持握高度、随身件位置、重心`

- 与 `engines/continuity_engine.md` 的初始站位一致；持械手与双手占用可校验。

## 03-05 机位与焦段

- 主视觉胸像 85mm，头约占板块高 40%。
- 三视图全身 85mm，三格等大，全身占格高 95%。
- 局部特写 100mm 微距。

## 03-06 版式（S1 横版三栏 + 九段骨架）

| 板块 | 内容 |
|---|---|
| A 主视觉 | 正面胸像，全卡最大单一板块 |
| B 三视图 | 正/背/侧全身，等高同比例 |
| C 服装补充 | 外搭/内搭平铺两格（平面图例外，允许无人体，见负向白名单） |

九段预算（总上限 1900 字符，整改后）：`主体 195 / 头身 140 / 状态 60 / 机位 220 / 画幅 480 / 三视图 300 / 服装 130 / 细节 135 / 负向 170`。

## 03-07 风格与运镜（强制调用）

- 所有提示词必须调用 `shared/aesthetic_system.md`（默认 `cinematic` profile 或用户风格档）与 `engines/camera_engine.md` 运镜设计。
- 人物默认背景为深色渐变底；用户风格或 `asset_neutral` 白底需求可覆盖。
- 卡面文字只写内容信息（物件/部位/材质），制作参数不印卡面。

## 03-08 输出契约

```json
{
  "character_id": "CHAR_A",
  "head_count": 9,
  "height_cm": 180,
  "head_length_cm": 20,
  "views": ["front_portrait", "front_full", "back_full", "side_full"],
  "costume_flats": ["outer", "inner"],
  "prompt_segments": {...},
  "negative": "来自 shared/negative_words.md 动态装配",
  "validated_by": ["scripts/calc_head_body.py", "scripts/validate_prompt.py"]
}
```

## 03-09 校验

- `scripts/calc_head_body.py`：头身公式与锚点校验。
- `scripts/validate_layout.py`：三栏骨架、九段面积归一与主视觉最大单一板块校验。
- `scripts/validate_prompt.py`：九段字段、负向装配、美学与运镜调用标记。
- 校验失败修正至多三轮，仍失败进入 HITL 暂停。
