# IoT转换规则

## 📑 目录

- [IoT转换规则](#iot转换规则)
  - [📑 目录](#-目录)
  - [1. IoT到OpenAPI转换规则](#1-iot到openapi转换规则)
    - [1.1 设备协议到RESTful API](#11-设备协议到restful-api)
    - [1.2 传感器数据到JSON格式](#12-传感器数据到json格式)
  - [2. IoT到AsyncAPI转换规则](#2-iot到asyncapi转换规则)
    - [2.1 设备事件到消息队列](#21-设备事件到消息队列)
  - [3. 协议间转换规则](#3-协议间转换规则)
    - [3.1 MQTT到CoAP转换](#31-mqtt到coap转换)
  - [6. 数据库存储与分析](#6-数据库存储与分析)
    - [6.1 PostgreSQL数据存储](#61-postgresql数据存储)
    - [6.2 数据分析查询示例](#62-数据分析查询示例)

---

## 1. IoT到OpenAPI转换规则

### 1.1 设备协议到RESTful API

**转换规则**：

- MQTT主题 → RESTful API路径
- MQTT消息 → API请求/响应体
- 设备ID → API资源ID

### 1.2 传感器数据到JSON格式

**转换规则**：

- 二进制数据 → JSON对象
- 时间戳 → ISO 8601格式
- 单位信息 → JSON Schema单位定义

---

## 2. IoT到AsyncAPI转换规则

### 2.1 设备事件到消息队列

**转换规则**：

- 设备事件 → AsyncAPI消息
- MQTT主题 → AsyncAPI通道
- 设备状态变更 → AsyncAPI事件

---

## 3. 协议间转换规则

### 3.1 MQTT到CoAP转换

**转换规则**：

- MQTT主题 → CoAP资源路径
- MQTT消息 → CoAP请求/响应
- MQTT QoS → CoAP确认机制

---

## 6. 数据库存储与分析

### 6.1 PostgreSQL数据存储

**表结构设计**：

```sql
-- IoT转换规则表
CREATE TABLE iot_conversion_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(200) UNIQUE NOT NULL,
    source_protocol VARCHAR(50) NOT NULL,  -- MQTT, CoAP, HTTP
    target_protocol VARCHAR(50) NOT NULL,  -- OpenAPI, AsyncAPI
    conversion_type VARCHAR(50),  -- Protocol, Data, Event
    rule_definition JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IoT设备转换记录表
CREATE TABLE iot_device_conversions (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(200) NOT NULL,
    rule_id INTEGER REFERENCES iot_conversion_rules(id),
    source_data JSONB,
    target_data JSONB,
    conversion_status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_iot_rules_source_target ON iot_conversion_rules(source_protocol, target_protocol);
CREATE INDEX idx_iot_conversions_device_id ON iot_device_conversions(device_id);
CREATE INDEX idx_iot_conversions_rule_id ON iot_device_conversions(rule_id);
```

**Python存储实现**：

```python
import psycopg2
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IoTSchemaConversionStorage:
    """IoT Schema转换数据存储类"""

    def __init__(self, db_config: Dict[str, Any]):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建表结构"""
        # IoT转换规则表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iot_conversion_rules (
                id SERIAL PRIMARY KEY,
                rule_name VARCHAR(200) UNIQUE NOT NULL,
                source_protocol VARCHAR(50) NOT NULL,
                target_protocol VARCHAR(50) NOT NULL,
                conversion_type VARCHAR(50),
                rule_definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # IoT设备转换记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS iot_device_conversions (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                rule_id INTEGER REFERENCES iot_conversion_rules(id),
                source_data JSONB,
                target_data JSONB,
                conversion_status VARCHAR(20) DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iot_rules_source_target
            ON iot_conversion_rules(source_protocol, target_protocol)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iot_conversions_device_id
            ON iot_device_conversions(device_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iot_conversions_rule_id
            ON iot_device_conversions(rule_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_iot_conversions_status
            ON iot_device_conversions(conversion_status, created_at DESC)
        """)

        self.conn.commit()

    def store_conversion_rule(self, rule_name: str, source_protocol: str,
                             target_protocol: str, conversion_type: str,
                             rule_definition: Dict) -> int:
        """存储IoT转换规则"""
        try:
            self.cur.execute("""
                INSERT INTO iot_conversion_rules
                (rule_name, source_protocol, target_protocol,
                 conversion_type, rule_definition)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (rule_name) DO UPDATE
                SET source_protocol = EXCLUDED.source_protocol,
                    target_protocol = EXCLUDED.target_protocol,
                    conversion_type = EXCLUDED.conversion_type,
                    rule_definition = EXCLUDED.rule_definition,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (rule_name, source_protocol, target_protocol,
                  conversion_type, json.dumps(rule_definition)))
            rule_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored conversion rule: {rule_name} (ID: {rule_id})")
            return rule_id
        except Exception as e:
            logger.error(f"Failed to store conversion rule: {e}")
            self.conn.rollback()
            raise

    def store_device_conversion(self, device_id: str, rule_id: int,
                               source_data: Dict, target_data: Optional[Dict] = None,
                               conversion_status: str = 'PENDING') -> int:
        """存储IoT设备转换记录"""
        try:
            self.cur.execute("""
                INSERT INTO iot_device_conversions
                (device_id, rule_id, source_data, target_data, conversion_status)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                RETURNING id
            """, (device_id, rule_id, json.dumps(source_data),
                  json.dumps(target_data) if target_data else None, conversion_status))
            conversion_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored device conversion: {conversion_id}")
            return conversion_id
        except Exception as e:
            logger.error(f"Failed to store device conversion: {e}")
            self.conn.rollback()
            raise

    def get_conversion_statistics(self) -> Dict:
        """获取转换统计信息"""
        try:
            self.cur.execute("""
                SELECT
                    source_protocol,
                    target_protocol,
                    COUNT(DISTINCT icr.id) as rule_count,
                    COUNT(idc.id) as conversion_count,
                    COUNT(CASE WHEN idc.conversion_status = 'COMPLETED' THEN 1 END) as completed_count
                FROM iot_conversion_rules icr
                LEFT JOIN iot_device_conversions idc ON icr.id = idc.rule_id
                GROUP BY source_protocol, target_protocol
                ORDER BY rule_count DESC
            """)
            results = []
            for row in self.cur.fetchall():
                results.append({
                    'source_protocol': row[0],
                    'target_protocol': row[1],
                    'rule_count': row[2],
                    'conversion_count': row[3],
                    'completed_count': row[4]
                })
            return {'by_protocol': results}
        except Exception as e:
            logger.error(f"Failed to get conversion statistics: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 数据分析查询示例

**查询转换规则统计**：

```python
# 按协议类型统计转换规则
storage.cur.execute("""
    SELECT source_protocol, target_protocol, COUNT(*) as count
    FROM iot_conversion_rules
    GROUP BY source_protocol, target_protocol
    ORDER BY count DESC
""")
```

**查询设备转换成功率**：

```python
# 查询设备转换成功率
storage.cur.execute("""
    SELECT
        device_id,
        COUNT(*) as total_conversions,
        COUNT(CASE WHEN conversion_status = 'COMPLETED' THEN 1 END) as completed,
        ROUND(100.0 * COUNT(CASE WHEN conversion_status = 'COMPLETED' THEN 1 END) / COUNT(*), 2) as success_rate
    FROM iot_device_conversions
    GROUP BY device_id
    HAVING COUNT(*) > 0
    ORDER BY success_rate DESC
""")
```

**查询转换类型分布**：

```python
# 查询转换类型分布
storage.cur.execute("""
    SELECT
        conversion_type,
        COUNT(*) as rule_count,
        COUNT(DISTINCT source_protocol) as source_protocol_count,
        COUNT(DISTINCT target_protocol) as target_protocol_count
    FROM iot_conversion_rules
    GROUP BY conversion_type
    ORDER BY rule_count DESC
""")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - IoT Schema特点
- `03_Standards.md` - IoT标准分析
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
