# 机器学习Schema实践案例

## 📑 目录

- [机器学习Schema实践案例](#机器学习schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：MLflow实验管理](#2-案例1mlflow实验管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：模型训练与注册](#3-案例2模型训练与注册)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
  - [4. 案例3：模型服务与监控](#4-案例3模型服务与监控)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：机器学习到MLflow转换](#5-案例4机器学习到mlflow转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：机器学习数据存储与分析系统](#6-案例5机器学习数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供机器学习Schema在实际应用中的实践案例。

---

## 2. 案例1：MLflow实验管理

### 2.1 场景描述

**应用场景**：
使用MLflow管理机器学习实验，跟踪实验参数、指标、结果。

**业务需求**：

- 支持实验创建和管理
- 支持运行跟踪和比较
- 支持实验重现

### 2.2 Schema定义

**MLflow实验管理Schema**：

```dsl
schema MLflowExperimentManagement {
  experiment: Experiment {
    experiment_id: String @value("EXP-20250001")
    experiment_name: String @value("CustomerChurnPrediction")
    experiment_description: String @value("客户流失预测实验")
    experiment_tags: List<String> {
      "classification"
      "customer_analytics"
    }
  }

  run: Run {
    run_id: String @value("RUN-20250001")
    experiment_id: String @value("EXP-20250001")
    run_name: String @value("RandomForest_v1")
    run_status: Enum @value("Finished")
    parameters: Map<String, String> {
      "n_estimators": String @value("100")
      "max_depth": String @value("10")
      "learning_rate": String @value("0.01")
    }
    metrics: Map<String, Decimal> {
      "accuracy": Decimal @value(0.85)
      "precision": Decimal @value(0.82)
      "recall": Decimal @value(0.88)
    }
  }
}
```

---

## 3. 案例2：模型训练与注册

### 3.1 场景描述

**应用场景**：
训练机器学习模型并注册到模型注册表。

**业务需求**：

- 支持模型训练
- 支持模型注册
- 支持模型版本管理

### 3.2 实现代码

```python
def train_and_register_model(ml_data: MachineLearningSchema) -> ModelVersion:
    """训练并注册模型"""
    import mlflow

    training_def = ml_data.model_training.training_definitions[0]

    # 创建实验
    experiment = mlflow.create_experiment(training_def.definition_name)

    with mlflow.start_run(experiment_id=experiment):
        # 训练模型
        model = train_model(training_def)

        # 记录参数
        mlflow.log_params({
            "optimizer": training_def.training_config.optimizer,
            "learning_rate": training_def.training_config.learning_rate,
            "batch_size": training_def.training_config.batch_size,
            "epochs": training_def.training_config.epochs
        })

        # 评估模型
        evaluation_metrics = evaluate_model(model, training_def.data_config.test_data_path)

        # 记录指标
        mlflow.log_metrics(evaluation_metrics)

        # 注册模型
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=training_def.definition_name
        )

        # 获取模型版本
        model_version = mlflow.get_model_version(
            name=training_def.definition_name,
            version=1
        )

        return model_version
```

---

## 4. 案例3：模型服务与监控

### 4.1 场景描述

**应用场景**：
部署模型到生产环境并提供API服务，监控模型性能。

**业务需求**：

- 支持模型部署
- 支持API服务
- 支持性能监控

### 4.2 实现代码

```python
def deploy_and_monitor_model(model_version: ModelVersion) -> ModelDeployment:
    """部署并监控模型"""
    import mlflow

    # 部署模型
    deployment = ModelDeployment()
    deployment.deployment_id = f"DEPLOY-{model_version.version_id}"
    deployment.model_id = model_version.model_id
    deployment.version_id = model_version.version_id
    deployment.deployment_name = f"{model_version.model_name}_v{model_version.version_number}"
    deployment.deployment_environment = "Production"
    deployment.deployment_status = "Deploying"
    deployment.deployment_date = datetime.now()

    # 使用MLflow部署模型
    mlflow.deployments.create_deployment(
        name=deployment.deployment_name,
        model_uri=f"models:/{model_version.model_name}/{model_version.version_number}",
        target="production"
    )

    deployment.deployment_status = "Active"
    deployment.deployment_endpoint = f"https://api.example.com/models/{deployment.deployment_id}/predict"

    # 创建API
    api = ModelAPI()
    api.api_id = f"API-{deployment.deployment_id}"
    api.deployment_id = deployment.deployment_id
    api.api_endpoint = deployment.deployment_endpoint
    api.api_version = "v1"
    api.request_schema = {
        "type": "object",
        "properties": {
            "features": {
                "type": "array",
                "items": {"type": "number"}
            }
        }
    }
    api.response_schema = {
        "type": "object",
        "properties": {
            "prediction": {"type": "number"},
            "probability": {"type": "number"}
        }
    }

    deployment.model_apis = [api]

    # 创建监控
    monitoring = ModelMonitoring()
    monitoring.monitoring_id = f"MON-{deployment.deployment_id}"
    monitoring.deployment_id = deployment.deployment_id

    # 监控指标
    monitoring.monitoring_metrics = [
        MonitoringMetric(
            metric_name="prediction_count",
            metric_type="Prediction_Count",
            metric_value=0,
            metric_timestamp=datetime.now()
        ),
        MonitoringMetric(
            metric_name="average_latency",
            metric_type="Latency",
            metric_value=0,
            metric_timestamp=datetime.now()
        )
    ]

    deployment.model_monitoring = [monitoring]

    return deployment

def monitor_model_performance(deployment_id: str, conn):
    """监控模型性能"""
    cursor = conn.cursor()

    # 查询预测统计
    cursor.execute("""
        SELECT
            COUNT(*) as prediction_count,
            AVG(latency_ms) as avg_latency,
            SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as error_rate
        FROM model_predictions
        WHERE deployment_id = %s
        AND prediction_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
    """, (deployment_id,))

    performance_stats = cursor.fetchone()

    # 更新监控指标
    cursor.execute("""
        INSERT INTO model_monitoring_metrics
        (monitoring_id, metric_name, metric_type, metric_value, metric_timestamp)
        VALUES
        (%s, 'prediction_count', 'Prediction_Count', %s, CURRENT_TIMESTAMP),
        (%s, 'average_latency', 'Latency', %s, CURRENT_TIMESTAMP),
        (%s, 'error_rate', 'Error_Rate', %s, CURRENT_TIMESTAMP)
    """, (
        deployment_id, performance_stats[0],
        deployment_id, performance_stats[1],
        deployment_id, performance_stats[2]
    ))

    conn.commit()
```

---

## 5. 案例4：机器学习到MLflow转换

### 5.1 场景描述

**应用场景**：
将机器学习Schema转换为MLflow格式，用于实验管理。

**业务需求**：

- 支持自动转换到MLflow
- 支持实验和运行跟踪
- 支持模型注册

### 5.2 实现代码

```python
def convert_ml_to_mlflow_complete(ml_data: MachineLearningSchema) -> MLflowExperiment:
    """完整转换机器学习Schema到MLflow"""
    import mlflow

    experiment = ml_data.experiment_management.experiments[0]

    # 创建MLflow实验
    mlflow_experiment = mlflow.create_experiment(experiment.experiment_name)

    # 转换运行
    for run in ml_data.experiment_management.runs:
        with mlflow.start_run(
            experiment_id=mlflow_experiment,
            run_name=run.run_name,
            nested=run.parent_run_id is not None
        ):
            # 记录参数
            if run.parameters:
                mlflow.log_params(run.parameters)

            # 记录指标
            if run.metrics:
                mlflow.log_metrics(run.metrics)

            # 记录标签
            if run.tags:
                mlflow.set_tags(run.tags)

            # 记录工件
            for artifact in run.artifacts:
                if artifact.artifact_type == "Model":
                    mlflow.sklearn.log_model(
                        artifact.artifact_path,
                        "model",
                        registered_model_name=experiment.experiment_name
                    )
                else:
                    mlflow.log_artifact(artifact.artifact_path)

    return mlflow_experiment
```

---

## 6. 案例5：机器学习数据存储与分析系统

### 6.1 场景描述

**应用场景**：
机器学习数据存储与分析系统，支持元数据存储、查询、分析。

**业务需求**：

- 支持机器学习元数据存储
- 支持元数据查询和分析
- 支持实验和模型性能分析

### 6.2 实现代码

```python
def store_ml_data(ml_data: MachineLearningSchema, conn):
    """存储机器学习数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储实验元数据
    for experiment in ml_data.experiment_management.experiments:
        cursor.execute("""
            INSERT INTO experiment_metadata
            (experiment_id, experiment_name, experiment_description, created_by)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (experiment_id) DO UPDATE SET
            experiment_name = EXCLUDED.experiment_name,
            experiment_description = EXCLUDED.experiment_description,
            updated_at = CURRENT_TIMESTAMP
        """, (experiment.experiment_id, experiment.experiment_name,
              experiment.experiment_description, experiment.created_by))

    # 存储运行元数据
    for run in ml_data.experiment_management.runs:
        cursor.execute("""
            INSERT INTO run_metadata
            (run_id, experiment_id, run_name, run_status, start_time, end_time, duration, parent_run_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE SET
            run_status = EXCLUDED.run_status,
            end_time = EXCLUDED.end_time,
            duration = EXCLUDED.duration
        """, (run.run_id, run.experiment_id, run.run_name, run.run_status,
              run.start_time, run.end_time, run.duration, run.parent_run_id))

        # 存储运行参数
        for param_name, param_value in run.parameters.items():
            cursor.execute("""
                INSERT INTO run_parameters
                (parameter_id, run_id, parameter_name, parameter_value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (parameter_id) DO UPDATE SET
                parameter_value = EXCLUDED.parameter_value
            """, (f"PARAM-{run.run_id}-{param_name}", run.run_id, param_name, param_value))

        # 存储运行指标
        for metric_name, metric_value in run.metrics.items():
            cursor.execute("""
                INSERT INTO run_metrics
                (metric_id, run_id, metric_name, metric_value, metric_timestamp)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO UPDATE SET
                metric_value = EXCLUDED.metric_value,
                metric_timestamp = EXCLUDED.metric_timestamp
            """, (f"METRIC-{run.run_id}-{metric_name}", run.run_id,
                  metric_name, metric_value, datetime.now()))

    # 存储模型注册
    for model in ml_data.model_registry.registered_models:
        cursor.execute("""
            INSERT INTO model_registry
            (model_id, model_name, model_description, created_by)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (model_id) DO UPDATE SET
            model_name = EXCLUDED.model_name,
            model_description = EXCLUDED.model_description,
            updated_at = CURRENT_TIMESTAMP
        """, (model.model_id, model.model_name, model.model_description, model.created_by))

        # 存储模型版本
        for version in ml_data.model_registry.model_versions:
            if version.model_id == model.model_id:
                cursor.execute("""
                    INSERT INTO model_versions
                    (version_id, model_id, version_number, version_stage, run_id, model_uri, model_format, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (version_id) DO UPDATE SET
                    version_stage = EXCLUDED.version_stage,
                    model_uri = EXCLUDED.model_uri
                """, (version.version_id, version.model_id, version.version_number,
                      version.version_stage, version.run_id, version.model_uri,
                      version.model_format, version.created_by))

    # 存储模型部署
    for deployment in ml_data.model_serving.model_deployments:
        cursor.execute("""
            INSERT INTO model_deployments
            (deployment_id, model_id, version_id, deployment_name, deployment_environment,
             deployment_status, deployment_date, deployment_endpoint)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (deployment_id) DO UPDATE SET
            deployment_status = EXCLUDED.deployment_status,
            deployment_endpoint = EXCLUDED.deployment_endpoint
        """, (deployment.deployment_id, deployment.model_id, deployment.version_id,
              deployment.deployment_name, deployment.deployment_environment,
              deployment.deployment_status, deployment.deployment_date,
              deployment.deployment_endpoint))

    conn.commit()

def generate_ml_report(conn):
    """生成机器学习报表"""
    cursor = conn.cursor()

    # 查询实验汇总
    cursor.execute("""
        SELECT
            em.experiment_name,
            COUNT(rm.run_id) as run_count,
            SUM(CASE WHEN rm.run_status = 'Finished' THEN 1 ELSE 0 END) as completed_runs
        FROM experiment_metadata em
        LEFT JOIN run_metadata rm ON em.experiment_id = rm.experiment_id
        GROUP BY em.experiment_id, em.experiment_name
        ORDER BY em.experiment_name
    """)

    experiment_report = cursor.fetchall()

    # 查询模型部署报表
    cursor.execute("""
        SELECT
            mr.model_name,
            mv.version_number,
            md.deployment_environment,
            md.deployment_status
        FROM model_registry mr
        JOIN model_versions mv ON mr.model_id = mv.model_id
        JOIN model_deployments md ON mv.version_id = md.version_id
        ORDER BY md.deployment_date DESC
    """)

    deployment_report = cursor.fetchall()

    return {
        "experiment_report": experiment_report,
        "deployment_report": deployment_report
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
