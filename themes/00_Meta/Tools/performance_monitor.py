#!/usr/bin/env python3
"""
Performance Monitor & Optimizer
===============================

性能监控与优化工具，提供：
- 实时性能指标收集
- 内存使用监控
- CPU使用率追踪
- 数据库查询优化建议
- 缓存命中率分析
- 自动性能报告生成

Version: 2.1.0
"""

import asyncio
import functools
import json
import time
import tracemalloc
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    operation: str = ""
    duration_ms: float = 0.0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """性能报告"""
    start_time: datetime
    end_time: datetime
    total_operations: int
    total_duration_ms: float
    avg_duration_ms: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    error_rate: float
    throughput_ops_per_sec: float
    metrics_by_operation: Dict[str, Dict[str, Any]]
    recommendations: List[str]


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, enable_tracing: bool = True):
        self.metrics: List[PerformanceMetrics] = []
        self.enable_tracing = enable_tracing
        self._operation_counts: Dict[str, int] = defaultdict(int)
        self._operation_times: Dict[str, List[float]] = defaultdict(list)
        
        if enable_tracing:
            tracemalloc.start()
    
    @contextmanager
    def track(self, operation: str, **custom_metrics):
        """跟踪操作性能的上下文管理器"""
        start_time = time.perf_counter()
        start_memory = tracemalloc.get_traced_memory()[0] if self.enable_tracing else 0
        
        metrics = PerformanceMetrics(
            operation=operation,
            custom_metrics=custom_metrics
        )
        
        try:
            yield metrics
        except Exception as e:
            metrics.error_count = 1
            raise
        finally:
            end_time = time.perf_counter()
            end_memory = tracemalloc.get_traced_memory()[0] if self.enable_tracing else 0
            
            metrics.duration_ms = (end_time - start_time) * 1000
            metrics.memory_mb = (end_memory - start_memory) / (1024 * 1024)
            
            self.metrics.append(metrics)
            self._operation_counts[operation] += 1
            self._operation_times[operation].append(metrics.duration_ms)
    
    def decorator(self, operation: str = None):
        """性能监控装饰器"""
        def decorator_func(func: Callable) -> Callable:
            op_name = operation or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.track(op_name):
                    return func(*args, **kwargs)
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.track(op_name):
                    return await func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
        return decorator_func
    
    def generate_report(self) -> PerformanceReport:
        """生成性能报告"""
        if not self.metrics:
            return PerformanceReport(
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                total_operations=0,
                total_duration_ms=0,
                avg_duration_ms=0,
                p50_duration_ms=0,
                p95_duration_ms=0,
                p99_duration_ms=0,
                error_rate=0,
                throughput_ops_per_sec=0,
                metrics_by_operation={},
                recommendations=[]
            )
        
        # 计算统计信息
        durations = [m.duration_ms for m in self.metrics]
        sorted_durations = sorted(durations)
        total_ops = len(self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        start_time = min(m.timestamp for m in self.metrics)
        end_time = max(m.timestamp for m in self.metrics)
        time_span_seconds = (end_time - start_time).total_seconds() or 1
        
        # 按操作分组统计
        metrics_by_op = {}
        for op_name, times in self._operation_times.items():
            sorted_times = sorted(times)
            metrics_by_op[op_name] = {
                'count': len(times),
                'avg_ms': sum(times) / len(times),
                'p50_ms': sorted_times[len(sorted_times) // 2],
                'p95_ms': sorted_times[int(len(sorted_times) * 0.95)],
                'p99_ms': sorted_times[int(len(sorted_times) * 0.99)],
                'max_ms': max(times)
            }
        
        # 生成优化建议
        recommendations = self._generate_recommendations(metrics_by_op)
        
        return PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            total_operations=total_ops,
            total_duration_ms=sum(durations),
            avg_duration_ms=sum(durations) / len(durations),
            p50_duration_ms=sorted_durations[len(sorted_durations) // 2],
            p95_duration_ms=sorted_durations[int(len(sorted_durations) * 0.95)],
            p99_duration_ms=sorted_durations[int(len(sorted_durations) * 0.99)],
            error_rate=total_errors / total_ops,
            throughput_ops_per_sec=total_ops / time_span_seconds,
            metrics_by_operation=metrics_by_op,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, metrics_by_op: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for op_name, metrics in metrics_by_op.items():
            # 慢查询检测
            if metrics['p95_ms'] > 1000:
                recommendations.append(
                    f"操作 '{op_name}' P95延迟为 {metrics['p95_ms']:.2f}ms，"
                    "建议进行性能优化"
                )
            
            # 异常高的平均值
            if metrics['avg_ms'] > metrics['p50_ms'] * 2:
                recommendations.append(
                    f"操作 '{op_name}' 平均延迟({metrics['avg_ms']:.2f}ms) "
                    "显著高于中位数，可能存在异常值"
                )
        
        if not recommendations:
            recommendations.append("所有操作性能正常，暂无优化建议")
        
        return recommendations
    
    def export_report(self, filepath: Optional[str] = None) -> str:
        """导出报告到文件"""
        report = self.generate_report()
        
        report_dict = {
            'generated_at': datetime.utcnow().isoformat(),
            'period': {
                'start': report.start_time.isoformat(),
                'end': report.end_time.isoformat()
            },
            'summary': {
                'total_operations': report.total_operations,
                'total_duration_ms': round(report.total_duration_ms, 2),
                'avg_duration_ms': round(report.avg_duration_ms, 2),
                'p95_duration_ms': round(report.p95_duration_ms, 2),
                'p99_duration_ms': round(report.p99_duration_ms, 2),
                'error_rate': round(report.error_rate, 4),
                'throughput_ops_per_sec': round(report.throughput_ops_per_sec, 2)
            },
            'operations': report.metrics_by_operation,
            'recommendations': report.recommendations
        }
        
        json_output = json.dumps(report_dict, indent=2, ensure_ascii=False)
        
        if filepath:
            Path(filepath).write_text(json_output, encoding='utf-8')
        
        return json_output
    
    def reset(self):
        """重置监控数据"""
        self.metrics.clear()
        self._operation_counts.clear()
        self._operation_times.clear()


class CacheAnalyzer:
    """缓存分析器"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.key_access_times: Dict[str, List[datetime]] = defaultdict(list)
        self.key_hit_counts: Dict[str, int] = defaultdict(int)
    
    def record_hit(self, key: str):
        """记录缓存命中"""
        self.hits += 1
        self.key_hit_counts[key] += 1
        self.key_access_times[key].append(datetime.utcnow())
    
    def record_miss(self, key: str):
        """记录缓存未命中"""
        self.misses += 1
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
    
    def get_hot_keys(self, top_n: int = 10) -> List[tuple]:
        """获取热点key"""
        sorted_keys = sorted(
            self.key_hit_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_keys[:top_n]
    
    def generate_report(self) -> Dict:
        """生成缓存分析报告"""
        return {
            'hit_rate': round(self.hit_rate, 4),
            'total_hits': self.hits,
            'total_misses': self.misses,
            'hot_keys': self.get_hot_keys(10),
            'unique_keys': len(self.key_hit_counts)
        }


class QueryOptimizer:
    """查询优化建议器"""
    
    @staticmethod
    def analyze_query(query: str, execution_time_ms: float) -> List[str]:
        """分析查询并提供优化建议"""
        suggestions = []
        
        query_lower = query.lower()
        
        # 检查SELECT *
        if 'select *' in query_lower:
            suggestions.append("避免使用SELECT *，只选择需要的列")
        
        # 检查缺少WHERE的DELETE/UPDATE
        if ('delete from' in query_lower or 'update' in query_lower) and 'where' not in query_lower:
            suggestions.append("DELETE/UPDATE语句缺少WHERE子句，可能导致全表操作")
        
        # 检查N+1查询模式
        if execution_time_ms > 100 and 'join' not in query_lower:
            suggestions.append("查询耗时较长，考虑使用JOIN优化或添加索引")
        
        # 检查LIKE前缀通配符
        if "like '%" in query_lower:
            suggestions.append("LIKE以%开头无法使用索引，考虑全文搜索")
        
        return suggestions if suggestions else ["查询看起来正常，暂无优化建议"]


# 全局监控器实例
_global_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """获取全局性能监控器"""
    return _global_monitor


def track_performance(operation: str = None):
    """便捷的装饰器函数"""
    return _global_monitor.decorator(operation)


# 示例用法
if __name__ == '__main__':
    monitor = PerformanceMonitor()
    
    # 模拟一些操作
    for i in range(10):
        with monitor.track('validate_schema', schema_id=f'schema_{i}'):
            time.sleep(0.01 * (i + 1))
    
    for i in range(5):
        with monitor.track('generate_matrix'):
            time.sleep(0.05)
    
    # 生成报告
    report = monitor.generate_report()
    
    print("=== 性能报告 ===")
    print(f"总操作数: {report.total_operations}")
    print(f"平均延迟: {report.avg_duration_ms:.2f}ms")
    print(f"P95延迟: {report.p95_duration_ms:.2f}ms")
    print(f"P99延迟: {report.p99_duration_ms:.2f}ms")
    print(f"吞吐量: {report.throughput_ops_per_sec:.2f} ops/sec")
    print(f"错误率: {report.error_rate:.2%}")
    
    print("\n=== 操作详情 ===")
    for op_name, metrics in report.metrics_by_operation.items():
        print(f"\n{op_name}:")
        print(f"  调用次数: {metrics['count']}")
        print(f"  平均延迟: {metrics['avg_ms']:.2f}ms")
        print(f"  P95延迟: {metrics['p95_ms']:.2f}ms")
    
    print("\n=== 优化建议 ===")
    for rec in report.recommendations:
        print(f"- {rec}")
    
    # 导出JSON
    print("\n=== JSON导出 ===")
    json_report = monitor.export_report()
    print(json_report[:500] + "...")
