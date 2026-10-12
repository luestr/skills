---
name: git-guardrails-claude-code
description: 配置 Claude Code 钩子，在危险 git 命令（push、reset --hard、clean、branch -D 等）执行前将其拦截。当用户想阻止破坏性 git 操作（destructive git operations）、添加 git 安全钩子（git safety hooks），或在 Claude Code 中拦截 git push/reset 时使用。
---

# 配置 Git 护栏

配置一个 PreToolUse 钩子，在 Claude 执行危险 git 命令前拦截并阻止它们。

## 拦截哪些命令

- `git push`（包括 `--force` 在内的所有变体）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

被拦截时，Claude 会看到一条消息，告知它无权访问这些命令。

## 步骤

### 1. 询问范围

询问用户：安装到**本项目**（`.claude/settings.json`）还是**所有项目**（`~/.claude/settings.json`）？

### 2. 复制钩子脚本

捆绑的脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

按范围把它复制到目标位置：

- **项目**：`.claude/hooks/block-dangerous-git.sh`
- **全局**：`~/.claude/hooks/block-dangerous-git.sh`

用 `chmod +x` 使其可执行。

### 3. 把钩子加入设置

添加到对应的设置文件：

**项目**（`.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**全局**（`~/.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

如果设置文件已存在，就把钩子合并进现有的 `hooks.PreToolUse` 数组。不要覆盖其他设置。

### 4. 询问是否定制

询问用户是否要增删拦截列表中的模式。相应修改复制出的脚本。

### 5. 验证

跑一个快速测试：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

应以退出码 2 退出，并向 stderr 打印一条 BLOCKED 消息。
