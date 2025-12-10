"""
数据转换验证器模块

专注于数据转换验证、转换结果验证、转换质量检查
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """验证类型"""
    SCHEMA = "schema"  # Schema验证
    DATA_QUALITY = "data_quality"  # 数据质量验证
    BUSINESS_RULE = "business_rule"  # 业务规则验证
    COMPLETENESS = "completeness"  # 完整性验证
    ACCURACY = "accuracy"  # 准确性验证


@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    validation_type: ValidationType
    rule_config: Dict[str, Any]
    enabled: bool = True


@dataclass
class ValidationResult:
    """验证结果"""
    validation_id: str
    valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    validation_time: float


class DataTransformationValidator:
    """
    数据转换验证器
    
    专注于数据转换验证、转换结果验证、转换质量检查
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
            validation_type=ValidationType(rule_config.get('validation_type', 'schema')),
            rule_config=rule_config.get('rule_config', {}),
            enabled=rule_config.get('enabled', True)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def validate_transformation(self, original_data: List[Dict[str, Any]],
                               transformed_data: List[Dict[str, Any]],
                               rule_ids: Optional[List[str]] = None) -> ValidationResult:
        """
        验证转换结果
        
        Args:
            original_data: 原始数据
            transformed_data: 转换后的数据
            rule_ids: 规则ID列表（可选）
            
        Returns:
            验证结果
        """
        validation_id = f"validate_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        errors = []
        warnings = []
        
        rules_to_apply = rule_ids if rule_ids else [r.rule_id for r in self.rules.values() if r.enabled]
        
        for rule_id in rules_to_apply:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            
            if not rule.enabled:
                continue
            
            # 根据验证类型执行验证
            if rule.validation_type == ValidationType.SCHEMA:
                schema_errors = self._validate_schema(original_data, transformed_data, rule)
                errors.extend(schema_errors)
            
            elif rule.validation_type == ValidationType.DATA_QUALITY:
                quality_errors, quality_warnings = self._validate_data_quality(transformed_data, rule)
                errors.extend(quality_errors)
                warnings.extend(quality_warnings)
            
            elif rule.validation_type == ValidationType.BUSINESS_RULE:
                business_errors = self._validate_business_rules(transformed_data, rule)
                errors.extend(business_errors)
            
            elif rule.validation_type == ValidationType.COMPLETENESS:
                completeness_errors = self._validate_completeness(original_data, transformed_data, rule)
                errors.extend(completeness_errors)
            
            elif rule.validation_type == ValidationType.ACCURACY:
                accuracy_errors = self._validate_accuracy(original_data, transformed_data, rule)
                errors.extend(accuracy_errors)
        
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
    
    def _validate_schema(self, original_data: List[Dict[str, Any]],
                        transformed_data: List[Dict[str, Any]],
                        rule: ValidationRule) -> List[Dict[str, Any]]:
        """Schema验证"""
        errors = []
        
        if not original_data or not transformed_data:
            return errors
        
        original_schema = set(original_data[0].keys())
        transformed_schema = set(transformed_data[0].keys())
        
        required_fields = rule.rule_config.get('required_fields', [])
        for field in required_fields:
            if field not in transformed_schema:
                errors.append({
                    'rule_id': rule.rule_id,
                    'type': 'missing_field',
                    'field': field,
                    'message': f'必需字段 {field} 在转换后的数据中缺失'
                })
        
        return errors
    
    def _validate_data_quality(self, transformed_data: List[Dict[str, Any]],
                               rule: ValidationRule) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """数据质量验证"""
        errors = []
        warnings = []
        
        quality_rules = rule.rule_config.get('quality_rules', [])
        
        for quality_rule in quality_rules:
            field = quality_rule.get('field')
            threshold = quality_rule.get('threshold', 0.9)
            
            if field:
                null_count = sum(1 for r in transformed_data if r.get(field) is None)
                null_rate = null_count / len(transformed_data) if transformed_data else 0.0
                
                if null_rate > (1 - threshold):
                    errors.append({
                        'rule_id': rule.rule_id,
                        'type': 'low_quality',
                        'field': field,
                        'null_rate': null_rate,
                        'message': f'字段 {field} 的空值率 {null_rate:.2%} 超过阈值'
                    })
                elif null_rate > (1 - threshold) * 0.8:
                    warnings.append({
                        'rule_id': rule.rule_id,
                        'type': 'quality_warning',
                        'field': field,
                        'null_rate': null_rate,
                        'message': f'字段 {field} 的空值率 {null_rate:.2%} 接近阈值'
                    })
        
        return errors, warnings
    
    def _validate_business_rules(self, transformed_data: List[Dict[str, Any]],
                                rule: ValidationRule) -> List[Dict[str, Any]]:
        """业务规则验证"""
        errors = []
        
        business_rules = rule.rule_config.get('business_rules', [])
        
        for business_rule in business_rules:
            rule_func = business_rule.get('function')
            if rule_func and callable(rule_func):
                for i, record in enumerate(transformed_data):
                    try:
                        if not rule_func(record):
                            errors.append({
                                'rule_id': rule.rule_id,
                                'type': 'business_rule_violation',
                                'record_index': i,
                                'message': business_rule.get('message', '业务规则验证失败')
                            })
                    except Exception as e:
                        errors.append({
                            'rule_id': rule.rule_id,
                            'type': 'business_rule_error',
                            'record_index': i,
                            'message': f'业务规则验证错误: {str(e)}'
                        })
        
        return errors
    
    def _validate_completeness(self, original_data: List[Dict[str, Any]],
                              transformed_data: List[Dict[str, Any]],
                              rule: ValidationRule) -> List[Dict[str, Any]]:
        """完整性验证"""
        errors = []
        
        # 检查记录数
        if len(transformed_data) < len(original_data):
            loss_rate = (len(original_data) - len(transformed_data)) / len(original_data)
            threshold = rule.rule_config.get('loss_threshold', 0.05)
            
            if loss_rate > threshold:
                errors.append({
                    'rule_id': rule.rule_id,
                    'type': 'data_loss',
                    'original_count': len(original_data),
                    'transformed_count': len(transformed_data),
                    'loss_rate': loss_rate,
                    'message': f'数据丢失率 {loss_rate:.2%} 超过阈值 {threshold:.2%}'
                })
        
        return errors
    
    def _validate_accuracy(self, original_data: List[Dict[str, Any]],
                          transformed_data: List[Dict[str, Any]],
                          rule: ValidationRule) -> List[Dict[str, Any]]:
        """准确性验证"""
        errors = []
        
        # 简化实现：检查关键字段的一致性
        key_fields = rule.rule_config.get('key_fields', [])
        
        if key_fields and len(original_data) == len(transformed_data):
            for i, (orig, trans) in enumerate(zip(original_data, transformed_data)):
                for field in key_fields:
                    orig_value = orig.get(field)
                    trans_value = trans.get(field)
                    
                    if orig_value != trans_value:
                        errors.append({
                            'rule_id': rule.rule_id,
                            'type': 'accuracy_mismatch',
                            'record_index': i,
                            'field': field,
                            'original_value': orig_value,
                            'transformed_value': trans_value,
                            'message': f'记录 {i} 字段 {field} 的值不一致'
                        })
        
        return errors
    
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
    validator = DataTransformationValidator()
    
    # 添加验证规则
    rule = validator.add_rule({
        'validation_type': 'completeness',
        'rule_config': {
            'loss_threshold': 0.1
        }
    })
    
    # 验证转换
    original = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    transformed = [{'id': 1, 'name': 'Alice'}]
    
    result = validator.validate_transformation(original, transformed, [rule.rule_id])
    print(f"验证结果: 有效={result.valid}, 错误数={len(result.errors)}")


if __name__ == '__main__':
    main()
