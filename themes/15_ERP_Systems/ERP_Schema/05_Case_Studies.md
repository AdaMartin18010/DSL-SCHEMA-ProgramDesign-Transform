# ERP Schema实践案例

## 📑 目录

- [ERP Schema实践案例](#erp-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：财务凭证处理](#2-案例1财务凭证处理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：采购订单管理](#3-案例2采购订单管理)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：生产订单执行](#4-案例3生产订单执行)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：ERP到OAGIS转换](#5-案例4erp到oagis转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：ERP数据存储与分析系统](#6-案例5erp数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供ERP Schema在实际应用中的实践案例。

---

## 2. 案例1：财务凭证处理

### 2.1 场景描述

**应用场景**：
ERP系统财务凭证处理，包括凭证录入、审核、过账等流程。

### 2.2 Schema定义

**财务凭证处理ERP Schema**：

```dsl
schema FinancialJournalEntry {
  entry_id: String @value("JE-2025-001")
  entry_date: Date @value("2025-01-21")
  entry_type: Enum @value("Manual")
  description: String @value("材料采购凭证")

  lines: List<JournalLine] {
    line1: JournalLine {
      account_code: String @value("1001")
      account_name: String @value("库存现金")
      debit_amount: Decimal @value(10000.00)
      credit_amount: Decimal @value(0.00)
    }

    line2: JournalLine {
      account_code: String @value("1201")
      account_name: String @value("原材料")
      debit_amount: Decimal @value(0.00)
      credit_amount: Decimal @value(10000.00)
    }
  }

  total_debit: Decimal @value(10000.00)
  total_credit: Decimal @value(10000.00)
} @standard("ISA-95")
```

---

## 3. 案例2：采购订单管理

### 3.1 场景描述

**应用场景**：
ERP系统采购订单管理，包括订单创建、审批、收货、付款等流程。

### 3.2 Schema定义

**采购订单管理ERP Schema**：

```dsl
schema PurchaseOrderManagement {
  purchase_order: PurchaseOrder {
    po_number: String @value("PO-2025-001")
    supplier_id: String @value("SUP-001")
    supplier_name: String @value("ABC供应商")
    order_date: Date @value("2025-01-21")
    delivery_date: Date @value("2025-01-28")
    status: Enum @value("Approved")

    items: List<POItem] {
      item1: POItem {
        item_code: String @value("MAT-001")
        item_name: String @value("原材料A")
        quantity: Decimal @value(100.00)
        unit_price: Decimal @value(50.00)
        total_amount: Decimal @value(5000.00)
      }

      item2: POItem {
        item_code: String @value("MAT-002")
        item_name: String @value("原材料B")
        quantity: Decimal @value(200.00)
        unit_price: Decimal @value(25.00)
        total_amount: Decimal @value(5000.00)
      }
    }

    total_amount: Decimal @value(10000.00)
  }
} @standard("OAGIS")
```

---

## 4. 案例3：生产订单执行

### 4.1 场景描述

**应用场景**：
ERP系统生产订单执行，包括订单下达、物料准备、生产执行、完工入库等流程。

### 4.2 Schema定义

**生产订单执行ERP Schema**：

```dsl
schema ProductionOrderExecution {
  production_order: ProductionOrder {
    order_number: String @value("PROD-2025-001")
    product_code: String @value("PROD-001")
    product_name: String @value("产品A")
    quantity: Decimal @value(1000.00)
    start_date: Date @value("2025-01-22")
    end_date: Date @value("2025-01-25")
    status: Enum @value("InProgress")

    bom_version: String @value("V1.0")
    routing_version: String @value("V1.0")
  }

  bill_of_material: BOM {
    bom_id: String @value("BOM-PROD-001-V1.0")
    product_code: String @value("PROD-001")
    version: String @value("V1.0")

    components: List<BOMComponent] {
      comp1: BOMComponent {
        component_code: String @value("MAT-001")
        component_name: String @value("原材料A")
        quantity: Decimal @value(2.00)
        unit_of_measure: String @value("KG")
      }

      comp2: BOMComponent {
        component_code: String @value("MAT-002")
        component_name: String @value("原材料B")
        quantity: Decimal @value(1.00)
        unit_of_measure: String @value("KG")
      }
    }
  }
} @standard("ISA-95")
```

---

## 5. 案例4：ERP到OAGIS转换

### 5.1 场景描述

**应用场景**：
将ERP采购订单转换为OAGIS格式，用于ERP系统间数据交换。

### 5.2 实现代码

详见 `04_Transformation.md` 第2章。

---

## 6. 案例5：ERP数据存储与分析系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储ERP业务数据，支持ERP数据分析和报表生成。

### 6.2 实现代码

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
