# 12. 测试、发布与示例

用户脚本是小型部署，但环境差异很大。可靠的发布版本要测试匹配、生命周期、权限、页面结构、网络结果和持久化状态。在开发所用配置文件之外，也要在干净的浏览器配置文件中测试脚本。

## 测试矩阵

| 场景 | 验证内容 | 预期结果 |
| --- | --- | --- |
| 匹配 | 精确协议、主机、路径、查询、哈希、排除项和框架上下文 | 脚本仅在目标页面启动，并具有预期的框架范围。 |
| 新页面加载 | 在配置的 `@run-at` 下首次运行 | 启动具备幂等性，不假设应用已就绪。 |
| SPA 导航 | `pushState`、`replaceState`、后退、前进和离开路由 | 路由 UI 只调和一次，过期 UI 被移除，teardown 时 history 被恢复。 |
| 元素缺失 | 目标永久或暂时不存在 | 页面保持可用，重试有界，失败可观察。 |
| 网络缓慢 | 延迟响应、超时和部分进度 | 加载状态清晰，超时有界，abort 释放请求。 |
| 请求受阻 | 缺少 `@connect`、权限被拒绝、DNS 失败、`4xx`、`5xx`、无效 JSON | 脚本区分权限、传输、服务器和解析失败，不泄露数据。 |
| 多标签页 | 同一脚本在两个标签页运行，以及远程设置变化 | 变更监听器更新有效状态，不假设事务，也不复制 UI。 |
| 重新加载 | 已存在面板、监听器、计时器或请求时重新加载 | 新一轮运行不会保留过期监听器、观察器、计时器或重复标记。 |
| 权限禁用 | 禁用 grant 或拒绝扩展提示 | 脚本报告不支持或被阻止的行为，并让页面保持可用。 |
| 更新迁移 | 安装旧存储 schema，然后升级并遇到未知的未来数据 | 已知数据确定性迁移；不支持的未来数据得到保留。 |

对每一行记录浏览器、Tampermonkey 版本、脚本版本、路由、预期可见状态和控制台结果。脚本添加 UI 时，加入键盘焦点、名称、禁用状态、可读状态消息和对比度的无障碍检查。

## 发布元数据和变更日志

每次行为或权限变化都更新 `@version`。将 `@match`、`@grant`、`@connect`、`@require`、`@resource`、存储 schema 和外部请求形状的变化视为发布说明，而不是实现细节。解释新的权限提示，以及任何用户可见的迁移或同意步骤。

变更日志条目应包含：

- 发布版本和日期。
- 新增、变更、修复和移除的行为。
- 新增或移除的 grant、主机、资源和依赖。
- 存储 schema 变化，以及迁移或回滚行为。
- 支持的浏览器和 Tampermonkey 版本说明。
- 已知限制和可复现的恢复步骤。

使用稳定的 `@namespace`，并且只通过经过审查的分发路径更新元数据。发布前验证更新和下载 URL。不要发布指向未经审查的可变依赖或过宽权限模式的脚本。

## 回滚和迁移

保留上一个已知良好的脚本，并明确回滚说明。回滚不能在没有明确降级策略的情况下覆盖较新 schema 写入的数据。迁移无法理解未来 schema 时，保留原始值并使用安全的内存默认值。在干净配置文件和包含格式错误值的配置文件中都测试升级与回滚。

发布前验证失败的网络请求、缺失选择器、被拒绝权限和更新迁移各自产生可见且可恢复的状态。特权操作应默认拒绝执行（fail closed）：目标或输入无法验证时，不得执行请求、下载或账户操作。

## 完整示例：静态增强

此脚本只使用浏览器 API，因此声明 `@grant none`。它精确匹配产品路由，在 `[data-product-actions]` 旁边添加一个面板，并使用标记和 `replaceChildren` 保持幂等性。

