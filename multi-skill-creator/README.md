# multi-skill-creator

一个**与工具无关**的技能创建器：帮你从零做一个 agent 技能，然后用可复现的评测反复把它打磨好。

派生自 [anthropics/skills](https://github.com/anthropics/skills) 的 `skill-creator`（Apache-2.0），但做了两处关键改造：

- **不再绑定 Claude**。原先所有 `claude -p` 的调用被抽成一层适配器，可以驱动 Claude Code、Codex、Gemini CLI、Cursor、OpenCode、Finch，或任何你自己的 agent CLI——包括一个只接受命令模板的自建工具。
- **双语独立可用**。中文版与英文版各自是完整、可单独安装的技能，不互相引用。

## 语言版本

| 语言 | 目录 | 技能名 | 元数据 |
|---|---|---|---|
| 简体中文（主开发语言） | [`zh-CN/multi-skill-creator/`](zh-CN/multi-skill-creator/) | `multi-skill-creator` | `metadata.language: zh-CN` |
| American English | [`en-US/multi-skill-creator/`](en-US/multi-skill-creator/) | `multi-skill-creator` | `metadata.language: en-US` |

两个版本使用同一个技能名，功能与行为保持一致。**只安装你需要的那个**——每个目录都是自足的。

## 它解决什么问题

写一个技能容易，写一个*真的会被用上、而且确实有用*的技能很难。难点通常不在措辞，而在于：

- 描述写得不够主动，该触发的时候 agent 不去用
- 改完一版不知道到底变好了还是变差了
- 感觉有效，但说不清是技能的功劳还是模型本来就会

这个技能给出一套可执行的流程来对付这些：

1. **写草案**：收窄意图、访谈边界情况、写出 SKILL.md
2. **造用例**：2-3 个真人会说的 prompt，存进 `evals/evals.json`
3. **对照跑**：每个用例同时跑「装技能」和「基线」两次，产出并列
4. **量化**：草拟可客观验证的断言，评分、汇总成 `benchmark.json`，含通过率、耗时、token 的均值 ± 标准差与差值
5. **人工复查**：生成一个本地网页，逐个用例看产出、留反馈、看基准对比
6. **按反馈重写**，再跑一轮，直到满意
7. **优化描述**：用 20 条该触发/不该触发的查询做 train/test 切分，自动迭代描述，按留出集得分选最优，避免过拟合

## 快速开始

```bash
# 1. 让它自己判断你该从哪一步开始
#    技能被触发后，会先问你现在是"有想法"、"有草案"还是"想优化描述"

# 2. 跑一次触发评测（需要 PATH 上有一个受支持的 agent CLI）
python -m scripts.run_eval \
  --eval-set triggers.json \
  --skill-path ../my-skill \
  --agent auto \
  --verbose

# 3. 跑完整的评测 + 改进循环
python -m scripts.run_loop \
  --eval-set triggers.json \
  --skill-path ../my-skill \
  --agent auto \
  --max-iterations 5 \
  --verbose

# 4. 汇总成基准报告
python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name my-skill

# 5. 打开人工复查页面
python eval-viewer/generate_review.py <workspace>/iteration-1 \
  --skill-name my-skill \
  --benchmark <workspace>/iteration-1/benchmark.json

# 6. 校验并打包
python scripts/quick_validate.py ../my-skill
python -m scripts.package_skill ../my-skill
```

这些命令要在**某个语言版本**的技能目录里执行（脚本通过 `scripts/` 包导入）。日常使用时，agent 会读 `SKILL.md` 并按流程替你调这些脚本，不需要你手敲。

## 支持哪些 agent

| 预设 | 命令 | 触发探针的判定方式 |
|---|---|---|
| `claude` | `claude` | JSON 事件流，精确 |
| `codex` | `codex` | 纯文本启发式 |
| `gemini` | `gemini` | 纯文本启发式 |
| `cursor-agent` | `cursor-agent` | 纯文本启发式 |
| `opencode` | `opencode` | 纯文本启发式 |
| `finch` | `finch` | 纯文本启发式 |

不在表里的工具用命令模板接进来：

```bash
--agent-cmd "my-agent --print {prompt}"
--agent-cmd "my-agent --print" --agent-transport stdin
```

细节（探针技能装到哪个目录、工程根目录怎么定、事件流与纯文本两种判定的精度差异）见技能里的 `references/agent-cli.md`。

**关于精度的诚实说明**：纯文本 CLIs 只能靠"回答里出现了探针标记"来推断是否触发了技能。这个证据弱于事件流，分数应视为上界，用来做版本间相对比较比做绝对判断更靠谱。

## 目录结构

```text
multi-skill-creator/
├── zh-CN/
│   └── multi-skill-creator/
│       ├── SKILL.md
│       ├── agents/          # 评分 / 盲测对比 / 事后分析 的子智能体指令
│       ├── assets/          # 测试集复查用的 HTML 模板
│       ├── eval-viewer/     # 产出复查页面（生成器 + 模板）
│       ├── references/      # JSON 结构定义、agent 适配层说明
│       ├── scripts/         # 全部可执行脚本
│       └── LICENSE
├── en-US/
│   └── multi-skill-creator/   # 与中文版同构
├── README.md
├── LICENSE
└── .gitignore
```

## 运行要求

- **Python 3.10+**（脚本用了 `X | None` 这样的类型写法）
- 一个受支持的 agent CLI，或任何能非交互接收 prompt 的命令
- 插件依赖：无。`quick_validate.py` 优先用 PyYAML，没装则自动回退到内置解析器
- 浏览器仅在生成复查页面时需要；无显示器的环境用 `--static` 输出独立 HTML

## 与上游的差异

| 方面 | 上游 skill-creator | 本项目 |
|---|---|---|
| agent 调用 | 硬编码 `claude -p` | `scripts/agent_cli.py` 适配层，6 个预设 + 任意命令模板 |
| 探针安装位置 | 写死 `.claude/commands/` | 按 preset 决定，可用 `--install-root` 覆盖 |
| 触发判定 | 只解析 Claude 的事件流 | 事件流 + 纯文本回退，精度差异已在文档中标明 |
| 训练/测试切分 | 小测试集会把 train 切空 | 每个分层至少留一条在 train，空 train 直接报错 |
| 校验脚本 | 强依赖 PyYAML | 可选依赖，带内置回退；新增 `metadata.language` 校验 |
| 语言 | 仅英文 | 中英双语，各自独立可用 |

## 许可

Apache License 2.0，见 [LICENSE](LICENSE)。原始版权归 Anthropic 所有；本仓库的修改部分同样以 Apache-2.0 发布。
