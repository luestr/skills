# Git 有而 Grit 没有的能力（v0.5.x）

判定依据：<https://grit-scm.com/docs/> 命令索引、Grit 仓库 `AGENTS.md`（含「What we drop」）、以及对 v0.5.2 二进制的实测。
结论先行：**grit 是 Git 的刻意精简子集**。它保证的是「磁盘格式与 wire protocol 兼容」，不是 argv 兼容；
每个常见动作只保留一条路径，其余全部交给 `git`。与本清单相关的一切操作，回退到 `git` 都是设计内用法，不是绕过。

## 先理解边界（决定要不要用 git 的三条规则）

1. **需要「只动一部分」时**：部分提交、部分暂存、取消暂存、暂存区挑选——grit 没有暂存区工作流，用 git。
2. **需要「改写既有历史」时**：amend、rebase、revert、force push、filter——grit 一律不做，用 git。
3. **需要「更细的控制」时**：diff/log 的筛选与范围、merge/pull/push 的选项、克隆深度、远程管理——grit 的命令选项极少，用 git。

反过来，日常的「看状态 → 提交全部 → 建/切分支 → 合并 → fetch/pull/push → 打标签」grit 都能覆盖，且输出对人和机器都更友好。

## 1. 暂存与工作区还原

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `git reset`（取消暂存、`--soft/--mixed/--hard` 回退提交） | 无 | `git reset` / `git reset --hard <commit>` |
| `git restore [--staged] [--source]` | 无 | `git restore --staged <file>`、`git restore <file>` |
| `git clean -fd`（清掉未跟踪文件） | 无 | `git clean -nd` 先预览，再 `git clean -fd` |
| `git rm --cached`（停止跟踪但保留文件） | 无 | `git rm --cached <file>`；注意普通删除会被 `grit commit` 直接记为删除 |
| `git mv`（改名） | 无 | 直接在磁盘改名；`grit status` 显示为 `added` + `deleted`（v0.5.2 实测未做 rename 检测），`grit commit` 照常记录；历史里的改名靠 git 的 `-M`/`--follow` 在查看时识别 |
| `git add -p/-i`（交互式挑选暂存） | 无 | `git add -p` |
| **部分提交**（`git commit <paths>`、只提交一部分改动） | **无**：`grit commit` 永远全量提交 | `git add <paths> && git commit -m "…"`，或 `git commit -m "…" -- <paths>` |
| `git stash push/pop/list/apply/-u` | 无 | `git stash`；带未提交改动切分支时 grit 的 switch/merge/pull/pick 会拒绝，最稳的做法是 `git stash` → 切分支 → `git stash pop`（改动不冲突时 `git checkout`/`git switch` 也能直接切） |
| `git checkout -- <file>` / `git checkout <commit> -- <file>`（按文件检出） | 无 | `git checkout <commit> -- <file>` / `git restore` |
| `git update-index` / `read-tree` / `symbolic-ref` 等底层索引命令 | 无 | 用 git（grit 不暴露索引级操作） |

## 2. 历史改写

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `git commit --amend`（补写最后一次提交） | 无 | `git commit --amend`（未推送时安全） |
| `git rebase`（含 `-i`、`--onto`、`--autosquash`、`--continue/--abort`） | 无 | 完整交给 git；改写后若已推送需 force push，也要用 git |
| `git revert`（生成反向提交） | 无 | `git revert <commit>` |
| `git cherry-pick` 多提交/区间/`-n`/`--continue` | **部分**：`grit pick` 只支持单个非合并提交，无选项 | 多提交或需要控制时用 `git cherry-pick`；单提交日常优先 `grit pick` |
| `git commit --fixup/--squash` | 无 | git |
| `git filter-repo` / `filter-branch` / `replace`（批量改写） | 无 | git |
| 改写后再同步（需要 force push） | **无**：grit push 永不覆盖远程 | `git push --force-with-lease`（比 `--force` 安全） |

