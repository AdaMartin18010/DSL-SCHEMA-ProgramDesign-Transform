# Protocol Buffers Schema转换体系

## 📑 目录

- [Protocol Buffers Schema转换体系](#protocol-buffers-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. Protocol Buffers到JSON转换](#2-protocol-buffers到json转换)
  - [3. Protocol Buffers到Avro转换](#3-protocol-buffers到avro转换)
  - [4. Protocol Buffers到OpenAPI转换](#4-protocol-buffers到openapi转换)
  - [5. 转换验证](#5-转换验证)
  - [6. Protocol Buffers数据存储与分析](#6-protocol-buffers数据存储与分析)
    - [6.1 PostgreSQL Protocol Buffers数据存储](#61-postgresql-protocol-buffers数据存储)
    - [6.2 Protocol Buffers数据分析查询](#62-protocol-buffers数据分析查询)

---

## 1. 转换体系概述

Protocol Buffers Schema转换体系支持Protocol Buffers与其他数据格式之间的转换。

### 1.1 转换目标

1. **Protocol Buffers到JSON转换**：Protocol Buffers消息转换为JSON
2. **Protocol Buffers到Avro转换**：Protocol Buffers Schema转换为Avro Schema
3. **Protocol Buffers到OpenAPI转换**：Protocol Buffers服务转换为OpenAPI规范
4. **Schema到数据库转换**：Protocol Buffers Schema定义到PostgreSQL存储

---

## 2. Protocol Buffers到JSON转换

**转换规则**：
- Protocol Buffers消息 → JSON对象
- Protocol Buffers字段 → JSON属性
- Protocol Buffers类型 → JSON类型

**转换示例**：

```python
from google.protobuf.json_format import MessageToJson, Parse

def protobuf_to_json(message):
    """将Protocol Buffers消息转换为JSON"""
    return MessageToJson(message)

def json_to_protobuf(json_str, message_class):
    """将JSON转换为Protocol Buffers消息"""
    message = message_class()
    Parse(json_str, message)
    return message
```

---

## 3. Protocol Buffers到Avro转换

**转换规则**：
- Protocol Buffers消息 → Avro记录
- Protocol Buffers字段 → Avro字段
- Protocol Buffers类型 → Avro类型

---

## 4. Protocol Buffers到OpenAPI转换

**转换规则**：
- Protocol Buffers服务 → OpenAPI路径
- Protocol Buffers消息 → OpenAPI Schema

---

## 5. 转换验证

验证转换的消息完整性、类型一致性和数据等价性。

---

## 6. Protocol Buffers数据存储与分析

### 6.1 PostgreSQL Protocol Buffers数据存储

**Protocol Buffers数据存储方案**：

```python
import psycopg2
import json
from google.protobuf.json_format import MessageToJson

class ProtobufDataStore:
    """Protocol Buffers数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Protocol Buffers数据存储表"""
        with self.conn.cursor() as cur:
            # Schema定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS protobuf_schemas (
                    id SERIAL PRIMARY KEY,
                    schema_name VARCHAR(255) NOT NULL UNIQUE,
                    schema_definition TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 消息定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS protobuf_messages (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES protobuf_schemas(id),
                    message_name VARCHAR(255) NOT NULL,
                    message_definition JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(schema_id, message_name)
                )
            """)

            # 消息实例表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS protobuf_instances (
                    id SERIAL PRIMARY KEY,
                    message_id INTEGER REFERENCES protobuf_messages(id),
                    instance_data JSONB NOT NULL,
                    size_bytes INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def store_schema(self, schema_name: str, schema_definition: str):
        """存储Protocol Buffers Schema定义"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO protobuf_schemas (schema_name, schema_definition)
                VALUES (%s, %s)
                ON CONFLICT (schema_name)
                DO UPDATE SET schema_definition = EXCLUDED.schema_definition
                RETURNING id
            """, (schema_name, schema_definition))

            return cur.fetchone()[0]

    def store_message_instance(self, message_id: int, message_instance):
        """存储Protocol Buffers消息实例"""
        json_data = MessageToJson(message_instance)
        size_bytes = len(message_instance.SerializeToString())

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO protobuf_instances (message_id, instance_data, size_bytes)
                VALUES (%s, %s, %s)
            """, (message_id, json.dumps(json.loads(json_data)), size_bytes))

            self.conn.commit()
```

### 6.2 Protocol Buffers数据分析查询

**分析查询示例**：

```python
def analyze_protobuf_usage(db_config: Dict):
    """分析Protocol Buffers使用情况"""
    store = ProtobufDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询消息大小统计
        cur.execute("""
            SELECT
                pm.message_name,
                COUNT(pi.id) as instance_count,
                AVG(pi.size_bytes) as avg_size,
                MIN(pi.size_bytes) as min_size,
                MAX(pi.size_bytes) as max_size
            FROM protobuf_messages pm
            LEFT JOIN protobuf_instances pi ON pm.id = pi.message_id
            GROUP BY pm.id, pm.message_name
            ORDER BY instance_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
