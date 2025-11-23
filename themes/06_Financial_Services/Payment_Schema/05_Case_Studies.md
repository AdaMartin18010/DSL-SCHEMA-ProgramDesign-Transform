# Payment Schema实践案例

## 📑 目录

- [Payment Schema实践案例](#payment-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：在线支付处理](#2-案例1在线支付处理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：支付清算结算](#3-案例2支付清算结算)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：数字货币支付](#4-案例3数字货币支付)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：Payment到ISO 20022转换](#5-案例4payment到iso-20022转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：Payment数据存储与分析系统](#6-案例5payment数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供Payment Schema在实际应用中的实践案例。

---

## 2. 案例1：在线支付处理

### 2.1 场景描述

**应用场景**：
电商平台在线支付处理，包括支付请求、支付响应、支付状态查询等。

### 2.2 Schema定义

**在线支付处理Payment Schema**：

```dsl
schema OnlinePaymentProcessing {
  payment_request: PaymentRequest {
    request_id: String @value("REQ-2025-001")
    merchant_id: String @value("MERCHANT-001")
    order_id: String @value("ORDER-2025-001")
    amount: Decimal @value(1000.00)
    currency: String @value("USD")
    payment_method: Enum @value("CreditCard")

    card_info: CardInfo {
      card_number: String @value("4111111111111111")
      card_holder_name: String @value("John Doe")
      expiry_date: String @value("12/25")
      cvv: String @value("123")
    }

    customer_info: CustomerInfo {
      customer_id: String @value("CUST-001")
      customer_name: String @value("John Doe")
      email: String @value("john.doe@example.com")
      phone: String @value("+1234567890")
    }

    callback_url: String @value("https://merchant.com/callback")
    timestamp: DateTime @value("2025-01-21T10:00:00Z")
    signature: String @value("signature_hash")
  }

  payment_response: PaymentResponse {
    response_id: String @value("RESP-2025-001")
    request_id: String @value("REQ-2025-001")
    status: Enum @value("Success")
    transaction_id: String @value("TXN-2025-001")
    amount: Decimal @value(1000.00)
    currency: String @value("USD")
    payment_time: DateTime @value("2025-01-21T10:00:05Z")
    timestamp: DateTime @value("2025-01-21T10:00:05Z")
    signature: String @value("response_signature_hash")
  }
} @standard("PCI_DSS")
```

---

## 3. 案例2：支付清算结算

### 3.1 场景描述

**应用场景**：
支付平台每日清算结算处理，包括清算记录生成、结算记录生成、对账文件生成等。

### 3.2 Schema定义

**支付清算结算Payment Schema**：

```dsl
schema PaymentClearingSettlement {
  clearing_record: ClearingRecord {
    clearing_id: String @value("CLEAR-2025-001")
    clearing_date: Date @value("2025-01-21")
    merchant_id: String @value("MERCHANT-001")
    transaction_count: Int @value(1000)
    total_amount: Decimal @value(1000000.00)
    currency: String @value("USD")
    clearing_status: Enum @value("Processed")
    settlement_id: String @value("SETTLE-2025-001")
    created_at: DateTime @value("2025-01-21T09:00:00Z")
    processed_at: DateTime @value("2025-01-21T09:30:00Z")
  }

  settlement_record: SettlementRecord {
    settlement_id: String @value("SETTLE-2025-001")
    settlement_date: Date @value("2025-01-22")
    merchant_id: String @value("MERCHANT-001")
    clearing_id: String @value("CLEAR-2025-001")
    settlement_amount: Decimal @value(1000000.00)
    currency: String @value("USD")
    fee_amount: Decimal @value(3000.00)
    net_amount: Decimal @value(997000.00)
    settlement_status: Enum @value("Completed")
    bank_account: String @value("BANK-ACC-001")
    created_at: DateTime @value("2025-01-22T09:00:00Z")
    completed_at: DateTime @value("2025-01-22T10:00:00Z")
  }
} @standard("ISO_8583")
```

---

## 4. 案例3：数字货币支付

### 4.1 场景描述

**应用场景**：
数字货币支付处理，包括数字货币交易、钱包管理、交易确认等。

### 4.2 Schema定义

**数字货币支付Payment Schema**：

```dsl
schema DigitalCurrencyPayment {
  digital_currency_transaction: DigitalCurrencyTransaction {
    transaction_id: String @value("TXN-DC-2025-001")
    transaction_hash: String @value("0x1234567890abcdef...")
    from_address: String @value("0xABCDEF1234567890...")
    to_address: String @value("0x9876543210FEDCBA...")
    amount: Decimal @value(1.5)
    currency: String @value("ETH")
    transaction_fee: Decimal @value(0.001)
    status: Enum @value("Confirmed")
    block_number: Int @value(12345678)
    block_hash: String @value("0xBLOCKHASH...")
    confirmation_count: Int @value(12)
    created_at: DateTime @value("2025-01-21T10:00:00Z")
    confirmed_at: DateTime @value("2025-01-21T10:05:00Z")
  }

  wallet_address: WalletAddress {
    address: String @value("0xABCDEF1234567890...")
    wallet_type: Enum @value("Ethereum")
    balance: Decimal @value(10.5)
    currency: String @value("ETH")
    public_key: String @value("PUBLIC_KEY...")
    private_key_hash: String @value("HASHED_PRIVATE_KEY...")
    created_at: DateTime @value("2025-01-01T00:00:00Z")
    last_transaction_at: DateTime @value("2025-01-21T10:05:00Z")
  }
} @standard("Blockchain")
```

---

## 5. 案例4：Payment到ISO 20022转换

### 5.1 场景描述

**应用场景**：
将Payment支付请求转换为ISO 20022 pacs.008消息，用于银行系统集成。

### 5.2 实现代码

详见 `04_Transformation.md` 第2章。

---

## 6. 案例5：Payment数据存储与分析系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储Payment交易数据，支持支付数据分析和报表生成。

### 6.2 实现代码

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
