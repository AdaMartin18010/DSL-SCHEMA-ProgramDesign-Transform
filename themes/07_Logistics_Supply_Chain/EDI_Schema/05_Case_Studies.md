# EDI Schema实践案例

## 📑 目录

- [EDI Schema实践案例](#edi-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：EDI X12 850采购订单](#2-案例1edi-x12-850采购订单)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 实现方案](#22-实现方案)
  - [3. 案例2：EDIFACT ORDERS订单消息](#3-案例2edifact-orders订单消息)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现方案](#32-实现方案)
  - [4. 案例3：EDI X12到EDIFACT转换](#4-案例3edi-x12到edifact转换)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：EDI消息验证](#5-案例4edi消息验证)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：EDI数据存储与分析](#6-案例5edi数据存储与分析)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现方案](#62-实现方案)

---

## 1. 案例概述

本文档提供EDI Schema在实际应用中的案例，
涵盖EDI X12、EDIFACT等场景。

---

## 2. 案例1：EDI X12 850采购订单

### 2.1 场景描述

供应商接收客户的EDI X12 850采购订单，
处理订单并返回855确认。

### 2.2 实现方案

**EDI X12 850数据结构**：

```python
x12_850_data = {
    "ISA": {
        "interchange_control_number": "000000001",
        "interchange_sender_id": "SUPPLIER01",
        "interchange_receiver_id": "CUSTOMER01",
        "interchange_date": "250121",
        "interchange_time": "1200"
    },
    "GS": {
        "functional_identifier_code": "PO",
        "group_control_number": "000000001",
        "application_sender_code": "SUPPLIER01",
        "application_receiver_code": "CUSTOMER01",
        "date": "20250121",
        "time": "120000"
    },
    "ST": {
        "transaction_set_identifier_code": "850",
        "transaction_set_control_number": "0001"
    },
    "BEG": {
        "transaction_set_purpose_code": "00",
        "purchase_order_type_code": "SA",
        "purchase_order_number": "PO-2025-001",
        "date": "20250121"
    },
    "N1": [
        {
            "entity_identifier_code": "ST",
            "name": "ABC Supplier",
            "identification_code_qualifier": "92",
            "identification_code": "SUPPLIER01"
        },
        {
            "entity_identifier_code": "BT",
            "name": "XYZ Customer",
            "identification_code_qualifier": "92",
            "identification_code": "CUSTOMER01"
        }
    ],
    "PO1": [
        {
            "assigned_identification": "1",
            "quantity_ordered": 100.0,
            "unit_of_measure": "EA",
            "unit_price": 25.50,
            "product_id_qualifier": "UP",
            "product_id": "123456789012"
        },
        {
            "assigned_identification": "2",
            "quantity_ordered": 50.0,
            "unit_of_measure": "EA",
            "unit_price": 15.75,
            "product_id_qualifier": "UP",
            "product_id": "987654321098"
        }
    ],
    "SE": {
        "number_of_included_segments": 10,
        "transaction_set_control_number": "0001"
    }
}
```

**EDI X12 850存储示例**：

```python
from edi_storage import EDIStorage

# 初始化存储
storage = EDIStorage("postgresql://user:password@localhost/edi_db")

# 存储EDI X12 850交易集
interchange_data = {"isa": x12_850_data["ISA"]}
functional_group_data = {"gs": x12_850_data["GS"]}
transaction_data = {k: v for k, v in x12_850_data.items() if k not in ["ISA", "GS"]}

transaction_id = storage.store_edi_x12_transaction(
    interchange_data,
    functional_group_data,
    transaction_data
)
print(f"EDI X12 850 stored with ID: {transaction_id}")

# 查询订单
orders = storage.query_transactions_by_type("X12", start_date=datetime(2025, 1, 1))
print(f"Found {len(orders)} X12 transactions")
```

---

## 3. 案例2：EDIFACT ORDERS订单消息

### 3.1 场景描述

供应商接收客户的EDIFACT ORDERS订单消息，
处理订单并返回ORDRSP确认。

### 3.2 实现方案

**EDIFACT ORDERS数据结构**：

```python
edifact_orders_data = {
    "UNB": {
        "syntax_identifier": "UNOA",
        "syntax_version_number": "3",
        "sender_identification": "SUPPLIER01",
        "sender_partner_qualifier": "ZZZ",
        "recipient_identification": "CUSTOMER01",
        "recipient_partner_qualifier": "ZZZ",
        "date_of_preparation": "20250121",
        "time_of_preparation": "1200",
        "interchange_control_reference": "000000001"
    },
    "UNH": {
        "message_reference_number": "000000001",
        "message_type": "ORDERS",
        "message_version_number": "D",
        "message_release_number": "23A",
        "controlling_agency": "UN"
    },
    "BGM": {
        "document_message_name": "220",
        "document_message_number": "PO-2025-001",
        "message_function_code": "9"
    },
    "DTM": [
        {
            "date_time_period_qualifier": "137",
            "date_time_period": "20250121",
            "date_time_period_format_qualifier": "102"
        }
    ],
    "NAD": [
        {
            "party_qualifier": "SU",
            "party_identification_details": {
                "party_id_identification": "SUPPLIER01"
            },
            "name_and_address": {
                "party_name": "ABC Supplier"
            }
        },
        {
            "party_qualifier": "BY",
            "party_identification_details": {
                "party_id_identification": "CUSTOMER01"
            },
            "name_and_address": {
                "party_name": "XYZ Customer"
            }
        }
    ],
    "LIN": [
        {
            "line_item_number": "1",
            "item_number_identification": {
                "item_number_type_code_qualifier": "EN",
                "item_number": "123456789012"
            },
            "quantity_details": {
                "quantity_type_code_qualifier": "21",
                "quantity": 100.0,
                "measure_unit_code": "EA"
            },
            "price_information": {
                "price_code_qualifier": "AAA",
                "price_amount": 25.50,
                "price_type_code": "CA"
            }
        },
        {
            "line_item_number": "2",
            "item_number_identification": {
                "item_number_type_code_qualifier": "EN",
                "item_number": "987654321098"
            },
            "quantity_details": {
                "quantity_type_code_qualifier": "21",
                "quantity": 50.0,
                "measure_unit_code": "EA"
            },
            "price_information": {
                "price_code_qualifier": "AAA",
                "price_amount": 15.75,
                "price_type_code": "CA"
            }
        }
    ],
    "UNT": {
        "number_of_segments_in_message": 10,
        "message_reference_number": "000000001"
    },
    "UNZ": {
        "interchange_control_count": 1,
        "interchange_control_reference": "000000001"
    }
}
```

**EDIFACT ORDERS存储示例**：

```python
# 存储EDIFACT ORDERS消息
interchange_data = {"UNB": edifact_orders_data["UNB"]}
message_data = {k: v for k, v in edifact_orders_data.items() if k not in ["UNB", "UNZ"]}

message_id = storage.store_edifact_message(interchange_data, message_data)
print(f"EDIFACT ORDERS stored with ID: {message_id}")

# 查询订单
orders = storage.query_transactions_by_type("EDIFACT", start_date=datetime(2025, 1, 1))
print(f"Found {len(orders)} EDIFACT transactions")
```

---

## 4. 案例3：EDI X12到EDIFACT转换

### 4.1 场景描述

企业需要将EDI X12 850采购订单转换为EDIFACT ORDERS消息，
以支持国际化业务。

### 4.2 实现代码

```python
from edi_transformation import convert_x12_850_to_edifact_orders

# 转换EDI X12 850到EDIFACT ORDERS
edifact_orders = convert_x12_850_to_edifact_orders(x12_850_data)

print("Converted EDIFACT ORDERS:")
print(f"  Message Type: {edifact_orders['UNH']['message_type']}")
print(f"  Order Number: {edifact_orders['BGM']['document_message_number']}")
print(f"  Line Items: {len(edifact_orders['LIN'])}")

# 存储转换后的消息
interchange_data = {"UNB": generate_unb_header()}
message_id = storage.store_edifact_message(interchange_data, edifact_orders)
print(f"Converted message stored with ID: {message_id}")
```

---

## 5. 案例4：EDI消息验证

### 5.1 场景描述

企业需要验证接收到的EDI消息格式和内容，
确保消息符合标准要求。

### 5.2 实现代码

```python
from edi_validation import validate_edi_x12_message, validate_edifact_message

# 验证EDI X12消息
x12_validation = validate_edi_x12_message(x12_850_data)
if x12_validation["valid"]:
    print("EDI X12 message is valid")
else:
    print("EDI X12 message validation errors:")
    for error in x12_validation["errors"]:
        print(f"  - {error}")

# 验证EDIFACT消息
edifact_validation = validate_edifact_message(edifact_orders_data)
if edifact_validation["valid"]:
    print("EDIFACT message is valid")
else:
    print("EDIFACT message validation errors:")
    for error in edifact_validation["errors"]:
        print(f"  - {error}")
```

---

## 6. 案例5：EDI数据存储与分析

### 6.1 场景描述

企业需要存储和分析EDI交易数据，
支持供应链数据统计和报表生成。

### 6.2 实现方案

**EDI数据统计查询**：

```python
from datetime import datetime, timedelta

# 查询EDI交易统计
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

statistics = storage.query_edi_statistics(start_date, end_date)
print("EDI Statistics (Last 30 days):")
for stat in statistics:
    print(f"  {stat[1]}: {stat[2]} transactions, {stat[3]} senders, {stat[4]} receivers")

# 查询订单处理流程
order_number = "PO-2025-001"
flow = storage.query_order_processing_flow(order_number)
print(f"\nOrder Processing Flow for {order_number}:")
for step in flow:
    print(f"  {step['interchange_date']}: {step['transaction_set_id']} from {step['sender_id']} to {step['receiver_id']}")
```

**EDI数据分析报表**：

```python
def generate_edi_analytics_report(storage: EDIStorage, start_date: datetime, end_date: datetime):
    """生成EDI数据分析报表"""
    cursor = storage.conn.cursor()

    # 1. 交易类型统计
    cursor.execute("""
        SELECT
            transaction_type,
            transaction_set_id,
            COUNT(*) as transaction_count
        FROM edi_transactions
        WHERE created_at BETWEEN %s AND %s
        GROUP BY transaction_type, transaction_set_id
        ORDER BY transaction_count DESC
    """, (start_date, end_date))
    transaction_stats = cursor.fetchall()

    # 2. 发送方/接收方统计
    cursor.execute("""
        SELECT
            sender_id,
            receiver_id,
            COUNT(*) as interchange_count
        FROM edi_interchanges
        WHERE interchange_date BETWEEN %s AND %s
        GROUP BY sender_id, receiver_id
        ORDER BY interchange_count DESC
    """, (start_date, end_date))
    partner_stats = cursor.fetchall()

    # 3. 错误统计
    cursor.execute("""
        SELECT
            transaction_type,
            COUNT(*) as error_count
        FROM edi_statistics
        WHERE statistic_type = 'ERROR'
        AND statistic_date BETWEEN %s AND %s
        GROUP BY transaction_type
        ORDER BY error_count DESC
    """, (start_date, end_date))
    error_stats = cursor.fetchall()

    cursor.close()

    return {
        "transaction_statistics": transaction_stats,
        "partner_statistics": partner_stats,
        "error_statistics": error_stats
    }

# 生成报表
report = generate_edi_analytics_report(storage, start_date, end_date)
print("EDI Analytics Report:")
print(f"Transaction Statistics: {report['transaction_statistics']}")
print(f"Partner Statistics: {report['partner_statistics']}")
print(f"Error Statistics: {report['error_statistics']}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
