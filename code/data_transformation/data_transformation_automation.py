"""
数据转换自动化引擎模块

专注于数据转换自动化、任务调度、工作流自动化、规则引擎
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class AutomationTriggerType(Enum):
    """自动化触发类型"""
    SCHEDULE = "schedule"  # 定时触发
    EVENT = "event"  # 事件触发
    CONDITION = "condition"  # 条件触发
    MANUAL = "manual"  # 手动触发
    API = "api"  # API触发


class AutomationStatus(Enum):
    """自动化状态"""
    IDLE = "idle"  # 空闲
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class RuleOperator(Enum):
    """规则操作符"""
    EQUALS = "equals"  # 等于
    NOT_EQUALS = "not_equals"  # 不等于
    GREATER_THAN = "greater_than"  # 大于
    LESS_THAN = "less_than"  # 小于
    CONTAINS = "contains"  # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    REGEX = "regex"  # 正则表达式


@dataclass
class AutomationRule:
    """自动化规则"""
    rule_id: str
    rule_name: str
    condition: Dict[str, Any]
    action: Callable
    enabled: bool = True
    priority: int = 0
    created_at: datetime = None


@dataclass
class AutomationTask:
    """自动化任务"""
    task_id: str
    task_name: str
    task_type: str
    trigger_type: AutomationTriggerType
    trigger_config: Dict[str, Any]
    handler: Callable
    status: AutomationStatus = AutomationStatus.IDLE
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    enabled: bool = True
    created_at: datetime = None


@dataclass
class AutomationExecution:
    """自动化执行"""
    execution_id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: AutomationStatus = AutomationStatus.RUNNING
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0


class DataTransformationAutomation:
    """数据转换自动化引擎"""
    
    def __init__(self):
        """初始化自动化引擎"""
        self.tasks: Dict[str, AutomationTask] = {}
        self.rules: Dict[str, AutomationRule] = {}
        self.executions: List[AutomationExecution] = []
        self.automation_config: Dict[str, Any] = {}
    
    def create_automation_task(
        self,
        task_name: str,
        task_type: str,
        trigger_type: AutomationTriggerType,
        trigger_config: Dict[str, Any],
        handler: Callable
    ) -> AutomationTask:
        """创建自动化任务"""
        task_id = f"task_{hashlib.md5(f'{task_name}_{task_type}'.encode()).hexdigest()[:8]}"
        
        # 计算下次运行时间
        next_run_time = self._calculate_next_run_time(trigger_type, trigger_config)
        
        task = AutomationTask(
            task_id=task_id,
            task_name=task_name,
            task_type=task_type,
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            handler=handler,
            next_run_time=next_run_time,
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        logger.info(f"创建自动化任务: {task_name} ({task_id})")
        
        return task
    
    def _calculate_next_run_time(
        self,
        trigger_type: AutomationTriggerType,
        trigger_config: Dict[str, Any]
    ) -> Optional[datetime]:
        """计算下次运行时间"""
        if trigger_type == AutomationTriggerType.SCHEDULE:
            # 定时触发：计算下次运行时间
            schedule = trigger_config.get("schedule", "")
            # 这里应该实现实际的调度逻辑（如cron表达式解析）
            return datetime.now() + timedelta(hours=1)
        elif trigger_type == AutomationTriggerType.EVENT:
            # 事件触发：不设置下次运行时间
            return None
        elif trigger_type == AutomationTriggerType.CONDITION:
            # 条件触发：不设置下次运行时间
            return None
        else:
            return None
    
    def create_automation_rule(
        self,
        rule_name: str,
        condition: Dict[str, Any],
        action: Callable,
        priority: int = 0
    ) -> AutomationRule:
        """创建自动化规则"""
        rule_id = f"rule_{hashlib.md5(rule_name.encode()).hexdigest()[:8]}"
        
        rule = AutomationRule(
            rule_id=rule_id,
            rule_name=rule_name,
            condition=condition,
            action=action,
            priority=priority,
            created_at=datetime.now()
        )
        
        self.rules[rule_id] = rule
        logger.info(f"创建自动化规则: {rule_name} ({rule_id})")
        
        return rule
    
    def execute_task(self, task_id: str, context: Dict[str, Any] = None) -> AutomationExecution:
        """执行自动化任务"""
        if task_id not in self.tasks:
            raise ValueError(f"任务不存在: {task_id}")
        
        task = self.tasks[task_id]
        
        if not task.enabled:
            raise ValueError(f"任务已禁用: {task_id}")
        
        execution_id = f"exec_{hashlib.md5(f'{task_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        start_time = datetime.now()
        
        execution = AutomationExecution(
            execution_id=execution_id,
            task_id=task_id,
            start_time=start_time,
            status=AutomationStatus.RUNNING
        )
        
        self.executions.append(execution)
        task.status = AutomationStatus.RUNNING
        task.last_run_time = start_time
        task.run_count += 1
        
        try:
            # 执行任务处理器
            result = task.handler(context or {})
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            execution.end_time = end_time
            execution.status = AutomationStatus.COMPLETED
            execution.result = result
            execution.execution_time = execution_time
            
            task.status = AutomationStatus.COMPLETED
            task.success_count += 1
            
            # 计算下次运行时间
            task.next_run_time = self._calculate_next_run_time(
                task.trigger_type, task.trigger_config
            )
            
            logger.info(f"任务执行成功: {task_name} ({task_id}) - {execution_time:.3f}s")
            
            return execution
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            execution.end_time = end_time
            execution.status = AutomationStatus.FAILED
            execution.error = str(e)
            execution.execution_time = execution_time
            
            task.status = AutomationStatus.FAILED
            task.failure_count += 1
            
            logger.error(f"任务执行失败: {task.task_name} ({task_id}) - {str(e)}")
            
            return execution
    
    def evaluate_rule(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """评估规则条件"""
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        
        if not rule.enabled:
            return False
        
        return self._evaluate_condition(rule.condition, context)
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """评估条件"""
        field = condition.get("field", "")
        operator = condition.get("operator", "")
        value = condition.get("value", "")
        
        context_value = context.get(field)
        
        if operator == RuleOperator.EQUALS.value:
            return context_value == value
        elif operator == RuleOperator.NOT_EQUALS.value:
            return context_value != value
        elif operator == RuleOperator.GREATER_THAN.value:
            return context_value > value
        elif operator == RuleOperator.LESS_THAN.value:
            return context_value < value
        elif operator == RuleOperator.CONTAINS.value:
            return value in str(context_value)
        elif operator == RuleOperator.NOT_CONTAINS.value:
            return value not in str(context_value)
        else:
            return False
    
    def trigger_rules(self, context: Dict[str, Any]):
        """触发规则"""
        # 按优先级排序规则
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if self._evaluate_condition(rule.condition, context):
                try:
                    rule.action(context)
                    logger.info(f"规则触发成功: {rule.rule_name} ({rule.rule_id})")
                except Exception as e:
                    logger.error(f"规则触发失败: {rule.rule_name} ({rule.rule_id}) - {str(e)}")
    
    def get_ready_tasks(self) -> List[AutomationTask]:
        """获取就绪的任务"""
        now = datetime.now()
        ready_tasks = []
        
        for task in self.tasks.values():
            if not task.enabled:
                continue
            
            if task.status == AutomationStatus.RUNNING:
                continue
            
            if task.trigger_type == AutomationTriggerType.SCHEDULE:
                if task.next_run_time and task.next_run_time <= now:
                    ready_tasks.append(task)
            elif task.trigger_type == AutomationTriggerType.EVENT:
                # 事件触发的任务需要外部触发
                pass
            elif task.trigger_type == AutomationTriggerType.CONDITION:
                # 条件触发的任务需要检查条件
                pass
        
        return ready_tasks
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """获取自动化统计信息"""
        total_tasks = len(self.tasks)
        enabled_tasks = len([t for t in self.tasks.values() if t.enabled])
        running_tasks = len([t for t in self.tasks.values() if t.status == AutomationStatus.RUNNING])
        
        total_executions = len(self.executions)
        successful_executions = len([
            e for e in self.executions
            if e.status == AutomationStatus.COMPLETED
        ])
        failed_executions = len([
            e for e in self.executions
            if e.status == AutomationStatus.FAILED
        ])
        
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules.values() if r.enabled])
        
        return {
            "total_tasks": total_tasks,
            "enabled_tasks": enabled_tasks,
            "running_tasks": running_tasks,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules
        }
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = AutomationStatus.PAUSED
        logger.info(f"暂停任务: {task_id}")
        
        return True
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = AutomationStatus.IDLE
        logger.info(f"恢复任务: {task_id}")
        
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id not in self.tasks:
            return False
        
        del self.tasks[task_id]
        logger.info(f"删除任务: {task_id}")
        
        return True
    
    def delete_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id not in self.rules:
            return False
        
        del self.rules[rule_id]
        logger.info(f"删除规则: {rule_id}")
        
        return True
