"""
多模态融合算法

实现文本和图像嵌入的融合
"""

import numpy as np
from typing import List, Optional
from sklearn.decomposition import PCA


class MultimodalFusion:
    """多模态融合算法"""
    
    def __init__(self, fusion_method: str = 'weighted_average'):
        """
        初始化多模态融合器
        
        Args:
            fusion_method: 融合方法
                - 'weighted_average': 加权平均
                - 'concatenation': 拼接
                - 'attention': 注意力机制
        """
        self.fusion_method = fusion_method
    
    def fuse(self, text_embedding: np.ndarray,
             image_embedding: np.ndarray,
             text_weight: float = 0.5,
             image_weight: float = 0.5) -> np.ndarray:
        """
        融合文本和图像嵌入
        
        Args:
            text_embedding: 文本嵌入向量
            image_embedding: 图像嵌入向量
            text_weight: 文本权重
            image_weight: 图像权重
            
        Returns:
            融合后的向量
        """
        if self.fusion_method == 'weighted_average':
            return self._weighted_average(
                text_embedding, image_embedding,
                text_weight, image_weight
            )
        elif self.fusion_method == 'concatenation':
            return self._concatenation(text_embedding, image_embedding)
        elif self.fusion_method == 'attention':
            return self._attention_fusion(text_embedding, image_embedding)
        else:
            raise ValueError(f"Unknown fusion method: {self.fusion_method}")
    
    def _weighted_average(self, text_emb: np.ndarray, image_emb: np.ndarray,
                         text_weight: float, image_weight: float) -> np.ndarray:
        """加权平均融合"""
        # 对齐维度
        if text_emb.shape[0] != image_emb.shape[0]:
            min_dim = min(text_emb.shape[0], image_emb.shape[0])
            
            if text_emb.shape[0] > min_dim:
                pca = PCA(n_components=min_dim)
                text_emb = pca.fit_transform(text_emb.reshape(1, -1))[0]
            
            if image_emb.shape[0] > min_dim:
                pca = PCA(n_components=min_dim)
                image_emb = pca.fit_transform(image_emb.reshape(1, -1))[0]
        
        # 加权平均
        fused = text_weight * text_emb + image_weight * image_emb
        return fused
    
    def _concatenation(self, text_emb: np.ndarray, image_emb: np.ndarray) -> np.ndarray:
        """拼接融合"""
        return np.concatenate([text_emb, image_emb])
    
    def _attention_fusion(self, text_emb: np.ndarray, image_emb: np.ndarray) -> np.ndarray:
        """注意力机制融合"""
        # 计算注意力权重
        attention_weights = self._compute_attention_weights(text_emb, image_emb)
        
        # 对齐维度（如果需要）
        if text_emb.shape[0] != image_emb.shape[0]:
            min_dim = min(text_emb.shape[0], image_emb.shape[0])
            
            if text_emb.shape[0] > min_dim:
                pca = PCA(n_components=min_dim)
                text_emb = pca.fit_transform(text_emb.reshape(1, -1))[0]
            
            if image_emb.shape[0] > min_dim:
                pca = PCA(n_components=min_dim)
                image_emb = pca.fit_transform(image_emb.reshape(1, -1))[0]
        
        # 加权融合
        fused = (attention_weights[0] * text_emb +
                attention_weights[1] * image_emb)
        return fused
    
    def _compute_attention_weights(self, text_emb: np.ndarray,
                                   image_emb: np.ndarray) -> List[float]:
        """
        计算注意力权重
        
        Args:
            text_emb: 文本嵌入向量
            image_emb: 图像嵌入向量
            
        Returns:
            注意力权重列表 [text_weight, image_weight]
        """
        # 简化实现：基于嵌入的范数
        text_norm = np.linalg.norm(text_emb)
        image_norm = np.linalg.norm(image_emb)
        
        total_norm = text_norm + image_norm
        if total_norm == 0:
            return [0.5, 0.5]
        
        text_weight = text_norm / total_norm
        image_weight = image_norm / total_norm
        
        return [text_weight, image_weight]
