#!/usr/bin/env python3
"""
Smart Recommendation Engine
===========================

智能推荐引擎，提供：
- 基于内容的Schema推荐
- 使用模式分析
- 相似度匹配
- 个性化建议
- 趋势发现

Version: 2.3.0
"""

import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict, Counter
from datetime import datetime


@dataclass
class SchemaProfile:
    """Schema档案"""
    schema_id: str
    schema_type: str
    properties: List[str]
    patterns: List[str]
    usage_count: int = 0
    last_used: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """推荐项"""
    item_id: str
    item_type: str  # 'schema', 'field', 'pattern', 'template'
    score: float
    reason: str
    confidence: float
    metadata: Dict = field(default_factory=dict)


class SmartRecommendationEngine:
    """智能推荐引擎"""
    
    def __init__(self):
        self.schema_profiles: Dict[str, SchemaProfile] = {}
        self.usage_history: List[Dict] = []
        self.patterns = self._initialize_patterns()
        self.templates = self._initialize_templates()
        self.user_preferences: Dict[str, List[str]] = defaultdict(list)
    
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """初始化常见模式"""
        return {
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "ISO 8601 timestamp"
            },
            "email": {
                "type": "string",
                "format": "email",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            },
            "uuid": {
                "type": "string",
                "format": "uuid",
                "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
            },
            "url": {
                "type": "string",
                "format": "uri",
                "pattern": "^https?://"
            },
            "money": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "enum": ["USD", "EUR", "CNY"]}
                },
                "required": ["amount", "currency"]
            },
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                    "postalCode": {"type": "string"}
                }
            },
            "person_name": {
                "type": "object",
                "properties": {
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "fullName": {"type": "string"}
                }
            },
            "pagination": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "minimum": 1},
                    "pageSize": {"type": "integer", "minimum": 1, "maximum": 100},
                    "totalPages": {"type": "integer"},
                    "totalItems": {"type": "integer"}
                }
            }
        }
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """初始化Schema模板"""
        return {
            "user_profile": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "username": {"type": "string"},
                    "email": {"$ref": "#/patterns/email"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "displayName": {"type": "string"},
                            "avatar": {"$ref": "#/patterns/url"},
                            "bio": {"type": "string"}
                        }
                    },
                    "createdAt": {"$ref": "#/patterns/timestamp"},
                    "updatedAt": {"$ref": "#/patterns/timestamp"}
                },
                "required": ["id", "username", "email"]
            },
            "api_response": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {"type": "object"},
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "message": {"type": "string"}
                        }
                    },
                    "meta": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"$ref": "#/patterns/timestamp"},
                            "requestId": {"type": "string"}
                        }
                    }
                },
                "required": ["success"]
            },
            "event_log": {
                "type": "object",
                "properties": {
                    "eventId": {"type": "string"},
                    "eventType": {"type": "string"},
                    "timestamp": {"$ref": "#/patterns/timestamp"},
                    "actor": {"type": "string"},
                    "resource": {"type": "string"},
                    "action": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["eventId", "eventType", "timestamp"]
            }
        }
    
    def analyze_schema(self, schema: Dict) -> SchemaProfile:
        """分析Schema并创建档案"""
        schema_id = schema.get("$id", schema.get("title", "unknown"))
        schema_type = schema.get("type", "object")
        
        # 提取所有属性
        properties = self._extract_properties(schema)
        
        # 识别模式
        patterns = self._identify_patterns(schema)
        
        profile = SchemaProfile(
            schema_id=schema_id,
            schema_type=schema_type,
            properties=properties,
            patterns=patterns
        )
        
        self.schema_profiles[schema_id] = profile
        return profile
    
    def _extract_properties(self, schema: Dict, prefix: str = "") -> List[str]:
        """提取所有属性路径"""
        properties = []
        
        if not isinstance(schema, dict):
            return properties
        
        props = schema.get("properties", {})
        for key, value in props.items():
            path = f"{prefix}.{key}" if prefix else key
            properties.append(path)
            
            # 递归处理嵌套对象
            if isinstance(value, dict) and value.get("type") == "object":
                properties.extend(self._extract_properties(value, path))
        
        return properties
    
    def _identify_patterns(self, schema: Dict) -> List[str]:
        """识别Schema中的模式"""
        patterns = []
        schema_str = json.dumps(schema)
        
        for pattern_name, pattern_def in self.patterns.items():
            if self._matches_pattern(schema, pattern_def):
                patterns.append(pattern_name)
        
        return patterns
    
    def _matches_pattern(self, schema: Dict, pattern: Dict) -> bool:
        """检查Schema是否匹配模式"""
        # 简化检查：比较关键特征
        if pattern.get("format") and schema.get("format") == pattern.get("format"):
            return True
        if pattern.get("pattern") and schema.get("pattern") == pattern.get("pattern"):
            return True
        return False
    
    def recommend_similar_schemas(self, schema: Dict, 
                                   top_k: int = 5) -> List[Recommendation]:
        """
        推荐相似Schema
        
        Args:
            schema: 目标Schema
            top_k: 推荐数量
        
        Returns:
            List[Recommendation]: 推荐列表
        """
        target_profile = self.analyze_schema(schema)
        recommendations = []
        
        for profile_id, profile in self.schema_profiles.items():
            if profile_id == target_profile.schema_id:
                continue
            
            # 计算相似度
            similarity = self._calculate_similarity(target_profile, profile)
            
            if similarity > 0.3:  # 阈值
                recommendations.append(Recommendation(
                    item_id=profile_id,
                    item_type="schema",
                    score=similarity,
                    reason=f"属性相似度: {similarity:.2%}",
                    confidence=similarity
                ))
        
        # 按分数排序
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_k]
    
    def _calculate_similarity(self, profile1: SchemaProfile, 
                               profile2: SchemaProfile) -> float:
        """计算两个Schema档案的相似度"""
        # Jaccard相似度
        set1 = set(profile1.properties)
        set2 = set(profile2.properties)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def recommend_fields(self, partial_schema: Dict, 
                         context: str = None) -> List[Recommendation]:
        """
        推荐字段
        
        Args:
            partial_schema: 部分完成的Schema
            context: 使用上下文
        
        Returns:
            List[Recommendation]: 推荐字段列表
        """
        recommendations = []
        existing_fields = set(self._extract_properties(partial_schema))
        
        # 基于上下文推荐
        if context:
            context_fields = self._get_context_fields(context)
            for field in context_fields:
                if field not in existing_fields:
                    recommendations.append(Recommendation(
                        item_id=field,
                        item_type="field",
                        score=0.8,
                        reason=f"'{context}' 上下文中常用字段",
                        confidence=0.8
                    ))
        
        # 基于相似Schema推荐
        profile = self.analyze_schema(partial_schema)
        for other_profile in self.schema_profiles.values():
            similarity = self._calculate_similarity(profile, other_profile)
            if similarity > 0.5:
                for field in other_profile.properties:
                    if field not in existing_fields:
                        recommendations.append(Recommendation(
                            item_id=field,
                            item_type="field",
                            score=similarity * 0.7,
                            reason=f"相似Schema '{other_profile.schema_id}' 中的字段",
                            confidence=similarity
                        ))
        
        # 去重并按分数排序
        seen = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda x: x.score, reverse=True):
            if rec.item_id not in seen:
                seen.add(rec.item_id)
                unique_recs.append(rec)
        
        return unique_recs[:10]
    
    def _get_context_fields(self, context: str) -> List[str]:
        """获取上下文相关的字段"""
        context_fields = {
            "user": ["id", "username", "email", "password", "createdAt", "updatedAt", "role"],
            "product": ["id", "name", "description", "price", "category", "inventory", "sku"],
            "order": ["id", "userId", "items", "total", "status", "createdAt", "shippingAddress"],
            "api": ["success", "data", "error", "message", "code", "timestamp"],
            "event": ["eventId", "eventType", "timestamp", "actor", "resource", "action"]
        }
        
        return context_fields.get(context.lower(), [])
    
    def recommend_patterns(self, schema: Dict) -> List[Recommendation]:
        """
        推荐可应用的模式
        
        Args:
            schema: 当前Schema
        
        Returns:
            List[Recommendation]: 模式推荐
        """
        recommendations = []
        existing_patterns = self._identify_patterns(schema)
        
        for pattern_name, pattern_def in self.patterns.items():
            if pattern_name not in existing_patterns:
                # 检查字段名匹配
                schema_str = json.dumps(schema)
                if any(keyword in schema_str.lower() for keyword in pattern_name.lower().split("_")):
                    recommendations.append(Recommendation(
                        item_id=pattern_name,
                        item_type="pattern",
                        score=0.75,
                        reason=f"字段名暗示可能使用 '{pattern_name}' 模式",
                        confidence=0.75,
                        metadata=pattern_def
                    ))
        
        return recommendations
    
    def recommend_templates(self, use_case: str) -> List[Recommendation]:
        """
        推荐模板
        
        Args:
            use_case: 使用场景描述
        
        Returns:
            List[Recommendation]: 模板推荐
        """
        recommendations = []
        
        use_case_lower = use_case.lower()
        
        for template_name, template_def in self.templates.items():
            score = self._calculate_template_match(use_case_lower, template_name, template_def)
            if score > 0.3:
                recommendations.append(Recommendation(
                    item_id=template_name,
                    item_type="template",
                    score=score,
                    reason=f"匹配 '{use_case}' 使用场景",
                    confidence=score,
                    metadata=template_def
                ))
        
        return sorted(recommendations, key=lambda x: x.score, reverse=True)
    
    def _calculate_template_match(self, use_case: str, template_name: str, 
                                   template: Dict) -> float:
        """计算模板匹配分数"""
        keywords = {
            "user_profile": ["user", "profile", "account", "member"],
            "api_response": ["api", "response", "endpoint", "result"],
            "event_log": ["event", "log", "audit", "track"]
        }
        
        template_keywords = keywords.get(template_name, [])
        matches = sum(1 for kw in template_keywords if kw in use_case)
        
        return matches / len(template_keywords) if template_keywords else 0.0
    
    def record_usage(self, schema_id: str, action: str):
        """记录Schema使用"""
        if schema_id in self.schema_profiles:
            profile = self.schema_profiles[schema_id]
            profile.usage_count += 1
            profile.last_used = datetime.now()
        
        self.usage_history.append({
            "schema_id": schema_id,
            "action": action,
            "timestamp": datetime.now()
        })
    
    def get_trending_schemas(self, days: int = 7, top_k: int = 10) -> List[Recommendation]:
        """获取热门Schema"""
        # 按使用次数排序
        sorted_profiles = sorted(
            self.schema_profiles.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )
        
        return [
            Recommendation(
                item_id=p.schema_id,
                item_type="schema",
                score=min(p.usage_count / 100, 1.0),  # 归一化
                reason=f"使用次数: {p.usage_count}",
                confidence=0.9
            )
            for p in sorted_profiles[:top_k]
        ]


