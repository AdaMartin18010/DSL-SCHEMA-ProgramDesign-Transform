# SWIFT Schema实践案例

## 📑 目录

- [SWIFT Schema实践案例](#swift-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：MT103跨境支付](#2-案例1mt103跨境支付)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：MT202银行间转账](#3-案例2mt202银行间转账)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：SWIFT gpi支付追踪](#4-案例3swift-gpi支付追踪)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：MT到MX转换](#5-案例4mt到mx转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：SWIFT数据存储与分析系统](#6-案例5swift数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供SWIFT Schema在实际应用中的实践案例。

---

## 2. 案例1：MT103跨境支付

### 2.1 场景描述

**应用场景**：
客户通过银行发起跨境支付，使用MT103消息格式。

### 2.2 Schema定义

**MT103跨境支付Schema**：

```dsl
schema MT103CrossBorderPayment {
  field_20: String @value("REF123456789") @tag(":20:")

  field_23B: Enum { CRED } @value(CRED) @tag(":23B:")

  field_32A: DateAmountCurrency {
    date: Date @value("250121") @format("YYMMDD")
    currency: String @value("USD")
    amount: Decimal @value(10000.00) @precision(15,2)
  } @tag(":32A:")

  field_50A: PartyIdentifier {
    account: String @value("1234567890")
    name_and_address: String @value("ABC COMPANY\n123 MAIN ST\nNEW YORK NY 10001")
  } @tag(":50A:")

  field_59: Beneficiary {
    account: String @value("9876543210")
    name_and_address: String @value("XYZ CORPORATION\n456 BROADWAY\nLONDON EC1A 1BB")
  } @tag(":59:")

  field_71A: Enum { SHA } @value(SHA) @tag(":71A:")

  field_72: Optional<String> @tag(":72:")
} @standard("SWIFT_MT103")
```

---

## 3. 案例2：MT202银行间转账

### 3.1 场景描述

**应用场景**：
银行间进行资金转账，使用MT202消息格式。

### 3.2 Schema定义

**MT202银行间转账Schema**：

```dsl
schema MT202BankTransfer {
  field_20: String @value("BANK202001") @tag(":20:")

  field_21: String @value("RELATED103") @tag(":21:")

  field_32A: DateAmountCurrency {
    date: Date @value("250121") @format("YYMMDD")
    currency: String @value("EUR")
    amount: Decimal @value(50000.00) @precision(15,2)
  } @tag(":32A:")

  field_52A: BankIdentifier {
    bic: String @value("DEUTDEFF")
    account: Optional<String>
  } @tag(":52A:")

  field_56A: IntermediaryBank {
    bic: String @value("CHASUS33")
  } @tag(":56A:")

  field_57A: AccountWithBank {
    bic: String @value("BNPAFRPP")
    account: Optional<String>
  } @tag(":57A:")

  field_58A: BeneficiaryBank {
    bic: String @value("BNPAFRPP")
    account: Optional<String>
  } @tag(":58A:")
} @standard("SWIFT_MT202")
```

---

## 4. 案例3：SWIFT gpi支付追踪

### 4.1 场景描述

**应用场景**：
使用SWIFT gpi追踪支付状态，获取实时支付信息。

### 4.2 Schema定义

**SWIFT gpi支付追踪Schema**：

```dsl
schema SWIFTGpiTracking {
  uetr: String @value("01234567-89AB-CDEF-0123-456789ABCDEF") @required

  transaction_status: Enum {
    ACSP,  // AcceptedSettlementInProcess
    ACSC,  // AcceptedSettlementCompleted
    ACWC,  // AcceptedWithChange
    PART,  // PartiallyAccepted
    PDNG,  // Pending
    RJCT   // Rejected
  } @required

  initiation_time: DateTime @required
  last_update_time: DateTime @required

  payment_information: {
    amount: Decimal @precision(18,5) @required
    currency: String @length(3) @required
    debtor: PartyIdentification @required
    creditor: PartyIdentification @required
  }

  tracking_events: List<TrackingEvent> {
    timestamp: DateTime @required
    status: TransactionStatus @required
    location: Optional<String>
    additional_information: Optional<String>
  }
} @standard("SWIFT_gpi")
```

---

## 5. 案例4：MT到MX转换

### 5.1 场景描述

**应用场景**：
将传统MT103消息转换为ISO 20022 pacs.008 MX消息。

### 5.2 实现代码

详见 `04_Transformation.md` 第2章。

---

## 6. 案例5：SWIFT数据存储与分析系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储SWIFT消息数据，支持支付流程分析和优化。

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
