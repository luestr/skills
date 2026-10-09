# 内联 CSS 样式与移除操作

元素隐藏过滤器不仅仅能隐藏元素 — 它们可以应用自定义 CSS 属性或完全从 DOM 中移除元素。这些功能扩展了 `##` 和 `#?#` 语法。

## 内联 CSS 样式

你可以对元素应用特定的 CSS 属性，而不是隐藏它。这在修复隐藏广告后留下的布局问题时很有用。

### 语法

在选择器后附加 CSS 属性块，用空格分隔：

```
<域名>##<选择器> { <属性>: <值>; }
```

### 示例

```
example.com##.banner { margin-bottom: 0 }
```
在 `example.com` 上，对匹配 `.banner` 的元素设置 `margin-bottom: 0`（而不是隐藏它们）。

```
example.com#?#.banner:-abp-has(.ad) { margin-bottom: 0 }
```
相同效果，但使用扩展选择器来找到包含 `.ad` 的 `.banner` 元素。

### 允许的 CSS 属性

出于安全考虑，并非所有 CSS 属性都被允许：

**属性名称：** 必须是有效的 CSS 属性名称。不能以 `--` 开头（自定义属性被阻止）。

**属性值：** 必须匹配以下模式之一：

| 类别 | 允许的值 |
|---|---|
| 全局关键字 | `inherit`、`initial`、`none`、`revert`、`revert-layer`、`unset` |
| 颜色 | 仅十六进制格式：`#000`、`#009900`、`#aabbccdd`（3-8 位十六进制） |
| 颜色关键字 | `currentcolor`、`transparent` |
| 数字 | 任何字面数字，可选带单位：`0`、`10px`、`1.5em`、`100%` |
| 数字正则 | `/^[+-]?(\d+(\.\d+)?|\.\d+)(e[+-]?\d+)?(cm\|mm\|q\|in\|pc\|pt\|px\|em\|ex\|ch\|rem\|lh\|rlh\|vw\|vh\|vmin\|vmax\|vb\|vi\|svw\|svh\|lvw\|lvh\|dvw\|dvh\|%\|fr)?$/` |
| 显示值 | `block`、`inline`、`inline-block`、`flex`、`inline-flex`、`grid`、`inline-grid`、`table`、`inline-table`、`table-row`、`flow-root`、`flow`、`list-item`、`ruby`、`none` |
| 定位值 | `absolute`、`relative`、`fixed`、`static`、`sticky`、`inset` |
| 可见性 | `visible`、`hidden`、`collapse`、`clip` |
| 溢出 | `auto`、`scroll`、`hidden` |
| 边框样式 | `solid`、`dashed`、`dotted`、`double`、`groove`、`ridge`、`inset`、`outset`、`thin` |
| 指针 | `pointer`、`default` |
| 其他 | `all`、`both`、`contain`、`element`、`fit-content`、`left`、`right`、`max-content`、`min-content`、`text`、`true` |

**常见用例：**
```
! 修复被移除广告横幅留下的间隙
example.com##.content-wrapper { margin-top: 0 }

! 为内容腾出空间
news.example.com##.sidebar { width: 0 }

! 修正间距
forum.example.com##.post-separator { border: none }
```

## 移除操作

`remove: true;` 声明将匹配的元素完全从 DOM 中移除，而不仅仅是用 CSS 隐藏。这更彻底 — 被隐藏的元素仍然可以触发脚本或影响布局。

### 语法

```
<域名>##<选择器> { remove: true; }
```

### 示例

```
example.com##.banner { remove: true; }
```
从 `example.com` 的 DOM 中移除所有 `.banner` 元素。

```
example.com#?#.banner:-abp-has(.ad) { remove: true; }
```
使用扩展选择器移除包含 `.ad` 的 `.banner` 元素。

### 关键行为

- **优先于** 任何 CSS 属性 — 如果同时存在 `remove: true;` 和样式属性，元素会被移除。
- 兼容 `##` 和 `#?#` 选择器。
- 被移除的元素完全从 DOM 中消失 — 无法在开发者工具中检查，也无法触发 MutationObserver。

### 移除和内联样式的例外规则

例外规则 (`#@#`) 只需匹配 CSS 选择器 — 无需重复样式/移除块：

```
##aside.info { remove: true }
example.com#@#aside.info    ← 这会豁免移除操作
```

这使例外更简洁 — 仅匹配选择器就足以停用整个过滤器（包括其样式或移除操作）。

## 何时使用哪种方式

| 目标 | 方法 |
|---|---|
| 隐藏元素（仍在 DOM 中，占空间） | `##selector` |
| 隐藏并折叠（不占空间） | `##selector { display: none }` 或直接 `##selector` |
| 修复隐藏广告后的布局 | `##selector { margin-top: 0 }` |
| 完全从 DOM 中移除 | `##selector { remove: true; }` |
| 移除匹配复杂条件的元素 | `#?#selector { remove: true; }` |

## 安全说明

- 内联样式限制为安全的 CSS 属性 — 不允许 `url()`、`expression()`、自定义属性。
- 属性值针对允许列表进行验证（参见上面的允许 CSS 属性）。
- `remove: true;` 在页面生命周期内不可逆 — 元素在页面重新加载前都会消失。
