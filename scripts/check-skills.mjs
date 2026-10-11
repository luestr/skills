#!/usr/bin/env node
// 技能规范校验：检查本仓库全部技能是否满足 ZCode / skills 规范。
// 用法：node scripts/check-skills.mjs
//
// 校验项（ERROR 会以非零退出码结束）：
//   - name 与目录名一致、小写 kebab-case、1–64 字符
//   - description 存在且不超过 1024 字符（ZCode 超过即丢弃该技能）
//   - top-level frontmatter 键仅限 name/description/when_to_use/license/metadata
//   - Markdown 相对链接与图片可解析（以 / 开头按仓库根解析，与 GitHub 一致）
//   - 参考文件都被同语言 SKILL.md 引用（无孤儿文件）
//   - en-US / zh-CN 文件集一一对应，文件名一律 ASCII
//   - 无 BOM、无 CRLF/LF 混用、无 U+FFFD、有结尾换行
//   - JSON 可解析、JS 语法通过 node --check
// WARN 仅提示：description 触发语落在 250 字符展示窗口之外。

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const KNOWN_KEYS = new Set(['name', 'description', 'when_to_use', 'license', 'metadata']);
const NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const TRIGGER_RE = /(\bUse (this skill|it)\b|\bwhenever\b|\bTrigger\b|当(用户|任务|请求)|时使用|使用此技能|触发)/i;
// 文档中的语法示例占位符，不是真实链接
const PLACEHOLDERS = new Set(['/absolute/path.png', '/绝对/路径.png']);

const errors = [];
const warnings = [];
const err = (m) => errors.push(m);
const warn = (m) => warnings.push(m);

const walk = (dir, out = []) => {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === '.git') continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full, out); else out.push(full);
  }
  return out;
};
const rel = (p) => path.relative(root, p).replace(/\\/g, '/');

// ZCode 的 frontmatter 解析器：只读取顶格 `key: value`，支持 > / | 多行块，忽略缩进行
function parseFrontmatter(text) {
  const t = text.replace(/^\uFEFF/, '');
  if (!t.startsWith('---')) return null;
  const lines = t.split(/\r?\n/);
  if ((lines[0] ?? '').trim() !== '---') return null;
  let end = -1;
  for (let i = 1; i < lines.length; i++) if (lines[i].trim() === '---') { end = i; break; }
  if (end <= 0) return null;
  const body = lines.slice(1, end);
  const values = {};
  const keys = [];
  const malformed = [];
  const indentOf = (s) => (/^(\s*)/.exec(s)?.[1]?.length ?? 0);
  const fold = (ls) => {
    const out = []; let cur = [];
    for (const raw of ls) {
      const s = raw.trim();
      if (!s) { if (cur.length) { out.push(cur.join(' ')); cur = []; } continue; }
      cur.push(s);
    }
    if (cur.length) out.push(cur.join(' '));
    return out.join('\n').trim();
  };
  for (let i = 0; i < body.length; i++) {
    const line = body[i] ?? '';
    if (!line.trim() || line.trim().startsWith('#') || /^\s/.test(line)) continue;
    const colon = line.indexOf(':');
    if (colon <= 0) { malformed.push(i + 2); continue; }
    const key = line.slice(0, colon).trim();
    const value = line.slice(colon + 1).trim();
    keys.push(key);
    const kind = /^>[+-]?$/.test(value) ? 'folded' : /^\|[+-]?$/.test(value) ? 'literal' : null;
    if (!kind) { values[key] = value; continue; }
    const buf = []; let j = i + 1;
    for (; j < body.length; j++) {
      const next = body[j] ?? '';
      if (next.trim() && !/^\s/.test(next)) break;
      buf.push(next);
    }
    const indent = buf.reduce((acc, l) => (l.trim() ? Math.min(acc ?? Infinity, indentOf(l)) : acc), null);
    const stripped = buf.map((l) => (l.trim() ? l.slice(indent ?? 0) : ''));
    values[key] = kind === 'folded' ? fold(stripped) : stripped.join('\n').trim();
    i = j - 1;
  }
  for (const key of Object.keys(values)) {
    const v = (values[key] ?? '').trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) values[key] = v.slice(1, -1).trim();
  }
  return { keys, values, malformed };
}

