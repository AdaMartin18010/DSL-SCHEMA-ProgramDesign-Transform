#!/usr/bin/env python3
"""
Tests for Performance Profiler
==============================

Test coverage for schema performance analysis functionality.

Version: 2.3.0
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools"))

from performance_profiler import (
    PerformanceProfiler, PerformanceMetrics, Bottleneck, PerformanceReport
)


class TestPerformanceProfiler(unittest.TestCase):
    """Test Performance Profiler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.profiler = PerformanceProfiler()
        
        self.test_schema = {
            "$schema": "https://json-schema.org/draft/2025-01/schema",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["id", "name"]
        }
        
        self.test_samples = [
            {"id": "user-1", "name": "Alice", "age": 30},
            {"id": "user-2", "name": "Bob", "age": 25}
        ]
    
    def test_initialization(self):
        """Test profiler initialization"""
        self.assertIsNotNone(self.profiler.thresholds)
        self.assertIn("validation_time_ms", self.profiler.thresholds)
    
    def test_profile_validation(self):
        """Test validation profiling"""
        metrics = self.profiler.profile_validation(
            self.test_schema, 
            self.test_samples, 
            iterations=100
        )
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertEqual(metrics.operation, "validation")
        self.assertEqual(metrics.iterations, 100)
        self.assertGreater(metrics.avg_time_ms, 0)
        self.assertGreater(metrics.throughput_ops_per_sec, 0)
    
    def test_profile_schema_loading(self):
        """Test schema loading profiling"""
        metrics = self.profiler.profile_schema_loading(
            self.test_schema,
            iterations=100
        )
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertEqual(metrics.operation, "schema_loading")
    
    def test_profile_compilation(self):
        """Test schema compilation profiling"""
        metrics = self.profiler.profile_compilation(
            self.test_schema,
            iterations=50
        )
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertEqual(metrics.operation, "compilation")
    
    def test_compile_schema(self):
        """Test schema compilation"""
        compiled = self.profiler._compile_schema(self.test_schema)
        
        self.assertIn("ref_map", compiled)
        self.assertIn("property_index", compiled)
        self.assertIn("type_checks", compiled)
    
    def test_get_schema_depth(self):
        """Test schema depth calculation"""
        nested_schema = {
            "type": "object",
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
        
        depth = self.profiler._get_schema_depth(nested_schema)
        self.assertGreaterEqual(depth, 3)
    
    def test_count_properties(self):
        """Test property counting"""
        count = self.profiler._count_properties(self.test_schema)
        self.assertEqual(count, 3)
    
    def test_identify_bottlenecks(self):
        """Test bottleneck identification"""
        metrics = {
            "validation": PerformanceMetrics(
                operation="validation",
                iterations=100,
                total_time_ms=5000,  # Slow
                avg_time_ms=50,
                min_time_ms=40,
                max_time_ms=100,
                median_time_ms=48,
                std_dev_ms=10,
                memory_peak_mb=10,
                throughput_ops_per_sec=20
            )
        }
        
        bottlenecks = self.profiler.identify_bottlenecks(self.test_schema, metrics)
        self.assertIsInstance(bottlenecks, list)
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        metrics = {
            "validation": PerformanceMetrics(
                operation="validation",
                iterations=100,
                total_time_ms=1000,
                avg_time_ms=10,
                min_time_ms=5,
                max_time_ms=20,
                median_time_ms=9,
                std_dev_ms=3,
                memory_peak_mb=10,
                throughput_ops_per_sec=100
            )
        }
        
        bottlenecks = []
        recommendations = self.profiler.generate_recommendations(metrics, bottlenecks)
        
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)
    
    def test_calculate_rating_excellent(self):
        """Test rating calculation for excellent"""
        metrics = {}
        bottlenecks = []
        
        rating = self.profiler._calculate_rating(metrics, bottlenecks)
        self.assertEqual(rating, "excellent")
    
    def test_calculate_rating_poor(self):
        """Test rating calculation for poor"""
        metrics = {}
        bottlenecks = [
            Bottleneck(
                location="validation",
                severity="critical",
                description="Too slow",
                impact="High",
                suggestion="Optimize"
            )
        ]
        
        rating = self.profiler._calculate_rating(metrics, bottlenecks)
        self.assertEqual(rating, "poor")


class TestPerformanceMetrics(unittest.TestCase):
    """Test PerformanceMetrics dataclass"""
    
    def test_metrics_creation(self):
        """Test creating performance metrics"""
        metrics = PerformanceMetrics(
            operation="validation",
            iterations=1000,
            total_time_ms=100.0,
            avg_time_ms=0.1,
            min_time_ms=0.05,
            max_time_ms=0.5,
            median_time_ms=0.09,
            std_dev_ms=0.02,
            memory_peak_mb=10.5,
            throughput_ops_per_sec=10000.0
        )
        
        self.assertEqual(metrics.operation, "validation")
        self.assertEqual(metrics.iterations, 1000)
        self.assertEqual(metrics.avg_time_ms, 0.1)


class TestBottleneck(unittest.TestCase):
    """Test Bottleneck dataclass"""
    
    def test_bottleneck_creation(self):
        """Test creating a bottleneck"""
        bottleneck = Bottleneck(
            location="validation",
            severity="high",
            description="Validation is slow",
            impact="Affects all requests",
            suggestion="Optimize regex patterns"
        )
        
        self.assertEqual(bottleneck.location, "validation")
        self.assertEqual(bottleneck.severity, "high")


if __name__ == "__main__":
    unittest.main()
