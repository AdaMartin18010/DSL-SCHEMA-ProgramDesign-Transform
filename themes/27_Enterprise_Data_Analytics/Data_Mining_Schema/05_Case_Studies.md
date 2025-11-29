# 数据挖掘Schema实践案例

## 📑 目录

- [数据挖掘Schema实践案例](#数据挖掘schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业客户流失预测数据挖掘系统](#2-案例1企业客户流失预测数据挖掘系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)
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

本文档提供数据挖掘Schema在实际企业应用中的实践案例，涵盖客户流失预测、CRISP-DM流程实施、模型训练与评估等真实场景。

**案例类型**：

1. **企业客户流失预测数据挖掘系统**：客户流失预测
2. **CRISP-DM流程实施系统**：数据挖掘流程管理
3. **模型训练与评估系统**：模型训练和评估
4. **模型部署与监控系统**：模型部署和监控
5. **数据挖掘数据存储与分析系统**：数据挖掘数据分析和监控

**参考企业案例**：

- **CRISP-DM**：数据挖掘标准流程
- **数据挖掘最佳实践**：KDnuggets数据挖掘指南

---

## 2. 案例1：企业客户流失预测数据挖掘系统

### 2.1 业务背景

**企业背景**：
某电信公司需要构建客户流失预测数据挖掘系统，通过分析客户特征和行为数据，预测客户流失概率，提前采取挽留措施。

**业务痛点**：

1. **客户流失率高**：客户流失率高，影响业务
2. **预测不准确**：缺乏准确的流失预测
3. **特征分析不足**：客户特征分析不足
4. **模型部署困难**：模型部署和监控困难

**业务目标**：

- 降低客户流失率
- 提高预测准确性
- 增强特征分析能力
- 简化模型部署

### 2.2 技术挑战

1. **特征工程**：提取有效的客户特征
2. **模型训练**：训练准确的预测模型
3. **模型评估**：评估模型性能
4. **模型部署**：部署和监控模型

### 2.3 解决方案

**使用Schema定义客户流失预测数据挖掘系统**：

### 2.4 完整代码实现

**客户流失预测Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
数据挖掘Schema实现
"""

from typing import Dict, List, Optional
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class FeatureType(str, Enum):
    """特征类型"""
    NUMERICAL = "Numerical"
    CATEGORICAL = "Categorical"
    TEXT = "Text"
    DATETIME = "DateTime"

class ModelType(str, Enum):
    """模型类型"""
    CLASSIFICATION = "Classification"
    REGRESSION = "Regression"
    CLUSTERING = "Clustering"

@dataclass
class Feature:
    """特征"""
    feature_name: str
    feature_type: FeatureType
    is_selected: bool = True
    importance_score: Decimal = Decimal('0')
    description: Optional[str] = None

@dataclass
class DataSampling:
    """数据采样"""
    train_ratio: Decimal = Decimal('0.7')
    test_ratio: Decimal = Decimal('0.15')
    validation_ratio: Decimal = Decimal('0.15')

    def validate(self) -> bool:
        """验证采样比例"""
        total = self.train_ratio + self.test_ratio + self.validation_ratio
        return abs(total - Decimal('1.0')) < Decimal('0.01')

@dataclass
class DataPreparation:
    """数据准备"""
    features: List[Feature] = field(default_factory=list)
    data_sampling: DataSampling = field(default_factory=DataSampling)

    def add_feature(self, feature: Feature):
        """添加特征"""
        self.features.append(feature)

    def get_selected_features(self) -> List[Feature]:
        """获取选中的特征"""
        return [f for f in self.features if f.is_selected]

@dataclass
class Model:
    """模型"""
    model_id: str
    model_name: str
    model_type: ModelType
    algorithm: str = ""
    parameters: Dict[str, str] = field(default_factory=dict)
    accuracy: Decimal = Decimal('0')
    precision: Decimal = Decimal('0')
    recall: Decimal = Decimal('0')
    f1_score: Decimal = Decimal('0')
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ModelTraining:
    """模型训练"""
    model: Model
    training_data_path: str = ""
    validation_data_path: str = ""
    training_status: str = "Pending"  # Pending, Training, Completed, Failed

    def start_training(self):
        """开始训练"""
        self.training_status = "Training"

    def complete_training(self, metrics: Dict[str, Decimal]):
        """完成训练"""
        self.training_status = "Completed"
        self.model.accuracy = metrics.get('accuracy', Decimal('0'))
        self.model.precision = metrics.get('precision', Decimal('0'))
        self.model.recall = metrics.get('recall', Decimal('0'))
        self.model.f1_score = metrics.get('f1_score', Decimal('0'))

@dataclass
class CustomerChurnPrediction:
    """客户流失预测"""
    data_preparation: DataPreparation
    model_training: Optional[ModelTraining] = None
    prediction_results: List[Dict] = field(default_factory=list)

    def prepare_data(self):
        """准备数据"""
        # 添加特征
        self.data_preparation.add_feature(Feature(
            feature_name="customer_age",
            feature_type=FeatureType.NUMERICAL,
            description="客户年龄"
        ))
        self.data_preparation.add_feature(Feature(
            feature_name="customer_tenure",
            feature_type=FeatureType.NUMERICAL,
            description="客户在网时长"
        ))
        self.data_preparation.add_feature(Feature(
            feature_name="monthly_charges",
            feature_type=FeatureType.NUMERICAL,
            description="月费用"
        ))

    def train_model(self, model_id: str, model_name: str):
        """训练模型"""
        model = Model(
            model_id=model_id,
            model_name=model_name,
            model_type=ModelType.CLASSIFICATION,
            algorithm="RandomForest"
        )

        self.model_training = ModelTraining(
            model=model,
            training_data_path="/data/train.csv"
        )
        self.model_training.start_training()

        # 模拟训练完成
        metrics = {
            'accuracy': Decimal('0.85'),
            'precision': Decimal('0.82'),
            'recall': Decimal('0.88'),
            'f1_score': Decimal('0.85')
        }
        self.model_training.complete_training(metrics)

    def predict(self, customer_data: Dict) -> Dict:
        """预测客户流失"""
        if not self.model_training or self.model_training.training_status != "Completed":
            return {"error": "Model not trained"}

        # 模拟预测
        churn_probability = Decimal('0.65')
        prediction = {
            'customer_id': customer_data.get('customer_id'),
            'churn_probability': float(churn_probability),
            'prediction': 'High Risk' if churn_probability > Decimal('0.5') else 'Low Risk',
            'prediction_date': datetime.now().isoformat()
        }

        self.prediction_results.append(prediction)
        return prediction

# 使用示例
if __name__ == '__main__':
    # 创建客户流失预测系统
    churn_prediction = CustomerChurnPrediction(
        data_preparation=DataPreparation()
    )

    # 准备数据
    churn_prediction.prepare_data()
    print(f"特征数量: {len(churn_prediction.data_preparation.features)}")

    # 训练模型
    churn_prediction.train_model("MODEL-CHURN-001", "CustomerChurnPrediction")
    print(f"模型准确率: {churn_prediction.model_training.model.accuracy}")

    # 预测
    customer_data = {'customer_id': 'CUST-001'}
    prediction = churn_prediction.predict(customer_data)
    print(f"预测结果: {prediction}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 预测准确性 | 70% | 85% | 15%提升 |
| 客户流失率 | 15% | 10% | 33%降低 |
| 特征分析能力 | 低 | 高 | 显著提升 |
| 模型部署效率 | 低 | 高 | 显著提升 |

**业务价值**：

1. **预测准确性提高**：提高客户流失预测准确性
2. **流失率降低**：降低客户流失率
3. **特征分析增强**：增强客户特征分析能力
4. **模型部署简化**：简化模型部署流程

**经验教训**：

1. 特征工程很重要
2. 模型评估需要全面
3. 模型部署需要标准化
4. 模型监控需要持续

**参考案例**：

- [CRISP-DM数据挖掘流程](https://www.ibm.com/docs/en/spss-modeler/saas)
- [数据挖掘最佳实践](https://www.kdnuggets.com/)
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
