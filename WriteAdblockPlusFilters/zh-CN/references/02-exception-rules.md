# 例外规则

例外规则定义了拦截过滤规则*不应*被应用的情况。它们允许你在不修改现有规则的情况下"打孔" — 在扩展你无法控制的过滤规则列表时至关重要。

## 基础语法

在任何过滤规则模式前加上 `@@` 来创建例外规则：

```
@@advice
```
这会阻止任何匹配 `advice` 的过滤规则拦截请求。所以如果你有规则 `adv` 不小心拦截了 `http://example.com/advice.html`，例外规则 `@@advice` 可以拯救该页面。

例外规则使用与拦截规则相同的匹配语法 — 通配符、锚点 (`|`、`||`)、分隔符 (`^`) 和正则表达式都可以使用。

## 页面级例外 (`$document`)

`$document` 选项在匹配的页面上关闭**所有** Adblock Plus 拦截：

```
@@||example.com^$document
```
当你访问 `example.com` 上的任何页面时，ABP 完全禁用 — 不应用任何类型的过滤规则。这是"白名单整个站点"的逃生出口。

## 元素隐藏例外 (`$elemhide`)

类似于 `$document`，但仅禁用元素隐藏规则 — 网络级别的拦截仍然生效：

```
@@||example.com^$elemhide
```
在 `example.com` 上，所有 `##` 元素隐藏规则被关闭，但网络请求仍可被拦截。

## 泛型例外 (`$generichide`、`$genericblock`)

这些是更有针对性的例外：

```
@@||example.com^$generichide
```
仅在 `example.com` 上禁用*泛型*元素隐藏规则（没有域名限制的规则，如 `##.ad-banner`）。站点特定规则（如 `example.com##.sponsor`）仍然生效。

```
@@||example.com^$genericblock
```
相同概念，但针对*泛型*拦截规则（没有域名限制的网络级别过滤规则）。

## 组合例外选项

可以组合多个例外选项：

```
@@||example.com^$document,elemhide
```
这等同于单独使用 `$document`（因为 `$document` 已隐含 `$elemhide`），但明确写出可以提高可读性。

## 何时使用例外规则

| 场景 | 使用方式 |
|---|---|
| 过滤规则拦截了不该拦截的内容 | `@@<匹配模式>` |
| 白名单整个站点 | `@@\|\|site.com^$document` |
| 在站点上禁用元素隐藏 | `@@\|\|site.com^$elemhide` |
| 在站点上仅禁用泛型规则 | `@@\|\|site.com^$generichide` |
| 扩展你无法修改的过滤规则列表 | 在你自己的列表中添加例外 |

## 例外 vs 域名限制

当你*可以*修改原始过滤规则时，优先使用 `$domain=` 来限制它，而不是添加例外。例外规则是最后的手段 — 当你扩展别人的过滤规则列表且无法更改过于宽泛的规则时使用它们。

```
! 优先这样做（限制过滤规则）：
||example.com/ads/$domain=example.com|example.net

! 而不是这样做（宽泛规则 + 例外）：
||example.com/ads/
@@||example.com/ads/$domain=example.org
```

## 重要提示

- 例外规则适用于*所有*匹配的过滤规则，而不仅仅是某一个特定规则。
- `$document` 例外非常宽泛 — 谨慎使用。
- 元素隐藏的例外规则使用 `#@#` 语法而不是 `@@`（参见元素隐藏模块）。
