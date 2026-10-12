# 何时使用 mock

只在**系统边界**上 mock：

- 外部 API（支付、邮件等）
- 数据库（视情况——优先用测试数据库）
- 时间/随机性
- 文件系统（视情况）

不要 mock：

- 你自己的类/模块
- 内部协作者
- 任何你能控制的东西

## 为可 mock 性做设计

在系统边界上，把接口设计得易于 mock：

**1. 使用依赖注入**

把外部依赖传进来，而不是在内部创建它们：

```typescript
// 容易 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 难以 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. 优先使用 SDK 风格的接口，而不是通用抓取函数**

为每个外部操作创建专门的函数，而不是一个带条件逻辑的通用函数：

```typescript
// 好：每个函数都能独立 mock
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// 坏：mock 需要在 mock 内部写条件逻辑
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK 方式意味着：
- 每个 mock 只返回一种特定形态
- 测试准备里没有条件逻辑
- 更容易看出一个测试跑到了哪些端点
- 每个端点都有类型安全
