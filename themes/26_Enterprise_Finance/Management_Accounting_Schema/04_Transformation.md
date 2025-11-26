# 管理会计Schema转换体系

## 📑 目录

- [管理会计Schema转换体系](#管理会计schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 管理会计到平衡计分卡转换](#2-管理会计到平衡计分卡转换)
  - [3. 管理会计到KPI转换](#3-管理会计到kpi转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 管理会计数据存储与分析](#5-管理会计数据存储与分析)
    - [5.1 PostgreSQL管理会计数据存储](#51-postgresql管理会计数据存储)
    - [5.2 管理会计数据分析查询](#52-管理会计数据分析查询)

---

## 1. 转换体系概述

管理会计Schema转换体系支持管理会计数据到平衡计分卡、KPI格式转换，
以及管理会计数据存储。

### 1.1 转换目标

1. **管理会计到平衡计分卡**：管理会计数据到平衡计分卡格式
2. **管理会计到KPI转换**：管理会计数据到KPI格式
3. **管理会计到数据库转换**：管理会计数据到PostgreSQL存储

---

## 2. 管理会计到平衡计分卡转换

**转换规则**：

- 责任中心 → 平衡计分卡维度
- 绩效指标 → 平衡计分卡指标
- 绩效得分 → 平衡计分卡

**转换示例**：

```python
def convert_management_to_balanced_scorecard(management_data: ManagementAccountingSchema) -> BalancedScorecard:
    """将管理会计数据转换为平衡计分卡格式"""
    bsc = BalancedScorecard()

    # 转换财务维度
    financial_perspective = BSCPerspective()
    financial_perspective.name = "财务维度"
    for profit_center in management_data.responsibility_centers.profit_centers:
        metric = BSCMetric()
        metric.name = f"{profit_center.profit_center_name}_利润"
        metric.value = profit_center.profit
        financial_perspective.metrics.append(metric)
    bsc.perspectives.append(financial_perspective)

    # 转换内部流程维度
    process_perspective = BSCPerspective()
    process_perspective.name = "内部流程维度"
    for kpi in management_data.performance_evaluation.kpi_definitions:
        if kpi.kpi_type == "Process":
            metric = BSCMetric()
            metric.name = kpi.kpi_name
            metric.value = get_kpi_value(kpi.kpi_id)
            process_perspective.metrics.append(metric)
    bsc.perspectives.append(process_perspective)

    return bsc
```

---

## 3. 管理会计到KPI转换

**转换规则**：

- 绩效指标 → KPI指标
- 绩效得分 → KPI得分
- 绩效报告 → KPI报告

**转换示例**：

```python
def convert_management_to_kpi(management_data: ManagementAccountingSchema) -> KPISystem:
    """将管理会计数据转换为KPI格式"""
    kpi_system = KPISystem()

    # 转换KPI定义
    for kpi_def in management_data.performance_evaluation.kpi_definitions:
        kpi = KPI()
        kpi.kpi_id = kpi_def.kpi_id
        kpi.kpi_name = kpi_def.kpi_name
        kpi.kpi_type = kpi_def.kpi_type
        kpi.target_value = kpi_def.target_value
        kpi_system.kpis.append(kpi)

    # 转换KPI值
    for metric in management_data.performance_evaluation.performance_metrics:
        kpi_value = KPIValue()
        kpi_value.kpi_id = metric.kpi_id
        kpi_value.value = metric.metric_value
        kpi_value.measurement_date = metric.measurement_date
        kpi_system.kpi_values.append(kpi_value)

    return kpi_system
```

---

## 4. 转换工具

### 4.1 平衡计分卡工具

- **Balanced Scorecard Software**：平衡计分卡软件
- **Performance Management Tools**：绩效管理工具

### 4.2 KPI工具

- **KPI Dashboard**：KPI仪表板
- **Performance Analytics**：绩效分析工具

---

## 5. 管理会计数据存储与分析

### 5.1 PostgreSQL管理会计数据存储

**表结构设计**：

```sql
-- 责任中心表
CREATE TABLE responsibility_centers (
    center_code VARCHAR(50) PRIMARY KEY,
    center_name VARCHAR(200) NOT NULL,
    center_type VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    manager VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 成本中心表
CREATE TABLE cost_centers (
    cost_center_code VARCHAR(50) PRIMARY KEY,
    cost_center_name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    budget_amount DECIMAL(18, 2) DEFAULT 0,
    actual_amount DECIMAL(18, 2) DEFAULT 0,
    variance DECIMAL(18, 2) GENERATED ALWAYS AS (actual_amount - budget_amount) STORED,
    FOREIGN KEY (cost_center_code) REFERENCES responsibility_centers(center_code)
);

-- 利润中心表
CREATE TABLE profit_centers (
    profit_center_code VARCHAR(50) PRIMARY KEY,
    profit_center_name VARCHAR(200) NOT NULL,
    revenue DECIMAL(18, 2) DEFAULT 0,
    costs DECIMAL(18, 2) DEFAULT 0,
    profit DECIMAL(18, 2) GENERATED ALWAYS AS (revenue - costs) STORED,
    profit_margin DECIMAL(5, 2) GENERATED ALWAYS AS (profit / NULLIF(revenue, 0) * 100) STORED,
    FOREIGN KEY (profit_center_code) REFERENCES responsibility_centers(center_code)
);

-- KPI定义表
CREATE TABLE kpi_definitions (
    kpi_id VARCHAR(50) PRIMARY KEY,
    kpi_name VARCHAR(200) NOT NULL,
    kpi_type VARCHAR(50) NOT NULL,
    target_value DECIMAL(18, 2) NOT NULL,
    calculation_formula TEXT NOT NULL,
    measurement_unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 绩效指标表
CREATE TABLE performance_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    kpi_id VARCHAR(50) NOT NULL,
    metric_value DECIMAL(18, 2) NOT NULL,
    measurement_date DATE NOT NULL,
    measurement_unit VARCHAR(50) NOT NULL,
    FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(kpi_id)
);

-- 预算差异表
CREATE TABLE budget_variances (
    variance_id VARCHAR(50) PRIMARY KEY,
    cost_center_code VARCHAR(50) NOT NULL,
    account_code VARCHAR(50) NOT NULL,
    budget_amount DECIMAL(18, 2) NOT NULL,
    actual_amount DECIMAL(18, 2) NOT NULL,
    variance_amount DECIMAL(18, 2) GENERATED ALWAYS AS (actual_amount - budget_amount) STORED,
    variance_percentage DECIMAL(5, 2) GENERATED ALWAYS AS ((actual_amount - budget_amount) / NULLIF(budget_amount, 0) * 100) STORED,
    variance_date DATE NOT NULL,
    FOREIGN KEY (cost_center_code) REFERENCES cost_centers(cost_center_code)
);

-- 创建索引
CREATE INDEX idx_performance_metrics_kpi ON performance_metrics(kpi_id);
CREATE INDEX idx_budget_variances_center ON budget_variances(cost_center_code);
```

**数据插入示例**：

```python
def store_management_accounting_data(management_data: ManagementAccountingSchema, conn):
    """存储管理会计数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入成本中心
    for cost_center in management_data.responsibility_centers.cost_centers:
        cursor.execute("""
            INSERT INTO cost_centers
            (cost_center_code, cost_center_name, department, budget_amount, actual_amount)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (cost_center_code) DO UPDATE SET
                budget_amount = EXCLUDED.budget_amount,
                actual_amount = EXCLUDED.actual_amount
        """, (cost_center.cost_center_code, cost_center.cost_center_name,
              cost_center.department, cost_center.budget_amount, cost_center.actual_amount))

    # 插入KPI定义
    for kpi_def in management_data.performance_evaluation.kpi_definitions:
        cursor.execute("""
            INSERT INTO kpi_definitions
            (kpi_id, kpi_name, kpi_type, target_value, calculation_formula, measurement_unit)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (kpi_def.kpi_id, kpi_def.kpi_name, kpi_def.kpi_type,
              kpi_def.target_value, kpi_def.calculation_formula, kpi_def.measurement_unit))

    conn.commit()
```

### 5.2 管理会计数据分析查询

**查询示例**：

```python
def analyze_management_accounting_data(conn, period_start, period_end):
    """分析管理会计数据"""
    cursor = conn.cursor()

    # 查询责任中心绩效
    cursor.execute("""
        SELECT
            rc.center_code,
            rc.center_name,
            rc.center_type,
            CASE
                WHEN rc.center_type = 'CostCenter' THEN cc.variance
                WHEN rc.center_type = 'ProfitCenter' THEN pc.profit
                ELSE NULL
            END as performance_metric
        FROM responsibility_centers rc
        LEFT JOIN cost_centers cc ON rc.center_code = cc.cost_center_code
        LEFT JOIN profit_centers pc ON rc.center_code = pc.profit_center_code
        WHERE rc.created_at BETWEEN %s AND %s
    """, (period_start, period_end))

    center_performance = cursor.fetchall()

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
    """, (period_start, period_end))

    kpi_performance = cursor.fetchall()

    return {
        "center_performance": center_performance,
        "kpi_performance": kpi_performance
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
