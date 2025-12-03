"""
知识图谱嵌入

实现实体、关系、子图的嵌入
"""

import numpy as np
from typing import List, Dict, Any, Optional
from .llm_interface import LLMInterface


class KGEmbedding:
    """知识图谱嵌入器"""
    
    def __init__(self, llm: LLMInterface):
        """
        初始化知识图谱嵌入器
        
        Args:
            llm: LLM接口实例
        """
        self.llm = llm
    
    def embed_entity(self, entity: Dict[str, Any]) -> np.ndarray:
        """
        嵌入实体
        
        Args:
            entity: 实体字典，包含id, type, properties等
            
        Returns:
            实体嵌入向量
        """
        # 构建实体描述
        description = self._build_entity_description(entity)
        
        # 生成嵌入
        embedding = self.llm.embed(description)
        
        return np.array(embedding)
    
    def embed_relation(self, relation: Dict[str, Any]) -> np.ndarray:
        """
        嵌入关系
        
        Args:
            relation: 关系字典，包含source, target, type等
            
        Returns:
            关系嵌入向量
        """
        # 构建关系描述
        description = self._build_relation_description(relation)
        
        # 生成嵌入
        embedding = self.llm.embed(description)
        
        return np.array(embedding)
    
    def embed_subgraph(self, entities: List[Dict], relations: List[Dict]) -> np.ndarray:
        """
        嵌入子图
        
        Args:
            entities: 实体列表
            relations: 关系列表
            
        Returns:
            子图嵌入向量
        """
        # 构建子图描述
        description = self._build_subgraph_description(entities, relations)
        
        # 生成嵌入
        embedding = self.llm.embed(description)
        
        return np.array(embedding)
    
    def _build_entity_description(self, entity: Dict[str, Any]) -> str:
        """构建实体描述"""
        parts = [f"实体ID: {entity.get('id', 'unknown')}"]
        
        if 'type' in entity:
            parts.append(f"类型: {entity['type']}")
        
        if 'properties' in entity:
            props = entity['properties']
            if isinstance(props, dict):
                prop_str = ", ".join([f"{k}: {v}" for k, v in props.items()])
                parts.append(f"属性: {prop_str}")
        
        return " | ".join(parts)
    
    def _build_relation_description(self, relation: Dict[str, Any]) -> str:
        """构建关系描述"""
        parts = []
        
        if 'source' in relation:
            parts.append(f"源实体: {relation['source']}")
        
        if 'type' in relation:
            parts.append(f"关系类型: {relation['type']}")
        
        if 'target' in relation:
            parts.append(f"目标实体: {relation['target']}")
        
        return " | ".join(parts)
    
    def _build_subgraph_description(self, entities: List[Dict],
                                   relations: List[Dict]) -> str:
        """构建子图描述"""
        parts = []
        
        # 实体描述
        entity_descriptions = []
        for entity in entities:
            entity_descriptions.append(self._build_entity_description(entity))
        parts.append(f"实体: {'; '.join(entity_descriptions)}")
        
        # 关系描述
        relation_descriptions = []
        for relation in relations:
            relation_descriptions.append(self._build_relation_description(relation))
        parts.append(f"关系: {'; '.join(relation_descriptions)}")
        
        return "\n".join(parts)
