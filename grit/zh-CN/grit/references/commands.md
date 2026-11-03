# Grit 命令参考（v0.5.x）

本文件是 `grit` 全部命令的速查：语法、关键行为边界、JSON 输出。
字段细节以本机 `grit <命令> --help` 与 <https://grit-scm.com/docs/> 各命令页为准；标注「main」的条目不在 v0.5.2。

## 调用形式与全局选项

```text
grit [OPTIONS] [COMMAND]
```

| 项 | 说明 |
| --- | --- |
| 裸 `grit` | 等价于 `grit status`；`--json` 同样可用 |
| `--json` | stdout 恰好一个 JSON 值；失败时 `{"error": "..."}`，退出码非 0 |
| `--filter <EXPR>` | jq 风格表达式，须与 `--json` 同用；多结果合成一个数组；表达式非法时输出 `{"error": ...}` |
| `-h` / `--help`、`-V` / `--version` | 帮助与版本；`--version` 即使加 `--json` 也只打印版本行（如 `grit 0.5.2`），不产生 JSON |
| `--markdown` | **仅 main，v0.5.2 无** |

别名：`st` = `status`；`sl` = `shortlog`；`co` / `checkout` = `switch`。
仓库发现与 Git 相同（支持 `GIT_DIR`、`GIT_WORK_TREE`、`GIT_CEILING_DIRECTORIES` 等）。

## 仓库与配置

### grit init

```text
grit init [--bare] [<path>]
```

- 目标目录不存在会自动创建；不传路径则初始化当前目录；默认分支固定为 `main`。
- 选项只有 `--bare`。文档中的 `--ref-format <files|reftable>`（reftable 引用后端）属 main，v0.5.2 传它会报 `unexpected argument`（exit 2）。
- JSON（v0.5.2）：`initialized`、`path`、`bare`、`branch`（**没有** `ref_format`）。

### grit clone

```text
grit clone <url> [<dir>]
```

- 支持 `https://`、`http://`、`ssh://`、`user@host:path`、`git://`、`file://` 与本地路径；本地路径会被存成绝对路径。
- 远程固定存为 `origin`；检出远程默认分支；目标目录必须不存在或为空。
- 从浅克隆源克隆在 v0.5.2 会失败（`object not found`）；需要浅克隆时用 git 克隆、再由 grit 接管该仓库。私有 GitHub HTTPS 需先 `grit auth`。
- JSON：`url`、`path`、`branch`。**无** `--depth` / `--branch` / `--bare` 等选项（需深度控制用 git）。

### grit config

```text
grit config [--global] <key>            # 读
grit config [--global] <key> <value>    # 写
grit config [--global] --unset <key>    # 删
grit config [--global] --list           # 列
```

- 读写与 Git 完全相同的文件：仓库 `<repo>/.git/config` 与用户 `~/.gitconfig`；两侧设置互通。
- 读取沿配置级联（仓库优先于全局）；写默认写入仓库级，`--global` 写用户级；读取/删除不存在的键报错（exit 1）。
- 两级之外的作用域（`--system`、`--add` 多值等）没有，用 git。
- grit 会使用的键（文档列出）：`user.name`、`user.email`、`target.branch`、`branch.<name>.remote`、`branch.<name>.merge`、`credential.helper`、`grit.githubClientId`、`receive.denyNonFastForwards`、`receive.denyDeletes`、`receive.denyCurrentBranch`；签名相关的 `commit.gpgsign`/`gpg.*`/`user.signingkey` 在 v0.5.2 **未生效**（见 commit 一节）。
- JSON：`action`（`get`/`set`/`unset`/`list`），`get`/`set` 带 `key`、`value`，`list` 带 `entries[]`。

### grit status（默认命令；别名 st）

```text
grit
grit status
grit st
```

自上而下显示：当前位置（分支 + 相对 target 领先多少及其提交，最多 10 条；无提交时 `no commits yet`；游离 HEAD 显示所在提交）→ **Staged** → **Changed (not staged)** → **Untracked** → 下一步提示。
改动标签（文档取值）：`new`、`modified`、`deleted`、`renamed`、`copied`、`type changed`、`conflict`；实测文件改名（含 `git mv`）显示为 `added` + `deleted` 两条，未观察到 `renamed`。

**target 解析顺序**：`target.branch` 配置 → `origin/master` → `origin/main` → `master` → `main`。

无任何选项。JSON 字段：`branch`（游离时为 null）、`detached`、`head`、`target`、`ahead`、`commits[]`（`oid`/`subject`，最多 10）、`staged[]`、`unstaged[]`（各含 `path`/`status`）、`untracked[]`、`clean`。

