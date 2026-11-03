# JSON 结构定义

本文档定义技能创建流程中用到的 JSON 结构。

字段名是要紧的：复查查看器和基准汇总脚本都按字面读取。如果这里写的形状和某个脚本实际产出的不一样，以这里的定义为准——而不是反过来。

---

## evals.json

定义技能的测试用例，位于技能目录下的 `evals/evals.json`。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的示例 prompt",
      "expected_output": "对期望结果的描述",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "产出中包含 X",
        "技能使用了脚本 Y"
      ]
    }
  ]
}
```

**字段：**
- `skill_name`：与技能 frontmatter 中的 `name` 一致
- `evals[].id`：唯一整数标识
- `evals[].prompt`：要执行的任务
- `evals[].expected_output`：人类可读的成功标准描述
- `evals[].files`：可选，输入文件路径列表（相对于技能根目录）
- `evals[].expectations`：可验证的断言列表

---

## history.json

记录改进模式下的版本演进，位于工作区根目录。

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**字段：**
- `started_at`：开始改进时的 ISO 时间戳
- `skill_name`：被改进的技能名
- `current_best`：表现最好的版本标识
- `iterations[].version`：版本标识（v0、v1 …）
- `iterations[].parent`：派生自哪个版本
- `iterations[].expectation_pass_rate`：评分得到的通过率
- `iterations[].grading_result`：`baseline`、`won`、`lost` 或 `tie`
- `iterations[].is_current_best`：是否为当前最优

---

## grading.json

评分 agent 的输出，位于 `<run-dir>/grading.json`。

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**字段：**
- `expectations[]`：逐条断言及其证据。**必须**用 `text`、`passed`、`evidence` 三个字段名，查看器依赖它们
- `summary`：通过数、失败数、总数、通过率
- `execution_metrics`：工具使用与产物体量（来自执行方的 metrics.json）
- `timing`：实际耗时（来自 timing.json）
- `claims`：从产出中抽取并核实的说法
- `user_notes_summary`：执行方标记的问题
- `eval_feedback`：可选，评分方发现测试用例本身有问题时才出现

---

## metrics.json

执行方的输出，位于 `<run-dir>/outputs/metrics.json`。

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Bash": 8,
    "Edit": 1,
    "Glob": 2,
    "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**字段：**
- `tool_calls`：各类工具的调用次数（按你环境里真实的工具名记录，名字不必和上面的示例一致）
- `total_tool_calls`：调用总数
- `total_steps`：主要执行步骤数
- `files_created`：产出的文件列表
- `errors_encountered`：执行过程中遇到的错误数
- `output_chars`：产物的总字符数
- `transcript_chars`：过程记录的字符数

---

## timing.json

单次 run 的实际耗时，位于 `<run-dir>/timing.json`。

**怎么采集：** 看运行环境在 run 结束时能给出什么——带 `total_tokens` 和 `duration_ms` 的任务通知、日志行，或者你自己记的表。立刻存下来，它通常不会写进别处，事后也补不回来。拿不到的字段就省略，不要估算；缺一列比编一个数字好。

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

基准模式的输出，位于 `benchmarks/<timestamp>/benchmark.json`。由 `scripts/aggregate_benchmark.py` 生成；手工写的时候严格照这个形状。

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "跑测试用的模型",
    "analyzer_model": "做分析用的模型",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },

  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "用的是 2023 年的数据，可能过时",
        "不可填字段回退成文本叠加"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "断言『产出是 PDF 文件』在两种配置下都 100% 通过——可能体现不出技能的价值",
    "用例 3 方差很大（50% ± 40%）——可能不稳定或依赖模型",
    "不装技能的 run 在表格抽取类断言上稳定失败",
    "技能平均多花 13 秒，但通过率提升 50%"
  ]
}
```

**字段：**
- `metadata`：基准运行的信息
  - `skill_name`：技能名
  - `timestamp`：跑基准的时间
  - `evals_run`：跑到的用例名或 ID
  - `runs_per_configuration`：每种配置跑了多少次（例如 3）
- `runs[]`：逐次 run 的结果
  - `eval_id`：数字型用例标识
  - `eval_name`：可读的用例名（在查看器里用作分节标题）
  - `configuration`：新建技能时必须写作 `with_skill` 或 `without_skill`；改进已有技能时用 `with_skill` / `old_skill`。查看器按这个确切字符串分组和着色
  - `run_number`：整数运行序号（1、2、3 …）
  - `result`：嵌套对象，含 `pass_rate`、`passed`、`total`、`time_seconds`、`tokens`、`errors`
- `run_summary`：各配置的统计汇总
  - `with_skill` / `without_skill`（或 `old_skill`）：各自含 `pass_rate`、`time_seconds`、`tokens`，每项有 `mean` 和 `stddev`
  - `delta`：差值字符串，如 `"+0.50"`、`"+13.0"`、`"+1700"`
- `notes`：分析方的自由观察

**重要：** 查看器严格按这些字段名读取。用 `config` 而不是 `configuration`，或者把 `pass_rate` 放在 run 顶层而不是 `result` 里面，都会导致查看器显示空值或 0。手工生成 benchmark.json 时务必回查本节。

---

## comparison.json

盲测对比的输出，位于 `<grading-dir>/comparison-N.json`。

```json
{
  "winner": "A",
  "reasoning": "A 给出了完整方案，格式规范、字段齐全。B 缺日期字段，且有格式不一致。",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5, "accuracy": 4},
      "structure": {"organization": 4, "formatting": 5, "usability": 4},
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2, "accuracy": 3},
      "structure": {"organization": 3, "formatting": 2, "usability": 3},
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["方案完整", "格式规范", "字段齐全"],
      "weaknesses": ["页眉有轻微的样式不一致"]
    },
    "B": {
      "score": 5,
      "strengths": ["可读", "基本结构正确"],
      "weaknesses": ["缺日期字段", "格式不一致", "数据抽取不完整"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "产出包含姓名", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "产出包含姓名", "passed": true}
      ]
    }
  }
}
```

---

## analysis.json

事后分析的输出，位于 `<grading-dir>/analysis.json`。

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "对比方选择该赢家的简要理由"
  },
  "winner_strengths": [
    "对多页文档处理给出了清晰的逐步指令",
    "附带校验脚本，能抓出格式错误"
  ],
  "loser_weaknesses": [
    "『适当地处理文档』这种模糊指令导致行为不一致",
    "没有校验脚本，agent 只能自己临时发挥"
  ],
  "instruction_following": {
    "winner": {"score": 9, "issues": ["次要：跳过了可选的日志步骤"]},
    "loser": {
      "score": 6,
      "issues": [
        "没有使用技能提供的格式模板",
        "没有按第 3 步执行，自己发明了一套办法"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "把『适当地处理文档』换成明确的步骤：1) 抽取文本 2) 识别章节 3) 按模板排版",
      "expected_impact": "消除导致行为不一致的模糊之处"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "读技能 → 按 5 步流程执行 → 用校验脚本 → 修掉 2 个问题 → 产出",
    "loser_execution_pattern": "读技能 → 方法不明确 → 试了 3 种办法 → 没有校验 → 产出有错误"
  }
}
```

**改进建议的类别**：`instructions`（正文措辞）、`tools`（脚本、模板、工具）、`examples`（示例输入输出）、`error_handling`（失败处理）、`structure`（内容重组）、`references`（外部文档或资源）。

**优先级**：`high`（很可能改变本次对比的结果）、`medium`（提升质量但未必改变胜负）、`low`（锦上添花）。
