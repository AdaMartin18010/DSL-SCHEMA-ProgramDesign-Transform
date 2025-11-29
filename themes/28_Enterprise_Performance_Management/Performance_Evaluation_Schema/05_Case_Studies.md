# 绩效评估Schema实践案例

## 📑 目录

- [绩效评估Schema实践案例](#绩效评估schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业员工年度绩效评估系统](#2-案例1企业员工年度绩效评估系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)
  - [4. 案例3：绩效评估到OLAP Cube转换](#4-案例3绩效评估到olap-cube转换)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：绩效改进计划系统](#5-案例4绩效改进计划系统)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：绩效评估数据存储与分析系统](#6-案例5绩效评估数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供绩效评估Schema在实际企业应用中的实践案例，涵盖员工年度绩效评估、360度评估、绩效改进计划等真实场景。

**案例类型**：

1. **企业员工年度绩效评估系统**：年度绩效评估
2. **360度评估系统**：多维度评估
3. **绩效评估到OLAP Cube转换工具**：绩效数据到OLAP转换
4. **绩效改进计划系统**：绩效改进计划管理
5. **绩效评估数据存储与分析系统**：绩效数据分析和监控

**参考企业案例**：

- **绩效评估最佳实践**：SHRM绩效管理指南
- **360度评估**：HR.com评估指南

---

## 2. 案例1：企业员工年度绩效评估系统

### 2.1 业务背景

**企业背景**：
某制造企业需要构建员工年度绩效评估系统，对员工进行年度绩效评估，包括目标完成情况、能力评估、行为评估等，为人力资源管理提供数据支持。

**业务痛点**：

1. **评估流程不规范**：评估流程不规范
2. **评估标准不统一**：评估标准不统一
3. **评估效率低**：评估效率低
4. **反馈机制缺失**：缺乏评估反馈机制

**业务目标**：

- 规范评估流程
- 统一评估标准
- 提高评估效率
- 建立反馈机制

### 2.2 技术挑战

1. **评估周期管理**：管理评估周期
2. **多维度评估**：支持多维度评估
3. **评估结果计算**：计算评估结果
4. **反馈机制**：建立评估反馈机制

### 2.3 解决方案

**使用Schema定义员工年度绩效评估系统**：

### 2.4 完整代码实现

**员工年度绩效评估Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
绩效评估Schema实现
"""

from typing import Dict, List, Optional
from datetime import date, datetime
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum

class CycleType(str, Enum):
    """周期类型"""
    ANNUAL = "Annual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"

class EvaluationLevel(str, Enum):
    """评估等级"""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    BELOW_AVERAGE = "BelowAverage"
    POOR = "Poor"

@dataclass
class EvaluationCycle:
    """评估周期"""
    cycle_id: str
    cycle_name: str
    cycle_type: CycleType
    cycle_start_date: date
    cycle_end_date: date
    evaluation_start_date: date
    evaluation_end_date: date
    evaluation_deadline: date
    status: str = "Draft"  # Draft, Active, Completed

@dataclass
class EvaluationObject:
    """评估对象"""
    object_id: str
    object_name: str
    object_type: str = "Employee"
    object_level: str = "Individual"
    department_id: str = ""
    position: str = ""

@dataclass
class EvaluationResult:
    """评估结果"""
    result_id: str
    cycle_id: str
    object_id: str
    evaluator_id: str
    evaluator_type: str = "Manager"
    total_score: Decimal = Decimal('0')
    weighted_score: Decimal = Decimal('0')
    evaluation_level: EvaluationLevel = EvaluationLevel.AVERAGE
    evaluation_date: date = field(default_factory=date.today)
    comments: Optional[str] = None

    def calculate_level(self):
        """计算评估等级"""
        if self.weighted_score >= Decimal('90'):
            self.evaluation_level = EvaluationLevel.EXCELLENT
        elif self.weighted_score >= Decimal('80'):
            self.evaluation_level = EvaluationLevel.GOOD
        elif self.weighted_score >= Decimal('70'):
            self.evaluation_level = EvaluationLevel.AVERAGE
        elif self.weighted_score >= Decimal('60'):
            self.evaluation_level = EvaluationLevel.BELOW_AVERAGE
        else:
            self.evaluation_level = EvaluationLevel.POOR

@dataclass
class EmployeeAnnualEvaluation:
    """员工年度绩效评估"""
    evaluation_cycle: EvaluationCycle
    evaluation_objects: Dict[str, EvaluationObject] = field(default_factory=dict)
    evaluation_results: Dict[str, EvaluationResult] = field(default_factory=dict)

    def add_evaluation_object(self, obj: EvaluationObject):
        """添加评估对象"""
        self.evaluation_objects[obj.object_id] = obj

    def add_evaluation_result(self, result: EvaluationResult):
        """添加评估结果"""
        result.calculate_level()
        self.evaluation_results[result.result_id] = result

    def get_evaluation_summary(self) -> Dict:
        """获取评估摘要"""
        total_objects = len(self.evaluation_objects)
        completed_results = len(self.evaluation_results)

        level_distribution = {}
        for result in self.evaluation_results.values():
            level = result.evaluation_level.value
            level_distribution[level] = level_distribution.get(level, 0) + 1

        return {
            'cycle_id': self.evaluation_cycle.cycle_id,
            'cycle_name': self.evaluation_cycle.cycle_name,
            'total_objects': total_objects,
            'completed_results': completed_results,
            'completion_rate': float(completed_results / total_objects * 100) if total_objects > 0 else 0,
            'level_distribution': level_distribution,
            'average_score': float(sum(r.weighted_score for r in self.evaluation_results.values()) / completed_results) if completed_results > 0 else 0
        }

# 使用示例
if __name__ == '__main__':
    # 创建评估周期
    cycle = EvaluationCycle(
        cycle_id="CYC-2025-ANNUAL",
        cycle_name="2025年度绩效评估",
        cycle_type=CycleType.ANNUAL,
        cycle_start_date=date(2025, 1, 1),
        cycle_end_date=date(2025, 12, 31),
        evaluation_start_date=date(2025, 12, 1),
        evaluation_end_date=date(2025, 12, 31),
        evaluation_deadline=date(2026, 1, 15)
    )

    # 创建评估系统
    evaluation = EmployeeAnnualEvaluation(evaluation_cycle=cycle)

    # 添加评估对象
    employee = EvaluationObject(
        object_id="OBJ-EMP-001",
        object_name="张三",
        department_id="DEPT-SALES",
        position="销售经理"
    )
    evaluation.add_evaluation_object(employee)

    # 添加评估结果
    result = EvaluationResult(
        result_id="RES-2025-001",
        cycle_id=cycle.cycle_id,
        object_id=employee.object_id,
        evaluator_id="MGR-001",
        total_score=Decimal('85.5'),
        weighted_score=Decimal('85.5')
    )
    evaluation.add_evaluation_result(result)

    # 获取评估摘要
    summary = evaluation.get_evaluation_summary()
    print(f"评估摘要: {summary}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 评估流程规范性 | 60% | 100% | 40%提升 |
| 评估标准统一性 | 70% | 100% | 30%提升 |
| 评估效率 | 低 | 高 | 显著提升 |
| 反馈机制完整性 | 40% | 100% | 60%提升 |

**业务价值**：

1. **评估流程规范**：规范评估流程
2. **评估标准统一**：统一评估标准
3. **评估效率提高**：提高评估效率
4. **反馈机制建立**：建立评估反馈机制

**经验教训**：

1. 评估周期管理很重要
2. 多维度评估需要合理设计
3. 评估结果计算需要准确
4. 反馈机制需要完善

**参考案例**：

- [绩效评估最佳实践](https://www.shrm.org/)
- [360度评估指南](https://www.hr.com/)
  }
}

```

---

## 3. 案例2：360度评估系统

### 3.1 场景描述

**应用场景**：
构建360度评估系统，支持多维度评估和综合评估。

**业务需求**：

- 支持多维度评估
- 支持匿名评估
- 支持综合评估结果

### 3.2 实现代码

```python
def conduct_360_evaluation(eval_data: PerformanceEvaluationSchema, object_id: str, cycle_id: str) -> EvaluationResult:
    """执行360度评估"""
    # 获取评估对象
    obj = find_object(eval_data, object_id)

    # 收集各维度评估
    evaluations = []

    # 1. 自我评估
    self_eval = conduct_self_evaluation(eval_data, object_id, cycle_id)
    evaluations.append(self_eval)

    # 2. 上级评估
    if obj.manager_id:
        manager_eval = conduct_manager_evaluation(eval_data, object_id, obj.manager_id, cycle_id)
        evaluations.append(manager_eval)

    # 3. 同级评估
    peer_evals = conduct_peer_evaluations(eval_data, object_id, cycle_id)
    evaluations.extend(peer_evals)

    # 4. 下级评估
    subordinate_evals = conduct_subordinate_evaluations(eval_data, object_id, cycle_id)
    evaluations.extend(subordinate_evals)

    # 5. 客户评估（如适用）
    if obj.object_type == "Employee" and is_customer_facing(obj):
        customer_evals = conduct_customer_evaluations(eval_data, object_id, cycle_id)
        evaluations.extend(customer_evals)

    # 综合评估结果
    comprehensive_result = aggregate_evaluation_results(evaluations)

    return comprehensive_result

def aggregate_evaluation_results(evaluations: List[EvaluationResult]) -> EvaluationResult:
    """综合评估结果"""
    comprehensive_result = EvaluationResult()
    comprehensive_result.result_id = f"RES-360-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    comprehensive_result.evaluator_type = "360"
    comprehensive_result.evaluation_date = datetime.now().date()

    # 计算加权平均分
    weights = {
        "Self": 0.1,
        "Manager": 0.4,
        "Peer": 0.3,
        "Subordinate": 0.15,
        "Customer": 0.05
    }

    weighted_sum = 0
    total_weight = 0

    for eval_result in evaluations:
        weight = weights.get(eval_result.evaluator_type, 0.1)
        weighted_sum += eval_result.total_score * weight
        total_weight += weight

    comprehensive_result.total_score = weighted_sum / total_weight if total_weight > 0 else 0
    comprehensive_result.weighted_score = comprehensive_result.total_score

    # 确定评估等级
    if comprehensive_result.total_score >= 90:
        comprehensive_result.evaluation_level = "Excellent"
    elif comprehensive_result.total_score >= 75:
        comprehensive_result.evaluation_level = "Good"
    elif comprehensive_result.total_score >= 60:
        comprehensive_result.evaluation_level = "Average"
    else:
        comprehensive_result.evaluation_level = "Poor"

    return comprehensive_result
```

---

## 4. 案例3：绩效评估到OLAP Cube转换

### 4.1 场景描述

**应用场景**：
将绩效评估Schema转换为OLAP Cube格式，用于多维分析。

**业务需求**：

- 支持绩效评估多维分析
- 支持评估趋势分析
- 支持评估对比分析

### 4.2 实现代码

```python
def convert_performance_evaluation_to_olap_cube_complete(eval_data: PerformanceEvaluationSchema) -> OLAPCube:
    """完整转换绩效评估Schema到OLAP Cube"""
    cube = OLAPCube()
    cube.name = "Performance_Evaluation_Cube"

    # 创建时间维度
    time_dimension = Dimension()
    time_dimension.name = "Time"
    time_dimension.hierarchies = [{
        "name": "Calendar",
        "levels": ["Year", "Quarter", "Month"]
    }]
    cube.dimensions.append(time_dimension)

    # 创建评估对象维度
    object_dimension = Dimension()
    object_dimension.name = "Evaluation_Object"
    object_dimension.attributes = ["Object_Type", "Department", "Position", "Level"]
    object_dimension.hierarchies = [{
        "name": "Org_Hierarchy",
        "levels": ["Organization", "Department", "Team", "Individual"]
    }]
    cube.dimensions.append(object_dimension)

    # 创建评估者维度
    evaluator_dimension = Dimension()
    evaluator_dimension.name = "Evaluator"
    evaluator_dimension.attributes = ["Evaluator_Type", "Department", "Position"]
    cube.dimensions.append(evaluator_dimension)

    # 创建评估周期维度
    cycle_dimension = Dimension()
    cycle_dimension.name = "Evaluation_Cycle"
    cycle_dimension.attributes = ["Cycle_Type", "Cycle_Name"]
    cube.dimensions.append(cycle_dimension)

    # 创建评估等级维度
    level_dimension = Dimension()
    level_dimension.name = "Evaluation_Level"
    level_dimension.attributes = ["Level"]
    cube.dimensions.append(level_dimension)

    # 创建度量
    measures = [
        {"name": "Total_Score", "function": "AVG", "type": "Decimal"},
        {"name": "Weighted_Score", "function": "AVG", "type": "Decimal"},
        {"name": "Evaluation_Count", "function": "COUNT", "type": "Integer"},
        {"name": "Excellent_Count", "function": "COUNT", "type": "Integer"},
        {"name": "Good_Count", "function": "COUNT", "type": "Integer"}
    ]

    for measure_def in measures:
        measure = Measure()
        measure.name = measure_def["name"]
        measure.aggregation_function = measure_def["function"]
        measure.data_type = measure_def["type"]
        cube.measures.append(measure)

    # 转换评估结果为事实数据
    for result in eval_data.evaluation_result.evaluation_results:
        cycle = find_cycle(eval_data, result.cycle_id)
        obj = find_object(eval_data, result.object_id)

        fact = Fact()
        fact.dimensions = {
            "Time": {
                "Year": cycle.cycle_start_date.year,
                "Quarter": get_quarter(cycle.cycle_start_date),
                "Month": cycle.cycle_start_date.month
            },
            "Evaluation_Object": {
                "Object_Type": obj.object_type,
                "Department": obj.department_id,
                "Position": obj.position,
                "Level": obj.object_level,
                "Organization": extract_organization(obj),
                "Team": extract_team(obj)
            },
            "Evaluator": {
                "Evaluator_Type": result.evaluator_type,
                "Department": find_evaluator_department(eval_data, result.evaluator_id),
                "Position": find_evaluator_position(eval_data, result.evaluator_id)
            },
            "Evaluation_Cycle": {
                "Cycle_Type": cycle.cycle_type,
                "Cycle_Name": cycle.cycle_name
            },
            "Evaluation_Level": {
                "Level": result.evaluation_level
            }
        }
        fact.measures = {
            "Total_Score": result.total_score,
            "Weighted_Score": result.weighted_score,
            "Evaluation_Count": 1,
            "Excellent_Count": 1 if result.evaluation_level == "Excellent" else 0,
            "Good_Count": 1 if result.evaluation_level == "Good" else 0
        }
        cube.facts.append(fact)

    return cube
```

---

## 5. 案例4：绩效改进计划系统

### 5.1 场景描述

**应用场景**：
基于绩效评估结果生成改进建议和行动计划。

**业务需求**：

- 支持改进建议生成
- 支持行动计划制定
- 支持行动计划跟踪

### 5.2 实现代码

```python
def generate_improvement_plan(eval_data: PerformanceEvaluationSchema, result_id: str) -> ImprovementPlan:
    """生成绩效改进计划"""
    result = find_result(eval_data, result_id)
    criteria_scores = get_criteria_scores(eval_data, result_id)

    improvement_plan = ImprovementPlan()
    improvement_plan.plan_id = f"PLAN-{result_id}"
    improvement_plan.result_id = result_id

    # 分析低分项
    low_scores = [score for score in criteria_scores if score.score_value < 70]

    recommendations = []
    for low_score in low_scores:
        criteria = find_criteria(eval_data, low_score.criteria_id)

        recommendation = ImprovementRecommendation()
        recommendation.recommendation_id = f"REC-{low_score.score_id}"
        recommendation.result_id = result_id
        recommendation.recommendation_content = generate_recommendation_content(criteria, low_score)
        recommendation.recommendation_priority = "High" if low_score.score_value < 60 else "Medium"
        recommendation.recommendation_category = map_criteria_to_category(criteria.criteria_type)
        recommendation.recommendation_owner = find_result_owner(eval_data, result_id)
        recommendation.target_completion_date = calculate_target_date(datetime.now(), recommendation.recommendation_priority)

        recommendations.append(recommendation)

    improvement_plan.recommendations = recommendations

    # 生成行动计划
    action_plans = []
    for recommendation in recommendations:
        action_plan = ActionPlan()
        action_plan.plan_id = f"ACT-{recommendation.recommendation_id}"
        action_plan.result_id = result_id
        action_plan.plan_name = f"改进计划-{recommendation.recommendation_category}"
        action_plan.plan_description = recommendation.recommendation_content
        action_plan.plan_owner = recommendation.recommendation_owner
        action_plan.plan_start_date = datetime.now().date()
        action_plan.plan_end_date = recommendation.target_completion_date
        action_plan.plan_status = "Not_Started"
        action_plan.related_recommendations = [recommendation.recommendation_id]

        action_plans.append(action_plan)

    improvement_plan.action_plans = action_plans

    return improvement_plan
```

---

## 6. 案例5：绩效评估数据存储与分析系统

### 6.1 场景描述

**应用场景**：
绩效评估数据存储与分析系统，支持评估元数据存储、查询、分析。

**业务需求**：

- 支持评估元数据存储
- 支持评估数据查询和分析
- 支持评估报告生成

### 6.2 实现代码

```python
def store_performance_evaluation_data(eval_data: PerformanceEvaluationSchema, conn):
    """存储绩效评估数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储评估周期
    for cycle in eval_data.evaluation_cycle.evaluation_cycles:
        cursor.execute("""
            INSERT INTO evaluation_cycles
            (cycle_id, cycle_name, cycle_type, cycle_start_date, cycle_end_date,
             evaluation_start_date, evaluation_end_date, evaluation_deadline, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cycle_id) DO UPDATE SET
            cycle_name = EXCLUDED.cycle_name,
            evaluation_deadline = EXCLUDED.evaluation_deadline,
            updated_at = CURRENT_TIMESTAMP
        """, (cycle.cycle_id, cycle.cycle_name, cycle.cycle_type,
              cycle.cycle_start_date, cycle.cycle_end_date,
              cycle.evaluation_start_date, cycle.evaluation_end_date,
              cycle.evaluation_deadline, cycle.is_active))

    # 存储评估对象
    for obj in eval_data.evaluation_object.evaluation_objects:
        cursor.execute("""
            INSERT INTO evaluation_objects
            (object_id, object_name, object_type, object_level, parent_object_id,
             manager_id, department_id, position, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (object_id) DO UPDATE SET
            object_name = EXCLUDED.object_name,
            manager_id = EXCLUDED.manager_id,
            department_id = EXCLUDED.department_id,
            position = EXCLUDED.position
        """, (obj.object_id, obj.object_name, obj.object_type, obj.object_level,
              obj.parent_object_id, obj.manager_id, obj.department_id,
              obj.position, obj.is_active))

    # 存储评估结果
    for result in eval_data.evaluation_result.evaluation_results:
        cursor.execute("""
            INSERT INTO evaluation_results
            (result_id, cycle_id, object_id, evaluator_id, evaluator_type,
             evaluation_date, total_score, weighted_score, evaluation_level, evaluation_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (result_id) DO UPDATE SET
            total_score = EXCLUDED.total_score,
            weighted_score = EXCLUDED.weighted_score,
            evaluation_level = EXCLUDED.evaluation_level,
            evaluation_status = EXCLUDED.evaluation_status
        """, (result.result_id, result.cycle_id, result.object_id,
              result.evaluator_id, result.evaluator_type, result.evaluation_date,
              result.total_score, result.weighted_score, result.evaluation_level,
              result.evaluation_status))

        # 存储标准分数
        for criteria_score in get_criteria_scores_for_result(eval_data, result.result_id):
            cursor.execute("""
                INSERT INTO criteria_scores
                (score_id, result_id, criteria_id, score_value, score_comment)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (score_id) DO UPDATE SET
                score_value = EXCLUDED.score_value,
                score_comment = EXCLUDED.score_comment
            """, (criteria_score.score_id, criteria_score.result_id,
                  criteria_score.criteria_id, criteria_score.score_value,
                  criteria_score.score_comment))

    # 存储评估反馈
    for feedback in eval_data.evaluation_feedback.evaluation_feedbacks:
        cursor.execute("""
            INSERT INTO evaluation_feedbacks
            (feedback_id, result_id, feedback_type, feedback_content, feedback_date, feedback_provider)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (feedback_id) DO UPDATE SET
            feedback_content = EXCLUDED.feedback_content
        """, (feedback.feedback_id, feedback.result_id, feedback.feedback_type,
              feedback.feedback_content, feedback.feedback_date, feedback.feedback_provider))

    # 存储改进建议
    for recommendation in eval_data.evaluation_feedback.improvement_recommendations:
        cursor.execute("""
            INSERT INTO improvement_recommendations
            (recommendation_id, result_id, recommendation_content, recommendation_priority,
             recommendation_category, recommendation_owner, target_completion_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (recommendation_id) DO UPDATE SET
            recommendation_content = EXCLUDED.recommendation_content,
            target_completion_date = EXCLUDED.target_completion_date
        """, (recommendation.recommendation_id, recommendation.result_id,
              recommendation.recommendation_content, recommendation.recommendation_priority,
              recommendation.recommendation_category, recommendation.recommendation_owner,
              recommendation.target_completion_date))

    conn.commit()

def generate_performance_evaluation_report(conn, cycle_id: str):
    """生成绩效评估报表"""
    cursor = conn.cursor()

    # 查询评估结果汇总
    cursor.execute("""
        SELECT
            eo.object_type,
            er.evaluator_type,
            COUNT(*) as evaluation_count,
            AVG(er.total_score) as avg_total_score,
            AVG(er.weighted_score) as avg_weighted_score,
            COUNT(CASE WHEN er.evaluation_level = 'Excellent' THEN 1 END) as excellent_count,
            COUNT(CASE WHEN er.evaluation_level = 'Good' THEN 1 END) as good_count,
            COUNT(CASE WHEN er.evaluation_level = 'Average' THEN 1 END) as average_count,
            COUNT(CASE WHEN er.evaluation_level = 'Poor' THEN 1 END) as poor_count
        FROM evaluation_results er
        JOIN evaluation_objects eo ON er.object_id = eo.object_id
        WHERE er.cycle_id = %s AND er.evaluation_status = 'Approved'
        GROUP BY eo.object_type, er.evaluator_type
        ORDER BY eo.object_type, er.evaluator_type
    """, (cycle_id,))

    evaluation_summary = cursor.fetchall()

    # 查询评估分数分布
    cursor.execute("""
        SELECT
            er.evaluation_level,
            COUNT(*) as count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM evaluation_results WHERE cycle_id = %s AND evaluation_status = 'Approved') as percentage
        FROM evaluation_results er
        WHERE er.cycle_id = %s AND er.evaluation_status = 'Approved'
        GROUP BY er.evaluation_level
        ORDER BY
            CASE er.evaluation_level
                WHEN 'Excellent' THEN 1
                WHEN 'Good' THEN 2
                WHEN 'Average' THEN 3
                WHEN 'Poor' THEN 4
            END
    """, (cycle_id, cycle_id))

    score_distribution = cursor.fetchall()

    # 查询改进建议汇总
    cursor.execute("""
        SELECT
            ir.recommendation_category,
            ir.recommendation_priority,
            COUNT(*) as recommendation_count,
            COUNT(CASE WHEN ir.target_completion_date < CURRENT_DATE THEN 1 END) as overdue_count
        FROM improvement_recommendations ir
        JOIN evaluation_results er ON ir.result_id = er.result_id
        WHERE er.cycle_id = %s
        GROUP BY ir.recommendation_category, ir.recommendation_priority
        ORDER BY recommendation_count DESC
    """, (cycle_id,))

    recommendation_summary = cursor.fetchall()

    return {
        "evaluation_summary": evaluation_summary,
        "score_distribution": score_distribution,
        "recommendation_summary": recommendation_summary
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
