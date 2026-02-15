# EMR Schema概述

## 📑 目录

- [EMR Schema概述](#emr-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 EMR Schema定义](#11-emr-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 EMR Schema定义](#21-emr-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. EMR系统架构](#3-emr系统架构)
    - [3.1 架构概述](#31-架构概述)
    - [3.2 数据层](#32-数据层)
    - [3.3 业务逻辑层](#33-业务逻辑层)
    - [3.4 表示层](#34-表示层)
  - [4. 病历结构](#4-病历结构)
    - [4.1 病历组成](#41-病历组成)
    - [4.2 门急诊病历](#42-门急诊病历)
    - [4.3 住院病历](#43-住院病历)
  - [5. 临床文档](#5-临床文档)
    - [5.1 文档类型](#51-文档类型)
    - [5.2 文档结构](#52-文档结构)
    - [5.3 文档模板](#53-文档模板)
  - [6. 数据交换](#6-数据交换)
    - [6.1 交换标准](#61-交换标准)
    - [6.2 交换协议](#62-交换协议)
    - [6.3 安全传输](#63-安全传输)
  - [7. 应用场景](#7-应用场景)
    - [7.1 电子病历管理](#71-电子病历管理)
    - [7.2 临床决策支持](#72-临床决策支持)
    - [7.3 医疗质量监控](#73-医疗质量监控)
    - [7.4 科研数据分析](#74-科研数据分析)
  - [8. 思维导图](#8-思维导图)

---

## 1. 核心结论

**电子病历（EMR）存在标准化的Schema体系**，为医疗机构提供完整的病历数据管理和交换能力。

### 1.1 EMR Schema定义

```text
EMR_Schema = (Clinical_Document ⊕ Patient_Data
              ⊕ Medical_Record_Structure ⊕ Data_Exchange_Protocol)
              × EMR_Standard_Compliance × Security_Framework
```

### 1.2 标准依据

- **HL7 CDA**：临床文档架构标准（Clinical Document Architecture）
- **ASTM E1384**：电子健康记录标准指南
- **ISO 18308**：电子健康记录系统要求标准
- **IHE**：医疗信息集成规范
- **GB/T 31992-2015**：中国电子病历基本数据集标准

---

## 2. 概念定义

### 2.1 EMR Schema定义

**EMR Schema**是描述电子病历数据结构和交换协议的形式化规范，包括病历文档、临床数据、患者信息等医疗记录元素。

### 2.2 核心特征

1. **标准化**：基于HL7 CDA R2/R3标准
2. **结构化**：支持结构化和半结构化数据
3. **完整性**：覆盖全生命周期病历数据
4. **可追溯**：支持数据修改历史追踪
5. **互操作性**：支持跨机构病历共享
6. **安全性**：符合医疗数据隐私保护要求

### 2.3 Schema分类

- **患者信息Schema**：患者基本信息、 demographics
- **就诊记录Schema**：门诊、住院、急诊记录
- **医嘱Schema**：药物、检查、治疗医嘱
- **检验检查Schema**：实验室结果、影像报告
- **护理记录Schema**：护理评估、护理计划
- **手术记录Schema**：手术申请、记录、麻醉
- **病程记录Schema**：病程进展、会诊记录

---

## 3. EMR系统架构

### 3.1 架构概述

**EMR系统采用分层架构设计**：

```text
EMR_Architecture = (Presentation_Layer, Business_Logic_Layer,
                   Data_Access_Layer, Integration_Layer)
```

### 3.2 数据层

**数据库架构**：

- **主数据库**：存储结构化病历数据
- **文档库**：存储非结构化临床文档
- **历史库**：存储归档病历数据
- **索引库**：支持全文检索和数据查询

**数据模型**：

```
┌─────────────────────────────────────────────────────────────┐
│                        数据访问层                            │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  主数据库    │  文档库      │  历史库      │    索引库         │
│  (Oracle)   │  (MongoDB)  │  (HBase)    │   (Elasticsearch) │
├─────────────┴─────────────┴─────────────┴───────────────────┤
│                      数据缓存层                              │
│                    (Redis Cluster)                           │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 业务逻辑层

**核心业务模块**：

1. **病历书写模块**：支持结构化病历录入
2. **医嘱管理模块**：医嘱开立、审核、执行
3. **护理文书模块**：护理评估、记录、计划
4. **检验检查模块**：申请、结果查询、报告
5. **质量管理模块**：病历质控、评分、反馈
6. **科研模块**：数据抽取、统计分析

### 3.4 表示层

**用户界面组件**：

- **医生工作站**：病历书写、医嘱管理
- **护士工作站**：护理记录、医嘱执行
- **医技工作站**：检查申请、报告录入
- **管理工作站**：质控管理、统计分析

---

## 4. 病历结构

### 4.1 病历组成

**EMR数据结构定义**：

```text
EMR_Record = (Header, Body, Footer, Attachments)
```

**病历头部（Header）**：

- 患者基本信息
- 就诊信息
- 文档元数据
- 作者信息
- 审核信息

**病历主体（Body）**：

- 主诉（Chief Complaint）
- 现病史（History of Present Illness）
- 既往史（Past Medical History）
- 个人史（Personal History）
- 家族史（Family History）
- 体格检查（Physical Examination）
- 辅助检查（Auxiliary Examination）
- 初步诊断（Preliminary Diagnosis）
- 诊疗计划（Treatment Plan）

**病历尾部（Footer）**：

- 签名信息
- 时间戳
- 版本信息

### 4.2 门急诊病历

**门诊病历结构**：

```dsl
schema OutpatientEMR {
  header: EMRHeader {
    patientId: String @required
    visitId: String @required
    visitType: Enum { outpatient, emergency } @required
    department: String @required
    attendingDoctor: Practitioner @required
    visitTime: DateTime @required
  }
  
  body: EMRBody {
    chiefComplaint: Text @maxLength(1000)
    presentIllness: Text @maxLength(5000)
    pastHistory: PastHistory
    physicalExam: PhysicalExamination
    auxiliaryExam: List<AuxiliaryExamination>
    diagnosis: List<Diagnosis> @required
    treatmentPlan: TreatmentPlan
  }
  
  footer: EMRFooter {
    signatures: List<Signature> @required
    createTime: DateTime @required
    modifyTime: DateTime
  }
}
```

### 4.3 住院病历

**住院病历组成**：

1. **入院记录**：入院评估、初步诊断
2. **病程记录**：日常病程、上级查房
3. **手术记录**：手术同意书、手术记录、麻醉记录
4. **出院记录**：出院诊断、出院医嘱
5. **死亡记录**：死亡讨论、尸检报告

---

## 5. 临床文档

### 5.1 文档类型

**标准临床文档分类**：

| 文档类型 | 英文名称 | 应用场景 |
|---------|---------|---------|
| 门诊病历 | Outpatient Note | 门诊就诊记录 |
| 住院病历 | Inpatient Note | 住院期间记录 |
| 出院小结 | Discharge Summary | 出院时汇总 |
| 手术记录 | Operative Report | 手术过程记录 |
| 病理报告 | Pathology Report | 病理检查结果 |
| 影像报告 | Imaging Report | 影像检查结果 |
| 检验报告 | Lab Report | 实验室检查结果 |
| 会诊记录 | Consultation Note | 会诊意见记录 |
| 转科记录 | Transfer Note | 转科过程记录 |
| 死亡记录 | Death Note | 患者死亡记录 |

### 5.2 文档结构

**HL7 CDA文档结构**：

```xml
<ClinicalDocument xmlns="urn:hl7-org:v3">
  <!-- 文档头部 -->
  <realmCode code="CN"/>
  <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
  <templateId root="2.16.156.10011.2.1.1.1"/>
  
  <!-- 文档唯一标识 -->
  <id root="2.16.156.10011.1.1" extension="DOC001"/>
  
  <!-- 文档代码 -->
  <code code="11506-3" codeSystem="2.16.840.1.113883.6.1" 
        displayName="Progress note"/>
  
  <!-- 文档标题 -->
  <title>病程记录</title>
  
  <!-- 文档创建时间 -->
  <effectiveTime value="20250115143000"/>
  
  <!-- 机密性 -->
  <confidentialityCode code="N" codeSystem="2.16.840.1.113883.5.25"/>
  
  <!-- 文档语言和编码 -->
  <languageCode code="zh-CN"/>
  
  <!-- 患者信息 -->
  <recordTarget>
    <patientRole>
      <id root="2.16.156.10011.1.12" extension="PAT001"/>
      <patient>
        <name>张三</name>
        <administrativeGenderCode code="M"/>
        <birthTime value="19800101"/>
      </patient>
    </patientRole>
  </recordTarget>
  
  <!-- 文档作者 -->
  <author>
    <assignedAuthor>
      <id root="2.16.156.10011.1.7" extension="DOC001"/>
      <assignedPerson>
        <name>李医生</name>
      </assignedPerson>
    </assignedAuthor>
  </author>
  
  <!-- 文档内容 -->
  <component>
    <structuredBody>
      <component>
        <section>
          <code code="10164-2" codeSystem="2.16.840.1.113883.6.1"/>
          <title>病程记录</title>
          <text>患者今日病情稳定...</text>
        </section>
      </component>
    </structuredBody>
  </component>
</ClinicalDocument>
```

### 5.3 文档模板

**标准文档模板库**：

1. **入院记录模板**：包含标准入院评估项目
2. **病程记录模板**：支持结构化病程记录
3. **出院记录模板**：标准化出院小结格式
4. **手术记录模板**：手术过程结构化记录
5. **会诊记录模板**：会诊意见标准格式

---

## 6. 数据交换

### 6.1 交换标准

**主要数据交换标准**：

| 标准 | 组织 | 用途 | 版本 |
|-----|------|-----|------|
| HL7 CDA | HL7 | 临床文档交换 | R2/R3 |
| HL7 FHIR | HL7 | 资源级数据交换 | R4/R5 |
| IHE XDS | IHE | 跨企业文档共享 | 1.1 |
| DICOM | DICOM | 医学影像交换 | 3.0 |
| XDS.b | IHE | 文档存储和检索 | 1.1 |

### 6.2 交换协议

**数据交换协议栈**：

```
┌────────────────────────────────────────────────────────┐
│                   应用层协议                            │
│         (HL7 CDA, FHIR, IHE XDS, DICOM)                │
├────────────────────────────────────────────────────────┤
│                   消息层协议                            │
│              (HL7 v2.x, HL7 v3, SOAP)                  │
├────────────────────────────────────────────────────────┤
│                   传输层协议                            │
│              (HTTP/HTTPS, MLLP, DICOM)                 │
├────────────────────────────────────────────────────────┤
│                   安全层协议                            │
│           (TLS/SSL, WS-Security, SAML)                 │
└────────────────────────────────────────────────────────┘
```

**交换模式**：

1. **点对点交换**：机构间直接数据交换
2. **区域平台交换**：通过区域卫生信息平台交换
3. **云交换**：基于云平台的医疗数据交换
4. **API交换**：基于RESTful API的数据交换

### 6.3 安全传输

**安全传输要求**：

1. **身份认证**：双向SSL证书认证
2. **数据加密**：传输层加密（TLS 1.3）
3. **完整性校验**：数字签名验证
4. **访问控制**：基于角色的访问控制（RBAC）
5. **审计追踪**：完整的交换日志记录

---

## 7. 应用场景

### 7.1 电子病历管理

**病历管理功能**：

- **病历创建**：支持多种方式创建病历
- **病历查询**：多维度病历检索
- **病历修改**：受控的病历修改流程
- **病历归档**：自动归档和存储管理
- **病历调阅**：跨机构病历调阅

### 7.2 临床决策支持

**CDS应用场景**：

- **用药提醒**：药物相互作用、过敏提醒
- **诊断辅助**：基于指南的诊断建议
- **检验提醒**：重复检查、必查项目提醒
- **治疗路径**：基于循证医学的治疗路径

### 7.3 医疗质量监控

**质量监控指标**：

- **病历质量评分**：完整性、规范性评分
- **诊疗规范符合度**：临床路径执行情况
- **抗菌药物使用**：DDD值、使用强度监控
- **手术并发症率**：手术质量监控

### 7.4 科研数据分析

**科研数据应用**：

- **队列研究**：基于EMR数据的回顾性研究
- **药物警戒**：不良反应监测和分析
- **流行病学研究**：疾病分布和趋势分析
- **真实世界研究**：RWS数据支持

---

## 8. 思维导图

```text
EMR Schema
│
├─ 系统架构
│   ├─ 数据层 (Oracle/MongoDB/HBase)
│   ├─ 业务逻辑层 (Java/.NET)
│   └─ 表示层 (Web/移动端)
│
├─ 病历结构
│   ├─ 门急诊病历
│   │   ├─ 病历头部
│   │   ├─ 主诉/现病史
│   │   ├─ 体格检查
│   │   ├─ 辅助检查
│   │   └─ 初步诊断
│   │
│   └─ 住院病历
│       ├─ 入院记录
│       ├─ 病程记录
│       ├─ 手术记录
│       ├─ 出院记录
│       └─ 护理记录
│
├─ 临床文档
│   ├─ CDA文档 (HL7 CDA R2/R3)
│   ├─ 文档模板库
│   └─ 文档版本管理
│
├─ 数据交换
│   ├─ HL7 CDA交换
│   ├─ FHIR API交换
│   ├─ IHE XDS交换
│   └─ 安全传输 (TLS/SSL)
│
└─ 应用场景
    ├─ 病历管理
    ├─ 临床决策支持
    ├─ 质量监控
    └─ 科研分析
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
