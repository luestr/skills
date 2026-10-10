# 09. Context Communication

A userscript can run in a Tampermonkey sandbox, interact with the page DOM, observe other instances of the same script through Tampermonkey storage, and exchange messages with page or frame contexts. These channels have different trust and lifetime properties. Treat every boundary as an input-validation boundary and keep privileged APIs inside the userscript.

## Select a Communication Channel

| Channel | Useful for | Boundary and limits |
| --- | --- | --- |
| `GM_addValueChangeListener` | Synchronizing settings or state between instances of the same script | Requires storage listener grants; receives a `remote` flag, but is not a transaction or general message bus. |
| `window.postMessage` | A structured message between a page window and another window or frame | Validate `event.source`, exact `event.origin`, message shape, and allowed message types. |
| Custom DOM events | Small page-DOM signals between code sharing a document | Events are observable by page scripts; never put credentials or privileged function handles in `detail`. |
| Page-context bridge | Calling or observing a page-owned library or variable | `unsafeWindow` crosses into page-owned objects and increases the attack surface. Prefer a narrow event bridge. |
| Direct frame access | Communication with a same-origin iframe | Same-origin policy and frame lifecycle apply; cross-origin frames need messaging and explicit cooperation. |

There is no universal cross-script channel. Tampermonkey storage is normally scoped to a userscript, so one script should not assume that another script can read its keys. `postMessage` can reach a page window or frame that participates in the channel, but it does not bypass origin policy or make a recipient trustworthy. If several independently installed scripts must communicate, define a documented, versioned protocol and accept that page code may observe it.

## Synchronize Same-Script Tabs

`GM_addValueChangeListener` is the natural channel for a setting shared by multiple tabs of the same userscript. The callback receives `key`, `oldValue`, `newValue`, and `remote`. Use `remote` to avoid re-rendering for a local write that the current instance already applied, but do not assume ordering, locking, atomic updates across keys, or conflict resolution.

```js
// ==UserScript==
// @name         Same-Script Tab Sync
// @namespace    https://userscripts.example.com/tab-sync
// @version      1.0.0
// @match        https://app.example.com/*
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_addValueChangeListener
// @grant        GM_removeValueChangeListener
// ==/UserScript==

(() => {
  'use strict';

  const key = 'tab-sync.enabled';
  let enabled = true;
  let listenerId = null;

  function readEnabled() {
    try {
      return GM_getValue(key, true) === true;
    } catch (error) {
      console.error('[tab-sync] read failed', error);
      return true;
    }
  }

  function render() {
    document.documentElement.dataset.tabSyncEnabled = String(enabled);
  }

  function setEnabled(nextEnabled) {
    const nextValue = nextEnabled === true;
    try {
      GM_setValue(key, nextValue);
      enabled = nextValue;
      render();
    } catch (error) {
      console.error('[tab-sync] write failed', error);
    }
  }

  function stop() {
    if (listenerId === null) return;
    try {
      GM_removeValueChangeListener(listenerId);
    } finally {
      listenerId = null;
    }
  }

  enabled = readEnabled();
  render();
  listenerId = GM_addValueChangeListener(key, (_key, _oldValue, newValue, remote) => {
    if (!remote) return;
    enabled = newValue === true;
    render();
  });
  window.addEventListener('pagehide', stop, { once: true });

  // A real UI command would call setEnabled(value); it is intentionally not
  // exposed to page scripts or stored as a window property.
  void setEnabled;
})();
```

Persist a versioned aggregate when several settings must be interpreted together. If two tabs can edit the same value, define whether last-writer-wins, validated field merge, or explicit revision checks are required. Remove the listener during teardown, including a partial-start failure.

## Validate `postMessage`

An origin check must be exact. Do not use `'*'` as `targetOrigin` for a sensitive message, and do not accept a message solely because its `type` string looks familiar. Check the sender window, the exact origin, a bounded payload, and the expected protocol version.

