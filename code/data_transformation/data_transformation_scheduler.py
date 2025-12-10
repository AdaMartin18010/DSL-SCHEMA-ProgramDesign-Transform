"""
数据转换调度器模块

专注于数据转换调度、定时任务、任务队列管理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
import time

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """调度类型"""
    ONCE = "once"  # 执行一次
    INTERVAL = "interval"  # 间隔执行
    CRON = "cron"  # Cron表达式
    DAILY = "daily"  # 每日执行
    WEEKLY = "weekly"  # 每周执行
    MONTHLY = "monthly"  # 每月执行


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class ScheduledTask:
    """调度任务"""
    task_id: str
    task_name: str
    task_func: Callable
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    status: TaskStatus
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    enabled: bool = True


@dataclass
class TaskExecutionResult:
    """任务执行结果"""
    task_id: str
    execution_id: str
    status: TaskStatus
    execution_time: float
    result: Any = None
    error: Optional[str] = None


class DataTransformationScheduler:
    """
    数据转换调度器
    
    专注于数据转换调度、定时任务、任务队列管理
    """
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.execution_history: List[TaskExecutionResult] = []
        self.scheduler_active = False
        self.scheduler_thread: Optional[threading.Thread] = None
    
    def schedule_task(self, task_config: Dict[str, Any]) -> ScheduledTask:
        """
        调度任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            调度任务对象
        """
        task_id = task_config.get('task_id', f"task_{datetime.utcnow().timestamp()}")
        
        schedule_type = ScheduleType(task_config.get('schedule_type', 'once'))
        schedule_config = task_config.get('schedule_config', {})
        
        # 计算下次执行时间
        next_run_time = self._calculate_next_run_time(schedule_type, schedule_config)
        
        task = ScheduledTask(
            task_id=task_id,
            task_name=task_config.get('task_name', ''),
            task_func=task_config['task_func'],
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            status=TaskStatus.PENDING,
            next_run_time=next_run_time,
            enabled=task_config.get('enabled', True)
        )
        
        self.tasks[task_id] = task
        return task
    
    def _calculate_next_run_time(self, schedule_type: ScheduleType,
                                 config: Dict[str, Any]) -> Optional[datetime]:
        """计算下次执行时间"""
        now = datetime.utcnow()
        
        if schedule_type == ScheduleType.ONCE:
            return now
        
        elif schedule_type == ScheduleType.INTERVAL:
            interval_seconds = config.get('interval_seconds', 3600)
            return now + timedelta(seconds=interval_seconds)
        
        elif schedule_type == ScheduleType.DAILY:
            hour = config.get('hour', 0)
            minute = config.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        elif schedule_type == ScheduleType.WEEKLY:
            weekday = config.get('weekday', 0)  # 0=Monday
            hour = config.get('hour', 0)
            minute = config.get('minute', 0)
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            return next_run
        
        return now
    
    def start_scheduler(self):
        """启动调度器"""
        if self.scheduler_active:
            return
        
        self.scheduler_active = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("调度器已启动")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler_active = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("调度器已停止")
    
    def _scheduler_loop(self):
        """调度器循环"""
        while self.scheduler_active:
            try:
                now = datetime.utcnow()
                
                for task in self.tasks.values():
                    if not task.enabled or task.status == TaskStatus.RUNNING:
                        continue
                    
                    if task.next_run_time and task.next_run_time <= now:
                        self._execute_task(task)
                
                time.sleep(1)  # 每秒检查一次
            
            except Exception as e:
                logger.error(f"调度器循环错误: {e}")
                time.sleep(5)
    
    def _execute_task(self, task: ScheduledTask):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.last_run_time = datetime.utcnow()
        
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = time.time()
        
        try:
            # 执行任务
            result = task.task_func()
            
            execution_time = time.time() - start_time
            
            # 计算下次执行时间
            task.next_run_time = self._calculate_next_run_time(task.schedule_type, task.schedule_config)
            task.status = TaskStatus.COMPLETED
            
            execution_result = TaskExecutionResult(
                task_id=task.task_id,
                execution_id=execution_id,
                status=TaskStatus.COMPLETED,
                execution_time=execution_time,
                result=result
            )
            
            self.execution_history.append(execution_result)
        
        except Exception as e:
            logger.error(f"任务执行失败: {task.task_name}, 错误: {e}")
            execution_time = time.time() - start_time
            
            task.status = TaskStatus.FAILED
            
            execution_result = TaskExecutionResult(
                task_id=task.task_id,
                execution_id=execution_id,
                status=TaskStatus.FAILED,
                execution_time=execution_time,
                error=str(e)
            )
            
            self.execution_history.append(execution_result)
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        获取调度器统计
        
        Returns:
            调度器统计
        """
        total_tasks = len(self.tasks)
        enabled_tasks = sum(1 for t in self.tasks.values() if t.enabled)
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e.status == TaskStatus.COMPLETED)
        
        return {
            'total_tasks': total_tasks,
            'enabled_tasks': enabled_tasks,
            'scheduler_active': self.scheduler_active,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    scheduler = DataTransformationScheduler()
    
    # 定义任务函数
    def sample_task():
        return "任务执行完成"
    
    # 调度任务
    task = scheduler.schedule_task({
        'task_name': '示例任务',
        'task_func': sample_task,
        'schedule_type': 'interval',
        'schedule_config': {'interval_seconds': 60}
    })
    
    print(f"任务已调度: {task.task_id}, 下次执行时间: {task.next_run_time}")


if __name__ == '__main__':
    main()