const allFiles = walk(root);
const skillDirs = fs.readdirSync(root, { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.startsWith('.') && fs.existsSync(path.join(root, d.name, 'en-US', 'SKILL.md')))
  .map((d) => d.name)
  .sort();

if (skillDirs.length === 0) { console.error('未找到任何技能目录'); process.exit(1); }

for (const skill of skillDirs) {
  for (const lang of ['en-US', 'zh-CN']) {
    const file = path.join(root, skill, lang, 'SKILL.md');
    if (!fs.existsSync(file)) { err(`${rel(file)} 缺失`); continue; }
    const fm = parseFrontmatter(fs.readFileSync(file, 'utf8'));
    if (!fm) { err(`${rel(file)} 缺少合法 frontmatter`); continue; }
    const name = fm.values.name ?? '';
    if (name !== skill) err(`${rel(file)} name=${name || '(空)'} 与目录名 ${skill} 不一致`);
    if (!NAME_RE.test(name) || name.length > 64) err(`${rel(file)} name 不符合小写 kebab-case（1–64 字符）: ${name}`);
    const desc = fm.values.description ?? '';
    if (!desc) err(`${rel(file)} description 为空（ZCode 会丢弃该技能）`);
    if (desc.length > 1024) err(`${rel(file)} description ${desc.length} 字符 > 1024（ZCode 会丢弃该技能）`);
    const m = desc.match(TRIGGER_RE);
    if (m && m.index > 250) warn(`${rel(file)} 触发语在第 ${m.index} 字符，超出模型可见的 250 字符窗口`);
    for (const key of new Set(fm.keys)) if (!KNOWN_KEYS.has(key)) err(`${rel(file)} 未识别的 frontmatter 键: ${key}`);
    if (fm.malformed.length) err(`${rel(file)} frontmatter 第 ${fm.malformed.join(',')} 行不是 key: value`);
  }
}

for (const file of allFiles.filter((p) => p.endsWith('.md'))) {
  const text = fs.readFileSync(file, 'utf8');
  const dir = path.dirname(file);
  text.split(/\r?\n/).forEach((line, i) => {
    for (const m of line.matchAll(/\[[^\]]*\]\(([^)\s]+)\)/g)) {
      const target = m[1];
      if (/^(https?:|mailto:|#|data:)/i.test(target) || PLACEHOLDERS.has(target)) continue;
      const [p] = decodeURIComponent(target).split('#');
      if (!p) continue;
      const resolved = p.startsWith('/') ? path.join(root, p.slice(1)) : path.resolve(dir, p);
      if (!fs.existsSync(resolved)) err(`${rel(file)}:${i + 1} 链接目标不存在: ${target}`);
    }
  });
}

for (const skill of skillDirs) {
  for (const lang of ['en-US', 'zh-CN']) {
    const dir = path.join(root, skill, lang);
    const text = fs.readFileSync(path.join(dir, 'SKILL.md'), 'utf8');
    for (const file of walk(dir)) {
      const base = path.basename(file);
      if (base === 'SKILL.md' || base === 'evals.json') continue;
      const r = rel(file).replace(`${skill}/${lang}/`, '');
      if (!text.includes(base) && !text.includes(r)) err(`${rel(file)} 未被 ${lang}/SKILL.md 引用`);
    }
  }
  const en = walk(path.join(root, skill, 'en-US')).map((p) => rel(p).replace(`${skill}/en-US/`, '')).sort();
  const zh = walk(path.join(root, skill, 'zh-CN')).map((p) => rel(p).replace(`${skill}/zh-CN/`, '')).sort();
  const onlyEn = en.filter((x) => !zh.includes(x));
  const onlyZh = zh.filter((x) => !en.includes(x));
  if (onlyEn.length) err(`${skill} 仅 en-US 存在: ${onlyEn.join(', ')}`);
  if (onlyZh.length) err(`${skill} 仅 zh-CN 存在: ${onlyZh.join(', ')}`);
  for (const f of [...en, ...zh]) if (/[^\x00-\x7F]/.test(f)) err(`${skill} 文件名含非 ASCII 字符: ${f}`);
}

for (const file of allFiles) {
  const buf = fs.readFileSync(file);
  const text = buf.toString('utf8');
  const r = rel(file);
  if (buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) err(`BOM: ${r}`);
  const crlf = (text.match(/\r\n/g) || []).length;
  const lf = (text.match(/(?<!\r)\n/g) || []).length;
  if (crlf && lf) err(`CRLF/LF 混用: ${r}`);
  if (text.length && !text.endsWith('\n') && path.basename(file) !== 'LICENSE') err(`缺少结尾换行: ${r}`);
  if (text.includes('\uFFFD')) err(`含 U+FFFD 替换字符: ${r}`);
  if (/\.(mjs|js)$/.test(file)) {
    try { execSync(`node --check "${file}"`, { stdio: 'pipe' }); } catch { err(`JS 语法错误: ${r}`); }
  }
  if (file.endsWith('.json')) {
    try { JSON.parse(text); } catch (e) { err(`JSON 解析失败: ${r} (${e.message})`); }
  }
}

const readme = path.join(root, 'README.md');
if (fs.existsSync(readme)) {
  for (const m of fs.readFileSync(readme, 'utf8').matchAll(/\]\(\/([^)]+)\)/g)) {
    if (!fs.existsSync(path.join(root, m[1]))) err(`README 链接目标不存在: /${m[1]}`);
  }
}

console.log(`技能数: ${skillDirs.length} — ${skillDirs.join(', ')}`);
if (warnings.length) {
  console.log(`\nWARN (${warnings.length})`);
  for (const w of warnings) console.log('  - ' + w);
}
if (errors.length) {
  console.log(`\nERROR (${errors.length})`);
  for (const e of errors) console.log('  - ' + e);
  console.log('\n校验失败');
  process.exit(1);
}
console.log(`\n校验通过${warnings.length ? `（${warnings.length} 条警告）` : ''}`);
