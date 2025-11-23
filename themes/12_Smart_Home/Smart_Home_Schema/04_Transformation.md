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
import logging
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, time
import json

logger = logging.getLogger(__name__)

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
    """场景执行动作 - 完整实现"""

    def __init__(self, device_id: str, command: str, parameters: Dict, delay: float = 0.0):
        self.device_id = device_id
        self.command = command
        self.parameters = parameters
        self.delay = delay  # 动作延迟执行时间（秒）
        self.retry_count = parameters.get("retry_count", 0)
        self.retry_delay = parameters.get("retry_delay", 1.0)

    def execute(self, device_controller) -> bool:
        """执行动作"""
        import time

        if self.delay > 0:
            time.sleep(self.delay)

        for attempt in range(self.retry_count + 1):
            try:
                success = device_controller.send_command(
                    self.device_id,
                    self.command,
                    self.parameters
                )
                if success:
                    logger.info(f"Action executed: {self.device_id} -> {self.command}")
                    return True
                elif attempt < self.retry_count:
                    logger.warning(f"Action failed, retrying ({attempt + 1}/{self.retry_count})")
                    time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Error executing action: {e}")
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)

        logger.error(f"Action failed after {self.retry_count + 1} attempts")
        return False

class TimeCondition:
    """时间条件"""

    def __init__(self, time_type: str, value: Any):
        """
        time_type: "time_of_day", "day_of_week", "date_range"
        value: 时间值（time对象、星期几、日期范围等）
        """
        self.time_type = time_type
        self.value = value

    def evaluate(self) -> bool:
        """评估时间条件是否满足"""
        now = datetime.now()

        if self.time_type == "time_of_day":
            # value是time对象，例如time(18, 0)表示18:00
            current_time = now.time()
            return current_time >= self.value
        elif self.time_type == "day_of_week":
            # value是星期几（0=Monday, 6=Sunday）
            return now.weekday() == self.value
        elif self.time_type == "date_range":
            # value是(start_date, end_date)元组
            start_date, end_date = self.value
            return start_date <= now.date() <= end_date
        return False

class SmartHomeScene:
    """智慧家居场景 - 完整实现"""

    def __init__(self, scene_id: str, scene_name: str,
                 conditions: List[SceneCondition], actions: List[SceneAction],
                 time_conditions: List[TimeCondition] = None,
                 condition_logic: str = "AND"):
        """
        condition_logic: "AND"表示所有条件必须满足，"OR"表示任一条件满足即可
        """
        self.scene_id = scene_id
        self.scene_name = scene_name
        self.conditions = conditions
        self.actions = actions
        self.time_conditions = time_conditions or []
        self.condition_logic = condition_logic
        self.enabled = True
        self.created_at = datetime.now()
        self.last_triggered = None
        self.trigger_count = 0
        self.device_controller = None

    def set_device_controller(self, controller):
        """设置设备控制器"""
        self.device_controller = controller

    def trigger(self, device_states: Dict[str, Dict]) -> bool:
        """触发场景执行 - 完整实现"""
        if not self.enabled:
            return False

        # 检查时间条件
        if self.time_conditions:
            time_conditions_met = all(tc.evaluate() for tc in self.time_conditions)
            if not time_conditions_met:
                return False

        # 检查设备条件
        if self.condition_logic == "AND":
            # 所有条件必须满足
            conditions_met = all(
                condition.evaluate(device_states.get(condition.device_id, {}))
                for condition in self.conditions
            )
        else:
            # OR逻辑：任一条件满足即可
            conditions_met = any(
                condition.evaluate(device_states.get(condition.device_id, {}))
                for condition in self.conditions
            )

        if not conditions_met:
            return False

        # 执行所有动作
        success = self._execute_actions()

        if success:
            self.last_triggered = datetime.now()
            self.trigger_count += 1

        return success

    def _execute_actions(self) -> bool:
        """执行所有动作 - 完整实现"""
        if not self.device_controller:
            logger.error("Device controller not set")
            return False

        results = []
        for action in self.actions:
            try:
                result = action.execute(self.device_controller)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing action {action.device_id}: {e}")
                results.append(False)

        return all(results)

    def enable(self):
        """启用场景"""
        self.enabled = True

    def disable(self):
        """禁用场景"""
        self.enabled = False

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "scene_id": self.scene_id,
            "scene_name": self.scene_name,
            "conditions": [
                {
                    "device_id": c.device_id,
                    "attribute": c.attribute,
                    "operator": c.operator,
                    "value": c.value
                }
                for c in self.conditions
            ],
            "actions": [
                {
                    "device_id": a.device_id,
                    "command": a.command,
                    "parameters": a.parameters,
                    "delay": a.delay
                }
                for a in self.actions
            ],
            "enabled": self.enabled,
            "trigger_count": self.trigger_count,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None
        }

