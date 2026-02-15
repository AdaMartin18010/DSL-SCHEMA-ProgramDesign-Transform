# 医疗设备Schema标准对标

## 📑 目录

- [医疗设备Schema标准对标](#医疗设备schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. DICOM标准](#2-dicom标准)
    - [2.1 DICOM概述](#21-dicom概述)
    - [2.2 DICOM信息模型](#22-dicom信息模型)
    - [2.3 DICOM与设备Schema映射](#23-dicom与设备schema映射)
  - [3. HL7 FHIR设备资源](#3-hl7-fhir设备资源)
    - [3.1 FHIR Device资源](#31-fhir-device资源)
    - [3.2 FHIR DeviceDefinition资源](#32-fhir-devicedefinition资源)
    - [3.3 映射关系](#33-映射关系)
  - [4. IEC 62304标准](#4-iec-62304标准)
    - [4.1 软件生命周期过程](#41-软件生命周期过程)
    - [4.2 安全分类](#42-安全分类)
    - [4.3 合规性要求](#43-合规性要求)
  - [5. FDA UDI系统](#5-fda-udi系统)
    - [5.1 UDI法规要求](#51-udi法规要求)
    - [5.2 GUDID数据库](#52-gudid数据库)
    - [5.3 国内UDI实施](#53-国内udi实施)
  - [6. ISO 13485标准](#6-iso-13485标准)
    - [6.1 质量管理体系要求](#61-质量管理体系要求)
    - [6.2 设备管理要求](#62-设备管理要求)
  - [7. 国内标准](#7-国内标准)
    - [7.1 医疗器械唯一标识](#71-医疗器械唯一标识)
    - [7.2 医疗器械监督管理条例](#72-医疗器械监督管理条例)
  - [8. 标准对比矩阵](#8-标准对比矩阵)
  - [9. 标准发展趋势](#9-标准发展趋势)

---

## 1. 标准体系概述

医疗设备标准体系分为六个层次：

```
┌─────────────────────────────────────────────────────────────────┐
│                     法规层                                      │
│         (FDA UDI, 国内UDI, 医疗器械监督管理条例)                    │
├─────────────────────────────────────────────────────────────────┤
│                     质量管理标准层                               │
│              (ISO 13485, FDA QSR, GMP)                          │
├─────────────────────────────────────────────────────────────────┤
│                     软件生命周期标准层                           │
│              (IEC 62304, IEC 62366, ISO 14971)                  │
├─────────────────────────────────────────────────────────────────┤
│                     数据交换标准层                               │
│              (DICOM, HL7 FHIR, IEEE 11073)                      │
├─────────────────────────────────────────────────────────────────┤
│                     安全标准层                                   │
│              (IEC 60601系列, ISO 14155, GB 9706)                │
├─────────────────────────────────────────────────────────────────┤
│                     测试与验证标准层                             │
│              (IEC 62353, IEC 61010, GB/T 14710)                 │
└─────────────────────────────────────────────────────────────────┘
```

**主要标准组织**：

| 组织 | 全称 | 主要标准 | 地域 |
|-----|------|---------|------|
| DICOM | Digital Imaging and Communications in Medicine | DICOM标准 | 国际 |
| HL7 | Health Level Seven | FHIR Device | 国际 |
| IEC | International Electrotechnical Commission | IEC 62304, IEC 60601 | 国际 |
| FDA | Food and Drug Administration | UDI, QSR | 美国 |
| ISO | International Organization for Standardization | ISO 13485, ISO 14971 | 国际 |
| NMPA | 国家药品监督管理局 | 医疗器械唯一标识 | 中国 |

---

## 2. DICOM标准

### 2.1 DICOM概述

**标准名称**：
Digital Imaging and Communications in Medicine (DICOM)

**发布组织**：NEMA (National Electrical Manufacturers Association)

**标准版本**：
- DICOM 3.0 (当前版本)
- 持续更新，2023版

**核心内容**：

- **数据结构和编码**：医学影像数据结构
- **网络通信协议**：影像传输协议
- **文件格式**：DICOM文件格式 (.dcm)
- **设备工作列表**：Modality Worklist
- **结构化报告**：DICOM SR

**Schema支持**：⭐⭐⭐⭐⭐

**参考链接**：
[DICOM标准官网](https://www.dicomstandard.org/)

### 2.2 DICOM信息模型

**DICOM信息模型层次**：

```
Patient (患者)
└── Study (检查)
    └── Series (序列)
        └── Image (图像)
```

**DICOM数据元素**：

| 标签 | 名称 | VR | 描述 |
|-----|------|-----|------|
| (0010,0010) | PatientName | PN | 患者姓名 |
| (0010,0020) | PatientID | LO | 患者ID |
| (0020,000D) | StudyInstanceUID | UI | 检查实例UID |
| (0020,000E) | SeriesInstanceUID | UI | 序列实例UID |
| (0008,0018) | SOPInstanceUID | UI | SOP实例UID |
| (0008,0060) | Modality | CS | 设备类型 |
| (0008,0070) | Manufacturer | LO | 制造商 |
| (0008,1090) | ManufacturerModelName | LO | 设备型号 |
| (0018,1000) | DeviceSerialNumber | LO | 设备序列号 |
| (0018,1020) | SoftwareVersions | LO | 软件版本 |

### 2.3 DICOM与设备Schema映射

**DICOM到设备Schema映射表**：

| DICOM Tag | DICOM名称 | 设备Schema属性 | 映射说明 |
|-----------|----------|---------------|---------|
| (0008,0070) | Manufacturer | device.manufacturer | 直接映射 |
| (0008,1090) | ManufacturerModelName | device.deviceModel | 直接映射 |
| (0018,1000) | DeviceSerialNumber | device.serialNumber | 直接映射 |
| (0018,1020) | SoftwareVersions | specifications.software.softwareVersion | 软件版本 |
| (0018,1008) | GantryID | device.deviceId | 设备ID |
| (0008,0060) | Modality | device.deviceType | 设备类型映射 |
| (0018,1030) | ProtocolName | device.specifications.performance.imaging.protocol | 协议名称 |
| (0018,0050) | SliceThickness | specifications.performance.imaging.sliceThickness | 层厚 |
| (0018,1100) | ReconstructionDiameter | specifications.performance.imaging.fieldOfView | 视野 |

**DICOM Modality到设备类型映射**：

```python
DICOM_MODALITY_MAP = {
    'CT': 'CT_SCANNER',
    'MR': 'MRI_SCANNER',
    'XR': 'X_RAY',
    'US': 'ULTRASOUND',
    'NM': 'NUCLEAR_MEDICINE',
    'PT': 'PET_SCANNER',
    'MG': 'MAMMOGRAPHY',
    'DX': 'DIGITAL_RADIOGRAPHY',
    'RF': 'FLUOROSCOPY',
    'XA': 'XRAY_ANGIOGRAPHY',
    'ES': 'ENDOSCOPY',
    'ECG': 'ECG_MACHINE',
    'EEG': 'EEG_MACHINE',
    'HD': 'HEMODIALYSIS',
    'US': 'ULTRASOUND'
}
```

---

## 3. HL7 FHIR设备资源

### 3.1 FHIR Device资源

**资源定义**：

FHIR Device资源表示一个物理设备、物质、软件或参与者。

**FHIR Device元素**：

| 元素 | 类型 | 描述 | Schema映射 |
|-----|------|-----|-----------|
| identifier | Identifier[] | 标识符 | device.identification |
| definition | Reference | 设备定义 | device.description |
| udiCarrier | DeviceUdiCarrier | UDI载体 | udi.carrier |
| status | code | 状态 | device.status |
| statusReason | CodeableConcept[] | 状态原因 | device.status.statusHistory |
| distinctIdentifier | string | 唯一标识符 | device.identification.serialNumber |
| manufacturer | string | 制造商 | device.description.manufacturer |
| manufactureDate | dateTime | 制造日期 | device.description.manufacturer.manufacturingDate |
| expirationDate | dateTime | 有效期 | udi.productionIdentifiers.expirationDate |
| lotNumber | string | 批号 | udi.productionIdentifiers.lotNumber |
| serialNumber | string | 序列号 | device.identification.serialNumber |
| deviceName | DeviceDeviceName[] | 设备名称 | device.description.deviceName |
| modelNumber | string | 型号 | device.description.deviceModel |
| partNumber | string | 部件号 | device.description.brand.catalogNumber |
| type | CodeableConcept | 类型 | device.description.deviceType |
| specialization | DeviceSpecialization[] | 专业化 | device.classification |
| version | DeviceVersion[] | 版本 | device.specifications.software |
| property | DeviceProperty[] | 属性 | device.specifications |
| patient | Reference | 患者 | device.location.currentLocation |
| owner | Reference | 所有者 | device.location.currentLocation |
| contact | ContactPoint[] | 联系方式 | device.location.currentLocation.responsiblePerson |
| location | Reference | 位置 | device.location.currentLocation |
| url | uri | URL | device.documentation |
| note | Annotation[] | 注释 | device.maintenance.notes |
| safety | CodeableConcept[] | 安全信息 | device.specifications.safety |
| parent | Reference | 父设备 | device.references.parentDevice |

### 3.2 FHIR DeviceDefinition资源

**资源定义**：

FHIR DeviceDefinition资源表示设备的设计规格，而非特定实例。

**主要元素**：

| 元素 | 类型 | 描述 | Schema映射 |
|-----|------|-----|-----------|
| identifier | Identifier[] | 标识符 | device.identification |
| udiDeviceIdentifier | DeviceDefinitionUdiDeviceIdentifier[] | UDI设备标识符 | udi.deviceIdentifier |
| manufacturerString | string | 制造商 | device.description.manufacturer |
| deviceName | DeviceDefinitionDeviceName[] | 设备名称 | device.description.deviceName |
| modelNumber | string | 型号 | device.description.deviceModel |
| classification | DeviceDefinitionClassification[] | 分类 | device.classification |
| specialization | DeviceDefinitionSpecialization[] | 专业化 | device.classification |
| hasPart | DeviceDefinitionHasPart[] | 组成部分 | device.references.childDevices |
| packaging | DeviceDefinitionPackaging[] | 包装 | udi.packaging |
| version | DeviceDefinitionVersion[] | 版本 | device.specifications |
| safety | CodeableConcept[] | 安全 | device.specifications.safety |
| shelfLifeStorage | ProductShelfLife[] | 保质期 | device.procurement.warrantyPeriod |
| physicalCharacteristics | ProdCharacteristic | 物理特性 | device.specifications.physical |
| languageCode | CodeableConcept | 语言代码 | device.description |
| capability | DeviceDefinitionCapability[] | 能力 | device.specifications.performance |
| property | DeviceDefinitionProperty[] | 属性 | device.specifications |
| owner | Reference | 所有者 | device.procurement |
| contact | ContactPoint[] | 联系方式 | device.location |
| url | uri | URL | device.documentation |
| onlineInformation | uri | 在线信息 | device.documentation |
| note | Annotation[] | 注释 | device.documentation |
| quantity | Quantity | 数量 | device.usage |
| parentDevice | Reference | 父设备 | device.references.parentDevice |
| material | DeviceDefinitionMaterial[] | 材料 | device.specifications.physical.materials |

### 3.3 映射关系

**FHIR Device到设备Schema映射**：

```python
FHIR_DEVICE_MAPPING = {
    "Device.identifier": "device.identification",
    "Device.udiCarrier": "udi.carrier",
    "Device.status": "device.status.operationalStatus",
    "Device.manufacturer": "device.description.manufacturer.manufacturerName",
    "Device.manufactureDate": "device.description.manufacturer.manufacturingDate",
    "Device.expirationDate": "udi.productionIdentifiers.expirationDate",
    "Device.lotNumber": "udi.productionIdentifiers.lotNumber",
    "Device.serialNumber": "device.identification.serialNumber",
    "Device.deviceName": "device.description.deviceName",
    "Device.modelNumber": "device.description.deviceModel",
    "Device.type": "device.description.deviceType",
    "Device.version": "device.specifications.software",
    "Device.property": "device.specifications",
    "Device.patient": "device.usage.usageLog.patient",
    "Device.location": "device.location.currentLocation",
    "Device.parent": "device.references.parentDevice",
    "Device.safety": "device.specifications.safety"
}

FHIR_DEVICEDEFINITION_MAPPING = {
    "DeviceDefinition.identifier": "device.identification",
    "DeviceDefinition.udiDeviceIdentifier": "udi.deviceIdentifier",
    "DeviceDefinition.manufacturerString": "device.description.manufacturer.manufacturerName",
    "DeviceDefinition.deviceName": "device.description.deviceName",
    "DeviceDefinition.modelNumber": "device.description.deviceModel",
    "DeviceDefinition.classification": "device.classification",
    "DeviceDefinition.packaging": "udi.packaging",
    "DeviceDefinition.physicalCharacteristics": "device.specifications.physical",
    "DeviceDefinition.capability": "device.specifications.performance",
    "DeviceDefinition.property": "device.specifications",
    "DeviceDefinition.material": "device.specifications.physical.materials"
}
```

---

## 4. IEC 62304标准

### 4.1 软件生命周期过程

**标准名称**：
IEC 62304 Medical device software – Software life cycle processes

**发布组织**：IEC (International Electrotechnical Commission)

**标准版本**：
- IEC 62304:2006
- IEC 62304:2006+AMD1:2015 (当前版本)

**软件安全分类**：

| 分类 | 描述 | 示例 | 医疗设备Schema关联 |
|-----|------|-----|------------------|
| Class A | 不可能造成伤害或健康损害 | 数据记录软件、报告软件 | 低风险设备 |
| Class B | 可能造成伤害或健康损害（非严重） | 生理监测系统、诊断图像处理 | 中等风险设备 |
| Class C | 可能导致死亡或严重伤害 | 生命支持系统、除颤器、输液泵 | 高风险设备 |

**软件生命周期活动**：

```dsl
schema SoftwareLifecycle {
  resourceType: String @value("SoftwareLifecycle") @required
  
  software: SoftwareInfo {
    softwareName: String @required
    version: String @required
    safetyClass: Enum { class_a, class_b, class_c } @required
    
    // 软件开发生命周期
    development: DevelopmentProcess {
      // 5.1 软件开发规划
      planning: DevelopmentPlanning {
        process: SoftwareProcess
        deliverables: List<String>
        schedule: ProjectSchedule
        resources: ResourcePlan
        riskManagement: RiskManagementIntegration
      }
      
      // 5.2 软件需求分析
      requirements: RequirementsAnalysis {
        softwareRequirements: List<SoftwareRequirement> {
          requirementId: String @required
          requirementDescription: String @required
          acceptanceCriteria: String
          priority: Enum { high, medium, low }
          verificationMethod: Enum { inspection, analysis, testing }
          traceability: List<String>  // 系统需求ID
        }
        systemRequirementsTraceability: TraceabilityMatrix
      }
      
      // 5.3 软件架构设计
      architecture: ArchitecturalDesign {
        softwareArchitecture: String
        components: List<SoftwareComponent> {
          componentName: String
          componentDescription: String
          interfaces: List<Interface>
          safetyClass: Enum { class_a, class_b, class_c }
        }
        riskControlMeasures: List<RiskControl>
        traceabilityToRequirements: TraceabilityMatrix
      }
      
      // 5.4 软件详细设计
      detailedDesign: DetailedDesign {
        units: List<SoftwareUnit> {
          unitName: String
          unitDescription: String
          algorithms: String
          dataStructures: String
          interfaces: List<Interface>
        }
        traceabilityToArchitecture: TraceabilityMatrix
      }
      
      // 5.5 软件单元实现和验证
      implementation: ImplementationAndVerification {
        sourceCode: List<SourceCodeFile>
        staticAnalysis: StaticAnalysisReport
        unitTests: List<UnitTest> {
          testId: String
          testObjective: String
          testProcedure: String
          testData: String
          expectedResults: String
          actualResults: String
          passFail: Boolean
        }
        codeReviews: List<CodeReview>
        traceabilityToDesign: TraceabilityMatrix
      }
      
      // 5.6 软件集成和集成测试
      integration: IntegrationAndTesting {
        integrationPlan: IntegrationPlan
        integrationTests: List<IntegrationTest>
        integrationTestReport: TestReport
        traceabilityToArchitecture: TraceabilityMatrix
      }
      
      // 5.7 软件系统测试
      systemTesting: SystemTesting {
        systemTestPlan: TestPlan
        systemTests: List<SystemTest>
        systemTestReport: TestReport
        traceabilityToRequirements: TraceabilityMatrix
      }
    }
    
    // 软件维护过程
    maintenance: MaintenanceProcess {
      problemReporting: List<ProblemReport>
      changeControl: ChangeControlProcess
      changeImplementation: List<ChangeImplementation>
      reVerificationAndReValidation: List<VerificationActivity>
    }
    
    // 软件风险管理
    riskManagement: SoftwareRiskManagement {
      riskAnalysis: RiskAnalysis
      riskEvaluation: RiskEvaluation
      riskControl: RiskControl {
        riskControlMeasures: List<RiskControlMeasure>
        verificationOfRiskControl: List<Verification>
        residualRiskEvaluation: RiskEvaluation
      }
      riskManagementReport: RiskManagementReport
    }
    
    // 软件配置管理
    configurationManagement: ConfigurationManagement {
      configurationItems: List<ConfigurationItem>
      changeControl: ChangeControlBoard
      versionControl: VersionControlSystem
      configurationAudits: List<ConfigurationAudit>
    }
    
    // 软件问题解决
    problemResolution: ProblemResolution {
      problemReports: List<ProblemReport>
      investigation: Investigation
      resolution: Resolution
      trendAnalysis: TrendAnalysis
    }
  }
}
```

### 4.2 安全分类

**安全分类决策树**：

```
软件是否直接控制医疗器械？
├── 否 → Class A (如：数据查看软件)
└── 是 → 是否可能导致伤害？
    ├── 否 → Class A
    └── 是 → 是否可能导致严重伤害或死亡？
        ├── 否 → Class B (如：监护仪软件)
        └── 是 → Class C (如：除颤器软件)
```

**安全分类对开发过程的要求**：

| 活动 | Class A | Class B | Class C |
|-----|---------|---------|---------|
| 软件开发规划 | ✓ | ✓ | ✓ |
| 软件需求分析 | ✓ | ✓ | ✓ |
| 软件架构设计 | - | ✓ | ✓ |
| 软件详细设计 | - | ✓ | ✓ |
| 软件单元验证 | - | ✓ | ✓ |
| 软件集成和测试 | - | ✓ | ✓ |
| 软件系统测试 | ✓ | ✓ | ✓ |
| 风险管理 | ✓ | ✓ | ✓ |
| 可追溯性分析 | ✓ | ✓ | ✓ |

### 4.3 合规性要求

**合规性检查清单**：

```python
IEC_62304_COMPLIANCE = {
    "Class_A": {
        "required_processes": [
            "5.1 Software development planning",
            "5.2 Software requirements analysis",
            "5.7 Software system testing",
            "6.1 Establish software maintenance plan",
            "6.2 Problem and modification analysis",
            "7.1 Software risk management process",
            "8.1 Software configuration management process",
            "9.1 Software problem resolution process"
        ],
        "documentation_required": [
            "Software development plan",
            "Software requirements specification",
            "Software system test plan and report",
            "Risk management file",
            "Software configuration management plan"
        ]
    },
    "Class_B": {
        "required_processes": [
            "All Class A processes",
            "5.3 Software architectural design",
            "5.4 Software detailed design",
            "5.5 Software unit implementation and verification",
            "5.6 Software integration and integration testing"
        ],
        "additional_documentation": [
            "Software architectural design",
            "Software detailed design",
            "Software unit verification plan and report",
            "Software integration test plan and report"
        ]
    },
    "Class_C": {
        "required_processes": [
            "All Class B processes",
            "Enhanced rigor for all activities",
            "Additional verification and validation"
        ],
        "additional_requirements": [
            "Formal design reviews",
            "Independent verification and validation",
            "Comprehensive testing coverage",
            "Detailed hazard analysis"
        ]
    }
}
```

---

## 5. FDA UDI系统

### 5.1 UDI法规要求

**法规名称**：
Unique Device Identification System (21 CFR Part 830)

**发布机构**：FDA (Food and Drug Administration)

**合规时间表**：

| 设备类别 | 合规日期 |
|---------|---------|
| Class III (生命支持/生命维持) | 2014年9月24日 |
| 植入式、生命支持/生命维持 Class II | 2015年9月24日 |
| 其他 Class II | 2016年9月24日 |
| Class I 和非分类设备 | 2018年9月24日 |

**UDI组成**：

```
UDI = Device Identifier (DI) + Production Identifier(s) (PI)
```

| 组成部分 | 要求 | 示例 |
|---------|------|-----|
| DI | 必须 | 设备型号固定标识 |
| PI - Lot/Batch | 条件必须 | 批号 |
| PI - Serial Number | 条件必须 | 序列号 |
| PI - Expiration Date | 条件必须 | 有效期 |
| PI - Manufacturing Date | 可选 | 生产日期 |
| PI - Donation ID | HCT/P设备 | 捐献标识 |

### 5.2 GUDID数据库

**数据库名称**：
Global Unique Device Identification Database (GUDID)

**数据提交要求**：

| 数据元素 | 必须 | 条件必须 | 可选 |
|---------|------|---------|------|
| Primary DI | ✓ | | |
| Brand Name | ✓ | | |
| Version/Model | ✓ | | |
| Company Name | ✓ | | |
| Device Description | ✓ | | |
| GMDN Terms | ✓ | | |
| FDA Product Code | ✓ | | |
| 所有包装DI | | ✓ | |
| 储运条件 | | ✓ | |
| 一次性使用 | | ✓ | |
| 灭菌要求 | | ✓ | |
| 尺寸信息 | | | ✓ |
| MRI安全 | | ✓ | |
| 乳胶标识 | | ✓ | |

**GUDID Schema映射**：

```python
GUDID_SCHEMA_MAPPING = {
    "Primary DI": "udi.deviceIdentifier",
    "Brand Name": "device.description.deviceName",
    "Version/Model": "device.description.deviceModel",
    "Catalog Number": "device.description.brand.catalogNumber",
    "Company Name": "device.description.manufacturer.manufacturerName",
    "Device Description": "device.description.deviceDescription",
    "GMDN Terms": "device.classification.coding.gmdnCode",
    "FDA Product Code": "udi.database.productCodes.fdaProductCode",
    "Device Size": "device.specifications.physical.dimensions",
    "Storage Handling": "udi.database.deviceDescription.storageHandling",
    "Sterilization": "udi.database.deviceDescription.sterilization",
    "MRI Safety": "udi.database.deviceDescription.mriSafetyStatus",
    "Latex": "udi.database.deviceDescription.labeledContainsNRL"
}
```

### 5.3 国内UDI实施

**法规名称**：
医疗器械唯一标识系统规则

**发布机构**：
国家药品监督管理局 (NMPA)

**实施进度**：

| 时间节点 | 实施范围 |
|---------|---------|
| 2019年7月 | 部分高风险植入类医疗器械试点 |
| 2020年10月 | 首批实施品种（64个三类医疗器械） |
| 2021年1月 | 全部第三类医疗器械（含体外诊断试剂） |
| 2022年6月 | 第二批实施品种（部分二类医疗器械） |
| 2024年6月 | 第三批实施品种（部分二类医疗器械） |

**国内UDI结构**：

```
医疗器械唯一标识 = 产品标识 (DI) + 生产标识 (PI)

DI：静态信息，企业编码 + 产品编码
PI：动态信息，包括生产批号、序列号、生产日期、失效日期等
```

**发码机构**：

| 发码机构 | 标准 | 应用 |
|---------|------|-----|
| 中国物品编码中心 | GS1 | 通用 |
| 中关村工信二维码技术研究院 | MA码 | 国内推广 |
| 中国轻工业联合会 | ZIIOT | 轻工领域 |

---

## 6. ISO 13485标准

### 6.1 质量管理体系要求

**标准名称**：
ISO 13485 Medical devices — Quality management systems — Requirements for regulatory purposes

**发布组织**：ISO (International Organization for Standardization)

**标准版本**：
- ISO 13485:2003
- **ISO 13485:2016** (当前版本)

**核心要求**：

| 章节 | 标题 | 医疗设备Schema关联 |
|-----|------|------------------|
| 4 | 质量管理体系 | QualityManagementSchema |
| 5 | 管理职责 | GovernanceSchema |
| 6 | 资源管理 | ResourceManagementSchema |
| 7 | 产品实现 | ProductRealizationSchema |
| 8 | 测量、分析和改进 | QualityControlSchema |

### 6.2 设备管理要求

**设备管理相关条款**：

```dsl
schema ISO13485DeviceManagement {
  resourceType: String @value("ISO13485DeviceManagement") @required
  
  // 7.1.3 基础设施
  infrastructure: Infrastructure {
    facilities: List<Facility> {
      facilityId: String
      facilityType: String
      environmentalControl: EnvironmentalControl
      maintenance: MaintenanceSchedule
    }
    
    equipment: List<Equipment> {
      equipmentId: String
      equipmentType: Enum { production, testing, monitoring }
      calibrationStatus: CalibrationStatus
      maintenanceStatus: MaintenanceStatus
    }
  }
  
  // 7.5.1.2.2 安装活动
  installation: Installation {
    installationPlan: InstallationPlan
    installationQualification: IQDocument
    operationalQualification: OQDocument
    performanceQualification: PQDocument
    acceptanceCriteria: AcceptanceCriteria
  }
  
  // 7.6 监视和测量设备的控制
  monitoringEquipment: MonitoringEquipment {
    equipmentList: List<Equipment>
    calibrationSchedule: CalibrationSchedule
    calibrationRecords: List<CalibrationRecord>
    measurementUncertainty: MeasurementUncertainty
    traceability: TraceabilityToNationalStandards
  }
  
  // 8.2.5 监视和测量
  monitoring: Monitoring {
    processMonitoring: ProcessMonitoring
    productMonitoring: ProductMonitoring
    feedbackSystems: FeedbackSystems
  }
}
```

---

## 7. 国内标准

### 7.1 医疗器械唯一标识

**标准名称**：
YY/T 1630-2018 医疗器械唯一标识基本要求

**标准名称**：
YY/T 1681-2019 医疗器械唯一标识系统基础与术语

**数据载体**：

| 载体类型 | 标准 | 特点 |
|---------|------|-----|
| 一维条码 | GB/T 12904 | 成本低，容量小 |
| 二维条码 | GB/T 21049 (汉信码) | 容量大，容错强 |
| RFID | GB/T 35273 | 非接触读取，批量识别 |

### 7.2 医疗器械监督管理条例

**法规名称**：
医疗器械监督管理条例 (国务院令第739号)

**修订时间**：2021年

**主要内容**：

| 章节 | 主要内容 |
|-----|---------|
| 总则 | 监管体制、分类管理 |
| 医疗器械产品注册与备案 | 注册程序、技术要求 |
| 医疗器械生产 | 生产许可、质量管理 |
| 医疗器械经营与使用 | 经营许可、使用管理 |
| 不良事件的处理与医疗器械的召回 | 不良事件监测、召回管理 |
| 监督检查 | 监管措施、法律责任 |

---

## 8. 标准对比矩阵

**综合标准对比表**：

| 标准 | 组织 | 适用范围 | 数据交换 | 质量管理 | 软件安全 | 标识追溯 | 国际认可度 | 国内适用性 |
|-----|------|---------|---------|---------|---------|---------|-----------|-----------|
| **DICOM** | NEMA | 医学影像 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | - | - | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **HL7 FHIR** | HL7 | 通用医疗 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | - | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **IEC 62304** | IEC | 医疗软件 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | - | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **FDA UDI** | FDA | 美国市场 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | - | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **国内UDI** | NMPA | 中国市场 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | - | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **ISO 13485** | ISO | 医疗器械 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **IEC 60601** | IEC | 电气安全 | ⭐⭐ | ⭐⭐⭐⭐⭐ | - | - | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 9. 标准发展趋势

### 9.1 2024-2025年趋势

#### 9.1.1 UDI全球一体化

- **趋势**：UDI标准全球统一化
- **影响**：企业需要支持多地区UDI要求
- **发展**：IMDRF (国际医疗器械监管机构论坛) 推动全球协调

#### 9.1.2 软件即医疗器械(SaMD)

- **趋势**：独立软件作为医疗器械监管
- **影响**：IEC 62304应用范围扩大
- **发展**：IMDRF SaMD指南全球推广

#### 9.1.3 网络安全要求强化

- **趋势**：医疗设备网络安全成为强制性要求
- **影响**：IEC 81001-5-1等标准应用
- **发展**：FDA、NMPA加强网络安全审查

### 9.2 2025-2026年展望

#### 9.2.1 人工智能医疗器械

- **趋势**：AI/ML医疗器械标准体系建立
- **影响**：全生命周期监管要求
- **标准**：ISO/IEC 23053, FDA AI/ML指导原则

#### 9.2.2 数字疗法

- **趋势**：数字疗法产品标准化
- **影响**：软件监管框架完善
- **发展**：循证医学与软件结合

#### 9.2.3 物联网医疗设备

- **趋势**：IoMT设备标准化管理
- **影响**：网络安全和数据安全要求
- **标准**：IEEE 11073, ISO/IEEE 11073

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
