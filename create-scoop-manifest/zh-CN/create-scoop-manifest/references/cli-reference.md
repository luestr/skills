# CLI 与配置参考

来源：Scoop core `libexec/*.ps1` 的 Usage/Help 块、`scoop-config.ps1` 的完整设置清单、`buckets.json`。

## 目录

- [命令总表](#命令总表)
- [逐命令选项](#逐命令选项)
- [配置项全集](#配置项全集)
- [aria2 配置](#aria2-配置)
- [已知 bucket](#已知-bucket)
- [退出码](#退出码)

---

## 命令总表

`scoop help` 的输出（28 个命令）：

```text
alias        Manage scoop aliases
bucket       Manage Scoop buckets
cache        Show or clear the download cache
cat          Show content of specified manifest
checkup      Check for potential problems
cleanup      Cleanup apps by removing old versions
config       Get or set configuration values
create       Create a custom app manifest
depends      List dependencies for an app, in the order they'll be installed
download     Download apps in the cache folder and verify hashes
export       Exports installed apps, buckets (and optionally configs) in JSON format
help         Show help for a command
hold         Hold an app to disable updates
home         Opens the app homepage
import       Imports apps, buckets and configs from a Scoopfile in JSON format
info         Display information about an app
install      Install apps
list         List installed apps
prefix       Returns the path to the specified app
reset        Reset an app to resolve conflicts
search       Search available apps
shim         Manipulate Scoop shims
status       Show status and check for new app versions
unhold       Unhold an app to enable updates
uninstall    Uninstall an app
update       Update apps, or Scoop itself
virustotal   Look for app's hash or url on virustotal.com
which        Locate a shim/executable (similar to 'which' on Linux)
```

---

## 逐命令选项

### `scoop install <app> [options]`

```text
scoop install git                                        # 从本地 buckets
scoop install gh@2.7.0                                   # 指定版本（先查 sqlite 缓存 → git 历史 → autoupdate 生成）
scoop install https://.../runat.json                      # 从 URL 的 manifest
scoop install https://.../neovim.json@0.9.0               # URL + 版本
scoop install .\path\to\app.json                          # 本地 manifest
scoop install .\path\to\app.json@version                  # 本地 manifest + 版本
```

| 选项 | 含义 |
|---|---|
| `-g, --global` | 全局安装（需管理员） |
| `-i, --independent` | 不自动安装依赖 |
| `-k, --no-cache` | 不使用下载缓存 |
| `-s, --skip-hash-check` | 跳过 hash 校验（慎用） |
| `-u, --no-update-scoop` | Scoop 过期时不先自更新 |
| `-a, --arch <32bit\|64bit\|arm64>` | 指定架构（manifest 支持时） |

版本解析顺序：sqlite 精确匹配 → bucket 的 git 历史（`use_git_history` 默认 `$true`）→ `autoupdate` 现场生成 → 都失败则 abort。

### `scoop update [<app>] [options]`

```text
scoop update              # 更新 Scoop 自身 + 所有 bucket 的 manifest
scoop update curl         # 更新单个 app
scoop update *            # 更新全部已装 app
```

| 选项 | 含义 |
|---|---|
| `-f, --force` | 没有新版本也强制更新 |
| `-g, --global` | 更新全局安装的 app |
| `-i, --independent` | 不自动装依赖 |
| `-k, --no-cache` | 不用缓存 |
| `-s, --skip-hash-check` | 跳过 hash 校验 |
| `-q, --quiet` | 少输出 |
| `-a, --all` | 等价 `*` |

副作用：`scoop update` 每 3 小时会被自动触发一次（在 install/update/download/virustotal 时）。旧版本不删除，留着供 `reset`，直到 `scoop cleanup`。

### `scoop uninstall <app> [options]`

| 选项 | 含义 |
|---|---|
| `-g, --global` | 卸载全局 app |
| `-p, --purge` | 同时删除 persist 数据 |

### `scoop cleanup <app> [options]`

| 选项 | 含义 |
|---|---|
| `-a, --all` | 清理全部（等价 `*`） |
| `-g, --global` | 清理全局 app 的旧版本 |
| `-k, --cache` | 顺带删过期下载缓存 |

### `scoop search <query>`

- 无 query：列出所有可用 app。
- `use_sqlite_cache` 开启：query 对 app 名、二进制名、快捷方式做**部分匹配**。
- 未开启：query 被当作**正则**，只匹配 app 名与二进制名。

### `scoop info <app>`

`-v, --verbose` 显示完整路径与 URL。这是唯一能看到「某 app 所有已安装版本」的命令（`scoop list` 只显示最新版本）。

### `scoop status [options]`

| 选项 | 含义 |
|---|---|
| `-l, --local` | 只检查本地已装 app，不联��检查 Scoop 与 bucket 更新 |

对比基准是**本地 manifest**，所以先 `scoop update` 才能看到真相。

### `scoop reset <app>`

重新生成该 app 的 shims、按 manifest 更新环境变量，从而在多个已装版本间切换优先级。支持 `*` 或 `-a/--all`。**不能切到未安装的版本。**

### `scoop hold <apps>` / `scoop unhold <apps>`

`hold` 后该 app 不参与 `scoop update *`。`-g` 作用于全局 app。`scoop hold scoop` 会把 `hold_update_until` 设为一天后。

### `scoop download <app> [options]`

只下载到 cache 并校验 hash，不安装。

| 选项 | 含义 |
|---|---|
| `-f, --force` | 覆盖缓存 |
| `-s, --skip-hash-check` | 跳过校验 |
| `-u, --no-update-scoop` | 不先自更新 |
| `-a, --arch <arch>` | 指定架构 |

支持 `app@version`、URL manifest、本地 manifest 路径。

### `scoop bucket <sub>`

```text
scoop bucket add <name> [<repo>]    # 已知 bucket 可省略 repo
scoop bucket list                   # Name / Source / Updated / Manifests
scoop bucket known                  # 全部已知 bucket 名
scoop bucket rm <name>
```

`add` 的硬依赖是 `git`；会先 `git ls-remote` 校验仓库可达，再 clone 到 `buckets\<name>`。同一远端地址已有 bucket 时会拒绝重复添加。

### `scoop cache show|rm [app...]`

`rm *` 或 `rm -a/--all` 清空全部缓存。

### `scoop config [rm] <name> [value]`

无参打印全部配置对象；有 name 无 value 打印单项；有 value 写入；`rm` 删除。完整键表见下一节。

### `scoop export [-c|--config]`

输出 JSON（apps + buckets，`-c` 时含配置）到 stdout，通常重定向成 scoopfile.json。

### `scoop import <path-or-url>`

从 scoopfile 恢复 apps、buckets 与配置。

### `scoop alias add|rm|list`

```powershell
scoop alias add rm 'scoop uninstall $args[0]' 'Uninstall an app'
scoop alias add upgrade 'scoop update *' 'Update all apps, just like brew or apt'
scoop alias list -v
scoop alias rm <name>
```

### `scoop shim <sub>`

```text
scoop shim add <shim_name> <command_path> [[--|--%] <args>...]
scoop shim rm <shim_name> [<shim_name>...]      # 注意：可能删掉 manifest 生成的 shim
scoop shim list [<regex_pattern>...]
scoop shim info <shim_name>
scoop shim alter <shim_name>                    # 换目标源
```

`-g/--global` 操作全局 shim。第一个 `--` 或 `--%` 之后的参数原样传给 shim，所以要把 `-g` 传给被包装程序必须放在分隔符之后。

### 其余

| 命令 | 说明 |
|---|---|
| `scoop which <cmd>` | 找到 shim/可执行文件的真实路径 |
| `scoop prefix <app>` | 返回 app 安装目录 |
| `scoop home <app>` | 打开 homepage |
| `scoop depends <app>` | 按安装顺序列出依赖 |
| `scoop cat <app>` | 打印 manifest；设了 `cat_style` 会用 `bat` 美化 |
| `scoop create <url>` | 交互式生成自定义 manifest |
| `scoop checkup` | 诊断：main bucket、长路径、开发者模式、7zip/innounp/dark、NTFS、Defender 排除项 |
| `scoop virustotal [*\|app...] [-a] [-s]` | 按 hash/URL 查 VirusTotal；`-s` 无记录时提交 URL 扫描 |

---

## 配置项全集

文件位置 `~/.config/scoop/config.json`（`$cfgpath`）。

### 路径与仓库

| 键 | 值 | 说明 |
|---|---|---|
| `root_path` | 路径 | 用户级根目录，默认 `$Env:UserProfile\scoop` |
| `global_path` | 路径 | 全局根目录，默认 `$Env:ProgramData\scoop` |
| `cache_path` | 路径 | 下载缓存，默认 `<root>\cache` |
| `scoop_repo` | URL | Scoop 源码仓库，默认 `https://github.com/ScoopInstaller/Scoop` |
| `scoop_branch` | `master`\|`develop` | 切到 `develop` 可提前拿到未发布功能 |

### 行为开关

| 键 | 默认 | 说明 |
|---|---|---|
| `use_external_7zip` | `$false` | 用 PATH 上的 `7z` 而非内置 helper；开启但找不到 7z 会直接 abort |
| `use_lessmsi` | `$false` | 用 lessmsi 而非 `msiexec /a` 解 MSI |
| `use_sqlite_cache` | — | 用 SQLite 缓存，加速 `search` / `shim` |
| `use_git_history` | `$true` | 装 `app@version` 时先在 bucket git 历史里找 |
| `no_junction` | `$false` | 不用 `current` 别名，shims/快捷方式直接指向版本目录 |
| `default_architecture` | 系统决定 | `64bit`\|`32bit`\|`arm64` |
| `force_update` | `$false` | 强制更新到 bucket 里的版本 |
| `debug` | `$false` | 输出详细日志（排错第一步） |
| `show_manifest` | `$false` | 安装前显示 manifest 并请求确认 |
| `show_update_log` | — | 不在 `scoop update` 时显示变更 commit |
| `autostash_on_conflict` | `$false` | 更新冲突时自动 stash，而不是中止 |
| `ignore_running_processes` | `$false` | `$true` 时目标进程在跑也只警告不中止（影响 reset/uninstall/update） |
| `update_nightly` | `$false` | nightly 版本一天后自动更新；否则需 `--force` |
| `use_isolated_path` | — | `$true` → 用 `SCOOP_PATH` 存 app 的 PATH；也可给任意变量名 |
| `shim` | — | shim 实现：`kiennq`\|`scoopcs`\|`71` |
| `cat_style` | — | 非空时 `scoop cat` 用 `bat` 渲染，值即 `bat --style` |

### 网络与凭据

| 键 | 说明 |
|---|---|
| `proxy` | `[username:password@]host:port`。`currentuser` 代替 `username:password` 用当前用户凭据；`default` 代替 `host:port` 用系统代理；空/未设等价 `default`；`none` 绕过系统代理直连 |
| `gh_token` | GitHub API token。checkver 等操作必须有它才能免限流、访问私有仓库 |
| `virustotal_api_key` | VirusTotal API key（64 位小写 hex） |
| `private_hosts` | 需额外认证的私有主机数组，元素含 `match` 与 `headers` |

### 其他

| 键 | 说明 |
|---|---|
| `hold_update_until` | 暂停 Scoop 自更新到指定日期；`scoop hold scoop` 设为一天后。接受 `YYYY-MM-DD`、`YYYY/MM/DD` 或任何 `[System.DateTime]::Parse()` 能解析的形式 |

---

## aria2 配置

装了 `aria2` 后默认启用。`scoop install` / `scoop update` 时会打印告警，`scoop config aria2-warning-enabled false` 可关。

| 键 | 默认 | 说明 |
|---|---|---|
| `aria2-enabled` | `$true` | 用 aria2c 下载 |
| `aria2-warning-enabled` | `$true` | 显示 aria2 告警 |
| `aria2-fallback-enabled` | `$true` | aria2 失败时回退默认下载器 |
| `aria2-retry-wait` | `2` | 重试间隔秒数 |
| `aria2-split` | `5` | 连接数（`-s`） |
| `aria2-max-connection-per-server` | `5` | 单服务器最大连接（`-x`） |
| `aria2-min-split-size` | `5M` | 分片大小（`-k`） |
| `aria2-options` | 空 | 额外 aria2 选项数组 |

CI / 弱网调试时先 `aria2-enabled false`，能把「下载问题」和「包问题」区分开。

---

## 已知 bucket

`buckets.json` 中 `scoop bucket known` 返回的全部条目：

| 名称 | 仓库 |
|---|---|
| `main` | https://github.com/ScoopInstaller/Main |
| `extras` | https://github.com/ScoopInstaller/Extras |
| `versions` | https://github.com/ScoopInstaller/Versions |
| `nirsoft` | https://github.com/ScoopInstaller/Nirsoft |
| `sysinternals` | https://github.com/ScoopInstaller/Sysinternals |
| `php` | https://github.com/ScoopInstaller/PHP |
| `nerd-fonts` | https://github.com/matthewjberger/scoop-nerd-fonts |
| `nonportable` | https://github.com/ScoopInstaller/Nonportable |
| `java` | https://github.com/ScoopInstaller/Java |
| `games` | https://github.com/ScoopInstaller/Games |

其他社区 bucket 走 [Scoop Directory](https://rasa.github.io/scoop-directory/)；给自己的 bucket 加 GitHub topic `scoop-bucket` 就会被收录。

---

## 退出码

- 大部分命令成功 `0`，参数错误 `1`。
- `scoop virustotal` 是多位合成码：`0` 成功、`1` 参数错误、`2` 有包被判危险、`4` 查询异常、`8` manifest 找不到、`16` 未配置 API key；`2|4|8` 可叠加（如 `6`）。
- `scoop bucket add`：`0` 成功、`1` 失败、`2` 已存在 / 重复远端。
- 脚本里判断结果只看 `$LASTEXITCODE`，不要匹配输出文本。
