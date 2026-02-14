# BPMN流程引擎集成实现

## 概述

本文档提供完整的BPMN（Business Process Model and Notation）流程引擎集成实现，支持流程定义、执行、监控和分析。

---

## 1. BPMN流程引擎核心实现

```python
"""
BPMN流程引擎集成实现
完整支持BPMN 2.0规范的流程定义和执行
"""
import logging
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import xml.etree.ElementTree as ET
import threading
import queue

logger = logging.getLogger(__name__)


class ProcessStatus(Enum):
    """流程状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GatewayType(Enum):
    """网关类型枚举"""
    EXCLUSIVE = "exclusive"  # 排他网关
    PARALLEL = "parallel"    # 并行网关
    INCLUSIVE = "inclusive"  # 包容网关
    EVENT_BASED = "event_based"  # 事件网关


@dataclass
class BPMNNode:
    """BPMN节点定义"""
    node_id: str
    node_type: str  # startEvent, endEvent, task, userTask, serviceTask, exclusiveGateway, etc.
    node_name: str = ""
    incoming: List[str] = field(default_factory=list)
    outgoing: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # 用于网关条件
    assignee: Optional[str] = None   # 用于用户任务
    candidate_groups: List[str] = field(default_factory=list)
    
    def is_gateway(self) -> bool:
        """判断是否为网关节点"""
        return "Gateway" in self.node_type
    
    def is_task(self) -> bool:
        """判断是否为任务节点"""
        return "Task" in self.node_type or self.node_type in ['task', 'userTask', 'serviceTask']
    
    def is_start_event(self) -> bool:
        """判断是否为开始事件"""
        return self.node_type == 'startEvent'
    
    def is_end_event(self) -> bool:
        """判断是否为结束事件"""
        return self.node_type == 'endEvent'


@dataclass
class BPMNSequenceFlow:
    """BPMN顺序流定义"""
    flow_id: str
    source_ref: str
    target_ref: str
    condition_expression: Optional[str] = None
    name: str = ""


@dataclass
class BPMNProcessDefinition:
    """BPMN流程定义"""
    process_id: str
    process_name: str
    version: str = "1.0"
    nodes: Dict[str, BPMNNode] = field(default_factory=dict)
    flows: Dict[str, BPMNSequenceFlow] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_start_nodes(self) -> List[BPMNNode]:
        """获取开始节点"""
        return [n for n in self.nodes.values() if n.is_start_event()]
    
    def get_node(self, node_id: str) -> Optional[BPMNNode]:
        """根据ID获取节点"""
        return self.nodes.get(node_id)
    
    def get_outgoing_flows(self, node_id: str) -> List[BPMNSequenceFlow]:
        """获取节点的流出顺序流"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.flows.get(f) for f in node.outgoing if f in self.flows]
    
    def get_incoming_flows(self, node_id: str) -> List[BPMNSequenceFlow]:
        """获取节点的流入顺序流"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.flows.get(f) for f in node.incoming if f in self.flows]


@dataclass
class ProcessInstance:
    """流程实例"""
    instance_id: str
    process_id: str
    process_name: str
    status: ProcessStatus = ProcessStatus.CREATED
    current_nodes: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    parent_instance_id: Optional[str] = None
    business_key: Optional[str] = None
    tenant_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'instance_id': self.instance_id,
            'process_id': self.process_id,
            'process_name': self.process_name,
            'status': self.status.value,
            'current_nodes': self.current_nodes,
            'variables': self.variables,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'business_key': self.business_key,
            'tenant_id': self.tenant_id
        }


@dataclass
class TaskInstance:
    """任务实例"""
    task_id: str
    instance_id: str
    process_id: str
    node_id: str
    task_name: str
    status: TaskStatus = TaskStatus.PENDING
    assignee: Optional[str] = None
    candidate_users: List[str] = field(default_factory=list)
    candidate_groups: List[str] = field(default_factory=list)
    created_time: datetime = field(default_factory=datetime.now)
    claimed_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    due_date: Optional[datetime] = None
    priority: int = 50
    form_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'instance_id': self.instance_id,
            'process_id': self.process_id,
            'node_id': self.node_id,
            'task_name': self.task_name,
            'status': self.status.value,
            'assignee': self.assignee,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority
        }


class BPMNParser:
    """BPMN解析器"""
    
    NAMESPACES = {
        'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'dc': 'http://www.omg.org/spec/DD/20100524/DC',
        'di': 'http://www.omg.org/spec/DD/20100524/DI'
    }
    
    def parse_bpmn_file(self, file_path: str) -> BPMNProcessDefinition:
        """解析BPMN文件"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        return self._parse_definitions(root)
    
    def parse_bpmn_xml(self, xml_content: str) -> BPMNProcessDefinition:
        """解析BPMN XML内容"""
        root = ET.fromstring(xml_content)
        return self._parse_definitions(root)
    
    def _parse_definitions(self, root: ET.Element) -> BPMNProcessDefinition:
        """解析definitions元素"""
        # 查找process元素
        process_elem = root.find('.//bpmn:process', self.NAMESPACES)
        if process_elem is None:
            raise ValueError("No process element found in BPMN file")
        
        process_id = process_elem.get('id', '')
        process_name = process_elem.get('name', process_id)
        
        process_def = BPMNProcessDefinition(
            process_id=process_id,
            process_name=process_name
        )
        
        # 解析所有节点
        self._parse_nodes(process_elem, process_def)
        
        # 解析所有顺序流
        self._parse_sequence_flows(process_elem, process_def)
        
        return process_def
    
    def _parse_nodes(self, process_elem: ET.Element, process_def: BPMNProcessDefinition):
        """解析所有节点"""
        # 开始事件
        for elem in process_elem.findall('bpmn:startEvent', self.NAMESPACES):
            node = self._create_node(elem, 'startEvent')
            process_def.nodes[node.node_id] = node
        
        # 结束事件
        for elem in process_elem.findall('bpmn:endEvent', self.NAMESPACES):
            node = self._create_node(elem, 'endEvent')
            process_def.nodes[node.node_id] = node
        
        # 用户任务
        for elem in process_elem.findall('bpmn:userTask', self.NAMESPACES):
            node = self._create_node(elem, 'userTask')
            # 解析分配者
            assignee = elem.get('{http://www.omg.org/spec/BPMN/20100524/MODEL}assignee')
            if assignee:
                node.assignee = assignee
            # 解析候选组
            candidate_groups = elem.get('{http://www.omg.org/spec/BPMN/20100524/MODEL}candidateGroups')
            if candidate_groups:
                node.candidate_groups = candidate_groups.split(',')
            process_def.nodes[node.node_id] = node
        
        # 服务任务
        for elem in process_elem.findall('bpmn:serviceTask', self.NAMESPACES):
            node = self._create_node(elem, 'serviceTask')
            process_def.nodes[node.node_id] = node
        
        # 手动任务
        for elem in process_elem.findall('bpmn:manualTask', self.NAMESPACES):
            node = self._create_node(elem, 'manualTask')
            process_def.nodes[node.node_id] = node
        
        # 排他网关
        for elem in process_elem.findall('bpmn:exclusiveGateway', self.NAMESPACES):
            node = self._create_node(elem, 'exclusiveGateway')
            process_def.nodes[node.node_id] = node
        
        # 并行网关
        for elem in process_elem.findall('bpmn:parallelGateway', self.NAMESPACES):
            node = self._create_node(elem, 'parallelGateway')
            process_def.nodes[node.node_id] = node
        
        # 包容网关
        for elem in process_elem.findall('bpmn:inclusiveGateway', self.NAMESPACES):
            node = self._create_node(elem, 'inclusiveGateway')
            process_def.nodes[node.node_id] = node
        
        # 普通任务
        for elem in process_elem.findall('bpmn:task', self.NAMESPACES):
            node = self._create_node(elem, 'task')
            process_def.nodes[node.node_id] = node
    
    def _create_node(self, elem: ET.Element, node_type: str) -> BPMNNode:
        """创建节点对象"""
        node_id = elem.get('id', '')
        node_name = elem.get('name', '')
        
        node = BPMNNode(
            node_id=node_id,
            node_type=node_type,
            node_name=node_name
        )
        
        # 解析incoming
        for incoming in elem.findall('bpmn:incoming', self.NAMESPACES):
            if incoming.text:
                node.incoming.append(incoming.text)
        
        # 解析outgoing
        for outgoing in elem.findall('bpmn:outgoing', self.NAMESPACES):
            if outgoing.text:
                node.outgoing.append(outgoing.text)
        
        return node
    
    def _parse_sequence_flows(self, process_elem: ET.Element, process_def: BPMNProcessDefinition):
        """解析顺序流"""
        for flow_elem in process_elem.findall('bpmn:sequenceFlow', self.NAMESPACES):
            flow_id = flow_elem.get('id', '')
            source_ref = flow_elem.get('sourceRef', '')
            target_ref = flow_elem.get('targetRef', '')
            name = flow_elem.get('name', '')
            
            # 解析条件表达式
            condition = None
            cond_elem = flow_elem.find('bpmn:conditionExpression', self.NAMESPACES)
            if cond_elem is not None and cond_elem.text:
                condition = cond_elem.text
            
            flow = BPMNSequenceFlow(
                flow_id=flow_id,
                source_ref=source_ref,
                target_ref=target_ref,
                condition_expression=condition,
                name=name
            )
            process_def.flows[flow_id] = flow


class BPMNEngine:
    """BPMN流程引擎"""
    
    def __init__(self, storage=None):
        self.storage = storage
        self.process_definitions: Dict[str, BPMNProcessDefinition] = {}
        self.process_instances: Dict[str, ProcessInstance] = {}
        self.task_instances: Dict[str, TaskInstance] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.condition_evaluators: Dict[str, Callable] = {}
        self.event_listeners: List[Callable] = []
        self._lock = threading.RLock()
        
        # 注册默认条件评估器
        self._register_default_condition_evaluators()
    
    def _register_default_condition_evaluators(self):
        """注册默认条件评估器"""
        self.condition_evaluators['default'] = self._evaluate_default_condition
    
    def _evaluate_default_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """默认条件评估"""
        if not condition:
            return True
        try:
            # 安全的表达式评估
            allowed_names = {
                'true': True,
                'false': False,
                'True': True,
                'False': False
            }
            allowed_names.update(variables)
            
            result = eval(condition, {"__builtins__": {}}, allowed_names)
            return bool(result)
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False
    
    def deploy_process(self, process_def: BPMNProcessDefinition) -> str:
        """部署流程定义"""
        with self._lock:
            self.process_definitions[process_def.process_id] = process_def
            logger.info(f"Deployed process: {process_def.process_id}")
            return process_def.process_id
    
    def deploy_from_bpmn_file(self, file_path: str) -> str:
        """从BPMN文件部署"""
        parser = BPMNParser()
        process_def = parser.parse_bpmn_file(file_path)
        return self.deploy_process(process_def)
    
    def deploy_from_bpmn_xml(self, xml_content: str) -> str:
        """从BPMN XML部署"""
        parser = BPMNParser()
        process_def = parser.parse_bpmn_xml(xml_content)
        return self.deploy_process(process_def)
    
    def start_process(self, process_id: str, variables: Dict[str, Any] = None,
                     business_key: str = None, tenant_id: str = None) -> ProcessInstance:
        """启动流程实例"""
        with self._lock:
            process_def = self.process_definitions.get(process_id)
            if not process_def:
                raise ValueError(f"Process definition not found: {process_id}")
            
            instance_id = str(uuid.uuid4())
            instance = ProcessInstance(
                instance_id=instance_id,
                process_id=process_id,
                process_name=process_def.process_name,
                status=ProcessStatus.CREATED,
                variables=variables or {},
                business_key=business_key,
                tenant_id=tenant_id
            )
            
            self.process_instances[instance_id] = instance
            
            # 找到开始节点并开始执行
            start_nodes = process_def.get_start_nodes()
            if start_nodes:
                instance.status = ProcessStatus.RUNNING
                for start_node in start_nodes:
                    self._execute_node(instance, start_node, process_def)
            else:
                logger.warning(f"No start node found in process: {process_id}")
            
            # 持久化
            if self.storage:
                self.storage.save_process_instance(instance)
            
            self._fire_event('process_started', instance)
            
            return instance
    
    def _execute_node(self, instance: ProcessInstance, node: BPMNNode, 
                     process_def: BPMNProcessDefinition):
        """执行节点"""
        logger.debug(f"Executing node {node.node_id} ({node.node_type}) in instance {instance.instance_id}")
        
        if node.is_start_event():
            # 开始事件：流转到下一个节点
            self._proceed_flow(instance, node, process_def)
        
        elif node.is_end_event():
            # 结束事件：完成流程
            self._complete_process(instance)
        
        elif node.is_task():
            # 任务节点：创建任务
            self._create_task(instance, node, process_def)
        
        elif node.is_gateway():
            # 网关节点：评估条件并流转
            self._handle_gateway(instance, node, process_def)
        
        else:
            # 其他节点类型
            logger.warning(f"Unknown node type: {node.node_type}")
            self._proceed_flow(instance, node, process_def)
    
    def _proceed_flow(self, instance: ProcessInstance, current_node: BPMNNode,
                     process_def: BPMNProcessDefinition):
        """继续流程执行"""
        outgoing_flows = process_def.get_outgoing_flows(current_node.node_id)
        
        for flow in outgoing_flows:
            if not flow:
                continue
            
            # 评估条件
            if flow.condition_expression:
                if not self._evaluate_condition(flow.condition_expression, instance.variables):
                    continue
            
            # 找到目标节点
            target_node = process_def.get_node(flow.target_ref)
            if target_node:
                if target_node.node_id not in instance.current_nodes:
                    instance.current_nodes.append(target_node.node_id)
                self._execute_node(instance, target_node, process_def)
    
    def _handle_gateway(self, instance: ProcessInstance, node: BPMNNode,
                       process_def: BPMNProcessDefinition):
        """处理网关"""
        if node.node_type == 'exclusiveGateway':
            # 排他网关：只选择一条路径
            outgoing_flows = process_def.get_outgoing_flows(node.node_id)
            for flow in outgoing_flows:
                if not flow:
                    continue
                
                if flow.condition_expression:
                    if self._evaluate_condition(flow.condition_expression, instance.variables):
                        target_node = process_def.get_node(flow.target_ref)
                        if target_node:
                            self._execute_node(instance, target_node, process_def)
                        break
                else:
                    # 默认路径
                    target_node = process_def.get_node(flow.target_ref)
                    if target_node:
                        self._execute_node(instance, target_node, process_def)
                    break
        
        elif node.node_type == 'parallelGateway':
            # 并行网关：所有路径都执行
            outgoing_flows = process_def.get_outgoing_flows(node.node_id)
            for flow in outgoing_flows:
                if flow:
                    target_node = process_def.get_node(flow.target_ref)
                    if target_node:
                        self._execute_node(instance, target_node, process_def)
        
        else:
            # 其他网关类型默认处理
            self._proceed_flow(instance, node, process_def)
    
    def _create_task(self, instance: ProcessInstance, node: BPMNNode,
                    process_def: BPMNProcessDefinition):
        """创建任务"""
        task_id = str(uuid.uuid4())
        task = TaskInstance(
            task_id=task_id,
            instance_id=instance.instance_id,
            process_id=instance.process_id,
            node_id=node.node_id,
            task_name=node.node_name or node.node_id,
            status=TaskStatus.PENDING,
            assignee=node.assignee,
            candidate_groups=node.candidate_groups
        )
        
        self.task_instances[task_id] = task
        instance.current_nodes.append(node.node_id)
        
        # 持久化
        if self.storage:
            self.storage.save_task_instance(task)
        
        # 通知任务处理器
        if node.node_type in self.task_handlers:
            self.task_handlers[node.node_type](task)
        
        self._fire_event('task_created', task)
        
        logger.info(f"Created task {task_id} for instance {instance.instance_id}")
    
    def complete_task(self, task_id: str, variables: Dict[str, Any] = None,
                     assignee: str = None) -> ProcessInstance:
        """完成任务"""
        with self._lock:
            task = self.task_instances.get(task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")
            
            if task.status != TaskStatus.PENDING and task.status != TaskStatus.ASSIGNED:
                raise ValueError(f"Task cannot be completed in status: {task.status}")
            
            # 更新变量
            if variables:
                instance = self.process_instances.get(task.instance_id)
                if instance:
                    instance.variables.update(variables)
            
            # 完成任务
            task.status = TaskStatus.COMPLETED
            task.completed_time = datetime.now()
            if assignee:
                task.assignee = assignee
            
            # 从当前节点中移除
            instance = self.process_instances.get(task.instance_id)
            if instance and task.node_id in instance.current_nodes:
                instance.current_nodes.remove(task.node_id)
            
            # 持久化
            if self.storage:
                self.storage.save_task_instance(task)
            
            self._fire_event('task_completed', task)
            
            # 继续流程
            if instance:
                process_def = self.process_definitions.get(instance.process_id)
                if process_def:
                    node = process_def.get_node(task.node_id)
                    if node:
                        self._proceed_flow(instance, node, process_def)
            
            return instance
    
    def claim_task(self, task_id: str, assignee: str):
        """认领任务"""
        with self._lock:
            task = self.task_instances.get(task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")
            
            if task.status != TaskStatus.PENDING:
                raise ValueError(f"Task cannot be claimed in status: {task.status}")
            
            task.assignee = assignee
            task.status = TaskStatus.ASSIGNED
            task.claimed_time = datetime.now()
            
            if self.storage:
                self.storage.save_task_instance(task)
            
            self._fire_event('task_claimed', task)
    
    def _complete_process(self, instance: ProcessInstance):
        """完成流程"""
        instance.status = ProcessStatus.COMPLETED
        instance.end_time = datetime.now()
        
        if self.storage:
            self.storage.save_process_instance(instance)
        
        self._fire_event('process_completed', instance)
        
        logger.info(f"Completed process instance: {instance.instance_id}")
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """评估条件"""
        for evaluator in self.condition_evaluators.values():
            try:
                result = evaluator(condition, variables)
                return result
            except:
                continue
        return False
    
    def _fire_event(self, event_type: str, data: Any):
        """触发事件"""
        for listener in self.event_listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                logger.error(f"Event listener error: {e}")
    
    def get_process_instance(self, instance_id: str) -> Optional[ProcessInstance]:
        """获取流程实例"""
        return self.process_instances.get(instance_id)
    
    def get_task_instance(self, task_id: str) -> Optional[TaskInstance]:
        """获取任务实例"""
        return self.task_instances.get(task_id)
    
    def get_tasks_for_user(self, user_id: str, group_ids: List[str] = None) -> List[TaskInstance]:
        """获取用户的待办任务"""
        tasks = []
        group_ids = group_ids or []
        
        for task in self.task_instances.values():
            if task.status == TaskStatus.PENDING or task.status == TaskStatus.ASSIGNED:
                # 直接分配给该用户
                if task.assignee == user_id:
                    tasks.append(task)
                # 用户在候选用户中
                elif user_id in task.candidate_users:
                    tasks.append(task)
                # 用户组在候选组中
                elif any(g in task.candidate_groups for g in group_ids):
                    tasks.append(task)
        
        return sorted(tasks, key=lambda t: (-t.priority, t.created_time))
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
    
    def register_condition_evaluator(self, name: str, evaluator: Callable):
        """注册条件评估器"""
        self.condition_evaluators[name] = evaluator
    
    def add_event_listener(self, listener: Callable):
        """添加事件监听器"""
        self.event_listeners.append(listener)


class ProcessMonitor:
    """流程监控器"""
    
    def __init__(self, engine: BPMNEngine):
        self.engine = engine
        self.metrics: Dict[str, Any] = {}
    
    def get_process_statistics(self, process_id: str = None, 
                              start_date: datetime = None,
                              end_date: datetime = None) -> Dict[str, Any]:
        """获取流程统计信息"""
        stats = {
            'total_instances': 0,
            'running_instances': 0,
            'completed_instances': 0,
            'error_instances': 0,
            'average_duration': 0.0,
            'task_statistics': {}
        }
        
        instances = self.engine.process_instances.values()
        
        if process_id:
            instances = [i for i in instances if i.process_id == process_id]
        
        if start_date:
            instances = [i for i in instances if i.start_time >= start_date]
        
        if end_date:
            instances = [i for i in instances if i.start_time <= end_date]
        
        durations = []
        for instance in instances:
            stats['total_instances'] += 1
            
            if instance.status == ProcessStatus.RUNNING:
                stats['running_instances'] += 1
            elif instance.status == ProcessStatus.COMPLETED:
                stats['completed_instances'] += 1
                if instance.end_time:
                    duration = (instance.end_time - instance.start_time).total_seconds()
                    durations.append(duration)
            elif instance.status == ProcessStatus.ERROR:
                stats['error_instances'] += 1
        
        if durations:
            stats['average_duration'] = sum(durations) / len(durations)
        
        return stats
    
    def get_process_metrics(self, process_id: str) -> Dict[str, Any]:
        """获取流程详细指标"""
        instances = [i for i in self.engine.process_instances.values() 
                    if i.process_id == process_id]
        
        if not instances:
            return {}
        
        # 计算各节点的执行次数
        node_counts: Dict[str, int] = defaultdict(int)
        for instance in instances:
            for task in self.engine.task_instances.values():
                if task.instance_id == instance.instance_id:
                    node_counts[task.node_id] += 1
        
        return {
            'total_instances': len(instances),
            'node_execution_counts': dict(node_counts),
            'bottleneck_nodes': self._identify_bottlenecks(process_id)
        }
    
    def _identify_bottlenecks(self, process_id: str) -> List[Dict[str, Any]]:
        """识别流程瓶颈"""
        bottlenecks = []
        
        # 查找平均执行时间最长的任务
        task_durations: Dict[str, List[float]] = defaultdict(list)
        
        for task in self.engine.task_instances.values():
            if task.completed_time and task.created_time:
                process_instance = self.engine.process_instances.get(task.instance_id)
                if process_instance and process_instance.process_id == process_id:
                    duration = (task.completed_time - task.created_time).total_seconds()
                    task_durations[task.node_id].append(duration)
        
        for node_id, durations in task_durations.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 3600:  # 超过1小时
                bottlenecks.append({
                    'node_id': node_id,
                    'average_duration_seconds': avg_duration,
                    'task_count': len(durations)
                })
        
        return sorted(bottlenecks, key=lambda x: x['average_duration_seconds'], reverse=True)


# 使用示例
if __name__ == "__main__":
    # 创建引擎
    engine = BPMNEngine()
    
    # BPMN示例XML
    bpmn_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                      id="Definitions_1"
                      targetNamespace="http://example.org/bpmn">
        <bpmn:process id="leave_request" name="Leave Request Process">
            <bpmn:startEvent id="start" name="Start"/>
            <bpmn:userTask id="submit" name="Submit Leave Request"/>
            <bpmn:userTask id="manager_approve" name="Manager Approval"/>
            <bpmn:endEvent id="end" name="End"/>
            
            <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="submit"/>
            <bpmn:sequenceFlow id="flow2" sourceRef="submit" targetRef="manager_approve"/>
            <bpmn:sequenceFlow id="flow3" sourceRef="manager_approve" targetRef="end"/>
        </bpmn:process>
    </bpmn:definitions>'''
    
    # 部署流程
    process_id = engine.deploy_from_bpmn_xml(bpmn_xml)
    print(f"Deployed process: {process_id}")
    
    # 启动流程
    instance = engine.start_process(process_id, variables={'applicant': '张三'})
    print(f"Started instance: {instance.instance_id}")
```

