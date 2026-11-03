# 解压、安装器与 NSIS 脱困

来源：`lib/decompress.ps1`（`Invoke-Extraction` / `Expand-*` 的判定逻辑）、`lib/install.ps1`（`Invoke-Installer` / `Invoke-HookScript`）、实测经验。

## 目录

- [Scoop 如何决定解压方式](#scoop-如何决定解压方式)
- [各种包型的处理策略](#各种包型的处理策略)
- [判断一个 exe 里面是什么](#判断一个-exe-里面是什么)
- [#dl.7z 手法](#dl7z-手法)
- [NSIS 静默安装失败的脱困方案](#nsis-静默安装失败的脱困方案)
- [installer.script vs pre_install 怎么选](#installerscript-vs-pre_install-怎么选)
- [引号与作用域三大坑](#引号与作用域三大坑)
- [本地复现测试](#本地复现测试)
- [zip/tar 的 extract_dir](#ziptar-的-extract_dir)

---

## Scoop 如何决定解压方式

`Invoke-Extraction` 对**每个下载的文件名**做一次 `switch -regex`，只看扩展名：

| 文件名匹配 | 走哪个函数 | 条件 |
|---|---|---|
| `\.zip$` | `Expand-7zipArchive` | 装了 7zip helper（默认）或 `use_external_7zip` 且 PATH 有 `7z` |
| `\.zip$` | `Expand-ZipArchive` | 上面都不满足，退回 `Microsoft.PowerShell.Archive\Expand-Archive` |
| `\.msi$` | `Expand-MsiArchive` | `use_lessmsi` 时用 lessmsi，否则 `msiexec /a` |
| `\.exe$` | `Expand-InnoArchive` | **仅当** `manifest.innosetup = true` |
| 其他（由 `Test-7zipRequirement` 判定） | `Expand-7zipArchive` | `.7z`、`.tar`、`.gz`、`.lzma`、`.lzh`、分卷 7z/rar 等 |

三条关键结论：

1. **`.exe` 默认既不解压、也不执行。** `Invoke-Extraction` 只对 `innosetup: true` 的 `.exe` 解包；而 `Invoke-Installer`（`lib/install.ps1`）的第一行判断就是 `if ($installer.file -or $installer.args)`，**没有 `installer` 块时整段跳过**。所以一个裸 `.exe` URL 只会被原样放进 `$dir`，不会被运行——实测验证过：`url` 指向 `where.exe`、不写 `installer`，安装日志里没有出现「Running installer」，`where.exe` 原封不动躺在安装目录，Scoop 直接给它建好了 shim。

   这意味着两种常见写法的真实含义完全不同：

   | 写法 | Scoop 做什么 |
   |---|---|
   | `"url": "...setup.exe"` + 只有 `bin` | **只下载，不执行**。适用于本身就是单个可执行程序的产物（Go/Rust 单文件 exe）。 |
   | `"url": "...setup.exe"` + `installer.file`/`args` | 先执行安装器，再跑 `installer.script` |
   | `"url": "...setup.exe#/dl.7z"` | 存成 `dl.7z` 后按 7z 解压 |

   所以「只发 NSIS 安装器、想装成便携版」时，**不写 `installer` 块是实现不了解包的**——安装器不会被运行，但你也没得到应用文件，`bin` 会指向不存在的文件并在 `create_shims` 阶段报 `Can't shim 'xxx.exe': File doesn't exist`。必须显式用 `#/dl.7z` 或 `pre_install` 里的 7z 来解。

2. **NSIS 不在自动解压白名单里。** electron-builder 的 NSIS 包即使能 7z 解开，Scoop 也不会自动去解。
3. **`.tar.gz` / `.tar.xz` 会二次解包**。`Expand-7zipArchive` 会检测内层 tar 并再解一次，`extract_dir` 在第二次时生效。

`Expand-7zipArchive` 的实际参数：`7z x <file> -o<dest> -xr!*.nsis -y`，有 `extract_dir` 时再加 `-ir!<dir>\*`。所以 `extract_dir` 对 7z 是「只解这一个子目录」而不是「解完再搬」。

---

## 各种包型的处理策略

| 包型 | 推荐写法 | 备注 |
|---|---|---|
| 便携 `.zip` / `.7z` | 直接 `url` + 必要时 `extract_dir` | 首选。用 `7z l` 看有没有根目录 |
| `.tar.gz` | 直接 `url` + `extract_dir` | Scoop 会自动二次解 tar |
| `.msi` | **不写 `msi` 块**，当 zip 处理 | 老写法 `msi.code` / `msi.silent` 已废弃 |
| InnoSetup `.exe` | `"innosetup": true` | Scoop 用 innounp 解，不解打包 |
| WiX / Burn `.exe` | `scoop install dark` 后由 helper 解 | `Expand-DarkArchive` |
| NSIS `.exe`（静默可跑） | 写 `installer.file` + `args: ["/S"]`，交给 Scoop 执行 | 不写 `installer` 块则**根本不会执行** |
| NSIS `.exe`（静默跑不通） | `#/dl.7z` 或 `pre_install` + 7z 两段解压 | 见下文 |
| 单文件 `.exe`（Go/Rust 产物） | 直接 `url` + `#/name.exe` + `bin` | 不需要 `installer`，也不需要解压 |
| 自解压 SFX | `#/dl.7z` | `7z l` 报 `Type = PE` 也常能解 |

MSI 走解压而非安装的好处：不进「应用列表」，不留注册表卸载项，卸载就是删目录。

---

## 判断一个 exe 里面是什么

```powershell
7z l .\setup.exe            # 列出内容
7z l -slt .\setup.exe       # 带类型信息
```

读法：

- 出现 `$PLUGINSDIR\app-64.7z`（或 `app-32.7z`）→ electron-builder / NSIS-3 Unicode 的 wrapper，真正的应用在内层 7z 里。
- 出现 `$PLUGINSDIR\` 里一堆 `.dll` + `System.dll` 之类 → 普通 NSIS。
- 出现 `{app}\...` 路径 → InnoSetup（应该用 `innosetup: true`）。
- 出现 `Binary.*` / `AttachedContainer\` → WiX Burn。
- `Type = PE` 但能列出内嵌 7z 流 → 用 `#/dl.7z` 仍可解。
- `7z l` 报 `Unknown Error` / 完全列不出 → 要么是纯 MSI 包在 exe 壳里，要么是私有格式，换思路。

`7z x -y -o<dir> setup.exe` 手工解一次，看目录结构，比读文档快。

---

## #dl.7z 手法

最省事的通用绕法，不需要写任何脚本：

```json
"url": "https://example.org/app-1.2.3-setup.exe#/dl.7z"
```

Scoop 会把 exe 存成 `dl.7z`，然后按 `.7z` 走 `Expand-7zipArchive`。安装器根本不会被执行，所以不会有 UAC 弹窗、不会写注册表、不会往安装目录外放文件。

代价：如果 exe 真是不透明的安装器（内层没有可用的 7z 流），解出来是垃圾或直接失败。所以先用 `7z l` 确认。

适用于：NSIS wrapper、SFX、以及任何「7z 能列出来」的 exe。

---

## NSIS 静默安装失败的脱困方案

### 现象

manifest 里写了 `"bin": "app.exe"`，`scoop install` 报：

```text
Can't shim 'app.exe': File doesn't exist.
```

或者安装卡住不动、弹出安装向导窗口。

### 原因

electron-builder 的 NSIS 配置是 `oneClick: false`、`perMachine: false`、`allowToChangeInstallationDirectory: true` 时，安装器有交互向导。Scoop 执行 `app-1.2.3-setup.exe /S`，安装器仍在等 GUI 交互，extract 没完成，`$dir` 里当然没有要 `bin` 的那个 exe。

### 解决：7z 两段解压

跳过 `installer` 块，用 `pre_install` 做两段解压，`depends` 拉 `7zip`（Scoop 会用内置 helper）。

```json
{
    "version": "2.4.2",
    "description": "Oh My PPT - Local-first AI presentation workbench",
    "homepage": "https://github.com/arcsin1/oh-my-ppt",
    "license": { "identifier": "Apache-2.0", "url": "https://github.com/arcsin1/oh-my-ppt/blob/main/LICENSE" },
    "url": "https://github.com/arcsin1/oh-my-ppt/releases/download/v2.4.2/oh-my-ppt-2.4.2-win.exe",
    "hash": "bca4930d53e2d2a9c75ede781216c4efa83ba6465a579dc2998f8e397bb5c13d",
    "depends": "7zip",
    "pre_install": [
        "$nsis = Get-Item \"$dir\\$fname\"",
        "$stage = Join-Path $env:TEMP (\"ohmyppt-extract-\" + $PID)",
        "if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }",
        "New-Item -ItemType Directory -Path $stage | Out-Null",
        "Push-Location $stage",
        "& 7z x -y -o\"$stage\" \"$nsis\" '$PLUGINSDIR\\app-64.7z' | Out-Null",
        "& 7z x -y -o\"$dir\" (Join-Path $stage '$PLUGINSDIR\\app-64.7z') | Out-Null",
        "Pop-Location",
        "Remove-Item -Recurse -Force $stage",
        "Remove-Item -Force \"$nsis\""
    ],
    "bin": "ohmyppt.exe",
    "shortcuts": [
        ["ohmyppt.exe", "OhMyPPT", "Oh My PPT - Local-first AI presentation workbench"]
    ],
    "checkver": { "github": "https://github.com/arcsin1/oh-my-ppt", "regex": "v([\\d.]+)" },
    "autoupdate": {
        "url": "https://github.com/arcsin1/oh-my-ppt/releases/download/v$version/oh-my-ppt-$version-win.exe"
    }
}
```

流程：解 NSIS 到临时目录拿到 `$PLUGINSDIR\app-64.7z` → 再把内层 7z 解到 `$dir` → 清理临时目录和原始 exe。

**内层文件名可能随版本变**，想更稳就用搜索而不是硬编码：

```powershell
"$inner = Get-ChildItem -Path $stage -Recurse -Filter 'app-64.7z' | Select-Object -First 1",
"if ($null -eq $inner) { throw 'Inner app archive (app-64.7z) not found inside NSIS payload' }",
"& 7z x -y -o\"$dir\" $inner.FullName | Out-Null"
```

### 适用边界

- ✅ electron-builder NSIS（内层 `app-64.7z` / `app-32.7z`）
- ✅ 其他 NSIS 工具链、外层能被 7z 抽出内嵌 7z 的（把 `$PLUGINSDIR\app-64.7z` 换成实际内层路径）
- ❌ 非 NSIS（MFC、WinRAR SFX、漏写 `innosetup: true` 的 InnoSetup）——先 `7z l` 看结构再定

---

## installer.script vs pre_install 怎么选

两种都能做纯解压安装，但语义不同：

| | `pre_install` + 7z | `installer.script` + 7z |
|---|---|---|
| 执行时机 | 解压阶段之前 | 解压阶段之后、`bin`/shim 之前 |
| Scoop 会不会执行 exe | 不会 | **只要写了 `file` 或 `args` 就会先执行** |
| 写错的风险 | 低 | 高（`file`/`args` 是陷阱） |
| 适用 | 需要先铺好文件，或彻底不走 installer 流程 | 需要在标准安装流程中间插入自定义逻辑 |

`installer.script` 版本（只在没有 `file`/`args` 时才安全）：

```json
"installer": {
    "script": "7z x \"-o$dir\\.cache\" \"$dir\\$fname\" -y | Out-Null; $inner = Get-ChildItem -Path \"$dir\\.cache\" -Recurse -Filter 'app-64.7z' | Select-Object -First 1; if ($null -eq $inner) { throw 'Inner app archive not found' }; 7z x \"-o$dir\" $inner.FullName -y | Out-Null; Remove-Item -Recurse -Force \"$dir\\.cache\", \"$dir\\$fname\""
}
```

**判断规则**：如果目标只是「别执行那个安装器，把文件解出来」，用 `pre_install`。只有确实需要在 Scoop 的安装器阶段插入逻辑时才用 `installer.script`，并且必须确认 `installer` 块里没有 `file` 和 `args`。

---

## 引号与作用域三大坑

### 1. `$PLUGINSDIR` 必须用**单引号**

`$PLUGINSDIR` 是 NSIS 的变量名，不是 PowerShell 变量。双引号会让 PowerShell 把它求值成空字符串，7z 于是找不到路径。

```powershell
"& 7z x -y -o\"$stage\" \"$nsis\" '$PLUGINSDIR\\app-64.7z'                # ✅
"& 7z x -y -o\"$stage\" \"$nsis\" \"$PLUGINSDIR\\app-64.7z\"              # ❌ 路径变成 \app-64.7z
"(Join-Path $stage '$PLUGINSDIR\\app-64.7z')"                             # ✅ 拼接时也只让 $stage 求值
```

### 2. `$dir` / `$fname` 必须用**双引号**

这两个是 Scoop 通过动态作用域注入的 PowerShell 变量。单引号拿不到值。

### 3. `pre_install` 数组的拼接与执行方式

Scoop 的实现（`lib/install.ps1` 的 `Invoke-HookScript`）：

```powershell
Invoke-Command ([scriptblock]::Create($Script -join "`r`n"))
```

含义：

- 数组元素用 `\r\n` 连接成一个 scriptblock。
- 用 `Invoke-Command` 执行，变量靠**动态作用域**从 `install_app` 函数传进来。

推论：本地模拟时必须在外层函数里定义 `$dir` / `$fname`，否则 `Invoke-Command` 拿到的是空值，脚本静默干错事。

另外，`pre_install` 里的 `$dir` 是**带版本号的真实目录**（`apps\<app>\1.2.3`），只有 `post_install` 里 `$dir` 才是 `current`。

---

## 本地复现测试

不上 bucket、不需要真实 `scoop install`，就能验 `pre_install` 逻辑：

```powershell
function Invoke-HookScript {
    param([string]$HookType, [string[]]$Script)
    if ($Script) {
        Invoke-Command ([scriptblock]::Create($Script -join "`r`n"))
    }
}

$dir = 'D:\tmp\apptest\2.4.2'                 # 任意目标目录
$fname = 'oh-my-ppt-2.4.2-win.exe'            # 目标文件名
$manifest = Get-Content 'bucket\oh-my-ppt.json' -Raw | ConvertFrom-Json

# 先把下载到的 exe 放进 $dir
Invoke-HookScript -HookType 'pre_install' -Script $manifest.pre_install

# 验证
Test-Path (Join-Path $dir 'ohmyppt.exe')      # 应为 True
Get-ChildItem $dir                            # 原 exe 应已删除，无中间垃圾
```

这一步过了再去做真实 `scoop install`，能省掉反复装/卸的时间。

---

## zip/tar 的 extract_dir

很多 zip 解出来带一个根目录（`App-1.2.3/`）。不写 `extract_dir` 的话所有文件会被摊到 `$dir` 下，`bin` 路径就错了。

```powershell
7z l .\app.zip | Select-Object -First 20      # 看第一层是不是单一根目录
```

```json
"extract_dir": "App-1.2.3",
"autoupdate": { "url": "...", "extract_dir": "App-$version" }
```

`autoupdate.extract_dir` 也要跟着写，否则下次自动更新后结构对不上。

同理，如果压缩包必须铺到某个子目录里：

```json
"extract_to": "bin"
```
