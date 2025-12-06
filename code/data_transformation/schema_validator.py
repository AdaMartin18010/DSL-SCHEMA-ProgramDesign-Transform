"""
Schema验证器

专注于Schema数据验证
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """验证级别"""
    STRICT = "strict"  # 严格验证
    MODERATE = "moderate"  # 中等验证
    LOOSE = "loose"  # 宽松验证


class ValidationErrorType(Enum):
    """验证错误类型"""
    MISSING_FIELD = "missing_field"  # 缺失字段
    INVALID_TYPE = "invalid_type"  # 无效类型
    INVALID_VALUE = "invalid_value"  # 无效值
    CONSTRAINT_VIOLATION = "constraint_violation"  # 约束违反
    REFERENCE_ERROR = "reference_error"  # 引用错误


@dataclass
class ValidationError:
    """验证错误"""
    error_type: ValidationErrorType
    path: str  # 错误路径
    message: str  # 错误消息
    severity: str = "error"  # 严重程度（error, warning, info）


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool  # 是否有效
    errors: List[ValidationError]  # 错误列表
    warnings: List[ValidationError]  # 警告列表
    info: List[ValidationError]  # 信息列表


class SchemaValidator:
    """
    Schema验证器
    
    专注于Schema数据验证
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.validation_level = validation_level
        self.validation_rules: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_validation_rule(self, schema_path: str, rule: Dict[str, Any]):
        """
        添加验证规则
        
        Args:
            schema_path: Schema路径
            rule: 验证规则
        """
        if schema_path not in self.validation_rules:
            self.validation_rules[schema_path] = []
        
        self.validation_rules[schema_path].append(rule)
    
    def validate_schema(self, schema: Dict[str, Any],
                       schema_definition: Dict[str, Any]) -> ValidationResult:
        """
        验证Schema
        
        Args:
            schema: 要验证的Schema数据
            schema_definition: Schema定义
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        info = []
        
        # 验证表结构
        if 'tables' in schema_definition:
            table_errors, table_warnings, table_info = self._validate_tables(
                schema.get('tables', {}),
                schema_definition.get('tables', {})
            )
            errors.extend(table_errors)
            warnings.extend(table_warnings)
            info.extend(table_info)
        
        # 验证关系
        if 'relationships' in schema_definition:
            rel_errors, rel_warnings, rel_info = self._validate_relationships(
                schema.get('relationships', []),
                schema_definition.get('relationships', []),
                schema.get('tables', {})
            )
            errors.extend(rel_errors)
            warnings.extend(rel_warnings)
            info.extend(rel_info)
        
        # 验证约束
        if 'constraints' in schema_definition:
            constraint_errors, constraint_warnings, constraint_info = self._validate_constraints(
                schema.get('constraints', []),
                schema_definition.get('constraints', []),
                schema.get('tables', {})
            )
            errors.extend(constraint_errors)
            warnings.extend(constraint_warnings)
            info.extend(constraint_info)
        
        # 应用自定义验证规则
        for schema_path, rules in self.validation_rules.items():
            custom_errors, custom_warnings, custom_info = self._apply_custom_rules(
                schema, schema_path, rules
            )
            errors.extend(custom_errors)
            warnings.extend(custom_warnings)
            info.extend(custom_info)
        
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            info=info
        )
    
    def _validate_tables(self, tables: Dict[str, Any],
                        table_definitions: Dict[str, Any]) -> tuple:
        """验证表结构"""
        errors = []
        warnings = []
        info = []
        
        # 检查必需的表
        required_tables = set(table_definitions.keys())
        actual_tables = set(tables.keys())
        
        missing_tables = required_tables - actual_tables
        for table_name in missing_tables:
            errors.append(ValidationError(
                error_type=ValidationErrorType.MISSING_FIELD,
                path=f"tables.{table_name}",
                message=f"必需的表 {table_name} 不存在",
                severity="error"
            ))
        
        # 验证每个表的结构
        for table_name, table_def in table_definitions.items():
            if table_name not in tables:
                continue
            
            table = tables[table_name]
            
            # 验证字段
            if 'fields' in table_def:
                field_errors, field_warnings, field_info = self._validate_fields(
                    table.get('fields', {}),
                    table_def.get('fields', {}),
                    f"tables.{table_name}"
                )
                errors.extend(field_errors)
                warnings.extend(field_warnings)
                info.extend(field_info)
            
            # 验证主键
            if 'primary_key' in table_def:
                pk = table_def['primary_key']
                if 'primary_key' not in table or table['primary_key'] != pk:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.CONSTRAINT_VIOLATION,
                        path=f"tables.{table_name}.primary_key",
                        message=f"主键不匹配：期望 {pk}，实际 {table.get('primary_key')}",
                        severity="error"
                    ))
        
        return errors, warnings, info
    
    def _validate_fields(self, fields: Dict[str, Any],
                        field_definitions: Dict[str, Any],
                        base_path: str) -> tuple:
        """验证字段"""
        errors = []
        warnings = []
        info = []
        
        # 检查必需的字段
        required_fields = {k for k, v in field_definitions.items() if v.get('required', False)}
        actual_fields = set(fields.keys())
        
        missing_fields = required_fields - actual_fields
        for field_name in missing_fields:
            errors.append(ValidationError(
                error_type=ValidationErrorType.MISSING_FIELD,
                path=f"{base_path}.fields.{field_name}",
                message=f"必需的字段 {field_name} 不存在",
                severity="error"
            ))
        
        # 验证每个字段
        for field_name, field_def in field_definitions.items():
            if field_name not in fields:
                continue
            
            field = fields[field_name]
            
            # 验证类型
            if 'type' in field_def:
                expected_type = field_def['type']
                actual_type = field.get('type')
                
                if actual_type != expected_type:
                    if self.validation_level == ValidationLevel.STRICT:
                        errors.append(ValidationError(
                            error_type=ValidationErrorType.INVALID_TYPE,
                            path=f"{base_path}.fields.{field_name}.type",
                            message=f"类型不匹配：期望 {expected_type}，实际 {actual_type}",
                            severity="error"
                        ))
                    elif self.validation_level == ValidationLevel.MODERATE:
                        warnings.append(ValidationError(
                            error_type=ValidationErrorType.INVALID_TYPE,
                            path=f"{base_path}.fields.{field_name}.type",
                            message=f"类型不匹配：期望 {expected_type}，实际 {actual_type}",
                            severity="warning"
                        ))
            
            # 验证可空性
            if 'nullable' in field_def:
                expected_nullable = field_def['nullable']
                actual_nullable = field.get('nullable', True)
                
                if actual_nullable != expected_nullable:
                    warnings.append(ValidationError(
                        error_type=ValidationErrorType.CONSTRAINT_VIOLATION,
                        path=f"{base_path}.fields.{field_name}.nullable",
                        message=f"可空性不匹配：期望 {expected_nullable}，实际 {actual_nullable}",
                        severity="warning"
                    ))
        
        return errors, warnings, info
    
    def _validate_relationships(self, relationships: List[Dict[str, Any]],
                               relationship_definitions: List[Dict[str, Any]],
                               tables: Dict[str, Any]) -> tuple:
        """验证关系"""
        errors = []
        warnings = []
        info = []
        
        # 验证每个关系
        for rel in relationships:
            from_table = rel.get('from_table')
            to_table = rel.get('to_table')
            
            # 检查表是否存在
            if from_table not in tables:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.REFERENCE_ERROR,
                    path=f"relationships.{from_table}",
                    message=f"关系引用的表 {from_table} 不存在",
                    severity="error"
                ))
            
            if to_table not in tables:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.REFERENCE_ERROR,
                    path=f"relationships.{to_table}",
                    message=f"关系引用的表 {to_table} 不存在",
                    severity="error"
                ))
            
            # 检查字段是否存在
            if from_table in tables and to_table in tables:
                from_field = rel.get('from_field')
                to_field = rel.get('to_field')
                
                from_table_fields = tables[from_table].get('fields', {})
                to_table_fields = tables[to_table].get('fields', {})
                
                if from_field and from_field not in from_table_fields:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.REFERENCE_ERROR,
                        path=f"relationships.{from_table}.{from_field}",
                        message=f"关系引用的字段 {from_table}.{from_field} 不存在",
                        severity="error"
                    ))
                
                if to_field and to_field not in to_table_fields:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.REFERENCE_ERROR,
                        path=f"relationships.{to_table}.{to_field}",
                        message=f"关系引用的字段 {to_table}.{to_field} 不存在",
                        severity="error"
                    ))
        
        return errors, warnings, info
    
    def _validate_constraints(self, constraints: List[Dict[str, Any]],
                             constraint_definitions: List[Dict[str, Any]],
                             tables: Dict[str, Any]) -> tuple:
        """验证约束"""
        errors = []
        warnings = []
        info = []
        
        # 验证每个约束
        for constraint in constraints:
            constraint_type = constraint.get('type')
            table_name = constraint.get('table')
            
            # 检查表是否存在
            if table_name and table_name not in tables:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.REFERENCE_ERROR,
                    path=f"constraints.{table_name}",
                    message=f"约束引用的表 {table_name} 不存在",
                    severity="error"
                ))
        
        return errors, warnings, info
    
    def _apply_custom_rules(self, schema: Dict[str, Any],
                          schema_path: str,
                          rules: List[Dict[str, Any]]) -> tuple:
        """应用自定义验证规则"""
        errors = []
        warnings = []
        info = []
        
        # 简化实现：根据规则类型应用验证
        for rule in rules:
            rule_type = rule.get('type')
            
            if rule_type == 'required':
                # 必需字段检查
                field_path = rule.get('field')
                if not self._get_value_by_path(schema, field_path):
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.MISSING_FIELD,
                        path=field_path,
                        message=f"必需字段 {field_path} 不存在",
                        severity="error"
                    ))
            
            elif rule_type == 'type_check':
                # 类型检查
                field_path = rule.get('field')
                expected_type = rule.get('expected_type')
                actual_value = self._get_value_by_path(schema, field_path)
                
                if actual_value is not None and not isinstance(actual_value, eval(expected_type)):
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.INVALID_TYPE,
                        path=field_path,
                        message=f"字段 {field_path} 类型不匹配：期望 {expected_type}",
                        severity="error"
                    ))
            
            elif rule_type == 'value_range':
                # 值范围检查
                field_path = rule.get('field')
                min_val = rule.get('min')
                max_val = rule.get('max')
                actual_value = self._get_value_by_path(schema, field_path)
                
                if actual_value is not None:
                    if min_val is not None and actual_value < min_val:
                        errors.append(ValidationError(
                            error_type=ValidationErrorType.INVALID_VALUE,
                            path=field_path,
                            message=f"字段 {field_path} 值 {actual_value} 小于最小值 {min_val}",
                            severity="error"
                        ))
                    
                    if max_val is not None and actual_value > max_val:
                        errors.append(ValidationError(
                            error_type=ValidationErrorType.INVALID_VALUE,
                            path=field_path,
                            message=f"字段 {field_path} 值 {actual_value} 大于最大值 {max_val}",
                            severity="error"
                        ))
        
        return errors, warnings, info
    
    def _get_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """根据路径获取值"""
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value


def main():
    """主函数 - 示例用法"""
    validator = SchemaValidator(ValidationLevel.MODERATE)
    
    # Schema定义
    schema_definition = {
        'tables': {
            'users': {
                'fields': {
                    'id': {'type': 'integer', 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'email': {'type': 'string', 'required': False}
                },
                'primary_key': 'id'
            }
        }
    }
    
    # 要验证的Schema
    schema = {
        'tables': {
            'users': {
                'fields': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'}
                },
                'primary_key': 'id'
            }
        }
    }
    
    # 验证
    result = validator.validate_schema(schema, schema_definition)
    
    print(f"验证结果: {'有效' if result.valid else '无效'}")
    print(f"错误数: {len(result.errors)}")
    print(f"警告数: {len(result.warnings)}")
    
    for error in result.errors:
        print(f"错误: {error.path} - {error.message}")


if __name__ == '__main__':
    main()
