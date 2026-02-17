#!/usr/bin/env python3
"""
Quality Analyzer
================

质量分析工具，提供：
- Schema质量评分
- 深度问题检测
- 性能影响分析
- 可维护性评估
- 改进建议生成

Version: 2.3.0
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict


class QualityCategory(Enum):
    """质量类别"""
    STRUCTURE = "structure"
    DOCUMENTATION = "documentation"
    CONSTRAINTS = "constraints"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"


class Severity(Enum):
    """问题严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityIssue:
    """质量问题"""
    category: QualityCategory
    severity: Severity
    message: str
    path: str
    suggestion: str
    rule_id: str


@dataclass
class QualityScore:
    """质量分数"""
    category: QualityCategory
    score: float  # 0-100
    weight: float
    issues: List[QualityIssue] = field(default_factory=list)


@dataclass
class QualityReport:
    """质量报告"""
    overall_score: float
    total_issues: int
    category_scores: Dict[QualityCategory, QualityScore]
    critical_issues: List[QualityIssue]
    recommendations: List[str]


class QualityAnalyzer:
    """Schema质量分析器"""
    
    # 类别权重
    CATEGORY_WEIGHTS = {
        QualityCategory.STRUCTURE: 0.20,
        QualityCategory.DOCUMENTATION: 0.15,
        QualityCategory.CONSTRAINTS: 0.20,
        QualityCategory.PERFORMANCE: 0.15,
        QualityCategory.SECURITY: 0.15,
        QualityCategory.MAINTAINABILITY: 0.15
    }
    
    def __init__(self):
        self.rules = self._initialize_rules()
        self.metrics = defaultdict(float)
    
    def _initialize_rules(self) -> List[Dict]:
        """初始化质量规则"""
        return [
            # 结构规则
            {
                "id": "STRUCT-001",
                "category": QualityCategory.STRUCTURE,
                "severity": Severity.CRITICAL,
                "check": lambda s: "$schema" in s or "type" in s,
                "message": "Schema缺少$schema或type声明",
                "suggestion": "添加'$schema'声明和/或'type'字段"
            },
            {
                "id": "STRUCT-002",
                "category": QualityCategory.STRUCTURE,
                "severity": Severity.HIGH,
                "check": lambda s: not self._has_circular_refs(s),
                "message": "检测到循环引用",
                "suggestion": "使用ID引用或重构嵌套结构"
            },
            {
                "id": "STRUCT-003",
                "category": QualityCategory.STRUCTURE,
                "severity": Severity.MEDIUM,
                "check": lambda s: self._count_depth(s) <= 5,
                "message": "嵌套层级过深(>5层)",
                "suggestion": "考虑扁平化结构或使用引用"
            },
            
            # 文档规则
            {
                "id": "DOC-001",
                "category": QualityCategory.DOCUMENTATION,
                "severity": Severity.MEDIUM,
                "check": lambda s: "description" in s,
                "message": "Schema缺少描述",
                "suggestion": "添加description字段说明Schema用途"
            },
            {
                "id": "DOC-002",
                "category": QualityCategory.DOCUMENTATION,
                "severity": Severity.LOW,
                "check": lambda s: self._has_field_descriptions(s),
                "message": "部分字段缺少描述",
                "suggestion": "为所有字段添加description"
            },
            {
                "id": "DOC-003",
                "category": QualityCategory.DOCUMENTATION,
                "severity": Severity.LOW,
                "check": lambda s: "examples" in s or "example" in s,
                "message": "缺少示例数据",
                "suggestion": "添加examples字段展示预期数据"
            },
            
            # 约束规则
            {
                "id": "CONST-001",
                "category": QualityCategory.CONSTRAINTS,
                "severity": Severity.HIGH,
                "check": lambda s: self._has_required_fields(s),
                "message": "对象类型缺少required字段定义",
                "suggestion": "明确哪些字段是必需的"
            },
            {
                "id": "CONST-002",
                "category": QualityCategory.CONSTRAINTS,
                "severity": Severity.MEDIUM,
                "check": lambda s: self._has_string_constraints(s),
                "message": "字符串字段缺少长度约束",
                "suggestion": "添加minLength和maxLength"
            },
            {
                "id": "CONST-003",
                "category": QualityCategory.CONSTRAINTS,
                "severity": Severity.MEDIUM,
                "check": lambda s: self._has_number_constraints(s),
                "message": "数值字段缺少范围约束",
                "suggestion": "添加minimum和maximum"
            },
            {
                "id": "CONST-004",
                "category": QualityCategory.CONSTRAINTS,
                "severity": Severity.LOW,
                "check": lambda s: self._has_enum_constraints(s),
                "message": "可考虑使用enum约束字符串取值",
                "suggestion": "对于有限取值的字段使用enum"
            },
            
            # 性能规则
            {
                "id": "PERF-001",
                "category": QualityCategory.PERFORMANCE,
                "severity": Severity.HIGH,
                "check": lambda s: self._count_properties(s) <= 50,
                "message": "属性数量过多(>50)",
                "suggestion": "考虑拆分为多个子Schema"
            },
            {
                "id": "PERF-002",
                "category": QualityCategory.PERFORMANCE,
                "severity": Severity.MEDIUM,
                "check": lambda s: not self._has_expensive_patterns(s),
                "message": "包含性能开销大的pattern",
                "suggestion": "优化正则表达式或移除不必要的pattern"
            },
            {
                "id": "PERF-003",
                "category": QualityCategory.PERFORMANCE,
                "severity": Severity.LOW,
                "check": lambda s: self._count_refs(s) <= 20,
                "message": "引用数量过多",
                "suggestion": "考虑内联部分引用"
            },
            
            # 安全规则
            {
                "id": "SEC-001",
                "category": QualityCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "check": lambda s: not self._has_sensitive_fields(s),
                "message": "可能包含敏感字段但缺少约束",
                "suggestion": "为敏感字段添加适当的约束和加密"
            },
            {
                "id": "SEC-002",
                "category": QualityCategory.SECURITY,
                "severity": Severity.HIGH,
                "check": lambda s: self._has_string_length_limits(s),
                "message": "字符串字段无长度限制",
                "suggestion": "添加maxLength防止DoS攻击"
            },
            {
                "id": "SEC-003",
                "category": QualityCategory.SECURITY,
                "severity": Severity.MEDIUM,
                "check": lambda s: not self._allows_additional_properties(s),
                "message": "允许额外属性可能带来风险",
                "suggestion": "设置additionalProperties: false"
            },
            
            # 可维护性规则
            {
                "id": "MAINT-001",
                "category": QualityCategory.MAINTAINABILITY,
                "severity": Severity.MEDIUM,
                "check": lambda s: "$id" in s or "title" in s,
                "message": "缺少$id或title标识",
                "suggestion": "添加唯一标识便于引用"
            },
            {
                "id": "MAINT-002",
                "category": QualityCategory.MAINTAINABILITY,
                "severity": Severity.LOW,
                "check": lambda s: not self._has_duplicate_patterns(s),
                "message": "检测到重复模式",
                "suggestion": "提取公共定义为单独Schema"
            },
            {
                "id": "MAINT-003",
                "category": QualityCategory.MAINTAINABILITY,
                "severity": Severity.LOW,
                "check": lambda s: self._has_version_info(s),
                "message": "缺少版本信息",
                "suggestion": "添加版本字段便于演进管理"
            }
        ]
    
    def analyze(self, schema: Dict, path: str = "$") -> QualityReport:
        """
        分析Schema质量
        
        Args:
            schema: 待分析的Schema
            path: 当前路径
        
        Returns:
            QualityReport: 质量报告
        """
        issues = self._collect_issues(schema, path)
        category_scores = self._calculate_scores(issues)
        overall_score = self._calculate_overall_score(category_scores)
        
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        recommendations = self._generate_recommendations(issues)
        
        return QualityReport(
            overall_score=overall_score,
            total_issues=len(issues),
            category_scores=category_scores,
            critical_issues=critical_issues,
            recommendations=recommendations
        )
    
    def _collect_issues(self, schema: Dict, path: str) -> List[QualityIssue]:
        """收集所有质量问题"""
        issues = []
        
        for rule in self.rules:
            try:
                if not rule["check"](schema):
                    issues.append(QualityIssue(
                        category=rule["category"],
                        severity=rule["severity"],
                        message=rule["message"],
                        path=path,
                        suggestion=rule["suggestion"],
                        rule_id=rule["id"]
                    ))
            except Exception:
                pass
        
        # 递归检查嵌套结构
        if isinstance(schema, dict):
            if "properties" in schema:
                for prop, subschema in schema["properties"].items():
                    if isinstance(subschema, dict):
                        sub_issues = self._collect_issues(
                            subschema, 
                            f"{path}.properties.{prop}"
                        )
                        issues.extend(sub_issues)
            
            if "items" in schema and isinstance(schema["items"], dict):
                sub_issues = self._collect_issues(
                    schema["items"],
                    f"{path}.items"
                )
                issues.extend(sub_issues)
        
        return issues
    
    def _calculate_scores(self, issues: List[QualityIssue]) -> Dict[QualityCategory, QualityScore]:
        """计算各类别分数"""
        category_issues = defaultdict(list)
        for issue in issues:
            category_issues[issue.category].append(issue)
        
        scores = {}
        for category in QualityCategory:
            cat_issues = category_issues.get(category, [])
            
            # 根据严重级别扣分
            deductions = {
                Severity.CRITICAL: 30,
                Severity.HIGH: 15,
                Severity.MEDIUM: 8,
                Severity.LOW: 3,
                Severity.INFO: 1
            }
            
            total_deduction = sum(
                deductions.get(i.severity, 0) for i in cat_issues
            )
            
            score = max(0, 100 - total_deduction)
            
            scores[category] = QualityScore(
                category=category,
                score=score,
                weight=self.CATEGORY_WEIGHTS[category],
                issues=cat_issues
            )
        
        return scores
    
    def _calculate_overall_score(self, category_scores: Dict[QualityCategory, QualityScore]) -> float:
        """计算总体分数"""
        weighted_sum = sum(
            s.score * s.weight for s in category_scores.values()
        )
        return round(weighted_sum, 1)
    
    def _generate_recommendations(self, issues: List[QualityIssue]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 按严重级别排序
        sorted_issues = sorted(
            issues,
            key=lambda i: (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, 
                          Severity.LOW, Severity.INFO).index(i.severity)
        )
        
        seen = set()
        for issue in sorted_issues[:10]:  # 最多10条建议
            rec = f"[{issue.severity.value.upper()}] {issue.message}: {issue.suggestion}"
            if rec not in seen:
                seen.add(rec)
                recommendations.append(rec)
        
        return recommendations
    
    # 辅助检查方法
    def _has_circular_refs(self, schema: Dict, seen: Set = None) -> bool:
        """检查循环引用"""
        if seen is None:
            seen = set()
        
        if not isinstance(schema, dict):
            return False
        
        schema_id = schema.get("$id") or id(schema)
        if schema_id in seen:
            return True
        
        seen.add(schema_id)
        
        for key, value in schema.items():
            if isinstance(value, dict):
                if self._has_circular_refs(value, seen.copy()):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if self._has_circular_refs(item, seen.copy()):
                            return True
        
        return False
    
    def _count_depth(self, schema: Dict, current_depth: int = 0) -> int:
        """计算嵌套深度"""
        if not isinstance(schema, dict) or current_depth > 10:
            return current_depth
        
        max_depth = current_depth
        
        for key, value in schema.items():
            if isinstance(value, dict):
                depth = self._count_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        depth = self._count_depth(item, current_depth + 1)
                        max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _has_field_descriptions(self, schema: Dict) -> bool:
        """检查字段是否有描述"""
        properties = schema.get("properties", {})
        if not properties:
            return True
        
        described = sum(1 for p in properties.values() 
                       if isinstance(p, dict) and "description" in p)
        return described >= len(properties) * 0.5
    
    def _has_required_fields(self, schema: Dict) -> bool:
        """检查是否有required定义"""
        if schema.get("type") == "object":
            return "required" in schema
        return True
    
    def _has_string_constraints(self, schema: Dict) -> bool:
        """检查字符串约束"""
        properties = schema.get("properties", {})
        for prop, definition in properties.items():
            if isinstance(definition, dict) and definition.get("type") == "string":
                if "minLength" not in definition and "maxLength" not in definition:
                    if "format" not in definition:
                        return False
        return True
    
    def _has_number_constraints(self, schema: Dict) -> bool:
        """检查数值约束"""
        properties = schema.get("properties", {})
        for prop, definition in properties.items():
            if isinstance(definition, dict) and definition.get("type") in ["number", "integer"]:
                if "minimum" not in definition and "maximum" not in definition:
                    return False
        return True
    
    def _has_enum_constraints(self, schema: Dict) -> bool:
        """检查是否有适当的enum约束"""
        return True  # 信息级别，不强制
    
    def _count_properties(self, schema: Dict) -> int:
        """计算属性数量"""
        return len(schema.get("properties", {}))
    
    def _has_expensive_patterns(self, schema: Dict) -> bool:
        """检查性能开销大的模式"""
        schema_str = json.dumps(schema)
        # 检测回溯严重的正则
        dangerous_patterns = ["(.*)*", "(a+)+"]
        return any(p in schema_str for p in dangerous_patterns)
    
    def _count_refs(self, schema: Dict) -> int:
        """计算引用数量"""
        count = 0
        if isinstance(schema, dict):
            if "$ref" in schema:
                count += 1
            for value in schema.values():
                if isinstance(value, (dict, list)):
                    count += self._count_refs(value)
        elif isinstance(schema, list):
            for item in schema:
                count += self._count_refs(item)
        return count
    
    def _has_sensitive_fields(self, schema: Dict) -> bool:
        """检查敏感字段"""
        sensitive_keywords = ["password", "secret", "token", "key", "credential"]
        schema_str = json.dumps(schema).lower()
        return any(kw in schema_str for kw in sensitive_keywords)
    
    def _has_string_length_limits(self, schema: Dict) -> bool:
        """检查字符串长度限制"""
        return self._has_string_constraints(schema)
    
    def _allows_additional_properties(self, schema: Dict) -> bool:
        """检查是否允许额外属性"""
        return schema.get("additionalProperties", True) is True
    
    def _has_duplicate_patterns(self, schema: Dict) -> bool:
        """检查重复模式"""
        patterns = []
        self._extract_patterns(schema, patterns)
        return len(patterns) != len(set(json.dumps(p, sort_keys=True) for p in patterns))
    
    def _extract_patterns(self, schema: Dict, patterns: List):
        """提取模式用于重复检测"""
        if not isinstance(schema, dict):
            return
        
        if schema.get("type") == "object" and "properties" in schema:
            props = tuple(sorted(schema["properties"].keys()))
            patterns.append(props)
        
        for value in schema.values():
            if isinstance(value, dict):
                self._extract_patterns(value, patterns)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._extract_patterns(item, patterns)
    
    def _has_version_info(self, schema: Dict) -> bool:
        """检查版本信息"""
        return any(keyword in json.dumps(schema).lower() 
                  for keyword in ["version", "v1", "v2"])


def main():
    """示例用法"""
    analyzer = QualityAnalyzer()
    
    # 示例Schema
    schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "$id": "user-profile",
        "type": "object",
        "description": "用户资料Schema",
        "properties": {
            "id": {
                "type": "string",
                "description": "用户ID"
            },
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 50,
                "description": "用户名"
            },
            "email": {
                "type": "string",
                "format": "email",
                "description": "邮箱"
            },
            "age": {
                "type": "integer",
                "description": "年龄"
            },
            "password": {
                "type": "string",
                "description": "密码"
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "createdAt": {"type": "string"},
                    "updatedAt": {"type": "string"}
                }
            }
        },
        "required": ["id", "username"]
    }
    
    print("=" * 60)
    print("Schema质量分析报告")
    print("=" * 60)
    
    report = analyzer.analyze(schema)
    
    print(f"\n总体质量分数: {report.overall_score}/100")
    print(f"发现问题数量: {report.total_issues}")
    print(f"严重问题数量: {len(report.critical_issues)}")
    
    print("\n各维度评分:")
    for category, score in report.category_scores.items():
        status = "✓" if score.score >= 80 else "⚠" if score.score >= 60 else "✗"
        print(f"  {status} {category.value:15} {score.score:5.1f}/100 ({len(score.issues)}个问题)")
    
    if report.critical_issues:
        print("\n严重问题:")
        for issue in report.critical_issues:
            print(f"  ✗ [{issue.rule_id}] {issue.message}")
            print(f"    路径: {issue.path}")
            print(f"    建议: {issue.suggestion}")
    
    print("\n改进建议:")
    for i, rec in enumerate(report.recommendations[:5], 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
