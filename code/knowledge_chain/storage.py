"""
知识链PostgreSQL存储实现

实现数据库连接、存储和查询功能
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import os
from .models import Base, KnowledgeNode, KnowledgeChain, ChainLink


class KnowledgeChainStorage:
    """知识链存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
        """
        if database_url is None:
            database_url = os.getenv(
                'KNOWLEDGE_CHAIN_DB_URL',
                'postgresql://user:password@localhost:5432/knowledge_chain'
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
                CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_level
                ON knowledge_nodes(level)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chain_links_chain
                ON chain_links(chain_id)
            """))
            
            conn.commit()
    
    def add_node(self, node_id: str, name: str, level: int,
                node_type: str, content: Optional[Dict[str, Any]] = None,
                properties: Optional[Dict[str, Any]] = None) -> bool:
        """添加知识节点"""
        try:
            session = self.Session()
            node = KnowledgeNode(
                node_id=node_id,
                name=name,
                level=level,
                node_type=node_type,
                content=content or {},
                properties=properties or {}
            )
            session.add(node)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"添加节点失败: {e}")
            return False
    
    def create_chain(self, chain_id: str, name: str, node_ids: List[str],
                    abstraction_functions: Optional[List[str]] = None) -> bool:
        """创建知识链"""
        try:
            session = self.Session()
            chain = KnowledgeChain(
                chain_id=chain_id,
                name=name,
                node_ids=node_ids,
                abstraction_functions=abstraction_functions or []
            )
            session.add(chain)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"创建知识链失败: {e}")
            return False
    
    def get_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """获取知识链"""
        try:
            session = self.Session()
            chain = session.query(KnowledgeChain).filter(
                KnowledgeChain.chain_id == chain_id
            ).first()
            
            if chain:
                result = {
                    'chain_id': chain.chain_id,
                    'name': chain.name,
                    'node_ids': chain.node_ids,
                    'abstraction_functions': chain.abstraction_functions
                }
                session.close()
                return result
            session.close()
            return None
        except SQLAlchemyError as e:
            print(f"获取知识链失败: {e}")
            return None
    
    def get_nodes_by_level(self, level: int) -> List[Dict[str, Any]]:
        """获取指定层次的所有节点"""
        try:
            session = self.Session()
            nodes = session.query(KnowledgeNode).filter(
                KnowledgeNode.level == level
            ).all()
            
            session.close()
            
            return [{
                'node_id': n.node_id,
                'name': n.name,
                'level': n.level,
                'node_type': n.node_type,
                'content': n.content,
                'properties': n.properties
            } for n in nodes]
        except SQLAlchemyError as e:
            print(f"查询节点失败: {e}")
            return []
