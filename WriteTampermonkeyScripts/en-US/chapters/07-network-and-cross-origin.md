# 07. Network and Cross-Origin Requests

Network access is a boundary, not just another data source. A page's browser APIs are subject to the page's origin and CORS policy. Tampermonkey's `GM_xmlhttpRequest` is dispatched by Tampermonkey's background context and can make approved cross-origin requests, but it still requires explicit host permission and careful response handling.

## Choose the Request API

Use the native `fetch` API when the request is same-origin or the target service intentionally supports the page's CORS policy. It is a browser API and needs no Tampermonkey grant. Use `GM_xmlhttpRequest` when a userscript needs an approved cross-origin request that the page's CORS policy would otherwise prevent.

| Need | API | Permission and notes |
| --- | --- | --- |
| Same-origin request | Browser `fetch` | No Tampermonkey grant; normal browser CORS and CSP rules apply. |
| Approved cross-origin request | `GM_xmlhttpRequest` | Add `@grant GM_xmlhttpRequest` and an exact `@connect` host. |
| Promise-based request | `GM.xmlHttpRequest` | Check the installed Tampermonkey version and namespaced grant syntax before adopting it. The documented name contains an uppercase `H` in `Http`. |

`GM_xmlhttpRequest` does not make an untrusted URL safe. A broad `@connect *` expands the permission boundary and makes an input-validation bug more serious. Declare the smallest set of hosts that the feature actually needs. Tampermonkey can ask the user to approve a newly encountered host, so an unexpected permission prompt is a behavior to handle, not a reason to silently retry forever.

## Metadata and Request Lifecycle

The following metadata is the minimum for the callback-based API in this example. The `@connect` value is a host allowlist entry, not a replacement for URL validation.

```js
// ==UserScript==
// @name         Approved API Request Example
// @namespace    https://userscripts.example.com/approved-request
// @version      1.0.0
// @match        https://app.example.com/reports/*
// @grant        GM_xmlhttpRequest
// @connect      api.example.com
// ==/UserScript==
```

Common callbacks have distinct meanings:

- `onload` means a response was received. It does not mean the HTTP status is successful. Check `status` yourself.
- `onerror` means the request could not complete normally. Display a recoverable state and avoid exposing raw response data.
- `ontimeout` is a bounded failure and should be reported separately when a retry may be useful.
- `onabort` means the script or user cancelled the request. Do not show a server error for an intentional abort.
- `onprogress` and `onreadystatechange` are optional instrumentation hooks. Do not perform expensive rendering for every progress event.
- The returned request handle exposes `abort()`. Keep it while a panel owns the request and call it during teardown or route exit.

Validate all of the following before using response data:

1. The final URL is present, is a string, and matches the fixed approved origin, endpoint path, query, and hash policy.
2. The status is in the accepted range, normally `200 <= status < 300`.
3. The body is present and parses as the expected format.
4. The parsed value has the required shape, types, bounds, and identifiers.

Require `finalUrl` to be a string and reject the response when it is missing, malformed, or outside the fixed approved origin, exact endpoint path, query, or hash policy. When response headers provide `Content-Type`, accept only JSON media types such as `application/json` or `application/*+json`. Define a clear maximum response size and measure the body before `JSON.parse`; oversized bodies must fail with a bounded, user-safe message.

Do not treat a `200` response as trusted HTML. Render text with `textContent`, create attributes from validated values, and reject unexpected fields when they would change a security-sensitive operation.

## Typed-by-Convention Helper

JavaScript does not enforce the request and response types at runtime. JSDoc types document the contract for editors and static tooling; the runtime checks remain necessary. This helper accepts only a fixed API origin, limits retries, validates JSON, and gives the caller a single success or failure result.

