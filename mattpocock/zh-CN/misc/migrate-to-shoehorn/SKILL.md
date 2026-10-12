---
name: migrate-to-shoehorn
description: 把测试文件从 `as` 类型断言迁移到 @total-typescript/shoehorn。当用户提到 shoehorn、想在测试中替换 `as`，或需要部分测试数据（partial test data）时使用。
---

# 迁移到 Shoehorn

## 为什么用 shoehorn？

`shoehorn` 让你在测试中传入部分数据，同时让 TypeScript 满意。它用类型安全的替代方案取代 `as` 断言。

**仅限测试代码。** 绝不要在生产代码中使用 shoehorn。

测试里用 `as` 的问题：

- 被训练成不使用它
- 必须手动指定目标类型
- 对故意写错的数据使用双重 as（`as unknown as Type`）

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 大对象，只需少量属性

之前：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...还有 20 个属性
};

it("gets user by id", () => {
  // 只关心 body.id，却必须伪造整个 Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...伪造全部 20 个属性
  });
});
```

之后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

之前：

```ts
getUser({ body: { id: "123" } } as Request);
```

之后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

之前：

```ts
getUser({ body: { id: 123 } } as unknown as Request); // 故意写错类型
```

之后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 各自的适用场景

| 函数            | 适用场景                                     |
| --------------- | -------------------------------------------- |
| `fromPartial()` | 传入仍能通过类型检查的部分数据               |
| `fromAny()`     | 传入故意写错的数据（保留自动补全）           |
| `fromExact()`   | 强制传入完整对象（之后再换回 fromPartial）   |

## 工作流程

1. **收集需求** —— 询问用户：
   - 哪些测试文件里的 `as` 断言造成了问题？
   - 他们是否在处理只有部分属性重要的大对象？
   - 他们是否需要为错误测试传入故意写错的数据？

2. **安装并迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 查找带 `as` 断言的测试文件：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 把 `as Type` 替换为 `fromPartial()`
   - [ ] 把 `as unknown as Type` 替换为 `fromAny()`
   - [ ] 添加来自 `@total-typescript/shoehorn` 的导入
   - [ ] 运行类型检查以验证
