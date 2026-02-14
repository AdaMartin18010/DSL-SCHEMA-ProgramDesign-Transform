"""
MCP协议性能优化模块测试

测试内容：
1. 连接池 (ConnectionPool) - 基本功能、并发、超时、指标
2. 批处理器 (BatchProcessor) - 提交、优先级、自适应、指标
3. 缓存管理器 (CacheManager) - 存取、过期、装饰器、防护机制
"""

import asyncio
import pytest
import sys
import os
from typing import List, Any

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.connection_pool import (
    ConnectionPool, ConnectionPoolConfig, PooledConnection, 
    ConnectionState, MockMCPConnection
)
from mcp.batch_processor import (
    BatchProcessor, BatchConfig, BatchItem, Priority, BatchStrategy
)
from mcp.cache_manager import (
    CacheManager, CacheConfig, CacheStrategy, BloomFilter
)


# ============================================================================
# Connection Pool Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pool_initialization():
    """测试连接池初始化"""
    config = ConnectionPoolConfig(min_connections=2, max_connections=5, enable_warmup=False)
    pool = ConnectionPool(config)
    
    await pool.initialize()
    assert pool._is_initialized
    await pool.close()


@pytest.mark.asyncio
async def test_acquire_and_release():
    """测试连接获取和释放"""
    config = ConnectionPoolConfig(min_connections=1, max_connections=2, enable_warmup=False)
    pool = ConnectionPool(config)
    
    conn = await pool.get_connection()
    assert conn is not None
    assert conn.state == ConnectionState.BUSY
    
    await pool.release(conn)
    assert conn.state == ConnectionState.IDLE
    
    await pool.close()


@pytest.mark.asyncio
async def test_acquire_context_manager():
    """测试上下文管理器获取连接"""
    config = ConnectionPoolConfig(min_connections=1, max_connections=2, enable_warmup=False)
    pool = ConnectionPool(config)
    
    async with pool.acquire() as conn:
        assert conn is not None
        assert conn.state == ConnectionState.BUSY
    
    assert conn.state == ConnectionState.IDLE
    await pool.close()


@pytest.mark.asyncio
async def test_pool_exhaustion():
    """测试连接池耗尽处理"""
    config = ConnectionPoolConfig(
        min_connections=1,
        max_connections=1,
        acquire_timeout=0.2,
        enable_warmup=False
    )
    pool = ConnectionPool(config)
    await pool.initialize()
    
    conn = await pool.get_connection()
    
    # 第二次获取应该超时
    with pytest.raises(TimeoutError):
        await pool.get_connection()
    
    await pool.release(conn)
    await pool.close()


@pytest.mark.asyncio
async def test_concurrent_access():
    """测试并发访问"""
    config = ConnectionPoolConfig(min_connections=1, max_connections=3, enable_warmup=False)
    pool = ConnectionPool(config)
    
    results = []
    
    async def worker():
        async with pool.acquire() as conn:
            await asyncio.sleep(0.01)
            results.append(conn.id)
    
    await asyncio.gather(*[worker() for _ in range(5)])
    
    assert len(results) == 5
    await pool.close()


@pytest.mark.asyncio
async def test_pool_metrics():
    """测试连接池指标"""
    config = ConnectionPoolConfig(min_connections=1, max_connections=3, enable_warmup=False)
    pool = ConnectionPool(config)
    await pool.initialize()
    
    for _ in range(3):
        conn = await pool.get_connection()
        await pool.release(conn)
    
    metrics = pool.get_metrics()
    assert metrics['total_requests'] == 3
    
    await pool.close()


def test_pool_config_validation():
    """测试配置验证"""
    with pytest.raises(ValueError):
        ConnectionPoolConfig(min_connections=10, max_connections=5)


# ============================================================================
# Batch Processor Tests
# ============================================================================

@pytest.mark.asyncio
async def test_basic_batch_processing():
    """测试基本批处理功能"""
    processed = []
    
    async def process_func(items: List[Any]) -> List[Any]:
        processed.extend(items)
        return [f"result_{item}" for item in items]
    
    config = BatchConfig(batch_size=5, flush_interval=0.05, worker_count=1)
    processor = BatchProcessor(config, process_func)
    
    await processor.start()
    result = await processor.submit("item1")
    
    assert result == "result_item1"
    assert "item1" in processed
    
    await processor.stop()


