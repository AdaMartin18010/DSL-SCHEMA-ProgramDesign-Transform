"""
Tests for Schema Visualizer
===========================

测试覆盖：
- ER图生成
- 类图生成
- Mermaid导出
- PlantUML导出
- D3.js JSON导出
- HTML可视化

Version: 2.1.0
"""

import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from schema_visualizer import (
    SchemaGraphBuilder, SchemaComparisonVisualizer,
    GraphNode, GraphEdge
)


class TestSchemaGraphBuilder:
    """Schema图构建器测试"""
    
    @pytest.fixture
    def builder(self):
        return SchemaGraphBuilder()
    
    @pytest.fixture
    def sample_schema(self):
        return {
            "type": "object",
            "title": "Product",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "category": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    }
                }
            }
        }
    
    def test_build_from_json_schema(self, builder, sample_schema):
        """测试从JSON Schema构建图"""
        builder.build_from_json_schema(sample_schema, "Product")
        
        assert len(builder.nodes) > 0
        assert len(builder.edges) > 0
        
        # 检查是否有实体节点
        entity_nodes = [n for n in builder.nodes if n.type == "entity"]
        assert len(entity_nodes) >= 1
    
    def test_to_mermaid(self, builder, sample_schema):
        """测试生成Mermaid图"""
        builder.build_from_json_schema(sample_schema, "Product")
        mermaid = builder.to_mermaid()
        
        assert "erDiagram" in mermaid
        assert "Product" in mermaid or "product" in mermaid.lower()
    
    def test_to_plantuml(self, builder, sample_schema):
        """测试生成PlantUML图"""
        builder.build_from_json_schema(sample_schema, "Product")
        plantuml = builder.to_plantuml()
        
        assert "@startuml" in plantuml
        assert "@enduml" in plantuml
        assert "class" in plantuml
    
    def test_to_d3_json(self, builder, sample_schema):
        """测试生成D3.js JSON"""
        builder.build_from_json_schema(sample_schema, "Product")
        d3_data = builder.to_d3_json()
        
        assert "nodes" in d3_data
        assert "links" in d3_data
        assert len(d3_data["nodes"]) > 0
        assert len(d3_data["links"]) > 0
    
    def test_to_html_visualization(self, builder, sample_schema, tmp_path):
        """测试生成HTML可视化"""
        builder.build_from_json_schema(sample_schema, "Product")
        html = builder.to_html_visualization("Test Visualization")
        
        assert "<!DOCTYPE html>" in html
        assert "d3.v7" in html or "d3js.org" in html
        assert "Test Visualization" in html
        assert "graph" in html.lower()


class TestSchemaComparisonVisualizer:
    """Schema对比可视化器测试"""
    
    @pytest.fixture
    def visualizer(self):
        return SchemaComparisonVisualizer()
    
    def test_generate_diff_html(self, visualizer, tmp_path):
        """测试生成差异对比HTML"""
        schema1 = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema2 = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
        
        html = visualizer.generate_diff_html(schema1, schema2, "Schema Diff")
        
        assert "<!DOCTYPE html>" in html
        assert "Schema Diff" in html
        assert "container" in html
    
    def test_compare_schemas_added(self, visualizer):
        """测试检测新增字段"""
        s1 = {"type": "object"}
        s2 = {"type": "object", "properties": {"name": {}}}
        
        diff = visualizer._compare_schemas(s1, s2)
        
        added = [d for d in diff if d["type"] == "added"]
        assert len(added) > 0
    
    def test_compare_schemas_removed(self, visualizer):
        """测试检测删除字段"""
        s1 = {"type": "object", "properties": {"name": {}}}
        s2 = {"type": "object"}
        
        diff = visualizer._compare_schemas(s1, s2)
        
        removed = [d for d in diff if d["type"] == "removed"]
        assert len(removed) > 0
    
    def test_compare_schemas_modified(self, visualizer):
        """测试检测修改字段"""
        s1 = {"type": "object", "title": "Old"}
        s2 = {"type": "object", "title": "New"}
        
        diff = visualizer._compare_schemas(s1, s2)
        
        modified = [d for d in diff if d["type"] == "modified"]
        assert len(modified) > 0
        assert modified[0]["old"] == "Old"
        assert modified[0]["new"] == "New"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
