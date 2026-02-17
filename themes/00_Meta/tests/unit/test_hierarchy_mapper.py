"""
Tests for Hierarchy Mapper
==========================

测试覆盖：
- 规则注册
- 单级映射
- 多级映射
- 转换函数
- 验证器

Version: 2.2.0
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from hierarchy_mapper import (
    HierarchyMappingEngine, MappingLevel, MappingResult,
    MappingRule
)


class TestHierarchyMappingEngine:
    """层次映射引擎测试"""
    
    @pytest.fixture
    def engine(self):
        return HierarchyMappingEngine()
    
    def test_register_rule(self, engine):
        """测试注册规则"""
        rule = MappingRule(
            name="test_rule",
            source_level=MappingLevel.L1_FOUNDATION,
            target_level=MappingLevel.L2_META_MODEL,
            condition=lambda x: True,
            transform=lambda x: x
        )
        
        engine.register_rule(rule)
        
        key = (MappingLevel.L1_FOUNDATION, MappingLevel.L2_META_MODEL)
        assert key in engine.rules
    
    def test_map_single_level(self, engine):
        """测试单级映射"""
        test_set = {"a", "b", "c"}
        
        result = engine.map(test_set, MappingLevel.L1_FOUNDATION, MappingLevel.L2_META_MODEL)
        
        assert result.success is True
        assert result.target is not None
        assert result.target.get("type") == "array"
    
    def test_map_multi_level(self, engine):
        """测试多级映射"""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        result = engine.map(schema, MappingLevel.L2_META_MODEL, MappingLevel.L4_SERVICE_MODEL)
        
        assert result.success is True
        assert len(result.trace) > 2  # 应该有多个步骤
    
    def test_map_no_rules(self, engine):
        """测试无规则时的映射"""
        # 尝试映射一个没有规则定义的路径
        result = engine.map({}, MappingLevel.L5_APPLICATION, MappingLevel.L1_FOUNDATION)
        
        assert result.success is False
        assert "No mapping rules" in result.issues[0]
    
    def test_set_to_schema_type(self, engine):
        """测试集合到Schema类型的转换"""
        test_set = {"item1", "item2"}
        
        result = engine._set_to_schema_type(test_set)
        
        assert result["type"] == "array"
        assert result["uniqueItems"] is True
    
    def test_json_schema_to_ontology(self, engine):
        """测试JSON Schema到本体的转换"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        result = engine._json_schema_to_ontology(schema)
        
        assert "@context" in result
        assert "owl:Class" in str(result.get("@type", ""))
    
    def test_entity_to_api_resource(self, engine):
        """测试实体到API资源的转换"""
        entity = {
            "entityType": "User",
            "attributes": ["name", "email"]
        }
        
        result = engine._entity_to_api_resource(entity)
        
        assert result["resource"] == "user"
        assert "endpoints" in result
        assert "GET" in result["endpoints"]


class TestMappingResult:
    """映射结果测试"""
    
    def test_mapping_result_creation(self):
        """测试映射结果创建"""
        result = MappingResult(
            success=True,
            source={"test": "data"},
            target={"mapped": "data"},
            trace=["step1", "step2"]
        )
        
        assert result.success is True
        assert len(result.trace) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
