# JSON Schema实践案例

## 📑 目录

- [JSON Schema实践案例](#json-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：API数据验证](#2-案例1api数据验证)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：表单验证](#3-案例2表单验证)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：OpenAPI集成](#4-案例3openapi集成)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：JSON Schema到GraphQL转换](#5-案例4json-schema到graphql转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：JSON Schema数据存储与分析系统](#6-案例5json-schema数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供JSON Schema在实际应用中的实践案例。

---

## 2. 案例1：API数据验证

### 2.1 场景描述

**应用场景**：
RESTful API使用JSON Schema进行请求和响应数据验证。

### 2.2 Schema定义

**API数据验证JSON Schema**：

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "email": {
      "type": "string",
      "format": "email"
    }
  },
  "required": ["id", "name"]
}
```

---

## 3. 案例2：表单验证

### 3.1 场景描述

**应用场景**：
Web表单使用JSON Schema进行客户端和服务器端验证。

### 3.2 Schema定义

**表单验证JSON Schema**：

```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_]{3,20}$"
    },
    "password": {
      "type": "string",
      "minLength": 8,
      "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)"
    }
  },
  "required": ["username", "password"]
}
```

---

## 4. 案例3：OpenAPI集成

### 4.1 场景描述

**应用场景**：
OpenAPI使用JSON Schema定义API请求和响应格式。

### 4.2 Schema定义

**OpenAPI JSON Schema**：

```json
{
  "openapi": "3.0.0",
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"}
        }
      }
    }
  }
}
```

---

## 5. 案例4：JSON Schema到GraphQL转换

### 5.1 场景描述

**应用场景**：
将JSON Schema转换为GraphQL Schema。

### 5.2 实现代码

**转换实现**：

```python
def json_schema_to_graphql(json_schema: dict) -> str:
    return convert_json_schema_to_graphql_types(json_schema)
```

---

## 6. 案例5：JSON Schema数据存储与分析系统

### 6.1 场景描述

**应用场景**：
存储JSON Schema定义和验证结果。

### 6.2 实现代码

**数据存储实现**：

```python
from json_schema_data_store import JSONSchemaDataStore

store = JSONSchemaDataStore(db_config)
schema_id = store.store_schema("UserSchema", json_schema_definition)
store.log_validation(schema_id, data_instance, is_valid, errors)
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
