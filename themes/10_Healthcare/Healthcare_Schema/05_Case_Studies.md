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

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
