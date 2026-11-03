#!/usr/bin/env node
// Print the version, download URLs and sha256 hashes of a project's Windows assets,
// without downloading the artifacts. GitHub computes the sha256 at upload time and
// exposes it as `digest`, so there is never a reason to fetch a 500 MB installer
// just to hash it.
//
// Usage:
//   node fetch-windows-assets.mjs <owner>/<repo> [tag]
//
// Examples:
//   node fetch-windows-assets.mjs liliMozi/openhanako
//   node fetch-windows-assets.mjs liliMozi/openhanako v0.450.0
//
// Environment:
//   GITHUB_TOKEN / GH_TOKEN   optional, raises the API rate limit and reaches private repos
//
// Output: tag, version (leading 'v' stripped), then name / url / size / sha256 / digest
// for every asset that looks like a Windows build. The sha256 is exactly what goes in
// the manifest's `hash` field.

const [repo, tag = 'latest'] = process.argv.slice(2);

if (!repo || !/^[^/\s]+\/[^/\s]+$/.test(repo)) {
  console.error('Usage: node fetch-windows-assets.mjs <owner>/<repo> [tag]');
  process.exit(1);
}

const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
const apiUrl =
  tag === 'latest'
    ? `https://api.github.com/repos/${repo}/releases/latest`
    : `https://api.github.com/repos/${repo}/releases/tags/${encodeURIComponent(tag)}`;

const headers = {
  'User-Agent': 'finch-scoop-skill',
  Accept: 'application/vnd.github+json',
};
if (token) headers.Authorization = `Bearer ${token}`;

const res = await fetch(apiUrl, { headers });
if (!res.ok) {
  console.error(`HTTP ${res.status} for ${apiUrl}`);
  console.error(await res.text());
  if (res.status === 403 || res.status === 429) {
    console.error('Rate limited. Set GITHUB_TOKEN (or run: scoop config gh_token <token>).');
  }
  process.exit(1);
}

const release = await res.json();
const tagName = release.tag_name ?? '';
const version = tagName.replace(/^v/i, '');

console.log(`Tag:        ${tagName}`);
console.log(`Version:    ${version}`);
console.log(`Pre-release:${release.prerelease ? ' yes' : ' no'}`);
console.log(`Published:  ${release.published_at}`);
console.log('');

// Windows builds show up as Windows-x64.zip, win64.7z, setup-x86.exe, ...
// Keep the filter loose and print the rest separately so nothing is silently dropped.
const winRe = /(windows|win(32|64)?|x64|arm64|x86|amd64)/i;
const archiveRe = /\.(exe|zip|msi|7z|tar\.gz|msix|appx)$/i;

const windows = [];
const others = [];

for (const asset of release.assets ?? []) {
  const entry = {
    name: asset.name,
    url: asset.browser_download_url,
    size: asset.size,
    digest: asset.digest ?? '',
    sha256: (asset.digest ?? '').replace(/^sha256:/, ''),
  };
  if (winRe.test(asset.name) || archiveRe.test(asset.name)) windows.push(entry);
  else others.push(entry);
}

if (windows.length === 0) {
  console.error('No Windows-looking assets matched. All assets:');
  for (const asset of release.assets ?? []) {
    console.error(`  - ${asset.name} (${asset.size} bytes)`);
  }
  process.exit(2);
}

for (const a of windows) {
  console.log(`Asset:  ${a.name}`);
  console.log(`  url:    ${a.url}`);
  console.log(`  size:   ${a.size} bytes`);
  console.log(`  sha256: ${a.sha256 || '<absent - compute with scripts/hashurl.ps1>'}`);
  if (a.digest && !a.digest.startsWith('sha256:')) {
    console.log(`  note:   GitHub reports ${a.digest}; Scoop needs sha256, compute it yourself`);
  }
  console.log('');
}

if (others.length) {
  console.log('Other assets (probably not what a Scoop manifest wants):');
  for (const a of others) console.log(`  - ${a.name}`);
}

console.log('Reminder: `url` uses the literal version; only `autoupdate.url` uses $version.');
