"""
增量转换器测试

测试增量转换器的核心功能
"""

import unittest
from data_transformation.incremental_converter import (
    IncrementalConverter,
    SchemaChange,
    ChangeType
)


class TestIncrementalConverter(unittest.TestCase):
    """增量转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = IncrementalConverter()
    
    def test_compute_schema_hash(self):
        """测试Schema哈希计算"""
        schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        hash1 = self.converter.compute_schema_hash(schema)
        hash2 = self.converter.compute_schema_hash(schema)
        
        # 相同Schema应该产生相同哈希
        self.assertEqual(hash1, hash2)
        
        # 修改Schema应该产生不同哈希
        schema2 = schema.copy()
        schema2['tables']['users']['fields']['email'] = {'type': 'string'}
        hash3 = self.converter.compute_schema_hash(schema2)
        
        self.assertNotEqual(hash1, hash3)
    
    def test_detect_changes_no_change(self):
        """测试无变更检测"""
        schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        changes = self.converter.detect_changes(schema, schema)
        self.assertEqual(len(changes), 0)
    
    def test_detect_changes_add_field(self):
        """测试新增字段检测"""
        old_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        new_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'}
                    }
                }
            }
        }
        
        changes = self.converter.detect_changes(old_schema, new_schema)
        
        # 应该检测到新增字段
        self.assertGreater(len(changes), 0)
        
        add_changes = [c for c in changes if c.change_type == ChangeType.ADD]
        self.assertGreater(len(add_changes), 0)
        
        # 检查路径
        email_change = [c for c in add_changes if 'email' in c.path]
        self.assertGreater(len(email_change), 0)
    
    def test_detect_changes_delete_field(self):
        """测试删除字段检测"""
        old_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'}
                    }
                }
            }
        }
        
        new_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        changes = self.converter.detect_changes(old_schema, new_schema)
        
        # 应该检测到删除字段
        delete_changes = [c for c in changes if c.change_type == ChangeType.DELETE]
        self.assertGreater(len(delete_changes), 0)
    
    def test_detect_changes_modify_field(self):
        """测试修改字段检测"""
        old_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        new_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'bigint'},  # 类型改变
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        changes = self.converter.detect_changes(old_schema, new_schema)
        
        # 应该检测到修改字段
        modify_changes = [c for c in changes if c.change_type == ChangeType.MODIFY]
        self.assertGreater(len(modify_changes), 0)
    
    def test_build_dependency_graph(self):
        """测试依赖图构建"""
        schema = {
            'tables': {
                'customers': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                },
                'orders': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'customer_id': {
                            'type': 'integer',
                            'foreign_key': {
                                'references_table': 'customers',
                                'references_field': 'id'
                            }
                        }
                    }
                }
            }
        }
        
        graph = self.converter.build_dependency_graph(schema)
        
        # 应该有两个节点
        self.assertGreaterEqual(len(graph), 2)
        
        # orders应该依赖customers
        orders_node = graph.get('table_orders')
        self.assertIsNotNone(orders_node)
        self.assertIn('table_customers', orders_node.dependencies)
    
    def test_incremental_convert(self):
        """测试增量转换"""
        old_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        
        new_schema = {
            'tables': {
                'users': {
                    'fields': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'}
                    }
                }
            }
        }
        
        result = self.converter.incremental_convert(old_schema, new_schema, 'postgresql')
        
        # 应该成功转换
        self.assertTrue(result['success'])
        self.assertTrue(result['has_changes'])
        self.assertGreater(result['changes_count'], 0)
        
        # 应该生成SQL语句
        conversion_result = result.get('conversion_result', {})
        statements = conversion_result.get('statements', [])
        self.assertGreater(len(statements), 0)
        
        # 应该包含ALTER TABLE语句
        alter_statements = [s for s in statements if 'ALTER TABLE' in s]
        self.assertGreater(len(alter_statements), 0)


if __name__ == '__main__':
    unittest.main()
