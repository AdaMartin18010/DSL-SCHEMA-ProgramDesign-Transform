# 数据湖Schema转换体系

## 📑 目录

- [数据湖Schema转换体系](#数据湖schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 数据湖到数据仓库转换](#2-数据湖到数据仓库转换)
  - [3. 数据湖到JSON Schema转换](#3-数据湖到json-schema转换)
  - [4. 数据湖到Hive Metastore转换](#4-数据湖到hive-metastore转换)
  - [5. 数据湖数据存储与分析](#5-数据湖数据存储与分析)
    - [5.1 PostgreSQL数据湖元数据存储](#51-postgresql数据湖元数据存储)
    - [5.2 数据湖数据分析查询](#52-数据湖数据分析查询)

---

## 1. 转换体系概述

数据湖Schema转换体系支持数据湖到数据仓库、JSON Schema、Hive Metastore格式转换，以及数据湖元数据存储。

### 1.1 转换目标

1. **数据湖到数据仓库转换**：数据湖Schema到数据仓库格式
2. **数据湖到JSON Schema转换**：数据湖Schema到JSON Schema格式
3. **数据湖到Hive Metastore转换**：数据湖Schema到Hive Metastore格式
4. **数据湖到数据库转换**：数据湖元数据到PostgreSQL存储

---

## 2. 数据湖到数据仓库转换

**转换规则**：

- 数据表 → 数据仓库表（事实表/维度表）
- 数据分区 → 数据仓库分区
- 数据血缘 → ETL流程

**转换示例**：

```python
def convert_datalake_to_datawarehouse(lake_data: DataLakeSchema) -> DataWarehouseSchema:
    """将数据湖Schema转换为数据仓库格式"""
    dw_schema = DataWarehouseSchema()

    # 转换数据表
    for table in lake_data.data_catalog.data_tables:
        # 判断表类型（事实表或维度表）
        if is_fact_table(table):
            fact_table = FactTable()
            fact_table.fact_table_id = table.table_id
            fact_table.fact_table_name = table.table_name
            fact_table.fact_table_type = "Transaction"

            # 转换度量
            for column in table.columns:
                if is_measure_column(column):
                    measure = Measure()
                    measure.measure_id = column.column_id
                    measure.measure_name = column.column_name
                    measure.measure_type = "Sum"
                    measure.data_type = map_column_type_to_measure_type(column.column_type)
                    fact_table.measures.append(measure)

            # 转换维度键
            for partition_key in table.partition_columns:
                dimension_key = DimensionKey()
                dimension_key.foreign_key_name = partition_key
                dimension_key.dimension_table_id = f"DIM-{partition_key}"
                fact_table.dimension_keys.append(dimension_key)

            dw_schema.star_schema.fact_tables.append(fact_table)
        else:
            dimension_table = DimensionTable()
            dimension_table.dimension_table_id = table.table_id
            dimension_table.dimension_table_name = table.table_name
            dimension_table.dimension_type = "Other"

            # 转换属性
            for column in table.columns:
                attribute = DimensionAttribute()
                attribute.attribute_id = column.column_id
                attribute.attribute_name = column.column_name
                attribute.attribute_type = "Descriptive"
                attribute.data_type = map_column_type_to_attribute_type(column.column_type)
                dimension_table.attributes.append(attribute)

            dimension_table.primary_key = table.columns[0].column_name
            dw_schema.star_schema.dimension_tables.append(dimension_table)

    # 转换数据血缘为ETL流程
    for edge in lake_data.data_catalog.data_lineage.lineage_edges:
        etl_process = ETLProcess()
        etl_process.process_id = edge.edge_id
        etl_process.source_table = find_table_by_node_id(lake_data, edge.from_node_id)
        etl_process.target_table = find_table_by_node_id(lake_data, edge.to_node_id)
        etl_process.transformation_rule = edge.transformation_rule
        dw_schema.etl_processes.append(etl_process)

    return dw_schema
```

---

## 3. 数据湖到JSON Schema转换

**转换规则**：

- 数据表 → JSON Schema Object
- 数据列 → JSON Schema Property
- 数据类型 → JSON Schema Type

**转换示例**：

```python
def convert_datalake_to_json_schema(lake_data: DataLakeSchema) -> JSONSchema:
    """将数据湖Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # 转换数据表
    for table in lake_data.data_catalog.data_tables:
        table_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换列
        for column in table.columns:
            table_schema["properties"][column.column_name] = {
                "type": map_column_type_to_json_type(column.column_type),
                "description": column.description or column.column_name
            }

            if not column.is_nullable:
                if "required" not in table_schema:
                    table_schema["required"] = []
                table_schema["required"].append(column.column_name)

        json_schema["properties"][table.table_name] = table_schema

    return json_schema
```

---

## 4. 数据湖到Hive Metastore转换

**转换规则**：

- 数据表 → Hive Table
- 数据列 → Hive Column
- 数据分区 → Hive Partition

**转换示例**：

```python
def convert_datalake_to_hive_metastore(lake_data: DataLakeSchema) -> HiveMetastore:
    """将数据湖Schema转换为Hive Metastore格式"""
    metastore = HiveMetastore()

    # 转换数据源为数据库
    databases = {}
    for source in lake_data.data_catalog.data_sources:
        database = HiveDatabase()
        database.name = source.source_name
        database.location = source.source_location
        databases[source.source_id] = database
        metastore.databases.append(database)

    # 转换数据表
    for table in lake_data.data_catalog.data_tables:
        hive_table = HiveTable()
        hive_table.database_name = databases[table.source_id].name
        hive_table.table_name = table.table_name
        hive_table.table_type = "EXTERNAL"
        hive_table.location = table.table_path
        hive_table.input_format = map_format_to_hive_input_format(table.table_format)
        hive_table.output_format = map_format_to_hive_output_format(table.table_format)

        # 转换列
        for column in table.columns:
            hive_column = HiveColumn()
            hive_column.name = column.column_name
            hive_column.type = map_column_type_to_hive_type(column.column_type)
            hive_column.comment = column.description
            hive_table.columns.append(hive_column)

        # 转换分区
        if table.partition_columns:
            for partition_key in table.partition_columns:
                partition_column = HivePartitionColumn()
                partition_column.name = partition_key
                partition_column.type = "string"  # 默认分区类型为string
                hive_table.partition_columns.append(partition_column)

        metastore.tables.append(hive_table)

    return metastore
```

---

## 5. 数据湖数据存储与分析

### 5.1 PostgreSQL数据湖元数据存储

**表结构设计**：

```sql
-- 数据源表
CREATE TABLE data_sources (
    source_id VARCHAR(50) PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    source_location VARCHAR(500) NOT NULL,
    source_format VARCHAR(20) NOT NULL,
    schema_definition JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 数据表表
CREATE TABLE data_tables (
    table_id VARCHAR(50) PRIMARY KEY,
    source_id VARCHAR(50) NOT NULL,
    table_name VARCHAR(200) NOT NULL,
    table_path VARCHAR(500) NOT NULL,
    table_format VARCHAR(20) NOT NULL,
    partition_columns TEXT[],
    row_count BIGINT,
    size_bytes BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id)
);

-- 表列表
CREATE TABLE table_columns (
    column_id VARCHAR(50) PRIMARY KEY,
    table_id VARCHAR(50) NOT NULL,
    column_name VARCHAR(200) NOT NULL,
    column_type VARCHAR(50) NOT NULL,
    is_nullable BOOLEAN DEFAULT TRUE,
    description TEXT,
    FOREIGN KEY (table_id) REFERENCES data_tables(table_id)
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
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(20) NOT NULL,
    metric_value DECIMAL(5, 2),
    threshold DECIMAL(5, 2) DEFAULT 90,
    is_passed BOOLEAN,
    check_date DATE NOT NULL,
    FOREIGN KEY (table_id) REFERENCES data_tables(table_id)
);

-- 访问控制表
CREATE TABLE access_controls (
    control_id VARCHAR(50) PRIMARY KEY,
    resource_id VARCHAR(50) NOT NULL,
    resource_type VARCHAR(20) NOT NULL,
    principal VARCHAR(200) NOT NULL,
    permission VARCHAR(20) NOT NULL,
    condition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_data_tables_source ON data_tables(source_id);
CREATE INDEX idx_table_columns_table ON table_columns(table_id);
CREATE INDEX idx_data_lineage_from ON data_lineage(from_node_id);
CREATE INDEX idx_data_lineage_to ON data_lineage(to_node_id);
CREATE INDEX idx_data_quality_metrics_table ON data_quality_metrics(table_id);
CREATE INDEX idx_access_controls_resource ON access_controls(resource_id);
```

### 5.2 数据湖数据分析查询

**查询示例**：

```python
def analyze_datalake_data(conn):
    """分析数据湖数据"""
    cursor = conn.cursor()

    # 查询数据源汇总
    cursor.execute("""
        SELECT
            ds.source_type,
            COUNT(DISTINCT ds.source_id) as source_count,
            COUNT(DISTINCT dt.table_id) as table_count,
            SUM(dt.row_count) as total_rows,
            SUM(dt.size_bytes) as total_size_bytes
        FROM data_sources ds
        LEFT JOIN data_tables dt ON ds.source_id = dt.source_id
        GROUP BY ds.source_type
        ORDER BY source_count DESC
    """)

    source_summary = cursor.fetchall()

    # 查询数据表格式汇总
    cursor.execute("""
        SELECT
            dt.table_format,
            COUNT(*) as table_count,
            SUM(dt.row_count) as total_rows,
            SUM(dt.size_bytes) as total_size_bytes
        FROM data_tables dt
        GROUP BY dt.table_format
        ORDER BY table_count DESC
    """)

    format_summary = cursor.fetchall()

    # 查询数据质量汇总
    cursor.execute("""
        SELECT
            dt.table_name,
            dqm.metric_type,
            AVG(dqm.metric_value) as avg_metric_value,
            SUM(CASE WHEN dqm.is_passed THEN 1 ELSE 0 END) as passed_count,
            COUNT(*) as total_checks
        FROM data_tables dt
        JOIN data_quality_metrics dqm ON dt.table_id = dqm.table_id
        WHERE dqm.check_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY dt.table_id, dt.table_name, dqm.metric_type
        ORDER BY dt.table_name, dqm.metric_type
    """)

    quality_summary = cursor.fetchall()

    return {
        "source_summary": source_summary,
        "format_summary": format_summary,
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