### grit auth

```text
grit auth          # GitHub device flow 登录并存储 token
grit auth logout   # 删除已存 token
```

- 打印网址与短码，浏览器授权后存 token 到 `credential.helper`；Windows 无 helper 时用内置 `grit manager`（Windows Credential Manager）。
- 其他平台需先配置：`grit config --global credential.helper osxkeychain|libsecret|store`。
- 自定义 OAuth app：环境变量 `GRIT_GITHUB_CLIENT_ID` 或配置 `grit.githubClientId`。
- JSON：`authenticated`/`logged_out`、`host`；无 helper 可存时 `logged_out` 为 false。

## 提交

### grit add

```text
grit add [<path>...]
```

- 无路径 = 暂存一切（修改、删除、未跟踪）；有路径则只暂存这些文件/目录。
- 路径相对当前目录，支持 `../` 与仓库内绝对路径；不匹配任何文件报错（exit 1）。
- **注意**：`grit commit` 会重新全量暂存，`add` 的暂存结果不决定提交内容——它主要用于预暂存与查看状态。
- **没有取消暂存/反向补丁**（无 `git reset`/`git restore --staged`/`add -p`）。
- JSON：`staged`（本次暂存的路径数）。

### grit commit

```text
grit commit [-a] <message>
grit commit [-a] -m <message>
```

- **总是提交工作区全部改动**（修改、删除、未跟踪）；`-a` 只是兼容 git 习惯（如 `-am`），行为不变。
- 消息必填（位置参数或 `-m`，二者不能同用）；多行消息首行为 subject；**不打开编辑器，无 `$GIT_EDITOR` 路径**。
- 作者/提交者取自 `user.name`/`user.email`；可用 `GIT_AUTHOR_DATE`、`GIT_COMMITTER_DATE` 固定时间。
- **签名在 v0.5.2 未生效**：文档描述 `commit.gpgsign`（OpenPGP/X.509 走 `gpg`/`gpgsm`，SSH 走 `ssh-keygen -Y sign`），但实测即使设为 true，提交照样成功且对象不带 `gpgsig`。需要签名提交时用 git。
- 失败情形：无改动可提交；HEAD 游离；无消息。
- **无** `--amend`、无 `--no-verify`、无部分提交/路径限制。
- JSON：`oid`、`branch`、`subject`、`changes`。

### grit diff

```text
grit diff [<commit>]
```

- 无参数：工作区全部未提交改动（暂存与未暂存**合并**展示，无法只看暂存区）；有参数：该提交相对其第一父的改动。
- `<commit>` 可以是完整/短 oid、分支、标签或 `HEAD~2` 这类表达式。
- 每文件以路径开头，hunk 标位置；行号两列（改动前后）；TTY 下彩色高亮行内改动，非 TTY 或 `NO_COLOR` 时用 `-`/`+`；默认 3 行上下文；二进制文件只报不显示。
- **无** `--staged`/`--cached`（都会报 exit 2）、无路径过滤、无两个提交间/范围 diff（这些交给 git）。
- JSON：`files[]`，各含 `path`、`status`、`binary`、`hunks[]`（`old_start`/`new_start`、`lines[]` 带 `kind`（`context`/`add`/`del`）与行号、`segments[]` 带可选 `emphasis`）。

## 历史检视

### grit log

```text
grit log [--before <commit>]
```

- 从 HEAD 可达提交、新到旧、**每页 10 条**；每行：短 oid、作者（邮箱 `@` 前缀或名字）、时间、subject；还有历史时末行给出 `→ more: grit log --before=<oid>`。
- 只支持 `--before` 翻页；无 `--all`/`--graph`/`--author`/`--grep`/`-p`/路径过滤/范围（用 git）。
- 空仓库（无提交）报错 `could not list commits from HEAD`（exit 1）；游离 HEAD 下可用。
- JSON：`commits[]`（`oid`/`subject`，≤10 条）、`next`（下一页的完整 oid，或 null）。

### grit shortlog（别名 sl）

```text
grit shortlog
```

- 列出当前分支相对 target 领先的**全部**提交（不受 10 条限制）+ 目标分支名。
- target 解析同 `status`。
- 注意与 git 的 `shortlog` **语义不同**：git 是按作者汇总提交；grit 是「相对目标的领先清单」。
- JSON：`branch`、`target`、`ahead`、`commits[]`（`oid`/`subject`）。

### grit show

```text
grit show [<object>]
```

