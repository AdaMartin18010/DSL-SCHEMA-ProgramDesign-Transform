# 医疗设备Schema概述

## 📑 目录

- [医疗设备Schema概述](#医疗设备schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 医疗设备Schema定义](#11-医疗设备schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 医疗设备Schema定义](#21-医疗设备schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. 设备管理系统](#3-设备管理系统)
    - [3.1 系统架构](#31-系统架构)
    - [3.2 设备台账管理](#32-设备台账管理)
    - [3.3 设备生命周期](#33-设备生命周期)
  - [4. 维护计划系统](#4-维护计划系统)
    - [4.1 预防性维护](#41-预防性维护)
    - [4.2 故障维修](#42-故障维修)
    - [4.3 维护记录](#43-维护记录)
  - [5. 质控管理系统](#5-质控管理系统)
    - [5.1 质控标准](#51-质控标准)
    - [5.2 质控执行](#52-质控执行)
    - [5.3 质控报告](#53-质控报告)
  - [6. UDI系统](#6-udi系统)
    - [6.1 UDI标识](#61-udi标识)
    - [6.2 UDI数据库](#62-udi数据库)
    - [6.3 UDI追溯](#63-udi追溯)
  - [7. 应用场景](#7-应用场景)
    - [7.1 设备采购管理](#71-设备采购管理)
    - [7.2 设备使用管理](#72-设备使用管理)
    - [7.3 设备报废管理](#73-设备报废管理)
    - [7.4 设备效益分析](#74-设备效益分析)
  - [8. 思维导图](#8-思维导图)

---

## 1. 核心结论

**医疗设备存在标准化的Schema体系**，为医疗机构提供完整的设备管理能力，支持设备全生命周期管理、质量控制和安全追溯。

### 1.1 医疗设备Schema定义

```text
Medical_Device_Schema = (Device_Inventory ⊕ Maintenance_Management
                         ⊕ Quality_Control ⊕ UDI_System
                         ⊕ Safety_Management ⊕ Compliance_Tracking)
                         × Regulatory_Standards × Security_Framework
```

### 1.2 标准依据

- **DICOM**：医学数字成像和通信标准
- **HL7 FHIR**：医疗设备资源标准
- **IEC 62304**：医疗器械软件生命周期过程
- **FDA UDI**：美国FDA唯一器械标识要求
- **ISO 13485**：医疗器械质量管理体系
- **GB/T 19971**：中国医疗器械唯一标识系统

---

## 2. 概念定义

### 2.1 医疗设备Schema定义

**医疗设备Schema**是描述医疗设备数据结构和业务流程的形式化规范，包括设备台账、维护保养、质量控制、UDI追溯等管理元素。

### 2.2 核心特征

1. **全生命周期管理**：从采购到报废的全程追踪
2. **预防性维护**：基于风险的维护策略
3. **质量控制**：符合法规要求的质量保证
4. **UDI追溯**：唯一标识和全程追溯
5. **安全管理**：设备安全和患者安全
6. **合规性**：满足国内外法规要求

### 2.3 Schema分类

- **设备台账Schema**：设备基本信息、技术参数、位置状态
- **维护管理Schema**：预防性维护、故障维修、校准管理
- **质控管理Schema**：质控计划、质控执行、质控报告
- **UDI管理Schema**：UDI标识、UDI数据库、追溯查询
- **安全管理Schema**：安全检测、风险评估、不良事件
- **效益分析Schema**：使用率、效益分析、成本核算

---

## 3. 设备管理系统

### 3.1 系统架构

**设备管理系统架构**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           应用层                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 设备台账     │ │ 维护管理     │ │ 质控管理     │ │ UDI管理      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 安全管理     │ │ 效益分析     │ │ 报表统计     │ │ 预警提醒     │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                           服务层                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 设备服务     │ │ 维护服务     │ │ 质控服务     │ │ UDI服务      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                           集成层                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ DICOM接口    │ │ HL7 FHIR接口 │ │ UDI数据库    │ │ 厂商接口     │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                           数据层                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 设备数据库   │ │ 维护数据库   │ │ 质控数据库   │ │ UDI数据库    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 设备台账管理

**设备台账Schema**：

```dsl
schema DeviceInventory {
  resourceType: String @value("DeviceInventory") @required

  // 设备基本信息
  device: DeviceBasicInfo {
    deviceId: String @pattern("^DEV[0-9]{12}$") @required
    assetNumber: String @required  // 资产编号
    deviceName: String @required @maxLength(200)
    deviceType: DeviceType @required
    deviceModel: String @required
    manufacturer: Organization @required
    serialNumber: String @required

    // 分类信息
    classification: DeviceClassification {
      riskClass: Enum { class_i, class_ii, class_iii } @required
      deviceClass: String
      gmdnCode: String  // 全球医疗器械命名代码
      umdnsCode: String  // 通用医疗器械命名系统代码
    }

    // 技术参数
    specifications: DeviceSpecifications {
      technicalParameters: List<TechnicalParameter> {
        parameterName: String @required
        parameterValue: String @required
        unit: String
        normalRange: Range
      }
      performanceCharacteristics: List<PerformanceCharacteristic>
      physicalDimensions: PhysicalDimensions
      powerRequirements: PowerRequirements
      environmentalRequirements: EnvironmentalRequirements
    }
  }

  // 采购信息
  procurement: ProcurementInfo {
    purchaseOrder: String
    purchaseDate: Date
    purchasePrice: Money
    vendor: Organization
    warrantyPeriod: Period
    warrantyExpiry: Date
    installationDate: Date
    acceptanceDate: Date
    depreciationMethod: String
    expectedLifespan: Integer  // 年
  }

  // 位置信息
  location: DeviceLocation {
    currentLocation: Location @required
    department: String @required
    building: String
    floor: String
    room: String
    responsiblePerson: Practitioner @required

    locationHistory: List<LocationHistory> {
      fromLocation: Location
      toLocation: Location
      moveDate: DateTime
      reason: String
      approvedBy: Practitioner
    }
  }

  // 状态管理
  status: DeviceStatus {
    operationalStatus: Enum {
      active, inactive, maintenance, malfunction,
      retired, destroyed, lost
    } @required
    availabilityStatus: Enum { available, in_use, reserved, unavailable }
    calibrationStatus: Enum { calibrated, due, overdue, not_required }

    statusHistory: List<StatusHistory> {
      fromStatus: String
      toStatus: String
      changeDate: DateTime
      reason: String
      changedBy: Practitioner
    }
  }

  // 使用信息
  usage: DeviceUsage {
    totalUsageHours: Decimal @default(0)
    totalUsageCount: Integer @default(0)
    lastUsageDate: DateTime
    averageDailyUsage: Decimal
    utilizationRate: Decimal @min(0) @max(1)

    usageLog: List<UsageRecord> {
      usageId: String
      patient: PatientReference
      procedure: ProcedureReference
      operator: Practitioner
      startTime: DateTime
      endTime: DateTime
      duration: Duration
      consumablesUsed: List<String>
      notes: String
    }
  }

  // 文档管理
  documentation: DeviceDocumentation {
    userManual: Attachment
    serviceManual: Attachment
    calibrationProcedures: Attachment
    maintenanceProcedures: Attachment
    regulatoryCertificates: List<Attachment>
    trainingMaterials: List<Attachment>
  }
}

enum DeviceType {
  DIAGNOSTIC_IMAGING     // 诊断影像设备
  PATIENT_MONITORING     // 患者监护设备
  LIFE_SUPPORT          // 生命支持设备
  SURGICAL_EQUIPMENT    // 手术设备
  LABORATORY_EQUIPMENT  // 实验室设备
  THERAPEUTIC_DEVICE    // 治疗设备
  INFUSION_PUMP         // 输液泵
  VENTILATOR           // 呼吸机
  DEFIBRILLATOR        // 除颤器
  ENDOSCOPE            // 内窥镜
  DIALYSIS_MACHINE     // 透析机
  ANESTHESIA_MACHINE   // 麻醉机
  OPERATING_TABLE      // 手术床
  STERILIZER           // 消毒设备
  ULTRASOUND           // 超声设备
  X_RAY                // X光设备
  CT_SCANNER           // CT设备
  MRI_SCANNER          // MRI设备
  OTHER                // 其他
}
```

### 3.3 设备生命周期

**设备生命周期管理**：

```
计划 → 采购 → 验收 → 安装 → 培训 → 使用 → 维护 → 更新/报废
```

| 阶段 | 主要活动 | Schema组件 |
|-----|---------|-----------|
| 计划 | 需求分析、预算编制、可行性研究 | DevicePlanning |
| 采购 | 招标、评标、合同签订 | ProcurementSchema |
| 验收 | 到货验收、性能验证、文档接收 | AcceptanceSchema |
| 安装 | 场地准备、设备安装、系统调试 | InstallationSchema |
| 培训 | 操作培训、维护培训、考核 | TrainingSchema |
| 使用 | 日常使用、性能监控、质控 | DeviceUsage |
| 维护 | 预防维护、故障维修、校准 | MaintenanceSchema |
| 更新/报废 | 性能评估、处置决策、资产清理 | DisposalSchema |

---

## 4. 维护计划系统

### 4.1 预防性维护

**预防性维护Schema**：

```dsl
schema PreventiveMaintenance {
  resourceType: String @value("PreventiveMaintenance") @required

  maintenancePlan: MaintenancePlan {
    planId: String @required
    device: DeviceReference @required
    planType: Enum { time_based, usage_based, condition_based, risk_based } @required

    // 维护周期
    schedule: MaintenanceSchedule {
      frequency: Enum { daily, weekly, monthly, quarterly, semi_annual, annual }
      intervalValue: Integer
      intervalUnit: Enum { days, weeks, months, years, operating_hours, cycles }
      lastMaintenanceDate: Date
      nextMaintenanceDate: Date @required
      maintenanceWindow: TimeRange
      estimatedDuration: Duration
    }

    // 维护内容
    tasks: List<MaintenanceTask> {
      taskId: String @required
      taskName: String @required
      taskDescription: String
      taskCategory: Enum {
        inspection, cleaning, lubrication, adjustment,
        replacement, calibration, software_update, safety_check
      }
      instructions: String
      requiredTools: List<String>
      requiredParts: List<String>
      estimatedTime: Duration
      safetyPrecautions: List<String>
      acceptanceCriteria: String
    }

    // 资源需求
    resources: MaintenanceResources {
      requiredSkills: List<String>
      requiredCertifications: List<String>
      assignedTechnicians: List<Practitioner>
      estimatedLaborHours: Decimal
      estimatedMaterialCost: Money
    }
  }

  // 维护执行
  execution: MaintenanceExecution {
    workOrderId: String @required
    scheduledDate: Date @required
    actualDate: Date

    // 执行团队
    team: MaintenanceTeam {
      leadTechnician: Practitioner @required
      assistingTechnicians: List<Practitioner>
      externalServiceProvider: Organization
    }

    // 任务执行
    taskResults: List<TaskResult> {
      taskId: String @required
      status: Enum { completed, partially_completed, skipped, failed } @required
      startTime: DateTime
      endTime: DateTime
      findings: String
      actionsTaken: String
      partsReplaced: List<String>
      measurements: List<Measurement>
      photos: List<Attachment>
      technicianSignature: Signature
    }

    // 维护结果
    outcome: MaintenanceOutcome {
      overallStatus: Enum { passed, passed_with_conditions, failed } @required
      deviceCondition: Enum { excellent, good, fair, poor, critical }
      issuesFound: List<String>
      recommendations: List<String>
      followUpRequired: Boolean
      followUpActions: List<String>
      nextMaintenanceDate: Date
    }

    // 验收
    acceptance: MaintenanceAcceptance {
      testedBy: Practitioner
      testResults: String
      acceptedBy: Practitioner
      acceptanceDate: DateTime
      comments: String
    }

    // 文档
    documentation: MaintenanceDocumentation {
      workOrderForm: Attachment
      checklist: Attachment
      testReports: List<Attachment>
      photos: List<Attachment>
      certificates: List<Attachment>
    }
  }
}
```

### 4.2 故障维修

**故障维修Schema**：

```dsl
schema CorrectiveMaintenance {
  resourceType: String @value("CorrectiveMaintenance") @required

  workOrder: WorkOrder {
    workOrderId: String @required
    device: DeviceReference @required
    reportType: Enum { malfunction, failure, user_error, safety_event }
    priority: Enum { low, medium, high, emergency } @required
    status: Enum { open, assigned, in_progress, pending_parts,
                  testing, completed, closed, cancelled }

    // 故障报告
    failureReport: FailureReport {
      reportedBy: Practitioner @required
      reportDate: DateTime @required
      failureDate: DateTime @required
      failureMode: String @required
      failureDescription: String @required
      symptoms: List<String>
      errorCodes: List<String>
      operationalContext: String
      patientImpact: Enum { none, minor, moderate, serious, critical }
      safetyImplications: Boolean
    }

    // 故障分析
    analysis: FailureAnalysis {
      rootCause: String
      causeCategory: Enum {
        wear_and_tear, operator_error, software_bug,
        electrical_failure, mechanical_failure, environmental,
        maintenance_deficiency, design_flaw, unknown
      }
      contributingFactors: List<String>
      recurrenceRisk: Enum { low, medium, high }
      analysisMethod: Enum { five_whys, fishbone, fmea, fault_tree }
      analyzedBy: Practitioner
      analysisDate: DateTime
    }

    // 维修执行
    repair: RepairExecution {
      assignedTo: Practitioner
      assignmentDate: DateTime
      startDate: DateTime
      completionDate: DateTime

      diagnosis: String
      repairActions: List<String>
      partsReplaced: List<ReplacedPart> {
        partNumber: String
        partName: String
        serialNumber: String
        quantity: Integer
        cost: Money
        warrantyInfo: String
      }

      laborHours: Decimal
      downtime: Duration
      totalCost: Money

      testingPerformed: List<String>
      testResults: String
      calibrationRequired: Boolean
      calibrationPerformed: Boolean
    }

    // 验证
    verification: RepairVerification {
      verifiedBy: Practitioner
      verificationDate: DateTime
      verificationMethod: String
      functionalTestPassed: Boolean
      safetyTestPassed: Boolean
      performanceTestPassed: Boolean
      releasedForUse: Boolean
    }
  }
}
```

### 4.3 维护记录

**维护记录管理**：

| 记录类型 | 内容 | 保存期限 |
|---------|------|---------|
| 预防性维护记录 | 维护计划、执行记录、检查结果 | 设备寿命+2年 |
| 故障维修记录 | 故障描述、维修过程、更换部件 | 设备寿命+2年 |
| 校准记录 | 校准数据、偏差分析、调整记录 | 设备寿命+2年 |
| 计量检定记录 | 检定证书、不合格处理 | 3个周期 |
| 性能验证记录 | 验收测试、性能测试 | 设备寿命+2年 |

---

## 5. 质控管理系统

### 5.1 质控标准

**质控标准Schema**：

```dsl
schema QualityControlStandard {
  resourceType: String @value("QualityControlStandard") @required

  standard: QCStandard {
    standardId: String @required
    standardName: String @required
    deviceType: DeviceType @required
    deviceModel: String

    // 适用法规
    applicableRegulations: List<Regulation> {
      regulationName: String
      regulationCode: String
      jurisdiction: Enum { china, usa, eu, japan, international }
      requirementCategory: String
      specificRequirements: String
    }

    // 质控参数
    parameters: List<QCParameter> {
      parameterId: String @required
      parameterName: String @required
      parameterDescription: String
      measurementMethod: String @required
      measurementUnit: String

      // 标准值
      standardValue: QCStandardValue {
        nominalValue: Decimal
        toleranceRange: Range
        upperLimit: Decimal
        lowerLimit: Decimal
        warningLimits: Range
        actionLimits: Range
      }

      // 测试频率
      testFrequency: Enum { daily, weekly, monthly, quarterly, annual, as_needed }
      testConditions: String
      requiredEquipment: List<String>
      requiredPhantoms: List<String>

      // 判定标准
      acceptanceCriteria: String
      passFailCriteria: String
    }

    // 质控程序
    procedure: QCProcedure {
      procedureDocument: Attachment
      version: String
      effectiveDate: Date
      steps: List<QCStep> {
        stepNumber: Integer
        stepDescription: String
        expectedResult: String
        acceptanceCriteria: String
      }
      safetyPrecautions: List<String>
      troubleshooting: List<TroubleshootingGuide>
    }
  }
}
```

### 5.2 质控执行

**质控执行Schema**：

```dsl
schema QualityControlExecution {
  resourceType: String @value("QualityControlExecution") @required

  qcRecord: QCRecord {
    recordId: String @required
    device: DeviceReference @required
    standard: QCStandardReference @required

    // 执行信息
    execution: QCExecution {
      scheduledDate: Date @required
      actualDate: Date
      performedBy: Practitioner @required
      witnessedBy: Practitioner

      // 环境条件
      environmentalConditions: EnvConditions {
        temperature: Quantity
        humidity: Quantity
        atmosphericPressure: Quantity
        powerSupplyStatus: String
        otherConditions: String
      }

      // 测试结果
      testResults: List<QCTestResult> {
        parameterId: String @required
        measuredValue: Decimal @required
        unit: String
        resultStatus: Enum { pass, fail, warning, not_tested }
        deviationFromStandard: Decimal
        deviationPercentage: Decimal

        // 重复测试
        repeatTests: List<RepeatTest> {
          testNumber: Integer
          measuredValue: Decimal
          resultStatus: Enum { pass, fail }
        }

        // 趋势分析
        trendAnalysis: TrendAnalysis {
          previousValues: List<Decimal>
          trendDirection: Enum { stable, increasing, decreasing, fluctuating }
          trendSignificance: String
        }

        notes: String
        attachments: List<Attachment>
      }

      // 总体结果
      overallResult: QCOverallResult {
        resultStatus: Enum { passed, passed_with_exception, failed } @required
        parametersPassed: Integer
        parametersFailed: Integer
        parametersWarning: Integer

        failureAnalysis: String
        correctiveActions: List<String>
        preventiveActions: List<String>

        deviceStatus: Enum { released, conditional_release, quarantined, removed }
        releaseAuthorizedBy: Practitioner
        releaseDate: DateTime
        conditionsOfRelease: String
      }
    }

    // 后续跟踪
    followUp: QCFollowUp {
      reTestRequired: Boolean
      reTestDate: Date
      monitoringRequired: Boolean
      monitoringPlan: String
      incidentReportRequired: Boolean
      incidentReportId: String
    }
  }
}
```

### 5.3 质控报告

**质控报告内容**：

```
质控报告应包含：
1. 设备基本信息
2. 质控标准依据
3. 测试条件记录
4. 各项参数测试结果
5. 趋势分析图表
6. 总体评价结论
7. 异常处理记录
8. 改进建议
9. 下次质控日期
```

---

## 6. UDI系统

### 6.1 UDI标识

**UDI标识Schema**：

```dsl
schema UDI {
  resourceType: String @value("UDI") @required

  // UDI基本结构
  udi: UDIBasic {
    // 设备标识符 (DI)
    deviceIdentifier: String @required
    diFormat: Enum {
      hibcc,     // HIBCC标准
      gs1,       // GS1标准
      iccbba     // ICCBBA标准 (ISBT 128)
    } @required

    // 生产标识符 (PI)
    productionIdentifiers: List<ProductionIdentifier> {
      piType: Enum {
        lot_number,        // 批号
        serial_number,     // 序列号
        expiration_date,   // 有效期
        manufacturing_date, // 生产日期
        donation_id        // 捐献标识 (人体细胞组织产品)
      } @required
      piValue: String @required
    }

    // 完整UDI
    fullUDI: String @required  // DI + PI 组合
    udiCarrier: UDICarrier {
      aidc: String  // 自动识别和数据采集 (条码)
      hrf: String   // 人工可读格式
      eudi: String  // 电子UDI (RFID等)
    }

    // 标识符状态
    status: UDIStatus {
      status: Enum { active, inactive, deprecated, recalled }
      effectiveDate: Date
      endDate: Date
    }
  }

  // UDI数据库信息
  databaseInfo: UDIDatabaseInfo {
    gudidEntry: GUDIDEntry {  // 全球UDID数据库条目
      publishDate: Date
      version: String
      packageLevel: Enum { base_package, higher_package }
    }

    deviceDescription: DeviceDescription {
      brandName: String
      versionModelNumber: String
      catalogNumber: String
      companyName: String
      deviceDescription: String
      deviceFamily: String
      deviceSize: String
      gmdnTerms: List<String>
      deviceSizes: List<DeviceSize>
      environmentalConditions: String
      labeledContainsNRL: Boolean
      labeledNoNRL: Boolean
      mriSafetyStatus: Enum { mr_safe, mr_conditional, mr_unsafe, insufficient_info }
      rxPrescription: Boolean
      overTheCounter: Boolean
      singleUse: Boolean
      sterilization: SterilizationInfo
      storageHandling: StorageHandlingInfo
    }

    identifiers: DeviceIdentifiers {
      primaryDI: String
      additionalDIs: List<String>
      directMarkers: List<String>
      packageDIs: List<PackageDI>
      previousDIs: List<String>
    }

    productCodes: ProductCodes {
      fdaProductCode: String
      fdaProductName: String
      ntn: String  // National Drug Code 或 National Health Related Item Code
    }

    characteristics: DeviceCharacteristics {
      kit: Boolean
      combinationProduct: Boolean
      deviceKit: Boolean
      devicePmp: Boolean
      singleUse: Boolean
      maxNumberReuses: Integer
      naturalRubberLatex: Boolean
      dimensions: DeviceDimensions
    }
  }

  // 追溯信息
  traceability: UDITraceability {
    manufacture: ManufactureInfo {
      manufacturer: Organization
      manufactureDate: Date
      manufactureLocation: Location
    }

    distribution: DistributionChain {
      distributor: Organization
      distributionDate: Date
      receivingFacility: Organization
      receivingDate: Date
      lotTrace: LotTraceability
    }

    usage: UsageTrace {
      patient: PatientReference
      procedure: ProcedureReference
      implantDate: Date
      explantDate: Date
      explantReason: String
    }

    recall: RecallInfo {
      recallNumber: String
      recallDate: Date
      recallReason: String
      recallStatus: Enum { ongoing, completed }
      actionRequired: String
    }
  }
}
```

### 6.2 UDI数据库

**UDI数据库Schema**：

```dsl
schema UDIDatabase {
  resourceType: String @value("UDIDatabase") @required

  // 数据库配置
  database: DatabaseConfig {
    databaseId: String @required
    databaseName: String @required
    databaseType: Enum { global, national, regional, institutional }
    jurisdiction: String @required
    regulatoryAuthority: Organization

    // 数据标准
    standards: List<Standard> {
      standardName: String
      standardVersion: String
      implementationDate: Date
    }
  }

  // UDI条目
  entries: List<UDIEntry> {
    entryId: String @required
    udi: UDI @required

    // 提交信息
    submission: SubmissionInfo {
      submitter: Organization @required
      submissionDate: DateTime @required
      submissionType: Enum { initial, update, correction, delete }
      submitterId: String
      regulatorySubmission: RegulatorySubmission
    }

    // 数据质量
    dataQuality: DataQuality {
      completeness: Decimal
      accuracy: Decimal
      timeliness: Decimal
      validationStatus: Enum { valid, invalid, pending_review }
      qualityIssues: List<String>
    }

    // 版本控制
    versioning: VersionControl {
      currentVersion: String
      versionHistory: List<VersionHistory>
      effectiveDate: Date
      endDate: Date
    }
  }

  // 查询服务
  queryService: QueryService {
    searchCapabilities: List<SearchCapability> {
      searchField: String
      searchType: Enum { exact, partial, range, fuzzy }
      supportedOperators: List<String>
    }

    api: APIConfig {
      apiVersion: String
      authentication: Enum { api_key, oauth, certificate }
      rateLimits: RateLimits
      supportedFormats: List<String>
    }
  }
}
```

### 6.3 UDI追溯

**UDI追溯流程**：

```
生产 → 包装 → 仓储 → 运输 → 入库 → 使用 → 患者
```

**追溯查询功能**：

1. **正向追溯**：从生产到患者
2. **反向追溯**：从患者到生产
3. **批量追溯**：按批号追溯
4. **时间追溯**：按时间段追溯

---

## 7. 应用场景

### 7.1 设备采购管理

**采购流程**：

- 需求评估和可行性研究
- 技术规格制定
- 招标和评标
- 合同谈判和签订
- 到货验收和安装

### 7.2 设备使用管理

**使用管理要点**：

- 操作规程制定
- 使用培训
- 使用记录
- 性能监控
- 安全管理

### 7.3 设备报废管理

**报废流程**：

```
报废申请 → 技术评估 → 审批 → 资产处置 → 账务处理 → 档案归档
```

### 7.4 设备效益分析

**效益分析指标**：

| 指标类别 | 指标名称 | 计算方法 |
|---------|---------|---------|
| 使用效率 | 设备利用率 | 实际使用时长/可用时长 |
| 经济效益 | 投资回收期 | 投资额/年净收益 |
| 社会效益 | 服务人次 | 年度检查/治疗人次 |
| 质量指标 | 故障率 | 故障次数/总使用次数 |

---

## 8. 思维导图

```text
Medical Device Schema
│
├─ 设备管理系统
│   ├─ 设备台账 (基本信息/采购/位置/状态)
│   ├─ 生命周期 (计划→采购→验收→使用→报废)
│   └─ 文档管理 (手册/证书/培训材料)
│
├─ 维护计划系统
│   ├─ 预防性维护 (计划/执行/记录)
│   ├─ 故障维修 (报修/维修/验证)
│   └─ 校准管理 (计划/执行/证书)
│
├─ 质控管理系统
│   ├─ 质控标准 (法规/参数/程序)
│   ├─ 质控执行 (测试/记录/判定)
│   └─ 质控报告 (趋势/异常/改进)
│
├─ UDI系统
│   ├─ UDI标识 (DI/PI/载体)
│   ├─ UDI数据库 (提交/查询/同步)
│   └─ UDI追溯 (全生命周期追溯)
│
└─ 应用场景
    ├─ 设备采购管理
    ├─ 设备使用管理
    ├─ 设备报废管理
    └─ 设备效益分析
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
