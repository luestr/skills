---
name: archify
description: "创建精炼、经过校验的架构图、工作流图、时序图、数据流图和生命周期/状态图，输出为可交互的独立 HTML（内联 SVG、深浅色主题、可选 trace 动效，支持 PNG/JPEG/WebP/SVG/WebM 导出）。可接受自然语言需求，或粘贴的 Mermaid flowchart、sequenceDiagram、stateDiagram 输入；当图必须反映真实代码时，检查仓库证据。适用于用户要求可视化系统架构、基础设施、云/安全/网络拓扑、技术流程、API 调用时序、请求生命周期、数据管道、ETL/ELT、数据血缘、状态机，或转换/美化 Mermaid 的场景。也适用于带步骤、部件、关系或状态的日常主题：请假或出行计划、申请或审批流程、租赁等往复流程、钱或单据的流向、申请或订单当前进度。不适用于数值图表或仪表盘。本技能是 Chatlo（iOS，内置 WebKit 浏览器）适配版：运行时统一用 bun，浏览器操作只用 Chatlo 内置浏览器，浏览器自动校验在 Chatlo 上委派给内置浏览器复核。"
license: MIT
metadata:
  version: "3.0"
  author: tt-a1i
  based_on: Cocoon-AI/architecture-diagram-generator (MIT, v1.0)
  adapted_for: Chatlo (iOS, built-in WebKit browser)
  display_name: Archify 架构图（Chatlo 适配版）
  display_name_en: Archify
---

# Archify（Chatlo 适配版）

本技能改编自上游仓库 `tt-a1i/archify`（MIT 许可，v3.0），并按 Chatlo 环境（iOS，内置 WebKit 浏览器）改写：运行时统一使用 `bun`；涉及浏览器的步骤只使用 Chatlo 内置浏览器；在 Chatlo 上无法运行的桌面 Chrome 自动校验改为委派给内置浏览器复核。

用**类型化 JSON** 生成可交互的 HTML 图。静态输出是默认行为；只有用户明确要求时才启用动效。

## Chatlo 环境适配（务必先读）

本技能其余章节与上游一致，但在 Chatlo 上，下列事项必须按本节执行：

- **运行时统一用 `bun`**：本技能 CLI 与渲染器都是零依赖 ESM，本机用 **`bun`** 运行。下文所有命令中的 `node bin/archify.mjs` 一律替换为 **`bun bin/archify.mjs`**。CLI 内部通过 `process.execPath` 派生子进程，因此用 `bun` 启动时会自动继续使用 `bun`，无需额外设置。
- **`bin/archify.mjs` 的路径**：下文命令里的 `bin/archify.mjs` 指本 SKILL.md 所在目录下的 `bin/archify.mjs`。输入/输出路径都相对工作目录解析。
- **浏览器（强制）**：任何打开网页、预览页面、抓取/渲染网页、网页自动化点击输入、截图、Cookie、导出等操作，**只能**使用 Chatlo 内置浏览器——即 `web_browser` 工具（或等价的 `chatlo-browser` 命令）。**禁止**安装、下载、运行 Chrome / Chromium / Firefox / Edge / Playwright / Puppeteer 等任何第三方浏览器或内核，也不得用无头内核绕过。
- **浏览器自动校验在 Chatlo 上不可用 → 委派**：上游的 `browser-check` 门控会启动桌面 Chrome，并通过 DevTools 协议在 4 个桌面视口下测量包含关系与可读性；Chatlo 没有 Chrome，内置浏览器的视口由系统固定（手机尺寸），无法复现这些桌面视口。因此 `finalize` 在 Chatlo 上把 `browser-check` 阶段标记为 **`delegated`（委派）**，不改判为失败：`validate → deliver → check` 仍会全部门控通过。被委派的浏览器复核由**你**用内置浏览器完成（见“交付”一节的“Chatlo 浏览器复核”）。
- **临时目录**：Chatlo 的 `/tmp` 是 tmpfs，会让原子输出的身份校验失败；CLI 已自动把内部临时目录切到 hostfs 的 `/agent/tmp`。如需覆盖，设 `ARCHIFY_TMPDIR` 或 `TMPDIR`。
- **自我更新检查默认关闭**：上游会访问一个 GitHub Pages 的更新清单，本技能默认设置 `ARCHIFY_UPDATE_CHECK_DISABLED=1`；无需（也不要）主动检查或安装更新。如确需开启，设 `ARCHIFY_UPDATE_CHECK_DISABLED=0`。
- **不要用 `preview`、也不要 `--open`**：Chatlo 没有 `open` / `xdg-open`，也不保证宿主的 `127.0.0.1` 可达。生成 HTML 后，用 `web_browser` 工具打开该文件的 `chatlo:///绝对路径`，例如 `chatlo:///agent/outputs/archify/.../xxx.html`；不要把页面当普通文本显示。
- **产出目录**：除非用户指定其他位置，每个图请求使用自己的目录 `.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`（本地时间，请求开始时选定一次）；也可放到 `/agent/outputs/archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`。目录内保留 `candidate.json` 与 `<slug>.html`，把 `meta.output` 设为该 HTML 的相对路径，修复重跑时沿用同一目录。后续请求用新目录，旧版本得以保留。
- **交付文件**：需要把 HTML 交给用户时，用 `present_files` 交付该 HTML 文件。

