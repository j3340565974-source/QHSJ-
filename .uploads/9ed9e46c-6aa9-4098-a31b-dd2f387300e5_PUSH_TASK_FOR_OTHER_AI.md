# 任务书：把 QHSJ_AIGC_Operation_Modes_Lite v1.5.2 推送到 GitHub

> 本任务书自包含，你（执行本任务的 AI）不需要任何额外背景，按步骤照抄执行即可。
> 所有命令中的占位符只有两个：`TOKEN`（用户提供的 GitHub PAT）与 `RELEASE_ID`（步骤 6 的 API 返回值）。

## 0. 任务目标（五件事，按顺序）

1. 把交付 ZIP 的内容**完整推送**到现有 GitHub 仓库（保留仓库历史）；
2. 用 GitHub API 把仓库**重命名**为 `QHSJ_AIGC_Operation_Modes_Lite` 并写入简介；
3. 创建 Release `v1.5.2` 并上传 ZIP 与 SHA256SUMS 两个附件；
4. 按第 8 节验收清单逐项验证；
5. 输出验收报告。

## 1. 前置条件

- **交付文件**（与任务书同目录）：
  - `QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip` —— 仓库全部 **55 个文件（40 文本 + 15 PNG）**，**解压后根目录直接是 `SKILL.md`，没有外层文件夹**；
  - `SHA256SUMS` —— 内容为一行：`2c49df8b90f0543204364d152ece11a7ede900d79a1d54cc0cf714faf2325bd1  QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip`
- **凭据**：用户提供 GitHub PAT，必须同时具备以下两个仓库权限（fine-grained，仅授权仓库 `j3340565974-source/QHSJ-`）：
  - `Contents: Read and write`
  - `Administration: Read and write`
  - 把 PAT 值记为 `TOKEN`。**不得回显、不得写入任何会被提交的文件。**
- **工具**：git、curl（Windows PowerShell 请用 `curl.exe`，PowerShell 的 `curl` 是别名）、unzip/Expand-Archive。

## 2. 关键参数表（全部写死，禁止改动）

| 参数 | 值 |
|---|---|
| 仓库原名 | `j3340565974-source/QHSJ-`（注意名字末尾有连字符 `-`） |
| 仓库新名 | `QHSJ_AIGC_Operation_Modes_Lite` |
| 目标分支 | `main` |
| Commit message | `feat: QHSJ_AIGC_Operation_Modes_Lite v1.5.2 micro-kernel skill` |
| Git 身份 | name `QINGHUI` / email `3340565974@qq.com`（仅当本地未配置时设置） |
| 简介（≤120 字） | `AI全流程运营模式轻量微内核：剧本→分镜→人物/场景设定卡→故事板→视频提示词，含美学/台账/负向共享服务与真实Python校验脚本` |
| Release tag | `v1.5.2` |
| Release 标题 | `QHSJ_AIGC_Operation_Modes_Lite v1.5.2` |
| 附件 1 名 | `QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip` |
| 附件 2 名 | `SHA256SUMS` |

## 3. 步骤 1：校验 ZIP（可选但建议）

```bash
# Linux/macOS
shasum -a 256 QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip
```
```powershell
# Windows PowerShell
certutil -hashfile QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip SHA256
```
期望值 `2c49df8b90f0543204364d152ece11a7ede900d79a1d54cc0cf714faf2325bd1`。不符则停止并报告用户重新下载。

## 4. 步骤 2-5：克隆 → 覆盖 → 提交 → 推送（旧仓库名）

```bash
git clone https://github.com/j3340565974-source/QHSJ-.git
cd QHSJ-
```

解压覆盖（ZIP 根目录直接是 SKILL.md，所以解压后复制**内容**进仓库根）：

```bash
# Linux/macOS
unzip -o ../QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip -d /tmp/qhsj_release
cp -R /tmp/qhsj_release/* .
```
```powershell
# Windows PowerShell
Expand-Archive -Path "..\QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip" -DestinationPath "$env:TEMP\qhsj_release" -Force
Copy-Item "$env:TEMP\qhsj_release\*" -Destination ".\" -Recurse -Force
```

提交与推送（推送用带 TOKEN 的 URL，避免依赖本机已登录状态）：

```bash
git config user.name "QINGHUI"
git config user.email "3340565974@qq.com"
git add -A
git status --short | wc -l   # 应为 55 左右（54 文件 + LICENSE 更新等，非 0 即正常）
git commit -m "feat: QHSJ_AIGC_Operation_Modes_Lite v1.5.2 micro-kernel skill"
git push "https://x-access-token:TOKEN@github.com/j3340565974-source/QHSJ-.git" main
```

> 推送成功后执行 `git ls-tree -r HEAD --name-only | wc -l`，**必须等于 55**（根目录 4：SKILL.md、README.md、ROUTING_CHECK.md、LICENSE；shared 5；modules 8；engines 8；scripts 8；tests/fixtures 6；assets 16 含 INDEX.md。合计 4+5+8+8+8+6+16 = 55）。注意 assets 内 PNG 是 15 张 + INDEX.md 1 个。

## 5. 步骤 6：重命名仓库 + 设置简介（API）

