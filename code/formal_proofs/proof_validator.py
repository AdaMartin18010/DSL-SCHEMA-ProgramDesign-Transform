"""
形式化证明验证器

提供证明结果的验证和报告功能
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from .integrated_proof_framework import (
    IntegratedProofFramework,
    IntegratedProofResult
)
from .information_theory_proof import InformationTheoryProof
from .formal_language_proof import FormalLanguageProof

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """验证报告"""
    validation_id: str
    timestamp: datetime
    source_schema_name: str
    target_schema_name: str
    proof_result: IntegratedProofResult
    validation_status: str
    recommendations: List[str]
    details: Dict[str, Any]


class ProofValidator:
    """证明验证器"""
    
    def __init__(self, framework: Optional[IntegratedProofFramework] = None):
        """初始化验证器"""
        self.framework = framework or IntegratedProofFramework()
        self.validation_history: List[ValidationReport] = []
    
    def validate_transformation(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_schema_name: str = "source",
        target_schema_name: str = "target",
        source_grammar_name: Optional[str] = None,
        target_grammar_name: Optional[str] = None,
        source_domain_name: Optional[str] = None,
        target_domain_name: Optional[str] = None
    ) -> ValidationReport:
        """验证转换"""
        # 执行证明
        proof_result = self.framework.prove_correctness(
            source_schema, target_schema,
            source_grammar_name=source_grammar_name,
            target_grammar_name=target_grammar_name,
            source_domain_name=source_domain_name,
            target_domain_name=target_domain_name
        )
        
        # 生成验证状态
        validation_status = self._determine_validation_status(proof_result)
        
        # 生成建议
        recommendations = self._generate_recommendations(proof_result)
        
        # 构建详细信息
        details = {
            "information_theory": {
                "correctness": proof_result.information_theory_result.correctness if proof_result.information_theory_result else None,
                "mutual_information": proof_result.information_theory_result.mutual_information if proof_result.information_theory_result else None,
                "source_entropy": proof_result.information_theory_result.source_entropy if proof_result.information_theory_result else None,
                "target_entropy": proof_result.information_theory_result.target_entropy if proof_result.information_theory_result else None,
                "is_lossless": proof_result.information_theory_result.is_lossless if proof_result.information_theory_result else None,
            } if proof_result.information_theory_result else None,
            "formal_language": {
                "syntax_correctness": proof_result.formal_language_result.syntax_correctness if proof_result.formal_language_result else None,
                "semantic_correctness": proof_result.formal_language_result.semantic_correctness if proof_result.formal_language_result else None,
                "consistency": proof_result.formal_language_result.consistency if proof_result.formal_language_result else None,
                "proof_steps": [
                    {
                        "step": step.step_number,
                        "description": step.description,
                        "verified": step.verified
                    }
                    for step in proof_result.formal_language_result.proof_steps
                ] if proof_result.formal_language_result else None,
            } if proof_result.formal_language_result else None,
            "traditional": proof_result.traditional_result
        }
        
        # 创建验证报告
        validation_id = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report = ValidationReport(
            validation_id=validation_id,
            timestamp=datetime.now(),
            source_schema_name=source_schema_name,
            target_schema_name=target_schema_name,
            proof_result=proof_result,
            validation_status=validation_status,
            recommendations=recommendations,
            details=details
        )
        
        self.validation_history.append(report)
        logger.info(f"验证完成: {validation_id} - {validation_status}")
        
        return report
    
    def _determine_validation_status(
        self,
        proof_result: IntegratedProofResult
    ) -> str:
        """确定验证状态"""
        if proof_result.overall_correctness >= 0.9 and proof_result.verification_passed:
            return "验证通过（完全正确）"
        elif proof_result.overall_correctness >= 0.7:
            return "验证通过（高度正确）"
        elif proof_result.overall_correctness >= 0.5:
            return "验证警告（中等正确）"
        else:
            return "验证失败（低正确性）"
    
    def _generate_recommendations(
        self,
        proof_result: IntegratedProofResult
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 信息论建议
        if proof_result.information_theory_result:
            if proof_result.information_theory_result.correctness < 0.9:
                recommendations.append(
                    f"信息论正确性较低（{proof_result.information_theory_result.correctness:.2%}），"
                    "建议优化转换算法以减少信息损失"
                )
            
            if not proof_result.information_theory_result.is_lossless:
                info_loss = proof_result.information_theory_result.information_loss
                recommendations.append(
                    f"转换存在信息损失（总计：{info_loss.total_loss:.2f} bits），"
                    "建议检查转换规则是否完整"
                )
        
        # 形式语言理论建议
        if proof_result.formal_language_result:
            if not proof_result.formal_language_result.syntax_correctness:
                recommendations.append(
                    "语法正确性验证失败，建议检查Schema语法是否符合规范"
                )
            
            if not proof_result.formal_language_result.semantic_correctness:
                recommendations.append(
                    "语义正确性验证失败，建议检查类型映射和语义等价性"
                )
            
            if not proof_result.formal_language_result.consistency:
                recommendations.append(
                    "语法-语义一致性验证失败，建议检查转换函数的语法和语义一致性"
                )
        
        # 传统方法建议
        if proof_result.traditional_result:
            similarity = proof_result.traditional_result.get("structure_similarity", 0.0)
            if similarity < 0.7:
                recommendations.append(
                    f"结构相似度较低（{similarity:.2%}），建议优化转换以保持结构一致性"
                )
        
        # 总体建议
        if proof_result.overall_correctness < 0.7:
            recommendations.append(
                "总体正确性较低，建议重新设计转换函数或使用不同的转换策略"
            )
        
        if not recommendations:
            recommendations.append("转换验证通过，无需额外建议")
        
        return recommendations
    
    def generate_validation_report(
        self,
        report: ValidationReport,
        format: str = "json"
    ) -> str:
        """生成验证报告"""
        if format == "json":
            import json
            return json.dumps({
                "validation_id": report.validation_id,
                "timestamp": report.timestamp.isoformat(),
                "source_schema": report.source_schema_name,
                "target_schema": report.target_schema_name,
                "validation_status": report.validation_status,
                "overall_correctness": report.proof_result.overall_correctness,
                "overall_status": report.proof_result.overall_status,
                "verification_passed": report.proof_result.verification_passed,
                "recommendations": report.recommendations,
                "details": report.details,
                "proof_summary": report.proof_result.proof_summary
            }, indent=2, ensure_ascii=False)
        else:
            # 文本格式
            lines = [
                f"验证报告 ID: {report.validation_id}",
                f"时间: {report.timestamp.isoformat()}",
                f"源Schema: {report.source_schema_name}",
                f"目标Schema: {report.target_schema_name}",
                f"验证状态: {report.validation_status}",
                f"总体正确性: {report.proof_result.overall_correctness:.2%}",
                f"总体状态: {report.proof_result.overall_status}",
                f"验证通过: {'是' if report.proof_result.verification_passed else '否'}",
                "",
                "建议:",
            ]
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            
            return "\n".join(lines)
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """获取验证统计信息"""
        total_validations = len(self.validation_history)
        
        if total_validations == 0:
            return {
                "total_validations": 0,
                "passed_validations": 0,
                "failed_validations": 0,
                "average_correctness": 0.0
            }
        
        passed_validations = len([
            r for r in self.validation_history
            if r.proof_result.verification_passed
        ])
        
        average_correctness = sum(
            r.proof_result.overall_correctness
            for r in self.validation_history
        ) / total_validations
        
        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "pass_rate": passed_validations / total_validations,
            "average_correctness": average_correctness,
            "correctness_distribution": {
                "high": len([r for r in self.validation_history if r.proof_result.overall_correctness >= 0.9]),
                "medium": len([r for r in self.validation_history if 0.7 <= r.proof_result.overall_correctness < 0.9]),
                "low": len([r for r in self.validation_history if r.proof_result.overall_correctness < 0.7])
            }
        }
