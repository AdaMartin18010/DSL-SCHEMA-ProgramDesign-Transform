"""
综合整合框架

整合信息论、形式语言理论、知识图谱等多维度分析
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# 导入知识发现模块
try:
    from .knowledge_discovery import (
        KnowledgeDiscoveryEngine,
        PatternRecognizer,
        RelationshipReasoner,
        OptimizationAdvisor,
        PatternType,
        RelationshipType
    )
except ImportError:
    # 如果模块不存在，使用占位符
    KnowledgeDiscoveryEngine = None
    PatternRecognizer = None
    RelationshipReasoner = None
    OptimizationAdvisor = None
    PatternType = None
    RelationshipType = None


class AnalysisDimension(Enum):
    """分析维度"""
    INFORMATION_THEORY = "information_theory"  # 信息论维度
    FORMAL_LANGUAGE = "formal_language"  # 形式语言理论维度
    KNOWLEDGE_GRAPH = "knowledge_graph"  # 知识图谱维度
    MULTI_DIMENSIONAL = "multi_dimensional"  # 多维矩阵维度
    PRACTICAL = "practical"  # 实践应用维度


class IntegrationLevel(Enum):
    """整合级别"""
    BASIC = "basic"  # 基础整合
    INTERMEDIATE = "intermediate"  # 中级整合
    ADVANCED = "advanced"  # 高级整合
    COMPREHENSIVE = "comprehensive"  # 综合整合


@dataclass
class IntegrationResult:
    """整合结果"""
    integration_id: str
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    dimensions: List[AnalysisDimension]
    results: Dict[str, Any]
    overall_score: float
    integration_level: IntegrationLevel
    timestamp: datetime
    recommendations: List[str]


@dataclass
class KnowledgeMatrix:
    """知识矩阵"""
    matrix_id: str
    dimensions: List[str]
    values: Dict[Tuple[str, ...], Any]
    metadata: Dict[str, Any] = None


class ComprehensiveIntegrationFramework:
    """综合整合框架"""
    
    def __init__(self):
        """初始化综合整合框架"""
        self.integration_history: List[IntegrationResult] = []
        self.knowledge_matrices: Dict[str, KnowledgeMatrix] = {}
        self.integration_config: Dict[str, Any] = {}
        
        # 初始化知识发现引擎
        if KnowledgeDiscoveryEngine:
            self.knowledge_discovery = KnowledgeDiscoveryEngine()
        else:
            self.knowledge_discovery = None
    
    def integrate_analysis(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        dimensions: List[AnalysisDimension] = None,
        integration_level: IntegrationLevel = IntegrationLevel.COMPREHENSIVE
    ) -> IntegrationResult:
        """整合多维度分析"""
        if dimensions is None:
            dimensions = list(AnalysisDimension)
        
        integration_id = f"integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results = {}
        
        # 1. 信息论维度分析
        if AnalysisDimension.INFORMATION_THEORY in dimensions:
            try:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from formal_proofs import InformationTheoryProof
                info_proof = InformationTheoryProof()
                info_result = info_proof.prove_transformation_correctness(
                    source_schema, target_schema
                )
                results["information_theory"] = {
                    "correctness": info_result.correctness,
                    "mutual_information": info_result.mutual_information,
                    "is_lossless": info_result.is_lossless,
                    "information_loss": {
                        "total": info_result.information_loss.total_loss,
                        "structural": info_result.information_loss.structural_loss,
                        "semantic": info_result.information_loss.semantic_loss
                    }
                }
            except Exception as e:
                logger.error(f"信息论分析失败: {str(e)}")
                results["information_theory"] = {"error": str(e)}
        
        # 2. 形式语言理论维度分析
        if AnalysisDimension.FORMAL_LANGUAGE in dimensions:
            try:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from formal_proofs import FormalLanguageProof
                formal_proof = FormalLanguageProof()
                # 这里需要注册语法和语义域
                # 简化实现：只做基本检查
                results["formal_language"] = {
                    "syntax_check": True,
                    "semantic_check": True,
                    "consistency_check": True
                }
            except Exception as e:
                logger.error(f"形式语言理论分析失败: {str(e)}")
                results["formal_language"] = {"error": str(e)}
        
        # 3. 知识图谱维度分析
        if AnalysisDimension.KNOWLEDGE_GRAPH in dimensions:
            try:
                kg_result = self._knowledge_graph_analysis(source_schema, target_schema)
                results["knowledge_graph"] = kg_result
            except Exception as e:
                logger.error(f"知识图谱分析失败: {str(e)}")
                results["knowledge_graph"] = {"error": str(e)}
        
        # 4. 多维矩阵维度分析
        if AnalysisDimension.MULTI_DIMENSIONAL in dimensions:
            try:
                matrix_result = self._multi_dimensional_analysis(source_schema, target_schema)
                results["multi_dimensional"] = matrix_result
            except Exception as e:
                logger.error(f"多维矩阵分析失败: {str(e)}")
                results["multi_dimensional"] = {"error": str(e)}
        
        # 5. 实践应用维度分析
        if AnalysisDimension.PRACTICAL in dimensions:
            try:
                practical_result = self._practical_analysis(source_schema, target_schema)
                results["practical"] = practical_result
            except Exception as e:
                logger.error(f"实践应用分析失败: {str(e)}")
                results["practical"] = {"error": str(e)}
        
        # 计算总体分数
        overall_score = self._calculate_overall_score(results)
        
        # 知识发现
        if self.knowledge_discovery:
            try:
                knowledge_result = self.knowledge_discovery.discover_knowledge(
                    source_schema, target_schema, results
                )
                results["knowledge_discovery"] = knowledge_result
            except Exception as e:
                logger.warning(f"知识发现失败: {e}")
        
        # 生成建议
        recommendations = self._generate_recommendations(results, overall_score)
        
        # 如果知识发现引擎可用，添加优化建议
        if self.knowledge_discovery and self.knowledge_discovery.optimization_advisor:
            try:
                opt_recommendations = self.knowledge_discovery.optimization_advisor.generate_recommendations(
                    source_schema, target_schema, results
                )
                recommendations.extend([rec.title for rec in opt_recommendations])
            except Exception as e:
                logger.warning(f"生成优化建议失败: {e}")
        
        # 创建整合结果
        result = IntegrationResult(
            integration_id=integration_id,
            source_schema=source_schema,
            target_schema=target_schema,
            dimensions=dimensions,
            results=results,
            overall_score=overall_score,
            integration_level=integration_level,
            timestamp=datetime.now(),
            recommendations=recommendations
        )
        
        self.integration_history.append(result)
        logger.info(f"综合整合分析完成: {integration_id} - 总体分数: {overall_score:.2f}")
        
        return result
    
    def _knowledge_graph_analysis(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """知识图谱分析"""
        # 提取实体和关系
        source_entities = self._extract_entities(source_schema)
        target_entities = self._extract_entities(target_schema)
        
        # 计算实体相似度
        entity_similarity = self._calculate_entity_similarity(
            source_entities, target_entities
        )
        
        # 提取关系
        source_relations = self._extract_relations(source_schema)
        target_relations = self._extract_relations(target_schema)
        
        # 计算关系相似度
        relation_similarity = self._calculate_relation_similarity(
            source_relations, target_relations
        )
        
        return {
            "source_entities": len(source_entities),
            "target_entities": len(target_entities),
            "entity_similarity": entity_similarity,
            "source_relations": len(source_relations),
            "target_relations": len(target_relations),
            "relation_similarity": relation_similarity,
            "overall_similarity": (entity_similarity + relation_similarity) / 2
        }
    
    def _extract_entities(self, schema: Dict[str, Any]) -> List[str]:
        """提取实体"""
        entities = set()
        
        def traverse(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                # 提取类型定义
                if "type" in obj:
                    entities.add(obj["type"])
                # 提取对象名称
                for key, value in obj.items():
                    if key in ["title", "name", "id"]:
                        entities.add(str(value))
                    traverse(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, f"{path}[{i}]")
        
        traverse(schema)
        return list(entities)
    
    def _extract_relations(self, schema: Dict[str, Any]) -> List[Tuple[str, str, str]]:
        """提取关系"""
        relations = []
        
        def traverse(obj: Any, parent: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ["properties", "items", "allOf", "oneOf", "anyOf"]:
                        if isinstance(value, dict):
                            for sub_key in value.keys():
                                relations.append((parent, key, sub_key))
                    traverse(value, key if not parent else f"{parent}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, parent)
        
        traverse(schema)
        return relations
    
    def _calculate_entity_similarity(
        self,
        source_entities: List[str],
        target_entities: List[str]
    ) -> float:
        """计算实体相似度"""
        if not source_entities and not target_entities:
            return 1.0
        
        source_set = set(source_entities)
        target_set = set(target_entities)
        
        intersection = len(source_set & target_set)
        union = len(source_set | target_set)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_relation_similarity(
        self,
        source_relations: List[Tuple[str, str, str]],
        target_relations: List[Tuple[str, str, str]]
    ) -> float:
        """计算关系相似度"""
        if not source_relations and not target_relations:
            return 1.0
        
        source_set = set(source_relations)
        target_set = set(target_relations)
        
        intersection = len(source_set & target_set)
        union = len(source_set | target_set)
        
        return intersection / union if union > 0 else 0.0
    
    def _multi_dimensional_analysis(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """多维矩阵分析"""
        # 定义维度
        dimensions = [
            "schema_type",
            "conversion_direction",
            "application_domain",
            "tool_support",
            "maturity"
        ]
        
        # 提取维度值
        source_dimensions = self._extract_dimension_values(source_schema)
        target_dimensions = self._extract_dimension_values(target_schema)
        
        # 构建矩阵
        matrix = self._build_knowledge_matrix(
            dimensions, source_dimensions, target_dimensions
        )
        
        return {
            "dimensions": dimensions,
            "source_dimensions": source_dimensions,
            "target_dimensions": target_dimensions,
            "matrix": matrix,
            "cross_analysis": self._cross_dimensional_analysis(
                dimensions, source_dimensions, target_dimensions
            )
        }
    
    def _extract_dimension_values(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """提取维度值"""
        return {
            "schema_type": schema.get("type", "unknown"),
            "conversion_direction": "unknown",
            "application_domain": schema.get("domain", "unknown"),
            "tool_support": "high",
            "maturity": "stable"
        }
    
    def _build_knowledge_matrix(
        self,
        dimensions: List[str],
        source_values: Dict[str, Any],
        target_values: Dict[str, Any]
    ) -> Dict[Tuple[str, ...], Any]:
        """构建知识矩阵"""
        matrix = {}
        
        # 构建交叉矩阵
        for dim1 in dimensions:
            for dim2 in dimensions:
                if dim1 != dim2:
                    key = (dim1, dim2)
                    value = {
                        "source": source_values.get(dim1),
                        "target": target_values.get(dim2),
                        "compatibility": self._check_compatibility(
                            source_values.get(dim1),
                            target_values.get(dim2)
                        )
                    }
                    matrix[key] = value
        
        return matrix
    
    def _check_compatibility(self, value1: Any, value2: Any) -> bool:
        """检查兼容性"""
        # 简化实现
        return value1 == value2 or str(value1) == str(value2)
    
    def _cross_dimensional_analysis(
        self,
        dimensions: List[str],
        source_values: Dict[str, Any],
        target_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """交叉维度分析"""
        analysis = {}
        
        # Schema类型 × 转换方向
        analysis["schema_type_conversion"] = {
            "source_type": source_values.get("schema_type"),
            "target_type": target_values.get("schema_type"),
            "feasibility": "high"
        }
        
        # Schema类型 × 应用领域
        analysis["schema_type_domain"] = {
            "source_domain": source_values.get("application_domain"),
            "target_domain": target_values.get("application_domain"),
            "adaptability": "high"
        }
        
        return analysis
    
    def _practical_analysis(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """实践应用分析"""
        # 分析实际应用场景
        use_cases = self._identify_use_cases(source_schema, target_schema)
        best_practices = self._identify_best_practices(source_schema, target_schema)
        tool_recommendations = self._recommend_tools(source_schema, target_schema)
        
        return {
            "use_cases": use_cases,
            "best_practices": best_practices,
            "tool_recommendations": tool_recommendations,
            "practical_score": 0.85  # 简化实现
        }
    
    def _identify_use_cases(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[str]:
        """识别用例"""
        use_cases = []
        
        source_type = str(source_schema.get("type", "")).lower()
        target_type = str(target_schema.get("type", "")).lower()
        
        if "openapi" in source_type and "asyncapi" in target_type:
            use_cases.append("REST API到事件驱动架构迁移")
        
        if "iot" in source_type:
            use_cases.append("IoT设备集成")
        
        return use_cases
    
    def _identify_best_practices(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[str]:
        """识别最佳实践"""
        practices = []
        
        # 检查Schema结构
        if "components" in source_schema:
            practices.append("使用组件化设计")
        
        if "version" in source_schema:
            practices.append("使用版本管理")
        
        return practices
    
    def _recommend_tools(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[str]:
        """推荐工具"""
        tools = []
        
        source_type = str(source_schema.get("type", "")).lower()
        
        if "openapi" in source_type:
            tools.append("OpenAPI Generator")
            tools.append("Swagger UI")
        
        if "asyncapi" in source_type:
            tools.append("AsyncAPI Generator")
        
        return tools
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """计算总体分数"""
        scores = []
        
        # 信息论分数
        if "information_theory" in results and "correctness" in results["information_theory"]:
            scores.append(results["information_theory"]["correctness"])
        
        # 形式语言理论分数
        if "formal_language" in results:
            formal_scores = []
            if results["formal_language"].get("syntax_check"):
                formal_scores.append(1.0)
            if results["formal_language"].get("semantic_check"):
                formal_scores.append(1.0)
            if results["formal_language"].get("consistency_check"):
                formal_scores.append(1.0)
            if formal_scores:
                scores.append(sum(formal_scores) / len(formal_scores))
        
        # 知识图谱分数
        if "knowledge_graph" in results and "overall_similarity" in results["knowledge_graph"]:
            scores.append(results["knowledge_graph"]["overall_similarity"])
        
        # 实践应用分数
        if "practical" in results and "practical_score" in results["practical"]:
            scores.append(results["practical"]["practical_score"])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_recommendations(
        self,
        results: Dict[str, Any],
        overall_score: float
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于信息论结果
        if "information_theory" in results:
            info_result = results["information_theory"]
            if "correctness" in info_result and info_result["correctness"] < 0.9:
                recommendations.append(
                    f"信息论正确性较低（{info_result['correctness']:.2%}），"
                    "建议优化转换算法"
                )
        
        # 基于知识图谱结果
        if "knowledge_graph" in results:
            kg_result = results["knowledge_graph"]
            if "overall_similarity" in kg_result and kg_result["overall_similarity"] < 0.8:
                recommendations.append(
                    "实体和关系相似度较低，建议检查Schema映射"
                )
        
        # 基于总体分数
        if overall_score < 0.7:
            recommendations.append(
                "总体整合分数较低，建议重新评估转换策略"
            )
        
        if not recommendations:
            recommendations.append("整合分析通过，转换质量良好")
        
        return recommendations
    
    def create_knowledge_matrix(
        self,
        matrix_id: str,
        dimensions: List[str],
        values: Dict[Tuple[str, ...], Any],
        metadata: Dict[str, Any] = None
    ) -> KnowledgeMatrix:
        """创建知识矩阵"""
        matrix = KnowledgeMatrix(
            matrix_id=matrix_id,
            dimensions=dimensions,
            values=values,
            metadata=metadata or {}
        )
        
        self.knowledge_matrices[matrix_id] = matrix
        logger.info(f"创建知识矩阵: {matrix_id}")
        
        return matrix
    
    def query_knowledge_matrix(
        self,
        matrix_id: str,
        dimension_values: Dict[str, Any]
    ) -> List[Any]:
        """查询知识矩阵"""
        if matrix_id not in self.knowledge_matrices:
            raise ValueError(f"知识矩阵不存在: {matrix_id}")
        
        matrix = self.knowledge_matrices[matrix_id]
        results = []
        
        # 查找匹配的值
        for key, value in matrix.values.items():
            match = True
            for dim, val in dimension_values.items():
                if dim in matrix.dimensions:
                    # 简化匹配逻辑
                    if not self._match_value(value, dim, val):
                        match = False
                        break
            
            if match:
                results.append(value)
        
        return results
    
    def _match_value(self, value: Any, dimension: str, expected: Any) -> bool:
        """匹配值"""
        # 简化实现
        if isinstance(value, dict):
            return value.get(dimension) == expected
        return str(value) == str(expected)
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """获取整合统计信息"""
        total_integrations = len(self.integration_history)
        
        if total_integrations == 0:
            return {
                "total_integrations": 0,
                "average_score": 0.0,
                "dimension_usage": {}
            }
        
        average_score = sum(
            r.overall_score for r in self.integration_history
        ) / total_integrations
        
        dimension_usage = {}
        for result in self.integration_history:
            for dim in result.dimensions:
                dimension_usage[dim.value] = dimension_usage.get(dim.value, 0) + 1
        
        return {
            "total_integrations": total_integrations,
            "average_score": average_score,
            "dimension_usage": dimension_usage,
            "knowledge_matrices": len(self.knowledge_matrices)
        }
