# OLAP Schema转换体系

## 📑 目录

- [OLAP Schema转换体系](#olap-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. OLAP到MDX转换](#2-olap到mdx转换)
  - [3. OLAP到SQL转换](#3-olap到sql转换)
  - [4. OLAP到JSON Schema转换](#4-olap到json-schema转换)
  - [5. OLAP数据存储与分析](#5-olap数据存储与分析)
    - [5.1 PostgreSQL OLAP数据存储](#51-postgresql-olap数据存储)
    - [5.2 OLAP数据分析查询](#52-olap数据分析查询)

---

## 1. 转换体系概述

OLAP Schema转换体系支持OLAP到MDX、SQL、JSON Schema格式转换，以及OLAP数据存储。

### 1.1 转换目标

1. **OLAP到MDX转换**：OLAP Schema到MDX查询格式
2. **OLAP到SQL转换**：OLAP Schema到SQL查询格式
3. **OLAP到JSON Schema转换**：OLAP Schema到JSON Schema格式
4. **OLAP到数据库转换**：OLAP数据到PostgreSQL存储

---

## 2. OLAP到MDX转换

**转换规则**：

- Cube → MDX FROM子句
- 维度 → MDX维度表达式
- 度量 → MDX度量表达式

**转换示例**：

```python
def convert_olap_to_mdx(olap_data: OLAPSchema, query_params: Dict) -> MDXQuery:
    """将OLAP Schema转换为MDX查询"""
    mdx_query = MDXQuery()

    # FROM子句
    mdx_query.from_clause = f"[{olap_data.cubes[0].cube_name}]"

    # SELECT子句 - 度量
    measures = []
    for measure_id in query_params.get("measures", []):
        measure = find_measure(olap_data, measure_id)
        if measure:
            measures.append(f"[Measures].[{measure.measure_name}]")
    mdx_query.select_clause = "SELECT " + " * ".join(measures) + " ON COLUMNS"

    # SELECT子句 - 维度
    dimensions = []
    for dimension_id in query_params.get("dimensions", []):
        dimension = find_dimension(olap_data, dimension_id)
        if dimension:
            hierarchy = dimension.dimension_hierarchies[0]
            dimensions.append(f"[{dimension.dimension_name}].[{hierarchy.hierarchy_name}].Members")
    mdx_query.select_clause += ", " + " * ".join(dimensions) + " ON ROWS"

    # WHERE子句
    if query_params.get("filters"):
        where_clauses = []
        for filter_item in query_params["filters"]:
            where_clauses.append(f"[{filter_item['dimension']}].[{filter_item['hierarchy']}].[{filter_item['member']}]")
        mdx_query.where_clause = "WHERE " + " * ".join(where_clauses)

    return mdx_query
```

---

## 3. OLAP到SQL转换

**转换规则**：

- Cube → SQL FROM子句（事实表）
- 维度 → SQL GROUP BY子句
- 度量 → SQL SELECT子句（聚合函数）

**转换示例**：

```python
def convert_olap_to_sql(olap_data: OLAPSchema, query_params: Dict) -> SQLQuery:
    """将OLAP Schema转换为SQL查询"""
    sql_query = SQLQuery()

    # SELECT子句 - 度量
    select_clauses = []
    for measure_id in query_params.get("measures", []):
        measure = find_measure(olap_data, measure_id)
        if measure:
            aggregation = measure.aggregation_function.upper()
            select_clauses.append(f"{aggregation}({measure.measure_name}) AS {measure.measure_name}")

    # SELECT子句 - 维度
    group_by_clauses = []
    for dimension_id in query_params.get("dimensions", []):
        dimension = find_dimension(olap_data, dimension_id)
        if dimension:
            hierarchy = dimension.dimension_hierarchies[0]
            for level in hierarchy.levels:
                select_clauses.append(f"{level.level_member_property} AS {level.level_name}")
                group_by_clauses.append(level.level_member_property)

    sql_query.select_clause = "SELECT " + ", ".join(select_clauses)

    # FROM子句
    sql_query.from_clause = f"FROM {olap_data.cubes[0].fact_table_name}"

    # JOIN子句 - 维度表
    join_clauses = []
    for dimension_id in query_params.get("dimensions", []):
        dimension = find_dimension(olap_data, dimension_id)
        if dimension:
            join_clauses.append(f"""
                JOIN {dimension.dimension_table_name}
                ON {olap_data.cubes[0].fact_table_name}.{dimension.dimension_key} = {dimension.dimension_table_name}.{dimension.primary_key}
            """)
    sql_query.join_clause = " ".join(join_clauses)

    # WHERE子句
    if query_params.get("filters"):
        where_clauses = []
        for filter_item in query_params["filters"]:
            where_clauses.append(f"{filter_item['dimension']}.{filter_item['attribute']} = '{filter_item['value']}'")
        sql_query.where_clause = "WHERE " + " AND ".join(where_clauses)

    # GROUP BY子句
    if group_by_clauses:
        sql_query.group_by_clause = "GROUP BY " + ", ".join(group_by_clauses)

    return sql_query
```

---

## 4. OLAP到JSON Schema转换

**转换规则**：

- Cube → JSON Schema Object
- 维度 → JSON Schema Property
- 度量 → JSON Schema Property

**转换示例**：

```python
def convert_olap_to_json_schema(olap_data: OLAPSchema) -> JSONSchema:
    """将OLAP Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # 转换Cube
    for cube in olap_data.cubes:
        cube_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换度量
        for measure_id in cube.measures:
            measure = find_measure(olap_data, measure_id)
            if measure:
                cube_schema["properties"][measure.measure_name] = {
                    "type": map_data_type_to_json_type(measure.data_type),
                    "description": measure.measure_name,
                    "aggregation": measure.aggregation_function
                }

        # 转换维度
        for dimension_id in cube.dimensions:
            dimension = find_dimension(olap_data, dimension_id)
            if dimension:
                cube_schema["properties"][dimension.dimension_name] = {
                    "type": "object",
                    "description": dimension.dimension_name,
                    "properties": {}
                }

                for attribute in dimension.attributes:
                    cube_schema["properties"][dimension.dimension_name]["properties"][attribute.attribute_name] = {
                        "type": map_data_type_to_json_type(attribute.data_type),
                        "description": attribute.attribute_name
                    }

        json_schema["properties"][cube.cube_name] = cube_schema

    return json_schema
```

---

## 5. OLAP数据存储与分析

### 5.1 PostgreSQL OLAP数据存储

**表结构设计**：

```sql
-- OLAP Cube元数据表
CREATE TABLE olap_cube_metadata (
    cube_id VARCHAR(50) PRIMARY KEY,
    cube_name VARCHAR(200) NOT NULL,
    cube_type VARCHAR(20) NOT NULL,
    fact_table_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OLAP维度元数据表
CREATE TABLE olap_dimension_metadata (
    dimension_id VARCHAR(50) PRIMARY KEY,
    dimension_name VARCHAR(200) NOT NULL,
    dimension_type VARCHAR(20) NOT NULL,
    dimension_table_name VARCHAR(200) NOT NULL,
    primary_key VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OLAP度量元数据表
CREATE TABLE olap_measure_metadata (
    measure_id VARCHAR(50) PRIMARY KEY,
    cube_id VARCHAR(50) NOT NULL,
    measure_name VARCHAR(200) NOT NULL,
    measure_type VARCHAR(20) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    aggregation_function VARCHAR(50) NOT NULL,
    format_string VARCHAR(50),
    FOREIGN KEY (cube_id) REFERENCES olap_cube_metadata(cube_id)
);

-- OLAP层次元数据表
CREATE TABLE olap_hierarchy_metadata (
    hierarchy_id VARCHAR(50) PRIMARY KEY,
    dimension_id VARCHAR(50) NOT NULL,
    hierarchy_name VARCHAR(200) NOT NULL,
    hierarchy_type VARCHAR(20) NOT NULL,
    is_balanced BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (dimension_id) REFERENCES olap_dimension_metadata(dimension_id)
);

-- OLAP层次级别元数据表
CREATE TABLE olap_hierarchy_level_metadata (
    level_id VARCHAR(50) PRIMARY KEY,
    hierarchy_id VARCHAR(50) NOT NULL,
    level_name VARCHAR(200) NOT NULL,
    level_number INT NOT NULL,
    level_attribute VARCHAR(200) NOT NULL,
    level_cardinality INT,
    FOREIGN KEY (hierarchy_id) REFERENCES olap_hierarchy_metadata(hierarchy_id)
);

-- 创建索引
CREATE INDEX idx_olap_measure_metadata_cube ON olap_measure_metadata(cube_id);
CREATE INDEX idx_olap_hierarchy_metadata_dimension ON olap_hierarchy_metadata(dimension_id);
CREATE INDEX idx_olap_hierarchy_level_metadata_hierarchy ON olap_hierarchy_level_metadata(hierarchy_id);
```

### 5.2 OLAP数据分析查询

**查询示例**：

```python
def analyze_olap_metadata(conn):
    """分析OLAP元数据"""
    cursor = conn.cursor()

    # 查询Cube汇总
    cursor.execute("""
        SELECT
            ocm.cube_name,
            ocm.cube_type,
            COUNT(omm.measure_id) as measure_count,
            COUNT(DISTINCT odm.dimension_id) as dimension_count
        FROM olap_cube_metadata ocm
        LEFT JOIN olap_measure_metadata omm ON ocm.cube_id = omm.cube_id
        LEFT JOIN olap_dimension_metadata odm ON ocm.cube_id = odm.cube_id
        GROUP BY ocm.cube_id, ocm.cube_name, ocm.cube_type
        ORDER BY ocm.cube_name
    """)

    cube_summary = cursor.fetchall()

    # 查询维度层次汇总
    cursor.execute("""
        SELECT
            odm.dimension_name,
            ohm.hierarchy_name,
            ohm.hierarchy_type,
            COUNT(ohlm.level_id) as level_count
        FROM olap_dimension_metadata odm
        JOIN olap_hierarchy_metadata ohm ON odm.dimension_id = ohm.dimension_id
        LEFT JOIN olap_hierarchy_level_metadata ohlm ON ohm.hierarchy_id = ohlm.hierarchy_id
        GROUP BY odm.dimension_id, odm.dimension_name, ohm.hierarchy_id, ohm.hierarchy_name, ohm.hierarchy_type
        ORDER BY odm.dimension_name, ohm.hierarchy_name
    """)

    hierarchy_summary = cursor.fetchall()

    return {
        "cube_summary": cube_summary,
        "hierarchy_summary": hierarchy_summary
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
