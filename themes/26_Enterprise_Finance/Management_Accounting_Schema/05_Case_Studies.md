# 管理会计Schema实践案例

## 📑 目录

- [管理会计Schema实践案例](#管理会计schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：责任中心绩效管理](#2-案例1责任中心绩效管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：预算差异分析](#3-案例2预算差异分析)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：KPI绩效评价](#4-案例3kpi绩效评价)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：管理会计到平衡计分卡转换](#5-案例4管理会计到平衡计分卡转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：管理会计数据存储与分析系统](#6-案例5管理会计数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供管理会计Schema在实际应用中的实践案例。

---

## 2. 案例1：责任中心绩效管理

### 2.1 场景描述

**应用场景**：
企业责任中心绩效管理，包括成本中心、利润中心、投资中心的绩效评价。

**业务需求**：

- 支持多种责任中心类型
- 计算责任中心绩效指标
- 生成责任中心绩效报告
- 支持责任中心对比分析

### 2.2 Schema定义

**责任中心绩效管理Schema**：

```dsl
schema ResponsibilityCenterPerformance {
  cost_centers: List<CostCenter> {
    cost_center1: CostCenter {
      cost_center_code: String @value("CC-001")
      cost_center_name: String @value("生产部门")
      department: String @value("生产部")
      budget_amount: Decimal @value(1000000.00)
      actual_amount: Decimal @value(950000.00)
      variance: Decimal @value(-50000.00)
    }
  }

  profit_centers: List<ProfitCenter> {
    profit_center1: ProfitCenter {
      profit_center_code: String @value("PC-001")
      profit_center_name: String @value("销售部门")
      revenue: Decimal @value(5000000.00)
      costs: Decimal @value(3000000.00)
      profit: Decimal @value(2000000.00)
      profit_margin: Decimal @value(40.00)
    }
  }

  investment_centers: List<InvestmentCenter> {
    investment_center1: InvestmentCenter {
      investment_center_code: String @value("IC-001")
      investment_center_name: String @value("新业务部门")
      investment_amount: Decimal @value(10000000.00)
      net_income: Decimal @value(1500000.00)
      roi: Decimal @value(15.00)
    }
  }
} @standard("Balanced Scorecard")
```

---

## 3. 案例2：预算差异分析

### 3.1 场景描述

**应用场景**：
企业预算差异分析，包括预算差异、数量差异、价格差异、效率差异分析。

**业务需求**：

- 计算各种预算差异
- 分析差异原因
- 生成差异分析报告
- 支持差异趋势分析

### 3.2 Schema定义

**预算差异分析Schema**：

```dsl
schema BudgetVarianceAnalysis {
  budget_variance: BudgetVariance {
    variance_id: String @value("VAR-001")
    cost_center_code: String @value("CC-001")
    account_code: String @value("3000")
    budget_amount: Decimal @value(100000.00)
    actual_amount: Decimal @value(120000.00)
    variance_amount: Decimal @value(20000.00)
    variance_percentage: Decimal @value(20.00)
  }

  volume_variance: VolumeVariance {
    variance_id: String @value("VAR-VOL-001")
    budget_volume: Decimal @value(1000.00)
    actual_volume: Decimal @value(1200.00)
    standard_price: Decimal @value(100.00)
    variance_amount: Decimal @value(20000.00)
  }

  price_variance: PriceVariance {
    variance_id: String @value("VAR-PRICE-001")
    budget_price: Decimal @value(100.00)
    actual_price: Decimal @value(110.00)
    actual_volume: Decimal @value(1200.00)
    variance_amount: Decimal @value(12000.00)
  }

  efficiency_variance: EfficiencyVariance {
    variance_id: String @value("VAR-EFF-001")
    budget_hours: Decimal @value(1000.00)
    actual_hours: Decimal @value(1100.00)
    standard_rate: Decimal @value(50.00)
    variance_amount: Decimal @value(5000.00)
  }
} @standard("Variance Analysis")
```

---

## 4. 案例3：KPI绩效评价

### 4.1 场景描述

**应用场景**：
企业KPI绩效评价，包括KPI定义、KPI监控、KPI分析、KPI报告。

**业务需求**：

- 定义KPI指标
- 监控KPI值
- 计算KPI得分
- 生成KPI报告

### 4.2 Schema定义

**KPI绩效评价Schema**：

```dsl
schema KPIPerformanceEvaluation {
  kpi_definitions: List<KPIDefinition> {
    kpi1: KPIDefinition {
      kpi_id: String @value("KPI-001")
      kpi_name: String @value("销售收入增长率")
      kpi_type: Enum @value("Financial")
      target_value: Decimal @value(10.00)
      calculation_formula: String @value("(本期收入 - 上期收入) / 上期收入 * 100")
      measurement_unit: String @value("百分比")
    }
    kpi2: KPIDefinition {
      kpi_id: String @value("KPI-002")
      kpi_name: String @value("客户满意度")
      kpi_type: Enum @value("Customer")
      target_value: Decimal @value(85.00)
      calculation_formula: String @value("满意客户数 / 总客户数 * 100")
      measurement_unit: String @value("百分比")
    }
  }

  performance_metrics: List<PerformanceMetric> {
    metric1: PerformanceMetric {
      metric_id: String @value("METRIC-001")
      kpi_id: String @value("KPI-001")
      metric_value: Decimal @value(12.50)
      measurement_date: Date @value("2025-01-31")
      measurement_unit: String @value("百分比")
    }
  }

  performance_scores: List<PerformanceScore> {
    score1: PerformanceScore {
      score_id: String @value("SCORE-001")
      kpi_id: String @value("KPI-001")
      score_value: Decimal @value(85.00)
      score_level: Enum @value("Good")
      score_rank: Int @value(3)
    }
  }
} @standard("KPI")
```

---

## 5. 案例4：管理会计到平衡计分卡转换

### 5.1 场景描述

**应用场景**：
将企业管理会计数据转换为平衡计分卡格式，用于企业绩效管理。

**业务需求**：

- 转换责任中心到平衡计分卡维度
- 转换绩效指标到平衡计分卡指标
- 生成平衡计分卡报告

### 5.2 实现代码

```python
from management_accounting_schema import ManagementAccountingSchema
from balanced_scorecard import BalancedScorecard, BSCPerspective, BSCMetric

def convert_management_to_balanced_scorecard(management_data: ManagementAccountingSchema) -> BalancedScorecard:
    """将管理会计数据转换为平衡计分卡格式"""
    bsc = BalancedScorecard()

    # 转换财务维度
    financial_perspective = BSCPerspective()
    financial_perspective.name = "财务维度"
    financial_perspective.weight = 0.25

    for profit_center in management_data.responsibility_centers.profit_centers:
        metric = BSCMetric()
        metric.name = f"{profit_center.profit_center_name}_利润"
        metric.value = profit_center.profit
        metric.target = profit_center.profit * 1.1  # 目标增长10%
        financial_perspective.metrics.append(metric)

    bsc.perspectives.append(financial_perspective)

    # 转换客户维度
    customer_perspective = BSCPerspective()
    customer_perspective.name = "客户维度"
    customer_perspective.weight = 0.25

    for kpi in management_data.performance_evaluation.kpi_definitions:
        if kpi.kpi_type == "Customer":
            metric = BSCMetric()
            metric.name = kpi.kpi_name
            metric.value = get_kpi_current_value(kpi.kpi_id)
            metric.target = kpi.target_value
            customer_perspective.metrics.append(metric)

    bsc.perspectives.append(customer_perspective)

    # 转换内部流程维度
    process_perspective = BSCPerspective()
    process_perspective.name = "内部流程维度"
    process_perspective.weight = 0.25

    for kpi in management_data.performance_evaluation.kpi_definitions:
        if kpi.kpi_type == "Process":
            metric = BSCMetric()
            metric.name = kpi.kpi_name
            metric.value = get_kpi_current_value(kpi.kpi_id)
            metric.target = kpi.target_value
            process_perspective.metrics.append(metric)

    bsc.perspectives.append(process_perspective)

    # 转换学习成长维度
    learning_perspective = BSCPerspective()
    learning_perspective.name = "学习成长维度"
    learning_perspective.weight = 0.25

    for kpi in management_data.performance_evaluation.kpi_definitions:
        if kpi.kpi_type == "Learning":
            metric = BSCMetric()
            metric.name = kpi.kpi_name
            metric.value = get_kpi_current_value(kpi.kpi_id)
            metric.target = kpi.target_value
            learning_perspective.metrics.append(metric)

    bsc.perspectives.append(learning_perspective)

    return bsc

# 使用示例
management_data = ManagementAccountingSchema.load_from_database("2025-01")
bsc = convert_management_to_balanced_scorecard(management_data)
bsc.generate_report("balanced_scorecard_2025-01.pdf")
```

---

## 6. 案例5：管理会计数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业管理会计数据存储与分析系统，支持管理会计数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持绩效报告生成
- 支持差异分析

### 6.2 实现代码

```python
import psycopg2
from management_accounting_schema import ManagementAccountingSchema, CostCenter, KPIDefinition

class ManagementAccountingDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_cost_center(self, cost_center: CostCenter):
        """存储成本中心"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO cost_centers
            (cost_center_code, cost_center_name, department, budget_amount, actual_amount)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (cost_center_code) DO UPDATE SET
                budget_amount = EXCLUDED.budget_amount,
                actual_amount = EXCLUDED.actual_amount
        """, (cost_center.cost_center_code, cost_center.cost_center_name,
              cost_center.department, cost_center.budget_amount, cost_center.actual_amount))

        self.conn.commit()

    def generate_performance_report(self, period_start, period_end):
        """生成绩效报告"""
        cursor = self.conn.cursor()

        # 查询责任中心绩效
        cursor.execute("""
            SELECT
                cc.cost_center_code,
                cc.cost_center_name,
                cc.budget_amount,
                cc.actual_amount,
                cc.variance,
                (cc.variance / NULLIF(cc.budget_amount, 0) * 100) as variance_percentage
            FROM cost_centers cc
            WHERE cc.created_at BETWEEN %s AND %s
            ORDER BY ABS(cc.variance) DESC
        """, (period_start, period_end))

        cost_center_performance = cursor.fetchall()

        # 查询KPI绩效
        cursor.execute("""
            SELECT
                kd.kpi_id,
                kd.kpi_name,
                kd.target_value,
                AVG(pm.metric_value) as average_value,
                AVG(pm.metric_value) - kd.target_value as variance
            FROM kpi_definitions kd
            JOIN performance_metrics pm ON kd.kpi_id = pm.kpi_id
            WHERE pm.measurement_date BETWEEN %s AND %s
            GROUP BY kd.kpi_id, kd.kpi_name, kd.target_value
            ORDER BY ABS(AVG(pm.metric_value) - kd.target_value) DESC
        """, (period_start, period_end))

        kpi_performance = cursor.fetchall()

        return {
            "cost_center_performance": cost_center_performance,
            "kpi_performance": kpi_performance
        }

# 使用示例
db_config = {
    "host": "localhost",
    "database": "management_accounting",
    "user": "ma_user",
    "password": "password"
}

store = ManagementAccountingDataStore(db_config)

# 生成绩效报告
performance_report = store.generate_performance_report("2025-01-01", "2025-01-31")
print("责任中心绩效:")
for row in performance_report["cost_center_performance"]:
    print(f"{row[1]}: 预算={row[2]}, 实际={row[3]}, 差异={row[4]}, 差异率={row[5]:.2f}%")

print("\nKPI绩效:")
for row in performance_report["kpi_performance"]:
    print(f"{row[1]}: 目标={row[2]}, 实际={row[3]:.2f}, 差异={row[4]:.2f}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
