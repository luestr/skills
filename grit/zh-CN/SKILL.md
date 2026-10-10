---
name: Grit
description: "用 Grit 命令行（grit-scm.com，Rust 重写的现代 Git 客户端）完成仓库检视、提交、分支、合并、cherry-pick、远程同步与打标签，并给出脚本/Agent 所需的 --json/--filter 契约；同时完整列出 Git 有而 Grit 没有的能力与回退方案。支持的 Grit 版本：0.5.x（以 v0.5.2 实测校准；不同补丁版本的命令面可能有差异，以本机 grit --help 为准）。当任务涉及版本控制（status、提交、建分支、切分支、合并、推送、拉取、标签、diff、历史查看）时，只要环境中可能存在 grit，就先查阅本技能；尤其在做「部分提交、取消暂存、改写历史、force push、解决冲突」这类 Grit 刻意不做的事情之前，务必先读 references/git-gaps.md 选择正确的工具。"
---

# Grit 使用技能

Grit 是 Git 的 Rust 实现，由两部分组成：**`grit`**（现代精简 CLI）与 **`grit-lib`**（可链接的 Rust 库）。
它与 Git 共享磁盘格式、wire protocol 和配置文件（`~/.gitconfig`、`.git/config`），但命令集是**刻意精简的子集**：
每个常见动作只有一条明显路径，argv 与消息不追求与 Git 一致。

**支持版本：0.5.x。** 本文以 **v0.5.2** 实测校准；不同补丁版本的命令面可能有差异，以本机 `grit --help` 为准。
动手前先确认环境：`grit --version`。在线文档（grit-scm.com/docs）跟踪 main 分支，可能描述尚未发布的命令（见「版本差异」）。

## 六条铁律（实测确认，最常踩的坑）

1. **全量提交，没有部分提交。** `grit commit` 每次都会把工作区里全部改动（含修改、删除、未跟踪文件）提交进去；`grit add <path>` 只是预暂存/预览，随后 `grit commit` 依然全量暂存。想只提交一部分文件，必须用 `git`（见 [references/git-gaps.md](references/git-gaps.md)）。
2. **提交消息必填，且没有编辑器。** 用 `grit commit "消息"` 或 `-m "消息"`；漏掉消息时它会先暂存改动再报错。HEAD 游离（detached）时 `grit commit` 直接失败（`HEAD is detached; grit commit needs a branch`）。
3. **有未提交改动时，切分支/合并/拉取/cherry-pick 一律拒绝。** `switch`、`merge`、`pull`、`pick` 遇到任何未提交改动（含未跟踪文件冲突）都会以 exit 1 停止。要切分支就先提交，包括把 WIP 落成提交——grit 没有 `stash`。
4. **冲突不自动解决。** `merge`/`pull`/`pick` 检测到冲突时报错、exit 1，并保持分支与工作区**完全原样**（不是半完成状态）；官方路径是改用 `git merge <branch>` 解决后提交。恢复现场不需要 `--abort`——本来就没动。
5. **机器读取一律 `--json`。** 此时 stdout 恰好一个 JSON 值，失败时是 `{"error": "..."}` 且退出码非 0；stderr 只放进度与人类提示。`--filter`（jq 风格表达式）必须与 `--json` 搭配，多结果会包成一个数组。退出码：`0` 成功、`1` 命令失败、`2` 用法错误（此时没有 JSON 错误对象）。
6. **缺失能力回退 `git` 是设计内用法。** git 与 grit 可以自由地操作同一个仓库（同索引、同对象库、同配置），git 改完 grit 立即看得到。不要试图用 grit 硬做 reset/rebase/force push——先查 [references/git-gaps.md](references/git-gaps.md)。

## 版本差异：文档 ≠ v0.5.2 二进制

