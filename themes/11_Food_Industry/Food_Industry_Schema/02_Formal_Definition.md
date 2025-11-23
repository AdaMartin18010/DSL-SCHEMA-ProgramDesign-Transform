# 食品行业Schema形式化定义

## 📑 目录

- [食品行业Schema形式化定义](#食品行业schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 食品信息Schema](#2-食品信息schema)
  - [3. 生产信息Schema](#3-生产信息schema)
  - [4. 追溯信息Schema](#4-追溯信息schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 食品信息完整性定理](#81-食品信息完整性定理)
    - [8.2 追溯链完整性定理](#82-追溯链完整性定理)

---

## 1. 形式化模型

**定义1（食品行业Schema）**：
食品行业Schema是一个四元组：

```text
Food_Industry_Schema = (Food_Info, Production_Info,
                       Traceability_Info, Safety_Info)
```

其中：

- `Food_Info`：食品信息Schema
- `Production_Info`：生产信息Schema
- `Traceability_Info`：追溯信息Schema
- `Safety_Info`：安全信息Schema

---

## 2. 食品信息Schema

**定义2（食品信息Schema）**：

```text
Food_Info_Schema = (Food_Basic_Info, Food_Composition,
                   Food_Packaging, Food_Shelf_Life)
```

**形式化DSL定义**：

```dsl
schema FoodInfo {
  food_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  gtin: String @pattern("^[0-9]{8,14}$") @required @unique
  food_name: String @max_length(200) @required

  food_basic_info: {
    food_category: Enum { Meat, Dairy, Vegetable, Fruit, Grain, Beverage, Other } @required
    food_type: String @max_length(100)
    brand_name: String @max_length(100)
    manufacturer: String @max_length(200) @required
    country_of_origin: String @length(2) @pattern("^[A-Z]{2}$")
    food_description: String @max_length(2000)
  } @required

  food_composition: {
    ingredients: List<String> @max_length(200) @required
    nutritional_info: {
      calories: Decimal @precision(6,2) @unit("kcal")
      protein: Decimal @precision(6,2) @unit("g")
      fat: Decimal @precision(6,2) @unit("g")
      carbohydrates: Decimal @precision(6,2) @unit("g")
      fiber: Decimal @precision(6,2) @unit("g")
      sugar: Decimal @precision(6,2) @unit("g")
      sodium: Decimal @precision(6,2) @unit("mg")
    }
    allergens: List<String> @max_length(100)
    additives: List<String> @max_length(100)
  } @required

  food_packaging: {
    packaging_type: Enum { Can, Bottle, Box, Bag, Other } @required
    packaging_material: String @max_length(100)
    packaging_size: String @max_length(50)
    packaging_weight: Decimal @precision(6,2) @unit("g")
    packaging_date: Date @format("YYYY-MM-DD")
  } @required

  food_shelf_life: {
    production_date: Date @format("YYYY-MM-DD") @required
    expiry_date: Date @format("YYYY-MM-DD") @required
    shelf_life_days: Integer @range(1, 3650) @unit("days")
    storage_conditions: String @max_length(200)
    best_before_date: Date @format("YYYY-MM-DD")
  } @required
} @standard("GS1")
```

---

## 3. 生产信息Schema

**定义3（生产信息Schema）**：

```text
Production_Info_Schema = (Production_Batch, Production_Process,
                         Production_Ingredients, Production_Environment)
```

**形式化DSL定义**：

```dsl
schema ProductionInfo {
  production_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  food_id: String @pattern("^[A-Z0-9]{20}$") @required
  batch_number: String @max_length(50) @required @unique

  production_batch: {
    batch_size: Integer @range(1, 999999) @required
    production_date: Date @format("YYYY-MM-DD") @required
    production_time: Time @format("HH:mm:ss")
    production_location: String @max_length(200) @required
    production_facility: String @max_length(200) @required
    production_line: String @max_length(50)
  } @required

  production_process: {
    process_steps: List<ProcessStep> {
      step_number: Integer @required
      step_name: String @max_length(100) @required
      step_description: String @max_length(500)
      equipment_id: String @max_length(50)
      operator: String @max_length(100)
      start_time: DateTime
      end_time: DateTime
      temperature: Decimal @precision(5,2) @unit("°C")
      humidity: Decimal @precision(5,2) @unit("%")
    } @required
    quality_checkpoints: List<QualityCheckpoint> {
      checkpoint_name: String @max_length(100) @required
      checkpoint_time: DateTime @required
      checkpoint_result: Enum { Pass, Fail, Pending } @required
      checkpoint_operator: String @max_length(100)
      checkpoint_notes: String @max_length(500)
    }
  } @required

  production_ingredients: {
    ingredients: List<Ingredient> {
      ingredient_name: String @max_length(200) @required
      ingredient_gtin: String @pattern("^[0-9]{8,14}$")
      supplier: String @max_length(200)
      supplier_gln: String @pattern("^[0-9]{13}$")
      batch_number: String @max_length(50)
      quantity: Decimal @precision(10,2) @required
      unit: String @max_length(20) @required
      receipt_date: Date @format("YYYY-MM-DD")
      expiry_date: Date @format("YYYY-MM-DD")
      quality_certificate: String @max_length(200)
    } @required
  } @required

  production_environment: {
    temperature: Decimal @precision(5,2) @unit("°C")
    humidity: Decimal @precision(5,2) @unit("%")
    air_quality: String @max_length(50)
    sanitation_status: Enum { Clean, Sanitized, Contaminated } @required
    sanitation_date: Date @format("YYYY-MM-DD")
    sanitation_operator: String @max_length(100)
  } @required
} @standard("ISO_22000")
```

---

## 4. 追溯信息Schema

**定义4（追溯信息Schema）**：

```text
Traceability_Info_Schema = (Traceability_Chain, Traceability_Event,
                            Traceability_Record)
```

**形式化DSL定义**：

```dsl
schema TraceabilityInfo {
  traceability_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  food_id: String @pattern("^[A-Z0-9]{20}$") @required
  batch_number: String @max_length(50) @required

  traceability_chain: {
    suppliers: List<Supplier> {
      supplier_name: String @max_length(200) @required
      supplier_gln: String @pattern("^[0-9]{13}$")
      supplier_role: Enum { IngredientSupplier, PackagingSupplier, Other } @required
      contact_info: String @max_length(500)
    } @required
    manufacturer: {
      manufacturer_name: String @max_length(200) @required
      manufacturer_gln: String @pattern("^[0-9]{13}$") @required
      production_facility: String @max_length(200) @required
      production_date: Date @format("YYYY-MM-DD") @required
    } @required
    distributors: List<Distributor> {
      distributor_name: String @max_length(200) @required
      distributor_gln: String @pattern("^[0-9]{13}$")
      distribution_center: String @max_length(200)
      receipt_date: Date @format("YYYY-MM-DD")
      dispatch_date: Date @format("YYYY-MM-DD")
    }
    retailers: List<Retailer> {
      retailer_name: String @max_length(200) @required
      retailer_gln: String @pattern("^[0-9]{13}$")
      store_location: String @max_length(200)
      receipt_date: Date @format("YYYY-MM-DD")
      sale_date: Date @format("YYYY-MM-DD")
    }
  } @required

  traceability_events: List<TraceabilityEvent> {
    event_id: String @pattern("^[A-Z0-9]{20}$") @required
    event_type: Enum { Production, Packaging, Storage, Transportation, Distribution, Sale, Recall } @required
    event_time: DateTime @required
    event_location: String @max_length(200) @required
    event_operator: String @max_length(100)
    event_description: String @max_length(500)
    event_data: JSON
  } @required

  traceability_records: List<TraceabilityRecord> {
    record_id: String @pattern("^[A-Z0-9]{20}$") @required
    record_type: Enum { Certificate, Inspection, Test, Audit } @required
    record_time: DateTime @required
    record_location: String @max_length(200)
    record_operator: String @max_length(100)
    record_result: Enum { Pass, Fail, Pending } @required
    record_document: String @max_length(500)
  }
} @standard("ISO_22005")
```

---

## 5. 类型系统

**定义5（食品行业数据类型）**：

```text
Food_Industry_Data_Type = Food_Info | Production_Info |
                          Traceability_Info | Safety_Info |
                          Traceability_Event | Traceability_Record
```

**基本类型定义**：

```dsl
type FoodComposition {
  ingredients: List<String> @required
  nutritional_info: NutritionalInfo
  allergens: List<String>
}

type ProductionBatch {
  batch_number: String @required
  production_date: Date @required
  production_location: String @required
}

type TraceabilityEvent {
  event_type: Enum { Production, Packaging, Storage, Transportation, Distribution, Sale, Recall } @required
  event_time: DateTime @required
  event_location: String @required
}
```

---

## 6. 约束规则

**约束1（食品信息完整性）**：

```text
∀ food ∈ Food_Info:
  food.food_id ≠ ∅
  ∧ food.gtin ≠ ∅
  ∧ food.food_name ≠ ∅
  ∧ validate_gtin(food.gtin)
  ∧ food.food_shelf_life.production_date < food.food_shelf_life.expiry_date
```

**约束2（生产信息完整性）**：

```text
∀ production ∈ Production_Info:
  production.production_id ≠ ∅
  ∧ production.batch_number ≠ ∅
  ∧ production.production_batch.production_date ≤ current_date()
  ∧ validate_production_process(production.production_process)
```

**约束3（追溯链完整性）**：

```text
∀ traceability ∈ Traceability_Info:
  traceability.traceability_id ≠ ∅
  ∧ traceability.traceability_chain.manufacturer ≠ ∅
  ∧ validate_traceability_chain(traceability.traceability_chain)
  ∧ validate_traceability_events(traceability.traceability_events)
```

---

## 7. 转换函数

**函数1（GS1到EPCIS转换）**：

```text
convert_GS1_to_EPCIS: GS1_Food_Info → EPCIS_Event
```

**函数2（EPCIS到GS1转换）**：

```text
convert_EPCIS_to_GS1: EPCIS_Event → GS1_Food_Info
```

**函数3（追溯链验证）**：

```text
validate_traceability_chain: Traceability_Info → Bool
```

---

## 8. 形式化定理

### 8.1 食品信息完整性定理

**定理1（食品信息完整性）**：

```text
∀ food ∈ Food_Info:
  validate_food_info(food)
  → food_info_integrity(food)
  ∧ gtin_uniqueness(food.gtin)
  ∧ shelf_life_validity(food.food_shelf_life)
```

### 8.2 追溯链完整性定理

**定理2（追溯链完整性）**：

```text
∀ traceability ∈ Traceability_Info:
  validate_traceability_chain(traceability.traceability_chain)
  → traceability_chain_completeness(traceability)
  ∧ event_sequence_validity(traceability.traceability_events)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
