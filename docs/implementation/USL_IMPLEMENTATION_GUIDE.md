# 统一Schema语言（USL）实现指南

## 📑 目录

- [统一Schema语言（USL）实现指南](#统一schema语言usl实现指南)
  - [📑 目录](#-目录)
  - [1. 实现概述](#1-实现概述)
    - [1.1 实现目标](#11-实现目标)
    - [1.2 实现架构](#12-实现架构)
  - [2. 技术栈选择](#2-技术栈选择)
    - [2.1 解析器](#21-解析器)
    - [2.2 框架](#22-框架)
  - [3. USL语法设计](#3-usl语法设计)
    - [3.1 USL语法（EBNF）](#31-usl语法ebnf)
    - [3.2 USL示例](#32-usl示例)
  - [4. USL解析器实现](#4-usl解析器实现)
    - [4.1 Lark语法定义](#41-lark语法定义)
  - [5. USL验证器实现](#5-usl验证器实现)
    - [5.1 类型检查器](#51-类型检查器)
  - [6. USL转换器实现](#6-usl转换器实现)
    - [6.1 USL到OpenAPI转换](#61-usl到openapi转换)
  - [7. 应用示例](#7-应用示例)
    - [7.1 完整示例](#71-完整示例)
  - [8. 测试与验证](#8-测试与验证)
    - [8.1 单元测试](#81-单元测试)
  - [9. 相关文档](#9-相关文档)
    - [架构和设计模式参考](#架构和设计模式参考)
    - [其他实现指南](#其他实现指南)

---

## 1. 实现概述

### 1.1 实现目标

- ✅ USL语法设计
- ✅ USL解析器实现
- ✅ USL验证器实现
- ✅ USL转换器实现

### 1.2 实现架构

```text
USL系统
├── 语法层
│   ├── USL语法定义（BNF/EBNF）
│   └── 词法分析器
├── 解析层
│   ├── 语法解析器（ANTLR/Lark）
│   └── AST生成
├── 验证层
│   ├── 类型检查
│   ├── 约束验证
│   └── 语义验证
├── 转换层
│   ├── USL → OpenAPI
│   ├── USL → JSON Schema
│   └── USL → 其他格式
└── API层
    └── REST API
```

---

## 2. 技术栈选择

### 2.1 解析器

- **Lark**：Python解析器生成器，易于使用
- **ANTLR**：强大的解析器生成器，多语言支持

### 2.2 框架

- **Python 3.10+**
- **Lark**：语法解析
- **Pydantic**：数据验证
- **FastAPI**：REST API框架

---

## 3. USL语法设计

### 3.1 USL语法（EBNF）

```ebnf
usl_schema ::= schema_declaration schema_body

schema_declaration ::= "schema" identifier "{" schema_body "}"

schema_body ::= (type_definition | field_definition | constraint_definition | relation_definition | metadata_definition)*

type_definition ::= "type" identifier ":" type_specifier constraint_clause?

type_specifier ::= primitive_type | composite_type | reference_type

primitive_type ::= "String" | "Integer" | "Float" | "Boolean" | "Date" | "DateTime"

composite_type ::= "Array" "<" type_specifier ">" | "Map" "<" type_specifier "," type_specifier ">" | "Object" "{" field_definition* "}"

reference_type ::= identifier

field_definition ::= "field" identifier ":" type_specifier constraint_clause? default_clause?

constraint_clause ::= "{" constraint* "}"

constraint ::= "required" ":" boolean
             | "min" ":" number
             | "max" ":" number
             | "pattern" ":" string
             | "enum" ":" "[" value ("," value)* "]"
             | "format" ":" string

default_clause ::= "default" ":" value

relation_definition ::= "relation" identifier ":" relation_type "(" identifier "," identifier ")"

relation_type ::= "one_to_one" | "one_to_many" | "many_to_many"

metadata_definition ::= "metadata" "{" metadata_item* "}"

metadata_item ::= identifier ":" value

identifier ::= [a-zA-Z_][a-zA-Z0-9_]*

value ::= string | number | boolean | null
```

### 3.2 USL示例

```usl
schema PaymentSchema {
  // 类型定义
  type Currency: String {
    constraint: enum("USD", "EUR", "CNY")
  }

  type Amount: Decimal {
    constraint: {
      min: 0
      max: 1000000
      precision: 2
    }
  }

  type Person: Object {
    field name: String { required: true }
    field email: String {
      required: true
      constraint: pattern("^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$")
    }
  }

  // 字段定义
  field currency: Currency {
    required: true
    default: "USD"
  }

  field amount: Amount {
    required: true
  }

  field debtor: Person {
    required: true
  }

  field creditor: Person {
    required: true
  }

  // 关系定义
  relation payment_flow: one_to_many(debtor, creditor)

  // 元数据
  metadata {
    version: "1.0"
    author: "DSL Schema Team"
    created_at: "2024-01-21"
  }
}
```

---

## 4. USL解析器实现

### 4.1 Lark语法定义

```python
from lark import Lark, Transformer

usl_grammar = """
    start: schema

    schema: "schema" IDENTIFIER "{" schema_body "}"

    schema_body: (type_def | field_def | constraint_def | relation_def | metadata_def)*

    type_def: "type" IDENTIFIER ":" type_spec constraint_clause?

    type_spec: primitive_type | composite_type | reference_type

    primitive_type: "String" | "Integer" | "Float" | "Boolean" | "Date" | "DateTime" | "Decimal"

    composite_type: "Array" "<" type_spec ">"
                  | "Map" "<" type_spec "," type_spec ">"
                  | "Object" "{" field_def* "}"

    reference_type: IDENTIFIER

    field_def: "field" IDENTIFIER ":" type_spec constraint_clause? default_clause?

    constraint_clause: "{" constraint* "}"

    constraint: "required" ":" BOOLEAN
             | "min" ":" NUMBER
             | "max" ":" NUMBER
             | "pattern" ":" STRING
             | "enum" ":" "[" value ("," value)* "]"
             | "format" ":" STRING
             | "precision" ":" NUMBER

    default_clause: "default" ":" value

    relation_def: "relation" IDENTIFIER ":" relation_type "(" IDENTIFIER "," IDENTIFIER ")"

    relation_type: "one_to_one" | "one_to_many" | "many_to_many"

    metadata_def: "metadata" "{" metadata_item* "}"

    metadata_item: IDENTIFIER ":" value

    value: STRING | NUMBER | BOOLEAN | "null"

    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /"[^"]*"/
    NUMBER: /-?\d+(\.\d+)?/
    BOOLEAN: "true" | "false"

    %import common.WS
    %ignore WS
"""

class USLTransformer(Transformer):
    """USL AST转换器"""

    def schema(self, items):
        name = items[0]
        body = items[1]
        return {'type': 'schema', 'name': name, 'body': body}

    def type_def(self, items):
        name = items[0]
        type_spec = items[1]
        constraint = items[2] if len(items) > 2 else None
        return {'type': 'type_definition', 'name': name,
                'type_spec': type_spec, 'constraint': constraint}

    def field_def(self, items):
        name = items[0]
        type_spec = items[1]
        constraint = items[2] if len(items) > 2 and items[2] else None
        default = items[3] if len(items) > 3 and items[3] else None
        return {'type': 'field_definition', 'name': name,
                'type_spec': type_spec, 'constraint': constraint, 'default': default}

    # ... 更多转换方法

class USLParser:
    """USL解析器"""

    def __init__(self):
        self.parser = Lark(usl_grammar, start='start', parser='lalr')
        self.transformer = USLTransformer()

    def parse(self, usl_code: str) -> dict:
        """解析USL代码"""
        tree = self.parser.parse(usl_code)
        ast = self.transformer.transform(tree)
        return ast
```

---

## 5. USL验证器实现

### 5.1 类型检查器

```python
class USLTypeChecker:
    """USL类型检查器"""

    def __init__(self, ast: dict):
        self.ast = ast
        self.type_registry = {}
        self.errors = []

    def check(self) -> bool:
        """执行类型检查"""
        # 注册类型定义
        self.register_types()

        # 检查字段类型
        self.check_fields()

        # 检查约束
        self.check_constraints()

        return len(self.errors) == 0

    def register_types(self):
        """注册类型定义"""
        schema_body = self.ast['body']
        for item in schema_body:
            if item['type'] == 'type_definition':
                self.type_registry[item['name']] = item

    def check_fields(self):
        """检查字段类型"""
        schema_body = self.ast['body']
        for item in schema_body:
            if item['type'] == 'field_definition':
                type_spec = item['type_spec']
                if not self.is_valid_type(type_spec):
                    self.errors.append(
                        f"Invalid type for field {item['name']}: {type_spec}"
                    )

    def is_valid_type(self, type_spec) -> bool:
        """检查类型是否有效"""
        if isinstance(type_spec, str):
            # 原始类型或引用类型
            primitive_types = ['String', 'Integer', 'Float', 'Boolean',
                              'Date', 'DateTime', 'Decimal']
            if type_spec in primitive_types:
                return True
            if type_spec in self.type_registry:
                return True
            return False
        elif isinstance(type_spec, dict):
            # 复合类型
            if type_spec['type'] == 'Array':
                return self.is_valid_type(type_spec['element_type'])
            elif type_spec['type'] == 'Map':
                return (self.is_valid_type(type_spec['key_type']) and
                       self.is_valid_type(type_spec['value_type']))
        return False
```

---

## 6. USL转换器实现

### 6.1 USL到OpenAPI转换

```python
class USLToOpenAPIConverter:
    """USL到OpenAPI转换器"""

    def __init__(self, usl_ast: dict):
        self.usl_ast = usl_ast

    def convert(self) -> dict:
        """转换为OpenAPI格式"""
        openapi_spec = {
            'openapi': '3.1.0',
            'info': {
                'title': self.usl_ast['name'],
                'version': self.get_metadata('version', '1.0.0')
            },
            'components': {
                'schemas': {}
            }
        }

        # 转换类型定义
        schema_body = self.usl_ast['body']
        for item in schema_body:
            if item['type'] == 'type_definition':
                openapi_spec['components']['schemas'][item['name']] = \
                    self.convert_type(item)
            elif item['type'] == 'field_definition':
                # 字段转换为属性
                if self.usl_ast['name'] not in openapi_spec['components']['schemas']:
                    openapi_spec['components']['schemas'][self.usl_ast['name']] = {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                schema = openapi_spec['components']['schemas'][self.usl_ast['name']]
                schema['properties'][item['name']] = self.convert_field(item)
                if item.get('constraint', {}).get('required'):
                    schema['required'].append(item['name'])

        return openapi_spec

    def convert_type(self, type_def: dict) -> dict:
        """转换类型定义"""
        type_spec = type_def['type_spec']
        openapi_type = self.type_spec_to_openapi(type_spec)

        # 添加约束
        if type_def.get('constraint'):
            openapi_type.update(self.convert_constraints(type_def['constraint']))

        return openapi_type

    def type_spec_to_openapi(self, type_spec) -> dict:
        """类型规范转换为OpenAPI"""
        if isinstance(type_spec, str):
            type_mapping = {
                'String': {'type': 'string'},
                'Integer': {'type': 'integer'},
                'Float': {'type': 'number', 'format': 'float'},
                'Decimal': {'type': 'number', 'format': 'double'},
                'Boolean': {'type': 'boolean'},
                'Date': {'type': 'string', 'format': 'date'},
                'DateTime': {'type': 'string', 'format': 'date-time'}
            }
            if type_spec in type_mapping:
                return type_mapping[type_spec]
            else:
                # 引用类型
                return {'$ref': f'#/components/schemas/{type_spec}'}
        elif isinstance(type_spec, dict):
            if type_spec['type'] == 'Array':
                return {
                    'type': 'array',
                    'items': self.type_spec_to_openapi(type_spec['element_type'])
                }
            elif type_spec['type'] == 'Map':
                return {
                    'type': 'object',
                    'additionalProperties': self.type_spec_to_openapi(
                        type_spec['value_type']
                    )
                }
        return {}

    def convert_constraints(self, constraints: dict) -> dict:
        """转换约束"""
        openapi_constraints = {}

        if 'min' in constraints:
            openapi_constraints['minimum'] = constraints['min']
        if 'max' in constraints:
            openapi_constraints['maximum'] = constraints['max']
        if 'pattern' in constraints:
            openapi_constraints['pattern'] = constraints['pattern']
        if 'enum' in constraints:
            openapi_constraints['enum'] = constraints['enum']
        if 'format' in constraints:
            openapi_constraints['format'] = constraints['format']

        return openapi_constraints
```

---

## 7. 应用示例

### 7.1 完整示例

```python
from usl_parser import USLParser
from usl_validator import USLTypeChecker
from usl_converter import USLToOpenAPIConverter

# USL代码
usl_code = """
schema PaymentSchema {
  type Currency: String {
    constraint: enum("USD", "EUR", "CNY")
  }

  type Amount: Decimal {
    constraint: {
      min: 0
      max: 1000000
      precision: 2
    }
  }

  field currency: Currency {
    required: true
    default: "USD"
  }

  field amount: Amount {
    required: true
  }

  metadata {
    version: "1.0"
  }
}
"""

# 解析
parser = USLParser()
ast = parser.parse(usl_code)

# 验证
checker = USLTypeChecker(ast)
if checker.check():
    print("USL schema is valid")
else:
    print(f"Validation errors: {checker.errors}")

# 转换
converter = USLToOpenAPIConverter(ast)
openapi_spec = converter.convert()
print(json.dumps(openapi_spec, indent=2))
```

---

## 8. 测试与验证

### 8.1 单元测试

```python
import pytest
from usl_parser import USLParser
from usl_validator import USLTypeChecker
from usl_converter import USLToOpenAPIConverter

def test_usl_parsing():
    """测试USL解析"""
    parser = USLParser()
    usl_code = "schema Test { field name: String }"
    ast = parser.parse(usl_code)
    assert ast['type'] == 'schema'
    assert ast['name'] == 'Test'

def test_usl_validation():
    """测试USL验证"""
    parser = USLParser()
    ast = parser.parse(usl_code)
    checker = USLTypeChecker(ast)
    assert checker.check() == True

def test_usl_to_openapi():
    """测试USL到OpenAPI转换"""
    parser = USLParser()
    ast = parser.parse(usl_code)
    converter = USLToOpenAPIConverter(ast)
    openapi = converter.convert()
    assert 'openapi' in openapi
    assert 'components' in openapi
```

---

## 9. 相关文档

### 架构和设计模式参考

在实现过程中，建议参考以下模式文档：

- **架构模式**：`../structure/ARCHITECTURE_PATTERNS_SUMMARY.md`
  - 推荐使用**四层架构**（语法层、解析层、验证层、转换层、API层）
- **设计模式**：`../structure/DESIGN_PATTERNS_SUMMARY.md`
  - 工厂模式：创建解析器、验证器、转换器
  - 策略模式：选择转换策略
  - 适配器模式：不同格式之间的适配
  - 建造者模式：构建复杂Schema
- **信息处理模式**：`../structure/INFORMATION_PROCESSING_PATTERNS_SUMMARY.md`
  - ETL模式：提取、转换、加载
- **表征模式**：`../structure/REPRESENTATION_PATTERNS_SUMMARY.md`
  - 形式语言表征：USL语法定义
- **模式快速参考**：`../structure/PATTERNS_QUICK_REFERENCE.md` ⭐推荐

### 其他实现指南

- `MULTIMODAL_KG_IMPLEMENTATION_GUIDE.md` - 多模态知识图谱实现指南
- `TEMPORAL_KG_IMPLEMENTATION_GUIDE.md` - 时序知识图谱实现指南
- `LLM_REASONING_IMPLEMENTATION_GUIDE.md` - LLM推理引擎实现指南
- `README.md` - 实现指南目录

---

**创建时间**：2025-01-21
**最后更新**：2025-01-27
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
