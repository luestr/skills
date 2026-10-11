# 工作流渲染器

把 `diagram_type: "workflow"` 的 JSON 文件渲染为标准 Archify HTML 模板。

```bash
bun archify/renderers/workflow/render-workflow.mjs input.workflow.json output.html
```

渲染器用随附的独立校验器按 `archify/schemas/workflow.schema.json` 校验输入。无需安装依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必需的 `meta.output` 值。

渲染后运行产物检查器：

```bash
bun archify/scripts/check-render-output.mjs output.html
```

它捕捉最容易在浏览器中看到的最终 SVG 问题：非有限 SVG 值、意外的两点对角箭头，以及穿过图例的箭头。

## 输入

工作流 JSON 必须设置：

```json
{
  "schema_version": 2,
  "diagram_type": "workflow",
  "meta": {
    "title": "Agent Tool Call Workflow",
    "output": "agent-tool-call.html"
  },
  "lanes": [],
  "phases": [],
  "groups": [],
  "mainPath": [],
  "nodes": [],
  "edges": [],
  "cards": []
}
```

新工作流使用 `schema_version: 2`。其可读布局编译器把每个 `col` 视为 `0..5` 的逻辑秩，并从实测文档推导几何。`schema_version: 1` 对既有来源仍是固定的旧契约；有效的 v1 输出按字节保留，且绝不静默地重新解释为 v2。

对常见的 v2 情形省略 `meta.viewBox`，让编译器使用内在的实测边界。在 v1 中，省略的宽度仍固定为 720，高度由 lane 数量推导。完整示例见 `archify/examples/agent-tool-call.workflow.json`；其 `schema_version` 选择适用的契约。

Schema 见：

```text
archify/schemas/workflow.schema.json
```

## 迁移与布局回执 <a id="migration-and-layout-receipt"></a>

把既有的 v1 来源迁移到单独的 v2 文件：

```bash
bun archify/bin/archify.mjs migrate workflow old.json new.json --to-schema 2 --json
```

以其 schema-v2 输出作为新来源再次运行该命令即是一次幂等验证：目标字节与几何保持不变。

若某个旧 v1 来源仅因 `meta.output` 缺失或不再可移植而被阻塞，为其单独的 v2 目标提供替代：

```bash
bun archify/bin/archify.mjs migrate workflow old.json new.json --to-schema 2 --output reports/workflow.html --json
```

`--output` 本身必须是可移植的 POSIX 相对 `.html` 路径。它只更新已验证的目标候选；来源字节保持不变，所有非输出的 schema 与编译器诊断仍会阻塞迁移。

该命令默认绝不覆盖来源。它把绝对 `via[*][0]`、`labelAt[0]` 与 `channelX` 值从旧空间映射到已求解的秩空间，保留 y 坐标，除非某条已报告的垂直约束需要作者输入，仅为一处无歧义的包含修复扩展显式 viewBox，并且只在 v2 编译与产物检查通过后才写入目标。有歧义的显式钉住会失败而不产出目标。

用以下命令检查稳定的、面向作者的 v2 方案：

```bash
bun archify/bin/archify.mjs validate workflow input.workflow.json --layout-json
```

回执报告所选契约、实测 `viewBox` 与 `requiredViewBox`、已求解的列、节点、边、标签与因果诊断。它刻意省略求解器迭代与候选评分。

## 图例

默认图例从 `nodes[].type` 推导组件种类。支持的 `meta.legend.entries` 键，按稳定顺序为 `frontend`、`backend`、`security`、`messagebus`、`database`、`cloud`、`external`。标签与可见性可经由共享图例契约覆盖；只有由已渲染节点支撑的种类才获得语义图例控件。

## 布局契约 <a id="layout-contracts"></a>

### 固定 v1

| 常量 | 取值 |
|----------|-------|
| viewBox | 默认 `[720, auto]`——自动高度 = 52 + lanes×104 + (lanes−1)×20 + 124 |
| Lane 框 | x 40，宽 640，高 104，间隙 20；第一个 lane 顶在 y 52 |
| Lane 标题条 | 每个 lane 的顶部 30px；节点框必须留在其下方 |
| 列中心（`col` 0–5） | x = 88、220、300、430、500、625 |
| 阶段页头 | 可选的 `phases[]` 渲染在第一个 lane 之上，跨 `fromCol..toCol` |
| Lane 分组 | 可选的 `groups[]` 在一个 lane 内框出并行工作或分支工作 |
| 异常 lane | 为 retry、denial、fallback 或 failure 路径设置 `lane.variant: "exception"` |
| 主路径 lint | 可选的 `mainPath[]` 检查 happy-path 步骤有匹配的边且不后退 |
| 默认节点 | 92×52（设置 `tag` 时高 68） |
| 节点间距 | 同一 lane 内节点间 ≥8px |
| 边长 | 直线段必须跨 ≥28px |
| 图例行 | y = lane 底 + 44；viewBox 高度必须 ≥ 图例 y + 18 |

