# 性能优化指南

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🎯 性能目标

### 吞吐量目标

| 操作 | 目标吞吐量 | 实际测试 |
|------|-----------|---------|
| 多模态存储插入 | > 100 条/秒 | 待测试 |
| 时序存储插入 | > 100 条/秒 | 待测试 |
| USL解析 | > 1000 次/秒 | 待测试 |
| 层次化抽象 | > 50 个/秒 | 待测试 |
| 知识链构建 | > 10 条/秒 | 待测试 |

### 延迟目标

| 操作 | 目标延迟 | 实际测试 |
|------|---------|---------|
| 单次插入 | < 100ms | 待测试 |
| 批量插入（100条） | < 10s | 待测试 |
| USL解析 | < 5ms | 待测试 |
| 查询操作 | < 500ms | 待测试 |

---

## 🔧 性能优化策略

### 1. 数据库优化

#### PostgreSQL优化

```sql
-- 创建索引
CREATE INDEX idx_entity_id ON entities(entity_id);
CREATE INDEX idx_timestamp ON temporal_entities(valid_from, valid_to);

-- 分析表统计信息
ANALYZE entities;
ANALYZE temporal_entities;

-- 调整连接池大小
-- 在config.py中设置
MAX_CONNECTIONS = 20
POOL_SIZE = 10
```

#### pgvector优化

```sql
-- 创建向量索引
CREATE INDEX idx_text_embedding ON text_entities
USING ivfflat (text_embedding vector_cosine_ops)
WITH (lists = 100);

-- 调整索引参数
SET ivfflat.probes = 10;
```

### 2. 代码优化

#### 批量操作

```python
# 不推荐：逐条插入
for entity in entities:
    storage.add_entity(entity)

# 推荐：批量插入
storage.batch_add_entities(entities)
```

#### 连接池管理

```python
# 使用连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

#### 异步操作

```python
# 使用异步操作提高并发性能
import asyncio

async def process_multiple_entities(entities):
    tasks = [process_entity(e) for e in entities]
    await asyncio.gather(*tasks)
```

### 3. 缓存优化

#### Redis缓存

```python
# 缓存查询结果
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def get_entity_cached(entity_id):
    cache_key = f"entity:{entity_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    entity = storage.get_entity(entity_id)
    redis_client.setex(cache_key, 3600, json.dumps(entity))
    return entity
```

### 4. API优化

#### 请求批处理

```python
# 支持批量请求
@app.post("/api/v1/entities/batch")
async def batch_add_entities(entities: List[Entity]):
    return storage.batch_add_entities(entities)
```

#### 分页查询

```python
# 使用分页避免大量数据查询
@app.get("/api/v1/entities")
async def list_entities(
    page: int = 1,
    page_size: int = 100
):
    offset = (page - 1) * page_size
    return storage.list_entities(limit=page_size, offset=offset)
```

---

## 📊 性能监控

### 1. 性能指标收集

```python
# 使用时间装饰器
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        return result
    return wrapper

@measure_time
def add_entity(entity):
    return storage.add_entity(entity)
```

### 2. 性能测试

```bash
# 运行性能测试
pytest code/tests/test_performance.py -v

# 生成性能报告
pytest code/tests/test_performance.py --benchmark-only
```

### 3. 监控工具

- **Prometheus** - 指标收集
- **Grafana** - 可视化监控
- **APM工具** - 应用性能监控

---

## 🚀 性能最佳实践

### 1. 数据库连接

- ✅ 使用连接池
- ✅ 及时关闭连接
- ✅ 避免长时间事务

### 2. 查询优化

- ✅ 使用索引
- ✅ 避免全表扫描
- ✅ 使用分页查询

### 3. 批量操作

- ✅ 批量插入而非逐条插入
- ✅ 批量更新而非逐条更新
- ✅ 使用事务批量提交

### 4. 缓存策略

- ✅ 缓存热点数据
- ✅ 设置合理的过期时间
- ✅ 使用缓存预热

---

## 📝 相关文档

- [开发指南](DEVELOPMENT_GUIDE.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [故障排查](TROUBLESHOOTING.md)

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
