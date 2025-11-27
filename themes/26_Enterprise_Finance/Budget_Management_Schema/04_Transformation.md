# 预算管理Schema转换体系

## 📑 目录

- [预算管理Schema转换体系](#预算管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 预算到EPM转换](#2-预算到epm转换)
  - [3. 预算到BPM转换](#3-预算到bpm转换)
  - [4. 转换工具](#4-转换工具)
    - [4.1 EPM转换工具](#41-epm转换工具)
    - [4.2 BPM转换工具](#42-bpm转换工具)
  - [5. 预算数据存储与分析](#5-预算数据存储与分析)
    - [5.1 PostgreSQL预算数据存储](#51-postgresql预算数据存储)
    - [5.2 预算数据分析查询](#52-预算数据分析查询)

---

## 1. 转换体系概述

预算管理Schema转换体系支持预算数据到EPM、BPM格式转换，
以及预算数据存储。

### 1.1 转换目标

1. **预算到EPM转换**：预算数据到EPM格式
2. **预算到BPM转换**：预算数据到BPM格式
3. **预算到数据库转换**：预算数据到PostgreSQL存储

---

## 2. 预算到EPM转换

**转换规则**：

- 预算版本 → EPM Budget Version
- 预算分配 → EPM Budget Allocation
- 预算执行 → EPM Budget Execution
- 预算差异 → EPM Budget Variance

**转换示例**：

```python
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
        epm_budget.versions.append(epm_version)

    # 转换预算分配
    for allocation in budget_data.budget_execution.budget_allocations:
        epm_allocation = EPMBudgetAllocation()
        epm_allocation.allocation_id = allocation.allocation_id
        epm_allocation.cost_center = allocation.cost_center_code
        epm_allocation.account = allocation.account_code
        epm_allocation.amount = allocation.allocated_amount
        epm_budget.allocations.append(epm_allocation)

    return epm_budget
```

---

## 3. 预算到BPM转换

**转换规则**：

- 预算执行 → BPM Performance Metric
- 预算差异 → BPM Variance Metric
- 预算趋势 → BPM Trend Analysis

**转换示例**：

```python
def convert_budget_to_bpm(budget_data: BudgetManagementSchema) -> BPMPerformance:
    """将预算数据转换为BPM格式"""
    bpm_performance = BPMPerformance()

    # 转换预算执行指标
    for allocation in budget_data.budget_execution.budget_allocations:
        metric = BPMPerformanceMetric()
        metric.metric_name = f"Budget_Execution_{allocation.cost_center_code}"
        metric.metric_value = allocation.allocated_amount
        metric.metric_type = "Budget"
        bpm_performance.metrics.append(metric)

    # 转换预算差异指标
    for variance in budget_data.budget_analysis.budget_variance:
        metric = BPMPerformanceMetric()
        metric.metric_name = f"Budget_Variance_{variance.allocation_id}"
        metric.metric_value = variance.variance_amount
        metric.metric_type = "Variance"
        bpm_performance.metrics.append(metric)

    return bpm_performance
```

---

## 4. 转换工具

### 4.1 EPM转换工具

- **Oracle EPM Cloud**：Oracle企业绩效管理云平台
- **SAP Analytics Cloud**：SAP分析云平台
- **IBM Planning Analytics**：IBM规划分析平台

### 4.2 BPM转换工具

- **Tableau**：数据可视化工具
- **Power BI**：商业智能工具
- **Qlik Sense**：数据发现平台

---

## 5. 预算数据存储与分析

### 5.1 PostgreSQL预算数据存储

**表结构设计**：

```sql
-- 预算期间表
CREATE TABLE budget_periods (
    period_id VARCHAR(50) PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    fiscal_year VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算版本表
CREATE TABLE budget_versions (
    version_id VARCHAR(50) PRIMARY KEY,
    version_name VARCHAR(200) NOT NULL,
    version_type VARCHAR(20) NOT NULL,
    base_version VARCHAR(50),
    created_date DATE NOT NULL,
    approved_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算分配表
CREATE TABLE budget_allocations (
    allocation_id VARCHAR(50) PRIMARY KEY,
    budget_version_id VARCHAR(50) NOT NULL,
    cost_center_code VARCHAR(50) NOT NULL,
    account_code VARCHAR(50) NOT NULL,
    allocated_amount DECIMAL(18, 2) NOT NULL,
    allocation_date DATE NOT NULL,
    FOREIGN KEY (budget_version_id) REFERENCES budget_versions(version_id)
);

-- 预算执行表
CREATE TABLE budget_expenditures (
    expenditure_id VARCHAR(50) PRIMARY KEY,
    allocation_id VARCHAR(50) NOT NULL,
    expenditure_type VARCHAR(20) NOT NULL,
    reference_number VARCHAR(100) NOT NULL,
    expenditure_amount DECIMAL(18, 2) NOT NULL,
    expenditure_date DATE NOT NULL,
    FOREIGN KEY (allocation_id) REFERENCES budget_allocations(allocation_id)
);

-- 预算差异表
CREATE TABLE budget_variances (
    variance_id VARCHAR(50) PRIMARY KEY,
    allocation_id VARCHAR(50) NOT NULL,
    period_end DATE NOT NULL,
    budget_amount DECIMAL(18, 2) NOT NULL,
    actual_amount DECIMAL(18, 2) NOT NULL,
    variance_amount DECIMAL(18, 2) NOT NULL,
    variance_percentage DECIMAL(5, 2) NOT NULL,
    variance_reason TEXT,
    FOREIGN KEY (allocation_id) REFERENCES budget_allocations(allocation_id)
);

-- 创建索引
CREATE INDEX idx_budget_allocations_version ON budget_allocations(budget_version_id);
CREATE INDEX idx_budget_allocations_cost_center ON budget_allocations(cost_center_code);
CREATE INDEX idx_budget_expenditures_allocation ON budget_expenditures(allocation_id);
CREATE INDEX idx_budget_variances_allocation ON budget_variances(allocation_id);
```

**数据插入示例**：

```python
def store_budget_data(budget_data: BudgetManagementSchema, conn):
    """存储预算数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入预算版本
    for version in budget_data.budget_planning.budget_versions:
        cursor.execute("""
            INSERT INTO budget_versions
            (version_id, version_name, version_type, base_version, created_date, approved_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (version.version_id, version.version_name, version.version_type,
              version.base_version, version.created_date, version.approved_date))

    # 插入预算分配
    for allocation in budget_data.budget_execution.budget_allocations:
        cursor.execute("""
            INSERT INTO budget_allocations
            (allocation_id, budget_version_id, cost_center_code, account_code, allocated_amount, allocation_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (allocation.allocation_id, allocation.budget_version_id,
              allocation.cost_center_code, allocation.account_code,
              allocation.allocated_amount, allocation.allocation_date))

    conn.commit()
```

### 5.2 预算数据分析查询

**查询示例**：

```python
def analyze_budget_data(conn, version_id, period_end):
    """分析预算数据"""
    cursor = conn.cursor()

    # 查询预算执行情况
    cursor.execute("""
        SELECT
            ba.cost_center_code,
            ba.account_code,
            ba.allocated_amount as budget_amount,
            COALESCE(SUM(be.expenditure_amount), 0) as actual_amount,
            ba.allocated_amount - COALESCE(SUM(be.expenditure_amount), 0) as remaining_amount
        FROM budget_allocations ba
        LEFT JOIN budget_expenditures be ON ba.allocation_id = be.allocation_id
        WHERE ba.budget_version_id = %s
        GROUP BY ba.allocation_id, ba.cost_center_code, ba.account_code, ba.allocated_amount
        ORDER BY ba.cost_center_code, ba.account_code
    """, (version_id,))

    execution_summary = cursor.fetchall()

    # 查询预算差异
    cursor.execute("""
        SELECT
            bv.allocation_id,
            ba.cost_center_code,
            ba.account_code,
            bv.budget_amount,
            bv.actual_amount,
            bv.variance_amount,
            bv.variance_percentage
        FROM budget_variances bv
        JOIN budget_allocations ba ON bv.allocation_id = ba.allocation_id
        WHERE bv.period_end = %s
        ORDER BY ABS(bv.variance_amount) DESC
    """, (period_end,))

    variance_summary = cursor.fetchall()

    return {
        "execution_summary": execution_summary,
        "variance_summary": variance_summary
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
