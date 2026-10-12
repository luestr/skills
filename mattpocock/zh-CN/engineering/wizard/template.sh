#!/usr/bin/env bash
#
# 向导带人一步步走完一套手工流程。
# 由 /wizard 技能生成。
#
# STAGES 标记以上的所有内容都是向导库：不要手工编辑它。
# 在标记以下编写每一步对应的阶段。

set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────
# 向导库：令人愉悦、一致的 UX，在每个向导里都完全相同。
# ──────────────────────────────────────────────────────────────────────────

if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
  BOLD=$(tput bold); DIM=$(tput dim); RESET=$(tput sgr0)
  BLUE=$(tput setaf 4); GREEN=$(tput setaf 2); YELLOW=$(tput setaf 3)
else
  BOLD=""; DIM=""; RESET=""; BLUE=""; GREEN=""; YELLOW=""
fi

# 作者在阶段区顶部设置这个值。
TOTAL_STAGES=0

_STAGE_INDEX=0
ENV_FILE="${ENV_FILE:-.env}"
WRITTEN_ENV=()    # 本次运行写入 ENV_FILE 的 KEY
WRITTEN_SECRET=() # 本次运行设置的 secret 名（NAME）
SKIPPED=()        # 没能完成的事项（例如缺失 gh）

# _clear 清空终端，让屏幕上只剩当前步骤。输出不是终端时是空操作，
# 这样管道输出的日志仍然可读。
_clear() {
  [[ -t 1 ]] || return 0
  if command -v tput >/dev/null 2>&1 && tput clear 2>/dev/null; then return 0; fi
  printf '\033[2J\033[3J\033[H'
}

# banner "Title" 显示开场画面：本向导的用途。
banner() {
  _clear
  printf '\n%s%s  %s%s\n' "$BOLD" "$BLUE" "$1" "$RESET"
  printf '%s  %s 个阶段%s\n\n' "$DIM" "$TOTAL_STAGES" "$RESET"
  printf '%s  你负责操作浏览器；本向导会明确告诉你该做什么，并\n' "$DIM"
  printf '  记录你复制回来的值。随时可按 Ctrl-C 停下，之后再重新运行，\n'
  printf '  因为它会记住已保存的值。%s\n' "$RESET"
  pause "准备好开始了吗？"
}

# stage "Name" 清屏，然后宣告一个阶段并显示进度。
# 清屏让屏幕上只剩当前步骤。
stage() {
  _clear
  _STAGE_INDEX=$((_STAGE_INDEX + 1))
  printf '\n%s%s▸ 阶段 %s/%s · %s%s\n' \
    "$BOLD" "$BLUE" "$_STAGE_INDEX" "$TOTAL_STAGES" "$1" "$RESET"
}

# say "..." 打印一行普通说明。
say()  { printf '  %s\n' "$1"; }
# step "..." 是人在浏览器里执行的动作，读起来像带编号的步骤。
step() { printf '  %s•%s %s\n' "$BLUE" "$RESET" "$1"; }
note() { printf '  %s%s%s\n' "$DIM" "$1" "$RESET"; }
warn() { printf '  %s⚠ %s%s\n' "$YELLOW" "$1" "$RESET"; }

# open_url URL 在用户的浏览器里打开它，跨平台，包括 WSL。
open_url() {
  local url="$1"
  printf '  %s↗ 正在打开%s %s\n' "$GREEN" "$RESET" "$url"
  { if   command -v wslview     >/dev/null 2>&1; then wslview "$url"
    elif command -v explorer.exe >/dev/null 2>&1; then explorer.exe "$url"
    elif command -v xdg-open    >/dev/null 2>&1; then xdg-open "$url"
    elif command -v open        >/dev/null 2>&1; then open "$url"
    else false; fi
  } >/dev/null 2>&1 || warn "打不开浏览器，请手动访问：$url"
}

# pause "msg" 等待用户确认他们已完成手工部分。
pause() {
  printf '  %s%s%s ' "$DIM" "${1:-按 Enter 继续}" "$RESET"
  read -r _ || true
}

# confirm "question" 是一个 y/N 关卡；回答 y 时返回成功。
confirm() {
  local reply=""
  printf '  %s? %s [y/N] ' "$YELLOW" "$1"
  read -r reply || true
  [[ "$reply" =~ ^[Yy] ]]
}

