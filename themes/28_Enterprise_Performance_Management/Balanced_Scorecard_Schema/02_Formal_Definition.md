# 平衡计分卡Schema形式化定义

## 📑 目录

- [平衡计分卡Schema形式化定义](#平衡计分卡schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 战略目标Schema](#2-战略目标schema)
  - [3. 指标Schema](#3-指标schema)
  - [4. 行动计划Schema](#4-行动计划schema)
  - [5. 战略地图Schema](#5-战略地图schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 平衡计分卡完整性定理](#91-平衡计分卡完整性定理)
    - [9.2 因果关系一致性定理](#92-因果关系一致性定理)
    - [9.3 价值创造路径定理](#93-价值创造路径定理)

---

## 1. 形式化模型

**定义1（平衡计分卡Schema）**：
平衡计分卡Schema是一个四元组：

```text
Balanced_Scorecard_Schema = (Strategic_Objective, Metric,
                            Action_Plan, Strategy_Map)
```

其中：

- `Strategic_Objective`：战略目标Schema
- `Metric`：指标Schema
- `Action_Plan`：行动方案Schema
- `Strategy_Map`：战略地图Schema

---

## 2. 战略目标Schema

**定义2（战略目标Schema）**：

```text
Strategic_Objective_Schema = (Objective_Definition, Objective_Category, Objective_Hierarchy)
```

**形式化DSL定义**：

```dsl
schema StrategicObjective {
  strategic_objectives: List<StrategicObjective> {
    objective_id: String @required @unique
    objective_name: String @required
    objective_description: String @required
    objective_dimension: Enum { Financial, Customer, Internal_Process, Learning_Growth } @required
    objective_category: String @required
    objective_priority: Enum { Critical, High, Medium, Low } @default("Medium")
    objective_level: Enum { Corporate, Division, Department, Team } @default("Corporate")
    parent_objective_id: Optional<String>
    owner: String @required
    target_date: Date @required
    is_active: Boolean @default(true)
  }

  objective_hierarchies: List<ObjectiveHierarchy> {
    hierarchy_id: String @required @unique
    parent_objective_id: String @required
    child_objective_id: String @required
    hierarchy_level: Int @range(1, 10) @required
  }
} @standard("BSC")
```

---

## 3. 指标Schema

**定义3（指标Schema）**：

```text
Metric_Schema = (Metric_Definition, Metric_Linkage, Metric_Value)
```

**形式化DSL定义**：

```dsl
schema Metric {
  metric_definitions: List<MetricDefinition> {
    metric_id: String @required @unique
    metric_name: String @required
    metric_description: String @required
    metric_type: Enum { Leading, Lagging, Outcome, Driver } @required
    objective_id: String @required
    calculation_formula: String @required
    measurement_unit: String @required
    target_value: Decimal @required
    baseline_value: Optional<Decimal>
    owner: String @required
  }

  metric_linkages: List<MetricLinkage> {
    linkage_id: String @required @unique
    source_metric_id: String @required
    target_metric_id: String @required
    linkage_type: Enum { Causal, Correlation, Dependency } @required
    linkage_strength: Enum { Strong, Medium, Weak } @default("Medium")
    linkage_direction: Enum { Positive, Negative } @required
  }

  metric_values: List<MetricValue> {
    value_id: String @required @unique
    metric_id: String @required
    value: Decimal @required
    measurement_date: Date @required
    completion_rate: Decimal @computed("value / target_value * 100") @range(0, null)
  }
} @standard("BSC")
```

---

## 4. 行动计划Schema

**定义4（行动计划Schema）**：

```text
Action_Plan_Schema = (Action_Definition, Action_Execution, Action_Evaluation)
```

**形式化DSL定义**：

```dsl
schema ActionPlan {
  action_definitions: List<ActionDefinition> {
    action_id: String @required @unique
    action_name: String @required
    action_description: String @required
    objective_id: String @required
    action_type: Enum { Initiative, Project, Program, Activity } @required
    action_priority: Enum { Critical, High, Medium, Low } @default("Medium")
    owner: String @required
    start_date: Date @required
    end_date: Date @required
    budget: Optional<Decimal>
    resources: List<String>
  }

  action_executions: List<ActionExecution> {
    execution_id: String @required @unique
    action_id: String @required
    execution_status: Enum { Not_Started, In_Progress, Completed, On_Hold, Cancelled } @default("Not_Started")
    execution_progress: Decimal @range(0, 100) @default(0)
    execution_start_date: Optional<Date>
    execution_end_date: Optional<Date>
    actual_cost: Optional<Decimal>
    milestones: List<Milestone> {
      milestone_id: String @required @unique
      milestone_name: String @required
      milestone_date: Date @required
      milestone_status: Enum { Not_Started, In_Progress, Completed } @default("Not_Started")
    }
  }

  action_evaluations: List<ActionEvaluation> {
    evaluation_id: String @required @unique
    action_id: String @required
    evaluation_date: Date @required
    evaluation_criteria: List<String> @required
    evaluation_result: Enum { Exceeded, Met, Partially_Met, Not_Met } @required
    evaluation_score: Decimal @range(0, 100)
    improvement_recommendations: List<String>
  }
} @standard("BSC")
```

---

## 5. 战略地图Schema

**定义5（战略地图Schema）**：

```text
Strategy_Map_Schema = (Map_Structure, Causal_Relationship, Value_Creation_Path)
```

**形式化DSL定义**：

```dsl
schema StrategyMap {
  strategy_maps: List<StrategyMap> {
    map_id: String @required @unique
    map_name: String @required
    map_version: String @required
    map_period: DateRange {
      start_date: Date @required
      end_date: Date @required
    }
    map_dimensions: List<MapDimension> {
      dimension_name: Enum { Learning_Growth, Internal_Process, Customer, Financial } @required
      dimension_order: Int @range(1, 4) @required
      objectives: List<String> @required
    }
  }

  causal_relationships: List<CausalRelationship> {
    relationship_id: String @required @unique
    source_objective_id: String @required
    target_objective_id: String @required
    relationship_type: Enum { Enables, Influences, Drives } @required
    relationship_strength: Enum { Strong, Medium, Weak } @default("Medium")
    relationship_evidence: Optional<String>
  }

  value_creation_paths: List<ValueCreationPath> {
    path_id: String @required @unique
    path_name: String @required
    path_objectives: List<String> @required
    path_metrics: List<String> @required
    expected_value: Decimal @required
    value_driver: String @required
  }
} @standard("BSC")
```

---

## 6. 类型系统

**类型定义**：

```dsl
type ObjectiveID = String @pattern("^OBJ-[0-9]{8}$")
type MetricID = String @pattern("^MET-[0-9]{8}$")
type ActionID = String @pattern("^ACT-[0-9]{8}$")
type Decimal = Float @precision(18, 2) @range(null, null)
type Percentage = Float @range(0, 100) @precision(5, 2)
type DateRange = Object {
  start_date: Date
  end_date: Date
} @constraint("end_date >= start_date")
```

---

## 7. 约束规则

**约束1（平衡计分卡完整性约束）**：

```text
∀bsc ∈ Balanced_Scorecards:
  bsc.strategic_objectives.size() >= 4
  ∧ ∀dimension ∈ [Financial, Customer, Internal_Process, Learning_Growth]:
    ∃objective: objective.objective_dimension == dimension
```

**约束2（指标关联一致性约束）**：

```text
∀metric ∈ Metrics:
  metric.objective_id exists in Strategic_Objectives
  ∧ metric.target_value != null
```

**约束3（因果关系一致性约束）**：

```text
∀relationship ∈ Causal_Relationships:
  relationship.source_objective_id exists in Strategic_Objectives
  ∧ relationship.target_objective_id exists in Strategic_Objectives
  ∧ relationship.source_objective_id != relationship.target_objective_id
```

---

## 8. 转换函数

**转换函数1（BSC到JSON Schema）**：

```text
f_BSC_to_JSONSchema: Balanced_Scorecard_Schema → JSON_Schema

f_BSC_to_JSONSchema(bsc) = {
  json_schema: {
    strategic_objectives: bsc.strategic_objectives.map(obj => {
      objective_id: obj.objective_id
      objective_name: obj.objective_name
      objective_dimension: obj.objective_dimension
    }),
    metrics: bsc.metrics.map(metric => {
      metric_id: metric.metric_id
      metric_name: metric.metric_name
      objective_id: metric.objective_id
    })
  }
}
```

**转换函数2（BSC到战略地图）**：

```text
f_BSC_to_StrategyMap: Balanced_Scorecard_Schema → Strategy_Map

f_BSC_to_StrategyMap(bsc) = {
  strategy_map: {
    dimensions: group_by_dimension(bsc.strategic_objectives)
    relationships: bsc.causal_relationships
    value_paths: calculate_value_paths(bsc)
  }
}
```

---

## 9. 形式化定理

### 9.1 平衡计分卡完整性定理

**定理1（平衡计分卡完整性）**：

对于任意平衡计分卡，必须包含四个维度的战略目标：

```text
∀bsc ∈ Balanced_Scorecards:
  ∀dimension ∈ [Financial, Customer, Internal_Process, Learning_Growth]:
    ∃objective: objective.objective_dimension == dimension
```

**证明**：

由约束1和类型系统定义，平衡计分卡完整性满足上述条件。

### 9.2 因果关系一致性定理

**定理2（因果关系一致性）**：

对于任意因果关系，源目标和目标目标必须存在且不同：

```text
∀relationship ∈ Causal_Relationships:
  relationship.source_objective_id exists in Strategic_Objectives
  ∧ relationship.target_objective_id exists in Strategic_Objectives
  ∧ relationship.source_objective_id != relationship.target_objective_id
```

**证明**：

由约束3和类型系统定义，因果关系一致性满足上述条件。

### 9.3 价值创造路径定理

**定理3（价值创造路径）**：

对于任意价值创造路径，必须从学习成长维度开始，最终到达财务维度：

```text
∀path ∈ Value_Creation_Paths:
  path.path_objectives[0].objective_dimension == "Learning_Growth"
  ∧ path.path_objectives[-1].objective_dimension == "Financial"
  ∧ ∀i ∈ [1, n-1]:
    path.path_objectives[i].objective_dimension in ["Internal_Process", "Customer"]
```

**证明**：

由战略地图定义和价值创造逻辑，价值创造路径满足上述条件。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
