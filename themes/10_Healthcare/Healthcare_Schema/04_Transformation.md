# 医疗信息系统Schema转换体系

## 📑 目录

- [医疗信息系统Schema转换体系](#医疗信息系统schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. FHIR到HL7转换](#2-fhir到hl7转换)
  - [3. HL7到FHIR转换](#3-hl7到fhir转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 医疗数据存储与分析](#6-医疗数据存储与分析)
    - [6.1 PostgreSQL医疗数据存储](#61-postgresql医疗数据存储)
    - [6.2 医疗数据分析查询](#62-医疗数据分析查询)

---

## 1. 转换体系概述

医疗信息系统Schema转换体系支持FHIR资源、HL7消息、
数据库存储之间的转换。

### 1.1 转换目标

1. **FHIR到HL7转换**：FHIR资源到HL7 v2消息
2. **HL7到FHIR转换**：HL7 v2消息到FHIR资源
3. **数据到数据库转换**：医疗数据到PostgreSQL存储

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
        "HIS",
        "HOSPITAL",
        "EHR",
        "CLINIC",
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
        fhir_patient.get("identifier", [{}])[0].get("value", ""),
        "",
        format_name(fhir_patient.get("name", [{}])[0]),
        format_birth_date(fhir_patient.get("birthDate", "")),
        fhir_patient.get("gender", "").upper(),
        "",
        format_address(fhir_patient.get("address", [{}])[0])
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

验证转换的数据完整性、编码一致性和患者信息一致性。

---

## 6. 医疗数据存储与分析

### 6.1 PostgreSQL医疗数据存储

**医疗数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class HealthcareStorage:
    """医疗数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建医疗数据表"""
        # 患者信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id BIGSERIAL PRIMARY KEY,
                patient_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                gender VARCHAR(1),
                birth_date DATE,
                id_number VARCHAR(18),
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                insurance_type VARCHAR(20),
                insurance_number VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 临床数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS clinical_data (
                id BIGSERIAL PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                encounter_id VARCHAR(20) NOT NULL,
                recorded_at TIMESTAMP NOT NULL,
                data_type VARCHAR(50) NOT NULL,
                data_content JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)

        # 医疗记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id BIGSERIAL PRIMARY KEY,
                record_id VARCHAR(20) UNIQUE NOT NULL,
                patient_id VARCHAR(20) NOT NULL,
                encounter_id VARCHAR(20) NOT NULL,
                record_type VARCHAR(50) NOT NULL,
                record_content JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)

        # 诊断记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS diagnoses (
                id BIGSERIAL PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                encounter_id VARCHAR(20) NOT NULL,
                diagnosis_code VARCHAR(20) NOT NULL,
                diagnosis_name VARCHAR(200) NOT NULL,
                diagnosis_date DATE NOT NULL,
                icd_version VARCHAR(10),
                severity VARCHAR(20),
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)

        # 用药记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id BIGSERIAL PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                encounter_id VARCHAR(20) NOT NULL,
                medication_name VARCHAR(200) NOT NULL,
                medication_code VARCHAR(20),
                dosage VARCHAR(100) NOT NULL,
                frequency VARCHAR(50) NOT NULL,
                route VARCHAR(20) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                prescriber VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_patients_patient_id
            ON patients(patient_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_clinical_data_patient_id
            ON clinical_data(patient_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_medical_records_patient_id
            ON medical_records(patient_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_diagnoses_patient_id
            ON diagnoses(patient_id)
        """)

        self.conn.commit()

    def store_patient(self, patient_data: Dict) -> int:
        """存储患者信息"""
        self.cur.execute("""
            INSERT INTO patients (
                patient_id, name, gender, birth_date, id_number,
                phone, email, address, insurance_type, insurance_number
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (patient_id) DO UPDATE SET
                name = EXCLUDED.name,
                gender = EXCLUDED.gender,
                birth_date = EXCLUDED.birth_date,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                address = EXCLUDED.address,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            patient_data.get("patient_id"),
            patient_data.get("name"),
            patient_data.get("gender"),
            patient_data.get("birth_date"),
            patient_data.get("id_number"),
            patient_data.get("phone"),
            patient_data.get("email"),
            patient_data.get("address"),
            patient_data.get("insurance_type"),
            patient_data.get("insurance_number")
        ))
        return self.cur.fetchone()[0]

    def store_clinical_data(self, clinical_data: Dict) -> int:
        """存储临床数据"""
        self.cur.execute("""
            INSERT INTO clinical_data (
                patient_id, encounter_id, recorded_at,
                data_type, data_content
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            clinical_data.get("patient_id"),
            clinical_data.get("encounter_id"),
            clinical_data.get("recorded_at"),
            clinical_data.get("data_type"),
            json.dumps(clinical_data.get("data_content"))
        ))
        return self.cur.fetchone()[0]

    def store_diagnosis(self, diagnosis_data: Dict) -> int:
        """存储诊断记录"""
        self.cur.execute("""
            INSERT INTO diagnoses (
                patient_id, encounter_id, diagnosis_code,
                diagnosis_name, diagnosis_date, icd_version,
                severity, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            diagnosis_data.get("patient_id"),
            diagnosis_data.get("encounter_id"),
            diagnosis_data.get("diagnosis_code"),
            diagnosis_data.get("diagnosis_name"),
            diagnosis_data.get("diagnosis_date"),
            diagnosis_data.get("icd_version"),
            diagnosis_data.get("severity"),
            diagnosis_data.get("status")
        ))
        return self.cur.fetchone()[0]

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 医疗数据分析查询

**查询示例**：

```python
# 查询患者诊断统计
def get_diagnosis_statistics(self, start_date: str, end_date: str):
    """查询诊断统计"""
    self.cur.execute("""
        SELECT diagnosis_code, diagnosis_name, COUNT(*) as count
        FROM diagnoses
        WHERE diagnosis_date BETWEEN %s AND %s
        GROUP BY diagnosis_code, diagnosis_name
        ORDER BY count DESC
        LIMIT 10
    """, (start_date, end_date))
    return self.cur.fetchall()

# 查询用药统计
def get_medication_statistics(self, medication_name: str):
    """查询用药统计"""
    self.cur.execute("""
        SELECT COUNT(*) as patient_count,
               AVG(EXTRACT(EPOCH FROM (end_date - start_date))/86400) as avg_days
        FROM medications
        WHERE medication_name = %s
    """, (medication_name,))
    return self.cur.fetchone()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
