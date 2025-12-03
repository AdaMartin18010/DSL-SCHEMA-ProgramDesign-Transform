"""
USL解析器

使用Lark解析USL语法
"""

from lark import Lark, Transformer
from typing import Dict, Any, List
from .grammar import USL_GRAMMAR


class USLTransformer(Transformer):
    """USL AST转换器"""
    
    def start(self, items):
        return items[0]
    
    def schema(self, items):
        name = items[0]
        body = items[1] if len(items) > 1 else {}
        return {
            'type': 'schema',
            'name': name,
            'body': body
        }
    
    def identifier(self, items):
        return str(items[0])
    
    def schema_body(self, items):
        body = {
            'types': [],
            'fields': [],
            'constraints': [],
            'relations': [],
            'metadata': {}
        }
        
        for item in items:
            if isinstance(item, dict):
                if item.get('type') == 'type_definition':
                    body['types'].append(item)
                elif item.get('type') == 'field_definition':
                    body['fields'].append(item)
                elif item.get('type') == 'constraint_definition':
                    body['constraints'].append(item)
                elif item.get('type') == 'relation_definition':
                    body['relations'].append(item)
                elif item.get('type') == 'metadata_definition':
                    body['metadata'].update(item.get('items', {}))
        
        return body
    
    def type_definition(self, items):
        name = items[0]
        type_spec = items[1]
        constraint = items[2] if len(items) > 2 else None
        
        return {
            'type': 'type_definition',
            'name': name,
            'type_specifier': type_spec,
            'constraint': constraint
        }
    
    def type_specifier(self, items):
        return items[0]
    
    def primitive_type(self, items):
        return {'type': 'primitive', 'name': str(items[0])}
    
    def composite_type(self, items):
        if len(items) == 1:
            # Array
            return {'type': 'array', 'item_type': items[0]}
        elif len(items) == 2:
            # Map
            return {'type': 'map', 'key_type': items[0], 'value_type': items[1]}
        else:
            # Object
            return {'type': 'object', 'fields': items}
    
    def reference_type(self, items):
        return {'type': 'reference', 'name': str(items[0])}
    
    def field_definition(self, items):
        name = items[0]
        type_spec = items[1]
        constraint = items[2] if len(items) > 2 and items[2] else None
        default = items[3] if len(items) > 3 and items[3] else None
        
        return {
            'type': 'field_definition',
            'name': name,
            'type_specifier': type_spec,
            'constraint': constraint,
            'default': default
        }
    
    def constraint_clause(self, items):
        return items[0] if items else {}
    
    def constraint(self, items):
        key = str(items[0])
        value = items[1] if len(items) > 1 else None
        return {key: value}
    
    def boolean(self, items):
        return str(items[0]) == 'true'
    
    def number(self, items):
        val = float(items[0])
        return int(val) if val.is_integer() else val
    
    def string(self, items):
        return str(items[0])[1:-1]  # 移除引号
    
    def value(self, items):
        return items[0]
    
    def relation_definition(self, items):
        name = items[0]
        relation_type = items[1]
        source = items[2]
        target = items[3]
        
        return {
            'type': 'relation_definition',
            'name': name,
            'relation_type': relation_type,
            'source': source,
            'target': target
        }
    
    def relation_type(self, items):
        return str(items[0])
    
    def metadata_definition(self, items):
        return {
            'type': 'metadata_definition',
            'items': items[0] if items else {}
        }
    
    def metadata_item(self, items):
        key = items[0]
        value = items[1]
        return {key: value}


class USLParser:
    """USL解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.parser = Lark(USL_GRAMMAR, start='start', parser='lalr')
        self.transformer = USLTransformer()
    
    def parse(self, usl_code: str) -> Dict[str, Any]:
        """
        解析USL代码
        
        Args:
            usl_code: USL代码字符串
            
        Returns:
            AST字典
        """
        try:
            tree = self.parser.parse(usl_code)
            ast = self.transformer.transform(tree)
            return ast
        except Exception as e:
            raise ValueError(f"USL解析失败: {str(e)}")
