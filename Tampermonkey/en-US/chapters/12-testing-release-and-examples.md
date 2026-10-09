# 12. Testing, Release, and Examples

Userscripts are small deployments with large environmental variation. A reliable release tests matching, lifecycle, permissions, page structure, network outcomes, and persisted state. Test the script in a clean browser profile as well as the profile in which it was developed.

## Test Matrix

| Scenario | What to verify | Expected result |
| --- | --- | --- |
| Matching | Exact scheme, host, path, query, hash, exclusions, and frame context | The script starts only on intended pages and has the expected frame scope. |
| Fresh page load | First run at the configured `@run-at` | Startup is idempotent and does not assume application readiness. |
| SPA navigation | `pushState`, `replaceState`, back, forward, and route exit | Route UI reconciles once, stale UI is removed, and history is restored on teardown. |
| Missing elements | Target absent permanently or temporarily | The page remains usable, retries are bounded, and the failure is observable. |
| Slow network | Delayed response, timeout, and partial progress | Loading state is clear, timeout is bounded, and abort releases the request. |
| Blocked request | Missing `@connect`, denied permission, DNS failure, `4xx`, `5xx`, invalid JSON | The script distinguishes permission, transport, server, and parse failures without leaking data. |
| Multiple tabs | Same script running in two tabs and a remote setting change | Change listeners update valid state without assuming transactions or duplicating UI. |
| Reload | Reload after a panel, listener, timer, or request exists | No stale listener, observer, timer, or duplicated marker survives the new run. |
| Disabled permission | Disable a grant or reject an extension prompt | The script reports unsupported or blocked behavior and leaves the page usable. |
| Update migration | Install an older stored schema, then upgrade and encounter unknown future data | Known data migrates deterministically; unsupported future data is preserved. |

For each row, record the browser, Tampermonkey version, script version, route, expected visible state, and console result. Include accessibility checks for keyboard focus, names, disabled states, readable status messages, and contrast when the script adds UI.

## Release Metadata and Changelog

Update `@version` for every behavior or permission change. Treat changes to `@match`, `@grant`, `@connect`, `@require`, `@resource`, storage schema, and external request shape as release notes, not implementation details. Explain new permission prompts and any user-visible migration or consent step.

Keep a changelog entry with:

- The released version and date.
- Added, changed, fixed, and removed behavior.
- New or removed grants, hosts, resources, and dependencies.
- Storage schema changes and the migration or rollback behavior.
- Supported browser and Tampermonkey version notes.
- Known limitations and a reproducible recovery step.

Use a stable `@namespace` and update metadata only through a reviewed distribution path. Verify the update and download URLs before publishing. Do not publish a script that points to an unreviewed mutable dependency or an overly broad permission pattern.

## Rollback and Migration

Keep the previous known-good script available and make rollback instructions explicit. A rollback must not overwrite data written by a newer schema without a deliberate downgrade policy. When a migration cannot understand a future schema, preserve the original value and use safe in-memory defaults. Test both upgrade and rollback from a clean profile and from a profile containing malformed values.

Before release, verify that a failed network request, missing selector, rejected permission, and update migration each produce a visible and recoverable state. A script should fail closed for privileged actions: no request, download, or account operation should run when its destination or input cannot be validated.

## Complete Example: Static Enhancement

This script uses only browser APIs, so it declares `@grant none`. It matches a product route precisely, adds one panel beside `[data-product-actions]`, and uses a marker plus `replaceChildren` to remain idempotent.

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

## Complete Example: SPA Enhancement

This controller uses a cross-execution sentinel before installing any resources. It observes a stable document root, patches history once, handles `popstate`, debounces refreshes, and removes its own panel when the route changes. It does not add a new observer or click listener on every refresh or script re-entry.

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

In a production script, coordinate history ownership with other code that may patch the same methods and avoid restoring a wrapper that another party installed after this script. Add bounded retries when a route host is known to render later, and cancel those timers in `stop()`.

## Complete Example: Cross-Origin Data Panel

This example requests a validated JSON summary from one approved host. It uses a timeout, status and schema checks, safe text rendering, and an abort handle. It stores only a non-sensitive display preference and never exposes credentials to the page.

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

The example strictly requires `response.finalUrl` to be present and to match the approved origin and `/v1/summary` path; adapt this only with an explicitly reviewed redirect policy. When `responseHeaders` provides `Content-Type`, it must identify JSON, and the body is bounded before parsing by `MAX_RESPONSE_BYTES`. Every callback finishes the current generation only when the panel and host are still connected, so a detached panel cannot be rendered into. The removal observer and `pagehide` handler both call the same teardown, which increments `requestGeneration`, aborts the active handle, disconnects the observer, removes the pagehide listener, removes the script-owned panel only when it is still attached to the owned host, and clears the panel and host references. Callbacks return without rendering after teardown. The example intentionally does not send page content or an access token. An authenticated deployment must define how the API authenticates requests, whether cookies are appropriate, and what user consent is required; do not add credentials just to make a sample appear to work.

## Release Review Checklist

- [ ] The full matrix covers matching, load, navigation, DOM absence, network delay, blocked permission, tabs, reload, and migration.
- [ ] Examples have language-tagged fences, precise metadata, minimal grants, and safe output.
- [ ] SPA controllers do not duplicate observers, route listeners, history wrappers, or UI.
- [ ] Cross-origin requests validate final origin/path, content type when available, bounded response size before parsing, status, response shape, timeout, abort, and user-visible errors.
- [ ] Cross-origin panel teardown observes panel/host removal, increments request generation, aborts the active handle, disconnects its removal observer, removes the pagehide listener, removes the owned panel from its owned host, and clears DOM references; callbacks cannot render after teardown.
- [ ] Storage contains only required non-sensitive state and has a migration policy.
- [ ] Release metadata, changelog, dependency integrity, and rollback instructions are reviewed.
- [ ] A known-good version can be restored without destroying newer stored data.

## Official References

- [Tampermonkey Documentation](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey FAQ](https://www.tampermonkey.net/faq.php?locale=en)
- [Tampermonkey `@version`](https://www.tampermonkey.net/documentation.php?locale=en&q=version)
- [Tampermonkey `@updateURL` and `@downloadURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url)
- [Tampermonkey `GM_xmlhttpRequest`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_xmlhttpRequest)
- [Tampermonkey `@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)
- [Tampermonkey storage APIs](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values)
- [MDN `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [MDN History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)
