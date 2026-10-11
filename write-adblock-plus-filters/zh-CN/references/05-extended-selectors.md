# 扩展 CSS 选择器（Adblock Plus 特有）

标准 CSS 选择器有时无法表达识别广告元素所需的模式。Adblock Plus 添加了超越 CSS 的自定义伪选择器 — 它们检查元素内容、文本和计算样式。这些选择器**必须**使用 `#?#` 分隔符语法。

**性能警告：** 扩展选择器由 ABP 的 JavaScript 引擎而非浏览器原生 CSS 引擎评估，因此速度明显更慢。始终优先使用标准 `##` 选择器，仅在确实需要扩展能力时才使用 `#?#`，并尽可能限定在特定域名上。

## `:-abp-has(selector)`

根据元素的**后代内容**来选择元素。类似于浏览器原生的 `:has()` 伪类，但在所有 ABP 支持的浏览器上都能工作。

```
example.com#?#div:-abp-has(> div > a.advertiser)
```
选择包含（作为直接后代）一个包含 class 为 `advertiser` 的 `<a>` 的 `<div>` 的 `<div>` 元素。

内部选择器可以：
- 使用相对定位（`>`、`+`）
- 嵌套其他扩展选择器，包括 `:-abp-has()` 本身
- 使用任何伪选择器

**关键陷阱 — 范围过宽：**
```
! 错误：隐藏整个页面（匹配 <html>，因为 .sponsored 在某处存在）
example.com#?#:-abp-has(.sponsored)

! 正确：用子代/后代组合器缩小范围
example.com#?#:-abp-has(> .sponsored)
```

如果没有 `>` 或 `+` 组合器，`:-abp-has()` 可以一直匹配到 `<html>` 祖先元素，实际上隐藏了整个页面。

## `:-abp-contains(text)`（别名：`:has-text()`）

根据元素的**文本内容**来选择元素。

```
div.sidebar > span:-abp-contains(Advertisement)
```
选择 `div.sidebar` 内包含文本 "Advertisement" 的 `<span>` 元素。

**实用模式** — 与 `:-abp-has()` 组合以选择外部容器：
```
example.com#?#div.sidebar > div:-abp-has(span:-abp-contains(Advertisement))
```
选择*包含*标有 "Advertisement" 的 span 的容器 `div` — 比单独隐藏 span 更稳健。

**范围警告：**
```
! 错误：匹配任何在子树中某处包含 "filters" 的元素
eyeo.com#?#:-abp-contains(filters)

! 较好：缩小到特定标签
eyeo.com#?#div:-abp-contains(filters)

! 最佳：精确目标元素
eyeo.com#?#.article-heading:-abp-contains(filters)
```

## `:-abp-properties(properties)`

根据元素的**计算 CSS 属性**来选择元素（来自样式表，包括 `::before` 和 `::after` 等伪元素）。

```
:-abp-properties(width:300px;height:250px;)
```
选择样式恰好为 `width: 300px` 和 `height: 250px` 的元素。

**属性值中的通配符：**
```
:-abp-properties(width:*px;height:250px;)
```
匹配任何以像素为单位的宽度和 250px 的高度。

**正则表达式**（用 `/` 包裹）：
```
:-abp-properties(/width:30[2-8]px;height:250px;/)
```
匹配宽度在 302px 到 308px 之间、高度为 250px 的元素。

**伪元素匹配：**
```
:-abp-properties(content:'Advertisement')
```
匹配 "Advertisement" 字符串出现在 `::before` 或 `::after` 伪元素内容中的元素。

**重要提示：**
- 属性名称匹配**不区分大小写**。
- 对于 `background-color`，使用 `rgb()` 表示法，而不是十六进制：
  ```
  ! 错误：
  :-abp-properties(background-color: #3D9C4F;)
  ! 正确：
  :-abp-properties(background-color: rgb(61, 156, 79))
  ```
- 旧的方括号语法 `[-abp-properties='...']` 已弃用并自动转换。

## `:not()` 集成

扩展选择器在标准 CSS `:not()` 伪类中可正确工作（ABP 3.13+）：

```
example.com#?#aside:not(:-abp-contains(Legitimate Content))
```
隐藏所有 `<aside>` 元素，**除了**包含 "Legitimate Content" 的那些。

```
example.com#?#div:not(:-abp-has(> .keep))
```
隐藏所有**没有** class 为 `keep` 的直接子元素的 `<div>` 元素。

## `:xpath(expression)`

使用 **XPath 表达式**来选择元素，作为 CSS 选择器的替代方案（ABP 3.13+）。

```
:xpath(//*[contains(text(), 'ad')])
```
选择任何包含文本 "ad" 的元素。

```
example.com#?#:xpath(//div[@class='ad-container']/..)
```
选择任何 `div.ad-container` 的**父元素** — 当你需要隐藏包装器而非广告本身时很有用。

**何时使用 XPath：**
- 选择父/兄弟元素（CSS 无法"向上"遍历 DOM 树）
- 复杂的文本匹配条件
- CSS 无法表达的位置选择

**注意：** XPath 功能强大但冗长 — 当 CSS 选择器配合 `:-abp-has()`/`:-abp-contains()` 可以表达相同逻辑时优先使用它们。

## 最佳实践

1. **始终使用 `#?#` 分隔符** 配合扩展选择器 — `##` 不会生效。
2. **尽可能限定域名** — `example.com#?#` 比裸 `#?#` 更好。
3. **避免宽泛选择器** — 可能匹配到 `<body>` 或 `<html>`。
4. **优先使用 `##` 而非 `#?#`** — 如果标准 CSS 可以表达，就不要使用扩展选择器。
5. **充分测试** — 扩展选择器更容易产生意外的副作用。
