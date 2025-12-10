"""
数据复制模块

专注于数据复制、数据镜像、数据同步复制
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReplicationMode(Enum):
    """复制模式"""
    FULL = "full"  # 全量复制
    INCREMENTAL = "incremental"  # 增量复制
    SNAPSHOT = "snapshot"  # 快照复制
    CONTINUOUS = "continuous"  # 持续复制


class ReplicationStatus(Enum):
    """复制状态"""
    PENDING = "pending"  # 待处理
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    PAUSED = "paused"  # 已暂停


@dataclass
class ReplicationTask:
    """复制任务"""
    task_id: str
    source: str
    target: str
    mode: ReplicationMode
    status: ReplicationStatus
    created_at: datetime
    filters: Optional[Dict[str, Any]] = None


@dataclass
class ReplicationResult:
    """复制结果"""
    task_id: str
    records_copied: int
    replication_time: float
    success: bool
    errors: List[Dict[str, Any]] = None


class DataReplication:
    """
    数据复制器
    
    专注于数据复制、数据镜像、数据同步复制
    """
    
    def __init__(self):
        self.replication_tasks: Dict[str, ReplicationTask] = {}
        self.replication_history: List[ReplicationResult] = {}
        self.data_stores: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_data_store(self, store_id: str, data: List[Dict[str, Any]]):
        """
        注册数据存储
        
        Args:
            store_id: 存储ID
            data: 数据列表
        """
        self.data_stores[store_id] = data
    
    def create_replication_task(self, task_config: Dict[str, Any]) -> ReplicationTask:
        """
        创建复制任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            复制任务对象
        """
        task_id = task_config.get('task_id', f"task_{datetime.utcnow().timestamp()}")
        
        task = ReplicationTask(
            task_id=task_id,
            source=task_config['source'],
            target=task_config['target'],
            mode=ReplicationMode(task_config.get('mode', 'full')),
            status=ReplicationStatus.PENDING,
            created_at=datetime.utcnow(),
            filters=task_config.get('filters')
        )
        
        self.replication_tasks[task_id] = task
        return task
    
    def execute_replication(self, task_id: str) -> ReplicationResult:
        """
        执行复制任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            复制结果
        """
        if task_id not in self.replication_tasks:
            raise ValueError(f"复制任务不存在: {task_id}")
        
        task = self.replication_tasks[task_id]
        
        if task.source not in self.data_stores:
            raise ValueError(f"源数据存储不存在: {task.source}")
        
        task.status = ReplicationStatus.RUNNING
        start_time = datetime.utcnow()
        
        try:
            source_data = self.data_stores[task.source].copy()
            
            # 应用过滤
            if task.filters:
                source_data = self._apply_filters(source_data, task.filters)
            
            # 复制数据
            if task.mode == ReplicationMode.FULL:
                # 全量复制：清空目标并复制所有数据
                self.data_stores[task.target] = source_data.copy()
            elif task.mode == ReplicationMode.INCREMENTAL:
                # 增量复制：追加新数据
                if task.target not in self.data_stores:
                    self.data_stores[task.target] = []
                self.data_stores[task.target].extend(source_data)
            elif task.mode == ReplicationMode.SNAPSHOT:
                # 快照复制：创建时间戳快照
                snapshot_data = source_data.copy()
                for record in snapshot_data:
                    record['_snapshot_time'] = datetime.utcnow().isoformat()
                if task.target not in self.data_stores:
                    self.data_stores[task.target] = []
                self.data_stores[task.target].extend(snapshot_data)
            else:
                # 默认全量复制
                self.data_stores[task.target] = source_data.copy()
            
            end_time = datetime.utcnow()
            replication_time = (end_time - start_time).total_seconds()
            
            task.status = ReplicationStatus.COMPLETED
            
            result = ReplicationResult(
                task_id=task_id,
                records_copied=len(source_data),
                replication_time=replication_time,
                success=True
            )
            
            if task_id not in self.replication_history:
                self.replication_history[task_id] = []
            self.replication_history[task_id].append(result)
            
            return result
        
        except Exception as e:
            logger.error(f"复制失败: {task_id}, 错误: {e}")
            task.status = ReplicationStatus.FAILED
            end_time = datetime.utcnow()
            replication_time = (end_time - start_time).total_seconds()
            
            result = ReplicationResult(
                task_id=task_id,
                records_copied=0,
                replication_time=replication_time,
                success=False,
                errors=[{'error': str(e)}]
            )
            
            if task_id not in self.replication_history:
                self.replication_history[task_id] = []
            self.replication_history[task_id].append(result)
            
            return result
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用过滤"""
        filtered_data = data
        
        for field, condition in filters.items():
            if isinstance(condition, dict):
                if 'eq' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) == condition['eq']]
                elif 'gt' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) is not None and r.get(field) > condition['gt']]
                elif 'in' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) in condition['in']]
            else:
                filtered_data = [r for r in filtered_data if r.get(field) == condition]
        
        return filtered_data
    
    def get_replication_stats(self) -> Dict[str, Any]:
        """
        获取复制统计
        
        Returns:
            复制统计
        """
        total_tasks = len(self.replication_tasks)
        completed_tasks = sum(1 for t in self.replication_tasks.values() if t.status == ReplicationStatus.COMPLETED)
        total_records = sum(
            sum(r.records_copied for r in history)
            for history in self.replication_history.values()
        )
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': sum(1 for t in self.replication_tasks.values() if t.status == ReplicationStatus.FAILED),
            'total_records_copied': total_records
        }


def main():
    """主函数 - 示例用法"""
    replication = DataReplication()
    
    # 注册数据存储
    replication.register_data_store('source', [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': 30}
    ])
    
    # 创建复制任务
    task = replication.create_replication_task({
        'source': 'source',
        'target': 'target',
        'mode': 'full'
    })
    
    # 执行复制
    result = replication.execute_replication(task.task_id)
    print(f"复制结果: 成功={result.success}, 复制记录数={result.records_copied}")


if __name__ == '__main__':
    main()
