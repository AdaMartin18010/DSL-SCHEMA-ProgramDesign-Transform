# ISO 20022 Schema转换体系

## 📑 目录

- [ISO 20022 Schema转换体系](#iso-20022-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. ISO 20022到SWIFT MT转换](#2-iso-20022到swift-mt转换)
  - [3. ISO 20022到XML转换](#3-iso-20022到xml转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. ISO 20022数据存储与分析](#6-iso-20022数据存储与分析)
    - [6.1 PostgreSQL ISO 20022数据存储](#61-postgresql-iso-20022数据存储)
    - [6.2 ISO 20022数据分析查询](#62-iso-20022数据分析查询)

---

## 1. 转换体系概述

ISO 20022 Schema转换体系支持ISO 20022消息
与SWIFT MT消息、XML格式之间的转换，以及
ISO 20022数据存储。

### 1.1 转换目标

1. **ISO 20022到SWIFT MT转换**：ISO 20022消息到SWIFT MT消息
2. **ISO 20022到XML转换**：ISO 20022消息到标准XML格式
3. **消息到数据库转换**：ISO 20022消息到PostgreSQL存储

---

## 2. ISO 20022到SWIFT MT转换

**转换规则**：

- pacs.008 → MT103
- pacs.009 → MT202
- camt.053 → MT940

**转换示例**：

```python
def convert_pacs008_to_mt103(pacs008: Pacs008) -> MT103:
    """将pacs.008转换为MT103"""
    mt103 = MT103()

    # 转换基本信息
    mt103.field_20 = pacs008.payment_information.payment_information_identification
    mt103.field_23B = "CRED"

    # 转换金额和日期
    transaction = pacs008.payment_information.credit_transfer_transaction_information[0]
    mt103.field_32A = format_date_amount_currency(
        pacs008.payment_information.requested_execution_date,
        transaction.amount.instructed_amount.value,
        transaction.amount.instructed_amount.currency
    )

    # 转换付款人信息
    mt103.field_50A = format_party(
        pacs008.payment_information.debtor.name,
        pacs008.payment_information.debtor_account.identification
    )

    # 转换收款人信息
    mt103.field_59 = format_party(
        transaction.creditor.name,
        transaction.creditor_account.identification
    )

    return mt103
```

---

## 3. ISO 20022到XML转换

**转换规则**：

- ISO 20022消息对象 → XML文档
- 标准XML命名空间：urn:iso:std:iso:20022:tech:xsd

**转换示例**：

```python
def convert_iso20022_to_xml(message: ISO20022Message) -> str:
    """将ISO 20022消息转换为XML"""
    root = ET.Element(
        message.message_type,
        xmlns="urn:iso:std:iso:20022:tech:xsd:" + message.message_type
    )

    # 转换组头
    group_header = ET.SubElement(root, "GrpHdr")
    ET.SubElement(group_header, "MsgId").text = message.group_header.message_identification
    ET.SubElement(group_header, "CreDtTm").text = message.group_header.creation_date_time.isoformat()

    # 转换消息内容
    if hasattr(message, 'payment_information'):
        payment_info = ET.SubElement(root, "PmtInf")
        ET.SubElement(payment_info, "PmtInfId").text = message.payment_information.payment_information_identification

        for transaction in message.payment_information.credit_transfer_transaction_information:
            cdt_trf_tx_inf = ET.SubElement(payment_info, "CdtTrfTxInf")
            pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
            ET.SubElement(pmt_id, "EndToEndId").text = transaction.payment_identification.end_to_end_identification

            amt = ET.SubElement(cdt_trf_tx_inf, "Amt")
            instd_amt = ET.SubElement(amt, "InstdAmt", Ccy=transaction.amount.instructed_amount.currency)
            instd_amt.text = str(transaction.amount.instructed_amount.value)

    return ET.tostring(root, encoding='unicode', pretty_print=True)
```

---

## 4. 转换工具

- **ISO 20022 Repository**：ISO 20022官方消息库
- **SWIFT Alliance**：SWIFT消息转换工具
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的消息完整性、格式正确性和业务逻辑一致性。

---

## 6. ISO 20022数据存储与分析

### 6.1 PostgreSQL ISO 20022数据存储

**ISO 20022数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class ISO20022Storage:
    """ISO 20022数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建ISO 20022数据表"""
        # ISO 20022消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iso20022_messages (
                id BIGSERIAL PRIMARY KEY,
                message_identification VARCHAR(35) UNIQUE NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                business_area VARCHAR(10) NOT NULL,
                creation_date_time TIMESTAMP NOT NULL,
                message_content JSONB NOT NULL,
                message_xml TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 支付消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iso20022_payment_messages (
                id BIGSERIAL PRIMARY KEY,
                message_identification VARCHAR(35) UNIQUE NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                payment_information_id VARCHAR(35),
                debtor_name VARCHAR(140),
                debtor_account VARCHAR(34),
                creditor_name VARCHAR(140),
                creditor_account VARCHAR(34),
                amount DECIMAL(18,5),
                currency VARCHAR(3),
                execution_date DATE,
                end_to_end_identification VARCHAR(35),
                status VARCHAR(20) DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 现金管理消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iso20022_cash_management_messages (
                id BIGSERIAL PRIMARY KEY,
                message_identification VARCHAR(35) UNIQUE NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                account_identification VARCHAR(34),
                statement_date DATE,
                opening_balance DECIMAL(18,5),
                closing_balance DECIMAL(18,5),
                currency VARCHAR(3),
                entry_count INTEGER,
                message_content JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 证券消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iso20022_securities_messages (
                id BIGSERIAL PRIMARY KEY,
                message_identification VARCHAR(35) UNIQUE NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                corporate_action_event_id VARCHAR(35),
                event_type VARCHAR(50),
                security_identification VARCHAR(35),
                record_date DATE,
                ex_date DATE,
                payment_date DATE,
                message_content JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ISO 20022消息统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iso20022_statistics (
                id SERIAL PRIMARY KEY,
                statistic_type VARCHAR(50) NOT NULL,
                business_area VARCHAR(10),
                message_type VARCHAR(20),
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(statistic_type, business_area, message_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iso20022_messages_type_date
            ON iso20022_messages(message_type, creation_date_time DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iso20022_payment_status
            ON iso20022_payment_messages(status, execution_date DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iso20022_payment_e2e
            ON iso20022_payment_messages(end_to_end_identification)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iso20022_cash_account_date
            ON iso20022_cash_management_messages(account_identification, statement_date DESC)
        """)

        self.conn.commit()

    def store_iso20022_message(self, message_identification: str,
                              message_type: str, business_area: str,
                              creation_date_time: datetime,
                              message_content: Dict, message_xml: str = None):
        """存储ISO 20022消息"""
        self.cur.execute("""
            INSERT INTO iso20022_messages
            (message_identification, message_type, business_area,
             creation_date_time, message_content, message_xml)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (message_identification) DO UPDATE
            SET message_content = EXCLUDED.message_content,
                message_xml = EXCLUDED.message_xml
        """, (message_identification, message_type, business_area,
              creation_date_time, json.dumps(message_content), message_xml))

        # 根据消息类型存储到相应表
        if business_area == 'pacs':
            self._store_payment_message(message_type, message_content)
        elif business_area == 'camt':
            self._store_cash_management_message(message_type, message_content)
        elif business_area == 'seev':
            self._store_securities_message(message_type, message_content)

        self.conn.commit()

    def _store_payment_message(self, message_type: str, message_content: Dict):
        """存储支付消息"""
        payment_info = message_content.get('payment_information', {})
        transaction = payment_info.get('credit_transfer_transaction_information', [{}])[0]

        self.cur.execute("""
            INSERT INTO iso20022_payment_messages
            (message_identification, message_type, payment_information_id,
             debtor_name, debtor_account, creditor_name, creditor_account,
             amount, currency, execution_date, end_to_end_identification, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_identification) DO UPDATE
            SET status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
        """, (
            message_content.get('group_header', {}).get('message_identification'),
            message_type,
            payment_info.get('payment_information_identification'),
            payment_info.get('debtor', {}).get('name'),
            payment_info.get('debtor_account', {}).get('identification', {}).get('iban'),
            transaction.get('creditor', {}).get('name'),
            transaction.get('creditor_account', {}).get('identification', {}).get('iban'),
            transaction.get('amount', {}).get('instructed_amount', {}).get('value'),
            transaction.get('amount', {}).get('instructed_amount', {}).get('currency'),
            payment_info.get('requested_execution_date'),
            transaction.get('payment_identification', {}).get('end_to_end_identification'),
            'PENDING'
        ))

    def calculate_message_statistics(self, business_area: str,
                                    message_type: str,
                                    time_window: datetime):
        """计算消息统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_messages,
                COUNT(DISTINCT message_identification) as unique_messages,
                MIN(creation_date_time) as first_message_time,
                MAX(creation_date_time) as last_message_time
            FROM iso20022_messages
            WHERE business_area = %s
            AND message_type = %s
            AND creation_date_time >= %s
        """, (business_area, message_type, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO iso20022_statistics
            (statistic_type, business_area, message_type, time_window, statistics)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (statistic_type, business_area, message_type, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, ('message_volume', business_area, message_type, time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 ISO 20022数据分析查询

**查询示例**：

```python
# 查询支付消息
storage.cur.execute("""
    SELECT message_identification, message_type, amount, currency, status
    FROM iso20022_payment_messages
    WHERE execution_date BETWEEN %s AND %s
    ORDER BY execution_date DESC
""", (start_date, end_date))

# 查询消息类型统计
storage.cur.execute("""
    SELECT message_type, COUNT(*) as message_count
    FROM iso20022_messages
    WHERE creation_date_time >= %s
    GROUP BY message_type
    ORDER BY message_count DESC
""", (start_date,))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
