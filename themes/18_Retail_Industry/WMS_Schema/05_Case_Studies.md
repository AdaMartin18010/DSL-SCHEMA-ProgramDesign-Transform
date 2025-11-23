# WMS Schema实践案例

## 📑 目录

- [WMS Schema实践案例](#wms-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：入库管理系统](#2-案例1入库管理系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：出库管理系统](#3-案例2出库管理系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：库存盘点系统](#4-案例3库存盘点系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：EPCIS集成和商品追踪](#5-案例4epcis集成和商品追踪)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：WMS数据分析和报表](#6-案例5wms数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供WMS Schema在实际应用中的实践案例。

---

## 2. 案例1：入库管理系统

### 2.1 场景描述

**业务背景**：
仓库需要处理入库流程，包括入库单创建、
商品验收、商品上架等，确保入库数据的准确性。

**技术挑战**：

- 需要GS1条码识别
- 需要入库验收流程
- 需要库位分配
- 需要库存更新

**解决方案**：
使用InboundOrderProcessor创建入库单，使用
InboundInspectionProcessor进行验收，使用
InboundPutawayProcessor进行上架，使用WMSStorage
存储数据。

### 2.2 Schema定义

**入库管理Schema**：

```json
{
  "inbound_management": {
    "inbound_id": "INB20250121001",
    "inbound_number": "INB-2025-001",
    "inbound_order": {
      "supplier_id": "SUP001",
      "supplier_name": "供应商A",
      "inbound_date": "2025-01-21",
      "inbound_type": "Purchase",
      "warehouse_id": "WH001",
      "warehouse_name": "仓库A",
      "status": "Completed"
    },
    "inbound_products": {
      "items": [
        {
          "item_id": "ITEM001",
          "product_barcode": "6901234567890",
          "product_name": "商品A",
          "quantity": 100,
          "batch_number": "BATCH001"
        }
      ]
    },
    "inbound_inspection": {
      "inspection_status": "Passed",
      "inspector": "质检员A",
      "inspection_time": "2025-01-21T10:00:00Z"
    },
    "inbound_putaway": {
      "putaway_items": [
        {
          "item_id": "ITEM001",
          "location_code": "A-01-01-01",
          "quantity": 100,
          "putaway_person": "上架员A",
          "putaway_time": "2025-01-21T11:00:00Z"
        }
      ],
      "putaway_status": "Completed"
    }
  }
}
```

### 2.3 实现代码

**完整的入库管理实现**：

```python
from inbound_order_processor import InboundOrderProcessor
from inbound_inspection_processor import InboundInspectionProcessor
from inbound_putaway_processor import InboundPutawayProcessor
from wms_storage import WMSStorage
from location_manager import LocationManager
from datetime import date

# 初始化组件
storage = WMSStorage("postgresql://user:pass@localhost/wms")
location_manager = LocationManager(storage)
inbound_processor = InboundOrderProcessor()
inspection_processor = InboundInspectionProcessor()
putaway_processor = InboundPutawayProcessor(location_manager)

# 创建入库单
order_data = {
    "supplier_id": "SUP001",
    "supplier_name": "供应商A",
    "inbound_type": "Purchase",
    "warehouse_id": "WH001",
    "warehouse_name": "仓库A",
    "items": [
        {
            "product_barcode": "6901234567890",
            "product_name": "商品A",
            "quantity": 100,
            "batch_number": "BATCH001",
            "expiry_date": "2026-01-21",
            "unit": "pieces"
        },
        {
            "product_barcode": "6901234567891",
            "product_name": "商品B",
            "quantity": 50,
            "batch_number": "BATCH002",
            "expiry_date": "2026-02-21",
            "unit": "pieces"
        }
    ]
}

inbound_order = inbound_processor.create_inbound_order(order_data)
print(f"Created inbound order: {inbound_order['inbound_number']}")

# 入库验收
inspection_data = {
    "inspector": "质检员A",
    "notes": "验收通过",
    "ITEM001": {"status": "Passed"},
    "ITEM002": {"status": "Passed"}
}

inbound_order = inspection_processor.inspect_inbound_order(
    inbound_order, inspection_data
)
print(f"Inspection status: {inbound_order['inbound_inspection']['inspection_status']}")

# 分配库位
inbound_order = putaway_processor.allocate_locations(inbound_order)
print(f"Allocated {len(inbound_order['inbound_putaway']['putaway_items'])} locations")

# 确认上架
putaway_data = {
    "ITEM001": {
        "confirmed": True,
        "putaway_person": "上架员A"
    },
    "ITEM002": {
        "confirmed": True,
        "putaway_person": "上架员B"
    }
}

inbound_order = putaway_processor.confirm_putaway(inbound_order, putaway_data)
print(f"Putaway status: {inbound_order['inbound_putaway']['putaway_status']}")

# 存储入库单
storage.store_inbound_order(inbound_order)
print(f"Stored inbound order: {inbound_order['inbound_id']}")
```

---

## 3. 案例2：出库管理系统

### 3.1 场景描述

**业务背景**：
仓库需要处理出库流程，包括出库单创建、
拣货、出库复核等，确保出库数据的准确性。

**技术挑战**：

- 需要出库单管理
- 需要拣货策略（FIFO、LIFO、FEFO）
- 需要拣货路径优化
- 需要出库复核

**解决方案**：
使用OutboundOrderProcessor创建出库单，使用
PickingProcessor进行拣货，使用OutboundVerificationProcessor
进行复核，使用WMSStorage存储数据。

### 3.2 Schema定义

**出库管理Schema**：

```json
{
  "outbound_management": {
    "outbound_id": "OUT20250121001",
    "outbound_number": "OUT-2025-001",
    "outbound_order": {
      "customer_id": "CUST001",
      "customer_name": "客户A",
      "outbound_date": "2025-01-21",
      "outbound_type": "Sales",
      "warehouse_id": "WH001",
      "priority": "High",
      "status": "Verified"
    },
    "outbound_products": {
      "items": [
        {
          "item_id": "ITEM001",
          "product_barcode": "6901234567890",
          "product_name": "商品A",
          "quantity": 20,
          "picking_strategy": "FIFO"
        }
      ]
    },
    "picking_management": {
      "picking_items": [
        {
          "item_id": "ITEM001",
          "location_code": "A-01-01-01",
          "quantity": 20,
          "picked_quantity": 20,
          "picker": "拣货员A",
          "picking_time": "2025-01-21T14:00:00Z",
          "picking_status": "Picked"
        }
      ],
      "picking_status": "Completed"
    },
    "outbound_verification": {
      "verifier": "复核员A",
      "verification_time": "2025-01-21T15:00:00Z",
      "verification_status": "Passed"
    }
  }
}
```

### 3.3 实现代码

**完整的出库管理实现**：

```python
from outbound_order_processor import OutboundOrderProcessor
from picking_processor import PickingProcessor
from outbound_verification_processor import OutboundVerificationProcessor
from wms_storage import WMSStorage
from inventory_manager import InventoryManager
from datetime import date

# 初始化组件
storage = WMSStorage("postgresql://user:pass@localhost/wms")
inventory_manager = InventoryManager(storage)
outbound_processor = OutboundOrderProcessor()
picking_processor = PickingProcessor(inventory_manager)
verification_processor = OutboundVerificationProcessor()

# 创建出库单
order_data = {
    "customer_id": "CUST001",
    "customer_name": "客户A",
    "outbound_type": "Sales",
    "warehouse_id": "WH001",
    "priority": "High",
    "items": [
        {
            "product_barcode": "6901234567890",
            "product_name": "商品A",
            "quantity": 20,
            "picking_strategy": "FIFO"
        },
        {
            "product_barcode": "6901234567891",
            "product_name": "商品B",
            "quantity": 10,
            "picking_strategy": "FEFO"
        }
    ]
}

outbound_order = outbound_processor.create_outbound_order(order_data)
print(f"Created outbound order: {outbound_order['outbound_number']}")

# 生成拣货单
outbound_order = picking_processor.generate_picking_list(outbound_order)
print(f"Generated picking list with {len(outbound_order['picking_management']['picking_items'])} items")

# 确认拣货
picking_data = {}
for picking_item in outbound_order["picking_management"]["picking_items"]:
    picking_data[picking_item["location_code"]] = {
        "picked": True,
        "picked_quantity": picking_item["quantity"],
        "picker": "拣货员A"
    }

outbound_order = picking_processor.confirm_picking(outbound_order, picking_data)
print(f"Picking status: {outbound_order['picking_management']['picking_status']}")

# 出库复核
verification_data = {
    "verifier": "复核员A",
    "notes": "复核通过",
    "ITEM001": {"barcode_mismatch": False},
    "ITEM002": {"barcode_mismatch": False}
}

outbound_order = verification_processor.verify_outbound_order(
    outbound_order, verification_data
)
print(f"Verification status: {outbound_order['outbound_verification']['verification_status']}")

# 存储出库单
storage.store_outbound_order(outbound_order)
print(f"Stored outbound order: {outbound_order['outbound_id']}")
```

---

## 4. 案例3：库存盘点系统

### 4.1 场景描述

**业务背景**：
仓库需要定期进行库存盘点，包括盘点计划、
盘点执行、盘点差异处理等，确保库存数据的准确性。

**技术挑战**：

- 需要盘点计划制定
- 需要盘点执行（全盘、抽盘）
- 需要盘点差异分析
- 需要库存调整

**解决方案**：
使用InventoryCountPlanProcessor创建盘点计划，使用
InventoryCountExecutionProcessor执行盘点，使用
InventoryCountDifferenceProcessor处理差异，使用
WMSStorage存储数据。

### 4.2 Schema定义

**库存盘点Schema**：

```json
{
  "inventory_count": {
    "count_id": "CNT20250121001",
    "count_number": "CNT-2025-001",
    "count_plan": {
      "warehouse_id": "WH001",
      "count_type": "Full",
      "count_date": "2025-01-21",
      "counters": ["盘点员A", "盘点员B"],
      "status": "Completed"
    },
    "count_execution": {
      "count_items": [
        {
          "item_id": "CNT_ITEM001",
          "product_barcode": "6901234567890",
          "location_code": "A-01-01-01",
          "system_quantity": 100,
          "counted_quantity": 98,
          "counter": "盘点员A",
          "count_status": "Counted"
        }
      ]
    },
    "count_difference": {
      "differences": [
        {
          "item_id": "CNT_ITEM001",
          "product_barcode": "6901234567890",
          "location_code": "A-01-01-01",
          "system_quantity": 100,
          "counted_quantity": 98,
          "difference_quantity": -2,
          "difference_reason": "损耗",
          "adjustment_status": "Adjusted"
        }
      ],
      "total_differences": 1,
      "adjustment_required": true
    }
  }
}
```

### 4.3 实现代码

**完整的库存盘点实现**：

```python
from inventory_count_plan_processor import InventoryCountPlanProcessor
from inventory_count_execution_processor import InventoryCountExecutionProcessor
from inventory_count_difference_processor import InventoryCountDifferenceProcessor
from wms_storage import WMSStorage
from inventory_manager import InventoryManager
from datetime import date

# 初始化组件
storage = WMSStorage("postgresql://user:pass@localhost/wms")
inventory_manager = InventoryManager(storage)
plan_processor = InventoryCountPlanProcessor(inventory_manager)
execution_processor = InventoryCountExecutionProcessor()
difference_processor = InventoryCountDifferenceProcessor(inventory_manager)

# 创建盘点计划
plan_data = {
    "warehouse_id": "WH001",
    "count_type": "Full",
    "count_date": date.today(),
    "counters": ["盘点员A", "盘点员B"]
}

count_plan = plan_processor.create_count_plan(plan_data)
print(f"Created count plan: {count_plan['count_number']}")
print(f"Total items to count: {len(count_plan['count_execution']['count_items'])}")

# 执行盘点
count_data = {}
for count_item in count_plan["count_execution"]["count_items"]:
    # 模拟盘点数据（实际应从RFID扫描或条码扫描获取）
    count_data[count_item["item_id"]] = {
        "counted": True,
        "counted_quantity": count_item["system_quantity"] - 2,  # 模拟差异
        "counter": "盘点员A"
    }

count_plan = execution_processor.execute_count(count_plan, count_data)
print(f"Count execution status: {count_plan['count_plan']['status']}")

# 审批差异
approval_data = {}
for difference in count_plan["count_difference"]["differences"]:
    approval_data[difference["item_id"]] = {
        "approved": True,
        "reason": "正常损耗"
    }

count_plan = difference_processor.approve_differences(count_plan, approval_data)
print(f"Total differences: {count_plan['count_difference']['total_differences']}")

# 调整库存
count_plan = difference_processor.adjust_inventory(count_plan)
print(f"Inventory adjustment completed")

# 输出盘点结果
print(f"\nCount Results:")
for difference in count_plan["count_difference"]["differences"]:
    print(f"  {difference['product_barcode']} @ {difference['location_code']}: "
          f"System={difference['system_quantity']}, "
          f"Counted={difference['counted_quantity']}, "
          f"Diff={difference['difference_quantity']}, "
          f"Status={difference['adjustment_status']}")
```

---

## 5. 案例4：EPCIS集成和商品追踪

### 5.1 场景描述

**业务背景**：
仓库需要集成EPCIS标准，实现商品的全程追踪，
包括入库事件、出库事件等。

**技术挑战**：

- 需要EPCIS事件生成
- 需要EPCIS事件解析
- 需要商品追踪查询

**解决方案**：
使用EPCISEventGenerator生成EPCIS事件，实现
商品追踪功能。

### 5.2 实现代码

**完整的EPCIS集成实现**：

```python
from epcis_event_generator import EPCISEventGenerator
from wms_storage import WMSStorage

# 初始化组件
storage = WMSStorage("postgresql://user:pass@localhost/wms")
event_generator = EPCISEventGenerator()

# 生成入库EPCIS事件
inbound_order = {
    "inbound_id": "INB20250121001",
    "inbound_order": {
        "warehouse_id": "WH001"
    },
    "inbound_products": {
        "items": [
            {"product_barcode": "6901234567890"},
            {"product_barcode": "6901234567891"}
        ]
    }
}

inbound_event = event_generator.generate_inbound_event(inbound_order)
print(f"Generated inbound EPCIS event:")
print(f"  Event Type: {inbound_event['event_type']}")
print(f"  Action: {inbound_event['action']}")
print(f"  EPCs: {inbound_event['epc_list']}")

# 生成出库EPCIS事件
outbound_order = {
    "outbound_id": "OUT20250121001",
    "outbound_order": {
        "warehouse_id": "WH001"
    },
    "outbound_products": {
        "items": [
            {"product_barcode": "6901234567890"}
        ]
    }
}

outbound_event = event_generator.generate_outbound_event(outbound_order)
print(f"\nGenerated outbound EPCIS event:")
print(f"  Event Type: {outbound_event['event_type']}")
print(f"  Action: {outbound_event['action']}")
print(f"  EPCs: {outbound_event['epc_list']}")
```

---

## 6. 案例5：WMS数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储WMS数据，支持数据查询、
分析和报表生成。

### 6.2 实现代码

**完整的数据分析实现**：

```python
from wms_storage import WMSStorage

storage = WMSStorage("postgresql://user:pass@localhost/wms")

# 查询入库统计
warehouse_id = "WH001"
inbound_stats = storage.get_inbound_statistics(warehouse_id, days=30)
print("Inbound Statistics (30 days):")
print(f"  Total Orders: {inbound_stats['total_orders']}")
print(f"  Total Quantity: {inbound_stats['total_quantity']}")
print(f"  Total Suppliers: {inbound_stats['total_suppliers']}")

# 查询出库统计
outbound_stats = storage.get_outbound_statistics(warehouse_id, days=30)
print(f"\nOutbound Statistics (30 days):")
print(f"  Total Orders: {outbound_stats['total_orders']}")
print(f"  Total Quantity: {outbound_stats['total_quantity']}")
print(f"  Total Customers: {outbound_stats['total_customers']}")

# 查询库存周转率
turnover_stats = storage.get_inventory_turnover(warehouse_id, days=30)
print(f"\nInventory Turnover (30 days):")
print(f"  Avg Inventory: {turnover_stats['avg_inventory']:.2f}")
print(f"  Total Outbound: {turnover_stats['total_outbound']:.2f}")
print(f"  Turnover Rate: {turnover_stats['turnover_rate']:.2f}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
