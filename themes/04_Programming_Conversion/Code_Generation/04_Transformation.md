# 代码生成转换实现

## 📑 目录

- [代码生成转换实现](#代码生成转换实现)
  - [📑 目录](#-目录)
  - [1. 转换实现概述](#1-转换实现概述)
  - [2. Schema解析实现](#2-schema解析实现)
  - [3. 模板引擎实现](#3-模板引擎实现)
  - [4. 代码生成实现](#4-代码生成实现)
  - [5. 转换工具](#5-转换工具)
  - [6. 参考文献](#6-参考文献)
    - [6.1 技术文档](#61-技术文档)

---

## 1. 转换实现概述

代码生成转换实现包括：

1. **Schema解析**：解析输入Schema
2. **模板应用**：应用代码模板
3. **代码生成**：生成目标代码

---

## 2. Schema解析实现

**Python实现**：

```python
import json
from typing import Dict, Any

class SchemaParser:
    """Schema解析器"""

    def __init__(self, schema_file: str):
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)

    def parse(self) -> Dict[str, Any]:
        """解析Schema"""
        return {
            'types': self._parse_types(),
            'models': self._parse_models()
        }

    def _parse_types(self) -> List[Dict[str, Any]]:
        """解析类型定义"""
        # 实现类型解析逻辑
        pass

    def _parse_models(self) -> List[Dict[str, Any]]:
        """解析模型定义"""
        # 实现模型解析逻辑
        pass
```

---

## 3. 模板引擎实现

**Python实现（使用Jinja2）**：

```python
from jinja2 import Template

class TemplateEngine:
    """模板引擎"""

    def __init__(self, template_file: str):
        with open(template_file, 'r') as f:
            self.template = Template(f.read())

    def render(self, context: Dict[str, Any]) -> str:
        """渲染模板"""
        return self.template.render(**context)
```

---

## 4. 代码生成实现

**Python实现**：

```python
class CodeGenerator:
    """代码生成器"""

    def __init__(self, parser: SchemaParser, template_engine: TemplateEngine):
        self.parser = parser
        self.template_engine = template_engine

    def generate(self, output_file: str):
        """生成代码"""
        schema_data = self.parser.parse()
        code = self.template_engine.render(schema_data)

        with open(output_file, 'w') as f:
            f.write(code)
```

---

## 5. 转换工具

**工具列表**：

1. **openapi-generator**：OpenAPI代码生成
2. **protoc**：Protocol Buffers编译器
3. **quicktype**：JSON到代码生成

---

## 6. 代码生成数据存储与分析

### 6.1 PostgreSQL代码生成数据存储

**代码生成任务和生成结果数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class CodeGenerationTask:
    """代码生成任务"""
    task_id: str
    source_schema: Dict
    target_language: str
    template_name: str
    generation_config: Dict
    timestamp: datetime
    status: str = 'pending'

@dataclass
class GeneratedCode:
    """生成的代码"""
    task_id: str
    file_path: str
    code_content: str
    metadata: Dict
    timestamp: datetime
    success: bool = True

class CodeGenerationStorage:
    """代码生成数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建代码生成数据表"""
        # 代码生成任务表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS code_generation_tasks (
                id SERIAL PRIMARY KEY,
                task_id VARCHAR(200) UNIQUE NOT NULL,
                source_schema JSONB NOT NULL,
                target_language VARCHAR(50) NOT NULL,
                template_name VARCHAR(100) NOT NULL,
                generation_config JSONB NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 生成代码表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS generated_code (
                id BIGSERIAL PRIMARY KEY,
                task_id VARCHAR(200) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                code_content TEXT NOT NULL,
                metadata JSONB NOT NULL,
                success BOOLEAN DEFAULT TRUE,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES code_generation_tasks(task_id)
            )
        """)

        # 代码生成统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS code_generation_statistics (
                id SERIAL PRIMARY KEY,
                target_language VARCHAR(50) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target_language, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_language_status
            ON code_generation_tasks(target_language, status)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_code_task_time
            ON generated_code(task_id, timestamp DESC)
        """)

        self.conn.commit()

    def create_task(self, task: CodeGenerationTask):
        """创建代码生成任务"""
        self.cur.execute("""
            INSERT INTO code_generation_tasks
            (task_id, source_schema, target_language, template_name, generation_config, status)
            VALUES (%s, %s::jsonb, %s, %s, %s::jsonb, %s)
        """, (task.task_id, json.dumps(task.source_schema),
              task.target_language, task.template_name,
              json.dumps(task.generation_config), task.status))
        self.conn.commit()

    def store_code(self, code: GeneratedCode):
        """存储生成的代码"""
        self.cur.execute("""
            INSERT INTO generated_code
            (task_id, file_path, code_content, metadata, success, timestamp)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
        """, (code.task_id, code.file_path, code.code_content,
              json.dumps(code.metadata), code.success, code.timestamp))

        # 更新任务状态
        self.cur.execute("""
            UPDATE code_generation_tasks
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE task_id = %s
        """, ('completed' if code.success else 'failed', code.task_id))

        self.conn.commit()

    def calculate_statistics(self, target_language: str,
                            time_window: timedelta = timedelta(hours=1)) -> Dict:
        """计算代码生成统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.cur.execute("""
            SELECT
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_generations
            FROM code_generation_tasks t
            LEFT JOIN generated_code c ON t.task_id = c.task_id
            WHERE t.target_language = %s
              AND t.created_at >= %s
              AND t.created_at <= %s
        """, (target_language, start_time, end_time))

        stats = self.cur.fetchone()

        statistics = {
            'total_tasks': stats[0] if stats[0] else 0,
            'completed_tasks': stats[1] if stats[1] else 0,
            'successful_generations': stats[2] if stats[2] else 0,
            'success_rate': (stats[2] / stats[0] * 100) if stats[0] > 0 else 0
        }

        # 存储统计结果
        self.cur.execute("""
            INSERT INTO code_generation_statistics
            (target_language, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (target_language, statistic_type, time_window) DO UPDATE
            SET statistics = EXCLUDED.statistics
        """, (target_language, 'code_generation_statistics', end_time,
              json.dumps(statistics)))
        self.conn.commit()

        return statistics

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()
```

---

## 7. 参考文献

### 7.1 技术文档

- 代码生成最佳实践
- PostgreSQL JSONB文档

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展代码生成数据存储和分析功能，新增PostgreSQL存储方案）
