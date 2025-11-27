# 资金管理Schema实践案例

## 📑 目录

- [资金管理Schema实践案例](#资金管理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：银行账户管理](#2-案例1银行账户管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：资金计划管理](#3-案例2资金计划管理)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：资金调拨系统](#4-案例3资金调拨系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：资金预测分析](#5-案例4资金预测分析)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：资金管理数据存储与分析系统](#6-案例5资金管理数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供资金管理Schema在实际应用中的实践案例。

---

## 2. 案例1：银行账户管理

### 2.1 场景描述

**应用场景**：
企业银行账户管理，包括账户信息管理、账户余额监控、账户交易记录、银行对账。

**业务需求**：

- 支持多银行账户管理
- 支持账户余额实时监控
- 支持账户交易记录和查询
- 支持银行对账

### 2.2 Schema定义

**银行账户管理Schema**：

```dsl
schema BankAccountManagement {
  bank_account: BankAccount {
    account_id: String @value("ACC-20250001")
    account_number: String @value("6222021234567890123")
    account_name: String @value("公司基本账户")
    bank_name: String @value("中国工商银行")
    bank_code: String @value("ICBC")
    account_type: Enum @value("Current")
    currency: String @value("CNY")
    is_active: Boolean @value(true)
  }

  account_balance: AccountBalance {
    balance_id: String @value("BAL-20250001")
    account_id: String @value("ACC-20250001")
    balance_date: Date @value("2025-01-21")
    opening_balance: Decimal @value(1000000.00)
    debit_amount: Decimal @value(50000.00)
    credit_amount: Decimal @value(200000.00)
    closing_balance: Decimal @value(1150000.00)
    available_balance: Decimal @value(1150000.00)
    frozen_amount: Decimal @value(0.00)
  }
}
```

---

## 3. 案例2：资金计划管理

### 3.1 场景描述

**应用场景**：
企业资金计划管理，包括资金计划编制、资金预算管理、资金执行监控。

**业务需求**：

- 支持年度、季度、月度资金计划
- 支持资金预算编制和执行
- 支持资金执行监控和分析

### 3.2 Schema定义

**资金计划管理Schema**：

```dsl
schema CashPlanningManagement {
  cash_plan: CashPlan {
    plan_id: String @value("PLAN-20250001")
    plan_name: String @value("2025年度资金计划")
    plan_type: Enum @value("Annual")
    plan_period_start: Date @value("2025-01-01")
    plan_period_end: Date @value("2025-12-31")
    plan_amount: Decimal @value(50000000.00)
    plan_category: Enum @value("Operating")
    status: Enum @value("Approved")
  }

  cash_budget: CashBudget {
    budget_id: String @value("BUDGET-20250001")
    plan_id: String @value("PLAN-20250001")
    budget_period: Date @value("2025-01")
    budget_category: String @value("Operating")
    budget_item: String @value("工资支出")
    budget_amount: Decimal @value(5000000.00)
    actual_amount: Decimal @value(4800000.00)
    variance: Decimal @value(-200000.00)
  }
}
```

---

## 4. 案例3：资金调拨系统

### 4.1 场景描述

**应用场景**：
资金调拨系统，支持企业内部账户间资金调拨、跨银行资金划转、资金归集。

**业务需求**：

- 支持资金调拨申请和审批
- 支持资金调拨执行和跟踪
- 支持资金调拨对账

### 4.2 实现代码

```python
def process_cash_transfer(transfer: CashTransfer, cash_data: CashManagementSchema):
    """处理资金调拨"""
    # 检查调出账户余额
    from_account = next(acc for acc in cash_data.bank_accounts
                       if acc.account_id == transfer.from_account_id)
    from_balance = next(bal for bal in cash_data.account_balances
                       if bal.account_id == transfer.from_account_id
                       and bal.balance_date == transfer.transfer_date)

    if from_balance.available_balance < transfer.transfer_amount:
        raise ValueError("调出账户余额不足")

    # 创建调出交易
    debit_transaction = AccountTransaction()
    debit_transaction.account_id = transfer.from_account_id
    debit_transaction.transaction_date = transfer.transfer_date
    debit_transaction.transaction_type = "Transfer_Out"
    debit_transaction.transaction_amount = -transfer.transfer_amount
    debit_transaction.balance_after = from_balance.available_balance - transfer.transfer_amount
    debit_transaction.status = "Completed"
    cash_data.account_transactions.append(debit_transaction)

    # 创建调入交易
    credit_transaction = AccountTransaction()
    credit_transaction.account_id = transfer.to_account_id
    credit_transaction.transaction_date = transfer.transfer_date
    credit_transaction.transaction_type = "Transfer_In"
    credit_transaction.transaction_amount = transfer.transfer_amount
    to_balance = next(bal for bal in cash_data.account_balances
                     if bal.account_id == transfer.to_account_id
                     and bal.balance_date == transfer.transfer_date)
    credit_transaction.balance_after = to_balance.available_balance + transfer.transfer_amount
    credit_transaction.status = "Completed"
    cash_data.account_transactions.append(credit_transaction)

    # 更新调拨状态
    transfer.status = "Completed"
    transfer.confirmation_number = f"TRF-{transfer.transfer_id}"

    return transfer
```

---

## 5. 案例4：资金预测分析

### 5.1 场景描述

**应用场景**：
资金预测分析，基于历史数据预测未来资金需求，支持短期、中期、长期预测。

**业务需求**：

- 支持资金预测模型
- 支持预测准确度评估
- 支持资金预警

### 5.2 实现代码

```python
def forecast_cash_flow(historical_data: List[CashFlowData], forecast_period: Date) -> CashFlowForecast:
    """预测现金流"""
    # 使用历史数据计算平均现金流
    avg_inflow = sum([d.cash_inflow for d in historical_data]) / len(historical_data)
    avg_outflow = sum([d.cash_outflow for d in historical_data]) / len(historical_data)

    # 计算趋势
    if len(historical_data) >= 2:
        recent_trend = (historical_data[-1].net_cash_flow - historical_data[0].net_cash_flow) / len(historical_data)
    else:
        recent_trend = 0

    # 生成预测
    forecast = CashFlowForecast()
    forecast.forecast_date = forecast_period
    forecast.cash_inflows.operating_inflows = avg_inflow * 1.05  # 假设5%增长
    forecast.cash_outflows.operating_outflows = avg_outflow * 1.03  # 假设3%增长
    forecast.net_cash_flow = forecast.cash_inflows.total_inflows - forecast.cash_outflows.total_outflows

    # 计算预测准确度（如果有实际数据）
    if has_actual_data:
        actual_net_flow = actual_data.net_cash_flow
        forecast.forecast_accuracy = 1 - abs(forecast.net_cash_flow - actual_net_flow) / abs(actual_net_flow)

    return forecast

def check_cash_alerts(cash_data: CashManagementSchema) -> List[CashAlert]:
    """检查资金预警"""
    alerts = []

    for account in cash_data.bank_accounts:
        balance = next((bal for bal in cash_data.account_balances
                       if bal.account_id == account.account_id), None)

        if balance:
            # 低余额预警
            if balance.available_balance < 100000:  # 假设阈值10万
                alert = CashAlert()
                alert.alert_type = "Low_Balance"
                alert.account_id = account.account_id
                alert.threshold = 100000
                alert.current_value = balance.available_balance
                alert.alert_level = "Warning" if balance.available_balance < 50000 else "Critical"
                alert.alert_message = f"账户 {account.account_name} 余额低于阈值"
                alerts.append(alert)

            # 大额交易预警
            recent_transactions = [t for t in cash_data.account_transactions
                                 if t.account_id == account.account_id
                                 and t.transaction_date >= (datetime.now() - timedelta(days=1)).date()]

            for transaction in recent_transactions:
                if abs(transaction.transaction_amount) > 1000000:  # 假设阈值100万
                    alert = CashAlert()
                    alert.alert_type = "Large_Transaction"
                    alert.account_id = account.account_id
                    alert.threshold = 1000000
                    alert.current_value = abs(transaction.transaction_amount)
                    alert.alert_level = "Warning"
                    alert.alert_message = f"账户 {account.account_name} 发生大额交易"
                    alerts.append(alert)

    return alerts
```

---

## 6. 案例5：资金管理数据存储与分析系统

### 6.1 场景描述

**应用场景**：
资金管理数据存储与分析系统，支持数据存储、查询、分析、报表生成。

**业务需求**：

- 支持资金管理数据存储
- 支持数据查询和分析
- 支持报表生成

### 6.2 实现代码

```python
def store_cash_data(cash_data: CashManagementSchema, conn):
    """存储资金管理数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储银行账户
    for account in cash_data.bank_accounts:
        cursor.execute("""
            INSERT INTO bank_accounts
            (account_id, account_number, account_name, bank_name, bank_code,
             account_type, currency, is_active, opening_date, closing_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (account_id) DO UPDATE SET
            account_name = EXCLUDED.account_name,
            is_active = EXCLUDED.is_active,
            updated_at = CURRENT_TIMESTAMP
        """, (account.account_id, account.account_number, account.account_name,
              account.bank_name, account.bank_code, account.account_type,
              account.currency, account.is_active, account.opening_date, account.closing_date))

    # 存储账户余额
    for balance in cash_data.account_balances:
        cursor.execute("""
            INSERT INTO account_balances
            (balance_id, account_id, balance_date, opening_balance, debit_amount,
             credit_amount, closing_balance, available_balance, frozen_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (balance_id) DO UPDATE SET
            opening_balance = EXCLUDED.opening_balance,
            debit_amount = EXCLUDED.debit_amount,
            credit_amount = EXCLUDED.credit_amount,
            closing_balance = EXCLUDED.closing_balance,
            available_balance = EXCLUDED.available_balance,
            frozen_amount = EXCLUDED.frozen_amount
        """, (balance.balance_id, balance.account_id, balance.balance_date,
              balance.opening_balance, balance.debit_amount, balance.credit_amount,
              balance.closing_balance, balance.available_balance, balance.frozen_amount))

    # 存储账户交易
    for transaction in cash_data.account_transactions:
        cursor.execute("""
            INSERT INTO account_transactions
            (transaction_id, account_id, transaction_date, transaction_type,
             transaction_amount, balance_after, counterparty, reference_number,
             description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO UPDATE SET
            transaction_amount = EXCLUDED.transaction_amount,
            balance_after = EXCLUDED.balance_after,
            status = EXCLUDED.status
        """, (transaction.transaction_id, transaction.account_id, transaction.transaction_date,
              transaction.transaction_type, transaction.transaction_amount, transaction.balance_after,
              transaction.counterparty, transaction.reference_number, transaction.description,
              transaction.status))

    conn.commit()

def generate_cash_report(conn, period_start, period_end):
    """生成资金管理报表"""
    cursor = conn.cursor()

    # 账户余额汇总
    cursor.execute("""
        SELECT
            ba.account_name,
            ba.account_number,
            ab.balance_date,
            ab.opening_balance,
            ab.closing_balance,
            ab.available_balance
        FROM account_balances ab
        JOIN bank_accounts ba ON ab.account_id = ba.account_id
        WHERE ab.balance_date BETWEEN %s AND %s
        ORDER BY ba.account_name, ab.balance_date
    """, (period_start, period_end))

    balance_report = cursor.fetchall()

    # 资金流量分析
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

    cash_flow_report = cursor.fetchall()

    return {
        "balance_report": balance_report,
        "cash_flow_report": cash_flow_report
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
