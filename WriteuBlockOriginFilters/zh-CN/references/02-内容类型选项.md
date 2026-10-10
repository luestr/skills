# 内容类型选项

> 将网络过滤器限制到特定内容/资源类型的选项。

## 概述

内容类型选项将过滤器缩小到只匹配特定类型的网络请求。多个类型可用逗号组合。未指定类型时，过滤器匹配所有类型。

## 可用内容类型选项

### `$script` / `$1p-script` / `$3p-script`

匹配 JavaScript 资源请求。

```
||example.com^$script
```
拦截到 example.com 的所有脚本请求。

- `$1p-script` — 仅第一方脚本（uBO 1.20.0+）
- `$3p-script` — 仅第三方脚本（uBO 1.20.0+）

### `$image` / `$1p-image` / `$3p-image`

匹配图片资源请求（jpg、png、gif、webp、svg 等）。

```
||ads.example.com^$image
```

- `$1p-image` — 仅第一方图片
- `$3p-image` — 仅第三方图片

### `$stylesheet` / `$css`

匹配 CSS 样式表资源请求。`$css` 是简写别名。

```
||example.com^$stylesheet
```

### `$font`

匹配 Web 字体资源请求。

```
||fonts.example.com^$font
```

### `$media`

匹配媒体资源请求（音频、视频文件）。

```
||cdn.example.com^$media
```

### `$subdocument` / `$frame`

匹配嵌入文档请求（iframe、frame）。`$frame` 是 uBO 推荐的别名。

```
||ads.example.com^$frame
```

### `$object`

匹配插件加载的资源请求（如 Flash、Java 小程序）。

### `$other`

匹配不属于任何标准内容类型类别的请求。

### `$ping`

匹配由 `Navigator.sendBeacon()` API 或 `<a ping="">` 属性发送的请求。

```
||tracking.example.com^$ping
```

### `$websocket`

匹配 WebSocket 连接（`ws://` 和 `wss://` 协议）。

```
||ws.example.com^$websocket
```

### `$xhr` / `$xmlhttprequest`

匹配由 `XMLHttpRequest` 或 `fetch()` API 发出的请求。`$xhr` 是简写别名。

```
||api.example.com/track^$xhr
```

### `$popup`

匹配页面打开的弹出窗口。既可作为拦截类型，也可作为独立选项。

```
||example.com^$popup
```
拦截从 example.com 打开的弹出窗口。

### `$document` / `$doc`

匹配主文档（顶层页面加载）。这是一个强大的选项 — 在拦截过滤器上使用会导致整个站点被严格拦截。

```
||example.com^$document
```
严格拦截 example.com 的一切。

**`$document` 例外过滤器：**
```
@@||example.com^$document
```
白名单允许 example.com（禁用该站点上的所有过滤）。

**重要：** uBO 不支持将 `$document` 用于"可接受广告"例外。用户必须通过受信站点功能显式信任站点。

### `$top`

仅匹配顶层文档请求（仅主框架，不含子文档/iframe）。uBO 1.20.0+ 新增。

```
||example.com^$top
```

### `$all`

等同于指定所有网络类型 + `$popup` + `$document` + `$inline-font` + `$inline-script`。uBO 1.20.0+ 新增。

```
||bet365.com^$all
```
拦截 bet365.com 的所有网络请求、弹出窗口、内联字体和脚本。

## 组合内容类型

多个类型可用逗号组合：

```
||example.com^$script,image
```
拦截 example.com 的脚本和图片请求。

## 1p/3p 变体

从 uBO 1.20.0 起，许多内容类型有第一方和第三方变体：

| 基础类型 | 第一方 | 第三方 |
|---|---|---|
| `$script` | `$1p-script` | `$3p-script` |
| `$image` | `$1p-image` | `$3p-image` |
| `$stylesheet` | `$1p-css` | `$3p-css` |
| `$font` | `$1p-font` | `$3p-font` |
| `$media` | `$1p-media` | `$3p-media` |
| `$frame` | `$1p-frame` | `$3p-frame` |
| `$xhr` | `$1p-xhr` | `$3p-xhr` |

这些比组合使用如 `$script,$third-party` 更高效，因为 uBO 可以在内部优化。

## 示例

```adblock
||tracker.example.com^$script,xhr
```
拦截 tracker.example.com 的脚本和 XHR 请求

```adblock
||cdn.example.com^$3p-image
```
拦截 cdn.example.com 的第三方图片请求

```adblock
@@||analytics.example.com^$1p-script
```
白名单允许 analytics.example.com 的第一方脚本

```adblock
||popads.net^$popup,important
```
强制拦截 popads.net 的所有弹出窗口
