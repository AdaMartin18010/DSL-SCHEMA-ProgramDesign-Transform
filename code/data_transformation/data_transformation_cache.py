"""
数据转换缓存模块

专注于数据转换缓存、缓存管理、缓存策略
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """缓存策略"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最不经常使用
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"  # 生存时间


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: Optional[timedelta] = None


class DataTransformationCache:
    """
    数据转换缓存器
    
    专注于数据转换缓存、缓存管理、缓存策略
    """
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # 用于LRU/FIFO
        self.access_frequency: Dict[str, int] = {}  # 用于LFU
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或过期则返回None
        """
        entry = self.cache.get(key)
        if not entry:
            return None
        
        # 检查TTL
        if entry.ttl:
            if datetime.utcnow() - entry.created_at > entry.ttl:
                self._remove_entry(key)
                return None
        
        # 更新访问信息
        entry.accessed_at = datetime.utcnow()
        entry.access_count += 1
        
        # 更新访问顺序
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        # 更新访问频率
        self.access_frequency[key] = self.access_frequency.get(key, 0) + 1
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（可选）
        """
        # 如果缓存已满，删除一个条目
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_entry()
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
            ttl=ttl
        )
        
        self.cache[key] = entry
        
        # 更新访问顺序
        if key not in self.access_order:
            self.access_order.append(key)
        
        # 更新访问频率
        self.access_frequency[key] = 1
    
    def _evict_entry(self):
        """驱逐一个缓存条目"""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # 删除最近最少使用的
            if self.access_order:
                key_to_remove = self.access_order[0]
                self._remove_entry(key_to_remove)
        
        elif self.strategy == CacheStrategy.LFU:
            # 删除最不经常使用的
            if self.access_frequency:
                key_to_remove = min(self.access_frequency.items(), key=lambda x: x[1])[0]
                self._remove_entry(key_to_remove)
        
        elif self.strategy == CacheStrategy.FIFO:
            # 删除最早进入的
            if self.access_order:
                key_to_remove = self.access_order[0]
                self._remove_entry(key_to_remove)
        
        elif self.strategy == CacheStrategy.TTL:
            # 删除过期的
            now = datetime.utcnow()
            for key, entry in list(self.cache.items()):
                if entry.ttl and now - entry.created_at > entry.ttl:
                    self._remove_entry(key)
                    return
            # 如果没有过期的，删除最早的
            if self.access_order:
                key_to_remove = self.access_order[0]
                self._remove_entry(key_to_remove)
    
    def _remove_entry(self, key: str):
        """删除缓存条目"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
        if key in self.access_frequency:
            del self.access_frequency[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()
        self.access_frequency.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            缓存统计
        """
        total_size = len(self.cache)
        total_access = sum(e.access_count for e in self.cache.values())
        
        return {
            'total_entries': total_size,
            'max_size': self.max_size,
            'strategy': self.strategy.value,
            'total_access': total_access,
            'hit_rate': 0.0  # 需要记录命中率
        }


def cached(ttl: Optional[timedelta] = None):
    """缓存装饰器"""
    def decorator(func: Callable):
        cache = DataTransformationCache()
        
        def wrapper(*args, **kwargs):
            key = cache._generate_key(*args, **kwargs)
            value = cache.get(key)
            if value is not None:
                return value
            
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator


def main():
    """主函数 - 示例用法"""
    cache = DataTransformationCache(max_size=100, strategy=CacheStrategy.LRU)
    
    # 设置缓存
    cache.set('key1', 'value1')
    
    # 获取缓存
    value = cache.get('key1')
    print(f"缓存值: {value}")


if __name__ == '__main__':
    main()
