# 应收应付Schema实践案例

## 📑 目录

- [应收应付Schema实践案例](#应收应付schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：应收账款管理](#2-案例1应收账款管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：应付账款管理](#3-案例2应付账款管理)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：自动对账系统](#4-案例3自动对账系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：应收应付到总账转换](#5-案例4应收应付到总账转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：应收应付数据存储与分析系统](#6-案例5应收应付数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供应收应付Schema在实际应用中的实践案例。

---

## 2. 案例1：应收账款管理

### 2.1 场景描述

**应用场景**：
企业应收账款管理，包括客户管理、发票管理、收款管理、对账管理。

**业务需求**：

- 支持客户信用管理
- 支持销售发票生成和管理
- 支持收款处理和跟踪
- 支持应收账款对账

### 2.2 Schema定义

**应收账款管理Schema**：

```dsl
schema AccountsReceivableManagement {
  customer: Customer {
    customer_id: String @value("CUST-20250001")
    customer_code: String @value("C001")
    customer_name: String @value("ABC公司")
    credit_limit: Decimal @value(100000.00)
    payment_terms: String @value("NET30")
    credit_rating: Enum @value("A")
  }

  sales_invoice: SalesInvoice {
    invoice_id: String @value("INV-20250001")
    invoice_number: String @value("SI-2025-001")
    invoice_date: Date @value("2025-01-15")
    customer_id: String @value("CUST-20250001")
    due_date: Date @value("2025-02-14")
    invoice_amount: Decimal @value(50000.00)
    tax_amount: Decimal @value(6500.00)
    total_amount: Decimal @value(56500.00)
    status: Enum @value("Issued")
    payment_status: Enum @value("Unpaid")
  }

  receipt: Receipt {
    receipt_id: String @value("REC-20250001")
    receipt_number: String @value("R-2025-001")
    receipt_date: Date @value("2025-02-10")
    customer_id: String @value("CUST-20250001")
    invoice_id: String @value("INV-20250001")
    receipt_amount: Decimal @value(56500.00)
    payment_method: Enum @value("Bank_Transfer")
    status: Enum @value("Confirmed")
  }
}
```

---

## 3. 案例2：应付账款管理

### 3.1 场景描述

**应用场景**：
企业应付账款管理，包括供应商管理、发票管理、付款管理、对账管理。

**业务需求**：

- 支持供应商管理
- 支持采购发票接收和验证
- 支持付款审批和执行
- 支持应付账款对账

### 3.2 Schema定义

**应付账款管理Schema**：

```dsl
schema AccountsPayableManagement {
  supplier: Supplier {
    supplier_id: String @value("SUPP-20250001")
    supplier_code: String @value("S001")
    supplier_name: String @value("XYZ供应商")
    payment_terms: String @value("NET30")
    credit_limit: Decimal @value(200000.00)
  }

  purchase_invoice: PurchaseInvoice {
    invoice_id: String @value("INV-20250002")
    invoice_number: String @value("PI-2025-001")
    invoice_date: Date @value("2025-01-20")
    supplier_id: String @value("SUPP-20250001")
    due_date: Date @value("2025-02-19")
    invoice_amount: Decimal @value(30000.00)
    tax_amount: Decimal @value(3900.00)
    total_amount: Decimal @value(33900.00)
    status: Enum @value("Approved")
    payment_status: Enum @value("Unpaid")
  }

  payment: Payment {
    payment_id: String @value("PAY-20250001")
    payment_number: String @value("P-2025-001")
    payment_date: Date @value("2025-02-15")
    supplier_id: String @value("SUPP-20250001")
    invoice_id: String @value("INV-20250002")
    payment_amount: Decimal @value(33900.00)
    payment_method: Enum @value("Bank_Transfer")
    status: Enum @value("Confirmed")
    approval_status: Enum @value("Approved")
  }
}
```

---

## 4. 案例3：自动对账系统

### 4.1 场景描述

**应用场景**：
自动对账系统，自动匹配发票和收款/付款，识别差异。

**业务需求**：

- 自动匹配发票和收款/付款
- 识别对账差异
- 生成对账报告

### 4.2 实现代码

```python
def auto_reconcile_ar(ar_data: AccountsReceivableSchema):
    """自动对账应收账款"""
    reconciliations = []

    for customer in ar_data.customers:
        invoices = [inv for inv in ar_data.sales_invoices
                   if inv.customer_id == customer.customer_id]
        receipts = [rec for rec in ar_data.receipts
                   if rec.customer_id == customer.customer_id]

        # 计算期初余额
        opening_balance = sum([inv.total_amount for inv in invoices
                              if inv.invoice_date < period_start])

        # 计算发票总额
        invoice_total = sum([inv.total_amount for inv in invoices
                            if period_start <= inv.invoice_date <= period_end])

        # 计算收款总额
        receipt_total = sum([rec.receipt_amount for rec in receipts
                            if period_start <= rec.receipt_date <= period_end])

        # 计算期末余额
        closing_balance = opening_balance + invoice_total - receipt_total

        # 创建对账记录
        reconciliation = Reconciliation()
        reconciliation.customer_id = customer.customer_id
        reconciliation.period_start = period_start
        reconciliation.period_end = period_end
        reconciliation.opening_balance = opening_balance
        reconciliation.invoice_total = invoice_total
        reconciliation.receipt_total = receipt_total
        reconciliation.closing_balance = closing_balance
        reconciliation.is_balanced = abs(closing_balance) < 0.01

        reconciliations.append(reconciliation)

    return reconciliations
```

---

## 5. 案例4：应收应付到总账转换

### 5.1 场景描述

**应用场景**：
将应收应付数据转换为总账凭证，实现财务数据集成。

**业务需求**：

- 自动生成总账凭证
- 支持批量转换
- 支持转换验证

### 5.2 实现代码

```python
def convert_ar_ap_to_gl(ar_data: AccountsReceivableSchema,
                        ap_data: AccountsPayableSchema) -> List[GeneralLedgerEntry]:
    """将应收应付数据转换为总账凭证"""
    gl_entries = []

    # 转换应收账款
    for invoice in ar_data.sales_invoices:
        if invoice.status == "Issued":
            gl_entry = GeneralLedgerEntry()
            gl_entry.entry_date = invoice.invoice_date
            gl_entry.entry_type = "AR_Invoice"
            gl_entry.description = f"销售发票 {invoice.invoice_number}"

            # 借：应收账款
            gl_line_debit = GLLine()
            gl_line_debit.account_code = "1120"
            gl_line_debit.debit_amount = invoice.total_amount
            gl_entry.lines.append(gl_line_debit)

            # 贷：主营业务收入
            gl_line_credit = GLLine()
            gl_line_credit.account_code = "6001"
            gl_line_credit.credit_amount = invoice.invoice_amount
            gl_entry.lines.append(gl_line_credit)

            # 贷：应交税费
            if invoice.tax_amount > 0:
                gl_line_tax = GLLine()
                gl_line_tax.account_code = "2221"
                gl_line_tax.credit_amount = invoice.tax_amount
                gl_entry.lines.append(gl_line_tax)

            gl_entries.append(gl_entry)

    # 转换应付账款
    for invoice in ap_data.purchase_invoices:
        if invoice.status == "Approved":
            gl_entry = GeneralLedgerEntry()
            gl_entry.entry_date = invoice.invoice_date
            gl_entry.entry_type = "AP_Invoice"
            gl_entry.description = f"采购发票 {invoice.invoice_number}"

            # 借：主营业务成本
            gl_line_debit = GLLine()
            gl_line_debit.account_code = "5001"
            gl_line_debit.debit_amount = invoice.invoice_amount
            gl_entry.lines.append(gl_line_debit)

            # 借：应交税费-进项税额
            if invoice.tax_amount > 0:
                gl_line_tax_debit = GLLine()
                gl_line_tax_debit.account_code = "2221"
                gl_line_tax_debit.debit_amount = invoice.tax_amount
                gl_entry.lines.append(gl_line_tax_debit)

            # 贷：应付账款
            gl_line_credit = GLLine()
            gl_line_credit.account_code = "2202"
            gl_line_credit.credit_amount = invoice.total_amount
            gl_entry.lines.append(gl_line_credit)

            gl_entries.append(gl_entry)

    return gl_entries
```

---

## 6. 案例5：应收应付数据存储与分析系统

### 6.1 场景描述

**应用场景**：
应收应付数据存储与分析系统，支持数据存储、查询、分析。

**业务需求**：

- 支持应收应付数据存储
- 支持数据查询和分析
- 支持报表生成

### 6.2 实现代码

```python
def store_ar_ap_data(ar_data: AccountsReceivableSchema,
                     ap_data: AccountsPayableSchema, conn):
    """存储应收应付数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储客户数据
    for customer in ar_data.customers:
        cursor.execute("""
            INSERT INTO customers
            (customer_id, customer_code, customer_name, credit_limit, payment_terms, credit_rating, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            credit_limit = EXCLUDED.credit_limit,
            payment_terms = EXCLUDED.payment_terms,
            credit_rating = EXCLUDED.credit_rating,
            is_active = EXCLUDED.is_active,
            updated_at = CURRENT_TIMESTAMP
        """, (customer.customer_id, customer.customer_code, customer.customer_name,
              customer.credit_limit, customer.payment_terms, customer.credit_rating, customer.is_active))

    # 存储销售发票数据
    for invoice in ar_data.sales_invoices:
        cursor.execute("""
            INSERT INTO sales_invoices
            (invoice_id, invoice_number, invoice_date, customer_id, due_date,
             invoice_amount, tax_amount, total_amount, status, payment_status, paid_amount, outstanding_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (invoice_id) DO UPDATE SET
            invoice_amount = EXCLUDED.invoice_amount,
            tax_amount = EXCLUDED.tax_amount,
            total_amount = EXCLUDED.total_amount,
            status = EXCLUDED.status,
            payment_status = EXCLUDED.payment_status,
            paid_amount = EXCLUDED.paid_amount,
            outstanding_amount = EXCLUDED.outstanding_amount,
            updated_at = CURRENT_TIMESTAMP
        """, (invoice.invoice_id, invoice.invoice_number, invoice.invoice_date,
              invoice.customer_id, invoice.due_date, invoice.invoice_amount,
              invoice.tax_amount, invoice.total_amount, invoice.status,
              invoice.payment_status, invoice.paid_amount, invoice.outstanding_amount))

    # 存储供应商数据
    for supplier in ap_data.suppliers:
        cursor.execute("""
            INSERT INTO suppliers
            (supplier_id, supplier_code, supplier_name, payment_terms, credit_limit, bank_account, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (supplier_id) DO UPDATE SET
            supplier_name = EXCLUDED.supplier_name,
            payment_terms = EXCLUDED.payment_terms,
            credit_limit = EXCLUDED.credit_limit,
            bank_account = EXCLUDED.bank_account,
            is_active = EXCLUDED.is_active,
            updated_at = CURRENT_TIMESTAMP
        """, (supplier.supplier_id, supplier.supplier_code, supplier.supplier_name,
              supplier.payment_terms, supplier.credit_limit, supplier.bank_account, supplier.is_active))

    # 存储采购发票数据
    for invoice in ap_data.purchase_invoices:
        cursor.execute("""
            INSERT INTO purchase_invoices
            (invoice_id, invoice_number, invoice_date, supplier_id, due_date,
             invoice_amount, tax_amount, total_amount, status, payment_status, paid_amount, outstanding_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (invoice_id) DO UPDATE SET
            invoice_amount = EXCLUDED.invoice_amount,
            tax_amount = EXCLUDED.tax_amount,
            total_amount = EXCLUDED.total_amount,
            status = EXCLUDED.status,
            payment_status = EXCLUDED.payment_status,
            paid_amount = EXCLUDED.paid_amount,
            outstanding_amount = EXCLUDED.outstanding_amount,
            updated_at = CURRENT_TIMESTAMP
        """, (invoice.invoice_id, invoice.invoice_number, invoice.invoice_date,
              invoice.supplier_id, invoice.due_date, invoice.invoice_amount,
              invoice.tax_amount, invoice.total_amount, invoice.status,
              invoice.payment_status, invoice.paid_amount, invoice.outstanding_amount))

    conn.commit()

def generate_ar_ap_report(conn, period_start, period_end):
    """生成应收应付报表"""
    cursor = conn.cursor()

    # 应收账款账龄分析
    cursor.execute("""
        SELECT
            c.customer_name,
            si.invoice_number,
            si.invoice_date,
            si.due_date,
            si.outstanding_amount,
            CASE
                WHEN CURRENT_DATE <= si.due_date THEN 'Current'
                WHEN CURRENT_DATE <= si.due_date + INTERVAL '30 days' THEN '1-30 Days'
                WHEN CURRENT_DATE <= si.due_date + INTERVAL '60 days' THEN '31-60 Days'
                WHEN CURRENT_DATE <= si.due_date + INTERVAL '90 days' THEN '61-90 Days'
                ELSE 'Over 90 Days'
            END as aging_bucket
        FROM sales_invoices si
        JOIN customers c ON si.customer_id = c.customer_id
        WHERE si.payment_status IN ('Unpaid', 'Partially_Paid')
        AND si.invoice_date BETWEEN %s AND %s
        ORDER BY si.due_date
    """, (period_start, period_end))

    ar_aging = cursor.fetchall()

    # 应付账款账龄分析
    cursor.execute("""
        SELECT
            s.supplier_name,
            pi.invoice_number,
            pi.invoice_date,
            pi.due_date,
            pi.outstanding_amount,
            CASE
                WHEN CURRENT_DATE <= pi.due_date THEN 'Current'
                WHEN CURRENT_DATE <= pi.due_date + INTERVAL '30 days' THEN '1-30 Days'
                WHEN CURRENT_DATE <= pi.due_date + INTERVAL '60 days' THEN '31-60 Days'
                WHEN CURRENT_DATE <= pi.due_date + INTERVAL '90 days' THEN '61-90 Days'
                ELSE 'Over 90 Days'
            END as aging_bucket
        FROM purchase_invoices pi
        JOIN suppliers s ON pi.supplier_id = s.supplier_id
        WHERE pi.payment_status IN ('Unpaid', 'Partially_Paid')
        AND pi.invoice_date BETWEEN %s AND %s
        ORDER BY pi.due_date
    """, (period_start, period_end))

    ap_aging = cursor.fetchall()

    return {
        "ar_aging": ar_aging,
        "ap_aging": ap_aging
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
