#!/usr/bin/env python3
"""
Schema Migration Tool
======================

Schema迁移工具，提供：
- 版本间自动迁移
- 数据转换
- 兼容性检查
- 回滚支持
- 迁移脚本生成

Version: 2.3.0
"""

import json
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from enum import Enum
from datetime import datetime


class MigrationType(Enum):
    """迁移类型"""
    ADD_FIELD = "add_field"
    REMOVE_FIELD = "remove_field"
    RENAME_FIELD = "rename_field"
    CHANGE_TYPE = "change_type"
    ADD_CONSTRAINT = "add_constraint"
    REMOVE_CONSTRAINT = "remove_constraint"
    SPLIT_FIELD = "split_field"
    MERGE_FIELDS = "merge_fields"
    CUSTOM = "custom"


class CompatibilityLevel(Enum):
    """兼容级别"""
    FULL = "full"  # 完全兼容
    BACKWARD = "backward"  # 向后兼容
    FORWARD = "forward"  # 向前兼容
    NONE = "none"  # 不兼容


@dataclass
class MigrationStep:
    """迁移步骤"""
    type: MigrationType
    path: str
    old_value: Any = None
    new_value: Any = None
    transform: Optional[Callable] = None
    description: str = ""


@dataclass
class MigrationPlan:
    """迁移计划"""
    from_version: str
    to_version: str
    steps: List[MigrationStep]
    compatibility: CompatibilityLevel
    estimated_impact: int  # 预计影响的数据量
    rollback_steps: List[MigrationStep] = field(default_factory=list)


@dataclass
class MigrationResult:
    """迁移结果"""
    success: bool
    migrated_count: int
    failed_count: int
    errors: List[str]
    warnings: List[str]
    duration_ms: float


