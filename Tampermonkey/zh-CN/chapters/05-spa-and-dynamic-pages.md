# 05. SPA 与动态页面

单页应用可以替换主要内容、在不重新加载的情况下改变 URL，并在多个异步步骤后渲染所需元素。因此，只在 `document-idle` 运行一次的用户脚本可能错过实际路由，或在后续更新中绑定重复 UI。

安全模型是一个包含三个操作的小型控制器：

- `start()` 负责观察器、路由钩子和初始刷新。
- `refresh()` 将当前 URL 和 DOM 调和为期望状态。
- `stop()` 释放每项资源，并恢复脚本修改过的内容。

## 使用 `MutationObserver` 观察 DOM 变化

`MutationObserver` 是浏览器 API，不需要 Tampermonkey grant。观察包含目标的最小稳定根节点。如果还不存在稳定根节点，在确认它存在后观察 `document.documentElement`。

将观察器用作安排一次刷新的信号，而不是对每次 mutation 执行昂贵工作的地方。脚本自己的 DOM 变化也可能触发观察器，因此当期望标记已经存在时，`refresh()` 必须具备幂等性并快速返回。

```js
const observer = new MutationObserver(() => scheduleRefresh('dom'));
if (document.documentElement) {
  observer.observe(document.documentElement, { childList: true, subtree: true });
}

function stop() {
  observer.disconnect();
}
```

除非需求确实需要，否则不要观察 attributes 或 character data。宽泛观察器配合昂贵工作可能形成反馈循环并降低页面性能。

## 观察 URL 变化

使用 `popstate` 处理浏览器后退和前进导航。`pushState` 和 `replaceState` 本身不会派发 `popstate`，因此需要了解程序化路由变化的控制器必须包装这些方法，或在检查版本和浏览器行为后使用 Tampermonkey 支持的 URL 变化功能。

包装 history 方法时：

1. 保存原始函数。
2. 使用原始的 `this` 值和参数调用它。
3. 保留其返回值和抛出的错误。
4. 调用成功后安排刷新。
5. 在 `stop()` 中恢复原始函数。

只安装一次补丁。第二次 `start()` 不得再次包装已经包装过的函数。

## 防抖和有界重试

对成批的 DOM 和路由信号进行刷新防抖。计时器是资源，teardown 时必须清除。

对于已知会在异步渲染后出现的目标，使用带递增延迟的有限重试预算。路由变化时重置预算。预算耗尽后停止重试并保持页面可用；不要创建无界 `setInterval` 或递归 timeout。

```js
let refreshTimer = null;
let retryTimer = null;
let retryCount = 0;
const maxRetries = 8;

function scheduleRefresh(reason) {
  if (refreshTimer !== null) return;
  refreshTimer = window.setTimeout(() => {
    refreshTimer = null;
    refresh(reason);
  }, 75);
}

function scheduleRetry() {
  if (retryTimer !== null || retryCount >= maxRetries) return;
  const delay = Math.min(1600, 100 * (2 ** retryCount));
  retryCount += 1;
  retryTimer = window.setTimeout(() => {
    retryTimer = null;
    scheduleRefresh('retry');
  }, delay);
}
```

此片段中的浏览器 API 不需要 Tampermonkey grant。刷新函数仍必须在执行操作前检查控制器正在运行。

## 路由重新进入与幂等性

路由处理应是调和操作：

- 如果 URL 不在功能路由内，移除脚本拥有的路由 UI，并取消路由专属重试。
- 如果 URL 在路由内且标记已经存在，只更新必要状态。
- 如果 URL 在路由内但目标宿主缺失，安排有界重试。
- 如果目标出现，只创建一次 UI 并绑定一次监听器。
- 应用替换目标时，让下一次刷新重新查找它，而不是一直保留已脱离页面的节点引用。

