# 医疗信息系统Schema实践案例

## 📑 目录

- [医疗信息系统Schema实践案例](#医疗信息系统schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：患者信息管理](#2-案例1患者信息管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：临床数据记录](#3-案例2临床数据记录)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：诊断记录管理](#4-案例3诊断记录管理)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：FHIR到HL7转换](#5-案例4fhir到hl7转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：医疗数据存储与分析系统](#6-案例5医疗数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)
  - [7. 案例6：远程医疗系统](#7-案例6远程医疗系统)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：智能诊断辅助系统](#8-案例7智能诊断辅助系统)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：药物管理系统](#9-案例8药物管理系统)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 Schema定义](#92-schema定义)
    - [9.3 实现代码](#93-实现代码)

---

## 1. 案例概述

本文档提供医疗信息系统Schema在实际应用中的实践案例。

---

## 2. 案例1：患者信息管理

### 2.1 场景描述

**应用场景**：
医院信息系统管理患者基本信息，使用FHIR Patient资源格式。

### 2.2 Schema定义

**患者信息Schema**：

```dsl
schema PatientInfo {
  patient_id: String @value("P1234567890") @required

  basic_info: {
    name: String @value("张三")
    gender: Enum { M } @value(M)
    birth_date: Date @value("1980-05-15") @format("YYYY-MM-DD")
    id_number: String @value("110101198005151234")
  } @required

  contact_info: {
    address: String @value("北京市朝阳区XX街道XX号")
    phone: String @value("13800138000")
    email: String @value("zhangsan@example.com")
  }

  insurance_info: {
    insurance_type: Enum { Public } @value(Public)
    insurance_number: String @value("BJ123456789")
    insurance_provider: String @value("北京市医保")
  }
} @standard("FHIR_R4")
```

---

## 3. 案例2：临床数据记录

### 3.1 场景描述

**应用场景**：
记录患者生命体征和实验室检查结果，使用FHIR Observation资源。

### 3.2 Schema定义

**临床数据Schema**：

```dsl
schema ClinicalData {
  patient_id: String @value("P1234567890") @required
  encounter_id: String @value("E9876543210") @required
  recorded_at: DateTime @value("2025-01-21T10:30:00") @required

  vital_signs: {
    temperature: Decimal @value(36.5) @unit("Celsius")
    blood_pressure: {
      systolic: Integer @value(120) @unit("mmHg")
      diastolic: Integer @value(80) @unit("mmHg")
    }
    heart_rate: Integer @value(72) @unit("bpm")
    respiratory_rate: Integer @value(18) @unit("breaths/min")
  }

  lab_results: [
    {
      test_name: String @value("血常规")
      test_code: String @value("CBC")
      result_value: String @value("正常")
      performed_at: DateTime @value("2025-01-21T09:00:00")
    }
  ]
} @standard("FHIR_R4")
```

---

## 4. 案例3：诊断记录管理

### 4.1 场景描述

**应用场景**：
记录患者诊断信息，使用FHIR Condition资源。

### 4.2 Schema定义

**诊断记录Schema**：

```dsl
schema DiagnosisRecord {
  record_id: String @value("D1234567890") @required
  patient_id: String @value("P1234567890") @required
  encounter_id: String @value("E9876543210") @required

  diagnosis: {
    diagnosis_code: String @value("I10") @required
    diagnosis_name: String @value("原发性高血压") @required
    diagnosis_date: Date @value("2025-01-21") @format("YYYY-MM-DD") @required
    icd_version: Enum { ICD10 } @value(ICD10) @required
    severity: Enum { Moderate } @value(Moderate)
    status: Enum { Confirmed } @value(Confirmed)
  } @required
} @standard("FHIR_R4")
```

---

## 5. 案例4：FHIR到HL7转换

### 5.1 场景描述

**应用场景**：
将FHIR Patient资源转换为HL7 ADT消息，用于与旧系统集成。

### 5.2 实现代码

详见 `04_Transformation.md` 第2章。

---

## 6. 案例5：医疗数据存储与分析系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储医疗数据，支持医疗质量分析和统计。

### 6.2 实现代码

详见 `04_Transformation.md` 第6章。

---

## 7. 案例6：远程医疗系统

### 7.1 场景描述

**业务背景**：
远程医疗系统支持患者通过视频、电话等方式
接受医生远程诊疗，实现医疗资源优化配置。

**技术挑战**：
- 需要实时音视频通信
- 需要患者数据同步
- 需要处方电子化
- 需要医疗记录存储

**解决方案**：
使用FHIR Encounter资源记录远程诊疗，
使用FHIR MedicationRequest资源记录处方，
使用HealthcareStorage存储远程医疗数据。

### 7.2 Schema定义

**远程医疗Schema**：

```dsl
schema TelemedicineEncounter {
  encounter_id: String @value("TELE-20250121-001") @required
  patient_id: String @value("P1234567890") @required
  practitioner_id: String @value("DOC-001") @required

  encounter_type: Enum { Telemedicine } @value(Telemedicine) @required
  encounter_status: Enum { InProgress } @value(InProgress) @required

  scheduled_period: {
    start: DateTime @value("2025-01-21T14:00:00") @required
    end: DateTime @value("2025-01-21T14:30:00")
  } @required

  communication_channel: {
    type: Enum { Video } @value(Video)
    platform: String @value("Zoom")
    meeting_id: String @value("123456789")
  } @required

  chief_complaint: String @value("头痛、发热")
  diagnosis: {
    diagnosis_code: String @value("R50.9")
    diagnosis_name: String @value("发热")
  }

  prescription: {
    medication_name: String @value("布洛芬")
    dosage: String @value("200mg")
    frequency: String @value("每日3次")
    duration: String @value("3天")
  }
} @standard("FHIR_R4")
```

### 7.3 实现代码

```python
from healthcare_storage import HealthcareStorage
from datetime import datetime

# 初始化存储
storage = HealthcareStorage("postgresql://user:password@localhost/healthcare_db")

# 创建远程医疗记录
telemedicine_data = {
    "patient_id": "P1234567890",
    "encounter_id": "TELE-20250121-001",
    "practitioner_id": "DOC-001",
    "encounter_type": "Telemedicine",
    "encounter_status": "Completed",
    "scheduled_start": datetime(2025, 1, 21, 14, 0, 0),
    "scheduled_end": datetime(2025, 1, 21, 14, 30, 0),
    "communication_channel": {
        "type": "Video",
        "platform": "Zoom",
        "meeting_id": "123456789"
    },
    "chief_complaint": "头痛、发热",
    "diagnosis_code": "R50.9",
    "diagnosis_name": "发热",
    "prescription": {
        "medication_name": "布洛芬",
        "dosage": "200mg",
        "frequency": "每日3次",
        "duration": "3天"
    }
}

# 存储远程医疗记录
encounter_id = storage.store_clinical_data(telemedicine_data)
print(f"Telemedicine encounter stored: {encounter_id}")

# 查询远程医疗记录
telemedicine_records = storage.query_encounters_by_patient("P1234567890", "Telemedicine")
print(f"Found {len(telemedicine_records)} telemedicine encounters")
```

---

## 8. 案例7：智能诊断辅助系统

### 8.1 场景描述

**业务背景**：
智能诊断辅助系统基于患者症状和检查结果，
提供诊断建议和风险评估，辅助医生做出诊断决策。

**技术挑战**：
- 需要症状数据标准化
- 需要检查结果分析
- 需要诊断规则引擎
- 需要风险评估算法

**解决方案**：
使用FHIR Observation资源记录症状和检查结果，
使用FHIR Condition资源记录诊断建议，
使用HealthcareStorage存储诊断数据。

### 8.2 Schema定义

**智能诊断Schema**：

```dsl
schema IntelligentDiagnosis {
  diagnosis_session_id: String @value("DIAG-20250121-001") @required
  patient_id: String @value("P1234567890") @required

  symptoms: [
    {
      symptom_code: String @value("R50.9") @required
      symptom_name: String @value("发热") @required
      severity: Enum { Moderate } @value(Moderate)
      duration: String @value("2天")
    },
    {
      symptom_code: String @value("R51")
      symptom_name: String @value("头痛")
      severity: Enum { Mild }
      duration: String @value("1天")
    }
  ] @required

  lab_results: [
    {
      test_name: String @value("血常规")
      test_code: String @value("CBC")
      result_value: String @value("白细胞计数: 12.5×10^9/L")
      abnormal_flag: Boolean @value(true)
    }
  ]

  ai_suggestions: [
    {
      suggested_diagnosis: String @value("上呼吸道感染")
      confidence_score: Decimal @value(0.85)
      risk_level: Enum { Low }
      recommended_tests: [String] @value(["C反应蛋白", "降钙素原"])
    }
  ] @required

  final_diagnosis: {
    diagnosis_code: String @value("J06.9")
    diagnosis_name: String @value("上呼吸道感染")
    confirmed_by: String @value("DOC-001")
    confirmed_at: DateTime @value("2025-01-21T15:00:00")
  }
} @standard("FHIR_R4")
```

### 8.3 实现代码

```python
# 创建智能诊断记录
diagnosis_data = {
    "patient_id": "P1234567890",
    "diagnosis_session_id": "DIAG-20250121-001",
    "symptoms": [
        {
            "symptom_code": "R50.9",
            "symptom_name": "发热",
            "severity": "Moderate",
            "duration": "2天"
        },
        {
            "symptom_code": "R51",
            "symptom_name": "头痛",
            "severity": "Mild",
            "duration": "1天"
        }
    ],
    "lab_results": [
        {
            "test_name": "血常规",
            "test_code": "CBC",
            "result_value": "白细胞计数: 12.5×10^9/L",
            "abnormal_flag": True
        }
    ],
    "ai_suggestions": [
        {
            "suggested_diagnosis": "上呼吸道感染",
            "confidence_score": 0.85,
            "risk_level": "Low",
            "recommended_tests": ["C反应蛋白", "降钙素原"]
        }
    ],
    "final_diagnosis_code": "J06.9",
    "final_diagnosis_name": "上呼吸道感染",
    "confirmed_by": "DOC-001",
    "confirmed_at": datetime(2025, 1, 21, 15, 0, 0)
}

# 存储诊断记录
diagnosis_id = storage.store_clinical_data(diagnosis_data)
print(f"Intelligent diagnosis stored: {diagnosis_id}")

# 查询诊断记录
diagnosis_records = storage.query_diagnosis_by_patient("P1234567890")
print(f"Found {len(diagnosis_records)} diagnosis records")
```

---

## 9. 案例8：药物管理系统

### 9.1 场景描述

**业务背景**：
药物管理系统管理患者用药记录，包括处方开具、
药物配送、用药提醒、不良反应监测等。

**技术挑战**：
- 需要药物信息标准化
- 需要用药时间管理
- 需要药物相互作用检查
- 需要不良反应监测

**解决方案**：
使用FHIR MedicationRequest资源记录处方，
使用FHIR MedicationAdministration资源记录用药记录，
使用HealthcareStorage存储药物管理数据。

### 9.2 Schema定义

**药物管理Schema**：

```dsl
schema MedicationManagement {
  medication_request_id: String @value("MED-REQ-001") @required
  patient_id: String @value("P1234567890") @required
  practitioner_id: String @value("DOC-001") @required

  medication: {
    medication_code: String @value("N02BE01") @required
    medication_name: String @value("布洛芬") @required
    form: Enum { Tablet } @value(Tablet)
    strength: String @value("200mg")
  } @required

  dosage_instruction: {
    text: String @value("每次200mg，每日3次，饭后服用")
    timing: {
      frequency: Integer @value(3)
      period: Integer @value(1)
      period_unit: Enum { Day } @value(Day)
    }
    route: Enum { Oral } @value(Oral)
    dose_quantity: {
      value: Decimal @value(200.0)
      unit: String @value("mg")
    }
  } @required

  duration: {
    value: Integer @value(3)
    unit: Enum { Day } @value(Day)
  } @required

  administration_records: [
    {
      administration_id: String @value("ADMIN-001")
      scheduled_time: DateTime @value("2025-01-21T08:00:00")
      actual_time: DateTime @value("2025-01-21T08:05:00")
      status: Enum { Completed } @value(Completed)
      administered_by: String @value("P1234567890")
    }
  ]

  adverse_reactions: [
    {
      reaction_type: String @value("Allergy")
      severity: Enum { Mild }
      description: String @value("轻微皮疹")
      reported_at: DateTime @value("2025-01-22T10:00:00")
    }
  ]
} @standard("FHIR_R4")
```

### 9.3 实现代码

```python
# 创建药物管理记录
medication_data = {
    "patient_id": "P1234567890",
    "medication_request_id": "MED-REQ-001",
    "practitioner_id": "DOC-001",
    "medication_code": "N02BE01",
    "medication_name": "布洛芬",
    "form": "Tablet",
    "strength": "200mg",
    "dosage_text": "每次200mg，每日3次，饭后服用",
    "frequency": 3,
    "period": 1,
    "period_unit": "Day",
    "route": "Oral",
    "dose_value": 200.0,
    "dose_unit": "mg",
    "duration_value": 3,
    "duration_unit": "Day",
    "prescribed_at": datetime(2025, 1, 21, 10, 0, 0)
}

# 存储药物管理记录
medication_id = storage.store_clinical_data(medication_data)
print(f"Medication management record stored: {medication_id}")

# 记录用药
administration_data = {
    "medication_request_id": "MED-REQ-001",
    "administration_id": "ADMIN-001",
    "scheduled_time": datetime(2025, 1, 21, 8, 0, 0),
    "actual_time": datetime(2025, 1, 21, 8, 5, 0),
    "status": "Completed",
    "administered_by": "P1234567890"
}

# 存储用药记录
admin_id = storage.store_clinical_data(administration_data)
print(f"Medication administration recorded: {admin_id}")

# 查询用药记录
medication_records = storage.query_medication_by_patient("P1234567890")
print(f"Found {len(medication_records)} medication records")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