```bash
curl -X PATCH \
  -H "Authorization: Bearer TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/j3340565974-source/QHSJ- \
  -d '{"name":"QHSJ_AIGC_Operation_Modes_Lite","description":"AI全流程运营模式轻量微内核：剧本→分镜→人物/场景设定卡→故事板→视频提示词，含美学/台账/负向共享服务与真实Python校验脚本"}'
```
```powershell
# Windows PowerShell（必须 curl.exe，JSON 用转义双引号）
curl.exe -X PATCH -H "Authorization: Bearer TOKEN" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/j3340565974-source/QHSJ- -d "{\"name\":\"QHSJ_AIGC_Operation_Modes_Lite\",\"description\":\"AI全流程运营模式轻量微内核：剧本→分镜→人物/场景设定卡→故事板→视频提示词，含美学/台账/负向共享服务与真实Python校验脚本\"}"
```
成功标志：返回 JSON 中 `full_name` = `j3340565974-source/QHSJ_AIGC_Operation_Modes_Lite`。

## 6. 步骤 7：创建 Release 并上传两个附件（新仓库名）

创建 Release：

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/j3340565974-source/QHSJ_AIGC_Operation_Modes_Lite/releases \
  -d '{"tag_name":"v1.5.2","name":"QHSJ_AIGC_Operation_Modes_Lite v1.5.2","body":"微内核架构 AIGC 运营模式 Skill。标准全流程：剧本→分镜→人物设定卡→场景设定卡→故事板→配套视频提示词。含 shared 共享服务、8 业务模块、8 引擎、真实 Python 校验脚本、15 张版式参考图与完整索引。自检 run_checks.py 17/17 通过，15 张参考图 SHA256 与原始资料逐字节一致。"}'
```

从返回 JSON 里取 `upload_url`（形如 `https://uploads.github.com/repos/j3340565974-source/QHSJ_AIGC_Operation_Modes_Lite/releases/123456/assets{?name,label}`），**去掉结尾的 `{?name,label}`**，并把 `123456` 记为 `RELEASE_ID`。然后：

```bash
UPLOAD="https://uploads.github.com/repos/j3340565974-source/QHSJ_AIGC_Operation_Modes_Lite/releases/RELEASE_ID/assets"
curl -X POST -H "Authorization: Bearer TOKEN" -H "Content-Type: application/zip" \
  --data-binary "@QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip" \
  "$UPLOAD?name=QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip"
curl -X POST -H "Authorization: Bearer TOKEN" -H "Content-Type: text/plain" \
  --data-binary "@SHA256SUMS" \
  "$UPLOAD?name=SHA256SUMS"
```
```powershell
# Windows PowerShell
$UPLOAD="https://uploads.github.com/repos/j3340565974-source/QHSJ_AIGC_Operation_Modes_Lite/releases/RELEASE_ID/assets"
curl.exe -X POST -H "Authorization: Bearer TOKEN" -H "Content-Type: application/zip" --data-binary "@QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip" "$UPLOAD`?name=QHSJ_AIGC_Operation_Modes_Lite-v1.5.2.zip"
curl.exe -X POST -H "Authorization: Bearer TOKEN" -H "Content-Type: text/plain" --data-binary "@SHA256SUMS" "$UPLOAD`?name=SHA256SUMS"
```
成功标志：两次返回 JSON 均含 `"state":"uploaded"`。

## 7. 步骤 8：验收清单（逐项打勾）

| # | 检查项 | 通过标准 |
|---|---|---|
| 1 | 推送文件数 | `git ls-tree -r HEAD --name-only | wc -l` = 55 |
| 2 | 根目录 | 含 `SKILL.md`、`README.md`、`ROUTING_CHECK.md`、`LICENSE` 及 `shared/ modules/ engines/ scripts/ tests/ assets/` |
| 3 | 参考图 | `assets/` 内恰好 15 张 `.png` + `INDEX.md` |
| 4 | 新仓库地址 | `https://github.com/j3340565974-source/QHSJ_AIGC_Operation_Modes_Lite` 可访问 |
| 5 | 简介 | 仓库页 About 显示第 2 节简介文本 |
| 6 | Release | `v1.5.2` 存在且含两个附件，均 `state:uploaded` |
| 7 | 历史保留 | 仓库 Commits 页含原 MIT LICENSE 提交与新 feat 提交 |

## 8. 已知坑（不要踩）

1. **仓库名末尾有连字符**：`QHSJ-`，clone 和 PATCH 时不能漏。
2. **PowerShell 的 `curl` 是 Invoke-WebRequest 别名**：一律写 `curl.exe`。
3. **upload_url 的 `{?name,label}` 必须去掉**，否则附件上传 404。
4. **ZIP 无外层文件夹**：解压后直接是 `SKILL.md` 等，复制时用 `*` 复制内容进仓库根，不要把整个解压目录粘进去。
5. **ZIP 内没有 `.git`**：必须先 clone 现有仓库再覆盖，才能保留历史并正常 push。
6. **TOKEN 安全**：只出现在命令的 `Authorization` 头与推送 URL 中；不要 echo、不要写入文件；任务完成后提醒用户去 GitHub 撤销该 PAT。
7. 若 `git push` 报 `! [rejected]`（远端有新提交）：先 `git pull --rebase "https://x-access-token:TOKEN@github.com/j3340565974-source/QHSJ-.git" main` 再 push。

## 9. 完成后输出报告格式

```text
推送结果：
- 推送 commit: <sha>
- 文件数: 55（40 文本 + 15 PNG）
- 重命名: 成功，full_name=<...>
- 简介: 已设置（66 字）
- Release: v1.5.2，附件 2 个（zip + SHA256SUMS）
- 验收清单: 7/7 通过（或列出未通过项）
- 提醒: 请到 https://github.com/settings/personal-access-tokens 撤销本次 PAT
```
