# API参考文档

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🎯 快速导航

- [API参考文档](#api参考文档)
  - [📋 文档信息](#-文档信息)
  - [🎯 快速导航](#-快速导航)
  - [🔗 统一API网关](#-统一api网关)
    - [接口列表](#接口列表)
  - [1. 多模态知识图谱API](#1-多模态知识图谱api)
    - [1.1 添加实体](#11-添加实体)
    - [1.2 相似实体搜索](#12-相似实体搜索)
  - [2. 时序知识图谱API](#2-时序知识图谱api)
    - [2.1 添加实体](#21-添加实体)
    - [2.2 查询演化历史](#22-查询演化历史)
  - [3. LLM推理引擎API](#3-llm推理引擎api)
    - [3.1 执行推理](#31-执行推理)
  - [4. 统一Schema语言API](#4-统一schema语言api)
    - [4.1 解析USL](#41-解析usl)
    - [4.2 验证USL](#42-验证usl)
  - [5. 层次化知识表示API](#5-层次化知识表示api)
    - [5.1 添加实体](#51-添加实体)
    - [5.2 层次化推理](#52-层次化推理)
  - [6. 知识链方法API](#6-知识链方法api)
    - [6.1 构建知识链](#61-构建知识链)
  - [7. 可解释性推理API](#7-可解释性推理api)
    - [7.1 可解释性推理](#71-可解释性推理)
  - [8. Schema版本管理API](#8-schema版本管理api)
    - [8.1 创建版本](#81-创建版本)
    - [8.2 检查兼容性](#82-检查兼容性)

---

## 🔗 统一API网关

**地址**：`http://localhost:8080`

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 根路径（服务列表） |
| GET | `/api/v1/health` | 健康检查（所有服务） |
| GET | `/api/v1/services` | 列出所有服务 |
| * | `/api/v1/{service_name}/{path}` | 代理请求到指定服务 |

---

## 1. 多模态知识图谱API

**服务地址**：`http://localhost:8000`
**网关路径**：`/api/v1/multimodal_kg/`

### 1.1 添加实体

```http
POST /api/v1/multimodal_kg/entity/add
Content-Type: application/json

{
  "entity_id": "schema_001",
  "entity_type": "schema",
  "text_content": "Payment schema",
  "text_type": "schema_doc"
}
```

### 1.2 相似实体搜索

```http
POST /api/v1/multimodal_kg/search/similar
Content-Type: application/json

{
  "query": "payment",
  "top_k": 5
}
```

---

## 2. 时序知识图谱API

**服务地址**：`http://localhost:8001`
**网关路径**：`/api/v1/temporal_kg/`

### 2.1 添加实体

```http
POST /api/v1/temporal_kg/entity/add
Content-Type: application/json

{
  "entity_id": "schema_001",
  "entity_type": "schema",
  "valid_from": "2025-01-01T00:00:00",
  "properties": {"version": "1.0"}
}
```

### 2.2 查询演化历史

```http
GET /api/v1/temporal_kg/evolution/{entity_id}
```

---

## 3. LLM推理引擎API

**服务地址**：`http://localhost:8002`
**网关路径**：`/api/v1/llm_reasoning/`

### 3.1 执行推理

```http
POST /api/v1/llm_reasoning/reason
Content-Type: application/json

{
  "query": "What is a schema?",
  "context": {
    "entities": [],
    "relations": []
  }
}
```

---

## 4. 统一Schema语言API

**服务地址**：`http://localhost:8003`
**网关路径**：`/api/v1/usl/`

### 4.1 解析USL

```http
POST /api/v1/usl/parse
Content-Type: application/json

{
  "usl_code": "schema PaymentSchema { field amount: Decimal { required: true } }"
}
```

### 4.2 验证USL

```http
POST /api/v1/usl/validate
Content-Type: application/json

{
  "usl_code": "schema PaymentSchema { field amount: Decimal { required: true } }"
}
```

---

## 5. 层次化知识表示API

**服务地址**：`http://localhost:8004`
**网关路径**：`/api/v1/hierarchical_kg/`

### 5.1 添加实体

```http
POST /api/v1/hierarchical_kg/entity/add
Content-Type: application/json

{
  "entity_id": "instance_001",
  "name": "Payment Instance",
  "level": 1,
  "content": {"type": "schema_instance"}
}
```

### 5.2 层次化推理

```http
POST /api/v1/hierarchical_kg/reasoning
Content-Type: application/json

{
  "entity_id": "instance_001",
  "reasoning_type": "bottom_up"
}
```

---

## 6. 知识链方法API

**服务地址**：`http://localhost:8005`
**网关路径**：`/api/v1/knowledge-chain/`

### 6.1 构建知识链

```http
POST /api/v1/knowledge-chain/build
Content-Type: application/json

{
  "schema_doc": {
    "entities": [{"id": 1, "name": "Entity1"}],
    "relations": []
  },
  "chain_name": "Test Chain"
}
```

---

## 7. 可解释性推理API

**服务地址**：`http://localhost:8006`
**网关路径**：`/api/v1/explainable-reasoning/`

### 7.1 可解释性推理

```http
POST /api/v1/explainable-reasoning/reason
Content-Type: application/json

{
  "query": "What is a schema?",
  "facts": {"type": "schema"}
}
```

---

## 8. Schema版本管理API

**服务地址**：`http://localhost:8007`
**网关路径**：`/api/v1/schema-versioning/`

### 8.1 创建版本

```http
POST /api/v1/schema-versioning/version/create
Content-Type: application/json

{
  "schema_id": "payment_schema",
  "schema_content": {"fields": {"amount": {"type": "decimal"}}},
  "version": "1.0.0"
}
```

### 8.2 检查兼容性

```http
POST /api/v1/schema-versioning/compatibility/check
Content-Type: application/json

{
  "schema_id": "payment_schema",
  "from_version": "1.0.0",
  "to_version": "1.1.0"
}
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
