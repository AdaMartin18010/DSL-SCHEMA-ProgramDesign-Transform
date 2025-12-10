"""
高级数据转换验证器模块

专注于高级数据转换验证、复杂验证规则、验证链
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class ValidationRuleType(Enum):
    """验证规则类型"""
    TYPE = "type"  # 类型验证
    RANGE = "range"  # 范围验证
    PATTERN = "pattern"  # 模式验证
    LENGTH = "length"  # 长度验证
    UNIQUE = "unique"  # 唯一性验证
    CUSTOM = "custom"  # 自定义验证
    CROSS_FIELD = "cross_field"  # 跨字段验证
    BUSINESS_RULE = "business_rule"  # 业务规则验证


class ValidationSeverity(Enum):
    """验证严重程度"""
    ERROR = "error"  # 错误
    WARNING = "warning"  # 警告
    INFO = "info"  # 信息


@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    rule_type: ValidationRuleType
    field_name: str
    rule_config: Dict[str, Any]
    severity: ValidationSeverity
    custom_validator: Optional[Callable] = None
    enabled: bool = True


@dataclass
class ValidationError:
    """验证错误"""
    rule_id: str
    field_name: str
    error_message: str
    severity: ValidationSeverity
    value: Any = None


@dataclass
class ValidationResult:
    """验证结果"""
    validation_id: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    validated_at: datetime


class DataTransformationValidatorAdvanced:
    """
    高级数据转换验证器
    
    专注于高级数据转换验证、复杂验证规则、验证链
    """
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
    
    def add_rule(self, rule_config: Dict[str, Any]) -> ValidationRule:
        """
        添加验证规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            验证规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = ValidationRule(
            rule_id=rule_id,
            rule_type=ValidationRuleType(rule_config.get('rule_type', 'type')),
            field_name=rule_config.get('field_name', ''),
            rule_config=rule_config.get('rule_config', {}),
            severity=ValidationSeverity(rule_config.get('severity', 'error')),
            custom_validator=rule_config.get('custom_validator'),
            enabled=rule_config.get('enabled', True)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        验证数据
        
        Args:
            data: 要验证的数据
            
        Returns:
            验证结果
        """
        validation_id = f"validation_{datetime.utcnow().timestamp()}"
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        
        # 应用所有启用的规则
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            error = self._apply_rule(rule, data)
            if error:
                if error.severity == ValidationSeverity.ERROR:
                    errors.append(error)
                elif error.severity == ValidationSeverity.WARNING:
                    warnings.append(error)
        
        is_valid = len(errors) == 0
        
        result = ValidationResult(
            validation_id=validation_id,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            validated_at=datetime.utcnow()
        )
        
        self.validation_history.append(result)
        return result
    
    def _apply_rule(self, rule: ValidationRule, data: Dict[str, Any]) -> Optional[ValidationError]:
        """应用验证规则"""
        field_value = data.get(rule.field_name)
        config = rule.rule_config
        
        if rule.rule_type == ValidationRuleType.TYPE:
            expected_type = config.get('type')
            if expected_type and not isinstance(field_value, expected_type):
                return ValidationError(
                    rule_id=rule.rule_id,
                    field_name=rule.field_name,
                    error_message=f"字段 {rule.field_name} 类型错误，期望 {expected_type.__name__}，实际 {type(field_value).__name__}",
                    severity=rule.severity,
                    value=field_value
                )
        
        elif rule.rule_type == ValidationRuleType.RANGE:
            min_value = config.get('min')
            max_value = config.get('max')
            if min_value is not None and field_value < min_value:
                return ValidationError(
                    rule_id=rule.rule_id,
                    field_name=rule.field_name,
                    error_message=f"字段 {rule.field_name} 值 {field_value} 小于最小值 {min_value}",
                    severity=rule.severity,
                    value=field_value
                )
            if max_value is not None and field_value > max_value:
                return ValidationError(
                    rule_id=rule.rule_id,
                    field_name=rule.field_name,
                    error_message=f"字段 {rule.field_name} 值 {field_value} 大于最大值 {max_value}",
                    severity=rule.severity,
                    value=field_value
                )
        
        elif rule.rule_type == ValidationRuleType.PATTERN:
            pattern = config.get('pattern')
            if pattern and field_value:
                if not re.match(pattern, str(field_value)):
                    return ValidationError(
                        rule_id=rule.rule_id,
                        field_name=rule.field_name,
                        error_message=f"字段 {rule.field_name} 值 {field_value} 不匹配模式 {pattern}",
                        severity=rule.severity,
                        value=field_value
                    )
        
        elif rule.rule_type == ValidationRuleType.LENGTH:
            min_length = config.get('min_length')
            max_length = config.get('max_length')
            if field_value:
                length = len(str(field_value))
                if min_length is not None and length < min_length:
                    return ValidationError(
                        rule_id=rule.rule_id,
                        field_name=rule.field_name,
                        error_message=f"字段 {rule.field_name} 长度 {length} 小于最小长度 {min_length}",
                        severity=rule.severity,
                        value=field_value
                    )
                if max_length is not None and length > max_length:
                    return ValidationError(
                        rule_id=rule.rule_id,
                        field_name=rule.field_name,
                        error_message=f"字段 {rule.field_name} 长度 {length} 大于最大长度 {max_length}",
                        severity=rule.severity,
                        value=field_value
                    )
        
        elif rule.rule_type == ValidationRuleType.CUSTOM:
            if rule.custom_validator:
                try:
                    if not rule.custom_validator(field_value, data):
                        return ValidationError(
                            rule_id=rule.rule_id,
                            field_name=rule.field_name,
                            error_message=f"字段 {rule.field_name} 自定义验证失败",
                            severity=rule.severity,
                            value=field_value
                        )
                except Exception as e:
                    return ValidationError(
                        rule_id=rule.rule_id,
                        field_name=rule.field_name,
                        error_message=f"字段 {rule.field_name} 自定义验证异常: {e}",
                        severity=rule.severity,
                        value=field_value
                    )
        
        return None
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        获取验证摘要
        
        Returns:
            验证摘要
        """
        total_validations = len(self.validation_history)
        successful_validations = sum(1 for v in self.validation_history if v.is_valid)
        total_errors = sum(len(v.errors) for v in self.validation_history)
        total_warnings = sum(len(v.warnings) for v in self.validation_history)
        
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled),
            'total_validations': total_validations,
            'successful_validations': successful_validations,
            'failed_validations': total_validations - successful_validations,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'success_rate': (successful_validations / total_validations * 100) if total_validations > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    validator = DataTransformationValidatorAdvanced()
    
    # 添加验证规则
    rule = validator.add_rule({
        'rule_type': 'type',
        'field_name': 'age',
        'rule_config': {'type': int},
        'severity': 'error'
    })
    
    # 验证数据
    data = {'age': 25}
    result = validator.validate(data)
    print(f"验证结果: {result.is_valid}")


if __name__ == '__main__':
    main()
