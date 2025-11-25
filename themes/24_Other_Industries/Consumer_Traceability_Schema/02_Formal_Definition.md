# 消费者追溯Schema形式化定义

## 📑 目录

- [消费者追溯Schema形式化定义](#消费者追溯schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 产品信息Schema](#2-产品信息schema)
  - [3. 追溯链Schema](#3-追溯链schema)
  - [4. 消费者查询Schema](#4-消费者查询schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)

---

## 1. 形式化模型

**定义1（消费者追溯Schema）**：
消费者追溯Schema是一个五元组：

```text
Consumer_Traceability_Schema = (Product_Info, Traceability_Chain,
                               Consumer_Query, Verification,
                               Recall_Management)
```

---

## 2. 产品信息Schema

**定义2（产品信息Schema）**：

```dsl
schema ProductInfo {
  product_id: String @required @unique
  gtin: String @pattern("^[0-9]{8,14}$") @required @unique
  product_name: String @max_length(200) @required
  batch_number: String @max_length(50) @required
  production_date: Date @format("YYYY-MM-DD") @required
} @standard("GS1")
```

---

## 3. 追溯链Schema

**定义3（追溯链Schema）**：

```dsl
schema TraceabilityChain {
  chain_id: String @required @unique
  product_id: String @required
  chain_events: List<TraceabilityEvent> @required
  chain_status: Enum { Complete, Incomplete } @required
} @standard("EPCIS")
```

---

## 4. 消费者查询Schema

**定义4（消费者查询Schema）**：

```dsl
schema ConsumerQuery {
  query_id: String @required @unique
  product_id: String @required
  query_type: Enum { Traceability, Recall, Quality } @required
  query_time: DateTime @format("ISO8601") @required
  query_result: Map<String, Any>
} @standard("GS1")
```

---

## 5. 类型系统

**定义5（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date, Enum, List, Map, Object}
```

---

## 6. 约束规则

**定义6（约束规则）**：

1. **唯一性约束**：`product_id`、`chain_id`、`query_id`必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