## 3. 合并、冲突与集成

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| **解决合并冲突** | **无**（官方路径就是让你用 git）：merge/pull/pick 冲突时报错 exit 1 且工作区保持原样 | `git merge <branch>` → 编辑冲突文件 → `git add` → `git commit`；回到 grit 继续 |
| `git merge --squash/--no-ff/--ff-only/--no-commit/-m/-s/-X` | 无任何选项 | git |
| `git merge --abort/--continue` | 不需要：grit 失败时不产生半完成状态 | 若用 git 合并到一半想放弃：`git merge --abort` |
| `git mergetool` / `git rerere`（冲突工具与复用） | 无 | git |
| `git pull --rebase/--ff-only/--no-rebase` | 无任何选项（固定 ff 或 merge commit） | git |
| 用 rebase 代替合并来集成 | 无 | git |

## 4. 远程与推送

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| **force push**（`-f`、`--force-with-lease`） | **无**：grit push 永不覆盖远程提交 | `git push --force-with-lease`（推送前确认没有他人的新提交） |
| push refspec、`--all`、`--mirror`、`--delete`、单标签推送、改名推送 | 无：`grit push` 不带参数，只推「当前分支 → 配置的 remote 同名分支」或 `--tags`（全部标签） | git；推送目的地可用 `grit config branch.<name>.remote/merge` 调整，但改名/多分支推送用 git |
| `git push -u/--set-upstream` | 无 upstream 概念：grit 靠 `branch.<name>.remote`/`branch.<name>.merge` 配置；pull/merge 采纳远程分支时会写 upstream（JSON `result: "set_upstream"`） | 用 `grit config` 或 `git push -u` |
| `--dry-run`、`--atomic`、`--no-verify`、`-o/--push-option` | 无 | git |
| `git fetch --all/--prune/refspec/--depth` | 无：`grit fetch [<remote>]` 只支持一个远端、默认 origin；**不会清理**已删除的远程分支 | `git fetch --prune` 清理过期远程跟踪分支 |
| `git remote remove/rename/set-url/get-url/show/prune/update` | 无：只有 list 与 add | git |
| `git ls-remote`（不下载先看远端 refs） | 无 CLI（grit-lib 有网络层 ls-remote） | `git ls-remote <url>` |
| `git submodule`、子模块克隆/更新 | 无 | git |
| `git credential fill/approve/reject` | 无 | git（grit 只通过 `credential.helper` 存取，不自带这些子命令） |

## 5. 检视、搜索与调试

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `git blame` | 无 | git |
| `git grep` | 无 | `git grep` / `rg` |
| `git bisect` | 无 | git |
| `git reflog`（找回误操作） | 无 CLI（grit-lib 有 reflog 读写） | `git reflog`——**误删分支/回退后先查它**，必要时配合 `git fsck`，找到 oid 后用 `git branch <name> <oid>` 恢复 |
| `git describe` | 无 | git |
| `git log` 的筛选与格式：`--all`、`--graph`、`-p/--stat`、`--author/--grep`、`--since/-n`、范围 `A..B`、路径过滤、`--follow` | **无**：`grit log` 固定 10 条一页、只支持 `--before` 翻页 | git（`--json` 里也拿不到范围/筛选，只有 `commits[]`+`next`） |
| `git diff --staged/--cached`、两个提交间/范围 diff、`--stat/--name-only`、路径过滤 | **无**：`grit diff` 只有「全部未提交（暂存+未暂存合并展示）」或「一个提交 vs 第一父」 | `git diff --cached`、`git diff A..B -- <path>`；文件清单可 `grit diff <commit> --json --filter '.files[].path'` |
| `git show` 的 `-p/--stat/--name-only`、查看 blob/tree 内容 | **部分**：`grit show` 只给消息 + 文件增删汇总 | 看改动内容用 `grit diff <commit>`；看对象内容用 `git cat-file` |
| `git rev-parse` / `rev-list` / `merge-base` / `name-rev` | 无 CLI（grit-lib 有 revparse/revwalk/merge base） | git |
| `git cat-file` / `hash-object` / `ls-files` / `ls-tree` / `show-ref` / `for-each-ref` / `count-objects` / `verify-pack` | 无 CLI | git |
| `git range-diff` | 无 | git |
| `git log` 语义的 `git shortlog`（按作者汇总） | **语义不同**：`grit shortlog` 是「相对 target 的领先提交清单」 | 按作者汇总用 `git shortlog -sn` |
| `git check-ignore` / `check-attr` | 无 | git |

