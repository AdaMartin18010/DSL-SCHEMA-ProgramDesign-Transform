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
  - [9. 案例9：离家场景（安防、能耗管理）](#9-案例9离家场景安防能耗管理)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 Schema定义](#92-schema定义)
    - [9.3 实现代码](#93-实现代码)
  - [10. 案例10：智慧家居数据存储系统](#10-案例10智慧家居数据存储系统)
    - [9.1 场景描述](#91-场景描述-1)
    - [9.2 实现代码](#92-实现代码)
  - [11. 案例11：智能安防系统](#11-案例11智能安防系统)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)
  - [12. 案例12：智能健康监测系统](#12-案例12智能健康监测系统)
    - [12.1 场景描述](#121-场景描述)
    - [12.2 Schema定义](#122-schema定义)
    - [12.3 实现代码](#123-实现代码)

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

## 9. 案例9：离家场景（安防、能耗管理）

### 9.1 场景描述

**业务背景**：
用户希望当检测到用户离开家时，自动执行离家场景，包括：

- 关闭所有灯光和电器设备
- 启动安防系统（门窗传感器、摄像头）
- 调节空调到节能模式
- 关闭窗帘
- 记录离开时间用于能耗分析

**技术挑战**：

- 需要准确检测用户离开（多种传感器组合判断）
- 需要确保所有设备正确关闭
- 需要启动安防系统并验证状态
- 需要记录能耗数据用于分析

**解决方案**：
使用场景联动系统，定义离家场景的触发条件（门锁状态+运动传感器+时间），
当条件满足时自动执行离家场景，并记录执行结果用于后续分析。

### 9.2 Schema定义

**离家场景Schema**：

```json
{
  "scene_id": "scene_away",
  "scene_name": "离家场景",
  "scene_description": "用户离开家时自动执行，关闭设备并启动安防",
  "enabled": true,
  "condition_logic": "AND",
  "conditions": [
    {
      "device_id": "LOCK001",
      "attribute": "lock_state",
      "operator": "==",
      "value": "Locked"
    },
    {
      "device_id": "MOTION001",
      "attribute": "motion_detected",
      "operator": "==",
      "value": false
    },
    {
      "device_id": "MOTION002",
      "attribute": "motion_detected",
      "operator": "==",
      "value": false
    }
  ],
  "time_conditions": [
    {
      "time_type": "time_of_day",
      "value": "08:00:00"
    }
  ],
  "actions": [
    {
      "device_id": "LIGHT001",
      "command": "turn_off",
      "parameters": {},
      "delay": 0.0
    },
    {
      "device_id": "LIGHT002",
      "command": "turn_off",
      "parameters": {},
      "delay": 0.0
    },
    {
      "device_id": "AC001",
      "command": "set_temperature",
      "parameters": {
        "temperature": 28,
        "mode": "Eco"
      },
      "delay": 0.0
    },
    {
      "device_id": "CURTAIN001",
      "command": "close",
      "parameters": {},
      "delay": 0.0
    },
    {
      "device_id": "CURTAIN002",
      "command": "close",
      "parameters": {},
      "delay": 0.0
    },
    {
      "device_id": "SECURITY001",
      "command": "arm",
      "parameters": {
        "mode": "Away",
        "zones": ["all"]
      },
      "delay": 5.0
    },
    {
      "device_id": "CAMERA001",
      "command": "start_recording",
      "parameters": {
        "mode": "motion_detection"
      },
      "delay": 5.0
    }
  ]
}
```

### 9.3 实现代码

**离家场景完整实现**：

```python
import logging
from datetime import datetime, time
from smart_home_storage import SmartHomeStorage
from scene_manager import SceneManager, DeviceController
from matter_sdk_wrapper import MatterSDKWrapper
from zigbee2mqtt_wrapper import Zigbee2MQTTWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化组件
storage = SmartHomeStorage("postgresql://user:pass@localhost/smarthome")
matter_sdk = MatterSDKWrapper(node_id=0x12344321)
zigbee_api = Zigbee2MQTTWrapper(base_url="http://localhost:8080")
device_controller = DeviceController(matter_sdk=matter_sdk, zigbee_api=zigbee_api)
scene_manager = SceneManager(storage, device_controller)

# 创建离家场景
def create_away_scene():
    """创建离家场景"""
    scene_manager.create_scene(
        scene_id="scene_away",
        scene_name="离家场景",
        conditions=[
            {
                "device_id": "LOCK001",
                "attribute": "lock_state",
                "operator": "==",
                "value": "Locked"
            },
            {
                "device_id": "MOTION001",
                "attribute": "motion_detected",
                "operator": "==",
                "value": False
            },
            {
                "device_id": "MOTION002",
                "attribute": "motion_detected",
                "operator": "==",
                "value": False
            }
        ],
        actions=[
            {
                "device_id": "LIGHT001",
                "command": "turn_off",
                "parameters": {},
                "delay": 0.0
            },
            {
                "device_id": "LIGHT002",
                "command": "turn_off",
                "parameters": {},
                "delay": 0.0
            },
            {
                "device_id": "AC001",
                "command": "set_temperature",
                "parameters": {"temperature": 28, "mode": "Eco"},
                "delay": 0.0
            },
            {
                "device_id": "CURTAIN001",
                "command": "close",
                "parameters": {},
                "delay": 0.0
            },
            {
                "device_id": "SECURITY001",
                "command": "arm",
                "parameters": {"mode": "Away", "zones": ["all"]},
                "delay": 5.0
            },
            {
                "device_id": "CAMERA001",
                "command": "start_recording",
                "parameters": {"mode": "motion_detection"},
                "delay": 5.0
            }
        ],
        time_conditions=[
            {
                "time_type": "time_of_day",
                "value": time(8, 0, 0)  # 8:00 AM之后
            }
        ],
        condition_logic="AND"
    )
    logger.info("离家场景创建成功")

# 模拟用户离开
def simulate_user_leaving():
    """模拟用户离开场景"""
    # 1. 用户锁门
    scene_manager.update_device_state("LOCK001", {
        "lock_state": "Locked",
        "timestamp": datetime.now().isoformat()
    })

    # 2. 等待5秒，确保用户离开
    import time
    time.sleep(5)

    # 3. 更新运动传感器状态（无运动）
    scene_manager.update_device_state("MOTION001", {
        "motion_detected": False,
        "timestamp": datetime.now().isoformat()
    })

    scene_manager.update_device_state("MOTION002", {
        "motion_detected": False,
        "timestamp": datetime.now().isoformat()
    })

    logger.info("用户离开检测完成，场景应自动触发")

# 验证场景执行结果
def verify_away_scene_execution():
    """验证离家场景执行结果"""
    # 查询场景执行历史
    executions = storage.get_scene_execution_statistics("scene_away", days=1)
    logger.info(f"离家场景执行统计: {executions}")

    # 验证设备状态
    devices_to_check = ["LIGHT001", "LIGHT002", "AC001", "SECURITY001"]
    for device_id in devices_to_check:
        state = storage.get_latest_device_state(device_id)
        if state:
            logger.info(f"设备 {device_id} 状态: {state}")
        else:
            logger.warning(f"设备 {device_id} 状态未找到")

    # 查询能耗数据
    energy_stats = storage.get_device_energy_statistics("AC001", datetime.now())
    logger.info(f"空调能耗统计: {energy_stats}")

# 测试用例
def test_away_scene():
    """测试离家场景"""
    # 测试1: 正常离开场景
    logger.info("测试1: 正常离开场景")
    create_away_scene()
    simulate_user_leaving()
    verify_away_scene_execution()

    # 测试2: 部分条件不满足（运动传感器仍检测到运动）
    logger.info("测试2: 部分条件不满足")
    scene_manager.update_device_state("MOTION001", {
        "motion_detected": True,  # 仍有运动
        "timestamp": datetime.now().isoformat()
    })
    # 场景不应触发

    # 测试3: 手动执行场景
    logger.info("测试3: 手动执行场景")
    result = scene_manager.execute_scene("scene_away", manual=True)
    logger.info(f"手动执行结果: {result}")

if __name__ == "__main__":
    test_away_scene()
```

**运行结果示例**：

```text
INFO:__main__:离家场景创建成功
INFO:__main__:用户离开检测完成，场景应自动触发
INFO:__main__:Scenes triggered: ['scene_away']
INFO:__main__:Action executed: LIGHT001 -> turn_off
INFO:__main__:Action executed: LIGHT002 -> turn_off
INFO:__main__:Action executed: AC001 -> set_temperature
INFO:__main__:Action executed: CURTAIN001 -> close
INFO:__main__:Action executed: SECURITY001 -> arm
INFO:__main__:Action executed: CAMERA001 -> start_recording
INFO:__main__:离家场景执行统计: [('auto', 1, 1, 0, None)]
INFO:__main__:设备 LIGHT001 状态: {'state': {'power': 'Off'}, 'recorded_at': '2025-01-21 10:30:00'}
INFO:__main__:设备 AC001 状态: {'state': {'temperature': 28, 'mode': 'Eco'}, 'recorded_at': '2025-01-21 10:30:00'}
```

---

## 10. 案例10：智慧家居数据存储系统

### 9.1 场景描述

**应用场景**：
使用PostgreSQL存储智慧家居设备数据，支持设备状态查询、
能耗分析、场景执行统计等功能。

### 9.2 实现代码

详见 `04_Transformation.md` 第7章。

---

## 11. 案例11：智能安防系统

### 11.1 场景描述

**业务背景**：
智能安防系统集成门锁、摄像头、传感器等设备，
实现入侵检测、异常行为识别、自动报警等功能。

**技术挑战**：
- 需要多设备联动
- 需要实时监控
- 需要异常检测算法
- 需要报警机制

**解决方案**：
使用Smart_Home_Schema整合安防设备，
使用AI算法进行异常检测，
使用SmartHomeStorage存储安防数据。

### 11.2 Schema定义

**智能安防Schema**：

```dsl
schema SmartSecurity {
  security_session_id: String @value("SEC-20250121-001") @required
  timestamp: DateTime @value("2025-01-21T22:00:00") @required

  security_devices: {
    door_lock: {
      device_id: String @value("LOCK-001")
      status: Enum { Locked } @value(Locked)
      last_unlock_time: DateTime @value("2025-01-21T18:00:00")
    }
    camera: {
      device_id: String @value("CAM-001")
      status: Enum { Active } @value(Active)
      motion_detected: Boolean @value(false)
    }
    motion_sensor: {
      device_id: String @value("MOTION-001")
      status: Enum { Active } @value(Active)
      motion_detected: Boolean @value(false)
    }
    window_sensor: {
      device_id: String @value("WINDOW-001")
      status: Enum { Closed } @value(Closed)
    }
  } @required

  security_status: {
    overall_status: Enum { Secure } @value(Secure)
    alert_level: Enum { Normal } @value(Normal)
    active_alerts: Integer @value(0)
  } @required

  security_rules: [
    {
      rule_id: String @value("RULE-001")
      rule_name: String @value("夜间入侵检测")
      trigger_condition: String @value("motion_detected AND time > 22:00")
      action: String @value("send_alert AND turn_on_lights")
      enabled: Boolean @value(true)
    }
  ] @required
} @standard("Matter")
```

### 11.3 实现代码

```python
from smart_home_storage import SmartHomeStorage
from datetime import datetime, time

def smart_security_system():
    """智能安防系统示例"""
    storage = SmartHomeStorage("postgresql://user:password@localhost/smart_home")

    # 安防设备状态
    security_devices = {
        "door_lock": {
            "device_id": "LOCK-001",
            "status": "Locked",
            "last_unlock_time": datetime(2025, 1, 21, 18, 0, 0)
        },
        "camera": {
            "device_id": "CAM-001",
            "status": "Active",
            "motion_detected": False
        },
        "motion_sensor": {
            "device_id": "MOTION-001",
            "status": "Active",
            "motion_detected": False
        },
        "window_sensor": {
            "device_id": "WINDOW-001",
            "status": "Closed"
        }
    }

    # 安防规则
    security_rules = [
        {
            "rule_id": "RULE-001",
            "rule_name": "夜间入侵检测",
            "trigger_condition": "motion_detected AND time > 22:00",
            "action": "send_alert AND turn_on_lights",
            "enabled": True
        }
    ]

    # 检查安防状态
    def check_security_status(devices, current_time):
        """检查安防状态"""
        overall_status = "Secure"
        alert_level = "Normal"
        active_alerts = 0

        # 检查门锁状态
        if devices["door_lock"]["status"] != "Locked":
            overall_status = "Warning"
            alert_level = "Medium"
            active_alerts += 1

        # 检查运动检测
        if devices["motion_sensor"]["motion_detected"]:
            if current_time.hour >= 22 or current_time.hour < 6:
                overall_status = "Alert"
                alert_level = "High"
                active_alerts += 1

        # 检查窗户传感器
        if devices["window_sensor"]["status"] != "Closed":
            overall_status = "Warning"
            alert_level = "Medium"
            active_alerts += 1

        return {
            "overall_status": overall_status,
            "alert_level": alert_level,
            "active_alerts": active_alerts
        }

    # 执行安防检查
    current_time = datetime.now()
    security_status = check_security_status(security_devices, current_time)

    # 存储安防数据
    security_data = {
        "security_session_id": "SEC-20250121-001",
        "timestamp": current_time,
        "door_lock_status": security_devices["door_lock"]["status"],
        "camera_status": security_devices["camera"]["status"],
        "motion_sensor_status": security_devices["motion_sensor"]["status"],
        "window_sensor_status": security_devices["window_sensor"]["status"],
        "overall_status": security_status["overall_status"],
        "alert_level": security_status["alert_level"],
        "active_alerts": security_status["active_alerts"]
    }

    # 存储到数据库
    security_id = storage.store_device_data(security_data)
    print(f"Security data stored: {security_id}")

    print(f"\nSmart Security Status:")
    print(f"  Overall status: {security_status['overall_status']}")
    print(f"  Alert level: {security_status['alert_level']}")
    print(f"  Active alerts: {security_status['active_alerts']}")
    print(f"  Door lock: {security_devices['door_lock']['status']}")
    print(f"  Motion sensor: {'Motion detected' if security_devices['motion_sensor']['motion_detected'] else 'No motion'}")

    return security_data

if __name__ == "__main__":
    smart_security_system()
```

---

## 12. 案例12：智能健康监测系统

### 12.1 场景描述

**业务背景**：
智能健康监测系统集成健康传感器、智能床垫、智能体重秤等设备，
监测用户健康指标，提供健康建议和预警。

**技术挑战**：
- 需要多传感器数据融合
- 需要健康数据分析
- 需要异常检测
- 需要健康报告生成

**解决方案**：
使用Smart_Home_Schema整合健康设备，
使用AI算法进行健康分析，
使用SmartHomeStorage存储健康数据。

### 12.2 Schema定义

**智能健康监测Schema**：

```dsl
schema SmartHealthMonitoring {
  health_session_id: String @value("HEALTH-20250121-001") @required
  user_id: String @value("USER-001") @required
  timestamp: DateTime @value("2025-01-21T08:00:00") @required

  health_metrics: {
    weight: Decimal @value(70.5) @unit("kg")
    bmi: Decimal @value(22.5)
    heart_rate: Integer @value(72) @unit("bpm")
    blood_pressure: {
      systolic: Integer @value(120) @unit("mmHg")
      diastolic: Integer @value(80) @unit("mmHg")
    }
    sleep_quality: {
      sleep_duration: Decimal @value(7.5) @unit("hours")
      deep_sleep_ratio: Decimal @value(0.25)
      sleep_score: Decimal @value(0.85) @range(0.0, 1.0)
    }
    activity_level: {
      steps: Integer @value(8500)
      calories_burned: Integer @value(2200)
      active_minutes: Integer @value(45)
    }
  } @required

  health_analysis: {
    overall_health_score: Decimal @value(0.82) @range(0.0, 1.0)
    health_status: Enum { Good } @value(Good)
    risk_factors: [
      {
        factor: String @value("Sedentary lifestyle")
        severity: Enum { Low } @value(Low)
        recommendation: String @value("增加日常活动量")
      }
    ]
    recommendations: [
      {
        recommendation: String @value("保持当前运动量")
        priority: Enum { Medium } @value(Medium)
      }
    ]
  } @required
} @standard("Matter")
```

### 12.3 实现代码

```python
from smart_home_storage import SmartHomeStorage
from datetime import datetime

def smart_health_monitoring():
    """智能健康监测系统示例"""
    storage = SmartHomeStorage("postgresql://user:password@localhost/smart_home")

    # 健康指标数据
    health_metrics = {
        "weight": 70.5,
        "bmi": 22.5,
        "heart_rate": 72,
        "blood_pressure": {
            "systolic": 120,
            "diastolic": 80
        },
        "sleep_quality": {
            "sleep_duration": 7.5,
            "deep_sleep_ratio": 0.25,
            "sleep_score": 0.85
        },
        "activity_level": {
            "steps": 8500,
            "calories_burned": 2200,
            "active_minutes": 45
        }
    }

    # 健康分析算法
    def analyze_health(metrics):
        """分析健康状态"""
        overall_score = 0.0
        risk_factors = []
        recommendations = []

        # BMI评分
        bmi = metrics["bmi"]
        if 18.5 <= bmi <= 24.9:
            bmi_score = 1.0
        elif 25.0 <= bmi <= 29.9:
            bmi_score = 0.7
            risk_factors.append({
                "factor": "Overweight",
                "severity": "Medium",
                "recommendation": "控制饮食，增加运动"
            })
        else:
            bmi_score = 0.5
            risk_factors.append({
                "factor": "BMI异常",
                "severity": "High",
                "recommendation": "咨询医生"
            })

        # 心率评分
        heart_rate = metrics["heart_rate"]
        if 60 <= heart_rate <= 100:
            hr_score = 1.0
        else:
            hr_score = 0.7
            risk_factors.append({
                "factor": "心率异常",
                "severity": "Medium",
                "recommendation": "监测心率变化"
            })

        # 睡眠评分
        sleep_score = metrics["sleep_quality"]["sleep_score"]

        # 活动评分
        steps = metrics["activity_level"]["steps"]
        if steps >= 10000:
            activity_score = 1.0
        elif steps >= 5000:
            activity_score = 0.8
            recommendations.append({
                "recommendation": "增加日常活动量",
                "priority": "Low"
            })
        else:
            activity_score = 0.6
            risk_factors.append({
                "factor": "Sedentary lifestyle",
                "severity": "Low",
                "recommendation": "增加日常活动量"
            })
            recommendations.append({
                "recommendation": "增加日常活动量",
                "priority": "Medium"
            })

        # 综合评分
        overall_score = (
            bmi_score * 0.2 +
            hr_score * 0.2 +
            sleep_score * 0.3 +
            activity_score * 0.3
        )

        # 确定健康状态
        if overall_score >= 0.8:
            health_status = "Excellent"
        elif overall_score >= 0.7:
            health_status = "Good"
        elif overall_score >= 0.6:
            health_status = "Fair"
        else:
            health_status = "Poor"

        return {
            "overall_health_score": overall_score,
            "health_status": health_status,
            "risk_factors": risk_factors,
            "recommendations": recommendations
        }

    # 执行健康分析
    health_analysis = analyze_health(health_metrics)

    # 存储健康数据
    health_data = {
        "health_session_id": "HEALTH-20250121-001",
        "user_id": "USER-001",
        "timestamp": datetime.now(),
        "weight": health_metrics["weight"],
        "bmi": health_metrics["bmi"],
        "heart_rate": health_metrics["heart_rate"],
        "blood_pressure_systolic": health_metrics["blood_pressure"]["systolic"],
        "blood_pressure_diastolic": health_metrics["blood_pressure"]["diastolic"],
        "sleep_duration": health_metrics["sleep_quality"]["sleep_duration"],
        "sleep_score": health_metrics["sleep_quality"]["sleep_score"],
        "steps": health_metrics["activity_level"]["steps"],
        "calories_burned": health_metrics["activity_level"]["calories_burned"],
        "overall_health_score": health_analysis["overall_health_score"],
        "health_status": health_analysis["health_status"],
        "risk_factors": health_analysis["risk_factors"],
        "recommendations": health_analysis["recommendations"]
    }

    # 存储到数据库
    health_id = storage.store_device_data(health_data)
    print(f"Health data stored: {health_id}")

    print(f"\nSmart Health Monitoring Results:")
    print(f"  Overall health score: {health_analysis['overall_health_score']:.2f}")
    print(f"  Health status: {health_analysis['health_status']}")
    print(f"  Risk factors: {len(health_analysis['risk_factors'])}")
    print(f"  Recommendations: {len(health_analysis['recommendations'])}")

    return health_data

if __name__ == "__main__":
    smart_health_monitoring()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
