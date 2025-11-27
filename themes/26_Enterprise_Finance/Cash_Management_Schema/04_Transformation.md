# 资金管理Schema转换体系

## 📑 目录

- [资金管理Schema转换体系](#资金管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 资金管理到总账转换](#2-资金管理到总账转换)
  - [3. 资金管理到现金流量表转换](#3-资金管理到现金流量表转换)
  - [4. 资金管理到ISO 20022转换](#4-资金管理到iso-20022转换)
  - [5. 资金管理数据存储与分析](#5-资金管理数据存储与分析)
    - [5.1 PostgreSQL资金管理数据存储](#51-postgresql资金管理数据存储)
    - [5.2 资金管理数据分析查询](#52-资金管理数据分析查询)

---

## 1. 转换体系概述

资金管理Schema转换体系支持资金管理数据到总账、现金流量表、ISO 20022格式转换，以及资金管理数据存储。

### 1.1 转换目标

1. **资金管理到总账转换**：资金管理数据到总账格式
2. **资金管理到现金流量表转换**：资金管理数据到现金流量表格式
3. **资金管理到ISO 20022转换**：资金管理数据到ISO 20022格式
4. **资金管理到数据库转换**：资金管理数据到PostgreSQL存储

---

## 2. 资金管理到总账转换

**转换规则**：

- 账户交易 → 总账凭证（借/贷：银行存款）
- 资金调拨 → 总账凭证（借：银行存款-调入，贷：银行存款-调出）
- 资金计划 → 总账预算科目

**转换示例**：

```python
def convert_cash_to_gl(cash_data: CashManagementSchema) -> GeneralLedgerEntry:
    """将资金管理数据转换为总账凭证"""
    gl_entry = GeneralLedgerEntry()

    # 转换账户交易
    for transaction in cash_data.account_transactions:
        if transaction.status == "Completed":
            gl_line = GLLine()
            gl_line.entry_date = transaction.transaction_date
            gl_line.account_code = "1002"  # 银行存款

            if transaction.transaction_type in ["Deposit", "Transfer_In", "Interest"]:
                gl_line.debit_amount = transaction.transaction_amount
            elif transaction.transaction_type in ["Withdrawal", "Transfer_Out", "Fee"]:
                gl_line.credit_amount = transaction.transaction_amount

            gl_entry.lines.append(gl_line)

    # 转换资金调拨
    for transfer in cash_data.cash_transfers:
        if transfer.status == "Completed":
            # 调出账户
            gl_line_out = GLLine()
            gl_line_out.account_code = f"1002-{transfer.from_account_id}"
            gl_line_out.credit_amount = transfer.transfer_amount
            gl_entry.lines.append(gl_line_out)

            # 调入账户
            gl_line_in = GLLine()
            gl_line_in.account_code = f"1002-{transfer.to_account_id}"
            gl_line_in.debit_amount = transfer.transfer_amount
            gl_entry.lines.append(gl_line_in)

    return gl_entry
```

---

## 3. 资金管理到现金流量表转换

**转换规则**：

- 经营活动交易 → 经营活动现金流量
- 投资活动交易 → 投资活动现金流量
- 筹资活动交易 → 筹资活动现金流量

**转换示例**：

```python
def convert_cash_to_cfs(cash_data: CashManagementSchema) -> CashFlowStatement:
    """将资金管理数据转换为现金流量表"""
    cfs = CashFlowStatement()

    # 转换经营活动现金流量
    operating_inflows = 0
    operating_outflows = 0

    for transaction in cash_data.account_transactions:
        if transaction.transaction_type == "Operating":
            if transaction.transaction_amount > 0:
                operating_inflows += transaction.transaction_amount
            else:
                operating_outflows += abs(transaction.transaction_amount)

    cfs.operating_activities = {
        "cash_inflows": operating_inflows,
        "cash_outflows": operating_outflows,
        "net_cash_flow": operating_inflows - operating_outflows
    }

    # 转换投资活动现金流量
    investing_inflows = 0
    investing_outflows = 0

    for transaction in cash_data.account_transactions:
        if transaction.transaction_type == "Investing":
            if transaction.transaction_amount > 0:
                investing_inflows += transaction.transaction_amount
            else:
                investing_outflows += abs(transaction.transaction_amount)

    cfs.investing_activities = {
        "cash_inflows": investing_inflows,
        "cash_outflows": investing_outflows,
        "net_cash_flow": investing_inflows - investing_outflows
    }

    # 转换筹资活动现金流量
    financing_inflows = 0
    financing_outflows = 0

    for transaction in cash_data.account_transactions:
        if transaction.transaction_type == "Financing":
            if transaction.transaction_amount > 0:
                financing_inflows += transaction.transaction_amount
            else:
                financing_outflows += abs(transaction.transaction_amount)

    cfs.financing_activities = {
        "cash_inflows": financing_inflows,
        "cash_outflows": financing_outflows,
        "net_cash_flow": financing_inflows - financing_outflows
    }

    cfs.net_cash_flow = (cfs.operating_activities["net_cash_flow"] +
                         cfs.investing_activities["net_cash_flow"] +
                         cfs.financing_activities["net_cash_flow"])

    return cfs
```

---

## 4. 资金管理到ISO 20022转换

**转换规则**：

- 账户余额 → ISO 20022 camt.053 Balance
- 账户交易 → ISO 20022 camt.053 Entry
- 资金调拨 → ISO 20022 pacs.008 Credit Transfer

**转换示例**：

```python
def convert_cash_to_iso20022(cash_data: CashManagementSchema) -> ISO20022Message:
    """将资金管理数据转换为ISO 20022格式"""
    iso_message = ISO20022Message()

    # 转换为camt.053银行对账单
    camt053 = Camt053()

    for account in cash_data.bank_accounts:
        statement = AccountStatement()
        statement.account = CashAccount20(
            identification=account.account_number,
            name=account.account_name,
            currency=account.currency
        )

        # 转换账户余额
        for balance in cash_data.account_balances:
            if balance.account_id == account.account_id:
                cash_balance = CashBalance()
                cash_balance.type = BalanceType12Choice(code="CLSG")
                cash_balance.amount = AmountAndCurrencyExchangeDetails3(
                    amount=ActiveOrHistoricCurrencyAndAmount(
                        currency=account.currency,
                        value=balance.closing_balance
                    )
                )
                cash_balance.credit_debit_indicator = "CRDT" if balance.closing_balance >= 0 else "DBIT"
                statement.balance.append(cash_balance)

        # 转换账户交易
        for transaction in cash_data.account_transactions:
            if transaction.account_id == account.account_id:
                entry = ReportEntry()
                entry.entry_reference = transaction.transaction_id
                entry.amount = AmountAndCurrencyExchangeDetails3(
                    amount=ActiveOrHistoricCurrencyAndAmount(
                        currency=account.currency,
                        value=abs(transaction.transaction_amount)
                    )
                )
                entry.credit_debit_indicator = "CRDT" if transaction.transaction_amount > 0 else "DBIT"
                entry.status = "BOOK"
                entry.booking_date = DateAndDateTimeChoice(date=transaction.transaction_date)
                entry.value_date = DateAndDateTimeChoice(date=transaction.transaction_date)
                statement.entry.append(entry)

        camt053.statement.append(statement)

    iso_message.camt053 = camt053

    # 转换为pacs.008资金划转
    for transfer in cash_data.cash_transfers:
        if transfer.transfer_type == "External":
            pacs008 = Pacs008()
            pacs008.group_header = GroupHeader33(
                message_identification=transfer.transfer_id,
                creation_date_time=transfer.transfer_date
            )

            credit_transfer = CreditTransferTransactionInformation11()
            credit_transfer.payment_identification = PaymentIdentification3(
                instruction_id=transfer.transfer_number,
                end_to_end_identification=transfer.transfer_id
            )
            credit_transfer.amount = AmountType3Choice(
                instructed_amount=ActiveOrHistoricCurrencyAndAmount(
                    currency=transfer.currency,
                    value=transfer.transfer_amount
                )
            )
            credit_transfer.creditor_account = CashAccount16(
                identification=AccountIdentification4Choice(
                    iban=transfer.to_account_id
                )
            )

            pacs008.credit_transfer_transaction_information.append(credit_transfer)
            iso_message.pacs008.append(pacs008)

    return iso_message
```

---

## 5. 资金管理数据存储与分析

### 5.1 PostgreSQL资金管理数据存储

**表结构设计**：

```sql
-- 银行账户表
CREATE TABLE bank_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    bank_name VARCHAR(200) NOT NULL,
    bank_code VARCHAR(50) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    is_active BOOLEAN DEFAULT TRUE,
    opening_date DATE NOT NULL,
    closing_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 账户余额表
CREATE TABLE account_balances (
    balance_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    balance_date DATE NOT NULL,
    opening_balance DECIMAL(18, 2) DEFAULT 0,
    debit_amount DECIMAL(18, 2) DEFAULT 0,
    credit_amount DECIMAL(18, 2) DEFAULT 0,
    closing_balance DECIMAL(18, 2) NOT NULL,
    available_balance DECIMAL(18, 2) NOT NULL,
    frozen_amount DECIMAL(18, 2) DEFAULT 0,
    FOREIGN KEY (account_id) REFERENCES bank_accounts(account_id)
);

-- 账户交易表
CREATE TABLE account_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    transaction_amount DECIMAL(18, 2) NOT NULL,
    balance_after DECIMAL(18, 2) NOT NULL,
    counterparty VARCHAR(200),
    reference_number VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES bank_accounts(account_id)
);

-- 资金调拨表
CREATE TABLE cash_transfers (
    transfer_id VARCHAR(50) PRIMARY KEY,
    transfer_number VARCHAR(50) UNIQUE NOT NULL,
    transfer_date DATE NOT NULL,
    from_account_id VARCHAR(50) NOT NULL,
    to_account_id VARCHAR(50) NOT NULL,
    transfer_amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10, 6) DEFAULT 1.0,
    transfer_type VARCHAR(20) NOT NULL,
    transfer_purpose TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    confirmation_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_account_id) REFERENCES bank_accounts(account_id),
    FOREIGN KEY (to_account_id) REFERENCES bank_accounts(account_id)
);

-- 创建索引
CREATE INDEX idx_account_balances_account ON account_balances(account_id);
CREATE INDEX idx_account_balances_date ON account_balances(balance_date);
CREATE INDEX idx_account_transactions_account ON account_transactions(account_id);
CREATE INDEX idx_account_transactions_date ON account_transactions(transaction_date);
CREATE INDEX idx_cash_transfers_from_account ON cash_transfers(from_account_id);
CREATE INDEX idx_cash_transfers_to_account ON cash_transfers(to_account_id);
```

### 5.2 资金管理数据分析查询

**查询示例**：

```python
def analyze_cash_data(conn, period_start, period_end):
    """分析资金管理数据"""
    cursor = conn.cursor()

    # 查询账户余额汇总
    cursor.execute("""
        SELECT
            ba.account_name,
            ba.account_number,
            ab.balance_date,
            ab.opening_balance,
            ab.closing_balance,
            ab.available_balance,
            ab.frozen_amount
        FROM account_balances ab
        JOIN bank_accounts ba ON ab.account_id = ba.account_id
        WHERE ab.balance_date BETWEEN %s AND %s
        ORDER BY ba.account_name, ab.balance_date
    """, (period_start, period_end))

    balance_summary = cursor.fetchall()

    # 查询资金调拨汇总
    cursor.execute("""
        SELECT
            ct.transfer_date,
            ba_from.account_name as from_account,
            ba_to.account_name as to_account,
            ct.transfer_amount,
            ct.transfer_type,
            ct.status
        FROM cash_transfers ct
        JOIN bank_accounts ba_from ON ct.from_account_id = ba_from.account_id
        JOIN bank_accounts ba_to ON ct.to_account_id = ba_to.account_id
        WHERE ct.transfer_date BETWEEN %s AND %s
        ORDER BY ct.transfer_date
    """, (period_start, period_end))

    transfer_summary = cursor.fetchall()

    # 查询资金流量分析
    cursor.execute("""
        SELECT
            at.transaction_type,
            SUM(CASE WHEN at.transaction_amount > 0 THEN at.transaction_amount ELSE 0 END) as total_inflow,
            SUM(CASE WHEN at.transaction_amount < 0 THEN ABS(at.transaction_amount) ELSE 0 END) as total_outflow,
            COUNT(*) as transaction_count
        FROM account_transactions at
        WHERE at.transaction_date BETWEEN %s AND %s
        AND at.status = 'Completed'
        GROUP BY at.transaction_type
        ORDER BY total_inflow DESC
    """, (period_start, period_end))

    cash_flow_analysis = cursor.fetchall()

    return {
        "balance_summary": balance_summary,
        "transfer_summary": transfer_summary,
        "cash_flow_analysis": cash_flow_analysis
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
