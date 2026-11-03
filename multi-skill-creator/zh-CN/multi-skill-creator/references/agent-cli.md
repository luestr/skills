# Agent CLI 适配层

`scripts/agent_cli.py` 是技能里唯一直接跟外部 agent 打交道的部分。它把两件事抽象成数据：

- **补全**：给一段长 prompt，要一段文本回来。用于根据评测失败重写技能描述。
- **触发探针**：在一个装了某技能的工程里跑一条用户查询，看 agent 到底有没有加载那个技能。

上游版本把这两件事都硬绑在 `claude -p` 上。这一版改成可配置，所以换成任何 CLI 都不用改技能内容。

## 选择 agent

解析顺序：

1. `--agent-cmd "<命令模板>"`，或环境变量 `SKILL_CREATOR_AGENT_CMD`
2. `--agent <预设名>`
3. 不给参数时，按顺序在 PATH 上找第一个可用的预设（等同 `--agent auto`）

都找不到时会抛出 `AgentUnavailable`，并打印可操作的提示，而不是抛一个看不懂的子进程错误。

命令模板里可以放两个占位符：

| 占位符 | 含义 |
|---|---|
| `{prompt}` | 用户 prompt 的插入位置。模板里没有它时，prompt 作为最后一个参数追加 |
| `{model}` | 模型名。没有传 `--model` 时，单独的 `{model}` 参数会被整段丢掉 |

```bash
# 模板里带占位符
--agent-cmd "my-agent --print {prompt}"
# prompt 走 stdin
--agent-cmd "my-agent --print" --agent-transport stdin
# 带模型
--agent-cmd "my-agent --print {prompt} --model {model}" --model fast-1
```

Windows 上含空格的路径不用特殊处理，引号会被正确剥掉：

```powershell
--agent-cmd 'python "C:\tools\my agent.py"'
```

## 内置预设

| 预设 | 可执行文件 | 探针事件流 | 技能安装位置 |
|---|---|---|---|
| `claude` | `claude` | JSON 流事件 | `.claude/skills/`、`.claude/commands/` |
| `codex` | `codex` | 纯文本 | `.agents/skills/` |
| `gemini` | `gemini` | 纯文本 | `.gemini/skills/` |
| `cursor-agent` | `cursor-agent` | 纯文本 | `.cursor/skills/`、`.agents/skills/` |
| `opencode` | `opencode` | 纯文本 | `.opencode/skills/` |
| `finch` | `finch` | 纯文本 | `.finch/skills/`、`.claude/skills/` |

预设只是起点，不是真理：CLI 的开关会随版本变。不一致时用 `--install-root`、`--agent-cmd` 覆盖，或者直接改 `PRESETS` 里对应的条目。每个预设都在代码里有注释说明它的假设。

## 探针是怎么工作的

1. 在工程根目录下，把一段很小的技能内容写到该 CLI 会去扫描的目录里：
   - `skill_md` 形式：`<dir>/<技能名>-probe-<随机串>/SKILL.md`
   - `command_md` 形式：`<dir>/<技能名>-probe-<随机串>.md`
   - 内容里带一个随机令牌 `PROBE-TOKEN-<hex>`。关键点：这个令牌**不出现在技能名里**，只出现在文件正文里。技能名是 agent 在技能清单里能直接看到的，正文则必须真的去读才拿得到。早先的版本拿技能名前缀当搜索串，于是"回答里提到了技能名"就被判为触发——而很多 CLI 在拒绝使用某个技能时会顺口列出它的名字，这会系统性地高估触发率
2. 把用户的查询交给 agent
3. 判断是否触发
4. 删掉探针文件（以及探针自己建的空目录）

**判断方式因 CLI 而异，这里必须诚实说明：**

- **结构化输出**（`claude`，以及任何输出 JSON 事件流的 CLI）：看第一个工具调用。如果它在读技能、且载荷里出现了那个令牌，算触发；如果第一个工具调用是别的东西，算没触发。这个判断比较可靠，而且是逐行流式判定的：CLI 一输出就能返回，不必等进程结束
- **纯文本输出**（其余预设）：用文本启发式——回答里必须出现那个随机令牌才算触发。令牌只存在于探针技能正文里，所以出现基本说明它确实读过，也不会被"提到了技能名"骗过。但这个证据仍比事件流弱：如果 CLI 会把技能目录的内容一股脑塞进上下文，就可能误判为触发

所以对纯文本 CLI，触发评测的分数应当理解为**上界**，用它做相对比较（这一版描述比那一版好）比用它做绝对判断更靠谱。真要精确评估触发，用支持事件流的 CLI。

如果探针装不进任何目录（工程目录只读、沙箱限制），脚本会明确报错而不是静默返回"未触发"——静默返回会把所有查询都判成没触发，分数全错。

## 工程根目录怎么定

探针必须装进 CLI 认定为本工程的那个根目录。`find_project_root()` 从当前目录往上找，遇到下面任一标记就认定是根：`.claude`、`.finch`、`.agents`、`.gemini`、`.cursor`、`.opencode`、`.git`。都没有就用当前目录。

判断不对时用 `--project-root` 直接指定。

## 装不进已知目录怎么办

CLI 的技能目录不在上面的表里，或者你用的是自建 agent：

```bash
python -m scripts.run_eval ... --install-root .myagent/skills
```

`--install-root` 可以重复多次，会覆盖预设里的猜测。指定的路径都相对于工程根目录。

## 嵌套调用

在某个 CLI 会话内部再非交互调用 CLI，有几个工具会因为检测到嵌套而拒绝运行。适配层在启动子进程前会剥掉这些环境变量：`CLAUDECODE`、`CLAUDE_CODE_ENTRYPOINT`、`CODEX_SANDBOX`、`GEMINI_CLI`。对不存在的变量是空操作。

## 与各脚本的对应关系

| 脚本 | 用到适配层的地方 |
|---|---|
| `run_eval.py` | 触发探针 |
| `improve_description.py` | 补全（重写描述） |
| `run_loop.py` | 两者都要 |
| `aggregate_benchmark.py` / `generate_report.py` / `package_skill.py` | 不用；纯本地计算与打包 |

`run_eval.py`、`improve_description.py`、`run_loop.py` 共用同一组参数（`--agent`、`--agent-cmd`、`--agent-transport`、`--install-root`、`--agent-model-flag`），定义在 `run_eval.add_agent_arguments()` 里，避免三个脚本的参数各自漂移。

## 模型怎么传给自定义 CLI

自定义模板默认**不会**被追加 `--model`：不认识的 CLI 很可能没有这个开关，猜错就会让本来能跑的命令因为参数错误而失败。两条路可选：

```bash
# 1) 在模板里自己安排位置（推荐）
--agent-cmd "my-agent --print {prompt} --model {model}" --model fast-1

# 2) 声明该 CLI 用哪个开关，由脚本追加
--agent-cmd "my-agent --print {prompt}" --agent-model-flag --model --model fast-1
```

两种方式都不会重复：模板里已经有 `{model}` 时，`build_command()` 不会再追加一遍。
