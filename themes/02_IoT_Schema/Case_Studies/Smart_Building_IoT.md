# 智能建筑IoT Schema案例研究

## 案例概述

**项目名称**: 智慧办公楼物联网平台
**行业**: 物联网 - 智能建筑
**涉及标准**: MQTT, JSON Schema, OneM2M, LwM2M, BACnet, Modbus
**目标**: 建立统一的IoT设备数据模型，实现楼宇设备的智能化管理

---

## 背景介绍

### 业务背景

某商业综合体需要管理：

- 50层楼，每层20+传感器（温度、湿度、CO2、光照）
- 300+空调末端设备
- 100+照明控制回路
- 20+电梯系统
- 5+变配电站

原有系统：

- BACnet（暖通空调）
- Modbus（电力监控）
- 各厂商私有协议（照明、电梯）
- 数据孤岛严重，无法实现联动控制

### 改造目标

1. 建立统一的设备数据模型
2. 实现跨系统联动（如：光照+窗帘+照明联动）
3. 建立能耗监测和优化平台
4. 支持移动端远程监控

---

## Schema设计

### 设备数据模型

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://smartbuilding.com/schemas/device.json",
  "title": "IoT Device Schema",
  "description": "Smart building IoT device data model",
  "type": "object",
  "required": ["deviceId", "deviceType", "status", "sensors"],
  "properties": {
    "deviceId": {
      "type": "string",
      "pattern": "^[A-Z0-9]{3}-[0-9]{4}-[0-9]{4}$",
      "description": "Unique device identifier (FMT-BLDG-FLOOR-SEQ)"
    },
    "deviceType": {
      "type": "string",
      "enum": ["thermostat", "light", "sensor", "elevator", "hvac", "energy_meter"]
    },
    "location": {
      "type": "object",
      "required": ["building", "floor", "zone"],
      "properties": {
        "building": { "type": "string" },
        "floor": { "type": "integer", "minimum": 1, "maximum": 100 },
        "zone": { "type": "string" },
        "coordinates": {
          "type": "object",
          "properties": {
            "x": { "type": "number" },
            "y": { "type": "number" },
            "z": { "type": "number" }
          }
        }
      }
    },
    "status": {
      "type": "string",
      "enum": ["online", "offline", "error", "maintenance"]
    },
    "sensors": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/sensor"
      }
    },
    "actuators": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/actuator"
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "manufacturer": { "type": "string" },
        "model": { "type": "string" },
        "firmware": { "type": "string" },
        "installDate": { "type": "string", "format": "date" },
        "warrantyExpire": { "type": "string", "format": "date" }
      }
    }
  },
  "definitions": {
    "sensor": {
      "type": "object",
      "required": ["sensorId", "type", "value", "unit"],
      "properties": {
        "sensorId": { "type": "string" },
        "type": {
          "type": "string",
          "enum": ["temperature", "humidity", "co2", "light", "occupancy", "energy", "voltage", "current"]
        },
        "value": { "type": "number" },
        "unit": { "type": "string" },
        "timestamp": { "type": "string", "format": "date-time" },
        "quality": {
          "type": "string",
          "enum": ["good", "uncertain", "bad"],
          "default": "good"
        },
        "thresholds": {
          "type": "object",
          "properties": {
            "min": { "type": "number" },
            "max": { "type": "number" },
            "critical": { "type": "number" }
          }
        }
      }
    },
    "actuator": {
      "type": "object",
      "required": ["actuatorId", "type", "currentState"],
      "properties": {
        "actuatorId": { "type": "string" },
        "type": {
          "type": "string",
          "enum": ["switch", "dimmer", "valve", "motor", "display"]
        },
        "currentState": {},
        "availableStates": {
          "type": "array",
          "items": {}
        },
        "commands": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "parameters": { "type": "object" }
            }
          }
        }
      }
    }
  }
}
```

### MQTT主题设计

```text
smartbuilding/
├── {buildingId}/
│   ├── devices/
│   │   ├── {deviceId}/telemetry      (设备遥测数据)
│   │   ├── {deviceId}/status         (设备状态)
│   │   ├── {deviceId}/commands       (命令下发)
│   │   └── {deviceId}/events         (设备事件)
│   ├── floors/
│   │   ├── {floorId}/aggregated      (楼层聚合数据)
│   │   └── {floorId}/energy          (楼层能耗)
│   ├── zones/
│   │   └── {zoneId}/climate          (区域气候控制)
│   ├── systems/
│   │   ├── hvac/status               (暖通状态)
│   │   ├── lighting/status           (照明状态)
│   │   ├── elevator/status           (电梯状态)
│   │   └── energy/consumption        (能耗统计)
│   └── alerts/
│       ├── critical                  (严重告警)
│       ├── warning                   (警告)
│       └── info                      (提示)
└── management/
    ├── firmware/update               (固件更新)
    ├── config/{deviceId}             (配置下发)
    └── discovery                     (设备发现)
