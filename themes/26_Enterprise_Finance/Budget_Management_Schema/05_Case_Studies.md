# 预算管理Schema实践案例

## 📑 目录

- [预算管理Schema实践案例](#预算管理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：年度预算编制](#2-案例1年度预算编制)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：预算执行监控](#3-案例2预算执行监控)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：预算差异分析](#4-案例3预算差异分析)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：预算到EPM转换](#5-案例4预算到epm转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：预算数据存储与分析系统](#6-案例5预算数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供预算管理Schema在实际应用中的实践案例。

---

## 2. 案例1：年度预算编制

### 2.1 场景描述

**应用场景**：
企业年度预算编制，包括预算期间定义、预算模板创建、预算版本管理、预算场景分析。

**业务需求**：
- 支持年度、季度、月度预算期间
- 支持预算模板和预算规则定义
- 支持多版本预算管理
- 支持多场景预算分析

### 2.2 Schema定义

**年度预算编制Schema**：

```dsl
schema AnnualBudgetPlanning {
  budget_period: BudgetPeriod {
    period_id: String @value("PERIOD-2025")
    period_type: Enum @value("Annual")
    period_start: Date @value("2025-01-01")
    period_end: Date @value("2025-12-31")
    fiscal_year: String @value("2025")
  }

  budget_template: BudgetTemplate {
    template_id: String @value("TEMPLATE-001")
    template_name: String @value("标准预算模板")
    account_structure: List<AccountCode> {
      "1000": AccountCode @value("收入类")
      "2000": AccountCode @value("成本类")
      "3000": AccountCode @value("费用类")
    }
  }

  budget_version: BudgetVersion {
    version_id: String @value("VERSION-2025-001")
    version_name: String @value("2025年度预算V1.0")
    version_type: Enum @value("Initial")
    created_date: Date @value("2025-01-15")
  }

  budget_scenarios: List<BudgetScenario> {
    base: BudgetScenario {
      scenario_id: String @value("SCENARIO-BASE")
      scenario_name: String @value("基准场景")
      scenario_type: Enum @value("Base")
      probability: Decimal @value(60.0)
    }
    optimistic: BudgetScenario {
      scenario_id: String @value("SCENARIO-OPT")
      scenario_name: String @value("乐观场景")
      scenario_type: Enum @value("Optimistic")
      probability: Decimal @value(20.0)
    }
    pessimistic: BudgetScenario {
      scenario_id: String @value("SCENARIO-PESS")
      scenario_name: String @value("悲观场景")
      scenario_type: Enum @value("Pessimistic")
      probability: Decimal @value(20.0)
    }
  }
} @standard("EPM", "ZBB")
```

---

## 3. 案例2：预算执行监控

### 3.1 场景描述

**应用场景**：
企业预算执行监控，包括预算分配、预算承诺、预算支出、预算预留管理。

**业务需求**：
- 实时监控预算执行情况
- 支持预算承诺和预算预留
- 支持预算执行率计算
- 支持预算预警

### 3.2 Schema定义

**预算执行监控Schema**：

```dsl
schema BudgetExecutionMonitoring {
  budget_allocation: BudgetAllocation {
    allocation_id: String @value("ALLOC-001")
    budget_version_id: String @value("VERSION-2025-001")
    cost_center_code: String @value("CC-001")
    account_code: String @value("3000")
    allocated_amount: Decimal @value(1000000.00)
    allocation_date: Date @value("2025-01-01")
  }

  budget_commitments: List<BudgetCommitment> {
    commitment1: BudgetCommitment {
      commitment_id: String @value("COMMIT-001")
      allocation_id: String @value("ALLOC-001")
      commitment_type: Enum @value("PurchaseOrder")
      reference_number: String @value("PO-2025-001")
      committed_amount: Decimal @value(200000.00)
      commitment_date: Date @value("2025-01-10")
    }
  }

  budget_expenditures: List<BudgetExpenditure> {
    expenditure1: BudgetExpenditure {
      expenditure_id: String @value("EXP-001")
      allocation_id: String @value("ALLOC-001")
      expenditure_type: Enum @value("Actual")
      reference_number: String @value("INV-2025-001")
      expenditure_amount: Decimal @value(150000.00)
      expenditure_date: Date @value("2025-01-20")
    }
  }

  available_budget: Decimal @value(650000.00)
  execution_rate: Decimal @value(35.00)
} @standard("EPM")
```

---

## 4. 案例3：预算差异分析

### 4.1 场景描述

**应用场景**：
企业预算差异分析，包括预算差异计算、差异原因分析、差异趋势分析。

**业务需求**：
- 计算预算差异金额和差异率
- 分析预算差异原因
- 支持预算差异趋势分析
- 生成预算差异报告

### 4.2 Schema定义

**预算差异分析Schema**：

```dsl
schema BudgetVarianceAnalysis {
  budget_variance: BudgetVariance {
    variance_id: String @value("VAR-001")
    allocation_id: String @value("ALLOC-001")
    period_end: Date @value("2025-01-31")
    budget_amount: Decimal @value(83333.33)
    actual_amount: Decimal @value(150000.00)
    variance_amount: Decimal @value(66666.67)
    variance_percentage: Decimal @value(80.00)
    variance_reason: String @value("实际支出超出预算，主要原因是原材料价格上涨")
  }

  budget_trends: BudgetTrends {
    trend_id: String @value("TREND-001")
    allocation_id: String @value("ALLOC-001")
    trend_period_start: Date @value("2025-01-01")
    trend_period_end: Date @value("2025-01-31")
    trend_data_points: List<TrendDataPoint> {
      week1: TrendDataPoint {
        period: Date @value("2025-01-07")
        budget_amount: Decimal @value(19230.77)
        actual_amount: Decimal @value(20000.00)
        variance_amount: Decimal @value(769.23)
      }
      week2: TrendDataPoint {
        period: Date @value("2025-01-14")
        budget_amount: Decimal @value(19230.77)
        actual_amount: Decimal @value(35000.00)
        variance_amount: Decimal @value(15769.23)
      }
      week3: TrendDataPoint {
        period: Date @value("2025-01-21")
        budget_amount: Decimal @value(19230.77)
        actual_amount: Decimal @value(45000.00)
        variance_amount: Decimal @value(25769.23)
      }
      week4: TrendDataPoint {
        period: Date @value("2025-01-31")
        budget_amount: Decimal @value(19230.77)
        actual_amount: Decimal @value(50000.00)
        variance_amount: Decimal @value(30769.23)
      }
    }
    trend_direction: Enum @value("Increasing")
  }
} @standard("EPM", "BPM")
```

---

## 5. 案例4：预算到EPM转换

### 5.1 场景描述

**应用场景**：
将企业预算数据转换为EPM格式，用于企业绩效管理平台集成。

**业务需求**：
- 支持预算版本转换
- 支持预算分配转换
- 支持预算执行转换
- 支持预算差异转换

### 5.2 实现代码

```python
from budget_management_schema import BudgetManagementSchema
from epm import EPMBudget, EPMBudgetVersion, EPMBudgetAllocation

def convert_budget_to_epm(budget_data: BudgetManagementSchema) -> EPMBudget:
    """将预算数据转换为EPM格式"""
    epm_budget = EPMBudget()

    # 转换预算版本
    for version in budget_data.budget_planning.budget_versions:
        epm_version = EPMBudgetVersion()
        epm_version.version_id = version.version_id
        epm_version.version_name = version.version_name
        epm_version.version_type = version.version_type
        epm_version.created_date = version.created_date
        epm_version.approved_date = version.approved_date
        epm_budget.versions.append(epm_version)

    # 转换预算分配
    for allocation in budget_data.budget_execution.budget_allocations:
        epm_allocation = EPMBudgetAllocation()
        epm_allocation.allocation_id = allocation.allocation_id
        epm_allocation.version_id = allocation.budget_version_id
        epm_allocation.cost_center = allocation.cost_center_code
        epm_allocation.account = allocation.account_code
        epm_allocation.amount = allocation.allocated_amount
        epm_allocation.allocation_date = allocation.allocation_date
        epm_budget.allocations.append(epm_allocation)

    # 转换预算执行
    for expenditure in budget_data.budget_execution.budget_expenditures:
        epm_expenditure = EPMBudgetExpenditure()
        epm_expenditure.expenditure_id = expenditure.expenditure_id
        epm_expenditure.allocation_id = expenditure.allocation_id
        epm_expenditure.amount = expenditure.expenditure_amount
        epm_expenditure.expenditure_date = expenditure.expenditure_date
        epm_budget.expenditures.append(epm_expenditure)

    return epm_budget

# 使用示例
budget_data = BudgetManagementSchema.load_from_database("VERSION-2025-001")
epm_budget = convert_budget_to_epm(budget_data)
epm_budget.export_to_file("budget_2025_epm.xml")
```

---

## 6. 案例5：预算数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业预算数据存储与分析系统，支持预算数据存储、查询、分析和报表生成。

**业务需求**：
- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持预算执行报告生成
- 支持预算差异分析

### 6.2 实现代码

```python
import psycopg2
from budget_management_schema import BudgetManagementSchema, BudgetAllocation, BudgetExpenditure

class BudgetDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_budget_allocation(self, allocation: BudgetAllocation):
        """存储预算分配"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO budget_allocations
            (allocation_id, budget_version_id, cost_center_code, account_code, allocated_amount, allocation_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (allocation.allocation_id, allocation.budget_version_id,
              allocation.cost_center_code, allocation.account_code,
              allocation.allocated_amount, allocation.allocation_date))

        self.conn.commit()

    def generate_budget_execution_report(self, version_id, period_end):
        """生成预算执行报告"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                ba.cost_center_code,
                ba.account_code,
                ba.allocated_amount as budget_amount,
                COALESCE(SUM(be.expenditure_amount), 0) as actual_amount,
                ba.allocated_amount - COALESCE(SUM(be.expenditure_amount), 0) as remaining_amount,
                (COALESCE(SUM(be.expenditure_amount), 0) / ba.allocated_amount * 100) as execution_rate
            FROM budget_allocations ba
            LEFT JOIN budget_expenditures be ON ba.allocation_id = be.allocation_id
            WHERE ba.budget_version_id = %s AND be.expenditure_date <= %s
            GROUP BY ba.allocation_id, ba.cost_center_code, ba.account_code, ba.allocated_amount
            ORDER BY ba.cost_center_code, ba.account_code
        """, (version_id, period_end))

        return cursor.fetchall()

    def generate_budget_variance_report(self, period_end):
        """生成预算差异报告"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                bv.allocation_id,
                ba.cost_center_code,
                ba.account_code,
                bv.budget_amount,
                bv.actual_amount,
                bv.variance_amount,
                bv.variance_percentage,
                bv.variance_reason
            FROM budget_variances bv
            JOIN budget_allocations ba ON bv.allocation_id = ba.allocation_id
            WHERE bv.period_end = %s
            ORDER BY ABS(bv.variance_amount) DESC
        """, (period_end,))

        return cursor.fetchall()

# 使用示例
db_config = {
    "host": "localhost",
    "database": "budget_management",
    "user": "budget_user",
    "password": "password"
}

store = BudgetDataStore(db_config)

# 生成预算执行报告
execution_report = store.generate_budget_execution_report("VERSION-2025-001", "2025-01-31")
print("预算执行报告:")
for row in execution_report:
    print(f"{row[0]}-{row[1]}: 预算={row[2]}, 实际={row[3]}, 剩余={row[4]}, 执行率={row[5]:.2f}%")

# 生成预算差异报告
variance_report = store.generate_budget_variance_report("2025-01-31")
print("\n预算差异报告:")
for row in variance_report:
    print(f"{row[0]}: 预算={row[3]}, 实际={row[4]}, 差异={row[5]}, 差异率={row[6]:.2f}%")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
