# 03. Runtime Timing and Permissions

Metadata controls when and where Tampermonkey can inject a script, while grants control which privileged interfaces the script receives. Both are constraints, not proof that the application or a page-owned JavaScript object is ready.

## Injection Timing

`@run-at` selects the first possible injection moment. Required scripts from `@require` can delay execution, and a page application can continue rendering after injection. The [Tampermonkey `@run-at` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at) defines the timing choices:

| Value | Timing choice | What it does not guarantee |
| --- | --- | --- |
| `document-start` | Inject as fast as possible, before most page DOM exists. | The target element, `document.body`, or application state exists. |
| `document-body` | Inject when the body element exists. | The body is complete or the application has rendered its route. |
| `document-end` | Inject when or after `DOMContentLoaded` was dispatched. | Async data, client-side route rendering, or hydration is complete. |
| `document-idle` | Inject after `DOMContentLoaded`; this is the default when omitted. | A SPA is ready, or later network and DOM updates will not occur. |

Choose the earliest timing that serves the requirement:

- Use `document-start` for an early page hook or a feature that must observe initial document work, with null checks and a later readiness path.
- Use `document-body` when a body parent is required but the script can tolerate a still-loading document.
- Use `document-end` when the initial DOM is the input and waiting for `DOMContentLoaded` is useful.
- Use `document-idle` for a non-critical initial enhancement, then separately observe application updates when necessary.

Treat these values as timing choices rather than application lifecycle events. For a dynamic page, combine them with a readiness check, route handling, or bounded retry.

## Context Boundaries

The page and a userscript can have different JavaScript contexts even though they can refer to related DOM nodes. Keep these boundaries explicit:

### Isolated userscript context

The normal userscript environment provides a sandboxed execution context in which Tampermonkey can expose granted APIs. Ordinary browser APIs such as `document`, `Element`, and event listeners remain useful. A page's JavaScript globals and a userscript's globals are not automatically the same object.

### Page context

Page context is the page's JavaScript realm, often called the main world. Code there can interact directly with page-defined globals and page functions, but it also shares the page's trust and collision surface. Do not enter page context merely to access the DOM.

### `unsafeWindow`

`unsafeWindow` is a Tampermonkey API for accessing the page window. It requires `@grant unsafeWindow`. Treat every property read from it as page-controlled input, and avoid writing to it unless the integration contract explicitly requires it. A page can replace functions, expose mutable objects, or use values that are not safe to pass into privileged code.

### `@sandbox`

`@sandbox` is a Tampermonkey feature documented as available in `4.18+`. It expresses the access the script needs:

- `raw` requests page (`MAIN_WORLD`) access for compatibility.
- `JavaScript` requests access to `unsafeWindow` or page JavaScript integration.
- `DOM` states that DOM access is sufficient and direct page-window access is not needed.

Tampermonkey may use an enabled fallback context when the requested injection is unavailable, and browser implementations can differ. Do not describe `@sandbox` as a universal browser standard. Pin and test a minimum Tampermonkey version, and use the [official `@sandbox` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox) for current behavior.

### `@grant none`

`@grant none` is distinct from omitting all `@grant` entries. Tampermonkey documents it as disabling the sandbox; no `GM_*` function is available, although `GM_info` remains available. This can make page-context integration easy, but it also removes the normal isolation boundary and can create global-name collisions or expose the script to page changes. Use it only as a deliberate compatibility choice, not as a default least-privilege setting.

The [official `@grant` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=grant) is the source of truth for the installed version's grant behavior.

## Permission Decision Table

| Need | Browser-only option | Tampermonkey option and required metadata | Decision rule |
| --- | --- | --- | --- |
| Read or update ordinary DOM | `document`, `querySelector`, `createElement`, events | None | Prefer the browser API. Add null checks and safe text or attributes. |
| Add CSS | A native `<style>` element | `GM_addStyle` with `@grant GM_addStyle` | Use the smallest option that survives the target page's constraints; retain the returned style element for cleanup. |
| Persist userscript data | `localStorage` when page-scoped persistence is acceptable | `GM_getValue`, `GM_setValue`, and related APIs with matching grants | Prefer Tampermonkey storage for script-scoped settings and cross-tab change events. |
| Access page-defined globals | Deliberate page integration mechanism | `unsafeWindow` with `@grant unsafeWindow`, or a tested `@sandbox` choice (`4.18+`) | Use only when a page API is required; document the trust boundary. |
| Cross-origin HTTP request | `fetch` is constrained by page origin and CORS | `GM_xmlhttpRequest` with `@grant GM_xmlhttpRequest` and narrow `@connect` entries | Validate URLs, redirects, status, content type, size, and response data. |
| Create an element through Tampermonkey | `document.createElement` | `GM_addElement` with `@grant GM_addElement` | Use for its specific injection behavior, including cases involving page CSP; still validate the element and clean it up. |
| Receive storage changes | No equivalent userscript-scoped event | `GM_addValueChangeListener` and `GM_removeValueChangeListener` with matching grants | Remove the listener during teardown. |

Only the APIs in the Tampermonkey column require grants. Metadata directives such as `@require` and `@resource` are not a replacement for declaring the API used to consume their result.

## Startup and Teardown Pattern

This self-contained pattern uses `GM_addStyle` and value-change listeners. Its metadata declares every Tampermonkey API used. The browser APIs in the example need no grant.

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

The `pagehide` handler is a useful teardown signal for page-owned resources, but it is not a replacement for route cleanup in an SPA. For route changes, expose the same `start`, `refresh`, and `stop` operations to a controller as described in [05. SPA and Dynamic Pages](05-spa-and-dynamic-pages.md).

If startup can be retried after a missing body, call `start` from a bounded readiness path rather than repeatedly setting an unbounded interval. If an API is asynchronous, handle rejected promises or error callbacks and release its request or listener during `stop`.

## Practical Review Questions

- Does the chosen timing match the earliest input the script needs?
- Which parts of the page can still change after startup?
- Is page-window access actually necessary, or is DOM access enough?
- Does every privileged API have a narrow grant and a failure path?
- Does teardown work after every possible partial-start failure?
- Is the minimum Tampermonkey version documented for `@sandbox` or modern APIs?

## Runtime Checklist

- [ ] `@run-at` is selected for the required input, not mistaken for application readiness.
- [ ] `document-start`, `document-body`, `document-end`, and `document-idle` assumptions are explicit.
- [ ] Userscript context, page context, and `unsafeWindow` use are distinguished.
- [ ] `@sandbox` is marked as version-specific and tested in the supported environment.
- [ ] `@grant none` is used only as a deliberate page-context decision.
- [ ] Each privileged API has its exact grant, validation, and failure path.
- [ ] Startup is idempotent and partial startup can be torn down safely.
- [ ] Listeners, styles, owned nodes, timers, and other resources are released.

## Official References

- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `@sandbox` (`4.18+`)](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey `unsafeWindow`](https://www.tampermonkey.net/documentation.php?locale=en&q=unsafeWindow)
- [MDN `DOMContentLoaded`](https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event)
- [MDN `pagehide`](https://developer.mozilla.org/en-US/docs/Web/API/Window/pagehide_event)
