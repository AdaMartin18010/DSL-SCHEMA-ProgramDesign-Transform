# 物理设备安全Schema转换体系

## 📑 目录

- [物理设备安全Schema转换体系](#物理设备安全schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 安全特性转换](#2-安全特性转换)
    - [2.1 安全等级转换](#21-安全等级转换)
    - [2.2 安全功能转换](#22-安全功能转换)
    - [2.3 安全认证转换](#23-安全认证转换)
    - [2.4 安全合规转换](#24-安全合规转换)
  - [3. 转换实例](#3-转换实例)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 安全数据存储与分析](#6-安全数据存储与分析)
    - [6.1 PostgreSQL安全数据存储](#61-postgresql安全数据存储)
  - [7. 参考文献](#7-参考文献)
    - [7.1 标准文档](#71-标准文档)
    - [7.2 技术文档](#72-技术文档)

---

## 1. 转换体系概述

物理设备安全Schema转换体系支持将安全Schema
转换为多种格式的安全代码和配置。

**转换目标**：

1. **安全PLC代码**：IEC 61131-3安全代码
2. **安全配置**：安全系统配置代码
3. **安全验证代码**：安全验证和测试代码
4. **合规检查代码**：合规性检查代码

---

## 2. 安全特性转换

### 2.1 安全等级转换

**Schema到Python转换**：

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class SILLevel(Enum):
    SIL_1 = "SIL_1"
    SIL_2 = "SIL_2"
    SIL_3 = "SIL_3"
    SIL_4 = "SIL_4"

class SafetyCategory(Enum):
    CATEGORY_B = "Category_B"
    CATEGORY_1 = "Category_1"
    CATEGORY_2 = "Category_2"
    CATEGORY_3 = "Category_3"
    CATEGORY_4 = "Category_4"

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "VeryHigh"

@dataclass
class SafetyLevel:
    """安全等级"""
    sil_level: SILLevel
    safety_category: SafetyCategory
    risk_level: RiskLevel
    pfh: float  # 每小时危险失效概率 (1/h)
    mtbf: Optional[float] = None  # 平均故障间隔时间 (h)

    def check_sil_requirement(self) -> tuple[bool, Optional[str]]:
        """检查SIL等级要求"""
        sil_pfh_limits = {
            SILLevel.SIL_1: (1e-5, 1e-4),
            SILLevel.SIL_2: (1e-6, 1e-5),
            SILLevel.SIL_3: (1e-7, 1e-6),
            SILLevel.SIL_4: (1e-8, 1e-7),
        }

        min_pfh, max_pfh = sil_pfh_limits[self.sil_level]
        if self.pfh < min_pfh or self.pfh > max_pfh:
            return False, f"PFH值{self.pfh}不在SIL {self.sil_level.value}要求范围内"
        return True, None
```

### 2.2 安全功能转换

**Schema到Python转换**：

```python
from enum import Enum

class StopCategory(Enum):
    CATEGORY_0 = "Category_0"  # 立即断电停止
    CATEGORY_1 = "Category_1"  # 受控停止后断电
    CATEGORY_2 = "Category_2"  # 受控停止

@dataclass
class EmergencyStop:
    """急停功能"""
    enabled: bool = True
    response_time: float = 500.0  # ms
    stop_category: StopCategory = StopCategory.CATEGORY_0
    reset_method: str = "manual"  # manual or automatic

    def trigger(self) -> bool:
        """触发急停"""
        if not self.enabled:
            return False
        # 实现急停逻辑
        return True

@dataclass
class SafetyDoorLock:
    """安全门锁"""
    enabled: bool = False
    lock_type: str = "mechanical"  # mechanical, magnetic, electronic
    interlock_switch: bool = True
    monitoring: bool = True

    def check_door_status(self) -> tuple[bool, bool]:
        """检查门状态"""
        # 返回 (门是否关闭, 门是否锁定)
        door_closed = True  # 从传感器读取
        door_locked = True  # 从锁读取
        return door_closed, door_locked

@dataclass
class LightCurtain:
    """光幕保护"""
    enabled: bool = False
    resolution: float = 14.0  # mm
    response_time: float = 20.0  # ms
    muting: bool = False

    def check_obstruction(self) -> bool:
        """检查是否有遮挡"""
        if not self.enabled:
            return False
        # 从光幕传感器读取
        obstructed = False
        return obstructed
```

### 2.3 安全认证转换

**Schema到Python转换**：

```python
@dataclass
class Certification:
    """安全认证"""
    ce_marking: bool = False
    ce_certificate_number: Optional[str] = None
    ul_listing: bool = False
    ul_file_number: Optional[str] = None
    ccc_certification: bool = False
    ccc_certificate_number: Optional[str] = None

    def check_compliance(self, target_market: str) -> tuple[bool, Optional[str]]:
        """检查合规性"""
        if target_market == "EU" and not self.ce_marking:
            return False, "缺少CE认证"
        elif target_market == "US" and not self.ul_listing:
            return False, "缺少UL认证"
        elif target_market == "CN" and not self.ccc_certification:
            return False, "缺少CCC认证"
        return True, None
```

### 2.4 安全合规转换

**Schema到Python转换**：

```python
@dataclass
class Compliance:
    """安全合规"""
    iec_61508_compliant: bool = False
    iec_61508_sil_level: Optional[SILLevel] = None
    iec_60335_compliant: bool = False
    gb_t_compliant: bool = False
    gb_t_standards: List[str] = None

    def __post_init__(self):
        if self.gb_t_standards is None:
            self.gb_t_standards = []

    def check_iec_61508_compliance(self) -> tuple[bool, Optional[str]]:
        """检查IEC 61508合规性"""
        if not self.iec_61508_compliant:
            return False, "不符合IEC 61508标准"
        return True, None

    def check_iec_60335_compliance(self) -> tuple[bool, Optional[str]]:
        """检查IEC 60335-1合规性"""
        if not self.iec_60335_compliant:
            return False, "不符合IEC 60335-1标准"
        return True, None
```

---

## 3. 转换实例

**完整安全Schema转换示例**：

```python
# Schema定义的安全特性转换为Python代码
class SafetySystem:
    """安全系统"""

    def __init__(self, safety_level: SafetyLevel,
                 emergency_stop: EmergencyStop,
                 door_lock: SafetyDoorLock,
                 light_curtain: LightCurtain,
                 certification: Certification,
                 compliance: Compliance):
        self.safety_level = safety_level
        self.emergency_stop = emergency_stop
        self.door_lock = door_lock
        self.light_curtain = light_curtain
        self.certification = certification
        self.compliance = compliance

    def safety_check(self) -> dict:
        """安全检查"""
        results = {}

        # 检查SIL等级
        sil_ok, sil_msg = self.safety_level.check_sil_requirement()
        results['sil'] = {'ok': sil_ok, 'message': sil_msg}

        # 检查安全功能
        results['emergency_stop'] = {'enabled': self.emergency_stop.enabled}
        results['door_lock'] = {'enabled': self.door_lock.enabled}
        results['light_curtain'] = {'enabled': self.light_curtain.enabled}

        # 检查合规性
        compliance_ok, compliance_msg = self.compliance.check_iec_61508_compliance()
        results['compliance'] = {'ok': compliance_ok, 'message': compliance_msg}

        return results
```

---

## 4. 转换工具

**工具列表**：

1. **安全代码生成器**：从Schema生成安全代码
2. **安全验证工具**：验证安全配置正确性
3. **合规检查工具**：检查合规性

---

## 5. 转换验证

**验证方法**：

1. **安全属性验证**：验证安全属性满足
2. **标准合规性验证**：验证符合安全标准
3. **安全测试**：进行安全功能测试

---

## 6. 安全数据存储与分析

### 6.1 PostgreSQL安全数据存储

**安全特性和事件数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class SafetyEvent:
    """安全事件"""
    device_id: str
    event_type: str
    event_data: Dict
    sil_level: str
    timestamp: datetime
    severity: str = 'info'

@dataclass
class SafetyInspection:
    """安全检查"""
    device_id: str
    inspection_type: str
    inspection_result: Dict
    compliance_status: str
    timestamp: datetime

class SafetyStorage:
    """安全数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建安全数据表"""
        # 安全设备定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS safety_devices (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) UNIQUE NOT NULL,
                device_name VARCHAR(200) NOT NULL,
                device_type VARCHAR(50) NOT NULL,
                safety_specs JSONB NOT NULL,
                sil_level VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 安全事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS safety_events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB NOT NULL,
                sil_level VARCHAR(10),
                severity VARCHAR(50) DEFAULT 'info',
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES safety_devices(device_id)
            )
        """)

        # 安全检查表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS safety_inspections (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                inspection_type VARCHAR(50) NOT NULL,
                inspection_result JSONB NOT NULL,
                compliance_status VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES safety_devices(device_id)
            )
        """)

        # 安全统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS safety_statistics (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES safety_devices(device_id),
                UNIQUE(device_id, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_device_time
            ON safety_events(device_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_inspections_device_time
            ON safety_inspections(device_id, timestamp DESC)
        """)

        self.conn.commit()

    def register_device(self, device_id: str, device_name: str,
                       device_type: str, safety_specs: Dict,
                       sil_level: str = None):
        """注册安全设备"""
        self.cur.execute("""
            INSERT INTO safety_devices
            (device_id, device_name, device_type, safety_specs, sil_level)
            VALUES (%s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (device_id) DO UPDATE
            SET device_name = EXCLUDED.device_name,
                device_type = EXCLUDED.device_type,
                safety_specs = EXCLUDED.safety_specs,
                sil_level = EXCLUDED.sil_level,
                updated_at = CURRENT_TIMESTAMP
        """, (device_id, device_name, device_type,
              json.dumps(safety_specs), sil_level))
        self.conn.commit()

    def store_event(self, event: SafetyEvent):
        """存储安全事件"""
        self.cur.execute("""
            INSERT INTO safety_events
            (device_id, event_type, event_data, sil_level, severity, timestamp)
            VALUES (%s, %s, %s::jsonb, %s, %s, %s)
        """, (event.device_id, event.event_type,
              json.dumps(event.event_data), event.sil_level,
              event.severity, event.timestamp))
        self.conn.commit()

    def store_inspection(self, inspection: SafetyInspection):
        """存储安全检查"""
        self.cur.execute("""
            INSERT INTO safety_inspections
            (device_id, inspection_type, inspection_result, compliance_status, timestamp)
            VALUES (%s, %s, %s::jsonb, %s, %s)
        """, (inspection.device_id, inspection.inspection_type,
              json.dumps(inspection.inspection_result),
              inspection.compliance_status, inspection.timestamp))
        self.conn.commit()

    def calculate_statistics(self, device_id: str,
                            time_window: timedelta = timedelta(hours=1)) -> Dict:
        """计算安全统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        # 事件统计
        self.cur.execute("""
            SELECT
                COUNT(*) as event_count,
                COUNT(DISTINCT event_type) as unique_event_types,
                COUNT(CASE WHEN severity = 'error' THEN 1 END) as error_count
            FROM safety_events
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        event_stats = self.cur.fetchone()

        # 检查统计
        self.cur.execute("""
            SELECT
                COUNT(*) as inspection_count,
                COUNT(CASE WHEN compliance_status = 'compliant' THEN 1 END) as compliant_count
            FROM safety_inspections
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        inspection_stats = self.cur.fetchone()

        statistics = {
            'events': {
                'count': event_stats[0] if event_stats[0] else 0,
                'unique_types': event_stats[1] if event_stats[1] else 0,
                'error_count': event_stats[2] if event_stats[2] else 0
            },
            'inspections': {
                'count': inspection_stats[0] if inspection_stats[0] else 0,
                'compliant_count': inspection_stats[1] if inspection_stats[1] else 0,
                'compliance_rate': (inspection_stats[1] / inspection_stats[0] * 100) if inspection_stats[0] > 0 else 0
            }
        }

        # 存储统计结果
        self.cur.execute("""
            INSERT INTO safety_statistics
            (device_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, statistic_type, time_window) DO UPDATE
            SET statistics = EXCLUDED.statistics
        """, (device_id, 'safety_statistics', end_time,
              json.dumps(statistics)))
        self.conn.commit()

        return statistics

    def find_non_compliant_devices(self, time_window: timedelta = timedelta(days=30)) -> List[Dict]:
        """查找不合规设备"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.cur.execute("""
            SELECT DISTINCT device_id, device_name, sil_level
            FROM safety_devices
            WHERE device_id IN (
                SELECT DISTINCT device_id
                FROM safety_inspections
                WHERE compliance_status != 'compliant'
                  AND timestamp >= %s
                  AND timestamp <= %s
            )
        """, (start_time, end_time))

        devices = []
        for row in self.cur.fetchall():
            devices.append({
                'device_id': row[0],
                'device_name': row[1],
                'sil_level': row[2]
            })
        return devices

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()
```

---

## 7. 参考文献

### 7.1 标准文档

- IEC 61508:2010 Functional safety
- IEC 60335-1:2020 Household and similar electrical appliances
- GB/T 20438 功能安全标准

### 7.2 技术文档

- 安全代码实现最佳实践
- 功能安全设计指南
- PostgreSQL JSONB文档

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展安全数据存储和分析功能，新增PostgreSQL存储方案）
