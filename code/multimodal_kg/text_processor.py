"""
文本模态处理器

实现文本嵌入、存储和检索功能
"""

from typing import List, Dict, Any, Optional
import numpy as np
from .storage import MultimodalKGStorage

# 条件导入sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class TextModalityProcessor:
    """文本模态处理器"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2',
                 storage: Optional[MultimodalKGStorage] = None):
        """
        初始化文本模态处理器
        
        Args:
            model_name: 文本嵌入模型名称
            storage: 存储管理器（如果为None，则创建新的）
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence_transformers is required for TextModalityProcessor. "
                "Install it with: pip install sentence-transformers"
            )
        self.model = SentenceTransformer(model_name)
        self.storage = storage or MultimodalKGStorage()
    
    def process_text(self, entity_id: str, content: str,
                    content_type: str = 'schema_doc',
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        处理文本并存储
        
        Args:
            entity_id: 实体ID
            content: 文本内容
            content_type: 内容类型
            metadata: 元数据
            
        Returns:
            是否成功
        """
        # 生成嵌入向量
        embedding = self.model.encode(content)
        
        # 存储到数据库
        return self.storage.add_text_modality(
            entity_id=entity_id,
            content=content,
            content_type=content_type,
            embedding=embedding.tolist(),
            metadata=metadata
        )
    
    def search_similar(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        语义相似度搜索
        
        Args:
            query_text: 查询文本
            top_k: 返回结果数量
            
        Returns:
            相似文本列表
        """
        # 生成查询向量
        query_embedding = self.model.encode(query_text)
        
        # 向量相似度搜索
        return self.storage.search_text_similar(
            query_embedding=query_embedding.tolist(),
            top_k=top_k
        )
    
    def batch_process(self, texts: List[Dict[str, Any]]) -> int:
        """
        批量处理文本
        
        Args:
            texts: 文本列表，每个元素包含entity_id, content, content_type等
            
        Returns:
            成功处理的数量
        """
        success_count = 0
        for text_data in texts:
            if self.process_text(
                entity_id=text_data['entity_id'],
                content=text_data['content'],
                content_type=text_data.get('content_type', 'schema_doc'),
                metadata=text_data.get('metadata')
            ):
                success_count += 1
        
        return success_count
