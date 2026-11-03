# HTML 过滤规则

> 在浏览器加载页面之前，从 HTML 源码中移除指定元素。

## 兼容性

仅支持：AdGuard for Windows/Mac/Android/Linux + Firefox 扩展。其他浏览器扩展因无法在网络层修改内容而不支持。

CoreLibs v1.18+ / Browser Extension v5.3+ 支持可选的属性值。

## 语法

### CoreLibs + Firefox + Browser Extension v5.2 及之前

```
selector = [tagName] [attributes] [pseudoClasses]
combinator = ">"
      rule = [域名] "$$" selector *(combinator selector)
```

- `tagName` — 小写元素名
- `attributes` — 属性列表：`[name[=value]]`
- `pseudoClasses` — 伪类
- `combinator` — CSS 子组合器 `>`（仅 v5.2 及之前）

### Browser Extension v5.3+

```
rule = [域名] "$$" CSS选择器
```

支持标准 CSS 选择器（不支持伪元素如 `::before`、`::after`）。

## 示例

```adblock
example.org$$script[data-src="banner"]
```
移除 `example.org` 上所有 `data-src` 属性包含 `banner` 的 `<script>` 元素。

```adblock
example.org$$div[some_attribute]
```
移除具有 `some_attribute` 属性的 `<div>`（无论属性值）。

## 特殊属性

### `:contains()` ⭐ 推荐

按内容过滤元素的主要方式。支持纯文本和正则表达式。

```adblock
example.com$$script:contains(Adverts)
example.com$$div:contains("Sponsored by")
example.com$$script:contains(/ad_system_\d+/)
```

**兼容性：** CoreLibs v1.13+、Browser Extension v5.3+。

`:-abp-contains()` 和 `:has-text()` 是同义词。

**限制：** `:contains()` 不能出现在 `>` 组合器左侧（v5.3+ 无此限制）。

---

### `tag-content` ⚠️ 遗留属性

限制选择 innerHTML 包含指定子串的元素。`""` 转义 `"`。

```adblock
$$script[tag-content="banner"]
$$script[tag-content="alert(""this is ad"")"]
```

**限制：** 不能出现在 `>` 组合器左侧（v5.3+ 无此限制）。

---

### `wildcard` ⚠️ 遗留属性

类似 `tag-content`，使用 glob 模式匹配 innerHTML。

```adblock
$$script[wildcard="*banner*text*"]
$$script[wildcard=""banner""]
```

**限制：** 同 `tag-content`。

---

### `max-length`

指定 HTML 元素内容的最大长度。默认值 **8192**。

```adblock
$$div[tag-content="banner"][max-length="400"]
```

---

### `min-length`

指定 HTML 元素内容的最小长度。

```adblock
$$div[tag-content="banner"][min-length="400"]
```

## 例外规则

使用 `$@$` 代替 `$$`：

```adblock
example.com$@$script[tag-content="banner"]
$@$script[tag-content="banner"]      -- 禁用所有域名
```
