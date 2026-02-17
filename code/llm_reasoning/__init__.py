"""
LLM推理引擎模块

提供大语言模型集成和知识推理支持
"""

from .llm_interface import (
    LLMInterface,
    OpenAILLM,
    AnthropicLLM,
    ReasoningResult
)
from .embedding import KGEmbedding, EmbeddingStore
from .chain_builder import ReasoningChainBuilder, ReasoningStep
from .validator import ResultValidator, ValidationResult

# 便捷别名
LLMReasoningEngine = LLMInterface

__all__ = [
    'LLMInterface',
    'LLMReasoningEngine',
    'OpenAILLM',
    'AnthropicLLM',
    'ReasoningResult',
    'KGEmbedding',
    'EmbeddingStore',
    'ReasoningChainBuilder',
    'ReasoningStep',
    'ResultValidator',
    'ValidationResult',
]
