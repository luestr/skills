# 规则优先级

> 当多条规则匹配同一请求时，优先级决定哪条规则生效。优先级为正整数，越大越优先。

## 核心概念

- 基础优先级 = **1**
- 优先级为浮点数时，**向上取整**为最小整数
- 同优先级规则冲突时，由引擎实现决定
- 优先级概念在 Manifest V3 中尤为重要（规则需转为 declarativeNetRequest）

**兼容性：** TSUrlFilter v2.1.0 / CoreLibs v1.13 引入。iOS/Safari/Content Blocker 依赖浏览器实现，不遵循此规则。

## 优先级分类（从低到高）

### 类别 1：基本修饰符（每个 +1）

- `$app`（否定应用，用 `~`）
- `$denyallow`
- `$domain`（否定域名，用 `~`）
- `$match-case`
- `$method`（否定方法，用 `~`）
- `$strict-first-party`
- `$strict-third-party`
- `$third-party`
- `$to`
- 受限内容类型（用 `~`）

**注意：** 否定域名/应用/方法/内容类型时，不论否定数量，只加 **1** 分（因规则范围已极广）。

### 类别 2：内容类型/方法/头/$all/$popup/特定例外

已定义的内容类型修饰符（`$document`、`$font`、`$image`、`$media`、`$object`、`$other`、`$ping`、`$script`、`$stylesheet`、`$subdocument`、`$websocket`、`$xmlhttprequest`）：

**加 `(50 + 50/N)`**，N 为修饰符数量。

```adblock
||example.com^$image,script   -- 50 + 50/2 = 75
```

也包括：
- `$all`（隐含所有内容类型）
- `$popup`（隐含 `$document`）
- 特定例外（`$content`、`$elemhide`、`$extension`、`$genericblock`、`$generichide`、`$jsinject`、`$specifichide`、`$urlblock`，隐含 `$document,subdocument`）
- `$method` 允许方法：**(50 + 50/N)**
- `$header`：**+50**

### 类别 3：`$domain` / `$app` 指定域名/应用

**加 `(100 + 100/N)`**，N 为修饰符值数量。

```adblock
||example.com^$domain=example.com|example.org|example.net  -- 100 + 100/3 ≈ 135
||example.com^$app=org.example.app1|org.example.app2       -- 100 + 100/2 = 150
||example.com^$domain=example.com,app=org.example.app1|org.example.app2
  -- $domain: 100+100/1 + $app: 100+100/2 = 350
```

TLD 和正则表达式按普通条目计算。

### 类别 4：特定例外

`$content`、`$elemhide`、`$extension`、`$genericblock`、`$generichide`、`$jsinject`、`$specifichide`、`$urlblock`：每个 **+10⁴**

`$document` 是上述的别名，**加 10⁴×5 = 50000**

### 类别 5：白名单规则

`@@` 标记 **+10⁵**

### 类别 6：`$redirect` 规则

`$redirect` 和 `$redirect-rule`：各 **+10³**

### 类别 7：`$important` 规则

`$important` **+10⁶**

### 无优先级权重的修饰符

其他执行预/后处理的[高级修饰符](#)不增加优先级。

**例外：** `$replace` 优先于类别 1-3 的所有拦截规则和类别 3-5 的例外规则，**但** `$content` 例外可覆盖 `$replace`。

## 计算示例

| 规则 | 计算 | 结果 |
|---|---|---|
| `\|\|example.com^` | 基础 | **1** |
| `\|\|example.com^$match-case` | 1 + 类别1: 1 | **2** |
| `\|\|example.org^$removeparam=p` | 1 + 0（无权重） | **1** |
| `\|\|example.org^$document,redirect=nooptext` | 1 + 类别3: (100+100/1) + 类别6: 1000 | **1201** |
| `@@\|\|example.org^$removeparam=p,document` | 1 + 类别5: 10000 + 类别2: (50+50/1) | **10101** |
| `@@\|\|example.com/ad/*$domain=example.org\|example.net,important` | 1 + 10000 + 1000000 + (100+100/2) | **1010152** |
| `@@\|\|example.org^$document` | 1 + 类别4: 10000×4 + 类别2: (50+50/2) | **40076** |
| `*$script,domain=a.com,denyallow=x.com\|y.com` | 1 + 类别2: (50+50/1) + 类别3: (100+100/1) + 类别1: 1 | **303** |
| `\|\|example.com^$all` | 1 + 类别2 popup: (50+50/12) | **55** |

## 优先级简记

```
$important (10⁶) > @@ (10⁵) > 特定例外 (10⁴) > $redirect (10³) > $domain/$app (100+) > 内容类型 (50+) > 基本修饰符 (1) > 无权重 (0)
```
