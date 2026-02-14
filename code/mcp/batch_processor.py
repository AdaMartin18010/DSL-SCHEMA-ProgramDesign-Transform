"""
MCP请求批处理优化模块

提供高效的请求批处理功能，支持：
- 自动批量处理
- 时间窗口触发
- 优先级队列
- 批量压缩
- 自适应批大小

示例：
    >>> config = BatchConfig(batch_size=100, flush_interval=0.1)
    >>> processor = BatchProcessor(config)
    >>> await processor.start()
    >>> result = await processor.submit(request)
    >>> await processor.stop()
"""

import asyncio
import logging
import time
import zlib
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, AsyncIterator
from functools import total_ordering
import heapq

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class Priority(IntEnum):
    """请求优先级"""
    CRITICAL = 0    # 关键 - 立即处理
    HIGH = 1        # 高优先级
    NORMAL = 2      # 普通
    LOW = 3         # 低优先级
    BACKGROUND = 4  # 后台任务


@total_ordering
@dataclass
class BatchItem(Generic[T, R]):
    """批处理项目
    
    Attributes:
        data: 请求数据
        priority: 优先级
        timestamp: 创建时间戳
        future: 异步Future对象（用于返回结果）
        id: 唯一标识
        metadata: 额外元数据
    """
    data: T
    priority: Priority = Priority.NORMAL
    timestamp: float = field(default_factory=time.time)
    future: Optional[asyncio.Future] = field(default=None)
    id: int = field(default=0)
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    
    _id_counter: int = 0
    
    def __post_init__(self):
        if self.id == 0:
            BatchItem._id_counter += 1
            self.id = BatchItem._id_counter
        if self.future is None:
            self.future = asyncio.get_event_loop().create_future()
    
    def __lt__(self, other):
        if not isinstance(other, BatchItem):
            return NotImplemented
        # 优先级高的在前，同优先级按时间先后
        return (self.priority, self.timestamp) < (other.priority, other.timestamp)
    
    def __eq__(self, other):
        if not isinstance(other, BatchItem):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def is_expired(self, timeout: float) -> bool:
        """检查是否已超时"""
        return time.time() - self.timestamp > timeout
    
    def set_result(self, result: R):
        """设置结果"""
        if self.future and not self.future.done():
            self.future.set_result(result)
    
    def set_exception(self, exception: Exception):
        """设置异常"""
        if self.future and not self.future.done():
            self.future.set_exception(exception)


class BatchStrategy(Enum):
    """批处理策略"""
    FIXED_SIZE = "fixed_size"           # 固定大小
    TIME_WINDOW = "time_window"         # 时间窗口
    ADAPTIVE = "adaptive"               # 自适应
    PRIORITY_BASED = "priority_based"   # 基于优先级


@dataclass
class BatchConfig:
    """批处理配置
    
    Attributes:
        batch_size: 批处理大小
        max_batch_size: 最大批大小（自适应模式）
        min_batch_size: 最小批大小（自适应模式）
        flush_interval: 刷新间隔（秒）
        max_wait_time: 最大等待时间（秒）
        strategy: 批处理策略
        enable_compression: 是否启用压缩
        compression_threshold: 压缩阈值（字节）
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        enable_deduplication: 是否启用去重
        dedup_window: 去重窗口（秒）
        worker_count: 工作线程数
        queue_capacity: 队列容量
        timeout: 单项超时时间（秒）
    """
    batch_size: int = 100
    max_batch_size: int = 500
    min_batch_size: int = 10
    flush_interval: float = 0.1
    max_wait_time: float = 5.0
    strategy: BatchStrategy = BatchStrategy.ADAPTIVE
    enable_compression: bool = True
    compression_threshold: int = 1024
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_deduplication: bool = False
    dedup_window: float = 60.0
    worker_count: int = 2
    queue_capacity: int = 10000
    timeout: float = 30.0
    
    def __post_init__(self):
        if self.min_batch_size > self.batch_size:
            self.min_batch_size = self.batch_size
        if self.max_batch_size < self.batch_size:
            self.max_batch_size = self.batch_size


