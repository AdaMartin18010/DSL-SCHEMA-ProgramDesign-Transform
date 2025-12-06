"""
数据聚合器

专注于数据聚合操作
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import defaultdict


class AggregationFunction(Enum):
    """聚合函数"""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STD = "std"
    VARIANCE = "variance"
    FIRST = "first"
    LAST = "last"


@dataclass
class AggregationConfig:
    """聚合配置"""
    config_id: str
    group_by_fields: List[str]
    aggregate_fields: Dict[str, AggregationFunction]
    created_at: datetime


class DataAggregator:
    """
    数据聚合器
    
    专注于数据聚合操作
    """
    
    def __init__(self):
        self.configs: Dict[str, AggregationConfig] = {}
    
    def aggregate(self, data: List[Dict[str, Any]], group_by_fields: List[str],
                  aggregate_fields: Dict[str, AggregationFunction]) -> List[Dict[str, Any]]:
        """
        聚合数据
        
        Args:
            data: 数据列表
            group_by_fields: 分组字段
            aggregate_fields: 聚合字段和函数
            
        Returns:
            聚合后的数据列表
        """
        if not data:
            return []
        
        # 按分组字段分组
        groups = defaultdict(list)
        
        for record in data:
            # 生成分组键
            group_key = tuple(record.get(field) for field in group_by_fields)
            groups[group_key].append(record)
        
        # 对每个组进行聚合
        aggregated_data = []
        
        for group_key, group_records in groups.items():
            aggregated_record = {}
            
            # 添加分组字段
            for i, field in enumerate(group_by_fields):
                aggregated_record[field] = group_key[i]
            
            # 聚合字段
            for field, agg_func in aggregate_fields.items():
                values = [r.get(field) for r in group_records if field in r and r[field] is not None]
                
                if values:
                    aggregated_value = self._apply_aggregation(values, agg_func)
                    aggregated_record[field] = aggregated_value
                else:
                    aggregated_record[field] = None
            
            aggregated_data.append(aggregated_record)
        
        return aggregated_data
    
    def _apply_aggregation(self, values: List[Any], agg_func: AggregationFunction) -> Any:
        """应用聚合函数"""
        if not values:
            return None
        
        # 过滤数值类型
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        
        if agg_func == AggregationFunction.SUM:
            return sum(numeric_values) if numeric_values else None
        elif agg_func == AggregationFunction.AVG:
            return sum(numeric_values) / len(numeric_values) if numeric_values else None
        elif agg_func == AggregationFunction.COUNT:
            return len(values)
        elif agg_func == AggregationFunction.MIN:
            return min(numeric_values) if numeric_values else None
        elif agg_func == AggregationFunction.MAX:
            return max(numeric_values) if numeric_values else None
        elif agg_func == AggregationFunction.STD:
            if len(numeric_values) > 1:
                mean = sum(numeric_values) / len(numeric_values)
                variance = sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
                return variance ** 0.5
            return 0.0
        elif agg_func == AggregationFunction.VARIANCE:
            if len(numeric_values) > 1:
                mean = sum(numeric_values) / len(numeric_values)
                return sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
            return 0.0
        elif agg_func == AggregationFunction.FIRST:
            return values[0] if values else None
        elif agg_func == AggregationFunction.LAST:
            return values[-1] if values else None
        else:
            return None
    
    def pivot(self, data: List[Dict[str, Any]], index_field: str,
              column_field: str, value_field: str,
              agg_func: AggregationFunction = AggregationFunction.SUM) -> List[Dict[str, Any]]:
        """
        数据透视
        
        Args:
            data: 数据列表
            index_field: 索引字段
            column_field: 列字段
            value_field: 值字段
            agg_func: 聚合函数
            
        Returns:
            透视后的数据列表
        """
        # 按索引和列分组
        pivot_data = defaultdict(lambda: defaultdict(list))
        
        for record in data:
            index_value = record.get(index_field)
            column_value = record.get(column_field)
            value = record.get(value_field)
            
            if index_value is not None and column_value is not None and value is not None:
                pivot_data[index_value][column_value].append(value)
        
        # 构建透视表
        result = []
        all_columns = set()
        
        for index_value in pivot_data:
            all_columns.update(pivot_data[index_value].keys())
        
        for index_value in pivot_data:
            row = {index_field: index_value}
            
            for column_value in all_columns:
                if column_value in pivot_data[index_value]:
                    values = pivot_data[index_value][column_value]
                    row[column_value] = self._apply_aggregation(values, agg_func)
                else:
                    row[column_value] = None
            
            result.append(row)
        
        return result


def main():
    """主函数 - 示例用法"""
    aggregator = DataAggregator()
    
    # 示例数据
    data = [
        {'region': 'North', 'product': 'A', 'sales': 1000},
        {'region': 'North', 'product': 'B', 'sales': 1500},
        {'region': 'South', 'product': 'A', 'sales': 1200},
        {'region': 'South', 'product': 'B', 'sales': 1800},
    ]
    
    # 聚合
    aggregated = aggregator.aggregate(
        data,
        group_by_fields=['region'],
        aggregate_fields={'sales': AggregationFunction.SUM}
    )
    
    print("聚合结果:")
    for record in aggregated:
        print(record)
    
    # 透视
    pivoted = aggregator.pivot(
        data,
        index_field='region',
        column_field='product',
        value_field='sales'
    )
    
    print("\n透视结果:")
    for record in pivoted:
        print(record)


if __name__ == '__main__':
    main()
