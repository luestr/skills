# Update awareness

Read this file when a `finalize` or standalone `deliver` receipt has `update.noticeRequired: true`.

Keep one compact line in the final response, in the user's language, with `installedVersion`, `availableVersion`, and the official `releaseNotes` link. Say that the installed Skill has not changed and that the user can ask to snooze or ignore the reminder. If `source` is `cache`, say that a previous check at `checkedAt` found the update. A process message or tool output does not replace this final line.
For `severity: "security"`, label it as a security update without making installation automatic or urgent by default.

You may translate the fixed local `noticeText`. Never quote, summarize, or translate the remote manifest's summary.

When the user explicitly asks to pause or stop this reminder, run `bun scripts/check-update.mjs --snooze "<eventKey>"` (seven days) or `--ignore "<eventKey>"` (this exact release only) from the Skill directory with the receipt's `update.eventKey`, then report the returned status. Never run them on your own initiative; `--ack` is a no-op. These commands do not install an update, and a newer release notifies again.

The notice is information, not permission. Keep the installed version unchanged. This workflow never downloads, installs, or executes an update, and silence is never consent.

## Chatlo adaptation

This skill is adapted for Chatlo (iOS, built-in WebKit browser). Run the CLI with `bun`: every `node bin/archify.mjs` is `bun bin/archify.mjs`. Use only the Chatlo built-in browser (the `web_browser` tool or the equivalent `chatlo-browser` command); do not install, download, or run Chrome/Chromium/Firefox/Edge/Playwright/Puppeteer or any other third-party browser or engine.

On Chatlo there is no desktop Chrome, and the built-in browser viewport is fixed by the host (phone-sized), so the automated desktop `browser-check` gate cannot run. `finalize` therefore marks the `browser-check` stage `delegated` (its `visualReview` is `delegated-to-chatlo-web_browser`): `validate -> deliver -> check` still all pass. Perform the delegated review with the built-in browser at the device viewport; see `chatlo-browser-evidence.md` for the probe scripts and pass criteria.

Do not use `preview` or `--open`: Chatlo has no OS opener. Open artifacts with the `web_browser` tool via `chatlo:///absolute/path`.

The self-update check is disabled by default (`ARCHIFY_UPDATE_CHECK_DISABLED=1`); do not check for or install updates.
