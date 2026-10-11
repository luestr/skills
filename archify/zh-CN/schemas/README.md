# Archify JSON IR Schemas

每个类型化渲染器都消费一份 JSON 中间表示（IR），它在任何布局工作发生之前，按本文件夹中的某个 schema 校验。

## 文件

| Schema | 管辖 | 结构数组 |
|--------|---------|-------------------|
| `workflow.schema.json` | `diagram_type: "workflow"` | `lanes`、`phases`、`groups`、`mainPath`、`nodes`、`edges` |
| `sequence.schema.json` | `diagram_type: "sequence"` | `participants`、`segments`、`messages`、`activations` |
| `dataflow.schema.json` | `diagram_type: "dataflow"` | `stages`、`nodes`、`flows` |
| `lifecycle.schema.json` | `diagram_type: "lifecycle"` | `lanes`、`states`、`transitions` |
| `architecture.schema.json` | `diagram_type: "architecture"` | `components`、`boundaries`、`connections` |
| `common.schema.json` | 仅共享 `$defs`（无顶层文档） | — |

每个图 schema 都要求 `schema_version`、`diagram_type`、`meta`（含 `title` 与持久的可移植 `output`）及其结构数组——但 `segments`、`activations` 与 `cards` 是可选的——并在每一层设置 `additionalProperties: false`，因此未知字段会被拒绝而不是静默忽略。

每个 `meta` 对象还接受用于生成 HTML 中选择性启用的 SVG/CSS 动效的 `animation: "trace"`。省略它，或设为 `"none"`，即为默认的静态输出。它还接受 `locale`，即任何规范的语言标签（schema 模式 `^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$`）。该字段选择固定的查看器 UI、渲染器拥有的默认图例与可访问性文案、文档标题后缀与 `<html lang>` 值；它不翻译已编写的字符串。`en` 与 `zh-CN` 是内置目录；任何其他标签都需要匹配的 `translations` 对象（见下），否则渲染器回退到英文并披露该事实。省略 `locale` 保留旧行为并解析为英文。畸形的 locale 标签会使 schema 校验失败，而不是被猜测或静默改写。

`meta.translations` 为没有内置目录的 `locale` 提供查看器消息目录，作为数据：一个对象，把规范消息键（见 `renderers/shared/i18n.mjs` 中的 `catalogKeys()`）映射到译文，其 `{placeholder}` 标记与英文来源匹配。缺失、未识别或占位符不匹配的键回退到英文，而不是使渲染失败；`validate`/`render`/`deliver` 把由此得到的覆盖率报告到 stderr。西班牙语使用可复用的 `examples/locales/es.json` 目录；先前仅用 `locale: "es"` 的 dev 输入现在需要在 `meta.translations` 中提供该对象以保留西班牙语 UI。
`visual_preset` 接受 `classic`（稳定的默认值）、`signal-flow`（发光的、动效导向的呈现）、`blueprint`（高对比的工程评审）或 `editorial`（温暖的出版物风格设计评审与文档）。预设只改变查看器样式；它们不改变语义 ID 或几何。
时序 `meta` 还接受 `column_fit`。默认 `fixed` 保留历史的 108px 列间距与 86px 参与者框，使已编写的图无论 viewBox 多宽都以相同坐标渲染。`spread` 则从 viewBox 推导间距与框宽，把宽画布变成列距与标签空间，而不是右侧的空白。两种方式下 lane 顺序、ID 与消息语义都保持不变。

`meta.views` 已弃用。schema 仍接受旧的引导视图形状，使既有文件继续校验，但渲染器忽略它；不要编写它。

### 图例呈现契约 <a id="legend-presentation-contract"></a>

每个 `meta` 对象都接受同一可选的图例形状，而不改变该渲染器已选择的 schema 版本：

```json
"legend": {
  "mode": "auto",
  "entries": {
    "security": { "label": "restricted data", "visible": true }
  }
}
```

`mode` 为 `auto`（默认）、`all` 或 `hidden`。`auto` 只包含类型化 IR 中存在的种类；`all` 包含渲染器的完整稳定目录；`hidden` 移除完整图例，并优先于条目覆盖。省略显式 `viewBox` 的架构文档，用与最终 SVG 布局相同的、实测解析图例足迹来确定该自动 viewBox。在所有渲染器中，省略 `meta.legend` 的旧文档使用兼容安全的隐式 `auto`：若解析出的图例在无重叠时放不进显式已编写的 viewBox，Archify 会省略完整图例，而不是把一个此前有效的 schema-v1 文档变成硬失败。一旦作者添加 `meta.legend`（包括显式的 `mode: "auto"`），布局即是有意的，放不下的标签或带会以路径前缀诊断失败。条目可以设置非空的、有界的 `label`、布尔 `visible` 或两者。`visible: false` 移除一个已解析条目，`visible: true` 强制把一个受支持但未使用的种类加入视觉图例。未知种类与属性会使严格校验失败。

