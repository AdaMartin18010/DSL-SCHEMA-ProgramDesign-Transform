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

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
