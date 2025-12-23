"""
形式化证明模块

提供信息论证明、形式语言理论证明和整合证明框架
"""

from .information_theory_proof import (
    InformationTheoryProof,
    InformationTheoryAnalyzer,
    EntropyWeights,
    InformationLoss,
    ProofResult
)
from .formal_language_proof import (
    FormalLanguageProof,
    FormalLanguageAnalyzer,
    Grammar,
    GrammarType,
    SemanticDomain,
    FormalProofResult
)
from .integrated_proof_framework import (
    IntegratedProofFramework,
    ProofFrameworkAnalyzer,
    ProofMethod,
    IntegratedProofResult
)
from .proof_validator import (
    ProofValidator,
    ValidationReport
)

__all__ = [
    # 信息论证明
    'InformationTheoryProof',
    'InformationTheoryAnalyzer',
    'EntropyWeights',
    'InformationLoss',
    'ProofResult',
    # 形式语言理论证明
    'FormalLanguageProof',
    'FormalLanguageAnalyzer',
    'Grammar',
    'GrammarType',
    'SemanticDomain',
    'FormalProofResult',
    # 整合证明框架
    'IntegratedProofFramework',
    'ProofFrameworkAnalyzer',
    'ProofMethod',
    'IntegratedProofResult',
    # 证明验证器
    'ProofValidator',
    'ValidationReport'
]
