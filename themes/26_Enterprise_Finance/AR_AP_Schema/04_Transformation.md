# 应收应付Schema转换体系

## 📑 目录

- [应收应付Schema转换体系](#应收应付schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 应收应付到总账转换](#2-应收应付到总账转换)
  - [3. 应收应付到OpenAPI转换](#3-应收应付到openapi转换)
  - [4. 应收应付到JSON Schema转换](#4-应收应付到json-schema转换)
  - [5. 应收应付数据存储与分析](#5-应收应付数据存储与分析)
    - [5.1 PostgreSQL应收应付数据存储](#51-postgresql应收应付数据存储)
    - [5.2 应收应付数据分析查询](#52-应收应付数据分析查询)

---

## 1. 转换体系概述

应收应付Schema转换体系支持应收应付数据到总账、OpenAPI、JSON Schema格式转换，以及应收应付数据存储。

### 1.1 转换目标

1. **应收应付到总账转换**：应收应付数据到总账格式
2. **应收应付到OpenAPI转换**：应收应付数据到OpenAPI格式
3. **应收应付到JSON Schema转换**：应收应付数据到JSON Schema格式
4. **应收应付到数据库转换**：应收应付数据到PostgreSQL存储

---

## 2. 应收应付到总账转换

**转换规则**：

- 销售发票 → 总账凭证（借：应收账款，贷：收入）
- 收款 → 总账凭证（借：银行存款，贷：应收账款）
- 采购发票 → 总账凭证（借：费用/资产，贷：应付账款）
- 付款 → 总账凭证（借：应付账款，贷：银行存款）

**转换示例**：

```python
def convert_ar_to_gl(ar_data: AccountsReceivableSchema) -> GeneralLedgerEntry:
    """将应收账款数据转换为总账凭证"""
    gl_entry = GeneralLedgerEntry()

    # 转换销售发票
    for invoice in ar_data.sales_invoices:
        if invoice.status == "Issued":
            gl_line_debit = GLLine()
            gl_line_debit.account_code = "1120"  # 应收账款
            gl_line_debit.debit_amount = invoice.total_amount
            gl_entry.lines.append(gl_line_debit)

            gl_line_credit = GLLine()
            gl_line_credit.account_code = "6001"  # 主营业务收入
            gl_line_credit.credit_amount = invoice.invoice_amount
            gl_entry.lines.append(gl_line_credit)

            if invoice.tax_amount > 0:
                gl_line_tax = GLLine()
                gl_line_tax.account_code = "2221"  # 应交税费
                gl_line_tax.credit_amount = invoice.tax_amount
                gl_entry.lines.append(gl_line_tax)

    # 转换收款
    for receipt in ar_data.receipts:
        if receipt.status == "Confirmed":
            gl_line_debit = GLLine()
            gl_line_debit.account_code = "1002"  # 银行存款
            gl_line_debit.debit_amount = receipt.receipt_amount
            gl_entry.lines.append(gl_line_debit)

            gl_line_credit = GLLine()
            gl_line_credit.account_code = "1120"  # 应收账款
            gl_line_credit.credit_amount = receipt.receipt_amount
            gl_entry.lines.append(gl_line_credit)

    return gl_entry

def convert_ap_to_gl(ap_data: AccountsPayableSchema) -> GeneralLedgerEntry:
    """将应付账款数据转换为总账凭证"""
    gl_entry = GeneralLedgerEntry()

    # 转换采购发票
    for invoice in ap_data.purchase_invoices:
        if invoice.status == "Approved":
            gl_line_debit = GLLine()
            gl_line_debit.account_code = "5001"  # 主营业务成本
            gl_line_debit.debit_amount = invoice.invoice_amount
            gl_entry.lines.append(gl_line_debit)

            if invoice.tax_amount > 0:
                gl_line_tax_debit = GLLine()
                gl_line_tax_debit.account_code = "2221"  # 应交税费-进项税额
                gl_line_tax_debit.debit_amount = invoice.tax_amount
                gl_entry.lines.append(gl_line_tax_debit)

            gl_line_credit = GLLine()
            gl_line_credit.account_code = "2202"  # 应付账款
            gl_line_credit.credit_amount = invoice.total_amount
            gl_entry.lines.append(gl_line_credit)

    # 转换付款
    for payment in ap_data.payments:
        if payment.status == "Confirmed":
            gl_line_debit = GLLine()
            gl_line_debit.account_code = "2202"  # 应付账款
            gl_line_debit.debit_amount = payment.payment_amount
            gl_entry.lines.append(gl_line_debit)

            gl_line_credit = GLLine()
            gl_line_credit.account_code = "1002"  # 银行存款
            gl_line_credit.credit_amount = payment.payment_amount
            gl_entry.lines.append(gl_line_credit)

    return gl_entry
```

---

## 3. 应收应付到OpenAPI转换

**转换规则**：

- 客户/供应商 → OpenAPI Customer/Supplier Schema
- 发票 → OpenAPI Invoice Schema
- 收款/付款 → OpenAPI Receipt/Payment Schema

**转换示例**：

```python
def convert_ar_to_openapi(ar_data: AccountsReceivableSchema) -> OpenAPISchema:
    """将应收账款数据转换为OpenAPI格式"""
    openapi_schema = OpenAPISchema()

    # 定义客户Schema
    customer_schema = {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "format": "uuid"},
            "customer_code": {"type": "string"},
            "customer_name": {"type": "string"},
            "credit_limit": {"type": "number", "format": "decimal"},
            "payment_terms": {"type": "string"},
            "credit_rating": {"type": "string", "enum": ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]}
        },
        "required": ["customer_id", "customer_code", "customer_name"]
    }

    # 定义发票Schema
    invoice_schema = {
        "type": "object",
        "properties": {
            "invoice_id": {"type": "string", "format": "uuid"},
            "invoice_number": {"type": "string"},
            "invoice_date": {"type": "string", "format": "date"},
            "customer_id": {"type": "string", "format": "uuid"},
            "due_date": {"type": "string", "format": "date"},
            "invoice_amount": {"type": "number", "format": "decimal"},
            "tax_amount": {"type": "number", "format": "decimal"},
            "total_amount": {"type": "number", "format": "decimal"},
            "status": {"type": "string", "enum": ["Draft", "Issued", "Paid", "Overdue", "Cancelled"]}
        },
        "required": ["invoice_id", "invoice_number", "invoice_date", "customer_id", "due_date", "invoice_amount"]
    }

    openapi_schema.components.schemas["Customer"] = customer_schema
    openapi_schema.components.schemas["SalesInvoice"] = invoice_schema

    return openapi_schema
```

---

## 4. 应收应付到JSON Schema转换

**转换规则**：

- 客户/供应商 → JSON Schema Customer/Supplier
- 发票 → JSON Schema Invoice
- 收款/付款 → JSON Schema Receipt/Payment

**转换示例**：

```python
def convert_ar_to_json_schema(ar_data: AccountsReceivableSchema) -> JSONSchema:
    """将应收账款数据转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "customers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "customer_code": {"type": "string"},
                        "customer_name": {"type": "string"},
                        "credit_limit": {"type": "number"},
                        "payment_terms": {"type": "string"},
                        "credit_rating": {"type": "string"}
                    },
                    "required": ["customer_id", "customer_code", "customer_name"]
                }
            },
            "sales_invoices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "invoice_id": {"type": "string"},
                        "invoice_number": {"type": "string"},
                        "invoice_date": {"type": "string", "format": "date"},
                        "customer_id": {"type": "string"},
                        "due_date": {"type": "string", "format": "date"},
                        "invoice_amount": {"type": "number"},
                        "tax_amount": {"type": "number"},
                        "total_amount": {"type": "number"},
                        "status": {"type": "string"}
                    },
                    "required": ["invoice_id", "invoice_number", "invoice_date", "customer_id", "due_date", "invoice_amount"]
                }
            }
        }
    }

    return json_schema
```

---

## 5. 应收应付数据存储与分析

### 5.1 PostgreSQL应收应付数据存储

**表结构设计**：

```sql
-- 客户表
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    credit_limit DECIMAL(18, 2) DEFAULT 0,
    payment_terms VARCHAR(50) DEFAULT 'NET30',
    credit_rating VARCHAR(10) DEFAULT 'A',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 销售发票表
CREATE TABLE sales_invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    due_date DATE NOT NULL,
    invoice_amount DECIMAL(18, 2) NOT NULL,
    tax_amount DECIMAL(18, 2) DEFAULT 0,
    total_amount DECIMAL(18, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Draft',
    payment_status VARCHAR(20) DEFAULT 'Unpaid',
    paid_amount DECIMAL(18, 2) DEFAULT 0,
    outstanding_amount DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 收款表
CREATE TABLE receipts (
    receipt_id VARCHAR(50) PRIMARY KEY,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    receipt_date DATE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    invoice_id VARCHAR(50) NOT NULL,
    receipt_amount DECIMAL(18, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    bank_account VARCHAR(100),
    reference_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (invoice_id) REFERENCES sales_invoices(invoice_id)
);

-- 供应商表
CREATE TABLE suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(200) NOT NULL,
    payment_terms VARCHAR(50) DEFAULT 'NET30',
    credit_limit DECIMAL(18, 2) DEFAULT 0,
    bank_account VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 采购发票表
CREATE TABLE purchase_invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    due_date DATE NOT NULL,
    invoice_amount DECIMAL(18, 2) NOT NULL,
    tax_amount DECIMAL(18, 2) DEFAULT 0,
    total_amount DECIMAL(18, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Draft',
    payment_status VARCHAR(20) DEFAULT 'Unpaid',
    paid_amount DECIMAL(18, 2) DEFAULT 0,
    outstanding_amount DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 付款表
CREATE TABLE payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    invoice_id VARCHAR(50) NOT NULL,
    payment_amount DECIMAL(18, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    bank_account VARCHAR(100) NOT NULL,
    reference_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Pending',
    approval_status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (invoice_id) REFERENCES purchase_invoices(invoice_id)
);

-- 创建索引
CREATE INDEX idx_sales_invoices_customer ON sales_invoices(customer_id);
CREATE INDEX idx_sales_invoices_status ON sales_invoices(status);
CREATE INDEX idx_sales_invoices_due_date ON sales_invoices(due_date);
CREATE INDEX idx_receipts_customer ON receipts(customer_id);
CREATE INDEX idx_receipts_invoice ON receipts(invoice_id);
CREATE INDEX idx_purchase_invoices_supplier ON purchase_invoices(supplier_id);
CREATE INDEX idx_purchase_invoices_status ON purchase_invoices(status);
CREATE INDEX idx_payments_supplier ON payments(supplier_id);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
```

### 5.2 应收应付数据分析查询

**查询示例**：

```python
def analyze_ar_data(conn, period_start, period_end):
    """分析应收账款数据"""
    cursor = conn.cursor()

    # 查询应收账款账龄分析
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

    aging_analysis = cursor.fetchall()

    # 查询应收账款汇总
    cursor.execute("""
        SELECT
            SUM(si.outstanding_amount) as total_outstanding,
            COUNT(*) as invoice_count,
            AVG(si.outstanding_amount) as avg_outstanding
        FROM sales_invoices si
        WHERE si.payment_status IN ('Unpaid', 'Partially_Paid')
        AND si.invoice_date BETWEEN %s AND %s
    """, (period_start, period_end))

    ar_summary = cursor.fetchone()

    return {
        "aging_analysis": aging_analysis,
        "ar_summary": ar_summary
    }

def analyze_ap_data(conn, period_start, period_end):
    """分析应付账款数据"""
    cursor = conn.cursor()

    # 查询应付账款账龄分析
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

    aging_analysis = cursor.fetchall()

    # 查询应付账款汇总
    cursor.execute("""
        SELECT
            SUM(pi.outstanding_amount) as total_outstanding,
            COUNT(*) as invoice_count,
            AVG(pi.outstanding_amount) as avg_outstanding
        FROM purchase_invoices pi
        WHERE pi.payment_status IN ('Unpaid', 'Partially_Paid')
        AND pi.invoice_date BETWEEN %s AND %s
    """, (period_start, period_end))

    ap_summary = cursor.fetchone()

    return {
        "aging_analysis": aging_analysis,
        "ap_summary": ap_summary
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