绝不要假设 URL 变化意味着旧 DOM 仍然有效，也不要假设 DOM mutation 意味着路由发生了变化。将 URL 状态和 DOM 状态作为 `refresh()` 的独立输入。

## 完整控制器模式

此示例只使用浏览器 API，因此有意不包含 `GM_*` 调用和 Tampermonkey API grant。改造版本只有使用 Tampermonkey API 时才添加 grant。示例路由和选择器均为占位符。

```js
// ==UserScript==
// @name         SPA Route Controller Example
// @namespace    https://userscripts.example.com/spa-controller
// @version      1.0.0
// @match        https://app.example.com/orders/*
// @run-at       document-end
// ==/UserScript==

(() => {
  'use strict';

  function createController() {
    const state = {
      running: false,
      observer: null,
      refreshTimer: null,
      retryTimer: null,
      retryCount: 0,
      routeKey: location.href,
      panel: null,
      panelOwned: false,
      historyPatched: false,
      originalPushState: null,
      originalReplaceState: null,
      wrappedPushState: null,
      wrappedReplaceState: null,
      popStateHandler: null,
      pagehideHandler: null,
    };

    const maxRetries = 8;
    const panelSelector = '[data-tm-spa-panel="orders"]';
    const hostSelector = '[data-orders-toolbar]';

    function isFeatureRoute() {
      return location.pathname.startsWith('/orders/');
    }

    function removePanel() {
      if (state.panelOwned) state.panel?.remove();
      state.panel = null;
      state.panelOwned = false;
    }

    function scheduleRefresh(reason) {
      if (!state.running || state.refreshTimer !== null) return;
      state.refreshTimer = window.setTimeout(() => {
        state.refreshTimer = null;
        refresh(reason);
      }, 75);
    }

    function scheduleRetry() {
      if (
        !state.running ||
        state.retryTimer !== null ||
        state.retryCount >= maxRetries
      ) {
        return;
      }

      const delay = Math.min(1600, 100 * (2 ** state.retryCount));
      state.retryCount += 1;
      state.retryTimer = window.setTimeout(() => {
        state.retryTimer = null;
        scheduleRefresh('retry');
      }, delay);
    }

    function createPanel(host) {
      const panel = document.createElement('button');
      panel.type = 'button';
      panel.dataset.tmSpaPanel = 'orders';
      panel.textContent = 'Review orders';
      panel.addEventListener('click', () => {
        console.log('[spa-controller] route action', location.href);
      });
      host.append(panel);
      state.panel = panel;
      state.panelOwned = true;
    }

    function refresh(reason) {
      if (!state.running) return;

      const nextRouteKey = location.href;
      if (nextRouteKey !== state.routeKey) {
        state.routeKey = nextRouteKey;
        state.retryCount = 0;
        if (!isFeatureRoute()) removePanel();
      }

      if (!isFeatureRoute()) {
        removePanel();
        return;
      }

      const existing = document.querySelector(panelSelector);
      if (existing) {
        const ownsExisting = state.panelOwned && state.panel === existing;
        state.panel = existing;
        state.panelOwned = ownsExisting;
        state.retryCount = 0;
        return;
      }

      const host = document.querySelector(hostSelector);
      if (!host) {
        scheduleRetry();
        return;
      }

      state.retryCount = 0;
      createPanel(host);
      console.debug('[spa-controller] refreshed', reason);
    }

    function patchHistory() {
      if (state.historyPatched) return;
      state.originalPushState = history.pushState;
      state.originalReplaceState = history.replaceState;

      state.wrappedPushState = function pushState(...args) {
        const result = state.originalPushState.apply(this, args);
        scheduleRefresh('pushState');
        return result;
      };

      state.wrappedReplaceState = function replaceState(...args) {
        const result = state.originalReplaceState.apply(this, args);
        scheduleRefresh('replaceState');
        return result;
      };

      history.pushState = state.wrappedPushState;
      history.replaceState = state.wrappedReplaceState;

      state.historyPatched = true;
    }

    function restoreHistory() {
      if (!state.historyPatched) return;
      if (history.pushState === state.wrappedPushState) {
        history.pushState = state.originalPushState;
      }
      if (history.replaceState === state.wrappedReplaceState) {
        history.replaceState = state.originalReplaceState;
      }
      state.originalPushState = null;
      state.originalReplaceState = null;
      state.wrappedPushState = null;
      state.wrappedReplaceState = null;
      state.historyPatched = false;
    }

    function start() {
      if (state.running) return;
      state.running = true;
      state.pagehideHandler = () => stop();
      window.addEventListener('pagehide', state.pagehideHandler, { once: true });
      state.observer = new MutationObserver(() => scheduleRefresh('dom'));
      if (document.documentElement) {
        state.observer.observe(document.documentElement, {
          childList: true,
          subtree: true,
        });
      }
      state.popStateHandler = () => scheduleRefresh('popstate');
      window.addEventListener('popstate', state.popStateHandler);
      patchHistory();
      refresh('start');
    }

    function stop() {
      if (!state.running) return;
      state.running = false;
      state.observer?.disconnect();
      state.observer = null;
      if (state.refreshTimer !== null) window.clearTimeout(state.refreshTimer);
      if (state.retryTimer !== null) window.clearTimeout(state.retryTimer);
      state.refreshTimer = null;
      state.retryTimer = null;
      state.retryCount = 0;
      if (state.popStateHandler) {
        window.removeEventListener('popstate', state.popStateHandler);
        state.popStateHandler = null;
      }
      if (state.pagehideHandler) {
        window.removeEventListener('pagehide', state.pagehideHandler);
        state.pagehideHandler = null;
      }
      removePanel();
      restoreHistory();
    }

    return { start, refresh, stop };
  }

  const controller = createController();
  controller.start();
})();
```

