"""
BPMN流程处理器

专注于BPMN流程解析、执行、监控
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .logger import logger
from .exceptions import ProcessingError, ValidationError, ParseError


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ProcessStatus(Enum):
    """流程状态"""
    RUNNING = "running"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class BPMNTask:
    """BPMN任务"""
    task_id: str
    name: str
    task_type: str  # user, service, script, manual
    assignee: Optional[str] = None
    candidate_users: List[str] = None
    candidate_groups: List[str] = None
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    form_key: Optional[str] = None
    properties: Dict[str, Any] = None


@dataclass
class BPMNProcess:
    """BPMN流程"""
    process_id: str
    name: str
    version: str
    definition: Dict[str, Any]
    tasks: List[BPMNTask] = None
    status: ProcessStatus = ProcessStatus.RUNNING


class BPMNProcessor:
    """
    BPMN流程处理器
    
    专注于BPMN流程解析、执行、监控
    """
    
    def __init__(self):
        self.processes: Dict[str, BPMNProcess] = {}
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[str, BPMNTask] = {}
        logger.info("BPMNProcessor initialized")
    
    def parse_bpmn(self, bpmn_xml: str) -> BPMNProcess:
        """
        解析BPMN XML
        
        Args:
            bpmn_xml: BPMN XML字符串
            
        Returns:
            BPMN流程对象
        """
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(bpmn_xml)
        
        # 查找流程定义
        process_elem = root.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}process')
        
        if process_elem is None:
            raise ValueError("BPMN XML中未找到流程定义")
        
        process_id = process_elem.get('id', f"process_{datetime.utcnow().timestamp()}")
        process_name = process_elem.get('name', '')
        
        # 解析任务
        tasks = []
        for task_elem in process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}task'):
            task_id = task_elem.get('id', '')
            task_name = task_elem.get('name', '')
            task_type = task_elem.tag.split('}')[-1] if '}' in task_elem.tag else task_elem.tag
            
            task = BPMNTask(
                task_id=task_id,
                name=task_name,
                task_type=task_type,
                assignee=task_elem.get('assignee'),
                properties={}
            )
            
            tasks.append(task)
            self.tasks[task_id] = task
        
        process = BPMNProcess(
            process_id=process_id,
            name=process_name,
            version='1.0',
            definition={'xml': bpmn_xml},
            tasks=tasks
        )
        
        self.processes[process_id] = process
        return process
    
    def start_process(self, process_id: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        启动流程实例
        
        Args:
            process_id: 流程ID
            variables: 流程变量
            
        Returns:
            流程实例ID
        """
        if process_id not in self.processes:
            raise ValueError(f"流程不存在: {process_id}")
        
        instance_id = f"instance_{datetime.utcnow().timestamp()}"
        
        instance = {
            'instance_id': instance_id,
            'process_id': process_id,
            'status': ProcessStatus.RUNNING.value,
            'variables': variables or {},
            'current_tasks': [],
            'completed_tasks': [],
            'started_at': datetime.utcnow(),
            'completed_at': None
        }
        
        # 初始化任务
        process = self.processes[process_id]
        for task in process.tasks:
            if task.status == TaskStatus.PENDING:
                instance['current_tasks'].append(task.task_id)
        
        self.instances[instance_id] = instance
        return instance_id
    
    def complete_task(self, task_id: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            variables: 任务变量
            
        Returns:
            是否成功
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        
        # 更新流程实例
        for instance_id, instance in self.instances.items():
            if task_id in instance['current_tasks']:
                instance['current_tasks'].remove(task_id)
                instance['completed_tasks'].append(task_id)
                
                # 更新变量
                if variables:
                    instance['variables'].update(variables)
                
                # 检查流程是否完成
                if not instance['current_tasks']:
                    instance['status'] = ProcessStatus.COMPLETED.value
                    instance['completed_at'] = datetime.utcnow()
        
        return True
    
    def get_process_status(self, instance_id: str) -> Dict[str, Any]:
        """
        获取流程状态
        
        Args:
            instance_id: 流程实例ID
            
        Returns:
            流程状态
        """
        if instance_id not in self.instances:
            return {'error': '流程实例不存在'}
        
        instance = self.instances[instance_id]
        
        return {
            'instance_id': instance_id,
            'process_id': instance['process_id'],
            'status': instance['status'],
            'current_tasks': instance['current_tasks'],
            'completed_tasks': instance['completed_tasks'],
            'variables': instance['variables'],
            'started_at': instance['started_at'].isoformat(),
            'completed_at': instance['completed_at'].isoformat() if instance['completed_at'] else None
        }


def main():
    """主函数 - 示例用法"""
    processor = BPMNProcessor()
    
    # 解析BPMN
    bpmn_xml = """
    <bpmn:process id="process_1" name="审批流程">
        <bpmn:userTask id="task_1" name="提交申请" />
        <bpmn:userTask id="task_2" name="审批" />
    </bpmn:process>
    """
    
    process = processor.parse_bpmn(bpmn_xml)
    print(f"解析流程: {process.process_id}")
    
    # 启动流程
    instance_id = processor.start_process(process.process_id, {'applicant': 'John'})
    print(f"启动流程实例: {instance_id}")
    
    # 完成任务
    processor.complete_task('task_1')
    print("任务1已完成")


if __name__ == '__main__':
    main()
