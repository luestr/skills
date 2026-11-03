# HTML 过滤与响应头过滤

> 在浏览器解析前从响应数据中移除元素，以及移除响应头。

## HTML 过滤器

### 概述

HTML 过滤器作用于**响应数据**（在浏览器解析之前）。它们从流式传输的 HTML 中移除匹配的元素，因此浏览器永远不会看到它们。

**平台：** 仅 Firefox（需要 `cap_html_filtering`）。

### 语法

在 `##` 后的选择器前加 `^`：

```
[主机名]##^[CSS 或过程式选择器]
[主机名]#@#^[选择器]     （例外）
```

### 重要：如何创建 HTML 过滤器

**不要使用浏览器 DevTools 检查器** — 那显示的是解析后的 DOM，不是原始响应数据。

**使用 `view-source:[URL]`** 查看实际的响应数据。在那里找到相关的 HTML 元素，然后根据你在源码中看到的内容创建过滤器。

### 示例

```
example.com##^.ad-container
```
从响应流中移除所有 class 为 `ad-container` 的元素。

```
example.com##^script:has-text(7c9e3a5d51cdacfc)
```
从响应中移除包含特定文本的 `<script>` 标签。

```
example.com##^script:has-text(/ad[-_]?block/i)
```
移除匹配正则模式的脚本。

### 支持的选择器

HTML 过滤支持在预解析上下文中有意义的 CSS 选择器和过程式操作符：
- `:has-text()` — 按文本内容匹配
- `:min-text-length()` — 按最小文本长度匹配
- `:has()` — 按后代元素匹配
- 原生 CSS 选择器

**HTML 过滤中不支持：** 需要活动 DOM 的操作符（如 `:matches-css()`、`:upward()` 等）

### 取反主机名（1.48.5b4+）

```
google.com,~translate.google.com##^script:has-text(consentCookiePayload)
```
在 google.com 上生效，但在 translate.google.com 上不生效。

### 字符编码支持

HTML 过滤仅适用于以下编码：
- UTF-8
- ISO-8859-1
- Windows-1250
- Windows-1251
- Windows-1252

### 与元素隐藏过滤器的关系

HTML 过滤器在解析**前**移除元素。元素隐藏过滤器在解析**后**隐藏元素（通过 CSS）。HTML 过滤更强大，因为浏览器根本不会处理被移除的内容 — 脚本不执行、图片不加载等。

### 历史说明

已弃用的 `script:contains(...)` 语法在内部被转换为 `##^script:has-text(...)`。

## 响应头过滤

### 概述

HTML 过滤的特殊情况，针对响应头而非响应体。

**平台：** 所有浏览器（头移除发生在 `onHeaderReceived` 时）。

### 语法

```
[主机名]##^responseheader(头名称)
```

头名称**必须小写**。

### 示例

```
example.com##^responseheader(refresh)
```
移除 `refresh` 头以防止定时重定向。

```
example.com##^responseheader(set-cookie)
```
移除 `set-cookie` 头。

### 支持的头

出于安全原因，只能移除有限的一组：

- `location`
- `refresh`
- `report-to`
- `set-cookie`

此限制确保 uBO 永远不会降低网页的安全性（例如，不能移除 `content-security-policy`）。

### 范围

响应头过滤只能应用于**文档资源**（主框架和子框架），不能应用于脚本或图片等子资源。

### 相关功能

要根据特定响应头是否存在并匹配值来过滤网络响应，请使用 `$header=` 网络过滤器选项。
