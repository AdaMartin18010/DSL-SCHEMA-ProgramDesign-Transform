"""
时序知识图谱数据模型

基于SQLAlchemy ORM定义数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class TemporalEntity(Base):
    """时序实体表"""
    __tablename__ = 'temporal_entities'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime)  # None表示持续有效
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TemporalRelation(Base):
    """时序关系表"""
    __tablename__ = 'temporal_relations'
    
    id = Column(Integer, primary_key=True)
    source_entity_id = Column(String(50), nullable=False)
    target_entity_id = Column(String(50), nullable=False)
    relation_type = Column(String(50), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime)
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)


class EntitySnapshot(Base):
    """实体快照表（用于快速查询历史状态）"""
    __tablename__ = 'entity_snapshots'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), nullable=False)
    snapshot_time = Column(DateTime, nullable=False)
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
