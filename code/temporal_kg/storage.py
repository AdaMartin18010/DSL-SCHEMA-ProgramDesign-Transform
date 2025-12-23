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
    
    def get_entities_in_time_range(
        self,
        entity_ids: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        获取时间区间内的实体
        
        Args:
            entity_ids: 实体ID列表（可选）
            entity_types: 实体类型列表（可选）
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            实体列表
        """
        try:
            session = self.Session()
            query = session.query(TemporalEntity)
            
            # 时间范围过滤
            if start_time and end_time:
                # 查询在时间区间内有重叠的实体
                query = query.filter(
                    and_(
                        TemporalEntity.valid_from <= end_time,
                        or_(
                            TemporalEntity.valid_to >= start_time,
                            TemporalEntity.valid_to.is_(None)
                        )
                    )
                )
            elif start_time:
                query = query.filter(
                    or_(
                        TemporalEntity.valid_to >= start_time,
                        TemporalEntity.valid_to.is_(None)
                    )
                )
            elif end_time:
                query = query.filter(
                    TemporalEntity.valid_from <= end_time
                )
            
            # 实体ID过滤
            if entity_ids:
                query = query.filter(TemporalEntity.entity_id.in_(entity_ids))
            
            # 实体类型过滤
            if entity_types:
                query = query.filter(TemporalEntity.entity_type.in_(entity_types))
            
            entities = query.all()
            session.close()
            
            return [
                {
                    'entity_id': entity.entity_id,
                    'entity_type': entity.entity_type,
                    'properties': entity.properties,
                    'valid_from': entity.valid_from,
                    'valid_to': entity.valid_to
                }
                for entity in entities
            ]
        except SQLAlchemyError as e:
            print(f"时间区间查询失败: {e}")
            return []
    
    def get_relations_in_time_range(
        self,
        source_entity_id: Optional[str] = None,
        target_entity_id: Optional[str] = None,
        relation_type: Optional[str] = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        获取时间区间内的关系
        
        Args:
            source_entity_id: 源实体ID（可选）
            target_entity_id: 目标实体ID（可选）
            relation_type: 关系类型（可选）
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            关系列表
        """
        try:
            session = self.Session()
            query = session.query(TemporalRelation)
            
            # 时间范围过滤
            if start_time and end_time:
                query = query.filter(
                    and_(
                        TemporalRelation.valid_from <= end_time,
                        or_(
                            TemporalRelation.valid_to >= start_time,
                            TemporalRelation.valid_to.is_(None)
                        )
                    )
                )
            elif start_time:
                query = query.filter(
                    or_(
                        TemporalRelation.valid_to >= start_time,
                        TemporalRelation.valid_to.is_(None)
                    )
                )
            elif end_time:
                query = query.filter(
                    TemporalRelation.valid_from <= end_time
                )
            
            # 源实体过滤
            if source_entity_id:
                query = query.filter(TemporalRelation.source_entity_id == source_entity_id)
            
            # 目标实体过滤
            if target_entity_id:
                query = query.filter(TemporalRelation.target_entity_id == target_entity_id)
            
            # 关系类型过滤
            if relation_type:
                query = query.filter(TemporalRelation.relation_type == relation_type)
            
            relations = query.all()
            session.close()
            
            return [
                {
                    'source_entity_id': relation.source_entity_id,
                    'target_entity_id': relation.target_entity_id,
                    'relation_type': relation.relation_type,
                    'properties': relation.properties,
                    'valid_from': relation.valid_from,
                    'valid_to': relation.valid_to
                }
                for relation in relations
            ]
        except SQLAlchemyError as e:
            print(f"时间区间关系查询失败: {e}")
            return []
