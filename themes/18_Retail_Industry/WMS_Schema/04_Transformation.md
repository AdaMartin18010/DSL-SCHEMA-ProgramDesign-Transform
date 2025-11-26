# WMS Schema转换体系

## 📑 目录

- [WMS Schema转换体系](#wms-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 入库流程实现](#2-入库流程实现)
    - [2.1 入库单处理器](#21-入库单处理器)
    - [2.2 入库验收处理器](#22-入库验收处理器)
    - [2.3 入库上架处理器](#23-入库上架处理器)
  - [3. 出库流程实现](#3-出库流程实现)
    - [3.1 出库单处理器](#31-出库单处理器)
    - [3.2 拣货处理器](#32-拣货处理器)
    - [3.3 出库复核处理器](#33-出库复核处理器)
  - [4. 库存盘点实现](#4-库存盘点实现)
    - [4.1 盘点计划处理器](#41-盘点计划处理器)
    - [4.2 盘点执行处理器](#42-盘点执行处理器)
    - [4.3 盘点差异处理器](#43-盘点差异处理器)
  - [5. EPCIS集成实现](#5-epcis集成实现)
    - [5.1 EPCIS事件生成器](#51-epcis事件生成器)
  - [6. WMS数据存储与分析](#6-wms数据存储与分析)
    - [6.1 PostgreSQL WMS数据存储](#61-postgresql-wms数据存储)
    - [6.2 WMS数据分析查询](#62-wms数据分析查询)

---

## 1. 转换体系概述

WMS Schema转换体系支持入库流程、出库流程、
库存盘点、EPCIS集成、数据库存储之间的转换。

### 1.1 转换目标

1. **入库流程处理**：入库单创建、验收、上架
2. **出库流程处理**：出库单创建、拣货、复核
3. **库存盘点处理**：盘点计划、执行、差异处理
4. **EPCIS集成**：EPCIS事件生成和解析
5. **数据到数据库转换**：WMS数据到PostgreSQL存储

---

## 2. 入库流程实现

### 2.1 入库单处理器

**完整的入库单处理实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime, date

logger = logging.getLogger(__name__)

class InboundOrderProcessor:
    """入库单处理器"""

    def __init__(self):
        """初始化入库单处理器"""
        self.logger = logging.getLogger(__name__)
        self.max_items_per_order = 1000
        self.max_quantity_per_item = 999999

    def create_inbound_order(self, order_data: Dict) -> Dict:
        """创建入库单 - 增强错误处理"""
        # 输入验证
        if not isinstance(order_data, dict):
            raise TypeError(f"Order data must be a dictionary, got {type(order_data)}")

        if not order_data:
            raise ValueError("Order data cannot be empty")

        # 必需字段验证
        required_fields = ["supplier_id", "warehouse_id"]
        missing_fields = [f for f in required_fields if not order_data.get(f)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # 供应商ID验证
        supplier_id = order_data.get("supplier_id")
        if not isinstance(supplier_id, str) or not supplier_id.strip():
            raise ValueError(f"Invalid supplier_id: {supplier_id}")

        # 仓库ID验证
        warehouse_id = order_data.get("warehouse_id")
        if not isinstance(warehouse_id, str) or not warehouse_id.strip():
            raise ValueError(f"Invalid warehouse_id: {warehouse_id}")

        # 入库类型验证
        inbound_type = order_data.get("inbound_type", "Purchase")
        valid_types = ["Purchase", "Return", "Transfer", "Adjustment"]
        if inbound_type not in valid_types:
            logger.warning(f"Invalid inbound type '{inbound_type}', using default 'Purchase'. Valid types: {valid_types}")
            inbound_type = "Purchase"

        # 商品列表验证
        items = order_data.get("items", [])
        if not isinstance(items, list):
            raise TypeError(f"Items must be a list, got {type(items)}")

        if not items:
            raise ValueError("Inbound order must have at least one item")

        if len(items) > 1000:  # 防止异常大的订单
            raise ValueError(f"Too many items: {len(items)} (max 1000)")

        try:
            inbound_id = f"INB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            inbound_number = f"INB-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

            inbound_order = {
                "inbound_id": inbound_id,
                "inbound_number": inbound_number,
                "inbound_order": {
                    "supplier_id": supplier_id,
                    "supplier_name": order_data.get("supplier_name", ""),
                    "inbound_date": date.today(),
                    "inbound_type": inbound_type,
                    "warehouse_id": warehouse_id,
                    "warehouse_name": order_data.get("warehouse_name", ""),
                    "status": "Pending"
                },
                "inbound_products": {
                    "items": []
                },
                "inbound_inspection": {
                    "inspection_status": "Pending",
                    "inspector": None,
                    "inspection_time": None,
                    "inspection_notes": "",
                    "rejected_items": []
                },
                "inbound_putaway": {
                    "putaway_items": [],
                    "putaway_status": "Pending"
                }
            }

            # 添加商品（带验证）
            for idx, item_data in enumerate(items):
                if not isinstance(item_data, dict):
                    raise TypeError(f"Item {idx} must be a dictionary, got {type(item_data)}")

                # 商品必需字段验证
                if not item_data.get("product_barcode") and not item_data.get("product_id"):
                    raise ValueError(f"Item {idx} missing product identifier (barcode or product_id)")

                quantity = item_data.get("quantity")
                if quantity is None:
                    raise ValueError(f"Item {idx} missing quantity")

                if not isinstance(quantity, (int, float)) or quantity <= 0:
                    raise ValueError(f"Item {idx} invalid quantity: {quantity}")

                if quantity > 999999:  # 防止异常大数量
                    raise ValueError(f"Item {idx} quantity too large: {quantity} (max 999999)")

                item = {
                    "item_id": f"ITEM{len(inbound_order['inbound_products']['items']) + 1:03d}",
                    "product_barcode": item_data.get("product_barcode", ""),
                    "product_id": item_data.get("product_id", ""),
                    "product_name": item_data.get("product_name", ""),
                    "quantity": float(quantity),
                    "batch_number": item_data.get("batch_number", ""),
                    "expiry_date": item_data.get("expiry_date"),
                    "unit": item_data.get("unit", "pieces")
                }
                inbound_order["inbound_products"]["items"].append(item)

            logger.info(f"Created inbound order: {inbound_number} with {len(items)} items")
            return inbound_order

        except (ValueError, TypeError) as e:
            logger.error(f"Inbound order creation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating inbound order: {e}", exc_info=True)
            raise RuntimeError(f"Inbound order creation failed: {e}") from e
```

### 2.2 入库验收处理器

**入库验收处理实现**：

```python
class InboundInspectionProcessor:
    """入库验收处理器"""

    def __init__(self):
        """初始化入库验收处理器"""
        self.logger = logging.getLogger(__name__)
        self.inspection_statuses = ["Passed", "Failed", "Partial"]

    def inspect_inbound_order(self, inbound_order: Dict,
                              inspection_data: Dict) -> Dict:
        """验收入库单"""
        inspection_results = {
            "passed_items": [],
            "failed_items": [],
            "partial_items": []
        }

        for item in inbound_order["inbound_products"]["items"]:
            item_result = inspection_data.get(item["item_id"], {})

            if item_result.get("status") == "Passed":
                inspection_results["passed_items"].append(item["item_id"])
            elif item_result.get("status") == "Failed":
                inspection_results["failed_items"].append({
                    "item_id": item["item_id"],
                    "reason": item_result.get("reason", "Quality issue")
                })
            elif item_result.get("status") == "Partial":
                inspection_results["partial_items"].append({
                    "item_id": item["item_id"],
                    "passed_quantity": item_result.get("passed_quantity", 0),
                    "failed_quantity": item_result.get("failed_quantity", 0)
                })

        # 更新验收状态
        if len(inspection_results["failed_items"]) == 0 and \
           len(inspection_results["partial_items"]) == 0:
            inbound_order["inbound_inspection"]["inspection_status"] = "Passed"
        elif len(inspection_results["passed_items"]) == 0:
            inbound_order["inbound_inspection"]["inspection_status"] = "Failed"
        else:
            inbound_order["inbound_inspection"]["inspection_status"] = "Partial"

        inbound_order["inbound_inspection"]["inspector"] = \
            inspection_data.get("inspector")
        inbound_order["inbound_inspection"]["inspection_time"] = datetime.now()
        inbound_order["inbound_inspection"]["inspection_notes"] = \
            inspection_data.get("notes", "")
        inbound_order["inbound_inspection"]["rejected_items"] = \
            inspection_results["failed_items"]

        return inbound_order
```

### 2.3 入库上架处理器

**入库上架处理实现**：

```python
class InboundPutawayProcessor:
    """入库上架处理器"""

    def __init__(self, location_manager):
        self.location_manager = location_manager

    def allocate_locations(self, inbound_order: Dict) -> Dict:
        """分配库位"""
        putaway_items = []

        for item in inbound_order["inbound_products"]["items"]:
            # 查询可用库位
            available_locations = self.location_manager.find_available_locations(
                warehouse_id=inbound_order["inbound_order"]["warehouse_id"],
                product_barcode=item["product_barcode"],
                required_capacity=item["quantity"]
            )

            if available_locations:
                location = available_locations[0]
                putaway_item = {
                    "item_id": item["item_id"],
                    "location_code": location["location_code"],
                    "quantity": item["quantity"],
                    "putaway_person": None,
                    "putaway_time": None
                }
                putaway_items.append(putaway_item)

        inbound_order["inbound_putaway"]["putaway_items"] = putaway_items
        inbound_order["inbound_putaway"]["putaway_status"] = "InProgress"

        return inbound_order

    def confirm_putaway(self, inbound_order: Dict,
                       putaway_data: Dict) -> Dict:
        """确认上架"""
        for putaway_item in inbound_order["inbound_putaway"]["putaway_items"]:
            item_data = putaway_data.get(putaway_item["item_id"], {})
            if item_data.get("confirmed"):
                putaway_item["putaway_person"] = item_data.get("putaway_person")
                putaway_item["putaway_time"] = datetime.now()

        # 检查是否全部上架完成
        all_confirmed = all(
            item.get("putaway_time") is not None
            for item in inbound_order["inbound_putaway"]["putaway_items"]
        )

        if all_confirmed:
            inbound_order["inbound_putaway"]["putaway_status"] = "Completed"
            inbound_order["inbound_order"]["status"] = "Completed"

        return inbound_order
```

---

## 3. 出库流程实现

### 3.1 出库单处理器

**完整的出库单处理实现**：

```python
class OutboundOrderProcessor:
    """出库单处理器"""

    def __init__(self):
        """初始化出库单处理器"""
        self.logger = logging.getLogger(__name__)
        self.max_items_per_order = 1000
        self.valid_outbound_types = ["Sales", "Return", "Transfer", "Adjustment"]
        self.valid_priorities = ["Low", "Normal", "High", "Urgent"]

    def create_outbound_order(self, order_data: Dict) -> Dict:
        """创建出库单"""
        outbound_id = f"OUT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        outbound_number = f"OUT-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

        outbound_order = {
            "outbound_id": outbound_id,
            "outbound_number": outbound_number,
            "outbound_order": {
                "customer_id": order_data.get("customer_id"),
                "customer_name": order_data.get("customer_name"),
                "outbound_date": date.today(),
                "outbound_type": order_data.get("outbound_type", "Sales"),
                "warehouse_id": order_data.get("warehouse_id"),
                "priority": order_data.get("priority", "Normal"),
                "status": "Pending"
            },
            "outbound_products": {
                "items": []
            },
            "picking_management": {
                "picking_items": [],
                "picking_status": "Pending"
            },
            "outbound_verification": {
                "verifier": None,
                "verification_time": None,
                "verification_status": "Pending",
                "verification_notes": ""
            }
        }

        # 添加商品
        for item_data in order_data.get("items", []):
            item = {
                "item_id": f"ITEM{len(outbound_order['outbound_products']['items']) + 1:03d}",
                "product_barcode": item_data.get("product_barcode"),
                "product_name": item_data.get("product_name"),
                "quantity": item_data.get("quantity"),
                "batch_number": item_data.get("batch_number"),
                "picking_strategy": item_data.get("picking_strategy", "FIFO")
            }
            outbound_order["outbound_products"]["items"].append(item)

        logger.info(f"Created outbound order: {outbound_number}")
        return outbound_order
```

### 3.2 拣货处理器

**拣货处理实现**：

```python
class PickingProcessor:
    """拣货处理器"""

    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager

    def generate_picking_list(self, outbound_order: Dict) -> Dict:
        """生成拣货单"""
        picking_items = []

        for item in outbound_order["outbound_products"]["items"]:
            # 根据拣货策略查询库存
            inventory_locations = self.inventory_manager.query_inventory(
                product_barcode=item["product_barcode"],
                warehouse_id=outbound_order["outbound_order"]["warehouse_id"],
                picking_strategy=item["picking_strategy"],
                required_quantity=item["quantity"]
            )

            remaining_quantity = item["quantity"]
            for location in inventory_locations:
                picking_quantity = min(remaining_quantity, location["available_quantity"])

                picking_item = {
                    "item_id": item["item_id"],
                    "location_code": location["location_code"],
                    "quantity": picking_quantity,
                    "picked_quantity": 0,
                    "picker": None,
                    "picking_time": None,
                    "picking_status": "Pending"
                }
                picking_items.append(picking_item)

                remaining_quantity -= picking_quantity
                if remaining_quantity <= 0:
                    break

        outbound_order["picking_management"]["picking_items"] = picking_items
        outbound_order["picking_management"]["picking_status"] = "InProgress"
        outbound_order["outbound_order"]["status"] = "Picking"

        return outbound_order

    def confirm_picking(self, outbound_order: Dict,
                      picking_data: Dict) -> Dict:
        """确认拣货"""
        for picking_item in outbound_order["picking_management"]["picking_items"]:
            item_data = picking_data.get(picking_item["location_code"], {})
            if item_data.get("picked"):
                picking_item["picked_quantity"] = item_data.get("picked_quantity", 0)
                picking_item["picker"] = item_data.get("picker")
                picking_item["picking_time"] = datetime.now()
                picking_item["picking_status"] = "Picked"

        # 检查是否全部拣货完成
        all_picked = all(
            item.get("picking_status") == "Picked"
            for item in outbound_order["picking_management"]["picking_items"]
        )

        if all_picked:
            outbound_order["picking_management"]["picking_status"] = "Completed"
            outbound_order["outbound_order"]["status"] = "Picked"

        return outbound_order
```

### 3.3 出库复核处理器

**出库复核处理实现**：

```python
class OutboundVerificationProcessor:
    """出库复核处理器"""

    def __init__(self):
        """初始化出库复核处理器"""
        self.logger = logging.getLogger(__name__)
        self.verification_statuses = ["Passed", "Failed", "Pending"]

    def verify_outbound_order(self, outbound_order: Dict,
                             verification_data: Dict) -> Dict:
        """复核出库单"""
        verification_passed = True

        for item in outbound_order["outbound_products"]["items"]:
            item_verification = verification_data.get(item["item_id"], {})

            # 检查数量
            picked_total = sum(
                p["picked_quantity"]
                for p in outbound_order["picking_management"]["picking_items"]
                if p["item_id"] == item["item_id"]
            )

            if picked_total != item["quantity"]:
                verification_passed = False
                break

            # 检查商品条码
            if item_verification.get("barcode_mismatch"):
                verification_passed = False
                break

        if verification_passed:
            outbound_order["outbound_verification"]["verification_status"] = "Passed"
            outbound_order["outbound_order"]["status"] = "Verified"
        else:
            outbound_order["outbound_verification"]["verification_status"] = "Failed"

        outbound_order["outbound_verification"]["verifier"] = \
            verification_data.get("verifier")
        outbound_order["outbound_verification"]["verification_time"] = datetime.now()
        outbound_order["outbound_verification"]["verification_notes"] = \
            verification_data.get("notes", "")

        return outbound_order
```

---

## 4. 库存盘点实现

### 4.1 盘点计划处理器

**盘点计划处理实现**：

```python
class InventoryCountPlanProcessor:
    """盘点计划处理器"""

    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager

    def create_count_plan(self, plan_data: Dict) -> Dict:
        """创建盘点计划"""
        count_id = f"CNT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        count_number = f"CNT-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

        count_plan = {
            "count_id": count_id,
            "count_number": count_number,
            "count_plan": {
                "warehouse_id": plan_data.get("warehouse_id"),
                "count_type": plan_data.get("count_type", "Full"),
                "count_date": plan_data.get("count_date", date.today()),
                "count_scope": plan_data.get("count_scope", []),
                "counters": plan_data.get("counters", []),
                "status": "Planned"
            },
            "count_execution": {
                "count_items": []
            },
            "count_difference": {
                "differences": [],
                "total_differences": 0,
                "adjustment_required": False
            }
        }

        # 生成盘点项
        if count_plan["count_plan"]["count_type"] == "Full":
            # 全盘：查询所有库存
            inventory_items = self.inventory_manager.query_all_inventory(
                warehouse_id=count_plan["count_plan"]["warehouse_id"]
            )
        else:
            # 抽盘：根据范围查询
            inventory_items = self.inventory_manager.query_inventory_by_scope(
                warehouse_id=count_plan["count_plan"]["warehouse_id"],
                scope=count_plan["count_plan"]["count_scope"]
            )

        for inv_item in inventory_items:
            count_item = {
                "item_id": f"CNT_ITEM{len(count_plan['count_execution']['count_items']) + 1:03d}",
                "product_barcode": inv_item["product_barcode"],
                "location_code": inv_item["location_code"],
                "system_quantity": inv_item["quantity"],
                "counted_quantity": None,
                "counter": None,
                "count_time": None,
                "count_status": "Pending"
            }
            count_plan["count_execution"]["count_items"].append(count_item)

        return count_plan
```

### 4.2 盘点执行处理器

**盘点执行处理实现**：

```python
class InventoryCountExecutionProcessor:
    """盘点执行处理器"""

    def __init__(self):
        """初始化盘点执行处理器"""
        self.logger = logging.getLogger(__name__)
        self.count_statuses = ["Pending", "Counted", "Completed"]

    def execute_count(self, count_plan: Dict, count_data: Dict) -> Dict:
        """执行盘点"""
        for count_item in count_plan["count_execution"]["count_items"]:
            item_data = count_data.get(count_item["item_id"], {})

            if item_data.get("counted"):
                count_item["counted_quantity"] = item_data.get("counted_quantity")
                count_item["counter"] = item_data.get("counter")
                count_item["count_time"] = datetime.now()
                count_item["count_status"] = "Counted"

        # 检查是否全部盘点完成
        all_counted = all(
            item.get("count_status") == "Counted"
            for item in count_plan["count_execution"]["count_items"]
        )

        if all_counted:
            count_plan["count_plan"]["status"] = "Completed"
            # 生成差异
            self._generate_differences(count_plan)

        return count_plan

    def _generate_differences(self, count_plan: Dict):
        """生成盘点差异"""
        differences = []

        for count_item in count_plan["count_execution"]["count_items"]:
            difference_quantity = count_item["counted_quantity"] - \
                                 count_item["system_quantity"]

            if difference_quantity != 0:
                difference = {
                    "item_id": count_item["item_id"],
                    "product_barcode": count_item["product_barcode"],
                    "location_code": count_item["location_code"],
                    "system_quantity": count_item["system_quantity"],
                    "counted_quantity": count_item["counted_quantity"],
                    "difference_quantity": difference_quantity,
                    "difference_reason": "",
                    "adjustment_status": "Pending"
                }
                differences.append(difference)

        count_plan["count_difference"]["differences"] = differences
        count_plan["count_difference"]["total_differences"] = len(differences)
        count_plan["count_difference"]["adjustment_required"] = len(differences) > 0
```

### 4.3 盘点差异处理器

**盘点差异处理实现**：

```python
class InventoryCountDifferenceProcessor:
    """盘点差异处理器"""

    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager

    def approve_differences(self, count_plan: Dict,
                          approval_data: Dict) -> Dict:
        """审批盘点差异"""
        for difference in count_plan["count_difference"]["differences"]:
            diff_approval = approval_data.get(difference["item_id"], {})

            if diff_approval.get("approved"):
                difference["adjustment_status"] = "Approved"
                difference["difference_reason"] = diff_approval.get("reason", "")

        return count_plan

    def adjust_inventory(self, count_plan: Dict) -> Dict:
        """调整库存"""
        for difference in count_plan["count_difference"]["differences"]:
            if difference["adjustment_status"] == "Approved":
                # 调整库存
                self.inventory_manager.adjust_inventory(
                    product_barcode=difference["product_barcode"],
                    location_code=difference["location_code"],
                    adjustment_quantity=difference["difference_quantity"]
                )

                difference["adjustment_status"] = "Adjusted"

        return count_plan
```

---

## 5. EPCIS集成实现

### 5.1 EPCIS事件生成器

**EPCIS事件生成实现**：

```python
from typing import Dict, List
from datetime import datetime

class EPCISEventGenerator:
    """EPCIS事件生成器"""

    def __init__(self):
        """初始化EPCIS事件生成器"""
        self.logger = logging.getLogger(__name__)
        self.event_types = ["ObjectEvent", "AggregationEvent", "TransactionEvent", "TransformationEvent"]
        self.valid_actions = ["ADD", "OBSERVE", "DELETE"]
        self.valid_biz_steps = ["receiving", "shipping", "storing", "picking"]

    def generate_inbound_event(self, inbound_order: Dict) -> Dict:
        """生成入库EPCIS事件"""
        event = {
            "event_time": datetime.now().isoformat(),
            "event_timezone_offset": "+08:00",
            "event_type": "ObjectEvent",
            "action": "ADD",
            "biz_step": "receiving",
            "disposition": "in_transit",
            "epc_list": [
                item["product_barcode"] for item in inbound_order["inbound_products"]["items"]
            ],
            "biz_location": {
                "id": inbound_order["inbound_order"]["warehouse_id"],
                "type": "urn:epcglobal:epcis:vtype:BusinessLocation"
            },
            "read_point": {
                "id": inbound_order["inbound_order"]["warehouse_id"],
                "type": "urn:epcglobal:epcis:vtype:ReadPoint"
            }
        }
        return event

    def generate_outbound_event(self, outbound_order: Dict) -> Dict:
        """生成出库EPCIS事件"""
        event = {
            "event_time": datetime.now().isoformat(),
            "event_timezone_offset": "+08:00",
            "event_type": "ObjectEvent",
            "action": "OBSERVE",
            "biz_step": "shipping",
            "disposition": "in_transit",
            "epc_list": [
                item["product_barcode"] for item in outbound_order["outbound_products"]["items"]
            ],
            "biz_location": {
                "id": outbound_order["outbound_order"]["warehouse_id"],
                "type": "urn:epcglobal:epcis:vtype:BusinessLocation"
            }
        }
        return event
```

---

## 6. WMS数据存储与分析

### 6.1 PostgreSQL WMS数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
from typing import Dict, List, Optional
from datetime import datetime

class WMSStorage:
    """WMS数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建WMS数据表"""
        # 入库单表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS inbound_orders (
                id BIGSERIAL PRIMARY KEY,
                inbound_id VARCHAR(20) UNIQUE NOT NULL,
                inbound_number VARCHAR(50) UNIQUE NOT NULL,
                supplier_id VARCHAR(50) NOT NULL,
                supplier_name VARCHAR(200),
                inbound_date DATE NOT NULL,
                inbound_type VARCHAR(50) NOT NULL,
                warehouse_id VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 入库明细表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS inbound_items (
                id BIGSERIAL PRIMARY KEY,
                item_id VARCHAR(20) UNIQUE NOT NULL,
                inbound_id VARCHAR(20) NOT NULL,
                product_barcode VARCHAR(50) NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                quantity INTEGER NOT NULL,
                batch_number VARCHAR(50),
                location_code VARCHAR(50),
                FOREIGN KEY (inbound_id) REFERENCES inbound_orders(inbound_id)
            )
        """)

        # 出库单表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS outbound_orders (
                id BIGSERIAL PRIMARY KEY,
                outbound_id VARCHAR(20) UNIQUE NOT NULL,
                outbound_number VARCHAR(50) UNIQUE NOT NULL,
                customer_id VARCHAR(50),
                customer_name VARCHAR(200),
                outbound_date DATE NOT NULL,
                outbound_type VARCHAR(50) NOT NULL,
                warehouse_id VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 出库明细表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS outbound_items (
                id BIGSERIAL PRIMARY KEY,
                item_id VARCHAR(20) UNIQUE NOT NULL,
                outbound_id VARCHAR(20) NOT NULL,
                product_barcode VARCHAR(50) NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                quantity INTEGER NOT NULL,
                picked_quantity INTEGER DEFAULT 0,
                location_code VARCHAR(50),
                FOREIGN KEY (outbound_id) REFERENCES outbound_orders(outbound_id)
            )
        """)

        # 库存表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id BIGSERIAL PRIMARY KEY,
                product_barcode VARCHAR(50) NOT NULL,
                warehouse_id VARCHAR(50) NOT NULL,
                location_code VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL,
                available_quantity INTEGER NOT NULL,
                reserved_quantity INTEGER DEFAULT 0,
                batch_number VARCHAR(50),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_barcode, warehouse_id, location_code, batch_number)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_inbound_orders_warehouse_date
            ON inbound_orders(warehouse_id, inbound_date DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_outbound_orders_warehouse_date
            ON outbound_orders(warehouse_id, outbound_date DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_inventory_product_location
            ON inventory(product_barcode, location_code)
        """)

        self.conn.commit()

    def store_inbound_order(self, inbound_order: Dict) -> int:
        """存储入库单"""
        self.cur.execute("""
            INSERT INTO inbound_orders (
                inbound_id, inbound_number, supplier_id, supplier_name,
                inbound_date, inbound_type, warehouse_id, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            inbound_order.get("inbound_id"),
            inbound_order.get("inbound_number"),
            inbound_order.get("inbound_order", {}).get("supplier_id"),
            inbound_order.get("inbound_order", {}).get("supplier_name"),
            inbound_order.get("inbound_order", {}).get("inbound_date"),
            inbound_order.get("inbound_order", {}).get("inbound_type"),
            inbound_order.get("inbound_order", {}).get("warehouse_id"),
            inbound_order.get("inbound_order", {}).get("status")
        ))
        self.conn.commit()
        order_id = self.cur.fetchone()[0]

        # 存储入库明细
        for item in inbound_order.get("inbound_products", {}).get("items", []):
            putaway_item = next(
                (p for p in inbound_order.get("inbound_putaway", {}).get("putaway_items", [])
                 if p["item_id"] == item["item_id"]),
                None
            )

            self.cur.execute("""
                INSERT INTO inbound_items (
                    item_id, inbound_id, product_barcode, product_name,
                    quantity, batch_number, location_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("item_id"),
                inbound_order.get("inbound_id"),
                item.get("product_barcode"),
                item.get("product_name"),
                item.get("quantity"),
                item.get("batch_number"),
                putaway_item.get("location_code") if putaway_item else None
            ))

            # 更新库存
            if putaway_item:
                self._update_inventory(
                    product_barcode=item.get("product_barcode"),
                    warehouse_id=inbound_order.get("inbound_order", {}).get("warehouse_id"),
                    location_code=putaway_item.get("location_code"),
                    quantity_change=item.get("quantity"),
                    batch_number=item.get("batch_number")
                )

        self.conn.commit()
        return order_id

    def store_outbound_order(self, outbound_order: Dict) -> int:
        """存储出库单"""
        self.cur.execute("""
            INSERT INTO outbound_orders (
                outbound_id, outbound_number, customer_id, customer_name,
                outbound_date, outbound_type, warehouse_id, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            outbound_order.get("outbound_id"),
            outbound_order.get("outbound_number"),
            outbound_order.get("outbound_order", {}).get("customer_id"),
            outbound_order.get("outbound_order", {}).get("customer_name"),
            outbound_order.get("outbound_order", {}).get("outbound_date"),
            outbound_order.get("outbound_order", {}).get("outbound_type"),
            outbound_order.get("outbound_order", {}).get("warehouse_id"),
            outbound_order.get("outbound_order", {}).get("status")
        ))
        self.conn.commit()
        order_id = self.cur.fetchone()[0]

        # 存储出库明细
        for item in outbound_order.get("outbound_products", {}).get("items", []):
            picking_items = [
                p for p in outbound_order.get("picking_management", {}).get("picking_items", [])
                if p["item_id"] == item["item_id"]
            ]

            picked_total = sum(p.get("picked_quantity", 0) for p in picking_items)

            self.cur.execute("""
                INSERT INTO outbound_items (
                    item_id, outbound_id, product_barcode, product_name,
                    quantity, picked_quantity, location_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("item_id"),
                outbound_order.get("outbound_id"),
                item.get("product_barcode"),
                item.get("product_name"),
                item.get("quantity"),
                picked_total,
                picking_items[0].get("location_code") if picking_items else None
            ))

            # 更新库存（出库）
            if picked_total > 0:
                for picking_item in picking_items:
                    self._update_inventory(
                        product_barcode=item.get("product_barcode"),
                        warehouse_id=outbound_order.get("outbound_order", {}).get("warehouse_id"),
                        location_code=picking_item.get("location_code"),
                        quantity_change=-picking_item.get("picked_quantity", 0)
                    )

        self.conn.commit()
        return order_id

    def _update_inventory(self, product_barcode: str, warehouse_id: str,
                         location_code: str, quantity_change: int,
                         batch_number: Optional[str] = None):
        """更新库存"""
        self.cur.execute("""
            INSERT INTO inventory (
                product_barcode, warehouse_id, location_code, quantity,
                available_quantity, batch_number
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_barcode, warehouse_id, location_code, batch_number)
            DO UPDATE SET
                quantity = inventory.quantity + %s,
                available_quantity = inventory.available_quantity + %s,
                last_updated = CURRENT_TIMESTAMP
        """, (
            product_barcode, warehouse_id, location_code,
            quantity_change, quantity_change, batch_number,
            quantity_change, quantity_change
        ))

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 WMS数据分析查询

**数据分析查询实现**：

```python
    def get_inbound_statistics(self, warehouse_id: str, days: int = 30) -> Dict:
        """查询入库统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_orders,
                SUM(quantity) as total_quantity,
                COUNT(DISTINCT supplier_id) as total_suppliers
            FROM inbound_orders io
            JOIN inbound_items ii ON io.inbound_id = ii.inbound_id
            WHERE io.warehouse_id = %s
            AND io.inbound_date >= CURRENT_DATE - INTERVAL '%s days'
        """, (warehouse_id, days))
        row = self.cur.fetchone()
        return {
            "total_orders": row[0],
            "total_quantity": row[1],
            "total_suppliers": row[2]
        }

    def get_outbound_statistics(self, warehouse_id: str, days: int = 30) -> Dict:
        """查询出库统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_orders,
                SUM(quantity) as total_quantity,
                COUNT(DISTINCT customer_id) as total_customers
            FROM outbound_orders oo
            JOIN outbound_items oi ON oo.outbound_id = oi.outbound_id
            WHERE oo.warehouse_id = %s
            AND oo.outbound_date >= CURRENT_DATE - INTERVAL '%s days'
        """, (warehouse_id, days))
        row = self.cur.fetchone()
        return {
            "total_orders": row[0],
            "total_quantity": row[1],
            "total_customers": row[2]
        }

    def get_inventory_turnover(self, warehouse_id: str, days: int = 30) -> Dict:
        """查询库存周转率"""
        # 计算平均库存
        self.cur.execute("""
            SELECT AVG(quantity) as avg_inventory
            FROM inventory
            WHERE warehouse_id = %s
            AND last_updated >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (warehouse_id, days))
        avg_inventory = self.cur.fetchone()[0] or 0

        # 计算出库总量
        self.cur.execute("""
            SELECT SUM(quantity) as total_outbound
            FROM outbound_orders oo
            JOIN outbound_items oi ON oo.outbound_id = oi.outbound_id
            WHERE oo.warehouse_id = %s
            AND oo.outbound_date >= CURRENT_DATE - INTERVAL '%s days'
        """, (warehouse_id, days))
        total_outbound = self.cur.fetchone()[0] or 0

        turnover_rate = (total_outbound / avg_inventory) if avg_inventory > 0 else 0

        return {
            "avg_inventory": float(avg_inventory),
            "total_outbound": float(total_outbound),
            "turnover_rate": float(turnover_rate)
        }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
