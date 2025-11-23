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

## 2. HL7/FHIR转换实现

### 2.1 HL7消息解析器

**完整的HL7消息解析实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class HL7Parser:
    """HL7消息解析器 - 完整实现"""

    def __init__(self):
        self.field_separator = "|"
        self.component_separator = "^"
        self.repetition_separator = "~"
        self.escape_character = "\\"
        self.sub_component_separator = "&"

    def parse_message(self, hl7_message: str) -> Dict:
        """解析HL7消息"""
        segments = hl7_message.split("\r")
        if not segments:
            segments = hl7_message.split("\n")

        parsed_segments = {}

        for segment in segments:
            if not segment.strip():
                continue

            segment_type = segment.split(self.field_separator)[0]
            parsed_segments[segment_type] = self.parse_segment(segment)

        return parsed_segments

    def parse_segment(self, segment: str) -> Dict:
        """解析单个段"""
        fields = segment.split(self.field_separator)
        segment_type = fields[0]

        parsed = {
            "segment_type": segment_type,
            "fields": []
        }

        for i, field in enumerate(fields[1:], start=1):
            if self.component_separator in field:
                # 复合字段
                components = field.split(self.component_separator)
                parsed["fields"].append({
                    "field_number": i,
                    "type": "composite",
                    "components": components
                })
            else:
                parsed["fields"].append({
                    "field_number": i,
                    "type": "simple",
                    "value": field
                })

        return parsed

    def parse_msh_segment(self, msh_segment: str) -> Dict:
        """解析MSH段（消息头）"""
        fields = msh_segment.split(self.field_separator)

        return {
            "segment_type": "MSH",
            "field_separator": fields[1] if len(fields) > 1 else "|",
            "encoding_characters": fields[2] if len(fields) > 2 else "^~\\&",
            "sending_application": fields[3] if len(fields) > 3 else "",
            "sending_facility": fields[4] if len(fields) > 4 else "",
            "receiving_application": fields[5] if len(fields) > 5 else "",
            "receiving_facility": fields[6] if len(fields) > 6 else "",
            "date_time": fields[7] if len(fields) > 7 else "",
            "security": fields[8] if len(fields) > 8 else "",
            "message_type": fields[9] if len(fields) > 9 else "",
            "message_control_id": fields[10] if len(fields) > 10 else "",
            "processing_id": fields[11] if len(fields) > 11 else "",
            "version_id": fields[12] if len(fields) > 12 else ""
        }

    def parse_pid_segment(self, pid_segment: str) -> Dict:
        """解析PID段（患者识别）"""
        fields = pid_segment.split(self.field_separator)

        # 解析患者ID（字段3）
        patient_id = ""
        if len(fields) > 3:
            patient_id_components = fields[3].split(self.component_separator)
            patient_id = patient_id_components[0] if patient_id_components else ""

        # 解析患者姓名（字段5）
        patient_name = {}
        if len(fields) > 5:
            name_components = fields[5].split(self.component_separator)
            patient_name = {
                "family": name_components[0] if len(name_components) > 0 else "",
                "given": name_components[1] if len(name_components) > 1 else "",
                "middle": name_components[2] if len(name_components) > 2 else ""
            }

        return {
            "segment_type": "PID",
            "set_id": fields[1] if len(fields) > 1 else "",
            "patient_id": patient_id,
            "patient_name": patient_name,
            "mother_maiden_name": fields[6] if len(fields) > 6 else "",
            "date_of_birth": fields[7] if len(fields) > 7 else "",
            "sex": fields[8] if len(fields) > 8 else "",
            "race": fields[10] if len(fields) > 10 else "",
            "address": fields[11] if len(fields) > 11 else "",
            "phone": fields[13] if len(fields) > 13 else ""
        }

    def parse_obr_segment(self, obr_segment: str) -> Dict:
        """解析OBR段（观察请求）"""
        fields = obr_segment.split(self.field_separator)

        return {
            "segment_type": "OBR",
            "set_id": fields[1] if len(fields) > 1 else "",
            "placer_order_number": fields[2] if len(fields) > 2 else "",
            "filler_order_number": fields[3] if len(fields) > 3 else "",
            "universal_service_id": fields[4] if len(fields) > 4 else "",
            "priority": fields[5] if len(fields) > 5 else "",
            "requested_date_time": fields[6] if len(fields) > 6 else "",
            "observation_date_time": fields[7] if len(fields) > 7 else "",
            "observation_end_date_time": fields[8] if len(fields) > 8 else "",
            "collector_identifier": fields[10] if len(fields) > 10 else "",
            "specimen_action_code": fields[11] if len(fields) > 11 else ""
        }

    def parse_obx_segment(self, obx_segment: str) -> Dict:
        """解析OBX段（观察结果）"""
        fields = obx_segment.split(self.field_separator)

        return {
            "segment_type": "OBX",
            "set_id": fields[1] if len(fields) > 1 else "",
            "value_type": fields[2] if len(fields) > 2 else "",
            "observation_id": fields[3] if len(fields) > 3 else "",
            "observation_sub_id": fields[4] if len(fields) > 4 else "",
            "observation_value": fields[5] if len(fields) > 5 else "",
            "units": fields[6] if len(fields) > 6 else "",
            "references_range": fields[7] if len(fields) > 7 else "",
            "abnormal_flags": fields[8] if len(fields) > 8 else "",
            "probability": fields[9] if len(fields) > 9 else "",
            "nature_of_abnormal_test": fields[10] if len(fields) > 10 else "",
            "observation_result_status": fields[11] if len(fields) > 11 else "",
            "date_time_of_observation": fields[14] if len(fields) > 14 else ""
        }
