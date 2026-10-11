# 编写契约

只有在“快速编写路径”要求更多细节时才读本参考。schema 与示例仍然是权威。

## 构图修复 <a id="composition-repair"></a>

在纠正已编写总览的抽象层级时，先把每个受影响的角色、关系方向、协议、边界、条件与来源引用映射到它继续存在的节点或关系，再重新分组。一条启动期引用并不证明某种消息协议。保留每条主张被检查过的证据。保持用户提供或已约定的拓扑固定；仅因路线更少并不足以作为合并的理由。环绕单个节点的边界需要一个显式的隔离事实，且不得只是重复其标签。

## 标签修复 <a id="label-repair"></a>

当关系标签发生碰撞时，先移动标签、调整路线或间距，然后在保留含义的前提下缩短措辞。只有当两端完全隐含该措辞、且它不传达协议、动作、方向、同步或异步行为或跨边界机制时，才省略它。间距指清晰间隙，而非中心距离；实测遮罩宽度优先。首稿的间隙预算见[布局与路由](authoring-defaults.md#layout-and-routing)。

对比例失衡的子标签，保留其确切角色或协议的简要表述，并把补充事实放进注释或卡片。保留每一项必需的职责、协议与边界事实。使用[布局与路由](authoring-defaults.md#layout-and-routing)中的首稿节点宽度预算。

## Schema 查找 <a id="schema-lookup"></a>

同时读该模式的 schema 与 `schemas/common.schema.json`。模式 schema 使用 `$ref`，因此共享枚举位于 common 文件中。

- `componentType`：`frontend`、`backend`、`database`、`cloud`、`security`、`messagebus`、`external`
- `variant`：`default`、`emphasis`、`security`、`dashed`
- 关系 ID 使用共享的标识符模式，且在其集合内必须唯一。

不要臆造字段。写任何新字段、枚举或受限文本之前，先读其 schema 定义，包括 common 的 `$ref` 目标。尤其要检查边界种类、仓库身份与来源引用形状。示例演示结构，并不枚举所有合法取值。编写全新的 ID、措辞、事实与布局。

## 工作流布局契约 <a id="workflow-layout-contracts"></a>

新工作流用 schema v2，当既有来源必须保留固定几何时保留 schema v1。两个版本中 `col` 都保持在 `0..5`，且绝不把语义边标签作为间距修复来删除。存在绝对坐标时不要只改 `schema_version`：遵循规范的[迁移与布局回执契约](../renderers/workflow/README.md#migration-and-layout-receipt)。完整规范不变量见工作流渲染器的[布局契约](../renderers/workflow/README.md#layout-contracts)。对堆叠在一个容器内的顺序阶段，用一个 v2 lane 与分组，省略 `meta.viewBox`，并让节点以对称的 `yOffset` 值（如 `-90 / 0 / 90`）相对 lane 内容居中。保留语义边标签，并对编译器诊断采取行动。

## 图例契约 <a id="legend-contract"></a>

对真实的默认省略 `meta.legend`：`auto` 只列出类型化 IR 中存在的语义种类。对渲染器参考用 `mode: "all"`，或对移除完整图例用 `mode: "hidden"`。在 `entries` 下，只有所选模式 schema 列出的键才有效；每个键接受 `label`、`visible` 或两者。`visible: true` 可以显示一个未使用的受支持约定，`visible: false` 则隐藏它。`hidden` 不可被覆盖。

标签覆盖只改变读者措辞。绝不从散文推断种类，或用图例去补偿缺失的节点、状态、消息或流。长标签会被测量并换行成确定性的行。架构图的隐式自动 viewBox 从同一实测足迹增长。为向后兼容，没有 `meta.legend` 的旧文档可以省略放不进其显式 viewBox 的隐式自动图例；这绝不改变其类型化拓扑。添加 `meta.legend` 会使呈现变得有意且严格：若其解析后的标签放不进已编写的 viewBox，则缩短或隐藏它们，或用发出的诊断加宽 viewBox。

## 语言一致性 <a id="language-consistency"></a>

选择一种主要的已编写语言。用户的显式选择优先；否则用请求的语言，或在请求本身语言中立时用对话的主导语言。单独选择查看器 locale。始终把匹配的 `meta.locale` 写为规范的语言标签：英文用 `"en"`，简体中文用 `"zh-CN"`，西班牙语用 `"es"`，或其他语言的任意标签。渲染器消费已编写的 locale，不从图中的字符串推断语言。省略它的文档仍然有效，并默认为英文。

`meta.locale` 只控制渲染器拥有的读者界面：`<html lang>`、文档标题后缀、默认 SVG 描述与聚焦标签、默认图例标签，以及固定的查看器控件、状态、可访问性名称与错误。它绝不翻译已编写的内容。把主要语言单独应用到标题、副标题、节点与关系文案、边界、lane、分组、图例标签覆盖与卡片。双语图仍为查看器选择一种主要 locale；遵循显式的主要语言请求，其次是提示顺序或对话主导性。

`en` 与 `zh-CN` 是内置的查看器目录，无需其他设置。对每个其他 `meta.locale`，还要设置 `meta.translations`：一个对象，把渲染器的规范消息键（`renderers/shared/i18n.mjs` 中的 `catalogKeys()`）映射到译文，其 `{placeholder}` 标记必须与英文来源完全一致。复用 `examples/locales/` 或先前已审阅目录中的合适译文；西班牙语用 `examples/locales/es.json`。按需翻译缺失的键或调整术语；用英文来源核对键与占位符。示例目录可能滞后于新的查看器键；校验会报告这些缺口并对其使用英文。缺失、未识别或占位符不匹配的键回退到其英文字符串——`validate`/`render`/`deliver` 会把由此得到的覆盖率报告到 stderr——而不是中断渲染或静默地把未翻译的字符串当作已翻译来发布。

对仅使用 `meta.locale: "es"` 的较旧 dev 输入，在再次渲染前把西班牙语目录复制进 `meta.translations`。既有的独立 HTML 保留其内嵌译文。

对于你无法提供 `meta.translations` 的请求语言，不要写一个既无内置目录又无翻译的 `meta.locale`。把每条面向读者的已编写字符串保持为请求语言，省略 `meta.locale` 使渲染器安全地使用英文，并明确告诉用户固定的查看器 UI 与 `<html lang>` 仍为英文、产物未完全本地化。回退只适用于渲染器拥有的界面；它绝不允许已编写文案回退为英文。不要把 `zh-CN` 静默替换为另一种语言或中文 locale，也不要机器翻译 `meta.translations` 的值而不说明它们未经审阅。

保留确切的产品名、代码标识符、命令、协议、API 路径与环境名不变。这些术语在本地化文案中可以保留英文，但周边的解释性散文仍必须使用所选语言。渲染器拥有的默认图例标签跟随 `meta.locale`；只有当图需要不同的领域措辞时才编写 `meta.legend.entries.*.label` 覆盖，并让该已编写覆盖保持为主要的语言。

## 视觉预设默认值 <a id="visual-preset-default"></a>

默认省略 `meta.visual_preset`。渲染器随后在浅色与深色两种色彩模式下以 `classic` 打开图。色彩模式与视觉预设是独立的查看器状态：切换 Light / Dark 必须保留当前预设。只有当用户明确要求该视觉风格时，才编写 `signal-flow`、`blueprint` 或 `editorial`。

## 工程画像默认值 <a id="engineering-profile-default"></a>

对普通的系统架构省略 `meta.engineering_profile`。区域、簇与安全边界措辞本身不会启用工程画像。只有当用户明确要求生产部署拓扑、归属交接或 fail-closed 部署评审，且来源事实已知时，才启用 `deployment-ownership`。一旦启用，不要仅为通过校验而移除工程画像；修复已编写的事实或如实报告诊断。

## 标题层级 <a id="title-hierarchy"></a>

用一个精炼的标题，让图承载解释。默认省略 `meta.subtitle`，且绝不用它复述标题、节点、边或卡片。只有当用户明确要求副标题时才包含一条简短的支撑行；省略或空白的副标题不得在生成的查看器中留下一个空的视觉行。

## 可执行几何规则 <a id="executable-geometry-rules"></a>

为笔记本与外部显示器生成一份响应式产物，保留已编写的 SVG/viewBox、比例、语义几何与正常的文档流。当完整图需要更多高度时，使用有意义的内容行与 Reader 声明的可读页面滚动行为；视口适配不授权改变拓扑或使用更小的字号。

- 节点锚点从边的中点开始。`left`/`right` 改变水平端点；`top`/`bottom` 改变垂直端点。对自动架构关系，轴偏移在 16px 以内、无遮挡的相向端口可以在两端都保留 16px 角落间隙的情况下共享一条水平或垂直轴。若恰有一端属于一个铺展组，则只有其未共享的对端移动；两端都铺展的关系保留其独立端口与外侧桥接，除非相向的一对能共同使用分开的直线车道，同时保留端点间距、标签以及周围所有路线与障碍净空。
- 一侧是一份方向契约。第一条与最后一条路线段必须垂直于该命名方向，并向外/向内。
- 在架构图、数据流图与生命周期图中，显式 `route: "straight"` 请求一条直接段，当端点侧未被钉住时它可以是斜的。产物检查器保留此意图；显式侧、不透明节点净空与其他质量门控仍然适用。`via` 优先并保留既有规则，包括数据流对正交 via 段的要求。
- Automatic Port Spread 是架构图、工作流、数据流与生命周期图的默认渲染器行为。共享的自动端点以 16px 角落间隙确定性地、对称地铺展。它不适用于时序消息、单条关系，或显式的 `via`、`channelX`、`channelY`、`labelAt` 或非 `auto` 路线。
- Showcase 路线节奏：每个非零段必须至少 8px；每个内部段必须至少 16px。当铺展端口近乎平行时，路由器使用 24px 端点短桩与 16px 外侧桥接，而不是制造一个极小的折角。
- Showcase 路线紧凑度：当一条显式架构路线的正交长度至少是一条障碍感知合法路线的 2.5 倍、至少多出 200px，并把一个控制点送到内容包络之外至少 96px 时，它以 `composition/excessive-route-detour` 失败。证据记录两种长度、比例、超出量、边界与越界量。移除不必要的 `via`，或把已诊断的走廊向内移动，而不是扩大画布。在同一外侧走廊上重叠至少 32px 的相关关系被视为有意的总线，仍然有效。
- 共享端点走廊只有在语义上保持无歧义时才被允许。无关的共线重叠达 8px 或更多会使 showcase 失败。
- 容器边框是有意的直通几何，但沿结构边框长距离运行的边不是。
- 边穿过无关的不透明节点始终是硬失败，与质量画像无关。

### 显式 `via` 坐标 <a id="explicit-via-coordinates"></a>

使用已解析的离开锚点 `S = [sx, sy]` 与到达锚点 `T = [tx, ty]`。锚点从边的中点开始，但如上面所述，自动路由与 Port Spread 可以移动它们；不要假定从自动路线复制来的锚点就是新编写的显式路线的锚点。显式 `via` 路线不获得 Automatic Port Spread。

对第一个航点 `F = via[0]` 与最后一个航点 `L = via[via.length - 1]`，使用这些对齐与方向（SVG 的 y 向下增大）：

| 侧 | 离开（`fromSide`）：`S` → `F` | 到达（`toSide`）：`L` → `T` |
| --- | --- | --- |
| `top` | `F[0] === sx`，`F[1] < sy` | `L[0] === tx`，`L[1] < ty` |
| `bottom` | `F[0] === sx`，`F[1] > sy` | `L[0] === tx`，`L[1] > ty` |
| `left` | `F[1] === sy`，`F[0] < sx` | `L[1] === ty`，`L[0] < tx` |
| `right` | `F[1] === sy`，`F[0] > sx` | `L[1] === ty`，`L[0] > tx` |

例如，给定一个底部离开锚点 `S = [180, 160]` 与一个左侧到达锚点 `T = [360, 260]`，下面这段关系从底部离开并向右进入目标：

```json
{
  "from": "source",
  "to": "target",
  "fromSide": "bottom",
  "toSide": "left",
  "via": [[180, 200], [300, 200], [300, 260]]
}
```

完整路径为 `[180, 160] → [180, 200] → [300, 200] → [300, 260] → [360, 260]`。只把第一个航点改为 `[200, 200]` 会使离开变成斜的；改为 `[180, 120]` 会让它的 x 保持对齐，但从源向上离开，而不是从其底部向外。两者都违反 `fromSide: "bottom"` 并产生 `clean-flow/endpoint-side-direction`。该示例只确立端点方向：让完整路线避开无关节点，并应用上面的其他几何规则。

### 间距与标签 <a id="spacing-and-labels"></a>

在 showcase 架构图中，未钉住的连接标签在无碰撞时保持其默认位置。若发生碰撞，渲染器会在已解析画布内沿既有路线尝试一组有界的附近位置，避开节点、边界标题、其他标签与其他路线。显式的 `labelAt`、`labelDx`、`labelDy` 或 `labelSegment`（包括零）会禁用该回退。路线与拓扑保持不变；若附近没有清晰位置，校验报告原始碰撞。在添加控件前用 `--layout-json` 检查已解析的标签。标准摆放保留其既有行为。

间距建议指框之间的清晰间隙，而不是中心距离。两个 165px 宽节点之间 200px 的中心距离只留下 35px 的清晰间隙。

对一条关系标签，要求：

```text
clear gap > label mask width + 8px breathing room
label mask width ≈ 6.5px × ASCII units + 13px
CJK characters count as two units
```

关系标签是语义数据。若间隙太小，移动标签、调整路线或间距，然后在保留含义的前提下缩短措辞。只省略已完全被两端隐含、且不承载协议、动作、方向、同步/异步行为或跨边界机制的措辞。保留每一条有意义的标签。删除它不是间距修复。若一条关系因两端完全隐含而一开始无标签，说明为何该措辞是冗余的；这是语义编写选择，不是间距修复。在工作流 v2 中，让编译器先分配其实测遮罩，再应用已诊断的 `labelAt`、`labelDx`/`labelDy` 或 `labelSegment`。除非多条边共享一个受限通道，否则一次只应用一个已诊断的几何控件。那种情况下，从实测几何规划最小的耦合改动并一起校验。架构图/工作流通过 `validate <type> <candidate.json> --layout-json` 提供布局证据；对其他类型，使用校验诊断与渲染出的 SVG 几何。在添加手工路线前，检查不必要的、由代理添加的控件是否禁用了自动端口铺展；保留用户要求的路线意图。使用上面的实测净空规则，而不是猜测坐标。

### 修复证据 <a id="repair-evidence"></a>

对架构图，`validate architecture <input.json> --layout-json` 暴露已解析的组件框、边界框、连接点与标签位置。一个可测量地被拒绝的布局也会返回这些字段，带有 `ok: false`、`contract: "archify-architecture-layout-v1"`、诊断与退出码 1。这是修复证据，不是产物验收；它不写 HTML。畸形输入或实现失败保留普通的失败回执而不带布局。

对 `layout/boundary-out-of-bounds`，使用实测的失败侧。左/上负坐标需要向内移动；只增大 viewBox 宽/高只能处理右/下溢出。边界可以跨行包裹成员。保持真实的成员关系，并在移动成员后重新检查相连路线。

自动架构画布除节点、框与标签外还包含路线点。已编写的 viewBox 保持权威。在 showcase 中，`layout/route-out-of-bounds` 标识被裁剪的路线点；负坐标需要向内调整路线，而右/下溢出也可以改用更大的已编写画布。扩大画布后重新检查桌面可读性。

当若干条交叉/走廊诊断涉及相同节点时，在添加路线控件前先一起考虑它们的摆放。应用一次连贯的修复并校验它；独立的标签微调无法修复共享的布局瓶颈。按 code、subject 与 stage 比较诊断，而不只是总数。

### 修复顺序 <a id="repair-order"></a>

1. 修复缺失/无效的 `meta.quality_profile` 与 schema 错误。
2. 修复节点重叠或越界摆放。
3. 修复边穿过节点与端点方向错误。
4. 修复交叉、歧义走廊、沿边框运行、过度迂回与路线节奏。
5. 修复标签到节点、标签到标签，然后是标签到路线的净空。
6. 修复离开画布的标签：用 `labelAt`/`labelDx`/`labelDy`/`labelSegment` 移动标签，或加宽 `meta.viewBox`。建议的 `labelDx`/`labelDy` 值会**替换**已编写字段，而不是加到其上。

每次编辑后运行 `validate`。按稳定的 `code`、确切的 `subject`、实测 `evidence` 与 `supportedFixes` 消费 `diagnostics[]`。若诊断给出 `labelAt`，就用那个点，而不要另估一个偏移。

## 模式摆放 <a id="mode-placement"></a>

### 架构图 <a id="architecture"></a>

用[构图与含义](authoring-defaults.md#composition-and-meaning)选择总览或机制细节。使用一条明显的主要阅读路径，当请求的拓扑需要空间时它可以跨过有意义的多行。让总览在其所选抽象层级下保持可读；当实现细节能回答读者问题时再展开它们。只对真实的归属、信任、流程或部署边界分组。边界不替代关系。

当 schema 支持时优先使用网格摆放。自由摆放适合有界的例外，而不适合散文级的坐标规划。当事实上确实如此时，把外部参与者留在系统边界之外。

### 工作流 <a id="workflow"></a>

Lane 表达职责或阶段。列 `0..5` 表达逻辑推进。新工作流从 `readable-v2` 开始；仅为旧几何兼容保留 `fixed-v1`。保持 happy path 单调，保留语义边标签，并把重试与异常返回路由到主 lane 走廊之外。

#### 工作流视口修复 <a id="workflow-viewport-repair"></a>

当 `viewer/viewport-overflow` 包含 `workflowLanes` 时，在改动来源前检查最高的已渲染框及其节点跨度。测量值是 CSS 像素；节点上方/下方的空间包含 lane 标题与路由，因此不是可移除空间的预算。框 ID 标识已渲染的 lane 索引。

运行 `validate workflow <source.json> --layout-json`，把这些框对应到来源 lane 与节点。检查是否许多步骤共享最后一个逻辑列并使用很大的 `yOffset` 值。可读 v2 目前在偏移周围保留对称空间，并在 lane 间共享基础内容高度，因此增大一个偏移会放大本来稀疏的 lane。

在来源的归属与显式几何允许之处，把步骤重新分配到逻辑列与有意义的 lane，同时保持主路径单调。保留每个必需节点、关系、标签与语义检查。若归属或绝对钉住阻止重排，报告该约束，而不是自动合并 lane 或移动钉住。校验改动后的 JSON，交付新的 HTML，然后重跑浏览器检查并检查首屏；仅静态通过并不决定视口适配。这些是修复方向，不是有保证的坐标。

### 时序图 <a id="sequence"></a>

参与者按会话角色排序。消息拥有其垂直顺序。用 return/async/security 变体表达含义，而不是装饰；时序图不使用 Automatic Port Spread。

### 数据流图 <a id="dataflow"></a>

阶段表达转换或托管。行分隔并行流。只标注不明显的数据契约、分类或跨边界移动。

### 生命周期图 <a id="lifecycle"></a>

Schema v2（新图）：每个有内容的 lane 是一行，`main` 在最前，`terminal` 在最后，其他按 `lanes[]` 顺序。`col` `0..4` 是一个共享的 x 网格，因此放在它离开的那个状态所在列的状态获得一条笔直的垂直迁移。每条迁移，包括主路径，都是编写出来的；没有隐含轨道。渲染器为画布定尺寸、为同行标签加宽列间距，并把自动迁移正交地路由穿过行间隙。保持标签简短：承载多条平行线的间隙空间很少。

Schema v1（旧版）：主阶段用列 `0..4`；事件与终态带用列 `0..2`，事件/终态列 `N` 对齐主列 `N + 2`。除 `main` 与 `terminal` 外的每个 lane 共用一个中间带；那里同一列的状态需要不同的 `yOffset` 值。

两个版本中，可恢复的失败都需要一条真实的回边到某个活动状态。一张写着“retry”的卡片不是拓扑。

## 仓库证据 <a id="repository-evidence"></a>

当图必须反映真实代码时，在编写前检查仓库入口点、运行时边界、存储、传输与部署配置。只记录你确实验证过的证据。`--repo-root <path>` 被 `render`、`validate`、`deliver` 与 `preview` 接受（对每种图类型），被架构图 `compare` 与工作流 `migrate` 接受；每种模式都以相同方式校验 `meta.repository` 与节点 `sources`。迁移一个基于来源的工作流需要相同的 `--repo-root`，以便在替换目标前校验其候选。绝不只凭文件邻近性或命名推断运行时因果。

声明 `meta.repository.url` 与一个完整 40 字符的 `revision`，然后把 `sources` 附到该模式的节点集合（架构 `components[]`、工作流与数据流 `nodes[]`、时序 `participants[]`、生命周期 `states[]`），带仓库相对 `path`、可选 `line`、`end_line` 与 `label`。校验在该提交处读取 blob，独立于工作树编辑。校验忽略本地 Git 替换引用，包括由 `GIT_REPLACE_REF_BASE` 选择的那些，并始终读取固定 SHA 处的原始对象。它不改变仓库配置，也不删除替换引用。每种链接模式都要求匹配的本地 origin、可用提交、有界路径、blob 与合法行范围。校验是本地且不发远程请求；它既不确立公开可用性，也不确立当前读者的访问权。

`link_mode` 默认为 `web`。GitHub 与 Gitee 的 HTTPS 仓库 URL 生成固定到修订的链接；其公开主机会自动选择提供方。可选的 `provider: "github"` 或 `"gitee"` 必须与主机一致。既有的 GitHub 声明与默认交付回执字段保持兼容。

```json
{
  "url": "https://gitee.com/team/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "provider": "gitee"
}
```

对内部或不受支持的 forge，选择 `link_mode: "local-only"`。查看器保留 SRC 标记、可搜索的文件路径、行范围与修订标签，但没有仓库或来源超链接。证据回执添加 `linkMode: "local-only"`。`url` 作为期望的 origin 身份仍然必需；local-only 禁用链接，而不是身份校验。没有 origin 的仓库不受支持。

```json
{
  "url": "http://git.internal:3000/Platform/Services/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "link_mode": "local-only"
}
```

Local-only 接受 HTTP(S)、`git@host:path` 与 `ssh://git@host[:port]/path` 地址，包括嵌套命名空间。声明一个不含凭据的地址；检出 origin 上的 HTTP(S) 凭据会为身份而被忽略，并在诊断中被隐去。主机名按大小写不敏感比较；仓库路径保留大小写，除既有的 GitHub 行为外。末尾斜杠会归一化掉。只有 GitHub 与 Gitee 会归一化末尾的 `.git` 并以 Git SSH/22 匹配标准 HTTPS/443。对其他主机，使用实际的克隆地址：传输、端口、`.git` 后缀，以及相对远端与绝对路径都必须匹配。例如，`git@host:Team/repo` 与 `ssh://git@host/Team/repo` 不同；`git@host:/Team/repo` 与后者匹配。SCP 风格路径保留字面百分号转义，而 URI 路径会解码它们。SSH 主机别名与 forge 特有的浏览/克隆前缀不作猜测。本版本未实现 GitLab/Gitea/Forgejo/Bitbucket 网页链接；在出现经过测试的链接提供方前使用 local-only。未知网页提供方以诊断失败，而不是发出猜测的链接。

## 手工放置回退 <a id="hand-placed-fallback"></a>

只在没有渲染器可运行时使用。从 `assets/template.html` 开始，保留语义 CSS 类，保留内联 SVG/可访问性结构，并运行交付视觉清单。绝不引入破坏深浅色一致性的内联字面颜色。

## 节点图标 <a id="node-icons"></a>

对领域特有的图，在架构组件、工作流/数据流节点、时序参与者或生命周期状态上设置可选的 `icon`。为日常概念选择 `calendar`、`clock`、`person`、`briefcase`、`flag` 或 `moon`；完整目录（包括既有的技术与生命周期符号）见 `common.schema.json#/$defs/nodeIcon`。用 `icon: "none"` 隐藏角标符号。省略 `icon` 保留基于类型的默认值。这些内联 SVG 符号由渲染器拥有，并随图导出；不接受 URL 与原始 SVG。

图标选择只改变角标符号。节点的类型仍决定颜色与语义分组；品牌标识保持独立。对一张假期工作流，把 `type: "backend", icon: "calendar"` 与 `meta.legend.entries.backend.label: "假期"` 配对，并对调休使用 `icon: "briefcase"` 加一个合适的图例标签。保持节点标签有意义：图标是装饰性的，并对辅助技术隐藏。

完整工作流示例见[假期规划](../examples/holiday-planning.workflow.json)。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版。涉及浏览器的步骤只用 Chatlo 内置浏览器（`web_browser` 工具 / `chatlo-browser` 命令）；`finalize` 的自动 `browser-check` 门控在 Chatlo 上标记为 `delegated`（委派），由内置浏览器在设备视口下完成复核（探针脚本见 `chatlo-browser-evidence.md`）。所有 `node bin/archify.mjs ...` 一律改用 `bun bin/archify.mjs ...`；`preview`/`--open` 不可用，改用 `web_browser` 打开 `chatlo:///绝对路径`。
