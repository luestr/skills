# 11. 调试与兼容性

从外向内调试用户脚本。先证明 Tampermonkey 匹配并启动脚本，再证明脚本到达预期的路由和生命周期节点，最后才调试选择器、权限、网络行为、沙箱边界或浏览器差异。单个控制台错误可能是更早不匹配的症状，因此要保持稳定的诊断顺序。

## 诊断顺序

1. **脚本未运行：** 确认脚本已启用、已安装、未被排除，并获准在当前网站运行。检查 Tampermonkey 面板和页面扩展指示器。
2. **页面不匹配：** 比较精确的协议、主机、端口、路径、查询、哈希、框架和 `@match` 模式。匹配某个主机不代表每条该主机上的路由都符合目标。
3. **时机：** 检查 `@run-at`，但不要把 `document-end` 或 `document-idle` 理解为应用就绪。目标可能由框架稍后渲染。
4. **选择器：** 检查实时 DOM，验证选择器的范围和拼写，并检查脚本找到节点后页面是否替换了它。
5. **生命周期：** 对 SPA 验证 `pushState`、`replaceState`、`popstate`、DOM 观察、防抖、重试上限和清理。确认路由变化后 UI 不会复制。
6. **权限：** 将每个 `GM_*` 调用与其 `@grant` 对照，检查 Tampermonkey 提示或扩展权限是否已禁用。
7. **跨源：** 验证 `@connect`、精确请求主机、状态处理、超时、响应形状和服务可用性。原生浏览器请求的 CORS 行为与 `GM_xmlhttpRequest` 不同。
8. **CSP：** 确定失败属于页面上下文脚本注入、资源被阻止还是普通 DOM 操作。不要假设可以或安全地修改 CSP。
9. **沙箱：** 检查代码是否需要页面全局对象、`unsafeWindow`、桥接或版本特定的 `@sandbox` 模式。在改变执行上下文前先缩小桥接范围。
10. **iframe：** 检查目标位于顶层文档还是框架、是否适用 `@noframes`，以及框架是否同源。
11. **浏览器特定行为：** 在每个支持的浏览器中复现，并记录其版本、Tampermonkey 版本、扩展模式、权限提示和控制台输出。

这个顺序可以防止把缺少 `@match` 误诊为选择器失败，也可以防止把权限阻止误认为服务器中断。

## 控制台位置和安全诊断

使用与执行上下文对应的控制台。页面控制台日志可能看不到用户脚本异常，用户脚本沙箱日志也可能看不到页面上下文桥接错误。记录当前 URL、脚本版本、路由和安全状态摘要。不要将 token、cookies、完整页面文本或原始响应 body 粘贴到问题报告中。

```js
const DEBUG = false;

function log(level, message, details) {
  if (!DEBUG) return;
  const safeDetails = details === undefined ? '' : details;
  const method = typeof console[level] === 'function' ? console[level] : console.debug;
  method.call(console, `[product-helper] ${message}`, safeDetails);
}

function reportStartupFailure(error) {
  log('error', 'startup failed', {
    href: location.href,
    message: String(error?.message || error),
  });
}
```

已发布脚本默认关闭此包装器。如果有持久化调试设置，应验证它，并提供菜单命令或明确用户操作来启用。需要扩展介导日志时可以使用 `GM_log`，但它需要 `@grant GM_log`，且仍然只能接收经过脱敏的数据。

## 检查 `GM_info`

`GM_info` 适合诊断面板或临时报告。它可以显示有助于解释兼容性差异的脚本名称、版本、处理器和模式信息。使用目标环境支持的 API 形式调用时，声明 `@grant GM_info`，不要用元数据作授权决策。

