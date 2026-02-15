# 银行业务Schema转换应用

## 📑 目录

- [银行业务Schema转换应用](#银行业务schema转换应用)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
    - [1.2 转换架构](#12-转换架构)
  - [2. 核心银行系统转换](#2-核心银行系统转换)
    - [2.1 账户数据转换](#21-账户数据转换)
    - [2.2 交易数据转换](#22-交易数据转换)
    - [2.3 客户数据转换](#23-客户数据转换)
  - [3. 支付系统转换](#3-支付系统转换)
    - [3.1 跨行支付转换](#31-跨行支付转换)
    - [3.2 跨境支付转换](#32-跨境支付转换)
    - [3.3 实时支付转换](#33-实时支付转换)
  - [4. ISO 20022转换](#4-iso-20022转换)
    - [4.1 账户到ISO 20022转换](#41-账户到iso-20022转换)
    - [4.2 支付到pacs.008转换](#42-支付到pacs008转换)
    - [4.3 对账单到camt.053转换](#43-对账单到camt053转换)
  - [5. 银行数据存储与分析](#5-银行数据存储与分析)
    - [5.1 PostgreSQL银行数据存储](#51-postgresql银行数据存储)
    - [5.2 银行业务分析查询](#52-银行业务分析查询)
  - [6. 转换验证与测试](#6-转换验证与测试)
    - [6.1 数据一致性验证](#61-数据一致性验证)
    - [6.2 业务规则验证](#62-业务规则验证)
    - [6.3 性能测试](#63-性能测试)
  - [7. 转换工具与平台](#7-转换工具与平台)
    - [7.1 ETL工具](#71-etl工具)
    - [7.2 消息转换平台](#72-消息转换平台)
    - [7.3 API网关](#73-api网关)

---

## 1. 转换体系概述

### 1.1 转换目标

银行业务Schema转换体系支持以下转换目标：

1. **核心银行系统转换**：核心系统数据迁移、系统升级
2. **支付系统转换**：跨行支付、跨境支付、实时支付
3. **ISO 20022转换**：传统格式与ISO 20022格式互转
4. **数据存储转换**：业务数据到分析数据仓库
5. **监管报送转换**：监管报表、统计报送

**转换函数定义**：

```text
Banking_Transform = {
  core_system_transform: CoreBanking × Target → CoreBanking',
  payment_transform: Payment × Standard → Payment',
  iso20022_transform: Message × Format → ISO20022Message,
  storage_transform: Transaction × Schema → StorageRecord,
  report_transform: Data × Template → Report
}
```

### 1.2 转换架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        转换架构层                                │
├───────────────────┬───────────────────┬─────────────────────────┤
│    源系统层        │     转换引擎层     │       目标系统层         │
├───────────────────┼───────────────────┼─────────────────────────┤
│ 核心银行系统       │   Schema解析器     │    新核心系统            │
│ 支付系统          │   数据映射引擎      │    ISO 20022系统         │
│ 卡系统            │   规则引擎         │    数据仓库              │
│ 信贷系统          │   验证引擎         │    监管报送系统           │
│ 网银系统          │   错误处理         │    API网关               │
└───────────────────┴───────────────────┴─────────────────────────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │     监控与治理层       │
                    │  日志、审计、质量监控   │
                    └───────────────────────┘
```

---

## 2. 核心银行系统转换

### 2.1 账户数据转换

**转换规则**：

```python
def transform_account_legacy_to_modern(legacy_account: LegacyAccount) -> ModernAccount:
    """将传统账户格式转换为现代账户格式"""
    modern_account = ModernAccount()

    # 账号映射
    modern_account.account_number = legacy_account.acct_no.strip()

    # 账户类型映射
    type_mapping = {
        "S": AccountType.SAVINGS,
        "C": AccountType.CHECKING,
        "F": AccountType.FIXED_DEPOSIT,
        "L": AccountType.CALL_DEPOSIT
    }
    modern_account.account_type = type_mapping.get(
        legacy_account.acct_type, AccountType.SAVINGS
    )

    # 币种映射
    modern_account.currency = legacy_account.ccy_code

    # 余额转换（从分转换为元）
    modern_account.balance = Decimal(legacy_account.balance) / 100
    modern_account.available_balance = Decimal(legacy_account.avail_bal) / 100

    # 状态映射
    status_mapping = {
        "1": AccountStatus.ACTIVE,
        "2": AccountStatus.DORMANT,
        "3": AccountStatus.FROZEN,
        "9": AccountStatus.CLOSED
    }
    modern_account.status = status_mapping.get(
        legacy_account.status, AccountStatus.ACTIVE
    )

    # 日期转换
    modern_account.open_date = parse_date(legacy_account.open_dt)

    # 客户号映射
    modern_account.customer_id = legacy_account.cust_no.strip()

    # 开户行映射
    modern_account.branch_code = legacy_account.open_brh

    return modern_account
```

**批量转换示例**：

```python
class AccountMigrationService:
    """账户数据迁移服务"""

    def __init__(self, source_db: Connection, target_db: Connection):
        self.source = source_db
        self.target = target_db
        self.logger = logging.getLogger(__name__)

    def migrate_accounts(self, batch_size: int = 1000) -> MigrationResult:
        """批量迁移账户数据"""
        result = MigrationResult()

        # 查询源数据
        cursor = self.source.cursor()
        cursor.execute("""
            SELECT acct_no, acct_type, ccy_code, balance, avail_bal,
                   status, open_dt, cust_no, open_brh
            FROM legacy_accounts
            WHERE migrated = 'N'
        """)

        batch = []
        for row in cursor:
            legacy_account = LegacyAccount(*row)
            try:
                modern_account = transform_account_legacy_to_modern(legacy_account)
                batch.append(modern_account)

                if len(batch) >= batch_size:
                    self._insert_batch(batch)
                    result.success_count += len(batch)
                    batch = []

            except Exception as e:
                result.error_count += 1
                result.errors.append({
                    'account': legacy_account.acct_no,
                    'error': str(e)
                })
                self.logger.error(f"Failed to migrate account {legacy_account.acct_no}: {e}")

        # 处理剩余批次
        if batch:
            self._insert_batch(batch)
            result.success_count += len(batch)

        return result

    def _insert_batch(self, accounts: List[ModernAccount]):
        """批量插入目标数据库"""
        cursor = self.target.cursor()

        insert_sql = """
            INSERT INTO modern_accounts
            (account_number, account_type, currency, balance, available_balance,
             status, open_date, customer_id, branch_code, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (account_number) DO UPDATE SET
            balance = EXCLUDED.balance,
            available_balance = EXCLUDED.available_balance,
            status = EXCLUDED.status
        """

        data = [
            (a.account_number, a.account_type.value, a.currency,
             a.balance, a.available_balance, a.status.value,
             a.open_date, a.customer_id, a.branch_code)
            for a in accounts
        ]

        cursor.executemany(insert_sql, data)
        self.target.commit()
```

### 2.2 交易数据转换

**交易记录转换**：

```python
def transform_transaction_legacy_to_modern(legacy_txn: LegacyTransaction) -> ModernTransaction:
    """将传统交易记录转换为现代格式"""
    txn = ModernTransaction()

    # 交易ID生成
    txn.transaction_id = generate_txn_id(
        legacy_txn.txn_date,
        legacy_txn.txn_seq
    )

    # 账号映射
    txn.account_number = legacy_txn.acct_no.strip()

    # 交易类型映射
    txn_type_mapping = {
        "D": TransactionType.DEBIT,
        "C": TransactionType.CREDIT,
        "T": TransactionType.TRANSFER,
        "I": TransactionType.INTEREST,
        "F": TransactionType.FEE
    }
    txn.transaction_type = txn_type_mapping.get(
        legacy_txn.drcr_flag, TransactionType.OTHER
    )

    # 金额转换
    txn.amount = Decimal(legacy_txn.txn_amt) / 100
    txn.currency = legacy_txn.txn_ccy

    # 借贷方向
    if legacy_txn.drcr_flag == "D":
        txn.direction = Direction.DEBIT
    else:
        txn.direction = Direction.CREDIT

    # 交易时间
    txn.transaction_date = parse_date(legacy_txn.txn_date)
    txn.transaction_time = parse_time(legacy_txn.txn_time)
    txn.value_date = parse_date(legacy_txn.value_date)

    # 交易描述
    txn.description = legacy_txn.txn_desc.decode('gbk').strip()

    # 对手方信息
    txn.counterparty_account = legacy_txn.opp_acct_no.strip() if legacy_txn.opp_acct_no else None
    txn.counterparty_name = legacy_txn.opp_name.decode('gbk').strip() if legacy_txn.opp_name else None

    # 余额
    txn.balance_after = Decimal(legacy_txn.acct_bal) / 100

    # 渠道映射
    channel_mapping = {
        "01": Channel.COUNTER,
        "02": Channel.ATM,
        "03": Channel.POS,
        "04": Channel.ONLINE,
        "05": Channel.MOBILE
    }
    txn.channel = channel_mapping.get(
        legacy_txn.channel_id, Channel.OTHER
    )

    return txn
```

### 2.3 客户数据转换

**客户信息转换**：

```python
def transform_customer_legacy_to_modern(legacy_cust: LegacyCustomer) -> ModernCustomer:
    """将传统客户信息转换为现代格式"""
    customer = ModernCustomer()

    # 客户号
    customer.customer_id = legacy_cust.cust_no.strip()

    # 客户类型
    if legacy_cust.cust_type == "1":
        customer.customer_type = CustomerType.INDIVIDUAL
    else:
        customer.customer_type = CustomerType.CORPORATE

    # 姓名
    if customer.customer_type == CustomerType.INDIVIDUAL:
        customer.first_name = legacy_cust.first_name.decode('gbk').strip()
        customer.last_name = legacy_cust.last_name.decode('gbk').strip()
        customer.full_name = f"{customer.last_name}{customer.first_name}"
    else:
        customer.company_name = legacy_cust.cust_name.decode('gbk').strip()
        customer.full_name = customer.company_name

    # 证件信息
    id_type_mapping = {
        "01": IdentificationType.ID_CARD,
        "02": IdentificationType.PASSPORT,
        "03": IdentificationType.HK_MACAO_PASS,
        "20": IdentificationType.BUSINESS_LICENSE
    }
    customer.identification_type = id_type_mapping.get(
        legacy_cust.id_type, IdentificationType.OTHER
    )
    customer.identification_number = legacy_cust.id_no.strip()

    # 联系方式
    customer.phone = legacy_cust.phone_no.strip()
    customer.email = legacy_cust.email_addr.strip() if legacy_cust.email_addr else None
    customer.address = Address(
        country="CN",
        province=legacy_cust.province.decode('gbk').strip(),
        city=legacy_cust.city.decode('gbk').strip(),
        district=legacy_cust.district.decode('gbk').strip(),
        street=legacy_cust.street.decode('gbk').strip(),
        postal_code=legacy_cust.zip_code.strip()
    )

    # 风险评级
    risk_mapping = {
        "L": RiskLevel.LOW,
        "M": RiskLevel.MEDIUM,
        "H": RiskLevel.HIGH
    }
    customer.risk_level = risk_mapping.get(
        legacy_cust.risk_grade, RiskLevel.MEDIUM
    )

    # KYC状态
    kyc_mapping = {
        "0": KycStatus.PENDING,
        "1": KycStatus.VERIFIED,
        "2": KycStatus.REJECTED
    }
    customer.kyc_status = kyc_mapping.get(
        legacy_cust.kyc_flag, KycStatus.PENDING
    )

    # 创建时间
    customer.created_at = parse_datetime(legacy_cust.create_dt)

    return customer
```

---

## 3. 支付系统转换

### 3.1 跨行支付转换

**HVPS（大额支付系统）转换**：

```python
def convert_to_hvps_message(payment: PaymentInstruction) -> HVPSMessage:
    """将支付指令转换为大额支付系统报文"""
    hvps = HVPSMessage()

    # 报文头
    hvps.message_header.version = "1.0"
    hvps.message_header.message_type = "hvps.111.001.01"
    hvps.message_header.creation_time = datetime.now()
    hvps.message_header.message_id = generate_message_id()

    # 业务标识
    hvps.business_id = payment.instruction_id
    hvps.business_type = "01"  # 普通贷记业务

    # 付款方信息
    hvps.payer.bank_code = payment.debtor_agent.clearing_code
    hvps.payer.account = payment.debtor.account.identification
    hvps.payer.name = payment.debtor.name

    # 收款方信息
    hvps.payee.bank_code = payment.creditor_agent.clearing_code
    hvps.payee.account = payment.creditor.account.identification
    hvps.payee.name = payment.creditor.name

    # 金额
    hvps.amount = payment.amount.value
    hvps.currency = payment.amount.currency

    # 业务优先级
    if payment.priority == Priority.HIGH:
        hvps.priority = "0"  # 特急
    elif payment.priority == Priority.NORMAL:
        hvps.priority = "1"  # 紧急
    else:
        hvps.priority = "2"  # 普通

    # 附言
    if payment.remittance_info:
        hvps.remarks = payment.remittance_info.unstructured[:60]

    # 时间
    hvps.value_date = payment.value_date or get_next_business_date()

    return hvps
```

**BEPS（小额支付系统）转换**：

```python
def convert_to_beps_message(payment: PaymentInstruction) -> BEPSMessage:
    """将支付指令转换为小额支付系统报文"""
    beps = BEPSMessage()

    # 报文头
    beps.message_header.version = "1.0"
    beps.message_header.message_type = "beps.121.001.01"
    beps.message_header.creation_time = datetime.now()

    # 批次信息
    beps.batch_id = generate_batch_id()
    beps.batch_count = 1
    beps.batch_amount = payment.amount.value

    # 交易明细
    txn = BEPSTransaction()
    txn.transaction_id = payment.instruction_id
    txn.transaction_type = "01"  # 普通贷记

    # 付款方
    txn.payer.bank_code = payment.debtor_agent.clearing_code
    txn.payer.account = payment.debtor.account.identification
    txn.payer.name = payment.debtor.name[:60]

    # 收款方
    txn.payee.bank_code = payment.creditor_agent.clearing_code
    txn.payee.account = payment.creditor.account.identification
    txn.payee.name = payment.creditor.name[:60]

    # 金额
    txn.amount = payment.amount.value
    txn.currency = payment.amount.currency

    # 附言
    if payment.remittance_info:
        txn.remarks = payment.remittance_info.unstructured[:30]

    beps.transactions = [txn]

    return beps
```

### 3.2 跨境支付转换

**CIPS（跨境人民币支付系统）转换**：

```python
def convert_to_cips_message(payment: PaymentInstruction) -> CIPSMessage:
    """将支付指令转换为CIPS报文"""
    cips = CIPSMessage()

    # 报文头
    cips.message_header.version = "1.0"
    cips.message_header.message_type = "cips.111.001.01"
    cips.message_header.creation_time = datetime.now()
    cips.message_header.message_id = generate_cips_message_id()

    # 业务标识
    cips.business_id = payment.instruction_id
    cips.business_type = "01"  # 客户汇款

    # 发起直接参与者
    cips.originator_direct_participant = payment.debtor_agent.bicfi

    # 付款方信息
    cips.originator.account = payment.debtor.account.identification
    cips.originator.name = payment.debtor.name
    cips.originator.address = convert_address(payment.debtor.postal_address)
    cips.originator.identification = payment.debtor.identification

    # 收款方信息
    cips.beneficiary.account = payment.creditor.account.identification
    cips.beneficiary.name = payment.creditor.name
    cips.beneficiary.address = convert_address(payment.creditor.postal_address)
    cips.beneficiary.bank_bic = payment.creditor_agent.bicfi

    # 金额
    cips.settlement_amount = payment.amount.value
    cips.settlement_currency = payment.amount.currency

    # 清算要求
    cips.settlement_priority = "00"  # 普通
    cips.settlement_method = "02"    # 净额清算

    # 费用承担方式
    cips.charge_bearer = "SHA"  # 共同承担

    # 附言
    if payment.remittance_info:
        cips.payment_details = payment.remittance_info.unstructured[:140]

    # 时间要求
    cips.expected_settlement_time = payment.requested_execution_time

    return cips
```

**SWIFT MT103到MX转换**：

```python
def convert_mt103_to_pacs008(mt103: MT103Message) -> Pacs008Message:
    """将SWIFT MT103转换为ISO 20022 pacs.008"""
    pacs008 = Pacs008Message()

    # Group Header
    pacs008.group_header.message_identification = generate_message_id()
    pacs008.group_header.creation_date_time = datetime.now()
    pacs008.group_header.number_of_transactions = 1
    pacs008.group_header.control_sum = parse_amount(mt103.field_32a.amount)

    # Credit Transfer Transaction Information
    txn = CreditTransferTransactionInformation()

    # Payment Identification
    txn.payment_identification.instruction_identification = mt103.field_20
    txn.payment_identification.end_to_end_identification = mt103.field_20

    # Amount
    amount = parse_amount(mt103.field_32a.amount)
    currency = mt103.field_32a.currency
    txn.amount.instructed_amount = ActiveCurrencyAndAmount(
        currency=currency,
        value=amount
    )

    # Debtor (Sender)
    debtor_info = parse_party_field(mt103.field_50a or mt103.field_50k)
    txn.debtor.name = debtor_info.name
    if debtor_info.account:
        txn.debtor_account.identification.other = GenericAccountIdentification(
            identification=debtor_info.account
        )
    if debtor_info.address:
        txn.debtor.postal_address = convert_swift_address(debtor_info.address)

    # Creditor (Receiver)
    creditor_info = parse_party_field(mt103.field_59 or mt103.field_59a)
    txn.creditor.name = creditor_info.name
    if creditor_info.account:
        txn.creditor_account.identification.other = GenericAccountIdentification(
            identification=creditor_info.account
        )
    if creditor_info.address:
        txn.creditor.postal_address = convert_swift_address(creditor_info.address)

    # Remittance Information
    if hasattr(mt103, 'field_70'):
        txn.remittance_information.unstructured = mt103.field_70

    pacs008.credit_transfer_transaction_information = [txn]

    return pacs008
```

### 3.3 实时支付转换

**IBPS（网上支付跨行清算）转换**：

```python
def convert_to_ibps_message(payment: PaymentInstruction) -> IBPSMessage:
    """将支付指令转换为IBPS报文"""
    ibps = IBPSMessage()

    # 报文头
    ibps.message_header.system_code = "IBPS"
    ibps.message_header.trade_code = "100001"  # 普通贷记业务
    ibps.message_header.create_time = datetime.now()
    ibps.message_header.msg_id = generate_ibps_msg_id()

    # 发起方信息
    ibps.sender.bank_code = payment.debtor_agent.clearing_code
    ibps.sender.branch_code = payment.debtor_agent.branch_code

    # 接收方信息
    ibps.receiver.bank_code = payment.creditor_agent.clearing_code
    ibps.receiver.branch_code = payment.creditor_agent.branch_code

    # 交易信息
    ibps.transaction.transaction_id = payment.instruction_id
    ibps.transaction.amount = payment.amount.value
    ibps.transaction.currency = payment.amount.currency

    # 付款方
    ibps.transaction.payer.account = payment.debtor.account.identification
    ibps.transaction.payer.name = payment.debtor.name[:60]
    ibps.transaction.payer.account_type = "01"  # 个人借记卡

    # 收款方
    ibps.transaction.payee.account = payment.creditor.account.identification
    ibps.transaction.payee.name = payment.creditor.name[:60]
    ibps.transaction.payee.account_type = "01"

    # 附言
    if payment.remittance_info:
        ibps.transaction.remarks = payment.remittance_info.unstructured[:30]

    # 响应方式
    ibps.transaction.response_type = "0"  # 需要回执

    return ibps
```

---

## 4. ISO 20022转换

### 4.1 账户到ISO 20022转换

```python
def convert_account_to_iso20022_party(account: BankAccount) -> PartyIdentification:
    """将银行账户转换为ISO 20022 Party格式"""
    party = PartyIdentification()

    # 名称
    party.name = account.account_holder_name

    # 邮政地址
    if account.address:
        party.postal_address = PostalAddress6()
        party.postal_address.address_line = [
            account.address.street,
            account.address.district
        ]
        party.postal_address.town_name = account.address.city
        party.postal_address.country_sub_division = account.address.province
        party.postal_address.country = account.address.country
        party.postal_address.post_code = account.address.postal_code

    # 标识
    if account.identification_number:
        party.identification = PartyIdentification43Choice()
        party.identification.org_id = OrganisationIdentification()
        party.identification.org_id.any_bic = None
        party.identification.org_id.othr = [
            GenericOrganisationIdentification(
                id=account.identification_number,
                schme_nm=None,
                issr=None
            )
        ]

    return party

def convert_account_to_cash_account(account: BankAccount) -> CashAccount16:
    """将银行账户转换为ISO 20022 CashAccount格式"""
    cash_account = CashAccount16()

    # 账户标识
    cash_account.identification = AccountIdentification4Choice()
    if account.iban:
        cash_account.identification.iban = account.iban
    else:
        cash_account.identification.other = GenericAccountIdentification(
            id=account.account_number,
            schme_nm=None,
            issr=account.branch_code
        )

    # 账户名称
    cash_account.name = account.account_holder_name

    # 币种
    cash_account.currency = account.currency

    return cash_account
```

### 4.2 支付到pacs.008转换

```python
def convert_payment_to_pacs008(payment: PaymentInstruction) -> Pacs008Message:
    """将支付指令转换为pacs.008格式"""
    pacs008 = Pacs008Message()

    # Group Header
    pacs008.group_header = GroupHeader()
    pacs008.group_header.message_identification = payment.instruction_id
    pacs008.group_header.creation_date_time = datetime.now()
    pacs008.group_header.number_of_transactions = 1
    pacs008.group_header.control_sum = payment.amount.value

    # Payment Type Information
    pacs008.group_header.payment_type_information = PaymentTypeInformation()
    pacs008.group_header.payment_type_information.service_level = ServiceLevel8Choice()
    pacs008.group_header.payment_type_information.service_level.code = "SEPA"

    # Credit Transfer Transaction Information
    cdt_trf_tx_inf = CreditTransferTransactionInformation()

    # Payment Identification
    cdt_trf_tx_inf.payment_identification = PaymentIdentification3()
    cdt_trf_tx_inf.payment_identification.instruction_identification = payment.instruction_id
    cdt_trf_tx_inf.payment_identification.end_to_end_identification = payment.end_to_end_id or payment.instruction_id

    # Amount
    cdt_trf_tx_inf.amount = AmountType3Choice()
    cdt_trf_tx_inf.amount.instructed_amount = ActiveCurrencyAndAmount(
        currency=payment.amount.currency,
        value=payment.amount.value
    )

    # Debtor
    cdt_trf_tx_inf.debtor = convert_party_to_iso20022(payment.debtor)
    cdt_trf_tx_inf.debtor_account = convert_account_to_cash_account16(payment.debtor_account)

    # Debtor Agent
    if payment.debtor_agent:
        cdt_trf_tx_inf.debtor_agent = BranchAndFinancialInstitutionIdentification4()
        cdt_trf_tx_inf.debtor_agent.financial_institution_identification = FinancialInstitutionIdentification7()
        cdt_trf_tx_inf.debtor_agent.financial_institution_identification.bicfi = payment.debtor_agent.bicfi

    # Creditor Agent
    if payment.creditor_agent:
        cdt_trf_tx_inf.creditor_agent = BranchAndFinancialInstitutionIdentification4()
        cdt_trf_tx_inf.creditor_agent.financial_institution_identification = FinancialInstitutionIdentification7()
        cdt_trf_tx_inf.creditor_agent.financial_institution_identification.bicfi = payment.creditor_agent.bicfi

    # Creditor
    cdt_trf_tx_inf.creditor = convert_party_to_iso20022(payment.creditor)
    cdt_trf_tx_inf.creditor_account = convert_account_to_cash_account16(payment.creditor_account)

    # Remittance Information
    if payment.remittance_info:
        cdt_trf_tx_inf.remittance_information = RemittanceInformation7()
        if payment.remittance_info.unstructured:
            cdt_trf_tx_inf.remittance_information.unstructured = [payment.remittance_info.unstructured]

    pacs008.credit_transfer_transaction_information = [cdt_trf_tx_inf]

    return pacs008
```

### 4.3 对账单到camt.053转换

```python
def convert_statement_to_camt053(statement: BankStatement) -> Camt053Message:
    """将银行对账单转换为camt.053格式"""
    camt053 = Camt053Message()

    # Group Header
    camt053.group_header = GroupHeader()
    camt053.group_header.message_identification = f"STMT{statement.statement_id}"
    camt053.group_header.creation_date_time = datetime.now()

    # Statement
    stmt = AccountStatement()
    stmt.identification = statement.statement_id
    stmt.electronic_sequence_number = statement.sequence_number
    stmt.legal_sequence_number = statement.legal_sequence_number

    # Account
    stmt.account = CashAccount20()
    stmt.account.identification = AccountIdentification4Choice()
    if statement.account.iban:
        stmt.account.identification.iban = statement.account.iban
    else:
        stmt.account.identification.other = GenericAccountIdentification(
            id=statement.account.account_number,
            schme_nm=None,
            issr=None
        )
    stmt.account.currency = statement.account.currency
    stmt.account.name = statement.account.account_holder_name

    # Owner
    if statement.account.owner:
        stmt.account.owner = PartyIdentification()
        stmt.account.owner.name = statement.account.owner.name

    # Balance
    for bal in statement.balances:
        cash_balance = CashBalance()
        cash_balance.type = BalanceType12Choice()
        cash_balance.type.code = convert_balance_type(bal.balance_type)

        cash_balance.amount = AmountAndCurrencyExchangeDetails3()
        cash_balance.amount.amount = ActiveOrHistoricCurrencyAndAmount(
            currency=bal.currency,
            value=bal.amount
        )

        cash_balance.credit_debit_indicator = "CRDT" if bal.amount >= 0 else "DBIT"
        cash_balance.date = DateAndDateTimeChoice()
        cash_balance.date.date = bal.date

        stmt.balance.append(cash_balance)

    # Entry
    for entry in statement.entries:
        report_entry = ReportEntry()
        report_entry.amount = AmountAndCurrencyExchangeDetails3()
        report_entry.amount.amount = ActiveOrHistoricCurrencyAndAmount(
            currency=entry.currency,
            value=abs(entry.amount)
        )
        report_entry.credit_debit_indicator = "CRDT" if entry.amount > 0 else "DBIT"
        report_entry.status = EntryStatus2Code.BOOK

        report_entry.booking_date = DateAndDateTimeChoice()
        report_entry.booking_date.date = entry.booking_date

        report_entry.value_date = DateAndDateTimeChoice()
        report_entry.value_date.date = entry.value_date

        report_entry.entry_reference = entry.transaction_reference

        # Transaction Details
        txn_details = EntryTransactionDetails()
        txn_details.transaction_identification = entry.transaction_id

        if entry.counterparty:
            txn_details.related_parties = TransactionParty()
            txn_details.related_parties.debtor = PartyIdentification()
            txn_details.related_parties.debtor.name = entry.counterparty.name

        if entry.remittance_info:
            txn_details.remittance_information = RemittanceInformation7()
            txn_details.remittance_information.unstructured = [entry.remittance_info]

        report_entry.entry_details = [txn_details]
        stmt.entry.append(report_entry)

    camt053.statement = [stmt]

    return camt053
```

---

## 5. 银行数据存储与分析

### 5.1 PostgreSQL银行数据存储

**银行数据存储方案**：

```python
import psycopg2
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

class BankingDataStorage:
    """银行业务数据存储系统"""

    def __init__(self, connection_string: str):
        if not connection_string:
            raise ValueError("Connection string cannot be empty")

        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("BankingDataStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e

    def _create_tables(self):
        """创建银行业务数据表"""

        # 客户信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id BIGSERIAL PRIMARY KEY,
                customer_id VARCHAR(20) UNIQUE NOT NULL,
                customer_type VARCHAR(20) NOT NULL,
                customer_name VARCHAR(140) NOT NULL,
                identification_type VARCHAR(20),
                identification_number VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(254),
                address JSONB,
                risk_level VARCHAR(10) DEFAULT 'MEDIUM',
                kyc_status VARCHAR(20) DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 账户信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id BIGSERIAL PRIMARY KEY,
                account_number VARCHAR(32) UNIQUE NOT NULL,
                customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
                account_type VARCHAR(30) NOT NULL,
                account_category VARCHAR(30),
                currency VARCHAR(3) NOT NULL,
                balance DECIMAL(18,2) DEFAULT 0,
                available_balance DECIMAL(18,2) DEFAULT 0,
                frozen_amount DECIMAL(18,2) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'ACTIVE',
                open_date DATE NOT NULL,
                interest_rate DECIMAL(5,4),
                branch_code VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 交易记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id BIGSERIAL PRIMARY KEY,
                transaction_id VARCHAR(35) UNIQUE NOT NULL,
                account_number VARCHAR(32) NOT NULL REFERENCES accounts(account_number),
                transaction_type VARCHAR(30) NOT NULL,
                direction VARCHAR(10) NOT NULL,
                amount DECIMAL(18,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                balance_after DECIMAL(18,2) NOT NULL,
                transaction_date DATE NOT NULL,
                transaction_time TIME,
                value_date DATE,
                counterparty_account VARCHAR(32),
                counterparty_name VARCHAR(140),
                description VARCHAR(255),
                channel VARCHAR(20),
                status VARCHAR(20) DEFAULT 'COMPLETED',
                reference_number VARCHAR(35),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 支付指令表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_instructions (
                id BIGSERIAL PRIMARY KEY,
                instruction_id VARCHAR(35) UNIQUE NOT NULL,
                instruction_type VARCHAR(30) NOT NULL,
                message_type VARCHAR(20),
                priority VARCHAR(10) DEFAULT 'NORMAL',
                debtor_account VARCHAR(32),
                debtor_name VARCHAR(140),
                creditor_account VARCHAR(32),
                creditor_name VARCHAR(140),
                amount DECIMAL(18,5) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                requested_execution_date DATE,
                value_date DATE,
                remittance_info VARCHAR(140),
                status VARCHAR(20) DEFAULT 'PENDING',
                clearing_system VARCHAR(20),
                message_reference VARCHAR(35),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 贷款合同表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS loan_contracts (
                id BIGSERIAL PRIMARY KEY,
                contract_id VARCHAR(20) UNIQUE NOT NULL,
                customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
                product_code VARCHAR(10) NOT NULL,
                contract_amount DECIMAL(18,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                outstanding_principal DECIMAL(18,2) NOT NULL,
                outstanding_interest DECIMAL(18,2) DEFAULT 0,
                interest_rate DECIMAL(5,4) NOT NULL,
                interest_rate_type VARCHAR(10) NOT NULL,
                repayment_method VARCHAR(30) NOT NULL,
                start_date DATE NOT NULL,
                maturity_date DATE NOT NULL,
                term_months INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'PENDING_DISBURSEMENT',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 银行卡表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bank_cards (
                id BIGSERIAL PRIMARY KEY,
                card_number VARCHAR(19) UNIQUE NOT NULL,
                card_type VARCHAR(20) NOT NULL,
                account_number VARCHAR(32) NOT NULL REFERENCES accounts(account_number),
                customer_id VARCHAR(20) NOT NULL,
                card_bin VARCHAR(6) NOT NULL,
                product_code VARCHAR(10) NOT NULL,
                expiry_date VARCHAR(4) NOT NULL,
                credit_limit DECIMAL(18,2),
                available_credit DECIMAL(18,2),
                status VARCHAR(20) DEFAULT 'PENDING_ACTIVATION',
                issue_date DATE NOT NULL,
                activation_date DATE,
                last_transaction_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
            ON accounts(customer_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_account_date
            ON transactions(account_number, transaction_date DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_payment_instructions_status
            ON payment_instructions(status, created_at)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_loan_contracts_customer
            ON loan_contracts(customer_id, status)
        """)

        self.conn.commit()

    def store_customer(self, customer_data: Dict):
        """存储客户信息"""
        try:
            self.cur.execute("""
                INSERT INTO customers
                (customer_id, customer_type, customer_name, identification_type,
                 identification_number, phone, email, address, risk_level, kyc_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (customer_id) DO UPDATE SET
                customer_name = EXCLUDED.customer_name,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                address = EXCLUDED.address,
                risk_level = EXCLUDED.risk_level,
                kyc_status = EXCLUDED.kyc_status,
                updated_at = CURRENT_TIMESTAMP
            """, (
                customer_data['customer_id'],
                customer_data['customer_type'],
                customer_data['customer_name'],
                customer_data.get('identification_type'),
                customer_data.get('identification_number'),
                customer_data.get('phone'),
                customer_data.get('email'),
                json.dumps(customer_data.get('address')),
                customer_data.get('risk_level', 'MEDIUM'),
                customer_data.get('kyc_status', 'PENDING')
            ))
            self.conn.commit()
            logger.info(f"Stored customer: {customer_data['customer_id']}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store customer: {e}")
            raise

    def store_account(self, account_data: Dict):
        """存储账户信息"""
        try:
            self.cur.execute("""
                INSERT INTO accounts
                (account_number, customer_id, account_type, account_category,
                 currency, balance, available_balance, frozen_amount,
                 status, open_date, interest_rate, branch_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (account_number) DO UPDATE SET
                balance = EXCLUDED.balance,
                available_balance = EXCLUDED.available_balance,
                frozen_amount = EXCLUDED.frozen_amount,
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
            """, (
                account_data['account_number'],
                account_data['customer_id'],
                account_data['account_type'],
                account_data.get('account_category'),
                account_data['currency'],
                account_data.get('balance', 0),
                account_data.get('available_balance', 0),
                account_data.get('frozen_amount', 0),
                account_data.get('status', 'ACTIVE'),
                account_data['open_date'],
                account_data.get('interest_rate'),
                account_data.get('branch_code')
            ))
            self.conn.commit()
            logger.info(f"Stored account: {account_data['account_number']}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store account: {e}")
            raise

    def store_transaction(self, txn_data: Dict):
        """存储交易记录"""
        try:
            self.cur.execute("""
                INSERT INTO transactions
                (transaction_id, account_number, transaction_type, direction,
                 amount, currency, balance_after, transaction_date, transaction_time,
                 value_date, counterparty_account, counterparty_name, description,
                 channel, status, reference_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
            """, (
                txn_data['transaction_id'],
                txn_data['account_number'],
                txn_data['transaction_type'],
                txn_data['direction'],
                txn_data['amount'],
                txn_data['currency'],
                txn_data['balance_after'],
                txn_data['transaction_date'],
                txn_data.get('transaction_time'),
                txn_data.get('value_date'),
                txn_data.get('counterparty_account'),
                txn_data.get('counterparty_name'),
                txn_data.get('description'),
                txn_data.get('channel'),
                txn_data.get('status', 'COMPLETED'),
                txn_data.get('reference_number')
            ))
            self.conn.commit()
            logger.info(f"Stored transaction: {txn_data['transaction_id']}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store transaction: {e}")
            raise
```

### 5.2 银行业务分析查询

**分析查询示例**：

```python
class BankingAnalytics:
    """银行业务分析查询"""

    def __init__(self, storage: BankingDataStorage):
        self.storage = storage

    def get_account_balance_summary(self, customer_id: str) -> Dict:
        """获取客户账户余额汇总"""
        self.storage.cur.execute("""
            SELECT
                currency,
                COUNT(*) as account_count,
                SUM(balance) as total_balance,
                SUM(available_balance) as total_available,
                SUM(frozen_amount) as total_frozen
            FROM accounts
            WHERE customer_id = %s AND status = 'ACTIVE'
            GROUP BY currency
        """, (customer_id,))

        results = self.storage.cur.fetchall()
        return {
            row[0]: {
                'account_count': row[1],
                'total_balance': float(row[2]),
                'total_available': float(row[3]),
                'total_frozen': float(row[4])
            }
            for row in results
        }

    def get_transaction_summary(self, account_number: str,
                                start_date: datetime, end_date: datetime) -> Dict:
        """获取账户交易汇总"""
        self.storage.cur.execute("""
            SELECT
                transaction_type,
                direction,
                COUNT(*) as txn_count,
                SUM(amount) as total_amount
            FROM transactions
            WHERE account_number = %s
            AND transaction_date BETWEEN %s AND %s
            AND status = 'COMPLETED'
            GROUP BY transaction_type, direction
        """, (account_number, start_date, end_date))

        results = self.storage.cur.fetchall()
        summary = {}
        for row in results:
            txn_type = row[0]
            direction = row[1]
            if txn_type not in summary:
                summary[txn_type] = {}
            summary[txn_type][direction] = {
                'count': row[2],
                'total_amount': float(row[3])
            }
        return summary

    def get_loan_portfolio_summary(self) -> Dict:
        """获取贷款组合汇总"""
        self.storage.cur.execute("""
            SELECT
                status,
                COUNT(*) as loan_count,
                SUM(contract_amount) as total_contract_amount,
                SUM(outstanding_principal) as total_outstanding,
                SUM(outstanding_interest) as total_interest,
                AVG(interest_rate) as avg_interest_rate
            FROM loan_contracts
            GROUP BY status
        """)

        results = self.storage.cur.fetchall()
        return {
            row[0]: {
                'loan_count': row[1],
                'total_contract_amount': float(row[2]),
                'total_outstanding': float(row[3]),
                'total_interest': float(row[4]),
                'avg_interest_rate': float(row[5]) if row[5] else 0
            }
            for row in results
        }

    def get_daily_payment_volume(self, date: datetime) -> Dict:
        """获取日支付量统计"""
        self.storage.cur.execute("""
            SELECT
                clearing_system,
                currency,
                COUNT(*) as payment_count,
                SUM(amount) as total_amount
            FROM payment_instructions
            WHERE DATE(created_at) = %s
            AND status = 'SETTLED'
            GROUP BY clearing_system, currency
        """, (date,))

        results = self.storage.cur.fetchall()
        summary = {}
        for row in results:
            system = row[0] or 'UNKNOWN'
            currency = row[1]
            if system not in summary:
                summary[system] = {}
            summary[system][currency] = {
                'payment_count': row[2],
                'total_amount': float(row[3])
            }
        return summary
```

---

## 6. 转换验证与测试

### 6.1 数据一致性验证

```python
class DataConsistencyValidator:
    """数据一致性验证器"""

    def validate_account_balance(self, account_number: str) -> ValidationResult:
        """验证账户余额一致性"""
        result = ValidationResult()

        # 查询账户信息
        self.cur.execute("""
            SELECT balance, available_balance, frozen_amount
            FROM accounts
            WHERE account_number = %s
        """, (account_number,))

        row = self.cur.fetchone()
        if not row:
            result.add_error(f"Account {account_number} not found")
            return result

        balance, available, frozen = row

        # 验证公式：balance = available + frozen
        if abs(balance - (available + frozen)) > Decimal('0.01'):
            result.add_error(
                f"Balance inconsistency: balance={balance}, "
                f"available={available}, frozen={frozen}"
            )

        return result

    def validate_transaction_consistency(self, account_number: str,
                                         date: datetime) -> ValidationResult:
        """验证交易记录一致性"""
        result = ValidationResult()

        # 获取期初余额
        self.cur.execute("""
            SELECT balance_after
            FROM transactions
            WHERE account_number = %s AND transaction_date < %s
            ORDER BY transaction_date DESC, transaction_time DESC
            LIMIT 1
        """, (account_number, date))

        row = self.cur.fetchone()
        opening_balance = row[0] if row else Decimal('0')

        # 获取当日所有交易
        self.cur.execute("""
            SELECT direction, amount, balance_after
            FROM transactions
            WHERE account_number = %s AND transaction_date = %s
            ORDER BY transaction_time
        """, (account_number, date))

        transactions = self.cur.fetchall()

        # 验证余额连续性
        expected_balance = opening_balance
        for i, (direction, amount, actual_balance) in enumerate(transactions):
            if direction == 'DEBIT':
                expected_balance -= amount
            else:
                expected_balance += amount

            if abs(expected_balance - actual_balance) > Decimal('0.01'):
                result.add_error(
                    f"Transaction {i+1} balance mismatch: "
                    f"expected={expected_balance}, actual={actual_balance}"
                )

        return result
```

### 6.2 业务规则验证

```python
class BusinessRuleValidator:
    """业务规则验证器"""

    def validate_payment_instruction(self, payment: PaymentInstruction) -> ValidationResult:
        """验证支付指令"""
        result = ValidationResult()

        # 验证金额大于0
        if payment.amount.value <= 0:
            result.add_error("Payment amount must be greater than 0")

        # 验证币种代码
        if len(payment.amount.currency) != 3:
            result.add_error("Currency code must be 3 characters")

        # 验证执行日期
        if payment.requested_execution_date < datetime.now().date():
            result.add_error("Execution date cannot be in the past")

        # 验证付款方和收款方不能相同
        if (payment.debtor.account.identification ==
            payment.creditor.account.identification):
            result.add_error("Debtor and creditor cannot be the same")

        return result

    def validate_loan_contract(self, contract: LoanContract) -> ValidationResult:
        """验证贷款合同"""
        result = ValidationResult()

        # 验证期限
        if contract.term_months < 1 or contract.term_months > 360:
            result.add_error("Loan term must be between 1 and 360 months")

        # 验证利率
        if contract.interest_rate < 0 or contract.interest_rate > 1:
            result.add_error("Interest rate must be between 0% and 100%")

        # 验证金额
        if contract.contract_amount <= 0:
            result.add_error("Contract amount must be greater than 0")

        # 验证未偿本金不大于合同金额
        if contract.outstanding_principal > contract.contract_amount:
            result.add_error("Outstanding principal cannot exceed contract amount")

        return result
```

### 6.3 性能测试

```python
import time
from concurrent.futures import ThreadPoolExecutor

class PerformanceTester:
    """性能测试工具"""

    def __init__(self, transformer):
        self.transformer = transformer

    def test_transformation_throughput(self,
                                       sample_data: List[Dict],
                                       batch_size: int = 1000) -> Dict:
        """测试转换吞吐量"""

        results = {
            'total_records': len(sample_data),
            'batch_size': batch_size,
            'batches': []
        }

        # 分批处理
        for i in range(0, len(sample_data), batch_size):
            batch = sample_data[i:i+batch_size]

            start_time = time.time()

            # 执行转换
            for record in batch:
                self.transformer.transform(record)

            end_time = time.time()

            batch_time = end_time - start_time
            throughput = len(batch) / batch_time

            results['batches'].append({
                'batch_number': i // batch_size + 1,
                'record_count': len(batch),
                'time_seconds': batch_time,
                'throughput_per_second': throughput
            })

        # 计算总体统计
        total_time = sum(b['time_seconds'] for b in results['batches'])
        results['total_time_seconds'] = total_time
        results['average_throughput'] = len(sample_data) / total_time

        return results

    def test_concurrent_transformation(self,
                                       sample_data: List[Dict],
                                       num_workers: int = 10) -> Dict:
        """测试并发转换性能"""

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(self.transformer.transform, record)
                for record in sample_data
            ]

            # 等待所有任务完成
            completed = 0
            errors = 0
            for future in futures:
                try:
                    future.result()
                    completed += 1
                except Exception as e:
                    errors += 1

        end_time = time.time()

        total_time = end_time - start_time

        return {
            'total_records': len(sample_data),
            'workers': num_workers,
            'completed': completed,
            'errors': errors,
            'total_time_seconds': total_time,
            'throughput_per_second': len(sample_data) / total_time
        }
```

---

## 7. 转换工具与平台

### 7.1 ETL工具

**Apache NiFi银行数据处理流程**：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Apache NiFi 数据流                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ GetFile  │───►│ SplitText│───►│ Transform│───►│ PutSQL   │  │
│  │ (源数据)  │    │ (解析)   │    │ (转换)   │    │ (存储)   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                      │                          │
│                                      ▼                          │
│                               ┌──────────┐                      │
│                               │ Validate │                      │
│                               │ (验证)   │                      │
│                               └────┬─────┘                      │
│                                    │                            │
│              ┌─────────────────────┼─────────────────────┐      │
│              │                     │                     │      │
│              ▼                     ▼                     ▼      │
│        ┌──────────┐         ┌──────────┐         ┌──────────┐  │
│        │ RouteOn  │         │ Update   │         │ PutFile  │  │
│        │ Attribute│         │ Attribute│         │ (错误)   │  │
│        │ (成功)   │         │ (重试)   │         │          │  │
│        └──────────┘         └──────────┘         └──────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 消息转换平台

**消息转换架构**：

```python
class MessageTransformationPlatform:
    """消息转换平台"""

    def __init__(self):
        self.transformers = {}
        self.validators = {}

    def register_transformer(self, source_format: str,
                            target_format: str,
                            transformer: Callable):
        """注册转换器"""
        key = f"{source_format}_to_{target_format}"
        self.transformers[key] = transformer

    def transform(self, message: Any,
                  source_format: str,
                  target_format: str) -> Any:
        """执行消息转换"""
        key = f"{source_format}_to_{target_format}"

        if key not in self.transformers:
            raise ValueError(f"No transformer registered for {key}")

        transformer = self.transformers[key]
        return transformer(message)

    def transform_with_validation(self, message: Any,
                                   source_format: str,
                                   target_format: str) -> Tuple[Any, ValidationResult]:
        """执行转换并验证"""
        # 转换
        result = self.transform(message, source_format, target_format)

        # 验证
        validation_result = ValidationResult()
        validator_key = f"{target_format}_validator"
        if validator_key in self.validators:
            validation_result = self.validators[validator_key](result)

        return result, validation_result
```

### 7.3 API网关

**银行API网关架构**：

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      接入层                               │  │
│  │   SSL/TLS   Load Balancer   Rate Limit   Authentication  │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │                      路由层                               │  │
│  │   /accounts/*   /payments/*   /loans/*   /cards/*        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │                    转换层                                 │  │
│  │   Request Transform   Response Transform   Protocol      │  │
│  │   JSON↔XML    REST↔SOAP    ISO20022↔Internal             │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │                    服务层                                 │  │
│  │   Core Banking   Payment System   Loan System   Card     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标

**创建时间**：2025-01-21
**最后更新**：2025-01-21
