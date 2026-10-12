---
name: setup-ts-deep-modules
description: 把 dependency-cruiser 接入 TypeScript 仓库，让每个包都成为深模块，实现藏在子目录中，只能经由包的入口文件访问。用户手动调用。
disable-model-invocation: true
---

# 配置 TS 深模块

让这个仓库里的每个包都成为**深模块**：小接口背后承载大量行为。一个包的公共表面是它的**入口文件（entry point）**（位于包根目录的文件），子目录中的一切都是隐藏的。本技能会安装 [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) 以及让入口文件成为唯一入口的规则，然后验证这些规则确实能拦下违规。

关于相关词汇（深模块、接口、接缝、深度），用 Skill 工具调用 “codebase-design”，并全程使用它的语言。

## 这里强制的形态

```
src/packages/
  <name>/
    index.ts        ← 一个入口文件（公共）。从外部导入它。
    client.ts       ← 另一个入口文件。包可以暴露多个入口。
    lib/            ← 实现：对外隐藏，内部文件可以互相导入。
    tests/          ← 就近聚合的测试与测试夹具（属于子目录，因此是私有的）。
```

公共表面是包的**根目录文件**，而不是某个指定的 `index.ts`。按约定，实现放在 `lib/`，测试放在 `tests/`，让每个包都拥有相同的双目录形态。不过规则本身是通用的：*任何*子目录里的*任何东西*都是私有的，所以你永远不需要为了新增目录而扩展配置。

四条规则，全部为 `error`：

1. **入口文件边界**：包外部的代码（应用代码或另一个包）只能导入该包的入口文件（它的根目录文件），永远不能导入其子目录中的任何东西。
2. **包内自由**：一个包自己的文件之间可以自由互相导入。
3. **测试经由入口文件**：`<pkg>/tests/` 下的文件可以导入任何包的入口文件以及自己 `tests/` 里的测试夹具，但绝不能导入任何包的子目录内部（连自己的也不行）。跨包的集成测试没问题；深度导入不行。
4. **无环**：不允许依赖环。

**用入口文件，不要用桶文件（barrel）。** 因为公共表面是*每一个*根目录文件，所以一个包可以暴露多个小入口文件（`index.ts`、`client.ts`、`server.ts`），而不必把所有东西都汇聚到一个巨大的 `index.ts` 里。不鼓励用桶文件再导出整棵子树；保持入口文件小巧，把实现藏在子目录里。

分层（哪些包可以依赖哪些包）是*另一个*关注点，配置里以注释形式留了一个占位模板，供这个仓库自行填写。

## 步骤

### 1. 检测环境

- **包管理器**：`pnpm-lock.yaml` → pnpm，`yarn.lock` → yarn，`bun.lockb` → bun，否则 npm。下面每条命令都按它来写（`pnpm`/`yarn`/`npm run`/`bunx`）。
- **包根目录**：如果存在 `src/`，用 `src/packages`，否则用 `packages`。如果仓库已有另一套显而易见的约定，与用户确认这一选择。
- **已有配置**：检查是否存在 `.dependency-cruiser.*` 文件。如果存在，**不要**覆盖它：把四条规则和选项合并进去，并告诉用户你添加了什么。

**完成判据：** 包管理器、包根目录和已有配置的状态都已查明。

### 2. 安装 dependency-cruiser

用检测到的包管理器把 `dependency-cruiser` 安装为 devDependency。

**完成判据：** `dependency-cruiser` 出现在 `devDependencies` 中。

### 3. 编写配置

把 [`dependency-cruiser.config.cjs`](./dependency-cruiser.config.cjs) 复制到仓库根目录，命名为 `.dependency-cruiser.cjs`。把 `PACKAGES_ROOT` 设为第 1 步检测到的根目录。这些规则基于路径深度、不关心扩展名，所以其他内容都不需要调整。

**完成判据：** `.dependency-cruiser.cjs` 已存在且 `PACKAGES_ROOT` 正确，四条 forbidden 规则都在。

