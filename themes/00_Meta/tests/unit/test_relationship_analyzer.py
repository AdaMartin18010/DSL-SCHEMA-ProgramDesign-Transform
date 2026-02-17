"""
Tests for Relationship Analyzer
===============================

测试覆盖：
- 实体提取
- 相似度计算
- 关系发现
- 层次分配
- 导出功能

Version: 2.2.0
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from relationship_analyzer import (
    ModelRelationshipAnalyzer, ModelEntity, Relationship,
    GraphNode, GraphEdge
)


class TestModelRelationshipAnalyzer:
    """模型关联分析器测试"""
    
    @pytest.fixture
    def analyzer(self, tmp_path):
        # 创建临时项目结构
        themes_dir = tmp_path / "themes"
        themes_dir.mkdir()
        
        # 创建测试主题
        theme1 = themes_dir / "01_Test"
        theme1.mkdir()
        concepts = theme1 / "Concepts"
        concepts.mkdir()
        (concepts / "concept1.md").write_text("# Concept 1")
        
        analyzer = ModelRelationshipAnalyzer(str(tmp_path))
        return analyzer
    
    def test_extract_entities(self, analyzer):
        """测试实体提取"""
        analyzer._extract_entities()
        
        assert len(analyzer.entities) > 0
        assert any(e.type == "concept" for e in analyzer.entities.values())
    
    def test_calculate_similarity_same_name(self, analyzer):
        """测试相同名称的相似度"""
        e1 = ModelEntity(id="e1", name="test", type="concept")
        e2 = ModelEntity(id="e2", name="test", type="concept")
        
        sim = analyzer._calculate_similarity(e1, e2)
        
        assert sim > 0.5  # 相同名称应该有高相似度
    
    def test_calculate_similarity_different_names(self, analyzer):
        """测试不同名称的相似度"""
        e1 = ModelEntity(id="e1", name="abc", type="concept")
        e2 = ModelEntity(id="e2", name="xyz", type="concept")
        
        sim = analyzer._calculate_similarity(e1, e2)
        
        assert sim < 0.5  # 不同名称应该有低相似度
    
    def test_string_similarity_identical(self, analyzer):
        """测试相同字符串的相似度"""
        sim = analyzer._string_similarity("test", "test")
        assert sim == 1.0
    
    def test_string_similarity_different(self, analyzer):
        """测试不同字符串的相似度"""
        sim = analyzer._string_similarity("abc", "xyz")
        assert sim < 0.5
    
    def test_determine_relationship_type_specialization(self, analyzer):
        """测试特化关系识别"""
        e1 = ModelEntity(id="e1", name="user", type="concept")
        e2 = ModelEntity(id="e2", name="admin_user", type="concept")
        
        rel_type = analyzer._determine_relationship_type(e1, e2)
        
        assert rel_type == "specialization"
    
    def test_determine_relationship_type_composition(self, analyzer):
        """测试组合关系识别"""
        e1 = ModelEntity(id="e1", name="part", type="concept", 
                        source_file="themes/01_Test/Concepts/part.md")
        e2 = ModelEntity(id="e2", name="whole", type="concept",
                        source_file="themes/01_Test/Concepts/whole.md")
        
        rel_type = analyzer._determine_relationship_type(e1, e2)
        
        assert rel_type == "composition"
    
    def test_export_to_graph_json(self, analyzer, tmp_path):
        """测试导出为图JSON"""
        # 添加一些测试实体和关系
        analyzer.entities = {
            "e1": ModelEntity(id="e1", name="Entity1", type="concept"),
            "e2": ModelEntity(id="e2", name="Entity2", type="concept")
        }
        
        output_file = tmp_path / "graph.json"
        graph = analyzer.export_to_graph_json(str(output_file))
        
        assert output_file.exists()
        assert "nodes" in graph
        assert "links" in graph
        assert len(graph["nodes"]) == 2
    
    def test_export_to_mermaid(self, analyzer):
        """测试导出为Mermaid"""
        analyzer.entities = {
            "e1": ModelEntity(id="e1", name="Entity1", type="concept"),
        }
        analyzer.hierarchy = {
            3: type('obj', (object,), {
                'name': 'Data Model',
                'entities': [analyzer.entities["e1"]]
            })()
        }
        
        mermaid = analyzer.export_to_mermaid()
        
        assert "graph TB" in mermaid
        assert "Entity1" in mermaid


class TestHierarchyMapping:
    """层次映射测试"""
    
    @pytest.fixture
    def analyzer(self):
        return ModelRelationshipAnalyzer()
    
    def test_assign_hierarchy_level_concept(self, analyzer):
        """测试概念实体的层次分配"""
        entity = ModelEntity(
            id="e1", 
            name="test", 
            type="concept",
            source_file="themes/01_Test/Concepts/test.md"
        )
        
        level = analyzer._assign_hierarchy_level(entity)
        
        assert level == 2  # Meta-Model层
    
    def test_assign_hierarchy_level_tool(self, analyzer):
        """测试工具实体的层次分配"""
        entity = ModelEntity(
            id="e1",
            name="validator",
            type="tool",
            source_file="themes/00_Meta/Tools/validator.py"
        )
        
        level = analyzer._assign_hierarchy_level(entity)
        
        assert level == 3  # Data Model层


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
