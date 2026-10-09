# 01. 可重复的用户脚本工作流

可靠的用户脚本始于一份小而明确的契约。在编写选择器或调用 `GM_*` API 前，先确认脚本在哪里运行、会改变什么、由谁负责，以及如何停止。目标是让脚本在页面、URL、浏览器或 Tampermonkey 配置发生变化时仍然易于理解。

本章介绍规划。精确的元数据、运行时、DOM、SPA 和存储细节请参阅后续章节。

## 1. 发现需求

把请求转化为可观察的行为：

- 哪个用户操作会启动行为？
- 哪个可见结果代表成功？
- 哪些数据可以读取、修改、存储或发送到其他地方？
- 哪些内容绝不能修改？
- 目标元素、值或服务不可用时应该怎样处理？
- 这是一次性增强、会随路由重复运行的功能，还是后台同步任务？

编写可以在浏览器中检查的验收标准。例如，“为每个订单行添加一个操作”可测试；“改善订单管理”则不可测试。加入空结果、格式错误的响应、权限拒绝和页面尚未完全加载等负面情况。

只要浏览器 API 足够，就使用浏览器 API 进行页面交互。Tampermonkey API 是浏览器环境的扩展，而不是让每个操作都获得特权的理由。DOM 查询、事件监听器、`MutationObserver`、`URL`、`URLSearchParams`、`fetch` 和 `localStorage` 都是浏览器 API。`GM_getValue`、`GM_addStyle`、`GM_xmlhttpRequest` 和 `unsafeWindow` 等 API 是 Tampermonkey 功能，需要有意识地作出元数据或兼容性决策。

## 2. 分析 URL 和框架

在选择 `@match` 前记录 URL 范围：

1. 列出实际需要的协议、主机、子域名和路径。
2. 确定查询字符串是否会改变行为。`@match` 不按查询字符串筛选，因此查询检查应放在代码中。
3. 确认功能属于顶层文档、同源框架，还是跨源框架。
4. 检查导航是否会在不完整重新加载的情况下改变 `location.href`。这在单页应用中很常见，需要观察路由。
5. 确定是否适合使用 `@noframes`。仅当顶层文档是目标时使用它。

优先选择精确模式，例如 `https://app.example.com/orders/*`，而不是 `*://*/*`。宽泛模式会增加执行、审查、隐私和维护风险。参阅 [Tampermonkey `@match` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:match) 和 [Tampermonkey `@noframes` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:noframes)。

## 3. 建模页面状态

不要把第一次成功的 DOM 查询当作应用已就绪的证明。描述重要状态：

- **加载中：** 文档或所需宿主尚不存在。
- **就绪：** 目标存在，并且具备功能所需的数据。
- **空：** 目标存在，但没有可用记录。
- **更新中：** 应用正在替换或追加内容。
- **不可用：** 页面处于不支持的路由、用户已登出，或者所需权限或服务失败。
- **离开中：** 文档正在被丢弃，监听器、计时器、样式和所有权节点必须释放。

每种状态都需要明确行为。有界重试可以将“加载中”推进到“就绪”。幂等刷新可以处理“更新中”。错误消息或静默不操作可以处理“不可用”。即使启动在中途失败，teardown 也必须让“离开中”保持安全。

`@run-at` 选择最早的注入机会，而不是应用就绪时间。`document-end` 和 `document-idle` 不代表 SPA 已经完成路由渲染。参阅 [Tampermonkey `@run-at` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)。

## 4. 分配数据所有权

对于每个值，说明它由谁拥有以及应存活多久：

| 数据 | 所有者 | 生命周期 | 安全处理 |
| --- | --- | --- | --- |
| 当前按钮状态 | 脚本实例 | 直到路由变化或 teardown | 保存在内存中；目标消失时重置 |
| 用户偏好 | 用户脚本 | 跨重新加载和标签页 | 使用带命名空间的 Tampermonkey 存储，并在读取时验证 |
| 页面记录 | 页面应用 | 直到其变化 | 只读取所需内容；不要假设对象形状稳定 |
| 远程响应 | 请求操作 | 直到消费完成 | 使用前验证状态、内容类型、大小和字段 |
| 脚本创建的 DOM 节点 | 脚本 | 直到 teardown 或离开路由 | 标记节点，只移除脚本拥有的节点 |

不要持久化 DOM 节点、事件处理器、promise 或任意页面对象。持久化小型的带版本数据结构。除非有经过审查的特定保留理由，否则不要将机密和敏感页面数据放入存储或日志。

## 5. 规划生命周期和 teardown

把脚本视为资源所有者。列出启动创建的每项资源：

- DOM 节点和样式元素
- 事件监听器和 `MutationObserver` 实例
- 计时器和待处理的重试句柄
- history 方法补丁
- Tampermonkey 存储监听器
- 网络请求和 abort signal
- 菜单命令、标签页或通知

为每项资源记录清理操作。让启动具备幂等性，使重复调用不会复制面板、监听器、计时器或请求。让 teardown 能容忍部分初始化：较早操作失败时，可选资源可能尚不存在。