```js
// Page window and userscript share this exact origin in this example.
const TRUSTED_ORIGIN = 'https://app.example.com';
const PROTOCOL_VERSION = 1;

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isSafeRequestMessage(value) {
  return (
    isRecord(value) &&
    value.channel === 'report-panel' &&
    value.version === PROTOCOL_VERSION &&
    value.type === 'request-refresh' &&
    typeof value.requestId === 'string' &&
    value.requestId.length > 0 &&
    value.requestId.length <= 80
  );
}

function onMessage(event) {
  if (event.source !== window || event.origin !== TRUSTED_ORIGIN) return;
  if (!isSafeRequestMessage(event.data)) return;

  // Perform the privileged work inside the userscript. Do not send a
  // GM_xmlhttpRequest function, token, or storage value to the page.
  refreshReport().then((summary) => {
    window.postMessage({
      channel: 'report-panel',
      version: PROTOCOL_VERSION,
      type: 'refresh-result',
      requestId: event.data.requestId,
      ok: true,
      summary: { count: summary.count },
    }, TRUSTED_ORIGIN);
  }).catch(() => {
    window.postMessage({
      channel: 'report-panel',
      version: PROTOCOL_VERSION,
      type: 'refresh-result',
      requestId: event.data.requestId,
      ok: false,
    }, TRUSTED_ORIGIN);
  });
}

window.addEventListener('message', onMessage);
window.addEventListener('pagehide', () => {
  window.removeEventListener('message', onMessage);
}, { once: true });
```

The receiving code must still validate values returned by `refreshReport()` before rendering them. A message protocol should be bounded in size and rate when page code can trigger it repeatedly. If the trusted page origin can change during navigation, recompute an explicitly allowed origin from the current route and reject stale messages.

## Custom Events and Page-Context Bridges

Custom events are convenient when both sides share a document, but the page can dispatch the same event and inspect event data. Use a namespaced event name and a plain-data detail object, then validate the detail just as if it arrived over `postMessage`.

`unsafeWindow` exposes the page's `window` rather than the extension window. It can be necessary to inspect a page-owned library, but page scripts can influence page-owned objects and may be able to interfere with a bridge. Keep the bridge narrow: exchange immutable, schema-checked data through events or messages, and keep all `GM_*` calls, tokens, storage, and request handles private to the userscript. Do not attach a privileged function such as `window.myUserscriptFetch = ...` to the page.

Tampermonkey's `@sandbox` metadata can select an execution context, and the documentation marks it as version-specific (`4.18+`). Do not use it as a portable guarantee across handlers or browsers. Check the installed version and test the exact bridge in the target environment.

## Iframes and Window Boundaries

An iframe has its own document, URL, event listeners, and lifecycle. A script that should run only in the top page can declare `@noframes`; a script that should enhance a frame must match the frame URL and use frame-local selectors. `window.top`, `window.parent`, and `event.source` are not interchangeable with the current window.

For same-origin frames, direct DOM or `contentWindow` access may be possible, but wait for the frame load and clean up when it is replaced. For cross-origin frames, use `postMessage` with an exact target origin and require cooperation from the frame. Never lower validation because the frame is embedded by a page you trust.

## Communication Review Checklist

- [ ] Same-script tab state uses a versioned value and a removed change listener.
- [ ] Cross-script assumptions are explicit; storage is not treated as a universal bus.
- [ ] `postMessage` checks exact `event.origin`, `event.source`, protocol version, type, and payload shape.
- [ ] Sensitive messages use an exact `targetOrigin`, never `'*'`.
- [ ] Custom event details contain bounded plain data and no credentials or privileged functions.
- [ ] Page-context bridges keep GM APIs, tokens, and storage private.
- [ ] `unsafeWindow` and `@sandbox` use are justified and version-tested.
- [ ] Iframe behavior distinguishes top windows, same-origin frames, and cross-origin frames.
- [ ] Listeners, observers, timers, and bridge hooks are removed during teardown.

## Official References

- [Tampermonkey `GM_addValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_addValueChangeListener)
- [Tampermonkey `GM_removeValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_removeValueChangeListener)
- [Tampermonkey `unsafeWindow`](https://www.tampermonkey.net/documentation.php?locale=en&q=unsafeWindow)
- [Tampermonkey `@sandbox`](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey `@noframes`](https://www.tampermonkey.net/documentation.php?locale=en&q=noframes)
- [MDN `Window.postMessage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [MDN `Window: message` event](https://developer.mozilla.org/en-US/docs/Web/API/Window/message_event)
