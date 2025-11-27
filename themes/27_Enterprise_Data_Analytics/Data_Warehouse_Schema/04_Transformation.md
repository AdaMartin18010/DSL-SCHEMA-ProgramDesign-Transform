# 数据仓库Schema转换体系

## 📑 目录

- [数据仓库Schema转换体系](#数据仓库schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 数据仓库到SQL Schema转换](#2-数据仓库到sql-schema转换)
  - [3. 数据仓库到JSON Schema转换](#3-数据仓库到json-schema转换)
  - [4. 数据仓库到OpenAPI转换](#4-数据仓库到openapi转换)
  - [5. 数据仓库数据存储与分析](#5-数据仓库数据存储与分析)
    - [5.1 PostgreSQL数据仓库数据存储](#51-postgresql数据仓库数据存储)
    - [5.2 数据仓库数据分析查询](#52-数据仓库数据分析查询)

---

## 1. 转换体系概述

数据仓库Schema转换体系支持数据仓库到SQL Schema、JSON Schema、OpenAPI格式转换，以及数据仓库数据存储。

### 1.1 转换目标

1. **数据仓库到SQL Schema转换**：数据仓库到SQL Schema格式
2. **数据仓库到JSON Schema转换**：数据仓库到JSON Schema格式
3. **数据仓库到OpenAPI转换**：数据仓库到OpenAPI格式
4. **数据仓库到数据库转换**：数据仓库数据到PostgreSQL存储

---

## 2. 数据仓库到SQL Schema转换

**转换规则**：

- 事实表 → SQL Table
- 维度表 → SQL Table
- 维度键 → SQL Foreign Key

**转换示例**：

```python
def convert_dw_to_sql(dw_data: DataWarehouseSchema) -> SQLSchema:
    """将数据仓库数据转换为SQL Schema格式"""
    sql_schema = SQLSchema()

    # 转换事实表
    for fact_table in dw_data.star_schema.fact_tables:
        sql_table = SQLTable()
        sql_table.table_name = fact_table.fact_table_name

        # 转换度量
        for measure in fact_table.measures:
            sql_column = SQLColumn()
            sql_column.column_name = measure.measure_name
            sql_column.data_type = measure.data_type
            sql_column.is_nullable = False
            sql_table.columns.append(sql_column)

        # 转换维度键
        for dimension_key in fact_table.dimension_keys:
            sql_column = SQLColumn()
            sql_column.column_name = dimension_key.foreign_key_name
            sql_column.data_type = "INTEGER"
            sql_column.is_nullable = False
            sql_table.columns.append(sql_column)

            # 创建外键
            sql_foreign_key = SQLForeignKey()
            sql_foreign_key.column_name = dimension_key.foreign_key_name
            sql_foreign_key.referenced_table = get_dimension_table_name(dimension_key.dimension_table_id)
            sql_foreign_key.referenced_column = "dimension_id"
            sql_table.foreign_keys.append(sql_foreign_key)

        sql_schema.tables.append(sql_table)

    # 转换维度表
    for dimension_table in dw_data.star_schema.dimension_tables:
        sql_table = SQLTable()
        sql_table.table_name = dimension_table.dimension_table_name

        # 转换主键
        sql_column = SQLColumn()
        sql_column.column_name = dimension_table.primary_key
        sql_column.data_type = "INTEGER"
        sql_column.is_primary_key = True
        sql_column.is_nullable = False
        sql_table.columns.append(sql_column)

        # 转换属性
        for attribute in dimension_table.attributes:
            sql_column = SQLColumn()
            sql_column.column_name = attribute.attribute_name
            sql_column.data_type = attribute.data_type
            sql_column.is_nullable = not attribute.is_required
            sql_table.columns.append(sql_column)

        sql_schema.tables.append(sql_table)

    return sql_schema
```

---

## 3. 数据仓库到JSON Schema转换

**转换规则**：

- 事实表 → JSON Schema Object
- 维度表 → JSON Schema Object
- 度量 → JSON Schema Property

**转换示例**：

```python
def convert_dw_to_json_schema(dw_data: DataWarehouseSchema) -> JSONSchema:
    """将数据仓库数据转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # 转换事实表
    for fact_table in dw_data.star_schema.fact_tables:
        fact_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换度量
        for measure in fact_table.measures:
            fact_schema["properties"][measure.measure_name] = {
                "type": map_data_type_to_json_type(measure.data_type),
                "description": measure.measure_name
            }

        # 转换维度键
        for dimension_key in fact_table.dimension_keys:
            fact_schema["properties"][dimension_key.foreign_key_name] = {
                "type": "integer",
                "description": f"Foreign key to {dimension_key.dimension_table_id}"
            }

        json_schema["properties"][fact_table.fact_table_name] = fact_schema

    # 转换维度表
    for dimension_table in dw_data.star_schema.dimension_tables:
        dimension_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换属性
        for attribute in dimension_table.attributes:
            dimension_schema["properties"][attribute.attribute_name] = {
                "type": map_data_type_to_json_type(attribute.data_type),
                "description": attribute.attribute_name
            }

        json_schema["properties"][dimension_table.dimension_table_name] = dimension_schema

    return json_schema
```

---

## 4. 数据仓库到OpenAPI转换

**转换规则**：

- 事实表 → OpenAPI Schema
- 维度表 → OpenAPI Schema
- 数据仓库 → OpenAPI API

**转换示例**：

```python
def convert_dw_to_openapi(dw_data: DataWarehouseSchema) -> OpenAPISchema:
    """将数据仓库数据转换为OpenAPI格式"""
    openapi_schema = OpenAPISchema()

    # 转换事实表
    for fact_table in dw_data.star_schema.fact_tables:
        fact_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换度量
        for measure in fact_table.measures:
            fact_schema["properties"][measure.measure_name] = {
                "type": map_data_type_to_openapi_type(measure.data_type),
                "description": measure.measure_name
            }

        # 转换维度键
        for dimension_key in fact_table.dimension_keys:
            fact_schema["properties"][dimension_key.foreign_key_name] = {
                "type": "integer",
                "format": "int64",
                "description": f"Foreign key to {dimension_key.dimension_table_id}"
            }

        openapi_schema.components.schemas[fact_table.fact_table_name] = fact_schema

    # 转换维度表
    for dimension_table in dw_data.star_schema.dimension_tables:
        dimension_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换属性
        for attribute in dimension_table.attributes:
            dimension_schema["properties"][attribute.attribute_name] = {
                "type": map_data_type_to_openapi_type(attribute.data_type),
                "description": attribute.attribute_name
            }

        openapi_schema.components.schemas[dimension_table.dimension_table_name] = dimension_schema

    return openapi_schema
```

---

## 5. 数据仓库数据存储与分析

### 5.1 PostgreSQL数据仓库数据存储

**表结构设计**：

```sql
-- 事实表元数据表
CREATE TABLE fact_table_metadata (
    fact_table_id VARCHAR(50) PRIMARY KEY,
    fact_table_name VARCHAR(200) NOT NULL,
    fact_table_type VARCHAR(20) NOT NULL,
    grain VARCHAR(200) NOT NULL,
    partition_key VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 维度表元数据表
CREATE TABLE dimension_table_metadata (
    dimension_table_id VARCHAR(50) PRIMARY KEY,
    dimension_table_name VARCHAR(200) NOT NULL,
    dimension_type VARCHAR(20) NOT NULL,
    primary_key VARCHAR(100) NOT NULL,
    slow_changing_type VARCHAR(10) DEFAULT 'Type1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 度量元数据表
CREATE TABLE measure_metadata (
    measure_id VARCHAR(50) PRIMARY KEY,
    fact_table_id VARCHAR(50) NOT NULL,
    measure_name VARCHAR(200) NOT NULL,
    measure_type VARCHAR(20) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    aggregation_function VARCHAR(50) NOT NULL,
    FOREIGN KEY (fact_table_id) REFERENCES fact_table_metadata(fact_table_id)
);

-- 维度属性元数据表
CREATE TABLE dimension_attribute_metadata (
    attribute_id VARCHAR(50) PRIMARY KEY,
    dimension_table_id VARCHAR(50) NOT NULL,
    attribute_name VARCHAR(200) NOT NULL,
    attribute_type VARCHAR(20) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (dimension_table_id) REFERENCES dimension_table_metadata(dimension_table_id)
);

-- 数据血缘表
CREATE TABLE data_lineage (
    lineage_id VARCHAR(50) PRIMARY KEY,
    from_node_id VARCHAR(50) NOT NULL,
    to_node_id VARCHAR(50) NOT NULL,
    transformation_rule TEXT,
    data_flow_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 数据质量指标表
CREATE TABLE data_quality_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    table_id VARCHAR(50) NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    metric_type VARCHAR(20) NOT NULL,
    metric_value DECIMAL(5, 2),
    threshold DECIMAL(5, 2) DEFAULT 90,
    is_passed BOOLEAN,
    check_date DATE NOT NULL
);

-- 创建索引
CREATE INDEX idx_measure_metadata_fact_table ON measure_metadata(fact_table_id);
CREATE INDEX idx_dimension_attribute_metadata_dimension ON dimension_attribute_metadata(dimension_table_id);
CREATE INDEX idx_data_lineage_from_node ON data_lineage(from_node_id);
CREATE INDEX idx_data_lineage_to_node ON data_lineage(to_node_id);
CREATE INDEX idx_data_quality_metrics_table ON data_quality_metrics(table_id);
```

### 5.2 数据仓库数据分析查询

**查询示例**：

```python
def analyze_dw_metadata(conn):
    """分析数据仓库元数据"""
    cursor = conn.cursor()

    # 查询事实表汇总
    cursor.execute("""
        SELECT
            ftm.fact_table_name,
            ftm.fact_table_type,
            COUNT(mm.measure_id) as measure_count,
            COUNT(DISTINCT dkm.dimension_key_id) as dimension_count
        FROM fact_table_metadata ftm
        LEFT JOIN measure_metadata mm ON ftm.fact_table_id = mm.fact_table_id
        LEFT JOIN dimension_key_metadata dkm ON ftm.fact_table_id = dkm.fact_table_id
        GROUP BY ftm.fact_table_id, ftm.fact_table_name, ftm.fact_table_type
        ORDER BY ftm.fact_table_name
    """)

    fact_table_summary = cursor.fetchall()

    # 查询维度表汇总
    cursor.execute("""
        SELECT
            dtm.dimension_table_name,
            dtm.dimension_type,
            COUNT(dam.attribute_id) as attribute_count
        FROM dimension_table_metadata dtm
        LEFT JOIN dimension_attribute_metadata dam ON dtm.dimension_table_id = dam.dimension_table_id
        GROUP BY dtm.dimension_table_id, dtm.dimension_table_name, dtm.dimension_type
        ORDER BY dtm.dimension_table_name
    """)

    dimension_table_summary = cursor.fetchall()

    # 查询数据质量汇总
    cursor.execute("""
        SELECT
            dqm.table_id,
            dqm.metric_type,
            AVG(dqm.metric_value) as avg_metric_value,
            COUNT(*) as check_count,
            SUM(CASE WHEN dqm.is_passed THEN 1 ELSE 0 END) as passed_count
        FROM data_quality_metrics dqm
        WHERE dqm.check_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY dqm.table_id, dqm.metric_type
        ORDER BY dqm.table_id, dqm.metric_type
    """)

    quality_summary = cursor.fetchall()

    return {
        "fact_table_summary": fact_table_summary,
        "dimension_table_summary": dimension_table_summary,
        "quality_summary": quality_summary
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
