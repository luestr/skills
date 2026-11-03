# 修改器过滤器（响应修改）

> 修改响应而非简单拦截或允许的选项。这些选项会转换、剥离或重定向内容。

## `$csp`（内容安全策略）

在匹配的响应中注入 Content Security Policy 头。这不会拦截请求 — 而是添加/修改 CSP 头。

```
||example.com^$csp=script-src 'self' *
```
添加 CSP，仅允许来自同源和指定来源的脚本。

```
||example.com^$csp=frame-src 'none'
```
阻止在 example.com 上的框架嵌入。

**重要：**
- CSP 过滤器无论请求是否被拦截都会应用
- 带 `$important` 的 CSP 过滤器覆盖例外过滤器
- 在例外过滤器上使用 `$csp` 会为该站点移除 CSP 注入

## `$redirect` / `$redirect-rule`

将被拦截的请求重定向到 uBO 资源库中的本地资源，而非完全拦截。

### `$redirect`

```
||tracker.com/analytics.js$3p,redirect=google-analytics_analytics.js
```
当 tracker.com/analytics.js 被拦截时，提供经清理的 Google Analytics 替代品。

### `$redirect-rule`

与 `$redirect` 相同，但仅在过滤器本身会拦截时才激活。它不会自行创建新的拦截过滤器 — 只是为已有的拦截过滤器指定重定向资源。

```
||ads.example.com^$redirect-rule=noop.js
```

**常用重定向资源：**
- `noop.js` — 空 JavaScript
- `noop.css` — 空样式表
- `noop.html` / `noopframe` — 空 HTML 页面
- `1x1.gif`、`2x2.png`、`3x2.png` — 小透明图片
- `none` — 禁用重定向过滤器
- `click2load.html` — iframe 的可交互占位符

**特定 URL 的替代资源：**
- `google-analytics_analytics.js` — GA 替代品
- `google-analytics_ga.js` — ga.js 替代品
- `googletagservices_gpt.js` — GPT 替代品
- `googletagmanager_gtm.js` — GTM 替代品
- `googlesyndication_adsbygoogle.js` — AdSense 替代品
- `amazon_apstag.js` — Amazon APS 替代品
- `nobab.js` — BlockAdblock 绕过器
- `nofab.js` — FuckAdBlock 绕过器

```
||google-analytics.com/analytics.js$redirect=google-analytics_analytics.js
```

## `$removeparam`

从 URL 中剥离查询字符串参数。支持纯文本和正则。

**纯文本：**
```
||example.com^$removeparam=utm_source
```
从查询字符串中移除 `utm_source=xxx`。

**正则：**
```
||example.com^$removeparam=/^utm_/
```
移除所有以 `utm_` 开头的参数。

**通配符移除所有参数：**
```
||example.com^$removeparam=*
```

**重要：** 如果正则参数以 `/` 开头并以 `$/` 结尾，使用 `_` noop 选项避免与普通正则过滤器歧义：
```
/ad-$removeparam=/^foo=bar\d$/,_
```

## `$replace`

使用正则替换网络响应中的文本内容。**仅限受信来源**（uBO 自带列表或用户启用信任的过滤规则）。

```
||example.com^$replace=/bad_ad_code/good_code/
```

**多次替换：**
```
||example.com^$replace=/pattern1/replacement1//pattern2/replacement2/
```

**重要限制：**
- 仅受信来源可用
- 只能应用于文本响应（非二进制）
- 替换在响应体到达浏览器之前执行

## `$uritransform`

对请求 URL 应用基于正则的转换。**仅限受信来源。**

```
||old.example.com^$uritransform=/old/new/
```

与 `$redirect` 不同 — 它在发出请求之前转换 URL 本身，而非提供不同的内容。

## `$urlskip`

通过从 URL 模式中提取真实目标来跳过（绕过）URL 重定向。**仅限受信来源。**

```
||tracker.example.com/redirect?url=$urlskip=url
```

提取 `url` 参数的值并直接导航到该目标，绕过跟踪重定向。

## `$empty`

`$redirect=empty` 的别名。为匹配的请求返回空响应。

```
||tracker.example.com/collect^$empty
```
请求成功但收到空响应体。

**注意：** `$empty` 是便捷别名。为清晰起见推荐使用 `$redirect=noop.js` 或其他特定重定向资源。

## `$mp4`

`$redirect=noopmp4-1s` 的别名。将媒体请求重定向到 1 秒无声 MP4 文件。

```
||cdn.example.com/videos^$mp4
```
常用于服务视频广告的站点 — 广告"播放"但显示空白。

## 过滤示例

```adblock
||example.com^$csp=script-src 'self' 'unsafe-inline'
```
在 example.com 注入 CSP，仅允许自托管的内联脚本

```adblock
||google-analytics.com/analytics.js$redirect=google-analytics_analytics.js
```
将 GA 脚本重定向到经清理的替代品

```adblock
||example.com^$removeparam=/^utm_/
```
从 example.com 的 URL 中剥离所有 UTM 跟踪参数

```adblock
||example.com/page$removeparam=ref
```
从 example.com/page 的 URL 中移除 `ref` 参数

```adblock
||tracking.example.com^$3p,redirect=noop.js
```
在第三方上下文中将跟踪脚本重定向为空 JS

```adblock
@@||cdn.example.com^$removeparam
```
对 cdn.example.com 禁用参数剥离
