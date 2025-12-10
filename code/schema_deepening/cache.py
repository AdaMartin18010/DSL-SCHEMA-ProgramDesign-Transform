"""
Schema深化模块缓存工具

提供缓存机制优化性能
"""

from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import threading
from .logger import logger


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, value: Any, expire_time: Optional[datetime] = None):
        self.value = value
        self.expire_time = expire_time
        self.created_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expire_time is None:
            return False
        return datetime.utcnow() > self.expire_time


class SimpleCache:
    """
    简单缓存实现
    
    支持过期时间和线程安全
    """
    
    def __init__(self, default_ttl: Optional[int] = None):
        """
        初始化缓存
        
        Args:
            default_ttl: 默认过期时间（秒），None表示不过期
        """
        self._cache: dict = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        logger.info(f"SimpleCache initialized with default_ttl={default_ttl}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                logger.debug(f"缓存键 {key} 已过期")
                return None
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None使用默认值
        """
        with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            expire_time = None
            
            if ttl is not None:
                expire_time = datetime.utcnow() + timedelta(seconds=ttl)
            
            self._cache[key] = CacheEntry(value, expire_time)
            logger.debug(f"设置缓存键 {key}，TTL={ttl}")
    
    def delete(self, key: str) -> bool:
        """
        删除缓存键
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"删除缓存键 {key}")
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"清空缓存，删除了 {count} 个条目")
    
    def cleanup_expired(self) -> int:
        """
        清理过期条目
        
        Returns:
            清理的条目数量
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"清理了 {len(expired_keys)} 个过期缓存条目")
            
            return len(expired_keys)
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)


def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """
    缓存装饰器
    
    Args:
        ttl: 过期时间（秒）
        key_func: 自定义键生成函数，默认使用函数名和参数
        
    Example:
        @cached(ttl=300)
        def expensive_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        cache = SimpleCache(default_ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"缓存结果: {cache_key}")
            return result
        
        wrapper.cache = cache  # 暴露缓存对象以便手动管理
        return wrapper
    
    return decorator


# 全局缓存实例
_global_cache: Optional[SimpleCache] = None


def get_global_cache() -> SimpleCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = SimpleCache(default_ttl=3600)  # 默认1小时
    return _global_cache
