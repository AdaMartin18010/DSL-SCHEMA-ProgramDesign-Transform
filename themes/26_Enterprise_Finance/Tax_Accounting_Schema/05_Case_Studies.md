# 税务会计Schema实践案例

## 📑 目录

- [税务会计Schema实践案例](#税务会计schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：所得税费用核算](#2-案例1所得税费用核算)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：增值税核算](#3-案例2增值税核算)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：税务申报](#4-案例3税务申报)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：会计到税务转换](#5-案例4会计到税务转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：税务数据存储与分析系统](#6-案例5税务数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供税务会计Schema在实际应用中的实践案例。

---

## 2. 案例1：所得税费用核算

### 2.1 场景描述

**应用场景**：
企业所得税费用核算，包括当期所得税费用、递延所得税费用、递延所得税资产和负债。

**业务需求**：

- 计算当期所得税费用
- 确认递延所得税资产和负债
- 计算总所得税费用
- 支持IAS 12标准

### 2.2 Schema定义

**所得税费用核算Schema**：

```dsl
schema IncomeTaxExpenseCalculation {
  tax_expense: TaxExpense {
    current_tax_expense: Decimal @value(100000.00)
    deferred_tax_expense: Decimal @value(20000.00)
    total_tax_expense: Decimal @value(120000.00)
  }

  deferred_tax_assets: List<DeferredTaxAsset> {
    asset1: DeferredTaxAsset {
      asset_id: String @value("DTA-001")
      temporary_difference: Decimal @value(50000.00)
      tax_rate: Decimal @value(25.00)
      asset_amount: Decimal @value(12500.00)
      recognition_date: Date @value("2025-01-01")
    }
  }

  tax_calculation: TaxCalculation {
    taxable_income: Decimal @value(400000.00)
    tax_rate: Decimal @value(25.00)
    tax_payable: Decimal @value(100000.00)
    tax_credits: Decimal @value(0.00)
    net_tax_payable: Decimal @value(100000.00)
  }
} @standard("IAS 12")
```

---

## 3. 案例2：增值税核算

### 3.1 场景描述

**应用场景**：
企业增值税核算，包括销项税额、进项税额、应交增值税计算。

**业务需求**：

- 计算销项税额
- 计算进项税额
- 计算应交增值税
- 支持VAT/GST标准

### 3.2 Schema定义

**增值税核算Schema**：

```dsl
schema VATCalculation {
  output_vat: List<OutputVAT> {
    output1: OutputVAT {
      transaction_id: String @value("SALE-001")
      transaction_type: Enum @value("Sale")
      transaction_amount: Decimal @value(100000.00)
      vat_rate: Decimal @value(13.00)
      vat_amount: Decimal @value(13000.00)
      transaction_date: Date @value("2025-01-15")
    }
  }

  input_vat: List<InputVAT> {
    input1: InputVAT {
      transaction_id: String @value("PURCHASE-001")
      transaction_type: Enum @value("Purchase")
      transaction_amount: Decimal @value(50000.00)
      vat_rate: Decimal @value(13.00)
      vat_amount: Decimal @value(6500.00)
      is_deductible: Boolean @value(true)
      transaction_date: Date @value("2025-01-10")
    }
  }

  vat_payable: VATPayable {
    total_output_vat: Decimal @value(13000.00)
    total_input_vat: Decimal @value(6500.00)
    vat_payable_amount: Decimal @value(6500.00)
    filing_period: Date @value("2025-01-31")
  }
} @standard("VAT/GST")
```

---

## 4. 案例3：税务申报

### 4.1 场景描述

**应用场景**：
企业税务申报，包括所得税申报、增值税申报、申报状态管理。

**业务需求**：

- 生成税务申报表
- 提交税务申报
- 跟踪申报状态
- 管理申报数据

### 4.2 Schema定义

**税务申报Schema**：

```dsl
schema TaxFiling {
  tax_returns: List<TaxReturn> {
    return1: TaxReturn {
      return_id: String @value("RETURN-001")
      return_type: Enum @value("IncomeTax")
      filing_period: Date @value("2025-01-31")
      filing_date: Date @value("2025-02-15")
      tax_amount: Decimal @value(100000.00)
      filing_status: Enum @value("Submitted")
    }
    return2: TaxReturn {
      return_id: String @value("RETURN-002")
      return_type: Enum @value("VAT")
      filing_period: Date @value("2025-01-31")
      filing_date: Date @value("2025-02-10")
      tax_amount: Decimal @value(6500.00)
      filing_status: Enum @value("Approved")
    }
  }
} @standard("Tax Filing")
```

---

## 5. 案例4：会计到税务转换

### 5.1 场景描述

**应用场景**：
将企业会计数据转换为税务数据，用于税务核算和申报。

**业务需求**：

- 会计利润转换为应纳税所得额
- 会计收入转换为应税收入
- 会计费用转换为可扣除费用

### 5.2 实现代码

```python
from accounting_schema import AccountingSchema
from tax_accounting_schema import TaxAccountingSchema, IncomeTaxAccounting

def convert_accounting_to_tax(accounting_data: AccountingSchema) -> TaxAccountingSchema:
    """将会计数据转换为税务数据"""
    tax_accounting = TaxAccountingSchema()
    tax_accounting.company_code = accounting_data.company_code

    # 转换所得税
    income_tax = IncomeTaxAccounting()

    # 计算应纳税所得额（会计利润调整）
    accounting_profit = accounting_data.income_statement.profit.net_profit

    # 税务调整（例如：不可扣除费用、非应税收入等）
    tax_adjustments = {
        "non_deductible_expenses": 10000.00,  # 不可扣除费用
        "non_taxable_income": -5000.00  # 非应税收入（减少）
    }

    income_tax.tax_calculation.taxable_income = accounting_profit + sum(tax_adjustments.values())
    income_tax.tax_calculation.tax_rate = 25.0  # 企业所得税率25%
    income_tax.tax_calculation.tax_payable = income_tax.tax_calculation.taxable_income * 25.0 / 100

    # 计算所得税费用
    income_tax.tax_expense.current_tax_expense = income_tax.tax_calculation.tax_payable
    income_tax.tax_expense.deferred_tax_expense = calculate_deferred_tax(accounting_data)

    tax_accounting.income_tax_accounting = income_tax

    return tax_accounting

# 使用示例
accounting_data = AccountingSchema.load_from_database("2025-01")
tax_data = convert_accounting_to_tax(accounting_data)
tax_data.save_to_database()
```

---

## 6. 案例5：税务数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业税务数据存储与分析系统，支持税务数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持税务费用趋势分析
- 支持增值税汇总分析

### 6.2 实现代码

```python
import psycopg2
from tax_accounting_schema import TaxAccountingSchema, IncomeTaxAccounting, VATAccounting

class TaxDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_tax_data(self, tax_data: TaxAccountingSchema):
        """存储税务数据"""
        cursor = self.conn.cursor()

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

        self.conn.commit()

    def generate_tax_analysis(self, company_code, period_start, period_end):
        """生成税务分析报告"""
        cursor = self.conn.cursor()

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

# 使用示例
db_config = {
    "host": "localhost",
    "database": "tax_accounting",
    "user": "tax_user",
    "password": "password"
}

store = TaxDataStore(db_config)

# 生成税务分析报告
tax_analysis = store.generate_tax_analysis("COMP-001", "2025-01-01", "2025-12-31")
print("所得税费用趋势:")
for row in tax_analysis["income_tax_trends"]:
    print(f"期间: {row[0]}, 当期: {row[1]}, 递延: {row[2]}, 总计: {row[3]}")

print("\n增值税汇总:")
for row in tax_analysis["vat_summary"]:
    print(f"月份: {row[0]}, 销项: {row[1]}, 进项: {row[2]}, 应交: {row[3]}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
