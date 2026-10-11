# 02. Userscript Metadata

The metadata block is the script's execution contract. Tampermonkey reads it before executing the body, so URL scope, timing, privileges, dependencies, and update behavior must be correct before runtime code can compensate for a mistake.

The authoritative reference is the [Tampermonkey documentation](https://www.tampermonkey.net/documentation.php?locale=en). The links below use its metadata entries.

## Directive Reference

| Directive | Purpose and practical guidance |
| --- | --- |
| `@name` | Human-readable script name shown in Tampermonkey. Keep it stable and descriptive. See [`@name`](https://www.tampermonkey.net/documentation.php?locale=en&q=name#meta:name). |
| `@namespace` | Identifies the script together with `@name` and helps distinguish unrelated scripts with the same name. Use a stable namespace you control. See [`@namespace`](https://www.tampermonkey.net/documentation.php?locale=en&q=name#meta:namespace). |
| `@version` | Version used for update comparison and display. Increase it when behavior, permissions, dependencies, or stored data handling changes. See [`@version`](https://www.tampermonkey.net/documentation.php?locale=en&q=version). |
| `@description` | Short explanation shown in script management UI. State the target and user-visible behavior without promising unsupported coverage. See [`@description`](https://www.tampermonkey.net/documentation.php?locale=en&q=description). |
| `@author` | Publisher or maintainer identity. Keep it accurate and add a support URL when users need a way to report issues. See [`@author`](https://www.tampermonkey.net/documentation.php?locale=en&q=author). |
| `@match` | URL pattern for pages where the script may run. Prefer precise protocol, host, subdomain, and path patterns. See [`@match`](https://www.tampermonkey.net/documentation.php?locale=en&q=include#meta:match). |
| `@include` | Older or more flexible URL matching. It may use wildcard or regular-expression forms, but it is easier to make broader than intended. Prefer `@match` for ordinary URL scopes. See [`@include`](https://www.tampermonkey.net/documentation.php?locale=en&q=include#meta:include). |
| `@exclude` | Removes URLs from an `@match` or `@include` scope. Use it for explicit exceptions, but do not use a broad include plus a long exclusion list as a substitute for a precise match. See [`@exclude`](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:exclude). |
| `@noframes` | Prevents execution in frames for the matching page scope. Use it when the top-level document is the only intended target, and verify frame behavior in the target browser and Tampermonkey version. See [`@noframes`](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:noframes). |
| `@run-at` | Earliest injection timing: `document-start`, `document-body`, `document-end`, `document-idle`, or supported special modes. It is not a guarantee that an application has finished rendering. See [`@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at). |
| `@grant` | Whitelists Tampermonkey APIs, `unsafeWindow`, and selected powerful window functions. Declare only what the script calls. See [`@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant). |
| `@require` | Loads an external JavaScript dependency before the script body. Pin the dependency URL or version, review its source, and treat it as trusted code with the same privileges as the script. See [`@require`](https://www.tampermonkey.net/documentation.php?locale=en&q=externals#meta:require). |
| `@resource` | Gives a named external resource to the script. Read it with the corresponding resource API such as `GM_getResourceText` or `GM_getResourceURL`, and declare the API grant when required. See [`@resource`](https://www.tampermonkey.net/documentation.php?locale=en&q=externals#meta:resource). |
| `@connect` | Whitelists domains for `GM_xmlhttpRequest`. List known domains narrowly and account for redirects because both initial and final URLs are checked. See [`@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect). |
| `@updateURL` | URL from which update metadata is checked. It is a deployment decision; use a stable endpoint that serves the expected userscript metadata. See [`@updateURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url#meta:updateURL). |
| `@downloadURL` | URL from which an updated script is downloaded. Keep it aligned with the published script and update URL unless there is a deliberate deployment split. See [`@downloadURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url#meta:downloadURL). |
| `@supportURL` | Help, issue, or contact URL shown to users. It should describe how to report failures and compatibility details. See [`@supportURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url#meta:supportURL). |
| `@sandbox` | Version-specific Tampermonkey feature introduced in `4.18+`. Expresses whether the script needs `raw`, `JavaScript`, or `DOM` access. Verify availability and actual behavior in the installed environment. See [`@sandbox`](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox). |

Other metadata such as `@run-in`, `@tag`, and `@webRequest` is also documented by Tampermonkey, but they are version- or feature-specific and are outside the minimum contract for these chapters. Do not add them without a concrete requirement and a version check.

## Scope and Least Privilege

`@match` controls where Tampermonkey considers the script eligible to run. It is not a substitute for a runtime check when behavior depends on the path, query, page state, or authenticated account. Use code to validate those details after injection.

Prefer:

```text
https://app.example.com/orders/*
```

over:

```text
*://*/*
```

Also prefer `@match` over a broad `@include` where the standard match pattern expresses the target. Avoid matching a whole parent domain when one application host is enough. Use `@exclude` for a small, explicit exception such as a print view.

Minimal grants reduce risk because they make privileged behavior visible, reduce the effects of accidental code, and make review easier. Ordinary browser APIs do not need a Tampermonkey grant. A call to `GM_addStyle` needs `@grant GM_addStyle`; a call to `GM_getValue` needs `@grant GM_getValue`; a call to `unsafeWindow` needs `@grant unsafeWindow`. Declare each API explicitly and remove unused grants.

Do not confuse a missing `@grant` with `@grant none`. Tampermonkey documents an empty grant list and `@grant none` differently. `@grant none` disables the sandbox and makes `GM_*` APIs unavailable except for `GM_info`; it is therefore an intentional page-context choice, not a generic way to request no permissions.

## Complete Example Block

This is a complete, valid example for a script that styles an order page, stores a local preference, and reads one known API domain. The URLs are placeholders. Remove directives and grants that the adapted script does not use.

```js
// ==UserScript==
// @name         Order Page Helper
// @namespace    https://userscripts.example.com/order-page-helper
// @version      1.2.0
// @description  Adds a small, persistent helper to the order page.
// @author       Example Maintainer
// @match        https://app.example.com/orders/*
// @exclude      https://app.example.com/orders/print/*
// @noframes
// @run-at       document-idle
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_xmlhttpRequest
// @require      https://cdn.example.com/order-helper@1.2.0/dist/helper.min.js
// @resource     helper-theme https://cdn.example.com/order-helper@1.2.0/theme.css
// @connect      api.example.com
// @updateURL    https://updates.example.com/order-page-helper.meta.js
// @downloadURL  https://updates.example.com/order-page-helper.user.js
// @supportURL   https://support.example.com/order-page-helper
// @sandbox      DOM
// ==/UserScript==
```

`@sandbox DOM` is version-specific (`4.18+`) and should be retained only if the script's tested behavior matches that access requirement. If the script uses resource text or resource URLs, add `@grant GM_getResourceText` or `@grant GM_getResourceURL` as appropriate. If it uses async namespaced APIs such as `GM.getValue`, declare the namespaced grant required by the installed Tampermonkey version and test it there.

The example intentionally includes several capabilities to show the shape of a full block. A real script should remove `@require`, `@resource`, `@connect`, and unused grants when it does not need them.

## Common Mistakes

- Matching `*://*/*` because the target URL was not analyzed. This runs on unrelated sites.
- Assuming `@match` can distinguish query strings or URL hashes. Check those values in code.
- Using `@include` regular expressions without testing edge cases such as ports, subdomains, or a URL that contains a similar string.
- Adding `@noframes` without checking whether the desired element actually lives in a frame.
- Treating `document-idle` as "the SPA is ready" rather than as an injection timing choice.
- Adding `@grant GM_xmlhttpRequest` without a narrow `@connect` list, or adding `@connect *` without a documented reason.
- Including a floating or unpinned `@require` dependency whose content can change without a script version change.
- Declaring a resource but forgetting the matching `GM_getResourceText` or `GM_getResourceURL` grant.
- Using `@grant none` and then expecting `GM_getValue`, `GM_addStyle`, or other `GM_*` APIs to exist.
- Publishing an update URL that serves a metadata file inconsistent with the downloadable script.
- Adding `@sandbox` without stating the minimum Tampermonkey version and testing browser-specific fallback behavior.

## Verification Checklist

- [ ] The metadata block is at the beginning of the file and uses the exact `// ==UserScript==` and `// ==/UserScript==` markers.
- [ ] Every `@match` is as narrow as the requirement allows.
- [ ] `@exclude` entries are concrete and tested.
- [ ] Frame behavior and `@run-at` are deliberate.
- [ ] Each Tampermonkey API call has its required `@grant`.
- [ ] `@connect` contains only required domains.
- [ ] External code and resources are pinned, reviewed, and documented.
- [ ] Version-specific directives state their minimum version and fallback behavior.
- [ ] Update, download, and support URLs point to the intended deployment.

## Official References

- [Tampermonkey metadata documentation](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey `@match` and `@include`](https://www.tampermonkey.net/documentation.php?locale=en&q=include)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `@sandbox` (`4.18+`)](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey update URLs](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url)
