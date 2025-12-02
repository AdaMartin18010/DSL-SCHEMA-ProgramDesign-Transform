# AsyncAPI Schema转换体系

## 📑 目录

- [AsyncAPI Schema转换体系](#asyncapi-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. AsyncAPI到OpenAPI转换](#2-asyncapi到openapi转换)
  - [3. AsyncAPI到GraphQL转换](#3-asyncapi到graphql转换)
  - [4. AsyncAPI到gRPC转换](#4-asyncapi到grpc转换)
  - [5. 转换验证](#5-转换验证)
  - [6. AsyncAPI数据存储与分析](#6-asyncapi数据存储与分析)
    - [6.1 PostgreSQL AsyncAPI数据存储](#61-postgresql-asyncapi数据存储)
    - [6.2 AsyncAPI数据分析查询](#62-asyncapi数据分析查询)

---

## 1. 转换体系概述

AsyncAPI Schema转换体系支持AsyncAPI与其他API格式之间的转换。

### 1.1 转换目标

1. **AsyncAPI到OpenAPI转换**：AsyncAPI规范转换为OpenAPI规范
2. **AsyncAPI到GraphQL转换**：AsyncAPI消息转换为GraphQL订阅
3. **AsyncAPI到gRPC转换**：AsyncAPI服务转换为gRPC服务
4. **Schema到数据库转换**：AsyncAPI Schema定义到PostgreSQL存储

---

## 2. AsyncAPI到OpenAPI转换

**转换规则**：

- AsyncAPI通道 → OpenAPI路径
- AsyncAPI操作 → OpenAPI操作
- AsyncAPI消息 → OpenAPI Schema

**转换示例**：

```python
def asyncapi_to_openapi(asyncapi_spec: dict) -> dict:
    """将AsyncAPI规范转换为OpenAPI规范"""
    openapi_spec = {
        "openapi": "3.0.0",
        "info": asyncapi_spec.get("info", {}),
        "servers": convert_servers(asyncapi_spec.get("servers", {})),
        "paths": convert_channels_to_paths(asyncapi_spec.get("channels", {})),
        "components": {
            "schemas": convert_messages_to_schemas(asyncapi_spec.get("components", {}).get("messages", {}))
        }
    }

    return openapi_spec

def convert_channels_to_paths(channels: dict) -> dict:
    """将AsyncAPI通道转换为OpenAPI路径"""
    paths = {}

    for channel_name, channel in channels.items():
        path = f"/{channel_name.replace('.', '/')}"
        paths[path] = {}

        if channel.get("publish"):
            paths[path]["post"] = convert_operation_to_openapi(channel["publish"])

        if channel.get("subscribe"):
            paths[path]["get"] = convert_operation_to_openapi(channel["subscribe"])

    return paths
```

---

## 3. AsyncAPI到GraphQL转换

**转换规则**：

- AsyncAPI通道 → GraphQL订阅
- AsyncAPI消息 → GraphQL类型
- AsyncAPI操作 → GraphQL订阅字段

---

## 4. AsyncAPI到gRPC转换

**转换规则**：

- AsyncAPI通道 → gRPC服务
- AsyncAPI消息 → Protocol Buffers消息
- AsyncAPI操作 → gRPC方法

---

## 5. 转换验证

验证转换的Schema完整性、消息一致性和操作有效性。

---

## 6. AsyncAPI数据存储与分析

### 6.1 PostgreSQL AsyncAPI数据存储

**AsyncAPI数据存储方案**：

```python
import psycopg2
import json
from datetime import datetime

class AsyncAPIDataStore:
    """AsyncAPI数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建AsyncAPI数据存储表"""
        with self.conn.cursor() as cur:
            # Schema定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS asyncapi_schemas (
                    id SERIAL PRIMARY KEY,
                    schema_name VARCHAR(255) NOT NULL UNIQUE,
                    schema_definition JSONB NOT NULL,
                    version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 通道定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS asyncapi_channels (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES asyncapi_schemas(id),
                    channel_name VARCHAR(255) NOT NULL,
                    channel_definition JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(schema_id, channel_name)
                )
            """)

            # 消息实例表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS asyncapi_messages (
                    id SERIAL PRIMARY KEY,
                    channel_id INTEGER REFERENCES asyncapi_channels(id),
                    message_data JSONB NOT NULL,
                    message_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def store_schema(self, schema_name: str, schema_definition: dict, version: str = "1.0.0"):
        """存储AsyncAPI Schema定义"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO asyncapi_schemas (schema_name, schema_definition, version)
                VALUES (%s, %s, %s)
                ON CONFLICT (schema_name)
                DO UPDATE SET
                    schema_definition = EXCLUDED.schema_definition,
                    version = EXCLUDED.version
                RETURNING id
            """, (schema_name, json.dumps(schema_definition), version))

            schema_id = cur.fetchone()[0]

            # 存储通道定义
            for channel_name, channel_def in schema_definition.get("channels", {}).items():
                cur.execute("""
                    INSERT INTO asyncapi_channels (schema_id, channel_name, channel_definition)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (schema_id, channel_name)
                    DO UPDATE SET channel_definition = EXCLUDED.channel_definition
                """, (schema_id, channel_name, json.dumps(channel_def)))

            self.conn.commit()
            return schema_id
```

### 6.2 AsyncAPI数据分析查询

**分析查询示例**：

```python
def analyze_asyncapi_usage(db_config: Dict):
    """分析AsyncAPI使用情况"""
    store = AsyncAPIDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询通道使用统计
        cur.execute("""
            SELECT
                ac.channel_name,
                COUNT(am.id) as message_count,
                COUNT(DISTINCT am.message_type) as message_type_count
            FROM asyncapi_channels ac
            LEFT JOIN asyncapi_messages am ON ac.id = am.channel_id
            GROUP BY ac.id, ac.channel_name
            ORDER BY message_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
