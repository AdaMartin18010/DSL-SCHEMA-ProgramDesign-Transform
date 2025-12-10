"""
数据性能模块

专注于性能监控、性能优化、性能分析
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """性能指标"""
    EXECUTION_TIME = "execution_time"  # 执行时间
    THROUGHPUT = "throughput"  # 吞吐量
    LATENCY = "latency"  # 延迟
    MEMORY_USAGE = "memory_usage"  # 内存使用
    CPU_USAGE = "cpu_usage"  # CPU使用
    IO_OPERATIONS = "io_operations"  # IO操作


@dataclass
class PerformanceRecord:
    """性能记录"""
    record_id: str
    operation: str
    metric: PerformanceMetric
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceThreshold:
    """性能阈值"""
    operation: str
    metric: PerformanceMetric
    threshold: float
    alert_on_exceed: bool = True


class DataPerformance:
    """
    数据性能监控器
    
    专注于性能监控、性能优化、性能分析
    """
    
    def __init__(self):
        self.performance_records: List[PerformanceRecord] = []
        self.thresholds: Dict[str, PerformanceThreshold] = {}
    
    def record_operation(self, operation: str, execution_time: float,
                       metadata: Optional[Dict[str, Any]] = None) -> PerformanceRecord:
        """
        记录操作性能
        
        Args:
            operation: 操作名称
            execution_time: 执行时间（秒）
            metadata: 元数据
            
        Returns:
            性能记录对象
        """
        record_id = f"perf_{datetime.utcnow().timestamp()}"
        
        record = PerformanceRecord(
            record_id=record_id,
            operation=operation,
            metric=PerformanceMetric.EXECUTION_TIME,
            value=execution_time,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.performance_records.append(record)
        
        # 检查阈值
        self._check_threshold(record)
        
        return record
    
    def measure_operation(self, operation: str, func: Callable, *args, **kwargs) -> Any:
        """
        测量操作性能
        
        Args:
            operation: 操作名称
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self.record_operation(operation, execution_time, {
                'args': str(args)[:100],  # 限制长度
                'kwargs': str(kwargs)[:100]
            })
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.record_operation(operation, execution_time, {
                'error': str(e),
                'status': 'failed'
            })
            raise
    
    def set_threshold(self, operation: str, metric: PerformanceMetric,
                     threshold: float, alert_on_exceed: bool = True) -> PerformanceThreshold:
        """
        设置性能阈值
        
        Args:
            operation: 操作名称
            metric: 性能指标
            threshold: 阈值
            alert_on_exceed: 超过阈值时是否告警
            
        Returns:
            性能阈值对象
        """
        threshold_key = f"{operation}:{metric.value}"
        
        perf_threshold = PerformanceThreshold(
            operation=operation,
            metric=metric,
            threshold=threshold,
            alert_on_exceed=alert_on_exceed
        )
        
        self.thresholds[threshold_key] = perf_threshold
        return perf_threshold
    
    def _check_threshold(self, record: PerformanceRecord):
        """检查阈值"""
        threshold_key = f"{record.operation}:{record.metric.value}"
        
        if threshold_key in self.thresholds:
            threshold = self.thresholds[threshold_key]
            
            if record.value > threshold.threshold and threshold.alert_on_exceed:
                logger.warning(
                    f"性能告警: {record.operation} 的 {record.metric.value} "
                    f"({record.value:.2f}) 超过阈值 ({threshold.threshold:.2f})"
                )
    
    def get_performance_stats(self, operation: Optional[str] = None,
                            metric: Optional[PerformanceMetric] = None) -> Dict[str, Any]:
        """
        获取性能统计
        
        Args:
            operation: 操作名称（可选）
            metric: 性能指标（可选）
            
        Returns:
            性能统计
        """
        records = self.performance_records
        
        if operation:
            records = [r for r in records if r.operation == operation]
        
        if metric:
            records = [r for r in records if r.metric == metric]
        
        if not records:
            return {
                'total_records': 0,
                'operation': operation,
                'metric': metric.value if metric else None
            }
        
        values = [r.value for r in records]
        
        return {
            'total_records': len(records),
            'operation': operation,
            'metric': metric.value if metric else None,
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values),
            'total_value': sum(values)
        }
    
    def get_operation_ranking(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取操作排名（按平均执行时间）
        
        Args:
            limit: 返回数量限制
            
        Returns:
            操作排名列表
        """
        operation_stats = {}
        
        for record in self.performance_records:
            if record.operation not in operation_stats:
                operation_stats[record.operation] = {
                    'count': 0,
                    'total_time': 0.0
                }
            
            operation_stats[record.operation]['count'] += 1
            operation_stats[record.operation]['total_time'] += record.value
        
        # 计算平均值并排序
        ranking = []
        for operation, stats in operation_stats.items():
            avg_time = stats['total_time'] / stats['count']
            ranking.append({
                'operation': operation,
                'avg_time': avg_time,
                'total_time': stats['total_time'],
                'count': stats['count']
            })
        
        ranking.sort(key=lambda x: x['avg_time'], reverse=True)
        return ranking[:limit]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Returns:
            性能摘要
        """
        total_records = len(self.performance_records)
        
        if total_records == 0:
            return {
                'total_records': 0,
                'total_operations': 0,
                'total_thresholds': len(self.thresholds)
            }
        
        unique_operations = len(set(r.operation for r in self.performance_records))
        total_execution_time = sum(r.value for r in self.performance_records)
        
        return {
            'total_records': total_records,
            'total_operations': unique_operations,
            'total_execution_time': total_execution_time,
            'avg_execution_time': total_execution_time / total_records,
            'total_thresholds': len(self.thresholds),
            'top_operations': self.get_operation_ranking(5)
        }


def main():
    """主函数 - 示例用法"""
    perf = DataPerformance()
    
    # 设置阈值
    perf.set_threshold('data_load', PerformanceMetric.EXECUTION_TIME, 1.0)
    
    # 测量操作
    def sample_operation():
        time.sleep(0.1)
        return "done"
    
    result = perf.measure_operation('data_load', sample_operation)
    print(f"操作结果: {result}")
    
    # 获取统计
    stats = perf.get_performance_stats('data_load')
    print(f"性能统计: {stats}")


if __name__ == '__main__':
    main()
