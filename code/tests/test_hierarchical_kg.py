"""
层次化知识表示单元测试
"""

import pytest
from hierarchical_kg import (
    HierarchicalKGStorage,
    KnowledgeAbstraction,
    HierarchicalReasoning
)


def check_database_available():
    """检查数据库是否可用"""
    try:
        storage = HierarchicalKGStorage(
            database_url='postgresql://test:test@localhost:5432/test_hierarchical_kg'
        )
        # 实际测试连接
        result = storage.initialize_database()
        return result is True
    except Exception:
        return False


DB_AVAILABLE = check_database_available()


@pytest.fixture
def storage():
    """创建测试存储实例"""
    if not DB_AVAILABLE:
        pytest.skip("数据库不可用，跳过测试")
    return HierarchicalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_hierarchical_kg'
    )


def test_add_entity(storage):
    """测试添加实体"""
    success = storage.add_entity(
        entity_id="instance_001",
        name="Test Instance",
        level=1,
        content={"type": "schema_instance"}
    )
    assert success == True


def test_abstraction(storage):
    """测试知识抽象"""
    abstraction = KnowledgeAbstraction(storage)
    
    # 添加实例
    storage.add_entity("inst_1", "Instance 1", 1, content={"type": "schema"})
    storage.add_entity("inst_2", "Instance 2", 1, content={"type": "schema"})
    
    # 抽象为模式
    pattern = abstraction.abstract_instances_to_pattern(["inst_1", "inst_2"])
    assert pattern is not None


def test_reasoning(storage):
    """测试层次化推理"""
    reasoning = HierarchicalReasoning(storage)
    
    # 添加实体
    storage.add_entity("inst_1", "Instance 1", 1, abstraction_id="pattern_1")
    storage.add_entity("pattern_1", "Pattern 1", 2, abstraction_id="concept_1")
    storage.add_entity("concept_1", "Concept 1", 3)
    
    # 自底向上推理
    path = reasoning.bottom_up_reasoning("inst_1")
    assert len(path) > 0
