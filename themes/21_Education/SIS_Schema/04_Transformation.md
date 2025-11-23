# 学生信息系统Schema转换体系

## 📑 目录

- [学生信息系统Schema转换体系](#学生信息系统schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. Ed-Fi到SIF转换](#2-ed-fi到sif转换)
  - [3. SIF到Ed-Fi转换](#3-sif到ed-fi转换)
  - [4. 学生数据存储与分析](#4-学生数据存储与分析)
    - [4.1 PostgreSQL学生数据存储](#41-postgresql学生数据存储)
    - [4.2 学生数据分析查询](#42-学生数据分析查询)

---

## 1. 转换体系概述

学生信息系统Schema转换体系支持Ed-Fi数据、SIF消息、
数据库存储之间的转换。

### 1.1 转换目标

1. **Ed-Fi到SIF转换**：Ed-Fi数据到SIF消息
2. **SIF到Ed-Fi转换**：SIF消息到Ed-Fi数据
3. **数据到数据库转换**：学生数据到PostgreSQL存储

---

## 2. Ed-Fi到SIF转换

**转换函数**：

```python
def convert_edfi_to_sif(edfi_data):
    """Ed-Fi数据转换为SIF消息"""
    sif_message = {
        "MessageId": generate_message_id(),
        "MessageType": "StudentPersonal",
        "StudentPersonal": {
            "RefId": edfi_data['student_id'],
            "LocalId": edfi_data['student_id'],
            "Name": {
                "Type": "Legal",
                "FamilyName": edfi_data['name'].split()[-1],
                "GivenName": edfi_data['name'].split()[0]
            },
            "Demographics": {
                "BirthDate": edfi_data['birth_date'],
                "Gender": edfi_data['gender']
            }
        }
    }
    return sif_message
```

---

## 3. SIF到Ed-Fi转换

**转换函数**：

```python
def convert_sif_to_edfi(sif_message):
    """SIF消息转换为Ed-Fi数据"""
    student_personal = sif_message['StudentPersonal']
    edfi_data = {
        "student_id": student_personal['RefId'],
        "name": f"{student_personal['Name']['GivenName']} {student_personal['Name']['FamilyName']}",
        "birth_date": student_personal['Demographics']['BirthDate'],
        "gender": student_personal['Demographics']['Gender']
    }
    return edfi_data
```

---

## 4. 学生数据存储与分析

### 4.1 PostgreSQL学生数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SISStorage:
    """学生信息系统PostgreSQL存储"""

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
            # 学生表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender VARCHAR(1),
                    birth_date DATE,
                    id_number VARCHAR(50),
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 学籍表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id VARCHAR(50) PRIMARY KEY,
                    student_id VARCHAR(50) REFERENCES students(student_id),
                    admission_date DATE NOT NULL,
                    admission_grade VARCHAR(20),
                    enrollment_status VARCHAR(20) DEFAULT 'Active',
                    graduation_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 成绩表
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    grade_id VARCHAR(50) PRIMARY KEY,
                    student_id VARCHAR(50) REFERENCES students(student_id),
                    course_id VARCHAR(50),
                    course_name VARCHAR(200),
                    semester VARCHAR(20),
                    academic_year VARCHAR(20),
                    grade VARCHAR(10),
                    grade_points DECIMAL(3,2),
                    credits DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
            logger.info("Tables created successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Table creation failed: {e}")
            raise

    def store_student(self, student_data):
        """存储学生数据"""
        try:
            self.cur.execute("""
                INSERT INTO students (student_id, name, gender, birth_date,
                                    id_number, email, phone, address, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email
            """, (
                student_data['student_id'],
                student_data['name'],
                student_data.get('gender'),
                student_data.get('birth_date'),
                student_data.get('id_number'),
                student_data.get('email'),
                student_data.get('phone'),
                student_data.get('address'),
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Student stored: {student_data['student_id']}")
            return student_data['student_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store student: {e}")
            raise

    def store_enrollment(self, enrollment_data):
        """存储学籍数据"""
        try:
            self.cur.execute("""
                INSERT INTO enrollments (enrollment_id, student_id, admission_date,
                                       admission_grade, enrollment_status, graduation_date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (enrollment_id) DO UPDATE SET
                    enrollment_status = EXCLUDED.enrollment_status
            """, (
                enrollment_data['enrollment_id'],
                enrollment_data['student_id'],
                enrollment_data['admission_date'],
                enrollment_data.get('admission_grade'),
                enrollment_data.get('enrollment_status', 'Active'),
                enrollment_data.get('graduation_date'),
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Enrollment stored: {enrollment_data['enrollment_id']}")
            return enrollment_data['enrollment_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store enrollment: {e}")
            raise

    def store_grade(self, grade_data):
        """存储成绩数据"""
        try:
            self.cur.execute("""
                INSERT INTO grades (grade_id, student_id, course_id, course_name,
                                 semester, academic_year, grade, grade_points, credits, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (grade_id) DO UPDATE SET
                    grade = EXCLUDED.grade,
                    grade_points = EXCLUDED.grade_points
            """, (
                grade_data['grade_id'],
                grade_data['student_id'],
                grade_data.get('course_id'),
                grade_data['course_name'],
                grade_data['semester'],
                grade_data['academic_year'],
                grade_data['grade'],
                grade_data.get('grade_points'),
                grade_data['credits'],
                datetime.now()
            ))
            self.conn.commit()
            logger.info(f"Grade stored: {grade_data['grade_id']}")
            return grade_data['grade_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store grade: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
```

### 4.2 学生数据分析查询

**学生数据分析查询示例**：

```python
def analyze_student_data(storage):
    """分析学生数据"""
    # GPA统计
    storage.cur.execute("""
        SELECT 
            s.student_id,
            s.name,
            AVG(g.grade_points) as avg_gpa,
            SUM(g.credits) as total_credits
        FROM students s
        LEFT JOIN grades g ON s.student_id = g.student_id
        GROUP BY s.student_id, s.name
        ORDER BY avg_gpa DESC
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