- 显示提交 id、作者、日期、完整消息，以及所改文件与增删行数汇总；无参数 = HEAD。
- `<object>` 支持 oid、表达式、分支、标签；命名分支/标签时首行显示名称；**附注标签**（annotated tag）会先显示标签自身的作者、日期与消息。
- 要看完整改动内容用 `grit diff <commit>`。
- JSON：`kind`（`commit`/`branch`/`tag`/`annotated_tag`）、`ref_name`（按 id 查看时省略）、`tag`（附注标签时）、`commit`（`oid`/`parents`/`author`/`committer`/`subject`/`message`）、`stat`（`files[]`/`files_changed`/`insertions`/`deletions`）。

## 分支与合并

### grit branch

```text
grit branch
grit branch <name>
grit branch -d <name>
grit branch -D <name>
```

- 无参数列出本地分支并以 `*` 标记当前分支。
- `<name>` 在当前提交处创建分支（**不切换**；要建且切用 `grit switch -c`）。
- `-d` 删除，未完全合并进当前分支时拒绝并提示用 `-D`；不能删除当前所在分支。
- **名称校验是部分的（v0.5.2 实测）**：结构性坏名（如结尾 `/`）会被拒绝（`invalid ref: refusing to update ref with bad name`），但 git 认为非法的名字——含空格、`..`、以 `.lock` 结尾、以及保留名 `HEAD`——实测都能创建成功。要保证与 git 兼容，请自行按 `git check-ref-format --branch` 校验，或用 git 创建。
- **文件/目录冲突**：分支 `feature` 与 `feature/login` 不能并存（后创建的一方报 `cannot lock ref … non-empty directory … blocking reference`），规则与 git 的 files 后端一致。
- **无** 重命名（`-m`）/upstream/远端分支列表/`-v` 详情。
- JSON：`action`（`list`/`create`/`delete`）；`list` 带 `current`、`branches[]`（`name`/`current`）；`create` 带 `name`；`delete` 带 `name`、`oid`、`short_oid`。

### grit switch（别名 co / checkout）

```text
grit switch <branch>
grit switch -c <branch>
```

- 切到本地分支并更新工作区；`-c` 在当前提交创建后切换（已存在则报错）。
- **有未提交改动（含暂存）拒绝执行**（exit 1，提示先提交）；未跟踪文件原地保留，但若目标分支在同路径有文件则停止而不覆盖。
- 游离 HEAD 下可以 `grit switch <branch>` 回到分支。
- **无** `--detach`、无强制切换、无文件级检出（`git checkout -- <file>` 需用 git）。
- JSON：`branch`、`created`。

### grit merge

```text
grit merge <branch>
```

- 三种结果：已包含（`up_to_date`，无变化）→ 快进（`fast_forward`，不产生新提交）→ 真合并（生成提交，提交消息为 `Merge <branch>`，CLI 输出 `Merged <branch> into the current branch (<oid>)`）。
- `<branch>` 可为本地分支或远程跟踪分支（如 `origin/main`），本地优先。
- **冲突时**：列出冲突文件，报错 exit 1，分支与工作区保持原样；grit 不解决冲突——改用 `git merge <branch>` 收尾（官方指引）。
- 拒绝执行的场景：有未提交改动、当前分支无提交、游离 HEAD、未跟踪文件会被覆盖。
- **无任何选项**（`--squash`/`--no-ff`/`--abort`/`-m` 都没有）。
- JSON：`result`（`up_to_date`/`fast_forward`/`merged`/`set_upstream`）、`branch`、`oid`、`upstream`。

### grit pick

```text
grit pick <commit>
```

- 把 `<commit>` 的改动作为新提交应用到当前分支（单提交 cherry-pick）；**保留原作者与消息**。
- `<commit>` 支持 oid、分支名（取其尖端提交）、`feature~2` 表达式。
- 拒绝（且不做任何改动）：有未提交改动/分支无提交/游离 HEAD；目标是合并提交；改动为空或已在当前分支；有冲突；未跟踪文件会被覆盖。
- **无** 多提交/区间、无 `-n`、无 continue/abort（用 git）。
- JSON：`source`、`oid`、`subject`。

## 远程与发布

### grit remote

```text
grit remote
grit remote add <name> <url>
```

- 无参数列出远程与 URL；`add` 新增（同名已存在则失败）。
- URL 支持 `clone` 接受的全部形式（https/ssh/git/file/本地路径）。
- clone 会自动加 `origin`。
- **无** `remove`/`rename`/`set-url`/`get-url`/`show`/`prune`（用 git）。
- JSON：`action`（`list`/`add`）；`list` 带 `remotes[]`（`name`/`url`）；`add` 带 `name`/`url`。

### grit fetch

```text
grit fetch [<remote>]
```

