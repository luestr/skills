# 元素隐藏（内容过滤器）

元素隐藏过滤器针对无法在网络层面拦截的页面内容 — 直接嵌入在 HTML 中、伪装成普通内容的广告。这些过滤器使用 CSS 选择器来识别和隐藏（或操作）DOM 元素。

## 内容过滤器结构

所有内容过滤器遵循以下模式：

```
<域名><分隔符><主体>
```

- **域名** — 逗号分隔的域名列表（泛型过滤器可为空）
- **分隔符** — 决定过滤器类型
- **主体** — CSS 选择器或代码片段

### 分隔符参考

| 分隔符 | 类型 | 主体内容 |
|---|---|---|
| `##` | 元素隐藏 | CSS 选择器 |
| `#?#` | 元素隐藏仿真 | 扩展 CSS 选择器 |
| `#@#` | 元素隐藏例外 | CSS 选择器 |
| `#$#` | 代码片段过滤器 | JavaScript 代码片段 |

## 元素隐藏 (`##`)

`##` 分隔符创建元素隐藏规则。主体是标准 CSS 选择器，用于标识要隐藏的元素。

```
##.textad
```
在**所有**站点上隐藏任何 `class="textad"` 的元素。

```
###sponsorad
```
隐藏 `id="sponsorad"` 的元素。

```
##textad
```
隐藏所有 `<textad>` 元素（按标签名）。

## 域名限制规则

在过滤器前加上域名来限制其生效范围：

```
example.com##.sponsor
```
在 `example.com` 及其子域名（如 `sub.example.com`）上隐藏 `.sponsor` 元素，包括匹配 URL 的 iframe 内部。

**多个域名**（逗号分隔）：
```
domain1.example,domain2.example,domain3.example##.sponsor
```

**排除域名**（波浪号前缀）：
```
~example.com##.sponsor
```
在除 `example.com` 之外的每个站点上隐藏 `.sponsor`。

**组合包含和排除：**
```
example.com,~foo.example.com##.sponsor
```
在 `example.com` 上隐藏 `.sponsor`，但不在 `foo.example.com` 上。

**重要：** 元素隐藏中的域名限制仅适用于完整域名 — 不能使用部分匹配或地址路径。

## 属性选择器

使用 CSS 属性选择器来定位没有 ID 或 class 的元素：

```
##table[width="80%"]
```
隐藏 `width` 属性设置为 `80%` 的表格。

```
##div[title*="adv"]
```
隐藏 `title` 属性*包含* "adv" 的 `<div>` 元素。

```
##div[title^="adv"][title$="ert"]
```
隐藏 `title` **以** "adv" **开头**且**以** "ert" **结尾**的 `<div>` 元素。

**多个属性条件：**
```
##table[width="80%"][bgcolor="white"]
```
匹配同时具有 `width="80%"` 和 `bgcolor="white"` 的表格。

### CSS 属性选择器快速参考

| 选择器 | 含义 |
|---|---|
| `[attr="val"]` | 精确匹配 |
| `[attr*="val"]` | 包含 "val" |
| `[attr^="val"]` | 以 "val" 开头 |
| `[attr$="val"]` | 以 "val" 结尾 |
| `[attr~="val"]` | 包含单词 "val"（空格分隔） |
| `[attr\|="val"]` | 以 "val" 开头（连字符分隔） |

## 高级 CSS 选择器

浏览器支持的任何 CSS 选择器都可以使用：

```
##.adheader + *
```
隐藏紧跟在 class 为 "adheader" 的元素之后的所有内容。

```
##div.sidebar > span
```
隐藏作为 `div.sidebar` 直接子元素的 `<span>` 元素。

常用高级选择器：
- **组合器：** `>`、`+`、`~`、` `（后代）
- **伪类：** `:first-child`、`:nth-child()`、`:not()`、`:has()`（浏览器原生）
- **伪元素：** `::before`、`::after`

**性能警告：** 复杂选择器（尤其是后代和兄弟组合器）比 class/ID 选择器处理速度慢。仅在更简单的选择器无法定位元素时才使用。

**验证：** Adblock Plus 会拒绝语法无效的 CSS 过滤器 — 始终验证你的选择器。

## 元素隐藏仿真 (`#?#`)

当标准 CSS 选择器不够强大时，使用 `#?#` 配合 ABP 的扩展 CSS 选择器（详见扩展选择器模块）：

```
example.com#?#div:-abp-has(.sponsored)
```

**性能提示：** `#?#` 过滤器比 `##` 慢，因为它们需要 ABP 主动评估扩展选择器。尽可能使用 `##` 来表达规则，仅在真正需要扩展选择器时才使用 `#?#`。

## 元素隐藏例外 (`#@#`)

在特定域名上停用元素隐藏规则：

```
##.textad
example.com#@#.textad
```
第一条规则在所有地方隐藏 `.textad`。第二条规则豁免 `example.com`。组合效果等同于 `~example.com##.textad`。

例外规则也适用于扩展 CSS 选择器（`#?#` 规则）。

**何时使用例外 vs 域名限制：**
- 如果你控制原始过滤器 → 使用域名限制（`~example.com##.textad`）
- 如果你在扩展别人的过滤规则列表 → 使用例外（`#@#`）

**内联样式和移除操作：** 如果被豁免的过滤器具有内联 CSS 样式或 `remove: true;`，例外规则只需匹配 CSS 选择器即可 — 样式/移除部分会自动被豁免。

```
##aside.info {remove: true}
example.com#@#aside.info     ← 这也会豁免移除操作
```
