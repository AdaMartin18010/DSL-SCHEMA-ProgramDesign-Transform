# Smart City Schema转换体系

## 📑 目录

- [Smart City Schema转换体系](#smart-city-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 传感器数据转换](#2-传感器数据转换)
  - [3. 城市数据聚合](#3-城市数据聚合)
  - [4. 数据格式转换](#4-数据格式转换)
  - [5. Smart City数据存储与分析](#5-smart-city数据存储与分析)
    - [5.1 PostgreSQL Smart City数据存储](#51-postgresql-smart-city数据存储)
    - [5.2 Smart City数据分析查询](#52-smart-city数据分析查询)

---

## 1. 转换体系概述

Smart City Schema转换体系支持传感器数据、
城市数据、数据库存储之间的转换。

### 1.1 转换目标

1. **传感器数据到城市数据转换**：IoT传感器数据到城市数据格式
2. **城市数据聚合**：多个数据源的城市数据聚合
3. **数据格式转换**：不同格式之间的数据转换
4. **城市数据到数据库转换**：城市数据到PostgreSQL存储

---

## 2. 传感器数据转换

**转换规则**：

- IoT传感器数据 → 智慧交通数据
- IoT传感器数据 → 智慧能源数据
- IoT传感器数据 → 智慧环境数据

**转换示例**：

```python
def convert_sensor_to_traffic_data(sensor_data: dict) -> dict:
    """将传感器数据转换为智慧交通数据"""
    traffic_data = {
        "location": {
            "latitude": sensor_data.get("latitude"),
            "longitude": sensor_data.get("longitude")
        },
        "flow_data": {
            "vehicle_count": sensor_data.get("vehicle_count", 0),
            "average_speed": sensor_data.get("average_speed", 0),
            "congestion_level": calculate_congestion_level(
                sensor_data.get("vehicle_count", 0),
                sensor_data.get("average_speed", 0)
            ),
            "timestamp": sensor_data.get("timestamp")
        }
    }
    return traffic_data

def convert_sensor_to_energy_data(sensor_data: dict) -> dict:
    """将传感器数据转换为智慧能源数据"""
    energy_data = {
        "meter_id": sensor_data.get("device_id"),
        "location": {
            "latitude": sensor_data.get("latitude"),
            "longitude": sensor_data.get("longitude")
        },
        "consumption_type": sensor_data.get("consumption_type", "Residential"),
        "current_consumption": sensor_data.get("power_consumption", 0),
        "timestamp": sensor_data.get("timestamp")
    }
    return energy_data
```

---

## 3. 城市数据聚合

**聚合规则**：

- 多个传感器数据 → 聚合城市数据
- 时间序列数据聚合
- 空间数据聚合

**聚合示例**：

```python
def aggregate_city_data(data_list: List[dict]) -> dict:
    """聚合城市数据"""
    if not data_list:
        return None

    aggregated = {
        "location": data_list[0].get("location"),
        "aggregated_values": {},
        "data_count": len(data_list),
        "timestamp": max(d.get("timestamp") for d in data_list)
    }

    # 聚合数值字段
    numeric_fields = ["vehicle_count", "current_consumption", "aqi"]
    for field in numeric_fields:
        values = [d.get(field) for d in data_list if d.get(field) is not None]
        if values:
            aggregated["aggregated_values"][field] = {
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }

    return aggregated
```

---

## 4. 数据格式转换

**转换规则**：

- JSON ↔ XML
- CSV ↔ JSON
- GeoJSON ↔ 标准格式

**转换示例**：

```python
def convert_json_to_geojson(city_data: dict) -> dict:
    """将JSON格式转换为GeoJSON格式"""
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                city_data.get("location", {}).get("longitude"),
                city_data.get("location", {}).get("latitude")
            ]
        },
        "properties": {
            k: v for k, v in city_data.items() if k != "location"
        }
    }
    return geojson
```

---

## 5. Smart City数据存储与分析

### 5.1 PostgreSQL Smart City数据存储

**数据库设计**：

```python
import psycopg2
from datetime import datetime
from typing import List, Optional, Dict
import uuid
import json

class SmartCityStorage:
    """Smart City数据PostgreSQL存储类"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.create_tables()

    def create_tables(self):
        """创建Smart City数据存储表"""
        cursor = self.conn.cursor()

        # IoT设备表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iot_devices (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                device_id VARCHAR(255) NOT NULL UNIQUE,
                device_type VARCHAR(50) NOT NULL,
                location_latitude DECIMAL(10, 7),
                location_longitude DECIMAL(10, 7),
                location_address VARCHAR(255),
                status VARCHAR(20) DEFAULT 'Online',
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 传感器数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                device_id VARCHAR(255) NOT NULL REFERENCES iot_devices(device_id),
                sensor_type VARCHAR(50) NOT NULL,
                sensor_value DECIMAL(15, 4),
                sensor_unit VARCHAR(20),
                timestamp TIMESTAMP NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 智慧交通数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                location_latitude DECIMAL(10, 7) NOT NULL,
                location_longitude DECIMAL(10, 7) NOT NULL,
                vehicle_count INTEGER DEFAULT 0,
                average_speed DECIMAL(10, 2),
                congestion_level VARCHAR(20),
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 智慧能源数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                meter_id VARCHAR(255) NOT NULL,
                location_latitude DECIMAL(10, 7),
                location_longitude DECIMAL(10, 7),
                consumption_type VARCHAR(50),
                current_consumption DECIMAL(15, 4),
                daily_consumption DECIMAL(15, 4),
                monthly_consumption DECIMAL(15, 4),
                peak_demand DECIMAL(15, 4),
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 智慧环境数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environment_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                station_id VARCHAR(255) NOT NULL,
                location_latitude DECIMAL(10, 7) NOT NULL,
                location_longitude DECIMAL(10, 7) NOT NULL,
                data_type VARCHAR(50) NOT NULL,
                aqi INTEGER,
                pm25 DECIMAL(10, 2),
                pm10 DECIMAL(10, 2),
                temperature DECIMAL(10, 2),
                humidity DECIMAL(5, 2),
                noise_level DECIMAL(10, 2),
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Smart City统计信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smart_city_statistics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                statistic_type VARCHAR(50) NOT NULL,
                data_category VARCHAR(50),
                statistic_date DATE NOT NULL,
                count_value BIGINT DEFAULT 0,
                aggregated_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_id ON iot_devices(device_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_device_timestamp ON sensor_data(device_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_location_timestamp ON traffic_data(location_latitude, location_longitude, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_energy_meter_timestamp ON energy_data(meter_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_environment_station_timestamp ON environment_data(station_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smart_city_statistics_date ON smart_city_statistics(statistic_date)")

        self.conn.commit()
        cursor.close()

    def store_traffic_data(self, traffic_data: dict) -> str:
        """存储智慧交通数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO traffic_data (
                location_latitude, location_longitude,
                vehicle_count, average_speed, congestion_level, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            traffic_data.get("location", {}).get("latitude"),
            traffic_data.get("location", {}).get("longitude"),
            traffic_data.get("flow_data", {}).get("vehicle_count"),
            traffic_data.get("flow_data", {}).get("average_speed"),
            traffic_data.get("flow_data", {}).get("congestion_level"),
            traffic_data.get("flow_data", {}).get("timestamp")
        ))
        traffic_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return str(traffic_id)

    def store_energy_data(self, energy_data: dict) -> str:
        """存储智慧能源数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO energy_data (
                meter_id, location_latitude, location_longitude,
                consumption_type, current_consumption, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (
            energy_data.get("meter_id"),
            energy_data.get("location", {}).get("latitude"),
            energy_data.get("location", {}).get("longitude"),
            energy_data.get("consumption_type"),
            energy_data.get("current_consumption"),
            energy_data.get("timestamp")
        ))
        result = cursor.fetchone()
        self.conn.commit()
        cursor.close()
        return str(result[0]) if result else None

    def query_traffic_by_location(self, latitude: float, longitude: float,
                                  start_time: Optional[datetime] = None,
                                  end_time: Optional[datetime] = None) -> List[dict]:
        """根据位置查询交通数据"""
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM traffic_data
            WHERE location_latitude = %s AND location_longitude = %s
        """
        params = [latitude, longitude]

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
```

---

### 5.2 Smart City数据分析查询

**查询示例**：

```python
# 查询城市数据统计
def query_city_statistics(storage: SmartCityStorage, start_date: datetime, end_date: datetime):
    """查询城市数据统计"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        SELECT
            data_category,
            COUNT(*) as data_count,
            AVG(sensor_value) as avg_value
        FROM sensor_data
        WHERE timestamp BETWEEN %s AND %s
        GROUP BY data_category
        ORDER BY data_count DESC
    """, (start_date, end_date))
    return cursor.fetchall()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
