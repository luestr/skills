---
name: setup-matt-pocock-skills
description: "为本仓库配置工程技能所需的设置：issue 跟踪器、分诊标签词汇表和领域文档布局。在首次使用其他工程技能之前运行一次。"
disable-model-invocation: true
---

# 配置 Matt Pocock 技能集

搭好工程技能默认依赖的仓库级配置：

- **Issue 跟踪器**：issue 存放在哪里（默认 GitHub；本地 markdown 也已开箱支持）
- **分诊标签**：五个规范分诊角色使用的字符串
- **领域文档**：`GLOSSARY.md` 和 ADR 存放的位置，以及读取它们时要遵守的规则

这是提示词驱动的技能，不是确定性脚本。先探索，把发现呈现出来，与用户确认，然后再写入。

## 流程

### 1. 探索

查看当前仓库，了解它的初始状态。存在什么就读什么，不要凭假设：

- `git remote -v` 和 `.git/config`：这是 GitHub 仓库吗？是哪一个？
- 仓库根目录的 `AGENTS.md` 和 `CLAUDE.md`：两者存在吗？其中是否已有 `## Agent 技能` 小节？
- 仓库根目录的 `GLOSSARY.md` 和 `GLOSSARY-MAP.md`
- `docs/adr/` 以及任何 `src/*/docs/adr/` 目录
- `docs/agents/`：本技能此前的产出是否已经存在？
- `.scratch/`：本地 markdown issue 跟踪器的约定已在使用中的迹象
- 安装了 `triage` 技能吗？（本技能旁边有 `triage` 技能目录，或你的可用技能里有 `triage`。）这决定 B 节是否运行。
- monorepo 信号：`pnpm-workspace.yaml`、`package.json` 里的 `workspaces` 字段，或 `packages/*` 下有不少内容且各有自己的 `src/`。这些只出现在真正的大型多包仓库里；没有它们就意味着单上下文，而几乎所有仓库都是单上下文。

### 2. 呈现发现并提问

总结哪里已有、哪里还缺。然后按顺序过每一节。一节一个问题，答完再进入下一节。

每节先给出推荐答案，让用户一句话就能接受。只有当选择确实会分叉时，才给一行说明；如果探索已经定了结论，就整节跳过（`triage` 未安装时跳过 B 节，没有 monorepo 时跳过 C 节）。

**A 节：Issue 跟踪器。**

> 说明：“issue 跟踪器”是本仓库存放 issue 的地方。`to-tickets`、`triage`、`to-spec` 等技能会读写它。它们需要知道该调用 `gh issue create`、在 `.scratch/` 下写 markdown 文件，还是遵循你描述的其他流程。选你实际用来跟踪本仓库工作的地方。

默认立场：这些技能是为 GitHub 设计的。如果某个 `git remote` 指向 GitHub，就提议 GitHub。如果某个 `git remote` 指向 GitLab（`gitlab.com` 或自建主机），就提议 GitLab。否则（或者用户更愿意），提供这些选项：

- **GitHub**：issue 存放在仓库的 GitHub Issues 里（使用 `gh` CLI）
- **GitLab**：issue 存放在仓库的 GitLab Issues 里（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **本地 markdown**：issue 以文件形式存放在本仓库的 `.scratch/<feature>/` 下（适合个人项目或没有远程的仓库）
- **其他**（Jira、Linear 等）：请用户用一段话描述工作流程；技能会把它记录为自由格式的说明文字

把选择记录到 `docs/agents/issue-tracker.md`。GitHub 和 GitLab 模板带有一个“PR 作为请求入口”标志，默认 **off**。保持 off，也不要主动提起：想把外部 PR 纳入分诊队列的用户，之后可以自己在文件里把这个标志翻过来。

**B 节：分诊标签词汇表。** 如果 `triage` 技能未安装（探索阶段已经告诉你），就整节跳过，因为未安装的技能不需要标签。

如果已安装，只问一个问题：

> 要保留默认的分诊标签吗？（推荐：**yes**）

默认值就是五个规范角色，每个标签字符串与角色名相同：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。回答 **yes** 时，原样写入。只有当用户说不——通常是因为他们的跟踪器已经在用别的名字（例如用 `bug:triage` 表示 `needs-triage`）——才收集这些覆盖项，让 `triage` 套用已有标签，而不是创建重复标签。

**C 节：领域文档。** 默认 **单上下文**（仓库根目录一个 `GLOSSARY.md` + `docs/adr/`）。这适合几乎所有仓库；不用询问，直接写入。

只有当探索发现 monorepo 信号时，才提供 **多上下文**（根目录一个 `GLOSSARY-MAP.md`，指向各上下文的 `GLOSSARY.md`）。然后确认他们想要哪种布局。

### 3. 确认并编辑

向用户展示以下内容的草稿：

- 要添加到 `CLAUDE.md` / `AGENTS.md`（以正在编辑的那个为准）的 `## Agent 技能` 块（选择规则见第 4 步）
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md` 和 `docs/agents/triage-labels.md` 的内容（最后一个仅在安装了 `triage` 时）

让他们先编辑，再写入。

### 4. 写入

**选择要编辑的文件：**

- 如果 `CLAUDE.md` 存在，就编辑它。
- 否则，如果 `AGENTS.md` 存在，就编辑它。
- 如果两者都不存在，问用户要创建哪一个；不要替他们决定。

`CLAUDE.md` 已存在时绝不创建 `AGENTS.md`（反过来也一样）；永远编辑已经存在的那个。

如果所选文件里已有 `## Agent 技能` 块，就地更新它的内容，而不是再追加一份重复的。不要覆盖用户对周围小节的修改。

这个块：

```markdown
## Agent 技能

### Issue 跟踪器

[用一行总结 issue 跟踪在哪里]。见 `docs/agents/issue-tracker.md`。

### 分诊标签

[用一行总结标签词汇表]。见 `docs/agents/triage-labels.md`。

### 领域文档

[用一行总结布局：“单上下文”还是“多上下文”]。见 `docs/agents/domain.md`。
```

只有当 `triage` 已安装且 B 节运行过时，才包含 `### 分诊标签` 子块并写入 `docs/agents/triage-labels.md`。否则两者都省略。

当 B 节在 GitHub 或 GitLab 上运行时，为跟踪器缺失的每个已配置标签创建它（`gh label create` / `glab label create`）。

然后以本技能目录里的种子模板为起点，写出这些文档文件：

- [issue-tracker-github.md](./issue-tracker-github.md)：GitHub issue 跟踪器
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)：GitLab issue 跟踪器
- [issue-tracker-local.md](./issue-tracker-local.md)：本地 markdown issue 跟踪器
- [triage-labels.md](./triage-labels.md)：标签映射（仅在安装了 `triage` 时）
- [domain.md](./domain.md)：领域文档的读取规则 + 布局

对于“其他”跟踪器，根据用户的描述从零写出 `docs/agents/issue-tracker.md`。

### 5. 完成

告诉用户配置已完成，以及接下来哪些工程技能会读取这些文件。提醒他们之后可以直接编辑 `docs/agents/*.md`；只有想更换 issue 跟踪器或推倒重来时，才需要重新运行本技能。
