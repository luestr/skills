---
name: create-scoop-manifest
description: >
  为 Windows 应用创建与维护 Scoop bucket manifest（bucket 目录下的 appname.json），以及围绕它的安装、校验、体检与排错。
  当用户说「生成 scoop manifest」「给 xxx 写 manifest」「加到我的 bucket」「提交 PR 到 scoop-extras / main / versions」
  「写 checkver / autoupdate」「这个包装了没 / 怎么装」「bucket 里的包过期了 / hash 不对 / 审计一下」
  「和 BucketTemplate 同步 / 升 GitHub Actions」「scoop 报错 / 装不上 / 解压失败 / 缺 hash / 找不到包 / 下载慢」时，
  都必须使用本技能，即使对方没有明确说出「scoop」这个词。
  只要涉及 Windows 上的 app manifest（NSIS .exe / MSI / 便携 .zip）、bucket 仓库、可移植软件安装或 Scoop 自身配置与排错，就触发本技能；
  只发 macOS/Linux 包的项目不适用。
metadata:
  language: zh-CN
---

# Scoop Manifest

Scoop 是 Windows 的命令行包管理器：装到用户目录、不要管理员权限、不留注册表垃圾、PATH 干净、依赖自动处理。它本身是一堆 PowerShell 脚本，**装什么、怎么装，完全由 bucket 里的 JSON manifest 描述**——所以本技能的重心是 manifest 的创作与维护。

**核心心智模型**：Linux 式的包管理（`apt-get` / `brew` 的等价物），但包定义是纯 JSON，可以自己写、自己托管、自己维护。

## 三条主线，先判断走哪条

| 用户想做的事 | 走哪条线 | 主入口 |
|---|---|---|
| **给某个应用写 manifest、加进 bucket、提 PR** | **B 创作（主线）** | 本文 §B |
| **已有 bucket 的体检、修复、和模板同步** | **C 维护（主线）** | 本文 §C |
| 装软件、配环境、更新、卸载、切版本、代理、全局安装 | A 使用（配套） | 本文 §A |

§B 与 §C 是本技能的主体；§A 是创作与维护 manifest 时需要的那部分使用知识——你总得先能 `scoop install`、`scoop update`、看懂 `scoop info` 的输出，才能验证自己写的 manifest 对不对。

判断入口：用户手里有没有一个「bucket 仓库」。有 → 走 B/C；没有、只是想装东西 → 走 A。

---

# §A 使用：安装与日常管理

## A1 前置条件（不满足则先修，别急着装）

- PowerShell 5.1+（`$PSVersionTable.PSVersion` 至少 5.1）；PowerShell 7 更好，且能绕开 5.1 下 `get.scoop.sh` 被杀软误报的问题。
- Language Mode 必须是 `FullLanguage`，ExecutionPolicy 必须是 `RemoteSigned` / `Unrestricted` / `ByPass`。
- **在非管理员 PowerShell 里装**。管理员控制台默认被禁用（安全考虑），要用得显式加 `-RunAsAdmin`。

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

默认装到 `C:\Users\<用户名>\scoop`。自定义目录、全局目录、缓存目录、代理、CI、静默安装、管理员安装——全部参数与写法见 `references/install-and-setup.md`。

## A2 装完之后第一件事

```powershell
scoop install git 7zip
scoop bucket add extras
```

`git` 是加 bucket 的硬依赖（没有它 `scoop bucket add` 直接报错）；`7zip` 解压绝大多数包；`innounp`、`dark` 分别解 InnoSetup 与 WiX 安装器。`scoop checkup` 会替你检查这几样和 NTFS / lang path / 开发者模式。

## A3 日常命令（完整选项见 `references/cli-reference.md`）

