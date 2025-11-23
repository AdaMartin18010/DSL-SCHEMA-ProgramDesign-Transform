# 学生信息系统Schema实践案例

## 📑 目录

- [学生信息系统Schema实践案例](#学生信息系统schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：学生信息管理](#2-案例1学生信息管理)
  - [3. 案例2：学籍管理](#3-案例2学籍管理)
  - [4. 案例3：成绩管理](#4-案例3成绩管理)
  - [5. 案例4：Ed-Fi到SIF转换](#5-案例4ed-fi到sif转换)
  - [6. 案例5：学生数据存储与分析](#6-案例5学生数据存储与分析)

---

## 1. 案例概述

本文档提供学生信息系统Schema在实际应用中的实践案例。

---

## 2. 案例1：学生信息管理

### 2.1 场景描述

**应用场景**：
管理学生基本信息，使用Ed-Fi标准格式。

### 2.2 Schema定义

**学生信息Schema**：

```dsl
schema StudentInfo {
  student_id: String @value("STU001") @required
  name: String @value("张三") @required
  gender: Enum { M } @value(M)
  birth_date: Date @value("2005-05-15")
  email: String @value("zhangsan@example.com")
} @standard("Ed-Fi")
```

---

## 3. 案例2：学籍管理

### 3.1 场景描述

**应用场景**：
管理学生学籍信息，跟踪学籍状态变更。

### 3.2 Schema定义

**学籍信息Schema**：

```dsl
schema EnrollmentInfo {
  enrollment_id: String @value("ENR001") @required
  student_id: String @value("STU001") @required
  admission_date: Date @value("2023-09-01")
  enrollment_status: Enum { Active } @value(Active)
} @standard("Ed-Fi")
```

---

## 4. 案例3：成绩管理

### 4.1 场景描述

**应用场景**：
管理学生课程成绩，计算GPA。

### 4.2 Schema定义

**成绩信息Schema**：

```dsl
schema GradeInfo {
  grade_id: String @value("GRD001") @required
  student_id: String @value("STU001") @required
  course_name: String @value("数学")
  semester: String @value("2024春季")
  grade: String @value("A")
  grade_points: Decimal @value(4.0)
  credits: Decimal @value(3.0)
} @standard("Ed-Fi")
```

---

## 5. 案例4：Ed-Fi到SIF转换

### 5.1 场景描述

**应用场景**：
将Ed-Fi格式的学生数据转换为SIF消息格式。

### 5.2 实现代码

```python
from sis_storage import SISStorage

def convert_edfi_to_sif_example():
    """Ed-Fi到SIF转换示例"""
    edfi_data = {
        "student_id": "STU001",
        "name": "张三",
        "birth_date": "2005-05-15",
        "gender": "M"
    }
    
    # 转换为SIF消息
    sif_message = convert_edfi_to_sif(edfi_data)
    print(f"SIF Message: {sif_message}")
    
    return sif_message

if __name__ == "__main__":
    convert_edfi_to_sif_example()
```

---

## 6. 案例5：学生数据存储与分析

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储学生数据，进行学生分析。

### 6.2 实现代码

```python
from sis_storage import SISStorage

def student_data_storage_example():
    """学生数据存储示例"""
    storage = SISStorage("postgresql://user:password@localhost/sis_db")
    storage.create_tables()
    
    # 存储学生
    student_data = {
        "student_id": "STU001",
        "name": "张三",
        "gender": "M",
        "birth_date": "2005-05-15",
        "email": "zhangsan@example.com"
    }
    storage.store_student(student_data)
    
    # 存储学籍
    enrollment_data = {
        "enrollment_id": "ENR001",
        "student_id": "STU001",
        "admission_date": "2023-09-01",
        "enrollment_status": "Active"
    }
    storage.store_enrollment(enrollment_data)
    
    # 存储成绩
    grade_data = {
        "grade_id": "GRD001",
        "student_id": "STU001",
        "course_name": "数学",
        "semester": "2024春季",
        "grade": "A",
        "grade_points": 4.0,
        "credits": 3.0
    }
    storage.store_grade(grade_data)
    
    # 分析学生数据
    results = analyze_student_data(storage)
    print(f"Student analysis results: {results}")
    
    storage.close()

if __name__ == "__main__":
    student_data_storage_example()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21

