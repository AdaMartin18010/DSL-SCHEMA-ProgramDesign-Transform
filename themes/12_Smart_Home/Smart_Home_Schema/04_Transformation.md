# 智慧家居Schema转换体系

## 📑 目录

- [智慧家居Schema转换体系](#智慧家居schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Matter到Zigbee转换](#2-matter到zigbee转换)
  - [3. Zigbee到Matter转换](#3-zigbee到matter转换)
  - [4. 场景联动系统](#4-场景联动系统)
    - [4.1 场景定义Schema](#41-场景定义schema)
    - [4.2 场景联动示例](#42-场景联动示例)
  - [5. 转换工具](#5-转换工具)
    - [5.1 Matter SDK集成](#51-matter-sdk集成)
    - [5.2 Zigbee2MQTT集成](#52-zigbee2mqtt集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 转换正确性验证](#61-转换正确性验证)
  - [7. 智慧家居数据存储与分析](#7-智慧家居数据存储与分析)
    - [7.1 PostgreSQL智慧家居数据存储](#71-postgresql智慧家居数据存储)
    - [7.2 智慧家居数据分析查询](#72-智慧家居数据分析查询)

---

## 1. 转换体系概述

智慧家居Schema转换体系支持Matter设备、Zigbee设备、
数据库存储之间的转换。

### 1.1 转换目标

1. **Matter到Zigbee转换**：Matter设备到Zigbee设备
2. **Zigbee到Matter转换**：Zigbee设备到Matter设备
3. **数据到数据库转换**：智慧家居数据到PostgreSQL存储

---

## 2. Matter到Zigbee转换

**转换规则**：

- Matter On/Off Light → Zigbee On/Off Light
- Matter Dimmable Light → Zigbee Dimmable Light
- Matter Extended Color Light → Zigbee Color Light
- Matter Door Lock → Zigbee Door Lock
- Matter Thermostat → Zigbee Thermostat

**完整转换实现**：

```python
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class MatterDeviceType(Enum):
    """Matter设备类型"""
    ON_OFF_LIGHT = "OnOffLight"
    DIMMABLE_LIGHT = "DimmableLight"
    COLOR_LIGHT = "ColorLight"
    EXTENDED_COLOR_LIGHT = "ExtendedColorLight"
    DOOR_LOCK = "DoorLock"
    THERMOSTAT = "Thermostat"
    WINDOW_COVERING = "WindowCovering"

class ZigbeeCluster(Enum):
    """Zigbee集群类型"""
    ON_OFF = "OnOff"
    LEVEL_CONTROL = "LevelControl"
    COLOR_CONTROL = "ColorControl"
    DOOR_LOCK = "DoorLock"
    THERMOSTAT = "Thermostat"
    WINDOW_COVERING = "WindowCovering"

class MatterToZigbeeConverter:
    """Matter到Zigbee转换器"""

    # Matter集群ID到Zigbee集群映射
    CLUSTER_MAPPING = {
        0x0006: ZigbeeCluster.ON_OFF,  # On/Off Cluster
        0x0008: ZigbeeCluster.LEVEL_CONTROL,  # Level Control Cluster
        0x0300: ZigbeeCluster.COLOR_CONTROL,  # Color Control Cluster
        0x0101: ZigbeeCluster.DOOR_LOCK,  # Door Lock Cluster
        0x0201: ZigbeeCluster.THERMOSTAT,  # Thermostat Cluster
        0x0102: ZigbeeCluster.WINDOW_COVERING,  # Window Covering Cluster
    }

    def __init__(self):
        self.conversion_log = []

    def convert_device(self, matter_device: Dict) -> Dict:
        """将Matter设备转换为Zigbee设备"""
        device_type = matter_device.get("device_type")

        if device_type == MatterDeviceType.ON_OFF_LIGHT.value:
            return self._convert_on_off_light(matter_device)
        elif device_type == MatterDeviceType.DIMMABLE_LIGHT.value:
            return self._convert_dimmable_light(matter_device)
        elif device_type == MatterDeviceType.EXTENDED_COLOR_LIGHT.value:
            return self._convert_color_light(matter_device)
        elif device_type == MatterDeviceType.DOOR_LOCK.value:
            return self._convert_door_lock(matter_device)
        elif device_type == MatterDeviceType.THERMOSTAT.value:
            return self._convert_thermostat(matter_device)
        else:
            raise ValueError(f"Unsupported Matter device type: {device_type}")

    def _convert_on_off_light(self, matter_device: Dict) -> Dict:
        """转换On/Off Light设备"""
        zigbee_device = {
            "ieee_address": matter_device.get("device_id", ""),
            "network_address": self._generate_network_address(matter_device.get("device_id")),
            "endpoint": matter_device.get("endpoint_id", 1),
            "clusters": []
        }

        # 转换On/Off Cluster
        on_off_cluster = {
            "cluster": "OnOff",
            "attributes": {}
        }

        # 转换开关状态
        power_state = matter_device.get("state", {}).get("power", "Off")
        on_off_cluster["attributes"]["OnOff"] = (power_state == "On")

        zigbee_device["clusters"].append(on_off_cluster)

        self.conversion_log.append({
            "device_id": matter_device.get("device_id"),
            "conversion_type": "OnOffLight",
            "timestamp": datetime.now().isoformat()
        })

        return zigbee_device

    def _convert_dimmable_light(self, matter_device: Dict) -> Dict:
        """转换Dimmable Light设备"""
        zigbee_device = self._convert_on_off_light(matter_device)

        # 添加Level Control Cluster
        level_cluster = {
            "cluster": "LevelControl",
            "attributes": {}
        }

        # 转换亮度（Matter: 0-254, Zigbee: 0-254）
        brightness = matter_device.get("state", {}).get("brightness", 0)
        level_cluster["attributes"]["CurrentLevel"] = max(0, min(254, brightness))

        zigbee_device["clusters"].append(level_cluster)

        return zigbee_device

    def _convert_color_light(self, matter_device: Dict) -> Dict:
        """转换Extended Color Light设备"""
        zigbee_device = self._convert_dimmable_light(matter_device)

        # 添加Color Control Cluster
        color_cluster = {
            "cluster": "ColorControl",
            "attributes": {}
        }

        state = matter_device.get("state", {})

        # 转换色温
        if "color_temperature" in state:
            color_temp = state["color_temperature"]
            # Matter色温范围：153-500 mireds
            # Zigbee色温范围：0-65279 (0xFEFF)
            zigbee_temp = int((color_temp - 153) / (500 - 153) * 65279)
            color_cluster["attributes"]["ColorTemperatureMireds"] = max(0, min(65279, zigbee_temp))

        # 转换RGB颜色
        if "color_rgb" in state:
            rgb = state["color_rgb"]
            # 转换RGB到HSV，再转换到Zigbee Hue/Saturation
            hue, saturation = self._rgb_to_hue_saturation(
                rgb.get("red", 0),
                rgb.get("green", 0),
                rgb.get("blue", 0)
            )
            color_cluster["attributes"]["CurrentHue"] = hue
            color_cluster["attributes"]["CurrentSaturation"] = saturation

        zigbee_device["clusters"].append(color_cluster)

        return zigbee_device

    def _convert_door_lock(self, matter_device: Dict) -> Dict:
        """转换Door Lock设备"""
        zigbee_device = {
            "ieee_address": matter_device.get("device_id", ""),
            "network_address": self._generate_network_address(matter_device.get("device_id")),
            "endpoint": matter_device.get("endpoint_id", 1),
            "clusters": [{
                "cluster": "DoorLock",
                "attributes": {}
            }]
        }

        lock_state = matter_device.get("door_lock_state", {}).get("lock_state", "Unknown")

        # 转换锁状态
        # Matter: Locked, Unlocked, Unknown
        # Zigbee: 0=NotFullyLocked, 1=Locked, 2=Unlocked
        if lock_state == "Locked":
            zigbee_device["clusters"][0]["attributes"]["LockState"] = 1
        elif lock_state == "Unlocked":
            zigbee_device["clusters"][0]["attributes"]["LockState"] = 2
        else:
            zigbee_device["clusters"][0]["attributes"]["LockState"] = 0

        return zigbee_device

    def _convert_thermostat(self, matter_device: Dict) -> Dict:
        """转换Thermostat设备"""
        zigbee_device = {
            "ieee_address": matter_device.get("device_id", ""),
            "network_address": self._generate_network_address(matter_device.get("device_id")),
            "endpoint": matter_device.get("endpoint_id", 1),
            "clusters": [{
                "cluster": "Thermostat",
                "attributes": {}
            }]
        }

        state = matter_device.get("state", {})

        # 转换当前温度（Matter: Celsius, Zigbee: 0.01°C）
        if "current_temperature" in state:
            temp_celsius = state["current_temperature"]
            zigbee_device["clusters"][0]["attributes"]["LocalTemperature"] = int(temp_celsius * 100)

        # 转换目标温度
        if "target_temperature" in state:
            target_temp = state["target_temperature"]
            zigbee_device["clusters"][0]["attributes"]["OccupiedCoolingSetpoint"] = int(target_temp * 100)
            zigbee_device["clusters"][0]["attributes"]["OccupiedHeatingSetpoint"] = int(target_temp * 100)

        # 转换运行模式
        operation_mode = state.get("operation_mode", "Cool")
        # Matter: Off, Heat, Cool, Auto
        # Zigbee: 0=Off, 1=Auto, 2=Cool, 3=Heat
        mode_map = {"Off": 0, "Auto": 1, "Cool": 2, "Heat": 3}
        zigbee_device["clusters"][0]["attributes"]["SystemMode"] = mode_map.get(operation_mode, 1)

        return zigbee_device

    def _rgb_to_hue_saturation(self, r: int, g: int, b: int) -> tuple:
        """将RGB转换为Hue和Saturation"""
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val

        # 计算亮度（Value）
        v = max_val

        # 计算饱和度
        if max_val == 0:
            s = 0
        else:
            s = delta / max_val

        # 计算色相
        if delta == 0:
            h = 0
        elif max_val == r:
            h = 60 * (((g - b) / delta) % 6)
        elif max_val == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)

        # 转换到Zigbee范围（Hue: 0-254, Saturation: 0-254）
        hue = int((h / 360.0) * 254)
        saturation = int(s * 254)

        return (max(0, min(254, hue)), max(0, min(254, saturation)))

    def _generate_network_address(self, device_id: str) -> int:
        """生成Zigbee网络地址"""
        # 简单的哈希算法生成网络地址
        hash_val = hash(device_id) & 0xFFFF
        return hash_val

    def get_conversion_log(self) -> List[Dict]:
        """获取转换日志"""
        return self.conversion_log
```

---

## 3. Zigbee到Matter转换

**转换规则**：

- Zigbee On/Off Light → Matter On/Off Light
- Zigbee Dimmable Light → Matter Dimmable Light
- Zigbee Color Light → Matter Extended Color Light
- Zigbee Door Lock → Matter Door Lock
- Zigbee Thermostat → Matter Thermostat

**完整转换实现**：

```python
class ZigbeeToMatterConverter:
    """Zigbee到Matter转换器"""

    def __init__(self):
        self.conversion_log = []

    def convert_device(self, zigbee_device: Dict) -> Dict:
        """将Zigbee设备转换为Matter设备"""
        clusters = [c.get("cluster") for c in zigbee_device.get("clusters", [])]

        # 根据集群判断设备类型
        if "ColorControl" in clusters:
            return self._convert_color_light(zigbee_device)
        elif "LevelControl" in clusters:
            return self._convert_dimmable_light(zigbee_device)
        elif "OnOff" in clusters:
            return self._convert_on_off_light(zigbee_device)
        elif "DoorLock" in clusters:
            return self._convert_door_lock(zigbee_device)
        elif "Thermostat" in clusters:
            return self._convert_thermostat(zigbee_device)
        else:
            raise ValueError(f"Unsupported Zigbee device clusters: {clusters}")

    def _convert_on_off_light(self, zigbee_device: Dict) -> Dict:
        """转换On/Off Light设备"""
        matter_device = {
            "device_id": zigbee_device.get("ieee_address", ""),
            "device_type": MatterDeviceType.ON_OFF_LIGHT.value,
            "endpoint_id": zigbee_device.get("endpoint", 1),
            "state": {}
        }

        # 查找OnOff集群
        on_off_cluster = self._find_cluster(zigbee_device, "OnOff")
        if on_off_cluster:
            on_off_state = on_off_cluster.get("attributes", {}).get("OnOff", False)
            matter_device["state"]["power"] = "On" if on_off_state else "Off"

        return matter_device

    def _convert_dimmable_light(self, zigbee_device: Dict) -> Dict:
        """转换Dimmable Light设备"""
        matter_device = self._convert_on_off_light(zigbee_device)
        matter_device["device_type"] = MatterDeviceType.DIMMABLE_LIGHT.value

        # 查找Level Control集群
        level_cluster = self._find_cluster(zigbee_device, "LevelControl")
        if level_cluster:
            current_level = level_cluster.get("attributes", {}).get("CurrentLevel", 0)
            matter_device["state"]["brightness"] = max(0, min(254, current_level))

        return matter_device

    def _convert_color_light(self, zigbee_device: Dict) -> Dict:
        """转换Color Light设备"""
        matter_device = self._convert_dimmable_light(zigbee_device)
        matter_device["device_type"] = MatterDeviceType.EXTENDED_COLOR_LIGHT.value

        # 查找Color Control集群
        color_cluster = self._find_cluster(zigbee_device, "ColorControl")
        if color_cluster:
            attributes = color_cluster.get("attributes", {})

            # 转换色温
            if "ColorTemperatureMireds" in attributes:
                zigbee_temp = attributes["ColorTemperatureMireds"]
                # Zigbee: 0-65279, Matter: 153-500 mireds
                matter_temp = int(153 + (zigbee_temp / 65279.0) * (500 - 153))
                matter_device["state"]["color_temperature"] = max(153, min(500, matter_temp))

            # 转换Hue和Saturation到RGB
            if "CurrentHue" in attributes and "CurrentSaturation" in attributes:
                hue = attributes["CurrentHue"]
                saturation = attributes["CurrentSaturation"]
                rgb = self._hue_saturation_to_rgb(hue, saturation)
                matter_device["state"]["color_rgb"] = rgb

        return matter_device

    def _convert_door_lock(self, zigbee_device: Dict) -> Dict:
        """转换Door Lock设备"""
        matter_device = {
            "device_id": zigbee_device.get("ieee_address", ""),
            "device_type": MatterDeviceType.DOOR_LOCK.value,
            "endpoint_id": zigbee_device.get("endpoint", 1),
            "door_lock_state": {}
        }

        # 查找Door Lock集群
        lock_cluster = self._find_cluster(zigbee_device, "DoorLock")
        if lock_cluster:
            lock_state = lock_cluster.get("attributes", {}).get("LockState", 0)
            # Zigbee: 0=NotFullyLocked, 1=Locked, 2=Unlocked
            # Matter: Locked, Unlocked, Unknown
            if lock_state == 1:
                matter_device["door_lock_state"]["lock_state"] = "Locked"
            elif lock_state == 2:
                matter_device["door_lock_state"]["lock_state"] = "Unlocked"
            else:
                matter_device["door_lock_state"]["lock_state"] = "Unknown"

        return matter_device

    def _convert_thermostat(self, zigbee_device: Dict) -> Dict:
        """转换Thermostat设备"""
        matter_device = {
            "device_id": zigbee_device.get("ieee_address", ""),
            "device_type": MatterDeviceType.THERMOSTAT.value,
            "endpoint_id": zigbee_device.get("endpoint", 1),
            "state": {}
        }

        # 查找Thermostat集群
        thermostat_cluster = self._find_cluster(zigbee_device, "Thermostat")
        if thermostat_cluster:
            attributes = thermostat_cluster.get("attributes", {})

            # 转换当前温度（Zigbee: 0.01°C, Matter: Celsius）
            if "LocalTemperature" in attributes:
                temp_centidegrees = attributes["LocalTemperature"]
                matter_device["state"]["current_temperature"] = temp_centidegrees / 100.0

            # 转换目标温度
            if "OccupiedCoolingSetpoint" in attributes:
                cooling_setpoint = attributes["OccupiedCoolingSetpoint"]
                matter_device["state"]["target_temperature"] = cooling_setpoint / 100.0

            # 转换运行模式
            system_mode = attributes.get("SystemMode", 1)
            # Zigbee: 0=Off, 1=Auto, 2=Cool, 3=Heat
            # Matter: Off, Heat, Cool, Auto
            mode_map = {0: "Off", 1: "Auto", 2: "Cool", 3: "Heat"}
            matter_device["state"]["operation_mode"] = mode_map.get(system_mode, "Auto")

        return matter_device

    def _find_cluster(self, zigbee_device: Dict, cluster_name: str) -> Optional[Dict]:
        """查找指定的集群"""
        for cluster in zigbee_device.get("clusters", []):
            if cluster.get("cluster") == cluster_name:
                return cluster
        return None

    def _hue_saturation_to_rgb(self, hue: int, saturation: int) -> Dict:
        """将Hue和Saturation转换为RGB"""
        h = (hue / 254.0) * 360.0
        s = saturation / 254.0
        v = 1.0  # 假设亮度为最大值

        c = v * s
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = v - c

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return {
            "red": int((r + m) * 255),
            "green": int((g + m) * 255),
            "blue": int((b + m) * 255)
        }

    def get_conversion_log(self) -> List[Dict]:
        """获取转换日志"""
        return self.conversion_log
```

---

## 4. 场景联动系统

### 4.1 场景定义Schema

**场景联动系统**支持基于条件的设备联动控制。

**场景定义Schema**：

```python
from typing import Dict, List, Callable
from datetime import datetime, time
import json

class SceneCondition:
    """场景触发条件"""

    def __init__(self, device_id: str, attribute: str, operator: str, value: Any):
        self.device_id = device_id
        self.attribute = attribute
        self.operator = operator  # ==, !=, >, <, >=, <=
        self.value = value

    def evaluate(self, device_state: Dict) -> bool:
        """评估条件是否满足"""
        current_value = device_state.get(self.attribute)

        if self.operator == "==":
            return current_value == self.value
        elif self.operator == "!=":
            return current_value != self.value
        elif self.operator == ">":
            return current_value > self.value
        elif self.operator == "<":
            return current_value < self.value
        elif self.operator == ">=":
            return current_value >= self.value
        elif self.operator == "<=":
            return current_value <= self.value
        else:
            return False

class SceneAction:
    """场景执行动作"""

    def __init__(self, device_id: str, command: str, parameters: Dict):
        self.device_id = device_id
        self.command = command
        self.parameters = parameters

class SmartHomeScene:
    """智慧家居场景"""

    def __init__(self, scene_id: str, scene_name: str,
                 conditions: List[SceneCondition], actions: List[SceneAction]):
        self.scene_id = scene_id
        self.scene_name = scene_name
        self.conditions = conditions
        self.actions = actions
        self.enabled = True
        self.created_at = datetime.now()

    def trigger(self, device_states: Dict[str, Dict]) -> bool:
        """触发场景执行"""
        if not self.enabled:
            return False

        # 检查所有条件是否满足
        for condition in self.conditions:
            device_state = device_states.get(condition.device_id, {})
            if not condition.evaluate(device_state):
                return False

        # 执行所有动作
        for action in self.actions:
            self._execute_action(action)

        return True

    def _execute_action(self, action: SceneAction):
        """执行动作"""
        # 这里应该调用实际的设备控制API
        logger.info(f"Executing action: {action.device_id} -> {action.command} with {action.parameters}")

class SceneManager:
    """场景管理器"""

    def __init__(self, storage):
        self.storage = storage
        self.scenes: Dict[str, SmartHomeScene] = {}
        self.device_states: Dict[str, Dict] = {}
        self._load_scenes()

    def _load_scenes(self):
        """从数据库加载场景"""
        scenes_data = self.storage.get_all_scenes()
        for scene_data in scenes_data:
            conditions = [
                SceneCondition(**c) for c in scene_data.get("conditions", [])
            ]
            actions = [
                SceneAction(**a) for a in scene_data.get("actions", [])
            ]
            scene = SmartHomeScene(
                scene_data["scene_id"],
                scene_data["scene_name"],
                conditions,
                actions
            )
            self.scenes[scene_data["scene_id"]] = scene

    def create_scene(self, scene_id: str, scene_name: str,
                     conditions: List[Dict], actions: List[Dict]) -> str:
        """创建场景"""
        scene_conditions = [SceneCondition(**c) for c in conditions]
        scene_actions = [SceneAction(**a) for a in actions]

        scene = SmartHomeScene(scene_id, scene_name, scene_conditions, scene_actions)
        self.scenes[scene_id] = scene

        # 保存到数据库
        self.storage.store_scene({
            "scene_id": scene_id,
            "scene_name": scene_name,
            "conditions": conditions,
            "actions": actions,
            "enabled": True
        })

        return scene_id

    def update_device_state(self, device_id: str, state: Dict):
        """更新设备状态并检查场景触发"""
        self.device_states[device_id] = state

        # 检查所有场景
        for scene in self.scenes.values():
            if scene.enabled:
                scene.trigger(self.device_states)

    def execute_scene(self, scene_id: str) -> bool:
        """手动执行场景"""
        scene = self.scenes.get(scene_id)
        if not scene:
            return False

        return scene.trigger(self.device_states)
```

### 4.2 场景联动示例

**回家场景**：

```python
# 创建回家场景
scene_manager.create_scene(
    scene_id="scene_home_arrival",
    scene_name="回家场景",
    conditions=[
        {
            "device_id": "SENSOR001",
            "attribute": "motion_detected",
            "operator": "==",
            "value": True
        }
    ],
    actions=[
        {
            "device_id": "LIGHT001",
            "command": "turn_on",
            "parameters": {"brightness": 80}
        },
        {
            "device_id": "AC001",
            "command": "set_temperature",
            "parameters": {"temperature": 26}
        },
        {
            "device_id": "MUSIC001",
            "command": "play",
            "parameters": {"playlist": "welcome"}
        }
    ]
)
```

---

## 5. 转换工具

### 5.1 Matter SDK集成

**Matter SDK Python封装**：

```python
import chip.clusters as Clusters
from chip import ChipDeviceCtrl
from chip.clusters.Attribute import AttributePath, AttributeReadResult

class MatterSDKWrapper:
    """Matter SDK封装类"""

    def __init__(self, node_id: int = 0x12344321):
        self.device_ctrl = ChipDeviceCtrl.ChipDeviceController()
        self.node_id = node_id

    def discover_devices(self) -> List[Dict]:
        """发现Matter设备"""
        devices = []
        # 使用Matter SDK发现设备
        # 这里需要实际的Matter SDK调用
        return devices

    def read_attribute(self, device_id: str, endpoint_id: int,
                      cluster_id: int, attribute_id: int) -> Any:
        """读取设备属性"""
        # 使用Matter SDK读取属性
        # 这里需要实际的Matter SDK调用
        pass

    def write_attribute(self, device_id: str, endpoint_id: int,
                       cluster_id: int, attribute_id: int, value: Any):
        """写入设备属性"""
        # 使用Matter SDK写入属性
        # 这里需要实际的Matter SDK调用
        pass

    def send_command(self, device_id: str, endpoint_id: int,
                    cluster_id: int, command_id: int, parameters: Dict):
        """发送命令"""
        # 使用Matter SDK发送命令
        # 这里需要实际的Matter SDK调用
        pass
```

### 5.2 Zigbee2MQTT集成

**Zigbee2MQTT API封装**：

```python
import requests
import json

class Zigbee2MQTTWrapper:
    """Zigbee2MQTT API封装类"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    def get_devices(self) -> List[Dict]:
        """获取所有Zigbee设备"""
        response = requests.get(f"{self.base_url}/api/devices")
        return response.json()

    def get_device_state(self, device_id: str) -> Dict:
        """获取设备状态"""
        response = requests.get(f"{self.base_url}/api/devices/{device_id}")
        return response.json()

    def set_device_state(self, device_id: str, state: Dict):
        """设置设备状态"""
        response = requests.post(
            f"{self.base_url}/api/devices/{device_id}/set",
            json=state
        )
        return response.json()
```

---

## 6. 转换验证

### 6.1 转换正确性验证

**转换验证器实现**：

```python
class ConversionValidator:
    """转换验证器"""

    def validate_matter_to_zigbee(self, matter_device: Dict,
                                  zigbee_device: Dict) -> bool:
        """验证Matter到Zigbee转换的正确性"""
        # 验证设备ID一致性
        if matter_device.get("device_id") != zigbee_device.get("ieee_address"):
            return False

        # 验证状态一致性
        matter_power = matter_device.get("state", {}).get("power", "Off")
        zigbee_onoff = zigbee_device.get("clusters", [{}])[0].get("attributes", {}).get("OnOff", False)

        if (matter_power == "On" and not zigbee_onoff) or \
           (matter_power == "Off" and zigbee_onoff):
            return False

        return True

    def validate_zigbee_to_matter(self, zigbee_device: Dict,
                                  matter_device: Dict) -> bool:
        """验证Zigbee到Matter转换的正确性"""
        # 验证设备ID一致性
        if zigbee_device.get("ieee_address") != matter_device.get("device_id"):
            return False

        # 验证状态一致性
        zigbee_onoff = zigbee_device.get("clusters", [{}])[0].get("attributes", {}).get("OnOff", False)
        matter_power = matter_device.get("state", {}).get("power", "Off")

        if (zigbee_onoff and matter_power != "On") or \
           (not zigbee_onoff and matter_power != "Off"):
            return False

        return True
```

---

## 7. 智慧家居数据存储与分析

### 7.1 PostgreSQL智慧家居数据存储

**智慧家居数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class SmartHomeStorage:
    """智慧家居数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建智慧家居数据表"""
        # 设备信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(20) UNIQUE NOT NULL,
                device_type VARCHAR(50) NOT NULL,
                device_name VARCHAR(100) NOT NULL,
                device_model VARCHAR(100),
                manufacturer VARCHAR(100),
                firmware_version VARCHAR(50),
                location_room VARCHAR(50),
                location_zone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 设备状态表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS device_states (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(20) NOT NULL,
                state_data JSONB NOT NULL,
                recorded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 传感器数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(20) NOT NULL,
                sensor_type VARCHAR(50) NOT NULL,
                sensor_value DECIMAL(10,2) NOT NULL,
                unit VARCHAR(20),
                recorded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 控制命令表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS control_commands (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(20) NOT NULL,
                command_type VARCHAR(50) NOT NULL,
                command_parameters JSONB,
                command_status VARCHAR(20) DEFAULT 'Pending',
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 事件记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(20) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB,
                event_time TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 能耗数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS energy_consumption (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(20) NOT NULL,
                power_consumption DECIMAL(10,2) NOT NULL,
                unit VARCHAR(10) DEFAULT 'W',
                recorded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 场景定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scenes (
                id BIGSERIAL PRIMARY KEY,
                scene_id VARCHAR(20) UNIQUE NOT NULL,
                scene_name VARCHAR(100) NOT NULL,
                scene_description TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 场景条件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scene_conditions (
                id BIGSERIAL PRIMARY KEY,
                scene_id VARCHAR(20) NOT NULL,
                condition_order INTEGER NOT NULL,
                device_id VARCHAR(20) NOT NULL,
                attribute_name VARCHAR(50) NOT NULL,
                operator VARCHAR(10) NOT NULL,
                condition_value JSONB NOT NULL,
                FOREIGN KEY (scene_id) REFERENCES scenes(scene_id),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 场景动作表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scene_actions (
                id BIGSERIAL PRIMARY KEY,
                scene_id VARCHAR(20) NOT NULL,
                action_order INTEGER NOT NULL,
                device_id VARCHAR(20) NOT NULL,
                command_name VARCHAR(50) NOT NULL,
                command_parameters JSONB,
                FOREIGN KEY (scene_id) REFERENCES scenes(scene_id),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 场景执行历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scene_executions (
                id BIGSERIAL PRIMARY KEY,
                scene_id VARCHAR(20) NOT NULL,
                execution_type VARCHAR(20) NOT NULL,
                execution_result VARCHAR(20) NOT NULL,
                execution_time TIMESTAMP NOT NULL,
                execution_details JSONB,
                FOREIGN KEY (scene_id) REFERENCES scenes(scene_id)
            )
        """)

        # 联动规则表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS automation_rules (
                id BIGSERIAL PRIMARY KEY,
                rule_id VARCHAR(20) UNIQUE NOT NULL,
                rule_name VARCHAR(100) NOT NULL,
                rule_description TEXT,
                trigger_device_id VARCHAR(20) NOT NULL,
                trigger_attribute VARCHAR(50) NOT NULL,
                trigger_operator VARCHAR(10) NOT NULL,
                trigger_value JSONB NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trigger_device_id) REFERENCES devices(device_id)
            )
        """)

        # 联动动作表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS automation_actions (
                id BIGSERIAL PRIMARY KEY,
                rule_id VARCHAR(20) NOT NULL,
                action_order INTEGER NOT NULL,
                device_id VARCHAR(20) NOT NULL,
                command_name VARCHAR(50) NOT NULL,
                command_parameters JSONB,
                FOREIGN KEY (rule_id) REFERENCES automation_rules(rule_id),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_devices_device_id
            ON devices(device_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_states_device_id
            ON device_states(device_id, recorded_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sensor_data_device_id
            ON sensor_data(device_id, recorded_at DESC)
        """)

        self.conn.commit()

    def store_device(self, device_data: Dict) -> int:
        """存储设备信息"""
        self.cur.execute("""
            INSERT INTO devices (
                device_id, device_type, device_name, device_model,
                manufacturer, firmware_version, location_room, location_zone
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE SET
                device_type = EXCLUDED.device_type,
                device_name = EXCLUDED.device_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            device_data.get("device_id"),
            device_data.get("device_type"),
            device_data.get("device_name"),
            device_data.get("device_model"),
            device_data.get("manufacturer"),
            device_data.get("firmware_version"),
            device_data.get("location_room"),
            device_data.get("location_zone")
        ))
        return self.cur.fetchone()[0]

    def store_device_state(self, device_id: str, state_data: Dict) -> int:
        """存储设备状态"""
        self.cur.execute("""
            INSERT INTO device_states (
                device_id, state_data, recorded_at
            ) VALUES (%s, %s::jsonb, CURRENT_TIMESTAMP)
            RETURNING id
        """, (device_id, json.dumps(state_data)))
        return self.cur.fetchone()[0]

    def store_sensor_data(self, device_id: str, sensor_type: str,
                         sensor_value: float, unit: str = None) -> int:
        """存储传感器数据"""
        self.cur.execute("""
            INSERT INTO sensor_data (
                device_id, sensor_type, sensor_value, unit, recorded_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (device_id, sensor_type, sensor_value, unit))
        return self.cur.fetchone()[0]

    def store_scene(self, scene_data: Dict) -> int:
        """存储场景定义"""
        self.cur.execute("""
            INSERT INTO scenes (
                scene_id, scene_name, scene_description, enabled
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (scene_id) DO UPDATE SET
                scene_name = EXCLUDED.scene_name,
                scene_description = EXCLUDED.scene_description,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            scene_data.get("scene_id"),
            scene_data.get("scene_name"),
            scene_data.get("scene_description"),
            scene_data.get("enabled", True)
        ))
        scene_db_id = self.cur.fetchone()[0]

        # 存储场景条件
        conditions = scene_data.get("conditions", [])
        for idx, condition in enumerate(conditions):
            self.cur.execute("""
                INSERT INTO scene_conditions (
                    scene_id, condition_order, device_id,
                    attribute_name, operator, condition_value
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """, (
                scene_data.get("scene_id"),
                idx,
                condition.get("device_id"),
                condition.get("attribute"),
                condition.get("operator"),
                json.dumps(condition.get("value"))
            ))

        # 存储场景动作
        actions = scene_data.get("actions", [])
        for idx, action in enumerate(actions):
            self.cur.execute("""
                INSERT INTO scene_actions (
                    scene_id, action_order, device_id,
                    command_name, command_parameters
                ) VALUES (%s, %s, %s, %s, %s::jsonb)
            """, (
                scene_data.get("scene_id"),
                idx,
                action.get("device_id"),
                action.get("command"),
                json.dumps(action.get("parameters", {}))
            ))

        self.conn.commit()
        return scene_db_id

    def get_all_scenes(self) -> List[Dict]:
        """获取所有场景"""
        self.cur.execute("""
            SELECT scene_id, scene_name, scene_description, enabled
            FROM scenes
            WHERE enabled = TRUE
        """)
        scenes = []
        for row in self.cur.fetchall():
            scene_id = row[0]

            # 获取场景条件
            self.cur.execute("""
                SELECT device_id, attribute_name, operator, condition_value
                FROM scene_conditions
                WHERE scene_id = %s
                ORDER BY condition_order
            """, (scene_id,))
            conditions = []
            for cond_row in self.cur.fetchall():
                conditions.append({
                    "device_id": cond_row[0],
                    "attribute": cond_row[1],
                    "operator": cond_row[2],
                    "value": json.loads(cond_row[3])
                })

            # 获取场景动作
            self.cur.execute("""
                SELECT device_id, command_name, command_parameters
                FROM scene_actions
                WHERE scene_id = %s
                ORDER BY action_order
            """, (scene_id,))
            actions = []
            for act_row in self.cur.fetchall():
                actions.append({
                    "device_id": act_row[0],
                    "command": act_row[1],
                    "parameters": json.loads(act_row[2]) if act_row[2] else {}
                })

            scenes.append({
                "scene_id": scene_id,
                "scene_name": row[1],
                "scene_description": row[2],
                "enabled": row[3],
                "conditions": conditions,
                "actions": actions
            })

        return scenes

    def record_scene_execution(self, scene_id: str, execution_type: str,
                               execution_result: str, details: Dict = None):
        """记录场景执行历史"""
        self.cur.execute("""
            INSERT INTO scene_executions (
                scene_id, execution_type, execution_result,
                execution_time, execution_details
            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s::jsonb)
        """, (
            scene_id,
            execution_type,
            execution_result,
            json.dumps(details or {})
        ))
        self.conn.commit()

    def store_automation_rule(self, rule_data: Dict) -> int:
        """存储自动化规则"""
        self.cur.execute("""
            INSERT INTO automation_rules (
                rule_id, rule_name, rule_description,
                trigger_device_id, trigger_attribute,
                trigger_operator, trigger_value, enabled
            ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (rule_id) DO UPDATE SET
                rule_name = EXCLUDED.rule_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            rule_data.get("rule_id"),
            rule_data.get("rule_name"),
            rule_data.get("rule_description"),
            rule_data.get("trigger_device_id"),
            rule_data.get("trigger_attribute"),
            rule_data.get("trigger_operator"),
            json.dumps(rule_data.get("trigger_value")),
            rule_data.get("enabled", True)
        ))
        rule_db_id = self.cur.fetchone()[0]

        # 存储规则动作
        actions = rule_data.get("actions", [])
        for idx, action in enumerate(actions):
            self.cur.execute("""
                INSERT INTO automation_actions (
                    rule_id, action_order, device_id,
                    command_name, command_parameters
                ) VALUES (%s, %s, %s, %s, %s::jsonb)
            """, (
                rule_data.get("rule_id"),
                idx,
                action.get("device_id"),
                action.get("command"),
                json.dumps(action.get("parameters", {}))
            ))

        self.conn.commit()
        return rule_db_id

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 智慧家居数据分析查询

**查询示例**：

```python
    def get_device_energy_statistics(self, device_id: str, start_date: datetime):
        """查询设备能耗统计"""
        self.cur.execute("""
            SELECT AVG(power_consumption) as avg_power,
                   SUM(power_consumption) as total_consumption,
                   MAX(power_consumption) as max_power,
                   MIN(power_consumption) as min_power,
                   COUNT(*) as data_points
            FROM energy_consumption
            WHERE device_id = %s AND recorded_at >= %s
        """, (device_id, start_date))
        return dict(zip([desc[0] for desc in self.cur.description],
                        self.cur.fetchone()))

    def get_sensor_statistics(self, device_id: str, sensor_type: str,
                             hours: int = 24):
        """查询传感器数据统计"""
        self.cur.execute("""
            SELECT AVG(sensor_value) as avg_value,
                   MAX(sensor_value) as max_value,
                   MIN(sensor_value) as min_value,
                   COUNT(*) as data_count,
                   STDDEV(sensor_value) as stddev_value
            FROM sensor_data
            WHERE device_id = %s AND sensor_type = %s
            AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (device_id, sensor_type, hours))
        return dict(zip([desc[0] for desc in self.cur.description],
                        self.cur.fetchone()))

    def get_scene_execution_statistics(self, scene_id: str, days: int = 7):
        """查询场景执行统计"""
        self.cur.execute("""
            SELECT execution_type,
                   COUNT(*) as execution_count,
                   COUNT(CASE WHEN execution_result = 'Success' THEN 1 END) as success_count,
                   COUNT(CASE WHEN execution_result = 'Failed' THEN 1 END) as failed_count,
                   AVG(EXTRACT(EPOCH FROM (execution_time - LAG(execution_time) OVER (ORDER BY execution_time)))) as avg_interval_seconds
            FROM scene_executions
            WHERE scene_id = %s
            AND execution_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY execution_type
        """, (scene_id, days))
        return self.cur.fetchall()

    def get_device_usage_statistics(self, device_id: str, days: int = 7):
        """查询设备使用统计"""
        self.cur.execute("""
            SELECT
                DATE(recorded_at) as usage_date,
                COUNT(*) as state_changes,
                SUM(CASE WHEN state_data->>'power' = 'On' THEN 1 ELSE 0 END) as on_count,
                SUM(CASE WHEN state_data->>'power' = 'Off' THEN 1 ELSE 0 END) as off_count,
                MAX(recorded_at) as last_used
            FROM device_states
            WHERE device_id = %s
            AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(recorded_at)
            ORDER BY usage_date DESC
        """, (device_id, days))
        return self.cur.fetchall()

    def get_energy_consumption_by_room(self, days: int = 7):
        """按房间查询能耗统计"""
        self.cur.execute("""
            SELECT
                d.location_room,
                SUM(ec.power_consumption) as total_consumption,
                AVG(ec.power_consumption) as avg_consumption,
                MAX(ec.power_consumption) as max_consumption,
                COUNT(DISTINCT ec.device_id) as device_count
            FROM energy_consumption ec
            JOIN devices d ON ec.device_id = d.device_id
            WHERE ec.recorded_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY d.location_room
            ORDER BY total_consumption DESC
        """, (days,))
        return self.cur.fetchall()

    def get_automation_rule_statistics(self, rule_id: str, days: int = 7):
        """查询自动化规则统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as trigger_count,
                COUNT(DISTINCT DATE(execution_time)) as active_days,
                AVG(EXTRACT(EPOCH FROM (execution_time - LAG(execution_time) OVER (ORDER BY execution_time)))) as avg_interval_seconds
            FROM scene_executions
            WHERE scene_id IN (
                SELECT scene_id FROM scenes WHERE scene_id = %s
            )
            AND execution_type = 'Automation'
            AND execution_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (rule_id, days))
        return dict(zip([desc[0] for desc in self.cur.description],
                        self.cur.fetchone()))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
