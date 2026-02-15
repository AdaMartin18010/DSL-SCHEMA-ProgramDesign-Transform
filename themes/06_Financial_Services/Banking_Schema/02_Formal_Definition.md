# 银行业务Schema形式化定义

## 📑 目录

- [银行业务Schema形式化定义](#银行业务schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 账户管理Schema](#2-账户管理schema)
  - [3. 支付清算Schema](#3-支付清算schema)
  - [4. 信贷业务Schema](#4-信贷业务schema)
  - [5. 银行卡Schema](#5-银行卡schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 账户一致性定理](#91-账户一致性定理)
    - [9.2 支付原子性定理](#92-支付原子性定理)
    - [9.3 信贷风险定理](#93-信贷风险定理)
  - [10. 数学模型](#10-数学模型)
    - [10.1 账户状态机](#101-账户状态机)
    - [10.2 支付状态机](#102-支付状态机)
    - [10.3 贷款状态机](#103-贷款状态机)

---

## 1. 形式化模型

**定义1（银行业务Schema）**：
银行业务Schema是一个五元组：

```text
Banking_Schema = (Account_Management, Payment_Clearing, Credit_Business, Card_Business, Core_Banking)
```

其中：

- `Account_Management`：账户管理Schema
- `Payment_Clearing`：支付清算Schema
- `Credit_Business`：信贷业务Schema
- `Card_Business`：银行卡业务Schema
- `Core_Banking`：核心银行系统Schema

**形式化定义**：

$$
\mathcal{B} = \langle A, P, C, K, G, \Sigma, \Phi \rangle
$$

其中：
- $\mathcal{B}$：银行业务Schema
- $A$：账户实体集合
- $P$：支付指令集合
- $C$：信贷合同集合
- $K$：银行卡集合
- $G$：核心总账集合
- $\Sigma$：状态转移函数
- $\Phi$：约束规则集合

---

## 2. 账户管理Schema

**定义2（账户管理Schema）**：

```text
Account_Management_Schema = (Customer_Account | Corporate_Account | Internal_Account)
```

**形式化DSL定义**：

```dsl
schema BankingAccountManagement {
  // 客户信息
  customer: Customer {
    customer_id: String(20) @required @unique
    customer_type: Enum { INDIVIDUAL, CORPORATE } @required
    customer_name: String(140) @required
    identification_type: Enum { ID_CARD, PASSPORT, BUSINESS_LICENSE } @required
    identification_number: String(50) @required @unique
    contact_info: ContactInformation {
      phone: String(20)
      email: String(254)
      address: PostalAddress
    }
    risk_level: Enum { LOW, MEDIUM, HIGH } @default("MEDIUM")
    kyc_status: Enum { PENDING, VERIFIED, REJECTED } @required
    created_at: DateTime @required
  }

  // 个人账户
  individual_account: IndividualAccount {
    account_number: String(32) @required @unique
    customer_id: String(20) @required @reference(Customer.customer_id)
    account_type: Enum { 
      SAVINGS,           // 储蓄账户
      CHECKING,          // 支票账户
      FIXED_DEPOSIT,     // 定期存款
      CALL_DEPOSIT       // 通知存款
    } @required
    currency: String(3) @required @pattern("[A-Z]{3}")
    balance: Decimal(18,2) @required @min(0)
    available_balance: Decimal(18,2) @required @min(0)
    frozen_amount: Decimal(18,2) @required @min(0) @default(0)
    status: Enum { ACTIVE, DORMANT, FROZEN, CLOSED } @required
    open_date: Date @required
    interest_rate: Decimal(5,4)
    maturity_date: Date?
    branch_code: String(10) @required
  }

  // 对公账户
  corporate_account: CorporateAccount {
    account_number: String(32) @required @unique
    customer_id: String(20) @required @reference(Customer.customer_id)
    account_category: Enum {
      BASIC,             // 基本存款账户
      GENERAL,           // 一般存款账户
      SPECIAL,           // 专用存款账户
      TEMPORARY          // 临时存款账户
    } @required
    company_name: String(140) @required
    unified_social_credit_code: String(18) @required
    legal_representative: String(50) @required
    registered_capital: Decimal(18,2)
    business_scope: String(500)
    currency: String(3) @required
    balance: Decimal(18,2) @required @min(0)
    status: Enum { ACTIVE, DORMANT, FROZEN, CLOSED } @required
    open_date: Date @required
    annual_review_date: Date @required
  }

  // 内部账户
  internal_account: InternalAccount {
    account_number: String(32) @required @unique
    account_name: String(140) @required
    account_category: Enum {
      ASSET,             // 资产类
      LIABILITY,         // 负债类
      EQUITY,            // 权益类
      INCOME,            // 收入类
      EXPENSE            // 费用类
    } @required
    subject_code: String(20) @required
    parent_subject: String(20)?
    currency: String(3) @required
    balance: Decimal(18,2) @required
    balance_direction: Enum { DEBIT, CREDIT } @required
    status: Enum { ACTIVE, INACTIVE } @required
  }
} @domain("BANKING") @version("1.0")
```

**账户数学模型**：

$$
\forall a \in A: \text{available\_balance}(a) = \text{balance}(a) - \text{frozen\_amount}(a)
$$

$$
\forall a \in A: \text{balance}(a) \geq 0 \land \text{frozen\_amount}(a) \geq 0 \land \text{available\_balance}(a) \geq 0
$$

---

## 3. 支付清算Schema

**定义3（支付清算Schema）**：

```text
Payment_Clearing_Schema = (Payment_Instruction × Clearing_Record × Settlement_Detail)
```

**形式化DSL定义**：

```dsl
schema BankingPaymentClearing {
  // 支付指令
  payment_instruction: PaymentInstruction {
    instruction_id: String(35) @required @unique
    instruction_type: Enum {
      CREDIT_TRANSFER,   // 贷记转账
      DIRECT_DEBIT,      // 直接借记
      INSTANT_PAYMENT    // 实时支付
    } @required
    message_type: Enum { pacs008, pacs009, pain001 } @required
    priority: Enum { HIGH, NORMAL, LOW } @default("NORMAL")
    
    // 付款方信息
    debtor: Party {
      name: String(140) @required
      account: AccountIdentification @required
      agent: FinancialInstitution
      identification: String(35)?
    }
    
    // 收款方信息
    creditor: Party {
      name: String(140) @required
      account: AccountIdentification @required
      agent: FinancialInstitution
      identification: String(35)?
    }
    
    // 金额信息
    amount: MonetaryAmount {
      value: Decimal(18,5) @required @min(0)
      currency: String(3) @required @pattern("[A-Z]{3}")
    }
    
    // 时间信息
    requested_execution_date: Date @required
    value_date: Date?
    
    // 附言信息
    remittance_info: RemittanceInformation {
      unstructured: String(140)?
      structured: StructuredRemittanceInformation?
    }
    
    status: Enum {
      PENDING,           // 待处理
      PROCESSING,        // 处理中
      ACCEPTED,          // 已接受
      REJECTED,          // 已拒绝
      SETTLED            // 已清算
    } @required
    
    created_at: DateTime @required
    updated_at: DateTime @required
  }

  // 清算记录
  clearing_record: ClearingRecord {
    record_id: String(35) @required @unique
    payment_instruction_id: String(35) @required @reference(PaymentInstruction.instruction_id)
    clearing_system: Enum {
      HVPS,              // 大额支付系统
      BEPS,              // 小额支付系统
      IBPS,              // 网上支付跨行清算
      CFXPS,             // 境内外币支付
      CIPS               // 跨境人民币支付
    } @required
    clearing_type: Enum { RTGS, DNS } @required
    
    // 清算金额
    clearing_amount: Decimal(18,5) @required
    clearing_currency: String(3) @required
    
    // 清算状态
    status: Enum {
      PENDING,
      IN_PROGRESS,
      COMPLETED,
      FAILED,
      RECONCILED
    } @required
    
    // 时间戳
    submission_time: DateTime @required
    clearing_time: DateTime?
    settlement_time: DateTime?
    
    // 报文信息
    message_reference: String(35) @required
    return_code: String(4)?
    return_reason: String(105)?
  }

  // 结算明细
  settlement_detail: SettlementDetail {
    settlement_id: String(35) @required @unique
    clearing_record_id: String(35) @required @reference(ClearingRecord.record_id)
    settlement_type: Enum {
      REAL_TIME,         // 实时结算
      BATCH,             // 批量结算
      NETTING            // 净额结算
    } @required
    
    // 借贷方信息
    debit_account: String(32) @required
    credit_account: String(32) @required
    settlement_amount: Decimal(18,5) @required
    settlement_currency: String(3) @required
    
    // 状态
    status: Enum { PENDING, POSTED, REVERSAL } @required
    posting_date: Date @required
    posting_time: DateTime @required
    
    // 会计分录
    accounting_entries: List<AccountingEntry> {
      entry_id: String(35) @required
      subject_code: String(20) @required
      debit_amount: Decimal(18,2)?
      credit_amount: Decimal(18,2)?
      description: String(140)
    }
  }
} @domain("BANKING") @version("1.0")
```

**支付原子性约束**：

$$
\forall p \in P: \text{atomic}(p) \Rightarrow \left( \text{debit}(p) \land \text{credit}(p) \right) \lor \neg\left( \text{debit}(p) \lor \text{credit}(p) \right)
$$

---

## 4. 信贷业务Schema

**定义4（信贷业务Schema）**：

```text
Credit_Business_Schema = (Loan_Application × Loan_Contract × Repayment_Schedule × Collateral)
```

**形式化DSL定义**：

```dsl
schema BankingCreditBusiness {
  // 贷款申请
  loan_application: LoanApplication {
    application_id: String(20) @required @unique
    customer_id: String(20) @required @reference(Customer.customer_id)
    product_code: String(10) @required
    
    // 申请金额
    applied_amount: Decimal(18,2) @required @min(0)
    applied_currency: String(3) @required
    applied_term_months: Integer @required @min(1) @max(360)
    
    // 利率信息
    interest_rate_type: Enum { FIXED, FLOATING } @required
    proposed_rate: Decimal(5,4) @required
    benchmark_rate: String(10)?
    spread: Decimal(5,4)?
    
    // 还款方式
    repayment_method: Enum {
      EQUAL_INSTALLMENT,     // 等额本息
      EQUAL_PRINCIPAL,       // 等额本金
      INTEREST_ONLY,         // 按期付息
      BULLET                 // 到期一次还本付息
    } @required
    
    // 用途
    loan_purpose: Enum {
      PURCHASE,              // 购房
      CONSUMPTION,           // 消费
      BUSINESS,              // 经营
      REFINANCE,             // 再融资
      OTHER
    } @required
    purpose_description: String(500)?
    
    // 申请状态
    status: Enum {
      DRAFT,
      SUBMITTED,
      UNDER_REVIEW,
      CREDIT_CHECK,
      APPROVED,
      REJECTED,
      CANCELLED
    } @required
    
    submission_date: Date?
    decision_date: Date?
    approved_amount: Decimal(18,2)?
    approved_term_months: Integer?
    approved_rate: Decimal(5,4)?
    rejection_reason: String(500)?
  }

  // 贷款合同
  loan_contract: LoanContract {
    contract_id: String(20) @required @unique
    application_id: String(20) @required @reference(LoanApplication.application_id)
    customer_id: String(20) @required
    
    // 合同金额
    contract_amount: Decimal(18,2) @required @min(0)
    currency: String(3) @required
    
    // 期限
    start_date: Date @required
    maturity_date: Date @required
    term_months: Integer @required
    
    // 利率
    interest_rate: Decimal(5,4) @required
    interest_rate_type: Enum { FIXED, FLOATING } @required
    
    // 还款计划
    repayment_method: Enum {
      EQUAL_INSTALLMENT,
      EQUAL_PRINCIPAL,
      INTEREST_ONLY,
      BULLET
    } @required
    repayment_frequency: Enum {
      MONTHLY,
      QUARTERLY,
      SEMI_ANNUALLY,
      ANNUALLY
    } @required
    repayment_day: Integer @min(1) @max(31)
    
    // 状态
    status: Enum {
      PENDING_DISBURSEMENT,
      ACTIVE,
      OVERDUE,
      DEFAULTED,
      CLOSED,
      WRITE_OFF
    } @required
    
    // 余额
    outstanding_principal: Decimal(18,2) @required
    outstanding_interest: Decimal(18,2) @required
    
    signing_date: Date @required
  }

  // 还款计划
  repayment_schedule: RepaymentSchedule {
    schedule_id: String(35) @required @unique
    contract_id: String(20) @required @reference(LoanContract.contract_id)
    installment_number: Integer @required @min(1)
    
    // 计划日期
    due_date: Date @required
    
    // 计划金额
    principal_amount: Decimal(18,2) @required
    interest_amount: Decimal(18,2) @required
    total_amount: Decimal(18,2) @required
    
    // 剩余本金
    remaining_principal: Decimal(18,2) @required
    
    // 实际还款
    actual_payment_date: Date?
    actual_principal_paid: Decimal(18,2) @default(0)
    actual_interest_paid: Decimal(18,2) @default(0)
    
    // 逾期
    is_overdue: Boolean @default(false)
    overdue_days: Integer @default(0)
    overdue_penalty: Decimal(18,2) @default(0)
    
    status: Enum { PENDING, PAID, PARTIAL, OVERDUE } @required
  }

  // 担保信息
  collateral: Collateral {
    collateral_id: String(20) @required @unique
    contract_id: String(20) @required @reference(LoanContract.contract_id)
    
    collateral_type: Enum {
      REAL_ESTATE,         // 房产
      LAND,                // 土地
      VEHICLE,             // 车辆
      DEPOSIT,             // 存款
      STOCK,               // 股票
      GUARANTEE,           // 保证
      MORTGAGE             // 抵押
    } @required
    
    description: String(500) @required
    valuation_amount: Decimal(18,2) @required
    valuation_date: Date @required
    valuation_currency: String(3) @required
    
    // 担保比例
    loan_to_value_ratio: Decimal(5,2) @required
    
    // 状态
    status: Enum { PENDING, REGISTERED, RELEASED } @required
    registration_date: Date?
    release_date: Date?
  }
} @domain("BANKING") @version("1.0")
```

**贷款余额约束**：

$$
\forall c \in C: \text{outstanding\_principal}(c) = \text{contract\_amount}(c) - \sum_{i \in \text{repayments}(c)} \text{principal\_paid}(i)
$$

$$
\forall c \in C: \text{outstanding\_principal}(c) \geq 0
$$

---

## 5. 银行卡Schema

**定义5（银行卡Schema）**：

```text
Card_Business_Schema = (Bank_Card × Card_Transaction × Card_Holder)
```

**形式化DSL定义**：

```dsl
schema BankingCardBusiness {
  // 银行卡
  bank_card: BankCard {
    card_number: String(19) @required @unique @pattern("\\d{13,19}")
    card_type: Enum { DEBIT, CREDIT, PREPAID } @required
    
    // 关联账户
    account_number: String(32) @required @reference(Account.account_number)
    customer_id: String(20) @required
    
    // 卡片信息
    card_bin: String(6) @required
    product_code: String(10) @required
    expiry_date: String(4) @required @pattern("\\d{4}")
    cvv2: String(3) @encrypted
    
    // 信用额度（信用卡）
    credit_limit: Decimal(18,2)? @min(0)
    available_credit: Decimal(18,2)? @min(0)
    cash_advance_limit: Decimal(18,2)? @min(0)
    
    // 状态
    status: Enum {
      PENDING_ACTIVATION,
      ACTIVE,
      SUSPENDED,
      BLOCKED,
      EXPIRED,
      CLOSED
    } @required
    
    // 功能开关
    functions: CardFunctions {
      domestic_purchase: Boolean @default(true)
      overseas_purchase: Boolean @default(false)
      atm_withdrawal: Boolean @default(true)
      online_payment: Boolean @default(true)
      contactless: Boolean @default(true)
    }
    
    issue_date: Date @required
    activation_date: Date?
    last_transaction_date: Date?
  }

  // 卡片交易
  card_transaction: CardTransaction {
    transaction_id: String(35) @required @unique
    card_number: String(19) @required @reference(BankCard.card_number)
    
    // 交易类型
    transaction_type: Enum {
      PURCHASE,            // 消费
      WITHDRAWAL,          // 取现
      TRANSFER,            // 转账
      REFUND,              // 退款
      PAYMENT,             // 还款
      FEE,                 // 费用
      INTEREST             // 利息
    } @required
    
    // 交易渠道
    channel: Enum {
      POS,                 // POS消费
      ATM,                 // ATM
      ONLINE,              // 网上支付
      MOBILE,              // 移动支付
      RECURRING            // 定期扣款
    } @required
    
    // 交易金额
    transaction_amount: Decimal(18,2) @required
    transaction_currency: String(3) @required
    billing_amount: Decimal(18,2) @required
    billing_currency: String(3) @required
    exchange_rate: Decimal(10,6)?
    
    // 商户信息
    merchant_info: MerchantInfo {
      merchant_id: String(15) @required
      merchant_name: String(50) @required
      merchant_category_code: String(4) @required
      merchant_country: String(2) @required
      merchant_city: String(13)?
    }
    
    // 交易状态
    status: Enum {
      AUTHORIZED,          // 已授权
      CAPTURED,            // 已清算
      SETTLED,             // 已入账
      REVERSED,            // 已撤销
      DISPUTED,            // 争议中
      CHARGEBACK           // 拒付
    } @required
    
    // 时间戳
    authorization_time: DateTime @required
    settlement_time: DateTime?
    posting_date: Date?
    
    // 授权码
    authorization_code: String(6)?
    retrieval_reference: String(12) @required
  }

  // 持卡人信息
  card_holder: CardHolder {
    holder_id: String(20) @required @unique
    customer_id: String(20) @required
    
    name_on_card: String(26) @required
    pin: String(256) @encrypted @required
    pin_attempts: Integer @default(0) @max(3)
    pin_locked: Boolean @default(false)
    
    // 限额设置
    limits: TransactionLimits {
      daily_purchase_limit: Decimal(18,2) @default(50000)
      daily_withdrawal_limit: Decimal(18,2) @default(20000)
      single_transaction_limit: Decimal(18,2) @default(50000)
      online_transaction_limit: Decimal(18,2) @default(20000)
    }
    
    // 通知设置
    notifications: NotificationSettings {
      sms_enabled: Boolean @default(true)
      email_enabled: Boolean @default(false)
      push_enabled: Boolean @default(true)
      transaction_threshold: Decimal(18,2) @default(1000)
    }
  }
} @domain("BANKING") @version("1.0")
```

**信用卡额度约束**：

$$
\forall k \in K_{credit}: \text{available\_credit}(k) = \text{credit\_limit}(k) - \text{outstanding\_balance}(k)
$$

$$
\forall k \in K_{credit}: \text{available\_credit}(k) \geq 0
$$

---

## 6. 类型系统

**定义6（银行业务数据类型）**：

```text
Banking_Data_Type = Account_Type | Payment_Type | Credit_Type | Card_Type | Monetary_Type
```

**基本类型定义**：

```dsl
type AccountIdentification {
  iban: String(34)? @pattern("[A-Z]{2}\\d{2}[A-Z0-9]{1,30}")
  other: GenericAccountIdentification?
}

type GenericAccountIdentification {
  identification: String(34) @required
  scheme_name: String(35)?
  issuer: String(35)?
}

type FinancialInstitution {
  bicfi: String(11)? @pattern("[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?")
  clearing_system_member_id: ClearingSystemMemberIdentification?
  name: String(140)?
  postal_address: PostalAddress?
}

type ClearingSystemMemberIdentification {
  clearing_system_id: String(5)?
  member_id: String(28) @required
}

type PostalAddress {
  address_type: Enum { ADDR, PBOX, HOME, BIZZ, MLTO, DLVY }?
  department: String(70)?
  sub_department: String(70)?
  street_name: String(70)?
  building_number: String(16)?
  post_code: String(16)?
  town_name: String(35) @required
  country_sub_division: String(35)?
  country: String(2) @required @pattern("[A-Z]{2}")
  address_line: List<String(70)>?
}

type MonetaryAmount {
  currency: String(3) @required @pattern("[A-Z]{3}")
  value: Decimal(18,5) @required
}

type ContactInformation {
  name: String(140)?
  phone: String(20)?
  mobile: String(20)?
  fax: String(20)?
  email: String(254)?
  other: String(35)?
}
```

---

## 7. 约束规则

**约束1（账户余额一致性）**：

```text
∀ account ∈ Account:
  account.balance ≥ 0
  ∧ account.frozen_amount ≥ 0
  ∧ account.frozen_amount ≤ account.balance
  ∧ account.available_balance = account.balance - account.frozen_amount
```

**约束2（支付金额有效性）**：

```text
∀ payment ∈ PaymentInstruction:
  payment.amount.value > 0
  ∧ payment.amount.currency.length = 3
  ∧ payment.requested_execution_date ≤ today + 365
```

**约束3（贷款期限约束）**：

```text
∀ contract ∈ LoanContract:
  contract.term_months ≥ 1
  ∧ contract.term_months ≤ 360
  ∧ contract.maturity_date = add_months(contract.start_date, contract.term_months)
```

**约束4（信用卡额度约束）**：

```text
∀ card ∈ BankCard:
  card.card_type = CREDIT
  → card.credit_limit ≥ 0
  ∧ card.available_credit ≥ 0
  ∧ card.available_credit ≤ card.credit_limit
```

**约束5（交易状态转换）**：

```text
∀ transaction ∈ CardTransaction:
  transaction.status transition ∈ {
    AUTHORIZED → CAPTURED,
    AUTHORIZED → REVERSED,
    CAPTURED → SETTLED,
    CAPTURED → DISPUTED,
    SETTLED → DISPUTED,
    DISPUTED → CHARGEBACK
  }
```

---

## 8. 转换函数

**函数1（账户到ISO 20022转换）**：

```text
convert_account_to_iso20022: Account → ISO20022_Party
```

**函数2（支付指令到pacs.008转换）**：

```text
convert_payment_to_pacs008: PaymentInstruction → Pacs008
```

**函数3（贷款合同到报告格式转换）**：

```text
convert_loan_to_report: LoanContract → LoanReport
```

**函数4（卡交易到对账单转换）**：

```text
convert_transaction_to_statement: CardTransaction → StatementEntry
```

**函数5（余额计算）**：

```text
calculate_available_balance: Account → Decimal
calculate_available_balance(a) = a.balance - a.frozen_amount
```

---

## 9. 形式化定理

### 9.1 账户一致性定理

**定理1（账户余额一致性）**：

```text
∀ account ∈ Account:
  account.balance = account.available_balance + account.frozen_amount
```

**证明**：
由定义2中IndividualAccount的约束可得：
$$
\text{available\_balance} = \text{balance} - \text{frozen\_amount}
$$
移项即得：
$$
\text{balance} = \text{available\_balance} + \text{frozen\_amount} \quad \square
$$

### 9.2 支付原子性定理

**定理2（支付处理原子性）**：

```text
∀ payment ∈ PaymentInstruction:
  process_payment(payment) →
    (debit_success ∧ credit_success) ∨ (¬debit_success ∧ ¬credit_success)
```

**证明**：
由定义3中支付指令的状态机和约束规则，支付处理必须满足原子性要求：
1. 如果借记成功，则必须完成贷记
2. 如果贷记失败，则必须回滚借记
3. 不存在借记成功但贷记失败的状态 $\square$

### 9.3 信贷风险定理

**定理3（贷款余额非负性）**：

```text
∀ contract ∈ LoanContract:
  contract.outstanding_principal ≥ 0
```

**证明**：
由定义4中LoanContract的约束：
$$
\text{outstanding\_principal} = \text{contract\_amount} - \sum_{i \in \text{repayments}} \text{principal\_paid}(i)
$$
且还款本金总额不超过合同金额：
$$
\sum_{i \in \text{repayments}} \text{principal\_paid}(i) \leq \text{contract\_amount}
$$
因此：
$$
\text{outstanding\_principal} \geq 0 \quad \square
$$

---

## 10. 数学模型

### 10.1 账户状态机

**账户状态转换**：

```
                    ┌─────────────┐
                    │   ACTIVE    │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               │               ▼
    ┌─────────────┐        │        ┌─────────────┐
    │   DORMANT   │◄───────┴───────►│   FROZEN    │
    └──────┬──────┘                 └──────┬──────┘
           │                               │
           │         ┌─────────────┐       │
           └────────►│   CLOSED    │◄──────┘
                     └─────────────┘
```

**状态转移函数**：

$$
\delta_A: S_A \times E_A \rightarrow S_A
$$

其中：
- $S_A = \{\text{ACTIVE}, \text{DORMANT}, \text{FROZEN}, \text{CLOSED}\}$
- $E_A = \{\text{no\_activity}, \text{frozen\_request}, \text{unfreeze}, \text{close\_request}, \text{reactivate}\}$

### 10.2 支付状态机

**支付状态转换**：

```
┌───────────┐    submit    ┌─────────────┐    accept    ┌───────────┐
│  PENDING  │──────────────►│  PROCESSING │──────────────►│ ACCEPTED  │
└─────┬─────┘               └──────┬──────┘               └─────┬─────┘
      │                            │                            │
      │ reject                     │ reject                     │ settle
      ▼                            ▼                            ▼
┌───────────┐               ┌───────────┐               ┌───────────┐
│ REJECTED  │               │ REJECTED  │               │  SETTLED  │
└───────────┘               └───────────┘               └───────────┘
```

**状态转移函数**：

$$
\delta_P: S_P \times E_P \rightarrow S_P
$$

### 10.3 贷款状态机

**贷款状态转换**：

```
┌─────────────────────┐
│ PENDING_DISBURSEMENT│
└──────────┬──────────┘
           │ disburse
           ▼
     ┌───────────┐     payment    ┌───────────┐
     │   ACTIVE  │◄──────────────►│   CLOSED  │
     └─────┬─────┘                └───────────┘
           │
     late  │
           ▼
     ┌───────────┐    default     ┌───────────┐
     │  OVERDUE  │───────────────►│ DEFAULTED │
     └───────────┘                └─────┬─────┘
                                        │ write-off
                                        ▼
                                   ┌───────────┐
                                   │ WRITE_OFF │
                                   └───────────┘
```

**状态转移函数**：

$$
\delta_C: S_C \times E_C \rightarrow S_C
$$

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
