# 领域文档

工程技能在探索代码库时应如何读取本仓库的领域文档。

## 探索之前，先读这些

- 仓库根目录的 **`GLOSSARY.md`**，或者
- 仓库根目录的 **`GLOSSARY-MAP.md`**（如果存在）：它指向每个上下文一份的 `GLOSSARY.md`。读取与当前主题相关的每一份。
- **`docs/adr/`**：读取涉及你即将改动的区域的 ADR。在多上下文仓库中，还要查看 `src/<context>/docs/adr/` 里与特定上下文相关的决策。

如果这些文件不存在，**静默继续**。不要指出它们缺失，也不要建议提前创建。`/domain-modeling` 技能（经由 `/grill-with-docs` 和 `/improve-codebase-architecture` 到达）会在术语或决策真正敲定时按需创建它们。

## 文件结构

单上下文仓库（大多数仓库）：

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `GLOSSARY-MAP.md`）：

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← 全系统范围的决策
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← 上下文专属的决策
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## 使用术语表的词汇

当你的输出要命名一个领域概念时（无论是 issue 标题、重构提案、假设，还是测试名称），都使用 `GLOSSARY.md` 中定义的术语。不要滑向术语表明确排除的同义词。

如果你需要的概念还不在术语表里，这是一个信号：要么你在发明项目并不使用的说法（重新考虑），要么这里存在真实的空白（记下来，留给 `/domain-modeling`）。

## 指出 ADR 冲突

如果你的输出与现有 ADR 矛盾，就明确指出来，而不是悄悄覆盖：

> _与 ADR-0007（事件溯源订单）矛盾，但值得重新讨论，因为……_
