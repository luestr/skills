# 外观规则 (Cosmetic Rules)

> 用于隐藏或修改网页元素。需要基本的 HTML 和 CSS 知识。

## 非基本规则总览

| 类别 | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| 元素隐藏 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CSS 规则 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Extended CSS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| HTML 过滤 | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| JavaScript | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| 脚本片段 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## 元素隐藏规则

隐藏网页元素（等同于 `display: none`）。

**语法：**
```
规则 = [域名] "##" 选择器
```

**域名限制：**
```adblock
example.com##div.textad                        -- 限定域名
example.com,example.org###adblock              -- 多域名
~example.com##.textad                          -- 排除域名
example.org,~subdomain.example.org##.textad    -- 混合使用
```

**例外规则：** 使用 `#@#` 代替 `##`
```adblock
example.com#@#.textad
#@#.textad          -- 禁用所有域名上的此规则
*#@#.textad         -- 同上
```

**Safari 限制：** 不支持同时指定允许和排除域名（如 `example.org,~foo.example.org##.textad`）。

---

## CSS 规则

注入自定义 CSS 样式（比简单隐藏更灵活）。

**语法：**
```
规则 = [域名] "#$#" 选择器 "{" 样式 "}"
```

**示例：**
```adblock
example.com#$#body { background-color: #333!important; }
```

**例外规则：** 使用 `#@$#` 代替 `#$#`
```adblock
example.com#@$#.textad { visibility: hidden; }
```

**限制：** 禁止使用会加载资源的样式（不能用 `<url>` 类型值）。Content Blocker 不支持。

**ABP 兼容：** CoreLibs v1.18+ 支持在元素隐藏规则中使用 `remove: true` 声明：
```adblock
example.org##body { remove: true; }
```

---

## Extended CSS 选择器

扩展 CSS 3.0 能力，支持基于元素自身表示（样式、文本内容等）或与其他元素的关系进行匹配。

**规则标记（推荐使用）：**
- `#?#` — 元素隐藏，`#@?#` — 例外
- `#$?#` — CSS 规则，`#@$?#` — 例外

**应用范围：** 可用于任何外观规则（元素隐藏或 CSS 规则）。

Content Blocker 不支持。

---

### ExtendedCss 通用限制

1. 不支持 CSS 注释和 at-rules
2. 特定伪类有各自限制（见下文）

---

### `:has()` — 关系匹配

选择包含指定子元素的 target 元素。CSS 4.0 规范，多数浏览器已原生支持。

**语法：**
```
[target]:has(selector)
```

- `target` — 可选，标准或扩展 CSS 选择器
- `selector` — 必需，支持选择器列表（当前为"全部匹配"）

**详细示例：**

```adblock
div:has(.banner)                  -- 选择包含 .banner 后代的 div
div:has(> .banner)                -- 选择直接子元素含 .banner 的 div
div:has(+ .banner)                -- 选择紧接在 .banner 之前的 div（相邻兄弟）
div:has(~ .banner)                -- 选择在 .banner 之前的 div（通用兄弟）
div:has(span, .banner)            -- 选择同时包含 span 和 .banner 的 div
```

**兼容性：**
- CoreLibs v1.12+ 原生支持
- Safari 16.4+ / SafariConverterLib v2.0.39+ 原生支持
- Browser Extension v5.3+ 原生支持（MV3 始终使用原生）
- 使用 `#?#` 强制使用 ExtendedCss 实现
- `:has()` 不能嵌套在另一个 `:has()` 中（原生实现）

**别名：** `:-abp-has()`（兼容）。`:if()` 已移除。

---

### `:contains()` — 文本内容匹配

选择包含指定文本或匹配正则的元素。

**语法：**
```
[target]:contains(unquoted text)
[target]:contains(/regexp/)
```

**重要：** `:contains()` 使用 `textContent` 属性匹配，而非 `innerHTML`。这意味着它匹配元素的纯文本内容，不匹配子元素的标签代码。

**示例：**
```adblock
div:contains(banner)               -- 匹配文本含 "banner" 的 div
div:contains(/as .*banner/)        -- 正则匹配
div:contains(/it .*banner/gi)      -- 带标志的正则（忽略大小写）
```

**注意：** `:-abp-contains()` 和 `:has-text()` 是同义词。

---

### `:matches-css()` — CSS 属性匹配

选择具有指定计算 CSS 属性的元素。

**语法：**
```
[target]:matches-css([pseudo-element, ] property: value)
[target]:matches-css-after(property: value)
[target]:matches-css-before(property: value)
```

- `pseudo-element` — 可选，标准伪元素如 `before`、`after`、`first-line` 等
- `property` — 必需，CSS 属性名
- `value` — 必需，支持通配符或正则表达式（始终不区分大小写）

