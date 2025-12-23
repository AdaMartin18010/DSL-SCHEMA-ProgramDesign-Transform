"""
综合整合模块

提供多维度整合、跨行业转换、AI驱动转换等功能
"""

from .comprehensive_integration_framework import (
    ComprehensiveIntegrationFramework,
    AnalysisDimension,
    IntegrationLevel,
    IntegrationResult,
    KnowledgeMatrix
)

# 导入知识发现模块
try:
    from .knowledge_discovery import (
        KnowledgeDiscoveryEngine,
        PatternRecognizer,
        RelationshipReasoner,
        OptimizationAdvisor,
        PatternType,
        RelationshipType,
        Pattern,
        Relationship,
        OptimizationRecommendation
    )
except ImportError:
    # 如果模块不存在，使用占位符
    KnowledgeDiscoveryEngine = None
    PatternRecognizer = None
    RelationshipReasoner = None
    OptimizationAdvisor = None
    PatternType = None
    RelationshipType = None
    Pattern = None
    Relationship = None
    OptimizationRecommendation = None
from .industry_adapter_framework import (
    IndustryAdapterFramework,
    IndustryType,
    SchemaFormat,
    IndustryAdapter,
    ConversionRule
)
from .ai_driven_transformation import (
    AIDrivenTransformation,
    AIModel,
    PromptStrategy,
    TransformationRequest,
    TransformationResult,
    PromptTemplate
)
from .comprehensive_analyzer import (
    ComprehensiveAnalyzer,
    ComprehensiveReport
)

__all__ = [
    # 综合整合框架
    'ComprehensiveIntegrationFramework',
    'AnalysisDimension',
    'IntegrationLevel',
    'IntegrationResult',
    'KnowledgeMatrix',
    # 行业适配器框架
    'IndustryAdapterFramework',
    'IndustryType',
    'SchemaFormat',
    'IndustryAdapter',
    'ConversionRule',
    # AI驱动转换
    'AIDrivenTransformation',
    'AIModel',
    'PromptStrategy',
    'TransformationRequest',
    'TransformationResult',
    'PromptTemplate',
    # 综合分析器
    'ComprehensiveAnalyzer',
    'ComprehensiveReport'
]
