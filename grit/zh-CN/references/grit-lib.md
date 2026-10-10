# grit-lib：在 Rust 中程序化使用 Grit（v0.5.x）

CLI 之外的另一半。当任务需要用 **Rust 程序**读写 Git 仓库（而不是敲命令）时用本文件；
纯命令行任务不需要读它。

## 何时用库、何时用 CLI

| 场景 | 选择 |
| --- | --- |
| 终端里做版本控制、脚本里调命令 | `grit` CLI（`--json`/`--filter`） |
| Rust 程序/服务内部读对象、refs、索引、diff、revision walk、fetch/push | `grit-lib` |
| 想要一个 `grit` 没有的 CLI 能力（stash、reflog、notes、fsck、worktree…） | 库里有 API；命令行场景先用 `git`（见 [git-gaps.md](git-gaps.md)） |

## 引入依赖

```toml
[dependencies]
grit-lib = "0.5.0"      # 以 crates.io 最新 0.5.x 为准
```

```bash
cargo add grit-lib
```

## 最小示例：打开仓库并读 HEAD

```rust
use grit_lib::objects::{parse_commit, ObjectKind};
use grit_lib::repo::Repository;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let repo = Repository::discover(None)?;                       // 从当前目录向上发现仓库
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

## 模块地图（按任务找入口）

| 需求 | 模块 / 类型 | 指南 |
| --- | --- | --- |
| 发现/打开仓库、读 git-dir 与 work tree、加载配置、错误类型 | `Repository`、`Environment` | <https://grit-scm.com/docs/library/repository/index.md> |
| 读/写对象（blob/tree/commit）、object id 与 kind | `Odb`、`ObjectId`、`ObjectKind` | <https://grit-scm.com/docs/library/objects/index.md> |
| 解析 HEAD、列分支/标签、更新 refs 与 reflog | `refs` | <https://grit-scm.com/docs/library/refs/index.md> |
| 读索引、暂存路径、由索引写 tree | `Index`（staging） | <https://grit-scm.com/docs/library/staging/index.md> |
| tree 间 / 索引-工作区 diff、blob patch | diff API | <https://grit-scm.com/docs/library/diff/index.md> |
| revision 解析、rev-list、范围 `A..B`、merge base | revwalk/revparse | <https://grit-scm.com/docs/library/revwalk/index.md> |
| ls-remote、fetch、push、凭据 | network | <https://grit-scm.com/docs/library/network/index.md> |
| 可插拔对象后端（自定义 ObjectStore） | OdbBuilder、odb_conformance | <https://grit-scm.com/docs/library/object-stores/index.md> |
| 一进程内多仓库、显式环境、输出 sink、子进程注入 | embedding | <https://grit-scm.com/docs/library/embedding/index.md> |
| 公共 API 全索引 | API map | <https://grit-scm.com/docs/library/api-map/index.md> |

exhaustive 参考：<https://docs.rs/grit-lib>。

## 嵌入约定（写库代码前先读，避免反模式）

- **显式上下文**：时间、随机性、环境（`HOME`、配置发现）都作为参数或可注入 provider，不要藏在深层调用里读 `std::env`。
- **类型化 API**：公共接口收 `ObjectId`、`RefName`、枚举等，不收未解析的字符串；人类可读字符串的解析留在调用方。
- **错误**：库用 `thiserror` 枚举，按失败模式分变体；不要在库层拼「git stderr」风格字符串。顶层程序可用 `anyhow` 包装。
- **IO 边界**：流式场景传 `&mut dyn Read/Write`、`AsRef<Path>`；整仓操作让测试可用临时目录/内存后端替换。
- **无全局状态、库不打印**、不在库里 `unwrap()/expect()`；`Option<T>` 优于哨兵值。
- 库**不 shell out** 到 `git`（CLI 只允许在钩子/过滤器语义必须时通过可注入 runner 委托）。
- 磁盘格式与 wire protocol 必须与 Git 兼容——这是产品的硬约束。

## 实测提示

- 已在 v0.5.2 实测验证；crate 名 `grit-lib`，CLI crate 名 `grit-cli`（安装后二进制是 `grit`）。
- 克隆/初始化后的仓库与 git 完全互通，库改完 CLI 立刻可见，反之亦然。

## 相关来源

- 库指南总览：<https://grit-scm.com/docs/library/index.md>
- 快速开始：<https://grit-scm.com/docs/library-quickstart/index.md>
- 想给 Grit 项目本身贡献代码：先读仓库 <https://github.com/gitbutlerapp/grit/blob/main/AGENTS.md>（库优先、grit-cli 保持薄壳、无 GPL 代码进入 grit-lib 等硬规则）。
