# HTML 报告格式

架构评审渲染为操作系统临时目录里的单个自包含 HTML 文件。Tailwind 和 Mermaid 都来自 CDN。Mermaid 可靠地处理图形状的图表；手工搭建的 div 和内联 SVG 处理更偏编辑风格的视觉（体量图、横截面）。两者混用：不要事事依赖 Mermaid，那样会开始显得千篇一律。

## 脚手架

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{{repo name}} 的架构评审</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* 为 Tailwind 覆盖不好的东西准备的一小层自定义样式：
         虚线接缝、手绘感的箭头等。 */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## 页眉

仓库名称、日期，以及一个紧凑的图例：实线方框 = 模块，虚线 = 接缝，红色箭头 = 泄漏，深色粗方框 = 深模块。不要引言段落。直接进入候选方案。

## 候选方案卡片

图表承担主要分量。文字稀疏、平实，使用（来自 `/codebase-design` 技能的）术语表词汇，不加修饰。

每个候选方案是一个 `<article>`：

- **标题**：简短，点出要做的深化（例如“把 Order 接收流水线合拢”）。
- **徽章行**：推荐强度（`Strong` = emerald，`Worth exploring` = amber，`Speculative` = slate），外加一个依赖类别的标签（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **文件**：等宽字体列表，`font-mono text-sm`。
- **前 / 后对比图**：视觉核心。两栏，并排。见下面的模式。
- **问题**：一句话。哪里疼。
- **方案**：一句话。改变什么。
- **收益**：条目列表，每条不超过 6 个词。例如“测试只穿过一个接口”“定价逻辑不再泄漏”“删掉 4 个浅包装器”。
- **ADR 提示框**（如适用）：琥珀色底框里的一行。

不要解释性段落。如果一张图需要一段文字才能看懂，就重画这张图。

## 图表模式

挑选适合候选方案的模式。混着用。不要让每张图长得一样。多样性本身就是要点的一部分。

### Mermaid 图（依赖 / 调用流的主力工具）

当要点是“X 调用 Y，Y 调用 Z，看看这一团乱”时，用 Mermaid 的 `flowchart` 或 `graph`。把它包进 Tailwind 样式的卡片里，免得像是空投进来的。用 classDef 给泄漏边染红色、让深模块变深色。时序图很适合表达“之前：6 次往返；之后：1 次”。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手工搭建的方框与箭头（当 Mermaid 的布局跟你较劲时）

模块用带边框和标签的 `<div>` 表示。箭头用内联 SVG 的 `<line>` 或 `<path>` 元素，绝对定位在一个相对定位的容器之上。当你希望“之后”的图读起来像一个粗边框的深模块、内部灰显时，就用这种方式，因为 Mermaid 渲染不出合适的分量。

### 横截面（适合层层堆叠的浅薄结构）

堆叠水平色带（`h-12 border-l-4`），展示一次调用穿过的各层。之前：6 个薄层，每层什么都没做。之后：1 个厚色带，标注合并后的职责。

### 体量图（适合“接口和实现一样宽”）

每个模块两个矩形：一个表示接口的表面积，一个表示实现。之前：接口矩形几乎和实现矩形一样高（浅）。之后：接口矩形矮，实现矩形高（深）。

### 调用图折叠

之前：函数调用树渲染为嵌套方框。之后：同一棵树折叠进一个方框，如今变成内部调用的那些以淡显方式画在里面。

## 样式指引

- 偏编辑风格，不要企业仪表盘风。留白充足。标题可选衬线体（`font-serif` 与 stone/slate 色系很搭）。
- 配色克制：一个强调色（emerald 或 indigo），加上红色表示泄漏、琥珀色表示警告。
- 图表高度保持在 320px 左右，让前/后两张图并排时无需滚动、看着舒服。
- 图内模块标签用 `text-xs uppercase tracking-wider`，让它们读起来像示意图，而不是 UI。
- 仅有的脚本是 Tailwind CDN 和 Mermaid 的 ESM 导入。除此之外报告是静态的：没有应用代码，除了 Mermaid 自身的渲染之外没有任何交互。

## 首要推荐小节

一张更大的卡片。候选方案名称、一句说明为什么、指向其卡片的锚点链接。就这些。

## 语气

平实的语言，简洁，但架构名词和动词直接来自 `/codebase-design` 技能。简洁不是漂移的借口。

**必须确切使用：**模块、接口、实现、深度、深、浅、接缝、适配器、杠杆、局部性。

**绝不替换为：**组件、服务、单元（代替模块时）· API、签名（代替接口时）· 边界（代替接缝时）· 层、包装器（想指模块却用它们代替时）。

**贴合这种风格的措辞：**

- “Order 接收模块是浅的：接口几乎和实现一样复杂。”
- “定价逻辑越过接缝泄漏。”
- “深化：一个接口，一处测试点。”
- “两个适配器让接缝成立：生产用 HTTP，测试用内存实现。”

**收益条目**要用术语表中的词说出收益：*“局部性：bug 集中到一个模块”*，*“杠杆：一个接口，N 个调用点”*，*“接口收缩；实现吸收包装器”*。不要写*“更易维护”*或*“代码更干净”*，这些说法不在术语表里，不配占位置。

不要含糊其辞，不要清嗓子，不要“值得一提的是……”。一句话能写成条目就写成条目。一个条目能删就删。如果一个术语不在 `/codebase-design` 的术语表里，先去找一个在表里的，再考虑发明新的。
