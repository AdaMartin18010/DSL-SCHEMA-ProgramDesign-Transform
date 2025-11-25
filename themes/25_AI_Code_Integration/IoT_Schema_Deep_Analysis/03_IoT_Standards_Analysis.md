# IoT标准分析

## 📑 目录

- [IoT标准分析](#iot标准分析)
  - [📑 目录](#-目录)
  - [1. 通信协议标准](#1-通信协议标准)
    - [1.1 MQTT标准](#11-mqtt标准)
    - [1.2 CoAP标准](#12-coap标准)
    - [1.3 LoRaWAN标准](#13-lorawan标准)
  - [2. 数据格式标准](#2-数据格式标准)
    - [2.1 JSON Schema](#21-json-schema)
    - [2.2 Protocol Buffers](#22-protocol-buffers)
  - [3. 平台标准](#3-平台标准)
    - [3.1 AWS IoT Core](#31-aws-iot-core)
    - [3.2 Azure IoT Hub](#32-azure-iot-hub)
    - [3.3 OGC SensorThings API](#33-ogc-sensorthings-api)
  - [4. 标准对比](#4-标准对比)

---

## 1. 通信协议标准

### 1.1 MQTT标准

- **标准名称**：ISO/IEC 20922
- **版本**：MQTT 3.1.1、MQTT 5.0
- **应用场景**：物联网消息传输

### 1.2 CoAP标准

- **标准名称**：RFC 7252
- **版本**：CoAP 1.0
- **应用场景**：受限设备通信

### 1.3 LoRaWAN标准

- **标准名称**：LoRaWAN Specification
- **版本**：LoRaWAN 1.0、1.1
- **应用场景**：低功耗广域网

---

## 2. 数据格式标准

### 2.1 JSON Schema

- **标准名称**：JSON Schema Draft 7
- **应用场景**：JSON数据验证

### 2.2 Protocol Buffers

- **标准名称**：Google Protocol Buffers
- **应用场景**：高效数据序列化

---

## 3. 平台标准

### 3.1 AWS IoT Core

- **标准**：AWS IoT平台标准
- **功能**：设备管理、消息路由、规则引擎

### 3.2 Azure IoT Hub

- **标准**：Azure IoT平台标准
- **功能**：设备管理、消息路由、设备孪生

### 3.3 OGC SensorThings API

- **标准**：OGC SensorThings API 1.1
- **功能**：传感器数据API标准

---

## 4. 标准对比

| 标准 | 类型 | 应用场景 | 优势 |
|------|------|---------|------|
| **MQTT** | 通信协议 | 物联网消息传输 | 轻量级、低带宽 |
| **CoAP** | 通信协议 | 受限设备 | 低功耗、RESTful |
| **LoRaWAN** | 通信协议 | 广域网 | 长距离、低功耗 |
| **JSON Schema** | 数据格式 | 数据验证 | 标准化、易用 |
| **OGC SensorThings** | 平台标准 | 传感器API | 标准化、互操作 |

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_IoT_Schema_Characteristics.md` - IoT Schema特点
- `04_IoT_Transformation_Rules.md` - IoT转换规则
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
