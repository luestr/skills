# 交付契约

## 失败的 finalize 与候选修复 <a id="failed-finalize-and-candidate-repair"></a>

`finalize` 在第一个未通过的门控处停止。使用精简 stdout 或 `evidence.summaryReceipt`；只有当摘要缺少进行连贯修复所需的证据时，才读它的完整伴随文件。只有四项产物检查的回执是基本校验，不是 showcase 验收：要求全部九项检查、零构图错误、零警告。先修复 `meta.quality_profile` 与 schema 错误，再处理几何。

对校验失败，在诊断所指的连通邻域内编辑既有 JSON，然后再重跑命令。保留所要求的语义、有意义的标签、源码证据，以及固定的或已约定的拓扑。多条共享节点的路线要求一次摆放修复；该情形读[架构布局修复](architecture-layout-repair.md)。重排被阻塞的主路径，而不是微调无关标签。当无关几何的构图已经读起来清晰时，保持它们不变。只有当精简证据缺少所需测量时，才在编辑前用 `--layout-json`。工作流 v2 用其稳定的编译器回执（而非求解器内部）作为编写证据。

编辑后，用 `--quality showcase` 重跑完整的 `finalize` 命令；对基于仓库的工作，再加 `--repo-root <repo-root>`。若输出路径已经有来自另一个候选的浏览器证据，为新 `finalize` 与任何 `visual-check` 使用全新的 `--out-dir <output-stem>.review-<revision>`。编辑后省略早先的 `--candidate-sha256`，因为它绑定的是上一个候选。按 code、subject、stage 与 evidence 比较诊断，绝不只看错误数下降。若某个问题在两次聚焦修复后仍存在，检查实测几何或相关契约；在一次基于证据的重试后，报告具体的缺口。

只有当聚焦诊断时才用独立的 `validate`，对基于仓库的工作传 `--repo-root`。它通过的回执标记 `candidateFrozen: true`；运行 `nextAction.arguments`，只替换 `<output.html>`，不要编辑、重新校验或重读候选。之后的环境或证据失败针对那些已冻结的字节重试。只有当实测原因要求编辑时，才产生新候选，并在不带旧 hash 的情况下调用完整 `finalize`。

## 校验与交付 <a id="validate-and-deliver"></a>

`render` 与直接渲染器入口把分类后的编写失败以可读诊断打印到 stderr 并退出 1。输入读取/JSON 解析失败用 `input/read` 或 `input/json-parse`；输出文件系统失败用 `output/write` 并标识输出路径。Schema 与布局失败保留其既有规则码。机器回执请用所宣传的 `validate --json` 或 `deliver --json` 接口；`render` 没有 `--json` 标志。意外的实现失败在人类模式下保留调试信息，在机器回执中保持 `internal/unclassified`。

每个已交付输出都有两条产物专属的元数据路径。当某个输出 stem 对派生的文件名太长时，Archify 会缩短它并附加一个稳定 hash：

- `<output-stem>.delivery.json` 记录最近一次完成的尝试。
- `<output-stem>.delivery-pending.json` 是进行中尝试的恢复日志。

对一个已经匹配 Archify 保留的有界名称标记的字面产物 stem，当编码后的伴随文件缺失时，一个命名空间之前的原始溯源伴随文件仍是读取回退。命名空间之前的原始 pending 日志是一道独立的 fail-closed 屏障：即使同时存在编码后的 pending 日志，它也会阻塞检查与重新交付，且两个日志都不会被静默替换。

一个目录级的 `.archify-delivery-lock.json` 会串行化所有解析到同一物理输出目录的交付。这刻意阻止大小写、Unicode 归一化、Windows 短名与符号链接别名在同一文件系统位置创建各自独立的拥有者。代价是：同一目录中针对不同产物名的交付也会串行运行；溯源与 pending 日志仍按产物区分。

为迁移安全，Archify 还会检测并保留所请求产物旁的旧版 `<output-stem>.delivery-lock.json`。存在的旧版条目是 fail-closed 恢复屏障。当一个新交付持有目录互斥量时，它还会为所请求的拼写与既有产物的物理目标拼写持有临时的旧格式围栏。它先获取目录锁，再在写日志或产物之前获取所有必需的兼容围栏，并在释放时先移除目录锁、再移除这些围栏。这阻止使用任一已知拼写的旧 Archify 二进制进入该交付。若某条旧版围栏的原始 HEAD 时代文件名超过宿主组件上限，则将其省略——因为旧二进制在宿主上也无法创建该锁或交付该产物。

`deliver` 在创建或替换恢复日志之前，通过排他 `open(..., "wx")` 获取锁。成功的排他创建产生一个绑定到该次尝试的内部不透明所有权能力。日志创建、失败溯源记录、成对提交、回滚、日志终结与锁释放，各自在会改变共享状态的操作内校验当前能力。被拒绝的竞争者不会创建日志或写入失败溯源。

