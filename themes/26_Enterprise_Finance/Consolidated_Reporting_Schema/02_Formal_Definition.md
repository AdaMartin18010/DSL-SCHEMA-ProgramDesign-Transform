# 合并报表Schema形式化定义

## 📑 目录

- [合并报表Schema形式化定义](#合并报表schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 合并范围Schema](#2-合并范围schema)
  - [3. 抵消分录Schema](#3-抵消分录schema)
  - [4. 合并报表Schema](#4-合并报表schema)
  - [5. 少数股东权益Schema](#5-少数股东权益schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 合并报表平衡定理](#91-合并报表平衡定理)
    - [9.2 抵消分录完整性定理](#92-抵消分录完整性定理)
    - [9.3 少数股东权益计算定理](#93-少数股东权益计算定理)

---

## 1. 形式化模型

**定义1（合并报表Schema）**：
合并报表Schema是一个四元组：

```text
Consolidated_Reporting_Schema = (Consolidation_Scope, Elimination_Entries,
                                  Consolidated_Statements, Minority_Interest)
```

其中：

- `Consolidation_Scope`：合并范围Schema
- `Elimination_Entries`：抵消分录Schema
- `Consolidated_Statements`：合并报表Schema
- `Minority_Interest`：少数股东权益Schema

---

## 2. 合并范围Schema

**定义2（合并范围Schema）**：

```text
Consolidation_Scope_Schema = (Subsidiary, Control_Assessment, Consolidation_Method)
```

**形式化DSL定义**：

```dsl
schema ConsolidationScope {
  subsidiaries: List<Subsidiary> {
    subsidiary_id: String @required @unique
    subsidiary_code: String @required @unique
    subsidiary_name: String @required
    parent_company_id: String @required
    ownership_percentage: Decimal @range(0, 100) @required
    voting_rights_percentage: Decimal @range(0, 100) @required
    control_assessment: ControlAssessment {
      has_control: Boolean @required
      control_indicators: List<String> {
        "Majority_Voting_Rights"
        "Board_Control"
        "Management_Control"
        "Economic_Control"
      }
      control_date: Date @required
    }
    consolidation_method: Enum { Full_Consolidation, Proportional_Consolidation, Equity_Method } @required
    is_consolidated: Boolean @computed("control_assessment.has_control AND consolidation_method == 'Full_Consolidation'")
    reporting_period_start: Date @required
    reporting_period_end: Date @required
  }

  consolidation_scope_changes: List<ConsolidationScopeChange> {
    change_id: String @required @unique
    subsidiary_id: String @required
    change_type: Enum { Added, Removed, Method_Changed } @required
    change_date: Date @required
    change_reason: String @required
    approved_by: String @required
    approved_date: Date @required
  }
} @standard("IFRS10")
```

---

## 3. 抵消分录Schema

**定义3（抵消分录Schema）**：

```text
Elimination_Entries_Schema = (Intercompany_Transaction_Elimination,
                              Intercompany_Investment_Elimination,
                              Intercompany_Balance_Elimination)
```

**形式化DSL定义**：

```dsl
schema EliminationEntries {
  intercompany_transactions: List<IntercompanyTransaction> {
    transaction_id: String @required @unique
    transaction_date: Date @required
    seller_entity_id: String @required
    buyer_entity_id: String @required
    transaction_type: Enum { Sales, Purchase, Service, Loan, Other } @required
    transaction_amount: Decimal @range(0, null) @required
    transaction_currency: String @length(3) @default("CNY")
    is_eliminated: Boolean @default(false)
    elimination_entry_id: Optional<String>
  }

  elimination_entries: List<EliminationEntry> {
    elimination_id: String @required @unique
    elimination_date: Date @required
    reporting_period: Date @required
    elimination_type: Enum { Intercompany_Sales, Intercompany_Investment, Intercompany_Balance, Unrealized_Profit } @required
    debit_account: String @required
    credit_account: String @required
    elimination_amount: Decimal @required
    description: String @required
    related_transactions: List<String>
  }

  intercompany_investments: List<IntercompanyInvestment> {
    investment_id: String @required @unique
    parent_entity_id: String @required
    subsidiary_entity_id: String @required
    investment_amount: Decimal @range(0, null) @required
    investment_date: Date @required
    investment_type: Enum { Equity_Investment, Loan_Investment, Other } @required
    is_eliminated: Boolean @default(false)
    elimination_entry_id: Optional<String>
  }

  unrealized_profits: List<UnrealizedProfit> {
    profit_id: String @required @unique
    transaction_id: String @required
    profit_amount: Decimal @required
    profit_percentage: Decimal @range(0, 100) @default(100)
    is_eliminated: Boolean @default(false)
    elimination_entry_id: Optional<String>
  }
} @standard("IFRS10", "IFRS3")
```

---

## 4. 合并报表Schema

**定义4（合并报表Schema）**：

```text
Consolidated_Statements_Schema = (Consolidated_Balance_Sheet,
                                  Consolidated_Income_Statement,
                                  Consolidated_Cash_Flow_Statement)
```

**形式化DSL定义**：

```dsl
schema ConsolidatedStatements {
  consolidated_balance_sheet: ConsolidatedBalanceSheet {
    report_date: Date @required
    reporting_period: Date @required
    consolidated_assets: Map<String, Decimal> {
      current_assets: Decimal @default(0)
      non_current_assets: Decimal @default(0)
      total_assets: Decimal @computed("current_assets + non_current_assets")
    }
    consolidated_liabilities: Map<String, Decimal> {
      current_liabilities: Decimal @default(0)
      non_current_liabilities: Decimal @default(0)
      total_liabilities: Decimal @computed("current_liabilities + non_current_liabilities")
    }
    consolidated_equity: Map<String, Decimal> {
      share_capital: Decimal @default(0)
      retained_earnings: Decimal @default(0)
      minority_interest: Decimal @default(0)
      total_equity: Decimal @computed("share_capital + retained_earnings + minority_interest")
    }
    total_liabilities_equity: Decimal @computed("total_liabilities + total_equity")
    is_balanced: Boolean @computed("total_assets == total_liabilities_equity")
  }

  consolidated_income_statement: ConsolidatedIncomeStatement {
    period_start: Date @required
    period_end: Date @required
    consolidated_revenue: Map<String, Decimal> {
      operating_revenue: Decimal @default(0)
      other_revenue: Decimal @default(0)
      total_revenue: Decimal @computed("operating_revenue + other_revenue")
    }
    consolidated_expenses: Map<String, Decimal> {
      operating_expenses: Decimal @default(0)
      financial_expenses: Decimal @default(0)
      tax_expenses: Decimal @default(0)
      total_expenses: Decimal @computed("operating_expenses + financial_expenses + tax_expenses")
    }
    net_income: Decimal @computed("total_revenue - total_expenses")
    net_income_attributable_to_parent: Decimal @computed("net_income - net_income_attributable_to_minority")
    net_income_attributable_to_minority: Decimal @default(0)
  }

  consolidated_cash_flow_statement: ConsolidatedCashFlowStatement {
    period_start: Date @required
    period_end: Date @required
    operating_activities: Map<String, Decimal> {
      cash_inflows: Decimal @default(0)
      cash_outflows: Decimal @default(0)
      net_cash_flow: Decimal @computed("cash_inflows - cash_outflows")
    }
    investing_activities: Map<String, Decimal> {
      cash_inflows: Decimal @default(0)
      cash_outflows: Decimal @default(0)
      net_cash_flow: Decimal @computed("cash_inflows - cash_outflows")
    }
    financing_activities: Map<String, Decimal> {
      cash_inflows: Decimal @default(0)
      cash_outflows: Decimal @default(0)
      net_cash_flow: Decimal @computed("cash_inflows - cash_outflows")
    }
    net_cash_flow: Decimal @computed("operating_activities.net_cash_flow + investing_activities.net_cash_flow + financing_activities.net_cash_flow")
    opening_cash_balance: Decimal @required
    closing_cash_balance: Decimal @computed("opening_cash_balance + net_cash_flow")
  }
} @standard("IFRS10", "IFRS18")
```

---

## 5. 少数股东权益Schema

**定义5（少数股东权益Schema）**：

```text
Minority_Interest_Schema = (Minority_Interest_Calculation,
                           Minority_Interest_Changes,
                           Minority_Interest_Disclosure)
```

**形式化DSL定义**：

```dsl
schema MinorityInterest {
  minority_interest_calculations: List<MinorityInterestCalculation> {
    calculation_id: String @required @unique
    subsidiary_id: String @required
    reporting_period: Date @required
    ownership_percentage: Decimal @range(0, 100) @required
    parent_ownership_percentage: Decimal @computed("100 - ownership_percentage")
    subsidiary_equity: Decimal @required
    minority_interest_amount: Decimal @computed("subsidiary_equity * ownership_percentage / 100")
    subsidiary_net_income: Decimal @required
    minority_interest_share_of_income: Decimal @computed("subsidiary_net_income * ownership_percentage / 100")
  }

  minority_interest_changes: List<MinorityInterestChange> {
    change_id: String @required @unique
    subsidiary_id: String @required
    change_date: Date @required
    change_type: Enum { Opening_Balance, Net_Income_Share, Dividends, Other } @required
    change_amount: Decimal @required
    closing_balance: Decimal @computed("opening_balance + change_amount")
  }

  minority_interest_disclosure: MinorityInterestDisclosure {
    disclosure_period: Date @required
    total_minority_interest: Decimal @computed("sum(minority_interest_calculations.minority_interest_amount)")
    minority_interest_by_subsidiary: Map<String, Decimal>
    minority_interest_changes_summary: Map<String, Decimal>
  }
} @standard("IFRS10")
```

---

## 6. 类型系统

**类型定义**：

```dsl
type SubsidiaryID = String @pattern("^SUB-[0-9]{8}$")
type EliminationID = String @pattern("^ELIM-[0-9]{10}$")
type Decimal = Float @precision(18, 2) @range(0, null)
type Date = DateTime @format("YYYY-MM-DD")
type Percentage = Float @range(0, 100) @precision(5, 2)
```

---

## 7. 约束规则

**约束1（合并报表平衡约束）**：

```text
∀consolidated_balance_sheet ∈ Consolidated_Balance_Sheets:
  consolidated_balance_sheet.total_assets = consolidated_balance_sheet.total_liabilities_equity
  ∧ consolidated_balance_sheet.total_equity = consolidated_balance_sheet.share_capital
                                    + consolidated_balance_sheet.retained_earnings
                                    + consolidated_balance_sheet.minority_interest
```

**约束2（抵消分录完整性约束）**：

```text
∀intercompany_transaction ∈ Intercompany_Transactions:
  intercompany_transaction.is_eliminated == true
  → ∃elimination_entry ∈ Elimination_Entries:
    elimination_entry.related_transactions.contains(intercompany_transaction.transaction_id)
    ∧ elimination_entry.elimination_amount == intercompany_transaction.transaction_amount
```

**约束3（少数股东权益计算约束）**：

```text
∀minority_interest_calculation ∈ Minority_Interest_Calculations:
  minority_interest_calculation.minority_interest_amount =
    minority_interest_calculation.subsidiary_equity
    * minority_interest_calculation.ownership_percentage / 100
  ∧ minority_interest_calculation.minority_interest_share_of_income =
    minority_interest_calculation.subsidiary_net_income
    * minority_interest_calculation.ownership_percentage / 100
```

---

## 8. 转换函数

**转换函数1（合并报表到XBRL）**：

```text
f_Consolidated_to_XBRL: Consolidated_Statements → XBRL_Instance

f_Consolidated_to_XBRL(consolidated) = {
  xbrl_instance: {
    context: {
      entity: "Consolidated_Entity"
      period: consolidated.reporting_period
    }
    facts: {
      "ConsolidatedAssets": consolidated.consolidated_assets.total_assets
      "ConsolidatedLiabilities": consolidated.consolidated_liabilities.total_liabilities
      "ConsolidatedEquity": consolidated.consolidated_equity.total_equity
      "MinorityInterest": consolidated.consolidated_equity.minority_interest
    }
  }
}
```

---

## 9. 形式化定理

### 9.1 合并报表平衡定理

**定理1（合并报表平衡）**：

对于任意合并资产负债表，合并报表满足：

```text
total_assets = total_liabilities_equity
  ∧ total_equity = share_capital + retained_earnings + minority_interest
```

**证明**：

由约束1和类型系统定义，合并报表平衡满足上述等式。

### 9.2 抵消分录完整性定理

**定理2（抵消分录完整性）**：

对于任意内部交易，如果已抵消，则存在对应的抵消分录：

```text
intercompany_transaction.is_eliminated == true
  → ∃elimination_entry: elimination_entry.related_transactions.contains(transaction_id)
    ∧ elimination_entry.elimination_amount == transaction.transaction_amount
```

**证明**：

由约束2和类型系统定义，抵消分录完整性满足上述条件。

### 9.3 少数股东权益计算定理

**定理3（少数股东权益计算）**：

对于任意少数股东权益计算，少数股东权益满足：

```text
minority_interest_amount = subsidiary_equity * ownership_percentage / 100
  ∧ minority_interest_share_of_income = subsidiary_net_income * ownership_percentage / 100
```

**证明**：

由约束3和类型系统定义，少数股东权益计算满足上述等式。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
