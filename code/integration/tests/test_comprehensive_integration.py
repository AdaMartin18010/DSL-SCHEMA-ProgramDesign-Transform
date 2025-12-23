"""
综合整合系统测试

测试综合整合框架、行业适配器、AI驱动转换等功能
"""

import unittest
from typing import Dict, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from integration import (
    ComprehensiveIntegrationFramework,
    AnalysisDimension,
    IntegrationLevel,
    IndustryAdapterFramework,
    IndustryType,
    SchemaFormat,
    AIDrivenTransformation,
    AIModel,
    PromptStrategy,
    ComprehensiveAnalyzer
)


class TestComprehensiveIntegrationFramework(unittest.TestCase):
    """综合整合框架测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.framework = ComprehensiveIntegrationFramework()
        self.source_schema = {
            "openapi": "3.1.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        self.target_schema = {
            "asyncapi": "3.0.0",
            "info": {"title": "Test Events", "version": "1.0.0"},
            "channels": {
                "test.events": {
                    "subscribe": {
                        "message": {"payload": {}}
                    }
                }
            }
        }
    
    def test_integrate_analysis(self):
        """测试综合整合分析"""
        result = self.framework.integrate_analysis(
            self.source_schema,
            self.target_schema,
            dimensions=[AnalysisDimension.INFORMATION_THEORY],
            integration_level=IntegrationLevel.BASIC
        )
        
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.integration_id)
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 1.0)
        self.assertIsInstance(result.recommendations, list)
    
    def test_create_knowledge_matrix(self):
        """测试创建知识矩阵"""
        matrix = self.framework.create_knowledge_matrix(
            matrix_id="test_matrix",
            dimensions=["dim1", "dim2"],
            values={
                ("value1", "value2"): {"score": 0.9}
            }
        )
        
        self.assertIsNotNone(matrix)
        self.assertEqual(matrix.matrix_id, "test_matrix")
        self.assertEqual(len(matrix.dimensions), 2)
    
    def test_query_knowledge_matrix(self):
        """测试查询知识矩阵"""
        matrix = self.framework.create_knowledge_matrix(
            matrix_id="test_matrix",
            dimensions=["dim1", "dim2"],
            values={
                ("value1", "value2"): {"score": 0.9},
                ("value1", "value3"): {"score": 0.8}
            }
        )
        
        results = self.framework.query_knowledge_matrix(
            "test_matrix",
            {"dim1": "value1"}
        )
        
        self.assertGreaterEqual(len(results), 0)
    
    def test_get_integration_statistics(self):
        """测试获取整合统计"""
        # 先执行一些整合
        self.framework.integrate_analysis(
            self.source_schema, self.target_schema
        )
        
        stats = self.framework.get_integration_statistics()
        
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats["total_integrations"], 0)


class TestIndustryAdapterFramework(unittest.TestCase):
    """行业适配器框架测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.framework = IndustryAdapterFramework()
    
    def test_register_adapter(self):
        """测试注册适配器"""
        def to_universal(schema): return {}
        def from_universal(schema): return {}
        def validate(schema): return True
        
        adapter = self.framework.register_adapter(
            IndustryType.FINANCE,
            SchemaFormat.SWIFT,
            SchemaFormat.OPENAPI,
            to_universal,
            from_universal,
            validate
        )
        
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.industry_type, IndustryType.FINANCE)
        self.assertEqual(adapter.source_format, SchemaFormat.SWIFT)
    
    def test_add_conversion_rule(self):
        """测试添加转换规则"""
        rule = self.framework.add_conversion_rule(
            "测试规则",
            "type_mapping",
            {"type": "string"},
            {"type": "text"},
            priority=1
        )
        
        self.assertIsNotNone(rule)
        self.assertEqual(rule.rule_name, "测试规则")
        self.assertEqual(rule.rule_type, "type_mapping")
    
    def test_get_adapter_list(self):
        """测试获取适配器列表"""
        # 先注册一个适配器
        def to_universal(schema): return {}
        def from_universal(schema): return {}
        def validate(schema): return True
        
        self.framework.register_adapter(
            IndustryType.FINANCE,
            SchemaFormat.SWIFT,
            SchemaFormat.OPENAPI,
            to_universal,
            from_universal,
            validate
        )
        
        adapters = self.framework.get_adapter_list()
        self.assertGreaterEqual(len(adapters), 1)


class TestAIDrivenTransformation(unittest.TestCase):
    """AI驱动转换测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.ai_system = AIDrivenTransformation()
    
    def test_create_prompt_template(self):
        """测试创建提示模板"""
        template = self.ai_system.create_prompt_template(
            "测试模板",
            "openapi",
            "asyncapi",
            "转换模板",
            PromptStrategy.FEW_SHOT
        )
        
        self.assertIsNotNone(template)
        self.assertEqual(template.template_name, "测试模板")
        self.assertEqual(template.source_format, "openapi")
    
    def test_get_transformation_statistics(self):
        """测试获取转换统计"""
        stats = self.ai_system.get_transformation_statistics()
        
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats["total_transformations"], 0)
        self.assertGreaterEqual(stats["success_rate"], 0.0)
        self.assertLessEqual(stats["success_rate"], 1.0)


class TestComprehensiveAnalyzer(unittest.TestCase):
    """综合分析器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.analyzer = ComprehensiveAnalyzer()
        self.source_schema = {
            "openapi": "3.1.0",
            "info": {"title": "Source", "version": "1.0.0"}
        }
        self.target_schema = {
            "asyncapi": "3.0.0",
            "info": {"title": "Target", "version": "1.0.0"}
        }
    
    def test_comprehensive_analysis(self):
        """测试综合分析"""
        report = self.analyzer.comprehensive_analysis(
            self.source_schema,
            self.target_schema,
            "Source Schema",
            "Target Schema"
        )
        
        self.assertIsNotNone(report)
        self.assertIsNotNone(report.report_id)
        self.assertIsNotNone(report.integration_result)
        self.assertIsInstance(report.recommendations, list)
    
    def test_generate_report(self):
        """测试生成报告"""
        report = self.analyzer.comprehensive_analysis(
            self.source_schema,
            self.target_schema
        )
        
        json_report = self.analyzer.generate_report(report, format="json")
        self.assertIsInstance(json_report, str)
        self.assertGreater(len(json_report), 0)
        
        text_report = self.analyzer.generate_report(report, format="text")
        self.assertIsInstance(text_report, str)
        self.assertGreater(len(text_report), 0)
    
    def test_get_analysis_statistics(self):
        """测试获取分析统计"""
        # 先执行一些分析
        self.analyzer.comprehensive_analysis(
            self.source_schema, self.target_schema
        )
        
        stats = self.analyzer.get_analysis_statistics()
        
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats["total_reports"], 0)


if __name__ == "__main__":
    unittest.main()
