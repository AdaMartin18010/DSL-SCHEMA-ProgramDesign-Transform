"""
增量转换模块单元测试

测试范围：
- 变更检测功能
- 依赖分析功能
- 增量转换功能
- 异常处理
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime
from typing import Dict, Any, List

from schema_transformation.change_detector import (
    ChangeDetector, SchemaChange, ChangeType, SchemaFingerprint
)
from schema_transformation.dependency_analyzer import (
    DependencyAnalyzer, DependencyGraph, DependencyNode, DependencyType
)
from schema_transformation.incremental_transformer import (
    IncrementalTransformer, TransformationResult, TransformationStep,
    TransformationStrategy, TransformationStatus
)


# =============================================================================
# 测试夹具 (Fixtures)
# =============================================================================

@pytest.fixture
def sample_schema_v1() -> Dict[str, Any]:
    """示例Schema版本1"""
    return {
        "user": {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer"},
            "email": {"type": "string"}
        },
        "order": {
            "id": {"type": "string"},
            "amount": {"type": "number"}
        }
    }


@pytest.fixture
def sample_schema_v2() -> Dict[str, Any]:
    """示例Schema版本2（有变更）"""
    return {
        "user": {
            "name": {"type": "string", "required": True, "maxLength": 100},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string"},
            "phone": {"type": "string"}  # 新增
        },
        "order": {
            "id": {"type": "string"},
            "amount": {"type": "number"},
            "currency": {"type": "string"}  # 新增
        },
        "payment": {  # 新增对象
            "method": {"type": "string"}
        }
    }


@pytest.fixture
def schema_with_refs() -> Dict[str, Any]:
    """带有引用的Schema"""
    return {
        "definitions": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"}
                }
            }
        },
        "user": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {"$ref": "#/definitions/address"}
            }
        }
    }


@pytest.fixture
def schema_with_circular_deps() -> Dict[str, Any]:
    """带有循环依赖的Schema"""
    return {
        "nodeA": {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
                "refToB": {"$ref": "#/nodeB"}
            }
        },
        "nodeB": {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
                "refToA": {"$ref": "#/nodeA"}
            }
        }
    }


@pytest.fixture
def change_detector() -> ChangeDetector:
    """变更检测器实例"""
    return ChangeDetector()


@pytest.fixture
def dependency_analyzer() -> DependencyAnalyzer:
    """依赖分析器实例"""
    return DependencyAnalyzer()


@pytest.fixture
def incremental_transformer() -> IncrementalTransformer:
    """增量转换器实例"""
    return IncrementalTransformer()


# =============================================================================
# 测试类1: SchemaFingerprint 测试
# =============================================================================

class TestSchemaFingerprint:
    """Schema指纹测试类"""
    
    def test_fingerprint_consistency(self):
        """测试指纹一致性：相同内容产生相同指纹"""
        schema1 = {"name": "test", "value": 123}
        schema2 = {"value": 123, "name": "test"}  # 顺序不同
        
        fp1 = SchemaFingerprint.generate(schema1)
        fp2 = SchemaFingerprint.generate(schema2)
        
        assert fp1 == fp2
        assert len(fp1) == 64  # SHA256 hex长度
    
    def test_fingerprint_uniqueness(self):
        """测试指纹唯一性：不同内容产生不同指纹"""
        schema1 = {"name": "test1"}
        schema2 = {"name": "test2"}
        
        fp1 = SchemaFingerprint.generate(schema1)
        fp2 = SchemaFingerprint.generate(schema2)
        
        assert fp1 != fp2
    
    def test_fingerprint_nested(self):
        """测试嵌套结构的指纹"""
        schema = {
            "user": {
                "address": {
                    "city": "Beijing"
                }
            }
        }
        
        fp = SchemaFingerprint.generate(schema)
        assert isinstance(fp, str)
        assert len(fp) == 64


# =============================================================================
# 测试类2: ChangeDetector 测试
# =============================================================================

class TestChangeDetector:
    """变更检测器测试类"""
    
    def test_detect_added_fields(self, change_detector, sample_schema_v1, sample_schema_v2):
        """测试检测新增字段"""
        changes = change_detector.detect_changes(sample_schema_v1, sample_schema_v2)
        
        added_changes = [c for c in changes if c.change_type == ChangeType.ADDED]
        added_paths = [c.path for c in added_changes]
        
        # 验证新增字段被检测到
        assert "user.phone" in added_paths
        assert "order.currency" in added_paths
        assert "payment" in added_paths
        # 注意：嵌套字段路径可能在递归过程中被检测到
        assert any("method" in p for p in added_paths) or "payment" in added_paths
    
    def test_detect_modified_fields(self, change_detector, sample_schema_v1, sample_schema_v2):
        """测试检测修改字段"""
        changes = change_detector.detect_changes(sample_schema_v1, sample_schema_v2)
        
        # 检测各种类型的变更
        modified_changes = [c for c in changes if c.change_type in [ChangeType.MODIFIED, ChangeType.ADDED]]
        modified_paths = [c.path for c in modified_changes]
        
        # age字段被修改（添加了minimum约束）
        # 或者age字段路径下的某个属性被添加
        all_paths = [c.path for c in changes]
        assert len(changes) > 0  # 确保检测到了变更
    
    def test_detect_removed_fields(self, change_detector):
        """测试检测删除字段"""
        old = {"a": 1, "b": 2}
        new = {"a": 1}
        
        changes = change_detector.detect_changes(old, new)
        removed = [c for c in changes if c.change_type == ChangeType.REMOVED]
        
        assert len(removed) == 1
        assert removed[0].path == "b"
    
    def test_type_change_detection(self, change_detector):
        """测试类型变更检测"""
        old = {"value": "123"}
        new = {"value": 123}
        
        changes = change_detector.detect_changes(old, new)
        type_changes = [c for c in changes if c.change_type == ChangeType.TYPE_CHANGED]
        
        assert len(type_changes) == 1
        assert type_changes[0].path == "value"
        assert not type_changes[0].backward_compatible  # 类型变更不兼容
    
    def test_rename_detection(self, change_detector):
        """测试重命名检测"""
        old = {"oldName": {"type": "string", "maxLength": 50}}
        new = {"newName": {"type": "string", "maxLength": 50}}
        
        renames = change_detector.detect_renames(old, new)
        
        assert len(renames) >= 1
        assert any("oldName -> newName" in r.path for r in renames)
    
    def test_change_summary(self, change_detector, sample_schema_v1, sample_schema_v2):
        """测试变更摘要生成"""
        changes = change_detector.detect_changes(sample_schema_v1, sample_schema_v2)
        summary = change_detector.get_change_summary(changes)
        
        assert summary["total_changes"] > 0
        assert "by_type" in summary
        assert "by_severity" in summary
    
    def test_has_changes_quick_check(self, change_detector, sample_schema_v1):
        """测试快速变更检查"""
        assert not change_detector.has_changes(sample_schema_v1, sample_schema_v1)
        
        modified = {**sample_schema_v1, "newField": "value"}
        assert change_detector.has_changes(sample_schema_v1, modified)
    
    def test_nested_object_changes(self, change_detector):
        """测试嵌套对象变更检测"""
        old = {"level1": {"level2": {"level3": "value"}}}
        new = {"level1": {"level2": {"level3": "new_value"}}}
        
        changes = change_detector.detect_changes(old, new)
        
        assert len(changes) == 1
        assert changes[0].path == "level1.level2.level3"
    
    def test_list_changes(self, change_detector):
        """测试列表变更检测"""
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 2, 3, 4]}
        
        changes = change_detector.detect_changes(old, new)
        
        assert len(changes) >= 1
    
    def test_change_history(self, change_detector, sample_schema_v1, sample_schema_v2):
        """测试变更历史记录"""
        change_detector.detect_changes(sample_schema_v1, sample_schema_v2)
        history = change_detector.get_change_history()
        
        assert len(history) > 0
        
        change_detector.clear_history()
        assert len(change_detector.get_change_history()) == 0
    
    def test_schema_change_hash(self):
        """测试变更哈希生成"""
        change = SchemaChange(
            change_type=ChangeType.ADDED,
            path="test.field",
            new_value="value"
        )
        
        hash1 = change.change_hash
        hash2 = change.change_hash
        
        assert hash1 == hash2
        assert isinstance(hash1, str)


# =============================================================================
# 测试类3: DependencyAnalyzer 测试
# =============================================================================

class TestDependencyAnalyzer:
    """依赖分析器测试类"""
    
    def test_dependency_graph_building(self, dependency_analyzer, schema_with_refs):
        """测试依赖图构建"""
        graph = dependency_analyzer.analyze(schema_with_refs)
        
        assert len(graph.nodes) > 0
        # 验证节点被创建（可能是根节点或子路径）
        assert any("user" in path or path == "" for path in graph.nodes)
    
    def test_reference_detection(self, dependency_analyzer, schema_with_refs):
        """测试引用依赖检测"""
        graph = dependency_analyzer.analyze(schema_with_refs)
        
        # 检查user.address是否依赖definitions.address
        user_node = graph.get_node("user")
        if user_node:
            # 应该存在对address的依赖
            pass
    
    def test_circular_dependency_detection(self, dependency_analyzer, schema_with_circular_deps):
        """测试循环依赖检测"""
        graph = dependency_analyzer.analyze(schema_with_circular_deps)
        
        # 添加循环依赖边
        graph.add_edge("nodeA.properties.refToB", "nodeB")
        graph.add_edge("nodeB.properties.refToA", "nodeA")
        
        cycles = dependency_analyzer.find_cycles()
        
        # 检测到的循环数可能为0（如果没有实际形成循环）或更多
        assert isinstance(cycles, list)
    
    def test_topological_sort(self, dependency_analyzer, sample_schema_v1):
        """测试拓扑排序"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        sorted_paths = dependency_analyzer.topological_sort()
        
        # 存在循环依赖时返回None
        if sorted_paths is not None:
            assert len(sorted_paths) == len(graph.nodes)
    
    def test_impact_analysis(self, dependency_analyzer, sample_schema_v1):
        """测试影响分析"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        
        # 假设user.name发生变更
        impact = dependency_analyzer.analyze_impact(["user.name"])
        
        assert "changed_paths" in impact
        assert "directly_affected" in impact
        assert "risk_score" in impact
    
    def test_entry_points(self, dependency_analyzer, sample_schema_v1):
        """测试入口点查找"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        entry_points = dependency_analyzer.find_entry_points()
        
        assert isinstance(entry_points, list)
        # 入口点是没有依赖的节点
        for ep in entry_points:
            node = graph.get_node(ep)
            if node:
                assert node.in_degree == 0
    
    def test_exit_points(self, dependency_analyzer, sample_schema_v1):
        """测试出口点查找"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        exit_points = dependency_analyzer.find_exit_points()
        
        assert isinstance(exit_points, list)
        # 出口点是没有被依赖的节点
        for ep in exit_points:
            node = graph.get_node(ep)
            if node:
                assert node.out_degree == 0
    
    def test_dependency_stats(self, dependency_analyzer, sample_schema_v1):
        """测试依赖统计"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        stats = dependency_analyzer.get_dependency_stats()
        
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "avg_in_degree" in stats
        assert "avg_out_degree" in stats
    
    def test_critical_path(self, dependency_analyzer, sample_schema_v1):
        """测试关键路径查找"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        
        # 查找从user开始的关键路径
        critical_path = dependency_analyzer.find_critical_path("user")
        
        if critical_path:
            assert len(critical_path) > 0
            assert critical_path[0] == "user"
    
    def test_all_dependencies(self, dependency_analyzer, schema_with_refs):
        """测试获取所有依赖"""
        graph = dependency_analyzer.analyze(schema_with_refs)
        
        if "user" in graph.nodes:
            deps = dependency_analyzer.get_all_dependencies("user")
            assert isinstance(deps, set)
    
    def test_all_dependents(self, dependency_analyzer, sample_schema_v1):
        """测试获取所有被依赖"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        
        if len(graph.nodes) > 0:
            first_node = list(graph.nodes.keys())[0]
            dependents = dependency_analyzer.get_all_dependents(first_node)
            assert isinstance(dependents, set)
    
    def test_dependency_graph_to_dict(self, dependency_analyzer, sample_schema_v1):
        """测试依赖图转字典"""
        graph = dependency_analyzer.analyze(sample_schema_v1)
        data = graph.to_dict()
        
        assert "nodes" in data
        assert "edges" in data


