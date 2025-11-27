# 网络管理Schema转换体系

## 📑 目录

- [网络管理Schema转换体系](#网络管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. SNMP到NETCONF转换](#2-snmp到netconf转换)
  - [3. PostgreSQL网络管理数据存储](#3-postgresql网络管理数据存储)

---

## 1. 转换体系概述

网络管理Schema转换体系支持SNMP、NETCONF、YANG、数据库存储之间的转换。

### 1.1 转换目标

1. **SNMP到NETCONF转换**：SNMP MIB到NETCONF配置
2. **YANG到NETCONF转换**：YANG模型到NETCONF配置
3. **数据到数据库转换**：网络管理数据到PostgreSQL存储

---

## 2. SNMP到NETCONF转换

**完整的SNMP到NETCONF转换实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

logger = logging.getLogger(__name__)

class SNMPToNETCONFConverter:
    """SNMP到NETCONF转换器"""

    def convert_mib_to_netconf(self, mib_data: Dict) -> str:
        """将SNMP MIB转换为NETCONF XML配置"""
        root = Element("config")
        root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")

        # 创建设备配置
        device_elem = SubElement(root, "device")
        device_elem.set("id", mib_data.get("device_id", ""))

        # 转换MIB对象
        for oid, value in mib_data.get("mib_objects", {}).items():
            oid_elem = SubElement(device_elem, "oid")
            oid_elem.set("value", oid)
            oid_elem.text = str(value)

        return tostring(root, encoding='unicode')
```

---

## 3. PostgreSQL网络管理数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NetworkManagementStorage:
    """网络管理数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 网络设备表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS network_devices (
                device_id VARCHAR(50) PRIMARY KEY,
                device_name VARCHAR(200) NOT NULL,
                device_type VARCHAR(50),
                ip_address VARCHAR(50),
                snmp_community VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # SNMP数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS snmp_data (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(50) REFERENCES network_devices(device_id),
                oid VARCHAR(200) NOT NULL,
                value TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_snmp_device_time ON snmp_data(device_id, timestamp)")
        self.conn.commit()

    def store_device(self, device_id: str, device_name: str,
                    device_type: str = None, ip_address: str = None,
                    snmp_community: str = None) -> Optional[str]:
        """存储网络设备"""
        if not device_id or not device_name:
            raise ValueError("Device ID and device name are required")

        try:
            self.cur.execute("""
                INSERT INTO network_devices (
                    device_id, device_name, device_type, ip_address, snmp_community
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (device_id) DO UPDATE SET
                    device_name = EXCLUDED.device_name,
                    device_type = EXCLUDED.device_type,
                    ip_address = EXCLUDED.ip_address,
                    snmp_community = EXCLUDED.snmp_community
                RETURNING device_id
            """, (device_id, device_name, device_type, ip_address, snmp_community))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored network device: {device_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing device: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def store_snmp_data(self, device_id: str, oid: str, value: str) -> Optional[int]:
        """存储SNMP数据"""
        if not device_id or not oid:
            raise ValueError("Device ID and OID are required")

        try:
            self.cur.execute("""
                INSERT INTO snmp_data (device_id, oid, value)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (device_id, oid, value))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored SNMP data: {device_id} - {oid}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing SNMP data: {e}")
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
