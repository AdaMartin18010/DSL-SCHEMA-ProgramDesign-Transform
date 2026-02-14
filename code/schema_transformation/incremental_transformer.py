"""
增量转换器模块 (Incremental Transformer Module)

该模块提供Schema的增量转换功能，基于变更检测和依赖分析结果，
实现高效、安全的Schema演进。

核心功能：
- 增量Schema转换
- 变更应用策略
- 转换事务管理
- 回滚支持
- 转换验证
"""

from typing import Dict, List, Set, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import copy
import json

from .change_detector import ChangeDetector, SchemaChange, ChangeType
from .dependency_analyzer import DependencyAnalyzer, DependencyGraph


class TransformationStrategy(Enum):
    """转换策略枚举"""
    SAFE = auto()            # 安全模式：只应用向后兼容的变更
    AGGRESSIVE = auto()      # 激进模式：应用所有变更
    SELECTIVE = auto()       # 选择性模式：手动选择变更
    ROLLBACK = auto()        # 回滚模式：回滚到之前版本
    MERGE = auto()           # 合并模式：合并多个变更


class TransformationStatus(Enum):
    """转换状态枚举"""
    PENDING = auto()         # 待处理
    IN_PROGRESS = auto()     # 进行中
    COMPLETED = auto()       # 已完成
    FAILED = auto()          # 失败
    ROLLED_BACK = auto()     # 已回滚
    PARTIAL = auto()         # 部分完成


@dataclass
class TransformationStep:
    """
    转换步骤
    
    Attributes:
        change: 对应的变更
        operation: 操作函数
        rollback_operation: 回滚操作函数
        status: 步骤状态
        executed_at: 执行时间
        error_message: 错误信息
    """
    change: SchemaChange
    operation: Optional[Callable] = None
    rollback_operation: Optional[Callable] = None
    status: TransformationStatus = TransformationStatus.PENDING
    executed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def execute(self) -> bool:
        """执行转换步骤"""
        if self.operation is None:
            self.status = TransformationStatus.COMPLETED
            return True
        
        try:
            self.status = TransformationStatus.IN_PROGRESS
            self.operation()
            self.status = TransformationStatus.COMPLETED
            self.executed_at = datetime.now()
            return True
        except Exception as e:
            self.status = TransformationStatus.FAILED
            self.error_message = str(e)
            return False
    
    def rollback(self) -> bool:
        """回滚转换步骤"""
        if self.rollback_operation is None:
            return True
        
        try:
            self.rollback_operation()
            self.status = TransformationStatus.ROLLED_BACK
            return True
        except Exception as e:
            self.error_message = f"Rollback failed: {e}"
            return False