- **v0.5.2 实际可用**：`init` `clone` `remote` `log` `diff` `show` `status` `shortlog` `add` `commit` `branch` `switch` `merge` `pick` `fetch` `pull` `push` `tag` `auth` `update` `config` `manager`，以及隐藏的 `upload-pack`、`receive-pack`；全局选项 `--json`、`--filter`、`-h`、`-V`。
- **别名**：`status`=`st`，`shortlog`=`sl`，`switch`=`co`=`checkout`（`grit checkout` 只切分支，不是 git 的文件检出/游离检出）。
- **文档里有、v0.5.2 没有**（属未发布的 main）：`grit skill`、`grit completions`、全局 `--markdown`、`grit init --ref-format`（reftable）。调用会得到 `unrecognized subcommand` 或 `unexpected argument`（exit 2）。需要它们时先 `grit --help` 确认。
- **文档描述、但 v0.5.2 未生效**（实测）：`commit.gpgsign` 签名（提交照常成功且不含签名）；从浅克隆源 `grit clone`（报 `object not found`）。这两项请按 v0.5.2 实际行为处理。

## 任务速查表

| 任务 | 命令 |
| --- | --- |
| 看当前状态（默认命令） | `grit` / `grit status` / `grit st` |
| 初始化 / 克隆 | `grit init [--bare] [path]`；`grit clone <url> [dir]` |
| 提交全部改动 | `grit commit "消息"`（`-am` 兼容 git 习惯，效果相同） |
| 查看未提交 diff / 某个提交的 diff | `grit diff`；`grit diff <commit>`（无 `--staged`、无路径过滤） |
| 历史（10 条一页） | `grit log`；翻页 `grit log --before=<oid>` |
| 本分支领先目标的提交 | `grit shortlog` / `grit sl` |
| 看提交/分支/标签详情 | `grit show [object]` |
| 建/切分支 | `grit switch -c feature`；`grit switch main`；`grit branch <name>`（只建不切） |
| 合并 | `grit merge <branch>`（也接受 `origin/main`） |
| 复制单个提交 | `grit pick <commit>`（单提交 cherry-pick） |
| 远程 | `grit remote add origin <url>`；`grit fetch [remote]`；`grit pull`；`grit push`；`grit push --tags` |
| 标签（轻量、指向 HEAD） | `grit tag v0.1`；`grit tag -d v0.1` |
| GitHub 登录（HTTPS） | `grit auth`；登出 `grit auth logout` |
| 配置（与 git 同一份文件） | `grit config [--global] <key> [value]`；`--list`；`--unset <key>` |

## 参考资料索引（按需读取，避免一次加载全部）

| 文件 | 内容 | 何时读取 |
| --- | --- | --- |
| [references/commands.md](references/commands.md) | 每个命令的语法、关键选项、行为边界与 JSON 字段速查 | 不确定某命令怎么用或输出什么字段时 |
| [references/automation.md](references/automation.md) | `--json`/`--filter` 契约、退出码、非交互清单、凭据、可用环境变量、JSON 配方 | 写脚本/自动化、无人值守运行、排查阻塞与认证时 |
| [references/git-gaps.md](references/git-gaps.md) | Git 有而 Grit 没有的能力全清单（9 类缺失 + 语义更窄、仅库限定、永久移除三类对照）+ 回退命令 | 任务涉及部分提交、取消暂存、历史改写、force push、冲突解决、blame/rebase/stash 等时**必读** |
| [references/workflows.md](references/workflows.md) | 任务型配方：首次推送、日常循环、同步、合并、cherry-pick、发版、冲突收尾、回退 git、自动化循环 | 执行端到端任务时直接照抄命令 |
| [references/grit-lib.md](references/grit-lib.md) | 在 Rust 程序里嵌入 grit-lib 的用法与模块地图 | 任务是用 Rust 程序化访问 Git 仓库时 |

## 最小闭环（最常用的五步）

```console
$ grit --version                      # 确认可用；不可用则改用 git
$ grit                                # 看状态：分支、领先目标多少、改动、下一步提示
$ grit commit "Add the greeting"      # 提交全部改动（消息必填）
$ grit push                           # 推送当前分支到 origin 同名分支
$ grit pull                           # 推送被拒时先拉取（ff 或生成 Merge 提交）
```

详细配方与异常处理见 [references/workflows.md](references/workflows.md)。
