# 合并报表Schema转换体系

## 📑 目录

- [合并报表Schema转换体系](#合并报表schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 合并报表到XBRL转换](#2-合并报表到xbrl转换)
  - [3. 合并报表到IFRS转换](#3-合并报表到ifrs转换)
  - [4. 合并报表数据存储与分析](#4-合并报表数据存储与分析)
    - [4.1 PostgreSQL合并报表数据存储](#41-postgresql合并报表数据存储)
    - [4.2 合并报表数据分析查询](#42-合并报表数据分析查询)

---

## 1. 转换体系概述

合并报表Schema转换体系支持合并报表数据到XBRL、IFRS格式转换，以及合并报表数据存储。

### 1.1 转换目标

1. **合并报表到XBRL转换**：合并报表数据到XBRL格式
2. **合并报表到IFRS转换**：合并报表数据到IFRS格式
3. **合并报表到数据库转换**：合并报表数据到PostgreSQL存储

---

## 2. 合并报表到XBRL转换

**转换规则**：

- 合并报表项目 → XBRL Taxonomy Element
- 合并报表金额 → XBRL Fact Element
- 合并报表 → XBRL Instance Document

**转换示例**：

```python
def convert_consolidated_to_xbrl(consolidated_data: ConsolidatedReportingSchema) -> XBRLInstance:
    """将合并报表数据转换为XBRL格式"""
    xbrl_instance = XBRLInstance()

    # 创建上下文
    context = Context()
    context.entity_identifier = "Consolidated_Entity"
    context.period_start = consolidated_data.consolidated_balance_sheet.reporting_period
    context.period_end = consolidated_data.consolidated_balance_sheet.reporting_period

    # 转换合并资产负债表
    balance_sheet = consolidated_data.consolidated_balance_sheet

    # 资产事实
    assets_fact = Fact()
    assets_fact.element = "ConsolidatedAssets"
    assets_fact.context = context
    assets_fact.unit = "CNY"
    assets_fact.value = balance_sheet.consolidated_assets.total_assets
    xbrl_instance.facts.append(assets_fact)

    # 负债事实
    liabilities_fact = Fact()
    liabilities_fact.element = "ConsolidatedLiabilities"
    liabilities_fact.context = context
    liabilities_fact.unit = "CNY"
    liabilities_fact.value = balance_sheet.consolidated_liabilities.total_liabilities
    xbrl_instance.facts.append(liabilities_fact)

    # 权益事实
    equity_fact = Fact()
    equity_fact.element = "ConsolidatedEquity"
    equity_fact.context = context
    equity_fact.unit = "CNY"
    equity_fact.value = balance_sheet.consolidated_equity.total_equity
    xbrl_instance.facts.append(equity_fact)

    # 少数股东权益事实
    minority_interest_fact = Fact()
    minority_interest_fact.element = "MinorityInterest"
    minority_interest_fact.context = context
    minority_interest_fact.unit = "CNY"
    minority_interest_fact.value = balance_sheet.consolidated_equity.minority_interest
    xbrl_instance.facts.append(minority_interest_fact)

    # 转换合并利润表
    income_statement = consolidated_data.consolidated_income_statement

    # 收入事实
    revenue_fact = Fact()
    revenue_fact.element = "ConsolidatedRevenue"
    revenue_fact.context = context
    revenue_fact.unit = "CNY"
    revenue_fact.value = income_statement.consolidated_revenue.total_revenue
    xbrl_instance.facts.append(revenue_fact)

    # 净利润事实
    net_income_fact = Fact()
    net_income_fact.element = "ConsolidatedNetIncome"
    net_income_fact.context = context
    net_income_fact.unit = "CNY"
    net_income_fact.value = income_statement.net_income
    xbrl_instance.facts.append(net_income_fact)

    return xbrl_instance
```

---

## 3. 合并报表到IFRS转换

**转换规则**：

- 合并报表项目 → IFRS报表项目
- 合并报表金额 → IFRS报表金额
- 合并报表 → IFRS格式报表

**转换示例**：

```python
def convert_consolidated_to_ifrs(consolidated_data: ConsolidatedReportingSchema) -> IFRSReport:
    """将合并报表数据转换为IFRS格式"""
    ifrs_report = IFRSReport()

    # 转换合并资产负债表
    ifrs_balance_sheet = IFRSBalanceSheet()
    ifrs_balance_sheet.report_date = consolidated_data.consolidated_balance_sheet.report_date

    # 转换资产
    ifrs_balance_sheet.assets = {
        "Current_Assets": consolidated_data.consolidated_balance_sheet.consolidated_assets.current_assets,
        "Non_Current_Assets": consolidated_data.consolidated_balance_sheet.consolidated_assets.non_current_assets,
        "Total_Assets": consolidated_data.consolidated_balance_sheet.consolidated_assets.total_assets
    }

    # 转换负债
    ifrs_balance_sheet.liabilities = {
        "Current_Liabilities": consolidated_data.consolidated_balance_sheet.consolidated_liabilities.current_liabilities,
        "Non_Current_Liabilities": consolidated_data.consolidated_balance_sheet.consolidated_liabilities.non_current_liabilities,
        "Total_Liabilities": consolidated_data.consolidated_balance_sheet.consolidated_liabilities.total_liabilities
    }

    # 转换权益
    ifrs_balance_sheet.equity = {
        "Share_Capital": consolidated_data.consolidated_balance_sheet.consolidated_equity.share_capital,
        "Retained_Earnings": consolidated_data.consolidated_balance_sheet.consolidated_equity.retained_earnings,
        "Minority_Interest": consolidated_data.consolidated_balance_sheet.consolidated_equity.minority_interest,
        "Total_Equity": consolidated_data.consolidated_balance_sheet.consolidated_equity.total_equity
    }

    ifrs_report.balance_sheet = ifrs_balance_sheet

    # 转换合并利润表
    ifrs_income_statement = IFRSIncomeStatement()
    ifrs_income_statement.period_start = consolidated_data.consolidated_income_statement.period_start
    ifrs_income_statement.period_end = consolidated_data.consolidated_income_statement.period_end

    ifrs_income_statement.revenue = consolidated_data.consolidated_income_statement.consolidated_revenue.total_revenue
    ifrs_income_statement.expenses = consolidated_data.consolidated_income_statement.consolidated_expenses.total_expenses
    ifrs_income_statement.net_income = consolidated_data.consolidated_income_statement.net_income
    ifrs_income_statement.net_income_attributable_to_parent = consolidated_data.consolidated_income_statement.net_income_attributable_to_parent
    ifrs_income_statement.net_income_attributable_to_minority = consolidated_data.consolidated_income_statement.net_income_attributable_to_minority

    ifrs_report.income_statement = ifrs_income_statement

    return ifrs_report
```

---

## 4. 合并报表数据存储与分析

### 4.1 PostgreSQL合并报表数据存储

**表结构设计**：

```sql
-- 合并范围表
CREATE TABLE consolidation_scope (
    subsidiary_id VARCHAR(50) PRIMARY KEY,
    subsidiary_code VARCHAR(50) UNIQUE NOT NULL,
    subsidiary_name VARCHAR(200) NOT NULL,
    parent_company_id VARCHAR(50) NOT NULL,
    ownership_percentage DECIMAL(5, 2) NOT NULL,
    voting_rights_percentage DECIMAL(5, 2) NOT NULL,
    has_control BOOLEAN NOT NULL,
    consolidation_method VARCHAR(20) NOT NULL,
    is_consolidated BOOLEAN NOT NULL,
    reporting_period_start DATE NOT NULL,
    reporting_period_end DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 抵消分录表
CREATE TABLE elimination_entries (
    elimination_id VARCHAR(50) PRIMARY KEY,
    elimination_date DATE NOT NULL,
    reporting_period DATE NOT NULL,
    elimination_type VARCHAR(20) NOT NULL,
    debit_account VARCHAR(50) NOT NULL,
    credit_account VARCHAR(50) NOT NULL,
    elimination_amount DECIMAL(18, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 合并资产负债表表
CREATE TABLE consolidated_balance_sheets (
    report_id VARCHAR(50) PRIMARY KEY,
    report_date DATE NOT NULL,
    reporting_period DATE NOT NULL,
    total_assets DECIMAL(18, 2) NOT NULL,
    total_liabilities DECIMAL(18, 2) NOT NULL,
    total_equity DECIMAL(18, 2) NOT NULL,
    minority_interest DECIMAL(18, 2) DEFAULT 0,
    is_balanced BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 合并利润表表
CREATE TABLE consolidated_income_statements (
    report_id VARCHAR(50) PRIMARY KEY,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue DECIMAL(18, 2) NOT NULL,
    total_expenses DECIMAL(18, 2) NOT NULL,
    net_income DECIMAL(18, 2) NOT NULL,
    net_income_attributable_to_parent DECIMAL(18, 2) NOT NULL,
    net_income_attributable_to_minority DECIMAL(18, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_consolidation_scope_parent ON consolidation_scope(parent_company_id);
CREATE INDEX idx_elimination_entries_period ON elimination_entries(reporting_period);
CREATE INDEX idx_consolidated_balance_sheets_date ON consolidated_balance_sheets(report_date);
CREATE INDEX idx_consolidated_income_statements_period ON consolidated_income_statements(period_start, period_end);
```

### 4.2 合并报表数据分析查询

**查询示例**：

```python
def analyze_consolidated_data(conn, period_start, period_end):
    """分析合并报表数据"""
    cursor = conn.cursor()

    # 查询合并范围汇总
    cursor.execute("""
        SELECT
            cs.subsidiary_name,
            cs.ownership_percentage,
            cs.consolidation_method,
            cs.is_consolidated
        FROM consolidation_scope cs
        WHERE cs.reporting_period_start <= %s
        AND cs.reporting_period_end >= %s
        ORDER BY cs.subsidiary_name
    """, (period_end, period_start))

    scope_summary = cursor.fetchall()

    # 查询合并资产负债表汇总
    cursor.execute("""
        SELECT
            cbs.report_date,
            cbs.total_assets,
            cbs.total_liabilities,
            cbs.total_equity,
            cbs.minority_interest,
            cbs.is_balanced
        FROM consolidated_balance_sheets cbs
        WHERE cbs.report_date BETWEEN %s AND %s
        ORDER BY cbs.report_date
    """, (period_start, period_end))

    balance_sheet_summary = cursor.fetchall()

    # 查询合并利润表汇总
    cursor.execute("""
        SELECT
            cis.period_start,
            cis.period_end,
            cis.total_revenue,
            cis.total_expenses,
            cis.net_income,
            cis.net_income_attributable_to_parent,
            cis.net_income_attributable_to_minority
        FROM consolidated_income_statements cis
        WHERE cis.period_start >= %s
        AND cis.period_end <= %s
        ORDER BY cis.period_start
    """, (period_start, period_end))

    income_statement_summary = cursor.fetchall()

    return {
        "scope_summary": scope_summary,
        "balance_sheet_summary": balance_sheet_summary,
        "income_statement_summary": income_statement_summary
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