| 任务 | 命令 |
|---|---|
| 装 | `scoop install <app>`（`-g` 全局、`-i` 不装依赖、`-k` 不用缓存、`-s` 跳过 hash 校验、`-a <arch>` 指定架构） |
| 装指定版本 | `scoop install <app>@<version>` |
| 从 URL / 本地文件装 | `scoop install <url-or-path>.json` |
| 卸载 | `scoop uninstall <app>`（`-p` 同时清 persist 数据） |
| 更新 Scoop 自身 + manifest | `scoop update` |
| 更新单个 / 全部 app | `scoop update <app>` / `scoop update *` |
| 看已装 | `scoop list [query]` |
| 搜 | `scoop search <keyword>`（无参列出全部；不开 sqlite 缓存时 query 是正则） |
| 看详情 | `scoop info <app>`（`-v` 显示完整路径与 URL） |
| 看哪些过期 | `scoop status`（`-l` 只看本地，不联网） |
| 清旧版本 | `scoop cleanup *`（`-k` 连过期下载缓存一起清） |
| 清下载缓存 | `scoop cache rm *` |
| 锁版本 | `scoop hold <app>` / `scoop unhold <app>` |
| 切版本 | `scoop reset <app>@<version>`（只在**已安装**的版本间切换） |
| 备份 / 恢复 | `scoop export > scoopfile.json`（`-c` 含配置）/ `scoop import scoopfile.json` |
| 找 shim 真实路径 | `scoop which <cmd>` |
| 打开主页 | `scoop home <app>` |
| 看依赖顺序 | `scoop depends <app>` |

其他：`alias`（自定义子命令）、`cat`（打印 manifest）、`create`（交互式生成 manifest）、`download`（只下不装到 cache 并校验 hash）、`prefix`（返回安装路径）、`shim`（add/rm/list/info/alter）、`virustotal`（按 hash/URL 查毒）、`cache show|rm`、`checkup`。

## A4 三条容易踩的用户级规则

1. **`scoop status` 依赖本地 bucket 的新鲜度**。它比的是「已安装版本」和「本地 manifest」，不 `scoop update` 就会显示过时信息。`scoop update` 每 3 小时会被自动触发一次（install/update/download/virustotal 时）。
2. **多版本共存靠 `reset`，不靠重装**。`scoop install python python27` 后 `scoop reset python27` 切过去；`scoop reset python` 回到最新已装版本。`scoop list` 只显示最新版本，`scoop info <app>` 才列出全部已装版本。
3. **`current` 是目录联接（junction），不是真实目录**。所以任何外部工具（文件关联、IDE、快捷方式）都该指向 `apps\<app>\current\...`，绝不要指向版本目录，也绝不要指向 shims（见 `references/troubleshooting.md` 的 Open With 一节）。

## A5 常用配置（`scoop config`，存在 `~/.config/scoop/config.json`）

```powershell
scoop config proxy currentuser@default          # 用当前 Windows 凭据走系统代理
scoop config proxy 127.0.0.1:7890                # 匿名走本地代理
scoop config rm proxy                           # 绕过系统代理
scoop install aria2; scoop config aria2-enabled true
scoop config aria2-warning-enabled false        # 关掉 aria2 的告警
scoop config use_sqlite_cache true              # 加速 search/shim
scoop config use_external_7zip true             # 用 PATH 上的 7z
scoop config no_junction true                   # 不用 current 别名
scoop config default_architecture 64bit
scoop config gh_token <token>                   # checkver 防限流、私有仓库
scoop config debug true                         # 排错时打开
```

全部配置项（含 `scoop_branch`、`root_path`、`global_path`、`private_hosts`、`use_isolated_path`、`ignore_running_processes` 等）见 `references/cli-reference.md`。

## A6 bucket 基础

bucket = 装着 JSON manifest 的 Git 仓库。`main` 随 Scoop 自带。社区已知 bucket：`extras` `versions` `nirsoft` `sysinternals` `php` `nerd-fonts` `nonportable` `java` `games`；`scoop bucket known` 看全量。

```powershell
scoop bucket add extras                      # 已知 bucket，不用给 URL
scoop bucket add my-bucket https://github.com/<user>/my-bucket   # 自定义
scoop bucket list
scoop bucket rm <name>
```

---

# §B 创作：写一个 manifest

