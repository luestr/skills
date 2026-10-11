# Built-in brand marks

Archify ships a bounded catalogue of 107 commonly used brands for architecture,
workflow, sequence, data-flow, and lifecycle nodes. The mark is optional authored
identity: it never replaces the node's semantic `type`, color, label, or
relationships.

Unknown sites are handled by an explicit two-stage workflow. Run
`bun bin/archify.mjs brands capture <url> --json`, then author the returned
digest-pinned `brand` value. Normal render and validate commands do not perform
an unpinned capture, and changed or unavailable content fails closed.

Most vector paths and brand metadata are generated from Simple Icons 16.28.0.
The OpenAI mark is traced to OpenAI's official brand guidelines. Every generated
entry records its source and, when available upstream, its guidelines and license
metadata in `renderers/shared/generated-brand-marks.mjs`.

Brand names and logos may be trademarks of their respective owners. Simple
Icons' CC0 license covers its collection work, not every underlying trademark or
artwork. Contributors must review the recorded source, current brand guidelines,
and intended referential use before adding or updating a mark. Archify does not
imply sponsorship, endorsement, or partnership.

Edit `catalog.json`, then regenerate the committed zero-runtime-dependency bundle:

```bash
npm run generate:brand-marks
npm run check:brand-marks
```

Do not hand-edit `renderers/shared/generated-brand-marks.mjs`.

## Chatlo adaptation

This skill is adapted for Chatlo (iOS, built-in WebKit browser). Run the CLI with `bun`: every `node bin/archify.mjs` is `bun bin/archify.mjs`. Use only the Chatlo built-in browser (the `web_browser` tool or the equivalent `chatlo-browser` command); do not install, download, or run Chrome/Chromium/Firefox/Edge/Playwright/Puppeteer or any other third-party browser or engine.

On Chatlo there is no desktop Chrome, and the built-in browser viewport is fixed by the host (phone-sized), so the automated desktop `browser-check` gate cannot run. `finalize` therefore marks the `browser-check` stage `delegated` (its `visualReview` is `delegated-to-chatlo-web_browser`): `validate -> deliver -> check` still all pass. Perform the delegated review with the built-in browser at the device viewport; see `chatlo-browser-evidence.md` for the probe scripts and pass criteria.

Do not use `preview` or `--open`: Chatlo has no OS opener. Open artifacts with the `web_browser` tool via `chatlo:///absolute/path`.

The self-update check is disabled by default (`ARCHIFY_UPDATE_CHECK_DISABLED=1`); do not check for or install updates.
