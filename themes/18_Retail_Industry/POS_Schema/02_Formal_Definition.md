# POS Schema形式化定义

## 📑 目录

- [POS Schema形式化定义](#pos-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 销售交易Schema](#2-销售交易schema)
  - [3. 支付处理Schema](#3-支付处理schema)
  - [4. 库存管理Schema](#4-库存管理schema)
  - [5. ISO 8583消息Schema](#5-iso-8583消息schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 交易完整性定理](#91-交易完整性定理)
    - [9.2 支付一致性定理](#92-支付一致性定理)

---

## 1. 形式化模型

**定义1（POS Schema）**：
POS Schema是一个四元组：

```text
POS_Schema = (Sales_Transaction_Schema, Payment_Processing_Schema,
             Inventory_Management_Schema, Customer_Management_Schema)
```

其中：

- `Sales_Transaction_Schema`：销售交易Schema
- `Payment_Processing_Schema`：支付处理Schema
- `Inventory_Management_Schema`：库存管理Schema
- `Customer_Management_Schema`：会员管理Schema

---

## 2. 销售交易Schema

**定义2（销售交易Schema）**：

```text
Sales_Transaction_Schema = (Transaction_Info, Product_Info,
                           Transaction_Status, Transaction_Amount)
```

**形式化DSL定义**：

```dsl
schema SalesTransaction {
  transaction_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  transaction_number: String @max_length(50) @required @unique

  transaction_info: {
    store_id: String @max_length(50) @required
    store_name: String @max_length(200)
    cashier_id: String @max_length(50) @required
    cashier_name: String @max_length(100)
    transaction_time: DateTime @required
    terminal_id: String @max_length(50) @required
    customer_id: String @max_length(50)
  } @required

  product_info: {
    items: List<TransactionItem> {
      item_id: String @required @unique
      product_barcode: String @max_length(50) @required
      product_name: String @max_length(200) @required
      quantity: Decimal @precision(10,3) @required
      unit_price: Decimal @precision(10,2) @required
      discount_rate: Decimal @precision(5,2) @default(0.0) @unit("%")
      discount_amount: Decimal @precision(10,2) @default(0.0)
      subtotal: Decimal @precision(10,2) @required
    } @required
  } @required

  transaction_status: {
    status: Enum { Pending, Completed, Cancelled, Refunded } @required
    payment_status: Enum { Unpaid, Partial, Paid, Refunded } @required
    refund_status: Enum { None, Partial, Full } @default("None")
  } @required

  transaction_amount: {
    subtotal: Decimal @precision(10,2) @required
    total_discount: Decimal @precision(10,2) @default(0.0)
    tax_amount: Decimal @precision(10,2) @default(0.0)
    tax_rate: Decimal @precision(5,2) @default(0.0) @unit("%")
    total_amount: Decimal @precision(10,2) @required
    paid_amount: Decimal @precision(10,2) @default(0.0)
    change_amount: Decimal @precision(10,2) @default(0.0)
  } @required
} @standard("GS1")
```

---

## 3. 支付处理Schema

**定义3（支付处理Schema）**：

```text
Payment_Processing_Schema = (Payment_Method, Payment_Info,
                            Payment_Security, Payment_Result)
```

**形式化DSL定义**：

```dsl
schema PaymentProcessing {
  payment_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  transaction_id: String @pattern("^[A-Z0-9]{20}$") @required

  payment_method: {
    method_type: Enum { Cash, Card, Mobile, Membership, Other } @required
    card_type: Enum { Debit, Credit, Prepaid }
    card_brand: Enum { Visa, MasterCard, UnionPay, Other }
    mobile_payment_type: Enum { Alipay, WeChatPay, ApplePay, Other }
  } @required

  payment_info: {
    payment_amount: Decimal @precision(10,2) @required
    payment_time: DateTime @required
    payment_reference: String @max_length(100)
    authorization_code: String @max_length(50)
    card_number_masked: String @max_length(20)
    expiry_date: String @pattern("^[0-9]{2}/[0-9]{2}$")
  } @required

  payment_security: {
    encryption_method: String @max_length(50)
    signature: String @max_length(500)
    risk_score: Decimal @precision(5,2) @range(0.0, 100.0)
    fraud_detection: Boolean @default(false)
  } @required

  payment_result: {
    result_code: String @max_length(10) @required
    result_message: String @max_length(200)
    status: Enum { Success, Failed, Pending, Cancelled } @required
    failure_reason: String @max_length(500)
  } @required
} @standard("ISO8583")
```

---

## 4. 库存管理Schema

**定义4（库存管理Schema）**：

```text
Inventory_Management_Schema = (Inventory_Query, Inventory_Update,
                              Inventory_Alert)
```

**形式化DSL定义**：

```dsl
schema InventoryManagement {
  inventory_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  product_barcode: String @max_length(50) @required

  inventory_query: {
    store_id: String @max_length(50) @required
    current_quantity: Integer @required
    available_quantity: Integer @required
    reserved_quantity: Integer @default(0)
    location: String @max_length(100)
    last_updated: DateTime @required
  } @required

  inventory_update: {
    update_type: Enum { Sale, Return, Adjustment, Transfer } @required
    quantity_change: Integer @required
    update_reason: String @max_length(200)
    update_time: DateTime @required
    operator: String @max_length(100) @required
  } @required

  inventory_alert: {
    low_stock_threshold: Integer @default(10)
    low_stock_alert: Boolean @default(false)
    expiry_date: Date @format("YYYY-MM-DD")
    expiry_alert: Boolean @default(false)
    slow_moving_days: Integer @default(90)
    slow_moving_alert: Boolean @default(false)
  }
} @standard("GS1")
```

---

## 5. ISO 8583消息Schema

**定义5（ISO 8583消息Schema）**：

```text
ISO8583_Message_Schema = (Message_Header, Message_Type, Message_Fields)
```

**形式化DSL定义**：

```dsl
schema ISO8583Message {
  message_header: {
    message_length: Integer @range(0, 9999) @required
    message_type: String @pattern("^[0-9]{4}$") @required
  } @required

  message_type: {
    mti: String @pattern("^[0-9]{4}$") @required
    transaction_type: Enum { Purchase, Refund, Reversal, BalanceInquiry } @required
    message_class: Enum { Authorization, Financial, Reversal, Network } @required
  } @required

  message_fields: {
    field_2: String @max_length(19)  # Primary Account Number
    field_3: String @pattern("^[0-9]{6}$")  # Processing Code
    field_4: String @pattern("^[0-9]{12}$")  # Amount
    field_7: String @pattern("^[0-9]{10}$")  # Transmission Date/Time
    field_11: String @pattern("^[0-9]{6}$")  # System Trace Audit Number
    field_12: String @pattern("^[0-9]{12}$")  # Local Transaction Time
    field_13: String @pattern("^[0-9]{4}$")  # Local Transaction Date
    field_37: String @max_length(12)  # Retrieval Reference Number
    field_38: String @max_length(6)  # Authorization Code
    field_39: String @pattern("^[0-9]{2}$")  # Response Code
    field_41: String @max_length(8)  # Terminal ID
    field_42: String @max_length(15)  # Merchant ID
  } @required
} @standard("ISO8583")
```

---

## 6. 类型系统

**定义6（POS类型系统）**：

```text
POS_Type_System = (Transaction_Types, Payment_Types, Inventory_Types, Customer_Types)
```

**交易类型**：

- **TransactionStatus**：交易状态枚举
- **PaymentStatus**：支付状态枚举
- **RefundStatus**：退款状态枚举

**支付类型**：

- **PaymentMethod**：支付方式枚举
- **CardType**：卡类型枚举
- **PaymentResult**：支付结果枚举

**库存类型**：

- **UpdateType**：更新类型枚举
- **AlertType**：预警类型枚举

**客户类型**：

- **MembershipLevel**：会员等级枚举
- **PointsType**：积分类型枚举

---

## 7. 约束规则

**规则1（交易金额约束）**：

```text
∀ st ∈ Sales_Transaction_Schema:
  st.transaction_amount.total_amount =
    st.transaction_amount.subtotal -
    st.transaction_amount.total_discount +
    st.transaction_amount.tax_amount
  st.transaction_amount.paid_amount ≥ st.transaction_amount.total_amount
  st.transaction_amount.change_amount =
    st.transaction_amount.paid_amount - st.transaction_amount.total_amount
```

**规则2（支付一致性约束）**：

```text
∀ pp ∈ Payment_Processing_Schema:
  pp.payment_result.status = "Success" ↔
    pp.payment_info.payment_amount > 0 ∧
    pp.payment_security.fraud_detection = false
```

**规则3（库存更新约束）**：

```text
∀ im ∈ Inventory_Management_Schema:
  im.inventory_update.update_type = "Sale" →
    im.inventory_query.available_quantity ≥ abs(im.inventory_update.quantity_change)
```

---

## 8. 转换函数

**函数1（GS1到POS转换）**：

```text
Convert_GS1_to_POS: GS1_Barcode_Schema → POS_Product_Schema
Convert_GS1_to_POS(gs1_barcode) = {
  product_barcode: gs1_barcode.gtin,
  product_name: gs1_barcode.product_name,
  unit_price: gs1_barcode.price
}
```

**函数2（ISO 8583到支付转换）**：

```text
Convert_ISO8583_to_Payment: ISO8583_Message_Schema → Payment_Processing_Schema
Convert_ISO8583_to_Payment(iso8583_msg) = {
  payment_amount: ParseAmount(iso8583_msg.message_fields.field_4),
  authorization_code: iso8583_msg.message_fields.field_38,
  result_code: iso8583_msg.message_fields.field_39
}
```

---

## 9. 形式化定理

### 9.1 交易完整性定理

**定理1（交易完整性）**：

对于任意销售交易ST，如果ST的所有必需信息都存在，
则ST是完整的：

```text
∀ st ∈ Sales_Transaction_Schema:
  Complete(st) ↔
    ∃ st.transaction_info ∧ ∃ st.product_info.items ∧
    ∃ st.transaction_status ∧ ∃ st.transaction_amount
```

**证明**：

根据GS1标准，销售交易的完整性定义为所有必需信息
都存在。因此，如果所有必需信息都存在，则销售交易
是完整的。

### 9.2 支付一致性定理

**定理2（支付一致性）**：

对于任意支付处理PP，如果PP的支付金额等于交易金额，
则PP是一致的：

```text
∀ pp ∈ Payment_Processing_Schema:
  ∀ st ∈ Sales_Transaction_Schema:
    Consistent(pp, st) ↔
      pp.transaction_id = st.transaction_id ∧
      pp.payment_info.payment_amount = st.transaction_amount.total_amount
```

**证明**：

根据ISO 8583标准，支付的一致性定义为支付金额等于
交易金额。因此，如果支付金额等于交易金额，则支付
是一致的。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
