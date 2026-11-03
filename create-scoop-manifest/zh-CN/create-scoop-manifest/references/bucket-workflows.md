# bucket 工作流：创建、CI、PR

来源：wiki [Buckets](https://github.com/ScoopInstaller/Scoop/wiki/Buckets)、[Criteria for including apps in the main bucket](https://github.com/ScoopInstaller/Scoop/wiki/Criteria-for-including-apps-in-the-main-bucket)、[CONTRIBUTING](https://github.com/ScoopInstaller/.github/blob/main/.github/CONTRIBUTING.md)、BucketTemplate 仓库。

## 目录

- [bucket 是什么](#bucket-是什么)
- [创建自己的 bucket](#创建自己的-bucket)
- [BucketTemplate 带来的自动化](#buckettemplate-带来的自动化)
- [main bucket 的收录标准](#main-bucket-的收录标准)
- [提交 PR 的完整流程](#提交-pr-的完整流程)
- [PR 标题格式](#pr-标题格式)
- [Excavator 与「不接受纯版本号 PR」](#excavator-与不接受纯版本号-pr)
- [脚本目录与附属文件](#脚本目录与附属文件)
- [发布与收录](#发布与收录)

---

## bucket 是什么

bucket 是一个装着 JSON manifest 的 Git 仓库。可以是 GitHub 仓库，也可以是本地/网络盘上的裸 Git 仓库。

- `main` 随 Scoop 自带，永远是默认搜索源。
- `extras` 放不适合 main 的 GUI / 非开发工具。
- `versions` 放知名包的旧版本。
- 任何人都可以建自己的 bucket，只要把仓库地址告诉别人。

`ScoopDirectory`（<https://rasa.github.io/scoop-directory/>）收录了社区 bucket；给自己的仓库加 GitHub topic `scoop-bucket` 就会被扫到。

---

## 创建自己的 bucket

### 方式一：用模板（推荐）

1. 打开 [ScoopInstaller/BucketTemplate](https://github.com/ScoopInstaller/BucketTemplate)，点 **Use this template**。
2. 起名，按 README 底部的说明改两处占位符（`<username>/<bucketname>`）。
3. 开箱就有 CI、自动更新、issue/PR 处理。

模板带来的东西见下一节。

### 方式二：手工

```powershell
git clone https://github.com/<your-username>/my-bucket
cd my-bucket
# 写第一个 manifest
'{ "version": "1.0", "url": "https://gist.githubusercontent.com/lukesampson/6446238/raw/hello.ps1", "bin": "hello.ps1", "description": "Hello world example", "homepage": "https://example.com", "license": "MIT" }' > bucket/hello.json
# 计算 hash 后填进 hash 字段
git add .
git commit -m "Add hello"
git push
```

目录约定：manifest 放在仓库根的 `bucket/` 下（`Find-BucketDirectory` 检测到 `<bucket>\bucket` 存在时会自动下沉一层）。

### 接入并验证

```powershell
scoop bucket add my-bucket https://github.com/<your-username>/my-bucket
scoop bucket list                    # 应看到 my-bucket
scoop search hello                   # 应列在 'my-bucket bucket:' 下
scoop install hello
hello
```

### 分享

只要把 `scoop bucket add my-bucket <url>` 这一行告诉别人。想让 ScoopDirectory 收录就加 topic。

---

## BucketTemplate 带来的自动化

| 能力 | 作用 |
|---|---|
| **Continuous integration** | 每次提交跑 Scoop 的官方测试，保证格式与可读性（非 YAML 文件强制 CRLF） |
| **Continuous delivery** | 每 4 小时自动把所有 manifest 更新到最新版本（跑 checkver -u） |
| **Issue handlers** | 自动处理 404、hash 校验失败这类常见反馈 |
| **Pull Request handlers** | PR 自动校验：必需字段、hash 验证、CI 测试 |
| **`bin/` 包装器** | `checkver.ps1` / `checkhashes.ps1` / `checkurls.ps1` / `formatjson.ps1` / `missing-checkver.ps1` 是 `$SCOOP_HOME/bin/` 的 4 行转发；`auto-pr.ps1`、`test.ps1`（Pester runner）稍长 |

**`bin/` 里不要自己加文件**。需要新工具就放 `tools/`，让 `bin/` 保持对模板的纯拷贝——否则模板同步时会一直显示漂移。细节见 `bucket-audit-and-sync.md`。

---

## main bucket 的收录标准

进 `main` 的 app 必须：

- 是**广为人知的开发者工具**（GitHub 项目大致要 ≥500 star、≥150 fork）
- 是最新的稳定版
- 是**完整版**，不是试用版
- 安装方式相对标准（版本化的下载 URL，不需要复杂的 pre/post 脚本）
- **非 GUI**

不符合的走 `extras`。只有 32bit 的老包、需要注册 / 付费的走 `nonportable` 或 `versions`。

---

## 提交 PR 的完整流程

### 0. 先开 issue

除了既有 issue 直接认领，任何新改动（包括新增包）都必须先在对应仓库开 issue，写清实现细节和理由。

> 「我们非常不情愿接受没有先建 issue 的随机 PR。」

等维护者确认可以提 PR，再开始写。

### 1. 认领

在 issue 下评论说你在做这件事，避免和别人撞车。如果已有活跃（7 天内）的讨论且有人在改，换一个。

### 2. 分支

- Scoop core：从 **`develop`** 切分支。
- bucket：从默认分支（通常 `master`）切分支。

### 3. 写 manifest 并本地验证

读 [App Manifests](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifests) 与 [Creating an App Manifest](https://github.com/ScoopInstaller/Scoop/wiki/Creating-an-app-manifest)，按字段顺序、4 空格缩进、SPDX license 等规则写。然后：

1. `scoop install bucket\<app>.json` → 装、跑、验功能与持久化、卸载
2. 确认 autoupdate 真的能跑：`.\bin\checkver.ps1 <app> -u`
3. 一个 PR 只改一个 manifest 及其相关文件（变体、`.reg`、`.ps1`）

### 4. 提 PR

标题按下一节规则。body 描述改了什么、为什么。

### 5. `/verify`

在 PR 下加一条评论，内容以 `/verify` 开头，触发自动 manifest 校验器。它会检查必需属性、hash、CI 测试等。

### 6. 等 review

尽快回应提出的问题。互相 review 别人的 PR 是被鼓励的，只要保持友善和建设性。

### Scoop core 额外要求

- 从 `develop` 切分支
- 跑测试，确认没有回归
- 需要时更新测试与文档
- PR 标题遵循 [Conventional Commits](https://www.conventionalcommits.org/)

---

## PR 标题格式

校验正则是 [regex101.com/r/cn45r4/1](https://regex101.com/r/cn45r4/1)。

| 场景 | 格式 | 例 |
|---|---|---|
| 新 manifest | `<app-name>: Add version <version>` | `tailcat: Add version 0.6.0` |
| 更新已有 manifest | `<app-name>(@<version>): <small description>` | `wget@1.21.4: Fix moved urls`<br>`wget: Update to version 1.25.0, remove arm64 version` |
| 同时改多个相关 manifest | `<app-name(*)>: <small description>` | `uutils-(*): Update homepage`<br>`uutils-coreutils(-lean): Fix shims` |
| 维护类改动 | `(chore): <small description>` | `(chore): Resolve redirected GitHub repository URLs in bulk` |

---

## Excavator 与「不接受纯版本号 PR」

公共 bucket 有自动更新机制（`checkver` + `autoupdate`）加一个定时任务（俗称 **Excavator**，通常每 4 小时跑一次）。

因此：

- **只把版本号往上 bump 的 PR 会被拒**。例外极少（例如 GitHub Runner 的 IP 被 Cloudflare 之类屏蔽）。
- 如果日志显示 autoupdate 本身出了问题，那就在 bump 版本的同时把 autoupdate 修好。
- 上游有新版本、但 manifest 没有 autoupdate 配置的，提交更新时**请把 autoupdate 一起加上**。

已知 bucket 的自动更新节奏：

| bucket | 频率 |
|---|---|
| `main` | 每小时 |
| `extras` | 每小时 |
| `versions` | 每天 |
| `java` | 每天 |
| `php` | 每天 |
| `games` | 每天 |

想让自己 bucket 里的包被自动更新：迁到上述 bucket，或自己跑一份 Excavator。

---

## 脚本目录与附属文件

需要 `.reg`、`.ps1` 之类附属脚本时，放在 bucket 仓库的 `scripts/<app-name>/` 下，再由 `pre_install` / `post_install` 复制到安装目录并执行。

范例：Extras bucket 的 [vscode scripts](https://github.com/ScoopInstaller/Extras/tree/master/scripts/vscode)（文件图标、程序关联，含安装与移除两套）、[windows-terminal](https://github.com/ScoopInstaller/Extras/tree/master/scripts/windows-terminal)。

文件关联与图标的注意事项（必须指向 `current` 目录、绝不能指向 shim）见 `troubleshooting.md`。

---

## 发布与收录

- 自己的 bucket：`scoop bucket add <name> <url>` 一行即可分发。
- 想进 ScoopDirectory：仓库加 GitHub topic `scoop-bucket`。
- 想进官方 main / extras：按上面的 main 收录标准，走 PR 流程（先开 issue）。
- 老包：`versions` bucket；需要管理员 / 系统级安装的：`nonportable`。
