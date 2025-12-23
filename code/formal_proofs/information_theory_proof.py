"""
信息论证明模块

专注于Schema转换的信息论证明，包括信息熵计算、互信息、信道容量等
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math
import json
import logging

logger = logging.getLogger(__name__)


class EntropyComponent(Enum):
    """信息熵组成部分"""
    TYPE = "type"  # 类型熵
    VALUE = "value"  # 值熵
    CONSTRAINT = "constraint"  # 约束熵
    METADATA = "metadata"  # 元数据熵


@dataclass
class EntropyWeights:
    """信息熵权重"""
    type_weight: float = 0.3
    value_weight: float = 0.3
    constraint_weight: float = 0.3
    metadata_weight: float = 0.1


@dataclass
class InformationLoss:
    """信息损失"""
    structural_loss: float = 0.0  # 结构损失
    semantic_loss: float = 0.0  # 语义损失
    constraint_loss: float = 0.0  # 约束损失
    metadata_loss: float = 0.0  # 元数据损失
    total_loss: float = 0.0  # 总损失


@dataclass
class ProofResult:
    """证明结果"""
    correctness: float  # 正确性（0.0-1.0）
    mutual_information: float  # 互信息
    source_entropy: float  # 源Schema熵
    target_entropy: float  # 目标Schema熵
    information_loss: InformationLoss  # 信息损失
    is_lossless: bool  # 是否无损
    proof_status: str  # 证明状态


class InformationTheoryProof:
    """信息论证明器"""
    
    def __init__(self, weights: Optional[EntropyWeights] = None):
        """初始化信息论证明器"""
        self.weights = weights or EntropyWeights()
        self.epsilon = 1e-6  # 浮点数比较精度
    
    def calculate_schema_entropy(
        self,
        schema: Dict[str, Any],
        weights: Optional[EntropyWeights] = None
    ) -> float:
        """计算Schema信息熵"""
        weights = weights or self.weights
        
        # 计算各部分熵
        type_entropy = self._calculate_type_entropy(schema)
        value_entropy = self._calculate_value_entropy(schema)
        constraint_entropy = self._calculate_constraint_entropy(schema)
        metadata_entropy = self._calculate_metadata_entropy(schema)
        
        # 加权求和
        total_entropy = (
            weights.type_weight * type_entropy +
            weights.value_weight * value_entropy +
            weights.constraint_weight * constraint_entropy +
            weights.metadata_weight * metadata_entropy
        )
        
        logger.debug(
            f"Schema熵计算: "
            f"类型={type_entropy:.2f}, "
            f"值={value_entropy:.2f}, "
            f"约束={constraint_entropy:.2f}, "
            f"元数据={metadata_entropy:.2f}, "
            f"总计={total_entropy:.2f}"
        )
        
        return total_entropy
    
    def _calculate_type_entropy(self, schema: Dict[str, Any]) -> float:
        """计算类型熵"""
        # 统计类型分布
        type_counts = {}
        total_types = 0
        
        def count_types(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                if "type" in obj:
                    type_name = obj["type"]
                    type_counts[type_name] = type_counts.get(type_name, 0) + 1
                    total_types += 1
                for key, value in obj.items():
                    count_types(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    count_types(item, f"{path}[{i}]")
        
        count_types(schema)
        
        if total_types == 0:
            return 0.0
        
        # 计算熵
        entropy = 0.0
        for count in type_counts.values():
            probability = count / total_types
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_value_entropy(self, schema: Dict[str, Any]) -> float:
        """计算值熵"""
        # 统计值分布
        value_counts = {}
        total_values = 0
        
        def count_values(obj: Any):
            if isinstance(obj, dict):
                if "enum" in obj:
                    enum_values = obj["enum"]
                    for value in enum_values:
                        value_counts[str(value)] = value_counts.get(str(value), 0) + 1
                        total_values += 1
                for value in obj.values():
                    count_values(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_values(item)
        
        count_values(schema)
        
        if total_values == 0:
            return 0.0
        
        # 计算熵
        entropy = 0.0
        for count in value_counts.values():
            probability = count / total_values
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_constraint_entropy(self, schema: Dict[str, Any]) -> float:
        """计算约束熵"""
        # 统计约束数量
        constraint_count = 0
        
        def count_constraints(obj: Any):
            nonlocal constraint_count
            if isinstance(obj, dict):
                # 常见的约束字段
                constraint_fields = [
                    "minimum", "maximum", "minLength", "maxLength",
                    "pattern", "format", "required", "uniqueItems"
                ]
                for field in constraint_fields:
                    if field in obj:
                        constraint_count += 1
                for value in obj.values():
                    count_constraints(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_constraints(item)
        
        count_constraints(schema)
        
        # 约束熵可以简单地用约束数量来衡量
        # 或者使用更复杂的分布计算
        return math.log2(constraint_count + 1) if constraint_count > 0 else 0.0
    
    def _calculate_metadata_entropy(self, schema: Dict[str, Any]) -> float:
        """计算元数据熵"""
        # 统计元数据字段
        metadata_fields = ["title", "description", "example", "default"]
        metadata_count = 0
        
        def count_metadata(obj: Any):
            nonlocal metadata_count
            if isinstance(obj, dict):
                for field in metadata_fields:
                    if field in obj:
                        metadata_count += 1
                for value in obj.values():
                    count_metadata(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_metadata(item)
        
        count_metadata(schema)
        
        return math.log2(metadata_count + 1) if metadata_count > 0 else 0.0
    
    def calculate_mutual_information(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> float:
        """计算互信息"""
        # 计算联合熵
        joint_entropy = self._calculate_joint_entropy(source_schema, target_schema)
        
        # 计算源和目标熵
        source_entropy = self.calculate_schema_entropy(source_schema)
        target_entropy = self.calculate_schema_entropy(target_schema)
        
        # 互信息 = H(source) + H(target) - H(source, target)
        mutual_info = source_entropy + target_entropy - joint_entropy
        
        return max(0.0, mutual_info)  # 确保非负
    
    def _calculate_joint_entropy(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> float:
        """计算联合熵"""
        # 简化实现：使用两个Schema的合并来计算联合熵
        # 实际应该考虑转换关系
        merged_schema = {
            "source": source_schema,
            "target": target_schema
        }
        return self.calculate_schema_entropy(merged_schema)
    
    def calculate_information_loss(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> InformationLoss:
        """计算信息损失"""
        source_entropy = self.calculate_schema_entropy(source_schema)
        target_entropy = self.calculate_schema_entropy(target_schema)
        mutual_info = self.calculate_mutual_information(source_schema, target_schema)
        
        # 总损失 = 源熵 - 互信息
        total_loss = source_entropy - mutual_info
        
        # 分类损失（简化实现）
        structural_loss = total_loss * 0.4
        semantic_loss = total_loss * 0.3
        constraint_loss = total_loss * 0.2
        metadata_loss = total_loss * 0.1
        
        return InformationLoss(
            structural_loss=structural_loss,
            semantic_loss=semantic_loss,
            constraint_loss=constraint_loss,
            metadata_loss=metadata_loss,
            total_loss=total_loss
        )
    
    def calculate_correctness(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> float:
        """计算转换正确性"""
        source_entropy = self.calculate_schema_entropy(source_schema)
        
        if source_entropy == 0:
            return 1.0  # 空Schema认为完全正确
        
        mutual_info = self.calculate_mutual_information(source_schema, target_schema)
        correctness = mutual_info / source_entropy
        
        return min(1.0, max(0.0, correctness))  # 限制在[0, 1]范围内
    
    def is_lossless_transformation(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> bool:
        """判断转换是否无损"""
        source_entropy = self.calculate_schema_entropy(source_schema)
        mutual_info = self.calculate_mutual_information(source_schema, target_schema)
        
        # 无损条件：互信息等于源Schema熵
        return abs(mutual_info - source_entropy) < self.epsilon
    
    def calculate_channel_capacity(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> float:
        """计算信道容量"""
        # 信道容量 = max I(source; target)
        # 简化实现：使用当前分布的互信息
        mutual_info = self.calculate_mutual_information(source_schema, target_schema)
        return mutual_info
    
    def prove_transformation_correctness(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        transform_func: Optional[callable] = None
    ) -> ProofResult:
        """证明转换正确性"""
        # 计算各种指标
        source_entropy = self.calculate_schema_entropy(source_schema)
        target_entropy = self.calculate_schema_entropy(target_schema)
        mutual_info = self.calculate_mutual_information(source_schema, target_schema)
        correctness = self.calculate_correctness(source_schema, target_schema)
        is_lossless = self.is_lossless_transformation(source_schema, target_schema)
        information_loss = self.calculate_information_loss(source_schema, target_schema)
        
        # 确定证明状态
        if correctness >= 0.9:
            proof_status = "高度正确"
        elif correctness >= 0.7:
            proof_status = "中等正确"
        else:
            proof_status = "低正确性"
        
        if is_lossless:
            proof_status = "完全正确（无损）"
        
        return ProofResult(
            correctness=correctness,
            mutual_information=mutual_info,
            source_entropy=source_entropy,
            target_entropy=target_entropy,
            information_loss=information_loss,
            is_lossless=is_lossless,
            proof_status=proof_status
        )


class InformationTheoryAnalyzer:
    """信息论分析器"""
    
    def __init__(self, proof_engine: InformationTheoryProof):
        """初始化分析器"""
        self.proof_engine = proof_engine
    
    def analyze_transformation_quality(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析转换质量"""
        result = self.proof_engine.prove_transformation_correctness(
            source_schema, target_schema
        )
        
        return {
            "correctness": result.correctness,
            "correctness_percentage": f"{result.correctness * 100:.2f}%",
            "mutual_information": result.mutual_information,
            "source_entropy": result.source_entropy,
            "target_entropy": result.target_entropy,
            "information_loss": {
                "total": result.information_loss.total_loss,
                "structural": result.information_loss.structural_loss,
                "semantic": result.information_loss.semantic_loss,
                "constraint": result.information_loss.constraint_loss,
                "metadata": result.information_loss.metadata_loss,
            },
            "loss_rate": (
                result.information_loss.total_loss / result.source_entropy
                if result.source_entropy > 0 else 0.0
            ),
            "is_lossless": result.is_lossless,
            "proof_status": result.proof_status,
            "channel_capacity": self.proof_engine.calculate_channel_capacity(
                source_schema, target_schema
            )
        }
    
    def compare_transformations(
        self,
        source_schema: Dict[str, Any],
        transformations: List[Tuple[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """比较多个转换"""
        results = {}
        
        for name, target_schema in transformations:
            analysis = self.analyze_transformation_quality(source_schema, target_schema)
            results[name] = analysis
        
        # 找出最佳转换
        best_transformation = max(
            results.items(),
            key=lambda x: x[1]["correctness"]
        )
        
        return {
            "transformations": results,
            "best_transformation": {
                "name": best_transformation[0],
                "correctness": best_transformation[1]["correctness"]
            },
            "comparison_summary": {
                "total": len(transformations),
                "high_quality": len([
                    r for r in results.values()
                    if r["correctness"] >= 0.9
                ]),
                "medium_quality": len([
                    r for r in results.values()
                    if 0.7 <= r["correctness"] < 0.9
                ]),
                "low_quality": len([
                    r for r in results.values()
                    if r["correctness"] < 0.7
                ])
            }
        }
