# 财务报告Schema转换体系

## 📑 目录

- [财务报告Schema转换体系](#财务报告schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 会计到财务报告转换](#2-会计到财务报告转换)
  - [3. 财务报告到XBRL转换](#3-财务报告到xbrl转换)
  - [4. 财务报告到IFRS转换](#4-财务报告到ifrs转换)
  - [5. 转换工具](#5-转换工具)
    - [5.1 财务报告生成工具](#51-财务报告生成工具)
  - [6. 财务报告数据存储与分析](#6-财务报告数据存储与分析)
    - [6.1 PostgreSQL财务报告数据存储](#61-postgresql财务报告数据存储)
    - [6.2 财务报告数据分析查询](#62-财务报告数据分析查询)

---

## 1. 转换体系概述

财务报告Schema转换体系支持会计数据到财务报告、财务报告到XBRL/IFRS格式转换，
以及财务报告数据存储。

### 1.1 转换目标

1. **会计到财务报告转换**：会计数据到财务报告格式
2. **财务报告到XBRL转换**：财务报告到XBRL格式
3. **财务报告到IFRS转换**：财务报告到IFRS格式
4. **财务报告到数据库转换**：财务报告数据到PostgreSQL存储

---

## 2. 会计到财务报告转换

**转换规则**：

- 会计科目余额 → 财务报表项目
- 总账数据 → 财务报表金额
- 会计期间 → 财务报表期间

**转换示例**：

```python
def convert_accounting_to_financial_report(accounting_data: AccountingSchema) -> FinancialReportingSchema:
    """将会计数据转换为财务报告"""
    financial_report = FinancialReportingSchema()

    # 转换资产负债表
    balance_sheet = BalanceSheet()
    balance_sheet.report_date = accounting_data.period_end

    # 转换资产
    for account in accounting_data.chart_of_accounts:
        if account.account_type == "Asset":
            if account.account_code.startswith("1"):  # 流动资产
                balance_sheet.assets.current_assets[account.account_name] = account.closing_balance
            else:  # 非流动资产
                balance_sheet.assets.non_current_assets[account.account_name] = account.closing_balance

    # 转换负债和权益
    for account in accounting_data.chart_of_accounts:
        if account.account_type == "Liability":
            if account.account_code.startswith("2"):  # 流动负债
                balance_sheet.liabilities.current_liabilities[account.account_name] = account.closing_balance
            else:  # 非流动负债
                balance_sheet.liabilities.non_current_liabilities[account.account_name] = account.closing_balance
        elif account.account_type == "Equity":
            balance_sheet.equity[account.account_name] = account.closing_balance

    financial_report.balance_sheet = balance_sheet

    # 转换利润表
    income_statement = IncomeStatement()
    income_statement.period_start = accounting_data.period_start
    income_statement.period_end = accounting_data.period_end

    for account in accounting_data.chart_of_accounts:
        if account.account_type == "Revenue":
            income_statement.revenue.operating_revenue[account.account_name] = account.period_total
        elif account.account_type == "Expense":
            income_statement.expenses.operating_expenses[account.account_name] = account.period_total

    financial_report.income_statement = income_statement

    return financial_report
```

---

## 3. 财务报告到XBRL转换

**转换规则**：

- 财务报表项目 → XBRL Taxonomy Element
- 财务报表金额 → XBRL Fact Element
- 财务报表 → XBRL Instance Document

**转换示例**：

```python
def convert_financial_report_to_xbrl(financial_report: FinancialReportingSchema) -> XBRLInstanceDocument:
    """将财务报告转换为XBRL格式"""
    xbrl_doc = XBRLInstanceDocument()

    # 创建上下文
    context = XBRLContext()
    context.id = "context_report_date"
    context.entity_identifier = financial_report.company_code
    context.period_type = "Instant"
    context.period_end = financial_report.report_date
    xbrl_doc.contexts.append(context)

    # 转换资产负债表
    for asset_name, amount in financial_report.balance_sheet.assets.current_assets.items():
        fact = XBRLFact()
        fact.element_id = f"ifrs:Assets_Current_{asset_name}"
        fact.context_ref = context.id
        fact.unit_ref = "unit_usd"
        fact.value = str(amount)
        xbrl_doc.facts.append(fact)

    return xbrl_doc
```

---

## 4. 财务报告到IFRS转换

**转换规则**：

- 财务报表项目 → IFRS报表项目
- 财务报表金额 → IFRS报表金额
- 财务报表 → IFRS财务报表格式

**转换示例**：

```python
def convert_financial_report_to_ifrs(financial_report: FinancialReportingSchema) -> IFRSFinancialStatements:
    """将财务报告转换为IFRS格式"""
    ifrs_statements = IFRSFinancialStatements()

    # 转换资产负债表（IFRS 18格式）
    balance_sheet = IFRSBalanceSheet()
    balance_sheet.report_date = financial_report.report_date

    # IFRS 18要求按经营损益和筹资损益分类
    for asset_name, amount in financial_report.balance_sheet.assets.current_assets.items():
        ifrs_item = IFRSBalanceSheetItem()
        ifrs_item.item_name = asset_name
        ifrs_item.amount = amount
        ifrs_item.category = "Operating"  # IFRS 18分类
        balance_sheet.assets.append(ifrs_item)

    ifrs_statements.balance_sheet = balance_sheet

    # 转换利润表（IFRS 18格式）
    income_statement = IFRSIncomeStatement()
    income_statement.period_start = financial_report.period_start
    income_statement.period_end = financial_report.period_end

    # IFRS 18要求按经营损益和筹资损益分类
    for revenue_name, amount in financial_report.income_statement.revenue.operating_revenue.items():
        ifrs_item = IFRSIncomeStatementItem()
        ifrs_item.item_name = revenue_name
        ifrs_item.amount = amount
        ifrs_item.category = "Operating"  # IFRS 18分类
        income_statement.revenue.append(ifrs_item)

    ifrs_statements.income_statement = income_statement

    return ifrs_statements
```

---

## 5. 转换工具

### 5.1 财务报告生成工具

- **财务报表生成器**：基于IFRS/GAAP标准的报表生成
- **XBRL生成器**：XBRL格式财务报告生成
- **会计软件集成**：与SAP、Oracle等ERP系统集成

---

## 6. 财务报告数据存储与分析

### 6.1 PostgreSQL财务报告数据存储

**表结构设计**：

```sql
-- 资产负债表表
CREATE TABLE balance_sheets (
    report_id VARCHAR(50) PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    total_assets DECIMAL(18, 2) NOT NULL,
    total_liabilities DECIMAL(18, 2) NOT NULL,
    total_equity DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_balance CHECK (total_assets = total_liabilities + total_equity)
);

-- 利润表表
CREATE TABLE income_statements (
    report_id VARCHAR(50) PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue DECIMAL(18, 2) NOT NULL,
    total_expenses DECIMAL(18, 2) NOT NULL,
    net_profit DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 现金流量表表
CREATE TABLE cash_flow_statements (
    report_id VARCHAR(50) PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    net_operating_cash_flow DECIMAL(18, 2) NOT NULL,
    net_investing_cash_flow DECIMAL(18, 2) NOT NULL,
    net_financing_cash_flow DECIMAL(18, 2) NOT NULL,
    net_cash_flow DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_balance_sheets_company_date ON balance_sheets(company_code, report_date);
CREATE INDEX idx_income_statements_company_period ON income_statements(company_code, period_start, period_end);
```

**数据插入示例**：

```python
def store_financial_report(financial_report: FinancialReportingSchema, conn):
    """存储财务报告到PostgreSQL"""
    cursor = conn.cursor()

    report_id = f"FR-{financial_report.company_code}-{financial_report.report_date}"

    # 插入资产负债表
    cursor.execute("""
        INSERT INTO balance_sheets
        (report_id, company_code, report_date, total_assets, total_liabilities, total_equity)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (report_id, financial_report.company_code, financial_report.report_date,
          financial_report.balance_sheet.total_assets,
          financial_report.balance_sheet.total_liabilities,
          financial_report.balance_sheet.total_equity))

    # 插入利润表
    cursor.execute("""
        INSERT INTO income_statements
        (report_id, company_code, period_start, period_end, total_revenue, total_expenses, net_profit)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (report_id, financial_report.company_code,
          financial_report.income_statement.period_start,
          financial_report.income_statement.period_end,
          financial_report.income_statement.revenue.total_revenue,
          financial_report.income_statement.expenses.total_expenses,
          financial_report.income_statement.profit.net_profit))

    conn.commit()
```

### 6.2 财务报告数据分析查询

**查询示例**：

```python
def analyze_financial_reports(conn, company_code, period_start, period_end):
    """分析财务报告数据"""
    cursor = conn.cursor()

    # 查询财务比率
    cursor.execute("""
        SELECT
            bs.report_date,
            bs.total_assets,
            bs.total_liabilities,
            bs.total_equity,
            is_net.net_profit,
            (bs.total_liabilities / NULLIF(bs.total_equity, 0)) as debt_to_equity_ratio,
            (is_net.net_profit / NULLIF(bs.total_assets, 0)) as return_on_assets
        FROM balance_sheets bs
        JOIN income_statements is_net ON bs.report_id = is_net.report_id
        WHERE bs.company_code = %s AND bs.report_date BETWEEN %s AND %s
        ORDER BY bs.report_date
    """, (company_code, period_start, period_end))

    financial_ratios = cursor.fetchall()

    return financial_ratios
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
