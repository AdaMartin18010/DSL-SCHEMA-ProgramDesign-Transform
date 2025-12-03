"""
可解释性推理数据模型

基于SQLAlchemy ORM定义数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ReasoningRule(Base):
    """推理规则表"""
    __tablename__ = 'reasoning_rules'
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    rule_type = Column(String(50))  # 'if_then', 'pattern', 'constraint'
    condition = Column(JSON)  # 条件
    conclusion = Column(JSON)  # 结论
    confidence = Column(Integer)  # 0-100
    priority = Column(Integer)  # 优先级
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)


class ReasoningPath(Base):
    """推理路径表"""
    __tablename__ = 'reasoning_paths'
    
    id = Column(Integer, primary_key=True)
    path_id = Column(String(50), unique=True, nullable=False)
    query = Column(Text)  # 查询问题
    result = Column(JSON)  # 推理结果
    steps = Column(JSON)  # 推理步骤列表
    rules_applied = Column(JSON)  # 应用的规则列表
    confidence = Column(Integer)  # 0-100
    created_at = Column(DateTime, default=datetime.now)


class ReasoningStep(Base):
    """推理步骤表"""
    __tablename__ = 'reasoning_steps'
    
    id = Column(Integer, primary_key=True)
    path_id = Column(String(50), ForeignKey('reasoning_paths.path_id'))
    step_number = Column(Integer, nullable=False)
    step_type = Column(String(50))  # 'rule_application', 'fact_retrieval', 'inference'
    input_data = Column(JSON)
    output_data = Column(JSON)
    rule_id = Column(String(50), ForeignKey('reasoning_rules.rule_id'))
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
