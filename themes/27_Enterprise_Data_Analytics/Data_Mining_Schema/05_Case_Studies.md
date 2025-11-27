# 数据挖掘Schema实践案例

## 📑 目录

- [数据挖掘Schema实践案例](#数据挖掘schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：客户流失预测](#2-案例1客户流失预测)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：CRISP-DM流程实施](#3-案例2crisp-dm流程实施)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
  - [4. 案例3：模型训练与评估](#4-案例3模型训练与评估)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：模型部署与监控](#5-案例4模型部署与监控)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：数据挖掘数据存储与分析系统](#6-案例5数据挖掘数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供数据挖掘Schema在实际应用中的实践案例。

---

## 2. 案例1：客户流失预测

### 2.1 场景描述

**应用场景**：
构建客户流失预测模型，预测客户流失概率。

**业务需求**：

- 支持客户特征分析
- 支持流失预测模型训练
- 支持模型评估和部署

### 2.2 Schema定义

**客户流失预测Schema**：

```dsl
schema CustomerChurnPrediction {
  data_preparation: DataPreparation {
    features: List<Feature> {
      customer_age: Feature {
        feature_name: String @value("customer_age")
        feature_type: Enum @value("Numerical")
        is_selected: Boolean @value(true)
      }
      customer_tenure: Feature {
        feature_name: String @value("customer_tenure")
        feature_type: Enum @value("Numerical")
        is_selected: Boolean @value(true)
      }
      monthly_charges: Feature {
        feature_name: String @value("monthly_charges")
        feature_type: Enum @value("Numerical")
        is_selected: Boolean @value(true)
      }
    }
    data_sampling: DataSampling {
      train_ratio: Decimal @value(0.7)
      test_ratio: Decimal @value(0.15)
      validation_ratio: Decimal @value(0.15)
    }
  }

  model_training: ModelTraining {
    model: Model {
      model_id: String @value("MODEL-CHURN-001")
      model_name: String @value("CustomerChurnPrediction")
      model_type: Enum @value("Classification")
      algorithm: Enum @value("Random_Forest")
      training_parameters: TrainingParameters {
        learning_rate: Decimal @value(0.01)
        max_iterations: Int @value(1000)
        batch_size: Int @value(32)
      }
    }
  }

  model_evaluation: ModelEvaluation {
    evaluation_result: EvaluationResult {
      model_id: String @value("MODEL-CHURN-001")
      metrics: Map<String, Decimal> {
        "Accuracy": Decimal @value(0.85)
        "Precision": Decimal @value(0.82)
        "Recall": Decimal @value(0.88)
        "F1_Score": Decimal @value(0.85)
      }
    }
  }
}
```

---

## 3. 案例2：CRISP-DM流程实施

### 3.1 场景描述

**应用场景**：
按照CRISP-DM标准流程执行数据挖掘项目。

**业务需求**：

- 支持CRISP-DM六个阶段
- 支持阶段间数据流转
- 支持流程追溯

### 3.2 实现代码

```python
def execute_crisp_dm_process(business_objectives: Dict) -> DataMiningSchema:
    """执行CRISP-DM流程"""
    mining_schema = DataMiningSchema()

    # 1. 业务理解
    business_understanding = BusinessUnderstanding()
    business_understanding.business_objectives = business_objectives
    business_understanding.success_criteria = define_success_criteria(business_objectives)
    mining_schema.business_understanding = business_understanding

    # 2. 数据理解
    data_understanding = DataUnderstanding()
    data_understanding.data_sources = collect_data_sources(business_objectives)
    data_understanding.data_quality = assess_data_quality(data_understanding.data_sources)
    mining_schema.data_understanding = data_understanding

    # 3. 数据准备
    data_preparation = DataPreparation()
    data_preparation.data_cleaning = clean_data(data_understanding.data_sources)
    data_preparation.feature_engineering = engineer_features(data_preparation.data_cleaning)
    data_preparation.data_sampling = sample_data(data_preparation.feature_engineering)
    mining_schema.data_preparation = data_preparation

    # 4. 建模
    model_training = ModelTraining()
    model_training.models = train_models(data_preparation.data_sampling)
    mining_schema.model_training = model_training

    # 5. 评估
    model_evaluation = ModelEvaluation()
    model_evaluation.evaluation_results = evaluate_models(model_training.models, data_preparation.data_sampling)
    model_evaluation.model_comparison = compare_models(model_evaluation.evaluation_results)
    mining_schema.model_evaluation = model_evaluation

    # 6. 部署
    best_model = model_evaluation.model_comparison.best_model_id
    model_deployment = ModelDeployment()
    model_deployment.model_deployments = deploy_model(best_model)
    mining_schema.model_deployment = model_deployment

    return mining_schema
```

---

## 4. 案例3：模型训练与评估

### 4.1 场景描述

**应用场景**：
训练多个模型并评估模型性能，选择最佳模型。

**业务需求**：

- 支持多模型训练
- 支持模型性能评估
- 支持模型比较和选择

### 4.2 实现代码

```python
def train_and_evaluate_models(mining_data: DataMiningSchema) -> ModelEvaluation:
    """训练和评估模型"""
    models = []
    evaluation_results = []

    # 训练多个模型
    algorithms = ["Decision_Tree", "Random_Forest", "SVM", "Neural_Network"]

    for algorithm in algorithms:
        model = Model()
        model.model_id = f"MODEL-{algorithm}-001"
        model.model_name = f"{algorithm}Model"
        model.model_type = "Classification"
        model.algorithm = algorithm
        model.training_parameters = TrainingParameters(
            learning_rate=0.01,
            max_iterations=1000,
            batch_size=32
        )

        # 训练模型
        trained_model = train_model(model, mining_data.data_preparation.data_sampling)
        models.append(trained_model)

        # 评估模型
        evaluation_result = evaluate_model(trained_model, mining_data.data_preparation.data_sampling)
        evaluation_results.append(evaluation_result)

    # 模型比较
    model_comparison = ModelComparison()
    model_comparison.comparison_id = "COMP-001"
    model_comparison.comparison_date = datetime.now().date()
    model_comparison.compared_models = [m.model_id for m in models]

    # 比较指标
    comparison_metrics = {}
    for result in evaluation_results:
        comparison_metrics[result.model_id] = {
            metric.metric_name: metric.metric_value
            for metric in result.metrics
        }

    model_comparison.comparison_metrics = comparison_metrics

    # 选择最佳模型（基于F1分数）
    best_model_id = max(
        comparison_metrics.keys(),
        key=lambda mid: comparison_metrics[mid].get("F1_Score", 0)
    )
    model_comparison.best_model_id = best_model_id

    model_evaluation = ModelEvaluation()
    model_evaluation.evaluation_results = evaluation_results
    model_evaluation.model_comparison = model_comparison

    return model_evaluation
```

---

## 5. 案例4：模型部署与监控

### 5.1 场景描述

**应用场景**：
部署模型到生产环境并监控模型性能。

**业务需求**：

- 支持模型部署
- 支持模型性能监控
- 支持模型漂移检测

### 5.2 实现代码

```python
def deploy_and_monitor_model(model_id: str, mining_data: DataMiningSchema) -> ModelDeployment:
    """部署和监控模型"""
    model = find_model(mining_data.model_training, model_id)

    # 部署模型
    deployment = ModelDeployment()
    deployment.deployment_id = f"DEPLOY-{model_id}"
    deployment.model_id = model_id
    deployment.deployment_environment = "Production"
    deployment.deployment_date = datetime.now().date()
    deployment.deployment_status = "Deployed"
    deployment.deployment_endpoint = f"https://api.example.com/models/{model_id}/predict"

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
        ),
        MonitoringMetric(
            metric_name="error_rate",
            metric_type="Error_Rate",
            metric_value=0,
            metric_timestamp=datetime.now()
        )
    ]

    # 漂移检测
    monitoring.drift_detection = DriftDetection(
        drift_score=0.0,
        drift_threshold=0.1,
        is_drifted=False
    )

    deployment.model_monitoring = monitoring

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

    # 检测漂移
    cursor.execute("""
        SELECT
            drift_score,
            drift_threshold
        FROM model_drift_detection
        WHERE deployment_id = %s
        ORDER BY detection_date DESC
        LIMIT 1
    """, (deployment_id,))

    drift_info = cursor.fetchone()
    if drift_info and drift_info[0] > drift_info[1]:
        # 触发漂移告警
        send_drift_alert(deployment_id, drift_info[0])

    conn.commit()
```

---

## 6. 案例5：数据挖掘数据存储与分析系统

### 6.1 场景描述

**应用场景**：
数据挖掘数据存储与分析系统，支持元数据存储、查询、分析。

**业务需求**：

- 支持数据挖掘元数据存储
- 支持元数据查询和分析
- 支持模型性能监控

### 6.2 实现代码

```python
def store_mining_data(mining_data: DataMiningSchema, conn):
    """存储数据挖掘数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储模型元数据
    for model in mining_data.model_training.models:
        cursor.execute("""
            INSERT INTO model_metadata
            (model_id, model_name, model_type, algorithm, training_status,
             training_start_time, training_end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (model_id) DO UPDATE SET
            model_name = EXCLUDED.model_name,
            training_status = EXCLUDED.training_status,
            training_start_time = EXCLUDED.training_start_time,
            training_end_time = EXCLUDED.training_end_time,
            updated_at = CURRENT_TIMESTAMP
        """, (model.model_id, model.model_name, model.model_type,
              model.algorithm, model.training_status,
              model.training_start_time, model.training_end_time))

        # 存储训练参数
        cursor.execute("""
            INSERT INTO training_parameters
            (parameter_id, model_id, parameter_name, parameter_value)
            VALUES
            (%s, %s, 'learning_rate', %s),
            (%s, %s, 'max_iterations', %s),
            (%s, %s, 'batch_size', %s),
            (%s, %s, 'regularization', %s)
            ON CONFLICT (parameter_id) DO UPDATE SET
            parameter_value = EXCLUDED.parameter_value
        """, (
            f"PARAM-{model.model_id}-LR", model.model_id, str(model.training_parameters.learning_rate),
            f"PARAM-{model.model_id}-MAX", model.model_id, str(model.training_parameters.max_iterations),
            f"PARAM-{model.model_id}-BATCH", model.model_id, str(model.training_parameters.batch_size),
            f"PARAM-{model.model_id}-REG", model.model_id, str(model.training_parameters.regularization)
        ))

    # 存储评估指标
    for result in mining_data.model_evaluation.evaluation_results:
        for metric in result.metrics:
            cursor.execute("""
                INSERT INTO evaluation_metrics
                (metric_id, model_id, metric_name, metric_type, metric_value, dataset_type, evaluation_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO UPDATE SET
                metric_value = EXCLUDED.metric_value,
                evaluation_date = EXCLUDED.evaluation_date
            """, (metric.metric_id, result.model_id, metric.metric_name,
                  metric.metric_type, metric.metric_value,
                  result.dataset_type, result.evaluation_date))

    # 存储模型部署
    for deployment in mining_data.model_deployment.model_deployments:
        cursor.execute("""
            INSERT INTO model_deployments
            (deployment_id, model_id, deployment_environment, deployment_date,
             deployment_status, deployment_endpoint)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (deployment_id) DO UPDATE SET
            deployment_status = EXCLUDED.deployment_status,
            deployment_endpoint = EXCLUDED.deployment_endpoint
        """, (deployment.deployment_id, deployment.model_id,
              deployment.deployment_environment, deployment.deployment_date,
              deployment.deployment_status, deployment.deployment_endpoint))

    conn.commit()

def generate_mining_report(conn):
    """生成数据挖掘报表"""
    cursor = conn.cursor()

    # 查询模型性能报表
    cursor.execute("""
        SELECT
            mm.model_name,
            mm.algorithm,
            em.metric_name,
            em.metric_value,
            em.dataset_type
        FROM model_metadata mm
        JOIN evaluation_metrics em ON mm.model_id = em.model_id
        WHERE em.dataset_type = 'Testing'
        ORDER BY mm.model_name, em.metric_name
    """)

    performance_report = cursor.fetchall()

    # 查询模型部署报表
    cursor.execute("""
        SELECT
            mm.model_name,
            md.deployment_environment,
            md.deployment_status,
            md.deployment_date
        FROM model_metadata mm
        JOIN model_deployments md ON mm.model_id = md.model_id
        ORDER BY md.deployment_date DESC
    """)

    deployment_report = cursor.fetchall()

    return {
        "performance_report": performance_report,
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
