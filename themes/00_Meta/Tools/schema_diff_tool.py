#!/usr/bin/env python3
"""
Schema Diff Tool
================

Schema差异比较工具，支持：
- 结构化差异分析
- 语义差异检测
- 变更影响分析
- 迁移脚本生成
- 可视化差异报告

Version: 2.2.0
"""

import json
import difflib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
from collections import defaultdict


class ChangeType(Enum):
    """变更类型"""
    ADDED = "added"           # 新增
    REMOVED = "removed"       # 删除
    MODIFIED = "modified"     # 修改
    MOVED = "moved"          # 移动
    UNCHANGED = "unchanged"   # 未变更


class ImpactLevel(Enum):
    """影响级别"""
    NONE = 0        # 无影响
    LOW = 1         # 低影响 (注释、格式)
    MEDIUM = 2      # 中等影响 (可选字段)
    HIGH = 3        # 高影响 (必填字段)
    BREAKING = 4    # 破坏性变更 (删除必填字段)


@dataclass
class DiffNode:
    """差异节点"""
    path: str
    change_type: ChangeType
    old_value: Any = None
    new_value: Any = None
    impact: ImpactLevel = ImpactLevel.NONE
    description: str = ""
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DiffReport:
    """差异报告"""
    source_id: str
    target_id: str
    summary: Dict[str, int] = field(default_factory=dict)
    changes: List[DiffNode] = field(default_factory=list)
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    migration_guide: List[str] = field(default_factory=list)