```js
// ==UserScript==
// @name         Static Product Action Panel
// @namespace    https://userscripts.example.com/static-product-panel
// @version      1.0.0
// @match        https://shop.example.com/products/*
// @grant        none
// @noframes
// @run-at       document-idle
// ==/UserScript==

(() => {
  'use strict';

  const panelSelector = '[data-tm-static-product-panel]';
  const hostSelector = '[data-product-actions]';

  function showMessage(panel, message, state) {
    panel.replaceChildren();
    const status = document.createElement('p');
    status.textContent = message;
    status.dataset.state = state;
    panel.append(status);
  }

  function createPanel(host) {
    if (!host.parentElement) return;
    const panel = document.createElement('section');
    panel.dataset.tmStaticProductPanel = 'true';
    panel.setAttribute('aria-label', 'Product actions');

    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Check product availability';
    button.addEventListener('click', () => {
      const productId = document.querySelector('[data-product-id]')?.getAttribute('data-product-id');
      if (!productId || productId.length > 100) {
        showMessage(panel, 'Product information is unavailable.', 'error');
        return;
      }
      showMessage(panel, `Product ${productId} is ready for review.`, 'ready');
    });

    panel.append(button);
    host.insertAdjacentElement('afterend', panel);
  }

  const host = document.querySelector(hostSelector);
  if (!host) {
    console.warn('[static-product-panel] action host not found');
    return;
  }
  if (host.nextElementSibling?.matches(panelSelector)) return;
  createPanel(host);
})();
```

## 完整示例：SPA 增强

此控制器在安装任何资源前使用跨执行哨兵。它观察稳定文档根节点，只补丁 history 一次，处理 `popstate`，对刷新进行防抖，并在路由变化时移除自己的面板。它不会在每次刷新或脚本重新进入时添加新的观察器或点击监听器。

```js
// ==UserScript==
// @name         SPA Enhancement Example
// @namespace    https://userscripts.example.com/spa-enhancement
// @version      1.0.0
// @match        https://app.example.com/orders/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(() => {
  'use strict';

  const instanceKey = '__tmSpaEnhancementInstance__';
  if (window[instanceKey]?.active === true) return;

    const state = {
      running: true,
      observer: null,
      refreshTimer: null,
      panel: null,
      panelOwned: false,
      originalPushState: history.pushState,
      originalReplaceState: history.replaceState,
      wrappedPushState: null,
      wrappedReplaceState: null,
  };
  const panelSelector = '[data-tm-spa-enhancement]';

  function onFeatureRoute() {
    return location.pathname.startsWith('/orders/');
  }

  function removePanel() {
    if (state.panelOwned) state.panel?.remove();
    state.panel = null;
    state.panelOwned = false;
  }

  function scheduleRefresh() {
    if (!state.running || state.refreshTimer !== null) return;
    state.refreshTimer = window.setTimeout(() => {
      state.refreshTimer = null;
      refresh();
    }, 75);
  }

  function createPanel(host) {
    const panel = document.createElement('aside');
    panel.dataset.tmSpaEnhancement = 'true';
    panel.textContent = 'Order helper active';
    host.append(panel);
    state.panel = panel;
    state.panelOwned = true;
  }

  function refresh() {
    if (!state.running || !onFeatureRoute()) {
      removePanel();
      return;
    }

    const existing = document.querySelector(panelSelector);
    if (existing) {
      if (!(state.panelOwned && state.panel === existing)) {
        state.panel = null;
        state.panelOwned = false;
      }
      return;
    }

    const host = document.querySelector('[data-orders-toolbar]');
    if (!host) return;
    createPanel(host);
  }

  function wrapHistoryMethod(original) {
    return function wrappedHistoryMethod(...args) {
      const result = original.apply(this, args);
      scheduleRefresh();
      return result;
    };
  }

  const instanceRecord = { active: true, stop };
  window[instanceKey] = instanceRecord;

  state.wrappedPushState = wrapHistoryMethod(state.originalPushState);
  state.wrappedReplaceState = wrapHistoryMethod(state.originalReplaceState);
  history.pushState = state.wrappedPushState;
  history.replaceState = state.wrappedReplaceState;
  window.addEventListener('popstate', scheduleRefresh);
  state.observer = new MutationObserver(scheduleRefresh);
  if (document.documentElement) {
    state.observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  refresh();

  function stop() {
    if (!state.running) return;
    state.running = false;
    instanceRecord.active = false;
    state.observer?.disconnect();
    if (state.refreshTimer !== null) window.clearTimeout(state.refreshTimer);
    window.removeEventListener('popstate', scheduleRefresh);
    window.removeEventListener('pagehide', stop);
    if (history.pushState === state.wrappedPushState) history.pushState = state.originalPushState;
    if (history.replaceState === state.wrappedReplaceState) history.replaceState = state.originalReplaceState;
    removePanel();
    if (window[instanceKey] === instanceRecord) delete window[instanceKey];
  }

  window.addEventListener('pagehide', stop, { once: true });
})();
```

