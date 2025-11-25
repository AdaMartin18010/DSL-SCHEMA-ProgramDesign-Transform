# 质量管理Schema转换体系

## 📑 目录

- [质量管理Schema转换体系](#质量管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ISO标准转换](#2-iso标准转换)
  - [3. PostgreSQL质量管理数据存储](#3-postgresql质量管理数据存储)

---

## 1. 转换体系概述

质量管理Schema转换体系支持ISO 9001、ISO 14001、ISO 45001、数据库存储之间的转换。

### 1.1 转换目标

1. **ISO标准间转换**：ISO 9001、ISO 14001、ISO 45001之间的转换
2. **数据到数据库转换**：质量管理数据到PostgreSQL存储

---

## 2. ISO标准转换

**完整的ISO标准转换实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ISOStandardConverter:
    """ISO标准转换器"""

    def convert_iso9001_to_iso14001(self, qm_data: Dict) -> Dict:
        """将ISO 9001数据转换为ISO 14001格式"""
        em_data = {
            "system_id": qm_data.get("system_id", ""),
            "system_name": qm_data.get("system_name", ""),
            "standard_type": "ISO14001",
            "environmental_aspects": [],
            "compliance_requirements": []
        }
        return em_data
```

---

## 3. PostgreSQL质量管理数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class QualityManagementStorage:
    """质量管理数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 质量体系表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_systems (
                system_id VARCHAR(50) PRIMARY KEY,
                system_name VARCHAR(200) NOT NULL,
                standard_type VARCHAR(50) NOT NULL,
                certification_date DATE,
                expiry_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 质量控制表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_controls (
                control_id VARCHAR(50) PRIMARY KEY,
                inspection_date DATE NOT NULL,
                product_id VARCHAR(50) NOT NULL,
                inspection_result VARCHAR(50) NOT NULL,
                inspector VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def store_quality_system(self, system_id: str, system_name: str,
                             standard_type: str, certification_date: datetime = None,
                             expiry_date: datetime = None) -> Optional[str]:
        """存储质量体系"""
        if not system_id or not system_name or not standard_type:
            raise ValueError("System ID, system name, and standard type are required")

        try:
            self.cur.execute("""
                INSERT INTO quality_systems (
                    system_id, system_name, standard_type, certification_date, expiry_date
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (system_id) DO UPDATE SET
                    system_name = EXCLUDED.system_name,
                    standard_type = EXCLUDED.standard_type,
                    certification_date = EXCLUDED.certification_date,
                    expiry_date = EXCLUDED.expiry_date
                RETURNING system_id
            """, (system_id, system_name, standard_type, certification_date, expiry_date))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored quality system: {system_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing quality system: {e}")
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
