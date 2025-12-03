"""
时间推理算法

实现时间关系推理
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from .storage import TemporalKGStorage
from .models import TemporalEntity


class TemporalReasoning:
    """时间推理算法"""
    
    def __init__(self, storage: TemporalKGStorage):
        """
        初始化时间推理器
        
        Args:
            storage: 时序知识图谱存储管理器
        """
        self.storage = storage
    
    def infer_temporal_relations(self, entity1_id: str, entity2_id: str,
                                query_time: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        推理时间关系
        
        Args:
            entity1_id: 实体1 ID
            entity2_id: 实体2 ID
            query_time: 查询时间
            
        Returns:
            时间关系列表
        """
        # 获取实体在查询时间点的状态
        entity1 = self._get_entity_at_time(entity1_id, query_time)
        entity2 = self._get_entity_at_time(entity2_id, query_time)
        
        if not entity1 or not entity2:
            return None
        
        # 推理时间关系
        relations = []
        
        # 1. 时间顺序关系
        if entity1['valid_from'] < entity2['valid_from']:
            relations.append({
                'type': 'before',
                'entity1': entity1_id,
                'entity2': entity2_id,
                'confidence': 1.0
            })
        
        # 2. 时间重叠关系
        if self._time_overlap(entity1, entity2):
            relations.append({
                'type': 'overlaps',
                'entity1': entity1_id,
                'entity2': entity2_id,
                'confidence': 0.9
            })
        
        # 3. 时间包含关系
        if self._time_contains(entity1, entity2):
            relations.append({
                'type': 'contains',
                'entity1': entity1_id,
                'entity2': entity2_id,
                'confidence': 0.8
            })
        
        return relations
    
    def _get_entity_at_time(self, entity_id: str,
                           query_time: datetime) -> Optional[Dict[str, Any]]:
        """获取时间点的实体状态"""
        return self.storage.get_entity_at_time(entity_id, query_time)
    
    def _time_overlap(self, entity1: Dict[str, Any],
                     entity2: Dict[str, Any]) -> bool:
        """判断时间是否重叠"""
        e1_end = entity1['valid_to'] if entity1['valid_to'] else datetime.max
        e2_end = entity2['valid_to'] if entity2['valid_to'] else datetime.max
        
        return (entity1['valid_from'] < e2_end and
                entity2['valid_from'] < e1_end)
    
    def _time_contains(self, entity1: Dict[str, Any],
                      entity2: Dict[str, Any]) -> bool:
        """判断entity1是否包含entity2的时间区间"""
        e1_end = entity1['valid_to'] if entity1['valid_to'] else datetime.max
        e2_end = entity2['valid_to'] if entity2['valid_to'] else datetime.max
        
        return (entity1['valid_from'] <= entity2['valid_from'] and
                e1_end >= e2_end)
