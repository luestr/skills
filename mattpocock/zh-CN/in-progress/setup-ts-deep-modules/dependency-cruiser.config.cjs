// @ts-check
// 为 dependency-cruiser 提供深模块约束。
//
// 包根目录下的每个包都是一个深模块（DEEP MODULE）：小接口背后承载大量
// 行为。一个包的公共表面（PUBLIC SURFACE）是它的入口文件（ENTRY POINTS）：
// 位于包根目录的文件。实现放在子目录（SUBFOLDERS）里，是私有的
// （按约定，`lib/` 放实现、`tests/` 放测试，不过任何子目录都是私有的）。
// 一个包可以暴露多个小入口文件（index.ts、client.ts、server.ts……）；
// 优先这样做，而不是用一个巨大的桶文件 index。
//
// 这里唯一需要你修改的地方就是 PACKAGES_ROOT。

/** 包所在的位置。每个包占一个直接子目录（平铺，不嵌套）。 */
const PACKAGES_ROOT = "src/packages";

// --- 派生模式（无需修改） ---------------------------------------------------
const R = PACKAGES_ROOT;
/**
 * 包的私有内部：包内子目录里的任何嵌套内容。
 * 包的根目录文件是它的入口文件，不在此匹配范围内：
 * 它们仍然可以从外部导入。
 */
const PACKAGE_INTERNALS = `^${R}/[^/]+/[^/]+/`;

/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "entrypoint-boundary-from-app",
      comment:
        "应用/根目录代码可以导入一个包的入口文件（它的根目录文件），但不能导入其子目录里的任何东西。",
      severity: "error",
      from: { pathNot: `^${R}/` }, // 导入方不在任何包内
      to: { path: PACKAGE_INTERNALS },
    },
    {
      name: "entrypoint-boundary-across-packages",
      comment:
        "包自己的文件之间可以自由互相导入，但访问其他包只能经由它们的入口文件，绝不能访问其内部。",
      severity: "error",
      // 导入方位于某个包内（$1），但不是测试文件
      from: { path: `^${R}/([^/]+)/`, pathNot: `^${R}/[^/]+/tests/` },
      to: {
        path: PACKAGE_INTERNALS,
        pathNot: `^${R}/$1/`, // 同一个包 → 包内自由
      },
    },
    {
      name: "tests-through-entrypoints",
      comment:
        "包的测试和其他代码一样经由入口文件来检验它：可以导入任何包的入口文件和自己的 tests/ 测试夹具，但绝不能导入任何包的内部，连自己的也不行。",
      severity: "error",
      from: { path: `^${R}/([^/]+)/tests/` }, // 一个测试文件，位于包 $1 内
      to: {
        path: PACKAGE_INTERNALS,
        pathNot: `^${R}/$1/tests/`, // 自己的 tests/ 测试夹具 → 允许
      },
    },
    {
      name: "tests-folder-is-private",
      comment:
        "包的 tests/ 目录只能从测试中访问：其他任何代码都不得导入其中的测试夹具。",
      severity: "error",
      from: { pathNot: `^${R}/[^/]+/tests/` }, // 导入方本身不是测试
      to: { path: `^${R}/[^/]+/tests/` },
    },
    {
      name: "no-circular",
      comment: "不允许依赖环。如果想让包之外允许存在依赖环，把范围限定到 `^${R}/`。",
      severity: "error",
      from: {},
      to: { circular: true },
    },

    // --- 分层（可选，默认关闭） -----------------------------------------------
    // 接口隐藏控制的是你怎样导入（经由入口文件）。
    // 分层控制的是哪些包可以依赖哪些包。在这里添加你自己的规则，例如：
    //
    // {
    //   name: "ui-may-not-depend-on-billing",
    //   severity: "error",
    //   from: { path: `^${R}/ui/` },
    //   to:   { path: `^${R}/billing/` },
    // },
  ],
  options: {
    doNotFollow: { path: "node_modules" },
    tsConfig: { fileName: "tsconfig.json" },
    enhancedResolveOptions: {
      extensions: [".ts", ".tsx", ".js", ".jsx", ".json"],
    },
  },
};