class BatchMetrics:
    """批处理指标统计"""
    
    def __init__(self):
        self.total_submitted: int = 0
        self.total_processed: int = 0
        self.total_failed: int = 0
        self.total_retried: int = 0
        self.total_deduplicated: int = 0
        self.total_batches: int = 0
        self.avg_batch_size: float = 0.0
        self.avg_processing_time: float = 0.0
        self.avg_wait_time: float = 0.0
        self.queue_size_history: deque = deque(maxlen=100)
        self._batch_sizes: deque = deque(maxlen=100)
        self._processing_times: deque = deque(maxlen=100)
        self._wait_times: deque = deque(maxlen=100)
        self._started_at: float = time.time()
    
    def record_submit(self):
        """记录提交"""
        self.total_submitted += 1
    
    def record_process(self, batch_size: int, processing_time: float, wait_time: float):
        """记录处理"""
        self.total_processed += batch_size
        self.total_batches += 1
        
        self._batch_sizes.append(batch_size)
        self._processing_times.append(processing_time)
        self._wait_times.append(wait_time)
        
        self.avg_batch_size = sum(self._batch_sizes) / len(self._batch_sizes)
        self.avg_processing_time = sum(self._processing_times) / len(self._processing_times)
        self.avg_wait_time = sum(self._wait_times) / len(self._wait_times)
    
    def record_failure(self, count: int = 1):
        """记录失败"""
        self.total_failed += count
    
    def record_retry(self):
        """记录重试"""
        self.total_retried += 1
    
    def record_dedup(self):
        """记录去重"""
        self.total_deduplicated += 1
    
    def update_queue_size(self, size: int):
        """更新队列大小历史"""
        self.queue_size_history.append(size)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_submitted": self.total_submitted,
            "total_processed": self.total_processed,
            "total_failed": self.total_failed,
            "total_retried": self.total_retried,
            "total_deduplicated": self.total_deduplicated,
            "total_batches": self.total_batches,
            "avg_batch_size": round(self.avg_batch_size, 2),
            "avg_processing_time": round(self.avg_processing_time, 4),
            "avg_wait_time": round(self.avg_wait_time, 4),
            "throughput": round(self.total_processed / (time.time() - self._started_at + 0.001), 2),
            "current_queue_size": self.queue_size_history[-1] if self.queue_size_history else 0,
        }


