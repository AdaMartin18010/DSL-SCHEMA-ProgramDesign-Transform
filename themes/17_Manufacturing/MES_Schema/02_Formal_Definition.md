# MES Schema形式化定义

## 📑 目录

- [MES Schema形式化定义](#mes-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 生产订单Schema](#2-生产订单schema)
  - [3. 生产执行Schema](#3-生产执行schema)
  - [4. 质量追溯Schema](#4-质量追溯schema)
  - [5. 设备管理Schema](#5-设备管理schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 生产订单完整性定理](#91-生产订单完整性定理)
    - [9.2 质量追溯一致性定理](#92-质量追溯一致性定理)

---

## 1. 形式化模型

**定义1（MES Schema）**：
MES Schema是一个四元组：

```text
MES_Schema = (Production_Order_Schema, Production_Execution_Schema,
             Quality_Traceability_Schema, Equipment_Management_Schema)
```

其中：

- `Production_Order_Schema`：生产订单Schema
- `Production_Execution_Schema`：生产执行Schema
- `Quality_Traceability_Schema`：质量追溯Schema
- `Equipment_Management_Schema`：设备管理Schema

---

## 2. 生产订单Schema

**定义2（生产订单Schema）**：

```text
Production_Order_Schema = (Order_Info, Order_Status, Order_Resources)
```

**形式化DSL定义**：

```dsl
schema ProductionOrder {
  order_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  order_number: String @max_length(50) @required @unique
  product_id: String @pattern("^[A-Z0-9]{20}$") @required
  product_name: String @max_length(200) @required

  order_info: {
    order_quantity: Integer @range(1, 999999) @required
    unit: String @max_length(20) @default("pieces")
    planned_start_date: DateTime @required
    planned_end_date: DateTime @required
    delivery_date: DateTime @required
    priority: Enum { Low, Normal, High, Urgent } @default("Normal")
    order_type: Enum { MakeToStock, MakeToOrder, EngineerToOrder } @required
  } @required

  order_status: {
    status: Enum { Planned, Released, InProgress, Completed, Cancelled } @required
    progress_percentage: Decimal @precision(5,2) @range(0.0, 100.0) @required
    actual_start_date: DateTime
    actual_end_date: DateTime
    completed_quantity: Integer @range(0, 999999) @default(0)
    rejected_quantity: Integer @range(0, 999999) @default(0)
  } @required

  order_resources: {
    work_centers: List<String> @required
    equipment_list: List<String>
    material_list: List<MaterialRequirement> {
      material_id: String @required
      material_name: String @required
      required_quantity: Decimal @precision(10,2) @required
      unit: String @required
      issued_quantity: Decimal @precision(10,2) @default(0)
    } @required
    labor_requirements: List<LaborRequirement> {
      skill_level: String @required
      required_hours: Decimal @precision(8,2) @required
      assigned_personnel: List<String>
    }
  } @required
} @standard("ISA-95")
```

---

## 3. 生产执行Schema

**定义3（生产执行Schema）**：

```text
Production_Execution_Schema = (Process_Info, Execution_Status, Resource_Usage)
```

**形式化DSL定义**：

```dsl
schema ProductionExecution {
  execution_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  order_id: String @pattern("^[A-Z0-9]{20}$") @required
  work_order_id: String @max_length(50) @required

  process_info: {
    process_steps: List<ProcessStep> {
      step_number: Integer @required
      step_name: String @max_length(100) @required
      work_center: String @required
      equipment_id: String
      operation_code: String @max_length(50)
      standard_time: Decimal @precision(8,2) @unit("minutes")
      setup_time: Decimal @precision(8,2) @unit("minutes")
    } @required
    routing: List<RoutingStep> {
      from_step: Integer @required
      to_step: Integer @required
      condition: String @max_length(200)
    }
  } @required

  execution_status: {
    current_step: Integer @required
    status: Enum { NotStarted, InProgress, Completed, Paused, Cancelled } @required
    start_time: DateTime
    end_time: DateTime
    operator: String @max_length(100)
    shift: String @max_length(50)
  } @required

  resource_usage: {
    material_consumption: List<MaterialConsumption> {
      material_id: String @required
      consumed_quantity: Decimal @precision(10,2) @required
      unit: String @required
      consumption_time: DateTime @required
    }
    equipment_usage: List<EquipmentUsage> {
      equipment_id: String @required
      usage_start_time: DateTime @required
      usage_end_time: DateTime
      utilization_rate: Decimal @precision(5,2) @unit("%")
    }
    energy_consumption: {
      electricity: Decimal @precision(10,2) @unit("kWh")
      gas: Decimal @precision(10,2) @unit("m³")
      water: Decimal @precision(10,2) @unit("L")
    }
  } @required
} @standard("ISA-95")
```

---

## 4. 质量追溯Schema

**定义4（质量追溯Schema）**：

```text
Quality_Traceability_Schema = (Quality_Inspection, Traceability_Chain, Quality_Report)
```

**形式化DSL定义**：

```dsl
schema QualityTraceability {
  traceability_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  order_id: String @pattern("^[A-Z0-9]{20}$") @required
  product_id: String @pattern("^[A-Z0-9]{20}$") @required

  quality_inspection: {
    inspections: List<Inspection> {
      inspection_id: String @required @unique
      inspection_type: Enum { Incoming, InProcess, Final, Return } @required
      inspection_item: String @max_length(200) @required
      inspection_standard: String @max_length(200)
      inspection_result: Enum { Pass, Fail, Conditional } @required
      inspection_value: Decimal @precision(10,2)
      inspection_unit: String @max_length(20)
      inspection_time: DateTime @required
      inspector: String @max_length(100) @required
      inspection_notes: String @max_length(500)
    } @required
  } @required

  traceability_chain: {
    material_traceability: List<MaterialTrace> {
      material_id: String @required
      material_batch: String @max_length(50)
      supplier: String @max_length(200)
      receipt_date: DateTime
    }
    process_traceability: List<ProcessTrace> {
      process_step: Integer @required
      equipment_id: String
      operator: String @max_length(100)
      process_time: DateTime @required
      process_parameters: Map<String, Any>
    }
    product_traceability: {
      production_batch: String @max_length(50) @required
      serial_numbers: List<String>
      production_date: DateTime @required
      production_line: String @max_length(50)
    }
  } @required

  quality_report: {
    report_id: String @required @unique
    report_type: Enum { Daily, Weekly, Monthly, Incident } @required
    report_date: DateTime @required
    pass_rate: Decimal @precision(5,2) @unit("%") @required
    defect_rate: Decimal @precision(5,2) @unit("%") @required
    defect_analysis: List<DefectAnalysis> {
      defect_type: String @required
      defect_count: Integer @required
      defect_rate: Decimal @precision(5,2) @unit("%")
      root_cause: String @max_length(500)
      corrective_action: String @max_length(500)
    }
  }
} @standard("ISO 22400")
```

---

## 5. 设备管理Schema

**定义5（设备管理Schema）**：

```text
Equipment_Management_Schema = (Equipment_Info, Equipment_Status, Maintenance_Management)
```

**形式化DSL定义**：

```dsl
schema EquipmentManagement {
  equipment_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  equipment_code: String @max_length(50) @required @unique
  equipment_name: String @max_length(200) @required

  equipment_info: {
    equipment_type: String @max_length(100) @required
    manufacturer: String @max_length(200) @required
    model: String @max_length(100)
    serial_number: String @max_length(100)
    installation_date: Date @format("YYYY-MM-DD")
    work_center: String @max_length(50)
    capacity: Decimal @precision(10,2)
    capacity_unit: String @max_length(20)
  } @required

  equipment_status: {
    operational_status: Enum { Running, Idle, Maintenance, Breakdown, Setup } @required
    availability: Decimal @precision(5,2) @unit("%") @range(0.0, 100.0) @required
    utilization: Decimal @precision(5,2) @unit("%") @range(0.0, 100.0) @required
    performance: Decimal @precision(5,2) @unit("%") @range(0.0, 100.0)
    quality_rate: Decimal @precision(5,2) @unit("%") @range(0.0, 100.0)
    oee: Decimal @precision(5,2) @unit("%") @range(0.0, 100.0)
    status_time: DateTime @required
  } @required

  maintenance_management: {
    maintenance_plans: List<MaintenancePlan> {
      plan_id: String @required @unique
      maintenance_type: Enum { Preventive, Corrective, Predictive } @required
      maintenance_interval: Integer @unit("days")
      last_maintenance_date: Date @format("YYYY-MM-DD")
      next_maintenance_date: Date @format("YYYY-MM-DD")
      maintenance_duration: Decimal @precision(8,2) @unit("hours")
    }
    maintenance_history: List<MaintenanceRecord> {
      record_id: String @required @unique
      maintenance_date: DateTime @required
      maintenance_type: Enum { Preventive, Corrective, Predictive } @required
      maintenance_description: String @max_length(500)
      maintenance_cost: Decimal @precision(10,2)
      maintenance_personnel: String @max_length(100)
      parts_replaced: List<String>
    }
  } @required
} @standard("ISO 22400")
```

---

## 6. 类型系统

**定义6（MES类型系统）**：

```text
MES_Type_System = (Order_Types, Execution_Types, Quality_Types, Equipment_Types)
```

**订单类型**：

- **OrderStatus**：订单状态枚举
- **OrderType**：订单类型枚举
- **Priority**：优先级枚举

**执行类型**：

- **ExecutionStatus**：执行状态枚举
- **ProcessStep**：工序步骤类型
- **ResourceUsage**：资源使用类型

**质量类型**：

- **InspectionResult**：检测结果枚举
- **DefectType**：缺陷类型枚举
- **TraceabilityType**：追溯类型枚举

**设备类型**：

- **OperationalStatus**：运行状态枚举
- **MaintenanceType**：维护类型枚举
- **OEE**：设备综合效率类型

---

## 7. 约束规则

**规则1（生产订单数量约束）**：

```text
∀ po ∈ Production_Order_Schema:
  po.order_status.completed_quantity + po.order_status.rejected_quantity ≤ po.order_info.order_quantity
  po.order_status.progress_percentage =
    (po.order_status.completed_quantity / po.order_info.order_quantity) × 100
```

**规则2（质量追溯完整性约束）**：

```text
∀ qt ∈ Quality_Traceability_Schema:
  Complete(qt) ↔
    ∃ qt.quality_inspection.inspections ∧
    ∃ qt.traceability_chain.material_traceability ∧
    ∃ qt.traceability_chain.process_traceability
```

**规则3（设备OEE计算约束）**：

```text
∀ em ∈ Equipment_Management_Schema:
  em.equipment_status.oee =
    em.equipment_status.availability ×
    em.equipment_status.utilization ×
    em.equipment_status.performance / 10000
```

---

## 8. 转换函数

**函数1（ERP到MES转换）**：

```text
Convert_ERP_to_MES: ERP_Order_Schema → MES_Production_Order_Schema
Convert_ERP_to_MES(erp_order) = {
  order_id: erp_order.order_id,
  order_number: erp_order.order_number,
  product_id: erp_order.product_id,
  order_info: {
    order_quantity: erp_order.quantity,
    planned_start_date: erp_order.start_date,
    planned_end_date: erp_order.end_date,
    delivery_date: erp_order.delivery_date
  }
}
```

**函数2（MES到数据库转换）**：

```text
Convert_MES_to_DB: MES_Schema → Database_Schema
Convert_MES_to_DB(mes) = {
  ProductionOrders: map(Convert_Order_to_DB, mes.production_orders),
  ProductionExecutions: map(Convert_Execution_to_DB, mes.production_executions),
  QualityRecords: map(Convert_Quality_to_DB, mes.quality_records),
  EquipmentRecords: map(Convert_Equipment_to_DB, mes.equipment_records)
}
```

---

## 9. 形式化定理

### 9.1 生产订单完整性定理

**定理1（生产订单完整性）**：

对于任意生产订单PO，如果PO的所有必需信息都存在，
则PO是完整的：

```text
∀ po ∈ Production_Order_Schema:
  Complete(po) ↔
    ∃ po.order_info ∧ ∃ po.order_status ∧ ∃ po.order_resources
```

**证明**：

根据ISA-95标准，生产订单的完整性定义为所有
必需信息都存在。因此，如果所有必需信息都存在，
则生产订单是完整的。

### 9.2 质量追溯一致性定理

**定理2（质量追溯一致性）**：

对于任意质量追溯记录QT，如果QT的所有追溯链
都指向同一产品，则QT是一致的：

```text
∀ qt ∈ Quality_Traceability_Schema:
  Consistent(qt) ↔
    ∀ trace ∈ qt.traceability_chain.material_traceability ∪
               qt.traceability_chain.process_traceability:
      trace.product_id = qt.product_id
```

**证明**：

根据ISO 22400标准，质量追溯的一致性定义为所有
追溯链都指向同一产品。因此，如果所有追溯链都
指向同一产品，则质量追溯是一致的。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
