# ISO 20022 Schema形式化定义

## 📑 目录

- [ISO 20022 Schema形式化定义](#iso-20022-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 支付消息Schema](#2-支付消息schema)
  - [3. 现金管理消息Schema](#3-现金管理消息schema)
  - [4. 证券消息Schema](#4-证券消息schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

**定义1（ISO 20022 Schema）**：
ISO 20022 Schema是一个三元组：

```text
ISO20022_Schema = (Payment_Message, Cash_Management_Message, Securities_Message)
```

其中：

- `Payment_Message`：支付消息Schema
- `Cash_Management_Message`：现金管理消息Schema
- `Securities_Message`：证券消息Schema

---

## 2. 支付消息Schema

**定义2（支付消息Schema）**：

```text
Payment_Message_Schema = (pacs008 | pacs009 | pain001 | pain002)
```

**形式化DSL定义**：

```dsl
schema ISO20022PaymentMessage {
  // pacs.008 - 客户贷记转账
  pacs008: Optional<Pacs008] {
    group_header: GroupHeader {
      message_identification: String @required
      creation_date_time: DateTime @required
      initiating_party: PartyIdentification43 {
        name: String @required
        identification: Optional<PartyIdentification43Choice]
      }
    }

    payment_information: PaymentInstructionInformation {
      payment_information_identification: String @required
      payment_method: Enum { TRF, TRA, CHK, DD } @required
      requested_execution_date: Date
      debtor: PartyIdentification43 {
        name: String @required
        postal_address: Optional<PostalAddress6]
        identification: Optional<PartyIdentification43Choice]
      }
      debtor_account: CashAccount16 {
        identification: AccountIdentification4Choice @required
        name: Optional<String]
        currency: Optional<String]
      }
      credit_transfer_transaction_information: List<CreditTransferTransactionInformation] {
        payment_identification: PaymentIdentification3 {
          instruction_identification: String @required
          end_to_end_identification: String @required
        }
        amount: AmountType3Choice {
          instructed_amount: ActiveCurrencyAndAmount {
            currency: String @required @length(3)
            value: Decimal @required
          }
        }
        creditor: PartyIdentification43 {
          name: String @required
          postal_address: Optional<PostalAddress6]
          identification: Optional<PartyIdentification43Choice]
        }
        creditor_account: CashAccount16 {
          identification: AccountIdentification4Choice @required
        }
        remittance_information: Optional<RemittanceInformation7]
      }
    }
  }

  // pacs.009 - 金融贷记转账
  pacs009: Optional<Pacs009] {
    group_header: GroupHeader
    financial_institution_credit_transfer: FinancialInstitutionCreditTransfer {
      credit_transfer_transaction_information: List<CreditTransferTransactionInformation]
    }
  }

  // pain.001 - 客户贷记转账发起
  pain001: Optional<Pain001] {
    customer_credit_transfer_initiation: CustomerCreditTransferInitiation {
      group_header: GroupHeader
      payment_information: PaymentInstructionInformation
    }
  }

  // pain.002 - 支付状态报告
  pain002: Optional<Pain002] {
    customer_payment_status_report: CustomerPaymentStatusReport {
      group_header: GroupHeader
      original_group_information_and_status: OriginalGroupInformationAndStatus {
        original_message_identification: String @required
        original_message_name_identification: String @required
        group_status: Enum { ACCP, RJCT } @required
      }
      original_payment_information_and_status: List<OriginalPaymentInformationAndStatus]
    }
  }
} @standard("ISO_20022")
```

---

## 3. 现金管理消息Schema

**定义3（现金管理消息Schema）**：

```text
Cash_Management_Message_Schema = (camt053 | camt054 | camt052 | camt056)
```

**形式化DSL定义**：

```dsl
schema ISO20022CashManagementMessage {
  // camt.053 - 银行对账单
  camt053: Optional<Camt053] {
    bank_to_customer_statement: BankToCustomerStatement {
      group_header: GroupHeader {
        message_identification: String @required
        creation_date_time: DateTime @required
      }
      statement: List<AccountStatement] {
        id: String @required
        electronic_sequence_number: Optional<String]
        legal_sequence_number: Optional<String]
        account: CashAccount20 {
          identification: AccountIdentification4Choice @required
          name: Optional<String]
          currency: Optional<String]
        }
        balance: List<CashBalance] {
          type: BalanceType12Choice {
            code: Enum { XPCD, OPNG, CLSG, ITBD } @required
          }
          amount: AmountAndCurrencyExchangeDetails3 {
            amount: ActiveOrHistoricCurrencyAndAmount {
              currency: String @required @length(3)
              value: Decimal @required
            }
          }
          credit_debit_indicator: Enum { CRDT, DBIT } @required
          date: DateAndDateTimeChoice {
            date: Date @required
          }
        }
        entry: List<ReportEntry] {
          entry_reference: String @required
          amount: AmountAndCurrencyExchangeDetails3
          credit_debit_indicator: Enum { CRDT, DBIT } @required
          status: EntryStatus2Code @required
          booking_date: Optional<DateAndDateTimeChoice]
          value_date: Optional<DateAndDateTimeChoice]
          bank_transaction_code: Optional<BankTransactionCodeStructure4]
          additional_information: Optional<String]
        }
      }
    }
  }

  // camt.054 - 银行通知
  camt054: Optional<Camt054] {
    bank_to_customer_debit_credit_notification: BankToCustomerDebitCreditNotification {
      group_header: GroupHeader
      notification: List<AccountNotification] {
        id: String @required
        account: CashAccount20
        entry: List<ReportEntry]
      }
    }
  }

  // camt.052 - 银行对账单请求
  camt052: Optional<Camt052] {
    bank_to_customer_account_report_request: BankToCustomerAccountReportRequest {
      group_header: GroupHeader
      account_report_request: AccountReportRequest {
        account: CashAccount20 @required
        date_range: Optional<DatePeriodDetails]
      }
    }
  }

  // camt.056 - 取消通知
  camt056: Optional<Camt056] {
    cancel_payment: CancelPayment {
      assignment: CaseAssignment {
        id: String @required
        assigner: PartyIdentification43 @required
        assignee: PartyIdentification43 @required
      }
      case: Case {
        id: String @required
        creator: PartyIdentification43 @required
      }
      original_payment_information_and_cancellation: OriginalPaymentInstructionAndCancellation {
        cancellation_reason_information: CancellationReasonInformation2 {
          originator: Optional<PartyIdentification43]
          reason: CancellationReason2Choice {
            code: Enum { DUPL, AGNT, CURR, CUST, UPAY } @required
          }
        }
        original_payment_information: PaymentInstructionInformation @required
      }
    }
  }
} @standard("ISO_20022")
```

---

## 4. 证券消息Schema

**定义4（证券消息Schema）**：

```text
Securities_Message_Schema = (seev031 | seev033 | seev034)
```

**形式化DSL定义**：

```dsl
schema ISO20022SecuritiesMessage {
  // seev.031 - 公司行动通知
  seev031: Optional<Seev031] {
    corporate_action_notification: CorporateActionNotification {
      notification_general_information: CorporateActionNotification2 {
        notification_type: CorporateActionNotificationType1Code @required
        notification_date: Date @required
      }
      corporate_action_general_information: CorporateActionGeneralInformation {
        corporate_action_event_identification: String @required
        corporate_action_event_type: CorporateActionEventType3Choice {
          code: Enum { DVCA, DVOP, DVSC, LIQU, SOFF } @required
        }
        underlying_security: SecurityIdentification14 {
          identification: String @required
          description: Optional<String]
        }
      }
      account_and_balance_details: List<AccountAndBalanceDetails] {
        safekeeping_account: String @required
        balance: CorporateActionBalanceDetails {
          total_eligible_balance: Quantity3Choice {
            quantity: Decimal @required
            quantity_code: Optional<String]
          }
        }
      }
      corporate_action_details: CorporateActionDetails {
        date_details: CorporateActionDate8 {
          record_date: Optional<DateAndDateTimeChoice]
          ex_date: Optional<DateAndDateTimeChoice]
          payment_date: Optional<DateAndDateTimeChoice]
        }
        rate_details: Optional<CorporateActionRate7]
      }
    }
  }

  // seev.033 - 公司行动选项
  seev033: Optional<Seev033] {
    corporate_action_notification_advice: CorporateActionNotificationAdvice {
      notification_general_information: CorporateActionNotification2
      corporate_action_general_information: CorporateActionGeneralInformation
      account_and_balance_details: List<AccountAndBalanceDetails]
      corporate_action_option_details: List<CorporateActionOptionDetails] {
        option_number: String @required
        option_type: CorporateActionOption2Choice {
          code: Enum { BSPL, BUYA, CASE, CASH, EXER } @required
        }
        option_features: Optional<List<OptionFeaturesFormat1Choice]]
        fraction_disposition: Optional<FractionDispositionType1Choice]
        currency_option: Optional<String]
        date_details: CorporateActionDate8
        rate_details: Optional<CorporateActionRate7]
        price_details: Optional<CorporateActionPrice2]
        securities_quantity: Optional<SecuritiesOption1]
        cash_movement_details: Optional<List<CashOption1]]
      }
    }
  }

  // seev.034 - 公司行动确认
  seev034: Optional<Seev034] {
    corporate_action_movement_confirmation: CorporateActionMovementConfirmation {
      notification_identification: DocumentIdentification15 {
        identification: String @required
        date_of_document: Date @required
      }
      corporate_action_general_information: CorporateActionGeneralInformation
      account_and_balance_details: List<AccountAndBalanceDetails]
      corporate_action_confirmation_details: List<CorporateActionConfirmationDetails] {
        transaction_identification: String @required
        corporate_action_option_details: CorporateActionOptionDetails
        confirmed_balance: CorporateActionBalanceDetails
        securities_movement_details: Optional<List<SecuritiesOption1]]
        cash_movement_details: Optional<List<CashOption1]]
      }
    }
  }
} @standard("ISO_20022")
```

---

## 5. 类型系统

**定义5（ISO 20022数据类型）**：

```text
ISO20022_Data_Type = Payment_Message | Cash_Management_Message | Securities_Message | Common_Components
```

**基本类型定义**：

```dsl
type GroupHeader {
  message_identification: String @required
  creation_date_time: DateTime @required
  message_pagination: Optional<Pagination]
  initiating_party: Optional<PartyIdentification43]
  forwarding_agent: Optional<BranchAndFinancialInstitutionIdentification4]
}

type PartyIdentification43 {
  name: String @required
  postal_address: Optional<PostalAddress6]
  identification: Optional<PartyIdentification43Choice]
  country_of_residence: Optional<String]
}

type CashAccount16 {
  identification: AccountIdentification4Choice @required
  name: Optional<String]
  currency: Optional<String]
  type: Optional<CashAccountType2Choice]
}

type AmountAndCurrencyExchangeDetails3 {
  amount: ActiveOrHistoricCurrencyAndAmount {
    currency: String @required @length(3)
    value: Decimal @required
  }
  currency_exchange: Optional<CurrencyExchange5]
}
```

---

## 6. 约束规则

**约束1（消息完整性）**：

```text
∀ message ∈ ISO20022_Message:
  has_group_header(message)
  ∧ has_message_identification(message)
  ∧ has_creation_date_time(message)
```

**约束2（支付金额约束）**：

```text
∀ payment ∈ Payment_Message:
  payment.amount.value > 0
  ∧ payment.amount.currency.length = 3
```

**约束3（账户约束）**：

```text
∀ account ∈ CashAccount:
  account.identification.required
  ∧ (account.currency → account.currency.length = 3)
```

---

## 7. 转换函数

**函数1（ISO 20022到SWIFT MT转换）**：

```text
convert_iso20022_to_mt: ISO20022_Message → SWIFT_MT_Message
```

**函数2（ISO 20022到XML转换）**：

```text
convert_iso20022_to_xml: ISO20022_Message → XML_Document
```

**函数3（消息验证）**：

```text
validate_iso20022_message: ISO20022_Message → ValidationResult
```

---

## 8. 形式化定理

### 8.1 消息一致性定理

**定理1（消息一致性）**：

```text
∀ message ∈ ISO20022_Message:
  validate_message_structure(message)
  → message_consistent(message)
```

### 8.2 转换正确性定理

**定理2（ISO 20022到SWIFT MT转换正确性）**：

```text
∀ iso20022_message ∈ ISO20022_Message:
  mt_message = convert_iso20022_to_mt(iso20022_message)
  → semantic_equivalent(iso20022_message, mt_message)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
