# MES Schema实践案例

## 📑 目录

- [MES Schema实践案例](#mes-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：生产执行管理系统](#2-案例1生产执行管理系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：质量追溯系统](#3-案例2质量追溯系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：ERP到MES订单转换](#4-案例3erp到mes订单转换)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：设备OEE监控和分析](#5-案例4设备oee监控和分析)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：MES数据分析和报表](#6-案例5mes数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供MES Schema在实际应用中的实践案例。

---

## 2. 案例1：生产执行管理系统

### 2.1 场景描述

**业务背景**：
制造企业需要管理生产订单的执行过程，跟踪
工序进度，监控资源使用，确保按时交付。

**技术挑战**：

- 需要接收ERP生产订单
- 需要跟踪生产执行进度
- 需要实时数据采集
- 需要资源使用监控

**解决方案**：
使用ERPToMESConverter转换ERP订单，使用
ProductionDataCollector采集生产数据，使用MESStorage
存储数据，实现完整的生产执行管理。

### 2.2 Schema定义

**生产执行管理Schema**：

```json
{
  "production_order": {
    "order_id": "PO20250121001",
    "order_number": "ORD-2025-001",
    "product_id": "PROD001",
    "product_name": "产品A",
    "order_info": {
      "order_quantity": 1000,
      "unit": "pieces",
      "planned_start_date": "2025-01-21T08:00:00Z",
      "planned_end_date": "2025-01-23T18:00:00Z",
      "delivery_date": "2025-01-24T00:00:00Z",
      "priority": "High",
      "order_type": "MakeToOrder"
    },
    "order_status": {
      "status": "InProgress",
      "progress_percentage": 45.5,
      "completed_quantity": 455,
      "rejected_quantity": 5
    }
  },
  "production_execution": {
    "execution_id": "EXE20250121001",
    "order_id": "PO20250121001",
    "work_order_id": "WO-2025-001",
    "current_step": 3,
    "status": "InProgress",
    "start_time": "2025-01-21T08:30:00Z"
  }
}
```

### 2.3 实现代码

**完整的生产执行管理实现**：

```python
from erp_to_mes_converter import ERPToMESConverter
from production_data_collector import ProductionDataCollector
from mes_storage import MESStorage
import time
from datetime import datetime

# 初始化组件
storage = MESStorage("postgresql://user:pass@localhost/mes")
converter = ERPToMESConverter()

# ERP订单数据
erp_order_data = {
    "order_id": "PO20250121001",
    "order_number": "ORD-2025-001",
    "product_id": "PROD001",
    "product_name": "产品A",
    "quantity": 1000,
    "unit": "pieces",
    "start_date": "2025-01-21T08:00:00Z",
    "end_date": "2025-01-23T18:00:00Z",
    "delivery_date": "2025-01-24T00:00:00Z",
    "priority": "High",
    "order_type": "MakeToOrder",
    "material_requirements": [
        {
            "material_id": "MAT001",
            "material_name": "原材料A",
            "quantity": 500,
            "unit": "kg"
        }
    ],
    "work_centers": ["WC001", "WC002", "WC003"]
}

# 转换为MES订单
mes_order = converter.convert_erp_order_to_mes(erp_order_data)
print(f"Converted ERP order to MES order: {mes_order['order_number']}")

# 存储生产订单
order_id = storage.store_production_order(mes_order)
print(f"Stored production order: {order_id}")

# 创建生产执行
execution_data = {
    "execution_id": "EXE20250121001",
    "order_id": mes_order["order_id"],
    "work_order_id": "WO-2025-001",
    "execution_status": {
        "current_step": 1,
        "status": "InProgress",
        "start_time": datetime.now(),
        "operator": "张三",
        "shift": "Day"
    }
}

execution_id = storage.store_production_execution(execution_data)
print(f"Created production execution: {execution_id}")

# 配置生产设备数据采集
equipment_configs = [
    {
        "equipment_id": "EQ001",
        "host": "192.168.1.101",
        "port": 502
    },
    {
        "equipment_id": "EQ002",
        "host": "192.168.1.102",
        "port": 502
    }
]

# 创建数据采集器
collectors = {}
for eq_config in equipment_configs:
    collector = ProductionDataCollector(
        eq_config["equipment_id"],
        eq_config["host"],
        eq_config["port"]
    )
    if collector.connect():
        collectors[eq_config["equipment_id"]] = collector

# 周期性数据采集
collection_interval = 10  # 秒
collection_duration = 300  # 秒

start_time = time.time()
total_production = 0
total_good = 0
total_reject = 0

while time.time() - start_time < collection_duration:
    for equipment_id, collector in collectors.items():
        # 读取生产数据
        prod_data = collector.read_production_data()
        if prod_data:
            storage.store_production_data(prod_data)

            total_production += prod_data.get("production_count", 0)
            total_good += prod_data.get("good_count", 0)
            total_reject += prod_data.get("reject_count", 0)

            print(f"{datetime.now()}: {equipment_id} - "
                  f"Production: {prod_data['production_count']}, "
                  f"Good: {prod_data['good_count']}, "
                  f"Reject: {prod_data['reject_count']}")

    # 更新订单进度
    if total_production > 0:
        progress = (total_good / mes_order["order_info"]["order_quantity"]) * 100
        mes_order["order_status"]["progress_percentage"] = progress
        mes_order["order_status"]["completed_quantity"] = total_good
        mes_order["order_status"]["rejected_quantity"] = total_reject
        storage.store_production_order(mes_order)

    time.sleep(collection_interval)

# 查询订单统计
stats = storage.get_production_order_statistics(days=1)
print(f"\nProduction Order Statistics (last day):")
print(f"  Total orders: {stats['total_orders']}")
print(f"  Completed orders: {stats['completed_orders']}")
print(f"  In progress orders: {stats['in_progress_orders']}")
print(f"  Average progress: {stats['avg_progress']:.2f}%")
```

---

## 3. 案例2：质量追溯系统

### 3.1 场景描述

**业务背景**：
制造企业需要实现产品质量追溯，从原料到
成品的全程追溯，确保质量可追溯。

**技术挑战**：

- 需要记录质量检测数据
- 需要构建追溯链
- 需要生成质量报告
- 需要不合格品处理

**解决方案**：
使用QualityDataCollector采集质量数据，使用
MESStorage存储质量记录，实现完整的质量追溯。

### 3.2 Schema定义

**质量追溯Schema**：

```json
{
  "quality_traceability": {
    "traceability_id": "TRACE20250121001",
    "order_id": "PO20250121001",
    "product_id": "PROD001",
    "quality_inspection": {
      "inspections": [
        {
          "inspection_id": "INS001",
          "inspection_type": "Incoming",
          "inspection_item": "原材料A质量检测",
          "inspection_result": "Pass",
          "inspection_time": "2025-01-21T08:00:00Z",
          "inspector": "质检员A"
        },
        {
          "inspection_id": "INS002",
          "inspection_type": "Final",
          "inspection_item": "成品质量检测",
          "inspection_result": "Pass",
          "inspection_time": "2025-01-23T16:00:00Z",
          "inspector": "质检员B"
        }
      ]
    },
    "traceability_chain": {
      "material_traceability": [
        {
          "material_id": "MAT001",
          "material_batch": "BATCH001",
          "supplier": "供应商A"
        }
      ],
      "process_traceability": [
        {
          "process_step": 1,
          "equipment_id": "EQ001",
          "operator": "张三",
          "process_time": "2025-01-21T09:00:00Z"
        }
      ]
    }
  }
}
```

### 3.3 实现代码

**完整的质量追溯实现**：

```python
from quality_data_collector import QualityDataCollector
from mes_storage import MESStorage
from datetime import datetime

# 初始化组件
storage = MESStorage("postgresql://user:pass@localhost/mes")

# 配置质量检测站
inspection_stations = [
    {
        "station_id": "INS001",
        "host": "192.168.2.101",
        "port": 502
    },
    {
        "station_id": "INS002",
        "host": "192.168.2.102",
        "port": 502
    }
]

# 创建质量数据采集器
collectors = {}
for station_config in inspection_stations:
    collector = QualityDataCollector(
        station_config["station_id"],
        station_config["host"],
        station_config["port"]
    )
    if collector.connect():
        collectors[station_config["station_id"]] = collector

# 质量检测流程
order_id = "PO20250121001"
product_id = "PROD001"

# 来料检测
incoming_inspection = {
    "inspection_id": f"INS_{product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "order_id": order_id,
    "product_id": product_id,
    "inspection_type": "Incoming",
    "inspection_item": "原材料质量检测",
    "inspection_result": "Pass",
    "inspection_value": 95.5,
    "inspection_unit": "score",
    "inspection_time": datetime.now(),
    "inspector": "质检员A"
}

storage.store_quality_inspection(incoming_inspection)
print(f"Stored incoming inspection: {incoming_inspection['inspection_id']}")

# 过程检测
process_inspection = {
    "inspection_id": f"INS_{product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "order_id": order_id,
    "product_id": product_id,
    "inspection_type": "InProcess",
    "inspection_item": "工序质量检测",
    "inspection_result": "Pass",
    "inspection_value": 98.0,
    "inspection_unit": "score",
    "inspection_time": datetime.now(),
    "inspector": "质检员B"
}

storage.store_quality_inspection(process_inspection)
print(f"Stored process inspection: {process_inspection['inspection_id']}")

# 最终检测（从检测站读取）
final_inspection_result = collectors["INS002"].read_inspection_result(product_id)
if final_inspection_result:
    final_inspection_result["order_id"] = order_id
    storage.store_quality_inspection(final_inspection_result)
    print(f"Stored final inspection: {final_inspection_result['inspection_id']}")

# 查询质量统计
quality_stats = storage.get_quality_statistics(order_id)
print(f"\nQuality Statistics for Order {order_id}:")
print(f"  Total inspections: {quality_stats['total_inspections']}")
print(f"  Pass count: {quality_stats['pass_count']}")
print(f"  Fail count: {quality_stats['fail_count']}")
print(f"  Pass rate: {quality_stats['pass_rate']:.2f}%")
```

---

## 4. 案例3：ERP到MES订单转换

### 4.1 场景描述

**业务背景**：
制造企业需要将ERP系统的生产订单转换为
MES系统的生产订单，实现ERP和MES系统集成。

**技术挑战**：

- 需要解析ERP订单数据
- 需要转换为MES格式
- 需要数据验证
- 需要错误处理

**解决方案**：
使用ERPOrderParser解析ERP订单，使用
ERPToMESConverter转换为MES格式。

### 4.2 实现代码

**完整的ERP到MES转换实现**：

```python
from erp_to_mes_converter import ERPToMESConverter
from mes_storage import MESStorage
import json

# 初始化组件
storage = MESStorage("postgresql://user:pass@localhost/mes")
converter = ERPToMESConverter()

# 从ERP系统获取订单（示例）
erp_orders = [
    {
        "order_id": "PO20250121001",
        "order_number": "ORD-2025-001",
        "product_id": "PROD001",
        "product_name": "产品A",
        "quantity": 1000,
        "start_date": "2025-01-21T08:00:00Z",
        "end_date": "2025-01-23T18:00:00Z",
        "delivery_date": "2025-01-24T00:00:00Z",
        "priority": "High",
        "material_requirements": [
            {"material_id": "MAT001", "material_name": "原材料A", "quantity": 500}
        ],
        "work_centers": ["WC001", "WC002"]
    },
    {
        "order_id": "PO20250121002",
        "order_number": "ORD-2025-002",
        "product_id": "PROD002",
        "product_name": "产品B",
        "quantity": 500,
        "start_date": "2025-01-22T08:00:00Z",
        "end_date": "2025-01-24T18:00:00Z",
        "delivery_date": "2025-01-25T00:00:00Z",
        "priority": "Normal",
        "material_requirements": [
            {"material_id": "MAT002", "material_name": "原材料B", "quantity": 300}
        ],
        "work_centers": ["WC003"]
    }
]

# 批量转换和存储
converted_orders = []
for erp_order in erp_orders:
    mes_order = converter.convert_erp_order_to_mes(erp_order)
    order_id = storage.store_production_order(mes_order)
    converted_orders.append(mes_order)
    print(f"Converted and stored: {mes_order['order_number']}")

print(f"\nConverted {len(converted_orders)} orders from ERP to MES")
```

---

## 5. 案例4：设备OEE监控和分析

### 5.1 场景描述

**业务背景**：
制造企业需要监控设备OEE（Overall Equipment
Effectiveness），分析设备效率，优化生产性能。

**技术挑战**：

- 需要实时设备状态监控
- 需要计算OEE指标
- 需要设备性能分析
- 需要效率优化建议

**解决方案**：
使用ProductionDataCollector采集设备数据，计算
OEE指标，使用MESStorage存储设备状态。

### 5.2 实现代码

**完整的设备OEE监控实现**：

```python
from production_data_collector import ProductionDataCollector
from mes_storage import MESStorage
import time
from datetime import datetime, timedelta

# 初始化存储
storage = MESStorage("postgresql://user:pass@localhost/mes")

# 配置设备
equipment_config = {
    "equipment_id": "EQ001",
    "equipment_code": "EQ-001",
    "host": "192.168.1.101",
    "port": 502
}

# 创建数据采集器
collector = ProductionDataCollector(
    equipment_config["equipment_id"],
    equipment_config["host"],
    equipment_config["port"]
)

if collector.connect():
    print(f"Connected to equipment {equipment_config['equipment_id']}")

# 计算OEE的函数
def calculate_oee(availability: float, utilization: float, performance: float, quality_rate: float) -> float:
    """计算OEE"""
    return (availability * utilization * performance * quality_rate) / 10000.0

# 监控周期
monitoring_duration = 3600  # 秒
monitoring_interval = 60  # 秒

start_time = time.time()
total_running_time = 0
total_production_time = 0
total_production_count = 0
total_good_count = 0
total_reject_count = 0

planned_production_time = monitoring_duration
standard_cycle_time = 30.0  # 秒

while time.time() - start_time < monitoring_duration:
    # 读取生产数据
    prod_data = collector.read_production_data()
    if prod_data:
        storage.store_production_data(prod_data)

        status = prod_data.get("status", "Idle")
        if status == "Running":
            total_running_time += monitoring_interval
            total_production_count += prod_data.get("production_count", 0)
            total_good_count += prod_data.get("good_count", 0)
            total_reject_count += prod_data.get("reject_count", 0)

    # 计算OEE指标
    availability = (total_running_time / planned_production_time * 100) if planned_production_time > 0 else 0
    utilization = (total_running_time / planned_production_time * 100) if planned_production_time > 0 else 0
    performance = (standard_cycle_time / (total_production_time / total_production_count * 100)) if total_production_count > 0 else 0
    quality_rate = (total_good_count / total_production_count * 100) if total_production_count > 0 else 0

    oee = calculate_oee(availability, utilization, performance, quality_rate)

    # 存储设备状态
    equipment_status = {
        "equipment_id": equipment_config["equipment_id"],
        "equipment_code": equipment_config["equipment_code"],
        "operational_status": prod_data.get("status", "Idle") if prod_data else "Idle",
        "availability": availability,
        "utilization": utilization,
        "performance": performance,
        "quality_rate": quality_rate,
        "oee": oee
    }

    storage.store_equipment_status(equipment_status)

    print(f"{datetime.now()}: OEE = {oee:.2f}%, "
          f"Availability = {availability:.2f}%, "
          f"Utilization = {utilization:.2f}%, "
          f"Performance = {performance:.2f}%, "
          f"Quality = {quality_rate:.2f}%")

    time.sleep(monitoring_interval)

# 查询OEE统计
oee_stats = storage.get_equipment_oee_statistics(equipment_config["equipment_id"], days=1)
print(f"\nEquipment OEE Statistics (last day):")
print(f"  Avg OEE: {oee_stats['avg_oee']:.2f}%")
print(f"  Avg Availability: {oee_stats['avg_availability']:.2f}%")
print(f"  Avg Utilization: {oee_stats['avg_utilization']:.2f}%")
print(f"  Avg Performance: {oee_stats['avg_performance']:.2f}%")
print(f"  Avg Quality Rate: {oee_stats['avg_quality_rate']:.2f}%")
```

---

## 6. 案例5：MES数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储MES数据，支持数据查询、
分析和报表生成。

### 6.2 实现代码

**完整的数据分析实现**：

```python
from mes_storage import MESStorage
from datetime import datetime, timedelta

storage = MESStorage("postgresql://user:pass@localhost/mes")

# 查询生产订单统计
order_stats = storage.get_production_order_statistics(days=30)
print("Production Order Statistics (30 days):")
print(f"  Total orders: {order_stats['total_orders']}")
print(f"  Completed orders: {order_stats['completed_orders']}")
print(f"  In progress orders: {order_stats['in_progress_orders']}")
print(f"  Average progress: {order_stats['avg_progress']:.2f}%")
print(f"  Total quantity: {order_stats['total_quantity']}")
print(f"  Total completed: {order_stats['total_completed']}")
print(f"  Total rejected: {order_stats['total_rejected']}")

# 查询质量统计
order_id = "PO20250121001"
quality_stats = storage.get_quality_statistics(order_id)
print(f"\nQuality Statistics for Order {order_id}:")
print(f"  Total inspections: {quality_stats['total_inspections']}")
print(f"  Pass rate: {quality_stats['pass_rate']:.2f}%")

# 查询设备OEE统计
equipment_id = "EQ001"
oee_stats = storage.get_equipment_oee_statistics(equipment_id, days=7)
print(f"\nEquipment OEE Statistics (7 days):")
print(f"  Avg OEE: {oee_stats['avg_oee']:.2f}%")
print(f"  Avg Availability: {oee_stats['avg_availability']:.2f}%")
print(f"  Avg Utilization: {oee_stats['avg_utilization']:.2f}%")
print(f"  Avg Performance: {oee_stats['avg_performance']:.2f}%")
print(f"  Avg Quality Rate: {oee_stats['avg_quality_rate']:.2f}%")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