## 6. 规划权限

从不使用特权 API 开始。只有当浏览器 API 无法满足需求，或 Tampermonkey API 提供了所需能力时，才添加一个 `@grant`。例如：

- 普通 DOM 操作使用 `document.createElement` 和 `textContent`；不需要 Tampermonkey grant。
- 使用 `GM_addStyle` 注入由 Tampermonkey 管理的样式；声明 `@grant GM_addStyle`。
- 使用 `GM_getValue` 和 `GM_setValue` 实现用户脚本范围的持久化；声明对应 grant。
- 仅在明确需要跨源请求时使用 `GM_xmlhttpRequest`；同时声明 `@grant GM_xmlhttpRequest` 和范围狭窄的 `@connect` 域名。
- 只有需要直接访问页面 JavaScript 时才使用 `unsafeWindow`；声明 `@grant unsafeWindow` 并记录信任边界。

让 `@require`、`@resource` 和 `@sandbox` 的决策在规划中可见。固定外部依赖版本，审查其源代码，并在功能依赖特定版本时说明最低 Tampermonkey 版本。[Tampermonkey `@grant` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)描述了白名单行为和 `@grant none` 的特殊含义。

## 7. 使用渐进增强

当增强功能无法运行时，脚本应让页面保持可用：

1. 检测所需能力和目标元素。
2. 检测失败时，不要移除或重写无关页面内容。
3. 添加具有清晰可访问名称和键盘行为的控件。
4. 尽可能保留原始页面操作。
5. 为用户触发的失败显示可操作错误；为瞬时失败使用有界且可观察的恢复路径。
6. 可选数据或样式加载时不要阻塞页面。

修改页面内容时，优先使用 `textContent`、明确属性和 DOM API。在验证之前，把页面文本、URL 参数、存储值和远程响应视为不可信输入。不要用这些值构造可执行 HTML 或 JavaScript。

## 8. 可重复的实现顺序

对每个功能使用以下顺序：

1. 编写验收标准和不支持的情况。
2. 选择最窄的 `@match`、框架策略和 `@run-at`。
3. 定义数据所有权、持久化和错误行为。
4. 起草最小 `@grant` 集合，并移除代码未使用的内容。
5. 实现用于检测和安全 DOM 更新的小型浏览器 API 辅助函数。
6. 当页面可以不重新加载而发生变化时，让 `start`、`refresh` 和 `stop` 具备幂等性。
7. 仅针对已知的瞬态条件添加有界重试。
8. 覆盖初始加载、重新加载、路由变化、空状态、格式错误输入、权限阻止和 teardown。
9. 发布前审查元数据和链接。记录浏览器及 Tampermonkey 版本假设。

## 规划模板

在实现非简单脚本前，将此模板复制到设计说明中：

```md
# Feature: <short name>

## Scope
- Pages: <exact hosts and paths>
- Frames: <top-level only / named frame / matching frames>
- Route changes: <yes/no; how detected>
- Browser and Tampermonkey versions tested: <versions>

## Behavior
- Trigger: <user or page event>
- Success: <observable result>
- Unsupported or unavailable: <quiet no-op / visible error / fallback>

## State and ownership
- In-memory state: <values and reset points>
- Persistent state: <keys, schema version, defaults>
- Page-owned nodes: <read-only inputs>
- Script-owned nodes: <markers and cleanup>

## Permissions
- Metadata: <@match, @noframes, @run-at, @sandbox>
- Grants: <each @grant and why>
- External code or data: <@require, @resource, @connect, or none>

## Lifecycle
- start: <initialization and readiness check>
- refresh: <route or DOM update behavior>
- stop: <listeners, observers, timers, requests, nodes, styles>

## Verification
- Initial load: <steps>
- Dynamic update: <steps>
- Failure and recovery: <steps>
- Teardown: <steps>
```

## 完成定义

- [ ] 目标主机、路径、协议和框架行为明确。
- [ ] 功能具有可观察的验收标准，并记录了不支持的状态。
- [ ] 页面状态和应用就绪状态没有仅凭 `@run-at` 推断。
- [ ] 每份状态都有所有者、生命周期、验证规则和持久化决策。
- [ ] `@grant` 列表只包含脚本使用的 API，并且每次使用都有理由。
- [ ] 外部依赖和网络域名已固定或严格声明并完成审查。
- [ ] DOM 变更使用空值检查、安全文本或属性 API 以及稳定标记。
- [ ] 重新进入和刷新具备幂等性；重试有界。
- [ ] teardown 释放每个监听器、观察器、计时器、请求、存储监听器、样式和所有权节点。
- [ ] 已执行初始加载、重新加载、路由变化、空状态、格式错误输入、权限失败和 teardown。
- [ ] 已说明浏览器和 Tampermonkey 的版本特定行为。

## 官方参考

- [Tampermonkey 文档](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey `@match`](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:match)
- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [MDN Web API](https://developer.mozilla.org/en-US/docs/Web/API)