支持的键由渲染器拥有：

| 渲染器 | `meta.legend.entries` 键 |
|---|---|
| Architecture | `frontend`、`backend`、`database`、`cloud`、`security`、`messagebus`、`external` |
| Workflow | `frontend`、`backend`、`security`、`messagebus`、`database`、`cloud`、`external` |
| Sequence | `emphasis`、`return`、`security`、`dashed`、`default` |
| Dataflow | `emphasis`、`security`、`dashed`、`database`、`default` |
| Lifecycle | `start`、`active`、`waiting`、`decision`、`success`、`failure`、`neutral`、`external` |

标签仅用于呈现：它们不重命名稳定种类、不改变节点/关系，也不创建语义透镜边事实。时序消息与数据流流变体条目是视觉键。由确切的已编译节点事实支撑的组件/状态条目获得交互式语义图例桥接；当存在真实的 `nodes[].type: "database"` 事实时，这包括数据流 `database`。

每个关系集合（`connections`、`edges`、`messages`、`flows`、`transitions`）都接受一个可选的、由作者控制的 `id`，使用共享 ID 模式。渲染器另外保留其源顺序运行时键，而已编写的 ID 支持一个稳定的 `#relation=<id>` 查看器链接，在数组重排后仍然有效。无 ID 的文档仍然有效，其关系钉住保持在当前页面本地。

每个语义节点集合（`components`、`nodes`、`participants`、`states`）还接受一个可选的 `brand`：要么是 `archify brands --json` 返回的规范字符串，要么是 `archify brands capture <url> --json` 返回的固定摘要的 `{ "url", "sha256" }` 对象。已知 ID 与已知品牌域使用随附的矢量目录。未知 URL 必须在编写前用该显式命令抓取；render 与 validate 绝不执行未固定的网络抓取。不安全、不可用、已改变或不支持的内容会以品牌诊断 fail closed。省略 `brand` 保留先前的输出。

## schema_version 策略 <a id="schema-version-policy"></a>

工作流支持 schema 版本 1 与 2。版本 1 仍是固定布局兼容契约；版本 2 进入可读工作流编译器，可用 `archify migrate workflow ... --to-schema 2` 显式生成。生命周期也支持版本 1 与 2，字段相同。版本 1 保持固定的三带布局；版本 2 在共享列网格上为每个 lane 渲染一行（见[生命周期渲染器](../renderers/lifecycle/README.md)）。生命周期没有迁移命令：要采用 v2，设置 `schema_version: 2`，把下带 `col` 值重新放到共享网格上（v1 列 `N` 位于 main 列 `N + 2` 之下），并删除为 v1 画布编写的坐标（`viewBox`、`via`、`channelX`、`channelY`、`labelAt`）。
其他三个图 schema 把 `schema_version` 固定为 `1`；它们没有 schema 版本迁移命令。对这五种图类型中的任意一种，修复来源中缺失或不可移植的旧 `meta.output` 并运行 `validate`。仅对工作流 v1 到 v2 迁移，`migrate workflow` 还接受 `--output reports/diagram.html`，把该可移植值放入单独的 v2 目标，而不改变旧来源。

工作流还接受可选的 `semanticChecks`。`allowedRoots` 与 `allowedTerminals` 封闭有意的图源与汇的集合；`requiredEdges` 要求确切的已编写关系；`requiredPaths` 要求有向可达性，同时允许中间节点。编译器在布局前评估这些事实并返回类型化的 `workflow/*` 诊断。该字段是增量且几何中立的：省略它保留既有工作流行为，包含一个已满足的契约不会改变 SVG 或布局回执字节。

今天能校验的文件必须在其声明的版本内、在整个 2.x 发布线中保持可校验与可渲染。明确审阅过的可移植输出加固是唯一的例外：省略 `meta.output` 的旧 v1 文档必须添加一个可移植的 POSIX 相对 `.html` 路径（例如 `reports/diagram.html`）；普通的显式 CLI 输出参数不替代这个持久的已编写值。仅工作流的 v1-to-v2 迁移命令可以改为以 `--output reports/diagram.html` 显式接收该值；它只把该值写入其单独的已验证目标。增量的查看器、可访问性与呈现改进可以增强生成的 HTML，但它们不得重新解释已编写的 IR，或把一个此前有效的、无 profile 的 v1 文件变成新的硬布局失败。破坏性的 IR 改动需要新版本；增量的、向后兼容的字段不需要。

## 共享定义（common.schema.json） <a id="shared-definitions"></a>

五个图 schema 引用 `common.schema.json#/$defs/...`：