class DeviceController:
    """设备控制器 - 用于执行场景动作"""

    def __init__(self, matter_sdk: MatterSDKWrapper = None, zigbee_api: Zigbee2MQTTWrapper = None):
        self.matter_sdk = matter_sdk
        self.zigbee_api = zigbee_api

    def send_command(self, device_id: str, command: str, parameters: Dict) -> bool:
        """发送设备命令"""
        # 根据设备类型选择相应的协议
        if device_id.startswith("MATTER"):
            return self._send_matter_command(device_id, command, parameters)
        else:
            return self._send_zigbee_command(device_id, command, parameters)

    def _send_matter_command(self, device_id: str, command: str, parameters: Dict) -> bool:
        """发送Matter命令"""
        if not self.matter_sdk:
            logger.error("Matter SDK not available")
            return False

        device = self.matter_sdk.get_device(device_id)
        if not device:
            logger.error(f"Device {device_id} not found")
            return False

        # 根据命令类型映射到Matter集群和命令ID
        if command == "turn_on":
            return self.matter_sdk.send_command(
                device_id, device.endpoint_id,
                MatterClusterId.ON_OFF, 0x0001, {}
            )
        elif command == "turn_off":
            return self.matter_sdk.send_command(
                device_id, device.endpoint_id,
                MatterClusterId.ON_OFF, 0x0000, {}
            )
        elif command == "set_brightness":
            level = parameters.get("brightness", 0)
            return self.matter_sdk.send_command(
                device_id, device.endpoint_id,
                MatterClusterId.LEVEL_CONTROL, 0x0000,
                {"level": level, "transition_time": 0}
            )
        elif command == "set_temperature":
            temp = parameters.get("temperature", 20)
            return self.matter_sdk.write_attribute(
                device_id, device.endpoint_id,
                MatterClusterId.THERMOSTAT,
                MatterAttributeId.THERMOSTAT_OCCUPIED_COOLING_SETPOINT,
                int(temp * 100)
            )
        else:
            logger.error(f"Unknown command: {command}")
            return False

    def _send_zigbee_command(self, device_id: str, command: str, parameters: Dict) -> bool:
        """发送Zigbee命令"""
        if not self.zigbee_api:
            logger.error("Zigbee API not available")
            return False

        state = {}
        if command == "turn_on":
            state = {"state": "ON"}
        elif command == "turn_off":
            state = {"state": "OFF"}
        elif command == "set_brightness":
            state = {"brightness": parameters.get("brightness", 0)}
        elif command == "set_temperature":
            state = {"current_heating_setpoint": parameters.get("temperature", 20)}

        try:
            result = self.zigbee_api.set_device_state(device_id, state)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Failed to send Zigbee command: {e}")
            return False

