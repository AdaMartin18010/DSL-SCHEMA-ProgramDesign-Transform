# 绩效评估Schema转换体系

## 📑 目录

- [绩效评估Schema转换体系](#绩效评估schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 绩效评估到JSON Schema转换](#2-绩效评估到json-schema转换)
  - [3. 绩效评估到OpenAPI转换](#3-绩效评估到openapi转换)
  - [4. 绩效评估到OLAP Cube转换](#4-绩效评估到olap-cube转换)
  - [5. 绩效评估数据存储与分析](#5-绩效评估数据存储与分析)
    - [5.1 PostgreSQL绩效评估数据存储](#51-postgresql绩效评估数据存储)
    - [5.2 绩效评估数据分析查询](#52-绩效评估数据分析查询)

---

## 1. 转换体系概述

绩效评估Schema转换体系支持绩效评估到JSON Schema、OpenAPI、OLAP Cube格式转换，以及绩效评估数据存储。

### 1.1 转换目标

1. **绩效评估到JSON Schema转换**：绩效评估Schema到JSON Schema格式
2. **绩效评估到OpenAPI转换**：绩效评估Schema到OpenAPI格式
3. **绩效评估到OLAP Cube转换**：绩效评估Schema到OLAP Cube格式
4. **绩效评估到数据库转换**：绩效评估数据到PostgreSQL存储

---

## 2. 绩效评估到JSON Schema转换

**转换规则**：

- 评估结果 → JSON Schema Object
- 评估分数 → JSON Schema Property
- 评估反馈 → JSON Schema Array

**转换示例**：

```python
def convert_performance_evaluation_to_json_schema(eval_data: PerformanceEvaluationSchema) -> JSONSchema:
    """将绩效评估Schema转换为JSON Schema格式"""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "evaluation_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "result_id": {"type": "string"},
                        "cycle_id": {"type": "string"},
                        "object_id": {"type": "string"},
                        "evaluator_id": {"type": "string"},
                        "evaluator_type": {
                            "type": "string",
                            "enum": ["Self", "Manager", "Peer", "Subordinate", "Customer", "System"]
                        },
                        "total_score": {"type": "number", "minimum": 0, "maximum": 100},
                        "weighted_score": {"type": "number", "minimum": 0, "maximum": 100},
                        "evaluation_level": {
                            "type": "string",
                            "enum": ["Excellent", "Good", "Average", "Poor"]
                        },
                        "evaluation_date": {"type": "string", "format": "date"}
                    },
                    "required": ["result_id", "object_id", "total_score"]
                }
            },
            "criteria_scores": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "score_id": {"type": "string"},
                        "result_id": {"type": "string"},
                        "criteria_id": {"type": "string"},
                        "score_value": {"type": "number", "minimum": 0, "maximum": 100},
                        "score_comment": {"type": "string"}
                    },
                    "required": ["score_id", "result_id", "criteria_id", "score_value"]
                }
            },
            "evaluation_feedbacks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "feedback_id": {"type": "string"},
                        "result_id": {"type": "string"},
                        "feedback_type": {"type": "string"},
                        "feedback_content": {"type": "string"},
                        "feedback_date": {"type": "string", "format": "date"}
                    },
                    "required": ["feedback_id", "result_id", "feedback_content"]
                }
            }
        }
    }

    return json_schema
```

---

## 3. 绩效评估到OpenAPI转换

**转换规则**：

- 评估结果 → OpenAPI Schema
- 评估查询 → OpenAPI Endpoint
- 评估提交 → OpenAPI Operation

**转换示例**：

```python
def convert_performance_evaluation_to_openapi(eval_data: PerformanceEvaluationSchema) -> OpenAPISpec:
    """将绩效评估Schema转换为OpenAPI格式"""
    spec = OpenAPISpec()
    spec.info.title = "Performance Evaluation API"
    spec.info.version = "1.0.0"

    # 定义评估结果Schema
    evaluation_result_schema = Schema()
    evaluation_result_schema.type = "object"
    evaluation_result_schema.properties = {
        "result_id": {"type": "string"},
        "cycle_id": {"type": "string"},
        "object_id": {"type": "string"},
        "evaluator_id": {"type": "string"},
        "evaluator_type": {
            "type": "string",
            "enum": ["Self", "Manager", "Peer", "Subordinate", "Customer", "System"]
        },
        "total_score": {"type": "number", "minimum": 0, "maximum": 100},
        "weighted_score": {"type": "number", "minimum": 0, "maximum": 100},
        "evaluation_level": {
            "type": "string",
            "enum": ["Excellent", "Good", "Average", "Poor"]
        }
    }
    spec.components.schemas["EvaluationResult"] = evaluation_result_schema

    # 定义获取评估结果端点
    get_evaluation_results = Operation()
    get_evaluation_results.summary = "Get Evaluation Results"
    get_evaluation_results.operation_id = "getEvaluationResults"
    get_evaluation_results.parameters = [
        Parameter(name="cycle_id", in_="query", schema={"type": "string"}),
        Parameter(name="object_id", in_="query", schema={"type": "string"}),
        Parameter(name="evaluator_type", in_="query", schema={"type": "string"})
    ]
    get_evaluation_results.responses = {
        "200": Response(
            description="Evaluation Results",
            content={"application/json": MediaType(schema={
                "type": "array",
                "items": {"$ref": "#/components/schemas/EvaluationResult"}
            })}
        )
    }

    path = PathItem()
    path.get = get_evaluation_results
    spec.paths["/api/v1/evaluation/results"] = path

    # 定义提交评估结果端点
    submit_evaluation_result = Operation()
    submit_evaluation_result.summary = "Submit Evaluation Result"
    submit_evaluation_result.operation_id = "submitEvaluationResult"
    submit_evaluation_result.request_body = RequestBody(
        content={"application/json": MediaType(schema={"$ref": "#/components/schemas/EvaluationResult"})}
    )
    submit_evaluation_result.responses = {
        "201": Response(description="Evaluation Result Created"),
        "400": Response(description="Bad Request")
    }

    path = PathItem()
    path.post = submit_evaluation_result
    spec.paths["/api/v1/evaluation/results"] = path

    return spec
```

---

## 4. 绩效评估到OLAP Cube转换

**转换规则**：

- 评估对象 → OLAP维度
- 评估分数 → OLAP度量
- 评估周期 → OLAP时间维度

**转换示例**：

```python
def convert_performance_evaluation_to_olap_cube(eval_data: PerformanceEvaluationSchema) -> OLAPCube:
    """将绩效评估Schema转换为OLAP Cube格式"""
    cube = OLAPCube()
    cube.name = "Performance_Evaluation_Cube"

    # 创建时间维度
    time_dimension = Dimension()
    time_dimension.name = "Time"
    time_dimension.hierarchies = [{
        "name": "Calendar",
        "levels": ["Year", "Quarter", "Month"]
    }]
    cube.dimensions.append(time_dimension)

    # 创建评估对象维度
    object_dimension = Dimension()
    object_dimension.name = "Evaluation_Object"
    object_dimension.attributes = ["Object_Type", "Department", "Position", "Level"]
    cube.dimensions.append(object_dimension)

    # 创建评估者维度
    evaluator_dimension = Dimension()
    evaluator_dimension.name = "Evaluator"
    evaluator_dimension.attributes = ["Evaluator_Type", "Department", "Position"]
    cube.dimensions.append(evaluator_dimension)

    # 创建评估周期维度
    cycle_dimension = Dimension()
    cycle_dimension.name = "Evaluation_Cycle"
    cycle_dimension.attributes = ["Cycle_Type", "Cycle_Name"]
    cube.dimensions.append(cycle_dimension)

    # 创建度量
    total_score_measure = Measure()
    total_score_measure.name = "Total_Score"
    total_score_measure.aggregation_function = "AVG"
    total_score_measure.data_type = "Decimal"
    cube.measures.append(total_score_measure)

    weighted_score_measure = Measure()
    weighted_score_measure.name = "Weighted_Score"
    weighted_score_measure.aggregation_function = "AVG"
    weighted_score_measure.data_type = "Decimal"
    cube.measures.append(weighted_score_measure)

    evaluation_count_measure = Measure()
    evaluation_count_measure.name = "Evaluation_Count"
    evaluation_count_measure.aggregation_function = "COUNT"
    evaluation_count_measure.data_type = "Integer"
    cube.measures.append(evaluation_count_measure)

    # 转换评估结果为事实数据
    for result in eval_data.evaluation_result.evaluation_results:
        cycle = find_cycle(eval_data, result.cycle_id)
        obj = find_object(eval_data, result.object_id)

        fact = Fact()
        fact.dimensions = {
            "Time": {
                "Year": cycle.cycle_start_date.year,
                "Quarter": get_quarter(cycle.cycle_start_date),
                "Month": cycle.cycle_start_date.month
            },
            "Evaluation_Object": {
                "Object_Type": obj.object_type,
                "Department": obj.department_id,
                "Position": obj.position,
                "Level": obj.object_level
            },
            "Evaluator": {
                "Evaluator_Type": result.evaluator_type,
                "Department": find_evaluator_department(eval_data, result.evaluator_id),
                "Position": find_evaluator_position(eval_data, result.evaluator_id)
            },
            "Evaluation_Cycle": {
                "Cycle_Type": cycle.cycle_type,
                "Cycle_Name": cycle.cycle_name
            }
        }
        fact.measures = {
            "Total_Score": result.total_score,
            "Weighted_Score": result.weighted_score,
            "Evaluation_Count": 1
        }
        cube.facts.append(fact)

    return cube
```

---

## 5. 绩效评估数据存储与分析

### 5.1 PostgreSQL绩效评估数据存储

**表结构设计**：

```sql
-- 评估周期表
CREATE TABLE evaluation_cycles (
    cycle_id VARCHAR(50) PRIMARY KEY,
    cycle_name VARCHAR(200) NOT NULL,
    cycle_type VARCHAR(20) NOT NULL,
    cycle_start_date DATE NOT NULL,
    cycle_end_date DATE NOT NULL,
    evaluation_start_date DATE NOT NULL,
    evaluation_end_date DATE NOT NULL,
    evaluation_deadline DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评估对象表
CREATE TABLE evaluation_objects (
    object_id VARCHAR(50) PRIMARY KEY,
    object_name VARCHAR(200) NOT NULL,
    object_type VARCHAR(20) NOT NULL,
    object_level VARCHAR(20) NOT NULL,
    parent_object_id VARCHAR(50),
    manager_id VARCHAR(50),
    department_id VARCHAR(50),
    position VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_object_id) REFERENCES evaluation_objects(object_id)
);

-- 评估标准表
CREATE TABLE evaluation_criteria (
    criteria_id VARCHAR(50) PRIMARY KEY,
    object_type VARCHAR(20) NOT NULL,
    criteria_name VARCHAR(200) NOT NULL,
    criteria_description TEXT,
    criteria_weight DECIMAL(5, 2) DEFAULT 100,
    criteria_type VARCHAR(20) NOT NULL,
    evaluation_method VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评估结果表
CREATE TABLE evaluation_results (
    result_id VARCHAR(50) PRIMARY KEY,
    cycle_id VARCHAR(50) NOT NULL,
    object_id VARCHAR(50) NOT NULL,
    evaluator_id VARCHAR(50) NOT NULL,
    evaluator_type VARCHAR(20) NOT NULL,
    evaluation_date DATE NOT NULL,
    total_score DECIMAL(5, 2) NOT NULL,
    weighted_score DECIMAL(5, 2) NOT NULL,
    evaluation_level VARCHAR(20),
    evaluation_status VARCHAR(20) DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cycle_id) REFERENCES evaluation_cycles(cycle_id),
    FOREIGN KEY (object_id) REFERENCES evaluation_objects(object_id)
);

-- 标准分数表
CREATE TABLE criteria_scores (
    score_id VARCHAR(50) PRIMARY KEY,
    result_id VARCHAR(50) NOT NULL,
    criteria_id VARCHAR(50) NOT NULL,
    score_value DECIMAL(5, 2) NOT NULL,
    score_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES evaluation_results(result_id),
    FOREIGN KEY (criteria_id) REFERENCES evaluation_criteria(criteria_id)
);

-- 评估反馈表
CREATE TABLE evaluation_feedbacks (
    feedback_id VARCHAR(50) PRIMARY KEY,
    result_id VARCHAR(50) NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,
    feedback_content TEXT NOT NULL,
    feedback_date DATE NOT NULL,
    feedback_provider VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES evaluation_results(result_id)
);

-- 改进建议表
CREATE TABLE improvement_recommendations (
    recommendation_id VARCHAR(50) PRIMARY KEY,
    result_id VARCHAR(50) NOT NULL,
    recommendation_content TEXT NOT NULL,
    recommendation_priority VARCHAR(20) DEFAULT 'Medium',
    recommendation_category VARCHAR(20) NOT NULL,
    recommendation_owner VARCHAR(200) NOT NULL,
    target_completion_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES evaluation_results(result_id)
);

-- 创建索引
CREATE INDEX idx_evaluation_results_cycle ON evaluation_results(cycle_id);
CREATE INDEX idx_evaluation_results_object ON evaluation_results(object_id);
CREATE INDEX idx_evaluation_results_evaluator ON evaluation_results(evaluator_id);
CREATE INDEX idx_evaluation_results_status ON evaluation_results(evaluation_status);
CREATE INDEX idx_criteria_scores_result ON criteria_scores(result_id);
CREATE INDEX idx_evaluation_feedbacks_result ON evaluation_feedbacks(result_id);
```

### 5.2 绩效评估数据分析查询

**查询示例**：

```python
def analyze_performance_evaluation_data(conn):
    """分析绩效评估数据"""
    cursor = conn.cursor()

    # 查询评估结果汇总
    cursor.execute("""
        SELECT
            eo.object_type,
            er.evaluator_type,
            COUNT(*) as evaluation_count,
            AVG(er.total_score) as avg_total_score,
            AVG(er.weighted_score) as avg_weighted_score,
            COUNT(CASE WHEN er.evaluation_level = 'Excellent' THEN 1 END) as excellent_count,
            COUNT(CASE WHEN er.evaluation_level = 'Good' THEN 1 END) as good_count,
            COUNT(CASE WHEN er.evaluation_level = 'Average' THEN 1 END) as average_count,
            COUNT(CASE WHEN er.evaluation_level = 'Poor' THEN 1 END) as poor_count
        FROM evaluation_results er
        JOIN evaluation_objects eo ON er.object_id = eo.object_id
        WHERE er.evaluation_status = 'Approved'
        GROUP BY eo.object_type, er.evaluator_type
        ORDER BY eo.object_type, er.evaluator_type
    """)

    evaluation_summary = cursor.fetchall()

    # 查询评估周期完成情况
    cursor.execute("""
        SELECT
            ec.cycle_name,
            ec.cycle_type,
            COUNT(DISTINCT er.object_id) as evaluated_objects,
            COUNT(DISTINCT eo.object_id) as total_objects,
            COUNT(DISTINCT er.object_id) * 100.0 / COUNT(DISTINCT eo.object_id) as completion_rate
        FROM evaluation_cycles ec
        LEFT JOIN evaluation_results er ON ec.cycle_id = er.cycle_id AND er.evaluation_status = 'Approved'
        LEFT JOIN evaluation_objects eo ON eo.is_active = TRUE
        WHERE ec.is_active = TRUE
        GROUP BY ec.cycle_id, ec.cycle_name, ec.cycle_type
        ORDER BY ec.cycle_start_date DESC
    """)

    cycle_completion = cursor.fetchall()

    # 查询评估分数趋势
    cursor.execute("""
        SELECT
            ec.cycle_name,
            eo.object_type,
            AVG(er.total_score) as avg_score,
            AVG(er.weighted_score) as avg_weighted_score
        FROM evaluation_results er
        JOIN evaluation_cycles ec ON er.cycle_id = ec.cycle_id
        JOIN evaluation_objects eo ON er.object_id = eo.object_id
        WHERE er.evaluation_status = 'Approved'
        GROUP BY ec.cycle_id, ec.cycle_name, eo.object_type
        ORDER BY ec.cycle_start_date, eo.object_type
    """)

    score_trends = cursor.fetchall()

    return {
        "evaluation_summary": evaluation_summary,
        "cycle_completion": cycle_completion,
        "score_trends": score_trends
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
