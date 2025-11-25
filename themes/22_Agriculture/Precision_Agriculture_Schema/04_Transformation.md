# 精准农业Schema转换体系

## 📑 目录

- [精准农业Schema转换体系](#精准农业schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ISO 11783到AgGateway转换实现](#2-iso-11783到aggateway转换实现)
    - [2.1 ISO 11783 TCXML解析和AgGateway转换](#21-iso-11783-tcxml解析和aggateway转换)
  - [3. OGC SensorThings到ISO 11783转换](#3-ogc-sensorthings到iso-11783转换)
  - [4. 精准农业数据管理系统](#4-精准农业数据管理系统)
    - [4.1 农田信息管理](#41-农田信息管理)
  - [5. 转换工具](#5-转换工具)
    - [5.1 ISO 11783解析器集成](#51-iso-11783解析器集成)
    - [5.2 AgGateway转换器集成](#52-aggateway转换器集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 ISO 11783到AgGateway转换验证](#61-iso-11783到aggateway转换验证)
  - [7. 精准农业数据存储与分析](#7-精准农业数据存储与分析)
    - [7.1 PostgreSQL精准农业数据存储](#71-postgresql精准农业数据存储)
    - [7.2 精准农业数据分析查询](#72-精准农业数据分析查询)

---

## 1. 转换体系概述

精准农业Schema转换体系支持ISO 11783 TCXML、AgGateway ADAPT、
OGC SensorThings、数据库存储之间的转换。

### 1.1 转换目标

1. **ISO 11783到AgGateway转换**：ISO 11783 TCXML到AgGateway ADAPT
2. **OGC SensorThings到ISO 11783转换**：OGC SensorThings到ISO 11783 TCXML
3. **数据到数据库转换**：精准农业数据到PostgreSQL存储

---

## 2. ISO 11783到AgGateway转换实现

### 2.1 ISO 11783 TCXML解析和AgGateway转换

**完整的ISO 11783到AgGateway转换实现**：

```python
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ISO11783Parser:
    """ISO 11783 TCXML解析器"""

    def __init__(self):
        self.namespaces = {
            'tc': 'http://www.iso.org/iso/11783/-10/tsc',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

    def parse_tcxml(self, tcxml_content: str) -> Dict:
        """解析ISO 11783 TCXML文档"""
        try:
            root = ET.fromstring(tcxml_content)
            tcxml_data = {
                "version": root.get("Version", ""),
                "management_data": {},
                "tasks": []
            }

            # 解析管理数据
            management_data = root.find('.//tc:ManagementData', self.namespaces)
            if management_data is not None:
                tcxml_data["management_data"] = self._parse_management_data(management_data)

            # 解析任务
            tasks = root.findall('.//tc:Task', self.namespaces)
            for task in tasks:
                task_data = self._parse_task(task)
                if task_data:
                    tcxml_data["tasks"].append(task_data)

            return tcxml_data
        except ET.ParseError as e:
            logger.error(f"Failed to parse TCXML: {e}")
            raise ValueError(f"Invalid TCXML format: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error parsing TCXML: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse TCXML: {e}") from e

    def _parse_management_data(self, management_data: ET.Element) -> Dict:
        """解析管理数据"""
        data = {}

        # 解析农场信息
        farm = management_data.find('.//tc:Farm', self.namespaces)
        if farm is not None:
            data["farm"] = {
                "id": farm.get("Id", ""),
                "name": farm.findtext('.//tc:Name', '', self.namespaces)
            }

        # 解析农田信息
        fields = management_data.findall('.//tc:Field', self.namespaces)
        data["fields"] = []
        for field in fields:
            field_data = {
                "id": field.get("Id", ""),
                "name": field.findtext('.//tc:Name', '', self.namespaces),
                "area": float(field.findtext('.//tc:Area', '0', self.namespaces))
            }
            data["fields"].append(field_data)

        return data

    def _parse_task(self, task: ET.Element) -> Optional[Dict]:
        """解析任务"""
        try:
            task_data = {
                "task_id": task.get("Id", ""),
                "task_status": task.get("Status", ""),
                "operation": {},
                "work_items": []
            }

            # 解析操作信息
            operation = task.find('.//tc:Operation', self.namespaces)
            if operation is not None:
                task_data["operation"] = {
                    "operation_type": operation.get("Type", ""),
                    "start_time": operation.findtext('.//tc:StartTime', '', self.namespaces),
                    "end_time": operation.findtext('.//tc:EndTime', '', self.namespaces)
                }

            # 解析工作项
            work_items = task.findall('.//tc:WorkItem', self.namespaces)
            for work_item in work_items:
                work_item_data = self._parse_work_item(work_item)
                if work_item_data:
                    task_data["work_items"].append(work_item_data)

            return task_data
        except Exception as e:
            logger.error(f"Failed to parse task: {e}")
            return None

    def _parse_work_item(self, work_item: ET.Element) -> Optional[Dict]:
        """解析工作项"""
        try:
            work_item_data = {
                "work_item_id": work_item.get("Id", ""),
                "product": {},
                "application_rate": {}
            }

            # 解析产品信息
            product = work_item.find('.//tc:Product', self.namespaces)
            if product is not None:
                work_item_data["product"] = {
                    "product_id": product.get("Id", ""),
                    "product_name": product.findtext('.//tc:Name', '', self.namespaces)
                }

            # 解析施用量
            application_rate = work_item.find('.//tc:ApplicationRate', self.namespaces)
            if application_rate is not None:
                work_item_data["application_rate"] = {
                    "value": float(application_rate.findtext('.//tc:Value', '0', self.namespaces)),
                    "unit": application_rate.findtext('.//tc:Unit', '', self.namespaces)
                }

            return work_item_data
        except Exception as e:
            logger.error(f"Failed to parse work item: {e}")
            return None


class AgGatewayConverter:
    """AgGateway ADAPT转换器"""

    def __init__(self):
        self.iso_parser = ISO11783Parser()

    def convert_iso11783_to_adapt(self, tcxml_content: str) -> Dict:
        """将ISO 11783 TCXML转换为AgGateway ADAPT格式"""
        try:
            # 解析TCXML
            tcxml_data = self.iso_parser.parse_tcxml(tcxml_content)

            # 转换为ADAPT格式
            adapt_data = {
                "Version": "1.0",
                "DocumentId": f"ADAPT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "WorkOrders": []
            }

            # 转换管理数据
            if "management_data" in tcxml_data:
                adapt_data["Farm"] = self._convert_farm(tcxml_data["management_data"])

            # 转换任务
            for task in tcxml_data.get("tasks", []):
                work_order = self._convert_task_to_work_order(task)
                if work_order:
                    adapt_data["WorkOrders"].append(work_order)

            return adapt_data
        except Exception as e:
            logger.error(f"Failed to convert ISO 11783 to ADAPT: {e}", exc_info=True)
            raise RuntimeError(f"Conversion failed: {e}") from e

    def _convert_farm(self, management_data: Dict) -> Dict:
        """转换农场信息"""
        farm_data = management_data.get("farm", {})
        return {
            "Id": farm_data.get("id", ""),
            "Name": farm_data.get("name", ""),
            "Fields": []
        }

    def _convert_task_to_work_order(self, task: Dict) -> Optional[Dict]:
        """将任务转换为工作订单"""
        try:
            operation = task.get("operation", {})
            work_order = {
                "Id": task.get("task_id", ""),
                "Status": self._convert_status(task.get("task_status", "")),
                "StartTime": operation.get("start_time", ""),
                "EndTime": operation.get("end_time", ""),
                "WorkItems": []
            }

            # 转换工作项
            for work_item in task.get("work_items", []):
                adapt_work_item = self._convert_work_item(work_item)
                if adapt_work_item:
                    work_order["WorkItems"].append(adapt_work_item)

            return work_order
        except Exception as e:
            logger.error(f"Failed to convert task to work order: {e}")
            return None

    def _convert_work_item(self, work_item: Dict) -> Optional[Dict]:
        """转换工作项"""
        try:
            product = work_item.get("product", {})
            application_rate = work_item.get("application_rate", {})

            return {
                "Id": work_item.get("work_item_id", ""),
                "Product": {
                    "Id": product.get("product_id", ""),
                    "Name": product.get("product_name", "")
                },
                "ApplicationRate": {
                    "Value": application_rate.get("value", 0.0),
                    "Unit": application_rate.get("unit", "kg/ha")
                }
            }
        except Exception as e:
            logger.error(f"Failed to convert work item: {e}")
            return None

    def _convert_status(self, status: str) -> str:
        """转换状态"""
        status_map = {
            "planned": "Planned",
            "in_progress": "InProgress",
            "completed": "Completed",
            "cancelled": "Cancelled"
        }
        return status_map.get(status.lower(), "Unknown")


class PrecisionAgricultureStorage:
    """精准农业数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 农田信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS fields (
                field_id VARCHAR(50) PRIMARY KEY,
                field_name VARCHAR(200) NOT NULL,
                field_area DECIMAL(10, 2) NOT NULL,
                field_type VARCHAR(50),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                altitude DECIMAL(8, 2),
                soil_type VARCHAR(100),
                ph_value DECIMAL(4, 2),
                organic_matter DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 传感器数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(50) NOT NULL,
                field_id VARCHAR(50) REFERENCES fields(field_id),
                timestamp TIMESTAMP NOT NULL,
                sensor_type VARCHAR(50) NOT NULL,
                soil_moisture DECIMAL(5, 2),
                soil_temperature DECIMAL(5, 2),
                soil_ph DECIMAL(4, 2),
                air_temperature DECIMAL(5, 2),
                air_humidity DECIMAL(5, 2),
                rainfall DECIMAL(6, 2),
                wind_speed DECIMAL(5, 2),
                solar_radiation DECIMAL(8, 2),
                ndvi DECIMAL(4, 3),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 农机作业表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS machinery_operations (
                operation_id VARCHAR(50) PRIMARY KEY,
                field_id VARCHAR(50) REFERENCES fields(field_id),
                machinery_id VARCHAR(50) NOT NULL,
                operation_type VARCHAR(50) NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                operation_speed DECIMAL(5, 2),
                operation_depth DECIMAL(5, 2),
                operation_width DECIMAL(5, 2),
                application_rate DECIMAL(8, 2),
                seed_rate DECIMAL(8, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_data_field_time ON sensor_data(field_id, timestamp)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_machinery_operations_field_time ON machinery_operations(field_id, start_time)")

        self.conn.commit()

    def store_field(self, field_id: str, field_name: str, field_area: float,
                   field_type: str = None, latitude: float = None,
                   longitude: float = None, altitude: float = None,
                   soil_type: str = None, ph_value: float = None,
                   organic_matter: float = None) -> Optional[int]:
        """存储农田信息"""
        # 输入验证
        if not field_id:
            raise ValueError("Field ID cannot be empty")
        if not isinstance(field_id, str):
            raise TypeError(f"Field ID must be a string, got {type(field_id)}")
        if len(field_id) > 50:
            raise ValueError(f"Field ID too long: {len(field_id)} (max 50)")

        if not field_name:
            raise ValueError("Field name cannot be empty")
        if not isinstance(field_name, str):
            raise TypeError(f"Field name must be a string, got {type(field_name)}")
        if len(field_name) > 200:
            raise ValueError(f"Field name too long: {len(field_name)} (max 200)")

        if field_area is None or field_area < 0:
            raise ValueError(f"Field area must be non-negative, got {field_area}")

        try:
            self.cur.execute("""
                INSERT INTO fields (
                    field_id, field_name, field_area, field_type,
                    latitude, longitude, altitude, soil_type, ph_value, organic_matter
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (field_id) DO UPDATE SET
                    field_name = EXCLUDED.field_name,
                    field_area = EXCLUDED.field_area,
                    field_type = EXCLUDED.field_type,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    altitude = EXCLUDED.altitude,
                    soil_type = EXCLUDED.soil_type,
                    ph_value = EXCLUDED.ph_value,
                    organic_matter = EXCLUDED.organic_matter,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING field_id
            """, (field_id, field_name, field_area, field_type,
                  latitude, longitude, altitude, soil_type, ph_value, organic_matter))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored field: {field_id}")
            return result[0] if result else None
        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing field: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate field ID or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing field: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing field: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Unexpected error: {e}") from e

    def store_sensor_data(self, sensor_id: str, field_id: str, timestamp: datetime,
                         sensor_type: str, **sensor_values) -> Optional[int]:
        """存储传感器数据"""
        # 输入验证
        if not sensor_id:
            raise ValueError("Sensor ID cannot be empty")
        if not field_id:
            raise ValueError("Field ID cannot be empty")
        if not timestamp:
            raise ValueError("Timestamp cannot be empty")
        if not sensor_type:
            raise ValueError("Sensor type cannot be empty")

        try:
            self.cur.execute("""
                INSERT INTO sensor_data (
                    sensor_id, field_id, timestamp, sensor_type,
                    soil_moisture, soil_temperature, soil_ph,
                    air_temperature, air_humidity, rainfall,
                    wind_speed, solar_radiation, ndvi
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                sensor_id, field_id, timestamp, sensor_type,
                sensor_values.get('soil_moisture'),
                sensor_values.get('soil_temperature'),
                sensor_values.get('soil_ph'),
                sensor_values.get('air_temperature'),
                sensor_values.get('air_humidity'),
                sensor_values.get('rainfall'),
                sensor_values.get('wind_speed'),
                sensor_values.get('solar_radiation'),
                sensor_values.get('ndvi')
            ))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored sensor data: {sensor_id} at {timestamp}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing sensor data: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing sensor data: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Unexpected error: {e}") from e

    def store_machinery_operation(self, operation_id: str, field_id: str,
                                 machinery_id: str, operation_type: str,
                                 start_time: datetime, end_time: datetime = None,
                                 operation_speed: float = None,
                                 operation_depth: float = None,
                                 operation_width: float = None,
                                 application_rate: float = None,
                                 seed_rate: float = None) -> Optional[int]:
        """存储农机作业数据"""
        # 输入验证
        if not operation_id:
            raise ValueError("Operation ID cannot be empty")
        if not field_id:
            raise ValueError("Field ID cannot be empty")
        if not machinery_id:
            raise ValueError("Machinery ID cannot be empty")
        if not operation_type:
            raise ValueError("Operation type cannot be empty")
        if not start_time:
            raise ValueError("Start time cannot be empty")

        try:
            self.cur.execute("""
                INSERT INTO machinery_operations (
                    operation_id, field_id, machinery_id, operation_type,
                    start_time, end_time, operation_speed, operation_depth,
                    operation_width, application_rate, seed_rate
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (operation_id) DO UPDATE SET
                    field_id = EXCLUDED.field_id,
                    machinery_id = EXCLUDED.machinery_id,
                    operation_type = EXCLUDED.operation_type,
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    operation_speed = EXCLUDED.operation_speed,
                    operation_depth = EXCLUDED.operation_depth,
                    operation_width = EXCLUDED.operation_width,
                    application_rate = EXCLUDED.application_rate,
                    seed_rate = EXCLUDED.seed_rate
                RETURNING operation_id
            """, (operation_id, field_id, machinery_id, operation_type,
                  start_time, end_time, operation_speed, operation_depth,
                  operation_width, application_rate, seed_rate))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored machinery operation: {operation_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing machinery operation: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing machinery operation: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Unexpected error: {e}") from e

    def get_field_sensor_data(self, field_id: str, start_time: datetime = None,
                              end_time: datetime = None) -> List[Dict]:
        """查询农田传感器数据"""
        try:
            query = """
                SELECT sensor_id, timestamp, sensor_type,
                       soil_moisture, soil_temperature, soil_ph,
                       air_temperature, air_humidity, rainfall,
                       wind_speed, solar_radiation, ndvi
                FROM sensor_data
                WHERE field_id = %s
            """
            params = [field_id]

            if start_time:
                query += " AND timestamp >= %s"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= %s"
                params.append(end_time)

            query += " ORDER BY timestamp DESC"

            self.cur.execute(query, params)
            columns = [desc[0] for desc in self.cur.description]
            results = []
            for row in self.cur.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except psycopg2.Error as e:
            logger.error(f"Database error querying sensor data: {e}")
            raise RuntimeError(f"Database query failed: {e}") from e

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
```

---

## 3. OGC SensorThings到ISO 11783转换

（转换实现代码...）

---

## 4. 精准农业数据管理系统

### 4.1 农田信息管理

（管理实现代码...）

---

## 5. 转换工具

### 5.1 ISO 11783解析器集成

（集成代码...）

### 5.2 AgGateway转换器集成

（集成代码...）

---

## 6. 转换验证

### 6.1 ISO 11783到AgGateway转换验证

（验证代码...）

---

## 7. 精准农业数据存储与分析

### 7.1 PostgreSQL精准农业数据存储

（存储实现见第2节）

### 7.2 精准农业数据分析查询

**查询示例**：

```python
# 查询农田平均土壤湿度
def get_average_soil_moisture(storage: PrecisionAgricultureStorage,
                              field_id: str, days: int = 7) -> float:
    """查询农田最近N天的平均土壤湿度"""
    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    data = storage.get_field_sensor_data(field_id, start_time, end_time)
    if not data:
        return 0.0

    moisture_values = [d['soil_moisture'] for d in data if d['soil_moisture'] is not None]
    return sum(moisture_values) / len(moisture_values) if moisture_values else 0.0

# 查询农机作业效率
def get_machinery_efficiency(storage: PrecisionAgricultureStorage,
                              machinery_id: str, start_date: datetime,
                              end_date: datetime) -> Dict:
    """查询农机作业效率"""
    storage.cur.execute("""
        SELECT
            COUNT(*) as operation_count,
            SUM(EXTRACT(EPOCH FROM (end_time - start_time))/3600) as total_hours,
            AVG(operation_speed) as avg_speed,
            SUM(application_rate) as total_application
        FROM machinery_operations
        WHERE machinery_id = %s
          AND start_time >= %s
          AND start_time <= %s
    """, (machinery_id, start_date, end_date))

    result = storage.cur.fetchone()
    return {
        "operation_count": result[0] or 0,
        "total_hours": result[1] or 0.0,
        "avg_speed": result[2] or 0.0,
        "total_application": result[3] or 0.0
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
