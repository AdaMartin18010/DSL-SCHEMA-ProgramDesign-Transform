"""
知识链构建

构建从低层到高层的知识链
"""

from typing import List, Dict, Any, Optional
from .storage import KnowledgeChainStorage
from .extraction import LowLevelKnowledgeExtractor
from .abstraction import HighLevelConceptAbstraction


class KnowledgeChainBuilder:
    """知识链构建器"""
    
    def __init__(self, storage: KnowledgeChainStorage):
        """
        初始化构建器
        
        Args:
            storage: 知识链存储管理器
        """
        self.storage = storage
        self.extractor = LowLevelKnowledgeExtractor(storage)
        self.abstraction = HighLevelConceptAbstraction(storage)
    
    def build_chain(self, schema_doc: Dict[str, Any],
                   chain_name: str) -> Optional[Dict[str, Any]]:
        """
        构建知识链
        
        Args:
            schema_doc: Schema文档字典
            chain_name: 知识链名称
            
        Returns:
            知识链字典（如果成功）
        """
        # 1. 提取低层次知识（K₁层）
        entities = self.extractor.extract_entities(schema_doc)
        relations = self.extractor.extract_relations(schema_doc)
        
        if not entities:
            return None
        
        # 2. 抽象为模式（K₂层）
        pattern = self.abstraction.abstract_pattern(entities)
        
        if not pattern:
            return None
        
        # 3. 抽象为概念（K₃层）
        concept = self.abstraction.abstract_concept([pattern])
        
        if not concept:
            return None
        
        # 4. 构建知识链
        node_ids = [
            e['node_id'] for e in entities
        ] + [pattern['node_id'], concept['node_id']]
        
        abstraction_functions = [
            'extract_entities',
            'abstract_pattern',
            'abstract_concept'
        ]
        
        chain_id = f"chain_{hash(str(node_ids))}"
        success = self.storage.create_chain(
            chain_id=chain_id,
            name=chain_name,
            node_ids=node_ids,
            abstraction_functions=abstraction_functions
        )
        
        if success:
            return {
                'chain_id': chain_id,
                'name': chain_name,
                'node_ids': node_ids,
                'abstraction_functions': abstraction_functions,
                'levels': {
                    'K1': [e['node_id'] for e in entities],
                    'K2': [pattern['node_id']],
                    'K3': [concept['node_id']]
                }
            }
        
        return None
