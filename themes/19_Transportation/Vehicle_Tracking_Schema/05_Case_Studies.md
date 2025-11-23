# 车辆跟踪Schema实践案例

## 📑 目录

- [车辆跟踪Schema实践案例](#车辆跟踪schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：GPS车辆位置跟踪](#2-案例1gps车辆位置跟踪)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：NMEA消息解析](#3-案例2nmea消息解析)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：轨迹分析和回放](#4-案例3轨迹分析和回放)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：地理围栏监控](#5-案例4地理围栏监控)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 Schema定义](#52-schema定义)
    - [5.3 实现代码](#53-实现代码)
  - [6. 案例5：AIS船舶跟踪](#6-案例5ais船舶跟踪)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 Schema定义](#62-schema定义)
    - [6.3 实现代码](#63-实现代码)
  - [7. 案例6：北斗定位跟踪](#7-案例6北斗定位跟踪)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：车辆跟踪数据存储和查询](#8-案例7车辆跟踪数据存储和查询)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 实现代码](#82-实现代码)

---

## 1. 案例概述

本文档提供车辆跟踪Schema在实际应用中的实践案例，涵盖GPS定位、NMEA消息解析、轨迹分析、地理围栏监控、AIS船舶跟踪、北斗定位等场景。

---

## 2. 案例1：GPS车辆位置跟踪

### 2.1 场景描述

**业务背景**：
物流公司需要实时跟踪车辆位置，监控车辆行驶状态，优化运输路线，提高运输效率。

**技术挑战**：

- 需要实时接收和处理GPS位置数据
- 需要验证GPS数据质量
- 需要存储大量位置数据
- 需要支持位置查询和轨迹回放

**解决方案**：
使用Vehicle_Tracking_Schema定义GPS位置数据结构，实现GPS位置跟踪、数据存储和查询功能。

### 2.2 Schema定义

**GPS车辆位置跟踪Schema**：

```json
{
  "vehicle_id": "VEH001",
  "vehicle_type": "Truck",
  "gps_positions": [
    {
      "timestamp": "2025-01-21T10:00:00Z",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "altitude": 10.5,
      "speed": 60.0,
      "course": 45.0,
      "fix_quality": 1,
      "num_satellites": 8,
      "hdop": 1.2,
      "source": "GPS"
    },
    {
      "timestamp": "2025-01-21T10:01:00Z",
      "latitude": 31.2310,
      "longitude": 121.4745,
      "altitude": 10.8,
      "speed": 62.0,
      "course": 46.0,
      "fix_quality": 1,
      "num_satellites": 9,
      "hdop": 1.1,
      "source": "GPS"
    }
  ]
}
```

### 2.3 实现代码

**完整的GPS车辆位置跟踪实现**：

```python
import logging
from typing import Dict, List
from datetime import datetime
from vehicle_tracking_schema.transformation import NMEAParser, GPSPositionTracker, VehicleTrackingStorage

logger = logging.getLogger(__name__)

# 案例1：GPS车辆位置跟踪
def case1_gps_vehicle_tracking():
    """案例1：GPS车辆位置跟踪"""

    # 1. 初始化GPS位置跟踪器
    vehicle_id = "VEH001"
    tracker = GPSPositionTracker(vehicle_id)

    # 2. 模拟接收NMEA消息
    nmea_messages = [
        "$GPGGA,100000.00,3113.8240,N,12128.4220,E,1,08,1.2,10.5,M,46.9,M,,*47",
        "$GPRMC,100100.00,A,3113.8300,N,12128.4270,E,032.4,045.0,210125,,,A*6A",
        "$GPGGA,100200.00,3113.8360,N,12128.4320,E,1,09,1.1,10.8,M,46.9,M,,*48"
    ]

    # 3. 解析NMEA消息并更新位置
    nmea_parser = NMEAParser()
    for nmea_msg in nmea_messages:
        try:
            parsed = nmea_parser.parse_nmea_message(nmea_msg)
            if parsed:
                tracker.update_position(nmea_msg)
                logger.info(f"Updated GPS position: {parsed.get('latitude')}, {parsed.get('longitude')}")
        except Exception as e:
            logger.error(f"Failed to parse NMEA message: {e}")

    # 4. 获取当前位置
    current_position = tracker.get_current_position()
    logger.info(f"Current position: {current_position}")

    # 5. 获取位置历史
    position_history = tracker.get_position_history(limit=100)
    logger.info(f"Position history: {len(position_history)} points")

    # 6. 存储位置数据
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "tracking_db",
        "user": "tracking_user",
        "password": "tracking_password"
    }
    storage = VehicleTrackingStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 存储位置数据
    for position in position_history:
        position_id = storage.store_position(position)
        logger.info(f"Stored position with ID: {position_id}")

    return {
        "vehicle_id": vehicle_id,
        "current_position": current_position,
        "position_count": len(position_history)
    }

# 运行案例1
if __name__ == "__main__":
    case1_gps_vehicle_tracking()
```

**预期结果**：

```text
Updated GPS position: 31.2304, 121.4737
Updated GPS position: 31.2310, 121.4745
Updated GPS position: 31.2316, 121.4752
Current position: {'vehicle_id': 'VEH001', 'latitude': 31.2316, 'longitude': 121.4752, ...}
Position history: 3 points
Stored position with ID: 1
Stored position with ID: 2
Stored position with ID: 3
```

---

## 3. 案例2：NMEA消息解析

### 3.1 场景描述

**业务背景**：
GPS设备厂商需要解析GPS接收器输出的NMEA消息，提取位置、速度、时间等信息。

**技术挑战**：

- 需要解析多种NMEA消息类型（GPGGA、GPRMC、GPGSV、GPGSA）
- 需要验证NMEA消息校验和
- 需要处理无效或损坏的NMEA消息
- 需要提取关键信息

**解决方案**：
使用NMEAParser解析NMEA消息，提取GPS位置、速度、时间等信息。

### 3.2 Schema定义

**NMEA消息解析Schema**：

```json
{
  "nmea_messages": [
    {
      "message_type": "GPGGA",
      "timestamp": "2025-01-21T10:00:00Z",
      "raw_message": "$GPGGA,100000.00,3113.8240,N,12128.4220,E,1,08,1.2,10.5,M,46.9,M,,*47",
      "gga_data": {
        "latitude": 31.2304,
        "longitude": 121.4737,
        "altitude": 10.5,
        "fix_quality": 1,
        "num_satellites": 8,
        "hdop": 1.2,
        "geoid_height": 46.9
      }
    },
    {
      "message_type": "GPRMC",
      "timestamp": "2025-01-21T10:00:00Z",
      "raw_message": "$GPRMC,100000.00,A,3113.8240,N,12128.4220,E,032.4,045.0,210125,,,A*6A",
      "rmc_data": {
        "status": "A",
        "latitude": 31.2304,
        "longitude": 121.4737,
        "speed_knots": 32.4,
        "speed_kmh": 60.0,
        "course": 45.0
      }
    }
  ]
}
```

### 3.3 实现代码

**完整的NMEA消息解析实现**：

```python
# 案例2：NMEA消息解析
def case2_nmea_message_parsing():
    """案例2：NMEA消息解析"""

    # 1. 初始化NMEA解析器
    nmea_parser = NMEAParser()

    # 2. 测试不同类型的NMEA消息
    test_messages = [
        # GPGGA消息
        "$GPGGA,100000.00,3113.8240,N,12128.4220,E,1,08,1.2,10.5,M,46.9,M,,*47",
        # GPRMC消息
        "$GPRMC,100000.00,A,3113.8240,N,12128.4220,E,032.4,045.0,210125,,,A*6A",
        # GPGSV消息
        "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74",
        # GPGSA消息
        "$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39"
    ]

    # 3. 解析每条消息
    parsed_results = []
    for msg in test_messages:
        try:
            parsed = nmea_parser.parse_nmea_message(msg)
            if parsed:
                parsed_results.append(parsed)
                logger.info(f"Parsed {parsed['message_type']} message successfully")
                logger.info(f"  Data: {parsed}")
            else:
                logger.warning(f"Failed to parse message: {msg[:50]}")
        except Exception as e:
            logger.error(f"Error parsing message: {e}")

    # 4. 统计解析结果
    message_types = {}
    for result in parsed_results:
        msg_type = result.get("message_type", "Unknown")
        message_types[msg_type] = message_types.get(msg_type, 0) + 1

    logger.info(f"Parsed {len(parsed_results)} messages")
    logger.info(f"Message types: {message_types}")

    return {
        "total_messages": len(test_messages),
        "parsed_messages": len(parsed_results),
        "message_types": message_types,
        "results": parsed_results
    }

# 运行案例2
if __name__ == "__main__":
    case2_nmea_message_parsing()
```

**预期结果**：

```text
Parsed GPGGA message successfully
  Data: {'message_type': 'GPGGA', 'latitude': 31.2304, 'longitude': 121.4737, ...}
Parsed GPRMC message successfully
  Data: {'message_type': 'GPRMC', 'status': 'A', 'latitude': 31.2304, ...}
Parsed GPGSV message successfully
  Data: {'message_type': 'GPGSV', 'total_messages': 3, ...}
Parsed GPGSA message successfully
  Data: {'message_type': 'GPGSA', 'selection_mode': 'A', ...}
Parsed 4 messages
Message types: {'GPGGA': 1, 'GPRMC': 1, 'GPGSV': 1, 'GPGSA': 1}
```

---

## 4. 案例3：轨迹分析和回放

### 4.1 场景描述

**业务背景**：
交通管理部门需要分析车辆行驶轨迹，识别异常行驶行为，回放历史轨迹，支持事故调查和路线优化。

**技术挑战**：

- 需要分析大量轨迹数据
- 需要计算轨迹统计信息（距离、速度、停留点）
- 需要支持轨迹回放
- 需要检测异常行为

**解决方案**：
使用TrajectoryAnalyzer分析轨迹数据，计算轨迹统计信息，检测停留点，支持轨迹回放。

### 4.2 Schema定义

**轨迹分析Schema**：

```json
{
  "vehicle_id": "VEH001",
  "trajectory_id": "TRAJ001",
  "trajectory_points": [
    {
      "sequence_number": 1,
      "timestamp": "2025-01-21T10:00:00Z",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "speed": 60.0,
      "course": 45.0
    },
    {
      "sequence_number": 2,
      "timestamp": "2025-01-21T10:01:00Z",
      "latitude": 31.2310,
      "longitude": 121.4745,
      "speed": 62.0,
      "course": 46.0
    }
  ],
  "path_analysis": {
    "total_distance": 12.5,
    "total_duration": 3600,
    "average_speed": 60.0,
    "max_speed": 80.0,
    "min_speed": 0.0
  },
  "stop_analysis": {
    "stops": [
      {
        "stop_id": "STOP001",
        "position": {
          "latitude": 31.2350,
          "longitude": 121.4800
        },
        "start_time": "2025-01-21T10:30:00Z",
        "end_time": "2025-01-21T10:45:00Z",
        "duration": 900
      }
    ],
    "total_stop_time": 900,
    "num_stops": 1
  }
}
```

### 4.3 实现代码

**完整的轨迹分析和回放实现**：

```python
from vehicle_tracking_schema.transformation import TrajectoryAnalyzer

# 案例3：轨迹分析和回放
def case3_trajectory_analysis():
    """案例3：轨迹分析和回放"""

    # 1. 初始化轨迹分析器
    analyzer = TrajectoryAnalyzer()

    # 2. 准备轨迹数据
    positions = [
        {
            "timestamp": "2025-01-21T10:00:00Z",
            "latitude": 31.2304,
            "longitude": 121.4737,
            "speed": 60.0,
            "course": 45.0
        },
        {
            "timestamp": "2025-01-21T10:01:00Z",
            "latitude": 31.2310,
            "longitude": 121.4745,
            "speed": 62.0,
            "course": 46.0
        },
        {
            "timestamp": "2025-01-21T10:02:00Z",
            "latitude": 31.2316,
            "longitude": 121.4752,
            "speed": 0.0,
            "course": 46.0
        },
        {
            "timestamp": "2025-01-21T10:17:00Z",
            "latitude": 31.2316,
            "longitude": 121.4752,
            "speed": 0.0,
            "course": 46.0
        },
        {
            "timestamp": "2025-01-21T10:18:00Z",
            "latitude": 31.2322,
            "longitude": 121.4760,
            "speed": 65.0,
            "course": 47.0
        }
    ]

    # 3. 分析轨迹
    try:
        analysis = analyzer.analyze_trajectory(positions)
        logger.info(f"Trajectory analysis:")
        logger.info(f"  Total distance: {analysis['total_distance']:.2f} km")
        logger.info(f"  Total duration: {analysis['total_duration']:.2f} seconds")
        logger.info(f"  Average speed: {analysis['average_speed']:.2f} km/h")
        logger.info(f"  Max speed: {analysis['max_speed']:.2f} km/h")
        logger.info(f"  Min speed: {analysis['min_speed']:.2f} km/h")
    except Exception as e:
        logger.error(f"Error analyzing trajectory: {e}")
        raise

    # 4. 检测停留点
    try:
        stops = analyzer.detect_stops(positions, stop_threshold=0.01, time_threshold=300)
        logger.info(f"Detected {len(stops)} stops")
        for i, stop in enumerate(stops, 1):
            logger.info(f"  Stop {i}: Duration {stop['duration']:.0f} seconds at {stop['position']['latitude']}, {stop['position']['longitude']}")
    except Exception as e:
        logger.error(f"Error detecting stops: {e}")
        raise

    return {
        "analysis": analysis,
        "stops": stops
    }

# 运行案例3
if __name__ == "__main__":
    case3_trajectory_analysis()
```

**预期结果**：

```text
Trajectory analysis:
  Total distance: 0.85 km
  Total duration: 1080.0 seconds
  Average speed: 2.83 km/h
  Max speed: 65.0 km/h
  Min speed: 0.0 km/h
Detected 1 stops
  Stop 1: Duration 900 seconds at 31.2316, 121.4752
```

---

## 5. 案例4：地理围栏监控

### 5.1 场景描述

**业务背景**：
企业需要设置地理围栏，监控车辆进出围栏区域，触发告警和通知，支持区域管理和安全监控。

**技术挑战**：

- 需要定义地理围栏（圆形、多边形、矩形）
- 需要实时判断车辆位置与围栏的关系
- 需要检测围栏进出事件
- 需要触发告警和通知

**解决方案**：
使用GeofenceMonitor定义地理围栏，实时监控车辆位置，检测围栏进出事件。

### 5.2 Schema定义

**地理围栏监控Schema**：

```json
{
  "geofences": [
    {
      "geofence_id": "GEOFENCE001",
      "geofence_name": "仓库区域",
      "geofence_type": "Circle",
      "coordinates": {
        "center": {
          "latitude": 31.2304,
          "longitude": 121.4737
        },
        "radius": 500.0
      }
    },
    {
      "geofence_id": "GEOFENCE002",
      "geofence_name": "办公区域",
      "geofence_type": "Polygon",
      "coordinates": {
        "points": [
          {"latitude": 31.2400, "longitude": 121.4800},
          {"latitude": 31.2400, "longitude": 121.4900},
          {"latitude": 31.2500, "longitude": 121.4900},
          {"latitude": 31.2500, "longitude": 121.4800}
        ]
      }
    }
  ],
  "events": [
    {
      "event_id": "EVENT001",
      "geofence_id": "GEOFENCE001",
      "vehicle_id": "VEH001",
      "event_type": "ENTER",
      "timestamp": "2025-01-21T10:00:00Z",
      "position": {
        "latitude": 31.2305,
        "longitude": 121.4738
      }
    }
  ]
}
```

### 5.3 实现代码

**完整的地理围栏监控实现**：

```python
from vehicle_tracking_schema.transformation import GeofenceMonitor

# 案例4：地理围栏监控
def case4_geofence_monitoring():
    """案例4：地理围栏监控"""

    # 1. 初始化地理围栏监控器
    monitor = GeofenceMonitor()

    # 2. 创建地理围栏
    geofences = [
        {
            "geofence_id": "GEOFENCE001",
            "geofence_name": "仓库区域",
            "geofence_type": "Circle",
            "coordinates": {
                "center": {"latitude": 31.2304, "longitude": 121.4737},
                "radius": 500.0  # 米
            }
        },
        {
            "geofence_id": "GEOFENCE002",
            "geofence_name": "办公区域",
            "geofence_type": "Polygon",
            "coordinates": {
                "points": [
                    {"latitude": 31.2400, "longitude": 121.4800},
                    {"latitude": 31.2400, "longitude": 121.4900},
                    {"latitude": 31.2500, "longitude": 121.4900},
                    {"latitude": 31.2500, "longitude": 121.4800}
                ]
            }
        }
    ]

    for geofence in geofences:
        monitor.add_geofence(geofence)
        logger.info(f"Added geofence: {geofence['geofence_name']}")

    # 3. 模拟车辆位置更新
    vehicle_positions = [
        {"vehicle_id": "VEH001", "latitude": 31.2305, "longitude": 121.4738, "timestamp": "2025-01-21T10:00:00Z"},
        {"vehicle_id": "VEH001", "latitude": 31.2405, "longitude": 121.4850, "timestamp": "2025-01-21T10:05:00Z"},
        {"vehicle_id": "VEH001", "latitude": 31.2505, "longitude": 121.4950, "timestamp": "2025-01-21T10:10:00Z"}
    ]

    # 4. 监控车辆位置
    events = []
    for position in vehicle_positions:
        try:
            detected_events = monitor.check_position(position)
            if detected_events:
                events.extend(detected_events)
                for event in detected_events:
                    logger.info(f"Geofence event: {event['event_type']} - {event['geofence_id']} at {event['timestamp']}")
        except Exception as e:
            logger.error(f"Error checking position: {e}")

    logger.info(f"Total geofence events: {len(events)}")

    return {
        "geofences": geofences,
        "events": events
    }

# 运行案例4
if __name__ == "__main__":
    case4_geofence_monitoring()
```

**预期结果**：

```text
Added geofence: 仓库区域
Added geofence: 办公区域
Geofence event: ENTER - GEOFENCE001 at 2025-01-21T10:00:00Z
Geofence event: ENTER - GEOFENCE002 at 2025-01-21T10:05:00Z
Geofence event: EXIT - GEOFENCE002 at 2025-01-21T10:10:00Z
Total geofence events: 3
```

---

## 6. 案例5：AIS船舶跟踪

### 6.1 场景描述

**业务背景**：
海事管理部门需要跟踪船舶位置，监控船舶航行状态，支持海上交通管理和安全监控。

**技术挑战**：

- 需要解析AIS消息（NMEA格式）
- 需要解码6-bit编码的AIS数据
- 需要提取船舶位置和状态信息
- 需要存储船舶跟踪数据

**解决方案**：
使用AISMessageParser解析AIS消息，提取船舶位置、速度、航向等信息，存储到数据库中。

### 6.2 Schema定义

**AIS船舶跟踪Schema**：

```json
{
  "vessel_id": "VESSEL001",
  "mmsi": "123456789",
  "ais_messages": [
    {
      "message_type": 1,
      "message_type_name": "Position Report Class A",
      "timestamp": "2025-01-21T10:00:00Z",
      "position_report": {
        "latitude": 31.2304,
        "longitude": 121.4737,
        "course_over_ground": 45.0,
        "speed_over_ground": 15.5,
        "heading": 46,
        "navigation_status": 0
      }
    }
  ],
  "vessel_positions": [
    {
      "timestamp": "2025-01-21T10:00:00Z",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "course": 45.0,
      "speed": 15.5,
      "heading": 46,
      "navigation_status": 0
    }
  ]
}
```

### 6.3 实现代码

**完整的AIS船舶跟踪实现**：

```python
from vehicle_tracking_schema.transformation import AISMessageParser

# 案例5：AIS船舶跟踪
def case5_ais_vessel_tracking():
    """案例5：AIS船舶跟踪"""

    # 1. 初始化AIS消息解析器
    ais_parser = AISMessageParser()

    # 2. 模拟AIS消息（NMEA格式）
    ais_messages = [
        "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46",
        "!AIVDM,1,1,,B,133m@ogP00PD;88MD5MTDww@2D7k,0*47"
    ]

    # 3. 解析AIS消息
    parsed_messages = []
    for ais_msg in ais_messages:
        try:
            parsed = ais_parser.parse_ais_message(ais_msg)
            if parsed:
                parsed_messages.append(parsed)
                logger.info(f"Parsed AIS message type {parsed['message_type']}: {parsed['message_type_name']}")
                if parsed.get("mmsi"):
                    logger.info(f"  MMSI: {parsed['mmsi']}")
                if parsed.get("position_report"):
                    pos = parsed["position_report"]
                    logger.info(f"  Position: {pos.get('latitude')}, {pos.get('longitude')}")
                    logger.info(f"  Speed: {pos.get('speed_over_ground')} knots")
                    logger.info(f"  Course: {pos.get('course_over_ground')} degrees")
        except Exception as e:
            logger.error(f"Error parsing AIS message: {e}")

    logger.info(f"Parsed {len(parsed_messages)} AIS messages")

    return {
        "total_messages": len(ais_messages),
        "parsed_messages": len(parsed_messages),
        "results": parsed_messages
    }

# 运行案例5
if __name__ == "__main__":
    case5_ais_vessel_tracking()
```

**预期结果**：

```text
Parsed AIS message type 1: Position Report Class A
  MMSI: 123456789
  Position: 31.2304, 121.4737
  Speed: 15.5 knots
  Course: 45.0 degrees
Parsed 2 AIS messages
```

---

## 7. 案例6：北斗定位跟踪

### 7.1 场景描述

**业务背景**：
中国地区的车辆跟踪系统需要使用北斗定位系统，与GPS定位系统互补，提供更可靠的定位服务。

**技术挑战**：

- 需要解析BDS消息（类似NMEA格式）
- 需要提取北斗位置数据
- 需要支持GPS和北斗双系统定位
- 需要存储北斗定位数据

**解决方案**：
使用BDSParser解析BDS消息，提取北斗位置数据，与GPS数据融合使用。

### 7.2 Schema定义

**北斗定位跟踪Schema**：

```json
{
  "vehicle_id": "VEH001",
  "beidou_positions": [
    {
      "timestamp": "2025-01-21T10:00:00Z",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "altitude": 10.5,
      "speed": 60.0,
      "course": 45.0,
      "fix_quality": 1,
      "num_satellites": 12,
      "hdop": 1.0,
      "source": "BDS"
    }
  ]
}
```

### 7.3 实现代码

**完整的北斗定位跟踪实现**：

```python
from vehicle_tracking_schema.transformation import BDSParser

# 案例6：北斗定位跟踪
def case6_beidou_tracking():
    """案例6：北斗定位跟踪"""

    # 1. 初始化BDS解析器
    bds_parser = BDSParser()

    # 2. 模拟BDS消息
    bds_messages = [
        "$BDGGA,100000.00,3113.8240,N,12128.4220,E,1,12,1.0,10.5,M,46.9,M,,*47",
        "$BDRMC,100000.00,A,3113.8240,N,12128.4220,E,032.4,045.0,210125,,,A*6A"
    ]

    # 3. 解析BDS消息
    parsed_messages = []
    for bds_msg in bds_messages:
        try:
            parsed = bds_parser.parse_bds_message(bds_msg)
            if parsed:
                parsed_messages.append(parsed)
                logger.info(f"Parsed BDS message type {parsed['message_type']}")
                if parsed.get("bds_gga_data"):
                    gga = parsed["bds_gga_data"]
                    logger.info(f"  Position: {gga.get('latitude')}, {gga.get('longitude')}")
                    logger.info(f"  Satellites: {gga.get('num_satellites')}")
                if parsed.get("bds_rmc_data"):
                    rmc = parsed["bds_rmc_data"]
                    logger.info(f"  Speed: {rmc.get('speed_kmh')} km/h")
                    logger.info(f"  Course: {rmc.get('course')} degrees")
        except Exception as e:
            logger.error(f"Error parsing BDS message: {e}")

    logger.info(f"Parsed {len(parsed_messages)} BDS messages")

    return {
        "total_messages": len(bds_messages),
        "parsed_messages": len(parsed_messages),
        "results": parsed_messages
    }

# 运行案例6
if __name__ == "__main__":
    case6_beidou_tracking()
```

**预期结果**：

```text
Parsed BDS message type BDGGA
  Position: 31.2304, 121.4737
  Satellites: 12
Parsed BDS message type BDRMC
  Speed: 60.0 km/h
  Course: 45.0 degrees
Parsed 2 BDS messages
```

---

## 8. 案例7：车辆跟踪数据存储和查询

### 8.1 场景描述

**业务背景**：
车辆跟踪系统需要存储大量位置数据，支持高效查询和分析，生成报表和统计信息。

**技术挑战**：

- 需要存储大量位置数据（百万级记录）
- 需要支持高效的时间范围查询
- 需要支持车辆轨迹查询
- 需要生成统计报表

**解决方案**：
使用VehicleTrackingStorage存储位置数据，实现高效的查询和分析功能。

### 8.2 实现代码

**完整的车辆跟踪数据存储和查询实现**：

```python
# 案例7：车辆跟踪数据存储和查询
def case7_tracking_data_storage():
    """案例7：车辆跟踪数据存储和查询"""

    # 1. 初始化存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "tracking_db",
        "user": "tracking_user",
        "password": "tracking_password"
    }
    storage = VehicleTrackingStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 2. 查询车辆位置
    vehicle_id = "VEH001"
    positions = storage.query_positions(vehicle_id, limit=100)
    logger.info(f"Found {len(positions)} positions for vehicle {vehicle_id}")

    # 3. 查询时间范围内的位置
    from datetime import datetime, timedelta
    start_time = datetime.now() - timedelta(hours=24)
    end_time = datetime.now()
    recent_positions = storage.query_positions(vehicle_id, start_time=start_time, end_time=end_time, limit=1000)
    logger.info(f"Found {len(recent_positions)} positions in last 24 hours")

    # 4. 统计信息
    if positions:
        speeds = [p.get("speed", 0) for p in positions if p.get("speed")]
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            max_speed = max(speeds)
            logger.info(f"Speed statistics:")
            logger.info(f"  Average speed: {avg_speed:.2f} km/h")
            logger.info(f"  Max speed: {max_speed:.2f} km/h")

    return {
        "total_positions": len(positions),
        "recent_positions": len(recent_positions),
        "statistics": {
            "average_speed": avg_speed if speeds else 0,
            "max_speed": max_speed if speeds else 0
        }
    }

# 运行案例7
if __name__ == "__main__":
    case7_tracking_data_storage()
```

**预期结果**：

```text
Found 100 positions for vehicle VEH001
Found 50 positions in last 24 hours
Speed statistics:
  Average speed: 55.50 km/h
  Max speed: 80.00 km/h
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
