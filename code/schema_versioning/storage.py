"""
Schema版本管理PostgreSQL存储实现

实现数据库连接、存储和查询功能
"""

from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import os
from .models import Base, SchemaVersion, SchemaMigration, SchemaEvolution, CompatibilityCheck


class SchemaVersioningStorage:
    """Schema版本管理存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
        """
        if database_url is None:
            database_url = os.getenv(
                'SCHEMA_VERSIONING_DB_URL',
                'postgresql://user:password@localhost:5432/schema_versioning'
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
                CREATE INDEX IF NOT EXISTS idx_schema_versions_schema
                ON schema_versions(schema_id, version)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_schema_versions_current
                ON schema_versions(schema_id, is_current)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_schema_migrations_schema
                ON schema_migrations(schema_id)
            """))
            
            conn.commit()
    
    def create_version(self, schema_id: str, version: str,
                      schema_content: Dict[str, Any],
                      changelog: Optional[str] = None,
                      created_by: Optional[str] = None) -> bool:
        """创建Schema版本"""
        try:
            session = self.Session()
            
            # 如果这是新版本，将旧版本标记为非当前版本
            if version:
                old_versions = session.query(SchemaVersion).filter(
                    and_(
                        SchemaVersion.schema_id == schema_id,
                        SchemaVersion.is_current == 1
                    )
                ).all()
                for old_version in old_versions:
                    old_version.is_current = 0
            
            version_obj = SchemaVersion(
                schema_id=schema_id,
                version=version,
                schema_content=schema_content,
                changelog=changelog,
                is_current=1,
                created_by=created_by
            )
            session.add(version_obj)
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            print(f"创建版本失败: {e}")
            return False
    
    def get_current_version(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """获取当前版本"""
        try:
            session = self.Session()
            version = session.query(SchemaVersion).filter(
                and_(
                    SchemaVersion.schema_id == schema_id,
                    SchemaVersion.is_current == 1
                )
            ).first()
            
            if version:
                result = {
                    'schema_id': version.schema_id,
                    'version': version.version,
                    'schema_content': version.schema_content,
                    'changelog': version.changelog,
                    'created_at': version.created_at.isoformat()
                }
                session.close()
                return result
            session.close()
            return None
        except SQLAlchemyError as e:
            print(f"获取当前版本失败: {e}")
            return None
    
    def get_version_history(self, schema_id: str) -> List[Dict[str, Any]]:
        """获取版本历史"""
        try:
            session = self.Session()
            versions = session.query(SchemaVersion).filter(
                SchemaVersion.schema_id == schema_id
            ).order_by(SchemaVersion.created_at.desc()).all()
            
            session.close()
            
            return [{
                'schema_id': v.schema_id,
                'version': v.version,
                'is_current': bool(v.is_current),
                'created_at': v.created_at.isoformat(),
                'created_by': v.created_by
            } for v in versions]
        except SQLAlchemyError as e:
            print(f"获取版本历史失败: {e}")
            return []