列中心间距为 132 / 80 / 130 / 70 / 125 px：列 1↔2（80px）与 3↔4（70px）都无法在同一 lane 内同时容纳默认宽 92px 的节点。这样的无效 v1 来源会收到一条因果 `workflow/column-capacity` 诊断与一个已验证的迁移至 v2 的修复；v1 绝不回退到自适应布局。

### 可读 v2

| 不变量 | 契约 |
|----------|----------|
| 逻辑列 | `col` 是 `0..5` 的整数；像素中心是实测输出 |
| 相邻秩基线 | 在文档特定约束前，中心距离 120px |
| 同 lane 节点净空 | 当垂直节点区间重叠时 ≥8px |
| 相对的直接边 | 清晰间隙 ≥`max(28px, 实测标签遮罩宽 + 8px)` |
| 自动路由节奏 | 直接段 ≥28px；端点短桩 ≥8px；内部转弯段 ≥16px |
| 隐含 viewBox | 内在内容边界加上契约内边距 |
| 显式 viewBox | 包含容量；过小的输入报告确切的 `requiredViewBox` 与贡献者 |
| Lane 测量 | 同一列的垂直堆叠（两个或更多不同的 `yOffset` 值）会使一个隐含的、未钉住的 workflow 进入逐 lane 测量。显式的 `meta.viewBox`、`via`、`labelAt`、`channelX` 或 `channelY`，以及没有堆叠的 workflow，都保留共享高度的 v2 几何以保持兼容。 |

编译器只对实际相关或重叠的同 lane 节点施加约束，因此无关 lane 里的宽节点不会扩展每个秩。旧中心在正确性约束之后是软偏好，而非几何承诺。阶段与分组框由已求解的秩带推导。自动路线归一化一次，同一最终场景驱动校验与 SVG 序列化。长自动标签比较直接栏位增长与一条合法通道，而不是加宽每个下游秩。实测的多行图例参与内在高度与显式 viewBox 容量。

Issue #250 的形状已有 v2 表示，无需编写 lane 尺寸。把三个阶段放在一个成组的 lane 中，省略 `meta.viewBox`，并让它们的偏移以零为中心：

```json
{
  "schema_version": 2,
  "diagram_type": "workflow",
  "meta": { "title": "stack", "output": "stack.html" },
  "lanes": [{ "id": "cage", "label": "one cage" }],
  "groups": [{ "id": "g", "label": "cage", "lane": "cage", "fromCol": 1, "toCol": 3 }],
  "nodes": [
    { "id": "a", "lane": "cage", "col": 2, "type": "security", "label": "stageA", "yOffset": -90 },
    { "id": "b", "lane": "cage", "col": 2, "type": "security", "label": "stageB", "yOffset": 0 },
    { "id": "c", "lane": "cage", "col": 2, "type": "security", "label": "stageC", "yOffset": 90 }
  ],
  "edges": [
    { "from": "a", "to": "b", "fromSide": "bottom", "toSide": "top" },
    { "from": "b", "to": "c", "fromSide": "bottom", "toSide": "top" }
  ]
}
```

一个隐含的可读 v2 垂直堆叠，其实测 lane 高度超过 104px 基线时，会进入桌面查看器的高度预算。此决定来自已编译几何，而非已编写的定尺寸字段。查看器只改变外侧阅读器宽度，使完整 lane 留在屏幕上；规范 SVG 几何与显式 `meta.viewBox` 的 workflow 保持其已编写契约。必要时，查看器可以缩放到内在 1:1 宽度以下，最远到 6px 投影节点文本下限。若完整 workflow 在该可读缩放下仍放不下，`visual-check` 会报告剩余的视口溢出，而不是裁剪或引入内部滚动条。

已编写的 `via`、`labelAt`、`channelX`、`channelY` 在 v2 中是绝对的硬钉住；不可行的钉住返回 `workflow/explicit-pin-conflict`，而不是被静默移动。`fromSide` 与 `toSide` 仍是方向约束。路线预设限制自动候选族，但本身不是绝对坐标钉住。当任一端点侧被省略时，v2 编译器选择一个可行侧；已编写的一侧把该端点限制到指定端口。

## 设计规则

- 用 lane 表示归属或运行时边界。
- 用阶段页头表示高层故事节拍，如 Intake、Plan、Execute、Report。
- 用分组表示并行检查、分支处理或一个 lane 内有界的工作；每个分组必须至少包含一个节点。
- 对堆叠在一个容器内的顺序阶段，用一个 v2 lane 与一个分组，把阶段放在一列，并省略 `meta.viewBox`。`yOffset` 相对该 lane 内容区的中心，所以用 `-90 / 0 / 90`（而非 `0 / 90 / 180`）居中三阶段堆叠。在编译器拥有路线与画布时，编译器只扩展该 lane。
- 用 `lane.variant: "exception"` 表示人工等待、拒绝、重试、回退与失败 lane，而不是把这些路径混入 happy path。
- 当图有清晰的 happy path 时设置 `mainPath`；渲染器验证连续 id 有匹配的边且从左到右移动。
- 用 lane ID 与 `0..5` 的 `col` 索引摆放节点，不用原始 SVG 坐标。
- 保留语义边标签。可读 v2 为实测标签净空分配空间；当标签放不下时，修复已报告的容量或路线约束，而不是删除含义。
- 用标签表示决策、审批、协议、异步追踪、返回路径，以及任何未完全由端点隐含的关系含义。
- 优先使用路线预设——`drop`（在 lane 间折弯；`bias` 0–1 决定位置）、`outside-right`、`return-left`、`bottom-channel`、`up-channel`——再使用原始 `via` 点。`straight` 与默认 `auto` 覆盖其余情形。
- 让 workflow 示例保持紧凑，以便在窄的聊天/浏览器预览中渲染良好。