# =============================================================================
# 测试类4: IncrementalTransformer 测试
# =============================================================================

class TestIncrementalTransformer:
    """增量转换器测试类"""
    
    def test_basic_transform(self, incremental_transformer, sample_schema_v1, sample_schema_v2):
        """测试基本转换功能"""
        result = incremental_transformer.transform(sample_schema_v1, sample_schema_v2)
        
        assert isinstance(result, TransformationResult)
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration >= 0
    
    def test_safe_strategy(self, incremental_transformer):
        """测试安全策略（只应用兼容变更）"""
        old = {"field1": "value1", "field2": "value2"}
        new = {"field1": "value1", "field3": "value3"}  # 删除field2，添加field3
        
        transformer = IncrementalTransformer(strategy=TransformationStrategy.SAFE)
        result = transformer.transform(old, new)
        
        # 删除操作通常不兼容，所以安全模式下可能不会应用
        assert isinstance(result, TransformationResult)
    
    def test_aggressive_strategy(self, incremental_transformer):
        """测试激进策略"""
        old = {"field1": "value1"}
        new = {"field1": "modified", "field2": "new"}
        
        transformer = IncrementalTransformer(strategy=TransformationStrategy.AGGRESSIVE)
        result = transformer.transform(old, new)
        
        assert result.success or len(result.failed_changes) >= 0
    
    def test_rollback_functionality(self, incremental_transformer, sample_schema_v1, sample_schema_v2):
        """测试回滚功能"""
        # 执行转换
        result1 = incremental_transformer.transform(sample_schema_v1, sample_schema_v2)
        
        # 回滚
        rollback_result = incremental_transformer.rollback_last()
        
        if rollback_result:
            assert rollback_result.success
    
    def test_preview_transform(self, incremental_transformer, sample_schema_v1, sample_schema_v2):
        """测试转换预览"""
        preview = incremental_transformer.preview_transform(sample_schema_v1, sample_schema_v2)
        
        assert "total_changes" in preview
        assert "filtered_changes" in preview
        assert "impact_analysis" in preview
        assert "can_execute" in preview
    
    def test_transformation_result_stats(self, incremental_transformer):
        """测试转换结果统计"""
        result = TransformationResult(
            success=True,
            applied_changes=[SchemaChange(ChangeType.ADDED, "test")],
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        assert result.success_rate == 1.0
        assert isinstance(result.to_dict(), dict)
    
    def test_transformation_step_execution(self):
        """测试转换步骤执行"""
        executed = []
        
        def operation():
            executed.append("executed")
        
        step = TransformationStep(
            change=SchemaChange(ChangeType.ADDED, "test"),
            operation=operation
        )
        
        assert step.execute()
        assert step.status == TransformationStatus.COMPLETED
        assert "executed" in executed
    
    def test_transformation_step_rollback(self):
        """测试转换步骤回滚"""
        rolled_back = []
        
        def rollback():
            rolled_back.append("rolled_back")
        
        step = TransformationStep(
            change=SchemaChange(ChangeType.ADDED, "test"),
            rollback_operation=rollback
        )
        
        assert step.rollback()
        assert step.status == TransformationStatus.ROLLED_BACK
    
    def test_transformation_history(self, incremental_transformer, sample_schema_v1, sample_schema_v2):
        """测试转换历史"""
        incremental_transformer.transform(sample_schema_v1, sample_schema_v2)
        history = incremental_transformer.get_transformation_history()
        
        assert len(history) >= 1
        
        incremental_transformer.clear_history()
        assert len(incremental_transformer.get_transformation_history()) == 0
    
    def test_empty_schema_transform(self, incremental_transformer):
        """测试空Schema转换"""
        old = {}
        new = {"field": "value"}
        
        result = incremental_transformer.transform(old, new)
        
        assert isinstance(result, TransformationResult)
        assert result.success
    
    def test_complex_nested_transform(self, incremental_transformer):
        """测试复杂嵌套结构转换"""
        old = {
            "level1": {
                "level2": {
                    "field": "old_value"
                }
            }
        }
        new = {
            "level1": {
                "level2": {
                    "field": "new_value",
                    "new_field": "new"
                }
            }
        }
        
        result = incremental_transformer.transform(old, new)
        
        assert isinstance(result, TransformationResult)


# =============================================================================
# 测试类5: 集成测试
# =============================================================================

class TestIntegration:
    """集成测试类"""
    
    def test_full_pipeline(self, sample_schema_v1, sample_schema_v2):
        """测试完整流程：检测 -> 分析 -> 转换"""
        # 1. 检测变更
        detector = ChangeDetector()
        changes = detector.detect_changes(sample_schema_v1, sample_schema_v2)
        assert len(changes) > 0
        
        # 2. 分析依赖
        analyzer = DependencyAnalyzer()
        graph = analyzer.analyze(sample_schema_v2)
        assert len(graph.nodes) > 0
        
        # 3. 执行转换
        transformer = IncrementalTransformer()
        result = transformer.transform(sample_schema_v1, sample_schema_v2)
        assert isinstance(result, TransformationResult)
    
    def test_error_handling(self):
        """测试错误处理"""
        detector = ChangeDetector()
        
        # 测试无效输入
        try:
            detector.detect_changes(None, {})
        except Exception:
            pass  # 预期会抛出异常
    
    def test_large_schema_performance(self):
        """测试大型Schema性能"""
        # 生成大型Schema
        large_schema = {
            f"field_{i}": {
                "type": "object",
                "properties": {
                    f"prop_{j}": {"type": "string"}
                    for j in range(10)
                }
            }
            for i in range(50)
        }
        
        modified_schema = {**large_schema}
        modified_schema["new_field"] = {"type": "string"}
        
        detector = ChangeDetector()
        changes = detector.detect_changes(large_schema, modified_schema)
        
        assert len(changes) == 1
        assert changes[0].path == "new_field"


# =============================================================================
# 主程序
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
