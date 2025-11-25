# 农业物联网Schema标准对标

## 📑 目录

- [农业物联网Schema标准对标](#农业物联网schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. LoRaWAN标准](#2-lorawan标准)
    - [2.1 LoRaWAN概述](#21-lorawan概述)
  - [3. MQTT标准](#3-mqtt标准)
    - [3.1 MQTT概述](#31-mqtt概述)
  - [4. CoAP标准](#4-coap标准)
    - [4.1 CoAP概述](#41-coap概述)
  - [5. OGC SensorThings标准](#5-ogc-sensorthings标准)
    - [5.1 OGC SensorThings概述](#51-ogc-sensorthings概述)
  - [6. 标准对比矩阵](#6-标准对比矩阵)

---

## 1. 标准体系概述

农业物联网Schema标准体系分为四个层次：

1. **LoRaWAN标准**：低功耗广域网
2. **MQTT标准**：消息队列协议
3. **CoAP标准**：受限应用协议
4. **OGC SensorThings标准**：传感器API

---

## 2. LoRaWAN标准

### 2.1 LoRaWAN概述

**标准名称**：LoRaWAN Specification

**核心内容**：

- **设备标识**：DevEUI、AppEUI、AppKey
- **通信参数**：频率、扩频因子、带宽
- **数据格式**：LoRaWAN数据包格式

**Schema支持**：完整支持

**参考链接**：[LoRa Alliance官网](https://lora-alliance.org/)

---

## 3. MQTT标准

### 3.1 MQTT概述

**标准名称**：MQTT (Message Queuing Telemetry Transport)

**核心内容**：

- **消息格式**：MQTT消息格式
- **主题结构**：MQTT主题命名
- **QoS级别**：消息质量等级

**Schema支持**：完整支持

---

## 4. CoAP标准

### 4.1 CoAP概述

**标准名称**：Constrained Application Protocol (CoAP)

**核心内容**：

- **RESTful API**：基于REST的API设计
- **资源模型**：CoAP资源模型
- **消息格式**：CoAP消息格式

**Schema支持**：完整支持

---

## 5. OGC SensorThings标准

### 5.1 OGC SensorThings概述

**标准名称**：OGC SensorThings API

**核心内容**：

- **Things**：物联网设备
- **Observations**：观测数据
- **Datastreams**：数据流

**Schema支持**：完整支持

---

## 6. 标准对比矩阵

| 标准 | 应用场景 | 通信距离 | 功耗 | Schema支持 |
|------|---------|---------|------|-----------|
| **LoRaWAN** | 广域网 | 1-15km | 低 | ✅ 完整支持 |
| **MQTT** | 物联网 | 不限 | 中 | ✅ 完整支持 |
| **CoAP** | 受限设备 | 不限 | 低 | ✅ 完整支持 |
| **OGC SensorThings** | 传感器API | 不限 | - | ✅ 完整支持 |

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
