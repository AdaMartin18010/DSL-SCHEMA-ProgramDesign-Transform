# FHIR Schema转换体系

## 📑 目录

- [FHIR Schema转换体系](#fhir-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. FHIR到HL7转换](#2-fhir到hl7转换)
  - [3. HL7到FHIR转换](#3-hl7到fhir转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. FHIR数据存储与分析](#6-fhir数据存储与分析)
    - [6.1 PostgreSQL FHIR数据存储](#61-postgresql-fhir数据存储)
    - [6.2 FHIR数据分析查询](#62-fhir数据分析查询)

---

## 1. 转换体系概述

FHIR Schema转换体系支持FHIR资源、HL7消息、
数据库存储之间的转换。

### 1.1 转换目标

1. **FHIR到HL7转换**：FHIR资源到HL7 v2消息
2. **HL7到FHIR转换**：HL7 v2消息到FHIR资源
3. **数据到数据库转换**：FHIR资源到PostgreSQL存储

---

## 2. FHIR到HL7转换

**转换规则**：

- FHIR Patient → HL7 ADT^A08
- FHIR Condition → HL7 ORU^R01
- FHIR Observation → HL7 ORU^R01

**转换示例**：

```python
def convert_fhir_patient_to_hl7(fhir_patient: dict) -> str:
    """将FHIR Patient资源转换为HL7 ADT消息"""
    hl7_message = []

    # MSH段：消息头
    msh = [
        "MSH",
        "^~\\&",
        "FHIR",
        "SYSTEM",
        "HL7",
        "SYSTEM",
        datetime.now().strftime("%Y%m%d%H%M%S"),
        "",
        "ADT^A08^ADT_A01",
        generate_message_id(),
        "P",
        "2.5"
    ]
    hl7_message.append("|".join(msh))

    # PID段：患者识别
    pid = [
        "PID",
        "1",
        fhir_patient.get("id", ""),
        extract_identifier(fhir_patient.get("identifier", [])),
        "",
        format_fhir_name(fhir_patient.get("name", [{}])[0]),
        parse_fhir_date(fhir_patient.get("birthDate", "")),
        fhir_patient.get("gender", "").upper(),
        "",
        format_fhir_address(fhir_patient.get("address", [{}])[0])
    ]
    hl7_message.append("|".join(pid))

    return "\r".join(hl7_message)
```

---

## 3. HL7到FHIR转换

**转换规则**：

- HL7 ADT^A08 → FHIR Patient
- HL7 ORU^R01 → FHIR Observation
- HL7 ORU^R01 → FHIR Condition

**转换示例**：

```python
def convert_hl7_to_fhir_patient(hl7_message: str) -> dict:
    """将HL7 ADT消息转换为FHIR Patient资源"""
    segments = hl7_message.split("\r")
    pid_segment = None

    for segment in segments:
        if segment.startswith("PID"):
            pid_segment = segment.split("|")
            break

    if not pid_segment:
        raise ValueError("PID segment not found")

    fhir_patient = {
        "resourceType": "Patient",
        "id": pid_segment[3] if len(pid_segment) > 3 else "",
        "identifier": [{
            "system": "http://hospital.example.org/patients",
            "value": pid_segment[3] if len(pid_segment) > 3 else ""
        }],
        "name": [parse_hl7_name(pid_segment[5])],
        "gender": pid_segment[8].lower() if len(pid_segment) > 8 else "",
        "birthDate": parse_hl7_date(pid_segment[7]) if len(pid_segment) > 7 else "",
        "address": [parse_hl7_address(pid_segment[11])] if len(pid_segment) > 11 else []
    }

    return fhir_patient
```

---

## 4. 转换工具

- **FHIR转换器**：HAPI FHIR、Firely
- **HL7转换器**：HL7 MLLP、HL7 API
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的资源完整性、编码一致性和患者信息一致性。

---

## 6. FHIR数据存储与分析

### 6.1 PostgreSQL FHIR数据存储

**FHIR数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

import psycopg2
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FHIRStorage:
    """FHIR数据存储系统 - 增强错误处理"""

    def __init__(self, connection_string: str):
        # 输入验证
        if not connection_string:
            raise ValueError("Connection string cannot be empty")

        if not isinstance(connection_string, str):
            raise TypeError(f"Connection string must be a string, got {type(connection_string)}")

        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("FHIRStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing FHIRStorage: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize FHIRStorage: {e}") from e

    def _create_tables(self):
        """创建FHIR数据表"""
        # FHIR资源表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS fhir_resources (
                id BIGSERIAL PRIMARY KEY,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(64) NOT NULL,
                resource_content JSONB NOT NULL,
                version_id VARCHAR(64),
                last_updated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(resource_type, resource_id)
            )
        """)

        # FHIR资源索引表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS fhir_resource_index (
                id BIGSERIAL PRIMARY KEY,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(64) NOT NULL,
                index_name VARCHAR(100) NOT NULL,
                index_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_type, resource_id)
                REFERENCES fhir_resources(resource_type, resource_id)
            )
        """)

        # FHIR API日志表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS fhir_api_logs (
                id BIGSERIAL PRIMARY KEY,
                request_method VARCHAR(10) NOT NULL,
                request_path TEXT NOT NULL,
                request_body JSONB,
                response_status INTEGER,
                response_body JSONB,
                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INTEGER
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_fhir_resources_type_id
            ON fhir_resources(resource_type, resource_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_fhir_resources_last_updated
            ON fhir_resources(last_updated DESC)
        """)

        self.conn.commit()

    def store_resource(self, resource_type: str, resource_id: str,
                      resource_content: Dict, version_id: str = None) -> int:
        """存储FHIR资源 - 增强错误处理"""
        # 输入验证
        if not resource_type:
            raise ValueError("Resource type cannot be empty")

        if not isinstance(resource_type, str):
            raise TypeError(f"Resource type must be a string, got {type(resource_type)}")

        if len(resource_type) > 50:
            raise ValueError(f"Resource type too long: {len(resource_type)} (max 50)")

        if not resource_id:
            raise ValueError("Resource ID cannot be empty")

        if not isinstance(resource_id, str):
            raise TypeError(f"Resource ID must be a string, got {type(resource_id)}")

        if len(resource_id) > 64:
            raise ValueError(f"Resource ID too long: {len(resource_id)} (max 64)")

        if not isinstance(resource_content, dict):
            raise TypeError(f"Resource content must be a dictionary, got {type(resource_content)}")

        if not resource_content:
            raise ValueError("Resource content cannot be empty")

        if version_id is not None and len(version_id) > 64:
            raise ValueError(f"Version ID too long: {len(version_id)} (max 64)")

        try:
            self.cur.execute("""
                INSERT INTO fhir_resources (
                    resource_type, resource_id, resource_content,
                    version_id, last_updated
                ) VALUES (%s, %s, %s::jsonb, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (resource_type, resource_id) DO UPDATE SET
                    resource_content = EXCLUDED.resource_content,
                    version_id = EXCLUDED.version_id,
                    last_updated = CURRENT_TIMESTAMP
                RETURNING id
            """, (resource_type, resource_id, json.dumps(resource_content), version_id))

            result = self.cur.fetchone()
            if not result:
                raise ValueError("Failed to store FHIR resource")

            self.conn.commit()
            logger.info(f"Stored FHIR resource: {resource_type}/{resource_id}")
            return result[0]

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing FHIR resource: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate resource or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing FHIR resource: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing FHIR resource: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store FHIR resource: {e}") from e

    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        """获取FHIR资源"""
        self.cur.execute("""
            SELECT resource_content
            FROM fhir_resources
            WHERE resource_type = %s AND resource_id = %s
        """, (resource_type, resource_id))
        result = self.cur.fetchone()
        return json.loads(result[0]) if result else None

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 FHIR数据分析查询

**查询示例**：

```python
# 查询Patient资源统计
def get_patient_statistics(self):
    """查询Patient资源统计"""
    self.cur.execute("""
        SELECT COUNT(*) as total_patients,
               COUNT(CASE WHEN resource_content->>'gender' = 'male' THEN 1 END) as male_count,
               COUNT(CASE WHEN resource_content->>'gender' = 'female' THEN 1 END) as female_count
        FROM fhir_resources
        WHERE resource_type = 'Patient'
    """)
    return self.cur.fetchone()

# 查询API调用统计
def get_api_statistics(self, start_time: datetime):
    """查询API调用统计"""
    self.cur.execute("""
        SELECT request_method, request_path,
               COUNT(*) as call_count,
               AVG(response_time_ms) as avg_response_time
        FROM fhir_api_logs
        WHERE request_time >= %s
        GROUP BY request_method, request_path
        ORDER BY call_count DESC
    """, (start_time,))
    return self.cur.fetchall()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
