# AsyncAPI Schema实践案例

## 📑 目录

- [AsyncAPI Schema实践案例](#asyncapi-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：事件驱动架构](#2-案例1事件驱动架构)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：Kafka消息定义](#3-案例2kafka消息定义)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：MQTT消息定义](#4-案例3mqtt消息定义)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：AsyncAPI到OpenAPI转换](#5-案例4asyncapi到openapi转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：AsyncAPI数据存储与分析系统](#6-案例5asyncapi数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供AsyncAPI Schema在实际应用中的实践案例。

---

## 2. 案例1：事件驱动架构

### 2.1 场景描述

**应用场景**：
事件驱动架构使用AsyncAPI定义事件接口。

### 2.2 Schema定义

**事件驱动AsyncAPI Schema**：

```yaml
asyncapi: 2.6.0
info:
  title: Event Service
  version: 1.0.0

channels:
  user/signedup:
    publish:
      message:
        $ref: '#/components/messages/UserSignedUp'

  order/created:
    publish:
      message:
        $ref: '#/components/messages/OrderCreated'

components:
  messages:
    UserSignedUp:
      payload:
        type: object
        properties:
          userId: { type: string }
          email: { type: string }
          timestamp: { type: string, format: date-time }
```

---

## 3. 案例2：Kafka消息定义

### 3.1 场景描述

**应用场景**：
Apache Kafka使用AsyncAPI定义消息格式。

### 3.2 Schema定义

**Kafka AsyncAPI Schema**：

```yaml
asyncapi: 2.6.0
info:
  title: Kafka Service
  version: 1.0.0

servers:
  production:
    url: kafka://broker.example.com:9092
    protocol: kafka

channels:
  user-events:
    publish:
      message:
        $ref: '#/components/messages/UserEvent'
      bindings:
        kafka:
          topic: user-events
          partition: 0
```

---

## 4. 案例3：MQTT消息定义

### 4.1 场景描述

**应用场景**：
MQTT使用AsyncAPI定义消息格式。

### 4.2 Schema定义

**MQTT AsyncAPI Schema**：

```yaml
asyncapi: 2.6.0
info:
  title: MQTT Service
  version: 1.0.0

servers:
  production:
    url: mqtt://broker.example.com:1883
    protocol: mqtt

channels:
  sensor/data:
    subscribe:
      message:
        $ref: '#/components/messages/SensorData'
      bindings:
        mqtt:
          qos: 1
          retain: false
```

---

## 5. 案例4：AsyncAPI到OpenAPI转换

### 5.1 场景描述

**应用场景**：
将AsyncAPI规范转换为OpenAPI规范。

### 5.2 实现代码

**转换实现**：

```python
def asyncapi_to_openapi(asyncapi_spec: dict) -> dict:
    return convert_asyncapi_to_openapi(asyncapi_spec)
```

---

## 6. 案例5：AsyncAPI数据存储与分析系统

### 6.1 场景描述

**应用场景**：
存储AsyncAPI Schema定义和消息实例。

### 6.2 实现代码

**数据存储实现**：

```python
from asyncapi_data_store import AsyncAPIDataStore

store = AsyncAPIDataStore(db_config)
schema_id = store.store_schema("EventService", asyncapi_spec)
store.store_message(channel_id, message_data, message_type)
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
