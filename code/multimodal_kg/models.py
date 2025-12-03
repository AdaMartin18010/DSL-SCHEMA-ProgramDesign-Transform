"""
多模态知识图谱数据模型

基于SQLAlchemy ORM定义数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import pgvector.sqlalchemy

Base = declarative_base()


class MultimodalEntity(Base):
    """多模态实体表（主表）"""
    __tablename__ = 'multimodal_entities'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), unique=True, nullable=False)
    entity_type = Column(String(50))  # 'schema', 'concept', 'relationship'
    text_content = Column(Text)
    image_url = Column(Text)
    fused_embedding = Column(pgvector.sqlalchemy.Vector(512))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    text_modalities = relationship("TextModality", back_populates="entity")
    image_modalities = relationship("ImageModality", back_populates="entity")


class TextModality(Base):
    """文本模态表"""
    __tablename__ = 'text_modalities'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), ForeignKey('multimodal_entities.entity_id'))
    content = Column(Text, nullable=False)
    content_type = Column(String(50))  # 'schema_doc', 'annotation', 'metadata'
    embedding = Column(pgvector.sqlalchemy.Vector(384))  # all-MiniLM-L6-v2维度
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    entity = relationship("MultimodalEntity", back_populates="text_modalities")


class ImageModality(Base):
    """图像模态表"""
    __tablename__ = 'image_modalities'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), ForeignKey('multimodal_entities.entity_id'))
    image_url = Column(Text, nullable=False)
    image_type = Column(String(50))  # 'schema_diagram', 'architecture', 'flowchart'
    embedding = Column(pgvector.sqlalchemy.Vector(512))  # CLIP维度
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    entity = relationship("MultimodalEntity", back_populates="image_modalities")


class MultimodalRelation(Base):
    """多模态关系表"""
    __tablename__ = 'multimodal_relations'
    
    id = Column(Integer, primary_key=True)
    source_entity_id = Column(String(50), ForeignKey('multimodal_entities.entity_id'))
    target_entity_id = Column(String(50), ForeignKey('multimodal_entities.entity_id'))
    relation_type = Column(String(50))
    confidence = Column(Integer)  # 0-100
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
