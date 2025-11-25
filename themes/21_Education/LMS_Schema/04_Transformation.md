# 学习管理系统Schema转换体系

## 📑 目录

- [学习管理系统Schema转换体系](#学习管理系统schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. SCORM到xAPI转换](#2-scorm到xapi转换)
  - [3. xAPI到SCORM转换](#3-xapi到scorm转换)
  - [4. 学习数据存储与分析](#4-学习数据存储与分析)
    - [4.1 PostgreSQL学习数据存储](#41-postgresql学习数据存储)
    - [4.2 学习数据分析查询](#42-学习数据分析查询)

---

## 1. 转换体系概述

学习管理系统Schema转换体系支持SCORM数据、xAPI语句、
数据库存储之间的转换。

### 1.1 转换目标

1. **SCORM到xAPI转换**：SCORM数据到xAPI语句
2. **xAPI到SCORM转换**：xAPI语句到SCORM数据
3. **数据到数据库转换**：学习数据到PostgreSQL存储

---

## 2. SCORM到xAPI转换

**转换函数**：

```python
def convert_scorm_to_xapi(scorm_data):
    """SCORM数据转换为xAPI语句"""
    statement = {
        "actor": {
            "mbox": f"mailto:{scorm_data['learner_email']}",
            "name": scorm_data['learner_name']
        },
        "verb": {
            "id": "http://adlnet.gov/expapi/verbs/completed",
            "display": {"en-US": "completed"}
        },
        "object": {
            "id": scorm_data['course_id'],
            "definition": {
                "name": {"en-US": scorm_data['course_title']}
            }
        },
        "result": {
            "score": {
                "scaled": scorm_data['score'] / 100.0
            },
            "duration": f"PT{scorm_data['duration']}S"
        }
    }
    return statement
```

---

## 3. xAPI到SCORM转换

**转换函数**：

```python
def convert_xapi_to_scorm(xapi_statement):
    """xAPI语句转换为SCORM数据"""
    scorm_data = {
        "learner_email": xapi_statement['actor']['mbox'].replace("mailto:", ""),
        "learner_name": xapi_statement['actor']['name'],
        "course_id": xapi_statement['object']['id'],
        "course_title": xapi_statement['object']['definition']['name']['en-US'],
        "score": xapi_statement['result']['score']['scaled'] * 100,
        "duration": parse_duration(xapi_statement['result']['duration'])
    }
    return scorm_data
```

---

## 4. 学习数据存储与分析

### 4.1 PostgreSQL学习数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LMSStorage:
    """学习管理系统PostgreSQL存储"""

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
            # 课程表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id VARCHAR(50) PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    category VARCHAR(50),
                    language VARCHAR(2),
                    level VARCHAR(20),
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)

            # 学习者表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS learners (
                    learner_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    language VARCHAR(2),
                    timezone VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 学习活动表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS learning_activities (
                    activity_id VARCHAR(50) PRIMARY KEY,
                    course_id VARCHAR(50) REFERENCES courses(course_id),
                    learner_id VARCHAR(50) REFERENCES learners(learner_id),
                    activity_type VARCHAR(50) NOT NULL,
                    content_id VARCHAR(50),
                    content_title VARCHAR(200),
                    status VARCHAR(20) DEFAULT 'Not_Started',
                    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 学习记录表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS learning_records (
                    record_id VARCHAR(50) PRIMARY KEY,
                    course_id VARCHAR(50) REFERENCES courses(course_id),
                    learner_id VARCHAR(50) REFERENCES learners(learner_id),
                    course_progress DECIMAL(5,2) DEFAULT 0.0,
                    total_time_spent DECIMAL(10,2) DEFAULT 0.0,
                    access_count INTEGER DEFAULT 0,
                    last_accessed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)

            self.conn.commit()
            logger.info("Tables created successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Table creation failed: {e}")
            raise

    def store_course(self, course_data):
        """存储课程数据"""
        try:
            self.cur.execute("""
                INSERT INTO courses (course_id, title, description, category,
                                   language, level, duration, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (course_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                course_data['course_id'],
                course_data['title'],
                course_data.get('description'),
                course_data.get('category'),
                course_data.get('language', 'en'),
                course_data.get('level'),
                course_data.get('duration'),
                datetime.now(),
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Course stored: {course_data['course_id']}")
            return course_data['course_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store course: {e}")
            raise

    def store_learner(self, learner_data):
        """存储学习者数据"""
        try:
            self.cur.execute("""
                INSERT INTO learners (learner_id, name, email, language, timezone, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (learner_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email
            """, (
                learner_data['learner_id'],
                learner_data['name'],
                learner_data['email'],
                learner_data.get('language', 'en'),
                learner_data.get('timezone'),
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Learner stored: {learner_data['learner_id']}")
            return learner_data['learner_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store learner: {e}")
            raise

    def store_learning_activity(self, activity_data):
        """存储学习活动数据"""
        try:
            self.cur.execute("""
                INSERT INTO learning_activities (
                    activity_id, course_id, learner_id, activity_type,
                    content_id, content_title, status, progress_percentage,
                    started_at, completed_at, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (activity_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    progress_percentage = EXCLUDED.progress_percentage,
                    completed_at = EXCLUDED.completed_at
            """, (
                activity_data['activity_id'],
                activity_data['course_id'],
                activity_data['learner_id'],
                activity_data['activity_type'],
                activity_data.get('content_id'),
                activity_data.get('content_title'),
                activity_data.get('status', 'Not_Started'),
                activity_data.get('progress_percentage', 0.0),
                activity_data.get('started_at'),
                activity_data.get('completed_at'),
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Learning activity stored: {activity_data['activity_id']}")
            return activity_data['activity_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store learning activity: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
```

### 4.2 学习数据分析查询

**学习数据分析查询示例**：

```python
def analyze_learning_data(storage):
    """分析学习数据"""
    # 课程完成率
    storage.cur.execute("""
        SELECT
            c.course_id,
            c.title,
            COUNT(DISTINCT lr.learner_id) as enrolled_learners,
            COUNT(DISTINCT CASE WHEN lr.course_progress = 100 THEN lr.learner_id END) as completed_learners,
            ROUND(COUNT(DISTINCT CASE WHEN lr.course_progress = 100 THEN lr.learner_id END)::numeric
                  / NULLIF(COUNT(DISTINCT lr.learner_id), 0) * 100, 2) as completion_rate
        FROM courses c
        LEFT JOIN learning_records lr ON c.course_id = lr.course_id
        GROUP BY c.course_id, c.title
        ORDER BY completion_rate DESC
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
