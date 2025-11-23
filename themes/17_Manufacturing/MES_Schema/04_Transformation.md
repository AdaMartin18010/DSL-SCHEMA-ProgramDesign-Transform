# MES Schema转换体系

## 📑 目录

- [MES Schema转换体系](#mes-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ERP到MES转换实现](#2-erp到mes转换实现)
    - [2.1 ERP订单解析器](#21-erp订单解析器)
    - [2.2 MES订单转换器](#22-mes订单转换器)
  - [3. B2MML解析和转换](#3-b2mml解析和转换)
    - [3.1 B2MML解析器](#31-b2mml解析器)
    - [3.2 B2MML到MES转换](#32-b2mml到mes转换)
  - [4. 生产数据采集系统](#4-生产数据采集系统)
    - [4.1 生产数据采集器](#41-生产数据采集器)
    - [4.2 质量数据采集器](#42-质量数据采集器)
  - [5. MES数据存储与分析](#5-mes数据存储与分析)
    - [5.1 PostgreSQL MES数据存储](#51-postgresql-mes数据存储)
    - [5.2 MES数据分析查询](#52-mes数据分析查询)

---

## 1. 转换体系概述

MES Schema转换体系支持ERP订单、B2MML消息、
生产数据、数据库存储之间的转换。

### 1.1 转换目标

1. **ERP到MES转换**：ERP生产订单到MES生产订单
2. **B2MML解析**：B2MML XML消息解析和转换
3. **生产数据采集**：从生产设备采集实时数据
4. **数据到数据库转换**：MES数据到PostgreSQL存储

---

## 2. ERP到MES转换实现

### 2.1 ERP订单解析器

**完整的ERP订单解析实现**：

```python
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ERPOrderParser:
    """ERP订单解析器"""

    def __init__(self):
        pass

    def parse_erp_order(self, erp_order_data: Dict) -> Dict:
        """解析ERP订单数据"""
        return {
            "order_id": erp_order_data.get("order_id"),
            "order_number": erp_order_data.get("order_number"),
            "product_id": erp_order_data.get("product_id"),
            "product_name": erp_order_data.get("product_name"),
            "quantity": erp_order_data.get("quantity"),
            "unit": erp_order_data.get("unit", "pieces"),
            "start_date": self._parse_datetime(erp_order_data.get("start_date")),
            "end_date": self._parse_datetime(erp_order_data.get("end_date")),
            "delivery_date": self._parse_datetime(erp_order_data.get("delivery_date")),
            "priority": erp_order_data.get("priority", "Normal"),
            "order_type": erp_order_data.get("order_type", "MakeToOrder"),
            "material_requirements": erp_order_data.get("material_requirements", []),
            "work_centers": erp_order_data.get("work_centers", [])
        }

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
```

### 2.2 MES订单转换器

**ERP到MES转换器实现**：

```python
class ERPToMESConverter:
    """ERP到MES转换器"""

    def __init__(self):
        self.parser = ERPOrderParser()

    def convert_erp_order_to_mes(self, erp_order_data: Dict) -> Dict:
        """将ERP订单转换为MES生产订单"""
        erp_order = self.parser.parse_erp_order(erp_order_data)

        mes_order = {
            "order_id": erp_order["order_id"],
            "order_number": erp_order["order_number"],
            "product_id": erp_order["product_id"],
            "product_name": erp_order["product_name"],
            "order_info": {
                "order_quantity": erp_order["quantity"],
                "unit": erp_order["unit"],
                "planned_start_date": erp_order["start_date"],
                "planned_end_date": erp_order["end_date"],
                "delivery_date": erp_order["delivery_date"],
                "priority": erp_order["priority"],
                "order_type": erp_order["order_type"]
            },
            "order_status": {
                "status": "Planned",
                "progress_percentage": 0.0,
                "completed_quantity": 0,
                "rejected_quantity": 0
            },
            "order_resources": {
                "work_centers": erp_order["work_centers"],
                "material_list": self._convert_material_requirements(
                    erp_order["material_requirements"]
                )
            }
        }

        logger.info(f"Converted ERP order {erp_order['order_number']} to MES order")
        return mes_order

    def _convert_material_requirements(self, materials: List[Dict]) -> List[Dict]:
        """转换物料需求"""
        return [
            {
                "material_id": mat.get("material_id"),
                "material_name": mat.get("material_name"),
                "required_quantity": mat.get("quantity", 0),
                "unit": mat.get("unit", "pieces"),
                "issued_quantity": 0
            }
            for mat in materials
        ]
```

---

## 3. B2MML解析和转换

### 3.1 B2MML解析器

**完整的B2MML解析实现**：

```python
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

class B2MMLParser:
    """B2MML解析器"""

    def __init__(self):
        self.namespaces = {
            'b2mml': 'http://www.mesa.org/xml/B2MML-V0600'
        }

    def parse_b2mml_file(self, b2mml_file_path: str) -> Dict:
        """解析B2MML文件"""
        try:
            tree = ET.parse(b2mml_file_path)
            root = tree.getroot()

            # 检测B2MML文档类型
            if root.tag.endswith('ProductionSchedule'):
                return self._parse_production_schedule(root)
            elif root.tag.endswith('WorkOrder'):
                return self._parse_work_order(root)
            elif root.tag.endswith('QualityTestResult'):
                return self._parse_quality_test_result(root)
            else:
                logger.warning(f"Unknown B2MML document type: {root.tag}")
                return {}
        except Exception as e:
            logger.error(f"Error parsing B2MML file: {e}")
            raise

    def _parse_production_schedule(self, root: ET.Element) -> Dict:
        """解析ProductionSchedule"""
        schedule = {
            "schedule_id": self._get_text(root, './/b2mml:ID'),
            "schedule_name": self._get_text(root, './/b2mml:Description'),
            "production_orders": []
        }

        # 解析生产订单
        order_elements = root.findall('.//b2mml:ProductionOrder', self.namespaces)
        for order_elem in order_elements:
            order = {
                "order_id": self._get_text(order_elem, './/b2mml:ID'),
                "order_number": self._get_text(order_elem, './/b2mml:OrderID'),
                "product_id": self._get_text(order_elem, './/b2mml:ProductID'),
                "quantity": self._get_float(order_elem, './/b2mml:Quantity'),
                "start_time": self._get_datetime(order_elem, './/b2mml:StartTime'),
                "end_time": self._get_datetime(order_elem, './/b2mml:EndTime')
            }
            schedule["production_orders"].append(order)

        return schedule

    def _parse_work_order(self, root: ET.Element) -> Dict:
        """解析WorkOrder"""
        return {
            "work_order_id": self._get_text(root, './/b2mml:ID'),
            "order_id": self._get_text(root, './/b2mml:ProductionOrderID'),
            "status": self._get_text(root, './/b2mml:Status'),
            "start_time": self._get_datetime(root, './/b2mml:StartTime'),
            "end_time": self._get_datetime(root, './/b2mml:EndTime')
        }

    def _parse_quality_test_result(self, root: ET.Element) -> Dict:
        """解析QualityTestResult"""
        return {
            "test_id": self._get_text(root, './/b2mml:ID'),
            "product_id": self._get_text(root, './/b2mml:ProductID'),
            "test_result": self._get_text(root, './/b2mml:TestResult'),
            "test_time": self._get_datetime(root, './/b2mml:TestTime')
        }

    def _get_text(self, parent: ET.Element, xpath: str) -> str:
        """获取文本内容"""
        elem = parent.find(xpath, self.namespaces)
        return elem.text if elem is not None and elem.text else ""

    def _get_float(self, parent: ET.Element, xpath: str) -> float:
        """获取浮点数"""
        text = self._get_text(parent, xpath)
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _get_datetime(self, parent: ET.Element, xpath: str) -> Optional[datetime]:
        """获取日期时间"""
        text = self._get_text(parent, xpath)
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace('Z', '+00:00'))
        except Exception:
            return None
```

### 3.2 B2MML到MES转换

**B2MML到MES转换器实现**：

```python
class B2MMLToMESConverter:
    """B2MML到MES转换器"""

    def __init__(self):
        self.parser = B2MMLParser()

    def convert_production_schedule_to_mes(self, b2mml_file_path: str) -> List[Dict]:
        """将B2MML ProductionSchedule转换为MES订单"""
        schedule = self.parser.parse_b2mml_file(b2mml_file_path)

        mes_orders = []
        for order in schedule.get("production_orders", []):
            mes_order = {
                "order_id": order["order_id"],
                "order_number": order["order_number"],
                "product_id": order["product_id"],
                "order_info": {
                    "order_quantity": int(order["quantity"]),
                    "planned_start_date": order["start_time"],
                    "planned_end_date": order["end_time"]
                },
                "order_status": {
                    "status": "Planned",
                    "progress_percentage": 0.0
                }
            }
            mes_orders.append(mes_order)

        return mes_orders
```

---

## 4. 生产数据采集系统

### 4.1 生产数据采集器

**完整的生产数据采集实现**：

```python
import socket
import json
from typing import Dict, Optional
from datetime import datetime

class ProductionDataCollector:
    """生产数据采集器"""

    def __init__(self, equipment_id: str, host: str, port: int = 502):
        self.equipment_id = equipment_id
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> bool:
        """连接到生产设备"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to equipment {self.equipment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to equipment: {e}")
            return False

    def read_production_data(self) -> Optional[Dict]:
        """读取生产数据"""
        if not self.connected:
            return None

        # Modbus读取生产数据寄存器
        data = self._read_modbus_registers(0x1000, 20)
        if data:
            return {
                "equipment_id": self.equipment_id,
                "production_count": data[0],
                "good_count": data[1],
                "reject_count": data[2],
                "cycle_time": data[3] / 100.0,  # seconds
                "status": self._parse_status(data[4]),
                "timestamp": datetime.now()
            }
        return None

    def read_quality_data(self) -> Optional[Dict]:
        """读取质量数据"""
        if not self.connected:
            return None

        # Modbus读取质量数据寄存器
        data = self._read_modbus_registers(0x2000, 10)
        if data:
            return {
                "equipment_id": self.equipment_id,
                "inspection_count": data[0],
                "pass_count": data[1],
                "fail_count": data[2],
                "pass_rate": (data[1] / data[0] * 100) if data[0] > 0 else 0,
                "timestamp": datetime.now()
            }
        return None

    def _read_modbus_registers(self, start_address: int, count: int) -> Optional[List[int]]:
        """读取Modbus寄存器"""
        # 实际实现需要使用pymodbus库
        return None

    def _parse_status(self, value: int) -> str:
        """解析设备状态"""
        status_map = {0: "Idle", 1: "Running", 2: "Setup", 3: "Maintenance", 4: "Breakdown"}
        return status_map.get(value, "Unknown")
```

### 4.2 质量数据采集器

**质量数据采集器实现**：

```python
class QualityDataCollector:
    """质量数据采集器"""

    def __init__(self, inspection_station_id: str, host: str, port: int = 502):
        self.station_id = inspection_station_id
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None

    def connect(self) -> bool:
        """连接到检测站"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"Connected to inspection station {self.station_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to inspection station: {e}")
            return False

    def read_inspection_result(self, product_id: str) -> Optional[Dict]:
        """读取检测结果"""
        if not self.socket:
            return None

        # Modbus读取检测结果
        data = self._read_modbus_registers(0x3000, 20)
        if data:
            return {
                "inspection_id": f"INS_{product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "product_id": product_id,
                "inspection_type": "Final",
                "inspection_result": "Pass" if data[0] == 1 else "Fail",
                "inspection_value": data[1] / 100.0,
                "inspection_time": datetime.now(),
                "inspector": "AutoInspection"
            }
        return None

    def _read_modbus_registers(self, start_address: int, count: int) -> Optional[List[int]]:
        """读取Modbus寄存器"""
        return None
```

---

## 5. MES数据存储与分析

### 5.1 PostgreSQL MES数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class MESStorage:
    """MES数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建MES数据表"""
        # 生产订单表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS production_orders (
                id BIGSERIAL PRIMARY KEY,
                order_id VARCHAR(20) UNIQUE NOT NULL,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                product_id VARCHAR(20) NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                order_quantity INTEGER NOT NULL,
                unit VARCHAR(20) DEFAULT 'pieces',
                planned_start_date TIMESTAMP NOT NULL,
                planned_end_date TIMESTAMP NOT NULL,
                delivery_date TIMESTAMP NOT NULL,
                priority VARCHAR(20) DEFAULT 'Normal',
                order_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'Planned',
                progress_percentage DECIMAL(5,2) DEFAULT 0.0,
                completed_quantity INTEGER DEFAULT 0,
                rejected_quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 生产执行表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS production_executions (
                id BIGSERIAL PRIMARY KEY,
                execution_id VARCHAR(20) UNIQUE NOT NULL,
                order_id VARCHAR(20) NOT NULL,
                work_order_id VARCHAR(50) NOT NULL,
                current_step INTEGER DEFAULT 1,
                status VARCHAR(20) NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                operator VARCHAR(100),
                shift VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES production_orders(order_id)
            )
        """)

        # 质量检测表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_inspections (
                id BIGSERIAL PRIMARY KEY,
                inspection_id VARCHAR(20) UNIQUE NOT NULL,
                order_id VARCHAR(20) NOT NULL,
                product_id VARCHAR(20) NOT NULL,
                inspection_type VARCHAR(50) NOT NULL,
                inspection_item VARCHAR(200) NOT NULL,
                inspection_result VARCHAR(20) NOT NULL,
                inspection_value DECIMAL(10,2),
                inspection_unit VARCHAR(20),
                inspection_time TIMESTAMP NOT NULL,
                inspector VARCHAR(100) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES production_orders(order_id)
            )
        """)

        # 设备状态表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS equipment_status (
                id BIGSERIAL PRIMARY KEY,
                equipment_id VARCHAR(20) NOT NULL,
                equipment_code VARCHAR(50) NOT NULL,
                operational_status VARCHAR(20) NOT NULL,
                availability DECIMAL(5,2),
                utilization DECIMAL(5,2),
                performance DECIMAL(5,2),
                quality_rate DECIMAL(5,2),
                oee DECIMAL(5,2),
                status_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 生产数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS production_data (
                id BIGSERIAL PRIMARY KEY,
                equipment_id VARCHAR(20) NOT NULL,
                production_count INTEGER DEFAULT 0,
                good_count INTEGER DEFAULT 0,
                reject_count INTEGER DEFAULT 0,
                cycle_time DECIMAL(8,2),
                data_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_orders_order_id
            ON production_orders(order_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_executions_order_id
            ON production_executions(order_id, status)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_quality_inspections_order_id
            ON quality_inspections(order_id, inspection_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_data_time
            ON production_data(equipment_id, data_time DESC)
        """)

        self.conn.commit()

    def store_production_order(self, order_data: Dict) -> int:
        """存储生产订单"""
        self.cur.execute("""
            INSERT INTO production_orders (
                order_id, order_number, product_id, product_name,
                order_quantity, unit, planned_start_date, planned_end_date,
                delivery_date, priority, order_type, status,
                progress_percentage, completed_quantity, rejected_quantity
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO UPDATE SET
                status = EXCLUDED.status,
                progress_percentage = EXCLUDED.progress_percentage,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            order_data.get("order_id"),
            order_data.get("order_number"),
            order_data.get("product_id"),
            order_data.get("product_name"),
            order_data.get("order_info", {}).get("order_quantity"),
            order_data.get("order_info", {}).get("unit"),
            order_data.get("order_info", {}).get("planned_start_date"),
            order_data.get("order_info", {}).get("planned_end_date"),
            order_data.get("order_info", {}).get("delivery_date"),
            order_data.get("order_info", {}).get("priority"),
            order_data.get("order_info", {}).get("order_type"),
            order_data.get("order_status", {}).get("status"),
            order_data.get("order_status", {}).get("progress_percentage"),
            order_data.get("order_status", {}).get("completed_quantity"),
            order_data.get("order_status", {}).get("rejected_quantity")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_production_execution(self, execution_data: Dict) -> int:
        """存储生产执行"""
        self.cur.execute("""
            INSERT INTO production_executions (
                execution_id, order_id, work_order_id, current_step,
                status, start_time, end_time, operator, shift
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (execution_id) DO UPDATE SET
                current_step = EXCLUDED.current_step,
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            execution_data.get("execution_id"),
            execution_data.get("order_id"),
            execution_data.get("work_order_id"),
            execution_data.get("execution_status", {}).get("current_step"),
            execution_data.get("execution_status", {}).get("status"),
            execution_data.get("execution_status", {}).get("start_time"),
            execution_data.get("execution_status", {}).get("end_time"),
            execution_data.get("execution_status", {}).get("operator"),
            execution_data.get("execution_status", {}).get("shift")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_quality_inspection(self, inspection_data: Dict) -> int:
        """存储质量检测"""
        self.cur.execute("""
            INSERT INTO quality_inspections (
                inspection_id, order_id, product_id, inspection_type,
                inspection_item, inspection_result, inspection_value,
                inspection_unit, inspection_time, inspector
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (inspection_id) DO UPDATE SET
                inspection_result = EXCLUDED.inspection_result
            RETURNING id
        """, (
            inspection_data.get("inspection_id"),
            inspection_data.get("order_id"),
            inspection_data.get("product_id"),
            inspection_data.get("inspection_type"),
            inspection_data.get("inspection_item"),
            inspection_data.get("inspection_result"),
            inspection_data.get("inspection_value"),
            inspection_data.get("inspection_unit"),
            inspection_data.get("inspection_time"),
            inspection_data.get("inspector")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_production_data(self, prod_data: Dict):
        """存储生产数据"""
        self.cur.execute("""
            INSERT INTO production_data (
                equipment_id, production_count, good_count,
                reject_count, cycle_time
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            prod_data.get("equipment_id"),
            prod_data.get("production_count"),
            prod_data.get("good_count"),
            prod_data.get("reject_count"),
            prod_data.get("cycle_time")
        ))
        self.conn.commit()

    def store_equipment_status(self, status_data: Dict):
        """存储设备状态"""
        self.cur.execute("""
            INSERT INTO equipment_status (
                equipment_id, equipment_code, operational_status,
                availability, utilization, performance, quality_rate, oee
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            status_data.get("equipment_id"),
            status_data.get("equipment_code"),
            status_data.get("operational_status"),
            status_data.get("availability"),
            status_data.get("utilization"),
            status_data.get("performance"),
            status_data.get("quality_rate"),
            status_data.get("oee")
        ))
        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 5.2 MES数据分析查询

**数据分析查询实现**：

```python
    def get_production_order_statistics(self, days: int = 30) -> Dict:
        """查询生产订单统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_orders,
                COUNT(CASE WHEN status = 'InProgress' THEN 1 END) as in_progress_orders,
                AVG(progress_percentage) as avg_progress,
                SUM(order_quantity) as total_quantity,
                SUM(completed_quantity) as total_completed,
                SUM(rejected_quantity) as total_rejected
            FROM production_orders
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (days,))
        row = self.cur.fetchone()
        return {
            "total_orders": row[0],
            "completed_orders": row[1],
            "in_progress_orders": row[2],
            "avg_progress": float(row[3]) if row[3] else None,
            "total_quantity": row[4],
            "total_completed": row[5],
            "total_rejected": row[6]
        }

    def get_quality_statistics(self, order_id: str) -> Dict:
        """查询质量统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_inspections,
                COUNT(CASE WHEN inspection_result = 'Pass' THEN 1 END) as pass_count,
                COUNT(CASE WHEN inspection_result = 'Fail' THEN 1 END) as fail_count,
                (COUNT(CASE WHEN inspection_result = 'Pass' THEN 1 END)::DECIMAL /
                 NULLIF(COUNT(*), 0) * 100) as pass_rate
            FROM quality_inspections
            WHERE order_id = %s
        """, (order_id,))
        row = self.cur.fetchone()
        return {
            "total_inspections": row[0],
            "pass_count": row[1],
            "fail_count": row[2],
            "pass_rate": float(row[3]) if row[3] else None
        }

    def get_equipment_oee_statistics(self, equipment_id: str, days: int = 30) -> Dict:
        """查询设备OEE统计"""
        self.cur.execute("""
            SELECT
                AVG(availability) as avg_availability,
                AVG(utilization) as avg_utilization,
                AVG(performance) as avg_performance,
                AVG(quality_rate) as avg_quality_rate,
                AVG(oee) as avg_oee,
                COUNT(*) as data_count
            FROM equipment_status
            WHERE equipment_id = %s
            AND status_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (equipment_id, days))
        row = self.cur.fetchone()
        return {
            "avg_availability": float(row[0]) if row[0] else None,
            "avg_utilization": float(row[1]) if row[1] else None,
            "avg_performance": float(row[2]) if row[2] else None,
            "avg_quality_rate": float(row[3]) if row[3] else None,
            "avg_oee": float(row[4]) if row[4] else None,
            "data_count": row[5]
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
