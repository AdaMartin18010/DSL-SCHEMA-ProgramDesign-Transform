# 税务会计Schema转换体系

## 📑 目录

- [税务会计Schema转换体系](#税务会计schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 会计到税务转换](#2-会计到税务转换)
  - [3. 税务到申报转换](#3-税务到申报转换)
  - [4. 转换工具](#4-转换工具)
    - [4.1 税务计算工具](#41-税务计算工具)
  - [5. 税务数据存储与分析](#5-税务数据存储与分析)
    - [5.1 PostgreSQL税务数据存储](#51-postgresql税务数据存储)
    - [5.2 税务数据分析查询](#52-税务数据分析查询)

---

## 1. 转换体系概述

税务会计Schema转换体系支持会计数据到税务数据、税务数据到申报格式转换，
以及税务数据存储。

### 1.1 转换目标

1. **会计到税务转换**：会计数据到税务会计格式
2. **税务到申报转换**：税务数据到税务申报格式
3. **税务到数据库转换**：税务数据到PostgreSQL存储

---

## 2. 会计到税务转换

**转换规则**：

- 会计利润 → 应纳税所得额
- 会计收入 → 应税收入
- 会计费用 → 可扣除费用

**转换示例**：

```python
def convert_accounting_to_tax(accounting_data: AccountingSchema) -> TaxAccountingSchema:
    """将会计数据转换为税务数据"""
    tax_accounting = TaxAccountingSchema()

    # 转换所得税
    income_tax = IncomeTaxAccounting()

    # 计算应纳税所得额（会计利润调整）
    accounting_profit = accounting_data.income_statement.net_profit
    tax_adjustments = calculate_tax_adjustments(accounting_data)
    income_tax.tax_calculation.taxable_income = accounting_profit + tax_adjustments

    # 计算应纳所得税额
    tax_rate = get_tax_rate(accounting_data.company_code)
    income_tax.tax_calculation.tax_rate = tax_rate
    income_tax.tax_calculation.tax_payable = income_tax.tax_calculation.taxable_income * tax_rate / 100

    tax_accounting.income_tax_accounting = income_tax

    # 转换增值税
    vat_accounting = VATAccounting()

    # 转换销项税额
    for sale in accounting_data.sales_transactions:
        output_vat = OutputVAT()
        output_vat.transaction_id = sale.transaction_id
        output_vat.transaction_amount = sale.amount
        output_vat.vat_rate = get_vat_rate(sale.product_type)
        output_vat.vat_amount = sale.amount * output_vat.vat_rate / 100
        vat_accounting.output_vat.append(output_vat)

    # 转换进项税额
    for purchase in accounting_data.purchase_transactions:
        input_vat = InputVAT()
        input_vat.transaction_id = purchase.transaction_id
        input_vat.transaction_amount = purchase.amount
        input_vat.vat_rate = get_vat_rate(purchase.product_type)
        input_vat.vat_amount = purchase.amount * input_vat.vat_rate / 100
        input_vat.is_deductible = check_deductible(purchase)
        vat_accounting.input_vat.append(input_vat)

    tax_accounting.vat_accounting = vat_accounting

    return tax_accounting
```

---

## 3. 税务到申报转换

**转换规则**：

- 税务数据 → 税务申报表数据
- 税务计算 → 税务申报金额
- 税务期间 → 税务申报期间

**转换示例**：

```python
def convert_tax_to_filing(tax_data: TaxAccountingSchema) -> TaxFiling:
    """将税务数据转换为税务申报格式"""
    tax_filing = TaxFiling()

    # 转换所得税申报
    income_tax_return = TaxReturn()
    income_tax_return.return_type = "IncomeTax"
    income_tax_return.filing_period = tax_data.income_tax_accounting.tax_calculation.filing_period
    income_tax_return.tax_amount = tax_data.income_tax_accounting.tax_calculation.net_tax_payable

    # 添加申报数据
    filing_data = TaxFilingData()
    filing_data.return_id = income_tax_return.return_id
    filing_data.data_item = "Taxable Income"
    filing_data.data_value = tax_data.income_tax_accounting.tax_calculation.taxable_income
    filing_data.data_type = "Revenue"
    tax_filing.tax_filing_data.append(filing_data)

    tax_filing.tax_returns.append(income_tax_return)

    # 转换增值税申报
    vat_return = TaxReturn()
    vat_return.return_type = "VAT"
    vat_return.filing_period = tax_data.vat_accounting.vat_payable.filing_period
    vat_return.tax_amount = tax_data.vat_accounting.vat_payable.vat_payable_amount

    tax_filing.tax_returns.append(vat_return)

    return tax_filing
```

---

## 4. 转换工具

### 4.1 税务计算工具

- **税务计算软件**：基于IAS 12、VAT/GST标准的税务计算
- **税务申报软件**：税务申报表生成和提交
- **ERP税务模块**：与SAP、Oracle等ERP系统集成

---

## 5. 税务数据存储与分析

### 5.1 PostgreSQL税务数据存储

**表结构设计**：

```sql
-- 所得税费用表
CREATE TABLE income_tax_expense (
    expense_id VARCHAR(50) PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL,
    tax_period DATE NOT NULL,
    current_tax_expense DECIMAL(18, 2) DEFAULT 0,
    deferred_tax_expense DECIMAL(18, 2) DEFAULT 0,
    total_tax_expense DECIMAL(18, 2) GENERATED ALWAYS AS (current_tax_expense + deferred_tax_expense) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 递延所得税资产表
CREATE TABLE deferred_tax_assets (
    asset_id VARCHAR(50) PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL,
    temporary_difference DECIMAL(18, 2) NOT NULL,
    tax_rate DECIMAL(5, 2) NOT NULL,
    asset_amount DECIMAL(18, 2) GENERATED ALWAYS AS (temporary_difference * tax_rate / 100) STORED,
    recognition_date DATE NOT NULL,
    reversal_date DATE
);

-- 增值税表
CREATE TABLE vat_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_amount DECIMAL(18, 2) NOT NULL,
    vat_rate DECIMAL(5, 2) NOT NULL,
    vat_amount DECIMAL(18, 2) GENERATED ALWAYS AS (transaction_amount * vat_rate / 100) STORED,
    transaction_date DATE NOT NULL,
    is_output_vat BOOLEAN NOT NULL
);

-- 税务申报表
CREATE TABLE tax_returns (
    return_id VARCHAR(50) PRIMARY KEY,
    return_type VARCHAR(50) NOT NULL,
    company_code VARCHAR(50) NOT NULL,
    filing_period DATE NOT NULL,
    filing_date DATE NOT NULL,
    tax_amount DECIMAL(18, 2) NOT NULL,
    filing_status VARCHAR(50) DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_income_tax_expense_company_period ON income_tax_expense(company_code, tax_period);
CREATE INDEX idx_vat_transactions_date ON vat_transactions(transaction_date);
CREATE INDEX idx_tax_returns_company_period ON tax_returns(company_code, filing_period);
```

**数据插入示例**：

```python
def store_tax_data(tax_data: TaxAccountingSchema, conn):
    """存储税务数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入所得税费用
    expense_id = f"ITE-{tax_data.company_code}-{tax_data.income_tax_accounting.tax_calculation.filing_period}"
    cursor.execute("""
        INSERT INTO income_tax_expense
        (expense_id, company_code, tax_period, current_tax_expense, deferred_tax_expense)
        VALUES (%s, %s, %s, %s, %s)
    """, (expense_id, tax_data.company_code,
          tax_data.income_tax_accounting.tax_calculation.filing_period,
          tax_data.income_tax_accounting.tax_expense.current_tax_expense,
          tax_data.income_tax_accounting.tax_expense.deferred_tax_expense))

    # 插入增值税交易
    for output_vat in tax_data.vat_accounting.output_vat:
        cursor.execute("""
            INSERT INTO vat_transactions
            (transaction_id, transaction_type, transaction_amount, vat_rate, transaction_date, is_output_vat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (output_vat.transaction_id, output_vat.transaction_type,
              output_vat.transaction_amount, output_vat.vat_rate,
              output_vat.transaction_date, True))

    conn.commit()
```

### 5.2 税务数据分析查询

**查询示例**：

```python
def analyze_tax_data(conn, company_code, period_start, period_end):
    """分析税务数据"""
    cursor = conn.cursor()

    # 查询所得税费用趋势
    cursor.execute("""
        SELECT
            tax_period,
            current_tax_expense,
            deferred_tax_expense,
            total_tax_expense
        FROM income_tax_expense
        WHERE company_code = %s AND tax_period BETWEEN %s AND %s
        ORDER BY tax_period
    """, (company_code, period_start, period_end))

    income_tax_trends = cursor.fetchall()

    # 查询增值税汇总
    cursor.execute("""
        SELECT
            DATE_TRUNC('month', transaction_date) as month,
            SUM(CASE WHEN is_output_vat THEN vat_amount ELSE 0 END) as total_output_vat,
            SUM(CASE WHEN NOT is_output_vat THEN vat_amount ELSE 0 END) as total_input_vat,
            SUM(CASE WHEN is_output_vat THEN vat_amount ELSE -vat_amount END) as net_vat
        FROM vat_transactions
        WHERE transaction_date BETWEEN %s AND %s
        GROUP BY DATE_TRUNC('month', transaction_date)
        ORDER BY month
    """, (period_start, period_end))

    vat_summary = cursor.fetchall()

    return {
        "income_tax_trends": income_tax_trends,
        "vat_summary": vat_summary
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
