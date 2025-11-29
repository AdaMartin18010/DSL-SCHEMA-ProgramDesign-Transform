# 机器学习Schema实践案例

## 📑 目录

- [机器学习Schema实践案例](#机器学习schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业MLflow机器学习实验管理系统](#2-案例1企业mlflow机器学习实验管理系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)
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

本文档提供机器学习Schema在实际企业应用中的实践案例，涵盖MLflow实验管理、模型训练与注册、模型服务与监控等真实场景。

**案例类型**：

1. **企业MLflow机器学习实验管理系统**：实验跟踪和管理
2. **模型训练与注册系统**：模型训练和版本管理
3. **模型服务与监控系统**：模型部署和监控
4. **机器学习到MLflow转换工具**：ML Schema到MLflow转换
5. **机器学习数据存储与分析系统**：ML数据分析和监控

**参考企业案例**：

- **MLflow官方**：MLflow实验管理最佳实践
- **机器学习Ops**：MLOps最佳实践

---

## 2. 案例1：企业MLflow机器学习实验管理系统

### 2.1 业务背景

**企业背景**：
某电商公司需要构建机器学习实验管理系统，使用MLflow跟踪和管理机器学习实验，提高模型开发效率和可重现性。

**业务痛点**：

1. **实验管理混乱**：实验参数、结果难以追踪
2. **实验重现困难**：无法重现历史实验
3. **模型版本管理缺失**：缺乏模型版本管理
4. **实验比较困难**：难以比较不同实验效果

**业务目标**：

- 统一实验管理
- 支持实验重现
- 规范模型版本管理
- 支持实验比较

### 2.2 技术挑战

1. **实验跟踪**：跟踪实验参数、指标、结果
2. **模型注册**：注册和管理模型版本
3. **实验重现**：确保实验可重现
4. **模型服务**：模型部署和服务化

### 2.3 解决方案

**使用Schema定义MLflow实验管理系统**：

### 2.4 完整代码实现

**MLflow实验管理Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
机器学习实验管理Schema实现
"""

from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum

class RunStatus(str, Enum):
    """运行状态"""
    RUNNING = "Running"
    FINISHED = "Finished"
    FAILED = "Failed"
    KILLED = "Killed"

@dataclass
class Experiment:
    """实验"""
    experiment_id: str
    experiment_name: str
    experiment_description: Optional[str] = None
    experiment_tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""

    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.experiment_tags:
            self.experiment_tags.append(tag)

@dataclass
class Run:
    """运行"""
    run_id: str
    experiment_id: str
    run_name: str
    run_status: RunStatus = RunStatus.RUNNING
    parameters: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, Decimal] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def add_parameter(self, key: str, value: str):
        """添加参数"""
        self.parameters[key] = value

    def add_metric(self, key: str, value: Decimal):
        """添加指标"""
        self.metrics[key] = value

    def finish(self, status: RunStatus = RunStatus.FINISHED):
        """完成运行"""
        self.run_status = status
        self.end_time = datetime.now()

@dataclass
class ModelVersion:
    """模型版本"""
    version_id: str
    model_name: str
    run_id: str
    version: int
    stage: str = "None"  # None, Staging, Production, Archived
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""

    def promote_to_staging(self):
        """提升到Staging"""
        self.stage = "Staging"

    def promote_to_production(self):
        """提升到Production"""
        self.stage = "Production"

    def archive(self):
        """归档"""
        self.stage = "Archived"

@dataclass
class MLflowExperimentManagement:
    """MLflow实验管理"""
    experiments: Dict[str, Experiment] = field(default_factory=dict)
    runs: Dict[str, Run] = field(default_factory=dict)
    model_versions: Dict[str, ModelVersion] = field(default_factory=dict)

    def create_experiment(self, experiment_name: str, description: Optional[str] = None) -> Experiment:
        """创建实验"""
        experiment_id = f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        experiment = Experiment(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            experiment_description=description
        )
        self.experiments[experiment_id] = experiment
        return experiment

    def create_run(self, experiment_id: str, run_name: str) -> Run:
        """创建运行"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        run_id = f"RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        run = Run(
            run_id=run_id,
            experiment_id=experiment_id,
            run_name=run_name
        )
        self.runs[run_id] = run
        return run

    def register_model(self, model_name: str, run_id: str, description: Optional[str] = None) -> ModelVersion:
        """注册模型"""
        if run_id not in self.runs:
            raise ValueError(f"Run {run_id} not found")

        # 获取下一个版本号
        existing_versions = [v for v in self.model_versions.values() if v.model_name == model_name]
        next_version = max([v.version for v in existing_versions], default=0) + 1

        version_id = f"MODEL-{model_name}-v{next_version}"
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            run_id=run_id,
            version=next_version,
            description=description
        )
        self.model_versions[version_id] = model_version
        return model_version

    def compare_runs(self, run_ids: List[str]) -> Dict:
        """比较运行"""
        comparison = {
            'runs': [],
            'metrics_comparison': {},
            'parameters_comparison': {}
        }

        for run_id in run_ids:
            if run_id not in self.runs:
                continue

            run = self.runs[run_id]
            comparison['runs'].append({
                'run_id': run_id,
                'run_name': run.run_name,
                'status': run.run_status.value,
                'metrics': {k: float(v) for k, v in run.metrics.items()},
                'parameters': run.parameters
            })

            # 比较指标
            for metric_name, metric_value in run.metrics.items():
                if metric_name not in comparison['metrics_comparison']:
                    comparison['metrics_comparison'][metric_name] = []
                comparison['metrics_comparison'][metric_name].append({
                    'run_id': run_id,
                    'value': float(metric_value)
                })

        return comparison

