# 04. DOM and Styles

DOM work is where a userscript meets an application it does not own. Keep the boundary explicit: locate only the nodes needed, check every optional result, write safe text and attributes, mark nodes owned by the script, and remove those nodes and listeners during teardown.

## Safe Selectors and Null Checks

Use selectors that describe a stable contract rather than a visual accident:

- Prefer a documented `data-*` attribute, stable semantic element, or a small combination of attributes.
- Avoid generated class names, positional selectors, and long descendant chains.
- Keep selectors in constants so a page change has one obvious repair point.
- Do not interpolate untrusted text into a selector. If a dynamic identifier is unavoidable, use `CSS.escape` and still validate the resulting element.
- Treat `querySelector` and `closest` as nullable. An absent node is a normal page state, not an exception to ignore.

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

The browser APIs in this example require no Tampermonkey grant. Validate a page-provided identifier before using it in a URL, selector, request, or storage key.

## Create and Update Elements Safely

Use `document.createElement`, explicit attributes, and `textContent` for ordinary DOM work. Avoid `innerHTML` when the value contains page, URL, storage, or remote data. If an HTML fragment is required, create a controlled template and validate every interpolated value before insertion.

```js
const button = document.createElement('button');
button.type = 'button';
button.className = 'tm-order-action';
button.textContent = 'Review order';
button.setAttribute('aria-label', 'Review this order');
```

Use native controls for native behavior. A `button` gives keyboard users a focusable, activatable control. If a custom element must behave like a control, provide an accessible name, focus behavior, keyboard handling, and an appropriate ARIA role; a native button is usually simpler and more reliable.

## Event Listeners and Cleanup

Keep handler references or use an `AbortController` so teardown can remove listeners. Delegate events from a stable script-owned root when repeated child nodes are expected. Check that an event target belongs to that root before acting.

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

`AbortController` and `addEventListener` are browser APIs and need no Tampermonkey grant. Do not assume the page will remove a listener for you when it replaces a subtree; the listener can keep script state alive if the owner remains reachable.

## Styles and Element Injection

`GM_addStyle(css)` is a Tampermonkey API and requires:

```js
// @grant GM_addStyle
```

Tampermonkey documents that it returns the injected style element, so retain that return value for cleanup. Use a CSS namespace such as `[data-tm-order-panel] .tm-order-panel__button` to avoid changing page styles accidentally. Keep selectors specific to the owned root rather than using global names such as `.button`.

`GM_addElement` is a Tampermonkey API and requires:

```js
// @grant GM_addElement
```

It supports `GM_addElement(tagName, attributes)` and `GM_addElement(parentNode, tagName, attributes)`, and returns the injected element or `null` on error. It can be useful for specific injection cases, including elements affected by page CSP. It does not make untrusted `src`, `href`, or `textContent` safe; validate those values and use a narrow source policy.

For a normal panel, `document.createElement` is sufficient and easier to reason about. Use `GM_addElement` when its injection semantics are needed, not as a default replacement for the browser API.

## Shadow DOM Trade-offs

A shadow root can isolate a panel's CSS and reduce collisions with page styles. It also changes integration behavior:

- Page selectors cannot normally reach shadow descendants.
- Events crossing the boundary can be retargeted, so `event.target` may be the host.
- Closed roots make debugging and external integration harder.
- Page-level themes, inherited styles, and accessibility tooling may not behave as expected.
- A shadow root does not make unsafe data safe and does not replace accessible labels or keyboard support.

Use an open shadow root when isolation is more important than page inspectability, and test focus, screen-reader output, and route teardown. For a small integration panel, a namespaced light-DOM root is often the least surprising choice.

## Idempotent `ensurePanel`

This complete example uses `GM_addStyle` and `GM_addElement`, so both grants are declared. It uses a stable `data-tm-panel` marker, avoids duplicate listeners by binding only to a newly created panel, and removes only nodes and styles created by this script instance.

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

The stable marker also lets a later `ensurePanel()` call find the existing panel. If several independent scripts might use the same page, choose a namespace unique to the owning script. Do not remove an existing node merely because it matches a generic class or a page-owned marker.

## Cleanup Review

- [ ] Every selector has a stable reason and a null path.
- [ ] Dynamic selector values are validated and escaped.
- [ ] Text and attributes use safe DOM APIs.
- [ ] Controls are native or have explicit accessibility behavior.
- [ ] CSS is namespaced beneath a script-owned marker.
- [ ] `GM_addStyle` and `GM_addElement` grants are declared only when used.
- [ ] Observer, listener, timer, style, and owned-node cleanup is reachable.
- [ ] Repeated `ensurePanel()` calls do not duplicate nodes or listeners.
- [ ] Shadow DOM behavior was tested if used.

## Official References

- [Tampermonkey `GM_addStyle`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_addStyle)
- [Tampermonkey `GM_addElement`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_addElement)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [MDN `Element.querySelector`](https://developer.mozilla.org/en-US/docs/Web/API/Element/querySelector)
- [MDN `EventTarget.addEventListener`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN `CSS.escape`](https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape_static)
- [MDN Using Shadow DOM](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM)
