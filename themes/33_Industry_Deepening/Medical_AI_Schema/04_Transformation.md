# 医疗AI Schema转换体系

## 📑 目录

- [医疗AI Schema转换体系](#医疗ai-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. DICOM转换](#3-dicom转换)
  - [4. HL7 FHIR转换](#4-hl7-fhir转换)
  - [5. PostgreSQL存储](#5-postgresql存储)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)

---

## 1. 转换体系概述

医疗AI Schema转换体系支持**医疗AI数据到各种格式的转换**，包括DICOM、HL7 FHIR、PostgreSQL等格式。

**转换目标**：

- DICOM格式
- HL7 FHIR格式
- PostgreSQL数据库
- JSON格式

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 | 隐私保护 |
|---------|--------|----------|------------|----------|------------|----------|
| **Medical_AI → DICOM** | Medical_AI_Schema | DICOM | ⭐⭐⭐ | ✅ 良好 | 高 | ✅ 支持 |
| **Medical_AI → HL7 FHIR** | Medical_AI_Schema | FHIR | ⭐⭐⭐ | ✅ 良好 | 高 | ✅ 支持 |
| **Medical_AI → PostgreSQL** | Medical_AI_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 | ⚠️ 需加密 |
| **Medical_AI → JSON** | Medical_AI_Schema | JSON Schema | ⭐⭐ | ✅ 良好 | 高 | ⚠️ 需加密 |

---

## 3. DICOM转换

### 3.1 Medical_AI → DICOM转换

**转换函数**：

```text
to_dicom: Medical_Imaging → DICOM_File
```

**转换示例**：

**输入（Medical_AI_Schema）**：

```dsl
medical_imaging CT_Scan {
  image_id: "CT_001"
  image_type: CT
  image_info: {
    patient_id: "P12345"
    study_date: "2024-01-21"
    modality: CT
  }
  image_data: {
    pixel_data: <binary_data>
    width: 512
    height: 512
    pixel_spacing: [0.5, 0.5]
  }
}
```

**输出（DICOM）**：

使用pydicom库：

```python
import pydicom
from pydicom.dataset import FileDataset

def to_dicom(medical_imaging: MedicalImaging) -> FileDataset:
    """转换为DICOM格式"""
    ds = FileDataset("CT_001.dcm", {}, file_meta={}, preamble=b"\x00" * 128)

    # 患者信息
    ds.PatientID = medical_imaging.image_info.patient_id
    ds.PatientName = medical_imaging.image_info.patient_name

    # 研究信息
    ds.StudyDate = medical_imaging.image_info.study_date
    ds.Modality = medical_imaging.image_info.modality

    # 影像数据
    ds.PixelData = medical_imaging.image_data.pixel_data
    ds.Rows = medical_imaging.image_data.height
    ds.Columns = medical_imaging.image_data.width
    ds.PixelSpacing = medical_imaging.image_data.pixel_spacing

    return ds
```

---

## 4. HL7 FHIR转换

### 4.1 Medical_AI → HL7 FHIR转换

**转换函数**：

```text
to_fhir: Electronic_Health_Record → FHIR_Resource
```

**转换示例**：

**输入（Medical_AI_Schema）**：

```dsl
ehr Patient_Record {
  patient_id: "P12345"
  diagnosis: {
    primary_diagnosis: "Pneumonia"
    icd_code: "J18.9"
  }
}
```

**输出（FHIR JSON）**：

```json
{
  "resourceType": "Patient",
  "id": "P12345",
  "identifier": [{
    "system": "http://hospital.example.org/patients",
    "value": "P12345"
  }],
  "condition": [{
    "code": {
      "coding": [{
        "system": "http://hl7.org/fhir/sid/icd-10",
        "code": "J18.9",
        "display": "Pneumonia"
      }]
    }
  }]
}
```

---

## 5. PostgreSQL存储

### 5.1 数据库Schema设计

**注意**：医疗数据需要加密存储，符合HIPAA要求。

```sql
-- 患者表（加密字段）
CREATE TABLE patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    encrypted_name BYTEA,  -- 加密存储
    encrypted_dob BYTEA,  -- 加密存储
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 医学影像表
CREATE TABLE medical_images (
    image_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    image_type VARCHAR(50),
    study_id VARCHAR(50),
    series_id VARCHAR(50),
    dicom_file_path TEXT,
    image_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 电子病历表
CREATE TABLE electronic_health_records (
    record_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    clinical_data JSONB,
    diagnosis JSONB,
    treatment JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI诊断表
CREATE TABLE ai_diagnoses (
    diagnosis_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    model_id VARCHAR(50),
    model_version VARCHAR(50),
    input_data JSONB,
    output_result JSONB,
    confidence FLOAT,
    explanation JSONB,
    physician_review JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引（注意隐私）
CREATE INDEX idx_medical_images_patient_id ON medical_images(patient_id);
CREATE INDEX idx_ehr_patient_id ON electronic_health_records(patient_id);
```

### 5.2 数据加密

**PostgreSQL加密示例**：

```sql
-- 使用pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密插入
INSERT INTO patients (patient_id, encrypted_name, encrypted_dob, gender)
VALUES (
    'P12345',
    pgp_sym_encrypt('John Doe', 'encryption_key'),
    pgp_sym_encrypt('1980-01-01', 'encryption_key'),
    'male'
);

-- 解密查询
SELECT
    patient_id,
    pgp_sym_decrypt(encrypted_name, 'encryption_key') AS name,
    pgp_sym_decrypt(encrypted_dob, 'encryption_key') AS date_of_birth,
    gender
FROM patients
WHERE patient_id = 'P12345';
```

---

## 6. 转换工具

### 6.1 开源工具

**DICOM工具**：

- **pydicom**：Python DICOM库
- **dcm4che**：Java DICOM工具
- **DCMTK**：C++ DICOM工具包

**HL7 FHIR工具**：

- **fhir-py**：Python FHIR库
- **HAPI FHIR**：Java FHIR库
- **Firely .NET SDK**：.NET FHIR库

### 6.2 自定义转换器

**转换器实现**：

```python
import pydicom
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition

class MedicalAITransformer:
    def to_dicom(self, medical_imaging: MedicalImaging) -> pydicom.Dataset:
        """转换为DICOM格式"""
        ds = pydicom.Dataset()
        # 设置DICOM标签
        ds.PatientID = medical_imaging.image_info.patient_id
        ds.Modality = medical_imaging.image_info.modality
        ds.PixelData = medical_imaging.image_data.pixel_data
        # ...
        return ds

    def to_fhir(self, ehr: ElectronicHealthRecord) -> dict:
        """转换为FHIR格式"""
        patient = Patient()
        patient.id = ehr.patient_id
        # 添加条件（诊断）
        condition = Condition()
        condition.code = {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": ehr.diagnosis.icd_code
            }]
        }
        return patient.dict()
```

---

## 7. 转换验证

### 7.1 DICOM验证

**验证方法**：

1. 验证DICOM文件格式
2. 验证必需标签存在
3. 验证数据完整性

**验证工具**：

```python
import pydicom

def validate_dicom(dicom_file: str) -> bool:
    """验证DICOM文件"""
    try:
        ds = pydicom.dcmread(dicom_file)
        # 验证必需标签
        required_tags = ['PatientID', 'StudyDate', 'Modality']
        for tag in required_tags:
            if tag not in ds:
                return False
        return True
    except Exception:
        return False
```

### 7.2 HL7 FHIR验证

**验证方法**：

1. 验证FHIR资源结构
2. 验证必需字段
3. 验证数据格式

**验证工具**：

```python
from fhir.resources import construct_fhir_element

def validate_fhir(fhir_json: dict, resource_type: str) -> bool:
    """验证FHIR资源"""
    try:
        resource = construct_fhir_element(resource_type, fhir_json)
        resource.validate()
        return True
    except Exception:
        return False
```

### 7.3 隐私保护验证

**验证方法**：

1. 验证敏感数据加密
2. 验证访问控制
3. 验证审计日志

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
