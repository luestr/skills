# 安装与配置

来源：<https://github.com/ScoopInstaller/Install#readme>、`install.ps1` 参数表、wiki Quick-Start / Global-Installs / Using-Scoop-behind-a-proxy / Uninstalling-Scoop。

## 目录

- [前置条件](#前置条件)
- [标准安装](#标准安装)
- [安装器全部参数](#安装器全部参数)
- [自定义目录的两种写法](#自定义目录的两种写法)
- [管理员安装](#管理员安装)
- [代理环境安装](#代理环境安装)
- [CI 环境](#ci-环境)
- [静默安装与退出码](#静默安装与退出码)
- [目录布局与环境变量](#目录布局与环境变量)
- [全局安装](#全局安装)
- [卸载](#卸载)
- [安装期故障](#安装期故障)

---

## 前置条件

| 条件 | 要求 | 检查 / 修复 |
|---|---|---|
| PowerShell | 5.1 或更高（Win10 / Server 2016+ 自带即满足） | `$PSVersionTable.PSVersion` |
| Language Mode | 必须是 `FullLanguage` | `$ExecutionContext.SessionState.LanguageMode` |
| Execution Policy | `RemoteSigned` / `Unrestricted` / `ByPass` 之一 | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

Win7/8、Server 2008/2012 需要装 [WMF 5.1](https://aka.ms/wmf5download) 或并排安装受支持的新版 PowerShell。更老的系统不受支持。

Language Mode 为 `ConstrainedLanguage` 时必须先在组策略 / AppLocker 层放行，脚本层改不了。

## 标准安装

在**非管理员**的 PowerShell 里：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
# 等价写法
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

默认位置 `C:\Users\<用户名>\scoop`。

`get.scoop.sh` 是一个跳转器，把 `install.ps1` 取下来执行。需要固定版本 / 审计内容时，先落盘再跑：

```powershell
irm get.scoop.sh -outfile 'install.ps1'
.\install.ps1
```

## 安装器全部参数

`install.ps1` 的完整 param 块：

```powershell
param(
    [String] $ScoopDir,                                          # 用户级 Scoop 根目录
    [String] $ScoopGlobalDir,                                    # 全局安装根目录
    [String] $ScoopCacheDir,                                     # 下载缓存目录
    [Switch] $NoProxy,                                           # 安装期忽略系统代理
    [Uri] $Proxy,                                                # 安装期使用的代理
    [System.Management.Automation.PSCredential] $ProxyCredential,# 代理凭据
    [Switch] $ProxyUseDefaultCredentials,                        # 用当前用户 Windows 凭据走代理
    [Switch] $RunAsAdmin                                         # 允许在管理员控制台安装
)
```

| 参数 | 作用 | 备注 |
|---|---|---|
| `-ScoopDir` | 用户级根目录 | 等价于设 `$env:SCOOP` |
| `-ScoopGlobalDir` | 全局（`--global`）根目录 | 等价于设 `$env:SCOOP_GLOBAL`，需 NTFS |
| `-ScoopCacheDir` | 下载缓存目录 | 默认 `<ScoopDir>\cache` |
| `-NoProxy` | 安装期绕过系统代理 | 只在安装期生效，不写进 Scoop 配置 |
| `-Proxy <Uri>` | 安装期代理 | 例 `-Proxy 'http://127.0.0.1:7890'` |
| `-ProxyCredential <PSCredential>` | 代理的用户名/密码 | 与 `-ProxyUseDefaultCredentials` 二选一 |
| `-ProxyUseDefaultCredentials` | 用当前登录用户的凭据认证代理 | |
| `-RunAsAdmin` | 允许管理员控制台安装 | 默认禁用，见下文 |

## 自定义目录的两种写法

**写法一：参数（推荐，一次到位）**

```powershell
.\install.ps1 -ScoopDir 'D:\Applications\Scoop' -ScoopGlobalDir 'F:\GlobalScoopApps' -NoProxy
```

**写法二：环境变量（legacy）**

```powershell
$env:SCOOP='D:\Applications\Scoop'
$env:SCOOP_GLOBAL='F:\GlobalScoopApps'
[Environment]::SetEnvironmentVariable('SCOOP_GLOBAL', $env:SCOOP_GLOBAL, 'Machine')
irm get.scoop.sh | iex
```

注意 `SCOOP_GLOBAL` 要写 Machine 域；`SCOOP` 写 User 域即可。两者都必须在**运行安装脚本的那个会话**里可见。

装好之后还可以再改：`scoop config root_path <path>` / `scoop config global_path <path>`（见 `cli-reference.md`）。但**已安装的 app 不会跟着搬**，改路径只影响后续操作，实际迁移要手工搬目录 + 重装 shim。

## 管理员安装

出于安全考虑，管理员控制台默认**不能**装 Scoop。要在提权会话里装，必须显式 `-RunAsAdmin`：

```powershell
irm get.scoop.sh -outfile 'install.ps1'
.\install.ps1 -RunAsAdmin [-OtherParameters ...]

# 一行版
iex "& {$(irm get.scoop.sh)} -RunAsAdmin"
```

即便如此，日常管理仍然建议回到普通用户会话。「要不要管理员」和「要不要全局安装」是两件事：管理员装 Scoop ≠ 全局 app，全局 app 靠 `scoop install <app> --global`。

## 代理环境安装

三种粒度，按需选：

```powershell
# 1) 只给安装脚本一个代理
iex "& {$(irm get.scoop.sh -Proxy 'http://<ip:port>')} -Proxy 'http://<ip:port>'}"

# 2) 用环境变量，本次会话内所有请求走代理
$env:HTTP_PROXY='http://<ip:port>'
$env:HTTPS_PROXY='http://<ip:port>'
irm get.scoop.sh | iex

# 3) 需要认证时用 .NET 默认代理（仅当前 PowerShell 会话有效）
[net.webrequest]::defaultwebproxy = new-object net.webproxy "http://proxy.example.org:8080"
[net.webrequest]::defaultwebproxy.credentials = [net.credentialcache]::defaultcredentials
# 或
[net.webrequest]::defaultwebproxy.credentials = new-object net.networkcredential 'username', 'password'
```

装完之后用 `scoop config proxy` 长期配置，见 `cli-reference.md` 的 proxy 一节与 `troubleshooting.md` 的 `bucket add` 代理坑。

## CI 环境

GitHub Actions：

```yaml
- name: Install Scoop
  shell: pwsh
  run: irm get.scoop.sh | iex
```

CI 里 `$env:CI` 没设时，`iex` 形式不会 `exit`，安装失败也不会让流水线失败。要么显式传退出码，要么设 `$env:CI`：

```yaml
- name: Install Scoop
  shell: pwsh
  run: |
    irm get.scoop.sh | iex
    exit $LASTEXITCODE
```

常见 CI 加固：`$env:SCOOP` 指到工作区缓存目录、`scoop config aria2-enabled false`（CI 里 aria2 收益不大）、`scoop install --no-update-scoop` 省掉每次自更新。

## 静默安装与退出码

```powershell
irm get.scoop.sh | iex *> $null        # 全部输出丢弃
irm get.scoop.sh | iex *> install.log  # 落到日志
$LASTEXITCODE                          # 0 = 成功
```

`install.ps1` 内部把失败转成 `$Global:LASTEXITCODE`（在 `iex` 场景下 `exit` 会关掉交互会话，所以只用 `LASTEXITCODE`）。判断成功只看这个值，别去匹配输出文本。

## 目录布局与环境变量

```text
%USERPROFILE%\scoop                 用户级根目录（%SCOOP% 可覆盖）
  apps\                             已安装应用，每个 app 一个目录
    <app>\<version>\                真实版本目录
    <app>\current\                  目录联接 → 当前版本
    scoop\                          Scoop 自身
  buckets\                          各 bucket 的 git clone
  cache\                            下载缓存（%SCOOP_CACHE% / cache_path 可覆盖）
  persist\                          持久化数据（%SCOOP%\persist\<app>）
  shims\                            加入 PATH 的 shim 目录
  modules\                          PowerShell 模块（psmodule 安装，自动进 PSModulePath）
%ProgramData%\scoop                 全局根目录（%SCOOP_GLOBAL% 可覆盖）
%USERPROFILE%\.config\scoop\config.json   配置文件
```

要求：**Scoop 目录必须位于 NTFS 卷**。`scoop checkup` 会用 `DriveInfo.DriveFormat` 检查，FAT32/exFAT 会直接报错。

### 配置文件位置的三个候选（按优先级）

`lib/core.ps1` 的实际逻辑：

1. **便携模式**：如果 Scoop 装在 `<root>\apps\scoop\current`，且 `<root>\config.json` 存在，就用它。这把整个 root 变成可搬移的便携配置。
2. **XDG**：`$env:XDG_CONFIG_HOME\scoop\config.json`（设了这个环境变量时才生效）。
3. **默认**：`%USERPROFILE%\.config\scoop\config.json`。

所以看到配置「改了不生效」时，先确认 `$env:XDG_CONFIG_HOME` 有没有把路径引到别处，再看 root 下有没有 `config.json`。

优先级顺序同理适用于根目录：`$env:SCOOP` → `root_path` 配置 → Scoop 自身所在的 root → `%USERPROFILE%\scoop`；全局目录：`$env:SCOOP_GLOBAL` → `global_path` → `%ProgramData%\scoop`；缓存：`$env:SCOOP_CACHE` → `cache_path` → `<root>\cache`。

注意 `SCOOP_CACHE` 官方标注为**实验性未充分测试**：多用户共享同一缓存目录可能有并发写冲突。

历史路径：极老版本装在 `%USERPROFILE%\AppData\Local\scoop`。脚本里曾有 `$oldscoopdir` 之类的变量，但**当前版本的 hook 作用域里并不存在**（实测为 `$null`），别在 manifest 里依赖它。

## 全局安装

```powershell
scoop install sudo
sudo scoop install git --global      # 长写法
sudo scoop install git -g            # 短写法
```

- 装到 `%ProgramData%\scoop`，改系统环境变量，需要管理员权限 → 所以配 `sudo`。
- 第一次全局安装后要**重启系统**，本地 system 账户才能看到新的环境变量。
- 卸载 / 更新 / 清理都要带 `-g`：`sudo scoop uninstall git -g`、`sudo scoop update git -g`、`sudo scoop cleanup * -g`。

## 卸载

```powershell
scoop uninstall scoop     # 会二次确认，输入 y
```

这会删掉 `~/scoop/persist`（持久化数据一起没）。

安装目录被手动删坏了想重装：

```powershell
del .\scoop -Force        # 在 $HOME 下执行
irm get.scoop.sh | iex
```

只想清掉某个 app 的持久化数据：`scoop uninstall -p <app>`。

## 安装期故障

| 现象 | 原因 | 处理 |
|---|---|---|
| `iex` 一闪而过、什么都没装上 | ExecutionPolicy 不是允许值 | 设 `RemoteSigned` |
| `无法加载文件 ... 因为在此系统上禁止运行脚本` | 同上 | 同上 |
| `ConstrainedLanguage` 相关报错 | Language Mode 不对 | 组策略放行 `FullLanguage` |
| 杀软报 `get.scoop.sh` 有毒 | PowerShell 5.1 + 启发式误报 | 用 PowerShell 7 安装；或加排除路径 |
| 管理员会话里报 security 提示 | 默认禁止管理员安装 | 加 `-RunAsAdmin` |
| 安装在 FAT32/exFAT 上，后续操作报错 | 非 NTFS | 换卷，或改 `SCOOP` / `root_path` |
| 公司网络下 `irm get.scoop.sh` 超时 | 代理 | 见上文代理安装 |
| 装完 `scoop` 命令找不到 | PATH 未刷新 | 重开终端；shims 目录应在 PATH |
| 全局装的 app 对 SYSTEM 不可见 | 环境变量未对 SYSTEM 生效 | 重启一次 |

`Add-MpPreference -ExclusionPath "$($env:programdata)\scoop", "$($env:scoop)"` 可把两个根目录排除实时扫描（需管理员），撤销用 `Remove-MpPreference -ExclusionPath ...`。
