"""
时序知识图谱单元测试
"""

import pytest
from datetime import datetime, timedelta
from temporal_kg import (
    TemporalKGStorage,
    TemporalEvolutionTracker,
    TemporalReasoning
)
import psycopg2


def check_database_available():
    """检查数据库是否可用"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='test_temporal_kg',
            user='test',
            password='test',
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False


DB_AVAILABLE = check_database_available()


@pytest.fixture
def storage():
    """创建测试存储实例"""
    if not DB_AVAILABLE:
        pytest.skip("数据库不可用，跳过测试")
    return TemporalKGStorage(
        database_url='postgresql://test:test@localhost:5432/test_temporal_kg'
    )


def test_temporal_entity_storage(storage):
    """测试时序实体存储"""
    now = datetime.now()
    
    success = storage.add_entity(
        entity_id="schema_001",
        entity_type="schema",
        valid_from=now,
        properties={"version": "1.0"}
    )
    assert success == True


def test_entity_update(storage):
    """测试实体更新"""
    now = datetime.now()
    
    # 添加实体
    storage.add_entity(
        entity_id="schema_001",
        entity_type="schema",
        valid_from=now,
        properties={"version": "1.0"}
    )
    
    # 更新实体
    success = storage.update_entity(
        entity_id="schema_001",
        new_properties={"version": "2.0"},
        update_time=now + timedelta(days=1)
    )
    assert success == True


def test_get_entity_at_time(storage):
    """测试时间点查询"""
    now = datetime.now()
    
    # 添加实体
    storage.add_entity(
        entity_id="schema_001",
        entity_type="schema",
        valid_from=now,
        properties={"version": "1.0"}
    )
    
    # 查询历史版本
    entity = storage.get_entity_at_time("schema_001", now)
    assert entity is not None
    assert entity['properties']['version'] == "1.0"
