"""
低层次知识提取

从Schema文档提取实体、关系、属性
"""

from typing import List, Dict, Any, Optional
from .storage import KnowledgeChainStorage


class LowLevelKnowledgeExtractor:
    """低层次知识提取器"""
    
    def __init__(self, storage: KnowledgeChainStorage):
        """
        初始化提取器
        
        Args:
            storage: 知识链存储管理器
        """
        self.storage = storage
    
    def extract_entities(self, schema_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取实体
        
        Args:
            schema_doc: Schema文档字典
            
        Returns:
            实体列表
        """
        entities = []
        
        # 从Schema文档中提取实体（简化实现）
        if 'entities' in schema_doc:
            for entity in schema_doc['entities']:
                entity_id = f"entity_{entity.get('id', len(entities))}"
                entities.append({
                    'node_id': entity_id,
                    'name': entity.get('name', 'Entity'),
                    'level': 1,  # 低层
                    'node_type': 'entity',
                    'content': entity,
                    'properties': entity.get('properties', {})
                })
                
                # 存储节点
                self.storage.add_node(
                    node_id=entity_id,
                    name=entity.get('name', 'Entity'),
                    level=1,
                    node_type='entity',
                    content=entity,
                    properties=entity.get('properties', {})
                )
        
        return entities
    
    def extract_relations(self, schema_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取关系
        
        Args:
            schema_doc: Schema文档字典
            
        Returns:
            关系列表
        """
        relations = []
        
        # 从Schema文档中提取关系（简化实现）
        if 'relations' in schema_doc:
            for relation in schema_doc['relations']:
                relation_id = f"relation_{relation.get('id', len(relations))}"
                relations.append({
                    'node_id': relation_id,
                    'name': relation.get('type', 'Relation'),
                    'level': 1,  # 低层
                    'node_type': 'relation',
                    'content': relation,
                    'properties': relation.get('properties', {})
                })
                
                # 存储节点
                self.storage.add_node(
                    node_id=relation_id,
                    name=relation.get('type', 'Relation'),
                    level=1,
                    node_type='relation',
                    content=relation,
                    properties=relation.get('properties', {})
                )
        
        return relations
    
    def extract_attributes(self, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取属性
        
        Args:
            entity: 实体字典
            
        Returns:
            属性列表
        """
        attributes = []
        
        # 从实体中提取属性（简化实现）
        if 'attributes' in entity:
            for attr in entity['attributes']:
                attr_id = f"attr_{attr.get('name', len(attributes))}"
                attributes.append({
                    'node_id': attr_id,
                    'name': attr.get('name', 'Attribute'),
                    'level': 1,  # 低层
                    'node_type': 'attribute',
                    'content': attr,
                    'properties': attr.get('properties', {})
                })
        
        return attributes
