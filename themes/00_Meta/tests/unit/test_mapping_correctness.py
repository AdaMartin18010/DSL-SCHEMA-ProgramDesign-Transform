"""
Tests for Mapping Correctness Verifier
======================================

测试覆盖：
- 语法正确性验证
- 语义保持性验证
- 完备性验证
- 形式化证明生成

Version: 2.3.0
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from mapping_correctness_verifier import (
    MappingCorrectnessVerifier, SyntaxCorrectnessVerifier,
    SemanticPreservationVerifier, CompletenessVerifier,
    VerificationType, VerificationStatus
)


class TestSyntaxCorrectnessVerifier:
    """语法正确性验证器测试"""
    
    def test_valid_json_schema(self):
        """测试有效JSON Schema"""
        verifier = SyntaxCorrectnessVerifier("json_schema")
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        result = verifier.verify({}, schema)
        
        assert result.status == VerificationStatus.PASSED
    
    def test_invalid_type(self):
        """测试无效类型"""
        verifier = SyntaxCorrectnessVerifier("json_schema")
        schema = {"type": "invalid_type"}
        
        result = verifier.verify({}, schema)
        
        assert result.status == VerificationStatus.FAILED
    
    def test_circular_reference(self):
        """测试循环引用"""
        verifier = SyntaxCorrectnessVerifier("json_schema")
        a = {}
        b = {"ref": a}
        a["ref"] = b  # 循环引用
        
        result = verifier.verify({}, a)
        
        assert result.status == VerificationStatus.FAILED


class TestSemanticPreservationVerifier:
    """语义保持性验证器测试"""
    
    @pytest.fixture
    def verifier(self):
        return SemanticPreservationVerifier()
    
    def test_type_preservation_integer_to_number(self, verifier):
        """测试integer到number的类型保持"""
        source = {"type": "integer"}
        target = {"type": "number"}
        
        result = verifier.verify(source, target)
        
        assert result.status == VerificationStatus.PASSED
    
    def test_type_preservation_string_to_integer(self, verifier):
        """测试string到integer的类型丢失"""
        source = {"type": "string"}
        target = {"type": "integer"}
        
        result = verifier.verify(source, target)
        
        # 这应该警告或失败，因为语义不兼容
        assert result.status in [VerificationStatus.FAILED, VerificationStatus.WARNING]
    
    def test_constraint_preservation_required(self, verifier):
        """测试required约束保持"""
        source = {"required": ["name"]}
        target = {"required": ["name"]}
        
        result = verifier.verify(source, target)
        
        assert result.status == VerificationStatus.PASSED


class TestCompletenessVerifier:
    """完备性验证器测试"""
    
    @pytest.fixture
    def verifier(self):
        return CompletenessVerifier()
    
    def test_complete_mapping(self, verifier):
        """测试完备映射"""
        source = {"a": 1, "b": 2}
        target = {"a": 1, "b": 2, "c": 3}  # 包含所有源元素
        
        result = verifier.verify(source, target)
        
        assert result.status == VerificationStatus.PASSED
    
    def test_incomplete_mapping(self, verifier):
        """测试不完备映射"""
        source = {"a": 1, "b": 2}
        target = {"a": 1}  # 缺少 b
        
        result = verifier.verify(source, target)
        
        assert result.status == VerificationStatus.FAILED


class TestMappingCorrectnessVerifier:
    """映射正确性验证器主类测试"""
    
    @pytest.fixture
    def verifier(self):
        return MappingCorrectnessVerifier()
    
    def test_verify_correct_mapping(self, verifier):
        """测试验证正确的映射"""
        source = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        target = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        
        report = verifier.verify_mapping(source, target, "test_mapping")
        
        assert report.summary["passed"] > 0
        assert report.mapping_name == "test_mapping"
    
    def test_generate_report(self, verifier):
        """测试生成报告"""
        source = {"type": "string"}
        target = {"type": "string"}
        
        report = verifier.verify_mapping(source, target)
        
        output = verifier.generate_report(report)
        
        assert "Mapping Correctness Verification Report" in output
        assert str(report.summary["total"]) in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
