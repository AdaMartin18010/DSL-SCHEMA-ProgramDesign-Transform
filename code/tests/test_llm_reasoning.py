"""
LLM推理引擎完整测试套件

包含单元测试、集成测试和Mock测试
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import sys

# 导入被测模块
from llm_reasoning.llm_interface import ReasoningResult
from llm_reasoning.embedding import KGEmbedding, EmbeddingStore
from llm_reasoning.chain_builder import ReasoningChainBuilder, ReasoningStep
from llm_reasoning.validator import ResultValidator, ValidationResult


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm():
    """创建Mock LLM实例"""
    llm = Mock()
    llm.generate.return_value = "测试回答"
    llm.embed.return_value = [0.1] * 1536
    
    # 模拟reason方法
    def mock_reason(query, context):
        return ReasoningResult(
            answer="测试回答",
            reasoning_steps=[{"step": 1, "action": "test"}],
            confidence=0.85,
            sources=["entity_001"]
        )
    
    llm.reason.side_effect = mock_reason
    return llm


@pytest.fixture
def mock_kg_processor():
    """模拟知识图谱处理器"""
    processor = Mock()
    
    # 模拟实体
    processor.entities = {
        "entity_001": {
            "id": "entity_001",
            "type": "schema",
            "name": "TestSchema",
            "properties": {"description": "A test schema"}
        },
        "entity_002": {
            "id": "entity_002",
            "type": "field",
            "name": "testField",
            "properties": {"type": "string"}
        }
    }
    
    # 模拟关系
    processor.relations = [
        {"source": "entity_001", "target": "entity_002", "type": "has_field"}
    ]
    
    processor.get_entity = Mock(side_effect=lambda eid: processor.entities.get(eid))
    processor.search_entities = Mock(return_value=list(processor.entities.values()))
    processor.get_related_entities = Mock(return_value=[processor.entities["entity_002"]])
    
    return processor


# =============================================================================
# 推理结果模型测试
# =============================================================================

class TestReasoningResult:
    """推理结果模型测试类"""
    
    def test_create_reasoning_result(self):
        """测试创建推理结果"""
        result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[{"step": 1, "action": "test"}],
            confidence=0.85,
            sources=["entity_001"]
        )
        
        assert result.answer == "测试回答"
        assert len(result.reasoning_steps) == 1
        assert result.confidence == 0.85
        assert result.sources == ["entity_001"]
    
    def test_reasoning_result_dict(self):
        """测试推理结果转换为字典"""
        result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[],
            confidence=0.5,
            sources=[]
        )
        
        d = result.model_dump()
        assert d["answer"] == "测试回答"
        assert d["confidence"] == 0.5


# =============================================================================
# 知识图谱嵌入测试
# =============================================================================

class TestKGEmbedding:
    """知识图谱嵌入测试类"""
    
    def test_embed_entity(self, mock_llm):
        """测试实体嵌入"""
        kg_embedding = KGEmbedding(mock_llm)
        
        entity = {
            "id": "entity_001",
            "type": "schema",
            "properties": {"name": "TestSchema"}
        }
        
        import numpy as np
        embedding = kg_embedding.embed_entity(entity)
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 1536
        mock_llm.embed.assert_called()
    
    def test_embed_relation(self, mock_llm):
        """测试关系嵌入"""
        kg_embedding = KGEmbedding(mock_llm)
        
        relation = {
            "source": "entity_001",
            "target": "entity_002",
            "type": "has_field"
        }
        
        import numpy as np
        embedding = kg_embedding.embed_relation(relation)
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 1536
    
    def test_embed_subgraph(self, mock_llm, mock_kg_processor):
        """测试子图嵌入"""
        kg_embedding = KGEmbedding(mock_llm)
        
        entities = list(mock_kg_processor.entities.values())
        relations = mock_kg_processor.relations
        
        import numpy as np
        embedding = kg_embedding.embed_subgraph(entities, relations)
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 1536


# =============================================================================
# 嵌入存储测试
# =============================================================================

class TestEmbeddingStore:
    """嵌入存储测试类"""
    
    def test_add_and_get(self):
        """测试添加和获取嵌入"""
        store = EmbeddingStore(dimension=128)
        
        store.add("key1", [0.1] * 128, {"type": "test"})
        embedding = store.get("key1")
        
        assert embedding is not None
        assert len(embedding) == 128
    
    def test_search_similar(self):
        """测试相似度搜索"""
        store = EmbeddingStore(dimension=128)
        
        # 添加测试嵌入
        store.add("entity_001", [0.1] * 128, {"type": "schema"})
        store.add("entity_002", [0.2] * 128, {"type": "field"})
        store.add("entity_003", [0.15] * 128, {"type": "type"})
        
        # 搜索相似项
        results = store.search([0.1] * 128, top_k=2)
        assert len(results) == 2
        # 最相似的应该是entity_001或entity_003（因为它们都是0.1或接近0.1）
        assert results[0][0] in ["entity_001", "entity_003"]
        # 相似度应该在0-1之间（允许浮点误差）
        assert -0.001 <= results[0][1] <= 1.001
    
    def test_remove(self):
        """测试删除嵌入"""
        store = EmbeddingStore(dimension=128)
        
        store.add("key1", [0.1] * 128)
        assert store.get("key1") is not None
        
        store.remove("key1")
        assert store.get("key1") is None
    
    def test_clear(self):
        """测试清空存储"""
        store = EmbeddingStore(dimension=128)
        
        store.add("key1", [0.1] * 128)
        store.add("key2", [0.2] * 128)
        
        assert len(store) == 2
        
        store.clear()
        assert len(store) == 0
    
    def test_cosine_similarity(self):
        """测试余弦相似度计算"""
        import numpy as np
        store = EmbeddingStore(dimension=3)
        
        # 相同向量，相似度为1
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        sim = store._cosine_similarity(a, b)
        assert abs(sim - 1.0) < 0.001
        
        # 正交向量，相似度为0
        c = np.array([0.0, 1.0, 0.0])
        sim = store._cosine_similarity(a, c)
        assert abs(sim) < 0.001


# =============================================================================
# 推理链构建测试
# =============================================================================

class TestReasoningChainBuilder:
    """推理链构建器测试类"""
    
    def test_build_reasoning_chain(self, mock_llm, mock_kg_processor):
        """测试推理链构建"""
        builder = ReasoningChainBuilder(mock_kg_processor, mock_llm)
        
        chain = builder.build_reasoning_chain("What is TestSchema?", max_steps=2)
        
        assert isinstance(chain, list)
        assert len(chain) > 0
    
    def test_execute_reasoning_step(self, mock_llm, mock_kg_processor):
        """测试执行推理步骤"""
        builder = ReasoningChainBuilder(mock_kg_processor, mock_llm)
        
        step = ReasoningStep(
            step_number=1,
            action="search",
            input="TestSchema",
            output="",
            confidence=0.0
        )
        
        result = builder.execute_step(step)
        assert result is not None
        assert result.output != ""
    
    def test_multi_step_reasoning(self, mock_llm, mock_kg_processor):
        """测试多步推理"""
        builder = ReasoningChainBuilder(mock_kg_processor, mock_llm)
        
        # 构建多步推理链
        chain = [
            ReasoningStep(1, "search", "TestSchema", "", 0.0),
            ReasoningStep(2, "expand", "entity_001", "", 0.0),
            ReasoningStep(3, "analyze", "fields", "", 0.0)
        ]
        
        results = builder.execute_chain(chain)
        assert isinstance(results, list)
        assert len(results) == len(chain)


# =============================================================================
# 结果验证测试
# =============================================================================

class TestResultValidator:
    """结果验证器测试类"""
    
    def test_validate_confidence(self, mock_kg_processor):
        """测试置信度验证"""
        validator = ResultValidator(mock_kg_processor)
        
        # 高置信度结果
        high_confidence_result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[],
            confidence=0.9,
            sources=["entity_001"]
        )
        
        validation = validator.validate_confidence(high_confidence_result)
        assert validation.is_valid is True
        
        # 低置信度结果
        low_confidence_result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[],
            confidence=0.3,
            sources=["entity_001"]
        )
        
        validation = validator.validate_confidence(low_confidence_result)
        assert validation.is_valid is False
    
    def test_validate_sources(self, mock_kg_processor):
        """测试来源验证"""
        validator = ResultValidator(mock_kg_processor)
        
        # 有效来源
        valid_result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[],
            confidence=0.8,
            sources=["entity_001", "entity_002"]
        )
        
        validation = validator.validate_sources(valid_result)
        assert validation.is_valid is True
        
        # 无效来源
        invalid_result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[],
            confidence=0.8,
            sources=["nonexistent_entity"]
        )
        
        validation = validator.validate_sources(invalid_result)
        assert validation.is_valid is False
    
    def test_validate_consistency(self, mock_kg_processor):
        """测试一致性验证"""
        validator = ResultValidator(mock_kg_processor)
        
        # 构建一致的推理步骤
        steps = [
            {"step": 1, "action": "search", "result": "entity_001"},
            {"step": 2, "action": "expand", "result": "entity_002"}
        ]
        
        result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=steps,
            confidence=0.8,
            sources=["entity_001", "entity_002"]
        )
        
        validation = validator.validate_consistency(result)
        assert isinstance(validation.is_valid, bool)
    
    def test_validate_full_result(self, mock_kg_processor):
        """测试完整结果验证"""
        validator = ResultValidator(mock_kg_processor)
        
        result = ReasoningResult(
            answer="测试回答",
            reasoning_steps=[
                {"step": 1, "type": "query_understanding"},
                {"step": 2, "type": "entity_retrieval"}
            ],
            confidence=0.8,
            sources=["entity_001"]
        )
        
        context = {"entities": [{"id": "entity_001"}]}
        validation = validator.validate_result(result, context)
        
        assert isinstance(validation, dict)
        assert "is_valid" in validation
        assert "confidence" in validation


# =============================================================================
# ValidationResult 测试
# =============================================================================

class TestValidationResult:
    """验证结果模型测试"""
    
    def test_create_validation_result(self):
        """测试创建验证结果"""
        result = ValidationResult(
            is_valid=True,
            confidence=0.9,
            issues=[],
            suggestions=[]
        )
        
        assert result.is_valid is True
        assert result.confidence == 0.9
    
    def test_validation_result_defaults(self):
        """测试验证结果默认值"""
        result = ValidationResult(is_valid=True)
        
        assert result.issues == []
        assert result.suggestions == []


# =============================================================================
# 集成测试
# =============================================================================

class TestLLMReasoningIntegration:
    """LLM推理引擎集成测试"""
    
    def test_full_reasoning_pipeline(self, mock_llm, mock_kg_processor):
        """测试完整推理流程"""
        # 构建组件
        builder = ReasoningChainBuilder(mock_kg_processor, mock_llm)
        validator = ResultValidator(mock_kg_processor)
        
        # 执行查询
        query = "What is TestSchema and what fields does it have?"
        
        # 构建推理链
        chain = builder.build_reasoning_chain(query, max_steps=2)
        assert len(chain) > 0
        
        # 构建最终结果
        final_result = ReasoningResult(
            answer="TestSchema has field testField",
            reasoning_steps=[{"step": 1, "type": "search"}],
            confidence=0.85,
            sources=["entity_001", "entity_002"]
        )
        
        # 验证结果
        validations = [
            validator.validate_confidence(final_result),
            validator.validate_sources(final_result),
            validator.validate_consistency(final_result)
        ]
        
        # 至少有一个验证通过
        assert any(v.is_valid for v in validations)
    
    def test_kg_embedding_integration(self, mock_llm, mock_kg_processor):
        """测试知识图谱嵌入集成"""
        kg_embedding = KGEmbedding(mock_llm)
        
        # 嵌入所有实体
        embeddings = {}
        for entity_id, entity in mock_kg_processor.entities.items():
            embeddings[entity_id] = kg_embedding.embed_entity(entity)
        
        assert len(embeddings) == len(mock_kg_processor.entities)
        
        # 嵌入所有关系
        for relation in mock_kg_processor.relations:
            emb = kg_embedding.embed_relation(relation)
            assert emb is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
