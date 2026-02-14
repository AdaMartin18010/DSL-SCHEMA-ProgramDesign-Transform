"""
变更检测模块 (Change Detector Module)

该模块提供Schema变更检测功能，能够识别两个Schema版本之间的差异，
包括字段添加、删除、修改、类型变更等。

核心功能：
- Schema结构对比
- 变更类型识别
- 变更影响评估
- 变更历史追踪
"""

from enum import Enum, auto
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


class ChangeType(Enum):
    """变更类型枚举"""
    ADDED = auto()           # 新增字段/属性
    REMOVED = auto()         # 删除字段/属性
    MODIFIED = auto()        # 修改字段/属性
    TYPE_CHANGED = auto()    # 类型变更
    CONSTRAINT_CHANGED = auto()  # 约束变更
    RENAMED = auto()         # 重命名
    DEPRECATED = auto()      # 弃用
    MOVED = auto()           # 移动位置
    ANNOTATION_CHANGED = auto()  # 注解/注释变更


@dataclass
class SchemaChange:
    """
    Schema变更数据类
    
    Attributes:
        change_type: 变更类型
        path: 变更字段的路径（如 "user.address.zip"）
        old_value: 变更前的值
        new_value: 变更后的值
        description: 变更描述
        timestamp: 变更检测时间
        severity: 变更严重程度 (1-5, 5为最严重)
        backward_compatible: 是否向后兼容
        affected_paths: 受影响的相关路径列表
    """
    change_type: ChangeType
    path: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    severity: int = 1
    backward_compatible: bool = True
    affected_paths: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """生成变更描述"""
        type_names = {
            ChangeType.ADDED: "添加",
            ChangeType.REMOVED: "删除",
            ChangeType.MODIFIED: "修改",
            ChangeType.TYPE_CHANGED: "类型变更",
            ChangeType.CONSTRAINT_CHANGED: "约束变更",
            ChangeType.RENAMED: "重命名",
            ChangeType.DEPRECATED: "弃用",
            ChangeType.MOVED: "移动",
            ChangeType.ANNOTATION_CHANGED: "注解变更",
        }
        action = type_names.get(self.change_type, "未知变更")
        return f"{action}: {self.path}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "change_type": self.change_type.name,
            "path": self.path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "backward_compatible": self.backward_compatible,
            "affected_paths": self.affected_paths,
        }
    
    @property
    def change_hash(self) -> str:
        """生成变更的唯一哈希值"""
        content = f"{self.change_type.name}:{self.path}:{self.old_value}:{self.new_value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class SchemaFingerprint:
    """Schema指纹生成器，用于快速比较Schema"""
    
    @staticmethod
    def generate(schema: Dict[str, Any]) -> str:
        """
        生成Schema的指纹
        
        Args:
            schema: Schema字典
            
        Returns:
            Schema指纹（SHA256哈希值）
        """
        # 规范化Schema（排序键值对）
        normalized = SchemaFingerprint._normalize(schema)
        content = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()
    
    @staticmethod
    def _normalize(obj: Any) -> Any:
        """递归规范化对象"""
        if isinstance(obj, dict):
            return {k: SchemaFingerprint._normalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [SchemaFingerprint._normalize(item) for item in obj]
        else:
            return obj


class ChangeDetector:
    """
    Schema变更检测器
    
    检测两个Schema版本之间的所有变更，提供详细的变更报告。
    
    Attributes:
        ignore_annotations: 是否忽略注解变更
        strict_mode: 严格模式（检测更细微的差异）
        max_depth: 最大检测深度
    """
    
    def __init__(
        self,
        ignore_annotations: bool = False,
        strict_mode: bool = False,
        max_depth: int = 100
    ):
        self.ignore_annotations = ignore_annotations
        self.strict_mode = strict_mode
        self.max_depth = max_depth
        self._change_history: List[SchemaChange] = []
    
    def detect_changes(
        self,
        old_schema: Dict[str, Any],
        new_schema: Dict[str, Any],
        path_prefix: str = ""
    ) -> List[SchemaChange]:
        """
        检测两个Schema之间的变更
        
        Args:
            old_schema: 旧版本Schema
            new_schema: 新版本Schema
            path_prefix: 路径前缀
            
        Returns:
            变更列表
        """
        changes = []
        current_depth = path_prefix.count('.')
        
        if current_depth >= self.max_depth:
            return changes
        
        # 获取所有键
        old_keys = set(old_schema.keys())
        new_keys = set(new_schema.keys())
        
        # 检测删除的字段
        for key in old_keys - new_keys:
            full_path = f"{path_prefix}.{key}" if path_prefix else key
            change = SchemaChange(
                change_type=ChangeType.REMOVED,
                path=full_path,
                old_value=old_schema[key],
                severity=4,  # 删除字段通常影响较大
                backward_compatible=False
            )
            changes.append(change)
        
        # 检测新增的字段
        for key in new_keys - old_keys:
            full_path = f"{path_prefix}.{key}" if path_prefix else key
            change = SchemaChange(
                change_type=ChangeType.ADDED,
                path=full_path,
                new_value=new_schema[key],
                severity=1,  # 新增字段通常是向后兼容的
                backward_compatible=True
            )
            changes.append(change)
        
        # 检测修改的字段
        for key in old_keys & new_keys:
            full_path = f"{path_prefix}.{key}" if path_prefix else key
            old_value = old_schema[key]
            new_value = new_schema[key]
            
            changes.extend(
                self._compare_values(full_path, old_value, new_value)
            )
        
        # 添加到历史记录
        self._change_history.extend(changes)
        
        return changes
    
    def _compare_values(
        self,
        path: str,
        old_value: Any,
        new_value: Any
    ) -> List[SchemaChange]:
        """比较两个值并生成变更"""
        changes = []
        
        # 类型不同
        if type(old_value) != type(new_value):
            change = SchemaChange(
                change_type=ChangeType.TYPE_CHANGED,
                path=path,
                old_value=old_value,
                new_value=new_value,
                severity=5,  # 类型变更通常是破坏性变更
                backward_compatible=False
            )
            changes.append(change)
            return changes
        
        # 字典类型，递归比较
        if isinstance(old_value, dict):
            nested_changes = self.detect_changes(old_value, new_value, path)
            changes.extend(nested_changes)
        
        # 列表类型
        elif isinstance(old_value, list):
            changes.extend(self._compare_lists(path, old_value, new_value))
        
        # 基本类型，直接比较值
        elif old_value != new_value:
            change = SchemaChange(
                change_type=ChangeType.MODIFIED,
                path=path,
                old_value=old_value,
                new_value=new_value,
                severity=self._calculate_severity(old_value, new_value),
                backward_compatible=self._check_backward_compatible(old_value, new_value)
            )
            changes.append(change)
        
        return changes
    
    def _compare_lists(
        self,
        path: str,
        old_list: List,
        new_list: List
    ) -> List[SchemaChange]:
        """比较两个列表"""
        changes = []
        
        # 列表长度变化
        if len(old_list) != len(new_list):
            change = SchemaChange(
                change_type=ChangeType.MODIFIED,
                path=path,
                old_value=f"list[{len(old_list)}]",
                new_value=f"list[{len(new_list)}]",
                severity=2,
                backward_compatible=len(new_list) >= len(old_list)
            )
            changes.append(change)
        
        # 比较列表元素
        min_len = min(len(old_list), len(new_list))
        for i in range(min_len):
            element_path = f"{path}[{i}]"
            changes.extend(
                self._compare_values(element_path, old_list[i], new_list[i])
            )
        
        return changes
    
    def _calculate_severity(self, old_value: Any, new_value: Any) -> int:
        """计算变更严重程度"""
        # 简单的启发式规则
        old_str = str(old_value)
        new_str = str(new_value)
        
        # 长度变化很大
        if abs(len(old_str) - len(new_str)) > 100:
            return 3
        
        # 空值检查
        if old_str == "" or new_str == "":
            return 2
        
        return 1
    
    def _check_backward_compatible(self, old_value: Any, new_value: Any) -> bool:
        """检查变更是否向后兼容"""
        # 空值变为非空值通常是兼容的
        if old_value is None and new_value is not None:
            return True
        # 非空值变为空值通常不兼容
        if old_value is not None and new_value is None:
            return False
        return True
    
    def detect_renames(
        self,
        old_schema: Dict[str, Any],
        new_schema: Dict[str, Any],
        similarity_threshold: float = 0.8
    ) -> List[SchemaChange]:
        """
        检测可能的重命名操作
        
        通过比较删除和新增的字段，识别可能的重命名
        
        Args:
            old_schema: 旧版本Schema
            new_schema: 新版本Schema
            similarity_threshold: 相似度阈值
            
        Returns:
            重命名变更列表
        """
        changes = []
        
        old_keys = set(old_schema.keys())
        new_keys = set(new_schema.keys())
        
        removed_keys = old_keys - new_keys
        added_keys = new_keys - old_keys
        
        for removed in removed_keys:
            for added in added_keys:
                similarity = self._calculate_similarity(
                    old_schema[removed],
                    new_schema[added]
                )
                if similarity >= similarity_threshold:
                    change = SchemaChange(
                        change_type=ChangeType.RENAMED,
                        path=f"{removed} -> {added}",
                        old_value=removed,
                        new_value=added,
                        description=f"可能的重命名: {removed} -> {added} (相似度: {similarity:.2%})",
                        severity=2,
                        backward_compatible=False
                    )
                    changes.append(change)
        
        return changes
    
    def _calculate_similarity(self, obj1: Any, obj2: Any) -> float:
        """计算两个对象的相似度"""
        if type(obj1) != type(obj2):
            return 0.0
        
        if isinstance(obj1, dict):
            keys1 = set(obj1.keys())
            keys2 = set(obj2.keys())
            if not keys1 and not keys2:
                return 1.0
            intersection = keys1 & keys2
            union = keys1 | keys2
            return len(intersection) / len(union) if union else 0.0
        
        return 1.0 if obj1 == obj2 else 0.0
    
    def get_change_summary(self, changes: List[SchemaChange]) -> Dict[str, Any]:
        """
        获取变更摘要
        
        Args:
            changes: 变更列表
            
        Returns:
            变更摘要字典
        """
        type_counts = {}
        severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        compatible_count = 0
        
        for change in changes:
            type_counts[change.change_type.name] = type_counts.get(change.change_type.name, 0) + 1
            severity_counts[change.severity] = severity_counts.get(change.severity, 0) + 1
            if change.backward_compatible:
                compatible_count += 1
        
        return {
            "total_changes": len(changes),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "backward_compatible": compatible_count,
            "breaking_changes": len(changes) - compatible_count,
            "breaking_ratio": (len(changes) - compatible_count) / len(changes) if changes else 0
        }
    
    def has_changes(
        self,
        old_schema: Dict[str, Any],
        new_schema: Dict[str, Any]
    ) -> bool:
        """
        快速检查是否有变更（使用指纹）
        
        Args:
            old_schema: 旧版本Schema
            new_schema: 新版本Schema
            
        Returns:
            是否有变更
        """
        old_fingerprint = SchemaFingerprint.generate(old_schema)
        new_fingerprint = SchemaFingerprint.generate(new_schema)
        return old_fingerprint != new_fingerprint
    
    def get_change_history(self) -> List[SchemaChange]:
        """获取变更历史"""
        return self._change_history.copy()
    
    def clear_history(self) -> None:
        """清空变更历史"""
        self._change_history.clear()
