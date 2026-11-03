# multi-skill-creator（简体中文版）

创建 agent 技能，并用可复现的评测把技能反复打磨好。**不绑定任何特定 CLI**。

完整说明（为什么这样设计、与上游的差异、支持的 agent 清单）见[仓库根目录的 README](../../README.md)。这里是安装与使用的最小说明。

## 安装

把这个目录（`multi-skill-creator/`）整个放进你的 agent 的技能目录：

| 工具 | 安装位置 |
|---|---|
| Claude Code | `.claude/skills/multi-skill-creator/`（项目级）或 `~/.claude/skills/`（全局） |
| Finch | `.finch/skills/multi-skill-creator/` |
| 通用约定 | `.agents/skills/multi-skill-creator/` |
| 其他 CLI | 见其文档中的技能/命令目录 |

只需要这一个目录。不要同时装英文版以外的副本——两版技能名相同，装两套会互相遮蔽。

## 前置条件

- Python 3.10+
- 一个可非交互调用的 agent CLI（`claude`、`codex`、`gemini`、`cursor-agent`、`opencode`、`finch` 之一），或任何能用命令模板驱动的命令
- 无第三方 Python 依赖；`quick_validate.py` 有 PyYAML 就用，没有就回退到内置解析器

## 它会带你做什么

装上之后，说一句"我想做一个处理 X 的技能"就能启动。技能会先判断你在流程的哪一步（有想法 / 有草案 / 想优化描述），然后往下推：

1. 收窄意图、访谈边界情况
2. 写 `SKILL.md` 草案与测试用例（`evals/evals.json`）
3. 每个用例跑「装技能」和「基线」两次
4. 评分并汇总成 `benchmark.json`（通过率、耗时、token，均值 ± 标准差）
5. 生成本地网页让你逐个看产出、留反馈
6. 按反馈重写，再跑一轮
7. 用 20 条查询自动优化描述，减少该触发却不触发

## 手动跑脚本

所有命令都在**本目录**内执行：

```bash
# 触发评测
python -m scripts.run_eval --eval-set triggers.json --skill-path ../my-skill --agent auto --verbose

# 评测 + 改进循环
python -m scripts.run_loop --eval-set triggers.json --skill-path ../my-skill --agent auto --max-iterations 5 --verbose

# 汇总基准
python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name my-skill

# 人工复查页面（无显示器时加 --static out.html）
python eval-viewer/generate_review.py <workspace>/iteration-1 --skill-name my-skill --benchmark <workspace>/iteration-1/benchmark.json

# 校验与打包
python scripts/quick_validate.py ../my-skill
python -m scripts.package_skill ../my-skill
```

## 用别的 agent

```bash
# 指定预设
--agent codex

# 任意 CLI，prompt 作为最后一个参数
--agent-cmd "my-agent --print {prompt}"

# 任意 CLI，prompt 走 stdin
--agent-cmd "my-agent --print" --agent-transport stdin

# 技能目录不在预设表里
--install-root .myagent/skills
```

各 CLI 的差异、探针技能装到哪里、以及纯文本 CLI 的触发判定为何只能当上界看待，见 [`references/agent-cli.md`](references/agent-cli.md)。

## 许可

Apache License 2.0，见 [LICENSE](LICENSE)。派生自 anthropics/skills 的 `skill-creator`。