def main():
    """示例用法"""
    engine = SmartRecommendationEngine()
    
    # 示例1: 分析Schema
    print("=" * 60)
    print("示例1: Schema分析")
    print("=" * 60)
    
    schema = {
        "$id": "user-schema",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "username": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "createdAt": {"type": "string", "format": "date-time"},
            "profile": {
                "type": "object",
                "properties": {
                    "bio": {"type": "string"},
                    "avatar": {"type": "string", "format": "uri"}
                }
            }
        }
    }
    
    profile = engine.analyze_schema(schema)
    print(f"Schema ID: {profile.schema_id}")
    print(f"类型: {profile.schema_type}")
    print(f"属性数量: {len(profile.properties)}")
    print(f"识别模式: {profile.patterns}")
    
    # 示例2: 推荐相似Schema
    print("\n" + "=" * 60)
    print("示例2: 相似Schema推荐")
    print("=" * 60)
    
    # 添加另一个Schema
    similar_schema = {
        "$id": "member-schema",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "joinedAt": {"type": "string", "format": "date-time"}
        }
    }
    engine.analyze_schema(similar_schema)
    
    recommendations = engine.recommend_similar_schemas(schema)
    print(f"找到 {len(recommendations)} 个相似Schema:")
    for rec in recommendations:
        print(f"  - {rec.item_id}: {rec.score:.2%} 置信度 ({rec.reason})")
    
    # 示例3: 字段推荐
    print("\n" + "=" * 60)
    print("示例3: 字段推荐")
    print("=" * 60)
    
    partial = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"}
        }
    }
    
    field_recs = engine.recommend_fields(partial, context="user")
    print("推荐字段:")
    for rec in field_recs[:5]:
        print(f"  - {rec.item_id}: {rec.score:.2f} ({rec.reason})")
    
    # 示例4: 模板推荐
    print("\n" + "=" * 60)
    print("示例4: 模板推荐")
    print("=" * 60)
    
    template_recs = engine.recommend_templates("user profile management")
    print(f"场景 'user profile management' 的推荐模板:")
    for rec in template_recs:
        print(f"  - {rec.item_id}: {rec.score:.2%} 匹配度")


if __name__ == "__main__":
    main()
