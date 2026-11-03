# bucket 体检与模板同步

来源：`scoop-audit` 与 `scoop-bucket-sync` 两个版本的实操规则、ScoopInstaller/BucketTemplate 的实际结构、`bin/` 包装器的真实内容。

## 目录

- [体检（只读）](#体检只读)
- [报告格式](#报告格式)
- [修复矩阵](#修复矩阵)
- [体检后收尾](#体检后收尾)
- [模板漂移检测](#模板漂移检测)
- [哪些差异不是漂移](#哪些差异不是漂移)
- [漂移分类与处理](#漂移分类与处理)
- [同步后的验证](#同步后的验证)

---

## 体检（只读）

一条命令跑完所有检查，输出一张表：

```powershell
pwsh -NoProfile -File tools/audit.ps1                 # 完整（会下载，慢）
pwsh -NoProfile -File tools/audit.ps1 -Offline        # 只跑 lint + checkautoupdate
pwsh -NoProfile -File tools/audit.ps1 <app>           # 只查一个 app（修完复验用）
```

它内部组合了：

| 检查 | 命令 | 说明 |
|---|---|---|
| 过期 | `checkver * -s` | 只列 outdated，不写回 |
| hash 不符 | `checkhashes` | **会下载每个 url**，几分钟量级 |
| schema + 规则 | `tools/lint.ps1` | 字段、hash 形态、风格 |
| autoupdate 一致性 | `tools/checkautoupdate.ps1` | autoupdate.url 能否复现静态 url |
| 源可达性 | `tools/checksources.ps1` | 上游是否还在 |

没有这套脚本时用等价组合：`checkver * -s` + `checkhashes` + 本技能的 `scripts/manifest-lint.ps1`（离线字段/hash/autoupdate 检查）。

**不要**把底层脚本一个个单独跑再自己加分析——报告以统一表格为准，否则容易漏项或重复劳动。

**必须用 `pwsh`，不要用 `powershell`**：从 pwsh 会话里启的 Windows PowerShell 会继承 PS7 的 `PSModulePath`，PS7 的 `Microsoft.PowerShell.Utility` 会遮住 5.1 的同名模块，`Get-FileHash` 直接不存在。

无 checkver 的 app（因上游没有可跟踪版本，`##` 里写明理由的）是设计如此，不算问题；这类 app 唯一的更新信号就是 hash 变化。

---

## 报告格式

按「检查项」分组，保留脚本原始措辞，空段落省略。

```markdown
## Bucket Health Report

### Outdated
| App | Change |
|-----|--------|
| feishu | 7.20.0 -> 7.21.5 |

### Hash mismatches
| App | Detail |
|-----|--------|
| uu | Mismatch found |

### Lint / autoupdate / sources
| App | Check | Level | Detail |
|-----|-------|-------|--------|
| adobe-creative-cloud-cleaner-tool | lint:hash-missing | error | top level: a url has no hash |
```

`warn` / `autoupdate:skip` 属于信息级，列在 errors 之后。脚本输出 `audit: no problems found` 时，直接说「没问题」然后结束，不要硬找问题。

---

## 修复矩阵

**修法不可互换**，对错会决定 manifest 是被修好还是被悄悄毁掉。

| 检查项 | 修法 | 备注 |
|---|---|---|
| `outdated` | `bin/checkver.ps1 <app> -u` | 重写 version / url / hash |
| `hash` 不符 | `bin/checkhashes.ps1 <app> -Update`，或 `checkver <app> -u -f` | 后者更彻底 |
| `lint:hash-missing` / 空 hash | `scripts/hashurl.ps1 <url>` 算出后手工写入 | 见下一节 |
| 其他 `lint:*` | 按 `manifest-reference.md` 的规则改 | 字段顺序、缩进、SPDX、数组单元素写字符串等 |
| `autoupdate:mismatch` | 编辑 `autoupdate`，让模板能复现静态 `url` | 最常见是静态 url 里混进了 `$version` 或版本号写错 |
| `source:*` / checkver 失配 | 报告给用户，需人工判断上游改版 | 不要瞎猜新正则 |

### 三条必须记住的边界

1. **同版本下的 hash 错误，`checkver -u` 修不了。**
   `checkver.ps1` 发现版本没变就打印版本然后 `continue`，根本走不到 autoupdate 那一步。

2. **空 hash 走的是另一条代码路径，容易踩空。**
   `checkhashes.ps1 -Update` 的分支条件是 `if ($current.manifest.url -and $current.manifest.hash)`——空字符串是 falsy，于是掉进 `architecture` 分支，第一句是：

   ```powershell
   $platforms = ($current.manifest.architecture | Get-Member -MemberType NoteProperty).Name
   ```

   如果 manifest 根本没有 `architecture` 块（顶层 `url`/`hash` 的单架构包很常见），在 `$null` 上取 `Get-Member` 直接报错，hash 保持原样。所以「空 hash + 无 architecture 块」这一组合下 `checkhashes -Update` 帮不上忙，只能用 `hashurl.ps1` 算出来手写。

   有 `architecture` 块时空 hash 能进到写回逻辑，但每段要写几个是按旧 hash 的 `.Count` 推的（空字符串 `.Count` 为 1），多架构清单容易错位，仍需人工核对结果。

   `URLS and hashes count mismatch` 是另一个错误：`url` 数组和 `hash` 数组长度不等，修长度。

3. **既过期又 hash 不符时，顺序是**：先 `checkver -u`，再对仍然不对的用 `checkhashes -Update`。

---

## 体检后收尾

1. 逐条修复，**每改一个就贴出该步输出**。
2. 每改完一个 app，复跑该 app 的检查：`pwsh -NoProfile -File tools/audit.ps1 <app>`。
3. `checkver -u` 失败（例如正则不再匹配）时**停下报告**，说清需要人工介入，不要绕道改。
4. 全部修完再问用户：要不要跑 `.\bin\formatjson.ps1` 统一格式？要不要 stage + commit 变更文件？
5. 提交只 stage 本次真正改动过的路径，不要顺手 `git add .`——工作区里常有无关的进行中改动。

---

## 模板漂移检测

```powershell
pwsh -NoProfile -File .claude/skills/scoop-bucket-sync/scripts/template-drift.ps1
# 或用本技能自带版本（参数化，不依赖仓库内路径）
pwsh -NoProfile -File <skill>/scripts/template-drift.ps1 -RepoRoot 'C:\path\to\bucket'
```

行为：

1. 在临时目录（默认 `%TEMP%\opencode\scoop-template`）刷新一份 `ScoopInstaller/BucketTemplate` 的浅克隆；
2. 打印模板 HEAD 的 `git log --oneline -1`；
3. 列出模板有而本仓库**缺失**或**内容不同**的文件；
4. 列出本仓库有而模板**没有**的文件（`Extra`）；
5. 对每个不同文件输出 unified diff。

只比较 **git 已跟踪**的文件，所以 `repomix-output.xml` 这种未跟踪的临时产物不会进报告。`bucket/` 与 `deprecated/` 被排除——它们是本仓库的 manifest，本来就不该和模板一致。

**读模板 HEAD 的提交标题**：它往往直接说明上游当前策略（例如 `ci: use pinned actions`），解释了为什么某个 diff 会出现。不读这一行，你会把策略变更当成噪音。

工具脚本请用 PowerShell 写。Scoop 的 Pester 风格测试要求**所有非 YAML 文件是 CRLF**，而 bash 脚本带 CRLF 会静默出错（drift 过滤器失配、`bucket/` 行泄漏），一个 `.sh` helper 无法同时满足两边。

---

## 哪些差异不是漂移

这些是本仓库刻意的定制，**不要「修」**：

| 差异 | 为什么属于本仓库 |
|---|---|
| `bin/auto-pr.ps1` 里写死了 `<owner>/<bucket>`（而不是占位符） | 默认分支可能不是 `main`；这是唯一需要回填仓库专属值的地方 |
| `Scoop-Bucket.Tests.ps1` 传 `-BucketPath $PSScriptRoot` | scoop core 的 `test/Import-Bucket-Tests.ps1` 用同名同默认值声明该参数，兼容 |
| `.gitignore`、`README.md` | bucket 专属内容 |
| 没有 `bucket/app-name.json.template` | manifest 创建由 `create-scoop-manifest` 技能的创作线覆盖 |
| 没有 `deprecated/.gitkeep` | 该目录里有真实 manifest |
| 多出 `docs/`、`CLAUDE.md`、`.claude/`、`tools/` | 仓库本地资产；`tools/` 放本仓库自己的维护脚本，`bin/` 保持纯模板拷贝 |
| 多出 `repomix-output.xml` | 已 gitignore；未跟踪文件不参与比较 |
| `deprecated/scripts/` 不出现 | 随 `deprecated/` 一起被排除 |

判定标准：一个差异只有在**承载了仓库专属价值**或**守住了模板无法为本仓库捕获的失败**时，才配留成一行。否则就采用模板版本。

反例：曾考虑给 Excavator 加一道「禁止 `"hash": ""`」的守卫，被否掉了——`bin/test.ps1` 里的 schema 测试已经会因为空 hash 失败，这个漂移买不到任何东西。

`bin/` 里永远不要新增文件；新 helper 一律进 `tools/`。

---

## 漂移分类与处理

先分类再动手，因为便宜项会掩盖真正重要的那项。

### 1. Pinned vs floating action 引用

digest 或 tag（带 `# vX.Y.Z` 注释）是上游策略。`@main` 今天能用，将来会静默坏掉。**跟上游：改回 pin。**

### 2. Action 版本落后

只 bump `uses:` 那一行，同时保持尾部版本注释准确。注释说 v7.0.1 而 digest 属于 v6.0.2 是典型的复制粘贴事故——`gh api repos/<o>/<r>/commits/<tag> --jq .sha` 一验就露。

### 3. Workflow 结构

决定**整个 job 跑不跑**的 `if:` 必须放在 job 上，不能放在 step 上：step 级条件仍然会为每个匹配 `on:` 的事件启动一台 `windows-latest` runner。上游正是基于这个原因把 `issue_comment` 处理器合进了 `pull_request.yml`；一个独立 workflow 文件 + step 级守卫，虽然行为看起来一样，也是漂移。

### 4. 脚手架

issue template 的 config、`.yaml` schema 提示、模板 JSON 之类。便宜，整份拷贝。

### 处理原则

- **优先整文件拷贝**，不要手工 merge：
  ```powershell
  Copy-Item <template>\.github\workflows\x.yml .github\workflows\x.yml -Force
  ```
- 拷贝后**回填仓库专属值**（目前只有 `bin/auto-pr.ps1`）。
- 上游删掉、内容已合并进别处的 workflow 文件，直接删除。
- 包装器（`checkver.ps1`、`checkhashes.ps1`、`checkurls.ps1`、`formatjson.ps1`、`missing-checkver.ps1`）有差异时，**拷贝模板文件**而不是编辑它。

---

## 同步后的验证

```bash
actionlint .github/workflows/*.yml
for f in .github/workflows/*.yml .github/ISSUE_TEMPLATE/config.yml; do
  yq eval '.' "$f" >/dev/null || echo "BAD $f"
done
gh api repos/<owner>/<repo>/commits/<tag> --jq .sha   # 必须等于你 pin 的 digest
```

再跑一次 `template-drift.ps1`，确认只剩上面「哪些差异不是漂移」清单里的项。

### 提交

```text
ci: Sync workflows and tooling with BucketTemplate
```

body 逐条列出每个行为变更及其原因。按名字 stage 工具路径（`git add -- .github/... bin/auto-pr.ps1`）——这棵树里经常有 `CLAUDE.md`、`.claude/skills/*`、`bucket/*.json` 的无关进行中改动，那些绝不能被 stage 或回滚。

**只 commit，不 push。**

### 职责边界

- manifest 健康 → 体检线（本文上半部分）
- 创建 manifest → 本技能 §B（创作线）
- 工具链与 workflow → 本节
