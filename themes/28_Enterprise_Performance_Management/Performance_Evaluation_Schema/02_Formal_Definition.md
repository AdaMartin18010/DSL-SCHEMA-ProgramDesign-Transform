# 绩效评估Schema形式化定义

## 📑 目录

- [绩效评估Schema形式化定义](#绩效评估schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 评估周期Schema](#2-评估周期schema)
  - [3. 评估对象Schema](#3-评估对象schema)
  - [4. 评估结果Schema](#4-评估结果schema)
  - [5. 评估反馈Schema](#5-评估反馈schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 评估完整性定理](#91-评估完整性定理)
    - [9.2 评估一致性定理](#92-评估一致性定理)
    - [9.3 评估公平性定理](#93-评估公平性定理)

---

## 1. 形式化模型

**定义1（绩效评估Schema）**：
绩效评估Schema是一个四元组：

```text
Performance_Evaluation_Schema = (Evaluation_Cycle, Evaluation_Object,
                                Evaluation_Result, Evaluation_Feedback)
```

其中：

- `Evaluation_Cycle`：评估周期Schema
- `Evaluation_Object`：评估对象Schema
- `Evaluation_Result`：评估结果Schema
- `Evaluation_Feedback`：评估反馈Schema

---

## 2. 评估周期Schema

**定义2（评估周期Schema）**：

```text
Evaluation_Cycle_Schema = (Cycle_Definition, Evaluation_Time, Evaluation_Frequency)
```

**形式化DSL定义**：

```dsl
schema EvaluationCycle {
  evaluation_cycles: List<EvaluationCycle> {
    cycle_id: String @required @unique
    cycle_name: String @required
    cycle_type: Enum { Annual, Semi_Annual, Quarterly, Monthly } @required
    cycle_start_date: Date @required
    cycle_end_date: Date @required
    evaluation_start_date: Date @required
    evaluation_end_date: Date @required
    evaluation_deadline: Date @required
    is_active: Boolean @default(true)
  }

  evaluation_schedules: List<EvaluationSchedule> {
    schedule_id: String @required @unique
    cycle_id: String @required
    evaluation_type: Enum { Self, Manager, Peer, Subordinate, Customer, 360 } @required
    schedule_date: Date @required
    reminder_days: Int @range(0, 30) @default(7)
  }
} @standard("Performance_Evaluation")
```

---

## 3. 评估对象Schema

**定义3（评估对象Schema）**：

```text
Evaluation_Object_Schema = (Object_Definition, Object_Category, Object_Hierarchy)
```

**形式化DSL定义**：

```dsl
schema EvaluationObject {
  evaluation_objects: List<EvaluationObject> {
    object_id: String @required @unique
    object_name: String @required
    object_type: Enum { Employee, Department, Team, Organization } @required
    object_level: Enum { Corporate, Division, Department, Team, Individual } @required
    parent_object_id: Optional<String>
    manager_id: Optional<String>
    department_id: Optional<String>
    position: Optional<String>
    is_active: Boolean @default(true)
  }

  evaluation_criteria: List<EvaluationCriteria> {
    criteria_id: String @required @unique
    object_type: Enum { Employee, Department, Team, Organization } @required
    criteria_name: String @required
    criteria_description: String @required
    criteria_weight: Decimal @range(0, 100) @default(100)
    criteria_type: Enum { Goal_Achievement, Competency, Behavior, Contribution } @required
    evaluation_method: Enum { Rating, Score, Yes_No, Text } @required
  }
} @standard("Performance_Evaluation")
```

---

## 4. 评估结果Schema

**定义4（评估结果Schema）**：

```text
Evaluation_Result_Schema = (Result_Definition, Evaluation_Score, Evaluation_Level)
```

**形式化DSL定义**：

```dsl
schema EvaluationResult {
  evaluation_results: List<EvaluationResult> {
    result_id: String @required @unique
    cycle_id: String @required
    object_id: String @required
    evaluator_id: String @required
    evaluator_type: Enum { Self, Manager, Peer, Subordinate, Customer, System } @required
    evaluation_date: Date @required
    total_score: Decimal @range(0, 100) @required
    weighted_score: Decimal @range(0, 100) @computed("SUM(criteria_scores * criteria_weights) / SUM(criteria_weights)")
    evaluation_level: Enum { Excellent, Good, Average, Poor } @computed
    evaluation_status: Enum { Draft, Submitted, Approved, Rejected } @default("Draft")
  }

  criteria_scores: List<CriteriaScore> {
    score_id: String @required @unique
    result_id: String @required
    criteria_id: String @required
    score_value: Decimal @range(0, 100) @required
    score_comment: Optional<String>
  }

  evaluation_summaries: List<EvaluationSummary> {
    summary_id: String @required @unique
    result_id: String @required
    summary_type: Enum { Strengths, Weaknesses, Achievements, Improvements } @required
    summary_content: String @required
  }
} @standard("Performance_Evaluation")
```

---

## 5. 评估反馈Schema

**定义5（评估反馈Schema）**：

```text
Evaluation_Feedback_Schema = (Feedback_Definition, Improvement_Recommendation, Action_Plan)
```

**形式化DSL定义**：

```dsl
schema EvaluationFeedback {
  evaluation_feedbacks: List<EvaluationFeedback> {
    feedback_id: String @required @unique
    result_id: String @required
    feedback_type: Enum { Manager_Feedback, Peer_Feedback, Self_Reflection, Improvement_Plan } @required
    feedback_content: String @required
    feedback_date: Date @required
    feedback_provider: String @required
  }

  improvement_recommendations: List<ImprovementRecommendation> {
    recommendation_id: String @required @unique
    result_id: String @required
    recommendation_content: String @required
    recommendation_priority: Enum { High, Medium, Low } @default("Medium")
    recommendation_category: Enum { Skill_Development, Process_Improvement, Behavior_Change, Goal_Adjustment } @required
    recommendation_owner: String @required
    target_completion_date: Optional<Date>
  }

  action_plans: List<ActionPlan> {
    plan_id: String @required @unique
    result_id: String @required
    plan_name: String @required
    plan_description: String @required
    plan_owner: String @required
    plan_start_date: Date @required
    plan_end_date: Date @required
    plan_status: Enum { Not_Started, In_Progress, Completed, Cancelled } @default("Not_Started")
    related_recommendations: List<String>
  }
} @standard("Performance_Evaluation")
```

---

## 6. 类型系统

**类型定义**：

```dsl
type CycleID = String @pattern("^CYC-[0-9]{8}$")
type ObjectID = String @pattern("^OBJ-[0-9]{8}$")
type ResultID = String @pattern("^RES-[0-9]{8}$")
type Decimal = Float @precision(18, 2) @range(null, null)
type Percentage = Float @range(0, 100) @precision(5, 2)
type DateRange = Object {
  start_date: Date
  end_date: Date
} @constraint("end_date >= start_date")
```

---

## 7. 约束规则

**约束1（评估周期完整性约束）**：

```text
∀cycle ∈ Evaluation_Cycles:
  cycle.cycle_end_date >= cycle.cycle_start_date
  ∧ cycle.evaluation_end_date >= cycle.evaluation_start_date
  ∧ cycle.evaluation_deadline >= cycle.evaluation_end_date
```

**约束2（评估结果一致性约束）**：

```text
∀result ∈ Evaluation_Results:
  result.cycle_id exists in Evaluation_Cycles
  ∧ result.object_id exists in Evaluation_Objects
  ∧ result.total_score == SUM(criteria_scores.score_value * criteria_weights) / SUM(criteria_weights)
```

**约束3（评估公平性约束）**：

```text
∀result ∈ Evaluation_Results:
  result.evaluator_type != "Self"
  → ∃peer_result: peer_result.object_id == result.object_id
    ∧ peer_result.evaluator_type == "Peer"
    ∧ peer_result.total_score within [result.total_score - 10, result.total_score + 10]
```

---

## 8. 转换函数

**转换函数1（绩效评估到JSON Schema）**：

```text
f_PerformanceEvaluation_to_JSONSchema: Performance_Evaluation_Schema → JSON_Schema

f_PerformanceEvaluation_to_JSONSchema(eval) = {
  json_schema: {
    evaluation_results: eval.evaluation_results.map(result => {
      result_id: result.result_id
      object_id: result.object_id
      total_score: result.total_score
      evaluation_level: result.evaluation_level
    })
  }
}
```

**转换函数2（绩效评估到OLAP Cube）**：

```text
f_PerformanceEvaluation_to_OLAPCube: Performance_Evaluation_Schema → OLAP_Cube

f_PerformanceEvaluation_to_OLAPCube(eval) = {
  olap_cube: {
    dimensions: ["Time", "Object_Type", "Department", "Evaluator_Type"]
    measures: ["Total_Score", "Weighted_Score", "Evaluation_Count"]
    facts: eval.evaluation_results
  }
}
```

---

## 9. 形式化定理

### 9.1 评估完整性定理

**定理1（评估完整性）**：

对于任意评估周期，必须包含有效的评估时间和截止时间：

```text
∀cycle ∈ Evaluation_Cycles:
  cycle.evaluation_end_date >= cycle.evaluation_start_date
  ∧ cycle.evaluation_deadline >= cycle.evaluation_end_date
```

**证明**：

由约束1和类型系统定义，评估完整性满足上述条件。

### 9.2 评估一致性定理

**定理2（评估一致性）**：

对于任意评估结果，总分必须等于加权分数：

```text
∀result ∈ Evaluation_Results:
  result.total_score == result.weighted_score
```

**证明**：

由约束2和类型系统定义，评估一致性满足上述条件。

### 9.3 评估公平性定理

**定理3（评估公平性）**：

对于任意评估结果，如果存在同级评估，则评估分数应该相近：

```text
∀result ∈ Evaluation_Results:
  result.evaluator_type != "Self"
  → ∃peer_result: peer_result.object_id == result.object_id
    ∧ peer_result.evaluator_type == "Peer"
    ∧ |peer_result.total_score - result.total_score| <= 10
```

**证明**：

由约束3和类型系统定义，评估公平性满足上述条件。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
