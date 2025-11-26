# 财务报告Schema形式化定义

## 📑 目录

- [财务报告Schema形式化定义](#财务报告schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 资产负债表Schema](#2-资产负债表schema)
  - [3. 利润表Schema](#3-利润表schema)
  - [4. 现金流量表Schema](#4-现金流量表schema)
  - [5. 股东权益变动表Schema](#5-股东权益变动表schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)

---

## 1. 形式化模型

**定义1（财务报告Schema）**：
财务报告Schema是一个四元组：

```text
Financial_Reporting_Schema = (Balance_Sheet, Income_Statement,
                             Cash_Flow_Statement, Equity_Statement)
```

其中：

- `Balance_Sheet`：资产负债表Schema
- `Income_Statement`：利润表Schema
- `Cash_Flow_Statement`：现金流量表Schema
- `Equity_Statement`：股东权益变动表Schema

---

## 2. 资产负债表Schema

**定义2（资产负债表Schema）**：

```text
Balance_Sheet_Schema = (Assets, Liabilities, Equity)
```

**形式化DSL定义**：

```dsl
schema BalanceSheet {
  report_date: Date @required
  assets: Assets {
    current_assets: Map<String, Decimal> {
      cash_and_equivalents: Decimal @default(0)
      accounts_receivable: Decimal @default(0)
      inventory: Decimal @default(0)
      prepaid_expenses: Decimal @default(0)
    }
    non_current_assets: Map<String, Decimal> {
      property_plant_equipment: Decimal @default(0)
      intangible_assets: Decimal @default(0)
      investments: Decimal @default(0)
    }
    total_assets: Decimal @computed("sum(current_assets.values()) + sum(non_current_assets.values())")
  }
  liabilities: Liabilities {
    current_liabilities: Map<String, Decimal> {
      accounts_payable: Decimal @default(0)
      short_term_debt: Decimal @default(0)
      accrued_expenses: Decimal @default(0)
    }
    non_current_liabilities: Map<String, Decimal> {
      long_term_debt: Decimal @default(0)
      deferred_tax_liabilities: Decimal @default(0)
    }
    total_liabilities: Decimal @computed("sum(current_liabilities.values()) + sum(non_current_liabilities.values())")
  }
  equity: Equity {
    share_capital: Decimal @default(0)
    capital_reserve: Decimal @default(0)
    retained_earnings: Decimal @default(0)
    total_equity: Decimal @computed("share_capital + capital_reserve + retained_earnings")
  }
  total_liabilities_equity: Decimal @computed("total_liabilities + total_equity")
  balance_check: Boolean @computed("total_assets == total_liabilities_equity")
} @standard("IFRS 18", "GAAP")
```

---

## 3. 利润表Schema

**定义3（利润表Schema）**：

```text
Income_Statement_Schema = (Revenue, Expenses, Profit)
```

**形式化DSL定义**：

```dsl
schema IncomeStatement {
  period_start: Date @required
  period_end: Date @required
  revenue: Revenue {
    operating_revenue: Map<String, Decimal> {
      sales_revenue: Decimal @default(0)
      service_revenue: Decimal @default(0)
    }
    other_revenue: Map<String, Decimal> {
      interest_income: Decimal @default(0)
      other_income: Decimal @default(0)
    }
    total_revenue: Decimal @computed("sum(operating_revenue.values()) + sum(other_revenue.values())")
  }
  expenses: Expenses {
    cost_of_sales: Decimal @default(0)
    operating_expenses: Map<String, Decimal> {
      selling_expenses: Decimal @default(0)
      administrative_expenses: Decimal @default(0)
      research_development: Decimal @default(0)
    }
    financial_expenses: Map<String, Decimal> {
      interest_expense: Decimal @default(0)
      foreign_exchange_loss: Decimal @default(0)
    }
    total_expenses: Decimal @computed("cost_of_sales + sum(operating_expenses.values()) + sum(financial_expenses.values())")
  }
  profit: Profit {
    operating_profit: Decimal @computed("total_revenue - cost_of_sales - sum(operating_expenses.values())")
    profit_before_tax: Decimal @computed("operating_profit - sum(financial_expenses.values()) + sum(revenue.other_revenue.values())")
    income_tax: Decimal @default(0)
    net_profit: Decimal @computed("profit_before_tax - income_tax")
  }
} @standard("IFRS 18", "IFRS 15")
```

---

## 4. 现金流量表Schema

**定义4（现金流量表Schema）**：

```text
Cash_Flow_Statement_Schema = (Operating_Activities, Investing_Activities, Financing_Activities)
```

**形式化DSL定义**：

```dsl
schema CashFlowStatement {
  period_start: Date @required
  period_end: Date @required
  operating_activities: OperatingActivities {
    cash_inflows: Map<String, Decimal> {
      cash_from_customers: Decimal @default(0)
      interest_received: Decimal @default(0)
      dividends_received: Decimal @default(0)
    }
    cash_outflows: Map<String, Decimal> {
      cash_to_suppliers: Decimal @default(0)
      cash_to_employees: Decimal @default(0)
      interest_paid: Decimal @default(0)
      taxes_paid: Decimal @default(0)
    }
    net_operating_cash_flow: Decimal @computed("sum(cash_inflows.values()) - sum(cash_outflows.values())")
  }
  investing_activities: InvestingActivities {
    cash_inflows: Map<String, Decimal> {
      proceeds_from_sale_of_assets: Decimal @default(0)
      proceeds_from_investments: Decimal @default(0)
    }
    cash_outflows: Map<String, Decimal> {
      purchase_of_assets: Decimal @default(0)
      purchase_of_investments: Decimal @default(0)
    }
    net_investing_cash_flow: Decimal @computed("sum(cash_inflows.values()) - sum(cash_outflows.values())")
  }
  financing_activities: FinancingActivities {
    cash_inflows: Map<String, Decimal> {
      proceeds_from_borrowing: Decimal @default(0)
      proceeds_from_equity: Decimal @default(0)
    }
    cash_outflows: Map<String, Decimal> {
      repayment_of_borrowing: Decimal @default(0)
      dividends_paid: Decimal @default(0)
    }
    net_financing_cash_flow: Decimal @computed("sum(cash_inflows.values()) - sum(cash_outflows.values())")
  }
  net_cash_flow: Decimal @computed("net_operating_cash_flow + net_investing_cash_flow + net_financing_cash_flow")
  opening_cash_balance: Decimal @required
  closing_cash_balance: Decimal @computed("opening_cash_balance + net_cash_flow")
} @standard("IFRS 18")
```

---

## 5. 股东权益变动表Schema

**定义5（股东权益变动表Schema）**：

```text
Equity_Statement_Schema = (Share_Capital_Changes, Capital_Reserve_Changes,
                          Retained_Earnings_Changes)
```

**形式化DSL定义**：

```dsl
schema EquityStatement {
  period_start: Date @required
  period_end: Date @required
  share_capital_changes: ShareCapitalChanges {
    opening_balance: Decimal @required
    increases: Map<String, Decimal> {
      new_share_issuance: Decimal @default(0)
      share_premium: Decimal @default(0)
    }
    decreases: Map<String, Decimal> {
      share_repurchase: Decimal @default(0)
    }
    closing_balance: Decimal @computed("opening_balance + sum(increases.values()) - sum(decreases.values())")
  }
  capital_reserve_changes: CapitalReserveChanges {
    opening_balance: Decimal @required
    increases: Map<String, Decimal> {
      revaluation_surplus: Decimal @default(0)
      other_reserves: Decimal @default(0)
    }
    decreases: Map<String, Decimal> {
      reserve_transfers: Decimal @default(0)
    }
    closing_balance: Decimal @computed("opening_balance + sum(increases.values()) - sum(decreases.values())")
  }
  retained_earnings_changes: RetainedEarningsChanges {
    opening_balance: Decimal @required
    net_profit: Decimal @required
    dividends_paid: Decimal @default(0)
    other_adjustments: Decimal @default(0)
    closing_balance: Decimal @computed("opening_balance + net_profit - dividends_paid + other_adjustments")
  }
  total_equity: Decimal @computed("share_capital_changes.closing_balance + capital_reserve_changes.closing_balance + retained_earnings_changes.closing_balance")
} @standard("IFRS 18")
```

---

## 6. 类型系统

**定义6（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date,
               Enum, List, Map, Object, Optional}
```

---

## 7. 约束规则

**定义7（约束规则）**：

1. **唯一性约束**：报告期间、报告日期等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **计算约束**：`@computed(expression)`计算字段值
4. **资产负债表平衡约束**：资产总额必须等于负债加所有者权益总额
5. **现金流量表平衡约束**：期末现金余额必须等于期初现金余额加净现金流量

---

## 8. 转换函数

**定义8（转换函数）**：

```text
转换函数集合 = {
  convert_accounting_to_financial_report: Accounting_Schema → Financial_Reporting_Schema,
  convert_financial_report_to_xbrl: Financial_Reporting_Schema → XBRL_Schema,
  convert_to_database: Financial_Reporting_Schema → PostgreSQL_Schema
}
```

---

## 9. 形式化定理

### 9.1 资产负债表平衡定理

**定理1（资产负债表平衡）**：
资产总额等于负债总额加所有者权益总额：

```text
Total_Assets = Total_Liabilities + Total_Equity
```

**证明**：根据会计等式，资产总额始终等于负债加所有者权益总额。

### 9.2 利润表完整性定理

**定理2（利润表完整性）**：
净利润等于收入总额减去费用总额：

```text
Net_Profit = Total_Revenue - Total_Expenses
```

**证明**：根据利润表定义，净利润等于收入减去所有费用。

### 9.3 现金流量表平衡定理

**定理3（现金流量表平衡）**：
期末现金余额等于期初现金余额加净现金流量：

```text
Closing_Cash_Balance = Opening_Cash_Balance + Net_Cash_Flow
```

**证明**：根据现金流量表定义，期末现金余额等于期初余额加所有现金流的净额。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