class SchemaDiffer:
    """Schema差异比较器"""
    
    def __init__(self, ignore_order: bool = True, ignore_descriptions: bool = False):
        self.ignore_order = ignore_order
        self.ignore_descriptions = ignore_descriptions
        self.changes: List[DiffNode] = []
    
    def diff(self, source: Dict, target: Dict, 
             source_name: str = "source", 
             target_name: str = "target") -> DiffReport:
        """
        比较两个Schema的差异
        
        Args:
            source: 源Schema
            target: 目标Schema
            source_name: 源标识
            target_name: 目标标识
        
        Returns:
            DiffReport: 差异报告
        """
        self.changes = []
        
        # 递归比较
        self._compare_values(source, target, "$")
        
        # 生成报告
        report = DiffReport(
            source_id=source_name,
            target_id=target_name,
            summary=self._generate_summary(),
            changes=self.changes,
            impact_analysis=self._analyze_impact(),
            migration_guide=self._generate_migration_guide()
        )
        
        return report
    
    def _compare_values(self, old: Any, new: Any, path: str):
        """递归比较值"""
        # 如果忽略描述且路径包含description，跳过
        if self.ignore_descriptions and "description" in path:
            return
        
        if isinstance(old, dict) and isinstance(new, dict):
            self._compare_dicts(old, new, path)
        elif isinstance(old, list) and isinstance(new, list):
            self._compare_lists(old, new, path)
        else:
            # 基本类型比较
            if old != new:
                self._add_change(path, ChangeType.MODIFIED, old, new)
    
    def _compare_dicts(self, old: Dict, new: Dict, path: str):
        """比较字典"""
        all_keys = set(old.keys()) | set(new.keys())
        
        for key in all_keys:
            new_path = f"{path}.{key}"
            
            if key not in old:
                # 新增
                self._add_change(new_path, ChangeType.ADDED, None, new[key])
            elif key not in new:
                # 删除
                self._add_change(new_path, ChangeType.REMOVED, old[key], None)
            else:
                # 递归比较
                self._compare_values(old[key], new[key], new_path)
    
    def _compare_lists(self, old: List, new: List, path: str):
        """比较列表"""
        if self.ignore_order:
            # 无序比较
            old_set = set(self._hashable(item) for item in old)
            new_set = set(self._hashable(item) for item in new)
            
            removed = old_set - new_set
            added = new_set - old_set
            
            for item in removed:
                self._add_change(f"{path}[]", ChangeType.REMOVED, item, None)
            
            for item in added:
                self._add_change(f"{path}[]", ChangeType.ADDED, None, item)
        else:
            # 有序比较
            max_len = max(len(old), len(new))
            for i in range(max_len):
                item_path = f"{path}[{i}]"
                if i >= len(old):
                    self._add_change(item_path, ChangeType.ADDED, None, new[i])
                elif i >= len(new):
                    self._add_change(item_path, ChangeType.REMOVED, old[i], None)
                else:
                    self._compare_values(old[i], new[i], item_path)
    
    def _hashable(self, item: Any) -> Union[str, tuple]:
        """转换为可哈希类型"""
        if isinstance(item, dict):
            return tuple(sorted((k, self._hashable(v)) for k, v in item.items()))
        elif isinstance(item, list):
            return tuple(self._hashable(i) for i in item)
        else:
            return str(item)
    
    def _add_change(self, path: str, change_type: ChangeType, 
                   old_val: Any, new_val: Any):
        """添加变更记录"""
        impact = self._calculate_impact(path, change_type, old_val, new_val)
        
        description = self._generate_description(path, change_type, old_val, new_val)
        suggestions = self._generate_suggestions(path, change_type, old_val, new_val)
        
        change = DiffNode(
            path=path,
            change_type=change_type,
            old_value=self._truncate(old_val),
            new_value=self._truncate(new_val),
            impact=impact,
            description=description,
            suggestions=suggestions
        )
        self.changes.append(change)
    
    def _calculate_impact(self, path: str, change_type: ChangeType,
                         old_val: Any, new_val: Any) -> ImpactLevel:
        """计算影响级别"""
        # 检查是否是required字段的变更
        if "required" in path:
            if change_type == ChangeType.REMOVED:
                return ImpactLevel.BREAKING
            elif change_type == ChangeType.ADDED:
                return ImpactLevel.HIGH
        
        # 检查类型变更
        if path.endswith(".type"):
            return ImpactLevel.HIGH
        
        # 检查属性删除
        if "properties." in path and change_type == ChangeType.REMOVED:
            return ImpactLevel.HIGH
        
        # 默认值变更
        if "default" in path:
            return ImpactLevel.MEDIUM
        
        # 描述变更
        if "description" in path:
            return ImpactLevel.LOW
        
        return ImpactLevel.MEDIUM
    
    def _generate_description(self, path: str, change_type: ChangeType,
                             old_val: Any, new_val: Any) -> str:
        """生成变更描述"""
        type_names = {
            ChangeType.ADDED: "新增",
            ChangeType.REMOVED: "删除",
            ChangeType.MODIFIED: "修改",
            ChangeType.MOVED: "移动"
        }
        
        desc = f"{type_names.get(change_type, '变更')} {path}"
        
        if change_type == ChangeType.MODIFIED:
            desc += f": {self._truncate(old_val)} → {self._truncate(new_val)}"
        
        return desc
    
    def _generate_suggestions(self, path: str, change_type: ChangeType,
                             old_val: Any, new_val: Any) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if change_type == ChangeType.REMOVED and "required" in path:
            suggestions.append("确保没有代码依赖此字段后再删除")
            suggestions.append("考虑先标记为废弃(deprecated)而非直接删除")
        
        if change_type == ChangeType.ADDED and "required" in path:
            suggestions.append("更新所有客户端以提供此必填字段")
            suggestions.append("考虑先作为可选字段，逐步过渡为必填")
        
        if ".type" in path:
            suggestions.append("验证所有数据符合新类型")
            suggestions.append("考虑数据迁移策略")
        
        return suggestions
    
    def _truncate(self, value: Any, max_len: int = 50) -> str:
        """截断值"""
        s = str(value)
        if len(s) > max_len:
            return s[:max_len] + "..."
        return s
    
    def _generate_summary(self) -> Dict[str, int]:
        """生成摘要"""
        summary = defaultdict(int)
        for change in self.changes:
            summary[change.change_type.value] += 1
            summary[f"impact_{change.impact.name.lower()}"] += 1
        return dict(summary)
    
    def _analyze_impact(self) -> Dict[str, Any]:
        """分析影响"""
        breaking = [c for c in self.changes if c.impact == ImpactLevel.BREAKING]
        high = [c for c in self.changes if c.impact == ImpactLevel.HIGH]
        medium = [c for c in self.changes if c.impact == ImpactLevel.MEDIUM]
        low = [c for c in self.changes if c.impact == ImpactLevel.LOW]
        
        return {
            "breaking_changes": len(breaking),
            "high_impact": len(high),
            "medium_impact": len(medium),
            "low_impact": len(low),
            "breaking_details": [
                {"path": c.path, "description": c.description} for c in breaking
            ],
            "recommendation": "需要版本升级" if breaking else "向后兼容" if not high else "需要审查"
        }
    
    def _generate_migration_guide(self) -> List[str]:
        """生成迁移指南"""
        guide = []
        
        breaking = [c for c in self.changes if c.impact == ImpactLevel.BREAKING]
        if breaking:
            guide.append("## 破坏性变更")
            guide.append("以下变更会破坏现有集成：")
            for c in breaking:
                guide.append(f"- {c.description}")
                for s in c.suggestions:
                    guide.append(f"  - {s}")
        
        required_additions = [c for c in self.changes 
                             if c.change_type == ChangeType.ADDED and "required" in c.path]
        if required_additions:
            guide.append("\n## 新增必填字段")
            guide.append("请更新客户端代码以提供以下字段：")
            for c in required_additions:
                guide.append(f"- {c.path}")
        
        return guide
    
    def generate_html_report(self, report: DiffReport, output_path: str):
        """生成HTML差异报告"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Schema Diff Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 15px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; 
                 box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-top: 0; color: #333; }}
        .metric {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .change {{ background: white; padding: 15px; margin: 10px 0; 
                   border-radius: 8px; border-left: 4px solid #ddd; }}
        .added {{ border-left-color: #28a745; background: #f0fff4; }}
        .removed {{ border-left-color: #dc3545; background: #fff5f5; }}
        .modified {{ border-left-color: #ffc107; background: #fffbf0; }}
        .breaking {{ border-left-color: #dc3545; background: #fff5f5; }}
        .high {{ border-left-color: #fd7e14; }}
        .path {{ font-family: monospace; font-weight: bold; color: #666; }}
        .value {{ font-family: monospace; background: #f8f9fa; padding: 5px; 
                  border-radius: 4px; margin: 5px 0; }}
        .suggestions {{ color: #666; font-size: 0.9em; margin-top: 10px; }}
        .impact-badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; 
                        font-size: 0.75em; font-weight: bold; margin-left: 10px; }}
        .impact-breaking {{ background: #dc3545; color: white; }}
        .impact-high {{ background: #fd7e14; color: white; }}
        .impact-medium {{ background: #ffc107; color: black; }}
        .impact-low {{ background: #28a745; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Schema Diff Report</h1>
        <p>Comparing: {report.source_id} → {report.target_id}</p>
    </div>
    
    <div class="summary">
        <div class="card">
            <h3>Total Changes</h3>
            <div class="metric">{sum(report.summary.values())}</div>
        </div>
        <div class="card">
            <h3>Added</h3>
            <div class="metric" style="color: #28a745;">{report.summary.get('added', 0)}</div>
        </div>
        <div class="card">
            <h3>Removed</h3>
            <div class="metric" style="color: #dc3545;">{report.summary.get('removed', 0)}</div>
        </div>
        <div class="card">
            <h3>Modified</h3>
            <div class="metric" style="color: #ffc107;">{report.summary.get('modified', 0)}</div>
        </div>
    </div>
    
    <div class="card">
        <h3>Impact Analysis</h3>
        <p><strong>Recommendation:</strong> {report.impact_analysis.get('recommendation', 'N/A')}</p>
        <ul>
            <li>🔴 Breaking: {report.impact_analysis.get('breaking_changes', 0)}</li>
            <li>🟠 High: {report.impact_analysis.get('high_impact', 0)}</li>
            <li>🟡 Medium: {report.impact_analysis.get('medium_impact', 0)}</li>
            <li>🟢 Low: {report.impact_analysis.get('low_impact', 0)}</li>
        </ul>
    </div>
    
    <h2>Detailed Changes</h2>
"""
        
        for change in report.changes:
            impact_class = f"impact-{change.impact.name.lower()}"
            change_class = change.change_type.value
            
            html += f"""
    <div class="change {change_class} {impact_class}">
        <div class="path">
            {change.path}
            <span class="impact-badge impact-{change.impact.name.lower()}">{change.impact.name}</span>
        </div>
        <div>{change.description}</div>
        {f'<div class="value">- {change.old_value}</div>' if change.old_value else ''}
        {f'<div class="value">+ {change.new_value}</div>' if change.new_value else ''}
        {f'<div class="suggestions">💡 {"; ".join(change.suggestions)}</div>' if change.suggestions else ''}
    </div>
"""
        
        if report.migration_guide:
            html += """
    <h2>Migration Guide</h2>
    <div class="card">
"""
            for line in report.migration_guide:
                html += f"        <p>{line}</p>\n"
            html += "    </div>"
        
        html += """
</body>
</html>
"""
        
        Path(output_path).write_text(html, encoding='utf-8')
        return output_path


def main():
    """示例用法"""
    differ = SchemaDiffer()
    
    # 示例Schema
    old_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"}
        },
        "required": ["name"]
    }
    
    new_schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0},
            "phone": {"type": "string"},  # 新增
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "email"]  # email变为必填
    }
    
    # 比较
    report = differ.diff(old_schema, new_schema, "v1.0", "v2.0")
    
    # 打印摘要
    print("Schema Diff Report")
    print("=" * 60)
    print(f"Total changes: {sum(report.summary.values())}")
    print(f"Added: {report.summary.get('added', 0)}")
    print(f"Removed: {report.summary.get('removed', 0)}")
    print(f"Modified: {report.summary.get('modified', 0)}")
    print()
    print("Impact Analysis:")
    print(f"  Breaking: {report.impact_analysis.get('breaking_changes', 0)}")
    print(f"  High: {report.impact_analysis.get('high_impact', 0)}")
    print(f"  Recommendation: {report.impact_analysis.get('recommendation', 'N/A')}")
    
    # 生成HTML报告
    output = differ.generate_html_report(report, "schema_diff_report.html")
    print(f"\n✅ HTML报告已生成: {output}")


if __name__ == "__main__":
    main()
