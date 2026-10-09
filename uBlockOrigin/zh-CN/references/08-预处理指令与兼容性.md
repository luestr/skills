# 预处理指令、不支持的功能与兼容性

> 条件编译的预处理指令、uBO 不支持的功能以及平台兼容性说明。

## 预处理指令（1.16.0+）

预处理指令以 `!#` 为前缀，因此旧版 uBO 和其他拦截器会将其视为注释并丢弃。它们在列表内容被解析**之前**执行，影响最终的过滤列表内容。

### `!#include [文件名]`

在指令出现的位置导入另一个过滤列表。子列表**必须**与主列表在同一目录中。

**正确的：**
```
!#include ublock-filters.txt
!#include ublock/filters.txt
```

**错误的：**
```
!#include https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters.txt
!#include ../filters.txt
```

目的：允许过滤列表维护者创建 uBO 特定的过滤规则，同时保持与其他拦截器的兼容性。

### `!#if [条件]`

条件编译 — 仅在条件满足时解析一块过滤规则。

```
!#if env_firefox
example.com##+js(nowebrtc)
!#endif
```

使用 `!` 取反：
```
!#if !env_firefox
example.com##^script:has-text(ad)
!#endif
```

### `!#else`（1.50.1b9+）

```
!#if cap_html_filtering
example.com##^script:has-text(fakeAd)
!#else
example.com##+js(rmnt, script, fakeAd)
!#endif
```

### 支持的条件令牌

| 令牌 | 值 | 说明 |
|---|---|---|
| `ext_abp` | **false** | 在 uBO 中始终为 false |
| `ext_ublock` | **true** | 在 uBO 中始终为 true |
| `ext_ubol` | 在 uBOL 上为 true | 1.44.3b12+ |
| `ext_devbuild` | 在开发版上为 true | 1.48.1b1+ |
| `env_chromium` | 在 Chromium 浏览器上为 true | |
| `env_edge` | 在 Edge（旧版）上为 true | |
| `env_firefox` | 在 Firefox 上为 true | |
| `env_mobile` | 在移动设备上为 true | |
| `env_safari` | 在 Safari（旧版 ≤12）上为 true | |
| `env_mv3` | uBOL 组装时为 true | 1.44.5b15+ |
| `false` | **false** | 1.22.0+ |
| `cap_html_filtering` | HTML 过滤可用时为 true | |
| `cap_user_stylesheet` | 在 Firefox、Chromium 66+ 上为 true | |
| `adguard` | **false** | 1.29.0+ |
| `adguard_app_*` | **false** | 所有 AdGuard 应用令牌 |
| `adguard_ext_*` | 参见版本说明 | 浏览器特定 |

**永久禁用一个块（1.22.0+）：**
```
!#if false
...被禁用的过滤规则...
!#endif
```

## 不支持的功能

### `document` 用于整页例外

不支持。例外过滤器上的 `document` 选项用于"可接受广告"，uBO 不支持此功能。用户必须通过受信站点功能显式信任站点。

**注意：** 在**拦截**过滤器上使用 `$document` 可以实现严格拦截，例外可以否定严格拦截。

### `genericblock`

不支持。会静默禁用大量通用过滤器（包括 hosts 文件条目和反跟踪列表），造成危险的安全漏洞。

### `$webrtc` 选项

不作为网络过滤器选项支持。改用 `nowebrtc` 脚本：
```
example.com##+js(nowebrtc)
```

### `elemhide` / `ehide`

**支持**，自 uBO 1.23.0 起（别名 `ehide`）。1.23.0 之前内部被转换为 `generichide`。

## 平台兼容性说明

### HTML 过滤
- 仅 Firefox
- 需要 `cap_html_filtering` 令牌
- 不适用于 Chromium 系浏览器

### CNAME 解封
- 仅 Firefox MV2（`$cname` 选项）
- Chromium 不支持扩展级别的 CNAME 解封

### 主机名正则
- 自 1.46.1b15 起可用
- 在主机名位置和 `$domain=`、`$to=`、`$from=` 中有效
- 谨慎使用 — O(n) 迭代对比普通主机名的 O(1) 查找

### 脚本日志
- 仅在开发版或设置 `filterAuthorMode` 高级设置时可用
- 所有日志现在显示在 uBO 的日志器中（1.57.3b1+）
- 旧的 `(log, 1)` 令牌方式已弃用

### 受信来源
以下来源可用于受限功能（`$replace`、受信脚本等）：
- uBO 自带过滤列表（"uBlock filters -- ..."）
- 用户的"我的过滤"（仅在勾选"允许需要信任的自定义过滤规则"时，或在开发版中）
- 通过 `trustedListPrefixes` 高级设置覆盖

## uBO 与其他拦截器的关键差异

| 功能 | uBO | ABP | AdGuard |
|---|---|---|---|
| `$document` 例外 | ❌ | ✅ | ✅ |
| `genericblock` | ❌ | ✅ | ✅ |
| `$webrtc` | ❌（用脚本） | ✅ | ✅ |
| `$replace` | 仅受信 | ❌ | 仅受信 |
| `$badfilter` | ✅ | ❌ | ✅ |
| `$denyallow` | ✅ | ❌ | ❌ |
| `$cname` | Firefox MV2 | ❌ | ❌ |
| HTML 过滤 `##^` | 仅 Firefox | ❌ | CoreLibs |
| `$header` 选项 | ✅ | ❌ | ✅ |
| `$method` 选项 | ✅ | ❌ | ✅ |
| HOSTS 解析 | `example.com` → `\|\|example.com^` | 模式匹配 | 模式匹配 |
| 脚本语法 | `##+js()` | N/A | `#%#//scriptlet()` |
| 过程式 CSS | 丰富 | 有限 | 丰富 |
| `$popunder` | ✅ | ❌ | ✅ |
| `$permissions` | ✅ | ❌ | ✅ |
