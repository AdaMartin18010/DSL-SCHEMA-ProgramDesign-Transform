# 数据转换模块

## 📋 模块概述

数据转换模块专注于**数据模型转换、数据处理**相关的转换功能。

## 🎯 核心功能

### 1. 增量转换器（IncrementalConverter）

**功能**：

- Schema变更检测（哈希比较、详细变更检测）
- 依赖图构建（表依赖、外键依赖）
- 增量转换（按依赖顺序转换）
- PostgreSQL DDL生成

**使用示例**：

```python
from code.data_transformation import IncrementalConverter

converter = IncrementalConverter()

old_schema = {
    'tables': {
        'users': {
            'fields': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        }
    }
}

new_schema = {
    'tables': {
        'users': {
            'fields': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'email': {'type': 'string'}  # 新增字段
            }
        }
    }
}

result = converter.incremental_convert(old_schema, new_schema, 'postgresql')
print(result['conversion_result']['statements'])
```

### 2. 数据模型转换器（DataModelConverter）

**功能**：

- 星型模式到PostgreSQL转换
- 雪花模式到PostgreSQL转换
- Data Vault到PostgreSQL转换
- 星型模式与雪花模式互转
- 星型模式与Data Vault互转

**使用示例**：

```python
from code.data_transformation import DataModelConverter, DataModelType

converter = DataModelConverter()

star_model = {
    'fact_tables': [{
        'name': 'sales_fact',
        'measures': [
            {'name': 'amount', 'data_type': 'decimal'},
            {'name': 'quantity', 'data_type': 'integer'}
        ],
        'dimension_keys': [
            {'name': 'customer', 'dimension_table': 'customer_dim'},
            {'name': 'product', 'dimension_table': 'product_dim'}
        ]
    }],
    'dimension_tables': [{
        'name': 'customer_dim',
        'attributes': [
            {'name': 'customer_name', 'data_type': 'string'},
            {'name': 'region', 'data_type': 'string'}
        ]
    }]
}

# 转换为PostgreSQL
result = converter.convert(star_model, DataModelType.STAR, 'postgresql')

# 生成DDL
ddl = converter.generate_sql_ddl(result)
print(ddl)
```

### 3. 数据处理器（DataProcessor）

**功能**：

- ETL管道处理（提取、转换、加载）
- 数据分析处理

**使用示例**：

```python
from code.data_transformation import DataProcessor

processor = DataProcessor()

# 处理ETL管道
etl_config = {
    'extract': {
        'data_sources': ['sales_db'],
        'rules': []
    },
    'transform': {
        'rules': [],
        'quality_checks': []
    },
    'load': {
        'targets': ['warehouse_db'],
        'strategy': 'append'
    }
}

result = processor.process_etl_pipeline(etl_config)
print(result)
```

### 4. ETL处理器（ETLProcessor）

**功能**：

- ETL管道创建和执行
- 数据提取（全量、增量、CDC）
- 数据转换（清洗、验证、丰富、聚合、关联）
- 数据加载（追加、更新插入、替换、合并）
- 执行历史记录

**使用示例**：

```python
from code.data_transformation import ETLProcessor

processor = ETLProcessor()

# 创建ETL管道
pipeline_config = {
    'pipeline_id': 'sales_etl',
    'name': '销售数据ETL管道',
    'extract': [{
        'rule_id': 'extract_sales',
        'source_type': 'database',
        'source_config': {
            'table': 'sales_source',
            'connection': 'postgresql://localhost/sales_db'
        },
        'extract_type': 'incremental',
        'batch_size': 1000
    }],
    'transform': [{
        'rule_id': 'clean_sales',
        'transform_type': 'clean',
        'source_fields': ['customer_name', 'product_name'],
        'target_fields': ['customer_name', 'product_name']
    }],
    'load': [{
        'rule_id': 'load_sales',
        'target_type': 'database',
        'target_config': {
            'table': 'sales_warehouse',
            'connection': 'postgresql://localhost/warehouse_db'
        },
        'load_type': 'append'
    }]
}

pipeline = processor.create_pipeline(pipeline_config)
result = processor.execute_pipeline(pipeline.pipeline_id)
```

### 5. 数据分析处理器（DataAnalyticsProcessor）

**功能**：

- 统计分析
- 预测分析
- 描述性分析
- 诊断分析
- 规范性分析

