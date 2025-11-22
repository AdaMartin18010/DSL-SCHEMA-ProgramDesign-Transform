# 数据库Schema转换体系

## 📑 目录

- [数据库Schema转换体系](#数据库schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Schema到SQL DDL转换](#2-schema到sql-ddl转换)
  - [3. SQL DDL到Schema转换](#3-sql-ddl到schema转换)
  - [4. 跨数据库转换](#4-跨数据库转换)
    - [4.1 SQLite到PostgreSQL转换](#41-sqlite到postgresql转换)
    - [4.2 PostgreSQL到SQLite转换](#42-postgresql到sqlite转换)
  - [5. Schema版本管理](#5-schema版本管理)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)
  - [8. 数据库Schema数据存储](#8-数据库schema数据存储)

---

## 1. 转换体系概述

数据库Schema转换体系支持Schema定义与SQL DDL之间的双向转换，
以及不同数据库之间的Schema转换。

### 1.1 转换目标

1. **Schema到DDL**：从Schema定义生成SQL DDL
2. **DDL到Schema**：从SQL DDL解析Schema定义
3. **跨数据库转换**：SQLite ↔ PostgreSQL

---

## 2. Schema到SQL DDL转换

**转换规则**：

- Schema表定义 → CREATE TABLE语句
- Schema列定义 → 列定义
- Schema约束 → CONSTRAINT子句
- Schema索引 → CREATE INDEX语句

**转换示例**：

```python
def schema_to_ddl(schema: Database_Schema) -> str:
    """将Schema转换为SQL DDL"""
    ddl_statements = []

    for table in schema.tables:
        ddl = f"CREATE TABLE {table.name} (\n"
        columns = []
        for col in table.columns:
            col_def = f"  {col.name} {col.data_type}"
            if not col.nullable:
                col_def += " NOT NULL"
            if col.default_value:
                col_def += f" DEFAULT {col.default_value}"
            columns.append(col_def)
        ddl += ",\n".join(columns)
        ddl += "\n);"
        ddl_statements.append(ddl)

    return "\n\n".join(ddl_statements)
```

---

## 3. SQL DDL到Schema转换

**转换规则**：

- CREATE TABLE语句 → Schema表定义
- 列定义 → Schema列定义
- CONSTRAINT子句 → Schema约束
- CREATE INDEX语句 → Schema索引

---

## 4. 跨数据库转换

### 4.1 SQLite到PostgreSQL转换

**转换规则**：

- SQLite INTEGER → PostgreSQL INTEGER/BIGINT
- SQLite TEXT → PostgreSQL TEXT/VARCHAR
- SQLite BLOB → PostgreSQL BYTEA
- SQLite约束 → PostgreSQL对应约束

### 4.2 PostgreSQL到SQLite转换

**转换规则**：

- PostgreSQL JSONB → SQLite TEXT（JSON存储）
- PostgreSQL数组 → SQLite TEXT（JSON数组）
- PostgreSQL特定类型 → SQLite兼容类型

---

## 5. Schema版本管理

支持Schema版本管理和迁移脚本生成。

---

## 6. 转换工具

- **SQLAlchemy**：Python ORM，支持多数据库
- **Liquibase**：数据库版本管理工具
- **Flyway**：数据库迁移工具

---

## 7. 转换验证

验证转换的语法正确性、语义等价性和完整性。

---

## 8. 数据库Schema数据存储

**Schema元数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class DatabaseSchemaStorage:
    """数据库Schema元数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建Schema元数据表"""
        # Schema定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_definitions (
                id SERIAL PRIMARY KEY,
                schema_name VARCHAR(200) UNIQUE NOT NULL,
                database_type VARCHAR(50) NOT NULL,
                version VARCHAR(50),
                definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 表定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS table_definitions (
                id SERIAL PRIMARY KEY,
                schema_id INTEGER NOT NULL,
                table_name VARCHAR(200) NOT NULL,
                definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schema_id) REFERENCES schema_definitions(id),
                UNIQUE(schema_id, table_name)
            )
        """)

        # 列定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS column_definitions (
                id SERIAL PRIMARY KEY,
                table_id INTEGER NOT NULL,
                column_name VARCHAR(200) NOT NULL,
                data_type VARCHAR(100) NOT NULL,
                nullable BOOLEAN DEFAULT TRUE,
                default_value TEXT,
                definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES table_definitions(id),
                UNIQUE(table_id, column_name)
            )
        """)

        # 索引定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS index_definitions (
                id SERIAL PRIMARY KEY,
                table_id INTEGER NOT NULL,
                index_name VARCHAR(200) NOT NULL,
                columns JSONB NOT NULL,
                index_type VARCHAR(50),
                unique BOOLEAN DEFAULT FALSE,
                definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES table_definitions(id),
                UNIQUE(table_id, index_name)
            )
        """)

        self.conn.commit()

    def store_schema(self, schema_name: str, database_type: str,
                    definition: Dict, version: str = None):
        """存储Schema定义"""
        self.cur.execute("""
            INSERT INTO schema_definitions
            (schema_name, database_type, version, definition)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (schema_name) DO UPDATE
            SET database_type = EXCLUDED.database_type,
                version = EXCLUDED.version,
                definition = EXCLUDED.definition,
                updated_at = CURRENT_TIMESTAMP
        """, (schema_name, database_type, version, json.dumps(definition)))
        self.conn.commit()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
