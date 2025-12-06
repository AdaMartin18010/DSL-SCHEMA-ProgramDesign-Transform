"""
Schema迁移器

专注于Schema版本迁移和数据迁移
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MigrationType(Enum):
    """迁移类型"""
    SCHEMA_MIGRATION = "schema_migration"  # Schema迁移
    DATA_MIGRATION = "data_migration"  # 数据迁移
    FULL_MIGRATION = "full_migration"  # 完整迁移


@dataclass
class MigrationStep:
    """迁移步骤"""
    step_id: str
    step_type: str  # 步骤类型（create_table, alter_table, migrate_data等）
    description: str
    sql_statements: List[str]  # SQL语句
    rollback_statements: List[str]  # 回滚语句
    dependencies: List[str] = None  # 依赖的步骤ID
    estimated_duration: int = 0  # 预计耗时（秒）


@dataclass
class MigrationPlan:
    """迁移计划"""
    plan_id: str
    source_version: str  # 源版本
    target_version: str  # 目标版本
    migration_type: MigrationType
    steps: List[MigrationStep]
    created_at: datetime
    estimated_total_duration: int = 0  # 预计总耗时（秒）


@dataclass
class MigrationResult:
    """迁移结果"""
    migration_id: str
    plan_id: str
    success: bool
    executed_steps: List[str]  # 已执行的步骤ID
    failed_steps: List[str]  # 失败的步骤ID
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # 耗时（秒）
    error_message: Optional[str] = None


class SchemaMigrator:
    """
    Schema迁移器
    
    专注于Schema版本迁移和数据迁移
    """
    
    def __init__(self):
        self.migration_plans: Dict[str, MigrationPlan] = {}
        self.migration_history: List[MigrationResult] = []
    
    def create_migration_plan(self, source_schema: Dict[str, Any],
                              target_schema: Dict[str, Any],
                              source_version: str,
                              target_version: str,
                              migration_type: MigrationType = MigrationType.FULL_MIGRATION) -> MigrationPlan:
        """
        创建迁移计划
        
        Args:
            source_schema: 源Schema
            target_schema: 目标Schema
            source_version: 源版本
            target_version: 目标版本
            migration_type: 迁移类型
            
        Returns:
            迁移计划
        """
        plan_id = f"migration_{source_version}_to_{target_version}_{datetime.utcnow().timestamp()}"
        
        steps = []
        
        # 分析Schema差异
        schema_diff = self._analyze_schema_diff(source_schema, target_schema)
        
        # 生成迁移步骤
        if migration_type in [MigrationType.SCHEMA_MIGRATION, MigrationType.FULL_MIGRATION]:
            schema_steps = self._generate_schema_migration_steps(schema_diff)
            steps.extend(schema_steps)
        
        if migration_type in [MigrationType.DATA_MIGRATION, MigrationType.FULL_MIGRATION]:
            data_steps = self._generate_data_migration_steps(schema_diff, source_schema, target_schema)
            steps.extend(data_steps)
        
        # 计算依赖关系
        steps = self._resolve_dependencies(steps)
        
        # 计算预计总耗时
        estimated_total_duration = sum(step.estimated_duration for step in steps)
        
        plan = MigrationPlan(
            plan_id=plan_id,
            source_version=source_version,
            target_version=target_version,
            migration_type=migration_type,
            steps=steps,
            created_at=datetime.utcnow(),
            estimated_total_duration=estimated_total_duration
        )
        
        self.migration_plans[plan_id] = plan
        return plan
    
    def _analyze_schema_diff(self, source_schema: Dict[str, Any],
                            target_schema: Dict[str, Any]) -> Dict[str, Any]:
        """分析Schema差异"""
        diff = {
            'tables_to_create': [],
            'tables_to_drop': [],
            'tables_to_alter': [],
            'fields_to_add': [],
            'fields_to_remove': [],
            'fields_to_modify': []
        }
        
        source_tables = source_schema.get('tables', {})
        target_tables = target_schema.get('tables', {})
        
        # 找出需要创建的表
        for table_name in target_tables:
            if table_name not in source_tables:
                diff['tables_to_create'].append({
                    'table_name': table_name,
                    'table_def': target_tables[table_name]
                })
        
        # 找出需要删除的表
        for table_name in source_tables:
            if table_name not in target_tables:
                diff['tables_to_drop'].append({
                    'table_name': table_name,
                    'table_def': source_tables[table_name]
                })
        
        # 找出需要修改的表
        for table_name in target_tables:
            if table_name in source_tables:
                source_table = source_tables[table_name]
                target_table = target_tables[table_name]
                
                source_fields = source_table.get('fields', {})
                target_fields = target_table.get('fields', {})
                
                # 找出需要添加的字段
                for field_name in target_fields:
                    if field_name not in source_fields:
                        diff['fields_to_add'].append({
                            'table_name': table_name,
                            'field_name': field_name,
                            'field_def': target_fields[field_name]
                        })
                
                # 找出需要删除的字段
                for field_name in source_fields:
                    if field_name not in target_fields:
                        diff['fields_to_remove'].append({
                            'table_name': table_name,
                            'field_name': field_name,
                            'field_def': source_fields[field_name]
                        })
                
                # 找出需要修改的字段
                for field_name in target_fields:
                    if field_name in source_fields:
                        source_field = source_fields[field_name]
                        target_field = target_fields[field_name]
                        
                        if source_field != target_field:
                            diff['fields_to_modify'].append({
                                'table_name': table_name,
                                'field_name': field_name,
                                'old_field_def': source_field,
                                'new_field_def': target_field
                            })
                
                # 如果表有变化，添加到需要修改的表列表
                if diff['fields_to_add'] or diff['fields_to_remove'] or diff['fields_to_modify']:
                    diff['tables_to_alter'].append({
                        'table_name': table_name,
                        'source_table': source_table,
                        'target_table': target_table
                    })
        
        return diff
    
    def _generate_schema_migration_steps(self, schema_diff: Dict[str, Any]) -> List[MigrationStep]:
        """生成Schema迁移步骤"""
        steps = []
        
        # 创建表的步骤
        for table_info in schema_diff['tables_to_create']:
            table_name = table_info['table_name']
            table_def = table_info['table_def']
            
            sql_statements = [self._generate_create_table_sql(table_name, table_def)]
            rollback_statements = [f"DROP TABLE IF EXISTS {table_name};"]
            
            step = MigrationStep(
                step_id=f"create_table_{table_name}",
                step_type='create_table',
                description=f"创建表 {table_name}",
                sql_statements=sql_statements,
                rollback_statements=rollback_statements,
                estimated_duration=5
            )
            steps.append(step)
        
        # 修改表的步骤
        for table_info in schema_diff['tables_to_alter']:
            table_name = table_info['table_name']
            
            sql_statements = []
            rollback_statements = []
            
            # 添加字段
            for field_info in schema_diff['fields_to_add']:
                if field_info['table_name'] == table_name:
                    field_name = field_info['field_name']
                    field_def = field_info['field_def']
                    
                    sql_statements.append(
                        self._generate_add_column_sql(table_name, field_name, field_def)
                    )
                    rollback_statements.append(
                        f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {field_name};"
                    )
            
            # 删除字段
            for field_info in schema_diff['fields_to_remove']:
                if field_info['table_name'] == table_name:
                    field_name = field_info['field_name']
                    field_def = field_info['field_def']
                    
                    sql_statements.append(
                        f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {field_name};"
                    )
                    rollback_statements.append(
                        self._generate_add_column_sql(table_name, field_name, field_def)
                    )
            
            # 修改字段
            for field_info in schema_diff['fields_to_modify']:
                if field_info['table_name'] == table_name:
                    field_name = field_info['field_name']
                    new_field_def = field_info['new_field_def']
                    old_field_def = field_info['old_field_def']
                    
                    sql_statements.append(
                        self._generate_modify_column_sql(table_name, field_name, new_field_def)
                    )
                    rollback_statements.append(
                        self._generate_modify_column_sql(table_name, field_name, old_field_def)
                    )
            
            if sql_statements:
                step = MigrationStep(
                    step_id=f"alter_table_{table_name}",
                    step_type='alter_table',
                    description=f"修改表 {table_name}",
                    sql_statements=sql_statements,
                    rollback_statements=rollback_statements,
                    estimated_duration=10
                )
                steps.append(step)
        
        # 删除表的步骤（放在最后）
        for table_info in schema_diff['tables_to_drop']:
            table_name = table_info['table_name']
            table_def = table_info['table_def']
            
            sql_statements = [f"DROP TABLE IF EXISTS {table_name};"]
            rollback_statements = [self._generate_create_table_sql(table_name, table_def)]
            
            step = MigrationStep(
                step_id=f"drop_table_{table_name}",
                step_type='drop_table',
                description=f"删除表 {table_name}",
                sql_statements=sql_statements,
                rollback_statements=rollback_statements,
                estimated_duration=3
            )
            steps.append(step)
        
        return steps
    
    def _generate_data_migration_steps(self, schema_diff: Dict[str, Any],
                                      source_schema: Dict[str, Any],
                                      target_schema: Dict[str, Any]) -> List[MigrationStep]:
        """生成数据迁移步骤"""
        steps = []
        
        # 为每个需要迁移的表生成数据迁移步骤
        for table_info in schema_diff['tables_to_alter']:
            table_name = table_info['table_name']
            source_table = table_info['source_table']
            target_table = table_info['target_table']
            
            # 生成数据迁移SQL
            sql_statements = [
                f"-- 迁移表 {table_name} 的数据",
                f"-- 注意：需要根据实际字段映射调整"
            ]
            
            rollback_statements = [
                f"-- 回滚表 {table_name} 的数据迁移",
                f"-- 注意：需要根据实际情况实现"
            ]
            
            step = MigrationStep(
                step_id=f"migrate_data_{table_name}",
                step_type='migrate_data',
                description=f"迁移表 {table_name} 的数据",
                sql_statements=sql_statements,
                rollback_statements=rollback_statements,
                estimated_duration=30,
                dependencies=[f"alter_table_{table_name}"]
            )
            steps.append(step)
        
        return steps
    
    def _resolve_dependencies(self, steps: List[MigrationStep]) -> List[MigrationStep]:
        """解析依赖关系"""
        # 简化实现：根据步骤类型设置依赖
        step_map = {step.step_id: step for step in steps}
        
        for step in steps:
            if step.dependencies is None:
                step.dependencies = []
            
            # 如果步骤需要修改表，应该依赖创建表的步骤
            if step.step_type == 'alter_table':
                table_name = step.step_id.replace('alter_table_', '')
                create_step_id = f"create_table_{table_name}"
                if create_step_id in step_map:
                    step.dependencies.append(create_step_id)
        
        return steps
    
    def _generate_create_table_sql(self, table_name: str, table_def: Dict[str, Any]) -> str:
        """生成CREATE TABLE SQL"""
        fields = []
        
        for field_name, field_def in table_def.get('fields', {}).items():
            field_type = field_def.get('type', 'TEXT')
            nullable = '' if field_def.get('nullable', True) else ' NOT NULL'
            fields.append(f"  {field_name} {field_type}{nullable}")
        
        sql = f"CREATE TABLE {table_name} (\n"
        sql += ",\n".join(fields)
        
        if 'primary_key' in table_def:
            pk = table_def['primary_key']
            sql += f",\n  PRIMARY KEY ({pk})"
        
        sql += "\n);"
        return sql
    
    def _generate_add_column_sql(self, table_name: str, field_name: str, field_def: Dict[str, Any]) -> str:
        """生成ADD COLUMN SQL"""
        field_type = field_def.get('type', 'TEXT')
        nullable = '' if field_def.get('nullable', True) else ' NOT NULL'
        return f"ALTER TABLE {table_name} ADD COLUMN {field_name} {field_type}{nullable};"
    
    def _generate_modify_column_sql(self, table_name: str, field_name: str, field_def: Dict[str, Any]) -> str:
        """生成MODIFY COLUMN SQL"""
        field_type = field_def.get('type', 'TEXT')
        nullable = '' if field_def.get('nullable', True) else ' NOT NULL'
        return f"ALTER TABLE {table_name} ALTER COLUMN {field_name} TYPE {field_type}{nullable};"
    
    def execute_migration(self, plan_id: str, dry_run: bool = False) -> MigrationResult:
        """
        执行迁移
        
        Args:
            plan_id: 迁移计划ID
            dry_run: 是否仅模拟运行
            
        Returns:
            迁移结果
        """
        if plan_id not in self.migration_plans:
            return MigrationResult(
                migration_id=f"migration_{datetime.utcnow().timestamp()}",
                plan_id=plan_id,
                success=False,
                executed_steps=[],
                failed_steps=[],
                start_time=datetime.utcnow(),
                error_message=f"迁移计划不存在: {plan_id}"
            )
        
        plan = self.migration_plans[plan_id]
        migration_id = f"migration_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        executed_steps = []
        failed_steps = []
        
        try:
            # 按依赖顺序执行步骤
            remaining_steps = plan.steps.copy()
            completed_steps = set()
            
            while remaining_steps:
                progress = False
                
                for step in remaining_steps[:]:
                    # 检查依赖是否完成
                    if step.dependencies:
                        if not all(dep in completed_steps for dep in step.dependencies):
                            continue
                    
                    # 执行步骤
                    if not dry_run:
                        # 实际执行SQL语句（简化实现）
                        for sql in step.sql_statements:
                            # 这里应该实际执行SQL
                            pass
                    
                    executed_steps.append(step.step_id)
                    completed_steps.add(step.step_id)
                    remaining_steps.remove(step)
                    progress = True
                
                if not progress:
                    # 无法继续执行（可能是依赖问题）
                    break
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            success = len(failed_steps) == 0 and len(executed_steps) == len(plan.steps)
            
            result = MigrationResult(
                migration_id=migration_id,
                plan_id=plan_id,
                success=success,
                executed_steps=executed_steps,
                failed_steps=failed_steps,
                start_time=start_time,
                end_time=end_time,
                duration=int(duration)
            )
            
            self.migration_history.append(result)
            return result
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            result = MigrationResult(
                migration_id=migration_id,
                plan_id=plan_id,
                success=False,
                executed_steps=executed_steps,
                failed_steps=failed_steps,
                start_time=start_time,
                end_time=end_time,
                duration=int(duration),
                error_message=str(e)
            )
            
            self.migration_history.append(result)
            return result
    
    def get_migration_history(self, plan_id: Optional[str] = None,
                              limit: int = 100) -> List[MigrationResult]:
        """
        获取迁移历史
        
        Args:
            plan_id: 迁移计划ID（可选）
            limit: 返回数量限制
            
        Returns:
            迁移历史列表
        """
        history = self.migration_history
        
        if plan_id:
            history = [h for h in history if h.plan_id == plan_id]
        
        return sorted(history, key=lambda x: x.start_time, reverse=True)[:limit]


def main():
    """主函数 - 示例用法"""
    migrator = SchemaMigrator()
    
    # 源Schema
    source_schema = {
        'tables': {
            'users': {
                'fields': {
                    'id': {'type': 'INTEGER'},
                    'name': {'type': 'VARCHAR(255)'}
                },
                'primary_key': 'id'
            }
        }
    }
    
    # 目标Schema
    target_schema = {
        'tables': {
            'users': {
                'fields': {
                    'id': {'type': 'INTEGER'},
                    'name': {'type': 'VARCHAR(255)'},
                    'email': {'type': 'VARCHAR(255)'}  # 新增字段
                },
                'primary_key': 'id'
            }
        }
    }
    
    # 创建迁移计划
    plan = migrator.create_migration_plan(
        source_schema,
        target_schema,
        'v1.0',
        'v2.0',
        MigrationType.FULL_MIGRATION
    )
    
    print(f"创建迁移计划: {plan.plan_id}")
    print(f"迁移步骤数: {len(plan.steps)}")
    print(f"预计总耗时: {plan.estimated_total_duration}秒")
    
    # 执行迁移（模拟运行）
    result = migrator.execute_migration(plan.plan_id, dry_run=True)
    print(f"迁移结果: {'成功' if result.success else '失败'}")
    print(f"执行步骤数: {len(result.executed_steps)}")


if __name__ == '__main__':
    main()
