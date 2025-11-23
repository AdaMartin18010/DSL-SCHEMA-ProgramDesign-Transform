# GS1 Schema形式化定义

## 📑 目录

- [GS1 Schema形式化定义](#gs1-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. GTIN Schema](#2-gtin-schema)
  - [3. GLN Schema](#3-gln-schema)
  - [4. SSCC Schema](#4-sscc-schema)
  - [5. EPCIS Schema](#5-epcis-schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)

---

## 1. 形式化模型

**定义1（GS1 Schema）**：
GS1 Schema是一个四元组：

```text
GS1_Schema = (GTIN, GLN, SSCC, EPCIS)
```

其中：

- `GTIN`：全球贸易项目代码Schema
- `GLN`：全球位置码Schema
- `SSCC`：系列货运包装箱代码Schema
- `EPCIS`：EPC信息服务Schema

---

## 2. GTIN Schema

**定义2（GTIN Schema）**：

```text
GTIN_Schema = (GTIN8 | GTIN12 | GTIN13 | GTIN14)
```

**形式化DSL定义**：

```dsl
schema GTIN {
  gtin_type: Enum { GTIN8, GTIN12, GTIN13, GTIN14 } @required

  // GTIN-8（8位）
  gtin8: Optional<GTIN8] {
    company_prefix: String @pattern("^[0-9]{4,7}$") @required
    item_reference: String @pattern("^[0-9]{1,4}$") @required
    check_digit: String @pattern("^[0-9]$") @required @computed("calculate_check_digit(company_prefix + item_reference)")
  }

  // GTIN-12（UPC，12位）
  gtin12: Optional<GTIN12] {
    company_prefix: String @pattern("^[0-9]{6,10}$") @required
    item_reference: String @pattern("^[0-9]{1,5}$") @required
    check_digit: String @pattern("^[0-9]$") @required @computed("calculate_check_digit(company_prefix + item_reference)")
  }

  // GTIN-13（EAN-13，13位）
  gtin13: Optional<GTIN13] {
    company_prefix: String @pattern("^[0-9]{7,9}$") @required
    item_reference: String @pattern("^[0-9]{1,5}$") @required
    check_digit: String @pattern("^[0-9]$") @required @computed("calculate_check_digit(company_prefix + item_reference)")
  }

  // GTIN-14（ITF-14，14位）
  gtin14: Optional<GTIN14] {
    indicator_digit: String @pattern("^[0-9]$") @required
    company_prefix: String @pattern("^[0-9]{7,9}$") @required
    item_reference: String @pattern("^[0-9]{1,5}$") @required
    check_digit: String @pattern("^[0-9]$") @required @computed("calculate_check_digit(indicator_digit + company_prefix + item_reference)")
  }

  product_information: ProductInformation {
    product_name: String @required
    brand_name: Optional<String]
    product_category: Optional<String]
    unit_of_measure: Optional<String]
    net_weight: Optional<Decimal]
    gross_weight: Optional<Decimal]
    dimensions: Optional<Dimensions] {
      length: Decimal
      width: Decimal
      height: Decimal
      unit: String @default("CM")
    }
  }
} @standard("GS1")
```

---

## 3. GLN Schema

**定义3（GLN Schema）**：

```text
GLN_Schema = (Location_Identifier, Location_Type, Location_Information)
```

**形式化DSL定义**：

```dsl
schema GLN {
  location_identifier: String @required @pattern("^[0-9]{13}$") @unique
  location_type: Enum { PhysicalLocation, LegalEntity, FunctionalLocation } @required

  location_information: LocationInformation {
    location_name: String @required
    address: Address {
      street_address: String @required
      city: String @required
      state_province: Optional<String]
      postal_code: String @required
      country: String @required @length(2) @pattern("^[A-Z]{2}$")
    }
    contact_information: ContactInformation {
      phone: Optional<String]
      email: Optional<String] @pattern("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
      website: Optional<String]
    }
    coordinates: Optional<Coordinates] {
      latitude: Decimal @range(-90, 90)
      longitude: Decimal @range(-180, 180)
    }
  }

  parent_gln: Optional<String]
  gln_status: Enum { Active, Inactive } @default("Active")
} @standard("GS1")
```

---

## 4. SSCC Schema

**定义4（SSCC Schema）**：

```text
SSCC_Schema = (SSCC_Identifier, Packaging_Type, Packaging_Level)
```

**形式化DSL定义**：

```dsl
schema SSCC {
  sscc_identifier: String @required @pattern("^[0-9]{18}$") @unique

  sscc_structure: SSCCStructure {
    extension_digit: String @pattern("^[0-9]$") @required
    company_prefix: String @pattern("^[0-9]{7,9}$") @required
    serial_reference: String @pattern("^[0-9]{1,9}$") @required
    check_digit: String @pattern("^[0-9]$") @required @computed("calculate_check_digit(extension_digit + company_prefix + serial_reference)")
  }

  packaging_information: PackagingInformation {
    packaging_type: Enum { Case, Pallet, Container, Other } @required
    packaging_level: Int @range(0, 9) @default(0)
    parent_sscc: Optional<String]
    contained_gtins: List<String]
    quantity: Optional<Int]
  }

  shipping_information: Optional<ShippingInformation] {
    shipper_gln: String @required
    receiver_gln: String @required
    ship_date: Optional<Date]
    expected_delivery_date: Optional<Date]
  }
} @standard("GS1")
```

---

## 5. EPCIS Schema

**定义5（EPCIS Schema）**：

```text
EPCIS_Schema = (ObjectEvent | AggregationEvent | TransactionEvent | TransformationEvent)
```

**形式化DSL定义**：

```dsl
schema EPCIS {
  epcis_document: EPCISDocument {
    epcis_header: EPCISHeader {
      standard_version: String @default("1.2")
      epcis_version: String @default("1.2")
      created_date_time: DateTime @required
      sender: String @required
      receiver: Optional<String]
    }

    epcis_body: EPCISBody {
      event_list: List<EPCISEvent] @required
    }
  }

  // ObjectEvent（对象事件）
  object_event: Optional<ObjectEvent] {
    event_time: DateTime @required
    event_time_zone_offset: String @pattern("^[+-][0-9]{2}:[0-9]{2}$")
    epc_list: List<String] @required
    action: Enum { ADD, OBSERVE, DELETE } @required
    biz_step: Optional<String]
    disposition: Optional<String]
    read_point: Optional<ReadPoint] {
      id: String @required
    }
    biz_location: Optional<BizLocation] {
      id: String @required
    }
    biz_transaction_list: Optional<List<BizTransaction]]
    source_list: Optional<List<Source]]
    destination_list: Optional<List<Destination]]
    quantity_list: Optional<List<Quantity]]
    sensor_element_list: Optional<List<SensorElement]]
  }

  // AggregationEvent（聚合事件）
  aggregation_event: Optional<AggregationEvent] {
    event_time: DateTime @required
    event_time_zone_offset: String
    parent_id: String @required
    child_epcs: List<String] @required
    action: Enum { ADD, OBSERVE, DELETE } @required
    biz_step: Optional<String]
    disposition: Optional<String]
    read_point: Optional<ReadPoint]
    biz_location: Optional<BizLocation]
    biz_transaction_list: Optional<List<BizTransaction]]
    source_list: Optional<List<Source]]
    destination_list: Optional<List<Destination]]
    quantity_list: Optional<List<Quantity]]
  }

  // TransactionEvent（交易事件）
  transaction_event: Optional<TransactionEvent] {
    event_time: DateTime @required
    event_time_zone_offset: String
    epc_list: List<String] @required
    action: Enum { ADD, OBSERVE, DELETE } @required
    biz_step: Optional<String]
    disposition: Optional<String]
    read_point: Optional<ReadPoint]
    biz_location: Optional<BizLocation]
    biz_transaction_list: List<BizTransaction] @required {
      type: String @required
      value: String @required
    }
    source_list: Optional<List<Source]]
    destination_list: Optional<List<Destination]]
    quantity_list: Optional<List<Quantity]]
  }

  // TransformationEvent（转换事件）
  transformation_event: Optional<TransformationEvent] {
    event_time: DateTime @required
    event_time_zone_offset: String
    transformation_id: String @required
    input_epc_list: List<String]
    input_quantity_list: Optional<List<Quantity]]
    output_epc_list: List<String]
    output_quantity_list: Optional<List<Quantity]]
    biz_step: Optional<String]
    disposition: Optional<String]
    read_point: Optional<ReadPoint]
    biz_location: Optional<BizLocation]
    biz_transaction_list: Optional<List<BizTransaction]]
    source_list: Optional<List<Source]]
    destination_list: Optional<List<Destination]]
  }
} @standard("GS1_EPCIS")
```

---

## 6. 类型系统

**定义6（GS1数据类型）**：

```text
GS1_Data_Type = GTIN | GLN | SSCC | EPCIS_Event
```

**基本类型定义**：

```dsl
type ReadPoint {
  id: String @required
  name: Optional<String]
}

type BizLocation {
  id: String @required
  name: Optional<String]
}

type BizTransaction {
  type: String @required
  value: String @required
}

type Quantity {
  epc_class: String @required
  quantity: Decimal @required
  uom: Optional<String]
}
```

---

## 7. 约束规则

**约束1（GTIN校验位）**：

```text
∀ gtin ∈ GTIN:
  validate_check_digit(gtin)
  → gtin_valid(gtin)
```

**约束2（GLN唯一性）**：

```text
∀ gln ∈ GLN:
  gln.location_identifier.unique
  → gln_unique(gln)
```

**约束3（SSCC结构）**：

```text
∀ sscc ∈ SSCC:
  sscc.sscc_identifier.length = 18
  ∧ validate_check_digit(sscc.sscc_identifier)
  → sscc_valid(sscc)
```

---

## 8. 转换函数

**函数1（GTIN到EPC转换）**：

```text
convert_gtin_to_epc: GTIN → EPC
```

**函数2（EPCIS到数据库转换）**：

```text
convert_epcis_to_database: EPCIS_Event → Database_Record
```

**函数3（GS1标识符验证）**：

```text
validate_gs1_identifier: GS1_Identifier → ValidationResult
```

---

## 9. 形式化定理

### 9.1 GTIN唯一性定理

**定理1（GTIN唯一性）**：

```text
∀ gtin1, gtin2 ∈ GTIN:
  gtin1.identifier = gtin2.identifier
  → gtin1 = gtin2
```

### 9.2 EPCIS事件完整性定理

**定理2（EPCIS事件完整性）**：

```text
∀ event ∈ EPCIS_Event:
  has_event_time(event)
  ∧ has_action(event)
  → event_complete(event)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