@pytest.mark.asyncio
async def test_priority_handling():
    """测试优先级处理"""
    processed_order = []
    
    async def process_func(items: List[Any]) -> List[Any]:
        processed_order.extend(items)
        return items
    
    config = BatchConfig(batch_size=10, flush_interval=0.1, worker_count=1)
    processor = BatchProcessor(config, process_func)
    
    await processor.start()
    
    # 按顺序提交不同优先级，critical应优先处理
    await processor.submit("low", priority=Priority.LOW)
    await processor.submit("normal", priority=Priority.NORMAL)
    await processor.submit("high", priority=Priority.HIGH)
    await processor.submit("critical", priority=Priority.CRITICAL)
    
    await asyncio.sleep(0.3)
    
    await processor.stop()
    
    # critical应该在列表中
    assert len(processed_order) == 4
    assert "critical" in processed_order


@pytest.mark.asyncio
async def test_batch_submit_many():
    """测试批量提交"""
    async def process_func(items: List[Any]) -> List[Any]:
        return [f"processed_{item}" for item in items]
    
    config = BatchConfig(batch_size=10, worker_count=1)
    processor = BatchProcessor(config, process_func)
    
    await processor.start()
    
    items = [f"item{i}" for i in range(10)]
    results = await processor.submit_many(items)
    
    assert len(results) == 10
    assert all(r.startswith("processed_") for r in results)
    
    await processor.stop()


@pytest.mark.asyncio
async def test_processor_metrics():
    """测试批处理器指标"""
    async def process_func(items: List[Any]) -> List[Any]:
        return items
    
    config = BatchConfig(batch_size=5, worker_count=1)
    processor = BatchProcessor(config, process_func)
    
    await processor.start()
    
    for i in range(5):
        await processor.submit(f"item{i}")
    
    await asyncio.sleep(0.2)
    
    metrics = processor.get_metrics()
    assert metrics['total_submitted'] == 5
    
    await processor.stop()


# ============================================================================
# Cache Manager Tests
# ============================================================================

@pytest.mark.asyncio
async def test_basic_cache_operations():
    """测试基本缓存操作"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    await cache.set("key1", "value1")
    value = await cache.get("key1")
    assert value == "value1"
    
    value = await cache.get("nonexistent", default="default")
    assert value == "default"
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_expiration():
    """测试缓存过期"""
    cache = CacheManager(CacheConfig(max_size=100, cleanup_interval=0.1))
    await cache.start()
    
    await cache.set("key1", "value1", ttl=0.05)
    
    value = await cache.get("key1")
    assert value == "value1"
    
    await asyncio.sleep(0.15)
    
    value = await cache.get("key1")
    assert value is None
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_set_many():
    """测试批量设置"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    items = {f"key{i}": f"value{i}" for i in range(5)}
    count = await cache.set_many(items)
    
    assert count == 5
    
    for i in range(5):
        value = await cache.get(f"key{i}")
        assert value == f"value{i}"
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_delete():
    """测试删除缓存"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    await cache.set("key1", "value1")
    assert await cache.get("key1") == "value1"
    
    result = await cache.delete("key1")
    assert result is True
    assert await cache.get("key1") is None
    
    result = await cache.delete("nonexistent")
    assert result is False
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_exists():
    """测试检查存在性"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    await cache.set("key1", "value1")
    assert await cache.exists("key1") is True
    assert await cache.exists("nonexistent") is False
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_with_loader():
    """测试带加载器的获取"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    call_count = 0
    
    async def loader():
        nonlocal call_count
        call_count += 1
        return f"loaded_value_{call_count}"
    
    value = await cache.get_with_loader("key1", loader)
    assert value == "loaded_value_1"
    assert call_count == 1
    
    value = await cache.get_with_loader("key1", loader)
    assert value == "loaded_value_1"
    assert call_count == 1
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_decorator():
    """测试缓存装饰器"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    call_count = 0
    
    @cache.cached(ttl=60)
    async def expensive_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x
    
    result1 = await expensive_function(5)
    assert result1 == 25
    assert call_count == 1
    
    result2 = await expensive_function(5)
    assert result2 == 25
    assert call_count == 1
    
    result3 = await expensive_function(3)
    assert result3 == 9
    assert call_count == 2
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_stats():
    """测试缓存统计"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    await cache.set("key1", "value1")
    await cache.get("key1")  # hit
    await cache.get("key2")  # miss
    await cache.delete("key1")
    
    stats = await cache.get_stats_async()
    
    assert stats['sets'] == 1
    assert stats['hits'] == 1
    assert stats['misses'] == 1
    assert stats['deletes'] == 1
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_ttl_method():
    """测试TTL方法"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    await cache.set("key1", "value1", ttl=2.0)
    
    ttl = await cache.ttl("key1")
    assert 1.0 < ttl <= 2.0
    
    assert await cache.ttl("nonexistent") == -1
    
    await cache.stop()