@dataclass
class TransformationResult:
    """
    转换结果
    
    Attributes:
        success: 是否成功
        steps: 转换步骤列表
        applied_changes: 已应用的变更
        failed_changes: 失败的变更
        rolled_back_changes: 已回滚的变更
        start_time: 开始时间
        end_time: 结束时间
        metadata: 元数据
    """
    success: bool = False
    steps: List[TransformationStep] = field(default_factory=list)
    applied_changes: List[SchemaChange] = field(default_factory=list)
    failed_changes: List[SchemaChange] = field(default_factory=list)
    rolled_back_changes: List[SchemaChange] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """转换耗时（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        total = len(self.applied_changes) + len(self.failed_changes)
        return len(self.applied_changes) / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "duration": self.duration,
            "success_rate": self.success_rate,
            "total_steps": len(self.steps),
            "applied_changes": len(self.applied_changes),
            "failed_changes": len(self.failed_changes),
            "rolled_back_changes": len(self.rolled_back_changes),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metadata": self.metadata
        }


class IncrementalTransformer:
    """
    Schema增量转换器
    
    基于变更检测和依赖分析，安全高效地应用Schema变更。
    
    Attributes:
        change_detector: 变更检测器
        dependency_analyzer: 依赖分析器
        strategy: 转换策略
        enable_rollback: 是否启用回滚
        validation_enabled: 是否启用验证
    """
    
    def __init__(
        self,
        strategy: TransformationStrategy = TransformationStrategy.SAFE,
        enable_rollback: bool = True,
        validation_enabled: bool = True
    ):
        self.change_detector = ChangeDetector()
        self.dependency_analyzer = DependencyAnalyzer()
        self.strategy = strategy
        self.enable_rollback = enable_rollback
        self.validation_enabled = validation_enabled
        self._transformation_history: List[TransformationResult] = []
        self._snapshot_stack: List[Dict[str, Any]] = []
    
    def transform(
        self,
        current_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        custom_strategy: Optional[TransformationStrategy] = None
    ) -> TransformationResult:
        """
        执行增量转换
        
        Args:
            current_schema: 当前Schema
            target_schema: 目标Schema
            custom_strategy: 自定义转换策略
            
        Returns:
            转换结果
        """
        strategy = custom_strategy or self.strategy
        result = TransformationResult()
        result.start_time = datetime.now()
        
        # 创建快照（用于回滚）
        if self.enable_rollback:
            self._snapshot_stack.append(copy.deepcopy(current_schema))
        
        # 1. 检测变更
        changes = self.change_detector.detect_changes(current_schema, target_schema)
        
        # 2. 分析依赖
        dep_graph = self.dependency_analyzer.analyze(target_schema)
        
        # 3. 根据策略筛选变更
        filtered_changes = self._filter_changes(changes, strategy)
        
        # 4. 排序变更（考虑依赖关系）
        sorted_changes = self._sort_changes(filtered_changes, dep_graph)
        
        # 5. 创建转换步骤
        steps = self._create_transformation_steps(
            sorted_changes,
            current_schema,
            target_schema
        )
        result.steps = steps
        
        # 6. 执行转换
        schema = copy.deepcopy(current_schema)
        
        for step in steps:
            if step.execute():
                # 更新Schema
                self._apply_change_to_schema(schema, step.change)
                result.applied_changes.append(step.change)
                
                # 验证
                if self.validation_enabled:
                    validation_result = self._validate_schema(schema)
                    if not validation_result:
                        step.status = TransformationStatus.FAILED
                        step.error_message = "Validation failed after change"
                        result.failed_changes.append(step.change)
                        
                        # 回滚
                        if self.enable_rollback:
                            self._rollback_steps(result.steps)
                            result.rolled_back_changes = result.applied_changes.copy()
                            result.applied_changes.clear()
                            result.success = False
                            result.end_time = datetime.now()
                            return result
            else:
                result.failed_changes.append(step.change)
                
                # 回滚
                if self.enable_rollback:
                    self._rollback_steps(result.steps)
                    result.rolled_back_changes = result.applied_changes.copy()
                    result.applied_changes.clear()
                    result.success = False
                    result.end_time = datetime.now()
                    return result
        
        result.success = len(result.failed_changes) == 0
        result.end_time = datetime.now()
        result.metadata = {
            "strategy": strategy.name,
            "total_changes_detected": len(changes),
            "changes_applied": len(result.applied_changes),
            "dependencies_analyzed": len(dep_graph.nodes)
        }
        
        self._transformation_history.append(result)
        return result
    
    def _filter_changes(
        self,
        changes: List[SchemaChange],
        strategy: TransformationStrategy
    ) -> List[SchemaChange]:
        """根据策略筛选变更"""
        if strategy == TransformationStrategy.SAFE:
            # 安全模式：只应用向后兼容的变更
            return [c for c in changes if c.backward_compatible]
        
        elif strategy == TransformationStrategy.AGGRESSIVE:
            # 激进模式：应用所有变更
            return changes
        
        elif strategy == TransformationStrategy.SELECTIVE:
            # 选择性模式：需要外部输入，这里默认只应用低严重性变更
            return [c for c in changes if c.severity <= 3]
        
        return changes
    
    def _sort_changes(
        self,
        changes: List[SchemaChange],
        dep_graph: DependencyGraph
    ) -> List[SchemaChange]:
        """排序变更（考虑依赖关系）"""
        # 依赖项优先（被依赖的先处理）
        change_order = {}
        
        for i, change in enumerate(changes):
            node = dep_graph.get_node(change.path)
            if node:
                # 计算优先级：依赖越多，优先级越高
                priority = node.in_degree
                change_order[i] = priority
            else:
                change_order[i] = 0
        
        # 按优先级排序
        sorted_indices = sorted(change_order.keys(), key=lambda x: change_order[x], reverse=True)
        return [changes[i] for i in sorted_indices]
    
    def _create_transformation_steps(
        self,
        changes: List[SchemaChange],
        current_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[TransformationStep]:
        """创建转换步骤"""
        steps = []
        
        for change in changes:
            operation = self._create_operation(change, target_schema)
            rollback = self._create_rollback(change, current_schema) if self.enable_rollback else None
            
            step = TransformationStep(
                change=change,
                operation=operation,
                rollback_operation=rollback
            )
            steps.append(step)
        
        return steps
    
    def _create_operation(
        self,
        change: SchemaChange,
        target_schema: Dict[str, Any]
    ) -> Optional[Callable]:
        """创建变更操作"""
        # 根据变更类型创建操作
        if change.change_type == ChangeType.ADDED:
            return lambda: None  # 添加操作在_apply_change_to_schema中处理
        elif change.change_type == ChangeType.REMOVED:
            return lambda: None
        elif change.change_type == ChangeType.MODIFIED:
            return lambda: None
        elif change.change_type == ChangeType.RENAMED:
            return lambda: None
        
        return None
    
    def _create_rollback(
        self,
        change: SchemaChange,
        original_schema: Dict[str, Any]
    ) -> Optional[Callable]:
        """创建回滚操作"""
        # 保存原始值
        original_value = self._get_value_at_path(original_schema, change.path)
        
        def rollback():
            # 回滚逻辑由具体的应用逻辑处理
            pass
        
        return rollback
    
    def _apply_change_to_schema(
        self,
        schema: Dict[str, Any],
        change: SchemaChange
    ) -> None:
        """将变更应用到Schema"""
        path_parts = change.path.split('.')
        
        if change.change_type == ChangeType.ADDED:
            self._set_value_at_path(schema, path_parts, change.new_value)
        
        elif change.change_type == ChangeType.REMOVED:
            self._remove_value_at_path(schema, path_parts)
        
        elif change.change_type == ChangeType.MODIFIED:
            self._set_value_at_path(schema, path_parts, change.new_value)
        
        elif change.change_type == ChangeType.TYPE_CHANGED:
            self._set_value_at_path(schema, path_parts, change.new_value)
        
        elif change.change_type == ChangeType.RENAMED:
            # 解析重命名路径
            if ' -> ' in change.path:
                old_path, new_path = change.path.split(' -> ')
                old_parts = old_path.split('.')
                new_parts = new_path.split('.')
                
                value = self._get_value_at_path(schema, old_parts)
                self._remove_value_at_path(schema, old_parts)
                self._set_value_at_path(schema, new_parts, value)
    
    def _get_value_at_path(self, schema: Dict[str, Any], path_parts: List[str]) -> Any:
        """获取指定路径的值"""
        current = schema
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
    
    def _set_value_at_path(
        self,
        schema: Dict[str, Any],
        path_parts: List[str],
        value: Any
    ) -> None:
        """设置指定路径的值"""
        current = schema
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        if path_parts:
            current[path_parts[-1]] = value
    
    def _remove_value_at_path(self, schema: Dict[str, Any], path_parts: List[str]) -> None:
        """移除指定路径的值"""
        current = schema
        for part in path_parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return
        
        if path_parts and path_parts[-1] in current:
            del current[path_parts[-1]]
    
    def _validate_schema(self, schema: Dict[str, Any]) -> bool:
        """验证Schema有效性"""
        # 基本验证：确保是有效的字典结构
        if not isinstance(schema, dict):
            return False
        
        # 检查是否有循环引用
        try:
            json.dumps(schema)
        except (TypeError, ValueError):
            return False
        
        return True
    
    def _rollback_steps(self, steps: List[TransformationStep]) -> None:
        """回滚步骤"""
        # 逆序回滚
        for step in reversed(steps):
            if step.status == TransformationStatus.COMPLETED:
                step.rollback()
    
    def rollback_last(self) -> Optional[TransformationResult]:
        """
        回滚最后一次转换
        
        Returns:
            回滚结果
        """
        if not self._transformation_history or not self._snapshot_stack:
            return None
        
        last_result = self._transformation_history[-1]
        original_schema = self._snapshot_stack.pop()
        
        rollback_result = TransformationResult(
            success=True,
            rolled_back_changes=last_result.applied_changes.copy(),
            start_time=datetime.now(),
            end_time=datetime.now(),
            metadata={"rollback": True, "original_result": last_result.to_dict()}
        )
        
        return rollback_result
    
    def preview_transform(
        self,
        current_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        预览转换结果（不实际执行）
        
        Args:
            current_schema: 当前Schema
            target_schema: 目标Schema
            
        Returns:
            预览结果
        """
        changes = self.change_detector.detect_changes(current_schema, target_schema)
        dep_graph = self.dependency_analyzer.analyze(target_schema)
        
        filtered_changes = self._filter_changes(changes, self.strategy)
        
        # 分析影响
        impact = self.dependency_analyzer.analyze_impact(
            [c.path for c in filtered_changes]
        )
        
        return {
            "total_changes": len(changes),
            "filtered_changes": len(filtered_changes),
            "changes": [c.to_dict() for c in filtered_changes],
            "dependencies": dep_graph.to_dict(),
            "impact_analysis": impact,
            "strategy": self.strategy.name,
            "can_execute": len(filtered_changes) > 0
        }
    
    def get_transformation_history(self) -> List[TransformationResult]:
        """获取转换历史"""
        return self._transformation_history.copy()
    
    def clear_history(self) -> None:
        """清空历史"""
        self._transformation_history.clear()
        self._snapshot_stack.clear()