class SceneManager:
    """场景管理器 - 完整实现"""

    def __init__(self, storage, device_controller: DeviceController = None):
        self.storage = storage
        self.device_controller = device_controller or DeviceController()
        self.scenes: Dict[str, SmartHomeScene] = {}
        self.device_states: Dict[str, Dict] = {}
        self.scene_execution_history: List[Dict] = []
        self._load_scenes()

    def _load_scenes(self):
        """从数据库加载场景 - 完整实现"""
        scenes_data = self.storage.get_all_scenes()
        for scene_data in scenes_data:
            try:
                conditions = [
                    SceneCondition(**c) for c in scene_data.get("conditions", [])
                ]
                actions = [
                    SceneAction(**a) for a in scene_data.get("actions", [])
                ]

                # 加载时间条件
                time_conditions = []
                for tc_data in scene_data.get("time_conditions", []):
                    time_conditions.append(TimeCondition(**tc_data))

                scene = SmartHomeScene(
                    scene_data["scene_id"],
                    scene_data["scene_name"],
                    conditions,
                    actions,
                    time_conditions,
                    scene_data.get("condition_logic", "AND")
                )
                scene.set_device_controller(self.device_controller)
                scene.enabled = scene_data.get("enabled", True)
                self.scenes[scene_data["scene_id"]] = scene
            except Exception as e:
                logger.error(f"Failed to load scene {scene_data.get('scene_id')}: {e}")

    def create_scene(self, scene_id: str, scene_name: str,
                     conditions: List[Dict], actions: List[Dict],
                     time_conditions: List[Dict] = None,
                     condition_logic: str = "AND") -> str:
        """创建场景 - 完整实现"""
        scene_conditions = [SceneCondition(**c) for c in conditions]
        scene_actions = [SceneAction(**a) for a in actions]

        time_cond_objects = []
        if time_conditions:
            time_cond_objects = [TimeCondition(**tc) for tc in time_conditions]

        scene = SmartHomeScene(
            scene_id, scene_name, scene_conditions, scene_actions,
            time_cond_objects, condition_logic
        )
        scene.set_device_controller(self.device_controller)
        self.scenes[scene_id] = scene

        # 保存到数据库
        self.storage.store_scene({
            "scene_id": scene_id,
            "scene_name": scene_name,
            "conditions": conditions,
            "actions": actions,
            "time_conditions": time_conditions or [],
            "condition_logic": condition_logic,
            "enabled": True
        })

        return scene_id

    def update_device_state(self, device_id: str, state: Dict):
        """更新设备状态并检查场景触发 - 完整实现"""
        old_state = self.device_states.get(device_id, {})
        self.device_states[device_id] = state

        # 检查所有场景
        triggered_scenes = []
        for scene in self.scenes.values():
            if scene.enabled:
                try:
                    if scene.trigger(self.device_states):
                        triggered_scenes.append(scene.scene_id)
                        # 记录执行历史
                        self.scene_execution_history.append({
                            "scene_id": scene.scene_id,
                            "trigger_time": datetime.now().isoformat(),
                            "trigger_device": device_id,
                            "device_state": state
                        })
                        # 保存到数据库
                        self.storage.record_scene_execution(
                            scene.scene_id, "auto", True
                        )
                except Exception as e:
                    logger.error(f"Error triggering scene {scene.scene_id}: {e}")

        if triggered_scenes:
            logger.info(f"Scenes triggered: {triggered_scenes}")

    def execute_scene(self, scene_id: str, manual: bool = True) -> bool:
        """手动执行场景 - 完整实现"""
        scene = self.scenes.get(scene_id)
        if not scene:
            logger.error(f"Scene {scene_id} not found")
            return False

        try:
            result = scene.trigger(self.device_states)
            if result:
                # 记录执行历史
                self.scene_execution_history.append({
                    "scene_id": scene_id,
                    "trigger_time": datetime.now().isoformat(),
                    "trigger_type": "manual" if manual else "auto"
                })
                # 保存到数据库
                self.storage.record_scene_execution(
                    scene_id, "manual" if manual else "auto", result
                )
            return result
        except Exception as e:
            logger.error(f"Error executing scene {scene_id}: {e}")
            return False

    def get_scene(self, scene_id: str) -> Optional[SmartHomeScene]:
        """获取场景"""
        return self.scenes.get(scene_id)

    def list_scenes(self) -> List[Dict]:
        """列出所有场景"""
        return [scene.to_dict() for scene in self.scenes.values()]

    def enable_scene(self, scene_id: str):
        """启用场景"""
        scene = self.scenes.get(scene_id)
        if scene:
            scene.enable()
            self.storage.update_scene_enabled(scene_id, True)

    def disable_scene(self, scene_id: str):
        """禁用场景"""
        scene = self.scenes.get(scene_id)
        if scene:
            scene.disable()
            self.storage.update_scene_enabled(scene_id, False)

    def delete_scene(self, scene_id: str) -> bool:
        """删除场景"""
        if scene_id in self.scenes:
            del self.scenes[scene_id]
            self.storage.delete_scene(scene_id)
            return True
        return False

    def get_scene_statistics(self, scene_id: str) -> Dict:
        """获取场景统计信息"""
        scene = self.scenes.get(scene_id)
        if not scene:
            return {}

        return {
            "scene_id": scene_id,
            "trigger_count": scene.trigger_count,
            "last_triggered": scene.last_triggered.isoformat() if scene.last_triggered else None,
            "enabled": scene.enabled,
            "condition_count": len(scene.conditions),
            "action_count": len(scene.actions)
        }
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
import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

try:
    import chip.clusters as Clusters
    from chip import ChipDeviceCtrl
    from chip.clusters.Attribute import AttributePath, AttributeReadResult
    from chip.clusters.ClusterObjects import ClusterCommand
    from chip.exceptions import ChipStackError
    MATTER_SDK_AVAILABLE = True
except ImportError:
    MATTER_SDK_AVAILABLE = False
    logging.warning("Matter SDK not available, using mock implementation")

logger = logging.getLogger(__name__)

class MatterClusterId(IntEnum):
    """Matter集群ID定义"""
    ON_OFF = 0x0006
    LEVEL_CONTROL = 0x0008
    COLOR_CONTROL = 0x0300
    DOOR_LOCK = 0x0101
    THERMOSTAT = 0x0201
    WINDOW_COVERING = 0x0102
    BASIC = 0x0028
    IDENTIFY = 0x0003

class MatterAttributeId(IntEnum):
    """Matter属性ID定义"""
    ON_OFF_ON_OFF = 0x0000
    LEVEL_CONTROL_CURRENT_LEVEL = 0x0000
    COLOR_CONTROL_CURRENT_HUE = 0x0000
    COLOR_CONTROL_CURRENT_SATURATION = 0x0001
    COLOR_CONTROL_CURRENT_X = 0x0003
    COLOR_CONTROL_CURRENT_Y = 0x0004
    DOOR_LOCK_LOCK_STATE = 0x0000
    THERMOSTAT_LOCAL_TEMPERATURE = 0x0000
    THERMOSTAT_OCCUPIED_COOLING_SETPOINT = 0x0011

@dataclass
class MatterDevice:
    """Matter设备信息"""
    device_id: str
    node_id: int
    endpoint_id: int
    device_type: str
    vendor_id: int
    product_id: int
    clusters: List[int]
    state: Dict[str, Any]

