# 学习管理系统Schema形式化定义

## 📑 目录

- [学习管理系统Schema形式化定义](#学习管理系统schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 课程Schema](#2-课程schema)
  - [3. 学习者Schema](#3-学习者schema)
  - [4. 学习活动Schema](#4-学习活动schema)
  - [5. 学习记录Schema](#5-学习记录schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
    - [8.1 SCORM到xAPI转换](#81-scorm到xapi转换)
    - [8.2 xAPI到SCORM转换](#82-xapi到scorm转换)
    - [8.3 数据到数据库转换](#83-数据到数据库转换)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 数据完整性定理](#91-数据完整性定理)
    - [9.2 进度一致性定理](#92-进度一致性定理)

---

## 1. 形式化模型

**定义1（学习管理系统Schema）**：
学习管理系统Schema是一个六元组：

```text
LMS_Schema = (Course, Learner, Learning_Activity,
             Learning_Record, Assessment, Progress)
```

其中：

- `Course`：课程Schema
- `Learner`：学习者Schema
- `Learning_Activity`：学习活动Schema
- `Learning_Record`：学习记录Schema
- `Assessment`：评估Schema
- `Progress`：进度Schema

---

## 2. 课程Schema

**定义2（课程Schema）**：

```text
Course_Schema = (Course_Info, Course_Structure,
                Course_Content, Course_Settings)
```

**形式化DSL定义**：

```dsl
schema Course {
  course_id: String @pattern("^[A-Z0-9]{10}$") @required @unique

  course_info: {
    title: String @max_length(200) @required
    description: String @max_length(2000)
    category: Enum { Technology, Business, Science, Arts } @required
    language: String @length(2) @pattern("^[a-z]{2}$") @default("en")
    level: Enum { Beginner, Intermediate, Advanced } @required
    duration: Integer @min(1) @unit("hours")
    created_at: DateTime @format("ISO8601") @required
    updated_at: DateTime @format("ISO8601")
  } @required

  course_structure: {
    chapters: List<Chapter> {
      chapter_id: String @required
      chapter_title: String @max_length(200) @required
      chapter_order: Integer @min(1) @required
      units: List<Unit> {
        unit_id: String @required
        unit_title: String @max_length(200) @required
        unit_order: Integer @min(1) @required
        resources: List<Resource> {
          resource_id: String @required
          resource_type: Enum { Video, Document, Quiz, Assignment } @required
          resource_url: String @pattern("^https?://") @required
          resource_duration: Integer @unit("minutes")
        }
      }
    }
  } @required

  course_settings: {
    enrollment_type: Enum { Open, Restricted, Paid } @required
    max_students: Integer @min(1)
    prerequisites: List<String>
    learning_objectives: List<String> @max_length(500)
  } @required
} @standard("SCORM_2004")
```

---

## 3. 学习者Schema

**定义3（学习者Schema）**：

```text
Learner_Schema = (Basic_Info, Learning_Preferences,
                 Learning_History, Learning_Goals)
```

**形式化DSL定义**：

```dsl
schema Learner {
  learner_id: String @pattern("^[A-Z0-9]{10}$") @required @unique

  basic_info: {
    name: String @max_length(100) @required
    email: String @pattern("^[^@]+@[^@]+\\.[^@]+$") @required
    language: String @length(2) @pattern("^[a-z]{2}$") @default("en")
    timezone: String @pattern("^[A-Z]+/[A-Z_]+$")
    created_at: DateTime @format("ISO8601") @required
  } @required

  learning_preferences: {
    learning_style: Enum { Visual, Auditory, Kinesthetic, Reading } @default(Visual)
    preferred_language: String @length(2) @pattern("^[a-z]{2}$")
    notification_preferences: {
      email_notifications: Boolean @default(true)
      push_notifications: Boolean @default(false)
    }
  }

  learning_history: {
    courses_completed: Integer @min(0) @default(0)
    total_learning_hours: Decimal @min(0) @unit("hours") @default(0)
    certificates_earned: Integer @min(0) @default(0)
    average_score: Decimal @range(0.0, 100.0) @unit("percentage")
  }

  learning_goals: List<LearningGoal> {
    goal_id: String @required
    goal_description: String @max_length(500) @required
    target_date: Date @format("YYYY-MM-DD")
    status: Enum { Active, Completed, Cancelled } @default(Active)
  }
} @standard("xAPI")
```

---

## 4. 学习活动Schema

**定义4（学习活动Schema）**：

```text
Learning_Activity_Schema = (Activity_Type, Activity_Content,
                          Activity_Duration, Activity_Status)
```

**形式化DSL定义**：

```dsl
schema LearningActivity {
  activity_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  course_id: String @required
  learner_id: String @required

  activity_type: Enum {
    Video_Watch,
    Document_Read,
    Quiz_Complete,
    Assignment_Submit,
    Discussion_Participate
  } @required

  activity_content: {
    content_id: String @required
    content_title: String @max_length(200) @required
    content_url: String @pattern("^https?://")
  } @required

  activity_duration: {
    estimated_duration: Integer @min(1) @unit("minutes")
    actual_duration: Integer @min(0) @unit("minutes")
  }

  activity_status: Enum {
    Not_Started,
    In_Progress,
    Completed,
    Skipped
  } @default(Not_Started) @required

  started_at: DateTime @format("ISO8601")
  completed_at: DateTime @format("ISO8601")
  progress_percentage: Decimal @range(0.0, 100.0) @unit("percentage") @default(0.0)
} @standard("xAPI")
```

---

## 5. 学习记录Schema

**定义5（学习记录Schema）**：

```text
Learning_Record_Schema = (Progress_Info, Time_Info,
                        Achievement_Info, Behavior_Info)
```

**形式化DSL定义**：

```dsl
schema LearningRecord {
  record_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  course_id: String @required
  learner_id: String @required

  progress_info: {
    course_progress: Decimal @range(0.0, 100.0) @unit("percentage") @required
    chapter_progress: Map<String, Decimal> @range(0.0, 100.0)
    unit_progress: Map<String, Decimal> @range(0.0, 100.0)
    last_accessed_at: DateTime @format("ISO8601") @required
  } @required

  time_info: {
    total_time_spent: Decimal @min(0) @unit("hours") @required
    daily_time_spent: Map<Date, Decimal> @unit("hours")
    average_session_duration: Decimal @unit("minutes")
  } @required

  achievement_info: {
    courses_completed: Integer @min(0) @default(0)
    certificates_earned: Integer @min(0) @default(0)
    badges_earned: List<String>
    average_score: Decimal @range(0.0, 100.0) @unit("percentage")
  }

  behavior_info: {
    access_count: Integer @min(0) @default(0)
    interaction_count: Integer @min(0) @default(0)
    submission_count: Integer @min(0) @default(0)
    last_interaction_at: DateTime @format("ISO8601")
  }
} @standard("xAPI")
```

---

## 6. 类型系统

**定义6（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime,
              Date, Enum, List, Map, Object}
```

**类型约束**：

- `String`：字符串类型，支持长度限制和模式匹配
- `Integer`：整数类型，支持范围限制
- `Decimal`：小数类型，支持精度和范围限制
- `Boolean`：布尔类型
- `DateTime`：日期时间类型，支持ISO8601格式
- `Date`：日期类型，支持YYYY-MM-DD格式
- `Enum`：枚举类型，支持预定义值集合
- `List<T>`：列表类型，支持元素类型约束
- `Map<K, V>`：映射类型，支持键值类型约束
- `Object`：对象类型，支持嵌套结构

---

## 7. 约束规则

**定义7（约束规则）**：

1. **唯一性约束**：`course_id`、`learner_id`、`activity_id`、`record_id`必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：数值类型支持`@min`、`@max`、`@range`约束
4. **长度约束**：字符串类型支持`@max_length`、`@min_length`约束
5. **模式约束**：字符串类型支持`@pattern`正则表达式约束
6. **格式约束**：日期时间类型支持`@format`格式约束

---

## 8. 转换函数

**定义8（转换函数）**：

### 8.1 SCORM到xAPI转换

```text
convert_SCORM_to_xAPI: SCORM_Data → xAPI_Statement
```

### 8.2 xAPI到SCORM转换

```text
convert_xAPI_to_SCORM: xAPI_Statement → SCORM_Data
```

### 8.3 数据到数据库转换

```text
convert_to_Database: LMS_Data → PostgreSQL_Row
```

---

## 9. 形式化定理

### 9.1 数据完整性定理

**定理1（数据完整性）**：
对于任意学习记录`r`，如果`r.course_id`和`r.learner_id`都存在，
则学习记录的数据完整性得到保证。

### 9.2 进度一致性定理

**定理2（进度一致性）**：
对于任意学习者`l`和课程`c`，学习进度`p`满足：
`0 ≤ p.course_progress ≤ 100`且`p.course_progress = Σ(p.chapter_progress) / |chapters|`

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
