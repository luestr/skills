# 生命周期渲染器

把 `diagram_type: "lifecycle"` 的 JSON 文件渲染为标准 Archify HTML 模板。

```bash
bun archify/renderers/lifecycle/render-lifecycle.mjs input.lifecycle.json output.html
```

渲染器用随附的独立校验器按 `archify/schemas/lifecycle.schema.json` 校验输入。无需安装依赖。

若省略 `output.html`，渲染器使用 JSON 文件中必需的 `meta.output` 值。

## 输入

生命周期 JSON 必须设置：

```json
{
  "schema_version": 2,
  "diagram_type": "lifecycle",
  "meta": {
    "title": "Deployment Release Lifecycle",
    "output": "deployment-release-lifecycle.html"
  },
  "lanes": [],
  "states": [],
  "transitions": [],
  "cards": []
}
```

`schema_version` 为 `1` 或 `2`；新图编写为 `2`。lane id `main`（必需）与 `terminal` 在两个版本中都保留。

- **v2** 为每个有内容的 lane 渲染一行：`main` 在最前，`terminal` 在最后，其他 lane 按 `lanes[]` 顺序，每个在左侧栏内标注标题。完整示例见 `archify/examples/deployment-release.lifecycle.json`。
- **v1** 保持固定的三个带：`main` 是顶部阶段带，`terminal` 是底部结果带，其他所有 lane 共用中间事件带，其页头用 ` + ` 连接它们的标签。完整示例见 `archify/examples/agent-run.lifecycle.json`。

Schema 见：

```text
archify/schemas/lifecycle.schema.json
```

## 图例与状态标记

状态颜色跟随 `states[].type`：active 与 start 为青色，waiting 为琥珀色，decision 为紫色，success 为绿色，failure 为玫瑰色，neutral 与 external 为石板色。结构是绘制出来的，而不是用颜色表示：每个 `start` 状态得到一个 UML 初始标记（一个圆点与指向其左侧的箭头），没有出边迁移的状态得到双边框作为终态（在 v1 中，一个 main 状态后面跟着另一个 main 列不算终态，因为隐含的轨道会继续）。

默认图例从 `states[].type` 推导种类；`start` 项显示初始标记，当存在终态时出现一个不可交互的 `final` 项。支持的 `meta.legend.entries` 键，按稳定顺序为 `start`、`active`、`waiting`、`decision`、`success`、`failure`、`neutral`、`external`。标签与可见性可经由共享图例契约覆盖；只有由已渲染状态支撑的种类才获得语义图例控件。

状态装饰共用一个顶部轨道：左侧是类型符号与 `step`，右角是品牌标识，查看器的运行时来源徽标紧挨品牌左侧。当状态具有已验证的仓库来源时，标签布局会为徽标预留其宽度。

## 布局预算（v2）

| 项 | 取值 |
|------|-------|
| 列 | `col` 0–4，每一行共享同一个 x 网格 |
| 默认状态 | 140×64（文本 11px 标签，8px 子标签与标记） |
| 列间距 | 64px；会加宽直到同一行带标签的相邻迁移能在其线旁放下；当画布会超过最小状态文本的桌面可读性预算时，所有间距收窄至 44px |
| 行间距 | 至少 120px；为其路线所需的水平轨道进一步敞开 |
| 画布 | 当省略 `meta.viewBox` 时，由行、列与实测图例定尺寸；已编写的 `viewBox` 会被尊重并校验 |

不带 `via`、通道或非 `auto` 路线的迁移使用 v2 网格路由器：同一行的相邻者水平相连（互为一对的运行成两条平行线），行通过相对的顶部/底部边相连，并在某个行间隙中有一个转弯，阻塞直降的状态把路线送过列之间的空走廊，而在外侧列被阻塞的无标签路线绕网格外侧环绕。每个间隙按最小化交叉的顺序分配轨道。没有隐含轨道；两个 `main` 状态之间不带 `variant` 的前向迁移渲染为强调的主路径。Showcase 标签按“在线的旁边、再在线之上、再向外越过相邻平行线”的顺序排名。

显式的 `fromSide` / `toSide` 值保持权威。与网格路由器所选侧一致的钉住保留其路线与自适应行间距。若自动迁移钉住了不同的侧，场景使用共享的侧感知障碍规划器，同时保留 v2 状态网格与共享端口铺展。

## 布局预算（v1）

