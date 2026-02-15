# 医院管理Schema形式化定义

## 📑 目录

- [医院管理Schema形式化定义](#医院管理schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 患者管理Schema](#2-患者管理schema)
    - [2.1 患者注册Schema](#21-患者注册schema)
    - [2.2 患者身份识别Schema](#22-患者身份识别schema)
    - [2.3 患者档案管理Schema](#23-患者档案管理schema)
  - [3. 预约挂号Schema](#3-预约挂号schema)
    - [3.1 预约请求Schema](#31-预约请求schema)
    - [3.2 号源Schema](#32-号源schema)
    - [3.3 预约确认Schema](#33-预约确认schema)
  - [4. 排班管理Schema](#4-排班管理schema)
    - [4.1 医生排班Schema](#41-医生排班schema)
    - [4.2 护士排班Schema](#42-护士排班schema)
    - [4.3 调班管理Schema](#43-调班管理schema)
  - [5. 资源调度Schema](#5-资源调度schema)
    - [5.1 床位管理Schema](#51-床位管理schema)
    - [5.2 手术室调度Schema](#52-手术室调度schema)
    - [5.3 检查设备调度Schema](#53-检查设备调度schema)
  - [6. 收费管理Schema](#6-收费管理schema)
  - [7. 类型系统](#7-类型系统)
  - [8. 约束规则](#8-约束规则)
  - [9. 转换函数](#9-转换函数)
  - [10. 形式化定理](#10-形式化定理)
    - [10.1 排班可行性定理](#101-排班可行性定理)
    - [10.2 资源分配最优性定理](#102-资源分配最优性定理)
    - [10.3 患者流转完整性定理](#103-患者流转完整性定理)

---

## 1. 形式化模型

**定义1（医院管理Schema）**：
医院管理Schema是一个八元组：

```text
Hospital_Management_Schema = (Patient_Management, Appointment_System,
                              Staff_Scheduling, Resource_Scheduling,
                              Charge_Management, Inventory_Management,
                              Quality_Control, Security_Policy)
```

**数学形式化**：

$$\mathcal{HM} = \langle PM, AS, SS, RS, CM, IM, QC, SP \rangle$$

其中：
- $PM$: 患者管理组件
- $AS$: 预约挂号系统
- $SS$: 员工排班系统
- $RS$: 资源调度系统
- $CM$: 收费管理系统
- $IM$: 库存管理系统
- $QC$: 质量控制组件
- $SP$: 安全策略组件

**系统约束**：

$$\forall hm \in \mathcal{HM}: valid(hm) \Rightarrow \bigwedge_{i} constraint_i(hm)$$

---

## 2. 患者管理Schema

**定义2（患者管理Schema）**：

```text
Patient_Management = (Patient_Registration, Identity_Management, 
                      Record_Management, Consent_Management)
```

### 2.1 患者注册Schema

**形式化DSL定义**：

```dsl
schema PatientRegistration {
  resourceType: String @value("PatientRegistration") @required
  
  // 注册标识
  registrationId: String @pattern("^REG[0-9]{14}[A-Z0-9]{6}$") @required
  registrationTime: DateTime @required
  registrationType: Enum { new_patient, returning_patient, transfer } @required
  
  // 患者基本信息
  patient: PatientDemographics {
    patientId: String @required
    mrn: String @pattern("^MRN[0-9]{10}$") @required  // 病历号
    
    // 身份信息
    identity: IdentityInfo {
      name: HumanName @required {
        family: String @required @maxLength(50)
        given: List<String> @maxLength(2)
        prefix: List<String>
        suffix: List<String>
      }
      gender: Enum { male, female, other, unknown } @required
      birthDate: Date @required
      birthPlace: Address
      nationality: CodeableConcept
      ethnicity: CodeableConcept
      maritalStatus: CodeableConcept
      occupation: String @maxLength(100)
      employer: String @maxLength(200)
    }
    
    // 证件信息
    identifiers: List<PatientIdentifier> @required {
      type: Enum { id_card, passport, birth_certificate, 
                   military_id, driver_license, other } @required
      value: String @required
      issuingAuthority: String
      issueDate: Date
      expirationDate: Date
      isPrimary: Boolean @default(false)
    }
    
    // 联系方式
    telecom: List<ContactPoint> {
      system: Enum { phone, mobile, email, fax } @required
      value: String @required
      use: Enum { home, work, temp, old } @default(home)
      rank: Integer
    }
    
    // 地址
    address: List<Address> {
      use: Enum { home, work, temp, old }
      type: Enum { postal, physical, both }
      text: String
      line: List<String> @maxLength(3)
      city: String @maxLength(50)
      district: String @maxLength(50)
      state: String @maxLength(50)
      postalCode: String @maxLength(10)
      country: String @default("CN")
      period: Period
    }
    
    // 紧急联系人
    emergencyContacts: List<EmergencyContact> {
      name: HumanName @required
      relationship: CodeableConcept @required
      telecom: List<ContactPoint> @minItems(1)
      address: Address
      priority: Integer @default(1)
    }
    
    // 保险信息
    insurance: List<InsuranceCoverage> {
      coverageType: Enum { medical, commercial, self_pay, other } @required
      insuranceOrg: Organization @required
      insuranceId: String @required
      groupNumber: String
      planType: String
      effectivePeriod: Period @required
      policyHolder: PatientReference
      dependents: List<PatientReference>
      copayPercentage: Decimal @min(0) @max(100)
      annualDeductible: Money
      annualMaximum: Money
    }
    
    // 健康状况
    healthStatus: HealthStatus {
      bloodType: Enum { A_positive, A_negative, B_positive, B_negative,
                       AB_positive, AB_negative, O_positive, O_negative, unknown }
      organDonor: Boolean
      advanceDirectives: Boolean
      languagePreference: List<String>
      communicationNeeds: List<String>
      disabilityStatus: List<String>
    }
  }
  
  // 注册渠道
  registrationChannel: RegistrationChannel {
    channelType: Enum { front_desk, phone, website, mobile_app, 
                       self_service_kiosk, wechat, alipay } @required
    location: Location
    staff: Practitioner
    deviceId: String
    ipAddress: String
    referrer: String
  }
  
  // 审核信息
  verification: RegistrationVerification {
    identityVerified: Boolean @default(false)
    verificationMethod: Enum { manual, automatic, document_scan, biometric }
    verifiedBy: Practitioner
    verifiedAt: DateTime
    remarks: String
  }
  
  // 隐私同意
  consent: PatientConsent {
    privacyConsentSigned: Boolean @default(false)
    treatmentConsentSigned: Boolean @default(false)
    researchConsentSigned: Boolean @default(false)
    marketingConsent: Boolean @default(false)
    consentDate: Date
    consentFormVersion: String
  }
}
```

**Python实现**：

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
import re
import uuid

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"

class RegistrationType(Enum):
    NEW_PATIENT = "new_patient"
    RETURNING_PATIENT = "returning_patient"
    TRANSFER = "transfer"

class IdentifierType(Enum):
    ID_CARD = "id_card"
    PASSPORT = "passport"
    BIRTH_CERTIFICATE = "birth_certificate"
    MILITARY_ID = "military_id"
    DRIVER_LICENSE = "driver_license"
    OTHER = "other"

@dataclass
class HumanName:
    """人名"""
    family: str
    given: List[str] = field(default_factory=list)
    prefix: List[str] = field(default_factory=list)
    suffix: List[str] = field(default_factory=list)
    
    def full_name(self) -> str:
        parts = self.prefix + [self.family] + self.given + self.suffix
        return ''.join(parts)

@dataclass
class Address:
    """地址"""
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "CN"
    line: List[str] = field(default_factory=list)
    use: str = "home"
    type: str = "physical"

@dataclass
class ContactPoint:
    """联系方式"""
    system: str  # phone, mobile, email, fax
    value: str
    use: str = "home"
    rank: Optional[int] = None

@dataclass
class PatientIdentifier:
    """患者标识"""
    id_type: IdentifierType
    value: str
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    is_primary: bool = False

@dataclass
class EmergencyContact:
    """紧急联系人"""
    name: HumanName
    relationship: str
    telecom: List[ContactPoint] = field(default_factory=list)
    address: Optional[Address] = None
    priority: int = 1

@dataclass
class InsuranceCoverage:
    """保险覆盖"""
    coverage_type: str  # medical, commercial, self_pay, other
    insurance_org: str
    insurance_id: str
    group_number: Optional[str] = None
    effective_start: Optional[date] = None
    effective_end: Optional[date] = None
    copay_percentage: Optional[float] = None

@dataclass
class PatientDemographics:
    """患者人口统计学信息"""
    patient_id: str
    mrn: str
    name: HumanName
    gender: Gender
    birth_date: date
    identifiers: List[PatientIdentifier] = field(default_factory=list)
    telecom: List[ContactPoint] = field(default_factory=list)
    address: List[Address] = field(default_factory=list)
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    insurance: List[InsuranceCoverage] = field(default_factory=list)
    birth_place: Optional[Address] = None
    nationality: Optional[str] = None
    ethnicity: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None

@dataclass
class PatientRegistration:
    """患者注册"""
    registration_id: str
    registration_time: datetime
    registration_type: RegistrationType
    patient: PatientDemographics
    channel_type: str
    location: Optional[str] = None
    staff: Optional[str] = None
    identity_verified: bool = False
    privacy_consent_signed: bool = False
    resource_type: str = "PatientRegistration"
    
    def __post_init__(self):
        # 生成注册ID
        if not self.registration_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            random_suffix = uuid.uuid4().hex[:6].upper()
            self.registration_id = f"REG{timestamp}{random_suffix}"
        
        # 生成MRN
        if not self.patient.mrn:
            self.patient.mrn = f"MRN{uuid.uuid4().int % 10000000000:010d}"
        
        # 验证身份证号
        for identifier in self.patient.identifiers:
            if identifier.id_type == IdentifierType.ID_CARD:
                if not self._validate_id_card(identifier.value):
                    raise ValueError(f"Invalid ID card: {identifier.value}")
    
    @staticmethod
    def _validate_id_card(id_card: str) -> bool:
        """验证身份证号"""
        if len(id_card) != 18:
            return False
        
        # 前17位必须是数字
        if not id_card[:17].isdigit():
            return False
        
        # 最后一位可以是数字或X
        if not (id_card[17].isdigit() or id_card[17].upper() == 'X'):
            return False
        
        # 校验位验证
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
        check_code = check_codes[sum_value % 11]
        
        return id_card[17].upper() == check_code
```

### 2.2 患者身份识别Schema

```dsl
schema PatientIdentityManagement {
  resourceType: String @value("PatientIdentityManagement") @required
  
  // 患者主索引
  mpi: MasterPatientIndex {
    mpiId: String @required
    
    // 关联标识
    linkedIdentifiers: List<LinkedIdentifier> {
      identifier: PatientIdentifier @required
      sourceSystem: String @required
      sourceId: String @required
      linkType: Enum { primary, secondary, merged, duplicate }
      linkStatus: Enum { active, inactive, pending_review }
      linkedAt: DateTime
      linkedBy: Practitioner
    }
    
    // 身份匹配规则
    matchingRules: List<MatchingRule> {
      ruleId: String @required
      ruleName: String @required
      ruleType: Enum { deterministic, probabilistic }
      criteria: List<MatchingCriterion> {
        field: String @required
        weight: Decimal @min(0) @max(1)
        matchType: Enum { exact, fuzzy, phonetic, date_range }
        threshold: Decimal
      }
      totalThreshold: Decimal @min(0) @max(1)
      autoLink: Boolean @default(false)
    }
    
    // 匹配结果
    matchResults: List<MatchResult> {
      queryPatient: PatientReference @required
      matchedPatients: List<MatchedPatient> {
        patient: PatientReference @required
        matchScore: Decimal @min(0) @max(1)
        matchingFields: List<String>
        matchType: Enum { exact, probable, possible }
        decision: Enum { auto_linked, manual_review, rejected }
      }
      matchTime: DateTime @required
      matchAlgorithm: String
    }
    
    // 合并历史
    mergeHistory: List<MergeRecord> {
      mergeId: String @required
      sourcePatient: PatientReference @required
      targetPatient: PatientReference @required
      mergedAt: DateTime @required
      mergedBy: Practitioner @required
      mergeReason: String
      unmergeAllowed: Boolean @default(false)
    }
  }
  
  // 身份验证
  identityVerification: IdentityVerification {
    verificationId: String @required
    patient: PatientReference @required
    verificationMethod: Enum { 
      document_scan, biometric, otp, security_question,
      video_verification, in_person 
    } @required
    verificationStatus: Enum { pending, in_progress, verified, failed } @required
    verifiedAt: DateTime
    verifiedBy: Practitioner
    verificationData: VerificationData {
      documentImages: List<Attachment>
      biometricData: BiometricData
      otpCode: String
      livenessScore: Decimal
      confidenceScore: Decimal
    }
    expiryDate: Date
  }
}
```

### 2.3 患者档案管理Schema

```dsl
schema PatientRecordManagement {
  resourceType: String @value("PatientRecordManagement") @required
  
  // 档案信息
  record: PatientRecord {
    recordId: String @required
    patient: PatientReference @required
    mrn: String @required
    
    // 档案状态
    status: RecordStatus {
      currentStatus: Enum { active, inactive, merged, deceased, deleted } @required
      statusHistory: List<StatusChange> {
        fromStatus: String @required
        toStatus: String @required
        changedAt: DateTime @required
        changedBy: Practitioner @required
        reason: String
      }
    }
    
    // 档案分类
    classification: RecordClassification {
      recordType: Enum { outpatient, inpatient, emergency, dental, mental_health }
      specialties: List<String>
      riskLevel: Enum { low, medium, high, critical }
      confidentiality: Enum { normal, sensitive, restricted } @default(normal)
      accessRestrictions: List<AccessRestriction> {
        restrictionType: Enum { legal_hold, research_exclusion, sensitive_condition }
        startDate: Date
        endDate: Date
        authorizedViewers: List<Practitioner>
      }
    }
    
    // 就诊历史
    encounterHistory: List<EncounterSummary> {
      encounterId: String @required
      encounterType: Enum { outpatient, inpatient, emergency, virtual }
      encounterDate: Date @required
      department: String @required
      chiefComplaint: String
      diagnosisCodes: List<String>
      procedures: List<String>
      dischargeDisposition: String
    }
    
    // 文档索引
    documentIndex: List<DocumentReference> {
      documentId: String @required
      documentType: String @required
      documentDate: DateTime @required
      author: Practitioner
      description: String
      confidentiality: String
      storageLocation: String
      accessUrl: String
    }
    
    // 档案统计
    statistics: RecordStatistics {
      totalEncounters: Integer @default(0)
      totalDocuments: Integer @default(0)
      lastEncounterDate: Date
      lastUpdated: DateTime
      storageSize: Integer  // bytes
    }
  }
  
  // 档案生命周期
  lifecycle: RecordLifecycle {
    createdAt: DateTime @required
    createdBy: Practitioner @required
    retentionPeriod: Integer  // 年
    retentionStartDate: Date
    scheduledArchiveDate: Date
    actualArchiveDate: Date
    archiveLocation: String
    destructionDate: Date
    destructionMethod: String
  }
}
```

---

## 3. 预约挂号Schema

**定义3（预约挂号Schema）**：

```text
Appointment_System = (Appointment_Request, Schedule_Management,
                      Slot_Allocation, Confirmation_Management)
```

### 3.1 预约请求Schema

```dsl
schema AppointmentRequest {
  resourceType: String @value("AppointmentRequest") @required
  
  requestId: String @required
  
  // 患者信息
  patient: AppointmentPatient {
    patientId: String
    isNewPatient: Boolean @default(false)
    name: HumanName @required
    gender: Enum { male, female, other, unknown }
    birthDate: Date
    idCard: String
    phoneNumber: String @required
    email: String
    address: Address
    
    // 如果是新患者
    registrationInfo: PatientRegistration
    
    // 既往病史
    medicalHistory: MedicalHistory {
      chronicDiseases: List<String>
      allergies: List<String>
      currentMedications: List<String>
      previousSurgeries: List<String>
    }
  }
  
  // 预约需求
  requirements: AppointmentRequirements {
    desiredDate: DateRange @required
    preferredTimes: List<TimeRange>
    specialty: String @required
    preferredDoctor: PractitionerReference
    appointmentType: Enum { 
      first_visit, follow_up, consultation, 
      procedure, pre_op, post_op, annual_checkup 
    } @required
    urgency: Enum { routine, urgent, emergent } @default(routine)
    reasonForVisit: String @required @maxLength(500)
    symptoms: List<String>
    durationOfSymptoms: String
    referralSource: String
    referralDoctor: PractitionerReference
    languagePreference: String
    accessibilityNeeds: List<String>
  }
  
  // 保险信息
  insurance: AppointmentInsurance {
    insuranceType: Enum { medical, commercial, self_pay }
    insuranceOrg: String
    insuranceId: String
    authorizationRequired: Boolean @default(false)
    authorizationNumber: String
  }
  
  // 预约来源
  source: AppointmentSource {
    channel: Enum { 
      phone, website, mobile_app, wechat, alipay,
      front_desk, referral, emergency_followup 
    } @required
    referralCode: String
    campaignCode: String
    ipAddress: String
    deviceType: String
    browserInfo: String
  }
  
  // 请求处理
  processing: RequestProcessing {
    requestedAt: DateTime @required
    status: Enum { pending, processing, scheduled, rejected, cancelled } @required
    processedAt: DateTime
    processedBy: Practitioner
    rejectionReason: String
    alternativeOptions: List<ScheduleSlot>
    priorityScore: Integer @min(1) @max(100)
  }
}
```

### 3.2 号源Schema

```dsl
schema ScheduleSlot {
  resourceType: String @value("ScheduleSlot") @required
  
  slotId: String @pattern("^S[0-9]{14}[A-Z0-9]{6}$") @required
  scheduleId: String @required
  
  // 时间信息
  time: SlotTime {
    date: Date @required
    startTime: Time @required
    endTime: Time @required
    duration: Integer @required  // 分钟
    timezone: String @default("Asia/Shanghai")
  }
  
  // 服务信息
  service: SlotService {
    department: String @required
    specialty: String @required
    clinicType: Enum { general, specialist, expert, international }
    serviceType: CodeableConcept
    
    // 医生信息
    practitioner: Practitioner {
      practitionerId: String @required
      name: HumanName @required
      title: String
      specialty: String @required
      subspecialty: String
      languages: List<String>
      gender: Enum { male, female }
      photo: Attachment
      rating: Decimal @min(1) @max(5)
      reviewCount: Integer
    }
    
    // 地点
    location: Location {
      locationId: String @required
      name: String @required
      building: String
      floor: String
      roomNumber: String
      address: Address
    }
  }
  
  // 容量管理
  capacity: SlotCapacity {
    totalCapacity: Integer @default(1) @required
    bookedCapacity: Integer @default(0)
    availableCapacity: Integer
    waitlistCapacity: Integer @default(0)
    maxOverbook: Integer @default(0)
  }
  
  // 号源状态
  status: SlotStatus {
    status: Enum { free, busy, blocked, tentative, entered_in_error } @required
    statusReason: String
    appointmentId: String
    patientId: String
    holdToken: String
    holdExpiry: DateTime
  }
  
  // 预约限制
  restrictions: SlotRestrictions {
    patientTypes: List<Enum { new_patient, existing_patient, referral_only }>
    ageRestrictions: AgeRange
    genderRestrictions: List<Enum { male, female }>
    insuranceRestrictions: List<String>
    requiresReferral: Boolean @default(false)
    requiresAuthorization: Boolean @default(false)
    minNoticeHours: Integer @default(24)
    maxAdvanceBookingDays: Integer @default(30)
  }
  
  // 费用信息
  pricing: SlotPricing {
    basePrice: Money
    insurancePrice: Money
    selfPayPrice: Money
    consultationFee: Money
    procedureFee: Money
    currency: String @default("CNY")
  }
  
  // 扩展属性
  extensions: List<SlotExtension> {
    name: String @required
    value: Any
  }
}
```

### 3.3 预约确认Schema

```dsl
schema AppointmentConfirmation {
  resourceType: String @value("AppointmentConfirmation") @required
  
  appointmentId: String @pattern("^APT[0-9]{14}[A-Z0-9]{6}$") @required
  
  // 关联信息
  references: AppointmentReferences {
    requestId: String
    slotId: String @required
    patientId: String @required
    practitionerId: String @required
    encounterId: String
    orderIds: List<String>
  }
  
  // 预约详情
  details: AppointmentDetails {
    scheduledDate: Date @required
    scheduledStartTime: Time @required
    scheduledEndTime: Time
    actualStartTime: DateTime
    actualEndTime: DateTime
    appointmentType: Enum { 
      first_visit, follow_up, consultation, procedure,
      pre_op, post_op, annual_checkup, emergency 
    } @required
    priority: Enum { routine, urgent, emergent }
    reason: String @required
    description: String
    instructions: String
  }
  
  // 参与者
  participants: List<AppointmentParticipant> {
    type: Enum { patient, practitioner, location, device }
    actor: Reference @required
    status: Enum { accepted, declined, tentative, needs_action, completed }
    required: Enum { required, optional, information_only }
    period: Period
  }
  
  // 状态管理
  status: AppointmentStatus {
    currentStatus: Enum { 
      proposed, pending, booked, arrived, fulfilled,
      cancelled, noshow, entered_in_error, checked_in, 
      in_progress, completed, discharged 
    } @required
    statusHistory: List<StatusHistory> {
      status: String @required
      timestamp: DateTime @required
      actor: Reference
      reason: String
    }
  }
  
  // 确认流程
  confirmation: ConfirmationProcess {
    confirmationSent: Boolean @default(false)
    confirmationSentAt: DateTime
    confirmationChannel: Enum { sms, email, app_push, phone }
    confirmedByPatient: Boolean @default(false)
    patientConfirmedAt: DateTime
    confirmationMethod: Enum { sms_reply, email_link, app, phone }
    confirmationCode: String
    reminderSettings: ReminderSettings {
      reminderEnabled: Boolean @default(true)
      reminderChannels: List<Enum { sms, email, app_push, phone }>
      reminderTimes: List<Integer>  // 提前小时数
      customMessage: String
    }
  }
  
  // 通知记录
  notifications: List<AppointmentNotification> {
    notificationId: String @required
    notificationType: Enum { confirmation, reminder, cancellation, rescheduled }
    channel: Enum { sms, email, app_push, phone, wechat } @required
    sentAt: DateTime @required
    content: String @required
    deliveryStatus: Enum { sent, delivered, read, failed }
    readAt: DateTime
    failureReason: String
  }
  
  // 支付信息
  payment: AppointmentPayment {
    paymentRequired: Boolean @default(true)
    amount: Money
    paymentStatus: Enum { pending, paid, refunded, waived }
    paymentMethod: Enum { cash, card, alipay, wechat, insurance }
    paymentTime: DateTime
    transactionId: String
    receiptNumber: String
  }
  
  // 就诊结果
  outcome: AppointmentOutcome {
    encounterCreated: Boolean @default(false)
    encounterId: String
    ordersCreated: List<String>
    prescriptionsCreated: List<String>
    referralCreated: String
    followUpRequired: Boolean
    followUpAppointmentId: String
    patientSatisfaction: Integer @min(1) @max(5)
    feedback: String
  }
}
```

---

## 4. 排班管理Schema

**定义4（排班管理Schema）**：

```text
Staff_Scheduling = (Doctor_Scheduling, Nurse_Scheduling, 
                    Support_Staff_Scheduling, Swap_Management)
```

### 4.1 医生排班Schema

```dsl
schema DoctorSchedule {
  resourceType: String @value("DoctorSchedule") @required
  
  scheduleId: String @required
  
  // 排班周期
  period: SchedulePeriod {
    startDate: Date @required
    endDate: Date @required
    cycleType: Enum { weekly, biweekly, monthly, custom }
    cycleLength: Integer  // 天数
    effectiveDates: List<DateRange>
    holidayExclusions: List<Date>
  }
  
  // 医生配置
  doctor: DoctorAssignment {
    practitioner: Practitioner @required
    department: String @required
    specialty: String @required
    title: String  // 职称
    employeeType: Enum { full_time, part_time, visiting, resident, intern }
    
    // 执业信息
    practiceInfo: PracticeInfo {
      licenseNumber: String @required
      licenseExpiry: Date @required
      supervisingPhysician: Practitioner  // 主治医师（住院医）
      privileges: List<String>  // 执业权限
      restrictions: List<String>  // 执业限制
    }
    
    // 工作偏好
    preferences: WorkPreferences {
      preferredDays: List<Enum { monday, tuesday, wednesday, thursday, friday, saturday, sunday }>
      preferredShifts: List<ShiftType>
      unavailableDates: List<Date>
      maxWeeklyHours: Integer
      maxConsecutiveDays: Integer
      minRestHours: Integer
    }
  }
  
  // 班次分配
  shifts: List<DoctorShift> {
    shiftId: String @required
    date: Date @required
    shiftType: ShiftType @required
    
    // 门诊班次
    clinicShift: ClinicShift {
      clinicType: Enum { general, specialist, expert }
      location: Location
      maxAppointments: Integer @default(30)
      appointmentDuration: Integer @default(15)
      services: List<String>
      specialProcedures: List<String>
    }
    
    // 病房班次
    wardShift: WardShift {
      ward: String
      bedCount: Integer
      patientLoad: Integer
      isOnCall: Boolean
      isNightFloat: Boolean
    }
    
    // 急诊班次
    emergencyShift: EmergencyShift {
      emergencyArea: Enum { triage, fast_track, main, pediatric, trauma }
      isAttending: Boolean
      isConsultant: Boolean
      backupCoverage: Boolean
    }
    
    // 手术班次
    orShift: ORShift {
      orRooms: List<String>
      isPrimarySurgeon: Boolean
      isAssistant: Boolean
      maxCases: Integer
    }
    
    startTime: Time @required
    endTime: Time @required
    breakTime: TimeRange
    location: Location
    notes: String
  }
  
  // 工时统计
  workHours: WorkHourStatistics {
    scheduledHours: Decimal @required
    actualHours: Decimal
    overtimeHours: Decimal @default(0)
    onCallHours: Decimal @default(0)
    leaveHours: Decimal @default(0)
    trainingHours: Decimal @default(0)
    administrativeHours: Decimal @default(0)
    clinicalHours: Decimal @default(0)
  }
  
  // 排班约束检查
  constraints: ScheduleConstraintCheck {
    violations: List<ConstraintViolation> {
      constraintType: Enum { 
        max_hours_exceeded, insufficient_rest, 
        license_expired, privilege_violation,
        overtime_limit, consecutive_days_limit 
      }
      severity: Enum { warning, error, critical }
      description: String
      suggestedFix: String
    }
    isValid: Boolean
  }
}
```

### 4.2 护士排班Schema

```dsl
schema NurseSchedule {
  resourceType: String @value("NurseSchedule") @required
  
  scheduleId: String @required
  
  // 护士配置
  nurse: NurseAssignment {
    practitioner: Practitioner @required
    department: String @required
    nursingUnit: String @required
    
    // 护士资质
    qualification: NurseQualification {
      licenseNumber: String @required
      licenseLevel: Enum { rn, lpn, apn, cns, np }
      certifications: List<String>
      specialtyCertifications: List<String>
      blsExpiry: Date
      aclsExpiry: Date
      palsExpiry: Date
    }
    
    // 岗位能力
    competency: NurseCompetency {
      skills: List<String>
      competencyLevel: Enum { novice, advanced_beginner, competent, proficient, expert }
      canFloat: Boolean @default(false)
      floatUnits: List<String>
      preceptor: Boolean @default(false)
      chargeNurse: Boolean @default(false)
    }
    
    // 工作偏好
    preferences: NursePreferences {
      preferredShift: Enum { day, evening, night, rotating }
      preferredUnit: String
      floatWilling: Boolean @default(false)
      maxPatients: Integer
      overtimeWilling: Boolean @default(false)
    }
  }
  
  // 班次分配
  assignments: List<NurseAssignmentShift> {
    assignmentId: String @required
    date: Date @required
    shiftType: Enum { day, evening, night, on_call, charge } @required
    
    // 岗位分配
    position: NursePosition {
      assignedUnit: String @required
      assignedArea: String
      role: Enum { staff_nurse, charge_nurse, float_nurse, resource_nurse }
      patientAssignment: List<PatientReference>
      nurseRatio: String  // "1:4", "1:6"等
      isPrecepting: Boolean @default(false)
      preceptee: PractitionerReference
    }
    
    // 班次时间
    time: ShiftTime {
      startTime: Time @required
      endTime: Time @required
      reportTime: Time  // 交班时间
      mealBreak: TimeRange
      restBreaks: List<TimeRange>
    }
    
    // 工作量
    workload: NurseWorkload {
      census: Integer  // 病区人数
      acuity: Decimal  // 病人严重程度
      admissionsExpected: Integer
      dischargesExpected: Integer
      proceduresScheduled: Integer
    }
  }
  
  // 人员配置计算
  staffing: StaffingCalculation {
    requiredNurses: Integer
    assignedNurses: Integer
    variance: Integer
    patientAcuity: Decimal
    requiredHours: Decimal
    budgetHours: Decimal
    varianceHours: Decimal
    
    // 安全人员配置检查
    safetyCheck: SafetyCheck {
      minimumMet: Boolean
      ratioCompliant: Boolean
      skillMixAppropriate: Boolean
      contingencyPlan: String
    }
  }
}
```

### 4.3 调班管理Schema

```dsl
schema ShiftSwap {
  resourceType: String @value("ShiftSwap") @required
  
  swapId: String @required
  
  // 申请信息
  request: SwapRequest {
    requestor: StaffReference {
      staffId: String @required
      name: String @required
      department: String @required
      originalShift: AssignedShift @required
    }
    
    swapType: Enum { 
      peer_swap,          // 与同事换班
      give_away,          // 出让班次
      pick_up,            // 接取班次
      leave_request,      // 请假
      overtime_request    // 加班申请
    } @required
    
    requestDetails: RequestDetails {
      requestedDate: Date @required
      requestedShiftType: ShiftType
      reason: String @required @maxLength(500)
      reasonCategory: Enum { 
        personal, family, health, education, 
        emergency, other 
      }
      urgency: Enum { routine, urgent }
      supportingDocuments: List<Attachment>
    }
    
    requestedAt: DateTime @required
    requestStatus: Enum { pending, approved, rejected, cancelled, expired } @required
  }
  
  // 换班对象（peer_swap时）
  partner: SwapPartner {
    partner: StaffReference {
      staffId: String
      name: String
      partnerShift: AssignedShift
      consentGiven: Boolean @default(false)
      consentTime: DateTime
      consentMethod: Enum { system, email, phone, in_person }
    }
    
    swapValidation: SwapValidation {
      qualificationsMatch: Boolean
      seniorityAppropriate: Boolean
      overtimeImplications: String
      costImpact: Money
      skillCoverageMaintained: Boolean
      validationPassed: Boolean
    }
  }
  
  // 审批流程
  approval: SwapApproval {
    approvalChain: List<ApprovalStep> {
      stepOrder: Integer @required
      approverRole: String @required
      approver: Practitioner
      decision: Enum { pending, approved, rejected, delegated }
      decisionTime: DateTime
      comments: String
      conditions: List<String>
    }
    
    currentStep: Integer @default(1)
    finalDecision: Enum { pending, approved, rejected, withdrawn }
    approvedAt: DateTime
    effectiveDate: Date
  }
  
  // 执行记录
  execution: SwapExecution {
    executedAt: DateTime
    executedBy: Practitioner
    originalScheduleUpdated: Boolean
    partnerNotified: Boolean
    departmentNotified: Boolean
    payrollUpdated: Boolean
    
    // 影响范围
    impact: SwapImpact {
      affectedStaff: List<StaffReference>
      affectedPatients: List<PatientReference>
      coverageChanges: List<String>
      additionalCosts: Money
    }
  }
  
  // 审计跟踪
  audit: SwapAudit {
    createdAt: DateTime @required
    createdBy: String @required
    modifiedAt: DateTime
    modifiedBy: String
    decisionRationale: String
    systemNotes: List<String>
  }
}
```

---

## 5. 资源调度Schema

**定义5（资源调度Schema）**：

```text
Resource_Scheduling = (Bed_Management, OR_Scheduling, 
                       Equipment_Scheduling, Staff_Deployment)
```

### 5.1 床位管理Schema

```dsl
schema BedManagement {
  resourceType: String @value("BedManagement") @required
  
  // 床位信息
  bed: Bed {
    bedId: String @required
    bedNumber: String @required
    bedType: BedType @required
    
    // 位置信息
    location: BedLocation {
      building: String @required
      floor: String @required
      ward: Ward {
        wardId: String @required
        wardName: String @required
        wardType: Enum { general, icu, ccu, nicu, picu, maternity, surgical }
        department: String @required
        unit: String
      }
      room: Room {
        roomId: String @required
        roomNumber: String @required
        roomType: Enum { single, double, triple, quad, ward, isolation, deluxe }
        gender: Enum { male, female, mixed, unrestricted }
      }
    }
    
    // 设备配置
    equipment: BedEquipment {
      hasOxygen: Boolean @default(false)
      hasSuction: Boolean @default(false)
      hasIVPole: Boolean @default(true)
      hasBedsideMonitor: Boolean @default(false)
      hasVentilator: Boolean @default(false)
      hasIsolation: Boolean @default(false)
      isBariatric: Boolean @default(false)
      isPressureRelief: Boolean @default(false)
      specialFeatures: List<String>
    }
    
    // 服务能力
    capabilities: BedCapabilities {
      careLevel: Enum { level_1, level_2, level_3, level_4 }  // 护理级别
      isolationCapabilities: List<Enum { contact, droplet, airborne, protective_environment }>
      maxPatientWeight: Quantity
      telemetryCapable: Boolean @default(false)
      dialysisCapable: Boolean @default(false)
    }
    
    status: Enum { active, inactive, maintenance, out_of_service }
    operationalStatus: Enum { available, occupied, reserved, blocked, cleaning }
  }
  
  // 床位占用
  occupancy: BedOccupancy {
    currentOccupancy: OccupancyRecord {
      occupancyId: String
      patient: PatientReference
      admission: AdmissionReference
      checkInTime: DateTime
      expectedDischarge: DateTime
      isolationRequired: Boolean
      specialNeeds: List<String>
    }
    
    occupancyHistory: List<HistoricalOccupancy> {
      occupancyId: String
      patient: PatientReference
      checkInTime: DateTime
      checkOutTime: DateTime
      lengthOfStay: Duration
      dischargeDisposition: String
    }
    
    upcomingReservations: List<BedReservation> {
      reservationId: String
      patient: PatientReference
      expectedAdmission: DateTime
      surgery: SurgeryReference
      estimatedStay: Duration
      priority: Enum { elective, urgent, emergent }
    }
  }
  
  // 床位分配算法
  assignment: BedAssignmentLogic {
    assignmentRules: List<AssignmentRule> {
      rulePriority: Integer @required
      ruleType: Enum { 
        gender_match, age_appropriate, isolation_needed,
        care_level_match, proximity_preference, 
        specialty_match, equipment_needed 
      }
      condition: Expression
      weight: Decimal @min(0) @max(1)
    }
    
    optimizationCriteria: OptimizationCriteria {
      primaryGoal: Enum { minimize_wait, maximize_utilization, optimize_flow }
      secondaryGoals: List<Enum { gender_matching, age_grouping, minimize_transfers }>
      constraints: List<Constraint>
    }
    
    currentScore: Decimal
    alternativeBeds: List<BedAlternative> {
      bed: BedReference
      score: Decimal
      matchReasons: List<String>
      mismatchReasons: List<String>
    }
  }
  
  // 周转管理
  turnover: BedTurnover {
    cleaningRequired: Boolean
    cleaningStatus: Enum { not_needed, pending, in_progress, completed, inspected }
    cleaningStarted: DateTime
    cleaningCompleted: DateTime
    inspectionPassed: Boolean
    readyForPatient: Boolean
    estimatedReadyTime: DateTime
    
    maintenance: MaintenanceRecord {
      maintenanceRequired: Boolean
      maintenanceType: Enum { preventive, corrective, emergency }
      maintenanceStatus: Enum { scheduled, in_progress, completed }
      estimatedCompletion: DateTime
    }
  }
  
  // 统计信息
  statistics: BedStatistics {
    utilizationRate: Decimal @min(0) @max(1)
    averageLengthOfStay: Duration
    turnoverTime: Duration
    occupancyRateByHour: List<Decimal>
    occupancyRateByDay: List<Decimal>
    
    // 质量指标
    qualityMetrics: BedQualityMetrics {
      cleaningCompliance: Decimal
      maintenanceCompliance: Decimal
      patientSatisfaction: Decimal
      pressureInjuryRate: Decimal
      fallRate: Decimal
    }
  }
}

enum BedType {
  STANDARD
  ELECTRIC
  ICU
  BARIATRIC
  PEDIATRIC
  MATERNITY
  ORTHOPEDIC
  BURN
  ISOLATION
  OBSERVATION
}
```

### 5.2 手术室调度Schema

```dsl
schema OperatingRoomSchedule {
  resourceType: String @value("OperatingRoomSchedule") @required
  
  scheduleId: String @required
  
  // 手术室信息
  orRoom: OperatingRoom {
    roomId: String @required
    roomNumber: String @required
    roomType: Enum { general, cardiac, neuro, ortho, obgyn, pediatric, hybrid, robotic }
    
    // 设备配置
    equipment: OREquipment {
      anesthesiaMachine: Boolean @default(true)
      surgicalLights: Integer @default(2)
      surgicalTables: Integer @default(1)
      imagingEquipment: List<String>  // C-arm, CT, MRI等
      laparoscopicEquipment: Boolean @default(false)
      roboticSystem: String  // Da Vinci等
      laserEquipment: List<String>
      microscope: Boolean @default(false)
      specialFeatures: List<String>
    }
    
    // 环境要求
    environment: OREnvironment {
      positivePressure: Boolean @default(true)
      laminarFlow: Boolean @default(false)
      hepaFiltration: Boolean @default(true)
      temperatureRange: Range
      humidityRange: Range
    }
    
    status: Enum { available, in_use, cleaning, maintenance, reserved, blocked }
  }
  
  // 手术安排
  cases: List<ScheduledSurgery> {
    caseId: String @required
    caseNumber: String @required
    
    // 手术信息
    surgery: SurgeryInfo {
      surgeryRequestId: String @required
      patient: PatientReference @required
      procedureCodes: List<ProcedureCode> {
        code: String @required
        description: String @required
        cptCode: String
        icd9cmCode: String
        estimatedDuration: Integer
        priority: Enum { elective, urgent, emergent }
      }
      diagnosisCodes: List<String>
      estimatedBloodLoss: Quantity
      specialEquipment: List<String>
      implantRequired: Boolean
      implantTypes: List<String>
    }
    
    // 时间安排
    scheduling: SurgeryTime {
      scheduledDate: Date @required
      scheduledStartTime: Time @required
      scheduledEndTime: Time
      estimatedDuration: Integer @required
      setupTime: Integer @default(30)
      cleanupTime: Integer @default(30)
      turnoverTime: Integer @default(60)
      actualStartTime: DateTime
      actualEndTime: DateTime
    }
    
    // 手术团队
    team: SurgicalTeam {
      primarySurgeon: Practitioner @required
      assistantSurgeons: List<Practitioner>
      anesthesiaProvider: Practitioner @required
      crna: Practitioner
      scrubTech: Practitioner
      circulatingNurse: Practitioner @required
      additionalNurses: List<Practitioner>
      perfusionist: Practitioner
      paOrNp: Practitioner
      medicalStudents: List<Practitioner>
    }
    
    // 术前状态
    preOp: PreOpStatus {
      patientArrived: Boolean @default(false)
      preOpAssessmentDone: Boolean @default(false)
      consentVerified: Boolean @default(false)
      siteMarked: Boolean @default(false)
      timeoutCompleted: Boolean @default(false)
      anesthesiaStarted: Boolean @default(false)
      holdReasons: List<String>
      readyForRoom: Boolean @default(false)
    }
    
    // 手术执行
    execution: SurgeryExecution {
      status: Enum { scheduled, confirmed, in_room, prepping, 
                    incision, closing, recovery, completed, cancelled }
      incisionTime: DateTime
      closureTime: DateTime
      specimenSent: Boolean
      implantsUsed: List<String>
      complications: List<String>
      estimatedBloodLoss: Quantity
      actualDuration: Integer
    }
    
    // 术后
    postOp: PostOpPlan {
      recoveryLocation: Enum { pacu, icu, ward, other }
      dischargeDisposition: String
      followUpRequired: Boolean
      physicalTherapy: Boolean
      caseCartCompleted: Boolean
    }
    
    priority: Integer @min(1) @max(10)
    notes: String
  }
  
  // 调度优化
  optimization: SchedulingOptimization {
    objective: Enum { minimize_makespan, maximize_throughput, minimize_overtime }
    constraints: List<SchedulingConstraint> {
      type: Enum { 
        surgeon_availability, equipment_availability, 
        staff_availability, room_compatibility, 
        patient_preference, sterilization_time 
      }
      hardConstraint: Boolean
      penalty: Decimal
    }
    
    metrics: ScheduleMetrics {
      roomUtilization: Decimal
      onTimeStarts: Decimal
      averageTurnover: Duration
      overtimeMinutes: Integer
      cancelledCases: Integer
      addOnCases: Integer
    }
    
    suggestions: List<OptimizationSuggestion> {
      type: Enum { reschedule, swap_rooms, add_staff, extend_hours }
      description: String
      expectedImprovement: Decimal
      implementationEffort: Enum { low, medium, high }
    }
  }
}
```

### 5.3 检查设备调度Schema

```dsl
schema ImagingSchedule {
  resourceType: String @value("ImagingSchedule") @required
  
  scheduleId: String @required
  
  // 设备信息
  modality: ImagingModality {
    modalityId: String @required
    modalityType: Enum { CT, MRI, XR, US, NM, PET, MG, DX, RF, XCT } @required
    manufacturer: String
    model: String
    serialNumber: String
    installationDate: Date
    
    // 设备能力
    capabilities: ModalityCapabilities {
      bodyParts: List<String>
      procedures: List<String>
      contrastCapability: Boolean
      sedationCapability: Boolean
      biopsyCapability: Boolean
      specialFeatures: List<String>
    }
    
    // 运营时间
    operatingHours: OperatingHours {
      regularHours: List<DailySchedule>
      extendedHours: List<DailySchedule>
      maintenanceWindows: List<TimeRange>
    }
    
    location: Location @required
    status: Enum { available, in_use, maintenance, calibration, out_of_service }
  }
  
  // 检查预约
  appointments: List<ImagingAppointment> {
    appointmentId: String @required
    orderId: String @required
    
    // 患者信息
    patient: ImagingPatient {
      patientReference: PatientReference @required
      patientWeight: Quantity
      patientHeight: Quantity
      bmi: Decimal
      mobilityStatus: Enum { ambulatory, wheelchair, stretcher, bed }
      contrastAllergy: Boolean
      renalFunction: String
      pregnancyStatus: Enum { not_pregnant, pregnant, possibly_pregnant, n_a }
      claustrophobia: Boolean
      sedationRequired: Boolean
      interpreterRequired: Boolean
      language: String
    }
    
    // 检查项目
    exam: ImagingExam {
      examType: Enum { 
        ct_head, ct_chest, ct_abdomen, ct_pelvis, ct_extremity,
        mri_brain, mri_spine, mri_joint, mri_abdomen,
        xray_chest, xray_extremity, xray_spine,
        us_abdomen, us_pelvic, us_cardiac, us_vascular,
        mammography_screening, mammography_diagnostic,
        nuclear_stress, nuclear_bone, pet_ct
      } @required
      examCode: String @required
      examDescription: String @required
      cptCode: String
      icd10Code: String
      bodyPart: String @required
      laterality: Enum { left, right, bilateral, not_applicable }
      
      // 检查细节
      protocol: String
      contrast: ContrastInfo {
        contrastRequired: Boolean @default(false)
        contrastType: Enum { iv, oral, rectal, intra_articular }
        contrastAgent: String
        contrastVolume: Quantity
        route: String
      }
      sedation: SedationInfo {
        sedationRequired: Boolean @default(false)
        sedationType: Enum { oral, iv, general }
        npoRequired: Boolean
        npoHours: Integer
      }
      
      priority: Enum { routine, urgent, stat } @default(routine)
      clinicalIndication: String @required
      clinicalHistory: String
    }
    
    // 预约安排
    scheduling: ImagingScheduling {
      scheduledDate: Date @required
      scheduledTime: Time @required
      estimatedDuration: Integer @default(30)
      bufferTime: Integer @default(15)
      actualStartTime: DateTime
      actualEndTime: DateTime
      
      // 时间槽
      timeSlot: TimeSlot {
        slotId: String
        startTime: DateTime
        endTime: DateTime
        slotType: Enum { routine, urgent, add_on, overflow }
      }
    }
    
    // 患者准备
    preparation: PatientPreparation {
      prepInstructionsSent: Boolean @default(false)
      prepInstructions: String
      prepCompleted: Boolean @default(false)
      prepVerifiedBy: Practitioner
      prepVerifiedAt: DateTime
      
      // 特殊准备
      labResultsRequired: List<String>
      labResultsCompleted: Boolean
      priorImagesRequired: Boolean
      priorImagesAvailable: Boolean
      
      patientArrived: Boolean @default(false)
      arrivalTime: DateTime
      checkedIn: Boolean @default(false)
    }
    
    // 检查执行
    execution: ImagingExecution {
      status: Enum { 
        scheduled, confirmed, checked_in, prepped, 
        in_progress, completed, cancelled, no_show, rescheduled 
      }
      
      technician: Practitioner
      radiologist: Practitioner
      
      imagesAcquired: Integer
      seriesCount: Integer
      contrastAdministered: Boolean
      complications: List<String>
      
      technicalQuality: Enum { excellent, good, fair, poor }
      repeatRequired: Boolean
      additionalViews: Boolean
      
      imagesSentToPACS: Boolean @default(false)
      imagesSentAt: DateTime
    }
    
    // 报告
    reporting: ImagingReporting {
      reportStatus: Enum { pending, dictated, transcribed, preliminary, final, amended }
      dictatingRadiologist: Practitioner
      transcriptionist: String
      reportText: String
      impression: String
      findings: String
      recommendations: String
      
      criticalFindings: Boolean @default(false)
      criticalFindingNotification: CriticalNotification {
        notified: Boolean @default(false)
        notifiedAt: DateTime
        notifiedTo: Practitioner
        notificationMethod: Enum { phone, pager, in_person }
        readBackConfirmed: Boolean
      }
      
      reportTime: DateTime
      verifiedBy: Practitioner
      verificationTime: DateTime
    }
  }
  
  // 调度优化
  optimization: ImagingOptimization {
    dailyCapacity: Integer
    bookedSlots: Integer
    availableSlots: Integer
    urgentSlotsReserved: Integer
    urgentSlotsUsed: Integer
    
    waitTimeStatistics: WaitTimeStats {
      averageWaitDays: Decimal
      maxWaitDays: Integer
      routineWaitDays: Decimal
      urgentWaitDays: Decimal
      statWaitMinutes: Integer
    }
    
    utilization: UtilizationMetrics {
      dailyUtilization: Decimal
      weeklyUtilization: Decimal
      monthlyUtilization: Decimal
      primeTimeUtilization: Decimal
      offHoursUtilization: Decimal
    }
  }
}
```

---

## 6. 收费管理Schema

**定义6（收费管理Schema）**：

```dsl
schema ChargeManagement {
  resourceType: String @value("ChargeManagement") @required
  
  chargeId: String @required
  
  // 费用项目
  chargeItem: ChargeItem {
    itemCode: String @required  // 收费项目编码
    itemName: String @required
    itemCategory: Enum { 
      medical_service, drug, material, exam, 
      lab_test, surgery, anesthesia, room, 
      nursing, consultation, other 
    } @required
    
    // 价格信息
    pricing: ChargePricing {
      unitPrice: Money @required
      quantity: Decimal @default(1)
      totalPrice: Money @required
      
      priceType: Enum { standard, negotiated, contractual, promotional }
      priceTier: Enum { level_1, level_2, level_3 }  // 医院等级
      
      // 折扣
      discount: DiscountInfo {
        discountType: Enum { percentage, amount, special_program }
        discountValue: Money
        discountReason: String
        authorizedBy: Practitioner
      }
      
      finalPrice: Money @required
    }
    
    // 计费来源
    source: ChargeSource {
      encounterId: String @required
      orderId: String
      procedureId: String
      medicationId: String
      serviceDate: DateTime @required
      performingProvider: Practitioner
      orderingProvider: Practitioner
      location: Location
      department: String
    }
    
    // 计费状态
    status: ChargeStatus {
      chargeStatus: Enum { 
        planned, billable, not_billable, aborted, 
        billed, entered_in_error 
      } @required
      billingDate: Date
      billId: String
    }
  }
  
  // 保险信息
  insurance: InsuranceBilling {
    primaryInsurance: InsuranceClaim {
      insuranceId: String
      claimNumber: String
      preAuthNumber: String
      eligibilityVerified: Boolean
      coveragePercentage: Decimal
      deductible: Money
      copay: Money
      coveredAmount: Money
      deniedAmount: Money
      denialReason: String
      claimStatus: Enum { pending, submitted, acknowledged, 
                         pending_additional_info, adjudicated, paid, denied }
    }
    
    secondaryInsurance: InsuranceClaim
    tertiaryInsurance: InsuranceClaim
  }
  
  // 患者责任
  patientResponsibility: PatientResponsibility {
    selfPayAmount: Money
    deductibleAmount: Money
    copayAmount: Money
    coinsuranceAmount: Money
    nonCoveredAmount: Money
    priorPayments: Money
    outstandingBalance: Money
    
    paymentPlan: PaymentPlan {
      planActive: Boolean
      monthlyPayment: Money
      remainingMonths: Integer
      totalPlanAmount: Money
    }
  }
  
  // 支付记录
  payments: List<PaymentRecord> {
    paymentId: String @required
    paymentDate: DateTime @required
    paymentAmount: Money @required
    paymentMethod: Enum { 
      cash, check, credit_card, debit_card, 
      insurance, bank_transfer, alipay, wechat, other 
    } @required
    paymentReference: String
    processedBy: Practitioner
    
    allocation: List<PaymentAllocation> {
      chargeId: String @required
      allocatedAmount: Money @required
    }
  }
  
  // 发票信息
  invoice: InvoiceInfo {
    invoiceNumber: String
    invoiceDate: Date
    invoiceType: Enum { outpatient, inpatient, pharmacy, comprehensive }
    invoiceStatus: Enum { draft, issued, printed, cancelled, reissued }
    invoiceItems: List<InvoiceItem>
    totalAmount: Money
    taxAmount: Money
    qrCode: String
    electronicInvoice: Boolean
  }
}
```

---

## 7. 类型系统

**定义7（医院管理数据类型）**：

```text
HM_Data_Type = Primitive | Complex | Reference | Temporal | Financial

Primitive = String | Integer | Decimal | Boolean
Complex = HumanName | Address | ContactPoint | CodeableConcept | Quantity | Range | Period
Reference = PatientRef | PractitionerRef | LocationRef | OrganizationRef
Temporal = Date | DateTime | Time | Duration
Financial = Money | Currency
```

**基本类型定义**：

```dsl
// 货币
type Money {
  value: Decimal @required
  currency: String @default("CNY")
}

// 时间段
type Duration {
  value: Decimal @required
  unit: Enum { ms, s, min, h, d, wk, mo, a } @required
}

// 年龄范围
type AgeRange {
  min: Integer
  max: Integer
}

// 时间范围
type TimeRange {
  start: Time @required
  end: Time @required
}

// 日期范围
type DateRange {
  start: Date @required
  end: Date @required
} @constraint("start <= end")

// 附件
type Attachment {
  contentType: String
  language: String
  data: Base64Binary
  url: String @pattern("^http://.*$")
  size: Integer
  hash: Base64Binary
  title: String
  creation: DateTime
}
```

---

## 8. 约束规则

**约束1（患者注册完整性）**：

```text
∀ reg ∈ PatientRegistration:
  reg.registrationId ≠ ∅
  ∧ reg.patient.name.family ≠ ∅
  ∧ reg.patient.gender ∈ {male, female, other, unknown}
  ∧ reg.patient.birthDate ≠ ∅
  ∧ reg.patient.telecom ≠ ∅
  ∧ (reg.patient.identifiers = ∅ → reg.registrationType = new_patient)
  ∧ (reg.registrationType = new_patient → reg.patient.identifiers ≠ ∅)
```

**约束2（预约有效性）**：

```text
∀ apt ∈ AppointmentConfirmation:
  apt.appointmentId ≠ ∅
  ∧ apt.details.scheduledDate ≥ today()
  ∧ apt.details.scheduledStartTime < apt.details.scheduledEndTime
  ∧ apt.participants.patient ≠ ∅
  ∧ apt.participants.practitioner ≠ ∅
  ∧ (apt.status.currentStatus = 'booked' → apt.confirmation.patientConfirmed = true)
```

**约束3（排班可行性）**：

```text
∀ sched ∈ DoctorSchedule:
  ∀ shift ∈ sched.shifts:
    shift.startTime < shift.endTime
    ∧ shift.date ≥ sched.period.startDate
    ∧ shift.date ≤ sched.period.endDate
    ∧ count(shifts on same date) ≤ sched.doctor.preferences.maxConsecutiveDays
    ∧ consecutive_hours(sched.doctor) ≤ 80  // 每周最大工时
```

**约束4（床位分配规则）**：

```text
∀ bed ∈ BedManagement:
  bed.status.operationalStatus = occupied → bed.occupancy.currentOccupancy ≠ ∅
  ∧ bed.occupancy.currentOccupancy.patient ≠ ∅
  ∧ bed.occupancy.currentOccupancy.checkInTime ≠ ∅
  ∧ bed.location.ward.wardType ∈ bed.capabilities.supportedWardTypes
```

**约束5（手术室调度）**：

```text
∀ or ∈ OperatingRoomSchedule:
  ∀ case1, case2 ∈ or.cases:
    case1 ≠ case2 → 
      (case1.scheduling.scheduledEndTime ≤ case2.scheduling.scheduledStartTime)
      ∨ (case2.scheduling.scheduledEndTime ≤ case1.scheduling.scheduledStartTime)
  ∧ case.scheduling.scheduledStartTime ≥ or.operatingHours.startTime
  ∧ case.scheduling.scheduledEndTime ≤ or.operatingHours.endTime
```

---

## 9. 转换函数

**函数1（患者数据标准化）**：

```text
standardize_patient: Raw_Patient_Data → Standard_Patient
```

**函数2（排班优化）**：

```text
optimize_schedule: Schedule_Request → Optimized_Schedule
```

**Python实现**：

```python
from datetime import datetime, timedelta
from typing import List, Dict, Any
import itertools

class ScheduleOptimizer:
    """排班优化器"""
    
    def optimize(self, staff: List[Dict], shifts: List[Dict], 
                 constraints: Dict[str, Any]) -> List[Dict]:
        """
        优化排班
        
        Args:
            staff: 员工列表
            shifts: 需要分配的班次
            constraints: 约束条件
            
        Returns:
            优化后的排班表
        """
        # 生成所有可能的分配方案
        assignments = self._generate_assignments(staff, shifts)
        
        # 过滤不可行方案
        feasible = [a for a in assignments if self._check_constraints(a, constraints)]
        
        # 评分并排序
        scored = [(a, self._score_assignment(a)) for a in feasible]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[0][0] if scored else []
    
    def _check_constraints(self, assignment: List[Dict], constraints: Dict) -> bool:
        """检查约束"""
        # 检查最大工时
        # 检查休息时间
        # 检查资质匹配
        return True
    
    def _score_assignment(self, assignment: List[Dict]) -> float:
        """评分"""
        # 偏好满足度
        # 均衡性
        # 成本
        return 0.0
```

**函数3（床位分配）**：

```text
assign_bed: Patient_Requirements, Available_Beds → Optimal_Bed_Assignment
```

---

## 10. 形式化定理

### 10.1 排班可行性定理

**定理1（排班可行性）**：

```text
∀ S ⊆ Staff, ∀ R ⊆ Requirements:
  |S| ≥ minimum_staff_required(R)
  ∧ ∀ s ∈ S: qualified(s, R)
  ∧ ∀ r ∈ R: ∃ s ∈ S: available(s, r.time)
  → ∃ schedule: valid_schedule(schedule, S, R)
```

### 10.2 资源分配最优性定理

**定理2（资源分配最优性）**：

```text
∀ resources ∈ Resources, ∀ demands ∈ Demands:
  optimize(resources, demands) = argmax_{allocation} 
    (utilization(allocation) - cost(allocation) - penalties(allocation))
```

### 10.3 患者流转完整性定理

**定理3（患者流转完整性）**：

```text
∀ patient ∈ Patients:
  complete_patient_journey(patient)
  → ∀ stage ∈ Journey_Stages:
      documented(patient, stage)
      ∧ timestamped(patient, stage)
      ∧ responsible_party_identified(patient, stage)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
