# 数据分析Schema实践案例

## 📑 目录

- [数据分析Schema实践案例](#数据分析schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：销售数据分析](#2-案例1销售数据分析)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：客户行为分析](#3-案例2客户行为分析)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：预测分析](#4-案例3预测分析)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：数据分析到数据仓库转换](#5-案例4数据分析到数据仓库转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：数据分析数据存储与分析系统](#6-案例5数据分析数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供数据分析Schema在实际应用中的实践案例。

---

## 2. 案例1：销售数据分析

### 2.1 场景描述

**应用场景**：
企业销售数据分析，包括销售趋势分析、销售预测、客户分析。

**业务需求**：

- 分析销售趋势
- 预测未来销售
- 分析客户行为
- 生成销售报表

### 2.2 Schema定义

**销售数据分析Schema**：

```dsl
schema SalesDataAnalysis {
  data_collection: DataCollection {
    data_sources: List<DataSource> {
      source1: DataSource {
        source_id: String @value("DS-SALES")
        source_type: Enum @value("Database")
        source_connection: String @value("postgresql://sales_db")
      }
    }
  }

  data_analysis: DataAnalysis {
    statistical_analysis: StatisticalAnalysis {
      analyses: List<Analysis> {
        analysis1: Analysis {
          analysis_id: String @value("ANALYSIS-SALES-TREND")
          analysis_type: Enum @value("Descriptive")
          analysis_method: String @value("Time Series Analysis")
          output_results: Map<String, Decimal> {
            "average_sales": Decimal @value(100000.00)
            "growth_rate": Decimal @value(10.50)
          }
        }
      }
    }
    predictive_analysis: PredictiveAnalysis {
      forecasts: List<Forecast> {
        forecast1: Forecast {
          forecast_id: String @value("FORECAST-SALES-2025")
          forecast_type: Enum @value("TimeSeries")
          forecast_period: Date @value("2025-12-31")
          forecast_value: Decimal @value(1200000.00)
          confidence_level: Decimal @value(85.00)
        }
      }
    }
  }

  data_visualization: DataVisualization {
    dashboards: List<Dashboard> {
      dashboard1: Dashboard {
        dashboard_id: String @value("DASHBOARD-SALES")
        dashboard_name: String @value("销售分析仪表板")
        dashboard_components: List<DashboardComponent> {
          component1: DashboardComponent {
            component_type: Enum @value("Chart")
            component_config: Map<String, String> {
              "chart_type": String @value("Line")
              "data_source": String @value("sales_trend")
            }
          }
        }
      }
    }
  }
} @standard("Kimball", "OLAP")
```

---

## 3. 案例2：客户行为分析

### 3.1 场景描述

**应用场景**：
企业客户行为分析，包括客户细分、客户预测、客户价值分析。

**业务需求**：

- 客户细分
- 客户行为预测
- 客户价值分析
- 客户推荐

### 3.2 Schema定义

**客户行为分析Schema**：

```dsl
schema CustomerBehaviorAnalysis {
  data_analysis: DataAnalysis {
    machine_learning: MachineLearning {
      models: List<MLModel> {
        model1: MLModel {
          model_id: String @value("MODEL-CUSTOMER-SEGMENT")
          model_type: Enum @value("Unsupervised")
          algorithm: String @value("K-Means Clustering")
          model_accuracy: Decimal @value(90.00)
        }
        model2: MLModel {
          model_id: String @value("MODEL-CUSTOMER-PREDICT")
          model_type: Enum @value("Supervised")
          algorithm: String @value("Random Forest")
          model_accuracy: Decimal @value(85.00)
        }
      }
      predictions: List<Prediction> {
        prediction1: Prediction {
          prediction_id: String @value("PRED-CUSTOMER-001")
          model_id: String @value("MODEL-CUSTOMER-PREDICT")
          predicted_value: Decimal @value(5000.00)
          confidence_score: Decimal @value(88.00)
        }
      }
    }
  }
} @standard("Machine Learning")
```

---

## 4. 案例3：预测分析

### 4.1 场景描述

**应用场景**：
企业预测分析，包括需求预测、销售预测、风险预测。

**业务需求**：

- 需求预测
- 销售预测
- 风险预测
- 预测准确性评估

### 4.2 Schema定义

**预测分析Schema**：

```dsl
schema PredictiveAnalysis {
  predictive_analysis: PredictiveAnalysis {
    forecasts: List<Forecast> {
      forecast1: Forecast {
        forecast_id: String @value("FORECAST-DEMAND-2025")
        forecast_type: Enum @value("TimeSeries")
        forecast_method: String @value("ARIMA")
        forecast_period: Date @value("2025-12-31")
        forecast_value: Decimal @value(1000000.00)
        confidence_level: Decimal @value(90.00)
      }
      forecast2: Forecast {
        forecast_id: String @value("FORECAST-SALES-2025")
        forecast_type: Enum @value("Regression")
        forecast_method: String @value("Linear Regression")
        forecast_period: Date @value("2025-12-31")
        forecast_value: Decimal @value(2000000.00)
        confidence_level: Decimal @value(85.00)
      }
    }
  }
} @standard("Predictive Analytics")
```

---

## 5. 案例4：数据分析到数据仓库转换

### 5.1 场景描述

**应用场景**：
将企业数据分析结果转换为数据仓库格式，用于数据仓库建设。

**业务需求**：

- 分析结果转换为事实表
- 分析维度转换为维度表
- 分析指标转换为度量值

### 5.2 实现代码

```python
from data_analytics_schema import DataAnalyticsSchema
from data_warehouse_schema import DataWarehouseSchema, StarSchema, FactTable, DimensionTable

def convert_analytics_to_data_warehouse(analytics_data: DataAnalyticsSchema) -> DataWarehouseSchema:
    """将数据分析数据转换为数据仓库格式"""
    dw_schema = DataWarehouseSchema()

    # 转换星型模式
    star_schema = StarSchema()

    # 创建销售事实表
    fact_table = FactTable()
    fact_table.fact_table_name = "sales_fact"
    fact_table.measures = [
        {"name": "sales_amount", "type": "Decimal"},
        {"name": "quantity", "type": "Integer"},
        {"name": "profit", "type": "Decimal"}
    ]
    fact_table.grain = "Daily Sales by Product and Customer"
    star_schema.fact_tables.append(fact_table)

    # 创建产品维度表
    product_dimension = DimensionTable()
    product_dimension.dimension_name = "product_dimension"
    product_dimension.dimension_attributes = [
        "product_id", "product_name", "product_category", "product_price"
    ]
    star_schema.dimension_tables.append(product_dimension)

    # 创建客户维度表
    customer_dimension = DimensionTable()
    customer_dimension.dimension_name = "customer_dimension"
    customer_dimension.dimension_attributes = [
        "customer_id", "customer_name", "customer_segment", "customer_region"
    ]
    star_schema.dimension_tables.append(customer_dimension)

    dw_schema.star_schema = star_schema

    return dw_schema

# 使用示例
analytics_data = DataAnalyticsSchema.load_from_database("2025-01")
dw_schema = convert_analytics_to_data_warehouse(analytics_data)
dw_schema.save_to_database()
```

---

## 6. 案例5：数据分析数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业数据分析数据存储与分析系统，支持数据分析数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持数据质量监控
- 支持模型性能分析

### 6.2 实现代码

```python
import psycopg2
from data_analytics_schema import DataAnalyticsSchema, DataSource, MLModel

class AnalyticsDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_analytics_data(self, analytics_data: DataAnalyticsSchema):
        """存储数据分析数据"""
        cursor = self.conn.cursor()

        # 插入数据源
        for source in analytics_data.data_collection.data_sources:
            cursor.execute("""
                INSERT INTO data_sources
                (source_id, source_type, source_connection, is_active)
                VALUES (%s, %s, %s, %s)
            """, (source.source_id, source.source_type,
                  source.source_connection, source.is_active))

        # 插入机器学习模型
        for model in analytics_data.data_analysis.machine_learning.models:
            cursor.execute("""
                INSERT INTO ml_models
                (model_id, model_type, algorithm, model_accuracy, training_date, model_version)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (model.model_id, model.model_type, model.algorithm,
                  model.model_accuracy, "2025-01-21", "v1.0"))

        self.conn.commit()

    def generate_analytics_report(self, period_start, period_end):
        """生成数据分析报告"""
        cursor = self.conn.cursor()

        # 查询数据质量趋势
        cursor.execute("""
            SELECT
                check_date,
                AVG(metric_value) as avg_quality_score,
                COUNT(CASE WHEN is_passed THEN 1 END) as passed_metrics,
                COUNT(*) as total_metrics
            FROM data_quality_metrics
            WHERE check_date BETWEEN %s AND %s
            GROUP BY check_date
            ORDER BY check_date
        """, (period_start, period_end))

        quality_trends = cursor.fetchall()

        # 查询模型性能
        cursor.execute("""
            SELECT
                model_type,
                AVG(model_accuracy) as avg_accuracy,
                COUNT(*) as model_count
            FROM ml_models
            WHERE training_date BETWEEN %s AND %s
            GROUP BY model_type
            ORDER BY avg_accuracy DESC
        """, (period_start, period_end))

        model_performance = cursor.fetchall()

        return {
            "quality_trends": quality_trends,
            "model_performance": model_performance
        }

# 使用示例
db_config = {
    "host": "localhost",
    "database": "data_analytics",
    "user": "analytics_user",
    "password": "password"
}

store = AnalyticsDataStore(db_config)

# 生成数据分析报告
analytics_report = store.generate_analytics_report("2025-01-01", "2025-12-31")
print("数据质量趋势:")
for row in analytics_report["quality_trends"]:
    print(f"日期: {row[0]}, 平均质量: {row[1]:.2f}, 通过: {row[2]}/{row[3]}")

print("\n模型性能:")
for row in analytics_report["model_performance"]:
    print(f"{row[0]}: 平均准确率={row[1]:.2f}%, 模型数={row[2]}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
