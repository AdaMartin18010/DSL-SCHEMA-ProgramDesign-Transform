# 消息队列Schema转换体系

## 📑 目录

- [消息队列Schema转换体系](#消息队列schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 协议转换](#2-协议转换)
    - [2.1 MQTT到Kafka转换](#21-mqtt到kafka转换)
    - [2.2 Kafka到MQTT转换](#22-kafka到mqtt转换)
    - [2.3 AMQP转换](#23-amqp转换)
  - [3. 消息格式转换](#3-消息格式转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 消息队列数据存储与分析](#6-消息队列数据存储与分析)
    - [6.1 PostgreSQL消息队列数据存储](#61-postgresql消息队列数据存储)
    - [6.2 消息队列数据分析查询](#62-消息队列数据分析查询)

---

## 1. 转换体系概述

消息队列Schema转换体系支持MQTT、Kafka、AMQP等协议之间的转换。

### 1.1 转换目标

1. **协议转换**：MQTT ↔ Kafka, MQTT ↔ AMQP
2. **消息格式转换**：JSON ↔ Avro, Binary ↔ Protobuf
3. **主题映射**：MQTT主题 ↔ Kafka主题

---

## 2. 协议转换

### 2.1 MQTT到Kafka转换

**转换规则**：

- MQTT主题 → Kafka主题
- MQTT消息负载 → Kafka消息值
- MQTT QoS → Kafka acks配置

### 2.2 Kafka到MQTT转换

**转换规则**：

- Kafka主题 → MQTT主题
- Kafka消息值 → MQTT消息负载
- Kafka分区键 → MQTT主题后缀

### 2.3 AMQP转换

**转换规则**：

- AMQP Exchange → MQTT/Kafka主题
- AMQP Queue → Kafka消费者组
- AMQP Routing Key → 主题模式

---

## 3. 消息格式转换

支持JSON、Avro、Protobuf、Binary等格式之间的转换。

---

## 4. 转换工具

- **Kafka Connect**：Kafka连接器
- **MQTT Bridge**：MQTT桥接工具
- **Protocol Gateway**：协议网关

---

## 5. 转换验证

验证转换的语义等价性、性能和可靠性。

---

## 6. 消息队列数据存储与分析

### 6.1 PostgreSQL消息队列数据存储

**消息队列数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class KafkaMessage:
    """Kafka消息"""
    topic: str
    partition: int
    offset: int
    key: Optional[bytes]
    value: bytes
    timestamp: datetime
    headers: Dict[str, bytes] = None

class MessageQueueStorage:
    """消息队列数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建消息队列数据表"""
        # MQTT消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mqtt_messages (
                id BIGSERIAL PRIMARY KEY,
                topic VARCHAR(500) NOT NULL,
                payload BYTEA NOT NULL,
                payload_text TEXT,
                qos INTEGER NOT NULL,
                retain BOOLEAN DEFAULT FALSE,
                client_id VARCHAR(200),
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Kafka消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS kafka_messages (
                id BIGSERIAL PRIMARY KEY,
                topic VARCHAR(500) NOT NULL,
                partition INTEGER NOT NULL,
                offset BIGINT NOT NULL,
                message_key BYTEA,
                message_value BYTEA NOT NULL,
                message_value_text TEXT,
                headers JSONB,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(topic, partition, offset)
            )
        """)

        # 主题定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS topic_definitions (
                id SERIAL PRIMARY KEY,
                topic_name VARCHAR(500) UNIQUE NOT NULL,
                protocol_type VARCHAR(50) NOT NULL,
                definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 消息统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS message_statistics (
                id SERIAL PRIMARY KEY,
                topic_name VARCHAR(500) NOT NULL,
                protocol_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(topic_name, protocol_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mqtt_topic_time
            ON mqtt_messages(topic, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_kafka_topic_partition_offset
            ON kafka_messages(topic, partition, offset DESC)
        """)

        self.conn.commit()

    def store_mqtt_message(self, topic: str, payload: bytes,
                          qos: int, retain: bool, timestamp: datetime,
                          client_id: str = None):
        """存储MQTT消息"""
        payload_text = payload.decode('utf-8', errors='ignore')
        self.cur.execute("""
            INSERT INTO mqtt_messages
            (topic, payload, payload_text, qos, retain, client_id, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (topic, payload, payload_text, qos, retain, client_id, timestamp))
        self.conn.commit()

    def store_kafka_message(self, message: KafkaMessage):
        """存储Kafka消息"""
        value_text = message.value.decode('utf-8', errors='ignore')
        headers_json = json.dumps({k: v.hex() for k, v in (message.headers or {}).items()})
        self.cur.execute("""
            INSERT INTO kafka_messages
            (topic, partition, offset, message_key, message_value,
             message_value_text, headers, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (topic, partition, offset) DO NOTHING
        """, (message.topic, message.partition, message.offset,
              message.key, message.value, value_text, headers_json,
              message.timestamp))
        self.conn.commit()

    def query_topic_messages(self, topic: str, protocol: str,
                            start_time: datetime, end_time: datetime,
                            limit: int = 1000):
        """查询主题消息"""
        if protocol == "MQTT":
            self.cur.execute("""
                SELECT topic, payload_text, qos, timestamp
                FROM mqtt_messages
                WHERE topic = %s AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (topic, start_time, end_time, limit))
        elif protocol == "Kafka":
            self.cur.execute("""
                SELECT topic, partition, offset, message_value_text, timestamp
                FROM kafka_messages
                WHERE topic = %s AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (topic, start_time, end_time, limit))
        return self.cur.fetchall()

    def calculate_statistics(self, topic: str, protocol: str,
                            time_window: datetime):
        """计算统计信息"""
        if protocol == "MQTT":
            self.cur.execute("""
                SELECT
                    COUNT(*) as message_count,
                    COUNT(DISTINCT client_id) as client_count,
                    AVG(LENGTH(payload)) as avg_payload_size
                FROM mqtt_messages
                WHERE topic = %s AND timestamp >= %s
            """, (topic, time_window))
        elif protocol == "Kafka":
            self.cur.execute("""
                SELECT
                    COUNT(*) as message_count,
                    COUNT(DISTINCT partition) as partition_count,
                    MAX(offset) - MIN(offset) as offset_range,
                    AVG(LENGTH(message_value)) as avg_value_size
                FROM kafka_messages
                WHERE topic = %s AND timestamp >= %s
            """, (topic, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO message_statistics
            (topic_name, protocol_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (topic_name, protocol_type, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, (topic, protocol, time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 消息队列数据分析查询

**查询示例**：

```python
# 查询MQTT主题消息流量
storage.query_topic_messages(
    topic="sensors/temperature",
    protocol="MQTT",
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now()
)

# 计算Kafka主题统计信息
stats = storage.calculate_statistics(
    topic="sensor-stream",
    protocol="Kafka",
    time_window=datetime.now() - timedelta(hours=1)
)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
