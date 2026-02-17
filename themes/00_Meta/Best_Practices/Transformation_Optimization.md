# Schema转换优化最佳实践

## 概述

本文档提供Schema转换的性能优化和最佳实践，帮助开发人员实现高效、可靠的转换系统。

---

## 性能优化策略

### 1. 算法优化

#### 复杂度分析

```python
import time
from functools import wraps

def benchmark(func):
    """性能基准测试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper

# 优化前: O(n²) 复杂度
@benchmark
def transform_naive(data_list, mapping):
    """朴素的转换实现"""
    result = []
    for item in data_list:  # O(n)
        for key, value in mapping.items():  # O(m)
            if key in item:
                # 转换操作
                pass
    return result

# 优化后: O(n) 复杂度
@benchmark
def transform_optimized(data_list, mapping):
    """优化的转换实现"""
    # 预构建查找表
    lookup = {k: v for k, v in mapping.items()}  # O(m)
    
    result = []
    for item in data_list:  # O(n)
        # 直接查找，无需内层循环
        transformed = {lookup[k]: v for k, v in item.items() if k in lookup}
        result.append(transformed)
    return result
```

#### 缓存策略

```python
from functools import lru_cache
import hashlib
import json

class CachedTransformer:
    """带缓存的转换器"""
    
    def __init__(self, maxsize: int = 1000):
        self.cache = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
    
    def _compute_hash(self, data: dict) -> str:
        """计算数据哈希"""
        # 使用确定性JSON序列化
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def transform_with_cache(self, data: dict, transform_fn) -> dict:
        """带缓存的转换"""
        cache_key = self._compute_hash(data)
        
        if cache_key in self.cache:
            self.hits += 1
            return self.cache[cache_key]
        
        self.misses += 1
        result = transform_fn(data)
        
        # LRU缓存淘汰
        if len(self.cache) >= self.maxsize:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = result
        return result
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }
```

### 2. 并发处理

#### 并行转换

```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import cpu_count
import asyncio

class ParallelTransformer:
    """并行转换器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or cpu_count()
    
    def transform_batch_parallel(self, data_list: list, transform_fn) -> list:
        """批量并行转换（CPU密集型）"""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(transform_fn, data_list))
        return results
    
    def transform_batch_threaded(self, data_list: list, transform_fn) -> list:
        """批量多线程转换（I/O密集型）"""
        with ThreadPoolExecutor(max_workers=self.max_workers * 2) as executor:
            results = list(executor.map(transform_fn, data_list))
        return results
    
    async def transform_batch_async(self, data_list: list, async_transform_fn) -> list:
        """异步批量转换"""
        tasks = [async_transform_fn(item) for item in data_list]
        results = await asyncio.gather(*tasks)
        return results


# 使用示例
async def example():
    transformer = ParallelTransformer()
    
    # 假设有1000条记录需要转换
    data = [{"id": i, "value": i * 2} for i in range(1000)]
    
    # 并行处理
    results = transformer.transform_batch_parallel(data, lambda x: x)
    
    # 异步处理
    async def async_transform(item):
        await asyncio.sleep(0.001)  # 模拟I/O
        return item
    
    results = await transformer.transform_batch_async(data, async_transform)
```

### 3. 流式处理

```python
from typing import Iterator, Generator
import json

class StreamingTransformer:
    """流式转换器（适合大文件）"""
    
    def transform_large_file(self, input_file: str, output_file: str, transform_fn):
        """流式处理大文件"""
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            outfile.write('[')
            first = True
            
            for line in infile:
                # 假设每行是一个JSON对象
                try:
                    data = json.loads(line)
                    result = transform_fn(data)
                    
                    if not first:
                        outfile.write(',\n')
                    json.dump(result, outfile)
                    first = False
                    
                except json.JSONDecodeError:
                    continue
            
            outfile.write(']')
    
    def transform_generator(self, data_source: Iterator[dict], 
                           transform_fn) -> Generator[dict, None, None]:
        """生成器式转换（内存友好）"""
        for item in data_source:
            result = transform_fn(item)
            if result is not None:
                yield result


# 使用示例
def large_dataset_generator(file_path: str):
    """大文件生成器"""
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)

# 流式处理
streamer = StreamingTransformer()
source = large_dataset_generator('large_data.json')
results = streamer.transform_generator(source, lambda x: x)

# 消费结果（每次只处理一条）
for result in results:
    process(result)
```

