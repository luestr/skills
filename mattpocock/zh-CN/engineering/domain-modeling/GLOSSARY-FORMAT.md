# GLOSSARY.md 格式

## 结构

```md
# {上下文名称}

{用一两句话描述这个上下文是什么、为什么存在。}

## 语言

**Order**:
{用一两句话描述该术语}
_Avoid_: Purchase, transaction

**Invoice**:
交付后向客户发出的付款请求。
_Avoid_: Bill, payment request

**Customer**:
下单的人或组织。
_Avoid_: Client, buyer, account
```

## 规则

- **要有主见。** 同一个概念有多个词时，挑一个最好的，其余列在 `_Avoid_` 下。
- **定义要紧凑。** 最多一两句话。定义它是什么，而不是它做什么。
- **只收录本项目上下文特有的术语。** 通用编程概念（超时、错误类型、工具函数模式）不属于这里，即使项目大量使用它们。添加术语前先问：这是本上下文独有的概念，还是通用编程概念？只有前者才该收录。
- **自然形成聚类时，把术语分到子标题下。** 如果所有术语都属于同一个紧密相关的领域，平铺列表即可。

## 单上下文与多上下文仓库

**单上下文（多数仓库）：** 仓库根目录一个 `GLOSSARY.md`。

**多上下文：** 仓库根目录的 `GLOSSARY-MAP.md` 列出各个上下文、它们的位置，以及它们之间的关系：

```md
# 术语表映射

## 上下文

- [Ordering](./src/ordering/GLOSSARY.md)：接收并跟踪客户订单
- [Billing](./src/billing/GLOSSARY.md)：生成发票并处理付款
- [Fulfillment](./src/fulfillment/GLOSSARY.md)：管理仓库拣货与发货

## 关系

- **Ordering → Fulfillment**：Ordering 发出 `OrderPlaced` 事件；Fulfillment 消费这些事件以开始拣货
- **Fulfillment → Billing**：Fulfillment 发出 `ShipmentDispatched` 事件；Billing 消费这些事件以生成发票
- **Ordering ↔ Billing**：`CustomerId` 和 `Money` 的共享类型
```

技能会推断适用哪种结构：

- 如果存在 `GLOSSARY-MAP.md`，读它来找到各个上下文
- 如果只有根目录的 `GLOSSARY.md`，即单上下文
- 如果两者都不存在，就在第一个术语敲定时按需创建根目录的 `GLOSSARY.md`

存在多个上下文时，推断当前话题属于哪一个。如果不明确，就问。
