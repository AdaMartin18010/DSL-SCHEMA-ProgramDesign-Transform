"""
数据Schema映射模块

专注于Schema映射、字段映射、数据映射
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MappingType(Enum):
    """映射类型"""
    DIRECT = "direct"  # 直接映射
    TRANSFORM = "transform"  # 转换映射
    DEFAULT = "default"  # 默认值映射
    CALCULATE = "calculate"  # 计算映射
    LOOKUP = "lookup"  # 查找映射


@dataclass
class FieldMapping:
    """字段映射"""
    source_field: str
    target_field: str
    mapping_type: MappingType
    transform_func: Optional[Callable] = None
    default_value: Any = None
    lookup_table: Optional[Dict[str, Any]] = None


@dataclass
class SchemaMapping:
    """Schema映射"""
    mapping_id: str
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    field_mappings: List[FieldMapping]
    created_at: datetime = None


class DataSchemaMapper:
    """
    数据Schema映射器
    
    专注于Schema映射、字段映射、数据映射
    """
    
    def __init__(self):
        self.mappings: Dict[str, SchemaMapping] = {}
    
    def create_mapping(self, source_schema: Dict[str, Any],
                      target_schema: Dict[str, Any],
                      field_mappings: List[Dict[str, Any]]) -> SchemaMapping:
        """
        创建Schema映射
        
        Args:
            source_schema: 源Schema
            target_schema: 目标Schema
            field_mappings: 字段映射配置列表
            
        Returns:
            Schema映射对象
        """
        mapping_id = f"mapping_{datetime.utcnow().timestamp()}"
        
        field_mapping_objects = []
        for mapping_config in field_mappings:
            field_mapping = FieldMapping(
                source_field=mapping_config['source_field'],
                target_field=mapping_config['target_field'],
                mapping_type=MappingType(mapping_config.get('mapping_type', 'direct')),
                transform_func=mapping_config.get('transform_func'),
                default_value=mapping_config.get('default_value'),
                lookup_table=mapping_config.get('lookup_table')
            )
            field_mapping_objects.append(field_mapping)
        
        mapping = SchemaMapping(
            mapping_id=mapping_id,
            source_schema=source_schema,
            target_schema=target_schema,
            field_mappings=field_mapping_objects,
            created_at=datetime.utcnow()
        )
        
        self.mappings[mapping_id] = mapping
        return mapping
    
    def apply_mapping(self, mapping_id: str, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用映射
        
        Args:
            mapping_id: 映射ID
            source_data: 源数据
            
        Returns:
            映射后的数据
        """
        if mapping_id not in self.mappings:
            raise ValueError(f"映射不存在: {mapping_id}")
        
        mapping = self.mappings[mapping_id]
        target_data = {}
        
        for field_mapping in mapping.field_mappings:
            source_field = field_mapping.source_field
            target_field = field_mapping.target_field
            mapping_type = field_mapping.mapping_type
            
            # 获取源字段值
            source_value = source_data.get(source_field) if source_field in source_data else None
            
            # 应用映射
            if mapping_type == MappingType.DIRECT:
                target_value = source_value
            
            elif mapping_type == MappingType.TRANSFORM:
                if field_mapping.transform_func:
                    try:
                        target_value = field_mapping.transform_func(source_value)
                    except Exception as e:
                        logger.warning(f"转换失败: {source_field} -> {target_field}, 错误: {e}")
                        target_value = None
                else:
                    target_value = source_value
            
            elif mapping_type == MappingType.DEFAULT:
                target_value = source_value if source_value is not None else field_mapping.default_value
            
            elif mapping_type == MappingType.CALCULATE:
                if field_mapping.transform_func:
                    try:
                        target_value = field_mapping.transform_func(source_data)
                    except Exception as e:
                        logger.warning(f"计算失败: {target_field}, 错误: {e}")
                        target_value = None
                else:
                    target_value = None
            
            elif mapping_type == MappingType.LOOKUP:
                if field_mapping.lookup_table and source_value:
                    target_value = field_mapping.lookup_table.get(source_value)
                else:
                    target_value = None
            
            else:
                target_value = source_value
            
            # 设置目标字段值
            if target_value is not None:
                target_data[target_field] = target_value
        
        return target_data
    
    def batch_apply_mapping(self, mapping_id: str,
                           source_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量应用映射
        
        Args:
            mapping_id: 映射ID
            source_data_list: 源数据列表
            
        Returns:
            映射后的数据列表
        """
        return [self.apply_mapping(mapping_id, data) for data in source_data_list]
    
    def validate_mapping(self, mapping_id: str) -> Dict[str, Any]:
        """
        验证映射
        
        Args:
            mapping_id: 映射ID
            
        Returns:
            验证结果
        """
        if mapping_id not in self.mappings:
            return {
                'valid': False,
                'error': '映射不存在'
            }
        
        mapping = self.mappings[mapping_id]
        errors = []
        warnings = []
        
        # 验证源Schema字段
        source_fields = set(mapping.source_schema.get('fields', {}).keys())
        for field_mapping in mapping.field_mappings:
            if field_mapping.source_field not in source_fields:
                warnings.append(f"源字段不存在: {field_mapping.source_field}")
        
        # 验证目标Schema字段
        target_fields = set(mapping.target_schema.get('fields', {}).keys())
        for field_mapping in mapping.field_mappings:
            if field_mapping.target_field not in target_fields:
                errors.append(f"目标字段不存在: {field_mapping.target_field}")
        
        # 验证映射函数
        for field_mapping in mapping.field_mappings:
            if field_mapping.mapping_type == MappingType.TRANSFORM:
                if not field_mapping.transform_func:
                    errors.append(f"转换映射缺少转换函数: {field_mapping.source_field} -> {field_mapping.target_field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_mapping_summary(self, mapping_id: str) -> Dict[str, Any]:
        """
        获取映射摘要
        
        Args:
            mapping_id: 映射ID
            
        Returns:
            映射摘要
        """
        if mapping_id not in self.mappings:
            return {'error': '映射不存在'}
        
        mapping = self.mappings[mapping_id]
        
        mapping_type_counts = {}
        for field_mapping in mapping.field_mappings:
            mapping_type = field_mapping.mapping_type.value
            mapping_type_counts[mapping_type] = mapping_type_counts.get(mapping_type, 0) + 1
        
        return {
            'mapping_id': mapping_id,
            'source_schema': mapping.source_schema.get('name', ''),
            'target_schema': mapping.target_schema.get('name', ''),
            'field_count': len(mapping.field_mappings),
            'mapping_type_counts': mapping_type_counts,
            'created_at': mapping.created_at.isoformat() if mapping.created_at else None
        }


def main():
    """主函数 - 示例用法"""
    mapper = DataSchemaMapper()
    
    # 创建映射
    source_schema = {
        'name': 'source_schema',
        'fields': {'id': 'integer', 'name': 'string', 'age': 'integer'}
    }
    
    target_schema = {
        'name': 'target_schema',
        'fields': {'user_id': 'integer', 'user_name': 'string', 'user_age': 'integer'}
    }
    
    field_mappings = [
        {
            'source_field': 'id',
            'target_field': 'user_id',
            'mapping_type': 'direct'
        },
        {
            'source_field': 'name',
            'target_field': 'user_name',
            'mapping_type': 'direct'
        },
        {
            'source_field': 'age',
            'target_field': 'user_age',
            'mapping_type': 'direct'
        }
    ]
    
    mapping = mapper.create_mapping(source_schema, target_schema, field_mappings)
    
    # 应用映射
    source_data = {'id': 1, 'name': 'Alice', 'age': 25}
    target_data = mapper.apply_mapping(mapping.mapping_id, source_data)
    print(f"映射结果: {target_data}")


if __name__ == '__main__':
    main()
