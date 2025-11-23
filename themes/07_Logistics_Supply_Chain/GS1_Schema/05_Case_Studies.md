# GS1 Schema实践案例

## 📑 目录

- [GS1 Schema实践案例](#gs1-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：零售供应链GTIN管理](#2-案例1零售供应链gtin管理)
  - [3. 案例2：物流GLN位置管理](#3-案例2物流gln位置管理)
  - [4. 案例3：包装SSCC追踪](#4-案例3包装sscc追踪)
  - [5. 案例4：EPCIS供应链追溯](#5-案例4-epcis供应链追溯)
  - [6. 案例5：GS1数据存储与分析](#6-案例5-gs1数据存储与分析)

---

## 1. 案例概述

本文档提供GS1 Schema在实际应用中的案例，
涵盖GTIN、GLN、SSCC、EPCIS等场景。

---

## 2. 案例1：零售供应链GTIN管理

### 2.1 场景描述

零售企业需要管理产品的GTIN标识，
支持产品信息查询和供应链管理。

### 2.2 实现方案

**GTIN数据结构**：

```python
gtin_data = {
    "gtin_type": "GTIN13",
    "gtin_identifier": "1234567890128",
    "company_prefix": "1234567",
    "item_reference": "89012",
    "check_digit": "8",
    "product_name": "Premium Coffee Beans 500g",
    "brand_name": "CoffeeMaster",
    "product_category": "Food & Beverage",
    "unit_of_measure": "EA",
    "net_weight": 0.5,
    "gross_weight": 0.55,
    "dimensions_length": 15.0,
    "dimensions_width": 10.0,
    "dimensions_height": 8.0,
    "dimensions_unit": "CM"
}
```

**GTIN存储示例**：

```python
from gs1_storage import GS1Storage

# 初始化存储
storage = GS1Storage("postgresql://user:password@localhost/gs1_db")

# 存储GTIN数据
gtin_id = storage.store_gtin(gtin_data)
print(f"GTIN stored with ID: {gtin_id}")

# 查询GTIN数据
gtin_info = storage.query_gtin_by_identifier("1234567890128")
print(f"Product: {gtin_info['product_name']}")
print(f"Brand: {gtin_info['brand_name']}")
```

---

## 3. 案例2：物流GLN位置管理

### 3.1 场景描述

物流公司需要管理仓库、配送中心等位置的GLN标识，
支持位置信息查询和物流路径规划。

### 3.2 实现方案

**GLN数据结构**：

```python
gln_data = {
    "location_identifier": "1234567890123",
    "location_type": "PhysicalLocation",
    "location_name": "Shanghai Distribution Center",
    "street_address": "123 Logistics Avenue",
    "city": "Shanghai",
    "state_province": "Shanghai",
    "postal_code": "200000",
    "country": "CN",
    "phone": "+86-21-12345678",
    "email": "shanghai@logistics.com",
    "website": "https://www.logistics.com",
    "latitude": 31.2304,
    "longitude": 121.4737,
    "gln_status": "Active"
}
```

**GLN存储示例**：

```python
# 存储GLN数据
gln_id = storage.store_gln(gln_data)
print(f"GLN stored with ID: {gln_id}")

# 查询GLN数据
gln_info = storage.query_gln_by_identifier("1234567890123")
print(f"Location: {gln_info['location_name']}")
print(f"Address: {gln_info['street_address']}, {gln_info['city']}")
```

---

## 4. 案例3：包装SSCC追踪

### 4.1 场景描述

制造商需要管理包装箱的SSCC标识，
支持包装层级关系和运输追踪。

### 4.2 实现方案

**SSCC数据结构**：

```python
sscc_data = {
    "sscc_identifier": "012345678901234567",
    "extension_digit": "0",
    "company_prefix": "12345678",
    "serial_reference": "90123456",
    "check_digit": "7",
    "packaging_type": "Pallet",
    "packaging_level": 2,
    "parent_sscc": None,
    "quantity": 24,
    "shipper_gln": "1234567890123",
    "receiver_gln": "9876543210987",
    "ship_date": "2025-01-15",
    "expected_delivery_date": "2025-01-20"
}
```

**SSCC存储示例**：

```python
# 存储SSCC数据
sscc_id = storage.store_sscc(sscc_data)
print(f"SSCC stored with ID: {sscc_id}")

# 查询SSCC数据
sscc_info = storage.query_sscc_by_identifier("012345678901234567")
print(f"Packaging Type: {sscc_info['packaging_type']}")
print(f"Quantity: {sscc_info['quantity']}")
print(f"Shipper: {sscc_info['shipper_gln']}")
print(f"Receiver: {sscc_info['receiver_gln']}")
```

---

## 5. 案例4：EPCIS供应链追溯

### 5.1 场景描述

食品企业需要实现产品全程追溯，
使用EPCIS事件记录产品在供应链中的流转过程。

### 5.2 实现方案

**EPCIS事件数据结构**：

```python
# ObjectEvent - 产品入库事件
object_event_1 = {
    "event_id": "urn:epc:id:objectevent:1.0",
    "event_time": datetime(2025, 1, 10, 10, 0, 0),
    "event_timezone": "+08:00",
    "event_type": "ObjectEvent",
    "action": "ADD",
    "biz_step": "urn:epcglobal:cbv:bizstep:receiving",
    "disposition": "urn:epcglobal:cbv:disp:in_progress",
    "read_point": "urn:epc:id:gln:1234567890123.warehouse1",
    "biz_location": "urn:epc:id:gln:1234567890123",
    "epc_list": [
        "urn:epc:id:sgtin:1234567.89012.1001",
        "urn:epc:id:sgtin:1234567.89012.1002"
    ],
    "biz_transaction_list": [
        {"type": "urn:epcglobal:cbv:btt:po", "value": "PO-2025-001"}
    ]
}

# AggregationEvent - 包装聚合事件
aggregation_event = {
    "event_id": "urn:epc:id:aggregationevent:1.0",
    "event_time": datetime(2025, 1, 10, 11, 0, 0),
    "event_timezone": "+08:00",
    "event_type": "AggregationEvent",
    "action": "ADD",
    "biz_step": "urn:epcglobal:cbv:bizstep:packing",
    "disposition": "urn:epcglobal:cbv:disp:in_progress",
    "read_point": "urn:epc:id:gln:1234567890123.packing1",
    "biz_location": "urn:epc:id:gln:1234567890123",
    "parent_id": "urn:epc:id:sscc:12345678.90123456.7",
    "child_epcs": [
        "urn:epc:id:sgtin:1234567.89012.1001",
        "urn:epc:id:sgtin:1234567.89012.1002"
    ]
}

# TransactionEvent - 销售交易事件
transaction_event = {
    "event_id": "urn:epc:id:transactionevent:1.0",
    "event_time": datetime(2025, 1, 15, 14, 0, 0),
    "event_timezone": "+08:00",
    "event_type": "TransactionEvent",
    "action": "OBSERVE",
    "biz_step": "urn:epcglobal:cbv:bizstep:selling",
    "disposition": "urn:epcglobal:cbv:disp:sold",
    "read_point": "urn:epc:id:gln:9876543210987.store1",
    "biz_location": "urn:epc:id:gln:9876543210987",
    "epc_list": [
        "urn:epc:id:sgtin:1234567.89012.1001"
    ],
    "biz_transaction_list": [
        {"type": "urn:epcglobal:cbv:btt:invoice", "value": "INV-2025-001"}
    ]
}
```

**EPCIS事件存储示例**：

```python
# 存储EPCIS事件
event_id_1 = storage.store_epcis_event(object_event_1)
event_id_2 = storage.store_epcis_event(aggregation_event)
event_id_3 = storage.store_epcis_event(transaction_event)

print(f"Events stored: {event_id_1}, {event_id_2}, {event_id_3}")

# 查询产品追溯路径
epc = "urn:epc:id:sgtin:1234567.89012.1001"
trace_path = storage.query_epcis_events_by_epc(epc)

print(f"Trace path for EPC {epc}:")
for event in trace_path:
    print(f"  {event['event_time']}: {event['biz_step']} at {event['biz_location']}")
```

---

## 6. 案例5：GS1数据存储与分析

### 6.1 场景描述

企业需要存储和分析GS1数据，
支持供应链数据统计和报表生成。

### 6.2 实现方案

**GS1数据统计查询**：

```python
from datetime import datetime, timedelta

# 查询GTIN使用统计
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

statistics = storage.query_gtin_statistics(start_date, end_date)
print("GTIN Statistics (Last 30 days):")
for stat in statistics:
    print(f"  {stat[0]}: {stat[1]} GTINs, {stat[2]} events")

# 查询供应链追溯路径
epc = "urn:epc:id:sgtin:1234567.89012.1001"
trace_path = storage.query_supply_chain_trace(epc)

print(f"\nSupply Chain Trace for {epc}:")
for i, event in enumerate(trace_path, 1):
    print(f"  Step {i}: {event['event_time']} - {event['biz_step']}")
    print(f"    Location: {event['biz_location']}")
    print(f"    Action: {event['action']}")
```

**GS1数据分析报表**：

```python
def generate_gs1_analytics_report(storage: GS1Storage, start_date: datetime, end_date: datetime):
    """生成GS1数据分析报表"""
    cursor = storage.conn.cursor()

    # 1. GTIN使用统计
    cursor.execute("""
        SELECT
            g.gtin_type,
            COUNT(DISTINCT g.gtin_identifier) as gtin_count,
            COUNT(DISTINCT e.id) as event_count
        FROM gtin_data g
        LEFT JOIN epcis_epc_list el ON el.epc LIKE '%' || g.gtin_identifier || '%'
        LEFT JOIN epcis_events e ON e.id = el.event_id
        WHERE e.event_time BETWEEN %s AND %s
        GROUP BY g.gtin_type
    """, (start_date, end_date))
    gtin_stats = cursor.fetchall()

    # 2. GLN位置统计
    cursor.execute("""
        SELECT
            gl.location_type,
            COUNT(DISTINCT gl.location_identifier) as location_count,
            COUNT(DISTINCT e.biz_location) as event_location_count
        FROM gln_data gl
        LEFT JOIN epcis_events e ON e.biz_location LIKE '%' || gl.location_identifier || '%'
        WHERE e.event_time BETWEEN %s AND %s OR e.event_time IS NULL
        GROUP BY gl.location_type
    """, (start_date, end_date))
    gln_stats = cursor.fetchall()

    # 3. EPCIS事件类型统计
    cursor.execute("""
        SELECT
            event_type,
            action,
            COUNT(*) as event_count
        FROM epcis_events
        WHERE event_time BETWEEN %s AND %s
        GROUP BY event_type, action
        ORDER BY event_count DESC
    """, (start_date, end_date))
    event_stats = cursor.fetchall()

    cursor.close()

    return {
        "gtin_statistics": gtin_stats,
        "gln_statistics": gln_stats,
        "event_statistics": event_stats
    }

# 生成报表
report = generate_gs1_analytics_report(storage, start_date, end_date)
print("GS1 Analytics Report:")
print(f"GTIN Statistics: {report['gtin_statistics']}")
print(f"GLN Statistics: {report['gln_statistics']}")
print(f"Event Statistics: {report['event_statistics']}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
