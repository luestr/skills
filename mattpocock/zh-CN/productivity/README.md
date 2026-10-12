# 生产力

通用工作流工具，与具体代码无关。

## 用户手动调用

只有你手动输入时才能调用（Claude Code：`disable-model-invocation: true`；Codex：在 `agents/openai.yaml` 中设置 `policy.allow_implicit_invocation: false`）。

- **[grill-me](./grill-me/SKILL.md)**：就一份计划或设计接受不留情面的访谈，直到设计树的每个分支都已解决。
- **[handoff](./handoff/SKILL.md)**：把当前对话压缩成一份交接文档，供另一个 Agent 接手工作。
- **[teach](./teach/SKILL.md)**：跨多个会话教用户一项新技能或概念，把当前目录当作有状态的教学工作区。
- **[to-questionnaire](./to-questionnaire/SKILL.md)**：把你无法独自回答的决策变成一份 Markdown 问卷，交给唯一能回答的那个人（异步填写，或借一次会议一起填）。
- **[wait-what](./wait-what/SKILL.md)**：某条消息一没听懂就立刻触发它。Agent 会带着你缺失的上下文，用平实、简明的中文重新讲一遍，并使用你 `GLOSSARY.md` 里的词汇。

## 模型自动调用

模型或用户都能调用（触发措辞丰富，好让模型主动取用）。

- **[grilling](./grilling/SKILL.md)**：就一份计划、决策或想法不留情面地访谈用户，直到设计树的每个分支都已解决。
- **[writing-for-agents](./writing-for-agents/SKILL.md)**：为 Agent 撰写文档：技能、AGENTS.md/CLAUDE.md，以及 Agent 经由指针触达的任何文档。
