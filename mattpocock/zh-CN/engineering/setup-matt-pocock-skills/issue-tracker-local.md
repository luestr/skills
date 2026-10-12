# Issue 跟踪器：本地 Markdown

本仓库的 issue 和规格说明以 markdown 文件的形式存放在 `.scratch/` 下。

## 约定

- 每个功能一个目录：`.scratch/<feature-slug>/`
- 规格说明是 `.scratch/<feature-slug>/spec.md`
- 实现类 issue 每个工单一个文件，位于 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 开始编号，绝不合并成单个工单文件
- 分诊状态记录在每个 issue 文件顶部附近的一行 `状态：` 上（角色字符串见 `triage-labels.md`）
- 评论和对话历史追加到文件末尾的 `## 评论` 标题下

## 当某个技能说“发布到 issue 跟踪器”时

在 `.scratch/<feature-slug>/` 下新建一个文件（必要时先创建目录）。

## 当某个技能说“获取相关工单”时

读取被引用路径上的文件。用户通常会直接给出路径或 issue 编号。

## 寻路操作

供 `/wayfinder` 使用。**地图**是一个文件，每个工单是一个**子**文件。

- **地图**：`.scratch/<effort>/map.md`（承载备注 / 已定决策 / 迷雾的正文）。
- **子工单**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 开始编号，正文写问题。一行 `类型：` 记录工单类型（`research`/`prototype`/`grilling`/`task`）；一行 `状态：` 记录 `claimed`/`resolved`。
- **阻塞关系**：顶部附近的一行 `阻塞项：NN, NN`。它列出的每个文件都是 `resolved` 时，工单即为无阻塞。
- **前沿**：扫描 `.scratch/<effort>/issues/`，找出未关闭、无阻塞且未被认领的文件；编号最靠前的胜出。
- **认领**：动手前先设 `状态：claimed` 并保存。
- **解决**：把答案追加到 `## 答案` 标题下，设 `状态：resolved`，再把一条上下文指针（要点 + 链接）追加到 `map.md` 里地图的已定决策。
