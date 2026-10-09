# 行为修饰符

> 控制网络过滤器行为的选项 — 来源方限制、域名定向、优先级和特殊行为。

## 来源方限制选项

### `$third-party` / `$3p`

仅匹配来自与当前访问站点不同域的请求。

```
||tracker.com^$third-party
```
拦截从**其他站点**发出的对 tracker.com 的请求。直接访问 tracker.com 时不会拦截。

### `$first-party` / `$1p`

仅匹配来自相同域名（或相关域名）的请求。等同于 `~third-party`。

```
||example.com/track^$first-party
```
拦截 example.com 在自己页面上发出的跟踪请求。

### `$strict1p`

uBO 1.20.0+ 新增。类似 `$first-party` 但更严格：请求的来源必须与文档来源精确匹配（无域名放宽）。

```
||example.com^$strict1p
```

### `$strict3p`

uBO 1.20.0+ 新增。类似 `$third-party` 但更严格：仅当请求来源与文档来源严格不同时匹配。

```
||tracker.com^$strict3p
```

## 域名定向选项

### `$domain=` / `$from=`

限制过滤器仅在页面发起请求的域名匹配指定域名时生效。`$from` 是现代别名。

```
||tracker.com^$3p,domain=example.com|example.org
```
仅在从 example.com 或 example.org 发出的第三方 tracker.com 请求时拦截。

**取反：** 域名前加 `~` 排除：
```
||ads.com^$domain=example.com|~sub.example.com
```
在 example.com 上生效，但在 sub.example.com 上不生效。

**实体匹配：** `google.*` 匹配所有 Google 顶级域名：
```
||ads.com^$domain=google.*
```

**正则域名**（1.46.1b15+）：
```
@@*$ghide,domain=/img[a-z]{3,4}\.buzz/
```

### `$to=`

uBO 1.20.0+ 新增。限制过滤器仅在请求 URL 的目标域名匹配时生效。用于缩小过滤器作用的目标范围。

```
*$frame,from=plainlight.com,to=~/youtube/
```
在 plainlight.com 上拦截指向 YouTube 以外域名的框架。

**实体和正则支持：** 与 `$domain` 相同。

### `$denyallow`

uBO 1.26.0+ 新增。将默认拒绝/例外允许能力引入静态网络过滤。要求同时存在 `$domain=`。

```
*$3p,script,denyallow=x.com|y.com,domain=a.com|b.com
```
在 a.com 或 b.com 上时，拦截所有第三方脚本，**除了**来自 x.com 和 y.com 的。

这比使用广泛拦截 + 例外过滤器的方式更简洁。`$denyallow` 不支持实体通配符匹配。

## 优先级选项

### `$important`

强制拦截过滤器覆盖所有例外过滤器，不论特异性。

```
||ads.example.com^$important
```
此拦截规则优先于任何相同 URL 的 `@@` 例外规则。

**关键行为：** `$important` 拦截过滤器始终胜过例外过滤器。没有 `$important` 时，更特异的过滤器优先。

### `$badfilter`

用于禁用来自其他过滤列表的已有过滤器。`badfilter` 过滤器必须与目标过滤器的模式和选项完全匹配。

```
*$image,badfilter
```
禁用 `*$image` 过滤器（不论它定义在哪里）。

**1.19.0 之后：** 形式为 `|https://` 或 `|http://` 且带有 `domain=` 选项的过滤器会被分解为每域名一个过滤器，允许只 `badfilter` 一个域名：
```
|https://$domain=a.com,badfilter
```

## 显示/行为选项

### `$elemhide` / `$ehide`

在匹配页面上禁用所有元素隐藏过滤器。

```
@@||example.com^$elemhide
```
在 example.com 上禁用元素隐藏。

### `$generichide` / `$ghide`

仅禁用通用元素隐藏过滤器（无主机名前缀的）。站点特定的元素隐藏过滤器仍然生效。

```
@@||example.com^$generichide
```

### `$specifichide` / `$shide`

仅禁用站点特定的元素隐藏过滤器。通用元素隐藏过滤器仍然生效。

```
@@||example.com^$specifichide
```

### `$popunder`

匹配弹底窗口（在当前窗口后打开的弹出窗口）。

```
||example.com^$popunder
```

### `$inline-script`

阻止页面上内联脚本的执行。拦截包含内联代码的 `<script>` 标签（不拦截外部脚本）。

```
||example.com^$inline-script
```

### `$inline-font`

阻止内联字体加载（在 `<style>` 标签或 `style` 属性中定义的字体）。

```
||example.com^$inline-font
```

## 请求匹配选项

### `$match-case`

使过滤器模式区分大小写。默认情况下模式不区分大小写。

```
||Example.COM^$match-case
```
仅匹配 `Example.COM`，不匹配 `example.com` 或 `EXAMPLE.COM`。

### `$method=`

按 HTTP 方法（GET、POST、PUT、DELETE 等）匹配请求。

```
||example.com/api^$method=post
```
仅匹配到 API 的 POST 请求。

### `$header=`

根据响应头的存在（或特定值）匹配请求。

```
||example.com^$header=content-type:application/json
```
匹配响应具有指定头值时。

### `$permissions`

在响应上设置 Permissions-Policy 头。仅受信来源可用。

```
||example.com^$permissions=autoplay=()
```

### `$ipaddress`

为匹配的 DNS 请求返回特定 IP 地址。

```
||tracker.example.com^$ipaddress=0.0.0.0
```

### `$cname`

框架兼容性：仅 Firefox MV2（1.26.0+）。

在例外过滤器中使用时，绕过 CNAME 解封请求的拦截。

```
@@*$cname
```
接受因 CNAME 解封而被拦截的网络请求。

过滤列表作者应谨慎使用此选项，且尽可能缩小范围。

## 示例

```adblock
||tracker.com^$3p,domain=example.com|example.org,image
```
在 example.com 和 example.org 上拦截第三方图片跟踪请求

```adblock
*$script,denyallow=cdn.trusted.com|apis.safe.com,domain=news.example.com
```
在 news.example.com 上拦截所有脚本，除 cdn.trusted.com 和 apis.safe.com 之外

```adblock
@@||example.com^$elemhide
```
在 example.com 上禁用所有元素隐藏

```adblock
||ads.example.com^$important,domain=~trusted.example.com
```
在所有站点强制拦截 ads.example.com，trusted.example.com 除外

```adblock
||cdn.example.com^$image,badfilter
```
禁用一条过于宽泛的图片拦截规则
