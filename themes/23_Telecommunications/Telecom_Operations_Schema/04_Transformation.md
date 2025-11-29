# 电信运营Schema转换体系

## 📑 目录

- [电信运营Schema转换体系](#电信运营schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. eTOM到TM Forum转换](#2-etom到tm-forum转换)
  - [3. PostgreSQL电信运营数据存储](#3-postgresql电信运营数据存储)

---

## 1. 转换体系概述

电信运营Schema转换体系支持eTOM、ITIL、TM Forum、数据库存储之间的转换。

### 1.1 转换目标

1. **eTOM到TM Forum转换**：eTOM流程到TM Forum API
2. **数据到数据库转换**：电信运营数据到PostgreSQL存储

---

## 2. eTOM到TM Forum转换

**完整的eTOM到TM Forum转换实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class eTOMToTMFConverter:
    """eTOM到TM Forum转换器"""

    def convert_service_order(self, etom_order: Dict) -> Dict:
        """将eTOM服务订单转换为TM Forum格式"""
        tmf_order = {
            "id": etom_order.get("service_order_id", ""),
            "category": "serviceOrder",
            "state": self._convert_order_status(etom_order.get("order_status", "")),
            "orderDate": datetime.now().isoformat(),
            "orderItem": [{
                "id": etom_order.get("service_order_id", ""),
                "action": "add",
                "service": {
                    "id": etom_order.get("service_id", ""),
                    "name": etom_order.get("service_name", "")
                }
            }]
        }
        return tmf_order

    def _convert_order_status(self, status: str) -> str:
        """转换订单状态"""
        status_map = {
            "Pending": "acknowledged",
            "InProgress": "inProgress",
            "Completed": "completed",
            "Cancelled": "cancelled"
        }
        return status_map.get(status, "acknowledged")
```

---

## 3. PostgreSQL电信运营数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelecomOperationsStorage:
    """电信运营数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 服务订单表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS service_orders (
                service_order_id VARCHAR(50) PRIMARY KEY,
                service_type VARCHAR(50) NOT NULL,
                customer_id VARCHAR(50) NOT NULL,
                order_status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 客户表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(200) NOT NULL,
                customer_type VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def store_service_order(self, service_order_id: str, service_type: str,
                           customer_id: str, order_status: str) -> Optional[str]:
        """存储服务订单"""
        if not service_order_id or not service_type or not customer_id:
            raise ValueError("Service order ID, service type, and customer ID are required")

        try:
            self.cur.execute("""
                INSERT INTO service_orders (
                    service_order_id, service_type, customer_id, order_status
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (service_order_id) DO UPDATE SET
                    service_type = EXCLUDED.service_type,
                    customer_id = EXCLUDED.customer_id,
                    order_status = EXCLUDED.order_status
                RETURNING service_order_id
            """, (service_order_id, service_type, customer_id, order_status))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored service order: {service_order_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing service order: {e}")
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
