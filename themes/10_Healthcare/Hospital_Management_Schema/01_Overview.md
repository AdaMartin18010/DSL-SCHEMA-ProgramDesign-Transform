# 医院管理Schema概述

## 📑 目录

- [医院管理Schema概述](#医院管理schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 医院管理Schema定义](#11-医院管理schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 医院管理Schema定义](#21-医院管理schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. HIS系统架构](#3-his系统架构)
    - [3.1 架构概述](#31-架构概述)
    - [3.2 核心模块](#32-核心模块)
    - [3.3 数据流](#33-数据流)
  - [4. 预约挂号系统](#4-预约挂号系统)
    - [4.1 预约流程](#41-预约流程)
    - [4.2 号源管理](#42-号源管理)
    - [4.3 取消与改约](#43-取消与改约)
  - [5. 排班管理系统](#5-排班管理系统)
    - [5.1 排班模式](#51-排班模式)
    - [5.2 班次类型](#52-班次类型)
    - [5.3 调班管理](#53-调班管理)
  - [6. 资源调度系统](#6-资源调度系统)
    - [6.1 床位管理](#61-床位管理)
    - [6.2 手术室调度](#62-手术室调度)
    - [6.3 检查设备调度](#63-检查设备调度)
  - [7. 应用场景](#7-应用场景)
    - [7.1 门诊管理](#71-门诊管理)
    - [7.2 住院管理](#72-住院管理)
    - [7.3 急诊管理](#73-急诊管理)
    - [7.4 医疗资源优化](#74-医疗资源优化)
  - [8. 思维导图](#8-思维导图)

---

## 1. 核心结论

**医院管理存在标准化的Schema体系**，为医疗机构提供完整的管理能力，支持患者流转、资源调度和运营优化。

### 1.1 医院管理Schema定义

```text
Hospital_Management_Schema = (Patient_Flow ⊕ Resource_Scheduling
                              ⊕ Staff_Management ⊕ Appointment_System
                              ⊕ Bed_Management ⊕ Equipment_Scheduling)
                              × Quality_Standards × Security_Framework
```

### 1.2 标准依据

- **HIMSS**：医疗信息与管理系统学会标准
- **JCI标准**：国际联合委员会医院评审标准
- **国内医院信息化标准**：卫健委发布的医院信息化建设标准
- **互联互通标准化成熟度**：国家医疗健康信息互联互通标准化成熟度测评
- **电子病历分级评价**：电子病历系统应用水平分级评价标准

---

## 2. 概念定义

### 2.1 医院管理Schema定义

**医院管理Schema**是描述医院运营管理数据结构和业务流程的形式化规范，包括患者管理、资源调度、人员排班等管理元素。

### 2.2 核心特征

1. **流程标准化**：基于JCI和HIMSS标准
2. **资源优化**：智能调度和资源分配
3. **实时监控**：实时数据监控和预警
4. **互联互通**：支持跨系统数据交换
5. **患者中心**：以患者为中心的流程设计
6. **数据驱动**：基于数据的决策支持

### 2.3 Schema分类

- **患者管理Schema**：患者注册、身份识别、就诊跟踪
- **预约管理Schema**：预约挂号、预约检查、预约手术
- **排班管理Schema**：医生排班、护士排班、医技排班
- **资源调度Schema**：床位、手术室、检查设备
- **收费管理Schema**：费用计算、医保结算、支付方式
- **物资管理Schema**：药品、耗材、设备管理

---

## 3. HIS系统架构

### 3.1 架构概述

**HIS系统采用微服务架构设计**：

```text
HIS_Architecture = (API_Gateway, Microservices, Data_Layer, Integration_Layer)
```

**系统架构图**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户接入层                                       │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│    │ 医生工作站    │ │ 护士工作站    │ │ 管理控制台    │ │ 患者移动端    │     │
│    └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │
├─────────────────────────────────────────────────────────────────────────────┤
│                              API网关层                                       │
│                    ┌──────────────────────────────────┐                     │
│                    │        API Gateway               │                     │
│                    │  (认证/限流/路由/负载均衡)          │                     │
│                    └──────────────────────────────────┘                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                              微服务层                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 患者服务      │ │ 预约服务      │ │ 排班服务      │ │ 收费服务      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 床位服务      │ │ 手术调度      │ │ 检查调度      │ │ 物资服务      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 报表服务      │ │ 消息服务      │ │ 工作流服务    │ │ 缓存服务      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                              数据层                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 主数据库      │ │ 读写分离      │ │ 缓存层       │ │ 数据仓库      │       │
│  │  (Oracle)   │ │  (MySQL)     │ │  (Redis)    │ │  (ClickHouse)│       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                              集成层                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ HL7接口      │ │ FHIR接口      │ │ 医保接口      │ │ 区域平台      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 核心模块

**HIS核心功能模块**：

| 模块名称 | 功能描述 | 主要实体 |
|---------|---------|---------|
| 患者管理 | 患者注册、身份识别、档案管理 | Patient, PatientIdentifier |
| 预约挂号 | 号源管理、预约处理、排队叫号 | Appointment, ScheduleSlot |
| 门诊管理 | 分诊、就诊、处方、收费 | OutpatientVisit, Prescription |
| 住院管理 | 入院、病房、医嘱、出院 | Admission, Ward, Bed |
| 收费管理 | 费用计算、医保结算、发票 | Charge, InsuranceClaim |
| 药房管理 | 药品库存、发药、退药 | Pharmacy, Medication |
| 检验检查 | 申请、执行、报告、图像 | LabOrder, ImagingOrder |
| 手术管理 | 手术申请、安排、执行、记录 | SurgeryRequest, ORSchedule |
| 物资管理 | 采购、库存、领用、盘点 | Inventory, Supply |
| 人事管理 | 员工、排班、考勤、绩效 | Staff, Schedule, Attendance |
| 财务管理 | 收入、支出、成本、报表 | Finance, Budget |
| 统计分析 | 运营指标、质量指标、报表 | KPI, Report |

### 3.3 数据流

**主要业务流程数据流**：

```
患者就诊流程：
Patient Registration → Appointment → Triage → Consultation 
→ Order → Execution → Billing → Discharge

住院流程：
Admission → Bed Assignment → Order Management 
→ Clinical Care → Discharge Planning → Discharge

手术流程：
Surgery Request → Pre-op Assessment → OR Scheduling 
→ Surgery Execution → Recovery → Post-op Care
```

---

## 4. 预约挂号系统

### 4.1 预约流程

**预约挂号流程**：

```dsl
workflow AppointmentWorkflow {
  // 预约请求
  request: AppointmentRequest {
    patient: PatientReference @required
    desiredDate: Date @required
    specialty: String @required
    doctor: PractitionerReference
    appointmentType: Enum { first_visit, follow_up, consultation }
    priority: Enum { routine, urgent }
    reason: String
    contactInfo: ContactPoint @required
  }
  
  // 号源查询
  query: SlotQuery {
    specialty: String @required
    dateRange: DateRange @required
    doctor: PractitionerReference
    appointmentType: Enum { first_visit, follow_up }
  }
  
  // 可用号源
  availableSlots: List<ScheduleSlot> {
    slotId: String @required
    scheduleId: String @required
    startTime: DateTime @required
    endTime: DateTime @required
    status: Enum { free, busy, blocked } @required
    doctor: Practitioner @required
    specialty: String @required
    location: Location
    serviceType: String
  }
  
  // 预约确认
  confirm: AppointmentConfirmation {
    appointmentId: String @required
    slot: ScheduleSlot @required
    patient: PatientReference @required
    status: Enum { pending, confirmed, arrived, completed, cancelled, no_show }
    confirmationTime: DateTime @required
    reminderSetting: ReminderSetting {
      smsReminder: Boolean @default(true)
      emailReminder: Boolean @default(false)
      reminderTime: Integer @default(24)  // 提前小时数
    }
  }
}
```

**预约状态机**：

```
┌─────────┐    预约      ┌─────────┐    确认      ┌─────────┐
│  初始   │ ───────────→ │  待确认  │ ───────────→ │  已确认  │
└─────────┘              └─────────┘              └─────────┘
                                                         │
                           ┌─────────────────────────────┼─────────────┐
                           │                             │             │
                           ↓                             ↓             ↓
                      ┌─────────┐                  ┌─────────┐   ┌─────────┐
                      │  已取消  │                  │  已签到  │   │ 未就诊  │
                      └─────────┘                  └─────────┘   └─────────┘
                                                          │
                                                          ↓
                                                    ┌─────────┐
                                                    │  已完成  │
                                                    └─────────┘
```

### 4.2 号源管理

**号源管理Schema**：

```dsl
schema ScheduleSlot {
  resourceType: String @value("ScheduleSlot") @required
  
  slotId: String @pattern("^S[0-9]{14}[A-Z0-9]{6}$") @required
  scheduleId: String @required
  
  // 时间信息
  timeInfo: SlotTimeInfo {
    date: Date @required
    startTime: Time @required
    endTime: Time @required
    duration: Integer @required  // 分钟
  }
  
  // 服务信息
  service: SlotService {
    specialty: String @required
    serviceType: Enum { outpatient, expert, special, emergency }
    doctor: Practitioner @required
    location: Location @required
    consultationType: Enum { video, phone, in_person }
  }
  
  // 号源状态
  status: SlotStatus {
    currentStatus: Enum { free, busy, blocked, tentative } @required
    appointmentId: String  // 关联的预约ID
    patientId: String     // 预约患者ID
    lockedUntil: DateTime // 锁定截止时间
    lockSessionId: String // 锁定会话ID
  }
  
  // 号源属性
  properties: SlotProperties {
    isWalkin: Boolean @default(false)  // 是否可现场挂号
    isReferralOnly: Boolean @default(false)  // 是否仅转诊
    isNewPatientOnly: Boolean @default(false)  // 是否仅初诊
    maxAppointments: Integer @default(1)  // 最大预约数
    price: Decimal
    insuranceCoverage: Boolean @default(true)
  }
  
  // 统计信息
  statistics: SlotStatistics {
    totalAppointments: Integer @default(0)
    completedAppointments: Integer @default(0)
    cancelledAppointments: Integer @default(0)
    noShowAppointments: Integer @default(0)
  }
}
```

**号源生成算法**：

```python
class SlotGenerator:
    """号源生成器"""
    
    def generate_slots(self, schedule_config: Dict[str, Any], 
                      start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        根据排班配置生成号源
        
        Args:
            schedule_config: 排班配置
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            生成的号源列表
        """
        slots = []
        
        current_date = start_date
        while current_date <= end_date:
            # 获取当天的排班规则
            day_schedule = self._get_day_schedule(schedule_config, current_date)
            
            if day_schedule:
                # 生成该天的号源
                day_slots = self._generate_day_slots(
                    current_date, 
                    day_schedule,
                    schedule_config.get('doctor'),
                    schedule_config.get('location')
                )
                slots.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _generate_day_slots(self, date: date, schedule: Dict[str, Any],
                           doctor: Dict[str, str], location: Dict[str, str]) -> List[Dict[str, Any]]:
        """生成单日号源"""
        slots = []
        
        start_time = datetime.combine(date, schedule['startTime'])
        end_time = datetime.combine(date, schedule['endTime'])
        duration = timedelta(minutes=schedule['duration'])
        
        current_time = start_time
        while current_time + duration <= end_time:
            slot = {
                'slotId': self._generate_slot_id(),
                'scheduleId': schedule['scheduleId'],
                'date': date.isoformat(),
                'startTime': current_time.time().isoformat(),
                'endTime': (current_time + duration).time().isoformat(),
                'duration': schedule['duration'],
                'doctor': doctor,
                'location': location,
                'specialty': schedule['specialty'],
                'status': 'free'
            }
            slots.append(slot)
            current_time += duration
        
        return slots
```

### 4.3 取消与改约

**取消和改约规则**：

```dsl
schema AppointmentCancellation {
  cancellationId: String @required
  appointmentId: String @required
  
  // 取消信息
  cancellation: CancellationInfo {
    cancelledAt: DateTime @required
    cancelledBy: Reference @required
    reason: Enum { 
      patient_request, doctor_unavailable, emergency, 
      duplicate, system_error, other 
    } @required
    reasonDetail: String
    penaltyApplied: Boolean @default(false)
    penaltyAmount: Decimal
  }
  
  // 号源释放
  slotRelease: SlotRelease {
    slotId: String @required
    releasedAt: DateTime @required
    newStatus: Enum { free, blocked }
  }
  
  // 退款处理
  refund: RefundInfo {
    refundRequired: Boolean @required
    refundAmount: Decimal
    refundMethod: Enum { original, cash, bank_transfer }
    refundStatus: Enum { pending, processing, completed, failed }
    refundTransactionId: String
  }
  
  // 通知
  notifications: List<Notification> {
    recipient: Reference @required
    channel: Enum { sms, email, app_push, phone }
    sentAt: DateTime
    status: Enum { pending, sent, delivered, failed }
  }
}

schema AppointmentReschedule {
  rescheduleId: String @required
  originalAppointmentId: String @required
  
  // 原预约
  originalAppointment: AppointmentReference {
    appointmentId: String @required
    slot: ScheduleSlot @required
    patient: PatientReference @required
  }
  
  // 新预约
  newAppointment: AppointmentInfo {
    newAppointmentId: String @required
    newSlot: ScheduleSlot @required
    rescheduledAt: DateTime @required
    rescheduledBy: Reference @required
    reason: String
  }
  
  // 费用处理
  priceAdjustment: PriceAdjustment {
    originalPrice: Decimal @required
    newPrice: Decimal @required
    priceDifference: Decimal
    adjustmentType: Enum { refund, additional, no_change }
    adjustmentTransactionId: String
  }
}
```

---

## 5. 排班管理系统

### 5.1 排班模式

**排班模式类型**：

| 排班模式 | 适用场景 | 特点 |
|---------|---------|------|
| 固定排班 | 门诊医生 | 周期性重复，规律性强 |
| 弹性排班 | 急诊、ICU | 根据工作量动态调整 |
| 轮班排班 | 护士、医技 | 三班倒，保证24小时覆盖 |
| 预约排班 | 专家门诊 | 按需安排，患者驱动 |
| 混合排班 | 综合科室 | 多种模式组合 |

**排班周期定义**：

```dsl
schema ShiftSchedule {
  resourceType: String @value("ShiftSchedule") @required
  
  scheduleId: String @required
  scheduleType: Enum { fixed, rotating, flexible, on_call } @required
  
  // 排班周期
  period: SchedulePeriod {
    startDate: Date @required
    endDate: Date @required
    cycleLength: Integer @required  // 周期天数
    effectiveDates: List<DateRange>
  }
  
  // 人员配置
  staffAssignment: List<StaffAssignment> {
    staff: Practitioner @required
    role: Enum { doctor, nurse, technician, resident, intern } @required
    department: String @required
    specialty: String
    
    // 班次分配
    shifts: List<AssignedShift> {
      date: Date @required
      shiftType: ShiftType @required
      location: Location
      responsibilities: List<String>
      notes: String
    }
    
    // 工时统计
    workHours: WorkHours {
      scheduledHours: Decimal @required
      actualHours: Decimal
      overtimeHours: Decimal @default(0)
      leaveHours: Decimal @default(0)
    }
  }
  
  // 排班约束
  constraints: ScheduleConstraints {
    maxConsecutiveDays: Integer @default(6)
    minRestHours: Integer @default(24)
    maxWeeklyHours: Integer @default(40)
    skillRequirements: List<SkillRequirement>
    seniorityRequirements: List<SeniorityRequirement>
  }
  
  // 排班状态
  status: ScheduleStatus {
    currentStatus: Enum { draft, published, active, completed, archived } @required
    publishedAt: DateTime
    publishedBy: Practitioner
    lastModifiedAt: DateTime
    lastModifiedBy: Practitioner
  }
}
```

### 5.2 班次类型

**标准班次定义**：

```dsl
enum ShiftType {
  // 门诊班次
  MORNING_CLINIC {      // 上午门诊
    startTime: "08:00"
    endTime: "12:00"
    breakTime: "10:00-10:15"
  }
  
  AFTERNOON_CLINIC {    // 下午门诊
    startTime: "14:00"
    endTime: "17:30"
    breakTime: "15:30-15:45"
  }
  
  EVENING_CLINIC {      // 晚间门诊
    startTime: "17:30"
    endTime: "21:00"
  }
  
  // 急诊班次
  DAY_EMERGENCY {       // 白班急诊
    startTime: "08:00"
    endTime: "16:00"
  }
  
  EVENING_EMERGENCY {   // 晚班急诊
    startTime: "16:00"
    endTime: "00:00"
  }
  
  NIGHT_EMERGENCY {     // 夜班急诊
    startTime: "00:00"
    endTime: "08:00"
  }
  
  // 病房班次
  DAY_WARD {            // 白班病房
    startTime: "08:00"
    endTime: "16:00"
  }
  
  EVENING_WARD {        // 小夜班
    startTime: "16:00"
    endTime: "00:00"
  }
  
  NIGHT_WARD {          // 大夜班
    startTime: "00:00"
    endTime: "08:00"
  }
  
  // 手术室班次
  OR_DAY {              // 手术室白班
    startTime: "08:00"
    endTime: "17:00"
  }
  
  OR_EXTENDED {         // 手术室延长班
    startTime: "08:00"
    endTime: "22:00"
  }
  
  OR_ON_CALL {          // 手术室备班
    startTime: "17:00"
    endTime: "08:00"
    isOnCall: true
  }
  
  // 行政班次
  ADMINISTRATIVE {      // 行政班
    startTime: "08:00"
    endTime: "17:30"
    lunchBreak: "12:00-13:30"
  }
}
```

### 5.3 调班管理

**调班申请流程**：

```dsl
schema ShiftSwap {
  swapId: String @required
  
  // 申请人信息
  requestor: StaffReference {
    staffId: String @required
    name: String @required
    department: String @required
    originalShift: AssignedShift @required
  }
  
  // 调班类型
  swapType: Enum { 
    swap_with_peer,     // 与同事换班
    request_leave,      // 请假
    request_overtime,   // 申请加班
    duty_exchange       // 调休
  } @required
  
  // 调班详情
  swapDetails: SwapDetails {
    requestedDate: Date @required
    requestedShift: ShiftType
    reason: String @required
    reasonCategory: Enum { personal, family, health, emergency, other }
    supportingDocuments: List<Attachment>
  }
  
  // 换班对象（如适用）
  swapPartner: StaffReference {
    staffId: String
    name: String
    partnerShift: AssignedShift
    partnerConsent: Boolean
    consentTime: DateTime
  }
  
  // 审批流程
  approval: ApprovalWorkflow {
    currentStep: Integer @default(1)
    totalSteps: Integer @required
    approvals: List<ApprovalStep> {
      stepNumber: Integer @required
      approver: Practitioner @required
      approverRole: String @required
      decision: Enum { pending, approved, rejected }
      decisionTime: DateTime
      comments: String
    }
    finalStatus: Enum { pending, approved, rejected, withdrawn }
  }
  
  // 调班执行
  execution: SwapExecution {
    executedAt: DateTime
    executedBy: Practitioner
    originalScheduleUpdated: Boolean
    notificationsSent: Boolean
    affectedStaffNotified: List<StaffReference>
  }
}
```

---

## 6. 资源调度系统

### 6.1 床位管理

**床位管理Schema**：

```dsl
schema BedManagement {
  resourceType: String @value("BedManagement") @required
  
  // 床位信息
  bed: Bed {
    bedId: String @required
    bedNumber: String @required
    bedType: Enum { 
      standard, deluxe, icu, ccu, nicu, 
      isolation, observation, recovery 
    } @required
    ward: Ward {
      wardId: String @required
      wardName: String @required
      department: String @required
      floor: String
      building: String
    }
    room: Room {
      roomId: String @required
      roomNumber: String @required
      roomType: Enum { single, double, triple, quad, ward }
      amenities: List<String>
    }
    features: List<BedFeature> {
      hasOxygen: Boolean @default(false)
      hasSuction: Boolean @default(false)
      hasMonitor: Boolean @default(false)
      hasIsolation: Boolean @default(false)
      isPressureRelief: Boolean @default(false)
    }
  }
  
  // 床位状态
  status: BedStatus {
    currentStatus: Enum { 
      available, occupied, reserved, blocked, 
      maintenance, cleaning, out_of_service 
    } @required
    currentPatient: PatientReference
    admissionId: String
    expectedDischarge: DateTime
    holdUntil: DateTime
    holdReason: String
    blockedReason: String
  }
  
  // 占用历史
  occupancyHistory: List<OccupancyRecord> {
    recordId: String @required
    patient: PatientReference @required
    admission: AdmissionReference @required
    checkInTime: DateTime @required
    checkOutTime: DateTime
    lengthOfStay: Integer  // 小时
  }
  
  // 维护记录
  maintenance: List<MaintenanceRecord> {
    maintenanceId: String @required
    maintenanceType: Enum { cleaning, repair, inspection, upgrade }
    scheduledTime: DateTime @required
    completedTime: DateTime
    technician: Practitioner
    description: String
    status: Enum { scheduled, in_progress, completed, cancelled }
  }
}

schema Admission {
  admissionId: String @required
  patient: PatientReference @required
  
  // 入院信息
  admissionInfo: AdmissionInfo {
    admissionType: Enum { elective, emergency, urgent, newborn, transfer } @required
    admissionSource: Enum { physician_referral, clinic_referral, er, transfer, other }
    admissionTime: DateTime @required
    admittingDoctor: Practitioner @required
    admittingDepartment: String @required
    preliminaryDiagnosis: String
  }
  
  // 床位分配
  bedAssignment: BedAssignment {
    assignedBed: Bed @required
    assignedTime: DateTime @required
    assignedBy: Practitioner @required
    expectedStay: Integer  // 预计住院天数
    roomPreference: String
    specialRequirements: List<String>
  }
  
  // 住院状态
  status: AdmissionStatus {
    currentStatus: Enum { admitted, transferred, discharged, deceased } @required
    currentLocation: Location
    attendingDoctor: Practitioner
    primaryNurse: Practitioner
    careTeam: List<Practitioner>
  }
  
  // 出院计划
  discharge: DischargePlan {
    plannedDischargeDate: Date
    dischargeDisposition: Enum { home, transfer, rehab, nursing, deceased }
    dischargeDiagnosis: String
    followUpInstructions: String
    actualDischargeTime: DateTime
  }
}
```

### 6.2 手术室调度

**手术室调度Schema**：

```dsl
schema ORSchedule {
  resourceType: String @value("ORSchedule") @required
  
  scheduleId: String @required
  
  // 手术信息
  surgery: Surgery {
    surgeryId: String @required
    surgeryRequestId: String @required
    patient: PatientReference @required
    surgeryType: Enum { elective, emergency, urgent } @required
    procedureCodes: List<ProcedureCode> {
      code: String @required
      description: String @required
      cptCode: String
      icd9cmCode: String
      estimatedDuration: Integer  // 分钟
    }
    diagnosisCodes: List<DiagnosisCode>
    surgicalPriority: Enum { low, medium, high, critical }
  }
  
  // 手术安排
  scheduling: SurgeryScheduling {
    scheduledDate: Date @required
    scheduledStartTime: Time @required
    scheduledEndTime: Time
    estimatedDuration: Integer @required
    orRoom: OperatingRoom {
      roomId: String @required
      roomNumber: String @required
      roomType: Enum { general, cardiac, neuro, ortho, obgyn, pediatric }
      equipment: List<String>
    }
    status: Enum { scheduled, confirmed, in_progress, completed, cancelled, delayed }
  }
  
  // 手术团队
  surgicalTeam: SurgicalTeam {
    primarySurgeon: Practitioner @required
    assistantSurgeons: List<Practitioner>
    anesthesiologist: Practitioner @required
    scrubNurses: List<Practitioner>
    circulatingNurses: List<Practitioner>
    otherStaff: List<StaffReference>
  }
  
  // 术前准备
  preOp: PreOpPreparation {
    preOpAssessmentCompleted: Boolean @default(false)
    consentSigned: Boolean @default(false)
    anesthesiaEvaluation: Boolean @default(false)
    requiredLabsCompleted: Boolean @default(false)
    npoStatus: Enum { compliant, not_compliant, unknown }
    patientArrived: Boolean @default(false)
    patientReady: Boolean @default(false)
    holdReasons: List<String>
  }
  
  // 手术执行
  execution: SurgeryExecution {
    actualStartTime: DateTime
    actualEndTime: DateTime
    actualDuration: Integer
    procedurePerformed: String
    complications: List<String>
    estimatedBloodLoss: Quantity
    specimensCollected: List<String>
    implantsUsed: List<String>
    closureTime: DateTime
    patientCondition: Enum { stable, critical, deceased }
    patientDestination: Enum { pacu, icu, ward, other_or }
  }
  
  // 资源冲突检测
  conflictDetection: ConflictDetection {
    conflicts: List<ScheduleConflict> {
      conflictType: Enum { room_overlap, staff_overlap, equipment_unavailable }
      severity: Enum { warning, error }
      description: String
      suggestedResolution: String
    }
    autoResolved: Boolean
  }
}
```

### 6.3 检查设备调度

**检查设备调度Schema**：

```dsl
schema ImagingSchedule {
  resourceType: String @value("ImagingSchedule") @required
  
  scheduleId: String @required
  orderId: String @required
  
  // 检查申请
  order: ImagingOrder {
    patient: PatientReference @required
    examType: Enum { 
      xray, ct, mri, ultrasound, mammography, 
      nuclear_medicine, pet, fluoroscopy 
    } @required
    examCode: String @required
    examDescription: String @required
    bodyPart: String @required
    clinicalIndication: String @required
    priority: Enum { routine, urgent, stat } @required
    contrastRequired: Boolean @default(false)
    contrastType: String
    specialInstructions: String
  }
  
  // 设备安排
  equipment: EquipmentAssignment {
    modality: ImagingModality {
      modalityId: String @required
      modalityType: Enum { CT, MR, XR, US, NM, PET } @required
      manufacturer: String
      model: String
      location: Location @required
    }
    scheduledDateTime: DateTime @required
    estimatedDuration: Integer @default(30)
    technician: Practitioner
    radiologist: Practitioner
  }
  
  // 患者准备
  patientPrep: PatientPreparation {
    prepInstructionsSent: Boolean @default(false)
    fastingRequired: Boolean @default(false)
    fastingHours: Integer
    contrastConsent: Boolean
    allergiesVerified: Boolean @default(false)
    renalFunctionChecked: Boolean @default(false)
    pregnancyStatus: Enum { not_pregnant, pregnant, unknown, n_a }
    patientArrived: Boolean @default(false)
    patientPrepped: Boolean @default(false)
  }
  
  // 检查执行
  execution: ImagingExecution {
    status: Enum { scheduled, checked_in, in_progress, completed, cancelled, no_show }
    actualStartTime: DateTime
    actualEndTime: DateTime
    imagesAcquired: Integer
    contrastAdministered: Boolean
    complications: List<String>
    technicianNotes: String
    imagesTransferredToPACS: Boolean
  }
  
  // 报告
  report: ImagingReport {
    reportId: String
    radiologist: Practitioner
    reportTime: DateTime
    impression: String
    findings: String
    criticalFindings: Boolean @default(false)
    notificationSent: Boolean @default(false)
  }
}
```

---

## 7. 应用场景

### 7.1 门诊管理

**门诊流程优化**：

- **智能分诊**：根据症状自动分诊到相应科室
- **排队叫号**：实时叫号系统，支持多渠道通知
- **诊室分配**：动态分配诊室，提高利用率
- **流量预测**：基于历史数据预测门诊流量

### 7.2 住院管理

**住院全流程管理**：

- **入院管理**：入院评估、床位分配、入院宣教
- **在院管理**：医嘱执行、护理记录、费用监控
- **出院管理**：出院评估、出院指导、随访安排
- **转科转院**：转科申请、转院协调、资料转移

### 7.3 急诊管理

**急诊绿色通道**：

- **预检分诊**：五级分诊，危重优先
- **绿色通道**：心梗、卒中、创伤快速通道
- **急诊留观**：留观病房管理、病情监测
- **急诊入院**：急诊到住院的快速衔接

### 7.4 医疗资源优化

**资源优化策略**：

- **床位利用率**：实时监测床位使用情况
- **手术室效率**：减少非手术时间，提高周转
- **检查设备利用率**：错峰预约，减少等待
- **人力资源优化**：智能排班，减少加班

---

## 8. 思维导图

```text
Hospital Management Schema
│
├─ HIS系统架构
│   ├─ 用户接入层 (Web/移动/自助)
│   ├─ API网关层 (认证/路由/限流)
│   ├─ 微服务层 (患者/预约/排班/收费)
│   ├─ 数据层 (主库/缓存/数仓)
│   └─ 集成层 (HL7/FHIR/医保)
│
├─ 预约挂号系统
│   ├─ 预约流程 (选择/确认/提醒)
│   ├─ 号源管理 (生成/分配/状态)
│   └─ 取消改约 (规则/退款/通知)
│
├─ 排班管理系统
│   ├─ 排班模式 (固定/轮班/弹性)
│   ├─ 班次类型 (门诊/急诊/病房)
│   └─ 调班管理 (申请/审批/执行)
│
├─ 资源调度系统
│   ├─ 床位管理 (分配/状态/历史)
│   ├─ 手术室调度 (安排/团队/执行)
│   └─ 检查设备调度 (预约/准备/报告)
│
└─ 应用场景
    ├─ 门诊管理
    ├─ 住院管理
    ├─ 急诊管理
    └─ 资源优化
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-02-15
**最后更新**：2025-02-15
