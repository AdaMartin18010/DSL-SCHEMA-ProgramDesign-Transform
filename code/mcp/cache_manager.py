"""
MCP缓存管理优化模块

提供高效的缓存策略，支持：
- 多级缓存 (LRU/LFU/FIFO)
- TTL自动过期
- 缓存预热
- 缓存穿透/击穿防护
- 分布式缓存支持

示例：
    >>> config = CacheConfig(max_size=1000, ttl=300, strategy=CacheStrategy.LRU)
    >>> cache = CacheManager(config)
    >>> await cache.set("key", value)
    >>> value = await cache.get("key")
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any, Callable, Dict, Generic, Hashable, List, Optional, 
    Set, Tuple, TypeVar, Union, AsyncIterator
)
from functools import wraps
import heapq

logger = logging.getLogger(__name__)

K = TypeVar('K', bound=Hashable)
V = TypeVar('V')


class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"          # 最近最少使用
    LFU = "lfu"          # 最少使用频率
    FIFO = "fifo"        # 先进先出
    TTL = "ttl"          # 基于过期时间
    ADAPTIVE = "adaptive"  # 自适应策略


@dataclass
class CacheConfig:
    """缓存配置类
    
    Attributes:
        max_size: 最大缓存条目数
        ttl: 默认过期时间（秒）
        cleanup_interval: 清理间隔（秒）
        enable_stats: 是否启用统计
        enable_persistence: 是否启用持久化
        persistence_path: 持久化路径
        enable_compression: 是否启用压缩
        compression_threshold: 压缩阈值（字节）
        enable_bloom_filter: 是否启用布隆过滤器（防穿透）
        enable_mutex: 是否启用互斥锁（防击穿）
        mutex_timeout: 互斥锁超时时间（秒）
        strategy: 缓存策略
        hot_key_threshold: 热点key阈值
        hot_key_duration: 热点key持续时间（秒）
        enable_prefetch: 是否启用预取
        prefetch_batch_size: 预取批量大小
    """
    max_size: int = 1000
    ttl: float = 300.0
    cleanup_interval: float = 60.0
    enable_stats: bool = True
    enable_persistence: bool = False
    persistence_path: Optional[str] = None
    enable_compression: bool = False
    compression_threshold: int = 1024
    enable_bloom_filter: bool = True
    enable_mutex: bool = True
    mutex_timeout: float = 10.0
    strategy: CacheStrategy = CacheStrategy.LRU
    hot_key_threshold: int = 100
    hot_key_duration: float = 60.0
    enable_prefetch: bool = False
    prefetch_batch_size: int = 10
    
    def __post_init__(self):
        if self.max_size <= 0:
            raise ValueError("max_size must be positive")


@dataclass
class CacheEntry(Generic[V]):
    """缓存条目
    
    Attributes:
        key: 缓存键
        value: 缓存值
        created_at: 创建时间
        expires_at: 过期时间
        access_count: 访问次数
        last_accessed: 最后访问时间
        size: 条目大小（字节）
    """
    key: K
    value: V
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 300)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size: int = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() > self.expires_at
    
    def touch(self):
        """更新访问信息"""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def time_to_live(self) -> float:
        """获取剩余生存时间"""
        return max(0, self.expires_at - time.time())


class CacheStats:
    """缓存统计信息"""
    
    def __init__(self):
        self.hits: int = 0
        self.misses: int = 0
        self.sets: int = 0
        self.deletes: int = 0
        self.evictions: int = 0
        self.expirations: int = 0
        self.total_size: int = 0
        self._hit_times: List[float] = []
        self._miss_times: List[float] = []
        self._started_at: float = time.time()
    
    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """未命中率"""
        return 1.0 - self.hit_rate
    
    @property
    def avg_hit_time(self) -> float:
        """平均命中时间"""
        return sum(self._hit_times) / len(self._hit_times) if self._hit_times else 0.0
    
    @property
    def avg_miss_time(self) -> float:
        """平均未命中时间"""
        return sum(self._miss_times) / len(self._miss_times) if self._miss_times else 0.0
    
    def record_hit(self, duration: float):
        """记录命中"""
        self.hits += 1
        self._hit_times.append(duration)
        if len(self._hit_times) > 1000:
            self._hit_times = self._hit_times[-500:]
    
    def record_miss(self, duration: float):
        """记录未命中"""
        self.misses += 1
        self._miss_times.append(duration)
        if len(self._miss_times) > 1000:
            self._miss_times = self._miss_times[-500:]
    
    def record_set(self):
        """记录设置"""
        self.sets += 1
    
    def record_delete(self):
        """记录删除"""
        self.deletes += 1
    
    def record_eviction(self):
        """记录驱逐"""
        self.evictions += 1
    
    def record_expiration(self):
        """记录过期"""
        self.expirations += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 4),
            "miss_rate": round(self.miss_rate, 4),
            "sets": self.sets,
            "deletes": self.deletes,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "total_size": self.total_size,
            "avg_hit_time": round(self.avg_hit_time, 6),
            "avg_miss_time": round(self.avg_miss_time, 6),
            "uptime": round(time.time() - self._started_at, 2),
        }


class BloomFilter:
    """布隆过滤器 - 用于防止缓存穿透"""
    
    def __init__(self, size: int = 100000, hash_count: int = 5):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [False] * size
        self._lock = asyncio.Lock()
    
    def _hashes(self, item: str) -> List[int]:
        """生成多个哈希值"""
        result = []
        for i in range(self.hash_count):
            hash_val = hashlib.md5(f"{item}:{i}".encode()).hexdigest()
            result.append(int(hash_val, 16) % self.size)
        return result
    
    async def add(self, item: str):
        """添加元素"""
        async with self._lock:
            for idx in self._hashes(item):
                self.bit_array[idx] = True
    
    async def contains(self, item: str) -> bool:
        """检查元素可能存在或肯定不存在"""
        async with self._lock:
            return all(self.bit_array[idx] for idx in self._hashes(item))
    
    async def clear(self):
        """清空过滤器"""
        async with self._lock:
            self.bit_array = [False] * self.size


class CacheBackend(ABC, Generic[K, V]):
    """缓存后端抽象基类"""
    
    @abstractmethod
    async def get(self, key: K) -> Optional[CacheEntry[V]]:
        """获取缓存条目"""
        pass
    
    @abstractmethod
    async def set(self, key: K, entry: CacheEntry[V]) -> bool:
        """设置缓存条目"""
        pass
    
    @abstractmethod
    async def delete(self, key: K) -> bool:
        """删除缓存条目"""
        pass
    
    @abstractmethod
    async def clear(self):
        """清空缓存"""
        pass
    
    @abstractmethod
    async def keys(self) -> List[K]:
        """获取所有键"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """获取缓存大小"""
        pass


class MemoryCacheBackend(CacheBackend[K, V]):
    """内存缓存后端"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._data: Dict[K, CacheEntry[V]] = {}
        self._lock = asyncio.Lock()
        
        # 根据策略选择数据结构
        if config.strategy == CacheStrategy.LRU:
            self._data = OrderedDict()
        elif config.strategy == CacheStrategy.LFU:
            self._frequency: Dict[K, int] = defaultdict(int)
            self._freq_heap: List[Tuple[int, K]] = []
    
    async def get(self, key: K) -> Optional[CacheEntry[V]]:
        async with self._lock:
            entry = self._data.get(key)
            if entry and not entry.is_expired():
                if self.config.strategy == CacheStrategy.LRU:
                    # 移到末尾（最近使用）
                    self._data.move_to_end(key)
                elif self.config.strategy == CacheStrategy.LFU:
                    self._frequency[key] += 1
                entry.touch()
                return entry
            elif entry and entry.is_expired():
                del self._data[key]
            return None
    
    async def set(self, key: K, entry: CacheEntry[V]) -> bool:
        async with self._lock:
            # 检查是否需要驱逐
            if len(self._data) >= self.config.max_size and key not in self._data:
                await self._evict()
            
            self._data[key] = entry
            if self.config.strategy == CacheStrategy.LFU:
                self._frequency[key] = entry.access_count
            return True
    
    async def _evict(self):
        """驱逐条目"""
        if not self._data:
            return
        
        if self.config.strategy == CacheStrategy.LRU:
            # 驱逐最久未使用
            key, _ = self._data.popitem(last=False)
        elif self.config.strategy == CacheStrategy.LFU:
            # 驱逐使用频率最低
            min_freq_key = min(self._frequency, key=self._frequency.get)
            del self._data[min_freq_key]
            del self._frequency[min_freq_key]
            key = min_freq_key
        elif self.config.strategy == CacheStrategy.FIFO:
            # 驱逐最早进入
            key = next(iter(self._data))
            del self._data[key]
        else:
            # 默认LRU
            key, _ = self._data.popitem(last=False)
        
        logger.debug(f"Evicted key: {key}")
    
    async def delete(self, key: K) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                if self.config.strategy == CacheStrategy.LFU:
                    del self._frequency[key]
                return True
            return False
    
    async def clear(self):
        async with self._lock:
            self._data.clear()
            if self.config.strategy == CacheStrategy.LFU:
                self._frequency.clear()
    
    async def keys(self) -> List[K]:
        async with self._lock:
            return list(self._data.keys())
    
    async def size(self) -> int:
        async with self._lock:
            return len(self._data)
    
    async def get_expired_keys(self) -> List[K]:
        """获取过期键"""
        async with self._lock:
            return [k for k, v in self._data.items() if v.is_expired()]