- `id` —— 元素标识符，模式 `^[a-zA-Z][a-zA-Z0-9_-]*$`
- `point` —— 一对数字 `[x, y]`（用于 `via` 与 `labelAt`）
- `componentType` —— `frontend`、`backend`、`database`、`cloud`、`security`、`messagebus`、`external`
- `locale` —— 规范的渲染器 locale 标签（`en` 与 `zh-CN` 为内置；任何其他标签需要匹配的 `translations` 对象）
- `translations` —— 规范消息键 → 译文，用于没有内置目录的 `locale`
- `portableOutputPath` —— `meta.output` 使用的可移植 POSIX 相对 `.html` 路径；见[交付契约](../references/delivery-contract.md#output-path-contracts)中的两条输出路径边界
- `brandMark` —— 一个可选的内置品牌 ID 或显式 HTTP(S) 站点 URL
- `variant` —— `default`、`emphasis`、`security`、`dashed`（时序消息在本地用 `return` 扩展该列表）
- `legendMode` 与 `legendEntry` —— 每个渲染器拥有的键映射使用的共享严格模式与标签/可见性覆盖形状
- `guidedViews` —— 已弃用的 `meta.views` 形状，仍被接受并忽略
- `cards` —— 渲染在 SVG 下方的摘要卡片块

生命周期状态 `type` 是模式特有的（`start`/`active`/`waiting`/...），保留在 `lifecycle.schema.json` 中。

JSON Schema 定义是可移植契约在结构上可表达的预检。随附的生成校验器包装与 CLI 额外强制基于字节的组件上限与完整的运行时路径契约；需要相同跨平台接受边界的消费者应使用该包装。

## 运行时校验 <a id="runtime-validation"></a>

开发时，`scripts/generate-validators.mjs` 用 ajv 的 draft 2020-12 standalone 生成器、以 `strict: true` 与 `allErrors: true` 编译全部五个 schema。生成的 `renderers/shared/generated-validators.mjs` 已提交并随技能分发，因此运行时校验没有 npm 或网络依赖。`renderers/shared/validator.mjs` 在渲染器自身的布局检查之前应用匹配的 standalone 校验器。共享加载器随后检查 JSON Schema 在此无法清晰表达的跨集合事实：重复的视图 ID、重复的聚焦 ID、不存在于图语义集合中的聚焦 ID，以及某模式关系集合内重复的已编写关系 ID。

全部五种模式都支持选择性启用的、固定到修订的仓库证据。`meta.repository` 命名仓库 URL 与完整提交 SHA，带可选的 `provider`（`github` 或 `gitee`）与 `link_mode`（`web` 或 `local-only`；见编写契约）；节点可以携带一到三个 `sources`，带仓库相对的 POSIX 路径、可选行范围与可选标签。来源编写在该模式自己的节点集合上——架构 `components`、工作流与数据流 `nodes`、时序 `participants`、生命周期 `states`——校验后的载荷按节点 id 作键。形状经 schema 检查后，渲染器要求 `--repo-root`：本地 Git origin 必须匹配，且 Git 必须证明提交、blob 与所请求的行。校验后的证据嵌入在规范 SVG 之外，供语义护照与节点查找使用；普通文档与视觉导出不携带仓库证据。

## 视觉质量与工程真实性 <a id="visual-quality-and-engineering-truth"></a>

`meta.quality_profile` 与 `meta.engineering_profile` 回答不同的问题。`quality_profile` 在全部五种模式中可用，控制 Archify 判断构图的严格程度。`engineering_profile` 是可选的、仅架构图的语义契约；省略它保留普通的 v1 行为。

第一个工程画像是 `deployment-ownership`。只有当用户想要 fail-closed 部署评审且来源事实已知时才启用它。它要求每个非外部组件在 `tag` 中命名一个 owner，并恰好属于一个 `region`；文档必须同时包含 `region` 与 `security-group` 边界；每个 `database` 必须在某个 `security-group` 内；每个安全组必须包含来自一个共享区域的成员；每个 region 或 security-group 归属发生改变的连接必须在 `label` 中命名真实的跨越机制。

该画像只校验已编写的 IR。它不发现基础设施、不推断 owner，也不证明图与实时环境匹配。若某事实未知，把画像留空或去获取该事实，而不是杜撰。

`pnpm test` 以 check 模式运行生成器，当已提交的校验器与其 schema 漂移时失败。

## 错误格式 <a id="error-format"></a>

Schema 违规以非零退出。每条 ajv 错误单独一行报告为实例路径——标注最近的外层元素的 `id` 或 `label`——后跟消息与参数：

```text
workflow schema validation failed:
  /nodes/3 (id/label: "router") must NOT have additional properties {"additionalProperty":"colour"}
```

Schema 捕捉形状错误（类型、枚举、范围、未知字段）；重叠与标签碰撞之类的几何问题由渲染器负责。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版。所有命令用 `bun` 运行（`node ...` → `bun ...`、`npm ...` → `pnpm ...`）；浏览器操作只用 Chatlo 内置浏览器（`web_browser` / `chatlo-browser`）。
