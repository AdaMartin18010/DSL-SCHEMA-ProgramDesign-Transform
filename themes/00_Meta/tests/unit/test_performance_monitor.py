"""
Tests for Performance Monitor
=============================

测试覆盖：
- 性能跟踪
- 报告生成
- 缓存分析
- 查询优化建议

Version: 2.1.0
"""

import pytest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from performance_monitor import (
    PerformanceMonitor, PerformanceMetrics, PerformanceReport,
    CacheAnalyzer, QueryOptimizer, track_performance, get_monitor
)


class TestPerformanceMonitor:
    """性能监控器测试"""
    
    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor(enable_tracing=False)
    
    def test_track_context_manager(self, monitor):
        """测试上下文管理器跟踪"""
        with monitor.track("test_operation"):
            time.sleep(0.01)
        
        assert len(monitor.metrics) == 1
        assert monitor.metrics[0].operation == "test_operation"
        assert monitor.metrics[0].duration_ms >= 10
    
    def test_track_with_custom_metrics(self, monitor):
        """测试带自定义指标的跟踪"""
        with monitor.track("test_op", custom_key="custom_value") as metrics:
            pass
        
        assert metrics.custom_metrics.get("custom_key") == "custom_value"
    
    def test_decorator(self, monitor):
        """测试装饰器"""
        
        @monitor.decorator("decorated_func")
        def test_func():
            time.sleep(0.01)
            return 42
        
        result = test_func()
        assert result == 42
        assert len(monitor.metrics) == 1
        assert monitor.metrics[0].operation == "decorated_func"
    
    def test_generate_report_empty(self, monitor):
        """测试空监控数据生成报告"""
        report = monitor.generate_report()
        
        assert report.total_operations == 0
        assert report.avg_duration_ms == 0
        assert len(report.recommendations) > 0
    
    def test_generate_report_with_data(self, monitor):
        """测试有数据时生成报告"""
        # 添加一些监控数据
        for i in range(5):
            with monitor.track(f"op_{i}"):
                time.sleep(0.01)
        
        report = monitor.generate_report()
        
        assert report.total_operations == 5
        assert report.avg_duration_ms > 0
        assert "op_0" in report.metrics_by_operation
        assert len(report.recommendations) >= 0
    
    def test_percentile_calculation(self, monitor):
        """测试百分位数计算"""
        # 添加不同耗时的操作
        for i in range(10):
            with monitor.track("test"):
                time.sleep(0.01 * (i + 1))
        
        report = monitor.generate_report()
        
        assert report.p50_duration_ms > 0
        assert report.p95_duration_ms >= report.p50_duration_ms
        assert report.p99_duration_ms >= report.p95_duration_ms
    
    def test_error_tracking(self, monitor):
        """测试错误跟踪"""
        try:
            with monitor.track("failing_op"):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        assert len(monitor.metrics) == 1
        assert monitor.metrics[0].error_count == 1
    
    def test_reset(self, monitor):
        """测试重置功能"""
        with monitor.track("test"):
            pass
        
        assert len(monitor.metrics) == 1
        
        monitor.reset()
        
        assert len(monitor.metrics) == 0
        assert len(monitor._operation_times) == 0
    
    def test_export_report(self, monitor, tmp_path):
        """测试导出报告"""
        with monitor.track("test"):
            pass
        
        output_file = tmp_path / "report.json"
        json_output = monitor.export_report(str(output_file))
        
        assert output_file.exists()
        assert "total_operations" in json_output
        assert "test" in json_output


class TestCacheAnalyzer:
    """缓存分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        return CacheAnalyzer()
    
    def test_hit_rate_calculation(self, analyzer):
        """测试命中率计算"""
        # 记录命中
        for _ in range(8):
            analyzer.record_hit("key1")
        
        # 记录未命中
        for _ in range(2):
            analyzer.record_miss("key2")
        
        assert analyzer.hit_rate == 0.8
        assert analyzer.hits == 8
        assert analyzer.misses == 2
    
    def test_hot_keys(self, analyzer):
        """测试热点key识别"""
        analyzer.record_hit("hot_key")
        analyzer.record_hit("hot_key")
        analyzer.record_hit("hot_key")
        analyzer.record_hit("warm_key")
        analyzer.record_hit("warm_key")
        analyzer.record_hit("cold_key")
        
        hot_keys = analyzer.get_hot_keys(top_n=2)
        
        assert len(hot_keys) == 2
        assert hot_keys[0][0] == "hot_key"
        assert hot_keys[0][1] == 3
    
    def test_generate_report(self, analyzer):
        """测试生成报告"""
        analyzer.record_hit("key1")
        analyzer.record_hit("key1")
        analyzer.record_miss("key2")
        
        report = analyzer.generate_report()
        
        assert report["hit_rate"] == 2/3
        assert report["total_hits"] == 2
        assert report["total_misses"] == 1
        assert report["unique_keys"] == 2
        assert len(report["hot_keys"]) == 2


class TestQueryOptimizer:
    """查询优化器测试"""
    
    @pytest.fixture
    def optimizer(self):
        return QueryOptimizer()
    
    def test_select_star_warning(self, optimizer):
        """测试SELECT *警告"""
        query = "SELECT * FROM users"
        suggestions = optimizer.analyze_query(query, 10)
        
        assert any("SELECT *" in s for s in suggestions)
    
    def test_delete_without_where(self, optimizer):
        """测试DELETE缺少WHERE警告"""
        query = "DELETE FROM users"
        suggestions = optimizer.analyze_query(query, 10)
        
        assert any("WHERE" in s for s in suggestions)
    
    def test_like_prefix_wildcard(self, optimizer):
        """测试LIKE前缀通配符警告"""
        query = "SELECT * FROM users WHERE name LIKE '%john'"
        suggestions = optimizer.analyze_query(query, 10)
        
        assert any("LIKE" in s or "%" in s for s in suggestions)
    
    def test_slow_query_without_join(self, optimizer):
        """测试慢查询无JOIN警告"""
        query = "SELECT * FROM large_table WHERE id > 100"
        suggestions = optimizer.analyze_query(query, 2000)
        
        # 耗时>100ms且没有JOIN
        assert any("JOIN" in s or "index" in s.lower() for s in suggestions)
    
    def test_good_query_no_suggestions(self, optimizer):
        """测试良好查询无建议"""
        query = "SELECT id, name FROM users WHERE id = 1"
        suggestions = optimizer.analyze_query(query, 5)
        
        assert len(suggestions) == 1
        assert "正常" in suggestions[0] or "normal" in suggestions[0].lower()


class TestGlobalMonitor:
    """全局监控器测试"""
    
    def test_get_monitor_singleton(self):
        """测试全局监控器单例"""
        monitor1 = get_monitor()
        monitor2 = get_monitor()
        
        assert monitor1 is monitor2
    
    def test_track_performance_decorator(self):
        """测试全局track_performance装饰器"""
        
        @track_performance("global_test")
        def test_func():
            time.sleep(0.01)
            return "done"
        
        result = test_func()
        monitor = get_monitor()
        
        assert result == "done"
        assert any(m.operation == "global_test" for m in monitor.metrics)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
