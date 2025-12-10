"""
增强数据验证模块

专注于增强数据验证、复杂验证规则、验证链
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class ValidationRuleType(Enum):
    """验证规则类型"""
    REQUIRED = "required"  # 必填
    TYPE_CHECK = "type_check"  # 类型检查
    RANGE_CHECK = "range_check"  # 范围检查
    PATTERN_MATCH = "pattern_match"  # 模式匹配
    LENGTH_CHECK = "length_check"  # 长度检查
    UNIQUE_CHECK = "unique_check"  # 唯一性检查
    CUSTOM = "custom"  # 自定义
    CROSS_FIELD = "cross_field"  # 跨字段验证


@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    field: Optional[str] = None
    rule_type: ValidationRuleType = ValidationRuleType.REQUIRED
    rule_config: Dict[str, Any] = None
    error_message: Optional[str] = None
    severity: str = "error"  # error, warning


@dataclass
class ValidationResult:
    """验证结果"""
    validation_id: str
    valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    validation_time: float


class DataValidationEnhanced:
    """
    增强数据验证器
    
    专注于增强数据验证、复杂验证规则、验证链
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
            field=rule_config.get('field'),
            rule_type=ValidationRuleType(rule_config.get('rule_type', 'required')),
            rule_config=rule_config.get('rule_config', {}),
            error_message=rule_config.get('error_message'),
            severity=rule_config.get('severity', 'error')
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def validate(self, data: List[Dict[str, Any]], rule_ids: Optional[List[str]] = None) -> ValidationResult:
        """
        验证数据
        
        Args:
            data: 数据列表
            rule_ids: 规则ID列表（可选）
            
        Returns:
            验证结果
        """
        validation_id = f"validate_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        errors = []
        warnings = []
        
        rules_to_apply = rule_ids if rule_ids else list(self.rules.keys())
        
        for rule_id in rules_to_apply:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            
            for i, record in enumerate(data):
                error = self._check_rule(record, rule, i)
                if error:
                    if rule.severity == 'error':
                        errors.append(error)
                    else:
                        warnings.append(error)
        
        end_time = datetime.utcnow()
        validation_time = (end_time - start_time).total_seconds()
        
        result = ValidationResult(
            validation_id=validation_id,
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_time=validation_time
        )
        
        self.validation_history.append(result)
        return result
    
    def _check_rule(self, record: Dict[str, Any], rule: ValidationRule, index: int) -> Optional[Dict[str, Any]]:
        """检查规则"""
        rule_type = rule.rule_type
        config = rule.rule_config or {}
        
        if rule_type == ValidationRuleType.REQUIRED:
            if rule.field and rule.field not in record or record.get(rule.field) is None:
                return {
                    'rule_id': rule.rule_id,
                    'field': rule.field,
                    'record_index': index,
                    'message': rule.error_message or f"字段 {rule.field} 是必填的"
                }
        
        elif rule_type == ValidationRuleType.TYPE_CHECK:
            if rule.field and rule.field in record:
                expected_type = config.get('type')
                value = record[rule.field]
                if expected_type == 'integer' and not isinstance(value, int):
                    return {
                        'rule_id': rule.rule_id,
                        'field': rule.field,
                        'record_index': index,
                        'message': rule.error_message or f"字段 {rule.field} 必须是整数"
                    }
                elif expected_type == 'string' and not isinstance(value, str):
                    return {
                        'rule_id': rule.rule_id,
                        'field': rule.field,
                        'record_index': index,
                        'message': rule.error_message or f"字段 {rule.field} 必须是字符串"
                    }
        
        elif rule_type == ValidationRuleType.RANGE_CHECK:
            if rule.field and rule.field in record:
                value = record[rule.field]
                if isinstance(value, (int, float)):
                    min_val = config.get('min')
                    max_val = config.get('max')
                    if min_val is not None and value < min_val:
                        return {
                            'rule_id': rule.rule_id,
                            'field': rule.field,
                            'record_index': index,
                            'message': rule.error_message or f"字段 {rule.field} 值 {value} 小于最小值 {min_val}"
                        }
                    if max_val is not None and value > max_val:
                        return {
                            'rule_id': rule.rule_id,
                            'field': rule.field,
                            'record_index': index,
                            'message': rule.error_message or f"字段 {rule.field} 值 {value} 大于最大值 {max_val}"
                        }
        
        elif rule_type == ValidationRuleType.PATTERN_MATCH:
            if rule.field and rule.field in record:
                pattern = config.get('pattern')
                value = record[rule.field]
                if pattern and isinstance(value, str):
                    if not re.match(pattern, value):
                        return {
                            'rule_id': rule.rule_id,
                            'field': rule.field,
                            'record_index': index,
                            'message': rule.error_message or f"字段 {rule.field} 不匹配模式 {pattern}"
                        }
        
        elif rule_type == ValidationRuleType.LENGTH_CHECK:
            if rule.field and rule.field in record:
                value = record[rule.field]
                if isinstance(value, str):
                    min_len = config.get('min_length')
                    max_len = config.get('max_length')
                    if min_len is not None and len(value) < min_len:
                        return {
                            'rule_id': rule.rule_id,
                            'field': rule.field,
                            'record_index': index,
                            'message': rule.error_message or f"字段 {rule.field} 长度小于最小值 {min_len}"
                        }
                    if max_len is not None and len(value) > max_len:
                        return {
                            'rule_id': rule.rule_id,
                            'field': rule.field,
                            'record_index': index,
                            'message': rule.error_message or f"字段 {rule.field} 长度大于最大值 {max_len}"
                        }
        
        elif rule_type == ValidationRuleType.UNIQUE_CHECK:
            if rule.field:
                # 需要在外部检查唯一性
                pass
        
        elif rule_type == ValidationRuleType.CUSTOM:
            custom_func = config.get('function')
            if custom_func and callable(custom_func):
                try:
                    if not custom_func(record):
                        return {
                            'rule_id': rule.rule_id,
                            'field': rule.field,
                            'record_index': index,
                            'message': rule.error_message or "自定义验证失败"
                        }
                except Exception as e:
                    return {
                        'rule_id': rule.rule_id,
                        'field': rule.field,
                        'record_index': index,
                        'message': f"自定义验证错误: {str(e)}"
                    }
        
        elif rule_type == ValidationRuleType.CROSS_FIELD:
            fields = config.get('fields', [])
            condition = config.get('condition')
            if condition and callable(condition):
                try:
                    if not condition(record):
                        return {
                            'rule_id': rule.rule_id,
                            'fields': fields,
                            'record_index': index,
                            'message': rule.error_message or "跨字段验证失败"
                        }
                except Exception as e:
                    return {
                        'rule_id': rule.rule_id,
                        'fields': fields,
                        'record_index': index,
                        'message': f"跨字段验证错误: {str(e)}"
                    }
        
        return None
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        获取验证统计
        
        Returns:
            验证统计
        """
        total_validations = len(self.validation_history)
        valid_count = sum(1 for r in self.validation_history if r.valid)
        total_errors = sum(len(r.errors) for r in self.validation_history)
        total_warnings = sum(len(r.warnings) for r in self.validation_history)
        
        return {
            'total_validations': total_validations,
            'valid_count': valid_count,
            'invalid_count': total_validations - valid_count,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'validation_rate': (valid_count / total_validations * 100) if total_validations > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    validator = DataValidationEnhanced()
    
    # 添加验证规则
    rule = validator.add_rule({
        'field': 'age',
        'rule_type': 'range_check',
        'rule_config': {'min': 0, 'max': 150},
        'error_message': '年龄必须在0-150之间'
    })
    
    # 验证数据
    data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 200}]
    result = validator.validate(data, [rule.rule_id])
    print(f"验证结果: 有效={result.valid}, 错误数={len(result.errors)}")


if __name__ == '__main__':
    main()