```

### 2.2 FHIR资源转换器

**完整的FHIR资源转换实现**：

```python
class FHIRConverter:
    """FHIR资源转换器 - 完整实现"""

    def __init__(self):
        self.base_url = "http://fhir.example.org"

    def convert_hl7_to_fhir_patient(self, hl7_message: str) -> Dict:
        """将HL7 ADT消息转换为FHIR Patient资源"""
        parser = HL7Parser()
        parsed = parser.parse_message(hl7_message)

        pid = parsed.get("PID")
        if not pid:
            raise ValueError("PID segment not found")

        # 构建FHIR Patient资源
        fhir_patient = {
            "resourceType": "Patient",
            "id": pid.get("patient_id", str(uuid.uuid4())),
            "identifier": [{
                "system": f"{self.base_url}/patients",
                "value": pid.get("patient_id", "")
            }],
            "name": [{
                "family": pid.get("patient_name", {}).get("family", ""),
                "given": [pid.get("patient_name", {}).get("given", "")]
            }],
            "gender": self._map_hl7_gender_to_fhir(pid.get("sex", "")),
            "birthDate": self._parse_hl7_date(pid.get("date_of_birth", "")),
            "address": [self._parse_hl7_address(pid.get("address", ""))]
        }

        # 添加电话
        if pid.get("phone"):
            fhir_patient["telecom"] = [{
                "system": "phone",
                "value": pid.get("phone")
            }]

        return fhir_patient

    def convert_hl7_to_fhir_observation(self, hl7_message: str) -> Dict:
        """将HL7 ORU消息转换为FHIR Observation资源"""
        parser = HL7Parser()
        parsed = parser.parse_message(hl7_message)

        pid = parsed.get("PID")
        obr = parsed.get("OBR")
        obx_segments = [seg for seg_type, seg in parsed.items() if seg_type == "OBX"]

        if not pid or not obr:
            raise ValueError("PID or OBR segment not found")

        # 构建FHIR Observation资源
        fhir_observation = {
            "resourceType": "Observation",
            "id": str(uuid.uuid4()),
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": obr.get("universal_service_id", ""),
                    "display": obr.get("universal_service_id", "")
                }]
            },
            "subject": {
                "reference": f"Patient/{pid.get('patient_id', '')}"
            },
            "effectiveDateTime": self._parse_hl7_date_time(obr.get("observation_date_time", "")),
            "performer": [{
                "reference": f"Practitioner/{obr.get('collector_identifier', '')}"
            }]
        }

        # 添加观察值
        if obx_segments:
            obx = obx_segments[0]  # 使用第一个OBX段
            value_type = obx.get("value_type", "")
            observation_value = obx.get("observation_value", "")

            if value_type == "NM":  # 数值
                fhir_observation["valueQuantity"] = {
                    "value": float(observation_value) if observation_value else None,
                    "unit": obx.get("units", ""),
                    "system": "http://unitsofmeasure.org",
                    "code": obx.get("units", "")
                }
            elif value_type == "ST" or value_type == "TX":  # 字符串
                fhir_observation["valueString"] = observation_value
            elif value_type == "CE":  # 编码元素
                fhir_observation["valueCodeableConcept"] = {
                    "coding": [{
                        "code": observation_value,
                        "display": observation_value
                    }]
                }

        return fhir_observation

    def convert_fhir_patient_to_hl7(self, fhir_patient: Dict) -> str:
        """将FHIR Patient资源转换为HL7 ADT消息"""
        hl7_segments = []

        # MSH段
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
            str(uuid.uuid4()),
            "P",
            "2.5"
        ]
        hl7_segments.append(self.field_separator.join(msh))

        # PID段
        patient_id = fhir_patient.get("id", "")
        identifier = fhir_patient.get("identifier", [{}])[0] if fhir_patient.get("identifier") else {}
        name = fhir_patient.get("name", [{}])[0] if fhir_patient.get("name") else {}

        pid = [
            "PID",
            "1",
            "",
            f"{patient_id}^{identifier.get('value', '')}",
            "",
            f"{name.get('family', '')}^{name.get('given', [''])[0] if name.get('given') else ''}",
            "",
            self._format_fhir_date_to_hl7(fhir_patient.get("birthDate", "")),
            self._map_fhir_gender_to_hl7(fhir_patient.get("gender", "")),
            "",
            "",
            self._format_fhir_address_to_hl7(fhir_patient.get("address", [{}])[0] if fhir_patient.get("address") else {})
        ]
        hl7_segments.append(self.field_separator.join(pid))

        return "\r".join(hl7_segments)

    def _map_hl7_gender_to_fhir(self, hl7_gender: str) -> str:
        """映射HL7性别代码到FHIR"""
        mapping = {
            "M": "male",
            "F": "female",
            "O": "other",
            "U": "unknown"
        }
        return mapping.get(hl7_gender.upper(), "unknown")

    def _map_fhir_gender_to_hl7(self, fhir_gender: str) -> str:
        """映射FHIR性别到HL7代码"""
        mapping = {
            "male": "M",
            "female": "F",
            "other": "O",
            "unknown": "U"
        }
        return mapping.get(fhir_gender.lower(), "U")

    def _parse_hl7_date(self, hl7_date: str) -> Optional[str]:
        """解析HL7日期格式"""
        if not hl7_date or len(hl7_date) < 8:
            return None

        try:
            if len(hl7_date) == 8:
                return f"{hl7_date[:4]}-{hl7_date[4:6]}-{hl7_date[6:8]}"
            elif len(hl7_date) >= 14:
                return f"{hl7_date[:4]}-{hl7_date[4:6]}-{hl7_date[6:8]}T{hl7_date[8:10]}:{hl7_date[10:12]}:{hl7_date[12:14]}Z"
        except Exception:
            pass

        return None

    def _parse_hl7_date_time(self, hl7_date_time: str) -> Optional[str]:
        """解析HL7日期时间格式"""
        return self._parse_hl7_date(hl7_date_time)

    def _format_fhir_date_to_hl7(self, fhir_date: str) -> str:
        """格式化FHIR日期为HL7格式"""
        if not fhir_date:
            return ""

        # 移除时间部分
        date_part = fhir_date.split("T")[0]
        return date_part.replace("-", "")

    def _parse_hl7_address(self, hl7_address: str) -> Dict:
        """解析HL7地址"""
        if not hl7_address:
            return {}

        components = hl7_address.split(self.component_separator)
        return {
            "line": [components[0]] if len(components) > 0 and components[0] else [],
            "city": components[2] if len(components) > 2 else "",
            "state": components[3] if len(components) > 3 else "",
            "postalCode": components[4] if len(components) > 4 else "",
            "country": components[5] if len(components) > 5 else ""
        }

    def _format_fhir_address_to_hl7(self, fhir_address: Dict) -> str:
        """格式化FHIR地址为HL7格式"""
        if not fhir_address:
            return ""

        line = fhir_address.get("line", [""])[0] if fhir_address.get("line") else ""
        city = fhir_address.get("city", "")
        state = fhir_address.get("state", "")
        postal_code = fhir_address.get("postalCode", "")
        country = fhir_address.get("country", "")

        return f"{line}^{city}^{state}^{postal_code}^{country}"
