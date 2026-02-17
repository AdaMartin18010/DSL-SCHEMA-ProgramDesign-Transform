#!/usr/bin/env python3
"""
Schema验证工具
提供JSON Schema、XML Schema、OpenAPI等多种格式的验证功能
"""

import json
import sys
from typing import Dict, List, Optional
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("Error: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


class SchemaValidator:
    """通用Schema验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_json_schema(self, data: dict, schema: dict) -> bool:
        """验证JSON数据是否符合JSON Schema"""
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            self.errors.append({
                'type': 'validation_error',
                'message': str(e.message),
                'path': list(e.path)
            })
            return False
    
    def validate_json_schema_detailed(self, data: dict, schema: dict) -> Dict:
        """详细验证并返回所有错误"""
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        
        return {
            'valid': len(errors) == 0,
            'error_count': len(errors),
            'errors': [{'message': e.message, 'path': list(e.path)} for e in errors]
        }
    
    def check_schema_quality(self, schema: dict) -> Dict:
        """检查Schema质量"""
        result = {'score': 100, 'suggestions': [], 'warnings': []}
        
        if 'description' not in schema:
            result['score'] -= 10
            result['suggestions'].append("Add 'description' to improve documentation")
        
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                if isinstance(prop_schema, dict) and 'description' not in prop_schema:
                    result['warnings'].append(f"Property '{prop_name}' lacks description")
        
        result['score'] = max(0, result['score'])
        return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Schema Validation Tool')
    parser.add_argument('--schema', '-s', required=True, help='Schema file path')
    parser.add_argument('--data', '-d', help='Data file to validate')
    parser.add_argument('--quality-check', '-q', action='store_true', help='Quality check')
    args = parser.parse_args()
    
    validator = SchemaValidator()
    
    with open(args.schema, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    if args.quality_check:
        quality = validator.check_schema_quality(schema)
        print(f"Quality Score: {quality['score']}/100")
    
    if args.data:
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = validator.validate_json_schema_detailed(data, schema)
        print("PASSED" if result['valid'] else f"FAILED ({result['error_count']} errors)")


if __name__ == '__main__':
    main()