- 下载远程全部新内容，更新远程跟踪分支（如 `origin/main`）与新标签；**不动本地分支与工作区**。
- 远端默认 `origin`；逐条列出更新的 ref（旧→新 oid）。
- 在 Git 建的浅克隆中可正常使用（实测）：`grit fetch` 尊重既有 shallow 边界，并更新远程跟踪分支与新标签。
- **无** `--prune`（过期的远程跟踪分支不会清理）/`--all`/refspec/`--depth`（用 git）。
- JSON：`remote`、`updates[]`（`ref`/`old_oid`/`new_oid`，新增 ref 的 `old_oid` 为 null，删除的 `new_oid` 为 null）、`updated`。

### grit pull

```text
grit pull
```

- = fetch + 把「当前分支对应的远程分支」整合进来：无本地新提交则快进；双方都有新提交则生成合并提交；分支尚无提交时直接采用远程的。
- 目标远端：`branch.<name>.remote`（默认 `origin`）；目标分支：`branch.<name>.merge`（默认同名）。
- 同 `merge`：有未提交改动或游离 HEAD 拒绝；冲突时不做任何改变（exit 1）。
- **无任何选项**（`--rebase`/`--ff-only` 等都没有）。
- JSON 形态同 `merge`。

### grit push

```text
grit push
grit push --tags
```

- **无参数**：把当前分支推到 `origin` 同名分支（不存在则创建）；没有 `-u`/upstream 概念，无 refspec。
  - 改推送目的地：`grit config branch.<name>.remote <remote>` 与 `branch.<name>.merge <ref>`。
- **永不覆盖远程提交**：远程有新提交时拒绝（exit 1，JSON 里 `rejected: true`、`status: "rejected"` 与 `reason`），提示先 `grit pull`；**没有 force push**。
- `-t`/`--tags`：推送全部本地标签（而非当前分支）。
- GitHub HTTPS 未登录导致失败时，会提示并可代为运行 `grit auth` 后重试。
- JSON：`remote`、`branch`（或 `--tags`）、`results[]`（`ref`/`status`：`ok`/`up_to_date`/拒绝）、`rejected`。

### grit tag

```text
grit tag
grit tag <name>
grit tag -d <name>
```

- 无参数列出标签；`<name>` 在**当前提交**（HEAD）创建**轻量标签**（无自身消息）；`-d` 删除。
- 名称校验与 `branch` 一样只是部分校验（见上）：git 认为非法的名字可能被接受；需要 git 兼容时用 `git check-ref-format refs/tags/<name>` 自行校验。删除不存在的标签报错。
- 本地创建，需 `grit push --tags` 发布。
- **无** 附注标签（`-a`/`-m`）、无指定其他提交、无 `-f` 覆盖。
- JSON：`action`（`list`/`create`/`delete`）；`list` 带 `tags[]`（`name`/`oid`）；`create` 带 `name`/`oid`。

## 维护与内部命令

| 命令 | 说明 |
| --- | --- |
| `grit update` | 重跑官方安装脚本替换当前二进制（Unix `curl \| sh`，Windows PowerShell）。**无人值守任务不要调用**，除非就是要升级。 |
| `grit manager` | Windows 凭据 helper（Windows Credential Manager）。plumbing，无 `--json`。 |
| `grit upload-pack` / `grit receive-pack` | 经 stdin/stdout 提供 fetch/push 的 smart 协议服务端（由 ssh 与 grit-http-server 调用）。plumbing，**无 `--json`**，不要包成 JSON 命令。 |
| `grit skill` / `grit completions` | **仅 main，v0.5.2 无**：打印内置 SKILL.md / 生成补全脚本。 |

## 命令覆盖对照（一眼看清缺什么）

| Git 能力 | grit 状态 |
| --- | --- |
| 状态/提交/日志/查看/分支/切换/合并/cherry-pick/标签/远程同步 | 有（更窄，见各节「无」标注） |
| `reset`、`restore`、`clean`、`rm`、`mv`、`stash`、`apply` | 无 |
| `rebase`、`revert`、`commit --amend`、`filter-repo` | 无 |
| `blame`、`grep`、`bisect`、`reflog`、`describe` | 无 |
| `gc`、`prune`、`repack`、`fsck`、`worktree`、`submodule`、`notes`、`bundle`、LFS | 无 |
| force push、refspec、`push -u`、`remote set-url`、`fetch --prune` | 无 |
| 附注标签、`branch -m`/`-u`、`switch --detach`、`diff --staged` | 无 |

完整清单、按类归组与逐条回退命令见 [git-gaps.md](git-gaps.md)。
