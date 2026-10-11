---
name: WriteTampermonkeyScripts
description: Guide an AI agent through planning, writing, debugging, testing, and maintaining Tampermonkey userscripts. Use this skill whenever a user asks for a userscript, browser-page automation, DOM enhancement, Tampermonkey metadata, GM_* API, @match, @grant, @run-at, @connect, cross-origin request, SPA page integration, or script injection task, even when Tampermonkey is not named explicitly.
compatibility: Platform-neutral Markdown guidance. Consult the official Tampermonkey documentation for browser, version, permission, and API availability details.
---

# Tampermonkey Userscript Authoring

Use this skill to plan, write, debug, test, and maintain Tampermonkey userscripts. Keep the guidance platform-neutral and adapt the implementation to the user's target browser, page, and constraints.

## Before Writing Code

First identify:

- The target pages, URL patterns, frames, and page contexts where the script must run.
- The user-visible behavior, interaction model, and success criteria.
- The page and script lifecycle, including initial load, navigation, reloads, and teardown.
- The permissions, metadata, grants, injection timing, and sandbox boundaries required.
- The data sources, persistence needs, communication paths, and external services involved.
- Failure modes, recovery behavior, and what should happen when the page or service changes.
- Browser, Tampermonkey version, page-structure, CSP, compatibility, and accessibility constraints.

After using this index, read only the chapters relevant to the task. Before presenting an implementation, verify its scope, grants, timing, dynamic-page behavior, security, and testability against the requirements.

## Relevant Chapters

1. [Workflow](chapters/01-workflow.md)
2. [Metadata](chapters/02-metadata.md)
3. [Runtime Permissions](chapters/03-runtime-permissions.md)
4. [DOM and Styles](chapters/04-dom-and-styles.md)
5. [SPA and Dynamic Pages](chapters/05-spa-and-dynamic-pages.md)
6. [Storage and State](chapters/06-storage-and-state.md)
7. [Network and Cross-Origin](chapters/07-network-and-cross-origin.md)
8. [UI and Utility APIs](chapters/08-ui-and-utility-apis.md)
9. [Context Communication](chapters/09-context-communication.md)
10. [Security and Privacy](chapters/10-security-and-privacy.md)
11. [Debugging and Compatibility](chapters/11-debugging-and-compatibility.md)
12. [Testing, Release, and Examples](chapters/12-testing-release-and-examples.md)

## Official Sources

- [Tampermonkey Documentation](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey FAQ](https://www.tampermonkey.net/faq.php?locale=en)

## Final Checklist

- [ ] Scope and target pages are explicit.
- [ ] Grants and metadata are minimal and justified.
- [ ] Lifecycle and injection timing are correct.
- [ ] Dynamic-page handling is idempotent.
- [ ] Errors have observable and recoverable behavior.
- [ ] Security and privacy risks are addressed.
- [ ] Browser and Tampermonkey compatibility is stated.
- [ ] Tests or a reproducible verification procedure are included.
