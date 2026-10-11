# Settings, clean-up and updates

Read this when section 0 of SKILL.md sends you here.

(This is the Chatlo-specific adaptation; the browser and update parts are rewritten for Chatlo. Every `am` command runs with `bun` and carries `AM_HOME=/agent/outputs/answer-me-with-html`, that is `AM_HOME=/agent/outputs/answer-me-with-html bun scripts/am.mjs …`.)

When the user's request starts with `config` (for example `/answer-me-with-html config open off`), this turn handles settings only and produces no page:

- `config`: run `am config` to show the current settings, then let the user choose. Where the current agent has a choice tool, use it: at most 4 settings at a time, these first: `open`, `theme`, `mode`, `style`, with the current value marked in the options. Otherwise ask in plain text.
- `config <key> <value>`: run `am config set <key> <value>`.
- `config reset [key]`: run `am config reset [key]`.

When the user asks in natural language ("stop opening the browser", "use the card theme by default"), also convert it to `am config set`. Settings: `open` (auto-open the browser), `theme`, `mode`, `style`, `voice` (video narration), `update_check` (new-version notices). Run `am config` to see all descriptions.

## Chatlo notes

- **`open` must stay off on Chatlo**: Chatlo has no usable system browser (no `open` / `xdg-open`); you always open pages with Chatlo's built-in browser. On first use, run `am config set open off` once.
- **Use only the built-in browser**: preview, web operations, screenshots and video export all use the `web_browser` tool (or the equivalent `chatlo-browser` CLI, WebKit). Do not install or invoke any third-party browser or engine.
- **Video export uses the built-in browser only**: see `references/video.md`; WebM (VP8 / VP9) only.

## Clean-up

When the user asks to clean up pages or the cache: first run `am clean --dry-run` and tell the user how many items and how much space will be deleted. Run `am clean` only after the user agrees (add `--all` to delete all pages and videos, `--days N` to change how many days to keep).

## Updates

Upstream updates through `npx skills update` / `claude plugin update` / `git pull`. **The Chatlo adaptation does not use those channels**: this skill is re-adapted from the source repository (`QingYunA/answer-me-with-html`) and re-imported; update it by re-adapting from the source repository, then running `chatlo-skills install` on the working copy under `/agent/skills/`.

- Do not run `git pull` on the upstream repository because of an `update_check` notice — that would overwrite the Chatlo adaptation.
- Pass the update notice on to the user and let them decide whether to re-adapt.
