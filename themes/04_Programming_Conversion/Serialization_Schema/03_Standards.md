# 序列化Schema标准对标

## 📑 目录

- [序列化Schema标准对标](#序列化schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. ASN.1标准](#2-asn1标准)
    - [2.1 ISO/IEC 8824-1:2015](#21-isoiec-8824-12015)
    - [2.2 ISO/IEC 8825-1:2015](#22-isoiec-8825-12015)
  - [3. Protocol Buffers标准](#3-protocol-buffers标准)
  - [4. 其他序列化标准](#4-其他序列化标准)
    - [4.1 Apache Avro](#41-apache-avro)
    - [4.2 MessagePack](#42-messagepack)
    - [4.3 CBOR](#43-cbor)
  - [5. 标准对比矩阵](#5-标准对比矩阵)

---

## 1. 标准体系概述

序列化Schema标准体系分为三个层次：

1. **国际标准**：ISO/IEC ASN.1标准
2. **行业标准**：Protocol Buffers、Avro等
3. **社区标准**：MessagePack、CBOR等

---

## 2. ASN.1标准

### 2.1 ISO/IEC 8824-1:2015

**标准名称**：Information technology - Abstract Syntax Notation One (ASN.1)

**核心内容**：

- **类型定义**：基本类型、构造类型、标签类型
- **模块系统**：模块定义和导入
- **约束**：SIZE、FROM、WITH COMPONENT等
- **标签**：APPLICATION、PRIVATE、CONTEXT-SPECIFIC

**Schema支持**：完整支持

**状态**：ISO/IEC标准

### 2.2 ISO/IEC 8825-1:2015

**标准名称**：Information technology - ASN.1 encoding rules

**核心内容**：

- **BER**：Basic Encoding Rules
- **DER**：Distinguished Encoding Rules
- **PER**：Packed Encoding Rules
- **XER**：XML Encoding Rules
- **CER**：Canonical Encoding Rules

**Schema支持**：完整支持

**状态**：ISO/IEC标准

---

## 3. Protocol Buffers标准

**标准名称**：Protocol Buffers 3.x

**核心内容**：

- **消息定义**：message关键字
- **字段类型**：标量类型、枚举、嵌套消息
- **字段编号**：唯一字段编号（1-536870911）
- **编码格式**：Varint、ZigZag、固定长度、长度分隔

**Schema支持**：完整支持

**状态**：Google标准

---

## 4. 其他序列化标准

### 4.1 Apache Avro

**标准名称**：Apache Avro

**核心内容**：

- **Schema定义**：JSON格式Schema
- **Schema演进**：Schema版本兼容性
- **编码格式**：二进制编码、JSON编码

**Schema支持**：完整支持

**状态**：Apache基金会标准

### 4.2 MessagePack

**标准名称**：MessagePack

**核心内容**：

- **二进制JSON**：紧凑二进制格式
- **类型系统**：支持JSON类型

**Schema支持**：基本支持

**状态**：社区标准

### 4.3 CBOR

**标准名称**：RFC 8949 - Concise Binary Object Representation

**核心内容**：

- **二进制格式**：紧凑二进制表示
- **类型系统**：支持JSON类型和扩展类型

**Schema支持**：基本支持

**状态**：IETF标准

---

## 5. 标准对比矩阵

| 标准 | 组织 | Schema支持 | 状态 | 应用场景 |
|------|------|-----------|------|---------|
| **ASN.1** | ISO/IEC | ⭐⭐⭐⭐⭐ | 标准 | 网络协议、电信 |
| **Protocol Buffers** | Google | ⭐⭐⭐⭐⭐ | 标准 | RPC、数据交换 |
| **Apache Avro** | Apache | ⭐⭐⭐⭐⭐ | 活跃 | Kafka、大数据 |
| **MessagePack** | 社区 | ⭐⭐⭐ | 活跃 | 高性能序列化 |
| **CBOR** | IETF | ⭐⭐⭐⭐ | 标准 | IoT、Web |

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
