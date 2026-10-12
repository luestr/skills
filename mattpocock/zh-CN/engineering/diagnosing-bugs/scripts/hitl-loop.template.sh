#!/usr/bin/env bash
# 人在回路（human-in-the-loop）的复现回路。
# 复制这个文件，编辑下面的步骤，然后运行它。
# Agent 运行脚本；用户在自己的终端里按提示操作。
#
# 用法：
#   bash hitl-loop.template.sh
#
# 两个辅助函数：
#   step "<instruction>"          → 显示提示语，等待回车
#   capture VAR "<question>"      → 显示问题，把回答读入 VAR
#
# 结束时，捕获到的值会以 KEY=VALUE 形式打印出来，供 Agent 解析。
#
# `capture` 会把值打印回终端，Agent 在那里读到它，
# 所以要捕获观察结果，把登录这类操作留给用户、用 `step` 处理。

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [完成后按回车] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- 在下方编辑 ---------------------------------------------------------

step "在 http://localhost:3000 打开应用并登录。"

capture ERRORED "点击“Export”按钮。它抛错了吗？（y/n）"

capture ERROR_MSG "粘贴错误信息（或“none”）："

# --- 在上方编辑 ---------------------------------------------------------

printf '\n--- 已捕获 ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
