# 医疗信息系统Schema实践案例

## 📑 目录

- [医疗信息系统Schema实践案例](#医疗信息系统schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：MediCore综合医院数字化升级](#2-案例1medicore综合医院数字化升级)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：临床数据记录](#3-案例2临床数据记录)
  - [4. 案例3：诊断记录管理](#4-案例3诊断记录管理)
  - [5. 案例4：FHIR到HL7转换](#5-案例4fhir到hl7转换)
  - [6. 案例5：医疗数据存储与分析系统](#6-案例5医疗数据存储与分析系统)

---

## 1. 案例概述

本文档提供医疗信息系统Schema在实际应用中的实践案例，涵盖患者管理、临床数据、诊断记录等核心场景。

---

## 2. 案例1：MediCore综合医院数字化升级

### 2.1 企业背景

**MediCore综合医院**是区域性三级甲等医院，拥有2,800张床位，年门诊量450万人次，年住院量18万人次，是区域医疗中心。

- **成立时间**：1952年
- **员工规模**：5,200人（医生850人，护士2,100人）
- **科室数量**：48个临床科室，22个医技科室
- **年医疗收入**：45亿元人民币
- **原系统**：HIS、LIS、PACS、EMR等系统独立运行，数据孤岛严重

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **信息孤岛** | 严重 | 各系统数据不互通，医生需登录5+系统查看患者信息 |
| 2 | **病历书写效率低** | 高 | 医生日均书写病历3.5小时，占工作时间35% |
| 3 | **药品管理混乱** | 高 | 药品库存周转慢，过期损耗年达200万元 |
| 4 | **检查预约排队长** | 中 | MRI/CT平均预约等待7天，患者满意度低 |
| 5 | **医保结算慢** | 中 | 医保结算平均耗时15分钟/人次，窗口压力大 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 系统集成覆盖率 | 30% | 95% | 18个月 |
| 2 | 病历书写时间占比 | 35% | <15% | 12个月 |
| 3 | 药品过期损耗 | 200万元/年 | <50万元/年 | 9个月 |
| 4 | 检查预约等待 | 7天 | <3天 | 12个月 |
| 5 | 医保结算时间 | 15分钟 | <3分钟 | 9个月 |

### 2.4 技术挑战

1. **多厂商系统集成**：需整合15+厂商的异构系统，接口标准不一

2. **数据标准统一**：需建立统一的数据字典，规范18万+条临床术语

3. **实时数据同步**：核心业务系统需保证秒级数据同步

4. **高可用性要求**：HIS系统需保证99.99%可用性

5. **合规性要求**：需满足电子病历评级、互联互通评级要求

### 2.5 Schema定义

**患者信息Schema**：

```dsl
schema PatientInfo {
  patient_id: String @value("P1234567890") @required

  basic_info: {
    name: String @value("张三")
    gender: Enum { M, F } @value(M)
    birth_date: Date @value("1980-05-15") @format("YYYY-MM-DD")
    id_number: String @value("110101198005151234") @length(18)
    marital_status: Enum { Single, Married, Divorced, Widowed }
    nationality: String @value("CN")
  } @required

  contact_info: {
    phone: String @value("13800138000")
    address: String @value("北京市朝阳区XX街道XX号")
    emergency_contact: {
      name: String @value("李四")
      phone: String @value("13900139000")
      relationship: String @value("配偶")
    }
  }

  medical_info: {
    blood_type: Enum { A, B, AB, O } @value(A)
    rh_factor: Enum { Positive, Negative } @value(Positive)
    allergies: List[String] @value(["青霉素", "磺胺"])
    chronic_diseases: List[String] @value(["高血压"])
  }

  insurance_info: {
    insurance_type: Enum { Public, Commercial, SelfPay } @value(Public)
    insurance_number: String @value("BJ123456789")
    insurance_provider: String @value("北京市医保")
  }
} @standard("HL7_FHIR_R4")
```

### 2.6 完整实现代码

```python
"""
MediCore综合医院医疗信息系统
集成患者管理、临床数据、药品管理、预约系统等模块
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict


class Gender(Enum):
    """性别"""
    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class BloodType(Enum):
    """血型"""
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"
    UNKNOWN = "Unknown"


class PatientStatus(Enum):
    """患者状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"


class AppointmentStatus(Enum):
    """预约状态"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked-in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no-show"


@dataclass
class Patient:
    """患者信息"""
    patient_id: str
    name: str
    gender: Gender
    birth_date: date
    id_number: str
    phone: str = ""
    address: str = ""
    blood_type: BloodType = BloodType.UNKNOWN
    rh_factor: str = "Positive"
    allergies: List[str] = field(default_factory=list)
    chronic_diseases: List[str] = field(default_factory=list)
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    insurance_type: str = "Public"
    insurance_number: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    status: PatientStatus = PatientStatus.ACTIVE
    
    def __post_init__(self):
        if isinstance(self.birth_date, str):
            self.birth_date = date.fromisoformat(self.birth_date)
    
    def calculate_age(self) -> int:
        """计算年龄"""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def get_age_group(self) -> str:
        """获取年龄组"""
        age = self.calculate_age()
        if age < 1:
            return "婴儿"
        elif age < 6:
            return "幼儿"
        elif age < 18:
            return "儿童"
        elif age < 60:
            return "成人"
        else:
            return "老年人"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "gender": self.gender.value,
            "birth_date": self.birth_date.isoformat(),
            "age": self.calculate_age(),
            "age_group": self.get_age_group(),
            "id_number": self.id_number,
            "phone": self.phone,
            "address": self.address,
            "blood_type": self.blood_type.value,
            "rh_factor": self.rh_factor,
            "allergies": self.allergies,
            "chronic_diseases": self.chronic_diseases,
            "emergency_contact": {
                "name": self.emergency_contact_name,
                "phone": self.emergency_contact_phone
            },
            "insurance": {
                "type": self.insurance_type,
                "number": self.insurance_number
            },
            "status": self.status.value
        }


@dataclass
class VitalSigns:
    """生命体征"""
    temperature: Optional[float] = None  # 摄氏度
    heart_rate: Optional[int] = None  # 次/分钟
    systolic_bp: Optional[int] = None  # 收缩压 mmHg
    diastolic_bp: Optional[int] = None  # 舒张压 mmHg
    respiratory_rate: Optional[int] = None  # 呼吸频率 次/分钟
    oxygen_saturation: Optional[float] = None  # 血氧饱和度 %
    weight: Optional[float] = None  # 体重 kg
    height: Optional[float] = None  # 身高 cm
    recorded_at: datetime = field(default_factory=datetime.now)
    recorded_by: str = ""
    
    def get_bmi(self) -> Optional[float]:
        """计算BMI"""
        if self.weight and self.height and self.height > 0:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    def get_bp_category(self) -> str:
        """获取血压分类"""
        if not self.systolic_bp or not self.diastolic_bp:
            return "未知"
        
        if self.systolic_bp < 120 and self.diastolic_bp < 80:
            return "正常"
        elif self.systolic_bp < 130 and self.diastolic_bp < 80:
            return "正常高值"
        elif self.systolic_bp < 140 or self.diastolic_bp < 90:
            return "1级高血压"
        else:
            return "2级高血压"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "temperature": self.temperature,
            "heart_rate": self.heart_rate,
            "blood_pressure": {
                "systolic": self.systolic_bp,
                "diastolic": self.diastolic_bp,
                "category": self.get_bp_category()
            },
            "respiratory_rate": self.respiratory_rate,
            "oxygen_saturation": self.oxygen_saturation,
            "weight": self.weight,
            "height": self.height,
            "bmi": self.get_bmi(),
            "recorded_at": self.recorded_at.isoformat(),
            "recorded_by": self.recorded_by
        }


@dataclass
class Diagnosis:
    """诊断记录"""
    diagnosis_id: str
    patient_id: str
    diagnosis_code: str  # ICD-10编码
    diagnosis_name: str
    diagnosis_type: str  # 主要诊断/次要诊断
    onset_date: date
    status: str  # active, resolved, chronic
    doctor_id: str = ""
    doctor_name: str = ""
    notes: str = ""
    recorded_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnosis_id": self.diagnosis_id,
            "patient_id": self.patient_id,
            "code": self.diagnosis_code,
            "name": self.diagnosis_name,
            "type": self.diagnosis_type,
            "onset_date": self.onset_date.isoformat(),
            "status": self.status,
            "doctor": {
                "id": self.doctor_id,
                "name": self.doctor_name
            },
            "notes": self.notes,
            "recorded_at": self.recorded_at.isoformat()
        }


@dataclass
class Medication:
    """药品信息"""
    medication_id: str
    name: str
    generic_name: str
    dosage_form: str  # 剂型
    strength: str  # 规格
    manufacturer: str
    unit_price: Decimal
    stock_quantity: int
    expiry_date: date
    storage_condition: str = "常温"
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> int:
        """距离过期天数"""
        return (self.expiry_date - date.today()).days
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "medication_id": self.medication_id,
            "name": self.name,
            "generic_name": self.generic_name,
            "dosage_form": self.dosage_form,
            "strength": self.strength,
            "manufacturer": self.manufacturer,
            "unit_price": str(self.unit_price),
            "stock_quantity": self.stock_quantity,
            "expiry_date": self.expiry_date.isoformat(),
            "is_expired": self.is_expired(),
            "days_until_expiry": self.days_until_expiry(),
            "storage_condition": self.storage_condition
        }


@dataclass
class MedicationOrder:
    """医嘱/处方"""
    order_id: str
    patient_id: str
    medication_id: str
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    quantity: int
    route: str  # 给药途径
    instructions: str = ""
    doctor_id: str = ""
    doctor_name: str = ""
    order_time: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, active, completed, cancelled
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "patient_id": self.patient_id,
            "medication": {
                "id": self.medication_id,
                "name": self.medication_name
            },
            "dosage": self.dosage,
            "frequency": self.frequency,
            "duration": self.duration,
            "quantity": self.quantity,
            "route": self.route,
            "instructions": self.instructions,
            "doctor": {
                "id": self.doctor_id,
                "name": self.doctor_name
            },
            "order_time": self.order_time.isoformat(),
            "status": self.status
        }


@dataclass
class Appointment:
    """预约记录"""
    appointment_id: str
    patient_id: str
    patient_name: str
    department: str
    doctor_id: str
    doctor_name: str
    appointment_date: date
    appointment_time: str
    appointment_type: str  # 门诊/检查/手术
    status: AppointmentStatus = AppointmentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "appointment_id": self.appointment_id,
            "patient": {
                "id": self.patient_id,
                "name": self.patient_name
            },
            "department": self.department,
            "doctor": {
                "id": self.doctor_id,
                "name": self.doctor_name
            },
            "appointment_datetime": f"{self.appointment_date.isoformat()} {self.appointment_time}",
            "type": self.appointment_type,
            "status": self.status.value,
            "notes": self.notes
        }


class HospitalInformationSystem:
    """医院信息系统"""
    
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.vital_signs: Dict[str, List[VitalSigns]] = defaultdict(list)
        self.diagnoses: Dict[str, List[Diagnosis]] = defaultdict(list)
        self.medications: Dict[str, Medication] = {}
        self.medication_orders: Dict[str, List[MedicationOrder]] = defaultdict(list)
        self.appointments: Dict[str, Appointment] = {}
        self.doctor_appointments: Dict[str, List[str]] = defaultdict(list)
        
        # 统计指标
        self.metrics = {
            "total_patients": 0,
            "daily_visits": 0,
            "appointments_today": 0,
            "pending_prescriptions": 0
        }
    
    def register_patient(self, patient: Patient) -> str:
        """登记患者"""
        if not patient.patient_id:
            patient.patient_id = f"P{datetime.now().strftime('%Y%m%d')}{len(self.patients)+1:06d}"
        self.patients[patient.patient_id] = patient
        self.metrics["total_patients"] += 1
        return patient.patient_id
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """获取患者信息"""
        return self.patients.get(patient_id)
    
    def search_patients(self, name: Optional[str] = None, 
                       id_number: Optional[str] = None) -> List[Patient]:
        """搜索患者"""
        results = []
        for patient in self.patients.values():
            if name and name.lower() in patient.name.lower():
                results.append(patient)
            elif id_number and patient.id_number == id_number:
                results.append(patient)
        return results
    
    def record_vital_signs(self, patient_id: str, vitals: VitalSigns):
        """记录生命体征"""
        if patient_id in self.patients:
            self.vital_signs[patient_id].append(vitals)
    
    def get_vital_signs(self, patient_id: str) -> List[VitalSigns]:
        """获取生命体征历史"""
        return self.vital_signs.get(patient_id, [])
    
    def add_diagnosis(self, diagnosis: Diagnosis):
        """添加诊断"""
        self.diagnoses[diagnosis.patient_id].append(diagnosis)
    
    def get_diagnoses(self, patient_id: str) -> List[Diagnosis]:
        """获取诊断历史"""
        return self.diagnoses.get(patient_id, [])
    
    def add_medication(self, medication: Medication):
        """添加药品"""
        self.medications[medication.medication_id] = medication
    
    def create_medication_order(self, order: MedicationOrder):
        """创建医嘱"""
        if not order.order_id:
            order.order_id = f"MO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
        self.medication_orders[order.patient_id].append(order)
        self.metrics["pending_prescriptions"] += 1
    
    def create_appointment(self, appointment: Appointment) -> str:
        """创建预约"""
        if not appointment.appointment_id:
            appointment.appointment_id = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4]}"
        self.appointments[appointment.appointment_id] = appointment
        self.doctor_appointments[appointment.doctor_id].append(appointment.appointment_id)
        return appointment.appointment_id
    
    def get_doctor_schedule(self, doctor_id: str, date: date) -> List[Appointment]:
        """获取医生排班"""
        appointments = []
        for apt_id in self.doctor_appointments.get(doctor_id, []):
            apt = self.appointments.get(apt_id)
            if apt and apt.appointment_date == date:
                appointments.append(apt)
        return sorted(appointments, key=lambda a: a.appointment_time)
    
    def get_expiring_medications(self, days: int = 30) -> List[Medication]:
        """获取即将过期的药品"""
        expiring = []
        for med in self.medications.values():
            if 0 < med.days_until_expiry() <= days:
                expiring.append(med)
        return sorted(expiring, key=lambda m: m.days_until_expiry())
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """获取患者摘要"""
        patient = self.get_patient(patient_id)
        if not patient:
            return {}
        
        vitals = self.get_vital_signs(patient_id)
        diagnoses = self.get_diagnoses(patient_id)
        orders = self.medication_orders.get(patient_id, [])
        
        return {
            "patient": patient.to_dict(),
            "latest_vitals": vitals[-1].to_dict() if vitals else None,
            "active_diagnoses": [d.to_dict() for d in diagnoses if d.status == "active"],
            "current_medications": [o.to_dict() for o in orders if o.status == "active"],
            "summary": {
                "age": patient.calculate_age(),
                "age_group": patient.get_age_group(),
                "allergy_count": len(patient.allergies),
                "chronic_disease_count": len(patient.chronic_diseases),
                "visit_count": len(vitals)
            }
        }
    
    def get_daily_statistics(self) -> Dict[str, Any]:
        """获取每日统计"""
        today = date.today()
        
        # 今日预约
        today_appointments = [
            apt for apt in self.appointments.values()
            if apt.appointment_date == today
        ]
        
        # 待处理处方
        pending_rx = sum(
            1 for orders in self.medication_orders.values()
            for o in orders if o.status == "pending"
        )
        
        # 即将过期药品
        expiring_meds = len(self.get_expiring_medications(30))
        
        return {
            "date": today.isoformat(),
            "total_patients": self.metrics["total_patients"],
            "today_appointments": len(today_appointments),
            "pending_prescriptions": pending_rx,
            "expiring_medications_30d": expiring_meds,
            "appointments_by_status": {
                status.value: sum(1 for a in today_appointments if a.status == status)
                for status in AppointmentStatus
            }
        }


def main():
    """主函数 - 演示"""
    his = HospitalInformationSystem()
    
    # 登记患者
    patient = Patient(
        patient_id="P20250121001",
        name="张三",
        gender=Gender.MALE,
        birth_date=date(1980, 5, 15),
        id_number="110101198005151234",
        phone="13800138000",
        address="北京市朝阳区XX街道XX号",
        blood_type=BloodType.A,
        allergies=["青霉素", "磺胺"],
        chronic_diseases=["高血压", "2型糖尿病"],
        emergency_contact_name="李四",
        emergency_contact_phone="13900139000",
        insurance_type="城镇职工医保",
        insurance_number="110101198005151234"
    )
    patient_id = his.register_patient(patient)
    print(f"登记患者: {patient_id} - {patient.name}")
    
    # 记录生命体征
    vitals = VitalSigns(
        temperature=36.5,
        heart_rate=72,
        systolic_bp=135,
        diastolic_bp=85,
        respiratory_rate=18,
        oxygen_saturation=98.5,
        weight=70.5,
        height=175.0,
        recorded_by="王医生"
    )
    his.record_vital_signs(patient_id, vitals)
    print(f"\n生命体征记录完成:")
    print(f"  BMI: {vitals.get_bmi()}")
    print(f"  血压分类: {vitals.get_bp_category()}")
    
    # 添加诊断
    diagnosis = Diagnosis(
        diagnosis_id="D001",
        patient_id=patient_id,
        diagnosis_code="I10",
        diagnosis_name="原发性高血压",
        diagnosis_type="主要诊断",
        onset_date=date(2020, 3, 15),
        status="active",
        doctor_id="DOC001",
        doctor_name="王医生"
    )
    his.add_diagnosis(diagnosis)
    print(f"\n添加诊断: {diagnosis.diagnosis_name}")
    
    # 添加药品
    medication = Medication(
        medication_id="M001",
        name="阿托伐他汀钙片",
        generic_name="Atorvastatin Calcium",
        dosage_form="片剂",
        strength="20mg",
        manufacturer="辉瑞制药",
        unit_price=Decimal("3.50"),
        stock_quantity=500,
        expiry_date=date(2026, 12, 31)
    )
    his.add_medication(medication)
    
    # 创建医嘱
    order = MedicationOrder(
        order_id="MO001",
        patient_id=patient_id,
        medication_id="M001",
        medication_name="阿托伐他汀钙片",
        dosage="20mg",
        frequency="每晚一次",
        duration="30天",
        quantity=30,
        route="口服",
        instructions="睡前服用",
        doctor_id="DOC001",
        doctor_name="王医生"
    )
    his.create_medication_order(order)
    print(f"创建医嘱: {order.medication_name}")
    
    # 创建预约
    appointment = Appointment(
        appointment_id="APT001",
        patient_id=patient_id,
        patient_name=patient.name,
        department="心内科",
        doctor_id="DOC001",
        doctor_name="王医生",
        appointment_date=date(2025, 1, 28),
        appointment_time="09:00",
        appointment_type="门诊复诊",
        notes="高血压随访"
    )
    his.create_appointment(appointment)
    print(f"创建预约: {appointment.appointment_date} {appointment.appointment_time}")
    
    # 获取患者摘要
    print("\n=== 患者摘要 ===")
    summary = his.get_patient_summary(patient_id)
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    
    # 获取每日统计
    print("\n=== 每日统计 ===")
    stats = his.get_daily_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 系统集成覆盖率 | 30% | 92% | +62% |
| 病历书写时间占比 | 35% | 12% | -66% |
| 药品过期损耗 | 200万元/年 | 35万元/年 | -82% |
| 检查预约等待 | 7天 | 2.5天 | -64% |
| 医保结算时间 | 15分钟 | 2分钟 | -87% |

#### ROI计算

**投资成本**（18个月项目周期）：
- 系统开发与集成：2,800万元
- 硬件升级：1,200万元
- 数据迁移：600万元
- 培训：400万元
- **总投资**：5,000万元

**年度收益**：
- 效率提升：1,200万元
- 药品损耗减少：165万元
- 患者满意度提升：800万元
- **年度总收益**：2,165万元

**ROI分析**：
- 投资回收期：27.7个月
- 5年ROI：117%

#### 经验教训

**成功因素**：
1. **统一数据标准**：建立全院统一数据字典，规范18万+条术语
2. **临床参与**：医生全程参与系统设计，符合临床实际需求
3. **分步实施**：先门诊后住院，先基础后高级功能

**挑战与应对**：
1. **系统切换风险**：采用双轨运行，逐步切换
2. **医生抵触**：加强培训，展示系统价值
3. **数据质量问题**：建立数据质量监控体系

---

## 3. 案例2：临床数据记录

详见 `04_Transformation.md` 第3章。

## 4. 案例3：诊断记录管理

详见 `04_Transformation.md` 第4章。

## 5. 案例4：FHIR到HL7转换

详见 `04_Transformation.md` 第2章。

## 6. 案例5：医疗数据存储与分析系统

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
