# GraphQL Schema转换体系

## 📑 目录

- [GraphQL Schema转换体系](#graphql-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GraphQL到OpenAPI转换](#2-graphql到openapi转换)
  - [3. GraphQL到JSON Schema转换](#3-graphql到json-schema转换)
  - [4. GraphQL到gRPC转换](#4-graphql到grpc转换)
  - [5. 转换验证](#5-转换验证)
  - [6. GraphQL数据存储与分析](#6-graphql数据存储与分析)
    - [6.1 PostgreSQL GraphQL数据存储](#61-postgresql-graphql数据存储)
    - [6.2 GraphQL数据分析查询](#62-graphql数据分析查询)

---

## 1. 转换体系概述

GraphQL Schema转换体系支持GraphQL Schema与其他API和数据格式之间的转换。

### 1.1 转换目标

1. **GraphQL到OpenAPI转换**：GraphQL Schema转换为OpenAPI规范
2. **GraphQL到JSON Schema转换**：GraphQL类型转换为JSON Schema
3. **GraphQL到gRPC转换**：GraphQL Schema转换为gRPC服务定义
4. **Schema到数据库转换**：GraphQL Schema定义到PostgreSQL存储

---

## 2. GraphQL到OpenAPI转换

**转换规则**：

- GraphQL类型 → OpenAPI Schema对象
- GraphQL查询 → OpenAPI POST端点
- GraphQL变更 → OpenAPI POST端点
- GraphQL订阅 → OpenAPI WebSocket端点

**转换示例**：

```python
from graphql import build_schema, parse
from openapi_spec_validator import validate_spec

def graphql_to_openapi(graphql_schema: str) -> dict:
    """将GraphQL Schema转换为OpenAPI规范"""
    schema = build_schema(graphql_schema)

    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "GraphQL API",
            "version": "1.0.0",
            "description": "Generated from GraphQL Schema"
        },
        "servers": [
            {
                "url": "https://api.example.com/graphql",
                "description": "GraphQL API Server"
            }
        ],
        "paths": {
            "/graphql": {
                "post": {
                    "summary": "GraphQL Query/Mutation",
                    "operationId": "graphqlQuery",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "GraphQL query string"
                                        },
                                        "variables": {
                                            "type": "object",
                                            "description": "GraphQL variables"
                                        },
                                        "operationName": {
                                            "type": "string",
                                            "description": "Operation name"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "GraphQL response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "object",
                                                "description": "GraphQL data"
                                            },
                                            "errors": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "message": {"type": "string"},
                                                        "locations": {"type": "array"},
                                                        "path": {"type": "array"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": convert_graphql_types_to_openapi_schemas(schema)
        }
    }

    return openapi_spec

def convert_graphql_types_to_openapi_schemas(schema):
    """将GraphQL类型转换为OpenAPI Schema"""
    schemas = {}

    for type_name, graphql_type in schema.type_map.items():
        if type_name.startswith("__"):
            continue

        if graphql_type.is_scalar_type():
            schemas[type_name] = convert_scalar_type(graphql_type)
        elif graphql_type.is_object_type():
            schemas[type_name] = convert_object_type(graphql_type)
        elif graphql_type.is_interface_type():
            schemas[type_name] = convert_interface_type(graphql_type)
        elif graphql_type.is_union_type():
            schemas[type_name] = convert_union_type(graphql_type)
        elif graphql_type.is_enum_type():
            schemas[type_name] = convert_enum_type(graphql_type)
        elif graphql_type.is_input_object_type():
            schemas[type_name] = convert_input_type(graphql_type)

    return schemas

def convert_scalar_type(scalar_type):
    """转换标量类型"""
    scalar_map = {
        "Int": {"type": "integer", "format": "int32"},
        "Float": {"type": "number", "format": "double"},
        "String": {"type": "string"},
        "Boolean": {"type": "boolean"},
        "ID": {"type": "string", "format": "uuid"}
    }
    return scalar_map.get(scalar_type.name, {"type": "string"})

def convert_object_type(object_type):
    """转换对象类型"""
    properties = {}
    required = []

    for field_name, field in object_type.fields.items():
        properties[field_name] = convert_field_type(field.type)
        if field.type.is_non_null_type():
            required.append(field_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required if required else None
    }
```

---

## 3. GraphQL到JSON Schema转换

**转换规则**：

- GraphQL标量类型 → JSON Schema基本类型
- GraphQL对象类型 → JSON Schema对象
- GraphQL列表类型 → JSON Schema数组
- GraphQL非空类型 → JSON Schema required

**转换示例**：

```python
import json
from graphql import build_schema

def graphql_to_json_schema(graphql_schema: str, type_name: str) -> dict:
    """将GraphQL类型转换为JSON Schema"""
    schema = build_schema(graphql_schema)
    graphql_type = schema.get_type(type_name)

    json_schema = convert_type_to_json_schema(graphql_type, schema)
    return json_schema

def convert_type_to_json_schema(graphql_type, schema):
    """递归转换GraphQL类型为JSON Schema"""
    if graphql_type.is_scalar_type():
        return convert_scalar_to_json_schema(graphql_type)
    elif graphql_type.is_object_type():
        return convert_object_to_json_schema(graphql_type, schema)
    elif graphql_type.is_list_type():
        return {
            "type": "array",
            "items": convert_type_to_json_schema(graphql_type.of_type, schema)
        }
    elif graphql_type.is_non_null_type():
        result = convert_type_to_json_schema(graphql_type.of_type, schema)
        result["required"] = True
        return result
    elif graphql_type.is_enum_type():
        return {
            "type": "string",
            "enum": [value.name for value in graphql_type.values]
        }
    elif graphql_type.is_input_object_type():
        return convert_input_to_json_schema(graphql_type, schema)

    return {"type": "object"}

def convert_scalar_to_json_schema(scalar_type):
    """转换标量类型"""
    scalar_map = {
        "Int": {"type": "integer"},
        "Float": {"type": "number"},
        "String": {"type": "string"},
        "Boolean": {"type": "boolean"},
        "ID": {"type": "string"}
    }
    return scalar_map.get(scalar_type.name, {"type": "string"})

def convert_object_to_json_schema(object_type, schema):
    """转换对象类型"""
    properties = {}
    required = []

    for field_name, field in object_type.fields.items():
        field_schema = convert_type_to_json_schema(field.type, schema)
        properties[field_name] = field_schema

        if field.type.is_non_null_type():
            required.append(field_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required if required else None
    }
```

---

## 4. GraphQL到gRPC转换

**转换规则**：

- GraphQL查询 → gRPC服务方法
- GraphQL变更 → gRPC服务方法
- GraphQL类型 → Protocol Buffers消息
- GraphQL输入类型 → Protocol Buffers消息

**转换示例**：

```python
def graphql_to_grpc(graphql_schema: str) -> str:
    """将GraphQL Schema转换为gRPC Protocol Buffers定义"""
    schema = build_schema(graphql_schema)

    proto_content = 'syntax = "proto3";\n\n'
    proto_content += 'package graphql;\n\n'

    # 转换类型为Protocol Buffers消息
    for type_name, graphql_type in schema.type_map.items():
        if type_name.startswith("__"):
            continue
        if graphql_type.is_object_type() or graphql_type.is_input_object_type():
            proto_content += convert_type_to_proto(graphql_type, schema)

    # 转换查询和变更为gRPC服务
    query_type = schema.query_type
    mutation_type = schema.mutation_type

    proto_content += '\nservice GraphQLService {\n'

    if query_type:
        for field_name, field in query_type.fields.items():
            proto_content += f'  rpc {field_name}({field_name}Request) returns ({field_name}Response);\n'

    if mutation_type:
        for field_name, field in mutation_type.fields.items():
            proto_content += f'  rpc {field_name}({field_name}Request) returns ({field_name}Response);\n'

    proto_content += '}\n'

    return proto_content

def convert_type_to_proto(graphql_type, schema):
    """转换GraphQL类型为Protocol Buffers消息"""
    proto_content = f'message {graphql_type.name} {{\n'

    field_number = 1
    for field_name, field in graphql_type.fields.items():
        proto_type = convert_graphql_type_to_proto_type(field.type, schema)
        proto_content += f'  {proto_type} {field_name} = {field_number};\n'
        field_number += 1

    proto_content += '}\n\n'
    return proto_content

def convert_graphql_type_to_proto_type(graphql_type, schema):
    """转换GraphQL类型为Protocol Buffers类型"""
    if graphql_type.is_scalar_type():
        scalar_map = {
            "Int": "int32",
            "Float": "double",
            "String": "string",
            "Boolean": "bool",
            "ID": "string"
        }
        return scalar_map.get(graphql_type.name, "string")
    elif graphql_type.is_list_type():
        item_type = convert_graphql_type_to_proto_type(graphql_type.of_type, schema)
        return f"repeated {item_type}"
    elif graphql_type.is_non_null_type():
        return convert_graphql_type_to_proto_type(graphql_type.of_type, schema)
    elif graphql_type.is_object_type() or graphql_type.is_input_object_type():
        return graphql_type.name
    else:
        return "string"
```

---

## 5. 转换验证

验证转换的Schema完整性、类型一致性和功能等价性。

**验证规则**：

1. **类型映射验证**：确保所有GraphQL类型都有对应的目标类型
2. **字段映射验证**：确保所有字段都正确映射
3. **约束验证**：确保约束规则正确转换
4. **功能等价验证**：确保转换后的Schema功能等价

---

## 6. GraphQL数据存储与分析

### 6.1 PostgreSQL GraphQL数据存储

**GraphQL数据存储方案**：

```python
import psycopg2
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from graphql import build_schema, parse, execute

logger = logging.getLogger(__name__)

class GraphQLDataStore:
    """GraphQL数据存储类"""

    def __init__(self, db_config: Dict):
        """初始化数据库连接"""
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建GraphQL数据存储表"""
        with self.conn.cursor() as cur:
            # Schema定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graphql_schemas (
                    id SERIAL PRIMARY KEY,
                    schema_name VARCHAR(255) NOT NULL UNIQUE,
                    schema_definition TEXT NOT NULL,
                    version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 类型定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graphql_types (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES graphql_schemas(id),
                    type_name VARCHAR(255) NOT NULL,
                    type_kind VARCHAR(50) NOT NULL,
                    description TEXT,
                    definition JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(schema_id, type_name)
                )
            """)

            # 字段定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graphql_fields (
                    id SERIAL PRIMARY KEY,
                    type_id INTEGER REFERENCES graphql_types(id),
                    field_name VARCHAR(255) NOT NULL,
                    field_type VARCHAR(255) NOT NULL,
                    is_required BOOLEAN DEFAULT FALSE,
                    is_deprecated BOOLEAN DEFAULT FALSE,
                    deprecation_reason TEXT,
                    description TEXT,
                    arguments JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(type_id, field_name)
                )
            """)

            # 查询日志表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graphql_queries (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES graphql_schemas(id),
                    query_string TEXT NOT NULL,
                    variables JSONB,
                    operation_name VARCHAR(255),
                    execution_time_ms INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 查询性能指标表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graphql_performance (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES graphql_schemas(id),
                    query_hash VARCHAR(64) NOT NULL,
                    operation_name VARCHAR(255),
                    avg_execution_time_ms DECIMAL(10, 2),
                    min_execution_time_ms INTEGER,
                    max_execution_time_ms INTEGER,
                    call_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    last_executed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(schema_id, query_hash)
                )
            """)

            # 类型使用统计表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graphql_type_usage (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES graphql_schemas(id),
                    type_name VARCHAR(255) NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_used_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(schema_id, type_name)
                )
            """)

            self.conn.commit()
            logger.info("GraphQL数据存储表创建成功")

    def store_schema(self, schema_name: str, schema_definition: str, version: str = "1.0.0"):
        """存储GraphQL Schema定义"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO graphql_schemas (schema_name, schema_definition, version)
                VALUES (%s, %s, %s)
                ON CONFLICT (schema_name)
                DO UPDATE SET
                    schema_definition = EXCLUDED.schema_definition,
                    version = EXCLUDED.version,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (schema_name, schema_definition, version))

            schema_id = cur.fetchone()[0]
            self.conn.commit()

            # 解析并存储类型和字段
            schema = build_schema(schema_definition)
            self._store_types(schema_id, schema)

            logger.info(f"GraphQL Schema '{schema_name}' 存储成功，ID: {schema_id}")
            return schema_id

    def _store_types(self, schema_id: int, schema):
        """存储类型和字段定义"""
        with self.conn.cursor() as cur:
            for type_name, graphql_type in schema.type_map.items():
                if type_name.startswith("__"):
                    continue

                # 存储类型
                cur.execute("""
                    INSERT INTO graphql_types (schema_id, type_name, type_kind, description, definition)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (schema_id, type_name)
                    DO UPDATE SET
                        type_kind = EXCLUDED.type_kind,
                        description = EXCLUDED.description,
                        definition = EXCLUDED.definition
                    RETURNING id
                """, (
                    schema_id,
                    type_name,
                    graphql_type.kind,
                    getattr(graphql_type, 'description', None),
                    json.dumps({"name": type_name, "kind": graphql_type.kind})
                ))

                type_id = cur.fetchone()[0]

                # 存储字段
                if hasattr(graphql_type, 'fields'):
                    for field_name, field in graphql_type.fields.items():
                        cur.execute("""
                            INSERT INTO graphql_fields (
                                type_id, field_name, field_type, is_required,
                                is_deprecated, deprecation_reason, description, arguments
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (type_id, field_name)
                            DO UPDATE SET
                                field_type = EXCLUDED.field_type,
                                is_required = EXCLUDED.is_required,
                                is_deprecated = EXCLUDED.is_deprecated,
                                deprecation_reason = EXCLUDED.deprecation_reason,
                                description = EXCLUDED.description,
                                arguments = EXCLUDED.arguments
                        """, (
                            type_id,
                            field_name,
                            str(field.type),
                            field.type.is_non_null_type(),
                            getattr(field, 'is_deprecated', False),
                            getattr(field, 'deprecation_reason', None),
                            getattr(field, 'description', None),
                            json.dumps([{"name": arg.name, "type": str(arg.type)}
                                      for arg in field.args]) if field.args else None
                        ))

            self.conn.commit()

    def log_query(self, schema_id: int, query_string: str, variables: Dict = None,
                  operation_name: str = None, execution_time_ms: int = None,
                  error_message: str = None):
        """记录GraphQL查询日志"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO graphql_queries (
                    schema_id, query_string, variables, operation_name,
                    execution_time_ms, error_message
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                schema_id,
                query_string,
                json.dumps(variables) if variables else None,
                operation_name,
                execution_time_ms,
                error_message
            ))
            self.conn.commit()

    def update_performance_metrics(self, schema_id: int, query_hash: str,
                                  operation_name: str, execution_time_ms: int,
                                  is_error: bool = False):
        """更新查询性能指标"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO graphql_performance (
                    schema_id, query_hash, operation_name,
                    avg_execution_time_ms, min_execution_time_ms, max_execution_time_ms,
                    call_count, error_count, last_executed_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (schema_id, query_hash)
                DO UPDATE SET
                    avg_execution_time_ms = (
                        (graphql_performance.avg_execution_time_ms * graphql_performance.call_count + %s)
                        / (graphql_performance.call_count + 1)
                    ),
                    min_execution_time_ms = LEAST(graphql_performance.min_execution_time_ms, %s),
                    max_execution_time_ms = GREATEST(graphql_performance.max_execution_time_ms, %s),
                    call_count = graphql_performance.call_count + 1,
                    error_count = graphql_performance.error_count + %s,
                    last_executed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                schema_id, query_hash, operation_name,
                execution_time_ms, execution_time_ms, execution_time_ms,
                1 if is_error else 0,
                execution_time_ms, execution_time_ms, execution_time_ms,
                1 if is_error else 0
            ))
            self.conn.commit()
```

### 6.2 GraphQL数据分析查询

**分析查询示例**：

```python
def analyze_schema_usage(db_config: Dict):
    """分析Schema使用情况"""
    store = GraphQLDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询最常用的类型
        cur.execute("""
            SELECT
                gt.type_name,
                gt.type_kind,
                COUNT(DISTINCT gf.id) as field_count,
                COUNT(DISTINCT gq.id) as query_count
            FROM graphql_types gt
            LEFT JOIN graphql_fields gf ON gt.id = gf.type_id
            LEFT JOIN graphql_queries gq ON gt.schema_id = gq.schema_id
            WHERE gt.schema_id = %s
            GROUP BY gt.id, gt.type_name, gt.type_kind
            ORDER BY query_count DESC, field_count DESC
            LIMIT 10
        """, (schema_id,))

        results = cur.fetchall()
        print("最常用的类型:")
        for row in results:
            print(f"  {row[0]} ({row[1]}): {row[2]} 字段, {row[3]} 查询")

        # 查询性能最差的查询
        cur.execute("""
            SELECT
                operation_name,
                query_hash,
                avg_execution_time_ms,
                call_count,
                error_count
            FROM graphql_performance
            WHERE schema_id = %s
            ORDER BY avg_execution_time_ms DESC
            LIMIT 10
        """, (schema_id,))

        results = cur.fetchall()
        print("\n性能最差的查询:")
        for row in results:
            print(f"  {row[0]}: 平均 {row[2]}ms, {row[3]} 次调用, {row[4]} 次错误")
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

**相关文档**：
- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例