Scoop 从 `bucket/<appname>.json` 安装应用。目标是写出版本化 manifest，并把 `checkver` + `autoupdate` 配好，让 Scoop 从此自动跟发版，不再手改 `version`/`url`/`hash`。

**先判断该不该做**：项目要发 Windows 二进制（NSIS `.exe`、MSI、便携 `.zip`/`.7z`），且 URL 稳定（通常 GitHub Releases）。只发 macOS/Linux 包的，Scoop 不适用——说清楚再停。

字段全集、license 写法、架构块、persist、psmodule、shortcuts、installer 全部定义：`references/manifest-reference.md`。checkver/autoupdate 的每个策略、每种 hash 提取模式、全部可替换变量：`references/autoupdate-reference.md`。

## B1 先探源，绝不猜 URL

```bash
gh repo view <owner>/<repo> --json url,description,licenseInfo -q '{homepage:.url, description:.description, license:.licenseInfo.spdxId}'
gh api repos/<owner>/<repo>/releases/latest --jq '{version:.tag_name, assets:[.assets[]|{name,size,browser_download_url,digest}]}'
```

非 GitHub 源：JSON 接口用 `curl ... | jq`，HTML 页面用 `curl ... | htmlq "a[href*='.exe']" --attribute href`。拿到 version（**剥掉 `v` 前缀**）、Windows 资源名（分 64bit/arm64/32bit）、homepage、description、license。

Node/Electron 项目另读 `package.json`：`build.productName`、`build.win.executableName`、`build.win.artifactName` 模板。其他生态看 `Cargo.toml`、`pyproject.toml`、`*.spec`、`installer/`。

## B2 拿版本 / URL / sha256——不下安装包

GitHub Release API 的每个 asset 都带 `digest: sha256:<hex>`，**这就是 Scoop 要的 hash**。为了算 hash 去下 500 MB 安装包是整个流程里最浪费时间的错误。

```bash
node <skill>/scripts/fetch-windows-assets.mjs <owner>/<repo> [tag]
# 没有 node 时的等价实现
pwsh -NoProfile -File <skill>/scripts/fetch-windows-assets.ps1 <owner>/<repo> [tag]
```

打印 tag、剥掉 `v` 的版本号、每个 Windows 资源的 URL / 大小 / sha256。非 GitHub 源没有 digest，只能下下来自己算：`<skill>/scripts/hashurl.ps1 <url>`。

## B3 选安装形态（决定 manifest 怎么写）

```text
只发便携 .zip/.7z            → 直接用，必要时 extract_dir            （首选）
同时发 .zip 和 NSIS .exe     → 选 .zip
只发 NSIS .exe               → 两种走法：
   a) NSIS 静默安装能跑通     → 直接给 bin，交给 installer
   b) /S 会弹 GUI 或提取失败  → pre_install + 7z 两段解压（见 references/installers-and-extraction.md）
MSI                          → 不要写 msi 块（已废弃），当 zip 解压
InnoSetup                    → "innosetup": true，Scoop 用 innounp 解
WiX / dark                   → 用 dark 解
```

判断 NSIS 内层结构：`7z l <file>.exe`；electron-builder 的产物解开会出现 `$PLUGINSDIR\app-64.7z`（真正的应用包在里头）。`7z l` 报 `Type = PE` 不代表不可解——同一个 listing 里往往就有内嵌 7z 流。

`#/dl.7z` 这个 URL 后缀是最省事的绕法：让 Scoop 把安装器当 7z 解，跳过执行与 UAC。NSIS 静默安装失败时的完整脱困方案（含 `$PLUGINSDIR` 引号坑、`$dir`/`$fname` 作用域、本地复现测试）在 `references/installers-and-extraction.md`。

## B4 写 JSON

必填：`version` `description` `homepage` `license` `url` `hash`。字段顺序、4 空格缩进、数组单元素写成字符串等风格硬规则见 `references/manifest-reference.md`。

**最容易写错的一条**：静态 `url` 用**字面版本号**，`autoupdate.url` 用 `$version`。写反了装的时候 404。

