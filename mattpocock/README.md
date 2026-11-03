# mattpocock skills（简体中文翻译版）

翻译自 [mattpocock/skills](https://github.com/mattpocock/skills)，翻译日期 2026年10月12日。中英双语，两个语言版本各自独立可用、互不引用。

## 结构

每个语言目录下按分类组织技能：

```text
mattpocock/
├── zh-CN/
│   ├── engineering/      20 个技能 + README.md
│   ├── in-progress/      7 个技能 + README.md（Beta，可能随时变更）
│   ├── misc/             4 个技能 + README.md
│   └── productivity/     7 个技能 + README.md
├── en-US/                与 zh-CN 同构
├── LICENSE
└── README.md
```

分类不是规范要求的一层，而是上游的组织方式。它带来的实际影响：技能发现机制通常不会递归进去，**安装时要指到具体技能目录**，例如把 `zh-CN/engineering/tdd/` 放进你的技能目录，而不是整个 `engineering/`。

各分类的完整技能清单见对应目录下的 `README.md`。

## 用户手动调用 vs 模型自动调用

多数技能声明了 `metadata.disable-model-invocation: true`，意图是「只在用户显式调用时使用」，与上游 Claude Code 的 `disable-model-invocation` 语义一致。上游直接把该键写在 frontmatter 顶层，但这不符合 Agent Skills 的元数据规范（顶层只允许 `name` / `description` / `license` / `allowed-tools` / `metadata` / `compatibility`），因此本项目把它收进 `metadata` 下。

**注意**：置于 `metadata` 之下意味着标准消费方会忽略它，这些技能在标准 Agent 里可能仍会被模型主动触发。要严格复现「只能手动调用」，需要在目标工具的支持范围内配置。

## 许可

MIT，见 [`LICENSE`](LICENSE)。版权归 Matt Pocock。
