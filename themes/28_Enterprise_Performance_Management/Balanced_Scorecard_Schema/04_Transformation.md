# 平衡计分卡Schema转换体系

## 📑 目录

- [平衡计分卡Schema转换体系](#平衡计分卡schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. BSC到JSON Schema转换](#2-bsc到json-schema转换)
  - [3. BSC到OpenAPI转换](#3-bsc到openapi转换)
  - [4. BSC到战略地图可视化转换](#4-bsc到战略地图可视化转换)
  - [5. BSC数据存储与分析](#5-bsc数据存储与分析)
    - [5.1 PostgreSQL BSC数据存储](#51-postgresql-bsc数据存储)
    - [5.2 BSC数据分析查询](#52-bsc数据分析查询)

---

## 1. 转换体系概述

平衡计分卡Schema转换体系支持BSC到JSON Schema、OpenAPI、战略地图可视化格式转换，以及BSC数据存储。

### 1.1 转换目标

1. **BSC到JSON Schema转换**：BSC Schema到JSON Schema格式
2. **BSC到OpenAPI转换**：BSC Schema到OpenAPI格式
3. **BSC到战略地图可视化转换**：BSC Schema到可视化格式
4. **BSC到数据库转换**：BSC数据到PostgreSQL存储

---

## 2. BSC到JSON Schema转换

**转换规则**：

- 战略目标 → JSON Schema Object
- 指标 → JSON Schema Property
- 行动计划 → JSON Schema Array

**转换示例**：

```python
def convert_bsc_to_json_schema(bsc_data: BalancedScorecardSchema) -> JSONSchema:
    """将平衡计分卡Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "strategic_objectives": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "objective_id": {"type": "string"},
                        "objective_name": {"type": "string"},
                        "objective_dimension": {
                            "type": "string",
                            "enum": ["Financial", "Customer", "Internal_Process", "Learning_Growth"]
                        },
                        "objective_priority": {"type": "string"},
                        "owner": {"type": "string"},
                        "target_date": {"type": "string", "format": "date"}
                    },
                    "required": ["objective_id", "objective_name", "objective_dimension"]
                }
            },
            "metrics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metric_id": {"type": "string"},
                        "metric_name": {"type": "string"},
                        "objective_id": {"type": "string"},
                        "target_value": {"type": "number"},
                        "current_value": {"type": "number"}
                    },
                    "required": ["metric_id", "metric_name", "objective_id"]
                }
            },
            "action_plans": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action_id": {"type": "string"},
                        "action_name": {"type": "string"},
                        "objective_id": {"type": "string"},
                        "execution_status": {"type": "string"},
                        "execution_progress": {"type": "number"}
                    },
                    "required": ["action_id", "action_name", "objective_id"]
                }
            }
        }
    }

    return json_schema
```

---

## 3. BSC到OpenAPI转换

**转换规则**：

- 战略目标 → OpenAPI Schema
- 指标 → OpenAPI Endpoint
- 行动计划 → OpenAPI Operation

**转换示例**：

```python
def convert_bsc_to_openapi(bsc_data: BalancedScorecardSchema) -> OpenAPISpec:
    """将平衡计分卡Schema转换为OpenAPI格式"""
    spec = OpenAPISpec()
    spec.info.title = "Balanced Scorecard API"
    spec.info.version = "1.0.0"

    # 定义战略目标Schema
    objective_schema = Schema()
    objective_schema.type = "object"
    objective_schema.properties = {
        "objective_id": {"type": "string"},
        "objective_name": {"type": "string"},
        "objective_dimension": {
            "type": "string",
            "enum": ["Financial", "Customer", "Internal_Process", "Learning_Growth"]
        },
        "objective_priority": {"type": "string"},
        "owner": {"type": "string"},
        "target_date": {"type": "string", "format": "date"}
    }
    spec.components.schemas["StrategicObjective"] = objective_schema

    # 定义指标Schema
    metric_schema = Schema()
    metric_schema.type = "object"
    metric_schema.properties = {
        "metric_id": {"type": "string"},
        "metric_name": {"type": "string"},
        "objective_id": {"type": "string"},
        "target_value": {"type": "number"},
        "current_value": {"type": "number"},
        "completion_rate": {"type": "number"}
    }
    spec.components.schemas["Metric"] = metric_schema

    # 定义获取战略目标端点
    get_objectives = Operation()
    get_objectives.summary = "Get Strategic Objectives"
    get_objectives.operation_id = "getStrategicObjectives"
    get_objectives.parameters = [
        Parameter(name="dimension", in_="query", schema={"type": "string"}),
        Parameter(name="level", in_="query", schema={"type": "string"})
    ]
    get_objectives.responses = {
        "200": Response(
            description="Strategic Objectives",
            content={"application/json": MediaType(schema={
                "type": "array",
                "items": {"$ref": "#/components/schemas/StrategicObjective"}
            })}
        )
    }

    path = PathItem()
    path.get = get_objectives
    spec.paths["/api/v1/bsc/objectives"] = path

    # 定义获取指标端点
    get_metrics = Operation()
    get_metrics.summary = "Get Metrics"
    get_metrics.operation_id = "getMetrics"
    get_metrics.parameters = [
        Parameter(name="objective_id", in_="query", schema={"type": "string"})
    ]
    get_metrics.responses = {
        "200": Response(
            description="Metrics",
            content={"application/json": MediaType(schema={
                "type": "array",
                "items": {"$ref": "#/components/schemas/Metric"}
            })}
        )
    }

    path = PathItem()
    path.get = get_metrics
    spec.paths["/api/v1/bsc/metrics"] = path

    return spec
```

---

## 4. BSC到战略地图可视化转换

**转换规则**：

- 战略目标 → 地图节点
- 因果关系 → 地图连接
- 价值创造路径 → 地图路径

**转换示例**：

```python
def convert_bsc_to_strategy_map_visualization(bsc_data: BalancedScorecardSchema) -> StrategyMapVisualization:
    """将平衡计分卡Schema转换为战略地图可视化格式"""
    visualization = StrategyMapVisualization()

    # 按维度组织目标
    dimensions = {
        "Learning_Growth": [],
        "Internal_Process": [],
        "Customer": [],
        "Financial": []
    }

    for objective in bsc_data.strategic_objective.strategic_objectives:
        dimensions[objective.objective_dimension].append(objective)

    # 创建地图节点
    nodes = []
    for dimension, objectives in dimensions.items():
        for objective in objectives:
            node = MapNode()
            node.id = objective.objective_id
            node.label = objective.objective_name
            node.dimension = objective.objective_dimension
            node.priority = objective.objective_priority
            node.position = calculate_node_position(objective.objective_dimension, len(dimensions[objective.objective_dimension]))
            nodes.append(node)

    # 创建地图连接
    links = []
    for relationship in bsc_data.strategy_map.causal_relationships:
        link = MapLink()
        link.source = relationship.source_objective_id
        link.target = relationship.target_objective_id
        link.type = relationship.relationship_type
        link.strength = relationship.relationship_strength
        links.append(link)

    visualization.nodes = nodes
    visualization.links = links

    return visualization
```

---

## 5. BSC数据存储与分析

### 5.1 PostgreSQL BSC数据存储

**表结构设计**：

```sql
-- 战略目标表
CREATE TABLE strategic_objectives (
    objective_id VARCHAR(50) PRIMARY KEY,
    objective_name VARCHAR(200) NOT NULL,
    objective_description TEXT,
    objective_dimension VARCHAR(20) NOT NULL,
    objective_category VARCHAR(100),
    objective_priority VARCHAR(20) DEFAULT 'Medium',
    objective_level VARCHAR(20) DEFAULT 'Corporate',
    parent_objective_id VARCHAR(50),
    owner VARCHAR(200) NOT NULL,
    target_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_objective_id) REFERENCES strategic_objectives(objective_id)
);

-- 指标定义表
CREATE TABLE metric_definitions (
    metric_id VARCHAR(50) PRIMARY KEY,
    metric_name VARCHAR(200) NOT NULL,
    metric_description TEXT,
    metric_type VARCHAR(20) NOT NULL,
    objective_id VARCHAR(50) NOT NULL,
    calculation_formula TEXT NOT NULL,
    measurement_unit VARCHAR(50) NOT NULL,
    target_value DECIMAL(18, 2) NOT NULL,
    baseline_value DECIMAL(18, 2),
    owner VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (objective_id) REFERENCES strategic_objectives(objective_id)
);

-- 指标值表
CREATE TABLE metric_values (
    value_id VARCHAR(50) PRIMARY KEY,
    metric_id VARCHAR(50) NOT NULL,
    value DECIMAL(18, 2) NOT NULL,
    measurement_date DATE NOT NULL,
    completion_rate DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (metric_id) REFERENCES metric_definitions(metric_id)
);

-- 行动计划表
CREATE TABLE action_definitions (
    action_id VARCHAR(50) PRIMARY KEY,
    action_name VARCHAR(200) NOT NULL,
    action_description TEXT,
    objective_id VARCHAR(50) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    action_priority VARCHAR(20) DEFAULT 'Medium',
    owner VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (objective_id) REFERENCES strategic_objectives(objective_id)
);

-- 行动计划执行表
CREATE TABLE action_executions (
    execution_id VARCHAR(50) PRIMARY KEY,
    action_id VARCHAR(50) NOT NULL,
    execution_status VARCHAR(20) DEFAULT 'Not_Started',
    execution_progress DECIMAL(5, 2) DEFAULT 0,
    execution_start_date DATE,
    execution_end_date DATE,
    actual_cost DECIMAL(18, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (action_id) REFERENCES action_definitions(action_id)
);

-- 因果关系表
CREATE TABLE causal_relationships (
    relationship_id VARCHAR(50) PRIMARY KEY,
    source_objective_id VARCHAR(50) NOT NULL,
    target_objective_id VARCHAR(50) NOT NULL,
    relationship_type VARCHAR(20) NOT NULL,
    relationship_strength VARCHAR(20) DEFAULT 'Medium',
    relationship_evidence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_objective_id) REFERENCES strategic_objectives(objective_id),
    FOREIGN KEY (target_objective_id) REFERENCES strategic_objectives(objective_id)
);

-- 创建索引
CREATE INDEX idx_metric_definitions_objective ON metric_definitions(objective_id);
CREATE INDEX idx_metric_values_metric ON metric_values(metric_id);
CREATE INDEX idx_metric_values_date ON metric_values(measurement_date);
CREATE INDEX idx_action_definitions_objective ON action_definitions(objective_id);
CREATE INDEX idx_action_executions_action ON action_executions(action_id);
CREATE INDEX idx_causal_relationships_source ON causal_relationships(source_objective_id);
CREATE INDEX idx_causal_relationships_target ON causal_relationships(target_objective_id);
```

### 5.2 BSC数据分析查询

**查询示例**：

```python
def analyze_bsc_data(conn):
    """分析平衡计分卡数据"""
    cursor = conn.cursor()

    # 查询各维度目标完成情况
    cursor.execute("""
        SELECT
            so.objective_dimension,
            COUNT(DISTINCT so.objective_id) as objective_count,
            COUNT(DISTINCT md.metric_id) as metric_count,
            AVG(mv.completion_rate) as avg_completion_rate
        FROM strategic_objectives so
        LEFT JOIN metric_definitions md ON so.objective_id = md.objective_id
        LEFT JOIN metric_values mv ON md.metric_id = mv.metric_id
        WHERE so.is_active = TRUE
        GROUP BY so.objective_dimension
        ORDER BY so.objective_dimension
    """)

    dimension_summary = cursor.fetchall()

    # 查询行动计划执行情况
    cursor.execute("""
        SELECT
            ad.action_type,
            COUNT(*) as action_count,
            SUM(CASE WHEN ae.execution_status = 'Completed' THEN 1 ELSE 0 END) as completed_count,
            AVG(ae.execution_progress) as avg_progress
        FROM action_definitions ad
        LEFT JOIN action_executions ae ON ad.action_id = ae.action_id
        GROUP BY ad.action_type
        ORDER BY action_count DESC
    """)

    action_summary = cursor.fetchall()

    # 查询因果关系网络
    cursor.execute("""
        SELECT
            so1.objective_dimension as source_dimension,
            so2.objective_dimension as target_dimension,
            COUNT(*) as relationship_count
        FROM causal_relationships cr
        JOIN strategic_objectives so1 ON cr.source_objective_id = so1.objective_id
        JOIN strategic_objectives so2 ON cr.target_objective_id = so2.objective_id
        GROUP BY so1.objective_dimension, so2.objective_dimension
        ORDER BY relationship_count DESC
    """)

    relationship_summary = cursor.fetchall()

    return {
        "dimension_summary": dimension_summary,
        "action_summary": action_summary,
        "relationship_summary": relationship_summary
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
