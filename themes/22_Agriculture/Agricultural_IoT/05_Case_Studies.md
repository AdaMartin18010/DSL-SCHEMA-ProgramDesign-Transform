# 农业物联网Schema实践案例

## 📑 目录

- [1. 案例概述](#1-案例概述)
- [2. 企业背景](#2-企业背景)
- [3. 业务痛点与目标](#3-业务痛点与目标)
- [4. 技术挑战](#4-技术挑战)
- [5. 解决方案架构](#5-解决方案架构)
- [6. 完整实现代码](#6-完整实现代码)
- [7. 效果评估与ROI分析](#7-效果评估与roi分析)

---

## 1. 案例概述

本文档提供农业物联网(IoT)Schema在实际应用中的完整实践案例，涵盖传感器数据采集、设备管理、远程控制、边缘计算等核心IoT场景。

---

## 2. 企业背景

### 2.1 企业概况

**企业名称**：智联农业物联网科技有限公司（虚构案例企业）

**企业规模**：
- 部署传感器节点：50,000+
- 覆盖农场：150+家
- 日处理数据量：2TB
- 年营业额：1.5亿元人民币

---

## 3. 业务痛点与目标

### 3.1 五大业务痛点

| 序号 | 痛点 | 具体表现 | 影响程度 |
|------|------|----------|----------|
| 1 | **设备管理复杂** | 多厂商设备协议不一 | 高 |
| 2 | **网络覆盖困难** | 农田网络信号不稳定 | 高 |
| 3 | **数据丢失风险** | 网络中断导致数据丢失 | 高 |
| 4 | **实时性差** | 控制指令延迟高 | 中 |
| 5 | **运维成本高** | 现场维护频繁 | 中 |

### 3.2 五大业务目标

| 序号 | 目标 | 具体指标 | 完成期限 |
|------|------|----------|----------|
| 1 | **统一设备管理** | 支持50+种设备协议 | 9个月 |
| 2 | **数据完整性** | 数据丢失率<0.1% | 6个月 |
| 3 | **实时控制** | 控制延迟<2秒 | 6个月 |
| 4 | **远程运维** | 80%问题远程解决 | 12个月 |
| 5 | **边缘智能** | 50%计算本地完成 | 12个月 |

---

## 4. 技术挑战

1. **协议兼容性**：Modbus、LoRaWAN、NB-IoT等多种通信协议
2. **边缘计算**：网络不稳定情况下的数据处理能力
3. **实时数据处理**：高频传感器数据的实时分析
4. **设备安全**：物联网设备的安全认证和加密
5. **能耗管理**：低功耗设计和电池寿命优化

---

## 5. 解决方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    云平台层                                  │
│  设备管理  数据存储  规则引擎  可视化                        │
├─────────────────────────────────────────────────────────────┤
│                    网络层                                    │
│  4G/5G  LoRaWAN  NB-IoT  WiFi  卫星                        │
├─────────────────────────────────────────────────────────────┤
│                    边缘层                                    │
│  边缘网关  协议转换  本地存储  边缘计算                      │
├─────────────────────────────────────────────────────────────┤
│                    感知层                                    │
│  土壤传感器  气象站  摄像头  控制器  执行器                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 完整实现代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农业物联网Schema实践案例
企业：智联农业物联网科技有限公司
"""

import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import threading
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """设备类型"""
    SOIL_SENSOR = "soil_sensor"
    WEATHER_STATION = "weather_station"
    CAMERA = "camera"
    IRRIGATION_CONTROLLER = "irrigation_controller"
    GATEWAY = "gateway"


class DeviceStatus(Enum):
    """设备状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    SLEEPING = "sleeping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ProtocolType(Enum):
    """通信协议"""
    MODBUS_RTU = "modbus_rtu"
    MODBUS_TCP = "modbus_tcp"
    LORAWAN = "lorawan"
    MQTT = "mqtt"
    HTTP = "http"
    COAP = "coap"
    NB_IOT = "nb_iot"


@dataclass
class SensorReading:
    """传感器读数"""
    sensor_id: str
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    quality: str = "good"  # good, suspect, bad
    
    def to_dict(self) -> Dict:
        return {
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "quality": self.quality
        }


@dataclass
class IoTDevice:
    """物联网设备"""
    device_id: str
    device_name: str
    device_type: DeviceType
    protocol: ProtocolType
    status: DeviceStatus = DeviceStatus.OFFLINE
    firmware_version: str = "1.0.0"
    last_seen: Optional[datetime] = None
    battery_level: Optional[float] = None  # %
    signal_strength: Optional[float] = None  # dBm
    location: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_online(self) -> bool:
        if not self.last_seen:
            return False
        return (datetime.now() - self.last_seen).seconds < 300  # 5分钟内有心跳
    
    def update_status(self):
        self.status = DeviceStatus.ONLINE if self.is_online() else DeviceStatus.OFFLINE
    
    def to_dict(self) -> Dict:
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type.value,
            "protocol": self.protocol.value,
            "status": self.status.value,
            "firmware_version": self.firmware_version,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "location": self.location
        }


@dataclass
class ControlCommand:
    """控制命令"""
    command_id: str
    device_id: str
    command_type: str
    parameters: Dict[str, Any]
    issued_at: datetime
    executed_at: Optional[datetime] = None
    status: str = "pending"  # pending, executing, completed, failed
    response: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "command_id": self.command_id,
            "device_id": self.device_id,
            "command_type": self.command_type,
            "parameters": self.parameters,
            "issued_at": self.issued_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "status": self.status,
            "response": self.response
        }


class ProtocolAdapter:
    """协议适配器"""
    
    def __init__(self):
        self.parsers: Dict[ProtocolType, Callable] = {
            ProtocolType.MODBUS_RTU: self._parse_modbus,
            ProtocolType.MQTT: self._parse_mqtt,
            ProtocolType.LORAWAN: self._parse_lorawan,
            ProtocolType.HTTP: self._parse_http
        }
    
    def parse_message(self, protocol: ProtocolType, raw_data: bytes) -> Optional[Dict]:
        """解析原始数据"""
        parser = self.parsers.get(protocol)
        if parser:
            return parser(raw_data)
        return None
    
    def _parse_modbus(self, data: bytes) -> Dict:
        """解析Modbus数据（简化）"""
        # 模拟Modbus解析
        return {
            "register_address": 0,
            "value": int.from_bytes(data[:2], 'big') if len(data) >= 2 else 0
        }
    
    def _parse_mqtt(self, data: bytes) -> Dict:
        """解析MQTT数据"""
        try:
            return json.loads(data.decode('utf-8'))
        except:
            return {"raw": data.hex()}
    
    def _parse_lorawan(self, data: bytes) -> Dict:
        """解析LoRaWAN数据"""
        # 简化的LoRaWAN解析
        return {
            "payload": data.hex(),
            "port": 1,
            "rssi": -80
        }
    
    def _parse_http(self, data: bytes) -> Dict:
        """解析HTTP数据"""
        try:
            return json.loads(data.decode('utf-8'))
        except:
            return {"raw": data.decode('utf-8', errors='ignore')}


class EdgeGateway:
    """边缘网关"""
    
    def __init__(self, gateway_id: str):
        self.gateway_id = gateway_id
        self.devices: Dict[str, IoTDevice] = {}
        self.data_buffer: deque = deque(maxlen=10000)
        self.command_queue: List[ControlCommand] = []
        self.local_storage: Dict[str, List[Dict]] = {}
        self.adapter = ProtocolAdapter()
        self.running = False
        self.edge_rules: List[Callable] = []
        
    def register_device(self, device: IoTDevice):
        """注册设备"""
        self.devices[device.device_id] = device
        self.local_storage[device.device_id] = []
        logger.info(f"Device {device.device_id} registered to gateway {self.gateway_id}")
    
    def process_sensor_data(self, device_id: str, raw_data: bytes, protocol: ProtocolType):
        """处理传感器数据"""
        device = self.devices.get(device_id)
        if not device:
            return
        
        # 更新设备状态
        device.last_seen = datetime.now()
        device.update_status()
        
        # 解析数据
        parsed = self.adapter.parse_message(protocol, raw_data)
        if not parsed:
            return
        
        # 创建读数记录
        reading = {
            "device_id": device_id,
            "gateway_id": self.gateway_id,
            "timestamp": datetime.now().isoformat(),
            "protocol": protocol.value,
            "data": parsed
        }
        
        # 本地存储
        self.local_storage[device_id].append(reading)
        
        # 边缘计算：执行本地规则
        self._execute_edge_rules(device_id, reading)
        
        # 加入上传缓冲区
        self.data_buffer.append(reading)
        
        return reading
    
    def _execute_edge_rules(self, device_id: str, reading: Dict):
        """执行边缘计算规则"""
        for rule in self.edge_rules:
            try:
                rule(device_id, reading)
            except Exception as e:
                logger.error(f"Edge rule error: {e}")
    
    def add_edge_rule(self, rule: Callable):
        """添加边缘规则"""
        self.edge_rules.append(rule)
    
    def queue_command(self, command: ControlCommand):
        """队列控制命令"""
        self.command_queue.append(command)
        logger.info(f"Command queued: {command.command_id}")
    
    def execute_command(self, command_id: str) -> bool:
        """执行控制命令"""
        command = next((c for c in self.command_queue if c.command_id == command_id), None)
        if not command:
            return False
        
        device = self.devices.get(command.device_id)
        if not device or device.status != DeviceStatus.ONLINE:
            command.status = "failed"
            command.response = "Device offline"
            return False
        
        # 模拟命令执行
        command.status = "executing"
        time.sleep(0.1)  # 模拟执行延迟
        command.status = "completed"
        command.executed_at = datetime.now()
        command.response = "Success"
        
        logger.info(f"Command executed: {command_id}")
        return True
    
    def sync_to_cloud(self) -> List[Dict]:
        """同步数据到云端"""
        data_to_sync = list(self.data_buffer)
        self.data_buffer.clear()
        return data_to_sync
    
    def get_device_stats(self) -> Dict:
        """获取设备统计"""
        online_count = sum(1 for d in self.devices.values() if d.status == DeviceStatus.ONLINE)
        return {
            "gateway_id": self.gateway_id,
            "total_devices": len(self.devices),
            "online_devices": online_count,
            "offline_devices": len(self.devices) - online_count,
            "buffer_size": len(self.data_buffer),
            "pending_commands": len(self.command_queue)
        }


class IoTPlatform:
    """物联网平台"""
    
    def __init__(self):
        self.gateways: Dict[str, EdgeGateway] = {}
        self.devices: Dict[str, IoTDevice] = {}
        self.data_store: Dict[str, List[Dict]] = {}
        self.rules: List[Dict] = []
        self.command_history: List[ControlCommand] = []
    
    def register_gateway(self, gateway: EdgeGateway):
        """注册网关"""
        self.gateways[gateway.gateway_id] = gateway
        logger.info(f"Gateway registered: {gateway.gateway_id}")
    
    def get_all_devices(self) -> List[IoTDevice]:
        """获取所有设备"""
        devices = []
        for gateway in self.gateways.values():
            devices.extend(gateway.devices.values())
        return devices
    
    def create_rule(self, rule_name: str, condition: Dict, action: Dict):
        """创建规则"""
        rule = {
            "rule_id": str(uuid.uuid4()),
            "name": rule_name,
            "condition": condition,
            "action": action,
            "enabled": True
        }
        self.rules.append(rule)
        return rule
    
    def process_data_stream(self, gateway_id: str, readings: List[Dict]):
        """处理数据流"""
        for reading in readings:
            device_id = reading.get("device_id")
            if device_id not in self.data_store:
                self.data_store[device_id] = []
            self.data_store[device_id].append(reading)
            
            # 评估规则
            self._evaluate_rules(reading)
    
    def _evaluate_rules(self, reading: Dict):
        """评估规则"""
        for rule in self.rules:
            if not rule["enabled"]:
                continue
            
            condition = rule["condition"]
            if self._check_condition(reading, condition):
                self._execute_action(rule["action"], reading)
    
    def _check_condition(self, reading: Dict, condition: Dict) -> bool:
        """检查条件"""
        metric = condition.get("metric")
        operator = condition.get("operator")
        threshold = condition.get("threshold")
        
        data = reading.get("data", {})
        value = data.get(metric) if isinstance(data, dict) else None
        
        if value is None:
            return False
        
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        
        return False
    
    def _execute_action(self, action: Dict, reading: Dict):
        """执行动作"""
        action_type = action.get("type")
        if action_type == "send_command":
            device_id = action.get("device_id")
            command_type = action.get("command_type")
            parameters = action.get("parameters", {})
            
            command = ControlCommand(
                command_id=str(uuid.uuid4()),
                device_id=device_id,
                command_type=command_type,
                parameters=parameters,
                issued_at=datetime.now()
            )
            
            # 找到对应的网关
            for gateway in self.gateways.values():
                if device_id in gateway.devices:
                    gateway.queue_command(command)
                    self.command_history.append(command)
                    break
        
        elif action_type == "alert":
            logger.warning(f"Rule triggered alert: {action.get('message')}")
    
    def get_analytics(self, device_id: str, metric: str, hours: int = 24) -> Dict:
        """获取设备分析数据"""
        data = self.data_store.get(device_id, [])
        
        # 过滤时间范围
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [
            d for d in data 
            if datetime.fromisoformat(d["timestamp"]) > cutoff_time
        ]
        
        # 提取指标值
        values = []
        for d in recent_data:
            d_data = d.get("data", {})
            if isinstance(d_data, dict) and metric in d_data:
                values.append(d_data[metric])
        
        if not values:
            return {"error": "No data available"}
        
        return {
            "device_id": device_id,
            "metric": metric,
            "period_hours": hours,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None
        }
    
    def generate_platform_report(self) -> Dict:
        """生成平台报告"""
        total_devices = len(self.get_all_devices())
        online_devices = sum(1 for d in self.get_all_devices() if d.status == DeviceStatus.ONLINE)
        
        return {
            "report_time": datetime.now().isoformat(),
            "gateways": len(self.gateways),
            "total_devices": total_devices,
            "online_devices": online_devices,
            "online_rate": round(online_devices / total_devices * 100, 2) if total_devices else 0,
            "active_rules": len([r for r in self.rules if r["enabled"]]),
            "total_data_points": sum(len(d) for d in self.data_store.values()),
            "commands_executed": len(self.command_history)
        }


def create_demo_iot_system():
    """创建演示IoT系统"""
    platform = IoTPlatform()
    
    # 创建网关
    gateway1 = EdgeGateway("GW-001")
    gateway2 = EdgeGateway("GW-002")
    
    # 创建设备
    devices = [
        IoTDevice("SOIL-001", "1号土壤传感器", DeviceType.SOIL_SENSOR, ProtocolType.LORAWAN),
        IoTDevice("SOIL-002", "2号土壤传感器", DeviceType.SOIL_SENSOR, ProtocolType.LORAWAN),
        IoTDevice("WEATHER-001", "气象站1", DeviceType.WEATHER_STATION, ProtocolType.MQTT),
        IoTDevice("IRR-001", "灌溉控制器", DeviceType.IRRIGATION_CONTROLLER, ProtocolType.MQTT),
        IoTDevice("SOIL-003", "3号土壤传感器", DeviceType.SOIL_SENSOR, ProtocolType.NB_IOT),
        IoTDevice("CAM-001", "监控摄像头", DeviceType.CAMERA, ProtocolType.HTTP),
    ]
    
    # 注册设备到网关
    for i, device in enumerate(devices):
        if i < 3:
            gateway1.register_device(device)
        else:
            gateway2.register_device(device)
    
    # 添加边缘规则：土壤湿度低时自动灌溉
    def auto_irrigation_rule(device_id: str, reading: Dict):
        data = reading.get("data", {})
        if isinstance(data, dict) and data.get("moisture", 100) < 40:
            logger.info(f"Edge rule: Low moisture detected on {device_id}, triggering irrigation")
    
    gateway1.add_edge_rule(auto_irrigation_rule)
    
    # 注册网关到平台
    platform.register_gateway(gateway1)
    platform.register_gateway(gateway2)
    
    # 创建平台规则
    platform.create_rule(
        rule_name="高温预警",
        condition={"metric": "temperature", "operator": ">", "threshold": 35},
        action={"type": "alert", "message": "温度过高，请注意遮阳"}
    )
    
    # 模拟数据收集
    for gateway in [gateway1, gateway2]:
        for device_id in gateway.devices:
            for _ in range(10):
                # 模拟传感器数据
                raw_data = json.dumps({
                    "moisture": random.uniform(30, 80),
                    "temperature": random.uniform(20, 38),
                    "battery": random.uniform(20, 100)
                }).encode()
                
                protocol = gateway.devices[device_id].protocol
                gateway.process_sensor_data(device_id, raw_data, protocol)
    
    return platform


def main():
    """主函数"""
    print("=" * 80)
    print("农业物联网Schema实践案例 - 智联农业IoT")
    print("=" * 80)
    
    # 创建系统
    print("\n【步骤1】创建IoT系统...")
    platform = create_demo_iot_system()
    print(f"  网关数量: {len(platform.gateways)}")
    print(f"  设备总数: {len(platform.get_all_devices())}")
    
    # 同步数据到云端
    print("\n【步骤2】同步数据到云端...")
    total_synced = 0
    for gateway in platform.gateways.values():
        data = gateway.sync_to_cloud()
        platform.process_data_stream(gateway.gateway_id, data)
        total_synced += len(data)
    print(f"  同步数据点: {total_synced}")
    
    # 设备统计
    print("\n【步骤3】设备状态统计...")
    for gw_id, gateway in platform.gateways.items():
        stats = gateway.get_device_stats()
        print(f"  网关 {gw_id}:")
        print(f"    设备数: {stats['total_devices']}, 在线: {stats['online_devices']}")
    
    # 数据分析
    print("\n【步骤4】传感器数据分析...")
    analytics = platform.get_analytics("SOIL-001", "moisture", hours=24)
    if "error" not in analytics:
        print(f"  设备 SOIL-001 土壤湿度:")
        print(f"    平均值: {analytics['avg']:.1f}%")
        print(f"    范围: {analytics['min']:.1f}% - {analytics['max']:.1f}%")
    
    # 平台报告
    print("\n【步骤5】生成平台报告...")
    report = platform.generate_platform_report()
    print(f"  在线率: {report['online_rate']}%")
    print(f"  活跃规则: {report['active_rules']}")
    print(f"  总数据点: {report['total_data_points']}")
    
    print("\n" + "=" * 80)
    print("农业物联网Schema实践案例执行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

---

## 7. 效果评估与ROI分析

### 7.1 关键绩效指标

| 指标 | 实施前 | 实施后 | 改善 |
|------|--------|--------|------|
| 设备在线率 | 75% | 98% | +31% |
| 数据完整性 | 85% | 99.9% | +18% |
| 响应延迟 | 8秒 | 1.2秒 | -85% |
| 现场维护次数 | 每月20次 | 每月4次 | -80% |

### 7.2 ROI分析

**投资**：¥120万  
**年收益**：¥200万  
**ROI**：167%（3年）

---

**创建时间**：2026-02-15  
**版本**：1.0.0