### 可选语义检查

布局校验无法从标签或卡片推断领域真相。当源码证据确立了根、终点、必需的直接关系或必需的有向可达性时，把这些事实编码进 `semanticChecks`：

```json
"semanticChecks": {
  "allowedRoots": ["request", "resource_catalog"],
  "allowedTerminals": ["reply", "audit_log"],
  "requiredEdges": [
    { "from": "dispatch", "to": "dispatch_ledger" }
  ],
  "requiredPaths": [
    { "from": "event_ledger", "to": "runtime_host" }
  ]
}
```

当 `allowedRoots` 或 `allowedTerminals` 存在时，它分别是零入边或零出边节点的完整允许清单。`requiredEdges` 要求一条确切的已编写方向；`requiredPaths` 允许中间节点，但遵循已编写的边方向。这些检查在布局前运行，不改变 SVG 或回执字节，且不得仅为解决某条路线或构图诊断而被削弱。未知领域事实的字段请省略。

Schema 违规会以非零退出，消息带有路径前缀，并标注元素的 id 或标签。渲染器还能检测到布局问题时一并失败，包括节点重叠、节点超出其 lane、无效的阶段/分组列范围、空分组、断裂的 `mainPath` 步骤、未知边目标、标签与节点或其他标签碰撞、标签宽于其节点、图例超出 viewBox，或短到无法清晰阅读的直线箭头。共享 Clean Flow Gate 还拒绝以 2px 间隙穿过无关节点的边；lane、阶段与分组是刻意的直通容器。文本宽度按中日韩感知估算：全角字形计为两个单位。

诊断是因果性的：秩容量失败会抑制派生的短边、端点方向与标签重叠发现。每条 `supportedFixes[]` 都通过重新规划所提议的编辑来验证，且当标签存在并非失败不变量的成因时，诊断绝不提议删除语义标签。

把 `meta.quality_profile` 设为 `showcase` 以获得精修交付。此时无关的正交 X 交叉会以 `composition/proper-crossing` 失败；默认 `standard` 将其保留为产物回执警告。共线 lane 走廊在正交 X 规则之外，但当无关边重叠至少 8px 时，另一个门控在 `standard` 中警告、在 `showcase` 中失败。V1 保持其已编写的共享端点契约。V2 还检查共享端点，包括显式受控的路线：长或混合样式的干线、逆流、真正的内部 X 交叉与重叠的独立箭头都不豁免。钉住被保留，而不是静默修复；未解决的 v2 走廊/箭头碰撞在 `standard` 中警告、在 `showcase` 中失败。

V2 仅在两条关系共享实际源或目标端口、有效变体、描边宽度与角色时，才允许最多 24 SVG 单位的同向共享终末短桩。非终末的重叠绝不算这种短桩；前向共线的航点不会把一条长干线拆成被允许的片段。兼容的短合并可以共享其终末箭头。自动路线会考虑分开的端口，在争用节点处保留绝对路线，并优先选择清晰路径而非更短的歧义路径。拥挤的自动走廊可以使用有界的局部调整，而不移动节点或改变显式坐标。

SVG 携带 `data-layout-contract="readable-v2"` 与每条边的角色，使产物检查把同样的分类应用于实际可见的路径几何，而不是陈旧的构图点元数据。这些内部输出属性不增加编写 schema 字段。其他图类型保留其现有规则。V2 的正交交叉诊断在编译器/layout-JSON 回执与最终 HTML 检查中都保留关系 ID、交点与受支持的修复；`standard` 报告警告而 `showcase` 拒绝该交叉。两种分析都合并前向共线航点而不改写已编写路径；真正的折弯与反向仍是端点接触，而不会合并成一个 X。

较旧的逐边 `data-composition-routing="workflow-v2-auto"` 标记保留，以兼容没有根布局契约的首轮导出 HTML 与较旧的产物检查器。仅含标记的产物保留其更窄的自动成对交叉/逆流策略；根 `readable-v2` 契约在存在时是权威，并且也检查显式路线。不要在没有弃用该导出格式的情况下，把仅含标记的路径当作死代码移除。Showcase 还拒绝任何低于 8px 的路线段与任何低于 16px 的内部转弯段；普通的 8–15px 端点短桩对固定 lane 间隙仍然有效。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版。所有命令用 `bun` 运行（`node bin/archify.mjs` → `bun bin/archify.mjs`）；浏览器操作只用 Chatlo 内置浏览器（`web_browser` / `chatlo-browser`），不使用任何第三方浏览器。`finalize` 的自动 `browser-check` 门控在 Chatlo 上标记为 `delegated`，由内置浏览器在设备视口复核。