控制器保存其 `pagehide` 处理器，并在 `stop()` 中移除，因此运行时重复 `start()` 会被忽略，而在 `stop()` 后再次启动会准确安装一个新的处理器。路由监听器、观察器、计时器、history 补丁和控制器创建的面板都会明确释放。`panelOwned` 标志防止路由退出或 teardown 移除只是拥有相同标记、但属于页面或其他脚本的节点。

不要在未考虑其他扩展或页面代码也可能包装 history 的情况下修改 history。保留调用语义，只恢复此实例保存的函数引用。如果补丁后该引用已经变化，stop 应避免覆盖其他包装器；根据目标页面调整恢复策略。

## 清理

清理必须断开 `MutationObserver`，移除 `popstate` 监听器，清除防抖和重试计时器，移除路由所有权节点，并且仅当此控制器仍拥有包装器时恢复 history 方法。即使文档仍然打开，离开路由也属于清理事件。

## 动态页面审查

- [ ] DOM 变化通过有界、防抖的刷新来观察。
- [ ] 观察器监听实际可行的最小根节点和所需的 mutation 类型。
- [ ] 已覆盖 `pushState`、`replaceState` 和 `popstate` 行为。
- [ ] history 方法只被补丁一次，使用原始接收者调用，并且会恢复。
- [ ] 重新进入路由会重置路由专属的重试状态。
- [ ] 重试有有限上限，并在 teardown 时取消。
- [ ] 已有标记能防止重复 UI 和重复监听器。
- [ ] 不会无限期保留脱离页面的节点。
- [ ] `start`、`refresh` 和 `stop` 具有清晰的所有权和错误行为。
- [ ] 脚本没有声称 `@run-at` 代表应用就绪。

## 官方参考

- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey URL 变化 API 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=window#api:window.onurlchange)
- [MDN `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [MDN `history.pushState`](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState)
- [MDN `history.replaceState`](https://developer.mozilla.org/en-US/docs/Web/API/History/replaceState)
- [MDN `popstate`](https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event)