@pytest.mark.asyncio
async def test_cache_lru_strategy():
    """测试LRU策略"""
    config = CacheConfig(max_size=3, strategy=CacheStrategy.LRU)
    cache = CacheManager(config)
    await cache.start()
    
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    
    await cache.get("key1")
    
    await cache.set("key4", "value4")
    
    assert await cache.get("key1") is not None
    assert await cache.get("key2") is None
    assert await cache.get("key3") is not None
    
    await cache.stop()


# ============================================================================
# Bloom Filter Tests
# ============================================================================

@pytest.mark.asyncio
async def test_bloom_filter_basic():
    """测试布隆过滤器基本功能"""
    bf = BloomFilter(size=1000, hash_count=5)
    
    await bf.add("item1")
    await bf.add("item2")
    
    assert await bf.contains("item1") is True
    assert await bf.contains("item2") is True


@pytest.mark.asyncio
async def test_bloom_filter_clear():
    """测试清空布隆过滤器"""
    bf = BloomFilter(size=1000, hash_count=5)
    
    await bf.add("item1")
    assert await bf.contains("item1") is True
    
    await bf.clear()
    assert await bf.contains("item1") is False


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pool_with_batch_processor():
    """测试连接池与批处理器集成"""
    pool_config = ConnectionPoolConfig(min_connections=1, max_connections=3, enable_warmup=False)
    pool = ConnectionPool(pool_config)
    await pool.initialize()
    
    async def process_with_pool(items: List[str]) -> List[str]:
        results = []
        for item in items:
            async with pool.acquire() as conn:
                result = f"{item}_via_pool"
                results.append(result)
        return results
    
    batch_config = BatchConfig(batch_size=3, worker_count=1)
    processor = BatchProcessor(batch_config, process_with_pool)
    
    await processor.start()
    
    results = await processor.submit_many([f"req{i}" for i in range(5)])
    
    assert len(results) == 5
    assert all("_via_pool" in r for r in results)
    
    await processor.stop()
    await pool.close()


@pytest.mark.asyncio
async def test_cache_with_batch_processor():
    """测试缓存与批处理器集成"""
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    processed_count = 0
    
    async def cached_process(items: List[str]) -> List[str]:
        nonlocal processed_count
        results = []
        for item in items:
            cached = await cache.get(item)
            if cached:
                results.append(cached)
            else:
                processed_count += 1
                result = f"processed_{item}"
                await cache.set(item, result)
                results.append(result)
        return results
    
    batch_config = BatchConfig(batch_size=3, worker_count=1)
    processor = BatchProcessor(batch_config, cached_process)
    
    await processor.start()
    
    results1 = await processor.submit_many(["a", "b", "c"])
    assert processed_count == 3
    
    results2 = await processor.submit_many(["a", "b", "d"])
    assert processed_count == 4  # 只有d是新处理的
    
    await processor.stop()
    await cache.stop()


@pytest.mark.asyncio
async def test_end_to_end_performance():
    """端到端性能测试"""
    pool_config = ConnectionPoolConfig(min_connections=1, max_connections=3, enable_warmup=False)
    pool = ConnectionPool(pool_config)
    await pool.initialize()
    
    cache = CacheManager(CacheConfig(max_size=100))
    await cache.start()
    
    async def full_pipeline(items: List[str]) -> List[str]:
        results = []
        for item in items:
            cached = await cache.get(item)
            if cached:
                results.append(f"cached:{cached}")
                continue
            
            async with pool.acquire() as conn:
                result = f"processed_{item}"
                await cache.set(item, result)
                results.append(result)
        return results
    
    batch_config = BatchConfig(batch_size=5, flush_interval=0.05, worker_count=1)
    processor = BatchProcessor(batch_config, full_pipeline)
    
    await processor.start()
    
    all_results = []
    for batch in range(2):
        items = [f"item{batch}_{i}" for i in range(5)]
        results = await processor.submit_many(items)
        all_results.extend(results)
    
    assert len(all_results) == 10
    
    pool_metrics = pool.get_metrics()
    cache_stats = cache.get_stats()
    
    assert pool_metrics['total_requests'] > 0
    
    await processor.stop()
    await cache.stop()
    await pool.close()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
