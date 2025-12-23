"""
知识发现模块

实现模式识别、关系推理、优化建议等知识发现功能
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """模式类型"""
    CONVERSION_PATTERN = "conversion_pattern"  # 转换模式
    STRUCTURE_PATTERN = "structure_pattern"  # 结构模式
    SEMANTIC_PATTERN = "semantic_pattern"  # 语义模式
    OPTIMIZATION_PATTERN = "optimization_pattern"  # 优化模式


class RelationshipType(Enum):
    """关系类型"""
    EQUIVALENT = "equivalent"  # 等价关系
    COMPATIBLE = "compatible"  # 兼容关系
    TRANSFORMABLE = "transformable"  # 可转换关系
    DEPENDENT = "dependent"  # 依赖关系
    SIMILAR = "similar"  # 相似关系


@dataclass
class Pattern:
    """模式"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    characteristics: List[str]
    examples: List[Dict[str, Any]]
    confidence: float
    frequency: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """关系"""
    relationship_id: str
    relationship_type: RelationshipType
    source_schema: str
    target_schema: str
    confidence: float
    evidence: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRecommendation:
    """优化建议"""
    recommendation_id: str
    title: str
    description: str
    priority: int  # 1-5, 5最高
    impact: str  # high, medium, low
    category: str
    suggested_actions: List[str]
    estimated_improvement: float  # 预期改进百分比
    created_at: datetime = field(default_factory=datetime.now)


class PatternRecognizer:
    """模式识别器"""
    
    def __init__(self):
        """初始化模式识别器"""
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_index: Dict[str, List[str]] = {}  # 特征 -> 模式ID列表
    
    def register_pattern(
        self,
        pattern_type: PatternType,
        name: str,
        description: str,
        characteristics: List[str],
        examples: List[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> Pattern:
        """注册模式"""
        pattern_id = f"pattern_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            name=name,
            description=description,
            characteristics=characteristics,
            examples=examples or [],
            confidence=confidence
        )
        
        self.patterns[pattern_id] = pattern
        
        # 更新索引
        for char in characteristics:
            if char not in self.pattern_index:
                self.pattern_index[char] = []
            if pattern_id not in self.pattern_index[char]:
                self.pattern_index[char].append(pattern_id)
        
        logger.info(f"注册模式: {name} ({pattern_id})")
        return pattern
    
    def recognize_patterns(
        self,
        schema: Dict[str, Any],
        pattern_types: List[PatternType] = None
    ) -> List[Pattern]:
        """识别模式"""
        if pattern_types is None:
            pattern_types = list(PatternType)
        
        recognized = []
        schema_str = json.dumps(schema, sort_keys=True)
        
        for pattern_id, pattern in self.patterns.items():
            if pattern.pattern_type not in pattern_types:
                continue
            
            # 检查特征匹配
            match_count = 0
            for char in pattern.characteristics:
                if char.lower() in schema_str.lower():
                    match_count += 1
            
            # 计算匹配度
            match_ratio = match_count / len(pattern.characteristics) if pattern.characteristics else 0
            
            if match_ratio >= 0.5:  # 至少50%特征匹配
                pattern.frequency += 1
                recognized.append(pattern)
                logger.debug(f"识别到模式: {pattern.name} (匹配度: {match_ratio:.2%})")
        
        return recognized
    
    def find_similar_patterns(
        self,
        pattern_id: str,
        threshold: float = 0.7
    ) -> List[Tuple[Pattern, float]]:
        """查找相似模式"""
        if pattern_id not in self.patterns:
            return []
        
        target_pattern = self.patterns[pattern_id]
        similar = []
        
        for pid, pattern in self.patterns.items():
            if pid == pattern_id:
                continue
            
            # 计算相似度（基于特征重叠）
            target_chars = set(target_pattern.characteristics)
            pattern_chars = set(pattern.characteristics)
            
            if len(target_chars) == 0:
                similarity = 0.0
            else:
                intersection = target_chars & pattern_chars
                union = target_chars | pattern_chars
                similarity = len(intersection) / len(union) if union else 0.0
            
            if similarity >= threshold:
                similar.append((pattern, similarity))
        
        # 按相似度排序
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """获取模式统计信息"""
        stats = {
            "total_patterns": len(self.patterns),
            "patterns_by_type": {},
            "most_frequent": [],
            "total_frequency": sum(p.frequency for p in self.patterns.values())
        }
        
        # 按类型统计
        for pattern_type in PatternType:
            count = sum(1 for p in self.patterns.values() if p.pattern_type == pattern_type)
            stats["patterns_by_type"][pattern_type.value] = count
        
        # 最频繁的模式
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )
        stats["most_frequent"] = [
            {
                "pattern_id": p.pattern_id,
                "name": p.name,
                "frequency": p.frequency
            }
            for p in sorted_patterns[:10]
        ]
        
        return stats


