"""
数据转换执行器模块

专注于数据转换执行、执行管理、执行结果处理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import threading
import time

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"  # 超时


class ExecutionPriority(Enum):
    """执行优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExecutionTask:
    """执行任务"""
    task_id: str
    task_name: str
    task_func: Callable
    priority: ExecutionPriority
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 0


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    execution_id: str
    status: ExecutionStatus
    execution_time: float
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


class DataTransformationExecutor:
    """
    数据转换执行器
    
    专注于数据转换执行、执行管理、执行结果处理
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: Dict[str, ExecutionTask] = {}
        self.execution_history: List[ExecutionResult] = []
        self.executor_active = False
        self.executor_threads: List[threading.Thread] = []
        self.task_queue: List[str] = []
        self.lock = threading.Lock()
    
    def submit_task(self, task_config: Dict[str, Any]) -> ExecutionTask:
        """
        提交任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            执行任务对象
        """
        task_id = task_config.get('task_id', f"task_{datetime.utcnow().timestamp()}")
        
        task = ExecutionTask(
            task_id=task_id,
            task_name=task_config.get('task_name', ''),
            task_func=task_config['task_func'],
            priority=ExecutionPriority(task_config.get('priority', 'normal')),
            timeout=task_config.get('timeout'),
            max_retries=task_config.get('max_retries', 0)
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self._add_to_queue(task_id)
        
        return task
    
    def _add_to_queue(self, task_id: str):
        """添加到队列"""
        task = self.tasks[task_id]
        
        # 根据优先级插入
        inserted = False
        for i, queued_id in enumerate(self.task_queue):
            queued_task = self.tasks[queued_id]
            if self._compare_priority(task.priority, queued_task.priority) > 0:
                self.task_queue.insert(i, task_id)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task_id)
    
    def _compare_priority(self, p1: ExecutionPriority, p2: ExecutionPriority) -> int:
        """比较优先级"""
        priority_order = {
            ExecutionPriority.CRITICAL: 4,
            ExecutionPriority.HIGH: 3,
            ExecutionPriority.NORMAL: 2,
            ExecutionPriority.LOW: 1
        }
        return priority_order.get(p1, 0) - priority_order.get(p2, 0)
    
    def start_executor(self):
        """启动执行器"""
        if self.executor_active:
            return
        
        self.executor_active = True
        
        for i in range(self.max_workers):
            thread = threading.Thread(target=self._worker_loop, daemon=True, name=f"Executor-{i}")
            thread.start()
            self.executor_threads.append(thread)
        
        logger.info(f"执行器已启动，工作线程数: {self.max_workers}")
    
    def stop_executor(self):
        """停止执行器"""
        self.executor_active = False
        
        for thread in self.executor_threads:
            thread.join(timeout=5)
        
        self.executor_threads.clear()
        logger.info("执行器已停止")
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.executor_active:
            try:
                task_id = self._get_next_task()
                if task_id:
                    self._execute_task(task_id)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"工作线程错误: {e}")
                time.sleep(1)
    
    def _get_next_task(self) -> Optional[str]:
        """获取下一个任务"""
        with self.lock:
            if self.task_queue:
                return self.task_queue.pop(0)
        return None
    
    def _execute_task(self, task_id: str):
        """执行任务"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = time.time()
        
        try:
            # 检查超时
            if task.timeout:
                # 简化实现，实际应该使用超时机制
                pass
            
            # 执行任务
            result = task.task_func()
            
            execution_time = time.time() - start_time
            
            execution_result = ExecutionResult(
                task_id=task_id,
                execution_id=execution_id,
                status=ExecutionStatus.COMPLETED,
                execution_time=execution_time,
                result=result,
                retry_count=task.retry_count
            )
            
            with self.lock:
                self.execution_history.append(execution_result)
        
        except Exception as e:
            logger.error(f"任务执行失败: {task.task_name}, 错误: {e}")
            execution_time = time.time() - start_time
            
            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                with self.lock:
                    self._add_to_queue(task_id)
                return
            
            execution_result = ExecutionResult(
                task_id=task_id,
                execution_id=execution_id,
                status=ExecutionStatus.FAILED,
                execution_time=execution_time,
                error=str(e),
                retry_count=task.retry_count
            )
            
            with self.lock:
                self.execution_history.append(execution_result)
    
    def get_executor_stats(self) -> Dict[str, Any]:
        """
        获取执行器统计
        
        Returns:
            执行器统计
        """
        with self.lock:
            total_tasks = len(self.tasks)
            queued_tasks = len(self.task_queue)
            total_executions = len(self.execution_history)
            successful_executions = sum(1 for e in self.execution_history if e.status == ExecutionStatus.COMPLETED)
        
        return {
            'total_tasks': total_tasks,
            'queued_tasks': queued_tasks,
            'executor_active': self.executor_active,
            'max_workers': self.max_workers,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    executor = DataTransformationExecutor(max_workers=2)
    
    # 定义任务函数
    def sample_task():
        return "任务执行完成"
    
    # 提交任务
    task = executor.submit_task({
        'task_name': '示例任务',
        'task_func': sample_task,
        'priority': 'normal'
    })
    
    print(f"任务已提交: {task.task_id}")


if __name__ == '__main__':
    main()
