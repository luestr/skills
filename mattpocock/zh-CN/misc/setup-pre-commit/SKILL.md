---
name: setup-pre-commit
description: 在当前仓库中配置 Husky pre-commit 钩子，配合 lint-staged（Prettier）、类型检查和测试。当用户想添加 pre-commit 钩子（pre-commit hooks）、配置 Husky、设置 lint-staged，或添加提交时的格式化/类型检查/测试（commit-time formatting/typechecking/testing）时使用。
---

# 配置 pre-commit 钩子

## 会配置什么

- **Husky** pre-commit 钩子
- **lint-staged** 对所有已暂存文件运行 Prettier
- **Prettier** 配置（如果缺失）
- pre-commit 钩子里的 **typecheck** 和 **test** 脚本

## 步骤

### 1. 检测包管理器

检查 `package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）、`bun.lockb`（bun）。哪个存在就用哪个。无法判断时默认用 npm。

### 2. 安装依赖

以 devDependencies 安装：

```
husky lint-staged prettier
```

### 3. 初始化 Husky

```bash
npx husky init
```

这会创建 `.husky/` 目录，并把 `prepare: "husky"` 加入 package.json。

### 4. 创建 `.husky/pre-commit`

写入以下内容（Husky v9+ 不需要 shebang）：

```
npx lint-staged
npm run typecheck
npm run test
```

**按需调整**：把 `npm` 换成检测到的包管理器。如果仓库的 package.json 里没有 `typecheck` 或 `test` 脚本，就省略对应行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 创建 `.prettierrc`（如果缺失）

只有在不存在 Prettier 配置时才创建。使用以下默认值：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. 验证

- [ ] `.husky/pre-commit` 存在且可执行
- [ ] `.lintstagedrc` 存在
- [ ] package.json 中的 `prepare` 脚本为 `"husky"`
- [ ] `prettier` 配置存在
- [ ] 运行 `npx lint-staged` 验证它能正常工作

### 8. 提交

暂存所有已改动/新建的文件，并用这条提交信息提交：`Add pre-commit hooks (husky + lint-staged + prettier)`

这次提交会走一遍新装的 pre-commit 钩子：这是对一切是否正常的一次很好的冒烟测试。

## 说明

- Husky v9+ 的钩子文件不需要 shebang
- `prettier --ignore-unknown` 会跳过 Prettier 无法解析的文件（图片等）
- pre-commit 先运行 lint-staged（快，只针对已暂存文件），然后运行完整的类型检查和测试
