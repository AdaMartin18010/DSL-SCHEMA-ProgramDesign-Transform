"""
知识链方法单元测试
"""

import pytest
from knowledge_chain import (
    KnowledgeChainStorage,
    KnowledgeChainBuilder,
    KnowledgeChainReasoning
)


@pytest.fixture
def storage():
    """创建测试存储实例"""
    return KnowledgeChainStorage(
        database_url='postgresql://test:test@localhost:5432/test_knowledge_chain'
    )


def test_build_chain(storage):
    """测试知识链构建"""
    builder = KnowledgeChainBuilder(storage)
    
    schema_doc = {
        'entities': [
            {'id': 1, 'name': 'Entity1', 'properties': {'type': 'schema'}},
            {'id': 2, 'name': 'Entity2', 'properties': {'type': 'schema'}}
        ],
        'relations': []
    }
    
    chain = builder.build_chain(schema_doc, "Test Chain")
    assert chain is not None
    assert 'chain_id' in chain


def test_reasoning(storage):
    """测试知识链推理"""
    reasoning = KnowledgeChainReasoning(storage)
    
    # 创建测试知识链
    storage.create_chain(
        chain_id="test_chain",
        name="Test Chain",
        node_ids=["entity_1", "pattern_1", "concept_1"]
    )
    
    # 自底向上推理
    path = reasoning.bottom_up_reasoning("test_chain")
    assert len(path) > 0
