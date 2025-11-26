# 成本会计Schema实践案例

## 📑 目录

- [成本会计Schema实践案例](#成本会计schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：作业成本法产品成本核算](#2-案例1作业成本法产品成本核算)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：标准成本差异分析](#3-案例2标准成本差异分析)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：成本分配](#4-案例3成本分配)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：ABC到标准成本转换](#5-案例4abc到标准成本转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：成本数据存储与分析系统](#6-案例5成本数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供成本会计Schema在实际应用中的实践案例。

---

## 2. 案例1：作业成本法产品成本核算

### 2.1 场景描述

**应用场景**：
使用作业成本法进行产品成本核算，识别作业、计算作业成本率、分配间接成本。

**业务需求**：

- 识别主要作业和成本动因
- 计算作业成本率
- 将间接成本分配到产品
- 计算产品总成本

### 2.2 Schema定义

**作业成本法产品成本核算Schema**：

```dsl
schema ABCProductCosting {
  activities: List<Activity> {
    activity1: Activity {
      activity_id: String @value("ACT-001")
      activity_name: String @value("机器设置")
      activity_type: Enum @value("BatchLevel")
      cost_pool: Decimal @value(50000.00)
    }
    activity2: Activity {
      activity_id: String @value("ACT-002")
      activity_name: String @value("质量检验")
      activity_type: Enum @value("BatchLevel")
      cost_pool: Decimal @value(30000.00)
    }
  }

  cost_drivers: List<CostDriver> {
    driver1: CostDriver {
      driver_id: String @value("DRIVER-001")
      driver_name: String @value("设置次数")
      driver_type: Enum @value("Transaction")
      driver_quantity: Decimal @value(100.00)
      activity_rate: Decimal @value(500.00)
    }
    driver2: CostDriver {
      driver_id: String @value("DRIVER-002")
      driver_name: String @value("检验批次")
      driver_type: Enum @value("Transaction")
      driver_quantity: Decimal @value(50.00)
      activity_rate: Decimal @value(600.00)
    }
  }

  cost_objects: List<ABCCostObject> {
    product1: ABCCostObject {
      object_id: String @value("PROD-001")
      object_code: String @value("产品A")
      direct_costs: Decimal @value(100000.00)
      activity_consumption: Map<String, Decimal> {
        "ACT-001": Decimal @value(20.00)
        "ACT-002": Decimal @value(10.00)
      }
      allocated_costs: Decimal @value(16000.00)
      total_costs: Decimal @value(116000.00)
    }
  }
} @standard("ABC")
```

---

## 3. 案例2：标准成本差异分析

### 3.1 场景描述

**应用场景**：
标准成本差异分析，包括价格差异、数量差异、效率差异分析。

**业务需求**：

- 计算标准成本和实际成本
- 分析成本差异
- 识别差异原因
- 采取改进措施

### 3.2 Schema定义

**标准成本差异分析Schema**：

```dsl
schema StandardCostVarianceAnalysis {
  standard_cost: StandardCost {
    product_code: String @value("PROD-001")
    material_cost: Decimal @value(50000.00)
    labor_cost: Decimal @value(30000.00)
    overhead_cost: Decimal @value(20000.00)
    total_standard_cost: Decimal @value(100000.00)
  }

  cost_variance: CostVariance {
    product_code: String @value("PROD-001")
    standard_cost: Decimal @value(100000.00)
    actual_cost: Decimal @value(110000.00)
    total_variance: Decimal @value(10000.00)
    price_variance: PriceVariance {
      material_price_variance: Decimal @value(5000.00)
      labor_price_variance: Decimal @value(2000.00)
    }
    quantity_variance: QuantityVariance {
      material_quantity_variance: Decimal @value(2000.00)
      labor_efficiency_variance: Decimal @value(1000.00)
    }
  }
} @standard("Standard Costing")
```

---

## 4. 案例3：成本分配

### 4.1 场景描述

**应用场景**：
成本中心成本分配，将服务部门成本分配到生产部门。

**业务需求**：

- 识别分配基础
- 选择分配方法
- 计算分配金额
- 验证分配结果

### 4.2 Schema定义

**成本分配Schema**：

```dsl
schema CostAllocation {
  allocation_bases: List<AllocationBase> {
    base1: AllocationBase {
      base_id: String @value("BASE-001")
      base_type: Enum @value("DirectLabor")
      base_amount: Decimal @value(10000.00)
    }
  }

  allocated_costs: List<AllocatedCost> {
    allocation1: AllocatedCost {
      allocation_id: String @value("ALLOC-001")
      cost_center_from: String @value("CC-SERVICE")
      cost_center_to: String @value("CC-PRODUCTION")
      allocation_base_id: String @value("BASE-001")
      allocation_amount: Decimal @value(50000.00)
      allocation_rate: Decimal @value(5.00)
    }
  }
} @standard("Cost Allocation")
```

---

## 5. 案例4：ABC到标准成本转换

### 5.1 场景描述

**应用场景**：
将ABC成本转换为标准成本，用于成本控制和预算编制。

**业务需求**：

- 转换ABC产品成本到标准成本
- 保持成本信息一致性
- 支持成本对比分析

### 5.2 实现代码

```python
from cost_accounting_schema import ActivityBasedCosting, StandardCosting

def convert_abc_to_standard_cost(abc_data: ActivityBasedCosting) -> StandardCosting:
    """将ABC成本转换为标准成本"""
    standard_costing = StandardCosting()

    # 转换产品成本
    for cost_object in abc_data.cost_objects:
        standard_cost = StandardCost()
        standard_cost.product_code = cost_object.object_code
        standard_cost.material_cost = cost_object.direct_costs * 0.6  # 假设60%为材料成本
        standard_cost.labor_cost = cost_object.direct_costs * 0.3  # 假设30%为人工成本
        standard_cost.overhead_cost = cost_object.allocated_costs  # 间接成本
        standard_cost.total_standard_cost = cost_object.total_costs
        standard_costing.standard_costs.append(standard_cost)

    return standard_costing

# 使用示例
abc_data = ActivityBasedCosting.load_from_database("2025-01")
standard_costing = convert_abc_to_standard_cost(abc_data)
standard_costing.save_to_database()
```

---

## 6. 案例5：成本数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业成本数据存储与分析系统，支持成本数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持成本差异报告生成
- 支持成本趋势分析

### 6.2 实现代码

```python
import psycopg2
from cost_accounting_schema import CostAccountingSchema, StandardCost, ActualCost

class CostDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_standard_cost(self, standard_cost: StandardCost):
        """存储标准成本"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO standard_costs
            (product_code, material_cost, labor_cost, overhead_cost, total_standard_cost, effective_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_code) DO UPDATE SET
                material_cost = EXCLUDED.material_cost,
                labor_cost = EXCLUDED.labor_cost,
                overhead_cost = EXCLUDED.overhead_cost,
                total_standard_cost = EXCLUDED.total_standard_cost
        """, (standard_cost.product_code, standard_cost.material_cost,
              standard_cost.labor_cost, standard_cost.overhead_cost,
              standard_cost.total_standard_cost, "2025-01-01"))

        self.conn.commit()

    def generate_cost_variance_report(self, product_code, period_start, period_end):
        """生成成本差异报告"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                cv.product_code,
                sc.total_standard_cost,
                SUM(ac.cost_amount) as actual_cost,
                SUM(ac.cost_amount) - sc.total_standard_cost as total_variance,
                cv.price_variance,
                cv.quantity_variance
            FROM cost_variances cv
            JOIN standard_costs sc ON cv.product_code = sc.product_code
            LEFT JOIN actual_costs ac ON cv.product_code = ac.cost_object_id
            WHERE cv.product_code = %s AND cv.variance_date BETWEEN %s AND %s
            GROUP BY cv.product_code, sc.total_standard_cost, cv.price_variance, cv.quantity_variance
        """, (product_code, period_start, period_end))

        return cursor.fetchall()

# 使用示例
db_config = {
    "host": "localhost",
    "database": "cost_accounting",
    "user": "cost_user",
    "password": "password"
}

store = CostDataStore(db_config)

# 生成成本差异报告
variance_report = store.generate_cost_variance_report("PROD-001", "2025-01-01", "2025-01-31")
print("成本差异报告:")
for row in variance_report:
    print(f"产品: {row[0]}, 标准成本: {row[1]}, 实际成本: {row[2]}, 总差异: {row[3]}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
