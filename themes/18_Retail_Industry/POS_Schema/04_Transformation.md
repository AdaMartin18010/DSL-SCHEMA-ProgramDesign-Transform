# POS Schema转换体系

## 📑 目录

- [POS Schema转换体系](#pos-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GS1条码解析实现](#2-gs1条码解析实现)
    - [2.1 GS1条码解析器](#21-gs1条码解析器)
    - [2.2 商品信息查询](#22-商品信息查询)
  - [3. ISO 8583消息处理实现](#3-iso-8583消息处理实现)
    - [3.1 ISO 8583消息解析器](#31-iso-8583消息解析器)
    - [3.2 ISO 8583消息构建器](#32-iso-8583消息构建器)
  - [4. 支付处理实现](#4-支付处理实现)
    - [4.1 支付处理器](#41-支付处理器)
    - [4.2 支付安全处理](#42-支付安全处理)
  - [5. POS数据存储与分析](#5-pos数据存储与分析)
    - [5.1 PostgreSQL POS数据存储](#51-postgresql-pos数据存储)
    - [5.2 POS数据分析查询](#52-pos数据分析查询)

---

## 1. 转换体系概述

POS Schema转换体系支持GS1条码、ISO 8583消息、
支付处理、数据库存储之间的转换。

### 1.1 转换目标

1. **GS1条码解析**：GS1条码到商品信息
2. **ISO 8583消息处理**：ISO 8583消息解析和构建
3. **支付处理**：多种支付方式处理
4. **数据到数据库转换**：POS数据到PostgreSQL存储

---

## 2. GS1条码解析实现

### 2.1 GS1条码解析器

**完整的GS1条码解析实现**：

```python
import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class GS1BarcodeParser:
    """GS1条码解析器"""

    def __init__(self):
        # GTIN-13/EAN-13格式：13位数字
        self.gtin13_pattern = re.compile(r'^[0-9]{13}$')
        # GTIN-12/UPC-A格式：12位数字
        self.gtin12_pattern = re.compile(r'^[0-9]{12}$')
        # GTIN-14格式：14位数字
        self.gtin14_pattern = re.compile(r'^[0-9]{14}$')

    def parse_barcode(self, barcode: str) -> Dict:
        """解析GS1条码"""
        barcode = barcode.strip()

        if self.gtin13_pattern.match(barcode):
            return self._parse_gtin13(barcode)
        elif self.gtin12_pattern.match(barcode):
            return self._parse_gtin12(barcode)
        elif self.gtin14_pattern.match(barcode):
            return self._parse_gtin14(barcode)
        else:
            raise ValueError(f"Invalid GS1 barcode format: {barcode}")

    def _parse_gtin13(self, barcode: str) -> Dict:
        """解析GTIN-13/EAN-13条码"""
        return {
            "barcode": barcode,
            "format": "GTIN-13",
            "gtin": barcode,
            "country_code": barcode[:3],
            "manufacturer_code": barcode[3:7],
            "product_code": barcode[7:12],
            "check_digit": barcode[12],
            "is_valid": self._validate_check_digit(barcode)
        }

    def _parse_gtin12(self, barcode: str) -> Dict:
        """解析GTIN-12/UPC-A条码"""
        # 补零到13位
        gtin13 = "0" + barcode
        return self._parse_gtin13(gtin13)

    def _parse_gtin14(self, barcode: str) -> Dict:
        """解析GTIN-14条码"""
        return {
            "barcode": barcode,
            "format": "GTIN-14",
            "gtin": barcode,
            "indicator": barcode[0],
            "gtin13": barcode[1:],
            "is_valid": self._validate_check_digit(barcode)
        }

    def _validate_check_digit(self, barcode: str) -> bool:
        """验证校验位"""
        if len(barcode) < 13:
            return False

        digits = [int(d) for d in barcode[:-1]]
        check_digit = int(barcode[-1])

        # 计算校验位
        total = sum(digits[i] * (3 if i % 2 == 1 else 1) for i in range(len(digits)))
        calculated_check = (10 - (total % 10)) % 10

        return calculated_check == check_digit
```

### 2.2 商品信息查询

**商品信息查询实现**：

```python
class ProductInfoQuery:
    """商品信息查询"""

    def __init__(self, db_connection):
        self.db = db_connection

    def query_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """根据条码查询商品信息"""
        parser = GS1BarcodeParser()
        parsed = parser.parse_barcode(barcode)

        # 查询数据库
        query = """
            SELECT product_id, product_name, unit_price,
                   category, brand, stock_quantity
            FROM products
            WHERE barcode = %s OR gtin = %s
        """

        # 执行查询（示例代码）
        # result = self.db.execute(query, (barcode, parsed['gtin']))
        # return result.fetchone() if result else None

        # 模拟返回
        return {
            "product_id": "PROD001",
            "product_name": "示例商品",
            "unit_price": 29.99,
            "category": "食品",
            "brand": "品牌A",
            "stock_quantity": 100
        }
```

---

## 3. ISO 8583消息处理实现

### 3.1 ISO 8583消息解析器

**完整的ISO 8583消息解析实现**：

```python
import struct
from typing import Dict, List, Optional

class ISO8583Parser:
    """ISO 8583消息解析器"""

    def __init__(self):
        # 字段定义（简化版）
        self.field_definitions = {
            2: {"type": "LLVAR", "max_length": 19, "name": "Primary Account Number"},
            3: {"type": "FIXED", "length": 6, "name": "Processing Code"},
            4: {"type": "FIXED", "length": 12, "name": "Amount"},
            7: {"type": "FIXED", "length": 10, "name": "Transmission Date/Time"},
            11: {"type": "FIXED", "length": 6, "name": "System Trace Audit Number"},
            12: {"type": "FIXED", "length": 12, "name": "Local Transaction Time"},
            13: {"type": "FIXED", "length": 4, "name": "Local Transaction Date"},
            37: {"type": "FIXED", "length": 12, "name": "Retrieval Reference Number"},
            38: {"type": "FIXED", "length": 6, "name": "Authorization Code"},
            39: {"type": "FIXED", "length": 2, "name": "Response Code"},
            41: {"type": "FIXED", "length": 8, "name": "Terminal ID"},
            42: {"type": "FIXED", "length": 15, "name": "Merchant ID"}
        }

    def parse_message(self, message_bytes: bytes) -> Dict:
        """解析ISO 8583消息"""
        offset = 0

        # 解析消息长度（前2字节）
        message_length = struct.unpack('>H', message_bytes[0:2])[0]
        offset += 2

        # 解析MTI（4字节）
        mti = message_bytes[offset:offset+4].decode('ascii')
        offset += 4

        # 解析位图（16字节）
        bitmap = message_bytes[offset:offset+16]
        offset += 16

        # 解析字段
        fields = {}
        for field_num in range(1, 129):
            byte_index = (field_num - 1) // 8
            bit_index = 7 - ((field_num - 1) % 8)

            if bitmap[byte_index] & (1 << bit_index):
                if field_num in self.field_definitions:
                    field_def = self.field_definitions[field_num]
                    field_value, offset = self._parse_field(
                        message_bytes, offset, field_num, field_def
                    )
                    fields[field_num] = {
                        "name": field_def["name"],
                        "value": field_value
                    }

        return {
            "message_length": message_length,
            "mti": mti,
            "bitmap": bitmap.hex(),
            "fields": fields
        }

    def _parse_field(self, message_bytes: bytes, offset: int,
                    field_num: int, field_def: Dict) -> tuple:
        """解析字段"""
        if field_def["type"] == "FIXED":
            length = field_def["length"]
            value = message_bytes[offset:offset+length].decode('ascii')
            return value, offset + length
        elif field_def["type"] == "LLVAR":
            length_bytes = message_bytes[offset:offset+2]
            length = int(length_bytes.decode('ascii'))
            offset += 2
            value = message_bytes[offset:offset+length].decode('ascii')
            return value, offset + length
        else:
            raise ValueError(f"Unknown field type: {field_def['type']}")
```

### 3.2 ISO 8583消息构建器

**ISO 8583消息构建器实现**：

```python
class ISO8583Builder:
    """ISO 8583消息构建器"""

    def __init__(self):
        self.parser = ISO8583Parser()

    def build_purchase_message(self, pan: str, amount: str,
                              terminal_id: str, merchant_id: str) -> bytes:
        """构建购买消息"""
        mti = "0200"  # Financial transaction request
        fields = {
            2: pan,  # Primary Account Number
            3: "000000",  # Processing Code (Purchase)
            4: amount.zfill(12),  # Amount
            7: self._get_transmission_datetime(),  # Transmission Date/Time
            11: self._generate_stan(),  # System Trace Audit Number
            12: self._get_local_time(),  # Local Transaction Time
            13: self._get_local_date(),  # Local Transaction Date
            41: terminal_id.ljust(8),  # Terminal ID
            42: merchant_id.ljust(15)  # Merchant ID
        }

        return self._build_message(mti, fields)

    def _build_message(self, mti: str, fields: Dict) -> bytes:
        """构建消息"""
        # 构建位图
        bitmap = bytearray(16)
        for field_num in fields.keys():
            byte_index = (field_num - 1) // 8
            bit_index = 7 - ((field_num - 1) % 8)
            bitmap[byte_index] |= (1 << bit_index)

        # 构建消息体
        message_body = bytearray()
        for field_num in sorted(fields.keys()):
            field_def = self.parser.field_definitions.get(field_num)
            if field_def:
                if field_def["type"] == "FIXED":
                    message_body.extend(fields[field_num].encode('ascii'))
                elif field_def["type"] == "LLVAR":
                    value = fields[field_num]
                    length_str = f"{len(value):02d}"
                    message_body.extend(length_str.encode('ascii'))
                    message_body.extend(value.encode('ascii'))

        # 构建完整消息
        message = bytearray()
        message.extend(struct.pack('>H', len(mti) + 16 + len(message_body)))
        message.extend(mti.encode('ascii'))
        message.extend(bitmap)
        message.extend(message_body)

        return bytes(message)

    def _get_transmission_datetime(self) -> str:
        """获取传输日期时间"""
        from datetime import datetime
        return datetime.now().strftime("%m%d%H%M%S")

    def _get_local_time(self) -> str:
        """获取本地时间"""
        from datetime import datetime
        return datetime.now().strftime("%H%M%S")

    def _get_local_date(self) -> str:
        """获取本地日期"""
        from datetime import datetime
        return datetime.now().strftime("%m%d")

    def _generate_stan(self) -> str:
        """生成系统跟踪审计号"""
        import random
        return f"{random.randint(100000, 999999)}"
```

---

## 4. 支付处理实现

### 4.1 支付处理器

**完整的支付处理实现**：

```python
from typing import Dict, Optional
from datetime import datetime
import hashlib

class PaymentProcessor:
    """支付处理器"""

    def __init__(self):
        self.iso8583_builder = ISO8583Builder()
        self.iso8583_parser = ISO8583Parser()

    def process_payment(self, payment_data: Dict) -> Dict:
        """处理支付"""
        payment_method = payment_data.get("payment_method", {}).get("method_type")

        if payment_method == "Cash":
            return self._process_cash_payment(payment_data)
        elif payment_method == "Card":
            return self._process_card_payment(payment_data)
        elif payment_method == "Mobile":
            return self._process_mobile_payment(payment_data)
        else:
            return {
                "payment_id": payment_data.get("payment_id"),
                "result": {
                    "result_code": "99",
                    "result_message": "Unsupported payment method",
                    "status": "Failed"
                }
            }

    def _process_cash_payment(self, payment_data: Dict) -> Dict:
        """处理现金支付"""
        payment_amount = payment_data.get("payment_info", {}).get("payment_amount", 0)
        paid_amount = payment_data.get("paid_amount", 0)

        if paid_amount >= payment_amount:
            return {
                "payment_id": payment_data.get("payment_id"),
                "result": {
                    "result_code": "00",
                    "result_message": "Payment successful",
                    "status": "Success"
                },
                "change_amount": paid_amount - payment_amount
            }
        else:
            return {
                "payment_id": payment_data.get("payment_id"),
                "result": {
                    "result_code": "51",
                    "result_message": "Insufficient funds",
                    "status": "Failed"
                }
            }

    def _process_card_payment(self, payment_data: Dict) -> Dict:
        """处理银行卡支付"""
        # 构建ISO 8583消息
        pan = payment_data.get("payment_info", {}).get("card_number_masked", "").replace(" ", "")
        amount = str(int(payment_data.get("payment_info", {}).get("payment_amount", 0) * 100))
        terminal_id = payment_data.get("terminal_id", "00000001")
        merchant_id = payment_data.get("merchant_id", "000000000000001")

        iso8583_msg = self.iso8583_builder.build_purchase_message(
            pan, amount, terminal_id, merchant_id
        )

        # 发送到支付网关（模拟）
        # response = self._send_to_gateway(iso8583_msg)
        # parsed_response = self.iso8583_parser.parse_message(response)

        # 模拟响应
        parsed_response = {
            "fields": {
                38: {"value": "AUTH01"},  # Authorization Code
                39: {"value": "00"}  # Response Code (Success)
            }
        }

        response_code = parsed_response["fields"].get(39, {}).get("value", "99")

        if response_code == "00":
            return {
                "payment_id": payment_data.get("payment_id"),
                "result": {
                    "result_code": "00",
                    "result_message": "Payment authorized",
                    "status": "Success"
                },
                "authorization_code": parsed_response["fields"].get(38, {}).get("value")
            }
        else:
            return {
                "payment_id": payment_data.get("payment_id"),
                "result": {
                    "result_code": response_code,
                    "result_message": "Payment failed",
                    "status": "Failed"
                }
            }

    def _process_mobile_payment(self, payment_data: Dict) -> Dict:
        """处理移动支付"""
        # 移动支付处理逻辑（简化版）
        return {
            "payment_id": payment_data.get("payment_id"),
            "result": {
                "result_code": "00",
                "result_message": "Mobile payment successful",
                "status": "Success"
            }
        }
```

### 4.2 支付安全处理

**支付安全处理实现**：

```python
class PaymentSecurityProcessor:
    """支付安全处理器"""

    def __init__(self):
        pass

    def mask_card_number(self, card_number: str) -> str:
        """掩码卡号"""
        if len(card_number) < 4:
            return "****"
        return "*" * (len(card_number) - 4) + card_number[-4:]

    def calculate_risk_score(self, payment_data: Dict) -> float:
        """计算风险评分"""
        risk_score = 0.0

        # 金额风险
        amount = payment_data.get("payment_info", {}).get("payment_amount", 0)
        if amount > 10000:
            risk_score += 30.0
        elif amount > 5000:
            risk_score += 15.0

        # 时间风险（深夜交易）
        payment_time = payment_data.get("payment_info", {}).get("payment_time")
        if payment_time:
            hour = payment_time.hour
            if hour < 6 or hour > 23:
                risk_score += 20.0

        return min(risk_score, 100.0)

    def detect_fraud(self, payment_data: Dict) -> bool:
        """检测欺诈"""
        risk_score = self.calculate_risk_score(payment_data)
        return risk_score > 70.0
```

---

## 5. POS数据存储与分析

### 5.1 PostgreSQL POS数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
from typing import Dict, List, Optional
from datetime import datetime

class POSStorage:
    """POS数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建POS数据表"""
        # 销售交易表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sales_transactions (
                id BIGSERIAL PRIMARY KEY,
                transaction_id VARCHAR(20) UNIQUE NOT NULL,
                transaction_number VARCHAR(50) UNIQUE NOT NULL,
                store_id VARCHAR(50) NOT NULL,
                store_name VARCHAR(200),
                cashier_id VARCHAR(50) NOT NULL,
                cashier_name VARCHAR(100),
                transaction_time TIMESTAMP NOT NULL,
                terminal_id VARCHAR(50) NOT NULL,
                customer_id VARCHAR(50),
                status VARCHAR(20) NOT NULL,
                payment_status VARCHAR(20) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                total_discount DECIMAL(10,2) DEFAULT 0.0,
                tax_amount DECIMAL(10,2) DEFAULT 0.0,
                total_amount DECIMAL(10,2) NOT NULL,
                paid_amount DECIMAL(10,2) DEFAULT 0.0,
                change_amount DECIMAL(10,2) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 交易明细表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transaction_items (
                id BIGSERIAL PRIMARY KEY,
                item_id VARCHAR(20) UNIQUE NOT NULL,
                transaction_id VARCHAR(20) NOT NULL,
                product_barcode VARCHAR(50) NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                quantity DECIMAL(10,3) NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                discount_rate DECIMAL(5,2) DEFAULT 0.0,
                discount_amount DECIMAL(10,2) DEFAULT 0.0,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES sales_transactions(transaction_id)
            )
        """)

        # 支付记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_records (
                id BIGSERIAL PRIMARY KEY,
                payment_id VARCHAR(20) UNIQUE NOT NULL,
                transaction_id VARCHAR(20) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                payment_amount DECIMAL(10,2) NOT NULL,
                payment_time TIMESTAMP NOT NULL,
                authorization_code VARCHAR(50),
                result_code VARCHAR(10) NOT NULL,
                result_message VARCHAR(200),
                status VARCHAR(20) NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES sales_transactions(transaction_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_transactions_store_time
            ON sales_transactions(store_id, transaction_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_items_transaction_id
            ON transaction_items(transaction_id)
        """)

        self.conn.commit()

    def store_transaction(self, transaction_data: Dict) -> int:
        """存储销售交易"""
        self.cur.execute("""
            INSERT INTO sales_transactions (
                transaction_id, transaction_number, store_id, store_name,
                cashier_id, cashier_name, transaction_time, terminal_id,
                customer_id, status, payment_status, subtotal, total_discount,
                tax_amount, total_amount, paid_amount, change_amount
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            transaction_data.get("transaction_id"),
            transaction_data.get("transaction_number"),
            transaction_data.get("transaction_info", {}).get("store_id"),
            transaction_data.get("transaction_info", {}).get("store_name"),
            transaction_data.get("transaction_info", {}).get("cashier_id"),
            transaction_data.get("transaction_info", {}).get("cashier_name"),
            transaction_data.get("transaction_info", {}).get("transaction_time"),
            transaction_data.get("transaction_info", {}).get("terminal_id"),
            transaction_data.get("transaction_info", {}).get("customer_id"),
            transaction_data.get("transaction_status", {}).get("status"),
            transaction_data.get("transaction_status", {}).get("payment_status"),
            transaction_data.get("transaction_amount", {}).get("subtotal"),
            transaction_data.get("transaction_amount", {}).get("total_discount"),
            transaction_data.get("transaction_amount", {}).get("tax_amount"),
            transaction_data.get("transaction_amount", {}).get("total_amount"),
            transaction_data.get("transaction_amount", {}).get("paid_amount"),
            transaction_data.get("transaction_amount", {}).get("change_amount")
        ))
        self.conn.commit()
        transaction_id = self.cur.fetchone()[0]

        # 存储交易明细
        for item in transaction_data.get("product_info", {}).get("items", []):
            self.cur.execute("""
                INSERT INTO transaction_items (
                    item_id, transaction_id, product_barcode, product_name,
                    quantity, unit_price, discount_rate, discount_amount, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("item_id"),
                transaction_data.get("transaction_id"),
                item.get("product_barcode"),
                item.get("product_name"),
                item.get("quantity"),
                item.get("unit_price"),
                item.get("discount_rate"),
                item.get("discount_amount"),
                item.get("subtotal")
            ))
        self.conn.commit()

        return transaction_id

    def store_payment(self, payment_data: Dict) -> int:
        """存储支付记录"""
        self.cur.execute("""
            INSERT INTO payment_records (
                payment_id, transaction_id, payment_method, payment_amount,
                payment_time, authorization_code, result_code, result_message, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            payment_data.get("payment_id"),
            payment_data.get("transaction_id"),
            payment_data.get("payment_method", {}).get("method_type"),
            payment_data.get("payment_info", {}).get("payment_amount"),
            payment_data.get("payment_info", {}).get("payment_time"),
            payment_data.get("payment_info", {}).get("authorization_code"),
            payment_data.get("payment_result", {}).get("result_code"),
            payment_data.get("payment_result", {}).get("result_message"),
            payment_data.get("payment_result", {}).get("status")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 5.2 POS数据分析查询

**数据分析查询实现**：

```python
    def get_sales_statistics(self, store_id: str, days: int = 30) -> Dict:
        """查询销售统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_transactions,
                SUM(total_amount) as total_sales,
                AVG(total_amount) as avg_transaction_amount,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM sales_transactions
            WHERE store_id = %s
            AND transaction_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (store_id, days))
        row = self.cur.fetchone()
        return {
            "total_transactions": row[0],
            "total_sales": float(row[1]) if row[1] else 0.0,
            "avg_transaction_amount": float(row[2]) if row[2] else 0.0,
            "unique_customers": row[3]
        }

    def get_payment_method_statistics(self, days: int = 30) -> Dict:
        """查询支付方式统计"""
        self.cur.execute("""
            SELECT
                payment_method,
                COUNT(*) as transaction_count,
                SUM(payment_amount) as total_amount
            FROM payment_records
            WHERE payment_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY payment_method
        """, (days,))
        results = self.cur.fetchall()
        return {
            method: {
                "transaction_count": count,
                "total_amount": float(amount)
            }
            for method, count, amount in results
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
