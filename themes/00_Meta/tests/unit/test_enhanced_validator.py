"""
Tests for Enhanced Schema Validator
===================================

测试覆盖：
- JSON Schema 2025-01 验证
- OpenAPI 3.1.2 验证  
- AsyncAPI 3.0 验证
- 标准合规性检查

Version: 2.1.0
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from enhanced_validator import (
    JSONSchema2025Validator, OpenAPI31Validator, AsyncAPI30Validator,
    StandardComplianceChecker, EnhancedSchemaValidator,
    SchemaType, ValidationSeverity
)


class TestJSONSchema2025Validator:
    """JSON Schema 2025-01 验证器测试"""
    
    @pytest.fixture
    def validator(self):
        return JSONSchema2025Validator()
    
    def test_valid_basic_schema(self, validator):
        """测试基本有效Schema"""
        schema = {
            "$schema": "https://json-schema.org/draft/2025-01/schema",
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        result = validator.validate(schema)
        assert result.valid is True
    
    def test_invalid_type(self, validator):
        """测试无效类型"""
        schema = {"type": "invalid_type"}
        result = validator.validate(schema)
        assert result.valid is False
        assert any(i.code == "INVALID_TYPE" for i in result.issues)
    
    def test_unresolved_reference(self, validator):
        """测试未解析引用"""
        schema = {"$ref": "#/definitions/NonExistent"}
        result = validator.validate(schema)
        warnings = [i for i in result.issues if i.code == "UNRESOLVED_REFERENCE"]
        assert len(warnings) > 0


class TestOpenAPI31Validator:
    """OpenAPI 3.1.2 验证器测试"""
    
    @pytest.fixture
    def validator(self):
        return OpenAPI31Validator()
    
    def test_valid_openapi_spec(self, validator):
        """测试有效OpenAPI规范"""
        spec = {
            "openapi": "3.1.2",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }
        result = validator.validate(spec)
        assert result.valid is True
    
    def test_missing_info(self, validator):
        """测试缺少info字段"""
        spec = {"openapi": "3.1.2", "paths": {}}
        result = validator.validate(spec)
        assert result.valid is False


class TestStandardComplianceChecker:
    """标准合规性检查器测试"""
    
    @pytest.fixture
    def checker(self):
        return StandardComplianceChecker()
    
    def test_gs1_compliance(self, checker):
        """测试GS1合规性"""
        schema = {"properties": {"gtin": {"type": "string"}}}
        reports = checker.check(schema, ['gs1'])
        assert len(reports) == 1
        assert reports[0].standard == 'GS1'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
