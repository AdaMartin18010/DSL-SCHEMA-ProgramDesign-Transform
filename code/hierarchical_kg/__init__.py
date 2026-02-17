"""
层次化知识表示模块

提供知识金字塔结构和层次化推理支持
"""

from .storage import HierarchicalKGStorage
from .abstraction import KnowledgeAbstraction
from .reasoning import HierarchicalReasoning
from .query import HierarchicalQuery
from .models import (
    HierarchicalEntity,
    AbstractionRelation
)

# 便捷别名
HierarchicalKG = HierarchicalKGStorage

__all__ = [
    'HierarchicalKGStorage',
    'HierarchicalKG',
    'KnowledgeAbstraction',
    'HierarchicalReasoning',
    'HierarchicalQuery',
    'HierarchicalEntity',
    'AbstractionRelation',
]
