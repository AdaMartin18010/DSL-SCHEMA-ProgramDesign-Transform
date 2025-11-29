# DSL转换工具

## 📑 目录

- [DSL转换工具](#dsl转换工具)
  - [📑 目录](#-目录)
  - [1. 编译器前端工具](#1-编译器前端工具)
    - [1.1 ANTLR](#11-antlr)
    - [1.2 Yacc/Bison](#12-yaccbison)
  - [2. 转换框架](#2-转换框架)
    - [2.1 Xtext](#21-xtext)
    - [2.2 MPS](#22-mps)
  - [3. 代码生成工具](#3-代码生成工具)
    - [3.1 Template Engine](#31-template-engine)
    - [3.2 Code Generator](#32-code-generator)
  - [4. 工具对比](#4-工具对比)
  - [6. 数据库存储与分析](#6-数据库存储与分析)
    - [6.1 PostgreSQL数据存储](#61-postgresql数据存储)
    - [6.2 数据分析查询示例](#62-数据分析查询示例)

---

## 1. 编译器前端工具

### 1.1 ANTLR

**功能**：

- 解析器生成器
- 支持多种目标语言
- 强大的语法定义能力

**应用场景**：

- DSL解析器开发
- 语法分析器生成

### 1.2 Yacc/Bison

**功能**：

- 语法分析器生成器
- LALR(1)解析算法
- C/C++代码生成

**应用场景**：

- 编译器开发
- 语法分析

---

## 2. 转换框架

### 2.1 Xtext

**功能**：

- Eclipse DSL框架
- 完整的IDE支持
- 代码生成支持

**应用场景**：

- Eclipse平台DSL开发
- 企业级DSL开发

### 2.2 MPS

**功能**：

- JetBrains Meta Programming System
- 项目ional编辑
- 多语言支持

**应用场景**：

- 复杂DSL开发
- 多语言集成

---

## 3. 代码生成工具

### 3.1 Template Engine

**功能**：

- 模板引擎（Jinja2、Handlebars）
- 支持变量替换
- 支持条件逻辑

**应用场景**：

- 代码生成
- 文档生成

### 3.2 Code Generator

**功能**：

- 代码生成器
- 支持多语言
- 支持自定义模板

**应用场景**：

- API客户端生成
- 服务器端代码生成

---

## 4. 工具对比

| 工具 | 类型 | 优势 | 适用场景 |
|------|------|------|---------|
| **ANTLR** | 解析器生成器 | 功能强大，支持多语言 | DSL解析器开发 |
| **Xtext** | DSL框架 | IDE支持完善 | Eclipse平台DSL |
| **MPS** | DSL开发环境 | 项目ional编辑 | 复杂DSL开发 |
| **Jinja2** | 模板引擎 | 简单易用 | 代码生成 |

---

## 6. 数据库存储与分析

### 6.1 PostgreSQL数据存储

**表结构设计**：

```sql
-- DSL转换工具表
CREATE TABLE dsl_transformation_tools (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(200) UNIQUE NOT NULL,
    tool_type VARCHAR(50) NOT NULL,  -- Parser, Framework, Generator
    supported_languages TEXT[],
    tool_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 转换工具使用记录表
CREATE TABLE tool_usage_records (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER REFERENCES dsl_transformation_tools(id),
    project_name VARCHAR(200),
    usage_context VARCHAR(100),
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_tools_type ON dsl_transformation_tools(tool_type);
CREATE INDEX idx_tool_usage_tool_id ON tool_usage_records(tool_id);
```

**Python存储实现**：

```python
import psycopg2
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DSLTransformationToolStorage:
    """DSL转换工具数据存储类"""

    def __init__(self, db_config: Dict[str, Any]):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建表结构"""
        # DSL转换工具表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS dsl_transformation_tools (
                id SERIAL PRIMARY KEY,
                tool_name VARCHAR(200) UNIQUE NOT NULL,
                tool_type VARCHAR(50) NOT NULL,
                supported_languages TEXT[],
                tool_metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 转换工具使用记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS tool_usage_records (
                id SERIAL PRIMARY KEY,
                tool_id INTEGER REFERENCES dsl_transformation_tools(id),
                project_name VARCHAR(200),
                usage_context VARCHAR(100),
                performance_metrics JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_tools_type
            ON dsl_transformation_tools(tool_type)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_usage_tool_id
            ON tool_usage_records(tool_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_usage_created_at
            ON tool_usage_records(created_at DESC)
        """)

        self.conn.commit()

    def store_tool(self, tool_name: str, tool_type: str,
                   supported_languages: List[str],
                   metadata: Optional[Dict] = None) -> int:
        """存储转换工具信息"""
        try:
            self.cur.execute("""
                INSERT INTO dsl_transformation_tools
                (tool_name, tool_type, supported_languages, tool_metadata)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (tool_name) DO UPDATE
                SET tool_type = EXCLUDED.tool_type,
                    supported_languages = EXCLUDED.supported_languages,
                    tool_metadata = EXCLUDED.tool_metadata,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (tool_name, tool_type, supported_languages,
                  json.dumps(metadata) if metadata else None))
            tool_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored tool: {tool_name} (ID: {tool_id})")
            return tool_id
        except Exception as e:
            logger.error(f"Failed to store tool: {e}")
            self.conn.rollback()
            raise

    def store_usage_record(self, tool_id: int, project_name: str,
                          usage_context: str, performance_metrics: Optional[Dict] = None) -> int:
        """存储工具使用记录"""
        try:
            self.cur.execute("""
                INSERT INTO tool_usage_records
                (tool_id, project_name, usage_context, performance_metrics)
                VALUES (%s, %s, %s, %s::jsonb)
                RETURNING id
            """, (tool_id, project_name, usage_context,
                  json.dumps(performance_metrics) if performance_metrics else None))
            record_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored usage record: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"Failed to store usage record: {e}")
            self.conn.rollback()
            raise

    def get_tool_statistics(self) -> Dict:
        """获取工具统计信息"""
        try:
            self.cur.execute("""
                SELECT
                    tool_type,
                    COUNT(*) as tool_count,
                    COUNT(DISTINCT ur.id) as usage_count
                FROM dsl_transformation_tools t
                LEFT JOIN tool_usage_records ur ON t.id = ur.tool_id
                GROUP BY tool_type
                ORDER BY tool_count DESC
            """)
            results = []
            for row in self.cur.fetchall():
                results.append({
                    'tool_type': row[0],
                    'tool_count': row[1],
                    'usage_count': row[2]
                })
            return {'by_type': results}
        except Exception as e:
            logger.error(f"Failed to get tool statistics: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 数据分析查询示例

**查询工具使用统计**：

```python
# 按工具类型统计
storage.cur.execute("""
    SELECT tool_type, COUNT(*) as count
    FROM dsl_transformation_tools
    GROUP BY tool_type
    ORDER BY count DESC
""")
```

**查询工具使用频率**：

```python
# 查询最常用的工具
storage.cur.execute("""
    SELECT
        t.tool_name,
        t.tool_type,
        COUNT(ur.id) as usage_count
    FROM dsl_transformation_tools t
    LEFT JOIN tool_usage_records ur ON t.id = ur.tool_id
    GROUP BY t.id, t.tool_name, t.tool_type
    ORDER BY usage_count DESC
    LIMIT 10
""")
```

**查询工具性能指标**：

```python
# 查询工具性能指标
storage.cur.execute("""
    SELECT
        t.tool_name,
        AVG((ur.performance_metrics->>'execution_time_ms')::numeric) as avg_execution_time,
        AVG((ur.performance_metrics->>'memory_usage_mb')::numeric) as avg_memory_usage
    FROM dsl_transformation_tools t
    JOIN tool_usage_records ur ON t.id = ur.tool_id
    WHERE ur.performance_metrics IS NOT NULL
    GROUP BY t.id, t.tool_name
    ORDER BY avg_execution_time
""")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 转换算法
- `03_Standards.md` - 转换规则
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