class RelationshipReasoner:
    """关系推理器"""
    
    def __init__(self):
        """初始化关系推理器"""
        self.relationships: Dict[str, Relationship] = {}
        self.relationship_graph: Dict[str, Set[str]] = {}  # schema_id -> 相关schema_id集合
    
    def infer_relationship(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        relationship_type: RelationshipType = None
    ) -> Relationship:
        """推理关系"""
        source_id = self._get_schema_id(source_schema)
        target_id = self._get_schema_id(target_schema)
        
        # 检查是否已存在关系
        existing = self._find_existing_relationship(source_id, target_id)
        if existing:
            return existing
        
        # 推理关系类型
        if relationship_type is None:
            relationship_type = self._infer_relationship_type(source_schema, target_schema)
        
        # 收集证据
        evidence = self._collect_evidence(source_schema, target_schema, relationship_type)
        
        # 计算置信度
        confidence = self._calculate_confidence(source_schema, target_schema, evidence)
        
        # 创建关系
        relationship_id = f"rel_{hashlib.md5(f'{source_id}_{target_id}'.encode()).hexdigest()[:8]}"
        relationship = Relationship(
            relationship_id=relationship_id,
            relationship_type=relationship_type,
            source_schema=source_id,
            target_schema=target_id,
            confidence=confidence,
            evidence=evidence
        )
        
        self.relationships[relationship_id] = relationship
        
        # 更新关系图
        if source_id not in self.relationship_graph:
            self.relationship_graph[source_id] = set()
        self.relationship_graph[source_id].add(target_id)
        
        logger.info(f"推理关系: {source_id} -> {target_id} ({relationship_type.value}, 置信度: {confidence:.2%})")
        return relationship
    
    def find_transformation_path(
        self,
        source_schema_id: str,
        target_schema_id: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        """查找转换路径"""
        paths = []
        
        def dfs(current: str, target: str, path: List[str], visited: Set[str], depth: int):
            if depth > max_depth:
                return
            
            if current == target:
                paths.append(path.copy())
                return
            
            if current not in self.relationship_graph:
                return
            
            for next_schema in self.relationship_graph[current]:
                if next_schema in visited:
                    continue
                
                # 检查关系是否支持转换
                rel = self._find_existing_relationship(current, next_schema)
                if rel and rel.relationship_type in [RelationshipType.TRANSFORMABLE, RelationshipType.EQUIVALENT]:
                    visited.add(next_schema)
                    path.append(next_schema)
                    dfs(next_schema, target, path, visited, depth + 1)
                    path.pop()
                    visited.remove(next_schema)
        
        visited = {source_schema_id}
        dfs(source_schema_id, target_schema_id, [source_schema_id], visited, 0)
        
        return paths
    
    def _get_schema_id(self, schema: Dict[str, Any]) -> str:
        """获取Schema ID"""
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()[:16]
    
    def _find_existing_relationship(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[Relationship]:
        """查找现有关系"""
        for rel in self.relationships.values():
            if rel.source_schema == source_id and rel.target_schema == target_id:
                return rel
        return None
    
    def _infer_relationship_type(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> RelationshipType:
        """推理关系类型"""
        # 简化实现：基于结构相似性
        source_str = json.dumps(source_schema, sort_keys=True)
        target_str = json.dumps(target_schema, sort_keys=True)
        
        if source_str == target_str:
            return RelationshipType.EQUIVALENT
        
        # 检查结构相似性
        source_keys = set(self._extract_keys(source_schema))
        target_keys = set(self._extract_keys(target_schema))
        
        intersection = source_keys & target_keys
        union = source_keys | target_keys
        
        similarity = len(intersection) / len(union) if union else 0.0
        
        if similarity > 0.8:
            return RelationshipType.SIMILAR
        elif similarity > 0.5:
            return RelationshipType.COMPATIBLE
        else:
            return RelationshipType.TRANSFORMABLE
    
    def _extract_keys(self, obj: Any, prefix: str = "") -> List[str]:
        """提取所有键"""
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                full_key = f"{prefix}.{k}" if prefix else k
                keys.append(full_key)
                keys.extend(self._extract_keys(v, full_key))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                keys.extend(self._extract_keys(item, f"{prefix}[{i}]"))
        return keys
    
    def _collect_evidence(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        relationship_type: RelationshipType
    ) -> List[str]:
        """收集证据"""
        evidence = []
        
        # 结构相似性证据
        source_keys = set(self._extract_keys(source_schema))
        target_keys = set(self._extract_keys(target_schema))
        common_keys = source_keys & target_keys
        
        if common_keys:
            evidence.append(f"共同键: {len(common_keys)}个")
        
        # 类型相似性证据
        source_types = self._extract_types(source_schema)
        target_types = self._extract_types(target_schema)
        common_types = source_types & target_types
        
        if common_types:
            evidence.append(f"共同类型: {len(common_types)}个")
        
        return evidence
    
    def _extract_types(self, obj: Any) -> Set[str]:
        """提取类型"""
        types = set()
        if isinstance(obj, dict):
            for v in obj.values():
                types.add(type(v).__name__)
                types.update(self._extract_types(v))
        elif isinstance(obj, list):
            for item in obj:
                types.update(self._extract_types(item))
        return types
    
    def _calculate_confidence(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        evidence: List[str]
    ) -> float:
        """计算置信度"""
        # 基于证据数量和质量计算置信度
        base_confidence = 0.5
        
        # 证据加分
        evidence_bonus = min(len(evidence) * 0.1, 0.3)
        
        # 结构相似性加分
        source_keys = set(self._extract_keys(source_schema))
        target_keys = set(self._extract_keys(target_schema))
        similarity = len(source_keys & target_keys) / len(source_keys | target_keys) if (source_keys | target_keys) else 0.0
        similarity_bonus = similarity * 0.2
        
        confidence = min(base_confidence + evidence_bonus + similarity_bonus, 1.0)
        return confidence


class OptimizationAdvisor:
    """优化建议器"""
    
    def __init__(self):
        """初始化优化建议器"""
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.applied_recommendations: Set[str] = set()
    
    def generate_recommendations(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """生成优化建议"""
        recommendations = []
        
        # 基于信息论分析生成建议
        if "information_theory" in analysis_results:
            info_result = analysis_results["information_theory"]
            if info_result.get("information_loss", {}).get("total", 0) > 0.1:
                rec = self._create_recommendation(
                    "减少信息损失",
                    "转换过程中存在信息损失，建议优化转换规则",
                    priority=4,
                    impact="high",
                    category="information_loss",
                    actions=[
                        "检查转换规则完整性",
                        "添加缺失字段映射",
                        "保留更多元数据"
                    ],
                    estimated_improvement=0.2
                )
                recommendations.append(rec)
        
        # 基于结构分析生成建议
        source_complexity = self._calculate_complexity(source_schema)
        target_complexity = self._calculate_complexity(target_schema)
        
        if target_complexity > source_complexity * 1.5:
            rec = self._create_recommendation(
                "简化目标Schema结构",
                "目标Schema结构过于复杂，建议简化",
                priority=3,
                impact="medium",
                category="structure",
                actions=[
                    "合并相似字段",
                    "减少嵌套层级",
                    "使用更简单的数据类型"
                ],
                estimated_improvement=0.15
            )
            recommendations.append(rec)
        
        # 基于性能分析生成建议
        if "performance" in analysis_results:
            perf_result = analysis_results["performance"]
            if perf_result.get("estimated_time", 0) > 1000:  # ms
                rec = self._create_recommendation(
                    "优化转换性能",
                    "转换性能较慢，建议优化",
                    priority=2,
                    impact="medium",
                    category="performance",
                    actions=[
                        "使用缓存机制",
                        "并行处理",
                        "优化转换算法"
                    ],
                    estimated_improvement=0.3
                )
                recommendations.append(rec)
        
        # 保存建议
        for rec in recommendations:
            self.recommendations[rec.recommendation_id] = rec
        
        return recommendations
    
    def _create_recommendation(
        self,
        title: str,
        description: str,
        priority: int,
        impact: str,
        category: str,
        actions: List[str],
        estimated_improvement: float
    ) -> OptimizationRecommendation:
        """创建建议"""
        recommendation_id = f"rec_{hashlib.md5(title.encode()).hexdigest()[:8]}"
        return OptimizationRecommendation(
            recommendation_id=recommendation_id,
            title=title,
            description=description,
            priority=priority,
            impact=impact,
            category=category,
            suggested_actions=actions,
            estimated_improvement=estimated_improvement
        )
    
    def _calculate_complexity(self, schema: Dict[str, Any]) -> float:
        """计算Schema复杂度"""
        def count_nodes(obj: Any, depth: int = 0) -> int:
            count = 1
            if isinstance(obj, dict):
                for v in obj.values():
                    count += count_nodes(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    count += count_nodes(item, depth + 1)
            return count
        
        return count_nodes(schema)
    
    def apply_recommendation(self, recommendation_id: str) -> bool:
        """应用建议"""
        if recommendation_id in self.recommendations:
            self.applied_recommendations.add(recommendation_id)
            logger.info(f"应用建议: {recommendation_id}")
            return True
        return False
    
    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """获取建议统计信息"""
        return {
            "total_recommendations": len(self.recommendations),
            "applied_recommendations": len(self.applied_recommendations),
            "by_category": self._count_by_category(),
            "by_priority": self._count_by_priority()
        }
    
    def _count_by_category(self) -> Dict[str, int]:
        """按类别统计"""
        counts = {}
        for rec in self.recommendations.values():
            counts[rec.category] = counts.get(rec.category, 0) + 1
        return counts
    
    def _count_by_priority(self) -> Dict[int, int]:
        """按优先级统计"""
        counts = {}
        for rec in self.recommendations.values():
            counts[rec.priority] = counts.get(rec.priority, 0) + 1
        return counts


class KnowledgeDiscoveryEngine:
    """知识发现引擎"""
    
    def __init__(self):
        """初始化知识发现引擎"""
        self.pattern_recognizer = PatternRecognizer()
        self.relationship_reasoner = RelationshipReasoner()
        self.optimization_advisor = OptimizationAdvisor()
    
    def discover_knowledge(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        analysis_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """发现知识"""
        discovery_result = {
            "patterns": [],
            "relationships": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. 模式识别
        source_patterns = self.pattern_recognizer.recognize_patterns(source_schema)
        target_patterns = self.pattern_recognizer.recognize_patterns(target_schema)
        discovery_result["patterns"] = {
            "source": [p.pattern_id for p in source_patterns],
            "target": [p.pattern_id for p in target_patterns],
            "common": [
                p.pattern_id for p in source_patterns
                if p.pattern_id in [tp.pattern_id for tp in target_patterns]
            ]
        }
        
        # 2. 关系推理
        relationship = self.relationship_reasoner.infer_relationship(
            source_schema, target_schema
        )
        discovery_result["relationships"] = [relationship.relationship_id]
        
        # 3. 优化建议
        if analysis_results:
            recommendations = self.optimization_advisor.generate_recommendations(
                source_schema, target_schema, analysis_results
            )
            discovery_result["recommendations"] = [
                rec.recommendation_id for rec in recommendations
            ]
        
        return discovery_result
    
    def find_optimal_path(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[List[str]]:
        """查找最优转换路径"""
        source_id = self.relationship_reasoner._get_schema_id(source_schema)
        target_id = self.relationship_reasoner._get_schema_id(target_schema)
        
        paths = self.relationship_reasoner.find_transformation_path(
            source_id, target_id
        )
        
        # 按路径长度排序
        paths.sort(key=len)
        
        return paths
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "patterns": self.pattern_recognizer.get_pattern_statistics(),
            "relationships": {
                "total": len(self.relationship_reasoner.relationships),
                "by_type": self._count_relationships_by_type()
            },
            "recommendations": self.optimization_advisor.get_recommendation_statistics()
        }
    
    def _count_relationships_by_type(self) -> Dict[str, int]:
        """按类型统计关系"""
        counts = {}
        for rel in self.relationship_reasoner.relationships.values():
            rel_type = rel.relationship_type.value
            counts[rel_type] = counts.get(rel_type, 0) + 1
        return counts
