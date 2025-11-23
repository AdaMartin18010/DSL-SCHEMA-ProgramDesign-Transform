# FHIR Schema概述

## 📑 目录

- [FHIR Schema概述](#fhir-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 FHIR Schema定义](#11-fhir-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 FHIR Schema定义](#21-fhir-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. FHIR资源类型Schema](#3-fhir资源类型schema)
    - [3.1 患者资源Schema](#31-患者资源schema)
    - [3.2 诊断资源Schema](#32-诊断资源schema)
    - [3.3 观察资源Schema](#33-观察资源schema)
  - [4. 标准对标](#4-标准对标)
    - [4.1 FHIR标准](#41-fhir标准)
    - [4.2 HL7标准](#42-hl7标准)
  - [5. 应用场景](#5-应用场景)
    - [5.1 电子健康记录](#51-电子健康记录)
    - [5.2 医疗信息交换](#52-医疗信息交换)
    - [5.3 远程医疗](#53-远程医疗)
    - [5.4 FHIR数据存储与分析](#54-fhir数据存储与分析)
  - [6. 思维导图](#6-思维导图)

---

## 1. 核心结论

**FHIR（快速医疗互操作性资源）存在标准化的
Schema体系**。

### 1.1 FHIR Schema定义

```text
FHIR_Schema = (Resource_Definition ⊕ RESTful_API
              ⊕ JSON_XML_Format ⊕ Extension_Mechanism) × FHIR_Profile
```

### 1.2 标准依据

- **FHIR R4**：快速医疗互操作性资源标准（HL7 FHIR R4）
- **HL7标准**：健康信息交换标准
- **ISO 13606**：电子健康记录通信标准
- **HIPAA**：美国健康保险流通与责任法案

---

## 2. 概念定义

### 2.1 FHIR Schema定义

**FHIR Schema**是描述FHIR资源结构和
RESTful API接口的形式化规范，包括患者、
诊断、观察等医疗资源。

### 2.2 核心特征

1. **标准化**：基于HL7 FHIR R4标准
2. **RESTful**：基于HTTP的RESTful API
3. **格式灵活**：支持JSON和XML格式
4. **可扩展**：支持自定义扩展
5. **互操作性**：支持不同医疗系统间的数据交换

### 2.3 Schema分类

- **患者资源Schema**：Patient资源定义
- **诊断资源Schema**：Condition资源定义
- **观察资源Schema**：Observation资源定义
- **用药资源Schema**：Medication资源定义
- **就诊资源Schema**：Encounter资源定义

---

## 3. FHIR资源类型Schema

### 3.1 患者资源Schema

**定义**：描述患者基本信息和医疗历史。

**包含内容**：

- 患者标识符（identifier）
- 患者姓名（name）
- 性别（gender）
- 出生日期（birthDate）
- 联系方式（telecom）
- 地址（address）
- 紧急联系人（contact）

### 3.2 诊断资源Schema

**定义**：描述患者诊断信息。

**包含内容**：

- 诊断编码（code）
- 诊断名称（code.text）
- 诊断时间（onsetDateTime）
- 严重程度（severity）
- 诊断状态（clinicalStatus）
- 验证状态（verificationStatus）

### 3.3 观察资源Schema

**定义**：描述临床观察数据和检查结果。

**包含内容**：

- 观察类型（code）
- 观察值（value）
- 观察时间（effectiveDateTime）
- 状态（status）
- 单位（unit）
- 参考范围（referenceRange）

---

## 4. 标准对标

### 4.1 FHIR标准

- **FHIR R4**：快速医疗互操作性资源标准（HL7 FHIR R4）
- **FHIR R5**：FHIR版本5标准（规划中）
- **FHIR基础资源**：核心资源定义

### 4.2 HL7标准

- **HL7 v2**：健康信息交换标准
- **HL7 v3**：健康信息交换标准
- **HL7 CDA**：临床文档架构标准

---

## 5. 应用场景

### 5.1 电子健康记录

- 患者信息管理
- 临床数据记录
- 医疗记录存储

### 5.2 医疗信息交换

- 医院间数据交换
- 医生间信息共享
- 患者转诊信息传递

### 5.3 远程医疗

- 远程诊断
- 远程会诊
- 远程监测

### 5.4 FHIR数据存储与分析

**数据库存储应用场景**：

- **PostgreSQL FHIR数据存储**：
  - FHIR资源存储（Patient、Condition、Observation等）
  - RESTful API日志存储
  - 资源版本存储
  - 扩展数据存储
  - 统计信息存储（资源使用统计、API调用统计）

**应用价值**：

- 高效存储大规模FHIR资源数据
- 支持FHIR资源查询和分析
- 提供FHIR API性能监控
- 支持FHIR资源版本管理

---

## 6. 思维导图

```text
FHIR Schema
│
├─ 患者资源
│   ├─ Patient
│   ├─ RelatedPerson
│   └─ Practitioner
│
├─ 诊断资源
│   ├─ Condition
│   ├─ AllergyIntolerance
│   └─ Procedure
│
└─ 观察资源
    ├─ Observation
    ├─ DiagnosticReport
    └─ ImagingStudy
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
