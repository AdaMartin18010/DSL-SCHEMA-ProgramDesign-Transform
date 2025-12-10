"""
数据转换工作流模块

专注于数据转换工作流、工作流编排、工作流执行
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 激活
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class NodeType(Enum):
    """节点类型"""
    START = "start"  # 开始节点
    END = "end"  # 结束节点
    TASK = "task"  # 任务节点
    CONDITION = "condition"  # 条件节点
    PARALLEL = "parallel"  # 并行节点
    MERGE = "merge"  # 合并节点


@dataclass
class WorkflowNode:
    """工作流节点"""
    node_id: str
    node_type: NodeType
    node_name: str
    task_func: Optional[Callable] = None
    condition_func: Optional[Callable] = None
    config: Dict[str, Any] = None


@dataclass
class WorkflowEdge:
    """工作流边"""
    from_node_id: str
    to_node_id: str
    condition: Optional[Callable] = None


@dataclass
class Workflow:
    """工作流"""
    workflow_id: str
    workflow_name: str
    nodes: Dict[str, WorkflowNode]
    edges: List[WorkflowEdge]
    status: WorkflowStatus
    created_at: datetime


@dataclass
class WorkflowExecution:
    """工作流执行"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_node_id: Optional[str] = None
    execution_data: Dict[str, Any] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DataTransformationWorkflow:
    """
    数据转换工作流
    
    专注于数据转换工作流、工作流编排、工作流执行
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
    
    def create_workflow(self, workflow_config: Dict[str, Any]) -> Workflow:
        """
        创建工作流
        
        Args:
            workflow_config: 工作流配置
            
        Returns:
            工作流对象
        """
        workflow_id = workflow_config.get('workflow_id', f"workflow_{datetime.utcnow().timestamp()}")
        
        # 创建节点
        nodes = {}
        for node_config in workflow_config.get('nodes', []):
            node = WorkflowNode(
                node_id=node_config['node_id'],
                node_type=NodeType(node_config.get('node_type', 'task')),
                node_name=node_config.get('node_name', ''),
                task_func=node_config.get('task_func'),
                condition_func=node_config.get('condition_func'),
                config=node_config.get('config', {})
            )
            nodes[node.node_id] = node
        
        # 创建边
        edges = []
        for edge_config in workflow_config.get('edges', []):
            edge = WorkflowEdge(
                from_node_id=edge_config['from_node_id'],
                to_node_id=edge_config['to_node_id'],
                condition=edge_config.get('condition')
            )
            edges.append(edge)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_name=workflow_config.get('workflow_name', ''),
            nodes=nodes,
            edges=edges,
            status=WorkflowStatus.DRAFT,
            created_at=datetime.utcnow()
        )
        
        self.workflows[workflow_id] = workflow
        return workflow
    
    def execute_workflow(self, workflow_id: str, execution_data: Optional[Dict[str, Any]] = None) -> WorkflowExecution:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            execution_data: 执行数据
            
        Returns:
            工作流执行对象
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.ACTIVE,
            execution_data=execution_data or {},
            started_at=datetime.utcnow()
        )
        
        self.executions[execution_id] = execution
        
        # 查找开始节点
        start_node = next((n for n in workflow.nodes.values() if n.node_type == NodeType.START), None)
        if not start_node:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            return execution
        
        # 执行工作流
        try:
            self._execute_node(workflow, execution, start_node.node_id)
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
        
        return execution
    
    def _execute_node(self, workflow: Workflow, execution: WorkflowExecution, node_id: str):
        """执行节点"""
        node = workflow.nodes.get(node_id)
        if not node:
            return
        
        execution.current_node_id = node_id
        
        if node.node_type == NodeType.START:
            # 开始节点，继续执行下一个节点
            next_nodes = self._get_next_nodes(workflow, node_id)
            for next_node_id in next_nodes:
                self._execute_node(workflow, execution, next_node_id)
        
        elif node.node_type == NodeType.TASK:
            # 任务节点，执行任务
            if node.task_func:
                result = node.task_func(execution.execution_data)
                execution.execution_data['last_result'] = result
            
            # 继续执行下一个节点
            next_nodes = self._get_next_nodes(workflow, node_id)
            for next_node_id in next_nodes:
                self._execute_node(workflow, execution, next_node_id)
        
        elif node.node_type == NodeType.CONDITION:
            # 条件节点，根据条件选择下一个节点
            if node.condition_func:
                condition_result = node.condition_func(execution.execution_data)
                next_nodes = self._get_next_nodes(workflow, node_id, condition_result)
                for next_node_id in next_nodes:
                    self._execute_node(workflow, execution, next_node_id)
        
        elif node.node_type == NodeType.END:
            # 结束节点
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
    
    def _get_next_nodes(self, workflow: Workflow, node_id: str, condition_result: Optional[bool] = None) -> List[str]:
        """获取下一个节点"""
        next_nodes = []
        for edge in workflow.edges:
            if edge.from_node_id == node_id:
                if edge.condition:
                    if edge.condition(condition_result):
                        next_nodes.append(edge.to_node_id)
                else:
                    next_nodes.append(edge.to_node_id)
        return next_nodes
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """
        获取工作流统计
        
        Returns:
            工作流统计
        """
        total_workflows = len(self.workflows)
        total_executions = len(self.executions)
        successful_executions = sum(1 for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED)
        
        return {
            'total_workflows': total_workflows,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    workflow_manager = DataTransformationWorkflow()
    
    # 定义任务函数
    def task1(data):
        return "任务1完成"
    
    def task2(data):
        return "任务2完成"
    
    # 创建工作流
    workflow = workflow_manager.create_workflow({
        'workflow_name': '示例工作流',
        'nodes': [
            {'node_id': 'start', 'node_type': 'start', 'node_name': '开始'},
            {'node_id': 'task1', 'node_type': 'task', 'node_name': '任务1', 'task_func': task1},
            {'node_id': 'task2', 'node_type': 'task', 'node_name': '任务2', 'task_func': task2},
            {'node_id': 'end', 'node_type': 'end', 'node_name': '结束'}
        ],
        'edges': [
            {'from_node_id': 'start', 'to_node_id': 'task1'},
            {'from_node_id': 'task1', 'to_node_id': 'task2'},
            {'from_node_id': 'task2', 'to_node_id': 'end'}
        ]
    })
    
    print(f"工作流已创建: {workflow.workflow_id}")


if __name__ == '__main__':
    main()
