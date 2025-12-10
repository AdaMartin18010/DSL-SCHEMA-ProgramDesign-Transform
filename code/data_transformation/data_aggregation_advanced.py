"""
高级数据聚合模块

专注于高级数据聚合、多维度聚合、聚合函数扩展
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import statistics
import logging

logger = logging.getLogger(__name__)


class AggregationFunction(Enum):
    """聚合函数"""
    SUM = "sum"  # 求和
    AVG = "avg"  # 平均值
    MIN = "min"  # 最小值
    MAX = "max"  # 最大值
    COUNT = "count"  # 计数
    MEDIAN = "median"  # 中位数
    STD = "std"  # 标准差
    VARIANCE = "variance"  # 方差
    PERCENTILE = "percentile"  # 百分位数
    DISTINCT_COUNT = "distinct_count"  # 去重计数
    FIRST = "first"  # 第一个值
    LAST = "last"  # 最后一个值


@dataclass
class AggregationConfig:
    """聚合配置"""
    group_by: List[str]  # 分组字段
    aggregations: Dict[str, AggregationFunction]  # 字段到聚合函数的映射
    having: Optional[Callable[[Dict[str, Any]], bool]] = None  # HAVING条件


@dataclass
class AggregationResult:
    """聚合结果"""
    aggregation_id: str
    groups: List[Dict[str, Any]]
    aggregation_time: float
    total_groups: int


class DataAggregationAdvanced:
    """
    高级数据聚合器
    
    专注于高级数据聚合、多维度聚合、聚合函数扩展
    """
    
    def __init__(self):
        self.aggregation_history: List[AggregationResult] = []
    
    def aggregate(self, data: List[Dict[str, Any]], config: AggregationConfig) -> AggregationResult:
        """
        聚合数据
        
        Args:
            data: 数据列表
            config: 聚合配置
            
        Returns:
            聚合结果
        """
        aggregation_id = f"agg_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        # 分组
        groups = self._group_data(data, config.group_by)
        
        # 对每个组进行聚合
        aggregated_groups = []
        for group_key, group_data in groups.items():
            aggregated_record = dict(group_key)
            
            for field, agg_func in config.aggregations.items():
                values = [r.get(field) for r in group_data if r.get(field) is not None]
                if values:
                    aggregated_value = self._apply_aggregation(values, agg_func)
                    aggregated_record[field] = aggregated_value
            
            # 应用HAVING条件
            if config.having is None or config.having(aggregated_record):
                aggregated_groups.append(aggregated_record)
        
        end_time = datetime.utcnow()
        aggregation_time = (end_time - start_time).total_seconds()
        
        result = AggregationResult(
            aggregation_id=aggregation_id,
            groups=aggregated_groups,
            aggregation_time=aggregation_time,
            total_groups=len(aggregated_groups)
        )
        
        self.aggregation_history.append(result)
        return result
    
    def _group_data(self, data: List[Dict[str, Any]], group_by: List[str]) -> Dict[tuple, List[Dict[str, Any]]]:
        """分组数据"""
        groups = {}
        
        for record in data:
            group_key = tuple(record.get(field) for field in group_by)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(record)
        
        return groups
    
    def _apply_aggregation(self, values: List[Any], agg_func: AggregationFunction) -> Any:
        """应用聚合函数"""
        if not values:
            return None
        
        if agg_func == AggregationFunction.SUM:
            return sum(v for v in values if isinstance(v, (int, float)))
        
        elif agg_func == AggregationFunction.AVG:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            return statistics.mean(numeric_values) if numeric_values else None
        
        elif agg_func == AggregationFunction.MIN:
            return min(values)
        
        elif agg_func == AggregationFunction.MAX:
            return max(values)
        
        elif agg_func == AggregationFunction.COUNT:
            return len(values)
        
        elif agg_func == AggregationFunction.MEDIAN:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            return statistics.median(numeric_values) if numeric_values else None
        
        elif agg_func == AggregationFunction.STD:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            return statistics.stdev(numeric_values) if len(numeric_values) > 1 else None
        
        elif agg_func == AggregationFunction.VARIANCE:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            return statistics.variance(numeric_values) if len(numeric_values) > 1 else None
        
        elif agg_func == AggregationFunction.PERCENTILE:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                sorted_values = sorted(numeric_values)
                index = int(len(sorted_values) * 0.5)  # 50th percentile
                return sorted_values[index]
            return None
        
        elif agg_func == AggregationFunction.DISTINCT_COUNT:
            return len(set(values))
        
        elif agg_func == AggregationFunction.FIRST:
            return values[0]
        
        elif agg_func == AggregationFunction.LAST:
            return values[-1]
        
        return None
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """
        获取聚合统计
        
        Returns:
            聚合统计
        """
        total_aggregations = len(self.aggregation_history)
        total_groups = sum(r.total_groups for r in self.aggregation_history)
        
        if total_aggregations > 0:
            avg_time = sum(r.aggregation_time for r in self.aggregation_history) / total_aggregations
        else:
            avg_time = 0.0
        
        return {
            'total_aggregations': total_aggregations,
            'total_groups': total_groups,
            'average_groups_per_aggregation': total_groups / total_aggregations if total_aggregations > 0 else 0.0,
            'average_aggregation_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    aggregator = DataAggregationAdvanced()
    
    # 聚合数据
    data = [
        {'category': 'A', 'value': 10},
        {'category': 'A', 'value': 20},
        {'category': 'B', 'value': 30}
    ]
    
    config = AggregationConfig(
        group_by=['category'],
        aggregations={'value': AggregationFunction.SUM}
    )
    
    result = aggregator.aggregate(data, config)
    print(f"聚合结果: 组数={result.total_groups}")


if __name__ == '__main__':
    main()
