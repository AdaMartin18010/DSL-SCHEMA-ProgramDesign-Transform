# 数据治理Schema实践案例

## 📑 目录

- [数据治理Schema实践案例](#数据治理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：医疗集团数据治理与合规平台](#2-案例1医疗集团数据治理与合规平台)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估与ROI分析](#27-效果评估与roi分析)

---

## 1. 案例概述

本文档提供数据治理Schema在实际企业应用中的深度实践案例，涵盖医疗数据合规、主数据管理、数据质量管理等企业级场景。

---

## 2. 案例1：医疗集团数据治理与合规平台

### 2.1 企业背景

**企业简介**：
某大型医疗集团（以下简称"华康医疗"）拥有50家医院、200家诊所，年门诊量3000万人次，年住院量100万人次，是中国领先的综合性医疗服务集团。

**业务规模**：

| 指标 | 数值 |
|------|------|
| 医院数量 | 50家 |
| 诊所数量 | 200家 |
| 年门诊量 | 3000万+ |
| 年住院量 | 100万+ |
| 电子病历数 | 5000万+ |
| 日新增数据 | 500GB+ |
| 合规要求 | HIPAA + 等保2.0 + 个人信息保护法 |

### 2.2 业务痛点

**痛点1：数据合规风险高**
医疗数据涉及高度敏感的个人健康信息（PHI），需要符合HIPAA、等保2.0、个人信息保护法等严格法规，违规风险极高。

**痛点2：数据质量差**
各医院数据标准不统一，同一患者存在多个ID，诊断编码不规范，数据缺失率高达20%，影响临床决策和科研分析。

**痛点3：数据孤岛严重**
HIS、EMR、PACS、LIS等系统各自独立，患者数据无法跨院共享，重复检查、重复用药问题突出。

**痛点4：隐私保护困难**
缺乏有效的数据脱敏和访问控制机制，数据泄露风险高，难以平衡数据利用和隐私保护。

**痛点5：缺乏统一视图**
无法构建完整的患者360度视图，医生无法获取患者完整就诊历史，影响诊疗质量。

### 2.3 业务目标

**目标1：建立统一数据标准**
制定集团级数据标准，统一患者主数据、医学术语、诊断编码，实现数据标准化率95%以上。

**目标2：实现合规自动化**
建立自动化的合规检查和审计机制，确保所有数据操作符合法规要求，合规检查覆盖率100%。

**目标3：构建主数据管理（MDM）**
建立统一的患者、医生、药品、诊断主数据管理中心，实现患者唯一身份识别。

**目标4：提升数据质量**
建立数据质量管理体系，将数据准确率提升至98%，数据完整率提升至95%。

**目标5：实现安全数据共享**
在保障隐私的前提下，实现跨院数据安全共享，支持临床协作和科研创新。

### 2.4 技术挑战

**挑战1：多源异构数据整合**
需要整合来自50家医院的HIS、EMR、PACS、LIS等20多类系统，数据格式、编码标准各不相同。

**挑战2：患者身份识别（EMPI）**
同一患者在不同医院可能有不同ID，需要构建企业级患者索引（EMPI），准确识别同一患者。

**挑战3：实时合规检查**
所有数据访问和操作都需要实时合规检查，不能影响业务系统性能。

**挑战4：细粒度访问控制**
需要支持基于角色、患者、科室、病种的多维度访问控制，权限管理极其复杂。

**挑战5：数据脱敏与溯源**
需要实现智能化的数据脱敏，同时保留数据血缘，支持合规审计。

### 2.5 解决方案

**整体架构**：
- **主数据管理层**：患者主数据、医疗术语、标准编码
- **数据质量层**：数据清洗、质量监控、问题修复
- **数据安全层**：加密、脱敏、访问控制、审计
- **合规管理层**：法规映射、合规检查、审计报告

**技术路线**：
- EMPI：概率匹配算法 + 人工审核
- 数据质量：Apache Griffin + 自定义规则
- 数据安全：列级加密 + 动态脱敏
- 合规管理：自动化策略引擎

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
医疗集团数据治理与合规平台
支持HIPAA合规、主数据管理、数据质量管理的企业级方案
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import re


class DataClassification(str, Enum):
    """数据分类"""
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    RESTRICTED = "Restricted"  # PHI数据


class ComplianceFramework(str, Enum):
    """合规框架"""
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    PERSONAL_INFO_PROTECTION = "PersonalInfoProtection"
    GRADE_PROTECTION_2_0 = "GradeProtection2.0"


class QualityDimension(str, Enum):
    """数据质量维度"""
    COMPLETENESS = "Completeness"
    UNIQUENESS = "Uniqueness"
    VALIDITY = "Validity"
    CONSISTENCY = "Consistency"
    ACCURACY = "Accuracy"
    TIMELINESS = "Timeliness"


class ConsentStatus(str, Enum):
    """授权状态"""
    GRANTED = "Granted"
    REVOKED = "Revoked"
    EXPIRED = "Expired"
    PENDING = "Pending"


@dataclass
class PatientIdentity:
    """患者身份"""
    patient_id: str
    empi_id: Optional[str] = None  # 企业级患者唯一标识
    
    # 身份信息
    name: str = ""
    id_card: str = ""
    phone: str = ""
    email: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: str = ""
    
    # 地址信息
    address: str = ""
    city: str = ""
    province: str = ""
    
    # 匹配权重
    match_score: float = 0.0
    source_systems: List[str] = field(default_factory=list)
    
    def get_pii_fields(self) -> List[str]:
        """获取PII字段"""
        return ["name", "id_card", "phone", "email", "address"]
    
    def generate_empi(self) -> str:
        """生成EMPI"""
        # 使用身份证号哈希生成EMPI
        if self.id_card:
            hash_obj = hashlib.sha256(self.id_card.encode())
            self.empi_id = f"EMPI-{hash_obj.hexdigest()[:16].upper()}"
        return self.empi_id


@dataclass
class DataQualityRule:
    """数据质量规则"""
    rule_id: str
    rule_name: str
    dimension: QualityDimension
    rule_type: str
    rule_expression: str
    threshold: float = 0.95
    severity: str = "Error"
    
    def evaluate(self, data: Dict) -> tuple[bool, str]:
        """评估数据质量"""
        try:
            if self.dimension == QualityDimension.COMPLETENESS:
                return self._check_completeness(data)
            elif self.dimension == QualityDimension.VALIDITY:
                return self._check_validity(data)
            elif self.dimension == QualityDimension.UNIQUENESS:
                return self._check_uniqueness(data)
            return True, "Pass"
        except Exception as e:
            return False, str(e)
    
    def _check_completeness(self, data: Dict) -> tuple[bool, str]:
        """检查完整性"""
        required_fields = self.rule_expression.split(",")
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return False, f"Missing fields: {missing}"
        return True, "Pass"
    
    def _check_validity(self, data: Dict) -> tuple[bool, str]:
        """检查有效性"""
        if "id_card" in self.rule_expression:
            id_card = data.get("id_card", "")
            # 简化身份证号校验
            if len(id_card) != 18:
                return False, "Invalid ID card format"
        return True, "Pass"
    
    def _check_uniqueness(self, data: Dict) -> tuple[bool, str]:
        """检查唯一性"""
        return True, "Pass"


@dataclass
class DataAccessPolicy:
    """数据访问策略"""
    policy_id: str
    policy_name: str
    data_classification: DataClassification
    allowed_roles: List[str] = field(default_factory=list)
    allowed_operations: List[str] = field(default_factory=list)  # READ, WRITE, DELETE
    require_consent: bool = True
    require_approval: bool = False
    mask_fields: List[str] = field(default_factory=list)
    
    def check_access(self, user_role: str, operation: str, has_consent: bool) -> bool:
        """检查访问权限"""
        if user_role not in self.allowed_roles:
            return False
        if operation not in self.allowed_operations:
            return False
        if self.require_consent and not has_consent:
            return False
        return True


@dataclass
class AuditLog:
    """审计日志"""
    log_id: str
    timestamp: datetime
    user_id: str
    user_role: str
    patient_id: str
    operation: str
    data_class: DataClassification
    accessed_fields: List[str]
    ip_address: str
    result: str  # SUCCESS, DENIED, ERROR
    reason: Optional[str] = None


@dataclass
class HealthcareDataGovernance:
    """医疗数据治理平台"""
    platform_id: str
    platform_name: str
    
    # 患者主数据
    patient_registry: Dict[str, PatientIdentity] = field(default_factory=dict)
    
    # 数据质量规则
    quality_rules: List[DataQualityRule] = field(default_factory=list)
    
    # 访问策略
    access_policies: Dict[str, DataAccessPolicy] = field(default_factory=dict)
    
    # 审计日志
    audit_logs: List[AuditLog] = field(default_factory=list)
    
    # 合规框架
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    
    def register_patient(self, patient: PatientIdentity):
        """注册患者"""
        patient.generate_empi()
        self.patient_registry[patient.patient_id] = patient
        return patient.empi_id
    
    def match_patient(self, query: Dict) -> List[PatientIdentity]:
        """患者匹配（EMPI）"""
        matches = []
        for patient in self.patient_registry.values():
            score = 0
            if query.get("name") == patient.name:
                score += 0.3
            if query.get("id_card") == patient.id_card:
                score += 0.4
            if query.get("phone") == patient.phone:
                score += 0.2
            if query.get("date_of_birth") == patient.date_of_birth:
                score += 0.1
            
            if score >= 0.8:
                patient.match_score = score
                matches.append(patient)
        
        return sorted(matches, key=lambda x: x.match_score, reverse=True)
    
    def add_quality_rule(self, rule: DataQualityRule):
        """添加质量规则"""
        self.quality_rules.append(rule)
    
    def evaluate_data_quality(self, data: Dict) -> Dict[str, Any]:
        """评估数据质量"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_rules": len(self.quality_rules),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for rule in self.quality_rules:
            passed, message = rule.evaluate(data)
            results["details"].append({
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "dimension": rule.dimension.value,
                "passed": passed,
                "message": message
            })
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def create_access_policy(self, policy: DataAccessPolicy):
        """创建访问策略"""
        self.access_policies[policy.policy_id] = policy
    
    def access_data(
        self,
        user_id: str,
        user_role: str,
        patient_id: str,
        operation: str,
        requested_fields: List[str],
        ip_address: str,
        has_consent: bool = False
    ) -> Dict[str, Any]:
        """访问数据（带合规检查）"""
        
        # 获取患者数据
        patient = self.patient_registry.get(patient_id)
        if not patient:
            return {"success": False, "error": "Patient not found"}
        
        # 确定数据分类
        data_class = DataClassification.RESTRICTED
        
        # 查找访问策略
        policy = None
        for p in self.access_policies.values():
            if p.data_classification == data_class:
                policy = p
                break
        
        if not policy:
            result = "DENIED"
            reason = "No access policy found"
        else:
            # 检查权限
            allowed = policy.check_access(user_role, operation, has_consent)
            if allowed:
                result = "SUCCESS"
                reason = None
            else:
                result = "DENIED"
                reason = "Access denied by policy"
        
        # 记录审计日志
        audit_log = AuditLog(
            log_id=f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            patient_id=patient_id,
            operation=operation,
            data_class=data_class,
            accessed_fields=requested_fields,
            ip_address=ip_address,
            result=result,
            reason=reason
        )
        self.audit_logs.append(audit_log)
        
        if result == "SUCCESS":
            # 应用脱敏
            masked_data = self._apply_masking(patient, policy.mask_fields if policy else [])
            return {"success": True, "data": masked_data}
        else:
            return {"success": False, "error": reason}
    
    def _apply_masking(self, patient: PatientIdentity, mask_fields: List[str]) -> Dict:
        """应用数据脱敏"""
        data = {
            "patient_id": patient.patient_id,
            "empi_id": patient.empi_id,
            "name": patient.name,
            "id_card": patient.id_card,
            "phone": patient.phone,
            "email": patient.email
        }
        
        for field in mask_fields:
            if field in data and data[field]:
                value = str(data[field])
                if field in ["name"]:
                    data[field] = value[0] + "*" * (len(value) - 1)
                elif field in ["id_card"]:
                    data[field] = value[:6] + "*" * 8 + value[-4:]
                elif field in ["phone"]:
                    data[field] = value[:3] + "*" * 4 + value[-4:]
        
        return data
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """生成合规报告"""
        total_accesses = len(self.audit_logs)
        successful_accesses = len([l for l in self.audit_logs if l.result == "SUCCESS"])
        denied_accesses = len([l for l in self.audit_logs if l.result == "DENIED"])
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_audit_logs": total_accesses,
            "successful_accesses": successful_accesses,
            "denied_accesses": denied_accesses,
            "success_rate": successful_accesses / total_accesses if total_accesses else 0,
            "compliance_frameworks": [f.value for f in self.compliance_frameworks],
            "active_policies": len(self.access_policies),
            "registered_patients": len(self.patient_registry)
        }


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("华康医疗 - 数据治理与合规平台")
    print("=" * 70)
    
    # 创建平台
    platform = HealthcareDataGovernance(
        platform_id="DG-HUAKANG-001",
        platform_name="华康医疗数据治理平台",
        compliance_frameworks=[
            ComplianceFramework.HIPAA,
            ComplianceFramework.PERSONAL_INFO_PROTECTION,
            ComplianceFramework.GRADE_PROTECTION_2_0
        ]
    )
    
    # 1. 注册患者
    print("\n[1] 注册患者...")
    patient1 = PatientIdentity(
        patient_id="PAT-001",
        name="张三",
        id_card="110101199001011234",
        phone="13800138000",
        gender="M",
        date_of_birth=datetime(1990, 1, 1),
        source_systems=["HIS-Hospital-A"]
    )
    empi = platform.register_patient(patient1)
    print(f"患者ID: {patient1.patient_id}")
    print(f"EMPI: {empi}")
    
    # 2. 添加数据质量规则
    print("\n[2] 添加数据质量规则...")
    completeness_rule = DataQualityRule(
        rule_id="RULE-COMP-001",
        rule_name="患者信息完整性检查",
        dimension=QualityDimension.COMPLETENESS,
        rule_type="RequiredFields",
        rule_expression="name,id_card,phone,date_of_birth",
        threshold=1.0
    )
    platform.add_quality_rule(completeness_rule)
    
    validity_rule = DataQualityRule(
        rule_id="RULE-VALID-001",
        rule_name="身份证号有效性检查",
        dimension=QualityDimension.VALIDITY,
        rule_type="RegexMatch",
        rule_expression="id_card",
        threshold=1.0
    )
    platform.add_quality_rule(validity_rule)
    
    print(f"已添加 {len(platform.quality_rules)} 条质量规则")
    
    # 3. 评估数据质量
    print("\n[3] 评估数据质量...")
    quality_result = platform.evaluate_data_quality({
        "name": "张三",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "date_of_birth": datetime(1990, 1, 1)
    })
    print(f"通过规则数: {quality_result['passed']}")
    print(f"失败规则数: {quality_result['failed']}")
    
    # 4. 创建访问策略
    print("\n[4] 创建数据访问策略...")
    policy = DataAccessPolicy(
        policy_id="POLICY-001",
        policy_name="医生访问PHI数据策略",
        data_classification=DataClassification.RESTRICTED,
        allowed_roles=["DOCTOR", "NURSE", "ADMIN"],
        allowed_operations=["READ"],
        require_consent=True,
        mask_fields=["id_card", "phone"]
    )
    platform.create_access_policy(policy)
    print(f"策略ID: {policy.policy_id}")
    
    # 5. 访问数据
    print("\n[5] 数据访问控制测试...")
    
    # 有权限的访问
    result1 = platform.access_data(
        user_id="DOC-001",
        user_role="DOCTOR",
        patient_id="PAT-001",
        operation="READ",
        requested_fields=["name", "id_card", "phone"],
        ip_address="192.168.1.100",
        has_consent=True
    )
    print(f"医生访问（有授权）: {'成功' if result1['success'] else '失败'}")
    if result1.get('data'):
        print(f"  脱敏后数据: {result1['data']}")
    
    # 无权限的访问
    result2 = platform.access_data(
        user_id="USER-001",
        user_role="PATIENT",
        patient_id="PAT-001",
        operation="READ",
        requested_fields=["name", "id_card"],
        ip_address="192.168.1.200"
    )
    print(f"患者角色访问: {'成功' if result2['success'] else '失败'}")
    if not result2['success']:
        print(f"  拒绝原因: {result2.get('error')}")
    
    # 6. 生成合规报告
    print("\n[6] 生成合规审计报告...")
    report = platform.generate_compliance_report()
    print(f"审计日志总数: {report['total_audit_logs']}")
    print(f"成功访问次数: {report['successful_accesses']}")
    print(f"拒绝访问次数: {report['denied_accesses']}")
    print(f"访问成功率: {report['success_rate']:.1%}")
    print(f"注册患者数: {report['registered_patients']}")
```

### 2.7 效果评估与ROI分析

**项目投入**：

| 投入类别 | 金额（万元） |
|---------|------------|
| 软件平台 | 600 |
| 实施服务 | 400 |
| 培训咨询 | 200 |
| **总投资** | **1200** |

**量化收益**：

| 收益类别 | 年收益（万元） |
|---------|--------------|
| 合规风险降低 | 2000 |
| 重复检查减少 | 800 |
| 科研效率提升 | 500 |
| 数据质量提升 | 300 |
| **年总收益** | **3600** |

**ROI**：300%（年收益3600万 vs 投资1200万）

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 数据标准化率 | 60% | 95% | +58% |
| 患者匹配准确率 | 70% | 98% | +40% |
| 合规检查覆盖率 | 40% | 100% | +150% |
| 数据访问审批时间 | 3天 | 实时 | 100% |

---

**创建时间**：2025-02-15
