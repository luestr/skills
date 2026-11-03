# 11. Debugging and Compatibility

Debug userscripts from the outside in. First prove that Tampermonkey matches and starts the script, then prove that the script reaches the intended route and lifecycle point, and only then debug selectors, permissions, network behavior, sandbox boundaries, or browser differences. A single console error can be a symptom of an earlier mismatch, so keep the diagnosis order stable.

## Diagnosis Order

1. **Script not running:** Confirm the script is enabled, installed, not excluded, and allowed to run on the current site. Check the Tampermonkey dashboard and the page's extension indicator.
2. **Wrong page:** Compare the exact scheme, host, port, path, query, hash, frame, and `@match` pattern. A script that matches a host is not necessarily intended for every route on that host.
3. **Timing:** Check `@run-at`, but do not interpret `document-end` or `document-idle` as application readiness. The target may be rendered later by a framework.
4. **Selector:** Inspect the live DOM, verify the selector's scope and spelling, and check whether the page replaces the node after the script finds it.
5. **Lifecycle:** For an SPA, verify `pushState`, `replaceState`, `popstate`, DOM observation, debounce, retry limits, and cleanup. Confirm that the UI does not duplicate after route changes.
6. **Permission:** Check every `GM_*` call against its `@grant`, and look for a Tampermonkey prompt or a disabled extension permission.
7. **Cross-origin:** Verify `@connect`, exact request host, status handling, timeout, response shape, and service availability. CORS behavior for native browser requests differs from `GM_xmlhttpRequest`.
8. **CSP:** Determine whether the failure is page-context script injection, a blocked resource, or a normal DOM operation. Do not assume that changing CSP is possible or safe.
9. **Sandbox:** Inspect whether the code needs page globals, `unsafeWindow`, a bridge, or a version-specific `@sandbox` mode. Minimize the bridge before changing execution context.
10. **Iframe:** Check whether the target is in the top document or a frame, whether `@noframes` applies, and whether the frame is same-origin.
11. **Browser-specific behavior:** Reproduce in each supported browser and record its version, Tampermonkey version, extension mode, permission prompts, and console output.

This order prevents a missing `@match` from being misdiagnosed as a selector failure and prevents a blocked permission from being mistaken for a server outage.

## Console Placement and Safe Diagnostics

Use the console that corresponds to the execution context. A page-console log may not show a userscript exception, and a userscript sandbox log may not show a page-context bridge error. Record the current URL, script version, route, and safe state summary. Do not paste tokens, cookies, full page text, or raw response bodies into a bug report.

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

Keep the wrapper disabled by default for a shipped script. If a persistent debug setting is available, validate it and provide a menu command or explicit user action to enable it. `GM_log` can be used when extension-mediated logs are needed, but it requires `@grant GM_log` and still must receive redacted data.

## Inspect `GM_info`

`GM_info` is useful for a diagnostic panel or a temporary report. It can reveal the script's name, version, handler, and mode information that helps explain compatibility differences. Declare `@grant GM_info` when calling the API form supported by the target environment, and do not use metadata as an authorization decision.

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

The shape of metadata can differ between API forms and handlers. Use optional access and display `unknown` rather than crashing the script when a field is absent.

## Feature Detection and Version Notes

Feature detection should test the operation the script will use, not just a global name. For example, check `typeof GM_xmlhttpRequest === 'function'` before using the callback API and check the exact namespaced function before using `GM.xmlHttpRequest`. Also verify that the metadata grant, `@connect` host, and browser permission are present; a defined function does not prove the operation is permitted.

Document version-specific behavior near the code that depends on it. Current Tampermonkey documentation labels bulk storage APIs such as `GM_getValues`, `GM_setValues`, and `GM_deleteValues` as `5.3+`; it labels `@sandbox` as `4.18+`, and some request or download options have later build labels. Choose a minimum version, test it, and provide a simpler single-key or browser-API path only when the product actually supports older installations.

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

Do not silently fall back from an approved cross-origin request to page `fetch` if that changes CORS, credential, or privacy behavior. Show an unsupported-state message and document the missing capability.

## Error Reproduction Notes

For each failure, record:

- Browser and version, Tampermonkey version, script version, and operating system.
- Exact URL, top-frame or iframe context, and whether the page was freshly loaded or navigated within an SPA.
- Expected state, observed state, console location, and first relevant error.
- Whether the extension was enabled, the matching rule changed, or a permission prompt was dismissed.
- A minimal sequence that reproduces the failure without private page data.

Reload after metadata changes because matching and permissions are evaluated at script startup. Test a clean profile or a fresh script install when stored settings or stale grants could affect the result. Preserve a safe export of the current setting schema before testing migration code.

## Debugging Review Checklist

- [ ] Match, enabled state, exclusions, frame scope, and exact URL were checked first.
- [ ] Timing and SPA lifecycle were tested separately from selector correctness.
- [ ] Every API grant and `@connect` host was checked against the failing call.
- [ ] Console output identifies the execution context and redacts sensitive data.
- [ ] `GM_info` is optional and used only for diagnostics.
- [ ] Feature detection checks the actual API form and does not hide permission failures.
- [ ] Version labels and minimum support are documented near dependent code.
- [ ] CSP, sandbox, iframe, and browser-specific failures have separate reproductions.
- [ ] A failure leaves the page usable and explains the next safe action.

## Official References

- [Tampermonkey FAQ: console output](https://www.tampermonkey.net/faq.php?locale=en&q=Q600)
- [Tampermonkey `GM_info`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_info)
- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey `@sandbox`](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey `@noframes`](https://www.tampermonkey.net/documentation.php?locale=en&q=noframes)
- [Tampermonkey FAQ: scripts executing unexpectedly](https://www.tampermonkey.net/faq.php?locale=en&q=Q405)
- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
