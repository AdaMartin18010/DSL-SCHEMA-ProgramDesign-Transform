"""
数据转换指标模块

专注于数据转换指标、指标收集、指标分析
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型"""
    EXECUTION_TIME = "execution_time"  # 执行时间
    THROUGHPUT = "throughput"  # 吞吐量
    ERROR_RATE = "error_rate"  # 错误率
    SUCCESS_RATE = "success_rate"  # 成功率
    DATA_VOLUME = "data_volume"  # 数据量
    RESOURCE_USAGE = "resource_usage"  # 资源使用


@dataclass
class Metric:
    """指标"""
    metric_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class MetricSummary:
    """指标摘要"""
    metric_type: MetricType
    count: int
    min_value: float
    max_value: float
    avg_value: float
    latest_value: float
    period_start: datetime
    period_end: datetime


class DataTransformationMetrics:
    """
    数据转换指标器
    
    专注于数据转换指标、指标收集、指标分析
    """
    
    def __init__(self):
        self.metrics: List[Metric] = []
    
    def record_metric(self, metric_type: MetricType, value: float,
                     metadata: Optional[Dict[str, Any]] = None) -> Metric:
        """
        记录指标
        
        Args:
            metric_type: 指标类型
            value: 指标值
            metadata: 元数据
            
        Returns:
            指标对象
        """
        metric_id = f"metric_{datetime.utcnow().timestamp()}"
        
        metric = Metric(
            metric_id=metric_id,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # 只保留最近10000条指标
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-10000:]
        
        return metric
    
    def get_metric_summary(self, metric_type: MetricType,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> MetricSummary:
        """
        获取指标摘要
        
        Args:
            metric_type: 指标类型
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            指标摘要
        """
        filtered_metrics = [m for m in self.metrics if m.metric_type == metric_type]
        
        if start_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
        
        if end_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
        
        if not filtered_metrics:
            return MetricSummary(
                metric_type=metric_type,
                count=0,
                min_value=0.0,
                max_value=0.0,
                avg_value=0.0,
                latest_value=0.0,
                period_start=start_time or datetime.utcnow(),
                period_end=end_time or datetime.utcnow()
            )
        
        values = [m.value for m in filtered_metrics]
        
        return MetricSummary(
            metric_type=metric_type,
            count=len(filtered_metrics),
            min_value=min(values),
            max_value=max(values),
            avg_value=sum(values) / len(values),
            latest_value=filtered_metrics[-1].value,
            period_start=filtered_metrics[0].timestamp,
            period_end=filtered_metrics[-1].timestamp
        )
    
    def get_metrics_by_type(self, metric_type: MetricType,
                           limit: int = 100) -> List[Metric]:
        """
        按类型获取指标
        
        Args:
            metric_type: 指标类型
            limit: 限制数量
            
        Returns:
            指标列表
        """
        filtered_metrics = [m for m in self.metrics if m.metric_type == metric_type]
        return sorted(filtered_metrics, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """
        获取所有指标摘要
        
        Returns:
            所有指标摘要
        """
        summaries = {}
        
        for metric_type in MetricType:
            summary = self.get_metric_summary(metric_type)
            summaries[metric_type.value] = {
                'count': summary.count,
                'min_value': summary.min_value,
                'max_value': summary.max_value,
                'avg_value': summary.avg_value,
                'latest_value': summary.latest_value
            }
        
        return {
            'total_metrics': len(self.metrics),
            'summaries': summaries
        }


def main():
    """主函数 - 示例用法"""
    metrics = DataTransformationMetrics()
    
    # 记录指标
    metric = metrics.record_metric(MetricType.EXECUTION_TIME, 1.5)
    print(f"指标已记录: {metric.metric_type.value}={metric.value}")


if __name__ == '__main__':
    main()
