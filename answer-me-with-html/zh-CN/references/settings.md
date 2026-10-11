# 设置、清理与更新

当 SKILL.md 第 0 节把你送到这里时读本文。

（本技能是 Chatlo 专项适配版；涉及浏览器与更新的部分已按 Chatlo 改写。所有 `am` 命令都用 `bun` 运行，并带上 `AM_HOME=/agent/outputs/answer-me-with-html`，即 `AM_HOME=/agent/outputs/answer-me-with-html bun scripts/am.mjs …`。）

当用户的要求以 `config` 开头（例如 `/answer-me-with-html config open off`）时，这一轮只处理设置，不产出页面：

- `config`：运行 `am config` 显示当前设置，再让用户选。若当前 agent 有选择工具就用它：一次最多 4 项，优先 `open`、`theme`、`mode`、`style`，在选项里标出当前值。否则用纯文本询问。
- `config <key> <value>`：运行 `am config set <key> <value>`。
- `config reset [key]`：运行 `am config reset [key]`。

用户用自然语言提出时（"别自动开浏览器"、"默认用卡片主题"），也把它转成 `am config set`。设置项：`open`（自动开浏览器）、`theme`、`mode`、`style`、`voice`（视频朗读）、`update_check`（新版本提示）。运行 `am config` 可看全部说明。

## Chatlo 注意事项

- **`open` 在 Chatlo 上应保持关闭**：Chatlo 没有可用的系统浏览器（没有 `open` / `xdg-open`），页面一律由你用 Chatlo 内置浏览器打开。首次使用本技能时先运行一次 `am config set open off`。
- **浏览器只能用内置的**：预览、网页操作、截图、视频导出都用 `web_browser` 工具（或等价的 `chatlo-browser` CLI，WebKit）。禁止安装或调用任何第三方浏览器/内核。
- **视频导出只用内置浏览器**：见 `references/video.md`，仅 WebM（VP8 / VP9）。

## 清理

当用户要求清理页面或缓存时：先运行 `am clean --dry-run`，告诉用户将删除多少项、多少空间。用户同意后再运行 `am clean`（`--all` 删除全部页面与视频，`--days N` 改变保留天数）。

## 更新

上游技能通过 `npx skills update` / `claude plugin update` / `git pull` 更新。**Chatlo 的适配版不走这些渠道**：本技能是按来源仓库（`QingYunA/answer-me-with-html`）重新适配并重新导入的版本，更新方式是按来源仓库重新适配，再沿用 `/agent/skills/` 下的工作副本执行 `chatlo-skills install`。

- 不要因为 `update_check` 的提示就去 `git pull` 上游仓库——那会覆盖 Chatlo 的适配改动。
- 只把更新提示转达给用户，由用户决定是否重新适配。