## 6. 分支与标签细节

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `git branch -m/-M`（重命名）、`-c/-C`（复制） | 无 | git |
| `git branch -u/--set-upstream-to`、`--unset-upstream` | 无 | `grit config branch.<name>.remote/merge` 或 git |
| `git branch -a/-r`（远端分支列表）、`-v`（详情）、`--merged/--contains`、`--sort/--format` | 无：`grit branch` 只列本地 | git |
| `git switch --detach`、`git checkout <commit>`（游离检出） | 无：grit 只能切分支 | git；注意之后 `grit commit` 会失败（detached），`grit log/diff/status` 仍可用 |
| `git switch -f/--discard-changes`、`--merge`、`--orphan` | 无 | git |
| `git tag -a -m`（附注标签）、给任意提交打标签、`-f`、`-l` 模式、`-v` 校验、单标签推送 | 无：`grit tag` 只在 HEAD 打**轻量标签**，可列表/删除 | git 创建附注标签；`grit push --tags` 会把所有本地标签一起推上去 |
| 删除远端分支/标签 | 无（push 不带 `--delete`） | `git push origin --delete <branch>` |

## 7. 仓库维护与工作区管理

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `git gc` / `prune` / `repack` / `pack-refs` / `maintenance` | 无 CLI | git（grit-lib 有 pack/midx/commit-graph 读写，但未暴露成命令） |
| `git fsck`（完整性校验）、`verify-pack` | 无 CLI（grit-lib 有 fsck） | git |
| `git worktree add/list/remove/lock` | 无 CLI（grit-lib 支持 worktrees） | git |
| `git submodule` | 无 | git |
| `git sparse-checkout`、部分克隆（`--filter`） | 无 | git |
| Git LFS | 不支持（命令面与能力列表都没有 LFS） | 涉及 LFS 的操作（大文件的拉取/推送）用 `git` + git-lfs |
| `git notes` | 无 CLI（grit-lib 有 notes） | git |
| `git bundle create/verify/unbundle` | 无 CLI（grit-lib 有 bundles） | git |
| `git apply`、`git am`（应用补丁） | 无 | git |
| 钩子管理、`--no-verify`、`core.hooksPath` | 无 CLI 选项（grit-lib 有 hooks 层） | git |
| `SHA-256` 对象格式仓库（`init --object-format=sha256`） | 无此选项（`grit init` 面向 SHA-1 仓库） | git |
| `git replace` / 对象命名空间 / alternates 管理 | 无 CLI | git（环境变量级 alternates 读取是支持的） |

## 8. 配置

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `--system` / `--local` / `--worktree` / `--file` / `--blob` 作用域 | 无：只有「仓库级（默认）」与 `--global` | `git config --system/--file …` |
| `--add` / `--replace-all` / `--unset-all`（多值键） | 无：只能设一个值或 `--unset` | git |
| `--get-regexp` / `--get-all` / `--show-origin` / `--show-scope` / `-z` | 无 | git |
| `--type=bool/int/…` 校验、`--edit` | 无 | git |

## 9. 克隆与初始化选项

| Git 能力 | grit | 回退做法 |
| --- | --- | --- |
| `git clone --depth/--shallow-since`（浅克隆）、`--single-branch`、`--branch`、`--bare`、`--mirror`、`--filter`、`-o`、`--no-checkout`、`--recurse-submodules` | 无选项：`grit clone <url> [dir]` | 需要这些参数时用 git 克隆（grit 之后可以正常操作该仓库，包括浅克隆） |
| `git init --initial-branch`、`--template`、`--separate-git-dir`、`--shared`、`--object-format` | 无：默认分支固定 `main`，唯一选项是 `--bare`（文档里的 `--ref-format` 属 main，v0.5.2 无） | git |