生产脚本应与可能修改相同方法的其他代码协调 history 所有权，并避免恢复其他参与者后来安装的包装器。当路由宿主已知会稍后渲染时，加入有界重试，并在 `stop()` 中取消这些计时器。

## 完整示例：跨源数据面板

此示例从一个获准主机请求经过验证的 JSON 摘要。它使用超时、状态和 schema 检查、安全文本渲染以及 abort 句柄。它只存储非敏感的显示偏好，绝不向页面暴露凭据。

```js
// ==UserScript==
// @name         Cross-Origin Data Panel
// @namespace    https://userscripts.example.com/cross-origin-panel
// @version      1.0.0
// @match        https://app.example.com/dashboard/*
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_xmlhttpRequest
// @connect      api.example.com
// ==/UserScript==

(() => {
  'use strict';

  const settingsKey = 'cross-origin-panel.compact';
  const apiOrigin = 'https://api.example.com';
  const apiPath = '/v1/summary';
  const MAX_RESPONSE_BYTES = 1_000_000;
  let requestHandle = null;
  let requestGeneration = 0;
  let panel = null;
  let lifecycleStopped = false;
  let removalObserver = null;
  let pagehideHandler = null;

  let host = document.querySelector('[data-dashboard-toolbar]');
  if (!host || host.querySelector('[data-tm-cross-origin-panel]')) return;

  function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  function readCompactSetting() {
    try {
      return GM_getValue(settingsKey, false) === true;
    } catch (error) {
      console.error('[cross-origin-panel] setting read failed', error);
      return false;
    }
  }

  function writeCompactSetting(value) {
    try {
      GM_setValue(settingsKey, value === true);
      return true;
    } catch (error) {
      console.error('[cross-origin-panel] setting write failed', error);
      return false;
    }
  }

  function parseSummary(value) {
    if (!isRecord(value) || !Number.isInteger(value.count) || value.count < 0 || value.count > 100000) {
      throw new Error('Invalid summary response');
    }
    return { count: value.count };
  }

  function isApprovedFinalUrl(response) {
    if (typeof response.finalUrl !== 'string') return false;
    try {
      const finalUrl = new URL(response.finalUrl);
      return finalUrl.origin === apiOrigin && finalUrl.pathname === apiPath;
    } catch {
      return false;
    }
  }

  function hasJsonContentType(response) {
    if (typeof response.responseHeaders !== 'string') return true;
    const contentTypeLine = response.responseHeaders
      .split(/\r?\n/)
      .find((line) => /^content-type\s*:/i.test(line));
    if (!contentTypeLine) return true;
    const contentType = contentTypeLine
      .slice(contentTypeLine.indexOf(':') + 1)
      .trim()
      .split(';', 1)[0]
      .toLowerCase();
    return contentType === 'application/json' || contentType.endsWith('+json');
  }

  function teardown() {
    if (lifecycleStopped) return;
    lifecycleStopped = true;
    requestGeneration += 1;
    const handle = requestHandle;
    requestHandle = null;
    try {
      handle?.abort();
    } catch (error) {
      console.error('[cross-origin-panel] request teardown failed', error);
    }
    removalObserver?.disconnect();
    removalObserver = null;
    if (pagehideHandler !== null) {
      window.removeEventListener('pagehide', pagehideHandler);
      pagehideHandler = null;
    }
    if (panel !== null && host !== null && panel.parentElement === host) panel.remove();
    panel = null;
    host = null;
  }

  function isPanelAttached() {
    return !lifecycleStopped && panel !== null && host !== null && panel.isConnected && host.isConnected;
  }

  function render(targetPanel, message, state) {
    if (!isPanelAttached()) return false;
    targetPanel.replaceChildren();
    const status = document.createElement('p');
    status.textContent = message;
    status.dataset.state = state;
    targetPanel.append(status);
    return true;
  }

  function loadSummary(targetPanel) {
    if (!isPanelAttached()) {
      teardown();
      return;
    }
    if (requestHandle !== null) {
      render(targetPanel, 'A summary request is already in progress.', 'loading');
      return;
    }
    if (typeof GM_xmlhttpRequest !== 'function') {
      render(targetPanel, 'Cross-origin requests are unavailable in this userscript.', 'error');
      return;
    }

    const url = new URL(apiPath, apiOrigin);
    if (url.origin !== apiOrigin || url.pathname !== apiPath) {
      render(targetPanel, 'The API URL is outside the approved endpoint.', 'error');
      return;
    }
    const requestId = ++requestGeneration;
    let callbackCompleted = false;

    function finishCurrentRequest() {
      if (requestId !== requestGeneration) return false;
      requestHandle = null;
      callbackCompleted = true;
      if (!isPanelAttached()) {
        teardown();
        return false;
      }
      return true;
    }

    render(targetPanel, 'Loading summary...', 'loading');
    try {
      const handle = GM_xmlhttpRequest({
        method: 'GET',
        url: url.href,
        timeout: 8000,
        headers: { Accept: 'application/json' },
        onload(response) {
          if (!finishCurrentRequest()) return;
          if (response.status < 200 || response.status >= 300) {
            render(targetPanel, `Service returned HTTP ${response.status}.`, 'error');
            return;
          }
          if (!isApprovedFinalUrl(response)) {
            render(targetPanel, 'The response final URL is outside the approved endpoint.', 'error');
            return;
          }
          if (!hasJsonContentType(response)) {
            render(targetPanel, 'The service returned a non-JSON response.', 'error');
            return;
          }
          try {
            const raw = response.responseText;
            if (typeof raw !== 'string') {
              render(targetPanel, 'The service returned a non-text response.', 'error');
              return;
            }
            const responseBytes = new TextEncoder().encode(raw).byteLength;
            if (responseBytes > MAX_RESPONSE_BYTES) {
              render(targetPanel, 'The service response is too large to process safely.', 'error');
              return;
            }
            const summary = parseSummary(JSON.parse(raw));
            render(targetPanel, `There are ${summary.count} items.`, 'ready');
          } catch {
            render(targetPanel, 'The service returned an invalid response.', 'error');
          }
        },
        onerror() {
          if (!finishCurrentRequest()) return;
          render(targetPanel, 'The service could not be reached.', 'error');
        },
        ontimeout() {
          if (!finishCurrentRequest()) return;
          render(targetPanel, 'The service timed out. Try again later.', 'error');
        },
        onabort() {
          finishCurrentRequest();
        },
      });
      if (!callbackCompleted && requestId === requestGeneration) requestHandle = handle;
    } catch (error) {
      if (finishCurrentRequest()) {
        render(targetPanel, 'The request could not be started. Check permissions and try again.', 'error');
      }
      console.error('[cross-origin-panel] request start failed', error);
    }
  }

  panel = document.createElement('section');
  panel.dataset.tmCrossOriginPanel = 'true';
  panel.dataset.compact = String(readCompactSetting());

  const refreshButton = document.createElement('button');
  refreshButton.type = 'button';
  refreshButton.textContent = 'Refresh summary';
  refreshButton.addEventListener('click', () => {
    if (lifecycleStopped || panel === null) return;
    loadSummary(panel);
  });

  const compactButton = document.createElement('button');
  compactButton.type = 'button';
  compactButton.textContent = 'Toggle compact view';
  compactButton.addEventListener('click', () => {
    if (lifecycleStopped || panel === null) return;
    const nextValue = panel.dataset.compact !== 'true';
    if (writeCompactSetting(nextValue)) {
      panel.dataset.compact = String(nextValue);
    }
  });

  panel.append(refreshButton, compactButton);
  host.append(panel);
  pagehideHandler = teardown;
  window.addEventListener('pagehide', pagehideHandler, { once: true });
  removalObserver = new MutationObserver(() => {
    if (!isPanelAttached()) teardown();
  });
  if (document.documentElement) {
    removalObserver.observe(document.documentElement, { childList: true, subtree: true });
  }
  loadSummary(panel);
})();
```

