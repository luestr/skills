# 03. 运行时机与权限

元数据控制 Tampermonkey 可以在何时何地注入脚本，而 grant 控制脚本获得哪些特权接口。两者都是约束，不能证明应用或页面拥有的 JavaScript 对象已经就绪。

## 注入时机

`@run-at` 选择第一个可能的注入时刻。`@require` 中的必需脚本可能延迟执行，而页面应用可能在注入后继续渲染。[Tampermonkey `@run-at` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)定义了这些时机选项：

| 值 | 时机选择 | 它不保证什么 |
| --- | --- | --- |
| `document-start` | 尽快注入，在大多数页面 DOM 存在前执行。 | 目标元素、`document.body` 或应用状态存在。 |
| `document-body` | body 元素存在时注入。 | body 已完整，或应用已经渲染路由。 |
| `document-end` | 在派发 `DOMContentLoaded` 时或之后注入。 | 异步数据、客户端路由渲染或 hydration 已完成。 |
| `document-idle` | 在 `DOMContentLoaded` 后注入；省略时这是默认值。 | SPA 已就绪，或之后不会再发生网络和 DOM 更新。 |

选择满足需求的最早时机：

- 对早期页面钩子或必须观察初始文档工作的功能使用 `document-start`，同时加入空值检查和后续就绪路径。
- 需要 body 父节点但能够容忍文档仍在加载时使用 `document-body`。
- 初始 DOM 是输入且等待 `DOMContentLoaded` 有用时使用 `document-end`。
- 对非关键的初始增强使用 `document-idle`，然后在必要时单独观察应用更新。

把这些值视为时机选择，而不是应用生命周期事件。对于动态页面，将它们与就绪检查、路由处理或有界重试结合使用。

## 上下文边界

页面和用户脚本可以拥有不同的 JavaScript 上下文，即使它们可以引用相关的 DOM 节点。明确维护这些边界：

### 隔离的用户脚本上下文

普通用户脚本环境提供沙箱执行上下文，Tampermonkey 可以在其中暴露已授权的 API。`document`、`Element` 和事件监听器等普通浏览器 API 仍然有用。页面的 JavaScript 全局对象和用户脚本的全局对象不会自动成为同一个对象。

### 页面上下文

页面上下文是页面的 JavaScript realm，通常称为主世界。这里的代码可以直接与页面定义的全局对象和页面函数交互，但也共享页面的信任和冲突面。不要仅为了访问 DOM 就进入页面上下文。

### `unsafeWindow`

`unsafeWindow` 是用于访问页面 window 的 Tampermonkey API。它需要 `@grant unsafeWindow`。将从中读取的每个属性都视为页面控制的输入，除非集成契约明确要求，否则避免写入。页面可以替换函数、暴露可变对象，或使用不适合传入特权代码的值。

### `@sandbox`

`@sandbox` 是 Tampermonkey 的功能，文档说明它在 `4.18+` 可用。它表示脚本需要的访问权限：

- `raw` 请求页面（`MAIN_WORLD`）访问，以实现兼容性。
- `JavaScript` 请求访问 `unsafeWindow` 或进行页面 JavaScript 集成。
- `DOM` 表示 DOM 访问已足够，不需要直接访问页面 window。

当请求的注入不可用时，Tampermonkey 可能使用已启用的回退上下文，浏览器实现也可能不同。不要把 `@sandbox` 描述为通用浏览器标准。固定并测试最低 Tampermonkey 版本，并使用[官方 `@sandbox` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)了解当前行为。

### `@grant none`

`@grant none` 与省略所有 `@grant` 条目不同。Tampermonkey 将其定义为禁用沙箱；没有任何 `GM_*` 函数可用，但 `GM_info` 仍可用。这会让页面上下文集成变得简单，但也会移除通常的隔离边界，产生全局名称冲突，或让脚本暴露于页面变化。仅将其作为有意的兼容性选择使用，不要把它作为默认的最小权限设置。

[官方 `@grant` 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)是已安装版本 grant 行为的事实来源。

## 权限决策表

| 需求 | 仅浏览器选项 | Tampermonkey 选项和所需元数据 | 决策规则 |
| --- | --- | --- | --- |
| 读取或更新普通 DOM | `document`、`querySelector`、`createElement`、事件 | 无 | 优先使用浏览器 API。添加空值检查以及安全的文本或属性操作。 |
| 添加 CSS | 原生 `<style>` 元素 | 使用 `@grant GM_addStyle` 的 `GM_addStyle` | 使用能够满足目标页面约束的最小选项；保留返回的样式元素以便清理。 |
| 持久化用户脚本数据 | 页面范围持久化可以接受时使用 `localStorage` | 带对应 grant 的 `GM_getValue`、`GM_setValue` 及相关 API | 用户脚本范围的设置和跨标签页变更事件优先使用 Tampermonkey 存储。 |
| 访问页面定义的全局对象 | 有意设计的页面集成机制 | 带 `@grant unsafeWindow` 的 `unsafeWindow`，或经过测试的 `@sandbox` 选择（`4.18+`） | 只有需要页面 API 时使用；记录信任边界。 |
| 跨源 HTTP 请求 | `fetch` 受页面源和 CORS 约束 | 带 `@grant GM_xmlhttpRequest` 和范围狭窄 `@connect` 条目的 `GM_xmlhttpRequest` | 验证 URL、重定向、状态、内容类型、大小和响应数据。 |
| 通过 Tampermonkey 创建元素 | `document.createElement` | 带 `@grant GM_addElement` 的 `GM_addElement` | 用于其特定的注入行为，包括涉及页面 CSP 的情况；仍需验证元素并清理。 |
| 接收存储变更 | 没有等价的用户脚本范围事件 | 带对应 grant 的 `GM_addValueChangeListener` 和 `GM_removeValueChangeListener` | teardown 时移除监听器。 |

