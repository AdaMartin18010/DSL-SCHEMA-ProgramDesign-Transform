#!/usr/bin/env python3
"""
Mapping Validator
=================

映射验证器，用于：
- 验证模型映射的正确性
- 检查语义保持性
- 验证完备性和一致性
- 生成验证报告

Version: 2.2.0
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from pathlib import Path


class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """验证问题"""
    check: str
    message: str
    severity: ValidationSeverity
    source_path: str = ""
    target_path: str = ""
    suggestion: str = ""


@dataclass
class MappingValidationResult:
    """映射验证结果"""
    valid: bool
    syntax_correct: bool
    semantic_preserved: bool
    complete: bool
    consistent: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


class MappingValidator:
    """映射验证器"""
    
    def __init__(self):
        self.checkers: Dict[str, Callable] = {
            "syntax": self._check_syntax,
            "semantics": self._check_semantics,
            "completeness": self._check_completeness,
            "consistency": self._check_consistency,
            "type_safety": self._check_type_safety,
            "constraint_preservation": self._check_constraint_preservation
        }
    
    def validate(self, source: Any, target: Any, 
                mapping_info: Dict = None) -> MappingValidationResult:
        """
        验证映射的正确性
        
        检查：
        1. 语法正确性
        2. 语义保持性
        3. 完备性
        4. 一致性
        5. 类型安全
        6. 约束保持
        """
        issues = []
        
        # 1. 语法检查
        syntax_ok, syntax_issues = self._check_syntax(target)
        issues.extend(syntax_issues)
        
        # 2. 语义保持检查
        semantic_ok, semantic_issues = self._check_semantics(source, target, mapping_info)
        issues.extend(semantic_issues)
        
        # 3. 完备性检查
        complete_ok, complete_issues = self._check_completeness(source, target)
        issues.extend(complete_issues)
        
        # 4. 一致性检查
        consistent_ok, consistent_issues = self._check_consistency(target)
        issues.extend(consistent_issues)
        
        # 5. 类型安全
        type_safe_ok, type_issues = self._check_type_safety(source, target)
        issues.extend(type_issues)
        
        # 6. 约束保持
        constraint_ok, constraint_issues = self._check_constraint_preservation(source, target)
        issues.extend(constraint_issues)
        
        # 计算指标
        metrics = self._calculate_metrics(source, target, issues)
        
        # 确定总体有效性
        valid = (syntax_ok and semantic_ok and complete_ok and 
                consistent_ok and type_safe_ok and constraint_ok)
        
        return MappingValidationResult(
            valid=valid,
            syntax_correct=syntax_ok,
            semantic_preserved=semantic_ok,
            complete=complete_ok,
            consistent=consistent_ok,
            issues=issues,
            metrics=metrics
        )
    
    def _check_syntax(self, target: Any) -> Tuple[bool, List[ValidationIssue]]:
        """检查目标模型语法正确性"""
        issues = []
        
        if target is None:
            issues.append(ValidationIssue(
                check="syntax",
                message="Target model is None",
                severity=ValidationSeverity.ERROR,
                suggestion="Check mapping transformation"
            ))
            return False, issues
        
        if isinstance(target, dict):
            # 检查JSON Schema基本结构
            if "$schema" in target:
                # 检查JSON Schema语法
                schema_issues = self._validate_json_schema_syntax(target)
                issues.extend(schema_issues)
            
            # 检查循环引用
            if self._has_circular_reference(target):
                issues.append(ValidationIssue(
                    check="syntax",
                    message="Circular reference detected in target",
                    severity=ValidationSeverity.ERROR,
                    suggestion="Refactor the schema to remove circular dependencies"
                ))
        
        return len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues
    
    def _validate_json_schema_syntax(self, schema: Dict) -> List[ValidationIssue]:
        """验证JSON Schema语法"""
        issues = []
        
        # 检查必需的字段
        if "type" not in schema and "enum" not in schema and "const" not in schema:
            issues.append(ValidationIssue(
                check="syntax",
                message="Schema missing type/enum/const constraint",
                severity=ValidationSeverity.WARNING,
                suggestion="Add explicit type constraint"
            ))
        
        # 检查无效的组合
        if "additionalProperties" in schema and "properties" not in schema:
            issues.append(ValidationIssue(
                check="syntax",
                message="additionalProperties without properties",
                severity=ValidationSeverity.WARNING
            ))
        
        return issues
    
    def _has_circular_reference(self, obj: Any, path: Set = None) -> bool:
        """检测循环引用"""
        if path is None:
            path = set()
        
        if id(obj) in path:
            return True
        
        if isinstance(obj, dict):
            path.add(id(obj))
            for v in obj.values():
                if self._has_circular_reference(v, path.copy()):
                    return True
        elif isinstance(obj, list):
            path.add(id(obj))
            for item in obj:
                if self._has_circular_reference(item, path.copy()):
                    return True
        
        return False
    
    def _check_semantics(self, source: Any, target: Any, 
                        mapping_info: Dict = None) -> Tuple[bool, List[ValidationIssue]]:
        """检查语义保持性"""
        issues = []
        
        if mapping_info and "preserved_properties" in mapping_info:
            for prop in mapping_info["preserved_properties"]:
                preserved = self._check_property_preservation(source, target, prop)
                if not preserved:
                    issues.append(ValidationIssue(
                        check="semantics",
                        message=f"Property '{prop}' not preserved in mapping",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Ensure {prop} is correctly transformed"
                    ))
        
        # 检查信息丢失
        source_info = self._measure_information_content(source)
        target_info = self._measure_information_content(target)
        
        if target_info < source_info * 0.7:  # 信息丢失超过30%
            issues.append(ValidationIssue(
                check="semantics",
                message=f"Significant information loss: {source_info:.2f} -> {target_info:.2f}",
                severity=ValidationSeverity.WARNING,
                suggestion="Review mapping rules for information preservation"
            ))
        
        return len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues
    
    def _check_property_preservation(self, source: Any, target: Any, prop: str) -> bool:
        """检查特定属性是否保持"""
        source_value = self._get_nested_value(source, prop)
        target_value = self._get_nested_value(target, prop)
        
        if source_value is None:
            return True  # 源中没有，无需保持
        
        if target_value is None:
            return False
        
        # 简单的值比较
        return str(source_value) == str(target_value) or type(source_value) == type(target_value)
    
    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """获取嵌套值"""
        if not isinstance(obj, dict):
            return None
        
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _measure_information_content(self, obj: Any) -> float:
        """测量信息内容 (简化版)"""
        if obj is None:
            return 0.0
        
        json_str = json.dumps(obj, sort_keys=True, default=str)
        return len(json_str)
    
    def _check_completeness(self, source: Any, target: Any) -> Tuple[bool, List[ValidationIssue]]:
        """检查完备性"""
        issues = []
        
        # 检查源中所有元素在目标中都有对应
        if isinstance(source, dict) and isinstance(target, dict):
            source_elements = self._extract_elements(source)
            target_elements = self._extract_elements(target)
            
            missing = source_elements - target_elements
            if missing:
                issues.append(ValidationIssue(
                    check="completeness",
                    message=f"Elements missing in target: {missing}",
                    severity=ValidationSeverity.ERROR,
                    suggestion="Add missing elements to target model"
                ))
        
        return len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues
    
    def _extract_elements(self, obj: Any, prefix: str = "") -> Set[str]:
        """提取所有元素路径"""
        elements = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                elements.add(path)
                elements.update(self._extract_elements(value, path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                path = f"{prefix}[{i}]"
                elements.update(self._extract_elements(item, path))
        
        return elements
    
    def _check_consistency(self, target: Any) -> Tuple[bool, List[ValidationIssue]]:
        """检查目标模型内部一致性"""
        issues = []
        
        if isinstance(target, dict):
            # 检查类型一致性
            if "type" in target and "properties" in target:
                if target["type"] != "object":
                    issues.append(ValidationIssue(
                        check="consistency",
                        message=f"Type is {target['type']} but has properties (should be object)",
                        severity=ValidationSeverity.ERROR
                    ))
            
            # 检查范围一致性
            if "minimum" in target and "maximum" in target:
                if target["minimum"] > target["maximum"]:
                    issues.append(ValidationIssue(
                        check="consistency",
                        message="minimum > maximum",
                        severity=ValidationSeverity.ERROR
                    ))
        
        return len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues
    
    def _check_type_safety(self, source: Any, target: Any) -> Tuple[bool, List[ValidationIssue]]:
        """检查类型安全"""
        issues = []
        
        # 简化的类型检查
        source_type = type(source).__name__
        target_type = type(target).__name__
        
        if source_type != target_type:
            # 某些转换是允许的
            allowed_conversions = {
                ("dict", "dict"): True,
                ("list", "list"): True,
                ("str", "str"): True
            }
            
            if (source_type, target_type) not in allowed_conversions:
                issues.append(ValidationIssue(
                    check="type_safety",
                    message=f"Type changed from {source_type} to {target_type}",
                    severity=ValidationSeverity.WARNING
                ))
        
        return len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues
    
    def _check_constraint_preservation(self, source: Any, target: Any) -> Tuple[bool, List[ValidationIssue]]:
        """检查约束保持"""
        issues = []
        
        if isinstance(source, dict) and isinstance(target, dict):
            # 检查必需字段
            source_required = set(source.get("required", []))
            target_required = set(target.get("required", []))
            
            # 必需字段不应该丢失
            lost_required = source_required - target_required
            if lost_required:
                issues.append(ValidationIssue(
                    check="constraint_preservation",
                    message=f"Required fields lost: {lost_required}",
                    severity=ValidationSeverity.ERROR
                ))
        
        return len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues
    
    def _calculate_metrics(self, source: Any, target: Any, 
                          issues: List[ValidationIssue]) -> Dict[str, float]:
        """计算验证指标"""
        total_issues = len(issues)
        error_count = len([i for i in issues if i.severity == ValidationSeverity.ERROR])
        warning_count = len([i for i in issues if i.severity == ValidationSeverity.WARNING])
        
        source_size = self._measure_information_content(source)
        target_size = self._measure_information_content(target)
        
        return {
            "issue_count": total_issues,
            "error_count": error_count,
            "warning_count": warning_count,
            "error_rate": error_count / max(total_issues, 1),
            "source_size": source_size,
            "target_size": target_size,
            "size_ratio": target_size / max(source_size, 1),
            "information_retention": min(target_size / max(source_size, 1), 1.0)
        }
    
    def generate_report(self, result: MappingValidationResult, 
                       output_path: str = None) -> str:
        """生成验证报告"""
        report = f"""
