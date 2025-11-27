# 农业物联网Schema实践案例

## 📑 目录

- [农业物联网Schema实践案例](#农业物联网schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：农田环境监测系统](#2-案例1农田环境监测系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 实现代码](#22-实现代码)
  - [3. 案例2：智能灌溉控制系统](#3-案例2智能灌溉控制系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)

---

## 1. 案例概述

本文档提供农业物联网Schema在实际应用中的实践案例。

---

## 2. 案例1：农田环境监测系统

### 2.1 场景描述

**业务背景**：
使用LoRaWAN传感器实时监测农田环境数据，包括土壤湿度、温度、气象数据等。

**技术挑战**：

- 需要低功耗传感器设备
- 需要广域网覆盖
- 需要实时数据传输

**解决方案**：
使用LoRaWAN协议采集传感器数据，转换为MQTT消息，存储到PostgreSQL。

### 2.2 实现代码

```python
from agricultural_iot_storage import AgriculturalIoTStorage
from lorawan_to_mqtt_converter import LoRaWANToMQTTConverter
from datetime import datetime

# 初始化存储和转换器
storage = AgriculturalIoTStorage("postgresql://user:pass@localhost/agricultural_iot")
converter = LoRaWANToMQTTConverter()

# 注册IoT设备
storage.store_device(
    device_id="DEV001",
    device_type="Sensor",
    device_name="土壤传感器1号",
    latitude=39.9042,
    longitude=116.4074
)

# 接收LoRaWAN数据包并转换
lorawan_packet = {
    "dev_eui": "DEV001",
    "payload": {
        "soil_moisture": 45.2,
        "soil_temperature": 18.5,
        "air_temperature": 22.3,
        "air_humidity": 65.0
    },
    "rssi": -120,
    "snr": 5
}

# 转换为MQTT消息
mqtt_message = converter.convert_lorawan_to_mqtt(lorawan_packet)

# 存储传感器数据
storage.store_sensor_data(
    device_id="DEV001",
    timestamp=datetime.now(),
    soil_moisture=lorawan_packet["payload"]["soil_moisture"],
    soil_temperature=lorawan_packet["payload"]["soil_temperature"],
    air_temperature=lorawan_packet["payload"]["air_temperature"],
    air_humidity=lorawan_packet["payload"]["air_humidity"]
)
```

---

## 3. 案例2：智能灌溉控制系统

### 3.1 场景描述

**业务背景**：
根据土壤湿度数据自动控制灌溉设备，实现精准灌溉。

**技术挑战**：

- 需要实时监测土壤湿度
- 需要控制灌溉设备
- 需要低延迟响应

**解决方案**：
使用实时监测和控制机制，结合MQTT消息队列，实现低延迟的智能灌溉控制。

### 3.2 实现代码

```python
import json
import logging
from typing import Optional, Dict
from datetime import datetime
from agricultural_iot_storage import AgriculturalIoTStorage

logger = logging.getLogger(__name__)

class IrrigationController:
    """智能灌溉控制器"""

    def __init__(self, storage: AgriculturalIoTStorage, mqtt_client=None):
        self.storage = storage
        self.mqtt_client = mqtt_client
        self.moisture_threshold = 30.0  # 土壤湿度阈值（%）
        self.irrigation_duration = 30  # 默认灌溉时长（分钟）

    def control_irrigation(self, device_id: str) -> Optional[Dict]:
        """根据土壤湿度控制灌溉"""
        try:
            # 查询最新土壤湿度数据
            self.storage.cur.execute("""
                SELECT soil_moisture, timestamp
                FROM sensor_data
                WHERE device_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (device_id,))

            result = self.storage.cur.fetchone()
            if not result or result[0] is None:
                logger.warning(f"设备 {device_id} 没有土壤湿度数据")
                return None

            soil_moisture = result[0]
            timestamp = result[1]

            logger.info(f"设备 {device_id} 当前土壤湿度: {soil_moisture}%")

            # 如果土壤湿度低于阈值，启动灌溉
            if soil_moisture < self.moisture_threshold:
                logger.info(f"土壤湿度低于阈值 {self.moisture_threshold}%，启动灌溉")

                # 构建控制命令
                control_message = {
                    "topic": f"agriculture/control/{device_id}",
                    "payload": json.dumps({
                        "action": "start_irrigation",
                        "duration": self.irrigation_duration,
                        "timestamp": datetime.now().isoformat(),
                        "moisture_level": soil_moisture
                    })
                }

                # 发送MQTT消息
                if self.mqtt_client:
                    self.mqtt_client.publish(
                        control_message["topic"],
                        control_message["payload"]
                    )
                    logger.info(f"已发送灌溉控制命令到设备 {device_id}")
                else:
                    logger.warning("MQTT客户端未配置，无法发送控制命令")

                # 记录控制命令
                self.storage.store_control_command(
                    device_id=device_id,
                    command_type="IrrigationControl",
                    command_payload=json.loads(control_message["payload"]),
                    status="sent"
                )

                return control_message
            else:
                logger.info(f"土壤湿度 {soil_moisture}% 高于阈值，无需灌溉")
                return None

        except Exception as e:
            logger.error(f"控制灌溉时发生错误: {e}", exc_info=True)
            raise RuntimeError(f"灌溉控制失败: {e}") from e

    def set_moisture_threshold(self, threshold: float):
        """设置土壤湿度阈值"""
        if not 0 <= threshold <= 100:
            raise ValueError("土壤湿度阈值必须在0-100之间")
        self.moisture_threshold = threshold
        logger.info(f"土壤湿度阈值已更新为: {threshold}%")

    def set_irrigation_duration(self, duration: int):
        """设置灌溉时长"""
        if duration <= 0:
            raise ValueError("灌溉时长必须大于0")
        self.irrigation_duration = duration
        logger.info(f"灌溉时长已更新为: {duration}分钟")

# 使用示例
if __name__ == "__main__":
    # 初始化存储
    storage = AgriculturalIoTStorage("postgresql://user:pass@localhost/agricultural_iot")

    # 初始化控制器
    controller = IrrigationController(storage)

    # 设置阈值和时长
    controller.set_moisture_threshold(30.0)
    controller.set_irrigation_duration(30)

    # 控制灌溉
    device_id = "DEV001"
    result = controller.control_irrigation(device_id)

    if result:
        print(f"已发送灌溉控制命令: {result}")
    else:
        print("无需灌溉")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
