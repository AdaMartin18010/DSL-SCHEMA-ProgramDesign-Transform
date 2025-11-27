# 应收应付Schema形式化定义

## 📑 目录

- [应收应付Schema形式化定义](#应收应付schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 应收账款Schema](#2-应收账款schema)
  - [3. 应付账款Schema](#3-应付账款schema)
  - [4. 发票管理Schema](#4-发票管理schema)
  - [5. 付款管理Schema](#5-付款管理schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 应收应付平衡定理](#91-应收应付平衡定理)
    - [9.2 发票金额验证定理](#92-发票金额验证定理)
    - [9.3 付款金额验证定理](#93-付款金额验证定理)

---

## 1. 形式化模型

**定义1（应收应付Schema）**：
应收应付Schema是一个四元组：

```text
AR_AP_Schema = (Accounts_Receivable, Accounts_Payable,
                Invoice_Management, Payment_Management)
```

其中：

- `Accounts_Receivable`：应收账款Schema
- `Accounts_Payable`：应付账款Schema
- `Invoice_Management`：发票管理Schema
- `Payment_Management`：付款管理Schema

---

## 2. 应收账款Schema

**定义2（应收账款Schema）**：

```text
Accounts_Receivable_Schema = (Customer, Sales_Invoice,
                              Receipt, Reconciliation)
```

**形式化DSL定义**：

```dsl
schema AccountsReceivable {
  customers: List<Customer> {
    customer_id: String @required @unique
    customer_code: String @required @unique
    customer_name: String @required
    credit_limit: Decimal @range(0, null) @default(0)
    payment_terms: String @default("NET30")
    credit_rating: Enum { AAA, AA, A, BBB, BB, B, CCC, CC, C, D } @default("A")
    is_active: Boolean @default(true)
  }

  sales_invoices: List<SalesInvoice> {
    invoice_id: String @required @unique
    invoice_number: String @required @unique
    invoice_date: Date @required
    customer_id: String @required
    due_date: Date @required
    invoice_amount: Decimal @range(0, null) @required
    tax_amount: Decimal @range(0, null) @default(0)
    total_amount: Decimal @computed("invoice_amount + tax_amount")
    status: Enum { Draft, Issued, Paid, Overdue, Cancelled } @default("Draft")
    payment_status: Enum { Unpaid, Partially_Paid, Paid } @default("Unpaid")
    paid_amount: Decimal @range(0, null) @default(0)
    outstanding_amount: Decimal @computed("total_amount - paid_amount")
  }

  receipts: List<Receipt> {
    receipt_id: String @required @unique
    receipt_number: String @required @unique
    receipt_date: Date @required
    customer_id: String @required
    invoice_id: String @required
    receipt_amount: Decimal @range(0, null) @required
    payment_method: Enum { Cash, Bank_Transfer, Check, Credit_Card, Other } @required
    bank_account: Optional<String>
    reference_number: Optional<String>
    status: Enum { Pending, Confirmed, Reversed } @default("Pending")
  }

  reconciliations: List<Reconciliation> {
    reconciliation_id: String @required @unique
    reconciliation_date: Date @required
    customer_id: String @required
    period_start: Date @required
    period_end: Date @required
    opening_balance: Decimal @default(0)
    invoice_total: Decimal @default(0)
    receipt_total: Decimal @default(0)
    closing_balance: Decimal @computed("opening_balance + invoice_total - receipt_total")
    is_balanced: Boolean @computed("abs(closing_balance) < 0.01")
  }
} @standard("IFRS15", "AR_Management")
```

---

## 3. 应付账款Schema

**定义3（应付账款Schema）**：

```text
Accounts_Payable_Schema = (Supplier, Purchase_Invoice,
                          Payment, Reconciliation)
```

**形式化DSL定义**：

```dsl
schema AccountsPayable {
  suppliers: List<Supplier> {
    supplier_id: String @required @unique
    supplier_code: String @required @unique
    supplier_name: String @required
    payment_terms: String @default("NET30")
    credit_limit: Decimal @range(0, null) @default(0)
    bank_account: Optional<String>
    is_active: Boolean @default(true)
  }

  purchase_invoices: List<PurchaseInvoice> {
    invoice_id: String @required @unique
    invoice_number: String @required @unique
    invoice_date: Date @required
    supplier_id: String @required
    due_date: Date @required
    invoice_amount: Decimal @range(0, null) @required
    tax_amount: Decimal @range(0, null) @default(0)
    total_amount: Decimal @computed("invoice_amount + tax_amount")
    status: Enum { Draft, Received, Approved, Paid, Cancelled } @default("Draft")
    payment_status: Enum { Unpaid, Partially_Paid, Paid } @default("Unpaid")
    paid_amount: Decimal @range(0, null) @default(0)
    outstanding_amount: Decimal @computed("total_amount - paid_amount")
  }

  payments: List<Payment> {
    payment_id: String @required @unique
    payment_number: String @required @unique
    payment_date: Date @required
    supplier_id: String @required
    invoice_id: String @required
    payment_amount: Decimal @range(0, null) @required
    payment_method: Enum { Bank_Transfer, Check, Credit_Card, Other } @required
    bank_account: String @required
    reference_number: Optional<String>
    status: Enum { Pending, Approved, Processed, Confirmed, Reversed } @default("Pending")
    approval_status: Enum { Pending, Approved, Rejected } @default("Pending")
  }

  reconciliations: List<Reconciliation> {
    reconciliation_id: String @required @unique
    reconciliation_date: Date @required
    supplier_id: String @required
    period_start: Date @required
    period_end: Date @required
    opening_balance: Decimal @default(0)
    invoice_total: Decimal @default(0)
    payment_total: Decimal @default(0)
    closing_balance: Decimal @computed("opening_balance + invoice_total - payment_total")
    is_balanced: Boolean @computed("abs(closing_balance) < 0.01")
  }
} @standard("IFRS15", "AP_Management")
```

---

## 4. 发票管理Schema

**定义4（发票管理Schema）**：

```text
Invoice_Management_Schema = (Invoice_Generation, Invoice_Validation,
                            Invoice_Archiving)
```

**形式化DSL定义**：

```dsl
schema InvoiceManagement {
  invoice_generation: InvoiceGeneration {
    template_id: String @required
    template_name: String @required
    invoice_type: Enum { Sales, Purchase } @required
    format: Enum { PDF, XML, EDI, JSON } @default("PDF")
    fields: Map<String, FieldDefinition> {
      invoice_number: FieldDefinition @required
      invoice_date: FieldDefinition @required
      amount: FieldDefinition @required
      tax: FieldDefinition
    }
  }

  invoice_validation: InvoiceValidation {
    validation_rules: List<ValidationRule> {
      rule_id: String @required
      rule_name: String @required
      rule_type: Enum { Format, Amount, Date, Tax, Business } @required
      rule_expression: String @required
      error_message: String @required
    }
    validation_status: Enum { Valid, Invalid, Warning } @default("Valid")
    validation_errors: List<ValidationError>
  }

  invoice_archiving: InvoiceArchiving {
    archive_id: String @required @unique
    invoice_id: String @required
    archive_date: Date @required
    storage_location: String @required
    retention_period: Int @default(7) @unit("years")
    access_level: Enum { Public, Internal, Confidential } @default("Internal")
  }
} @standard("Invoice_Standards")
```

---

## 5. 付款管理Schema

**定义5（付款管理Schema）**：

```text
Payment_Management_Schema = (Payment_Plan, Payment_Execution,
                             Payment_Reconciliation)
```

**形式化DSL定义**：

```dsl
schema PaymentManagement {
  payment_plans: List<PaymentPlan> {
    plan_id: String @required @unique
    plan_name: String @required
    supplier_id: String @required
    payment_schedule: List<PaymentScheduleItem> {
      schedule_id: String @required
      due_date: Date @required
      amount: Decimal @range(0, null) @required
      priority: Int @range(1, 10) @default(5)
      status: Enum { Pending, Scheduled, Processed, Cancelled } @default("Pending")
    }
    total_amount: Decimal @computed("sum(payment_schedule.amount)")
  }

  payment_execution: PaymentExecution {
    execution_id: String @required @unique
    payment_id: String @required
    execution_date: Date @required
    approval_workflow: ApprovalWorkflow {
      approver_id: String @required
      approval_level: Int @range(1, 5) @required
      approval_status: Enum { Pending, Approved, Rejected } @default("Pending")
      approval_date: Optional<Date>
    }
    processing_status: Enum { Pending, Processing, Completed, Failed } @default("Pending")
    confirmation_number: Optional<String>
  }

  payment_reconciliation: PaymentReconciliation {
    reconciliation_id: String @required @unique
    reconciliation_date: Date @required
    bank_statement_id: String @required
    payment_matches: List<PaymentMatch> {
      match_id: String @required
      payment_id: String @required
      statement_line_id: String @required
      match_status: Enum { Matched, Unmatched, Disputed } @default("Unmatched")
      difference_amount: Decimal @default(0)
    }
    total_matched: Decimal @computed("sum(payment_matches where match_status == 'Matched')")
    total_unmatched: Decimal @computed("sum(payment_matches where match_status == 'Unmatched')")
    is_reconciled: Boolean @computed("total_unmatched == 0")
  }
} @standard("Payment_Standards")
```

---

## 6. 类型系统

**类型定义**：

```dsl
type CustomerID = String @pattern("^CUST-[0-9]{8}$")
type SupplierID = String @pattern("^SUPP-[0-9]{8}$")
type InvoiceID = String @pattern("^INV-[0-9]{10}$")
type PaymentID = String @pattern("^PAY-[0-9]{10}$")
type Decimal = Float @precision(18, 2) @range(0, null)
type Date = DateTime @format("YYYY-MM-DD")
type Currency = Enum { USD, EUR, CNY, JPY, GBP } @default("CNY")
```

---

## 7. 约束规则

**约束1（发票金额约束）**：

```text
∀invoice ∈ Sales_Invoices ∪ Purchase_Invoices:
  invoice.total_amount = invoice.invoice_amount + invoice.tax_amount
  ∧ invoice.outstanding_amount = invoice.total_amount - invoice.paid_amount
  ∧ invoice.outstanding_amount ≥ 0
```

**约束2（收款金额约束）**：

```text
∀receipt ∈ Receipts:
  receipt.receipt_amount ≤ invoice.outstanding_amount
  ∧ invoice.paid_amount = sum(receipt.receipt_amount where receipt.invoice_id == invoice.invoice_id)
```

**约束3（付款金额约束）**：

```text
∀payment ∈ Payments:
  payment.payment_amount ≤ invoice.outstanding_amount
  ∧ invoice.paid_amount = sum(payment.payment_amount where payment.invoice_id == invoice.invoice_id)
```

**约束4（对账平衡约束）**：

```text
∀reconciliation ∈ Reconciliations:
  reconciliation.closing_balance = reconciliation.opening_balance
                                + reconciliation.invoice_total
                                - reconciliation.receipt_total
  ∧ abs(reconciliation.closing_balance) < 0.01
```

---

## 8. 转换函数

**转换函数1（应收到总账）**：

```text
f_AR_to_GL: Accounts_Receivable → General_Ledger

f_AR_to_GL(ar) = {
  journal_entry: {
    entry_type: "AR_Invoice"
    debit_account: "Accounts_Receivable"
    credit_account: "Revenue"
    amount: ar.invoice_amount
  }
}
```

**转换函数2（应付到总账）**：

```text
f_AP_to_GL: Accounts_Payable → General_Ledger

f_AP_to_GL(ap) = {
  journal_entry: {
    entry_type: "AP_Invoice"
    debit_account: "Expense"
    credit_account: "Accounts_Payable"
    amount: ap.invoice_amount
  }
}
```

---

## 9. 形式化定理

### 9.1 应收应付平衡定理

**定理1（应收应付平衡）**：

对于任意期间，应收账款和应付账款的余额满足：

```text
∑(AR.closing_balance) - ∑(AP.closing_balance) = Net_Working_Capital
```

**证明**：

```text
AR.closing_balance = AR.opening_balance + AR.invoice_total - AR.receipt_total
AP.closing_balance = AP.opening_balance + AP.invoice_total - AP.payment_total

Net_Working_Capital = AR.closing_balance - AP.closing_balance
                    = (AR.opening_balance - AP.opening_balance)
                    + (AR.invoice_total - AP.invoice_total)
                    - (AR.receipt_total - AP.payment_total)
```

### 9.2 发票金额验证定理

**定理2（发票金额验证）**：

对于任意发票，发票金额满足：

```text
invoice.total_amount = invoice.invoice_amount + invoice.tax_amount
  ∧ invoice.outstanding_amount = invoice.total_amount - invoice.paid_amount
  ∧ 0 ≤ invoice.outstanding_amount ≤ invoice.total_amount
```

**证明**：

由约束1和类型系统定义，发票金额计算满足上述等式。

### 9.3 付款金额验证定理

**定理3（付款金额验证）**：

对于任意付款，付款金额满足：

```text
payment.payment_amount ≤ invoice.outstanding_amount
  ∧ invoice.paid_amount = sum(payment.payment_amount where payment.invoice_id == invoice.invoice_id)
  ∧ invoice.paid_amount ≤ invoice.total_amount
```

**证明**：

由约束3和类型系统定义，付款金额验证满足上述条件。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
