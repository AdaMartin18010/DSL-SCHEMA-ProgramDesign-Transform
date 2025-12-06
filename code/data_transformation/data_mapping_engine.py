"""
数据映射引擎

专注于数据字段映射和转换
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FieldMapping:
    """字段映射"""
    mapping_id: str
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    default_value: Optional[Any] = None
    required: bool = False


@dataclass
class SchemaMapping:
    """Schema映射"""
    mapping_id: str
    source_schema: str
    target_schema: str
    field_mappings: List[FieldMapping]
    created_at: datetime


class DataMappingEngine:
    """
    数据映射引擎
    
    专注于数据字段映射和转换
    """
    
    def __init__(self):
        self.mappings: Dict[str, SchemaMapping] = {}
    
    def create_mapping(self, mapping_config: Dict[str, Any]) -> SchemaMapping:
        """
        创建Schema映射
        
        Args:
            mapping_config: 映射配置
            
        Returns:
            Schema映射对象
        """
        mapping_id = mapping_config.get('mapping_id', f"mapping_{datetime.utcnow().timestamp()}")
        
        field_mappings = []
        for fm_config in mapping_config.get('field_mappings', []):
            field_mapping = FieldMapping(
                mapping_id=f"{mapping_id}_field_{len(field_mappings)}",
                source_field=fm_config.get('source_field', ''),
                target_field=fm_config.get('target_field', ''),
                transformation=fm_config.get('transformation'),
                default_value=fm_config.get('default_value'),
                required=fm_config.get('required', False)
            )
            field_mappings.append(field_mapping)
        
        mapping = SchemaMapping(
            mapping_id=mapping_id,
            source_schema=mapping_config.get('source_schema', ''),
            target_schema=mapping_config.get('target_schema', ''),
            field_mappings=field_mappings,
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
            
            # 获取源字段值
            if source_field in source_data:
                value = source_data[source_field]
                
                # 应用转换
                if field_mapping.transformation:
                    value = self._apply_transformation(value, field_mapping.transformation)
                
                target_data[target_field] = value
            elif field_mapping.required:
                # 必需字段缺失，使用默认值或抛出错误
                if field_mapping.default_value is not None:
                    target_data[target_field] = field_mapping.default_value
                else:
                    raise ValueError(f"必需字段缺失: {source_field}")
            elif field_mapping.default_value is not None:
                # 使用默认值
                target_data[target_field] = field_mapping.default_value
        
        return target_data
    
    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """应用转换"""
        # 简化实现：支持基本转换
        if transformation == 'uppercase':
            return str(value).upper() if value else ''
        elif transformation == 'lowercase':
            return str(value).lower() if value else ''
        elif transformation == 'trim':
            return str(value).strip() if value else ''
        elif transformation.startswith('cast:'):
            target_type = transformation.split(':')[1]
            try:
                if target_type == 'int':
                    return int(value)
                elif target_type == 'float':
                    return float(value)
                elif target_type == 'str':
                    return str(value)
            except:
                return value
        else:
            return value
    
    def batch_apply_mapping(self, mapping_id: str, source_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量应用映射
        
        Args:
            mapping_id: 映射ID
            source_data_list: 源数据列表
            
        Returns:
            映射后的数据列表
        """
        return [self.apply_mapping(mapping_id, data) for data in source_data_list]
    
    def validate_mapping(self, mapping_id: str, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证映射
        
        Args:
            mapping_id: 映射ID
            sample_data: 样本数据
            
        Returns:
            验证结果
        """
        if mapping_id not in self.mappings:
            return {'valid': False, 'error': '映射不存在'}
        
        mapping = self.mappings[mapping_id]
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for field_mapping in mapping.field_mappings:
            source_field = field_mapping.source_field
            
            if field_mapping.required:
                if source_field not in sample_data:
                    validation_result['valid'] = False
                    validation_result['errors'].append(
                        f"必需字段缺失: {source_field}"
                    )
            elif source_field not in sample_data and field_mapping.default_value is None:
                validation_result['warnings'].append(
                    f"字段缺失且无默认值: {source_field}"
                )
        
        return validation_result


def main():
    """主函数 - 示例用法"""
    engine = DataMappingEngine()
    
    # 创建映射
    mapping = engine.create_mapping({
        'source_schema': 'source_schema',
        'target_schema': 'target_schema',
        'field_mappings': [
            {
                'source_field': 'user_id',
                'target_field': 'id',
                'transformation': 'cast:int',
                'required': True
            },
            {
                'source_field': 'user_name',
                'target_field': 'name',
                'transformation': 'trim',
                'required': True
            },
            {
                'source_field': 'user_email',
                'target_field': 'email',
                'transformation': 'lowercase',
                'required': False
            }
        ]
    })
    
    # 应用映射
    source_data = {
        'user_id': '123',
        'user_name': '  John Doe  ',
        'user_email': 'JOHN@EXAMPLE.COM'
    }
    
    target_data = engine.apply_mapping(mapping.mapping_id, source_data)
    print(f"映射结果: {target_data}")


if __name__ == '__main__':
    main()
