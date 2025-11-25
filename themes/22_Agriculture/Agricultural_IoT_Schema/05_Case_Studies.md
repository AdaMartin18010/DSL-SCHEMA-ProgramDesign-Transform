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

**

3.2 实现代码

```python
def control_irrigation(storage: AgriculturalIoTStorage, device_id: str):
    """根据土壤湿度控制灌溉"""
    # 查询最新土壤湿度数据
    storage.cur.execute("""
        SELECT soil_moisture, timestamp
        FROM sensor_data
        WHERE device_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """, (device_id,))

    result = storage.cur.fetchone()
    if result and result[0] is not None:
        soil_moisture = result[0]

        # 如果土壤湿度低于30%，启动灌溉
        if soil_moisture < 30.0:
            # 发送控制命令到MQTT
            control_message = {
                "topic": f"agriculture/control/{device_id}",
                "payload": json.dumps({
                    "action": "start_irrigation",
                    "duration": 30  # 分钟
                })
            }
            return control_message
    return None
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