class SchemaMigrationEngine:
    """Schema迁移引擎"""
    
    def __init__(self):
        self.migration_history: List[MigrationPlan] = []
        self.transform_registry: Dict[str, Callable] = {}
        self._register_default_transforms()
    
    def _register_default_transforms(self):
        """注册默认转换函数"""
        self.transform_registry.update({
            "string_to_int": lambda x: int(x) if x is not None else None,
            "int_to_string": lambda x: str(x) if x is not None else None,
            "string_to_date": lambda x: datetime.fromisoformat(x.replace('Z', '+00:00')) if x else None,
            "date_to_string": lambda x: x.isoformat() if x else None,
            "concat_fields": lambda fields: ' '.join(str(f) for f in fields if f),
            "split_name": lambda x: {"first": x.split()[0], "last": x.split()[-1]} if x else {}
        })
    
    def compare_schemas(self, old_schema: Dict, new_schema: Dict) -> List[MigrationStep]:
        """
        比较两个Schema并生成迁移步骤
        
        Args:
            old_schema: 旧版本Schema
            new_schema: 新版本Schema
        
        Returns:
            List[MigrationStep]: 迁移步骤列表
        """
        steps = []
        
        # 比较属性
        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})
        
        # 检测新增字段
        for prop_name in new_props:
            if prop_name not in old_props:
                steps.append(MigrationStep(
                    type=MigrationType.ADD_FIELD,
                    path=f"properties.{prop_name}",
                    new_value=new_props[prop_name],
                    description=f"Add new field '{prop_name}'"
                ))
        
        # 检测删除字段
        for prop_name in old_props:
            if prop_name not in new_props:
                steps.append(MigrationStep(
                    type=MigrationType.REMOVE_FIELD,
                    path=f"properties.{prop_name}",
                    old_value=old_props[prop_name],
                    description=f"Remove field '{prop_name}'"
                ))
        
        # 检测修改的字段
        for prop_name in old_props:
            if prop_name in new_props:
                old_prop = old_props[prop_name]
                new_prop = new_props[prop_name]
                
                # 检测类型变更
                if old_prop.get("type") != new_prop.get("type"):
                    steps.append(MigrationStep(
                        type=MigrationType.CHANGE_TYPE,
                        path=f"properties.{prop_name}",
                        old_value=old_prop.get("type"),
                        new_value=new_prop.get("type"),
                        description=f"Change type of '{prop_name}' from {old_prop.get('type')} to {new_prop.get('type')}"
                    ))
                
                # 检测约束变更
                old_required = prop_name in old_schema.get("required", [])
                new_required = prop_name in new_schema.get("required", [])
                
                if not old_required and new_required:
                    steps.append(MigrationStep(
                        type=MigrationType.ADD_CONSTRAINT,
                        path=f"properties.{prop_name}",
                        new_value="required",
                        description=f"Make '{prop_name}' required"
                    ))
        
        # 检测required字段变更
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        
        removed_required = old_required - new_required
        added_required = new_required - old_required
        
        for prop in removed_required:
            if not any(s.path == f"properties.{prop}" and s.type == MigrationType.REMOVE_FIELD for s in steps):
                steps.append(MigrationStep(
                    type=MigrationType.REMOVE_CONSTRAINT,
                    path=f"properties.{prop}",
                    old_value="required",
                    description=f"Remove 'required' constraint from '{prop}'"
                ))
        
        return steps
    
    def create_migration_plan(self, old_schema: Dict, new_schema: Dict,
                             from_version: str, to_version: str) -> MigrationPlan:
        """
        创建迁移计划
        
        Args:
            old_schema: 旧版本Schema
            new_schema: 新版本Schema
            from_version: 起始版本
            to_version: 目标版本
        
        Returns:
            MigrationPlan: 迁移计划
        """
        steps = self.compare_schemas(old_schema, new_schema)
        
        # 计算兼容性
        compatibility = self._calculate_compatibility(steps)
        
        # 生成回滚步骤
        rollback_steps = self._generate_rollback_steps(steps)
        
        return MigrationPlan(
            from_version=from_version,
            to_version=to_version,
            steps=steps,
            compatibility=compatibility,
            estimated_impact=len(steps) * 100,  # 简化估计
            rollback_steps=rollback_steps
        )
    
    def _calculate_compatibility(self, steps: List[MigrationStep]) -> CompatibilityLevel:
        """计算兼容性级别"""
        has_breaking = False
        has_additive = False
        
        for step in steps:
            if step.type in [MigrationType.REMOVE_FIELD, MigrationType.CHANGE_TYPE]:
                has_breaking = True
            elif step.type in [MigrationType.ADD_FIELD]:
                has_additive = True
        
        if not has_breaking and not has_additive:
            return CompatibilityLevel.FULL
        elif not has_breaking:
            return CompatibilityLevel.BACKWARD  # 向后兼容（旧代码可读取新数据）
        elif not has_additive:
            return CompatibilityLevel.FORWARD  # 向前兼容（新代码可读取旧数据）
        else:
            return CompatibilityLevel.NONE
    
    def _generate_rollback_steps(self, steps: List[MigrationStep]) -> List[MigrationStep]:
        """生成回滚步骤"""
        rollback = []
        
        for step in reversed(steps):
            if step.type == MigrationType.ADD_FIELD:
                rollback.append(MigrationStep(
                    type=MigrationType.REMOVE_FIELD,
                    path=step.path,
                    description=f"Rollback: {step.description}"
                ))
            elif step.type == MigrationType.REMOVE_FIELD:
                rollback.append(MigrationStep(
                    type=MigrationType.ADD_FIELD,
                    path=step.path,
                    old_value=step.old_value,
                    description=f"Rollback: {step.description}"
                ))
            elif step.type == MigrationType.CHANGE_TYPE:
                rollback.append(MigrationStep(
                    type=MigrationType.CHANGE_TYPE,
                    path=step.path,
                    old_value=step.new_value,
                    new_value=step.old_value,
                    description=f"Rollback: {step.description}"
                ))
        
        return rollback
    
    def migrate_data(self, data: List[Dict], plan: MigrationPlan,
                    dry_run: bool = False) -> MigrationResult:
        """
        执行数据迁移
        
        Args:
            data: 待迁移的数据列表
            plan: 迁移计划
            dry_run: 是否仅模拟，不实际修改
        
        Returns:
            MigrationResult: 迁移结果
        """
        import time
        start_time = time.time()
        
        migrated = 0
        failed = 0
        errors = []
        warnings = []
        
        migrated_data = []
        
        for item in data:
            try:
                new_item = self._apply_migration_steps(item, plan.steps)
                migrated += 1
                migrated_data.append(new_item)
            except Exception as e:
                failed += 1
                errors.append(f"Failed to migrate item: {str(e)}")
        
        duration = (time.time() - start_time) * 1000
        
        if not dry_run:
            # 实际迁移时更新数据
            data.clear()
            data.extend(migrated_data)
        
        return MigrationResult(
            success=failed == 0,
            migrated_count=migrated,
            failed_count=failed,
            errors=errors,
            warnings=warnings,
            duration_ms=duration
        )
    
    def _apply_migration_steps(self, item: Dict, steps: List[MigrationStep]) -> Dict:
        """应用迁移步骤到单个数据项"""
        result = copy.deepcopy(item)
        
        for step in steps:
            path_parts = step.path.split(".")
            
            if step.type == MigrationType.ADD_FIELD:
                if len(path_parts) == 2:  # properties.field
                    field_name = path_parts[1]
                    if field_name not in result:
                        # 使用默认值或null
                        result[field_name] = step.new_value.get("default") if isinstance(step.new_value, dict) else None
            
            elif step.type == MigrationType.REMOVE_FIELD:
                if len(path_parts) == 2:
                    field_name = path_parts[1]
                    if field_name in result:
                        del result[field_name]
            
            elif step.type == MigrationType.CHANGE_TYPE:
                if len(path_parts) == 2:
                    field_name = path_parts[1]
                    if field_name in result and result[field_name] is not None:
                        # 查找转换函数
                        old_type = step.old_value
                        new_type = step.new_value
                        transform_key = f"{old_type}_to_{new_type}"
                        
                        if transform_key in self.transform_registry:
                            result[field_name] = self.transform_registry[transform_key](result[field_name])
            
            elif step.type == MigrationType.RENAME_FIELD:
                # 需要额外处理重命名
                pass
        
        return result
    
    def generate_migration_script(self, plan: MigrationPlan, 
                                 language: str = "python") -> str:
        """
        生成迁移脚本
        
        Args:
            plan: 迁移计划
            language: 目标语言
        
        Returns:
            str: 迁移脚本代码
        """
        if language == "python":
            return self._generate_python_script(plan)
        elif language == "javascript":
            return self._generate_javascript_script(plan)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _generate_python_script(self, plan: MigrationPlan) -> str:
        """生成Python迁移脚本"""
        lines = [
            "#!/usr/bin/env python3",
            f'"""',
            f"Migration from {plan.from_version} to {plan.to_version}",
            f'Compatibility: {plan.compatibility.value}',
            f'Estimated impact: {plan.estimated_impact} records',
            f'"""',
            "",
            "import json",
            "from datetime import datetime",
            "",
            f"def migrate(data):",
            f'    """Migrate data from v{plan.from_version} to v{plan.to_version}"""',
            "    migrated = []",
            "",
            "    for item in data:",
            "        # Apply migration steps",
        ]
        
        for step in plan.steps:
            lines.append(f"        # {step.description}")
            if step.type == MigrationType.ADD_FIELD:
                field = step.path.split(".")[-1]
                default = "None"
                if isinstance(step.new_value, dict) and "default" in step.new_value:
                    default = repr(step.new_value["default"])
                lines.append(f"        if '{field}' not in item:")
                lines.append(f"            item['{field}'] = {default}")
            
            elif step.type == MigrationType.REMOVE_FIELD:
                field = step.path.split(".")[-1]
                lines.append(f"        item.pop('{field}', None)")
        
        lines.extend([
            "",
            "        migrated.append(item)",
            "",
            "    return migrated",
            "",
            'if __name__ == "__main__":',
            '    # Load data',
            '    with open("data.json", "r") as f:',
            '        data = json.load(f)',
            '',
            '    # Migrate',
            '    migrated = migrate(data)',
            '',
            '    # Save',
            '    with open("data_migrated.json", "w") as f:',
            '        json.dump(migrated, f, indent=2)',
        ])
        
        return "\n".join(lines)
    
    def _generate_javascript_script(self, plan: MigrationPlan) -> str:
        """生成JavaScript迁移脚本"""
        lines = [
            "/**",
            f" * Migration from {plan.from_version} to {plan.to_version}",
            f" * Compatibility: {plan.compatibility.value}",
            " */",
            "",
            "function migrate(data) {",
            "    return data.map(item => {",
            "        // Apply migration steps",
        ]
        
        for step in plan.steps:
            lines.append(f"        // {step.description}")
            if step.type == MigrationType.ADD_FIELD:
                field = step.path.split(".")[-1]
                lines.append(f"        if (!('{field}' in item)) {{;")
                lines.append(f"            item['{field}'] = null;")
                lines.append("        }")
        
        lines.extend([
            "        return item;",
            "    });",
            "}",
            "",
            "module.exports = { migrate };",
        ])
        
        return "\n".join(lines)
    
    def validate_migration(self, old_data: List[Dict], new_data: List[Dict],
                          plan: MigrationPlan) -> Tuple[bool, List[str]]:
        """
        验证迁移结果
        
        Args:
            old_data: 原始数据
            new_data: 迁移后的数据
            plan: 迁移计划
        
        Returns:
            (是否有效, 问题列表)
        """
        issues = []
        
        # 检查数据量
        if len(old_data) != len(new_data):
            issues.append(f"Data count mismatch: {len(old_data)} -> {len(new_data)}")
        
        # 检查必需字段
        for step in plan.steps:
            if step.type == MigrationType.ADD_CONSTRAINT and step.new_value == "required":
                field = step.path.split(".")[-1]
                missing_count = sum(1 for item in new_data if field not in item or item[field] is None)
                if missing_count > 0:
                    issues.append(f"Required field '{field}' missing in {missing_count} records")
        
        return len(issues) == 0, issues


