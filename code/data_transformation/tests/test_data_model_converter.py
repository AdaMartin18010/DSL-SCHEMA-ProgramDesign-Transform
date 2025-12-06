"""
数据模型转换器测试

测试数据模型转换器的核心功能
"""

import unittest
from code.data_transformation.data_model_converter import (
    DataModelConverter,
    DataModelType,
    DataModelValidator
)


class TestDataModelConverter(unittest.TestCase):
    """数据模型转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = DataModelConverter()
        self.validator = DataModelValidator()
    
    def test_star_to_postgresql(self):
        """测试星型模式到PostgreSQL转换"""
        star_model = {
            'fact_tables': [{
                'name': 'sales_fact',
                'measures': [
                    {'name': 'amount', 'data_type': 'decimal'},
                    {'name': 'quantity', 'data_type': 'integer'}
                ],
                'dimension_keys': [
                    {'name': 'customer', 'dimension_table': 'customer_dim'},
                    {'name': 'product', 'dimension_table': 'product_dim'}
                ]
            }],
            'dimension_tables': [{
                'name': 'customer_dim',
                'attributes': [
                    {'name': 'customer_name', 'data_type': 'string'},
                    {'name': 'region', 'data_type': 'string'}
                ]
            }]
        }
        
        result = self.converter.convert(star_model, DataModelType.STAR, 'postgresql')
        
        # 应该生成表
        self.assertIn('tables', result)
        self.assertIn('sales_fact', result['tables'])
        self.assertIn('customer_dim', result['tables'])
        
        # 事实表应该包含度量和维度键
        fact_table = result['tables']['sales_fact']
        self.assertIn('amount', fact_table['fields'])
        self.assertIn('customer_id', fact_table['fields'])
        
        # 维度表应该包含属性
        dim_table = result['tables']['customer_dim']
        self.assertIn('customer_name', dim_table['fields'])
        self.assertIn('region', dim_table['fields'])
    
    def test_datavault_to_postgresql(self):
        """测试Data Vault到PostgreSQL转换"""
        datavault_model = {
            'hubs': [{
                'name': 'customer_hub',
                'business_key': 'customer_id',
                'load_timestamp': True
            }],
            'links': [{
                'name': 'order_link',
                'hub_references': ['customer_hub'],
                'load_timestamp': True
            }],
            'satellites': [{
                'name': 'customer_sat',
                'parent': 'customer_hub',
                'attributes': [
                    {'name': 'customer_name', 'data_type': 'string'},
                    {'name': 'region', 'data_type': 'string'}
                ],
                'load_timestamp': True,
                'load_end_timestamp': True
            }]
        }
        
        result = self.converter.convert(datavault_model, DataModelType.DATA_VAULT, 'postgresql')
        
        # 应该生成Hub、Link、Satellite表
        self.assertIn('tables', result)
        self.assertIn('customer_hub', result['tables'])
        self.assertIn('order_link', result['tables'])
        self.assertIn('customer_sat', result['tables'])
        
        # Hub应该包含业务键
        hub_table = result['tables']['customer_hub']
        self.assertIn('customer_id', hub_table['fields'])
        self.assertIn('hub_key', hub_table['fields'])
    
    def test_star_to_snowflake(self):
        """测试星型模式到雪花模式转换"""
        star_model = {
            'fact_tables': [{
                'name': 'sales_fact',
                'measures': [{'name': 'amount', 'data_type': 'decimal'}],
                'dimension_keys': [{'name': 'customer', 'dimension_table': 'customer_dim'}]
            }],
            'dimension_tables': [{
                'name': 'customer_dim',
                'attributes': [
                    {'name': 'customer_name', 'data_type': 'string'},
                    {'name': 'region', 'data_type': 'string'}
                ]
            }]
        }
        
        result = self.converter.convert(star_model, DataModelType.STAR, 'snowflake')
        
        # 应该包含层次结构
        dimension_tables = result.get('dimension_tables', [])
        self.assertGreater(len(dimension_tables), 0)
    
    def test_generate_sql_ddl(self):
        """测试SQL DDL生成"""
        converted_model = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'INTEGER', 'nullable': False},
                        'name': {'type': 'VARCHAR(255)', 'nullable': True}
                    },
                    'primary_key': 'id'
                }
            },
            'relationships': [],
            'indexes': []
        }
        
        ddl = self.converter.generate_sql_ddl(converted_model)
        
        # 应该包含CREATE TABLE语句
        self.assertIn('CREATE TABLE', ddl)
        self.assertIn('users', ddl)
        self.assertIn('PRIMARY KEY', ddl)
    
    def test_validate_star_model(self):
        """测试星型模式验证"""
        # 有效的星型模式
        valid_star_model = {
            'fact_tables': [{
                'name': 'sales_fact',
                'measures': [{'name': 'amount', 'data_type': 'decimal'}],
                'dimension_keys': [{'name': 'customer', 'dimension_table': 'customer_dim'}]
            }],
            'dimension_tables': [{
                'name': 'customer_dim',
                'attributes': [{'name': 'customer_name', 'data_type': 'string'}]
            }]
        }
        
        result = self.validator.validate_star_model(valid_star_model)
        self.assertTrue(result['valid'])
        
        # 无效的星型模式（没有事实表）
        invalid_star_model = {
            'fact_tables': [],
            'dimension_tables': [{
                'name': 'customer_dim',
                'attributes': [{'name': 'customer_name', 'data_type': 'string'}]
            }]
        }
        
        result = self.validator.validate_star_model(invalid_star_model)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)


if __name__ == '__main__':
    unittest.main()
