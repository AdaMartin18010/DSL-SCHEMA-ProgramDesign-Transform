# 商业智能Schema实践案例

## 📑 目录

- [商业智能Schema实践案例](#商业智能schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：销售分析仪表板](#2-案例1销售分析仪表板)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：BI到Tableau转换](#3-案例2bi到tableau转换)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
  - [4. 案例3：报表生成系统](#4-案例3报表生成系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：数据挖掘分析系统](#5-案例4数据挖掘分析系统)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：BI数据存储与分析系统](#6-案例5bi数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供商业智能Schema在实际应用中的实践案例。

---

## 2. 案例1：销售分析仪表板

### 2.1 场景描述

**应用场景**：
构建销售分析仪表板，包含销售趋势图表、区域销售分布、产品销售排行等组件。

**业务需求**：

- 支持多图表展示
- 支持数据筛选和钻取
- 支持实时数据更新

### 2.2 Schema定义

**销售分析仪表板Schema**：

```dsl
schema SalesAnalysisDashboard {
  dashboard: Dashboard {
    dashboard_id: String @value("DASH-SALES-001")
    dashboard_name: String @value("销售分析仪表板")
    dashboard_layout: DashboardLayout {
      layout_id: String @value("LAYOUT-SALES-001")
      layout_structure: Map<String, Integer> {
        "rows": Int @value(4)
        "columns": Int @value(4)
      }
      component_positions: Map<String, Map<String, Integer>> {
        "sales_trend_chart": Map<String, Integer> {
          "row": Int @value(0)
          "column": Int @value(0)
          "width": Int @value(2)
          "height": Int @value(2)
        }
      }
    }
    dashboard_components: List<DashboardComponent> {
      sales_trend_chart: DashboardComponent {
        component_id: String @value("COMP-SALES-TREND")
        component_type: Enum @value("Chart")
        component_config: Map<String, String> {
          "chart_type": String @value("Line")
          "x_axis": String @value("date")
          "y_axis": String @value("sales_amount")
        }
        data_source: String @value("sales_data")
      }
    }
  }
}
```

---

## 3. 案例2：BI到Tableau转换

### 3.1 场景描述

**应用场景**：
将商业智能Schema转换为Tableau Workbook格式，用于Tableau可视化。

**业务需求**：

- 支持自动转换到Tableau
- 支持数据源连接
- 支持可视化配置

### 3.2 实现代码

```python
def convert_bi_to_tableau_complete(bi_data: BusinessIntelligenceSchema) -> TableauWorkbook:
    """完整转换商业智能Schema到Tableau"""
    workbook = TableauWorkbook()

    # 转换数据源
    data_sources = {}
    for report in bi_data.reporting.report_definitions:
        if report.data_source not in data_sources:
            data_source = TableauDataSource()
            data_source.name = report.data_source
            data_source.connection_type = "PostgreSQL"
            data_source.connection_string = f"server={report.data_source};database=bi_db;"
            workbook.data_sources[report.data_source] = data_source

    # 转换报表
    for report in bi_data.reporting.report_definitions:
        worksheet = TableauWorksheet()
        worksheet.name = report.report_name
        worksheet.data_source = workbook.data_sources[report.data_source]

        # 转换字段
        for field_name, field_type in report.report_structure.items():
            field = TableauField()
            field.name = field_name
            field.type = map_field_type_to_tableau(field_type)
            field.role = "Dimension" if field_type in ["String", "Date"] else "Measure"
            worksheet.fields.append(field)

        # 创建默认可视化
        if report.report_type == "Standard":
            visual = TableauVisual()
            visual.type = "Table"
            visual.fields = [f.name for f in worksheet.fields]
            worksheet.visuals.append(visual)

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
                dashboard_object.position = {
                    "x": component.component_position.get("x", 0),
                    "y": component.component_position.get("y", 0),
                    "width": component.component_position.get("width", 200),
                    "height": component.component_position.get("height", 150)
                }

                # 创建对应的Worksheet
                worksheet = create_worksheet_from_component(component)
                workbook.worksheets.append(worksheet)
                dashboard_object.worksheet = worksheet.name

                dashboard_object.config = component.component_config
                tableau_dashboard.objects.append(dashboard_object)

        workbook.dashboards.append(tableau_dashboard)

    return workbook
```

---

## 4. 案例3：报表生成系统

### 4.1 场景描述

**应用场景**：
基于报表定义自动生成报表，支持多种格式导出。

**业务需求**：

- 支持报表自动生成
- 支持多格式导出
- 支持报表分发

### 4.2 实现代码

```python
def generate_report(report_id: str, bi_data: BusinessIntelligenceSchema, parameters: dict) -> Report:
    """生成报表"""
    report_def = find_report_definition(bi_data, report_id)

    # 查询数据
    data = query_report_data(
        report_def.data_source,
        report_def.report_structure,
        parameters
    )

    # 生成报表
    report = Report()
    report.report_id = f"REPORT-{report_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    report.report_name = report_def.report_name
    report.report_format = report_def.report_format
    report.report_data = data

    # 根据格式生成报表
    if report_def.report_format == "PDF":
        report.content = generate_pdf_report(report_def, data)
    elif report_def.report_format == "Excel":
        report.content = generate_excel_report(report_def, data)
    elif report_def.report_format == "HTML":
        report.content = generate_html_report(report_def, data)

    # 记录生成历史
    generation = ReportGeneration()
    generation.generation_id = f"GEN-{report.report_id}"
    generation.report_id = report_id
    generation.generation_time = datetime.now()
    generation.generation_status = "Completed"
    generation.generation_result = report.report_id

    bi_data.reporting.report_generation.append(generation)

    return report

def distribute_report(report_id: str, bi_data: BusinessIntelligenceSchema, recipients: List[str]):
    """分发报表"""
    report = find_report(bi_data, report_id)

    for recipient in recipients:
        distribution = ReportDistribution()
        distribution.distribution_id = f"DIST-{report_id}-{recipient}"
        distribution.report_id = report_id
        distribution.recipients = [recipient]
        distribution.distribution_method = "Email"
        distribution.distribution_status = "Pending"

        # 发送报表
        send_report_email(recipient, report)

        distribution.distribution_status = "Sent"
        distribution.distribution_time = datetime.now()

        bi_data.reporting.report_distribution.append(distribution)
```

---

## 5. 案例4：数据挖掘分析系统

### 5.1 场景描述

**应用场景**：
构建数据挖掘分析系统，支持分类、聚类、关联规则挖掘。

**业务需求**：

- 支持多种挖掘算法
- 支持挖掘结果可视化
- 支持挖掘模型评估

### 5.2 实现代码

```python
def execute_mining_task(task_id: str, bi_data: BusinessIntelligenceSchema) -> MiningResult:
    """执行数据挖掘任务"""
    task = find_mining_task(bi_data, task_id)
    algorithm = find_mining_algorithm(bi_data, task_id)

    # 加载数据
    data = load_mining_data(task.input_data)

    # 执行挖掘
    if task.task_type == "Classification":
        result = execute_classification(data, algorithm)
    elif task.task_type == "Clustering":
        result = execute_clustering(data, algorithm)
    elif task.task_type == "Association":
        result = execute_association(data, algorithm)
    elif task.task_type == "Regression":
        result = execute_regression(data, algorithm)

    # 创建挖掘结果
    mining_result = MiningResult()
    mining_result.result_id = f"RESULT-{task_id}"
    mining_result.task_id = task_id
    mining_result.result_type = task.task_type
    mining_result.result_data = result
    mining_result.confidence_score = calculate_confidence(result)
    mining_result.result_timestamp = datetime.now()

    bi_data.data_mining.mining_results.append(mining_result)

    return mining_result

def visualize_mining_result(result_id: str, bi_data: BusinessIntelligenceSchema) -> Visualization:
    """可视化挖掘结果"""
    result = find_mining_result(bi_data, result_id)

    # 创建可视化
    visualization = Visualization()
    visualization.visualization_id = f"VIZ-{result_id}"
    visualization.result_id = result_id

    if result.result_type == "Classification":
        # 分类结果可视化：混淆矩阵
        visualization.visualization_type = "ConfusionMatrix"
        visualization.visualization_data = create_confusion_matrix(result.result_data)
    elif result.result_type == "Clustering":
        # 聚类结果可视化：散点图
        visualization.visualization_type = "ScatterPlot"
        visualization.visualization_data = create_cluster_scatter(result.result_data)
    elif result.result_type == "Association":
        # 关联规则可视化：网络图
        visualization.visualization_type = "NetworkGraph"
        visualization.visualization_data = create_association_network(result.result_data)

    return visualization
```

---

## 6. 案例5：BI数据存储与分析系统

### 6.1 场景描述

**应用场景**：
BI数据存储与分析系统，支持元数据存储、查询、分析。

**业务需求**：

- 支持BI元数据存储
- 支持元数据查询和分析
- 支持使用情况分析

### 6.2 实现代码

```python
def store_bi_data(bi_data: BusinessIntelligenceSchema, conn):
    """存储商业智能数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储报表定义
    for report in bi_data.reporting.report_definitions:
        cursor.execute("""
            INSERT INTO report_definitions
            (report_id, report_name, report_type, data_source, report_format)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (report_id) DO UPDATE SET
            report_name = EXCLUDED.report_name,
            report_type = EXCLUDED.report_type,
            data_source = EXCLUDED.data_source,
            report_format = EXCLUDED.report_format,
            updated_at = CURRENT_TIMESTAMP
        """, (report.report_id, report.report_name, report.report_type,
              report.data_source, report.report_format))

        # 存储报表生成记录
        for generation in bi_data.reporting.report_generation:
            if generation.report_id == report.report_id:
                cursor.execute("""
                    INSERT INTO report_generations
                    (generation_id, report_id, generation_time, generation_status, generation_result)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (generation_id) DO UPDATE SET
                    generation_status = EXCLUDED.generation_status,
                    generation_result = EXCLUDED.generation_result
                """, (generation.generation_id, generation.report_id,
                      generation.generation_time, generation.generation_status,
                      generation.generation_result))

    # 存储仪表板定义
    for dashboard in bi_data.dashboard.dashboard_layouts:
        cursor.execute("""
            INSERT INTO dashboard_definitions
            (dashboard_id, dashboard_name, layout_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (dashboard_id) DO UPDATE SET
            dashboard_name = EXCLUDED.dashboard_name,
            layout_type = EXCLUDED.layout_type,
            updated_at = CURRENT_TIMESTAMP
        """, (dashboard.dashboard_id, dashboard.dashboard_id, dashboard.layout_structure.get("layout_type", "Grid")))

        # 存储仪表板组件
        for component in bi_data.dashboard.dashboard_components:
            if component.dashboard_id == dashboard.dashboard_id:
                cursor.execute("""
                    INSERT INTO dashboard_components
                    (component_id, dashboard_id, component_type, component_config,
                     position_x, position_y, width, height, data_source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (component_id) DO UPDATE SET
                    component_type = EXCLUDED.component_type,
                    component_config = EXCLUDED.component_config,
                    position_x = EXCLUDED.position_x,
                    position_y = EXCLUDED.position_y,
                    width = EXCLUDED.width,
                    height = EXCLUDED.height,
                    data_source = EXCLUDED.data_source
                """, (component.component_id, component.dashboard_id,
                      component.component_type, json.dumps(component.component_config),
                      component.component_position.get("x", 0),
                      component.component_position.get("y", 0),
                      component.component_position.get("width", 200),
                      component.component_position.get("height", 150),
                      component.data_source))

    # 存储数据挖掘任务
    for task in bi_data.data_mining.mining_tasks:
        cursor.execute("""
            INSERT INTO mining_tasks
            (task_id, task_type, task_objective, input_data, task_parameters)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (task_id) DO UPDATE SET
            task_objective = EXCLUDED.task_objective,
            input_data = EXCLUDED.input_data,
            task_parameters = EXCLUDED.task_parameters
        """, (task.task_id, task.task_type, task.task_objective,
              task.input_data, json.dumps(task.task_parameters)))

    conn.commit()

def generate_bi_report(conn):
    """生成商业智能报表"""
    cursor = conn.cursor()

    # 查询报表使用情况
    cursor.execute("""
        SELECT
            rd.report_type,
            COUNT(DISTINCT rd.report_id) as report_count,
            COUNT(rg.generation_id) as total_generations,
            SUM(CASE WHEN rg.generation_status = 'Completed' THEN 1 ELSE 0 END) as successful_generations
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
            STRING_AGG(DISTINCT dc.component_type, ', ') as component_types
        FROM dashboard_definitions dd
        LEFT JOIN dashboard_components dc ON dd.dashboard_id = dc.dashboard_id
        GROUP BY dd.dashboard_id, dd.dashboard_name
        ORDER BY dd.dashboard_name
    """)

    dashboard_summary = cursor.fetchall()

    return {
        "report_usage": report_usage,
        "dashboard_summary": dashboard_summary
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