既有的目录锁或旧版锁在没有自动恢复的情况下处理：

| 观察到的锁状态 | 必需的 `deliver` 结果 |
| --- | --- |
| 无目录条目 | 尝试排他创建；只有其成功才授予所有权。 |
| 有效的 schema-v1 锁，其 PID 正在运行，或其死亡无法确定 | 以 `delivery/concurrent-attempt` 退出 1；保留每条共享路径。 |
| 有效的 schema-v1 锁，其 PID 已知已退出 | 以 `delivery/lock-stale` 退出 1；原样保留锁、产物、日志与当前溯源。 |
| 不可读、畸形、符号链接、悬空符号链接、目录或其他非普通锁条目 | 以 `delivery/lock-invalid` 退出 1；保留该条目与每条其他共享路径。 |
| 已获取的能力不再匹配当前锁或日志 | 以 `delivery/ownership-lost` 退出 1；停止所有共享路径改动。 |
| 匹配的拥有者无法移除其锁 | 以 `delivery/lock-release` 退出 1；保留该锁。 |

`delivery/lock-stale` 诊断标识绝对的输出与锁路径，以及原始 PID 与回执 ID。恢复是刻意显式且串行的：停止该物理输出目录的所有交付尝试，确认没有活动交付拥有它、且所报告的陈旧条目未被替换，只移除所报告的锁，然后重跑 `deliver`。**不要**把产物、当前溯源或 pending 日志作为陈旧锁恢复的一部分移除。

锁协议面向本地文件系统上、相互协作的 Archify 进程的 Node.js 18 或更高版本。PID、回执与文件身份比较是防御性检查，不是原子 compare-and-swap。兼容围栏覆盖所请求的拼写与既有的物理目标拼写；它们无法枚举任意硬链接名或先前未知的文件系统别名，因此通过此类别名的混合版本交付不在范围内。本契约不声称在 NFS、SMB 或其他网络文件系统上的分布式锁正确性，也无法阻止忽略该协议的外部进程替换共享路径。

每个 no-clobber HTML 发布器（`render`、`deliver`、`compare`、`preview`）在暂存前捕获所请求的目录条目、规范写入槽、物理父级，以及既有目标类型、设备/inode 身份与模式，然后在替换前立即重新校验该快照。既有的写入目标必须是恰好有一个硬链接名的普通文件。有多个硬链接名的目标以 `output/target-hardlinked` fail closed：替换所请求的名字无法把未知的兄弟名字更新为一次发布。硬链接对读取身份与输入/别名碰撞检查仍然受支持；只在作为写入目标时才不受支持。指向单链接普通文件的符号链接仍受支持：发布会保留该符号链接条目，并对其解析后的目标应用同样的协议。目录、FIFO、套接字、设备、变化的模式、新的主张者与不确定的身份在替换前失败。

发布是 no-clobber 且可恢复的，而不是对既有目标的崩溃原子替换。为避免覆盖在最后一次身份检查之后出现的主张者，Archify 先把已绑定的旧文件保留在一个私有恢复备份中，通过身份绑定的隔离移除公共名，然后用排他硬链接创建新的公共名。被捕获的失败在公共槽与恢复绑定仍允许时回滚。这两个命名空间操作之间的进程中断则可能让公共路径缺席，而经校验的前一字节仍留在相邻的私有恢复备份中。单产物发布把原始槽/别名身份与备份的 inode、模式、SHA-256 与字节数记录在私有 `.archify-remove-*/publication-recovery-v1.json` 中，紧挨 `previous`。要让某次被中断的发布重新可见，停止并发写入者并运行：

```bash
bun bin/recover-output.mjs /absolute/path/to/.archify-remove-<id> --json
```

这是显式恢复，不是目录扫描器。在链接前，该助手检查父级或别名是否改变、记录或备份是否被改动/硬链接、摘要或 inode 是否不匹配，以及是否存在任何公共目标。它只通过 no-clobber 硬链接恢复，因此新的主张者被保留而不是被覆盖；它绝不递归移除未知条目。完成的恢复是幂等的。记录是要被独立校验的证据，而不是恢复任意私有字节的权威：该助手只接受来自原始物理目标父级的已记录生成子目录、且具有相同目录身份的记录。指名被中断进程所报告的确切目录，并手工检查不确定的记录。不协作的进程仍可能在这些检查之后、Node.js `linkSync` 之前交换路径名；Node 不暴露绑定描述符的链接操作。链接后的身份校验随后 fail closed 并保留恢复证据，而不是声称恢复或删除一个不确定的名字。若恢复本身在链接后被中断，旧的公共字节与私有备份可能都保留；后续的恢复运行会保留公共目标，并需要显式的人工处理。在支持目录同步的平台上，记录会在旧公共名被退役之前 fsync，且所测试的保证是进程被杀后的恢复；这不是对断电、存储控制器、NFS 或 SMB 持久性的声称。成对流程把其备份保留在私有的交换暂存中。对 `deliver`，pending 日志与锁使严格检查器 fail-closed。可移植的 Node.js 文件系统 API 没有一种路径名 compare-and-swap，能既原子替换既有名字、又拒绝覆盖迟到的主张者：`rename` 只有通过覆盖该主张者才能关闭可见性缺口。

