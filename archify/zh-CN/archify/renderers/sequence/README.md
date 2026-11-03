# 时序渲染器

把 `diagram_type: "sequence"` 的 JSON 文件渲染为标准 Archify HTML 模板。

```bash
bun archify/renderers/sequence/render-sequence.mjs input.sequence.json output.html
```

渲染器用随附的独立校验器按 `archify/schemas/sequence.schema.json` 校验输入。无需安装依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必需的 `meta.output` 值。

## 输入

时序 JSON 必须设置：

```json
{
  "schema_version": 1,
  "diagram_type": "sequence",
  "meta": {
    "title": "Cache Miss Request Sequence",
    "output": "cache-miss-request.html",
    "viewBox": [920, 760]
  },
  "participants": [],
  "segments": [],
  "messages": [],
  "activations": [],
  "cards": []
}
```

时间线随 viewBox 高度缩放：更高的 `meta.viewBox` 换来更多消息空间，更矮的则收缩可读带而不是裁剪。完整示例见 `archify/examples/cache-miss-request.sequence.json`。

Schema 见：

```text
archify/schemas/sequence.schema.json
```

## 图例

默认视觉图例从 `messages[].variant` 推导种类（省略 `variant` 表示 `default`）。支持的 `meta.legend.entries` 键，按稳定顺序为 `emphasis`、`return`、`security`、`dashed`、`default`。这些是视觉消息键，不是语义透镜控件；标签/可见性覆盖不会产生边事实。

图例位于所有时间线内容之下：最后一条消息及其 note、激活条与分段框，间距 12px。没有 `meta.viewBox` 时画布会增长以保持该间隙。若已编写的 `viewBox` 太矮，`showcase` 会失败并给出应设置的确切高度，`standard` 则隐藏隐含图例而不是把它画在内容之上。生命线止于图例之上。消息标签使用其所在线的颜色；灰色默认线与返回线保持静音文本色。

## 布局预算

| 常量 | 取值 |
|----------|-------|
| viewBox | 默认 `[920, 760]`，当靠后的内容需要图例空间时更高；schema 最小 `[480, 480]` |
| 参与者框 | `fixed`（默认）：86×54，y 72；`spread`：相对 viewBox 的宽度，从 86px 到 190px |
| 参与者列 | `fixed`：中心在 x = 62 + 序号×108；`spread`：列分布于可用 viewBox 宽度 |
| 参与者数量 | 最后一个框必须在 width − 40 或之前结束；放不下的布局 fail closed |
| 生命线 | 从 y 142 到 height − 65（画到图例正上方）；带高必须 ≥120px |
| 消息 `y` 范围 | `[160, height − 83]` |
| 消息间距 | 共享水平空间的消息之间垂直 ≥28px |
| 箭头跨度 | 两个参与者之间水平 ≥60px |
| 分段 | y 像素范围，`to > from`，在 `[72, 生命线底 + 20]` 内 |
| 图例 | 最后一行基线在 height − 54；额外行向上回绕，且保持在时间线内容下方 12px |

`segments[].from/to` 与 `activations[].from/to` 是 y 像素坐标，不是参与者 id；激活还要求 `to > from`。

### 列适配

时序图默认使用 `meta.column_fit: "fixed"`，使既有文档保留其历史坐标。当宽 viewBox 否则会在右侧留下空白，或有意义的参与者标签放不进固定的 86px 框时，用 `"spread"`。Spread 从 viewBox 推导框宽与列距，同时保留参与者顺序、生命线与消息语义。

产物检查器从已渲染的参与者、路线与文本报告 `composition.sequenceColumnSpace`。固定布局中一大块未用的右侧区域可能在 `finalize` 中产生 `inspect-sequence-width` 建议；它是建议，不是新警告或失败。关于有界编写修复与显式 fixed/legacy 保留规则，见[时序宽度复核](../../references/delivery-contract.md#sequence-width-review)。

## 设计规则

- 把参与者排在顶部，按读者应遵循的故事顺序。
- 时间向下推进。
- 用 `emphasis` 表示主请求路径。
- 用 `security` 表示认证、同意、权限与策略调用。
- 用 `return` 表示安静的响应消息。
- 用 `dashed` 表示异步追踪、事件、日志与非阻塞工作。
- 用分段作为浅色背景引导；保持分段标签简短。
- 保持标签精炼，但先尝试 `meta.column_fit: "spread"`，再为了塞进固定框而缩短一个有意义的参与者标签。

Schema 违规会以非零退出，消息带有路径前缀，并标注元素的 id 或标签。渲染器还能检测到布局问题时一并失败，包括缺失参与者、重复参与者 ID、参与者标签宽于其框、未知消息端点、消息超出可读时间线、共享水平空间的消息间垂直间距过紧、无效的分段或激活范围，或参与者超出 viewBox。共享 Clean Flow 契约把参与者页头视为语义框，同时显式允许消息穿过中间生命线、激活条与分段框。文本宽度按中日韩感知估算：全角字形计为两个单位。

把 `meta.quality_profile` 设为 `showcase` 以获得精修交付。此时无关的正交消息 X 交叉会以 `composition/proper-crossing` 失败；默认 `standard` 将其保留为产物回执警告。消息仍可穿过中间生命线。共线走廊在正交 X 规则之外，但当无关消息重叠至少 8px 时，另一个门控在 `standard` 中警告、在 `showcase` 中失败。共享语义端点、点接触与更短的重叠仍然有效。Showcase 还拒绝任何低于 8px 的路线段与任何低于 16px 的内部转弯段；普通的 8–15px 端点短桩仍然有效。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版。所有命令用 `bun` 运行（`node ...` → `bun ...`）；浏览器操作只用 Chatlo 内置浏览器（`web_browser` / `chatlo-browser`）。
