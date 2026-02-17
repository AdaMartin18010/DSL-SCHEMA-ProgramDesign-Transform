#!/usr/bin/env python3
"""
Schema工具性能测试套件
"""

import time
import json
import random
import string
import sys
sys.path.insert(0, '../Tools')

from schema_validator import SchemaValidator
from matrix_generator import MatrixGenerator


class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_schema_validation(self, sizes=[10, 100, 1000]):
        """测试不同规模Schema的验证性能"""
        print("=== Schema Validation Performance ===")
        
        for size in sizes:
            # 创建测试Schema
            schema = {
                "type": "object",
                "properties": {}
            }
            
            for i in range(size):
                schema["properties"][f"field_{i}"] = {"type": "string"}
            
            data = {f"field_{i}": f"value_{i}" for i in range(size)}
            
            validator = SchemaValidator()
            
            # 预热
            validator.validate_json_schema(data, schema)
            
            # 正式测试
            start = time.time()
            iterations = 100
            for _ in range(iterations):
                validator.validate_json_schema(data, schema)
            elapsed = time.time() - start
            
            avg_time = (elapsed / iterations) * 1000  # ms
            throughput = iterations / elapsed
            
            self.results[f"validation_{size}"] = {
                "avg_time_ms": avg_time,
                "throughput_ops": throughput
            }
            
            print(f"Size {size}: {avg_time:.2f}ms/op, {throughput:.0f} ops/sec")
    
    def benchmark_matrix_generation(self, theme_counts=[10, 50, 100]):
        """测试矩阵生成性能"""
        print("\n=== Matrix Generation Performance ===")
        
        for count in theme_counts:
            generator = MatrixGenerator()
            
            # 添加测试数据
            for i in range(count):
                generator.add_theme(f"T{i:03d}", f"Theme {i}", {
                    "theory": random.choice(["Info", "Formal", "Graph"]),
                    "application": random.choice(["Data", "API", "Config"]),
                    "standard": random.choice(["W3C", "ISO", "IEC"]),
                    "tool": random.choice(["Python", "Java", "JS"]),
                    "industry": random.choice(["Fin", "Health", "Ind"])
                })
            
            # 测试
            start = time.time()
            matrix = generator.generate_matrix()
            elapsed = time.time() - start
            
            self.results[f"matrix_{count}"] = {
                "time_ms": elapsed * 1000,
                "themes": count
            }
            
            print(f"Themes {count}: {elapsed*1000:.2f}ms")
    
    def generate_report(self):
        """生成性能报告"""
        print("\n=== Performance Report ===")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": sys.version,
            "results": self.results
        }
        
        # 保存报告
        with open('performance_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("Report saved to performance_report.json")
        
        # 生成建议
        print("\n=== Optimization Suggestions ===")
        
        for key, result in self.results.items():
            if "validation" in key:
                avg_time = result["avg_time_ms"]
                if avg_time > 10:
                    print(f"⚠️  {key}: Consider caching for {avg_time:.1f}ms operations")
                else:
                    print(f"✅  {key}: Good performance at {avg_time:.1f}ms")


if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.benchmark_schema_validation()
    benchmark.benchmark_matrix_generation()
    benchmark.generate_report()
