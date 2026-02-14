"""
Schema增量转换算法模块

提供Schema增量转换、变更检测和依赖分析功能
"""

from .change_detector import ChangeDetector, SchemaChange, ChangeType
from .dependency_analyzer import DependencyAnalyzer, DependencyGraph, DependencyNode
from .incremental_transformer import IncrementalTransformer, TransformationResult, TransformationStrategy

__all__ = [
    # 变更检测
    'ChangeDetector',
    'SchemaChange',
    'ChangeType',
    # 依赖分析
    'DependencyAnalyzer',
    'DependencyGraph',
    'DependencyNode',
    # 增量转换
    'IncrementalTransformer',
    'TransformationResult',
    'TransformationStrategy',
]
