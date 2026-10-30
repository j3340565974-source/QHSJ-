# assets/INDEX.md — 参考图资产索引与溯源

> **参考图契约（最高指令）**：以下 15 张图是**结构参考图**，仅供使用本 Skill 的 AI 理解设定卡/故事板的板块、视图关系、信息层级与一致性要求。它们**不是输出样张**：不得复制其像素尺寸、配色、字体、装饰、示例物体或遗留参数；默认不作为图生图输入，除非用户明确指定。图片字节与原始压缩包逐字节一致（见 SHA256），未做缩放、转码或修改。

| 新英文文件名 | 原文件名 | 实际像素 | 内容标称 | 主要引用位置 | 状态/注意事项 | SHA256 |
|---|---|---|---|---|---|---|
| scene_sheet_21x9.png | 01_场景设定卡_21比9.png | 2100×1050 | 21:9 场景卡结构 | modules/04_asset_scene.md | 图内“主图约46%”标注已废止 | 0eb16e913b1dede4e97882495682a77b21cb17a4f32d15bafea546a9dc187f61 |
| scene_sheet_9x16.png | 02_场景设定卡_9比16.png | 1080×1780 | 9:16 场景卡结构 | modules/04_asset_scene.md | 资产带按 6×2 理解 | 8b9c3f8470d268486808b1d7693270a138a11ca7e544822bb21dd327e10f13d9 |
| prop_sheet_white.png | 03_道具设定卡_白底.png | 1920×1560 | 道具 L1 结构 | modules/06_asset_prop.md | 仅 L1 示例，不得套全部道具 | 284d1725d22de7668928a58142930e057cef9a1c845eecee8e34ed14dbacad29 |
| costume_sheet_white.png | 04_服装设定卡_白底.png | 1920×1380 | 服装卡现行结构 | modules/05_asset_costume.md | 1:1 区域→三个 1:3 + 右侧 2×2；M6 参考 | 8794097e6b7623850a1f82ce0589f2c30d86e8e08224bf391ad4ceea5e64d0df |
| storyboard_white_model_16x9.png | 05_白模故事板_16比9.png | 1920×1180 | G8 故事板结构 | modules/07_storyboard_gen.md | 4×2+16:9 组合几何不成立，以公式为准 | 7876e9b9b4fad21d67c18d13d47058bacb1fac7388ef31f7ac579920b41beedd |
| storyboard_white_model_9x16.png | 06_白模故事板_9比16.png | 1080×1720 | 竖版 G6 结构 | modules/07_storyboard_gen.md | 竖版网格结构参考 | 9099a3f5ec4c1052640625daeb010493f8f602397592fcaada7226813b94a976 |
| aspect_ratio_adaptation.png | 07_任意比例适配表.png | 1920×1080 | 比例适配历史表 | shared/standard_specs.md、modules/04_asset_scene.md | 旧 2% 边距与 46% 已废止 | f7082b7154d0857abbf107298c2056b0c2b92989f69505e0ae5d0893b214582f |
| universal_layout_engine.png | 08_万能版式引擎.png | 1920×1180 | 版式四层关系 | shared/standard_specs.md | 材质区仅 M1–M5 | ccf54881d4a9eb5d5392357a8f8e34d8f61eed6961d1d203e0a6b1105a4989c8 |
| grid_modes_nine_grid.png | 09_九宫格与网格档.png | 1920×1180 | G9 九宫格结构 | modules/07_storyboard_gen.md | G9/16:9 主参考，其他档由公式校验 | ef8790747ad246329051d9772f6ad8cf9d1134ae87ef5d5c5e9381d78fe721f6 |
| interior_direction_sheet.png | 10_内景方位卡.png | 1920×1360 | 内景方位 G9 结构 | modules/04_asset_scene.md | P03 布局基底与派生方位 | 4cb0a0f42b3e9d9d288e68ba83d46a0c65bd61ab43db94e174e07d5070989326 |
| material_modes_m1_m5.png | 11_材质档对照.png | 1920×980 | 材质档 M1–M5 历史示意 | modules/07_storyboard_gen.md | 不含 M6，禁止冒充角色卡骨架 | 7f79c35c387a925671733aa10dbbdb26d1f91e644d9b72802d26fc2896e785ed |
| exterior_panorama_sheet.png | 12_外景720全景卡.png | 1920×1300 | 外景全景卡结构 | modules/04_asset_scene.md | “720°”为产品名，投影为 360°×180° 2:1 | 11163a7be3ebe703aace9f3d99a633f2880ee4b1d63b5366b3e9df435d307db0 |
| universal_style_formula.png | 13_万能风格公式.png | 1960×1440 | 六层风格公式 | shared/aesthetic_system.md | 非风格 OS 八维全图 | bb7d8a3bdff836a96ccb4a6fbd2b4899e0751104ff5aad7fb2e0d51fe17680a6 |
| scene_formula_horizontal.png | 版式公式_FORM_A_横版.png | 1920×1330 | 场景横版公式 legacy | modules/04_asset_scene.md | 旧参数以 LAY 现行字段为准 | b98ef601493fce0e563912928b5f26cffa7071dede67b850cd2f095e606f3cd4 |
| scene_formula_vertical.png | 版式公式_FORM_B_竖版.png | 1300×1700 | 场景竖版公式 legacy | modules/04_asset_scene.md | 旧参数以 LAY 现行字段为准 | f3a02c53623714f292e8870440c406af8b6a5d6d7bc614a3d61b669b9d61712b |

## 引用约定

- 所有引用一律相对路径：`../assets/<新英文文件名>.png`。
- 图注必须注明“结构参考”及遗留问题（如 M1–M5 缺 M6、46% 废止）。
- 人物设定卡没有专属参考图：禁止把 material_modes_m1_m5.png 等冒充人物卡骨架。
- 完整性由 `../scripts/validate_assets.py` 校验：数量、SHA256、INDEX 覆盖、Markdown 链接。