## 已有候选交接

当用户提供一个冻结的候选（candidate）时，先作为一次 CLI 调用运行 `finalize`。它通过的回执即完成自动门控；在声明视觉质量前，按“交付”一节处理任何视觉复核建议。修复则遵循下面的第 5 步。

`finalize` 在交付回执中带有有界的更新检查；在 Chatlo 上该检查默认关闭（见“更新感知”）。

## 快速编写路径

普通生成走这条路径。只有在各自触发条件成立时，才去读分支参考文档。

1. 从问题判断类型：`architecture`、`workflow`、`sequence`、`dataflow` 或 `lifecycle`。
2. 使用“类型路由”表中给出的确切 schema 与示例路径，不要罗列其目录。把 [编写默认值](references/authoring-defaults.md) 与该模式的示例放在一个有限的批次里读取，和项目文档、完整 schema 分开读，避免任一方被截断；写之前补齐任何缺失的小节。架构图使用对应的 showcase 示例；时序图、数据流图、生命周期图还要读该模式的 schema 与公共 schema。选择任何新字段、枚举或受限文本（尤其是边界种类）之前，先读相关 schema 定义。**示例只教“形状”，不教“事实”**；使用全新的 ID、措辞与布局。直接产出候选，不要先跑 help、doctor、starter 校验、临时图或输出路径枚举。只有用户明确要求某个品牌标识时才查询品牌；遇到未知标识且用户给了 URL 时，读 [品牌标识](references/brand-marks.md)。
3. 一旦覆盖了用户要求的范围，且（对真实代码库）覆盖了[源码证据](references/repository-authoring.md)，就直接写出完整候选，不要用文字先规划坐标。在定坐标前，按“编写默认值”选择架构抽象层级与连通布局：展示主要用户旅程与必要分支，保留控制角色与改变行为的条件，并为实际的关系标签留足空间。任何节点、关系、来源、视图、卡片或边界的数量都不是目标或上限。优先使用自动路由；只有必要分支、回边、给定几何或实测修复时才加显式路由。除非用户要求密集的 `standard`，否则把 `meta.quality_profile` 设为 `"showcase"`。
4. 写完完整的第一版候选后，直接运行 `finalize`。它的第一个门控就是 showcase 校验；成功的第一版无需单独预校验。命令运行期间保持候选不变：

   ```bash
   bun bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
   ```

   对基于仓库证据的候选，在第一版就带上证据，并使用完整首条命令：`bun bin/archify.mjs finalize <type> <candidate.json> <output.html> --repo-root <repo-root> --quality showcase --json`。

   通过的回执证明其中的 `validate`、`deliver`、严格 `check` 以及 `browser-check` 门控已通过；在 Chatlo 上 `browser-check` 显示为 `delegated`（见“Chatlo 环境适配”）。使用它的精简摘要；只有在单独请求或聚焦诊断某个失败时，才单独运行各命令。

