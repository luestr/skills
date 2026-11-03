# Manifest 字段参考

来源：wiki [App-Manifests](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifests)、CONTRIBUTING 的字段顺序与风格规则、`lib/manifest.ps1` 的实际行为。

## 目录

- [最小可用 manifest](#最小可用-manifest)
- [必填字段](#必填字段)
- [可选字段](#可选字段)
- [architecture 块](#architecture-块)
- [url 与 # 片段](#url-与--片段)
- [hash](#hash)
- [installer / uninstaller](#installer--uninstaller)
- [persist](#persist)
- [bin 与 shim 别名](#bin-与-shim-别名)
- [shortcuts](#shortcuts)
- [psmodule](#psmodule)
- [checkver / autoupdate](#checkver--autoupdate)
- [depends / suggest](#depends--suggest)
- [废弃与未文档化字段](#废弃与未文档化字段)
- [风格硬规则](#风格硬规则)

---

## 最小可用 manifest

```json
{
    "version": "1.0",
    "url": "https://github.com/lukesampson/cowsay-psh/archive/master.zip",
    "extract_dir": "cowsay-psh-master",
    "bin": "cowsay.ps1"
}
```

`version` + `url` + `bin` 就够装。但真正进 bucket 的 manifest 还要 `description`、`homepage`、`license`、`hash`。

---

## 必填字段

### `version`
要装的版本号，字符串。tag 带 `v` 前缀时要剥掉（`v1.2.3` → `"1.2.3"`）。

### `description`
单行简短描述。**如果和文件名相同，不要在描述里重复程序名。** 技术上非必需，但所有新增/更新的 manifest 都必须有。

### `homepage`
程序主页。用 `"checkver": "github"` 时**必须是 GitHub 仓库 URL**（否则 checkver 报「expects the homepage to be a github repository」）；主页不是 GitHub 时改用 `"checkver": { "github": "<repo url>" }` 或显式 `url`。

### `license`
字符串或对象。

- 已知许可证用 [SPDX 标识符](https://spdx.org/licenses)：`"MIT"`、`"Apache-2.0"`、`"GPL-3.0-or-later"`。
- 非 SPDX 时用这几个词之一：`Freeware`（永久免费）、`Proprietary`（付费）、`Public Domain`、`Shareware`（先试后付）、`Unknown`（无法判断）。
- 不同文件有不同许可证：逗号分隔。整体双许可（dual license）：管道符分隔。开源 + 闭源混合时**先列非开源许可证**。
- 无法穷举时允许在末尾加 `,...`。
- 对象形式 `{ "identifier": "Apache-2.0", "url": "https://.../LICENSE" }` 能在 bucket 页面链到上游 LICENSE 文件。

```json
"license": "MIT"
"license": { "identifier": "Proprietary", "url": "https://example.com/eula" }
"license": { "identifier": "Freeware" }
```

---

## 可选字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `##` | 字符串 / 数组 | 注释。用于说明「为什么没有 checkver」这类判断，方便审计时解释异常 |
| `architecture` | 对象 | 见下节 |
| `autoupdate` | 对象 | 见 `autoupdate-reference.md` |
| `bin` | 字符串 / 数组 | 见下节 |
| `checkver` | 字符串 / 对象 | 见 `autoupdate-reference.md` |
| `depends` | 字符串 / 数组 | 运行时依赖，自动安装 |
| `suggest` | 对象 | 建议性可选依赖，见下节 |
| `env_add_path` | 字符串 / 数组 | 加进用户 PATH（`--global` 时加系统 PATH）。**必须是安装目录内的相对路径** |
| `env_set` | 对象 | 设置环境变量（`--global` 时设系统级） |
| `extract_dir` | 字符串 | 只解压压缩包里的这个子目录 |
| `extract_to` | 字符串 | 把内容解压到指定子目录 |
| `hash` | 字符串 / 数组 | 与 `url` 一一对应 |
| `innosetup` | `true` | 声明这是 InnoSetup 安装器，Scoop 会用 innounp 解 |
| `installer` | 对象 | 见下节 |
| `notes` | 字符串 / 数组 | 安装完成后显示的消息 |
| `persist` | 字符串 / 数组 | 见下节 |
| `post_install` / `pre_install` / `pre_uninstall` / `post_uninstall` | 字符串 / 数组 | PowerShell 片段，见「脚本钩子」 |
| `psmodule` | 对象 | 作为 PowerShell 模块安装 |
| `shortcuts` | 数组的数组 | 开始菜单快捷方式 |
| `uninstaller` | 对象 | 同 `installer`，卸载时执行 |

### 脚本钩子

`pre_install` / `post_install` / `pre_uninstall` / `post_uninstall` / `installer.script` / `uninstaller.script` 共用一套变量。下表是**实测**结果（Scoop v0.6.0，用一个 `pre_install` 脚本把所有变量 dump 出来得到），不是照抄 wiki：

| 变量 | 实测值示例 | 说明 |
|---|---|---|
| `$app` | `probe2` | app 名（manifest 文件名） |
| `$version` | `2.0.0` | 正在安装的版本 |
| `$cmd` | `install` / `update` / `uninstall` | 当前子命令 |
| `$architecture` | `64bit` / `32bit` / `arm64` | 目标架构 |
| `$global` | `$false` / `$true` | 是否全局 |
| `$manifest` | 反序列化对象 | 完整 manifest |
| `$scoopConfig` | `@{root_path=...; scoop_branch=master; ...}` | Scoop 配置对象 |
| `$dir` | `...\apps\probe2\2.0.0` | 安装目录（作用域差异见下） |
| `$original_dir` | `...\apps\probe2\2.0.0` | 真实版本目录 |
| `$persist_dir` | `...\persist\probe2` | 持久化目录 |
| `$bucketsdir` | `...\scoop\buckets` | |
| `$cachedir` | `...\scoop\cache` | |
| `$globaldir` | `...\ScoopGlobal`（即 `%ProgramData%\scoop` 或其覆盖值） | |
| `$scoopdir` | `...\ScoopUser`（即 `%USERPROFILE%\scoop` 或其覆盖值） | |
| `$fname` | `probe2.zip` | 最后下载的文件名 |
| `$url` | 本次使用的 manifest 来源 | |
| `$bucket` | **未定义**（本地 manifest 时） | 从 bucket 安装时才有值 |

**wiki 上有但你拿不到的三个变量**（实测均为 `$null`）：

| wiki 写法 | 实际 |
|---|---|
| `$cfg` | 不存在；配置对象叫 **`$scoopConfig`** |
| `$cfgpath` | 不存在 |
| `$modulesdir`、`$oldscoopdir` | 不存在 |

要拿配置项，用 `$scoopConfig.root_path` 或直接调 `get_config <KEY>`（`get_config` 在 hook 里可用）。要拿模块目录，用 `modulesdir $global`（这是**函数**，不是变量）。

**`$dir` 的作用域差异（实测确认）**：

- `pre_install`、`installer.script`、`pre_uninstall`、`uninstaller.script`、`post_uninstall` → `$dir` 是**带版本号的真实目录**（`...\apps\<app>\2.0.0`）。
- `post_install` → `$dir` 已被 `link_current` 换成 **`current` 联结**（`...\apps\<app>\current`）。

实测输出：`post_install` 里 `$dir = ...\postdir\current`，而 `$original_dir = ...\postdir\1.0.0`。所以需要真实路径时用 `$original_dir`，别在 `post_install` 里用 `$dir` 做路径比较。

`appdir` 是**函数**（`appdir <app> [<global>]`），用来取另一个 scoop app 的目录：

```powershell
"post_install": "if (Test-Path \"$(appdir otherapp)\\current\\otherapp.exe\") { ... }"
```

`pre_install` 数组会被 `\r\n` 拼成一个 scriptblock，再用 `Invoke-Command` 执行；变量靠 PowerShell 动态作用域从 `install_app` 传进来。所以本地模拟测试时必须在外层函数里先定义 `$dir` / `$fname`，否则拿到空值——细节见 `installers-and-extraction.md`。

---

## architecture 块

`architecture` 下可放 `64bit` / `arm64` / `32bit`，每个子对象可含：`bin`、`checkver`、`extract_dir`、`hash`、`installer`、`pre_install`、`post_install`、`shortcuts`、`uninstaller`、`url`、`msi`（已废弃）。

**规则**：只有「只提供 32bit 下载」的应用才允许省略 `architecture`；其他所有情况 `architecture` 都是必需的（这是 bucket 的强制风格）。只有单一全架构二进制时用顶层 `url`/`hash`。

```json
{
    "architecture": {
        "64bit": { "url": "...x64.zip", "hash": "..." },
        "arm64": { "url": "...arm64.zip", "hash": "..." },
        "32bit": { "url": "...x86.zip", "hash": "..." }
    }
}
```

---

## url 与 # 片段

`url` 可以是字符串或数组（数组时 `hash` 也必须是等长数组）。支持 HTTP / HTTPS / FTP。

**`#` 片段**改下载后的本地文件名，必须写成 `#/` 开头：

| 片段 | 效果 | 用途 |
|---|---|---|
| `#/name.exe` | 下载后重命名为 `name.exe` | 文件名不稳定 |
| `#/dl.7z` | 保存为 7z 并自动解压 | **绕开会改注册表 / 需提权的安装器** |
| `#/dl.exe` | 重命名为 exe 后交给 `installer.script` | 多层嵌套包 |

```json
"url": "https://example.org/program.exe#/dl.7z"
```

Scoop 会下载 `program.exe` 但存成 `dl.7z` 再解压——这是跳过 EXE 安装器副作用的标准手法。

---

## hash

字符串或数组，与 `url` 一一对应。默认 SHA256；其他算法加前缀：`sha512:`、`sha1:`、`md5:`。小写，无反斜杠。

```json
"hash": "54fabf3778685680cf97ba9fd4e84ea54f5c3ac72c54e740f9e9a12fd7dce480"
"hash": [ "<hash-of-url1>", "<hash-of-url2>" ]
```

**空 hash 是陷阱**：安装时只警告 `No hash in manifest` 然后继续**不校验**；`checkver -u` 也补不回来（空 hash 会掉进需要 `architecture` 块的分支）。新 manifest 必须播种真实 hash。

反过来的坑更隐蔽：**`autoupdate` 里只写了 `hash` 没写 `url`，会让 `checkver -u` 把已有的正确 hash 写成 `""`**。实测过，退出码还是 0。所以 `autoupdate` 里出现 `hash` 就必须同时有 `url`。

算 hash 的正确工具是本技能的 `scripts/hashurl.ps1`——它会剥掉 `#/...` 片段（那是 Scoop 指令，不是 HTTP URL 的一部分），用 Scoop 的 UA，输出小写 SHA256。

---

## installer / uninstaller

```json
"installer": {
    "file": "setup.exe",
    "script": "…PowerShell 片段…",
    "args": ["/S", "/D=$dir"],
    "keep": "true"
}
```

| 键 | 说明 |
|---|---|
| `file` | 安装器文件名。默认是最后下载的那个文件。`uninstaller` 里**必须**显式指定 |
| `script` | 用一段 PowerShell 代替 `file` 执行安装 |
| `args` | 传给安装器的参数数组 |
| `keep` | `"true"` 时保留安装器（例如卸载时要用）。在 `uninstaller` 里会被忽略 |

**`file`/`args` 与 `script` 的先后顺序是坑**：只要写了 `file` 或 `args`，Scoop 的 `Invoke-Installer` 就会**先**启动那个二进制（`/S` 静默，不带参数则弹 GUI），**再**跑 `script` 钩子。想做纯解压安装，只能留 `script`，把 `file`/`args` 都去掉——没有 `file`/`args` 时它会跳过执行，但仍然调用 `Invoke-HookScript`。

`uninstaller` 在 `scoop uninstall` 和 `scoop update` 时都会跑。

---

## persist

把文件/目录重定向到 `~/scoop/persist/<app>/`，更新时保留。用目录联接或硬链接实现。

```json
"persist": "config.ini"
"persist": ["conf", "data"]
"persist": [
    "keeps_its_name",
    ["original_name", "new_name_inside_the_data_dir"]
]
```

- 安装时已有持久数据会被复制进数据目录并建立链接。
- 卸载默认**保留**数据；`scoop uninstall -p <app>` 才清。
- 便携化优先：能给 `persist` 就别让程序把配置写到 `%APPDATA%`。

---

## bin 与 shim 别名

```json
"bin": "app.exe"
"bin": ["app.exe", "helper.exe"]
"bin": ["busybox.exe", "sh", "bash"]          // 别名 + 无参
"bin": [["program.exe", "alias", "--args"]]   // 别名 + 参数
```

**单个别名 shim 必须再套一层数组**：`"bin": [["program.exe", "alias"]]`。否则会被当成两个独立 shim。

---

## shortcuts

数组，每项是一个 2~4 元组：

1. 目标文件路径（必填，相对安装目录）
2. 快捷方式名（必填，支持子目录 `<AppsSubDir>\\<AppShortcut>`）
3. 启动参数（可选）
4. 图标路径（可选）

```json
"shortcuts": [
    ["HanaAgent.exe", "HanaAgent", "--fast", "assets\\icon.ico"]
]
```

CLI 程序不需要 shortcuts；GUI 程序且不接受命令行参数时，不需要进 `bin`。

---

## psmodule

```json
"psmodule": { "name": "NameOfTheModule" }
```

`name` 必需，且必须与解压目录里 `.psd1` 的名字一致，PowerShell 才会自动识别。装好后链接到 `~/scoop/modules`（该目录自动进 `$env:PSModulePath`），实际是两层 junction：`modules\Name` → `apps\name\current` → `apps\name\<version>`。

---

## checkver / autoupdate

见 `autoupdate-reference.md`。一句话：`checkver` 找版本，`autoupdate` 用 `$version` / `$match*` / `$majorVersion` 等变量重建 `url`、`hash`、`extract_dir` 等。

---

## depends / suggest

```json
"depends": ["7zip", "innounp"]
"suggest": { "JDK": ["extras/oraclejdk", "openjdk"] }
```

- `depends` 是**运行时**依赖，安装时自动装最新版；`scoop status` 只对缺失的运行时依赖告警。
- 安装期依赖（如解压需要的 7zip/innounp）由 `url` 的文件扩展名自动判断，不需要写进 `depends`。
- `suggest` 是提示，不是依赖。如果该分组下任意一个 app 已安装，整组视为已满足、不再提示。
- 更新时依赖只在**完全缺失**时才装，版本偏旧不处理。

**不要给现代 NSIS 包加 VC++ 运行时 `depends`**——它自带，加了反而在精简系统上装不上。

---

## 废弃与未文档化字段

| 字段 | 状态 |
|---|---|
| `msi` | **废弃**。不要再写。新做法是把 `.msi` 当 zip 解压（不写这个字段即可）。旧字段结构：`code`（产品 GUID，必需）、`silent` |
| `_comment` | 废弃，用 `##` |
| `cookie` | 未文档化，只在个别第三方 bucket 出现 |

---

## 风格硬规则

来自 CONTRIBUTING，PR 会被自动检查：

1. **字段按这个顺序**（存在才写）：
   `version` → `description` → `homepage` → `license` → `notes` → `depends` → `suggest` → `architecture`（内含 `url`、`hash`）→ `extract_dir` → `extract_to` → `pre_install` → `installer` → `post_install` → `env_add_path` → `env_set` → `bin` → `shortcuts` → `persist` → `pre_uninstall` → `uninstaller` → `post_uninstall` → `checkver` → `autoupdate`
2. **缩进 4 空格**（tab width 4）。
3. `license` 必须是合法 SPDX 标识符（或上文列出的非 SPDX 词）。
4. **优先便携化**（用 `persist`）。
5. CLI 程序不需要 `shortcuts`；GUI 程序且无命令行参数时不需要 `bin`。
6. **数组只有一个元素时写成字符串**。
7. 只提供 32bit 下载时可省略 `architecture`，其他情况必需。
8. 更新后要确认 autoupdate 真的能跑通。
9. 一个 PR 只改一个 manifest 及其相关文件（变体、`.reg`、`.ps1` 等）。

参考现成范例：[main bucket](https://github.com/ScoopInstaller/Main/tree/master/bucket)、官方模板 [app-name.json.template](https://github.com/ScoopInstaller/BucketTemplate/blob/master/bucket/app-name.json.template)（本技能 `assets/app-name.json.template` 是它的等价副本）。
