"""
多模态知识图谱单元测试
"""

import pytest
import numpy as np
from multimodal_kg import (
    TextModalityProcessor,
    ImageModalityProcessor,
    MultimodalFusion,
    MultimodalKGStorage
)


@pytest.fixture
def storage():
    """创建测试存储实例"""
    return MultimodalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_multimodal_kg'
    )


@pytest.fixture
def text_processor(storage):
    """创建文本处理器实例"""
    return TextModalityProcessor(storage=storage)


def test_text_processing(text_processor):
    """测试文本处理"""
    success = text_processor.process_text(
        entity_id="test_001",
        content="This is a test schema document",
        content_type="schema_doc"
    )
    assert success == True


def test_text_search(text_processor):
    """测试文本搜索"""
    # 先添加测试数据
    text_processor.process_text(
        entity_id="test_001",
        content="This is a test schema document",
        content_type="schema_doc"
    )
    
    # 搜索
    results = text_processor.search_similar("schema document", top_k=5)
    assert len(results) > 0
    assert results[0]['entity_id'] == "test_001"


def test_multimodal_fusion():
    """测试多模态融合"""
    fusion = MultimodalFusion()
    text_emb = np.random.rand(384)
    image_emb = np.random.rand(512)
    
    fused = fusion.fuse(text_emb, image_emb)
    assert fused.shape[0] > 0
