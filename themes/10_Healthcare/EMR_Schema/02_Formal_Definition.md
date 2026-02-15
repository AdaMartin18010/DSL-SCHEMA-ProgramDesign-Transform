# EMR Schema形式化定义

## 📑 目录

- [EMR Schema形式化定义](#emr-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 病历Schema定义](#2-病历schema定义)
    - [2.1 病历头部Schema](#21-病历头部schema)
    - [2.2 病历主体Schema](#22-病历主体schema)
    - [2.3 病历尾部Schema](#23-病历尾部schema)
  - [3. 患者信息Schema](#3-患者信息schema)
  - [4. 就诊记录Schema](#4-就诊记录schema)
  - [5. 医嘱Schema](#5-医嘱schema)
    - [5.1 药物医嘱](#51-药物医嘱)
    - [5.2 检查医嘱](#52-检查医嘱)
    - [5.3 治疗医嘱](#53-治疗医嘱)
  - [6. 检验检查Schema](#6-检验检查schema)
  - [7. 护理记录Schema](#7-护理记录schema)
  - [8. 类型系统](#8-类型系统)
  - [9. 约束规则](#9-约束规则)
  - [10. 转换函数](#10-转换函数)
  - [11. 形式化定理](#11-形式化定理)
    - [11.1 病历完整性定理](#111-病历完整性定理)
    - [11.2 数据一致性定理](#112-数据一致性定理)
    - [11.3 隐私安全定理](#113-隐私安全定理)

---

## 1. 形式化模型

**定义1（EMR Schema）**：
EMR Schema是一个七元组：

```text
EMR_Schema = (Patient, Visit, MedicalRecord, Order,
              LabResult, NursingRecord, SecurityPolicy)
```

其中：

- `Patient`：患者信息Schema
- `Visit`：就诊记录Schema
- `MedicalRecord`：病历文档Schema
- `Order`：医嘱Schema
- `LabResult`：检验检查结果Schema
- `NursingRecord`：护理记录Schema
- `SecurityPolicy`：安全策略Schema

**数学形式化**：

$$\mathcal{EMR} = \langle P, V, M, O, L, N, S \rangle$$

其中：
- $P$: 患者信息集合
- $V$: 就诊记录集合
- $M$: 病历文档集合
- $O$: 医嘱集合
- $L$: 检验检查结果集合
- $N$: 护理记录集合
- $S$: 安全策略集合

---

## 2. 病历Schema定义

**定义2（病历Schema）**：

```text
MedicalRecord = (Header, Body, Footer, Metadata, Version)
```

### 2.1 病历头部Schema

**形式化DSL定义**：

```dsl
schema EMRHeader {
  resourceType: String @value("EMRHeader") @required
  
  // 文档标识
  documentId: String @pattern("^EMR[0-9]{14}[A-Z0-9]{6}$") @required
  documentType: Enum { 
    outpatient, inpatient, emergency, 
    discharge, surgery, consultation 
  } @required
  
  // 患者信息
  patient: PatientReference {
    patientId: String @required
    idCard: String @pattern("^[0-9]{17}[0-9X]$")
    healthCard: String
    name: String @required @maxLength(50)
    gender: Enum { male, female, unknown } @required
    birthDate: Date @required
    age: Integer @min(0) @max(150)
  } @required
  
  // 就诊信息
  visit: VisitInfo {
    visitId: String @required
    visitType: Enum { first_visit, follow_up, referral, emergency } @required
    department: String @required
    departmentCode: String @pattern("^[A-Z0-9]{6,10}$")
    ward: String
    bedNo: String
    attendingDoctor: Practitioner @required
    residentDoctor: Practitioner
    visitTime: DateTime @required
    admissionTime: DateTime
    dischargeTime: DateTime
  } @required
  
  // 文档元数据
  metadata: DocumentMetadata {
    templateId: String
    templateVersion: String
    confidentiality: Enum { normal, sensitive, restricted } @default(normal)
    priority: Enum { routine, urgent, emergent } @default(routine)
  }
  
  // 创建信息
  createdBy: Practitioner @required
  createdAt: DateTime @required
  modifiedBy: Practitioner
  modifiedAt: DateTime
  version: Integer @default(1)
}
```

**Python实现**：

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
import re

class DocumentType(Enum):
    OUTPATIENT = "outpatient"
    INPATIENT = "inpatient"
    EMERGENCY = "emergency"
    DISCHARGE = "discharge"
    SURGERY = "surgery"
    CONSULTATION = "consultation"

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

class VisitType(Enum):
    FIRST_VISIT = "first_visit"
    FOLLOW_UP = "follow_up"
    REFERRAL = "referral"
    EMERGENCY = "emergency"

@dataclass
class PatientReference:
    """患者引用信息"""
    patient_id: str
    name: str
    gender: Gender
    birth_date: date
    id_card: Optional[str] = None
    health_card: Optional[str] = None
    age: Optional[int] = None
    
    def __post_init__(self):
        if self.id_card and not re.match(r'^[0-9]{17}[0-9X]$', self.id_card):
            raise ValueError(f"Invalid ID card format: {self.id_card}")
        if self.age is not None and (self.age < 0 or self.age > 150):
            raise ValueError(f"Invalid age: {self.age}")

@dataclass
class Practitioner:
    """医护人员信息"""
    practitioner_id: str
    name: str
    title: Optional[str] = None
    department: Optional[str] = None
    license_no: Optional[str] = None

@dataclass
class VisitInfo:
    """就诊信息"""
    visit_id: str
    visit_type: VisitType
    department: str
    attending_doctor: Practitioner
    visit_time: datetime
    department_code: Optional[str] = None
    ward: Optional[str] = None
    bed_no: Optional[str] = None
    resident_doctor: Optional[Practitioner] = None
    admission_time: Optional[datetime] = None
    discharge_time: Optional[datetime] = None

@dataclass
class EMRHeader:
    """EMR病历头部"""
    document_id: str
    document_type: DocumentType
    patient: PatientReference
    visit: VisitInfo
    created_by: Practitioner
    created_at: datetime
    template_id: Optional[str] = None
    template_version: Optional[str] = None
    confidentiality: str = "normal"
    priority: str = "routine"
    modified_by: Optional[Practitioner] = None
    modified_at: Optional[datetime] = None
    version: int = 1
    resource_type: str = "EMRHeader"
    
    def __post_init__(self):
        if not re.match(r'^EMR[0-9]{14}[A-Z0-9]{6}$', self.document_id):
            raise ValueError(f"Invalid document ID format: {self.document_id}")
        if self.version < 1:
            raise ValueError(f"Invalid version: {self.version}")
```

### 2.2 病历主体Schema

**形式化定义**：

```dsl
schema EMRBody {
  // 主诉
  chiefComplaint: TextBlock {
    content: String @maxLength(1000) @required
    onsetTime: DateTime
    severity: Enum { mild, moderate, severe }
  }
  
  // 现病史
  presentIllness: PresentIllness {
    content: String @maxLength(5000)
    onset: DateTime
    course: String
    associatedSymptoms: List<String>
    treatmentHistory: String
  }
  
  // 既往史
  pastHistory: PastHistory {
    diseases: List<PastDisease>
    surgeries: List<PastSurgery>
    allergies: List<Allergy>
    medications: List<CurrentMedication>
    familyHistory: FamilyHistory
    personalHistory: PersonalHistory
  }
  
  // 体格检查
  physicalExam: PhysicalExamination {
    general: GeneralExam {
      vitalSigns: VitalSigns {
        temperature: Decimal @min(30) @max(45)  // °C
        pulse: Integer @min(0) @max(300)  // bpm
        respiration: Integer @min(0) @max(100)  // rpm
        bloodPressure: BloodPressure {
          systolic: Integer @min(0) @max(300)
          diastolic: Integer @min(0) @max(200)
        }
        spo2: Decimal @min(0) @max(100)  // %
      }
      consciousness: Enum { alert, voice, pain, unresponsive }
      appearance: String
    }
    systems: SystemicExam {
      cardiovascular: String
      respiratory: String
      gastrointestinal: String
      neurological: String
      musculoskeletal: String
      skin: String
    }
  }
  
  // 辅助检查
  auxiliaryExams: List<AuxiliaryExamination> {
    examType: Enum { lab, imaging, ecg, endoscopy, pathology }
    examName: String @required
    results: String
    impressions: String
    abnormal: Boolean
  }
  
  // 诊断
  diagnoses: List<Diagnosis> @minItems(1) @required {
    diagnosisType: Enum { preliminary, final, differential }
    diagnosisCode: String @pattern("^ICD-10-[A-Z][0-9]{2}(\.[0-9]{1,2})?$")
    diagnosisName: String @required
    severity: Enum { mild, moderate, severe, critical }
    isPrimary: Boolean @default(false)
  }
  
  // 诊疗计划
  treatmentPlan: TreatmentPlan {
    orders: List<Order>
    procedures: List<Procedure>
    nursingPlan: String
    diet: Enum { normal, soft, liquid, npo }
    activity: Enum { ambulatory, bedrest, restricted }
    followUp: FollowUpPlan
    patientEducation: String
  }
}
```

### 2.3 病历尾部Schema

```dsl
schema EMRFooter {
  // 签名链
  signatures: List<Signature> @required {
    signer: Practitioner @required
    signatureType: Enum { author, reviewer, supervisor, patient }
    signatureTime: DateTime @required
    signatureData: Binary
    certificateId: String
    ipAddress: String
    deviceId: String
  }
  
  // 审核信息
  reviewInfo: ReviewInfo {
    reviewedBy: Practitioner
    reviewedAt: DateTime
    reviewStatus: Enum { pending, approved, rejected, revised }
    reviewComments: String
  }
  
  // 版本信息
  versionInfo: VersionInfo {
    version: Integer @required
    previousVersion: String
    changeSummary: String
    changeReason: String
  }
  
  // 审计信息
  auditInfo: AuditInfo {
    createdAt: DateTime @required
    createdBy: String @required
    modifiedAt: DateTime
    modifiedBy: String
    accessedBy: List<AccessRecord>
    printedAt: DateTime
    printedBy: String
  }
}
```

---

## 3. 患者信息Schema

**定义3（患者信息Schema）**：

```text
Patient = (Demographics, Identifiers, Contacts, Insurance, EmergencyContact)
```

**形式化定义**：

```dsl
schema Patient {
  resourceType: String @value("Patient") @required
  
  // 标识符
  identifiers: List<Identifier> @required {
    system: String @required  // "http://hl7.org/fhir/sid/mrn"
    value: String @required
    use: Enum { usual, official, temp, secondary, old }
    type: CodeableConcept {
      coding: List<Coding> {
        system: String
        code: String
        display: String
      }
    }
  }
  
  // 人口统计学信息
  demographics: Demographics {
    name: List<HumanName> @required {
      use: Enum { official, usual, temp, nickname, anonymous, old, maiden }
      family: String @required
      given: List<String>
      prefix: List<String>
      suffix: List<String>
    }
    gender: Enum { male, female, other, unknown } @required
    birthDate: Date @required
    birthPlace: Address
    nationality: CodeableConcept
    ethnicity: CodeableConcept
    maritalStatus: CodeableConcept
  }
  
  // 联系方式
  contacts: List<Contact> {
    system: Enum { phone, fax, email, pager, url, sms, other }
    value: String @required
    use: Enum { home, work, temp, old, mobile }
    rank: Integer
    period: Period
  }
  
  // 地址
  addresses: List<Address> {
    use: Enum { home, work, temp, old, billing }
    type: Enum { postal, physical, both }
    text: String
    line: List<String>
    city: String
    district: String
    state: String
    postalCode: String
    country: String
  }
  
  // 医保信息
  insurance: List<Insurance> {
    insuranceType: Enum { medical, commercial, self_pay, other }
    insuranceId: String @required
    insuranceOrg: Organization
    effectivePeriod: Period
    coverageLevel: Enum { basic, enhanced, premium }
  }
  
  // 紧急联系人
  emergencyContacts: List<EmergencyContact> {
    name: HumanName @required
    relationship: CodeableConcept
    phone: String @required
    address: Address
    priority: Integer @default(1)
  }
  
  // 健康状况
  healthStatus: HealthStatus {
    bloodType: Enum { A_positive, A_negative, B_positive, B_negative, 
                     AB_positive, AB_negative, O_positive, O_negative, unknown }
    organDonor: Boolean
    advanceDirectives: String
    advanceDirectiveDate: Date
  }
  
  // 扩展信息
  extensions: List<Extension>
}
```

---

## 4. 就诊记录Schema

**定义4（就诊记录Schema）**：

```text
Visit = (VisitInfo, ChiefComplaint, Diagnosis, Orders, Procedures, Discharge)
```

```dsl
schema Visit {
  resourceType: String @value("Visit") @required
  
  visitId: String @pattern("^V[0-9]{14}[A-Z0-9]{6}$") @required
  visitType: Enum { outpatient, inpatient, emergency, day_surgery, physical } @required
  
  // 时间信息
  timeInfo: VisitTimeInfo {
    registrationTime: DateTime @required
    triageTime: DateTime
    consultationStart: DateTime
    consultationEnd: DateTime
    admissionTime: DateTime
    dischargeTime: DateTime
    lengthOfStay: Integer  // 住院天数
  }
  
  // 分诊信息
  triageInfo: TriageInfo {
    triageLevel: Enum { level_1, level_2, level_3, level_4, level_5 }
    chiefComplaint: String
    vitalSigns: VitalSigns
    triageNurse: Practitioner
    triageTime: DateTime
  }
  
  // 就诊状态
  status: Enum { 
    planned, arrived, triaged, in_progress, on_hold, 
    completed, cancelled, entered_in_error 
  } @required
  
  // 费用信息
  billingInfo: BillingInfo {
    totalAmount: Decimal
    paidAmount: Decimal
    insuranceAmount: Decimal
    selfPayAmount: Decimal
    discountAmount: Decimal
    paymentStatus: Enum { pending, partial, paid, refunded }
  }
  
  // 关联资源
  medicalRecords: List<Reference>
  orders: List<Reference>
  labResults: List<Reference>
  imagingReports: List<Reference>
}
```

---

## 5. 医嘱Schema

**定义5（医嘱Schema）**：

```text
Order = (OrderInfo, OrderItem, Schedule, Execution, Monitoring)
```

### 5.1 药物医嘱

```dsl
schema MedicationOrder {
  resourceType: String @value("MedicationOrder") @required
  
  orderId: String @required
  orderType: Enum { medication } @required
  
  // 药物信息
  medication: Medication {
    drugCode: String @required @pattern("^YPC-[0-9]{9}$")
    drugName: String @required
    genericName: String
    dosageForm: Enum { tablet, capsule, injection, solution, ointment, patch }
    strength: String @required  // "500mg"
    manufacturer: String
    batchNumber: String
    expirationDate: Date
  }
  
  // 用法用量
  dosage: Dosage {
    route: CodeableConcept @required  // 给药途径
    method: CodeableConcept  // 给药方法
    timing: Timing {
      frequency: String  // "tid", "q8h"
      period: Integer
      periodUnit: Enum { s, min, h, d, wk, mo, a }
      timeOfDay: List<Time>
      when: List<Enum { AC, PC, CM, CD, CV, ACV, PCV, ACM, PCM }>
    }
    doseQuantity: Quantity {
      value: Decimal @required
      unit: String @required
      system: String
      code: String
    }
    maxDosePerPeriod: Ratio
    additionalInstruction: String
  }
  
  // 疗程
  duration: Duration {
    value: Decimal
    unit: Enum { d, wk, mo, a }
    startDate: Date
    endDate: Date
    totalQuantity: Decimal
  }
  
  // 执行信息
  execution: OrderExecution {
    status: Enum { draft, active, on_hold, revoked, completed, entered_in_error }
    priority: Enum { routine, urgent, asap, stat }
    authoredOn: DateTime @required
    requester: Practitioner @required
    performer: List<Practitioner>
    reasonCode: List<CodeableConcept>
    reasonReference: List<Reference>
    note: String
  }
  
  // 药物监测
  monitoring: MedicationMonitoring {
    therapeuticDrugMonitoring: Boolean
    monitoringParameters: List<String>
    targetLevels: Range
    adverseEventWatch: List<String>
    drugInteractions: List<DrugInteraction>
  }
  
  // 特殊标记
  flags: OrderFlags {
    isAllergen: Boolean @default(false)
    isHighRisk: Boolean @default(false)
    isControlledSubstance: Boolean @default(false)
    isAntimicrobial: Boolean @default(false)
    requiresDoubleCheck: Boolean @default(false)
  }
}
```

### 5.2 检查医嘱

```dsl
schema LabOrder {
  resourceType: String @value("LabOrder") @required
  
  orderId: String @required
  orderType: Enum { lab_order } @required
  
  // 检查项目
  testPanel: TestPanel {
    panelCode: String @required
    panelName: String @required
    tests: List<LabTest> @required {
      testCode: String @required
      testName: String @required
      loincCode: String
      specimenType: Enum { blood, urine, stool, sputum, csf, tissue, swab, other }
      specimenVolume: Quantity
      collectionMethod: String
      specialRequirements: String
    }
  }
  
  // 标本信息
  specimen: Specimen {
    specimenId: String
    specimenType: CodeableConcept
    collection: Collection {
      collector: Practitioner
      collectedDateTime: DateTime
      collectionSite: String
      collectionMethod: String
      quantity: Quantity
    }
    processing: List<Processing> {
      procedure: CodeableConcept
      additive: CodeableConcept
      timeDateTime: DateTime
    }
    container: List<Container> {
      type: CodeableConcept
      capacity: Quantity
      specimenQuantity: Quantity
      additive: CodeableConcept
    }
  }
  
  // 申请信息
  requisition: Requisition {
    clinicalInfo: String
    diagnosis: List<String>
    relevantHistory: String
    fastingStatus: Enum { fasting, non_fasting, unknown }
    urgency: Enum { routine, urgent, stat }
    requestedDateTime: DateTime @required
    requester: Practitioner @required
  }
  
  // 执行信息
  execution: OrderExecution {
    status: Enum { draft, active, collected, in_progress, completed, cancelled }
    scheduledDateTime: DateTime
    performedDateTime: DateTime
    performer: Practitioner
    location: Location
    note: String
  }
}
```

### 5.3 治疗医嘱

```dsl
schema ProcedureOrder {
  resourceType: String @value("ProcedureOrder") @required
  
  orderId: String @required
  orderType: Enum { procedure } @required
  
  // 治疗项目
  procedure: Procedure {
    procedureCode: String @required @pattern("^ICD-9-CM-[0-9]{2}\.[0-9]{1,2}$")
    procedureName: String @required
    procedureCategory: Enum { surgery, interventional, endoscopic, therapeutic, diagnostic }
    anesthesiaType: Enum { general, spinal, epidural, local, sedation, none }
    estimatedDuration: Integer  // 分钟
  }
  
  // 术前准备
  preOpPreparation: PreOpPreparation {
    requiredLabs: List<String>
    requiredImaging: List<String>
    medicationsToHold: List<String>
    fastingRequirements: String
    consentRequired: Boolean @default(true)
    anesthesiaEvaluation: Boolean @default(false)
  }
  
  // 手术安排
  scheduling: ProcedureScheduling {
    requestedDate: Date
    scheduledDateTime: DateTime
    operatingRoom: String
    surgeon: Practitioner @required
    assistants: List<Practitioner>
    anesthesiaProvider: Practitioner
    scrubNurse: Practitioner
    circulatingNurse: Practitioner
  }
  
  // 执行跟踪
  execution: ProcedureExecution {
    status: Enum { preparation, in_progress, suspended, aborted, completed }
    actualStartTime: DateTime
    actualEndTime: DateTime
    complications: List<String>
    bloodLoss: Quantity
    specimensObtained: List<String>
    implantsUsed: List<String>
  }
}
```

---

## 6. 检验检查Schema

**定义6（检验检查Schema）**：

```text
LabResult = (OrderReference, Specimen, TestResults, Interpretation, Report)
```

```dsl
schema LabResult {
  resourceType: String @value("LabResult") @required
  
  resultId: String @required
  basedOn: Reference @required  // 关联医嘱
  
  // 标本信息
  specimen: SpecimenInfo {
    specimenId: String @required
    specimenType: CodeableConcept @required
    collectedDateTime: DateTime @required
    receivedDateTime: DateTime
    collector: Practitioner
    collectionSite: String
    collectionMethod: String
    specimenCondition: Enum { adequate, hemolyzed, lipemic, icteric, inadequate }
  }
  
  // 检验结果
  results: List<TestResult> @required {
    testCode: String @required
    testName: String @required
    loincCode: String
    
    valueType: Enum { quantity, code, string, boolean, sample_data }
    
    // 定量结果
    valueQuantity: Quantity {
      value: Decimal
      unit: String
      system: String
      code: String
    }
    
    // 定性结果
    valueCodeableConcept: CodeableConcept {
      coding: List<Coding> {
        system: String
        code: String
        display: String
      }
    }
    
    valueString: String
    valueBoolean: Boolean
    
    // 参考范围
    referenceRange: List<ReferenceRange> {
      low: Quantity
      high: Quantity
      type: CodeableConcept
      appliesTo: CodeableConcept
      age: Range
      text: String
    }
    
    // 结果解释
    interpretation: List<CodeableConcept> {
      coding: List<Coding> {
        system: String @value("http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation")
        code: Enum { N, A, H, L, HH, LL, CR, NR, U, D, I, W, MS, VS }
      }
    }
    
    // 结果状态
    status: Enum { registered, preliminary, final, amended, corrected, cancelled }
    issued: DateTime
    performer: List<Practitioner>
    note: String
    
    // 危急值标记
    isCriticalValue: Boolean @default(false)
    criticalValueNotification: Notification {
      notifiedAt: DateTime
      notifiedTo: Practitioner
      notificationMethod: Enum { phone, pager, system, in_person }
      acknowledged: Boolean
      acknowledgedAt: DateTime
    }
  }
  
  // 报告信息
  report: LabReport {
    reportId: String @required
    status: Enum { preliminary, final, amended, appended, cancelled, entered_in_error }
    issued: DateTime @required
    performer: Organization
    resultInterpreter: Practitioner
    conclusion: String
    codedDiagnosis: List<CodeableConcept>
    presentedForm: List<Attachment>
  }
}
```

---

## 7. 护理记录Schema

**定义7（护理记录Schema）**：

```text
NursingRecord = (Assessment, Diagnosis, Plan, Implementation, Evaluation)
```

```dsl
schema NursingRecord {
  resourceType: String @value("NursingRecord") @required
  
  recordId: String @required
  recordType: Enum { 
    admission_assessment, shift_assessment, focus_assessment,
    progress_note, care_plan, discharge_summary 
  } @required
  
  // 护理评估
  assessment: NursingAssessment {
    assessmentTime: DateTime @required
    assessor: Practitioner @required
    
    // 身体评估
    physicalAssessment: PhysicalAssessment {
      generalAppearance: String
      vitalSigns: VitalSigns
      painAssessment: PainAssessment {
        painScale: Integer @min(0) @max(10)
        painLocation: String
        painQuality: Enum { sharp, dull, burning, aching, throbbing, cramping }
        painOnset: String
        painFactors: String
      }
      skinAssessment: SkinAssessment {
        color: Enum { normal, pale, flushed, cyanotic, jaundiced }
        turgor: Enum { normal, decreased, increased }
        integrity: Enum { intact, impaired }
        riskFactors: List<String>
      }
      respiratoryAssessment: RespiratoryAssessment
      cardiovascularAssessment: CardiovascularAssessment
      neurologicalAssessment: NeurologicalAssessment
    }
    
    // 功能评估
    functionalAssessment: FunctionalAssessment {
      adlScore: Integer @min(0) @max(100
      mobility: Enum { independent, assisted, dependent }
      nutrition: Enum { normal, impaired, at_risk }
      elimination: EliminationStatus
      sleep: SleepAssessment
    }
    
    // 心理社会评估
    psychosocialAssessment: PsychosocialAssessment {
      mentalStatus: MentalStatusExam
      emotionalStatus: Enum { stable, anxious, depressed, agitated, confused }
      copingMechanisms: String
      supportSystem: String
      culturalConsiderations: String
    }
    
    // 风险评估
    riskAssessment: RiskAssessment {
      fallRisk: FallRiskAssessment {
        riskScore: Integer
        riskLevel: Enum { low, moderate, high }
        interventions: List<String>
      }
      pressureInjuryRisk: PressureInjuryRisk {
        scaleUsed: Enum { Braden, Norton, Waterlow }
        score: Integer
        riskLevel: Enum { low, moderate, high }
      }
      dvtRisk: DVTRiskAssessment
      aspirationRisk: Boolean
      elopementRisk: Boolean
    }
  }
  
  // 护理诊断
  nursingDiagnoses: List<NursingDiagnosis> {
    diagnosisCode: String  // NANDA-I code
    diagnosisName: String @required
    relatedFactors: List<String>
    definingCharacteristics: List<String>
    priority: Enum { high, medium, low }
  }
  
  // 护理计划
  carePlan: CarePlan {
    goals: List<NursingGoal> {
      goalDescription: String @required
      targetDate: Date
      measurableOutcome: String
      priority: Enum { high, medium, low }
      goalStatus: Enum { active, achieved, partially_achieved, not_achieved }
    }
    
    interventions: List<NursingIntervention> {
      interventionCode: String  // NIC code
      interventionName: String @required
      description: String
      rationale: String
      frequency: String
      responsible: Practitioner
    }
  }
  
  // 护理实施
  implementations: List<NursingImplementation> {
    implementationTime: DateTime @required
    nurse: Practitioner @required
    interventionsPerformed: List<String>
    patientResponse: String
    complications: List<String>
    modifications: String
  }
  
  // 效果评价
  evaluations: List<NursingEvaluation> {
    evaluationTime: DateTime
    evaluator: Practitioner
    goalId: String
    goalStatus: Enum { achieved, partially_achieved, not_achieved, continued }
    evaluationNotes: String
    planModifications: String
  }
}
```

---

## 8. 类型系统

**定义8（EMR数据类型）**：

```text
EMR_Data_Type = Primitive | Complex | Reference | Temporal

Primitive = String | Integer | Decimal | Boolean
Complex = CodeableConcept | Quantity | Range | Ratio | Period | Address | HumanName
Reference = PatientRef | PractitionerRef | OrganizationRef | LocationRef
Temporal = Date | DateTime | Time | Instant
```

**基本类型定义**：

```dsl
// 编码概念
type CodeableConcept {
  coding: List<Coding> {
    system: String @pattern("^http://.*$")
    version: String
    code: String @required
    display: String
    userSelected: Boolean
  }
  text: String
}

// 数量
type Quantity {
  value: Decimal
  comparator: Enum { <, <=, >=, > }
  unit: String
  system: String @pattern("^http://.*$")
  code: String
}

// 范围
type Range {
  low: Quantity
  high: Quantity
}

// 比率
type Ratio {
  numerator: Quantity
  denominator: Quantity
}

// 时间段
type Period {
  start: DateTime
  end: DateTime
} @constraint("start <= end")

// 地址
type Address {
  use: Enum { home, work, temp, old, billing }
  type: Enum { postal, physical, both }
  text: String
  line: List<String>
  city: String
  district: String
  state: String
  postalCode: String
  country: String
  period: Period
}

// 人名
type HumanName {
  use: Enum { official, usual, temp, nickname, anonymous, old, maiden }
  text: String
  family: String
  given: List<String>
  prefix: List<String>
  suffix: List<String>
  period: Period
}

// 签名
type Signature {
  type: List<Coding>
  when: Instant @required
  who: Reference @required
  onBehalfOf: Reference
  targetFormat: String
  sigFormat: String
  data: Base64Binary
}
```

---

## 9. 约束规则

**约束1（病历完整性）**：

```text
∀ emr ∈ EMR:
  emr.header ≠ ∅
  ∧ emr.header.patient ≠ ∅
  ∧ emr.header.visit ≠ ∅
  ∧ emr.body ≠ ∅
  ∧ emr.body.diagnoses ≠ ∅
  ∧ emr.footer.signatures ≠ ∅
  ∧ validate_patient_id(emr.header.patient.patientId)
  ∧ validate_document_id(emr.header.documentId)
```

**约束2（医嘱有效性）**：

```text
∀ order ∈ Order:
  order.orderId ≠ ∅
  ∧ order.orderType ∈ {medication, lab_order, procedure, nursing}
  ∧ order.execution.requester ≠ ∅
  ∧ order.execution.authoredOn ≠ ∅
  ∧ (order.orderType = medication → order.medication ≠ ∅)
  ∧ (order.orderType = lab_order → order.testPanel ≠ ∅)
  ∧ (order.orderType = procedure → order.procedure ≠ ∅)
```

**约束3（检验结果有效性）**：

```text
∀ result ∈ LabResult:
  result.resultId ≠ ∅
  ∧ result.basedOn ≠ ∅
  ∧ result.results ≠ ∅
  ∧ ∀ r ∈ result.results:
      r.testCode ≠ ∅
      ∧ r.testName ≠ ∅
      ∧ (r.valueQuantity ≠ ∅ ∨ r.valueCodeableConcept ≠ ∅ ∨ r.valueString ≠ ∅)
      ∧ r.status ∈ {registered, preliminary, final, amended, corrected}
```

**约束4（护理记录时序性）**：

```text
∀ nr ∈ NursingRecord:
  nr.assessment.assessmentTime ≠ ∅
  ∧ (∀ i ∈ nr.implementations: i.implementationTime ≥ nr.assessment.assessmentTime)
  ∧ (∀ e ∈ nr.evaluations: e.evaluationTime ≥ nr.assessment.assessmentTime)
  ∧ (∀ i ∈ nr.carePlan.interventions: i.frequency ≠ ∅)
```

**约束5（隐私保护约束）**：

```text
∀ emr ∈ EMR:
  emr.header.metadata.confidentiality ∈ {normal, sensitive, restricted}
  ∧ (emr.header.metadata.confidentiality = restricted → 
     emr.footer.signatures.signer.certificateId ≠ ∅)
  ∧ access_control(emr, requester)
```

---

## 10. 转换函数

**函数1（CDA文档生成）**：

```text
generate_cda_document: EMR → CDA_Document
```

**Python实现**：

```python
def generate_cda_document(emr: MedicalRecord) -> str:
    """将EMR转换为HL7 CDA文档"""
    from xml.etree.ElementTree import Element, SubElement, tostring
    from datetime import datetime
    
    # 创建根元素
    root = Element("ClinicalDocument")
    root.set("xmlns", "urn:hl7-org:v3")
    
    # 添加文档头
    realm_code = SubElement(root, "realmCode")
    realm_code.set("code", "CN")
    
    type_id = SubElement(root, "typeId")
    type_id.set("root", "2.16.840.1.113883.1.3")
    type_id.set("extension", "POCD_HD000040")
    
    # 添加文档ID
    doc_id = SubElement(root, "id")
    doc_id.set("root", "2.16.156.10011.1.1")
    doc_id.set("extension", emr.header.document_id)
    
    # 添加文档代码
    code = SubElement(root, "code")
    code.set("code", "11506-3")
    code.set("codeSystem", "2.16.840.1.113883.6.1")
    code.set("displayName", "Progress note")
    
    # 添加标题
    title = SubElement(root, "title")
    title.text = "病程记录"
    
    # 添加创建时间
    effective_time = SubElement(root, "effectiveTime")
    effective_time.set("value", emr.header.created_at.strftime("%Y%m%d%H%M%S"))
    
    # 添加患者信息
    record_target = SubElement(root, "recordTarget")
    patient_role = SubElement(record_target, "patientRole")
    patient_id = SubElement(patient_role, "id")
    patient_id.set("root", "2.16.156.10011.1.12")
    patient_id.set("extension", emr.header.patient.patient_id)
    
    patient = SubElement(patient_role, "patient")
    name = SubElement(patient, "name")
    name.text = emr.header.patient.name
    
    # 添加文档内容
    component = SubElement(root, "component")
    structured_body = SubElement(component, "structuredBody")
    
    # 添加主诉
    section = SubElement(structured_body, "component")
    section_elem = SubElement(section, "section")
    section_code = SubElement(section_elem, "code")
    section_code.set("code", "10164-2")
    section_code.set("codeSystem", "2.16.840.1.113883.6.1")
    section_title = SubElement(section_elem, "title")
    section_title.text = "主诉"
    section_text = SubElement(section_elem, "text")
    section_text.text = emr.body.chief_complaint.content if emr.body.chief_complaint else ""
    
    return tostring(root, encoding="unicode")
```

**函数2（FHIR资源转换）**：

```text
convert_emr_to_fhir: EMR → List[FHIR_Resource]
```

**函数3（病历验证）**：

```text
validate_emr: EMR → ValidationResult
```

---

## 11. 形式化定理

### 11.1 病历完整性定理

**定理1（EMR数据完整性）**：

```text
∀ emr ∈ EMR:
  validate_emr(emr) = True
  → complete_patient_info(emr.header.patient)
  ∧ complete_visit_info(emr.header.visit)
  ∧ non_empty_diagnosis(emr.body.diagnoses)
  ∧ valid_signatures(emr.footer.signatures)
  ∧ temporal_consistency(emr)
```

**证明思路**：
1. 验证患者信息完整性：姓名、性别、出生日期等必填字段
2. 验证就诊信息完整性：就诊科室、医生、时间等
3. 验证诊断信息非空：至少包含一个诊断
4. 验证签名有效性：作者签名、审核签名
5. 验证时间一致性：创建时间 ≤ 修改时间

### 11.2 数据一致性定理

**定理2（跨资源引用一致性）**：

```text
∀ emr ∈ EMR, ∀ ref ∈ emr.references:
  resolve_reference(ref) ≠ ∅
  → referenced_resource_exists(ref)
  ∧ reference_type_matches(ref)
  ∧ circular_reference_free(emr, ref)
```

### 11.3 隐私安全定理

**定理3（隐私保护合规性）**：

```text
∀ emr ∈ EMR, ∀ access ∈ AccessRequest:
  authorized(access, emr)
  → rbac_check(access.user, emr.confidentiality)
  ∧ audit_logged(access)
  ∧ data_minimization(access, emr)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
