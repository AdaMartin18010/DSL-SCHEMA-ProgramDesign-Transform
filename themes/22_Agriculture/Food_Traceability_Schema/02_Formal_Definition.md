# 农产品追溯Schema形式化定义

## 📑 目录

- [农产品追溯Schema形式化定义](#农产品追溯schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 产品信息Schema](#2-产品信息schema)
  - [3. 生产信息Schema](#3-生产信息schema)
  - [4. 追溯信息Schema](#4-追溯信息schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
    - [7.1 GS1到EPCIS转换](#71-gs1到epcis转换)
    - [7.2 EPCIS到ISO 22005转换](#72-epcis到iso-22005转换)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 追溯链完整性定理](#81-追溯链完整性定理)

---

## 1. 形式化模型

**定义1（农产品追溯Schema）**：
农产品追溯Schema是一个五元组：

```text
Food_Traceability_Schema = (Product_Info, Production_Info,
                           Processing_Info, Distribution_Info,
                           Retail_Info)
```

其中：

- `Product_Info`：产品信息Schema
- `Production_Info`：生产信息Schema
- `Processing_Info`：加工信息Schema
- `Distribution_Info`：流通信息Schema
- `Retail_Info`：零售信息Schema

---

## 2. 产品信息Schema

**定义2（产品信息Schema）**：

```text
Product_Info_Schema = (Basic_Info, Identification, Classification)
```

**形式化DSL定义**：

```dsl
schema ProductInfo {
  product_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  gtin: String @pattern("^[0-9]{8,14}$") @required @unique
  product_name: String @max_length(200) @required

  basic_info: {
    product_type: Enum { Grain, Vegetable, Fruit, Livestock, Poultry, Other } @required
    category: String @max_length(100)
    origin: String @max_length(200) @required
  } @required

  identification: {
    batch_number: String @max_length(50) @required
    production_date: Date @format("YYYY-MM-DD") @required
    expiry_date: Date @format("YYYY-MM-DD")
  } @required
} @standard("GS1")
```

---

## 3. 生产信息Schema

**定义3（生产信息Schema）**：

```text
Production_Info_Schema = (Farm_Info, Production_Process, Quality_Info)
```

**形式化DSL定义**：

```dsl
schema ProductionInfo {
  production_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  product_id: String @required
  farm_id: String @required

  farm_info: {
    farm_name: String @max_length(200) @required
    farm_location: {
      latitude: Decimal @range(-90.0, 90.0) @required
      longitude: Decimal @range(-180.0, 180.0) @required
    } @required
    certification: List<String> @max_length(100)
  } @required

  production_process: {
    planting_date: Date @format("YYYY-MM-DD")
    harvest_date: Date @format("YYYY-MM-DD") @required
    production_method: Enum { Organic, Conventional, Hydroponic } @required
 50
  } @required
} @standard("ISO_22005")
```

---

## 4. 追溯信息Schema

**定义4（追溯信息Schema）**：

```text
Traceability_Info_Schema = (Traceability_Chain, Traceability_Event, Verification)
```

**形式化DSL定义**：

```dsl
schema TraceabilityInfo {
  traceability_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  product_id: String @required

  traceability_chain: {
    chain_id: String @required
    chain_events: List<TraceabilityEvent> @required
  } @required

  traceability_event: {
    event_id: String @required
    event_type: Enum { Production, Processing, Transportation, Storage, Retail } @required
    event_time: DateTime @format("ISO8601") @required
    event_location: String @max_length(200) @required
  } @required
} @standard("EPCIS")
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

1. **唯一性约束**：`product_id`、`production_id`、`traceability_id`必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **追溯链完整性**：追溯链必须包含从生产到零售的所有环节

---

## 7. 转换函数

**定义7（转换函数）**：

### 7.1 GS1到EPCIS转换

```text
convert_GS1_to_EPCIS: GS1_Data → EPCIS_Data
```

### 7.2 EPCIS到ISO 22005转换

```text
convert_EPCIS_to_ISO22005: EPCIS_Data → ISO22005_Data
```

---

## 8. 形式化定理

### 8.1 追溯链完整性定理

**定理1（追溯链完整性）**：
对于任意农产品`p`，如果`p`的追溯链完整，则可以从生产追溯到零售。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
