# Matter Schema转换体系

## 📑 目录

- [Matter Schema转换体系](#matter-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Matter设备控制实现](#2-matter设备控制实现)
    - [2.1 Matter SDK设备控制封装](#21-matter-sdk设备控制封装)
    - [2.2 Matter到Zigbee转换](#22-matter到zigbee转换)
  - [3. Zigbee到Matter转换](#3-zigbee到matter转换)
  - [4. Matter设备发现和管理](#4-matter设备发现和管理)
    - [4.1 设备发现实现](#41-设备发现实现)
  - [5. 转换工具](#5-转换工具)
    - [5.1 Matter SDK集成](#51-matter-sdk集成)
    - [5.2 CHIP Tool集成](#52-chip-tool集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 转换正确性验证](#61-转换正确性验证)
    - [6.2 设备控制验证](#62-设备控制验证)
  - [7. Matter数据存储与分析](#7-matter数据存储与分析)
    - [7.1 PostgreSQL Matter数据存储](#71-postgresql-matter数据存储)
    - [7.2 Matter数据分析查询](#72-matter数据分析查询)

---

## 1. 转换体系概述

Matter Schema转换体系支持Matter设备、Zigbee设备、
数据库存储之间的转换。

### 1.1 转换目标

1. **Matter到Zigbee转换**：Matter集群到Zigbee集群
2. **Zigbee到Matter转换**：Zigbee集群到Matter集群
3. **数据到数据库转换**：Matter数据到PostgreSQL存储

---

## 2. Matter设备控制实现

### 2.1 Matter SDK设备控制封装

**完整的Matter设备控制实现**：

```python
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import IntEnum

logger = logging.getLogger(__name__)

# Matter集群ID定义
class MatterClusterId(IntEnum):
    """Matter集群ID"""
    ON_OFF = 0x0006
    LEVEL_CONTROL = 0x0008
    COLOR_CONTROL = 0x0300
    DOOR_LOCK = 0x0101
    THERMOSTAT = 0x0201
    WINDOW_COVERING = 0x0102
    TEMPERATURE_MEASUREMENT = 0x0402
    PRESSURE_MEASUREMENT = 0x0403
    FLOW_MEASUREMENT = 0x0404

# Matter属性ID定义
class MatterAttributeId(IntEnum):
    """Matter属性ID"""
    # On/Off Cluster
    ON_OFF_ON_OFF = 0x0000
    ON_OFF_GLOBAL_SCENE_CONTROL = 0x4000
    ON_OFF_ON_TIME = 0x4001
    ON_OFF_OFF_WAIT_TIME = 0x4002
    ON_OFF_START_UP_ON_OFF = 0x4003

    # Level Control Cluster
    LEVEL_CONTROL_CURRENT_LEVEL = 0x0000
    LEVEL_CONTROL_REMAINING_TIME = 0x0001
    LEVEL_CONTROL_MIN_LEVEL = 0x0002
    LEVEL_CONTROL_MAX_LEVEL = 0x0003

    # Color Control Cluster
    COLOR_CONTROL_CURRENT_HUE = 0x0000
    COLOR_CONTROL_CURRENT_SATURATION = 0x0001
    COLOR_CONTROL_CURRENT_X = 0x0003
    COLOR_CONTROL_CURRENT_Y = 0x0004
    COLOR_CONTROL_COLOR_TEMPERATURE_MIREDS = 0x0007

# Matter命令ID定义
class MatterCommandId(IntEnum):
    """Matter命令ID"""
    # On/Off Cluster
    ON_OFF_ON = 0x00
    ON_OFF_OFF = 0x01
    ON_OFF_TOGGLE = 0x02

    # Level Control Cluster
    LEVEL_CONTROL_MOVE_TO_LEVEL = 0x00
    LEVEL_CONTROL_MOVE = 0x01
    LEVEL_CONTROL_MOVE = 0x01
    LEVEL_CONTROL_STEP = 0x02
    LEVEL_CONTROL_STOP = 0x03

    # Color Control Cluster
    COLOR_CONTROL_MOVE_TO_HUE = 0x00
    COLOR_CONTROL_MOVE_HUE = 0x01
    COLOR_CONTROL_STEP_HUE = 0x02
    COLOR_CONTROL_MOVE_TO_SATURATION = 0x03
    COLOR_CONTROL_MOVE_SATURATION = 0x04
    COLOR_CONTROL_STEP_SATURATION = 0x05
    COLOR_CONTROL_MOVE_TO_COLOR = 0x06
    COLOR_CONTROL_MOVE_COLOR = 0x07
    COLOR_CONTROL_STEP_COLOR = 0x08
    COLOR_CONTROL_MOVE_TO_COLOR_TEMPERATURE = 0x0A

class MatterDeviceController:
    """Matter设备控制器"""

    def __init__(self, device_id: str, node_id: int, endpoint_id: int = 1):
        self.device_id = device_id
        self.node_id = node_id
        self.endpoint_id = endpoint_id
        self.connected = False
        self.attribute_subscriptions: Dict[int, Callable] = {}

    async def connect(self) -> bool:
        """连接到Matter设备"""
        try:
            # 这里需要实际的Matter SDK连接代码
            # 使用chip-device-ctrl或Matter SDK
            logger.info(f"Connecting to Matter device {self.device_id}")
            # 模拟连接过程
            await asyncio.sleep(0.1)
            self.connected = True
            logger.info(f"Connected to Matter device {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device {self.device_id}: {e}")
            return False

    async def disconnect(self):
        """断开Matter设备连接"""
        self.connected = False
        self.attribute_subscriptions.clear()
        logger.info(f"Disconnected from Matter device {self.device_id}")

    async def read_attribute(self, cluster_id: int, attribute_id: int) -> Optional[Any]:
        """读取设备属性"""
        if not self.connected:
            raise RuntimeError("Device not connected")

        try:
            # 这里需要实际的Matter SDK属性读取代码
            # 使用chip-device-ctrl读取属性
            logger.debug(f"Reading attribute {attribute_id} from cluster {cluster_id}")
            # 模拟属性读取
            return None
        except Exception as e:
            logger.error(f"Failed to read attribute: {e}")
            return None

    async def write_attribute(self, cluster_id: int, attribute_id: int, value: Any) -> bool:
        """写入设备属性"""
        if not self.connected:
            raise RuntimeError("Device not connected")

        try:
            # 这里需要实际的Matter SDK属性写入代码
            logger.debug(f"Writing attribute {attribute_id} = {value} to cluster {cluster_id}")
            # 模拟属性写入
            return True
        except Exception as e:
            logger.error(f"Failed to write attribute: {e}")
            return False

    async def send_command(self, cluster_id: int, command_id: int,
                          parameters: Dict = None) -> bool:
        """发送命令到设备"""
        if not self.connected:
            raise RuntimeError("Device not connected")

        try:
            # 这里需要实际的Matter SDK命令发送代码
            logger.info(f"Sending command {command_id} to cluster {cluster_id} with {parameters}")
            # 模拟命令发送
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def subscribe_attribute(self, cluster_id: int, attribute_id: int,
                          callback: Callable[[Any], None]):
        """订阅属性变化"""
        key = (cluster_id, attribute_id)
        self.attribute_subscriptions[key] = callback
        logger.info(f"Subscribed to attribute {attribute_id} in cluster {cluster_id}")

class MatterOnOffLightController(MatterDeviceController):
    """Matter On/Off Light控制器"""

    async def turn_on(self) -> bool:
        """打开灯光"""
        return await self.send_command(
            MatterClusterId.ON_OFF,
            MatterCommandId.ON_OFF_ON
        )

    async def turn_off(self) -> bool:
        """关闭灯光"""
        return await self.send_command(
            MatterClusterId.ON_OFF,
            MatterCommandId.ON_OFF_OFF
        )

    async def toggle(self) -> bool:
        """切换灯光状态"""
        return await self.send_command(
            MatterClusterId.ON_OFF,
            MatterCommandId.ON_OFF_TOGGLE
        )

    async def get_state(self) -> Optional[bool]:
        """获取灯光状态"""
        value = await self.read_attribute(
            MatterClusterId.ON_OFF,
            MatterAttributeId.ON_OFF_ON_OFF
        )
        return value if value is not None else None

class MatterDimmableLightController(MatterOnOffLightController):
    """Matter Dimmable Light控制器"""

    async def set_level(self, level: int) -> bool:
        """设置亮度级别（0-254）"""
        if level < 0 or level > 254:
            raise ValueError("Level must be between 0 and 254")

        return await self.send_command(
            MatterClusterId.LEVEL_CONTROL,
            MatterCommandId.LEVEL_CONTROL_MOVE_TO_LEVEL,
            {
                "level": level,
                "transition_time": 0  # 立即切换
            }
        )

    async def get_level(self) -> Optional[int]:
        """获取当前亮度级别"""
        value = await self.read_attribute(
            MatterClusterId.LEVEL_CONTROL,
            MatterAttributeId.LEVEL_CONTROL_CURRENT_LEVEL
        )
        return value if value is not None else None

    async def move_level(self, move_mode: str, rate: int) -> bool:
        """移动亮度级别"""
        # move_mode: "Up" or "Down"
        move_mode_map = {"Up": 0, "Down": 1}
        return await self.send_command(
            MatterClusterId.LEVEL_CONTROL,
            MatterCommandId.LEVEL_CONTROL_MOVE,
            {
                "move_mode": move_mode_map.get(move_mode, 0),
                "rate": rate
            }
        )

class MatterColorLightController(MatterDimmableLightController):
    """Matter Color Light控制器"""

    async def set_hue_saturation(self, hue: int, saturation: int) -> bool:
        """设置色相和饱和度"""
        if hue < 0 or hue > 254:
            raise ValueError("Hue must be between 0 and 254")
        if saturation < 0 or saturation > 254:
            raise ValueError("Saturation must be between 0 and 254")

        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_MOVE_TO_HUE,
            {
                "hue": hue,
                "saturation": saturation,
                "transition_time": 0,
                "options_mask": 0,
                "options_override": 0
            }
        )

    async def set_color_temperature(self, color_temp_mireds: int) -> bool:
        """设置色温（mireds）"""
        if color_temp_mireds < 153 or color_temp_mireds > 500:
            raise ValueError("Color temperature must be between 153 and 500 mireds")

        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_MOVE_TO_COLOR_TEMPERATURE,
            {
                "color_temperature_mireds": color_temp_mireds,
                "transition_time": 0,
                "options_mask": 0,
                "options_override": 0
            }
        )

    async def get_hue_saturation(self) -> Optional[Dict]:
        """获取当前色相和饱和度"""
        hue = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_CURRENT_HUE
        )
        saturation = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_CURRENT_SATURATION
        )

        if hue is not None and saturation is not None:
            return {"hue": hue, "saturation": saturation}
        return None

    async def get_color_temperature(self) -> Optional[int]:
        """获取当前色温"""
        value = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_COLOR_TEMPERATURE_MIREDS
        )
        return value if value is not None else None

class MatterDoorLockController(MatterDeviceController):
    """Matter Door Lock控制器"""

    async def lock_door(self, pin_code: Optional[str] = None) -> bool:
        """锁定门锁"""
        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            0x00,  # LockDoor command
            {"pin_code": pin_code} if pin_code else {}
        )

    async def unlock_door(self, pin_code: Optional[str] = None) -> bool:
        """解锁门锁"""
        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            0x01,  # UnlockDoor command
            {"pin_code": pin_code} if pin_code else {}
        )

    async def get_lock_state(self) -> Optional[str]:
        """获取门锁状态"""
        value = await self.read_attribute(
            MatterClusterId.DOOR_LOCK,
            0x0000  # LockState attribute
        )
        # Matter锁状态：0=NotFullyLocked, 1=Locked, 2=Unlocked
        state_map = {0: "NotFullyLocked", 1: "Locked", 2: "Unlocked"}
        return state_map.get(value, "Unknown") if value is not None else None

class MatterThermostatController(MatterDeviceController):
    """Matter Thermostat控制器"""

    async def set_target_temperature(self, temperature: float, mode: str = "Cool") -> bool:
        """设置目标温度"""
        # 根据模式设置不同的setpoint
        if mode == "Cool":
            return await self.write_attribute(
                MatterClusterId.THERMOSTAT,
                0x0011,  # OccupiedCoolingSetpoint
                int(temperature * 100)  # Matter使用0.01°C单位
            )
        elif mode == "Heat":
            return await self.write_attribute(
                MatterClusterId.THERMOSTAT,
                0x0012,  # OccupiedHeatingSetpoint
                int(temperature * 100)
            )
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    async def get_current_temperature(self) -> Optional[float]:
        """获取当前温度"""
        value = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            0x0000  # LocalTemperature
        )
        return value / 100.0 if value is not None else None

    async def set_system_mode(self, mode: str) -> bool:
        """设置系统模式"""
        # Matter系统模式：0=Off, 1=Auto, 2=Cool, 3=Heat
        mode_map = {"Off": 0, "Auto": 1, "Cool": 2, "Heat": 3}
        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            0x001C,  # SystemMode
            mode_map.get(mode, 1)
        )
```

### 2.2 Matter到Zigbee转换

**转换规则**：

- Matter On/Off Cluster → Zigbee On/Off Cluster
- Matter Level Control Cluster → Zigbee Level Control Cluster
- Matter Color Control Cluster → Zigbee Color Control Cluster
- Matter Door Lock Cluster → Zigbee Door Lock Cluster
- Matter Thermostat Cluster → Zigbee Thermostat Cluster

**完整转换实现**：

详见 `Smart_Home_Schema/04_Transformation.md` 第2章。

---

## 3. Zigbee到Matter转换

**转换规则**：

- Zigbee On/Off Cluster → Matter On/Off Cluster
- Zigbee Level Control Cluster → Matter Level Control Cluster
- Zigbee Color Control Cluster → Matter Color Control Cluster
- Zigbee Door Lock Cluster → Matter Door Lock Cluster
- Zigbee Thermostat Cluster → Matter Thermostat Cluster

**完整转换实现**：

详见 `Smart_Home_Schema/04_Transformation.md` 第3章。

---

## 4. Matter设备发现和管理

### 4.1 设备发现实现

**完整的设备发现实现**：

```python
import asyncio
from typing import List, Dict, Optional
from matter_device_controller import MatterDeviceController

class MatterDeviceDiscovery:
    """Matter设备发现"""

    def __init__(self):
        self.discovered_devices: Dict[str, Dict] = {}

    async def discover_devices(self, timeout: int = 30) -> List[Dict]:
        """发现Matter设备"""
        logger.info("Starting Matter device discovery")

        # 这里需要实际的Matter SDK设备发现代码
        # 使用chip-device-ctrl或Matter SDK进行设备发现
        # 模拟设备发现过程
        devices = []

        # 模拟发现的设备
        sample_devices = [
            {
                "device_id": "LIGHT001",
                "device_type": "OnOffLight",
                "vendor_id": 0x1234,
                "product_id": 0x5678,
                "serial_number": "SN001",
                "firmware_version": "1.0.0"
            },
            {
                "device_id": "LOCK001",
                "device_type": "DoorLock",
                "vendor_id": 0x1234,
                "product_id": 0x5679,
                "serial_number": "SN002",
                "firmware_version": "1.0.0"
            }
        ]

        for device_info in sample_devices:
            devices.append(device_info)
            self.discovered_devices[device_info["device_id"]] = device_info

        logger.info(f"Discovered {len(devices)} Matter devices")
        return devices

    async def get_device_info(self, device_id: str) -> Optional[Dict]:
        """获取设备信息"""
        return self.discovered_devices.get(device_id)

class MatterDeviceManager:
    """Matter设备管理器"""

    def __init__(self, storage):
        self.storage = storage
        self.devices: Dict[str, MatterDeviceController] = {}
        self.discovery = MatterDeviceDiscovery()

    async def discover_and_register(self) -> List[str]:
        """发现并注册设备"""
        discovered = await self.discovery.discover_devices()
        registered_ids = []

        for device_info in discovered:
            # 存储设备信息
            self.storage.store_device(device_info)

            # 创建设备控制器
            controller = self._create_controller(device_info)
            if controller:
                self.devices[device_info["device_id"]] = controller
                registered_ids.append(device_info["device_id"])

        return registered_ids

    def _create_controller(self, device_info: Dict) -> Optional[MatterDeviceController]:
        """根据设备类型创建控制器"""
        device_type = device_info.get("device_type")

        if device_type == "OnOffLight":
            return MatterOnOffLightController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "DimmableLight":
            return MatterDimmableLightController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "ExtendedColorLight":
            return MatterColorLightController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "DoorLock":
            return MatterDoorLockController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "Thermostat":
            return MatterThermostatController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        else:
            logger.warning(f"Unknown device type: {device_type}")
            return None

    async def connect_device(self, device_id: str) -> bool:
        """连接设备"""
        controller = self.devices.get(device_id)
        if not controller:
            logger.error(f"Device {device_id} not found")
            return False

        return await controller.connect()

    async def disconnect_device(self, device_id: str):
        """断开设备连接"""
        controller = self.devices.get(device_id)
        if controller:
            await controller.disconnect()

    def get_controller(self, device_id: str) -> Optional[MatterDeviceController]:
        """获取设备控制器"""
        return self.devices.get(device_id)
```

---

## 5. 转换工具

### 5.1 Matter SDK集成

**Matter SDK Python封装**：

详见 `Smart_Home_Schema/04_Transformation.md` 第5.1章。

### 5.2 CHIP Tool集成

**CHIP Tool命令行封装**：

```python
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class CHIPToolWrapper:
    """CHIP Tool命令行封装"""

    def __init__(self, chip_tool_path: str = "chip-tool"):
        self.chip_tool_path = chip_tool_path

    def read_attribute(self, node_id: int, endpoint_id: int,
                      cluster_name: str, attribute_name: str) -> Optional[Any]:
        """读取属性"""
        cmd = [
            self.chip_tool_path,
            "read",
            cluster_name,
            attribute_name,
            str(node_id),
            str(endpoint_id)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # 解析输出
                return self._parse_output(result.stdout)
            else:
                logger.error(f"CHIP Tool error: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Failed to read attribute: {e}")
            return None

    def write_attribute(self, node_id: int, endpoint_id: int,
                       cluster_name: str, attribute_name: str, value: Any) -> bool:
        """写入属性"""
        cmd = [
            self.chip_tool_path,
            "write",
            cluster_name,
            attribute_name,
            str(value),
            str(node_id),
            str(endpoint_id)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to write attribute: {e}")
            return False

    def send_command(self, node_id: int, endpoint_id: int,
                    cluster_name: str, command_name: str, *args) -> bool:
        """发送命令"""
        cmd = [
            self.chip_tool_path,
            cluster_name,
            command_name,
            str(node_id),
            str(endpoint_id),
            *[str(arg) for arg in args]
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def _parse_output(self, output: str) -> Optional[Any]:
        """解析CHIP Tool输出"""
        # 这里需要根据CHIP Tool的实际输出格式进行解析
        # 示例：解析JSON格式的输出
        try:
            # 尝试提取JSON部分
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start:json_end]
                data = json.loads(json_str)
                return data.get("value")
        except Exception as e:
            logger.error(f"Failed to parse output: {e}")
        return None
```

---

## 6. 转换验证

### 6.1 转换正确性验证

**转换验证器实现**：

详见 `Smart_Home_Schema/04_Transformation.md` 第6章。

### 6.2 设备控制验证

**设备控制测试**：

```python
import pytest
from matter_device_controller import (
    MatterOnOffLightController,
    MatterDimmableLightController,
    MatterColorLightController
)

@pytest.mark.asyncio
async def test_on_off_light_control():
    """测试On/Off Light控制"""
    controller = MatterOnOffLightController("LIGHT001", 0x12344321)
    await controller.connect()

    # 测试打开
    result = await controller.turn_on()
    assert result == True

    # 测试获取状态
    state = await controller.get_state()
    assert state == True

    # 测试关闭
    result = await controller.turn_off()
    assert result == True

    # 测试切换
    result = await controller.toggle()
    assert result == True

    await controller.disconnect()

@pytest.mark.asyncio
async def test_dimmable_light_control():
    """测试Dimmable Light控制"""
    controller = MatterDimmableLightController("LIGHT002", 0x12344322)
    await controller.connect()

    # 测试设置亮度
    result = await controller.set_level(128)
    assert result == True

    # 测试获取亮度
    level = await controller.get_level()
    assert level == 128

    # 测试移动亮度
    result = await controller.move_level("Up", 10)
    assert result == True

    await controller.disconnect()

@pytest.mark.asyncio
async def test_color_light_control():
    """测试Color Light控制"""
    controller = MatterColorLightController("LIGHT003", 0x12344323)
    await controller.connect()

    # 测试设置色相和饱和度
    result = await controller.set_hue_saturation(120, 200)
    assert result == True

    # 测试设置色温
    result = await controller.set_color_temperature(400)
    assert result == True

    # 测试获取色温
    color_temp = await controller.get_color_temperature()
    assert color_temp == 400

    await controller.disconnect()
```

---

## 7. Matter数据存储与分析

### 7.1 PostgreSQL Matter数据存储

**Matter数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class MatterStorage:
    """Matter数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建Matter数据表"""
        # Matter设备表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_devices (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) UNIQUE NOT NULL,
                device_type VARCHAR(50) NOT NULL,
                device_name VARCHAR(100) NOT NULL,
                vendor_id INTEGER,
                product_id INTEGER,
                serial_number VARCHAR(100),
                firmware_version VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Matter集群表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_clusters (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                cluster_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id),
                UNIQUE(device_id, endpoint_id, cluster_id)
            )
        """)

        # Matter属性表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_attributes (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                attribute_id INTEGER NOT NULL,
                attribute_name VARCHAR(100),
                attribute_value JSONB,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id),
                UNIQUE(device_id, endpoint_id, cluster_id, attribute_id)
            )
        """)

        # Matter命令表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_commands (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                command_id INTEGER NOT NULL,
                command_name VARCHAR(100),
                command_parameters JSONB,
                command_status VARCHAR(20) DEFAULT 'Pending',
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # Matter事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                event_name VARCHAR(100),
                event_data JSONB,
                event_time TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_devices_device_id
            ON matter_devices(device_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_clusters_device_id
            ON matter_clusters(device_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_attributes_device_id
            ON matter_attributes(device_id, updated_at DESC)
        """)

        self.conn.commit()

    def store_device(self, device_data: Dict) -> int:
        """存储Matter设备"""
        self.cur.execute("""
            INSERT INTO matter_devices (
                device_id, device_type, device_name, vendor_id,
                product_id, serial_number, firmware_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE SET
                device_type = EXCLUDED.device_type,
                device_name = EXCLUDED.device_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            device_data.get("device_id"),
            device_data.get("device_type"),
            device_data.get("device_name"),
            device_data.get("vendor_id"),
            device_data.get("product_id"),
            device_data.get("serial_number"),
            device_data.get("firmware_version")
        ))
        return self.cur.fetchone()[0]

    def store_attribute(self, device_id: str, endpoint_id: int,
                       cluster_id: int, attribute_id: int,
                       attribute_name: str, attribute_value: Dict) -> int:
        """存储Matter属性"""
        self.cur.execute("""
            INSERT INTO matter_attributes (
                device_id, endpoint_id, cluster_id, attribute_id,
                attribute_name, attribute_value
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, endpoint_id, cluster_id, attribute_id)
            DO UPDATE SET
                attribute_value = EXCLUDED.attribute_value,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (device_id, endpoint_id, cluster_id, attribute_id,
              attribute_name, json.dumps(attribute_value)))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_command(self, device_id: str, endpoint_id: int,
                     cluster_id: int, command_id: int,
                     command_name: str, parameters: Dict = None) -> int:
        """存储Matter命令"""
        self.cur.execute("""
            INSERT INTO matter_commands (
                device_id, endpoint_id, cluster_id, command_id,
                command_name, command_parameters, command_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'Pending', CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            device_id, endpoint_id, cluster_id, command_id,
            command_name, json.dumps(parameters or {})
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update_command_status(self, command_db_id: int, status: str):
        """更新命令状态"""
        self.cur.execute("""
            UPDATE matter_commands
            SET command_status = %s, executed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (status, command_db_id))
        self.conn.commit()

    def store_event(self, device_id: str, endpoint_id: int,
                   cluster_id: int, event_id: int,
                   event_name: str, event_data: Dict = None) -> int:
        """存储Matter事件"""
        self.cur.execute("""
            INSERT INTO matter_events (
                device_id, endpoint_id, cluster_id, event_id,
                event_name, event_data, event_time
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            device_id, endpoint_id, cluster_id, event_id,
            event_name, json.dumps(event_data or {})
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_device_clusters(self, device_id: str) -> List[Dict]:
        """获取设备的所有集群"""
        self.cur.execute("""
            SELECT cluster_id, cluster_name, endpoint_id
            FROM matter_clusters
            WHERE device_id = %s
            ORDER BY endpoint_id, cluster_id
        """, (device_id,))
        return [
            {
                "cluster_id": row[0],
                "cluster_name": row[1],
                "endpoint_id": row[2]
            }
            for row in self.cur.fetchall()
        ]

    def get_cluster_attributes(self, device_id: str, endpoint_id: int,
                              cluster_id: int) -> List[Dict]:
        """获取集群的所有属性"""
        self.cur.execute("""
            SELECT attribute_id, attribute_name, attribute_value, updated_at
            FROM matter_attributes
            WHERE device_id = %s AND endpoint_id = %s AND cluster_id = %s
            ORDER BY attribute_id
        """, (device_id, endpoint_id, cluster_id))
        return [
            {
                "attribute_id": row[0],
                "attribute_name": row[1],
                "attribute_value": json.loads(row[2]) if row[2] else None,
                "updated_at": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 Matter数据分析查询

**查询示例**：

```python
    def get_cluster_statistics(self, device_id: str) -> List[Dict]:
        """查询设备集群统计"""
        self.cur.execute("""
            SELECT
                c.cluster_id,
                c.cluster_name,
                COUNT(DISTINCT a.attribute_id) as attribute_count,
                COUNT(DISTINCT cmd.command_id) as command_count,
                MAX(a.updated_at) as last_attribute_update
            FROM matter_clusters c
            LEFT JOIN matter_attributes a
            ON c.device_id = a.device_id AND c.cluster_id = a.cluster_id
            LEFT JOIN matter_commands cmd
            ON c.device_id = cmd.device_id AND c.cluster_id = cmd.cluster_id
            WHERE c.device_id = %s
            GROUP BY c.cluster_id, c.cluster_name
            ORDER BY c.cluster_id
        """, (device_id,))
        return [
            {
                "cluster_id": row[0],
                "cluster_name": row[1],
                "attribute_count": row[2],
                "command_count": row[3],
                "last_attribute_update": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_command_statistics(self, start_time: datetime) -> List[Dict]:
        """查询命令执行统计"""
        self.cur.execute("""
            SELECT
                command_name,
                command_status,
                COUNT(*) as count,
                AVG(EXTRACT(EPOCH FROM (executed_at - created_at))) as avg_execution_time_seconds,
                MIN(EXTRACT(EPOCH FROM (executed_at - created_at))) as min_execution_time_seconds,
                MAX(EXTRACT(EPOCH FROM (executed_at - created_at))) as max_execution_time_seconds
            FROM matter_commands
            WHERE created_at >= %s AND executed_at IS NOT NULL
            GROUP BY command_name, command_status
            ORDER BY command_name, command_status
        """, (start_time,))
        return [
            {
                "command_name": row[0],
                "command_status": row[1],
                "count": row[2],
                "avg_execution_time": row[3],
                "min_execution_time": row[4],
                "max_execution_time": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def get_device_event_statistics(self, device_id: str, days: int = 7) -> List[Dict]:
        """查询设备事件统计"""
        self.cur.execute("""
            SELECT
                event_name,
                COUNT(*) as event_count,
                MIN(event_time) as first_event,
                MAX(event_time) as last_event
            FROM matter_events
            WHERE device_id = %s
            AND event_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY event_name
            ORDER BY event_count DESC
        """, (device_id, days))
        return [
            {
                "event_name": row[0],
                "event_count": row[1],
                "first_event": row[2],
                "last_event": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def get_attribute_history(self, device_id: str, endpoint_id: int,
                             cluster_id: int, attribute_id: int,
                             hours: int = 24) -> List[Dict]:
        """查询属性历史变化"""
        # 注意：这里需要属性历史表，当前实现仅查询最新值
        self.cur.execute("""
            SELECT
                attribute_name,
                attribute_value,
                updated_at
            FROM matter_attributes
            WHERE device_id = %s
            AND endpoint_id = %s
            AND cluster_id = %s
            AND attribute_id = %s
            AND updated_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
            ORDER BY updated_at DESC
        """, (device_id, endpoint_id, cluster_id, attribute_id, hours))
        return [
            {
                "attribute_name": row[0],
                "attribute_value": json.loads(row[1]) if row[1] else None,
                "updated_at": row[2]
            }
            for row in self.cur.fetchall()
        ]

    def get_device_usage_statistics(self, device_id: str, days: int = 7) -> Dict:
        """查询设备使用统计"""
        self.cur.execute("""
            SELECT
                COUNT(DISTINCT DATE(created_at)) as active_days,
                COUNT(*) as total_commands,
                COUNT(CASE WHEN command_status = 'Success' THEN 1 END) as success_commands,
                COUNT(CASE WHEN command_status = 'Failed' THEN 1 END) as failed_commands,
                AVG(EXTRACT(EPOCH FROM (executed_at - created_at))) as avg_response_time_seconds
            FROM matter_commands
            WHERE device_id = %s
            AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND executed_at IS NOT NULL
        """, (device_id, days))
        row = self.cur.fetchone()
        return {
            "active_days": row[0],
            "total_commands": row[1],
            "success_commands": row[2],
            "failed_commands": row[3],
            "avg_response_time": row[4]
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
