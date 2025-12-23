"""
整合证明框架

整合信息论证明、形式语言理论证明和传统方法证明
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .information_theory_proof import (
    InformationTheoryProof,
    ProofResult as InfoTheoryProofResult
)
from .formal_language_proof import (
    FormalLanguageProof,
    FormalProofResult
)

logger = logging.getLogger(__name__)


class ProofMethod(Enum):
    """证明方法"""
    INFORMATION_THEORY = "information_theory"  # 信息论证明
    FORMAL_LANGUAGE = "formal_language"  # 形式语言理论证明
    TRADITIONAL = "traditional"  # 传统方法证明


@dataclass
class IntegratedProofResult:
    """整合证明结果"""
    information_theory_result: Optional[InfoTheoryProofResult] = None
    formal_language_result: Optional[FormalProofResult] = None
    traditional_result: Optional[Dict[str, Any]] = None
    
    overall_correctness: float = 0.0
    overall_status: str = ""
    verification_passed: bool = False
    
    proof_summary: Dict[str, Any] = None


class IntegratedProofFramework:
    """整合证明框架"""
    
    def __init__(
        self,
        info_theory_proof: Optional[InformationTheoryProof] = None,
        formal_language_proof: Optional[FormalLanguageProof] = None
    ):
        """初始化整合证明框架"""
        self.info_theory_proof = info_theory_proof or InformationTheoryProof()
        self.formal_language_proof = formal_language_proof or FormalLanguageProof()
    
    def prove_correctness(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        transform_func: Optional[callable] = None,
        source_grammar_name: Optional[str] = None,
        target_grammar_name: Optional[str] = None,
        source_domain_name: Optional[str] = None,
        target_domain_name: Optional[str] = None,
        methods: List[ProofMethod] = None
    ) -> IntegratedProofResult:
        """多维度证明转换正确性"""
        if methods is None:
            methods = list(ProofMethod)
        
        info_theory_result = None
        formal_language_result = None
        traditional_result = None
        
        # 1. 信息论证明
        if ProofMethod.INFORMATION_THEORY in methods:
            try:
                info_theory_result = self.info_theory_proof.prove_transformation_correctness(
                    source_schema, target_schema, transform_func
                )
                logger.info(f"信息论证明完成: {info_theory_result.proof_status}")
            except Exception as e:
                logger.error(f"信息论证明失败: {str(e)}")
        
        # 2. 形式语言理论证明
        if ProofMethod.FORMAL_LANGUAGE in methods:
            if source_grammar_name and target_grammar_name:
                try:
                    formal_language_result = self.formal_language_proof.prove_transformation_correctness(
                        source_schema, target_schema,
                        source_grammar_name, target_grammar_name,
                        source_domain_name or "default",
                        target_domain_name or "default",
                        transform_func
                    )
                    logger.info(f"形式语言理论证明完成: {formal_language_result.proof_status}")
                except Exception as e:
                    logger.error(f"形式语言理论证明失败: {str(e)}")
        
        # 3. 传统方法证明
        if ProofMethod.TRADITIONAL in methods:
            try:
                traditional_result = self._traditional_proof(
                    source_schema, target_schema, transform_func
                )
                logger.info(f"传统方法证明完成")
            except Exception as e:
                logger.error(f"传统方法证明失败: {str(e)}")
        
        # 4. 整合验证
        integrated_result = self._integrate_proofs(
            info_theory_result,
            formal_language_result,
            traditional_result
        )
        
        return integrated_result
    
    def _traditional_proof(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        transform_func: Optional[callable] = None
    ) -> Dict[str, Any]:
        """传统方法证明（结构归纳法）"""
        # 简化实现：检查结构相似性
        source_structure = self._extract_structure(source_schema)
        target_structure = self._extract_structure(target_schema)
        
        # 检查结构相似度
        similarity = self._calculate_structure_similarity(
            source_structure, target_structure
        )
        
        return {
            "method": "structural_induction",
            "structure_similarity": similarity,
            "verified": similarity >= 0.7,
            "status": "通过" if similarity >= 0.7 else "失败"
        }
    
    def _extract_structure(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """提取结构"""
        structure = {
            "keys": set(),
            "types": set(),
            "depth": 0
        }
        
        def traverse(obj: Any, depth: int = 0):
            structure["depth"] = max(structure["depth"], depth)
            
            if isinstance(obj, dict):
                structure["keys"].update(obj.keys())
                for key, value in obj.items():
                    if key == "type" and isinstance(value, str):
                        structure["types"].add(value)
                    traverse(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item, depth + 1)
        
        traverse(schema)
        
        return {
            "keys": list(structure["keys"]),
            "types": list(structure["types"]),
            "depth": structure["depth"]
        }
    
    def _calculate_structure_similarity(
        self,
        source_structure: Dict[str, Any],
        target_structure: Dict[str, Any]
    ) -> float:
        """计算结构相似度"""
        # 计算键集合相似度
        source_keys = set(source_structure["keys"])
        target_keys = set(target_structure["keys"])
        
        if not source_keys and not target_keys:
            return 1.0
        
        key_similarity = (
            len(source_keys & target_keys) /
            len(source_keys | target_keys)
            if (source_keys | target_keys) else 0.0
        )
        
        # 计算类型相似度
        source_types = set(source_structure["types"])
        target_types = set(target_structure["types"])
        
        type_similarity = (
            len(source_types & target_types) /
            len(source_types | target_types)
            if (source_types | target_types) else 0.0
        )
        
        # 综合相似度
        similarity = (key_similarity * 0.6 + type_similarity * 0.4)
        
        return similarity
    
    def _integrate_proofs(
        self,
        info_theory_result: Optional[InfoTheoryProofResult],
        formal_language_result: Optional[FormalProofResult],
        traditional_result: Optional[Dict[str, Any]]
    ) -> IntegratedProofResult:
        """整合证明结果"""
        correctness_scores = []
        verification_flags = []
        
        # 信息论证明结果
        if info_theory_result:
            correctness_scores.append(info_theory_result.correctness)
            verification_flags.append(
                info_theory_result.correctness >= 0.9 or info_theory_result.is_lossless
            )
        
        # 形式语言理论证明结果
        if formal_language_result:
            if formal_language_result.syntax_correctness and \
               formal_language_result.semantic_correctness and \
               formal_language_result.consistency:
                correctness_scores.append(1.0)
                verification_flags.append(True)
            elif formal_language_result.syntax_correctness:
                correctness_scores.append(0.7)
                verification_flags.append(False)
            else:
                correctness_scores.append(0.0)
                verification_flags.append(False)
        
        # 传统方法证明结果
        if traditional_result:
            correctness_scores.append(traditional_result.get("structure_similarity", 0.0))
            verification_flags.append(traditional_result.get("verified", False))
        
        # 计算总体正确性
        overall_correctness = (
            sum(correctness_scores) / len(correctness_scores)
            if correctness_scores else 0.0
        )
        
        # 确定总体状态
        all_verified = all(verification_flags) if verification_flags else False
        
        if overall_correctness >= 0.9 and all_verified:
            overall_status = "完全正确"
        elif overall_correctness >= 0.7:
            overall_status = "高度正确"
        elif overall_correctness >= 0.5:
            overall_status = "中等正确"
        else:
            overall_status = "低正确性"
        
        # 构建证明摘要
        proof_summary = {
            "methods_used": [],
            "verification_results": {}
        }
        
        if info_theory_result:
            proof_summary["methods_used"].append("信息论证明")
            proof_summary["verification_results"]["信息论"] = {
                "correctness": info_theory_result.correctness,
                "status": info_theory_result.proof_status,
                "is_lossless": info_theory_result.is_lossless
            }
        
        if formal_language_result:
            proof_summary["methods_used"].append("形式语言理论证明")
            proof_summary["verification_results"]["形式语言理论"] = {
                "syntax_correctness": formal_language_result.syntax_correctness,
                "semantic_correctness": formal_language_result.semantic_correctness,
                "consistency": formal_language_result.consistency,
                "status": formal_language_result.proof_status
            }
        
        if traditional_result:
            proof_summary["methods_used"].append("传统方法证明")
            proof_summary["verification_results"]["传统方法"] = {
                "structure_similarity": traditional_result.get("structure_similarity", 0.0),
                "status": traditional_result.get("status", "未知")
            }
        
        return IntegratedProofResult(
            information_theory_result=info_theory_result,
            formal_language_result=formal_language_result,
            traditional_result=traditional_result,
            overall_correctness=overall_correctness,
            overall_status=overall_status,
            verification_passed=all_verified,
            proof_summary=proof_summary
        )


class ProofFrameworkAnalyzer:
    """证明框架分析器"""
    
    def __init__(self, framework: IntegratedProofFramework):
        """初始化分析器"""
        self.framework = framework
    
    def comprehensive_analysis(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_grammar_name: Optional[str] = None,
        target_grammar_name: Optional[str] = None,
        source_domain_name: Optional[str] = None,
        target_domain_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """综合分析"""
        result = self.framework.prove_correctness(
            source_schema, target_schema,
            source_grammar_name=source_grammar_name,
            target_grammar_name=target_grammar_name,
            source_domain_name=source_domain_name,
            target_domain_name=target_domain_name
        )
        
        return {
            "overall_correctness": result.overall_correctness,
            "overall_correctness_percentage": f"{result.overall_correctness * 100:.2f}%",
            "overall_status": result.overall_status,
            "verification_passed": result.verification_passed,
            "proof_summary": result.proof_summary,
            "information_theory": {
                "correctness": result.information_theory_result.correctness if result.information_theory_result else None,
                "mutual_information": result.information_theory_result.mutual_information if result.information_theory_result else None,
                "is_lossless": result.information_theory_result.is_lossless if result.information_theory_result else None,
                "status": result.information_theory_result.proof_status if result.information_theory_result else None
            } if result.information_theory_result else None,
            "formal_language": {
                "syntax_correctness": result.formal_language_result.syntax_correctness if result.formal_language_result else None,
                "semantic_correctness": result.formal_language_result.semantic_correctness if result.formal_language_result else None,
                "consistency": result.formal_language_result.consistency if result.formal_language_result else None,
                "status": result.formal_language_result.proof_status if result.formal_language_result else None
            } if result.formal_language_result else None,
            "traditional": result.traditional_result
        }
