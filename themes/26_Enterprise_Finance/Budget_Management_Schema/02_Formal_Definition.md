# 预算管理Schema形式化定义

## 📑 目录

- [预算管理Schema形式化定义](#预算管理schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 预算编制Schema](#2-预算编制schema)
  - [3. 预算执行Schema](#3-预算执行schema)
  - [4. 预算控制Schema](#4-预算控制schema)
  - [5. 预算分析Schema](#5-预算分析schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 预算平衡定理](#91-预算平衡定理)
    - [9.2 预算执行定理](#92-预算执行定理)
    - [9.3 预算差异定理](#93-预算差异定理)

---

## 1. 形式化模型

**定义1（预算管理Schema）**：
预算管理Schema是一个四元组：

```text
Budget_Management_Schema = (Budget_Planning, Budget_Execution,
                            Budget_Control, Budget_Analysis)
```

其中：

- `Budget_Planning`：预算编制Schema
- `Budget_Execution`：预算执行Schema
- `Budget_Control`：预算控制Schema
- `Budget_Analysis`：预算分析Schema

---

## 2. 预算编制Schema

**定义2（预算编制Schema）**：

```text
Budget_Planning_Schema = (Budget_Period, Budget_Template,
                         Budget_Version, Budget_Scenario)
```

**形式化DSL定义**：

```dsl
schema BudgetPlanning {
  budget_periods: List<BudgetPeriod> {
    period_id: String @required @unique
    period_type: Enum { Annual, Quarterly, Monthly } @required
    period_start: Date @required
    period_end: Date @required
    fiscal_year: String @required
  }

  budget_templates: List<BudgetTemplate> {
    template_id: String @required @unique
    template_name: String @required
    account_structure: List<AccountCode> @required
    budget_rules: List<BudgetRule>
    is_active: Boolean @default(true)
  }

  budget_versions: List<BudgetVersion> {
    version_id: String @required @unique
    version_name: String @required
    version_type: Enum { Initial, Revised, Approved } @required
    base_version: Optional<String>
    created_date: Date @required
    approved_date: Optional<Date>
  }

  budget_scenarios: List<BudgetScenario> {
    scenario_id: String @required @unique
    scenario_name: String @required
    scenario_type: Enum { Base, Optimistic, Pessimistic } @required
    assumptions: Map<String, String>
    probability: Decimal @range(0, 100)
  }
} @standard("EPM", "ZBB")
```

---

## 3. 预算执行Schema

**定义3（预算执行Schema）**：

```text
Budget_Execution_Schema = (Budget_Allocation, Budget_Commitment,
                          Budget_Expenditure, Budget_Encumbrance)
```

**形式化DSL定义**：

```dsl
schema BudgetExecution {
  budget_allocations: List<BudgetAllocation> {
    allocation_id: String @required @unique
    budget_version_id: String @required
    cost_center_code: String @required
    account_code: String @required
    allocated_amount: Decimal @required @range(0, null)
    allocation_date: Date @required
  }

  budget_commitments: List<BudgetCommitment> {
    commitment_id: String @required @unique
    allocation_id: String @required
    commitment_type: Enum { PurchaseOrder, Contract } @required
    reference_number: String @required
    committed_amount: Decimal @required @range(0, null)
    commitment_date: Date @required
  }

  budget_expenditures: List<BudgetExpenditure> {
    expenditure_id: String @required @unique
    allocation_id: String @required
    expenditure_type: Enum { Actual, Paid } @required
    reference_number: String @required
    expenditure_amount: Decimal @required @range(0, null)
    expenditure_date: Date @required
  }

  budget_encumbrances: List<BudgetEncumbrance> {
    encumbrance_id: String @required @unique
    allocation_id: String @required
    encumbrance_amount: Decimal @required @range(0, null)
    encumbrance_reason: String
    encumbrance_date: Date @required
  }
} @standard("EPM")
```

---

## 4. 预算控制Schema

**定义4（预算控制Schema）**：

```text
Budget_Control_Schema = (Budget_Limit, Budget_Approval,
                        Budget_Violation, Budget_Adjustment)
```

**形式化DSL定义**：

```dsl
schema BudgetControl {
  budget_limits: List<BudgetLimit> {
    limit_id: String @required @unique
    allocation_id: String @required
    limit_type: Enum { Hard, Soft, Warning } @required
    limit_amount: Decimal @required @range(0, null)
    warning_threshold: Decimal @default(0.8) @range(0, 1)
  }

  budget_approvals: List<BudgetApproval> {
    approval_id: String @required @unique
    request_id: String @required
    approver_id: String @required
    approval_level: Int @required @range(1, 10)
    approval_status: Enum { Pending, Approved, Rejected } @required
    approval_date: Optional<Date>
    approval_comment: Optional<String>
  }

  budget_violations: List<BudgetViolation> {
    violation_id: String @required @unique
    allocation_id: String @required
    violation_type: Enum { OverBudget, Unauthorized } @required
    violation_amount: Decimal @required
    violation_date: Date @required
    violation_reason: String
    resolution_status: Enum { Open, Resolved, Escalated } @default("Open")
  }

  budget_adjustments: List<BudgetAdjustment> {
    adjustment_id: String @required @unique
    allocation_id: String @required
    adjustment_type: Enum { Increase, Decrease, Transfer } @required
    adjustment_amount: Decimal @required
    adjustment_reason: String @required
    adjustment_date: Date @required
    approval_status: Enum { Pending, Approved, Rejected } @default("Pending")
  }
} @standard("EPM", "BPM")
```

---

## 5. 预算分析Schema

**定义5（预算分析Schema）**：

```text
Budget_Analysis_Schema = (Budget_Variance, Budget_Trends,
                         Budget_Forecasts, Budget_Reports)
```

**形式化DSL定义**：

```dsl
schema BudgetAnalysis {
  budget_variance: BudgetVariance {
    variance_id: String @required @unique
    allocation_id: String @required
    period_end: Date @required
    budget_amount: Decimal @required
    actual_amount: Decimal @required
    variance_amount: Decimal @computed("actual_amount - budget_amount")
    variance_percentage: Decimal @computed("variance_amount / budget_amount * 100")
    variance_reason: Optional<String>
  }

  budget_trends: BudgetTrends {
    trend_id: String @required @unique
    allocation_id: String @required
    trend_period_start: Date @required
    trend_period_end: Date @required
    trend_data_points: List<TrendDataPoint> {
      period: Date @required
      budget_amount: Decimal @required
      actual_amount: Decimal @required
      variance_amount: Decimal @computed("actual_amount - budget_amount")
    }
    trend_direction: Enum { Increasing, Decreasing, Stable } @computed
  }

  budget_forecasts: BudgetForecasts {
    forecast_id: String @required @unique
    allocation_id: String @required
    forecast_method: Enum { Linear, Exponential, MovingAverage } @required
    forecast_period_start: Date @required
    forecast_period_end: Date @required
    forecast_amount: Decimal @required
    confidence_level: Decimal @range(0, 100)
    historical_accuracy: Decimal @range(0, 100)
  }

  budget_reports: BudgetReports {
    execution_report: BudgetExecutionReport {
      report_period_start: Date @required
      report_period_end: Date @required
      total_budget: Decimal @required
      total_allocated: Decimal @required
      total_committed: Decimal @required
      total_expended: Decimal @required
      available_budget: Decimal @computed("total_budget - total_committed - total_expended")
    }
    variance_report: BudgetVarianceReport {
      report_period_end: Date @required
      variance_items: List<VarianceItem> {
        allocation_id: String @required
        variance_amount: Decimal @required
        variance_percentage: Decimal @required
      }
    }
  }
} @standard("EPM", "BPM")
```

---

## 6. 类型系统

**定义6（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date,
               Enum, List, Map, Object, Optional}
```

**类型约束**：

- `String`：字符串类型，支持模式匹配
- `Decimal`：十进制数值类型，支持精度控制
- `Date`：日期类型，格式：YYYY-MM-DD
- `Enum`：枚举类型，限定值集合
- `List<T>`：列表类型，元素类型为T
- `Map<K, V>`：映射类型，键类型为K，值类型为V
- `Optional<T>`：可选类型，值可为空

---

## 7. 约束规则

**定义7（约束规则）**：

1. **唯一性约束**：`period_id`、`template_id`、`version_id`等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：`@range(min, max)`限制数值范围
4. **计算约束**：`@computed(expression)`计算字段值
5. **预算平衡约束**：预算分配总额不能超过预算总额
6. **预算执行约束**：预算支出不能超过预算分配

---

## 8. 转换函数

**定义8（转换函数）**：

```text
转换函数集合 = {
  convert_to_epm: Budget_Management_Schema → EPM_Format,
  convert_to_bpm: Budget_Management_Schema → BPM_Format,
  convert_to_database: Budget_Management_Schema → PostgreSQL_Schema
}
```

---

## 9. 形式化定理

### 9.1 预算平衡定理

**定理1（预算平衡）**：
预算分配总额等于预算总额：

```text
∑Budget_Allocation.allocated_amount = Budget_Total
```

**证明**：根据预算编制规则，所有预算分配必须基于预算总额，且分配总额不能超过预算总额。

### 9.2 预算执行定理

**定理2（预算执行）**：
预算支出总额不超过预算分配总额：

```text
∑Budget_Expenditure.expenditure_amount ≤ ∑Budget_Allocation.allocated_amount
```

**证明**：根据预算控制规则，预算支出必须基于预算分配，且支出总额不能超过分配总额。

### 9.3 预算差异定理

**定理3（预算差异）**：
预算差异等于实际金额减去预算金额：

```text
Budget_Variance.variance_amount = Budget_Variance.actual_amount - Budget_Variance.budget_amount
```

**证明**：根据预算差异定义，差异金额等于实际执行金额与预算金额的差值。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
