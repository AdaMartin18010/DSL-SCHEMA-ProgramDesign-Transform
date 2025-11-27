# 管理会计Schema形式化定义

## 📑 目录

- [管理会计Schema形式化定义](#管理会计schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 责任中心Schema](#2-责任中心schema)
  - [3. 预算差异分析Schema](#3-预算差异分析schema)
  - [4. 绩效评价Schema](#4-绩效评价schema)
  - [5. 决策支持Schema](#5-决策支持schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 利润中心定理](#91-利润中心定理)
    - [9.2 投资回报率定理](#92-投资回报率定理)
    - [9.3 预算差异定理](#93-预算差异定理)

---

## 1. 形式化模型

**定义1（管理会计Schema）**：
管理会计Schema是一个四元组：

```text
Management_Accounting_Schema = (Responsibility_Center, Variance_Analysis,
                                Performance_Evaluation, Decision_Support)
```

其中：

- `Responsibility_Center`：责任中心Schema
- `Variance_Analysis`：预算差异分析Schema
- `Performance_Evaluation`：绩效评价Schema
- `Decision_Support`：决策支持Schema

---

## 2. 责任中心Schema

**定义2（责任中心Schema）**：

```text
Responsibility_Center_Schema = (Cost_Center, Profit_Center,
                               Investment_Center, Revenue_Center)
```

**形式化DSL定义**：

```dsl
schema ResponsibilityCenter {
  cost_centers: List<CostCenter> {
    cost_center_code: String @required @unique
    cost_center_name: String @required
    department: String @required
    manager: Optional<String>
    budget_amount: Decimal @default(0)
    actual_amount: Decimal @default(0)
    variance: Decimal @computed("actual_amount - budget_amount")
  }

  profit_centers: List<ProfitCenter> {
    profit_center_code: String @required @unique
    profit_center_name: String @required
    revenue: Decimal @default(0)
    costs: Decimal @default(0)
    profit: Decimal @computed("revenue - costs")
    profit_margin: Decimal @computed("profit / revenue * 100")
  }

  investment_centers: List<InvestmentCenter> {
    investment_center_code: String @required @unique
    investment_center_name: String @required
    investment_amount: Decimal @required @range(0, null)
    net_income: Decimal @default(0)
    roi: Decimal @computed("net_income / investment_amount * 100")
  }

  revenue_centers: List<RevenueCenter> {
    revenue_center_code: String @required @unique
    revenue_center_name: String @required
    revenue_target: Decimal @required @range(0, null)
    actual_revenue: Decimal @default(0)
    revenue_variance: Decimal @computed("actual_revenue - revenue_target")
  }
} @standard("Balanced Scorecard")
```

---

## 3. 预算差异分析Schema

**定义3（预算差异分析Schema）**：

```text
Variance_Analysis_Schema = (Budget_Variance, Volume_Variance,
                           Price_Variance, Efficiency_Variance)
```

**形式化DSL定义**：

```dsl
schema VarianceAnalysis {
  budget_variance: BudgetVariance {
    variance_id: String @required @unique
    cost_center_code: String @required
    account_code: String @required
    budget_amount: Decimal @required
    actual_amount: Decimal @required
    variance_amount: Decimal @computed("actual_amount - budget_amount")
    variance_percentage: Decimal @computed("variance_amount / budget_amount * 100")
  }

  volume_variance: VolumeVariance {
    variance_id: String @required @unique
    budget_volume: Decimal @required
    actual_volume: Decimal @required
    standard_price: Decimal @required
    variance_amount: Decimal @computed("(actual_volume - budget_volume) * standard_price")
  }

  price_variance: PriceVariance {
    variance_id: String @required @unique
    budget_price: Decimal @required
    actual_price: Decimal @required
    actual_volume: Decimal @required
    variance_amount: Decimal @computed("(actual_price - budget_price) * actual_volume")
  }

  efficiency_variance: EfficiencyVariance {
    variance_id: String @required @unique
    budget_hours: Decimal @required
    actual_hours: Decimal @required
    standard_rate: Decimal @required
    variance_amount: Decimal @computed("(actual_hours - budget_hours) * standard_rate")
  }
} @standard("Variance Analysis")
```

---

## 4. 绩效评价Schema

**定义4（绩效评价Schema）**：

```text
Performance_Evaluation_Schema = (KPI_Definition, Performance_Metric,
                                Performance_Score, Performance_Report)
```

**形式化DSL定义**：

```dsl
schema PerformanceEvaluation {
  kpi_definitions: List<KPIDefinition> {
    kpi_id: String @required @unique
    kpi_name: String @required
    kpi_type: Enum { Financial, Customer, Process, Learning } @required
    target_value: Decimal @required
    calculation_formula: String @required
    measurement_unit: String @required
  }

  performance_metrics: List<PerformanceMetric> {
    metric_id: String @required @unique
    kpi_id: String @required
    metric_value: Decimal @required
    measurement_date: Date @required
    measurement_unit: String @required
  }

  performance_scores: List<PerformanceScore> {
    score_id: String @required @unique
    kpi_id: String @required
    score_value: Decimal @required @range(0, 100)
    score_level: Enum { Excellent, Good, Average, Poor } @computed
    score_rank: Int
  }

  performance_reports: List<PerformanceReport> {
    report_id: String @required @unique
    report_period_start: Date @required
    report_period_end: Date @required
    report_type: Enum { Summary, Detailed, Dashboard } @required
    report_data: Map<String, Decimal>
  }
} @standard("KPI", "Balanced Scorecard")
```

---

## 5. 决策支持Schema

**定义5（决策支持Schema）**：

```text
Decision_Support_Schema = (Relevant_Cost, Opportunity_Cost,
                          Sunk_Cost, Decision_Model)
```

**形式化DSL定义**：

```dsl
schema DecisionSupport {
  relevant_costs: List<RelevantCost> {
    cost_id: String @required @unique
    cost_type: Enum { Variable, Fixed, Incremental } @required
    cost_amount: Decimal @required
    decision_impact: Enum { Positive, Negative, Neutral } @required
  }

  opportunity_costs: List<OpportunityCost> {
    cost_id: String @required @unique
    opportunity_type: String @required
    opportunity_amount: Decimal @required
    opportunity_loss: Decimal @required
  }

  sunk_costs: List<SunkCost> {
    cost_id: String @required @unique
    cost_type: String @required
    cost_amount: Decimal @required
    is_recoverable: Boolean @default(false)
  }

  decision_models: List<DecisionModel> {
    model_id: String @required @unique
    model_type: Enum { NPV, IRR, Payback, BreakEven } @required
    decision_variables: Map<String, Decimal>
    decision_result: Decimal @computed
    decision_recommendation: Enum { Accept, Reject, Defer } @computed
  }
} @standard("Decision Support")
```

---

## 6. 类型系统

**定义6（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date,
               Enum, List, Map, Object, Optional}
```

---

## 7. 约束规则

**定义7（约束规则）**：

1. **唯一性约束**：`cost_center_code`、`kpi_id`、`variance_id`等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：`@range(min, max)`限制数值范围
4. **计算约束**：`@computed(expression)`计算字段值
5. **绩效评分约束**：绩效得分范围0-100

---

## 8. 转换函数

**定义8（转换函数）**：

```text
转换函数集合 = {
  convert_to_balanced_scorecard: Management_Accounting_Schema → Balanced_Scorecard_Format,
  convert_to_kpi: Management_Accounting_Schema → KPI_Format,
  convert_to_database: Management_Accounting_Schema → PostgreSQL_Schema
}
```

---

## 9. 形式化定理

### 9.1 利润中心定理

**定理1（利润中心）**：
利润等于收入减去成本：

```text
Profit = Revenue - Costs
```

### 9.2 投资回报率定理

**定理2（投资回报率）**：
投资回报率等于净收入除以投资额：

```text
ROI = Net_Income / Investment_Amount × 100%
```

### 9.3 预算差异定理

**定理3（预算差异）**：
预算差异等于实际金额减去预算金额：

```text
Budget_Variance = Actual_Amount - Budget_Amount
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
