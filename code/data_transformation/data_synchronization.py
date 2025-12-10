"""
数据同步模块

专注于数据同步、一致性保证、冲突解决
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SyncStrategy(Enum):
    """同步策略"""
    PUSH = "push"  # 推送
    PULL = "pull"  # 拉取
    BIDIRECTIONAL = "bidirectional"  # 双向
    MASTER_SLAVE = "master_slave"  # 主从


class ConflictResolution(Enum):
    """冲突解决策略"""
    LAST_WRITE_WINS = "last_write_wins"  # 最后写入获胜
    FIRST_WRITE_WINS = "first_write_wins"  # 首次写入获胜
    MERGE = "merge"  # 合并
    MANUAL = "manual"  # 手动
    REJECT = "reject"  # 拒绝


@dataclass
class SyncTask:
    """同步任务"""
    task_id: str
    source: str
    target: str
    strategy: SyncStrategy
    conflict_resolution: ConflictResolution
    sync_fields: List[str] = None
    enabled: bool = True


@dataclass
class SyncResult:
    """同步结果"""
    task_id: str
    source: str
    target: str
    records_synced: int
    conflicts: List[Dict[str, Any]] = None
    success: bool = True
    sync_time: float = 0.0


class DataSynchronization:
    """
    数据同步器
    
    专注于数据同步、一致性保证、冲突解决
    """
    
    def __init__(self):
        self.sync_tasks: Dict[str, SyncTask] = {}
        self.sync_history: List[SyncResult] = []
        self.data_stores: Dict[str, Dict[str, Any]] = {}  # 数据存储
    
    def register_data_store(self, store_id: str, data: Dict[str, Any]):
        """
        注册数据存储
        
        Args:
            store_id: 存储ID
            data: 数据
        """
        self.data_stores[store_id] = data
    
    def create_sync_task(self, task_config: Dict[str, Any]) -> SyncTask:
        """
        创建同步任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            同步任务对象
        """
        task_id = task_config.get('task_id', f"task_{datetime.utcnow().timestamp()}")
        
        task = SyncTask(
            task_id=task_id,
            source=task_config['source'],
            target=task_config['target'],
            strategy=SyncStrategy(task_config.get('strategy', 'push')),
            conflict_resolution=ConflictResolution(task_config.get('conflict_resolution', 'last_write_wins')),
            sync_fields=task_config.get('sync_fields'),
            enabled=task_config.get('enabled', True)
        )
        
        self.sync_tasks[task_id] = task
        return task
    
    def execute_sync(self, task_id: str) -> SyncResult:
        """
        执行同步任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            同步结果
        """
        if task_id not in self.sync_tasks:
            return SyncResult(
                task_id=task_id,
                source='',
                target='',
                records_synced=0,
                success=False
            )
        
        task = self.sync_tasks[task_id]
        
        if not task.enabled:
            return SyncResult(
                task_id=task_id,
                source=task.source,
                target=task.target,
                records_synced=0,
                success=False
            )
        
        start_time = datetime.utcnow()
        
        try:
            source_data = self.data_stores.get(task.source, {})
            target_data = self.data_stores.get(task.target, {})
            
            # 根据策略执行同步
            if task.strategy == SyncStrategy.PUSH:
                records_synced, conflicts = self._push_sync(source_data, target_data, task)
            elif task.strategy == SyncStrategy.PULL:
                records_synced, conflicts = self._pull_sync(source_data, target_data, task)
            elif task.strategy == SyncStrategy.BIDIRECTIONAL:
                records_synced, conflicts = self._bidirectional_sync(source_data, target_data, task)
            else:
                records_synced, conflicts = self._push_sync(source_data, target_data, task)
            
            # 更新目标数据存储
            self.data_stores[task.target] = target_data
            
            end_time = datetime.utcnow()
            sync_time = (end_time - start_time).total_seconds()
            
            result = SyncResult(
                task_id=task_id,
                source=task.source,
                target=task.target,
                records_synced=records_synced,
                conflicts=conflicts,
                success=True,
                sync_time=sync_time
            )
            
            self.sync_history.append(result)
            return result
        
        except Exception as e:
            logger.error(f"同步失败: {task_id}, 错误: {e}")
            end_time = datetime.utcnow()
            sync_time = (end_time - start_time).total_seconds()
            
            return SyncResult(
                task_id=task_id,
                source=task.source,
                target=task.target,
                records_synced=0,
                success=False,
                sync_time=sync_time
            )
    
    def _push_sync(self, source_data: Dict[str, Any], target_data: Dict[str, Any],
                  task: SyncTask) -> tuple[int, List[Dict[str, Any]]]:
        """推送同步"""
        records_synced = 0
        conflicts = []
        
        sync_fields = task.sync_fields or list(source_data.keys())
        
        for field in sync_fields:
            if field in source_data:
                source_value = source_data[field]
                target_value = target_data.get(field)
                
                # 检查冲突
                if field in target_data and target_value != source_value:
                    conflict = self._resolve_conflict(field, source_value, target_value, task.conflict_resolution)
                    if conflict:
                        conflicts.append(conflict)
                        continue
                
                target_data[field] = source_value
                records_synced += 1
        
        return records_synced, conflicts
    
    def _pull_sync(self, source_data: Dict[str, Any], target_data: Dict[str, Any],
                  task: SyncTask) -> tuple[int, List[Dict[str, Any]]]:
        """拉取同步"""
        # 拉取同步是推送同步的反向
        return self._push_sync(target_data, source_data, task)
    
    def _bidirectional_sync(self, source_data: Dict[str, Any], target_data: Dict[str, Any],
                           task: SyncTask) -> tuple[int, List[Dict[str, Any]]]:
        """双向同步"""
        records_synced = 0
        conflicts = []
        
        sync_fields = task.sync_fields or (set(source_data.keys()) | set(target_data.keys()))
        
        for field in sync_fields:
            source_value = source_data.get(field)
            target_value = target_data.get(field)
            
            # 检查冲突
            if source_value is not None and target_value is not None and source_value != target_value:
                conflict = self._resolve_conflict(field, source_value, target_value, task.conflict_resolution)
                if conflict:
                    conflicts.append(conflict)
                    continue
            
            # 同步到两个方向
            if source_value is not None:
                target_data[field] = source_value
                records_synced += 1
            
            if target_value is not None:
                source_data[field] = target_value
                records_synced += 1
        
        return records_synced, conflicts
    
    def _resolve_conflict(self, field: str, source_value: Any, target_value: Any,
                         resolution: ConflictResolution) -> Optional[Dict[str, Any]]:
        """解决冲突"""
        if resolution == ConflictResolution.LAST_WRITE_WINS:
            # 最后写入获胜（假设源是最后写入的）
            return None  # 使用源值，无冲突
        
        elif resolution == ConflictResolution.FIRST_WRITE_WINS:
            # 首次写入获胜（假设目标是首次写入的）
            return {
                'field': field,
                'source_value': source_value,
                'target_value': target_value,
                'resolution': 'first_write_wins',
                'message': f'字段 {field} 冲突，保留首次写入的值'
            }
        
        elif resolution == ConflictResolution.MERGE:
            # 合并（简化实现）
            if isinstance(source_value, dict) and isinstance(target_value, dict):
                merged = {**target_value, **source_value}
                return None  # 合并成功，无冲突
            else:
                return {
                    'field': field,
                    'source_value': source_value,
                    'target_value': target_value,
                    'resolution': 'merge_failed',
                    'message': f'字段 {field} 无法合并（类型不兼容）'
                }
        
        elif resolution == ConflictResolution.MANUAL:
            # 手动解决
            return {
                'field': field,
                'source_value': source_value,
                'target_value': target_value,
                'resolution': 'manual',
                'message': f'字段 {field} 需要手动解决冲突'
            }
        
        elif resolution == ConflictResolution.REJECT:
            # 拒绝
            return {
                'field': field,
                'source_value': source_value,
                'target_value': target_value,
                'resolution': 'rejected',
                'message': f'字段 {field} 冲突被拒绝'
            }
        
        return None
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """
        获取同步统计
        
        Returns:
            同步统计
        """
        total_syncs = len(self.sync_history)
        successful_syncs = sum(1 for s in self.sync_history if s.success)
        total_conflicts = sum(len(s.conflicts or []) for s in self.sync_history)
        
        return {
            'total_tasks': len(self.sync_tasks),
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'failed_syncs': total_syncs - successful_syncs,
            'total_conflicts': total_conflicts,
            'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    sync = DataSynchronization()
    
    # 注册数据存储
    sync.register_data_store('store1', {'id': 1, 'name': 'Alice', 'age': 25})
    sync.register_data_store('store2', {'id': 1, 'name': 'Bob', 'age': 30})
    
    # 创建同步任务
    task = sync.create_sync_task({
        'source': 'store1',
        'target': 'store2',
        'strategy': 'push',
        'conflict_resolution': 'last_write_wins'
    })
    
    # 执行同步
    result = sync.execute_sync(task.task_id)
    print(f"同步结果: 成功={result.success}, 同步记录数={result.records_synced}")


if __name__ == '__main__':
    main()