class BatchProcessor(Generic[T, R]):
    """MCP请求批处理器
    
    高性能批处理实现，支持优先级队列、自适应批大小和压缩。
    
    核心特性：
    1. 优先级队列支持
    2. 多种批处理策略
    3. 自动压缩大请求
    4. 请求去重
    5. 完整的指标统计
    
    使用示例：
        >>> config = BatchConfig(batch_size=100, flush_interval=0.1)
        >>> processor = BatchProcessor(config, process_func=my_handler)
        >>> await processor.start()
        >>> 
        >>> # 提交请求
        >>> result = await processor.submit(data, priority=Priority.HIGH)
        >>> 
        >>> # 批量提交
        >>> results = await processor.submit_many([data1, data2, data3])
        >>> 
        >>> await processor.stop()
    
    Attributes:
        config: 批处理配置
        _queue: 优先级队列
        _process_func: 处理函数
        _metrics: 性能指标
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        process_func: Optional[Callable[[List[T]], List[R]]] = None
    ):
        self.config = config or BatchConfig()
        self._process_func = process_func or self._default_process_func
        
        # 队列
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=self.config.queue_capacity
        )
        self._emergency_queue: deque = deque()  # 高优先级紧急队列
        
        # 状态
        self._is_running: bool = False
        self._is_stopping: bool = False
        self._flush_event: asyncio.Event = asyncio.Event()
        self._shutdown_event: asyncio.Event = asyncio.Event()
        
        # 工作线程
        self._workers: List[asyncio.Task] = []
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # 去重
        self._recent_hashes: Dict[int, float] = {}
        self._dedup_lock: asyncio.Lock = asyncio.Lock()
        
        # 指标
        self._metrics = BatchMetrics()
        
        # 自适应调整
        self._current_batch_size: int = self.config.batch_size
        self._performance_history: deque = deque(maxlen=10)
    
    @staticmethod
    def _default_process_func(items: List[T]) -> List[R]:
        """默认处理函数 - 简单返回"""
        return [f"processed_{item}" for item in items]  # type: ignore
    
    async def start(self):
        """启动批处理器"""
        if self._is_running:
            return
        
        self._is_running = True
        self._is_stopping = False
        
        # 启动工作线程
        for i in range(self.config.worker_count):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)
        
        # 启动调度器
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info(f"Batch processor started with {self.config.worker_count} workers")
    
    async def stop(self, timeout: float = 30.0):
        """停止批处理器
        
        Args:
            timeout: 等待处理完成的超时时间
        """
        if not self._is_running:
            return
        
        self._is_stopping = True
        self._flush_event.set()
        
        try:
            # 等待队列清空
            await asyncio.wait_for(
                self._wait_for_empty(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Stop timeout reached, forcing shutdown")
        
        self._is_running = False
        self._shutdown_event.set()
        
        # 取消工作线程
        for worker in self._workers:
            worker.cancel()
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
        
        # 等待所有任务完成
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        # 处理剩余项目
        await self._drain_remaining()
        
        logger.info("Batch processor stopped")
    
    async def _wait_for_empty(self):
        """等待队列为空"""
        while not self._queue.empty() or self._emergency_queue:
            await asyncio.sleep(0.01)
    
    async def _drain_remaining(self):
        """处理剩余项目"""
        remaining: List[BatchItem] = []
        
        # 收集剩余项目
        while not self._queue.empty():
            try:
                _, item = self._queue.get_nowait()
                remaining.append(item)
            except asyncio.QueueEmpty:
                break
        
        remaining.extend(self._emergency_queue)
        
        # 处理剩余批次
        if remaining:
            logger.info(f"Draining {len(remaining)} remaining items")
            await self._process_batch(remaining)
    
    async def submit(
        self,
        data: T,
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> R:
        """提交单个请求
        
        Args:
            data: 请求数据
            priority: 优先级
            metadata: 元数据
            
        Returns:
            处理结果
            
        Raises:
            asyncio.TimeoutError: 处理超时
            RuntimeError: 处理器未运行
        """
        if not self._is_running:
            raise RuntimeError("Batch processor is not running")
        
        # 去重检查
        if self.config.enable_deduplication:
            if await self._check_duplicate(data):
                self._metrics.record_dedup()
                raise ValueError("Duplicate request detected")
        
        item = BatchItem(
            data=data,
            priority=priority,
            metadata=metadata or {}
        )
        
        self._metrics.record_submit()
        
        # 高优先级直接放入紧急队列
        if priority == Priority.CRITICAL:
            self._emergency_queue.append(item)
            self._flush_event.set()
        else:
            await self._queue.put((priority.value, item))
        
        self._metrics.update_queue_size(self._queue.qsize() + len(self._emergency_queue))
        
        # 等待结果
        try:
            result = await asyncio.wait_for(item.future, timeout=self.config.timeout)
            return result
        except asyncio.TimeoutError:
            item.set_exception(TimeoutError(f"Request timed out after {self.config.timeout}s"))
            self._metrics.record_failure()
            raise
    
    async def submit_many(
        self,
        items: List[T],
        priority: Priority = Priority.NORMAL
    ) -> List[R]:
        """批量提交请求
        
        Args:
            items: 请求数据列表
            priority: 优先级
            
        Returns:
            结果列表
        """
        futures = []
        for data in items:
            item = BatchItem(data=data, priority=priority)
            self._metrics.record_submit()
            await self._queue.put((priority.value, item))
            futures.append(item.future)
        
        self._metrics.update_queue_size(self._queue.qsize())
        
        # 等待所有结果
        results = await asyncio.gather(*futures, return_exceptions=True)
        return results  # type: ignore
    
    async def _check_duplicate(self, data: T) -> bool:
        """检查是否为重复请求"""
        try:
            data_hash = hash(str(data))
        except Exception:
            return False
        
        async with self._dedup_lock:
            now = time.time()
            
            # 清理过期记录
            self._recent_hashes = {
                h: t for h, t in self._recent_hashes.items()
                if now - t < self.config.dedup_window
            }
            
            if data_hash in self._recent_hashes:
                return True
            
            self._recent_hashes[data_hash] = now
            return False
    
    async def _scheduler_loop(self):
        """调度器循环 - 基于时间窗口触发刷新"""
        while self._is_running and not self._is_stopping:
            try:
                await asyncio.wait_for(
                    self._flush_event.wait(),
                    timeout=self.config.flush_interval
                )
                self._flush_event.clear()
            except asyncio.TimeoutError:
                pass
            
            # 触发刷新
            if self._queue.qsize() > 0 or self._emergency_queue:
                await self._trigger_flush()
    
    async def _trigger_flush(self):
        """触发刷新批次"""
        batch = await self._collect_batch()
        if batch:
            await self._process_batch(batch)
    
    async def _collect_batch(self) -> List[BatchItem]:
        """收集批次"""
        batch: List[BatchItem] = []
        batch_size = self._current_batch_size
        
        # 首先处理紧急队列
        while self._emergency_queue and len(batch) < batch_size:
            batch.append(self._emergency_queue.popleft())
        
        # 从主队列收集
        deadline = time.time() + self.config.max_wait_time
        
        while len(batch) < batch_size and time.time() < deadline:
            try:
                timeout = max(0, deadline - time.time())
                _, item = await asyncio.wait_for(self._queue.get(), timeout=timeout)
                batch.append(item)
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Error collecting item: {e}")
                break
        
        return batch
    
    async def _worker_loop(self, worker_id: int):
        """工作线程循环"""
        logger.debug(f"Worker {worker_id} started")
        
        while self._is_running:
            try:
                # 收集批次
                batch = await self._collect_batch()
                
                if not batch:
                    await asyncio.sleep(0.001)
                    continue
                
                # 处理批次
                await self._process_batch(batch)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.debug(f"Worker {worker_id} stopped")
    
    async def _process_batch(self, batch: List[BatchItem]):
        """处理批次
        
        Args:
            batch: 批处理项目列表
        """
        if not batch:
            return
        
        start_time = time.time()
        
        try:
            # 提取数据
            data_list = [item.data for item in batch]
            
            # 压缩（如果需要）
            if self.config.enable_compression:
                data_list = await self._compress_batch(data_list)
            
            # 执行处理
            results = await self._execute_with_retry(data_list)
            
            # 分发结果
            for item, result in zip(batch, results):
                item.set_result(result)
            
            # 记录指标
            processing_time = time.time() - start_time
            wait_time = start_time - batch[0].timestamp if batch else 0
            self._metrics.record_process(len(batch), processing_time, wait_time)
            
            # 自适应调整
            if self.config.strategy == BatchStrategy.ADAPTIVE:
                await self._adapt_batch_size(processing_time, len(batch))
                
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            # 设置所有项目为失败
            for item in batch:
                item.set_exception(e)
            self._metrics.record_failure(len(batch))
    
    async def _compress_batch(self, data_list: List[T]) -> List[T]:
        """压缩批次数据"""
        # 简化实现：实际应根据数据类型进行压缩
        return data_list
    
    async def _execute_with_retry(self, data_list: List[T]) -> List[R]:
        """带重试的执行"""
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                if asyncio.iscoroutinefunction(self._process_func):
                    return await self._process_func(data_list)
                else:
                    return self._process_func(data_list)
            except Exception as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    self._metrics.record_retry()
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        raise last_exception or RuntimeError("All retry attempts failed")
    
    async def _adapt_batch_size(self, processing_time: float, batch_size: int):
        """自适应调整批大小
        
        根据处理时间动态调整批大小以优化吞吐量。
        """
        self._performance_history.append((batch_size, processing_time))
        
        if len(self._performance_history) < 5:
            return
        
        # 计算最近效率
        recent_throughput = sum(s / max(t, 0.001) for s, t in self._performance_history) / len(self._performance_history)
        
        # 如果处理时间太长，减小批大小
        if processing_time > self.config.flush_interval * 2:
            self._current_batch_size = max(
                self.config.min_batch_size,
                int(self._current_batch_size * 0.9)
            )
        # 如果处理时间很短且队列积压，增加批大小
        elif processing_time < self.config.flush_interval * 0.5 and self._queue.qsize() > batch_size:
            self._current_batch_size = min(
                self.config.max_batch_size,
                int(self._current_batch_size * 1.1)
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return self._metrics.to_dict()
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self._queue.qsize() + len(self._emergency_queue)
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


class StreamingBatchProcessor(BatchProcessor):
    """流式批处理器
    
    支持流式处理的批处理器，适用于大数据量场景。
    """
    
    async def submit_stream(
        self,
        data_stream: AsyncIterator[T],
        priority: Priority = Priority.NORMAL
    ) -> AsyncIterator[R]:
        """提交流式数据
        
        Args:
            data_stream: 数据流
            priority: 优先级
            
        Yields:
            处理结果
        """
        buffer: List[BatchItem] = []
        
        async for data in data_stream:
            item = BatchItem(data=data, priority=priority)
            buffer.append(item)
            
            if len(buffer) >= self._current_batch_size:
                await self._process_batch(buffer)
                for item in buffer:
                    if item.future.done():
                        yield await item.future
                buffer.clear()
        
        # 处理剩余
        if buffer:
            await self._process_batch(buffer)
            for item in buffer:
                if item.future.done():
                    yield await item.future