所有权建立后，`deliver` 在渲染前创建日志，并在可恢复的 HTML/伴随文件成对提交期间一直保留它。它只在该提交完成后才移除日志。因此校验、渲染或成对提交失败，或进程中断，都可能留下一个日志。日志是一道安全屏障：当日志或锁路径上存在任何目录条目时（包括不可读文件、符号链接或悬空符号链接），`check`、`browser-check` 与 `visual-check` 都 fail closed。串行运行针对同一物理输出目录的交付；一次尝试必须完成或被恢复后，另一次才能开始。

成功的伴随文件有 `schemaVersion: 1`、`status: "current"`、`command: "deliver"`、唯一的 `receiptId`、图的 `type`、绝对的 `input` 路径、与所检查产物匹配的绝对 `output` 路径，以及规格/产物的 SHA-256 与字节数。检查器把缺失、畸形、不支持或不一致的字段视为无效。它们还拒绝伴随文件符号链接，包括悬空的。检查器把溯源绑定到它实际检查的产物字节，并在报告成功前再次校验该绑定；并发的字节改变会失败。溯源目录条目本身必须是单链接普通文件：当它还有另一个硬链接时，`deliver` 与严格检查以 `delivery/provenance-hardlink-unsupported` fail closed，而不扫描或猜测兄弟名。

若当前经验证的拥有者在旧 HTML 存在之后失败，Archify 会写一个新的 `status: "failed"` 伴随文件，并保留日志直到恢复完成。不可读的旧 HTML 不阻止该标记；其产物 hash 与字节数可能缺席。若伴随文件被锁定或不可写，Archify 保留先前的伴随文件而不是删除证据，且日志阻止检查器信任它。被拒绝的并发、陈旧或无效锁尝试不会写入失败溯源。若所有权丢失，Archify 报告 `delivery/ownership-lost`，不覆盖或移除后继者的产物、溯源、日志或锁，也不声称已记录失败溯源；失败回执可能报告 `provenance: "unrecorded"`。若每条元数据路径都不可用，同样适用未记录状态；没有工具能跨进程保留该事实。恢复元数据路径访问，并在信任输出前完成一次成功的 `deliver`。

没有伴随文件、日志或锁的产物仍受支持，以向后兼容并支持更低层的 `render` 命令。其检查器回执报告 `provenance: "unknown"`；当工作流要求成功交付的产物时，用 `--require-provenance` 把该状态变成非零失败：

```bash
bun bin/archify.mjs check <output.html> --require-provenance
bun bin/archify.mjs browser-check <output.html> --json --require-provenance
```

## 输出路径契约 <a id="output-path-contracts"></a>

Archify 刻意把持久的已编写路径与命令行路径分开：

- 必需的已编写 `meta.output` 是可移植的 POSIX 相对路径，例如 `reports/diagram.html`。它使用 `/`，以非空的 `.html` 基名结尾，且不能包含绝对或盘符相对前缀、URI、反斜杠、空段或点段、控制字符、未配对的 UTF-16 代理项、Windows 备用数据流分隔符或非法文件名字符、结尾的点或空格、DOS 设备名，或超过 255 字节 UTF-8 或 255 码元 UTF-16 上限的组件。它从当前工作目录解析，并在跟随符号链接后仍必须物理地位于该目录内，且目标是 `.html`。持久输出/归档配置文件还保守地拒绝形如 `PROGRA~1` 的 Windows 8.3 短名；描述性的 repo/Git POSIX 路径使用单独的配置文件，不受此限。
- 显式 CLI 输出参数使用当前宿主机的原生语法。它们可以是相对或绝对的，使用原生分隔符，并解析到当前工作目录之外。在 Windows 上，支持普通的盘符绝对、UNC 与相对路径（包括普通的 `.` 与 `..` 导航）。当 Archify 能证明其物理身份时，接受系统解析出的既有文件或目录的 8.3 拼写；此原生别名支持不放松持久输出/归档配置文件对 8.3 形状名的拒绝。扩展长度路径仅限原始、只含反斜杠的 `\\?\C:\...` 与 `\\?\UNC\server\share\...` 形式，且不含点段；设备命名空间、畸形根、盘符相对路径（如 `C:file.html`）、当前盘根（如 `\file.html`）、备用数据流、保留设备名、非法或结尾文件名字符与过长组件都 fail closed。POSIX CLI 路径保留 POSIX 文件名规则，而不继承 Windows 拼写限制。所有宿主机都拒绝 NUL、未配对代理项与超过其支持上限的组件。

