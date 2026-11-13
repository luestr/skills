---
name: grit
description: 在 Git 仓库中使用 grit CLI 做版本控制——status、diff、提交、分支、合并、cherry-pick、revert、fetch/pull/push 与标签——并为脚本和 Agent 提供 JSON 输出。当任务涉及提交、建分支、与远程同步或读取历史，且环境中安装了 `grit` 时使用。
metadata:
  language: zh-CN
---

# grit

`grit` 是一个小巧、有明确取向的 Git 客户端。它读写普通的 Git 仓库，因此 `git` 和 `grit` 可以用于同一个仓库。它不照搬 Git 的命令与参数：每件事通常只有一条显而易见的做法，而且每条命令都能用 JSON 作答。

本技能由 `grit 0.5.33` 生成。运行 `grit <command> --help` 查看已安装版本的确切选项。

## 规则

- 只要会读取结果，就传 `--json`。此时 stdout 恰好包含一个 JSON 对象；进度和提示输出到 stderr。
- 使用 `--filter '<类 jq 表达式>'`（配合 `--json`）只保留需要的内容：`grit status --json --filter '{branch, clean}'`。迭代器过滤器（`.commits[].oid`、`.staged[].path`）总是返回 JSON 数组；单值字段保持标量（缺失时为 `null`）。
- 失败时退出码通常是 1，stdout 为 `{"error": "…"}`（或带 `kind` 的结构化对象）。退出码 2 表示用法错误（未知参数、错误的 `--hunks` id……）；配合 **`--json`** 时，即便是 clap 用法错误，stdout 仍有 `{"error": "…"}`。无法访问或读取的远程（路径不存在、DNS 或连接被拒、HTTP 错误）在 `clone`、`fetch`、`pull`、`push` 和 `remote refs` 上以退出码 128 和 `kind: remote_unreadable` 结束，便于脚本重试。128/129 及各命令特有的检查见文档站的 [exit codes](https://grit-scm.com/docs/exit-codes/) 页面。
- 共用参数规则：**`-n` 始终是列表条数上限**（绝不是 dry-run）；**`--dry-run`** 在会修改状态的命令上只有长格式；提交消息用 **`-m`**、**`-F` / `--message-file`** 或位置参数；路径操作数放在 **`--`** 之后。完整表格见 [CLI conventions](https://grit-scm.com/docs/cli-conventions/)。
- 不用 `cd` 也能操作别的仓库：把 **`-C <dir>`** 放在命令名之前（可重复；另有 `--git-dir <path>` / `--work-tree <path>`）。同样地，用 **`-c key=value`** 为单次运行覆盖配置（例如 `-c user.name=CI -c user.email=ci@example.com commit -m …`）；不会改动任何配置文件。
- 始终给 `grit commit` 提供消息（`-m`、位置参数，或 `-F` / `--message-file`，`-` 表示标准输入）。它从不打开编辑器。用 `--author "Name <email>"` 单次覆盖作者；`--no-verify` 跳过 `pre-commit` 和 `commit-msg`（`prepare-commit-msg` 仍会运行，并可能像 Git 里那样修改消息）。用 `--dry-run` 预览路径、父提交和作者，而不写入对象或更新引用（`--json` 会省略 `oid` 并设置 `dry_run: true`）。
- 不要照搬 Git 的交互模式（`git add -p`、`git rebase -i`、编辑器）。使用 `grit diff --json` 给出的稳定 **`hunks[].id`** 搭配 **`--hunks`** / **`--lines`**（见下文 **操作配方**）。`grit commit -a` / `--all` 强制自动暂存整棵树；`grit reset`、`grit rebase` 和 `grit history` 覆盖 Git 用 reset / 交互式 rebase 完成的历史编辑。

## 新建仓库

`grit init` 创建一个空仓库。默认分支是 `main`；省略 `-b` 时取 Git 配置中的 `init.defaultBranch`。用 `-b develop` / `--initial-branch` 覆盖。`--object-format sha256` 创建 SHA-256 对象库；`--separate-git-dir <path>` 让 `.git` 成为指向外部目录的 gitfile。重新初始化会保留现有的 `HEAD` 分支（新的 `-b` 名称被忽略）。`--json` 包含 `branch`、`object_format`，在分离目录时还包含 `git_dir`。

## 我在哪里？

```console
$ grit status --json
```

直接运行 `grit` 等同于 `grit status`。键：`branch`、`detached`、`head`、`target`（你的工作所指向的分支）、`ahead`、`commits`（目标分支上不存在的最多十个提交；每个提交行包含 `change_id` 和 `change_id_stored`）、`staged`、`unstaged`、`untracked`、`clean`。

目标分支取下列项中第一个存在的：`target.branch` 配置值、`origin/master`、`origin/main`、`master`、`main`；用 `grit config target.branch origin/develop` 修改。

## 读取历史与改动

| 任务 | 命令 |
| --- | --- |
| 未提交改动作为 diff | `grit diff` |
| 仅变更路径 | `grit diff --name-only` |
| 每个文件的行数统计 | `grit diff --stat` 或 `grit diff --numstat` |
| 某个提交所做的改动 | `grit show <commit>`（默认输出补丁；合并提交使用组合 diff，除非 `--diff-merges=first-parent`） |
| 一次查看多个提交 | `grit show <A> <B>`（`--json` → `{ "objects": [ … ] }`） |
| 某个修订的 blob 或 tree | `grit show <rev>:<path>`（解析方式同 `grit cat`） |
| 仅提交消息和 diffstat | `grit show [<commit-or-branch-or-tag>] --stat` |
| 最近历史，每次二十条 | `grit log`，然后用 `→ more` 行上的令牌执行 `grit log --cursor=<token>`（或 `--json` 里的 `next`；向 `--before` 传游标已废弃） |
| 带补丁或文件列表的历史 | `grit log -p`、`grit log --stat`、`grit log --name-status`……（格式参数与 `grit diff` 相同） |
| 本分支上不在目标分支的提交 | `grit shortlog` 或 `grit ahead`（`-n` / `--max-count`、`--behind`、`--stat`、`--name-only`；加 `--target <REF>` 选择基准） |
| 每行最后被谁改动 | `grit blame [<rev>] [--] <file>`；用 `-L` 切片（`10,25`、`10,+20`、`/pattern/`、`:funcname`）；大文件上加 **`--group`** 让 `--json` 输出更小的 `hunks[]`。不给修订时 blame 工作区文件（未提交行带 `not_committed: true` 和全零提交）；`--rev HEAD` blame 已提交的文件；`--contents <file\|->` blame 未保存的缓冲区 |
| 在 blame 中跳过格式化提交 | `grit blame --ignore-rev <OID>` 或 `grit blame --ignore-revs-file .git-blame-ignore-revs`（在配置里设 `blame.ignoreRevsFile` 作为默认列表） |
| 在 blame 中忽略纯空白改动 | `grit blame -w` / `--ignore-all-space`（拼写与 `grit diff -w` 相同） |
| 在 blame 中跨文件跟踪复制 | `grit blame -C`（最多重复 `-C` 三次以加深复制搜索，与 Git 相同） |
| 有 reflog 的引用 | `grit reflog list`（可选 `-n` / `--limit`；`--json` → `{ "refs": [{ "ref": "…" }] }`） |
| 某个引用的 reflog 条目 | `grit reflog [REF] --limit N`（默认 `HEAD`；可用分支短名） |
| 本分支最近发生了什么 | `grit reflog [REF] -n 20 --json`（`--since` / `--until` / `--grep`；`old_oid`、`new_oid`、`date`、`committer`，可选 `action`；索引与 Git 的 `ref@{n}` 一致） |
| 预览 reflog 过期 | `grit reflog expire --dry-run --json`（不写日志文件；`dry_run` 与逐引用的 `refs[].pruned`） |
| 丢弃旧的 reflog 条目 | `grit reflog expire`（gc 规则；`--expire`、`--expire-unreachable`、`--all`） |
| 该引用或对象是否存在？ | `grit resolve --verify <SPEC> --quiet`（退出 `0` = 存在，`1` = 不存在；无输出；只有在不用 `--quiet` 却需要 oid 时才加 `--json`） |

字面名为 `list` 的分支不是 `list` 子命令——用 **`grit reflog refs/heads/list`** 显示该分支的条目。

`grit diff --json` 在 **`--staged`** 或 **`--unstaged`** 的补丁输出中包含稳定的 **`hunks[].id`**（12 个小写十六进制字符）和 **`hunks[].index`**（在文件内从 0 开始）。id 对侧、路径和行内容做哈希（不含行号），因此较早的 hunk 被暂存后它们依然有效。使用 **`grit add --hunks <id,...>`** 或 **`grit add --lines path:start-end`**（新侧 **`lines[].new`**，从 1 开始、含端点）；提交区间 diff 目前省略 `id`。

**部分暂存：** `grit diff --unstaged --json -- path | jq '.files[].hunks[] | .id'` → `grit add --hunks id1,id2 -- path`，或选 **`lines[].new`** → `grit add --lines path:10-15 -- path`。可以混用 `--hunks` 和 `--lines`。一次性提交：**`grit commit --hunks id1,id2 -m msg -- path`** 或 **`grit commit --lines path:10-15 -m msg -- path`**。把选中的未暂存 hunk 收起而不动索引：**`grit stash push --hunks id1,id2`**（可选 **`--dry-run`**）。只收起部分路径（其余保持脏状态）：**`grit stash push -- path1 path2`**。apply/pop 时恢复收起的索引：**`grit stash apply --index`**。查看包含未跟踪文件的 stash：**`grit stash show -u`**。从 stash 建分支（基准提交 + 带索引应用）：**`grit stash branch <name> [<n>]`**。清空所有条目：**`grit stash clear --force`**（不带 `--force` 时以非零退出并报告数量；**`--dry-run`** 预览）。用 `--dry-run` 预览部分 hunk。未知/过期 id 或无效行范围退出码为 **2**。

**部分丢弃 / 取消暂存：** 在 **`grit restore --hunks`** / **`grit restore --lines`** 上使用相同的 id 或行范围（默认作用于工作区；加 **`--staged`** 取消暂存选中的 hunk）。**`--dry-run`** 只预览不写入。

修订可以是完整或短 id、分支或标签名，或 `HEAD~2` 这类表达式。

`log`、`show`、`revs` 和 `status` 的 `--json` 提交行共享 `change_id`（反向十六进制）和 `change_id_stored`。人类可读的 `log` 和 `show` 给每个提交加上 `change <8 字符>` 前缀；`--oneline` 不加。

## 提交

```console
$ grit commit -m "Explain what changed and why"
```

`grit commit` 默认 **自动暂存** 整个工作区（`commit.autoStage=true`），包括未跟踪文件，除非 `status.showUntrackedFiles=no`（此时只含已跟踪的修改/删除——与 `git commit -a` 及 status 显示一致）。用 **`grit commit --staged`** 只提交索引（设置 `commit.autoStage=false` 可让它成为默认）。用 **`grit commit -m msg -- <paths>`**（或 `--pathspec-from-file`）做部分提交，且不影响其他已暂存改动——类似 `git commit --only`；按路径提交仍可记录一个指定的未跟踪文件。`-a` / `--all` 强制自动暂存；`--staged` 与路径不能同时使用，也不能与 `-a` 组合。

**部分 hunk：** `grit diff --unstaged --json` → 选 `hunks[].id` → **`grit commit --hunks id1,id2 -m msg`**（可选 `-- paths`）。未知或过期 id 的退出码 **2** 与 `grit add --hunks` 相同。**`grit commit --patch-file file`** 先应用缓存的补丁再提交。这两种模式都不会自动暂存树中其余内容。

### 暂存（`grit add`）

| 任务 | 命令 |
| --- | --- |
| 暂存全部（修改、删除、未跟踪） | `grit add` |
| 仅暂存已跟踪的修改与删除 | `grit add -u`（或 `grit add --update`） |
| 只预览，不写索引 | `grit add --dry-run`（可与 `-u` 或路径组合） |
| 记录添加意图（空的索引位，尚无 blob） | `grit add -N -- path`（必须给路径；不改变已跟踪条目） |
| 暂存被忽略的路径 | `grit add -f -- ignored.log` |
| 暂存指定路径 | `grit add -- path/to/file` |
| 把 unified diff 应用到索引 | `grit add --patch-file file.diff`（或用 `-` 从标准输入；类似 `git apply --cached`） |
| 按 id 暂存选中的 diff hunk | `grit add --hunks <id,...>`（来自 `grit diff --json`；可选 `-- paths`） |
| 按行范围暂存 hunk 的一部分 | `grit add --lines path:start-end`（新侧行号来自 `grit diff --json`；可与 `--hunks` 混用） |

`grit add --json` 返回 `{added, modified, removed, intent_to_add, dry_run, count, staged}`，路径为仓库相对路径。批量暂存前先用 `--dry-run` 限定 Agent 的工作量；路径列表经过排序且稳定。使用 `--patch-file` 时，路径来自补丁（JSON 字段与按路径暂存相同）。

### 删除、重命名与清理路径

| 任务 | 命令 |
| --- | --- |
| 停止跟踪（默认同时从磁盘删除） | `grit rm -- <paths>` |
| 预览 `rm`，不写入 | `grit rm --dry-run -- <paths>` |
| `rm` 时忽略不存在的 pathspec | `grit rm --ignore-unmatch -- <paths>` |
| 重命名或移动已跟踪路径 | `grit mv <source>... <destination>` |
| 预览 `mv` | `grit mv --dry-run <source>... <destination>`（`--json` → `{moves:[{from,to}], dry_run}`） |
| 列出将被删除的未跟踪路径 | `grit clean`（默认 dry run） |
| 删除未跟踪路径 | `grit clean -f` |
| 只删除被忽略的未跟踪文件 | `grit clean --only-ignored`（不能与 `--ignored` 组合） |
| 从 clean 中排除路径 | `grit clean -e '<pattern>'`（可重复） |
| 只清理文件，不清理目录 | `grit clean --files-only` |

`grit commit` 在干净的工作树上会以 “nothing to commit” 失败，除非传 `--allow-empty`。在游离 HEAD 上它推进 `HEAD` 而不移动分支；用 `grit switch -c <name>` 把这些提交保留到新分支。切换到别处会让它们不属于任何分支；`grit switch --json` 在 `stranded_commits` 中列出它们（`--dry-run` 预览），用 `grit branch <name> <oid>` 保留它们。

每个提交都会得到一个稳定的 **`change-id`** 头（默认开启），并在 `--amend` 后保留。需要与 Git 完全一致的提交对象时，用 `grit config grit.changeIds false` 关闭。推导方式与测试配置见文档站关于 change id 的章节。

## 分支

| 任务 | 命令 |
| --- | --- |
| 列出分支 | `grit branch` |
| 带过滤 / JSON 详情 | `grit branch --list 'feat*' -a --merged main --sort date -n 20 --json` |
| 仅当前分支名 | `grit branch --show-current` 或 `grit resolve --abbrev-ref HEAD` |
| 上游跟踪分支名 | `grit resolve --abbrev-ref '@{u}'`（完整形式：`grit resolve --symbolic-full-name '@{u}'`） |
| 在当前提交建分支（不切换） | `grit branch <name>` |
| 在指定提交建分支 | `grit branch <name> <start>` |
| 建分支并设置上游跟踪 | `grit branch -t <name> <remote>/<branch>`，或依赖 `branch.autoSetupMerge` |
| 重命名分支 | `grit branch -m [<old>] <new>` 或 `grit branch -M <new>`（强制） |
| 设置 / 清除上游 | `grit branch -u <upstream> [<name>]`、`grit branch --unset-upstream [<name>]` |
| 预览任何分支变更 | 加 `--dry-run --json`（不改引用、配置或 reflog） |
| 创建并切换 | `grit switch -c <name>` |
| 切换 | `grit switch <name>`（也支持 `grit checkout`、`grit co`） |
| 删除已合并的分支 | `grit branch -d <name>` |
| 不管是否合并都删除 | `grit branch --force-delete <name>`（短格式 `-D`） |
| 预测合并冲突（不改仓库） | `grit merge --check <branch>`（退出 0 = 干净/可快进/已最新，1 = 会冲突；`--json` → `result: clean\|conflicts\|…`） |

`grit branch --json` 和 `--markdown` 列出 `full_ref`、`oid`、`subject`、`date`、可选的 `upstream`（`ref`、`remote`、`gone`、`ahead`、`behind`），以及在别处检出时的 `worktree`。人类可读列表在配置了上游时显示上游标记。

`grit switch`、`grit merge`、`grit pick`、`grit revert` 和 `grit pull` 在检出会覆盖本地修改或未跟踪文件时拒绝运行。切换前用 `grit switch <branch> --dry-run --json` 预检（只检查；报告 `changed_paths`）。被拒绝时，`--json` 输出 `kind: would_overwrite`，带 `reason`（`local_changes` 或 `untracked`）和排序后的 `paths`。

当另一个进程持有 `.git/index.lock` 时，暂存和提交会在更新索引或记录提交之前停止，`--json` 输出 `kind: lock_held`，带 `lock.path`（记录到持有者时还有 `lock.holder.pid` / `lock.holder.running`）。稍后重试；只有在没有 grit 或 git 进程运行，或 `lock.holder.running` 为 `false` 时才删除 `lock.path`。

有已知下一步的失败会在 `--json` 中携带 `hint`（并在 stderr 输出一行 `hint:`），指明要运行的命令；按 `kind` 分支处理：`no_remote` / `remote_not_found`（`grit remote add <name> <url>`）、`remote_no_url`、`auth_required` / `auth_rejected`（github.com 用 `grit auth`，其他用 `grit auth <url> --username <user> --token <token>` 或 `GIT_ASKPASS` 程序）、`remote_unreadable`（404 时给 hint）、`branch_no_upstream`（`grit pull origin <branch>` 或 `grit push -u origin <branch>`）、`unmerged_paths` 和 `dirty_worktree`（两者都带 `paths`）。

## 组合工作

- `grit merge <rev>` 能快进时就快进，否则记录一个合并提交。`<rev>` 可以是本地或远程跟踪分支（`origin/main`）、标签（`v1.2`）、提交 id，或 `topic~2` 这类表达式；未知名称以 JSON `kind: revision_not_found` 失败。用 `grit merge --check <rev>` 在内存中预测冲突，不碰引用、索引或工作区。常用参数：`--ff-only`（分叉时退出 128）、`--no-ff`、`--squash`（写 `SQUASH_MSG`；用 `grit commit` 收尾）、`--no-commit`（Git 合并状态；用 `grit commit` 收尾）、`-X ours|theirs`、`--conflict diff3|zdiff3|merge`、`--allow-unrelated-histories`、`-m` / `-F` / `--message-file`。合并提交会像 Git 一样运行 `pre-merge-commit`、`prepare-commit-msg` 和 `commit-msg`；钩子拒绝时退出 **1** 并带 `kind: hook_failed`，合并保持进行中（`MERGE_HEAD`，分支不变），并给出 `grit merge --continue` 或 `--abort` 的 `hint`。`--no-verify` 跳过 `pre-merge-commit` 和 `commit-msg`；`grit rebase --no-verify` 跳过 `pre-rebase`。
- `grit pick [<commit>…]` 把提交 cherry-pick 到当前分支（支持区间）。用 `grit pick --check` 在不改引用、索引或工作区的情况下预测冲突（退出 0 = 干净，1 = 会冲突或空停止）。`-X ours|theirs` 自动解决重放冲突；`--conflict diff3|zdiff3|merge` 设置步骤停下时的标记风格。
- `grit revert [<commit>…]` 撤销一个或多个提交（支持区间；从最新开始）。合并提交需要 `--mainline <n>`。`-m` / `-F` / `--message-file` 只为 **单个** 提交设置消息。`grit revert --check` 与 pick 的 `--check` 契约一致；同样适用 `-X` 和 `--conflict` 参数。
- `grit revert --continue`、`--abort` 和 `--skip` 恢复或取消停下的 revert 序列（冲突模型与 pick 相同）。
- 发生冲突时，这些命令会用冲突标记更新索引和工作区，退出 1，并把 merge/pick/revert/rebase 状态留在磁盘上。要查看某一侧或在不解决的情况下重建标记，对冲突路径使用 `grit restore --ours`、`--theirs` 或 `--merge`（索引保持未合并）。修复冲突（`grit diff`）、暂存（`grit add`），合并用 `grit commit` 收尾，pick/revert/rebase 分别用 `grit pick --continue` / `grit revert --continue` / `grit rebase --continue`。用同一命令的 `--abort` 取消；`grit rebase --skip` 跳过当前提交。

## 改写历史

- `grit history drop`、`move`、`reword`、`fixup`、`squash` 和 `absorb` 共用 `--dry-run`、`--update-refs`、`--empty=(drop|keep|abort)`（空的重放提交）和 `--keep-committer`（保留每个重放提交的 committer 行）。
- `grit history fixup` 像 `grit add` 一样接受 **`--hunks`** 和 **`--lines`**，可以把选中的未暂存改动折进历史提交，而不暂存整个文件；可选的 `-- paths` 缩小 diff 范围。不带这些参数时，fixup 使用已暂存的索引（与之前相同）。

## 远程仓库

| 任务 | 命令 |
| --- | --- |
| 复制仓库 | `grit clone <url> [<dir>]`（`--depth N`；`-b` / `--branch` 指定分支或标签；隐藏的 `--shallow` = `--depth 1`；`--blobs none` 或 `--blobs 1k` 做部分克隆） |
| 面向 CI/Agent 的快速克隆 | `grit clone --depth 1 …` 或 `grit clone --blobs none …`（`-q` 静默进度和摘要；fetch、pull、push 也接受 `-q`） |
| 列出、添加、删除、修剪、设置默认分支或显示远程 | `grit remote`、`grit remote add <name> <url> [--fetch]`、`grit remote -v`、`grit remote remove <name>`（`--dry-run`）、`grit remote prune <name>`（`--dry-run`）、`grit remote set-head <name> (--auto \| <branch> \| --delete)`（`--dry-run`）、`grit remote show <name> [--no-query] [-n N]` |
| 修正远程 URL | `grit remote set-url <name> <url>`（fetch URL）；`grit remote set-url --push <name> <url>` 只改 push；`--dry-run` 预览 |
| 重命名远程 | `grit remote rename <old> <new>`；`--dry-run` 预览；会重命名跟踪引用并重定向分支上游配置 |
| 下载但不改当前分支 | `grit fetch [<remote>]` |
| 只 fetch 一个分支或引用 | `grit fetch origin main`（PR 用 `grit fetch origin pull/123/head:pr-123`） |
| 浅 fetch 控制 | `grit fetch --depth N`、`--deepen N` 或 `--unshallow`（语义同 Git；互斥） |
| 强制更新标签或分支 | `grit fetch -f` / `--force` 配合 `--tags` 或 `+refs/…` refspec；默认 fetch 忽略你已经有的、被移动的标签 |
| 拉取并合并本分支的远程副本 | `grit pull` |
| 仅在可快进时拉取 | `grit pull --ff-only`（成功退出 **0**，分叉时退出 **128** 并带 `refused_not_ff`；分支保持不变） |
| 拉取并在上游之上重放本地提交 | `grit pull --rebase`（或配置 `pull.rebase`；冲突时带标记停下，退出 **1**，`--json` 中 `operation: rebase` 和 `next_steps`：解决、`grit add`、`grit rebase --continue`，或 `--abort` / `--skip`；`grit pull --check` 可预测） |
| 把本地提交重放到另一个基上 | `grit rebase [<upstream>]`（默认 `@{upstream}`；`--onto`；`--check` 无副作用预测冲突；`-X ours\|theirs` 与 `git rebase -X` 一致，其中 **ours** 是 onto/上游；冲突时用 `--continue` / `--abort` / `--skip` 停下，退出 **1**） |
| 把本分支以同名发布到 `origin` | `grit push` |
| 推送到不同的远程分支名 | `grit push origin HEAD:refs/heads/<name>` |
| 安全地发布改写过的历史 | `grit fetch`，然后 `grit push --force-with-lease`（单个引用用 `--force-with-lease=<rev>`）；租约过期 → 退出 **1**，`"rejected": true` |
| 发布所有本地标签 | `grit push --tags` |
| 删除远程分支或标签 | `grit push origin --delete <ref>...`（每个引用一行 `results`；引用不存在 → 退出 **1**、`remote_ref_missing`；`--delete` 旁出现 `src:dst` refspec 是错误，且不会推送任何内容） |

普通推送必须能快进远程。如果远程有你没有的提交，grit 会拒绝推送（退出 **1**，`"rejected": true`）；先运行 `grit pull`，再推送。经过 `grit history` 编辑（reword、drop、fixup、squash、split、rebase）或 `grit rebase` 之后，先 fetch，再用 `--force-with-lease` 代替 `--force`，以免覆盖别人的工作。确实需要时 `--force` 会无条件覆盖。失败的 `pre-push` 钩子会在发送任何内容之前阻止推送（退出 **1**，`"error": "hook pre-push failed …"`）；`--no-verify` 跳过它。

历史改写成功后（drop、move、reword、fixup、squash、absorb 或 rebase apply），grit 会把引用计划存到 `.git/grit/history-last`。当引用顶端未变时，`grit history undo` 会恢复这些引用；再运行一次即重做。撤销 fixup 或 absorb 还会把被消耗的已暂存 / 选中改动放回索引和工作区（`--json` 中的 `restored_paths`）；没有保存状态的记录会以 `unrestored_edits` 报告承载它们的提交。用 `--dry-run` 预览引用移动。引用已移动、恢复的路径在命令之后被编辑过，或本地改动会被覆盖时，undo 会拒绝执行。

URL 可以是 `https://`、`ssh://`、`user@host:path`、`git://`、`file://` 或本地路径。

## 操作配方

按顺序照抄这些命令序列。除非另有说明，每一步都假定使用 **`--json`**。读取 HTML 注释中列出的 **`fields`**（CI 在 `skill_recipes_run` 中运行同样的代码块）。出现 **`$HUNK0`** 时，用上一步 JSON 的值替换。

### 精确提交（hunk、路径或仅索引）

```console recipe:precise-commit
<!-- step exit=0 fields=files.0.hunks.0.id -->
$ grit diff --unstaged --json -- partial.txt
<!-- step exit=0 fields=oid -->
$ grit commit --hunks $HUNK0 -m "commit one hunk" --json
<!-- step exit=0 -->
$ grit add -- staged-only.txt
<!-- step exit=0 fields=oid -->
$ grit commit --staged -m "commit staged index only" --json
<!-- step exit=0 -->
$ grit add -- partial-other.txt
<!-- step exit=0 fields=oid -->
$ grit commit -m "commit one path" --json -- partial-other.txt
```

其他路径是脏的时候，在 diff 前先用 **`grit add -- partial.txt`**（或按路径暂存）。**`--staged`** 只提交索引中已有的内容；**`-- paths`** 提交子集，不自动暂存树中其余内容。

### 处理合并冲突

```console recipe:merge-conflict
<!-- step exit=1 fields=result -->
$ grit merge --check topic --json
<!-- step exit=1 fields=result -->
$ grit merge topic --json
<!-- step exit=0 -->
$ grit restore --ours -- conflict.txt
<!-- step exit=0 -->
$ grit add -- conflict.txt
<!-- step exit=0 fields=oid -->
$ grit merge --continue --json
```

需要放弃这次尝试时，运行 **`grit merge --abort`**（回到合并前状态）。在 merge 与 restore 之间用 **`grit diff`** / **`grit status --json`** 查看冲突路径。

### rebase 并用租约推送

```console recipe:rebase-push-lease
<!-- step exit=0 -->
$ grit fetch origin --json
<!-- step exit=0 fields=result -->
$ grit rebase --check origin/main --json
<!-- step exit=0 fields=result -->
$ grit rebase origin/main --json
<!-- step exit=1 fields=rejected -->
$ grit push --force-with-lease --json
<!-- step exit=0 -->
$ grit fetch origin --json
<!-- step exit=0 fields=result -->
$ grit rebase --check origin/main --json
<!-- step exit=0 fields=result -->
$ grit rebase origin/main --json
<!-- step exit=0 fields=rejected -->
$ grit push --force-with-lease --json
```

改写历史后，始终先 **fetch** 再 **`--force-with-lease`**。退出 **1** 且 **`"rejected": true`** 表示远程已移动或租约过期——先 **fetch**，然后 **`rebase --check`** 并在更新后的上游上 **`rebase`**（在本地历史包含刚 fetch 的内容前不要再次推送），再重试 **`--force-with-lease`**。只有确实要覆盖远程工作时才用 **`--force`**。

### Fetch 一个 Pull Request 引用

```console recipe:fetch-pr
<!-- step exit=0 -->
$ grit fetch origin pull/1/head:pr-1 --json
<!-- step exit=0 fields=branch -->
$ grit switch pr-1 --json
```

GitHub 在 **`origin`** 上以 **`pull/<n>/head`** 暴露 PR 头。该 refspec 会创建本地分支 **`pr-<n>`**，无需先检出默认分支。

### 浅克隆再加深

```console recipe:shallow-clone
<!-- step exit=0 fields=depth -->
$ grit clone --depth 1 $REMOTE_URL $CLONE_DIR --json
<!-- step exit=0 fields=shallow -->
$ grit fetch --deepen 1 --json
<!-- step exit=0 fields=shallow.removed -->
$ grit fetch --unshallow --json
```

在克隆目录（`$CLONE_DIR`）内运行 **`fetch`** 步骤。克隆时 **`--depth 1`** 是常见的 Agent 默认值；**`--deepen`** 逐步增加历史；需要完整历史时用 **`--unshallow`** 移除浅边界。

## 打包文件与关联工作树

| 任务 | 命令 |
| --- | --- |
| 离线打包传输 | `grit bundle create`、`verify`、`list`、`unbundle` |
| 额外工作树 | `grit worktree list`、`add`（`-b`、`-B`、`--detach`、`--lock`、`--no-checkout`、`--track`）、`remove`、`move`、`repair`、`lock`、`unlock`、`prune`（`--dry-run`）——`list --json` 含 `is_current`、`lock_reason`（无锁时为 null），可修剪时含 `prunable_reason`；`move` / `repair` 支持 `--dry-run` |

## 标签与配置

- `grit tag` 列出标签（默认 `--sort=version`）。过滤：`-l/--list <pattern>`（可重复）、`--sort version|date|name`、`--reverse`、`--contains [REV]`、`--points-at <REV>`、`-n` / `--limit`。`--json` 列表在附注标签上包含 `target_kind` 和 `annotation`（subject、message、带 RFC 3339 `date` 的 tagger）；人类可读输出在名称旁显示 subject。
- `grit tag <name> [<target>]` 在 `HEAD` 或 `<target>` 上创建轻量标签。`-m` / `-F` / `--message-file` 创建附注标签（`--file` 是 `--message-file` 的废弃别名）；`-f` 替换已有标签；`--dry-run` 预览创建/删除。`grit tag -d <name>` 删除一个。`grit tag --verify <name>…` 检查附注标签签名和可选的 `tree-sha256` 声明（任一失败则退出 1）；`--no-signature` 跳过签名检查。
- `grit config <key>` 读取，`grit config <key> <value>` 设置，`grit config --unset <key>` 删除，`grit config --list` 列出。用 `--global`、`--local` 或 `-f <path>` 指定作用域。缺失的键退出 **1**；`--json` 返回 `"value": null`，设置时带 scope/file/line。

## 保持非交互

- HTTPS GitHub：在交互式会话中运行一次 `grit auth`（它使用浏览器设备流）。之后 fetch、pull 和 push 使用已存令牌。stdin 不是终端时，grit 不会提示登录；它会带 hint 失败。
- 其他主机的 HTTPS（GitLab、Gitea、公司服务器）：grit 从不提示输入密码。用 `grit auth <url> --username <user> --token <token>` 保存一次用户名和令牌（存到该主机的凭据 helper），或在 CI 里提供 `GIT_ASKPASS` 程序。已存令牌被拒绝时以 `auth_rejected` 失败；用同样方式存新的。
- SSH：设置 `GIT_SSH_COMMAND='ssh -o BatchMode=yes'`，让缺失密钥或未知主机快速失败，而不是等待输入。
- 不要在自动化里运行 `grit update`；它会重装二进制。
- `grit manager`、`grit upload-pack` 和 `grit receive-pack` 是在 stdin/stdout 上说 Git 协议的管道命令。不要直接调用。

## grit 不做什么

grit 没有 TTY 或编辑器工作流：没有 **`add -p`**、**`restore -p`**、**`rebase -i`**，也没有不带 `-m`/`-F` 的 **`commit`**。部分暂存和丢弃改用 `add`、`restore`、`commit` 和 `stash push` 上的 **`--hunks`**、**`--lines`** 和 **`--patch-file`**。**`grit tag -m`** 创建附注标签；`grit tag --verify` 之外的 OpenPGP 签名与验证不在目标内——需要完整签名工作流时用 `git`。合并冲突期间，用 `grit restore --ours|--theirs|--merge` 比较两侧或还原标记，然后用 `grit merge --continue`（或 `grit commit` 做 Git 兼容的收尾）。用 `grit commit --amend`（可选消息，JSON `amended` 字段）改写顶端提交。带工作区合并冲突的 `grit stash pop` 或 `grit stash apply`，解决路径（例如用 `grit restore --ours|--theirs|--merge`），并按需保留或丢弃 stash 条目。带 `--index` 的仅索引冲突会失败，且不改工作区或索引。任务需要 grit 刻意跳过的能力时，在同一个仓库上用 `git`，完成后再回到 `grit`。
