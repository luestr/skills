# Chatlo 浏览器证据（委派复核）

在 Chatlo 上，上游的桌面 Chrome 自动浏览器门控不可用：`finalize` 的 `browser-check` 阶段显示为 `delegated`（委派），`visualReview` 为 `delegated-to-chatlo-web_browser`。本文件给出用 **Chatlo 内置浏览器**（`web_browser` 工具，或等价的 `chatlo-browser` 命令）完成同一套几何/可读性复核的步骤与探针脚本。

## 环境限制（务必先读）

- 内置浏览器是设备上的 WebKit（WKWebView），视口由系统固定为设备尺寸（本机实测 430×932，DPR 3）。**无法**设置 4 个桌面视口，也**无法**只截取视口区域（只能截取整页）。
- 因此本复核是**“设备视口证据”**，与上游的“4 个桌面视口证据”不是同一口径。在回执和给用户的说明中要如实区分，不要声称复现了桌面视口。
- 内置浏览器只能由**顶层命令**驱动：你通过 shell 工具直接运行 `chatlo-browser ...`，或使用 `web_browser` 工具。**被 CLI 派生出的子进程无法调用内置浏览器**，所以浏览器这一步必须由你（代理）执行，不能塞进 `bin/*.mjs` 里自动完成。
- `bun bin/archify.mjs visual-check <html>` 在无 Chrome 时会报告 `skipped`、诊断 `viewer/chrome-unavailable`——这是**预期**行为；真正要拿数据就按本文用内置浏览器复核。

## 探针脚本

### 1) 稳定脚本（同步）

进入页面后先执行一次，冻结动效并切到“阅读”细节层级：

```js
(function () {
  document.documentElement.setAttribute('data-motion', 'still');
  var panel = document.querySelector('.diagram-container');
  if (panel) panel.setAttribute('data-detail-level', 'read');
  return true;
})()
```

### 2) 几何/可读性探针（同步，返回对象）

与上游 Chrome 引擎同口径的测量脚本（选择器与字段一致）：

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

## 用 `chatlo-browser` 命令执行（推荐，可脚本化）

```sh
# 1. 打开并记下返回的 targetId
chatlo-browser open --url "chatlo:///绝对路径/<slug>.html?theme=light"
# 2. 稳定
chatlo-browser act --target-id <targetId> --kind evaluate --fn "<稳定脚本>"
# 3. 读取几何/可读性（返回对象）
chatlo-browser act --target-id <targetId> --kind evaluate --fn "<几何探针>"
# 4. 整页截图
chatlo-browser screenshot --target-id <targetId> --full-page
# 5. 关闭
chatlo-browser close --target-id <targetId>
```

对深色主题把 `?theme=light` 换成 `?theme=dark` 重复第 1–5 步。

> 注意：内置浏览器脚本桥**不支持返回 Promise**（会报“返回结果的类型不受支持”），所以两个探针都必须是**同步**表达式；用 `setTimeout` 之类的等待请用整页加载完成后再执行。

## 用 `web_browser` 工具执行

等价的工具调用序列：`open` → `act`（`kind: "evaluate"`，先稳定脚本、再几何探针）→ `screenshot`（`full_page`）→ 关闭标签。工具与 `chatlo-browser` 底层相同。

## 通过判据（设备视口口径）

- **包含关系 containment**：水平无溢出，即 `scrollWidth <= innerWidth`（`overflowX` 为 false）。窄视口下出现垂直滚动是预期，不算失败。
- **主题 themeStates**：页面 `data-theme`（`resolvedTheme`）等于请求的 `theme`。
- **可读性 readability**：最小投影节点字号为 `null` 或 **≥ 6px**（`MIN_PROJECTED_NODE_TEXT_PX = 6`）。设备视口很窄，为桌面设计的图很可能低于 6px——这属于**预期**，据此决定要不要修复，或改用桌面 Chrome 复核。
- **查看器 chrome**：图例与底部导航不重叠，即 `legendDockIntersectionArea <= 0.5`。

## 记录

- 把每次探针返回的关键字段（`minimumProjectedNodeTextPx`、`legendDockIntersectionArea`、`scrollWidth/innerWidth`、`resolvedTheme`）与截图路径记进你的回复或回执，作为“浏览器证据”。
- 需要持久化时，可写入产物目录下的 `<slug>.device-evidence.json`。
- **只有你确实查看过截图/快照后**，才声明视觉质量；否则只报告自动校验与实际观测到的数值。
