"""
数据转换构建器模块

专注于数据转换构建、转换模板、转换配置管理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BuilderType(Enum):
    """构建器类型"""
    TEMPLATE = "template"  # 模板构建
    CUSTOM = "custom"  # 自定义构建
    WIZARD = "wizard"  # 向导构建


@dataclass
class TransformationTemplate:
    """转换模板"""
    template_id: str
    template_name: str
    description: str
    steps: List[Dict[str, Any]]
    parameters: Dict[str, Any] = None


@dataclass
class TransformationBuilder:
    """转换构建器"""
    builder_id: str
    builder_name: str
    builder_type: BuilderType
    template: Optional[TransformationTemplate] = None
    config: Dict[str, Any] = None


class DataTransformationBuilder:
    """
    数据转换构建器
    
    专注于数据转换构建、转换模板、转换配置管理
    """
    
    def __init__(self):
        self.templates: Dict[str, TransformationTemplate] = {}
        self.builders: Dict[str, TransformationBuilder] = {}
    
    def create_template(self, template_config: Dict[str, Any]) -> TransformationTemplate:
        """
        创建转换模板
        
        Args:
            template_config: 模板配置
            
        Returns:
            转换模板对象
        """
        template_id = template_config.get('template_id', f"template_{datetime.utcnow().timestamp()}")
        
        template = TransformationTemplate(
            template_id=template_id,
            template_name=template_config.get('template_name', ''),
            description=template_config.get('description', ''),
            steps=template_config.get('steps', []),
            parameters=template_config.get('parameters', {})
        )
        
        self.templates[template_id] = template
        return template
    
    def create_builder(self, builder_config: Dict[str, Any]) -> TransformationBuilder:
        """
        创建转换构建器
        
        Args:
            builder_config: 构建器配置
            
        Returns:
            转换构建器对象
        """
        builder_id = builder_config.get('builder_id', f"builder_{datetime.utcnow().timestamp()}")
        
        template_id = builder_config.get('template_id')
        template = self.templates.get(template_id) if template_id else None
        
        builder = TransformationBuilder(
            builder_id=builder_id,
            builder_name=builder_config.get('builder_name', ''),
            builder_type=BuilderType(builder_config.get('builder_type', 'custom')),
            template=template,
            config=builder_config.get('config', {})
        )
        
        self.builders[builder_id] = builder
        return builder
    
    def build_transformation(self, builder_id: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        构建转换
        
        Args:
            builder_id: 构建器ID
            data: 数据列表
            
        Returns:
            转换后的数据
        """
        if builder_id not in self.builders:
            raise ValueError(f"构建器不存在: {builder_id}")
        
        builder = self.builders[builder_id]
        result_data = data.copy()
        
        if builder.template:
            # 使用模板构建
            for step in builder.template.steps:
                step_type = step.get('type')
                step_config = step.get('config', {})
                
                if step_type == 'transform':
                    result_data = self._apply_transform(result_data, step_config)
                elif step_type == 'filter':
                    result_data = self._apply_filter(result_data, step_config)
                elif step_type == 'aggregate':
                    result_data = self._apply_aggregate(result_data, step_config)
        else:
            # 自定义构建
            if builder.config:
                result_data = self._apply_custom_build(result_data, builder.config)
        
        return result_data
    
    def _apply_transform(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用转换"""
        field = config.get('field')
        transform_type = config.get('transform_type')
        
        if not field:
            return data
        
        transformed_data = []
        for record in data:
            transformed_record = record.copy()
            value = record.get(field)
            
            if transform_type == 'uppercase' and isinstance(value, str):
                transformed_record[field] = value.upper()
            elif transform_type == 'lowercase' and isinstance(value, str):
                transformed_record[field] = value.lower()
            elif transform_type == 'multiply' and isinstance(value, (int, float)):
                multiplier = config.get('multiplier', 1)
                transformed_record[field] = value * multiplier
            
            transformed_data.append(transformed_record)
        
        return transformed_data
    
    def _apply_filter(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用过滤"""
        field = config.get('field')
        condition = config.get('condition')
        value = config.get('value')
        
        if not field:
            return data
        
        filtered_data = []
        for record in data:
            field_value = record.get(field)
            
            if condition == 'eq' and field_value == value:
                filtered_data.append(record)
            elif condition == 'gt' and isinstance(field_value, (int, float)) and field_value > value:
                filtered_data.append(record)
            elif condition == 'lt' and isinstance(field_value, (int, float)) and field_value < value:
                filtered_data.append(record)
        
        return filtered_data
    
    def _apply_aggregate(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用聚合"""
        # 简化实现
        return data
    
    def _apply_custom_build(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用自定义构建"""
        # 简化实现
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
                'description': t.description,
                'steps_count': len(t.steps)
            }
            for t in self.templates.values()
        ]


def main():
    """主函数 - 示例用法"""
    builder_manager = DataTransformationBuilder()
    
    # 创建模板
    template = builder_manager.create_template({
        'template_name': '数据清理模板',
        'description': '标准数据清理流程',
        'steps': [
            {'type': 'transform', 'config': {'field': 'name', 'transform_type': 'uppercase'}},
            {'type': 'filter', 'config': {'field': 'age', 'condition': 'gt', 'value': 18}}
        ]
    })
    
    # 创建构建器
    builder = builder_manager.create_builder({
        'builder_name': '清理构建器',
        'builder_type': 'template',
        'template_id': template.template_id
    })
    
    # 构建转换
    data = [{'name': 'alice', 'age': 25}, {'name': 'bob', 'age': 15}]
    result = builder_manager.build_transformation(builder.builder_id, data)
    print(f"构建结果: 记录数={len(result)}")


if __name__ == '__main__':
    main()
