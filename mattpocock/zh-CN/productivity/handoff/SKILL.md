---
name: handoff
description: 把当前对话压缩成一份交接文档，供另一个 Agent 接手。
argument-hint: "下一次会话将用来做什么？"
disable-model-invocation: true
---

写一份交接文档，概述当前对话，让一个全新的 Agent 能接着做下去。保存到用户操作系统的临时目录（`$TMPDIR`，没有则 `/tmp`；Windows 上是 `%TEMP%`）——不要存到当前工作区。

文档里要包含一个“建议技能”小节，写明下一个 Agent 应当把哪些技能传给 Skill 工具调用。

不要重复其他产物（规格说明、计划、ADR、issue、提交、diff）里已经记录的内容，改用路径或 URL 引用它们。

隐去任何敏感信息，例如 API 密钥、密码或个人身份信息。

如果用户传了参数，就把它们当作对下一次会话重点的描述，并据此裁剪文档。