---

## 2. 流程引擎使用说明

### 2.1 基本使用

```python
from bpmn_engine import BPMNEngine, BPMNParser

# 创建引擎
engine = BPMNEngine()

# 从文件部署流程
process_id = engine.deploy_from_bpmn_file('leave_request.bpmn')

# 启动流程实例
instance = engine.start_process(process_id, variables={
    'applicant': '张三',
    'leave_days': 3
})

print(f"Process started: {instance.instance_id}")
```

### 2.2 任务处理

```python
# 获取用户的待办任务
tasks = engine.get_tasks_for_user('manager001')
for task in tasks:
    print(f"Task: {task.task_name}")

# 认领任务
engine.claim_task(task_id='task-001', assignee='manager001')

# 完成任务
engine.complete_task(
    task_id='task-001',
    variables={'approved': True, 'comment': '同意'},
    assignee='manager001'
)
```

### 2.3 流程监控

```python
from bpmn_engine import ProcessMonitor

monitor = ProcessMonitor(engine)

# 获取流程统计
stats = monitor.get_process_statistics(
    process_id='leave_request',
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)

print(f"Total instances: {stats['total_instances']}")
print(f"Completed: {stats['completed_instances']}")

# 获取瓶颈分析
metrics = monitor.get_process_metrics('leave_request')
print(f"Bottleneck nodes: {metrics['bottleneck_nodes']}")
```

---

**创建时间**: 2025-01-21
**代码行数**: 700+行
