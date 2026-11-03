# 10. Security and Privacy

A userscript combines page-controlled input with extension-mediated capabilities. The page can change its DOM, navigation, timing, and JavaScript objects while the script is running. Security therefore depends on reducing privileges, validating boundaries, limiting disclosure, and making side effects visible to the user.

## Threat Model First

Before writing a script, identify:

- What page origins and URL paths can start it?
- Which page text, attributes, URLs, form values, messages, frames, and network responses are untrusted?
- Which capabilities can disclose data or cause an external side effect?
- Which data is sensitive, where can it be stored, and how long should it remain?
- Can a compromised page, third-party library, redirect, or updated API observe or influence the operation?
- What will the user see before a download, external request, clipboard write, or account action?

The answers should determine the metadata, not the other way around. A script that only adds a local button should not need network, storage, clipboard, or unsafe window access.

## Least Privilege Metadata

Use precise `@match` entries for the actual scheme, host, and route. Avoid `@include *`, broad host patterns, and unnecessary `@noframes` exceptions. Add one `@grant` for each privileged API used and remove grants after refactoring. Use exact `@connect` hosts for cross-origin requests, and never treat `@connect *` as a harmless convenience.

```js
// ==UserScript==
// @name         Narrowly Scoped Enhancement
// @namespace    https://userscripts.example.com/narrow-enhancement
// @version      1.0.0
// @match        https://shop.example.com/products/*
// @grant        none
// @noframes
// ==/UserScript==
```

`@grant none` is appropriate only when the script uses browser APIs and no Tampermonkey API. If the script calls a `GM_*` API, declare the matching grant explicitly. `@sandbox` and other metadata entries are version-specific; document a minimum version and test the actual execution context rather than claiming universal support.

## DOM Injection and XSS

Page text and attributes are untrusted even when they look like labels. Prefer `textContent`, `createElement`, and explicit property assignment. Avoid `innerHTML` for values that came from the page, a network response, storage, a query string, or a message. If a trusted template must be parsed, keep dynamic values out of its HTML source and sanitize the result with a reviewed sanitizer before insertion.

Do not turn untrusted strings into selectors, CSS, URLs, or JavaScript. If a selector must include an identifier, validate its character set and length or use `CSS.escape` where the browser support and selector semantics are appropriate. Never evaluate page text with `eval`, `Function`, or string-built event handlers.

```js
const productStatusOwnerSelector = ':scope > [data-tm-product-status-region-owner="true"]';

function renderProductStatus(host, product) {
  let region = host.querySelector(productStatusOwnerSelector);
  if (!region) {
    region = document.createElement('div');
    region.dataset.tmProductStatusRegionOwner = 'true';
    region.setAttribute('aria-live', 'polite');
    host.append(region);
  }

  const status = document.createElement('span');
  status.className = 'tm-product-status';
  status.textContent = typeof product.status === 'string'
    ? product.status.slice(0, 120)
    : 'Status unavailable';

  const detailsUrl = safeProductUrl(product.detailsUrl);
  if (detailsUrl !== null) {
    const detailsLink = document.createElement('a');
    detailsLink.textContent = 'View details';
    detailsLink.href = detailsUrl;
    detailsLink.rel = 'noopener noreferrer';
    detailsLink.target = '_blank';
    region.replaceChildren(status, detailsLink);
    return;
  }

  const unavailable = document.createElement('span');
  unavailable.textContent = 'Details are unavailable for this product.';
  unavailable.dataset.state = 'unavailable';
  region.replaceChildren(status, unavailable);
}

function safeProductUrl(value) {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value, location.href);
    if (url.protocol !== 'https:' || url.origin !== location.origin || !url.pathname.startsWith('/products/')) return null;
    return url.href;
  } catch {
    return null;
  }
}
```

An invalid URL produces explanatory text instead of an active link. `host` is caller-provided and may contain page-owned children, so `renderProductStatus` creates or reuses only its direct `data-tm-product-status-region-owner="true"` child and calls `replaceChildren` only inside that script namespace's owned region. It never clears the page-owned host itself or reuses a generic status marker. If a design needs a control in that state, render a disabled button with `disabled` rather than assigning `'#'`. Always bound text length and array counts before rendering a response that could be unusually large.

## URLs, Requests, and Disclosure

