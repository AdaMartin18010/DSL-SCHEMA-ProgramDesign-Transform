# 平衡计分卡Schema实践案例

## 📑 目录

- [平衡计分卡Schema实践案例](#平衡计分卡schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业战略目标设定](#2-案例1企业战略目标设定)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：战略地图构建](#3-案例2战略地图构建)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
  - [4. 案例3：指标关联与监控](#4-案例3指标关联与监控)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：行动计划执行管理](#5-案例4行动计划执行管理)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：BSC数据存储与分析系统](#6-案例5bsc数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供平衡计分卡Schema在实际应用中的实践案例。

---

## 2. 案例1：企业战略目标设定

### 2.1 场景描述

**应用场景**：
设定企业战略目标，包括财务、客户、内部流程、学习成长四个维度的目标。

**业务需求**：

- 支持四个维度目标设定
- 支持目标层次结构
- 支持目标关联

### 2.2 Schema定义

**企业战略目标Schema**：

```dsl
schema EnterpriseStrategicObjectives {
  financial_objective: StrategicObjective {
    objective_id: String @value("OBJ-FIN-001")
    objective_name: String @value("提升盈利能力")
    objective_dimension: Enum @value("Financial")
    objective_priority: Enum @value("Critical")
    owner: String @value("财务部")
    target_date: Date @value("2025-12-31")
  }

  customer_objective: StrategicObjective {
    objective_id: String @value("OBJ-CUS-001")
    objective_name: String @value("提升客户满意度")
    objective_dimension: Enum @value("Customer")
    objective_priority: Enum @value("High")
    owner: String @value("客户服务部")
    target_date: Date @value("2025-12-31")
  }

  process_objective: StrategicObjective {
    objective_id: String @value("OBJ-PROC-001")
    objective_name: String @value("优化业务流程")
    objective_dimension: Enum @value("Internal_Process")
    objective_priority: Enum @value("High")
    owner: String @value("运营部")
    target_date: Date @value("2025-12-31")
  }

  learning_objective: StrategicObjective {
    objective_id: String @value("OBJ-LEARN-001")
    objective_name: String @value("提升员工能力")
    objective_dimension: Enum @value("Learning_Growth")
    objective_priority: Enum @value("Medium")
    owner: String @value("人力资源部")
    target_date: Date @value("2025-12-31")
  }
}
```

---

## 3. 案例2：战略地图构建

### 3.1 场景描述

**应用场景**：
构建企业战略地图，展示从学习成长到财务的价值创造路径。

**业务需求**：

- 支持战略地图可视化
- 支持因果关系展示
- 支持价值创造路径分析

### 3.2 实现代码

```python
def build_strategy_map(bsc_data: BalancedScorecardSchema) -> StrategyMap:
    """构建战略地图"""
    strategy_map = StrategyMap()
    strategy_map.map_id = "MAP-001"
    strategy_map.map_name = "企业战略地图"
    strategy_map.map_version = "1.0"

    # 按维度组织目标
    dimensions_order = ["Learning_Growth", "Internal_Process", "Customer", "Financial"]
    dimension_objectives = {}

    for objective in bsc_data.strategic_objective.strategic_objectives:
        if objective.objective_dimension not in dimension_objectives:
            dimension_objectives[objective.objective_dimension] = []
        dimension_objectives[objective.objective_dimension].append(objective)

    # 创建战略地图维度
    for i, dimension_name in enumerate(dimensions_order):
        map_dimension = MapDimension()
        map_dimension.dimension_name = dimension_name
        map_dimension.dimension_order = i + 1
        map_dimension.objectives = [obj.objective_id for obj in dimension_objectives.get(dimension_name, [])]
        strategy_map.map_dimensions.append(map_dimension)

    # 构建因果关系
    for relationship in bsc_data.strategy_map.causal_relationships:
        causal_relationship = CausalRelationship()
        causal_relationship.relationship_id = relationship.relationship_id
        causal_relationship.source_objective_id = relationship.source_objective_id
        causal_relationship.target_objective_id = relationship.target_objective_id
        causal_relationship.relationship_type = relationship.relationship_type
        causal_relationship.relationship_strength = relationship.relationship_strength
        strategy_map.causal_relationships.append(causal_relationship)

    # 计算价值创造路径
    value_paths = calculate_value_creation_paths(bsc_data)
    strategy_map.value_creation_paths = value_paths

    return strategy_map

def calculate_value_creation_paths(bsc_data: BalancedScorecardSchema) -> List[ValueCreationPath]:
    """计算价值创造路径"""
    paths = []

    # 从学习成长维度开始
    learning_objectives = [obj for obj in bsc_data.strategic_objective.strategic_objectives
                          if obj.objective_dimension == "Learning_Growth"]

    # 遍历每个学习成长目标
    for learning_obj in learning_objectives:
        # 查找关联的内部流程目标
        process_objectives = find_related_objectives(bsc_data, learning_obj.objective_id, "Internal_Process")

        for process_obj in process_objectives:
            # 查找关联的客户目标
            customer_objectives = find_related_objectives(bsc_data, process_obj.objective_id, "Customer")

            for customer_obj in customer_objectives:
                # 查找关联的财务目标
                financial_objectives = find_related_objectives(bsc_data, customer_obj.objective_id, "Financial")

                for financial_obj in financial_objectives:
                    # 创建价值创造路径
                    path = ValueCreationPath()
                    path.path_id = f"PATH-{learning_obj.objective_id}-{financial_obj.objective_id}"
                    path.path_name = f"{learning_obj.objective_name} → {financial_obj.objective_name}"
                    path.path_objectives = [
                        learning_obj.objective_id,
                        process_obj.objective_id,
                        customer_obj.objective_id,
                        financial_obj.objective_id
                    ]
                    path.expected_value = calculate_expected_value(bsc_data, path.path_objectives)
                    path.value_driver = learning_obj.objective_name
                    paths.append(path)

    return paths
```

---

## 4. 案例3：指标关联与监控

### 4.1 场景描述

**应用场景**：
关联指标与战略目标，监控指标执行情况。

**业务需求**：

- 支持指标与目标关联
- 支持指标值监控
- 支持指标完成率计算

### 4.2 实现代码

```python
def link_metrics_to_objectives(bsc_data: BalancedScorecardSchema, objective_id: str, metric_ids: List[str]):
    """关联指标与战略目标"""
    objective = find_objective(bsc_data, objective_id)

    for metric_id in metric_ids:
        metric = find_metric(bsc_data, metric_id)
        if metric:
            metric.objective_id = objective_id

            # 创建指标关联
            linkage = MetricLinkage()
            linkage.linkage_id = f"LINK-{objective_id}-{metric_id}"
            linkage.source_metric_id = metric_id
            linkage.target_metric_id = None  # 如果是指标间关联
            linkage.linkage_type = "Causal"
            linkage.linkage_strength = "Strong"
            linkage.linkage_direction = "Positive"
            bsc_data.metric.metric_linkages.append(linkage)

def monitor_metric_performance(bsc_data: BalancedScorecardSchema, metric_id: str) -> MetricPerformance:
    """监控指标绩效"""
    metric = find_metric(bsc_data, metric_id)
    metric_values = get_metric_values(bsc_data, metric_id)

    performance = MetricPerformance()
    performance.metric_id = metric_id
    performance.current_value = metric_values[-1].value if metric_values else 0
    performance.target_value = metric.target_value
    performance.completion_rate = (performance.current_value / metric.target_value * 100) if metric.target_value > 0 else 0

    # 计算趋势
    if len(metric_values) >= 2:
        trend = calculate_trend(metric_values)
        performance.trend_direction = trend.direction
        performance.trend_magnitude = trend.magnitude

    # 评估绩效
    if performance.completion_rate >= 100:
        performance.performance_level = "Exceeded"
    elif performance.completion_rate >= 80:
        performance.performance_level = "Met"
    elif performance.completion_rate >= 60:
        performance.performance_level = "Partially_Met"
    else:
        performance.performance_level = "Not_Met"

    return performance
```

---

## 5. 案例4：行动计划执行管理

### 5.1 场景描述

**应用场景**：
管理行动计划执行，跟踪执行进度和结果。

**业务需求**：

- 支持行动计划执行跟踪
- 支持里程碑管理
- 支持执行评估

### 5.2 实现代码

```python
def execute_action_plan(bsc_data: BalancedScorecardSchema, action_id: str, execution_data: dict):
    """执行行动计划"""
    action = find_action(bsc_data, action_id)

    execution = ActionExecution()
    execution.execution_id = f"EXEC-{action_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    execution.action_id = action_id
    execution.execution_status = "In_Progress"
    execution.execution_start_date = datetime.now().date()
    execution.execution_progress = 0

    # 更新执行状态
    bsc_data.action_plan.action_executions.append(execution)

    return execution

def update_action_progress(bsc_data: BalancedScorecardSchema, execution_id: str, progress: Decimal, milestone_id: Optional[str] = None):
    """更新行动计划进度"""
    execution = find_execution(bsc_data, execution_id)

    if execution:
        execution.execution_progress = progress

        # 更新里程碑状态
        if milestone_id:
            milestone = find_milestone(execution, milestone_id)
            if milestone:
                if progress >= calculate_milestone_progress(milestone):
                    milestone.milestone_status = "Completed"

        # 检查是否完成
        if progress >= 100:
            execution.execution_status = "Completed"
            execution.execution_end_date = datetime.now().date()

        execution.updated_at = datetime.now()

def evaluate_action_plan(bsc_data: BalancedScorecardSchema, action_id: str) -> ActionEvaluation:
    """评估行动计划"""
    action = find_action(bsc_data, action_id)
    execution = find_execution_by_action(bsc_data, action_id)

    evaluation = ActionEvaluation()
    evaluation.evaluation_id = f"EVAL-{action_id}-{datetime.now().strftime('%Y%m%d')}"
    evaluation.action_id = action_id
    evaluation.evaluation_date = datetime.now().date()

    # 评估标准
    evaluation.evaluation_criteria = [
        "执行进度",
        "预算执行",
        "质量指标",
        "时间要求"
    ]

    # 评估结果
    if execution:
        progress_score = execution.execution_progress
        budget_score = calculate_budget_score(action, execution)
        quality_score = calculate_quality_score(action, execution)
        time_score = calculate_time_score(action, execution)

        evaluation.evaluation_score = (progress_score + budget_score + quality_score + time_score) / 4

        if evaluation.evaluation_score >= 90:
            evaluation.evaluation_result = "Exceeded"
        elif evaluation.evaluation_score >= 75:
            evaluation.evaluation_result = "Met"
        elif evaluation.evaluation_score >= 60:
            evaluation.evaluation_result = "Partially_Met"
        else:
            evaluation.evaluation_result = "Not_Met"

        # 生成改进建议
        if evaluation.evaluation_score < 75:
            evaluation.improvement_recommendations = generate_improvement_recommendations(action, execution)

    bsc_data.action_plan.action_evaluations.append(evaluation)

    return evaluation
```

---

## 6. 案例5：BSC数据存储与分析系统

### 6.1 场景描述

**应用场景**：
BSC数据存储与分析系统，支持BSC元数据存储、查询、分析。

**业务需求**：

- 支持BSC元数据存储
- 支持BSC数据查询和分析
- 支持BSC报告生成

### 6.2 实现代码

```python
def store_bsc_data(bsc_data: BalancedScorecardSchema, conn):
    """存储平衡计分卡数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储战略目标
    for objective in bsc_data.strategic_objective.strategic_objectives:
        cursor.execute("""
            INSERT INTO strategic_objectives
            (objective_id, objective_name, objective_description, objective_dimension,
             objective_category, objective_priority, objective_level, parent_objective_id,
             owner, target_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (objective_id) DO UPDATE SET
            objective_name = EXCLUDED.objective_name,
            objective_description = EXCLUDED.objective_description,
            objective_priority = EXCLUDED.objective_priority,
            updated_at = CURRENT_TIMESTAMP
        """, (objective.objective_id, objective.objective_name, objective.objective_description,
              objective.objective_dimension, objective.objective_category, objective.objective_priority,
              objective.objective_level, objective.parent_objective_id, objective.owner,
              objective.target_date, objective.is_active))

    # 存储指标定义
    for metric in bsc_data.metric.metric_definitions:
        cursor.execute("""
            INSERT INTO metric_definitions
            (metric_id, metric_name, metric_description, metric_type, objective_id,
             calculation_formula, measurement_unit, target_value, baseline_value, owner)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (metric_id) DO UPDATE SET
            metric_name = EXCLUDED.metric_name,
            calculation_formula = EXCLUDED.calculation_formula,
            target_value = EXCLUDED.target_value
        """, (metric.metric_id, metric.metric_name, metric.metric_description,
              metric.metric_type, metric.objective_id, metric.calculation_formula,
              metric.measurement_unit, metric.target_value, metric.baseline_value, metric.owner))

    # 存储指标值
    for value in bsc_data.metric.metric_values:
        cursor.execute("""
            INSERT INTO metric_values
            (value_id, metric_id, value, measurement_date, completion_rate)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (value_id) DO UPDATE SET
            value = EXCLUDED.value,
            completion_rate = EXCLUDED.completion_rate
        """, (value.value_id, value.metric_id, value.value,
              value.measurement_date, value.completion_rate))

    # 存储行动计划
    for action in bsc_data.action_plan.action_definitions:
        cursor.execute("""
            INSERT INTO action_definitions
            (action_id, action_name, action_description, objective_id, action_type,
             action_priority, owner, start_date, end_date, budget)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (action_id) DO UPDATE SET
            action_name = EXCLUDED.action_name,
            action_description = EXCLUDED.action_description,
            updated_at = CURRENT_TIMESTAMP
        """, (action.action_id, action.action_name, action.action_description,
              action.objective_id, action.action_type, action.action_priority,
              action.owner, action.start_date, action.end_date, action.budget))

    # 存储行动计划执行
    for execution in bsc_data.action_plan.action_executions:
        cursor.execute("""
            INSERT INTO action_executions
            (execution_id, action_id, execution_status, execution_progress,
             execution_start_date, execution_end_date, actual_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (execution_id) DO UPDATE SET
            execution_status = EXCLUDED.execution_status,
            execution_progress = EXCLUDED.execution_progress,
            updated_at = CURRENT_TIMESTAMP
        """, (execution.execution_id, execution.action_id, execution.execution_status,
              execution.execution_progress, execution.execution_start_date,
              execution.execution_end_date, execution.actual_cost))

    # 存储因果关系
    for relationship in bsc_data.strategy_map.causal_relationships:
        cursor.execute("""
            INSERT INTO causal_relationships
            (relationship_id, source_objective_id, target_objective_id,
             relationship_type, relationship_strength, relationship_evidence)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (relationship_id) DO UPDATE SET
            relationship_type = EXCLUDED.relationship_type,
            relationship_strength = EXCLUDED.relationship_strength
        """, (relationship.relationship_id, relationship.source_objective_id,
              relationship.target_objective_id, relationship.relationship_type,
              relationship.relationship_strength, relationship.relationship_evidence))

    conn.commit()

def generate_bsc_report(conn):
    """生成平衡计分卡报表"""
    cursor = conn.cursor()

    # 查询各维度目标完成情况
    cursor.execute("""
        SELECT
            so.objective_dimension,
            COUNT(DISTINCT so.objective_id) as objective_count,
            COUNT(DISTINCT md.metric_id) as metric_count,
            AVG(mv.completion_rate) as avg_completion_rate,
            SUM(CASE WHEN mv.completion_rate >= 100 THEN 1 ELSE 0 END) as achieved_count
        FROM strategic_objectives so
        LEFT JOIN metric_definitions md ON so.objective_id = md.objective_id
        LEFT JOIN metric_values mv ON md.metric_id = mv.metric_id
        WHERE so.is_active = TRUE
        GROUP BY so.objective_dimension
        ORDER BY so.objective_dimension
    """)

    dimension_report = cursor.fetchall()

    # 查询行动计划执行情况
    cursor.execute("""
        SELECT
            ad.action_type,
            COUNT(*) as total_actions,
            SUM(CASE WHEN ae.execution_status = 'Completed' THEN 1 ELSE 0 END) as completed_actions,
            AVG(ae.execution_progress) as avg_progress,
            SUM(ad.budget) as total_budget,
            SUM(ae.actual_cost) as total_actual_cost
        FROM action_definitions ad
        LEFT JOIN action_executions ae ON ad.action_id = ae.action_id
        GROUP BY ad.action_type
        ORDER BY total_actions DESC
    """)

    action_report = cursor.fetchall()

    return {
        "dimension_report": dimension_report,
        "action_report": action_report
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
