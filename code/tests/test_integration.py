"""
集成测试

测试各个模块之间的集成
"""

import pytest
from multimodal_kg import MultimodalKGStorage, TextModalityProcessor
from temporal_kg import TemporalKGStorage
from llm_reasoning import OpenAILLM
from usl import USLParser, USLValidator


@pytest.fixture
def multimodal_storage():
    """创建多模态知识图谱存储实例"""
    return MultimodalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_multimodal_kg'
    )


@pytest.fixture
def temporal_storage():
    """创建时序知识图谱存储实例"""
    return TemporalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_temporal_kg'
    )


def test_multimodal_temporal_integration(multimodal_storage, temporal_storage):
    """测试多模态和时序知识图谱的集成"""
    # 1. 在多模态KG中添加实体
    text_processor = TextModalityProcessor(storage=multimodal_storage)
    success = text_processor.process_text(
        entity_id="schema_001",
        content="This is a test schema",
        content_type="schema_doc"
    )
    assert success == True
    
    # 2. 在时序KG中记录实体变化
    from datetime import datetime
    success = temporal_storage.add_entity(
        entity_id="schema_001",
        entity_type="schema",
        valid_from=datetime.now(),
        properties={"version": "1.0"}
    )
    assert success == True


def test_llm_usl_integration():
    """测试LLM和USL的集成"""
    # 1. 解析USL代码
    parser = USLParser()
    usl_code = """
    schema TestSchema {
      field name: String {
        required: true
      }
    }
    """
    ast = parser.parse(usl_code)
    assert ast is not None
    
    # 2. 验证USL
    validator = USLValidator(ast)
    result = validator.validate()
    assert result['valid'] == True
    
    # 3. 使用LLM生成Schema描述（需要API密钥）
    # llm = OpenAILLM(api_key="test_key")
    # description = llm.generate(f"Describe this schema: {usl_code}")
    # assert description is not None


def test_end_to_end_workflow():
    """端到端工作流测试"""
    # 1. 创建USL Schema
    parser = USLParser()
    usl_code = """
    schema PaymentSchema {
      field amount: Decimal {
        required: true
        constraint: {
          min: 0
          max: 1000000
        }
      }
    }
    """
    ast = parser.parse(usl_code)
    
    # 2. 验证Schema
    validator = USLValidator(ast)
    validation_result = validator.validate()
    assert validation_result['valid'] == True
    
    # 3. 存储到多模态KG
    # 4. 记录到时序KG
    # 5. 使用LLM推理
    # （需要完整的数据库和API配置）