| 带 | Lane id | 顶 y | 列中心 | 默认状态 |
|------|---------|-------|----------------|---------------|
| Phase | `main`（必需） | 126 | `col` 0–4 → x = 94、248、402、556、710 | 118×62 |
| Event | 其他任意 id | 278 | `col` 0–2 → x = 402、556、710 | 126×58 |
| Outcome | `terminal` | 450 | `col` 0–2 → x = 402、556、710 | 118×58 |

事件与终态列刻意相对主轨道偏移：事件/终态 `col: N` 使用与 main `col: N + 2` 相同的 x 坐标。例如，下带列 0、1、2 分别对齐到 main 列 2、3、4 之下。

| 常量 | 取值 |
|----------|-------|
| viewBox | 默认 `[980, 660]`；schema 最小 `[420, 566]` |
| 状态区域 | x 在 `[32, 宽度 − 32]` 内；状态底边在 `height − 122` 或以上 |
| 状态间距 | 任意两状态间 ≥10px——跨 lane 检查，因为所有事件 lane 共用一个带；用 `col` 或 `yOffset` 分隔同带状态 |
| 迁移长度 | 端点间 ≥32px |
| 图例行 | 最终基线 y = 高度 − 36；额外的实测行向上回绕 |

主生命周期轨道沿阶段带运行，并延伸到最远的已占用阶段列。迁移的路线预设：`straight`、`drop`（在 `channelY` 折弯，默认为垂直中点）、`bottom-channel`、`top-channel`、`right-channel`、`left-channel`、显式 `via` 点，或默认 `auto`。多段迁移得到圆角；用 `cornerRadius`（默认 10，`0` 为尖角）微调。

迁移的 `label` 与 `note` 各自可选。非空 `note` 即使 `label` 被省略或为空也会渲染，使用其现有的次级文本样式、单行，并保留 note 的精细细节可见性。两者都存在时，note 保持在标签下方。Note 参与自动标签摆放、路线空间预留与标签碰撞检查；现有的 `labelAt`、`labelDx`、`labelDy`、`labelSegment` 控件也可用于摆放仅 note 的文本块。

## 设计规则

- 把生命周期图当作阶段图，而不是密集的状态迁移图。
- 用 `main` lane 把主生命周期放在一条水平行上；在 v2 中，把它的每一步编写为一条迁移。
- 在 v2 中，把中断、恢复或退出放在它离开的那个状态所在列，使它的迁移直落向下。
- 用 `step` 标签表示有序阶段，例如 `01`、`02`、`03`。
- 下带仅用于中断、恢复与终态退出。
- 除非标签不可或缺，否则让迁移标签离开主 SVG；优先使用节点标签、标记、图例项与摘要卡片。
- 优先使用轴对齐线并避免交叉。终态退出在可能时应从其来源事件垂直下落。仍支持显式 `straight` 路线；见[已编写路由契约](../../references/authoring-contract.md#executable-geometry-rules)。
- 用 `success` 表示完成，`failure` 表示失败/终态退出，`waiting` 表示暂停，`decision` 表示质量关卡。

Schema 违规会以非零退出，消息带有路径前缀，并标注元素的 id 或标签。渲染器还能检测到布局问题时一并失败，包括缺失 `main` lane、重复状态 ID、未知 lane、未知迁移端点、状态超出生命周期区域、状态重叠（含跨 lane）、标签与状态或其他标签碰撞、标签宽于其状态、短到无法阅读的迁移，或迁移穿过无关状态（2px Clean Flow 间隙）。生命周期带是刻意的直通容器。文本宽度按中日韩感知估算：全角字形计为两个单位。

把 `meta.quality_profile` 设为 `showcase` 以获得精修交付。此时无关的正交 X 交叉会以 `composition/proper-crossing` 失败；默认 `standard` 将其保留为产物回执警告。最终产物检查会采样圆角 `Q` 角。共线走廊在正交 X 规则之外，但当无关迁移重叠至少 8px 时，另一个门控在 `standard` 中警告、在 `showcase` 中失败。共享语义端点、点接触与更短的重叠仍然有效。Showcase 还拒绝任何低于 8px 的路线段与任何低于 16px 的内部转弯段；普通的 8–15px 端点短桩仍然有效。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版。所有命令用 `bun` 运行（`node ...` → `bun ...`）；浏览器操作只用 Chatlo 内置浏览器（`web_browser` / `chatlo-browser`）。