```json
{
    "version": "1.2.3",
    "description": "One-line description without the app name",
    "homepage": "https://github.com/owner/repo",
    "license": "MIT",
    "architecture": {
        "64bit": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-x64.exe#/app.exe",
            "hash": "<sha256>"
        },
        "arm64": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-arm64.exe#/app.exe",
            "hash": "<sha256>"
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

四种源模式（GitHub release / CDN 带 token / 镜像派生 URL / 签名旋转链接）与各自模板见 `references/autoupdate-reference.md` §模式。

**`checkver` 与 `homepage` 的绑定**：`"checkver": "github"` 会从 `homepage` 读仓库地址，所以 homepage 必须是 GitHub 仓库 URL，或者是自定义页面时用 `"checkver": { "github": "<repo url>" }`。用独立产品页配 `"github"` 会让 checkver 直接失败。

## B5 校验——按顺序跑，每步过了再下一步

```bash
# 0. 离线静态检查：字段、hash 形态、autoupdate.url 能否复现静态 url
pwsh -NoProfile -File <skill>/scripts/manifest-lint.ps1 bucket/<appname>.json

# 1. 版本探测
pwsh -NoProfile -Command "cd '<bucket>'; .\bin\checkver.ps1 <appname>"

# 2. 安装验证
scoop install '<bucket>\bucket\<appname>.json'
<appname> --version
scoop uninstall <appname>
```

没装 Scoop 时至少：`node -e "require('./bucket/<appname>.json')"` + `curl -I` 确认 URL 200。

`checkver -u`（强制更新）能证明 autoupdate 能写回 `version`/`url`/`hash`。但**哈希是否真被算出来**要单独验：把 hash 改成 64 个 0，跑 `checkver -f`，看结果是否回到你提交的值。`checkver -f` 本身证明不了什么——hash 正确时它只是原地重写同值。

## B6 提交

新 manifest 提交信息：`Add <appname>`。提 PR 到公共 bucket 时的标题格式、`/verify` 评论、字段顺序、Excavator 会拒绝纯版本号 PR 的规则，见 `references/bucket-workflows.md`。

---

# §C 维护：体检、修复、与模板同步

## C1 体检（只读，先报告再动手）

```bash
pwsh -NoProfile -File tools/audit.ps1            # 完整：checkver -s + checkhashes + lint + autoupdate + sources
pwsh -NoProfile -File tools/audit.ps1 -Offline   # 秒级：只跑 lint + autoupdate 静态检查
```

没有自家 `audit.ps1` 时用等价组合：`checkver * -s`（过期）、`checkhashes`（hash 不符，会真下载，慢）、lint 类静态检查（用本技能 `scripts/manifest-lint.ps1`）、`checkver`（源是否还在）。

**流程**：跑 → 按检查项分组贴出问题（过时 / hash 不符 / lint / autoupdate / source）→ **列清单问用户要不要修** → 得到明确同意后才改。空段落不写；`warn` 级别放 errors 之后。

## C2 修复（不同问题的修法不可互换）

| 检查项 | 修法 |
|---|---|
| `outdated` | `bin/checkver.ps1 <app> -u`（重写 version/url/hash） |
| `hash` 不符 | `bin/checkhashes.ps1 <app> -Update`，或 `checkver <app> -u -f` |
| hash 缺失 / 为空 | `<skill>/scripts/hashurl.ps1 <url>` 算出来，手工写入 |
| 其他 lint、`autoupdate:mismatch` | 按规则改 manifest |
| `source:*` / checkver 失配 | 上游变了，报告给用户，需人工判断 |

三条铁律（都已实测确认）：

- **同版本下的 hash 错误，`checkver -u` 修不了**——它打印版本发现没变就 `continue`，根本走不到 autoupdate。
- **空 hash 补不回来**——`checkver -u` 会掉进需要 `architecture` 块的分支；`checkhashes -Update` 在没有 `architecture` 块时直接 `Get-Member` 报错。只能用 `hashurl.ps1` 手算。
- **`autoupdate` 里只写 `hash` 不写 `url`，会让 `checkver -u` 把正确 hash 写成 `""` 并以 0 退出**——这是会主动毁数据的那种坑，比空 hash 更危险。

既过期又 hash 不符的，先 `checkver -u`，再对剩下的用 `checkhashes -Update`。

改完逐条复跑该 app 的检查。`checkver -u` 失败（比如正则不再匹配）就停下报告，别绕着改。全部修完再问是否 `formatjson.ps1` 规范化、是否 stage + commit。

## C3 与 BucketTemplate 同步

```powershell
pwsh -NoProfile -File <skill>/scripts/template-drift.ps1 -RepoRoot <bucket>
# 仓库内已有自带版本时也可以用它
pwsh -NoProfile -File .claude/skills/scoop-bucket-sync/scripts/template-drift.ps1
```

报告模板 HEAD 提交（它写明上游当前策略，比如 `ci: use pinned actions`）、缺失/有差异的文件、以及模板没有而本仓库有的文件。**`bucket/`、`deprecated/` 属于本仓库，不算漂移**；`CLAUDE.md`、`README`、`.gitignore`、`docs/`、`.claude/`、`tools/` 也是刻意定制。

分类后再动：固定 vs 浮动的 action 引用、action 版本落后、workflow 结构（决定整个 job 跑不跑的 `if:` 要放在 job 上，不能放在 step 上）、脚手架文件。优先整文件拷贝再补回仓库专属值。验证：`actionlint`、YAML 解析、`gh api repos/<o>/<r>/commits/<tag> --jq .sha` 核对 digest。提交信息：`ci: Sync workflows and tooling with BucketTemplate`，只 stage 工具文件，不 push。

完整规则与「哪些差异必须保留」清单见 `references/bucket-audit-and-sync.md`。

---

# 排错入口

先 `scoop checkup`，再看 `references/troubleshooting.md`（覆盖执行策略、包找不到、hash 缺失、解压失败、NSIS 卡 GUI、下载慢、代理认证、NTFS 要求、长路径、开发者模式、杀软实时扫描、装不上 / 版本冲突、`current` 断链）。诊断顺序永远是从「环境」到「包」到「上游源」，不要一上来就改 manifest。

## scripts / references 一览

| 文件 | 用途 |
|---|---|
| `scripts/fetch-windows-assets.ps1` | 从 GitHub Release API 取版本、URL、sha256（不下载）；本机没 node 时用这个 |
| `scripts/fetch-windows-assets.mjs` | 同上，Node 实现 |
| `scripts/hashurl.ps1` | 给一个或多个 URL 算 sha256（自动剥 `#/...` 片段，用 Scoop UA） |
| `scripts/manifest-lint.ps1` | 离线静态检查：字段、hash 形态、架构配对、autoupdate.url 复现、命名捕获组大小写；`-Strict` 把字段顺序也升级为 error |
| `scripts/template-drift.ps1` | 与 ScoopInstaller/BucketTemplate 比对漂移 |
| `assets/app-name.json.template` | 新 manifest 起点（官方字段顺序） |
| `references/install-and-setup.md` | 安装器全部参数、环境变量、CI、静默、管理员、镜像、代理 |
| `references/cli-reference.md` | 每个命令的完整选项 + 全部 config 键 |
| `references/manifest-reference.md` | manifest 全字段、license、架构、persist、psmodule、shortcuts |
| `references/autoupdate-reference.md` | checkver 策略、autoupdate、hash 提取模式、全部变量、命名捕获组坑 |
| `references/installers-and-extraction.md` | 解压/安装器判定、NSIS 脱困、7z 两段解压、本地复现 |
| `references/bucket-workflows.md` | bucket 创建、模板 CI/Excavator、PR 与提交规范 |
| `references/bucket-audit-and-sync.md` | 体检报告格式、修复矩阵、模板同步细则 |
| `references/troubleshooting.md` | 全部已知故障与修法 |
