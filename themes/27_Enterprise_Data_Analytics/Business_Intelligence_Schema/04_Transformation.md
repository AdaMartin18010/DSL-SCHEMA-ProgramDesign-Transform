# 商业智能Schema转换体系

## 📑 目录

- [商业智能Schema转换体系](#商业智能schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. BI到Tableau转换](#2-bi到tableau转换)
  - [3. BI到Power BI转换](#3-bi到power-bi转换)
  - [4. BI到JSON Schema转换](#4-bi到json-schema转换)
  - [5. BI数据存储与分析](#5-bi数据存储与分析)
    - [5.1 PostgreSQL BI数据存储](#51-postgresql-bi数据存储)
    - [5.2 BI数据分析查询](#52-bi数据分析查询)

---

## 1. 转换体系概述

商业智能Schema转换体系支持BI到Tableau、Power BI、JSON Schema格式转换，以及BI数据存储。

### 1.1 转换目标

1. **BI到Tableau转换**：BI Schema到Tableau格式
2. **BI到Power BI转换**：BI Schema到Power BI格式
3. **BI到JSON Schema转换**：BI Schema到JSON Schema格式
4. **BI到数据库转换**：BI数据到PostgreSQL存储

---

## 2. BI到Tableau转换

**转换规则**：

- 报表定义 → Tableau Workbook
- 仪表板布局 → Tableau Dashboard
- 数据源 → Tableau Data Source

**转换示例**：

```python
def convert_bi_to_tableau(bi_data: BusinessIntelligenceSchema) -> TableauWorkbook:
    """将商业智能Schema转换为Tableau格式"""
    workbook = TableauWorkbook()

    # 转换数据源
    for report in bi_data.reporting.report_definitions:
        data_source = TableauDataSource()
        data_source.name = report.report_name
        data_source.connection = report.data_source
        workbook.data_sources.append(data_source)

    # 转换报表
    for report in bi_data.reporting.report_definitions:
        worksheet = TableauWorksheet()
        worksheet.name = report.report_name

        # 转换报表结构
        for field_name, field_type in report.report_structure.items():
            field = TableauField()
            field.name = field_name
            field.type = map_field_type_to_tableau(field_type)
            worksheet.fields.append(field)

        workbook.worksheets.append(worksheet)

    # 转换仪表板
    for dashboard in bi_data.dashboard.dashboard_layouts:
        tableau_dashboard = TableauDashboard()
        tableau_dashboard.name = dashboard.dashboard_id

        # 转换组件
        for component in bi_data.dashboard.dashboard_components:
            if component.dashboard_id == dashboard.dashboard_id:
                dashboard_object = TableauDashboardObject()
                dashboard_object.type = map_component_type_to_tableau(component.component_type)
                dashboard_object.position = component.component_position
                dashboard_object.config = component.component_config
                tableau_dashboard.objects.append(dashboard_object)

        workbook.dashboards.append(tableau_dashboard)

    return workbook
```

---

## 3. BI到Power BI转换

**转换规则**：

- 报表定义 → Power BI Report
- 仪表板布局 → Power BI Dashboard
- 数据模型 → Power BI Data Model

**转换示例**：

```python
def convert_bi_to_powerbi(bi_data: BusinessIntelligenceSchema) -> PowerBIReport:
    """将商业智能Schema转换为Power BI格式"""
    powerbi_report = PowerBIReport()

    # 转换数据模型
    data_model = PowerBIDataModel()

    for report in bi_data.reporting.report_definitions:
        # 创建表
        table = PowerBITable()
        table.name = report.report_name

        # 转换字段
        for field_name, field_type in report.report_structure.items():
            column = PowerBIColumn()
            column.name = field_name
            column.data_type = map_field_type_to_powerbi(field_type)
            table.columns.append(column)

        data_model.tables.append(table)

    powerbi_report.data_model = data_model

    # 转换报表页面
    for report in bi_data.reporting.report_definitions:
        page = PowerBIPage()
        page.name = report.report_name

        # 转换可视化
        for field_name in report.report_structure.keys():
            visual = PowerBIVisual()
            visual.type = "Table"
            visual.fields = [field_name]
            page.visuals.append(visual)

        powerbi_report.pages.append(page)

    # 转换仪表板
    for dashboard in bi_data.dashboard.dashboard_layouts:
        powerbi_dashboard = PowerBIDashboard()
        powerbi_dashboard.name = dashboard.dashboard_id

        # 转换磁贴
        for component in bi_data.dashboard.dashboard_components:
            if component.dashboard_id == dashboard.dashboard_id:
                tile = PowerBITile()
                tile.title = component.component_id
                tile.visual_type = map_component_type_to_powerbi(component.component_type)
                tile.position = component.component_position
                powerbi_dashboard.tiles.append(tile)

        powerbi_report.dashboards.append(powerbi_dashboard)

    return powerbi_report
```

---

## 4. BI到JSON Schema转换

**转换规则**：

- 报表定义 → JSON Schema Object
- 仪表板布局 → JSON Schema Object
- 数据模型 → JSON Schema Properties

**转换示例**：

```python
def convert_bi_to_json_schema(bi_data: BusinessIntelligenceSchema) -> JSONSchema:
    """将商业智能Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # 转换报表
    for report in bi_data.reporting.report_definitions:
        report_schema = {
            "type": "object",
            "properties": {}
        }

        # 转换报表结构
        for field_name, field_type in report.report_structure.items():
            report_schema["properties"][field_name] = {
                "type": map_field_type_to_json_type(field_type),
                "description": field_name
            }

        json_schema["properties"][report.report_name] = report_schema

    # 转换仪表板
    for dashboard in bi_data.dashboard.dashboard_layouts:
        dashboard_schema = {
            "type": "object",
            "properties": {
                "layout_id": {"type": "string"},
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component_id": {"type": "string"},
                            "component_type": {"type": "string"},
                            "position": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"},
                                    "width": {"type": "integer"},
                                    "height": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            }
        }

        json_schema["properties"][dashboard.dashboard_id] = dashboard_schema

    return json_schema
```

---

## 5. BI数据存储与分析

### 5.1 PostgreSQL BI数据存储

**表结构设计**：

```sql
-- 报表定义表
CREATE TABLE report_definitions (
    report_id VARCHAR(50) PRIMARY KEY,
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(20) NOT NULL,
    data_source VARCHAR(500) NOT NULL,
    report_format VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 报表生成记录表
CREATE TABLE report_generations (
    generation_id VARCHAR(50) PRIMARY KEY,
    report_id VARCHAR(50) NOT NULL,
    generation_time TIMESTAMP NOT NULL,
    generation_status VARCHAR(20) DEFAULT 'Pending',
    generation_result TEXT,
    FOREIGN KEY (report_id) REFERENCES report_definitions(report_id)
);

-- 仪表板定义表
CREATE TABLE dashboard_definitions (
    dashboard_id VARCHAR(50) PRIMARY KEY,
    dashboard_name VARCHAR(200) NOT NULL,
    layout_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 仪表板组件表
CREATE TABLE dashboard_components (
    component_id VARCHAR(50) PRIMARY KEY,
    dashboard_id VARCHAR(50) NOT NULL,
    component_type VARCHAR(20) NOT NULL,
    component_config JSONB,
    position_x INT NOT NULL,
    position_y INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    data_source VARCHAR(500),
    FOREIGN KEY (dashboard_id) REFERENCES dashboard_definitions(dashboard_id)
);

-- 数据挖掘任务表
CREATE TABLE mining_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_type VARCHAR(20) NOT NULL,
    task_objective TEXT NOT NULL,
    input_data VARCHAR(500) NOT NULL,
    task_parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_report_generations_report ON report_generations(report_id);
CREATE INDEX idx_report_generations_status ON report_generations(generation_status);
CREATE INDEX idx_dashboard_components_dashboard ON dashboard_components(dashboard_id);
CREATE INDEX idx_mining_tasks_type ON mining_tasks(task_type);
```

### 5.2 BI数据分析查询

**查询示例**：

```python
def analyze_bi_data(conn):
    """分析商业智能数据"""
    cursor = conn.cursor()

    # 查询报表使用情况
    cursor.execute("""
        SELECT
            rd.report_type,
            COUNT(DISTINCT rd.report_id) as report_count,
            COUNT(rg.generation_id) as generation_count,
            SUM(CASE WHEN rg.generation_status = 'Completed' THEN 1 ELSE 0 END) as completed_count
        FROM report_definitions rd
        LEFT JOIN report_generations rg ON rd.report_id = rg.report_id
        GROUP BY rd.report_type
        ORDER BY report_count DESC
    """)

    report_usage = cursor.fetchall()

    # 查询仪表板组件汇总
    cursor.execute("""
        SELECT
            dd.dashboard_name,
            COUNT(dc.component_id) as component_count,
            COUNT(DISTINCT dc.component_type) as component_type_count
        FROM dashboard_definitions dd
        LEFT JOIN dashboard_components dc ON dd.dashboard_id = dc.dashboard_id
        GROUP BY dd.dashboard_id, dd.dashboard_name
        ORDER BY dd.dashboard_name
    """)

    dashboard_summary = cursor.fetchall()

    # 查询数据挖掘任务汇总
    cursor.execute("""
        SELECT
            task_type,
            COUNT(*) as task_count,
            COUNT(DISTINCT task_objective) as objective_count
        FROM mining_tasks
        GROUP BY task_type
        ORDER BY task_count DESC
    """)

    mining_summary = cursor.fetchall()

    return {
        "report_usage": report_usage,
        "dashboard_summary": dashboard_summary,
        "mining_summary": mining_summary
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