# _existing KEY：ENV_FILE 中 KEY 的当前值（如果有），已去除 write_env 的单引号
# 或普通 dotenv 双引号包裹。
_existing() {
  [[ -f "$ENV_FILE" ]] || return 1
  local line value sq="'\\''"; line=$(grep -E "^${1}=" "$ENV_FILE" | tail -n1) || return 1
  value="${line#*=}"
  if [[ "$value" == \'*\' ]]; then value="${value:1:${#value}-2}"; value="${value//"$sq"/\'}"
  elif [[ "$value" == \"*\" ]]; then
    value="${value:1:${#value}-2}"
    [[ "$value" == *[\\\$\"]* ]] && return 1   # 含转义、$ 或 "：无法安全解码，重新询问
  fi
  printf '%s' "$value"
}

# ask KEY "Prompt" 读取一个值存入 $KEY。重新运行时把 .env 中的现有值作为
# 默认值提供（按 Enter 保留）。输入可见（非密钥），由 Readline 编辑。
# 在 EOF 且无输入时失败。
ask() {
  local key="$1" prompt="$2" current input s=$'\001' e=$'\002' p rc=0
  current=$(_existing "$key" || true)
  # Readline 需要把颜色码包在 \001..\002 里，才能正确放置光标。
  p="  $s$BOLD$e$prompt$s$RESET$e "
  [[ -n "$current" ]] && p+="$s$DIM$e[按 Enter 保留当前值]$s$RESET$e "
  read -e -r -p "$p" input || rc=1
  if (( rc )) && [[ -z "$input" ]]; then return 1; fi
  [[ -z "$input" && -n "$current" ]] && input="$current"
  printf -v "$key" '%s' "$input"
}

# ask_secret KEY "Prompt" 与 ask 类似，但输入隐藏。
ask_secret() {
  local key="$1" prompt="$2" current input rc=0
  current=$(_existing "$key" || true)
  if [[ -n "$current" ]]; then
    printf '  %s%s%s %s[按 Enter 保留当前值]%s ' "$BOLD" "$prompt" "$RESET" "$DIM" "$RESET"
  else
    printf '  %s%s%s ' "$BOLD" "$prompt" "$RESET"
  fi
  read -rs input || rc=1
  printf '\n'
  if (( rc )) && [[ -z "$input" ]]; then return 1; fi
  [[ -z "$input" && -n "$current" ]] && input="$current"
  printf -v "$key" '%s' "$input"
}

# write_env KEY VALUE 把 KEY='VALUE' 更新插入 ENV_FILE（替换任何已有行）
# 并设置 $KEY。幂等。以 0600 权限创建 ENV_FILE；通过符号链接写入，
# 并保留已有文件的权限。
write_env() {
  local key="$1" value="$2" tmp sq="'\\''"
  [[ -e "$ENV_FILE" ]] || (umask 077 && : > "$ENV_FILE")
  tmp=$(mktemp)
  grep -vE "^${key}=" "$ENV_FILE" > "$tmp" || true
  printf "%s='%s'\n" "$key" "${value//\'/$sq}" >> "$tmp"
  cat "$tmp" > "$ENV_FILE"
  rm -f "$tmp"
  printf -v "$key" '%s' "$value"
  WRITTEN_ENV+=("$key")
  printf '  %s✓ 已写入%s %s → %s\n' "$GREEN" "$RESET" "$key" "$ENV_FILE"
}

# set_secret NAME VALUE 通过 gh 设置 GitHub Actions 仓库 secret。如果 gh
# 不可用或未认证，就降级为警告（并记录下来）。
set_secret() {
  local name="$1" value="$2"
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    if printf '%s' "$value" | gh secret set "$name" >/dev/null 2>&1; then
      WRITTEN_SECRET+=("$name")
      printf '  %s✓ 已设置%s GitHub secret %s\n' "$GREEN" "$RESET" "$name"
      return
    fi
  fi
  SKIPPED+=("GitHub secret $name（请手动设置：gh secret set $name）")
  warn "已跳过 GitHub secret $name：gh 尚未就绪，请稍后再设置"
}

# set_var NAME VALUE 设置一个 GitHub Actions 仓库变量（非密钥）。
set_var() {
  local name="$1" value="$2"
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    if gh variable set "$name" --body "$value" >/dev/null 2>&1; then
      printf '  %s✓ 已设置%s GitHub variable %s\n' "$GREEN" "$RESET" "$name"
      return
    fi
  fi
  SKIPPED+=("GitHub variable $name")
  warn "已跳过 GitHub variable $name，gh 尚未就绪，请稍后再设置"
}

# finish 清屏，然后显示所有已配置内容的收尾总结。
finish() {
  _clear
  printf '\n%s%s  ✓ 配置完成%s\n' "$BOLD" "$GREEN" "$RESET"
  (( ${#WRITTEN_ENV[@]} ))    && note "已写入 ${#WRITTEN_ENV[@]} 个值到 $ENV_FILE：${WRITTEN_ENV[*]}"
  (( ${#WRITTEN_SECRET[@]} )) && note "已设置 ${#WRITTEN_SECRET[@]} 个 GitHub secret：${WRITTEN_SECRET[*]}"
  if (( ${#SKIPPED[@]} )); then
    printf '\n'; warn "仍需手动完成："
    for s in "${SKIPPED[@]}"; do note "  - $s"; done
  fi
  printf '\n'
}

# ──────────────────────────────────────────────────────────────────────────
# STAGES：编写这一节。人类每执行一步，就对应一个 stage()。
# 用你的实际步骤替换下面的示例。把 TOTAL_STAGES 设为与所写阶段数一致。
# 保持所有阶段都在 run_wizard 内，且最后一行原样不动：bash 会在第一个提示
# 出现之前解析整个文件，因此运行中途的编辑不会破坏它。
# ──────────────────────────────────────────────────────────────────────────

run_wizard() {

TOTAL_STAGES=1

banner "Stripe 配置"

# ── 示例阶段：替换为你自己的真实步骤 ──────────────────────────────────────
stage "Stripe：API 密钥"
say "我们这就获取你的 Stripe 测试密钥，并存好，供本地开发和 CI 使用。"
open_url "https://dashboard.stripe.com/test/apikeys"
step "在 API 密钥页面复制 Publishable key（以 pk_test_ 开头）。"
ask STRIPE_PUBLISHABLE_KEY "粘贴 publishable key："
step "在 Secret key 那一行点击“Reveal test key”，然后复制它。"
ask_secret STRIPE_SECRET_KEY "粘贴 secret key："
write_env STRIPE_PUBLISHABLE_KEY "$STRIPE_PUBLISHABLE_KEY"
write_env STRIPE_SECRET_KEY "$STRIPE_SECRET_KEY"
set_secret STRIPE_SECRET_KEY "$STRIPE_SECRET_KEY"   # CI 需要这个
# ──────────────────────────────────────────────────────────────────────────

finish
}

run_wizard "$@"; exit
