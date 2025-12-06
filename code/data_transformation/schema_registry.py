"""
Schema注册表

专注于Schema版本管理和注册
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SchemaStatus(Enum):
    """Schema状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 活跃
    DEPRECATED = "deprecated"  # 已弃用
    ARCHIVED = "archived"  # 已归档


@dataclass
class SchemaVersion:
    """Schema版本"""
    version_id: str
    schema_id: str
    version: str  # 版本号（如 1.0.0）
    schema_definition: Dict[str, Any]
    status: SchemaStatus
    created_at: datetime
    created_by: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class Schema:
    """Schema"""
    schema_id: str
    name: str
    namespace: str
    description: Optional[str] = None
    tags: List[str] = None
    versions: List[SchemaVersion] = None
    current_version: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None


class SchemaRegistry:
    """
    Schema注册表
    
    专注于Schema版本管理和注册
    """
    
    def __init__(self):
        self.schemas: Dict[str, Schema] = {}
        self.versions: Dict[str, SchemaVersion] = {}
    
    def register_schema(self, schema_config: Dict[str, Any]) -> Schema:
        """
        注册Schema
        
        Args:
            schema_config: Schema配置
            
        Returns:
            Schema对象
        """
        schema_id = schema_config.get('schema_id', f"schema_{datetime.utcnow().timestamp()}")
        
        schema = Schema(
            schema_id=schema_id,
            name=schema_config.get('name', ''),
            namespace=schema_config.get('namespace', 'default'),
            description=schema_config.get('description'),
            tags=schema_config.get('tags', []),
            versions=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.schemas[schema_id] = schema
        return schema
    
    def register_version(self, schema_id: str, version_config: Dict[str, Any]) -> SchemaVersion:
        """
        注册Schema版本
        
        Args:
            schema_id: Schema ID
            version_config: 版本配置
            
        Returns:
            Schema版本对象
        """
        if schema_id not in self.schemas:
            raise ValueError(f"Schema不存在: {schema_id}")
        
        version = version_config.get('version', '1.0.0')
        version_id = f"{schema_id}_v{version}"
        
        schema_version = SchemaVersion(
            version_id=version_id,
            schema_id=schema_id,
            version=version,
            schema_definition=version_config.get('schema_definition', {}),
            status=SchemaStatus(version_config.get('status', 'draft')),
            created_at=datetime.utcnow(),
            created_by=version_config.get('created_by'),
            description=version_config.get('description'),
            metadata=version_config.get('metadata', {})
        )
        
        self.versions[version_id] = schema_version
        
        # 更新Schema的版本列表
        schema = self.schemas[schema_id]
        schema.versions.append(schema_version)
        schema.current_version = version
        schema.updated_at = datetime.utcnow()
        
        return schema_version
    
    def get_schema(self, schema_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取Schema
        
        Args:
            schema_id: Schema ID
            version: 版本号（可选，默认使用当前版本）
            
        Returns:
            Schema定义
        """
        if schema_id not in self.schemas:
            return None
        
        schema = self.schemas[schema_id]
        
        if version:
            version_id = f"{schema_id}_v{version}"
            if version_id in self.versions:
                return self.versions[version_id].schema_definition
        else:
            # 使用当前版本
            if schema.current_version:
                version_id = f"{schema_id}_v{schema.current_version}"
                if version_id in self.versions:
                    return self.versions[version_id].schema_definition
        
        return None
    
    def list_schemas(self, namespace: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> List[Schema]:
        """
        列出Schema
        
        Args:
            namespace: 命名空间（可选）
            tags: 标签列表（可选）
            
        Returns:
            Schema列表
        """
        results = []
        
        for schema in self.schemas.values():
            if namespace and schema.namespace != namespace:
                continue
            
            if tags:
                if not any(tag in schema.tags for tag in tags):
                    continue
            
            results.append(schema)
        
        return results
    
    def get_version_history(self, schema_id: str) -> List[SchemaVersion]:
        """
        获取版本历史
        
        Args:
            schema_id: Schema ID
            
        Returns:
            版本历史列表
        """
        if schema_id not in self.schemas:
            return []
        
        schema = self.schemas[schema_id]
        return sorted(schema.versions, key=lambda v: v.created_at, reverse=True)
    
    def deprecate_version(self, schema_id: str, version: str):
        """
        弃用版本
        
        Args:
            schema_id: Schema ID
            version: 版本号
        """
        version_id = f"{schema_id}_v{version}"
        
        if version_id in self.versions:
            self.versions[version_id].status = SchemaStatus.DEPRECATED
    
    def compare_versions(self, schema_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        比较两个版本
        
        Args:
            schema_id: Schema ID
            version1: 版本1
            version2: 版本2
            
        Returns:
            比较结果
        """
        version1_id = f"{schema_id}_v{version1}"
        version2_id = f"{schema_id}_v{version2}"
        
        if version1_id not in self.versions or version2_id not in self.versions:
            return {
                'error': '版本不存在'
            }
        
        v1 = self.versions[version1_id].schema_definition
        v2 = self.versions[version2_id].schema_definition
        
        # 简化实现：比较表结构
        differences = {
            'tables_added': [],
            'tables_removed': [],
            'tables_modified': []
        }
        
        v1_tables = set(v1.get('tables', {}).keys())
        v2_tables = set(v2.get('tables', {}).keys())
        
        differences['tables_added'] = list(v2_tables - v1_tables)
        differences['tables_removed'] = list(v1_tables - v2_tables)
        differences['tables_modified'] = list(v1_tables & v2_tables)
        
        return {
            'schema_id': schema_id,
            'version1': version1,
            'version2': version2,
            'differences': differences
        }


def main():
    """主函数 - 示例用法"""
    registry = SchemaRegistry()
    
    # 注册Schema
    schema = registry.register_schema({
        'name': 'sales_schema',
        'namespace': 'warehouse',
        'description': '销售数据Schema',
        'tags': ['sales', 'warehouse']
    })
    
    print(f"注册Schema: {schema.schema_id}")
    
    # 注册版本
    version1 = registry.register_version(schema.schema_id, {
        'version': '1.0.0',
        'schema_definition': {
            'tables': {
                'sales': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'amount': {'type': 'decimal'}
                    }
                }
            }
        },
        'status': 'active'
    })
    
    print(f"注册版本: {version1.version_id}")
    
    # 获取Schema
    schema_def = registry.get_schema(schema.schema_id)
    print(f"获取Schema: {schema_def is not None}")


if __name__ == '__main__':
    main()