值支持正则表达式：`:matches-css(width: /3[0-9]0px/)`

**转义规则：** 非正则模式中 `(`、`)`、`[`、`]` 必须**取消转义**；正则模式中 `\` 必须**转义**。

**示例：**
```adblock
div:matches-css(before, content: block me)    -- 伪元素匹配
div:matches-css(before, content: block*)      -- 通配符
div:matches-css(before, content: /block me/)  -- 正则
```

**注意：** 正则模式**不支持**标志（flags）。废弃的 `:matches-css-before()` 和 `:matches-css-after()` 仍兼容支持。。

---

### `:matches-attr()` — 属性模式匹配

选择具有匹配指定模式的属性的元素。

**语法：**
```
[target]:matches-attr("name"[="value"])
```

名称和值都支持通配符和正则表达式。

**示例：**
```adblock
div:matches-attr("ad-link")                   -- 匹配含 ad-link 属性的 div
div:matches-attr("data-*"="adBanner")         -- 通配符匹配属性名
div:matches-attr(*unit*=/^click$/)            -- 通配符匹配名 + 正则匹配值
*:matches-attr("/.{5,}delay$/"="/^[0-9]*$/")  -- 正则匹配名和值
```

**转义规则：** 正则模式中 `"` 和 `\` 必须转义，如 `div:matches-attr(class=/[\\w]{5}/)`。正则模式**不支持**标志（flags）。

---

### `:matches-property()` — JS 属性匹配

选择具有匹配 JS 属性的元素。

**语法：**
```
[target]:matches-property("name"[="value"])
```

**示例：**
```adblock
div:matches-property(check.track)
div:matches-property("check./^unit_.{4,8}$/")
div:matches-property("check.unit_*"=true)
div:matches-property(memoizedProps.key="null")
```

**调试技巧：** 在 DevTools 中选中元素，Console 执行 `console.dir($0)` 查看属性。

---

### `:xpath()` — XPath 表达式

通过 XPath 表达式选择元素。

**语法：**
```
[target]:xpath(expression)
```

**限制：**
- 省略 target 时自动限制在 `body` 标签内
- 仅在选择器末尾有效（`:remove()` 除外）

**示例：**
```adblock
: xpath(//*[@class="banner"])
: xpath(//*[@class="inner"]/..)
```

---

### `:nth-ancestor()` — N 级祖先

向上查找第 N 个祖先元素。

**语法：**
```
subject:nth-ancestor(n)
```
N: 1~255

**限制：** 不能在 `:not()` 参数中使用。

---

### `:upward()` — 匹配祖先

向上查找匹配的祖先元素。

**语法：**
```
subject:upward(ancestor)
```
`ancestor` 可以是数字（1~255，等同于 `:nth-ancestor()`）或标准 CSS 选择器。

**限制：** 不能在 `:not()` 参数中使用。

---

### `:remove()` — 移除元素

移除匹配的元素（不仅仅是隐藏）。**只能放在选择器末尾。**

**语法：**
```adblock
selector:remove()
selector { remove: true; }    -- 伪属性，需用 #$?# 标记
```

**示例：**
```adblock
div.banner:remove()
div:has(> div[ad-attr]):remove()
div:contains(advertisement) { remove: true; }
```

使用 `:remove()` 时所有样式属性被忽略（`debug` 除外）。选择任意元素需用 `*`：`.banner > *:remove()`。

---

### `:is()` — 匹配任一

标准 CSS `:is()` 的实现。匹配选择器列表中任一选择器的元素。

**语法：**
```
[target]:is(selectors)
```

**限制：**
- 扩展选择器参数仅支持复合选择器（compound），不支持复杂选择器（complex）
- `#?#:is(...)` 和 `#?#*:is(...)` 解析为 `#?#html *:is(...)`
- 使用 `##` 标记且无其他扩展选择器时，使用原生实现

---

### `:not()` — 否定匹配

标准 CSS `:not()` 的实现。选择不匹配参数选择器的元素。

**语法：**
```
[target]:not(selectors)
```

**限制：**
- `:nth-ancestor()` 和 `:upward()` 不能在 `:not()` 参数中使用
- 使用 `##` 标记且无其他扩展选择器时，使用原生实现

`:if-not()` 已移除。

---

## 外观规则优先级

外观规则的应用方式因平台而异：

| 平台 | 实现方式 | 特点 |
|---|---|---|
| CoreLibs apps | 注入样式表 | 与网站 CSS 优先级相同，**不能覆盖内联样式** |
| Browser Extension | 用户样式表 | 优先级**高于内联样式** |
| Extended CSS 选择器 | JavaScript | 添加内联样式，**可覆盖任何样式** |
