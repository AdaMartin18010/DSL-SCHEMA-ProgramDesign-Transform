# ETL Schema实践案例

## 📑 目录

- [ETL Schema实践案例](#etl-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：销售数据ETL流程](#2-案例1销售数据etl流程)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：ETL到Informatica转换](#3-案例2etl到informatica转换)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
  - [4. 案例3：增量ETL流程](#4-案例3增量etl流程)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：数据质量检查ETL](#5-案例4数据质量检查etl)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：ETL数据存储与分析系统](#6-案例5etl数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供ETL Schema在实际应用中的实践案例。

---

## 2. 案例1：销售数据ETL流程

### 2.1 场景描述

**应用场景**：
构建销售数据ETL流程，从源系统提取销售数据，进行数据转换和清洗，加载到数据仓库。

**业务需求**：

- 支持增量数据提取
- 支持数据转换和清洗
- 支持数据加载到数据仓库

### 2.2 Schema定义

**销售数据ETL流程Schema**：

```dsl
schema SalesDataETL {
  extract_rule: ExtractRule {
    rule_id: String @value("RULE-SALES-EXTRACT")
    connection_id: String @value("CONN-SALES-DB")
    source_table: String @value("sales_transactions")
    extract_condition: String @value("sale_date >= :last_extract_date")
    extract_fields: List<String> {
      "sale_id"
      "sale_date"
      "customer_id"
      "product_id"
      "sale_amount"
      "sale_quantity"
    }
    extract_frequency: Enum @value("Daily")
  }

  transform_rule: TransformRule {
    rule_id: String @value("RULE-SALES-TRANSFORM")
    rule_name: String @value("销售数据转换")
    rule_type: Enum @value("Mapping")
    source_fields: List<String> {
      "sale_id"
      "sale_date"
      "customer_id"
      "product_id"
      "sale_amount"
      "sale_quantity"
    }
    target_fields: List<String> {
      "sale_id"
      "sale_date"
      "customer_key"
      "product_key"
      "sale_amount"
      "sale_quantity"
    }
    transform_logic: String @value("customer_key = lookup_customer(customer_id); product_key = lookup_product(product_id);")
  }

  load_strategy: LoadStrategy {
    strategy_id: String @value("STRATEGY-SALES-LOAD")
    table_id: String @value("TBL-FACT-SALES")
    strategy_type: Enum @value("Incremental_Load")
    load_frequency: Enum @value("Daily")
  }

  etl_process: ProcessDefinition {
    process_id: String @value("PROC-SALES-ETL")
    process_name: String @value("销售数据ETL流程")
    process_type: Enum @value("Batch")
    extract_rule_id: String @value("RULE-SALES-EXTRACT")
    transform_rule_ids: List<String> {
      "RULE-SALES-TRANSFORM"
    }
    load_strategy_id: String @value("STRATEGY-SALES-LOAD")
  }
}
```

---

## 3. 案例2：ETL到Informatica转换

### 3.1 场景描述

**应用场景**：
将ETL Schema转换为Informatica Workflow格式，用于Informatica执行。

**业务需求**：

- 支持自动转换到Informatica
- 支持数据源连接配置
- 支持转换逻辑配置

### 3.2 实现代码

```python
def convert_etl_to_informatica_complete(etl_data: ETLSchema) -> InformaticaWorkflow:
    """完整转换ETL Schema到Informatica"""
    workflow = InformaticaWorkflow()
    workflow.name = "ETL_Workflow"

    # 转换数据源连接
    connections_map = {}
    for connection in etl_data.extract.data_source_connections:
        infa_connection = InformaticaConnection()
        infa_connection.name = connection.connection_name
        infa_connection.type = map_connection_type_to_informatica(connection.connection_type)
        infa_connection.connection_string = connection.connection_string

        # 转换连接参数
        if connection.connection_type == "Database":
            infa_connection.properties = {
                "database_type": connection.connection_parameters.get("database_type", "Oracle"),
                "host": connection.connection_parameters.get("host", ""),
                "port": connection.connection_parameters.get("port", "1521"),
                "database_name": connection.connection_parameters.get("database_name", ""),
                "username": connection.authentication.credentials.get("username", ""),
                "password": connection.authentication.credentials.get("password", "")
            }
        elif connection.connection_type == "File":
            infa_connection.properties = {
                "file_type": connection.connection_parameters.get("file_type", "Delimited"),
                "file_path": connection.connection_string
            }

        workflow.connections.append(infa_connection)
        connections_map[connection.connection_id] = infa_connection

    # 转换ETL流程
    for process in etl_data.etl_process.process_definitions:
        # 创建映射
        mapping = InformaticaMapping()
        mapping.name = f"{process.process_name}_Mapping"

        # 转换提取规则
        extract_rule = find_extract_rule(etl_data, process.extract_rule_id)
        connection = connections_map[extract_rule.connection_id]

        source = InformaticaSource()
        source.name = extract_rule.source_table or "Source"
        source.connection = connection.name
        source.type = "Relational"

        # 转换字段
        for field in extract_rule.extract_fields:
            source_field = InformaticaSourceField()
            source_field.name = field
            source_field.data_type = infer_data_type(field)
            source.fields.append(source_field)

        if extract_rule.source_query:
            source.query = extract_rule.source_query
        elif extract_rule.extract_condition:
            source.query = f"SELECT * FROM {extract_rule.source_table} WHERE {extract_rule.extract_condition}"

        mapping.sources.append(source)

        # 转换转换规则
        prev_output = source
        for transform_rule_id in process.transform_rule_ids:
            transform_rule = find_transform_rule(etl_data, transform_rule_id)

            if transform_rule.rule_type == "Mapping":
                # 字段映射转换
                transformation = InformaticaExpression()
                transformation.name = f"{transform_rule.rule_name}_Expression"

                for i, source_field in enumerate(transform_rule.source_fields):
                    target_field = InformaticaField()
                    target_field.name = transform_rule.target_fields[i]
                    target_field.data_type = infer_data_type(transform_rule.target_fields[i])
                    target_field.expression = f"{prev_output.name}.{source_field}"
                    transformation.fields.append(target_field)

                mapping.transformations.append(transformation)
                prev_output = transformation

            elif transform_rule.rule_type == "Calculation":
                # 计算转换
                transformation = InformaticaExpression()
                transformation.name = f"{transform_rule.rule_name}_Expression"

                for target_field in transform_rule.target_fields:
                    field = InformaticaField()
                    field.name = target_field
                    field.expression = extract_calculation_expression(transform_rule.transform_logic, target_field)
                    transformation.fields.append(field)

                mapping.transformations.append(transformation)
                prev_output = transformation

        # 转换加载策略
        load_strategy = find_load_strategy(etl_data, process.load_strategy_id)
        target_table = find_target_table(etl_data, load_strategy.table_id)

        target = InformaticaTarget()
        target.name = target_table.table_name
        target.type = "Relational"
        target.connection = create_target_connection(workflow, target_table).name
        target.load_mode = map_load_mode_to_informatica(load_strategy)

        # 转换字段
        for field_name, field_type in target_table.table_structure.items():
            target_field = InformaticaTargetField()
            target_field.name = field_name
            target_field.data_type = map_data_type_to_informatica(field_type)
            target.fields.append(target_field)

        mapping.targets.append(target)

        # 创建连接
        create_mapping_links(mapping, prev_output, target)

        workflow.mappings.append(mapping)

        # 创建会话
        session = InformaticaSession()
        session.name = f"{process.process_name}_Session"
        session.mapping = mapping.name
        session.source_connection = connection.name
        session.target_connection = target.connection
        session.commit_interval = 10000
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

## 4. 案例3：增量ETL流程

### 4.1 场景描述

**应用场景**：
构建增量ETL流程，支持基于时间戳的增量数据提取和加载。

**业务需求**：

- 支持增量数据提取
- 支持增量数据加载
- 支持增量状态管理

### 4.2 实现代码

```python
def execute_incremental_etl(etl_data: ETLSchema, process_id: str) -> ExecutionResult:
    """执行增量ETL流程"""
    process = find_process(etl_data, process_id)
    extract_rule = find_extract_rule(etl_data, process.extract_rule_id)
    incremental_extract = find_incremental_extract(etl_data, extract_rule.rule_id)

    # 获取上次提取值
    last_extract_value = incremental_extract.last_extract_value
    last_extract_time = incremental_extract.last_extract_time

    # 执行提取
    if incremental_extract.incremental_strategy == "Timestamp":
        extract_condition = f"{incremental_extract.incremental_field} > '{last_extract_time}'"
    elif incremental_extract.incremental_strategy == "Sequence":
        extract_condition = f"{incremental_extract.incremental_field} > {last_extract_value}"
    elif incremental_extract.incremental_strategy == "Change_Data_Capture":
        extract_condition = f"change_type IN ('INSERT', 'UPDATE')"

    # 更新提取条件
    extract_rule.extract_condition = extract_condition

    # 执行ETL
    result = execute_etl_process(etl_data, process_id)

    # 更新增量状态
    if result.status == "Completed":
        # 获取本次提取的最大值
        new_max_value = get_max_incremental_value(
            extract_rule.connection_id,
            incremental_extract.incremental_field,
            extract_condition
        )

        # 更新增量提取记录
        incremental_extract.last_extract_value = str(new_max_value)
        incremental_extract.last_extract_time = datetime.now()

    return result
```

---

## 5. 案例4：数据质量检查ETL

### 5.1 场景描述

**应用场景**：
在ETL流程中添加数据质量检查步骤，确保数据质量。

**业务需求**：

- 支持数据质量检查
- 支持数据质量报告
- 支持数据质量修复

### 5.2 实现代码

```python
def add_data_quality_check(etl_data: ETLSchema, process_id: str, quality_rules: List[QualityRule]):
    """添加数据质量检查"""
    process = find_process(etl_data, process_id)

    # 创建数据质量检查转换规则
    for quality_rule in quality_rules:
        transform_rule = TransformRule()
        transform_rule.rule_id = f"RULE-QC-{quality_rule.rule_id}"
        transform_rule.rule_name = f"数据质量检查-{quality_rule.rule_name}"
        transform_rule.rule_type = "Validate"
        transform_rule.source_fields = quality_rule.fields
        transform_rule.target_fields = [f"{field}_valid" for field in quality_rule.fields]
        transform_rule.transform_logic = quality_rule.validation_rule

        # 添加数据清洗规则
        if quality_rule.cleaning_enabled:
            cleaning = DataCleaning()
            cleaning.cleaning_id = f"CLEAN-{quality_rule.rule_id}"
            cleaning.rule_id = transform_rule.rule_id
            cleaning.cleaning_type = quality_rule.cleaning_type
            cleaning.cleaning_rule = quality_rule.cleaning_rule
            transform_rule.data_cleaning.append(cleaning)

        etl_data.transform.transform_rules.append(transform_rule)
        process.transform_rule_ids.append(transform_rule.rule_id)

    return etl_data

def execute_etl_with_quality_check(etl_data: ETLSchema, process_id: str) -> ExecutionResult:
    """执行带数据质量检查的ETL"""
    process = find_process(etl_data, process_id)

    # 执行提取
    extract_result = execute_extract(etl_data, process.extract_rule_id)

    if extract_result.status != "Success":
        return ExecutionResult(status="Failed", error=extract_result.error)

    # 执行转换和质量检查
    for transform_rule_id in process.transform_rule_ids:
        transform_rule = find_transform_rule(etl_data, transform_rule_id)

        # 执行转换
        transform_result = execute_transform(transform_rule, extract_result.data)

        if transform_result.status != "Success":
            return ExecutionResult(status="Failed", error=transform_result.error)

        # 执行数据质量检查
        if transform_rule.rule_type == "Validate":
            quality_result = execute_quality_check(transform_rule, transform_result.data)

            if quality_result.passed:
                # 执行数据清洗
                if transform_rule.data_cleaning:
                    for cleaning in transform_rule.data_cleaning:
                        transform_result.data = execute_cleaning(cleaning, transform_result.data)
            else:
                # 生成质量报告
                quality_report = generate_quality_report(quality_result)
                log_quality_issues(quality_report)

                # 根据错误处理策略决定是否继续
                if quality_result.error_action == "Stop":
                    return ExecutionResult(status="Failed", error="Data quality check failed")

        extract_result.data = transform_result.data

    # 执行加载
    load_result = execute_load(etl_data, process.load_strategy_id, extract_result.data)

    return ExecutionResult(
        status=load_result.status,
        rows_extracted=extract_result.rows_count,
        rows_transformed=len(extract_result.data),
        rows_loaded=load_result.rows_count
    )
```

---

## 6. 案例5：ETL数据存储与分析系统

### 6.1 场景描述

**应用场景**：
ETL数据存储与分析系统，支持ETL元数据存储、查询、分析。

**业务需求**：

- 支持ETL元数据存储
- 支持ETL执行历史查询
- 支持ETL性能分析

### 6.2 实现代码

```python
def store_etl_data(etl_data: ETLSchema, conn):
    """存储ETL数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储数据源连接
    for connection in etl_data.extract.data_source_connections:
        cursor.execute("""
            INSERT INTO data_source_connections
            (connection_id, connection_name, connection_type, connection_string, connection_parameters, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (connection_id) DO UPDATE SET
            connection_name = EXCLUDED.connection_name,
            connection_string = EXCLUDED.connection_string,
            connection_parameters = EXCLUDED.connection_parameters,
            is_active = EXCLUDED.is_active,
            updated_at = CURRENT_TIMESTAMP
        """, (connection.connection_id, connection.connection_name,
              connection.connection_type, connection.connection_string,
              json.dumps(connection.connection_parameters), connection.is_active))

    # 存储提取规则
    for rule in etl_data.extract.extract_rules:
        cursor.execute("""
            INSERT INTO extract_rules
            (rule_id, connection_id, source_table, source_query, extract_condition, extract_fields, extract_frequency)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rule_id) DO UPDATE SET
            source_table = EXCLUDED.source_table,
            source_query = EXCLUDED.source_query,
            extract_condition = EXCLUDED.extract_condition,
            extract_fields = EXCLUDED.extract_fields,
            extract_frequency = EXCLUDED.extract_frequency
        """, (rule.rule_id, rule.connection_id, rule.source_table,
              rule.source_query, rule.extract_condition,
              rule.extract_fields, rule.extract_frequency))

    # 存储转换规则
    for rule in etl_data.transform.transform_rules:
        cursor.execute("""
            INSERT INTO transform_rules
            (rule_id, rule_name, rule_type, source_fields, target_fields, transform_logic, transform_parameters)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rule_id) DO UPDATE SET
            rule_name = EXCLUDED.rule_name,
            rule_type = EXCLUDED.rule_type,
            source_fields = EXCLUDED.source_fields,
            target_fields = EXCLUDED.target_fields,
            transform_logic = EXCLUDED.transform_logic,
            transform_parameters = EXCLUDED.transform_parameters
        """, (rule.rule_id, rule.rule_name, rule.rule_type,
              rule.source_fields, rule.target_fields,
              rule.transform_logic, json.dumps(rule.transform_parameters)))

    # 存储目标表
    for table in etl_data.load.target_tables:
        cursor.execute("""
            INSERT INTO target_tables
            (table_id, table_name, table_schema, table_type, table_structure, primary_key)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (table_id) DO UPDATE SET
            table_name = EXCLUDED.table_name,
            table_schema = EXCLUDED.table_schema,
            table_type = EXCLUDED.table_type,
            table_structure = EXCLUDED.table_structure,
            primary_key = EXCLUDED.primary_key
        """, (table.table_id, table.table_name, table.table_schema,
              table.table_type, json.dumps(table.table_structure), table.primary_key))

    # 存储加载策略
    for strategy in etl_data.load.load_strategies:
        cursor.execute("""
            INSERT INTO load_strategies
            (strategy_id, table_id, strategy_type, strategy_parameters, load_frequency)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (strategy_id) DO UPDATE SET
            strategy_type = EXCLUDED.strategy_type,
            strategy_parameters = EXCLUDED.strategy_parameters,
            load_frequency = EXCLUDED.load_frequency
        """, (strategy.strategy_id, strategy.table_id,
              strategy.strategy_type, json.dumps(strategy.strategy_parameters),
              strategy.load_frequency))

    # 存储ETL流程定义
    for process in etl_data.etl_process.process_definitions:
        cursor.execute("""
            INSERT INTO etl_process_definitions
            (process_id, process_name, process_type, extract_rule_id, transform_rule_ids, load_strategy_id, process_dependencies, process_parameters)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (process_id) DO UPDATE SET
            process_name = EXCLUDED.process_name,
            process_type = EXCLUDED.process_type,
            extract_rule_id = EXCLUDED.extract_rule_id,
            transform_rule_ids = EXCLUDED.transform_rule_ids,
            load_strategy_id = EXCLUDED.load_strategy_id,
            process_dependencies = EXCLUDED.process_dependencies,
            process_parameters = EXCLUDED.process_parameters
        """, (process.process_id, process.process_name, process.process_type,
              process.extract_rule_id, process.transform_rule_ids,
              process.load_strategy_id, process.process_dependencies,
              json.dumps(process.process_parameters)))

    conn.commit()

def generate_etl_report(conn):
    """生成ETL报表"""
    cursor = conn.cursor()

    # 查询ETL流程执行统计
    cursor.execute("""
        SELECT
            epd.process_name,
            epd.process_type,
            COUNT(eh.execution_id) as total_executions,
            SUM(CASE WHEN eh.execution_status = 'Completed' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN eh.execution_status = 'Failed' THEN 1 ELSE 0 END) as failed_count,
            AVG(eh.rows_loaded) as avg_rows_loaded,
            AVG(EXTRACT(EPOCH FROM (eh.execution_end_time - eh.execution_start_time))) as avg_duration_seconds
        FROM etl_process_definitions epd
        LEFT JOIN etl_execution_history eh ON epd.process_id = eh.process_id
        WHERE eh.execution_start_time >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY epd.process_id, epd.process_name, epd.process_type
        ORDER BY total_executions DESC
    """)

    process_statistics = cursor.fetchall()

    # 查询数据源连接使用情况
    cursor.execute("""
        SELECT
            dsc.connection_type,
            COUNT(DISTINCT dsc.connection_id) as connection_count,
            COUNT(DISTINCT er.rule_id) as extract_rule_count,
            COUNT(DISTINCT epd.process_id) as process_count
        FROM data_source_connections dsc
        LEFT JOIN extract_rules er ON dsc.connection_id = er.connection_id
        LEFT JOIN etl_process_definitions epd ON er.rule_id = epd.extract_rule_id
        WHERE dsc.is_active = TRUE
        GROUP BY dsc.connection_type
        ORDER BY connection_count DESC
    """)

    connection_usage = cursor.fetchall()

    return {
        "process_statistics": process_statistics,
        "connection_usage": connection_usage
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
