"""
数据转换消息队列模块

专注于数据转换消息队列、消息发布订阅、消息路由、消息管理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import hashlib
import json
import queue
import threading

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """消息优先级"""
    LOW = "low"  # 低
    NORMAL = "normal"  # 正常
    HIGH = "high"  # 高
    CRITICAL = "critical"  # 关键


class MessageStatus(Enum):
    """消息状态"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    RETRYING = "retrying"  # 重试中


class QueueType(Enum):
    """队列类型"""
    FIFO = "fifo"  # 先进先出
    PRIORITY = "priority"  # 优先级队列
    DELAYED = "delayed"  # 延迟队列
    DEAD_LETTER = "dead_letter"  # 死信队列


@dataclass
class Message:
    """消息"""
    message_id: str
    topic: str
    payload: Any
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    timestamp: datetime = None
    retry_count: int = 0
    max_retries: int = 3
    headers: Dict[str, str] = None
    metadata: Dict[str, Any] = None


@dataclass
class Queue:
    """队列"""
    queue_id: str
    queue_name: str
    queue_type: QueueType
    max_size: int = 10000
    message_ttl: int = 3600  # 秒
    enabled: bool = True
    created_at: datetime = None


@dataclass
class Subscription:
    """订阅"""
    subscription_id: str
    topic: str
    handler: Callable
    queue_name: str
    filter: Optional[Callable] = None
    enabled: bool = True
    created_at: datetime = None