**使用示例**：

```python
from code.data_transformation import DataAnalyticsProcessor

processor = DataAnalyticsProcessor()

# 创建分析规则
rule_config = {
    'rule_id': 'sales_analysis',
    'analysis_type': 'statistical',
    'data_sources': ['sales_data'],
    'metrics': ['amount', 'quantity'],
    'dimensions': ['region', 'product_category']
}

rule = processor.create_analysis_rule(rule_config)

# 执行分析
sample_data = [
    {'region': 'North', 'product_category': 'Electronics', 'amount': 1000, 'quantity': 10},
    {'region': 'South', 'product_category': 'Electronics', 'amount': 1500, 'quantity': 15},
]

result = processor.execute_analysis(rule.rule_id, sample_data)
print(f"指标: {result.metrics}")
print(f"洞察: {result.insights}")
```

### 6. 数据质量检查器（DataQualityChecker）

**功能**：

- 数据质量规则定义
- 完整性检查
- 准确性检查
- 一致性检查

**使用示例**：

```python
from code.data_transformation import DataQualityChecker

checker = DataQualityChecker()

# 添加质量规则
checker.add_quality_rule('sales_quality', {
    'field': 'amount',
    'type': 'completeness'
})

checker.add_quality_rule('sales_quality', {
    'field': 'amount',
    'type': 'range',
    'min': 0
})

# 检查数据质量
data = [
    {'amount': 100, 'quantity': 10},
    {'amount': None, 'quantity': 5},  # 质量问题
    {'amount': -50, 'quantity': 3},  # 质量问题
]

result = checker.check_data_quality(data, 'sales_quality')
print(f"质量分数: {result['quality_score']}%")
print(f"问题: {result['issues']}")
```

## 📁 文件结构

```
code/data_transformation/
├── __init__.py
├── incremental_converter.py      # 增量转换器
├── data_model_converter.py        # 数据模型转换器
├── etl_processor.py               # ETL处理器
├── data_analytics_processor.py    # 数据分析处理器
└── README.md                      # 本文档
```

## 🔧 依赖

- Python 3.8+
- 标准库：typing, dataclasses, enum, datetime, hashlib, json

## 📝 使用说明

1. **导入模块**：

```python
from code.data_transformation import (
    IncrementalConverter,
    DataModelConverter,
    DataModelType,
    ETLProcessor,
    DataAnalyticsProcessor,
    DataQualityChecker
)
```

2. **使用转换器**：

```python
# 增量转换
converter = IncrementalConverter()
result = converter.incremental_convert(old_schema, new_schema, 'postgresql')

# 数据模型转换
model_converter = DataModelConverter()
result = model_converter.convert(star_model, DataModelType.STAR, 'postgresql')
```

3. **使用处理器**：

```python
# ETL处理
etl_processor = ETLProcessor()
pipeline = etl_processor.create_pipeline(pipeline_config)
result = etl_processor.execute_pipeline(pipeline.pipeline_id)

# 数据分析
analytics_processor = DataAnalyticsProcessor()
rule = analytics_processor.create_analysis_rule(rule_config)
result = analytics_processor.execute_analysis(rule.rule_id, data)
```

## 🎯 核心特性

### 数据模型转换

- ✅ 星型模式 ↔ PostgreSQL
- ✅ 雪花模式 ↔ PostgreSQL
- ✅ Data Vault ↔ PostgreSQL
- ✅ 星型模式 ↔ 雪花模式
- ✅ 星型模式 ↔ Data Vault

### 数据处理

- ✅ ETL管道（提取、转换、加载）
- ✅ 数据分析（统计、预测、描述、诊断、规范）
- ✅ 数据质量检查（完整性、准确性、一致性）

### 增量转换

- ✅ Schema变更检测
- ✅ 依赖分析
- ✅ 增量转换执行
- ✅ PostgreSQL DDL生成

## 📊 代码统计

- **总代码行数**：约2,500行
- **核心类数量**：6个
- **方法数量**：约80个

## 🔄 后续计划

1. **完善依赖传播算法**：实现完整的依赖传播和影响分析
2. **冲突处理**：实现变更冲突检测和解决策略
3. **性能优化**：缓存机制、并行处理、延迟计算
4. **测试验证**：单元测试、集成测试、性能测试
5. **扩展支持**：支持更多数据模型类型和转换方向

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
