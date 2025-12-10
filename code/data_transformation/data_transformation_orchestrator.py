"""
数据转换编排器模块

专注于数据转换编排、工作流管理、任务调度
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"  # 待处理
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    PAUSED = "paused"  # 已暂停
    CANCELLED = "cancelled"  # 已取消


class TaskType(Enum):
    """任务类型"""
    EXTRACT = "extract"  # 提取
    TRANSFORM = "transform"  # 转换
    LOAD = "load"  # 加载
    VALIDATE = "validate"  # 验证
    CLEAN = "clean"  # 清理
    ENRICH = "enrich"  # 丰富化
    AGGREGATE = "aggregate"  # 聚合


@dataclass
class WorkflowTask:
    """工作流任务"""
    task_id: str
    task_name: str
    task_type: TaskType
    executor: Callable
    dependencies: List[str] = None  # 依赖的任务ID
    config: Dict[str, Any] = None
    enabled: bool = True


@dataclass
class Workflow:
    """工作流"""
    workflow_id: str
    workflow_name: str
    tasks: List[WorkflowTask]
    status: WorkflowStatus
    created_at: datetime


@dataclass
class WorkflowExecutionResult:
    """工作流执行结果"""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    tasks_executed: int
    execution_time: float
    results: Dict[str, Any] = None
    errors: List[Dict[str, Any]] = None


class DataTransformationOrchestrator:
    """
    数据转换编排器
    
    专注于数据转换编排、工作流管理、任务调度
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[WorkflowExecutionResult] = []
    
    def create_workflow(self, workflow_config: Dict[str, Any]) -> Workflow:
        """
        创建工作流
        
        Args:
            workflow_config: 工作流配置
            
        Returns:
            工作流对象
        """
        workflow_id = workflow_config.get('workflow_id', f"workflow_{datetime.utcnow().timestamp()}")
        
        tasks = []
        for task_config in workflow_config.get('tasks', []):
            task = WorkflowTask(
                task_id=task_config.get('task_id', f"task_{datetime.utcnow().timestamp()}"),
                task_name=task_config.get('task_name', ''),
                task_type=TaskType(task_config.get('task_type', 'transform')),
                executor=task_config['executor'],
                dependencies=task_config.get('dependencies', []),
                config=task_config.get('config', {}),
                enabled=task_config.get('enabled', True)
            )
            tasks.append(task)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_name=workflow_config.get('workflow_name', ''),
            tasks=tasks,
            status=WorkflowStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.workflows[workflow_id] = workflow
        return workflow
    
    def execute_workflow(self, workflow_id: str, initial_data: Optional[Any] = None) -> WorkflowExecutionResult:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            initial_data: 初始数据（可选）
            
        Returns:
            工作流执行结果
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        current_data = initial_data
        tasks_executed = 0
        results = {}
        errors = []
        executed_tasks = set()
        
        try:
            # 按依赖顺序执行任务
            while len(executed_tasks) < len(workflow.tasks):
                progress_made = False
                
                for task in workflow.tasks:
                    if task.task_id in executed_tasks or not task.enabled:
                        continue
                    
                    # 检查依赖是否都已完成
                    if task.dependencies:
                        if not all(dep_id in executed_tasks for dep_id in task.dependencies):
                            continue
                    
                    try:
                        # 执行任务
                        if task.config:
                            task_result = task.executor(current_data, **task.config)
                        else:
                            task_result = task.executor(current_data)
                        
                        current_data = task_result
                        results[task.task_id] = task_result
                        executed_tasks.add(task.task_id)
                        tasks_executed += 1
                        progress_made = True
                    
                    except Exception as e:
                        logger.error(f"任务执行失败: {task.task_name}, 错误: {e}")
                        errors.append({
                            'task_id': task.task_id,
                            'task_name': task.task_name,
                            'error': str(e)
                        })
                        # 根据配置决定是否继续
                        if task.config.get('stop_on_error', True):
                            workflow.status = WorkflowStatus.FAILED
                            break
                
                if not progress_made:
                    # 可能存在循环依赖或无法满足的依赖
                    workflow.status = WorkflowStatus.FAILED
                    errors.append({'error': '无法满足任务依赖关系'})
                    break
            
            if workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            result = WorkflowExecutionResult(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=workflow.status,
                tasks_executed=tasks_executed,
                execution_time=execution_time,
                results=results,
                errors=errors if errors else None
            )
            
            self.execution_history.append(result)
            return result
        
        except Exception as e:
            logger.error(f"工作流执行失败: {workflow_id}, 错误: {e}")
            workflow.status = WorkflowStatus.FAILED
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            result = WorkflowExecutionResult(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.FAILED,
                tasks_executed=tasks_executed,
                execution_time=execution_time,
                results=results,
                errors=[{'error': str(e)}]
            )
            
            self.execution_history.append(result)
            return result
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """
        获取工作流统计
        
        Returns:
            工作流统计
        """
        total_workflows = len(self.workflows)
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e.status == WorkflowStatus.COMPLETED)
        
        if total_executions > 0:
            avg_time = sum(e.execution_time for e in self.execution_history) / total_executions
        else:
            avg_time = 0.0
        
        return {
            'total_workflows': total_workflows,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0.0,
            'average_execution_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    orchestrator = DataTransformationOrchestrator()
    
    # 定义任务函数
    def extract_task(data):
        return [{'id': 1, 'name': 'Alice'}]
    
    def transform_task(data):
        return [{'id': r['id'], 'name': r['name'].upper()} for r in data]
    
    # 创建工作流
    workflow = orchestrator.create_workflow({
        'workflow_name': 'ETL工作流',
        'tasks': [
            {'task_name': '提取', 'task_type': 'extract', 'executor': extract_task},
            {'task_name': '转换', 'task_type': 'transform', 'executor': transform_task, 'dependencies': []}
        ]
    })
    
    # 执行工作流
    result = orchestrator.execute_workflow(workflow.workflow_id)
    print(f"工作流执行结果: 状态={result.status.value}, 任务数={result.tasks_executed}")


if __name__ == '__main__':
    main()
