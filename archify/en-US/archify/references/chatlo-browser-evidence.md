# Chatlo browser evidence (delegated review)

On Chatlo the upstream desktop-Chrome automated browser gate is unavailable: `finalize` marks the `browser-check` stage `delegated`, and `visualReview` is `delegated-to-chatlo-web_browser`. This file gives the steps and probe scripts to perform the same geometry/readability review with the **Chatlo built-in browser** (the `web_browser` tool, or the equivalent `chatlo-browser` command).

## Environment limits (read first)

- The built-in browser is WebKit (WKWebView) on the device; the viewport is fixed by the host to the device size (measured 430×932, DPR 3). You **cannot** set the four desktop viewports, and you **cannot** capture only the viewport region (only full-page).
- So this review is **device-viewport evidence**, not the same basis as upstream's four desktop viewports. Say so honestly in receipts and to the user; do not claim to have reproduced the desktop viewports.
- The built-in browser can only be driven by **top-level commands**: you run `chatlo-browser ...` directly through the shell tool, or use the `web_browser` tool. A subprocess spawned by the CLI cannot call the built-in browser, so this browser step must be performed by you (the agent), not automated inside `bin/*.mjs`.
- `bun bin/archify.mjs visual-check <html>` reports `skipped` with diagnostic `viewer/chrome-unavailable` when no Chrome is present — this is **expected**; to get data, use the built-in browser per this file.

## Probe scripts

### 1) Stability script (synchronous)

Run once after the page loads to freeze motion and switch to the "read" detail level:

```js
(function () {
  document.documentElement.setAttribute('data-motion', 'still');
  var panel = document.querySelector('.diagram-container');
  if (panel) panel.setAttribute('data-detail-level', 'read');
  return true;
})()
```

### 2) Geometry/readability probe (synchronous, returns an object)

The same measurements as the upstream Chrome engine (same selectors and fields):

```js
(function () {
  var reader = document.querySelector('.container');
  var diagram = document.querySelector('.diagram-container');
  var svg = diagram && (diagram.querySelector(':scope > svg') || diagram.querySelector(':scope > .diagram-stage > svg'));
  var stage = diagram && (diagram.querySelector(':scope > .diagram-stage') || svg);
  var legend = svg && svg.querySelector('[data-legend]');
  var navigationDock = diagram && diagram.querySelector('.diagram-nav');
  var viewBox = svg && svg.viewBox && svg.viewBox.baseVal;
  var diagramWidth = svg ? svg.getBoundingClientRect().width : 0;
  var viewBoxWidth = viewBox ? viewBox.width : 0;
  var scale = viewBoxWidth > 0 ? Math.min(1, diagramWidth / viewBoxWidth) : 0;
  var minimum = null, minimumNonEdge = null, minimumEdge = null;
  if (svg && scale > 0) {
    Array.from(svg.querySelectorAll('text[data-node-label], text[data-boundary-label], text[data-detail="context"], g[data-detail="context"] text')).forEach(function (text) {
      if (text.getAttribute('data-detail') === 'fine' || text.closest('[data-detail="fine"]')) return;
      var edge = text.closest('[data-edge-from][data-edge-to]');
      var node = text.closest('[data-node-id]');
      var context = text.getAttribute('data-detail') === 'context' || Boolean(text.closest('g[data-detail="context"]'));
      var detail = text.hasAttribute('data-node-label') ? 'primary' : text.hasAttribute('data-boundary-label') ? 'boundary' : context && edge ? 'edge' : 'context';
      if (detail === 'context' && !node) return;
      var sourceFontPx = parseFloat(text.getAttribute('font-size') || '');
      if (!Number.isFinite(sourceFontPx)) return;
      var projectedFontPx = sourceFontPx * scale;
      var entry = { text: (text.textContent || '').trim(), detail: detail,
        owner: edge ? { kind: 'edge', id: edge.getAttribute('data-edge-id'), from: edge.getAttribute('data-edge-from'), to: edge.getAttribute('data-edge-to') } : node ? { kind: 'node', id: node.getAttribute('data-node-id') } : detail === 'boundary' ? { kind: 'boundary', id: null } : null,
        sourceFontPx: sourceFontPx, projectedFontPx: projectedFontPx };
      if (!minimum || projectedFontPx < minimum.projectedFontPx) minimum = entry;
      if (detail === 'edge') { if (!minimumEdge || projectedFontPx < minimumEdge.projectedFontPx) minimumEdge = entry; }
      else if (!minimumNonEdge || projectedFontPx < minimumNonEdge.projectedFontPx) minimumNonEdge = entry;
    });
  }
  function intersectionArea(a, b) {
    if (!a || !b || !a.width || !a.height || !b.width || !b.height) return 0;
    var w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
    var h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
    return w * h;
  }
  var legendRect = legend ? legend.getBoundingClientRect() : null;
  var stageRect = window.Archify && Archify.viewerChromeLayout && typeof Archify.viewerChromeLayout.stageRect === 'function' ? Archify.viewerChromeLayout.stageRect() : (stage ? stage.getBoundingClientRect() : null);
  var navigationDockRect = !navigationDock ? null : window.Archify && Archify.viewerChromeLayout && typeof Archify.viewerChromeLayout.dockRect === 'function' ? Archify.viewerChromeLayout.dockRect() : navigationDock.getBoundingClientRect();
  var stageDockIntersectionArea = intersectionArea(stageRect, navigationDockRect);
  var viewerChromeReceipt = window.Archify && Archify.viewerChromeLayout && typeof Archify.viewerChromeLayout.receipt === 'function' ? Archify.viewerChromeLayout.receipt() : null;
  var svgRect = svg && svg.getBoundingClientRect();
  var diagramRect = diagram && diagram.getBoundingClientRect();
  var documentScrollUnclipped = Boolean(svgRect && diagramRect
    && svgRect.top >= diagramRect.top - 1 && svgRect.left >= diagramRect.left - 1
    && svgRect.bottom <= diagramRect.bottom + 1 && svgRect.right <= diagramRect.right + 1
    && diagram.scrollHeight <= diagram.clientHeight + 1 && diagram.scrollWidth <= diagram.clientWidth + 1
    && [document.documentElement, document.body].every(function (e) { return !['hidden', 'clip'].includes(window.getComputedStyle(e).overflowY); }));
  return {
    innerWidth: window.innerWidth, innerHeight: window.innerHeight, devicePixelRatio: window.devicePixelRatio || 1,
    scrollWidth: Math.ceil(document.documentElement.scrollWidth), scrollHeight: Math.ceil(document.documentElement.scrollHeight),
    resolvedTheme: document.documentElement.getAttribute('data-theme') || '',
    readerLayout: document.documentElement.getAttribute('data-reader-layout') || null,
    readerFit: svg ? svg.getAttribute('data-reader-fit') : null,
    diagramType: svg ? svg.getAttribute('data-diagram-type') : null,
    documentScrollUnclipped: documentScrollUnclipped,
    diagramWidth: diagramWidth, viewBoxWidth: viewBoxWidth,
    minimumProjectedNodeTextPx: minimum ? minimum.projectedFontPx : null,
    minimumProjectedNonEdgeTextPx: minimumNonEdge ? minimumNonEdge.projectedFontPx : null,
    minimumProjectedEdgeTextPx: minimumEdge ? minimumEdge.projectedFontPx : null,
    minimumProjectedNodeText: minimum ? minimum.text : null,
    hasLegend: Boolean(legendRect && legendRect.width && legendRect.height),
    hasNavigationDock: Boolean(navigationDockRect && navigationDockRect.width && navigationDockRect.height),
    legendDockIntersectionArea: stageDockIntersectionArea > 0 ? intersectionArea(legendRect, navigationDockRect) : 0,
    dockStageIntersectionArea: stageDockIntersectionArea,
    dockStageGap: stageRect && navigationDockRect ? navigationDockRect.top - stageRect.bottom : null,
    viewerChromeRequiredGap: viewerChromeReceipt ? viewerChromeReceipt.gap : null,
    viewerChromeActive: viewerChromeReceipt ? viewerChromeReceipt.active : false
  };
})()
```

