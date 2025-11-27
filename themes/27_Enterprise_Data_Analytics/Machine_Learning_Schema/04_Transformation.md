# 机器学习Schema转换体系

## 📑 目录

- [机器学习Schema转换体系](#机器学习schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 机器学习到MLflow转换](#2-机器学习到mlflow转换)
  - [3. 机器学习到Kubeflow转换](#3-机器学习到kubeflow转换)
  - [4. 机器学习到ONNX转换](#4-机器学习到onnx转换)
  - [5. 机器学习数据存储与分析](#5-机器学习数据存储与分析)
    - [5.1 PostgreSQL机器学习数据存储](#51-postgresql机器学习数据存储)
    - [5.2 机器学习数据分析查询](#52-机器学习数据分析查询)

---

## 1. 转换体系概述

机器学习Schema转换体系支持机器学习到MLflow、Kubeflow、ONNX格式转换，以及机器学习数据存储。

### 1.1 转换目标

1. **机器学习到MLflow转换**：机器学习实验到MLflow格式
2. **机器学习到Kubeflow转换**：机器学习管道到Kubeflow格式
3. **机器学习到ONNX转换**：机器学习模型到ONNX格式
4. **机器学习到数据库转换**：机器学习数据到PostgreSQL存储

---

## 2. 机器学习到MLflow转换

**转换规则**：

- 实验 → MLflow Experiment
- 运行 → MLflow Run
- 模型 → MLflow Model

**转换示例**：

```python
def convert_ml_to_mlflow(ml_data: MachineLearningSchema) -> MLflowExperiment:
    """将机器学习Schema转换为MLflow格式"""
    import mlflow

    experiment = ml_data.experiment_management.experiments[0]

    # 创建MLflow实验
    mlflow_experiment = mlflow.create_experiment(experiment.experiment_name)

    # 转换运行
    for run in ml_data.experiment_management.runs:
        with mlflow.start_run(experiment_id=mlflow_experiment, run_name=run.run_name):
            # 记录参数
            mlflow.log_params(run.parameters)

            # 记录指标
            mlflow.log_metrics(run.metrics)

            # 记录工件
            for artifact in run.artifacts:
                if artifact.artifact_type == "Model":
                    mlflow.sklearn.log_model(
                        artifact.artifact_path,
                        "model"
                    )
                else:
                    mlflow.log_artifact(artifact.artifact_path)

            # 记录标签
            if run.tags:
                mlflow.set_tags(run.tags)

    return mlflow_experiment
```

---

## 3. 机器学习到Kubeflow转换

**转换规则**：

- 训练定义 → Kubeflow Pipeline Component
- 训练流程 → Kubeflow Pipeline
- 模型部署 → Kubeflow Serving

**转换示例**：

```python
def convert_ml_to_kubeflow(ml_data: MachineLearningSchema) -> KubeflowPipeline:
    """将机器学习Schema转换为Kubeflow Pipeline格式"""
    from kfp import dsl

    @dsl.pipeline(
        name=ml_data.experiment_management.experiments[0].experiment_name,
        description="Machine Learning Pipeline"
    )
    def ml_pipeline():
        # 数据准备组件
        data_prep = dsl.ContainerOp(
            name="data-preparation",
            image="data-prep:latest",
            command=["python", "prepare_data.py"],
            arguments=[
                "--input-path", ml_data.model_training.training_definitions[0].data_config.training_data_path,
                "--output-path", "/data/processed"
            ]
        )

        # 模型训练组件
        train = dsl.ContainerOp(
            name="model-training",
            image="train:latest",
            command=["python", "train_model.py"],
            arguments=[
                "--data-path", data_prep.outputs["output-path"],
                "--model-type", ml_data.model_training.training_definitions[0].model_architecture.model_type,
                "--epochs", str(ml_data.model_training.training_definitions[0].training_config.epochs)
            ]
        )
        train.after(data_prep)

        # 模型评估组件
        evaluate = dsl.ContainerOp(
            name="model-evaluation",
            image="evaluate:latest",
            command=["python", "evaluate_model.py"],
            arguments=[
                "--model-path", train.outputs["model-path"],
                "--test-data-path", ml_data.model_training.training_definitions[0].data_config.test_data_path
            ]
        )
        evaluate.after(train)

    return ml_pipeline
```

---

## 4. 机器学习到ONNX转换

**转换规则**：

- 模型架构 → ONNX Graph
- 模型参数 → ONNX Initializers
- 模型输入输出 → ONNX Inputs/Outputs

**转换示例**：

```python
def convert_ml_to_onnx(ml_data: MachineLearningSchema) -> ONNXModel:
    """将机器学习模型转换为ONNX格式"""
    import onnx
    from onnx import helper, TensorProto

    model_arch = ml_data.model_training.training_definitions[0].model_architecture

    # 创建ONNX图输入
    graph_inputs = [
        helper.make_tensor_value_info(
            "input",
            TensorProto.FLOAT,
            model_arch.input_shape
        )
    ]

    # 创建ONNX图输出
    graph_outputs = [
        helper.make_tensor_value_info(
            "output",
            TensorProto.FLOAT,
            model_arch.output_shape
        )
    ]

    # 创建ONNX节点
    graph_nodes = []
    if model_arch.model_type == "Neural_Network":
        # 神经网络层
        for i, layer_size in enumerate(model_arch.hidden_layers):
            node = helper.make_node(
                "MatMul",
                inputs=[f"input_{i}", f"weight_{i}"],
                outputs=[f"output_{i}"]
            )
            graph_nodes.append(node)

            # 激活函数
            if model_arch.activation_functions and i < len(model_arch.activation_functions):
                activation_node = helper.make_node(
                    model_arch.activation_functions[i],
                    inputs=[f"output_{i}"],
                    outputs=[f"activated_{i}"]
                )
                graph_nodes.append(activation_node)

    # 创建ONNX模型
    onnx_model = helper.make_model(
        helper.make_graph(
            graph_nodes,
            ml_data.model_training.training_definitions[0].definition_name,
            graph_inputs,
            graph_outputs
        )
    )

    return onnx_model
```

---

## 5. 机器学习数据存储与分析

### 5.1 PostgreSQL机器学习数据存储

**表结构设计**：

```sql
-- 实验元数据表
CREATE TABLE experiment_metadata (
    experiment_id VARCHAR(50) PRIMARY KEY,
    experiment_name VARCHAR(200) NOT NULL,
    experiment_description TEXT,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 运行元数据表
CREATE TABLE run_metadata (
    run_id VARCHAR(50) PRIMARY KEY,
    experiment_id VARCHAR(50) NOT NULL,
    run_name VARCHAR(200) NOT NULL,
    run_status VARCHAR(20) DEFAULT 'Running',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration INTEGER,
    parent_run_id VARCHAR(50),
    FOREIGN KEY (experiment_id) REFERENCES experiment_metadata(experiment_id)
);

-- 运行参数表
CREATE TABLE run_parameters (
    parameter_id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_value VARCHAR(500) NOT NULL,
    FOREIGN KEY (run_id) REFERENCES run_metadata(run_id)
);

-- 运行指标表
CREATE TABLE run_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(18, 4) NOT NULL,
    metric_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (run_id) REFERENCES run_metadata(run_id)
);

-- 模型注册表
CREATE TABLE model_registry (
    model_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(200) NOT NULL,
    model_description TEXT,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模型版本表
CREATE TABLE model_versions (
    version_id VARCHAR(50) PRIMARY KEY,
    model_id VARCHAR(50) NOT NULL,
    version_number INT NOT NULL,
    version_stage VARCHAR(20) DEFAULT 'None',
    run_id VARCHAR(50) NOT NULL,
    model_uri VARCHAR(500) NOT NULL,
    model_format VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model_registry(model_id),
    FOREIGN KEY (run_id) REFERENCES run_metadata(run_id)
);

-- 模型部署表
CREATE TABLE model_deployments (
    deployment_id VARCHAR(50) PRIMARY KEY,
    model_id VARCHAR(50) NOT NULL,
    version_id VARCHAR(50) NOT NULL,
    deployment_name VARCHAR(200) NOT NULL,
    deployment_environment VARCHAR(20) NOT NULL,
    deployment_status VARCHAR(20) DEFAULT 'Deploying',
    deployment_date TIMESTAMP NOT NULL,
    deployment_endpoint VARCHAR(500) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model_registry(model_id),
    FOREIGN KEY (version_id) REFERENCES model_versions(version_id)
);

-- 创建索引
CREATE INDEX idx_run_metadata_experiment ON run_metadata(experiment_id);
CREATE INDEX idx_run_metadata_status ON run_metadata(run_status);
CREATE INDEX idx_run_parameters_run ON run_parameters(run_id);
CREATE INDEX idx_run_metrics_run ON run_metrics(run_id);
CREATE INDEX idx_model_versions_model ON model_versions(model_id);
CREATE INDEX idx_model_versions_stage ON model_versions(version_stage);
CREATE INDEX idx_model_deployments_model ON model_deployments(model_id);
CREATE INDEX idx_model_deployments_status ON model_deployments(deployment_status);
```

### 5.2 机器学习数据分析查询

**查询示例**：

```python
def analyze_ml_data(conn):
    """分析机器学习数据"""
    cursor = conn.cursor()

    # 查询实验汇总
    cursor.execute("""
        SELECT
            em.experiment_name,
            COUNT(rm.run_id) as run_count,
            SUM(CASE WHEN rm.run_status = 'Finished' THEN 1 ELSE 0 END) as completed_runs,
            SUM(CASE WHEN rm.run_status = 'Failed' THEN 1 ELSE 0 END) as failed_runs
        FROM experiment_metadata em
        LEFT JOIN run_metadata rm ON em.experiment_id = rm.experiment_id
        GROUP BY em.experiment_id, em.experiment_name
        ORDER BY em.experiment_name
    """)

    experiment_summary = cursor.fetchall()

    # 查询模型性能汇总
    cursor.execute("""
        SELECT
            mr.model_name,
            mv.version_number,
            mv.version_stage,
            AVG(rm_metrics.metric_value) as avg_metric_value
        FROM model_registry mr
        JOIN model_versions mv ON mr.model_id = mv.model_id
        JOIN run_metadata rm ON mv.run_id = rm.run_id
        JOIN run_metrics rm_metrics ON rm.run_id = rm_metrics.run_id
        WHERE rm_metrics.metric_name = 'accuracy'
        GROUP BY mr.model_id, mr.model_name, mv.version_id, mv.version_number, mv.version_stage
        ORDER BY mr.model_name, mv.version_number
    """)

    model_performance = cursor.fetchall()

    # 查询模型部署汇总
    cursor.execute("""
        SELECT
            mr.model_name,
            mv.version_number,
            md.deployment_environment,
            md.deployment_status,
            md.deployment_date
        FROM model_registry mr
        JOIN model_versions mv ON mr.model_id = mv.model_id
        JOIN model_deployments md ON mv.version_id = md.version_id
        WHERE md.deployment_status = 'Active'
        ORDER BY md.deployment_date DESC
    """)

    deployment_summary = cursor.fetchall()

    return {
        "experiment_summary": experiment_summary,
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
