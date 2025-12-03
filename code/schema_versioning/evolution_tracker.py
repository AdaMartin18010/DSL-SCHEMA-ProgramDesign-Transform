"""
演化追踪

追踪Schema的演化过程
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from .storage import SchemaVersioningStorage


class SchemaEvolutionTracker:
    """Schema演化追踪器"""
    
    def __init__(self, storage: SchemaVersioningStorage):
        """
        初始化演化追踪器
        
        Args:
            storage: Schema版本管理存储管理器
        """
        self.storage = storage
    
    def track_evolution(self, schema_id: str, from_version: str, to_version: str,
                       changes: Dict[str, Any]) -> Optional[str]:
        """
        追踪演化
        
        Args:
            schema_id: Schema ID
            from_version: 源版本
            to_version: 目标版本
            changes: 变更字典
            
        Returns:
            演化ID（如果成功）
        """
        evolution_id = f"evolution_{uuid.uuid4().hex[:16]}"
        
        # 分析变更类型
        change_type = self._analyze_change_type(changes)
        breaking_change = self._is_breaking_change(changes)
        
        # 保存演化记录（需要扩展storage方法）
        # 这里简化实现
        
        return evolution_id
    
    def get_evolution_history(self, schema_id: str) -> List[Dict[str, Any]]:
        """
        获取演化历史
        
        Args:
            schema_id: Schema ID
            
        Returns:
            演化历史列表
        """
        # 获取版本历史
        versions = self.storage.get_version_history(schema_id)
        
        # 构建演化历史
        evolution_history = []
        for i in range(len(versions) - 1):
            from_version = versions[i + 1]['version']
            to_version = versions[i]['version']
            
            evolution_history.append({
                'from_version': from_version,
                'to_version': to_version,
                'timestamp': versions[i]['created_at'],
                'changes': {}  # 需要从演化表中获取
            })
        
        return evolution_history
    
    def _analyze_change_type(self, changes: Dict[str, Any]) -> str:
        """分析变更类型"""
        if 'added' in changes and changes['added']:
            return 'added'
        elif 'removed' in changes and changes['removed']:
            return 'removed'
        elif 'modified' in changes and changes['modified']:
            return 'modified'
        else:
            return 'unknown'
    
    def _is_breaking_change(self, changes: Dict[str, Any]) -> bool:
        """判断是否为破坏性变更"""
        # 如果有删除或修改，可能是破坏性变更
        if changes.get('removed') or changes.get('modified'):
            return True
        return False
