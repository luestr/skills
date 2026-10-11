# 05. SPA and Dynamic Pages

Single-page applications can replace the main content, change the URL without reloading, and render required elements after several asynchronous steps. A userscript that runs once at `document-idle` can therefore miss the actual route or attach duplicate UI during later updates.

The safe model is a small controller with three operations:

- `start()` owns observers, route hooks, and the initial refresh.
- `refresh()` reconciles the current URL and DOM into the desired state.
- `stop()` releases every resource and restores anything patched by the script.

## Observe DOM Changes with `MutationObserver`

`MutationObserver` is a browser API and needs no Tampermonkey grant. Observe the smallest stable root that contains the target. If no stable root exists yet, observe `document.documentElement` after checking that it exists.

Use the observer as a signal to schedule one refresh, not as a place to perform expensive work for every mutation. The script's own DOM changes can trigger the observer, so `refresh()` must be idempotent and return quickly when the desired marker already exists.

```js
const observer = new MutationObserver(() => scheduleRefresh('dom'));
if (document.documentElement) {
  observer.observe(document.documentElement, { childList: true, subtree: true });
}

function stop() {
  observer.disconnect();
}
```

Do not observe attributes or character data unless the requirement needs them. A broad observer with expensive work can create a feedback loop and degrade the page.

## Observe URL Changes

Use `popstate` for browser back and forward navigation. `pushState` and `replaceState` do not themselves dispatch `popstate`, so a controller that needs to know about programmatic route changes must wrap those methods or use a Tampermonkey-supported URL-change feature after checking its version and browser behavior.

When wrapping history methods:

1. Save the original function.
2. Call it with the original `this` value and arguments.
3. Preserve its return value and thrown errors.
4. Schedule a refresh after the call succeeds.
5. Restore the original function in `stop()`.

Keep the patch installed only once. A second `start()` must not wrap an already wrapped function.

## Debounce and Bound Retries

Debounce refreshes from bursts of DOM and route signals. A timer is a resource and must be cleared during teardown.

For a target that appears after a known asynchronous render, use a finite retry budget with increasing delays. Reset the budget when the route changes. Stop retrying after the budget is exhausted and leave the page usable; do not create an unbounded `setInterval` or recursive timeout.

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

The browser APIs in this fragment need no Tampermonkey grant. The refresh function must still check that the controller is running before acting.

## Route Re-entry and Idempotence

Route handling should be a reconciliation operation:

- If the URL is outside the feature route, remove the script-owned route UI and cancel route-specific retries.
- If the URL is inside the route and the marker already exists, update only the necessary state.
- If the URL is inside the route and the target host is missing, schedule a bounded retry.
- If the target appears, create the UI once and bind listeners once.
- When the application replaces the target, let the next refresh find it again instead of keeping references to detached page nodes.

Never assume that a URL change means the old DOM is still valid. Never assume that a DOM mutation means the route changed. Keep URL state and DOM state as separate inputs to `refresh()`.

## Complete Controller Pattern

This example uses only browser APIs, so it intentionally has no `GM_*` calls and no Tampermonkey API grant. Add a grant only if an adapted version uses a Tampermonkey API. The example route and selector are placeholders.

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

The controller stores its `pagehide` handler and removes it in `stop()`, so a repeated `start()` while running is ignored and a later start after `stop()` installs exactly one fresh handler. The route listener, observer, timers, history patch, and controller-created panel are explicitly released. The `panelOwned` flag prevents a route exit or teardown from removing a page-owned or other-script-owned node that merely has the same marker.

Do not patch history without considering other extensions or page code that may also wrap it. Preserve call semantics and restore only the function reference that this instance saved. If the reference has changed since patching, stop should avoid overwriting another wrapper; adapt the restoration policy to the target page.

## Cleanup

Cleanup must disconnect the `MutationObserver`, remove the `popstate` listener, clear debounce and retry timers, remove route-owned nodes, and restore history methods only when this controller still owns its wrappers. A route exit is also a cleanup event even when the document itself remains open.

## Dynamic-Page Review

- [ ] DOM changes are observed with a bounded, debounced refresh.
- [ ] The observer watches the smallest practical root and only needed mutation types.
- [ ] `pushState`, `replaceState`, and `popstate` behavior is covered.
- [ ] History methods are patched once, called with the original receiver, and restored.
- [ ] Route re-entry resets route-specific retry state.
- [ ] Retries have a finite maximum and are cancelled during teardown.
- [ ] Existing markers prevent duplicate UI and duplicate listeners.
- [ ] Detached page nodes are not retained indefinitely.
- [ ] `start`, `refresh`, and `stop` have clear ownership and error behavior.
- [ ] The script does not claim that `@run-at` means application readiness.

## Official References

- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey URL-change API documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=window#api:window.onurlchange)
- [MDN `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [MDN `history.pushState`](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState)
- [MDN `history.replaceState`](https://developer.mozilla.org/en-US/docs/Web/API/History/replaceState)
- [MDN `popstate`](https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event)
