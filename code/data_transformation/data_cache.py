"""
数据缓存模块

专注于数据缓存、缓存策略、缓存管理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import logging

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
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = None


class DataCache:
    """
    数据缓存器
    
    专注于数据缓存、缓存策略、缓存管理
    """
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.strategy = strategy
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值（如果存在且未过期）
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # 检查是否过期
        if entry.expires_at and datetime.utcnow() > entry.expires_at:
            del self.cache[key]
            self.misses += 1
            return None
        
        # 更新访问信息
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        
        self.hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            
        Returns:
            是否成功
        """
        # 检查缓存大小
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_entry()
        
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_accessed=datetime.utcnow()
        )
        
        self.cache[key] = entry
        return True
    
    def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def _evict_entry(self):
        """根据策略驱逐条目"""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # 最近最少使用
            lru_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].last_accessed or self.cache[k].created_at
            )
            del self.cache[lru_key]
        
        elif self.strategy == CacheStrategy.LFU:
            # 最不经常使用
            lfu_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].access_count
            )
            del self.cache[lfu_key]
        
        elif self.strategy == CacheStrategy.FIFO:
            # 先进先出
            fifo_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].created_at
            )
            del self.cache[fifo_key]
        
        elif self.strategy == CacheStrategy.TTL:
            # 生存时间（驱逐最早过期的）
            expired_keys = [
                k for k, v in self.cache.items()
                if v.expires_at and v.expires_at < datetime.utcnow()
            ]
            if expired_keys:
                del self.cache[expired_keys[0]]
            else:
                # 如果没有过期的，驱逐最早创建的
                fifo_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k].created_at
                )
                del self.cache[fifo_key]
    
    def get_or_set(self, key: str, default_func: Callable[[], Any],
                   ttl: Optional[int] = None) -> Any:
        """
        获取或设置缓存值
        
        Args:
            key: 缓存键
            default_func: 默认值函数
            ttl: 生存时间（秒）
            
        Returns:
            缓存值
        """
        value = self.get(key)
        if value is None:
            value = default_func()
            self.set(key, value, ttl)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            缓存统计
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'strategy': self.strategy.value
        }
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            缓存键
        """
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()


def main():
    """主函数 - 示例用法"""
    cache = DataCache(max_size=100, strategy=CacheStrategy.LRU)
    
    # 设置缓存
    cache.set('key1', 'value1', ttl=60)
    
    # 获取缓存
    value = cache.get('key1')
    print(f"缓存值: {value}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"缓存统计: {stats}")


if __name__ == '__main__':
    main()
