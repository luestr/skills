# Issue 跟踪器：GitHub

本仓库的 issue 和规格说明都以 GitHub issue 的形式存在。所有操作都使用 `gh` CLI。

## 约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行正文用 heredoc。
- **读取 issue**：`gh issue view <number> --json number,title,body,labels,comments`。
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，配合适当的 `--label` 和 `--state` 过滤条件。
- **把 issue 变成父 issue 的子 issue**：`gh issue create --parent <parent> ...`，或事后执行 `gh issue edit <parent> --add-sub-issue <child>`（`gh` 2.94+）。更旧的 `gh`：`gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`（数据库 id，见下文 **阻塞关系**）。不支持子 issue 时，在子 issue 正文顶部写 `Part of #<parent>`。
- **评论 issue**：`gh issue comment <number> --body "..."`。
- **应用 / 移除标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`。
- **关闭**：`gh issue close <number> --comment "..."`。

从 `git remote -v` 推断仓库；在克隆目录里运行时，`gh` 会自动完成这一步。

## PR 作为分诊入口

**PR 作为请求入口：no。** _（如果本仓库把外部 PR 当作功能请求，就设为 `yes`；`/triage` 会读取这个标志。）_

设为 `yes` 后，PR 会像 issue 一样走同一套标签和状态，只是改用 `gh pr` 的对应命令：

- **读取 PR**：`gh pr view <number> --comments`，diff 用 `gh pr diff <number>`。
- **列出待分诊的外部 PR**：`gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`。
- **评论 / 打标签 / 关闭**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHub 的 issue 和 PR 共用同一套编号，所以单独出现的 `#42` 可能是其中任何一个：先用 `gh pr view 42` 解析，不行再退回 `gh issue view 42`。

## 当某个技能说“发布到 issue 跟踪器”时

创建一个 GitHub issue。

## 当某个技能说“获取相关工单”时

按上文 **读取 issue** 的方式读取它。

## 寻路操作

供 `/wayfinder` 使用。**地图**是一个 issue，其中的工单都是它的**子** issue。

- **地图**：一个带 `wayfinder:map` 标签的 issue，正文承载备注 / 已定决策 / 迷雾。`gh issue create --label wayfinder:map`。
- **子工单**：作为 GitHub 子 issue 链接到地图的 issue（见 **把 issue 变成父 issue 的子 issue**）。未启用子 issue 时，把子 issue 加进地图正文的任务列表，并在子 issue 正文顶部写 `Part of #<map>`。标签：`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。一旦被认领，工单就指派给驱动地图的开发者。
- **阻塞关系**：GitHub 的**原生 issue 依赖关系**，这是规范做法，在 UI 中可见。用 `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>` 添加这条阻塞关系，其中 `<blocker-db-id>` 是阻塞项的数字**数据库 id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`，_不是_ `#number` 或 `node_id`）。GitHub 会报告 `issue_dependencies_summary.blocked_by`（只含未关闭的阻塞项，即实时生效的关卡）。不支持依赖关系时，回退为在子 issue 正文顶部写一行 `阻塞项：#<n>, #<n>`。所有阻塞项都关闭后，工单即为无阻塞。
- **前沿查询**：列出地图的未关闭子 issue（`gh issue list --state open`，限定为地图的子 issue / 任务列表），去掉任何还有未关闭阻塞项的（`issue_dependencies_summary.blocked_by > 0`，或 `阻塞项` 行中仍有未关闭的 issue）以及任何已被指派的；按地图中的顺序，第一个胜出。
- **认领**：`gh issue edit <n> --add-assignee @me`，这是本会话的第一次写入。
- **解决**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，再把一条上下文指针（要点 + 链接）追加到地图的已定决策。
