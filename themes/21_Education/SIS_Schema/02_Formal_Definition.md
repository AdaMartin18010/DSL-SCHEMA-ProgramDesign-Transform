# 学生信息系统Schema形式化定义

## 📑 目录

- [学生信息系统Schema形式化定义](#学生信息系统schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 学生信息Schema](#2-学生信息schema)
  - [3. 学籍信息Schema](#3-学籍信息schema)
  - [4. 成绩信息Schema](#4-成绩信息schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

**定义1（学生信息系统Schema）**：
学生信息系统Schema是一个五元组：

```text
SIS_Schema = (Student_Info, Enrollment_Info,
             Grade_Info, Course_Registration, Attendance)
```

其中：

- `Student_Info`：学生信息Schema
- `Enrollment_Info`：学籍信息Schema
- `Grade_Info`：成绩信息Schema
- `Course_Registration`：课程注册Schema
- `Attendance`：考勤信息Schema

---

## 2. 学生信息Schema

**定义2（学生信息Schema）**：

```text
Student_Info_Schema = (Basic_Info, Contact_Info,
                      Family_Info, Emergency_Contact)
```

**形式化DSL定义**：

```dsl
schema StudentInfo {
  student_id: String @pattern("^[A-Z0-9]{10}$") @required @unique

  basic_info: {
    name: String @max_length(100) @required
    gender: Enum { M, F, O } @required
    birth_date: Date @format("YYYY-MM-DD") @required
    id_number: String @pattern("^[0-9X]{18}$")
    nationality: String @length(2) @pattern("^[A-Z]{2}$")
  } @required

  contact_info: {
    address: String @max_length(200)
    phone: String @pattern("^[0-9-+]{10,20}$")
    email: String @pattern("^[^@]+@[^@]+\\.[^@]+$")
  }

  family_info: {
    parent1_name: String @max_length(100)
    parent1_relationship: String @max_length(50)
    parent1_phone: String @pattern("^[0-9-+]{10,20}$")
    parent2_name: String @max_length(100)
    parent2_relationship: String @max_length(50)
    parent2_phone: String @pattern("^[0-9-+]{10,20}$")
  }

  emergency_contact: {
    name: String @max_length(100) @required
    relationship: String @max_length(50) @required
    phone: String @pattern("^[0-9-+]{10,20}$") @required
  } @required
} @standard("Ed-Fi")
```

---

## 3. 学籍信息Schema

**定义3（学籍信息Schema）**：

```text
Enrollment_Info_Schema = (Admission_Info, Enrollment_Status,
                         Enrollment_Changes, Graduation_Info)
```

**形式化DSL定义**：

```dsl
schema EnrollmentInfo {
  enrollment_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  student_id: String @required

  admission_info: {
    admission_date: Date @format("YYYY-MM-DD") @required
    admission_grade: String @max_length(20) @required
    admission_type: Enum { Regular, Transfer, Special } @required
  } @required

  enrollment_status: Enum {
    Active,
    Inactive,
    Suspended,
    Graduated,
    Transferred
  } @default(Active) @required

  enrollment_changes: List<EnrollmentChange> {
    change_type: Enum { Transfer, Suspension, Reinstatement } @required
    change_date: Date @format("YYYY-MM-DD") @required
    reason: String @max_length(500)
  }

  graduation_info: {
    graduation_date: Date @format("YYYY-MM-DD")
    diploma_number: String @max_length(50)
    honors: List<String>
  }
} @standard("Ed-Fi")
```

---

## 4. 成绩信息Schema

**定义4（成绩信息Schema）**：

```text
Grade_Info_Schema = (Course_Grades, GPA_Info, Credit_Info)
```

**形式化DSL定义**：

```dsl
schema GradeInfo {
  grade_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  student_id: String @required
  course_id: String @required

  course_grade: {
    course_name: String @max_length(200) @required
    semester: String @max_length(20) @required
    academic_year: String @pattern("^[0-9]{4}-[0-9]{4}$") @required
    grade: String @max_length(10) @required
    grade_points: Decimal @range(0.0, 4.0)
    credits: Decimal @min(0) @required
  } @required

  gpa_info: {
    semester_gpa: Decimal @range(0.0, 4.0)
    cumulative_gpa: Decimal @range(0.0, 4.0)
    class_rank: Integer @min(1)
    grade_rank: Integer @min(1)
  }

  credit_info: {
    credits_earned: Decimal @min(0) @default(0)
    credits_required: Decimal @min(0)
    credits_remaining: Decimal
  }
} @standard("Ed-Fi")
```

---

## 5. 类型系统

**定义5（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime,
              Date, Enum, List, Map, Object}
```

---

## 6. 约束规则

**定义6（约束规则）**：

1. **唯一性约束**：`student_id`、`enrollment_id`、`grade_id`必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：数值类型支持`@min`、`@max`、`@range`约束
4. **格式约束**：日期时间类型支持`@format`格式约束

---

## 7. 转换函数

**定义7（转换函数）**：

### 7.1 Ed-Fi到SIF转换

```text
convert_EdFi_to_SIF: EdFi_Data → SIF_Message
```

### 7.2 SIF到Ed-Fi转换

```text
convert_SIF_to_EdFi: SIF_Message → EdFi_Data
```

---

## 8. 形式化定理

### 8.1 数据完整性定理

**定理1（数据完整性）**：
对于任意学籍记录`e`，如果`e.student_id`存在，
则学籍记录的数据完整性得到保证。

### 8.2 GPA一致性定理

**定理2（GPA一致性）**：
对于任意学生`s`，累计GPA满足：
`GPA = Σ(grade_points × credits) / Σ(credits)`

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21

