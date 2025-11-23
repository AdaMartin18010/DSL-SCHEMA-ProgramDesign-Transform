# 在线教育平台Schema转换体系

## 📑 目录

- [在线教育平台Schema转换体系](#在线教育平台schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Common Cartridge到xAPI转换](#2-common-cartridge到xapi转换)
  - [3. xAPI到Common Cartridge转换](#3-xapi到common-cartridge转换)
  - [4. 在线教育数据存储与分析](#4-在线教育数据存储与分析)
    - [4.1 PostgreSQL在线教育数据存储](#41-postgresql在线教育数据存储)
    - [4.2 在线教育数据分析查询](#42-在线教育数据分析查询)

---

## 1. 转换体系概述

在线教育平台Schema转换体系支持Common Cartridge课程包、xAPI语句、
数据库存储之间的转换。

### 1.1 转换目标

1. **Common Cartridge到xAPI转换**：课程包到xAPI语句
2. **xAPI到Common Cartridge转换**：xAPI语句到课程包
3. **数据到数据库转换**：在线教育数据到PostgreSQL存储

---

## 2. Common Cartridge到xAPI转换

**转换函数**：

```python
def convert_cc_to_xapi(cc_data):
    """Common Cartridge数据转换为xAPI语句"""
    statement = {
        "actor": {
            "mbox": f"mailto:{cc_data['learner_email']}",
            "name": cc_data['learner_name']
        },
        "verb": {
            "id": "http://adlnet.gov/expapi/verbs/experienced",
            "display": {"en-US": "experienced"}
        },
        "object": {
            "id": cc_data['content_id'],
            "definition": {
                "name": {"en-US": cc_data['content_title']}
            }
        },
        "context": {
            "contextActivities": {
                "parent": [{
                    "id": cc_data['course_id']
                }]
            }
        }
    }
    return statement
```

---

## 3. xAPI到Common Cartridge转换

**转换函数**：

```python
def convert_xapi_to_cc(xapi_statement):
    """xAPI语句转换为Common Cartridge数据"""
    cc_data = {
        "learner_email": xapi_statement['actor']['mbox'].replace("mailto:", ""),
        "learner_name": xapi_statement['actor']['name'],
        "content_id": xapi_statement['object']['id'],
        "content_title": xapi_statement['object']['definition']['name']['en-US'],
        "course_id": xapi_statement['context']['contextActivities']['parent'][0]['id']
    }
    return cc_data
```

---

## 4. 在线教育数据存储与分析

### 4.1 PostgreSQL在线教育数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OnlineEducationStorage:
    """在线教育平台PostgreSQL存储"""

    def __init__(self, connection_string):
        """初始化存储连接"""
        if not connection_string:
            raise ValueError("Connection string cannot be empty")

        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def create_tables(self):
        """创建数据表"""
        try:
            # 课程内容表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS course_contents (
                    content_id VARCHAR(50) PRIMARY KEY,
                    course_id VARCHAR(50) NOT NULL,
                    package_id VARCHAR(50),
                    package_name VARCHAR(200),
                    resource_type VARCHAR(50),
                    resource_title VARCHAR(200),
                    resource_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 学习路径表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS learning_paths (
                    path_id VARCHAR(50) PRIMARY KEY,
                    learner_id VARCHAR(50) NOT NULL,
                    current_progress DECIMAL(5,2) DEFAULT 0.0,
                    completed_steps INTEGER DEFAULT 0,
                    total_steps INTEGER NOT NULL,
                    last_accessed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 互动学习表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS interactive_learnings (
                    interaction_id VARCHAR(50) PRIMARY KEY,
                    course_id VARCHAR(50),
                    learner_id VARCHAR(50),
                    interaction_type VARCHAR(50),
                    topic_id VARCHAR(50),
                    topic_title VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
            logger.info("Tables created successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Table creation failed: {e}")
            raise

    def store_course_content(self, content_data):
        """存储课程内容数据"""
        try:
            self.cur.execute("""
                INSERT INTO course_contents (content_id, course_id, package_id,
                                           package_name, resource_type, resource_title,
                                           resource_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_id) DO UPDATE SET
                    resource_title = EXCLUDED.resource_title
            """, (
                content_data['content_id'],
                content_data['course_id'],
                content_data.get('package_id'),
                content_data.get('package_name'),
                content_data.get('resource_type'),
                content_data.get('resource_title'),
                content_data.get('resource_url'),
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Course content stored: {content_data['content_id']}")
            return content_data['content_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store course content: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
```

### 4.2 在线教育数据分析查询

**在线教育数据分析查询示例**：

```python
def analyze_online_education_data(storage):
    """分析在线教育数据"""
    # 学习路径完成率
    storage.cur.execute("""
        SELECT
            learner_id,
            AVG(current_progress) as avg_progress,
            COUNT(*) as total_paths
        FROM learning_paths
        GROUP BY learner_id
        ORDER BY avg_progress DESC
    """)

    results = storage.cur.fetchall()
    return results
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
