# 04. DOM 与样式

DOM 工作是用户脚本接触其并不拥有的应用的地方。保持边界明确：只定位所需节点，检查每个可选结果，写入安全文本和属性，标记由脚本拥有的节点，并在 teardown 期间移除这些节点和监听器。

## 安全选择器和空值检查

使用描述稳定契约而非视觉偶然的选择器：

- 优先使用有文档记录的 `data-*` 属性、稳定的语义元素或少量属性组合。
- 避免生成的类名、位置选择器和很长的后代链。
- 将选择器放在常量中，使页面变化时有一个明确的修复点。
- 不要将不可信文本插入选择器。如果无法避免动态标识符，使用 `CSS.escape`，并继续验证得到的元素。
- 将 `querySelector` 和 `closest` 视为可返回空值。缺少节点是正常页面状态，不应被忽略为异常。

```js
const rowSelector = '[data-order-id]';
const row = document.querySelector(rowSelector);

if (!row) {
  console.warn('[order-helper] no order row is available');
  return;
}

const orderId = row.getAttribute('data-order-id');
if (!orderId || !/^[A-Za-z0-9_-]+$/.test(orderId)) {
  throw new Error('The order identifier is missing or has an invalid format.');
}
```

示例中的浏览器 API 不需要 Tampermonkey grant。在 URL、选择器、请求或存储键中使用页面提供的标识符前，先验证它。

## 安全创建和更新元素

普通 DOM 操作使用 `document.createElement`、明确属性和 `textContent`。当值包含页面、URL、存储或远程数据时，避免使用 `innerHTML`。如果确实需要 HTML 片段，创建受控模板，并在插入前验证每个插值。

```js
const button = document.createElement('button');
button.type = 'button';
button.className = 'tm-order-action';
button.textContent = 'Review order';
button.setAttribute('aria-label', 'Review this order');
```

原生行为使用原生控件。`button` 为键盘用户提供可聚焦、可激活的控件。如果自定义元素必须表现为控件，应提供可访问名称、焦点行为、键盘处理和适当的 ARIA role；原生按钮通常更简单、更可靠。

## 事件监听器和清理

保留处理器引用，或使用 `AbortController`，以便 teardown 能移除监听器。预期子节点会重复出现时，从稳定的脚本所有根节点进行事件委托。执行操作前检查事件目标属于该根节点。

```js
const controller = new AbortController();

root.addEventListener('click', (event) => {
  const action = event.target.closest('[data-tm-action="refresh"]');
  if (!action || !root.contains(action)) return;
  refresh();
}, { signal: controller.signal });

function stop() {
  controller.abort();
  root.remove();
}
```

`AbortController` 和 `addEventListener` 是浏览器 API，不需要 Tampermonkey grant。不要假设页面在替换子树时会为你移除监听器；如果所有者仍可达，监听器可能使脚本状态继续存活。

## 样式和元素注入

`GM_addStyle(css)` 是 Tampermonkey API，需要：

```js
// @grant GM_addStyle
```

Tampermonkey 文档说明它会返回注入的样式元素，因此要保留返回值以便清理。使用类似 `[data-tm-order-panel] .tm-order-panel__button` 的 CSS 命名空间，避免意外修改页面样式。选择器应限定在所有权根节点下，而不是使用 `.button` 等全局名称。

`GM_addElement` 是 Tampermonkey API，需要：

```js
// @grant GM_addElement
```

它支持 `GM_addElement(tagName, attributes)` 和 `GM_addElement(parentNode, tagName, attributes)`，并在出错时返回注入元素或 `null`。它可用于特定注入场景，包括受页面 CSP 影响的元素。它不会让不可信的 `src`、`href` 或 `textContent` 变得安全；仍需验证这些值并采用范围狭窄的来源策略。

普通面板使用 `document.createElement` 就足够，而且更容易推理。需要其注入语义时使用 `GM_addElement`，不要把它作为浏览器 API 的默认替代品。

## Shadow DOM 权衡

shadow root 可以隔离面板的 CSS，减少与页面样式的冲突，但也会改变集成行为：

- 页面选择器通常无法访问 shadow 后代。
- 穿过边界的事件可能被重新定位，因此 `event.target` 可能是宿主。
- closed root 会让调试和外部集成更困难。
- 页面级主题、继承样式和无障碍工具的行为可能不符合预期。
- shadow root 不会让不安全数据变安全，也不能替代可访问标签或键盘支持。

当隔离比页面可检查性更重要时使用 open shadow root，并测试焦点、屏幕阅读器输出和路由 teardown。对于小型集成面板，带命名空间的 light DOM 根节点通常是最不令人意外的选择。

## 幂等的 `ensurePanel`

这个完整示例使用 `GM_addStyle` 和 `GM_addElement`，因此声明了两个 grant。它使用稳定的 `data-tm-panel` 标记，只为新创建的面板绑定监听器以避免重复，并只移除本脚本实例创建的节点和样式。