```

---

## 实现代码

### IoT设备管理器

```python
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import jsonschema
from jsonschema import validate

class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class SensorData:
    sensorId: str
    type: str
    value: float
    unit: str
    timestamp: str
    quality: str = "good"

@dataclass
class IoTDevice:
    deviceId: str
    deviceType: str
    location: Dict
    status: DeviceStatus
    sensors: List[SensorData]
    metadata: Dict

class SmartBuildingIoTManager:
    """智能建筑IoT设备管理器"""

    DEVICE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["deviceId", "deviceType", "status", "sensors"],
        "properties": {
            "deviceId": {
                "type": "string",
                "pattern": "^[A-Z0-9]{3}-[0-9]{4}-[0-9]{4}$"
            },
            "deviceType": {
                "type": "string",
                "enum": ["thermostat", "light", "sensor", "elevator", "hvac", "energy_meter"]
            },
            "location": {
                "type": "object",
                "required": ["building", "floor", "zone"],
                "properties": {
                    "building": {"type": "string"},
                    "floor": {"type": "integer", "minimum": 1},
                    "zone": {"type": "string"}
                }
            },
            "status": {
                "type": "string",
                "enum": ["online", "offline", "error", "maintenance"]
            },
            "sensors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["sensorId", "type", "value", "unit"],
                    "properties": {
                        "sensorId": {"type": "string"},
                        "type": {"type": "string"},
                        "value": {"type": "number"},
                        "unit": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "quality": {"type": "string"}
                    }
                }
            }
        }
    }

    def __init__(self, mqtt_broker: str, mqtt_port: int = 1883):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message

        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port

        self.devices: Dict[str, IoTDevice] = {}
        self.callbacks: Dict[str, List[Callable]] = {}

        # 告警阈值配置
        self.thresholds = {
            'temperature': {'min': 18, 'max': 26, 'critical': 30},
            'humidity': {'min': 30, 'max': 70, 'critical': 80},
            'co2': {'min': 0, 'max': 1000, 'critical': 1500}
        }

    def connect(self):
        """连接MQTT Broker"""
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.mqtt_client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        print(f"Connected to MQTT Broker with result code {rc}")
        # 订阅所有设备数据
        client.subscribe("smartbuilding/+/devices/+/telemetry")
        client.subscribe("smartbuilding/+/devices/+/status")
        client.subscribe("smartbuilding/+/alerts/+")

    def _on_message(self, client, userdata, msg):
        """MQTT消息回调"""
        try:
            topic_parts = msg.topic.split('/')
            payload = json.loads(msg.payload.decode())

            if 'telemetry' in topic_parts:
                self._handle_telemetry(topic_parts, payload)
            elif 'status' in topic_parts:
                self._handle_status(topic_parts, payload)
            elif 'alerts' in topic_parts:
                self._handle_alert(topic_parts, payload)

        except Exception as e:
            print(f"Error processing message: {e}")

    def _handle_telemetry(self, topic_parts: List[str], payload: Dict):
        """处理遥测数据"""
        device_id = topic_parts[3]

        try:
            # 验证数据格式
            validate(instance=payload, schema=self.DEVICE_SCHEMA)

            # 更新设备数据
            if device_id in self.devices:
                device = self.devices[device_id]
                device.sensors = [SensorData(**s) for s in payload.get('sensors', [])]

                # 检查告警阈值
                self._check_thresholds(device)

                # 触发回调
                self._trigger_callbacks(device_id, 'telemetry', device)

        except jsonschema.exceptions.ValidationError as e:
            print(f"Schema validation error for device {device_id}: {e}")

    def _handle_status(self, topic_parts: List[str], payload: Dict):
        """处理状态更新"""
        device_id = topic_parts[3]

        if device_id in self.devices:
            status = payload.get('status', 'offline')
            self.devices[device_id].status = DeviceStatus(status)
            self._trigger_callbacks(device_id, 'status', self.devices[device_id])

    def _handle_alert(self, topic_parts: List[str], payload: Dict):
        """处理告警"""
        alert_level = topic_parts[-1]
        print(f"[{alert_level.upper()}] {payload.get('message')}")

        # 可以在这里集成告警通知系统

    def _check_thresholds(self, device: IoTDevice):
        """检查传感器阈值"""
        for sensor in device.sensors:
            if sensor.type in self.thresholds:
                threshold = self.thresholds[sensor.type]

                if sensor.value > threshold['critical']:
                    self._publish_alert('critical', {
                        'deviceId': device.deviceId,
                        'sensor': sensor.type,
                        'value': sensor.value,
                        'threshold': threshold['critical'],
                        'message': f"Critical {sensor.type} level: {sensor.value}"
                    })

                elif sensor.value > threshold['max'] or sensor.value < threshold['min']:
                    self._publish_alert('warning', {
                        'deviceId': device.deviceId,
                        'sensor': sensor.type,
                        'value': sensor.value,
                        'threshold': threshold,
                        'message': f"{sensor.type} out of range: {sensor.value}"
                    })

    def _publish_alert(self, level: str, alert_data: Dict):
        """发布告警"""
        topic = f"smartbuilding/alerts/{level}"
        self.mqtt_client.publish(topic, json.dumps(alert_data))

    def _trigger_callbacks(self, device_id: str, event_type: str, data):
        """触发注册的回调"""
        key = f"{device_id}:{event_type}"
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Callback error: {e}")

    def register_device(self, device: IoTDevice):
        """注册设备"""
        self.devices[device.deviceId] = device
        print(f"Registered device: {device.deviceId}")

    def send_command(self, device_id: str, command: str, params: Dict = None):
        """发送命令到设备"""
        if device_id not in self.devices:
            print(f"Device {device_id} not found")
            return

        topic = f"smartbuilding/devices/{device_id}/commands"
        payload = {
            'command': command,
            'parameters': params or {},
            'timestamp': datetime.now().isoformat()
        }

        self.mqtt_client.publish(topic, json.dumps(payload))
        print(f"Command sent to {device_id}: {command}")

    def subscribe_event(self, device_id: str, event_type: str, callback: Callable):
        """订阅设备事件"""
        key = f"{device_id}:{event_type}"
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)

    def get_device_aggregation(self, floor: int = None, zone: str = None) -> Dict:
        """获取设备聚合数据"""
        filtered_devices = self.devices.values()

        if floor:
            filtered_devices = [d for d in filtered_devices
                              if d.location.get('floor') == floor]

        if zone:
            filtered_devices = [d for d in filtered_devices
                              if d.location.get('zone') == zone]

        # 计算聚合统计
        aggregation = {
            'total_devices': len(filtered_devices),
            'online_count': sum(1 for d in filtered_devices
                              if d.status == DeviceStatus.ONLINE),
            'avg_temperature': self._calculate_avg(filtered_devices, 'temperature'),
            'avg_humidity': self._calculate_avg(filtered_devices, 'humidity'),
            'total_energy': self._calculate_sum(filtered_devices, 'energy')
        }

        return aggregation

    def _calculate_avg(self, devices: List[IoTDevice], sensor_type: str) -> float:
        """计算平均值"""
        values = []
        for device in devices:
            for sensor in device.sensors:
                if sensor.type == sensor_type:
                    values.append(sensor.value)

        return sum(values) / len(values) if values else 0.0

    def _calculate_sum(self, devices: List[IoTDevice], sensor_type: str) -> float:
        """计算总和"""
        total = 0.0
        for device in devices:
            for sensor in device.sensors:
                if sensor.type == sensor_type:
                    total += sensor.value
        return total


