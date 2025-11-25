# 热学Schema转换体系

## 📑 目录

- [热学Schema转换体系](#热学schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 热学模型转换](#2-热学模型转换)
  - [3. 热阻网络转换](#3-热阻网络转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 热学数据存储与分析](#6-热学数据存储与分析)
    - [6.1 PostgreSQL热学数据存储](#61-postgresql热学数据存储)
    - [6.2 热学数据分析查询](#62-热学数据分析查询)

---

## 1. 转换体系概述

热学Schema转换体系支持热学模型、热阻网络、
热仿真软件之间的转换。

### 1.1 转换目标

1. **热学模型转换**：Schema到热仿真模型
2. **热阻网络转换**：Schema到热阻网络
3. **热学数据转换**：不同格式热学数据转换

---

## 2. 热学模型转换

**转换规则**：

- 温度特性 → 边界条件
- 热传导特性 → 材料属性
- 热容量特性 → 热容参数
- 热辐射特性 → 辐射参数

---

## 3. 热阻网络转换

**转换规则**：

- 热阻 → 电阻网络节点
- 热容 → 电容网络节点
- 热源 → 电流源

---

## 4. 转换工具

- **ANSYS Fluent**：CFD热仿真软件
- **COMSOL Multiphysics**：多物理场仿真
- **OpenFOAM**：开源CFD软件

---

## 5. 转换验证

验证转换的热平衡、温度分布和热流分布。

---

## 6. 热学数据存储与分析

### 6.1 PostgreSQL热学数据存储

**热学数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class ThermalStorage:
    """热学数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建热学数据表"""
        # 温度数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS temperature_data (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                sensor_location VARCHAR(200),
                temperature FLOAT NOT NULL,
                temperature_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 热传导数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS heat_conduction_data (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                material_name VARCHAR(200),
                thermal_conductivity FLOAT,
                thermal_resistance FLOAT,
                heat_dissipation_capacity FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 热容量数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS heat_capacity_data (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                material_name VARCHAR(200),
                specific_heat FLOAT,
                heat_capacity FLOAT,
                thermal_inertia FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 热辐射数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS heat_radiation_data (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                surface_name VARCHAR(200),
                emissivity FLOAT CHECK (emissivity >= 0.0 AND emissivity <= 1.0),
                absorptivity FLOAT CHECK (absorptivity >= 0.0 AND absorptivity <= 1.0),
                reflectivity FLOAT CHECK (reflectivity >= 0.0 AND reflectivity <= 1.0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 热学测试数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thermal_test_data (
                id SERIAL PRIMARY KEY,
                test_name VARCHAR(200) NOT NULL,
                device_id VARCHAR(200) NOT NULL,
                test_type VARCHAR(50) NOT NULL,
                test_conditions JSONB NOT NULL,
                test_results JSONB NOT NULL,
                test_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 热学统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thermal_statistics (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_temperature_device_time
            ON temperature_data(device_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_temperature_type
            ON temperature_data(temperature_type, timestamp DESC)
        """)

        self.conn.commit()

    def store_temperature(self, device_id: str, temperature: float,
                         temperature_type: str, sensor_location: str = None,
                         timestamp: datetime = None):
        """存储温度数据"""
        if timestamp is None:
            timestamp = datetime.now()
        self.cur.execute("""
            INSERT INTO temperature_data
            (device_id, sensor_location, temperature, temperature_type, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (device_id, sensor_location, temperature, temperature_type, timestamp))
        self.conn.commit()

    def store_heat_conduction(self, device_id: str, material_name: str,
                             thermal_conductivity: float,
                             thermal_resistance: float,
                             heat_dissipation_capacity: float):
        """存储热传导数据"""
        self.cur.execute("""
            INSERT INTO heat_conduction_data
            (device_id, material_name, thermal_conductivity,
             thermal_resistance, heat_dissipation_capacity)
            VALUES (%s, %s, %s, %s, %s)
        """, (device_id, material_name, thermal_conductivity,
              thermal_resistance, heat_dissipation_capacity))
        self.conn.commit()

    def calculate_temperature_statistics(self, device_id: str,
                                        time_window: datetime):
        """计算温度统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as count,
                AVG(temperature) as avg_temperature,
                MIN(temperature) as min_temperature,
                MAX(temperature) as max_temperature,
                STDDEV(temperature) as stddev_temperature
            FROM temperature_data
            WHERE device_id = %s AND timestamp >= %s
        """, (device_id, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO thermal_statistics
            (device_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, statistic_type, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, (device_id, "temperature", time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 热学数据分析查询

**查询示例**：

```python
# 查询温度趋势
storage.cur.execute("""
    SELECT timestamp, temperature
    FROM temperature_data
    WHERE device_id = %s AND timestamp >= %s
    ORDER BY timestamp
""", (device_id, start_time))

# 计算热阻分析
storage.cur.execute("""
    SELECT device_id, AVG(thermal_resistance) as avg_resistance
    FROM heat_conduction_data
    GROUP BY device_id
""")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
