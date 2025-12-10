"""
数据转换引擎模块

专注于统一的数据转换引擎、转换规则管理、转换执行
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """转换类型"""
    TYPE_CAST = "type_cast"  # 类型转换
    VALUE_MAP = "value_map"  # 值映射
    FORMAT_CONVERT = "format_convert"  # 格式转换
    AGGREGATE = "aggregate"  # 聚合
    CALCULATE = "calculate"  # 计算
    FILTER = "filter"  # 过滤
    JOIN = "join"  # 关联
    CUSTOM = "custom"  # 自定义


@dataclass
class TransformationRule:
    """转换规则"""
    rule_id: str
    name: str
    transformation_type: TransformationType
    source_field: str
    target_field: str
    rule_config: Dict[str, Any]
    enabled: bool = True


@dataclass
class TransformationResult:
    """转换结果"""
    transformation_id: str
    rule_id: str
    input_data: Any
    output_data: Any
    success: bool
    execution_time: float
    error: Optional[str] = None


class DataTransformationEngine:
    """
    数据转换引擎
    
    专注于统一的数据转换引擎、转换规则管理、转换执行
    """
    
    def __init__(self):
        self.rules: Dict[str, TransformationRule] = {}
        self.transformation_history: List[TransformationResult] = []
    
    def add_rule(self, rule_config: Dict[str, Any]) -> TransformationRule:
        """
        添加转换规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            转换规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = TransformationRule(
            rule_id=rule_id,
            name=rule_config.get('name', ''),
            transformation_type=TransformationType(rule_config.get('transformation_type', 'type_cast')),
            source_field=rule_config['source_field'],
            target_field=rule_config.get('target_field', rule_config['source_field']),
            rule_config=rule_config.get('rule_config', {}),
            enabled=rule_config.get('enabled', True)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def transform(self, data: Dict[str, Any], rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        转换数据
        
        Args:
            data: 数据字典
            rule_ids: 规则ID列表（可选，默认使用所有规则）
            
        Returns:
            转换后的数据
        """
        transformed_data = data.copy()
        
        # 确定要使用的规则
        rules_to_use = rule_ids if rule_ids else [r.rule_id for r in self.rules.values() if r.enabled]
        
        for rule_id in rules_to_use:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            
            if not rule.enabled:
                continue
            
            # 执行转换
            start_time = datetime.utcnow()
            
            try:
                result = self._apply_transformation(transformed_data, rule)
                transformed_data.update(result)
                
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()
                
                transformation_result = TransformationResult(
                    transformation_id=f"trans_{datetime.utcnow().timestamp()}",
                    rule_id=rule_id,
                    input_data=data.get(rule.source_field),
                    output_data=result.get(rule.target_field),
                    success=True,
                    execution_time=execution_time
                )
                
                self.transformation_history.append(transformation_result)
            
            except Exception as e:
                logger.error(f"转换失败: {rule_id}, 错误: {e}")
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()
                
                transformation_result = TransformationResult(
                    transformation_id=f"trans_{datetime.utcnow().timestamp()}",
                    rule_id=rule_id,
                    input_data=data.get(rule.source_field),
                    output_data=None,
                    success=False,
                    execution_time=execution_time,
                    error=str(e)
                )
                
                self.transformation_history.append(transformation_result)
        
        return transformed_data
    
    def _apply_transformation(self, data: Dict[str, Any], rule: TransformationRule) -> Dict[str, Any]:
        """应用转换规则"""
        source_value = data.get(rule.source_field)
        transformation_type = rule.transformation_type
        config = rule.rule_config
        
        result = {}
        
        if transformation_type == TransformationType.TYPE_CAST:
            # 类型转换
            target_type = config.get('target_type', 'string')
            if target_type == 'integer':
                result[rule.target_field] = int(source_value) if source_value is not None else None
            elif target_type == 'float':
                result[rule.target_field] = float(source_value) if source_value is not None else None
            elif target_type == 'string':
                result[rule.target_field] = str(source_value) if source_value is not None else None
            elif target_type == 'boolean':
                result[rule.target_field] = bool(source_value) if source_value is not None else None
            else:
                result[rule.target_field] = source_value
        
        elif transformation_type == TransformationType.VALUE_MAP:
            # 值映射
            value_map = config.get('value_map', {})
            result[rule.target_field] = value_map.get(source_value, config.get('default_value', source_value))
        
        elif transformation_type == TransformationType.FORMAT_CONVERT:
            # 格式转换
            format_func = config.get('formatter')
            if format_func and callable(format_func):
                result[rule.target_field] = format_func(source_value)
            else:
                result[rule.target_field] = source_value
        
        elif transformation_type == TransformationType.CALCULATE:
            # 计算
            formula = config.get('formula')
            if formula and callable(formula):
                result[rule.target_field] = formula(data)
            else:
                result[rule.target_field] = source_value
        
        elif transformation_type == TransformationType.FILTER:
            # 过滤
            filter_func = config.get('filter')
            if filter_func and callable(filter_func):
                if filter_func(source_value):
                    result[rule.target_field] = source_value
            else:
                result[rule.target_field] = source_value
        
        elif transformation_type == TransformationType.CUSTOM:
            # 自定义转换
            transform_func = config.get('transform')
            if transform_func and callable(transform_func):
                result[rule.target_field] = transform_func(source_value, data)
            else:
                result[rule.target_field] = source_value
        
        else:
            result[rule.target_field] = source_value
        
        return result
    
    def batch_transform(self, data_list: List[Dict[str, Any]],
                       rule_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        批量转换数据
        
        Args:
            data_list: 数据列表
            rule_ids: 规则ID列表（可选）
            
        Returns:
            转换后的数据列表
        """
        return [self.transform(data, rule_ids) for data in data_list]
    
    def get_transformation_stats(self) -> Dict[str, Any]:
        """
        获取转换统计
        
        Returns:
            转换统计
        """
        total_transformations = len(self.transformation_history)
        successful_transformations = sum(1 for t in self.transformation_history if t.success)
        failed_transformations = total_transformations - successful_transformations
        
        if total_transformations > 0:
            avg_time = sum(t.execution_time for t in self.transformation_history) / total_transformations
        else:
            avg_time = 0.0
        
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled),
            'total_transformations': total_transformations,
            'successful_transformations': successful_transformations,
            'failed_transformations': failed_transformations,
            'success_rate': (successful_transformations / total_transformations * 100) if total_transformations > 0 else 0.0,
            'average_execution_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    engine = DataTransformationEngine()
    
    # 添加转换规则
    rule = engine.add_rule({
        'name': '类型转换',
        'source_field': 'age',
        'target_field': 'age_int',
        'transformation_type': 'type_cast',
        'rule_config': {
            'target_type': 'integer'
        }
    })
    
    # 转换数据
    data = {'age': '25', 'name': 'Alice'}
    transformed = engine.transform(data, [rule.rule_id])
    print(f"转换结果: {transformed}")


if __name__ == '__main__':
    main()