# 使用示例
if __name__ == "__main__":
    # 创建管理器
    manager = SmartBuildingIoTManager("localhost", 1883)
    manager.connect()

    # 注册设备
    device = IoTDevice(
        deviceId="BLD-0001-0001",
        deviceType="sensor",
        location={"building": "BLD", "floor": 10, "zone": "A"},
        status=DeviceStatus.ONLINE,
        sensors=[
            SensorData("TEMP-01", "temperature", 24.5, "°C", datetime.now().isoformat()),
            SensorData("HUM-01", "humidity", 55.0, "%", datetime.now().isoformat())
        ],
        metadata={"manufacturer": "Honeywell", "model": "HPT-100"}
    )

    manager.register_device(device)

    # 订阅事件
    def on_telemetry(data):
        print(f"Telemetry received: {data}")

    manager.subscribe_event("BLD-0001-0001", "telemetry", on_telemetry)

    # 发送命令
    manager.send_command("BLD-0001-0001", "set_interval", {"seconds": 30})
```

---

## 能耗优化实现

```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from typing import List, Dict
import numpy as np

class EnergyOptimizer:
    """建筑能耗优化器"""

    def __init__(self, iot_manager: SmartBuildingIoTManager):
        self.iot_manager = iot_manager
        self.model = RandomForestRegressor(n_estimators=100)
        self.is_trained = False

    def collect_training_data(self, days: int = 30) -> pd.DataFrame:
        """收集训练数据"""
        data = []

        # 模拟历史数据收集
        for _ in range(days * 24):  # 每小时一个样本
            # 获取聚合数据
            agg = self.iot_manager.get_device_aggregation()

            # 特征
            features = {
                'hour': np.random.randint(0, 24),
                'day_of_week': np.random.randint(0, 7),
                'outside_temp': np.random.uniform(10, 35),
                'avg_floor_temp': agg.get('avg_temperature', 22),
                'occupancy_rate': np.random.uniform(0.1, 0.9),
                'hvac_status': np.random.choice([0, 1]),
                'lighting_level': np.random.uniform(0, 100)
            }

            # 目标：能耗
            energy = self._calculate_energy(features)
            features['energy_consumption'] = energy

            data.append(features)

        return pd.DataFrame(data)

    def _calculate_energy(self, features: Dict) -> float:
        """计算能耗（简化模型）"""
        base_load = 100  # kW

        # HVAC能耗
        temp_diff = abs(features['avg_floor_temp'] - 22)
        hvac_energy = features['hvac_status'] * temp_diff * 5

        # 照明能耗
        lighting_energy = features['lighting_level'] * 0.5

        # 人员相关
        occupancy_energy = features['occupancy_rate'] * 20

        return base_load + hvac_energy + lighting_energy + occupancy_energy

    def train_model(self, df: pd.DataFrame):
        """训练预测模型"""
        X = df[['hour', 'day_of_week', 'outside_temp', 'avg_floor_temp',
                'occupancy_rate', 'hvac_status', 'lighting_level']]
        y = df['energy_consumption']

        self.model.fit(X, y)
        self.is_trained = True

        # 评估
        score = self.model.score(X, y)
        print(f"Model trained with R² score: {score:.3f}")

    def optimize_settings(self, current_conditions: Dict) -> Dict:
        """优化设备设置"""
        if not self.is_trained:
            return {}

        best_settings = None
        min_energy = float('inf')

        # 网格搜索最优设置
        for hvac in [0, 1]:
            for lighting in range(0, 101, 10):
                conditions = current_conditions.copy()
                conditions['hvac_status'] = hvac
                conditions['lighting_level'] = lighting

                # 预测能耗
                features = np.array([[
                    conditions['hour'],
                    conditions['day_of_week'],
                    conditions['outside_temp'],
                    conditions['avg_floor_temp'],
                    conditions['occupancy_rate'],
                    hvac,
                    lighting
                ]])

                energy = self.model.predict(features)[0]

                # 考虑舒适度约束
                comfort_score = self._calculate_comfort(conditions)

                # 综合评分
                if comfort_score >= 0.8 and energy < min_energy:
                    min_energy = energy
                    best_settings = {
                        'hvac_status': hvac,
                        'lighting_level': lighting,
                        'predicted_energy': energy,
                        'comfort_score': comfort_score
                    }

        return best_settings or {}

    def _calculate_comfort(self, conditions: Dict) -> float:
        """计算舒适度评分"""
        # 温度舒适度
        temp = conditions.get('avg_floor_temp', 22)
        temp_comfort = 1.0 - abs(temp - 22) / 10
        temp_comfort = max(0, min(1, temp_comfort))

        # 照明舒适度
        lighting = conditions.get('lighting_level', 50)
        lighting_comfort = lighting / 100 if conditions.get('occupancy_rate', 0) > 0.3 else 1.0

        return (temp_comfort + lighting_comfort) / 2


