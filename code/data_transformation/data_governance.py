"""
数据治理模块

专注于数据治理规则、数据策略、合规性检查
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GovernanceRuleType(Enum):
    """治理规则类型"""
    ACCESS_CONTROL = "access_control"  # 访问控制
    DATA_CLASSIFICATION = "data_classification"  # 数据分类
    RETENTION = "retention"  # 数据保留
    PRIVACY = "privacy"  # 隐私保护
    COMPLIANCE = "compliance"  # 合规性
    QUALITY = "quality"  # 质量要求


class ComplianceLevel(Enum):
    """合规级别"""
    COMPLIANT = "compliant"  # 合规
    NON_COMPLIANT = "non_compliant"  # 不合规
    WARNING = "warning"  # 警告
    UNKNOWN = "unknown"  # 未知


@dataclass
class GovernanceRule:
    """治理规则"""
    rule_id: str
    name: str
    rule_type: GovernanceRuleType
    rule_config: Dict[str, Any]
    enabled: bool = True
    priority: int = 0


@dataclass
class ComplianceResult:
    """合规性结果"""
    rule_id: str
    compliance_level: ComplianceLevel
    message: str
    violations: List[Dict[str, Any]] = None
    checked_at: datetime = None


class DataGovernance:
    """
    数据治理器
    
    专注于数据治理规则、数据策略、合规性检查
    """
    
    def __init__(self):
        self.rules: Dict[str, GovernanceRule] = {}
        self.compliance_results: Dict[str, List[ComplianceResult]] = {}
    
    def add_rule(self, rule_config: Dict[str, Any]) -> GovernanceRule:
        """
        添加治理规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            治理规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = GovernanceRule(
            rule_id=rule_id,
            name=rule_config.get('name', ''),
            rule_type=GovernanceRuleType(rule_config.get('rule_type', 'access_control')),
            rule_config=rule_config.get('rule_config', {}),
            enabled=rule_config.get('enabled', True),
            priority=rule_config.get('priority', 0)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def check_compliance(self, data: Dict[str, Any],
                        rule_ids: Optional[List[str]] = None) -> List[ComplianceResult]:
        """
        检查合规性
        
        Args:
            data: 数据
            rule_ids: 规则ID列表（可选，默认检查所有规则）
            
        Returns:
            合规性结果列表
        """
        results = []
        
        # 确定要检查的规则
        rules_to_check = rule_ids if rule_ids else [r.rule_id for r in self.rules.values() if r.enabled]
        
        # 按优先级排序
        rules_to_check.sort(key=lambda rid: self.rules[rid].priority, reverse=True)
        
        for rule_id in rules_to_check:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            
            if not rule.enabled:
                continue
            
            # 执行合规性检查
            result = self._check_rule_compliance(data, rule)
            results.append(result)
            
            # 记录结果
            if rule_id not in self.compliance_results:
                self.compliance_results[rule_id] = []
            self.compliance_results[rule_id].append(result)
        
        return results
    
    def _check_rule_compliance(self, data: Dict[str, Any], rule: GovernanceRule) -> ComplianceResult:
        """检查规则合规性"""
        rule_type = rule.rule_type
        config = rule.rule_config
        violations = []
        
        if rule_type == GovernanceRuleType.ACCESS_CONTROL:
            # 访问控制检查
            required_permissions = config.get('required_permissions', [])
            user_permissions = data.get('permissions', [])
            
            missing_permissions = [p for p in required_permissions if p not in user_permissions]
            if missing_permissions:
                violations.append({
                    'type': 'missing_permissions',
                    'details': missing_permissions
                })
        
        elif rule_type == GovernanceRuleType.DATA_CLASSIFICATION:
            # 数据分类检查
            required_classification = config.get('classification')
            data_classification = data.get('classification')
            
            if data_classification != required_classification:
                violations.append({
                    'type': 'classification_mismatch',
                    'expected': required_classification,
                    'actual': data_classification
                })
        
        elif rule_type == GovernanceRuleType.RETENTION:
            # 数据保留检查
            max_retention_days = config.get('max_retention_days')
            created_at = data.get('created_at')
            
            if created_at and max_retention_days:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                
                age_days = (datetime.utcnow() - created_at).days
                if age_days > max_retention_days:
                    violations.append({
                        'type': 'retention_exceeded',
                        'age_days': age_days,
                        'max_days': max_retention_days
                    })
        
        elif rule_type == GovernanceRuleType.PRIVACY:
            # 隐私保护检查
            sensitive_fields = config.get('sensitive_fields', [])
            exposed_fields = [f for f in sensitive_fields if f in data and data[f] is not None]
            
            if exposed_fields:
                violations.append({
                    'type': 'sensitive_data_exposed',
                    'fields': exposed_fields
                })
        
        elif rule_type == GovernanceRuleType.COMPLIANCE:
            # 合规性检查
            compliance_check = config.get('check')
            if compliance_check and callable(compliance_check):
                try:
                    is_compliant = compliance_check(data)
                    if not is_compliant:
                        violations.append({
                            'type': 'compliance_violation',
                            'details': config.get('violation_message', '合规性检查失败')
                        })
                except Exception as e:
                    violations.append({
                        'type': 'compliance_check_error',
                        'error': str(e)
                    })
        
        elif rule_type == GovernanceRuleType.QUALITY:
            # 质量要求检查
            quality_rules = config.get('quality_rules', [])
            for quality_rule in quality_rules:
                field = quality_rule.get('field')
                threshold = quality_rule.get('threshold')
                
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)) and value < threshold:
                        violations.append({
                            'type': 'quality_threshold_not_met',
                            'field': field,
                            'value': value,
                            'threshold': threshold
                        })
        
        # 确定合规级别
        if len(violations) == 0:
            compliance_level = ComplianceLevel.COMPLIANT
            message = f"规则 {rule.name} 合规"
        elif len(violations) <= 1:
            compliance_level = ComplianceLevel.WARNING
            message = f"规则 {rule.name} 有警告"
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
            message = f"规则 {rule.name} 不合规"
        
        return ComplianceResult(
            rule_id=rule.rule_id,
            compliance_level=compliance_level,
            message=message,
            violations=violations,
            checked_at=datetime.utcnow()
        )
    
    def get_compliance_summary(self, rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取合规性摘要
        
        Args:
            rule_ids: 规则ID列表（可选）
            
        Returns:
            合规性摘要
        """
        if rule_ids:
            results = []
            for rule_id in rule_ids:
                if rule_id in self.compliance_results:
                    results.extend(self.compliance_results[rule_id])
        else:
            results = []
            for rule_results in self.compliance_results.values():
                results.extend(rule_results)
        
        if not results:
            return {
                'total_checks': 0,
                'compliant': 0,
                'non_compliant': 0,
                'warnings': 0
            }
        
        compliant = sum(1 for r in results if r.compliance_level == ComplianceLevel.COMPLIANT)
        non_compliant = sum(1 for r in results if r.compliance_level == ComplianceLevel.NON_COMPLIANT)
        warnings = sum(1 for r in results if r.compliance_level == ComplianceLevel.WARNING)
        
        return {
            'total_checks': len(results),
            'compliant': compliant,
            'non_compliant': non_compliant,
            'warnings': warnings,
            'compliance_rate': (compliant / len(results) * 100) if results else 0.0
        }


def main():
    """主函数 - 示例用法"""
    governance = DataGovernance()
    
    # 添加治理规则
    rule = governance.add_rule({
        'name': '数据保留规则',
        'rule_type': 'retention',
        'rule_config': {
            'max_retention_days': 365
        }
    })
    
    # 检查合规性
    data = {
        'created_at': datetime.utcnow() - timedelta(days=400),
        'classification': 'public'
    }
    
    results = governance.check_compliance(data, [rule.rule_id])
    print(f"合规性检查: {results[0].compliance_level.value}")


if __name__ == '__main__':
    main()
