# SWIFT Schema转换体系

## 📑 目录

- [SWIFT Schema转换体系](#swift-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. MT到MX转换](#2-mt到mx转换)
  - [3. MX到MT转换](#3-mx到mt转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. SWIFT数据存储与分析](#6-swift数据存储与分析)
    - [6.1 PostgreSQL SWIFT数据存储](#61-postgresql-swift数据存储)
    - [6.2 SWIFT数据分析查询](#62-swift数据分析查询)

---

## 1. 转换体系概述

SWIFT Schema转换体系支持MT消息、MX消息、
数据库存储之间的转换。

### 1.1 转换目标

1. **MT到MX转换**：传统MT消息到ISO 20022 MX消息
2. **MX到MT转换**：MX消息到MT消息（兼容性）
3. **消息到数据库转换**：SWIFT消息到PostgreSQL存储

---

## 2. MT到MX转换

**转换规则**：

- MT103 → pacs.008.001.08
- MT202 → pacs.009.001.08
- MT940 → camt.053.001.08

**转换示例**：

```python
def convert_mt103_to_mx(mt103: MT103) -> pacs008:
    """将MT103转换为pacs.008 MX消息"""
    mx = pacs008()

    # 转换基本信息
    mx.group_header.message_identification = generate_uuid()
    mx.group_header.creation_date_time = datetime.now()

    # 转换支付信息
    mx.payment_information.payment_information_identification = mt103.field_20
    mx.payment_information.payment_method = "TRF"
    mx.payment_information.requested_execution_date = parse_date(mt103.field_32A.date)

    # 转换付款人信息
    mx.payment_information.debtor.name = extract_name(mt103.field_50A)
    mx.payment_information.debtor_account.identification = extract_account(mt103.field_50A)

    # 转换收款人信息
    credit_transfer = CreditTransferTransaction()
    credit_transfer.payment_identification.end_to_end_identification = mt103.field_20
    credit_transfer.amount.currency = mt103.field_32A.currency
    credit_transfer.amount.value = mt103.field_32A.amount
    credit_transfer.creditor.name = extract_name(mt103.field_59)
    credit_transfer.creditor_account.identification = extract_account(mt103.field_59)

    mx.payment_information.credit_transfer_transaction_information.append(credit_transfer)

    return mx
```

---

## 3. MX到MT转换

**转换规则**：

- pacs.008.001.08 → MT103
- pacs.009.001.08 → MT202
- camt.053.001.08 → MT940

**转换示例**：

```python
def convert_mx_to_mt103(mx: pacs008) -> MT103:
    """将pacs.008 MX消息转换为MT103"""
    mt103 = MT103()

    # 转换基本信息
    mt103.field_20 = mx.payment_information.payment_information_identification
    mt103.field_23B = "CRED"

    # 转换金额和日期
    transaction = mx.payment_information.credit_transfer_transaction_information[0]
    mt103.field_32A = format_date_amount_currency(
        mx.payment_information.requested_execution_date,
        transaction.amount.value,
        transaction.amount.currency
    )

    # 转换付款人信息
    mt103.field_50A = format_party(mx.payment_information.debtor)

    # 转换收款人信息
    mt103.field_59 = format_party(transaction.creditor)

    # 转换费用承担方式
    mt103.field_71A = "SHA"  # 默认共享费用

    return mt103
```

---

## 4. 转换工具

- **SWIFT Alliance**：SWIFT官方转换工具
- **ISO 20022工具**：ISO 20022消息处理工具
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的消息完整性、金额一致性和参与方信息一致性。

---

## 6. SWIFT数据存储与分析

### 6.1 PostgreSQL SWIFT数据存储

**SWIFT数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class SWIFTStorage:
    """SWIFT数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建SWIFT数据表"""
        # MT消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mt_messages (
                id BIGSERIAL PRIMARY KEY,
                message_type VARCHAR(10) NOT NULL,
                message_reference VARCHAR(16) NOT NULL,
                sender_bic VARCHAR(11),
                receiver_bic VARCHAR(11),
                message_content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                processed_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'PENDING',
                UNIQUE(message_reference)
            )
        """)

        # MX消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mx_messages (
                id BIGSERIAL PRIMARY KEY,
                message_type VARCHAR(50) NOT NULL,
                message_identification VARCHAR(35) NOT NULL,
                creation_date_time TIMESTAMP NOT NULL,
                message_content JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_identification)
            )
        """)

        # BIC代码表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bic_codes (
                id SERIAL PRIMARY KEY,
                bic VARCHAR(11) UNIQUE NOT NULL,
                bank_name VARCHAR(200),
                country_code VARCHAR(2),
                location_code VARCHAR(2),
                branch_code VARCHAR(3),
                is_active BOOLEAN DEFAULT TRUE,
                registered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 交易记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id BIGSERIAL PRIMARY KEY,
                transaction_reference VARCHAR(35) NOT NULL,
                end_to_end_identification VARCHAR(35),
                message_type VARCHAR(10) NOT NULL,
                sender_bic VARCHAR(11),
                receiver_bic VARCHAR(11),
                amount DECIMAL(18,5),
                currency VARCHAR(3),
                debtor_name VARCHAR(140),
                debtor_account VARCHAR(34),
                creditor_name VARCHAR(140),
                creditor_account VARCHAR(34),
                execution_date DATE,
                status VARCHAR(20) DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 账户信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS account_statements (
                id BIGSERIAL PRIMARY KEY,
                account_identification VARCHAR(34) NOT NULL,
                statement_date DATE NOT NULL,
                opening_balance DECIMAL(18,5),
                closing_balance DECIMAL(18,5),
                currency VARCHAR(3),
                statement_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_identification, statement_date)
            )
        """)

        # SWIFT统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS swift_statistics (
                id SERIAL PRIMARY KEY,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                message_type VARCHAR(10),
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(statistic_type, time_window, message_type)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mt_messages_type_date
            ON mt_messages(message_type, created_at DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_reference
            ON transactions(transaction_reference)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_status
            ON transactions(status, created_at DESC)
        """)

        self.conn.commit()

    def store_mt_message(self, message_type: str, message_reference: str,
                        sender_bic: str, receiver_bic: str,
                        message_content: str, created_at: datetime):
        """存储MT消息"""
        self.cur.execute("""
            INSERT INTO mt_messages
            (message_type, message_reference, sender_bic, receiver_bic,
             message_content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_reference) DO NOTHING
        """, (message_type, message_reference, sender_bic, receiver_bic,
              message_content, created_at))
        self.conn.commit()

    def store_mx_message(self, message_type: str, message_identification: str,
                        creation_date_time: datetime, message_content: Dict):
        """存储MX消息"""
        self.cur.execute("""
            INSERT INTO mx_messages
            (message_type, message_identification, creation_date_time, message_content)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (message_identification) DO NOTHING
        """, (message_type, message_identification, creation_date_time,
              json.dumps(message_content)))
        self.conn.commit()

    def calculate_transaction_statistics(self, time_window: datetime):
        """计算交易统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount
            FROM transactions
            WHERE created_at >= %s
        """, (time_window,))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO swift_statistics
            (statistic_type, time_window, statistics)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (statistic_type, time_window, message_type)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, ("transaction", time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 SWIFT数据分析查询

**查询示例**：

```python
# 查询MT103消息
storage.cur.execute("""
    SELECT message_reference, sender_bic, receiver_bic, created_at
    FROM mt_messages
    WHERE message_type = 'MT103' AND created_at >= %s
    ORDER BY created_at DESC
""", (start_time,))

# 查询交易统计
storage.cur.execute("""
    SELECT currency, COUNT(*) as count, SUM(amount) as total
    FROM transactions
    WHERE status = 'COMPLETED' AND created_at >= %s
    GROUP BY currency
""", (start_time,))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
