# Avro Schema转换体系

## 📑 目录

- [Avro Schema转换体系](#avro-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. Avro到JSON Schema转换](#2-avro到json-schema转换)
  - [3. Avro到Protocol Buffers转换](#3-avro到protocol-buffers转换)
  - [4. Avro到Parquet转换](#4-avro到parquet转换)
  - [5. 转换验证](#5-转换验证)
  - [6. Avro数据存储与分析](#6-avro数据存储与分析)
    - [6.1 PostgreSQL Avro数据存储](#61-postgresql-avro数据存储)
    - [6.2 Avro数据分析查询](#62-avro数据分析查询)

---

## 1. 转换体系概述

Avro Schema转换体系支持Avro Schema与其他数据格式之间的转换。

### 1.1 转换目标

1. **Avro到JSON Schema转换**：Avro Schema转换为JSON Schema
2. **Avro到Protocol Buffers转换**：Avro Schema转换为Protocol Buffers Schema
3. **Avro到Parquet转换**：Avro数据转换为Parquet格式
4. **Schema到数据库转换**：Avro Schema定义到PostgreSQL存储

---

## 2. Avro到JSON Schema转换

**转换规则**：
- Avro类型 → JSON Schema类型
- Avro记录 → JSON Schema对象
- Avro数组 → JSON Schema数组

**转换示例**：

```python
import json
from avro.schema import parse

def avro_to_json_schema(avro_schema_str: str) -> dict:
    """将Avro Schema转换为JSON Schema"""
    avro_schema = parse(avro_schema_str)

    if avro_schema.type == "record":
        return {
            "type": "object",
            "properties": {
                field.name: convert_avro_type_to_json_schema(field.type)
                for field in avro_schema.fields
            },
            "required": [
                field.name for field in avro_schema.fields
                if not isinstance(field.type, (list, type(None))) or None not in field.type
            ]
        }
    # 其他类型转换...
    return {}
```

---

## 3. Avro到Protocol Buffers转换

**转换规则**：
- Avro记录 → Protocol Buffers消息
- Avro字段 → Protocol Buffers字段
- Avro类型 → Protocol Buffers类型

---

## 4. Avro到Parquet转换

**转换规则**：
- Avro记录 → Parquet行组
- Avro字段 → Parquet列
- Avro类型 → Parquet类型

---

## 5. 转换验证

验证转换的Schema完整性、类型一致性和数据等价性。

---

## 6. Avro数据存储与分析

### 6.1 PostgreSQL Avro数据存储

**Avro数据存储方案**：

```python
import psycopg2
import json
from avro.schema import parse
from avro.io import DatumReader, BinaryDecoder
import io

class AvroDataStore:
    """Avro数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Avro数据存储表"""
        with self.conn.cursor() as cur:
            # Schema定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS avro_schemas (
                    id SERIAL PRIMARY KEY,
                    schema_name VARCHAR(255) NOT NULL UNIQUE,
                    schema_definition JSONB NOT NULL,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 数据实例表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS avro_instances (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES avro_schemas(id),
                    instance_data JSONB NOT NULL,
                    size_bytes INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Schema演进表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS avro_schema_evolution (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES avro_schemas(id),
                    from_version INTEGER NOT NULL,
                    to_version INTEGER NOT NULL,
                    compatibility_type VARCHAR(50) NOT NULL,
                    evolution_details JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def store_schema(self, schema_name: str, schema_definition: str, version: int = 1):
        """存储Avro Schema定义"""
        schema_json = json.loads(schema_definition) if isinstance(schema_definition, str) else schema_definition

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO avro_schemas (schema_name, schema_definition, version)
                VALUES (%s, %s, %s)
                ON CONFLICT (schema_name)
                DO UPDATE SET
                    schema_definition = EXCLUDED.schema_definition,
                    version = EXCLUDED.version
                RETURNING id
            """, (schema_name, json.dumps(schema_json), version))

            return cur.fetchone()[0]

    def store_instance(self, schema_id: int, avro_data: bytes):
        """存储Avro数据实例"""
        # 读取Schema
        with self.conn.cursor() as cur:
            cur.execute("SELECT schema_definition FROM avro_schemas WHERE id = %s", (schema_id,))
            schema_json = cur.fetchone()[0]

        schema = parse(json.dumps(schema_json))
        reader = DatumReader(schema)
        decoder = BinaryDecoder(io.BytesIO(avro_data))
        instance_data = reader.read(decoder)

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO avro_instances (schema_id, instance_data, size_bytes)
                VALUES (%s, %s, %s)
            """, (schema_id, json.dumps(instance_data), len(avro_data)))

            self.conn.commit()
```

### 6.2 Avro数据分析查询

**分析查询示例**：

```python
def analyze_avro_usage(db_config: Dict):
    """分析Avro使用情况"""
    store = AvroDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询Schema使用统计
        cur.execute("""
            SELECT
                as_schema.schema_name,
                COUNT(ai.id) as instance_count,
                AVG(ai.size_bytes) as avg_size,
                SUM(ai.size_bytes) as total_size
            FROM avro_schemas as_schema
            LEFT JOIN avro_instances ai ON as_schema.id = ai.schema_id
            GROUP BY as_schema.id, as_schema.schema_name
            ORDER BY instance_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
