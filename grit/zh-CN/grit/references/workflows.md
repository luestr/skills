# 任务配方（v0.5.x）

每个配方都是可直接执行的命令序列，含预期输出与失败分支。
共同前提：已确认 `grit --version` 可用；作者身份已设置（`grit config --global user.name/user.email`，与 git 共用）。

## 1. 全新项目 → 首次推送

```console
$ grit init project && cd project
$ grit config --global user.name "Ada Lovelace"     # 只需一次，git 也共用
$ grit config --global user.email ada@example.com
$ echo "# Notes" > README.md
$ grit commit "Start the project"                   # 全量提交，未跟踪文件一起进
$ grit remote add origin https://github.com/<user>/<repo>.git
$ grit push                                         # 创建远端分支并推送
```

私有仓库 HTTPS 先 `grit auth`；SSH 远端用 `git@github.com:<user>/<repo>.git`，认证走 ssh。

## 2. 日常循环（在已有仓库里干活）

```console
$ grit st                            # 1. 看状态：分支、ahead、改动、下一步提示
$ grit switch -c feature/login       # 2. 建分支并切换（有未提交改动会拒绝——先 commit）
$ ...编辑文件...
$ grit diff                          # 3. 看未提交改动全文
$ grit commit "Add login form"       # 4. 全量提交
$ grit push                          # 5. 推送到 origin 同名分支
$ grit show                          # 6. 复看最后一次提交的消息与改动汇总
```

## 3. 同步远程（推送被拒的标准流程）

```console
$ grit push
  rejected origin refs/heads/main: not a fast-forward — run `grit pull` first
$ grit pull                          # ff 或生成 Merge 提交
$ grit push
```

要点：

- 推送前想先看差异：`grit fetch` 后 `grit status --json --filter '{branch, ahead, target}'` 与 `grit diff origin/main`。
- `pull` 报冲突时：**它什么都没改**。按配方 7 用 git 收尾。
- 分支推送到别处（非 origin/非同名）：`grit config branch.main.remote upstream`、`grit config branch.main.merge refs/heads/main`。

## 4. 合并分支（含清理）

```console
$ grit switch main
$ grit merge feature                 # 三种输出：Fast-forwarded feature → <oid> / Merged feature into the current branch (<oid>) / Already up to date
$ grit branch -d feature             # 已合并则删除；(was <oid>) 会显示出来
$ grit shortlog                      # 确认当前分支相对 target 的领先提交
```

`-d` 提示 `not fully merged` 但你确定要删：`grit branch -D feature`（误删后先查 `git reflog` / `git fsck` 尝试找回）。

## 5. 复制单个提交（cherry-pick）

```console
$ grit log --json --filter '.commits[].subject'      # 先找到目标
$ grit pick 9a1c2e0                                  # 或 grit pick feature（取该分支尖端）
$ grit show --json --filter '{subject: .commit.subject, author: .commit.author}'
```

`grit pick` 会保留原作者与消息；目标已是合并提交、改动已存在或有冲突时会拒绝且不改动任何东西——后两种按配方 7 处理。

## 6. 发布与打标签

```console
$ grit tag v0.2                      # 轻量标签，指向当前 HEAD
$ grit push --tags                   # 推送全部本地标签（不是只推 v0.2）
$ grit tag                           # 核对标签列表
```

需要附注标签（`-a -m`）或给历史提交打标签：用 `git tag`，之后 `grit push --tags` 照样能推上去。

## 7. 冲突：grit 拒绝 → git 收尾 → 回到 grit

```console
$ grit merge topic
error: merge has conflicts in:
  README.md

Nothing was changed. grit can't resolve conflicts yet — run `git merge topic` to resolve them.

$ git merge topic                    # 在干净的工作区上重新执行
$ ...编辑冲突文件...
$ git add README.md
$ git commit                         # 或 git merge --continue
$ grit st                            # 一切照旧；继续 grit 流程
```

为什么安全：grit 检测到冲突时**分支与工作区保持原样**，所以 `git merge` 不会遇到半完成状态；`pull`、`pick` 同理。

## 8. 需要部分提交 / 取消暂存 / WIP 切分支（git 回退）

grit 全量提交，所以这些必须用 git，且用完后 grit 能立即看到结果：

```console
# 只提交一部分文件
$ git add src/login.rs && git commit -m "login only"

# 提交错文件后取消暂存
$ git restore --staged src/other.rs

# 把改动撤出工作区
$ git restore src/scratch.rs

# 带未提交改动切分支（grit switch 会拒绝）
$ git stash push -u -m wip
$ grit switch main                   # 或 git switch
$ git stash pop
```

## 9. 需要 force push 或改写历史（git 回退）

```console
$ git commit --amend                 # 补最后一次提交
$ git rebase -i origin/main          # 或任何 rebase/ revert/ filter-repo 场景
$ git push --force-with-lease        # grit push 永不覆盖远程，必须用 git
```

`--force-with-lease` 优于 `--force`：远端有他人新提交时会拒绝，避免覆盖别人的工作。

## 10. Agent 自动化循环（非交互、可判定）

```console
# 0. 一次性准备（交互会话里做完）：grit auth；确认 credential.helper
# 1. 自检
$ grit --version
$ grit status --json --filter '{branch, clean, detached}'

# 2. 有改动就提交（消息必填；如需确定性时间戳，设 GIT_AUTHOR_DATE/GIT_COMMITTER_DATE）
$ grit status --json --filter .clean
$ grit commit "Automated change: <what>" --json --filter .oid

# 3. 推送并处理拒绝（exit 1 + rejected=true）
$ grit push --json --filter '{rejected, results}'
$ grit pull                                   # 被拒就拉取合并；冲突则转人工/git
$ grit push

# 4. 无人值守防护（SSH 远端；PowerShell 写法，Bash 用 export）
PS> $env:GIT_SSH_COMMAND = "ssh -o BatchMode=yes"
```

判定规则用 JSON 字段而不是人类文本；不要把 `grit manager`/`upload-pack`/`receive-pack` 当 JSON 命令。
细节（阻塞点清单、退出码、凭据）见 [automation.md](automation.md)。

## 11. 快速检视组合拳

```console
$ grit                                  # 我在哪、领先多少、有什么改动
$ grit shortlog                         # 相对 target 的完整领先清单
$ grit diff                             # 未提交改动全文
$ grit diff HEAD~1                      # 上一提交改了什么
$ grit log                              # 最近 10 条；按提示 --before 翻页
$ grit log --json --filter '.commits[].subject'
$ grit show v0.1                        # 看标签指向的提交
$ grit diff v0.1 --json --filter '.files[].path'   # 该提交的文件清单
```

历史很长时注意：`grit log` 每页固定 10 条，脚本批量取历史用 `--before` 循环，或改用 `git log`。
