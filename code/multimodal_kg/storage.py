"""
多模态知识图谱PostgreSQL存储实现

实现数据库连接、存储和查询功能
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import os
from .models import Base, MultimodalEntity, TextModality, ImageModality, MultimodalRelation


class MultimodalKGStorage:
    """多模态知识图谱存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
                         默认从环境变量DATABASE_URL读取
        """
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://user:password@localhost:5432/multimodal_kg'
            )
        
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def initialize_database(self):
        """初始化数据库（创建表）"""
        try:
            # 创建pgvector扩展
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            
            # 创建所有表
            Base.metadata.create_all(self.engine)
            
            # 创建索引
            self._create_indexes()
            
            return True
        except SQLAlchemyError as e:
            print(f"数据库初始化失败: {e}")
            return False
    
    def _create_indexes(self):
        """创建数据库索引"""
        with self.engine.connect() as conn:
            # 向量索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_multimodal_entities_fused_embedding
                ON multimodal_entities USING ivfflat (fused_embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_text_modalities_embedding
                ON text_modalities USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_image_modalities_embedding
                ON image_modalities USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            # 全文搜索索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_text_modalities_content
                ON text_modalities USING GIN (to_tsvector('english', content))
            """))
            
            conn.commit()
    
    def add_text_modality(self, entity_id: str, content: str,
                         content_type: str, embedding: List[float],
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加文本模态
        
        Args:
            entity_id: 实体ID
            content: 文本内容
            content_type: 内容类型
            embedding: 文本嵌入向量
            metadata: 元数据
            
        Returns:
            是否成功
        """
        try:
            session = self.Session()
            
            # 确保实体存在
            entity = session.query(MultimodalEntity).filter(
                MultimodalEntity.entity_id == entity_id
            ).first()
            
            if not entity:
                entity = MultimodalEntity(
                    entity_id=entity_id,
                    entity_type='schema',
                    text_content=content
                )
                session.add(entity)
            
            # 添加文本模态
            text_modality = TextModality(
                entity_id=entity_id,
                content=content,
                content_type=content_type,
                embedding=embedding,
            )
            session.add(text_modality)
            session.commit()
            session.close()
            
            return True
        except SQLAlchemyError as e:
            print(f"添加文本模态失败: {e}")
            return False
    
    def add_image_modality(self, entity_id: str, image_url: str,
                          image_type: str, embedding: List[float],
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加图像模态
        
        Args:
            entity_id: 实体ID
            image_url: 图像URL
            image_type: 图像类型
            embedding: 图像嵌入向量
            metadata: 元数据
            
        Returns:
            是否成功
        """
        try:
            session = self.Session()
            
            # 确保实体存在
            entity = session.query(MultimodalEntity).filter(
                MultimodalEntity.entity_id == entity_id
            ).first()
            
            if not entity:
                entity = MultimodalEntity(
                    entity_id=entity_id,
                    entity_type='schema',
                    image_url=image_url
                )
                session.add(entity)
            
            # 添加图像模态
            image_modality = ImageModality(
                entity_id=entity_id,
                image_url=image_url,
                image_type=image_type,
                embedding=embedding,
            )
            session.add(image_modality)
            session.commit()
            session.close()
            
            return True
        except SQLAlchemyError as e:
            print(f"添加图像模态失败: {e}")
            return False
    
    def search_text_similar(self, query_embedding: List[float],
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """
        文本相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            
        Returns:
            相似文本列表
        """
        try:
            session = self.Session()
            
            # 使用向量相似度搜索
            results = session.query(TextModality).order_by(
                TextModality.embedding.cosine_distance(query_embedding)
            ).limit(top_k).all()
            
            session.close()
            
            return [{
                'entity_id': r.entity_id,
                'content': r.content,
                'content_type': r.content_type,
                'similarity': 1.0 - float(r.embedding.cosine_distance(query_embedding))
            } for r in results]
        except SQLAlchemyError as e:
            print(f"文本搜索失败: {e}")
            return []
    
    def search_image_similar(self, query_embedding: List[float],
                            top_k: int = 10) -> List[Dict[str, Any]]:
        """
        图像相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            
        Returns:
            相似图像列表
        """
        try:
            session = self.Session()
            
            # 使用向量相似度搜索
            results = session.query(ImageModality).order_by(
                ImageModality.embedding.cosine_distance(query_embedding)
            ).limit(top_k).all()
            
            session.close()
            
            return [{
                'entity_id': r.entity_id,
                'image_url': r.image_url,
                'image_type': r.image_type,
                'similarity': 1.0 - float(r.embedding.cosine_distance(query_embedding))
            } for r in results]
        except SQLAlchemyError as e:
            print(f"图像搜索失败: {e}")
            return []
    
    def update_fused_embedding(self, entity_id: str, fused_embedding: List[float]) -> bool:
        """
        更新融合嵌入向量
        
        Args:
            entity_id: 实体ID
            fused_embedding: 融合后的嵌入向量
            
        Returns:
            是否成功
        """
        try:
            session = self.Session()
            entity = session.query(MultimodalEntity).filter(
                MultimodalEntity.entity_id == entity_id
            ).first()
            
            if entity:
                entity.fused_embedding = fused_embedding
                session.commit()
                session.close()
                return True
            else:
                session.close()
                return False
        except SQLAlchemyError as e:
            print(f"更新融合嵌入失败: {e}")
            return False
    
    def search_fused_similar(self, query_embedding: List[float],
                            top_k: int = 10) -> List[Dict[str, Any]]:
        """
        融合向量相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            
        Returns:
            相似实体列表
        """
        try:
            session = self.Session()
            
            # 使用向量相似度搜索
            results = session.query(MultimodalEntity).filter(
                MultimodalEntity.fused_embedding.isnot(None)
            ).order_by(
                MultimodalEntity.fused_embedding.cosine_distance(query_embedding)
            ).limit(top_k).all()
            
            session.close()
            
            return [{
                'entity_id': r.entity_id,
                'entity_type': r.entity_type,
                'text_content': r.text_content,
                'image_url': r.image_url,
                'similarity': 1.0 - float(r.fused_embedding.cosine_distance(query_embedding))
            } for r in results]
        except SQLAlchemyError as e:
            print(f"融合向量搜索失败: {e}")
            return []
