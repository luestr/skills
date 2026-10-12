# 进行中

Beta 版。这些技能是故意公开的：试用它们，把坏掉的地方告诉我。在它们晋级到稳定分类之前，不会收录进插件和顶层 README，没有文档页面，并且可能毫无预警地变更或消失。

插件不会提供这些技能。单独安装一个：

```bash
npx skills@latest add mattpocock/skills --skill=<name>
```

- **[loop-me](./loop-me/SKILL.md)**：在多个会话中拷问自己（grill），打磨出可实现的工作流规格，把当前目录当作有状态的工作区。用户手动调用。
- **[writing-beats](./writing-beats/SKILL.md)**：把文章塑造成一段由节拍（beat）构成的旅程，风格像“选择你自己的冒险”。选定一个起始节拍，只写这一个节拍，然后转向下一个，直到文章抵达自然的结尾。
- **[writing-fragments](./writing-fragments/SKILL.md)**：一场拷问式访谈（grilling session），从你身上挖掘片段（fragment，异质的写作小块），并把它们追加到同一个文档里，作为未来文章的素材。
- **[writing-shape](./writing-shape/SKILL.md)**：拿一份装着素材的 markdown 文件，逐段把它塑造成文章，每一步都就格式选择展开论证。
- **[claude-handoff](./claude-handoff/SKILL.md)**：通过 `claude --bg` 把当前对话交接给一个全新的后台 Agent，用一份交接摘要作为它的起始输入，让它立刻接手工作。用户手动调用。
- **[setup-ts-deep-modules](./setup-ts-deep-modules/SKILL.md)**：把 dependency-cruiser 接入 TypeScript 仓库，让每个包都成为深模块：实现藏在子目录里，只能经由包的入口文件访问，测试也通过这些入口文件来检验它。用户手动调用。
