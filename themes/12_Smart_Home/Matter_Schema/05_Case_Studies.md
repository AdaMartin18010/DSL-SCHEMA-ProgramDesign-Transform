# Matter Schema实践案例

## 📑 目录

- [Matter Schema实践案例](#matter-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：Matter On/Off Light控制](#2-案例1matter-onoff-light控制)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：Matter Door Lock控制](#3-案例2matter-door-lock控制)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：Matter Thermostat控制](#4-案例3matter-thermostat控制)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：Matter设备发现和管理](#5-案例4matter设备发现和管理)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：Matter Color Light控制](#6-案例5matter-color-light控制)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)
  - [7. 案例6：Matter数据存储和分析](#7-案例6matter数据存储和分析)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 实现代码](#72-实现代码)
    - [7.3 数据分析示例](#73-数据分析示例)
  - [8. 案例7：Matter设备组控制](#8-案例7matter设备组控制)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：Matter设备固件升级](#9-案例8matter设备固件升级)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 Schema定义](#92-schema定义)
    - [9.3 实现代码](#93-实现代码)
  - [10. 案例9：Matter多设备联动](#10-案例9matter多设备联动)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 Schema定义](#102-schema定义)
    - [10.3 实现代码](#103-实现代码)
  - [11. 案例10：Matter场景自动化](#11-案例10matter场景自动化)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)
  - [12. 案例11：Matter设备故障诊断](#12-案例11matter设备故障诊断)
    - [12.1 场景描述](#121-场景描述)
    - [12.2 Schema定义](#122-schema定义)
    - [12.3 实现代码](#123-实现代码)

---

## 1. 案例概述

本文档提供Matter Schema在实际应用中的实践案例。

---

## 2. 案例1：Matter On/Off Light控制

### 2.1 场景描述

**业务背景**：
用户需要通过Matter协议控制智能开关灯，实现远程开关控制、
状态查询和定时控制功能。

**技术挑战**：

- 需要建立Matter设备连接
- 需要处理设备离线情况
- 需要实现状态同步
- 需要记录操作历史

**解决方案**：
使用MatterDeviceController封装Matter SDK，实现设备连接、
命令发送和状态查询功能。

### 2.2 Schema定义

**Matter On/Off Light Schema**：

```json
{
  "device_id": "LIGHT001",
  "device_type": "OnOffLight",
  "endpoint_id": 1,
  "node_id": 0x12344321,
  "clusters": [{
    "cluster_id": 0x0006,
    "cluster_name": "OnOff",
    "attributes": {
      "on_off": false,
      "global_scene_control": true,
      "on_time": 0,
      "off_wait_time": 0,
      "start_up_on_off": "Off"
    },
    "commands": {
      "on": {
        "command_id": 0x00,
        "parameters": {}
      },
      "off": {
        "command_id": 0x01,
        "parameters": {}
      },
      "toggle": {
        "command_id": 0x02,
        "parameters": {}
      }
    }
  }]
}
```

### 2.3 实现代码

**完整的On/Off Light控制实现**：

```python
import asyncio
from matter_device_controller import MatterOnOffLightController
from matter_storage import MatterStorage
from datetime import datetime

# 初始化存储
storage = MatterStorage("postgresql://user:pass@localhost/matter")

# 创建设备控制器
light_controller = MatterOnOffLightController("LIGHT001", 0x12344321)

async def control_on_off_light():
    """控制On/Off Light"""
    try:
        # 连接设备
        connected = await light_controller.connect()
        if not connected:
            print("Failed to connect to device")
            return

        # 打开灯光
        print("Turning on light...")
        result = await light_controller.turn_on()
        if result:
            # 记录命令
            cmd_id = storage.store_command(
                "LIGHT001", 1, 0x0006, 0x00, "on", {}
            )
            storage.update_command_status(cmd_id, "Success")
            print("Light turned on successfully")
        else:
            storage.update_command_status(cmd_id, "Failed")
            print("Failed to turn on light")

        # 获取状态
        state = await light_controller.get_state()
        print(f"Current light state: {state}")

        # 等待3秒
        await asyncio.sleep(3)

        # 关闭灯光
        print("Turning off light...")
        result = await light_controller.turn_off()
        if result:
            cmd_id = storage.store_command(
                "LIGHT001", 1, 0x0006, 0x01, "off", {}
            )
            storage.update_command_status(cmd_id, "Success")
            print("Light turned off successfully")

        # 切换灯光
        print("Toggling light...")
        result = await light_controller.toggle()
        if result:
            cmd_id = storage.store_command(
                "LIGHT001", 1, 0x0006, 0x02, "toggle", {}
            )
            storage.update_command_status(cmd_id, "Success")
            print("Light toggled successfully")

        # 断开连接
        await light_controller.disconnect()

    except Exception as e:
        print(f"Error controlling light: {e}")

# 运行控制示例
if __name__ == "__main__":
    asyncio.run(control_on_off_light())
```

---

## 3. 案例2：Matter Door Lock控制

### 3.1 场景描述

**业务背景**：
用户需要通过Matter协议控制智能门锁，实现远程开锁、锁定、
状态查询和PIN码验证功能。

**技术挑战**：

- 需要安全的PIN码验证
- 需要处理门锁状态变化事件
- 需要记录开锁历史
- 需要处理异常情况（如门未关闭）

**解决方案**：
使用MatterDoorLockController实现门锁控制，集成PIN码验证
和事件监听功能。

### 3.2 Schema定义

**Matter Door Lock Schema**：

```json
{
  "device_id": "LOCK001",
  "device_type": "DoorLock",
  "endpoint_id": 1,
  "node_id": 0x12344322,
  "clusters": [{
    "cluster_id": 0x0101,
    "cluster_name": "DoorLock",
    "attributes": {
      "lock_state": 1,
      "lock_type": "DeadBolt",
      "actuator_enabled": true,
      "door_state": "Closed",
      "door_open_events": 0,
      "door_closed_events": 0,
      "open_period": 0
    },
    "commands": {
      "lock_door": {
        "command_id": 0x00,
        "parameters": {
          "pin_code": "1234"
        }
      },
      "unlock_door": {
        "command_id": 0x01,
        "parameters": {
          "pin_code": "1234"
        }
      }
    },
    "events": {
      "door_lock_alarm": {
        "event_id": 0x00,
        "alarm_code": "DoorForcedOpen"
      }
    }
  }]
}
```

### 3.3 实现代码

**完整的Door Lock控制实现**：

```python
import asyncio
from matter_device_controller import MatterDoorLockController
from matter_storage import MatterStorage

# 初始化存储
storage = MatterStorage("postgresql://user:pass@localhost/matter")

# 创建设备控制器
lock_controller = MatterDoorLockController("LOCK001", 0x12344322)

async def control_door_lock():
    """控制Door Lock"""
    try:
        # 连接设备
        connected = await lock_controller.connect()
        if not connected:
            print("Failed to connect to door lock")
            return

        # 获取当前锁状态
        lock_state = await lock_controller.get_lock_state()
        print(f"Current lock state: {lock_state}")

        # 如果已锁定，则解锁
        if lock_state == "Locked":
            print("Unlocking door...")
            pin_code = "1234"  # 实际应用中应从安全存储获取
            result = await lock_controller.unlock_door(pin_code)

            if result:
                cmd_id = storage.store_command(
                    "LOCK001", 1, 0x0101, 0x01, "unlock_door",
                    {"pin_code": "****"}  # 不存储实际PIN码
                )
                storage.update_command_status(cmd_id, "Success")

                # 记录事件
                storage.store_event(
                    "LOCK001", 1, 0x0101, 0x01, "DoorUnlocked",
                    {"timestamp": datetime.now().isoformat()}
                )
                print("Door unlocked successfully")
            else:
                print("Failed to unlock door")

        # 等待5秒
        await asyncio.sleep(5)

        # 锁定门
        print("Locking door...")
        result = await lock_controller.lock_door()

        if result:
            cmd_id = storage.store_command(
                "LOCK001", 1, 0x0101, 0x00, "lock_door", {}
            )
            storage.update_command_status(cmd_id, "Success")

            # 记录事件
            storage.store_event(
                "LOCK001", 1, 0x0101, 0x00, "DoorLocked",
                {"timestamp": datetime.now().isoformat()}
            )
            print("Door locked successfully")

        # 再次获取状态确认
        lock_state = await lock_controller.get_lock_state()
        print(f"Final lock state: {lock_state}")

        # 断开连接
        await lock_controller.disconnect()

    except Exception as e:
        print(f"Error controlling door lock: {e}")

# 运行控制示例
if __name__ == "__main__":
    asyncio.run(control_door_lock())
```

---

## 4. 案例3：Matter Thermostat控制

### 4.1 场景描述

**业务背景**：
用户需要通过Matter协议控制智能温控器，实现温度设置、
模式切换和温度监控功能。

**技术挑战**：

- 需要实时读取温度值
- 需要设置目标温度
- 需要切换运行模式（制冷/制热/自动）
- 需要处理温度范围限制

**解决方案**：
使用MatterThermostatController实现温控器控制，支持温度
读取、设置和模式切换功能。

### 4.2 Schema定义

**Matter Thermostat Schema**：

详见第4.2节原始定义。

### 4.3 实现代码

**完整的Thermostat控制实现**：

```python
import asyncio
from matter_device_controller import MatterThermostatController
from matter_storage import MatterStorage
from datetime import datetime

# 初始化存储
storage = MatterStorage("postgresql://user:pass@localhost/matter")

# 创建设备控制器
thermostat_controller = MatterThermostatController("THERMOSTAT001", 0x12344323)

async def control_thermostat():
    """控制Thermostat"""
    try:
        # 连接设备
        connected = await thermostat_controller.connect()
        if not connected:
            print("Failed to connect to thermostat")
            return

        # 获取当前温度
        current_temp = await thermostat_controller.get_current_temperature()
        print(f"Current temperature: {current_temp}°C")

        # 设置目标温度为26°C（制冷模式）
        print("Setting target temperature to 26°C (Cool mode)...")
        result = await thermostat_controller.set_target_temperature(26.0, "Cool")

        if result:
            # 设置系统模式为制冷
            await thermostat_controller.set_system_mode("Cool")

            # 记录命令
            cmd_id = storage.store_command(
                "THERMOSTAT001", 1, 0x0201, 0x00, "set_target_temperature",
                {"temperature": 26.0, "mode": "Cool"}
            )
            storage.update_command_status(cmd_id, "Success")
            print("Target temperature set successfully")

        # 等待并再次读取温度
        await asyncio.sleep(5)
        current_temp = await thermostat_controller.get_current_temperature()
        print(f"Current temperature after setting: {current_temp}°C")

        # 切换到自动模式
        print("Switching to Auto mode...")
        result = await thermostat_controller.set_system_mode("Auto")

        if result:
            cmd_id = storage.store_command(
                "THERMOSTAT001", 1, 0x0201, 0x00, "set_system_mode",
                {"mode": "Auto"}
            )
            storage.update_command_status(cmd_id, "Success")
            print("System mode switched to Auto")

        # 断开连接
        await thermostat_controller.disconnect()

    except Exception as e:
        print(f"Error controlling thermostat: {e}")

# 运行控制示例
if __name__ == "__main__":
    asyncio.run(control_thermostat())
```

---

## 5. 案例4：Matter设备发现和管理

### 5.1 场景描述

**业务背景**：
系统需要自动发现网络中的Matter设备，注册设备信息，
并建立设备连接池进行统一管理。

**技术挑战**：

- 需要实现设备发现协议
- 需要处理设备上线/下线
- 需要管理设备连接状态
- 需要存储设备信息

**解决方案**：
使用MatterDeviceDiscovery和MatterDeviceManager实现设备
发现和管理功能。

### 5.2 实现代码

**完整的设备发现和管理实现**：

```python
import asyncio
from matter_device_manager import MatterDeviceManager
from matter_storage import MatterStorage

# 初始化存储和管理器
storage = MatterStorage("postgresql://user:pass@localhost/matter")
device_manager = MatterDeviceManager(storage)

async def discover_and_manage_devices():
    """发现和管理设备"""
    try:
        # 发现设备
        print("Discovering Matter devices...")
        registered_ids = await device_manager.discover_and_register()
        print(f"Discovered and registered {len(registered_ids)} devices: {registered_ids}")

        # 连接所有设备
        for device_id in registered_ids:
            print(f"Connecting to device {device_id}...")
            connected = await device_manager.connect_device(device_id)
            if connected:
                print(f"Device {device_id} connected successfully")
            else:
                print(f"Failed to connect to device {device_id}")

        # 获取设备控制器并执行操作
        light_controller = device_manager.get_controller("LIGHT001")
        if light_controller:
            # 控制灯光
            await light_controller.turn_on()
            await asyncio.sleep(2)
            await light_controller.turn_off()

        # 断开所有设备
        for device_id in registered_ids:
            await device_manager.disconnect_device(device_id)
            print(f"Disconnected from device {device_id}")

    except Exception as e:
        print(f"Error in device discovery and management: {e}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(discover_and_manage_devices())
```

---

## 6. 案例5：Matter Color Light控制

### 6.1 场景描述

**业务背景**：
用户需要通过Matter协议控制彩色智能灯，实现色相、饱和度、
色温和亮度的精确控制。

**技术挑战**：

- 需要支持多种颜色空间（HSV、RGB、色温）
- 需要实现颜色转换
- 需要平滑的颜色过渡
- 需要保存和恢复颜色场景

**解决方案**：
使用MatterColorLightController实现完整的颜色控制功能。

### 6.2 实现代码

**完整的Color Light控制实现**：

```python
import asyncio
from matter_device_controller import MatterColorLightController
from matter_storage import MatterStorage

# 初始化存储
storage = MatterStorage("postgresql://user:pass@localhost/matter")

# 创建设备控制器
color_light_controller = MatterColorLightController("LIGHT003", 0x12344323)

async def control_color_light():
    """控制Color Light"""
    try:
        # 连接设备
        connected = await color_light_controller.connect()
        if not connected:
            print("Failed to connect to color light")
            return

        # 打开灯光
        await color_light_controller.turn_on()

        # 设置亮度为50%
        await color_light_controller.set_level(127)  # 127/254 = 50%
        print("Set brightness to 50%")

        # 设置色相和饱和度（绿色）
        await color_light_controller.set_hue_saturation(120, 200)
        print("Set color to green (Hue: 120, Saturation: 200)")

        await asyncio.sleep(3)

        # 设置色温（暖白光）
        await color_light_controller.set_color_temperature(400)
        print("Set color temperature to 400 mireds (warm white)")

        await asyncio.sleep(3)

        # 获取当前颜色状态
        hue_sat = await color_light_controller.get_hue_saturation()
        color_temp = await color_light_controller.get_color_temperature()
        level = await color_light_controller.get_level()

        print(f"Current color state:")
        print(f"  Hue: {hue_sat['hue']}, Saturation: {hue_sat['saturation']}")
        print(f"  Color Temperature: {color_temp} mireds")
        print(f"  Level: {level}/254")

        # 关闭灯光
        await color_light_controller.turn_off()

        # 断开连接
        await color_light_controller.disconnect()

    except Exception as e:
        print(f"Error controlling color light: {e}")

# 运行控制示例
if __name__ == "__main__":
    asyncio.run(control_color_light())
```

---

## 7. 案例6：Matter数据存储和分析

### 7.1 场景描述

**应用场景**：
使用PostgreSQL存储Matter设备数据，支持设备状态查询、
命令执行分析和设备使用统计。

### 7.2 实现代码

详见 `04_Transformation.md` 第6章。

### 7.3 数据分析示例

**设备使用统计查询**：

```python
from matter_storage import MatterStorage
from datetime import datetime, timedelta

storage = MatterStorage("postgresql://user:pass@localhost/matter")

# 查询设备集群统计
clusters = storage.get_cluster_statistics("LIGHT001")
print("Device clusters:")
for cluster in clusters:
    print(f"  {cluster['cluster_name']}: {cluster['attribute_count']} attributes")

# 查询命令执行统计
start_time = datetime.now() - timedelta(days=7)
cmd_stats = storage.get_command_statistics(start_time)
print("\nCommand statistics:")
for stat in cmd_stats:
    print(f"  {stat['command_name']}: {stat['count']} executions, "
          f"avg time: {stat['avg_execution_time']:.2f}s")

# 查询设备使用统计
usage_stats = storage.get_device_usage_statistics("LIGHT001", days=7)
print("\nDevice usage statistics:")
print(f"  Active days: {usage_stats['active_days']}")
print(f"  Total commands: {usage_stats['total_commands']}")
print(f"  Success rate: {usage_stats['success_commands'] / usage_stats['total_commands'] * 100:.1f}%")
print(f"  Avg response time: {usage_stats['avg_response_time']:.2f}s")
```

---

## 8. 案例7：Matter设备组控制

### 8.1 场景描述

**业务背景**：
智能家居场景中，用户需要同时控制多个设备，例如：

- 同时打开/关闭多个房间的灯光
- 同时调整多个温控器的温度
- 创建场景联动（如"回家模式"、"睡眠模式"）

**技术挑战**：

- 需要将多个设备组织成组
- 需要支持组内设备的批量控制
- 需要处理组内设备的部分失败情况
- 需要记录组操作的执行历史

**解决方案**：
使用Matter设备组功能，将多个设备组织成逻辑组，实现批量控制和场景联动。

### 8.2 Schema定义

**Matter设备组Schema**：

```json
{
  "group_id": 1,
  "group_name": "客厅灯光组",
  "devices": [
    {
      "device_id": "LIGHT001",
      "endpoint_id": 1,
      "device_type": "DimmableLight"
    },
    {
      "device_id": "LIGHT002",
      "endpoint_id": 1,
      "device_type": "DimmableLight"
    },
    {
      "device_id": "LIGHT003",
      "endpoint_id": 1,
      "device_type": "ColorLight"
    }
  ],
  "scenes": [
    {
      "scene_id": "scene_bright",
      "scene_name": "明亮模式",
      "actions": [
        {
          "device_id": "LIGHT001",
          "cluster_id": 0x0008,
          "command": "move_to_level",
          "parameters": {"level": 254, "transition_time": 0}
        },
        {
          "device_id": "LIGHT002",
          "cluster_id": 0x0008,
          "command": "move_to_level",
          "parameters": {"level": 254, "transition_time": 0}
        }
      ]
    }
  ]
}
```

### 8.3 实现代码

**完整的设备组控制实现**：

```python
import asyncio
import logging
from typing import List, Dict, Optional
from matter_device_controller import (
    MatterDeviceController,
    MatterDimmableLightController,
    MatterColorLightController
)
from matter_storage import MatterStorage

logger = logging.getLogger(__name__)

class MatterDeviceGroupController:
    """Matter设备组控制器"""

    def __init__(self, group_id: int, group_name: str, storage: MatterStorage):
        self.group_id = group_id
        self.group_name = group_name
        self.storage = storage
        self.devices: Dict[str, MatterDeviceController] = {}
        self.scenes: Dict[str, Dict] = {}

    async def initialize(self):
        """初始化设备组"""
        # 从存储中加载组内设备
        group_devices = self.storage.get_group_devices(self.group_id)

        for device_info in group_devices:
            device_id = device_info["device_id"]
            device_type = device_info["device_type"]

            # 根据设备类型创建控制器
            if device_type == "DimmableLight":
                controller = MatterDimmableLightController(
                    device_id,
                    device_info.get("node_id", 0x12344321),
                    device_info.get("endpoint_id", 1)
                )
            elif device_type == "ExtendedColorLight":
                controller = MatterColorLightController(
                    device_id,
                    device_info.get("node_id", 0x12344321),
                    device_info.get("endpoint_id", 1)
                )
            else:
                logger.warning(f"Unsupported device type: {device_type}")
                continue

            # 连接设备
            if await controller.connect():
                self.devices[device_id] = controller
                logger.info(f"Added device {device_id} to group {self.group_name}")
            else:
                logger.error(f"Failed to connect device {device_id}")

    async def group_turn_on(self) -> Dict[str, bool]:
        """组内所有设备打开"""
        results = {}

        for device_id, controller in self.devices.items():
            if isinstance(controller, MatterOnOffLightController):
                try:
                    result = await controller.turn_on()
                    results[device_id] = result
                except Exception as e:
                    logger.error(f"Failed to turn on {device_id}: {e}")
                    results[device_id] = False
            else:
                logger.warning(f"Device {device_id} does not support On/Off")
                results[device_id] = False

        return results

    async def group_turn_off(self) -> Dict[str, bool]:
        """组内所有设备关闭"""
        results = {}

        for device_id, controller in self.devices.items():
            if isinstance(controller, MatterOnOffLightController):
                try:
                    result = await controller.turn_off()
                    results[device_id] = result
                except Exception as e:
                    logger.error(f"Failed to turn off {device_id}: {e}")
                    results[device_id] = False
            else:
                logger.warning(f"Device {device_id} does not support On/Off")
                results[device_id] = False

        return results

    async def group_set_level(self, level: int, transition_time: int = 0) -> Dict[str, bool]:
        """组内所有可调光设备设置亮度"""
        results = {}

        for device_id, controller in self.devices.items():
            if isinstance(controller, MatterDimmableLightController):
                try:
                    result = await controller.set_level(level)
                    results[device_id] = result
                except Exception as e:
                    logger.error(f"Failed to set level for {device_id}: {e}")
                    results[device_id] = False
            else:
                logger.warning(f"Device {device_id} does not support level control")
                results[device_id] = False

        return results

    async def execute_scene(self, scene_id: str) -> Dict[str, bool]:
        """执行场景"""
        if scene_id not in self.scenes:
            logger.error(f"Scene {scene_id} not found")
            return {}

        scene = self.scenes[scene_id]
        results = {}

        # 并行执行所有场景动作
        tasks = []
        for action in scene.get("actions", []):
            device_id = action["device_id"]
            controller = self.devices.get(device_id)

            if not controller:
                logger.error(f"Device {device_id} not found in group")
                results[device_id] = False
                continue

            # 根据命令类型执行
            command = action.get("command")
            parameters = action.get("parameters", {})

            if command == "turn_on":
                task = controller.turn_on()
            elif command == "turn_off":
                task = controller.turn_off()
            elif command == "move_to_level":
                task = controller.set_level(parameters.get("level", 128))
            elif command == "set_color_temperature":
                task = controller.set_color_temperature(parameters.get("color_temp_mireds", 250))
            else:
                logger.warning(f"Unknown command: {command}")
                results[device_id] = False
                continue

            tasks.append((device_id, task))

        # 等待所有任务完成
        for device_id, task in tasks:
            try:
                result = await task
                results[device_id] = result
            except Exception as e:
                logger.error(f"Failed to execute action for {device_id}: {e}")
                results[device_id] = False

        return results

    def add_scene(self, scene_id: str, scene_name: str, actions: List[Dict]):
        """添加场景"""
        self.scenes[scene_id] = {
            "scene_id": scene_id,
            "scene_name": scene_name,
            "actions": actions
        }
        logger.info(f"Added scene {scene_name} to group {self.group_name}")

    async def cleanup(self):
        """清理资源"""
        for device_id, controller in self.devices.items():
            await controller.disconnect()

async def control_device_group():
    """设备组控制示例"""
    # 初始化存储
    storage = MatterStorage("postgresql://user:pass@localhost/matter")

    # 创建设备组
    group_id = storage.create_device_group(1, "客厅灯光组")

    # 添加设备到组
    storage.add_device_to_group(1, "LIGHT001", 1)
    storage.add_device_to_group(1, "LIGHT002", 1)
    storage.add_device_to_group(1, "LIGHT003", 1)

    # 创建设备组控制器
    group_controller = MatterDeviceGroupController(1, "客厅灯光组", storage)
    await group_controller.initialize()

    # 执行组操作
    print("Turning on all devices in group...")
    results = await group_controller.group_turn_on()
    print(f"Results: {results}")

    # 设置组内所有设备亮度
    print("\nSetting all devices to level 200...")
    results = await group_controller.group_set_level(200)
    print(f"Results: {results}")

    # 添加场景
    group_controller.add_scene(
        "scene_bright",
        "明亮模式",
        [
            {
                "device_id": "LIGHT001",
                "cluster_id": 0x0008,
                "command": "move_to_level",
                "parameters": {"level": 254}
            },
            {
                "device_id": "LIGHT002",
                "cluster_id": 0x0008,
                "command": "move_to_level",
                "parameters": {"level": 254}
            }
        ]
    )

    # 执行场景
    print("\nExecuting scene 'bright'...")
    results = await group_controller.execute_scene("scene_bright")
    print(f"Results: {results}")

    # 清理
    await group_controller.cleanup()
    storage.close()

if __name__ == "__main__":
    asyncio.run(control_device_group())
```

---

## 9. 案例8：Matter设备固件升级

### 9.1 场景描述

**业务背景**：
智能家居设备需要定期进行固件升级，以修复bug、添加新功能或提升性能。Matter协议支持OTA（Over-The-Air）固件升级功能。

**技术挑战**：

- 需要支持固件版本检查
- 需要支持固件下载和验证
- 需要支持升级进度监控
- 需要处理升级失败和回滚
- 需要记录升级历史

**解决方案**：
使用Matter OTA升级功能，结合PostgreSQL存储升级记录，实现完整的固件升级管理。

### 9.2 Schema定义

**Matter固件升级Schema**：

```json
{
  "device_id": "LIGHT001",
  "current_firmware_version": "1.0.0",
  "target_firmware_version": "1.1.0",
  "firmware_info": {
    "firmware_url": "https://example.com/firmware/light_v1.1.0.bin",
    "firmware_size": 524288,
    "firmware_checksum": "sha256:abc123...",
    "firmware_format": "OTA",
    "min_hardware_version": 1,
    "max_hardware_version": 2
  },
  "upgrade_policy": {
    "auto_upgrade": false,
    "scheduled_time": "2025-01-22T02:00:00Z",
    "rollback_on_failure": true
  }
}
```

### 9.3 实现代码

**完整的固件升级实现**：

```python
import asyncio
import logging
import hashlib
import aiohttp
from typing import Dict, Optional, Callable
from datetime import datetime
from matter_device_controller import MatterDeviceController
from matter_storage import MatterStorage

logger = logging.getLogger(__name__)

class MatterFirmwareUpdater:
    """Matter设备固件升级器"""

    def __init__(self, device_controller: MatterDeviceController,
                 storage: MatterStorage):
        self.device_controller = device_controller
        self.storage = storage
        self.device_id = device_controller.device_id
        self.upgrade_progress_callback: Optional[Callable] = None

    async def check_firmware_version(self) -> Optional[str]:
        """检查当前固件版本"""
        try:
            # 读取Basic Cluster的SoftwareVersion属性
            version = await self.device_controller.read_attribute(
                0x0028,  # Basic Cluster
                0x0009   # SoftwareVersion
            )
            return version if version else None
        except Exception as e:
            logger.error(f"Failed to check firmware version: {e}")
            return None

    async def download_firmware(self, firmware_url: str) -> bytes:
        """下载固件文件"""
        async with aiohttp.ClientSession() as session:
            async with session.get(firmware_url) as response:
                if response.status == 200:
                    firmware_data = await response.read()
                    logger.info(f"Downloaded firmware: {len(firmware_data)} bytes")
                    return firmware_data
                else:
                    raise Exception(f"Failed to download firmware: HTTP {response.status}")

    def verify_firmware_checksum(self, firmware_data: bytes,
                                expected_checksum: str) -> bool:
        """验证固件校验和"""
        # 提取算法和哈希值
        if expected_checksum.startswith("sha256:"):
            algorithm = "sha256"
            expected_hash = expected_checksum[7:]
        elif expected_checksum.startswith("sha1:"):
            algorithm = "sha1"
            expected_hash = expected_checksum[5:]
        else:
            logger.warning(f"Unknown checksum format: {expected_checksum}")
            return False

        # 计算实际哈希值
        if algorithm == "sha256":
            actual_hash = hashlib.sha256(firmware_data).hexdigest()
        elif algorithm == "sha1":
            actual_hash = hashlib.sha1(firmware_data).hexdigest()
        else:
            return False

        return actual_hash.lower() == expected_hash.lower()

    async def upgrade_firmware(self, firmware_url: str, firmware_version: str,
                              firmware_size: int = None,
                              firmware_checksum: str = None,
                              progress_callback: Callable = None) -> bool:
        """执行固件升级"""
        self.upgrade_progress_callback = progress_callback

        # 记录升级开始
        update_id = self.storage.store_firmware_update(
            self.device_id,
            firmware_version,
            firmware_url,
            firmware_size,
            firmware_checksum
        )

        try:
            # 检查当前版本
            current_version = await self.check_firmware_version()
            logger.info(f"Current firmware version: {current_version}")

            # 下载固件
            if progress_callback:
                progress_callback(0, "Downloading firmware...")

            firmware_data = await self.download_firmware(firmware_url)

            # 验证固件
            if firmware_checksum:
                if progress_callback:
                    progress_callback(10, "Verifying firmware...")

                if not self.verify_firmware_checksum(firmware_data, firmware_checksum):
                    raise Exception("Firmware checksum verification failed")

            # 更新状态为进行中
            self.storage.update_firmware_status(update_id, "InProgress")

            # 发送固件到设备（这里需要实际的Matter OTA升级命令）
            if progress_callback:
                progress_callback(20, "Uploading firmware to device...")

            # 模拟升级过程
            await self._simulate_firmware_upgrade(firmware_data, progress_callback)

            # 验证升级结果
            if progress_callback:
                progress_callback(90, "Verifying upgrade...")

            new_version = await self.check_firmware_version()
            if new_version == firmware_version:
                self.storage.update_firmware_status(update_id, "Completed")
                logger.info(f"Firmware upgrade completed: {current_version} -> {new_version}")
                return True
            else:
                raise Exception(f"Version mismatch: expected {firmware_version}, got {new_version}")

        except Exception as e:
            logger.error(f"Firmware upgrade failed: {e}")
            self.storage.update_firmware_status(update_id, "Failed", str(e))
            return False

    async def _simulate_firmware_upgrade(self, firmware_data: bytes,
                                        progress_callback: Callable):
        """模拟固件升级过程"""
        # 模拟升级进度
        for progress in range(20, 90, 10):
            await asyncio.sleep(0.5)
            if progress_callback:
                progress_callback(progress, f"Upgrading... {progress}%")

    async def rollback_firmware(self, previous_version: str) -> bool:
        """回滚到之前的固件版本"""
        logger.info(f"Rolling back to version {previous_version}")
        # 这里需要实际的回滚逻辑
        # Matter协议可能不支持直接回滚，需要重新升级到之前的版本
        return False

async def upgrade_device_firmware():
    """固件升级示例"""
    # 初始化存储
    storage = MatterStorage("postgresql://user:pass@localhost/matter")

    # 创建设备控制器
    device_controller = MatterDeviceController("LIGHT001", 0x12344321)
    await device_controller.connect()

    # 创建固件升级器
    updater = MatterFirmwareUpdater(device_controller, storage)

    # 检查当前版本
    current_version = await updater.check_firmware_version()
    print(f"Current firmware version: {current_version}")

    # 定义进度回调
    def progress_callback(progress: int, message: str):
        print(f"[{progress}%] {message}")

    # 执行升级
    success = await updater.upgrade_firmware(
        firmware_url="https://example.com/firmware/light_v1.1.0.bin",
        firmware_version="1.1.0",
        firmware_size=524288,
        firmware_checksum="sha256:abc123def456...",
        progress_callback=progress_callback
    )

    if success:
        print("Firmware upgrade completed successfully!")
    else:
        print("Firmware upgrade failed!")

    # 查询升级历史
    updates = storage.get_firmware_updates(device_id="LIGHT001")
    print("\nFirmware update history:")
    for update in updates:
        print(f"  Version: {update['firmware_version']}, "
              f"Status: {update['update_status']}, "
              f"Time: {update['created_at']}")

    await device_controller.disconnect()
    storage.close()

if __name__ == "__main__":
    asyncio.run(upgrade_device_firmware())
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

---

## 10. 案例9：Matter多设备联动

### 10.1 场景描述

**业务背景**：
Matter多设备联动系统实现多个Matter设备之间的
协同工作，例如开门时自动开灯、温度变化时自动
调节空调等。

**技术挑战**：

- 需要设备状态同步
- 需要联动规则管理
- 需要事件触发机制
- 需要联动效果评估

**解决方案**：
使用Matter_Schema定义设备联动规则，
使用Matter SDK实现设备联动，
使用MatterStorage存储联动数据。

### 10.2 Schema定义

**Matter多设备联动Schema**：

```dsl
schema MatterDeviceCoordination {
  coordination_id: String @value("COORD-20250121-001") @required
  coordination_name: String @value("回家场景联动") @required
  trigger_device: {
    device_id: String @value("DOOR-LOCK-001")
    device_type: Enum { DoorLock } @value(DoorLock)
    trigger_event: Enum { Unlocked } @value(Unlocked)
  } @required

  target_devices: [
    {
      device_id: String @value("LIGHT-001")
      device_type: Enum { Light } @value(Light)
      action: {
        cluster_id: Integer @value(6) @comment("On/Off Cluster")
        command_id: Integer @value(1) @comment("On Command")
        parameters: {
          on_off: Boolean @value(true)
        }
      }
    },
    {
      device_id: String @value("THERMOSTAT-001")
      device_type: Enum { Thermostat } @value(Thermostat)
      action: {
        cluster_id: Integer @value(513) @comment("Thermostat Cluster")
        command_id: Integer @value(0) @comment("Set Setpoint")
        parameters: {
          setpoint: Decimal @value(22.0) @unit("Celsius")
        }
      }
    }
  ] @required

  coordination_status: {
    status: Enum { Active } @value(Active)
    last_triggered: DateTime @value("2025-01-21T18:00:00")
    trigger_count: Integer @value(5)
    success_rate: Decimal @value(1.0) @range(0.0, 1.0)
  } @required
} @standard("Matter")
```

### 10.3 实现代码

```python
from matter_storage import MatterStorage
from matter_sdk_wrapper import MatterSDKWrapper
from datetime import datetime

async def matter_device_coordination():
    """Matter多设备联动示例"""
    storage = MatterStorage("postgresql://user:password@localhost/matter_db")
    sdk = MatterSDKWrapper()

    # 联动规则
    coordination_rule = {
        "coordination_id": "COORD-20250121-001",
        "coordination_name": "回家场景联动",
        "trigger_device": {
            "device_id": "DOOR-LOCK-001",
            "device_type": "DoorLock",
            "trigger_event": "Unlocked"
        },
        "target_devices": [
            {
                "device_id": "LIGHT-001",
                "device_type": "Light",
                "action": {
                    "cluster_id": 6,  # On/Off Cluster
                    "command_id": 1,  # On Command
                    "parameters": {"on_off": True}
                }
            },
            {
                "device_id": "THERMOSTAT-001",
                "device_type": "Thermostat",
                "action": {
                    "cluster_id": 513,  # Thermostat Cluster
                    "command_id": 0,  # Set Setpoint
                    "parameters": {"setpoint": 22.0}
                }
            }
        ]
    }

    # 监听触发设备事件
    async def on_door_unlocked(device_id, event_data):
        """门锁解锁事件处理"""
        print(f"Door unlocked: {device_id}")

        # 执行联动动作
        for target_device in coordination_rule["target_devices"]:
            try:
                result = await sdk.send_command(
                    target_device["device_id"],
                    target_device["action"]["cluster_id"],
                    target_device["action"]["command_id"],
                    target_device["action"]["parameters"]
                )

                if result:
                    print(f"  {target_device['device_id']} action executed successfully")
                else:
                    print(f"  {target_device['device_id']} action failed")
            except Exception as e:
                print(f"  Error executing action on {target_device['device_id']}: {e}")

        # 记录联动事件
        coordination_data = {
            "coordination_id": coordination_rule["coordination_id"],
            "trigger_device_id": device_id,
            "trigger_time": datetime.now(),
            "target_devices": [d["device_id"] for d in coordination_rule["target_devices"]],
            "status": "Completed"
        }

        storage.store_coordination_event(coordination_data)

    # 注册事件监听
    await sdk.subscribe_to_events("DOOR-LOCK-001", on_door_unlocked)

    print("Matter device coordination system started")
    print(f"  Coordination: {coordination_rule['coordination_name']}")
    print(f"  Trigger device: {coordination_rule['trigger_device']['device_id']}")
    print(f"  Target devices: {len(coordination_rule['target_devices'])}")

    return coordination_rule

if __name__ == "__main__":
    import asyncio
    asyncio.run(matter_device_coordination())
```

---

## 11. 案例10：Matter场景自动化

### 11.1 场景描述

**业务背景**：
Matter场景自动化系统根据时间、环境条件等
自动触发设备场景，例如早晨自动开灯、温度
过高时自动开启空调等。

**技术挑战**：

- 需要时间条件判断
- 需要环境条件监测
- 需要场景规则管理
- 需要自动化效果评估

**解决方案**：
使用Matter_Schema定义场景自动化规则，
使用Matter SDK实现场景自动化，
使用MatterStorage存储自动化数据。

### 11.2 Schema定义

**Matter场景自动化Schema**：

```dsl
schema MatterSceneAutomation {
  automation_id: String @value("AUTO-20250121-001") @required
  automation_name: String @value("早晨自动场景") @required

  trigger_conditions: {
    time_condition: {
      enabled: Boolean @value(true)
      time: Time @value("07:00:00")
      days_of_week: [Enum] @value([Monday, Tuesday, Wednesday, Thursday, Friday])
    }
    environment_condition: {
      enabled: Boolean @value(true)
      sensor_device_id: String @value("SENSOR-001")
      condition_type: Enum { Temperature } @value(Temperature)
      threshold: Decimal @value(25.0) @unit("Celsius")
      operator: Enum { GreaterThan } @value(GreaterThan)
    }
  } @required

  scene_actions: [
    {
      device_id: String @value("LIGHT-001")
      action: {
        cluster_id: Integer @value(6)
        command_id: Integer @value(1)
        parameters: {
          on_off: Boolean @value(true)
          brightness: Integer @value(80) @range(0, 100)
        }
      }
    },
    {
      device_id: String @value("CURTAIN-001")
      action: {
        cluster_id: Integer @value(258) @comment("Window Covering Cluster")
        command_id: Integer @value(1) @comment("Up Command")
        parameters: {
          lift_percent: Integer @value(100)
        }
      }
    }
  ] @required

  automation_status: {
    status: Enum { Active } @value(Active)
    last_executed: DateTime @value("2025-01-21T07:00:00")
    execution_count: Integer @value(30)
    success_rate: Decimal @value(0.97) @range(0.0, 1.0)
  } @required
} @standard("Matter")
```

### 11.3 实现代码

```python
from matter_storage import MatterStorage
from matter_sdk_wrapper import MatterSDKWrapper
from datetime import datetime, time

async def matter_scene_automation():
    """Matter场景自动化示例"""
    storage = MatterStorage("postgresql://user:password@localhost/matter_db")
    sdk = MatterSDKWrapper()

    # 自动化规则
    automation_rule = {
        "automation_id": "AUTO-20250121-001",
        "automation_name": "早晨自动场景",
        "trigger_conditions": {
            "time_condition": {
                "enabled": True,
                "time": time(7, 0, 0),
                "days_of_week": [0, 1, 2, 3, 4]  # Monday to Friday
            },
            "environment_condition": {
                "enabled": True,
                "sensor_device_id": "SENSOR-001",
                "condition_type": "Temperature",
                "threshold": 25.0,
                "operator": "GreaterThan"
            }
        },
        "scene_actions": [
            {
                "device_id": "LIGHT-001",
                "action": {
                    "cluster_id": 6,
                    "command_id": 1,
                    "parameters": {"on_off": True, "brightness": 80}
                }
            },
            {
                "device_id": "CURTAIN-001",
                "action": {
                    "cluster_id": 258,
                    "command_id": 1,
                    "parameters": {"lift_percent": 100}
                }
            }
        ]
    }

    # 检查触发条件
    def check_trigger_conditions(rule):
        """检查触发条件"""
        conditions_met = True

        # 检查时间条件
        if rule["trigger_conditions"]["time_condition"]["enabled"]:
            current_time = datetime.now().time()
            target_time = rule["trigger_conditions"]["time_condition"]["time"]
            current_day = datetime.now().weekday()
            days_of_week = rule["trigger_conditions"]["time_condition"]["days_of_week"]

            if current_time.hour != target_time.hour or \
               current_time.minute != target_time.minute or \
               current_day not in days_of_week:
                conditions_met = False

        # 检查环境条件
        if rule["trigger_conditions"]["environment_condition"]["enabled"]:
            sensor_id = rule["trigger_conditions"]["environment_condition"]["sensor_device_id"]
            condition_type = rule["trigger_conditions"]["environment_condition"]["condition_type"]
            threshold = rule["trigger_conditions"]["environment_condition"]["threshold"]
            operator = rule["trigger_conditions"]["environment_condition"]["operator"]

            # 获取传感器数据（简化示例）
            sensor_value = 26.5  # 假设从传感器读取

            if operator == "GreaterThan" and sensor_value <= threshold:
                conditions_met = False
            elif operator == "LessThan" and sensor_value >= threshold:
                conditions_met = False

        return conditions_met

    # 执行场景动作
    async def execute_scene_actions(rule):
        """执行场景动作"""
        success_count = 0

        for action in rule["scene_actions"]:
            try:
                result = await sdk.send_command(
                    action["device_id"],
                    action["action"]["cluster_id"],
                    action["action"]["command_id"],
                    action["action"]["parameters"]
                )

                if result:
                    success_count += 1
                    print(f"  {action['device_id']} action executed successfully")
                else:
                    print(f"  {action['device_id']} action failed")
            except Exception as e:
                print(f"  Error executing action on {action['device_id']}: {e}")

        return success_count

    # 自动化循环
    while True:
        if check_trigger_conditions(automation_rule):
            print(f"Trigger conditions met for: {automation_rule['automation_name']}")

            success_count = await execute_scene_actions(automation_rule)
            total_actions = len(automation_rule["scene_actions"])
            success_rate = success_count / total_actions if total_actions > 0 else 0

            # 记录自动化执行
            automation_data = {
                "automation_id": automation_rule["automation_id"],
                "execution_time": datetime.now(),
                "success_count": success_count,
                "total_actions": total_actions,
                "success_rate": success_rate,
                "status": "Completed" if success_rate == 1.0 else "Partial"
            }

            storage.store_automation_event(automation_data)

            print(f"Automation executed: {success_count}/{total_actions} actions succeeded")

        # 等待1分钟再检查
        await asyncio.sleep(60)

    return automation_rule

if __name__ == "__main__":
    import asyncio
    asyncio.run(matter_scene_automation())
```

---

## 12. 案例11：Matter设备故障诊断

### 12.1 场景描述

**业务背景**：
Matter设备故障诊断系统监测设备状态，
识别设备故障，提供故障诊断和修复建议。

**技术挑战**：

- 需要设备状态监测
- 需要故障模式识别
- 需要诊断算法
- 需要修复建议生成

**解决方案**：
使用Matter_Schema监测设备状态，
使用AI算法进行故障诊断，
使用MatterStorage存储诊断数据。

### 12.2 Schema定义

**Matter设备故障诊断Schema**：

```dsl
schema MatterDeviceDiagnostics {
  diagnosis_session_id: String @value("DIAG-20250121-001") @required
  device_id: String @value("LIGHT-001") @required
  diagnosis_time: DateTime @value("2025-01-21T10:00:00") @required

  device_status: {
    online: Boolean @value(false)
    last_seen: DateTime @value("2025-01-21T09:30:00")
    response_time: Decimal @value(5000.0) @unit("ms")
    error_count: Integer @value(5)
    last_error: String @value("Timeout")
  } @required

  diagnostic_results: {
    fault_detected: Boolean @value(true)
    fault_type: Enum { Connectivity } @value(Connectivity)
    fault_severity: Enum { Medium } @value(Medium)
    fault_description: String @value("设备响应超时")
    root_cause: String @value("网络连接不稳定")
    confidence: Decimal @value(0.85) @range(0.0, 1.0)
  } @required

  repair_recommendations: [
    {
      recommendation: String @value("检查网络连接")
      priority: Enum { High } @value(High)
      expected_fix_probability: Decimal @value(0.80)
    },
    {
      recommendation: String @value("重启设备")
      priority: Enum { Medium } @value(Medium)
      expected_fix_probability: Decimal @value(0.60)
    }
  ] @required
} @standard("Matter")
```

### 12.3 实现代码

```python
from matter_storage import MatterStorage
from matter_sdk_wrapper import MatterSDKWrapper
from datetime import datetime, timedelta

async def matter_device_diagnostics():
    """Matter设备故障诊断示例"""
    storage = MatterStorage("postgresql://user:password@localhost/matter_db")
    sdk = MatterSDKWrapper()

    # 设备状态
    device_id = "LIGHT-001"
    device_status = {
        "online": False,
        "last_seen": datetime.now() - timedelta(minutes=30),
        "response_time": 5000.0,
        "error_count": 5,
        "last_error": "Timeout"
    }

    # 故障诊断算法
    def diagnose_device_fault(status):
        """诊断设备故障"""
        fault_detected = False
        fault_type = None
        fault_severity = None
        fault_description = None
        root_cause = None
        confidence = 0.0
        recommendations = []

        # 检查在线状态
        if not status["online"]:
            time_since_last_seen = datetime.now() - status["last_seen"]

            if time_since_last_seen.total_seconds() > 3600:  # 1小时
                fault_detected = True
                fault_type = "Connectivity"
                fault_severity = "High"
                fault_description = "设备长时间离线"
                root_cause = "网络连接中断或设备故障"
                confidence = 0.90
                recommendations.append({
                    "recommendation": "检查网络连接和设备电源",
                    "priority": "High",
                    "expected_fix_probability": 0.70
                })
            else:
                fault_detected = True
                fault_type = "Connectivity"
                fault_severity = "Medium"
                fault_description = "设备暂时离线"
                root_cause = "网络连接不稳定"
                confidence = 0.75
                recommendations.append({
                    "recommendation": "检查网络连接",
                    "priority": "High",
                    "expected_fix_probability": 0.80
                })

        # 检查响应时间
        if status["response_time"] > 3000:  # 3秒
            fault_detected = True
            if fault_type is None:
                fault_type = "Performance"
                fault_severity = "Medium"
                fault_description = "设备响应缓慢"
                root_cause = "网络延迟或设备负载过高"
                confidence = 0.70
                recommendations.append({
                    "recommendation": "检查网络延迟和设备负载",
                    "priority": "Medium",
                    "expected_fix_probability": 0.60
                })

        # 检查错误计数
        if status["error_count"] > 3:
            fault_detected = True
            if fault_type is None:
                fault_type = "Reliability"
                fault_severity = "Medium"
                fault_description = "设备频繁出错"
                root_cause = "设备不稳定或配置错误"
                confidence = 0.80
                recommendations.append({
                    "recommendation": "重启设备",
                    "priority": "Medium",
                    "expected_fix_probability": 0.60
                })
                recommendations.append({
                    "recommendation": "检查设备配置",
                    "priority": "Low",
                    "expected_fix_probability": 0.50
                })

        return {
            "fault_detected": fault_detected,
            "fault_type": fault_type,
            "fault_severity": fault_severity,
            "fault_description": fault_description,
            "root_cause": root_cause,
            "confidence": confidence,
            "recommendations": recommendations
        }

    # 执行诊断
    diagnostic_results = diagnose_device_fault(device_status)

    # 存储诊断数据
    diagnosis_data = {
        "diagnosis_session_id": "DIAG-20250121-001",
        "device_id": device_id,
        "diagnosis_time": datetime.now(),
        "device_online": device_status["online"],
        "device_last_seen": device_status["last_seen"],
        "device_response_time": device_status["response_time"],
        "device_error_count": device_status["error_count"],
        "device_last_error": device_status["last_error"],
        "fault_detected": diagnostic_results["fault_detected"],
        "fault_type": diagnostic_results["fault_type"],
        "fault_severity": diagnostic_results["fault_severity"],
        "fault_description": diagnostic_results["fault_description"],
        "root_cause": diagnostic_results["root_cause"],
        "confidence": diagnostic_results["confidence"],
        "recommendations": diagnostic_results["recommendations"]
    }

    # 存储到数据库
    diagnosis_id = storage.store_diagnostic_data(diagnosis_data)
    print(f"Device diagnosis stored: {diagnosis_id}")

    print(f"\nMatter Device Diagnostics:")
    print(f"  Device: {device_id}")
    print(f"  Fault detected: {diagnostic_results['fault_detected']}")
    if diagnostic_results['fault_detected']:
        print(f"  Fault type: {diagnostic_results['fault_type']}")
        print(f"  Fault severity: {diagnostic_results['fault_severity']}")
        print(f"  Fault description: {diagnostic_results['fault_description']}")
        print(f"  Root cause: {diagnostic_results['root_cause']}")
        print(f"  Confidence: {diagnostic_results['confidence']:.2f}")
        print(f"  Recommendations: {len(diagnostic_results['recommendations'])}")
        for i, rec in enumerate(diagnostic_results['recommendations'], 1):
            print(f"    {i}. {rec['recommendation']} (Priority: {rec['priority']})")

    return diagnosis_data

if __name__ == "__main__":
    import asyncio
    asyncio.run(matter_device_diagnostics())
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21


---

## 12. 案例12：Matter多管理员(FMA)配置管理

### 12.1 场景描述

**业务背景**：
Matter多管理员(Fabric Multi-Admin)功能允许一个设备被多个生态系统（如Apple Home、Google Home、Amazon Alexa）同时管理。需要实现安全的Commissioning流程、ACL权限管理和跨Fabric的设备状态同步。

**技术挑战**：

- 需要管理多个Fabric的Credentials
- 需要精细的ACL权限控制
- 需要处理跨Fabric的命令冲突
- 需要确保Commissioning安全性

**解决方案**：
使用Matter的Multi-Admin功能，结合PostgreSQL存储各Fabric的配置和ACL规则，实现安全的多管理员管理。

### 12.2 Schema定义

**多管理员配置Schema**：

```json
{
  "device_id": "MATTER_LIGHT_001",
  "fabrics": [
    {
      "fabric_id": 1,
      "fabric_name": "Apple Home",
      "node_id": 12345,
      "is_commissioner": true,
      "acl_entries": [
        {
          "privilege": 5,
          "auth_mode": "CASE",
          "subjects": [12345],
          "targets": [{"cluster": 6, "endpoint": 1}]
        }
      ]
    },
    {
      "fabric_id": 2,
      "fabric_name": "Google Home",
      "node_id": 67890,
      "acl_entries": [
        {
          "privilege": 3,
          "auth_mode": "CASE",
          "subjects": [67890],
          "targets": [{"cluster": 6, "endpoint": 1}]
        }
      ]
    }
  ],
  "operational_credentials": {
    "root_certificate": "...",
    "intermediate_certificate": "...",
    "operational_certificate": "..."
  }
}
```

### 12.3 实现代码

```python
from matter_storage import MatterStorage
from typing import List, Dict

class MatterMultiAdminManager:
    """Matter多管理员管理器"""

    def __init__(self, storage: MatterStorage):
        self.storage = storage

    def commission_to_new_fabric(self, device_id: str, fabric_id: int,
                                 fabric_name: str, node_id: int,
                                 passcode: int, discriminator: int) -> bool:
        """将设备Commission到新Fabric"""
        try:
            # 记录Commissioning过程
            self.storage.store_commissioning_record(
                device_id=device_id,
                node_id=node_id,
                fabric_id=fabric_id,
                passcode=passcode,
                discriminator=discriminator,
                success=True
            )

            # 存储Fabric信息到设备元数据
            self.storage.store_network_info(
                device_id=device_id,
                fabric_id=fabric_id,
                node_id=node_id,
                network_type="Thread"
            )

            print(f"Device {device_id} successfully commissioned to {fabric_name}")
            return True
        except Exception as e:
            self.storage.store_commissioning_record(
                device_id=device_id,
                fabric_id=fabric_id,
                passcode=passcode,
                discriminator=discriminator,
                success=False,
                error_message=str(e)
            )
            return False

    def setup_acl_for_fabric(self, fabric_id: int, privilege: int,
                            subjects: List[int], targets: List[Dict]) -> int:
        """为Fabric设置ACL"""
        acl_id = self.storage.store_acl_entry(
            fabric_id=fabric_id,
            privilege=privilege,
            auth_mode="CASE",
            subjects=subjects,
            targets=targets
        )
        print(f"ACL entry created: {acl_id} for fabric {fabric_id}")
        return acl_id

    def get_device_fabrics(self, device_id: str) -> List[Dict]:
        """获取设备所属的所有Fabric"""
        device = self.storage.get_device_by_id(device_id)
        if not device:
            return []

        # 查询网络信息获取Fabric列表
        network_info = self.storage.get_network_info_by_device(device_id)
        return [
            {
                "fabric_id": info.get("fabric_id"),
                "node_id": info.get("node_id"),
                "last_seen": info.get("last_seen")
            }
            for info in network_info
        ]

    def remove_fabric(self, device_id: str, fabric_id: int) -> bool:
        """从设备移除Fabric"""
        # 实际实现中需要调用Matter SDK的RemoveFabric命令
        print(f"Removing fabric {fabric_id} from device {device_id}")
        return True

# 使用示例
def demo_multi_admin():
    storage = MatterStorage("postgresql://user:pass@localhost/matter")
    manager = MatterMultiAdminManager(storage)

    # Commission设备到Apple Home
    manager.commission_to_new_fabric(
        device_id="MATTER_LIGHT_001",
        fabric_id=1,
        fabric_name="Apple Home",
        node_id=12345,
        passcode=20202021,
        discriminator=3840
    )

    # 设置ACL权限
    manager.setup_acl_for_fabric(
        fabric_id=1,
        privilege=5,  # Administer
        subjects=[12345],
        targets=[{"cluster": 6, "endpoint": 1}]  # On/Off Cluster
    )
```

---

## 13. 案例13：Matter设备固件OTA升级管理

### 13.1 场景描述

**业务背景**：
Matter设备需要支持OTA（Over-The-Air）固件升级，以修复安全漏洞、添加新功能或提升性能。需要管理固件版本、分发升级包、监控升级进度并处理失败回滚。

**技术挑战**：

- 需要管理固件版本兼容性
- 需要可靠的断点续传
- 需要处理升级失败和回滚
- 需要批量管理多台设备升级

**解决方案**：
使用Matter OTA Provider集群，结合PostgreSQL存储升级状态和进度，实现安全可靠的固件升级管理。

### 13.2 Schema定义

**OTA升级管理Schema**：

```json
{
  "ota_provider": {
    "provider_node_id": 1000,
    "provider_fabric_id": 1,
    "software_version": "2.1.0",
    "software_version_string": "v2.1.0-stable",
    "update_token": "OTA-TOKEN-001",
    "user_consent_needed": false,
    "metadata_for_requestor": {
      "release_notes": "Bug fixes and performance improvements",
      "release_date": "2025-02-01"
    }
  },
  "target_devices": [
    {
      "device_id": "MATTER_LIGHT_001",
      "current_version": "2.0.0",
      "target_version": "2.1.0",
      "update_state": "downloading",
      "progress_percent": 45,
      "download_timestamp": "2025-02-14T10:30:00Z"
    }
  ]
}
```

### 13.3 实现代码

```python
from datetime import datetime
from typing import List, Dict

class MatterOTAManager:
    """Matter OTA升级管理器"""

    OTA_STATUS = ["Idle", "Querying", "Delayed", "Downloading", "Applying", "Rebooting", "Complete", "Error"]

    def __init__(self, storage: MatterStorage):
        self.storage = storage

    def query_image_availability(self, device_id: str, current_version: str) -> Dict:
        """查询可用升级镜像"""
        # 实际实现中调用OTA Provider的QueryImage命令
        available_versions = ["2.1.0", "2.1.1", "2.2.0"]

        if current_version in available_versions:
            idx = available_versions.index(current_version)
            if idx < len(available_versions) - 1:
                return {
                    "available": True,
                    "version": available_versions[idx + 1],
                    "url": f"https://ota.example.com/firmware/v{available_versions[idx + 1]}.bin"
                }

        return {"available": False}

    def initiate_ota_update(self, device_id: str, firmware_version: str,
                           firmware_url: str, checksum: str) -> int:
        """启动OTA升级"""
        update_id = self.storage.store_firmware_update(
            device_id=device_id,
            firmware_version=firmware_version,
            firmware_url=firmware_url,
            firmware_checksum=checksum
        )

        self.storage.update_firmware_status(update_id, "Downloading")

        print(f"OTA update initiated: {update_id} for {device_id} to version {firmware_version}")
        return update_id

    def update_progress(self, update_id: int, progress_percent: int):
        """更新升级进度"""
        # 存储进度到事件日志
        self.storage.store_event(
            device_id="OTA_SYSTEM",
            event_type="ota_progress",
            event_data={
                "update_id": update_id,
                "progress": progress_percent
            }
        )

        if progress_percent >= 100:
            self.storage.update_firmware_status(update_id, "Applying")

    def complete_update(self, update_id: int, success: bool, error_message: str = None):
        """完成升级"""
        if success:
            self.storage.update_firmware_status(update_id, "Completed")
        else:
            self.storage.update_firmware_status(
                update_id, "Failed", error_message
            )

    def get_update_status(self, device_id: str) -> Dict:
        """获取升级状态"""
        updates = self.storage.get_firmware_updates(device_id=device_id)
        if updates:
            latest = updates[0]
            return {
                "device_id": device_id,
                "current_version": latest.get("firmware_version"),
                "status": latest.get("update_status"),
                "progress": self._calculate_progress(latest),
                "started_at": latest.get("started_at"),
                "completed_at": latest.get("completed_at")
            }
        return {"device_id": device_id, "status": "No updates"}

    def _calculate_progress(self, update_record: Dict) -> int:
        """计算升级进度"""
        status = update_record.get("update_status")
        progress_map = {
            "Pending": 0,
            "Downloading": 50,
            "Applying": 80,
            "Completed": 100,
            "Failed": 0
        }
        return progress_map.get(status, 0)

    def batch_update(self, device_ids: List[str], firmware_version: str) -> Dict:
        """批量升级设备"""
        results = {
            "total": len(device_ids),
            "initiated": 0,
            "failed": 0,
            "update_ids": []
        }

        for device_id in device_ids:
            try:
                update_id = self.initiate_ota_update(
                    device_id, firmware_version,
                    f"https://ota.example.com/firmware/v{firmware_version}.bin",
                    checksum="sha256:abc123..."
                )
                results["initiated"] += 1
                results["update_ids"].append(update_id)
            except Exception as e:
                results["failed"] += 1
                print(f"Failed to initiate update for {device_id}: {e}")

        return results

# 使用示例
def demo_ota_update():
    storage = MatterStorage("postgresql://user:pass@localhost/matter")
    ota_manager = MatterOTAManager(storage)

    # 检查升级可用性
    availability = ota_manager.query_image_availability("MATTER_LIGHT_001", "2.0.0")
    print(f"Update available: {availability}")

    if availability.get("available"):
        # 启动升级
        update_id = ota_manager.initiate_ota_update(
            device_id="MATTER_LIGHT_001",
            firmware_version=availability["version"],
            firmware_url=availability["url"],
            checksum="sha256:abc123..."
        )

        # 模拟进度更新
        for progress in [25, 50, 75, 100]:
            ota_manager.update_progress(update_id, progress)

        # 完成升级
        ota_manager.complete_update(update_id, success=True)
```

---

## 14. 案例14：Matter桥接设备管理

### 14.1 场景描述

**业务背景**：
Matter Bridge设备可以将非Matter设备（如Zigbee、Z-Wave设备）桥接到Matter网络。需要管理桥接设备、映射集群、处理设备发现和能力转换。

**技术挑战**：

- 需要动态发现桥接设备
- 需要处理协议差异的映射
- 需要管理桥接设备的生命周期
- 需要处理设备可达性变化

**解决方案**：
使用Matter Bridged Device Basic Information集群，结合PostgreSQL存储桥接关系和设备信息。

### 14.2 Schema定义

**桥接设备管理Schema**：

```json
{
  "bridge_device": {
    "device_id": "MATTER_BRIDGE_001",
    "bridge_type": "Zigbee",
    "firmware_version": "1.2.0"
  },
  "bridged_devices": [
    {
      "bridged_device_id": "ZIGBEE_SENSOR_001",
      "vendor_name": "Aqara",
      "product_name": "Temperature Sensor",
      "unique_id": "00:11:22:33:44:55:66:77",
      "endpoint": 1,
      "clusters": [
        {
          "cluster_id": 1026,
          "cluster_name": "TemperatureMeasurement",
          "attributes": {
            "MeasuredValue": 2560
          }
        }
      ],
      "reachable": true
    }
  ]
}
```

### 14.3 实现代码

```python
class MatterBridgeManager:
    """Matter桥接设备管理器"""

    def __init__(self, storage: MatterStorage):
        self.storage = storage

    def discover_bridged_devices(self, bridge_id: str) -> List[Dict]:
        """发现桥接设备"""
        # 实际实现中调用Bridge的Device Discovery功能
        # 模拟发现的设备
        discovered = [
            {
                "unique_id": "00:11:22:33:44:55:66:77",
                "vendor": "Aqara",
                "product": "Temperature Sensor",
                "endpoint": 1,
                "clusters": [1026]  # TemperatureMeasurement
            }
        ]

        for device in discovered:
            self.storage.store_bridged_device(
                bridge_id=bridge_id,
                bridged_id=device["unique_id"],
                vendor=device["vendor"],
                product=device["product"],
                unique_id=device["unique_id"],
                endpoint=device["endpoint"]
            )

        return discovered

    def map_cluster(self, bridged_device_id: str, native_cluster: int) -> int:
        """映射原生集群到Matter集群"""
        # 集群映射表
        cluster_map = {
            # Zigbee to Matter
            0x0006: 0x0006,   # On/Off
            0x0008: 0x0008,   # Level Control
            0x0300: 0x0300,   # Color Control
            0x0402: 0x0402,   # Temperature Measurement
            # Z-Wave to Matter
            0x25: 0x0006,     # Binary Switch -> On/Off
            0x26: 0x0008,     # Multilevel Switch -> Level Control
        }
        return cluster_map.get(native_cluster, native_cluster)

    def update_bridged_device_reachability(self, bridge_id: str,
                                          bridged_id: str, reachable: bool):
        """更新桥接设备可达性"""
        # 查询并更新可达性状态
        self.storage.store_event(
            device_id=bridge_id,
            event_type="bridged_device_reachability",
            event_data={
                "bridged_device_id": bridged_id,
                "reachable": reachable,
                "timestamp": datetime.now().isoformat()
            }
        )

        print(f"Bridged device {bridged_id} reachability updated: {reachable}")

    def remove_bridged_device(self, bridge_id: str, bridged_id: str):
        """移除桥接设备"""
        # 实际实现中需要调用Bridge的RemoveBridgedDevice命令
        print(f"Removing bridged device {bridged_id} from bridge {bridge_id}")

    def get_bridged_devices(self, bridge_id: str) -> List[Dict]:
        """获取桥接设备列表"""
        # 查询数据库获取桥接设备
        self.storage.cur.execute("""
            SELECT bridged_device_id, vendor_name, product_name,
                   unique_id, bridged_endpoint, reachable
            FROM matter_bridged_devices
            WHERE bridge_device_id = %s
        """, (bridge_id,))
        return [
            {
                "bridged_id": row[0],
                "vendor": row[1],
                "product": row[2],
                "unique_id": row[3],
                "endpoint": row[4],
                "reachable": row[5]
            }
            for row in self.storage.cur.fetchall()
        ]

# 使用示例
def demo_bridge_management():
    storage = MatterStorage("postgresql://user:pass@localhost/matter")
    bridge_manager = MatterBridgeManager(storage)

    # 发现桥接设备
    devices = bridge_manager.discover_bridged_devices("MATTER_BRIDGE_001")
    print(f"Discovered {len(devices)} bridged devices")

    # 获取桥接设备列表
    bridged = bridge_manager.get_bridged_devices("MATTER_BRIDGE_001")
    for device in bridged:
        print(f"  - {device['vendor']} {device['product']} ({device['unique_id']})")
```

---

## 15. 案例15：Matter设备订阅与事件管理

### 15.1 场景描述

**业务背景**：
Matter订阅机制允许控制器实时接收设备状态变化通知。需要管理订阅生命周期、处理订阅超时、优化订阅间隔以平衡实时性和网络负载。

**技术挑战**：

- 需要管理大量订阅
- 需要处理订阅超时和重连
- 需要优化订阅间隔
- 需要处理事件丢失

**解决方案**：
使用Matter Subscribe交互，结合PostgreSQL存储订阅信息和事件历史，实现可靠的订阅管理。

### 15.2 Schema定义

**订阅与事件管理Schema**：

```json
{
  "subscription": {
    "subscription_id": 1,
    "device_id": "MATTER_LIGHT_001",
    "endpoint_id": 1,
    "cluster_id": 6,
    "attribute_id": 0,
    "min_interval": 0,
    "max_interval": 60,
    "is_active": true,
    "last_report": "2025-02-14T10:30:00Z"
  },
  "events": [
    {
      "event_id": 1,
      "event_number": 100,
      "priority": "Info",
      "timestamp": "2025-02-14T10:30:00Z",
      "data": {
        "new_value": true,
        "previous_value": false
      }
    }
  ]
}
```

### 15.3 实现代码

```python
class MatterSubscriptionManager:
    """Matter订阅管理器"""

    def __init__(self, storage: MatterStorage):
        self.storage = storage
        self.active_subscriptions = {}

    def create_subscription(self, device_id: str, endpoint_id: int,
                           cluster_id: int, attribute_id: int = None,
                           min_interval: int = 0, max_interval: int = 60) -> int:
        """创建订阅"""
        subscription_id = self._generate_subscription_id()

        sub_db_id = self.storage.create_subscription(
            subscription_id=subscription_id,
            device_id=device_id,
            endpoint_id=endpoint_id,
            cluster_id=cluster_id,
            attribute_id=attribute_id,
            min_interval=min_interval,
            max_interval=max_interval
        )

        self.active_subscriptions[subscription_id] = {
            "device_id": device_id,
            "endpoint_id": endpoint_id,
            "cluster_id": cluster_id,
            "attribute_id": attribute_id,
            "min_interval": min_interval,
            "max_interval": max_interval
        }

        print(f"Subscription created: ID={subscription_id}, DB_ID={sub_db_id}")
        return subscription_id

    def _generate_subscription_id(self) -> int:
        """生成订阅ID"""
        import random
        return random.randint(1, 0xFFFFFFFF)

    def handle_report_data(self, subscription_id: int, data: Dict):
        """处理订阅报告数据"""
        # 更新最后报告时间
        sub_info = self.active_subscriptions.get(subscription_id)
        if sub_info:
            self.storage.update_subscription_report(
                sub_info["device_id"], subscription_id
            )

        # 存储属性更新
        if sub_info:
            self.storage.store_attribute(
                device_id=sub_info["device_id"],
                endpoint_id=sub_info["endpoint_id"],
                cluster_id=sub_info["cluster_id"],
                attribute_id=sub_info["attribute_id"] or 0,
                attribute_name="subscribed_value",
                attribute_value=data
            )

        print(f"Report received for subscription {subscription_id}: {data}")

    def check_subscription_health(self) -> List[Dict]:
        """检查订阅健康状态"""
        stats = self.storage.get_subscription_statistics()

        # 找出超时订阅
        stale_subs = []
        for sub_id, sub_info in self.active_subscriptions.items():
            # 检查最后报告时间
            pass  # 实际实现中查询数据库

        return [
            {
                "total_subscriptions": stats.get("total", 0),
                "active_subscriptions": stats.get("active", 0),
                "stale_subscriptions": stats.get("stale", 0)
            }
        ]

    def optimize_subscriptions(self, device_id: str = None):
        """优化订阅间隔"""
        # 分析事件频率，调整订阅间隔
        # 高频变化属性：减小max_interval
        # 低频变化属性：增大max_interval
        pass

    def unsubscribe(self, subscription_id: int):
        """取消订阅"""
        sub_info = self.active_subscriptions.get(subscription_id)
        if sub_info:
            self.storage.deactivate_subscription(
                sub_info["device_id"], subscription_id
            )
            del self.active_subscriptions[subscription_id]
            print(f"Subscription {subscription_id} unsubscribed")

# 使用示例
def demo_subscription():
    storage = MatterStorage("postgresql://user:pass@localhost/matter")
    sub_manager = MatterSubscriptionManager(storage)

    # 创建订阅
    sub_id = sub_manager.create_subscription(
        device_id="MATTER_LIGHT_001",
        endpoint_id=1,
        cluster_id=6,  # On/Off
        attribute_id=0,  # OnOff
        min_interval=0,
        max_interval=10
    )

    # 模拟接收报告
    sub_manager.handle_report_data(sub_id, {"value": True})

    # 检查订阅健康
    health = sub_manager.check_subscription_health()
    print(f"Subscription health: {health}")
```

---

## 16. 案例16：Matter网络拓扑分析与优化

### 16.1 场景描述

**业务背景**：
Matter over Thread网络需要分析和优化网络拓扑，确保良好的连接性和低延迟。需要分析路由器分布、链路质量、网络直径等指标。

**技术挑战**：

- 需要收集网络拓扑信息
- 需要分析链路质量和RSSI
- 需要识别网络瓶颈
- 需要优化路由器布局

**解决方案**：
使用Thread Network Data和Matter Network Commissioning集群获取网络信息，结合PostgreSQL存储和分析网络拓扑。

### 16.2 Schema定义

**网络拓扑分析Schema**：

```json
{
  "network_analysis": {
    "fabric_id": 1,
    "timestamp": "2025-02-14T10:30:00Z",
    "topology": {
      "total_nodes": 15,
      "routers": 5,
      "end_devices": 10,
      "network_diameter": 4
    },
    "link_quality": {
      "avg_rssi": -65,
      "avg_lqi": 220,
      "weak_links": [
        {
          "source": "NODE_001",
          "target": "NODE_002",
          "rssi": -82,
          "lqi": 120
        }
      ]
    },
    "recommendations": [
      "考虑在客厅区域增加一个路由器以改善连接"
    ]
  }
}
```

### 16.3 实现代码

```python
class MatterNetworkAnalyzer:
    """Matter网络分析器"""

    def __init__(self, storage: MatterStorage):
        self.storage = storage

    def collect_network_topology(self, fabric_id: int) -> Dict:
        """收集网络拓扑"""
        # 获取网络健康视图
        health_data = self.storage.get_network_health_report()
        fabric_health = next(
            (h for h in health_data if h.get("fabric_id") == fabric_id),
            None
        )

        if not fabric_health:
            return {}

        return {
            "fabric_id": fabric_id,
            "total_nodes": fabric_health.get("device_count", 0),
            "avg_rssi": fabric_health.get("avg_rssi"),
            "avg_lqi": fabric_health.get("avg_lqi"),
            "online_percentage": fabric_health.get("online_percentage")
        }

    def analyze_link_quality(self, fabric_id: int) -> Dict:
        """分析链路质量"""
        # 获取所有设备的网络信息
        devices = self.storage.get_all_devices()

        link_stats = {
            "excellent": 0,  # LQI > 220
            "good": 0,       # LQI 180-220
            "fair": 0,       # LQI 120-180
            "poor": 0        # LQI < 120
        }

        weak_links = []

        for device in devices:
            network_info = self.storage.get_network_info_by_device(device["device_id"])
            for info in network_info:
                lqi = info.get("lqi", 0)
                rssi = info.get("rssi", -100)

                if lqi > 220:
                    link_stats["excellent"] += 1
                elif lqi > 180:
                    link_stats["good"] += 1
                elif lqi > 120:
                    link_stats["fair"] += 1
                else:
                    link_stats["poor"] += 1
                    weak_links.append({
                        "device_id": device["device_id"],
                        "rssi": rssi,
                        "lqi": lqi
                    })

        return {
            "link_distribution": link_stats,
            "weak_links": weak_links[:10]  # 返回前10个弱链接
        }

    def generate_optimization_recommendations(self, fabric_id: int) -> List[str]:
        """生成优化建议"""
        recommendations = []

        topology = self.collect_network_topology(fabric_id)
        link_analysis = self.analyze_link_quality(fabric_id)

        # 检查在线率
        if topology.get("online_percentage", 100) < 95:
            recommendations.append(
                f"网络在线率较低({topology['online_percentage']}%)，建议检查离线设备"
            )

        # 检查链路质量
        poor_count = link_analysis["link_distribution"].get("poor", 0)
        total_links = sum(link_analysis["link_distribution"].values())

        if total_links > 0 and poor_count / total_links > 0.2:
            recommendations.append(
                f"弱链接比例较高({poor_count}/{total_links})，建议优化设备位置或增加路由器"
            )

        # 检查RSSI
        avg_rssi = topology.get("avg_rssi", -50)
        if avg_rssi < -75:
            recommendations.append(
                f"平均信号强度较弱({avg_rssi}dBm)，建议增加Thread路由器"
            )

        if not recommendations:
            recommendations.append("网络状况良好，无需优化")

        return recommendations

    def store_network_diagnosis(self, fabric_id: int, diagnosis_data: Dict):
        """存储网络诊断结果"""
        self.storage.store_network_diagnostic(
            device_id=f"FABRIC_{fabric_id}",
            diagnostic_type="network_topology",
            result_data=diagnosis_data
        )

    def generate_network_report(self, fabric_id: int) -> Dict:
        """生成网络报告"""
        topology = self.collect_network_topology(fabric_id)
        link_analysis = self.analyze_link_quality(fabric_id)
        recommendations = self.generate_optimization_recommendations(fabric_id)

        report = {
            "fabric_id": fabric_id,
            "timestamp": datetime.now().isoformat(),
            "topology": topology,
            "link_analysis": link_analysis,
            "recommendations": recommendations
        }

        # 存储报告
        self.store_network_diagnosis(fabric_id, report)

        return report

# 使用示例
def demo_network_analysis():
    storage = MatterStorage("postgresql://user:pass@localhost/matter")
    analyzer = MatterNetworkAnalyzer(storage)

    # 收集网络拓扑
    topology = analyzer.collect_network_topology(fabric_id=1)
    print(f"Network topology: {topology}")

    # 分析链路质量
    link_quality = analyzer.analyze_link_quality(fabric_id=1)
    print(f"Link quality: {link_quality}")

    # 生成优化建议
    recommendations = analyzer.generate_optimization_recommendations(fabric_id=1)
    print(f"Recommendations: {recommendations}")

    # 生成完整报告
    report = analyzer.generate_network_report(fabric_id=1)
    print(f"Network report generated: {report['timestamp']}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-14（新增5个Matter高级案例）
