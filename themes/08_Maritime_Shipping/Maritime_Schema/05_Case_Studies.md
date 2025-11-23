# 海运与航运Schema实践案例

## 📑 目录

- [海运与航运Schema实践案例](#海运与航运schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：船舶信息管理](#2-案例1船舶信息管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：货物追踪系统](#3-案例2货物追踪系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：航线规划系统](#4-案例3航线规划系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：EDIFACT到XML转换](#5-案例4edifact到xml转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：海运航运数据存储系统](#6-案例5海运航运数据存储系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供海运与航运Schema在实际应用中的实践案例。

---

## 2. 案例1：船舶信息管理和位置追踪

### 2.1 场景描述

**业务背景**：
航运公司需要管理船舶信息，实时追踪船舶位置，监控船舶状态，
并预测到达时间，优化航线规划。

**技术挑战**：
- 需要实时接收AIS位置数据
- 需要计算船舶速度和航向
- 需要预测到达时间
- 需要存储大量位置数据

**解决方案**：
使用VesselPositionTracker实现船舶位置追踪，集成AIS数据源，
实时更新船舶位置并计算航行参数。

### 2.2 Schema定义

详见第2.2节原始定义。

### 2.3 实现代码

**完整的船舶管理和位置追踪实现**：

```python
from maritime_storage import MaritimeStorage
from vessel_position_tracker import VesselPositionTracker
from datetime import datetime, timedelta

# 初始化存储和追踪器
storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")
tracker = VesselPositionTracker(storage)

# 注册船舶
vessel_data = {
    "vessel_id": "VESSEL001",
    "imo_number": "1234567",
    "vessel_name": "MV OCEAN STAR",
    "vessel_type": "ContainerShip",
    "flag_state": "SG",
    "call_sign": "9V1234",
    "mmsi": "563123456",
    "gross_tonnage": 50000.00,
    "net_tonnage": 30000.00,
    "deadweight_tonnage": 40000.00,
    "length_overall": 300.00,
    "breadth": 40.00,
    "draft": 12.50,
    "year_built": 2020,
    "builder": "Shipyard Co."
}

vessel_id = storage.store_vessel(vessel_data)
print(f"Registered vessel: {vessel_id}")

# 更新船舶位置（模拟AIS数据）
positions = [
    {"latitude": 1.234567, "longitude": 103.456789, "course": 45.5, "speed": 18.5, "heading": 45.0},
    {"latitude": 1.245678, "longitude": 103.467890, "course": 46.0, "speed": 19.0, "heading": 46.0},
    {"latitude": 1.256789, "longitude": 103.478901, "course": 45.8, "speed": 18.8, "heading": 45.8}
]

for i, pos in enumerate(positions):
    position_data = {
        **pos,
        "position_time": datetime.now() + timedelta(hours=i)
    }
    tracker.update_position("VESSEL001", position_data)
    print(f"Updated position {i+1}: {pos['latitude']}, {pos['longitude']}")

# 获取当前位置
current_pos = tracker.get_current_position("VESSEL001")
if current_pos:
    print(f"\nCurrent position:")
    print(f"  Latitude: {current_pos['latitude']}")
    print(f"  Longitude: {current_pos['longitude']}")
    print(f"  Speed: {current_pos['speed']} knots")
    print(f"  Course: {current_pos['course']}°")

# 估算到达时间（新加坡港）
singapore_lat = 1.2897
singapore_lon = 103.8501
eta = tracker.estimate_arrival_time("VESSEL001", singapore_lat, singapore_lon)
if eta:
    print(f"\nEstimated arrival time: {eta}")

# 获取船舶轨迹
track = tracker.get_vessel_track("VESSEL001", hours=24)
print(f"\nVessel track (24h): {len(track)} positions")

# 查询位置统计
stats = storage.get_vessel_position_statistics(
    "VESSEL001",
    datetime.now() - timedelta(days=1)
)
print(f"\nPosition statistics:")
print(f"  Position count: {stats['position_count']}")
print(f"  Avg speed: {stats['avg_speed']:.2f} knots")
print(f"  Max speed: {stats['max_speed']:.2f} knots")
```

---

## 3. 案例2：货物全程追踪系统

### 3.1 场景描述

**业务背景**：
货主和收货人需要实时追踪货物状态，从预订、装船、运输到卸船的
全程追踪，确保货物安全和及时交付。

**技术挑战**：
- 需要实时更新货物状态
- 需要记录所有追踪事件
- 需要支持多货物批量追踪
- 需要生成追踪报告

**解决方案**：
使用CargoTrackingSystem实现货物追踪，集成EDIFACT消息处理，
自动更新货物状态并记录追踪事件。

### 3.2 Schema定义

详见第3.2节原始定义。

### 3.3 实现代码

**完整的货物追踪系统实现**：

```python
from maritime_storage import MaritimeStorage
from cargo_tracking_system import CargoTrackingSystem
from datetime import datetime

# 初始化存储和追踪系统
storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")
tracking_system = CargoTrackingSystem(storage)

# 创建货物
cargo_data = {
    "cargo_id": "CARGO20250121001",
    "cargo_name": "电子产品",
    "cargo_type": "Container",
    "shipper": "ABC Trading Co.",
    "consignee": "XYZ Import Co.",
    "weight": 20000.00,
    "volume": 50.00,
    "quantity": 100,
    "unit": "pieces",
    "hs_code": "85171200",
    "value": 500000.00,
    "currency": "USD",
    "status": "Booked",
    "loading_port": "Shanghai",
    "loading_port_code": "CNSHA",
    "discharge_port": "Singapore",
    "discharge_port_code": "SGSIN",
    "loading_date": datetime(2025, 1, 20, 10, 0, 0),
    "vessel_id": "VESSEL001",
    "container_number": "CONT1234567"
}

cargo_id = storage.store_cargo(cargo_data)
print(f"Created cargo: {cargo_id}")

# 记录货物事件
events = [
    {
        "event_type": "Booked",
        "event_location": "Shanghai",
        "event_description": "货物预订"
    },
    {
        "event_type": "Loaded",
        "event_location": "Shanghai Port",
        "event_description": "货物已装船"
    },
    {
        "event_type": "Departed",
        "event_location": "Shanghai Port",
        "event_description": "船舶已离港"
    },
    {
        "event_type": "Arrived",
        "event_location": "Singapore Port",
        "event_description": "船舶已到达"
    }
]

for event in events:
    tracking_system.track_cargo_event(
        "CARGO20250121001",
        event["event_type"],
        event["event_location"],
        event["event_description"]
    )
    print(f"Tracked event: {event['event_type']} at {event['event_location']}")

# 获取货物追踪历史
history = tracking_system.get_cargo_tracking_history("CARGO20250121001")
print(f"\nCargo tracking history:")
for event in history:
    print(f"  {event['event_time']}: {event['event_type']} - {event['event_location']}")

# 获取当前状态
current_status = tracking_system.get_cargo_current_status("CARGO20250121001")
if current_status:
    print(f"\nCurrent cargo status:")
    print(f"  Status: {current_status['status']}")
    print(f"  Location: {current_status['current_location']}")
    print(f"  Last update: {current_status['last_update']}")

# 查询追踪统计
stats = storage.get_cargo_tracking_statistics("CARGO20250121001")
print(f"\nTracking statistics:")
for stat in stats:
    print(f"  {stat['event_type']}: {stat['count']} events")
```

---

## 4. 案例3：航线规划和性能分析

### 4.1 场景描述

**业务背景**：
航运公司需要规划船舶航线，监控航线执行情况，分析航线性能，
优化燃油消耗和航行时间。

**技术挑战**：
- 需要规划最优航线
- 需要监控实际执行情况
- 需要分析航线性能
- 需要优化燃油消耗

**解决方案**：
使用MaritimeStorage存储航线数据，实现航线规划和性能分析功能。

### 4.2 Schema定义

详见第4.2节原始定义。

### 4.3 实现代码

**完整的航线规划实现**：

```python
from maritime_storage import MaritimeStorage
from datetime import datetime, timedelta

# 初始化存储
storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")

# 创建航线
route_data = {
    "route_id": "ROUTE20250121001",
    "vessel_id": "VESSEL001",
    "voyage_number": "VOY001",
    "origin_port": "Shanghai",
    "origin_port_code": "CNSHA",
    "destination_port": "Singapore",
    "destination_port_code": "SGSIN",
    "planned_departure": datetime(2025, 1, 20, 14, 0, 0),
    "planned_arrival": datetime(2025, 1, 22, 8, 0, 0),
    "planned_distance": 1500.00,
    "planned_duration": 2,
    "actual_departure": datetime(2025, 1, 20, 14, 30, 0),
    "actual_arrival": datetime(2025, 1, 22, 9, 0, 0),
    "actual_distance": 1520.00,
    "actual_duration": 2,
    "average_speed": 18.5,
    "fuel_consumption": 120.50
}

route_id = storage.store_route(route_data)
print(f"Created route: {route_id}")

# 查询航线性能统计
performance = storage.get_route_performance_statistics("VESSEL001", days=30)
print(f"\nRoute performance statistics (30 days):")
print(f"  Voyage count: {performance['voyage_count']}")
print(f"  Avg duration: {performance['avg_duration_hours']:.2f} hours")
print(f"  Avg distance: {performance['avg_distance']:.2f} nautical miles")
print(f"  Avg speed: {performance['avg_speed']:.2f} knots")
print(f"  Avg fuel consumption: {performance['avg_fuel_consumption']:.2f} tons")
print(f"  Avg delay: {performance['avg_delay_hours']:.2f} hours")

# 查询船舶利用率
utilization = storage.get_vessel_utilization("VESSEL001", days=30)
print(f"\nVessel utilization (30 days):")
print(f"  Voyage count: {utilization['voyage_count']}")
print(f"  Days at sea: {utilization['total_days_at_sea']:.2f}")
print(f"  Cargo count: {utilization['cargo_count']}")
print(f"  Total cargo weight: {utilization['total_cargo_weight']:.2f} tons")
print(f"  Utilization rate: {utilization['utilization_rate']:.2f}%")
```

---

## 5. 案例4：EDIFACT消息处理和转换

### 5.1 场景描述

**业务背景**：
航运公司需要处理EDIFACT消息（IFTMIN、IFTMCS、IFTMAN），
与合作伙伴交换货物清单、状态更新和到达通知。

**技术挑战**：
- 需要解析EDIFACT消息
- 需要转换为XML格式
- 需要验证消息完整性
- 需要处理多种消息类型

**解决方案**：
使用EDIFACTParser和EDIFACTToXMLConverter实现EDIFACT消息处理。

### 5.2 实现代码

**完整的EDIFACT消息处理实现**：

```python
from edifact_parser import EDIFACTParser, EDIFACTToXMLConverter
from maritime_storage import MaritimeStorage

# 初始化组件
parser = EDIFACTParser()
converter = EDIFACTToXMLConverter()
storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")

# 示例EDIFACT IFTMIN消息（货物清单）
edifact_iftmin = """UNH+1+IFTMIN:D:96A:UN'
BGM+270+MSG001+9'
DTM+137:20250120:102'
TDT+20+1+13+MV OCEAN STAR::172'
LOC+5+CNSHA:172:6+Shanghai'
LOC+8+SGSIN:172:6+Singapore'
GID+1+Electronics'
MEA+WT+20000:KGM'
UNT+7+1'"""

# 解析EDIFACT消息
segments = parser.parse_message(edifact_iftmin)
print(f"Parsed {len(segments)} segments")

# 解析IFTMIN消息
cargo_manifest = parser.parse_iftmin(segments)
print(f"\nCargo Manifest:")
print(f"  Message Reference: {cargo_manifest.get('message_reference')}")
print(f"  Vessel: {cargo_manifest.get('vessel_name')}")
print(f"  Loading Port: {cargo_manifest.get('loading_port')}")
print(f"  Discharge Port: {cargo_manifest.get('discharge_port')}")
print(f"  Cargoes: {len(cargo_manifest.get('cargoes', []))}")

# 转换为XML
xml_output = converter.convert_to_xml(edifact_iftmin, "IFTMIN")
print(f"\nXML Output:")
print(xml_output[:500])  # 显示前500字符

# 存储货物信息
for cargo in cargo_manifest.get("cargoes", []):
    cargo_data = {
        "cargo_id": f"CARGO_{cargo_manifest.get('message_reference')}_{len(cargo_manifest.get('cargoes', []))}",
        "cargo_name": cargo.get("cargo_name", ""),
        "cargo_type": "General",
        "shipper": "Unknown",
        "consignee": "Unknown",
        "weight": cargo.get("weight", 0),
        "status": "Booked",
        "loading_port": cargo_manifest.get("loading_port"),
        "loading_port_code": cargo_manifest.get("loading_port_code"),
        "discharge_port": cargo_manifest.get("discharge_port"),
        "discharge_port_code": cargo_manifest.get("discharge_port_code"),
        "vessel_id": "VESSEL001"
    }
    storage.store_cargo(cargo_data)
    print(f"\nStored cargo: {cargo_data['cargo_id']}")
```

---

## 6. 案例5：海运航运数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储海运航运数据，支持船舶追踪、货物查询、
航线性能分析和船舶利用率统计。

### 6.2 实现代码

详见 `04_Transformation.md` 第7章。

### 6.3 数据分析示例

**海运航运数据分析查询**：

```python
from maritime_storage import MaritimeStorage
from datetime import datetime, timedelta

storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")

# 查询货物状态分布
status_dist = storage.get_cargo_status_distribution(days=30)
print("Cargo Status Distribution (30 days):")
for stat in status_dist:
    print(f"  {stat['status']}: {stat['count']} cargoes, "
          f"Weight: {stat['total_weight']:.2f} tons, "
          f"Value: ${stat['total_value']:,.2f}")

# 查询船舶位置统计
position_stats = storage.get_vessel_position_statistics(
    "VESSEL001",
    datetime.now() - timedelta(days=1)
)
print(f"\nVessel Position Statistics (24h):")
print(f"  Position count: {position_stats['position_count']}")
print(f"  Avg speed: {position_stats['avg_speed']:.2f} knots")
print(f"  Speed range: {position_stats['min_speed']:.2f} - {position_stats['max_speed']:.2f} knots")

# 查询航线性能
route_perf = storage.get_route_performance_statistics("VESSEL001", days=30)
print(f"\nRoute Performance (30 days):")
print(f"  Voyages: {route_perf['voyage_count']}")
print(f"  Avg duration: {route_perf['avg_duration_hours']:.2f} hours")
print(f"  Avg delay: {route_perf['avg_delay_hours']:.2f} hours")
print(f"  Avg fuel: {route_perf['avg_fuel_consumption']:.2f} tons")

# 查询船舶利用率
utilization = storage.get_vessel_utilization("VESSEL001", days=30)
print(f"\nVessel Utilization (30 days):")
print(f"  Utilization rate: {utilization['utilization_rate']:.2f}%")
print(f"  Total cargo weight: {utilization['total_cargo_weight']:.2f} tons")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
