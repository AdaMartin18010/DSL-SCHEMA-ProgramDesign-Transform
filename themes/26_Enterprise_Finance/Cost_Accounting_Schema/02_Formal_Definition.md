# 成本会计Schema形式化定义

## 📑 目录

- [成本会计Schema形式化定义](#成本会计schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 作业成本法Schema](#2-作业成本法schema)
  - [3. 标准成本法Schema](#3-标准成本法schema)
  - [4. 实际成本法Schema](#4-实际成本法schema)
  - [5. 成本分配Schema](#5-成本分配schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 成本分配定理](#91-成本分配定理)
    - [9.2 标准成本差异定理](#92-标准成本差异定理)
    - [9.3 作业成本分配定理](#93-作业成本分配定理)

---

## 1. 形式化模型

**定义1（成本会计Schema）**：
成本会计Schema是一个四元组：

```text
Cost_Accounting_Schema = (Activity_Based_Costing, Standard_Costing,
                          Actual_Costing, Cost_Allocation)
```

其中：

- `Activity_Based_Costing`：作业成本法Schema
- `Standard_Costing`：标准成本法Schema
- `Actual_Costing`：实际成本法Schema
- `Cost_Allocation`：成本分配Schema

---

## 2. 作业成本法Schema

**定义2（作业成本法Schema）**：

```text
Activity_Based_Costing_Schema = (Activity, Activity_Cost_Pool,
                                Cost_Driver, Activity_Rate)
```

**形式化DSL定义**：

```dsl
schema ActivityBasedCosting {
  activities: List<Activity> {
    activity_id: String @required @unique
    activity_name: String @required
    activity_type: Enum { UnitLevel, BatchLevel, ProductLevel, FacilityLevel } @required
    cost_pool: Decimal @default(0)
  }

  activity_cost_pools: List<ActivityCostPool> {
    pool_id: String @required @unique
    pool_name: String @required
    total_cost: Decimal @required @range(0, null)
    cost_driver_id: String @required
  }

  cost_drivers: List<CostDriver> {
    driver_id: String @required @unique
    driver_name: String @required
    driver_type: Enum { Volume, Transaction, Duration } @required
    driver_quantity: Decimal @default(0)
    activity_rate: Decimal @computed("pool.total_cost / driver_quantity")
  }

  cost_objects: List<ABCCostObject> {
    object_id: String @required @unique
    object_type: Enum { Product, Service, Customer, Order } @required
    object_code: String @required
    activity_consumption: Map<String, Decimal>
    allocated_costs: Decimal @computed("sum(activity_consumption.values() * activity_rate)")
    total_cost: Decimal @computed("direct_costs + allocated_costs")
  }
} @standard("ABC")
```

---

## 3. 标准成本法Schema

**定义3（标准成本法Schema）**：

```text
Standard_Costing_Schema = (Standard_Cost, Standard_Cost_Variance,
                          Price_Variance, Quantity_Variance)
```

**形式化DSL定义**：

```dsl
schema StandardCosting {
  standard_costs: List<StandardCost> {
    product_code: String @required @unique
    material_cost: Decimal @required @range(0, null)
    labor_cost: Decimal @required @range(0, null)
    overhead_cost: Decimal @required @range(0, null)
    total_standard_cost: Decimal @computed("material_cost + labor_cost + overhead_cost")
  }

  cost_variance: CostVariance {
    product_code: String @required
    standard_cost: Decimal @required
    actual_cost: Decimal @required
    total_variance: Decimal @computed("actual_cost - standard_cost")
    price_variance: PriceVariance {
      material_price_variance: Decimal @computed("(actual_material_price - standard_material_price) * actual_quantity")
      labor_price_variance: Decimal @computed("(actual_labor_rate - standard_labor_rate) * actual_hours")
    }
    quantity_variance: QuantityVariance {
      material_quantity_variance: Decimal @computed("(actual_quantity - standard_quantity) * standard_price")
      labor_efficiency_variance: Decimal @computed("(actual_hours - standard_hours) * standard_rate")
    }
  }
} @standard("Standard Costing")
```

---

## 4. 实际成本法Schema

**定义4（实际成本法Schema）**：

```text
Actual_Costing_Schema = (Actual_Cost, Cost_Accumulation, Cost_Assignment)
```

**形式化DSL定义**：

```dsl
schema ActualCosting {
  actual_costs: List<ActualCost> {
    cost_id: String @required @unique
    cost_object_id: String @required
    cost_type: Enum { Material, Labor, Overhead } @required
    cost_amount: Decimal @required @range(0, null)
    cost_date: Date @required
  }

  cost_accumulation: CostAccumulation {
    accumulation_method: Enum { JobOrder, Process, Hybrid } @required
    accumulation_period: Date @required
    total_material_cost: Decimal @default(0)
    total_labor_cost: Decimal @default(0)
    total_overhead_cost: Decimal @default(0)
    total_cost: Decimal @computed("total_material_cost + total_labor_cost + total_overhead_cost")
  }

  cost_assignment: CostAssignment {
    assignment_method: Enum { Direct, Allocated } @required
    assigned_costs: List<AssignedCost> {
      cost_object_id: String @required
      assigned_amount: Decimal @required
      assignment_base: String @required
    }
  }
} @standard("Actual Costing")
```

---

## 5. 成本分配Schema

**定义5（成本分配Schema）**：

```text
Cost_Allocation_Schema = (Allocation_Base, Allocation_Method, Allocated_Cost)
```

**形式化DSL定义**：

```dsl
schema CostAllocation {
  allocation_bases: List<AllocationBase> {
    base_id: String @required @unique
    base_type: Enum { DirectLabor, MachineHours, SquareFeet, Units } @required
    base_amount: Decimal @required @range(0, null)
  }

  allocation_methods: List<AllocationMethod> {
    method_id: String @required @unique
    method_type: Enum { Direct, StepDown, Reciprocal } @required
    allocation_rules: Map<String, Decimal>
  }

  allocated_costs: List<AllocatedCost> {
    allocation_id: String @required @unique
    cost_center_from: String @required
    cost_center_to: String @required
    allocation_base_id: String @required
    allocation_amount: Decimal @required @range(0, null)
    allocation_rate: Decimal @computed("allocation_amount / allocation_base.base_amount")
  }
} @standard("Cost Allocation")
```

---

## 6. 类型系统

**定义6（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date,
               Enum, List, Map, Object, Optional}
```

---

## 7. 约束规则

**定义7（约束规则）**：

1. **唯一性约束**：`activity_id`、`product_code`、`cost_id`等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：`@range(min, max)`限制数值范围
4. **计算约束**：`@computed(expression)`计算字段值
5. **成本平衡约束**：分配成本总额等于待分配成本总额

---

## 8. 转换函数

**定义8（转换函数）**：

```text
转换函数集合 = {
  convert_abc_to_standard: Activity_Based_Costing → Standard_Costing,
  convert_standard_to_actual: Standard_Costing → Actual_Costing,
  convert_to_database: Cost_Accounting_Schema → PostgreSQL_Schema
}
```

---

## 9. 形式化定理

### 9.1 成本分配定理

**定理1（成本分配）**：
分配成本总额等于待分配成本总额：

```text
∑Allocated_Cost.allocation_amount = Total_Cost_to_Allocate
```

### 9.2 标准成本差异定理

**定理2（标准成本差异）**：
总差异等于价格差异加数量差异：

```text
Total_Variance = Price_Variance + Quantity_Variance
```

### 9.3 作业成本分配定理

**定理3（作业成本分配）**：
产品成本等于直接成本加分配的间接成本：

```text
Product_Cost = Direct_Cost + ∑(Activity_Consumption × Activity_Rate)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
