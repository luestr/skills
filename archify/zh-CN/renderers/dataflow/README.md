# 数据流渲染器

把 `diagram_type: "dataflow"` 的 JSON 文件渲染为标准 Archify HTML 模板。

```bash
bun archify/renderers/dataflow/render-dataflow.mjs input.dataflow.json output.html
```

渲染器用随附的独立校验器按 `archify/schemas/dataflow.schema.json` 校验输入。无需安装依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必需的 `meta.output` 值。

## 输入

数据流 JSON 必须设置：

```json
{
  "schema_version": 1,
  "diagram_type": "dataflow",
  "meta": {
    "title": "Product Analytics Data Flow",
    "output": "product-analytics-dataflow.html",
    "viewBox": [940, 720]
  },
  "stages": [],
  "nodes": [],
  "flows": [],
  "cards": []
}
```

完整示例见 `archify/examples/product-analytics.dataflow.json`。

Schema 见：

```text
archify/schemas/dataflow.schema.json
```

## 图例

默认视觉图例从 `flows[].variant` 推导种类（省略 `variant` 表示 `default`），并且仅当存在数据库节点时加入 `database`。支持的 `meta.legend.entries` 键，按稳定顺序为 `emphasis`、`security`、`dashed`、`database`、`default`。流变体仅用于视觉，因为 Archify 在这一层没有已编译的边种类事实。而存在的 `database` 项不同：它来自确切的 `nodes[].type: "database"` 事实，因此会发布常规的语义图例计数、可访问名称与键盘交互。在没有数据库节点时强制 `database` 可见，则保持其仅视觉。

## 布局预算

| 常量 | 取值 |
|----------|-------|
| viewBox | 默认 `[940, 720]`；schema 最小 `[360, 360]` |
| 阶段（2–5） | 中心位于 x = 100 + 阶段×215；阶段带宽 168，页头在 y 46 |
| 行顶（`row` 0–4） | y = 128、242、356、470、584（加上 `yOffset`） |
| 默认节点 | 112×58 |
| 节点区域 | x 在 `[24, 宽度 − 24]` 内；y 在 `[104, 高度 − 74]` 内 |
| 节点间距 | 任意两节点间 ≥10px（跨阶段与行检查） |
| 流长度 | 端点间 ≥34px |
| 图例行 | y = 高度 − 36 |

流的路线预设：`straight`、`vertical-channel`、`bottom-channel`、`top-channel`、显式 `via` 点，或默认 `auto`（中点折线）。

## 设计规则

- 用阶段表示数据生命周期边界：来源、摄取、处理、存储、消费。
- 按阶段索引与行索引摆放节点；常见情形不要手工放置原始 SVG。
- 用流标签命名数据资产，而不是传输原语：`clickstream`、`identity map`、`normalized facts`、`feature vectors`。
- 用 `classification` 表示简短的敏感性或治理语境：`PII touch`、`non-PII`、`approved only`、`batch`、`read-only`。
- 用 `security` 表示 PII、策略、同意、访问控制或受限连接。
- 用 `emphasis` 表示主数据路径，用 `dashed` 表示异步或批量派生。
- 标签保持简短，以便在窄预览中放得下。

Schema 违规会以非零退出，消息带有路径前缀，并标注元素的 id 或标签。渲染器还能检测到布局问题时一并失败，包括缺失阶段、重复节点 ID、节点超出可读图区、节点重叠、标签与节点或其他标签碰撞、标签宽于其节点、未知流端点、缺少流标签、短到无法阅读的流、流穿过无关节点（2px Clean Flow 间隙），或阶段超出 viewBox。阶段框是刻意的直通容器。文本宽度按中日韩感知估算：全角字形计为两个单位。

把 `meta.quality_profile` 设为 `showcase` 以获得精修交付。此时无关的正交 X 交叉会以 `composition/proper-crossing` 失败；默认 `standard` 将其保留为产物回执警告。共线阶段走廊在正交 X 规则之外，但当无关流重叠至少 8px 时，另一个门控在 `standard` 中警告、在 `showcase` 中失败。共享语义端点、点接触与更短的重叠仍然有效。Showcase 还拒绝任何低于 8px 的路线段与任何低于 16px 的内部转弯段；普通的 8–15px 端点短桩仍然有效。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版。所有命令用 `bun` 运行（`node ...` → `bun ...`）；浏览器操作只用 Chatlo 内置浏览器（`web_browser` / `chatlo-browser`）。
