# Payment Schema转换体系

## 📑 目录

- [Payment Schema转换体系](#payment-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Payment到ISO 20022转换](#2-payment到iso-20022转换)
  - [3. Payment到ISO 8583转换](#3-payment到iso-8583转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. Payment数据存储与分析](#6-payment数据存储与分析)
    - [6.1 PostgreSQL Payment数据存储](#61-postgresql-payment数据存储)
    - [6.2 Payment数据分析查询](#62-payment数据分析查询)

---

## 1. 转换体系概述

Payment Schema转换体系支持Payment消息
与ISO 20022、ISO 8583之间的转换，以及
Payment数据存储。

### 1.1 转换目标

1. **Payment到ISO 20022转换**：Payment消息到ISO 20022格式
2. **Payment到ISO 8583转换**：Payment消息到ISO 8583格式
3. **消息到数据库转换**：Payment消息到PostgreSQL存储

---

## 2. Payment到ISO 20022转换

**转换规则**：

- Payment请求 → pacs.008
- Payment响应 → pain.002
- Payment状态 → camt.054

**转换示例**：

```python
def convert_payment_to_iso20022(payment_request: PaymentRequest) -> Pacs008:
    """将Payment请求转换为pacs.008"""
    pacs008 = Pacs008()

    # 转换基本信息
    pacs008.group_header.message_identification = payment_request.request_id
    pacs008.group_header.creation_date_time = payment_request.timestamp

    # 转换支付信息
    pacs008.payment_information.payment_information_identification = payment_request.order_id
    pacs008.payment_information.payment_method = "TRF"
    pacs008.payment_information.requested_execution_date = payment_request.timestamp.date()

    # 转换付款人信息
    pacs008.payment_information.debtor.name = payment_request.customer_info.customer_name
    pacs008.payment_information.debtor_account.identification.iban = payment_request.customer_info.customer_id

    # 转换收款人信息
    transaction = CreditTransferTransactionInformation()
    transaction.payment_identification.end_to_end_identification = payment_request.order_id
    transaction.amount.instructed_amount.currency = payment_request.currency
    transaction.amount.instructed_amount.value = payment_request.amount
    transaction.creditor.name = payment_request.merchant_id

    pacs008.payment_information.credit_transfer_transaction_information.append(transaction)

    return pacs008
```

---

## 3. Payment到ISO 8583转换

**转换规则**：

- Payment请求 → ISO 8583授权消息
- Payment响应 → ISO 8583响应消息

**转换示例**：

```python
def convert_payment_to_iso8583(payment_request: PaymentRequest) -> ISO8583Message:
    """将Payment请求转换为ISO 8583消息"""
    iso8583 = ISO8583Message()

    # 消息类型：授权请求
    iso8583.message_type = "0100"

    # 处理代码
    iso8583.field_3 = "000000"

    # 交易金额
    iso8583.field_4 = str(int(payment_request.amount * 100))

    # 交易时间
    iso8583.field_7 = payment_request.timestamp.strftime("%m%d%H%M%S")

    # 系统跟踪号
    iso8583.field_11 = payment_request.request_id[-6:]

    # 商户信息
    iso8583.field_42 = payment_request.merchant_id

    # 卡号
    if payment_request.card_info:
        iso8583.field_2 = payment_request.card_info.card_number

    return iso8583
```

---

## 4. 转换工具

- **支付网关SDK**：各支付网关提供的SDK
- **ISO 20022工具**：ISO 20022消息转换工具
- **ISO 8583工具**：ISO 8583消息转换工具
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的消息完整性、格式正确性和业务逻辑一致性。

---

## 6. Payment数据存储与分析

### 6.1 PostgreSQL Payment数据存储

**Payment数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal

class PaymentStorage:
    """Payment数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建Payment数据表"""
        # 支付交易表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id BIGSERIAL PRIMARY KEY,
                request_id VARCHAR(50) UNIQUE NOT NULL,
                transaction_id VARCHAR(50) UNIQUE,
                merchant_id VARCHAR(50) NOT NULL,
                order_id VARCHAR(50) NOT NULL,
                amount NUMERIC(18, 2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                customer_id VARCHAR(50),
                customer_name VARCHAR(200),
                customer_email VARCHAR(200),
                card_last_four: VARCHAR(4),
                error_code VARCHAR(50),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # 支付回调表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_callbacks (
                id BIGSERIAL PRIMARY KEY,
                callback_id VARCHAR(50) UNIQUE NOT NULL,
                transaction_id VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                callback_data JSONB NOT NULL,
                callback_time TIMESTAMP NOT NULL,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 清算记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS clearing_records (
                id BIGSERIAL PRIMARY KEY,
                clearing_id VARCHAR(50) UNIQUE NOT NULL,
                clearing_date DATE NOT NULL,
                merchant_id VARCHAR(50) NOT NULL,
                transaction_count INTEGER NOT NULL,
                total_amount NUMERIC(18, 2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                clearing_status VARCHAR(50) NOT NULL,
                settlement_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)

        # 结算记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS settlement_records (
                id BIGSERIAL PRIMARY KEY,
                settlement_id VARCHAR(50) UNIQUE NOT NULL,
                settlement_date DATE NOT NULL,
                merchant_id VARCHAR(50) NOT NULL,
                clearing_id VARCHAR(50) NOT NULL,
                settlement_amount NUMERIC(18, 2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                fee_amount NUMERIC(18, 2) DEFAULT 0,
                net_amount NUMERIC(18, 2) NOT NULL,
                settlement_status VARCHAR(50) NOT NULL,
                bank_account VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # 数字货币交易表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS digital_currency_transactions (
                id BIGSERIAL PRIMARY KEY,
                transaction_id VARCHAR(100) UNIQUE NOT NULL,
                transaction_hash VARCHAR(100) UNIQUE NOT NULL,
                from_address VARCHAR(100) NOT NULL,
                to_address VARCHAR(100) NOT NULL,
                amount NUMERIC(36, 18) NOT NULL,
                currency VARCHAR(20) NOT NULL,
                transaction_fee NUMERIC(36, 18) DEFAULT 0,
                status VARCHAR(50) NOT NULL,
                block_number BIGINT,
                block_hash VARCHAR(100),
                confirmation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP
            )
        """)

        # Payment统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_statistics (
                id SERIAL PRIMARY KEY,
                statistic_type VARCHAR(50) NOT NULL,
                merchant_id VARCHAR(50),
                payment_method VARCHAR(50),
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(statistic_type, merchant_id, payment_method, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_payment_transactions_merchant
            ON payment_transactions(merchant_id, created_at DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_payment_transactions_status
            ON payment_transactions(status, created_at DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_clearing_records_date
            ON clearing_records(clearing_date DESC, merchant_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_settlement_records_date
            ON settlement_records(settlement_date DESC, merchant_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_digital_currency_status
            ON digital_currency_transactions(status, created_at DESC)
        """)

        self.conn.commit()

    def store_payment_transaction(self, request_id: str, merchant_id: str,
                                  order_id: str, amount: Decimal,
                                  currency: str, payment_method: str,
                                  customer_id: str = None,
                                  customer_name: str = None,
                                  customer_email: str = None,
                                  card_last_four: str = None):
        """存储支付交易"""
        self.cur.execute("""
            INSERT INTO payment_transactions
            (request_id, merchant_id, order_id, amount, currency,
             payment_method, status, customer_id, customer_name,
             customer_email, card_last_four)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (request_id) DO UPDATE
            SET updated_at = CURRENT_TIMESTAMP
        """, (request_id, merchant_id, order_id, amount, currency,
              payment_method, 'Pending', customer_id, customer_name,
              customer_email, card_last_four))
        self.conn.commit()

    def update_payment_status(self, request_id: str, transaction_id: str,
                             status: str, error_code: str = None,
                             error_message: str = None):
        """更新支付状态"""
        self.cur.execute("""
            UPDATE payment_transactions
            SET transaction_id = %s,
                status = %s,
                error_code = %s,
                error_message = %s,
                updated_at = CURRENT_TIMESTAMP,
                completed_at = CASE WHEN %s IN ('Completed', 'Failed')
                                   THEN CURRENT_TIMESTAMP
                                   ELSE completed_at END
            WHERE request_id = %s
        """, (transaction_id, status, error_code, error_message, status, request_id))
        self.conn.commit()

    def calculate_payment_statistics(self, merchant_id: str,
                                    time_window: datetime):
        """计算支付统计信息"""
        self.cur.execute("""
            SELECT
                payment_method,
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN status = 'Completed' THEN 1 END) as successful,
                COUNT(CASE WHEN status = 'Failed' THEN 1 END) as failed,
                SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END) as total_amount,
                AVG(CASE WHEN status = 'Completed'
                    THEN EXTRACT(EPOCH FROM (completed_at - created_at))
                    ELSE NULL END) as avg_processing_time
            FROM payment_transactions
            WHERE merchant_id = %s AND created_at >= %s
            GROUP BY payment_method
        """, (merchant_id, time_window))

        stats = {}
        for row in self.cur.fetchall():
            stats[row[0]] = {
                'total_transactions': row[1],
                'successful': row[2],
                'failed': row[3],
                'total_amount': float(row[4]),
                'avg_processing_time': row[5]
            }

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO payment_statistics
            (statistic_type, merchant_id, payment_method, time_window, statistics)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (statistic_type, merchant_id, payment_method, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, ('payment_performance', merchant_id, 'ALL', time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 Payment数据分析查询

**查询示例**：

```python
# 查询支付交易
storage.cur.execute("""
    SELECT request_id, order_id, amount, currency, status, created_at
    FROM payment_transactions
    WHERE merchant_id = %s AND created_at BETWEEN %s AND %s
    ORDER BY created_at DESC
""", (merchant_id, start_date, end_date))

# 查询支付成功率
storage.cur.execute("""
    SELECT
        DATE(created_at) as date,
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'Completed' THEN 1 END) as successful,
        ROUND(COUNT(CASE WHEN status = 'Completed' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
    FROM payment_transactions
    WHERE merchant_id = %s AND created_at >= %s
    GROUP BY DATE(created_at)
    ORDER BY date DESC
""", (merchant_id, start_date))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
