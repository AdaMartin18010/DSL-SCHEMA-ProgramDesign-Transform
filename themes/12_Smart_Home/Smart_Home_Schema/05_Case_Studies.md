# 智慧家居Schema实践案例

## 📑 目录

- [智慧家居Schema实践案例](#智慧家居schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：智能照明控制](#2-案例1智能照明控制)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：智能门锁管理](#3-案例2智能门锁管理)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：智能空调控制](#4-案例3智能空调控制)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：回家场景联动](#5-案例4回家场景联动)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 Schema定义](#52-schema定义)
    - [5.3 实现代码](#53-实现代码)
  - [6. 案例5：睡眠场景联动](#6-案例5睡眠场景联动)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 Schema定义](#62-schema定义)
    - [6.3 实现代码](#63-实现代码)
  - [7. 案例6：能耗优化场景](#7-案例6能耗优化场景)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：故障诊断场景](#8-案例7故障诊断场景)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：智慧家居数据存储系统](#9-案例8智慧家居数据存储系统)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 实现代码](#92-实现代码)

---

## 1. 案例概述

本文档提供智慧家居Schema在实际应用中的实践案例。

---

## 2. 案例1：智能照明控制

### 2.1 场景描述

**应用场景**：
使用Matter协议控制智能灯光，实现亮度调节和色温控制。

### 2.2 Schema定义

**智能照明Schema**：

```json
{
  "device_id": "LIGHT001",
  "device_type": "ExtendedColorLight",
  "device_name": "客厅主灯",
  "state": {
    "power": "On",
    "brightness": 80,
    "color_temperature": 4000,
    "color_rgb": {
      "red": 255,
      "green": 200,
      "blue": 150
    },
    "scene_mode": "Reading"
  },
  "location": {
    "room": "客厅",
    "zone": "主区域"
  }
}
```

---

## 3. 案例2：智能门锁管理

### 3.1 场景描述

**应用场景**：
使用Matter协议管理智能门锁，实现远程开锁和状态监控。

### 3.2 Schema定义

**智能门锁Schema**：

```json
{
  "device_id": "LOCK001",
  "device_type": "DoorLock",
  "device_name": "前门智能锁",
  "state": {
    "power": "On",
    "battery_level": 85,
    "signal_strength": 90
  },
  "door_lock_state": {
    "lock_state": "Locked",
    "auto_lock_enabled": true,
    "auto_lock_delay": 30
  },
  "event_log": [
    {
      "event_type": "Lock",
      "event_time": "2025-01-21T10:30:00Z",
      "event_details": "用户通过手机APP锁定"
    }
  ]
}
```

---

## 4. 案例3：智能空调控制

### 4.1 场景描述

**应用场景**：
使用Matter协议控制智能空调，实现温度调节和模式切换。

### 4.2 Schema定义

**智能空调Schema**：

```json
{
  "device_id": "AC001",
  "device_type": "AirConditioner",
  "device_name": "客厅空调",
  "state": {
    "power": "On",
    "operation_mode": "Cool",
    "target_temperature": 26.0,
    "current_temperature": 28.5,
    "fan_speed": "Auto"
  },
  "energy_consumption": {
    "current_power": 1500.0,
    "daily_consumption": 12.5,
    "monthly_consumption": 375.0,
    "energy_rating": "A"
  }
}
```

---

## 5. 案例4：回家场景联动

### 5.1 场景描述

**业务背景**：
用户希望当检测到有人回家时，自动执行一系列设备控制操作，
包括打开灯光、调节空调温度、播放欢迎音乐等。

**技术挑战**：

- 需要实时检测运动传感器状态变化
- 需要协调多个设备的控制命令
- 需要处理设备控制失败的情况
- 需要记录场景执行历史

**解决方案**：
使用场景联动系统，定义回家场景的触发条件和执行动作，
当运动传感器检测到运动时自动触发场景执行。

### 5.2 Schema定义

**回家场景Schema**：

```json
{
  "scene_id": "scene_home_arrival",
  "scene_name": "回家场景",
  "scene_description": "检测到回家时自动执行",
  "enabled": true,
  "conditions": [
    {
      "device_id": "SENSOR001",
      "attribute": "motion_detected",
      "operator": "==",
      "value": true
    },
    {
      "device_id": "SENSOR001",
      "attribute": "location",
      "operator": "==",
      "value": "entrance"
    }
  ],
  "actions": [
    {
      "device_id": "LIGHT001",
      "command": "turn_on",
      "parameters": {
        "brightness": 80,
        "color_temperature": 4000
      }
    },
    {
      "device_id": "LIGHT002",
      "command": "turn_on",
      "parameters": {
        "brightness": 60
      }
    },
    {
      "device_id": "AC001",
      "command": "set_temperature",
      "parameters": {
        "temperature": 26,
        "mode": "Cool"
      }
    },
    {
      "device_id": "MUSIC001",
      "command": "play",
      "parameters": {
        "playlist": "welcome",
        "volume": 30
      }
    }
  ]
}
```

### 5.3 实现代码

**场景管理器实现**：

```python
from matter_to_zigbee_converter import MatterToZigbeeConverter
from smart_home_storage import SmartHomeStorage
from scene_manager import SceneManager, SmartHomeScene
import time

# 初始化存储和场景管理器
storage = SmartHomeStorage("postgresql://user:pass@localhost/smarthome")
scene_manager = SceneManager(storage)

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
        },
        {
            "device_id": "SENSOR001",
            "attribute": "location",
            "operator": "==",
            "value": "entrance"
        }
    ],
    actions=[
        {
            "device_id": "LIGHT001",
            "command": "turn_on",
            "parameters": {"brightness": 80, "color_temperature": 4000}
        },
        {
            "device_id": "LIGHT002",
            "command": "turn_on",
            "parameters": {"brightness": 60}
        },
        {
            "device_id": "AC001",
            "command": "set_temperature",
            "parameters": {"temperature": 26, "mode": "Cool"}
        },
        {
            "device_id": "MUSIC001",
            "command": "play",
            "parameters": {"playlist": "welcome", "volume": 30}
        }
    ]
)

# 模拟传感器状态更新
def simulate_motion_detection():
    """模拟运动检测"""
    # 更新传感器状态
    scene_manager.update_device_state("SENSOR001", {
        "motion_detected": True,
        "location": "entrance",
        "timestamp": datetime.now().isoformat()
    })

    # 场景管理器会自动检查并触发场景

# 测试场景执行
if __name__ == "__main__":
    simulate_motion_detection()
    time.sleep(1)

    # 查询场景执行历史
    executions = storage.get_scene_execution_statistics("scene_home_arrival", days=1)
    print(f"场景执行次数: {executions}")
```

---

## 6. 案例5：睡眠场景联动

### 6.1 场景描述

**业务背景**：
用户希望晚上10点后，当检测到卧室灯光关闭时，自动执行睡眠场景，
包括关闭所有灯光、调节空调温度、开启安防系统、关闭窗帘等。

**技术挑战**：

- 需要基于时间条件触发
- 需要检测多个设备状态
- 需要延迟执行某些动作
- 需要处理场景冲突

**解决方案**：
使用场景联动系统，定义睡眠场景的触发条件（时间+灯光状态），
当条件满足时自动执行睡眠场景。

### 6.2 Schema定义

**睡眠场景Schema**：

```json
{
  "scene_id": "scene_sleep",
  "scene_name": "睡眠场景",
  "scene_description": "晚上10点后灯光关闭时自动执行",
  "enabled": true,
  "conditions": [
    {
      "device_id": "TIME",
      "attribute": "hour",
      "operator": ">=",
      "value": 22
    },
    {
      "device_id": "LIGHT003",
      "attribute": "power",
      "operator": "==",
      "value": "Off"
    }
  ],
  "actions": [
    {
      "device_id": "LIGHT001",
      "command": "turn_off",
      "parameters": {}
    },
    {
      "device_id": "LIGHT002",
      "command": "turn_off",
      "parameters": {}
    },
    {
      "device_id": "AC001",
      "command": "set_temperature",
      "parameters": {
        "temperature": 24,
        "mode": "Auto"
      }
    },
    {
      "device_id": "CURTAIN001",
      "command": "close",
      "parameters": {}
    },
    {
      "device_id": "SECURITY001",
      "command": "arm",
      "parameters": {
        "mode": "Night"
      }
    }
  ]
}
```

### 6.3 实现代码

**睡眠场景实现**：

```python
from datetime import datetime, time

# 创建睡眠场景
scene_manager.create_scene(
    scene_id="scene_sleep",
    scene_name="睡眠场景",
    conditions=[
        {
            "device_id": "TIME",
            "attribute": "hour",
            "operator": ">=",
            "value": 22
        },
        {
            "device_id": "LIGHT003",
            "attribute": "power",
            "operator": "==",
            "value": "Off"
        }
    ],
    actions=[
        {"device_id": "LIGHT001", "command": "turn_off", "parameters": {}},
        {"device_id": "LIGHT002", "command": "turn_off", "parameters": {}},
        {
            "device_id": "AC001",
            "command": "set_temperature",
            "parameters": {"temperature": 24, "mode": "Auto"}
        },
        {"device_id": "CURTAIN001", "command": "close", "parameters": {}},
        {
            "device_id": "SECURITY001",
            "command": "arm",
            "parameters": {"mode": "Night"}
        }
    ]
)

# 时间条件检查函数
def check_time_condition(hour_threshold: int) -> bool:
    """检查时间条件"""
    current_hour = datetime.now().hour
    return current_hour >= hour_threshold

# 模拟灯光关闭事件
def simulate_bedroom_light_off():
    """模拟卧室灯光关闭"""
    current_hour = datetime.now().hour

    # 更新灯光状态
    scene_manager.update_device_state("LIGHT003", {
        "power": "Off",
        "timestamp": datetime.now().isoformat()
    })

    # 检查时间条件
    if check_time_condition(22):
        # 手动触发睡眠场景
        scene_manager.execute_scene("scene_sleep")
```

---

## 7. 案例6：能耗优化场景

### 7.1 场景描述

**业务背景**：
用户希望根据实时电价和能耗数据，自动优化设备运行策略，
在电价高峰时段降低非必要设备的能耗，在电价低谷时段增加设备运行。

**技术挑战**：

- 需要实时获取电价信息
- 需要计算设备能耗
- 需要优化设备运行策略
- 需要平衡舒适度和能耗

**解决方案**：
使用自动化规则系统，定义基于电价的能耗优化规则，
自动调整设备运行参数以降低能耗成本。

### 7.2 Schema定义

**能耗优化规则Schema**：

```json
{
  "rule_id": "rule_energy_optimization",
  "rule_name": "能耗优化规则",
  "rule_description": "根据电价自动优化设备能耗",
  "enabled": true,
  "trigger_device_id": "PRICE001",
  "trigger_attribute": "price_level",
  "trigger_operator": ">",
  "trigger_value": 0.8,
  "actions": [
    {
      "device_id": "AC001",
      "command": "set_temperature",
      "parameters": {
        "temperature": 28,
        "mode": "Eco"
      }
    },
    {
      "device_id": "LIGHT001",
      "command": "set_brightness",
      "parameters": {
        "brightness": 50
      }
    },
    {
      "device_id": "WASHER001",
      "command": "delay_start",
      "parameters": {
        "delay_hours": 2
      }
    }
  ]
}
```

### 7.3 实现代码

**能耗优化实现**：

```python
# 创建能耗优化规则
storage.store_automation_rule({
    "rule_id": "rule_energy_optimization",
    "rule_name": "能耗优化规则",
    "rule_description": "根据电价自动优化设备能耗",
    "trigger_device_id": "PRICE001",
    "trigger_attribute": "price_level",
    "trigger_operator": ">",
    "trigger_value": 0.8,
    "actions": [
        {
            "device_id": "AC001",
            "command": "set_temperature",
            "parameters": {"temperature": 28, "mode": "Eco"}
        },
        {
            "device_id": "LIGHT001",
            "command": "set_brightness",
            "parameters": {"brightness": 50}
        },
        {
            "device_id": "WASHER001",
            "command": "delay_start",
            "parameters": {"delay_hours": 2}
        }
    ]
})

# 模拟电价更新
def simulate_price_update(price_level: float):
    """模拟电价更新"""
    scene_manager.update_device_state("PRICE001", {
        "price_level": price_level,
        "timestamp": datetime.now().isoformat()
    })

    # 检查自动化规则
    # 规则管理器会自动检查并执行规则

# 查询能耗统计
def get_energy_savings():
    """查询能耗节省统计"""
    # 查询优化前后的能耗对比
    before_optimization = storage.get_energy_consumption_by_room(days=7)
    # 模拟优化后的数据
    after_optimization = storage.get_energy_consumption_by_room(days=7)

    savings = {}
    for room_data in before_optimization:
        room = room_data[0]
        before_consumption = room_data[1]
        # 计算节省（假设优化后降低20%）
        savings[room] = before_consumption * 0.2

    return savings
```

---

## 8. 案例7：故障诊断场景

### 8.1 场景描述

**业务背景**：
系统需要自动检测设备故障，当检测到设备异常时，
自动执行故障诊断流程，记录故障信息，并尝试自动恢复。

**技术挑战**：

- 需要实时监控设备状态
- 需要识别异常模式
- 需要故障分类和诊断
- 需要自动恢复策略

**解决方案**：
使用自动化规则系统，定义故障检测规则，
当检测到设备异常时自动触发故障诊断和恢复流程。

### 8.2 Schema定义

**故障检测规则Schema**：

```json
{
  "rule_id": "rule_device_fault_detection",
  "rule_name": "设备故障检测规则",
  "rule_description": "检测设备故障并自动诊断",
  "enabled": true,
  "trigger_device_id": "DEVICE_MONITOR",
  "trigger_attribute": "fault_detected",
  "trigger_operator": "==",
  "trigger_value": true,
  "actions": [
    {
      "device_id": "LOGGER001",
      "command": "log_fault",
      "parameters": {
        "severity": "High",
        "category": "DeviceFault"
      }
    },
    {
      "device_id": "DIAGNOSTIC001",
      "command": "run_diagnosis",
      "parameters": {
        "diagnosis_type": "Auto"
      }
    },
    {
      "device_id": "NOTIFICATION001",
      "command": "send_alert",
      "parameters": {
        "alert_type": "DeviceFault",
        "recipients": ["admin@example.com"]
      }
    }
  ]
}
```

### 8.3 实现代码

**故障诊断实现**：

```python
# 创建故障检测规则
storage.store_automation_rule({
    "rule_id": "rule_device_fault_detection",
    "rule_name": "设备故障检测规则",
    "trigger_device_id": "DEVICE_MONITOR",
    "trigger_attribute": "fault_detected",
    "trigger_operator": "==",
    "trigger_value": True,
    "actions": [
        {
            "device_id": "LOGGER001",
            "command": "log_fault",
            "parameters": {"severity": "High", "category": "DeviceFault"}
        },
        {
            "device_id": "DIAGNOSTIC001",
            "command": "run_diagnosis",
            "parameters": {"diagnosis_type": "Auto"}
        },
        {
            "device_id": "NOTIFICATION001",
            "command": "send_alert",
            "parameters": {
                "alert_type": "DeviceFault",
                "recipients": ["admin@example.com"]
            }
        }
    ]
})

# 设备故障检测函数
def detect_device_fault(device_id: str, device_state: Dict) -> bool:
    """检测设备故障"""
    # 检查设备状态异常
    if device_state.get("status") == "Error":
        return True

    # 检查设备响应超时
    last_update = device_state.get("last_update")
    if last_update:
        time_diff = (datetime.now() - datetime.fromisoformat(last_update)).total_seconds()
        if time_diff > 300:  # 5分钟无响应
            return True

    # 检查设备参数异常
    if device_state.get("temperature", 0) > 80:  # 温度过高
        return True

    return False

# 模拟故障检测
def monitor_devices():
    """监控设备状态"""
    devices = storage.get_all_devices()

    for device in devices:
        device_id = device["device_id"]
        device_state = storage.get_device_state(device_id)

        if detect_device_fault(device_id, device_state):
            # 触发故障检测规则
            scene_manager.update_device_state("DEVICE_MONITOR", {
                "fault_detected": True,
                "fault_device_id": device_id,
                "fault_type": "DeviceError",
                "timestamp": datetime.now().isoformat()
            })
```

---

## 9. 案例8：智慧家居数据存储系统

### 9.1 场景描述

**应用场景**：
使用PostgreSQL存储智慧家居设备数据，支持设备状态查询、
能耗分析、场景执行统计等功能。

### 9.2 实现代码

详见 `04_Transformation.md` 第7章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
