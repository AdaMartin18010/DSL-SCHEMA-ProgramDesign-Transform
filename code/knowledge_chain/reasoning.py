"""
知识链推理

实现自底向上和自顶向下推理
"""

from typing import List, Dict, Any, Optional
from .storage import KnowledgeChainStorage


class KnowledgeChainReasoning:
    """知识链推理器"""
    
    def __init__(self, storage: KnowledgeChainStorage):
        """
        初始化推理器
        
        Args:
            storage: 知识链存储管理器
        """
        self.storage = storage
    
    def bottom_up_reasoning(self, chain_id: str) -> List[Dict[str, Any]]:
        """
        自底向上推理（K₁ → K₂ → K₃）
        
        Args:
            chain_id: 知识链ID
            
        Returns:
            推理路径
        """
        chain = self.storage.get_chain(chain_id)
        if not chain:
            return []
        
        node_ids = chain['node_ids']
        reasoning_path = []
        
        # 按层次组织节点
        k1_nodes = []
        k2_nodes = []
        k3_nodes = []
        
        for node_id in node_ids:
            # 获取节点信息（简化实现）
            if node_id.startswith('entity_'):
                k1_nodes.append(node_id)
            elif node_id.startswith('pattern_'):
                k2_nodes.append(node_id)
            elif node_id.startswith('concept_'):
                k3_nodes.append(node_id)
        
        # 构建推理路径
        step = 1
        for node_id in k1_nodes:
            reasoning_path.append({
                'step': step,
                'level': 1,
                'node_id': node_id,
                'reasoning_type': 'extraction'
            })
            step += 1
        
        for node_id in k2_nodes:
            reasoning_path.append({
                'step': step,
                'level': 2,
                'node_id': node_id,
                'reasoning_type': 'pattern_abstraction'
            })
            step += 1
        
        for node_id in k3_nodes:
            reasoning_path.append({
                'step': step,
                'level': 3,
                'node_id': node_id,
                'reasoning_type': 'concept_abstraction'
            })
            step += 1
        
        return reasoning_path
    
    def top_down_reasoning(self, chain_id: str) -> List[Dict[str, Any]]:
        """
        自顶向下推理（K₃ → K₂ → K₁）
        
        Args:
            chain_id: 知识链ID
            
        Returns:
            推理路径
        """
        chain = self.storage.get_chain(chain_id)
        if not chain:
            return []
        
        node_ids = chain['node_ids']
        reasoning_path = []
        
        # 反向遍历节点
        step = 1
        for node_id in reversed(node_ids):
            if node_id.startswith('concept_'):
                level = 3
                reasoning_type = 'concept_concretization'
            elif node_id.startswith('pattern_'):
                level = 2
                reasoning_type = 'pattern_concretization'
            else:
                level = 1
                reasoning_type = 'instance'
            
            reasoning_path.append({
                'step': step,
                'level': level,
                'node_id': node_id,
                'reasoning_type': reasoning_type
            })
            step += 1
        
        return reasoning_path