5. 非零退出永远不等于成功。读取精简 stdout 或 `evidence.summaryReceipt`，然后[修复失败的门控](references/delivery-contract.md#failed-finalize-and-candidate-repair)，包括其修复次数上限。保留用户要求的含义与源码证据。对纠缠的架构路由，读[架构布局修复](references/architecture-layout-repair.md)；对实测的字段或几何失败，读[编写契约](references/authoring-contract.md)。编辑连通的邻域，并从第 4 步重跑完整的 `finalize` 命令。

## 更新感知

`finalize` 与独立的 `deliver` 会在回执中包含 `update`。**在 Chatlo 上该检查默认关闭**，`update.status` 为 `unavailable`、`reason` 为 `disabled`，因此**无需**保留任何更新提示行，也不要主动检查或安装更新。只有当用户显式把 `ARCHIFY_UPDATE_CHECK_DISABLED` 设为 `0` 时，才遵循上游的更新提示约定（见 `references/update-awareness.md`）。

第一个候选之前，请使用编写参考与相关仓库源码，而不是 Archify 实现或测试。只有在聚焦修复后诊断仍无法处理时，才检查 Archify 实现。

## 类型路由

| 类型 | 用于 | Schema | 示例 |
|---|---|---|---|
| `architecture` | 组件、服务、云/安全边界、基础设施；某日常事物由什么构成 | `schemas/architecture.schema.json` | 系统描述、服务、库、CLI 仓库：`examples/web-app.architecture.json`；部署仓库：`examples/production-deployment.architecture.json` |
| `workflow` | 流程、审批关卡、工具调用、运维手册、CI/CD；计划与分步的日常流程 | `schemas/workflow.schema.json` | `examples/agent-tool-call.workflow.json` |
| `sequence` | API 调用链、请求生命周期、异步追踪、返回值；人与人之间的往复 | `schemas/sequence.schema.json` | `examples/cache-miss-request.sequence.json` |
| `dataflow` | 管道、ETL/ELT、血缘、治理、消费方；钱或单据的流向 | `schemas/dataflow.schema.json` | `examples/product-analytics.dataflow.json` |
| `lifecycle` | 状态/状态迁移、重试、等待与终态；申请或订单当前进度 | `schemas/lifecycle.schema.json` | `examples/deployment-release.lifecycle.json` |

类型含糊时，运行 `bun bin/archify.mjs guide "<scenario>" --json`。场景示例是结构性参考，不是要照抄的事实。

对日常主题，沿用同样的五种模式与语义类型，然后按读者来命名：使用日常化的 `icon` 值与 `meta.legend` 标签，见[节点图标](references/authoring-contract.md#node-icons)。缺失的个人事实（日期、金额、规则）应向用户询问，而不是杜撰。

## Mermaid 输入

把 Mermaid 当作拓扑与语义来读，然后重新编写全新的 Archify JSON；不要机械地照搬 Mermaid 样式。

- `flowchart` / `graph` → `workflow`；若为组件映射则用 `architecture`。
- `sequenceDiagram` → `sequence`；参与者变成语义参与者，箭头变成消息。
- `stateDiagram` → `lifecycle`；状态与迁移保留含义，而不是 Mermaid 样式。

## 交付

第一版候选以及每次修复之后，使用上面的 `finalize` 命令。

`finalize` 在第一个未通过的门控处停止。它的精简 stdout 与 `<output-stem>.finalize-summary.json` 是普通证据。通过的一轮不生成截图，并报告 `visualReview: "not-requested"`。

### Chatlo 浏览器复核

在 Chatlo 上 `browser-check` 显示为 `delegated`，`finalize` 的 `visualReview` 为 `delegated-to-chatlo-web_browser`。当你需要视觉/感知复核，或用户明确要求“看一下效果/视觉复核”时，用**内置浏览器**完成：

1. 用 `web_browser` 工具 `open` 打开产出的 HTML：`chatlo:///绝对路径/<slug>.html`（深浅色可加 `?theme=light` / `?theme=dark`）。
2. 用 `web_browser` `screenshot` 截图（长页面加 `--full-page`），或 `snapshot` 读取可见文本与结构，检查：是否出现横向溢出、图例与底部导航是否重叠、文字是否过小、深浅色主题是否正确。
3. 可选：用 `web_browser` `act --kind evaluate` 执行 `references/chatlo-browser-evidence.md` 中的探针脚本，得到与上游同口径的几何/可读性数据（如最小投影字号、包含关系、图例-导航交叠面积），据此判断是否需要修复。
4. 只有你**实际**查看过截图/快照后，才声明视觉质量；否则只报告自动校验结果。

当一次通过的架构回执报告 `visualReviewRecommendation.signals.resolvedCrossovers` 时，把候选另存一份，然后做一次只改节点位置与尺寸的编辑：每个节点、关系（含其 `from` 与 `to`）、标签与来源保持原样。用 `--out-dir <folder>/review-2` 重跑一次完整 `finalize`，因为上一版 HTML 已拥有其浏览器证据。若该轮失败或报告更多交叉，则恢复副本并用 `--out-dir <folder>/review-3` 收尾。不要开启第二轮布局。仅有额外折弯的提示是可选的。

当 `layoutReviewRecommendation.action` 为 `inspect-sequence-width` 时，在交接新编写的时序图前，遵循[时序宽度复核](references/delivery-contract.md#sequence-width-review)。

`visualReviewRecommendation` 是建议性的。只有在用户请求视觉复核、开发审计或存在具体路由/浏览器问题时，才做感知复核。关于失败门控、独立命令、溯源/恢复、重复交付、导出或打开，读[交付契约](references/delivery-contract.md)。恢复顺序为 `deliver` → 严格溯源 `check` → `browser-check`（在 Chatlo 上后一步的浏览器门控委派给内置浏览器）。

对工作流视口溢出，在下一次布局编辑前读[工作流视口修复](references/authoring-contract.md#workflow-viewport-repair)。

把产物检查、浏览器证据、截图与实际的感知复核作为**不同**的结果分别报告。用户明确要求立即预览或持续桌面循环时，见[可选打开](references/delivery-contract.md#optional-opening)（注意：Chatlo 上应改用内置浏览器打开）。

## 可选查看器能力

`meta.animation: "trace"` 为可选启用。

仅当用户明确要求分享卡片（Share Cards）、路由/可达卡片（Route/Reach cards）、动效、深链、演示、搜索/聚焦或其他查看器运行时（Viewer Runtime）能力时，才读 `references/viewer-runtime.md`。

## 安装与回退

技能包内无需安装。诊断安装时，用以下命令自检：

```bash
bun bin/archify.mjs doctor
bun bin/archify.mjs demo <output-directory>
```

当 shell 不可用时，把架构 SVG 手工放入 `assets/template.html`，使用 CSS 语义类而非内联颜色，并遵循 `references/delivery-contract.md` 中的视觉复核约定。

## 输出

返回：已校验 HTML 的绝对路径、图的类型、校验摘要、规格/产物回执、浏览器证据状态，以及真实的视觉复核状态。**不要**为非零命令声明成功，也不要宣称你并未实际执行的视觉检查。
