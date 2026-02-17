#!/usr/bin/env python3
"""
Performance Profiler
====================

性能分析工具，提供：
- Schema验证性能测试
- 内存使用分析
- 响应时间监控
- 瓶颈识别
- 优化建议

Version: 2.3.0
"""

import json
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from statistics import mean, median, stdev
from collections import defaultdict
import sys


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    median_time_ms: float
    std_dev_ms: float
    memory_peak_mb: float
    throughput_ops_per_sec: float


@dataclass
class Bottleneck:
    """性能瓶颈"""
    location: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    impact: str
    suggestion: str


@dataclass
class PerformanceReport:
    """性能报告"""
    schema_name: str
    metrics: Dict[str, PerformanceMetrics]
    bottlenecks: List[Bottleneck]
    recommendations: List[str]
    overall_rating: str  # 'excellent', 'good', 'fair', 'poor'


class PerformanceProfiler:
    """Schema性能分析器"""
    
    def __init__(self):
        self.results: Dict[str, PerformanceMetrics] = {}
        self.thresholds = {
            "validation_time_ms": 10,  # 10ms以下优秀
            "memory_mb": 50,  # 50MB以下优秀
            "throughput": 1000  # 1000 ops/s以上优秀
        }
    
    def profile_validation(self, schema: Dict, samples: List[Dict], 
                          iterations: int = 1000) -> PerformanceMetrics:
        """
        分析验证性能
        
        Args:
            schema: 待测试的Schema
            samples: 测试样本数据
            iterations: 迭代次数
        
        Returns:
            PerformanceMetrics: 性能指标
        """
        times = []
        
        # 预热
        for _ in range(min(10, iterations // 10)):
            self._validate_sample(schema, samples[0])
        
        # 开始内存追踪
        tracemalloc.start()
        
        # 性能测试
        for i in range(iterations):
            sample = samples[i % len(samples)]
            
            start = time.perf_counter()
            self._validate_sample(schema, sample)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            
            times.append(elapsed)
        
        # 获取内存峰值
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_peak_mb = peak / (1024 * 1024)
        
        total_time = sum(times)
        avg_time = mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = median(times)
        std_dev = stdev(times) if len(times) > 1 else 0
        throughput = iterations / (total_time / 1000) if total_time > 0 else 0
        
        return PerformanceMetrics(
            operation="validation",
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            median_time_ms=median_time,
            std_dev_ms=std_dev,
            memory_peak_mb=memory_peak_mb,
            throughput_ops_per_sec=throughput
        )
    
    def _validate_sample(self, schema: Dict, sample: Dict) -> bool:
        """验证样本 (简化实现)"""
        # 这里应该调用实际的验证器
        # 简化: 只检查类型
        schema_type = schema.get("type")
        if schema_type == "object":
            return isinstance(sample, dict)
        elif schema_type == "array":
            return isinstance(sample, list)
        return True
    
    def profile_schema_loading(self, schema: Dict, 
                               iterations: int = 1000) -> PerformanceMetrics:
        """分析Schema加载性能"""
        schema_json = json.dumps(schema)
        times = []
        
        tracemalloc.start()
        
        for _ in range(iterations):
            start = time.perf_counter()
            json.loads(schema_json)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        total_time = sum(times)
        
        return PerformanceMetrics(
            operation="schema_loading",
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            median_time_ms=median(times),
            std_dev_ms=stdev(times) if len(times) > 1 else 0,
            memory_peak_mb=peak / (1024 * 1024),
            throughput_ops_per_sec=iterations / (total_time / 1000) if total_time > 0 else 0
        )
    
    def profile_compilation(self, schema: Dict, 
                           iterations: int = 100) -> PerformanceMetrics:
        """分析Schema编译性能"""
        times = []
        
        tracemalloc.start()
        
        for _ in range(iterations):
            start = time.perf_counter()
            # 模拟编译: 解析并建立索引
            self._compile_schema(schema)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        total_time = sum(times)
        
        return PerformanceMetrics(
            operation="compilation",
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            median_time_ms=median(times),
            std_dev_ms=stdev(times) if len(times) > 1 else 0,
            memory_peak_mb=peak / (1024 * 1024),
            throughput_ops_per_sec=iterations / (total_time / 1000) if total_time > 0 else 0
        )
    
    def _compile_schema(self, schema: Dict) -> Dict:
        """模拟Schema编译"""
        compiled = {
            "ref_map": {},
            "property_index": set(),
            "type_checks": {}
        }
        
        def traverse(node, path=""):
            if not isinstance(node, dict):
                return
            
            if "$ref" in node:
                compiled["ref_map"][path] = node["$ref"]
            
            if "type" in node:
                compiled["type_checks"][path] = node["type"]
            
            if "properties" in node:
                for prop in node["properties"]:
                    compiled["property_index"].add(f"{path}.{prop}")
        
        traverse(schema)
        return compiled
    
    def identify_bottlenecks(self, schema: Dict, 
                            metrics: Dict[str, PerformanceMetrics]) -> List[Bottleneck]:
        """
        识别性能瓶颈
        
        Args:
            schema: 测试的Schema
            metrics: 性能指标
        
        Returns:
            List[Bottleneck]: 瓶颈列表
        """
        bottlenecks = []
        
        # 检查验证时间
        if "validation" in metrics:
            vm = metrics["validation"]
            if vm.avg_time_ms > 100:
                bottlenecks.append(Bottleneck(
                    location="validation",
                    severity="critical",
                    description=f"验证时间过长: {vm.avg_time_ms:.2f}ms",
                    impact="每个请求都会受到影响，可能导致超时",
                    suggestion="简化Schema结构，减少嵌套层级，使用更高效的验证器"
                ))
            elif vm.avg_time_ms > 10:
                bottlenecks.append(Bottleneck(
                    location="validation",
                    severity="medium",
                    description=f"验证时间较慢: {vm.avg_time_ms:.2f}ms",
                    impact="高并发时可能成为瓶颈",
                    suggestion="优化复杂验证规则，考虑缓存验证结果"
                ))
        
        # 检查内存使用
        for op, m in metrics.items():
            if m.memory_peak_mb > 500:
                bottlenecks.append(Bottleneck(
                    location=op,
                    severity="high",
                    description=f"内存使用过高: {m.memory_peak_mb:.2f}MB",
                    impact="可能导致内存不足错误",
                    suggestion="检查是否有内存泄漏，优化数据结构"
                ))
        
        # 检查Schema结构
        schema_size = len(json.dumps(schema))
        if schema_size > 100000:  # 100KB
            bottlenecks.append(Bottleneck(
                location="schema_structure",
                severity="medium",
                description=f"Schema过大: {schema_size / 1024:.1f}KB",
                impact="解析和传输开销增加",
                suggestion="拆分大型Schema，使用引用和模块化"
            ))
        
        # 检查嵌套深度
        depth = self._get_schema_depth(schema)
        if depth > 10:
            bottlenecks.append(Bottleneck(
                location="schema_structure",
                severity="medium",
                description=f"嵌套层级过深: {depth}层",
                impact="递归验证开销大",
                suggestion="扁平化数据结构"
            ))
        
        # 检查属性数量
        prop_count = self._count_properties(schema)
        if prop_count > 100:
            bottlenecks.append(Bottleneck(
                location="schema_structure",
                severity="low",
                description=f"属性数量过多: {prop_count}",
                impact="验证复杂度增加",
                suggestion="考虑分组合并相关属性"
            ))
        
        return bottlenecks
    
    def _get_schema_depth(self, schema: Dict, current_depth: int = 0) -> int:
        """获取Schema深度"""
        if not isinstance(schema, dict):
            return current_depth
        
        max_depth = current_depth
        
        for value in schema.values():
            if isinstance(value, dict):
                depth = self._get_schema_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        depth = self._get_schema_depth(item, current_depth + 1)
                        max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _count_properties(self, schema: Dict) -> int:
        """计算属性数量"""
        count = 0
        
        if isinstance(schema, dict):
            if "properties" in schema:
                count += len(schema["properties"])
                for prop in schema["properties"].values():
                    count += self._count_properties(prop)
            
            if "items" in schema and isinstance(schema["items"], dict):
                count += self._count_properties(schema["items"])
        
        return count
    
    def generate_recommendations(self, metrics: Dict[str, PerformanceMetrics],
                                 bottlenecks: List[Bottleneck]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于指标的建议
        if "validation" in metrics:
            vm = metrics["validation"]
            if vm.throughput_ops_per_sec < 100:
                recommendations.append(
                    "验证吞吐量低，考虑使用预编译Schema或缓存验证结果"
                )
            if vm.std_dev_ms / vm.avg_time_ms > 0.5:
                recommendations.append(
                    "验证时间波动大，检查是否有异常复杂的数据样本"
                )
        
        # 基于瓶颈的建议
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_bottlenecks = sorted(bottlenecks, 
                                    key=lambda b: severity_order.get(b.severity, 4))
        
        for bottleneck in sorted_bottlenecks[:5]:
            recommendations.append(f"[{bottleneck.severity.upper()}] {bottleneck.suggestion}")
        
        # 通用建议
        recommendations.extend([
            "使用JSON Schema Draft 2020-12或更高版本以获得更好的性能",
            "考虑使用二进制序列化格式（如MessagePack）提高传输效率",
            "在高并发场景下使用Schema实例池避免重复编译"
        ])
        
        return recommendations
    
    def run_full_profile(self, schema: Dict, samples: List[Dict],
                        schema_name: str = "Untitled") -> PerformanceReport:
        """
        运行完整性能分析
        
        Args:
            schema: 待分析的Schema
            samples: 测试样本
            schema_name: Schema名称
        
        Returns:
            PerformanceReport: 完整报告
        """
        print(f"Profiling schema: {schema_name}...")
        
        # 运行各项测试
        metrics = {}
        
        print("  - Testing validation performance...")
        metrics["validation"] = self.profile_validation(schema, samples)
        
        print("  - Testing schema loading...")
        metrics["schema_loading"] = self.profile_loading(schema)
        
        print("  - Testing compilation...")
        metrics["compilation"] = self.profile_compilation(schema)
        
        # 识别瓶颈
        print("  - Identifying bottlenecks...")
        bottlenecks = self.identify_bottlenecks(schema, metrics)
        
        # 生成建议
        recommendations = self.generate_recommendations(metrics, bottlenecks)
        
        # 计算总体评级
        overall_rating = self._calculate_rating(metrics, bottlenecks)
        
        return PerformanceReport(
            schema_name=schema_name,
            metrics=metrics,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            overall_rating=overall_rating
        )
    
    def _calculate_rating(self, metrics: Dict[str, PerformanceMetrics],
                         bottlenecks: List[Bottleneck]) -> str:
        """计算总体评级"""
        critical_count = sum(1 for b in bottlenecks if b.severity == "critical")
        high_count = sum(1 for b in bottlenecks if b.severity == "high")
        
        if critical_count > 0:
            return "poor"
        elif high_count > 1:
            return "fair"
        elif high_count == 1:
            return "good"
        else:
            return "excellent"


def main():
    """示例用法"""
    profiler = PerformanceProfiler()
    
    # 测试Schema
    schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string"}
                }
            }
        },
        "required": ["id", "name", "email"]
    }
    
    # 测试样本
    samples = [
        {
            "id": "user-001",
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001"
            }
        },
        {
            "id": "user-002",
            "name": "Bob",
            "email": "bob@example.com",
            "age": 25
        }
    ]
    
    print("=" * 60)
    print("Schema性能分析报告")
    print("=" * 60)
    
    report = profiler.run_full_profile(schema, samples, "UserProfile")
    
    print(f"\n总体评级: {report.overall_rating.upper()}")
    print(f"发现瓶颈: {len(report.bottlenecks)}")
    
    print("\n性能指标:")
    for operation, metrics in report.metrics.items():
        print(f"\n  {operation}:")
        print(f"    平均时间: {metrics.avg_time_ms:.4f} ms")
        print(f"    吞吐量: {metrics.throughput_ops_per_sec:,.0f} ops/sec")
        print(f"    内存峰值: {metrics.memory_peak_mb:.2f} MB")
    
    if report.bottlenecks:
        print("\n性能瓶颈:")
        for b in report.bottlenecks:
            print(f"  [{b.severity.upper()}] {b.location}")
            print(f"    {b.description}")
    
    print("\n优化建议:")
    for i, rec in enumerate(report.recommendations[:5], 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
