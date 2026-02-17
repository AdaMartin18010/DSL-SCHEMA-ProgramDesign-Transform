#!/usr/bin/env python3
"""
Schema Comparator
=================

Schema比较工具，提供：
- 深度差异分析
- 可视化差异报告
- 版本对比
- 影响分析
- 合并建议

Version: 2.3.0
"""

import json
import difflib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict


class DifferenceType(Enum):
    """差异类型"""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"
    TYPE_CHANGED = "type_changed"
    CONSTRAINT_CHANGED = "constraint_changed"


class ImpactLevel(Enum):
    """影响级别"""
    BREAKING = "breaking"
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


@dataclass
class Difference:
    """差异项"""
    type: DifferenceType
    path: str
    old_value: Any = None
    new_value: Any = None
    description: str = ""
    impact: ImpactLevel = ImpactLevel.NONE


@dataclass
class ComparisonReport:
    """比较报告"""
    schema_a_name: str
    schema_b_name: str
    differences: List[Difference]
    similarity_score: float  # 0-1
    structural_similarity: float
    semantic_similarity: float
    breaking_changes: List[Difference]
    recommendations: List[str]


class SchemaComparator:
    """Schema比较器"""
    
    def __init__(self):
        self.impact_rules = self._initialize_impact_rules()
    
    def _initialize_impact_rules(self) -> Dict:
        """初始化影响规则"""
        return {
            "required_removed": ImpactLevel.BREAKING,
            "type_changed": ImpactLevel.BREAKING,
            "property_removed": ImpactLevel.BREAKING,
            "required_added": ImpactLevel.MAJOR,
            "constraint_tightened": ImpactLevel.MAJOR,
            "property_added": ImpactLevel.MINOR,
            "description_added": ImpactLevel.PATCH,
            "example_added": ImpactLevel.PATCH
        }
    
    def compare(self, schema_a: Dict, schema_b: Dict,
                name_a: str = "Schema A", name_b: str = "Schema B") -> ComparisonReport:
        """
        比较两个Schema
        
        Args:
            schema_a: 第一个Schema
            schema_b: 第二个Schema
            name_a: Schema A的名称
            name_b: Schema B的名称
        
        Returns:
            ComparisonReport: 比较报告
        """
        differences = []
        
        # 结构比较
        structural_diffs = self._compare_structure(schema_a, schema_b, "$")
        differences.extend(structural_diffs)
        
        # 语义比较
        semantic_diffs = self._compare_semantics(schema_a, schema_b, "$")
        differences.extend(semantic_diffs)
        
        # 计算相似度
        similarity = self._calculate_similarity(schema_a, schema_b)
        structural_sim = self._calculate_structural_similarity(schema_a, schema_b)
        semantic_sim = self._calculate_semantic_similarity(schema_a, schema_b)
        
        # 识别破坏性变更
        breaking = [d for d in differences if d.impact == ImpactLevel.BREAKING]
        
        # 生成建议
        recommendations = self._generate_recommendations(differences)
        
        return ComparisonReport(
            schema_a_name=name_a,
            schema_b_name=name_b,
            differences=differences,
            similarity_score=similarity,
            structural_similarity=structural_sim,
            semantic_similarity=semantic_sim,
            breaking_changes=breaking,
            recommendations=recommendations
        )
    
    def _compare_structure(self, a: Dict, b: Dict, path: str) -> List[Difference]:
        """比较结构差异"""
        differences = []
        
        if not isinstance(a, dict) or not isinstance(b, dict):
            if a != b:
                differences.append(Difference(
                    type=DifferenceType.MODIFIED,
                    path=path,
                    old_value=a,
                    new_value=b,
                    description=f"Value changed at {path}",
                    impact=self._assess_impact(path, a, b)
                ))
            return differences
        
        # 获取所有键
        keys_a = set(a.keys())
        keys_b = set(b.keys())
        
        # 新增的键
        for key in keys_b - keys_a:
            differences.append(Difference(
                type=DifferenceType.ADDED,
                path=f"{path}.{key}",
                new_value=b[key],
                description=f"Added '{key}' at {path}",
                impact=self._assess_impact(f"{path}.{key}", None, b[key])
            ))
        
        # 删除的键
        for key in keys_a - keys_b:
            differences.append(Difference(
                type=DifferenceType.REMOVED,
                path=f"{path}.{key}",
                old_value=a[key],
                description=f"Removed '{key}' from {path}",
                impact=self._assess_impact(f"{path}.{key}", a[key], None)
            ))
        
        # 修改的键
        for key in keys_a & keys_b:
            new_path = f"{path}.{key}"
            
            if key == "type":
                if a[key] != b[key]:
                    differences.append(Difference(
                        type=DifferenceType.TYPE_CHANGED,
                        path=new_path,
                        old_value=a[key],
                        new_value=b[key],
                        description=f"Type changed from '{a[key]}' to '{b[key]}'",
                        impact=ImpactLevel.BREAKING
                    ))
            elif key in ["minimum", "maximum", "minLength", "maxLength", "pattern"]:
                if a[key] != b[key]:
                    differences.append(Difference(
                        type=DifferenceType.CONSTRAINT_CHANGED,
                        path=new_path,
                        old_value=a[key],
                        new_value=b[key],
                        description=f"Constraint '{key}' changed",
                        impact=self._assess_constraint_impact(key, a[key], b[key])
                    ))
            elif isinstance(a[key], dict) and isinstance(b[key], dict):
                sub_diffs = self._compare_structure(a[key], b[key], new_path)
                differences.extend(sub_diffs)
            elif a[key] != b[key]:
                differences.append(Difference(
                    type=DifferenceType.MODIFIED,
                    path=new_path,
                    old_value=a[key],
                    new_value=b[key],
                    description=f"Modified '{key}'",
                    impact=self._assess_impact(new_path, a[key], b[key])
                ))
        
        return differences
    
    def _compare_semantics(self, a: Dict, b: Dict, path: str) -> List[Difference]:
        """比较语义差异"""
        differences = []
        
        # 比较描述
        desc_a = a.get("description", "")
        desc_b = b.get("description", "")
        
        if not desc_a and desc_b:
            differences.append(Difference(
                type=DifferenceType.ADDED,
                path=f"{path}.description",
                new_value=desc_b,
                description="Added description",
                impact=ImpactLevel.PATCH
            ))
        
        # 比较标题
        title_a = a.get("title", "")
        title_b = b.get("title", "")
        
        if title_a != title_b and title_b:
            differences.append(Difference(
                type=DifferenceType.MODIFIED,
                path=f"{path}.title",
                old_value=title_a,
                new_value=title_b,
                description=f"Title changed",
                impact=ImpactLevel.MINOR
            ))
        
        return differences
    
    def _assess_impact(self, path: str, old_val: Any, new_val: Any) -> ImpactLevel:
        """评估变更影响"""
        # 检查路径中的关键字
        if "required" in path:
            if old_val and not new_val:
                return ImpactLevel.BREAKING
            elif not old_val and new_val:
                return ImpactLevel.MAJOR
        
        if "properties" in path:
            if old_val is None and new_val is not None:
                return ImpactLevel.MINOR  # 新增属性
            elif old_val is not None and new_val is None:
                return ImpactLevel.BREAKING  # 删除属性
        
        return ImpactLevel.NONE
    
    def _assess_constraint_impact(self, constraint: str, old_val: Any, 
                                   new_val: Any) -> ImpactLevel:
        """评估约束变更影响"""
        # 更严格的约束
        tightening_constraints = ["minimum", "minLength", "pattern"]
        
        if constraint in tightening_constraints:
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                if new_val > old_val:
                    return ImpactLevel.MAJOR
        
        if constraint == "maximum" or constraint == "maxLength":
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                if new_val < old_val:
                    return ImpactLevel.MAJOR
        
        return ImpactLevel.MINOR
    
    def _calculate_similarity(self, a: Dict, b: Dict) -> float:
        """计算整体相似度"""
        a_json = json.dumps(a, sort_keys=True)
        b_json = json.dumps(b, sort_keys=True)
        
        # 使用序列匹配
        matcher = difflib.SequenceMatcher(None, a_json, b_json)
        return matcher.ratio()
    
    def _calculate_structural_similarity(self, a: Dict, b: Dict) -> float:
        """计算结构相似度"""
        a_props = set(self._get_all_paths(a))
        b_props = set(self._get_all_paths(b))
        
        if not a_props and not b_props:
            return 1.0
        
        intersection = len(a_props & b_props)
        union = len(a_props | b_props)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_semantic_similarity(self, a: Dict, b: Dict) -> float:
        """计算语义相似度"""
        # 比较描述、标题等语义信息
        a_desc = a.get("description", "")
        b_desc = b.get("description", "")
        
        if not a_desc or not b_desc:
            return 0.5  # 中性
        
        matcher = difflib.SequenceMatcher(None, a_desc, b_desc)
        return matcher.ratio()
    
    def _get_all_paths(self, obj: Dict, prefix: str = "") -> List[str]:
        """获取对象的所有路径"""
        paths = []
        
        if not isinstance(obj, dict):
            return paths
        
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.append(path)
            
            if isinstance(value, dict):
                paths.extend(self._get_all_paths(value, path))
        
        return paths
    
    def _generate_recommendations(self, differences: List[Difference]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        breaking_count = sum(1 for d in differences if d.impact == ImpactLevel.BREAKING)
        major_count = sum(1 for d in differences if d.impact == ImpactLevel.MAJOR)
        
        if breaking_count > 0:
            recommendations.append(
                f"警告: 发现 {breaking_count} 个破坏性变更，需要版本号主版本升级 (X.0.0)"
            )
        elif major_count > 0:
            recommendations.append(
                f"建议: 发现 {major_count} 个重要变更，建议次版本升级 (0.X.0)"
            )
        
        # 针对具体差异的建议
        for diff in differences:
            if diff.type == DifferenceType.TYPE_CHANGED:
                recommendations.append(
                    f"类型变更 '{diff.path}': 确保所有使用者都已更新"
                )
            elif diff.type == DifferenceType.REMOVED and "properties" in diff.path:
                recommendations.append(
                    f"属性删除 '{diff.path}': 确认没有遗留依赖"
                )
        
        return recommendations
    
    def generate_diff_visualization(self, report: ComparisonReport) -> str:
        """
        生成可视化差异报告
        
        Args:
            report: 比较报告
        
        Returns:
            str: Markdown格式的可视化报告
        """
        lines = [
            f"# Schema 对比报告: {report.schema_a_name} vs {report.schema_b_name}",
            "",
            "## 相似度概览",
            "",
            f"- **整体相似度**: {report.similarity_score:.1%}",
            f"- **结构相似度**: {report.structural_similarity:.1%}",
            f"- **语义相似度**: {report.semantic_similarity:.1%}",
            "",
            "## 差异统计",
            "",
        ]
        
        # 统计各类差异
        type_counts = defaultdict(int)
        impact_counts = defaultdict(int)
        
        for diff in report.differences:
            type_counts[diff.type.value] += 1
            impact_counts[diff.impact.value] += 1
        
        lines.append("### 按类型")
        for diff_type, count in sorted(type_counts.items()):
            lines.append(f"- {diff_type}: {count}")
        
        lines.extend(["", "### 按影响级别"])
        for impact, count in sorted(impact_counts.items(), 
                                    key=lambda x: ["breaking", "major", "minor", "patch", "none"].index(x[0])):
            emoji = {"breaking": "🔴", "major": "🟠", "minor": "🟡", "patch": "🟢", "none": "⚪"}.get(impact, "⚪")
            lines.append(f"- {emoji} {impact}: {count}")
        
        # 破坏性变更
        if report.breaking_changes:
            lines.extend(["", "## 🔴 破坏性变更", ""])
            for diff in report.breaking_changes:
                lines.append(f"- **{diff.path}**: {diff.description}")
        
        # 详细差异
        lines.extend(["", "## 详细差异", ""])
        for diff in report.differences:
            emoji = {
                DifferenceType.ADDED: "➕",
                DifferenceType.REMOVED: "➖",
                DifferenceType.MODIFIED: "📝",
                DifferenceType.TYPE_CHANGED: "🔄",
                DifferenceType.CONSTRAINT_CHANGED: "🔒",
                DifferenceType.MOVED: "📦"
            }.get(diff.type, "📝")
            
            impact_emoji = {
                ImpactLevel.BREAKING: "🔴",
                ImpactLevel.MAJOR: "🟠",
                ImpactLevel.MINOR: "🟡",
                ImpactLevel.PATCH: "🟢",
                ImpactLevel.NONE: "⚪"
            }.get(diff.impact, "⚪")
            
            lines.append(f"### {emoji} {diff.path} {impact_emoji}")
            lines.append(f"- **类型**: {diff.type.value}")
            lines.append(f"- **描述**: {diff.description}")
            if diff.old_value is not None:
                lines.append(f"- **旧值**: `{json.dumps(diff.old_value)}`")
            if diff.new_value is not None:
                lines.append(f"- **新值**: `{json.dumps(diff.new_value)}`")
            lines.append("")
        
        # 建议
        if report.recommendations:
            lines.extend(["## 建议", ""])
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
        
        return "\n".join(lines)
    
    def merge_schemas(self, schema_a: Dict, schema_b: Dict,
                     strategy: str = "union") -> Dict:
        """
        合并两个Schema
        
        Args:
            schema_a: 第一个Schema
            schema_b: 第二个Schema
            strategy: 合并策略 (union, intersection, prefer_a, prefer_b)
        
        Returns:
            Dict: 合并后的Schema
        """
        if strategy == "union":
            return self._merge_union(schema_a, schema_b)
        elif strategy == "intersection":
            return self._merge_intersection(schema_a, schema_b)
        elif strategy == "prefer_a":
            return self._merge_prefer_a(schema_a, schema_b)
        elif strategy == "prefer_b":
            return self._merge_prefer_b(schema_a, schema_b)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _merge_union(self, a: Dict, b: Dict) -> Dict:
        """合并所有字段（并集）"""
        result = copy.deepcopy(a)
        
        for key, value in b.items():
            if key not in result:
                result[key] = copy.deepcopy(value)
            elif isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_union(result[key], value)
        
        return result
    
    def _merge_intersection(self, a: Dict, b: Dict) -> Dict:
        """合并公共字段（交集）"""
        result = {}
        
        for key in a:
            if key in b:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    result[key] = self._merge_intersection(a[key], b[key])
                else:
                    result[key] = a[key]
        
        return result
    
    def _merge_prefer_a(self, a: Dict, b: Dict) -> Dict:
        """优先使用A"""
        return copy.deepcopy(a)
    
    def _merge_prefer_b(self, a: Dict, b: Dict) -> Dict:
        """优先使用B"""
        return copy.deepcopy(b)


import copy


def main():
    """示例用法"""
    comparator = SchemaComparator()
    
    # 定义两个Schema进行比较
    schema_v1 = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "$id": "user-v1",
        "title": "User Schema",
        "description": "User profile schema",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "age": {"type": "string"}
        },
        "required": ["id", "name"]
    }
    
    schema_v2 = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "$id": "user-v2",
        "title": "User Profile Schema",
        "description": "Enhanced user profile schema with email support",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "fullName": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["id", "fullName", "email"]
    }
    
    print("=" * 60)
    print("Schema 对比分析")
    print("=" * 60)
    
    report = comparator.compare(schema_v1, schema_v2, "User v1", "User v2")
    
    print(f"\n整体相似度: {report.similarity_score:.1%}")
    print(f"结构相似度: {report.structural_similarity:.1%}")
    print(f"语义相似度: {report.semantic_similarity:.1%}")
    
    print(f"\n发现 {len(report.differences)} 个差异:")
    print(f"  - 破坏性变更: {len(report.breaking_changes)}")
    
    print("\n详细差异:")
    for diff in report.differences[:5]:
        print(f"  [{diff.type.value}] {diff.path}")
        print(f"    {diff.description}")
        print(f"    影响: {diff.impact.value}")
    
    # 生成可视化报告
    print("\n" + "=" * 60)
    print("生成可视化报告")
    print("=" * 60)
    
    viz = comparator.generate_diff_visualization(report)
    print(viz[:1500] + "...")


if __name__ == "__main__":
    main()
