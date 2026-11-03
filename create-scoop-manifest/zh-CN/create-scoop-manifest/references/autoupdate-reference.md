# checkver 与 autoupdate

来源：wiki [App-Manifest-Autoupdate](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifest-Autoupdate)、`lib/autoupdate.ps1` 实现（变量大小写转换、hash 模式、内置正则）。

## 目录

- [分工](#分工)
- [checkver.ps1 参数](#checkverps1-参数)
- [checkver 策略](#checkver-策略)
- [四种源模式与模板](#四种源模式与模板)
- [autoupdate 各字段](#autoupdate-各字段)
- [autoupdate.hash 的六种模式](#autoupdatehash-的六种模式)
- [可替换变量全集](#可替换变量全集)
- [命名捕获组的大小写陷阱](#命名捕获组的大小写陷阱)
- [测试 autoupdate](#测试-autoupdate)

---

## 分工

- `checkver`：找出上游当前版本号。
- `autoupdate`：拿到版本号后，重建 `url`、`hash`、`extract_dir` 等字段。
- `bin/checkver.ps1 -u`：把上面两件事的结果写回 manifest。

只有 `checkver` 没有 `autoupdate`，`scoop update <app>` 仍然能发现新版本，但 manifest 不会自动重写。**永远把两个都配上**，否则每次发版都要手改 `version`、`url`、`hash` 三个字段。

---

## checkver.ps1 参数

```powershell
# 在 scoop 根目录（apps\scoop\current）或 bucket 仓库根目录执行
.\bin\checkver.ps1 <app>
.\bin\checkver.ps1 *                 # 全部
.\bin\checkver.ps1 <app> -u          # 查到新版本就写回
.\bin\checkver.ps1 <app> <dir> -u    # 指定目录（如 .\TODO）
```

| 参数 | 短写 | 说明 |
|---|---|---|
| `-App` | `-a` | manifest 名，支持通配 `*` |
| `-Dir` | `-d` | 搜索目录 |
| `-Update` | `-u` | 写回 manifest |
| `-ForceUpdate` | `-f` | 即使版本没变也检查并更新（验证 autoupdate 必用） |
| `-SkipUpdated` | `-s` | 只列出过期的 manifest |
| `-Version` | `-v` | 用指定版本检查，通常和 `-u` 搭配 |

排错时先 `scoop config debug $true`，能看到实际抓的 URL 与匹配过程。

---

## checkver 策略

### 1. 纯正则（在 homepage 上匹配）

```json
"homepage": "https://www.rust-lang.org",
"checkver": "Version ([\\d.]+)"
```

### 2. 换一个 URL 抓版本

```json
"homepage": "https://www.7-zip.org/",
"checkver": {
    "url": "https://www.7-zip.org/download.html",
    "regex": "Download 7-Zip ([\\d.]+)"
}
```

### 3. JSONPath

```json
"checkver": {
    "url": "https://example.com/app.config.json",
    "jsonpath": "$.latestVersion"
}
```

`jsonpath` 与 `jp` 等价。JSONPath 里可以带过滤表达式：

```json
"checkver": {
    "url": "https://dist.nuget.org/index.json",
    "jp": "$..versions[?(@.displayName == 'nuget.exe - recommended latest')].version"
}
```

### 4. JSONPath + 正则（先取串再匹配）

两个都写时，**先**用 JSONPath 取出字符串，**再**对其套 regex：

```json
"checkver": {
    "url": "https://nwjs.io/versions.json",
    "jsonpath": "$.stable",
    "regex": "v([\\d.]+)"
}
```

### 5. XPath

```json
"checkver": { "url": "https://example.com/versions.xml", "xpath": "/versions/stable/text()" }
```

### 6. GitHub release

```json
"homepage": "https://github.com/coreybutler/nvm-windows",
"checkver": "github"
```

内部用 `\/releases\/tag\/(?:v|V)?([\d.]+)` 匹配。要求上游确实用了 GitHub Releases 功能；**预发布版会被忽略**。

主页不是仓库时显式给仓库地址：

```json
"homepage": "http://cmder.net",
"checkver": { "github": "https://github.com/cmderdev/cmder" }
```

### 7. reverse

默认匹配**第一次**出现；`reverse: true` 匹配**最后一次**：

```json
"checkver": {
    "url": "https://download.videolan.org/pub/videolan/x264/binaries/win64/",
    "regex": "x264-r(?<version>[\\d]+)-(?<commit>[a-fA-F0-9]{7}).exe",
    "reverse": true
}
```

### 8. replace（重算版本号）

`checkver.replace` 可以用捕获组拼出版本：`${1}`、`${2}` 是无名组，`${name}` 是命名组。

```json
"checkver": {
    "url": "https://github.com/lukesampson/pshazz/commits/master.atom",
    "regex": "(\\d+)-(\\d+)-(\\d+)[\\S\\s]*?(?<sha>[0-9a-f]{40})",
    "replace": "0.${1}.${2}.${3}"
}
```

### 9. script（复杂抓取）

```json
"checkver": {
    "script": [
        "$page = Invoke-WebRequest 'https://example.com/download' -UseBasicParsing",
        "$page.Links.href | Where-Object { $_ -match 'Setup-([\\d.]+)\\.exe' } | Select-Object -First 1"
    ]
}
```

适合需要跟随多个链接、或上游结构完全非标的场景（UltraVNC、Spotify 这类）。`script` 的输出会再经过 `regex`（如果写了）。

### 10. useragent

个别站点按 UA 返回不同内容：

```json
"checkver": {
    "url": "https://www.telerik.com/download/fiddler",
    "useragent": "Mozilla/5.0 ..."
}
```

### checkver 支持的键

| 键 | 类型 | 说明 |
|---|---|---|
| `github` | URI | 仓库地址 |
| `url` | URI | 抓取页面；支持 version 变量 |
| `regex` / `re` | 正则 | 找版本 |
| `jsonpath` / `jp` | JSONPath | 找版本 |
| `xpath` | XPath | 找版本 |
| `reverse` | bool | 取最后一次匹配 |
| `replace` | 字符串 | 用捕获组重算版本；支持捕获变量 |
| `useragent` | 字符串 | 自定义 UA |
| `script` | 字符串 / 数组 | PowerShell 抓取逻辑 |

---

## 四种源模式与模板

### 模式 A：标准 GitHub release（最常见）

版本稳定、URL 可预测。

```json
{
    "version": "1.2.3",
    "description": "...",
    "homepage": "https://github.com/owner/repo",
    "license": "MIT",
    "architecture": {
        "64bit": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-x64.exe#/app.exe",
            "hash": ""
        },
        "arm64": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-arm64.exe#/app.exe",
            "hash": ""
        }
    },
    "bin": "app.exe",
    "checkver": "github",
    "autoupdate": {
        "architecture": {
            "64bit": { "url": "https://github.com/owner/repo/releases/download/v$version/app-x64.exe#/app.exe" },
            "arm64": { "url": "https://github.com/owner/repo/releases/download/v$version/app-arm64.exe#/app.exe" }
        }
    }
}
```

zip 版本（不用重命名）：

```json
"url": "https://github.com/owner/repo/releases/download/v1.2.3/app-1.2.3-windows-x64.zip",
"autoupdate": { "url": "https://github.com/owner/repo/releases/download/v$version/app-$version-windows-x64.zip" }
```

单 exe、不分架构：

```json
"url": "https://github.com/owner/repo/releases/download/v1.2.3/app.exe#/app.exe",
"bin": "app.exe",
"checkver": "github",
"autoupdate": { "url": "https://github.com/owner/repo/releases/download/v$version/app.exe#/app.exe" }
```

### 模式 B：CDN、URL 里带随版本变的 token

需要 `checkver` 用命名捕获组把 token 抠出来，`autoupdate.url` 再用 `$matchXxx` 回填。

```json
{
    "version": "7.65.8",
    "homepage": "https://example.com/",
    "license": { "identifier": "Freeware" },
    "url": "https://cdn.example.com/9f3a/App-win_64-7.65.8.exe#/dl.7z",
    "hash": "<sha256>",
    "checkver": {
        "url": "https://example.com/api/versions",
        "jp": "$.versions.Windows.download_link",
        "regex": "/(?<id>[\\w]+)/App-(?<arch>[\\w_]+)-([\\d\\.]+)\\.exe"
    },
    "autoupdate": {
        "url": "https://cdn.example.com/$matchId/App-$matchArch-$version.exe#/dl.7z",
        "hash": {
            "url": "https://example.com/api/versions",
            "jp": "$.versions.Windows.hash"
        }
    }
}
```

关键点：**版本必须是唯一一个无名组**（这里 `([\d\.]+)`），否则 checkver 会把 group 1 当成版本号。

### 模式 C：镜像 / 派生 URL

版本从上游原站探测，下载走镜像；路径常用 `$majorVersion.$minorVersion` 拼。

```json
"checkver": { "url": "https://upstream.example.org/download/", "regex": "blender-([\\d.]+)-windows-x64.zip" },
"autoupdate": {
    "url": "https://mirror.example.cn/blender/$majorVersion.$minorVersion/blender-$version-windows-x64.zip"
}
```

### 模式 D：签名 / 旋转链接背后取产物

落点页或 API 给的是每次请求都变的带 token 链接。此时**页面本身不能当 `url`**（内容每次都变，hash 不可复现），要定位到真正的公共 CDN 对象。

判定步骤：

1. 用不带 query 的 URL、以及带乱填 key 的 URL 各取一次。
2. 比较 `ETag` / `x-goog-generation` 与签名响应是否一致。
3. 一致 → 令牌只是装饰，直接用它：`https://.../App-$version.exe#/dl.7z`，`checkver` 仍盯官方页面。
4. 把会变的路径段做成命名组，但**版本保持第一个无名组**。

```json
"url": "https://dl.example.com/obj/app-$version.exe#/dl.7z",
"checkver": {
    "url": "https://example.com/download",
    "regex": "app-([\\d.]+)\\.exe"
}
```

---

## autoupdate 各字段

```json
"autoupdate": {
    "note": "Thanks for using autoupdate, please test your updates!",
    "architecture": {
        "64bit": { "url": "https://example.org/dl/example-v$version-x64.msi" },
        "32bit": { "url": "https://example.org/dl/example-v$version-x86.msi" }
    },
    "hash": { "url": "$baseurl/SHASUMS256.txt.asc" }
}
```

可放进 `autoupdate` 的字段：`bin`、`extract_dir`、`extract_to`、`env_add_path`、`env_set`、`installer`、`license`、`note`、`persist`、`post_install`、`psmodule`、`shortcuts`，以及最重要的 `url` 和 `hash`。

- 除 `note` 外，所有字段都可以写**全局**，也可以写在 `architecture.<arch>` 下。全局值会用于更新对应架构的字段——所以只写一个全局 `autoupdate.url`，就能同时更新 `architecture.64bit.url` 和 `architecture.32bit.url`。
- 除 `hash` 外，所有字段都支持捕获变量与版本变量。

**`autoupdate.url` 必须是能对任意未来版本成立的模板**。静态 `url` 里绝不能出现 `$version`——那是 404 的头号原因。

### 架构示例（nodejs / php / nginx / imagemagick）

```json
"autoupdate": {
    "architecture": {
        "64bit": { "url": "https://nodejs.org/dist/v$version/node-v$version-win-x64.7z", "extract_dir": "node-v$version-win-x64" },
        "32bit": { "url": "https://nodejs.org/dist/v$version/node-v$version-win-x86.7z", "extract_dir": "node-v$version-win-x86" }
    },
    "hash": { "url": "$baseurl/SHASUMS256.txt.asc" }
}
```

```json
"autoupdate": { "url": "https://nginx.org/download/nginx-$version.zip", "extract_dir": "nginx-$version" }
```

```json
"autoupdate": {
    "architecture": {
        "64bit": { "url": "https://www.imagemagick.org/download/binaries/ImageMagick-$version-portable-Q16-x64.zip" },
        "32bit": { "url": "https://www.imagemagick.org/download/binaries/ImageMagick-$version-portable-Q16-x86.zip" }
    },
    "hash": { "mode": "rdf", "url": "https://www.imagemagick.org/download/binaries/digest.rdf" }
}
```

---

## autoupdate.hash 的模式

`autoupdate.hash.mode` 的**实际可取值**（对着 `lib/autoupdate.ps1` 的 `switch ($hashmode)` 核过）：

| mode | 从哪取 | 关键键 | 如何被选中 |
|---|---|---|---|
| `extract` | 纯文本文件或网页 | `url` + `regex`/`find` | 默认值；写了 `hash.url` 但没给别的提示时也是它 |
| `json` | JSON 文件 | `url` + `jsonpath`/`jp` | 写了 `jp` 或 `jsonpath` 自动切过来 |
| `xpath` | XML 文件 | `url` + `xpath` | 写了 `xpath` 自动切过来 |
| `rdf` | RDF 文件 | `url` | 必须显式写 `"mode": "rdf"` |
| `metalink` | 下载响应头，或 `<url>.meta4` | `url` 可省 | 必须显式写 `"mode": "metalink"` |

**`mode: "download"` 不是一个合法取值**——switch 里没有这个分支，写了等于没写（会退回 `extract`）。「下载后本地计算」是**兜底行为**，不是模式：任何模式都没取到 hash 时，Scoop 会打印 `Downloading ... to compute hashes!` 然后真下载。

这个区别很重要：你没法用 `mode: download` **强制**它别去解析网页。想让它直接下载计算，就只写 `"hash": {}` 或者干脆不写 `hash`。

另有两种**自动**判定的预定义模式，不用写 `hash`：

- `fosshub`：`autoupdate.url` 匹配 `^(?:.*fosshub.com\/).*(?:\/|\?dwl=)(?<filename>.*)$` 时自动生效，内部正则 `$basename.*?"sha256":"([a-fA-F0-9]{64})"`。
- `sourceforge`：`autoupdate.url` 匹配 `(?:downloads\.)?sourceforge.net\/projects?\/(?<project>[^\/]+)\/(?:files\/)?(?<file>.*)` 时自动生效，内部正则 `"$basename":.*?"sha1":\s*"([a-fA-F0-9]{40})"`。注意它会把请求改到 `https://sourceforge.net/projects/<project>/files/<file>`，因为 `downloads.sourceforge.net` 不提供校验和。

**还有第三种，wiki 完全没写**——`github` 自动模式：

- `autoupdate.url` 匹配 `https://github.com/<owner>/<repo>/releases/download/<tag>/<file>` 时，`hashmode` 自动变成 `github`。
- 它会去查 `https://api.github.com/repos/<owner>/<repo>/releases`，用 `$..assets[?(@.browser_download_url == '<你的 url>')].digest` 把这个 asset 的 digest 取出来。

这解释了一个常见现象：**标准 GitHub release manifest 里 `autoupdate.hash` 什么都不写也能更新 hash**。反过来说，如果你的 `autoupdate.url` 长得像 GitHub release 但实际不在那里（镜像、私有 CDN），这条自动模式就会去查一个不存在的 asset，然后落回「下载后本地计算」。要避免这种静默降级，显式写 `hash.url` + `find`/`jp`。

### extract（默认）

`find` 留空时会按**顺序**试两条内置正则（`lib/autoupdate.ps1` 的 `find_hash_in_textfile`）：

```text
1)  ^\s*([a-fA-F0-9]+)\s*$                     # 整份文件只有一个 hash（允许前后空白）
2)  ([a-fA-F0-9]{32,128})[\x20\t]+.*$basename(?:\s|$)|$basename[\x20\t]+.*?([a-fA-F0-9]{32,128})
```

第 2 条是**双向匹配**：`hash<空格>文件名` 或 `文件名<空格>hash` 都能命中。也就是说这两种清单格式都开箱可用：

```text
abcdef01... *example.zip           ← hash 在前
example.zip  abcdef01...           ← 文件名在前
```

第 1 条带 `\s*` 前后缀，所以末尾有换行/空格的单行 hash 文件也能直接用（原 wiki 写的是 `^([a-fA-F0-9]+)$`，对带换行的文件会失配）。

内置正则都没命中时，还会再试一次 `<hash...>` 形式的 metalink 正则 `'<hash[^>]+>([a-fA-F0-9]{64})'`。

不够用时自定义：

```json
"hash": {
    "url": "$baseurl/hashes.txt",
    "find": "SHA256\\($basename\\)=\\s+([a-fA-F\\d]{64})"
}
```

```json
"hash": {
    "url": "https://www.python.org/downloads/release/python-$cleanVersion/",
    "find": "$basename[\\S\\s]+?$md5"
}
```

### json

```json
"hash": {
    "mode": "json",
    "jp": "$.files.['$basename'].sha512",
    "url": "$baseurl/win32_openssl_hashes.json"
}
```

JSONPath 里同样可以用过滤表达式：

```json
"hash": { "mode": "json", "jsonpath": "$..versions[?(@.downloadText == '$basename')].sha256", "url": "..." }
```

### xpath / rdf

```json
"hash": { "url": "https://example.com/chrome.xml", "xpath": "/chromechecker/stable64[version=\"$version\"]/sha256" }
"hash": { "mode": "rdf", "url": "https://www.imagemagick.org/download/binaries/digest.rdf" }
```

### metalink

```json
"hash": { "mode": "metalink" }
```

从下载 URL 的响应头，或同目录的 `.meta4` 文件取。

### 用捕获 / 版本 / URL 变量拼 hash.url

```json
"checkver": { "regex": "<strong>(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})</strong>...(?<version>[\\d.a-z\\-]+)" },
"autoupdate": {
    "architecture": {
        "64bit": {
            "url": "https://example.org/w64/qemu-w64-setup-$matchYear$matchMonth$matchDay.exe#/dl.7z",
            "hash": { "url": "https://example.org/w64/qemu-w64-setup-$matchYear$matchMonth$matchDay.sha512" }
        }
    }
}
```

```json
"hash": { "url": "https://julialang-s3.julialang.org/bin/checksums/julia-$version.sha256" }
"hash": { "url": "$url_fossies.sha256" }
```

### hash 提取失败会怎样

三种情形**实测**结果（直接调 `Invoke-AutoUpdate`，绕过网络版本探测）：

| manifest 的 autoupdate | 结果 |
|---|---|
| `{ "hash": { "url": ... } }`（有 hash，无 url） | **`version` 被改成新版本，`hash` 被写成空字符串 `""`**，退出码 0，日志只说 `Writing updated ... manifest`。manifest 被静默毁掉。 |
| `{ "url": ... }`（有 url，无 hash） | 打印 `Downloading <file> to compute hashes!` → 真下载 → `Computed hash: ...` → 写入正确 hash。 |
| `{ "url": ..., "hash": { "url": ... } }`（两者都有但供应商页里没匹配到） | 先 `Searching hash for ... in ...` → `Could not find hash in ...` → 落回本地下载计算 → 写入正确 hash。 |

所以：

- **`autoupdate` 里只要有 `hash` 就必须同时有 `url`**，否则每次 `checkver -u` 都把 hash 清空一次。这条比「hash 为空不会被自动更新」更危险，因为它会主动破坏已有的正确 hash。
- 本地下载兜底本身是可靠的（有网络、`autoupdate.url` 可达时），只是慢。
- 空 hash 一旦被写进 manifest，**后续 `checkver -u` 也补不回来**——`Update-ManifestProperty` 里空的 `$Manifest.hash` 会掉进 `architecture` 分支，而这一步同时要求 `$Manifest.architecture` 存在，否则在 `$null` 上取 `Get-Member` 报错。这时只能手工用 `hashurl.ps1` 补。

### 供应商校验和 vs 自己算

供应商发布了校验和文件（如 `SHA256SUMS`）时：

1. 用它做交叉验证；
2. 把 `autoupdate.hash` 指向它（`url` + `regex`/`jp`），而**不要**放任它走兜底的本地下载。

原因：厂商的校验和能证明「厂商发布了什么」，本地计算的只能证明「CDN 给了我什么」。

---

## 可替换变量全集

### 捕获变量

**在 `checkver.replace` 里**：

- `${1}`、`${2}`、`${3}`……：无名组
- `${name1}`、`${Name2}`：命名组（`(?<name1>...)`）

**在 `autoupdate` 里**：

- `$match1`、`$match2`……：无名组
- `$matchName1`、`$matchName2`……：命名组

### 版本变量

来自 `lib/autoupdate.ps1` 的 `Get-VersionVariables`（已核对实现）。`$Version` 先按 `-` 切成 `$firstPart`（第一段）和 `$lastPart`（最后一段）：

| 变量 | 实现 | `3.7.1.2-rc.1` 的结果 |
|---|---|---|
| `$version` | 原样 | `3.7.1.2-rc.1` |
| `$dotVersion` | `[._-]` → `.` | `3.7.1.2.rc.1` |
| `$underscoreVersion` | `[._-]` → `_` | `3_7_1_2_rc_1` |
| `$dashVersion` | `[._-]` → `-` | `3-7-1-2-rc-1` |
| `$cleanVersion` | 删掉 `[._-]` | `3712rc1` |
| `$majorVersion` | `$firstPart` 第 1 段 | `3` |
| `$minorVersion` | `$firstPart` 第 2 段 | `7` |
| `$patchVersion` | `$firstPart` 第 3 段 | `1` |
| `$buildVersion` | `$firstPart` 第 4 段 | `2` |
| `$preReleaseVersion` | `$lastPart` | `rc.1` |
| `$matchHead` | 正则 `(?<head>\d+\.\d+(?:\.\d+)?)(?<tail>.*)` 的 head | `3.7.1` |
| `$matchTail` | 同正则的 tail | `.2-rc.1` |

四个容易写错的地方：

1. **`$majorVersion` 系列切的是 `$firstPart`（`-` 之前那段）**，不是整个版本号。`1.0-beta.5` 只会在 `1.0` 上切，`$patchVersion` 是空。
2. **`$preReleaseVersion` 就是 `Split('-')` 的最后一段**，不是「最后一个 `-` 之后的通用解析」；版本里没有 `-` 时它等于整个版本号。
3. **`$dotVersion` 存在且有用**：`1.2.3_4` → `1.2.3.4`，比自己写 replace 稳。
4. **`$matchHead` / `$matchTail` 只在版本号形如 `<数字>.<数字>[.<数字>]` 时才被加入变量表**；否则这两个键根本不存在，模板里写了会原样留在生成的 url 里。

注意：原 wiki 表格把 `$underscoreVersion` 写成 `3_7_1_2-rc_1`（只替换点）是错的——实现是 `[._-]` 三类全替换。

### URL 变量

由 `get_hash_for_app` 注入，共五个（`$urlNoExt` / `$basenameNoExt` 是 wiki 没写的）：

| 变量 | 含义 | 例（url = `https://e.com/a/b/app-1.2.3.exe#/dl.7z`） |
|---|---|---|
| `$url` | autoupdate URL，剥掉 `#` 片段 | `https://e.com/a/b/app-1.2.3.exe` |
| `$baseurl` | `$url` 再去掉文件名、去掉尾部斜杠 | `https://e.com/a/b` |
| `$basename` | 文件名（URL 解码后，忽略片段） | `app-1.2.3.exe` |
| `$urlNoExt` | `$url` 去掉扩展名 | `https://e.com/a/b/app-1.2.3` |
| `$basenameNoExt` | `$basename` 去掉扩展名 | `app-1.2.3` |

`$basename` 经过 `UrlDecode`，所以文件名里带 `%20` 之类的编码时拿到的是解码后的真实名；`$baseurl` 会 `TrimEnd('/')`，拼 `$baseurl/x.sha256` 不会出现双斜杠。

### Hash 变量（用在 `hash.find` 里简化正则）

| 变量 | 等价正则 |
|---|---|
| `$md5` | `([a-fA-F0-9]{32})` |
| `$sha1` | `([a-fA-F0-9]{40})` |
| `$sha256` | `([a-fA-F0-9]{64})` |
| `$sha512` | `([a-fA-F0-9]{128})` |
| `$checksum` | `([a-fA-F0-9]{32,128})` |
| `$base64` | `([a-zA-Z0-9+\/=]{24,88})` |

---

## 命名捕获组的大小写陷阱

`autoupdate` 里的命名组变量名由这段代码生成（`lib/autoupdate.ps1`）：

```powershell
$versionVariables.Add('$match' + (Get-Culture).TextInfo.ToTitleCase($_.Name), $_.Value)
```

`ToTitleCase` **不是「首字母大写」**，而是把每个词首字母大写、其余字母**小写**。后果：

| 组名 | 生成的变量 | 你以为的 |
|---|---|---|
| `(?<build>...)` | `$matchBuild` | ✅ |
| `(?<buildId>...)` | `$matchBuildid` | ❌ `$matchBuildId` |
| `(?<build_id>...)` | `$matchBuild_Id` | ❌ `$matchBuild_id` |

**规则：命名组名只用单个小写单词。** 需要多个词时换更短的单字（`id`、`arch`、`file`、`path`、`sha`、`type`）。

主 bucket 里有两个真实的反例值得记住：

- `camunda-operate`：组名 `(?<genVer>...)`，autoupdate 里写 `$matchGenver` —— 名字对得上，**但反过来了**：程序生成的是 `$matchGenver`，manifest 写的是 `$matchGenVer`。这种最隐蔽，因为读代码时「genVer 首字母大写」看起来天经地义。
- `ngrok`：组名 `hashArm64` 生成 `$matchHasharm64`，而 manifest 里**正确地**写了 `$matchHasharm64`。所以看到这种「不正常」的写法先别改，先算一遍 ToTitleCase 结果。

全小写的组名（`date`、`arch`、`vs`、`version`）没有任何问题——ToTitleCase 之后和首字母大写完全一致。

### 另一个相关坑：第 1 个无名组抢走版本号

checkver 把**第一个无名捕获组**当作版本号。所以：

```json
"regex": "/(?<id>[\\w]+)/App-(?<arch>[\\w_]+)-([\\d\\.]+)\\.exe"   // ✅ 版本是唯一无名组
"regex": "/([\\w]+)/App-(?<arch>[\\w_]+)-([\\d\\.]+)\\.exe"        // ❌ 版本变成了 id
```

要么让版本成为唯一无名组，要么把版本命名为 `version` 且不写任何无名组（命名组只在 group 1 为空时作为兜底）。

---

## 测试 autoupdate

```powershell
cd <bucket repo>
scoop config debug $true
.\bin\checkver.ps1 <app> -u
```

或者把 `version` 改成更低的版本再跑一次（或用 `-f`），确认 `url`、`hash`、`extract_dir` 都被正确重写。然后 `scoop install bucket\<app>.json` 安装、运行、卸载。

**注意 `checkver -f` 只能证明「流程跑通」，不能证明「hash 真算出来了」**——hash 本来正确时它把同值写回去。要验证 hash 计算路径：

1. 临时把 hash 改成 64 个 `0`（不是空字符串——空 hash 会走 `architecture` 分支并保持为空）；
2. 清空 `SCOOP_CACHE`；
3. 跑 `checkver -f`；
4. 看是否回到你提交的真实值。

在临时副本上做（本技能 `scripts/provehash` 逻辑就是这么设计的），不要污染 `bucket/`。

已知 bucket 由 [ScoopInstaller/GithubActions](https://github.com/ScoopInstaller/GithubActions)（俗称 Excavator）自动巡检：`main` / `extras` 每小时，`versions` / `java` / `php` / `games` 每天。

### 日常工作流

```powershell
cd <bucket repo>
.\bin\checkver * -u        # 更新全部
git commit -m "Updated apps"
git push
scoop update
scoop status               # 现在看到的是真实版本差
scoop update <app>
```
