# 预处理器指令、提示与调试

## 预处理器指令

过滤器维护者用于提高兼容性的指令。任何错误都会导致过滤器更新失败。

指令可用于用户规则和自定义过滤器。

---

### `!#include` — 包含文件

将指定文件的内容包含到过滤器中。仅支持同源文件。

**语法：**
```adblock
!#include 文件路径
```

- 支持绝对和相对路径
- 包含的文件中可嵌套 `!#include`（需实现递归保护）
- 文件未找到会导致整个过滤器更新失败
- 本地自定义过滤器不受同源限制

**示例：**
```adblock
过滤器 URL: https://example.org/path/filter.txt

!#include https://example.org/path/includedfile.txt    -- 同源绝对路径
!#include /includedfile.txt                             -- 相对路径
!#include ../path2/includedfile.txt                     -- 相对路径
!#include https://domain.com/path/includedfile.txt      -- ❌ 不同源
```

---

### `!#if` / `!#else` / `!#endif` — 条件指令

根据广告拦截器类型有条件地应用规则。支持基本逻辑运算符。

**语法：**
```adblock
!#if (条件)
规则列表
!#endif
```

```adblock
!#if (条件)
条件为真时的规则
!#else
条件为假时的规则
!#endif
```

**可用常量：**
- `adguard` — 始终声明，适用于 95% 的情况
- **产品特定常量：**
  - `adguard_app_windows` — AdGuard for Windows
  - `adguard_app_mac` — AdGuard for Mac
  - `adguard_app_cli` — AdGuard for Linux
  - `adguard_app_android` — AdGuard for Android
  - `adguard_app_ios` — AdGuard for iOS
  - `adguard_ext_safari` — AdGuard for Safari
  - `adguard_ext_chromium` — AdGuard Browser Extension for Chrome
  - `adguard_ext_chromium_mv3` — AdGuard for Chrome MV3
  - `adguard_ext_firefox` — AdGuard Browser Extension for Firefox
  - `adguard_ext_edge` — AdGuard Browser Extension for Edge Legacy
  - `adguard_ext_opera` — AdGuard Browser Extension for Opera
  - `adguard_ext_android_cb` — AdGuard Content Blocker
  - `ext_ublock` — uBlock Origin（FiltersRegistry 编译时）
  - `cap_html_filtering` — 支持 HTML 过滤的产品

**示例：**
```adblock
!#if (adguard && !adguard_ext_safari)
||example.org^$third-party
domain.com##div.ad
!#endif

!#if (adguard_app_android)
!#include /androidspecific.txt
!#endif

!#if (adguard && !adguard_ext_safari)
||example.org^$third-party
!#else
||subdomain.example.org^$third-party
!#endif
```

**`!#else` 兼容性：** FiltersDownloader v1.1.20+、CoreLibs v1.13+、Browser Extension v4.2.208+、Safari v1.11.16+。

---

### `!#safari_cb_affinity` — Safari 内容拦截器亲和性

Safari 每个内容拦截器限 150,000 条活跃规则。AdGuard 将规则分为 6 个内容拦截器，总限 900,000 条。

**内容拦截器组成：**
- `general` — 广告拦截、语言特定
- `privacy` — 隐私
- `social` — 社交组件、烦扰
- `security` — 安全
- `other` — 其他
- `custom` — 自定义
- `all` — 所有内容拦截器

**问题：** 不同拦截器中的规则独立应用。拦截规则在一个拦截器，例外在另一个时，例外不会生效。

**语法：**
```adblock
!#safari_cb_affinity(拦截器列表)
规则列表
!#safari_cb_affinity
```

**示例：**
```adblock
!#safari_cb_affinity(general)
example.org#@#.adBanner
!#safari_cb_affinity

!#safari_cb_affinity(privacy)
@@||example.org^
!#safari_cb_affinity
```

---

## 提示 (Hints)

特殊的注释指令，用于服务端过滤器编译器。

