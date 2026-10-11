# 内置品牌标识

Archify 内置一份有界的目录，收录 107 个常用于架构图、工作流图、时序图、数据流图与生命周期图节点的品牌。标识是可选的已编写身份：它绝不替代节点的语义 `type`、颜色、标签或关系。

未知站点通过显式的两阶段工作流处理。运行 `bun bin/archify.mjs brands capture <url> --json`，然后编写返回的、固定摘要的 `brand` 值。普通的 render 与 validate 命令不会执行未固定的抓取，内容变化或不可用都会 fail closed。

大部分矢量路径与品牌元数据由 Simple Icons 16.28.0 生成。OpenAI 标识依据 OpenAI 官方品牌指南描绘。每个生成的条目都在 `renderers/shared/generated-brand-marks.mjs` 中记录其来源，以及（上游可用时）其指南与许可元数据。

品牌名与标识可能是各自所有者的商标。Simple Icons 的 CC0 许可涵盖其收集工作，而不涵盖每一底层商标或图形。贡献者在添加或更新标识前必须审阅所记录的来源、当前品牌指南与预期的指代性使用。Archify 不暗示赞助、背书或合作关系。

编辑 `catalog.json`，然后重新生成已提交的零运行时依赖包：

```bash
pnpm run generate:brand-marks
pnpm run check:brand-marks
```

不要手工编辑 `renderers/shared/generated-brand-marks.mjs`。