## Run with `chatlo-browser` commands (recommended, scriptable)

```sh
# 1. Open and record the returned targetId
chatlo-browser open --url "chatlo:///absolute/path/<slug>.html?theme=light"
# 2. Stabilize
chatlo-browser act --target-id <targetId> --kind evaluate --fn "<stability script>"
# 3. Read geometry/readability (returns an object)
chatlo-browser act --target-id <targetId> --kind evaluate --fn "<geometry probe>"
# 4. Full-page screenshot
chatlo-browser screenshot --target-id <targetId> --full-page
# 5. Close
chatlo-browser close --target-id <targetId>
```

Repeat steps 1–5 with `?theme=dark` for dark mode.

> Note: the built-in browser script bridge **cannot return a Promise** (it errors with "unsupported result type"), so both probes must be **synchronous** expressions; instead of `setTimeout`, wait for full page load before evaluating.

## Run with the `web_browser` tool

Equivalent tool sequence: `open` → `act` (`kind: "evaluate"`, stability script then geometry probe) → `screenshot` (`full_page`) → close the tab. Same underlying engine as `chatlo-browser`.

## Pass criteria (device-viewport basis)

- **Containment**: no horizontal overflow, i.e. `scrollWidth <= innerWidth` (`overflowX` false). Vertical scrolling on a narrow viewport is expected and is not a failure.
- **Theme states**: the page `data-theme` (`resolvedTheme`) equals the requested `theme`.
- **Readability**: minimum projected node text is `null` or **≥ 6px** (`MIN_PROJECTED_NODE_TEXT_PX = 6`). The device viewport is narrow, so a diagram designed for desktop may fall below 6px — that is **expected**; use it to decide whether to repair or to fall back to desktop Chrome.
- **Viewer chrome**: legend and bottom navigation do not overlap, i.e. `legendDockIntersectionArea <= 0.5`.

## Recording

- Record the key fields from each probe (`minimumProjectedNodeTextPx`, `legendDockIntersectionArea`, `scrollWidth`/`innerWidth`, `resolvedTheme`) and the screenshot paths in your reply or receipt as the "browser evidence".
- To persist, write `<slug>.device-evidence.json` in the artifact directory.
- Claim visual quality **only after** you have actually inspected a screenshot/snapshot; otherwise report the automated checks and the observed numbers only.
