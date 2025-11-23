# ISO 20022 Schema实践案例

## 📑 目录

- [ISO 20022 Schema实践案例](#iso-20022-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：pacs.008客户贷记转账](#2-案例1pacs008客户贷记转账)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：camt.053银行对账单](#3-案例2camt053银行对账单)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：seev.031公司行动通知](#4-案例3seev031公司行动通知)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：ISO 20022到SWIFT MT转换](#5-案例4iso-20022到swift-mt转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：ISO 20022数据存储与分析系统](#6-案例5iso-20022数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供ISO 20022 Schema在实际应用中的实践案例。

---

## 2. 案例1：pacs.008客户贷记转账

### 2.1 场景描述

**应用场景**：
银行使用pacs.008消息处理客户贷记转账业务。

### 2.2 Schema定义

**pacs.008客户贷记转账ISO 20022 Schema**：

```dsl
schema Pacs008CustomerCreditTransfer {
  group_header: GroupHeader {
    message_identification: String @value("MSG-2025-001")
    creation_date_time: DateTime @value("2025-01-21T10:00:00Z")
    initiating_party: PartyIdentification43 {
      name: String @value("ABC Bank")
    }
  }

  payment_information: PaymentInstructionInformation {
    payment_information_identification: String @value("PAY-2025-001")
    payment_method: Enum @value("TRF")
    requested_execution_date: Date @value("2025-01-22")

    debtor: PartyIdentification43 {
      name: String @value("Customer A")
    }

    debtor_account: CashAccount16 {
      identification: AccountIdentification4Choice {
        iban: String @value("GB82WEST12345698765432")
      }
    }

    credit_transfer_transaction_information: List[CreditTransferTransactionInformation] {
      transaction1: CreditTransferTransactionInformation {
        payment_identification: PaymentIdentification3 {
          instruction_identification: String @value("INST-001")
          end_to_end_identification: String @value("E2E-001")
        }

        amount: AmountType3Choice {
          instructed_amount: ActiveCurrencyAndAmount {
            currency: String @value("USD")
            value: Decimal @value(10000.00)
          }
        }

        creditor: PartyIdentification43 {
          name: String @value("Customer B")
        }

        creditor_account: CashAccount16 {
          identification: AccountIdentification4Choice {
            iban: String @value("GB29NWBK60161331926819")
          }
        }
      }
    }
  }
} @standard("ISO_20022")
```

---

## 3. 案例2：camt.053银行对账单

### 3.1 场景描述

**应用场景**：
银行使用camt.053消息向客户发送银行对账单。

### 3.2 Schema定义

**camt.053银行对账单ISO 20022 Schema**：

```dsl
schema Camt053BankStatement {
  bank_to_customer_statement: BankToCustomerStatement {
    group_header: GroupHeader {
      message_identification: String @value("STMT-2025-001")
      creation_date_time: DateTime @value("2025-01-21T09:00:00Z")
    }

    statement: List[AccountStatement] {
      statement1: AccountStatement {
        id: String @value("STMT-ACC-001")
        account: CashAccount20 {
          identification: AccountIdentification4Choice {
            iban: String @value("GB82WEST12345698765432")
          }
          currency: String @value("USD")
        }

        balance: List[CashBalance] {
          opening_balance: CashBalance {
            type: BalanceType12Choice {
              code: Enum @value("OPNG")
            }
            amount: AmountAndCurrencyExchangeDetails3 {
              amount: ActiveOrHistoricCurrencyAndAmount {
                currency: String @value("USD")
                value: Decimal @value(50000.00)
              }
            }
            credit_debit_indicator: Enum @value("CRDT")
            date: DateAndDateTimeChoice {
              date: Date @value("2025-01-01")
            }
          }

          closing_balance: CashBalance {
            type: BalanceType12Choice {
              code: Enum @value("CLSG")
            }
            amount: AmountAndCurrencyExchangeDetails3 {
              amount: ActiveOrHistoricCurrencyAndAmount {
                currency: String @value("USD")
                value: Decimal @value(60000.00)
              }
            }
            credit_debit_indicator: Enum @value("CRDT")
            date: DateAndDateTimeChoice {
              date: Date @value("2025-01-31")
            }
          }
        }

        entry: List[ReportEntry] {
          entry1: ReportEntry {
            entry_reference: String @value("ENTRY-001")
            amount: AmountAndCurrencyExchangeDetails3 {
              amount: ActiveOrHistoricCurrencyAndAmount {
                currency: String @value("USD")
                value: Decimal @value(10000.00)
              }
            }
            credit_debit_indicator: Enum @value("CRDT")
            status: EntryStatus2Code @value("BOOK")
            booking_date: DateAndDateTimeChoice {
              date: Date @value("2025-01-15")
            }
          }
        }
      }
    }
  }
} @standard("ISO_20022")
```

---

## 4. 案例3：seev.031公司行动通知

### 4.1 场景描述

**应用场景**：
证券托管机构使用seev.031消息通知客户公司行动事件。

### 4.2 Schema定义

**seev.031公司行动通知ISO 20022 Schema**：

```dsl
schema Seev031CorporateActionNotification {
  corporate_action_notification: CorporateActionNotification {
    notification_general_information: CorporateActionNotification2 {
      notification_type: CorporateActionNotificationType1Code @value("NEWM")
      notification_date: Date @value("2025-01-21")
    }

    corporate_action_general_information: CorporateActionGeneralInformation {
      corporate_action_event_identification: String @value("CA-2025-001")
      corporate_action_event_type: CorporateActionEventType3Choice {
        code: Enum @value("DVCA")
      }
      underlying_security: SecurityIdentification14 {
        identification: String @value("US0378331005")
        description: String @value("Apple Inc. Common Stock")
      }
    }

    account_and_balance_details: List[AccountAndBalanceDetails] {
      account1: AccountAndBalanceDetails {
        safekeeping_account: String @value("ACC-001")
        balance: CorporateActionBalanceDetails {
          total_eligible_balance: Quantity3Choice {
            quantity: Decimal @value(1000.00)
          }
        }
      }
    }

    corporate_action_details: CorporateActionDetails {
      date_details: CorporateActionDate8 {
        record_date: DateAndDateTimeChoice {
          date: Date @value("2025-02-01")
        }
        ex_date: DateAndDateTimeChoice {
          date: Date @value("2025-01-30")
        }
        payment_date: DateAndDateTimeChoice {
          date: Date @value("2025-02-15")
        }
      }
      rate_details: CorporateActionRate7 {
        interest_rate: Optional[RateFormat3Choice]
        dividend_rate: Optional[RateFormat3Choice]
      }
    }
  }
} @standard("ISO_20022")
```

---

## 5. 案例4：ISO 20022到SWIFT MT转换

### 5.1 场景描述

**应用场景**：
将ISO 20022 pacs.008消息转换为SWIFT MT103消息，用于兼容传统SWIFT系统。

### 5.2 实现代码

详见 `04_Transformation.md` 第2章。

---

## 6. 案例5：ISO 20022数据存储与分析系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储ISO 20022消息数据，支持消息分析和合规性检查。

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
