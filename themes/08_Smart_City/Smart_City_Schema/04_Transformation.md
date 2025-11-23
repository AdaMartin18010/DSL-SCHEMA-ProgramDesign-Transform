# Smart City Schema转换体系

## 📑 目录

- [Smart City Schema转换体系](#smart-city-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 传感器数据转换](#2-传感器数据转换)
  - [3. 城市数据聚合](#3-城市数据聚合)
    - [3.1 IoT数据聚合器](#31-iot数据聚合器)
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

### 3.1 IoT数据聚合器

**完整的IoT数据聚合实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class IoTDataAggregator:
    """IoT数据聚合器 - 完整实现"""

    def __init__(self):
        self.aggregation_window = timedelta(minutes=5)  # 默认5分钟聚合窗口

    def aggregate_by_time(self, data_list: List[Dict], window_minutes: int = 5) -> List[Dict]:
        """按时间窗口聚合数据"""
        if not data_list:
            return []

        # 按时间排序
        sorted_data = sorted(data_list, key=lambda x: x.get("timestamp", datetime.min))

        # 按时间窗口分组
        window = timedelta(minutes=window_minutes)
        aggregated_results = []
        current_window_start = None
        current_window_data = []

        for data_point in sorted_data:
            timestamp = data_point.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            if current_window_start is None:
                current_window_start = timestamp

            # 检查是否在当前窗口内
            if timestamp < current_window_start + window:
                current_window_data.append(data_point)
            else:
                # 聚合当前窗口的数据
                if current_window_data:
                    aggregated = self._aggregate_window(current_window_data)
                    aggregated_results.append(aggregated)

                # 开始新窗口
                current_window_start = timestamp
                current_window_data = [data_point]

        # 处理最后一个窗口
        if current_window_data:
            aggregated = self._aggregate_window(current_window_data)
            aggregated_results.append(aggregated)

        return aggregated_results

    def aggregate_by_location(self, data_list: List[Dict], grid_size: float = 0.01) -> Dict:
        """按地理位置聚合数据"""
        if not data_list:
            return {}

        # 按网格分组
        grid_groups = defaultdict(list)

        for data_point in data_list:
            location = data_point.get("location", {})
            lat = location.get("latitude")
            lon = location.get("longitude")

            if lat is not None and lon is not None:
                # 计算网格坐标
                grid_lat = round(lat / grid_size) * grid_size
                grid_lon = round(lon / grid_size) * grid_size
                grid_key = f"{grid_lat},{grid_lon}"
                grid_groups[grid_key].append(data_point)

        # 聚合每个网格的数据
        aggregated_grids = {}
        for grid_key, grid_data in grid_groups.items():
            aggregated = self._aggregate_window(grid_data)
            aggregated["grid_location"] = grid_key
            aggregated_grids[grid_key] = aggregated

        return aggregated_grids

    def aggregate_by_device_type(self, data_list: List[Dict]) -> Dict:
        """按设备类型聚合数据"""
        if not data_list:
            return {}

        # 按设备类型分组
        type_groups = defaultdict(list)

        for data_point in data_list:
            device_type = data_point.get("device_type") or data_point.get("sensor_type", "unknown")
            type_groups[device_type].append(data_point)

        # 聚合每种类型的数据
        aggregated_types = {}
        for device_type, type_data in type_groups.items():
            aggregated = self._aggregate_window(type_data)
            aggregated["device_type"] = device_type
            aggregated_types[device_type] = aggregated

        return aggregated_types

    def aggregate_traffic_data(self, traffic_data_list: List[Dict]) -> Dict:
        """聚合交通数据"""
        if not traffic_data_list:
            return {}

        aggregated = {
            "total_vehicles": sum(d.get("vehicle_count", 0) for d in traffic_data_list),
            "average_speed": statistics.mean([d.get("average_speed", 0) for d in traffic_data_list if d.get("average_speed")]),
            "congestion_levels": {},
            "peak_hour": None,
            "data_points": len(traffic_data_list)
        }

        # 统计拥堵等级分布
        congestion_levels = [d.get("congestion_level") for d in traffic_data_list if d.get("congestion_level")]
        for level in set(congestion_levels):
            aggregated["congestion_levels"][level] = congestion_levels.count(level)

        # 找出高峰时段
        if traffic_data_list:
            hourly_counts = defaultdict(int)
            for data_point in traffic_data_list:
                timestamp = data_point.get("timestamp")
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = timestamp.hour
                hourly_counts[hour] += data_point.get("vehicle_count", 0)

            if hourly_counts:
                peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0]
                aggregated["peak_hour"] = peak_hour

        return aggregated

    def aggregate_energy_data(self, energy_data_list: List[Dict]) -> Dict:
        """聚合能源数据"""
        if not energy_data_list:
            return {}

        consumptions = [d.get("current_consumption", 0) for d in energy_data_list if d.get("current_consumption")]

        aggregated = {
            "total_consumption": sum(consumptions),
            "average_consumption": statistics.mean(consumptions) if consumptions else 0,
            "peak_consumption": max(consumptions) if consumptions else 0,
            "min_consumption": min(consumptions) if consumptions else 0,
            "consumption_by_type": {},
            "data_points": len(energy_data_list)
        }

        # 按消费类型分组
        type_groups = defaultdict(list)
        for data_point in energy_data_list:
            consumption_type = data_point.get("consumption_type", "unknown")
            type_groups[consumption_type].append(data_point.get("current_consumption", 0))

        for consumption_type, values in type_groups.items():
            aggregated["consumption_by_type"][consumption_type] = {
                "total": sum(values),
                "average": statistics.mean(values),
                "count": len(values)
            }

        return aggregated

    def aggregate_environment_data(self, env_data_list: List[Dict]) -> Dict:
        """聚合环境数据"""
        if not env_data_list:
            return {}

        # 提取各种环境指标
        aqi_values = [d.get("aqi") for d in env_data_list if d.get("aqi")]
        temperature_values = [d.get("temperature") for d in env_data_list if d.get("temperature")]
        humidity_values = [d.get("humidity") for d in env_data_list if d.get("humidity")]
        pm25_values = [d.get("pm25") for d in env_data_list if d.get("pm25")]
        pm10_values = [d.get("pm10") for d in env_data_list if d.get("pm10")]

        aggregated = {
            "aqi": {
                "average": statistics.mean(aqi_values) if aqi_values else None,
                "max": max(aqi_values) if aqi_values else None,
                "min": min(aqi_values) if aqi_values else None,
                "level": self._get_aqi_level(statistics.mean(aqi_values)) if aqi_values else None
            },
            "temperature": {
                "average": statistics.mean(temperature_values) if temperature_values else None,
                "max": max(temperature_values) if temperature_values else None,
                "min": min(temperature_values) if temperature_values else None
            },
            "humidity": {
                "average": statistics.mean(humidity_values) if humidity_values else None,
                "max": max(humidity_values) if humidity_values else None,
                "min": min(humidity_values) if humidity_values else None
            },
            "pm25": {
                "average": statistics.mean(pm25_values) if pm25_values else None,
                "max": max(pm25_values) if pm25_values else None
            },
            "pm10": {
                "average": statistics.mean(pm10_values) if pm10_values else None,
                "max": max(pm10_values) if pm10_values else None
            },
            "data_points": len(env_data_list)
        }

        return aggregated

    def clean_data(self, data_list: List[Dict]) -> List[Dict]:
        """数据清洗"""
        cleaned_data = []

        for data_point in data_list:
            # 移除异常值
            if self._is_valid_data_point(data_point):
                cleaned_data.append(data_point)
            else:
                logger.warning(f"Invalid data point removed: {data_point}")

        return cleaned_data

    def _aggregate_window(self, window_data: List[Dict]) -> Dict:
        """聚合单个窗口的数据"""
        if not window_data:
            return {}

        # 提取所有数值字段
        numeric_fields = defaultdict(list)
        for data_point in window_data:
            for key, value in data_point.items():
                if isinstance(value, (int, float)) and key != "timestamp":
                    numeric_fields[key].append(value)

        aggregated = {
            "timestamp": max(d.get("timestamp", datetime.min) for d in window_data),
            "data_count": len(window_data),
            "aggregated_values": {}
        }

        # 计算统计值
        for field, values in numeric_fields.items():
            if values:
                aggregated["aggregated_values"][field] = {
                    "sum": sum(values),
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "median": statistics.median(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0
                }

        # 保留第一个数据点的非数值字段
        if window_data:
            first_point = window_data[0]
            for key, value in first_point.items():
                if key not in aggregated and not isinstance(value, (int, float)):
                    aggregated[key] = value

        return aggregated

    def _is_valid_data_point(self, data_point: Dict) -> bool:
        """验证数据点是否有效"""
        # 检查必需字段
        if "timestamp" not in data_point:
            return False

        # 检查数值是否在合理范围内
        for key, value in data_point.items():
            if isinstance(value, (int, float)):
                # 检查是否为NaN或Infinity
                if value != value or value == float('inf') or value == float('-inf'):
                    return False

        return True

    def _get_aqi_level(self, aqi: float) -> str:
        """获取AQI等级"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
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

import psycopg2

class SmartCityStorage:
    """Smart City数据PostgreSQL存储类 - 增强错误处理"""

    def __init__(self, connection_string: str):
        # 输入验证
        if not connection_string:
            raise ValueError("Connection string cannot be empty")

        if not isinstance(connection_string, str):
            raise TypeError(f"Connection string must be a string, got {type(connection_string)}")

        try:
            self.conn = psycopg2.connect(connection_string)
            self.create_tables()
            logger.info("SmartCityStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing SmartCityStorage: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize SmartCityStorage: {e}") from e

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
        """存储智慧交通数据 - 增强错误处理"""
        # 输入验证
        if not isinstance(traffic_data, dict):
            raise TypeError(f"Traffic data must be a dictionary, got {type(traffic_data)}")

        if not traffic_data:
            raise ValueError("Traffic data cannot be empty")

        location = traffic_data.get("location", {})
        if not isinstance(location, dict):
            raise TypeError(f"Location must be a dictionary, got {type(location)}")

        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if latitude is None:
            raise ValueError("Latitude is required")

        if not isinstance(latitude, (int, float)):
            raise TypeError(f"Latitude must be numeric, got {type(latitude)}")

        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude out of range: {latitude} (must be -90 to 90)")

        if longitude is None:
            raise ValueError("Longitude is required")

        if not isinstance(longitude, (int, float)):
            raise TypeError(f"Longitude must be numeric, got {type(longitude)}")

        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude out of range: {longitude} (must be -180 to 180)")

        flow_data = traffic_data.get("flow_data", {})
        timestamp = flow_data.get("timestamp")
        if not timestamp:
            raise ValueError("Timestamp is required")

        if not isinstance(timestamp, datetime):
            raise TypeError(f"Timestamp must be a datetime, got {type(timestamp)}")

        vehicle_count = flow_data.get("vehicle_count", 0)
        if vehicle_count is not None and vehicle_count < 0:
            raise ValueError(f"Vehicle count cannot be negative: {vehicle_count}")

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO traffic_data (
                    location_latitude, location_longitude,
                    vehicle_count, average_speed, congestion_level, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                latitude,
                longitude,
                vehicle_count,
                flow_data.get("average_speed"),
                flow_data.get("congestion_level"),
                timestamp
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store traffic data")

            traffic_id = result[0]
            self.conn.commit()
            cursor.close()
            logger.info(f"Stored traffic data at {latitude}, {longitude}")
            return str(traffic_id)

        except psycopg2.Error as e:
            logger.error(f"Database error storing traffic data: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing traffic data: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store traffic data: {e}") from e

    def store_energy_data(self, energy_data: dict) -> str:
        """存储智慧能源数据 - 增强错误处理"""
        # 输入验证
        if not isinstance(energy_data, dict):
            raise TypeError(f"Energy data must be a dictionary, got {type(energy_data)}")

        if not energy_data:
            raise ValueError("Energy data cannot be empty")

        meter_id = energy_data.get("meter_id")
        if not meter_id:
            raise ValueError("Meter ID is required")

        if not isinstance(meter_id, str):
            raise TypeError(f"Meter ID must be a string, got {type(meter_id)}")

        if len(meter_id) > 255:
            raise ValueError(f"Meter ID too long: {len(meter_id)} (max 255)")

        location = energy_data.get("location", {})
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if latitude is not None:
            if not isinstance(latitude, (int, float)):
                raise TypeError(f"Latitude must be numeric, got {type(latitude)}")
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Latitude out of range: {latitude}")

        if longitude is not None:
            if not isinstance(longitude, (int, float)):
                raise TypeError(f"Longitude must be numeric, got {type(longitude)}")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Longitude out of range: {longitude}")

        timestamp = energy_data.get("timestamp")
        if not timestamp:
            raise ValueError("Timestamp is required")

        if not isinstance(timestamp, datetime):
            raise TypeError(f"Timestamp must be a datetime, got {type(timestamp)}")

        current_consumption = energy_data.get("current_consumption")
        if current_consumption is not None and current_consumption < 0:
            raise ValueError(f"Current consumption cannot be negative: {current_consumption}")

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO energy_data (
                    meter_id, location_latitude, location_longitude,
                    consumption_type, current_consumption, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                meter_id,
                latitude,
                longitude,
                energy_data.get("consumption_type"),
                current_consumption,
                timestamp
            ))

            result = cursor.fetchone()
            self.conn.commit()
            cursor.close()

            if not result:
                logger.warning(f"No data stored for meter {meter_id} (possible conflict)")
                return None

            logger.info(f"Stored energy data for meter {meter_id}")
            return str(result[0])

        except psycopg2.Error as e:
            logger.error(f"Database error storing energy data: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing energy data: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store energy data: {e}") from e

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

**完整的城市数据分析类**：

```python
class SmartCityDataAnalyzer:
    """Smart City数据分析器 - 完整实现"""

    def __init__(self, storage):
        self.storage = storage

    def analyze_traffic_patterns(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析交通模式 - 增强错误处理"""
        # 输入验证
        if not isinstance(start_date, datetime):
            raise TypeError(f"Start date must be a datetime, got {type(start_date)}")

        if not isinstance(end_date, datetime):
            raise TypeError(f"End date must be a datetime, got {type(end_date)}")

        if start_date > end_date:
            raise ValueError(f"Start date ({start_date}) cannot be after end date ({end_date})")

        cursor = self.storage.conn.cursor()

        # 按小时统计交通流量
        cursor.execute("""
            SELECT
                EXTRACT(HOUR FROM timestamp) as hour,
                AVG(vehicle_count) as avg_vehicles,
                AVG(average_speed) as avg_speed,
                COUNT(*) as data_points
            FROM traffic_data
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY EXTRACT(HOUR FROM timestamp)
            ORDER BY hour
        """, (start_date, end_date))

        hourly_stats = []
        for row in cursor.fetchall():
            hourly_stats.append({
                "hour": int(row[0]),
                "average_vehicles": float(row[1]) if row[1] else 0,
                "average_speed": float(row[2]) if row[2] else 0,
                "data_points": int(row[3])
            })

        # 找出高峰时段
        peak_hours = sorted(hourly_stats, key=lambda x: x["average_vehicles"], reverse=True)[:3]

        # 拥堵区域分析
        cursor.execute("""
            SELECT
                location_latitude,
                location_longitude,
                AVG(vehicle_count) as avg_vehicles,
                AVG(CASE WHEN congestion_level = 'High' THEN 1 ELSE 0 END) as congestion_rate
            FROM traffic_data
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY location_latitude, location_longitude
            HAVING AVG(vehicle_count) > 50
            ORDER BY avg_vehicles DESC
            LIMIT 10
        """, (start_date, end_date))

        congestion_areas = []
        for row in cursor.fetchall():
            congestion_areas.append({
                "latitude": float(row[0]),
                "longitude": float(row[1]),
                "average_vehicles": float(row[2]),
                "congestion_rate": float(row[3])
            })

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "hourly_patterns": hourly_stats,
            "peak_hours": [h["hour"] for h in peak_hours],
            "congestion_areas": congestion_areas,
            "summary": {
                "total_data_points": sum(h["data_points"] for h in hourly_stats),
                "peak_hour": peak_hours[0]["hour"] if peak_hours else None,
                "most_congested_area": congestion_areas[0] if congestion_areas else None
            }
        }

    def analyze_energy_consumption(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析能源消耗"""
        cursor = self.storage.conn.cursor()

        # 按消费类型统计
        cursor.execute("""
            SELECT
                consumption_type,
                SUM(current_consumption) as total_consumption,
                AVG(current_consumption) as avg_consumption,
                MAX(current_consumption) as peak_consumption,
                COUNT(*) as data_points
            FROM energy_data
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY consumption_type
        """, (start_date, end_date))

        consumption_by_type = {}
        total_consumption = 0

        for row in cursor.fetchall():
            consumption_by_type[row[0]] = {
                "total": float(row[1]),
                "average": float(row[2]),
                "peak": float(row[3]),
                "data_points": int(row[4])
            }
            total_consumption += float(row[1])

        # 按小时统计能源消耗
        cursor.execute("""
            SELECT
                EXTRACT(HOUR FROM timestamp) as hour,
                AVG(current_consumption) as avg_consumption,
                MAX(current_consumption) as peak_consumption
            FROM energy_data
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY EXTRACT(HOUR FROM timestamp)
            ORDER BY hour
        """, (start_date, end_date))

        hourly_consumption = []
        for row in cursor.fetchall():
            hourly_consumption.append({
                "hour": int(row[0]),
                "average_consumption": float(row[1]),
                "peak_consumption": float(row[2])
            })

        # 找出峰值时段
        peak_hours = sorted(hourly_consumption, key=lambda x: x["peak_consumption"], reverse=True)[:3]

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_consumption": total_consumption,
            "consumption_by_type": consumption_by_type,
            "hourly_patterns": hourly_consumption,
            "peak_hours": [h["hour"] for h in peak_hours],
            "summary": {
                "largest_consumer_type": max(consumption_by_type.items(), key=lambda x: x[1]["total"])[0] if consumption_by_type else None,
                "peak_hour": peak_hours[0]["hour"] if peak_hours else None
            }
        }

    def analyze_environment_quality(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析环境质量"""
        cursor = self.storage.conn.cursor()

        # 环境质量统计
        cursor.execute("""
            SELECT
                AVG(aqi) as avg_aqi,
                MAX(aqi) as max_aqi,
                MIN(aqi) as min_aqi,
                AVG(temperature) as avg_temperature,
                AVG(humidity) as avg_humidity,
                AVG(pm25) as avg_pm25,
                AVG(pm10) as avg_pm10,
                COUNT(*) as data_points
            FROM environment_data
            WHERE timestamp >= %s AND timestamp <= %s
        """, (start_date, end_date))

        row = cursor.fetchone()
        if not row or not row[0]:
            return {"error": "No data available"}

        # 按区域统计
        cursor.execute("""
            SELECT
                station_id,
                AVG(aqi) as avg_aqi,
                MAX(aqi) as max_aqi,
                COUNT(*) as data_points
            FROM environment_data
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY station_id
            ORDER BY avg_aqi DESC
        """, (start_date, end_date))

        station_stats = []
        for stat_row in cursor.fetchall():
            station_stats.append({
                "station_id": stat_row[0],
                "average_aqi": float(stat_row[1]),
                "max_aqi": float(stat_row[2]),
                "data_points": int(stat_row[3])
            })

        # 找出污染最严重的区域
        worst_stations = sorted(station_stats, key=lambda x: x["average_aqi"], reverse=True)[:5]

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "overall_statistics": {
                "average_aqi": float(row[0]),
                "max_aqi": float(row[1]),
                "min_aqi": float(row[2]),
                "average_temperature": float(row[3]) if row[3] else None,
                "average_humidity": float(row[4]) if row[4] else None,
                "average_pm25": float(row[5]) if row[5] else None,
                "average_pm10": float(row[6]) if row[6] else None,
                "data_points": int(row[7])
            },
            "station_statistics": station_stats,
            "worst_air_quality_stations": worst_stations,
            "summary": {
                "overall_aqi_level": self._get_aqi_level(float(row[0])),
                "worst_station": worst_stations[0] if worst_stations else None
            }
        }

    def generate_city_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """生成城市综合报告"""
        traffic_analysis = self.analyze_traffic_patterns(start_date, end_date)
        energy_analysis = self.analyze_energy_consumption(start_date, end_date)
        environment_analysis = self.analyze_environment_quality(start_date, end_date)

        # 计算城市健康指数
        health_score = self._calculate_city_health_score(
            traffic_analysis,
            energy_analysis,
            environment_analysis
        )

        return {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "traffic_analysis": traffic_analysis,
            "energy_analysis": energy_analysis,
            "environment_analysis": environment_analysis,
            "city_health_score": health_score,
            "recommendations": self._generate_recommendations(
                traffic_analysis,
                energy_analysis,
                environment_analysis
            )
        }

    def _calculate_city_health_score(self, traffic: Dict, energy: Dict, environment: Dict) -> float:
        """计算城市健康指数（0-100）"""
        score = 100.0

        # 交通评分（30%）
        if traffic.get("congestion_areas"):
            congestion_rate = len(traffic["congestion_areas"]) / 10.0  # 假设10个区域为基准
            score -= congestion_rate * 10

        # 能源评分（30%）
        if energy.get("total_consumption"):
            # 假设基准消耗为1000，超过则扣分
            consumption_rate = min(energy["total_consumption"] / 1000.0, 2.0)
            score -= (consumption_rate - 1) * 15

        # 环境评分（40%）
        if environment.get("overall_statistics"):
            aqi = environment["overall_statistics"].get("average_aqi", 0)
            if aqi > 100:
                score -= (aqi - 100) / 2

        return max(0, min(100, score))

    def _generate_recommendations(self, traffic: Dict, energy: Dict, environment: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 交通建议
        if traffic.get("congestion_areas"):
            if len(traffic["congestion_areas"]) > 5:
                recommendations.append("建议优化交通信号灯时序，减少拥堵区域")

        # 能源建议
        if energy.get("peak_hours"):
            peak_hour = energy["peak_hours"][0]
            if peak_hour >= 18 and peak_hour <= 20:
                recommendations.append("建议实施分时电价，鼓励错峰用电")

        # 环境建议
        if environment.get("overall_statistics"):
            aqi = environment["overall_statistics"].get("average_aqi", 0)
            if aqi > 100:
                recommendations.append("建议加强空气质量监测，采取减排措施")

        return recommendations

    def _get_aqi_level(self, aqi: float) -> str:
        """获取AQI等级"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
```

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