Validate URL scheme, origin, path, and any required identifier before opening a tab, fetching a resource, setting an image source, or downloading a file. Accept only `https:` unless the feature explicitly requires another scheme. Reject `javascript:`, `data:`, `file:`, and unexpected custom schemes for navigation and resource attributes.

Cross-origin disclosure includes more than response bodies. Query parameters, headers, cookies, referrers, download filenames, logs, and timing can reveal account or page information. Do not send page secrets to a service merely because `GM_xmlhttpRequest` can reach it. Remove tokens from URLs and error messages, use the narrowest request payload, and validate redirected final URLs when the API or handler supports redirects.

## Storage and Sensitive Values

Tampermonkey storage is scoped to a userscript but is not a secure secret vault. Do not store passwords, long-lived bearer tokens, session cookies, private documents, or full page snapshots unless the risk, retention, and user consent have been explicitly reviewed. Store the smallest non-sensitive settings possible, validate them on read, and include a schema version for migrations.

Avoid logging storage values. A debug statement can leak a secret to extension logs, the page console, a bug report, or a screen recording. When a diagnostic needs an identifier, log a short non-reversible label or a redacted prefix instead.

## Supply Chain and `@require`

An `@require` script executes with the userscript's authority. Review its source, update policy, ownership, and transitive dependencies. Pin to a reviewed version and use Tampermonkey's documented Subresource Integrity form when a stable hash is available:

```js
// @require      https://cdn.example.com/reviewed-lib@1.4.2/lib.min.js#sha256-BASE64_HASH
```

Replace `BASE64_HASH` with the real hash produced by the release process. An illustrative placeholder is not a valid integrity check. Re-review the hash when intentionally upgrading and keep the dependency out entirely when a small local implementation is clearer and less risky.

The same review applies to `@resource` content, remote configuration, and response-driven code. Never execute JavaScript received from a request or page field. A content security policy can block some page-context operations, but CSP is not a sanitizer and should not be relied on as the script's primary defense.

## `unsafeWindow`, Downloads, and Consent

`unsafeWindow` provides the page's `window` and therefore crosses into objects controlled by page code. Use it only for a narrow, documented integration. Keep privileged functions, request handles, storage access, and credentials in the userscript sandbox. Exchange schema-checked plain data through a validated event or message channel.

Downloads through `GM_download` (which requires `@grant GM_download`), clipboard writes, external requests, and account changes are user-visible side effects. Require a clear action or confirmation when the trigger is not obvious, show the destination or filename, and report success or failure. Do not silently upload page content, auto-download a large file, or copy a secret as part of startup.

## Threat-Model Checklist

- [ ] `@match` is precise for scheme, host, path, frame scope, and lifecycle.
- [ ] `@grant` lists only the APIs actually used; `@connect` lists only required hosts.
- [ ] DOM text and attributes are inserted without unsafe HTML or string-built handlers.
- [ ] Selectors, URLs, schemes, paths, and lengths are validated before use.
- [ ] Network payloads, headers, redirects, and errors do not disclose page secrets.
- [ ] Stored values are non-sensitive where possible, schema-checked, and not logged.
- [ ] `@require` and `@resource` sources are pinned, reviewed, and integrity-protected when feasible.
- [ ] `unsafeWindow` and page bridges expose no privileged functions or credentials.
- [ ] Downloads, clipboard writes, external requests, and account actions have transparent consent.
- [ ] Failure states preserve privacy and do not display raw response bodies or secrets.
- [ ] Security assumptions are tested in the target browser and Tampermonkey version.

## Official References

- [Tampermonkey `@match`](https://www.tampermonkey.net/documentation.php?locale=en&q=match)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)
- [Tampermonkey `unsafeWindow`](https://www.tampermonkey.net/documentation.php?locale=en&q=unsafeWindow)
- [Tampermonkey Subresource Integrity](https://www.tampermonkey.net/documentation.php?locale=en&q=sri)
- [Tampermonkey `@require`](https://www.tampermonkey.net/documentation.php?locale=en&q=externals)
- [Tampermonkey FAQ: required permissions](https://www.tampermonkey.net/faq.php?locale=en&q=Q304)
- [MDN Cross-site scripting](https://developer.mozilla.org/en-US/docs/Glossary/Cross-site_scripting)
- [MDN `innerHTML` security considerations](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML#security_considerations)
