"""
Tests for Auto Fix Tool
=======================

测试覆盖：
- Schema版本修复
- 格式修复
- 引用修复
- 类型推断
- 最佳实践应用

Version: 2.2.0
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from auto_fix_tool import (
    SchemaAutoFixer, FixResult, AutoFixReport,
    FixType
)


class TestSchemaAutoFixer:
    """Schema自动修复器测试"""
    
    @pytest.fixture
    def fixer(self):
        return SchemaAutoFixer()
    
    def test_fix_missing_schema_version(self, fixer):
        """测试修复缺失的Schema版本"""
        schema = {"type": "object"}
        
        fixed, report = fixer.fix(schema)
        
        assert "$schema" in fixed
        assert any(f.fix_type == FixType.SCHEMA_VERSION for f in report.fixes)
    
    def test_fix_outdated_schema_version(self, fixer):
        """测试修复过时的Schema版本"""
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object"
        }
        
        fixed, report = fixer.fix(schema)
        
        assert "2025-01" in fixed["$schema"]
    
    def test_fix_missing_object_type(self, fixer):
        """测试修复缺失的object类型"""
        schema = {"properties": {"name": {"type": "string"}}}
        
        fixed, report = fixer.fix(schema)
        
        assert fixed.get("type") == "object"
    
    def test_fix_missing_array_type(self, fixer):
        """测试修复缺失的array类型"""
        schema = {"items": {"type": "string"}}
        
        fixed, report = fixer.fix(schema)
        
        assert fixed.get("type") == "array"
    
    def test_fix_definitions_to_defs(self, fixer):
        """测试修复definitions到$defs"""
        schema = {
            "$schema": "https://json-schema.org/draft/2025-01/schema",
            "$defs": {"address": {"type": "object"}},
            "properties": {
                "home": {"$ref": "#/definitions/address"}  # 旧引用
            }
        }
        
        fixed, report = fixer.fix(schema)
        
        assert "#/$defs/address" in str(fixed)
    
    def test_fix_invalid_range(self, fixer):
        """测试修复无效的范围"""
        schema = {
            "type": "integer",
            "minimum": 100,
            "maximum": 10
        }
        
        fixed, report = fixer.fix(schema)
        
        assert fixed["minimum"] <= fixed["maximum"]
    
    def test_infer_type_from_enum(self, fixer):
        """测试从enum推断类型"""
        schema = {"enum": ["a", "b", "c"]}
        
        fixed, report = fixer.fix(schema, aggressive=True)
        
        assert fixed.get("type") == "string"
    
    def test_add_missing_description(self, fixer):
        """测试添加缺失的描述"""
        schema = {
            "title": "User",
            "type": "object"
        }
        
        fixed, report = fixer.fix(schema)
        
        assert "description" in fixed
    
    def test_report_generation(self, fixer):
        """测试报告生成"""
        schema = {"type": "object"}  # 缺少$schema
        
        fixed, report = fixer.fix(schema)
        
        assert report.fixed_issues > 0
        assert len(report.fixes) > 0
    
    def test_safe_mode_respects_existing(self, fixer):
        """测试安全模式尊重现有值"""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object"
        }
        
        fixed, report = fixer.fix(schema)
        
        # 不应该降级版本
        assert "2020-12" in fixed["$schema"]


class TestFixFile:
    """文件修复测试"""
    
    @pytest.fixture
    def fixer(self):
        return SchemaAutoFixer()
    
    def test_fix_valid_json_file(self, fixer, tmp_path):
        """测试修复有效的JSON文件"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"type": "object"}')
        
        report = fixer.fix_file(str(json_file))
        
        assert report.total_issues >= 0
    
    def test_fix_invalid_json_file(self, fixer, tmp_path):
        """测试修复无效的JSON文件"""
        json_file = tmp_path / "invalid.json"
        json_file.write_text('{"type": "object",}')  # 无效的JSON
        
        report = fixer.fix_file(str(json_file))
        
        assert report.total_issues > 0
        assert "解析错误" in str(report.suggestions) or "parse" in str(report.suggestions).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
