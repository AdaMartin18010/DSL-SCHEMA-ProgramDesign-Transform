"""
MCP (Model Context Protocol) 性能优化模块

该模块提供了MCP协议的性能优化功能，包括：
- 连接池管理 (Connection Pool)
- 请求批处理 (Batch Processing)
- 缓存策略 (Cache Management)

Usage:
    from code.mcp import ConnectionPool, BatchProcessor, CacheManager
    
    # 使用连接池
    pool = ConnectionPool(max_connections=10)
    
    # 使用批处理器
    batcher = BatchProcessor(batch_size=100, flush_interval=0.1)
    
    # 使用缓存管理器
    cache = CacheManager(max_size=1000, ttl=300)
"""

from .connection_pool import ConnectionPool, ConnectionPoolConfig, PooledConnection
from .batch_processor import BatchProcessor, BatchConfig, BatchItem
from .cache_manager import CacheManager, CacheConfig, CacheStrategy

__version__ = "1.0.0"
__all__ = [
    # 连接池相关
    "ConnectionPool",
    "ConnectionPoolConfig", 
    "PooledConnection",
    # 批处理相关
    "BatchProcessor",
    "BatchConfig",
    "BatchItem",
    # 缓存相关
    "CacheManager",
    "CacheConfig",
    "CacheStrategy",
]
