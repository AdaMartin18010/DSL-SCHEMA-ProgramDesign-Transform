"""
MCP连接池优化模块

提供高效的连接管理，支持：
- 连接复用和池化管理
- 动态连接扩容/缩容
- 连接健康检查
- 连接超时管理
- 负载均衡策略

示例：
    >>> config = ConnectionPoolConfig(max_connections=20, min_connections=5)
    >>> pool = ConnectionPool(config)
    >>> async with pool.acquire() as conn:
    ...     result = await conn.execute("query")
"""

import asyncio
import logging
import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set, TypeVar, Generic
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConnectionState(Enum):
    """连接状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    CLOSED = "closed"
    UNHEALTHY = "unhealthy"


@dataclass
class ConnectionPoolConfig:
    """连接池配置类
    
    Attributes:
        max_connections: 最大连接数
        min_connections: 最小连接数（保持空闲）
        connection_timeout: 连接超时时间（秒）
        idle_timeout: 空闲连接超时时间（秒）
        max_lifetime: 连接最大生命周期（秒）
        health_check_interval: 健康检查间隔（秒）
        acquire_timeout: 获取连接超时时间（秒）
        enable_warmup: 是否启用连接预热
        warmup_size: 预热连接数
        load_balance_strategy: 负载均衡策略
        retry_attempts: 连接重试次数
        retry_delay: 重试延迟（秒）
    """
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: float = 10.0
    idle_timeout: float = 300.0
    max_lifetime: float = 3600.0
    health_check_interval: float = 60.0
    acquire_timeout: float = 5.0
    enable_warmup: bool = True
    warmup_size: int = 3
    load_balance_strategy: str = "round_robin"  # round_robin, least_busy, random
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_metrics: bool = True
    
    def __post_init__(self):
        if self.min_connections > self.max_connections:
            raise ValueError("min_connections cannot be greater than max_connections")
        if self.warmup_size > self.max_connections:
            self.warmup_size = self.max_connections


class ConnectionMetrics:
    """连接池指标统计"""
    
    def __init__(self):
        self.total_connections: int = 0
        self.active_connections: int = 0
        self.idle_connections: int = 0
        self.waiting_requests: int = 0
        self.total_requests: int = 0
        self.failed_requests: int = 0
        self.avg_wait_time: float = 0.0
        self._wait_times: deque = deque(maxlen=100)
        self._created_at: float = time.time()
    
    def record_wait_time(self, wait_time: float):
        """记录等待时间"""
        self._wait_times.append(wait_time)
        self.avg_wait_time = sum(self._wait_times) / len(self._wait_times)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "waiting_requests": self.waiting_requests,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "avg_wait_time": round(self.avg_wait_time, 4),
            "uptime": round(time.time() - self._created_at, 2),
        }


class PooledConnection:
    """池化连接封装类
    
    包装实际连接对象，提供状态管理和元数据跟踪。
    
    Attributes:
        id: 连接唯一标识
        connection: 实际连接对象
        state: 连接状态
        created_at: 创建时间
        last_used_at: 最后使用时间
        use_count: 使用次数
    """
    
    _id_counter: int = 0
    _lock: asyncio.Lock = asyncio.Lock()
    
    def __init__(self, connection: Any):
        self.connection = connection
        self.state: ConnectionState = ConnectionState.IDLE
        self.created_at: float = time.time()
        self.last_used_at: float = time.time()
        self.use_count: int = 0
        self.health_check_failures: int = 0
        
        self._assign_id_sync()
    
    def _assign_id_sync(self):
        PooledConnection._id_counter += 1
        self.id: int = PooledConnection._id_counter
    
    def mark_busy(self):
        """标记为忙碌状态"""
        self.state = ConnectionState.BUSY
        self.last_used_at = time.time()
        self.use_count += 1
    
    def mark_idle(self):
        """标记为空闲状态"""
        self.state = ConnectionState.IDLE
        self.last_used_at = time.time()
    
    def mark_unhealthy(self):
        """标记为不健康状态"""
        self.state = ConnectionState.UNHEALTHY
        self.health_check_failures += 1
    
    def mark_closed(self):
        """标记为已关闭"""
        self.state = ConnectionState.CLOSED
    
    def is_expired(self, max_lifetime: float, idle_timeout: float) -> bool:
        """检查连接是否过期"""
        now = time.time()
        if now - self.created_at > max_lifetime:
            return True
        if self.state == ConnectionState.IDLE and now - self.last_used_at > idle_timeout:
            return True
        return False
    
    def is_healthy(self) -> bool:
        """检查连接是否健康"""
        return self.state not in (ConnectionState.CLOSED, ConnectionState.UNHEALTHY)
    
    async def close(self):
        """关闭连接"""
        self.mark_closed()
        if hasattr(self.connection, 'close'):
            if asyncio.iscoroutinefunction(self.connection.close):
                await self.connection.close()
            else:
                self.connection.close()
    
    def __repr__(self) -> str:
        return f"PooledConnection(id={self.id}, state={self.state.value}, use_count={self.use_count})"


class ConnectionPool:
    """MCP连接池管理器
    
    高性能连接池实现，支持异步操作、自动扩缩容和健康检查。
    
    核心特性：
    1. 异步获取/释放连接
    2. 动态连接池大小调整
    3. 连接健康检查和自动恢复
    4. 多种负载均衡策略
    5. 完整的指标统计
    
    使用示例：
        >>> pool = ConnectionPool(config)
        >>> await pool.initialize()
        >>> 
        >>> # 方式1: 使用 async with
        >>> async with pool.acquire() as conn:
        ...     await conn.execute("SELECT * FROM data")
        >>> 
        >>> # 方式2: 手动获取/释放
        >>> conn = await pool.get_connection()
        >>> try:
        ...     await conn.execute("SELECT * FROM data")
        >>> finally:
        ...     await pool.release(conn)
        >>> 
        >>> await pool.close()
    
    Attributes:
        config: 连接池配置
        _pool: 连接池队列
        _semaphore: 连接数量信号量
        _connection_factory: 连接创建工厂函数
        _metrics: 性能指标统计
    """
    
    def __init__(
        self,
        config: Optional[ConnectionPoolConfig] = None,
        connection_factory: Optional[Callable[[], Any]] = None
    ):
        self.config = config or ConnectionPoolConfig()
        self._connection_factory = connection_factory or self._default_connection_factory
        
        # 连接池数据结构
        self._pool: deque = deque()
        self._all_connections: Set[PooledConnection] = set()
        self._busy_connections: Set[PooledConnection] = set()
        
        # 同步原语
        self._lock: asyncio.Lock = asyncio.Lock()
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(self.config.max_connections)
        self._condition: asyncio.Condition = asyncio.Condition(self._lock)
        
        # 后台任务
        self._health_check_task: Optional[asyncio.Task] = None
        self._maintenance_task: Optional[asyncio.Task] = None
        self._is_initialized: bool = False
        self._is_closing: bool = False
        
        # 指标
        self._metrics = ConnectionMetrics()
        self._round_robin_index: int = 0
        
        # 等待队列
        self._waiting_queue: deque = deque()
    
    @staticmethod
    def _default_connection_factory() -> Any:
        """默认连接工厂 - 创建一个模拟连接"""
        return MockMCPConnection()
    
    async def initialize(self):
        """初始化连接池
        
        执行以下操作：
        1. 创建最小连接数
        2. 启动健康检查任务
        3. 启动维护任务
        4. 预热连接（如果启用）
        """
        if self._is_initialized:
            return
        
        async with self._lock:
            # 创建最小连接数
            for _ in range(self.config.min_connections):
                conn = await self._create_connection()
                self._pool.append(conn)
                self._all_connections.add(conn)
            
            self._metrics.total_connections = len(self._all_connections)
            logger.info(f"Connection pool initialized with {len(self._pool)} connections")
            
            # 预热连接
            if self.config.enable_warmup:
                await self._warmup_connections()
            
            # 启动后台任务
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())
            
            self._is_initialized = True
    
    async def _create_connection(self, retry_count: int = 0) -> PooledConnection:
        """创建新连接（带重试机制）"""
        try:
            raw_conn = await asyncio.wait_for(
                self._do_create_connection(),
                timeout=self.config.connection_timeout
            )
            return PooledConnection(raw_conn)
        except Exception as e:
            if retry_count < self.config.retry_attempts:
                logger.warning(f"Connection creation failed, retrying... ({retry_count + 1}/{self.config.retry_attempts})")
                await asyncio.sleep(self.config.retry_delay)
                return await self._create_connection(retry_count + 1)
            raise ConnectionError(f"Failed to create connection after {self.config.retry_attempts} attempts: {e}")
    
    async def _do_create_connection(self) -> Any:
        """执行实际连接创建"""
        if asyncio.iscoroutinefunction(self._connection_factory):
            return await self._connection_factory()
        return self._connection_factory()
    
    async def _warmup_connections(self):
        """预热连接"""
        warmup_count = min(self.config.warmup_size, self.config.max_connections - len(self._pool))
        tasks = [self._create_connection() for _ in range(warmup_count)]
        
        try:
            connections = await asyncio.gather(*tasks)
            async with self._lock:
                for conn in connections:
                    self._pool.append(conn)
                    self._all_connections.add(conn)
                self._metrics.total_connections = len(self._all_connections)
            logger.info(f"Warmed up {len(connections)} connections")
        except Exception as e:
            logger.warning(f"Warmup partially failed: {e}")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while not self._is_closing:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _perform_health_check(self):
        """执行健康检查"""
        unhealthy_connections: List[PooledConnection] = []
        
        async with self._lock:
            for conn in list(self._all_connections):
                if conn.state == ConnectionState.BUSY:
                    continue
                
                is_healthy = await self._check_connection_health(conn)
                if not is_healthy:
                    unhealthy_connections.append(conn)
                    conn.mark_unhealthy()
        
        # 替换不健康的连接
        for conn in unhealthy_connections:
            await self._replace_connection(conn)
            logger.info(f"Replaced unhealthy connection {conn.id}")
    
    async def _check_connection_health(self, conn: PooledConnection) -> bool:
        """检查单个连接的健康状态"""
        try:
            if hasattr(conn.connection, 'ping'):
                if asyncio.iscoroutinefunction(conn.connection.ping):
                    await asyncio.wait_for(conn.connection.ping(), timeout=5.0)
                else:
                    conn.connection.ping()
                return True
            return conn.is_healthy()
        except Exception:
            return False
    
    async def _replace_connection(self, old_conn: PooledConnection):
        """替换不健康的连接"""
        try:
            new_conn = await self._create_connection()
            
            async with self._lock:
                self._all_connections.discard(old_conn)
                self._pool = deque(c for c in self._pool if c != old_conn)
                self._pool.append(new_conn)
                self._all_connections.add(new_conn)
                self._metrics.total_connections = len(self._all_connections)
            
            await old_conn.close()
        except Exception as e:
            logger.error(f"Failed to replace connection: {e}")
    
    async def _maintenance_loop(self):
        """维护循环 - 清理过期连接"""
        while not self._is_closing:
            try:
                await asyncio.sleep(30)  # 每30秒执行一次维护
                await self._cleanup_expired_connections()
                await self._adjust_pool_size()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance error: {e}")
    
    async def _cleanup_expired_connections(self):
        """清理过期连接"""
        expired_connections: List[PooledConnection] = []
        
        async with self._lock:
            current_size = len(self._pool)
            # 保留最小连接数
            to_check = list(self._pool)[:max(0, current_size - self.config.min_connections)]
            
            for conn in to_check:
                if conn.is_expired(self.config.max_lifetime, self.config.idle_timeout):
                    expired_connections.append(conn)
                    self._pool.remove(conn)
                    self._all_connections.discard(conn)
            
            self._metrics.total_connections = len(self._all_connections)
        
        # 关闭过期连接
        for conn in expired_connections:
            await conn.close()
            logger.debug(f"Closed expired connection {conn.id}")
    
    async def _adjust_pool_size(self):
        """根据负载动态调整连接池大小"""
        async with self._lock:
            current_idle = len(self._pool)
            
            # 如果空闲连接不足，考虑扩容
            if current_idle < self.config.min_connections and len(self._all_connections) < self.config.max_connections:
                needed = min(
                    self.config.min_connections - current_idle,
                    self.config.max_connections - len(self._all_connections)
                )
                
                for _ in range(needed):
                    try:
                        conn = await self._create_connection()
                        self._pool.append(conn)
                        self._all_connections.add(conn)
                    except Exception as e:
                        logger.warning(f"Failed to expand pool: {e}")
                        break
                
                self._metrics.total_connections = len(self._all_connections)
    
    async def get_connection(self) -> PooledConnection:
        """获取连接
        
        Returns:
            PooledConnection: 池化连接对象
            
        Raises:
            TimeoutError: 获取连接超时
            RuntimeError: 连接池已关闭
        """
        if not self._is_initialized:
            await self.initialize()
        
        if self._is_closing:
            raise RuntimeError("Connection pool is closing")
        
        start_time = time.time()
        self._metrics.total_requests += 1
        
        try:
            async with asyncio.timeout(self.config.acquire_timeout):
                await self._semaphore.acquire()
                
                async with self._condition:
                    while not self._pool and not self._is_closing:
                        self._metrics.waiting_requests += 1
                        await self._condition.wait()
                        self._metrics.waiting_requests -= 1
                    
                    if self._is_closing:
                        self._semaphore.release()
                        raise RuntimeError("Connection pool is closing")
                    
                    # 根据负载均衡策略选择连接
                    conn = self._select_connection()
                    conn.mark_busy()
                    self._busy_connections.add(conn)
                    self._metrics.active_connections = len(self._busy_connections)
                    self._metrics.idle_connections = len(self._pool)
                    
                    wait_time = time.time() - start_time
                    self._metrics.record_wait_time(wait_time)
                    
                    return conn
                    
        except asyncio.TimeoutError:
            self._metrics.failed_requests += 1
            raise TimeoutError(f"Failed to acquire connection within {self.config.acquire_timeout}s")
    
    def _select_connection(self) -> PooledConnection:
        """根据负载均衡策略选择连接"""
        if not self._pool:
            raise RuntimeError("No available connections")
        
        strategy = self.config.load_balance_strategy
        
        if strategy == "round_robin":
            conn = self._pool[self._round_robin_index % len(self._pool)]
            self._round_robin_index += 1
            self._pool.remove(conn)
            return conn
        
        elif strategy == "least_busy":
            # 选择使用次数最少的连接
            conn = min(self._pool, key=lambda c: c.use_count)
            self._pool.remove(conn)
            return conn
        
        elif strategy == "random":
            import random
            conn = random.choice(list(self._pool))
            self._pool.remove(conn)
            return conn
        
        else:  # 默认FIFO
            return self._pool.popleft()
    
    async def release(self, conn: PooledConnection):
        """释放连接回连接池
        
        Args:
            conn: 要释放的连接
        """
        if conn is None:
            return
        
        async with self._lock:
            if conn in self._busy_connections:
                self._busy_connections.remove(conn)
            
            if conn.is_healthy() and not conn.is_expired(self.config.max_lifetime, self.config.idle_timeout):
                conn.mark_idle()
                self._pool.append(conn)
            else:
                # 连接不健康或已过期，移除并替换
                self._all_connections.discard(conn)
                asyncio.create_task(self._replace_connection(conn))
            
            self._metrics.active_connections = len(self._busy_connections)
            self._metrics.idle_connections = len(self._pool)
            self._semaphore.release()
            self._condition.notify()
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[PooledConnection, None]:
        """上下文管理器方式获取连接
        
        使用示例：
            >>> async with pool.acquire() as conn:
            ...     result = await conn.execute("query")
        """
        conn = None
        try:
            conn = await self.get_connection()
            yield conn
        finally:
            if conn:
                await self.release(conn)
    
    async def execute(self, operation: Callable[[Any], Any], *args, **kwargs) -> Any:
        """使用连接池执行操作
        
        Args:
            operation: 要执行的操作函数
            *args, **kwargs: 传递给操作的参数
            
        Returns:
            操作结果
        """
        async with self.acquire() as conn:
            if asyncio.iscoroutinefunction(operation):
                return await operation(conn.connection, *args, **kwargs)
            return operation(conn.connection, *args, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取连接池指标"""
        return self._metrics.to_dict()
    
    async def close(self):
        """关闭连接池"""
        self._is_closing = True
        
        # 取消后台任务
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._maintenance_task:
            self._maintenance_task.cancel()
        
        # 关闭所有连接
        async with self._lock:
            close_tasks = [conn.close() for conn in self._all_connections]
            await asyncio.gather(*close_tasks, return_exceptions=True)
            
            self._pool.clear()
            self._all_connections.clear()
            self._busy_connections.clear()
        
        logger.info("Connection pool closed")
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class MockMCPConnection:
    """模拟MCP连接，用于测试"""
    
    def __init__(self):
        self.id = id(self)
        self.is_connected = True
    
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行查询"""
        await asyncio.sleep(0.01)  # 模拟延迟
        return {"query": query, "result": "success", "timestamp": time.time()}
    
    async def ping(self):
        """健康检查"""
        await asyncio.sleep(0.001)
        if not self.is_connected:
            raise ConnectionError("Connection lost")
    
    def close(self):
        """关闭连接"""
        self.is_connected = False
    
    def __repr__(self):
        return f"MockMCPConnection(id={self.id})"


def with_retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} after error: {e}")
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} after error: {e}")
                        import time
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
