# 智能交通系统Schema转换体系

## 📑 目录

- [智能交通系统Schema转换体系](#智能交通系统schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 交通数据采集和转换](#2-交通数据采集和转换)
    - [2.1 传感器数据采集器](#21-传感器数据采集器)
    - [2.2 视频数据处理器](#22-视频数据处理器)
    - [2.3 GPS数据处理](#23-gps数据处理)
  - [3. 交通信号控制实现](#3-交通信号控制实现)
    - [3.1 信号控制器](#31-信号控制器)
    - [3.2 配时优化算法](#32-配时优化算法)
  - [4. 车辆通信实现](#4-车辆通信实现)
    - [4.1 V2V消息处理器](#41-v2v消息处理器)
  - [5. 路况分析实现](#5-路况分析实现)
    - [5.1 交通流量分析器](#51-交通流量分析器)
    - [5.2 拥堵检测器](#52-拥堵检测器)
  - [6. ITS数据存储与分析](#6-its数据存储与分析)
    - [6.1 PostgreSQL ITS数据存储](#61-postgresql-its数据存储)

---

## 1. 转换体系概述

ITS Schema转换体系支持交通数据采集、交通信号控制、
车辆通信、路况分析、数据库存储之间的转换。

### 1.1 转换目标

1. **交通数据采集**：从传感器、视频、GPS采集数据
2. **数据格式转换**：设备数据格式到标准Schema格式
3. **交通信号控制**：信号灯控制和配时优化
4. **车辆通信**：V2V、V2I、V2X消息处理
5. **路况分析**：交通流量分析、拥堵检测、路径规划
6. **数据到数据库转换**：ITS数据到PostgreSQL存储

---

## 2. 交通数据采集和转换

### 2.1 传感器数据采集器

**完整的传感器数据采集实现**：

```python
import logging
import socket
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TrafficSensorDataCollector:
    """交通传感器数据采集器 - 增强错误处理"""

    def __init__(self, sensor_id: str, host: str, port: int = 502):
        # 输入验证
        if not sensor_id:
            raise ValueError("Sensor ID cannot be empty")

        if not isinstance(sensor_id, str):
            raise TypeError(f"Sensor ID must be a string, got {type(sensor_id)}")

        if not host:
            raise ValueError("Host cannot be empty")

        if not isinstance(host, str):
            raise TypeError(f"Host must be a string, got {type(host)}")

        if not isinstance(port, int):
            raise TypeError(f"Port must be an integer, got {type(port)}")

        if not (1 <= port <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {port}")

        self.sensor_id = sensor_id
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self, timeout: float = 10.0) -> bool:
        """连接到传感器 - 增强错误处理"""
        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")

        if timeout > 300:
            raise ValueError(f"Timeout too large: {timeout} seconds (max 300)")

        # 如果已连接，先断开
        if self.connected and self.socket:
            try:
                self.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting existing connection: {e}")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)

            self.socket.connect((self.host, self.port))
            self.connected = True

            logger.info(f"Connected to traffic sensor {self.sensor_id} at {self.host}:{self.port}")
            return True

        except socket.timeout:
            logger.error(f"Connection timeout to sensor {self.sensor_id}")
            self._cleanup_socket()
            raise TimeoutError(f"Connection timeout to sensor {self.sensor_id}") from None
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for sensor {self.sensor_id} host {self.host}: {e}")
            self._cleanup_socket()
            raise ConnectionError(f"Cannot resolve hostname {self.host}: {e}") from e
        except socket.error as e:
            logger.error(f"Socket error connecting to sensor {self.sensor_id}: {e}")
            self._cleanup_socket()
            raise ConnectionError(f"Cannot connect to sensor {self.sensor_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error connecting to sensor {self.sensor_id}: {e}", exc_info=True)
            self._cleanup_socket()
            raise RuntimeError(f"Failed to connect to sensor {self.sensor_id}: {e}") from e

    def _cleanup_socket(self):
        """清理socket资源"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None
                self.connected = False

    def disconnect(self):
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
                logger.info(f"Disconnected from sensor {self.sensor_id}")
            except Exception as e:
                logger.warning(f"Error closing socket: {e}")
            finally:
                self.socket = None
                self.connected = False

    def read_traffic_data(self) -> Optional[Dict]:
        """读取交通数据 - 增强错误处理"""
        if not self.connected:
            raise ConnectionError(f"Not connected to sensor {self.sensor_id}. Call connect() first.")

        if self.socket is None:
            raise ConnectionError("Socket is not initialized")

        try:
            # 模拟读取交通数据（实际实现需要根据传感器协议）
            # 这里使用Modbus协议示例
            traffic_data = {
                "sensor_id": self.sensor_id,
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": self._read_register(0x1000),  # 车辆计数
                "average_speed": self._read_register(0x1001) / 10.0,  # 平均速度（km/h）
                "occupancy": self._read_register(0x1002) / 100.0,  # 占有率（%）
                "lane_id": self._read_register(0x1003)  # 车道ID
            }

            # 数据验证
            if traffic_data["vehicle_count"] < 0:
                raise ValueError(f"Invalid vehicle count: {traffic_data['vehicle_count']}")

            if not (0 <= traffic_data["average_speed"] <= 200):
                raise ValueError(f"Average speed out of range: {traffic_data['average_speed']}")

            if not (0 <= traffic_data["occupancy"] <= 100):
                raise ValueError(f"Occupancy out of range: {traffic_data['occupancy']}")

            return traffic_data

        except socket.timeout:
            logger.error(f"Timeout reading data from sensor {self.sensor_id}")
            raise TimeoutError(f"Timeout reading data from sensor {self.sensor_id}") from None
        except socket.error as e:
            logger.error(f"Socket error reading data from sensor {self.sensor_id}: {e}")
            self.connected = False
            raise ConnectionError(f"Socket error: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid data from sensor {self.sensor_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading data from sensor {self.sensor_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to read traffic data: {e}") from e

    def _read_register(self, address: int) -> int:
        """读取Modbus寄存器（模拟实现）"""
        # 实际实现需要根据Modbus协议
        # 这里返回模拟数据
        import random
        if address == 0x1000:
            return random.randint(0, 100)  # 车辆计数
        elif address == 0x1001:
            return random.randint(300, 1200)  # 速度（0.1 km/h单位）
        elif address == 0x1002:
            return random.randint(0, 10000)  # 占有率（0.01%单位）
        elif address == 0x1003:
            return random.randint(1, 4)  # 车道ID
        return 0
```

### 2.2 视频数据处理器

**完整的视频数据处理实现**：

```python
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoTrafficDataProcessor:
    """视频交通数据处理器 - 增强错误处理"""

    def __init__(self, camera_id: str):
        if not camera_id:
            raise ValueError("Camera ID cannot be empty")

        if not isinstance(camera_id, str):
            raise TypeError(f"Camera ID must be a string, got {type(camera_id)}")

        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.vehicle_detector = None  # 车辆检测器（YOLO、SSD等）

    def connect_camera(self, camera_url: str, timeout: int = 10) -> bool:
        """连接摄像头 - 增强错误处理"""
        if not camera_url:
            raise ValueError("Camera URL cannot be empty")

        if not isinstance(camera_url, str):
            raise TypeError(f"Camera URL must be a string, got {type(camera_url)}")

        if not isinstance(timeout, int):
            raise TypeError(f"Timeout must be an integer, got {type(timeout)}")

        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")

        try:
            self.cap = cv2.VideoCapture(camera_url)

            if not self.cap.isOpened():
                raise ConnectionError(f"Failed to open camera {self.camera_id} at {camera_url}")

            # 设置超时
            self.cap.set(cv2.CAP_PROP_TIMEOUT, timeout * 1000)

            logger.info(f"Connected to camera {self.camera_id} at {camera_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to camera {self.camera_id}: {e}", exc_info=True)
            self._cleanup_camera()
            raise ConnectionError(f"Failed to connect to camera {self.camera_id}: {e}") from e

    def _cleanup_camera(self):
        """清理摄像头资源"""
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            finally:
                self.cap = None

    def process_frame(self) -> Optional[Dict]:
        """处理视频帧 - 增强错误处理"""
        if self.cap is None:
            raise ConnectionError(f"Camera {self.camera_id} not connected. Call connect_camera() first.")

        try:
            ret, frame = self.cap.read()

            if not ret:
                logger.warning(f"Failed to read frame from camera {self.camera_id}")
                return None

            if frame is None:
                raise ValueError("Frame is None")

            # 车辆检测
            vehicles = self._detect_vehicles(frame)

            # 车牌识别（可选）
            license_plates = self._recognize_license_plates(frame, vehicles)

            traffic_data = {
                "camera_id": self.camera_id,
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": len(vehicles),
                "vehicles": vehicles,
                "license_plates": license_plates,
                "frame_width": frame.shape[1],
                "frame_height": frame.shape[0]
            }

            return traffic_data

        except ValueError as e:
            logger.error(f"Invalid frame data from camera {self.camera_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing frame from camera {self.camera_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process frame: {e}") from e

    def _detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        """检测车辆（模拟实现）"""
        # 实际实现需要使用YOLO、SSD等目标检测模型
        # 这里返回模拟数据
        vehicles = []
        # 模拟检测结果
        for i in range(3):
            vehicles.append({
                "vehicle_id": f"VEH{i+1}",
                "bbox": [100 + i*50, 100 + i*30, 200 + i*50, 200 + i*30],  # [x1, y1, x2, y2]
                "confidence": 0.85 + i * 0.05,
                "vehicle_type": ["car", "truck", "bus"][i % 3]
            })
        return vehicles

    def _recognize_license_plates(self, frame: np.ndarray, vehicles: List[Dict]) -> List[Dict]:
        """识别车牌（模拟实现）"""
        # 实际实现需要使用OCR或车牌识别模型
        license_plates = []
        for vehicle in vehicles:
            license_plates.append({
                "vehicle_id": vehicle["vehicle_id"],
                "plate_number": f"京A{1000 + hash(vehicle['vehicle_id']) % 9000}",
                "confidence": 0.90
            })
        return license_plates
```

### 2.3 GPS数据处理

**GPS数据处理实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GPSDataProcessor:
    """GPS数据处理器 - 增强错误处理"""

    def __init__(self):
        pass

    def parse_nmea_message(self, nmea_message: str) -> Optional[Dict]:
        """解析NMEA消息 - 增强错误处理"""
        if not nmea_message:
            raise ValueError("NMEA message cannot be empty")

        if not isinstance(nmea_message, str):
            raise TypeError(f"NMEA message must be a string, got {type(nmea_message)}")

        if not nmea_message.startswith('$'):
            raise ValueError(f"Invalid NMEA message format: {nmea_message[:20]}")

        try:
            # 解析NMEA消息
            parts = nmea_message.strip().split(',')

            if len(parts) < 2:
                raise ValueError(f"Insufficient NMEA message parts: {len(parts)}")

            message_type = parts[0]

            if message_type == '$GPGGA':
                return self._parse_gga(parts)
            elif message_type == '$GPRMC':
                return self._parse_rmc(parts)
            else:
                logger.warning(f"Unsupported NMEA message type: {message_type}")
                return None

        except ValueError as e:
            logger.error(f"Invalid NMEA message format: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing NMEA message: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse NMEA message: {e}") from e

    def _parse_gga(self, parts: List[str]) -> Dict:
        """解析GPGGA消息"""
        if len(parts) < 15:
            raise ValueError(f"Insufficient GPGGA message parts: {len(parts)}")

        latitude = self._parse_latitude(parts[2], parts[3])
        longitude = self._parse_longitude(parts[4], parts[5])

        return {
            "message_type": "GPGGA",
            "timestamp": self._parse_time(parts[1]),
            "latitude": latitude,
            "longitude": longitude,
            "altitude": float(parts[9]) if parts[9] else None,
            "satellites": int(parts[7]) if parts[7] else 0,
            "quality": int(parts[6]) if parts[6] else 0
        }

    def _parse_rmc(self, parts: List[str]) -> Dict:
        """解析GPRMC消息"""
        if len(parts) < 12:
            raise ValueError(f"Insufficient GPRMC message parts: {len(parts)}")

        latitude = self._parse_latitude(parts[3], parts[4])
        longitude = self._parse_longitude(parts[5], parts[6])

        return {
            "message_type": "GPRMC",
            "timestamp": self._parse_datetime(parts[1], parts[9]),
            "latitude": latitude,
            "longitude": longitude,
            "speed": float(parts[7]) if parts[7] else 0.0,  # 节
            "course": float(parts[8]) if parts[8] else 0.0,  # 度
            "status": parts[2]  # A=有效，V=无效
        }

    def _parse_latitude(self, lat_str: str, lat_dir: str) -> float:
        """解析纬度"""
        if not lat_str or not lat_dir:
            raise ValueError("Latitude string or direction cannot be empty")

        degrees = float(lat_str[:2])
        minutes = float(lat_str[2:])
        latitude = degrees + minutes / 60.0

        if lat_dir == 'S':
            latitude = -latitude

        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude out of range: {latitude}")

        return latitude

    def _parse_longitude(self, lon_str: str, lon_dir: str) -> float:
        """解析经度"""
        if not lon_str or not lon_dir:
            raise ValueError("Longitude string or direction cannot be empty")

        degrees = float(lon_str[:3])
        minutes = float(lon_str[3:])
        longitude = degrees + minutes / 60.0

        if lon_dir == 'W':
            longitude = -longitude

        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude out of range: {longitude}")

        return longitude

    def _parse_time(self, time_str: str) -> str:
        """解析时间字符串"""
        if not time_str or len(time_str) < 6:
            raise ValueError(f"Invalid time string: {time_str}")

        hour = int(time_str[0:2])
        minute = int(time_str[2:4])
        second = int(time_str[4:6])

        if not (0 <= hour < 24):
            raise ValueError(f"Hour out of range: {hour}")
        if not (0 <= minute < 60):
            raise ValueError(f"Minute out of range: {minute}")
        if not (0 <= second < 60):
            raise ValueError(f"Second out of range: {second}")

        return f"{hour:02d}:{minute:02d}:{second:02d}"

    def _parse_datetime(self, time_str: str, date_str: str) -> str:
        """解析日期时间字符串"""
        time_part = self._parse_time(time_str)

        if not date_str or len(date_str) < 6:
            raise ValueError(f"Invalid date string: {date_str}")

        day = int(date_str[0:2])
        month = int(date_str[2:4])
        year = 2000 + int(date_str[4:6])

        return f"{year}-{month:02d}-{day:02d}T{time_part}"
```

---

## 3. 交通信号控制实现

### 3.1 信号控制器

**完整的信号控制器实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class SignalState(Enum):
    """信号灯状态"""
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    RED_YELLOW = "RedYellow"  # 某些国家的过渡状态

class TrafficSignalController:
    """交通信号控制器 - 增强错误处理"""

    def __init__(self, intersection_id: str):
        if not intersection_id:
            raise ValueError("Intersection ID cannot be empty")

        if not isinstance(intersection_id, str):
            raise TypeError(f"Intersection ID must be a string, got {type(intersection_id)}")

        self.intersection_id = intersection_id
        self.phases: List[Dict] = []
        self.current_phase = 0
        self.cycle_time = 120  # 默认周期120秒
        self.start_time: Optional[datetime] = None

    def set_phases(self, phases: List[Dict]) -> bool:
        """设置相位序列 - 增强错误处理"""
        if not isinstance(phases, list):
            raise TypeError(f"Phases must be a list, got {type(phases)}")

        if not phases:
            raise ValueError("Phases list cannot be empty")

        if len(phases) > 20:  # 防止异常大的相位列表
            raise ValueError(f"Too many phases: {len(phases)} (max 20)")

        try:
            # 验证相位格式
            for idx, phase in enumerate(phases):
                if not isinstance(phase, dict):
                    raise TypeError(f"Phase {idx} must be a dictionary, got {type(phase)}")

                required_fields = ["phase_id", "duration", "signals"]
                missing_fields = [f for f in required_fields if f not in phase]
                if missing_fields:
                    raise ValueError(f"Phase {idx} missing required fields: {', '.join(missing_fields)}")

                duration = phase.get("duration")
                if not isinstance(duration, (int, float)) or duration <= 0:
                    raise ValueError(f"Phase {idx} invalid duration: {duration}")

                if duration > 300:  # 最大5分钟
                    raise ValueError(f"Phase {idx} duration too long: {duration} seconds (max 300)")

            self.phases = phases
            logger.info(f"Set {len(phases)} phases for intersection {self.intersection_id}")
            return True

        except (ValueError, TypeError) as e:
            logger.error(f"Phase setting validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error setting phases: {e}", exc_info=True)
            raise RuntimeError(f"Failed to set phases: {e}") from e

    def set_cycle_time(self, cycle_time: int):
        """设置周期时间 - 增强错误处理"""
        if not isinstance(cycle_time, int):
            raise TypeError(f"Cycle time must be an integer, got {type(cycle_time)}")

        if cycle_time <= 0:
            raise ValueError(f"Cycle time must be positive, got {cycle_time}")

        if cycle_time > 600:  # 最大10分钟
            raise ValueError(f"Cycle time too long: {cycle_time} seconds (max 600)")

        self.cycle_time = cycle_time
        logger.info(f"Set cycle time to {cycle_time} seconds for intersection {self.intersection_id}")

    def start_cycle(self):
        """启动信号周期"""
        if not self.phases:
            raise ValueError("No phases set. Call set_phases() first.")

        self.start_time = datetime.now()
        self.current_phase = 0
        logger.info(f"Started signal cycle for intersection {self.intersection_id}")

    def get_current_signal_state(self) -> Optional[Dict]:
        """获取当前信号状态"""
        if not self.phases:
            return None

        if self.start_time is None:
            return None

        elapsed = (datetime.now() - self.start_time).total_seconds()
        phase_duration = 0

        for i, phase in enumerate(self.phases):
            phase_duration += phase["duration"]
            if elapsed < phase_duration:
                return {
                    "intersection_id": self.intersection_id,
                    "current_phase": i,
                    "phase_id": phase["phase_id"],
                    "signals": phase["signals"],
                    "elapsed_time": elapsed,
                    "remaining_time": phase_duration - elapsed
                }

        # 周期结束，重新开始
        self.start_cycle()
        return self.get_current_signal_state()
```

### 3.2 配时优化算法

**配时优化算法实现**：

```python
import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)

class SignalTimingOptimizer:
    """信号配时优化器 - 增强错误处理"""

    def __init__(self):
        pass

    def optimize_cycle_time(self, traffic_flows: Dict[str, float],
                           saturation_flows: Dict[str, float] = None) -> int:
        """优化周期时间 - Webster方法"""
        if not isinstance(traffic_flows, dict):
            raise TypeError(f"Traffic flows must be a dictionary, got {type(traffic_flows)}")

        if not traffic_flows:
            raise ValueError("Traffic flows cannot be empty")

        if saturation_flows is None:
            saturation_flows = {lane: 1800.0 for lane in traffic_flows.keys()}  # 默认1800 veh/h

        try:
            # 计算各车道的流量比
            flow_ratios = {}
            for lane, flow in traffic_flows.items():
                if not isinstance(flow, (int, float)) or flow < 0:
                    raise ValueError(f"Invalid traffic flow for lane {lane}: {flow}")

                sat_flow = saturation_flows.get(lane, 1800.0)
                if sat_flow <= 0:
                    raise ValueError(f"Invalid saturation flow for lane {lane}: {sat_flow}")

                flow_ratios[lane] = flow / sat_flow

            # 找到最大流量比
            max_flow_ratio = max(flow_ratios.values())

            if max_flow_ratio >= 1.0:
                logger.warning(f"Traffic flow exceeds saturation flow (ratio: {max_flow_ratio})")
                return 180  # 返回最大周期时间

            # Webster公式：C = (1.5L + 5) / (1 - Y)
            # 其中L是总损失时间，Y是最大流量比
            L = len(traffic_flows) * 4  # 假设每个相位损失时间4秒
            Y = max_flow_ratio

            cycle_time = int((1.5 * L + 5) / (1 - Y))

            # 限制周期时间范围（60-180秒）
            cycle_time = max(60, min(180, cycle_time))

            logger.info(f"Optimized cycle time: {cycle_time} seconds (max flow ratio: {Y:.2f})")
            return cycle_time

        except (ValueError, TypeError) as e:
            logger.error(f"Cycle time optimization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error optimizing cycle time: {e}", exc_info=True)
            raise RuntimeError(f"Failed to optimize cycle time: {e}") from e

    def optimize_green_time(self, traffic_flow: float, cycle_time: int,
                           saturation_flow: float = 1800.0) -> int:
        """优化绿灯时间"""
        if not isinstance(traffic_flow, (int, float)) or traffic_flow < 0:
            raise ValueError(f"Invalid traffic flow: {traffic_flow}")

        if not isinstance(cycle_time, int) or cycle_time <= 0:
            raise ValueError(f"Invalid cycle time: {cycle_time}")

        if not isinstance(saturation_flow, (int, float)) or saturation_flow <= 0:
            raise ValueError(f"Invalid saturation flow: {saturation_flow}")

        try:
            # 计算流量比
            flow_ratio = traffic_flow / saturation_flow

            if flow_ratio >= 1.0:
                logger.warning(f"Traffic flow exceeds saturation flow")
                return cycle_time - 20  # 返回最大绿灯时间（减去损失时间）

            # 计算绿灯时间
            green_time = int(flow_ratio * cycle_time)

            # 限制绿灯时间范围（最小10秒，最大cycle_time-20秒）
            green_time = max(10, min(cycle_time - 20, green_time))

            return green_time

        except ValueError as e:
            logger.error(f"Green time optimization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error optimizing green time: {e}", exc_info=True)
            raise RuntimeError(f"Failed to optimize green time: {e}") from e
```

---

## 4. 车辆通信实现

### 4.1 V2V消息处理器

**V2V消息处理器实现**：

```python
import logging
import struct
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class V2VMessageProcessor:
    """V2V消息处理器 - 增强错误处理"""

    def __init__(self):
        pass

    def parse_bsm_message(self, bsm_data: bytes) -> Optional[Dict]:
        """解析BSM（基本安全消息） - SAE J2735标准"""
        if not isinstance(bsm_data, bytes):
            raise TypeError(f"BSM data must be bytes, got {type(bsm_data)}")

        if not bsm_data:
            raise ValueError("BSM data cannot be empty")

        if len(bsm_data) < 20:  # BSM最小长度
            raise ValueError(f"BSM data too short: {len(bsm_data)} bytes (minimum 20)")

        try:
            # 解析BSM消息（简化实现）
            # 实际实现需要根据SAE J2735标准完整解析
            offset = 0

            # 消息ID（2字节）
            message_id = struct.unpack('>H', bsm_data[offset:offset+2])[0]
            offset += 2

            if message_id != 0x0014:  # BSM消息ID
                raise ValueError(f"Invalid BSM message ID: {message_id}")

            # 车辆ID（4字节）
            vehicle_id = struct.unpack('>I', bsm_data[offset:offset+4])[0]
            offset += 4

            # 位置信息（纬度、经度各4字节）
            latitude = struct.unpack('>i', bsm_data[offset:offset+4])[0] / 10000000.0
            offset += 4
            longitude = struct.unpack('>i', bsm_data[offset:offset+4])[0] / 10000000.0
            offset += 4

            # 速度（2字节，0.02 m/s单位）
            speed = struct.unpack('>H', bsm_data[offset:offset+2])[0] * 0.02
            offset += 2

            # 航向（2字节，0.0125度单位）
            heading = struct.unpack('>H', bsm_data[offset:offset+2])[0] * 0.0125
            offset += 2

            # 数据验证
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Latitude out of range: {latitude}")

            if not (-180 <= longitude <= 180):
                raise ValueError(f"Longitude out of range: {longitude}")

            if not (0 <= speed <= 200):
                raise ValueError(f"Speed out of range: {speed} m/s")

            if not (0 <= heading < 360):
                raise ValueError(f"Heading out of range: {heading} degrees")

            bsm_message = {
                "message_type": "BSM",
                "vehicle_id": vehicle_id,
                "timestamp": datetime.now().isoformat(),
                "position": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "speed": speed,  # m/s
                "heading": heading,  # 度
                "message_size": len(bsm_data)
            }

            return bsm_message

        except struct.error as e:
            logger.error(f"BSM message parsing error: {e}")
            raise ValueError(f"Invalid BSM message format: {e}") from e
        except ValueError as e:
            logger.error(f"BSM message validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing BSM message: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse BSM message: {e}") from e

    def build_bsm_message(self, vehicle_data: Dict) -> bytes:
        """构建BSM消息"""
        if not isinstance(vehicle_data, dict):
            raise TypeError(f"Vehicle data must be a dictionary, got {type(vehicle_data)}")

        required_fields = ["vehicle_id", "latitude", "longitude", "speed", "heading"]
        missing_fields = [f for f in required_fields if f not in vehicle_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            # 构建BSM消息
            message = bytearray()

            # 消息ID（BSM = 0x0014）
            message.extend(struct.pack('>H', 0x0014))

            # 车辆ID
            vehicle_id = vehicle_data["vehicle_id"]
            if not isinstance(vehicle_id, int) or vehicle_id < 0:
                raise ValueError(f"Invalid vehicle ID: {vehicle_id}")
            message.extend(struct.pack('>I', vehicle_id))

            # 位置信息
            latitude = vehicle_data["latitude"]
            longitude = vehicle_data["longitude"]

            if not (-90 <= latitude <= 90):
                raise ValueError(f"Latitude out of range: {latitude}")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Longitude out of range: {longitude}")

            message.extend(struct.pack('>i', int(latitude * 10000000)))
            message.extend(struct.pack('>i', int(longitude * 10000000)))

            # 速度（0.02 m/s单位）
            speed = vehicle_data["speed"]
            if not isinstance(speed, (int, float)) or speed < 0:
                raise ValueError(f"Invalid speed: {speed}")
            if speed > 200:
                raise ValueError(f"Speed too high: {speed} m/s (max 200)")
            message.extend(struct.pack('>H', int(speed / 0.02)))

            # 航向（0.0125度单位）
            heading = vehicle_data["heading"]
            if not isinstance(heading, (int, float)) or heading < 0:
                raise ValueError(f"Invalid heading: {heading}")
            if heading >= 360:
                raise ValueError(f"Heading out of range: {heading} degrees (must be 0-360)")
            message.extend(struct.pack('>H', int(heading / 0.0125)))

            return bytes(message)

        except (ValueError, TypeError) as e:
            logger.error(f"BSM message building error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building BSM message: {e}", exc_info=True)
            raise RuntimeError(f"Failed to build BSM message: {e}") from e
```

---

## 5. 路况分析实现

### 5.1 交通流量分析器

**交通流量分析器实现**：

```python
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class TrafficFlowAnalyzer:
    """交通流量分析器 - 增强错误处理"""

    def __init__(self):
        pass

    def analyze_flow_pattern(self, traffic_data_list: List[Dict],
                           time_window_minutes: int = 15) -> Dict:
        """分析交通流量模式"""
        if not isinstance(traffic_data_list, list):
            raise TypeError(f"Traffic data list must be a list, got {type(traffic_data_list)}")

        if not traffic_data_list:
            raise ValueError("Traffic data list cannot be empty")

        if not isinstance(time_window_minutes, int):
            raise TypeError(f"Time window must be an integer, got {type(time_window_minutes)}")

        if time_window_minutes <= 0:
            raise ValueError(f"Time window must be positive, got {time_window_minutes}")

        if time_window_minutes > 1440:  # 最大24小时
            raise ValueError(f"Time window too large: {time_window_minutes} minutes (max 1440)")

        try:
            # 按时间窗口分组
            window = timedelta(minutes=time_window_minutes)
            window_groups = defaultdict(list)

            for data in traffic_data_list:
                if not isinstance(data, dict):
                    raise TypeError(f"Traffic data must be a dictionary, got {type(data)}")

                timestamp_str = data.get("timestamp")
                if not timestamp_str:
                    raise ValueError("Traffic data missing timestamp")

                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                window_start = timestamp.replace(minute=0, second=0, microsecond=0)

                # 计算窗口索引
                window_index = int((timestamp - window_start).total_seconds() / window.total_seconds())
                window_key = window_start + timedelta(minutes=window_index * time_window_minutes)

                window_groups[window_key].append(data)

            # 分析每个窗口
            analysis_results = []
            for window_time, data_points in sorted(window_groups.items()):
                vehicle_counts = [d.get("vehicle_count", 0) for d in data_points]
                speeds = [d.get("average_speed", 0) for d in data_points if d.get("average_speed", 0) > 0]

                if vehicle_counts:
                    analysis_results.append({
                        "window_start": window_time.isoformat(),
                        "vehicle_count_avg": statistics.mean(vehicle_counts),
                        "vehicle_count_max": max(vehicle_counts),
                        "vehicle_count_min": min(vehicle_counts),
                        "speed_avg": statistics.mean(speeds) if speeds else 0,
                        "speed_max": max(speeds) if speeds else 0,
                        "speed_min": min(speeds) if speeds else 0,
                        "data_points": len(data_points)
                    })

            return {
                "analysis_type": "flow_pattern",
                "time_window_minutes": time_window_minutes,
                "total_data_points": len(traffic_data_list),
                "windows": analysis_results
            }

        except (ValueError, TypeError) as e:
            logger.error(f"Flow pattern analysis error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error analyzing flow pattern: {e}", exc_info=True)
            raise RuntimeError(f"Failed to analyze flow pattern: {e}") from e
```

### 5.2 拥堵检测器

**拥堵检测器实现**：

```python
class CongestionDetector:
    """拥堵检测器 - 增强错误处理"""

    def __init__(self):
        # 拥堵阈值配置
        self.speed_threshold = 20.0  # km/h，低于此速度视为拥堵
        self.occupancy_threshold = 80.0  # %，高于此占有率视为拥堵

    def detect_congestion(self, traffic_data: Dict) -> Dict:
        """检测拥堵"""
        if not isinstance(traffic_data, dict):
            raise TypeError(f"Traffic data must be a dictionary, got {type(traffic_data)}")

        required_fields = ["average_speed", "occupancy"]
        missing_fields = [f for f in required_fields if f not in traffic_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            speed = traffic_data.get("average_speed", 0)
            occupancy = traffic_data.get("occupancy", 0)

            # 数据验证
            if not isinstance(speed, (int, float)) or speed < 0:
                raise ValueError(f"Invalid speed: {speed}")

            if not isinstance(occupancy, (int, float)) or not (0 <= occupancy <= 100):
                raise ValueError(f"Invalid occupancy: {occupancy}")

            # 判断拥堵等级
            is_congested = speed < self.speed_threshold or occupancy > self.occupancy_threshold

            if is_congested:
                if speed < self.speed_threshold * 0.5 or occupancy > self.occupancy_threshold * 1.2:
                    congestion_level = "Severe"
                elif speed < self.speed_threshold * 0.7 or occupancy > self.occupancy_threshold * 1.1:
                    congestion_level = "Moderate"
                else:
                    congestion_level = "Light"
            else:
                congestion_level = "None"

            return {
                "is_congested": is_congested,
                "congestion_level": congestion_level,
                "speed": speed,
                "occupancy": occupancy,
                "speed_threshold": self.speed_threshold,
                "occupancy_threshold": self.occupancy_threshold
            }

        except ValueError as e:
            logger.error(f"Congestion detection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error detecting congestion: {e}", exc_info=True)
            raise RuntimeError(f"Failed to detect congestion: {e}") from e
```

---

## 6. ITS数据存储与分析

### 6.1 PostgreSQL ITS数据存储

**完整的PostgreSQL存储实现**：

```python
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ITSStorage:
    """ITS数据存储 - 增强错误处理"""

    def __init__(self, db_config: Dict):
        if not isinstance(db_config, dict):
            raise TypeError(f"Database config must be a dictionary, got {type(db_config)}")

        required_fields = ["host", "port", "database", "user", "password"]
        missing_fields = [f for f in required_fields if f not in db_config]
        if missing_fields:
            raise ValueError(f"Missing required database config fields: {', '.join(missing_fields)}")

        self.db_config = db_config
        self.conn: Optional[psycopg2.extensions.connection] = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            logger.info("Connected to PostgreSQL database")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e

    def create_tables(self):
        """创建表结构"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        try:
            with self.conn.cursor() as cur:
                # 交通传感器数据表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS traffic_sensor_data (
                        id SERIAL PRIMARY KEY,
                        sensor_id VARCHAR(100) NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        vehicle_count INTEGER NOT NULL CHECK (vehicle_count >= 0),
                        average_speed DECIMAL(5,2) NOT NULL CHECK (average_speed >= 0 AND average_speed <= 200),
                        occupancy DECIMAL(5,2) NOT NULL CHECK (occupancy >= 0 AND occupancy <= 100),
                        lane_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 交通信号控制表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS traffic_signal_control (
                        id SERIAL PRIMARY KEY,
                        intersection_id VARCHAR(100) NOT NULL,
                        phase_id INTEGER NOT NULL,
                        signal_state VARCHAR(20) NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        duration INTEGER NOT NULL CHECK (duration > 0),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # V2V消息表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS v2v_messages (
                        id SERIAL PRIMARY KEY,
                        vehicle_id INTEGER NOT NULL,
                        message_type VARCHAR(20) NOT NULL,
                        latitude DECIMAL(10,7) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
                        longitude DECIMAL(10,7) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
                        speed DECIMAL(5,2) NOT NULL CHECK (speed >= 0 AND speed <= 200),
                        heading DECIMAL(5,2) NOT NULL CHECK (heading >= 0 AND heading < 360),
                        timestamp TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 创建索引
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON traffic_sensor_data(timestamp)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_id ON traffic_sensor_data(sensor_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_signal_intersection ON traffic_signal_control(intersection_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_v2v_vehicle ON v2v_messages(vehicle_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_v2v_timestamp ON v2v_messages(timestamp)")

                self.conn.commit()
                logger.info("Created ITS database tables")

        except psycopg2.Error as e:
            logger.error(f"Failed to create tables: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Failed to create tables: {e}") from e

    def store_sensor_data(self, sensor_data: Dict) -> int:
        """存储传感器数据"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        if not isinstance(sensor_data, dict):
            raise TypeError(f"Sensor data must be a dictionary, got {type(sensor_data)}")

        required_fields = ["sensor_id", "timestamp", "vehicle_count", "average_speed", "occupancy"]
        missing_fields = [f for f in required_fields if f not in sensor_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO traffic_sensor_data
                    (sensor_id, timestamp, vehicle_count, average_speed, occupancy, lane_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    sensor_data["sensor_id"],
                    sensor_data["timestamp"],
                    sensor_data["vehicle_count"],
                    sensor_data["average_speed"],
                    sensor_data["occupancy"],
                    sensor_data.get("lane_id")
                ))

                record_id = cur.fetchone()[0]
                self.conn.commit()
                logger.debug(f"Stored sensor data with ID: {record_id}")
                return record_id

        except psycopg2.Error as e:
            logger.error(f"Failed to store sensor data: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Failed to store sensor data: {e}") from e

    def query_traffic_data(self, sensor_id: str, start_time: datetime,
                          end_time: datetime) -> List[Dict]:
        """查询交通数据"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        if not isinstance(sensor_id, str):
            raise TypeError(f"Sensor ID must be a string, got {type(sensor_id)}")

        if not isinstance(start_time, datetime):
            raise TypeError(f"Start time must be a datetime, got {type(start_time)}")

        if not isinstance(end_time, datetime):
            raise TypeError(f"End time must be a datetime, got {type(end_time)}")

        if end_time <= start_time:
            raise ValueError(f"End time must be after start time")

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM traffic_sensor_data
                    WHERE sensor_id = %s AND timestamp BETWEEN %s AND %s
                    ORDER BY timestamp
                """, (sensor_id, start_time, end_time))

                return cur.fetchall()

        except psycopg2.Error as e:
            logger.error(f"Failed to query traffic data: {e}")
            raise RuntimeError(f"Failed to query traffic data: {e}") from e
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