示例严格要求 `response.finalUrl` 存在，并且匹配获准来源和 `/v1/summary` 路径；只有经过明确审查的重定向策略才能改变这一点。当 `responseHeaders` 提供 `Content-Type` 时，它必须标识 JSON；body 在解析前受 `MAX_RESPONSE_BYTES` 限制。每个回调只有在面板和宿主仍然连接时才完成当前代数，因此脱离的面板不会被渲染。移除观察器和 `pagehide` 处理器都会调用同一个 teardown；该 teardown 增加 `requestGeneration`、abort 活动句柄、断开观察器、移除 pagehide 监听器、仅在脚本拥有的面板仍附着于脚本拥有的宿主时移除面板，并清空面板和宿主引用。teardown 后回调直接返回，不再渲染。示例有意不发送页面内容或访问 token。经过认证的部署必须定义 API 如何认证请求、cookies 是否合适，以及需要什么用户同意；不要只是为了让样例看起来能运行就添加凭据。

## 发布审查清单

- [ ] 完整矩阵覆盖匹配、加载、导航、DOM 缺失、网络延迟、权限阻止、标签页、重新加载和迁移。
- [ ] 示例使用带语言标签的代码围栏、精确元数据、最小 grant 和安全输出。
- [ ] SPA 控制器不会复制观察器、路由监听器、history 包装器或 UI。
- [ ] 跨源请求在解析前验证最终来源/路径、可用时的 content type、有界响应大小、状态、响应形状、超时、abort 和用户可见错误。
- [ ] 跨源面板 teardown 观察面板/宿主移除，增加请求代数，abort 活动句柄，断开移除观察器，移除 pagehide 监听器，从脚本拥有的宿主移除仍附着的脚本面板并清空 DOM 引用；teardown 后回调不能渲染。
- [ ] 存储只包含所需的非敏感状态，并具有迁移策略。
- [ ] 发布元数据、变更日志、依赖完整性和回滚说明已经审查。
- [ ] 可以恢复已知良好版本，且不会销毁较新的存储数据。

## 官方参考

- [Tampermonkey 文档](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey 常见问题](https://www.tampermonkey.net/faq.php?locale=en)
- [Tampermonkey `@version`](https://www.tampermonkey.net/documentation.php?locale=en&q=version)
- [Tampermonkey `@updateURL` 和 `@downloadURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url)
- [Tampermonkey `GM_xmlhttpRequest`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_xmlhttpRequest)
- [Tampermonkey `@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)
- [Tampermonkey 存储 API](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values)
- [MDN `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [MDN History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)
