# HL7 Schema转换体系

## 📑 目录

- [HL7 Schema转换体系](#hl7-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. HL7到FHIR转换](#2-hl7到fhir转换)
  - [3. FHIR到HL7转换](#3-fhir到hl7转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. HL7数据存储与分析](#6-hl7数据存储与分析)
    - [6.1 PostgreSQL HL7数据存储](#61-postgresql-hl7数据存储)
    - [6.2 HL7数据分析查询](#62-hl7数据分析查询)

---

## 1. 转换体系概述

HL7 Schema转换体系支持HL7消息、FHIR资源、
数据库存储之间的转换。

### 1.1 转换目标

1. **HL7到FHIR转换**：HL7 v2消息到FHIR资源
2. **FHIR到HL7转换**：FHIR资源到HL7 v2消息
3. **数据到数据库转换**：HL7消息到PostgreSQL存储

---

## 2. HL7到FHIR转换

**转换规则**：

- HL7 ADT^A08 → FHIR Patient
- HL7 ORU^R01 → FHIR Observation
- HL7 ORM^O01 → FHIR MedicationRequest

**转换示例**：

```python
def convert_hl7_adt_to_fhir_patient(hl7_message: str) -> dict:
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

## 3. FHIR到HL7转换

**转换规则**：

- FHIR Patient → HL7 ADT^A08
- FHIR Observation → HL7 ORU^R01
- FHIR MedicationRequest → HL7 ORM^O01

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

## 4. 转换工具

- **HL7转换器**：HL7 MLLP、HL7 API
- **FHIR转换器**：HAPI FHIR、Firely
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的消息完整性、字段一致性和患者信息一致性。

---

## 6. HL7数据存储与分析

### 6.1 PostgreSQL HL7数据存储

**HL7数据存储方案**：

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

class HL7Storage:
    """HL7数据存储系统 - 增强错误处理"""

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
            logger.info("HL7Storage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing HL7Storage: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize HL7Storage: {e}") from e

    def _create_tables(self):
        """创建HL7数据表"""
        # HL7消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS hl7_messages (
                id BIGSERIAL PRIMARY KEY,
                message_type VARCHAR(20) NOT NULL,
                message_control_id VARCHAR(20) UNIQUE NOT NULL,
                message_content TEXT NOT NULL,
                sending_application VARCHAR(180),
                sending_facility VARCHAR(180),
                receiving_application VARCHAR(180),
                receiving_facility VARCHAR(180),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)

        # HL7段表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS hl7_segments (
                id BIGSERIAL PRIMARY KEY,
                message_id BIGINT NOT NULL,
                segment_type VARCHAR(3) NOT NULL,
                segment_content TEXT NOT NULL,
                segment_order INTEGER NOT NULL,
                FOREIGN KEY (message_id) REFERENCES hl7_messages(id)
            )
        """)

        # HL7字段表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS hl7_fields (
                id BIGSERIAL PRIMARY KEY,
                segment_id BIGINT NOT NULL,
                field_position INTEGER NOT NULL,
                field_value TEXT,
                FOREIGN KEY (segment_id) REFERENCES hl7_segments(id)
            )
        """)

        # HL7消息日志表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS hl7_message_logs (
                id BIGSERIAL PRIMARY KEY,
                message_control_id VARCHAR(20) NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                processing_status VARCHAR(20),
                error_message TEXT,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_hl7_messages_type
            ON hl7_messages(message_type)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_hl7_messages_control_id
            ON hl7_messages(message_control_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_hl7_segments_message_id
            ON hl7_segments(message_id)
        """)

        self.conn.commit()

    def store_message(self, message_type: str, message_control_id: str,
                     message_content: str, sending_app: str = None,
                     sending_facility: str = None) -> int:
        """存储HL7消息 - 增强错误处理"""
        # 输入验证
        if not message_type:
            raise ValueError("Message type cannot be empty")

        if not isinstance(message_type, str):
            raise TypeError(f"Message type must be a string, got {type(message_type)}")

        if len(message_type) > 20:
            raise ValueError(f"Message type too long: {len(message_type)} (max 20)")

        if not message_control_id:
            raise ValueError("Message control ID cannot be empty")

        if not isinstance(message_control_id, str):
            raise TypeError(f"Message control ID must be a string, got {type(message_control_id)}")

        if len(message_control_id) > 20:
            raise ValueError(f"Message control ID too long: {len(message_control_id)} (max 20)")

        if not message_content:
            raise ValueError("Message content cannot be empty")

        if not isinstance(message_content, str):
            raise TypeError(f"Message content must be a string, got {type(message_content)}")

        if sending_app is not None and len(sending_app) > 180:
            raise ValueError(f"Sending application too long: {len(sending_app)} (max 180)")

        if sending_facility is not None and len(sending_facility) > 180:
            raise ValueError(f"Sending facility too long: {len(sending_facility)} (max 180)")

        try:
            self.cur.execute("""
                INSERT INTO hl7_messages (
                    message_type, message_control_id, message_content,
                    sending_application, sending_facility
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (message_control_id) DO NOTHING
                RETURNING id
            """, (message_type, message_control_id, message_content,
                  sending_app, sending_facility))

            result = self.cur.fetchone()
            self.conn.commit()

            if result:
                logger.info(f"Stored HL7 message: {message_control_id}")
                return result[0]
            else:
                logger.warning(f"HL7 message {message_control_id} already exists")
                return None

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing HL7 message: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate message control ID or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing HL7 message: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing HL7 message: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store HL7 message: {e}") from e

    def get_message(self, message_control_id: str) -> Optional[str]:
        """获取HL7消息"""
        self.cur.execute("""
            SELECT message_content
            FROM hl7_messages
            WHERE message_control_id = %s
        """, (message_control_id,))
        result = self.cur.fetchone()
        return result[0] if result else None

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 HL7数据分析查询

**查询示例**：

```python
# 查询ADT消息统计
def get_adt_statistics(self, start_date: datetime):
    """查询ADT消息统计"""
    self.cur.execute("""
        SELECT message_type, COUNT(*) as count
        FROM hl7_messages
        WHERE message_type LIKE 'ADT%' AND created_at >= %s
        GROUP BY message_type
        ORDER BY count DESC
    """, (start_date,))
    return self.cur.fetchall()

# 查询消息处理统计
def get_message_processing_statistics(self):
    """查询消息处理统计"""
    self.cur.execute("""
        SELECT processing_status, COUNT(*) as count,
               AVG(processing_time_ms) as avg_time
        FROM hl7_message_logs
        GROUP BY processing_status
    """)
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