**语法：**
```adblock
!+ 提示名1(参数) 提示名2(参数)
```

---

### `NOT_OPTIMIZED` — 不优化

防止规则在优化版本中被移除。

```adblock
!+ NOT_OPTIMIZED
||example.org^

!+ NOT_OPTIMIZED PLATFORM(android)
||example.org^
```

---

### `PLATFORM` / `NOT_PLATFORM` — 平台限定

指定规则应用的平台。

**平台列表：**
`windows`、`mac`、`cli`（Linux）、`android`、`ios`、`ext_chromium`、`ext_chromium_mv3`、`ext_ff`、`ext_edge`、`ext_opera`、`ext_safari`、`ext_android_cb`、`ext_ublock`

```adblock
!+ PLATFORM(windows,mac,android)
||example.org^

!+ NOT_PLATFORM(ext_safari, ext_android_cb, ios)
||example.org^
```

---

### `NOT_VALIDATE` — 跳过验证

跳过规则验证，用于尚未支持的规则或被错误丢弃的规则。

```adblock
!+ NOT_VALIDATE
||example.org^$newmodifier
```

---

## 调试方法

### 过滤日志 (Filtering Log)

列出通过 AdGuard 的所有网络请求的详细工具。

**各产品位置：**
- **Windows:** Ad Blocker 标签页或托盘菜单
- **Mac:** 设置 → 高级 → 过滤日志
- **Android:** 统计 → 最近活动
- **Browser Extension:** 杂项设置标签页或右键扩展图标

**iOS/Safari 不存在过滤日志**（Safari 内容拦截器实现方式限制）。

---

### 选择器调试模式

使用 `debug` 样式属性检查选择器性能。

**单个选择器调试：**
```adblock
#$?#.banner { display: none; debug: true; }
```

**全局调试：**
```adblock
#$?#.banner { display: none; debug: global; }
```

**不使用 AdGuard 测试 ExtendedCss：**
```js
!function(e,t,d){C=e.createElement(t),C.src=d,C.onload=function(){alert("ExtendedCss loaded")},s=e.getElementsByTagName(t)[0],s?s.parentNode.insertBefore(C,s):(h=e.getElementsByTagName("head")[0],h.appendChild(C))}(document,"script","https://AdguardTeam.github.io/ExtendedCss/extended-css.min.js");

// 使用
const selector = 'div.block:has=(.header:matches-css(after, content: Ads))';
ExtendedCss.query(selector);
```

---

### 调试脚本片段

在 Browser Extension 中打开过滤日志，脚本片段会切换到调试模式。

**专用调试脚本片段：**
- `debug-current-inline-script`
- `debug-on-property-read`
- `debug-on-property-write`
- `log-addEventListener`
- `log-on-stack-trace`
- `log-eval`
- `log`

**可用于调试的脚本片段：**
- `json-prune`、`prevent-fetch`、`prevent-requestAnimationFrame`、`prevent-setInterval`、`prevent-setTimeout`、`prevent-window-open`、`prevent-xhr`、`trusted-replace-fetch-response`、`trusted-replace-xhr-response`

---

## 兼容性图例

| 符号 | 含义 |
|---|---|
| ✅ | 完全支持 |
| ✅ * | 有限制支持 |
| 🧩 | 可在 nightly/beta 中使用 |
| ⏳ | 计划实现但尚未可用 |
| ❌ | 不支持 |
| 👎 | 已废弃 |
| 🚫 | 已移除 |

**产品缩写：**
- **CoreLibs apps** — Windows/Mac/Android/Linux
- **AdGuard for Chromium** — Chrome/Edge/Opera 扩展
- **AdGuard for Chrome MV3** — Chrome MV3 扩展
- **AdGuard for Firefox** — Firefox 扩展
- **AdGuard for iOS** — iOS Safari
- **AdGuard for Safari** — 桌面 Safari
- **AdGuard Content Blocker** — Android 三星/Yandex 浏览器
