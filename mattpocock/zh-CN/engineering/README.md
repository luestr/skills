# 工程

我每天做代码工作时都会用的技能。

## 用户手动调用

只有你手动输入时才能调用（Claude Code：`disable-model-invocation: true`；Codex：在 `agents/openai.yaml` 中设置 `policy.allow_implicit_invocation: false`）。

- **[ask-matt](./ask-matt/SKILL.md)**：问哪种技能或流程适合你的处境。本仓库各项用户手动调用技能之上的路由。
- **[grill-with-docs](./grill-with-docs/SKILL.md)**：拷问式访谈，同时顺带构建项目的领域模型，打磨术语，并就地更新 `GLOSSARY.md` 和 ADR。
- **[triage](./triage/SKILL.md)**：让 issue 依次经过一套由分诊角色组成的状态机。
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)**：扫描代码库寻找深化机会，把它们做成可视化 HTML 报告呈现出来，然后对你选中的那一个展开拷问。
- **[setup-matt-pocock-skills](./setup-matt-pocock-skills/SKILL.md)**：为本仓库配置各项工程技能所需的设置（issue 跟踪器、分诊标签、领域文档布局）。每个仓库运行一次。
- **[to-spec](./to-spec/SKILL.md)**：把当前对话变成一份规格说明，并发布到 issue 跟踪器。
- **[to-tickets](./to-tickets/SKILL.md)**：把任何计划、规格说明或对话拆成一组曳光弹工单，每个工单都声明自己的阻塞关系——无论是以文本形式写在本地文件里，还是作为真实跟踪器上的原生阻塞链接。
- **[implement](./implement/SKILL.md)**：构建某份规格说明或某组工单所描述的工作，在事先商定的接缝上驱动 `/tdd`，并在提交前用 `/code-review` 收尾。
- **[implement-spec](./implement-spec/SKILL.md)**：在一个集成分支上实现整份规格说明。它把工单当作任务图来推进，在已就绪的前沿上并行运行实现者子 Agent 以获得最大并发，最后用 `/code-review` 收尾。
- **[wayfinder](./wayfinder/SKILL.md)**：把一大块工作（多到一个 Agent 会话装不下）规划成 issue 跟踪器上由决策工单构成的共享地图，一次解决一个，直到通往目的地的路清晰可见。
- **[retro](./retro/SKILL.md)**：在一次会话之后，对编程 Agent 的环境（导航、自动化检查、编码标准、引导文件、工具链）提出改进建议，最严重的排在最前面。

## 模型自动调用

模型或用户都能调用（触发措辞丰富，好让模型主动取用）。

- **[prototype](./prototype/SKILL.md)**：构建一个一次性（用完即弃）原型来回答某个设计问题：要么是一个可分享的单个 HTML 文件，用于状态/逻辑；要么是几个可切换的 UI 变体。

- **[diagnosing-bugs](./diagnosing-bugs/SKILL.md)**：针对难缠 bug 和性能回归的严谨诊断回路：搭起一个会因这个 bug 而变红的反馈回路 → 最小化 → 提出假设 → 插桩 → 修复 → 回归测试。
- **[research](./research/SKILL.md)**：依据高可信度的一手资料调查某个问题，并把发现整理成一份带引用的 Markdown 文件放进仓库，以后台 Agent 的形式运行。
- **[tdd](./tdd/SKILL.md)**：测试驱动开发，采用红-绿-重构回路。一次一个垂直切片地构建功能或修复 bug。
- **[domain-modeling](./domain-modeling/SKILL.md)**：主动构建并打磨项目的领域模型：质疑术语、用场景做压力测试，并就地更新 `GLOSSARY.md` 和 ADR。
- **[codebase-design](./codebase-design/SKILL.md)**：设计深模块所需的共同纪律与词汇：小接口、干净的接缝、可通过接口测试。
- **[code-review](./code-review/SKILL.md)**：对自某个固定基点以来的 diff 做双轴评审：**标准**（是否符合仓库的编码标准，再加一条 Fowler 坏味道基线？）和**规格**（是否忠实实现了最初的 issue/规格说明？），以并行子 Agent 的方式运行。
- **[pr](./pr/SKILL.md)**：一个 PR 正文应有的形态：用能说清改动的最小可视化作摘要，用改前/改后证据证明它有效，以及一个合并风险判断（单向门还是双向门，外加影响半径）。
- **[wizard](./wizard/SKILL.md)**：生成一个交互式 bash 向导，带你走完只有你能完成的步骤：开通基础设施、设置凭据或 CI secrets、在一个陌生的第三方控制台里摸索操作，或执行一次性的迁移或上线切换。
