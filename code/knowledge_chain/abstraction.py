"""
高层次概念抽象

从低层次知识抽象高层次概念
"""

from typing import List, Dict, Any, Optional
from .storage import KnowledgeChainStorage


class HighLevelConceptAbstraction:
    """高层次概念抽象器"""
    
    def __init__(self, storage: KnowledgeChainStorage):
        """
        初始化抽象器
        
        Args:
            storage: 知识链存储管理器
        """
        self.storage = storage
    
    def abstract_pattern(self, instance_nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        模式抽象（从多个实例抽象模式）
        
        Args:
            instance_nodes: 实例节点列表
            
        Returns:
            模式节点（如果成功）
        """
        if not instance_nodes:
            return None
        
        # 提取共同特征
        common_features = self._extract_common_features(instance_nodes)
        
        # 构建模式
        pattern = {
            'name': 'Abstracted Pattern',
            'level': 2,  # 中层
            'node_type': 'pattern',
            'content': {
                'common_features': common_features,
                'instance_count': len(instance_nodes)
            },
            'properties': {
                'instance_ids': [n['node_id'] for n in instance_nodes]
            }
        }
        
        # 存储模式节点
        pattern_id = f"pattern_{hash(str([n['node_id'] for n in instance_nodes]))}"
        success = self.storage.add_node(
            node_id=pattern_id,
            name=pattern['name'],
            level=2,
            node_type='pattern',
            content=pattern['content'],
            properties=pattern['properties']
        )
        
        if success:
            pattern['node_id'] = pattern_id
            return pattern
        return None
    
    def abstract_concept(self, pattern_nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        概念抽象（从多个模式抽象概念）
        
        Args:
            pattern_nodes: 模式节点列表
            
        Returns:
            概念节点（如果成功）
        """
        if not pattern_nodes:
            return None
        
        # 提取模式共性
        commonality = self._extract_commonality(pattern_nodes)
        
        # 构建概念
        concept = {
            'name': 'Abstracted Concept',
            'level': 3,  # 高层
            'node_type': 'concept',
            'content': {
                'commonality': commonality,
                'pattern_count': len(pattern_nodes)
            },
            'properties': {
                'pattern_ids': [n['node_id'] for n in pattern_nodes]
            }
        }
        
        # 存储概念节点
        concept_id = f"concept_{hash(str([n['node_id'] for n in pattern_nodes]))}"
        success = self.storage.add_node(
            node_id=concept_id,
            name=concept['name'],
            level=3,
            node_type='concept',
            content=concept['content'],
            properties=concept['properties']
        )
        
        if success:
            concept['node_id'] = concept_id
            return concept
        return None
    
    def abstract_principle(self, concept_nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        原理抽象（从多个概念抽象原理）
        
        Args:
            concept_nodes: 概念节点列表
            
        Returns:
            原理节点（如果成功）
        """
        if not concept_nodes:
            return None
        
        # 提取概念共性
        commonality = self._extract_commonality(concept_nodes)
        
        # 构建原理
        principle = {
            'name': 'Abstracted Principle',
            'level': 3,  # 高层（原理也是概念层）
            'node_type': 'principle',
            'content': {
                'commonality': commonality,
                'concept_count': len(concept_nodes)
            },
            'properties': {
                'concept_ids': [n['node_id'] for n in concept_nodes]
            }
        }
        
        # 存储原理节点
        principle_id = f"principle_{hash(str([n['node_id'] for n in concept_nodes]))}"
        success = self.storage.add_node(
            node_id=principle_id,
            name=principle['name'],
            level=3,
            node_type='principle',
            content=principle['content'],
            properties=principle['properties']
        )
        
        if success:
            principle['node_id'] = principle_id
            return principle
        return None
    
    def _extract_common_features(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取共同特征"""
        if not nodes:
            return {}
        
        common_features = {}
        first_node = nodes[0]
        
        # 比较属性
        if 'properties' in first_node:
            for key, value in first_node['properties'].items():
                if all(n.get('properties', {}).get(key) == value for n in nodes):
                    common_features[key] = value
        
        return common_features
    
    def _extract_commonality(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取共性"""
        if not nodes:
            return {}
        
        commonality = {
            'common_structure': {},
            'common_principles': []
        }
        
        # 简化实现
        return commonality