只有 Tampermonkey 列中的 API 需要 grant。`@require` 和 `@resource` 等元数据指令不能替代用于消费其结果的 API 声明。

## 启动与 teardown 模式

这个自包含模式使用 `GM_addStyle` 和值变更监听器。其元数据声明了每个使用的 Tampermonkey API。示例中的浏览器 API 不需要 grant。

```js
// ==UserScript==
// @name         Runtime Lifecycle Example
// @namespace    https://userscripts.example.com/runtime-lifecycle
// @version      1.0.0
// @match        https://app.example.com/*
// @run-at       document-end
// @grant        GM_addStyle
// @grant        GM_addValueChangeListener
// @grant        GM_removeValueChangeListener
// ==/UserScript==

(() => {
  'use strict';

  const settingKey = 'runtime-example.enabled';
  let root = null;
  let style = null;
  let listenerId = null;
  let started = false;
  let domContentLoadedHandler = null;

  function start() {
    if (started) return;
    started = true;

    try {
      if (!document.body) {
        throw new Error('The document body is not available yet.');
      }

      style = GM_addStyle(`
        [data-runtime-example] {
          position: fixed;
          inset: auto 1rem 1rem auto;
          z-index: 2147483647;
          padding: 0.5rem;
          background: white;
          color: black;
          border: 1px solid currentColor;
        }
      `);

      root = document.createElement('output');
      root.dataset.runtimeExample = '';
      root.textContent = 'Runtime example is enabled.';
      root.setAttribute('role', 'status');
      document.body.append(root);

      listenerId = GM_addValueChangeListener(
        settingKey,
        (_key, _oldValue, newValue, remote) => {
          if (remote && root) {
            root.hidden = newValue === false;
          }
        },
      );
    } catch (error) {
      console.error('[runtime-example] startup failed', error);
      stop();
    }
  }

  function stop() {
    if (domContentLoadedHandler !== null) {
      document.removeEventListener('DOMContentLoaded', domContentLoadedHandler);
      domContentLoadedHandler = null;
    }
    if (listenerId !== null) {
      GM_removeValueChangeListener(listenerId);
      listenerId = null;
    }
    root?.remove();
    style?.remove();
    root = null;
    style = null;
    started = false;
  }

  if (document.readyState === 'loading') {
    domContentLoadedHandler = start;
    document.addEventListener('DOMContentLoaded', domContentLoadedHandler, { once: true });
  } else {
    start();
  }

  window.addEventListener('pagehide', stop, { once: true });
})();
```

`pagehide` 处理器是页面资源的有用 teardown 信号，但不能替代 SPA 中的路由清理。对于路由变化，将相同的 `start`、`refresh` 和 `stop` 操作暴露给控制器，具体见 [05. SPA and Dynamic Pages](05-spa-and-dynamic-pages.md)。

如果 body 缺失后可以重试启动，应从有界就绪路径调用 `start`，而不是反复设置无界 interval。如果 API 是异步的，应处理被拒绝的 promise 或错误回调，并在 `stop` 期间释放请求或监听器。

## 实践审查问题

- 所选时机是否符合脚本需要的最早输入？
- 启动后页面的哪些部分仍可能变化？
- 是否真的需要页面 window 访问，还是 DOM 访问已经足够？
- 每个特权 API 是否都有范围狭窄的 grant 和失败路径？
- 对每一种可能的部分启动失败，teardown 是否都能工作？
- 是否为 `@sandbox` 或现代 API 记录了最低 Tampermonkey 版本？

## 运行时检查清单

- [ ] `@run-at` 是根据所需输入选择的，没有被误认为应用就绪。
- [ ] `document-start`、`document-body`、`document-end` 和 `document-idle` 的假设明确。
- [ ] 已区分用户脚本上下文、页面上下文和 `unsafeWindow` 的使用。
- [ ] `@sandbox` 已标明版本特定，并在支持的环境中测试。
- [ ] 仅将 `@grant none` 用作有意的页面上下文决策。
- [ ] 每个特权 API 都有精确 grant、验证和失败路径。
- [ ] 启动具备幂等性，部分启动也能安全 teardown。
- [ ] 监听器、样式、所有权节点、计时器和其他资源都能释放。

## 官方参考

- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `@sandbox`（`4.18+`）](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey `unsafeWindow`](https://www.tampermonkey.net/documentation.php?locale=en&q=unsafeWindow)
- [MDN `DOMContentLoaded`](https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event)
- [MDN `pagehide`](https://developer.mozilla.org/en-US/docs/Web/API/Window/pagehide_event)