def main():
    """示例用法"""
    engine = SchemaMigrationEngine()
    
    # 定义旧版本Schema
    old_schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "version": "1.0.0",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "age": {"type": "string"}  # v1中是字符串
        },
        "required": ["id", "name"]
    }
    
    # 定义新版本Schema
    new_schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "version": "2.0.0",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "fullName": {"type": "string"},  # 重命名
            "age": {"type": "integer"},  # 类型变更
            "email": {"type": "string"}  # 新增字段
        },
        "required": ["id", "fullName", "email"]  # 新增必需字段
    }
    
    print("=" * 60)
    print("Schema迁移分析")
    print("=" * 60)
    
    # 创建迁移计划
    plan = engine.create_migration_plan(old_schema, new_schema, "1.0.0", "2.0.0")
    
    print(f"\n从版本 {plan.from_version} 到 {plan.to_version}")
    print(f"兼容级别: {plan.compatibility.value}")
    print(f"预计影响: {plan.estimated_impact} 条记录")
    print(f"迁移步骤: {len(plan.steps)}")
    
    print("\n迁移步骤:")
    for i, step in enumerate(plan.steps, 1):
        print(f"  {i}. [{step.type.value}] {step.description}")
    
    # 示例数据
    sample_data = [
        {"id": "user-1", "name": "Alice", "age": "30"},
        {"id": "user-2", "name": "Bob", "age": "25"}
    ]
    
    print("\n" + "=" * 60)
    print("数据迁移测试")
    print("=" * 60)
    
    # 执行迁移
    result = engine.migrate_data(sample_data, plan, dry_run=False)
    
    print(f"迁移成功: {result.success}")
    print(f"成功数: {result.migrated_count}")
    print(f"失败数: {result.failed_count}")
    print(f"耗时: {result.duration_ms:.2f}ms")
    
    print("\n迁移后数据:")
    for item in sample_data:
        print(f"  {item}")
    
    # 生成脚本
    print("\n" + "=" * 60)
    print("生成迁移脚本")
    print("=" * 60)
    
    script = engine.generate_migration_script(plan, "python")
    print(script[:1000] + "...")


if __name__ == "__main__":
    main()
