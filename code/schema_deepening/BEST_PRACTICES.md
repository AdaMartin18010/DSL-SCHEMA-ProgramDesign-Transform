# Schema深化模块最佳实践

## 📚 目录

- [Schema深化模块最佳实践](#schema深化模块最佳实践)
  - [📚 目录](#-目录)
  - [📝 日志记录](#-日志记录)
    - [1. 使用统一的日志工具](#1-使用统一的日志工具)
    - [2. 日志级别选择](#2-日志级别选择)
    - [3. 日志格式](#3-日志格式)
  - [⚠️ 错误处理](#️-错误处理)
    - [1. 使用自定义异常](#1-使用自定义异常)
    - [2. 输入验证](#2-输入验证)
    - [3. 数据库操作错误处理](#3-数据库操作错误处理)
  - [🚀 性能优化](#-性能优化)
    - [1. 使用缓存](#1-使用缓存)
    - [2. 数据库索引](#2-数据库索引)
    - [3. 批量操作](#3-批量操作)
  - [📁 代码组织](#-代码组织)
    - [1. 模块导入](#1-模块导入)
    - [2. 函数文档](#2-函数文档)
    - [3. 类型提示](#3-类型提示)
  - [🧪 测试策略](#-测试策略)
    - [1. 单元测试](#1-单元测试)
    - [2. 测试覆盖](#2-测试覆盖)
    - [3. 模拟外部依赖](#3-模拟外部依赖)
  - [🔧 配置管理](#-配置管理)
    - [1. 环境变量](#1-环境变量)
    - [2. 配置文件](#2-配置文件)
  - [📊 监控和调试](#-监控和调试)
    - [1. 性能监控](#1-性能监控)
    - [2. 调试技巧](#2-调试技巧)
  - [🔒 安全考虑](#-安全考虑)
    - [1. 输入验证](#1-输入验证)
    - [2. SQL注入防护](#2-sql注入防护)
  - [📈 性能建议](#-性能建议)
  - [🎯 总结](#-总结)

## 📝 日志记录

### 1. 使用统一的日志工具

```python
from code.schema_deepening import logger

# 记录信息
logger.info("操作成功")
logger.debug("调试信息")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)
```

### 2. 日志级别选择

- **DEBUG**: 详细的调试信息，仅在开发时使用
- **INFO**: 一般信息，记录重要操作
- **WARNING**: 警告信息，不影响功能但需要注意
- **ERROR**: 错误信息，需要记录异常堆栈

### 3. 日志格式

```python
from code.schema_deepening.logger import setup_logger

# 自定义日志配置
logger = setup_logger(
    name='my_module',
    level=logging.INFO,
    log_file='my_module.log'
)
```

## ⚠️ 错误处理

### 1. 使用自定义异常

```python
from code.schema_deepening.exceptions import (
    ValidationError,
    ConversionError,
    StorageError
)

try:
    # 操作代码
    pass
except ValidationError as e:
    # 处理验证错误
    logger.error(f"验证失败: {str(e)}")
except ConversionError as e:
    # 处理转换错误
    logger.error(f"转换失败: {str(e)}")
except StorageError as e:
    # 处理存储错误
    logger.error(f"存储失败: {str(e)}")
```

### 2. 输入验证

```python
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """处理数据"""
    # 验证输入
    if not data:
        raise ValidationError("数据不能为空")

    if 'required_field' not in data:
        raise ValidationError("缺少必需字段: required_field")

    # 处理逻辑
    return result
```

### 3. 数据库操作错误处理

```python
try:
    # 数据库操作
    self.cur.execute(query, params)
    self.conn.commit()
    logger.info("操作成功")
except psycopg2.Error as e:
    self.conn.rollback()
    logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
    raise StorageError(f"操作失败: {str(e)}") from e
```

## 🚀 性能优化

### 1. 使用缓存

```python
from code.schema_deepening.cache import cached, get_global_cache

# 使用装饰器缓存
@cached(ttl=300)  # 缓存5分钟
def expensive_function(x, y):
    return x + y

# 使用全局缓存
cache = get_global_cache()
cache.set('key', 'value', ttl=3600)
value = cache.get('key')
```

### 2. 数据库索引

- 为常用查询字段创建索引
- 使用复合索引优化多字段查询
- 定期清理过期数据

### 3. 批量操作

```python
# 批量插入而不是逐条插入
def batch_insert(items: List[Dict]):
    """批量插入"""
    for item in items:
        # 准备数据
        pass

    # 一次性执行
    self.cur.executemany(query, params_list)
    self.conn.commit()
```

## 📁 代码组织

### 1. 模块导入

```python
# 好的做法：按功能分组导入
from code.schema_deepening import (
    SmartHomeConverter,
    DeviceProtocol,
    DeviceType
)
from code.schema_deepening.exceptions import ValidationError
from code.schema_deepening.logger import logger

# 避免：导入所有内容
# from code.schema_deepening import *
```

### 2. 函数文档

```python
def convert_device(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    转换设备数据

    Args:
        device_data: 设备数据字典

    Returns:
        转换后的设备数据

    Raises:
        ValidationError: 数据验证失败时抛出
        ConversionError: 转换失败时抛出
    """
    # 实现代码
    pass
```

### 3. 类型提示

```python
from typing import Dict, List, Any, Optional

def process_items(
    items: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """处理项目列表"""
    pass
```

## 🧪 测试策略

### 1. 单元测试

```python
import unittest
from code.schema_deepening import SmartHomeConverter

class TestSmartHomeConverter(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.converter = SmartHomeConverter()

    def test_convert_device(self):
        """测试设备转换"""
        # 测试代码
        pass
```

### 2. 测试覆盖

- 测试正常流程
- 测试边界情况
- 测试错误情况
- 测试异常处理

### 3. 模拟外部依赖

```python
from unittest.mock import Mock, patch

@patch('code.schema_deepening.smart_home_storage.psycopg2')
def test_storage(mock_psycopg2):
    """测试存储功能"""
    # 模拟数据库连接
    mock_conn = Mock()
    mock_psycopg2.connect.return_value = mock_conn
    # 测试代码
```

## 🔧 配置管理

### 1. 环境变量

```python
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

### 2. 配置文件

```python
# config.py
class Config:
    DATABASE_URL = "postgresql://localhost/db"
    LOG_LEVEL = "INFO"
    CACHE_TTL = 3600
```

## 📊 监控和调试

### 1. 性能监控

```python
import time
from code.schema_deepening.logger import logger

def monitored_function():
    """监控函数性能"""
    start_time = time.time()

    try:
        # 执行操作
        result = perform_operation()

        elapsed = time.time() - start_time
        logger.info(f"操作完成，耗时: {elapsed:.2f}秒")

        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"操作失败，耗时: {elapsed:.2f}秒", exc_info=True)
        raise
```

### 2. 调试技巧

- 使用日志记录关键步骤
- 记录输入和输出数据
- 使用断点调试
- 分析性能瓶颈

## 🔒 安全考虑

### 1. 输入验证

```python
def safe_process(input_data: str) -> str:
    """安全处理输入"""
    # 验证输入
    if not input_data or len(input_data) > 1000:
        raise ValidationError("输入无效")

    # 清理输入
    cleaned = input_data.strip()

    # 处理
    return process(cleaned)
```

### 2. SQL注入防护

```python
# 好的做法：使用参数化查询
self.cur.execute(
    "SELECT * FROM table WHERE id = %s",
    (user_id,)
)

# 避免：字符串拼接
# self.cur.execute(f"SELECT * FROM table WHERE id = {user_id}")
```

## 📈 性能建议

1. **数据库连接池**: 使用连接池管理数据库连接
2. **异步操作**: 对于I/O密集型操作使用异步
3. **批量处理**: 批量处理数据而不是逐条处理
4. **缓存策略**: 合理使用缓存减少数据库查询
5. **索引优化**: 为常用查询创建合适的索引

## 🎯 总结

遵循这些最佳实践可以：

- ✅ 提高代码质量
- ✅ 减少错误和bug
- ✅ 提升性能
- ✅ 便于维护和调试
- ✅ 增强系统稳定性

---

**维护者**: DSL Schema研究团队
**最后更新**: 2025-01-21
