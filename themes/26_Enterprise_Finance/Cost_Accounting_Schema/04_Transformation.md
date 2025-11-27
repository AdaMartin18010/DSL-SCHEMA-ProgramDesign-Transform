# 成本会计Schema转换体系

## 📑 目录

- [成本会计Schema转换体系](#成本会计schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ABC到标准成本转换](#2-abc到标准成本转换)
  - [3. 标准成本到实际成本转换](#3-标准成本到实际成本转换)
  - [4. 转换工具](#4-转换工具)
    - [4.1 成本核算工具](#41-成本核算工具)
  - [5. 成本数据存储与分析](#5-成本数据存储与分析)
    - [5.1 PostgreSQL成本数据存储](#51-postgresql成本数据存储)
    - [5.2 成本数据分析查询](#52-成本数据分析查询)

---

## 1. 转换体系概述

成本会计Schema转换体系支持ABC、标准成本、实际成本之间的转换，
以及成本数据存储。

### 1.1 转换目标

1. **ABC到标准成本转换**：ABC成本到标准成本格式
2. **标准成本到实际成本转换**：标准成本到实际成本格式
3. **成本到数据库转换**：成本数据到PostgreSQL存储

---

## 2. ABC到标准成本转换

**转换规则**：

- ABC作业成本 → 标准成本制造费用
- ABC成本动因 → 标准成本分配基础
- ABC产品成本 → 标准产品成本

**转换示例**：

```python
def convert_abc_to_standard_cost(abc_data: ActivityBasedCosting) -> StandardCosting:
    """将ABC成本转换为标准成本"""
    standard_costing = StandardCosting()

    # 转换产品成本
    for cost_object in abc_data.cost_objects:
        standard_cost = StandardCost()
        standard_cost.product_code = cost_object.object_code
        standard_cost.material_cost = cost_object.direct_costs
        standard_cost.overhead_cost = cost_object.allocated_costs
        standard_cost.total_standard_cost = cost_object.total_costs
        standard_costing.standard_costs.append(standard_cost)

    return standard_costing
```

---

## 3. 标准成本到实际成本转换

**转换规则**：

- 标准成本 → 实际成本基准
- 标准成本差异 → 实际成本调整
- 标准产品成本 → 实际产品成本

**转换示例**：

```python
def convert_standard_to_actual_cost(standard_data: StandardCosting, actual_data: ActualCosting) -> ActualCosting:
    """将标准成本转换为实际成本"""
    # 基于标准成本和差异计算实际成本
    for standard_cost in standard_data.standard_costs:
        actual_cost = ActualCost()
        actual_cost.cost_object_id = standard_cost.product_code
        actual_cost.cost_amount = standard_cost.total_standard_cost + standard_data.cost_variance.total_variance
        actual_data.actual_costs.append(actual_cost)

    return actual_data
```

---

## 4. 转换工具

### 4.1 成本核算工具

- **SAP Cost Accounting**：SAP成本会计模块
- **Oracle Cost Management**：Oracle成本管理模块
- **自定义成本核算器**：基于Schema的成本核算器

---

## 5. 成本数据存储与分析

### 5.1 PostgreSQL成本数据存储

**表结构设计**：

```sql
-- 作业表
CREATE TABLE activities (
    activity_id VARCHAR(50) PRIMARY KEY,
    activity_name VARCHAR(200) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    cost_pool DECIMAL(18, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 成本动因表
CREATE TABLE cost_drivers (
    driver_id VARCHAR(50) PRIMARY KEY,
    driver_name VARCHAR(200) NOT NULL,
    driver_type VARCHAR(50) NOT NULL,
    driver_quantity DECIMAL(18, 2) DEFAULT 0,
    activity_rate DECIMAL(18, 4) DEFAULT 0
);

-- 标准成本表
CREATE TABLE standard_costs (
    product_code VARCHAR(50) PRIMARY KEY,
    material_cost DECIMAL(18, 2) NOT NULL,
    labor_cost DECIMAL(18, 2) NOT NULL,
    overhead_cost DECIMAL(18, 2) NOT NULL,
    total_standard_cost DECIMAL(18, 2) NOT NULL,
    effective_date DATE NOT NULL
);

-- 实际成本表
CREATE TABLE actual_costs (
    cost_id VARCHAR(50) PRIMARY KEY,
    cost_object_id VARCHAR(50) NOT NULL,
    cost_type VARCHAR(50) NOT NULL,
    cost_amount DECIMAL(18, 2) NOT NULL,
    cost_date DATE NOT NULL
);

-- 成本差异表
CREATE TABLE cost_variances (
    variance_id VARCHAR(50) PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL,
    standard_cost DECIMAL(18, 2) NOT NULL,
    actual_cost DECIMAL(18, 2) NOT NULL,
    total_variance DECIMAL(18, 2) NOT NULL,
    price_variance DECIMAL(18, 2),
    quantity_variance DECIMAL(18, 2),
    variance_date DATE NOT NULL
);

-- 创建索引
CREATE INDEX idx_actual_costs_object ON actual_costs(cost_object_id);
CREATE INDEX idx_cost_variances_product ON cost_variances(product_code);
```

**数据插入示例**：

```python
def store_cost_data(cost_data: CostAccountingSchema, conn):
    """存储成本数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入标准成本
    for standard_cost in cost_data.standard_costing.standard_costs:
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

    conn.commit()
```

### 5.2 成本数据分析查询

**查询示例**：

```python
def analyze_cost_data(conn, product_code, period_start, period_end):
    """分析成本数据"""
    cursor = conn.cursor()

    # 查询成本差异
    cursor.execute("""
        SELECT
            product_code,
            standard_cost,
            actual_cost,
            total_variance,
            price_variance,
            quantity_variance
        FROM cost_variances
        WHERE product_code = %s AND variance_date BETWEEN %s AND %s
        ORDER BY variance_date
    """, (product_code, period_start, period_end))

    variance_analysis = cursor.fetchall()

    # 查询成本趋势
    cursor.execute("""
        SELECT
            cost_date,
            SUM(cost_amount) as total_cost
        FROM actual_costs
        WHERE cost_object_id = %s AND cost_date BETWEEN %s AND %s
        GROUP BY cost_date
        ORDER BY cost_date
    """, (product_code, period_start, period_end))

    cost_trends = cursor.fetchall()

    return {
        "variance_analysis": variance_analysis,
        "cost_trends": cost_trends
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
