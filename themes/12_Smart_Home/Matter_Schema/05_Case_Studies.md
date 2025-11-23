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

**创建时间**：2025-01-21
**最后更新**：2025-01-21
