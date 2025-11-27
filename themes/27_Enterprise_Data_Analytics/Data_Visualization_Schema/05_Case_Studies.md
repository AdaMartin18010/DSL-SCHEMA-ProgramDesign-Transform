# 数据可视化Schema实践案例

## 📑 目录

- [数据可视化Schema实践案例](#数据可视化schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：销售仪表板设计](#2-案例1销售仪表板设计)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：可视化到Vega-Lite转换](#3-案例2可视化到vega-lite转换)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
  - [4. 案例3：交互式可视化系统](#4-案例3交互式可视化系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：报表生成系统](#5-案例4报表生成系统)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：数据可视化数据存储与分析系统](#6-案例5数据可视化数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供数据可视化Schema在实际应用中的实践案例。

---

## 2. 案例1：销售仪表板设计

### 2.1 场景描述

**应用场景**：
设计销售分析仪表板，包含多个图表组件，支持数据筛选和钻取。

**业务需求**：

- 支持多图表展示
- 支持数据筛选
- 支持数据钻取

### 2.2 Schema定义

**销售仪表板Schema**：

```dsl
schema SalesDashboard {
  dashboard: Dashboard {
    dashboard_id: String @value("DASH-SALES-001")
    dashboard_name: String @value("销售分析仪表板")
    dashboard_layout: DashboardLayout {
      layout_type: Enum @value("Grid")
      grid_config: GridConfig {
        rows: Int @value(4)
        columns: Int @value(4)
      }
      components: List<DashboardComponent> {
        sales_chart: DashboardComponent {
          component_id: String @value("COMP-SALES-CHART")
          component_type: Enum @value("Chart")
          chart_id: String @value("CHART-SALES-001")
          position: Position {
            row: Int @value(0)
            column: Int @value(0)
            width: Int @value(2)
            height: Int @value(2)
          }
        }
        region_filter: DashboardComponent {
          component_id: String @value("COMP-REGION-FILTER")
          component_type: Enum @value("Filter")
          position: Position {
            row: Int @value(0)
            column: Int @value(2)
            width: Int @value(1)
            height: Int @value(1)
          }
        }
      }
    }
    dashboard_interactions: List<DashboardInteraction> {
      filter_interaction: DashboardInteraction {
        interaction_id: String @value("INT-FILTER-001")
        interaction_type: Enum @value("Filter")
        source_component_id: String @value("COMP-REGION-FILTER")
        target_component_ids: List<String> {
          "COMP-SALES-CHART"
        }
      }
    }
  }
}
```

---

## 3. 案例2：可视化到Vega-Lite转换

### 3.1 场景描述

**应用场景**：
将数据可视化Schema转换为Vega-Lite格式，用于Web可视化。

**业务需求**：

- 支持自动转换到Vega-Lite
- 支持图表配置转换
- 支持交互定义转换

### 3.2 实现代码

```python
def convert_chart_to_vega_lite(chart: Chart) -> dict:
    """将图表转换为Vega-Lite格式"""
    vega_lite_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "url": chart.chart_data.data_source
        },
        "mark": map_chart_type_to_vega_mark(chart.chart_type),
        "encoding": {}
    }

    # X轴编码
    vega_lite_spec["encoding"]["x"] = {
        "field": chart.chart_data.data_mapping.x_field,
        "type": map_axis_type_to_vega_type(chart.chart_config.x_axis.type),
        "title": chart.chart_config.x_axis.title or chart.chart_data.data_mapping.x_field
    }

    # Y轴编码
    vega_lite_spec["encoding"]["y"] = {
        "field": chart.chart_data.data_mapping.y_field,
        "type": map_axis_type_to_vega_type(chart.chart_config.y_axis.type),
        "title": chart.chart_config.y_axis.title or chart.chart_data.data_mapping.y_field
    }

    # 颜色编码
    if chart.chart_data.data_mapping.color_field:
        vega_lite_spec["encoding"]["color"] = {
            "field": chart.chart_data.data_mapping.color_field,
            "type": "nominal",
            "scale": {
                "scheme": chart.chart_config.color_scheme
            }
        }

    # 数据聚合
    if chart.chart_data.data_aggregation:
        vega_lite_spec["encoding"]["y"]["aggregate"] = map_aggregation_to_vega(
            chart.chart_data.data_aggregation.aggregation_type
        )
        if chart.chart_data.data_aggregation.group_by:
            vega_lite_spec["encoding"]["x"]["field"] = chart.chart_data.data_aggregation.group_by[0]

    # 配置
    vega_lite_spec["config"] = {
        "title": {
            "text": chart.chart_config.title,
            "subtitle": chart.chart_config.subtitle
        },
        "legend": {
            "orient": chart.chart_config.legend.orientation.lower()
        }
    }

    # 工具提示
    if chart.chart_config.tooltip:
        vega_lite_spec["tooltip"] = True

    return vega_lite_spec
```

---

## 4. 案例3：交互式可视化系统

### 4.1 场景描述

**应用场景**：
构建交互式可视化系统，支持数据筛选、钻取、联动等交互功能。

**业务需求**：

- 支持数据筛选交互
- 支持数据钻取交互
- 支持图表联动交互

### 4.2 实现代码

```python
def create_interactive_visualization(viz_data: DataVisualizationSchema) -> InteractiveVisualization:
    """创建交互式可视化"""
    interactive_viz = InteractiveVisualization()

    # 创建筛选交互
    filter_interaction = Interaction()
    filter_interaction.interaction_id = "INT-FILTER-001"
    filter_interaction.interaction_name = "Region Filter"
    filter_interaction.interaction_type = "Select"
    filter_interaction.source_element = "COMP-REGION-FILTER"
    filter_interaction.interaction_response = InteractionResponse(
        response_type="Filter",
        target_elements=["COMP-SALES-CHART", "COMP-PRODUCT-CHART"],
        response_action="filter_data",
        response_data={"filter_field": "region"}
    )
    interactive_viz.interactions.append(filter_interaction)

    # 创建钻取交互
    drill_down_interaction = Interaction()
    drill_down_interaction.interaction_id = "INT-DRILL-001"
    drill_down_interaction.interaction_name = "Drill Down"
    drill_down_interaction.interaction_type = "Click"
    drill_down_interaction.source_element = "COMP-SALES-CHART"
    drill_down_interaction.interaction_response = InteractionResponse(
        response_type="Navigate",
        target_elements=["DASH-SALES-DETAIL"],
        response_action="navigate_to_detail",
        response_data={"drill_level": "detail"}
    )
    interactive_viz.interactions.append(drill_down_interaction)

    # 创建联动交互
    link_interaction = Interaction()
    link_interaction.interaction_id = "INT-LINK-001"
    link_interaction.interaction_name = "Chart Link"
    link_interaction.interaction_type = "Brush"
    link_interaction.source_element = "COMP-SALES-CHART"
    link_interaction.interaction_response = InteractionResponse(
        response_type="Highlight",
        target_elements=["COMP-PRODUCT-CHART"],
        response_action="highlight_data",
        response_data={"link_field": "product_id"}
    )
    interactive_viz.interactions.append(link_interaction)

    return interactive_viz

def handle_interaction_event(interaction_id: str, event_data: dict, viz_data: DataVisualizationSchema):
    """处理交互事件"""
    interaction = find_interaction(viz_data, interaction_id)

    if interaction:
        # 执行交互响应
        if interaction.interaction_response.response_type == "Filter":
            # 应用数据筛选
            filter_value = event_data.get("value")
            for target_element in interaction.interaction_response.target_elements:
                apply_filter(target_element, interaction.interaction_response.response_data["filter_field"], filter_value)

        elif interaction.interaction_response.response_type == "Navigate":
            # 导航到目标页面
            navigate_to(interaction.interaction_response.target_elements[0], event_data)

        elif interaction.interaction_response.response_type == "Highlight":
            # 高亮目标元素
            highlight_data(interaction.interaction_response.target_elements[0], event_data)
```

---

## 5. 案例4：报表生成系统

### 5.1 场景描述

**应用场景**：
基于报表模板和数据源生成报表，支持多种格式导出。

**业务需求**：

- 支持报表模板定义
- 支持报表数据查询
- 支持多格式导出

### 5.2 实现代码

```python
def generate_report(report_id: str, viz_data: DataVisualizationSchema, parameters: dict) -> Report:
    """生成报表"""
    report_template = find_report_template(viz_data, report_id)

    # 查询数据
    data = query_report_data(
        report_template.report_data.data_source,
        report_template.report_data.data_query,
        parameters
    )

    # 应用筛选
    if report_template.report_data.data_filters:
        for filter_item in report_template.report_data.data_filters:
            data = apply_filter(data, filter_item)

    # 生成报表
    report = Report()
    report.report_id = f"REPORT-{report_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    report.report_name = report_template.template_name
    report.report_format = report_template.report_format

    # 填充报表内容
    report_content = []
    for section in report_template.template_layout.sections:
        if section.section_type == "Chart":
            # 生成图表
            chart = find_chart(viz_data, section.section_content)
            chart_data = filter_chart_data(data, chart.chart_data.data_mapping)
            chart_image = render_chart(chart, chart_data)
            report_content.append({
                "section_id": section.section_id,
                "content": chart_image,
                "position": section.section_position
            })
        elif section.section_type == "Table":
            # 生成表格
            table_data = format_table_data(data, section.section_content)
            report_content.append({
                "section_id": section.section_id,
                "content": table_data,
                "position": section.section_position
            })
        elif section.section_type == "Text":
            # 填充文本
            text_content = format_text(section.section_content, data, parameters)
            report_content.append({
                "section_id": section.section_id,
                "content": text_content,
                "position": section.section_position
            })

    report.report_content = report_content

    # 导出报表
    if report_template.report_format == "PDF":
        export_to_pdf(report)
    elif report_template.report_format == "Excel":
        export_to_excel(report)
    elif report_template.report_format == "HTML":
        export_to_html(report)

    return report
```

---

## 6. 案例5：数据可视化数据存储与分析系统

### 6.1 场景描述

**应用场景**：
数据可视化数据存储与分析系统，支持元数据存储、查询、分析。

**业务需求**：

- 支持可视化元数据存储
- 支持元数据查询和分析
- 支持使用情况分析

### 6.2 实现代码

```python
def store_visualization_data(viz_data: DataVisualizationSchema, conn):
    """存储数据可视化数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储图表元数据
    for chart in viz_data.charts:
        cursor.execute("""
            INSERT INTO chart_metadata
            (chart_id, chart_name, chart_type, data_source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (chart_id) DO UPDATE SET
            chart_name = EXCLUDED.chart_name,
            chart_type = EXCLUDED.chart_type,
            data_source = EXCLUDED.data_source,
            updated_at = CURRENT_TIMESTAMP
        """, (chart.chart_id, chart.chart_name, chart.chart_type, chart.chart_data.data_source))

    # 存储仪表板元数据
    for dashboard in viz_data.dashboards:
        cursor.execute("""
            INSERT INTO dashboard_metadata
            (dashboard_id, dashboard_name, layout_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (dashboard_id) DO UPDATE SET
            dashboard_name = EXCLUDED.dashboard_name,
            layout_type = EXCLUDED.layout_type,
            updated_at = CURRENT_TIMESTAMP
        """, (dashboard.dashboard_id, dashboard.dashboard_name, dashboard.dashboard_layout.layout_type))

        # 存储仪表板组件
        for component in dashboard.dashboard_layout.components:
            cursor.execute("""
                INSERT INTO dashboard_components
                (component_id, dashboard_id, component_type, chart_id,
                 position_row, position_column, width, height)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (component_id) DO UPDATE SET
                component_type = EXCLUDED.component_type,
                chart_id = EXCLUDED.chart_id,
                position_row = EXCLUDED.position_row,
                position_column = EXCLUDED.position_column,
                width = EXCLUDED.width,
                height = EXCLUDED.height
            """, (component.component_id, dashboard.dashboard_id,
                  component.component_type, component.chart_id,
                  component.position.row, component.position.column,
                  component.position.width, component.position.height))

    # 存储报表元数据
    for report in viz_data.reports:
        cursor.execute("""
            INSERT INTO report_metadata
            (report_id, report_name, report_template_id, report_format, data_source)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (report_id) DO UPDATE SET
            report_name = EXCLUDED.report_name,
            report_format = EXCLUDED.report_format,
            data_source = EXCLUDED.data_source,
            updated_at = CURRENT_TIMESTAMP
        """, (report.report_id, report.report_name,
              report.report_template.template_id, report.report_format,
              report.report_data.data_source))

    conn.commit()

def generate_visualization_report(conn):
    """生成数据可视化报表"""
    cursor = conn.cursor()

    # 查询图表使用情况
    cursor.execute("""
        SELECT
            cm.chart_type,
            COUNT(DISTINCT cm.chart_id) as chart_count,
            COUNT(DISTINCT dc.dashboard_id) as dashboard_count
        FROM chart_metadata cm
        LEFT JOIN dashboard_components dc ON cm.chart_id = dc.chart_id
        GROUP BY cm.chart_type
        ORDER BY chart_count DESC
    """)

    chart_usage = cursor.fetchall()

    # 查询仪表板汇总
    cursor.execute("""
        SELECT
            dm.dashboard_name,
            COUNT(dc.component_id) as component_count,
            COUNT(DISTINCT dc.chart_id) as chart_count
        FROM dashboard_metadata dm
        LEFT JOIN dashboard_components dc ON dm.dashboard_id = dc.dashboard_id
        GROUP BY dm.dashboard_id, dm.dashboard_name
        ORDER BY dm.dashboard_name
    """)

    dashboard_summary = cursor.fetchall()

    return {
        "chart_usage": chart_usage,
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
