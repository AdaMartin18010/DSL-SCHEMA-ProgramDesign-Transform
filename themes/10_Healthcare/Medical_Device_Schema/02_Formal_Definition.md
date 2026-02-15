# 医疗设备Schema形式化定义

## 📑 目录

- [医疗设备Schema形式化定义](#医疗设备schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 设备Schema定义](#2-设备schema定义)
    - [2.1 设备基本信息Schema](#21-设备基本信息schema)
    - [2.2 设备技术参数Schema](#22-设备技术参数schema)
    - [2.3 设备位置管理Schema](#23-设备位置管理schema)
  - [3. 维护记录Schema](#3-维护记录schema)
    - [3.1 预防性维护Schema](#31-预防性维护schema)
    - [3.2 故障维修Schema](#32-故障维修schema)
    - [3.3 校准管理Schema](#33-校准管理schema)
  - [4. 质控数据Schema](#4-质控数据schema)
  - [5. UDI数据Schema](#5-udi数据schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 设备可用性定理](#91-设备可用性定理)
    - [9.2 维护完整性定理](#92-维护完整性定理)
    - [9.3 UDI追溯完整性定理](#93-udi追溯完整性定理)

---

## 1. 形式化模型

**定义1（医疗设备Schema）**：
医疗设备Schema是一个六元组：

```text
Medical_Device_Schema = (Device_Inventory, Maintenance_Management,
                         Quality_Control, UDI_System,
                         Safety_Management, Compliance_Tracking)
```

**数学形式化**：

$$\mathcal{MD} = \langle DI, MM, QC, UDI, SM, CT \rangle$$

其中：

- $DI$: 设备台账组件
- $MM$: 维护管理组件
- $QC$: 质量控制组件
- $UDI$: UDI系统组件
- $SM$: 安全管理组件
- $CT$: 合规追踪组件

---

## 2. 设备Schema定义

**定义2（设备Schema）**：

```text
Device = (Basic_Info, Technical_Specs, Location_Mgmt, Status_Mgmt, Usage_Tracking)
```

### 2.1 设备基本信息Schema

**形式化DSL定义**：

```dsl
schema Device {
  resourceType: String @value("Device") @required

  // 标识信息
  identification: DeviceIdentification {
    deviceId: String @pattern("^DEV[0-9]{12}$") @required
    assetNumber: String @required
    udi: String  // UDI标识符
    serialNumber: String @required
    batchNumber: String
    lotNumber: String
  }

  // 设备描述
  description: DeviceDescription {
    deviceName: String @required @maxLength(200)
    deviceType: DeviceType @required
    deviceModel: String @required
    modelVersion: String
    deviceDescription: String @maxLength(1000)

    // 厂商信息
    manufacturer: DeviceManufacturer {
      manufacturerName: String @required
      manufacturerId: String
      manufacturerAddress: Address
      manufacturerContact: ContactPoint
      manufacturingLocation: Location
      manufacturingDate: Date
    }

    // 品牌信息
    brand: DeviceBrand {
      brandName: String @required
      catalogNumber: String
      versionModelNumber: String
      referenceNumber: String
    }
  }

  // 分类信息
  classification: DeviceClassification {
    riskClass: Enum { class_i, class_iia, class_iib, class_iii } @required
    deviceClass: String

    // 标准代码
    coding: DeviceCoding {
      gmdnCode: String  // 全球医疗器械命名代码
      gmdnTermName: String
      umdnsCode: String  // 通用医疗器械命名系统代码
      umdnsTermName: String
      fdaProductCode: String
      fdaDeviceName: String
      snomedCt: List<String>
    }

    // 特殊属性
    specialAttributes: SpecialAttributes {
      implantable: Boolean @default(false)
      singleUse: Boolean @default(false)
      sterile: Boolean @default(false)
      latexFree: Boolean
      mriCompatible: Enum { mr_safe, mr_conditional, mr_unsafe }
      prescriptionRequired: Boolean
      otcAvailable: Boolean
    }
  }

  // 关联信息
  references: DeviceReferences {
    parentDevice: DeviceReference  // 父设备（模块化设备）
    childDevices: List<DeviceReference>  // 子设备
    compatibleDevices: List<DeviceReference>
    accessories: List<DeviceAccessory> {
      accessoryName: String
      accessoryModel: String
      required: Boolean
    }
  }

  // 状态
  status: DeviceOperationalStatus {
    status: Enum {
      active, inactive, entered_in_error,
      unknown, available, not_available
    } @required
    availabilityStatus: Enum { lost, damaged, destroyed, available }
  }
}

enum DeviceType {
  DIAGNOSTIC_EQUIPMENT    // 诊断设备
  THERAPEUTIC_EQUIPMENT   // 治疗设备
  MONITORING_EQUIPMENT    // 监护设备
  LIFE_SUPPORT_EQUIPMENT  // 生命支持设备
  SURGICAL_EQUIPMENT      // 手术设备
  LABORATORY_EQUIPMENT    // 实验室设备
  REHABILITATION_EQUIPMENT // 康复设备
  DENTAL_EQUIPMENT        // 口腔设备
  OPHTHALMIC_EQUIPMENT    // 眼科设备
  RADIOLOGY_EQUIPMENT     // 放射设备
  CARDIOLOGY_EQUIPMENT    // 心血管设备
  ANESTHESIA_EQUIPMENT    // 麻醉设备
  STERILIZATION_EQUIPMENT // 消毒设备
  EMERGENCY_EQUIPMENT     // 急救设备
  MOBILITY_EQUIPMENT      // 移动设备
  GENERAL_HOSPITAL_EQUIPMENT // 通用医疗设备
  CONSUMABLE              // 耗材
  ACCESSORY               // 配件
  SPARE_PART              // 备件
  SOFTWARE                // 软件
}
```

### 2.2 设备技术参数Schema

```dsl
schema DeviceSpecifications {
  resourceType: String @value("DeviceSpecifications") @required

  // 物理规格
  physical: PhysicalSpecifications {
    dimensions: PhysicalDimensions {
      length: Quantity
      width: Quantity
      height: Quantity
      weight: Quantity
      volume: Quantity
    }

    materials: List<Material> {
      materialName: String
      materialType: String
      biocompatible: Boolean
      sterilizable: Boolean
    }

    mobility: MobilitySpecs {
      mobile: Boolean
      transportWheels: Boolean
      ceilingMounted: Boolean
      wallMounted: Boolean
      tabletop: Boolean
      portable: Boolean
      handheld: Boolean
    }
  }

  // 电气规格
  electrical: ElectricalSpecifications {
    powerType: Enum { ac, dc, battery, universal }
    voltage: List<Quantity>  // 支持电压范围
    frequency: Quantity  // Hz
    powerConsumption: Quantity  // W
    battery: BatterySpecs {
      batteryType: String
      batteryCapacity: Quantity
      batteryLife: Duration
      rechargeable: Boolean
      hotSwappable: Boolean
    }
    backupPower: BackupPower {
      ups: Boolean
      upsRuntime: Duration
      generatorCompatible: Boolean
    }
  }

  // 性能规格
  performance: PerformanceSpecifications {
    operatingPrinciple: String
    measurementRange: List<Range>
    accuracy: Quantity
    precision: Quantity
    resolution: Quantity
    sensitivity: Quantity
    specificity: Quantity
    responseTime: Duration
    throughput: Quantity  // 处理能力/小时

    // 影像设备特殊参数
    imaging: ImagingSpecs {
      modality: Enum { xray, ct, mri, ultrasound, nuclear_medicine, pet }
      imageResolution: String
      fieldOfView: Quantity
      sliceThickness: Quantity
      contrastResolution: Quantity
      spatialResolution: Quantity
      temporalResolution: Quantity
      radiationDose: Quantity
    }

    // 监护设备特殊参数
    monitoring: MonitoringSpecs {
      parameters: List<String>
      samplingRate: Quantity
      alarmTypes: List<String>
      displayChannels: Integer
      trendStorage: Duration
    }
  }

  // 环境规格
  environmental: EnvironmentalSpecifications {
    operatingConditions: OperatingConditions {
      temperatureRange: Range
      humidityRange: Range
      atmosphericPressureRange: Range
      vibrationTolerance: String
      shockResistance: String
      electromagneticCompatibility: String
      ipRating: String  // 防护等级
    }

    storageConditions: StorageConditions {
      temperatureRange: Range
      humidityRange: Range
      maxStorageDuration: Duration
      specialRequirements: List<String>
    }
  }

  // 软件规格
  software: SoftwareSpecifications {
    softwareVersion: String
    operatingSystem: String
    minimumHardware: HardwareRequirements
    networkRequirements: NetworkRequirements {
      ethernet: Boolean
      wifi: Boolean
      bluetooth: Boolean
      cellular: Boolean
      minimumBandwidth: Quantity
    }
    dataInterface: List<String>
    dicomCompatible: Boolean
    hl7Compatible: Boolean
    fhirCompatible: Boolean
    cybersecurityFeatures: List<String>
  }

  // 安全规格
  safety: SafetySpecifications {
    safetyClass: Enum { class_i, class_ii, class_iii }
    electricalSafety: ElectricalSafety {
      leakageCurrent: Quantity
      groundResistance: Quantity
      insulationResistance: Quantity
      dielectricStrength: Quantity
    }
    safetyCertifications: List<SafetyCertification> {
      certificationBody: String
      certificationNumber: String
      certificationDate: Date
      expiryDate: Date
      scope: String
    }
    riskManagement: RiskManagementFile {
      riskAnalysis: Attachment
      riskEvaluation: Attachment
      riskControl: Attachment
      residualRisk: String
    }
  }
}
```

### 2.3 设备位置管理Schema

```dsl
schema DeviceLocation {
  resourceType: String @value("DeviceLocation") @required

  // 当前位置
  currentLocation: CurrentLocation {
    location: Location @required
    department: String @required
    building: String
    floor: String
    wing: String
    room: String
    exactPosition: String

    installedDate: Date
    installationOrder: String
    installationTechnician: Practitioner

    responsiblePerson: Practitioner @required
    alternateResponsible: Practitioner
    contactPhone: String
  }

  // 位置历史
  locationHistory: List<LocationHistory> {
    historyId: String @required
    fromLocation: Location
    toLocation: Location @required
    moveDate: DateTime @required
    moveReason: Enum {
      new_installation, relocation, repair,
      upgrade, storage, disposal, other
    }
    approvedBy: Practitioner
    executedBy: Practitioner
    transportMethod: String
    conditionBeforeMove: String
    conditionAfterMove: String
    notes: String
  }

  // 网络位置
  networkLocation: NetworkLocation {
    ipAddress: String @pattern("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    macAddress: String @pattern("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    hostname: String
    networkSegment: String
    vlan: String
    dhcpReservation: Boolean
    dicomAeTitle: String  // DICOM应用实体标题
    dicomPort: Integer
    hl7Interface: String
  }
}
```

---

## 3. 维护记录Schema

**定义3（维护管理Schema）**：

```text
Maintenance_Management = (Preventive_Maintenance, Corrective_Maintenance, Calibration_Management)
```

### 3.1 预防性维护Schema

```dsl
schema PreventiveMaintenancePlan {
  resourceType: String @value("PreventiveMaintenancePlan") @required

  plan: PMPlan {
    planId: String @required
    device: DeviceReference @required
    planName: String @required
    planDescription: String

    // 维护策略
    strategy: MaintenanceStrategy {
      strategyType: Enum { time_based, usage_based, condition_based, risk_based }
      riskLevel: Enum { low, medium, high, critical }
      criticalityScore: Integer @min(1) @max(10)

      // 基于时间的维护
      timeBased: TimeBasedSchedule {
        frequency: Integer @required
        frequencyUnit: Enum { days, weeks, months, years, operating_hours }
        lastMaintenanceDate: Date
        nextMaintenanceDate: Date @required
        maintenanceWindow: TimeRange
        scheduledDayOfWeek: Integer @min(1) @max(7)
        scheduledWeekOfMonth: Integer @min(1) @max(4)
        allowedVariance: Integer  // 允许的偏差天数
      }

      // 基于使用量的维护
      usageBased: UsageBasedSchedule {
        operatingHoursInterval: Decimal
        cycleCountInterval: Integer
        patientExaminationInterval: Integer
        currentOperatingHours: Decimal
        currentCycleCount: Integer
        currentPatientCount: Integer
        nextMaintenanceAtHours: Decimal
        nextMaintenanceAtCycles: Integer
      }

      // 基于状态的维护
      conditionBased: ConditionBasedSchedule {
        monitoredParameters: List<MonitoredParameter> {
          parameterName: String
          sensorType: String
          thresholdValue: Decimal
          currentValue: Decimal
          status: Enum { normal, warning, critical }
        }
        predictiveModel: String
        failureProbability: Decimal
        recommendedAction: String
      }
    }

    // 维护任务
    tasks: List<MaintenanceTask> {
      taskId: String @required
      taskName: String @required
      taskCategory: Enum {
        inspection, cleaning, lubrication, adjustment,
        replacement, calibration, software_update,
        safety_check, functional_test, performance_test
      }
      taskDescription: String @required
      procedureReference: String
      estimatedDuration: Duration
      requiredCompetency: String
      requiredCertifications: List<String>

      // 任务细节
      details: TaskDetails {
        inspectionPoints: List<String>
        cleaningRequirements: String
        lubricationPoints: List<String>
        adjustmentParameters: List<String>
        replaceableParts: List<String>
        calibrationPoints: List<String>
        softwareVersion: String
        safetyChecks: List<String>
        functionalTests: List<String>
      }

      // 资源需求
      resources: TaskResources {
        requiredTools: List<String>
        requiredConsumables: List<Consumable>
        requiredParts: List<Part>
        estimatedLaborHours: Decimal
        estimatedMaterialCost: Money
      }

      // 安全要求
      safety: TaskSafety {
        ppeRequired: List<String>
        lockoutTagoutRequired: Boolean
        electricalIsolationRequired: Boolean
        radiationSafetyRequired: Boolean
        biologicalSafetyRequired: Boolean
        specialPrecautions: String
      }

      acceptanceCriteria: String
      documentationRequired: List<String>
    }

    // 计划状态
    status: PlanStatus {
      planStatus: Enum { active, suspended, completed, cancelled }
      activationDate: Date
      suspensionReason: String
      totalTasks: Integer
      completedTasks: Integer
      overdueTasks: Integer
      complianceRate: Decimal
    }
  }
}
```

### 3.2 故障维修Schema

```dsl
schema CorrectiveMaintenanceRecord {
  resourceType: String @value("CorrectiveMaintenanceRecord") @required

  workOrder: WorkOrder {
    workOrderId: String @required
    device: DeviceReference @required

    // 工单信息
    ticketInfo: TicketInfo {
      ticketNumber: String @required
      creationDate: DateTime @required
      priority: Enum { low, medium, high, critical, emergency } @required
      category: Enum {
        malfunction, failure, degradation,
        user_error, safety_incident, preventive_maintenance
      }
      status: Enum {
        open, assigned, in_progress, pending_parts,
        awaiting_response, resolved, closed, cancelled
      }
    }

    // 故障报告
    failure: FailureReport {
      reportedBy: Practitioner @required
      reportDate: DateTime @required
      failureDateTime: DateTime @required
      discoveryMethod: Enum { user_report, routine_inspection, alarm, automatic_detection }

      failureDescription: String @required
      symptoms: List<String>
      errorMessages: List<String>
      errorCodes: List<String>

      operationalContext: String
      recentChanges: String
      frequency: Enum { first_time, intermittent, continuous, recurrent }

      impact: FailureImpact {
        operationalImpact: Enum { none, minor, moderate, major, complete_shutdown }
        clinicalImpact: Enum { none, delayed_care, compromised_care, patient_safety_risk }
        financialImpact: Money
        patientsAffected: Integer
        proceduresDelayed: Integer
      }

      safety: SafetyAssessment {
        safetyImplications: Boolean
        patientSafetyRisk: Enum { none, low, medium, high, critical }
        immediateActionTaken: String
        deviceQuarantined: Boolean
        incidentReportFiled: Boolean
        incidentReportNumber: String
      }
    }

    // 任务分配
    assignment: WorkAssignment {
      assignedTo: Practitioner
      assignedDate: DateTime
      assignedBy: Practitioner
      expectedCompletion: DateTime
      workType: Enum { in_house, external_service, manufacturer_service }
      serviceProvider: Organization
      serviceContract: String
    }

    // 诊断过程
    diagnosis: DiagnosisProcess {
      diagnosedBy: Practitioner
      diagnosisDate: DateTime
      diagnosticMethod: List<String>
      diagnosticTools: List<String>

      rootCause: String
      causeCategory: Enum {
        wear_and_tear, material_defect, design_flaw,
        manufacturing_defect, software_bug, user_error,
        inadequate_maintenance, environmental_factors,
        electrical_issues, mechanical_failure, unknown
      }

      contributingFactors: List<String>
      recurrenceRisk: Enum { low, medium, high }
      similarFailures: Integer
    }

    // 维修执行
    repair: RepairExecution {
      startedDate: DateTime
      completedDate: DateTime
      actualLaborHours: Decimal

      repairActions: List<String>
      partsReplaced: List<ReplacedPart> {
        partNumber: String
        partName: String
        manufacturer: String
        serialNumber: String
        lotNumber: String
        quantity: Integer
        unitCost: Money
        totalCost: Money
        warrantyInfo: String
        oldPartDisposition: Enum { scrapped, returned, retained }
      }

      softwareActions: SoftwareActions {
        softwareVersion: String
        updateInstalled: Boolean
        patchApplied: String
        configurationChanges: String
        dataBackupPerformed: Boolean
      }

      adjustments: List<Adjustment> {
        parameter: String
        oldValue: String
        newValue: String
        reason: String
      }

      testing: RepairTesting {
        testsPerformed: List<String>
        testResults: String
        calibrationPerformed: Boolean
        calibrationCertificate: String
        safetyChecks: List<String>
        performanceVerification: String
      }
    }

    // 维修结果
    outcome: RepairOutcome {
      resolution: Enum { repaired, replaced, upgraded, obsoleted, not_repaired }
      deviceStatus: Enum { operational, limited_functionality, non_operational }
      downtime: Duration
      totalCost: RepairCost {
        laborCost: Money
        partsCost: Money
        externalServiceCost: Money
        shippingCost: Money
        otherCosts: Money
        totalCost: Money
      }
      warrantyClaim: WarrantyClaim {
        claimFiled: Boolean
        claimNumber: String
        claimAmount: Money
        claimStatus: Enum { pending, approved, denied }
      }
    }

    // 验证和关闭
    closure: WorkOrderClosure {
      verifiedBy: Practitioner
      verificationDate: DateTime
      userTrainingRequired: Boolean
      userTrainingCompleted: Boolean
      documentationUpdated: Boolean
      preventiveMaintenanceUpdated: Boolean

      closedBy: Practitioner
      closureDate: DateTime
      closureCode: Enum { resolved, duplicate, no_fault_found, user_error, not_repairable }
      customerSatisfaction: Integer @min(1) @max(5)
      followUpRequired: Boolean
      followUpDate: Date

      lessonsLearned: String
      recommendations: String
    }
  }
}
```

### 3.3 校准管理Schema

```dsl
schema CalibrationManagement {
  resourceType: String @value("CalibrationManagement") @required

  calibration: Calibration {
    calibrationId: String @required
    device: DeviceReference @required

    // 校准计划
    plan: CalibrationPlan {
      calibrationType: Enum {
        internal, external, manufacturer, accredited_lab
      }
      calibrationStandard: String
      calibrationProcedure: String
      calibrationInterval: Duration
      lastCalibrationDate: Date
      nextCalibrationDate: Date @required
      toleranceLimit: Decimal
      uncertaintyBudget: String
    }

    // 校准执行
    execution: CalibrationExecution {
      calibrationDate: Date @required
      calibratedBy: Practitioner @required
      calibrationLocation: Location

      environmentalConditions: EnvConditions {
        temperature: Quantity
        humidity: Quantity
        atmosphericPressure: Quantity
      }

      referenceStandards: List<ReferenceStandard> {
        standardName: String
        standardNumber: String
        calibrationCertificate: String
        expiryDate: Date
        traceability: String
      }

      // 校准点
      calibrationPoints: List<CalibrationPoint> {
        pointId: String
        parameter: String
        nominalValue: Decimal
        measuredValue: Decimal
        referenceValue: Decimal
        deviation: Decimal
        tolerance: Decimal
        uncertainty: Decimal
        passFail: Enum { pass, fail, warning }
        adjustmentMade: Boolean
        adjustmentValue: Decimal
        adjustedReading: Decimal
      }

      // 校准结果
      results: CalibrationResults {
        overallResult: Enum { passed, passed_with_adjustment, failed } @required
        pointsPassed: Integer
        pointsFailed: Integer
        maximumDeviation: Decimal
        measurementUncertainty: Decimal

        adjustments: List<Adjustment> {
          parameter: String
          adjustmentMade: String
          adjustmentValue: Decimal
          verificationAfterAdjustment: Decimal
        }

        linearityCheck: String
        repeatability: Decimal
        reproducibility: Decimal
      }
    }

    // 校准证书
    certificate: CalibrationCertificate {
      certificateNumber: String @required
      certificateDate: Date @required
      certificateTemplate: String
      issuedBy: Organization
      accreditedBody: String
      accreditationNumber: String

      certificateContent: CertificateContent {
        deviceInfo: String
        calibrationProcedure: String
        calibrationResults: String
        measurementUncertainty: String
        traceabilityStatement: String
        environmentalConditions: String
        conclusions: String
      }

      certificateAttachments: List<Attachment>
      nextCalibrationDate: Date
      validityPeriod: Duration
    }

    // 状态管理
    status: CalibrationStatus {
      calibrationStatus: Enum { calibrated, due, overdue, suspended, not_required }
      daysUntilDue: Integer
      daysOverdue: Integer
      gracePeriod: Integer

      actions: CalibrationActions {
        reminderSent: Boolean
        reminderDate: Date
        escalationSent: Boolean
        escalationDate: Date
        deviceQuarantined: Boolean
        quarantineDate: Date
      }
    }
  }
}
```

---

## 4. 质控数据Schema

**定义4（质控数据Schema）**：

```dsl
schema QualityControlData {
  resourceType: String @value("QualityControlData") @required

  qcRecord: QCRecord {
    recordId: String @required
    device: DeviceReference @required
    standard: QCStandardReference @required

    // 测试信息
    testInfo: QCTestInfo {
      testDate: Date @required
      testTime: Time
      performedBy: Practitioner @required
      witnessedBy: Practitioner
      testLocation: Location

      deviceStatus: Enum { in_service, after_maintenance, after_repair, new_installation }
      softwareVersion: String
      firmwareVersion: String

      // 环境条件
      environment: TestEnvironment {
        temperature: Quantity
        humidity: Quantity
        powerSupply: String
        groundingStatus: String
        electromagneticInterference: String
      }

      // 测试设备
      testEquipment: List<TestEquipment> {
        equipmentName: String
        equipmentModel: String
        serialNumber: String
        calibrationDate: Date
        calibrationDue: Date
      }
    }

    // 测试结果
    results: List<QCResult> {
      parameterId: String @required
      parameterName: String @required

      // 标准值
      standardValue: Decimal
      tolerancePlus: Decimal
      toleranceMinus: Decimal
      warningLimitPlus: Decimal
      warningLimitMinus: Decimal
      actionLimitPlus: Decimal
      actionLimitMinus: Decimal

      // 测量值
      measuredValue: Decimal @required
      unit: String

      // 统计
      replicateMeasurements: List<Decimal>
      meanValue: Decimal
      standardDeviation: Decimal
      coefficientOfVariation: Decimal

      // 判定
      deviation: Decimal
      deviationPercent: Decimal
      resultStatus: Enum { pass, fail, warning, not_applicable }

      // 趋势
      previousValues: List<HistoricalValue> {
        date: Date
        value: Decimal
        status: Enum { pass, fail }
      }
      trend: Enum { stable, improving, deteriorating, fluctuating }

      notes: String
      attachments: List<Attachment>
    }

    // 总体评价
    evaluation: QCEvaluation {
      overallResult: Enum { pass, conditional_pass, fail } @required
      parametersTested: Integer
      parametersPassed: Integer
      parametersFailed: Integer
      parametersWarning: Integer

      failureAnalysis: String
      rootCause: String
      riskAssessment: String

      correctiveActions: List<String>
      preventiveActions: List<String>

      deviceDisposition: Enum { release, conditional_release, quarantine, remove_from_service }
      releaseConditions: String
      releasedBy: Practitioner
      releaseDate: DateTime
    }

    // 文档
    documentation: QCDocumentation {
      qcForm: Attachment
      rawData: Attachment
      calibrationCertificates: List<Attachment>
      trendCharts: List<Attachment>
      photos: List<Attachment>
    }

    // 跟踪
    followUp: QCFollowUp {
      reTestRequired: Boolean
      reTestDate: Date
      increasedMonitoring: Boolean
      monitoringFrequency: String
      incidentReportRequired: Boolean
      incidentReportNumber: String
    }
  }
}
```

---

## 5. UDI数据Schema

**定义5（UDI数据Schema）**：

```dsl
schema UDIData {
  resourceType: String @value("UDIData") @required

  udi: UDIComponents {
    // 设备标识符 (DI)
    deviceIdentifier: String @required
    diIssuer: Enum { gs1, hibcc, iccbba, gsa }
    diFormat: String

    // 生产标识符 (PI)
    productionIdentifiers: List<ProductionIdentifier> {
      piType: Enum { lot, serial, expiration, mfg_date, donation_id }
      piValue: String @required
    }

    // 载体
    carrier: UDICarrier {
      barcodeType: Enum { gs1_128, gs1_datamatrix, hibc, iccbba }
      barcodeData: String
      humanReadable: String
      rfid: RFIDInfo {
        rfidType: String
        epc: String
      }
      directPartMark: Boolean
    }

    // 包装层级
    packaging: PackagingHierarchy {
      packageLevel: Enum { base_package, intermediate, shipping }
      quantity: Integer
      childUDIs: List<String>
      parentUDI: String
    }
  }

  // 数据库信息
  database: UDIDatabaseEntry {
    gudidRecord: GUDIDRecord {
      publishDate: Date
      version: String
      brandName: String
      versionModelNumber: String
      catalogNumber: String
      companyName: String
      deviceDescription: String
      deviceFamily: String
      deviceSize: String
      deviceSizeType: String
      environmentalConditions: String
      gmdnTerms: List<String>
      labeledContainsNRL: Boolean
      labeledNoNRL: Boolean
      mriSafetyStatus: String
      rxPrescription: Boolean
      overTheCounter: Boolean
      singleUse: Boolean
      sterilization: SterilizationInfo
      storageHandling: StorageHandlingInfo
    }

    identifiers: UDIIdentifiers {
      primaryDI: String
      additionalDIs: List<String>
      previousDIs: List<String>
      deviceIdentifiers: List<DeviceIdentifier>
      packageDIs: List<PackageDI>
    }

    productCodes: ProductCodes {
      fdaProductCode: String
      fdaProductName: String
      ntn: String
    }

    characteristics: DeviceCharacteristicsUDI {
      kit: Boolean
      combinationProduct: Boolean
      deviceKit: Boolean
      devicePMP: Boolean
      singleUse: Boolean
      maxNumberReuses: Integer
      naturalRubberLatex: Boolean
      dimensions: DeviceDimensions
    }
  }

  // 追溯信息
  traceability: UDITraceability {
    manufacture: ManufactureTrace {
      manufacturer: Organization
      manufactureDate: Date
      manufactureLocation: Location
      lotNumber: String
      batchNumber: String
    }

    distribution: DistributionTrace {
      distributor: Organization
      distributionDate: Date
      supplyChain: List<DistributionNode> {
        nodeType: Enum { manufacturer, distributor, provider }
        organization: Organization
        date: Date
        document: String
      }
    }

    usage: UsageTrace {
      receivingFacility: Organization
      receiveDate: Date
      patient: PatientReference
      implantDate: Date
      explantDate: Date
      explantReason: String
      procedure: ProcedureReference
      operator: Practitioner
    }

    adverseEvent: AdverseEventTrace {
      eventReported: Boolean
      mdrNumber: String
      eventDescription: String
      eventDate: Date
      patientImpact: String
      deviceEvaluation: String
    }
  }
}
```

---

## 6. 类型系统

**定义6（医疗设备数据类型）**：

```text
Device_Data_Type = Primitive | Complex | Reference | Measurement | Financial

Primitive = String | Integer | Decimal | Boolean | Date | DateTime | Time
Complex = Quantity | Range | Period | Ratio | Address | Attachment
Reference = DeviceRef | PractitionerRef | LocationRef | OrganizationRef
Measurement = Length | Weight | Volume | Temperature | Pressure | Duration
Financial = Money | Currency
```

**基本类型定义**：

```dsl
// 数量类型
type Quantity {
  value: Decimal @required
  unit: String @required
  system: String
  code: String
}

// 范围类型
type Range {
  low: Quantity
  high: Quantity
}

// 货币类型
type Money {
  value: Decimal @required
  currency: String @default("CNY")
}

// 附件类型
type Attachment {
  contentType: String
  language: String
  data: Base64Binary
  url: String
  size: Integer
  hash: Base64Binary
  title: String
  creation: DateTime
}

// 签名类型
type Signature {
  type: List<Coding>
  when: DateTime @required
  who: Reference @required
  onBehalfOf: Reference
  targetFormat: String
  sigFormat: String
  data: Base64Binary
}
```

---

## 7. 约束规则

**约束1（设备标识唯一性）**：

```text
∀ d1, d2 ∈ Device:
  d1.deviceId = d2.deviceId → d1 = d2
  ∧ d1.serialNumber = d2.serialNumber → d1 = d2
  ∧ d1.udi ≠ ∅ → d1.udi = d2.udi → d1 = d2
```

**约束2（维护周期有效性）**：

```text
∀ pm ∈ PreventiveMaintenance:
  pm.plan.strategy.timeBased.nextMaintenanceDate ≥ today()
  ∧ pm.plan.strategy.timeBased.frequency > 0
  ∧ pm.plan.tasks ≠ ∅
```

**约束3（校准有效性）**：

```text
∀ cal ∈ Calibration:
  cal.execution.calibrationDate ≤ today()
  ∧ cal.certificate.nextCalibrationDate > cal.execution.calibrationDate
  ∧ cal.results.overallResult ∈ {passed, passed_with_adjustment}
  → device.status.calibrationStatus = calibrated
```

**约束4（质控参数范围）**：

```text
∀ qc ∈ QualityControl:
  ∀ result ∈ qc.results:
    result.measuredValue ≠ ∅
    ∧ (result.resultStatus = pass →
       |result.deviation| ≤ result.tolerance)
    ∧ (result.resultStatus = warning →
       result.warningLimitMinus ≤ result.deviation ≤ result.warningLimitPlus)
```

**约束5（UDI完整性）**：

```text
∀ udi ∈ UDI:
  udi.deviceIdentifier ≠ ∅
  ∧ udi.carrier.barcodeData ≠ ∅
  ∧ (udi.device.singleUse = true → udi.productionIdentifiers.serialNumber ≠ ∅)
  ∧ (udi.device.sterile = true → udi.productionIdentifiers.expirationDate ≠ ∅)
```

---

## 8. 转换函数

**函数1（UDI编码生成）**：

```text
generate_udi: Device_Info → UDI_String
```

**Python实现**：

```python
class UDIGenerator:
    """UDI生成器"""

    def generate_gs1_udi(self, device_info: Dict) -> str:
        """
        生成GS1标准UDI

        Args:
            device_info: 设备信息

        Returns:
            UDI字符串
        """
        # GS1 UDI结构: (01)GTIN(11)生产日期(17)有效期(10)批号(21)序列号

        gtin = device_info.get('gtin', '')
        mfg_date = device_info.get('manufacturingDate', '')
        exp_date = device_info.get('expirationDate', '')
        lot = device_info.get('lotNumber', '')
        serial = device_info.get('serialNumber', '')

        udi_parts = [f"(01){gtin}"]

        if mfg_date:
            udi_parts.append(f"(11){mfg_date}")
        if exp_date:
            udi_parts.append(f"(17){exp_date}")
        if lot:
            udi_parts.append(f"(10){lot}")
        if serial:
            udi_parts.append(f"(21){serial}")

        return ''.join(udi_parts)
```

**函数2（维护计划优化）**：

```text
optimize_maintenance_schedule: Device_List, Resource_Constraints → Optimized_Schedule
```

**函数3（设备健康评估）**：

```text
assess_device_health: Device, Maintenance_History, QC_History → Health_Score
```

---

## 9. 形式化定理

### 9.1 设备可用性定理

**定理1（设备可用性）**：

```text
∀ d ∈ Device:
  d.status.operationalStatus = active
  ∧ d.status.calibrationStatus ≠ overdue
  ∧ d.maintenance.nextDueDate > today() + 7_days
  → device_available(d)
```

### 9.2 维护完整性定理

**定理2（维护完整性）**：

```text
∀ d ∈ Device:
  complete_maintenance_history(d)
  → ∀ m ∈ d.maintenance:
      m.workOrderId ≠ ∅
      ∧ m.execution.date ≠ ∅
      ∧ m.outcome.status ≠ ∅
      ∧ m.closure.documentationUpdated = true
```

### 9.3 UDI追溯完整性定理

**定理3（UDI追溯完整性）**：

```text
∀ udi ∈ UDI:
  valid_traceability(udi)
  → udi.traceability.manufacture ≠ ∅
    ∧ (udi.device.implantable = true → udi.traceability.usage.patient ≠ ∅)
    ∧ (udi.traceability.adverseEvent.eventReported = true → udi.traceability.adverseEvent.mdrNumber ≠ ∅)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
