# 高级修饰符

> 这些修饰符能完全改变基本规则的行为，用于响应修改、重定向、cookie 控制等高级功能。

## 兼容性总览

| 修饰符 | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$all` | ✅ | ✅ | ✅*[1]* | ✅ | ✅ | ✅ | ❌ |
| `$badfilter` | ✅ | ✅ | ✅*[2]* | ✅ | ✅ | ✅ | ❌ |
| `$cookie` | ✅ | ✅ | ✅*[3]* | ✅ | ❌ | ❌ | ❌ |
| `$csp` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$hls` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$inline-font` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$inline-script` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$jsonprune` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$xmlprune` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$network` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$permissions` | ✅*[4]* | ✅ | ✅ | ✅*[4]* | ❌ | ❌ | ❌ |
| `$redirect` | ✅ | ✅ | ✅*[5]* | ✅ | ❌ | ❌ | ❌ |
| `$redirect-rule` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `$referrerpolicy` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$removeheader` | ✅ | ✅*[7]* | ✅*[7]* | ✅*[7]* | ❌ | ❌ | ❌ |
| `$removeparam` | ✅ | ✅ | ✅*[6]* | ✅ | ❌ | ❌ | ❌ |
| `$replace` | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `$urltransform` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$reason` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `noop` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$empty` 👎 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$mp4` 👎 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## `$all` — 匹配所有内容类型

等同于所有内容类型修饰符 + `$popup`。不能与 `@@` 一起使用。

```adblock
||example.org^$all
```
等价于：`||example.org^$document,subdocument,font,image,media,object,other,ping,script,stylesheet,websocket,xmlhttprequest,popup`

**限制：** 因包含 `$popup`，MV3 不支持。Content Blocker 不支持。

---

## `$badfilter` — 禁用其他规则

禁用其引用的基本规则。被禁用规则的文本必须与 `$badfilter` 规则匹配（不含 `$badfilter`）。

```adblock
||example.com$badfilter                    -- 禁用 ||example.com
||example.com$image,badfilter              -- 禁用 ||example.com$image
@@||example.com$badfilter                  -- 禁用 @@||example.com
||example.com$domain=domain.com,badfilter  -- 禁用 ||example.com$domain=domain.com
```

**域名部分禁用：** 当规则有 `$domain` 修饰符且无否定域名时，`$badfilter` 可仅禁用部分域名：
```adblock
/some$domain=example.com|example.org|example.io
/some$domain=example.com,badfilter  -- 仅对 example.com 禁用
```

**限制：** MV3 中仅支持完全取消规则。Content Blocker 不支持。

---

## `$cookie` — 控制 Cookie

不拦截请求，而是抑制或修改 `Cookie` 和 `Set-Cookie` 头。

**语法：**
```
$cookie [= 名称[; maxAge = 秒数[; sameSite = 策略]]]
```

**示例：**
```adblock
||example.org^$cookie                              -- 阻止所有 cookie
$cookie=__cfduid                                   -- 阻止 CloudFlare cookie
$cookie=/__utm[a-z]/                               -- 阻止 GA cookies
||facebook.com^$third-party,cookie=c_user          -- 阻止 Facebook 跟踪
||example.org^$cookie=NAME;maxAge=3600;sameSite=lax -- 修改 cookie 属性
```

**例外：**
```adblock
@@||example.org^$cookie                -- 放行所有 cookie
@@||example.org^$cookie=concept        -- 放行特定 cookie
@@||example.org^$cookie=/^_ga_/        -- 放行匹配正则的 cookie
```

**兼容修饰符：** `$domain`、`$~domain`、`$important`、`$third-party`、`$~third-party`、`$strict-third-party`、`$strict-first-party`。**受信过滤器规则。** Content Blocker/iOS/Safari 不支持。

---

## `$csp` — 内容安全策略

不拦截请求，而是修改响应头加强 CSP。

**语法：** 值与 CSP 头语法相同。异常规则值可为空。

```adblock
||example.org^$csp=frame-src 'none'
||example.org^$csp=script-src 'self' 'unsafe-eval' http: https:
@@||example.org/page/*$csp=frame-src 'none'
@@||example.org/page/*$csp                           -- 禁用所有 $csp 规则
```

**兼容修饰符：** `$domain`、`$important`、`$subdocument`。Content Blocker/iOS/Safari 不支持。

---

## `$hls` — HLS 播放列表过滤

修改 HLS 播放列表 (RFC 8216) 响应，移除匹配的片段。**受信过滤器规则。**