```

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

**完整的医疗数据分析类**：

```python
class HealthcareDataAnalyzer:
    """医疗数据分析器 - 完整实现"""

    def __init__(self, storage):
        self.storage = storage

    def analyze_patient_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析患者统计"""
        cursor = self.storage.conn.cursor()

        # 患者总数
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]

        # 按性别统计
        cursor.execute("""
            SELECT gender, COUNT(*) as count
            FROM patients
            GROUP BY gender
        """)
        gender_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 按年龄段统计
        cursor.execute("""
            SELECT
                CASE
                    WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 18 THEN '0-17'
                    WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 30 THEN '18-29'
                    WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 50 THEN '30-49'
                    WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 70 THEN '50-69'
                    ELSE '70+'
                END as age_group,
                COUNT(*) as count
            FROM patients
            WHERE birth_date IS NOT NULL
            GROUP BY age_group
            ORDER BY age_group
        """)
        age_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 新增患者统计
        cursor.execute("""
            SELECT COUNT(*)
            FROM patients
            WHERE created_at >= %s AND created_at <= %s
        """, (start_date, end_date))
        new_patients = cursor.fetchone()[0]

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_patients": total_patients,
            "new_patients": new_patients,
            "gender_distribution": gender_stats,
            "age_distribution": age_stats
        }

    def analyze_diagnosis_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析诊断统计"""
        cursor = self.storage.conn.cursor()

        # 最常见诊断
        cursor.execute("""
            SELECT
                diagnosis_code,
                diagnosis_name,
                COUNT(*) as diagnosis_count
            FROM diagnoses
            WHERE diagnosis_date >= %s AND diagnosis_date <= %s
            GROUP BY diagnosis_code, diagnosis_name
            ORDER BY diagnosis_count DESC
            LIMIT 10
        """, (start_date, end_date))

        top_diagnoses = []
        for row in cursor.fetchall():
            top_diagnoses.append({
                "code": row[0],
                "name": row[1],
                "count": row[2]
            })

        # 按严重程度统计
        cursor.execute("""
            SELECT
                severity,
                COUNT(*) as count
            FROM diagnoses
            WHERE diagnosis_date >= %s AND diagnosis_date <= %s
            GROUP BY severity
        """, (start_date, end_date))

        severity_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 诊断趋势（按月）
        cursor.execute("""
            SELECT
                DATE_TRUNC('month', diagnosis_date) as month,
                COUNT(*) as count
            FROM diagnoses
            WHERE diagnosis_date >= %s AND diagnosis_date <= %s
            GROUP BY month
            ORDER BY month
        """, (start_date, end_date))

        monthly_trends = []
        for row in cursor.fetchall():
            monthly_trends.append({
                "month": row[0].isoformat() if row[0] else None,
                "count": row[1]
            })

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "top_diagnoses": top_diagnoses,
            "severity_distribution": severity_stats,
            "monthly_trends": monthly_trends
        }

    def analyze_medication_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析用药统计"""
        cursor = self.storage.conn.cursor()

        # 最常用药物
        cursor.execute("""
            SELECT
                medication_name,
                medication_code,
                COUNT(*) as prescription_count,
                COUNT(DISTINCT patient_id) as patient_count
            FROM medications
            WHERE start_date >= %s AND start_date <= %s
            GROUP BY medication_name, medication_code
            ORDER BY prescription_count DESC
            LIMIT 10
        """, (start_date, end_date))

        top_medications = []
        for row in cursor.fetchall():
            top_medications.append({
                "name": row[0],
                "code": row[1],
                "prescription_count": row[2],
                "patient_count": row[3]
            })

        # 按给药途径统计
        cursor.execute("""
            SELECT
                route,
                COUNT(*) as count
            FROM medications
            WHERE start_date >= %s AND start_date <= %s
            GROUP BY route
        """, (start_date, end_date))

        route_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 用药趋势（按月）
        cursor.execute("""
            SELECT
                DATE_TRUNC('month', start_date) as month,
                COUNT(*) as count
            FROM medications
            WHERE start_date >= %s AND start_date <= %s
            GROUP BY month
            ORDER BY month
        """, (start_date, end_date))

        monthly_trends = []
        for row in cursor.fetchall():
            monthly_trends.append({
                "month": row[0].isoformat() if row[0] else None,
                "count": row[1]
            })

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "top_medications": top_medications,
            "route_distribution": route_stats,
            "monthly_trends": monthly_trends
        }

    def analyze_clinical_data_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """分析临床数据统计"""
        cursor = self.storage.conn.cursor()

        # 按数据类型统计
        cursor.execute("""
            SELECT
                data_type,
                COUNT(*) as count
            FROM clinical_data
            WHERE recorded_at >= %s AND recorded_at <= %s
            GROUP BY data_type
            ORDER BY count DESC
        """, (start_date, end_date))

        data_type_stats = []
        for row in cursor.fetchall():
            data_type_stats.append({
                "type": row[0],
                "count": row[1]
            })

        # 数据记录趋势（按天）
        cursor.execute("""
            SELECT
                DATE(recorded_at) as date,
                COUNT(*) as count
            FROM clinical_data
            WHERE recorded_at >= %s AND recorded_at <= %s
            GROUP BY date
            ORDER BY date
        """, (start_date, end_date))

        daily_trends = []
        for row in cursor.fetchall():
            daily_trends.append({
                "date": row[0].isoformat() if row[0] else None,
                "count": row[1]
            })

        return {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data_type_distribution": data_type_stats,
            "daily_trends": daily_trends
        }

    def generate_healthcare_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """生成医疗综合报告"""
        patient_stats = self.analyze_patient_statistics(start_date, end_date)
        diagnosis_stats = self.analyze_diagnosis_statistics(start_date, end_date)
        medication_stats = self.analyze_medication_statistics(start_date, end_date)
        clinical_stats = self.analyze_clinical_data_statistics(start_date, end_date)

        return {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "patient_statistics": patient_stats,
            "diagnosis_statistics": diagnosis_stats,
            "medication_statistics": medication_stats,
            "clinical_data_statistics": clinical_stats,
            "summary": {
                "total_patients": patient_stats.get("total_patients", 0),
                "new_patients": patient_stats.get("new_patients", 0),
                "top_diagnosis": diagnosis_stats.get("top_diagnoses", [{}])[0] if diagnosis_stats.get("top_diagnoses") else None,
                "top_medication": medication_stats.get("top_medications", [{}])[0] if medication_stats.get("top_medications") else None
            }
        }
```

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
