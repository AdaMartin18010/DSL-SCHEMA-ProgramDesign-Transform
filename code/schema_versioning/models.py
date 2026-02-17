"""
Schema版本管理数据模型

基于SQLAlchemy ORM定义数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class SchemaVersion(Base):
    """Schema版本表"""
    __tablename__ = 'schema_versions'
    
    id = Column(Integer, primary_key=True)
    schema_id = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)  # 版本号（如：1.0.0）
    schema_content = Column(JSON, nullable=False)  # Schema内容
    changelog = Column(Text)  # 变更日志
    is_current = Column(Integer, default=0)  # 是否为当前版本（0或1）
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(100))
    
    # 关系
    migrations = relationship("SchemaMigration", back_populates="from_version")
    evolutions = relationship("SchemaEvolution", back_populates="version")


class SchemaMigration(Base):
    """Schema迁移表"""
    __tablename__ = 'schema_migrations'
    
    id = Column(Integer, primary_key=True)
    migration_id = Column(String(50), unique=True, nullable=False)
    schema_id = Column(String(50), nullable=False)
    from_version = Column(String(50), ForeignKey('schema_versions.version'))
    to_version = Column(String(50), nullable=False)
    migration_script = Column(Text)  # 迁移脚本
    migration_type = Column(String(50))  # 'forward', 'backward', 'bidirectional'
    is_automatic = Column(Integer, default=0)  # 是否自动迁移
    status = Column(String(50))  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.now)


class SchemaEvolution(Base):
    """Schema演化表"""
    __tablename__ = 'schema_evolutions'
    
    id = Column(Integer, primary_key=True)
    evolution_id = Column(String(50), unique=True, nullable=False)
    schema_id = Column(String(50), nullable=False)
    version = Column(String(50), ForeignKey('schema_versions.version'))
    change_type = Column(String(50))  # 'added', 'modified', 'removed', 'deprecated'
    change_description = Column(Text)
    affected_fields = Column(JSON)  # 受影响的字段列表
    breaking_change = Column(Integer, default=0)  # 是否破坏性变更
    created_at = Column(DateTime, default=datetime.now)


class CompatibilityCheck(Base):
    """兼容性检查表"""
    __tablename__ = 'compatibility_checks'
    
    id = Column(Integer, primary_key=True)
    check_id = Column(String(50), unique=True, nullable=False)
    schema_id = Column(String(50), nullable=False)
    from_version = Column(String(50), nullable=False)
    to_version = Column(String(50), nullable=False)
    is_compatible = Column(Integer)  # 0:不兼容, 1:兼容, 2:部分兼容
    compatibility_report = Column(JSON)  # 兼容性报告
    breaking_changes = Column(JSON)  # 破坏性变更列表
    created_at = Column(DateTime, default=datetime.now)