# 映射验证报告
## Mapping Validation Report

**总体结果**: {'✅ 通过' if result.valid else '❌ 失败'}

### 验证项状态
| 检查项 | 状态 |
|--------|------|
| 语法正确性 | {'✅' if result.syntax_correct else '❌'} |
| 语义保持性 | {'✅' if result.semantic_preserved else '❌'} |
| 完备性 | {'✅' if result.complete else '❌'} |
| 一致性 | {'✅' if result.consistent else '❌'} |

### 指标
"""
        for metric, value in result.metrics.items():
            if isinstance(value, float):
                report += f"- **{metric}**: {value:.3f}\n"
            else:
                report += f"- **{metric}**: {value}\n"
        
        if result.issues:
            report += "\n### 发现的问题\n"
            for issue in result.issues:
                emoji = "🔴" if issue.severity == ValidationSeverity.ERROR else "🟡"
                report += f"\n{emoji} **{issue.check}**: {issue.message}\n"
                if issue.suggestion:
                    report += f"   建议: {issue.suggestion}\n"
        
        if output_path:
            Path(output_path).write_text(report, encoding='utf-8')
        
        return report


def main():
    """示例用法"""
    validator = MappingValidator()
    
    # 示例1: 正确的映射
    source1 = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    target1 = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    result1 = validator.validate(source1, target1)
    print("示例1: 正确映射")
    print(f"  有效: {result1.valid}")
    print(f"  问题数: {len(result1.issues)}")
    
    # 示例2: 有问题的映射
    source2 = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name", "email"]
    }
    
    target2 = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"]  # 丢失了 email
        "minimum": 100,  # 错误: 范围不合理
        "maximum": 10
    }
    
    result2 = validator.validate(source2, target2)
    print("\n示例2: 有问题的映射")
    print(f"  有效: {result2.valid}")
    print(f"  问题数: {len(result2.issues)}")
    for issue in result2.issues:
        print(f"  - [{issue.severity.value}] {issue.message}")
    
    # 生成报告
    report = validator.generate_report(result2, "validation_report.md")
    print("\n✅ 报告已保存到: validation_report.md")


if __name__ == "__main__":
    main()
