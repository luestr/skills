# 01. A Repeatable Userscript Workflow

A reliable userscript starts with a small, explicit contract. Before writing selectors or calling a `GM_*` API, identify where the script runs, what it changes, what it owns, and how it stops. The goal is a script that remains understandable when the page, URL, browser, or Tampermonkey configuration changes.

This chapter is about planning. Use the later chapters for the exact metadata, runtime, DOM, SPA, and storage details.

## 1. Discover the Requirement

Turn a request into observable behavior:

- What user action starts the behavior?
- What visible result means success?
- Which data may be read, changed, stored, or sent elsewhere?
- What must never be changed?
- What should happen when the target element, value, or service is unavailable?
- Is the behavior a one-time enhancement, a repeated route-aware feature, or a background synchronization task?

Write acceptance criteria that can be checked in a browser. For example, "adds one action to each order row" is testable; "improves order management" is not. Include negative cases such as an empty result, a malformed response, a permission denial, and a page that is not fully loaded.

Use browser APIs for page interaction whenever they are sufficient. Tampermonkey APIs are an extension to the browser environment, not a reason to make every operation privileged. A DOM query, event listener, `MutationObserver`, `URL`, `URLSearchParams`, `fetch`, and `localStorage` are browser APIs. APIs such as `GM_getValue`, `GM_addStyle`, `GM_xmlhttpRequest`, and `unsafeWindow` are Tampermonkey features and require deliberate metadata or compatibility decisions.

## 2. Analyze URLs and Frames

Record the URL scope before choosing `@match`:

1. List the protocols, hosts, subdomains, and paths that are actually required.
2. Decide whether a query string changes behavior. `@match` does not select by query string, so query checks belong in code.
3. Check whether the feature belongs in the top-level document, a same-origin frame, or a cross-origin frame.
4. Check whether a navigation changes `location.href` without a full reload. That is common in single-page applications and requires route observation.
5. Decide whether `@noframes` is appropriate. Use it only when the top-level document is the intended target.

Prefer an exact pattern such as `https://app.example.com/orders/*` over `*://*/*`. A broad pattern increases execution, review, privacy, and maintenance risk. See the [Tampermonkey `@match` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:match) and the [Tampermonkey `@noframes` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:noframes).

## 3. Model Page States

Do not treat the first successful DOM query as proof that the application is ready. Describe the states that matter:

- **Loading:** the document or required host does not exist yet.
- **Ready:** the target is present and has the data needed for the feature.
- **Empty:** the target exists but has no usable records.
- **Updating:** the application is replacing or appending content.
- **Unavailable:** the page is in an unsupported route, the user is logged out, or a required permission or service failed.
- **Leaving:** the document is being discarded and listeners, timers, styles, and owned nodes must be released.

Each state needs an explicit behavior. A bounded retry can move Loading to Ready. An idempotent refresh can handle Updating. An error message or a quiet no-op can handle Unavailable. Teardown must make Leaving safe even if startup failed halfway through.

`@run-at` selects an earliest injection opportunity, not application readiness. `document-end` and `document-idle` do not mean that an SPA has finished rendering its route. See the [Tampermonkey `@run-at` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at).

## 4. Assign Data Ownership

For every value, state who owns it and how long it should live:

| Data | Owner | Lifetime | Safe handling |
| --- | --- | --- | --- |
| Current button state | The script instance | Until route change or teardown | Keep in memory; reset when the target disappears |
| User preference | The userscript | Across reloads and tabs | Use namespaced Tampermonkey storage and validate on read |
| Page record | The page application | Until it changes | Read only what is needed; do not assume a stable object shape |
| Remote response | The request operation | Until consumed | Validate status, content type, size, and fields before use |
| DOM node created by the script | The script | Until teardown or route exit | Mark it and remove only what the script owns |

Do not persist DOM nodes, event handlers, promises, or arbitrary page objects. Persist a small versioned data structure. Keep secrets and sensitive page data out of storage and logs unless there is a specific, reviewed reason to retain them.

## 5. Plan Lifecycle and Teardown

Treat the script as a resource owner. List every resource created by startup:

- DOM nodes and style elements
- event listeners and `MutationObserver` instances
- timers and pending retry handles
- history method patches
- Tampermonkey storage listeners
- network requests and abort signals
- menu commands, tabs, or notifications

For each resource, record its cleanup operation. Make startup idempotent so a repeated call does not duplicate a panel, listener, timer, or request. Make teardown tolerant of partial initialization: optional resources may not exist when an earlier operation failed.

## 6. Plan Permissions