```js
// ==UserScript==
// @name         Typed-by-Convention Request Helper
// @namespace    https://userscripts.example.com/request-helper
// @version      1.0.0
// @match        https://app.example.com/reports/*
// @grant        GM_xmlhttpRequest
// @connect      api.example.com
// ==/UserScript==

(() => {
  'use strict';

  /** @typedef {{ id: string, label: string, value: number }} ReportRow */
  /** @typedef {{ rows: ReportRow[] }} ReportResponse */
  /** @typedef {{ ok: true, value: ReportResponse } | { ok: false, error: string, retryable: boolean }} RequestResult */

  const API_ORIGIN = 'https://api.example.com';
  const API_PATH = '/v1/reports/current';
  const REQUEST_TIMEOUT_MS = 8000;
  const MAX_ATTEMPTS = 3;
  const RETRY_DELAY_MS = 400;
  const MAX_RESPONSE_BYTES = 1_000_000;

  function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  /** @param {unknown} value @returns {ReportResponse} */
  function parseReportResponse(value) {
    if (!isRecord(value) || !Array.isArray(value.rows)) {
      throw new Error('Response schema is invalid');
    }

    const rows = value.rows.map((row) => {
      if (!isRecord(row) || typeof row.id !== 'string' || row.id.length > 100) {
        throw new Error('Response row id is invalid');
      }
      if (typeof row.label !== 'string' || row.label.length > 500) {
        throw new Error('Response row label is invalid');
      }
      if (typeof row.value !== 'number' || !Number.isFinite(row.value)) {
        throw new Error('Response row value is invalid');
      }
      return { id: row.id, label: row.label, value: row.value };
    });

    return { rows };
  }

  /** @returns {string} */
  function makeApiUrl() {
    const url = new URL(API_PATH, API_ORIGIN);
    if (url.origin !== API_ORIGIN || url.pathname !== API_PATH || url.search !== '' || url.hash !== '') {
      throw new Error('Request URL is outside the approved endpoint');
    }
    return url.href;
  }

  /** @param {unknown} response @param {URL} expectedUrl @returns {boolean} */
  function hasApprovedFinalUrl(response, expectedUrl) {
    if (!isRecord(response) || typeof response.finalUrl !== 'string') return false;
    try {
      const finalUrl = new URL(response.finalUrl);
      return finalUrl.origin === API_ORIGIN
        && finalUrl.pathname === expectedUrl.pathname
        && finalUrl.search === expectedUrl.search
        && finalUrl.hash === expectedUrl.hash;
    } catch {
      return false;
    }
  }

  /** @param {unknown} response @returns {boolean} */
  function hasJsonContentType(response) {
    if (!isRecord(response) || typeof response.responseHeaders !== 'string') return true;
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

  /** @param {string} url @returns {Promise<RequestResult>} */
  function requestReport(url) {
    return new Promise((resolve) => {
      let settled = false;
      let requestHandle = null;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        resolve(result);
      };

      requestHandle = GM_xmlhttpRequest({
        method: 'GET',
        url,
        timeout: REQUEST_TIMEOUT_MS,
        headers: { Accept: 'application/json' },
        onload(response) {
          if (response.status < 200 || response.status >= 300) {
            finish({ ok: false, error: `Server returned HTTP ${response.status}`, retryable: response.status >= 500 });
            return;
          }
          const expectedUrl = new URL(url);
          if (!hasApprovedFinalUrl(response, expectedUrl)) {
            finish({ ok: false, error: 'Response final URL is outside the approved API', retryable: false });
            return;
          }
          if (!hasJsonContentType(response)) {
            finish({ ok: false, error: 'Response content type is not JSON', retryable: false });
            return;
          }

          try {
            const raw = response.responseText;
            if (typeof raw !== 'string') {
              finish({ ok: false, error: 'Response body is not text', retryable: false });
              return;
            }
            const responseBytes = new TextEncoder().encode(raw).byteLength;
            if (responseBytes > MAX_RESPONSE_BYTES) {
              finish({ ok: false, error: `Response body exceeds ${MAX_RESPONSE_BYTES} bytes`, retryable: false });
              return;
            }
            const parsed = JSON.parse(raw);
            finish({ ok: true, value: parseReportResponse(parsed) });
          } catch (error) {
            finish({ ok: false, error: `Invalid JSON response: ${String(error.message || error)}`, retryable: false });
          }
        },
        onerror() {
          finish({ ok: false, error: 'The request could not reach the service', retryable: true });
        },
        ontimeout() {
          finish({ ok: false, error: 'The service did not respond in time', retryable: true });
        },
        onabort() {
          finish({ ok: false, error: 'The request was cancelled', retryable: false });
        },
      });

      // Keep a handle in the closure so a larger controller can expose an abort path.
      void requestHandle;
    });
  }

  /** @returns {Promise<RequestResult>} */
  async function requestWithRetry() {
    const url = makeApiUrl();
    let lastResult = { ok: false, error: 'No request was attempted', retryable: true };

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
      lastResult = await requestReport(url);
      if (lastResult.ok || !lastResult.retryable || attempt === MAX_ATTEMPTS) return lastResult;
      await new Promise((resolve) => window.setTimeout(resolve, RETRY_DELAY_MS * attempt));
    }

    return lastResult;
  }

  function showResult(result) {
    const status = document.querySelector('[data-report-status]');
    if (!status) return;
    status.textContent = result.ok ? `Loaded ${result.value.rows.length} rows` : `Report unavailable: ${result.error}`;
    status.dataset.state = result.ok ? 'ready' : 'error';
  }

  requestWithRetry().then(showResult).catch((error) => {
    showResult({ ok: false, error: 'Unexpected request failure', retryable: false });
    console.error('[request-helper] unexpected failure', error);
  });
})();
```

