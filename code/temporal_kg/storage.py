"""
时序知识图谱PostgreSQL存储实现

实现时间戳存储、演化追踪和查询功能
"""

from sqlalchemy import create_engine, and_, or_, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from .models import Base, TemporalEntity, TemporalRelation, EntitySnapshot


class TemporalKGStorage:
    """时序知识图谱存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
        """
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://user:password@localhost:5432/temporal_kg'
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
                CREATE INDEX IF NOT EXISTS idx_temporal_entities_time
                ON temporal_entities(valid_from, valid_to)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_temporal_entities_entity_time
                ON temporal_entities(entity_id, valid_from)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_temporal_relations_time
                ON temporal_relations(valid_from, valid_to)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_entity_snapshots_time
                ON entity_snapshots(entity_id, snapshot_time)
            """))
            
            conn.commit()
    
    def add_entity(self, entity_id: str, entity_type: str,
                   valid_from: datetime, valid_to: Optional[datetime] = None,
                   properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加时序实体
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型
            valid_from: 有效开始时间
            valid_to: 有效结束时间（None表示持续有效）
            properties: 属性字典
            
        Returns:
            是否成功
        """
        try:
            session = self.Session()
            entity = TemporalEntity(
                entity_id=entity_id,
                entity_type=entity_type,
                valid_from=valid_from,
                valid_to=valid_to,
                properties=properties or {}
            )
            session.add(entity)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"添加实体失败: {e}")
            return False
    
    def update_entity(self, entity_id: str, new_properties: Dict[str, Any],
                     update_time: datetime) -> bool:
        """
        更新实体（创建新版本）
        
        Args:
            entity_id: 实体ID
            new_properties: 新属性
            update_time: 更新时间
            
        Returns:
            是否成功
        """
        try:
            session = self.Session()
            
            # 结束旧版本
            old_entity = session.query(TemporalEntity).filter(
                and_(
                    TemporalEntity.entity_id == entity_id,
                    TemporalEntity.valid_to.is_(None)
                )
            ).first()
            
            if old_entity:
                old_entity.valid_to = update_time
            
            # 创建新版本
            new_entity = TemporalEntity(
                entity_id=entity_id,
                entity_type=old_entity.entity_type if old_entity else None,
                valid_from=update_time,
                valid_to=None,
                properties=new_properties
            )
            session.add(new_entity)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"更新实体失败: {e}")
            return False
    
    def get_entity_at_time(self, entity_id: str, query_time: datetime) -> Optional[Dict[str, Any]]:
        """
        获取时间点的实体状态
        
        Args:
            entity_id: 实体ID
            query_time: 查询时间
            
        Returns:
            实体信息（如果存在）
        """
        try:
            session = self.Session()
            entity = session.query(TemporalEntity).filter(
                and_(
                    TemporalEntity.entity_id == entity_id,
                    TemporalEntity.valid_from <= query_time,
                    or_(
                        TemporalEntity.valid_to >= query_time,
                        TemporalEntity.valid_to.is_(None)
                    )
                )
            ).first()
            
            session.close()
            
            if entity:
                return {
                    'entity_id': entity.entity_id,
                    'entity_type': entity.entity_type,
                    'properties': entity.properties,
                    'valid_from': entity.valid_from,
                    'valid_to': entity.valid_to
                }
            return None
        except SQLAlchemyError as e:
            print(f"查询实体失败: {e}")
            return None
