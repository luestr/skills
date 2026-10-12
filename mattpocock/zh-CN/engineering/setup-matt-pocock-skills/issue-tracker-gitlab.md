# Issue 跟踪器：GitLab

本仓库的 issue 和规格说明都以 GitLab issue 的形式存在。所有操作都使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI。

## 约定

- **创建 issue**：`glab issue create --title "..." --description "..."`。多行描述用 heredoc。传 `--description -` 可以打开编辑器。
- **读取 issue**：`glab issue view <number> --comments`。机器可读输出用 `-F json`。
- **列出 issue**：`glab issue list -O json`，配合适当的 `--label` 过滤条件。
- **评论 issue**：`glab issue note <number> --message "..."`。GitLab 把评论叫 “notes”。
- **应用 / 移除标签**：`glab issue update <number> --label "..."` / `--unlabel "..."`。多个标签可以用逗号分隔，也可以重复这个标志。
- **关闭**：`glab issue close <number>`。`glab issue close` 不接受关闭评论，所以先用 `glab issue note <number> --message "..."` 发出说明，再关闭。
- **合并请求**：GitLab 把 PR 叫 “merge requests”。用 `glab mr create`、`glab mr view`、`glab mr note` 等，用法与 `gh pr ...` 相同，只是用 `mr` 代替 `pr`，用 `note`/`--message` 代替 `comment`/`--body`。

从 `git remote -v` 推断仓库；在克隆目录里运行时，`glab` 会自动完成这一步。

## MR 作为分诊入口

**MR 作为请求入口：no。** _（如果本仓库把外部 merge request 当作功能请求，就设为 `yes`；`/triage` 会读取这个标志。）_

设为 `yes` 后，MR 会像 issue 一样走同一套标签和状态，只是改用 `glab mr` 的对应命令：

- **读取 MR**：`glab mr view <number> --comments`，diff 用 `glab mr diff <number>`。
- **列出待分诊的外部 MR**：`glab mr list -F json`，然后只保留作者不是项目成员/所有者的 MR（贡献者的 MR，而不是维护者正在进行中的工作）。
- **评论 / 打标签 / 关闭**：`glab mr note`、`glab mr update --label`/`--unlabel`、`glab mr close`。

与 GitHub 不同，GitLab 的 issue 和 MR 分开编号，所以只要知道维护者指的是哪一种入口，`#42` 就没有歧义。

## 当某个技能说“发布到 issue 跟踪器”时

创建一个 GitLab issue。

## 当某个技能说“获取相关工单”时

运行 `glab issue view <number> --comments`。

## 寻路操作

供 `/wayfinder` 使用。**地图**是一个 issue，其中的工单都是它的**子** issue。

- **地图**：一个带 `wayfinder:map` 标签的 issue，正文承载备注 / 已定决策 / 迷雾。`glab issue create --label wayfinder:map`。（在有原生 epic 的 GitLab 层级上，也可以改由 epic 承载地图；带标签的 issue 在所有层级都能用。）
- **子工单**：描述顶部带有 `Part of #<map>`、并带 `wayfinder:<type>` 标签（`research`/`prototype`/`grilling`/`task`）的 issue。一旦被认领，工单就指派给驱动地图的开发者。
- **阻塞关系**：GitLab 的**原生阻塞链接**，这是规范做法，在 UI 中可见。用 `/blocked_by #<n>` 快捷操作添加这条阻塞关系，以 note 形式发布（`glab issue note <child> --message "/blocked_by #<blocker>"`）。原生阻塞链接是 Premium/Ultimate 功能；在免费层级（或不可用时）回退为在描述顶部写一行 `阻塞项：#<n>, #<n>`。所有阻塞项都关闭后，工单即为无阻塞。
- **前沿查询**：`glab issue list -O json`，限定为地图的子 issue，去掉任何还有未关闭阻塞项的：指向未关闭 issue 的原生 `blocked_by` 链接（`glab api projects/:id/issues/<child-iid>/links`）、`阻塞项` 行中仍有未关闭的 issue，或已有指派；按地图中的顺序，第一个胜出。
- **认领**：`glab issue update <n> --assignee @me`，这是本会话的第一次写入。
- **解决**：`glab issue note <n> --message "<answer>"`，然后 `glab issue close <n>`，再把一条上下文指针（要点 + 链接）追加到地图的已定决策。
