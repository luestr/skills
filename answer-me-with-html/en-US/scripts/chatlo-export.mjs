#!/usr/bin/env node
// Chatlo-only WebM export for answer-me-with-html player pages.
//
// The upstream skill exports a WebM by driving a local Chrome over the DevTools protocol.
// Chatlo has no local Chrome (and installing a browser is not allowed), so this helper drives
// the SAME in-page encoder (window.__amvEnc, WebCodecs) through Chatlo's built-in WebKit browser
// instead, using the `chatlo-browser` CLI (the `web_browser` tool).
//
// WebKit's WebCodecs encoder in Chatlo supports VP8 and VP9 only, so the page picks VP9
// (vp09.00.31.08) and falls back to VP8; no other codec is ever used.
//
// Usage:
//   bun scripts/chatlo-export.mjs <player.html> <out.webm> [--bitrate 900000]
import { spawnSync } from 'node:child_process';
import { closeSync, mkdtempSync, openSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { isAbsolute, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SLICE = 262144;      // bytes fetched per evaluate round trip (keeps each string small)
const POLL_MS = 500;       // how often to ask the page for progress
const OPEN_WAIT_MS = 3000; // settle time after the page opens
const DEFAULT_BITRATE = 900000;

// chatlo-browser only succeeds when stdout is a real file descriptor (not a pipe created by Node),
// so every call writes its JSON to a temp file and reads it back.
function chatloBrowser(args) {
  const dir = mkdtempSync(join(tmpdir(), 'am-chatlo-'));
  const out = join(dir, 'out.json');
  const fd = openSync(out, 'w');
  let result;
  try {
    spawnSync('chatlo-browser', args, { stdio: ['inherit', fd, 'pipe'] });
  } finally {
    closeSync(fd);
  }
  const text = readFileSync(out, 'utf8');
  rmSync(dir, { recursive: true, force: true });
  if (!text.trim()) throw new Error(`chatlo-browser ${args[0]} produced no output (is Chatlo's browser available?)`);
  result = JSON.parse(text);
  if (result.ok === false) throw new Error(`chatlo-browser ${args[0]}: ${result.error?.message ?? 'failed'}`);
  return result.result;
}

const evaluate = (targetId, fn) => {
  const r = chatloBrowser(['act', '--kind', 'evaluate', '--fn', fn, '--target-id', targetId]);
  return r.result;
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main(argv) {
  const args = argv.slice(2);
  const positional = args.filter((a) => !a.startsWith('--'));
  const flag = (name, def) => {
    const i = args.indexOf(name);
    return i >= 0 && args[i + 1] ? args[i + 1] : def;
  };
  const [htmlArg, outArg] = positional;
  if (!htmlArg || !outArg) {
    process.stderr.write('Usage: bun scripts/chatlo-export.mjs <player.html> <out.webm> [--bitrate 900000]\n');
    return 2;
  }
  const html = isAbsolute(htmlArg) ? htmlArg : resolve(process.cwd(), htmlArg);
  const outFile = isAbsolute(outArg) ? outArg : resolve(process.cwd(), outArg);
  const bitrate = Number(flag('--bitrate', DEFAULT_BITRATE)) || DEFAULT_BITRATE;

  const opened = chatloBrowser(['open', '--url', pathToFileURL(html).href.replace(/^file:/, 'chatlo:')]);
  const targetId = opened.targetId;
  if (!targetId) throw new Error('the browser did not return a tab id');
  process.stderr.write(`tab ${targetId}\n`);
  await sleep(OPEN_WAIT_MS);

  const supported = evaluate(targetId, 'String(Boolean(window.__amvEnc && window.__amvEnc.supported()))');
  if (supported !== 'true') throw new Error('this page has no in-browser encoder (is it an am video player page?)');

  const started = JSON.parse(evaluate(targetId, `JSON.stringify(window.__amvEnc.start({ bitrate: ${bitrate} }))`));
  if (started.error) throw new Error(started.error);
  process.stderr.write(`encoding ${started.total} frames (${started.duration.toFixed(1)}s @ ${started.fps}fps)\n`);

  let state;
  for (;;) {
    state = JSON.parse(evaluate(targetId, 'JSON.stringify(window.__amvEnc.progress())'));
    if (state.error) throw new Error(`the browser stopped encoding: ${state.error}`);
    process.stderr.write(`\r${state.done}/${state.total}`);
    if (!state.running) break;
    await sleep(POLL_MS);
  }
  process.stderr.write(`\ncodec ${state.codec}${state.audio ? ' + opus' : ' (captions only)'}\n`);

  const size = Number(evaluate(targetId, 'String(window.__amvEnc.size())'));
  process.stderr.write(`file ${size} bytes\n`);
  const chunks = [];
  for (let at = 0; at < size; at += SLICE) {
    const b64 = evaluate(targetId, `window.__amvEnc.bytes(${at}, ${Math.min(SLICE, size - at)})`);
    chunks.push(Buffer.from(b64, 'base64'));
  }
  writeFileSync(outFile, Buffer.concat(chunks));
  process.stderr.write(`✓ ${outFile}\n`);
  return 0;
}

main(process.argv).then((code) => { process.exitCode = code; }, (err) => {
  process.stderr.write(`✗ ${err.message}\n`);
  process.exitCode = 1;
});
