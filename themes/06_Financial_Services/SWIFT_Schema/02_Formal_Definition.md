# SWIFT Schema形式化定义

## 📑 目录

- [SWIFT Schema形式化定义](#swift-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. MT消息Schema](#2-mt消息schema)
  - [3. MX消息Schema](#3-mx消息schema)
  - [4. BIC代码Schema](#4-bic代码schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

**定义1（SWIFT Schema）**：
SWIFT Schema是一个三元组：

```text
SWIFT_Schema = (MT_Message, MX_Message, BIC_Code)
```

其中：

- `MT_Message`：SWIFT MT消息Schema
- `MX_Message`：SWIFT MX（ISO 20022）消息Schema
- `BIC_Code`：银行识别代码Schema

---

## 2. MT消息Schema

**定义2（MT消息Schema）**：

```text
MT_Message_Schema = (Header, Body, Trailer)
```

**形式化DSL定义**：

```dsl
schema MTMessage {
  header: {
    application_id: Enum { A, F, L, S } @required
    service_id: String @length(2) @required
    logical_terminal_address: String @length(12) @required
    session_number: String @length(4) @required
    sequence_number: String @length(6) @required
  }

  body: {
    message_type: String @pattern("^MT[0-9]{3}$") @required
    fields: Map<String, Field> {
      tag: String @pattern("^:[0-9]{2}[A-Z]?:$") @required
      content: String @required
      format: Enum { Fixed, Variable, Optional }
    }
  }

  trailer: {
    checksum: String @length(4) @required
    authentication_code: Optional<String>
  }
} @standard("SWIFT_MT")
```

**MT103消息示例**：

```dsl
schema MT103 {
  message_type: String @value("MT103")

  field_20: String @tag(":20:") @required
  field_23B: Enum { CRED, CRTS } @tag(":23B:") @required
  field_32A: DateAmountCurrency {
    date: Date @format("YYMMDD")
    currency: String @length(3)
    amount: Decimal @precision(15,2)
  } @tag(":32A:") @required

  field_50A: PartyIdentifier {
    account: Optional<String>
    name_and_address: String
  } @tag(":50A:") @required

  field_59: Beneficiary {
    account: Optional<String>
    name_and_address: String
  } @tag(":59:") @required

  field_71A: Enum { SHA, OUR, BEN } @tag(":71A:") @default(SHA)
} @standard("SWIFT_MT103")
```

---

## 3. MX消息Schema

**定义3（MX消息Schema）**：

```text
MX_Message_Schema = (Document, GroupHeader, PaymentInformation)
```

**形式化DSL定义**：

```dsl
schema MXMessage {
  document: {
    xmlns: String @value("urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08")
    xmlns_xsi: String @value("http://www.w3.org/2001/XMLSchema-instance")
  }

  group_header: {
    message_identification: String @required @unique
    creation_date_time: DateTime @required
    initiating_party: PartyIdentification {
      name: String @required
      identification: Optional<PartyIdentification>
    }
  }

  payment_information: {
    payment_information_identification: String @required
    payment_method: Enum { TRF, TRA } @required
    requested_execution_date: Date @required
    debtor: PartyIdentification @required
    debtor_account: CashAccount @required
    credit_transfer_transaction_information: List<CreditTransferTransaction> {
      payment_identification: PaymentIdentification @required
      amount: Amount {
        currency: String @length(3) @required
        value: Decimal @precision(18,5) @required
      }
      creditor: PartyIdentification @required
      creditor_account: CashAccount @required
      remittance_information: Optional<String>
    } @required
  }
} @standard("ISO_20022")
```

---

## 4. BIC代码Schema

**定义4（BIC代码Schema）**：

```text
BIC_Code_Schema = (Bank_Code, Country_Code, Location_Code, Branch_Code)
```

**形式化DSL定义**：

```dsl
schema BICCode {
  bank_code: String @length(4) @pattern("^[A-Z]{4}$") @required
  country_code: String @length(2) @pattern("^[A-Z]{2}$") @required
  location_code: String @length(2) @pattern("^[A-Z0-9]{2}$") @required
  branch_code: Optional<String> @length(3) @pattern("^[A-Z0-9]{3}$")
} @standard("ISO_13616")
```

**BIC验证规则**：

```text
BIC_Valid(bic) =
  length(bic) ∈ {8, 11}
  ∧ bank_code ∈ [A-Z]{4}
  ∧ country_code ∈ [A-Z]{2}
  ∧ location_code ∈ [A-Z0-9]{2}
  ∧ (branch_code = ∅ ∨ branch_code ∈ [A-Z0-9]{3})
```

---

## 5. 类型系统

**定义5（SWIFT数据类型）**：

```text
SWIFT_Data_Type = MT_Message | MX_Message | BIC_Code | Amount | Date | Party
```

**基本类型定义**：

```dsl
type Amount {
  currency: String @length(3) @pattern("^[A-Z]{3}$")
  value: Decimal @precision(18,5) @min(0)
}

type Date {
  format: Enum { YYMMDD, YYYYMMDD }
  value: String @pattern("^[0-9]{6}|[0-9]{8}$")
}

type PartyIdentification {
  name: String @max_length(140)
  identification: Optional<String>
  address: Optional<PostalAddress>
}
```

---

## 6. 约束规则

**约束1（MT消息完整性）**：

```text
∀ mt ∈ MT_Message:
  checksum(mt.body) = mt.trailer.checksum
  ∧ validate_fields(mt.body.fields)
```

**约束2（MX消息有效性）**：

```text
∀ mx ∈ MX_Message:
  validate_xml_schema(mx, ISO_20022_XSD)
  ∧ unique(mx.payment_information.credit_transfer_transaction_information)
```

**约束3（BIC代码有效性）**：

```text
∀ bic ∈ BIC_Code:
  BIC_Valid(bic)
  ∧ registered_in_swift_directory(bic)
```

---

## 7. 转换函数

**函数1（MT到MX转换）**：

```text
convert_MT103_to_MX: MT103 → pacs.008.001.08
```

**函数2（MX到MT转换）**：

```text
convert_MX_to_MT103: pacs.008.001.08 → MT103
```

**函数3（BIC验证）**：

```text
validate_bic: BIC_Code → Bool
```

---

## 8. 形式化定理

### 8.1 转换正确性定理

**定理1（MT到MX转换正确性）**：

```text
∀ mt103 ∈ MT103:
  mx = convert_MT103_to_MX(mt103)
  → financial_equivalent(mt103, mx)
  ∧ amount_preserved(mt103.field_32A, mx.amount)
  ∧ party_preserved(mt103.field_50A, mx.debtor)
  ∧ party_preserved(mt103.field_59, mx.creditor)
```

### 8.2 消息完整性定理

**定理2（MT消息完整性）**：

```text
∀ mt ∈ MT_Message:
  validate_checksum(mt)
  → message_integrity(mt)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
