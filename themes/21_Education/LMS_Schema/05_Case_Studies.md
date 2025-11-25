# 学习管理系统Schema实践案例

## 📑 目录

- [学习管理系统Schema实践案例](#学习管理系统schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：课程管理](#2-案例1课程管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：学习者注册](#3-案例2学习者注册)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：学习进度跟踪](#4-案例3学习进度跟踪)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：SCORM到xAPI转换](#5-案例4scorm到xapi转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：学习数据存储与分析](#6-案例5学习数据存储与分析)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供学习管理系统Schema在实际应用中的实践案例。

---

## 2. 案例1：课程管理

### 2.1 场景描述

**应用场景**：
创建和管理在线课程，使用SCORM标准格式。

### 2.2 Schema定义

**课程Schema**：

```dsl
schema Course {
  course_id: String @value("COURSE001") @required
  title: String @value("Python编程基础") @required
  description: String @value("学习Python编程基础")
  category: Enum { Technology } @value(Technology)
  level: Enum { Beginner } @value(Beginner)
  duration: Integer @value(40) @unit("hours")
} @standard("SCORM_2004")
```

---

## 3. 案例2：学习者注册

### 3.1 场景描述

**应用场景**：
学习者注册到LMS系统，创建学习者账户。

### 3.2 Schema定义

**学习者Schema**：

```dsl
schema Learner {
  learner_id: String @value("LEARNER001") @required
  name: String @value("张三") @required
  email: String @value("zhangsan@example.com") @required
  language: String @value("zh") @default("en")
} @standard("xAPI")
```

---

## 4. 案例3：学习进度跟踪

### 4.1 场景描述

**应用场景**：
跟踪学习者的学习进度，记录学习活动。

### 4.2 Schema定义

**学习活动Schema**：

```dsl
schema LearningActivity {
  activity_id: String @value("ACTIVITY001") @required
  course_id: String @value("COURSE001") @required
  learner_id: String @value("LEARNER001") @required
  activity_type: Enum { Video_Watch } @value(Video_Watch)
  status: Enum { Completed } @value(Completed)
  progress_percentage: Decimal @value(100.0) @range(0.0, 100.0)
} @standard("xAPI")
```

---

## 5. 案例4：SCORM到xAPI转换

### 5.1 场景描述

**应用场景**：
将SCORM格式的学习数据转换为xAPI语句。

### 5.2 实现代码

```python
from lms_storage import LMSStorage

def convert_scorm_to_xapi_example():
    """SCORM到xAPI转换示例"""
    scorm_data = {
        "learner_email": "learner@example.com",
        "learner_name": "张三",
        "course_id": "COURSE001",
        "course_title": "Python编程基础",
        "score": 85,
        "duration": 3600
    }

    # 转换为xAPI语句
    xapi_statement = convert_scorm_to_xapi(scorm_data)
    print(f"xAPI Statement: {xapi_statement}")

    return xapi_statement

if __name__ == "__main__":
    convert_scorm_to_xapi_example()
```

---

## 6. 案例5：学习数据存储与分析

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储学习数据，进行学习分析。

### 6.2 实现代码

```python
from lms_storage import LMSStorage

def learning_data_storage_example():
    """学习数据存储示例"""
    storage = LMSStorage("postgresql://user:password@localhost/lms_db")
    storage.create_tables()

    # 存储课程
    course_data = {
        "course_id": "COURSE001",
        "title": "Python编程基础",
        "description": "学习Python编程基础",
        "category": "Technology",
        "level": "Beginner",
        "duration": 40
    }
    storage.store_course(course_data)

    # 存储学习者
    learner_data = {
        "learner_id": "LEARNER001",
        "name": "张三",
        "email": "zhangsan@example.com",
        "language": "zh"
    }
    storage.store_learner(learner_data)

    # 存储学习活动
    activity_data = {
        "activity_id": "ACTIVITY001",
        "course_id": "COURSE001",
        "learner_id": "LEARNER001",
        "activity_type": "Video_Watch",
        "status": "Completed",
        "progress_percentage": 100.0
    }
    storage.store_learning_activity(activity_data)

    # 分析学习数据
    results = analyze_learning_data(storage)
    print(f"Learning analysis results: {results}")

    storage.close()

if __name__ == "__main__":
    learning_data_storage_example()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
