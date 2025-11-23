# 医疗信息系统Schema形式化定义

## 📑 目录

- [医疗信息系统Schema形式化定义](#医疗信息系统schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 患者信息Schema](#2-患者信息schema)
  - [3. 临床数据Schema](#3-临床数据schema)
  - [4. 医疗记录Schema](#4-医疗记录schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 数据完整性定理](#81-数据完整性定理)
    - [8.2 隐私保护定理](#82-隐私保护定理)

---

## 1. 形式化模型

**定义1（医疗信息系统Schema）**：
医疗信息系统Schema是一个五元组：

```text
Healthcare_Schema = (Patient_Info, Clinical_Data,
                    Medical_Record, Diagnosis, Treatment)
```

其中：

- `Patient_Info`：患者信息Schema
- `Clinical_Data`：临床数据Schema
- `Medical_Record`：医疗记录Schema
- `Diagnosis`：诊断Schema
- `Treatment`：治疗Schema

---

## 2. 患者信息Schema

**定义2（患者信息Schema）**：

```text
Patient_Info_Schema = (Basic_Info, Contact_Info,
                      Insurance_Info, Allergy_Info, Medical_History)
```

**形式化DSL定义**：

```dsl
schema PatientInfo {
  patient_id: String @pattern("^[A-Z0-9]{10}$") @required @unique

  basic_info: {
    name: String @max_length(100) @required
    gender: Enum { M, F, O } @required
    birth_date: Date @format("YYYY-MM-DD") @required
    id_number: String @pattern("^[0-9X]{18}$") @required
    nationality: String @length(2) @pattern("^[A-Z]{2}$")
  } @required

  contact_info: {
    address: String @max_length(200)
    phone: String @pattern("^[0-9-+]{10,20}$")
    email: String @pattern("^[^@]+@[^@]+\\.[^@]+$")
    emergency_contact: {
      name: String @max_length(100)
      relationship: String @max_length(50)
      phone: String @pattern("^[0-9-+]{10,20}$")
    }
  }

  insurance_info: {
    insurance_type: Enum { Public, Private, Self } @required
    insurance_number: String @max_length(50)
    insurance_provider: String @max_length(100)
    effective_date: Date @format("YYYY-MM-DD")
    expiry_date: Date @format("YYYY-MM-DD")
  }

  allergy_info: List<Allergy> {
    allergen: String @max_length(100) @required
    reaction: String @max_length(200)
    severity: Enum { Mild, Moderate, Severe } @required
    recorded_date: Date @format("YYYY-MM-DD") @required
  }

  medical_history: List<MedicalHistory> {
    condition: String @max_length(200) @required
    diagnosis_date: Date @format("YYYY-MM-DD")
    treatment: String @max_length(500)
    status: Enum { Active, Resolved, Chronic }
  }
} @standard("FHIR_R4")
```

---

## 3. 临床数据Schema

**定义3（临床数据Schema）**：

```text
Clinical_Data_Schema = (Vital_Signs, Lab_Results,
                       Imaging_Results, Pathology_Results)
```

**形式化DSL定义**：

```dsl
schema ClinicalData {
  patient_id: String @pattern("^[A-Z0-9]{10}$") @required
  encounter_id: String @pattern("^[A-Z0-9]{10}$") @required
  recorded_at: DateTime @required

  vital_signs: {
    temperature: Decimal @precision(4,1) @unit("Celsius") @range(30.0, 45.0)
    blood_pressure: {
      systolic: Integer @range(50, 300) @unit("mmHg")
      diastolic: Integer @range(30, 200) @unit("mmHg")
    }
    heart_rate: Integer @range(30, 220) @unit("bpm")
    respiratory_rate: Integer @range(8, 40) @unit("breaths/min")
    oxygen_saturation: Decimal @precision(4,1) @range(0.0, 100.0) @unit("%")
  }

  lab_results: List<LabResult> {
    test_name: String @max_length(100) @required
    test_code: String @pattern("^[A-Z0-9]{5,10}$")
    result_value: String @max_length(200)
    unit: String @max_length(20)
    reference_range: String @max_length(100)
    status: Enum { Final, Preliminary, Corrected }
    performed_at: DateTime @required
  }

  imaging_results: List<ImagingResult> {
    study_type: Enum { XRay, CT, MRI, Ultrasound, PET } @required
    body_part: String @max_length(100) @required
    study_date: Date @format("YYYY-MM-DD") @required
    report: String @max_length(5000)
    image_url: String @pattern("^https?://.+$")
  }

  pathology_results: List<PathologyResult> {
    specimen_type: String @max_length(100) @required
    test_name: String @max_length(100) @required
    result: String @max_length(1000) @required
    diagnosis: String @max_length(500)
    performed_at: DateTime @required
  }
} @standard("FHIR_R4")
```

---

## 4. 医疗记录Schema

**定义4（医疗记录Schema）**：

```text
Medical_Record_Schema = (Diagnosis_Record, Treatment_Record,
                        Medication_Record, Surgery_Record)
```

**形式化DSL定义**：

```dsl
schema MedicalRecord {
  record_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  patient_id: String @pattern("^[A-Z0-9]{10}$") @required
  encounter_id: String @pattern("^[A-Z0-9]{10}$") @required
  created_at: DateTime @required
  created_by: String @max_length(100) @required

  diagnosis_record: List<Diagnosis> {
    diagnosis_code: String @pattern("^[A-Z0-9]{3,10}$") @required
    diagnosis_name: String @max_length(200) @required
    diagnosis_date: Date @format("YYYY-MM-DD") @required
    icd_version: Enum { ICD10, ICD11 } @required
    severity: Enum { Mild, Moderate, Severe }
    status: Enum { Confirmed, Provisional, RuledOut }
  } @required

  treatment_record: List<Treatment> {
    treatment_type: Enum { Medication, Surgery, Therapy, Other } @required
    treatment_name: String @max_length(200) @required
    start_date: Date @format("YYYY-MM-DD") @required
    end_date: Date @format("YYYY-MM-DD")
    status: Enum { Planned, InProgress, Completed, Discontinued }
    outcome: String @max_length(500)
  }

  medication_record: List<Medication> {
    medication_name: String @max_length(200) @required
    medication_code: String @pattern("^[A-Z0-9]{5,15}$")
    dosage: String @max_length(100) @required
    frequency: String @max_length(50) @required
    route: Enum { Oral, IV, IM, Topical, Inhalation } @required
    start_date: Date @format("YYYY-MM-DD") @required
    end_date: Date @format("YYYY-MM-DD")
    prescriber: String @max_length(100) @required
  }

  surgery_record: List<Surgery> {
    surgery_name: String @max_length(200) @required
    surgery_code: String @pattern("^[A-Z0-9]{5,15}$")
    surgery_date: DateTime @required
    surgeon: String @max_length(100) @required
    anesthesia_type: Enum { General, Regional, Local }
    duration_minutes: Integer @range(0, 1440)
    complications: String @max_length(1000)
  }
} @standard("FHIR_R4")
```

---

## 5. 类型系统

**定义5（医疗数据类型）**：

```text
Healthcare_Data_Type = Patient_Info | Clinical_Data |
                      Medical_Record | Diagnosis | Treatment |
                      Medication | Lab_Result | Imaging_Result
```

**基本类型定义**：

```dsl
type Date {
  format: Enum { YYYYMMDD, YYYY-MM-DD }
  value: String @pattern("^[0-9]{8}|[0-9]{4}-[0-9]{2}-[0-9]{2}$")
}

type DateTime {
  format: Enum { ISO8601 }
  value: String @pattern("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")
}

type PatientIdentifier {
  system: String @required
  value: String @required @unique
}

type CodeableConcept {
  coding: List<Coding> {
    system: String @required
    code: String @required
    display: String
  }
  text: String
}
```

---

## 6. 约束规则

**约束1（患者信息完整性）**：

```text
∀ patient ∈ Patient_Info:
  patient.patient_id ≠ ∅
  ∧ patient.basic_info.name ≠ ∅
  ∧ patient.basic_info.birth_date ≤ current_date()
```

**约束2（临床数据有效性）**：

```text
∀ clinical_data ∈ Clinical_Data:
  clinical_data.patient_id ∈ Patient_Info.patient_id
  ∧ clinical_data.recorded_at ≤ current_datetime()
  ∧ validate_vital_signs(clinical_data.vital_signs)
```

**约束3（医疗记录关联性）**：

```text
∀ record ∈ Medical_Record:
  record.patient_id ∈ Patient_Info.patient_id
  ∧ record.encounter_id ∈ Encounter.encounter_id
  ∧ record.diagnosis_record ≠ ∅
```

**约束4（隐私保护）**：

```text
∀ patient ∈ Patient_Info:
  encrypt_sensitive_data(patient.id_number)
  ∧ access_control(patient, authorized_users)
```

---

## 7. 转换函数

**函数1（FHIR到HL7转换）**：

```text
convert_FHIR_to_HL7: FHIR_Patient → HL7_Patient
```

**函数2（HL7到FHIR转换）**：

```text
convert_HL7_to_FHIR: HL7_Patient → FHIR_Patient
```

**函数3（数据验证）**：

```text
validate_healthcare_data: Healthcare_Data → Bool
```

---

## 8. 形式化定理

### 8.1 数据完整性定理

**定理1（患者信息完整性）**：

```text
∀ patient ∈ Patient_Info:
  validate_patient_info(patient)
  → data_integrity(patient)
  ∧ referential_integrity(patient)
```

### 8.2 隐私保护定理

**定理2（医疗数据隐私保护）**：

```text
∀ data ∈ Healthcare_Data:
  encrypt_sensitive_fields(data)
  ∧ access_control(data, authorized_users)
  → privacy_protected(data)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
