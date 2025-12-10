"""
数据转换优化器模块

专注于数据转换优化、性能优化、资源优化
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """优化类型"""
    PERFORMANCE = "performance"  # 性能优化
    MEMORY = "memory"  # 内存优化
    PARALLEL = "parallel"  # 并行优化
    CACHE = "cache"  # 缓存优化
    BATCH = "batch"  # 批处理优化


@dataclass
class OptimizationConfig:
    """优化配置"""
    optimization_type: OptimizationType
    config: Dict[str, Any]


@dataclass
class OptimizationResult:
    """优化结果"""
    optimization_id: str
    optimization_type: OptimizationType
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    improvement: Dict[str, Any]
    optimization_time: float


class DataTransformationOptimizer:
    """
    数据转换优化器
    
    专注于数据转换优化、性能优化、资源优化
    """
    
    def __init__(self):
        self.optimization_history: List[OptimizationResult] = []
    
    def optimize(self, transformation_func: Callable, data: List[Dict[str, Any]],
                config: OptimizationConfig) -> OptimizationResult:
        """
        优化转换
        
        Args:
            transformation_func: 转换函数
            data: 数据列表
            config: 优化配置
            
        Returns:
            优化结果
        """
        optimization_id = f"opt_{datetime.utcnow().timestamp()}"
        
        # 测量优化前的性能
        before_start = time.time()
        before_result = transformation_func(data)
        before_time = time.time() - before_start
        
        before_metrics = {
            'execution_time': before_time,
            'data_size': len(data),
            'result_size': len(before_result) if isinstance(before_result, list) else 1
        }
        
        # 应用优化
        optimized_func = self._apply_optimization(transformation_func, config)
        
        # 测量优化后的性能
        after_start = time.time()
        after_result = optimized_func(data)
        after_time = time.time() - after_start
        
        after_metrics = {
            'execution_time': after_time,
            'data_size': len(data),
            'result_size': len(after_result) if isinstance(after_result, list) else 1
        }
        
        # 计算改进
        time_improvement = ((before_time - after_time) / before_time * 100) if before_time > 0 else 0.0
        
        improvement = {
            'time_improvement': time_improvement,
            'speedup': before_time / after_time if after_time > 0 else 1.0
        }
        
        optimization_time = time.time() - before_start
        
        result = OptimizationResult(
            optimization_id=optimization_id,
            optimization_type=config.optimization_type,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement=improvement,
            optimization_time=optimization_time
        )
        
        self.optimization_history.append(result)
        return result
    
    def _apply_optimization(self, func: Callable, config: OptimizationConfig) -> Callable:
        """应用优化"""
        opt_type = config.optimization_type
        opt_config = config.config
        
        if opt_type == OptimizationType.BATCH:
            # 批处理优化
            batch_size = opt_config.get('batch_size', 1000)
            
            def optimized_func(data):
                results = []
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    batch_result = func(batch)
                    if isinstance(batch_result, list):
                        results.extend(batch_result)
                    else:
                        results.append(batch_result)
                return results
            
            return optimized_func
        
        elif opt_type == OptimizationType.CACHE:
            # 缓存优化
            cache = {}
            
            def optimized_func(data):
                data_key = str(data)
                if data_key in cache:
                    return cache[data_key]
                result = func(data)
                cache[data_key] = result
                return result
            
            return optimized_func
        
        else:
            # 默认：直接返回原函数
            return func
    
    def suggest_optimizations(self, transformation_func: Callable,
                            data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        建议优化
        
        Args:
            transformation_func: 转换函数
            data: 数据列表
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        # 测量性能
        start_time = time.time()
        result = transformation_func(data)
        execution_time = time.time() - start_time
        
        data_size = len(data)
        
        # 根据性能特征提供建议
        if execution_time > 1.0 and data_size > 1000:
            suggestions.append({
                'type': 'batch_processing',
                'reason': f'数据量大({data_size})且执行时间长({execution_time:.2f}s)，建议使用批处理',
                'config': {'batch_size': 1000}
            })
        
        if execution_time > 0.5:
            suggestions.append({
                'type': 'caching',
                'reason': f'执行时间较长({execution_time:.2f}s)，建议使用缓存',
                'config': {}
            })
        
        return suggestions
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        获取优化统计
        
        Returns:
            优化统计
        """
        total_optimizations = len(self.optimization_history)
        
        if total_optimizations == 0:
            return {'total_optimizations': 0}
        
        avg_time_improvement = sum(
            r.improvement.get('time_improvement', 0) for r in self.optimization_history
        ) / total_optimizations
        
        avg_speedup = sum(
            r.improvement.get('speedup', 1.0) for r in self.optimization_history
        ) / total_optimizations
        
        return {
            'total_optimizations': total_optimizations,
            'average_time_improvement': avg_time_improvement,
            'average_speedup': avg_speedup
        }


def main():
    """主函数 - 示例用法"""
    optimizer = DataTransformationOptimizer()
    
    # 定义转换函数
    def transform_func(data):
        return [{'id': r.get('id'), 'name': r.get('name', '').upper()} for r in data]
    
    # 优化转换
    data = [{'id': i, 'name': f'user_{i}'} for i in range(100)]
    
    config = OptimizationConfig(
        optimization_type=OptimizationType.BATCH,
        config={'batch_size': 50}
    )
    
    result = optimizer.optimize(transform_func, data, config)
    print(f"优化结果: 时间改进={result.improvement['time_improvement']:.2f}%")


if __name__ == '__main__':
    main()
