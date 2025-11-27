# KPI管理Schema转换体系

## 📑 目录

- [KPI管理Schema转换体系](#kpi管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. KPI到OLAP Cube转换](#2-kpi到olap-cube转换)
  - [3. KPI到JSON Schema转换](#3-kpi到json-schema转换)
  - [4. KPI到OpenAPI转换](#4-kpi到openapi转换)
  - [5. KPI数据存储与分析](#5-kpi数据存储与分析)
    - [5.1 PostgreSQL KPI数据存储](#51-postgresql-kpi数据存储)
    - [5.2 KPI数据分析查询](#52-kpi数据分析查询)

---

## 1. 转换体系概述

KPI管理Schema转换体系支持KPI到OLAP Cube、JSON Schema、OpenAPI格式转换，以及KPI数据存储。

### 1.1 转换目标

1. **KPI到OLAP Cube转换**：KPI Schema到OLAP多维数据集格式
2. **KPI到JSON Schema转换**：KPI Schema到JSON Schema格式
3. **KPI到OpenAPI转换**：KPI Schema到OpenAPI格式
4. **KPI到数据库转换**：KPI数据到PostgreSQL存储

---

## 2. KPI到OLAP Cube转换

**转换规则**：

- KPI定义 → OLAP维度
- KPI值 → OLAP度量
- KPI分类 → OLAP层次

**转换示例**：

```python
def convert_kpi_to_olap_cube(kpi_data: KPIManagementSchema) -> OLAPCube:
    """将KPI管理Schema转换为OLAP Cube格式"""
    cube = OLAPCube()
    cube.name = "KPI_Cube"

    # 创建时间维度
    time_dimension = Dimension()
    time_dimension.name = "Time"
    time_dimension.attributes = ["Year", "Quarter", "Month", "Week", "Day"]
    cube.dimensions.append(time_dimension)

    # 创建KPI分类维度
    category_dimension = Dimension()
    category_dimension.name = "KPI_Category"
    category_dimension.attributes = ["Category", "Type", "Owner"]
    cube.dimensions.append(category_dimension)

    # 创建组织维度
    org_dimension = Dimension()
    org_dimension.name = "Organization"
    org_dimension.attributes = ["Company", "Department", "Team"]
    cube.dimensions.append(org_dimension)

    # 转换KPI定义为度量
    for kpi in kpi_data.kpi_definition.kpi_definitions:
        measure = Measure()
        measure.name = kpi.kpi_name
        measure.aggregation_function = "AVG"  # 根据KPI类型选择聚合函数
        measure.data_type = map_kpi_type_to_measure_type(kpi.kpi_type)
        cube.measures.append(measure)

    # 转换KPI值为事实数据
    for value in kpi_data.kpi_monitoring.kpi_values:
        fact = Fact()
        fact.dimensions = {
            "Time": value.measurement_date,
            "KPI_Category": find_kpi_category(kpi_data, value.kpi_id),
            "Organization": find_kpi_owner(kpi_data, value.kpi_id)
        }
        fact.measures = {
            find_kpi_name(kpi_data, value.kpi_id): value.value
        }
        cube.facts.append(fact)

    return cube
```

---

## 3. KPI到JSON Schema转换

**转换规则**：

- KPI定义 → JSON Schema Object
- KPI值 → JSON Schema Array
- KPI目标 → JSON Schema Property

**转换示例**：

```python
def convert_kpi_to_json_schema(kpi_data: KPIManagementSchema) -> JSONSchema:
    """将KPI管理Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "kpi_definitions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "kpi_id": {"type": "string"},
                        "kpi_name": {"type": "string"},
                        "kpi_type": {"type": "string"},
                        "calculation_formula": {"type": "string"},
                        "measurement_unit": {"type": "string"}
                    },
                    "required": ["kpi_id", "kpi_name", "kpi_type"]
                }
            },
            "kpi_values": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "kpi_id": {"type": "string"},
                        "value": {"type": "number"},
                        "measurement_date": {"type": "string", "format": "date"},
                        "completion_rate": {"type": "number"}
                    },
                    "required": ["kpi_id", "value", "measurement_date"]
                }
            },
            "kpi_targets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "kpi_id": {"type": "string"},
                        "target_value": {"type": "number"},
                        "target_period": {
                            "type": "object",
                            "properties": {
                                "start_date": {"type": "string", "format": "date"},
                                "end_date": {"type": "string", "format": "date"}
                            }
                        }
                    },
                    "required": ["kpi_id", "target_value"]
                }
            }
        }
    }

    return json_schema
```

---

## 4. KPI到OpenAPI转换

**转换规则**：

- KPI定义 → OpenAPI Schema
- KPI值 → OpenAPI Endpoint
- KPI报告 → OpenAPI Operation

**转换示例**：

```python
def convert_kpi_to_openapi(kpi_data: KPIManagementSchema) -> OpenAPISpec:
    """将KPI管理Schema转换为OpenAPI格式"""
    spec = OpenAPISpec()
    spec.info.title = "KPI Management API"
    spec.info.version = "1.0.0"

    # 定义KPI Schema
    kpi_schema = Schema()
    kpi_schema.type = "object"
    kpi_schema.properties = {
        "kpi_id": {"type": "string"},
        "kpi_name": {"type": "string"},
        "kpi_type": {"type": "string", "enum": ["Financial", "Customer", "Process", "Learning_Growth"]},
        "value": {"type": "number"},
        "target_value": {"type": "number"},
        "completion_rate": {"type": "number"}
    }
    spec.components.schemas["KPI"] = kpi_schema

    # 定义KPI值端点
    get_kpi_values = Operation()
    get_kpi_values.summary = "Get KPI Values"
    get_kpi_values.operation_id = "getKPIValues"
    get_kpi_values.parameters = [
        Parameter(name="kpi_id", in_="query", schema={"type": "string"}),
        Parameter(name="start_date", in_="query", schema={"type": "string", "format": "date"}),
        Parameter(name="end_date", in_="query", schema={"type": "string", "format": "date"})
    ]
    get_kpi_values.responses = {
        "200": Response(
            description="KPI Values",
            content={"application/json": MediaType(schema={"type": "array", "items": {"$ref": "#/components/schemas/KPI"}})}
        )
    }

    path = PathItem()
    path.get = get_kpi_values
    spec.paths["/api/v1/kpi/values"] = path

    return spec
```

---

## 5. KPI数据存储与分析

### 5.1 PostgreSQL KPI数据存储

**表结构设计**：

```sql
-- KPI定义表
CREATE TABLE kpi_definitions (
    kpi_id VARCHAR(50) PRIMARY KEY,
    kpi_name VARCHAR(200) NOT NULL,
    kpi_description TEXT,
    kpi_type VARCHAR(20) NOT NULL,
    kpi_category VARCHAR(100),
    calculation_formula TEXT NOT NULL,
    data_source VARCHAR(500) NOT NULL,
    measurement_unit VARCHAR(50) NOT NULL,
    calculation_frequency VARCHAR(20) DEFAULT 'Monthly',
    owner VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KPI目标表
CREATE TABLE kpi_targets (
    target_id VARCHAR(50) PRIMARY KEY,
    kpi_id VARCHAR(50) NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    target_value DECIMAL(18, 2) NOT NULL,
    target_start_date DATE NOT NULL,
    target_end_date DATE NOT NULL,
    target_owner VARCHAR(200) NOT NULL,
    target_status VARCHAR(20) DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(kpi_id)
);

-- KPI值表
CREATE TABLE kpi_values (
    value_id VARCHAR(50) PRIMARY KEY,
    kpi_id VARCHAR(50) NOT NULL,
    value DECIMAL(18, 2) NOT NULL,
    measurement_date DATE NOT NULL,
    measurement_time TIMESTAMP,
    data_source VARCHAR(500),
    is_actual BOOLEAN DEFAULT TRUE,
    completion_rate DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(kpi_id)
);

-- KPI趋势表
CREATE TABLE kpi_trends (
    trend_id VARCHAR(50) PRIMARY KEY,
    kpi_id VARCHAR(50) NOT NULL,
    trend_start_date DATE NOT NULL,
    trend_end_date DATE NOT NULL,
    trend_direction VARCHAR(20) NOT NULL,
    trend_magnitude DECIMAL(18, 2) NOT NULL,
    trend_confidence DECIMAL(5, 2) DEFAULT 95,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(kpi_id)
);

-- KPI预警表
CREATE TABLE kpi_alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    kpi_id VARCHAR(50) NOT NULL,
    alert_rule TEXT NOT NULL,
    alert_threshold DECIMAL(18, 2) NOT NULL,
    alert_level VARCHAR(20) NOT NULL,
    alert_condition VARCHAR(20) NOT NULL,
    notification_channels TEXT[],
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(kpi_id)
);

-- 创建索引
CREATE INDEX idx_kpi_targets_kpi ON kpi_targets(kpi_id);
CREATE INDEX idx_kpi_values_kpi ON kpi_values(kpi_id);
CREATE INDEX idx_kpi_values_date ON kpi_values(measurement_date);
CREATE INDEX idx_kpi_trends_kpi ON kpi_trends(kpi_id);
CREATE INDEX idx_kpi_alerts_kpi ON kpi_alerts(kpi_id);
```

### 5.2 KPI数据分析查询

**查询示例**：

```python
def analyze_kpi_data(conn):
    """分析KPI数据"""
    cursor = conn.cursor()

    # 查询KPI完成情况
    cursor.execute("""
        SELECT
            kd.kpi_name,
            kd.kpi_type,
            kt.target_value,
            AVG(kv.value) as avg_value,
            AVG(kv.completion_rate) as avg_completion_rate,
            COUNT(kv.value_id) as measurement_count
        FROM kpi_definitions kd
        LEFT JOIN kpi_targets kt ON kd.kpi_id = kt.kpi_id AND kt.target_status = 'Active'
        LEFT JOIN kpi_values kv ON kd.kpi_id = kv.kpi_id
        WHERE kv.measurement_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY kd.kpi_id, kd.kpi_name, kd.kpi_type, kt.target_value
        ORDER BY avg_completion_rate DESC
    """)

    kpi_completion = cursor.fetchall()

    # 查询KPI趋势分析
    cursor.execute("""
        SELECT
            kd.kpi_name,
            kt.trend_direction,
            kt.trend_magnitude,
            kt.trend_confidence
        FROM kpi_definitions kd
        JOIN kpi_trends kt ON kd.kpi_id = kt.kpi_id
        WHERE kt.trend_end_date >= CURRENT_DATE - INTERVAL '90 days'
        ORDER BY kt.trend_end_date DESC
    """)

    kpi_trends = cursor.fetchall()

    # 查询KPI预警统计
    cursor.execute("""
        SELECT
            ka.alert_level,
            COUNT(*) as alert_count,
            COUNT(DISTINCT ka.kpi_id) as kpi_count
        FROM kpi_alerts ka
        WHERE ka.is_enabled = TRUE
        GROUP BY ka.alert_level
        ORDER BY alert_count DESC
    """)

    alert_statistics = cursor.fetchall()

    return {
        "kpi_completion": kpi_completion,
        "kpi_trends": kpi_trends,
        "alert_statistics": alert_statistics
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
