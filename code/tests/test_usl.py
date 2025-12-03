"""
USL单元测试
"""

import pytest
from usl import (
    USLParser,
    USLValidator,
    USLToOpenAPIConverter,
    USLToJSONSchemaConverter
)


def test_usl_parser():
    """测试USL解析"""
    parser = USLParser()
    
    usl_code = """
    schema PaymentSchema {
      type Currency: String {
        constraint: enum("USD", "EUR", "CNY")
      }
      
      field currency: Currency {
        required: true
        default: "USD"
      }
      
      field amount: Decimal {
        required: true
        constraint: {
          min: 0
          max: 1000000
        }
      }
    }
    """
    
    ast = parser.parse(usl_code)
    assert ast is not None
    assert ast.get('type') == 'schema'
    assert ast.get('name') == 'PaymentSchema'


def test_usl_validator():
    """测试USL验证"""
    parser = USLParser()
    usl_code = """
    schema TestSchema {
      field name: String {
        required: true
      }
    }
    """
    
    ast = parser.parse(usl_code)
    validator = USLValidator(ast)
    result = validator.validate()
    
    assert result is not None
    assert 'valid' in result


def test_usl_to_openapi():
    """测试USL到OpenAPI转换"""
    parser = USLParser()
    usl_code = """
    schema TestSchema {
      field name: String {
        required: true
      }
    }
    """
    
    ast = parser.parse(usl_code)
    converter = USLToOpenAPIConverter(ast)
    openapi_spec = converter.convert()
    
    assert openapi_spec is not None
    assert 'openapi' in openapi_spec
    assert 'components' in openapi_spec


def test_usl_to_json_schema():
    """测试USL到JSON Schema转换"""
    parser = USLParser()
    usl_code = """
    schema TestSchema {
      field name: String {
        required: true
      }
    }
    """
    
    ast = parser.parse(usl_code)
    converter = USLToJSONSchemaConverter(ast)
    json_schema = converter.convert()
    
    assert json_schema is not None
    assert '$schema' in json_schema
    assert 'properties' in json_schema
