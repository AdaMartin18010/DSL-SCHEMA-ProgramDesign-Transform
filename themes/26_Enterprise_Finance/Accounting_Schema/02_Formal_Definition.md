# 会计Schema形式化定义

## 📑 目录

- [会计Schema形式化定义](#会计schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 财务会计Schema](#2-财务会计schema)
  - [3. 管理会计Schema](#3-管理会计Schema)
  - [4. 成本会计Schema](#4-成本会计Schema)
  - [5. 税务会计Schema](#5-税务会计Schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)

---

## 1. 形式化模型

**定义1（会计Schema）**：
会计Schema是一个四元组：

```text
Accounting_Schema = (Financial_Accounting, Management_Accounting,
                    Cost_Accounting, Tax_Accounting)
```

其中：

- `Financial_Accounting`：财务会计Schema
- `Management_Accounting`：管理会计Schema
- `Cost_Accounting`：成本会计Schema
- `Tax_Accounting`：税务会计Schema

---

## 2. 财务会计Schema

**定义2（财务会计Schema）**：

```text
Financial_Accounting_Schema = (Chart_of_Accounts, Journal_Entry,
                                General_Ledger, Trial_Balance,
                                Financial_Statements)
```

**形式化DSL定义**：

```dsl
schema FinancialAccounting {
  chart_of_accounts: List<Account> {
    account_code: String @required @pattern("^[0-9]{1,10}$")
    account_name: String @required
    account_type: Enum { Asset, Liability, Equity, Revenue, Expense } @required
    parent_account: Optional<String>
    level: Int @range(1, 10)
    is_active: Boolean @default(true)
  }

  journal_entries: List<JournalEntry> {
    entry_id: String @required @unique
    entry_date: Date @required
    entry_type: Enum { Manual, Automatic, Reversal } @required
    description: String
    lines: List<JournalLine> @required @min_size(2) {
      account_code: String @required
      debit_amount: Decimal @range(0, null)
      credit_amount: Decimal @range(0, null)
      cost_center: Optional<String>
    }
    total_debit: Decimal @required
    total_credit: Decimal @required
    balance: Decimal @default(0) @constraint("total_debit == total_credit")
  }

  general_ledger: GeneralLedger {
    account_code: String @required
    period_start: Date @required
    period_end: Date @required
    opening_balance: Decimal @default(0)
    debit_total: Decimal @default(0)
    credit_total: Decimal @default(0)
    closing_balance: Decimal @computed("opening_balance + debit_total - credit_total")
  }

  trial_balance: TrialBalance {
    period_end: Date @required
    accounts: List<TrialBalanceAccount> {
      account_code: String @required
      debit_balance: Decimal @default(0)
      credit_balance: Decimal @default(0)
    }
    total_debit: Decimal @computed("sum(accounts.debit_balance)")
    total_credit: Decimal @computed("sum(accounts.credit_balance)")
    is_balanced: Boolean @computed("total_debit == total_credit")
  }

  financial_statements: FinancialStatements {
    balance_sheet: BalanceSheet {
      report_date: Date @required
      assets: Map<String, Decimal>
      liabilities: Map<String, Decimal>
      equity: Map<String, Decimal>
      total_assets: Decimal @computed("sum(assets.values())")
      total_liabilities_equity: Decimal @computed("sum(liabilities.values()) + sum(equity.values())")
    }
    income_statement: IncomeStatement {
      period_start: Date @required
      period_end: Date @required
      revenue: Map<String, Decimal>
      expenses: Map<String, Decimal>
      net_income: Decimal @computed("sum(revenue.values()) - sum(expenses.values())")
    }
    cash_flow_statement: CashFlowStatement {
      period_start: Date @required
      period_end: Date @required
      operating_activities: Map<String, Decimal>
      investing_activities: Map<String, Decimal>
      financing_activities: Map<String, Decimal>
      net_cash_flow: Decimal @computed("sum(operating_activities.values()) + sum(investing_activities.values()) + sum(financing_activities.values())")
    }
  }
} @standard("IFRS", "GAAP")
```

---

## 3. 管理会计Schema

**定义3（管理会计Schema）**：

```text
Management_Accounting_Schema = (Cost_Center, Profit_Center,
                                Variance_Analysis, Performance_Reports)
```

**形式化DSL定义**：

```dsl
schema ManagementAccounting {
  cost_centers: List<CostCenter> {
    cost_center_code: String @required @unique
    cost_center_name: String @required
    department: String @required
    manager: Optional<String>
    budget_amount: Decimal @default(0)
    actual_amount: Decimal @default(0)
    variance: Decimal @computed("actual_amount - budget_amount")
  }

  profit_centers: List<ProfitCenter> {
    profit_center_code: String @required @unique
    profit_center_name: String @required
    revenue: Decimal @default(0)
    costs: Decimal @default(0)
    profit: Decimal @computed("revenue - costs")
    profit_margin: Decimal @computed("profit / revenue * 100")
  }

  variance_analysis: VarianceAnalysis {
    budget_variance: BudgetVariance {
      budget_amount: Decimal @required
      actual_amount: Decimal @required
      variance: Decimal @computed("actual_amount - budget_amount")
      variance_percentage: Decimal @computed("variance / budget_amount * 100")
    }
    volume_variance: VolumeVariance {
      budget_volume: Decimal @required
      actual_volume: Decimal @required
      standard_price: Decimal @required
      variance: Decimal @computed("(actual_volume - budget_volume) * standard_price")
    }
    price_variance: PriceVariance {
      budget_price: Decimal @required
      actual_price: Decimal @required
      actual_volume: Decimal @required
      variance: Decimal @computed("(actual_price - budget_price) * actual_volume")
    }
    efficiency_variance: EfficiencyVariance {
      budget_hours: Decimal @required
      actual_hours: Decimal @required
      standard_rate: Decimal @required
      variance: Decimal @computed("(actual_hours - budget_hours) * standard_rate")
    }
  }

  performance_reports: PerformanceReports {
    responsibility_center_report: ResponsibilityCenterReport {
      center_code: String @required
      period_start: Date @required
      period_end: Date @required
      budget_data: Map<String, Decimal>
      actual_data: Map<String, Decimal>
      variance_data: Map<String, Decimal>
    }
    budget_execution_report: BudgetExecutionReport {
      period_start: Date @required
      period_end: Date @required
      budget_items: List<BudgetItem> {
        item_code: String @required
        budget_amount: Decimal @required
        actual_amount: Decimal @default(0)
        variance: Decimal @computed("actual_amount - budget_amount")
      }
    }
  }
} @standard("COSO")
```

---

## 4. 成本会计Schema

**定义4（成本会计Schema）**：

```text
Cost_Accounting_Schema = (Cost_Object, Cost_Allocation,
                         Activity_Based_Costing, Standard_Costing)
```

**形式化DSL定义**：

```dsl
schema CostAccounting {
  cost_objects: List<CostObject> {
    object_id: String @required @unique
    object_type: Enum { Product, Service, Project, Order } @required
    object_code: String @required
    direct_costs: Decimal @default(0)
    allocated_costs: Decimal @default(0)
    total_costs: Decimal @computed("direct_costs + allocated_costs")
  }

  cost_allocation: CostAllocation {
    allocation_base: AllocationBase {
      base_type: Enum { DirectLabor, MachineHours, SquareFeet } @required
      base_amount: Decimal @required
    }
    allocation_method: Enum { Direct, StepDown, Reciprocal } @required
    allocated_costs: List<AllocatedCost> {
      cost_center_code: String @required
      allocation_amount: Decimal @required
      allocation_rate: Decimal @computed("allocation_amount / allocation_base.base_amount")
    }
  }

  activity_based_costing: ActivityBasedCosting {
    activities: List<Activity> {
      activity_id: String @required @unique
      activity_name: String @required
      cost_pool: Decimal @default(0)
      cost_driver: String @required
      driver_quantity: Decimal @default(0)
      activity_rate: Decimal @computed("cost_pool / driver_quantity")
    }
    cost_objects: List<ABCCostObject> {
      object_id: String @required
      activity_consumption: Map<String, Decimal>
      allocated_costs: Decimal @computed("sum(activity_consumption.values() * activity_rate)")
    }
  }

  standard_costing: StandardCosting {
    standard_costs: List<StandardCost> {
      product_code: String @required
      material_cost: Decimal @required
      labor_cost: Decimal @required
      overhead_cost: Decimal @required
      total_standard_cost: Decimal @computed("material_cost + labor_cost + overhead_cost")
    }
    cost_variance: CostVariance {
      standard_cost: Decimal @required
      actual_cost: Decimal @required
      variance: Decimal @computed("actual_cost - standard_cost")
      price_variance: Decimal
      quantity_variance: Decimal
    }
  }
} @standard("ABC", "Standard Costing")
```

---

## 5. 税务会计Schema

**定义5（税务会计Schema）**：

```text
Tax_Accounting_Schema = (Tax_Code, Tax_Calculation,
                        Tax_Returns, Tax_Compliance)
```

**形式化DSL定义**：

```dsl
schema TaxAccounting {
  tax_codes: List<TaxCode> {
    tax_code: String @required @unique
    tax_type: Enum { VAT, IncomeTax, SalesTax, PropertyTax } @required
    tax_rate: Decimal @required @range(0, 100)
    tax_base: Enum { Amount, Quantity } @required
    exemption_conditions: Optional<String>
  }

  tax_calculations: TaxCalculations {
    taxable_amount: Decimal @required
    tax_code: String @required
    tax_rate: Decimal @required
    tax_amount: Decimal @computed("taxable_amount * tax_rate / 100")
    tax_included: Boolean @default(false)
    net_amount: Decimal @computed("tax_included ? taxable_amount : taxable_amount + tax_amount")
  }

  tax_returns: TaxReturns {
    return_id: String @required @unique
    return_type: Enum { Monthly, Quarterly, Annual } @required
    period_start: Date @required
    period_end: Date @required
    taxable_income: Decimal @required
    tax_deductions: Decimal @default(0)
    tax_credits: Decimal @default(0)
    tax_owed: Decimal @computed("(taxable_income - tax_deductions) * tax_rate - tax_credits")
    tax_paid: Decimal @default(0)
    tax_refund: Decimal @computed("tax_paid - tax_owed")
    filing_status: Enum { Draft, Submitted, Approved, Rejected } @default("Draft")
  }

  tax_compliance: TaxCompliance {
    compliance_check: ComplianceCheck {
      check_date: Date @required
      check_type: Enum { Filing, Payment, Reporting } @required
      is_compliant: Boolean @required
      violations: List<String>
    }
    audit_support: AuditSupport {
      audit_period_start: Date @required
      audit_period_end: Date @required
      supporting_documents: List<String>
      tax_records: List<TaxRecord>
    }
  }
} @standard("Tax Law")
```

---

## 6. 类型系统

**定义6（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date,
               Enum, List, Map, Object, Optional}
```

**类型约束**：

- `String`：字符串类型，支持模式匹配
- `Decimal`：十进制数值类型，支持精度控制
- `Date`：日期类型，格式：YYYY-MM-DD
- `DateTime`：日期时间类型，格式：YYYY-MM-DD HH:MM:SS
- `Enum`：枚举类型，限定值集合
- `List<T>`：列表类型，元素类型为T
- `Map<K, V>`：映射类型，键类型为K，值类型为V
- `Optional<T>`：可选类型，值可为空

---

## 7. 约束规则

**定义7（约束规则）**：

1. **唯一性约束**：`account_code`、`entry_id`、`cost_center_code`等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：`@range(min, max)`限制数值范围
4. **模式约束**：`@pattern(regex)`限制字符串格式
5. **计算约束**：`@computed(expression)`计算字段值
6. **借贷平衡约束**：凭证借贷金额必须相等
7. **试算平衡约束**：试算平衡表借贷总额必须相等

---

## 8. 转换函数

**定义8（转换函数）**：

```text
转换函数集合 = {
  convert_to_xbrl: Accounting_Schema → XBRL_Schema,
  convert_to_ifrs: Accounting_Schema → IFRS_Report,
  convert_to_gaap: Accounting_Schema → GAAP_Report,
  convert_to_database: Accounting_Schema → PostgreSQL_Schema
}
```

---

## 9. 形式化定理

### 9.1 会计等式定理

**定理1（会计等式）**：
对于任何会计期间，资产总额等于负债总额加所有者权益总额：

```text
Assets = Liabilities + Equity
```

**证明**：根据复式记账原理，每笔交易都同时影响至少两个账户，且借贷平衡，因此资产总额始终等于负债加所有者权益总额。

### 9.2 借贷平衡定理

**定理2（借贷平衡）**：
对于任何凭证，借方总额等于贷方总额：

```text
∑Debit = ∑Credit
```

**证明**：根据复式记账原理，每笔交易必须同时有借方和贷方，且金额相等，因此凭证借贷总额必须相等。

### 9.3 试算平衡定理

**定理3（试算平衡）**：
如果所有凭证借贷平衡，则试算平衡表借贷总额相等：

```text
∀entry ∈ JournalEntries: entry.total_debit == entry.total_credit
⇒ TrialBalance.total_debit == TrialBalance.total_credit
```

**证明**：如果所有凭证借贷平衡，则所有科目的借方发生额之和等于贷方发生额之和，因此试算平衡表借贷总额相等。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
