# 税务会计Schema形式化定义

## 📑 目录

- [税务会计Schema形式化定义](#税务会计schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 所得税会计Schema](#2-所得税会计schema)
  - [3. 增值税会计Schema](#3-增值税会计schema)
  - [4. 税务申报Schema](#4-税务申报schema)
  - [5. 税务筹划Schema](#5-税务筹划schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 所得税费用定理](#91-所得税费用定理)
    - [9.2 增值税计算定理](#92-增值税计算定理)
    - [9.3 递延所得税资产定理](#93-递延所得税资产定理)

---

## 1. 形式化模型

**定义1（税务会计Schema）**：
税务会计Schema是一个四元组：

```text
Tax_Accounting_Schema = (Income_Tax_Accounting, VAT_Accounting,
                         Tax_Filing, Tax_Planning)
```

其中：

- `Income_Tax_Accounting`：所得税会计Schema
- `VAT_Accounting`：增值税会计Schema
- `Tax_Filing`：税务申报Schema
- `Tax_Planning`：税务筹划Schema

---

## 2. 所得税会计Schema

**定义2（所得税会计Schema）**：

```text
Income_Tax_Accounting_Schema = (Tax_Expense, Deferred_Tax_Asset,
                               Deferred_Tax_Liability, Tax_Calculation)
```

**形式化DSL定义**：

```dsl
schema IncomeTaxAccounting {
  tax_expense: TaxExpense {
    current_tax_expense: Decimal @default(0)
    deferred_tax_expense: Decimal @default(0)
    total_tax_expense: Decimal @computed("current_tax_expense + deferred_tax_expense")
  }

  deferred_tax_assets: List<DeferredTaxAsset> {
    asset_id: String @required @unique
    temporary_difference: Decimal @required
    tax_rate: Decimal @required @range(0, 100)
    asset_amount: Decimal @computed("temporary_difference * tax_rate / 100")
    recognition_date: Date @required
    reversal_date: Optional<Date>
  }

  deferred_tax_liabilities: List<DeferredTaxLiability> {
    liability_id: String @required @unique
    temporary_difference: Decimal @required
    tax_rate: Decimal @required @range(0, 100)
    liability_amount: Decimal @computed("temporary_difference * tax_rate / 100")
    recognition_date: Date @required
    reversal_date: Optional<Date>
  }

  tax_calculation: TaxCalculation {
    taxable_income: Decimal @required
    tax_rate: Decimal @required @range(0, 100)
    tax_payable: Decimal @computed("taxable_income * tax_rate / 100")
    tax_credits: Decimal @default(0)
    net_tax_payable: Decimal @computed("tax_payable - tax_credits")
  }
} @standard("IAS 12")
```

---

## 3. 增值税会计Schema

**定义3（增值税会计Schema）**：

```text
VAT_Accounting_Schema = (Output_VAT, Input_VAT, VAT_Payable, VAT_Filing)
```

**形式化DSL定义**：

```dsl
schema VATAccounting {
  output_vat: List<OutputVAT> {
    transaction_id: String @required @unique
    transaction_type: Enum { Sale, Service } @required
    transaction_amount: Decimal @required @range(0, null)
    vat_rate: Decimal @required @range(0, 100)
    vat_amount: Decimal @computed("transaction_amount * vat_rate / 100")
    transaction_date: Date @required
  }

  input_vat: List<InputVAT> {
    transaction_id: String @required @unique
    transaction_type: Enum { Purchase, Service } @required
    transaction_amount: Decimal @required @range(0, null)
    vat_rate: Decimal @required @range(0, 100)
    vat_amount: Decimal @computed("transaction_amount * vat_rate / 100")
    is_deductible: Boolean @default(true)
    transaction_date: Date @required
  }

  vat_payable: VATPayable {
    total_output_vat: Decimal @computed("sum(output_vat.vat_amount)")
    total_input_vat: Decimal @computed("sum(input_vat.vat_amount where is_deductible == true)")
    vat_payable_amount: Decimal @computed("total_output_vat - total_input_vat")
    filing_period: Date @required
  }

  vat_filing: VATFiling {
    filing_id: String @required @unique
    filing_period: Date @required
    filing_date: Date @required
    filing_status: Enum { Draft, Submitted, Approved, Rejected } @default("Draft")
    vat_payable_amount: Decimal @required
  }
} @standard("VAT/GST")
```

---

## 4. 税务申报Schema

**定义4（税务申报Schema）**：

```text
Tax_Filing_Schema = (Tax_Return, Tax_Filing_Data, Tax_Filing_Status)
```

**形式化DSL定义**：

```dsl
schema TaxFiling {
  tax_returns: List<TaxReturn> {
    return_id: String @required @unique
    return_type: Enum { IncomeTax, VAT, CorporateTax, Other } @required
    filing_period: Date @required
    filing_date: Date @required
    tax_amount: Decimal @required
    filing_status: Enum { Draft, Submitted, Approved, Rejected } @default("Draft")
  }

  tax_filing_data: List<TaxFilingData> {
    data_id: String @required @unique
    return_id: String @required
    data_item: String @required
    data_value: Decimal @required
    data_type: Enum { Revenue, Expense, Deduction, Credit } @required
  }

  tax_filing_status: TaxFilingStatus {
    return_id: String @required
    submission_date: Optional<Date>
    approval_date: Optional<Date>
    rejection_reason: Optional<String>
    status_history: List<StatusHistory> {
      status: Enum { Draft, Submitted, Approved, Rejected } @required
      status_date: Date @required
      status_comment: Optional<String>
    }
  }
} @standard("Tax Filing")
```

---

## 5. 税务筹划Schema

**定义5（税务筹划Schema）**：

```text
Tax_Planning_Schema = (Tax_Planning_Scheme, Tax_Optimization, Tax_Risk)
```

**形式化DSL定义**：

```dsl
schema TaxPlanning {
  tax_planning_schemes: List<TaxPlanningScheme> {
    scheme_id: String @required @unique
    scheme_type: Enum { Structure, Transaction, Timing, Location } @required
    scheme_objective: String @required
    expected_tax_savings: Decimal @required
    implementation_cost: Decimal @default(0)
    net_tax_benefit: Decimal @computed("expected_tax_savings - implementation_cost")
    risk_level: Enum { Low, Medium, High } @required
  }

  tax_optimization: TaxOptimization {
    optimization_id: String @required @unique
    optimization_type: Enum { Rate, Timing, Structure } @required
    current_tax_liability: Decimal @required
    optimized_tax_liability: Decimal @required
    tax_savings: Decimal @computed("current_tax_liability - optimized_tax_liability")
    optimization_effectiveness: Decimal @computed("tax_savings / current_tax_liability * 100")
  }

  tax_risks: List<TaxRisk> {
    risk_id: String @required @unique
    risk_type: Enum { Compliance, Audit, Penalty, Reputation } @required
    risk_level: Enum { Low, Medium, High, Critical } @required
    risk_description: String @required
    risk_probability: Decimal @range(0, 100)
    risk_impact: Decimal @required
    risk_mitigation: Optional<String>
  }
} @standard("Tax Planning")
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

1. **唯一性约束**：`asset_id`、`liability_id`、`return_id`等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：`@range(min, max)`限制数值范围
4. **计算约束**：`@computed(expression)`计算字段值
5. **税务平衡约束**：应交增值税等于销项税额减去可抵扣进项税额

---

## 8. 转换函数

**定义8（转换函数）**：

```text
转换函数集合 = {
  convert_accounting_to_tax: Accounting_Schema → Tax_Accounting_Schema,
  convert_tax_to_filing: Tax_Accounting_Schema → Tax_Filing_Schema,
  convert_to_database: Tax_Accounting_Schema → PostgreSQL_Schema
}
```

---

## 9. 形式化定理

### 9.1 所得税费用定理

**定理1（所得税费用）**：
所得税费用总额等于当期所得税费用加递延所得税费用：

```text
Total_Tax_Expense = Current_Tax_Expense + Deferred_Tax_Expense
```

### 9.2 增值税计算定理

**定理2（增值税计算）**：
应交增值税等于销项税额减去可抵扣进项税额：

```text
VAT_Payable = Total_Output_VAT - Total_Deductible_Input_VAT
```

### 9.3 递延所得税资产定理

**定理3（递延所得税资产）**：
递延所得税资产金额等于可抵扣暂时性差异乘以适用税率：

```text
Deferred_Tax_Asset = Temporary_Difference × Tax_Rate
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
