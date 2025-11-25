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

**参考文档**：

- `01_Overview.md` - 概述
- `02_IoT_Schema_Characteristics.md` - IoT Schema特点
- `03_IoT_Standards_Analysis.md` - IoT标准分析
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
