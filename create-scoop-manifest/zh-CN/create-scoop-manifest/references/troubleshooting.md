# 故障排查

诊断顺序永远是：**环境 → 包 → 上游源**。先 `scoop checkup`，再按症状查表。不要一上来就改 manifest。

## 目录

- [checkup 覆盖了什么](#checkup-覆盖了什么)
- [安装 / 启动类](#安装--启动类)
- [找不到包 / 版本问题](#找不到包--版本问题)
- [下载类](#下载类)
- [解压 / 安装器类](#解压--安装器类)
- [hash 类](#hash-类)
- [checkver / autoupdate 类](#checkver--autoupdate-类)
- [路径 / 链接 / 关联类](#路径--链接--关联类)
- [性能与安全软件](#性能与安全软件)
- [命令与环境怪癖](#命令与环境怪癖)

---

## checkup 覆盖了什么

`scoop checkup` 会检查（部分项需管理员）：

| 项 | 失败后果 |
|---|---|
| Windows Defender 排除项 | 解压/安装极慢、CPU 打满，需管理员才检测 |
| `main` bucket 存在 | 装什么都没搜到 |
| 长路径支持 | 深目录解压失败 |
| Windows 开发者模式 | junction 相关异常 |
| 7zip helper（或 `use_external_7zip`） | 大多数包解不开 |
| innounp | InnoSetup 包解不开 |
| dark | WiX 安装器解不开 |
| `$globaldir` 所在卷为 NTFS | 全局安装失败 |
| `$scoopdir` 所在卷为 NTFS | Scoop 本身工作不正常 |

输出 `No problems identified!` 才说明环境层没事。分开看 `$issues`（问题）和 `$defenderIssues`（仅是性能问题）。

---

## 安装 / 启动类

| 现象 | 原因 | 处理 |
|---|---|---|
| `无法加载文件 ... 禁止运行脚本` | ExecutionPolicy | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `iex` 一闪而过什么都没装 | ExecutionPolicy / LanguageMode | 设策略；检查 `$ExecutionContext.SessionState.LanguageMode` 为 `FullLanguage` |
| `scoop` 命令找不到 | PATH 未刷新 | 重开终端；`scoop which scoop` 定位 |
| 管理员会话里装报安全错误 | 默认禁止管理员安装 | `-RunAsAdmin` |
| 装完重启后命令才生效（全局） | 系统环境变量对 SYSTEM 需重启 | 重启一次 |
| `scoop install` 装到一半失败 | 环境（7zip/innounp/dark 缺）或网络 | 先 `scoop checkup`，再 `scoop install 7zip innounp dark` |
| 老版本冲突 / 装了两个版本行为不对 | 多版本共存需要显式切换 | `scoop reset <app>@<version>`；`scoop list` 只显示最新版，用 `scoop info <app>` 看全部 |
| 升级后配置丢了 | 程序把配置写在版本目录里 | manifest 该用 `persist`；临时可从旧版本目录拷回 |
| 卸载后残留 | `persist` 数据默认保留 | `scoop uninstall -p <app>` |

---

## 找不到包 / 版本问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `Couldn't find manifest for 'x'` | 没有对应 bucket | `scoop bucket add extras`（或对应 bucket）；`scoop search x` |
| `scoop search` 结果和预期不符 | sqlite 缓存开启时是部分匹配，未开启时 query 是正则 | 换关键词；或 `scoop config use_sqlite_cache true` |
| `scoop install x@1.2.3` 说找不到版本 | 该版本不在 git 历史里，且 autoupdate 生成失败 | 检查 `use_git_history`；手工确认 manfiest 有 `autoupdate`；必要时从 versions bucket 找 |
| `scoop status` 显示的过时信息不对 | 本地 bucket 没更新 | 先 `scoop update`；`scoop status` 比的是本地 manifest |
| 刚推的 manifest 搜不到 | bucket 没更新 | `scoop update`；确认 bucket 已 `scoop bucket add` |

---

## 下载类

| 现象 | 原因 | 处理 |
|---|---|---|
| 下载极慢 | 没走代理 / 没启用 aria2 / CDN 慢 | `scoop install aria2`；`scoop config proxy ...` |
| aria2 导致失败 | aria2 与某些服务器不兼容 | `scoop config aria2-enabled false`，或用 `aria2-fallback-enabled true`（默认已开） |
| `scoop update` 时出现 aria2 告警 | 默认行为 | `scoop config aria2-warning-enabled false` |
| `scoop bucket add` 走不通代理 | scoop 把 `currentuser@host:port` 直接塞给 git，格式不兼容 | 临时改成 git 格式：`scoop config proxy ':@proxy.example.org:8080'` → `scoop bucket add extras` → 改回 `scoop config proxy 'currentuser@proxy.example.org:8080'` |
| 代理密码含 `@` 或 `:` | 分隔符冲突 | 用 `\` 转义：`scoop config proxy 'username:p\@ssword@proxy.example.org:8080'` |
| 想绕过系统代理 | | `scoop config rm proxy`，或 `scoop config proxy none` |
| 私有仓库 401 | 缺 token / 缺 private_hosts | `scoop config gh_token <token>`；`private_hosts` 配 `match` + `headers` |
| 下载了但装在别处 / 报 `Invoke-WebRequest` 异常 | URL 里带了 `#/...` 片段 | 片段是 Scoop 指令不是 HTTP 的一部分；用 `scripts/hashurl.ps1` 算 hash 时会自动剥掉 |

---

## 解压 / 安装器类

| 现象 | 原因 | 处理 |
|---|---|---|
| `Can't shim 'x.exe': File doesn't exist` | 安装器没真正解开（NSIS 卡 GUI 最常见） | 见 `installers-and-extraction.md` 的 NSIS 脱困方案 |
| `Failed to extract files from ...` | 7z 不支持该格式，或 helper 缺失 | 看 `7zip.log`；`scoop install 7zip`；确认不是 exe 被当 zip 处理 |
| InnoSetup 包解出来是空的 | 漏写 `"innosetup": true` | 补上 |
| WiX / Burn 包失败 | 缺 dark | `scoop install dark` 或 `wixtoolset` |
| MSI 装出来带着卸载项、不愿这样 | 写了废弃的 `msi` 块 | 删掉 `msi` 块，Scoop 会把 msi 当 zip 解 |
| zip 解出来文件全摊在根上、`bin` 找不到 | 缺 `extract_dir` | `7z l` 看根目录名，补 `extract_dir`（autoupdate 里也要补） |
| `7z l` 报 `Type = PE` 就以为不可解 | 误判 | 同一个 listing 里往往有内嵌 7z 流；用 `#/dl.7z` 试 |
| 解压后多了个奇怪的 `.nsis` 目录 | 7z 默认排除规则 | `Expand-7zipArchive` 已带 `-xr!*.nsis`；手工解压时自己加 |
| 安装时弹 UAC / 安装向导 | `.exe` 被当安装器执行 | 用 `#/dl.7z` 或 `pre_install` + 7z |
| `installer.script` 跑了但安装器也跑了 | `installer` 块里写了 `file` 或 `args` | 删掉 `file`/`args`，只留 `script` |

---

## hash 类

| 现象 | 原因 | 处理 |
|---|---|---|
| `No hash in manifest` 警告 | manifest 没有 hash | 用 `scripts/hashurl.ps1` 算并写入（绝不能留空） |
| 装了但没校验 | 空 hash 只警告不阻断 | 同上；或临时 `-s` 明确跳过（慎用） |
| `Hash check failed` | manifest hash 错 / 上游换包 / CDN 返回错误页 | `checkhashes -Update`；或 `checkver -u -f`；核实 URL 是否还指向同一个产物 |
| `checkhashes -Update` 填不上空 hash | 已知缺陷：`Get-Member` 报错，值不变 | 手工算：`scripts/hashurl.ps1 <url>` |
| `URLS and hashes count mismatch` | url 数组与 hash 数组长度不等 | 补齐长度 |
| `checkver -f` 说成功但 hash 是空的 | `autoupdate.url` 缺失，Scoop 无处下载 | 补一个能复现静态 url 的 `autoupdate.url` |
| 给落地页算 hash，每次都不一样 | 落地页本身在变 | 改为对真正的产物 URL 算/host（源模式 D） |

---

## checkver / autoupdate 类

| 现象 | 原因 | 处理 |
|---|---|---|
| `expects the homepage to be a github repository` | `"checkver": "github"` 但 `homepage` 不是仓库 | 改 homepage，或写成 `"checkver": { "github": "<repo>" }` |
| checkver 永远匹配不上 | 上游页面改版 / regex 过期 | `scoop config debug true` 看抓到的内容，重写 regex |
| checkver 取到的版本号是错的 token | 第一个无名组不是版本 | 让版本成为唯一无名组，或命名成 `version` |
| `$matchXxx` 变量为空 | 命名组名大小写被 `ToTitleCase` 改了 | 组名只用单个小写单词（`build` 而非 `buildId`） |
| autoupdate 写出的 url 404 | 静态 url 里写了 `$version`，或模板拼错 | 静态 url 用字面版本；`autoupdate.url` 才用变量 |
| `checkver -u` 不修当前版本的 hash | 版本没变就 `continue` | 用 `checkhashes -Update` 或 `checkver -u -f` |
| 频繁 403 / rate limit | GitHub API 未认证 | `scoop config gh_token <token>` |
| 预发布版被忽略却想用它 | GitHub 策略 | 改用显式 `url` + `regex` 而不是 `"github"` |
| 大批量更新时 hash 全空 | 一批里个别 manifest 的 `autoupdate.url` 缺 | 补全后单跑；不要靠 `mode: download` 兜底掩盖问题 |

---

## 路径 / 链接 / 关联类

### `current` 断链

`apps\<app>\current` 是**目录联接（junction）**，指向当前版本目录。为什么不用 symlink：创建 symlink 需要管理员权限，junction 不需要。

断链表现：`scoop install`/`reset` 后 app 目录里的 `current` 指向不存在的版本。处理：`scoop reset <app>` 重建；仍坏则 `scoop uninstall <app>` 后重装。

不想用 junction：`scoop config no_junction true`（代价是 shims 和快捷方式会绑死到具体版本目录，更新后需重新生成）。

### 文件关联 / Open With 图标

规则只有一条：**指向 `apps\<app>\current\<exe>`，绝不指向 shims，也绝不指向版本目录。**

- 指向版本目录（`...\apps\mpv\0.32.0\mpv.exe`）→ 一更新就失效。
- 指向 shim（`...\scoop\shims\mpv.exe`）→ Open With 菜单里显示成无名块 + 未知图标，多个 shim 之间无法区分，关联的文件全部被传染，有时 shim 启动程序后自己还不退出。

操作路径：右键 → `Open With` → `Choose another app` → `Browse...` → 选 `current` 下的 exe。

**已经误加 shim 了怎么办**：Windows 不允许再为同一个 basename 添加正确路径。必须卸载提供该 shim 的包 → 用任意文件触发一次「打开方式」让 Windows 清掉过期条目 → 重装 → 再添加正确路径。或者手工改注册表。

已知限制：可执行文件名不稳定的程序（如 GIMP 的 `bin/gimp-2.10.exe`）跨更新无法保持关联。

### 长路径 / 深目录

`checkup` 会查长路径支持。没开启时深层 `node_modules`、长资源名解压会失败。开启方式（管理员 + 组策略/注册表 `LongPathsEnabled`），或缩短 `SCOOP` 根路径。

---

## 性能与安全软件

| 现象 | 原因 | 处理 |
|---|---|---|
| 安装时 CPU 打满、文件访问被拒 | 杀软实时扫描正在解压的文件 | 加排除路径 |
| `get.scoop.sh` 被杀软判毒 | PowerShell 5.1 的启发式误报 | 用 PowerShell 7 安装 |
| 装完运行被杀软隔离 | 同上 | 加排除 + 上报误报 |

```powershell
# 需管理员
Add-MpPreference -ExclusionPath "$($env:programdata)\scoop", "$($env:scoop)"
# 撤销
Remove-MpPreference -ExclusionPath "$($env:programdata)\scoop", "$($env:scoop)"
```

`checkup` 在管理员会话下会检测这两条排除是否已设。

---

## 命令与环境怪癖

| 现象 | 原因 | 处理 |
|---|---|---|
| `Get-FileHash` 不存在 | 从 pwsh 会话里启了 `powershell`，`PSModulePath` 继承了 PS7 | 统一用 `pwsh -NoProfile` |
| bash 里 `cd` 后脚本找不到文件 | 工作目录不对 | git 用 `git -C <path>`；pwsh 用 `pwsh -NoProfile -Command "cd '...'; ..."` |
| 在 bash/zsh 里想用 scoop | Scoop 装了 sh 版本的 shim | 可以直接用；不要跨 shell 混用路径分隔符 |
| `scoop` 输出里带颜色码影响解析 | 终端 ANSI | 用 `$LASTEXITCODE` 判断，不要匹配输出文本 |
| CI 里安装失败但流水线是绿的 | `iex` 不 `exit` | `exit $LASTEXITCODE`，或设 `$env:CI` |
| `scoop update` 报冲突 | 本地改过 bucket 仓库 | `scoop config autostash_on_conflict true`，或手动 `git -C <bucket> stash` |
| 目标进程在跑导致 reset/uninstall/update 中止 | 默认行为 | 关掉程序，或 `scoop config ignore_running_processes true`（仅警告继续） |

---

## 排错顺序备忘

1. `scoop checkup` —— 环境层有没有洞。
2. `scoop config debug true` —— 打开详细输出，看它到底做了什么。
3. 把「下载」和「安装」分开验：`scoop download <app>` 只验网络与 hash；过了说明问题在解压/安装器。
4. `scoop install <app> -k` —— 绕过缓存，排除缓存污染。
5. `scoop install <app> -s` —— 跳过 hash，区分「hash 错」和「文件错」。
6. 手工 `7z l` / `7z x` 目标包 —— 排除 Scoop 层，确认包本身可用。
7. 最后才怀疑 manifest，并按 `manifest-reference.md` 的字段规则逐条核。