这些契约不可互换：显式 CLI 输出不会隐藏无效的持久 `meta.output`（包括缺失值），并且即使 `validate` 不发布到该路径，它也会检查已编写的输出。工作流 v1 到 v2 的迁移可以显式地通过 `migrate workflow old.json new.json --to-schema 2 --output reports/diagram.html` 接收一个可移植的持久替代；该值只写入其单独的、已验证的 v2 目标。此迁移候选例外不修复来源，也不绕过任何非输出的 schema 或编译器错误。对每一次其他修复，向 `meta.output` 添加一个可移植的 POSIX 相对 `.html` 路径；否则不需要改 schema 版本。

对一个完整的第一版候选以及每次修复编辑之后，直接运行 `finalize`。它内嵌的校验在交付前检查候选；只有当聚焦诊断时才用独立的 `validate`。编辑后省略早先的 `--candidate-sha256`，它绑定的是上一个候选。CLI HTML 输出路径必须以 `.html` 结尾（包括符号链接解析之后）。Compare 回执路径必须以 `.json` 结尾。类型不匹配会在写入前以 `output/cli-extension` 或 `output/cli-resolved-extension` 失败。这些检查防止意外的文件类型覆盖；它们不对显式 CLI 目录做沙箱，也不阻止替换预期类型的既有产物。

只有在候选被冻结后才使用最终经验证的交付：

```bash
bun bin/archify.mjs deliver <type> <candidate.json> <output.html> --quality showcase --json
```

Deliver 只读一次规格，把这些确切的字节写入一个同目录的私有候选快照，渲染该快照，运行完整的产物检查器，并且只在所有产物检查通过后才替换目标。JSON 回执包含 `specification` 与 `artifact` 二者的 SHA-256 与字节数。

对普通的代理交接路径，优先使用 finalizer：

```bash
bun bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
```

`finalize` 调用一次经验证的 `deliver`，复用其内嵌的 showcase 校验结果，然后运行严格 `check --require-provenance` 与 `browser-check --require-provenance`。它在第一个失败或跳过的阶段停止，并保留该阶段的完整回执。它的 stdout 是一个精简 JSON 对象，含门控状态、有界的可操作诊断、产物身份与证据路径。同一个精简对象被原子地写入 `<output-stem>.finalize-summary.json`；正常失败修复请用那个文件。完整的阶段回执与耗时仍保留在 `<output-stem>.finalize.json` 中供审计。用 `--out-dir` 时两个文件都写在那里；`--receipt <path.json>` 覆盖完整回执路径，并派生一个不同的 `<path>-summary.json`。只有当精简摘要被截断、其所示 subject 与 evidence 无法识别一次连贯的本地修复时，或当明确要求完整审计证据时，才读完整回执。精简回执报告 `visualReview: "not-requested"`；自动门控不创建图像，也不要求感知复核者。精简 `visualReviewRecommendation` 保留严格检查中正向的交叉与路线迂回度量，使作者无需读完整回执即可应用下面的复核升级。建议不改变机器退出码，也不声称复核已发生。其 `affectedRoutes` 标识交叉对与迂回（各至多八个，带截断标志）；完整严格检查的 `composition.routeReview` 保留所有受影响关系。用这些 ID 在捕获的默认视口中追踪路线。迂回可能包含 `directCorridorBlockers`，标识对齐端点之间的节点。这些是几何复核线索，不是新的校验失败或推断的主路径语义。对被阻塞的主路径或若干条纠缠路线，遵循[架构布局修复](architecture-layout-repair.md)，在微调个别侧或标签之前先重排连通场景。保留每条语义事实；只有当无关位置周边的构图已被接受时才保留它们。

对具有一大块未用前置区域的实测自动架构图，精简回执可能包含 `layoutReviewRecommendation`。其 `composition.leadingSpace` 证据计入节点、边界标题、路线与标签。检查该空间是否有意；若否，在保留含义与用户固定几何的前提下重新摆放连通场景，然后再 finalize 一次。该建议不改变任何门控或退出状态，也不需要截图。固定的画布或不确定的测量不会得到建议。

通过 finalizer 的回执对全部四个门控都是充分证据。仅枚举这些门控或要求每一个都通过，并不需要重放它们的独立命令。只有当请求明确要求单独执行、或聚焦失败诊断需要时，才重放个别命令。

个别命令保持权威且向后兼容。对聚焦诊断、恢复，或只需要一个门控时，直接使用它们。finalize 失败不放松任何门控，也不会把一个被保留的旧产物变成当前成功的交付。

`finalize` 把私有 Chrome 启动与交付、严格检查重叠进行。它只在那些门控通过且当前溯源被校验后才加载产物。浏览器门控保留每个视口、主题与稳定检查；浏览器在完成或更早失败时关闭。其完整阶段回执记录 `execution: "in-process"` 与供重放的等价独立 `command`。用总 finalize 耗时比较性能，因为 Chrome 启动与更早阶段重叠。

