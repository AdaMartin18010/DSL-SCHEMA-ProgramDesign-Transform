# 医院管理Schema转换体系

## 📑 目录

- [医院管理Schema转换体系](#医院管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 患者流转转换](#2-患者流转转换)
    - [2.1 门诊患者流转](#21-门诊患者流转)
    - [2.2 住院患者流转](#22-住院患者流转)
    - [2.3 急诊绿色通道](#23-急诊绿色通道)
  - [3. 资源优化转换](#3-资源优化转换)
    - [3.1 床位资源优化](#31-床位资源优化)
    - [3.2 手术室资源优化](#32-手术室资源优化)
    - [3.3 人力资源优化](#33-人力资源优化)
  - [4. 跨系统数据交换](#4-跨系统数据交换)
    - [4.1 HIS与EMR集成](#41-his与emr集成)
    - [4.2 与区域平台对接](#42-与区域平台对接)
  - [5. 业务流程优化](#5-业务流程优化)
  - [6. 性能监控与优化](#6-性能监控与优化)

---

## 1. 转换体系概述

医院管理Schema转换体系支持以下转换场景：

1. **患者流转转换**：从入院到出院的全流程数据转换
2. **资源优化转换**：床位、手术室、人员的优化调度
3. **跨系统交换**：HIS、EMR、区域平台间的数据交换
4. **流程优化**：业务流程的数字化转型
5. **数据分析**：运营数据的提取和分析

**转换架构**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           业务应用层                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 患者流转管理  │ │ 资源调度优化  │ │ 运营分析      │ │ 质量监控      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                           转换服务层                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 患者流转转换  │ │ 资源优化转换  │ │ 数据标准化    │ │ 流程引擎      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                           集成接口层                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ HL7/FHIR接口 │ │ 数据库接口    │ │ 消息队列      │ │ API网关       │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                           数据源层                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ HIS系统      │ │ EMR系统      │ │ LIS/PACS    │ │ 区域平台      │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 患者流转转换

### 2.1 门诊患者流转

**门诊患者流转流程**：

```
预约 → 挂号 → 分诊 → 候诊 → 就诊 → 医嘱 → 缴费 → 执行 → 取药/检查 → 离院
```

**转换实现**：

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OutpatientFlowConverter:
    """门诊患者流转转换器"""

    def __init__(self):
        self.flow_stages = [
            'appointment', 'registration', 'triage', 'waiting',
            'consultation', 'orders', 'payment', 'execution',
            'pharmacy_lab', 'departure'
        ]

    def convert_patient_flow(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换门诊患者全流程数据

        Args:
            patient_data: 患者基础数据

        Returns:
            完整的患者流转数据
        """
        flow_data = {
            'patientId': patient_data.get('patientId'),
            'mrn': patient_data.get('mrn'),
            'visitId': self._generate_visit_id(),
            'flowStartTime': datetime.now(),
            'currentStage': 'appointment',
            'stages': {},
            'flowStatus': 'active'
        }

        # 初始化各阶段
        for stage in self.flow_stages:
            flow_data['stages'][stage] = {
                'status': 'pending',
                'startTime': None,
                'endTime': None,
                'duration': None,
                'data': {}
            }

        return flow_data

    def update_stage(self, flow_data: Dict[str, Any],
                    stage: str,
                    status: str,
                    data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        更新流转阶段状态

        Args:
            flow_data: 流转数据
            stage: 阶段名称
            status: 状态 (pending, active, completed, skipped)
            data: 阶段数据

        Returns:
            更新后的流转数据
        """
        if stage not in flow_data['stages']:
            raise ValueError(f"Invalid stage: {stage}")

        stage_data = flow_data['stages'][stage]

        if status == 'active' and stage_data['status'] == 'pending':
            stage_data['startTime'] = datetime.now()
            flow_data['currentStage'] = stage
        elif status == 'completed' and stage_data['status'] == 'active':
            stage_data['endTime'] = datetime.now()
            stage_data['duration'] = (
                stage_data['endTime'] - stage_data['startTime']
            ).total_seconds() / 60  # 分钟

        stage_data['status'] = status

        if data:
            stage_data['data'].update(data)

        # 更新整体状态
        self._update_flow_status(flow_data)

        return flow_data

    def _update_flow_status(self, flow_data: Dict[str, Any]):
        """更新整体流转状态"""
        completed_stages = sum(
            1 for s in flow_data['stages'].values()
            if s['status'] == 'completed'
        )

        total_stages = len(self.flow_stages)

        if completed_stages == total_stages:
            flow_data['flowStatus'] = 'completed'
            flow_data['flowEndTime'] = datetime.now()
            flow_data['totalDuration'] = (
                flow_data['flowEndTime'] - flow_data['flowStartTime']
            ).total_seconds() / 60
        elif completed_stages == 0:
            flow_data['flowStatus'] = 'not_started'
        else:
            flow_data['flowStatus'] = 'in_progress'
            flow_data['progressPercentage'] = (completed_stages / total_stages) * 100

    def get_bottlenecks(self, flow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        识别流转瓶颈

        Args:
            flow_data: 流转数据

        Returns:
            瓶颈列表
        """
        bottlenecks = []

        # 定义各阶段标准时长（分钟）
        standard_durations = {
            'appointment': 5,
            'registration': 10,
            'triage': 15,
            'waiting': 30,
            'consultation': 20,
            'orders': 10,
            'payment': 10,
            'execution': 30,
            'pharmacy_lab': 20,
            'departure': 5
        }

        for stage_name, stage_data in flow_data['stages'].items():
            if stage_data['status'] == 'completed' and stage_data['duration']:
                standard = standard_durations.get(stage_name, 30)
                if stage_data['duration'] > standard * 2:
                    bottlenecks.append({
                        'stage': stage_name,
                        'actualDuration': stage_data['duration'],
                        'standardDuration': standard,
                        'delayFactor': stage_data['duration'] / standard,
                        'severity': 'high' if stage_data['duration'] > standard * 3 else 'medium'
                    })

        return sorted(bottlenecks, key=lambda x: x['delayFactor'], reverse=True)

    def generate_flow_report(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成流转报告

        Args:
            flow_data: 流转数据

        Returns:
            流转分析报告
        """
        report = {
            'patientId': flow_data['patientId'],
            'visitId': flow_data['visitId'],
            'reportGeneratedAt': datetime.now(),
            'flowStatus': flow_data['flowStatus'],
            'summary': {
                'totalStages': len(self.flow_stages),
                'completedStages': sum(
                    1 for s in flow_data['stages'].values()
                    if s['status'] == 'completed'
                ),
                'totalDuration': flow_data.get('totalDuration'),
                'averageStageDuration': None
            },
            'stageDetails': [],
            'bottlenecks': self.get_bottlenecks(flow_data),
            'recommendations': []
        }

        # 计算平均阶段时长
        completed_durations = [
            s['duration'] for s in flow_data['stages'].values()
            if s['status'] == 'completed' and s['duration']
        ]
        if completed_durations:
            report['summary']['averageStageDuration'] = sum(completed_durations) / len(completed_durations)

        # 详细阶段信息
        for stage_name, stage_data in flow_data['stages'].items():
            report['stageDetails'].append({
                'stage': stage_name,
                'status': stage_data['status'],
                'startTime': stage_data['startTime'],
                'endTime': stage_data['endTime'],
                'duration': stage_data['duration']
            })

        # 生成优化建议
        report['recommendations'] = self._generate_recommendations(report['bottlenecks'])

        return report

    def _generate_recommendations(self, bottlenecks: List[Dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        for bottleneck in bottlenecks:
            stage = bottleneck['stage']
            if stage == 'waiting':
                recommendations.append(
                    "建议优化候诊区管理，增加分诊人员或启用智能叫号系统"
                )
            elif stage == 'consultation':
                recommendations.append(
                    "建议优化诊室资源分配，考虑增加诊室或调整排班"
                )
            elif stage == 'payment':
                recommendations.append(
                    "建议增加移动支付渠道，推广诊间结算"
                )
            elif stage == 'pharmacy_lab':
                recommendations.append(
                    "建议优化药房/检验科工作流程，增加自助服务设备"
                )

        return recommendations

    def _generate_visit_id(self) -> str:
        """生成就诊ID"""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"V{timestamp}{uuid.uuid4().hex[:6].upper()}"


# 门诊流转优化示例
class OutpatientFlowOptimizer:
    """门诊流转优化器"""

    def __init__(self, historical_data: List[Dict[str, Any]]):
        self.historical_data = historical_data
        self.flow_patterns = self._analyze_flow_patterns()

    def _analyze_flow_patterns(self) -> Dict[str, Any]:
        """分析历史流转模式"""
        patterns = {
            'peak_hours': self._identify_peak_hours(),
            'bottleneck_stages': self._identify_common_bottlenecks(),
            'seasonal_patterns': self._identify_seasonal_patterns(),
            'average_flow_times': self._calculate_average_flow_times()
        }
        return patterns

    def predict_wait_time(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        预测等待时间

        Args:
            current_state: 当前状态

        Returns:
            预测结果
        """
        # 基于当前队列长度和历史数据预测
        current_queue = current_state.get('queueLength', 0)
        current_stage = current_state.get('currentStage', '')

        # 获取该阶段的平均处理时间
        avg_time = self.flow_patterns['average_flow_times'].get(current_stage, 15)

        predicted_wait = current_queue * avg_time

        return {
            'currentStage': current_stage,
            'queueLength': current_queue,
            'predictedWaitMinutes': predicted_wait,
            'confidence': 0.85,
            'suggestion': self._get_wait_suggestion(predicted_wait)
        }

    def _get_wait_suggestion(self, wait_minutes: float) -> str:
        """获取等待建议"""
        if wait_minutes < 15:
            return "预计等待时间较短，请耐心等候"
        elif wait_minutes < 30:
            return "预计等待时间约半小时，您可在候诊区休息"
        elif wait_minutes < 60:
            return "预计等待时间较长，建议您到周边休息，留意叫号"
        else:
            return "当前就诊人数较多，预计等待超过1小时，建议您改约其他时段"

    def optimize_appointment_scheduling(self, date: datetime) -> Dict[str, Any]:
        """
        优化预约排班

        Args:
            date: 目标日期

        Returns:
            优化建议
        """
        # 分析该日期的历史数据
        day_of_week = date.weekday()
        historical_volume = self._get_historical_volume(day_of_week)

        # 生成优化建议
        recommendations = {
            'recommendedSlotDistribution': self._calculate_optimal_slots(historical_volume),
            'staffingRecommendations': self._calculate_staffing_needs(historical_volume),
            'bufferSlots': max(5, int(historical_volume * 0.1)),  # 10%缓冲
            'expectedPeakHours': self.flow_patterns['peak_hours']
        }

        return recommendations

    def _calculate_optimal_slots(self, expected_volume: int) -> Dict[str, int]:
        """计算最优号源分配"""
        # 基础分配 + 动态调整
        base_distribution = {
            'morning': int(expected_volume * 0.5),
            'afternoon': int(expected_volume * 0.4),
            'evening': int(expected_volume * 0.1)
        }
        return base_distribution

    def _calculate_staffing_needs(self, expected_volume: int) -> Dict[str, int]:
        """计算人员需求"""
        # 根据预期患者量计算各岗位人员需求
        return {
            'doctors': max(5, int(expected_volume / 20)),  # 每位医生20个患者
            'nurses': max(3, int(expected_volume / 30)),
            'registration_staff': max(2, int(expected_volume / 50)),
            'pharmacy_staff': max(2, int(expected_volume / 40))
        }
```

### 2.2 住院患者流转

**住院患者流转流程**：

```
入院申请 → 床位分配 → 入院登记 → 医嘱管理 → 临床护理 → 出院评估 → 出院结算 → 出院随访
```

```python
class InpatientFlowConverter:
    """住院患者流转转换器"""

    def __init__(self):
        self.admission_stages = [
            'admission_request', 'bed_assignment', 'admission_registration',
            'initial_assessment', 'care_planning', 'daily_care', 'discharge_planning',
            'discharge_assessment', 'discharge_process', 'follow_up'
        ]

    def convert_admission(self, admission_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换入院流程

        Args:
            admission_request: 入院申请数据

        Returns:
            入院流转数据
        """
        admission_data = {
            'admissionId': self._generate_admission_id(),
            'patientId': admission_request.get('patientId'),
            'mrn': admission_request.get('mrn'),
            'requestTime': datetime.now(),
            'expectedAdmissionDate': admission_request.get('expectedDate'),
            'admissionType': admission_request.get('type', 'elective'),
            'admissionSource': admission_request.get('source', 'outpatient'),
            'referringPhysician': admission_request.get('referringPhysician'),
            'admittingDepartment': admission_request.get('department'),
            'requestedBedType': admission_request.get('bedType', 'standard'),
            'diagnosis': admission_request.get('diagnosis'),
            'specialNeeds': admission_request.get('specialNeeds', []),
            'stages': {},
            'currentStage': 'admission_request',
            'status': 'active',
            'lengthOfStay': {
                'expected': admission_request.get('expectedLOS', 5),
                'actual': None
            },
            'bed': None,
            'careTeam': [],
            'dailyCharges': [],
            'totalCharges': 0
        }

        # 初始化各阶段
        for stage in self.admission_stages:
            admission_data['stages'][stage] = {
                'status': 'pending',
                'startTime': None,
                'endTime': None,
                'duration': None,
                'data': {}
            }

        # 入院申请阶段完成
        admission_data['stages']['admission_request']['status'] = 'completed'
        admission_data['stages']['admission_request']['startTime'] = datetime.now()
        admission_data['stages']['admission_request']['endTime'] = datetime.now()

        return admission_data

    def assign_bed(self, admission_data: Dict[str, Any],
                   bed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分配床位

        Args:
            admission_data: 入院数据
            bed_info: 床位信息

        Returns:
            更新后的入院数据
        """
        # 更新床位信息
        admission_data['bed'] = {
            'bedId': bed_info.get('bedId'),
            'bedNumber': bed_info.get('bedNumber'),
            'ward': bed_info.get('ward'),
            'room': bed_info.get('room'),
            'bedType': bed_info.get('bedType'),
            'assignedAt': datetime.now(),
            'assignedBy': bed_info.get('assignedBy')
        }

        # 更新阶段状态
        self._complete_stage(admission_data, 'bed_assignment')
        self._start_stage(admission_data, 'admission_registration')

        return admission_data

    def complete_admission(self, admission_data: Dict[str, Any],
                          registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        完成入院登记

        Args:
            admission_data: 入院数据
            registration_data: 登记数据

        Returns:
            更新后的入院数据
        """
        # 更新入院信息
        admission_data['actualAdmissionDate'] = datetime.now()
        admission_data['admissionRegistration'] = registration_data

        # 完成入院登记阶段
        self._complete_stage(admission_data, 'admission_registration')
        self._start_stage(admission_data, 'initial_assessment')

        return admission_data

    def plan_discharge(self, admission_data: Dict[str, Any],
                      discharge_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        制定出院计划

        Args:
            admission_data: 入院数据
            discharge_plan: 出院计划

        Returns:
            更新后的入院数据
        """
        admission_data['dischargePlan'] = {
            'plannedDate': discharge_plan.get('plannedDate'),
            'disposition': discharge_plan.get('disposition', 'home'),
            'followUpRequired': discharge_plan.get('followUpRequired', False),
            'followUpAppointments': discharge_plan.get('followUpAppointments', []),
            'medications': discharge_plan.get('medications', []),
            'instructions': discharge_plan.get('instructions', ''),
            'homeCareNeeds': discharge_plan.get('homeCareNeeds', []),
            'equipmentNeeds': discharge_plan.get('equipmentNeeds', []),
            'createdAt': datetime.now(),
            'createdBy': discharge_plan.get('createdBy')
        }

        # 开始出院计划阶段
        self._start_stage(admission_data, 'discharge_planning')

        return admission_data

    def complete_discharge(self, admission_data: Dict[str, Any],
                          discharge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        完成出院

        Args:
            admission_data: 入院数据
            discharge_data: 出院数据

        Returns:
            更新后的入院数据
        """
        # 计算住院时长
        admission_date = admission_data.get('actualAdmissionDate')
        discharge_date = datetime.now()

        if admission_date:
            los_days = (discharge_date - admission_date).days
            los_hours = (discharge_date - admission_date).total_seconds() / 3600
            admission_data['lengthOfStay']['actual'] = {
                'days': los_days,
                'hours': los_hours
            }

        # 更新出院信息
        admission_data['discharge'] = {
            'dischargeDate': discharge_date,
            'dischargeDisposition': discharge_data.get('disposition'),
            'dischargeDiagnosis': discharge_data.get('diagnosis'),
            'dischargeCondition': discharge_data.get('condition'),
            'medications': discharge_data.get('medications', []),
            'followUpInstructions': discharge_data.get('followUpInstructions'),
            'dischargedBy': discharge_data.get('dischargedBy')
        }

        # 完成相关阶段
        self._complete_stage(admission_data, 'daily_care')
        self._complete_stage(admission_data, 'discharge_planning')
        self._complete_stage(admission_data, 'discharge_assessment')
        self._complete_stage(admission_data, 'discharge_process')

        admission_data['status'] = 'discharged'

        return admission_data

    def _complete_stage(self, admission_data: Dict[str, Any], stage: str):
        """完成阶段"""
        if stage in admission_data['stages']:
            stage_data = admission_data['stages'][stage]
            stage_data['status'] = 'completed'
            stage_data['endTime'] = datetime.now()
            if stage_data['startTime']:
                stage_data['duration'] = (
                    stage_data['endTime'] - stage_data['startTime']
                ).total_seconds() / 3600  # 小时

    def _start_stage(self, admission_data: Dict[str, Any], stage: str):
        """开始阶段"""
        if stage in admission_data['stages']:
            stage_data = admission_data['stages'][stage]
            stage_data['status'] = 'active'
            stage_data['startTime'] = datetime.now()
            admission_data['currentStage'] = stage

    def _generate_admission_id(self) -> str:
        """生成入院ID"""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"ADM{timestamp}{uuid.uuid4().hex[:6].upper()}"
```

### 2.3 急诊绿色通道

**急诊绿色通道Schema**：

```dsl
schema EmergencyGreenChannel {
  resourceType: String @value("EmergencyGreenChannel") @required

  // 患者信息
  patient: EmergencyPatient {
    patientId: String
    isUnknown: Boolean @default(false)
    tempId: String  // 无名氏临时ID
    estimatedAge: AgeRange
    estimatedGender: Enum { male, female, unknown }
    arrivedBy: Enum { ambulance, walk_in, transfer, police }
    ambulanceInfo: AmbulanceInfo {
      ambulanceId: String
      emsProvider: String
      cccReport: String
      vitalSignsEnRoute: List<VitalSign>
      interventions: List<String>
      eta: DateTime
    }
  }

  // 分诊信息
  triage: EmergencyTriage {
    triageId: String @required
    triageTime: DateTime @required
    triageNurse: Practitioner @required

    // 五级分诊
    acuityLevel: Enum { resuscitation, emergent, urgent, less_urgent, non_urgent } @required
    chiefComplaint: String @required
    presentingProblem: String @required

    // 生命体征
    vitalSigns: VitalSigns {
      temperature: Quantity
      heartRate: Quantity
      respiratoryRate: Quantity
      bloodPressure: BloodPressure
      spo2: Quantity
      painScore: Integer @min(0) @max(10)
      consciousness: Enum { alert, verbal, pain, unresponsive }
      glucose: Quantity
    }

    // 绿色通道指征
    greenChannelIndicators: List<GreenChannelIndicator> {
      indicatorType: Enum {
        stemi, stroke, trauma, severe_trauma,
        pregnancy_emergency, pediatric_emergency,
        severe_sepsis, acute_respiratory_failure
      }
      activationTime: DateTime
      activatedBy: Practitioner
      targetResponseTime: Integer  // 分钟
    }

    // 目标响应时间
    targetTime: TargetResponseTime {
      physicianAssessment: Integer  // STEMI: 10分钟
      ecg: Integer                  // STEMI: 10分钟
      labResults: Integer           // 60分钟
      imaging: Integer              // 30分钟
      intervention: Integer         // STEMI: 90分钟 (D2B)
    }
  }

  // 绿色通道执行
  execution: GreenChannelExecution {
    status: Enum { activated, in_progress, completed, cancelled }
    activatedAt: DateTime
    activatedBy: Practitioner

    // 时间节点
    milestones: List<Milestone> {
      milestoneType: Enum {
        door_time, triage_complete, physician_assessment,
        ecg_complete, lab_drawn, lab_reported,
        imaging_ordered, imaging_complete, imaging_reported,
        specialist_consult, intervention_start, intervention_complete,
        icu_admission, or_admission, ward_admission, discharge
      }
      scheduledTime: DateTime
      actualTime: DateTime
      variance: Integer  // 分钟
      responsiblePerson: Practitioner
    }

    // 质量控制
    qualityMetrics: QualityMetrics {
      doorToDoctor: Duration
      doorToEcg: Duration
      doorToNeedle: Duration  // 溶栓
      doorToBalloon: Duration  // PCI
      doorToCT: Duration  // 卒中
      doorToDrug: Duration  // 卒中溶栓
    }

    // 团队激活
    teamActivation: TeamActivation {
      teamType: Enum { code_stroke, code_stemi, trauma_team, sepsis_team }
      activatedAt: DateTime
      teamMembers: List<Practitioner>
      teamLeader: Practitioner
      responseTime: Duration
    }
  }

  // 患者去向
  disposition: EmergencyDisposition {
    dispositionType: Enum {
      discharge, admit_ward, admit_icu, admit_or,
      transfer, expired, left_ama, eloped
    }
    dispositionTime: DateTime
    dispositionLocation: Location

    // 住院信息
    admission: EmergencyAdmission {
      admissionId: String
      admittingService: String
      admittingPhysician: Practitioner
      bedAssigned: Bed
    }

    // 转院信息
    transfer: EmergencyTransfer {
      transferReason: String
      receivingFacility: String
      transportMode: Enum { ambulance, helicopter, fixed_wing }
      handoffComplete: Boolean
    }
  }
}
```

---

## 3. 资源优化转换

### 3.1 床位资源优化

**床位优化算法**：

```python
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

class BedResourceOptimizer:
    """床位资源优化器"""

    def __init__(self, bed_inventory: List[Dict], historical_occupancy: List[Dict]):
        self.bed_inventory = bed_inventory
        self.historical_occupancy = historical_occupancy
        self.optimization_model = self._build_optimization_model()

    def optimize_bed_allocation(self, forecast_demand: Dict[str, int],
                               constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化床位分配

        Args:
            forecast_demand: 预测需求 {ward_type: predicted_demand}
            constraints: 约束条件

        Returns:
            优化方案
        """
        # 分析当前床位状态
        current_status = self._analyze_current_status()

        # 计算床位缺口
        bed_gaps = self._calculate_bed_gaps(forecast_demand, current_status)

        # 生成优化策略
        optimization_plan = {
            'currentUtilization': current_status['utilization'],
            'forecastDemand': forecast_demand,
            'bedGaps': bed_gaps,
            'recommendations': self._generate_bed_recommendations(bed_gaps),
            'flexibleBedPlan': self._create_flexible_bed_plan(forecast_demand),
            'staffingRecommendations': self._calculate_staffing_needs(forecast_demand),
            'expectedOutcomes': {
                'projectedUtilization': None,
                'projectedWaitTime': None,
                'projectedTurnAwayRate': None
            }
        }

        return optimization_plan

    def _analyze_current_status(self) -> Dict[str, Any]:
        """分析当前床位状态"""
        total_beds = len(self.bed_inventory)
        occupied_beds = sum(1 for b in self.bed_inventory if b.get('status') == 'occupied')
        available_beds = total_beds - occupied_beds

        return {
            'totalBeds': total_beds,
            'occupiedBeds': occupied_beds,
            'availableBeds': available_beds,
            'utilization': occupied_beds / total_beds if total_beds > 0 else 0,
            'byWard': self._group_by_ward()
        }

    def _group_by_ward(self) -> Dict[str, Dict[str, int]]:
        """按病区分组统计"""
        ward_stats = {}
        for bed in self.bed_inventory:
            ward = bed.get('ward', 'unknown')
            if ward not in ward_stats:
                ward_stats[ward] = {'total': 0, 'occupied': 0, 'available': 0}

            ward_stats[ward]['total'] += 1
            if bed.get('status') == 'occupied':
                ward_stats[ward]['occupied'] += 1
            else:
                ward_stats[ward]['available'] += 1

        return ward_stats

    def _calculate_bed_gaps(self, forecast_demand: Dict[str, int],
                           current_status: Dict[str, Any]) -> Dict[str, int]:
        """计算床位缺口"""
        gaps = {}
        for ward_type, demand in forecast_demand.items():
            current_available = current_status['byWard'].get(ward_type, {}).get('available', 0)
            gap = demand - current_available
            gaps[ward_type] = max(0, gap)
        return gaps

    def _generate_bed_recommendations(self, bed_gaps: Dict[str, int]) -> List[Dict[str, Any]]:
        """生成床位优化建议"""
        recommendations = []

        for ward_type, gap in bed_gaps.items():
            if gap > 0:
                recommendations.append({
                    'type': 'capacity_expansion',
                    'wardType': ward_type,
                    'recommendedBeds': gap,
                    'priority': 'high' if gap > 5 else 'medium',
                    'timeline': 'immediate' if gap > 10 else 'short_term',
                    'estimatedCost': gap * 50000  // 每床位5万元估算
                })

        # 添加效率提升建议
        recommendations.append({
            'type': 'efficiency_improvement',
            'description': '优化出院流程，缩短平均住院日',
            'potentialBedDays': 50,
            'implementationEffort': 'medium'
        })

        recommendations.append({
            'type': 'flexible_beds',
            'description': '建立弹性床位池，应对需求波动',
            'flexibleBedCount': 10,
            'targetWards': ['general', 'observation']
        })

        return recommendations

    def _create_flexible_bed_plan(self, forecast_demand: Dict[str, int]) -> Dict[str, Any]:
        """创建弹性床位计划"""
        return {
            'flexibleBedPool': {
                'totalBeds': 10,
                'allocationStrategy': 'dynamic',
                'triggerThreshold': 0.9,  // 利用率超90%时激活
                'releaseThreshold': 0.7   // 利用率低于70%时释放
            },
            'surgeCapacity': {
                'maxSurgeBeds': 20,
                'activationCriteria': 'disaster_or_epidemic',
                'staffingPlan': 'on_call_activation'
            }
        }

    def predict_discharge_readiness(self, current_inpatients: List[Dict]) -> List[Dict]:
        """
        预测出院准备度

        Args:
            current_inpatients: 当前住院患者列表

        Returns:
            出院预测列表
        """
        predictions = []

        for patient in current_inpatients:
            # 基于临床指标预测出院时间
            predicted_los = self._predict_length_of_stay(patient)
            days_remaining = predicted_los - patient.get('currentLOS', 0)

            predictions.append({
                'patientId': patient.get('patientId'),
                'admissionId': patient.get('admissionId'),
                'currentLOS': patient.get('currentLOS'),
                'predictedTotalLOS': predicted_los,
                'predictedDischargeDate': datetime.now() + timedelta(days=days_remaining),
                'dischargeReadiness': self._assess_discharge_readiness(patient),
                'dischargeBarriers': self._identify_discharge_barriers(patient),
                'confidence': 0.8
            })

        return sorted(predictions, key=lambda x: x['predictedDischargeDate'])

    def _predict_length_of_stay(self, patient: Dict) -> float:
        """预测住院时长"""
        # 基于诊断、年龄、合并症等因素预测
        base_los = self._get_typical_los_for_diagnosis(patient.get('primaryDiagnosis'))

        # 调整因素
        age_factor = 1.0
        if patient.get('age', 50) > 75:
            age_factor = 1.3
        elif patient.get('age', 50) < 18:
            age_factor = 0.9

        comorbidity_factor = 1 + (len(patient.get('comorbidities', [])) * 0.1)

        return base_los * age_factor * comorbidity_factor

    def _get_typical_los_for_diagnosis(self, diagnosis: str) -> float:
        """获取诊断的典型住院时长"""
        typical_los = {
            'pneumonia': 5.5,
            'heart_failure': 4.2,
            'copd': 4.8,
            'mi': 3.5,
            'stroke': 6.2,
            'fracture': 4.0,
            'appendectomy': 2.5,
            'cholecystectomy': 3.0
        }
        return typical_los.get(diagnosis.lower(), 4.0)

    def _assess_discharge_readiness(self, patient: Dict) -> str:
        """评估出院准备度"""
        # 基于临床指标评估
        clinical_stability = patient.get('clinicalStability', 'unstable')
        discharge_plan_complete = patient.get('dischargePlanComplete', False)

        if clinical_stability == 'stable' and discharge_plan_complete:
            return 'ready'
        elif clinical_stability == 'stable':
            return 'likely_ready_24h'
        else:
            return 'not_ready'

    def _identify_discharge_barriers(self, patient: Dict) -> List[str]:
        """识别出院障碍"""
        barriers = []

        if not patient.get('dischargeDisposition'):
            barriers.append('未确定出院去向')

        if patient.get('pendingTests', []):
            barriers.append('有未完成检查')

        if patient.get('needsHomeCare') and not patient.get('homeCareArranged'):
            barriers.append('家庭护理未安排')

        if patient.get('needsEquipment') and not patient.get('equipmentArranged'):
            barriers.append('出院设备未安排')

        return barriers
```

### 3.2 手术室资源优化

```python
class ORResourceOptimizer:
    """手术室资源优化器"""

    def __init__(self, or_rooms: List[Dict], surgery_schedules: List[Dict]):
        self.or_rooms = or_rooms
        self.surgery_schedules = surgery_schedules

    def optimize_or_schedule(self, surgery_requests: List[Dict],
                            date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """
        优化手术室排程

        Args:
            surgery_requests: 手术申请列表
            date_range: 日期范围

        Returns:
            优化后的排程方案
        """
        # 按优先级和紧急程度排序
        sorted_requests = self._prioritize_surgeries(surgery_requests)

        # 分配手术室和时间
        schedule = self._assign_or_slots(sorted_requests, date_range)

        # 计算效率指标
        efficiency_metrics = self._calculate_efficiency(schedule)

        return {
            'schedule': schedule,
            'efficiencyMetrics': efficiency_metrics,
            'unscheduledCases': self._identify_unscheduled(sorted_requests, schedule),
            'optimizationSuggestions': self._generate_or_suggestions(efficiency_metrics)
        }

    def _prioritize_surgeries(self, requests: List[Dict]) -> List[Dict]:
        """手术优先级排序"""
        priority_order = {
            'emergent': 1,
            'urgent': 2,
            'elective': 3
        }

        return sorted(requests, key=lambda x: (
            priority_order.get(x.get('priority', 'elective'), 3),
            x.get('requestedDate', datetime.max)
        ))

    def _assign_or_slots(self, requests: List[Dict],
                        date_range: Tuple[datetime, datetime]) -> List[Dict]:
        """分配手术室时段"""
        schedule = []
        or_availability = self._initialize_or_availability(date_range)

        for request in requests:
            assigned = False

            # 查找可用时段
            for date in self._date_range(date_range[0], date_range[1]):
                if assigned:
                    break

                for or_room in self.or_rooms:
                    if self._can_accommodate(or_room, request, or_availability, date):
                        slot = self._create_slot(or_room, request, date)
                        schedule.append(slot)
                        self._update_availability(or_availability, slot)
                        assigned = True
                        break

            if not assigned:
                request['unscheduled'] = True

        return schedule

    def _calculate_efficiency(self, schedule: List[Dict]) -> Dict[str, float]:
        """计算效率指标"""
        total_scheduled_time = sum(
            s.get('estimatedDuration', 0) + s.get('turnover', 30)
            for s in schedule
        )

        available_time = len(self.or_rooms) * 8 * 60  // 8小时/天

        return {
            'roomUtilization': total_scheduled_time / available_time if available_time > 0 else 0,
            'firstCaseOnTime': 0.85,  // 首台准时率
            'turnoverTime': 28,  // 平均周转时间（分钟）
            'addOnRate': 0.15,  // 加台率
            'cancellationRate': 0.05  // 取消率
        }

    def predict_surgery_duration(self, surgery_type: str,
                                 patient_factors: Dict) -> Dict[str, float]:
        """
        预测手术时长

        Args:
            surgery_type: 手术类型
            patient_factors: 患者因素

        Returns:
            时长预测
        """
        # 基于历史数据和患者因素预测
        base_duration = self._get_base_duration(surgery_type)

        # 调整因素
        bmi_factor = 1.0
        if patient_factors.get('bmi', 25) > 35:
            bmi_factor = 1.2

        age_factor = 1.0
        if patient_factors.get('age', 50) > 75:
            age_factor = 1.1

        asa_factor = 1.0 + (patient_factors.get('asa', 2) - 2) * 0.1

        adjusted_duration = base_duration * bmi_factor * age_factor * asa_factor

        return {
            'predictedDuration': adjusted_duration,
            'confidenceInterval': (adjusted_duration * 0.8, adjusted_duration * 1.2),
            'confidence': 0.85
        }
```

### 3.3 人力资源优化

```python
class StaffingOptimizer:
    """人力资源优化器"""

    def __init__(self, staff_pool: List[Dict], demand_forecast: Dict):
        self.staff_pool = staff_pool
        self.demand_forecast = demand_forecast

    def optimize_staffing(self, department: str,
                         date: datetime) -> Dict[str, Any]:
        """
        优化排班人员配置

        Args:
            department: 科室
            date: 日期

        Returns:
            优化方案
        """
        # 预测需求量
        predicted_demand = self.demand_forecast.get(department, {}).get(date, {})

        # 计算人员需求
        staffing_requirements = self._calculate_requirements(
            department, predicted_demand
        )

        # 匹配可用人员
        available_staff = self._get_available_staff(department, date)

        # 生成排班方案
        schedule = self._generate_optimal_schedule(
            staffing_requirements, available_staff
        )

        return {
            'date': date,
            'department': department,
            'predictedDemand': predicted_demand,
            'staffingRequirements': staffing_requirements,
            'proposedSchedule': schedule,
            'coverageAnalysis': self._analyze_coverage(schedule, staffing_requirements),
            'costEstimate': self._estimate_cost(schedule)
        }

    def _calculate_requirements(self, department: str,
                               predicted_demand: Dict) -> Dict[str, int]:
        """计算人员需求"""
        # 基于患者量和复杂度计算
        patient_count = predicted_demand.get('patientCount', 0)
        acuity_level = predicted_demand.get('averageAcuity', 1)

        # 护士配比计算（基于患者严重程度和数量）
        if department in ['ICU', 'CCU']:
            nurse_ratio = 1  // 1:1或1:2
            nurses_needed = max(4, int(patient_count * 0.6))
        elif department in ['ER']:
            nurse_ratio = 4
            nurses_needed = max(6, int(patient_count / nurse_ratio))
        else:
            nurse_ratio = 6
            nurses_needed = max(3, int(patient_count / nurse_ratio * acuity_level))

        return {
            'nurses': nurses_needed,
            'doctors': max(2, int(nurses_needed / 3)),
            'technicians': max(1, int(nurses_needed / 4)),
            'supportStaff': max(1, int(nurses_needed / 5))
        }
```

---

## 4. 跨系统数据交换

### 4.1 HIS与EMR集成

**HIS-EMR集成架构**：

```python
class HISEMRIntegration:
    """HIS与EMR系统集成"""

    def __init__(self, his_connector, emr_connector):
        self.his = his_connector
        self.emr = emr_connector
        self.sync_mapping = self._load_sync_mapping()

    def sync_patient_data(self, patient_id: str, sync_type: str = 'bidirectional') -> bool:
        """
        同步患者数据

        Args:
            patient_id: 患者ID
            sync_type: 同步类型 (his_to_emr, emr_to_his, bidirectional)

        Returns:
            是否成功
        """
        try:
            if sync_type in ['his_to_emr', 'bidirectional']:
                # 从HIS获取患者基础信息
                his_patient = self.his.get_patient(patient_id)
                # 转换并更新到EMR
                emr_patient = self._convert_his_to_emr_patient(his_patient)
                self.emr.update_patient(emr_patient)

            if sync_type in ['emr_to_his', 'bidirectional']:
                # 从EMR获取临床信息
                emr_clinical = self.emr.get_clinical_data(patient_id)
                # 更新到HIS
                his_updates = self._convert_emr_to_his_clinical(emr_clinical)
                self.his.update_patient_clinical(patient_id, his_updates)

            return True
        except Exception as e:
            logger.error(f"Patient sync failed: {e}")
            return False

    def sync_admission_data(self, admission_id: str) -> bool:
        """同步入院数据"""
        try:
            # 从HIS获取入院信息
            his_admission = self.his.get_admission(admission_id)

            # 转换并创建EMR入院记录
            emr_encounter = self._convert_his_admission_to_emr(his_admission)
            self.emr.create_encounter(emr_encounter)

            # 同步床位信息
            bed_info = his_admission.get('bed')
            if bed_info:
                self.emr.update_patient_location(
                    his_admission['patientId'],
                    bed_info
                )

            return True
        except Exception as e:
            logger.error(f"Admission sync failed: {e}")
            return False

    def sync_financial_data(self, encounter_id: str) -> bool:
        """同步财务数据"""
        try:
            # 从HIS获取收费信息
            charges = self.his.get_encounter_charges(encounter_id)

            # 转换并更新到EMR（用于临床成本分析）
            emr_charges = self._convert_his_charges_to_emr(charges)
            self.emr.add_encounter_charges(encounter_id, emr_charges)

            return True
        except Exception as e:
            logger.error(f"Financial sync failed: {e}")
            return False

    def _convert_his_to_emr_patient(self, his_patient: Dict) -> Dict:
        """转换HIS患者数据到EMR格式"""
        return {
            'resourceType': 'Patient',
            'id': his_patient.get('patientId'),
            'identifier': [{
                'system': 'http://hospital.org/mrn',
                'value': his_patient.get('mrn')
            }],
            'name': [{
                'family': his_patient.get('lastName'),
                'given': [his_patient.get('firstName')]
            }],
            'gender': his_patient.get('gender'),
            'birthDate': his_patient.get('birthDate'),
            'address': self._convert_address(his_patient.get('address')),
            'telecom': self._convert_telecom(his_patient.get('contact'))
        }
```

### 4.2 与区域平台对接

```python
class RegionalPlatformIntegration:
    """区域卫生信息平台集成"""

    def __init__(self, platform_config: Dict[str, str]):
        self.platform_url = platform_config.get('url')
        self.api_key = platform_config.get('api_key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def upload_patient_summary(self, patient_id: str) -> bool:
        """
        上传患者病历摘要到区域平台

        Args:
            patient_id: 患者ID

        Returns:
            是否成功
        """
        try:
            # 获取患者摘要
            summary = self._generate_patient_summary(patient_id)

            # 转换为区域平台标准格式
            platform_format = self._convert_to_platform_format(summary)

            # 上传
            response = requests.post(
                f"{self.platform_url}/api/v1/patient/summary",
                headers=self.headers,
                json=platform_format
            )

            return response.status_code == 200
        except Exception as e:
            logger.error(f"Upload to regional platform failed: {e}")
            return False

    def query_regional_records(self, patient_id: str,
                               id_type: str = 'id_card') -> List[Dict]:
        """
        查询患者在区域平台的记录

        Args:
            patient_id: 患者标识
            id_type: 标识类型

        Returns:
            区域医疗记录列表
        """
        try:
            response = requests.get(
                f"{self.platform_url}/api/v1/patient/records",
                headers=self.headers,
                params={
                    'patientId': patient_id,
                    'idType': id_type
                }
            )

            if response.status_code == 200:
                records = response.json()
                # 转换为本地格式
                return [self._convert_from_platform_format(r) for r in records]

            return []
        except Exception as e:
            logger.error(f"Query regional records failed: {e}")
            return []
```

---

## 5. 业务流程优化

**业务流程优化框架**：

```python
class BusinessProcessOptimizer:
    """业务流程优化器"""

    def analyze_process(self, process_name: str,
                       process_data: List[Dict]) -> Dict[str, Any]:
        """
        分析业务流程

        Args:
            process_name: 流程名称
            process_data: 流程执行数据

        Returns:
            分析报告
        """
        analysis = {
            'processName': process_name,
            'analysisDate': datetime.now(),
            'totalExecutions': len(process_data),
            'averageDuration': self._calculate_average_duration(process_data),
            'bottlenecks': self._identify_bottlenecks(process_data),
            'variability': self._calculate_variability(process_data),
            'defects': self._identify_defects(process_data),
            'recommendations': []
        }

        # 生成优化建议
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def optimize_registration_process(self) -> Dict[str, Any]:
        """优化挂号流程"""
        return {
            'currentSteps': 8,
            'optimizedSteps': 4,
            'improvements': [
                '引入自助挂号机，减少排队',
                '推广移动支付，减少现金窗口',
                '实施预约优先制，错峰就诊',
                '诊间结算，减少二次排队'
            ],
            'expectedBenefits': {
                'waitTimeReduction': '40%',
                'patientSatisfactionIncrease': '25%',
                'staffEfficiencyImprovement': '30%'
            }
        }
```

---

## 6. 性能监控与优化

**系统性能监控**：

```python
class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {}

    def record_metric(self, metric_name: str, value: float,
                     tags: Dict[str, str] = None):
        """记录指标"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append({
            'timestamp': datetime.now(),
            'value': value,
            'tags': tags or {}
        })

    def get_performance_dashboard(self) -> Dict[str, Any]:
        """获取性能仪表板数据"""
        return {
            'systemMetrics': {
                'responseTime': self._get_avg_response_time(),
                'throughput': self._get_throughput(),
                'errorRate': self._get_error_rate(),
                'availability': self._get_availability()
            },
            'businessMetrics': {
                'patientFlow': self._get_patient_flow_metrics(),
                'resourceUtilization': self._get_resource_utilization(),
                'serviceLevel': self._get_service_level_metrics()
            }
        }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标

**创建时间**：2025-02-15
**最后更新**：2025-02-15
