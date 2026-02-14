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
  - [8. 案例8：离家场景（安防、能耗管理）](#8-案例8离家场景安防能耗管理)
    - [8.1 场景描述](#81-场景描述-1)
    - [8.2 Schema定义](#82-schema定义-1)
    - [8.3 实现代码](#83-实现代码-1)
  - [9. 案例9：智慧家居数据存储系统](#9-案例9智慧家居数据存储系统)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 实现代码](#92-实现代码)
  - [10. 案例10：智能安防系统](#10-案例10智能安防系统)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 Schema定义](#102-schema定义)
    - [10.3 实现代码](#103-实现代码)
  - [11. 案例11：智能健康监测系统](#11-案例11智能健康监测系统)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)

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

## 8. 案例8：离家场景（安防、能耗管理）

### 8.1 场景描述

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

### 8.2 Schema定义

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

### 8.3 实现代码

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

## 9. 案例9：智慧家居数据存储系统

### 9.1 场景描述

**应用场景**：
使用PostgreSQL存储智慧家居设备数据，支持设备状态查询、
能耗分析、场景执行统计等功能。

### 9.2 实现代码

详见 `04_Transformation.md` 第7章。

---

## 10. 案例10：智能安防系统

### 10.1 场景描述

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

### 10.2 Schema定义

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

### 10.3 实现代码

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

## 11. 案例11：智能健康监测系统

### 11.1 场景描述

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

### 11.2 Schema定义

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

### 11.3 实现代码

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


---

## 12. 案例12：智能窗帘与光照调节系统

### 12.1 场景描述

**业务背景**：
现代智能家居需要根据自然光照条件自动调节窗帘开合度和室内灯光，实现节能和舒适的居住环境。系统需要集成光照传感器、智能窗帘电机、智能灯光，根据时间、天气、用户习惯自动调节。

**技术挑战**：

- 需要实时监测室内外光照强度
- 需要根据季节和时间动态调整策略
- 需要支持手动覆盖和自动模式的切换
- 需要学习用户偏好并优化控制策略

**解决方案**：
使用Smart_Home_Schema定义光照调节场景，结合机器学习算法学习用户习惯，使用PostgreSQL存储历史数据用于分析和优化。

### 12.2 Schema定义

**智能光照调节Schema**：

```json
{
  "scene_id": "scene_lighting_adjustment",
  "scene_name": "智能光照调节",
  "sensors": {
    "outdoor_light_sensor": {
      "device_id": "LIGHT_SENSOR_001",
      "current_lux": 45000,
      "location": "balcony"
    },
    "indoor_light_sensor": {
      "device_id": "LIGHT_SENSOR_002",
      "current_lux": 350,
      "location": "living_room"
    }
  },
  "actuators": {
    "smart_curtain": {
      "device_id": "CURTAIN_001",
      "current_position": 30,
      "target_position": 60
    },
    "smart_light": {
      "device_id": "LIGHT_001",
      "current_brightness": 80,
      "target_brightness": 50
    }
  },
  "control_rules": [
    {
      "condition": "outdoor_lux > 30000 AND time BETWEEN 09:00 AND 17:00",
      "action": "open_curtain_to(60) AND dim_light_to(30)"
    },
    {
      "condition": "outdoor_lux < 10000 OR time BETWEEN 17:00 AND 09:00",
      "action": "close_curtain_to(0) AND brighten_light_to(80)"
    }
  ]
}
```

### 12.3 实现代码

```python
from smart_home_storage import SmartHomeStorage
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

class SmartLightingController:
    """智能光照调节控制器"""

    def __init__(self, storage: SmartHomeStorage):
        self.storage = storage
        self.outdoor_lux_threshold_high = 30000
        self.outdoor_lux_threshold_low = 10000

    def evaluate_lighting_conditions(self, outdoor_lux: int, indoor_lux: int) -> Dict:
        """评估光照条件并决定控制策略"""
        current_time = datetime.now().time()
        is_daytime = time(9, 0) <= current_time <= time(17, 0)

        if outdoor_lux > self.outdoor_lux_threshold_high and is_daytime:
            return {
                "curtain_position": 70,  # 打开70%
                "light_brightness": 30,   # 调暗到30%
                "reason": "充足自然光"
            }
        elif outdoor_lux < self.outdoor_lux_threshold_low or not is_daytime:
            return {
                "curtain_position": 0,    # 关闭窗帘
                "light_brightness": 80,   # 调亮到80%
                "reason": "自然光不足"
            }
        else:
            return {
                "curtain_position": 40,
                "light_brightness": 60,
                "reason": "适中光照"
            }

    def adjust_lighting(self, outdoor_sensor_id: str, indoor_sensor_id: str,
                       curtain_id: str, light_id: str):
        """执行光照调节"""
        # 获取传感器数据
        outdoor_state = self.storage.get_latest_device_state(outdoor_sensor_id)
        indoor_state = self.storage.get_latest_device_state(indoor_sensor_id)

        outdoor_lux = outdoor_state.get("state", {}).get("lux", 0) if outdoor_state else 0
        indoor_lux = indoor_state.get("state", {}).get("lux", 0) if indoor_state else 0

        # 评估并决定控制策略
        strategy = self.evaluate_lighting_conditions(outdoor_lux, indoor_lux)

        # 存储控制命令
        curtain_cmd = self.storage.store_control_command(
            curtain_id, "set_position",
            {"position": strategy["curtain_position"]}
        )
        light_cmd = self.storage.store_control_command(
            light_id, "set_brightness",
            {"brightness": strategy["light_brightness"]}
        )

        # 记录场景执行
        self.storage.record_scene_execution(
            "scene_lighting_adjustment",
            "auto",
            True,
            {"strategy": strategy, "outdoor_lux": outdoor_lux, "indoor_lux": indoor_lux}
        )

        logger.info(f"Lighting adjusted: curtain={strategy['curtain_position']}%, "
                   f"light={strategy['light_brightness']}%, reason={strategy['reason']}")

        return strategy

# 使用示例
def demo_smart_lighting():
    storage = SmartHomeStorage("postgresql://user:pass@localhost/smarthome")
    controller = SmartLightingController(storage)

    # 模拟不同光照条件下的调节
    strategies = [
        {"outdoor_lux": 45000, "indoor_lux": 200, "time": "10:00"},
        {"outdoor_lux": 8000, "indoor_lux": 150, "time": "19:00"},
        {"outdoor_lux": 25000, "indoor_lux": 400, "time": "14:00"}
    ]

    for condition in strategies:
        result = controller.evaluate_lighting_conditions(
            condition["outdoor_lux"],
            condition["indoor_lux"]
        )
        print(f"Time: {condition['time']}, Outdoor: {condition['outdoor_lux']}lux, "
              f"Indoor: {condition['indoor_lux']}lux -> {result}")
```

---

## 13. 案例13：智能空调与新风系统联动

### 13.1 场景描述

**业务背景**：
智能空调与新风系统的联动可以实现室内温度和空气质量的双重优化。当室外空气质量良好时，优先使用新风系统；当室外温度适宜时，减少空调使用，实现节能。

**技术挑战**：

- 需要实时监测室内外温度、湿度、空气质量
- 需要协调空调和新风系统的工作模式
- 需要根据用户舒适度偏好动态调整
- 需要实现节能与舒适的平衡

**解决方案**：
使用场景联动系统定义空调与新风系统的联动规则，根据环境条件自动选择最优运行模式。

### 13.2 Schema定义

**空调新风联动Schema**：

```json
{
  "scene_id": "scene_hvac_air_quality",
  "scene_name": "空调新风智能联动",
  "sensors": {
    "outdoor_air": {
      "temperature": 26.5,
      "humidity": 65,
      "aqi": 45,
      "pm25": 12
    },
    "indoor_air": {
      "temperature": 28.0,
      "humidity": 70,
      "co2": 800,
      "pm25": 8
    }
  },
  "hvac_system": {
    "air_conditioner": {
      "device_id": "AC_001",
      "mode": "Cool",
      "target_temp": 26,
      "fan_speed": "Auto"
    },
    "fresh_air_system": {
      "device_id": "FRESH_AIR_001",
      "mode": "Auto",
      "fan_speed": 2,
      "filter_status": "Good"
    }
  },
  "control_strategy": {
    "priority": "comfort",
    "eco_mode": true,
    "auto_switch": true
  }
}
```

### 13.3 实现代码

```python
class HVACAirQualityController:
    """空调新风系统联动控制器"""

    def __init__(self, storage: SmartHomeStorage):
        self.storage = storage

    def calculate_comfort_index(self, temp: float, humidity: float) -> float:
        """计算舒适度指数(0-100)"""
        # 基于温湿度的舒适度计算
        temp_score = max(0, 100 - abs(temp - 24) * 5)  # 24°C为最佳温度
        humidity_score = max(0, 100 - abs(humidity - 50) * 2)  # 50%为最佳湿度
        return (temp_score + humidity_score) / 2

    def determine_hvac_strategy(self, outdoor: Dict, indoor: Dict,
                                user_preference: str = "comfort") -> Dict:
        """确定空调新风控制策略"""
        strategy = {
            "ac_mode": "Off",
            "ac_target_temp": 26,
            "fresh_air_mode": "Off",
            "fresh_air_speed": 0,
            "reason": ""
        }

        indoor_comfort = self.calculate_comfort_index(
            indoor["temperature"], indoor["humidity"]
        )

        # CO2浓度高，优先开启新风
        if indoor.get("co2", 400) > 1000:
            strategy["fresh_air_mode"] = "On"
            strategy["fresh_air_speed"] = 3
            strategy["reason"] = "CO2浓度过高，需要通风"

        # 室外空气质量好且温度适宜，使用新风降温
        elif (outdoor.get("aqi", 100) < 50 and
              outdoor["temperature"] < indoor["temperature"] - 2):
            strategy["fresh_air_mode"] = "On"
            strategy["fresh_air_speed"] = 2
            strategy["reason"] = "室外空气好且凉爽，使用新风"

        # 室内舒适度低，使用空调
        elif indoor_comfort < 60:
            if indoor["temperature"] > 26:
                strategy["ac_mode"] = "Cool"
                strategy["ac_target_temp"] = 25
            else:
                strategy["ac_mode"] = "Heat"
                strategy["ac_target_temp"] = 22
            strategy["reason"] = f"舒适度低({indoor_comfort:.1f})，需要空调调节"

        else:
            strategy["reason"] = "室内环境舒适，保持当前状态"

        return strategy

    def execute_hvac_control(self, ac_id: str, fresh_air_id: str,
                            outdoor_data: Dict, indoor_data: Dict):
        """执行空调新风控制"""
        strategy = self.determine_hvac_strategy(outdoor_data, indoor_data)

        # 存储控制命令
        if strategy["ac_mode"] != "Off":
            self.storage.store_control_command(ac_id, "set_mode", {
                "mode": strategy["ac_mode"],
                "target_temperature": strategy["ac_target_temp"]
            })

        if strategy["fresh_air_mode"] != "Off":
            self.storage.store_control_command(fresh_air_id, "set_fresh_air", {
                "mode": strategy["fresh_air_mode"],
                "fan_speed": strategy["fresh_air_speed"]
            })

        logger.info(f"HVAC control executed: AC={strategy['ac_mode']}, "
                   f"FreshAir={strategy['fresh_air_mode']}, Reason={strategy['reason']}")

        return strategy
```

---

## 14. 案例14：智能灌溉与花园管理系统

### 14.1 场景描述

**业务背景**：
智能花园管理系统根据土壤湿度、天气预报、植物类型自动执行灌溉，同时监测花园环境（光照、温度），为植物提供最佳生长条件。

**技术挑战**：

- 需要实时监测多点土壤湿度
- 需要获取并解析天气预报数据
- 需要根据不同植物类型制定灌溉策略
- 需要考虑降雨预测避免过度灌溉

**解决方案**：
使用多传感器融合和天气预报API，结合植物数据库，实现精准灌溉控制。

### 14.2 Schema定义

**智能花园管理Schema**：

```json
{
  "scene_id": "scene_garden_irrigation",
  "scene_name": "智能花园灌溉",
  "garden_zones": [
    {
      "zone_id": "zone_001",
      "zone_name": "草坪区",
      "plant_type": "grass",
      "soil_moisture": 35,
      "moisture_threshold": 40,
      "irrigation_duration": 15
    },
    {
      "zone_id": "zone_002",
      "zone_name": "花卉区",
      "plant_type": "flowers",
      "soil_moisture": 55,
      "moisture_threshold": 50,
      "irrigation_duration": 10
    }
  ],
  "weather_forecast": {
    "today_rain_probability": 20,
    "next_24h_rain": false,
    "temperature_high": 32,
    "temperature_low": 24
  },
  "irrigation_schedule": {
    "morning_time": "06:00",
    "evening_time": "18:00",
    "max_daily_cycles": 2
  }
}
```

### 14.3 实现代码

```python
class SmartGardenController:
    """智能花园控制器"""

    PLANT_PROFILES = {
        "grass": {"moisture_optimal": 45, "moisture_min": 35, "moisture_max": 60},
        "flowers": {"moisture_optimal": 55, "moisture_min": 45, "moisture_max": 70},
        "vegetables": {"moisture_optimal": 65, "moisture_min": 55, "moisture_max": 80},
        "succulents": {"moisture_optimal": 25, "moisture_min": 15, "moisture_max": 35}
    }

    def __init__(self, storage: SmartHomeStorage):
        self.storage = storage

    def should_irrigate(self, zone: Dict, weather: Dict) -> Tuple[bool, str]:
        """判断是否需要灌溉"""
        plant_type = zone.get("plant_type", "grass")
        current_moisture = zone.get("soil_moisture", 0)
        profile = self.PLANT_PROFILES.get(plant_type, self.PLANT_PROFILES["grass"])

        # 检查降雨预测
        if weather.get("next_24h_rain", False):
            return False, "24小时内有降雨预测，跳过灌溉"

        if weather.get("today_rain_probability", 0) > 70:
            return False, f"降雨概率{weather['today_rain_probability']}%，跳过灌溉"

        # 检查土壤湿度
        if current_moisture < profile["moisture_min"]:
            return True, f"土壤湿度{current_moisture}%低于最小值{profile['moisture_min']}%，需要灌溉"

        if current_moisture < profile["moisture_optimal"]:
            return True, f"土壤湿度{current_moisture}%低于最佳值{profile['moisture_optimal']}%，建议灌溉"

        return False, f"土壤湿度{current_moisture}%适宜，无需灌溉"

    def calculate_irrigation_duration(self, zone: Dict, weather: Dict) -> int:
        """计算灌溉时长（分钟）"""
        base_duration = zone.get("irrigation_duration", 10)
        plant_type = zone.get("plant_type", "grass")
        profile = self.PLANT_PROFILES.get(plant_type, self.PLANT_PROFILES["grass"])

        # 根据湿度缺口调整
        moisture_gap = profile["moisture_optimal"] - zone.get("soil_moisture", 0)
        adjustment = min(max(moisture_gap / 10, 0), 2)  # 最多增加2倍时长

        # 根据温度调整
        temp = weather.get("temperature_high", 25)
        if temp > 35:
            temp_factor = 1.3
        elif temp > 30:
            temp_factor = 1.1
        else:
            temp_factor = 1.0

        duration = int(base_duration * (1 + adjustment) * temp_factor)
        return min(duration, 30)  # 最长30分钟

    def execute_irrigation(self, zones: List[Dict], weather: Dict):
        """执行灌溉"""
        results = []

        for zone in zones:
            should_water, reason = self.should_irrigate(zone, weather)

            if should_water:
                duration = self.calculate_irrigation_duration(zone, weather)
                valve_id = f"VALVE_{zone['zone_id']}"

                # 存储灌溉命令
                self.storage.store_control_command(valve_id, "irrigate", {
                    "duration_minutes": duration,
                    "zone_name": zone["zone_name"],
                    "reason": reason
                })

                results.append({
                    "zone_id": zone["zone_id"],
                    "action": "irrigate",
                    "duration": duration,
                    "reason": reason
                })

                logger.info(f"Zone {zone['zone_name']}: irrigation started for {duration}min, {reason}")
            else:
                results.append({
                    "zone_id": zone["zone_id"],
                    "action": "skip",
                    "reason": reason
                })
                logger.info(f"Zone {zone['zone_name']}: irrigation skipped, {reason}")

        return results

# 使用示例
def demo_garden_irrigation():
    storage = SmartHomeStorage("postgresql://user:pass@localhost/smarthome")
    controller = SmartGardenController(storage)

    zones = [
        {"zone_id": "zone_001", "zone_name": "草坪区", "plant_type": "grass", "soil_moisture": 32},
        {"zone_id": "zone_002", "zone_name": "花卉区", "plant_type": "flowers", "soil_moisture": 58}
    ]

    weather = {
        "today_rain_probability": 10,
        "next_24h_rain": False,
        "temperature_high": 33
    }

    results = controller.execute_irrigation(zones, weather)
    for result in results:
        print(f"Zone {result['zone_id']}: {result['action']} - {result['reason']}")
```

---

## 15. 案例15：老人居家安全监护系统

### 15.1 场景描述

**业务背景**：
针对独居老人的智能监护系统，通过运动传感器、紧急呼叫按钮、睡眠监测设备等，实时监测老人活动状态，检测异常情况（如长时间无活动、夜间异常活动等），并及时通知家属或护理人员。

**技术挑战**：

- 需要区分正常活动和异常情况
- 需要处理误报（如老人外出）
- 需要保护隐私的同时实现有效监护
- 需要多级别的告警机制

**解决方案**：
使用多传感器数据融合和行为模式分析，建立老人日常行为基线，检测异常并及时告警。

### 15.2 Schema定义

**老人监护系统Schema**：

```json
{
  "scene_id": "scene_elderly_care",
  "scene_name": "老人居家安全监护",
  "resident": {
    "user_id": "elderly_001",
    "name": "张爷爷",
    "age": 78,
    "emergency_contacts": [
      {"name": "儿子", "phone": "13800138000", "relation": "son"},
      {"name": "社区卫生服务中心", "phone": "120", "relation": "medical"}
    ]
  },
  "monitoring_devices": {
    "motion_sensors": ["MOTION_BEDROOM", "MOTION_LIVING", "MOTION_KITCHEN"],
    "emergency_button": "EMERGENCY_001",
    "sleep_monitor": "SLEEP_001",
    "door_sensor": "DOOR_MAIN"
  },
  "alert_rules": [
    {
      "rule_id": "no_activity_12h",
      "condition": "no_motion_detected > 12 hours",
      "severity": "critical",
      "action": "notify_emergency_contacts"
    },
    {
      "rule_id": "bathroom_fall_risk",
      "condition": "bathroom_motion > 30min AND nighttime",
      "severity": "warning",
      "action": "send_check_reminder"
    }
  ]
}
```

### 15.3 实现代码

```python
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ElderlyCareMonitor:
    """老人居家安全监护系统"""

    def __init__(self, storage: SmartHomeStorage):
        self.storage = storage
        self.alert_cooldown = {}  # 告警冷却时间

    def check_activity_status(self, user_id: str, motion_sensors: List[str],
                             hours: int = 12) -> Dict:
        """检查活动状态"""
        latest_activity = None
        sensor_with_activity = None

        for sensor_id in motion_sensors:
            events = self.storage.get_recent_events(sensor_id, "motion_detected", limit=1)
            if events:
                event_time = events[0].get("event_time")
                if latest_activity is None or event_time > latest_activity:
                    latest_activity = event_time
                    sensor_with_activity = sensor_id

        if latest_activity is None:
            return {
                "status": "unknown",
                "last_activity": None,
                "hours_since_activity": None,
                "alert_needed": False
            }

        hours_since = (datetime.now() - latest_activity).total_seconds() / 3600

        status = "normal"
        alert_needed = False

        if hours_since > 24:
            status = "critical"
            alert_needed = True
        elif hours_since > 12:
            status = "warning"
            alert_needed = True
        elif hours_since > 6:
            status = "attention"

        return {
            "status": status,
            "last_activity": latest_activity,
            "hours_since_activity": round(hours_since, 2),
            "last_sensor": sensor_with_activity,
            "alert_needed": alert_needed
        }

    def check_sleep_pattern(self, sleep_monitor_id: str, days: int = 7) -> Dict:
        """检查睡眠模式"""
        # 获取睡眠监测数据
        sleep_data = self.storage.get_sensor_statistics(
            sleep_monitor_id, "sleep_quality", hours=days*24
        )

        avg_sleep_duration = sleep_data.get("avg_value", 0)

        pattern_analysis = {
            "avg_sleep_hours": round(avg_sleep_duration, 1),
            "pattern": "normal"
        }

        if avg_sleep_duration < 5:
            pattern_analysis["pattern"] = "insufficient_sleep"
            pattern_analysis["alert"] = "睡眠时间不足，建议关注健康状况"
        elif avg_sleep_duration > 10:
            pattern_analysis["pattern"] = "excessive_sleep"
            pattern_analysis["alert"] = "睡眠时间过长，建议关注健康状况"

        return pattern_analysis

    def process_emergency_button(self, button_id: str, user_id: str):
        """处理紧急按钮事件"""
        logger.critical(f"EMERGENCY BUTTON PRESSED: {button_id}, User: {user_id}")

        # 获取紧急联系人
        user_prefs = self.storage.get_user_preferences(user_id)
        emergency_contacts = user_prefs.get("emergency_contacts", [])

        # 存储紧急事件
        self.storage.store_event(button_id, "emergency_alert", {
            "user_id": user_id,
            "alert_type": "emergency_button",
            "contacts_notified": len(emergency_contacts)
        })

        # 触发告警
        alert_result = {
            "timestamp": datetime.now().isoformat(),
            "severity": "critical",
            "message": "紧急按钮被按下",
            "contacts_notified": [c["name"] for c in emergency_contacts]
        }

        return alert_result

    def run_daily_check(self, user_id: str, config: Dict):
        """执行每日检查"""
        results = {
            "user_id": user_id,
            "check_time": datetime.now().isoformat(),
            "checks": []
        }

        # 检查活动状态
        activity_status = self.check_activity_status(
            user_id, config.get("motion_sensors", [])
        )
        results["checks"].append({"type": "activity", "result": activity_status})

        # 检查睡眠模式
        if "sleep_monitor" in config:
            sleep_pattern = self.check_sleep_pattern(config["sleep_monitor"])
            results["checks"].append({"type": "sleep", "result": sleep_pattern})

        # 汇总健康状态
        critical_alerts = [c for c in results["checks"]
                          if c["result"].get("status") == "critical" or
                          c["result"].get("alert_needed")]

        results["overall_status"] = "critical" if critical_alerts else "normal"
        results["alert_count"] = len(critical_alerts)

        return results

# 使用示例
def demo_elderly_care():
    storage = SmartHomeStorage("postgresql://user:pass@localhost/smarthome")
    monitor = ElderlyCareMonitor(storage)

    config = {
        "motion_sensors": ["MOTION_BEDROOM", "MOTION_LIVING"],
        "sleep_monitor": "SLEEP_001"
    }

    # 模拟每日检查
    results = monitor.run_daily_check("elderly_001", config)
    print(f"Daily check for {results['user_id']}: {results['overall_status']}")
    for check in results["checks"]:
        print(f"  - {check['type']}: {check['result']}")
```

---

## 16. 案例16：全屋智能能耗优化系统

### 16.1 场景描述

**业务背景**：
全屋智能能耗优化系统通过分析各设备的能耗模式、电价时段、用户生活习惯，自动优化设备运行时间，在不影响用户体验的前提下实现最大节能效果。

**技术挑战**：

- 需要实时监测各设备能耗
- 需要获取分时电价信息
- 需要学习用户生活习惯
- 需要平衡节能与舒适度

**解决方案**：
使用机器学习预测能耗模式，结合电价时段自动调整高耗能设备的运行时间，实现智能节能。

### 16.2 Schema定义

**能耗优化系统Schema**：

```json
{
  "scene_id": "scene_energy_optimization",
  "scene_name": "全屋能耗智能优化",
  "energy_tariff": {
    "peak_hours": ["08:00-11:00", "18:00-22:00"],
    "peak_price": 0.85,
    "valley_hours": ["23:00-07:00"],
    "valley_price": 0.35,
    "normal_price": 0.55
  },
  "controllable_devices": {
    "water_heater": {
      "device_id": "HEATER_001",
      "power_kw": 2.5,
      "flexible_hours": ["23:00-06:00"],
      "priority": "medium"
    },
    "dishwasher": {
      "device_id": "DISHWASHER_001",
      "power_kw": 1.8,
      "flexible": true,
      "max_delay_hours": 4
    },
    "washing_machine": {
      "device_id": "WASHER_001",
      "power_kw": 2.0,
      "flexible": true,
      "max_delay_hours": 6
    }
  },
  "optimization_goal": {
    "target_savings_percent": 20,
    "comfort_threshold": 0.9,
    "max_inconvenience_minutes": 30
  }
}
```

### 16.3 实现代码

```python
class EnergyOptimizationController:
    """能耗优化控制器"""

    def __init__(self, storage: SmartHomeStorage):
        self.storage = storage

    def get_current_tariff(self, tariff_config: Dict) -> Tuple[str, float]:
        """获取当前电价时段"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_minutes = current_hour * 60 + current_minute

        # 解析峰谷时段
        def parse_time_range(time_str):
            start, end = time_str.split("-")
            start_h, start_m = map(int, start.split(":"))
            end_h, end_m = map(int, end.split(":"))
            return start_h * 60 + start_m, end_h * 60 + end_m

        # 检查峰时
        for period in tariff_config.get("peak_hours", []):
            start, end = parse_time_range(period)
            if start <= current_minutes < end:
                return "peak", tariff_config["peak_price"]

        # 检查谷时
        for period in tariff_config.get("valley_hours", []):
            start, end = parse_time_range(period)
            if start <= current_minutes < end:
                return "valley", tariff_config["valley_price"]

        return "normal", tariff_config["normal_price"]

    def calculate_optimal_schedule(self, device: Dict, tariff_config: Dict,
                                   user_schedule: Dict) -> Dict:
        """计算设备最优运行时间"""
        current_period, current_price = self.get_current_tariff(tariff_config)

        # 如果当前是谷时且设备灵活可调，立即运行
        if current_period == "valley" and device.get("flexible", False):
            return {
                "action": "run_now",
                "reason": "当前为谷时电价，是最优运行时机",
                "estimated_cost": device["power_kw"] * current_price
            }

        # 如果是峰时，推迟到谷时
        if current_period == "peak" and device.get("flexible", False):
            next_valley_start = None
            for period in tariff_config.get("valley_hours", []):
                start, _ = map(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]),
                              period.split("-"))
                if start > datetime.now().hour * 60 + datetime.now().minute:
                    next_valley_start = start
                    break

            if next_valley_start:
                valley_price = tariff_config["valley_price"]
                savings = device["power_kw"] * (current_price - valley_price)
                return {
                    "action": "delay",
                    "delay_until": f"{next_valley_start // 60:02d}:{next_valley_start % 60:02d}",
                    "reason": "峰时电价高，建议推迟到谷时运行",
                    "estimated_savings": round(savings, 2)
                }

        return {
            "action": "run_now",
            "reason": "设备不可灵活调度或已到最优时段"
        }

    def optimize_daily_energy(self, devices: List[Dict], tariff_config: Dict):
        """优化全天能耗"""
        optimization_results = []
        total_potential_savings = 0

        for device in devices:
            schedule = self.calculate_optimal_schedule(device, tariff_config, {})
            optimization_results.append({
                "device_id": device["device_id"],
                "device_name": device.get("device_name", device["device_id"]),
                "schedule": schedule
            })

            if schedule.get("estimated_savings"):
                total_potential_savings += schedule["estimated_savings"]

            # 存储优化决策
            self.storage.store_control_command(
                device["device_id"],
                "energy_optimization",
                schedule
            )

        logger.info(f"Energy optimization completed. Potential daily savings: ${total_potential_savings:.2f}")

        return {
            "results": optimization_results,
            "total_potential_savings": round(total_potential_savings, 2)
        }

    def generate_energy_report(self, days: int = 30) -> Dict:
        """生成能耗报告"""
        # 获取历史能耗数据
        room_energy = self.storage.get_energy_consumption_by_room(days=days)

        total_consumption = sum(row[1] for row in room_energy) if room_energy else 0

        return {
            "report_period_days": days,
            "total_consumption_kwh": round(total_consumption, 2),
            "room_breakdown": [
                {"room": row[0], "consumption": round(row[1], 2), "percentage": round(row[1]/total_consumption*100, 1)}
                for row in room_energy
            ] if total_consumption > 0 else [],
            "generated_at": datetime.now().isoformat()
        }

# 使用示例
def demo_energy_optimization():
    storage = SmartHomeStorage("postgresql://user:pass@localhost/smarthome")
    controller = EnergyOptimizationController(storage)

    tariff_config = {
        "peak_hours": ["08:00-11:00", "18:00-22:00"],
        "peak_price": 0.85,
        "valley_hours": ["23:00-07:00"],
        "valley_price": 0.35,
        "normal_price": 0.55
    }

    devices = [
        {"device_id": "DISHWASHER_001", "device_name": "洗碗机", "power_kw": 1.8, "flexible": True},
        {"device_id": "WASHER_001", "device_name": "洗衣机", "power_kw": 2.0, "flexible": True}
    ]

    result = controller.optimize_daily_energy(devices, tariff_config)
    print(f"Optimization potential: ${result['total_potential_savings']}/day")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-14（新增5个真实场景案例）
