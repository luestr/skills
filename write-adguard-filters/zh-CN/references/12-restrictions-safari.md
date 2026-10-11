# 限制与兼容性：SafariConverterLib、Content Blocker、受信过滤器

> 编写 Safari/iOS 过滤规则前必读。

## 受信过滤器 (Trusted Filters)

以下规则只能在受信过滤器中使用：
- `$replace`、`$hls`、`$jsonprune`、`$xmlprune`、`$urltransform`
- `$removeheader`、`$removeparam`
- JavaScript 规则 (`#%#`)
- 脚本片段规则 (`//scriptlet()`)

受信过滤器包括：
- AdGuard 团队创建的过滤列表
- 安装为 `trusted` 的自定义过滤列表
- 用户规则

---

## AdGuard Content Blocker

Android 上三星和 Yandex 浏览器的扩展。功能非常有限，仅支持旧的 ABP 语法：

- 基本拦截规则：仅 `$domain`、`$third-party`、内容类型修饰符
- 基本例外规则：仅 `$document`、`$elemhide`
- 基本元素隐藏规则（不支持 Extended CSS）

**不支持：** CSS 规则、HTML 过滤、JavaScript、脚本片段及所有高级修饰符。

---

## SafariConverterLib 详细限制

Safari Converter 尽可能支持 AdGuard 语法规则，但仍有重要限制。

### 基本（网络）规则

#### 有限制支持

| 项目 | 限制说明 |
|---|---|
| **正则表达式** | 仅限 [Safari 支持的正则子集](https://developer.apple.com/documentation/safariservices/creating-a-content-blocker#Capture-URLs-by-pattern) |
| **`$domain`** | ① 不允许混合允许和排除域名（如 `$domain=example.org\|~sub.example.org`）<br>② `domain.*` 不完全支持（仅替换为前 100 个热门 TLD）<br>③ 不支持正则表达式 |
| **`$denyallow`** | 通过转换为一组规则实现，**必须同时有 `$domain` 修饰符** |
| **`$popup`** | 等同于 `$document` 拦截，不会尝试关闭标签页 |
| **`@@` 例外规则** | 无修饰符的例外会禁用所有过滤（包括外观规则），因为 Safari 的 `ignore-previous-rules` 机制 |
| **`$urlblock`/`$genericblock`** | 等同于 `$document`，禁用所有过滤 |
| **`$content`** | 仅兼容目的，限制为 `document` 资源类型 |
| **`$specifichide`** | 必须以域名开头（如 `\|\|example.org^$specifichide`），不覆盖子域名 |
| **单修饰符限制** | `urlblock`、`genericblock`、`generichide`、`elemhide`、`specifichide`、`jsinject` 只能作为规则中的唯一修饰符 |

#### 不支持的修饰符

`$app`、`$header`、`$method`、`$extension`、`$stealth`、`$cookie`、`$csp`、`$hls`、`$inline-script`、`$inline-font`、`$jsonprune`、`$xmlprune`、`$network`、`$permissions`、`$redirect`、`$redirect-rule`、`$referrerpolicy`、`$removeheader`、`$removeparam`、`$replace`、`$urltransform`

**计划支持：** `$strict-first-party`、`$strict-third-party`、`$to`、`$cookie`（部分）

---

### 外观规则限制

- 域名限制受与基本规则的 `$domain` 相同的限制
- `$path` 支持，但正则受 Safari 子集限制
- `$url` 尚不支持

---

### 脚本/脚本片段规则

- **完全支持** JS 规则和脚本片段规则，但只能通过单独的扩展解释
- **重要：** 脚本片段应尽早运行（在页面脚本之前），Safari 中始终会有轻微延迟

---

### HTML 过滤规则

**不支持且不会支持**——Safari 不提供必要的技术能力。

---

### Safari 内容拦截器架构

Safari 每个内容拦截器限 **150,000** 条活跃规则。AdGuard 拆分为 6 个拦截器，总限 **900,000** 条：

| 拦截器 | 内容 |
|---|---|
| `general` | 广告拦截、语言特定 |
| `privacy` | 隐私 |
| `social` | 社交组件、烦扰 |
| `security` | 安全 |
| `other` | 其他 |
| `custom` | 自定义 |

用户规则和白名单添加到所有拦截器。

**关键问题：** 不同拦截器中的规则独立应用。拦截规则在 A 拦截器、例外在 B 拦截器时，**例外不会生效**。使用 `!#safari_cb_affinity` 指令将相关规则放入同一拦截器。

```adblock
!#safari_cb_affinity(general)
example.org#@#.adBanner
!#safari_cb_affinity
```

---

## 已移除的修饰符

| 修饰符 | 状态 | 替代方案 |
|---|---|---|
| `$object-subrequest` | 🚫 已移除 | 无 |
| `$webrtc` | 🚫 已移除 | `nowebrtc` 脚本片段 |
| `$empty` | 👎 已废弃 | `$redirect=nooptext` |
| `$mp4` | 👎 已废弃 | `$redirect=noopmp4-1s,media` |
| `:if-not()` | 🚫 已移除 | `:not(:has())` |
| `:if()` | 🚫 已移除 | `:has()` |