class DataTransformationMessageQueue:
    """数据转换消息队列管理器"""
    
    def __init__(self):
        """初始化消息队列管理器"""
        self.queues: Dict[str, Queue] = {}
        self.messages: Dict[str, Message] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.message_queues: Dict[str, queue.Queue] = {}  # 实际的消息队列
        self.workers: Dict[str, threading.Thread] = {}
        self.queue_config: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def create_queue(
        self,
        queue_name: str,
        queue_type: QueueType = QueueType.FIFO,
        max_size: int = 10000,
        message_ttl: int = 3600
    ) -> Queue:
        """创建队列"""
        queue_id = f"queue_{hashlib.md5(queue_name.encode()).hexdigest()[:8]}"
        
        queue_obj = Queue(
            queue_id=queue_id,
            queue_name=queue_name,
            queue_type=queue_type,
            max_size=max_size,
            message_ttl=message_ttl,
            created_at=datetime.now()
        )
        
        self.queues[queue_id] = queue_obj
        self.message_queues[queue_name] = queue.Queue(maxsize=max_size)
        
        logger.info(f"创建队列: {queue_name} ({queue_id})")
        
        return queue_obj
    
    def publish_message(
        self,
        topic: str,
        payload: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        headers: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> Message:
        """发布消息"""
        message_id = f"msg_{hashlib.md5(f'{topic}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        message = Message(
            message_id=message_id,
            topic=topic,
            payload=payload,
            priority=priority,
            timestamp=datetime.now(),
            headers=headers or {},
            metadata=metadata or {}
        )
        
        self.messages[message_id] = message
        
        # 查找订阅该主题的队列
        subscribed_queues = [
            sub.queue_name for sub in self.subscriptions.values()
            if sub.topic == topic and sub.enabled
        ]
        
        if not subscribed_queues:
            logger.warning(f"主题 {topic} 没有订阅者")
            return message
        
        # 将消息发送到所有订阅的队列
        for queue_name in subscribed_queues:
            if queue_name in self.message_queues:
                try:
                    self.message_queues[queue_name].put_nowait(message)
                    logger.info(f"发布消息到队列: {topic} -> {queue_name} ({message_id})")
                except queue.Full:
                    logger.error(f"队列已满: {queue_name}")
                    message.status = MessageStatus.FAILED
        
        return message
    
    def subscribe(
        self,
        topic: str,
        handler: Callable,
        queue_name: str,
        filter: Optional[Callable] = None
    ) -> Subscription:
        """订阅主题"""
        subscription_id = f"sub_{hashlib.md5(f'{topic}_{queue_name}'.encode()).hexdigest()[:8]}"
        
        subscription = Subscription(
            subscription_id=subscription_id,
            topic=topic,
            handler=handler,
            queue_name=queue_name,
            filter=filter,
            created_at=datetime.now()
        )
        
        self.subscriptions[subscription_id] = subscription
        
        # 启动工作线程处理消息
        if queue_name not in self.workers:
            self._start_worker(queue_name)
        
        logger.info(f"订阅主题: {topic} -> {queue_name} ({subscription_id})")
        
        return subscription
    
    def _start_worker(self, queue_name: str):
        """启动工作线程"""
        def worker():
            message_queue = self.message_queues.get(queue_name)
            if not message_queue:
                return
            
            while True:
                try:
                    message = message_queue.get(timeout=1)
                    if message is None:
                        break
                    
                    # 查找处理该消息的订阅
                    subscriptions = [
                        sub for sub in self.subscriptions.values()
                        if sub.queue_name == queue_name
                        and sub.topic == message.topic
                        and sub.enabled
                    ]
                    
                    for subscription in subscriptions:
                        # 应用过滤器
                        if subscription.filter and not subscription.filter(message):
                            continue
                        
                        # 更新消息状态
                        message.status = MessageStatus.PROCESSING
                        self.messages[message.message_id] = message
                        
                        try:
                            # 执行处理器
                            subscription.handler(message)
                            
                            message.status = MessageStatus.COMPLETED
                            logger.info(f"消息处理成功: {message.message_id}")
                            
                        except Exception as e:
                            message.status = MessageStatus.FAILED
                            message.retry_count += 1
                            
                            logger.error(f"消息处理失败: {message.message_id} - {str(e)}")
                            
                            # 重试逻辑
                            if message.retry_count < message.max_retries:
                                message.status = MessageStatus.RETRYING
                                # 重新加入队列
                                message_queue.put(message)
                            else:
                                # 发送到死信队列
                                self._send_to_dead_letter_queue(message)
                        
                        finally:
                            self.messages[message.message_id] = message
                            message_queue.task_done()
                
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"工作线程错误: {str(e)}")
        
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        self.workers[queue_name] = worker_thread
    
    def _send_to_dead_letter_queue(self, message: Message):
        """发送到死信队列"""
        dead_letter_queue_name = f"{message.topic}_dead_letter"
        
        if dead_letter_queue_name not in self.message_queues:
            self.create_queue(dead_letter_queue_name, QueueType.DEAD_LETTER)
        
        try:
            self.message_queues[dead_letter_queue_name].put_nowait(message)
            logger.warning(f"消息发送到死信队列: {message.message_id} -> {dead_letter_queue_name}")
        except queue.Full:
            logger.error(f"死信队列已满: {dead_letter_queue_name}")
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """获取消息"""
        return self.messages.get(message_id)
    
    def get_queue_statistics(self, queue_name: str) -> Dict[str, Any]:
        """获取队列统计信息"""
        message_queue = self.message_queues.get(queue_name)
        if not message_queue:
            return {}
        
        total_messages = len([
            m for m in self.messages.values()
            if any(
                sub.queue_name == queue_name and sub.topic == m.topic
                for sub in self.subscriptions.values()
            )
        ])
        
        pending_messages = len([
            m for m in self.messages.values()
            if m.status == MessageStatus.PENDING
            and any(
                sub.queue_name == queue_name and sub.topic == m.topic
                for sub in self.subscriptions.values()
            )
        ])
        
        completed_messages = len([
            m for m in self.messages.values()
            if m.status == MessageStatus.COMPLETED
            and any(
                sub.queue_name == queue_name and sub.topic == m.topic
                for sub in self.subscriptions.values()
            )
        ])
        
        failed_messages = len([
            m for m in self.messages.values()
            if m.status == MessageStatus.FAILED
            and any(
                sub.queue_name == queue_name and sub.topic == m.topic
                for sub in self.subscriptions.values()
            )
        ])
        
        return {
            "queue_name": queue_name,
            "queue_size": message_queue.qsize(),
            "total_messages": total_messages,
            "pending_messages": pending_messages,
            "completed_messages": completed_messages,
            "failed_messages": failed_messages,
            "success_rate": completed_messages / total_messages if total_messages > 0 else 0
        }
    
    def get_message_statistics(self) -> Dict[str, Any]:
        """获取消息统计信息"""
        total_messages = len(self.messages)
        
        messages_by_status = {}
        for message in self.messages.values():
            status = message.status.value
            messages_by_status[status] = messages_by_status.get(status, 0) + 1
        
        messages_by_priority = {}
        for message in self.messages.values():
            priority = message.priority.value
            messages_by_priority[priority] = messages_by_priority.get(priority, 0) + 1
        
        return {
            "total_messages": total_messages,
            "messages_by_status": messages_by_status,
            "messages_by_priority": messages_by_priority,
            "total_queues": len(self.queues),
            "total_subscriptions": len(self.subscriptions)
        }
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        if subscription_id not in self.subscriptions:
            return False
        
        del self.subscriptions[subscription_id]
        logger.info(f"取消订阅: {subscription_id}")
        
        return True
    
    def delete_queue(self, queue_name: str) -> bool:
        """删除队列"""
        queue_obj = next(
            (q for q in self.queues.values() if q.queue_name == queue_name),
            None
        )
        
        if not queue_obj:
            return False
        
        # 停止工作线程
        if queue_name in self.workers:
            # 发送停止信号
            if queue_name in self.message_queues:
                self.message_queues[queue_name].put(None)
            del self.workers[queue_name]
        
        # 删除队列
        del self.queues[queue_obj.queue_id]
        if queue_name in self.message_queues:
            del self.message_queues[queue_name]
        
        logger.info(f"删除队列: {queue_name}")
        
        return True


class MessageFilter:
    """消息过滤器"""
    
    @staticmethod
    def priority_filter(min_priority: MessagePriority) -> Callable:
        """优先级过滤器"""
        def filter_func(message: Message) -> bool:
            priority_order = {
                MessagePriority.LOW: 1,
                MessagePriority.NORMAL: 2,
                MessagePriority.HIGH: 3,
                MessagePriority.CRITICAL: 4
            }
            return priority_order.get(message.priority, 0) >= priority_order.get(min_priority, 0)
        return filter_func
    
    @staticmethod
    def header_filter(header_key: str, header_value: str) -> Callable:
        """头部过滤器"""
        def filter_func(message: Message) -> bool:
            return message.headers.get(header_key) == header_value
        return filter_func
    
    @staticmethod
    def topic_filter(topic_pattern: str) -> Callable:
        """主题过滤器"""
        def filter_func(message: Message) -> bool:
            return topic_pattern in message.topic
        return filter_func