## 10. grit 有、但语义更窄或不同

容易误用的地方（不是「没有」，而是「不一样」）：

| 命令 | 差异 |
| --- | --- |
| `grit checkout` / `co` | 是 `switch` 的**别名**：只切分支；不是 git 的文件检出，也不能游离检出 |
| `grit add` | 全量暂存或按路径预暂存；**不能取消暂存、不能交互挑选**（`commit` 会重新全量暂存） |
| `grit commit` | 全量提交；消息必填；无 amend/无钩子选项/无 `--no-verify` |
| `grit diff` | 无 `--staged`、无路径/范围参数 |
| `grit log` | 固定 10 条一页 + `--before`；无筛选、无 `-p`、无范围 |
| `grit shortlog` | 「相对 target 的领先清单」，不是 git 的按作者汇总 |
| `grit branch` | 只有 列出/创建/删除；无重命名、无 upstream、无远端分支 |
| `grit merge` / `grit pull` | 无任何选项；冲突不解决 |
| `grit push` | 无参数、无 force、无 refspec；目标由 `branch.<name>.remote/merge` 决定 |
| `grit tag` | 只有轻量标签且只能指向当前 HEAD |
| `grit config` | 读/写/列/删，仅仓库级与 `--global` |
| `grit status` | 无选项，但 `--json` 字段完整（`staged`/`unstaged`/`untracked`…） |

## 11. 只在 grit-lib（CLI 未暴露）

以下能力库里有 API，但**没有** grit 命令，脚本/程序可考虑用库（见 [grit-lib.md](grit-lib.md)），否则用 git：

stash（读写）、reflog（读写）、notes、bundle、fsck、worktrees、hooks、patch-id、多 pack / multi-pack-index / commit-graph、reftable 引用后端、pack 与协议底层（upload-pack/receive-pack 是隐藏命令）、revparse/rev-list/merge-base、ls-remote。

## 12. 永久移除（不会回归，直接用 git）

Grit 项目在 `AGENTS.md` 的「What we drop」里明确这些**不做、也不再做**：

- `archive`；
- 邮件工作流：`am`、`format-patch`、`send-email`、`imap-send`、`request-pull`；
- 外部 VCS 桥（`svn`、`hg`、`p4` 之类）；
- `daemon`、`instaweb` 及其它外围工具；
- 另一个 Git 兼容 CLI（`grit-git` 已删除）——不要期待 grit 增加「和 git 一样的子命令」。

## 回退 git 时的注意

- **可以自由混用**：grit 与 git 操作同一仓库（同索引、同对象库、同配置、同 refs），git 改完 grit 立即反映；反之亦然。
- **grit 更保守**：有未提交改动时 grit 的 `switch`/`merge`/`pull`/`pick` 会拒绝，而 git 允许——带改动切分支最稳的是 `git stash` → 切换 → `git stash pop`（改动与目标分支不冲突时，`git checkout`/`git switch` 也能直接切）。
- **恢复误操作先看 `git reflog`**：`grit branch -D`、`git reset --hard` 之后都可能还能找回。
- **冲突的标准闭环**：grit 报冲突（工作区未变）→ `git merge <branch>` → 解决 → `git add` + `git commit`（或用 `git merge --continue`）→ 继续用 grit 推送。
- **改写历史后**：本地用 git 完成后，同步需要 `git push --force-with-lease`；grit 侧不需要任何补偿。

来源：命令覆盖以 <https://grit-scm.com/docs/> 索引与 v0.5.2 实测为准；「永久移除」与库能力边界见仓库 <https://github.com/gitbutlerapp/grit/blob/main/AGENTS.md>。
