# DSL到代码转换

## 📑 目录

- [DSL到代码转换](#dsl到代码转换)
  - [📑 目录](#-目录)
  - [1. 转换概述](#1-转换概述)
    - [1.1 转换流程](#11-转换流程)
    - [1.2 转换目标](#12-转换目标)
  - [2. 自然语言到DSL转换](#2-自然语言到dsl转换)
    - [2.1 转换工具](#21-转换工具)
    - [2.2 转换示例](#22-转换示例)
  - [3. DSL到代码生成](#3-dsl到代码生成)
    - [3.1 OpenAPI代码生成](#31-openapi代码生成)
    - [3.2 AsyncAPI代码生成](#32-asyncapi代码生成)
    - [3.3 IoTSchema适配](#33-iotschema适配)
  - [4. 转换工具](#4-转换工具)
    - [4.1 OpenAPI Generator](#41-openapi-generator)
    - [4.2 AsyncAPI Generator](#42-asyncapi-generator)
    - [4.3 自定义转换工具](#43-自定义转换工具)
  - [5. 转换实践](#5-转换实践)
    - [5.1 实践流程](#51-实践流程)
    - [5.2 最佳实践](#52-最佳实践)
  - [6. 数据库存储与分析](#6-数据库存储与分析)
    - [6.1 PostgreSQL数据存储](#61-postgresql数据存储)
    - [6.2 数据分析查询示例](#62-数据分析查询示例)

---

## 1. 转换概述

### 1.1 转换流程

```text
自然语言 → DSL → 代码生成 → 验证 → 部署
```

### 1.2 转换目标

1. **自然语言到DSL**：用户描述转换为DSL规范
2. **DSL到代码生成**：DSL规范生成可执行代码
3. **代码验证**：自动验证生成代码的正确性

---

## 2. 自然语言到DSL转换

### 2.1 转换工具

**AI模型**：

- Claude（Anthropic）
- GPT（OpenAI）
- Gemini（Google）

**转换场景**：

- 用户输入："创建一个支持文件上传的API"
- AI输出：自动生成OpenAPI 3.1规范并验证

### 2.2 转换示例

**输入（自然语言）**：

```text
创建一个用户管理API，包含以下功能：
1. 创建用户（POST /users）
2. 查询用户（GET /users/{id}）
3. 更新用户（PUT /users/{id}）
4. 删除用户（DELETE /users/{id}）
```

**输出（OpenAPI DSL）**：

```yaml
openapi: 3.1.0
paths:
  /users:
    post:
      summary: 创建用户
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
  /users/{id}:
    get:
      summary: 查询用户
    put:
      summary: 更新用户
    delete:
      summary: 删除用户
```

---

## 3. DSL到代码生成

### 3.1 OpenAPI代码生成

**OpenAPI Generator**：

- **输入**：OpenAPI规范文件
- **输出**：多语言客户端代码（Python、Node.js、Go、Java等）
- **特性**：支持模板自定义、代码风格配置

**生成示例**：

```bash
openapi-generator generate \
  -i api.yaml \
  -g python \
  -o ./generated/python-client
```

### 3.2 AsyncAPI代码生成

**AsyncAPI Generator**：

- **输入**：AsyncAPI规范文件
- **输出**：Kafka/AMQP代码模板
- **特性**：支持消息处理逻辑生成

**生成示例**：

```bash
asyncapi-generator generate \
  -i asyncapi.yaml \
  -g kafka \
  -o ./generated/kafka-client
```

### 3.3 IoTSchema适配

**AI将设备协议映射到JSON Schema**：

- **输入**：设备协议描述（MQTT主题结构）
- **输出**：IoTSchema的JSON Schema
- **确保**：数据一致性、类型安全

---

## 4. 转换工具

### 4.1 OpenAPI Generator

**功能**：

- 生成多语言客户端代码
- 生成服务器端代码
- 生成API文档

**支持语言**：

- Python、Node.js、Go、Java、C#、PHP等50+种语言

### 4.2 AsyncAPI Generator

**功能**：

- 生成消息队列客户端代码
- 生成消息处理逻辑
- 生成测试代码

**支持协议**：

- Kafka、RabbitMQ、MQTT、AMQP等

### 4.3 自定义转换工具

**开发自定义转换器**：

- 基于模板引擎（Jinja2、Handlebars）
- 支持自定义转换规则
- 支持多格式输出

---

## 5. 转换实践

### 5.1 实践流程

1. **需求分析**：理解用户需求
2. **DSL生成**：AI生成DSL规范
3. **规范验证**：验证DSL规范正确性
4. **代码生成**：生成可执行代码
5. **代码测试**：自动测试生成代码
6. **部署上线**：部署到生产环境

### 5.2 最佳实践

- **迭代优化**：根据反馈不断优化转换规则
- **模板管理**：统一管理代码生成模板
- **版本控制**：对生成的代码进行版本控制
- **自动化测试**：自动测试生成代码的正确性

---

## 6. 数据库存储与分析

### 6.1 PostgreSQL数据存储

**表结构设计**：

```sql
-- 转换任务表
CREATE TABLE dsl_conversion_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(50) NOT NULL,  -- OpenAPI, AsyncAPI, IoTSchema
    target_type VARCHAR(50) NOT NULL,
    source_schema JSONB NOT NULL,
    target_schema JSONB,
    conversion_status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, PROCESSING, COMPLETED, FAILED
    conversion_result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 转换规则表
CREATE TABLE conversion_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    rule_definition JSONB NOT NULL,
    rule_priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 转换历史表
CREATE TABLE conversion_history (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL REFERENCES dsl_conversion_tasks(task_id),
    conversion_step VARCHAR(100) NOT NULL,
    step_input JSONB,
    step_output JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_conversion_tasks_status ON dsl_conversion_tasks(conversion_status);
CREATE INDEX idx_conversion_tasks_source_target ON dsl_conversion_tasks(source_type, target_type);
CREATE INDEX idx_conversion_tasks_created_at ON dsl_conversion_tasks(created_at);
CREATE INDEX idx_conversion_rules_source_target ON conversion_rules(source_type, target_type);
CREATE INDEX idx_conversion_history_task_id ON conversion_history(task_id);
```

**Python存储实现**：

```python
import psycopg2
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DSLConversionStorage:
    """DSL转换数据存储类"""

    def __init__(self, db_config: Dict[str, Any]):
        """初始化数据库连接"""
        self.conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.cur = self.conn.cursor()

    def create_conversion_task(self, task_id: str, source_type: str,
                              target_type: str, source_schema: Dict) -> int:
        """创建转换任务"""
        try:
            self.cur.execute("""
                INSERT INTO dsl_conversion_tasks
                (task_id, source_type, target_type, source_schema)
                VALUES (%s, %s, %s, %s::jsonb)
                RETURNING id
            """, (task_id, source_type, target_type, json.dumps(source_schema)))

            task_db_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Created conversion task: {task_id}")
            return task_db_id
        except psycopg2.IntegrityError as e:
            logger.error(f"Task {task_id} already exists: {e}")
            self.conn.rollback()
            raise ValueError(f"Task {task_id} already exists") from e
        except Exception as e:
            logger.error(f"Failed to create conversion task: {e}")
            self.conn.rollback()
            raise

    def update_conversion_result(self, task_id: str, target_schema: Dict,
                                status: str, error_message: Optional[str] = None):
        """更新转换结果"""
        try:
            self.cur.execute("""
                UPDATE dsl_conversion_tasks
                SET target_schema = %s::jsonb,
                    conversion_status = %s,
                    error_message = %s,
                    completed_at = CASE WHEN %s = 'COMPLETED' THEN CURRENT_TIMESTAMP ELSE NULL END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = %s
            """, (json.dumps(target_schema), status, error_message, status, task_id))

            self.conn.commit()
            logger.info(f"Updated conversion task {task_id} with status {status}")
        except Exception as e:
            logger.error(f"Failed to update conversion result: {e}")
            self.conn.rollback()
            raise

    def add_conversion_history(self, task_id: str, step: str,
                              step_input: Dict, step_output: Dict,
                              execution_time_ms: int):
        """添加转换历史记录"""
        try:
            self.cur.execute("""
                INSERT INTO conversion_history
                (task_id, conversion_step, step_input, step_output, execution_time_ms)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
            """, (task_id, step, json.dumps(step_input),
                  json.dumps(step_output), execution_time_ms))

            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add conversion history: {e}")
            self.conn.rollback()
            raise

    def get_conversion_statistics(self, start_time: datetime, end_time: datetime) -> Dict:
        """获取转换统计信息"""
        try:
            self.cur.execute("""
                SELECT
                    source_type,
                    target_type,
                    conversion_status,
                    COUNT(*) as count,
                    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration_seconds
                FROM dsl_conversion_tasks
                WHERE created_at >= %s AND created_at <= %s
                GROUP BY source_type, target_type, conversion_status
            """, (start_time, end_time))

            results = []
            for row in self.cur.fetchall():
                results.append({
                    'source_type': row[0],
                    'target_type': row[1],
                    'status': row[2],
                    'count': row[3],
                    'avg_duration_seconds': float(row[4]) if row[4] else None
                })

            return results
        except Exception as e:
            logger.error(f"Failed to get conversion statistics: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 数据分析查询示例

**查询转换成功率**：

```python
# 查询各类型转换的成功率
storage.cur.execute("""
    SELECT
        source_type,
        target_type,
        COUNT(*) as total,
        COUNT(CASE WHEN conversion_status = 'COMPLETED' THEN 1 END) as completed,
        ROUND(100.0 * COUNT(CASE WHEN conversion_status = 'COMPLETED' THEN 1 END) / COUNT(*), 2) as success_rate
    FROM dsl_conversion_tasks
    WHERE created_at >= %s
    GROUP BY source_type, target_type
    ORDER BY success_rate DESC
""", (start_time,))
```

**查询转换性能**：

```python
# 查询平均转换时间
storage.cur.execute("""
    SELECT
        source_type,
        target_type,
        AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration,
        MIN(EXTRACT(EPOCH FROM (completed_at - created_at))) as min_duration,
        MAX(EXTRACT(EPOCH FROM (completed_at - created_at))) as max_duration
    FROM dsl_conversion_tasks
    WHERE conversion_status = 'COMPLETED' AND created_at >= %s
    GROUP BY source_type, target_type
""", (start_time,))
```

**查询转换历史详情**：

```python
# 查询特定任务的转换历史
storage.cur.execute("""
    SELECT
        conversion_step,
        step_input,
        step_output,
        execution_time_ms,
        created_at
    FROM conversion_history
    WHERE task_id = %s
    ORDER BY created_at ASC
""", (task_id,))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 三大Schema差异分析
- `03_Standards.md` - MCP协议标准化
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
