"""
数据验证模块

专注于数据验证、数据清洗、数据质量检查
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
    TYPE = "type"  # 类型检查
    RANGE = "range"  # 范围检查
    PATTERN = "pattern"  # 模式匹配
    LENGTH = "length"  # 长度检查
    UNIQUE = "unique"  # 唯一性检查
    CUSTOM = "custom"  # 自定义规则


class ValidationSeverity(Enum):
    """验证严重程度"""
    ERROR = "error"  # 错误
    WARNING = "warning"  # 警告
    INFO = "info"  # 信息


@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    field: str
    rule_type: ValidationRuleType
    rule_config: Dict[str, Any]
    severity: ValidationSeverity = ValidationSeverity.ERROR
    message: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""
    field: str
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: Optional[str] = None
    value: Any = None


class DataValidator:
    """
    数据验证器
    
    专注于数据验证、数据清洗、数据质量检查
    """
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.rule_sets: Dict[str, List[str]] = {}  # 规则集ID到规则ID列表的映射
    
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
            field=rule_config['field'],
            rule_type=ValidationRuleType(rule_config.get('rule_type', 'required')),
            rule_config=rule_config.get('rule_config', {}),
            severity=ValidationSeverity(rule_config.get('severity', 'error')),
            message=rule_config.get('message')
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def create_rule_set(self, rule_set_id: str, rule_ids: List[str]) -> bool:
        """
        创建规则集
        
        Args:
            rule_set_id: 规则集ID
            rule_ids: 规则ID列表
            
        Returns:
            是否成功
        """
        # 验证规则ID是否存在
        for rule_id in rule_ids:
            if rule_id not in self.rules:
                logger.warning(f"规则不存在: {rule_id}")
                return False
        
        self.rule_sets[rule_set_id] = rule_ids
        return True
    
    def validate_data(self, data: Dict[str, Any],
                     rule_set_id: Optional[str] = None,
                     rule_ids: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        验证数据
        
        Args:
            data: 数据字典
            rule_set_id: 规则集ID（可选）
            rule_ids: 规则ID列表（可选）
            
        Returns:
            验证结果列表
        """
        results = []
        
        # 确定要使用的规则
        if rule_set_id:
            if rule_set_id not in self.rule_sets:
                logger.error(f"规则集不存在: {rule_set_id}")
                return results
            rule_ids_to_use = self.rule_sets[rule_set_id]
        elif rule_ids:
            rule_ids_to_use = rule_ids
        else:
            # 使用所有规则
            rule_ids_to_use = list(self.rules.keys())
        
        # 执行验证
        for rule_id in rule_ids_to_use:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            field = rule.field
            
            # 获取字段值
            value = data.get(field)
            
            # 执行验证
            passed, message = self._validate_field(value, rule)
            
            result = ValidationResult(
                field=field,
                rule_id=rule_id,
                passed=passed,
                severity=rule.severity,
                message=message or rule.message,
                value=value
            )
            
            results.append(result)
        
        return results
    
    def _validate_field(self, value: Any, rule: ValidationRule) -> tuple[bool, Optional[str]]:
        """验证字段"""
        rule_type = rule.rule_type
        config = rule.rule_config
        
        if rule_type == ValidationRuleType.REQUIRED:
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, f"字段 {rule.field} 是必填的"
            return True, None
        
        elif rule_type == ValidationRuleType.TYPE:
            expected_type = config.get('type')
            if expected_type:
                type_mapping = {
                    'string': str,
                    'integer': int,
                    'float': float,
                    'boolean': bool,
                    'list': list,
                    'dict': dict
                }
                expected_python_type = type_mapping.get(expected_type)
                
                if expected_python_type and not isinstance(value, expected_python_type):
                    return False, f"字段 {rule.field} 类型错误，期望 {expected_type}"
            return True, None
        
        elif rule_type == ValidationRuleType.RANGE:
            min_val = config.get('min')
            max_val = config.get('max')
            
            if isinstance(value, (int, float)):
                if min_val is not None and value < min_val:
                    return False, f"字段 {rule.field} 值 {value} 小于最小值 {min_val}"
                if max_val is not None and value > max_val:
                    return False, f"字段 {rule.field} 值 {value} 大于最大值 {max_val}"
            return True, None
        
        elif rule_type == ValidationRuleType.PATTERN:
            pattern = config.get('pattern', '')
            if pattern and isinstance(value, str):
                if not re.match(pattern, value):
                    return False, f"字段 {rule.field} 值 {value} 不匹配模式 {pattern}"
            return True, None
        
        elif rule_type == ValidationRuleType.LENGTH:
            min_len = config.get('min_length')
            max_len = config.get('max_length')
            
            if isinstance(value, (str, list)):
                length = len(value)
                if min_len is not None and length < min_len:
                    return False, f"字段 {rule.field} 长度 {length} 小于最小长度 {min_len}"
                if max_len is not None and length > max_len:
                    return False, f"字段 {rule.field} 长度 {length} 大于最大长度 {max_len}"
            return True, None
        
        elif rule_type == ValidationRuleType.UNIQUE:
            # 唯一性检查需要在数据集中进行，这里简化处理
            return True, None
        
        elif rule_type == ValidationRuleType.CUSTOM:
            custom_validator = config.get('validator')
            if custom_validator and callable(custom_validator):
                try:
                    result = custom_validator(value)
                    if isinstance(result, tuple):
                        return result
                    elif isinstance(result, bool):
                        return result, None if result else f"字段 {rule.field} 自定义验证失败"
                except Exception as e:
                    return False, f"自定义验证器执行失败: {e}"
            return True, None
        
        return True, None
    
    def clean_data(self, data: Dict[str, Any],
                  cleaning_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        清洗数据
        
        Args:
            data: 数据字典
            cleaning_rules: 清洗规则列表
            
        Returns:
            清洗后的数据
        """
        cleaned_data = data.copy()
        
        for rule in cleaning_rules:
            rule_type = rule.get('type')
            field = rule.get('field')
            
            if field not in cleaned_data:
                continue
            
            value = cleaned_data[field]
            
            if rule_type == 'trim':
                # 去除首尾空格
                if isinstance(value, str):
                    cleaned_data[field] = value.strip()
            
            elif rule_type == 'lowercase':
                # 转换为小写
                if isinstance(value, str):
                    cleaned_data[field] = value.lower()
            
            elif rule_type == 'uppercase':
                # 转换为大写
                if isinstance(value, str):
                    cleaned_data[field] = value.upper()
            
            elif rule_type == 'remove_special_chars':
                # 移除特殊字符
                if isinstance(value, str):
                    pattern = rule.get('pattern', r'[^a-zA-Z0-9\s]')
                    cleaned_data[field] = re.sub(pattern, '', value)
            
            elif rule_type == 'default_value':
                # 设置默认值
                if value is None or (isinstance(value, str) and not value.strip()):
                    cleaned_data[field] = rule.get('default')
            
            elif rule_type == 'format':
                # 格式化
                format_func = rule.get('formatter')
                if format_func and callable(format_func):
                    try:
                        cleaned_data[field] = format_func(value)
                    except Exception as e:
                        logger.warning(f"格式化字段失败: {field}, 错误: {e}")
        
        return cleaned_data
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        获取验证摘要
        
        Args:
            results: 验证结果列表
            
        Returns:
            验证摘要
        """
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        
        errors = [r for r in results if not r.passed and r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in results if not r.passed and r.severity == ValidationSeverity.WARNING]
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'pass_rate': (passed / total * 100) if total > 0 else 0.0,
            'errors': errors,
            'warnings': warnings
        }


def main():
    """主函数 - 示例用法"""
    validator = DataValidator()
    
    # 添加验证规则
    rule = validator.add_rule({
        'field': 'email',
        'rule_type': 'pattern',
        'rule_config': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        },
        'severity': 'error',
        'message': '邮箱格式不正确'
    })
    
    # 验证数据
    data = {
        'email': 'test@example.com',
        'age': 25
    }
    
    results = validator.validate_data(data, rule_ids=[rule.rule_id])
    summary = validator.get_validation_summary(results)
    print(f"验证摘要: {summary}")


if __name__ == '__main__':
    main()
