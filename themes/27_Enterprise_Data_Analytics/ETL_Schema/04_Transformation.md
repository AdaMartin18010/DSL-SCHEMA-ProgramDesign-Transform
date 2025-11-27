# ETL Schema转换体系

## 📑 目录

- [ETL Schema转换体系](#etl-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ETL到Informatica转换](#2-etl到informatica转换)
  - [3. ETL到Talend转换](#3-etl到talend转换)
  - [4. ETL到JSON Schema转换](#4-etl到json-schema转换)
  - [5. ETL数据存储与分析](#5-etl数据存储与分析)
    - [5.1 PostgreSQL ETL元数据存储](#51-postgresql-etl元数据存储)
    - [5.2 ETL数据分析查询](#52-etl数据分析查询)

---

## 1. 转换体系概述

ETL Schema转换体系支持ETL到Informatica、Talend、JSON Schema格式转换，以及ETL元数据存储。

### 1.1 转换目标

1. **ETL到Informatica转换**：ETL Schema到Informatica格式
2. **ETL到Talend转换**：ETL Schema到Talend格式
3. **ETL到JSON Schema转换**：ETL Schema到JSON Schema格式
4. **ETL到数据库转换**：ETL元数据到PostgreSQL存储

---

## 2. ETL到Informatica转换

**转换规则**：

- 数据源连接 → Informatica Connection
- 提取规则 → Informatica Source
- 转换规则 → Informatica Transformation
- 加载策略 → Informatica Target

**转换示例**：

```python
def convert_etl_to_informatica(etl_data: ETLSchema) -> InformaticaWorkflow:
    """将ETL Schema转换为Informatica格式"""
    workflow = InformaticaWorkflow()

    # 转换数据源连接
    for connection in etl_data.extract.data_source_connections:
        infa_connection = InformaticaConnection()
        infa_connection.name = connection.connection_name
        infa_connection.type = map_connection_type_to_informatica(connection.connection_type)
        infa_connection.connection_string = connection.connection_string
        infa_connection.parameters = connection.connection_parameters
        workflow.connections.append(infa_connection)

    # 转换ETL流程
    for process in etl_data.etl_process.process_definitions:
        # 创建映射
        mapping = InformaticaMapping()
        mapping.name = process.process_name

        # 转换提取规则
        extract_rule = find_extract_rule(etl_data, process.extract_rule_id)
        source = InformaticaSource()
        source.name = extract_rule.source_table or "Source"
        source.connection = find_connection_by_id(workflow, extract_rule.connection_id)
        source.query = extract_rule.source_query
        mapping.sources.append(source)

        # 转换转换规则
        for transform_rule_id in process.transform_rule_ids:
            transform_rule = find_transform_rule(etl_data, transform_rule_id)
            transformation = InformaticaTransformation()
            transformation.name = transform_rule.rule_name
            transformation.type = map_transform_type_to_informatica(transform_rule.rule_type)
            transformation.expression = transform_rule.transform_logic
            transformation.parameters = transform_rule.transform_parameters
            mapping.transformations.append(transformation)

        # 转换加载策略
        load_strategy = find_load_strategy(etl_data, process.load_strategy_id)
        target = InformaticaTarget()
        target.name = find_target_table(etl_data, load_strategy.table_id).table_name
        target.connection = create_target_connection(workflow, load_strategy)
        target.load_mode = map_load_mode_to_informatica(load_strategy)
        mapping.targets.append(target)

        workflow.mappings.append(mapping)

        # 创建会话
        session = InformaticaSession()
        session.name = f"{process.process_name}_Session"
        session.mapping = mapping.name
        session.source_connection = source.connection.name
        session.target_connection = target.connection.name
        workflow.sessions.append(session)

        # 创建工作流任务
        task = InformaticaTask()
        task.name = f"{process.process_name}_Task"
        task.type = "Session"
        task.session = session.name
        workflow.tasks.append(task)

    return workflow
```

---

## 3. ETL到Talend转换

**转换规则**：

- 数据源连接 → Talend Connection
- 提取规则 → Talend Input Component
- 转换规则 → Talend Transformation Component
- 加载策略 → Talend Output Component

**转换示例**：

```python
def convert_etl_to_talend(etl_data: ETLSchema) -> TalendJob:
    """将ETL Schema转换为Talend格式"""
    job = TalendJob()
    job.name = "ETL_Job"

    # 转换数据源连接
    for connection in etl_data.extract.data_source_connections:
        talend_connection = TalendConnection()
        talend_connection.name = connection.connection_name
        talend_connection.type = map_connection_type_to_talend(connection.connection_type)
        talend_connection.properties = {
            "connection_string": connection.connection_string,
            **connection.connection_parameters
        }
        job.connections.append(talend_connection)

    # 转换ETL流程
    for process in etl_data.etl_process.process_definitions:
        # 转换提取规则
        extract_rule = find_extract_rule(etl_data, process.extract_rule_id)
        input_component = TalendInputComponent()
        input_component.name = f"tInput_{extract_rule.rule_id}"
        input_component.type = map_connection_type_to_talend_input(extract_rule.connection_id)
        input_component.connection = find_connection_by_id(job, extract_rule.connection_id)
        input_component.query = extract_rule.source_query
        input_component.table = extract_rule.source_table
        job.components.append(input_component)

        prev_component = input_component

        # 转换转换规则
        for transform_rule_id in process.transform_rule_ids:
            transform_rule = find_transform_rule(etl_data, transform_rule_id)
            transform_component = TalendTransformComponent()
            transform_component.name = f"tTransform_{transform_rule.rule_id}"
            transform_component.type = map_transform_type_to_talend(transform_rule.rule_type)
            transform_component.expression = transform_rule.transform_logic
            transform_component.parameters = transform_rule.transform_parameters
            job.components.append(transform_component)

            # 创建连接
            link = TalendLink()
            link.from_component = prev_component.name
            link.to_component = transform_component.name
            job.links.append(link)

            prev_component = transform_component

        # 转换加载策略
        load_strategy = find_load_strategy(etl_data, process.load_strategy_id)
        target_table = find_target_table(etl_data, load_strategy.table_id)
        output_component = TalendOutputComponent()
        output_component.name = f"tOutput_{load_strategy.strategy_id}"
        output_component.type = map_load_strategy_to_talend_output(load_strategy)
        output_component.table = target_table.table_name
        output_component.schema = target_table.table_schema
        output_component.mode = map_load_mode_to_talend(load_strategy)
        job.components.append(output_component)

        # 创建连接
        link = TalendLink()
        link.from_component = prev_component.name
        link.to_component = output_component.name
        job.links.append(link)

    return job
```

---

## 4. ETL到JSON Schema转换

**转换规则**：

- ETL流程 → JSON Schema Object
- 提取规则 → JSON Schema Property
- 转换规则 → JSON Schema Property
- 加载策略 → JSON Schema Property

**转换示例**：

```python
def convert_etl_to_json_schema(etl_data: ETLSchema) -> JSONSchema:
    """将ETL Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # 转换ETL流程
    for process in etl_data.etl_process.process_definitions:
        process_schema = {
            "type": "object",
            "properties": {
                "process_id": {"type": "string"},
                "process_name": {"type": "string"},
                "process_type": {"type": "string"},
                "extract": {
                    "type": "object",
                    "properties": {
                        "rule_id": {"type": "string"},
                        "source_table": {"type": "string"},
                        "source_query": {"type": "string"}
                    }
                },
                "transform": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rule_id": {"type": "string"},
                            "rule_name": {"type": "string"},
                            "rule_type": {"type": "string"},
                            "transform_logic": {"type": "string"}
                        }
                    }
                },
                "load": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {"type": "string"},
                        "table_id": {"type": "string"},
                        "strategy_type": {"type": "string"}
                    }
                }
            }
        }

        json_schema["properties"][process.process_name] = process_schema

    return json_schema
```

---

## 5. ETL数据存储与分析

### 5.1 PostgreSQL ETL元数据存储

**表结构设计**：

```sql
-- 数据源连接表
CREATE TABLE data_source_connections (
    connection_id VARCHAR(50) PRIMARY KEY,
    connection_name VARCHAR(200) NOT NULL,
    connection_type VARCHAR(20) NOT NULL,
    connection_string VARCHAR(500) NOT NULL,
    connection_parameters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 提取规则表
CREATE TABLE extract_rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    connection_id VARCHAR(50) NOT NULL,
    source_table VARCHAR(200),
    source_query TEXT,
    extract_condition TEXT,
    extract_fields TEXT[],
    extract_frequency VARCHAR(20) DEFAULT 'Daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES data_source_connections(connection_id)
);

-- 转换规则表
CREATE TABLE transform_rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(20) NOT NULL,
    source_fields TEXT[] NOT NULL,
    target_fields TEXT[] NOT NULL,
    transform_logic TEXT NOT NULL,
    transform_parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 目标表表
CREATE TABLE target_tables (
    table_id VARCHAR(50) PRIMARY KEY,
    table_name VARCHAR(200) NOT NULL,
    table_schema VARCHAR(100) NOT NULL,
    table_type VARCHAR(20) NOT NULL,
    table_structure JSONB,
    primary_key VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 加载策略表
CREATE TABLE load_strategies (
    strategy_id VARCHAR(50) PRIMARY KEY,
    table_id VARCHAR(50) NOT NULL,
    strategy_type VARCHAR(20) NOT NULL,
    strategy_parameters JSONB,
    load_frequency VARCHAR(20) DEFAULT 'Daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_id) REFERENCES target_tables(table_id)
);

-- ETL流程定义表
CREATE TABLE etl_process_definitions (
    process_id VARCHAR(50) PRIMARY KEY,
    process_name VARCHAR(200) NOT NULL,
    process_type VARCHAR(20) NOT NULL,
    extract_rule_id VARCHAR(50) NOT NULL,
    transform_rule_ids TEXT[] NOT NULL,
    load_strategy_id VARCHAR(50) NOT NULL,
    process_dependencies TEXT[],
    process_parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (extract_rule_id) REFERENCES extract_rules(rule_id),
    FOREIGN KEY (load_strategy_id) REFERENCES load_strategies(strategy_id)
);

-- ETL执行历史表
CREATE TABLE etl_execution_history (
    execution_id VARCHAR(50) PRIMARY KEY,
    process_id VARCHAR(50) NOT NULL,
    execution_start_time TIMESTAMP NOT NULL,
    execution_end_time TIMESTAMP,
    execution_status VARCHAR(20) DEFAULT 'Running',
    rows_extracted BIGINT,
    rows_transformed BIGINT,
    rows_loaded BIGINT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES etl_process_definitions(process_id)
);

-- 创建索引
CREATE INDEX idx_extract_rules_connection ON extract_rules(connection_id);
CREATE INDEX idx_load_strategies_table ON load_strategies(table_id);
CREATE INDEX idx_etl_process_extract ON etl_process_definitions(extract_rule_id);
CREATE INDEX idx_etl_process_load ON etl_process_definitions(load_strategy_id);
CREATE INDEX idx_etl_execution_process ON etl_execution_history(process_id);
CREATE INDEX idx_etl_execution_status ON etl_execution_history(execution_status);
```

### 5.2 ETL数据分析查询

**查询示例**：

```python
def analyze_etl_data(conn):
    """分析ETL数据"""
    cursor = conn.cursor()

    # 查询ETL流程执行统计
    cursor.execute("""
        SELECT
            epd.process_name,
            epd.process_type,
            COUNT(eh.execution_id) as execution_count,
            SUM(CASE WHEN eh.execution_status = 'Completed' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN eh.execution_status = 'Failed' THEN 1 ELSE 0 END) as failed_count,
            AVG(eh.rows_loaded) as avg_rows_loaded,
            AVG(EXTRACT(EPOCH FROM (eh.execution_end_time - eh.execution_start_time))) as avg_duration_seconds
        FROM etl_process_definitions epd
        LEFT JOIN etl_execution_history eh ON epd.process_id = eh.process_id
        WHERE eh.execution_start_time >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY epd.process_id, epd.process_name, epd.process_type
        ORDER BY execution_count DESC
    """)

    process_statistics = cursor.fetchall()

    # 查询数据源连接使用情况
    cursor.execute("""
        SELECT
            dsc.connection_type,
            COUNT(DISTINCT dsc.connection_id) as connection_count,
            COUNT(DISTINCT er.rule_id) as extract_rule_count
        FROM data_source_connections dsc
        LEFT JOIN extract_rules er ON dsc.connection_id = er.connection_id
        WHERE dsc.is_active = TRUE
        GROUP BY dsc.connection_type
        ORDER BY connection_count DESC
    """)

    connection_usage = cursor.fetchall()

    # 查询转换规则使用情况
    cursor.execute("""
        SELECT
            tr.rule_type,
            COUNT(*) as rule_count,
            COUNT(DISTINCT epd.process_id) as process_count
        FROM transform_rules tr
        LEFT JOIN etl_process_definitions epd ON tr.rule_id = ANY(epd.transform_rule_ids)
        GROUP BY tr.rule_type
        ORDER BY rule_count DESC
    """)

    transform_usage = cursor.fetchall()

    return {
        "process_statistics": process_statistics,
        "connection_usage": connection_usage,
        "transform_usage": transform_usage
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
