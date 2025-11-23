# 智能交通系统Schema实践案例

## 📑 目录

- [智能交通系统Schema实践案例](#智能交通系统schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：交通信号控制](#2-案例1交通信号控制)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：路况监控](#3-案例2路况监控)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：车辆通信（V2V）](#4-案例3车辆通信v2v)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：交通流量分析](#5-案例4交通流量分析)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 Schema定义](#52-schema定义)
    - [5.3 实现代码](#53-实现代码)
  - [6. 案例5：拥堵检测和预警](#6-案例5拥堵检测和预警)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 Schema定义](#62-schema定义)
    - [6.3 实现代码](#63-实现代码)
  - [7. 案例6：路径规划](#7-案例6路径规划)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：事件检测和处理](#8-案例7事件检测和处理)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：ITS数据存储系统](#9-案例8its数据存储系统)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 实现代码](#92-实现代码)
  - [10. 案例9：智能信号优化系统](#10-案例9智能信号优化系统)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 Schema定义](#102-schema定义)
    - [10.3 实现代码](#103-实现代码)
  - [11. 案例10：交通预测系统](#11-案例10交通预测系统)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)
  - [12. 案例11：事故预防系统](#12-案例11事故预防系统)
    - [12.1 场景描述](#121-场景描述)
    - [12.2 Schema定义](#122-schema定义)
    - [12.3 实现代码](#123-实现代码)

---

## 1. 案例概述

本文档提供智能交通系统Schema在实际应用中的实践案例，
涵盖交通信号控制、路况监控、车辆通信、路况分析等场景。

---

## 2. 案例1：交通信号控制

### 2.1 场景描述

**应用场景**：
城市交通管理部门需要实现智能交通信号控制系统，根据实时交通流量自动调整信号灯配时，优化交通流，减少拥堵。

**技术挑战**：

- 实时交通数据采集和处理
- 信号配时优化算法
- 多路口协调控制
- 系统可靠性和实时性要求

**解决方案**：
使用ITS_Schema定义交通信号控制数据结构，实现基于实时交通流量的自适应信号控制算法。

### 2.2 Schema定义

**交通信号控制Schema**：

```json
{
  "intersection_id": "INT001",
  "intersection_name": "人民路-解放路交叉口",
  "location": {
    "latitude": 31.2304,
    "longitude": 121.4737
  },
  "signal_states": [
    {
      "signal_id": "SIG001",
      "direction": "North",
      "current_state": "Green",
      "state_duration": 45,
      "next_state": "Yellow",
      "transition_time": "2025-01-21T10:30:45Z"
    },
    {
      "signal_id": "SIG002",
      "direction": "South",
      "current_state": "Red",
      "state_duration": 30,
      "next_state": "Green",
      "transition_time": "2025-01-21T10:31:00Z"
    }
  ],
  "phases": [
    {
      "phase_id": 1,
      "phase_name": "南北直行",
      "signals": ["SIG001", "SIG002"],
      "duration": 45,
      "min_duration": 20,
      "max_duration": 60,
      "yellow_time": 5,
      "all_red_time": 2
    },
    {
      "phase_id": 2,
      "phase_name": "东西直行",
      "signals": ["SIG003", "SIG004"],
      "duration": 40,
      "min_duration": 20,
      "max_duration": 60,
      "yellow_time": 5,
      "all_red_time": 2
    }
  ],
  "timing_plan": {
    "cycle_time": 120,
    "offset": 0,
    "phase_sequence": [1, 2, 3, 4],
    "green_split": [0.375, 0.333, 0.167, 0.125],
    "coordination": {
      "coordination_type": "Arterial",
      "master_intersection": "INT000",
      "coordination_offset": 30
    }
  },
  "control_mode": "Adaptive",
  "timestamp": "2025-01-21T10:30:00Z"
}
```

### 2.3 实现代码

**完整的交通信号控制实现**：

```python
import logging
from typing import Dict, List
from datetime import datetime
from its_schema.transformation import TrafficSignalController, SignalTimingOptimizer

logger = logging.getLogger(__name__)

# 案例1：交通信号控制
def case1_traffic_signal_control():
    """案例1：交通信号控制"""

    # 1. 初始化信号控制器
    controller = TrafficSignalController("INT001")

    # 2. 设置相位序列
    phases = [
        {
            "phase_id": 1,
            "phase_name": "南北直行",
            "signals": ["SIG001", "SIG002"],
            "duration": 45,
            "min_duration": 20,
            "max_duration": 60,
            "yellow_time": 5,
            "all_red_time": 2
        },
        {
            "phase_id": 2,
            "phase_name": "东西直行",
            "signals": ["SIG003", "SIG004"],
            "duration": 40,
            "min_duration": 20,
            "max_duration": 60,
            "yellow_time": 5,
            "all_red_time": 2
        },
        {
            "phase_id": 3,
            "phase_name": "南北左转",
            "signals": ["SIG005", "SIG006"],
            "duration": 20,
            "min_duration": 15,
            "max_duration": 30,
            "yellow_time": 3,
            "all_red_time": 1
        },
        {
            "phase_id": 4,
            "phase_name": "东西左转",
            "signals": ["SIG007", "SIG008"],
            "duration": 15,
            "min_duration": 15,
            "max_duration": 30,
            "yellow_time": 3,
            "all_red_time": 1
        }
    ]
    controller.set_phases(phases)

    # 3. 优化周期时间
    optimizer = SignalTimingOptimizer()
    traffic_flows = {
        "North": 800.0,  # veh/h
        "South": 750.0,
        "East": 600.0,
        "West": 650.0
    }
    saturation_flows = {
        "North": 1800.0,
        "South": 1800.0,
        "East": 1800.0,
        "West": 1800.0
    }

    optimal_cycle_time = optimizer.optimize_cycle_time(traffic_flows, saturation_flows)
    controller.set_cycle_time(optimal_cycle_time)

    # 4. 启动信号周期
    controller.start_cycle()

    # 5. 获取当前信号状态
    current_state = controller.get_current_signal_state()
    print(f"Current signal state: {current_state}")

    # 6. 模拟运行一段时间
    import time
    for i in range(5):
        time.sleep(1)
        state = controller.get_current_signal_state()
        if state:
            print(f"Phase {state['current_phase']}: {state['phase_id']}, "
                  f"Remaining: {state['remaining_time']:.1f}s")

    return controller

# 运行案例
if __name__ == "__main__":
    controller = case1_traffic_signal_control()
    print("Case 1 completed successfully")
```

---

## 3. 案例2：路况监控

### 3.1 场景描述

**应用场景**：
交通管理部门需要实时监控道路状况，通过传感器和视频监控系统检测拥堵、事故等事件，及时发布路况信息。

**技术挑战**：

- 多源数据融合（传感器、视频、GPS）
- 实时事件检测算法
- 路况信息准确性和及时性
- 大规模数据处理

**解决方案**：
使用ITS_Schema定义路况监控数据结构，实现多源数据融合和实时事件检测系统。

### 3.2 Schema定义

**路况监控Schema**：

```json
{
  "sensor_data": {
    "sensor_id": "SENSOR001",
    "sensor_type": "Loop",
    "location": {
      "latitude": 31.2304,
      "longitude": 121.4737,
      "road_name": "人民路",
      "lane_id": 1
    },
    "traffic_metrics": {
      "vehicle_count": 150,
      "average_speed": 35.5,
      "occupancy": 75.2,
      "density": 45.8,
      "headway": 8.5
    },
    "timestamp": "2025-01-21T10:30:00Z",
    "data_quality": "Good"
  },
  "video_data": {
    "camera_id": "CAM001",
    "camera_type": "Fixed",
    "location": {
      "latitude": 31.2304,
      "longitude": 121.4737
    },
    "detection_results": [
      {
        "vehicle_id": "VEH001",
        "vehicle_type": "Car",
        "bbox": {
          "x1": 100,
          "y1": 200,
          "x2": 300,
          "y2": 400
        },
        "confidence": 0.95,
        "license_plate": "京A12345",
        "speed": 38.2
      }
    ],
    "timestamp": "2025-01-21T10:30:00Z",
    "frame_id": "FRAME001",
    "resolution": "FullHD"
  }
}
```

### 3.3 实现代码

**完整的路况监控实现**：

```python
from its_schema.transformation import (
    TrafficSensorDataCollector, VideoTrafficDataProcessor, GPSDataProcessor
)

def case2_traffic_monitoring():
    """案例2：路况监控"""

    # 1. 传感器数据采集
    sensor_collector = TrafficSensorDataCollector("SENSOR001", "192.168.1.100", 502)
    sensor_collector.connect(timeout=10.0)

    try:
        sensor_data = sensor_collector.read_traffic_data()
        print(f"Sensor data: {sensor_data}")
    finally:
        sensor_collector.disconnect()

    # 2. 视频数据处理
    video_processor = VideoTrafficDataProcessor("CAM001")
    video_processor.connect_camera("rtsp://192.168.1.101:554/stream", timeout=10)

    try:
        video_data = video_processor.process_frame()
        print(f"Video data: {video_data}")
        print(f"Detected {video_data['vehicle_count']} vehicles")
    finally:
        video_processor._cleanup_camera()

    # 3. GPS数据处理
    gps_processor = GPSDataProcessor()
    nmea_message = "$GPRMC,103000.00,A,3113.8240,N,12128.4220,E,38.5,045.0,210125,0.0,E,A*2C"

    gps_data = gps_processor.parse_nmea_message(nmea_message)
    print(f"GPS data: {gps_data}")

    # 4. 数据融合和分析
    # 这里可以添加数据融合逻辑

    return {
        "sensor_data": sensor_data,
        "video_data": video_data,
        "gps_data": gps_data
    }

# 运行案例
if __name__ == "__main__":
    result = case2_traffic_monitoring()
    print("Case 2 completed successfully")
```

---

## 4. 案例3：车辆通信（V2V）

### 4.1 场景描述

**应用场景**：
车辆通过V2V通信获取周围车辆的位置、速度、方向等信息，实现协同驾驶和碰撞预警。

**技术挑战**：

- V2V消息格式标准化（SAE J2735、ETSI ITS）
- 消息传输的实时性和可靠性
- 安全认证和消息完整性
- 大规模车辆通信管理

**解决方案**：
使用ITS_Schema定义V2V消息数据结构，实现BSM消息的解析和处理系统。

### 4.2 Schema定义

**V2V消息Schema**：

```json
{
  "message_type": "BSM",
  "vehicle_id": 12345678,
  "timestamp": "2025-01-21T10:30:00Z",
  "position": {
    "latitude": 31.2304,
    "longitude": 121.4737
  },
  "speed": 15.5,
  "heading": 45.0,
  "message_size": 150
}
```

### 4.3 实现代码

**完整的V2V消息处理实现**：

```python
from its_schema.transformation import V2VMessageProcessor

def case3_v2v_communication():
    """案例3：车辆通信（V2V）"""

    # 1. 初始化V2V消息处理器
    v2v_processor = V2VMessageProcessor()

    # 2. 构建BSM消息
    vehicle_data = {
        "vehicle_id": 12345678,
        "latitude": 31.2304,
        "longitude": 121.4737,
        "speed": 15.5,  # m/s
        "heading": 45.0  # degrees
    }

    bsm_message = v2v_processor.build_bsm_message(vehicle_data)
    print(f"BSM message built: {len(bsm_message)} bytes")

    # 3. 解析BSM消息
    parsed_bsm = v2v_processor.parse_bsm_message(bsm_message)
    print(f"Parsed BSM: {parsed_bsm}")

    # 4. 模拟接收其他车辆的BSM消息
    other_vehicle_bsm = bsm_message  # 实际应用中从网络接收
    other_vehicle_data = v2v_processor.parse_bsm_message(other_vehicle_bsm)

    # 5. 计算车辆间距离和相对速度
    import math

    lat1 = math.radians(vehicle_data["latitude"])
    lon1 = math.radians(vehicle_data["longitude"])
    lat2 = math.radians(other_vehicle_data["position"]["latitude"])
    lon2 = math.radians(other_vehicle_data["position"]["longitude"])

    # 使用Haversine公式计算距离
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = 6371000 * c  # 地球半径6371km，转换为米

    print(f"Distance to other vehicle: {distance:.2f} meters")

    # 6. 碰撞预警（如果距离小于50米且相对速度较大）
    if distance < 50:
        relative_speed = abs(vehicle_data["speed"] - other_vehicle_data["speed"])
        if relative_speed > 5:  # 相对速度大于5 m/s
            print(f"WARNING: Potential collision risk! Distance: {distance:.2f}m, "
                  f"Relative speed: {relative_speed:.2f}m/s")

    return {
        "bsm_message": bsm_message,
        "parsed_data": parsed_bsm,
        "distance": distance
    }

# 运行案例
if __name__ == "__main__":
    result = case3_v2v_communication()
    print("Case 3 completed successfully")
```

---

## 5. 案例4：交通流量分析

### 5.1 场景描述

**应用场景**：
交通管理部门需要分析历史交通流量数据，识别交通模式，为交通规划和管理提供决策支持。

**技术挑战**：

- 大规模时序数据处理
- 交通模式识别算法
- 多维度数据分析
- 数据可视化

**解决方案**：
使用ITS_Schema定义交通流量分析数据结构，实现交通流量模式分析系统。

### 5.2 Schema定义

**交通流量分析Schema**：

```json
{
  "analysis_type": "flow_pattern",
  "time_window_minutes": 15,
  "total_data_points": 1000,
  "windows": [
    {
      "window_start": "2025-01-21T10:00:00Z",
      "vehicle_count_avg": 120.5,
      "vehicle_count_max": 180,
      "vehicle_count_min": 80,
      "speed_avg": 45.2,
      "speed_max": 60.0,
      "speed_min": 30.0,
      "data_points": 15
    }
  ]
}
```

### 5.3 实现代码

**完整的交通流量分析实现**：

```python
from its_schema.transformation import TrafficFlowAnalyzer
from datetime import datetime, timedelta
import random

def case4_traffic_flow_analysis():
    """案例4：交通流量分析"""

    # 1. 生成模拟交通数据
    traffic_data_list = []
    base_time = datetime(2025, 1, 21, 10, 0, 0)

    for i in range(100):
        traffic_data_list.append({
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "vehicle_count": random.randint(80, 200),
            "average_speed": random.uniform(30.0, 60.0),
            "occupancy": random.uniform(50.0, 90.0)
        })

    # 2. 初始化流量分析器
    analyzer = TrafficFlowAnalyzer()

    # 3. 分析交通流量模式（15分钟窗口）
    analysis_result = analyzer.analyze_flow_pattern(traffic_data_list, time_window_minutes=15)

    print(f"Analysis type: {analysis_result['analysis_type']}")
    print(f"Time window: {analysis_result['time_window_minutes']} minutes")
    print(f"Total data points: {analysis_result['total_data_points']}")
    print(f"Number of windows: {len(analysis_result['windows'])}")

    # 4. 输出分析结果
    for window in analysis_result['windows']:
        print(f"\nWindow: {window['window_start']}")
        print(f"  Average vehicle count: {window['vehicle_count_avg']:.1f}")
        print(f"  Average speed: {window['speed_avg']:.1f} km/h")
        print(f"  Data points: {window['data_points']}")

    # 5. 识别交通模式
    for window in analysis_result['windows']:
        avg_speed = window['speed_avg']
        avg_count = window['vehicle_count_avg']

        if avg_speed < 30 and avg_count > 150:
            flow_pattern = "Congested"
        elif avg_speed < 50 and avg_count > 100:
            flow_pattern = "Unstable_Flow"
        elif avg_speed >= 50:
            flow_pattern = "Free_Flow"
        else:
            flow_pattern = "Stable_Flow"

        print(f"Window {window['window_start']}: Flow pattern = {flow_pattern}")

    return analysis_result

# 运行案例
if __name__ == "__main__":
    result = case4_traffic_flow_analysis()
    print("Case 4 completed successfully")
```

---

## 6. 案例5：拥堵检测和预警

### 6.1 场景描述

**应用场景**：
交通管理部门需要实时检测道路拥堵情况，及时发布拥堵预警信息，引导车辆绕行。

**技术挑战**：

- 实时拥堵检测算法
- 拥堵等级判断标准
- 预警信息发布机制
- 拥堵预测

**解决方案**：
使用ITS_Schema定义拥堵检测数据结构，实现实时拥堵检测和预警系统。

### 6.2 Schema定义

**拥堵检测Schema**：

```json
{
  "segment_id": "SEG001",
  "location": {
    "latitude": 31.2304,
    "longitude": 121.4737
  },
  "congestion_status": {
    "is_congested": true,
    "congestion_level": "Moderate",
    "congestion_index": 0.65,
    "indicators": {
      "speed_ratio": 0.55,
      "occupancy_ratio": 1.15,
      "density_ratio": 1.25,
      "queue_length": 500.0,
      "delay_time": 120
    },
    "start_time": "2025-01-21T10:15:00Z",
    "duration": 900,
    "affected_length": 2000.0
  },
  "timestamp": "2025-01-21T10:30:00Z"
}
```

### 6.3 实现代码

**完整的拥堵检测实现**：

```python
from its_schema.transformation import CongestionDetector

def case5_congestion_detection():
    """案例5：拥堵检测和预警"""

    # 1. 初始化拥堵检测器
    detector = CongestionDetector()

    # 2. 模拟交通数据
    traffic_data = {
        "average_speed": 18.5,  # km/h
        "occupancy": 85.0  # %
    }

    # 3. 检测拥堵
    congestion_result = detector.detect_congestion(traffic_data)

    print(f"Congestion detection result:")
    print(f"  Is congested: {congestion_result['is_congested']}")
    print(f"  Congestion level: {congestion_result['congestion_level']}")
    print(f"  Speed: {congestion_result['speed']} km/h")
    print(f"  Occupancy: {congestion_result['occupancy']}%")

    # 4. 根据拥堵等级发布预警
    if congestion_result['congestion_level'] == "Severe":
        print("ALERT: Severe congestion detected! Consider alternative routes.")
    elif congestion_result['congestion_level'] == "Moderate":
        print("WARNING: Moderate congestion detected. Expect delays.")
    elif congestion_result['congestion_level'] == "Light":
        print("INFO: Light congestion detected.")
    else:
        print("INFO: No congestion detected.")

    return congestion_result

# 运行案例
if __name__ == "__main__":
    result = case5_congestion_detection()
    print("Case 5 completed successfully")
```

---

## 7. 案例6：路径规划

### 7.1 场景描述

**应用场景**：
导航系统需要根据实时路况信息规划最优路径，考虑距离、时间、拥堵程度等因素。

**技术挑战**：

- 实时路况数据获取
- 多目标路径优化算法
- 动态路径调整
- 路径规划准确性

**解决方案**：
使用ITS_Schema定义路径规划数据结构，实现多目标路径规划系统。

### 7.2 Schema定义

**路径规划Schema**：

```json
{
  "route_id": "ROUTE001",
  "origin": {
    "latitude": 31.2304,
    "longitude": 121.4737
  },
  "destination": {
    "latitude": 31.2504,
    "longitude": 121.4937
  },
  "route_options": {
    "optimization_criteria": "Fastest",
    "avoid_tolls": false,
    "avoid_highways": false,
    "avoid_ferries": false
  },
  "calculated_route": {
    "total_distance": 5000.0,
    "total_duration": 600,
    "estimated_duration": 720,
    "waypoints": [
      {
        "sequence": 1,
        "location": {
          "latitude": 31.2354,
          "longitude": 121.4787
        },
        "distance_from_origin": 1000.0,
        "estimated_arrival": "2025-01-21T10:35:00Z",
        "road_name": "人民路",
        "maneuver": "Turn_Right"
      }
    ],
    "segments": [
      {
        "segment_id": "SEG001",
        "start_location": {
          "latitude": 31.2304,
          "longitude": 121.4737
        },
        "end_location": {
          "latitude": 31.2354,
          "longitude": 121.4787
        },
        "distance": 1000.0,
        "duration": 120,
        "average_speed": 30.0,
        "road_type": "Arterial",
        "congestion_level": "Light"
      }
    ]
  },
  "timestamp": "2025-01-21T10:30:00Z"
}
```

### 7.3 实现代码

**路径规划实现（简化版）**：

```python
def case6_route_planning():
    """案例6：路径规划"""

    # 1. 定义起点和终点
    origin = {
        "latitude": 31.2304,
        "longitude": 121.4737
    }

    destination = {
        "latitude": 31.2504,
        "longitude": 121.4937
    }

    # 2. 路径规划选项
    route_options = {
        "optimization_criteria": "Fastest",
        "avoid_tolls": False,
        "avoid_highways": False,
        "avoid_ferries": False
    }

    # 3. 模拟路径规划（实际实现需要使用地图API，如Google Maps、高德地图等）
    route_data = {
        "route_id": "ROUTE001",
        "origin": origin,
        "destination": destination,
        "route_options": route_options,
        "calculated_route": {
            "total_distance": 5000.0,  # meters
            "total_duration": 600,  # seconds
            "estimated_duration": 720,  # seconds (考虑拥堵)
            "waypoints": [
                {
                    "sequence": 1,
                    "location": {
                        "latitude": 31.2354,
                        "longitude": 121.4787
                    },
                    "distance_from_origin": 1000.0,
                    "estimated_arrival": "2025-01-21T10:35:00Z",
                    "road_name": "人民路",
                    "maneuver": "Turn_Right"
                }
            ],
            "segments": [
                {
                    "segment_id": "SEG001",
                    "start_location": origin,
                    "end_location": {
                        "latitude": 31.2354,
                        "longitude": 121.4787
                    },
                    "distance": 1000.0,
                    "duration": 120,
                    "average_speed": 30.0,
                    "road_type": "Arterial",
                    "congestion_level": "Light"
                }
            ]
        },
        "timestamp": datetime.now().isoformat()
    }

    print(f"Route planned:")
    print(f"  Total distance: {route_data['calculated_route']['total_distance']} meters")
    print(f"  Estimated duration: {route_data['calculated_route']['estimated_duration']} seconds")
    print(f"  Number of waypoints: {len(route_data['calculated_route']['waypoints'])}")

    return route_data

# 运行案例
if __name__ == "__main__":
    result = case6_route_planning()
    print("Case 6 completed successfully")
```

---

## 8. 案例7：事件检测和处理

### 8.1 场景描述

**应用场景**：
交通管理部门需要自动检测交通事故、施工、拥堵等事件，及时处理和发布信息。

**技术挑战**：

- 多源事件检测（传感器、视频、V2X报告）
- 事件类型识别和分类
- 事件影响评估
- 事件处理流程管理

**解决方案**：
使用ITS_Schema定义事件检测数据结构，实现自动事件检测和处理系统。

### 8.2 Schema定义

**事件检测Schema**：

```json
{
  "event_id": "EVT001",
  "event_type": "Accident",
  "location": {
    "latitude": 31.2304,
    "longitude": 121.4737
  },
  "event_details": {
    "severity": "High",
    "description": "两车追尾事故",
    "start_time": "2025-01-21T10:25:00Z",
    "end_time": null,
    "affected_lanes": [1, 2],
    "affected_directions": ["North"],
    "impact": {
      "affected_length": 500.0,
      "expected_delay": 600,
      "speed_reduction": 30.0,
      "capacity_reduction": 50.0
    }
  },
  "detection_method": "Automatic_Video",
  "confidence": 0.95,
  "timestamp": "2025-01-21T10:30:00Z"
}
```

### 8.3 实现代码

**事件检测和处理实现**：

```python
def case7_event_detection():
    """案例7：事件检测和处理"""

    # 1. 模拟检测到的事件
    event_data = {
        "event_id": "EVT001",
        "event_type": "Accident",
        "location": {
            "latitude": 31.2304,
            "longitude": 121.4737
        },
        "event_details": {
            "severity": "High",
            "description": "两车追尾事故",
            "start_time": "2025-01-21T10:25:00Z",
            "end_time": None,
            "affected_lanes": [1, 2],
            "affected_directions": ["North"],
            "impact": {
                "affected_length": 500.0,
                "expected_delay": 600,
                "speed_reduction": 30.0,
                "capacity_reduction": 50.0
            }
        },
        "detection_method": "Automatic_Video",
        "confidence": 0.95,
        "timestamp": datetime.now().isoformat()
    }

    print(f"Event detected:")
    print(f"  Event ID: {event_data['event_id']}")
    print(f"  Event type: {event_data['event_type']}")
    print(f"  Severity: {event_data['event_details']['severity']}")
    print(f"  Confidence: {event_data['confidence']}")

    # 2. 根据事件严重程度处理
    severity = event_data['event_details']['severity']

    if severity == "Critical":
        print("CRITICAL: Immediate response required!")
        # 发送紧急通知
        # 调度救援车辆
        # 封闭相关车道
    elif severity == "High":
        print("HIGH: Rapid response required!")
        # 发送预警信息
        # 调整信号控制
        # 发布绕行建议
    elif severity == "Medium":
        print("MEDIUM: Standard response.")
        # 记录事件
        # 监控影响
    else:
        print("LOW: Monitor situation.")
        # 记录事件

    # 3. 评估事件影响
    impact = event_data['event_details']['impact']
    print(f"\nEvent impact:")
    print(f"  Affected length: {impact['affected_length']} meters")
    print(f"  Expected delay: {impact['expected_delay']} seconds")
    print(f"  Speed reduction: {impact['speed_reduction']} km/h")
    print(f"  Capacity reduction: {impact['capacity_reduction']}%")

    return event_data

# 运行案例
if __name__ == "__main__":
    result = case7_event_detection()
    print("Case 7 completed successfully")
```

---

## 9. 案例8：ITS数据存储系统

### 9.1 场景描述

**应用场景**：
ITS系统需要存储大量的交通数据、信号控制数据、V2V消息等，支持历史数据查询和分析。

**技术挑战**：

- 大规模时序数据存储
- 高效的数据查询
- 数据压缩和归档
- 数据一致性保证

**解决方案**：
使用ITS_Schema定义数据存储结构，实现PostgreSQL数据存储系统。

### 9.2 实现代码

**完整的ITS数据存储实现**：

```python
from its_schema.transformation import ITSStorage
from datetime import datetime, timedelta

def case8_its_data_storage():
    """案例8：ITS数据存储系统"""

    # 1. 初始化存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "its_db",
        "user": "its_user",
        "password": "its_password"
    }

    storage = ITSStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 2. 存储传感器数据
    sensor_data = {
        "sensor_id": "SENSOR001",
        "timestamp": datetime.now().isoformat(),
        "vehicle_count": 150,
        "average_speed": 45.5,
        "occupancy": 75.2,
        "lane_id": 1
    }

    sensor_id = storage.store_sensor_data(sensor_data)
    print(f"Stored sensor data with ID: {sensor_id}")

    # 3. 查询交通数据
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now()

    traffic_records = storage.query_traffic_data("SENSOR001", start_time, end_time)
    print(f"Found {len(traffic_records)} traffic records")

    # 4. 数据统计分析
    if traffic_records:
        total_vehicles = sum(r['vehicle_count'] for r in traffic_records)
        avg_speed = sum(r['average_speed'] for r in traffic_records) / len(traffic_records)
        avg_occupancy = sum(r['occupancy'] for r in traffic_records) / len(traffic_records)

        print(f"\nStatistics:")
        print(f"  Total vehicles: {total_vehicles}")
        print(f"  Average speed: {avg_speed:.2f} km/h")
        print(f"  Average occupancy: {avg_occupancy:.2f}%")

    return {
        "sensor_id": sensor_id,
        "traffic_records": traffic_records
    }

# 运行案例
if __name__ == "__main__":
    result = case8_its_data_storage()
    print("Case 8 completed successfully")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

---

## 10. 案例9：智能信号优化系统

### 10.1 场景描述

**业务背景**：
智能信号优化系统基于实时交通流量数据，
动态调整交通信号灯配时，优化交通流，减少拥堵。

**技术挑战**：

- 需要实时交通流量监测
- 需要信号配时算法
- 需要多交叉口协调
- 需要效果评估

**解决方案**：
使用ITS_Schema收集交通流量数据，
使用AI算法优化信号配时，
使用ITSStorage存储优化结果。

### 10.2 Schema定义

**智能信号优化Schema**：

```dsl
schema IntelligentSignalOptimization {
  optimization_session_id: String @value("SIGNAL-OPT-20250121-001") @required
  intersection_id: String @value("INT-001") @required
  optimization_time: DateTime @value("2025-01-21T10:00:00") @required

  current_traffic: {
    phase_1_vehicle_count: Integer @value(50)
    phase_2_vehicle_count: Integer @value(80)
    phase_3_vehicle_count: Integer @value(60)
    phase_4_vehicle_count: Integer @value(40)
    average_waiting_time: Decimal @value(45.5) @unit("seconds")
  } @required

  current_signal_timing: {
    phase_1_duration: Integer @value(30) @unit("seconds")
    phase_2_duration: Integer @value(40) @unit("seconds")
    phase_3_duration: Integer @value(35) @unit("seconds")
    phase_4_duration: Integer @value(25) @unit("seconds")
    cycle_time: Integer @value(130) @unit("seconds")
  } @required

  optimized_timing: {
    phase_1_duration: Integer @value(35) @unit("seconds")
    phase_2_duration: Integer @value(45) @unit("seconds")
    phase_3_duration: Integer @value(40) @unit("seconds")
    phase_4_duration: Integer @value(30) @unit("seconds")
    cycle_time: Integer @value(150) @unit("seconds")
  } @required

  optimization_results: {
    expected_waiting_time_reduction: Decimal @value(0.15) @unit("15% reduction")
    expected_throughput_increase: Decimal @value(0.12) @unit("12% increase")
    optimization_score: Decimal @value(0.85) @range(0.0, 1.0)
  } @required
} @standard("ISO_14813")
```

### 10.3 实现代码

```python
from its_storage import ITSStorage
from datetime import datetime

def intelligent_signal_optimization():
    """智能信号优化示例"""
    storage = ITSStorage("postgresql://user:password@localhost/its_db")

    # 获取当前交通流量数据
    intersection_id = "INT-001"
    current_traffic = {
        "phase_1_vehicle_count": 50,
        "phase_2_vehicle_count": 80,
        "phase_3_vehicle_count": 60,
        "phase_4_vehicle_count": 40,
        "average_waiting_time": 45.5
    }

    # 当前信号配时
    current_timing = {
        "phase_1_duration": 30,
        "phase_2_duration": 40,
        "phase_3_duration": 35,
        "phase_4_duration": 25,
        "cycle_time": 130
    }

    # AI优化算法（简化示例）
    def optimize_signal_timing(traffic_data, current_timing):
        """优化信号配时"""
        total_vehicles = sum([
            traffic_data["phase_1_vehicle_count"],
            traffic_data["phase_2_vehicle_count"],
            traffic_data["phase_3_vehicle_count"],
            traffic_data["phase_4_vehicle_count"]
        ])

        # 根据车流量比例分配时间
        phase_1_ratio = traffic_data["phase_1_vehicle_count"] / total_vehicles
        phase_2_ratio = traffic_data["phase_2_vehicle_count"] / total_vehicles
        phase_3_ratio = traffic_data["phase_3_vehicle_count"] / total_vehicles
        phase_4_ratio = traffic_data["phase_4_vehicle_count"] / total_vehicles

        # 优化后的配时（总周期150秒）
        optimized_cycle = 150
        optimized_timing = {
            "phase_1_duration": int(optimized_cycle * phase_1_ratio),
            "phase_2_duration": int(optimized_cycle * phase_2_ratio),
            "phase_3_duration": int(optimized_cycle * phase_3_ratio),
            "phase_4_duration": int(optimized_cycle * phase_4_ratio),
            "cycle_time": optimized_cycle
        }

        return optimized_timing

    # 执行优化
    optimized_timing = optimize_signal_timing(current_traffic, current_timing)

    # 计算优化效果
    expected_waiting_time_reduction = 0.15  # 预计减少15%
    expected_throughput_increase = 0.12  # 预计增加12%
    optimization_score = 0.85

    # 存储优化结果
    optimization_data = {
        "optimization_session_id": "SIGNAL-OPT-20250121-001",
        "intersection_id": intersection_id,
        "optimization_time": datetime.now(),
        "current_traffic": current_traffic,
        "current_signal_timing": current_timing,
        "optimized_timing": optimized_timing,
        "expected_waiting_time_reduction": expected_waiting_time_reduction,
        "expected_throughput_increase": expected_throughput_increase,
        "optimization_score": optimization_score
    }

    # 存储到数据库
    optimization_id = storage.store_signal_control_data(optimization_data)
    print(f"Signal optimization stored: {optimization_id}")

    print(f"\nSignal Optimization Results:")
    print(f"  Intersection: {intersection_id}")
    print(f"  Current cycle time: {current_timing['cycle_time']}s")
    print(f"  Optimized cycle time: {optimized_timing['cycle_time']}s")
    print(f"  Expected waiting time reduction: {expected_waiting_time_reduction*100:.1f}%")
    print(f"  Expected throughput increase: {expected_throughput_increase*100:.1f}%")
    print(f"  Optimization score: {optimization_score:.2f}")

    return optimization_data

if __name__ == "__main__":
    intelligent_signal_optimization()
```

---

## 11. 案例10：交通预测系统

### 11.1 场景描述

**业务背景**：
交通预测系统基于历史交通数据和实时数据，
预测未来交通流量和拥堵情况，支持交通管理决策。

**技术挑战**：

- 需要历史数据分析
- 需要预测模型训练
- 需要实时数据融合
- 需要预测准确性评估

**解决方案**：
使用ITS_Schema收集历史交通数据，
使用机器学习模型进行交通预测，
使用ITSStorage存储预测结果。

### 11.2 Schema定义

**交通预测Schema**：

```dsl
schema TrafficPrediction {
  prediction_session_id: String @value("PRED-20250121-001") @required
  prediction_time: DateTime @value("2025-01-21T10:00:00") @required
  prediction_horizon: Integer @value(60) @unit("minutes")

  location: {
    intersection_id: String @value("INT-001")
    latitude: Decimal @value(31.2304)
    longitude: Decimal @value(121.4737)
  } @required

  historical_data: {
    time_window: {
      start: DateTime @value("2025-01-21T09:00:00")
      end: DateTime @value("2025-01-21T10:00:00")
    }
    average_vehicle_count: Integer @value(150)
    average_speed: Decimal @value(45.5)
    congestion_events: Integer @value(3)
  } @required

  predictions: [
    {
      prediction_time: DateTime @value("2025-01-21T11:00:00")
      predicted_vehicle_count: Integer @value(180)
      predicted_speed: Decimal @value(40.5)
      predicted_congestion_level: Enum { Medium } @value(Medium)
      confidence: Decimal @value(0.85) @range(0.0, 1.0)
    }
  ] @required

  prediction_accuracy: {
    model_name: String @value("LSTM")
    mae: Decimal @value(12.5) @unit("vehicles")
    rmse: Decimal @value(15.8) @unit("vehicles")
    accuracy: Decimal @value(0.88) @range(0.0, 1.0)
  } @required
} @standard("ISO_14813")
```

### 11.3 实现代码

```python
from its_storage import ITSStorage
from datetime import datetime, timedelta

def traffic_prediction_system():
    """交通预测系统示例"""
    storage = ITSStorage("postgresql://user:password@localhost/its_db")

    # 获取历史交通数据
    intersection_id = "INT-001"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    historical_data = storage.query_traffic_data(intersection_id, start_time, end_time)

    # 计算历史统计
    if historical_data:
        avg_vehicle_count = sum(d['vehicle_count'] for d in historical_data) / len(historical_data)
        avg_speed = sum(d['average_speed'] for d in historical_data) / len(historical_data)
        congestion_events = sum(1 for d in historical_data if d.get('congestion_level') == 'High')
    else:
        avg_vehicle_count = 150
        avg_speed = 45.5
        congestion_events = 3

    # 预测模型（简化示例）
    def predict_traffic(historical_avg, prediction_horizon_minutes):
        """预测交通流量"""
        # 简化预测：基于历史平均值和时间因子
        time_factor = 1.2 if prediction_horizon_minutes <= 30 else 1.5
        predicted_count = int(historical_avg * time_factor)
        predicted_speed = max(20.0, historical_avg * 0.9)

        congestion_level = "Low" if predicted_count < 100 else \
                          "Medium" if predicted_count < 200 else "High"

        return {
            "predicted_vehicle_count": predicted_count,
            "predicted_speed": predicted_speed,
            "predicted_congestion_level": congestion_level,
            "confidence": 0.85
        }

    # 生成预测
    prediction_horizon = 60  # 60分钟
    prediction_time = end_time + timedelta(minutes=prediction_horizon)

    prediction = predict_traffic(avg_vehicle_count, prediction_horizon)

    # 存储预测结果
    prediction_data = {
        "prediction_session_id": "PRED-20250121-001",
        "prediction_time": datetime.now(),
        "prediction_horizon": prediction_horizon,
        "intersection_id": intersection_id,
        "historical_avg_vehicle_count": avg_vehicle_count,
        "historical_avg_speed": avg_speed,
        "historical_congestion_events": congestion_events,
        "predicted_vehicle_count": prediction["predicted_vehicle_count"],
        "predicted_speed": prediction["predicted_speed"],
        "predicted_congestion_level": prediction["predicted_congestion_level"],
        "confidence": prediction["confidence"],
        "model_name": "LSTM",
        "mae": 12.5,
        "rmse": 15.8,
        "accuracy": 0.88
    }

    # 存储到数据库
    prediction_id = storage.store_traffic_data(prediction_data)
    print(f"Traffic prediction stored: {prediction_id}")

    print(f"\nTraffic Prediction Results:")
    print(f"  Intersection: {intersection_id}")
    print(f"  Prediction horizon: {prediction_horizon} minutes")
    print(f"  Historical avg vehicle count: {avg_vehicle_count:.0f}")
    print(f"  Predicted vehicle count: {prediction['predicted_vehicle_count']}")
    print(f"  Predicted speed: {prediction['predicted_speed']:.1f} km/h")
    print(f"  Predicted congestion level: {prediction['predicted_congestion_level']}")
    print(f"  Confidence: {prediction['confidence']:.2f}")
    print(f"  Model accuracy: 0.88")

    return prediction_data

if __name__ == "__main__":
    traffic_prediction_system()
```

---

## 12. 案例11：事故预防系统

### 12.1 场景描述

**业务背景**：
事故预防系统通过分析交通数据、天气数据、历史事故数据，
识别事故风险点，提前预警，减少交通事故发生。

**技术挑战**：

- 需要多源数据融合
- 需要风险识别算法
- 需要实时预警
- 需要效果评估

**解决方案**：
使用ITS_Schema整合交通、天气、事故数据，
使用AI模型识别事故风险，
使用ITSStorage存储预警信息。

### 12.2 Schema定义

**事故预防Schema**：

```dsl
schema AccidentPrevention {
  prevention_session_id: String @value("PREVENT-20250121-001") @required
  analysis_time: DateTime @value("2025-01-21T10:00:00") @required

  location: {
    intersection_id: String @value("INT-001")
    latitude: Decimal @value(31.2304)
    longitude: Decimal @value(121.4737)
  } @required

  risk_factors: {
    traffic_volume: Integer @value(200)
    average_speed: Decimal @value(55.5)
    speed_variance: Decimal @value(15.2)
    weather_condition: Enum { Rainy } @value(Rainy)
    visibility: Decimal @value(500.0) @unit("meters")
    road_condition: Enum { Wet } @value(Wet)
    historical_accidents: Integer @value(5) @unit("last 30 days")
  } @required

  risk_assessment: {
    risk_level: Enum { High } @value(High)
    risk_score: Decimal @value(0.75) @range(0.0, 1.0)
    risk_factors_count: Integer @value(4)
    primary_risk_factor: String @value("High speed variance + Rainy weather")
  } @required

  prevention_actions: [
    {
      action_type: String @value("SpeedLimit")
      action_description: String @value("降低限速至40km/h")
      expected_risk_reduction: Decimal @value(0.30)
    },
    {
      action_type: String @value("WarningSign")
      action_description: String @value("显示雨天减速警告")
      expected_risk_reduction: Decimal @value(0.15)
    }
  ] @required

  alert: {
    alert_level: Enum { High } @value(High)
    alert_message: String @value("高风险路段，请减速慢行")
    alert_sent: Boolean @value(true)
    alert_time: DateTime @value("2025-01-21T10:05:00")
  } @required
} @standard("ISO_14813")
```

### 12.3 实现代码

```python
from its_storage import ITSStorage
from datetime import datetime

def accident_prevention_system():
    """事故预防系统示例"""
    storage = ITSStorage("postgresql://user:password@localhost/its_db")

    # 获取交通数据
    intersection_id = "INT-001"
    traffic_data = {
        "traffic_volume": 200,
        "average_speed": 55.5,
        "speed_variance": 15.2
    }

    # 获取天气数据
    weather_data = {
        "weather_condition": "Rainy",
        "visibility": 500.0,
        "road_condition": "Wet"
    }

    # 获取历史事故数据
    historical_accidents = 5  # 过去30天

    # 风险识别算法
    def assess_accident_risk(traffic_data, weather_data, historical_accidents):
        """评估事故风险"""
        risk_score = 0.0
        risk_factors = []

        # 交通流量风险
        if traffic_data["traffic_volume"] > 150:
            risk_score += 0.15
            risk_factors.append("High traffic volume")

        # 速度风险
        if traffic_data["average_speed"] > 50:
            risk_score += 0.20
            risk_factors.append("High average speed")

        # 速度方差风险
        if traffic_data["speed_variance"] > 10:
            risk_score += 0.25
            risk_factors.append("High speed variance")

        # 天气风险
        if weather_data["weather_condition"] == "Rainy":
            risk_score += 0.20
            risk_factors.append("Rainy weather")

        if weather_data["visibility"] < 1000:
            risk_score += 0.10
            risk_factors.append("Low visibility")

        # 历史事故风险
        if historical_accidents > 3:
            risk_score += 0.10
            risk_factors.append("High historical accident rate")

        # 确定风险等级
        if risk_score >= 0.7:
            risk_level = "High"
        elif risk_score >= 0.5:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "primary_risk_factor": " + ".join(risk_factors[:2])
        }

    # 执行风险评估
    risk_assessment = assess_accident_risk(traffic_data, weather_data, historical_accidents)

    # 生成预防措施
    prevention_actions = []
    if risk_assessment["risk_level"] == "High":
        prevention_actions = [
            {
                "action_type": "SpeedLimit",
                "action_description": "降低限速至40km/h",
                "expected_risk_reduction": 0.30
            },
            {
                "action_type": "WarningSign",
                "action_description": "显示雨天减速警告",
                "expected_risk_reduction": 0.15
            }
        ]

    # 发送预警
    alert_level = risk_assessment["risk_level"]
    alert_message = f"高风险路段，请减速慢行" if alert_level == "High" else \
                   f"中等风险路段，请注意安全" if alert_level == "Medium" else \
                   f"低风险路段，正常行驶"

    # 存储预防数据
    prevention_data = {
        "prevention_session_id": "PREVENT-20250121-001",
        "analysis_time": datetime.now(),
        "intersection_id": intersection_id,
        "traffic_volume": traffic_data["traffic_volume"],
        "average_speed": traffic_data["average_speed"],
        "speed_variance": traffic_data["speed_variance"],
        "weather_condition": weather_data["weather_condition"],
        "visibility": weather_data["visibility"],
        "road_condition": weather_data["road_condition"],
        "historical_accidents": historical_accidents,
        "risk_level": risk_assessment["risk_level"],
        "risk_score": risk_assessment["risk_score"],
        "risk_factors_count": len(risk_assessment["risk_factors"]),
        "primary_risk_factor": risk_assessment["primary_risk_factor"],
        "prevention_actions": prevention_actions,
        "alert_level": alert_level,
        "alert_message": alert_message,
        "alert_sent": True,
        "alert_time": datetime.now()
    }

    # 存储到数据库
    prevention_id = storage.store_traffic_data(prevention_data)
    print(f"Accident prevention data stored: {prevention_id}")

    print(f"\nAccident Prevention Analysis:")
    print(f"  Intersection: {intersection_id}")
    print(f"  Risk level: {risk_assessment['risk_level']}")
    print(f"  Risk score: {risk_assessment['risk_score']:.2f}")
    print(f"  Risk factors: {len(risk_assessment['risk_factors'])}")
    print(f"  Primary risk: {risk_assessment['primary_risk_factor']}")
    print(f"  Alert: {alert_message}")
    print(f"  Prevention actions: {len(prevention_actions)}")

    return prevention_data

if __name__ == "__main__":
    accident_prevention_system()
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