---

## 内存优化

### 1. 数据结构优化

```python
from dataclasses import dataclass
from typing import __slots__
import sys

# 优化前: 普通类
class TransformConfig:
    def __init__(self, source_schema, target_schema, mappings):
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.mappings = mappings

# 优化后: 使用__slots__
class TransformConfigOptimized:
    __slots__ = ['source_schema', 'target_schema', 'mappings']
    
    def __init__(self, source_schema, target_schema, mappings):
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.mappings = mappings

# 内存对比
print(f"Normal class: {sys.getsizeof(TransformConfig(None, None, None))} bytes")
print(f"Optimized class: {sys.getsizeof(TransformConfigOptimized(None, None, None))} bytes")

# 使用dataclass
@dataclass(slots=True)
class TransformRule:
    """转换规则（内存优化）"""
    source_field: str
    target_field: str
    transform_type: str
    params: dict = None
```

### 2. 对象池模式

```python
from typing import List
import threading

class TransformerPool:
    """转换器对象池"""
    
    def __init__(self, factory_fn, max_size: int = 10):
        self.factory_fn = factory_fn
        self.max_size = max_size
        self.pool = []
        self.in_use = set()
        self.lock = threading.Lock()
    
    def acquire(self):
        """获取转换器"""
        with self.lock:
            if self.pool:
                transformer = self.pool.pop()
                self.in_use.add(id(transformer))
                return transformer
            else:
                transformer = self.factory_fn()
                self.in_use.add(id(transformer))
                return transformer
    
    def release(self, transformer):
        """释放转换器"""
        with self.lock:
            transformer_id = id(transformer)
            if transformer_id in self.in_use:
                self.in_use.remove(transformer_id)
                if len(self.pool) < self.max_size:
                    # 重置状态
                    transformer.reset()
                    self.pool.append(transformer)
    
    def __enter__(self):
        self.transformer = self.acquire()
        return self.transformer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release(self.transformer)


# 使用示例
def create_transformer():
    return SchemaTransformer()  # 假设这是转换器类

pool = TransformerPool(create_transformer, max_size=5)

with pool as transformer:
    result = transformer.transform(data)
```

---

## 数据库优化

### 1. 批量操作

```python
from typing import List
import sqlite3

class BatchDatabaseTransformer:
    """批量数据库转换器"""
    
    def __init__(self, db_path: str, batch_size: int = 1000):
        self.db_path = db_path
        self.batch_size = batch_size
    
    def transform_batch_insert(self, data_list: List[dict], table: str):
        """批量插入优化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 准备批量插入
        for i in range(0, len(data_list), self.batch_size):
            batch = data_list[i:i + self.batch_size]
            
            # 构建批量插入SQL
            columns = batch[0].keys()
            placeholders = ', '.join(['?' for _ in columns])
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # 批量执行
            values = [tuple(item.values()) for item in batch]
            cursor.executemany(sql, values)
            conn.commit()
        
        conn.close()
    
    def transform_streaming_query(self, query: str, transform_fn):
        """流式查询转换"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 使用服务器端游标
        cursor.execute(query)
        
        batch = []
        for row in cursor:
            batch.append(row)
            
            if len(batch) >= self.batch_size:
                # 批量处理
                for item in batch:
                    yield transform_fn(item)
                batch = []
        
        # 处理剩余
        for item in batch:
            yield transform_fn(item)
        
        conn.close()
```

### 2. 索引优化

