"""
Tests for Schema Diff Tool
==========================

测试覆盖：
- 基本差异检测
- 变更类型识别
- 影响级别计算
- HTML报告生成

Version: 2.2.0
"""

import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from schema_diff_tool import (
    SchemaDiffer, DiffNode, DiffReport,
    ChangeType, ImpactLevel
)


class TestSchemaDiffer:
    """Schema差异比较器测试"""
    
    @pytest.fixture
    def differ(self):
        return SchemaDiffer()
    
    def test_no_changes(self, differ):
        """测试无变更"""
        schema = {"type": "object"}
        report = differ.diff(schema, schema)
        
        assert len(report.changes) == 0
        assert report.summary.get("unchanged", 0) == 0  # 无变更不记录
    
    def test_added_property(self, differ):
        """测试新增属性"""
        old = {"type": "object"}
        new = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        report = differ.diff(old, new)
        
        added = [c for c in report.changes if c.change_type == ChangeType.ADDED]
        assert len(added) > 0
    
    def test_removed_property(self, differ):
        """测试删除属性"""
        old = {"type": "object", "properties": {"name": {"type": "string"}}}
        new = {"type": "object"}
        
        report = differ.diff(old, new)
        
        removed = [c for c in report.changes if c.change_type == ChangeType.REMOVED]
        assert len(removed) > 0
    
    def test_modified_value(self, differ):
        """测试修改值"""
        old = {"type": "string"}
        new = {"type": "integer"}
        
        report = differ.diff(old, new)
        
        modified = [c for c in report.changes if c.change_type == ChangeType.MODIFIED]
        assert len(modified) == 1
        assert modified[0].old_value == "string"
        assert modified[0].new_value == "integer"
    
    def test_nested_changes(self, differ):
        """测试嵌套变更"""
        old = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }
        new = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}  # 新增
                    }
                }
            }
        }
        
        report = differ.diff(old, new)
        
        # 应该检测到age的添加
        added_paths = [c.path for c in report.changes if c.change_type == ChangeType.ADDED]
        assert any("age" in p for p in added_paths)
    
    def test_impact_level_breaking(self, differ):
        """测试破坏性变更影响级别"""
        old = {"required": ["name", "email"]}
        new = {"required": ["name"]}
        
        report = differ.diff(old, new)
        
        breaking = [c for c in report.changes if c.impact == ImpactLevel.BREAKING]
        assert len(breaking) > 0
    
    def test_impact_level_high(self, differ):
        """测试高影响变更"""
        old = {"type": "string"}
        new = {"type": "integer"}
        
        report = differ.diff(old, new)
        
        high = [c for c in report.changes if c.impact == ImpactLevel.HIGH]
        assert len(high) > 0
    
    def test_summary_generation(self, differ):
        """测试摘要生成"""
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 3, "c": 4}
        
        report = differ.diff(old, new)
        
        assert "added" in report.summary or "modified" in report.summary
    
    def test_migration_guide_generation(self, differ):
        """测试迁移指南生成"""
        old = {"required": ["name"]}
        new = {"required": ["name", "email"]}
        
        report = differ.diff(old, new)
        
        assert len(report.migration_guide) > 0
    
    def test_html_report_generation(self, differ, tmp_path):
        """测试HTML报告生成"""
        old = {"type": "string"}
        new = {"type": "integer"}
        
        report = differ.diff(old, new)
        output_file = tmp_path / "diff_report.html"
        
        result = differ.generate_html_report(report, str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "Schema Diff Report" in content
        assert "integer" in content


class TestImpactAnalysis:
    """影响分析测试"""
    
    @pytest.fixture
    def differ(self):
        return SchemaDiffer()
    
    def test_no_breaking_changes(self, differ):
        """测试无破坏性变更"""
        old = {"description": "Old description"}
        new = {"description": "New description"}
        
        report = differ.diff(old, new)
        
        assert report.impact_analysis["breaking_changes"] == 0
        assert report.impact_analysis["recommendation"] == "向后兼容"
    
    def test_with_breaking_changes(self, differ):
        """测试有破坏性变更"""
        old = {"required": ["id", "name"]}
        new = {"required": ["id"]}
        
        report = differ.diff(old, new)
        
        assert report.impact_analysis["breaking_changes"] > 0
        assert "版本升级" in report.impact_analysis["recommendation"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