**语法：**
```adblock
||example.org^$hls=urlpattern        -- URL 模式匹配
||example.org^$hls=/regexp/options    -- 正则匹配 (t=标签匹配, i=忽略大小写)
```

```adblock
||example.org^$hls=\/videoplayback^?*&source=dclk_video_ads
||example.org^$hls=/#UPLYNK-SEGMENT:.*\,ad/t
```

**限制：** 受信过滤器规则。兼容 `$domain`、`$third-party`、`$strict-third-party`、`$strict-first-party`、`$app`、`$important`、`$match-case`、`$xmlhttprequest`。仅适用于 UTF-8 编码以 `#EXTM3U` 开头的 HLS 播放列表，最大 10MB。仅 CoreLibs apps。

---

## `$inline-script` — 阻止内联脚本

使用 CSP 阻止页面中的内联 JavaScript。

```adblock
||example.org^$inline-script
```
等价于：`||example.org^$csp=script-src 'self' 'unsafe-eval' http: https: data: blob: mediastream: filesystem:`

---

## `$inline-font` — 阻止内联字体

使用 CSP 阻止页面中的内联字体。

```adblock
||example.org^$inline-font
```

---

## `$jsonprune` — JSON 响应修改

通过修改的 JSONPath 表达式移除 JSON 响应中的项目。**受信过滤器规则。** 仅 CoreLibs apps。

**语法：**
```adblock
||example.org^$jsonprune=expression
```

