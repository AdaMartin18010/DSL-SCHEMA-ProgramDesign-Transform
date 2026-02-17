"""
知识链数据模型

基于SQLAlchemy ORM定义数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class KnowledgeNode(Base):
    """知识节点表"""
    __tablename__ = 'knowledge_nodes'
    
    id = Column(Integer, primary_key=True)
    node_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    level = Column(Integer, nullable=False)  # 1:低层, 2:中层, 3:高层
    node_type = Column(String(50))  # 'entity', 'relation', 'pattern', 'concept', 'principle'
    
    # 知识内容
    content = Column(JSON)
    properties = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class KnowledgeChain(Base):
    """知识链表"""
    __tablename__ = 'knowledge_chains'
    
    id = Column(Integer, primary_key=True)
    chain_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    node_ids = Column(JSON)  # 节点ID列表，按层次排序
    abstraction_functions = Column(JSON)  # 抽象函数列表
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ChainLink(Base):
    """知识链链接表"""
    __tablename__ = 'chain_links'
    
    id = Column(Integer, primary_key=True)
    chain_id = Column(String(50), ForeignKey('knowledge_chains.chain_id'))
    source_node_id = Column(String(50), ForeignKey('knowledge_nodes.node_id'))
    target_node_id = Column(String(50), ForeignKey('knowledge_nodes.node_id'))
    link_type = Column(String(50))  # 'abstraction', 'concretization'
    abstraction_function = Column(String(200))  # 抽象函数名称
    confidence = Column(Integer)  # 0-100
    
    created_at = Column(DateTime, default=datetime.now)
