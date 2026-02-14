"""
层次化知识表示数据模型

基于SQLAlchemy ORM定义数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class HierarchicalEntity(Base):
    """层次化实体表"""
    __tablename__ = 'hierarchical_entities'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    level = Column(Integer, nullable=False)  # 1:实例层, 2:模式层, 3:概念层
    
    # 层次关系
    abstraction_id = Column(String(50), ForeignKey('hierarchical_entities.entity_id'))  # 抽象实体ID
    concretizations = Column(JSON)  # 具体化实体ID列表
    
    # 知识内容
    content = Column(JSON)  # 根据层次不同，存储不同内容
    properties = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    abstraction = relationship("HierarchicalEntity", remote_side=[entity_id], backref="concretization_list")


class AbstractionRelation(Base):
    """抽象关系表"""
    __tablename__ = 'abstraction_relations'
    
    id = Column(Integer, primary_key=True)
    source_entity_id = Column(String(50), ForeignKey('hierarchical_entities.entity_id'))
    target_entity_id = Column(String(50), ForeignKey('hierarchical_entities.entity_id'))
    abstraction_type = Column(String(50))  # 'instance_to_pattern', 'pattern_to_concept', 'instance_to_concept'
    confidence = Column(Integer)  # 0-100
    meta_data = Column(JSON)  # 使用meta_data避免与SQLAlchemy保留字冲突
    created_at = Column(DateTime, default=datetime.now)
