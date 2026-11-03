# 自动化与脚本化（v0.5.x）

面向程序与自主 Agent 驱动 `grit` 的共享契约：JSON 输出、退出码、非交互要求、凭据与文档资源。
逐命令的 JSON 字段见 [commands.md](commands.md) 与各命令 `--help`。

## JSON 契约

给机器读的结果一律加 `--json`：

- **stdout**：恰好**一个** JSON 值——成功是命令的结果对象，失败是 `{"error": "…"}`。
- **stderr**：进度行、认证提示、人类风格 `error: …` 诊断。解析只看 stdout。
- 失败时退出码非 0；可以按退出码判断，也可以按是否存在 `error` 键判断。

```console
$ grit commit --json
{"error":"provide a commit message, e.g. grit commit \"what changed\""}
```

`--filter <EXPR>` 用 jq 风格表达式就地裁剪 JSON（需 `--json`）。表达式按 jq 规则书写：裸字段名简写只适用于顶层，嵌套要写显式键：

```console
$ grit status --json --filter '{branch, clean}'
$ grit status --json --filter '{b: .branch, c: .clean}'    # 显式键也支持
$ grit log --json --filter '.commits[].subject'            # 多结果 → 一个 JSON 数组
$ grit log --json --filter '.commits | length'
```

- 失败时过滤器作用在 `{"error": "…"}` 上，因此**错误信息会被过滤结果顶掉**：无消息时 `grit commit --json --filter .oid` 的 stdout 是 `null`（exit 1），而不是错误对象。用 `--filter` 时请以**退出码**判断成败；需要错误原文就别加 `--filter`。
- **表达式非法**同样输出 `{"error": "invalid filter …"}`（exit 1）——这是 `--filter` 下少数仍能看到 `error` 键的失败情形。
- 路径不存在可得到 `null`（仍 exit 0）。

只要有任何 ref 被拒绝，`grit push` 会打印完整 JSON 结果，但退出码仍是 **1**（`rejected: true`）——不加 `--filter` 时看 `rejected` 字段，加了 `--filter` 时以退出码为准。

## 退出码

| 码 | 含义 |
| --- | --- |
| 0 | 成功（包括某些 jq 路径缺失得到 `null` 的情况） |
| 1 | 命令失败（无仓库、push 被拒、校验错误等）；有 `--json` 时 stdout 仍有 `{"error": "…"}` |
| 2 | 用法错误（未知选项/子命令）。clap 把帮助打到 stderr，**stdout 没有 JSON** |

```console
$ grit status --filter '.branch'   # 忘记 --json
error: --filter requires --json    # exit 1
```

## 颜色与终端检测

人类输出只在「stdout 是 TTY + 环境支持 ANSI + `NO_COLOR` 未设置」时着色；管道/重定向自动变纯文本。
`NO_COLOR=1` 可强制纯文本。JSON 模式与颜色无关，机器交互永远用 `--json`。

## 保持非交互

`grit` **不打开外部编辑器**：`grit commit` 必须带消息（位置参数或 `-m`），没有 `$GIT_EDITOR` 路径。也没有全局 `--yes`。

可能**阻塞在人上**的流程与规避：

| 场景 | 行为 | 规避 |
| --- | --- | --- |
| `grit auth` | OAuth device flow：stderr 给网址与短码，轮询直到浏览器里授权 | 自动化前先在交互会话跑一次 `grit auth`，token 存进 `credential.helper` |
| `grit fetch`/`push`/`pull`（HTTPS GitHub） | 认证失败且 **stdin 是 TTY** 时可能询问 `Sign in to GitHub now? [Y/n]` 并启动 device flow | 用已存 token；或保证 stdin 不是 TTY（会打印提示直接退出，不提问） |
| `clone`/`fetch`/`pull`/`push` 走 SSH | grit 以管道连接 ssh 的协议 stdin/stdout，但**继承 stderr**，ssh 子进程仍可能与 `/dev/tty` 交互（host key 确认、口令、ssh-askpass）；`--json` 不关掉它 | 预置密钥与 known_hosts；无人值守设 `GIT_SSH_COMMAND='ssh -o BatchMode=yes'`，让 SSH 快速失败而不是提问。grit 解析 SSH 的顺序是 `GIT_SSH_COMMAND` → `GIT_SSH` → `PATH` 里的 `ssh`（**不读** `core.sshCommand`） |
| `grit update` | 直接跑发布安装脚本（Unix `curl \| sh`） | 无人值守不要调用，除非就是要升级二进制 |

