#!/usr/bin/env python3
"""
Auto Fix Tool
=============

自动修复工具，支持：
- 常见Schema问题自动修复
- 格式标准化
- 引用修复
- 类型推断
- 最佳实践应用

Version: 2.2.0
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path


class FixType(Enum):
    """修复类型"""
    SCHEMA_VERSION = "schema_version"
    FORMATTING = "formatting"
    REFERENCE = "reference"
    TYPE_INFERENCE = "type_inference"
    BEST_PRACTICE = "best_practice"
    VALIDATION = "validation"


@dataclass
class FixResult:
    """修复结果"""
    fixed: bool
    original: Any
    fixed_value: Any
    fix_type: FixType
    description: str
    warnings: List[str] = field(default_factory=list)


@dataclass
class AutoFixReport:
    """自动修复报告"""
    file_path: str
    total_issues: int
    fixed_issues: int
    remaining_issues: int
    fixes: List[FixResult] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class SchemaAutoFixer:
    """Schema自动修复器"""
    
    # 最新的JSON Schema版本
    LATEST_SCHEMA_VERSION = "https://json-schema.org/draft/2025-01/schema"
    
    # 常见的format值
    KNOWN_FORMATS = {
        "date-time", "date", "time", "duration",
        "email", "idn-email",
        "hostname", "idn-hostname",
        "ipv4", "ipv6",
        "uri", "uri-reference", "iri", "iri-reference",
        "uuid", "uri-template",
        "json-pointer", "relative-json-pointer",
        "regex"
    }
    
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.fixes_applied: List[FixResult] = []
    
    def fix(self, schema: Dict, aggressive: bool = False) -> Tuple[Dict, AutoFixReport]:
        """
        自动修复Schema
        
        Args:
            schema: 待修复的Schema
            aggressive: 是否启用激进修复模式
        
        Returns:
            (修复后的Schema, 修复报告)
        """
        self.fixes_applied = []
        fixed_schema = schema.copy()
        
        # 1. 修复Schema版本
        fixed_schema = self._fix_schema_version(fixed_schema)
        
        # 2. 修复格式问题
        fixed_schema = self._fix_formatting(fixed_schema)
        
        # 3. 修复引用
        fixed_schema = self._fix_references(fixed_schema)
        
        # 4. 推断类型
        if aggressive:
            fixed_schema = self._infer_types(fixed_schema)
        
        # 5. 应用最佳实践
        fixed_schema = self._apply_best_practices(fixed_schema)
        
        # 6. 验证并修复
        fixed_schema = self._validate_and_fix(fixed_schema)
        
        # 生成报告
        report = AutoFixReport(
            file_path="schema.json",
            total_issues=len(self.fixes_applied) + len([f for f in self.fixes_applied if f.warnings]),
            fixed_issues=len([f for f in self.fixes_applied if f.fixed]),
            remaining_issues=len([f for f in self.fixes_applied if f.warnings]),
            fixes=self.fixes_applied,
            suggestions=self._generate_suggestions(fixed_schema)
        )
        
        return fixed_schema, report
    
    def _fix_schema_version(self, schema: Dict) -> Dict:
        """修复Schema版本"""
        if "$schema" not in schema:
            schema["$schema"] = self.LATEST_SCHEMA_VERSION
            self.fixes_applied.append(FixResult(
                fixed=True,
                original=None,
                fixed_value=self.LATEST_SCHEMA_VERSION,
                fix_type=FixType.SCHEMA_VERSION,
                description="添加缺失的$schema声明"
            ))
        elif schema["$schema"] == "http://json-schema.org/draft-04/schema#":
            old_version = schema["$schema"]
            schema["$schema"] = self.LATEST_SCHEMA_VERSION
            self.fixes_applied.append(FixResult(
                fixed=True,
                original=old_version,
                fixed_value=self.LATEST_SCHEMA_VERSION,
                fix_type=FixType.SCHEMA_VERSION,
                description="升级过时的Schema版本 (draft-04 → 2025-01)"
            ))
        
        return schema
    
    def _fix_formatting(self, schema: Dict) -> Dict:
        """修复格式问题"""
        # 确保properties在object类型下
        if "properties" in schema and "type" not in schema:
            schema["type"] = "object"
            self.fixes_applied.append(FixResult(
                fixed=True,
                original=None,
                fixed_value="object",
                fix_type=FixType.FORMATTING,
                description="添加缺失的type: object (因为有properties)"
            ))
        
        # 确保items在array类型下
        if "items" in schema and schema.get("type") != "array":
            schema["type"] = "array"
            self.fixes_applied.append(FixResult(
                fixed=True,
                original=None,
                fixed_value="array",
                fix_type=FixType.FORMATTING,
                description="添加缺失的type: array (因为有items)"
            ))
        
        return schema
    
    def _fix_references(self, schema: Dict, root: Dict = None) -> Dict:
        """修复引用"""
        if root is None:
            root = schema
        
        if "$ref" in schema:
            ref = schema["$ref"]
            # 修复definitions到$defs
            if "#/definitions/" in ref and "$defs" in root:
                old_ref = ref
                new_ref = ref.replace("#/definitions/", "#/$defs/")
                schema["$ref"] = new_ref
                self.fixes_applied.append(FixResult(
                    fixed=True,
                    original=old_ref,
                    fixed_value=new_ref,
                    fix_type=FixType.REFERENCE,
                    description="更新引用路径: definitions → $defs"
                ))
        
        # 递归处理
        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = self._fix_references(value, root)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        value[i] = self._fix_references(item, root)
        
        return schema
    
    def _infer_types(self, schema: Dict) -> Dict:
        """推断并修复类型"""
        if "type" not in schema and "enum" in schema:
            # 从enum推断类型
            enum_values = schema["enum"]
            if enum_values:
                inferred_type = self._infer_type_from_values(enum_values)
                schema["type"] = inferred_type
                self.fixes_applied.append(FixResult(
                    fixed=True,
                    original=None,
                    fixed_value=inferred_type,
                    fix_type=FixType.TYPE_INFERENCE,
                    description=f"从enum值推断类型: {inferred_type}"
                ))
        
        # 递归处理
        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = self._infer_types(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        value[i] = self._infer_types(item)
        
        return schema
    
    def _infer_type_from_values(self, values: List[Any]) -> str:
        """从值列表推断类型"""
        types = set(type(v).__name__ for v in values)
        
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object"
        }
        
        if len(types) == 1:
            py_type = list(types)[0]
            return type_mapping.get(py_type, "string")
        elif types == {"int", "float"}:
            return "number"
        else:
            return "string"  # 默认
    
    def _apply_best_practices(self, schema: Dict) -> Dict:
        """应用最佳实践"""
        # 添加描述（如果缺失）
        if "description" not in schema and "title" in schema:
            schema["description"] = f"Schema for {schema['title']}"
            self.fixes_applied.append(FixResult(
                fixed=True,
                original=None,
                fixed_value=schema["description"],
                fix_type=FixType.BEST_PRACTICE,
                description="添加缺失的description"
            ))
        
        # 添加$id（如果缺失）
        if "$id" not in schema and "$schema" in schema:
            schema["$id"] = "https://example.com/schema.json"
            self.fixes_applied.append(FixResult(
                fixed=True,
                original=None,
                fixed_value=schema["$id"],
                fix_type=FixType.BEST_PRACTICE,
                description="添加缺失的$id"
            ))
        
        # 验证format值
        if "format" in schema:
            fmt = schema["format"]
            if fmt not in self.KNOWN_FORMATS:
                self.fixes_applied.append(FixResult(
                    fixed=False,
                    original=fmt,
                    fixed_value=None,
                    fix_type=FixType.VALIDATION,
                    description=f"未知的format值: {fmt}",
                    warnings=[f"'{fmt}' 不是标准format值，建议使用: {', '.join(list(self.KNOWN_FORMATS)[:5])}..."]
                ))
        
        # 递归处理
        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = self._apply_best_practices(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        value[i] = self._apply_best_practices(item)
        
        return schema
    
    def _validate_and_fix(self, schema: Dict) -> Dict:
        """验证并修复"""
        # 检查循环引用
        if self._has_circular_reference(schema):
            self.fixes_applied.append(FixResult(
                fixed=False,
                original=None,
                fixed_value=None,
                fix_type=FixType.VALIDATION,
                description="检测到循环引用",
                warnings=["Schema中存在循环引用，需要手动重构"]
            ))
        
        # 检查最小值/最大值合理性
        if "minimum" in schema and "maximum" in schema:
            if schema["minimum"] > schema["maximum"]:
                # 交换
                min_val = schema["minimum"]
                max_val = schema["maximum"]
                schema["minimum"] = max_val
                schema["maximum"] = min_val
                self.fixes_applied.append(FixResult(
                    fixed=True,
                    original=f"min: {min_val}, max: {max_val}",
                    fixed_value=f"min: {max_val}, max: {min_val}",
                    fix_type=FixType.VALIDATION,
                    description="修复不合理的范围 (minimum > maximum)"
                ))
        
        return schema
    
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
    
    def _generate_suggestions(self, schema: Dict) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if "examples" not in schema:
            suggestions.append("考虑添加'examples'字段以提供更好的文档")
        
        if "default" not in schema and "const" not in schema:
            suggestions.append("考虑添加'default'值")
        
        if schema.get("type") == "object" and "additionalProperties" not in schema:
            suggestions.append("考虑显式设置'additionalProperties'以明确是否允许额外属性")
        
        return suggestions
    
    def fix_file(self, file_path: str, output_path: str = None) -> AutoFixReport:
        """修复文件中的Schema"""
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        
        # 解析JSON
        try:
            schema = json.loads(content)
        except json.JSONDecodeError as e:
            return AutoFixReport(
                file_path=file_path,
                total_issues=1,
                fixed_issues=0,
                remaining_issues=1,
                fixes=[],
                suggestions=[f"JSON解析错误: {e}"]
            )
        
        # 修复
        fixed_schema, report = self.fix(schema)
        report.file_path = file_path
        
        # 保存
        output = output_path or file_path
        Path(output).write_text(
            json.dumps(fixed_schema, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return report


def main():
    """示例用法"""
    fixer = SchemaAutoFixer()
    
    # 示例：有问题的Schema
    problematic_schema = {
        # 缺少$schema
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "format": "unknown-format"  # 未知format
            },
            "count": {
                "type": "integer",
                "minimum": 100,  # 不合理的范围
                "maximum": 10
            },
            "status": {
                "enum": ["active", "inactive"]  # 缺少type
            }
        },
        # 缺少title和description
        "definitions": {  # 旧版语法
            "address": {
                "type": "object"
            }
        }
    }
    
    print("原始Schema:")
    print(json.dumps(problematic_schema, indent=2)[:500])
    
    # 自动修复
    fixed_schema, report = fixer.fix(problematic_schema, aggressive=True)
    
    print("\n\n修复后的Schema:")
    print(json.dumps(fixed_schema, indent=2)[:800])
    
    print(f"\n\n修复报告:")
    print(f"  总问题数: {report.total_issues}")
    print(f"  已修复: {report.fixed_issues}")
    print(f"  剩余问题: {report.remaining_issues}")
    
    print(f"\n修复详情:")
    for fix in report.fixes:
        status = "✅" if fix.fixed else "⚠️"
        print(f"  {status} [{fix.fix_type.value}] {fix.description}")
        if fix.warnings:
            for w in fix.warnings:
                print(f"     ⚠️ {w}")
    
    if report.suggestions:
        print(f"\n建议:")
        for s in report.suggestions:
            print(f"  💡 {s}")


if __name__ == "__main__":
    main()
