---
name: claude-handoff
description: 把当前对话交接（hand off）给一个全新的后台 Agent，让它立刻接手工作。
argument-hint: "下一次会话将用来做什么？"
disable-model-invocation: true
---

为当前对话写一份交接摘要，好让一个全新的 Agent 能继续这项工作。把它保存到用户操作系统的临时目录，然后启动一个后台 Agent，把摘要作为提示词交给它：`claude --bg --name "<descriptive name>" -- "$(cat <summary file>)"`。以文件形式传入可以避免 shell 执行摘要中的反引号或展开 `$`。它从当前工作目录启动并立即返回；用户用 `claude agents` 管理它。

始终带上 `-n`/`--name` 并给出描述性的名称（例如 `--name "Fix login bug"`）；它决定任务列表、会话选择器和终端标题中显示的名称。

摘要中要包含“建议技能”一节，写明下一个 Agent 应当为哪些技能调用 Skill 工具。

不要重复其他产物（规格、计划、ADR、issue、提交、diff）中已经记录的内容。改用路径或 URL 引用它们。

隐去任何敏感信息，例如 API 密钥、密码或个人身份信息，因为摘要会成为 Agent 的提示词。

如果用户传入了参数，把它们视为对下一次会话重点的描述，并据此调整摘要。
