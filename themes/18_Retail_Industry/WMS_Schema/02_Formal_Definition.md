# WMS Schema形式化定义

## 📑 目录

- [WMS Schema形式化定义](#wms-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 入库管理Schema](#2-入库管理schema)
  - [3. 出库管理Schema](#3-出库管理schema)
  - [4. 库存盘点Schema](#4-库存盘点schema)
  - [5. 库位管理Schema](#5-库位管理schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 入库完整性定理](#91-入库完整性定理)
    - [9.2 库存一致性定理](#92-库存一致性定理)

---

## 1. 形式化模型

**定义1（WMS Schema）**：
WMS Schema是一个四元组：

```text
WMS_Schema = (Inbound_Management_Schema, Outbound_Management_Schema,
             Inventory_Count_Schema, Location_Management_Schema)
```

其中：

- `Inbound_Management_Schema`：入库管理Schema
- `Outbound_Management_Schema`：出库管理Schema
- `Inventory_Count_Schema`：库存盘点Schema
- `Location_Management_Schema`：库位管理Schema

---

## 2. 入库管理Schema

**定义2（入库管理Schema）**：

```text
Inbound_Management_Schema = (Inbound_Order, Inbound_Products,
                            Inbound_Inspection, Inbound_Putaway)
```

**形式化DSL定义**：

```dsl
schema InboundManagement {
  inbound_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  inbound_number: String @max_length(50) @required @unique

  inbound_order: {
    supplier_id: String @max_length(50) @required
    supplier_name: String @max_length(200)
    inbound_date: Date @format("YYYY-MM-DD") @required
    inbound_type: Enum { Purchase, Return, Transfer, Adjustment } @required
    warehouse_id: String @max_length(50) @required
    warehouse_name: String @max_length(200)
    status: Enum { Pending, InProgress, Completed, Cancelled } @required
  } @required

  inbound_products: {
    items: List<InboundItem> {
      item_id: String @required @unique
      product_barcode: String @max_length(50) @required
      product_name: String @max_length(200) @required
      quantity: Integer @range(1, 999999) @required
      batch_number: String @max_length(50)
      expiry_date: Date @format("YYYY-MM-DD")
      unit: String @max_length(20) @default("pieces")
    } @required
  } @required

  inbound_inspection: {
    inspection_status: Enum { Pending, Passed, Failed, Partial } @required
    inspector: String @max_length(100)
    inspection_time: DateTime
    inspection_notes: String @max_length(500)
    rejected_items: List<String>
  } @required

  inbound_putaway: {
    putaway_items: List<PutawayItem> {
      item_id: String @required
      location_code: String @max_length(50) @required
      quantity: Integer @required
      putaway_person: String @max_length(100) @required
      putaway_time: DateTime @required
    }
    putaway_status: Enum { Pending, InProgress, Completed } @required
  } @required
} @standard("GS1")
```

---

## 3. 出库管理Schema

**定义3（出库管理Schema）**：

```text
Outbound_Management_Schema = (Outbound_Order, Outbound_Products,
                             Picking_Management, Outbound_Verification)
```

**形式化DSL定义**：

```dsl
schema OutboundManagement {
  outbound_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  outbound_number: String @max_length(50) @required @unique

  outbound_order: {
    customer_id: String @max_length(50)
    customer_name: String @max_length(200)
    outbound_date: Date @format("YYYY-MM-DD") @required
    outbound_type: Enum { Sales, Return, Transfer, Adjustment } @required
    warehouse_id: String @max_length(50) @required
    priority: Enum { Low, Normal, High, Urgent } @default("Normal")
    status: Enum { Pending, Picking, Picked, Verified, Shipped, Cancelled } @required
  } @required

  outbound_products: {
    items: List<OutboundItem> {
      item_id: String @required @unique
      product_barcode: String @max_length(50) @required
      product_name: String @max_length(200) @required
      quantity: Integer @range(1, 999999) @required
      batch_number: String @max_length(50)
      picking_strategy: Enum { FIFO, LIFO, FEFO, Specified } @default("FIFO")
    } @required
  } @required

  picking_management: {
    picking_items: List<PickingItem> {
      item_id: String @required
      location_code: String @max_length(50) @required
      quantity: Integer @required
      picked_quantity: Integer @default(0)
      picker: String @max_length(100)
      picking_time: DateTime
      picking_status: Enum { Pending, Picking, Picked } @required
    }
    picking_status: Enum { Pending, InProgress, Completed } @required
  } @required

  outbound_verification: {
    verifier: String @max_length(100)
    verification_time: DateTime
    verification_status: Enum { Pending, Passed, Failed } @required
    verification_notes: String @max_length(500)
  } @required
} @standard("GS1")
```

---

## 4. 库存盘点Schema

**定义4（库存盘点Schema）**：

```text
Inventory_Count_Schema = (Count_Plan, Count_Execution, Count_Difference)
```

**形式化DSL定义**：

```dsl
schema InventoryCount {
  count_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  count_number: String @max_length(50) @required @unique

  count_plan: {
    warehouse_id: String @max_length(50) @required
    count_type: Enum { Full, Partial, Cycle } @required
    count_date: Date @format("YYYY-MM-DD") @required
    count_scope: List<String>  # Location codes or product codes
    counters: List<String> @required
    status: Enum { Planned, InProgress, Completed, Cancelled } @required
  } @required

  count_execution: {
    count_items: List<CountItem> {
      item_id: String @required @unique
      product_barcode: String @max_length(50) @required
      location_code: String @max_length(50) @required
      system_quantity: Integer @required
      counted_quantity: Integer
      counter: String @max_length(100)
      count_time: DateTime
      count_status: Enum { Pending, Counted } @required
    } @required
  } @required

  count_difference: {
    differences: List<CountDifference> {
      item_id: String @required
      product_barcode: String @max_length(50) @required
      location_code: String @max_length(50) @required
      system_quantity: Integer @required
      counted_quantity: Integer @required
      difference_quantity: Integer @required
      difference_reason: String @max_length(500)
      adjustment_status: Enum { Pending, Approved, Adjusted } @required
    }
    total_differences: Integer @default(0)
    adjustment_required: Boolean @default(false)
  }
} @standard("GS1")
```

---

## 5. 库位管理Schema

**定义5（库位管理Schema）**：

```text
Location_Management_Schema = (Location_Info, Location_Allocation, Location_Query)
```

**形式化DSL定义**：

```dsl
schema LocationManagement {
  location_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  location_code: String @max_length(50) @required @unique

  location_info: {
    warehouse_id: String @max_length(50) @required
    warehouse_name: String @max_length(200)
    zone: String @max_length(50)
    aisle: String @max_length(50)
    shelf: String @max_length(50)
    position: String @max_length(50)
    location_type: Enum { Storage, Picking, Staging, Quarantine } @required
    capacity: Integer @range(1, 999999)
    current_quantity: Integer @default(0)
    available_capacity: Integer
  } @required

  location_allocation: {
    allocated_items: List<AllocatedItem> {
      product_barcode: String @required
      quantity: Integer @required
      batch_number: String @max_length(50)
      allocated_time: DateTime @required
    }
  } @required

  location_query: {
    query_criteria: {
      warehouse_id: String @max_length(50)
      zone: String @max_length(50)
      location_type: Enum { Storage, Picking, Staging, Quarantine }
      available_capacity_min: Integer
    }
  }
} @standard("GS1")
```

---

## 6. 类型系统

**定义6（WMS类型系统）**：

```text
WMS_Type_System = (Inbound_Types, Outbound_Types, Count_Types, Location_Types)
```

**入库类型**：

- **InboundType**：入库类型枚举
- **InboundStatus**：入库状态枚举
- **InspectionStatus**：验收状态枚举

**出库类型**：

- **OutboundType**：出库类型枚举
- **OutboundStatus**：出库状态枚举
- **PickingStrategy**：拣货策略枚举

**盘点类型**：

- **CountType**：盘点类型枚举
- **CountStatus**：盘点状态枚举
- **AdjustmentStatus**：调整状态枚举

**库位类型**：

- **LocationType**：库位类型枚举
- **AllocationStatus**：分配状态枚举

---

## 7. 约束规则

**规则1（入库数量约束）**：

```text
∀ im ∈ Inbound_Management_Schema:
  ∀ item ∈ im.inbound_products.items:
    item.quantity > 0
    im.inbound_putaway.putaway_items中item对应的quantity总和 ≤ item.quantity
```

**规则2（出库数量约束）**：

```text
∀ om ∈ Outbound_Management_Schema:
  ∀ item ∈ om.outbound_products.items:
    item.quantity > 0
    om.picking_management.picking_items中item对应的picked_quantity ≤ item.quantity
```

**规则3（库存一致性约束）**：

```text
∀ ic ∈ Inventory_Count_Schema:
  ∀ diff ∈ ic.count_difference.differences:
    diff.difference_quantity = diff.counted_quantity - diff.system_quantity
    diff.adjustment_status = "Adjusted" →
      ∃ adjustment_record: adjustment_record.item_id = diff.item_id
```

---

## 8. 转换函数

**函数1（EPCIS到入库转换）**：

```text
Convert_EPCIS_to_Inbound: EPCIS_ObjectEvent_Schema → Inbound_Management_Schema
Convert_EPCIS_to_Inbound(epcis_event) = {
  inbound_number: epcis_event.event_time + "_INBOUND",
  inbound_order: {
    supplier_id: epcis_event.business_location,
    inbound_date: epcis_event.event_time.date()
  },
  inbound_products: {
    items: map(Convert_EPC_to_InboundItem, epcis_event.epc_list)
  }
}
```

**函数2（出库到EPCIS转换）**：

```text
Convert_Outbound_to_EPCIS: Outbound_Management_Schema → EPCIS_ObjectEvent_Schema
Convert_Outbound_to_EPCIS(outbound) = {
  event_time: outbound.outbound_order.outbound_date,
  event_type: "ObjectEvent",
  action: "OBSERVE",
  epc_list: map(Get_EPC_from_Product, outbound.outbound_products.items),
  business_location: outbound.outbound_order.warehouse_id
}
```

---

## 9. 形式化定理

### 9.1 入库完整性定理

**定理1（入库完整性）**：

对于任意入库管理IM，如果IM的所有必需信息都存在，
则IM是完整的：

```text
∀ im ∈ Inbound_Management_Schema:
  Complete(im) ↔
    ∃ im.inbound_order ∧ ∃ im.inbound_products.items ∧
    ∃ im.inbound_inspection ∧ ∃ im.inbound_putaway
```

**证明**：

根据GS1标准，入库管理的完整性定义为所有必需信息
都存在。因此，如果所有必需信息都存在，则入库管理
是完整的。

### 9.2 库存一致性定理

**定理2（库存一致性）**：

对于任意库存盘点IC，如果IC的盘点数量等于系统数量
（考虑差异调整），则IC是一致的：

```text
∀ ic ∈ Inventory_Count_Schema:
  Consistent(ic) ↔
    ∀ item ∈ ic.count_execution.count_items:
      item.count_status = "Counted" →
        ∃ diff ∈ ic.count_difference.differences:
          diff.item_id = item.item_id ∧
          diff.adjustment_status = "Adjusted" →
            System_Quantity_After_Adjustment(diff) = diff.counted_quantity
```

**证明**：

根据GS1标准，库存的一致性定义为盘点数量等于系统数量
（考虑差异调整）。因此，如果盘点数量等于系统数量
（考虑差异调整），则库存是一致的。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21

