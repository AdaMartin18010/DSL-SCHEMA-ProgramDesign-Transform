"""
性能测试

测试各个模块的性能指标
"""

import pytest
import time
import asyncio
from multimodal_kg import MultimodalKGStorage, TextModalityProcessor
from temporal_kg import TemporalKGStorage
from usl import USLParser, USLValidator
from hierarchical_kg import HierarchicalKGStorage
from knowledge_chain import KnowledgeChainBuilder


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


def test_multimodal_storage_performance(multimodal_storage):
    """测试多模态存储性能"""
    text_processor = TextModalityProcessor(storage=multimodal_storage)
    
    # 测试批量插入性能
    start_time = time.time()
    for i in range(100):
        text_processor.process_text(
            entity_id=f"entity_{i}",
            content=f"Test content {i}",
            content_type="schema_doc"
        )
    end_time = time.time()
    
    elapsed = end_time - start_time
    throughput = 100 / elapsed
    
    print(f"\n批量插入100条记录耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {throughput:.2f} 条/秒")
    
    # 性能断言（根据实际情况调整）
    assert elapsed < 10.0, "批量插入性能不达标"
    assert throughput > 10.0, "吞吐量不达标"


def test_temporal_storage_performance(temporal_storage):
    """测试时序存储性能"""
    from datetime import datetime
    
    # 测试批量插入性能
    start_time = time.time()
    for i in range(100):
        temporal_storage.add_entity(
            entity_id=f"entity_{i}",
            entity_type="schema",
            valid_from=datetime.now(),
            properties={"version": f"1.{i}"}
        )
    end_time = time.time()
    
    elapsed = end_time - start_time
    throughput = 100 / elapsed
    
    print(f"\n批量插入100条记录耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {throughput:.2f} 条/秒")
    
    # 性能断言
    assert elapsed < 10.0, "批量插入性能不达标"
    assert throughput > 10.0, "吞吐量不达标"


def test_usl_parsing_performance():
    """测试USL解析性能"""
    parser = USLParser()
    
    usl_code = """
    schema TestSchema {
      field name: String { required: true }
      field age: Integer { required: true }
      field email: String { required: false }
    }
    """
    
    # 测试解析性能
    start_time = time.time()
    for _ in range(1000):
        parser.parse(usl_code)
    end_time = time.time()
    
    elapsed = end_time - start_time
    throughput = 1000 / elapsed
    
    print(f"\n解析1000次耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {throughput:.2f} 次/秒")
    
    # 性能断言
    assert elapsed < 5.0, "解析性能不达标"
    assert throughput > 200.0, "吞吐量不达标"


def test_hierarchical_abstraction_performance():
    """测试层次化抽象性能"""
    storage = HierarchicalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_hierarchical_kg'
    )
    
    # 创建测试数据
    instances = []
    for i in range(50):
        instances.append({
            "entity_id": f"instance_{i}",
            "name": f"Instance {i}",
            "level": 1,
            "content": {"type": "schema_instance", "domain": "finance"}
        })
    
    # 测试抽象性能
    start_time = time.time()
    for instance in instances:
        storage.add_entity(**instance)
    end_time = time.time()
    
    elapsed = end_time - start_time
    throughput = 50 / elapsed
    
    print(f"\n抽象50个实例耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {throughput:.2f} 个/秒")
    
    # 性能断言
    assert elapsed < 5.0, "抽象性能不达标"
    assert throughput > 10.0, "吞吐量不达标"


def test_knowledge_chain_building_performance():
    """测试知识链构建性能"""
    builder = KnowledgeChainBuilder(
        database_url='postgresql://test:test@localhost:5432/test_knowledge_chain'
    )
    
    schema_doc = {
        "entities": [{"id": i, "name": f"Entity{i}"} for i in range(20)],
        "relations": [{"from": i, "to": i+1, "type": "related"} for i in range(19)]
    }
    
    # 测试构建性能
    start_time = time.time()
    for _ in range(10):
        builder.build_chain(schema_doc, "Test Chain")
    end_time = time.time()
    
    elapsed = end_time - start_time
    throughput = 10 / elapsed
    
    print(f"\n构建10条知识链耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {throughput:.2f} 条/秒")
    
    # 性能断言
    assert elapsed < 10.0, "构建性能不达标"
    assert throughput > 1.0, "吞吐量不达标"


@pytest.mark.asyncio
async def test_concurrent_operations():
    """测试并发操作性能"""
    storage = MultimodalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_multimodal_kg'
    )
    text_processor = TextModalityProcessor(storage=storage)
    
    # 并发插入
    async def insert_entity(i):
        text_processor.process_text(
            entity_id=f"concurrent_entity_{i}",
            content=f"Concurrent content {i}",
            content_type="schema_doc"
        )
    
    start_time = time.time()
    await asyncio.gather(*[insert_entity(i) for i in range(50)])
    end_time = time.time()
    
    elapsed = end_time - start_time
    throughput = 50 / elapsed
    
    print(f"\n并发插入50条记录耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {throughput:.2f} 条/秒")
    
    # 性能断言
    assert elapsed < 5.0, "并发性能不达标"
    assert throughput > 10.0, "吞吐量不达标"
