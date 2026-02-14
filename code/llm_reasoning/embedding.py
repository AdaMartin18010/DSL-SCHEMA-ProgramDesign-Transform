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


class EmbeddingStore:
    """
    嵌入存储类
    
    用于存储和搜索嵌入向量
    """
    
    def __init__(self, dimension: int = 1536):
        """
        初始化嵌入存储
        
        Args:
            dimension: 嵌入向量维度
        """
        self.dimension = dimension
        self.embeddings: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add(self, key: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """
        添加嵌入向量
        
        Args:
            key: 唯一标识符
            embedding: 嵌入向量
            metadata: 关联的元数据
        """
        self.embeddings[key] = np.array(embedding)
        self.metadata[key] = metadata or {}
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """
        获取嵌入向量
        
        Args:
            key: 唯一标识符
            
        Returns:
            嵌入向量或None
        """
        return self.embeddings.get(key)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[tuple]:
        """
        搜索最相似的嵌入向量
        
        Args:
            query_embedding: 查询嵌入向量
            top_k: 返回结果数量
            
        Returns:
            列表，每个元素为 (key, similarity)
        """
        if not self.embeddings:
            return []
        
        query = np.array(query_embedding)
        similarities = []
        
        for key, embedding in self.embeddings.items():
            # 计算余弦相似度
            similarity = self._cosine_similarity(query, embedding)
            similarities.append((key, similarity))
        
        # 按相似度排序并返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            a: 向量a
            b: 向量b
            
        Returns:
            余弦相似度 (-1 到 1)
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def remove(self, key: str):
        """
        删除嵌入向量
        
        Args:
            key: 唯一标识符
        """
        if key in self.embeddings:
            del self.embeddings[key]
        if key in self.metadata:
            del self.metadata[key]
    
    def clear(self):
        """清空所有嵌入向量"""
        self.embeddings.clear()
        self.metadata.clear()
    
    def keys(self) -> List[str]:
        """
        获取所有键
        
        Returns:
            键列表
        """
        return list(self.embeddings.keys())
    
    def __len__(self) -> int:
        """返回存储的嵌入数量"""
        return len(self.embeddings)
