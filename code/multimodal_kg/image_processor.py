"""
图像模态处理器

实现图像嵌入、存储和检索功能
"""

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import requests
from io import BytesIO
from typing import List, Dict, Any, Optional
import numpy as np
from .storage import MultimodalKGStorage


class ImageModalityProcessor:
    """图像模态处理器"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32",
                 storage: Optional[MultimodalKGStorage] = None):
        """
        初始化图像模态处理器
        
        Args:
            model_name: CLIP模型名称
            storage: 存储管理器（如果为None，则创建新的）
        """
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        self.storage = storage or MultimodalKGStorage()
    
    def load_image(self, image_url: str) -> Image.Image:
        """
        加载图像
        
        Args:
            image_url: 图像URL或本地路径
            
        Returns:
            PIL Image对象
        """
        if image_url.startswith('http://') or image_url.startswith('https://'):
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_url)
        
        return image
    
    def get_embedding(self, image: Image.Image) -> np.ndarray:
        """
        生成图像嵌入向量
        
        Args:
            image: PIL Image对象
            
        Returns:
            嵌入向量
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            embedding = self.model.get_image_features(**inputs)
        
        embedding = embedding.cpu().numpy()[0]
        return embedding
    
    def process_image(self, entity_id: str, image_url: str,
                     image_type: str = 'schema_diagram',
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        处理图像并存储
        
        Args:
            entity_id: 实体ID
            image_url: 图像URL
            image_type: 图像类型
            metadata: 元数据
            
        Returns:
            是否成功
        """
        try:
            # 加载图像
            image = self.load_image(image_url)
            
            # 生成嵌入向量
            embedding = self.get_embedding(image)
            
            # 存储到数据库
            return self.storage.add_image_modality(
                entity_id=entity_id,
                image_url=image_url,
                image_type=image_type,
                embedding=embedding.tolist(),
                metadata=metadata
            )
        except Exception as e:
            print(f"处理图像失败: {e}")
            return False
    
    def search_similar(self, query_image_url: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        图像相似度搜索
        
        Args:
            query_image_url: 查询图像URL
            top_k: 返回结果数量
            
        Returns:
            相似图像列表
        """
        try:
            # 加载查询图像
            query_image = self.load_image(query_image_url)
            
            # 生成查询向量
            query_embedding = self.get_embedding(query_image)
            
            # 向量相似度搜索
            return self.storage.search_image_similar(
                query_embedding=query_embedding.tolist(),
                top_k=top_k
            )
        except Exception as e:
            print(f"图像搜索失败: {e}")
            return []
    
    def batch_process(self, images: List[Dict[str, Any]]) -> int:
        """
        批量处理图像
        
        Args:
            images: 图像列表，每个元素包含entity_id, image_url, image_type等
            
        Returns:
            成功处理的数量
        """
        success_count = 0
        for image_data in images:
            if self.process_image(
                entity_id=image_data['entity_id'],
                image_url=image_data['image_url'],
                image_type=image_data.get('image_type', 'schema_diagram'),
                metadata=image_data.get('metadata')
            ):
                success_count += 1
        
        return success_count
