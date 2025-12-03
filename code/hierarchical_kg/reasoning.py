"""
层次化推理

实现自底向上、自顶向下、跨层推理
"""

from typing import List, Dict, Any, Optional
from .storage import HierarchicalKGStorage


class HierarchicalReasoning:
    """层次化推理器"""
    
    def __init__(self, storage: HierarchicalKGStorage):
        """
        初始化层次化推理器
        
        Args:
            storage: 层次化知识图谱存储管理器
        """
        self.storage = storage
    
    def bottom_up_reasoning(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        自底向上推理（L₁ → L₂ → L₃）
        
        Args:
            instance_id: 实例实体ID
            
        Returns:
            推理链（从实例到概念）
        """
        # 获取抽象链
        abstraction_chain = self.storage.get_abstraction_chain(instance_id)
        
        # 构建推理路径
        reasoning_path = []
        for i, entity in enumerate(abstraction_chain):
            reasoning_path.append({
                'step': i + 1,
                'level': entity['level'],
                'entity_id': entity['entity_id'],
                'name': entity['name'],
                'reasoning_type': 'abstraction',
                'content': entity['content']
            })
        
        return reasoning_path
    
    def top_down_reasoning(self, concept_id: str) -> List[Dict[str, Any]]:
        """
        自顶向下推理（L₃ → L₂ → L₁）
        
        Args:
            concept_id: 概念实体ID
            
        Returns:
            推理链（从概念到实例）
        """
        # 获取具体化链
        concretization_chain = self.storage.get_concretization_chain(concept_id)
        
        # 构建推理路径
        reasoning_path = []
        for i, entity in enumerate(concretization_chain):
            reasoning_path.append({
                'step': i + 1,
                'level': entity['level'],
                'entity_id': entity['entity_id'],
                'name': entity['name'],
                'reasoning_type': 'concretization',
                'content': entity['content']
            })
        
        return reasoning_path
    
    def cross_layer_reasoning(self, source_entity_id: str,
                             target_level: int) -> List[Dict[str, Any]]:
        """
        跨层推理
        
        Args:
            source_entity_id: 源实体ID
            target_level: 目标层次
            
        Returns:
            推理路径
        """
        # 获取源实体
        entities = self.storage.get_entities_by_level(1)
        source_entity = next((e for e in entities if e['entity_id'] == source_entity_id), None)
        
        if not source_entity:
            return []
        
        source_level = source_entity['level']
        
        if source_level < target_level:
            # 向上推理（抽象）
            return self.bottom_up_reasoning(source_entity_id)
        elif source_level > target_level:
            # 向下推理（具体化）
            return self.top_down_reasoning(source_entity_id)
        else:
            # 同层推理
            return [{
                'step': 1,
                'level': source_level,
                'entity_id': source_entity_id,
                'reasoning_type': 'same_level',
                'content': source_entity['content']
            }]
    
    def analogical_reasoning(self, source_entity_id: str,
                           target_entity_id: str) -> Dict[str, Any]:
        """
        类比推理
        
        Args:
            source_entity_id: 源实体ID
            target_entity_id: 目标实体ID
            
        Returns:
            类比结果
        """
        # 获取两个实体的抽象链
        source_chain = self.storage.get_abstraction_chain(source_entity_id)
        target_chain = self.storage.get_abstraction_chain(target_entity_id)
        
        # 找到共同的高层概念
        common_concept = None
        for source_entity in source_chain:
            if source_entity['level'] == 3:  # 概念层
                for target_entity in target_chain:
                    if (target_entity['level'] == 3 and
                        source_entity['entity_id'] == target_entity['entity_id']):
                        common_concept = source_entity
                        break
                if common_concept:
                    break
        
        return {
            'source_entity_id': source_entity_id,
            'target_entity_id': target_entity_id,
            'common_concept': common_concept,
            'similarity': 0.8 if common_concept else 0.0
        }
