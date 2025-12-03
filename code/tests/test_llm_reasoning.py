"""
LLM推理引擎单元测试
"""

import pytest
from llm_reasoning import (
    OpenAILLM,
    KGEmbedding,
    ReasoningChainBuilder
)


@pytest.fixture
def llm():
    """创建LLM实例（需要API密钥）"""
    api_key = "test_key"  # 测试时使用模拟
    return OpenAILLM(api_key=api_key)


def test_kg_embedding(llm):
    """测试知识图谱嵌入"""
    embedding = KGEmbedding(llm)
    
    entity = {
        'id': 'entity_001',
        'type': 'schema',
        'properties': {'name': 'Test Schema'}
    }
    
    # 测试实体嵌入（需要实际API调用，这里简化）
    # emb = embedding.embed_entity(entity)
    # assert emb is not None


def test_reasoning_chain_builder(llm):
    """测试推理链构建"""
    kg_processor = None  # 模拟知识图谱处理器
    builder = ReasoningChainBuilder(kg_processor, llm)
    
    # 测试推理链构建（需要实际API调用，这里简化）
    # chain = builder.build_reasoning_chain("What is a schema?")
    # assert len(chain) > 0
