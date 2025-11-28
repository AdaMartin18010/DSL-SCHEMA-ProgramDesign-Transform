# JSON Schema转换体系

## 📑 目录

- [JSON Schema转换体系](#json-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. JSON Schema到GraphQL转换](#2-json-schema到graphql转换)
  - [3. JSON Schema到OpenAPI转换](#3-json-schema到openapi转换)
  - [4. JSON Schema到Avro转换](#4-json-schema到avro转换)
  - [5. 转换验证](#5-转换验证)
  - [6. JSON Schema数据存储与分析](#6-json-schema数据存储与分析)
    - [6.1 PostgreSQL JSON Schema数据存储](#61-postgresql-json-schema数据存储)
    - [6.2 JSON Schema数据分析查询](#62-json-schema数据分析查询)

---

## 1. 转换体系概述

JSON Schema转换体系支持JSON Schema与其他Schema格式之间的转换。

### 1.1 转换目标

1. **JSON Schema到GraphQL转换**：JSON Schema转换为GraphQL类型
2. **JSON Schema到OpenAPI转换**：JSON Schema转换为OpenAPI Schema
3. **JSON Schema到Avro转换**：JSON Schema转换为Avro Schema
4. **Schema到数据库转换**：JSON Schema定义到PostgreSQL存储

---

## 2. JSON Schema到GraphQL转换

**转换规则**：
- JSON Schema对象 → GraphQL对象类型
- JSON Schema数组 → GraphQL列表类型
- JSON Schema类型 → GraphQL标量类型

**转换示例**：

```python
def json_schema_to_graphql(json_schema: dict) -> str:
    """将JSON Schema转换为GraphQL Schema"""
    graphql_types = []

    if json_schema.get("type") == "object":
        type_name = json_schema.get("title", "Object")
        fields = []

        for prop_name, prop_schema in json_schema.get("properties", {}).items():
            field_type = convert_json_type_to_graphql(prop_schema)
            required = prop_name in json_schema.get("required", [])
            fields.append(f"  {prop_name}: {field_type}{'!' if required else ''}")

        graphql_type = f"type {type_name} {{\n" + "\n".join(fields) + "\n}"
        graphql_types.append(graphql_type)

    return "\n\n".join(graphql_types)

def convert_json_type_to_graphql(json_schema: dict) -> str:
    """转换JSON类型为GraphQL类型"""
    json_type = json_schema.get("type")

    type_map = {
        "string": "String",
        "number": "Float",
        "integer": "Int",
        "boolean": "Boolean",
        "array": f"[{convert_json_type_to_graphql(json_schema.get('items', {}))}]",
        "object": "Object"
    }

    return type_map.get(json_type, "String")
```

---

## 3. JSON Schema到OpenAPI转换

**转换规则**：
- JSON Schema → OpenAPI Schema对象
- JSON Schema引用 → OpenAPI引用

**转换示例**：

```python
def json_schema_to_openapi(json_schema: dict) -> dict:
    """将JSON Schema转换为OpenAPI Schema"""
    openapi_schema = {}

    if "type" in json_schema:
        openapi_schema["type"] = json_schema["type"]

    if "properties" in json_schema:
        openapi_schema["properties"] = {
            prop_name: json_schema_to_openapi(prop_schema)
            for prop_name, prop_schema in json_schema["properties"].items()
        }

    if "required" in json_schema:
        openapi_schema["required"] = json_schema["required"]

    return openapi_schema
```

---

## 4. JSON Schema到Avro转换

**转换规则**：
- JSON Schema对象 → Avro记录
- JSON Schema类型 → Avro类型

---

## 5. 转换验证

验证转换的Schema完整性、类型一致性和验证规则等价性。

---

## 6. JSON Schema数据存储与分析

### 6.1 PostgreSQL JSON Schema数据存储

**JSON Schema数据存储方案**：

```python
import psycopg2
import json

class JSONSchemaDataStore:
    """JSON Schema数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建JSON Schema数据存储表"""
        with self.conn.cursor() as cur:
            # Schema定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS json_schemas (
                    id SERIAL PRIMARY KEY,
                    schema_name VARCHAR(255) NOT NULL UNIQUE,
                    schema_definition JSONB NOT NULL,
                    $id VARCHAR(255),
                    $schema VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 验证结果表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS json_schema_validations (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES json_schemas(id),
                    data_instance JSONB NOT NULL,
                    is_valid BOOLEAN NOT NULL,
                    errors JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def store_schema(self, schema_name: str, schema_definition: dict):
        """存储JSON Schema定义"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO json_schemas (schema_name, schema_definition, $id, $schema)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (schema_name)
                DO UPDATE SET schema_definition = EXCLUDED.schema_definition
                RETURNING id
            """, (
                schema_name,
                json.dumps(schema_definition),
                schema_definition.get("$id"),
                schema_definition.get("$schema")
            ))

            return cur.fetchone()[0]

    def log_validation(self, schema_id: int, data_instance: dict, is_valid: bool, errors: list = None):
        """记录验证结果"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO json_schema_validations (schema_id, data_instance, is_valid, errors)
                VALUES (%s, %s, %s, %s)
            """, (schema_id, json.dumps(data_instance), is_valid, json.dumps(errors) if errors else None))

            self.conn.commit()
```

### 6.2 JSON Schema数据分析查询

**分析查询示例**：

```python
def analyze_json_schema_usage(db_config: Dict):
    """分析JSON Schema使用情况"""
    store = JSONSchemaDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询验证统计
        cur.execute("""
            SELECT
                js.schema_name,
                COUNT(jsv.id) as validation_count,
                SUM(CASE WHEN jsv.is_valid THEN 1 ELSE 0 END) as valid_count,
                SUM(CASE WHEN NOT jsv.is_valid THEN 1 ELSE 0 END) as invalid_count
            FROM json_schemas js
            LEFT JOIN json_schema_validations jsv ON js.id = jsv.schema_id
            GROUP BY js.id, js.schema_name
            ORDER BY validation_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
