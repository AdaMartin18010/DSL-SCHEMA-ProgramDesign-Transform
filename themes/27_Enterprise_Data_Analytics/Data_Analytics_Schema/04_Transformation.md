# 数据分析Schema转换体系

## 📑 目录

- [数据分析Schema转换体系](#数据分析schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 数据分析到数据仓库转换](#2-数据分析到数据仓库转换)
  - [3. 数据分析到BI转换](#3-数据分析到bi转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 数据分析数据存储](#5-数据分析数据存储)
    - [5.1 PostgreSQL数据分析数据存储](#51-postgresql数据分析数据存储)
    - [5.2 数据分析查询](#52-数据分析查询)

---

## 1. 转换体系概述

数据分析Schema转换体系支持数据分析数据到数据仓库、BI格式转换，
以及数据分析数据存储。

### 1.1 转换目标

1. **数据分析到数据仓库转换**：数据分析数据到数据仓库格式
2. **数据分析到BI转换**：数据分析数据到BI格式
3. **数据分析到数据库转换**：数据分析数据到PostgreSQL存储

---

## 2. 数据分析到数据仓库转换

**转换规则**：

- 分析结果 → 数据仓库事实表
- 分析维度 → 数据仓库维度表
- 分析指标 → 数据仓库度量值

**转换示例**：

```python
def convert_analytics_to_data_warehouse(analytics_data: DataAnalyticsSchema) -> DataWarehouseSchema:
    """将数据分析数据转换为数据仓库格式"""
    dw_schema = DataWarehouseSchema()

    # 转换星型模式
    star_schema = StarSchema()

    # 创建事实表
    fact_table = FactTable()
    fact_table.fact_table_name = "sales_fact"
    fact_table.measures = [
        {"name": "sales_amount", "type": "Decimal"},
        {"name": "quantity", "type": "Integer"}
    ]
    fact_table.grain = "Daily Sales by Product and Customer"
    star_schema.fact_tables.append(fact_table)

    # 创建维度表
    dimension_table = DimensionTable()
    dimension_table.dimension_name = "product_dimension"
    dimension_table.dimension_attributes = [
        "product_id", "product_name", "product_category", "product_price"
    ]
    star_schema.dimension_tables.append(dimension_table)

    dw_schema.star_schema = star_schema

    return dw_schema
```

---

## 3. 数据分析到BI转换

**转换规则**：

- 分析结果 → BI报表数据
- 分析图表 → BI仪表板组件
- 分析指标 → BI KPI

**转换示例**：

```python
def convert_analytics_to_bi(analytics_data: DataAnalyticsSchema) -> BusinessIntelligenceSchema:
    """将数据分析数据转换为BI格式"""
    bi_schema = BusinessIntelligenceSchema()

    # 转换报表
    report = Report()
    report.report_name = "Sales Analysis Report"
    report.report_format = "PDF"
    report.report_content = generate_report_content(analytics_data)
    bi_schema.reports.append(report)

    # 转换仪表板
    dashboard = Dashboard()
    dashboard.dashboard_name = "Sales Dashboard"

    # 转换图表组件
    for chart in analytics_data.data_visualization.chart_types:
        component = DashboardComponent()
        component.component_type = "Chart"
        component.component_config = chart.chart_config
        dashboard.dashboard_components.append(component)

    bi_schema.dashboards.append(dashboard)

    return bi_schema
```

---

## 4. 转换工具

### 4.1 数据分析工具

- **Python数据分析**：Pandas、NumPy、Scikit-learn
- **R数据分析**：R语言数据分析包
- **Spark数据分析**：Apache Spark数据分析

---

## 5. 数据分析数据存储

### 5.1 PostgreSQL数据分析数据存储

**表结构设计**：

```sql
-- 数据源表
CREATE TABLE data_sources (
    source_id VARCHAR(50) PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_connection TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 数据质量指标表
CREATE TABLE data_quality_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    metric_name VARCHAR(200) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(5, 2) NOT NULL,
    threshold DECIMAL(5, 2) NOT NULL,
    is_passed BOOLEAN GENERATED ALWAYS AS (metric_value >= threshold) STORED,
    check_date DATE NOT NULL
);

-- 分析结果表
CREATE TABLE analysis_results (
    result_id VARCHAR(50) PRIMARY KEY,
    analysis_id VARCHAR(50) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    result_data JSONB NOT NULL,
    result_date DATE NOT NULL
);

-- 机器学习模型表
CREATE TABLE ml_models (
    model_id VARCHAR(50) PRIMARY KEY,
    model_type VARCHAR(50) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    model_accuracy DECIMAL(5, 2) NOT NULL,
    training_date DATE NOT NULL,
    model_version VARCHAR(50) NOT NULL
);

-- 创建索引
CREATE INDEX idx_data_quality_metrics_date ON data_quality_metrics(check_date);
CREATE INDEX idx_analysis_results_analysis ON analysis_results(analysis_id);
CREATE INDEX idx_ml_models_type ON ml_models(model_type);
```

**数据插入示例**：

```python
def store_analytics_data(analytics_data: DataAnalyticsSchema, conn):
    """存储数据分析数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入数据源
    for source in analytics_data.data_collection.data_sources:
        cursor.execute("""
            INSERT INTO data_sources
            (source_id, source_type, source_connection, is_active)
            VALUES (%s, %s, %s, %s)
        """, (source.source_id, source.source_type,
              source.source_connection, source.is_active))

    # 插入数据质量指标
    for metric in analytics_data.data_collection.data_quality.quality_metrics:
        cursor.execute("""
            INSERT INTO data_quality_metrics
            (metric_id, metric_name, metric_type, metric_value, threshold, check_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (metric.metric_id, metric.metric_name, metric.metric_type,
              metric.metric_value, metric.threshold, "2025-01-21"))

    # 插入机器学习模型
    for model in analytics_data.data_analysis.machine_learning.models:
        cursor.execute("""
            INSERT INTO ml_models
            (model_id, model_type, algorithm, model_accuracy, training_date, model_version)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (model.model_id, model.model_type, model.algorithm,
              model.model_accuracy, "2025-01-21", "v1.0"))

    conn.commit()
```

### 5.2 数据分析查询

**查询示例**：

```python
def analyze_analytics_data(conn, period_start, period_end):
    """分析数据分析数据"""
    cursor = conn.cursor()

    # 查询数据质量趋势
    cursor.execute("""
        SELECT
            check_date,
            AVG(metric_value) as avg_quality_score,
            COUNT(CASE WHEN is_passed THEN 1 END) as passed_metrics,
            COUNT(*) as total_metrics
        FROM data_quality_metrics
        WHERE check_date BETWEEN %s AND %s
        GROUP BY check_date
        ORDER BY check_date
    """, (period_start, period_end))

    quality_trends = cursor.fetchall()

    # 查询模型准确率
    cursor.execute("""
        SELECT
            model_type,
            AVG(model_accuracy) as avg_accuracy,
            COUNT(*) as model_count
        FROM ml_models
        WHERE training_date BETWEEN %s AND %s
        GROUP BY model_type
        ORDER BY avg_accuracy DESC
    """, (period_start, period_end))

    model_performance = cursor.fetchall()

    return {
        "quality_trends": quality_trends,
        "model_performance": model_performance
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
