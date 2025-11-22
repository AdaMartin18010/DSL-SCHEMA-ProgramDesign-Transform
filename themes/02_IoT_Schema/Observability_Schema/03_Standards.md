# 可观测性Schema标准对标

## 📑 目录

- [可观测性Schema标准对标](#可观测性schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. OpenTelemetry标准](#2-opentelemetry标准)
    - [2.1 OTLP协议](#21-otlp协议)
    - [2.2 OpenTelemetry规范](#22-opentelemetry规范)
  - [3. Prometheus标准](#3-prometheus标准)
  - [4. 其他标准](#4-其他标准)
    - [4.1 Jaeger](#41-jaeger)
    - [4.2 Zipkin](#42-zipkin)
    - [4.3 W3C Trace Context](#43-w3c-trace-context)
  - [5. 标准对比矩阵](#5-标准对比矩阵)

---

## 1. 标准体系概述

可观测性Schema标准体系分为三个层次：

1. **CNCF标准**：OpenTelemetry、Prometheus等
2. **W3C标准**：Trace Context等
3. **行业标准**：Jaeger、Zipkin等

---

## 2. OpenTelemetry标准

### 2.1 OTLP协议

**标准名称**：OpenTelemetry Protocol (OTLP)

**核心内容**：

- **指标**：Metric、DataPoint、Resource
- **日志**：LogRecord、Resource、Scope
- **追踪**：Span、Trace、Resource
- **传输**：gRPC、HTTP/JSON

**Schema支持**：完整支持

**状态**：CNCF标准，v1.0+

### 2.2 OpenTelemetry规范

**标准名称**：OpenTelemetry Specification

**核心内容**：

- **语义约定**：资源语义约定
- **指标语义**：指标命名和单位
- **追踪语义**：Span命名和属性

**Schema支持**：完整支持

---

## 3. Prometheus标准

**标准名称**：Prometheus Data Model

**核心内容**：

- **指标格式**：Prometheus文本格式
- **标签系统**：键值对标签
- **时间序列**：时间序列数据模型
- **查询语言**：PromQL

**Schema支持**：完整支持

**状态**：CNCF标准

---

## 4. 其他标准

### 4.1 Jaeger

**标准名称**：Jaeger Tracing

**核心内容**：

- **追踪格式**：Jaeger格式
- **存储后端**：Cassandra、Elasticsearch等

**Schema支持**：基本支持

**状态**：CNCF项目

### 4.2 Zipkin

**标准名称**：Zipkin Tracing

**核心内容**：

- **追踪格式**：Zipkin格式
- **HTTP API**：Zipkin HTTP API

**Schema支持**：基本支持

**状态**：开源项目

### 4.3 W3C Trace Context

**标准名称**：W3C Trace Context

**核心内容**：

- **Trace Context**：HTTP头格式
- **Trace ID**：128位Trace ID
- **Parent Span ID**：64位Span ID

**Schema支持**：完整支持

**状态**：W3C标准

---

## 5. 标准对比矩阵

| 标准 | 组织 | Schema支持 | 状态 | 应用场景 |
|------|------|-----------|------|---------|
| **OTLP** | CNCF | ⭐⭐⭐⭐⭐ | 标准 | 统一可观测性 |
| **Prometheus** | CNCF | ⭐⭐⭐⭐⭐ | 标准 | 指标监控 |
| **Jaeger** | CNCF | ⭐⭐⭐⭐ | 活跃 | 分布式追踪 |
| **Zipkin** | 开源 | ⭐⭐⭐ | 活跃 | 分布式追踪 |
| **W3C Trace Context** | W3C | ⭐⭐⭐⭐⭐ | 标准 | HTTP追踪 |

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
