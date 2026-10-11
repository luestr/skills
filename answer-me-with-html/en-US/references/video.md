# Explainer videos (am video, 3Blue1Brown style)

Read this when section 7 of SKILL.md sends you here. `am` means the full command from section 2 of SKILL.md (including `AM_HOME=/agent/outputs/answer-me-with-html`); resolve the script path in this file against this file's directory and write it out in full (once installed, this directory is `/agent/skills/answer-me-with-html/en-US/`).

A video draft has the same format as a page draft, with one extra rule: lines starting with `>` are narration, one beat per line.

````bash
AM_HOME=/agent/outputs/answer-me-with-html bun scripts/am.mjs video - --no-open <<'AM_EOF'
---
title: The TCP three-way handshake
subtitle: Why three
---
> Opening narration (optional).

## Both ends are waiting
```sequence
Client -> Server: SYN
Server -> Client: SYN-ACK
Client -> Server: ACK
```
> First the client sends SYN to ask for a connection.
> [Server] answers with SYN-ACK.
> The client replies with ACK, and the connection is open.
AM_EOF
````

- One `## ` is one scene. Put one component (or one table, one list) in a scene as the picture, and write 2–5 narration lines below it.
- When the Nth narration line plays, the picture shows step N. In flow / er / sequence / tree every source line is one step; timeline, limits, table rows and list items step by entry. So the line order of the component is the order of the explanation. When there are more narration lines than steps, the extra first lines serve as an opening and show nothing new.
- Write `[name]` in narration: the camera zooms in on the node or actor with that name and highlights it. The name must match how it is written in the component.
- Nodes with the same name in adjacent scenes move smoothly to their new position. To keep the viewer following one object, reuse the same name in the next scene.
- 3–6 scenes per video, one or two sentences per narration line.
- Narration is read aloud, so write it as speech, as if explaining to someone face to face; transitions are fine, and characters' "lines" go in quotes. Do not write it like a manual. Sentence length is still subject to the STE check.
- The look follows the theme in the settings by default (usually the blueprint drawing style). When the user wants "that dark 3b1b style", write `theme: 3b1b` in the frontmatter.

## Chatlo specifics: narration and video export

### Narration (`--voice`)

- The default is `--voice auto`: ElevenLabs when `ELEVENLABS_API_KEY` is set, otherwise system TTS, and captions only when neither is available.
- **Chatlo has neither macOS `say` nor `espeak-ng`**, so the default result is **captions only, no voice-over**. To get narration, do either:
  - set `ELEVENLABS_API_KEY` (with `--voice elevenlabs`, or just `auto`);
  - set `AM_TTS_URL` to a local OpenAI-compatible speech service and use `--voice local`.
- When the user says "no sound", add `--voice off` (on Chatlo this equals the default).

### Output

- `am video` produces a **single-file player page** under `AM_HOME/videos/`. The player carries a chapter strip (jump to a scene), a speed button (0.5×–2×) and an export button (⤓).

### Exporting a video file (important, Chatlo-specific)

- Upstream's `am video --mp4` (local Chrome + CDP, then ffmpeg encodes H.264) and `--webm` (local Chrome + CDP driving the in-page encoder) **do not work on Chatlo**: Chatlo does not allow installing any third-party browser and has no usable Chrome channel. **Do not** use those two flags.
- On Chatlo, export **only** with the WebCodecs encoder inside the built-in browser, container **WebM, video codec VP8 / VP9 only** (this machine was measured to support VP9 `vp09.00.31.08`, VP8, and Opus audio). Use this skill's bundled script:

```bash
AM_HOME=/agent/outputs/answer-me-with-html bun scripts/chatlo-export.mjs \
  "/agent/outputs/answer-me-with-html/videos/<player-page>.html" \
  "/agent/outputs/answer-me-with-html/videos/<output>.webm" --bitrate 900000
```

- That script uses `chatlo-browser` to open the player page in the built-in browser (WebKit), drives the in-page encoder (`window.__amvEnc`) frame by frame, and writes the bytes back to a local `.webm`. It does **not** call Chrome, CDP, Playwright or Puppeteer.
- After export, verify with `ffprobe` (this machine has `ffprobe`): `ffprobe -v error -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 <file>` should show `codec_name=vp9` (or `vp8`).
- The player page's own export button (⤓) can also export WebM directly inside Chatlo's built-in browser; prefer the script above when the file must land on disk.
- If the user explicitly wants **MP4**: it is not available on Chatlo (no local Chrome, and the built-in browser's WebCodecs exports WebM only). Export WebM with the script above, then convert with the local `ffmpeg`: `ffmpeg -i in.webm out.mp4`, and tell the user this is a transcoding step, not upstream's native MP4 path.
- Full syntax: `am help video`. In the terminal, reply with one sentence plus the player page link (and the video file link).
