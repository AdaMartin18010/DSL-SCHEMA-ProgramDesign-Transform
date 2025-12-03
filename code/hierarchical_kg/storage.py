"""
层次化知识表示PostgreSQL存储实现

实现数据库连接、存储和查询功能
"""

from sqlalchemy import create_engine, and_, or_, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import os
from .models import Base, HierarchicalEntity, AbstractionRelation


class HierarchicalKGStorage:
    """层次化知识图谱存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
        """
        if database_url is None:
            database_url = os.getenv(
                'HIERARCHICAL_DB_URL',
                'postgresql://user:password@localhost:5432/hierarchical_kg'
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
                CREATE INDEX IF NOT EXISTS idx_hierarchical_entities_level
                ON hierarchical_entities(level)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_hierarchical_entities_abstraction
                ON hierarchical_entities(abstraction_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_abstraction_relations_source
                ON abstraction_relations(source_entity_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_abstraction_relations_target
                ON abstraction_relations(target_entity_id)
            """))
            
            conn.commit()
    
    def add_entity(self, entity_id: str, name: str, level: int,
                   abstraction_id: Optional[str] = None,
                   content: Optional[Dict[str, Any]] = None,
                   properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加层次化实体
        
        Args:
            entity_id: 实体ID
            name: 实体名称
            level: 层次（1、2、3）
            abstraction_id: 抽象实体ID
            content: 知识内容
            properties: 属性
            
        Returns:
            是否成功
        """
        try:
            session = self.Session()
            entity = HierarchicalEntity(
                entity_id=entity_id,
                name=name,
                level=level,
                abstraction_id=abstraction_id,
                content=content or {},
                properties=properties or {}
            )
            session.add(entity)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"添加实体失败: {e}")
            return False
    
    def get_entities_by_level(self, level: int) -> List[Dict[str, Any]]:
        """
        获取指定层次的所有实体
        
        Args:
            level: 层次（1、2、3）
            
        Returns:
            实体列表
        """
        try:
            session = self.Session()
            entities = session.query(HierarchicalEntity).filter(
                HierarchicalEntity.level == level
            ).all()
            
            session.close()
            
            return [{
                'entity_id': e.entity_id,
                'name': e.name,
                'level': e.level,
                'abstraction_id': e.abstraction_id,
                'content': e.content,
                'properties': e.properties
            } for e in entities]
        except SQLAlchemyError as e:
            print(f"查询实体失败: {e}")
            return []
    
    def get_abstraction_chain(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        获取抽象链（从低层到高层）
        
        Args:
            entity_id: 实体ID
            
        Returns:
            抽象链列表
        """
        try:
            session = self.Session()
            chain = []
            current_id = entity_id
            
            while current_id:
                entity = session.query(HierarchicalEntity).filter(
                    HierarchicalEntity.entity_id == current_id
                ).first()
                
                if not entity:
                    break
                
                chain.append({
                    'entity_id': entity.entity_id,
                    'name': entity.name,
                    'level': entity.level,
                    'content': entity.content,
                    'properties': entity.properties
                })
                
                current_id = entity.abstraction_id
            
            session.close()
            return chain
        except SQLAlchemyError as e:
            print(f"获取抽象链失败: {e}")
            return []
    
    def get_concretization_chain(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        获取具体化链（从高层到低层）
        
        Args:
            entity_id: 实体ID
            
        Returns:
            具体化链列表
        """
        try:
            session = self.Session()
            chain = []
            current_id = entity_id
            
            while current_id:
                entity = session.query(HierarchicalEntity).filter(
                    HierarchicalEntity.entity_id == current_id
                ).first()
                
                if not entity:
                    break
                
                chain.append({
                    'entity_id': entity.entity_id,
                    'name': entity.name,
                    'level': entity.level,
                    'content': entity.content,
                    'properties': entity.properties
                })
                
                # 获取第一个具体化实体
                if entity.concretizations and len(entity.concretizations) > 0:
                    current_id = entity.concretizations[0]
                else:
                    break
            
            session.close()
            return chain
        except SQLAlchemyError as e:
            print(f"获取具体化链失败: {e}")
            return []
