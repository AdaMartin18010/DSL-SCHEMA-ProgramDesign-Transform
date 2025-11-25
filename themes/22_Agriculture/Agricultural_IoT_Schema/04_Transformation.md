# 农业物联网Schema转换体系

## 📑 目录

- [农业物联网Schema转换体系](#农业物联网schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. LoRaWAN到MQTT转换](#2-lorawan到mqtt转换)
  - [3. PostgreSQL农业物联网数据存储](#3-postgresql农业物联网数据存储)

---

## 1. 转换体系概述

农业物联网Schema转换体系支持LoRaWAN、MQTT、CoAP、数据库存储之间的转换。

### 1.1 转换目标

1. **LoRaWAN到MQTT转换**：LoRaWAN数据包到MQTT消息
2. **MQTT到OGC SensorThings转换**：MQTT消息到OGC SensorThings API
3. **数据到数据库转换**：农业物联网数据到PostgreSQL存储

---

## 2. LoRaWAN到MQTT转换

**完整的LoRaWAN到MQTT转换实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class LoRaWANToMQTTConverter:
    """LoRaWAN到MQTT转换器"""

    def convert_lorawan_to_mqtt(self, lorawan_packet: Dict) -> Optional[Dict]:
        """将LoRaWAN数据包转换为MQTT消息"""
        try:
            mqtt_message = {
                "topic": f"agriculture/sensor/{lorawan_packet.get('dev_eui', '')}",
                "payload": json.dumps({
                    "device_id": lorawan_packet.get("dev_eui", ""),
                    "timestamp": datetime.now().isoformat(),
                    "data": lorawan_packet.get("payload", {}),
                    "rssi": lorawan_packet.get("rssi", 0),
                    "snr": lorawan_packet.get("snr", 0)
                }),
                "qos": 1,
                "retain": False
            }
            return mqtt_message
        except Exception as e:
            logger.error(f"Failed to convert LoRaWAN to MQTT: {e}")
            return None
```

---

## 3. PostgreSQL农业物联网数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AgriculturalIoTStorage:
    """农业物联网数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # IoT设备表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iot_devices (
                device_id VARCHAR(50) PRIMARY KEY,
                device_type VARCHAR(50) NOT NULL,
                device_name VARCHAR(200),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                online BOOLEAN DEFAULT FALSE,
                battery_level DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 传感器数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(50) REFERENCES iot_devices(device_id),
                timestamp TIMESTAMP NOT NULL,
                soil_moisture DECIMAL(5, 2),
                soil_temperature DECIMAL(5, 2),
                air_temperature DECIMAL(5, 2),
                air_humidity DECIMAL(5, 2),
                rainfall DECIMAL(6, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_data_device_time ON sensor_data(device_id, timestamp)")
        self.conn.commit()

    def store_device(self, device_id: str, device_type: str,
                    device_name: str = None, latitude: float = None,
                    longitude: float = None) -> Optional[str]:
        """存储IoT设备信息"""
        if not device_id or not device_type:
            raise ValueError("Device ID and device type are required")

        try:
            self.cur.execute("""
                INSERT INTO iot_devices (
                    device_id, device_type, device_name, latitude, longitude
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (device_id) DO UPDATE SET
                    device_type = EXCLUDED.device_type,
                    device_name = EXCLUDED.device_name,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
                RETURNING device_id
            """, (device_id, device_type, device_name, latitude, longitude))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored IoT device: {device_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing device: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def store_sensor_data(self, device_id: str, timestamp: datetime,
                         soil_moisture: float = None,
                         soil_temperature: float = None,
                         air_temperature: float = None,
                         air_humidity: float = None,
                         rainfall: float = None) -> Optional[int]:
        """存储传感器数据"""
        if not device_id or not timestamp:
            raise ValueError("Device ID and timestamp are required")

        try:
            self.cur.execute("""
                INSERT INTO sensor_data (
                    device_id, timestamp, soil_moisture, soil_temperature,
                    air_temperature, air_humidity, rainfall
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (device_id, timestamp, soil_moisture, soil_temperature,
                  air_temperature, air_humidity, rainfall))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored sensor data: {device_id} at {timestamp}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing sensor data: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
