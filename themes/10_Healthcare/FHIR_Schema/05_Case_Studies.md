# FHIR Schema实践案例

## 📑 目录

- [FHIR Schema实践案例](#fhir-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：FHIR Patient资源](#2-案例1fhir-patient资源)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：FHIR Observation资源](#3-案例2fhir-observation资源)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：FHIR Condition资源](#4-案例3fhir-condition资源)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：FHIR RESTful API](#5-案例4fhir-restful-api)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：FHIR数据存储系统](#6-案例5fhir数据存储系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供FHIR Schema在实际应用中的实践案例。

---

## 2. 案例1：FHIR Patient资源

### 2.1 场景描述

**应用场景**：
使用FHIR Patient资源管理患者信息。

### 2.2 Schema定义

**FHIR Patient资源Schema**：

```json
{
  "resourceType": "Patient",
  "id": "example-patient",
  "identifier": [{
    "system": "http://hospital.example.org/patients",
    "value": "P1234567890"
  }],
  "name": [{
    "use": "official",
    "family": "张",
    "given": ["三"]
  }],
  "gender": "male",
  "birthDate": "1980-05-15",
  "telecom": [{
    "system": "phone",
    "value": "13800138000",
    "use": "mobile"
  }],
  "address": [{
    "use": "home",
    "line": ["北京市朝阳区XX街道XX号"],
    "city": "北京",
    "postalCode": "100000",
    "country": "CN"
  }]
}
```

---

## 3. 案例2：FHIR Observation资源

### 3.1 场景描述

**应用场景**：
使用FHIR Observation资源记录生命体征数据。

### 3.2 Schema定义

**FHIR Observation资源Schema**：

```json
{
  "resourceType": "Observation",
  "id": "example-observation",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "vital-signs"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "85354-9",
      "display": "Blood pressure"
    }]
  },
  "subject": {
    "reference": "Patient/example-patient"
  },
  "effectiveDateTime": "2025-01-21T10:30:00Z",
  "valueQuantity": {
    "value": 120,
    "unit": "mmHg",
    "system": "http://unitsofmeasure.org",
    "code": "mm[Hg]"
  }
}
```

---

## 4. 案例3：FHIR Condition资源

### 4.1 场景描述

**应用场景**：
使用FHIR Condition资源记录诊断信息。

### 4.2 Schema定义

**FHIR Condition资源Schema**：

```json
{
  "resourceType": "Condition",
  "id": "example-condition",
  "clinicalStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
      "code": "active"
    }]
  },
  "verificationStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
      "code": "confirmed"
    }]
  },
  "code": {
    "coding": [{
      "system": "http://hl7.org/fhir/sid/icd-10",
      "code": "I10",
      "display": "原发性高血压"
    }]
  },
  "subject": {
    "reference": "Patient/example-patient"
  },
  "onsetDateTime": "2025-01-21T00:00:00Z"
}
```

---

## 5. 案例4：FHIR RESTful API

### 5.1 场景描述

**应用场景**：
使用FHIR RESTful API访问FHIR资源。

### 5.2 实现代码

```python
import requests

# 获取Patient资源
def get_patient(patient_id: str):
    response = requests.get(
        f"http://fhir.example.org/fhir/Patient/{patient_id}"
    )
    return response.json()

# 创建Patient资源
def create_patient(patient_data: dict):
    response = requests.post(
        "http://fhir.example.org/fhir/Patient",
        json=patient_data,
        headers={"Content-Type": "application/fhir+json"}
    )
    return response.json()

# 搜索Patient资源
def search_patients(name: str):
    response = requests.get(
        "http://fhir.example.org/fhir/Patient",
        params={"name": name}
    )
    return response.json()
```

---

## 6. 案例5：FHIR数据存储系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储FHIR资源数据。

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
