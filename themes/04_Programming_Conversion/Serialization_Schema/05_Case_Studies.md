# 序列化Schema实践案例

## 📑 目录

- [序列化Schema实践案例](#序列化schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：ASN.1在SNMP协议中的应用](#2-案例1asn1在snmp协议中的应用)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：Protocol Buffers在gRPC中的应用](#3-案例2protocol-buffers在grpc中的应用)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：序列化格式转换](#4-案例3序列化格式转换)
    - [4.1 场景描述](#41-场景描述)

---

## 1. 案例概述

本文档提供序列化Schema在实际应用中的实践案例。

---

## 2. 案例1：ASN.1在SNMP协议中的应用

### 2.1 场景描述

**应用场景**：
使用ASN.1定义SNMP协议消息格式。

### 2.2 Schema定义

**SNMP ASN.1 Schema**：

```asn1
SNMP-MESSAGE DEFINITIONS ::= BEGIN

SNMPMessage ::= SEQUENCE {
    version INTEGER,
    community OCTET STRING,
    data PDU
}

PDU ::= CHOICE {
    get-request GetRequestPDU,
    get-next-request GetNextRequestPDU,
    get-response GetResponsePDU,
    set-request SetRequestPDU,
    trap TrapPDU
}

END
```

---

## 3. 案例2：Protocol Buffers在gRPC中的应用

### 3.1 场景描述

**应用场景**：
使用Protocol Buffers定义gRPC服务接口。

### 3.2 Schema定义

**gRPC Protobuf Schema**：

```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
}

message GetUserRequest {
  string user_id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}
```

---

## 4. 案例3：序列化格式转换

### 4.1 场景描述

**应用场景**：
将ASN.1 Schema转换为Protocol Buffers Schema。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
