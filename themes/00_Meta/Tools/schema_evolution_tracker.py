#!/usr/bin/env python3
"""
Schema Evolution Tracker
========================

Schema演化追踪器，用于：
- 版本历史管理
- 变更追踪
- 迁移脚本生成
- 兼容性分析
- 演化路径可视化

Version: 2.2.0
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict


class VersionChangeType(Enum):
    """版本变更类型"""
    MAJOR = "major"      # 破坏性变更
    MINOR = "minor"      # 向后兼容的功能添加
    PATCH = "patch"      # 向后兼容的问题修复


class CompatibilityType(Enum):
    """兼容性类型"""
    FULL = "full"           # 完全兼容
    BACKWARD = "backward"   # 向后兼容
    FORWARD = "forward"     # 向前兼容
    NONE = "none"          # 不兼容


@dataclass
class SchemaVersion:
    """Schema版本"""
    version: str
    timestamp: datetime
    hash: str
    author: str
    message: str
    changes: List[Dict]
    schema: Dict


@dataclass
class EvolutionPath:
    """演化路径"""
    from_version: str
    to_version: str
    change_type: VersionChangeType
    compatibility: CompatibilityType
    migration_steps: List[str]
    breaking_changes: List[str]


class SchemaEvolutionTracker:
    """Schema演化追踪器"""
    
    def __init__(self, history_dir: str = ".schema_history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.versions: List[SchemaVersion] = []
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        if not self.history_dir.exists():
            return
        
        for file in sorted(self.history_dir.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding='utf-8'))
                version = SchemaVersion(
                    version=data["version"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    hash=data["hash"],
                    author=data.get("author", "unknown"),
                    message=data.get("message", ""),
                    changes=data.get("changes", []),
                    schema=data.get("schema", {})
                )
                self.versions.append(version)
            except Exception:
                pass
    
    def commit(self, schema: Dict, version: str, author: str = "", 
              message: str = "") -> SchemaVersion:
        """
        提交新版本
        
        Args:
            schema: Schema内容
            version: 版本号
            author: 作者
            message: 提交信息
        
        Returns:
            SchemaVersion: 版本记录
        """
        # 计算哈希
        schema_json = json.dumps(schema, sort_keys=True, ensure_ascii=False)
        schema_hash = hashlib.sha256(schema_json.encode()).hexdigest()[:16]
        
        # 检测变更
        changes = []
        if self.versions:
            changes = self._detect_changes(self.versions[-1].schema, schema)
        
        version_record = SchemaVersion(
            version=version,
            timestamp=datetime.now(),
            hash=schema_hash,
            author=author,
            message=message,
            changes=changes,
            schema=schema
        )
        
        self.versions.append(version_record)
        self._save_version(version_record)
        
        return version_record
    
    def _detect_changes(self, old: Dict, new: Dict) -> List[Dict]:
        """检测变更"""
        changes = []
        
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        
        # 新增
        for key in new_keys - old_keys:
            changes.append({
                "type": "added",
                "path": key,
                "value": str(new[key])[:100]
            })
        
        # 删除
        for key in old_keys - new_keys:
            changes.append({
                "type": "removed",
                "path": key,
                "value": str(old[key])[:100]
            })
        
        # 修改
        for key in old_keys & new_keys:
            if old[key] != new[key]:
                changes.append({
                    "type": "modified",
                    "path": key,
                    "old": str(old[key])[:50],
                    "new": str(new[key])[:50]
                })
        
        return changes
    
    def _save_version(self, version: SchemaVersion):
        """保存版本"""
        file_path = self.history_dir / f"{version.version.replace('.', '_')}.json"
        
        data = {
            "version": version.version,
            "timestamp": version.timestamp.isoformat(),
            "hash": version.hash,
            "author": version.author,
            "message": version.message,
            "changes": version.changes,
            "schema": version.schema
        }
        
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), 
                            encoding='utf-8')
    
    def get_version(self, version_str: str) -> Optional[SchemaVersion]:
        """获取特定版本"""
        for v in self.versions:
            if v.version == version_str:
                return v
        return None
    
    def get_evolution_path(self, from_ver: str, to_ver: str) -> EvolutionPath:
        """获取两个版本间的演化路径"""
        from_version = self.get_version(from_ver)
        to_version = self.get_version(to_ver)
        
        if not from_version or not to_version:
            raise ValueError("Version not found")
        
        # 分析兼容性
        compatibility = self._analyze_compatibility(from_version, to_version)
        
        # 确定变更类型
        change_type = self._determine_change_type(from_version, to_version)
        
        # 生成迁移步骤
        migration_steps = self._generate_migration_steps(from_version, to_version)
        
        # 识别破坏性变更
        breaking_changes = self._identify_breaking_changes(from_version, to_version)
        
        return EvolutionPath(
            from_version=from_ver,
            to_version=to_ver,
            change_type=change_type,
            compatibility=compatibility,
            migration_steps=migration_steps,
            breaking_changes=breaking_changes
        )
    
    def _analyze_compatibility(self, old: SchemaVersion, 
                              new: SchemaVersion) -> CompatibilityType:
        """分析兼容性"""
        # 检查required字段
        old_required = set(old.schema.get("required", []))
        new_required = set(new.schema.get("required", []))
        
        # 如果新增必填字段，不向后兼容
        if new_required - old_required:
            return CompatibilityType.NONE
        
        # 如果删除必填字段，不向前兼容
        if old_required - new_required:
            return CompatibilityType.BACKWARD
        
        # 检查类型变更
        if self._has_type_changes(old.schema, new.schema):
            return CompatibilityType.NONE
        
        return CompatibilityType.FULL
    
    def _has_type_changes(self, old: Dict, new: Dict) -> bool:
        """检查是否有类型变更"""
        if old.get("type") != new.get("type"):
            return True
        
        # 递归检查properties
        old_props = old.get("properties", {})
        new_props = new.get("properties", {})
        
        for key in set(old_props.keys()) & set(new_props.keys()):
            if self._has_type_changes(old_props[key], new_props[key]):
                return True
        
        return False
    
    def _determine_change_type(self, old: SchemaVersion, 
                              new: SchemaVersion) -> VersionChangeType:
        """确定变更类型"""
        # 根据语义化版本规则
        old_parts = old.version.split(".")
        new_parts = new.version.split(".")
        
        if len(old_parts) >= 1 and len(new_parts) >= 1:
            if old_parts[0] != new_parts[0]:
                return VersionChangeType.MAJOR
        
        if len(old_parts) >= 2 and len(new_parts) >= 2:
            if old_parts[1] != new_parts[1]:
                return VersionChangeType.MINOR
        
        return VersionChangeType.PATCH
    
    def _generate_migration_steps(self, old: SchemaVersion, 
                                 new: SchemaVersion) -> List[str]:
        """生成迁移步骤"""
        steps = []
        
        # 检查字段变更
        old_props = old.schema.get("properties", {})
        new_props = new.schema.get("properties", {})
        
        # 新增字段
        for key in new_props:
            if key not in old_props:
                steps.append(f"添加新字段 '{key}' 的默认值")
        
        # 删除字段
        for key in old_props:
            if key not in new_props:
                steps.append(f"从数据中移除字段 '{key}'")
        
        # 类型变更
        for key in set(old_props.keys()) & set(new_props.keys()):
            if old_props[key].get("type") != new_props[key].get("type"):
                steps.append(f"转换字段 '{key}' 的数据类型")
        
        return steps if steps else ["无需迁移步骤"]
    
    def _identify_breaking_changes(self, old: SchemaVersion, 
                                  new: SchemaVersion) -> List[str]:
        """识别破坏性变更"""
        breaking = []
        
        # 检查必填字段
        old_required = set(old.schema.get("required", []))
        new_required = set(new.schema.get("required", []))
        
        for field in new_required - old_required:
            breaking.append(f"新增必填字段: {field}")
        
        # 检查类型变更
        old_props = old.schema.get("properties", {})
        new_props = new.schema.get("properties", {})
        
        for key in set(old_props.keys()) & set(new_props.keys()):
            if old_props[key].get("type") != new_props[key].get("type"):
                breaking.append(f"字段 '{key}' 类型变更: {old_props[key].get('type')} → {new_props[key].get('type')}")
        
        return breaking
    
    def generate_changelog(self, since: str = None) -> str:
        """生成变更日志"""
        lines = ["# Schema Change Log\n"]
        
        versions_to_include = self.versions
        if since:
            since_version = self.get_version(since)
            if since_version:
                idx = self.versions.index(since_version)
                versions_to_include = self.versions[idx+1:]
        
        for version in reversed(versions_to_include):
            lines.append(f"## [{version.version}] - {version.timestamp.strftime('%Y-%m-%d')}")
            lines.append(f"**Author**: {version.author}")
            lines.append(f"**Hash**: {version.hash}")
            lines.append(f"**Message**: {version.message}\n")
            
            if version.changes:
                lines.append("### Changes")
                for change in version.changes:
                    emoji = {"added": "➕", "removed": "➖", "modified": "📝"}.get(
                        change["type"], "•"
                    )
                    lines.append(f"- {emoji} {change['type'].title()}: {change['path']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def export_evolution_graph(self, output_path: str):
        """导出演化图 (Mermaid)"""
        lines = ["graph LR"]
        
        for i, version in enumerate(self.versions):
            node_id = f"V{version.version.replace('.', '_')}"
            label = f"{version.version}\\n{version.hash[:8]}"
            lines.append(f"    {node_id}[{label}]")
            
            if i > 0:
                prev_id = f"V{self.versions[i-1].version.replace('.', '_')}"
                lines.append(f"    {prev_id} --> {node_id}")
        
        Path(output_path).write_text("\n".join(lines), encoding='utf-8')
        return output_path


def main():
    """示例用法"""
    tracker = SchemaEvolutionTracker()
    
    # 模拟版本演进
    v1 = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    
    tracker.commit(v1, "1.0.0", "author1", "初始版本")
    
    v2 = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"}  # 新增
        },
        "required": ["name"]
    }
    
    tracker.commit(v2, "1.1.0", "author2", "添加email字段")
    
    v3 = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "email"]  # 新增必填
    }
    
    tracker.commit(v3, "2.0.0", "author3", "email变为必填，升级Schema版本")
    
    # 分析演化路径
    print("Schema演化分析")
    print("=" * 60)
    
    path = tracker.get_evolution_path("1.0.0", "2.0.0")
    print(f"演化路径: {path.from_version} → {path.to_version}")
    print(f"变更类型: {path.change_type.value}")
    print(f"兼容性: {path.compatibility.value}")
    
    print("\n破坏性变更:")
    for bc in path.breaking_changes:
        print(f"  ⚠️ {bc}")
    
    print("\n迁移步骤:")
    for step in path.migration_steps:
        print(f"  {step}")
    
    # 生成变更日志
    changelog = tracker.generate_changelog()
    Path("CHANGELOG.md").write_text(changelog, encoding='utf-8')
    print("\n✅ 变更日志已保存到: CHANGELOG.md")
    
    # 导出演化图
    tracker.export_evolution_graph("evolution_graph.mmd")
    print("✅ 演化图已保存到: evolution_graph.mmd")


if __name__ == "__main__":
    main()
