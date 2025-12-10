"""
数据转换模板模块

专注于数据转换模板、模板管理、模板应用
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import copy

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """模板类型"""
    TRANSFORMATION = "transformation"  # 转换模板
    VALIDATION = "validation"  # 验证模板
    MAPPING = "mapping"  # 映射模板
    AGGREGATION = "aggregation"  # 聚合模板
    FILTER = "filter"  # 过滤模板
    CUSTOM = "custom"  # 自定义模板


@dataclass
class TransformationTemplate:
    """转换模板"""
    template_id: str
    template_name: str
    template_type: TemplateType
    template_config: Dict[str, Any]
    parameters: Dict[str, Any]
    created_at: datetime


class DataTransformationTemplate:
    """
    数据转换模板器
    
    专注于数据转换模板、模板管理、模板应用
    """
    
    def __init__(self):
        self.templates: Dict[str, TransformationTemplate] = {}
    
    def create_template(self, template_config: Dict[str, Any]) -> TransformationTemplate:
        """
        创建模板
        
        Args:
            template_config: 模板配置
            
        Returns:
            转换模板对象
        """
        template_id = template_config.get('template_id', f"template_{datetime.utcnow().timestamp()}")
        
        template = TransformationTemplate(
            template_id=template_id,
            template_name=template_config.get('template_name', ''),
            template_type=TemplateType(template_config.get('template_type', 'transformation')),
            template_config=template_config.get('template_config', {}),
            parameters=template_config.get('parameters', {}),
            created_at=datetime.utcnow()
        )
        
        self.templates[template_id] = template
        return template
    
    def apply_template(self, template_id: str, data: Any, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        应用模板
        
        Args:
            template_id: 模板ID
            data: 数据
            parameters: 参数（可选）
            
        Returns:
            转换后的数据
        """
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        # 合并参数
        merged_parameters = {**template.parameters, **(parameters or {})}
        
        # 根据模板类型应用
        if template.template_type == TemplateType.TRANSFORMATION:
            return self._apply_transformation_template(template, data, merged_parameters)
        elif template.template_type == TemplateType.VALIDATION:
            return self._apply_validation_template(template, data, merged_parameters)
        elif template.template_type == TemplateType.MAPPING:
            return self._apply_mapping_template(template, data, merged_parameters)
        elif template.template_type == TemplateType.AGGREGATION:
            return self._apply_aggregation_template(template, data, merged_parameters)
        elif template.template_type == TemplateType.FILTER:
            return self._apply_filter_template(template, data, merged_parameters)
        else:
            return self._apply_custom_template(template, data, merged_parameters)
    
    def _apply_transformation_template(self, template: TransformationTemplate, data: Any, parameters: Dict[str, Any]) -> Any:
        """应用转换模板"""
        config = template.template_config
        result = copy.deepcopy(data)
        
        # 字段映射
        if 'field_mapping' in config:
            if isinstance(result, dict):
                for old_field, new_field in config['field_mapping'].items():
                    if old_field in result:
                        result[new_field] = result.pop(old_field)
        
        # 字段转换
        if 'field_transforms' in config:
            if isinstance(result, dict):
                for field, transform_config in config['field_transforms'].items():
                    if field in result:
                        transform_type = transform_config.get('type')
                        if transform_type == 'uppercase':
                            result[field] = str(result[field]).upper()
                        elif transform_type == 'lowercase':
                            result[field] = str(result[field]).lower()
                        elif transform_type == 'trim':
                            result[field] = str(result[field]).strip()
        
        return result
    
    def _apply_validation_template(self, template: TransformationTemplate, data: Any, parameters: Dict[str, Any]) -> bool:
        """应用验证模板"""
        config = template.template_config
        
        # 必填字段验证
        if 'required_fields' in config:
            if isinstance(data, dict):
                for field in config['required_fields']:
                    if field not in data or data[field] is None:
                        return False
        
        # 类型验证
        if 'type_validation' in config:
            if isinstance(data, dict):
                for field, expected_type in config['type_validation'].items():
                    if field in data and not isinstance(data[field], expected_type):
                        return False
        
        return True
    
    def _apply_mapping_template(self, template: TransformationTemplate, data: Any, parameters: Dict[str, Any]) -> Any:
        """应用映射模板"""
        config = template.template_config
        
        if isinstance(data, dict) and 'field_mapping' in config:
            result = {}
            for old_field, new_field in config['field_mapping'].items():
                if old_field in data:
                    result[new_field] = data[old_field]
            return result
        
        return data
    
    def _apply_aggregation_template(self, template: TransformationTemplate, data: Any, parameters: Dict[str, Any]) -> Any:
        """应用聚合模板"""
        config = template.template_config
        
        if isinstance(data, list) and 'aggregation' in config:
            agg_type = config['aggregation'].get('type')
            field = config['aggregation'].get('field')
            
            if agg_type == 'sum':
                return sum(item.get(field, 0) for item in data if isinstance(item, dict))
            elif agg_type == 'avg':
                values = [item.get(field, 0) for item in data if isinstance(item, dict)]
                return sum(values) / len(values) if values else 0
            elif agg_type == 'count':
                return len(data)
            elif agg_type == 'max':
                values = [item.get(field) for item in data if isinstance(item, dict) and field in item]
                return max(values) if values else None
            elif agg_type == 'min':
                values = [item.get(field) for item in data if isinstance(item, dict) and field in item]
                return min(values) if values else None
        
        return data
    
    def _apply_filter_template(self, template: TransformationTemplate, data: Any, parameters: Dict[str, Any]) -> Any:
        """应用过滤模板"""
        config = template.template_config
        
        if isinstance(data, list) and 'filter' in config:
            filter_config = config['filter']
            field = filter_config.get('field')
            operator = filter_config.get('operator')
            value = filter_config.get('value')
            
            def filter_func(item):
                if not isinstance(item, dict) or field not in item:
                    return False
                
                item_value = item[field]
                if operator == 'eq':
                    return item_value == value
                elif operator == 'ne':
                    return item_value != value
                elif operator == 'gt':
                    return item_value > value
                elif operator == 'gte':
                    return item_value >= value
                elif operator == 'lt':
                    return item_value < value
                elif operator == 'lte':
                    return item_value <= value
                return False
            
            return [item for item in data if filter_func(item)]
        
        return data
    
    def _apply_custom_template(self, template: TransformationTemplate, data: Any, parameters: Dict[str, Any]) -> Any:
        """应用自定义模板"""
        # 自定义模板需要用户提供自定义函数
        custom_func = template.template_config.get('custom_func')
        if custom_func:
            return custom_func(data, parameters)
        return data
    
    def get_template_list(self) -> List[Dict[str, Any]]:
        """
        获取模板列表
        
        Returns:
            模板列表
        """
        return [
            {
                'template_id': t.template_id,
                'template_name': t.template_name,
                'template_type': t.template_type.value,
                'created_at': t.created_at.isoformat()
            }
            for t in self.templates.values()
        ]


def main():
    """主函数 - 示例用法"""
    template_manager = DataTransformationTemplate()
    
    # 创建模板
    template = template_manager.create_template({
        'template_name': '字段映射模板',
        'template_type': 'mapping',
        'template_config': {
            'field_mapping': {
                'old_name': 'new_name',
                'old_age': 'new_age'
            }
        }
    })
    
    print(f"模板已创建: {template.template_id}")


if __name__ == '__main__':
    main()
