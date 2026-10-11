# Authoring defaults <a id="authoring-defaults"></a>

在编写全新候选图之前先读一次。一个已冻结、直接进入 `finalize` 的既有候选图，只有在校修改变了其作者归属时才需要读本文件。

## 构图与含义 <a id="composition-and-meaning"></a>

对于 Architecture，默认以系统总览为主，并以主要用户旅程为线索——除非用户要求更窄的机制、模块图或部署拓扑。当把协作的角色按准确命名的子系统分组仍能解释所请求的交互时，就这样分组。当分组会掩盖控制权的归属、信任或持久化边界、生命周期行为，或读者所询问的其他区分时，就把角色分开。把次要且可选的能力放在有来源依据的简短注释中，除非它们的路径对所求问题至关重要。在标题中指明刻意收窄的范围。

保留所有被请求的职责、关系方向、协议以及会改变行为的条件。在被影响节点或关系上展示审批、授权与状态转换门控；仅凭一张卡片无法为一个本应无条件的箭头附带限定。把来源证据与每条被断言的声明保持在一起。边界表达真实的隔离、归属、运行时或持久化事实。卡片回答读者额外的提问；它们不替代所需的拓扑。节点、边、来源、卡片或边界都没有配额。若编写好的总览在失败后需要重新分组，使用 [构图修复](authoring-contract.md#composition-repair)；用户提供或已确认的拓扑保持固定。

关系标签承载含义。为它们留出清晰的空间，并保留动作、协议、方向、异步行为或跨边界含义。标签只有在两个端点都已完全蕴含它时，才可以一开始就省略；发生碰撞时需要间距或走线修复。当实测证据报告碰撞时，见 [标签修复](authoring-contract.md#label-repair)。

## 布局与走线 <a id="layout-and-routing"></a>

在分配坐标之前，先按 Architecture 节点的真实连接来摆放它们；路由器无法重新排列方框，因此摆放位置决定了连线能否保持笔直。先对每条关系分类，再摆放：

- **主路径**：读者的主要旅程，相邻节点按阅读顺序相邻排列。让中等长度的路径跨越多行有意义的行，而不是压成一条浅浅的水平条带。
- **分支或存储**：直接位于拥有、读取或写入它的节点的上方或下方，并以其为中心，使边成为一段直线。把同一行的所有存储与分支都保持在它的同一侧。
- **回流**（回到更早的主路径节点）：把它的源头放在主路径上没有分支或存储的那一侧，让它穿过一条空的走廊，而不是横穿它们。
- **第二入口**进入一个已有入边的节点：把新的源头摆放到从另一侧到达该节点的位置，通常正下方或正上方。
- **扇出**：一侧有 k 条关系时，至少需要 `32 + 14 × (k − 1)`px（四条需要 74px）。把枢纽的对端摊到两侧或三侧，或者放大枢纽。让父节点相对其子节点居中，并让子节点与其唯一父节点对齐。

在写坐标之前，追踪每条非主路径的关系：它笔直或单折的走廊不得穿过另一个节点，也不得与另一条关系交叉。若是如此，就移动不在主路径上的那个端点。让主要参与者及其首个相连步骤一起从靠近画布原点处开始；用内容行来建立纵向节奏。对全新的 Architecture 省略 `meta.viewBox`，让 Reader 测量内在高度。保留提供的固定几何为权威。

从自动走线和端点侧开始。仅为必要的分支、回流或提供的几何固定某一侧。把 `via`、`channelX`、`channelY` 和标签坐标保留给实测到的缺陷。在写坐标之前，为每条带标签的主路径边预算 `6.5px × ASCII 单位 + 21px` 的净空，CJK 按两个单位计算；使用该标签自身长度，而非整行固定的间距。为 Architecture 子标签按其偏好的 9px 文本尺寸设为 `5.4px × 文本单位 + 8px`，CJK 按两倍计；在不丢失必需事实的前提下让辅助文案保持简洁。不要为减少交叉而牺牲可读性或含义。[几何参考](authoring-contract.md#executable-geometry-rules)对已诊断的布局问题给出了实测的间距、端口、画布与走线规则。

## 证据与 schema <a id="evidence-and-schema"></a>

对于真实仓库，在检视源码的同时遵循 [仓库编写](repository-authoring.md)。把其不含凭据的 origin 与 40 字符的 commit 冻结进 `meta.repository`，把检视过的、相对于仓库的 `sources` 附到每个关键语义节点上，并把 `--repo-root` 传给第一次 `finalize`。每条引用只证明该位置可见的事实。顺着实质性的关系与条件找到其真正的来源；不要拿一条启动时的引用当作协议或持久化的证据。

示例展示的是字段形状，而不是合法取值或来源事实。在添加字段、枚举或受约束文本之前，先读该模式的 schema 与共享定义。尤其要检视 Architecture 的边界种类。把更长的证据放进卡片，同时保留该事实。详见 [Schema 查询](authoring-contract.md#schema-lookup)。

## 呈现与模式 <a id="presentation-and-modes"></a>

使用用户在请求/对话中选择的或所给出的一种主要编写语言。为内置英文（`en`）或简体中文（`zh-CN`）设置 `meta.locale`；对于其他语言，包括西班牙语（`es`），提供 `meta.translations` 并给出可复用的 UI 翻译，或者说明固定的 Viewer UI 与 `<html lang>` 会回退到英文。保留精确的产品、代码、协议、命令、API 与环境名称，同时本地化周围的解释。双语情形见 [语言一致性](authoring-contract.md#language-consistency)。

对 classic 省略 `meta.visual_preset`，对纯标题头部省略 `meta.subtitle`，对真实的自动值省略 `meta.legend`，对普通系统总览省略 `meta.engineering_profile`。显式样式与副标题需要用户的请求。在 [legend](authoring-contract.md#legend-contract) 或 [engineering profile](authoring-contract.md#engineering-profile-default) 契约下使用 legend 或部署归属。品牌标识是可选的，且当某个节点命名了真实产品时是显式的；[品牌标识](brand-marks.md)给出了该分支的查找与捕获规则。绝不要让徽标替代语义类型、标签或关系事实。把必需的 `meta.output` 设为工作目录内可移植的、相对 POSIX 的 `.html` 路径；原生路径的例外见 [输出路径契约](delivery-contract.md#output-path-contracts)。

对于新的 Workflow 使用 schema v2，为固定的旧版来源保留 v1；当泳道或分组几何需要细节时，使用其 [布局契约](../renderers/workflow/README.md#layout-contracts)。对于 Sequence，从固定列开始；当宽的 viewBox 留下未用的水平空间，或有意义的标签需要宽度时，使用 `spread`。对于新的 Lifecycle 使用 schema v2：每条泳道自成一行（`main` 在最前，`terminal` 在最后），并且 `col` `0..4` 在每一行对应同一个 x，因此把中断或退出放在它所离开的状态所在的列；把主路径编写为 transitions，省略 `viewBox`，并让 transition 标签保持简短；一次可恢复的失败需要一条真正的回流 transition。当某个模式特有的摆位或视口问题需要更多细节时，读 [模式摆位](authoring-contract.md#mode-placement)。

`finalize` 执行浏览器门禁。让整幅图在桌面端保持舒适可读，水平溢出为零。必要时使用有意义的纵向行与内在高度的页面滚动。6px 投影文本检查是失败底线；在 1440px 下，普通上下文文本以约 7.5px 或更大为目标。当视口证据失败时，见 [自动化浏览器证据](delivery-contract.md#automated-browser-evidence)。
