# 消费者追溯Schema转换体系

## 📑 目录

- [消费者追溯Schema转换体系](#消费者追溯schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GS1到EPCIS转换](#2-gs1到epcis转换)
  - [3. PostgreSQL消费者追溯数据存储](#3-postgresql消费者追溯数据存储)

---

## 1. 转换体系概述

消费者追溯Schema转换体系支持GS1标准、EPCIS事件、数据库存储之间的转换。

### 1.1 转换目标

1. **GS1到EPCIS转换**：GS1产品信息到EPCIS事件
2. **数据到数据库转换**：消费者追溯数据到PostgreSQL存储

---

## 2. GS1到EPCIS转换

**完整的GS1到EPCIS转换实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GS1ToEPCISConverter:
    """GS1到EPCIS转换器"""

    def convert_product_to_object_event(self, product_info: Dict) -> Dict:
        """将产品信息转换为EPCIS ObjectEvent"""
        epcis_event = {
            "eventTime": datetime.now().isoformat(),
            "eventTimeZoneOffset": "+00:00",
            "eventType": "ObjectEvent",
            "epcList": [product_info.get("gtin", "")],
            "action": "ADD",
            "bizStep": "producing",
            "disposition": "in_progress"
        }
        return epcis_event
```

---

## 3. PostgreSQL消费者追溯数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConsumerTraceabilityStorage:
    """消费者追溯数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 产品表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(50) PRIMARY KEY,
                gtin VARCHAR(20) UNIQUE NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                batch_number VARCHAR(50),
                production_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 追溯链表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS traceability_chains (
                chain_id VARCHAR(50) PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES products(product_id),
                chain_status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 消费者查询表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS consumer_queries (
                query_id VARCHAR(50) PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES products(product_id),
                query_type VARCHAR(50) NOT NULL,
                query_time TIMESTAMP NOT NULL,
                query_result JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def store_product(self, product_id: str, gtin: str, product_name: str,
                     batch_number: str = None, production_date: datetime = None) -> Optional[str]:
        """存储产品信息"""
        if not product_id or not gtin or not product_name:
            raise ValueError("Product ID, GTIN, and product name are required")

        try:
            self.cur.execute("""
                INSERT INTO products (
                    product_id, gtin, product_name, batch_number, production_date
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    gtin = EXCLUDED.gtin,
                    product_name = EXCLUDED.product_name,
                    batch_number = EXCLUDED.batch_number,
                    production_date = EXCLUDED.production_date
                RETURNING product_id
            """, (product_id, gtin, product_name, batch_number, production_date))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored product: {product_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing product: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
