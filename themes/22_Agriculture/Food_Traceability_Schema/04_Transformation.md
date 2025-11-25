# 农产品追溯Schema转换体系

## 📑 目录

- [农产品追溯Schema转换体系](#农产品追溯schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GS1到EPCIS转换实现](#2-gs1到epcis转换实现)
  - [3. PostgreSQL农产品追溯数据存储](#3-postgresql农产品追溯数据存储)

---

## 1. 转换体系概述

农产品追溯Schema转换体系支持GS1标准、EPCIS事件、数据库存储之间的转换。

### 1.1 转换目标

1. **GS1到EPCIS转换**：GS1产品信息到EPCIS事件
2. **数据到数据库转换**：农产品追溯数据到PostgreSQL存储

---

## 2. GS1到EPCIS转换实现

**完整的GS1到EPCIS转换实现**：

```python
import logging
from typing import Dict, List, Optional
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
            "disposition": "in_progress",
            "readPoint": {
                "id": product_info.get("farm_location", "")
            },
            "bizLocation": {
                "id": product_info.get("farm_gln", "")
            }
        }
        return epcis_event

    def convert_traceability_chain_to_epcis(self, traceability_chain: Dict) -> List[Dict]:
        """将追溯链转换为EPCIS事件列表"""
        events = []
        for event in traceability_chain.get("chain_events", []):
            epcis_event = self._convert_event_to_epcis(event)
            if epcis_event:
                events.append(epcis_event)
        return events

    def _convert_event_to_epcis(self, event: Dict) -> Optional[Dict]:
        """转换单个事件到EPCIS格式"""
        event_type_map = {
            "Production": "ObjectEvent",
            "Processing": "TransformationEvent",
            "Transportation": "TransactionEvent",
            "Storage": "AggregationEvent",
            "Retail": "TransactionEvent"
        }

        epcis_type = event_type_map.get(event.get("event_type", ""))
        if not epcis_type:
            return None

        return {
            "eventTime": event.get("event_time", datetime.now().isoformat()),
            "eventType": epcis_type,
            "bizStep": event.get("event_type", "").lower(),
            "readPoint": {"id": event.get("event_location", "")}
        }
```

---

## 3. PostgreSQL农产品追溯数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FoodTraceabilityStorage:
    """农产品追溯数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 产品信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(50) PRIMARY KEY,
                gtin VARCHAR(20) UNIQUE NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                product_type VARCHAR(50),
                batch_number VARCHAR(50),
                production_date DATE,
                expiry_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 生产信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS production_info (
                production_id VARCHAR(50) PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES products(product_id),
                farm_id VARCHAR(50),
                farm_name VARCHAR(200),
                harvest_date DATE,
                production_method VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 追溯事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS traceability_events (
                event_id VARCHAR(50) PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES products(product_id),
                event_type VARCHAR(50) NOT NULL,
                event_time TIMESTAMP NOT NULL,
                event_location VARCHAR(200),
                event_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_traceability_events_product ON traceability_events(product_id, event_time)")
        self.conn.commit()

    def store_product(self, product_id: str, gtin: str, product_name: str,
                     product_type: str = None, batch_number: str = None,
                     production_date: datetime = None, expiry_date: datetime = None) -> Optional[str]:
        """存储产品信息"""
        if not product_id or not gtin or not product_name:
            raise ValueError("Product ID, GTIN, and product name are required")

        try:
            self.cur.execute("""
                INSERT INTO products (
                    product_id, gtin, product_name, product_type,
                    batch_number, production_date, expiry_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    gtin = EXCLUDED.gtin,
                    product_name = EXCLUDED.product_name,
                    product_type = EXCLUDED.product_type,
                    batch_number = EXCLUDED.batch_number,
                    production_date = EXCLUDED.production_date,
                    expiry_date = EXCLUDED.expiry_date
                RETURNING product_id
            """, (product_id, gtin, product_name, product_type,
                  batch_number, production_date, expiry_date))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored product: {product_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing product: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def store_traceability_event(self, event_id: str, product_id: str,
                                event_type: str, event_time: datetime,
                                event_location: str = None,
                                event_data: Dict = None) -> Optional[str]:
        """存储追溯事件"""
        if not event_id or not product_id or not event_type or not event_time:
            raise ValueError("Event ID, product ID, event type, and event time are required")

        try:
            import json
            event_data_json = json.dumps(event_data) if event_data else None

            self.cur.execute("""
                INSERT INTO traceability_events (
                    event_id, product_id, event_type, event_time,
                    event_location, event_data
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO UPDATE SET
                    product_id = EXCLUDED.product_id,
                    event_type = EXCLUDED.event_type,
                    event_time = EXCLUDED.event_time,
                    event_location = EXCLUDED.event_location,
                    event_data = EXCLUDED.event_data
                RETURNING event_id
            """, (event_id, product_id, event_type, event_time,
                  event_location, event_data_json))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored traceability event: {event_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing traceability event: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def get_traceability_chain(self, product_id: str) -> List[Dict]:
        """查询产品追溯链"""
        try:
            self.cur.execute("""
                SELECT event_id, event_type, event_time, event_location, event_data
                FROM traceability_events
                WHERE product_id = %s
                ORDER BY event_time ASC
            """, (product_id,))
            columns = [desc[0] for desc in self.cur.description]
            results = []
            for row in self.cur.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except psycopg2.Error as e:
            logger.error(f"Database error querying traceability chain: {e}")
            raise RuntimeError(f"Database query failed: {e}") from e

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
