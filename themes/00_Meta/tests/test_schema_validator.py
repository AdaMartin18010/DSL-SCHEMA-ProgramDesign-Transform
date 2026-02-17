#!/usr/bin/env python3
"""
Schema验证器测试套件
"""

import unittest
import json
import sys
sys.path.insert(0, '../Tools')

from schema_validator import SchemaValidator


class TestSchemaValidator(unittest.TestCase):
    """Schema验证器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = SchemaValidator()
    
    def test_validate_simple_schema(self):
        """测试简单Schema验证"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        data = {"name": "John", "age": 30}
        result = self.validator.validate_json_schema(data, schema)
        self.assertTrue(result)
    
    def test_validate_invalid_data(self):
        """测试无效数据验证"""
        schema = {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"}
            }
        }
        
        data = {"email": "invalid-email"}
        result = self.validator.validate_json_schema(data, schema)
        self.assertFalse(result)
    
    def test_quality_check_good_schema(self):
        """测试高质量Schema检查"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "User Schema",
            "description": "User data schema",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "User name"
                }
            }
        }
        
        quality = self.validator.check_schema_quality(schema)
        self.assertGreater(quality['score'], 80)
    
    def test_quality_check_poor_schema(self):
        """测试低质量Schema检查"""
        schema = {
            "type": "object"
        }
        
        quality = self.validator.check_schema_quality(schema)
        self.assertLess(quality['score'], 80)
        self.assertTrue(len(quality['suggestions']) > 0)


class TestPerformance(unittest.TestCase):
    """性能测试类"""
    
    def test_large_schema_validation(self):
        """测试大规模Schema验证性能"""
        import time
        
        # 创建大型Schema
        schema = {
            "type": "object",
            "properties": {}
        }
        
        for i in range(100):
            schema["properties"][f"field_{i}"] = {
                "type": "string",
                "description": f"Field {i}"
            }
        
        data = {f"field_{i}": f"value_{i}" for i in range(100)}
        
        validator = SchemaValidator()
        
        start_time = time.time()
        result = validator.validate_json_schema(data, schema)
        end_time = time.time()
        
        # 验证应在1秒内完成
        self.assertTrue(end_time - start_time < 1.0)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
