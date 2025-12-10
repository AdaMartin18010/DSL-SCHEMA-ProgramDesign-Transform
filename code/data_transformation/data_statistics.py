"""
数据统计模块

专注于数据统计、聚合统计、统计分析
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import statistics
import logging

logger = logging.getLogger(__name__)


class StatisticType(Enum):
    """统计类型"""
    COUNT = "count"  # 计数
    SUM = "sum"  # 求和
    AVG = "avg"  # 平均值
    MIN = "min"  # 最小值
    MAX = "max"  # 最大值
    MEDIAN = "median"  # 中位数
    STD = "std"  # 标准差
    VARIANCE = "variance"  # 方差
    PERCENTILE = "percentile"  # 百分位数
    DISTINCT = "distinct"  # 去重计数


@dataclass
class StatisticConfig:
    """统计配置"""
    field: str
    statistic_type: StatisticType
    group_by: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    percentile: Optional[float] = None  # 用于百分位数


@dataclass
class StatisticResult:
    """统计结果"""
    statistic_id: str
    config: StatisticConfig
    result: Any
    computed_at: datetime


class DataStatistics:
    """
    数据统计器
    
    专注于数据统计、聚合统计、统计分析
    """
    
    def __init__(self):
        self.statistics_history: List[StatisticResult] = []
        self.data_stores: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_data_store(self, store_id: str, data: List[Dict[str, Any]]):
        """
        注册数据存储
        
        Args:
            store_id: 存储ID
            data: 数据列表
        """
        self.data_stores[store_id] = data
    
    def compute_statistic(self, store_id: str, config: StatisticConfig) -> StatisticResult:
        """
        计算统计
        
        Args:
            store_id: 存储ID
            config: 统计配置
            
        Returns:
            统计结果
        """
        if store_id not in self.data_stores:
            raise ValueError(f"数据存储不存在: {store_id}")
        
        statistic_id = f"stat_{datetime.utcnow().timestamp()}"
        
        data = self.data_stores[store_id].copy()
        
        # 应用过滤
        if config.filters:
            data = self._apply_filters(data, config.filters)
        
        # 计算统计
        if config.group_by:
            result = self._compute_grouped_statistic(data, config)
        else:
            result = self._compute_single_statistic(data, config)
        
        statistic_result = StatisticResult(
            statistic_id=statistic_id,
            config=config,
            result=result,
            computed_at=datetime.utcnow()
        )
        
        self.statistics_history.append(statistic_result)
        return statistic_result
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用过滤"""
        filtered_data = data
        
        for field, condition in filters.items():
            if isinstance(condition, dict):
                # 支持多种条件
                if 'eq' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) == condition['eq']]
                elif 'gt' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) is not None and r.get(field) > condition['gt']]
                elif 'gte' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) is not None and r.get(field) >= condition['gte']]
                elif 'lt' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) is not None and r.get(field) < condition['lt']]
                elif 'lte' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) is not None and r.get(field) <= condition['lte']]
                elif 'in' in condition:
                    filtered_data = [r for r in filtered_data if r.get(field) in condition['in']]
            else:
                # 简单相等
                filtered_data = [r for r in filtered_data if r.get(field) == condition]
        
        return filtered_data
    
    def _compute_single_statistic(self, data: List[Dict[str, Any]], config: StatisticConfig) -> Any:
        """计算单一统计"""
        field = config.field
        statistic_type = config.statistic_type
        
        values = [r.get(field) for r in data if r.get(field) is not None]
        
        if not values:
            return None
        
        if statistic_type == StatisticType.COUNT:
            return len(values)
        
        elif statistic_type == StatisticType.SUM:
            return sum(values) if all(isinstance(v, (int, float)) for v in values) else None
        
        elif statistic_type == StatisticType.AVG:
            return statistics.mean(values) if all(isinstance(v, (int, float)) for v in values) else None
        
        elif statistic_type == StatisticType.MIN:
            return min(values)
        
        elif statistic_type == StatisticType.MAX:
            return max(values)
        
        elif statistic_type == StatisticType.MEDIAN:
            return statistics.median(values) if all(isinstance(v, (int, float)) for v in values) else None
        
        elif statistic_type == StatisticType.STD:
            return statistics.stdev(values) if len(values) > 1 and all(isinstance(v, (int, float)) for v in values) else None
        
        elif statistic_type == StatisticType.VARIANCE:
            return statistics.variance(values) if len(values) > 1 and all(isinstance(v, (int, float)) for v in values) else None
        
        elif statistic_type == StatisticType.PERCENTILE:
            if config.percentile is not None and all(isinstance(v, (int, float)) for v in values):
                return statistics.quantiles(values, n=100)[int(config.percentile * 100) - 1] if config.percentile <= 1.0 else None
            return None
        
        elif statistic_type == StatisticType.DISTINCT:
            return len(set(values))
        
        return None
    
    def _compute_grouped_statistic(self, data: List[Dict[str, Any]], config: StatisticConfig) -> Dict[str, Any]:
        """计算分组统计"""
        group_by = config.group_by
        field = config.field
        statistic_type = config.statistic_type
        
        # 分组
        groups = {}
        for record in data:
            group_key = tuple(record.get(gb) for gb in group_by)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(record)
        
        # 计算每个组的统计
        result = {}
        for group_key, group_data in groups.items():
            group_config = StatisticConfig(
                field=field,
                statistic_type=statistic_type,
                percentile=config.percentile
            )
            group_result = self._compute_single_statistic(group_data, group_config)
            result[str(group_key)] = group_result
        
        return result
    
    def compute_multiple_statistics(self, store_id: str,
                                   configs: List[StatisticConfig]) -> List[StatisticResult]:
        """
        计算多个统计
        
        Args:
            store_id: 存储ID
            configs: 统计配置列表
            
        Returns:
            统计结果列表
        """
        return [self.compute_statistic(store_id, config) for config in configs]
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        获取统计摘要
        
        Returns:
            统计摘要
        """
        total_statistics = len(self.statistics_history)
        
        statistic_type_counts = {}
        for stat in self.statistics_history:
            stat_type = stat.config.statistic_type.value
            statistic_type_counts[stat_type] = statistic_type_counts.get(stat_type, 0) + 1
        
        return {
            'total_statistics': total_statistics,
            'statistic_type_counts': statistic_type_counts
        }


def main():
    """主函数 - 示例用法"""
    stats = DataStatistics()
    
    # 注册数据存储
    stats.register_data_store('sales', [
        {'product': 'A', 'amount': 100, 'quantity': 10},
        {'product': 'A', 'amount': 150, 'quantity': 15},
        {'product': 'B', 'amount': 200, 'quantity': 20}
    ])
    
    # 计算统计
    config = StatisticConfig(
        field='amount',
        statistic_type=StatisticType.SUM,
        group_by=['product']
    )
    
    result = stats.compute_statistic('sales', config)
    print(f"统计结果: {result.result}")


if __name__ == '__main__':
    main()