The example's `requestHandle` is kept inside the promise only to show where an abort handle belongs. A production controller should store that handle in its state and abort it when the panel is removed. Do not put a bearer token in a URL, log it in a callback, or copy it into page-visible DOM. Prefer a server design that authenticates through an approved browser credential or a short-lived, narrowly scoped credential; the correct choice depends on the service and browser permissions.

## Status, Timeout, Abort, and Retry Policy

Retries need a reason and a budget. Retry transient transport failures, timeouts, and selected `5xx` responses with a short backoff. Do not retry malformed JSON, `4xx` authorization errors, or a user cancellation unless the user explicitly asks to retry. Add jitter when many installations could retry at once.

Respect service rate limits:

- Do not poll on every DOM mutation or keystroke.
- Cache a result for an explicit, bounded lifetime when stale data is acceptable.
- Honor documented `Retry-After` information when the API supplies it.
- Use one in-flight request per route or key unless concurrent requests are intentional.
- Cancel route-specific work when the user leaves the route.

The UI should distinguish loading, ready, empty, and error states. A failure message should explain the next safe action, such as retrying, checking permission, or returning later. It should not tell the user to paste a token into a page field or expose a raw response body.

## Credentials and CORS Boundaries

`GM_xmlhttpRequest` and `fetch` do not have identical credential behavior. A request may include cookies, credentials, or custom headers only when the service, browser, Tampermonkey mode, and user permission support that behavior. Treat `anonymous`, `user`, `password`, and `cookie` request options as security-sensitive. Do not send page cookies or account identifiers to a host that is not required by the feature.

Cross-origin permission is not the same as server authorization. `@connect api.example.com` allows the userscript to request that host; it does not guarantee the endpoint accepts the request, that cookies are available, or that redirects are safe. Validate the final URL when a redirect could move data to another origin, and keep the approved host list narrow.

## Network Review Checklist

- [ ] Native `fetch` is used when the page's same-origin and CORS policy is sufficient.
- [ ] `GM_xmlhttpRequest` has `@grant GM_xmlhttpRequest` and an exact `@connect` host.
- [ ] URL construction rejects unexpected origins, schemes, and paths.
- [ ] `onload` rejects a missing or unapproved final URL, then validates status, exact final URL origin/path/query/hash, JSON content type when available, bounded body size before parsing, and response shape.
- [ ] Timeout, abort, transport error, and user cancellation have distinct handling.
- [ ] Retries are finite, rate-limited, and limited to retryable failures.
- [ ] In-flight requests are cancelled when their UI or route is gone.
- [ ] Credentials, tokens, cookies, and page secrets are not logged or disclosed.
- [ ] Loading, empty, success, and failure states are visible and recoverable.
- [ ] Version-specific namespaced APIs are verified against the installed Tampermonkey documentation.

## Official References

- [Tampermonkey `GM_xmlhttpRequest`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_xmlhttpRequest)
- [Tampermonkey `@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey FAQ: runtime host permissions](https://www.tampermonkey.net/faq.php?locale=en&q=Q306)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [MDN `fetch`](https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch)
