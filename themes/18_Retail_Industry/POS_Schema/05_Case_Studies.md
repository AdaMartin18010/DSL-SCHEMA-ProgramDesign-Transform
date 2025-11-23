# POS Schema实践案例

## 📑 目录

- [POS Schema实践案例](#pos-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：销售交易处理系统](#2-案例1销售交易处理系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：支付处理系统](#3-案例2支付处理系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：GS1条码扫描和商品查询](#4-案例3gs1条码扫描和商品查询)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：交易对账系统](#5-案例4交易对账系统)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：POS数据分析和报表](#6-案例5pos数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供POS Schema在实际应用中的实践案例。

---

## 2. 案例1：销售交易处理系统

### 2.1 场景描述

**业务背景**：
零售门店需要处理销售交易，包括商品扫描、
交易记录、金额计算等，确保交易数据的准确性。

**技术挑战**：
- 需要GS1条码识别
- 需要实时交易处理
- 需要金额计算
- 需要交易数据存储

**解决方案**：
使用GS1BarcodeParser解析条码，使用POSStorage
存储交易数据，实现完整的销售交易处理。

### 2.2 Schema定义

**销售交易Schema**：

```json
{
  "sales_transaction": {
    "transaction_id": "TXN20250121001",
    "transaction_number": "TXN-2025-001",
    "transaction_info": {
      "store_id": "STORE001",
      "store_name": "门店A",
      "cashier_id": "CASHIER001",
      "cashier_name": "收银员A",
      "transaction_time": "2025-01-21T10:30:00Z",
      "terminal_id": "TERM001"
    },
    "product_info": {
      "items": [
        {
          "item_id": "ITEM001",
          "product_barcode": "6901234567890",
          "product_name": "商品A",
          "quantity": 2.0,
          "unit_price": 29.99,
          "subtotal": 59.98
        }
      ]
    },
    "transaction_amount": {
      "subtotal": 59.98,
      "total_discount": 0.0,
      "tax_amount": 5.40,
      "total_amount": 65.38
    }
  }
}
```

### 2.3 实现代码

**完整的销售交易处理实现**：

```python
from gs1_barcode_parser import GS1BarcodeParser
from product_info_query import ProductInfoQuery
from pos_storage import POSStorage
from datetime import datetime

# 初始化组件
storage = POSStorage("postgresql://user:pass@localhost/pos")
barcode_parser = GS1BarcodeParser()
product_query = ProductInfoQuery(None)

# 创建新交易
transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
transaction_number = f"TXN-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

transaction_data = {
    "transaction_id": transaction_id,
    "transaction_number": transaction_number,
    "transaction_info": {
        "store_id": "STORE001",
        "store_name": "门店A",
        "cashier_id": "CASHIER001",
        "cashier_name": "收银员A",
        "transaction_time": datetime.now(),
        "terminal_id": "TERM001"
    },
    "product_info": {
        "items": []
    },
    "transaction_status": {
        "status": "Pending",
        "payment_status": "Unpaid"
    },
    "transaction_amount": {
        "subtotal": 0.0,
        "total_discount": 0.0,
        "tax_amount": 0.0,
        "total_amount": 0.0
    }
}

# 扫描商品
scanned_barcodes = [
    "6901234567890",
    "6901234567890",
    "6901234567891"
]

for barcode in scanned_barcodes:
    # 解析条码
    parsed_barcode = barcode_parser.parse_barcode(barcode)
    print(f"Scanned barcode: {parsed_barcode['gtin']}")

    # 查询商品信息
    product_info = product_query.query_product_by_barcode(barcode)
    if product_info:
        # 添加到交易
        item_id = f"ITEM{len(transaction_data['product_info']['items']) + 1:03d}"
        item = {
            "item_id": item_id,
            "product_barcode": barcode,
            "product_name": product_info["product_name"],
            "quantity": 1.0,
            "unit_price": product_info["unit_price"],
            "discount_rate": 0.0,
            "discount_amount": 0.0,
            "subtotal": product_info["unit_price"]
        }
        transaction_data["product_info"]["items"].append(item)

        # 更新交易金额
        transaction_data["transaction_amount"]["subtotal"] += item["subtotal"]
        print(f"Added: {item['product_name']} - ${item['unit_price']:.2f}")

# 计算税费（假设税率10%）
tax_rate = 0.10
transaction_data["transaction_amount"]["tax_amount"] = \
    transaction_data["transaction_amount"]["subtotal"] * tax_rate
transaction_data["transaction_amount"]["total_amount"] = \
    transaction_data["transaction_amount"]["subtotal"] + \
    transaction_data["transaction_amount"]["tax_amount"]

print(f"\nTransaction Summary:")
print(f"  Subtotal: ${transaction_data['transaction_amount']['subtotal']:.2f}")
print(f"  Tax: ${transaction_data['transaction_amount']['tax_amount']:.2f}")
print(f"  Total: ${transaction_data['transaction_amount']['total_amount']:.2f}")

# 存储交易
storage.store_transaction(transaction_data)
print(f"\nStored transaction: {transaction_id}")
```

---

## 3. 案例2：支付处理系统

### 3.1 场景描述

**业务背景**：
零售门店需要处理多种支付方式，包括现金、
银行卡、移动支付等，确保支付安全和准确性。

**技术挑战**：
- 需要支持多种支付方式
- 需要支付安全处理
- 需要ISO 8583消息处理
- 需要支付对账

**解决方案**：
使用PaymentProcessor处理支付，使用
PaymentSecurityProcessor处理支付安全，使用
ISO8583Builder构建ISO 8583消息。

### 3.2 Schema定义

**支付处理Schema**：

```json
{
  "payment_processing": {
    "payment_id": "PAY20250121001",
    "transaction_id": "TXN20250121001",
    "payment_method": {
      "method_type": "Card",
      "card_type": "Credit",
      "card_brand": "Visa"
    },
    "payment_info": {
      "payment_amount": 65.38,
      "payment_time": "2025-01-21T10:35:00Z",
      "card_number_masked": "************1234",
      "authorization_code": "AUTH01"
    },
    "payment_result": {
      "result_code": "00",
      "result_message": "Payment authorized",
      "status": "Success"
    }
  }
}
```

### 3.3 实现代码

**完整的支付处理实现**：

```python
from payment_processor import PaymentProcessor
from payment_security_processor import PaymentSecurityProcessor
from pos_storage import POSStorage
from datetime import datetime

# 初始化组件
storage = POSStorage("postgresql://user:pass@localhost/pos")
payment_processor = PaymentProcessor()
security_processor = PaymentSecurityProcessor()

# 交易数据
transaction_id = "TXN20250121001"
total_amount = 65.38

# 支付方式选择
payment_methods = [
    {
        "method_type": "Cash",
        "paid_amount": 100.00
    },
    {
        "method_type": "Card",
        "card_number": "4111111111111234",
        "card_type": "Credit",
        "card_brand": "Visa",
        "expiry_date": "12/25"
    }
]

# 处理支付
for payment_method_data in payment_methods:
    payment_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}"

    payment_data = {
        "payment_id": payment_id,
        "transaction_id": transaction_id,
        "payment_method": {
            "method_type": payment_method_data["method_type"],
            "card_type": payment_method_data.get("card_type"),
            "card_brand": payment_method_data.get("card_brand")
        },
        "payment_info": {
            "payment_amount": total_amount,
            "payment_time": datetime.now(),
            "card_number_masked": security_processor.mask_card_number(
                payment_method_data.get("card_number", "")
            ) if payment_method_data.get("card_number") else None
        },
        "payment_security": {
            "encryption_method": "AES-256",
            "risk_score": 0.0,
            "fraud_detection": False
        },
        "payment_result": {
            "result_code": "",
            "result_message": "",
            "status": "Pending"
        },
        "terminal_id": "TERM001",
        "merchant_id": "MERCHANT001"
    }

    # 计算风险评分
    payment_data["payment_security"]["risk_score"] = \
        security_processor.calculate_risk_score(payment_data)
    payment_data["payment_security"]["fraud_detection"] = \
        security_processor.detect_fraud(payment_data)

    # 处理支付
    if not payment_data["payment_security"]["fraud_detection"]:
        result = payment_processor.process_payment(payment_data)
        payment_data["payment_result"] = result["result"]
        payment_data["payment_info"]["authorization_code"] = result.get("authorization_code")

        if result["result"]["status"] == "Success":
            print(f"\nPayment successful: {payment_method_data['method_type']}")
            print(f"  Authorization Code: {result.get('authorization_code', 'N/A')}")

            # 更新交易支付状态
            # 存储支付记录
            storage.store_payment(payment_data)

            # 如果是现金支付，计算找零
            if payment_method_data["method_type"] == "Cash":
                change = payment_method_data["paid_amount"] - total_amount
                print(f"  Change: ${change:.2f}")

            break
    else:
        print(f"\nFraud detected! Risk score: {payment_data['payment_security']['risk_score']:.2f}")
        payment_data["payment_result"] = {
            "result_code": "99",
            "result_message": "Fraud detected",
            "status": "Failed"
        }
        storage.store_payment(payment_data)
```

---

## 4. 案例3：GS1条码扫描和商品查询

### 4.1 场景描述

**业务背景**：
零售门店需要扫描商品条码，查询商品信息，
确保商品信息的准确性。

**技术挑战**：
- 需要GS1条码解析
- 需要商品信息查询
- 需要条码验证

**解决方案**：
使用GS1BarcodeParser解析条码，使用
ProductInfoQuery查询商品信息。

### 4.2 实现代码

**完整的GS1条码扫描实现**：

```python
from gs1_barcode_parser import GS1BarcodeParser
from product_info_query import ProductInfoQuery

# 初始化组件
barcode_parser = GS1BarcodeParser()
product_query = ProductInfoQuery(None)

# 扫描条码
barcodes = [
    "6901234567890",  # GTIN-13
    "123456789012",   # GTIN-12/UPC-A
    "12345678901234"  # GTIN-14
]

for barcode in barcodes:
    try:
        # 解析条码
        parsed = barcode_parser.parse_barcode(barcode)
        print(f"\nBarcode: {barcode}")
        print(f"  Format: {parsed['format']}")
        print(f"  GTIN: {parsed['gtin']}")
        print(f"  Valid: {parsed['is_valid']}")

        if parsed['is_valid']:
            # 查询商品信息
            product_info = product_query.query_product_by_barcode(barcode)
            if product_info:
                print(f"  Product Name: {product_info['product_name']}")
                print(f"  Unit Price: ${product_info['unit_price']:.2f}")
                print(f"  Stock: {product_info['stock_quantity']}")
            else:
                print(f"  Product not found in database")
        else:
            print(f"  Invalid barcode check digit")
    except ValueError as e:
        print(f"\nError parsing barcode {barcode}: {e}")
```

---

## 5. 案例4：交易对账系统

### 5.1 场景描述

**业务背景**：
零售门店需要对账，确保交易数据和支付数据
的一致性，发现异常交易。

**技术挑战**：
- 需要交易数据查询
- 需要支付数据查询
- 需要数据对比
- 需要异常检测

**解决方案**：
使用POSStorage查询交易和支付数据，实现
对账逻辑。

### 5.2 实现代码

**完整的交易对账实现**：

```python
from pos_storage import POSStorage
from datetime import datetime, timedelta

# 初始化存储
storage = POSStorage("postgresql://user:pass@localhost/pos")

# 对账日期
reconciliation_date = datetime.now().date()

# 查询交易数据
storage.cur.execute("""
    SELECT transaction_id, transaction_number, total_amount, payment_status
    FROM sales_transactions
    WHERE DATE(transaction_time) = %s
    ORDER BY transaction_time
""", (reconciliation_date,))

transactions = storage.cur.fetchall()

# 查询支付数据
storage.cur.execute("""
    SELECT transaction_id, payment_method, payment_amount, status
    FROM payment_records
    WHERE DATE(payment_time) = %s
    ORDER BY payment_time
""", (reconciliation_date,))

payments = storage.cur.fetchall()

# 创建支付字典
payment_dict = {}
for payment in payments:
    txn_id = payment[0]
    if txn_id not in payment_dict:
        payment_dict[txn_id] = []
    payment_dict[txn_id].append({
        "method": payment[1],
        "amount": float(payment[2]),
        "status": payment[3]
    })

# 对账处理
reconciliation_results = {
    "total_transactions": len(transactions),
    "matched_transactions": 0,
    "unmatched_transactions": [],
    "total_transaction_amount": 0.0,
    "total_payment_amount": 0.0,
    "difference": 0.0
}

for transaction in transactions:
    txn_id = transaction[0]
    txn_number = transaction[1]
    txn_amount = float(transaction[2])
    payment_status = transaction[3]

    reconciliation_results["total_transaction_amount"] += txn_amount

    # 检查支付记录
    if txn_id in payment_dict:
        payments_for_txn = payment_dict[txn_id]
        total_paid = sum(p["amount"] for p in payments_for_txn if p["status"] == "Success")

        reconciliation_results["total_payment_amount"] += total_paid

        if abs(total_paid - txn_amount) < 0.01:  # 允许0.01的误差
            reconciliation_results["matched_transactions"] += 1
        else:
            reconciliation_results["unmatched_transactions"].append({
                "transaction_id": txn_id,
                "transaction_number": txn_number,
                "transaction_amount": txn_amount,
                "paid_amount": total_paid,
                "difference": txn_amount - total_paid
            })
    else:
        if payment_status == "Paid":
            reconciliation_results["unmatched_transactions"].append({
                "transaction_id": txn_id,
                "transaction_number": txn_number,
                "transaction_amount": txn_amount,
                "paid_amount": 0.0,
                "difference": txn_amount,
                "issue": "No payment record found"
            })

# 计算差异
reconciliation_results["difference"] = \
    reconciliation_results["total_transaction_amount"] - \
    reconciliation_results["total_payment_amount"]

# 输出对账结果
print(f"\nReconciliation Report for {reconciliation_date}")
print(f"  Total Transactions: {reconciliation_results['total_transactions']}")
print(f"  Matched Transactions: {reconciliation_results['matched_transactions']}")
print(f"  Unmatched Transactions: {len(reconciliation_results['unmatched_transactions'])}")
print(f"  Total Transaction Amount: ${reconciliation_results['total_transaction_amount']:.2f}")
print(f"  Total Payment Amount: ${reconciliation_results['total_payment_amount']:.2f}")
print(f"  Difference: ${reconciliation_results['difference']:.2f}")

if reconciliation_results["unmatched_transactions"]:
    print(f"\nUnmatched Transactions:")
    for unmatched in reconciliation_results["unmatched_transactions"]:
        print(f"  {unmatched['transaction_number']}: "
              f"TXN=${unmatched['transaction_amount']:.2f}, "
              f"PAID=${unmatched['paid_amount']:.2f}, "
              f"DIFF=${unmatched['difference']:.2f}")
```

---

## 6. 案例5：POS数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储POS数据，支持数据查询、
分析和报表生成。

### 6.2 实现代码

**完整的数据分析实现**：

```python
from pos_storage import POSStorage

storage = POSStorage("postgresql://user:pass@localhost/pos")

# 查询销售统计
store_id = "STORE001"
sales_stats = storage.get_sales_statistics(store_id, days=30)
print("Sales Statistics (30 days):")
print(f"  Total Transactions: {sales_stats['total_transactions']}")
print(f"  Total Sales: ${sales_stats['total_sales']:.2f}")
print(f"  Avg Transaction Amount: ${sales_stats['avg_transaction_amount']:.2f}")
print(f"  Unique Customers: {sales_stats['unique_customers']}")

# 查询支付方式统计
payment_stats = storage.get_payment_method_statistics(days=30)
print(f"\nPayment Method Statistics (30 days):")
for method, stats in payment_stats.items():
    print(f"  {method}:")
    print(f"    Transactions: {stats['transaction_count']}")
    print(f"    Total Amount: ${stats['total_amount']:.2f}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
