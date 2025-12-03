"""
层次化查询

实现基于层次的查询功能
"""

from typing import List, Dict, Any, Optional
from .storage import HierarchicalKGStorage


class HierarchicalQuery:
    """层次化查询器"""
    
    def __init__(self, storage: HierarchicalKGStorage):
        """
        初始化层次化查询器
        
        Args:
            storage: 层次化知识图谱存储管理器
        """
        self.storage = storage
    
    def query_by_level(self, level: int,
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        按层次查询
        
        Args:
            level: 层次（1、2、3）
            filters: 过滤条件
            
        Returns:
            实体列表
        """
        entities = self.storage.get_entities_by_level(level)
        
        # 应用过滤条件
        if filters:
            filtered_entities = []
            for entity in entities:
                match = True
                for key, value in filters.items():
                    if entity.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_entities.append(entity)
            return filtered_entities
        
        return entities
    
    def query_abstraction_hierarchy(self, entity_id: str) -> Dict[str, Any]:
        """
        查询抽象层次结构
        
        Args:
            entity_id: 实体ID
            
        Returns:
            层次结构字典
        """
        # 获取抽象链
        abstraction_chain = self.storage.get_abstraction_chain(entity_id)
        
        # 构建层次结构
        hierarchy = {
            'entity_id': entity_id,
            'levels': {}
        }
        
        for entity in abstraction_chain:
            level = entity['level']
            if level not in hierarchy['levels']:
                hierarchy['levels'][level] = []
            hierarchy['levels'][level].append(entity)
        
        return hierarchy
    
    def query_concept_instances(self, concept_id: str) -> List[Dict[str, Any]]:
        """
        查询概念的所有实例
        
        Args:
            concept_id: 概念实体ID
            
        Returns:
            实例列表
        """
        # 获取具体化链
        concretization_chain = self.storage.get_concretization_chain(concept_id)
        
        # 过滤出实例层（level=1）
        instances = [e for e in concretization_chain if e['level'] == 1]
        
        return instances
    
    def query_pattern_instances(self, pattern_id: str) -> List[Dict[str, Any]]:
        """
        查询模式的所有实例
        
        Args:
            pattern_id: 模式实体ID
            
        Returns:
            实例列表
        """
        # 获取模式实体
        entities = self.storage.get_entities_by_level(2)
        pattern = next((e for e in entities if e['entity_id'] == pattern_id), None)
        
        if not pattern:
            return []
        
        # 从属性中获取实例ID列表
        instance_ids = pattern.get('properties', {}).get('instance_ids', [])
        
        # 获取实例实体
        instances = []
        for instance_id in instance_ids:
            entities = self.storage.get_entities_by_level(1)
            instance = next((e for e in entities if e['entity_id'] == instance_id), None)
            if instance:
                instances.append(instance)
        
        return instances
