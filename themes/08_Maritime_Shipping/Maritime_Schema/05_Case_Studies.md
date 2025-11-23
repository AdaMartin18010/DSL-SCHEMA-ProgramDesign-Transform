# 海运与航运Schema实践案例

## 📑 目录

- [海运与航运Schema实践案例](#海运与航运schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：船舶信息管理和位置追踪](#2-案例1船舶信息管理和位置追踪)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：货物全程追踪系统](#3-案例2货物全程追踪系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：航线规划和性能分析](#4-案例3航线规划和性能分析)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：EDIFACT消息处理和转换](#5-案例4edifact消息处理和转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：海运航运数据分析和报表](#6-案例5海运航运数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)
    - [6.3 数据分析示例](#63-数据分析示例)
  - [7. 案例6：船舶实时追踪（AIS集成）](#7-案例6船舶实时追踪ais集成)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：货物全程追踪（EDIFACT）](#8-案例7货物全程追踪edifact)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：航线优化（成本+时间）](#9-案例8航线优化成本时间)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 Schema定义](#92-schema定义)
    - [9.3 实现代码](#93-实现代码)
  - [10. 案例9：港口效率分析](#10-案例9港口效率分析)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 实现代码](#102-实现代码)
  - [11. 案例10：异常事件处理](#11-案例10异常事件处理)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)
  - [12. 案例11：智能航线规划系统](#12-案例11智能航线规划系统)
    - [12.1 场景描述](#121-场景描述)
    - [12.2 Schema定义](#122-schema定义)
    - [12.3 实现代码](#123-实现代码)
  - [13. 案例12：碳排放管理系统](#13-案例12碳排放管理系统)
    - [13.1 场景描述](#131-场景描述)
    - [13.2 Schema定义](#132-schema定义)
    - [13.3 实现代码](#133-实现代码)

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

## 7. 案例6：船舶实时追踪（AIS集成）

### 7.1 场景描述

**业务背景**：
航运公司需要实时追踪船舶位置，通过AIS（Automatic Identification System）系统接收船舶位置数据，实时更新船舶状态，并预测到达时间。

**技术挑战**：

- 需要解析AIS NMEA格式消息
- 需要实时处理大量AIS数据
- 需要计算船舶速度和航向
- 需要预测到达时间

**解决方案**：
使用AISMessageParser解析AIS消息，使用VesselPositionTracker实时更新船舶位置，支持多种AIS消息类型。

### 7.2 Schema定义

**AIS数据Schema**：

```json
{
  "ais_message": "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46",
  "message_type": 1,
  "message_type_name": "Position Report Class A",
  "mmsi": "563123456",
  "vessel_id": "VESSEL001",
  "position_data": {
    "latitude": 1.234567,
    "longitude": 103.456789,
    "course_over_ground": 45.5,
    "speed_over_ground": 18.5,
    "heading": 45,
    "navigation_status": 0
  },
  "timestamp": "2025-01-21T10:30:00Z"
}
```

### 7.3 实现代码

**完整的AIS实时追踪实现**：

```python
import asyncio
import logging
from vessel_position_tracker import VesselPositionTracker, AISMessageParser
from maritime_storage import MaritimeStorage

logger = logging.getLogger(__name__)

async def real_time_ais_tracking():
    """实时AIS追踪示例"""
    storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")
    tracker = VesselPositionTracker(storage)

    # 模拟AIS消息流
    ais_messages = [
        "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46",
        "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46",
        "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46"
    ]

    print("Processing AIS messages...")
    for ais_msg in ais_messages:
        try:
            # 处理AIS消息
            tracker.process_ais_message(ais_msg)
            print(f"Processed AIS message: {ais_msg[:50]}...")
        except Exception as e:
            logger.error(f"Failed to process AIS message: {e}")

    # 获取船舶当前位置
    vessel_id = "VESSEL001"
    current_pos = tracker.get_current_position(vessel_id)
    if current_pos:
        print(f"\nCurrent position for {vessel_id}:")
        print(f"  Latitude: {current_pos['latitude']}")
        print(f"  Longitude: {current_pos['longitude']}")
        print(f"  Speed: {current_pos.get('speed', 0)} knots")
        print(f"  Course: {current_pos.get('course', 0)} degrees")

    # 估算到达时间
    destination_lat = 1.300000
    destination_lon = 103.500000
    eta = tracker.estimate_arrival_time(vessel_id, destination_lat, destination_lon)
    if eta:
        print(f"\nEstimated arrival time: {eta}")

    # 获取船舶轨迹
    track = tracker.get_vessel_track(vessel_id, hours=24)
    print(f"\nVessel track (24h): {len(track)} positions")

    # 获取区域内的船舶
    vessels_in_area = tracker.get_vessels_in_area(
        min_lat=1.200000,
        max_lat=1.400000,
        min_lon=103.400000,
        max_lon=103.600000
    )
    print(f"\nVessels in area: {len(vessels_in_area)}")
    for vessel in vessels_in_area:
        print(f"  {vessel['vessel_name']}: {vessel['latitude']}, {vessel['longitude']}")

    storage.close()

if __name__ == "__main__":
    asyncio.run(real_time_ais_tracking())
```

---

## 8. 案例7：货物全程追踪（EDIFACT）

### 8.1 场景描述

**业务背景**：
航运公司需要全程追踪货物状态，通过EDIFACT消息（IFTMIN、IFTMCS、IFTMAN）与合作伙伴交换货物信息，实现货物从预订到交付的全程追踪。

**技术挑战**：

- 需要解析多种EDIFACT消息类型
- 需要验证消息完整性
- 需要关联不同消息中的货物信息
- 需要生成货物追踪报告

**解决方案**：
使用EDIFACTParser解析EDIFACT消息，使用CargoTrackingSystem追踪货物状态，实现货物全程追踪。

### 8.2 Schema定义

**货物全程追踪Schema**：

```json
{
  "cargo_id": "CARGO20250121001",
  "tracking_events": [
    {
      "event_type": "Booked",
      "event_time": "2025-01-15T10:00:00Z",
      "event_location": "Shanghai",
      "source_message": "IFTMIN",
      "message_reference": "MSG001"
    },
    {
      "event_type": "Loaded",
      "event_time": "2025-01-18T14:00:00Z",
      "event_location": "Shanghai Port",
      "source_message": "IFTMCS",
      "message_reference": "MSG002"
    },
    {
      "event_type": "Arrived",
      "event_time": "2025-01-22T08:00:00Z",
      "event_location": "Singapore Port",
      "source_message": "IFTMAN",
      "message_reference": "MSG003"
    }
  ]
}
```

### 8.3 实现代码

**完整的货物全程追踪实现**：

```python
from edifact_parser import EDIFACTParser
from cargo_tracking_system import CargoTrackingSystem
from maritime_storage import MaritimeStorage

def cargo_full_tracking():
    """货物全程追踪示例"""
    storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")
    parser = EDIFACTParser()
    tracking_system = CargoTrackingSystem(storage)

    # 1. 接收IFTMIN消息（货物清单）
    iftmin_message = """UNH+1+IFTMIN:D:96A:UN'
BGM+270+MSG001+9'
DTM+137:20250115:102'
TDT+20+1+13+MV OCEAN STAR::172'
LOC+5+CNSHA:172:6+Shanghai'
LOC+8+SGSIN:172:6+Singapore'
GID+1+Electronics'
MEA+WT+20000:KGM'
UNT+8+1'"""

    segments = parser.parse_message(iftmin_message)
    cargo_manifest = parser.parse_iftmin(segments)

    cargo_id = "CARGO20250121001"

    # 记录预订事件
    tracking_system.track_cargo_event(
        cargo_id,
        "Booked",
        cargo_manifest.get("loading_port", "Unknown"),
        f"From EDIFACT message: {cargo_manifest.get('message_reference')}"
    )

    # 2. 接收IFTMCS消息（货物状态更新）
    iftmcs_message = """UNH+1+IFTMCS:D:96A:UN'
BGM+270+MSG002+9'
RFF+BM:CARGO20250121001'
DTM+137:20250118:102'
LOC+11+Shanghai Port'
STS+1+Loaded'
UNT+5+1'"""

    segments = parser.parse_message(iftmcs_message)
    cargo_status = parser.parse_iftmcs(segments)

    # 记录状态更新
    for update in cargo_status.get("status_updates", []):
        tracking_system.track_cargo_event(
            update.get("cargo_id", cargo_id),
            update.get("status", "Unknown"),
            update.get("event_location", "Unknown"),
            f"From EDIFACT message: {cargo_status.get('message_reference')}"
        )

    # 3. 接收IFTMAN消息（到达通知）
    iftman_message = """UNH+1+IFTMAN:D:96A:UN'
BGM+270+MSG003+9'
TDT+20+1+13+MV OCEAN STAR::172'
LOC+8+SGSIN:172:6+Singapore'
DTM+132:20250122:102'
DTM+133:20250122:102'
UNT+6+1'"""

    segments = parser.parse_message(iftman_message)
    arrival_notice = parser.parse_iftman(segments)

    # 记录到达事件
    arrival_info = arrival_notice.get("arrival_info", {})
    tracking_system.track_cargo_event(
        cargo_id,
        "Arrived",
        arrival_info.get("port_name", "Unknown"),
        f"From EDIFACT message: {arrival_notice.get('message_reference')}"
    )

    # 获取货物追踪历史
    history = tracking_system.get_cargo_tracking_history(cargo_id)
    print(f"\nCargo Tracking History for {cargo_id}:")
    for event in history:
        print(f"  {event['event_time']}: {event['event_type']} at {event['event_location']}")

    # 获取当前状态
    current_status = tracking_system.get_cargo_current_status(cargo_id)
    if current_status:
        print(f"\nCurrent Status:")
        print(f"  Status: {current_status['status']}")
        print(f"  Location: {current_status['current_location']}")
        print(f"  Last Update: {current_status['last_update']}")

    storage.close()

if __name__ == "__main__":
    cargo_full_tracking()
```

---

## 9. 案例8：航线优化（成本+时间）

### 9.1 场景描述

**业务背景**：
航运公司需要在成本和时间之间找到平衡，优化航线规划。需要考虑燃油成本、港口成本、航行时间、天气因素等多个因素。

**技术挑战**：

- 需要计算最短路径
- 需要优化燃油成本
- 需要优化航行时间
- 需要考虑天气因素
- 需要多目标优化

**解决方案**：
使用RouteOptimizer实现航线优化，支持最短路径、成本优化、时间优化和多目标优化。

### 9.2 Schema定义

**航线优化Schema**：

```json
{
  "optimization_id": "OPT001",
  "route_id": "ROUTE20250121001",
  "optimization_type": "multi_objective",
  "origin": {
    "latitude": 31.230416,
    "longitude": 121.473701,
    "port_code": "CNSHA",
    "port_name": "Shanghai"
  },
  "destination": {
    "latitude": 1.289670,
    "longitude": 103.850070,
    "port_code": "SGSIN",
    "port_name": "Singapore"
  },
  "optimization_parameters": {
    "weights": {
      "cost": 0.6,
      "time": 0.4
    },
    "fuel_price_per_ton": 500.0,
    "max_speed": 20.0,
    "weather_data": {
      "wind_speed": 15,
      "wind_direction": 90
    }
  },
  "optimization_result": {
    "total_distance": 1500.0,
    "estimated_hours": 75.0,
    "fuel_consumption": 75.0,
    "total_cost": 37500.0,
    "recommended_speed": 18.5
  }
}
```

### 9.3 实现代码

**完整的航线优化实现**：

```python
from route_optimizer import RouteOptimizer
from vessel_position_tracker import VesselPositionTracker
from maritime_storage import MaritimeStorage

def route_optimization_example():
    """航线优化示例"""
    storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")
    tracker = VesselPositionTracker(storage)
    optimizer = RouteOptimizer(storage, tracker)

    vessel_id = "VESSEL001"
    origin_lat, origin_lon = 31.230416, 121.473701  # Shanghai
    dest_lat, dest_lon = 1.289670, 103.850070  # Singapore

    # 1. 最短路径优化
    print("1. Shortest Path Optimization:")
    shortest_result = optimizer.optimize_route_shortest_path(
        origin_lat, origin_lon, dest_lat, dest_lon
    )
    print(f"  Total distance: {shortest_result['total_distance']:.2f} nautical miles")
    print(f"  Route segments: {len(shortest_result['route_segments'])}")

    # 2. 成本优化
    print("\n2. Cost Optimization:")
    cost_result = optimizer.optimize_route_cost(
        origin_lat, origin_lon, dest_lat, dest_lon,
        vessel_id,
        fuel_price_per_ton=500.0,
        port_costs={"loading": 5000, "discharge": 5000}
    )
    print(f"  Total distance: {cost_result['total_distance']:.2f} nautical miles")
    print(f"  Fuel consumption: {cost_result['fuel_consumption']:.2f} tons")
    print(f"  Fuel cost: ${cost_result['fuel_cost']:,.2f}")
    print(f"  Port cost: ${cost_result['port_cost']:,.2f}")
    print(f"  Total cost: ${cost_result['total_cost']:,.2f}")
    print(f"  Estimated hours: {cost_result['estimated_hours']:.2f}")

    # 3. 时间优化
    print("\n3. Time Optimization:")
    time_result = optimizer.optimize_route_time(
        origin_lat, origin_lon, dest_lat, dest_lon,
        vessel_id,
        max_speed=20.0,
        weather_data={"wind_speed": 15, "wind_direction": 90}
    )
    print(f"  Total distance: {time_result['total_distance']:.2f} nautical miles")
    print(f"  Max speed: {time_result['max_speed']:.2f} knots")
    print(f"  Effective speed: {time_result['effective_speed']:.2f} knots")
    print(f"  Estimated hours: {time_result['estimated_hours']:.2f}")
    print(f"  Weather impact: {time_result['weather_impact']}")

    # 4. 多目标优化
    print("\n4. Multi-Objective Optimization:")
    multi_result = optimizer.optimize_route_multi_objective(
        origin_lat, origin_lon, dest_lat, dest_lon,
        vessel_id,
        weights={"cost": 0.6, "time": 0.4}
    )
    print(f"  Combined score: {multi_result['combined_score']:.4f}")
    print(f"  Recommended speed: {multi_result['recommended_speed']:.2f} knots")
    print(f"  Estimated cost: ${multi_result['estimated_cost']:,.2f}")
    print(f"  Estimated hours: {multi_result['estimated_hours']:.2f}")

    # 5. 寻找最优中间港口
    print("\n5. Optimal Waypoints:")
    available_ports = [
        {"port_code": "CNXMN", "port_name": "Xiamen", "latitude": 24.479834, "longitude": 118.081871},
        {"port_code": "CNFOC", "port_name": "Fuzhou", "latitude": 26.074508, "longitude": 119.296494},
        {"port_code": "MYTPP", "port_name": "Port Klang", "latitude": 3.000000, "longitude": 101.400000}
    ]

    optimal_waypoints = optimizer.find_optimal_waypoints(
        origin_lat, origin_lon, dest_lat, dest_lon, available_ports
    )
    print(f"  Optimal waypoints: {len(optimal_waypoints)}")
    for wp in optimal_waypoints:
        print(f"    {wp['port_name']} ({wp['port_code']})")

    # 存储优化结果
    optimization_data = {
        "optimization_id": "OPT001",
        "route_id": "ROUTE20250121001",
        "optimization_type": "multi_objective",
        "origin_latitude": origin_lat,
        "origin_longitude": origin_lon,
        "destination_latitude": dest_lat,
        "destination_longitude": dest_lon,
        "total_distance": multi_result["total_distance"],
        "estimated_hours": multi_result["estimated_hours"],
        "fuel_consumption": multi_result["cost_optimization"]["fuel_consumption"],
        "fuel_cost": multi_result["estimated_cost"],
        "total_cost": multi_result["estimated_cost"],
        "recommended_speed": multi_result["recommended_speed"],
        "waypoints": optimal_waypoints,
        "optimization_parameters": {"weights": {"cost": 0.6, "time": 0.4}}
    }

    storage.store_route_optimization(optimization_data)
    print(f"\nStored optimization result: OPT001")

    storage.close()

if __name__ == "__main__":
    route_optimization_example()
```

---

## 10. 案例9：港口效率分析

### 10.1 场景描述

**业务背景**：
航运公司需要分析港口效率，了解各港口的平均停靠时间、货物处理速度、等待时间等指标，以便选择最优港口和优化港口操作。

**技术挑战**：

- 需要收集港口操作数据
- 需要计算港口效率指标
- 需要比较不同港口的效率
- 需要识别效率瓶颈

**解决方案**：
使用港口效率表和港口操作记录表存储数据，实现港口效率分析和比较。

### 10.2 实现代码

**完整的港口效率分析实现**：

```python
from maritime_storage import MaritimeStorage
from datetime import datetime, timedelta

def port_efficiency_analysis():
    """港口效率分析示例"""
    storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")

    # 记录港口操作
    operations = [
        {
            "operation_id": "OP001",
            "port_code": "CNSHA",
            "vessel_id": "VESSEL001",
            "operation_type": "Loading",
            "operation_start": datetime(2025, 1, 18, 8, 0, 0),
            "operation_end": datetime(2025, 1, 18, 20, 0, 0),
            "duration_hours": 12.0,
            "cargo_tonnage": 20000.0,
            "berth_number": "Berth 5",
            "crane_count": 3,
            "efficiency_rating": 0.85
        },
        {
            "operation_id": "OP002",
            "port_code": "SGSIN",
            "vessel_id": "VESSEL001",
            "operation_type": "Discharge",
            "operation_start": datetime(2025, 1, 22, 8, 0, 0),
            "operation_end": datetime(2025, 1, 22, 18, 0, 0),
            "duration_hours": 10.0,
            "cargo_tonnage": 20000.0,
            "berth_number": "Berth 12",
            "crane_count": 4,
            "efficiency_rating": 0.90
        }
    ]

    for op in operations:
        storage.store_port_operation(op)
        print(f"Stored operation: {op['operation_id']} at {op['port_code']}")

    # 更新港口效率数据
    port_efficiency_data = {
        "port_code": "CNSHA",
        "port_name": "Shanghai",
        "country_code": "CN",
        "latitude": 31.230416,
        "longitude": 121.473701,
        "average_berth_time_hours": 12.5,
        "average_cargo_handling_rate": 1666.67,  # 吨/小时
        "average_waiting_time_hours": 2.0,
        "total_vessels": 100,
        "total_cargo_tonnage": 2000000.0,
        "efficiency_score": 0.85
    }
    storage.store_port_efficiency(port_efficiency_data)

    port_efficiency_data_sg = {
        "port_code": "SGSIN",
        "port_name": "Singapore",
        "country_code": "SG",
        "latitude": 1.289670,
        "longitude": 103.850070,
        "average_berth_time_hours": 10.0,
        "average_cargo_handling_rate": 2000.0,  # 吨/小时
        "average_waiting_time_hours": 1.5,
        "total_vessels": 150,
        "total_cargo_tonnage": 3000000.0,
        "efficiency_score": 0.90
    }
    storage.store_port_efficiency(port_efficiency_data_sg)

    # 获取港口效率统计
    print("\nPort Efficiency Statistics:")
    efficiency_stats = storage.get_port_efficiency_statistics()
    for stat in efficiency_stats:
        print(f"\n{stat['port_name']} ({stat['port_code']}):")
        print(f"  Average berth time: {stat['average_berth_time_hours']:.2f} hours")
        print(f"  Cargo handling rate: {stat['average_cargo_handling_rate']:.2f} tons/hour")
        print(f"  Average waiting time: {stat['average_waiting_time_hours']:.2f} hours")
        print(f"  Efficiency score: {stat['efficiency_score']:.2f}")
        print(f"  Total vessels: {stat['total_vessels']}")
        print(f"  Total cargo: {stat['total_cargo_tonnage']:,.2f} tons")

    # 比较港口效率
    print("\nPort Efficiency Comparison:")
    if len(efficiency_stats) >= 2:
        port1 = efficiency_stats[0]
        port2 = efficiency_stats[1]

        print(f"\n{port1['port_name']} vs {port2['port_name']}:")
        print(f"  Berth time difference: {abs(port1['average_berth_time_hours'] - port2['average_berth_time_hours']):.2f} hours")
        print(f"  Handling rate difference: {abs(port1['average_cargo_handling_rate'] - port2['average_cargo_handling_rate']):.2f} tons/hour")
        print(f"  Efficiency score difference: {abs(port1['efficiency_score'] - port2['efficiency_score']):.2f}")

        if port1['efficiency_score'] > port2['efficiency_score']:
            print(f"  {port1['port_name']} is more efficient")
        else:
            print(f"  {port2['port_name']} is more efficient")

    storage.close()

if __name__ == "__main__":
    port_efficiency_analysis()
```

---

## 11. 案例10：异常事件处理

### 11.1 场景描述

**业务背景**：
航运公司需要监控和处理异常事件，如船舶故障、货物损坏、航线延误、天气异常等。需要及时记录、分析和处理这些事件。

**技术挑战**：

- 需要实时监控异常事件
- 需要分类和分级事件
- 需要记录事件处理过程
- 需要生成事件报告

**解决方案**：
使用异常事件表存储事件数据，实现事件分类、分级、追踪和处理功能。

### 11.2 Schema定义

**异常事件Schema**：

```json
{
  "event_id": "EVT001",
  "event_type": "VesselBreakdown",
  "event_severity": "High",
  "vessel_id": "VESSEL001",
  "route_id": "ROUTE20250121001",
  "cargo_id": "CARGO20250121001",
  "event_location": {
    "latitude": 1.250000,
    "longitude": 103.500000
  },
  "event_description": "Engine failure, vessel stopped",
  "event_time": "2025-01-21T14:30:00Z",
  "resolved_time": "2025-01-21T18:00:00Z",
  "resolution_description": "Engine repaired, vessel resumed voyage"
}
```

### 11.3 实现代码

**完整的异常事件处理实现**：

```python
from maritime_storage import MaritimeStorage
from datetime import datetime

def maritime_event_handling():
    """异常事件处理示例"""
    storage = MaritimeStorage("postgresql://user:pass@localhost/maritime")

    # 记录异常事件
    events = [
        {
            "event_id": "EVT001",
            "event_type": "VesselBreakdown",
            "event_severity": "High",
            "vessel_id": "VESSEL001",
            "route_id": "ROUTE20250121001",
            "cargo_id": None,
            "event_location_latitude": 1.250000,
            "event_location_longitude": 103.500000,
            "event_description": "Engine failure, vessel stopped",
            "event_time": datetime(2025, 1, 21, 14, 30, 0),
            "resolved_time": datetime(2025, 1, 21, 18, 0, 0),
            "resolution_description": "Engine repaired, vessel resumed voyage"
        },
        {
            "event_id": "EVT002",
            "event_type": "CargoDamage",
            "event_severity": "Medium",
            "vessel_id": "VESSEL001",
            "route_id": "ROUTE20250121001",
            "cargo_id": "CARGO20250121001",
            "event_location_latitude": None,
            "event_location_longitude": None,
            "event_description": "Container damaged during loading",
            "event_time": datetime(2025, 1, 18, 10, 0, 0),
            "resolved_time": datetime(2025, 1, 18, 12, 0, 0),
            "resolution_description": "Container replaced, cargo reloaded"
        },
        {
            "event_id": "EVT003",
            "event_type": "WeatherDelay",
            "event_severity": "Low",
            "vessel_id": "VESSEL001",
            "route_id": "ROUTE20250121001",
            "cargo_id": None,
            "event_location_latitude": 1.300000,
            "event_location_longitude": 103.600000,
            "event_description": "Heavy weather, vessel slowed down",
            "event_time": datetime(2025, 1, 21, 8, 0, 0),
            "resolved_time": datetime(2025, 1, 21, 12, 0, 0),
            "resolution_description": "Weather cleared, normal speed resumed"
        }
    ]

    for event in events:
        storage.store_maritime_event(event)
        print(f"Stored event: {event['event_id']} - {event['event_type']}")

    # 查询事件
    print("\nAll Events:")
    all_events = storage.get_maritime_events(limit=10)
    for event in all_events:
        print(f"  {event['event_id']}: {event['event_type']} ({event['event_severity']}) at {event['event_time']}")

    # 查询特定船舶的事件
    print("\nEvents for VESSEL001:")
    vessel_events = storage.get_maritime_events(vessel_id="VESSEL001")
    for event in vessel_events:
        print(f"  {event['event_type']}: {event['event_description']}")
        if event['resolved_time']:
            duration = (event['resolved_time'] - event['event_time']).total_seconds() / 3600
            print(f"    Resolved in {duration:.2f} hours")

    # 查询高严重性事件
    print("\nHigh Severity Events:")
    high_severity_events = storage.get_maritime_events(severity="High")
    for event in high_severity_events:
        print(f"  {event['event_id']}: {event['event_type']} - {event['event_description']}")

    # 查询未解决的事件
    print("\nUnresolved Events:")
    unresolved_events = [
        e for e in all_events if e['resolved_time'] is None
    ]
    for event in unresolved_events:
        print(f"  {event['event_id']}: {event['event_type']} - {event['event_description']}")

    # 事件统计
    print("\nEvent Statistics:")
    event_types = {}
    for event in all_events:
        event_type = event['event_type']
        event_types[event_type] = event_types.get(event_type, 0) + 1

    for event_type, count in event_types.items():
        print(f"  {event_type}: {count} events")

    storage.close()

if __name__ == "__main__":
    maritime_event_handling()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

---

## 12. 案例11：智能航线规划系统

### 12.1 场景描述

**业务背景**：
智能航线规划系统基于天气、海况、港口情况等数据，
优化船舶航线，减少航行时间、降低燃料消耗、提高安全性。

**技术挑战**：
- 需要多源数据整合
- 需要航线优化算法
- 需要实时更新
- 需要效果评估

**解决方案**：
使用Maritime_Schema整合航线数据，
使用优化算法进行航线规划，
使用MaritimeStorage存储航线数据。

### 12.2 Schema定义

**智能航线规划Schema**：

```dsl
schema IntelligentRoutePlanning {
  planning_session_id: String @value("ROUTE-PLAN-20250121-001") @required
  vessel_id: String @value("VESSEL-001") @required
  planning_time: DateTime @value("2025-01-21T10:00:00") @required

  route_requirements: {
    origin_port: String @value("Shanghai")
    destination_port: String @value("Singapore")
    cargo_type: String @value("Container")
    cargo_weight: Decimal @value(50000.0) @unit("tons")
    deadline: DateTime @value("2025-01-28T00:00:00")
  } @required

  route_options: [
    {
      route_id: String @value("ROUTE-001")
      waypoints: [
        {
          latitude: Decimal @value(31.2304)
          longitude: Decimal @value(121.4737)
          port_name: String @value("Shanghai")
        },
        {
          latitude: Decimal @value(1.2897)
          longitude: Decimal @value(103.8501)
          port_name: String @value("Singapore")
        }
      ]
      estimated_distance: Decimal @value(2500.0) @unit("nautical miles")
      estimated_duration: Decimal @value(120.0) @unit("hours")
      estimated_fuel_consumption: Decimal @value(500.0) @unit("tons")
      estimated_cost: Decimal @value(50000.0) @unit("USD")
      weather_risk: Enum { Low } @value(Low)
      safety_score: Decimal @value(0.90) @range(0.0, 1.0)
    }
  ] @required

  selected_route: {
    route_id: String @value("ROUTE-001")
    selection_reason: String @value("最优成本和时间平衡")
    optimization_score: Decimal @value(0.88) @range(0.0, 1.0)
  } @required
} @standard("EDIFACT")
```

### 12.3 实现代码

```python
from maritime_storage import MaritimeStorage
from datetime import datetime

def intelligent_route_planning():
    """智能航线规划系统示例"""
    storage = MaritimeStorage("postgresql://user:password@localhost/maritime_db")

    # 航线需求
    route_requirements = {
        "vessel_id": "VESSEL-001",
        "origin_port": "Shanghai",
        "destination_port": "Singapore",
        "cargo_type": "Container",
        "cargo_weight": 50000.0,
        "deadline": datetime(2025, 1, 28, 0, 0, 0)
    }

    # 航线优化算法
    def optimize_route(requirements):
        """优化航线"""
        route_options = []

        # 生成多个航线选项（简化示例）
        route1 = {
            "route_id": "ROUTE-001",
            "waypoints": [
                {"latitude": 31.2304, "longitude": 121.4737, "port_name": "Shanghai"},
                {"latitude": 1.2897, "longitude": 103.8501, "port_name": "Singapore"}
            ],
            "estimated_distance": 2500.0,
            "estimated_duration": 120.0,
            "estimated_fuel_consumption": 500.0,
            "estimated_cost": 50000.0,
            "weather_risk": "Low",
            "safety_score": 0.90
        }

        route2 = {
            "route_id": "ROUTE-002",
            "waypoints": [
                {"latitude": 31.2304, "longitude": 121.4737, "port_name": "Shanghai"},
                {"latitude": 22.3193, "longitude": 114.1694, "port_name": "Hong Kong"},
                {"latitude": 1.2897, "longitude": 103.8501, "port_name": "Singapore"}
            ],
            "estimated_distance": 2600.0,
            "estimated_duration": 130.0,
            "estimated_fuel_consumption": 520.0,
            "estimated_cost": 52000.0,
            "weather_risk": "Low",
            "safety_score": 0.92
        }

        route_options = [route1, route2]

        # 选择最优航线（综合考虑成本、时间、安全性）
        best_route = None
        best_score = 0.0

        for route in route_options:
            # 计算优化分数
            cost_score = 1.0 / (route["estimated_cost"] / 10000.0)
            time_score = 1.0 / (route["estimated_duration"] / 100.0)
            safety_score = route["safety_score"]

            optimization_score = (
                cost_score * 0.4 +
                time_score * 0.3 +
                safety_score * 0.3
            )

            if optimization_score > best_score:
                best_score = optimization_score
                best_route = route

        return {
            "route_options": route_options,
            "selected_route": best_route,
            "optimization_score": best_score,
            "selection_reason": "最优成本和时间平衡"
        }

    # 执行航线规划
    route_planning = optimize_route(route_requirements)

    # 存储航线规划数据
    planning_data = {
        "planning_session_id": "ROUTE-PLAN-20250121-001",
        "vessel_id": route_requirements["vessel_id"],
        "planning_time": datetime.now(),
        "origin_port": route_requirements["origin_port"],
        "destination_port": route_requirements["destination_port"],
        "cargo_type": route_requirements["cargo_type"],
        "cargo_weight": route_requirements["cargo_weight"],
        "deadline": route_requirements["deadline"],
        "selected_route_id": route_planning["selected_route"]["route_id"],
        "selected_route_distance": route_planning["selected_route"]["estimated_distance"],
        "selected_route_duration": route_planning["selected_route"]["estimated_duration"],
        "selected_route_fuel": route_planning["selected_route"]["estimated_fuel_consumption"],
        "selected_route_cost": route_planning["selected_route"]["estimated_cost"],
        "optimization_score": route_planning["optimization_score"],
        "selection_reason": route_planning["selection_reason"]
    }

    # 存储到数据库
    planning_id = storage.store_vessel(planning_data)
    print(f"Route planning stored: {planning_id}")

    print(f"\nIntelligent Route Planning Results:")
    print(f"  Vessel: {route_requirements['vessel_id']}")
    print(f"  Route: {route_requirements['origin_port']} -> {route_requirements['destination_port']}")
    print(f"  Selected route: {route_planning['selected_route']['route_id']}")
    print(f"  Distance: {route_planning['selected_route']['estimated_distance']:.1f} nm")
    print(f"  Duration: {route_planning['selected_route']['estimated_duration']:.1f} hours")
    print(f"  Fuel consumption: {route_planning['selected_route']['estimated_fuel_consumption']:.1f} tons")
    print(f"  Cost: ${route_planning['selected_route']['estimated_cost']:.2f}")
    print(f"  Optimization score: {route_planning['optimization_score']:.2f}")

    return planning_data

if __name__ == "__main__":
    intelligent_route_planning()
```

---

## 13. 案例12：碳排放管理系统

### 13.1 场景描述

**业务背景**：
碳排放管理系统监测和管理船舶碳排放，
支持碳排放报告、碳减排优化、碳交易等功能。

**技术挑战**：
- 需要碳排放数据收集
- 需要碳排放计算
- 需要减排策略
- 需要碳交易支持

**解决方案**：
使用Maritime_Schema整合碳排放数据，
使用碳排放模型进行计算，
使用MaritimeStorage存储碳排放数据。

### 13.2 Schema定义

**碳排放管理Schema**：

```dsl
schema CarbonEmissionManagement {
  emission_session_id: String @value("CARBON-20250121-001") @required
  vessel_id: String @value("VESSEL-001") @required
  reporting_period: {
    start_date: Date @value("2025-01-01")
    end_date: Date @value("2025-01-21")
  } @required

  emission_data: {
    total_fuel_consumption: Decimal @value(5000.0) @unit("tons")
    fuel_type: Enum { HFO } @value(HFO)
    emission_factor: Decimal @value(3.114) @unit("tons CO2/ton fuel")
    total_co2_emissions: Decimal @value(15570.0) @unit("tons CO2")
    distance_traveled: Decimal @value(10000.0) @unit("nautical miles")
    cargo_carried: Decimal @value(50000.0) @unit("tons")
    emission_intensity: Decimal @value(0.311) @unit("tons CO2/ton cargo")
  } @required

  emission_reduction: {
    reduction_target: Decimal @value(0.10) @unit("10% reduction")
    current_reduction: Decimal @value(0.05) @unit("5% reduction")
    reduction_measures: [
      {
        measure: String @value("优化航线")
        reduction_potential: Decimal @value(0.03)
        implementation_status: Enum { Implemented } @value(Implemented)
      },
      {
        measure: String @value("使用低硫燃料")
        reduction_potential: Decimal @value(0.02)
        implementation_status: Enum { Planned } @value(Planned)
      }
    ]
  } @required

  carbon_trading: {
    carbon_credits_required: Decimal @value(1557.0) @unit("tons CO2")
    carbon_price: Decimal @value(50.0) @unit("USD/ton CO2")
    total_cost: Decimal @value(77850.0) @unit("USD")
  } @required
} @standard("EDIFACT")
```

### 13.3 实现代码

```python
from maritime_storage import MaritimeStorage
from datetime import datetime, date

def carbon_emission_management():
    """碳排放管理系统示例"""
    storage = MaritimeStorage("postgresql://user:password@localhost/maritime_db")

    # 碳排放数据
    emission_data = {
        "vessel_id": "VESSEL-001",
        "reporting_start_date": date(2025, 1, 1),
        "reporting_end_date": date(2025, 1, 21),
        "total_fuel_consumption": 5000.0,
        "fuel_type": "HFO",
        "emission_factor": 3.114,  # tons CO2 per ton fuel
        "distance_traveled": 10000.0,
        "cargo_carried": 50000.0
    }

    # 计算碳排放
    total_co2_emissions = emission_data["total_fuel_consumption"] * emission_data["emission_factor"]
    emission_intensity = total_co2_emissions / emission_data["cargo_carried"]

    # 减排措施
    reduction_measures = [
        {
            "measure": "优化航线",
            "reduction_potential": 0.03,
            "implementation_status": "Implemented"
        },
        {
            "measure": "使用低硫燃料",
            "reduction_potential": 0.02,
            "implementation_status": "Planned"
        }
    ]

    # 计算当前减排
    implemented_reductions = sum(
        m["reduction_potential"] for m in reduction_measures
        if m["implementation_status"] == "Implemented"
    )

    reduction_target = 0.10
    current_reduction = implemented_reductions

    # 碳交易计算
    carbon_credits_required = total_co2_emissions * (1 - current_reduction)
    carbon_price = 50.0  # USD per ton CO2
    total_cost = carbon_credits_required * carbon_price

    # 存储碳排放数据
    carbon_data = {
        "emission_session_id": "CARBON-20250121-001",
        "vessel_id": emission_data["vessel_id"],
        "reporting_start_date": emission_data["reporting_start_date"],
        "reporting_end_date": emission_data["reporting_end_date"],
        "total_fuel_consumption": emission_data["total_fuel_consumption"],
        "fuel_type": emission_data["fuel_type"],
        "emission_factor": emission_data["emission_factor"],
        "total_co2_emissions": total_co2_emissions,
        "distance_traveled": emission_data["distance_traveled"],
        "cargo_carried": emission_data["cargo_carried"],
        "emission_intensity": emission_intensity,
        "reduction_target": reduction_target,
        "current_reduction": current_reduction,
        "reduction_measures": reduction_measures,
        "carbon_credits_required": carbon_credits_required,
        "carbon_price": carbon_price,
        "total_cost": total_cost
    }

    # 存储到数据库
    carbon_id = storage.store_vessel(carbon_data)
    print(f"Carbon emission data stored: {carbon_id}")

    print(f"\nCarbon Emission Management:")
    print(f"  Vessel: {emission_data['vessel_id']}")
    print(f"  Total CO2 emissions: {total_co2_emissions:.1f} tons")
    print(f"  Emission intensity: {emission_intensity:.3f} tons CO2/ton cargo")
    print(f"  Reduction target: {reduction_target*100:.1f}%")
    print(f"  Current reduction: {current_reduction*100:.1f}%")
    print(f"  Carbon credits required: {carbon_credits_required:.1f} tons CO2")
    print(f"  Total cost: ${total_cost:.2f}")

    return carbon_data

if __name__ == "__main__":
    carbon_emission_management()
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
