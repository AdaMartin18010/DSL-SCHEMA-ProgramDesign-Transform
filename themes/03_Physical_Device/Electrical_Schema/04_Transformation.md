# 物理设备电气Schema转换体系

## 📑 目录

- [物理设备电气Schema转换体系](#物理设备电气schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 电气特性转换](#2-电气特性转换)
    - [2.1 电压特性转换](#21-电压特性转换)
    - [2.2 电流特性转换](#22-电流特性转换)
    - [2.3 功率特性转换](#23-功率特性转换)
    - [2.4 绝缘特性转换](#24-绝缘特性转换)
  - [3. 转换实例](#3-转换实例)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 电气数据存储与分析](#6-电气数据存储与分析)
    - [6.1 PostgreSQL电气数据存储](#61-postgresql电气数据存储)
    - [6.2 电气数据分析查询](#62-电气数据分析查询)
  - [7. 参考文献](#7-参考文献)
    - [7.1 标准文档](#71-标准文档)
    - [7.2 技术文档](#72-技术文档)

---

## 1. 转换体系概述

物理设备电气Schema转换体系支持将电气Schema
转换为多种编程语言的电气特性监测和控制代码。

**转换目标**：

1. **Python**：电气特性监测代码
2. **C/C++**：嵌入式电气监测代码
3. **PLC代码**：IEC 61131-3代码
4. **数字孪生模型**：数字孪生电气模型

---

## 2. 电气特性转换

### 2.1 电压特性转换

**Schema到Python转换**：

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ProtectionType(Enum):
    SHUTDOWN = "shutdown"
    CURRENT_LIMIT = "current_limit"
    VOLTAGE_CLAMP = "voltage_clamp"

@dataclass
class VoltageCharacteristics:
    """电压特性"""
    rated_voltage: float  # V
    voltage_range_min: float  # V
    voltage_range_max: float  # V
    tolerance: float = 5.0  # %
    overvoltage_threshold: Optional[float] = None  # V
    overvoltage_response_time: Optional[float] = None  # ms
    overvoltage_protection_type: Optional[ProtectionType] = None

    def check_voltage(self, voltage: float) -> tuple[bool, Optional[str]]:
        """检查电压是否在范围内"""
        min_voltage = self.rated_voltage * (1 - self.tolerance / 100)
        max_voltage = self.rated_voltage * (1 + self.tolerance / 100)

        if voltage < min_voltage:
            return False, f"电压过低: {voltage}V < {min_voltage}V"
        elif voltage > max_voltage:
            return False, f"电压过高: {voltage}V > {max_voltage}V"

        # 检查过压保护
        if self.overvoltage_threshold and voltage > self.overvoltage_threshold:
            return False, f"触发过压保护: {voltage}V > {self.overvoltage_threshold}V"

        return True, None

    def apply_protection(self, voltage: float) -> float:
        """应用过压保护"""
        if self.overvoltage_protection_type == ProtectionType.VOLTAGE_CLAMP:
            if self.overvoltage_threshold:
                return min(voltage, self.overvoltage_threshold)
        return voltage
```

### 2.2 电流特性转换

**Schema到Python转换**：

```python
@dataclass
class CurrentCharacteristics:
    """电流特性"""
    rated_current: float  # A
    current_range_min: float  # A
    current_range_max: float  # A
    overcurrent_threshold: Optional[float] = None  # A
    overcurrent_response_time: Optional[float] = None  # ms
    max_leakage_current: float = 0.5  # mA

    def check_current(self, current: float) -> tuple[bool, Optional[str]]:
        """检查电流是否在范围内"""
        if current < self.current_range_min:
            return False, f"电流过低: {current}A < {self.current_range_min}A"
        elif current > self.current_range_max:
            return False, f"电流过高: {current}A > {self.current_range_max}A"

        # 检查过流保护
        if self.overcurrent_threshold and current > self.overcurrent_threshold:
            return False, f"触发过流保护: {current}A > {self.overcurrent_threshold}A"

        return True, None

    def check_leakage_current(self, leakage: float) -> tuple[bool, Optional[str]]:
        """检查漏电流"""
        if leakage > self.max_leakage_current:
            return False, f"漏电流超标: {leakage}mA > {self.max_leakage_current}mA"
        return True, None
```

### 2.3 功率特性转换

**Schema到Python转换**：

```python
@dataclass
class PowerCharacteristics:
    """功率特性"""
    rated_power: float  # W
    power_range_min: float  # W
    power_range_max: float  # W
    nominal_efficiency: float  # %
    power_factor: float = 1.0

    def calculate_power(self, voltage: float, current: float) -> float:
        """计算功率"""
        return voltage * current * self.power_factor

    def calculate_efficiency(self, input_power: float, output_power: float) -> float:
        """计算效率"""
        if input_power == 0:
            return 0.0
        return (output_power / input_power) * 100

    def check_power(self, power: float) -> tuple[bool, Optional[str]]:
        """检查功率是否在范围内"""
        if power < self.power_range_min:
            return False, f"功率过低: {power}W < {self.power_range_min}W"
        elif power > self.power_range_max:
            return False, f"功率过高: {power}W > {self.power_range_max}W"
        return True, None
```

### 2.4 绝缘特性转换

**Schema到Python转换**：

```python
from enum import Enum

class InsulationClass(Enum):
    CLASS_I = "Class_I"
    CLASS_II = "Class_II"
    CLASS_III = "Class_III"

@dataclass
class InsulationCharacteristics:
    """绝缘特性"""
    insulation_class: InsulationClass
    min_insulation_resistance: float  # MΩ
    dielectric_withstand_voltage: float  # V
    min_creepage_distance: float  # mm
    min_clearance_distance: float  # mm

    def check_insulation_resistance(self, resistance: float) -> tuple[bool, Optional[str]]:
        """检查绝缘电阻"""
        if resistance < self.min_insulation_resistance:
            return False, f"绝缘电阻不足: {resistance}MΩ < {self.min_insulation_resistance}MΩ"
        return True, None

    def perform_dielectric_test(self, test_voltage: float) -> tuple[bool, Optional[str]]:
        """执行耐压测试"""
        if test_voltage < self.dielectric_withstand_voltage:
            return False, f"测试电压不足: {test_voltage}V < {self.dielectric_withstand_voltage}V"
        return True, None
```

---

## 3. 转换实例

**完整电气Schema转换示例**：

```python
# Schema定义的电气特性转换为Python代码
class ElectricalDeviceMonitor:
    """电气设备监测器"""

    def __init__(self, voltage_spec: VoltageCharacteristics,
                 current_spec: CurrentCharacteristics,
                 power_spec: PowerCharacteristics,
                 insulation_spec: InsulationCharacteristics):
        self.voltage_spec = voltage_spec
        self.current_spec = current_spec
        self.power_spec = power_spec
        self.insulation_spec = insulation_spec

    def monitor(self, voltage: float, current: float) -> dict:
        """监测电气参数"""
        results = {}

        # 检查电压
        voltage_ok, voltage_msg = self.voltage_spec.check_voltage(voltage)
        results['voltage'] = {'ok': voltage_ok, 'message': voltage_msg}

        # 检查电流
        current_ok, current_msg = self.current_spec.check_current(current)
        results['current'] = {'ok': current_ok, 'message': current_msg}

        # 计算功率
        power = self.power_spec.calculate_power(voltage, current)
        power_ok, power_msg = self.power_spec.check_power(power)
        results['power'] = {'value': power, 'ok': power_ok, 'message': power_msg}

        return results
```

---

## 4. 转换工具

**工具列表**：

1. **代码生成器**：从Schema生成电气监测代码
2. **验证工具**：验证电气特性正确性
3. **测试工具**：电气特性测试工具

---

## 5. 转换验证

**验证方法**：

1. **语法验证**：验证代码语法
2. **语义验证**：验证电气逻辑语义
3. **标准合规性验证**：验证符合电气标准

---

## 6. 电气数据存储与分析

### 6.1 PostgreSQL电气数据存储

**电气特性和监测数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ElectricalReading:
    """电气读数"""
    device_id: str
    voltage: float
    current: float
    power: float
    timestamp: datetime
    status: str = 'normal'

@dataclass
class ElectricalEvent:
    """电气事件"""
    device_id: str
    event_type: str
    event_data: Dict
    timestamp: datetime
    severity: str = 'info'

class ElectricalStorage:
    """电气数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建电气数据表"""
        # 电气设备定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS electrical_devices (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) UNIQUE NOT NULL,
                device_name VARCHAR(200) NOT NULL,
                device_type VARCHAR(50) NOT NULL,
                electrical_specs JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 电气读数表（时序数据）
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS electrical_readings (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                voltage FLOAT NOT NULL,
                current FLOAT NOT NULL,
                power FLOAT NOT NULL,
                status VARCHAR(50) DEFAULT 'normal',
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES electrical_devices(device_id)
            )
        """)

        # 电气事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS electrical_events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB NOT NULL,
                severity VARCHAR(50) DEFAULT 'info',
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES electrical_devices(device_id)
            )
        """)

        # 电气统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS electrical_statistics (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES electrical_devices(device_id),
                UNIQUE(device_id, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_readings_device_time
            ON electrical_readings(device_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_device_time
            ON electrical_events(device_id, timestamp DESC)
        """)

        self.conn.commit()

    def register_device(self, device_id: str, device_name: str,
                       device_type: str, electrical_specs: Dict):
        """注册电气设备"""
        self.cur.execute("""
            INSERT INTO electrical_devices
            (device_id, device_name, device_type, electrical_specs)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id) DO UPDATE
            SET device_name = EXCLUDED.device_name,
                device_type = EXCLUDED.device_type,
                electrical_specs = EXCLUDED.electrical_specs,
                updated_at = CURRENT_TIMESTAMP
        """, (device_id, device_name, device_type,
              json.dumps(electrical_specs)))
        self.conn.commit()

    def store_reading(self, reading: ElectricalReading):
        """存储电气读数"""
        self.cur.execute("""
            INSERT INTO electrical_readings
            (device_id, voltage, current, power, status, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (reading.device_id, reading.voltage, reading.current,
              reading.power, reading.status, reading.timestamp))
        self.conn.commit()

    def store_event(self, event: ElectricalEvent):
        """存储电气事件"""
        self.cur.execute("""
            INSERT INTO electrical_events
            (device_id, event_type, event_data, severity, timestamp)
            VALUES (%s, %s, %s::jsonb, %s, %s)
        """, (event.device_id, event.event_type,
              json.dumps(event.event_data), event.severity,
              event.timestamp))
        self.conn.commit()

    def get_readings(self, device_id: str,
                    start_time: datetime = None,
                    end_time: datetime = None,
                    limit: int = 1000) -> List[Dict]:
        """获取电气读数历史"""
        query = """
            SELECT voltage, current, power, status, timestamp
            FROM electrical_readings
            WHERE device_id = %s
        """
        params = [device_id]

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        results = []
        for row in self.cur.fetchall():
            results.append({
                'voltage': row[0],
                'current': row[1],
                'power': row[2],
                'status': row[3],
                'timestamp': row[4]
            })
        return results

    def calculate_statistics(self, device_id: str,
                            time_window: timedelta = timedelta(hours=1)) -> Dict:
        """计算电气统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.cur.execute("""
            SELECT
                COUNT(*) as reading_count,
                AVG(voltage) as avg_voltage,
                AVG(current) as avg_current,
                AVG(power) as avg_power,
                MIN(voltage) as min_voltage,
                MAX(voltage) as max_voltage,
                MIN(current) as min_current,
                MAX(current) as max_current,
                MIN(power) as min_power,
                MAX(power) as max_power
            FROM electrical_readings
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        stats = self.cur.fetchone()

        statistics = {
            'reading_count': stats[0] if stats[0] else 0,
            'avg_voltage': float(stats[1]) if stats[1] else 0,
            'avg_current': float(stats[2]) if stats[2] else 0,
            'avg_power': float(stats[3]) if stats[3] else 0,
            'min_voltage': float(stats[4]) if stats[4] else 0,
            'max_voltage': float(stats[5]) if stats[5] else 0,
            'min_current': float(stats[6]) if stats[6] else 0,
            'max_current': float(stats[7]) if stats[7] else 0,
            'min_power': float(stats[8]) if stats[8] else 0,
            'max_power': float(stats[9]) if stats[9] else 0
        }

        # 存储统计结果
        self.cur.execute("""
            INSERT INTO electrical_statistics
            (device_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, statistic_type, time_window) DO UPDATE
            SET statistics = EXCLUDED.statistics
        """, (device_id, 'electrical_statistics', end_time,
              json.dumps(statistics)))
        self.conn.commit()

        return statistics

    def detect_anomalies(self, device_id: str,
                        time_window: timedelta = timedelta(hours=24)) -> List[Dict]:
        """检测电气异常"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        # 获取设备规格
        self.cur.execute("""
            SELECT electrical_specs FROM electrical_devices
            WHERE device_id = %s
        """, (device_id,))
        device = self.cur.fetchone()
        if not device:
            return []

        specs = device[0]
        voltage_min = specs.get('voltage_range_min', 0)
        voltage_max = specs.get('voltage_range_max', 1000)
        current_max = specs.get('current_max', 100)

        # 查找异常读数
        self.cur.execute("""
            SELECT voltage, current, power, timestamp
            FROM electrical_readings
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
              AND (voltage < %s OR voltage > %s OR current > %s)
            ORDER BY timestamp DESC
        """, (device_id, start_time, end_time,
              voltage_min, voltage_max, current_max))

        anomalies = []
        for row in self.cur.fetchall():
            anomalies.append({
                'voltage': row[0],
                'current': row[1],
                'power': row[2],
                'timestamp': row[3],
                'reason': 'voltage_out_of_range' if row[0] < voltage_min or row[0] > voltage_max
                         else 'current_exceeded'
            })
        return anomalies

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 电气数据分析查询

**高级分析查询**：

```python
class ElectricalAnalyzer:
    """电气数据分析器"""

    def __init__(self, storage: ElectricalStorage):
        self.storage = storage

    def analyze_power_consumption(self, device_id: str,
                                 time_window: timedelta = timedelta(hours=24)) -> Dict:
        """分析功耗"""
        stats = self.storage.calculate_statistics(device_id, time_window)

        # 计算总能耗（假设采样间隔为1秒）
        total_energy = stats['avg_power'] * time_window.total_seconds() / 3600  # kWh

        return {
            'device_id': device_id,
            'time_window': time_window,
            'avg_power': stats['avg_power'],
            'max_power': stats['max_power'],
            'min_power': stats['min_power'],
            'total_energy_kwh': total_energy
        }
```

---

## 7. 参考文献

### 7.1 标准文档

- IEC 60335-1:2020 Household and similar electrical appliances
- GB/T 19903 工业设备控制标准

### 7.2 技术文档

- 电气特性监测代码实现最佳实践
- PostgreSQL JSONB文档

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展电气数据存储和分析功能，新增PostgreSQL存储方案）
