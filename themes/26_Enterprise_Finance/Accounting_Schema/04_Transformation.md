# 会计Schema转换体系

## 📑 目录

- [会计Schema转换体系](#会计schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 会计到XBRL转换](#2-会计到xbrl转换)
  - [3. 会计到IFRS转换](#3-会计到ifrs转换)
  - [4. 会计到GAAP转换](#4-会计到gaap转换)
  - [5. 转换工具](#5-转换工具)
    - [5.1 XBRL转换工具](#51-xbrl转换工具)
    - [5.2 IFRS/GAAP转换工具](#52-ifrsgaap转换工具)
  - [6. 会计数据存储与分析](#6-会计数据存储与分析)
    - [6.1 PostgreSQL会计数据存储](#61-postgresql会计数据存储)
    - [6.2 会计数据分析查询](#62-会计数据分析查询)

---

## 1. 转换体系概述

会计Schema转换体系支持会计数据到XBRL、IFRS、GAAP格式转换，
以及会计数据存储。

### 1.1 转换目标

1. **会计到XBRL转换**：会计数据到XBRL实例文档
2. **会计到IFRS转换**：会计数据到IFRS财务报表
3. **会计到GAAP转换**：会计数据到GAAP财务报表
4. **会计到数据库转换**：会计数据到PostgreSQL存储

---

## 2. 会计到XBRL转换

**转换规则**：

- 会计科目 → XBRL Taxonomy Element
- 凭证数据 → XBRL Fact Element
- 财务报表 → XBRL Instance Document

**转换示例**：

```python
def convert_accounting_to_xbrl(accounting_data: AccountingSchema) -> XBRLInstanceDocument:
    """将会计数据转换为会计数据"""
    xbrl_doc = XBRLInstanceDocument()

    # 创建上下文
    context = XBRLContext()
    context.entity_identifier = accounting_data.company_code
    context.period_start = accounting_data.period_start
    context.period_end = accounting_data.period_end
    xbrl_doc.contexts.append(context)

    # 转换会计科目余额
    for account in accounting_data.chart_of_accounts:
        fact = XBRLFact()
        fact.context_ref = context.id
        fact.unit_ref = "USD"
        fact.name = f"account_{account.account_code}"
        fact.value = account.closing_balance
        xbrl_doc.facts.append(fact)

    return xbrl_doc
```

---

## 3. 会计到IFRS转换

**转换规则**：

- 会计科目 → IFRS报表项目
- 凭证数据 → IFRS报表金额
- 财务报表 → IFRS财务报表格式

**转换示例**：

```python
def convert_accounting_to_ifrs(accounting_data: AccountingSchema) -> IFRSFinancialStatements:
    """将会计数据转换为IFRS财务报表"""
    ifrs_statements = IFRSFinancialStatements()

    # 转换资产负债表
    balance_sheet = IFRSBalanceSheet()
    balance_sheet.report_date = accounting_data.period_end

    # 转换资产
    for account in accounting_data.chart_of_accounts:
        if account.account_type == "Asset":
            ifrs_item = IFRSBalanceSheetItem()
            ifrs_item.item_name = account.account_name
            ifrs_item.amount = account.closing_balance
            balance_sheet.assets.append(ifrs_item)

    # 转换负债和权益
    for account in accounting_data.chart_of_accounts:
        if account.account_type in ["Liability", "Equity"]:
            ifrs_item = IFRSBalanceSheetItem()
            ifrs_item.item_name = account.account_name
            ifrs_item.amount = account.closing_balance
            if account.account_type == "Liability":
                balance_sheet.liabilities.append(ifrs_item)
            else:
                balance_sheet.equity.append(ifrs_item)

    ifrs_statements.balance_sheet = balance_sheet

    # 转换利润表
    income_statement = IFRSIncomeStatement()
    income_statement.period_start = accounting_data.period_start
    income_statement.period_end = accounting_data.period_end

    for account in accounting_data.chart_of_accounts:
        if account.account_type == "Revenue":
            ifrs_item = IFRSIncomeStatementItem()
            ifrs_item.item_name = account.account_name
            ifrs_item.amount = account.period_total
            income_statement.revenue.append(ifrs_item)
        elif account.account_type == "Expense":
            ifrs_item = IFRSIncomeStatementItem()
            ifrs_item.item_name = account.account_name
            ifrs_item.amount = account.period_total
            income_statement.expenses.append(ifrs_item)

    ifrs_statements.income_statement = income_statement

    return ifrs_statements
```

---

## 4. 会计到GAAP转换

**转换规则**：

- 会计科目 → GAAP报表项目
- 凭证数据 → GAAP报表金额
- 财务报表 → GAAP财务报表格式

**转换示例**：

```python
def convert_accounting_to_gaap(accounting_data: AccountingSchema) -> GAAPFinancialStatements:
    """将会计数据转换为GAAP财务报表"""
    gaap_statements = GAAPFinancialStatements()

    # 转换资产负债表（GAAP格式）
    balance_sheet = GAAPBalanceSheet()
    balance_sheet.report_date = accounting_data.period_end

    # GAAP要求资产按流动性排序
    asset_accounts = sorted(
        [acc for acc in accounting_data.chart_of_accounts if acc.account_type == "Asset"],
        key=lambda x: x.account_code
    )

    for account in asset_accounts:
        gaap_item = GAAPBalanceSheetItem()
        gaap_item.item_name = account.account_name
        gaap_item.amount = account.closing_balance
        balance_sheet.assets.append(gaap_item)

    gaap_statements.balance_sheet = balance_sheet

    return gaap_statements
```

---

## 5. 转换工具

### 5.1 XBRL转换工具

- **Arelle**：开源XBRL工具
- **XBRL API**：XBRL处理库
- **自定义转换器**：基于Schema的转换器

### 5.2 IFRS/GAAP转换工具

- **财务报表生成器**：基于IFRS/GAAP标准的报表生成
- **会计软件集成**：与SAP、Oracle等ERP系统集成

---

## 6. 会计数据存储与分析

### 6.1 PostgreSQL会计数据存储

**表结构设计**：

```sql
-- 会计科目表
CREATE TABLE chart_of_accounts (
    account_code VARCHAR(20) PRIMARY KEY,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    parent_account VARCHAR(20),
    level INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 凭证表
CREATE TABLE journal_entries (
    entry_id VARCHAR(50) PRIMARY KEY,
    entry_date DATE NOT NULL,
    entry_type VARCHAR(20) NOT NULL,
    description TEXT,
    total_debit DECIMAL(18, 2) NOT NULL,
    total_credit DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_balance CHECK (total_debit = total_credit)
);

-- 凭证分录表
CREATE TABLE journal_lines (
    line_id SERIAL PRIMARY KEY,
    entry_id VARCHAR(50) NOT NULL,
    account_code VARCHAR(20) NOT NULL,
    debit_amount DECIMAL(18, 2) DEFAULT 0,
    credit_amount DECIMAL(18, 2) DEFAULT 0,
    cost_center VARCHAR(50),
    FOREIGN KEY (entry_id) REFERENCES journal_entries(entry_id),
    FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
);

-- 总账表
CREATE TABLE general_ledger (
    ledger_id SERIAL PRIMARY KEY,
    account_code VARCHAR(20) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    opening_balance DECIMAL(18, 2) DEFAULT 0,
    debit_total DECIMAL(18, 2) DEFAULT 0,
    credit_total DECIMAL(18, 2) DEFAULT 0,
    closing_balance DECIMAL(18, 2) NOT NULL,
    FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code),
    UNIQUE (account_code, period_start, period_end)
);

-- 创建索引
CREATE INDEX idx_journal_entries_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_lines_account ON journal_lines(account_code);
CREATE INDEX idx_general_ledger_account ON general_ledger(account_code);
CREATE INDEX idx_general_ledger_period ON general_ledger(period_start, period_end);
```

**数据插入示例**：

```python
def store_accounting_data(accounting_data: AccountingSchema, conn):
    """存储会计数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入会计科目
    for account in accounting_data.chart_of_accounts:
        cursor.execute("""
            INSERT INTO chart_of_accounts
            (account_code, account_name, account_type, parent_account, level, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_code) DO UPDATE SET
                account_name = EXCLUDED.account_name,
                updated_at = CURRENT_TIMESTAMP
        """, (account.account_code, account.account_name, account.account_type,
              account.parent_account, account.level, account.is_active))

    # 插入凭证
    for entry in accounting_data.journal_entries:
        cursor.execute("""
            INSERT INTO journal_entries
            (entry_id, entry_date, entry_type, description, total_debit, total_credit)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (entry.entry_id, entry.entry_date, entry.entry_type,
              entry.description, entry.total_debit, entry.total_credit))

        # 插入凭证分录
        for line in entry.lines:
            cursor.execute("""
                INSERT INTO journal_lines
                (entry_id, account_code, debit_amount, credit_amount, cost_center)
                VALUES (%s, %s, %s, %s, %s)
            """, (entry.entry_id, line.account_code, line.debit_amount,
                  line.credit_amount, line.cost_center))

    conn.commit()
```

### 6.2 会计数据分析查询

**查询示例**：

```python
def analyze_accounting_data(conn, period_start, period_end):
    """分析会计数据"""
    cursor = conn.cursor()

    # 查询试算平衡表
    cursor.execute("""
        SELECT
            account_code,
            account_name,
            SUM(debit_amount) as total_debit,
            SUM(credit_amount) as credit_total
        FROM journal_lines jl
        JOIN journal_entries je ON jl.entry_id = je.entry_id
        JOIN chart_of_accounts coa ON jl.account_code = coa.account_code
        WHERE je.entry_date BETWEEN %s AND %s
        GROUP BY account_code, account_name
        ORDER BY account_code
    """, (period_start, period_end))

    trial_balance = cursor.fetchall()

    # 查询财务报表
    cursor.execute("""
        SELECT
            account_type,
            SUM(closing_balance) as total_balance
        FROM general_ledger gl
        JOIN chart_of_accounts coa ON gl.account_code = coa.account_code
        WHERE gl.period_end = %s
        GROUP BY account_type
    """, (period_end,))

    financial_summary = cursor.fetchall()

    return {
        "trial_balance": trial_balance,
        "financial_summary": financial_summary
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