class CacheManager(Generic[K, V]):
    """MCP缓存管理器
    
    高性能缓存实现，支持多级缓存策略和防护机制。
    
    核心特性：
    1. 多种缓存策略 (LRU/LFU/FIFO/TTL)
    2. 缓存穿透防护 (布隆过滤器)
    3. 缓存击穿防护 (互斥锁)
    4. 自动过期清理
    5. 热点key识别
    
    使用示例：
        >>> config = CacheConfig(max_size=1000, ttl=300)
        >>> cache = CacheManager(config)
        >>> 
        >>> # 基本操作
        >>> await cache.set("key", value, ttl=60)
        >>> value = await cache.get("key")
        >>> 
        >>> # 使用装饰器缓存函数结果
        >>> @cache.cached(ttl=60)
        >>> async def expensive_function(x):
        ...     return x * 2
        >>> 
        >>> # 缓存预热
        >>> await cache.warmup({"key1": val1, "key2": val2})
        >>> 
        >>> # 获取统计
        >>> stats = cache.get_stats()
    
    Attributes:
        config: 缓存配置
        _backend: 缓存后端
        _stats: 统计信息
        _hot_keys: 热点key记录
        _mutexes: 互斥锁字典（防击穿）
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._backend = MemoryCacheBackend[K, V](self.config)
        
        # 防护机制
        self._bloom_filter: Optional[BloomFilter] = None
        if self.config.enable_bloom_filter:
            self._bloom_filter = BloomFilter()
        
        self._mutexes: Dict[K, asyncio.Lock] = {}
        self._mutex_lock = asyncio.Lock()
        
        # 统计
        self._stats = CacheStats()
        
        # 热点key
        self._hot_keys: Dict[K, Tuple[int, float]] = {}
        self._hot_key_lock = asyncio.Lock()
        
        # 后台任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running: bool = False
        
        # 预取队列
        self._prefetch_queue: asyncio.Queue = asyncio.Queue()
        self._prefetch_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动缓存管理器"""
        if self._is_running:
            return
        
        self._is_running = True
        
        # 启动清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # 启动预取任务
        if self.config.enable_prefetch:
            self._prefetch_task = asyncio.create_task(self._prefetch_loop())
        
        logger.info("Cache manager started")
    
    async def stop(self):
        """停止缓存管理器"""
        self._is_running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._prefetch_task:
            self._prefetch_task.cancel()
        
        # 持久化（如果启用）
        if self.config.enable_persistence:
            await self._persist()
        
        logger.info("Cache manager stopped")
    
    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        start_time = time.time()
        
        # 检查布隆过滤器（防穿透）
        if self._bloom_filter and not await self._bloom_filter.contains(str(key)):
            self._stats.record_miss(time.time() - start_time)
            return default
        
        # 获取缓存
        entry = await self._backend.get(key)
        
        if entry:
            duration = time.time() - start_time
            self._stats.record_hit(duration)
            await self._update_hot_key(key)
            return entry.value
        
        # 记录热点key可能的击穿
        await self._track_miss(key)
        
        duration = time.time() - start_time
        self._stats.record_miss(duration)
        return default
    
    async def get_with_loader(
        self,
        key: K,
        loader: Callable[[], V],
        ttl: Optional[float] = None
    ) -> V:
        """获取缓存值，如果不存在则加载
        
        使用互斥锁防止缓存击穿。
        
        Args:
            key: 缓存键
            loader: 加载函数
            ttl: 过期时间
            
        Returns:
            缓存值
        """
        # 先尝试获取
        value = await self.get(key)
        if value is not None:
            return value
        
        # 获取互斥锁（防击穿）
        if self.config.enable_mutex:
            async with self._get_mutex(key):
                # 双重检查
                value = await self.get(key)
                if value is not None:
                    return value
                
                # 加载数据
                value = await self._load_with_timeout(loader)
                await self.set(key, value, ttl)
                return value
        else:
            value = await self._load_with_timeout(loader)
            await self.set(key, value, ttl)
            return value
    
    def _get_mutex(self, key: K) -> asyncio.Lock:
        """获取key对应的互斥锁"""
        if key not in self._mutexes:
            self._mutexes[key] = asyncio.Lock()
        return self._mutexes[key]
    
    async def _load_with_timeout(self, loader: Callable[[], V]) -> V:
        """带超时的加载"""
        if asyncio.iscoroutinefunction(loader):
            return await asyncio.wait_for(loader(), timeout=self.config.mutex_timeout)
        return loader()
    
    async def set(
        self,
        key: K,
        value: V,
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            metadata: 元数据
            
        Returns:
            是否设置成功
        """
        ttl = ttl or self.config.ttl
        
        # 计算大小
        size = await self._calculate_size(value)
        
        entry = CacheEntry(
            key=key,
            value=value,
            expires_at=time.time() + ttl,
            size=size
        )
        
        if metadata:
            entry.metadata = metadata
        
        # 更新布隆过滤器
        if self._bloom_filter:
            await self._bloom_filter.add(str(key))
        
        result = await self._backend.set(key, entry)
        
        if result:
            self._stats.record_set()
            self._stats.total_size += size
        
        return result
    
    async def set_many(self, items: Dict[K, V], ttl: Optional[float] = None) -> int:
        """批量设置缓存
        
        Args:
            items: 键值对字典
            ttl: 过期时间
            
        Returns:
            成功设置的数量
        """
        count = 0
        for key, value in items.items():
            if await self.set(key, value, ttl):
                count += 1
        return count
    
    async def delete(self, key: K) -> bool:
        """删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        result = await self._backend.delete(key)
        if result:
            self._stats.record_delete()
        return result
    
    async def delete_many(self, keys: List[K]) -> int:
        """批量删除缓存
        
        Args:
            keys: 键列表
            
        Returns:
            成功删除的数量
        """
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        return count
    
    async def clear(self):
        """清空所有缓存"""
        await self._backend.clear()
        if self._bloom_filter:
            await self._bloom_filter.clear()
        self._hot_keys.clear()
        self._stats.total_size = 0
        logger.info("Cache cleared")
    
    async def exists(self, key: K) -> bool:
        """检查key是否存在"""
        entry = await self._backend.get(key)
        return entry is not None and not entry.is_expired()
    
    async def ttl(self, key: K) -> float:
        """获取key的剩余生存时间
        
        Returns:
            剩余秒数，-1表示不存在或永不过期
        """
        entry = await self._backend.get(key)
        if entry:
            return entry.time_to_live()
        return -1
    
    async def expire(self, key: K, ttl: float) -> bool:
        """设置key的过期时间
        
        Args:
            key: 缓存键
            ttl: 新的过期时间（秒）
            
        Returns:
            是否设置成功
        """
        entry = await self._backend.get(key)
        if entry:
            entry.expires_at = time.time() + ttl
            return True
        return False
    
    async def keys(self, pattern: Optional[str] = None) -> List[K]:
        """获取所有key（可选匹配模式）
        
        Args:
            pattern: 匹配模式（简单字符串匹配）
            
        Returns:
            key列表
        """
        keys = await self._backend.keys()
        if pattern:
            keys = [k for k in keys if pattern in str(k)]
        return keys
    
    async def warmup(self, data: Dict[K, V], ttl: Optional[float] = None):
        """缓存预热
        
        Args:
            data: 预加载数据
            ttl: 过期时间
        """
        logger.info(f"Warming up cache with {len(data)} items")
        await self.set_many(data, ttl)
    
    async def _cleanup_loop(self):
        """清理循环 - 定期清理过期条目"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    async def _cleanup_expired(self):
        """清理过期条目"""
        if isinstance(self._backend, MemoryCacheBackend):
            expired_keys = await self._backend.get_expired_keys()
            for key in expired_keys:
                await self._backend.delete(key)
                self._stats.record_expiration()
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    async def _update_hot_key(self, key: K):
        """更新热点key统计"""
        async with self._hot_key_lock:
            now = time.time()
            count, _ = self._hot_keys.get(key, (0, now))
            self._hot_keys[key] = (count + 1, now)
    
    async def _track_miss(self, key: K):
        """追踪未命中"""
        # 如果是热点key但未命中，可能是过期导致的
        async with self._hot_key_lock:
            if key in self._hot_keys:
                count, _ = self._hot_keys[key]
                if count > self.config.hot_key_threshold:
                    logger.warning(f"Hot key {key} missed, possible cache breakdown")
    
    async def get_hot_keys(self, limit: int = 10) -> List[Tuple[K, int]]:
        """获取热点key
        
        Args:
            limit: 返回数量限制
            
        Returns:
            (key, count) 列表
        """
        async with self._hot_key_lock:
            # 清理过期记录
            now = time.time()
            self._hot_keys = {
                k: (c, t) for k, (c, t) in self._hot_keys.items()
                if now - t < self.config.hot_key_duration
            }
            
            # 排序返回
            sorted_keys = sorted(
                self._hot_keys.items(),
                key=lambda x: x[1][0],
                reverse=True
            )
            return [(k, v[0]) for k, v in sorted_keys[:limit]]
    
    async def _calculate_size(self, value: V) -> int:
        """计算值的大小"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return 0
    
    async def _prefetch_loop(self):
        """预取循环"""
        while self._is_running:
            try:
                key, loader = await self._prefetch_queue.get()
                value = await self._load_with_timeout(loader)
                await self.set(key, value)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Prefetch error: {e}")
    
    async def prefetch(self, key: K, loader: Callable[[], V]):
        """添加预取任务"""
        if self.config.enable_prefetch:
            await self._prefetch_queue.put((key, loader))
    
    async def _persist(self):
        """持久化缓存"""
        if not self.config.persistence_path:
            return
        
        try:
            data = {}
            keys = await self._backend.keys()
            for key in keys:
                entry = await self._backend.get(key)
                if entry and not entry.is_expired():
                    data[key] = entry.value
            
            with open(self.config.persistence_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Cache persisted to {self.config.persistence_path}")
        except Exception as e:
            logger.error(f"Persist error: {e}")
    
    async def restore(self) -> int:
        """从持久化恢复缓存
        
        Returns:
            恢复的数量
        """
        if not self.config.persistence_path:
            return 0
        
        try:
            with open(self.config.persistence_path, 'rb') as f:
                data = pickle.load(f)
            
            await self.warmup(data)
            logger.info(f"Cache restored from {self.config.persistence_path}")
            return len(data)
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return 0
    
    def cached(
        self,
        ttl: Optional[float] = None,
        key_func: Optional[Callable] = None,
        condition: Optional[Callable[[V], bool]] = None
    ):
        """缓存装饰器
        
        Args:
            ttl: 过期时间
            key_func: 自定义key生成函数
            condition: 缓存条件函数
            
        使用示例：
            >>> @cache.cached(ttl=60)
            >>> async def get_user(user_id: int) -> User:
            ...     return await db.get_user(user_id)
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 生成缓存key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_key(func, args, kwargs)
                
                # 尝试获取缓存
                result = await self.get(cache_key)
                if result is not None:
                    return result
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 检查缓存条件
                if condition is None or condition(result):
                    await self.set(cache_key, result, ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 同步版本
                return asyncio.run(async_wrapper(*args, **kwargs))
            
            return async_wrapper
        return decorator
    
    def _generate_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """生成缓存key"""
        key_data = {
            'func': func.__name__,
            'args': args,
            'kwargs': kwargs
        }
        return hashlib.md5(
            json.dumps(key_data, sort_keys=True, default=str).encode()
        ).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息（同步版本）"""
        stats = self._stats.to_dict()
        return stats
    
    async def get_stats_async(self) -> Dict[str, Any]:
        """异步获取统计信息"""
        stats = self._stats.to_dict()
        stats['size'] = await self._backend.size()
        return stats
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


class MultiLevelCache(CacheManager):
    """多级缓存管理器
    
    实现L1（内存）+ L2（持久化/分布式）两级缓存。
    """
    
    def __init__(
        self,
        l1_config: Optional[CacheConfig] = None,
        l2_backend: Optional[CacheBackend] = None
    ):
        super().__init__(l1_config)
        self._l1 = self._backend
        self._l2 = l2_backend  # 可扩展为Redis等
    
    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """获取值 - 先查L1，再查L2"""
        # L1查询
        value = await super().get(key)
        if value is not None:
            return value
        
        # L2查询（如果有）
        if self._l2:
            entry = await self._l2.get(key)
            if entry and not entry.is_expired():
                # 回填L1
                await self.set(key, entry.value)
                return entry.value
        
        return default
    
    async def set(self, key: K, value: V, ttl: Optional[float] = None, **kwargs) -> bool:
        """设置值 - 同时设置L1和L2"""
        # 设置L1
        result = await super().set(key, value, ttl, **kwargs)
        
        # 设置L2
        if self._l2:
            entry = CacheEntry(key=key, value=value, expires_at=time.time() + (ttl or self.config.ttl))
            await self._l2.set(key, entry)
        
        return result
