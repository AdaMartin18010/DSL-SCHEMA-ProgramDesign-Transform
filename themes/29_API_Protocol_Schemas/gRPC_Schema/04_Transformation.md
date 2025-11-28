# gRPC Schema转换体系

## 📑 目录

- [gRPC Schema转换体系](#grpc-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. gRPC到OpenAPI转换](#2-grpc到openapi转换)
  - [3. gRPC到GraphQL转换](#3-grpc到graphql转换)
  - [4. Protocol Buffers到JSON转换](#4-protocol-buffers到json转换)
  - [5. 转换验证](#5-转换验证)
  - [6. gRPC数据存储与分析](#6-grpc数据存储与分析)
    - [6.1 PostgreSQL gRPC数据存储](#61-postgresql-grpc数据存储)
    - [6.2 gRPC数据分析查询](#62-grpc数据分析查询)

---

## 1. 转换体系概述

gRPC Schema转换体系支持gRPC服务与其他API格式之间的转换。

### 1.1 转换目标

1. **gRPC到OpenAPI转换**：gRPC服务转换为OpenAPI规范
2. **gRPC到GraphQL转换**：gRPC服务转换为GraphQL Schema
3. **Protocol Buffers到JSON转换**：Protocol Buffers消息转换为JSON
4. **Schema到数据库转换**：gRPC Schema定义到PostgreSQL存储

---

## 2. gRPC到OpenAPI转换

**转换规则**：
- gRPC服务 → OpenAPI路径
- gRPC方法 → OpenAPI操作
- Protocol Buffers消息 → OpenAPI Schema

**转换示例**：

```python
def grpc_to_openapi(proto_file: str) -> dict:
    """将gRPC Protocol Buffers定义转换为OpenAPI规范"""
    from google.protobuf import descriptor_pb2

    # 解析Protocol Buffers文件
    # 转换为OpenAPI规范
    return openapi_spec
```

---

## 3. gRPC到GraphQL转换

**转换规则**：
- gRPC服务 → GraphQL类型
- gRPC方法 → GraphQL查询/变更
- Protocol Buffers消息 → GraphQL类型

---

## 4. Protocol Buffers到JSON转换

**转换规则**：
- Protocol Buffers消息 → JSON对象
- Protocol Buffers字段 → JSON属性

---

## 5. 转换验证

验证转换的服务完整性、类型一致性和功能等价性。

---

## 6. gRPC数据存储与分析

### 6.1 PostgreSQL gRPC数据存储

**gRPC数据存储方案**：

```python
import psycopg2
import json
from datetime import datetime

class GRPCDataStore:
    """gRPC数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建gRPC数据存储表"""
        with self.conn.cursor() as cur:
            # 服务定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS grpc_services (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(255) NOT NULL UNIQUE,
                    service_definition TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # RPC方法表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS grpc_methods (
                    id SERIAL PRIMARY KEY,
                    service_id INTEGER REFERENCES grpc_services(id),
                    method_name VARCHAR(255) NOT NULL,
                    request_type VARCHAR(255) NOT NULL,
                    response_type VARCHAR(255) NOT NULL,
                    method_type VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(service_id, method_name)
                )
            """)

            # 调用日志表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS grpc_calls (
                    id SERIAL PRIMARY KEY,
                    service_id INTEGER REFERENCES grpc_services(id),
                    method_id INTEGER REFERENCES grpc_methods(id),
                    request_data JSONB,
                    response_data JSONB,
                    execution_time_ms INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
```

### 6.2 gRPC数据分析查询

**分析查询示例**：

```python
def analyze_grpc_usage(db_config: Dict):
    """分析gRPC使用情况"""
    store = GRPCDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询最常用的方法
        cur.execute("""
            SELECT
                gm.method_name,
                COUNT(gc.id) as call_count,
                AVG(gc.execution_time_ms) as avg_time
            FROM grpc_methods gm
            LEFT JOIN grpc_calls gc ON gm.id = gc.method_id
            GROUP BY gm.id, gm.method_name
            ORDER BY call_count DESC
            LIMIT 10
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