```js
// ==UserScript==
// @name         DOM Panel Example
// @namespace    https://userscripts.example.com/dom-panel
// @version      1.0.0
// @match        https://app.example.com/orders/*
// @run-at       document-end
// @grant        GM_addStyle
// @grant        GM_addElement
// ==/UserScript==

(() => {
  'use strict';

  const panelSelector = '[data-tm-panel="order-actions"]';
  const styleSelector = 'style[data-tm-style="order-actions"]';
  const controller = new AbortController();
  let panel = null;
  let style = null;
  let createdPanel = false;
  let createdStyle = false;
  let feedbackTimer = null;

  function ensureStyle() {
    const existing = document.querySelector(styleSelector);
    if (existing) return existing;

    const injected = GM_addStyle(`
      [data-tm-panel="order-actions"] {
        display: block;
        margin: 0.75rem 0;
        padding: 0.75rem;
        border: 1px solid #67748a;
        background: #f7f9fc;
        color: #18212f;
      }

      [data-tm-panel="order-actions"] .tm-order-panel__button {
        min-block-size: 2.25rem;
        padding: 0.35rem 0.7rem;
      }
    `);

    if (!injected) {
      throw new Error('Tampermonkey did not return a style element.');
    }
    injected.dataset.tmStyle = 'order-actions';
    style = injected;
    createdStyle = true;
    return injected;
  }

  function bindPanel(root) {
    root.addEventListener('click', (event) => {
      const target = event.target instanceof Element ? event.target : null;
      const button = target?.closest('[data-tm-action="refresh"]');
      if (!button || !root.contains(button)) return;
      button.disabled = true;
      button.textContent = 'Updated';
      if (feedbackTimer !== null) window.clearTimeout(feedbackTimer);
      feedbackTimer = window.setTimeout(() => {
        feedbackTimer = null;
        if (!controller.signal.aborted && button.isConnected) {
          button.disabled = false;
          button.textContent = 'Refresh order data';
        }
      }, 500);
    }, { signal: controller.signal });
  }

  function ensurePanel() {
    const existing = document.querySelector(panelSelector);
    if (existing) {
      panel = existing;
      return existing;
    }

    if (!document.body) {
      throw new Error('Cannot create the panel before document.body exists.');
    }

    const created = GM_addElement(document.body, 'section', {
      'data-tm-panel': 'order-actions',
      'aria-labelledby': 'tm-order-panel-title',
    });
    if (!created) {
      throw new Error('Tampermonkey could not create the panel.');
    }

    const heading = document.createElement('h2');
    heading.id = 'tm-order-panel-title';
    heading.textContent = 'Order actions';

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'tm-order-panel__button';
    button.dataset.tmAction = 'refresh';
    button.textContent = 'Refresh order data';

    created.append(heading, button);
    bindPanel(created);
    panel = created;
    createdPanel = true;
    return created;
  }

  function stop() {
    if (feedbackTimer !== null) {
      window.clearTimeout(feedbackTimer);
      feedbackTimer = null;
    }
    controller.abort();
    if (createdPanel) panel?.remove();
    if (createdStyle) style?.remove();
    panel = null;
    style = null;
  }

  try {
    ensureStyle();
    ensurePanel();
    window.addEventListener('pagehide', stop, { once: true });
  } catch (error) {
    console.error('[dom-panel] startup failed', error);
    stop();
  }
})();
```

稳定标记也让后续 `ensurePanel()` 调用能够找到已有面板。如果多个独立脚本可能使用同一页面，应选择对所有者脚本唯一的命名空间。不要仅因为节点匹配通用类名或页面所有标记，就移除已有节点。

## 清理审查

- [ ] 每个选择器都有稳定理由和空值路径。
- [ ] 动态选择器值经过验证和转义。
- [ ] 文本和属性使用安全 DOM API。
- [ ] 控件是原生控件，或具有明确的无障碍行为。
- [ ] CSS 位于脚本所有标记之下的命名空间中。
- [ ] 仅在使用时声明 `GM_addStyle` 和 `GM_addElement` grant。
- [ ] 观察器、监听器、计时器、样式和所有权节点的清理路径可达。
- [ ] 重复调用 `ensurePanel()` 不会复制节点或监听器。
- [ ] 若使用 Shadow DOM，已测试其行为。

## 官方参考

- [Tampermonkey `GM_addStyle`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_addStyle)
- [Tampermonkey `GM_addElement`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_addElement)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [MDN `Element.querySelector`](https://developer.mozilla.org/en-US/docs/Web/API/Element/querySelector)
- [MDN `EventTarget.addEventListener`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN `CSS.escape`](https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape_static)
- [MDN 使用 Shadow DOM](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM)
