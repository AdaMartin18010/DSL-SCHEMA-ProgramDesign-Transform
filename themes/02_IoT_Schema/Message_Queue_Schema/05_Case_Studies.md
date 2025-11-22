# 消息队列Schema实践案例

## 📑 目录

- [消息队列Schema实践案例](#消息队列schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：IoT传感器数据Kafka流处理](#2-案例1iot传感器数据kafka流处理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：MQTT到Kafka协议转换](#3-案例2mqtt到kafka协议转换)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：消息队列数据存储与分析系统](#4-案例3消息队列数据存储与分析系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)

---

## 1. 案例概述

本文档提供消息队列Schema在实际应用中的实践案例。

---

## 2. 案例1：IoT传感器数据Kafka流处理

### 2.1 场景描述

**应用场景**：
使用Kafka处理大规模IoT传感器数据流，
支持实时数据处理和分析。

**需求分析**：

- **数据量**：每秒10万条消息
- **延迟要求**：端到端延迟 < 100ms
- **可靠性**：至少一次传递保证
- **数据格式**：Avro格式

### 2.2 Schema定义

**Kafka主题Schema**：

```dsl
schema SensorDataTopic {
  topic_name: "sensor-data-stream"
  partitions: 10
  replication_factor: 3

  message: struct {
    device_id: String @required
    sensor_type: Enum { Temperature, Humidity, Pressure }
    value: Float @required
    timestamp: Timestamp @required @unit("ms")
    location: GeoPoint @optional
  }
} @format("Avro")
```

### 2.3 实现代码

**Kafka生产者**：

```python
from confluent_kafka import Producer
from avro.schema import parse
import avro.io
import io

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'retries': 3
})

schema = parse(open("sensor_schema.avsc").read())
writer = avro.io.DatumWriter(schema)

def produce_sensor_data(device_id: str, sensor_type: str, value: float):
    message = {
        "device_id": device_id,
        "sensor_type": sensor_type,
        "value": value,
        "timestamp": int(time.time() * 1000)
    }

    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer.write(message, encoder)

    producer.produce('sensor-data-stream', bytes_writer.getvalue())
    producer.flush()
```

---

## 3. 案例2：MQTT到Kafka协议转换

### 3.1 场景描述

**应用场景**：
将MQTT消息转换为Kafka消息，
实现IoT设备数据到大数据平台的集成。

### 3.2 Schema定义

**MQTT到Kafka转换Schema**：

```dsl
schema MQTTToKafkaBridge {
  mqtt: {
    topic: String @pattern("sensors/+/data")
    qos: Enum { 0, 1, 2 } @default(1)
  }

  kafka: {
    topic: "sensor-stream"
    partition_key: String @from("mqtt.topic.device_id")
  }

  transformation: {
    topic_mapping: Map<String, String] {
      "sensors/temperature/data": "temperature-stream"
      "sensors/humidity/data": "humidity-stream"
    }
  }
}
```

---

## 4. 案例3：消息队列数据存储与分析系统

### 4.1 场景描述

**应用场景**：
使用PostgreSQL存储MQTT和Kafka消息数据，
支持历史数据查询和统计分析。

### 4.2 实现代码

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