```js
// ==UserScript==
// @name         Compatibility Probe
// @namespace    https://userscripts.example.com/compatibility-probe
// @version      1.0.0
// @match        https://app.example.com/*
// @grant        GM_info
// ==/UserScript==

(() => {
  'use strict';

  const info = typeof GM_info === 'object' && GM_info !== null ? GM_info : null;
  console.info('[compatibility-probe]', {
    scriptVersion: info?.script?.version || 'unknown',
    handler: info?.scriptHandler || 'unknown',
    downloadMode: info?.downloadMode || 'unknown',
    browser: navigator.userAgent,
  });
})();
```

不同 API 形式和处理器的元数据形状可能不同。使用可选访问；字段缺失时显示 `unknown`，不要让脚本崩溃。

## 功能检测和版本说明

功能检测应测试脚本将使用的操作，而不只是全局名称。例如，使用回调 API 前检查 `typeof GM_xmlhttpRequest === 'function'`，使用 `GM.xmlHttpRequest` 前检查确切的命名空间函数。还要验证元数据 grant、`@connect` 主机和浏览器权限；函数已定义不能证明操作获准。

在依赖它的代码附近记录版本特定行为。当前 Tampermonkey 文档将 `GM_getValues`、`GM_setValues` 和 `GM_deleteValues` 等批量存储 API 标记为 `5.3+`；将 `@sandbox` 标记为 `4.18+`，某些请求或下载选项还有更晚的构建标签。选择最低版本并测试；仅当产品实际支持旧安装时，才提供更简单的单键或浏览器 API 路径。

```js
function getRequestApi() {
  if (typeof GM_xmlhttpRequest === 'function') {
    return { kind: 'callback', request: GM_xmlhttpRequest };
  }
  if (typeof GM === 'object' && typeof GM.xmlHttpRequest === 'function') {
    return { kind: 'promise', request: GM.xmlHttpRequest };
  }
  return null;
}

const requestApi = getRequestApi();
if (!requestApi) {
  console.error('[compatibility] no supported request API is available');
}
```

如果这会改变 CORS、凭据或隐私行为，不要从获准的跨源请求悄然回退到页面 `fetch`。显示不支持状态消息，并记录缺少的能力。

## 错误复现记录

对每次失败记录：

- 浏览器和版本、Tampermonkey 版本、脚本版本及操作系统。
- 精确 URL、顶层框架或 iframe 上下文，以及页面是新加载还是在 SPA 内导航。
- 预期状态、观察到的状态、控制台位置和第一个相关错误。
- 扩展是否启用、匹配规则是否变化，或权限提示是否被忽略。
- 不包含私有页面数据的最小复现步骤。

修改元数据后重新加载，因为匹配和权限在脚本启动时评估。存储设置或过期 grant 可能影响结果时，使用干净配置文件或新安装脚本进行测试。测试迁移代码前保存当前设置 schema 的安全导出。

## 调试审查清单

- [ ] 首先检查了匹配、启用状态、排除项、框架范围和精确 URL。
- [ ] 将时机和 SPA 生命周期与选择器正确性分开测试。
- [ ] 根据失败调用检查了每个 API grant 和 `@connect` 主机。
- [ ] 控制台输出标识执行上下文，并隐藏敏感数据。
- [ ] `GM_info` 是可选的，且只用于诊断。
- [ ] 功能检测检查实际 API 形式，不隐藏权限失败。
- [ ] 版本标签和最低支持版本记录在依赖代码附近。
- [ ] CSP、沙箱、iframe 和浏览器特定失败有独立复现。
- [ ] 失败会让页面保持可用，并说明下一步安全操作。

## 官方参考

- [Tampermonkey 常见问题：控制台输出](https://www.tampermonkey.net/faq.php?locale=en&q=Q600)
- [Tampermonkey `GM_info`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_info)
- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey `@sandbox`](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey `@noframes`](https://www.tampermonkey.net/documentation.php?locale=en&q=noframes)
- [Tampermonkey 常见问题：脚本异常执行](https://www.tampermonkey.net/faq.php?locale=en&q=Q405)
- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