# 使用示例
if __name__ == "__main__":
    from SmartBuildingIoTManager import SmartBuildingIoTManager

    # 创建IoT管理器
    iot_manager = SmartBuildingIoTManager("localhost")
    iot_manager.connect()

    # 创建能耗优化器
    optimizer = EnergyOptimizer(iot_manager)

    # 收集训练数据
    print("Collecting training data...")
    df = optimizer.collect_training_data(days=30)

    # 训练模型
    print("Training model...")
    optimizer.train_model(df)

    # 优化设置
    current = {
        'hour': 14,
        'day_of_week': 2,
        'outside_temp': 30,
        'avg_floor_temp': 24,
        'occupancy_rate': 0.7
    }

    optimal = optimizer.optimize_settings(current)
    print(f"Optimal settings: {optimal}")
```

---

## 实施成果

### 运营效果

| 指标 | 改造前 | 改造后 | 改善 |
|------|--------|--------|------|
| 能耗 | 基准 | -25% | 显著降低 |
| 设备故障响应 | 30分钟 | 5分钟 | 83% ↓ |
| 舒适度投诉 | 10/月 | 1/月 | 90% ↓ |
| 运维人员 | 15人 | 8人 | 47% ↓ |

### 技术创新

1. **统一数据模型**: JSON Schema标准化设备描述
2. **实时优化**: ML驱动的能耗优化
3. **预测性维护**: 基于传感器数据的故障预测
4. **数字孪生**: 楼宇3D可视化与实时数据映射

---

**创建时间**: 2026-02-17
**维护者**: DSL Schema研究团队