`$` 和 `,` 需用 `\` 转义。支持 JSONP 文档（CoreLibs v1.11+）。

**修改的 JSONPath 语法差异：**
- 不支持脚本表达式
- 支持的过滤器：`?(has <key>)`、`?(key-eq <key> <value>)`、`?(key-substr <key> <value>)`

**示例：**
```adblock
||example.org^$jsonprune=\$..[one\, "two three"]
||example.org^$jsonprune=\$.a[?(has ad_origin)]
||example.org^$jsonprune=\$.*.*[?(key-eq 'Some key' 'Some value')]
```

---

## `$xmlprune` — XML 响应修改

通过 XPath 1.0 表达式移除 XML 响应中的项目。**受信过滤器规则。** 仅 CoreLibs apps (v1.15+)。

```adblock
||example.org^$xmlprune=/bookstore/book[position() mod 2 = 1]
||example.org^$xmlprune=/bookstore/book[year = 2003]
||example.org^$xmlprune=//*/@*
```

---

## `$network` — 网络层防火墙

完全阻止或放行指定的远程 IP 地址。**仅匹配 IP 地址，不匹配域名。** 仅 CoreLibs apps。

```adblock
174.129.166.49:3478^$network
[2001:4860:4860::8888]:443^$network
174.129.166.49$network
@@174.129.166.49$network              -- 绕过，不进行任何过滤
/.+:3[0-9]{4}/$network                -- 阻止端口 30000-39999
```

**兼容修饰符：** 仅 `$app` 和 `$important`。

---

## `$permissions` — 权限策略

不拦截请求，而是修改响应头添加 Permissions-Policy。

```adblock
||example.org^$permissions=autoplay=()
$domain=example.org|example.com,permissions=storage-access=()\, camera=()
@@||example.org/page/*$permissions=autoplay=()
@@||example.org/page/*$permissions
```

**注意：** 多个匹配规则各添加独立的 Permissions-Policy 头。`|` 可替代转义逗号（CoreLibs v1.14+）。Firefox 忽略 Permissions-Policy 头。

**兼容修饰符：** `$domain`、`$important`、`$subdocument`、内容类型修饰符。

---

## `$redirect` — 重定向到本地资源

将请求重定向到本地"资源"。

```adblock
||example.org/script.js$script,redirect=noopjs
||example.org/test.mp4$media,redirect=noopmp4-1s
@@||example.org^$redirect
@@||example.org^$redirect=nooptext
```

**优先级：** `$important` > `@@` > `$redirect` > 基本规则

**限制：** MV3 中不支持带 `$redirect` 的白名单规则。不支持指定优先级（uBO 的 `:42` 语法）。Content Blocker/iOS/Safari 不支持。

---

## `$redirect-rule` — 条件重定向

`$redirect` 的别名，但**仅在目标请求被其他基本规则拦截时**才生效。

```adblock
||example.org/script.js
||example.org^$redirect-rule=noopjs
```
仅 `script.js` 被重定向，其他 `example.org` 请求不受影响。

Content Blocker/iOS/Safari/MV3 不支持。

---

## `$referrerpolicy` — 覆盖 Referrer 策略

覆盖页面的 referrer 策略。也替换 HTML 中 `<meta name="referrer">` 的 content 属性。

```adblock
||example.com^$referrerpolicy=unsafe-url
@@||example.com^$referrerpolicy=unsafe-url
@@||example.com/abcd.html^$referrerpolicy
```

无内容类型修饰符时，匹配 `$document` 和 `$subdocument`。CoreLibs v1.12+。

---

## `$removeheader` — 移除 HTTP 头

移除 HTTP 请求或响应头。**受信过滤器规则。**

```adblock
||example.org^$removeheader=refresh              -- 移除响应头
||example.org^$removeheader=request:x-client-data -- 移除请求头
@@||example.org/path/$removeheader
```

**安全限制：** 不能移除安全相关头（如 `access-control-*`、`origin`、`content-security-policy`、`content-type` 等完整列表见文档）。

**兼容修饰符：** `$domain`、`$third-party`、`$strict-third-party`、`$strict-first-party`、`$app`、`$important`、`$match-case`、内容类型修饰符。

---

## `$removeparam` — 移除查询参数

从请求 URL 中剥离查询参数。仅适用于 `GET`、`HEAD`、`OPTIONS` 及部分 `POST` 请求。**受信过滤器规则。**

**别名：** `$queryprune`（已废弃）

**语法：**
```adblock
$removeparam=param                           -- 移除指定参数
$removeparam=/regexp/[i]                     -- 正则匹配移除
$removeparam=~param                          -- 移除除 param 外的所有参数
$removeparam                                 -- 移除所有参数
```

**示例：**
```adblock
$removeparam=/^(utm_source|utm_medium|utm_term)=/
$removeparam=/^(utm_content|utm_campaign|utm_referrer)=/
@@||example.com^$removeparam
```

**MV3 限制：** 不支持正则表达式、否定和白名单规则。每个命名参数生成独立的声明式规则，通过重定向链逐个移除（Chrome 允许每导航最多 20 跳）。

---

## `$replace` — 正则替换响应内容

不拦截请求，而是修改响应文本。需要正则表达式知识。**受信过滤器规则。** 仅 CoreLibs apps + Firefox 扩展。

**语法：**
```
$replace = "/" regexp "/" replacement "/" modifiers
```

`$` 和 `,` 需用 `\` 转义。

```adblock
||example.org^$replace=/(<VAST[\s\S]*?>)[\s\S]*<\/VAST>/\$1<\/VAST>/i
@@||example.org^$replace
@@||example.org^$document  -- 禁用所有 $replace 规则
```

**特性：** 不适用于二进制响应；响应 >10MB 不生效；优先级高于其他基本规则（包括例外规则），但 `$content` 例外可覆盖；多条规则按字母序逐条应用。

---

## `$urltransform` — URL 重写

通过正则替换修改请求 URL。**受信过滤器规则。** CoreLibs v1.15+。

**语法：** 一系列以 `|` 分隔的转换。支持 `substitute`（正则替换）和 `decode`（`b64` Base64 / `pct` 百分号编码）。

```adblock
||example.org^$urltransform=/(pref\/).*\/(suf)/\$1\$2/i
```

**改变 origin：** 若 regexp 以 `^http` 开头，可修改完整 URL（CoreLibs v1.17+）。转换后的请求会重新匹配所有规则。

---

## `$reason` — 自定义拦截原因

在拦截页面显示自定义说明信息。需配合 `$document` 使用。

```adblock
||example.com^$document,reason="Tracker"
||tracking.example.com^$document,reason=tracker
||malware.example.com^$document,reason=disreputable
```

预定义可本地化 token：`malicious`、`tracker`、`disreputable`。CoreLibs v1.20+。

---

## `noop` — 空操作修饰符

不做任何事，仅提高规则可读性。由任意长度的 `_` 组成。

```adblock
||example.com$_,removeparam=/^ss\\$/,_,image
||example.com$replace=/bad/good/,___,~third-party
```

Content Blocker 不支持。

---

## `$empty` 👎（已废弃）

替代 `$redirect=nooptext`。返回空的 200 OK 响应。

```adblock
||example.org^$empty
```

---

## `$mp4` 👎（已废弃）

替代 `$redirect=noopmp4-1s,media`。返回短占位视频。

```adblock
||example.com/videos/$mp4
```
