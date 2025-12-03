"""
时间演化追踪

实现实体随时间的变化追踪
"""

from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Dict, Any, Optional
from .storage import TemporalKGStorage
from .models import TemporalEntity


class TemporalEvolutionTracker:
    """时间演化追踪器"""
    
    def __init__(self, storage: TemporalKGStorage):
        """
        初始化演化追踪器
        
        Args:
            storage: 时序知识图谱存储管理器
        """
        self.storage = storage
    
    def track_entity_evolution(self, entity_id: str,
                              start_time: datetime,
                              end_time: datetime) -> List[Dict[str, Any]]:
        """
        追踪实体演化
        
        Args:
            entity_id: 实体ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            演化历史列表
        """
        session = self.storage.Session()
        
        # 获取时间区间内的所有版本
        versions = session.query(TemporalEntity).filter(
            and_(
                TemporalEntity.entity_id == entity_id,
                TemporalEntity.valid_from <= end_time,
                or_(
                    TemporalEntity.valid_to >= start_time,
                    TemporalEntity.valid_to.is_(None)
                )
            )
        ).order_by(TemporalEntity.valid_from).all()
        
        evolution = []
        for i, version in enumerate(versions):
            evolution.append({
                'version': i + 1,
                'valid_from': version.valid_from.isoformat(),
                'valid_to': version.valid_to.isoformat() if version.valid_to else None,
                'properties': version.properties,
                'changes': self._compute_changes(
                    versions[i-1].properties if i > 0 else {},
                    version.properties
                )
            })
        
        session.close()
        return evolution
    
    def _compute_changes(self, old_props: Dict[str, Any],
                        new_props: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算属性变化
        
        Args:
            old_props: 旧属性
            new_props: 新属性
            
        Returns:
            变化字典
        """
        changes = {
            'added': {},
            'removed': {},
            'modified': {}
        }
        
        # 新增和修改的属性
        for key, value in new_props.items():
            if key not in old_props:
                changes['added'][key] = value
            elif old_props[key] != value:
                changes['modified'][key] = {
                    'old': old_props[key],
                    'new': value
                }
        
        # 删除的属性
        for key in old_props:
            if key not in new_props:
                changes['removed'][key] = old_props[key]
        
        return changes
