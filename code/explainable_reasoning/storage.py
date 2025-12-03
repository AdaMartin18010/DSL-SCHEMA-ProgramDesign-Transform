"""
可解释性推理PostgreSQL存储实现

实现数据库连接、存储和查询功能
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import os
from .models import Base, ReasoningRule, ReasoningPath, ReasoningStep


class ExplainableReasoningStorage:
    """可解释性推理存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
        """
        if database_url is None:
            database_url = os.getenv(
                'EXPLAINABLE_REASONING_DB_URL',
                'postgresql://user:password@localhost:5432/explainable_reasoning'
            )
        
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def initialize_database(self):
        """初始化数据库（创建表）"""
        try:
            Base.metadata.create_all(self.engine)
            self._create_indexes()
            return True
        except SQLAlchemyError as e:
            print(f"数据库初始化失败: {e}")
            return False
    
    def _create_indexes(self):
        """创建数据库索引"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reasoning_rules_type
                ON reasoning_rules(rule_type)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reasoning_paths_created
                ON reasoning_paths(created_at)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reasoning_steps_path
                ON reasoning_steps(path_id)
            """))
            
            conn.commit()
    
    def add_rule(self, rule_id: str, name: str, rule_type: str,
                 condition: Dict[str, Any], conclusion: Dict[str, Any],
                 confidence: int = 80, priority: int = 0) -> bool:
        """添加推理规则"""
        try:
            session = self.Session()
            rule = ReasoningRule(
                rule_id=rule_id,
                name=name,
                rule_type=rule_type,
                condition=condition,
                conclusion=conclusion,
                confidence=confidence,
                priority=priority
            )
            session.add(rule)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"添加规则失败: {e}")
            return False
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        try:
            session = self.Session()
            rules = session.query(ReasoningRule).all()
            session.close()
            
            return [{
                'rule_id': r.rule_id,
                'name': r.name,
                'rule_type': r.rule_type,
                'condition': r.condition,
                'conclusion': r.conclusion,
                'confidence': r.confidence,
                'priority': r.priority
            } for r in rules]
        except SQLAlchemyError as e:
            print(f"获取规则失败: {e}")
            return []
    
    def save_reasoning_path(self, path_id: str, query: str, result: Dict[str, Any],
                           steps: List[Dict[str, Any]], rules_applied: List[str],
                           confidence: int) -> bool:
        """保存推理路径"""
        try:
            session = self.Session()
            path = ReasoningPath(
                path_id=path_id,
                query=query,
                result=result,
                steps=steps,
                rules_applied=rules_applied,
                confidence=confidence
            )
            session.add(path)
            
            # 保存推理步骤
            for i, step in enumerate(steps):
                step_record = ReasoningStep(
                    path_id=path_id,
                    step_number=i + 1,
                    step_type=step.get('type', 'inference'),
                    input_data=step.get('input'),
                    output_data=step.get('output'),
                    rule_id=step.get('rule_id'),
                    explanation=step.get('explanation')
                )
                session.add(step_record)
            
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"保存推理路径失败: {e}")
            return False
    
    def get_reasoning_path(self, path_id: str) -> Optional[Dict[str, Any]]:
        """获取推理路径"""
        try:
            session = self.Session()
            path = session.query(ReasoningPath).filter(
                ReasoningPath.path_id == path_id
            ).first()
            
            if path:
                result = {
                    'path_id': path.path_id,
                    'query': path.query,
                    'result': path.result,
                    'steps': path.steps,
                    'rules_applied': path.rules_applied,
                    'confidence': path.confidence
                }
                session.close()
                return result
            session.close()
            return None
        except SQLAlchemyError as e:
            print(f"获取推理路径失败: {e}")
            return None
