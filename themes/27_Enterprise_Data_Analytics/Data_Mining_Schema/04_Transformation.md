# 数据挖掘Schema转换体系

## 📑 目录

- [数据挖掘Schema转换体系](#数据挖掘schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 数据挖掘到PMML转换](#2-数据挖掘到pmml转换)
  - [3. 数据挖掘到MLflow转换](#3-数据挖掘到mlflow转换)
  - [4. 数据挖掘到ONNX转换](#4-数据挖掘到onnx转换)
  - [5. 数据挖掘数据存储与分析](#5-数据挖掘数据存储与分析)
    - [5.1 PostgreSQL数据挖掘数据存储](#51-postgresql数据挖掘数据存储)
    - [5.2 数据挖掘数据分析查询](#52-数据挖掘数据分析查询)

---

## 1. 转换体系概述

数据挖掘Schema转换体系支持数据挖掘到PMML、MLflow、ONNX格式转换，以及数据挖掘数据存储。

### 1.1 转换目标

1. **数据挖掘到PMML转换**：数据挖掘模型到PMML格式
2. **数据挖掘到MLflow转换**：数据挖掘模型到MLflow格式
3. **数据挖掘到ONNX转换**：数据挖掘模型到ONNX格式
4. **数据挖掘到数据库转换**：数据挖掘数据到PostgreSQL存储

---

## 2. 数据挖掘到PMML转换

**转换规则**：

- 模型定义 → PMML Model Element
- 模型参数 → PMML Parameters
- 模型结构 → PMML Structure

**转换示例**：

```python
def convert_mining_to_pmml(mining_data: DataMiningSchema) -> PMMLModel:
    """将数据挖掘模型转换为PMML格式"""
    pmml_model = PMMLModel()

    model = mining_data.model_training.models[0]

    # 模型头部
    pmml_model.header = PMMLHeader(
        copyright="Data Mining Model",
        description=model.model_name,
        application_name="Data Mining System",
        application_version="1.0"
    )

    # 数据字典
    data_dictionary = PMMLDataDictionary()
    for feature in mining_data.data_preparation.feature_engineering.features:
        if feature.is_selected:
            data_field = PMMLDataField(
                name=feature.feature_name,
                optype=map_feature_type_to_pmml_optype(feature.feature_type),
                data_type=map_feature_type_to_pmml_data_type(feature.feature_type)
            )
            data_dictionary.data_fields.append(data_field)

    pmml_model.data_dictionary = data_dictionary

    # 模型定义
    if model.model_type == "Classification":
        pmml_model.model = PMMLClassificationModel(
            model_name=model.model_name,
            function_name="classification",
            algorithm_name=model.algorithm
        )
    elif model.model_type == "Regression":
        pmml_model.model = PMMLRegressionModel(
            model_name=model.model_name,
            function_name="regression",
            algorithm_name=model.algorithm
        )

    # 模型参数
    pmml_model.model.mining_schema = PMMLMiningSchema()
    for feature in mining_data.data_preparation.feature_engineering.features:
        if feature.is_selected:
            mining_field = PMMLMiningField(
                name=feature.feature_name,
                usage_type="active"
            )
            pmml_model.model.mining_schema.mining_fields.append(mining_field)

    return pmml_model
```

---

## 3. 数据挖掘到MLflow转换

**转换规则**：

- 模型定义 → MLflow Model
- 训练参数 → MLflow Parameters
- 评估指标 → MLflow Metrics

**转换示例**：

```python
def convert_mining_to_mlflow(mining_data: DataMiningSchema) -> MLflowExperiment:
    """将数据挖掘模型转换为MLflow格式"""
    import mlflow

    model = mining_data.model_training.models[0]
    evaluation = mining_data.model_evaluation.evaluation_results[0]

    # 创建MLflow实验
    experiment = mlflow.create_experiment(model.model_name)

    with mlflow.start_run(experiment_id=experiment):
        # 记录参数
        mlflow.log_params({
            "learning_rate": model.training_parameters.learning_rate,
            "max_iterations": model.training_parameters.max_iterations,
            "batch_size": model.training_parameters.batch_size,
            "regularization": model.training_parameters.regularization
        })

        # 记录指标
        for metric in evaluation.metrics:
            mlflow.log_metric(metric.metric_name, metric.metric_value)

        # 记录模型
        mlflow.sklearn.log_model(
            model.model_structure,
            "model",
            registered_model_name=model.model_name
        )

        # 记录特征重要性
        if evaluation.feature_importance:
            feature_importance_dict = {
                fi.feature_name: fi.importance_score
                for fi in evaluation.feature_importance
            }
            mlflow.log_dict(feature_importance_dict, "feature_importance.json")

    return experiment
```

---

## 4. 数据挖掘到ONNX转换

**转换规则**：

- 模型结构 → ONNX Graph
- 模型参数 → ONNX Initializers
- 模型输入输出 → ONNX Inputs/Outputs

**转换示例**：

```python
def convert_mining_to_onnx(mining_data: DataMiningSchema) -> ONNXModel:
    """将数据挖掘模型转换为ONNX格式"""
    import onnx
    from onnx import helper, TensorProto

    model = mining_data.model_training.models[0]

    # 创建ONNX图
    graph_inputs = []
    for feature in mining_data.data_preparation.feature_engineering.features:
        if feature.is_selected:
            input_tensor = helper.make_tensor_value_info(
                feature.feature_name,
                TensorProto.FLOAT,
                [None, 1]
            )
            graph_inputs.append(input_tensor)

    graph_outputs = [
        helper.make_tensor_value_info(
            model.model_structure.output_target,
            TensorProto.FLOAT,
            [None, 1]
        )
    ]

    # 创建ONNX节点（根据算法类型）
    graph_nodes = []
    if model.algorithm == "Neural_Network":
        # 神经网络节点
        for i, layer_size in enumerate(model.model_structure.hidden_layers):
            node = helper.make_node(
                "MatMul",
                inputs=[f"input_{i}", f"weight_{i}"],
                outputs=[f"output_{i}"]
            )
            graph_nodes.append(node)

    # 创建ONNX模型
    onnx_model = helper.make_model(
        helper.make_graph(
            graph_nodes,
            model.model_name,
            graph_inputs,
            graph_outputs
        )
    )

    return onnx_model
```

---

## 5. 数据挖掘数据存储与分析

### 5.1 PostgreSQL数据挖掘数据存储

**表结构设计**：

```sql
-- 模型元数据表
CREATE TABLE model_metadata (
    model_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(200) NOT NULL,
    model_type VARCHAR(20) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    training_status VARCHAR(20) DEFAULT 'Not_Started',
    training_start_time TIMESTAMP,
    training_end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 特征元数据表
CREATE TABLE feature_metadata (
    feature_id VARCHAR(50) PRIMARY KEY,
    feature_name VARCHAR(200) NOT NULL,
    feature_type VARCHAR(20) NOT NULL,
    feature_source VARCHAR(200) NOT NULL,
    is_selected BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 训练参数表
CREATE TABLE training_parameters (
    parameter_id VARCHAR(50) PRIMARY KEY,
    model_id VARCHAR(50) NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_value VARCHAR(200) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model_metadata(model_id)
);

-- 评估指标表
CREATE TABLE evaluation_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    model_id VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(20) NOT NULL,
    metric_value DECIMAL(18, 4) NOT NULL,
    dataset_type VARCHAR(20) NOT NULL,
    evaluation_date DATE NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model_metadata(model_id)
);

-- 模型部署表
CREATE TABLE model_deployments (
    deployment_id VARCHAR(50) PRIMARY KEY,
    model_id VARCHAR(50) NOT NULL,
    deployment_environment VARCHAR(20) NOT NULL,
    deployment_date DATE NOT NULL,
    deployment_status VARCHAR(20) DEFAULT 'Deployed',
    deployment_endpoint VARCHAR(500) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model_metadata(model_id)
);

-- 创建索引
CREATE INDEX idx_training_parameters_model ON training_parameters(model_id);
CREATE INDEX idx_evaluation_metrics_model ON evaluation_metrics(model_id);
CREATE INDEX idx_evaluation_metrics_date ON evaluation_metrics(evaluation_date);
CREATE INDEX idx_model_deployments_model ON model_deployments(model_id);
CREATE INDEX idx_model_deployments_status ON model_deployments(deployment_status);
```

### 5.2 数据挖掘数据分析查询

**查询示例**：

```python
def analyze_mining_data(conn):
    """分析数据挖掘数据"""
    cursor = conn.cursor()

    # 查询模型性能汇总
    cursor.execute("""
        SELECT
            mm.model_name,
            mm.model_type,
            mm.algorithm,
            AVG(em.metric_value) as avg_metric_value,
            MAX(em.metric_value) as max_metric_value,
            MIN(em.metric_value) as min_metric_value
        FROM model_metadata mm
        JOIN evaluation_metrics em ON mm.model_id = em.model_id
        WHERE em.dataset_type = 'Testing'
        AND em.metric_type = 'Accuracy'
        GROUP BY mm.model_id, mm.model_name, mm.model_type, mm.algorithm
        ORDER BY avg_metric_value DESC
    """)

    model_performance = cursor.fetchall()

    # 查询模型部署汇总
    cursor.execute("""
        SELECT
            mm.model_name,
            md.deployment_environment,
            md.deployment_status,
            md.deployment_date
        FROM model_metadata mm
        JOIN model_deployments md ON mm.model_id = md.model_id
        WHERE md.deployment_status = 'Active'
        ORDER BY md.deployment_date DESC
    """)

    deployment_summary = cursor.fetchall()

    return {
        "model_performance": model_performance,
        "deployment_summary": deployment_summary
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
