# 可观测性Schema转换体系

## 📑 目录

- [可观测性Schema转换体系](#可观测性schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 协议转换](#2-协议转换)
    - [2.1 OTLP到Prometheus转换](#21-otlp到prometheus转换)
    - [2.2 OTLP到Jaeger转换](#22-otlp到jaeger转换)
    - [2.3 Prometheus到OTLP转换](#23-prometheus到otlp转换)
  - [3. 数据格式转换](#3-数据格式转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 可观测性数据存储与分析](#6-可观测性数据存储与分析)
    - [6.1 PostgreSQL可观测性数据存储](#61-postgresql可观测性数据存储)
    - [6.2 可观测性数据分析查询](#62-可观测性数据分析查询)

---

## 1. 转换体系概述

可观测性Schema转换体系支持OTLP、Prometheus、Jaeger等协议之间的转换。

### 1.1 转换目标

1. **协议转换**：OTLP ↔ Prometheus, OTLP ↔ Jaeger
2. **数据格式转换**：gRPC ↔ HTTP/JSON
3. **指标格式转换**：OTLP Metric ↔ Prometheus Metric

---

## 2. 协议转换

### 2.1 OTLP到Prometheus转换

**转换规则**：

- OTLP Metric → Prometheus Metric
- OTLP DataPoint → Prometheus Sample
- OTLP Resource Attributes → Prometheus Labels

### 2.2 OTLP到Jaeger转换

**转换规则**：

- OTLP Span → Jaeger Span
- OTLP Trace → Jaeger Trace
- OTLP Resource → Jaeger Process

### 2.3 Prometheus到OTLP转换

**转换规则**：

- Prometheus Metric → OTLP Metric
- Prometheus Labels → OTLP Attributes
- Prometheus Sample → OTLP DataPoint

---

## 3. 数据格式转换

支持gRPC、HTTP/JSON、Protobuf等格式之间的转换。

---

## 4. 转换工具

- **OpenTelemetry Collector**：OTLP收集器
- **Prometheus Exporter**：Prometheus导出器
- **Jaeger Exporter**：Jaeger导出器

---

## 5. 转换验证

验证转换的语义等价性、数据完整性和性能。

---

## 6. 可观测性数据存储与分析

### 6.1 PostgreSQL可观测性数据存储

**可观测性数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class MetricDataPoint:
    """指标数据点"""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    resource: Dict[str, str]

@dataclass
class LogRecord:
    """日志记录"""
    severity: str
    message: str
    timestamp: datetime
    attributes: Dict[str, str]
    trace_id: Optional[str]
    span_id: Optional[str]

@dataclass
class Span:
    """追踪Span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    start_time: datetime
    end_time: datetime
    attributes: Dict[str, str]

class ObservabilityStorage:
    """可观测性数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建可观测性数据表"""
        # 指标数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id BIGSERIAL PRIMARY KEY,
                metric_name VARCHAR(500) NOT NULL,
                value FLOAT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                labels JSONB,
                resource JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 日志记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id BIGSERIAL PRIMARY KEY,
                severity VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                attributes JSONB,
                trace_id VARCHAR(32),
                span_id VARCHAR(16),
                resource JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 追踪Span表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                id BIGSERIAL PRIMARY KEY,
                trace_id VARCHAR(32) NOT NULL,
                span_id VARCHAR(16) NOT NULL,
                parent_span_id VARCHAR(16),
                name VARCHAR(500) NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                duration_ms BIGINT GENERATED ALWAYS AS (
                    EXTRACT(EPOCH FROM (end_time - start_time)) * 1000
                ) STORED,
                attributes JSONB,
                resource JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 资源定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id SERIAL PRIMARY KEY,
                service_name VARCHAR(200) NOT NULL,
                service_version VARCHAR(100),
                attributes JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 统计信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS observability_statistics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(500),
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_name, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_name_time
            ON metrics(metric_name, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_severity_time
            ON logs(severity, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_spans_trace_id
            ON spans(trace_id, start_time)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_spans_trace_span
            ON spans(trace_id, span_id)
        """)

        self.conn.commit()

    def store_metric(self, data_point: MetricDataPoint):
        """存储指标数据点"""
        self.cur.execute("""
            INSERT INTO metrics
            (metric_name, value, timestamp, labels, resource)
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
        """, (data_point.metric_name, data_point.value,
              data_point.timestamp, json.dumps(data_point.labels or {}),
              json.dumps(data_point.resource or {})))
        self.conn.commit()

    def store_log(self, log: LogRecord):
        """存储日志记录"""
        self.cur.execute("""
            INSERT INTO logs
            (severity, message, timestamp, attributes, trace_id, span_id, resource)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s::jsonb)
        """, (log.severity, log.message, log.timestamp,
              json.dumps(log.attributes or {}), log.trace_id, log.span_id,
              json.dumps({})))
        self.conn.commit()

    def store_span(self, span: Span):
        """存储追踪Span"""
        self.cur.execute("""
            INSERT INTO spans
            (trace_id, span_id, parent_span_id, name, start_time, end_time, attributes, resource)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
        """, (span.trace_id, span.span_id, span.parent_span_id,
              span.name, span.start_time, span.end_time,
              json.dumps(span.attributes or {}), json.dumps({})))
        self.conn.commit()

    def query_trace(self, trace_id: str):
        """查询完整追踪"""
        self.cur.execute("""
            SELECT trace_id, span_id, parent_span_id, name,
                   start_time, end_time, duration_ms, attributes
            FROM spans
            WHERE trace_id = %s
            ORDER BY start_time
        """, (trace_id,))
        return self.cur.fetchall()

    def calculate_metric_statistics(self, metric_name: str, time_window: datetime):
        """计算指标统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as count,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                STDDEV(value) as stddev_value
            FROM metrics
            WHERE metric_name = %s AND timestamp >= %s
        """, (metric_name, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO observability_statistics
            (metric_name, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (metric_name, statistic_type, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, (metric_name, "aggregate", time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 可观测性数据分析查询

**查询示例**：

```python
# 查询完整追踪
spans = storage.query_trace("abc123def456")

# 计算指标统计信息
stats = storage.calculate_metric_statistics(
    metric_name="http_request_duration",
    time_window=datetime.now() - timedelta(hours=1)
)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
