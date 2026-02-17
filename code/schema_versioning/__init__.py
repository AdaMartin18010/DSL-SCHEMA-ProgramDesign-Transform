"""
Schema版本管理模块

提供版本控制、演化追踪、兼容性检查和迁移工具支持
"""

from .storage import SchemaVersioningStorage
from .version_control import SchemaVersionControl
from .evolution_tracker import SchemaEvolutionTracker
from .compatibility import CompatibilityChecker
from .migration import SchemaMigrationTool
from .models import (
    SchemaVersion,
    SchemaMigration,
    SchemaEvolution,
    CompatibilityCheck
)

# 便捷别名
SchemaVersionManager = SchemaVersionControl

__all__ = [
    'SchemaVersioningStorage',
    'SchemaVersionControl',
    'SchemaVersionManager',
    'SchemaEvolutionTracker',
    'CompatibilityChecker',
    'SchemaMigrationTool',
    'SchemaVersion',
    'SchemaMigration',
    'SchemaEvolution',
    'CompatibilityCheck',
]
