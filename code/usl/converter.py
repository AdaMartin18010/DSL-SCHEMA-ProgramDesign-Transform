"""
USL转换器

将USL转换为其他格式（OpenAPI、JSON Schema等）
"""

from typing import Dict, Any, List


class USLToOpenAPIConverter:
    """USL到OpenAPI转换器"""
    
    def __init__(self, usl_ast: Dict[str, Any]):
        """
        初始化转换器
        
        Args:
            usl_ast: USL AST
        """
        self.usl_ast = usl_ast
    
    def convert(self) -> Dict[str, Any]:
        """
        转换为OpenAPI规范
        
        Returns:
            OpenAPI规范字典
        """
        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': self.usl_ast.get('name', 'Schema'),
                'version': '1.0.0'
            },
            'components': {
                'schemas': {}
            }
        }
        
        # 转换类型定义
        if 'body' in self.usl_ast and 'types' in self.usl_ast['body']:
            for type_def in self.usl_ast['body']['types']:
                type_name = type_def.get('name')
                schema = self._convert_type(type_def)
                openapi_spec['components']['schemas'][type_name] = schema
        
        # 转换字段定义
        if 'body' in self.usl_ast and 'fields' in self.usl_ast['body']:
            schema_name = self.usl_ast.get('name', 'Schema')
            properties = {}
            required = []
            
            for field in self.usl_ast['body']['fields']:
                field_name = field.get('name')
                field_schema = self._convert_type_spec(field.get('type_specifier'))
                
                # 应用约束
                if field.get('constraint'):
                    field_schema.update(self._convert_constraints(field.get('constraint')))
                
                properties[field_name] = field_schema
                
                # 检查是否必需
                if field.get('constraint', {}).get('required', False):
                    required.append(field_name)
            
            openapi_spec['components']['schemas'][schema_name] = {
                'type': 'object',
                'properties': properties,
                'required': required if required else None
            }
        
        return openapi_spec
    
    def _convert_type(self, type_def: Dict[str, Any]) -> Dict[str, Any]:
        """转换类型定义"""
        type_spec = type_def.get('type_specifier', {})
        return self._convert_type_spec(type_spec)
    
    def _convert_type_spec(self, type_spec: Dict[str, Any]) -> Dict[str, Any]:
        """转换类型说明符"""
        if type_spec.get('type') == 'primitive':
            return self._primitive_to_openapi(type_spec.get('name'))
        elif type_spec.get('type') == 'array':
            return {
                'type': 'array',
                'items': self._convert_type_spec(type_spec.get('item_type', {}))
            }
        elif type_spec.get('type') == 'map':
            return {
                'type': 'object',
                'additionalProperties': self._convert_type_spec(type_spec.get('value_type', {}))
            }
        elif type_spec.get('type') == 'object':
            return {
                'type': 'object',
                'properties': {}
            }
        elif type_spec.get('type') == 'reference':
            return {'$ref': f"#/components/schemas/{type_spec.get('name')}"}
        else:
            return {'type': 'string'}
    
    def _primitive_to_openapi(self, type_name: str) -> Dict[str, Any]:
        """原始类型到OpenAPI映射"""
        mapping = {
            'String': {'type': 'string'},
            'Integer': {'type': 'integer'},
            'Float': {'type': 'number', 'format': 'float'},
            'Decimal': {'type': 'number', 'format': 'double'},
            'Boolean': {'type': 'boolean'},
            'Date': {'type': 'string', 'format': 'date'},
            'DateTime': {'type': 'string', 'format': 'date-time'}
        }
        return mapping.get(type_name, {'type': 'string'})
    
    def _convert_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """转换约束"""
        openapi_constraints = {}
        
        if 'min' in constraints:
            openapi_constraints['minimum'] = constraints['min']
        if 'max' in constraints:
            openapi_constraints['maximum'] = constraints['max']
        if 'minLength' in constraints:
            openapi_constraints['minLength'] = constraints['minLength']
        if 'maxLength' in constraints:
            openapi_constraints['maxLength'] = constraints['maxLength']
        if 'pattern' in constraints:
            openapi_constraints['pattern'] = constraints['pattern']
        if 'enum' in constraints:
            openapi_constraints['enum'] = constraints['enum']
        if 'format' in constraints:
            openapi_constraints['format'] = constraints['format']
        
        return openapi_constraints


class USLToJSONSchemaConverter:
    """USL到JSON Schema转换器"""
    
    def __init__(self, usl_ast: Dict[str, Any]):
        """
        初始化转换器
        
        Args:
            usl_ast: USL AST
        """
        self.usl_ast = usl_ast
    
    def convert(self) -> Dict[str, Any]:
        """
        转换为JSON Schema
        
        Returns:
            JSON Schema字典
        """
        json_schema = {
            '$schema': 'http://json-schema.org/draft-2020-12/schema#',
            'type': 'object',
            'properties': {},
            'required': []
        }
        
        if 'body' in self.usl_ast and 'fields' in self.usl_ast['body']:
            for field in self.usl_ast['body']['fields']:
                field_name = field.get('name')
                field_schema = self._convert_type_spec(field.get('type_specifier'))
                
                # 应用约束
                if field.get('constraint'):
                    field_schema.update(self._convert_constraints(field.get('constraint')))
                
                json_schema['properties'][field_name] = field_schema
                
                # 检查是否必需
                if field.get('constraint', {}).get('required', False):
                    json_schema['required'].append(field_name)
        
        return json_schema
    
    def _convert_type_spec(self, type_spec: Dict[str, Any]) -> Dict[str, Any]:
        """转换类型说明符"""
        if type_spec.get('type') == 'primitive':
            return self._primitive_to_json_schema(type_spec.get('name'))
        elif type_spec.get('type') == 'array':
            return {
                'type': 'array',
                'items': self._convert_type_spec(type_spec.get('item_type', {}))
            }
        else:
            return {'type': 'string'}
    
    def _primitive_to_json_schema(self, type_name: str) -> Dict[str, Any]:
        """原始类型到JSON Schema映射"""
        mapping = {
            'String': {'type': 'string'},
            'Integer': {'type': 'integer'},
            'Float': {'type': 'number'},
            'Decimal': {'type': 'number'},
            'Boolean': {'type': 'boolean'},
            'Date': {'type': 'string', 'format': 'date'},
            'DateTime': {'type': 'string', 'format': 'date-time'}
        }
        return mapping.get(type_name, {'type': 'string'})
    
    def _convert_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """转换约束"""
        json_schema_constraints = {}
        
        if 'min' in constraints:
            json_schema_constraints['minimum'] = constraints['min']
        if 'max' in constraints:
            json_schema_constraints['maximum'] = constraints['max']
        if 'minLength' in constraints:
            json_schema_constraints['minLength'] = constraints['minLength']
        if 'maxLength' in constraints:
            json_schema_constraints['maxLength'] = constraints['maxLength']
        if 'pattern' in constraints:
            json_schema_constraints['pattern'] = constraints['pattern']
        if 'enum' in constraints:
            json_schema_constraints['enum'] = constraints['enum']
        
        return json_schema_constraints