> **Chatlo 适配**：Chatlo 上没有桌面 Chrome，无法运行自动浏览器门控。`finalize` 把 `browser-check` 阶段标记为 `delegated`（委派），`visualReview` 为 `delegated-to-chatlo-web_browser`：`validate → deliver → check` 仍全部门控通过。被委派的复核由 Chatlo 内置浏览器（`web_browser` 工具 / `chatlo-browser` 命令）在设备视口下完成，见[自动浏览器证据](#automated-browser-evidence)与 `chatlo-browser-evidence.md`。

成对提交是可恢复的，而不是声称两个文件系统路径原子改变或跨断电持久。日志终结是该提交的一部分：在验证或移除日志时被捕获的失败，在可能且所有权仍当前时回滚被替换的文件。若所有权丢失，旧尝试立即停止重命名、回滚、终结日志、记录失败溯源或清理共享路径。任何私有暂存或可恢复备份仍可用，并由失败诊断标识。若恢复因另一原因失败，失败回执同样标识保留的备份供恢复。进程中断可能把日志、备份或私有暂存留在后面；此时检查器 fail closed。在同一输出上串行重跑 `deliver` 之前，遵循所报告的恢复证据。失败的尝试以非零退出，且绝不调用 opener；它绝不授权收集视觉证据。

若排他创建成功但锁初始化失败，Archify 只在其能力仍标识那个确切条目时，才可能记录失败溯源并移除不完整的锁。替换物被保留。文件系统与清理错误与活动的并发交付分开报告。活动的、陈旧的、未识别的或以其他方式被保留的锁，独立地阻止检查器接受先前的产物。在重试前修复所报告的文件系统错误；若锁路径包含无关数据，则改用另一个物理输出目录。

锁释放是交付完成的一部分。若产物/溯源成对已提交、日志已终结，但匹配的锁无法移除，`deliver` 以 `delivery/lock-release` 退出 1，保留锁，不打印成功回执，也不调用 opener。被保留的锁使严格检查器 fail-closed。只有在成对提交、日志终结与锁释放全部成功后，`deliver` 才可以退出零、打印其成功回执，或运行 `--open`。

在 `deliver` 退出零后运行严格 `check`。只在该严格检查退出零后运行 `browser-check` 或可选的 `visual-check`。失败标记、恢复日志或交付锁会使每个检查器在接受被保留的 HTML 之前失败；报告诊断，并在收集新的浏览器证据前完成一次成功的恢复交付。

交付接口暴露四种独立的声称：

1. `deliver` 证明确定性的产物检查与字节身份。
2. `browser-check` 从确切产物收集所需的自动浏览器证据，不捕获图像。
3. `visual-check` 可选地添加绑定产物截图与一份联系表。
4. 感知视觉复核记录人类或具备读图能力的复核者的判断。

通过一种声称绝不蕴含其他声称。绝不声称确定性回执包含浏览器或感知复核证据。

## 恢复失败的比较 <a id="recovering-a-failed-comparison"></a>

`compare` 把 HTML 产物与其 JSON 回执作为一对提交。若该提交失败，它尝试恢复先前的文件。完整的回滚照常移除临时目录。

若某个先前文件无法恢复，compare 以 `delta/commit-rollback-failed` 非零退出并保留恢复目录。在 JSON 失败回执中，`diagnostics[].evidence.recoveryDirectory` 标识该目录，`recoveryFiles` 列出恢复失败文件的 `{ backup, target }` 路径。人类可读诊断也会打印恢复路径。

解决文件系统错误，检查当前目标，并在重试前把每个所列备份恢复到其对应目标。在两个先前文件都被恢复并校验之前保留恢复目录；它也可能包含被拒绝的候选文件，不得把它们误当作备份。成功的比较与提交前的失败保留其正常清理。

## 自动浏览器证据 <a id="automated-browser-evidence"></a>

`finalize` 对确切的受信 HTML 运行所需的浏览器门控，而不重新渲染或修改它。对聚焦诊断，等价独立命令是：

```bash
bun bin/archify.mjs browser-check <output.html> --json --require-provenance
```

零依赖命令通过 DevTools 管道使用 Chrome/Chromium。它测量 1440×900、1600×1000、1920×1080 与 2048×1320 下的浅色主题包含关系，并在全部四个视口校验所请求的浅色主题、在两个端点校验深色主题，以及 READ/Still 运行时状态。请求的主题若解析为不同主题会以实测证据失败。它创建一个 `<output-stem>.browser-check.json` 回执，不产生截图或联系表。传 `--out-dir <dir>` 把回执放到单独的证据目录。回执绑定产物 SHA-256 与字节数，标识 `evidenceKind: "automated-browser"`，并报告 `visualReview: "not-requested"`。

水平溢出始终失败。正常的文档级垂直滚动只有在渲染器声明契约且文本实测可读时才被接受。自动画布声明 `data-reader-fit="intrinsic-height"`；其自适应 Reader 必须达到其可读宽度并暴露 `data-reader-overflow="authored"`。带显式 `meta.viewBox` 的架构图则声明 `data-diagram-type="architecture"` 与 `data-reader-fit="authored-height"`：其 SVG 坐标、宽高比与既有 Reader 宽度行为保持不变。其完整 SVG 必须留在图面板内，无内部滚动或裁剪，且文档必须允许垂直滚动。回执记录 `verticalScrollAccepted: true` 与 `overflowDisposition: "readable-vertical-scroll"`。缺失或未知的声明、其他模式中的显式 viewBox、不可读文本、水平溢出、裁剪与查看器 chrome 碰撞仍然是失败。不要添加内部图滚动条或隐藏溢出。

交接中的 `browser_evidence` 只记录该自动命令的结果：

- `passed` 映射自退出 0 与回执 `status: "pass"`，在每项必需测量完成并通过之后。
- `failed` 映射自退出 1 与回执 `status: "fail"`，当检查发现缺陷、命令失败，或运行时错误使证据不完整时。
- `skipped` 只映射自退出 2 与回执 `status: "skipped"`，当 Chrome/Chromium 不可用且检查未运行时。

运行时失败留下不完整证据，不得被归一化为 `skipped`。它们不会使已经成功的确定性交付失效。在可行时，在具备浏览器能力的执行上下文中重试环境失败。保持打包传输不变，除非该失败在一个有能力的环境中通过该接缝重现。

溯源失败在浏览器检查前退出，并持久化一个绑定到所尝试产物的失败 browser-check 回执。若失败回执无法写入，诊断会指名该不完整证据。

两个浏览器命令都检查确切已交付的 HTML，不修改也不重新渲染它。

> **Chatlo 适配**：Chatlo 上没有桌面 Chrome，`browser-check` / `visual-check` 的独立命令会报告 `skipped` 与诊断 `viewer/chrome-unavailable`（预期行为）。真正的复核改用 Chatlo 内置浏览器：`web_browser` 打开 `chatlo:///绝对路径`，`screenshot`/`snapshot`，并可选地用 `chatlo-browser act --kind evaluate` 运行 `chatlo-browser-evidence.md` 中的探针（设备视口口径）。内置浏览器视口由系统固定（非 4 个桌面视口）。

## 时序宽度复核 <a id="sequence-width-review"></a>

一次通过的 `finalize` 可能报告 `layoutReviewRecommendation.action: "inspect-sequence-width"`。其 `evidence` 测量固定参与者列在计入消息标签、注释与分段标题之后未用的右侧空间。该建议不添加警告、失败、截图要求或自动几何改变。

对一个新编写、省略 `meta.column_fit` 且没有用户固定列几何的候选，保存候选，只把 `meta.column_fit` 设为 `"spread"`，并用 `--out-dir <folder>/width-review` 重跑一次完整 `finalize`。保持参与者顺序、消息及其 y 位置、标签、注释、来源与画布尺寸。若该尝试失败，恢复候选并用 `--out-dir <folder>/width-restore` finalize 它；报告剩余的布局建议，而不是反复迭代。保留显式固定的布局或已提供的旧候选，并披露该建议而不改动它。该复核关乎水平构图；通过的回执仍不声称感知批准。

## 可选的截图证据 <a id="optional-capture-evidence"></a>

`visual-check` 对请求的或升级的感知复核保持向后兼容：

```bash
bun bin/archify.mjs visual-check <output.html> --summary --require-provenance
```

`--summary` 返回精简 JSON，含所有诊断与到完整回执、联系表及每张截图的绝对路径。对被选定的视觉复核，检查相关截图；截图成功不是感知批准。`--json` 为既有消费者保留完整回执输出。两种模式运行相同检查并保持相同退出状态。若发布后清理失败，摘要保留最终失败诊断与 `publication` 恢复细节；所链接回执记录更早提交的证据。

它执行相同的自动浏览器测量，在 1440×900 与 2048×1320 捕获浅/深截图，并写入四张视口 PNG 伴随文件、一份相对路径 HTML 联系表与一份 JSON 回执。`--out-dir <dir>` 把所有这些伴随文件一起移动。在浏览器中打开该 HTML 联系表，或用图像阅读器检查视口 PNG。其回执报告 `visualReview: "pending"`，因为截图本身不做感知判断。截图与溯源失败遵循下面的所有权规则。

回执、联系表与四张 PNG 构成一个被拥有的证据集。在截图前，`visual-check` 冻结每个所请求的目录条目、其规范写入槽与物理父级，以及目标的缺席/文件状态、类型、设备/inode 身份与模式。硬链接的证据目标不是安全写入目标。所有候选文件都在物理证据目录之下的一个随机私有暂存目录中排他创建；回执最后发布。每个暂存的候选在发布前必须恰好有一个硬链接名。no-clobber 发布链接临时使暂存名与最终名都有链接计数二；解除已验证暂存名的链接必须让最终条目留下链接计数一。意外的外部硬链接 fail closed，且其别名绝不被移除。

Chrome 在一个私有的本地临时目录中检查被捕获产物的一个经身份与内容校验的副本，因此浏览器文件加载不依赖 UNC 或长路径支持。六个发布候选留在证据卷上。两个临时目录都在不递归删除未知内容的情况下清理；被保留的条目包含其恢复位置。

在提交任何东西之前，`visual-check` 立即重新解析并校验完整的六路径集。缺席路径的主张者、既有路径的替换、符号链接或悬空链接重定向、父级拓扑改变、硬链接或不确定身份都以 `viewer/evidence-path-conflict` fail closed。该主张者与每条其他最终证据路径保持不动。清理在重新检查其被捕获身份后，只移除此运行暂存或已发布的条目；被改动或未知的条目被保留。

既有的视觉证据集只有在如下情形才可替换：一份普通 `visual-check` 回执证明对同一产物与证据目录的所有权，且其确切的伴随文件清单与每份既有联系表或 PNG 字节数及 SHA-256 摘要匹配。缺失、畸形、未知、不匹配或不完整的所有权记录绝不授权删除。失败与跳过的运行只有在同一已验证事务中、且该所有权证明成功时，才退役先前的截图/联系表；否则保留所有未知证据并报告 `viewer/evidence-path-conflict`。

当 Chrome 不可用或溯源在浏览器检查前失败时，此规则同样适用：两条路径都不得盲目删除看似陈旧的证据。一个经验证被拥有的集合可以在发布跳过或失败回执之前被可恢复地退役；无主证据保持完整。这些结果不会使已经成功的确定性交付失效，也不会把感知视觉复核变成通过或失败。在可行时，在具备浏览器能力的环境中通过受支持命令重试环境失败。保持打包传输不变，除非该失败在一个有能力的环境中通过该接缝重现。

`browser-check` 对其单个 JSON 回执应用相同的私有快照、身份、所有权与 no-clobber 规则。其命名空间与 `visual-check` 分开，因此仅浏览器的重跑无法移除截图证据。

## 在既有输出路径上的新候选 <a id="a-new-candidate-at-an-existing-output-path"></a>

浏览器证据属于确切的产物字节。在编辑一个其先前 HTML 已有浏览器证据的候选之后，在运行下一次 `finalize` 前选择一个全新的证据目录；这保留了旧回执与截图，避免可避免的所有权冲突重试：

```bash
bun bin/archify.mjs finalize architecture candidate.json diagram.html --quality showcase --repo-root <root> --out-dir diagram.review-2 --json
bun bin/archify.mjs visual-check diagram.html --out-dir diagram.review-2 --summary --require-provenance
```

保持所请求的 HTML 路径稳定。对每个被改动的候选使用新的修订目录，对未变字节的重试保留同一目录。对没有仓库证据的图，省略 `--repo-root`。让命令创建其输出目录。先前未产出 HTML 或浏览器证据的校验失败不需要新目录。绝不移除未知证据来让重试通过。

## 可选打开 <a id="optional-opening"></a>

只有当用户想要立即的本地预览时才添加 `--open`。它在已验证成对提交完成、恢复日志已移除、交付锁已成功释放之后运行。它使用一个参数数组 OS opener，在 macOS 与 Linux 上五秒上限，在 Windows 上 PowerShell 启动十五秒上限。回执记录 `open.status`；失败或不可用的启动尝试还包括归一化的 `open.failure` 细节。对 CI、无人值守代理与非交互环境保持关闭。失败或不支持打开不会使交付失效；其状态只证明本地 opener 调用是否成功。

> **Chatlo 适配**：Chatlo 上没有 `open` / `xdg-open`，`--open` 与 `preview` 不可用。改用 `web_browser` 工具打开产物的 `chatlo:///绝对路径`。

## 最后可用版本实时预览（Last-Good Live Preview） <a id="last-good-live-preview"></a>

仅用于活动的桌面编写循环：

```bash
bun bin/archify.mjs preview <type> <input>.json <output>.html --quality showcase
```

Preview 在回环上监视一个显式输入，把每个稳定摘要绑定到一个私有快照，并且只在既有已验证交付管道通过后才推进。无效、写了一半、被删除或被取代的输入让上一个已验证修订留在屏幕上与磁盘上。相同的字节不重建也不重载。

preview 运行时随零依赖 Skill ZIP 分发，且必须在没有 `node_modules` 时可用。

绝不默认启动它。不要把它用于 CI、无人值守代理、远程分享或移动端使用。`--no-open` 只适用于会打开所打印本地 URL 的用户，或回环测试。交接前用 Ctrl-C 停止它。第一次 Ctrl-C 排空活动交付而不发布它；第二次 Ctrl-C 强制关闭两个交付进程与 HTTP 连接，包括未完成的请求。关闭保留最后一个已验证产物，只移除所有权可被校验的暂存文件。若交付在其回执到达 Preview 之前被中断，未确认的文件与恢复材料可能留在私有暂存目录中；关闭不递归删除未知内容。服务器状态、端口、来源路径、诊断、错误文本与重载令牌绝不进入生成的产物或任何导出。

## 感知复核 <a id="perceptual-review"></a>

自动路径以确定性的浏览器门控结束，并报告 `visual_review: not_requested`。普通生成不需要截图或读图步骤，包括新编写或重新摆放的架构图。感知复核是可选的；对显式请求或具体视觉调查使用它。可能的原因包括：

- 精简 finalizer 因交叉或迂回而包含 `visualReviewRecommendation`（建议性，不是交付门控）；
- 用户明确要求美学或视觉复核；
- 模板、渲染器或查看器改动需要视觉回归证据；
- 新颖的布局或浏览器诊断留下低置信；
- 该运行被选为抽样审计或 dogfood。

对默认的独立桌面查看器，测量 1440×900、1600×1000、1920×1080 与 2048×1320。在每个检查尺寸下要求 `document.documentElement.scrollWidth <= window.innerWidth`。优先 `scrollHeight <= window.innerHeight`；只通过上面定义的 Reader 声明的可读例外接受页面级垂直滚动。在最大的检查视口下，检查渲染后的构图是否有一条显眼的空白下部带：主面板与必要的结论卡片应把可用高度作为一个平衡的整体使用，而不是塌缩成一条浅带。对意外溢出，通过只移除真正冗余的内容或压缩间距来修复已编写的构图，然后再考虑缩小节点、标签或主面板。不要隐藏溢出、裁剪内容、引入内部图滚动条，或为让测量通过而减小节点/标签字号。窄/移动端包含可以保留垂直页面滚动。

对升级复核，在当前已 finalize 的产物上运行 `visual-check`，用具备能力的图像阅读器或人检查其联系表，并检查两个端点主题、默认 READ 视图、线交叉/走廊、标签遮罩、节点/卡片贴合、聚焦/搜索/护照关闭与导出整洁性。该复核是补充性的，绝不改变 `browser_evidence`。不受约束的浏览器一瞥只能支持感知复核。

报告一个真实的可选复核状态：

- `visual_review: not_requested` —— 不适用复核触发条件；这不是视觉验收声称。
- `visual_review: passed` —— 只在检查过渲染产物之后。
- `visual_review: skipped (image reader unavailable)` —— 请求或触发的复核无法运行。
- `visual_review: failed` —— 附具体可见缺陷。

对升级复核，用 `correction_rounds: 0`、`correction_rounds: 1` 或 `correction_rounds: 2`；绝不超过两次聚焦纠正轮。当未请求复核时，用 `correction_rounds: 0`。绝不在未检查产物的情况下报告 `visual_review: passed`。若感知复核改动了候选，重跑 `finalize`，因为先前的规格与产物回执不再是当前的。

## 交接回执 <a id="handoff-receipt"></a>

返回：

```text
diagram_type: architecture|workflow|sequence|dataflow|lifecycle
output: /absolute/path/to/file.html
specification_sha256: <receipt value>
artifact_sha256: <receipt value>
validation: 9/9 showcase, 0 errors, 0 warnings
browser_evidence: passed|failed|skipped
visual_review: not_requested|passed|skipped (image reader unavailable)|failed
correction_rounds: 0|1|2
```

只从最新的、绑定产物的 `browser-check` 回执（通常是 `finalize` 内嵌的阶段）派生 `browser_evidence`。单独记录可选的截图或手工浏览器工作，附其产物绑定、视口/主题范围与观察；绝不改用它或 `visual_review` 覆盖自动状态。

> **Chatlo 适配**：在 Chatlo 上，`finalize` 的 `browser-check` 为 `delegated`，因此 `browser_evidence` 应报告为 `delegated`（或用 `skipped` 并在说明中给出原因），并附内置浏览器复核的实际观察；`visual_review` 只有在确实检查过截图/快照后才可标 `passed`。

打开、preview 状态、分享卡片与其他查看器导出不是校验声称。

finalize 回执发布使用与上面相同的身份绑定、no-clobber 发布器与显式恢复记录。完整与摘要回执必须与候选、产物、交付元数据与浏览器回执不同。它们的目标必须缺席或是单链接普通文件；符号链接回执条目与硬链接目标 fail closed。迟到的或被改动的父级主张者停止发布并保持不动。默认回执名共享物理产物命名空间，并为宿主机文件名上限做有界处理。这两个回执单独发布，而不是作为崩溃原子对；只有完成且通过的命令才是成功交接。
