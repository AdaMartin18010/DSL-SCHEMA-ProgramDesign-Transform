# 数据可视化Schema转换体系

## 📑 目录

- [数据可视化Schema转换体系](#数据可视化schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 可视化到Vega-Lite转换](#2-可视化到vega-lite转换)
  - [3. 可视化到D3.js转换](#3-可视化到d3js转换)
  - [4. 可视化到JSON Schema转换](#4-可视化到json-schema转换)
  - [5. 可视化数据存储与分析](#5-可视化数据存储与分析)
    - [5.1 PostgreSQL可视化数据存储](#51-postgresql可视化数据存储)
    - [5.2 可视化数据分析查询](#52-可视化数据分析查询)

---

## 1. 转换体系概述

数据可视化Schema转换体系支持可视化到Vega-Lite、D3.js、JSON Schema格式转换，以及可视化数据存储。

### 1.1 转换目标

1. **可视化到Vega-Lite转换**：可视化Schema到Vega-Lite格式
2. **可视化到D3.js转换**：可视化Schema到D3.js格式
3. **可视化到JSON Schema转换**：可视化Schema到JSON Schema格式
4. **可视化到数据库转换**：可视化数据到PostgreSQL存储

---

## 2. 可视化到Vega-Lite转换

**转换规则**：

- 图表类型 → Vega-Lite Mark
- 数据映射 → Vega-Lite Encoding
- 图表配置 → Vega-Lite Config

**转换示例**：

```python
def convert_visualization_to_vega_lite(viz_data: DataVisualizationSchema) -> VegaLiteSpec:
    """将数据可视化Schema转换为Vega-Lite格式"""
    chart = viz_data.charts[0]

    vega_lite_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "url": chart.chart_data.data_source
        },
        "mark": map_chart_type_to_vega_mark(chart.chart_type),
        "encoding": {}
    }

    # 转换X轴
    vega_lite_spec["encoding"]["x"] = {
        "field": chart.chart_data.data_mapping.x_field,
        "type": map_axis_type_to_vega_type(chart.chart_config.x_axis.type),
        "title": chart.chart_config.x_axis.title
    }

    # 转换Y轴
    vega_lite_spec["encoding"]["y"] = {
        "field": chart.chart_data.data_mapping.y_field,
        "type": map_axis_type_to_vega_type(chart.chart_config.y_axis.type),
        "title": chart.chart_config.y_axis.title
    }

    # 转换颜色
    if chart.chart_data.data_mapping.color_field:
        vega_lite_spec["encoding"]["color"] = {
            "field": chart.chart_data.data_mapping.color_field,
            "type": "nominal",
            "scale": {
                "scheme": chart.chart_config.color_scheme
            }
        }

    # 转换数据聚合
    if chart.chart_data.data_aggregation:
        vega_lite_spec["encoding"]["y"]["aggregate"] = map_aggregation_to_vega(
            chart.chart_data.data_aggregation.aggregation_type
        )

    # 转换配置
    vega_lite_spec["config"] = {
        "title": {
            "text": chart.chart_config.title,
            "subtitle": chart.chart_config.subtitle
        },
        "legend": {
            "orient": chart.chart_config.legend.orientation.lower(),
            "title": None
        }
    }

    return vega_lite_spec
```

---

## 3. 可视化到D3.js转换

**转换规则**：

- 图表类型 → D3.js Chart Function
- 数据映射 → D3.js Data Binding
- 图表配置 → D3.js Config

**转换示例**：

```python
def convert_visualization_to_d3(viz_data: DataVisualizationSchema) -> str:
    """将数据可视化Schema转换为D3.js代码"""
    chart = viz_data.charts[0]

    d3_code = f"""
    // D3.js可视化代码
    const margin = {{top: 20, right: 20, bottom: 40, left: 40}};
    const width = {chart.chart_config.width} - margin.left - margin.right;
    const height = {chart.chart_config.height} - margin.top - margin.bottom;

    // 创建SVG
    const svg = d3.select("body")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);

    const g = svg.append("g")
        .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

    // 加载数据
    d3.csv("{chart.chart_data.data_source}").then(data => {{
        // 数据转换
        data.forEach(d => {{
            d.{chart.chart_data.data_mapping.x_field} = +d.{chart.chart_data.data_mapping.x_field};
            d.{chart.chart_data.data_mapping.y_field} = +d.{chart.chart_data.data_mapping.y_field};
        }});

        // 创建比例尺
        const xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.{chart.chart_data.data_mapping.x_field}))
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.{chart.chart_data.data_mapping.y_field}))
            .range([height, 0]);

        // 创建图表
        {generate_d3_chart_code(chart.chart_type, chart.chart_config, chart.chart_data)}

        // 创建坐标轴
        g.append("g")
            .attr("transform", `translate(0,${{height}})`)
            .call(d3.axisBottom(xScale))
            .append("text")
            .attr("x", width / 2)
            .attr("y", 35)
            .attr("fill", "black")
            .text("{chart.chart_config.x_axis.title}");

        g.append("g")
            .call(d3.axisLeft(yScale))
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", -35)
            .attr("x", -height / 2)
            .attr("fill", "black")
            .text("{chart.chart_config.y_axis.title}");
    }});
    """

    return d3_code
```

---

## 4. 可视化到JSON Schema转换

**转换规则**：

- 图表定义 → JSON Schema Object
- 图表配置 → JSON Schema Properties
- 图表数据 → JSON Schema Data

**转换示例**：

```python
def convert_visualization_to_json_schema(viz_data: DataVisualizationSchema) -> JSONSchema:
    """将数据可视化Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # 转换图表
    for chart in viz_data.charts:
        chart_schema = {
            "type": "object",
            "properties": {
                "chart_id": {"type": "string"},
                "chart_name": {"type": "string"},
                "chart_type": {
                    "type": "string",
                    "enum": ["Bar", "Line", "Pie", "Scatter", "Heatmap"]
                },
                "chart_config": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "width": {"type": "integer"},
                        "height": {"type": "integer"}
                    }
                },
                "chart_data": {
                    "type": "object",
                    "properties": {
                        "data_source": {"type": "string"},
                        "data_mapping": {
                            "type": "object",
                            "properties": {
                                "x_field": {"type": "string"},
                                "y_field": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "required": ["chart_id", "chart_name", "chart_type", "chart_data"]
        }

        json_schema["properties"][chart.chart_name] = chart_schema

    return json_schema
```

---

## 5. 可视化数据存储与分析

### 5.1 PostgreSQL可视化数据存储

**表结构设计**：

```sql
-- 图表元数据表
CREATE TABLE chart_metadata (
    chart_id VARCHAR(50) PRIMARY KEY,
    chart_name VARCHAR(200) NOT NULL,
    chart_type VARCHAR(20) NOT NULL,
    data_source VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 仪表板元数据表
CREATE TABLE dashboard_metadata (
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
    chart_id VARCHAR(50),
    position_row INT NOT NULL,
    position_column INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    FOREIGN KEY (dashboard_id) REFERENCES dashboard_metadata(dashboard_id),
    FOREIGN KEY (chart_id) REFERENCES chart_metadata(chart_id)
);

-- 报表元数据表
CREATE TABLE report_metadata (
    report_id VARCHAR(50) PRIMARY KEY,
    report_name VARCHAR(200) NOT NULL,
    report_template_id VARCHAR(50) NOT NULL,
    report_format VARCHAR(20) NOT NULL,
    data_source VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_dashboard_components_dashboard ON dashboard_components(dashboard_id);
CREATE INDEX idx_dashboard_components_chart ON dashboard_components(chart_id);
```

### 5.2 可视化数据分析查询

**查询示例**：

```python
def analyze_visualization_data(conn):
    """分析可视化数据"""
    cursor = conn.cursor()

    # 查询图表汇总
    cursor.execute("""
        SELECT
            chart_type,
            COUNT(*) as chart_count
        FROM chart_metadata
        GROUP BY chart_type
        ORDER BY chart_count DESC
    """)

    chart_summary = cursor.fetchall()

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
        "chart_summary": chart_summary,
        "dashboard_summary": dashboard_summary
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
