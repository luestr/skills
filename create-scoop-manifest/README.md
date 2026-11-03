# create-scoop-manifest

A bilingual Agent Skill for creating and maintaining **Scoop bucket manifests** on Windows — plus the install, verification, health-check and troubleshooting work that surrounds them.

| Language | Skill directory | Metadata |
|---|---|---|
| 简体中文 | [`zh-CN/create-scoop-manifest/`](zh-CN/create-scoop-manifest/) | `metadata.language: zh-CN` |
| English (US) | [`en-US/create-scoop-manifest/`](en-US/create-scoop-manifest/) | `metadata.language: en-US` |

Each language directory is a **standalone, independently installable skill**. Install one, or both — you never need to download both, and neither references files outside its own directory.

## What it does

Scoop installs apps from `bucket/<appname>.json`. This skill covers the whole lifecycle of that file:

- **§B Authoring (primary)** — probe an upstream source, get version/URL/sha256 without downloading the artifact, pick the right install shape (portable zip / NSIS / MSI / InnoSetup), write the manifest, wire up `checkver` + `autoupdate`, and verify it end to end.
- **§C Maintenance (primary)** — audit a bucket, repair outdated or hash-mismatched manifests, and reconcile tooling against `ScoopInstaller/BucketTemplate`.
- **§A Using Scoop (supporting)** — the install/update/reset/config knowledge you need in order to test what you wrote.

## Layout

```text
create-scoop-manifest/
├── zh-CN/
│   └── create-scoop-manifest/
│       ├── SKILL.md
│       ├── references/          8 documents, loaded on demand
│       ├── scripts/             5 executable helpers
│       └── assets/              manifest template
├── en-US/
│   └── create-scoop-manifest/
│       └── …                    same structure, same scripts
└── README.md
```

## Scripts

Functional resources are identical in both languages (pure ASCII, no localized strings):

| Script | Purpose |
|---|---|
| `scripts/fetch-windows-assets.ps1` | Version, URLs and sha256 straight from the GitHub Release API — no artifact download |
| `scripts/fetch-windows-assets.mjs` | Same thing for environments that have node |
| `scripts/hashurl.ps1` | SHA256 for one or more URLs; strips Scoop's `#/...` fragment and sends Scoop's user agent |
| `scripts/manifest-lint.ps1` | Offline static checks: required fields, hash shape, architecture pairing, `autoupdate.url` reproduction, named-capture-group casing, deprecated fields, field ordering |
| `scripts/template-drift.ps1` | Read-only comparison against `ScoopInstaller/BucketTemplate` |

## Install

Copy the language directory you want into your agent's skill path, for example:

```powershell
# project-scoped
Copy-Item -Recurse .\zh-CN\create-scoop-manifest <your-project>\.finch\skills\

# or personal / home-scoped
Copy-Item -Recurse .\en-US\create-scoop-manifest ~\.finch\skills\
```

Confirm your agent discovers `SKILL.md` at the root of the installed directory — some agents do not descend into nested language folders automatically.

## Ground truth

Field definitions, `checkver` strategies and hash modes follow the official [Scoop](https://github.com/ScoopInstaller/Scoop) and [Install](https://github.com/ScoopInstaller/Install) repositories and the [Scoop wiki](https://github.com/ScoopInstaller/Scoop/wiki).

Where the wiki disagrees with the implementation, **the implementation wins**, and the documents say so explicitly. Several long-standing wiki claims were corrected against Scoop v0.6.0 during authoring — for example:

- A bare `.exe` URL is neither extracted nor executed (`Invoke-Installer` short-circuits unless `installer.file` or `installer.args` is set).
- The hook-scope configuration object is `$scoopConfig`; `$cfg` and `$cfgpath` do not exist.
- `autoupdate.hash.mode` has no `download` value — download-and-hash is the automatic fallback, not a mode.
- An `autoupdate` block carrying `hash` but no `url` makes `checkver -u` overwrite a correct hash with `""` and exit 0.

Claims marked "verified by experiment" in the documents were reproduced on a real Scoop installation, not inferred from reading source.

## License

MIT. Include the license text at the repository level — skill directories intentionally carry no `LICENSE` or `.gitignore` of their own, since neither plays any part in running the skill and both would only clutter the install artifact.
