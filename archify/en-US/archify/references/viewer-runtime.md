# Viewer Runtime reference

Read this only when the user asks for a reader-facing capability. Ordinary generation does not require implementing or re-documenting these features; they are already in the generated HTML.

## Exploration

- Diagram Guide lists current actions and shortcuts.
- Reading Depth starts at READ at the default 100% scale, reveals FULL detail at 175%, and falls back to MAP only below 100%. Focus, route, and semantic interactions reveal their exact facts at any scale.
- Semantic Lens summarizes selected node/relationship kinds without changing authored geometry.
- Intent Trace previews a fine-pointer or keyboard target before committed focus.
- Node Finder searches labels and stable IDs.
- Semantic Passport opens on focus, shows authored upstream/downstream facts, supports a copyable deep link, has an explicit close action, closes on true outside activation and Escape, and never enters canonical export.
- Semantic Radar mirrors the visible viewport and authored graph without becoming a second source of truth.
- Direct Relationship Pin makes a unique compiled relationship operable while preserving the authored line and stable relationship identity. It must fail closed on conflicting source/target/label/ID metadata.
- Route Probe resolves exactly two endpoints over authored directed relationships. It never infers a route from geometry.

## Motion and presentation

`meta.animation: "trace"` enables a finite reader-controlled Live/Still trace. Static is the default. Still, reduced motion, page hiding, print, and canonical export preserve complete static meaning. Presentation Stage changes viewer chrome and framing, never authored geometry. This is not a mobile product feature; narrow layouts get containment only.

## Canonical exports

The export menu can copy/download full-diagram PNG, download JPEG/WebP, download a dual-theme SVG, and record a trace-enabled WebM. Viewer state—Guide, Lens, finder, focus, route, camera, radar, presentation, motion ownership, and temporary overlays—must be removed from canonical export.

### Route Share Card

After a real directed Route Probe resolves, the reader may use **Export → Route Share Card**. It reuses the exact ordered route snapshot and the shared Share Card seam: `format=share-card`, `variant=route`. The isolated clone may use only static `data-share-route-*` decoration. It is download-only, fails closed for stale/unreachable/conflicting routes, and never becomes the canonical artifact.

### Reach Share Card

After a non-empty authored reachability query, the reader may use **Export → Reach Share Card**. It consumes the already resolved upstream/downstream node and edge set without rerunning traversal: `format=share-card`, `variant=reach`. The isolated clone may use only static `data-share-reach-*` decoration. It is download-only. Call it authored reachability—not impact, blast radius, breakage, or runtime causality.

## Truth boundary

Viewer exports are communication assets. They do not replace the checked HTML, the deterministic delivery receipt, or a real visual review. Do not add a hosted service, storage surface, dependency, schema branch, or mobile product surface for these viewer-only capabilities.

## Chatlo adaptation

This skill is adapted for Chatlo (iOS, built-in WebKit browser). Run the CLI with `bun`: every `node bin/archify.mjs` is `bun bin/archify.mjs`. Use only the Chatlo built-in browser (the `web_browser` tool or the equivalent `chatlo-browser` command); do not install, download, or run Chrome/Chromium/Firefox/Edge/Playwright/Puppeteer or any other third-party browser or engine.

On Chatlo there is no desktop Chrome, and the built-in browser viewport is fixed by the host (phone-sized), so the automated desktop `browser-check` gate cannot run. `finalize` therefore marks the `browser-check` stage `delegated` (its `visualReview` is `delegated-to-chatlo-web_browser`): `validate -> deliver -> check` still all pass. Perform the delegated review with the built-in browser at the device viewport; see `chatlo-browser-evidence.md` for the probe scripts and pass criteria.

Do not use `preview` or `--open`: Chatlo has no OS opener. Open artifacts with the `web_browser` tool via `chatlo:///absolute/path`.

The self-update check is disabled by default (`ARCHIFY_UPDATE_CHECK_DISABLED=1`); do not check for or install updates.
