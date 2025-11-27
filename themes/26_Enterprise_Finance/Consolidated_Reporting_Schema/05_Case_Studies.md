# 合并报表Schema实践案例

## 📑 目录

- [合并报表Schema实践案例](#合并报表schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：合并范围确定](#2-案例1合并范围确定)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：抵消分录编制](#3-案例2抵消分录编制)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：合并报表生成](#4-案例3合并报表生成)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：合并报表到XBRL转换](#5-案例4合并报表到xbrl转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：合并报表数据存储与分析系统](#6-案例5合并报表数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供合并报表Schema在实际应用中的实践案例。

---

## 2. 案例1：合并范围确定

### 2.1 场景描述

**应用场景**：
确定合并范围，评估控制权，选择合并方法。

**业务需求**：

- 支持控制权评估
- 支持合并范围确定
- 支持合并方法选择

### 2.2 Schema定义

**合并范围确定Schema**：

```dsl
schema ConsolidationScopeDetermination {
  subsidiary: Subsidiary {
    subsidiary_id: String @value("SUB-20250001")
    subsidiary_code: String @value("SUB001")
    subsidiary_name: String @value("子公司A")
    parent_company_id: String @value("PARENT-001")
    ownership_percentage: Decimal @value(80.00)
    voting_rights_percentage: Decimal @value(80.00)
    control_assessment: ControlAssessment {
      has_control: Boolean @value(true)
      control_indicators: List<String> {
        "Majority_Voting_Rights"
        "Board_Control"
      }
      control_date: Date @value("2025-01-01")
    }
    consolidation_method: Enum @value("Full_Consolidation")
    is_consolidated: Boolean @value(true)
  }
}
```

---

## 3. 案例2：抵消分录编制

### 3.1 场景描述

**应用场景**：
编制内部交易抵消、内部投资抵消、内部往来抵消。

**业务需求**：

- 支持内部交易抵消
- 支持内部投资抵消
- 支持内部往来抵消

### 3.2 Schema定义

**抵消分录编制Schema**：

```dsl
schema EliminationEntriesPreparation {
  intercompany_transaction: IntercompanyTransaction {
    transaction_id: String @value("ICT-20250001")
    transaction_date: Date @value("2025-01-15")
    seller_entity_id: String @value("SUB-20250001")
    buyer_entity_id: String @value("PARENT-001")
    transaction_type: Enum @value("Sales")
    transaction_amount: Decimal @value(100000.00)
    is_eliminated: Boolean @value(true)
  }

  elimination_entry: EliminationEntry {
    elimination_id: String @value("ELIM-20250001")
    elimination_date: Date @value("2025-01-31")
    reporting_period: Date @value("2025-01")
    elimination_type: Enum @value("Intercompany_Sales")
    debit_account: String @value("Revenue")
    credit_account: String @value("Cost_of_Sales")
    elimination_amount: Decimal @value(100000.00)
    related_transactions: List<String> {
      "ICT-20250001"
    }
  }
}
```

---

## 4. 案例3：合并报表生成

### 4.1 场景描述

**应用场景**：
生成合并资产负债表、合并利润表、合并现金流量表。

**业务需求**：

- 支持合并报表自动生成
- 支持合并报表验证
- 支持合并报表披露

### 4.2 实现代码

```python
def generate_consolidated_statements(consolidated_data: ConsolidatedReportingSchema) -> ConsolidatedStatements:
    """生成合并报表"""
    consolidated_statements = ConsolidatedStatements()

    # 生成合并资产负债表
    consolidated_balance_sheet = ConsolidatedBalanceSheet()
    consolidated_balance_sheet.report_date = consolidated_data.reporting_period
    consolidated_balance_sheet.reporting_period = consolidated_data.reporting_period

    # 汇总各子公司资产
    total_current_assets = 0
    total_non_current_assets = 0

    for subsidiary in consolidated_data.consolidated_scope.subsidiaries:
        if subsidiary.is_consolidated:
            # 获取子公司资产负债表
            subsidiary_balance_sheet = get_subsidiary_balance_sheet(subsidiary.subsidiary_id)
            total_current_assets += subsidiary_balance_sheet.current_assets
            total_non_current_assets += subsidiary_balance_sheet.non_current_assets

    consolidated_balance_sheet.consolidated_assets.current_assets = total_current_assets
    consolidated_balance_sheet.consolidated_assets.non_current_assets = total_non_current_assets
    consolidated_balance_sheet.consolidated_assets.total_assets = total_current_assets + total_non_current_assets

    # 应用抵消分录
    for elimination in consolidated_data.elimination_entries.elimination_entries:
        if elimination.elimination_type == "Intercompany_Sales":
            # 抵消内部销售收入
            consolidated_balance_sheet.consolidated_assets.total_assets -= elimination.elimination_amount

    consolidated_statements.consolidated_balance_sheet = consolidated_balance_sheet

    # 生成合并利润表
    consolidated_income_statement = ConsolidatedIncomeStatement()
    consolidated_income_statement.period_start = consolidated_data.reporting_period_start
    consolidated_income_statement.period_end = consolidated_data.reporting_period_end

    # 汇总各子公司收入
    total_revenue = 0
    total_expenses = 0

    for subsidiary in consolidated_data.consolidated_scope.subsidiaries:
        if subsidiary.is_consolidated:
            # 获取子公司利润表
            subsidiary_income_statement = get_subsidiary_income_statement(subsidiary.subsidiary_id)
            total_revenue += subsidiary_income_statement.revenue
            total_expenses += subsidiary_income_statement.expenses

    # 应用抵消分录
    for elimination in consolidated_data.elimination_entries.elimination_entries:
        if elimination.elimination_type == "Intercompany_Sales":
            # 抵消内部销售收入和成本
            total_revenue -= elimination.elimination_amount
            total_expenses -= elimination.elimination_amount

    consolidated_income_statement.consolidated_revenue.total_revenue = total_revenue
    consolidated_income_statement.consolidated_expenses.total_expenses = total_expenses
    consolidated_income_statement.net_income = total_revenue - total_expenses

    # 计算少数股东权益
    for subsidiary in consolidated_data.consolidated_scope.subsidiaries:
        if subsidiary.is_consolidated and subsidiary.ownership_percentage < 100:
            minority_share = (100 - subsidiary.ownership_percentage) / 100
            consolidated_income_statement.net_income_attributable_to_minority += consolidated_income_statement.net_income * minority_share

    consolidated_income_statement.net_income_attributable_to_parent = consolidated_income_statement.net_income - consolidated_income_statement.net_income_attributable_to_minority

    consolidated_statements.consolidated_income_statement = consolidated_income_statement

    return consolidated_statements
```

---

## 5. 案例4：合并报表到XBRL转换

### 5.1 场景描述

**应用场景**：
将合并报表转换为XBRL格式，用于监管报告。

**业务需求**：

- 支持合并报表到XBRL转换
- 支持XBRL验证
- 支持XBRL披露

### 5.2 实现代码

```python
def convert_consolidated_to_xbrl(consolidated_statements: ConsolidatedStatements) -> XBRLInstance:
    """将合并报表转换为XBRL格式"""
    xbrl_instance = XBRLInstance()

    # 创建上下文
    context = Context()
    context.entity_identifier = "Consolidated_Entity"
    context.period_start = consolidated_statements.consolidated_balance_sheet.reporting_period
    context.period_end = consolidated_statements.consolidated_balance_sheet.reporting_period

    # 转换合并资产负债表
    balance_sheet = consolidated_statements.consolidated_balance_sheet

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
    income_statement = consolidated_statements.consolidated_income_statement

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

## 6. 案例5：合并报表数据存储与分析系统

### 6.1 场景描述

**应用场景**：
合并报表数据存储与分析系统，支持数据存储、查询、分析、报表生成。

**业务需求**：

- 支持合并报表数据存储
- 支持数据查询和分析
- 支持报表生成

### 6.2 实现代码

```python
def store_consolidated_data(consolidated_data: ConsolidatedReportingSchema, conn):
    """存储合并报表数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储合并范围
    for subsidiary in consolidated_data.consolidation_scope.subsidiaries:
        cursor.execute("""
            INSERT INTO consolidation_scope
            (subsidiary_id, subsidiary_code, subsidiary_name, parent_company_id,
             ownership_percentage, voting_rights_percentage, has_control,
             consolidation_method, is_consolidated, reporting_period_start, reporting_period_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (subsidiary_id) DO UPDATE SET
            ownership_percentage = EXCLUDED.ownership_percentage,
            voting_rights_percentage = EXCLUDED.voting_rights_percentage,
            has_control = EXCLUDED.has_control,
            consolidation_method = EXCLUDED.consolidation_method,
            is_consolidated = EXCLUDED.is_consolidated,
            updated_at = CURRENT_TIMESTAMP
        """, (subsidiary.subsidiary_id, subsidiary.subsidiary_code, subsidiary.subsidiary_name,
              subsidiary.parent_company_id, subsidiary.ownership_percentage,
              subsidiary.voting_rights_percentage, subsidiary.control_assessment.has_control,
              subsidiary.consolidation_method, subsidiary.is_consolidated,
              subsidiary.reporting_period_start, subsidiary.reporting_period_end))

    # 存储抵消分录
    for elimination in consolidated_data.elimination_entries.elimination_entries:
        cursor.execute("""
            INSERT INTO elimination_entries
            (elimination_id, elimination_date, reporting_period, elimination_type,
             debit_account, credit_account, elimination_amount, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (elimination_id) DO UPDATE SET
            elimination_amount = EXCLUDED.elimination_amount,
            description = EXCLUDED.description
        """, (elimination.elimination_id, elimination.elimination_date,
              elimination.reporting_period, elimination.elimination_type,
              elimination.debit_account, elimination.credit_account,
              elimination.elimination_amount, elimination.description))

    # 存储合并资产负债表
    balance_sheet = consolidated_data.consolidated_statements.consolidated_balance_sheet
    cursor.execute("""
        INSERT INTO consolidated_balance_sheets
        (report_id, report_date, reporting_period, total_assets, total_liabilities,
         total_equity, minority_interest, is_balanced)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (report_id) DO UPDATE SET
        total_assets = EXCLUDED.total_assets,
        total_liabilities = EXCLUDED.total_liabilities,
        total_equity = EXCLUDED.total_equity,
        minority_interest = EXCLUDED.minority_interest,
        is_balanced = EXCLUDED.is_balanced
    """, (f"BS-{balance_sheet.report_date}", balance_sheet.report_date,
          balance_sheet.reporting_period, balance_sheet.consolidated_assets.total_assets,
          balance_sheet.consolidated_liabilities.total_liabilities,
          balance_sheet.consolidated_equity.total_equity,
          balance_sheet.consolidated_equity.minority_interest,
          balance_sheet.is_balanced))

    # 存储合并利润表
    income_statement = consolidated_data.consolidated_statements.consolidated_income_statement
    cursor.execute("""
        INSERT INTO consolidated_income_statements
        (report_id, period_start, period_end, total_revenue, total_expenses,
         net_income, net_income_attributable_to_parent, net_income_attributable_to_minority)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (report_id) DO UPDATE SET
        total_revenue = EXCLUDED.total_revenue,
        total_expenses = EXCLUDED.total_expenses,
        net_income = EXCLUDED.net_income,
        net_income_attributable_to_parent = EXCLUDED.net_income_attributable_to_parent,
        net_income_attributable_to_minority = EXCLUDED.net_income_attributable_to_minority
    """, (f"IS-{income_statement.period_end}", income_statement.period_start,
          income_statement.period_end, income_statement.consolidated_revenue.total_revenue,
          income_statement.consolidated_expenses.total_expenses,
          income_statement.net_income,
          income_statement.net_income_attributable_to_parent,
          income_statement.net_income_attributable_to_minority))

    conn.commit()

def generate_consolidated_report(conn, period_start, period_end):
    """生成合并报表"""
    cursor = conn.cursor()

    # 查询合并范围
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

    scope_report = cursor.fetchall()

    # 查询合并资产负债表
    cursor.execute("""
        SELECT
            cbs.report_date,
            cbs.total_assets,
            cbs.total_liabilities,
            cbs.total_equity,
            cbs.minority_interest
        FROM consolidated_balance_sheets cbs
        WHERE cbs.report_date BETWEEN %s AND %s
        ORDER BY cbs.report_date
    """, (period_start, period_end))

    balance_sheet_report = cursor.fetchall()

    # 查询合并利润表
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

    income_statement_report = cursor.fetchall()

    return {
        "scope_report": scope_report,
        "balance_sheet_report": balance_sheet_report,
        "income_statement_report": income_statement_report
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
