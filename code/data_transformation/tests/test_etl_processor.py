"""
ETL处理器测试

测试ETL处理器的核心功能
"""

import unittest
from data_transformation.etl_processor import (
    ETLProcessor,
    ExtractType,
    TransformType,
    LoadType
)


class TestETLProcessor(unittest.TestCase):
    """ETL处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = ETLProcessor()
    
    def test_create_pipeline(self):
        """测试创建ETL管道"""
        pipeline_config = {
            'pipeline_id': 'test_pipeline',
            'name': '测试ETL管道',
            'extract': [{
                'rule_id': 'extract_1',
                'source_type': 'database',
                'source_config': {'table': 'source_table'},
                'extract_type': 'full',
                'batch_size': 1000
            }],
            'transform': [{
                'rule_id': 'transform_1',
                'transform_type': 'clean',
                'source_fields': ['field1'],
                'target_fields': ['field1']
            }],
            'load': [{
                'rule_id': 'load_1',
                'target_type': 'database',
                'target_config': {'table': 'target_table'},
                'load_type': 'append'
            }]
        }
        
        pipeline = self.processor.create_pipeline(pipeline_config)
        
        # 应该成功创建
        self.assertIsNotNone(pipeline)
        self.assertEqual(pipeline.pipeline_id, 'test_pipeline')
        self.assertEqual(len(pipeline.extract_rules), 1)
        self.assertEqual(len(pipeline.transform_rules), 1)
        self.assertEqual(len(pipeline.load_rules), 1)
        
        # 应该保存在pipelines中
        self.assertIn('test_pipeline', self.processor.pipelines)
    
    def test_execute_pipeline(self):
        """测试执行ETL管道"""
        # 先创建管道
        pipeline_config = {
            'pipeline_id': 'test_pipeline',
            'name': '测试ETL管道',
            'extract': [{
                'rule_id': 'extract_1',
                'source_type': 'database',
                'source_config': {'table': 'source_table'},
                'extract_type': 'full',
                'batch_size': 1000
            }],
            'transform': [{
                'rule_id': 'transform_1',
                'transform_type': 'clean',
                'source_fields': ['field1'],
                'target_fields': ['field1']
            }],
            'load': [{
                'rule_id': 'load_1',
                'target_type': 'database',
                'target_config': {'table': 'target_table'},
                'load_type': 'append'
            }]
        }
        
        pipeline = self.processor.create_pipeline(pipeline_config)
        
        # 执行管道
        result = self.processor.execute_pipeline('test_pipeline')
        
        # 应该成功执行
        self.assertTrue(result['success'])
        self.assertIn('execution_id', result)
        self.assertIn('extract', result)
        self.assertIn('transform', result)
        self.assertIn('load', result)
    
    def test_execute_pipeline_not_found(self):
        """测试执行不存在的管道"""
        result = self.processor.execute_pipeline('non_existent_pipeline')
        
        # 应该失败
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_execution_history(self):
        """测试获取执行历史"""
        # 创建并执行管道
        pipeline_config = {
            'pipeline_id': 'test_pipeline',
            'name': '测试ETL管道',
            'extract': [],
            'transform': [],
            'load': []
        }
        
        pipeline = self.processor.create_pipeline(pipeline_config)
        self.processor.execute_pipeline('test_pipeline')
        
        # 获取执行历史
        history = self.processor.get_execution_history('test_pipeline')
        
        # 应该包含执行记录
        self.assertGreater(len(history), 0)
        
        # 检查执行记录格式
        record = history[0]
        self.assertIn('execution_id', record)
        self.assertIn('pipeline_id', record)
        self.assertIn('success', record)


if __name__ == '__main__':
    unittest.main()