### 4. 接入检查流程

- 添加一个 `lint:boundaries` 脚本：`depcruise <packages-root>`（或 `depcruise src`）。
- 把它并入仓库的总检查命令，也就是已经在跑 typecheck 的那个（例如 `check` / `ci` / `validate` 脚本）。**不要**改动 `tsconfig`，也不要添加路径别名。
- 如果没有总检查脚本，就添加 `lint:boundaries`，并告诉用户把它纳入 CI。

**完成判据：** `lint:boundaries` 已存在，并与 typecheck 在同一条命令中运行。

### 5. 搭建示例包

创建一个会提交进仓库的 `<packages-root>/example/`，作为可供照抄的模板：

- `index.ts` 是一个入口文件。导出一个函数，该函数委托给内部文件（这样包肉眼可见是*深*的，而不是透传）。
- `lib/impl.ts`：位于**子目录**中的内部文件，由 `index.ts` 导入，外部无法访问。
- `tests/example.test.ts` **只**导入 `../index`（一个入口文件），并针对这个公共函数做断言。

告诉用户这是一个起步模板，可以复制也可以删除。

**完成判据：** 示例包已存在，通过根目录的入口文件暴露其行为，并把 `impl` 藏在子目录中。

### 6. 验证规则真的会拦截

这是整个技能的完成判据：一份在违规时不会失败的配置毫无价值。

1. 运行 `lint:boundaries`。在干净的示例上它必须**通过**。
2. 临时给 `tests/example.test.ts` 加一个深度导入（例如 `import { thing } from "../lib/impl"`）。再次运行 `lint:boundaries`；它必须因 `tests-through-entrypoints` 而**失败**。
3. 还原这个深度导入。再运行一次，必须**通过**。

**完成判据：** 你已经观察到通过，然后因深度导入而失败，接着再次通过。如果第 2 步没有失败，说明规则没有正确接入，完成前必须修好。

### 7. 记录约定

在**包目录里**写一份 `README.md`（`<packages-root>/README.md`，与它所管辖的各个包并排），内容涵盖：`src/packages/<name>/` 的目录结构（入口文件在根目录、`lib/` 放实现、`tests/` 放测试）、“只能经由包的入口文件（它的根目录文件）导入”，以及如何运行 `lint:boundaries`。明确**劝阻桶文件**：暴露多个小入口文件，而不是通过一个 index 再导出整棵子树。内容保持精简：照抄用的代码片段，加上四条规则，每条一段。

然后从仓库的 Agent 指令文件（`CLAUDE.md`，如果存在；否则 `AGENTS.md`，两者都不存在就创建 `AGENTS.md`）里加一条指向它的**上下文指针**。一行就够了，例如 `Packages are deep modules: see [src/packages/README.md](./src/packages/README.md) before adding or importing one.` 正是这一点让 Agent 主动发现边界规则，而不是一头撞上去。

**完成判据：** `<packages-root>/README.md` 已存在并劝阻桶文件，且仓库的 `CLAUDE.md`/`AGENTS.md` 已链接到它。

## 备注

- 配置里的 `$1` 反向引用（dependency-cruiser 的分组匹配）让一个包能访问自己的内部，而外部代码不能。不要把它们拆平成按包分开写的规则。
- 公共还是私有由**深度**决定：包的根目录文件是入口文件；子目录里的任何东西都是私有的。约定俗成的子目录是 `lib/`（实现）和 `tests/`，但规则并没有把它们写死：任何子目录都是私有的，所以新增目录永远不需要改配置。新增一个入口文件就是新增一个根目录文件（不要桶文件）。
- 包是**平铺**的：根目录下只有一层直接子项。包的内部可以随意嵌套到任意深度；但一个包里不能再包含另一个包。
- 使用 `.cjs`（而不是 `.js`），这样即使仓库是 `"type": "module"`，配置里的 `module.exports` 也能正常工作。