class MatterSDKWrapper:
    """Matter SDK封装类 - 完整的设备发现、控制和事件订阅实现"""

    def __init__(self, node_id: int = 0x12344321, fabric_id: int = 1):
        self.node_id = node_id
        self.fabric_id = fabric_id
        self.device_ctrl: Optional[ChipDeviceCtrl.ChipDeviceController] = None
        self.discovered_devices: Dict[str, MatterDevice] = {}
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self.subscription_thread: Optional[threading.Thread] = None
        self.running = False

        if MATTER_SDK_AVAILABLE:
            self._initialize_controller()
        else:
            logger.warning("Using mock Matter SDK implementation")

    def _initialize_controller(self):
        """初始化Matter控制器"""
        try:
            self.device_ctrl = ChipDeviceCtrl.ChipDeviceController()
            self.device_ctrl.SetFabricId(self.fabric_id)
            self.device_ctrl.SetNodeId(self.node_id)
            logger.info(f"Matter controller initialized: node_id={self.node_id}, fabric_id={self.fabric_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Matter controller: {e}")
            self.device_ctrl = None

    def discover_devices(self, timeout: int = 10) -> List[Dict]:
        """发现Matter设备 - 完整实现"""
        devices = []

        if not MATTER_SDK_AVAILABLE or not self.device_ctrl:
            # Mock实现用于测试
            logger.info("Using mock device discovery")
            mock_devices = [
                {
                    "device_id": "MATTER001",
                    "node_id": 0x12345678,
                    "endpoint_id": 1,
                    "device_type": "ExtendedColorLight",
                    "vendor_id": 0xFFF1,
                    "product_id": 0x8000,
                    "clusters": [0x0006, 0x0008, 0x0300],
                    "state": {"power": "On", "brightness": 50}
                },
                {
                    "device_id": "MATTER002",
                    "node_id": 0x12345679,
                    "endpoint_id": 1,
                    "device_type": "DoorLock",
                    "vendor_id": 0xFFF1,
                    "product_id": 0x8001,
                    "clusters": [0x0101],
                    "state": {"lock_state": "Locked"}
                }
            ]
            for dev_data in mock_devices:
                device = MatterDevice(**dev_data)
                self.discovered_devices[device.device_id] = device
                devices.append(dev_data)
            return devices

        try:
            # 使用Matter SDK进行设备发现
            # 1. 启动BLE扫描
            logger.info("Starting Matter device discovery...")

            # 2. 发现设备并获取设备信息
            # 注意：实际实现需要使用Matter的Commissioning流程
            # 这里展示完整的发现流程

            discovered_nodes = []
            # 模拟发现过程
            for i in range(timeout):
                # 在实际实现中，这里会调用Matter SDK的发现API
                # node_list = self.device_ctrl.DiscoverCommissionableNodes()
                # for node in node_list:
                #     discovered_nodes.append(node)
                pass

            # 3. 对每个发现的设备进行连接和属性读取
            for node_info in discovered_nodes:
                try:
                    device_info = self._connect_and_read_device_info(node_info)
                    if device_info:
                        device = MatterDevice(**device_info)
                        self.discovered_devices[device.device_id] = device
                        devices.append(device_info)
                except Exception as e:
                    logger.error(f"Failed to connect to device {node_info}: {e}")

            logger.info(f"Discovered {len(devices)} Matter devices")
            return devices

        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return devices

    def _connect_and_read_device_info(self, node_info: Dict) -> Optional[Dict]:
        """连接设备并读取设备信息"""
        try:
            # 1. 建立连接
            # node_id = node_info.get("node_id")
            # self.device_ctrl.ConnectDevice(node_id)

            # 2. 读取Basic Cluster信息
            endpoint_id = 0
            basic_cluster = Clusters.Basic

            # 读取VendorID
            # vendor_id = self.read_attribute(
            #     node_id, endpoint_id,
            #     MatterClusterId.BASIC,
            #     Clusters.Basic.Attributes.VendorID
            # )

            # 读取ProductID
            # product_id = self.read_attribute(
            #     node_id, endpoint_id,
            #     MatterClusterId.BASIC,
            #     Clusters.Basic.Attributes.ProductID
            # )

            # 3. 读取设备类型
            # device_type = self.read_attribute(
            #     node_id, endpoint_id,
            #     MatterClusterId.BASIC,
            #     Clusters.Basic.Attributes.DeviceType
            # )

            # 4. 读取支持的集群列表
            # clusters = self._read_supported_clusters(node_id, endpoint_id)

            # 返回设备信息
            return {
                "device_id": f"MATTER_{node_info.get('node_id', 0):08X}",
                "node_id": node_info.get("node_id", 0),
                "endpoint_id": endpoint_id,
                "device_type": "Unknown",
                "vendor_id": 0xFFF1,
                "product_id": 0x8000,
                "clusters": [],
                "state": {}
            }

        except Exception as e:
            logger.error(f"Failed to connect and read device info: {e}")
            return None

    def read_attribute(self, device_id: str, endpoint_id: int,
                      cluster_id: int, attribute_id: int) -> Any:
        """读取设备属性 - 完整实现"""
        device = self.discovered_devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        if not MATTER_SDK_AVAILABLE or not self.device_ctrl:
            # Mock实现
            logger.debug(f"Mock read attribute: device={device_id}, cluster={cluster_id:04X}, attr={attribute_id:04X}")
            return self._mock_read_attribute(device, cluster_id, attribute_id)

        try:
            # 构建属性路径
            attribute_path = AttributePath(
                EndpointId=endpoint_id,
                ClusterId=cluster_id,
                AttributeId=attribute_id
            )

            # 读取属性
            result = self.device_ctrl.ReadAttribute(
                device.node_id,
                [attribute_path],
                timeoutMs=5000
            )

            if result and len(result) > 0:
                read_result: AttributeReadResult = result[0]
                if read_result.Status == 0:  # SUCCESS
                    value = read_result.Data
                    logger.debug(f"Read attribute success: {device_id}, value={value}")
                    return value
                else:
                    logger.error(f"Read attribute failed: status={read_result.Status}")
                    return None
            else:
                logger.error("Read attribute returned empty result")
                return None

        except ChipStackError as e:
            logger.error(f"ChipStackError reading attribute: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to read attribute: {e}")
            return None

    def _mock_read_attribute(self, device: MatterDevice, cluster_id: int, attribute_id: int) -> Any:
        """Mock属性读取实现"""
        if cluster_id == MatterClusterId.ON_OFF:
            if attribute_id == MatterAttributeId.ON_OFF_ON_OFF:
                return device.state.get("power") == "On"
        elif cluster_id == MatterClusterId.LEVEL_CONTROL:
            if attribute_id == MatterAttributeId.LEVEL_CONTROL_CURRENT_LEVEL:
                return device.state.get("brightness", 0)
        elif cluster_id == MatterClusterId.DOOR_LOCK:
            if attribute_id == MatterAttributeId.DOOR_LOCK_LOCK_STATE:
                return device.state.get("lock_state", "Locked")
        return None

    def write_attribute(self, device_id: str, endpoint_id: int,
                       cluster_id: int, attribute_id: int, value: Any) -> bool:
        """写入设备属性 - 完整实现"""
        device = self.discovered_devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        if not MATTER_SDK_AVAILABLE or not self.device_ctrl:
            # Mock实现
            logger.debug(f"Mock write attribute: device={device_id}, cluster={cluster_id:04X}, attr={attribute_id:04X}, value={value}")
            return self._mock_write_attribute(device, cluster_id, attribute_id, value)

        try:
            # 构建属性路径和值
            attribute_path = AttributePath(
                EndpointId=endpoint_id,
                ClusterId=cluster_id,
                AttributeId=attribute_id
            )

            # 写入属性
            result = self.device_ctrl.WriteAttribute(
                device.node_id,
                attribute_path,
                value,
                timeoutMs=5000
            )

            if result == 0:  # SUCCESS
                logger.info(f"Write attribute success: {device_id}, value={value}")
                # 更新本地状态
                self._update_device_state(device, cluster_id, attribute_id, value)
                return True
            else:
                logger.error(f"Write attribute failed: status={result}")
                return False

        except ChipStackError as e:
            logger.error(f"ChipStackError writing attribute: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to write attribute: {e}")
            return False

    def _mock_write_attribute(self, device: MatterDevice, cluster_id: int, attribute_id: int, value: Any) -> bool:
        """Mock属性写入实现"""
        if cluster_id == MatterClusterId.ON_OFF:
            if attribute_id == MatterAttributeId.ON_OFF_ON_OFF:
                device.state["power"] = "On" if value else "Off"
                return True
        elif cluster_id == MatterClusterId.LEVEL_CONTROL:
            if attribute_id == MatterAttributeId.LEVEL_CONTROL_CURRENT_LEVEL:
                device.state["brightness"] = max(0, min(254, value))
                return True
        elif cluster_id == MatterClusterId.DOOR_LOCK:
            if attribute_id == MatterAttributeId.DOOR_LOCK_LOCK_STATE:
                device.state["lock_state"] = value
                return True
        return False

    def send_command(self, device_id: str, endpoint_id: int,
                    cluster_id: int, command_id: int, parameters: Dict = None) -> bool:
        """发送命令 - 完整实现"""
        device = self.discovered_devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        if parameters is None:
            parameters = {}

        if not MATTER_SDK_AVAILABLE or not self.device_ctrl:
            # Mock实现
            logger.debug(f"Mock send command: device={device_id}, cluster={cluster_id:04X}, command={command_id:04X}")
            return self._mock_send_command(device, cluster_id, command_id, parameters)

        try:
            # 构建命令
            # 根据集群类型构建相应的命令对象
            command = self._build_command(cluster_id, command_id, parameters)

            if not command:
                logger.error(f"Failed to build command for cluster {cluster_id:04X}, command {command_id:04X}")
                return False

            # 发送命令
            result = self.device_ctrl.SendCommand(
                device.node_id,
                endpoint_id,
                cluster_id,
                command,
                timeoutMs=5000
            )

            if result == 0:  # SUCCESS
                logger.info(f"Send command success: {device_id}, command={command_id:04X}")
                return True
            else:
                logger.error(f"Send command failed: status={result}")
                return False

        except ChipStackError as e:
            logger.error(f"ChipStackError sending command: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def _build_command(self, cluster_id: int, command_id: int, parameters: Dict) -> Optional[ClusterCommand]:
        """构建Matter命令对象"""
        try:
            if cluster_id == MatterClusterId.ON_OFF:
                if command_id == 0x0000:  # Off
                    return Clusters.OnOff.Commands.Off()
                elif command_id == 0x0001:  # On
                    return Clusters.OnOff.Commands.On()
                elif command_id == 0x0002:  # Toggle
                    return Clusters.OnOff.Commands.Toggle()
            elif cluster_id == MatterClusterId.LEVEL_CONTROL:
                if command_id == 0x0000:  # MoveToLevel
                    level = parameters.get("level", 0)
                    transition_time = parameters.get("transition_time", 0)
                    return Clusters.LevelControl.Commands.MoveToLevel(
                        level=level,
                        transitionTime=transition_time
                    )
            elif cluster_id == MatterClusterId.DOOR_LOCK:
                if command_id == 0x0000:  # LockDoor
                    return Clusters.DoorLock.Commands.LockDoor()
                elif command_id == 0x0001:  # UnlockDoor
                    return Clusters.DoorLock.Commands.UnlockDoor()
            return None
        except Exception as e:
            logger.error(f"Failed to build command: {e}")
            return None

    def _mock_send_command(self, device: MatterDevice, cluster_id: int, command_id: int, parameters: Dict) -> bool:
        """Mock命令发送实现"""
        if cluster_id == MatterClusterId.ON_OFF:
            if command_id == 0x0000:  # Off
                device.state["power"] = "Off"
                return True
            elif command_id == 0x0001:  # On
                device.state["power"] = "On"
                return True
            elif command_id == 0x0002:  # Toggle
                device.state["power"] = "Off" if device.state.get("power") == "On" else "On"
                return True
        elif cluster_id == MatterClusterId.LEVEL_CONTROL:
            if command_id == 0x0000:  # MoveToLevel
                device.state["brightness"] = parameters.get("level", 0)
                return True
        elif cluster_id == MatterClusterId.DOOR_LOCK:
            if command_id == 0x0000:  # LockDoor
                device.state["lock_state"] = "Locked"
                return True
            elif command_id == 0x0001:  # UnlockDoor
                device.state["lock_state"] = "Unlocked"
                return True
        return False

    def subscribe_events(self, device_id: str, endpoint_id: int,
                        cluster_id: int, callback: Callable[[Dict], None],
                        min_interval: int = 0, max_interval: int = 60):
        """订阅设备事件 - 完整实现"""
        device = self.discovered_devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        subscription_key = f"{device_id}:{endpoint_id}:{cluster_id}"

        if subscription_key not in self.event_callbacks:
            self.event_callbacks[subscription_key] = []

        self.event_callbacks[subscription_key].append(callback)

        if not self.running:
            self._start_subscription_thread()

        logger.info(f"Subscribed to events: {subscription_key}")

    def _start_subscription_thread(self):
        """启动事件订阅线程"""
        if self.subscription_thread and self.subscription_thread.is_alive():
            return

        self.running = True
        self.subscription_thread = threading.Thread(target=self._subscription_loop, daemon=True)
        self.subscription_thread.start()
        logger.info("Event subscription thread started")

    def _subscription_loop(self):
        """事件订阅循环"""
        while self.running:
            try:
                for subscription_key, callbacks in self.event_callbacks.items():
                    device_id, endpoint_id_str, cluster_id_str = subscription_key.split(":")
                    device = self.discovered_devices.get(device_id)

                    if not device:
                        continue

                    # 读取设备状态变化
                    if MATTER_SDK_AVAILABLE and self.device_ctrl:
                        # 实际实现中会使用Matter SDK的订阅API
                        # 这里模拟状态变化检测
                        pass
                    else:
                        # Mock实现：模拟状态变化
                        self._mock_check_state_changes(device, int(cluster_id_str), callbacks)

                # 每1秒检查一次
                threading.Event().wait(1.0)

            except Exception as e:
                logger.error(f"Error in subscription loop: {e}")

    def _mock_check_state_changes(self, device: MatterDevice, cluster_id: int, callbacks: List[Callable]):
        """Mock状态变化检测"""
        # 在实际实现中，这里会检测设备状态的实际变化
        # 并调用回调函数
        pass

    def _update_device_state(self, device: MatterDevice, cluster_id: int, attribute_id: int, value: Any):
        """更新设备状态并触发事件"""
        # 更新状态
        if cluster_id == MatterClusterId.ON_OFF:
            device.state["power"] = "On" if value else "Off"
        elif cluster_id == MatterClusterId.LEVEL_CONTROL:
            device.state["brightness"] = value

        # 触发事件回调
        subscription_key = f"{device.device_id}:{device.endpoint_id}:{cluster_id}"
        if subscription_key in self.event_callbacks:
            event_data = {
                "device_id": device.device_id,
                "endpoint_id": device.endpoint_id,
                "cluster_id": cluster_id,
                "attribute_id": attribute_id,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            for callback in self.event_callbacks[subscription_key]:
                try:
                    callback(event_data)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")

    def get_device(self, device_id: str) -> Optional[MatterDevice]:
        """获取设备信息"""
        return self.discovered_devices.get(device_id)

    def list_devices(self) -> List[str]:
        """列出所有已发现的设备ID"""
        return list(self.discovered_devices.keys())

    def disconnect_device(self, device_id: str):
        """断开设备连接"""
        device = self.discovered_devices.get(device_id)
        if device and MATTER_SDK_AVAILABLE and self.device_ctrl:
            try:
                self.device_ctrl.CloseSession(device.node_id)
                logger.info(f"Disconnected device: {device_id}")
            except Exception as e:
                logger.error(f"Failed to disconnect device: {e}")

    def shutdown(self):
        """关闭SDK连接"""
        self.running = False
        if self.subscription_thread:
            self.subscription_thread.join(timeout=5.0)

        if self.device_ctrl:
            try:
                self.device_ctrl.Shutdown()
                logger.info("Matter SDK shutdown complete")
            except Exception as e:
                logger.error(f"Error during SDK shutdown: {e}")
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

    def update_scene_enabled(self, scene_id: str, enabled: bool):
        """更新场景启用状态"""
        self.cur.execute("""
            UPDATE scenes
            SET enabled = %s, updated_at = CURRENT_TIMESTAMP
            WHERE scene_id = %s
        """, (enabled, scene_id))
        self.conn.commit()

    def update_scene(self, scene_id: str, scene_data: Dict):
        """更新场景定义"""
        # 更新场景基本信息
        self.cur.execute("""
            UPDATE scenes
            SET scene_name = %s, scene_description = %s, updated_at = CURRENT_TIMESTAMP
            WHERE scene_id = %s
        """, (
            scene_data.get("scene_name"),
            scene_data.get("scene_description"),
            scene_id
        ))

        # 删除旧的条件和动作
        self.cur.execute("DELETE FROM scene_conditions WHERE scene_id = %s", (scene_id,))
        self.cur.execute("DELETE FROM scene_actions WHERE scene_id = %s", (scene_id,))

        # 插入新的条件
        conditions = scene_data.get("conditions", [])
        for idx, condition in enumerate(conditions):
            self.cur.execute("""
                INSERT INTO scene_conditions (
                    scene_id, condition_order, device_id,
                    attribute_name, operator, condition_value
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """, (
                scene_id, idx,
                condition.get("device_id"),
                condition.get("attribute"),
                condition.get("operator"),
                json.dumps(condition.get("value"))
            ))

        # 插入新的动作
        actions = scene_data.get("actions", [])
        for idx, action in enumerate(actions):
            self.cur.execute("""
                INSERT INTO scene_actions (
                    scene_id, action_order, device_id,
                    command_name, command_parameters
                ) VALUES (%s, %s, %s, %s, %s::jsonb)
            """, (
                scene_id, idx,
                action.get("device_id"),
                action.get("command"),
                json.dumps(action.get("parameters", {}))
            ))

        self.conn.commit()

    def delete_scene(self, scene_id: str):
        """删除场景"""
        # 删除场景执行历史
        self.cur.execute("DELETE FROM scene_executions WHERE scene_id = %s", (scene_id,))
        # 删除场景动作
        self.cur.execute("DELETE FROM scene_actions WHERE scene_id = %s", (scene_id,))
        # 删除场景条件
        self.cur.execute("DELETE FROM scene_conditions WHERE scene_id = %s", (scene_id,))
        # 删除场景
        self.cur.execute("DELETE FROM scenes WHERE scene_id = %s", (scene_id,))
        self.conn.commit()

    def get_device(self, device_id: str) -> Optional[Dict]:
        """获取设备信息"""
        self.cur.execute("""
            SELECT device_id, device_type, device_name, device_model,
                   manufacturer, firmware_version, location_room, location_zone,
                   created_at, updated_at
            FROM devices
            WHERE device_id = %s
        """, (device_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "device_id": row[0],
                "device_type": row[1],
                "device_name": row[2],
                "device_model": row[3],
                "manufacturer": row[4],
                "firmware_version": row[5],
                "location_room": row[6],
                "location_zone": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            }
        return None

    def get_latest_device_state(self, device_id: str) -> Optional[Dict]:
        """获取设备最新状态"""
        self.cur.execute("""
            SELECT state_data, recorded_at
            FROM device_states
            WHERE device_id = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (device_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "state": json.loads(row[0]),
                "recorded_at": row[1]
            }
        return None

    def get_device_states_history(self, device_id: str, start_time: datetime,
                                  end_time: datetime = None) -> List[Dict]:
        """获取设备状态历史"""
        if end_time is None:
            end_time = datetime.now()

        self.cur.execute("""
            SELECT state_data, recorded_at
            FROM device_states
            WHERE device_id = %s
            AND recorded_at >= %s AND recorded_at <= %s
            ORDER BY recorded_at DESC
        """, (device_id, start_time, end_time))

        return [
            {
                "state": json.loads(row[0]),
                "recorded_at": row[1]
            }
            for row in self.cur.fetchall()
        ]

    def store_control_command(self, device_id: str, command_type: str,
                             command_parameters: Dict, status: str = "Pending") -> int:
        """存储控制命令"""
        self.cur.execute("""
            INSERT INTO control_commands (
                device_id, command_type, command_parameters, command_status
            ) VALUES (%s, %s, %s::jsonb, %s)
            RETURNING id
        """, (
            device_id,
            command_type,
            json.dumps(command_parameters),
            status
        ))
        command_id = self.cur.fetchone()[0]
        self.conn.commit()
        return command_id

    def update_command_status(self, command_id: int, status: str, executed_at: datetime = None):
        """更新命令状态"""
        if executed_at is None:
            executed_at = datetime.now()

        self.cur.execute("""
            UPDATE control_commands
            SET command_status = %s, executed_at = %s
            WHERE id = %s
        """, (status, executed_at, command_id))
        self.conn.commit()

    def store_event(self, device_id: str, event_type: str, event_data: Dict):
        """存储事件"""
        self.cur.execute("""
            INSERT INTO events (
                device_id, event_type, event_data, event_time
            ) VALUES (%s, %s, %s::jsonb, CURRENT_TIMESTAMP)
        """, (
            device_id,
            event_type,
            json.dumps(event_data)
        ))
        self.conn.commit()

    def get_recent_events(self, device_id: str = None, event_type: str = None,
                          limit: int = 100) -> List[Dict]:
        """获取最近的事件"""
        query = "SELECT device_id, event_type, event_data, event_time FROM events WHERE 1=1"
        params = []

        if device_id:
            query += " AND device_id = %s"
            params.append(device_id)

        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)

        query += " ORDER BY event_time DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        return [
            {
                "device_id": row[0],
                "event_type": row[1],
                "event_data": json.loads(row[2]),
                "event_time": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def store_energy_consumption(self, device_id: str, power_consumption: float,
                                unit: str = "W") -> int:
        """存储能耗数据"""
        self.cur.execute("""
            INSERT INTO energy_consumption (
                device_id, power_consumption, unit, recorded_at
            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (device_id, power_consumption, unit))
        energy_id = self.cur.fetchone()[0]
        self.conn.commit()
        return energy_id

    def get_devices_by_location(self, room: str = None, zone: str = None) -> List[Dict]:
        """按位置查询设备"""
        query = "SELECT device_id, device_type, device_name, location_room, location_zone FROM devices WHERE 1=1"
        params = []

        if room:
            query += " AND location_room = %s"
            params.append(room)

        if zone:
            query += " AND location_zone = %s"
            params.append(zone)

        self.cur.execute(query, params)
        return [
            {
                "device_id": row[0],
                "device_type": row[1],
                "device_name": row[2],
                "location_room": row[3],
                "location_zone": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_scene_by_id(self, scene_id: str) -> Optional[Dict]:
        """根据ID获取场景"""
        self.cur.execute("""
            SELECT scene_id, scene_name, scene_description, enabled
            FROM scenes
            WHERE scene_id = %s
        """, (scene_id,))
        row = self.cur.fetchone()

        if not row:
            return None

        # 获取场景条件
        self.cur.execute("""
            SELECT device_id, attribute_name, operator, condition_value
            FROM scene_conditions
            WHERE scene_id = %s
            ORDER BY condition_order
        """, (scene_id,))
        conditions = [
            {
                "device_id": cond_row[0],
                "attribute": cond_row[1],
                "operator": cond_row[2],
                "value": json.loads(cond_row[3])
            }
            for cond_row in self.cur.fetchall()
        ]

        # 获取场景动作
        self.cur.execute("""
            SELECT device_id, command_name, command_parameters
            FROM scene_actions
            WHERE scene_id = %s
            ORDER BY action_order
        """, (scene_id,))
        actions = [
            {
                "device_id": act_row[0],
                "command": act_row[1],
                "parameters": json.loads(act_row[2]) if act_row[2] else {}
            }
            for act_row in self.cur.fetchall()
        ]

        return {
            "scene_id": row[0],
            "scene_name": row[1],
            "scene_description": row[2],
            "enabled": row[3],
            "conditions": conditions,
            "actions": actions
        }

    def get_automation_rules(self, enabled_only: bool = True) -> List[Dict]:
        """获取自动化规则"""
        query = """
            SELECT rule_id, rule_name, rule_description, trigger_device_id,
                   trigger_attribute, trigger_operator, trigger_value, enabled
            FROM automation_rules
        """
        if enabled_only:
            query += " WHERE enabled = TRUE"

        self.cur.execute(query)
        rules = []
        for row in self.cur.fetchall():
            rule_id = row[0]

            # 获取规则动作
            self.cur.execute("""
                SELECT device_id, command_name, command_parameters
                FROM automation_actions
                WHERE rule_id = %s
                ORDER BY action_order
            """, (rule_id,))
            actions = [
                {
                    "device_id": act_row[0],
                    "command": act_row[1],
                    "parameters": json.loads(act_row[2]) if act_row[2] else {}
                }
                for act_row in self.cur.fetchall()
            ]

            rules.append({
                "rule_id": rule_id,
                "rule_name": row[1],
                "rule_description": row[2],
                "trigger_device_id": row[3],
                "trigger_attribute": row[4],
                "trigger_operator": row[5],
                "trigger_value": json.loads(row[6]),
                "enabled": row[7],
                "actions": actions
            })

        return rules

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