```sql
-- 转换映射表索引优化
CREATE TABLE schema_mappings (
    id INTEGER PRIMARY KEY,
    source_schema_id INTEGER,
    target_schema_id INTEGER,
    field_path VARCHAR(500),
    mapping_rule JSON,
    created_at TIMESTAMP
);

-- 为查询优化创建索引
CREATE INDEX idx_source_target ON schema_mappings(source_schema_id, target_schema_id);
CREATE INDEX idx_field_path ON schema_mappings(field_path);

-- 复合索引（用于范围查询）
CREATE INDEX idx_created_source ON schema_mappings(created_at, source_schema_id);
```

---

## 缓存策略

### 多级缓存

```python
import redis
import pickle
from functools import wraps

class MultiLevelCache:
    """多级缓存（内存 + Redis）"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.local_cache = {}
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.local_max_size = 1000
    
    def get(self, key: str):
        """获取缓存值"""
        # L1: 本地内存
        if key in self.local_cache:
            return self.local_cache[key]
        
        # L2: Redis
        value = self.redis_client.get(key)
        if value:
            result = pickle.loads(value)
            # 回填本地缓存
            self._add_to_local(key, result)
            return result
        
        return None
    
    def set(self, key: str, value, ttl: int = 3600):
        """设置缓存值"""
        # 保存到本地
        self._add_to_local(key, value)
        
        # 保存到Redis
        self.redis_client.setex(key, ttl, pickle.dumps(value))
    
    def _add_to_local(self, key: str, value):
        """添加到本地缓存（LRU淘汰）"""
        if len(self.local_cache) >= self.local_max_size:
            oldest = next(iter(self.local_cache))
            del self.local_cache[oldest]
        self.local_cache[key] = value


def cached_transform(cache: MultiLevelCache, ttl: int = 3600):
    """转换结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            cache_key = f"{func.__name__}:{hash(str(args))}:{hash(str(kwargs))}"
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行转换
            result = func(*args, **kwargs)
            
            # 保存到缓存
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

---

## 监控和调优

### 性能监控

```python
import time
from collections import defaultdict
import statistics

class TransformationMonitor:
    """转换性能监控器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.error_count = 0
        self.success_count = 0
    
    def record(self, operation: str, duration: float, success: bool = True):
        """记录指标"""
        self.metrics[operation].append(duration)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        stats = {}
        for operation, durations in self.metrics.items():
            stats[operation] = {
                'count': len(durations),
                'avg': statistics.mean(durations),
                'median': statistics.median(durations),
                'p95': self._percentile(durations, 95),
                'p99': self._percentile(durations, 99),
                'min': min(durations),
                'max': max(durations)
            }
        
        total = self.success_count + self.error_count
        stats['overall'] = {
            'success_rate': self.success_count / total if total > 0 else 0,
            'error_rate': self.error_count / total if total > 0 else 0,
            'total_operations': total
        }
        
        return stats
    
    def _percentile(self, data: list, percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# 上下文管理器使用
class MonitoredTransform:
    """受监控的转换"""
    
    def __init__(self, monitor: TransformationMonitor, operation: str):
        self.monitor = monitor
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        success = exc_type is None
        self.monitor.record(self.operation, duration, success)
        return False  # 不吞掉异常


# 使用示例
monitor = TransformationMonitor()

with MonitoredTransform(monitor, "json_to_xml"):
    result = transform_json_to_xml(data)

# 查看统计
print(monitor.get_statistics())
```

---

## 最佳实践检查清单

### 性能检查

- [ ] 使用了缓存机制
- [ ] 实现了批量处理
- [ ] 使用了并发/并行
- [ ] 优化了算法复杂度
- [ ] 使用了流式处理（大文件）
- [ ] 内存使用优化（slots, 对象池）

### 可靠性检查

- [ ] 实现了错误重试机制
- [ ] 添加了超时控制
- [ ] 有完善的日志记录
- [ ] 实现了断点续传
- [ ] 有监控和告警

### 可维护性检查

- [ ] 代码模块化
- [ ] 配置外部化
- [ ] 单元测试覆盖
- [ ] 文档完善
- [ ] 版本控制

---

**创建时间**: 2026-02-17  
**维护者**: DSL Schema研究团队