Start with no privileged API. Add one `@grant` only when a browser API cannot meet the requirement or when the Tampermonkey API provides a needed capability. Examples:

- Use `document.createElement` and `textContent` for ordinary DOM work; no Tampermonkey grant is needed.
- Use `GM_addStyle` for Tampermonkey-managed style injection; declare `@grant GM_addStyle`.
- Use `GM_getValue` and `GM_setValue` for userscript-scoped persistence; declare the matching grants.
- Use `GM_xmlhttpRequest` only for a demonstrated cross-origin request; declare both `@grant GM_xmlhttpRequest` and narrow `@connect` domains.
- Use `unsafeWindow` only when direct page JavaScript access is required; declare `@grant unsafeWindow` and document the trust boundary.

Keep `@require`, `@resource`, and `@sandbox` decisions visible in the plan. Pin external dependencies, review their source, and state the minimum Tampermonkey version when a feature is version-specific. The [Tampermonkey `@grant` documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=grant) describes the whitelist behavior and the special meaning of `@grant none`.

## 7. Use Progressive Enhancement

The script should leave the page usable when the enhancement cannot run:

1. Detect the required capability and target element.
2. Do not remove or rewrite unrelated page content when detection fails.
3. Add controls that have a clear accessible name and keyboard behavior.
4. Keep the original page action available when possible.
5. Show actionable errors for user-triggered failures, and use a bounded, observable recovery path for transient failures.
6. Avoid blocking the page while optional data or styling loads.

For changes to page content, prefer `textContent`, explicit attributes, and DOM APIs. Treat page text, URL parameters, storage values, and remote responses as untrusted input until validated. Do not construct executable HTML or JavaScript from those values.

## 8. A Repeatable Implementation Sequence

Use this sequence for each feature:

1. Write the acceptance criteria and the unsupported cases.
2. Select the narrowest `@match`, frame policy, and `@run-at`.
3. Define data ownership, persistence, and error behavior.
4. Draft the minimum `@grant` set and remove anything not used by code.
5. Implement small browser-API helpers for detection and safe DOM updates.
6. Make `start`, `refresh`, and `stop` idempotent where the page can change without reload.
7. Add bounded retries only for a known transient condition.
8. Exercise initial load, reload, route changes, empty states, malformed input, blocked permissions, and teardown.
9. Review the metadata and links before publishing. Record browser and Tampermonkey version assumptions.

## Planning Template

Copy this template into a design note before implementing a non-trivial script:

```md
# Feature: <short name>

## Scope
- Pages: <exact hosts and paths>
- Frames: <top-level only / named frame / matching frames>
- Route changes: <yes/no; how detected>
- Browser and Tampermonkey versions tested: <versions>

## Behavior
- Trigger: <user or page event>
- Success: <observable result>
- Unsupported or unavailable: <quiet no-op / visible error / fallback>

## State and ownership
- In-memory state: <values and reset points>
- Persistent state: <keys, schema version, defaults>
- Page-owned nodes: <read-only inputs>
- Script-owned nodes: <markers and cleanup>

## Permissions
- Metadata: <@match, @noframes, @run-at, @sandbox>
- Grants: <each @grant and why>
- External code or data: <@require, @resource, @connect, or none>

## Lifecycle
- start: <initialization and readiness check>
- refresh: <route or DOM update behavior>
- stop: <listeners, observers, timers, requests, nodes, styles>

## Verification
- Initial load: <steps>
- Dynamic update: <steps>
- Failure and recovery: <steps>
- Teardown: <steps>
```

## Definition of Done

- [ ] The target hosts, paths, protocols, and frame behavior are explicit.
- [ ] The feature has observable acceptance criteria and documented unsupported states.
- [ ] Page states and application readiness are not inferred from `@run-at` alone.
- [ ] Each piece of state has an owner, lifetime, validation rule, and persistence decision.
- [ ] The `@grant` list contains only APIs used by the script, and each use is justified.
- [ ] External dependencies and network domains are pinned or narrowly declared and reviewed.
- [ ] DOM changes use null checks, safe text or attribute APIs, and stable markers.
- [ ] Re-entry and refresh are idempotent; retries are bounded.
- [ ] Teardown releases every listener, observer, timer, request, storage listener, style, and owned node.
- [ ] Initial load, reload, route change, empty state, malformed input, permission failure, and teardown were exercised.
- [ ] Browser and Tampermonkey version-specific behavior is stated.

## Official References

- [Tampermonkey Documentation](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey `@match`](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:match)
- [Tampermonkey `@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [MDN Web APIs](https://developer.mozilla.org/en-US/docs/Web/API)
