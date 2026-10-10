# grit-lib: using Grit from Rust (v0.5.x)

The other half of Grit. Read this file when a task needs a **Rust program** to read or write a Git repository rather than run commands;
pure command-line tasks do not need it.

## Library or CLI?

| Situation | Choice |
| --- | --- |
| Version control from a terminal, or a script shelling out | The `grit` CLI (`--json`/`--filter`) |
| A Rust program/service reading objects, refs, the index, diffs, walking revisions, fetch/push | `grit-lib` |
| A capability the grit CLI lacks (stash, reflog, notes, fsck, worktree, …) | The library has APIs; command-line scenarios should use `git` for now (see [git-gaps.md](git-gaps.md)) |

## Adding the dependency

```toml
[dependencies]
grit-lib = "0.5.0"      # track the latest 0.5.x on crates.io
```

```bash
cargo add grit-lib
```

## Minimal example: open a repo and read HEAD

```rust
use grit_lib::objects::{parse_commit, ObjectKind};
use grit_lib::repo::Repository;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let repo = Repository::discover(None)?;                       // discover upward from the current directory
    let head = grit_lib::refs::resolve_ref(&repo.git_dir, "HEAD")?;
    let object = repo.odb.read(&head)?;
    if object.kind != ObjectKind::Commit {
        return Err("HEAD is not a commit".into());
    }
    let commit = parse_commit(&object.data)?;
    println!("{head}");
    println!("{}", commit.message.lines().next().unwrap_or(""));
    Ok(())
}
```

## Module map (find your entry point by task)

| Need | Module / type | Guide |
| --- | --- | --- |
| Discover/open repositories, git-dir vs work tree, config, error type | `Repository`, `Environment` | <https://grit-scm.com/docs/library/repository/index.md> |
| Read/write objects (blob/tree/commit), object ids and kinds | `Odb`, `ObjectId`, `ObjectKind` | <https://grit-scm.com/docs/library/objects/index.md> |
| Resolve HEAD, list branches/tags, update refs with reflog | `refs` | <https://grit-scm.com/docs/library/refs/index.md> |
| Read the index, stage paths, write a tree from the index | `Index` (staging) | <https://grit-scm.com/docs/library/staging/index.md> |
| Tree-to-tree and index-to-worktree diffs, blob patches | diff API | <https://grit-scm.com/docs/library/diff/index.md> |
| Revision parsing, rev-list, ranges (`A..B`), merge base | revwalk/revparse | <https://grit-scm.com/docs/library/revwalk/index.md> |
| ls-remote, fetch, push, credentials | network | <https://grit-scm.com/docs/library/network/index.md> |
| Pluggable object backends (custom ObjectStore) | OdbBuilder, odb_conformance | <https://grit-scm.com/docs/library/object-stores/index.md> |
| Several repositories in one process, explicit Environment, sinks, subprocess injection | embedding | <https://grit-scm.com/docs/library/embedding/index.md> |
| Full index of public modules and types | API map | <https://grit-scm.com/docs/library/api-map/index.md> |

Exhaustive reference: <https://docs.rs/grit-lib>.

## Embedding conventions (read before writing library code)

- **Explicit context**: time, randomness and environment (`HOME`, config discovery) are arguments or injectable providers — never hidden `std::env` reads deep in a call.
- **Typed APIs**: public surfaces take `ObjectId`, `RefName`, enums and newtypes, not unparsed strings; human-string parsing stays at the caller.
- **Errors**: the library uses `thiserror` enums with specific variants per failure mode; do not leak stringly "git stderr" shapes. Top-level programs may wrap with `anyhow`.
- **IO boundaries**: pass `&mut dyn Read/Write` / `AsRef<Path>` where streams matter; whole-repo operations should be swappable for temp dirs or in-memory backends in tests.
- **No global state, no printing from the library**, no `unwrap()/expect()` in the library; prefer `Option<T>` over sentinels.
- The library **never shells out** to `git` (the CLI may delegate only where hook/filter semantics require it, via injectable runners).
- On-disk formats and wire protocols must stay Git-compatible — that is the product's hard constraint.

## Practical notes

- Verified against v0.5.2; the crate is `grit-lib`, the CLI crate is `grit-cli` (the installed binary is `grit`).
- Repositories touched by the library interop fully with git: library changes are visible to the CLI and vice versa.

## Related sources

- Library guide overview: <https://grit-scm.com/docs/library/index.md>
- Quick start: <https://grit-scm.com/docs/library-quickstart/index.md>
- Contributing to the Grit project itself: read the repository's <https://github.com/gitbutlerapp/grit/blob/main/AGENTS.md> first (library-first, thin grit-cli, no GPL code in grit-lib, and other hard rules).