# 使用示例
if __name__ == '__main__':
    # 创建MLflow实验管理
    mlflow_mgmt = MLflowExperimentManagement()

    # 创建实验
    experiment = mlflow_mgmt.create_experiment(
        experiment_name="CustomerChurnPrediction",
        description="客户流失预测实验"
    )
    experiment.add_tag("classification")
    experiment.add_tag("customer_analytics")

    # 创建运行
    run = mlflow_mgmt.create_run(experiment.experiment_id, "RandomForest_v1")
    run.add_parameter("n_estimators", "100")
    run.add_parameter("max_depth", "10")
    run.add_parameter("learning_rate", "0.01")
    run.add_metric("accuracy", Decimal('0.85'))
    run.add_metric("precision", Decimal('0.82'))
    run.add_metric("recall", Decimal('0.88'))
    run.finish(RunStatus.FINISHED)

    # 注册模型
    model_version = mlflow_mgmt.register_model(
        model_name="CustomerChurnModel",
        run_id=run.run_id,
        description="客户流失预测模型v1"
    )
    model_version.promote_to_staging()

    print(f"实验: {experiment.experiment_name}")
    print(f"运行: {run.run_name}, 状态: {run.run_status.value}")
    print(f"模型版本: {model_version.model_name} v{model_version.version}, 阶段: {model_version.stage}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 实验管理效率 | 低 | 高 | 显著提升 |
| 实验重现性 | 60% | 100% | 40%提升 |
| 模型版本管理 | 无 | 完整 | 100% |
| 实验比较效率 | 低 | 高 | 显著提升 |

**业务价值**：

1. **实验管理统一**：统一实验管理流程
2. **实验可重现**：确保实验可重现
3. **模型版本管理**：规范模型版本管理
4. **实验比较支持**：支持实验效果比较

**经验教训**：

1. 实验跟踪很重要
2. 模型版本管理需要规范
3. 实验重现需要完整记录
4. 模型服务需要标准化

**参考案例**：

- [MLflow官方文档](https://mlflow.org/)
- [机器学习实验管理最佳实践](https://mlflow.org/docs/latest/index.html)

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