`grit auth logout` 是非交互的，报告 helper 里是否有 token 被删除：

```console
$ grit auth logout --json
{"logged_out": false, "host": "github.com"}
```

## 凭据（HTTPS GitHub）

- `grit auth` 走 GitHub device flow，token 通过配置的 `credential.helper` 存储（与 Git 同一机制）。
- OAuth app 可用 `GRIT_GITHUB_CLIENT_ID` 环境变量或 `grit config --global grit.githubClientId …` 覆盖。
- 无 helper 时无法存储：Windows 内置 `grit manager`；macOS/Linux 需先 `grit config --global credential.helper osxkeychain|libsecret|store`。
- SSH 远端不用 device-flow token，认证完全交给 ssh（注意上面的阻塞风险）。

## 不可 JSON 化的命令

`grit manager`、`grit upload-pack`、`grit receive-pack` 是协议命令（stdin/stdout 二进制或行协议），**没有 `--json`**，不要把它们包成 JSON 命令。
`-V`/`--version` 即使加 `--json` 也只打印版本行（如 `grit 0.5.2`），不产生 JSON 值。

## 常用环境变量（节选）

| 变量 | 作用 |
| --- | --- |
| `GIT_DIR`、`GIT_WORK_TREE`、`GIT_CEILING_DIRECTORIES`、`GIT_PREFIX` | 仓库发现 |
| `GIT_INDEX_FILE`、`GIT_OBJECT_DIRECTORY`、`GIT_ALTERNATE_OBJECT_DIRECTORIES` | 索引与对象库路径 |
| `GIT_CONFIG`、`GIT_CONFIG_GLOBAL`、`GIT_CONFIG_SYSTEM`、`GIT_CONFIG_NOSYSTEM`、`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`/`GIT_CONFIG_PARAMETERS` | 配置级联（可用 `GIT_CONFIG_NOSYSTEM=1` 跳过损坏的系统配置） |
| `HOME`、`XDG_CONFIG_HOME`、`USERPROFILE` | 主目录与身份回退 |
| `GIT_AUTHOR_*`、`GIT_COMMITTER_*` | 新对象的作者/提交者姓名、邮箱、**时间**覆盖（可做确定性提交） |
| `GIT_SSH`、`GIT_SSH_COMMAND` | SSH 传输命令 |
| `GIT_HTTP_LOW_SPEED_LIMIT`、`GIT_HTTP_LOW_SPEED_TIME` | HTTP 低速中止阈值 |
| `TZ` | 无显式偏移时的本地时区 |
| `NO_COLOR` | 强制纯文本输出 |

## JSON 配方

```console
# 工作区是否干净
$ grit status --json --filter .clean                          # true / false

# 当前分支与领先数
$ grit status --json --filter '{branch, ahead, target}'
$ grit shortlog --json --filter .ahead

# 最近提交主题
$ grit log --json --filter '.commits[].subject'
$ grit show HEAD~1 --json --filter .commit.subject

# 某提交改了哪些文件
$ grit diff HEAD~1 --json --filter '.files[].path'

# 分支清单
$ grit branch --json --filter '{action, current, branches}'
$ grit branch --json --filter '.branches[].name'

# 远程
$ grit remote --json --filter '.remotes[].name'

# 推送结果判断（注意 exit 也可能是 1）
$ grit push --json --filter '{rejected, results}'
```

无 `--json` 时的等价人类输出：`grit` 的状态屏、`grit log` 的十行分页、`grit diff` 的 `-`/`+` 标记——脚本不要解析这些，直接上 JSON。

## 给 Agent 的文档资源

| 资源 | 位置 | 用途 |
| --- | --- | --- |
| llms.txt | <https://grit-scm.com/llms.txt> | 全部文档页的策展索引 |
| llms-full.txt | <https://grit-scm.com/llms-full.txt> | 所有文档 Markdown 全文 |
| Markdown 孪生页 | 把 HTML 页的 `index.html` 换成 `index.md` | 单页原文，适合精读某命令 |
| `grit skill` | 内置 SKILL.md | **仅 main，v0.5.2 无**；升级后再用，且它自带版本号 |
| grit-lib API | <https://docs.rs/grit-lib> | Rust 库参考 |

## JSON 输出的稳定性

命令页把字段作为契约记录；用 `--json` 时优先依赖**文档化的顶层字段**（如 `branch`、`clean`、`rejected`），
不要依赖人类文本的措辞（会随版本变化），也不要依赖未在文档中出现的嵌套键。
