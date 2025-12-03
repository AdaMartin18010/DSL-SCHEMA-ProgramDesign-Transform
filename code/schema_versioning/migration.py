"""
版本迁移工具

实现Schema版本间的迁移
"""

from typing import Dict, Any, Optional, List
import uuid
from .storage import SchemaVersioningStorage
from .version_control import SchemaVersionControl
from .compatibility import CompatibilityChecker


class SchemaMigrationTool:
    """Schema迁移工具"""
    
    def __init__(self, storage: SchemaVersioningStorage):
        """
        初始化迁移工具
        
        Args:
            storage: Schema版本管理存储管理器
        """
        self.storage = storage
        self.version_control = SchemaVersionControl(storage)
        self.compatibility_checker = CompatibilityChecker(storage)
    
    def migrate(self, schema_id: str, from_version: str, to_version: str,
               data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行迁移
        
        Args:
            schema_id: Schema ID
            from_version: 源版本
            to_version: 目标版本
            data: 要迁移的数据
            
        Returns:
            迁移后的数据
        """
        # 1. 检查兼容性
        compatibility = self.compatibility_checker.check_compatibility(
            schema_id, from_version, to_version
        )
        
        if compatibility.get('is_compatible') == 0:
            return {
                'success': False,
                'error': '版本不兼容，无法自动迁移',
                'breaking_changes': compatibility.get('breaking_changes', [])
            }
        
        # 2. 获取版本信息
        from_schema = self.version_control.get_version(schema_id, from_version)
        to_schema = self.version_control.get_version(schema_id, to_version)
        
        if not from_schema or not to_schema:
            return {
                'success': False,
                'error': '版本不存在'
            }
        
        # 3. 执行迁移
        migrated_data = self._apply_migration(
            data,
            from_schema.get('schema_content', {}),
            to_schema.get('schema_content', {})
        )
        
        # 4. 记录迁移
        migration_id = f"migration_{uuid.uuid4().hex[:16]}"
        # 保存迁移记录（需要扩展storage方法）
        
        return {
            'success': True,
            'migration_id': migration_id,
            'migrated_data': migrated_data,
            'compatibility': compatibility
        }
    
    def _apply_migration(self, data: Dict[str, Any],
                        from_schema: Dict[str, Any],
                        to_schema: Dict[str, Any]) -> Dict[str, Any]:
        """应用迁移"""
        migrated_data = data.copy()
        
        # 处理删除的字段
        from_fields = set(from_schema.get('fields', {}).keys())
        to_fields = set(to_schema.get('fields', {}).keys())
        removed_fields = from_fields - to_fields
        
        for field in removed_fields:
            if field in migrated_data:
                del migrated_data[field]
        
        # 处理新增的字段（使用默认值）
        added_fields = to_fields - from_fields
        for field in added_fields:
            field_def = to_schema.get('fields', {}).get(field, {})
            if 'default' in field_def:
                migrated_data[field] = field_def['default']
        
        # 处理修改的字段（类型转换等）
        modified_fields = []
        for field in from_fields & to_fields:
            from_field_def = from_schema.get('fields', {}).get(field, {})
            to_field_def = to_schema.get('fields', {}).get(field, {})
            
            if from_field_def.get('type') != to_field_def.get('type'):
                # 类型转换
                migrated_data[field] = self._convert_type(
                    migrated_data.get(field),
                    from_field_def.get('type'),
                    to_field_def.get('type')
                )
                modified_fields.append(field)
        
        return migrated_data
    
    def _convert_type(self, value: Any, from_type: str, to_type: str) -> Any:
        """类型转换"""
        # 简化实现
        if from_type == 'string' and to_type == 'integer':
            try:
                return int(value)
            except:
                return 0
        elif from_type == 'integer' and to_type == 'string':
            return str(value)
        # 其他类型转换...
        
        return value
    
    def generate_migration_script(self, schema_id: str, from_version: str,
                                  to_version: str) -> str:
        """
        生成迁移脚本
        
        Args:
            schema_id: Schema ID
            from_version: 源版本
            to_version: 目标版本
            
        Returns:
            迁移脚本
        """
        # 获取版本比较结果
        comparison = self.version_control.compare_versions(
            schema_id, from_version, to_version
        )
        
        differences = comparison.get('differences', {})
        
        # 生成迁移脚本
        script_lines = [
            f"-- Migration script: {from_version} -> {to_version}",
            f"-- Schema ID: {schema_id}",
            ""
        ]
        
        # 处理删除的字段
        if differences.get('removed'):
            script_lines.append("-- Remove fields:")
            for field in differences['removed']:
                script_lines.append(f"--   ALTER TABLE ... DROP COLUMN {field};")
        
        # 处理新增的字段
        if differences.get('added'):
            script_lines.append("-- Add fields:")
            for field in differences['added']:
                script_lines.append(f"--   ALTER TABLE ... ADD COLUMN {field};")
        
        # 处理修改的字段
        if differences.get('modified'):
            script_lines.append("-- Modify fields:")
            for field in differences['modified']:
                script_lines.append(f"--   ALTER TABLE ... ALTER COLUMN {field};")
        
        return "\n".join(script_lines)
