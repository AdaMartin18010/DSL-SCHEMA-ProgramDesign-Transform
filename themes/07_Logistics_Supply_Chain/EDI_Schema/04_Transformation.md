# EDI Schema转换体系

## 📑 目录

- [EDI Schema转换体系](#edi-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. EDI X12到EDIFACT转换](#2-edi-x12到edifact转换)
  - [3. EDIFACT到EDI X12转换](#3-edifact到edi-x12转换)
  - [4. EDI消息验证](#4-edi消息验证)
  - [5. EDI数据存储与分析](#5-edi数据存储与分析)
    - [5.1 PostgreSQL EDI数据存储](#51-postgresql-edi数据存储)
    - [5.2 EDI数据分析查询](#52-edi数据分析查询)

---

## 1. 转换体系概述

EDI Schema转换体系支持EDI X12、EDIFACT之间的转换，
以及EDI数据到数据库存储的转换。

### 1.1 转换目标

1. **EDI X12到EDIFACT转换**：EDI X12交易集到EDIFACT消息
2. **EDIFACT到EDI X12转换**：EDIFACT消息到EDI X12交易集
3. **EDI消息验证**：EDI消息格式和内容验证
4. **EDI数据到数据库转换**：EDI消息到PostgreSQL存储

---

## 2. EDI X12到EDIFACT转换

**转换规则**：

- 850 (Purchase Order) → ORDERS
- 855 (Purchase Order Acknowledgment) → ORDRSP
- 856 (Ship Notice) → DESADV
- 810 (Invoice) → INVOIC

**转换示例**：

```python
def convert_x12_850_to_edifact_orders(x12_850: dict) -> dict:
    """将EDI X12 850交易集转换为EDIFACT ORDERS消息"""
    edifact_orders = {
        "UNH": {
            "message_reference_number": generate_message_ref(),
            "message_type": "ORDERS",
            "message_version_number": "D",
            "message_release_number": "23A",
            "controlling_agency": "UN"
        },
        "BGM": {
            "document_message_name": "220",
            "document_message_number": x12_850.get("BEG", {}).get("purchase_order_number"),
            "message_function_code": "9"  # Original
        },
        "DTM": [
            {
                "date_time_period_qualifier": "137",
                "date_time_period": format_date(x12_850.get("BEG", {}).get("date")),
                "date_time_period_format_qualifier": "102"
            }
        ],
        "LIN": []
    }

    # 转换订单行项
    for po1 in x12_850.get("PO1_segments", []):
        lin_segment = {
            "line_item_number": po1.get("assigned_identification"),
            "item_number_identification": {
                "item_number_type_code_qualifier": map_product_id_qualifier(po1.get("product_id_qualifier")),
                "item_number": po1.get("product_id")
            },
            "quantity_details": {
                "quantity_type_code_qualifier": "21",
                "quantity": po1.get("quantity_ordered"),
                "measure_unit_code": po1.get("unit_of_measure")
            },
            "price_information": {
                "price_code_qualifier": "AAA",
                "price_amount": po1.get("unit_price"),
                "price_type_code": "CA"
            }
        }
        edifact_orders["LIN"].append(lin_segment)

    return edifact_orders

def map_product_id_qualifier(x12_qualifier: str) -> str:
    """映射EDI X12产品ID限定符到EDIFACT"""
    mapping = {
        "UP": "EN",  # Universal Product Code -> EAN
        "VN": "EN",  # Vendor Item Number -> EAN
        "IN": "IN"   # Buyer Item Number -> Item Number
    }
    return mapping.get(x12_qualifier, "IN")
```

---

## 3. EDIFACT到EDI X12转换

**转换规则**：

- ORDERS → 850 (Purchase Order)
- ORDRSP → 855 (Purchase Order Acknowledgment)
- DESADV → 856 (Ship Notice)
- INVOIC → 810 (Invoice)

**转换示例**：

```python
def convert_edifact_orders_to_x12_850(edifact_orders: dict) -> dict:
    """将EDIFACT ORDERS消息转换为EDI X12 850交易集"""
    x12_850 = {
        "ST": {
            "transaction_set_identifier_code": "850",
            "transaction_set_control_number": generate_control_number()
        },
        "BEG": {
            "transaction_set_purpose_code": map_message_function_code(edifact_orders.get("BGM", {}).get("message_function_code")),
            "purchase_order_type_code": "SA",  # Stand-alone
            "purchase_order_number": edifact_orders.get("BGM", {}).get("document_message_number"),
            "date": parse_date(edifact_orders.get("DTM", [{}])[0].get("date_time_period"))
        },
        "PO1_segments": []
    }

    # 转换订单行项
    for lin in edifact_orders.get("LIN", []):
        po1_segment = {
            "assigned_identification": lin.get("line_item_number", "1"),
            "quantity_ordered": lin.get("quantity_details", {}).get("quantity"),
            "unit_of_measure": lin.get("quantity_details", {}).get("measure_unit_code"),
            "unit_price": lin.get("price_information", {}).get("price_amount"),
            "product_id_qualifier": map_item_number_qualifier(lin.get("item_number_identification", {}).get("item_number_type_code_qualifier")),
            "product_id": lin.get("item_number_identification", {}).get("item_number")
        }
        x12_850["PO1_segments"].append(po1_segment)

    x12_850["SE"] = {
        "number_of_included_segments": calculate_segment_count(x12_850),
        "transaction_set_control_number": x12_850["ST"]["transaction_set_control_number"]
    }

    return x12_850

def map_message_function_code(edifact_code: str) -> str:
    """映射EDIFACT消息功能代码到EDI X12"""
    mapping = {
        "9": "00",   # Original -> Original
        "5": "08",   # Replace -> Change
        "36": "01"   # Cancellation -> Cancellation
    }
    return mapping.get(edifact_code, "00")
```

---

## 4. EDI消息验证

**验证规则**：

- 消息结构验证
- 段顺序验证
- 数据元素格式验证
- 必填字段验证

**验证示例**：

```python
def validate_edi_x12_message(x12_message: dict) -> dict:
    """验证EDI X12消息"""
    errors = []
    warnings = []

    # 验证交易集头
    if "ST" not in x12_message:
        errors.append("Missing ST segment (Transaction Set Header)")

    # 验证交易集尾
    if "SE" not in x12_message:
        errors.append("Missing SE segment (Transaction Set Trailer)")

    # 验证段计数
    if "ST" in x12_message and "SE" in x12_message:
        expected_count = x12_message["SE"]["number_of_included_segments"]
        actual_count = count_segments(x12_message)
        if expected_count != actual_count:
            errors.append(f"Segment count mismatch: expected {expected_count}, actual {actual_count}")

    # 验证必填字段
    if "BEG" in x12_message:
        if not x12_message["BEG"].get("purchase_order_number"):
            errors.append("BEG segment missing required field: purchase_order_number")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_edifact_message(edifact_message: dict) -> dict:
    """验证EDIFACT消息"""
    errors = []
    warnings = []

    # 验证消息头
    if "UNH" not in edifact_message:
        errors.append("Missing UNH segment (Message Header)")

    # 验证消息尾
    if "UNT" not in edifact_message:
        errors.append("Missing UNT segment (Message Trailer)")

    # 验证段计数
    if "UNH" in edifact_message and "UNT" in edifact_message:
        expected_count = edifact_message["UNT"]["number_of_segments_in_message"]
        actual_count = count_segments(edifact_message)
        if expected_count != actual_count:
            errors.append(f"Segment count mismatch: expected {expected_count}, actual {actual_count}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
```

---

## 5. EDI数据存储与分析

### 5.1 PostgreSQL EDI数据存储

**数据库设计**：

```python
import psycopg2
from datetime import datetime
from typing import List, Optional, Dict
import uuid
import json

class EDIStorage:
    """EDI数据PostgreSQL存储类"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.create_tables()

    def create_tables(self):
        """创建EDI数据存储表"""
        cursor = self.conn.cursor()

        # EDI交换表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_interchanges (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                interchange_type VARCHAR(10) NOT NULL,
                interchange_control_number VARCHAR(14) NOT NULL UNIQUE,
                sender_id VARCHAR(35),
                receiver_id VARCHAR(35),
                interchange_date DATE,
                interchange_time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI功能组表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_functional_groups (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                interchange_id UUID NOT NULL REFERENCES edi_interchanges(id) ON DELETE CASCADE,
                functional_identifier_code VARCHAR(2),
                group_control_number VARCHAR(9) NOT NULL,
                sender_code VARCHAR(15),
                receiver_code VARCHAR(15),
                date DATE,
                time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI交易集/消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                functional_group_id UUID NOT NULL REFERENCES edi_functional_groups(id) ON DELETE CASCADE,
                transaction_type VARCHAR(10) NOT NULL,
                transaction_set_id VARCHAR(3),
                transaction_control_number VARCHAR(14) NOT NULL,
                message_type VARCHAR(6),
                message_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI段表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_segments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                transaction_id UUID NOT NULL REFERENCES edi_transactions(id) ON DELETE CASCADE,
                segment_id VARCHAR(3) NOT NULL,
                segment_position INTEGER NOT NULL,
                segment_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI元素表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_elements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                segment_id UUID NOT NULL REFERENCES edi_segments(id) ON DELETE CASCADE,
                element_position INTEGER NOT NULL,
                element_value TEXT,
                element_format VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI统计信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_statistics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                statistic_type VARCHAR(50) NOT NULL,
                transaction_type VARCHAR(10),
                statistic_date DATE NOT NULL,
                count_value BIGINT DEFAULT 0,
                additional_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interchange_control_number ON edi_interchanges(interchange_control_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interchange_date ON edi_interchanges(interchange_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_functional_group_number ON edi_functional_groups(group_control_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_type ON edi_transactions(transaction_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_control_number ON edi_transactions(transaction_control_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_segment_id ON edi_segments(segment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_segment_position ON edi_segments(segment_position)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edi_statistics_date ON edi_statistics(statistic_date)")

        self.conn.commit()
        cursor.close()

    def store_edi_x12_transaction(self, interchange_data: dict, functional_group_data: dict, transaction_data: dict) -> str:
        """存储EDI X12交易集"""
        cursor = self.conn.cursor()

        # 存储交换
        cursor.execute("""
            INSERT INTO edi_interchanges (
                interchange_type, interchange_control_number,
                sender_id, receiver_id, interchange_date, interchange_time
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (interchange_control_number) DO UPDATE SET
                sender_id = EXCLUDED.sender_id,
                receiver_id = EXCLUDED.receiver_id
            RETURNING id
        """, (
            "X12",
            interchange_data.get("isa", {}).get("interchange_control_number"),
            interchange_data.get("isa", {}).get("interchange_sender_id"),
            interchange_data.get("isa", {}).get("interchange_receiver_id"),
            parse_date(interchange_data.get("isa", {}).get("interchange_date")),
            parse_time(interchange_data.get("isa", {}).get("interchange_time"))
        ))
        interchange_id = cursor.fetchone()[0]

        # 存储功能组
        cursor.execute("""
            INSERT INTO edi_functional_groups (
                interchange_id, functional_identifier_code,
                group_control_number, sender_code, receiver_code, date, time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            interchange_id,
            functional_group_data.get("gs", {}).get("functional_identifier_code"),
            functional_group_data.get("gs", {}).get("group_control_number"),
            functional_group_data.get("gs", {}).get("application_sender_code"),
            functional_group_data.get("gs", {}).get("application_receiver_code"),
            parse_date(functional_group_data.get("gs", {}).get("date")),
            parse_time(functional_group_data.get("gs", {}).get("time"))
        ))
        functional_group_id = cursor.fetchone()[0]

        # 存储交易集
        cursor.execute("""
            INSERT INTO edi_transactions (
                functional_group_id, transaction_type,
                transaction_set_id, transaction_control_number, message_data
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            functional_group_id,
            "X12",
            transaction_data.get("ST", {}).get("transaction_set_identifier_code"),
            transaction_data.get("ST", {}).get("transaction_set_control_number"),
            json.dumps(transaction_data)
        ))
        transaction_id = cursor.fetchone()[0]

        # 存储段
        segment_position = 1
        for segment_id, segment_data in transaction_data.items():
            if segment_id not in ["ST", "SE"]:  # 跳过头尾段
                cursor.execute("""
                    INSERT INTO edi_segments (
                        transaction_id, segment_id, segment_position, segment_data
                    ) VALUES (%s, %s, %s, %s)
                """, (transaction_id, segment_id, segment_position, json.dumps(segment_data)))
                segment_position += 1

        self.conn.commit()
        cursor.close()
        return str(transaction_id)

    def store_edifact_message(self, interchange_data: dict, message_data: dict) -> str:
        """存储EDIFACT消息"""
        cursor = self.conn.cursor()

        # 存储交换
        cursor.execute("""
            INSERT INTO edi_interchanges (
                interchange_type, interchange_control_number,
                sender_id, receiver_id, interchange_date, interchange_time
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (interchange_control_number) DO UPDATE SET
                sender_id = EXCLUDED.sender_id,
                receiver_id = EXCLUDED.receiver_id
            RETURNING id
        """, (
            "EDIFACT",
            interchange_data.get("UNB", {}).get("interchange_control_reference"),
            interchange_data.get("UNB", {}).get("sender_identification"),
            interchange_data.get("UNB", {}).get("recipient_identification"),
            parse_date(interchange_data.get("UNB", {}).get("date_of_preparation")),
            parse_time(interchange_data.get("UNB", {}).get("time_of_preparation"))
        ))
        interchange_id = cursor.fetchone()[0]

        # 存储功能组（EDIFACT中为消息）
        cursor.execute("""
            INSERT INTO edi_functional_groups (
                interchange_id, group_control_number
            ) VALUES (%s, %s)
            RETURNING id
        """, (
            interchange_id,
            message_data.get("UNH", {}).get("message_reference_number")
        ))
        functional_group_id = cursor.fetchone()[0]

        # 存储消息
        cursor.execute("""
            INSERT INTO edi_transactions (
                functional_group_id, transaction_type,
                message_type, transaction_control_number, message_data
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            functional_group_id,
            "EDIFACT",
            message_data.get("UNH", {}).get("message_type"),
            message_data.get("UNH", {}).get("message_reference_number"),
            json.dumps(message_data)
        ))
        transaction_id = cursor.fetchone()[0]

        self.conn.commit()
        cursor.close()
        return str(transaction_id)

    def query_transactions_by_type(self, transaction_type: str, start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[dict]:
        """根据交易类型查询交易集"""
        cursor = self.conn.cursor()
        query = """
            SELECT t.*, fg.group_control_number, i.interchange_control_number
            FROM edi_transactions t
            INNER JOIN edi_functional_groups fg ON t.functional_group_id = fg.id
            INNER JOIN edi_interchanges i ON fg.interchange_id = i.id
            WHERE t.transaction_type = %s
        """
        params = [transaction_type]

        if start_date:
            query += " AND i.interchange_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND i.interchange_date <= %s"
            params.append(end_date)

        query += " ORDER BY i.interchange_date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
```

---

### 5.2 EDI数据分析查询

**查询示例**：

```python
# 查询EDI交易统计
def query_edi_statistics(storage: EDIStorage, start_date: datetime, end_date: datetime):
    """查询EDI交易统计"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        SELECT
            t.transaction_type,
            t.transaction_set_id,
            COUNT(*) as transaction_count,
            COUNT(DISTINCT i.sender_id) as sender_count,
            COUNT(DISTINCT i.receiver_id) as receiver_count
        FROM edi_transactions t
        INNER JOIN edi_functional_groups fg ON t.functional_group_id = fg.id
        INNER JOIN edi_interchanges i ON fg.interchange_id = i.id
        WHERE i.interchange_date BETWEEN %s AND %s
        GROUP BY t.transaction_type, t.transaction_set_id
        ORDER BY transaction_count DESC
    """, (start_date, end_date))
    return cursor.fetchall()

# 查询订单处理流程
def query_order_processing_flow(storage: EDIStorage, order_number: str):
    """查询订单处理流程"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        SELECT
            t.transaction_type,
            t.transaction_set_id,
            t.message_data->>'BEG'->>'purchase_order_number' as order_number,
            i.interchange_date,
            i.sender_id,
            i.receiver_id
        FROM edi_transactions t
        INNER JOIN edi_functional_groups fg ON t.functional_group_id = fg.id
        INNER JOIN edi_interchanges i ON fg.interchange_id = i.id
        WHERE t.message_data::text LIKE %s
        ORDER BY i.interchange_date
    """, (f'%{order_number}%',))
    return cursor.fetchall()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
