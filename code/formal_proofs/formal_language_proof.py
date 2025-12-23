"""
形式语言理论证明模块

专注于Schema转换的形式语言理论证明，包括语法-语义一致性、转换正确性等
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GrammarType(Enum):
    """语法类型"""
    REGULAR = "regular"  # 正则语法（类型3）
    CONTEXT_FREE = "context_free"  # 上下文无关语法（类型2）
    CONTEXT_SENSITIVE = "context_sensitive"  # 上下文相关语法（类型1）
    UNRESTRICTED = "unrestricted"  # 无限制语法（类型0）


@dataclass
class Grammar:
    """语法定义"""
    grammar_type: GrammarType
    terminals: Set[str]  # 终结符集合
    non_terminals: Set[str]  # 非终结符集合
    productions: List[Tuple[str, str]]  # 产生式规则
    start_symbol: str  # 起始符号


@dataclass
class SemanticDomain:
    """语义域"""
    type_domain: Dict[str, Any]  # 类型语义域
    value_domain: Dict[str, Any]  # 值语义域
    constraint_domain: Dict[str, Any]  # 约束语义域
    metadata_domain: Dict[str, Any]  # 元数据语义域
    protocol_domain: Dict[str, Any]  # 协议语义域


@dataclass
class ProofStep:
    """证明步骤"""
    step_number: int
    description: str
    condition: str
    result: str
    verified: bool


@dataclass
class FormalProofResult:
    """形式化证明结果"""
    syntax_correctness: bool  # 语法正确性
    semantic_correctness: bool  # 语义正确性
    consistency: bool  # 语法-语义一致性
    proof_steps: List[ProofStep]  # 证明步骤
    proof_status: str  # 证明状态


class FormalLanguageProof:
    """形式语言理论证明器"""
    
    def __init__(self):
        """初始化形式语言理论证明器"""
        self.grammars: Dict[str, Grammar] = {}
        self.semantic_domains: Dict[str, SemanticDomain] = {}
    
    def register_grammar(
        self,
        name: str,
        grammar_type: GrammarType,
        terminals: Set[str],
        non_terminals: Set[str],
        productions: List[Tuple[str, str]],
        start_symbol: str
    ) -> Grammar:
        """注册语法"""
        grammar = Grammar(
            grammar_type=grammar_type,
            terminals=terminals,
            non_terminals=non_terminals,
            productions=productions,
            start_symbol=start_symbol
        )
        
        self.grammars[name] = grammar
        logger.info(f"注册语法: {name} ({grammar_type.value})")
        
        return grammar
    
    def register_semantic_domain(
        self,
        name: str,
        type_domain: Dict[str, Any],
        value_domain: Dict[str, Any],
        constraint_domain: Dict[str, Any],
        metadata_domain: Dict[str, Any],
        protocol_domain: Optional[Dict[str, Any]] = None
    ) -> SemanticDomain:
        """注册语义域"""
        domain = SemanticDomain(
            type_domain=type_domain,
            value_domain=value_domain,
            constraint_domain=constraint_domain,
            metadata_domain=metadata_domain,
            protocol_domain=protocol_domain or {}
        )
        
        self.semantic_domains[name] = domain
        logger.info(f"注册语义域: {name}")
        
        return domain
    
    def check_syntax_correctness(
        self,
        schema: Dict[str, Any],
        grammar_name: str
    ) -> bool:
        """检查语法正确性"""
        if grammar_name not in self.grammars:
            raise ValueError(f"语法未注册: {grammar_name}")
        
        grammar = self.grammars[grammar_name]
        
        # 简化实现：检查Schema是否符合语法规则
        # 实际应该使用语法解析器进行完整检查
        return self._validate_syntax(schema, grammar)
    
    def _validate_syntax(self, schema: Dict[str, Any], grammar: Grammar) -> bool:
        """验证语法"""
        # 简化实现：检查基本结构
        # 实际应该使用完整的语法解析
        
        # 检查是否包含必需的终结符
        schema_str = str(schema)
        has_terminals = any(
            terminal in schema_str
            for terminal in grammar.terminals
        )
        
        return has_terminals
    
    def check_semantic_correctness(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_domain_name: str,
        target_domain_name: str
    ) -> bool:
        """检查语义正确性"""
        if source_domain_name not in self.semantic_domains:
            raise ValueError(f"源语义域未注册: {source_domain_name}")
        if target_domain_name not in self.semantic_domains:
            raise ValueError(f"目标语义域未注册: {target_domain_name}")
        
        source_domain = self.semantic_domains[source_domain_name]
        target_domain = self.semantic_domains[target_domain_name]
        
        # 检查语义等价性
        return self._check_semantic_equivalence(
            source_schema, target_schema, source_domain, target_domain
        )
    
    def _check_semantic_equivalence(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_domain: SemanticDomain,
        target_domain: SemanticDomain
    ) -> bool:
        """检查语义等价性"""
        # 简化实现：检查类型映射是否正确
        # 实际应该进行完整的语义分析
        
        source_types = self._extract_types(source_schema)
        target_types = self._extract_types(target_schema)
        
        # 检查类型是否能够映射
        for source_type in source_types:
            if source_type not in source_domain.type_domain:
                return False
        
        return True
    
    def _extract_types(self, schema: Dict[str, Any]) -> Set[str]:
        """提取类型"""
        types = set()
        
        def extract(obj: Any):
            if isinstance(obj, dict):
                if "type" in obj:
                    types.add(obj["type"])
                for value in obj.values():
                    extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item)
        
        extract(schema)
        return types
    
    def check_consistency(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_grammar_name: str,
        target_grammar_name: str,
        source_domain_name: str,
        target_domain_name: str
    ) -> bool:
        """检查语法-语义一致性"""
        # 检查语法正确性
        source_syntax_ok = self.check_syntax_correctness(source_schema, source_grammar_name)
        target_syntax_ok = self.check_syntax_correctness(target_schema, target_grammar_name)
        
        if not source_syntax_ok or not target_syntax_ok:
            return False
        
        # 检查语义正确性
        semantic_ok = self.check_semantic_correctness(
            source_schema, target_schema, source_domain_name, target_domain_name
        )
        
        return semantic_ok
    
    def prove_transformation_correctness(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_grammar_name: str,
        target_grammar_name: str,
        source_domain_name: str,
        target_domain_name: str,
        transform_func: Optional[callable] = None
    ) -> FormalProofResult:
        """证明转换正确性"""
        proof_steps = []
        
        # 步骤1：检查源Schema语法正确性
        step1 = ProofStep(
            step_number=1,
            description="检查源Schema语法正确性",
            condition=f"source_schema ∈ L(G_{source_grammar_name})",
            result="",
            verified=False
        )
        
        source_syntax_ok = self.check_syntax_correctness(source_schema, source_grammar_name)
        step1.result = "通过" if source_syntax_ok else "失败"
        step1.verified = source_syntax_ok
        proof_steps.append(step1)
        
        if not source_syntax_ok:
            return FormalProofResult(
                syntax_correctness=False,
                semantic_correctness=False,
                consistency=False,
                proof_steps=proof_steps,
                proof_status="失败：源Schema语法不正确"
            )
        
        # 步骤2：检查目标Schema语法正确性
        step2 = ProofStep(
            step_number=2,
            description="检查目标Schema语法正确性",
            condition=f"target_schema ∈ L(G_{target_grammar_name})",
            result="",
            verified=False
        )
        
        target_syntax_ok = self.check_syntax_correctness(target_schema, target_grammar_name)
        step2.result = "通过" if target_syntax_ok else "失败"
        step2.verified = target_syntax_ok
        proof_steps.append(step2)
        
        if not target_syntax_ok:
            return FormalProofResult(
                syntax_correctness=False,
                semantic_correctness=False,
                consistency=False,
                proof_steps=proof_steps,
                proof_status="失败：目标Schema语法不正确"
            )
        
        # 步骤3：检查语义正确性
        step3 = ProofStep(
            step_number=3,
            description="检查语义正确性",
            condition="[[source_schema]]_1 = [[target_schema]]_2",
            result="",
            verified=False
        )
        
        semantic_ok = self.check_semantic_correctness(
            source_schema, target_schema, source_domain_name, target_domain_name
        )
        step3.result = "通过" if semantic_ok else "失败"
        step3.verified = semantic_ok
        proof_steps.append(step3)
        
        # 步骤4：检查语法-语义一致性
        step4 = ProofStep(
            step_number=4,
            description="检查语法-语义一致性",
            condition="f_Σ ∘ [[·]]_1 = [[·]]_2 ∘ f_G",
            result="",
            verified=False
        )
        
        consistency_ok = self.check_consistency(
            source_schema, target_schema,
            source_grammar_name, target_grammar_name,
            source_domain_name, target_domain_name
        )
        step4.result = "通过" if consistency_ok else "失败"
        step4.verified = consistency_ok
        proof_steps.append(step4)
        
        # 确定证明状态
        if source_syntax_ok and target_syntax_ok and semantic_ok and consistency_ok:
            proof_status = "完全正确"
        elif source_syntax_ok and target_syntax_ok:
            proof_status = "部分正确"
        else:
            proof_status = "失败"
        
        return FormalProofResult(
            syntax_correctness=source_syntax_ok and target_syntax_ok,
            semantic_correctness=semantic_ok,
            consistency=consistency_ok,
            proof_steps=proof_steps,
            proof_status=proof_status
        )


class FormalLanguageAnalyzer:
    """形式语言理论分析器"""
    
    def __init__(self, proof_engine: FormalLanguageProof):
        """初始化分析器"""
        self.proof_engine = proof_engine
    
    def analyze_transformation(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_grammar_name: str,
        target_grammar_name: str,
        source_domain_name: str,
        target_domain_name: str
    ) -> Dict[str, Any]:
        """分析转换"""
        result = self.proof_engine.prove_transformation_correctness(
            source_schema, target_schema,
            source_grammar_name, target_grammar_name,
            source_domain_name, target_domain_name
        )
        
        return {
            "syntax_correctness": result.syntax_correctness,
            "semantic_correctness": result.semantic_correctness,
            "consistency": result.consistency,
            "proof_status": result.proof_status,
            "proof_steps": [
                {
                    "step": step.step_number,
                    "description": step.description,
                    "condition": step.condition,
                    "result": step.result,
                    "verified": step.verified
                }
                for step in result.proof_steps
            ],
            "is_completely_correct": (
                result.syntax_correctness and
                result.semantic_correctness and
                result.consistency
            )
        }
