# JavaScript 规则 & 脚本片段规则

## JavaScript 规则

向网站页面注入任意 JavaScript 代码。**强烈建议优先使用脚本片段规则。** JS 规则主要用于调试。

**语法：**
```
规则 = [域名] "#%#" 脚本
```

- `域名` — 域名限制
- `脚本` — **单行** JavaScript 代码

**示例：**
```adblock
example.org#%#window.__gaq = undefined;
```

**例外规则：** 使用 `#@%#` 代替 `#%#`
```adblock
example.com#@%#window.__gaq = undefined;
#@%#window.__gaq = undefined;       -- 禁用所有域名
```

**限制：** 只能在**受信过滤器**中使用。Content Blocker 不支持。

---

## 脚本片段规则 (Scriptlet Rules)

脚本片段是用于内容拦截的 JavaScript 函数，以声明方式在过滤规则中使用。

**语法：**
```
[域名]#%#//scriptlet(名称[, 参数1[, 参数2[, ...]]])
```

**示例：**
```adblock
example.org#%#//scriptlet('abort-on-property-read', 'alert')
example.org#%#//scriptlet('remove-class', 'branding', 'div[class^="inner"]')
```

**例外规则语法：**
```
[域名]#@%#//scriptlet([名称[, 参数]])
```

- 不指定名称 → 禁用所有脚本片段
- 指定名称 → 仅禁用特定脚本片段
- 指定参数 → 匹配相同参数的规则

**示例：**
```adblock
! 禁用特定脚本片段
example.org,example.com#%#//scriptlet("abort-on-property-read", "alert")
example.com#@%#//scriptlet("abort-on-property-read", "alert")

! 禁用指定名称的所有脚本片段
example.com#@%#//scriptlet("abort-on-property-read")

! 禁用所有脚本片段
example.com#@%#//scriptlet()

! 混合使用
#%#//scriptlet('set-constant', 'adList', 'emptyArr')
#%#//scriptlet('set-cookie', 'accepted', 'true')
example.org#@%#//scriptlet('set-cookie')
```

**兼容性：** 不受 Content Blocker 支持。完整例外语法需 CoreLibs v1.16+ / TSUrlFilter v3.0+。

**限制：** 只能在**受信过滤器**中使用。

更多脚本片段信息：https://github.com/AdguardTeam/Scriptlets#scriptlets

---

## 受信脚本片段 (Trusted Scriptlets)

功能扩展的脚本片段，名称以 `trusted-` 为前缀（如 `trusted-set-cookie`）。

**语法与限制：** 与普通脚本片段相同。

**注意：**
- 与其他广告拦截器不兼容（仅 AdGuard 支持）
- 只能在**受信过滤器**中使用
- Content Blocker 不支持

更多受信脚本片段信息：https://github.com/AdguardTeam/Scriptlets#trusted-scriptlets
