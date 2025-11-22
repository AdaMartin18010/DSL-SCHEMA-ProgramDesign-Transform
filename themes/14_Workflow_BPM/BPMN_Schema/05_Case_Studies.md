# BPMN Schema实践案例

## 📑 目录

- [BPMN Schema实践案例](#bpmn-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：订单处理流程](#2-案例1订单处理流程)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：审批工作流](#3-案例2审批工作流)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：并行任务处理](#4-案例3并行任务处理)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：BPMN到BPEL转换](#5-案例4bpmn到bpel转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：BPMN数据存储与分析系统](#6-案例5bpmn数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供BPMN Schema在实际应用中的实践案例。

---

## 2. 案例1：订单处理流程

### 2.1 场景描述

**应用场景**：
电商订单处理流程，包括订单创建、支付、发货、确认收货等步骤。

### 2.2 Schema定义

**订单处理流程BPMN Schema**：

```dsl
schema OrderProcess {
  id: String @value("order_process")
  name: String @value("订单处理流程")

  start_event: StartEvent {
    id: String @value("start_order")
    name: String @value("订单创建")
  }

  user_task_payment: UserTask {
    id: String @value("payment_task")
    name: String @value("支付处理")
    assignee: String @value("payment_service")
    due_date: Duration @value("PT24H")
  }

  exclusive_gateway_payment: ExclusiveGateway {
    id: String @value("payment_gateway")
    name: String @value("支付结果判断")
    default_flow: String @value("payment_failed")
  }

  service_task_ship: ServiceTask {
    id: String @value("ship_task")
    name: String @value("发货处理")
    implementation: String @value("##WebService")
    operation_ref: String @value("shipOrder")
  }

  user_task_confirm: UserTask {
    id: String @value("confirm_task")
    name: String @value("确认收货")
    candidate_groups: List<String> @value(["customer"])
  }

  end_event_completed: EndEvent {
    id: String @value("end_completed")
    name: String @value("订单完成")
  }

  end_event_cancelled: EndEvent {
    id: String @value("end_cancelled")
    name: String @value("订单取消")
  }
} @standard("BPMN_2.0")
```

---

## 3. 案例2：审批工作流

### 3.1 场景描述

**应用场景**：
多级审批工作流，包括部门经理审批、财务审批、总经理审批。

### 3.2 Schema定义

**审批工作流BPMN Schema**：

```dsl
schema ApprovalWorkflow {
  id: String @value("approval_workflow")
  name: String @value("审批工作流")

  start_event: StartEvent {
    id: String @value("start_approval")
    name: String @value("提交审批")
  }

  user_task_dept_manager: UserTask {
    id: String @value("dept_manager_task")
    name: String @value("部门经理审批")
    candidate_groups: List<String> @value(["dept_manager"])
    due_date: Duration @value("PT48H")
  }

  exclusive_gateway_dept: ExclusiveGateway {
    id: String @value("dept_gateway")
    name: String @value("部门审批结果")
  }

  user_task_finance: UserTask {
    id: String @value("finance_task")
    name: String @value("财务审批")
    candidate_groups: List<String> @value(["finance"])
    due_date: Duration @value("PT48H")
  }

  exclusive_gateway_finance: ExclusiveGateway {
    id: String @value("finance_gateway")
    name: String @value("财务审批结果")
  }

  user_task_general_manager: UserTask {
    id: String @value("gm_task")
    name: String @value("总经理审批")
    candidate_users: List<String> @value(["general_manager"])
    due_date: Duration @value("PT72H")
  }

  end_event_approved: EndEvent {
    id: String @value("end_approved")
    name: String @value("审批通过")
  }

  end_event_rejected: EndEvent {
    id: String @value("end_rejected")
    name: String @value("审批拒绝")
  }
} @standard("BPMN_2.0")
```

---

## 4. 案例3：并行任务处理

### 4.1 场景描述

**应用场景**：
订单处理中并行执行库存检查、信用检查和价格计算。

### 4.2 Schema定义

**并行任务处理BPMN Schema**：

```dsl
schema ParallelTaskProcess {
  id: String @value("parallel_process")
  name: String @value("并行任务处理")

  start_event: StartEvent {
    id: String @value("start_parallel")
  }

  parallel_gateway_split: ParallelGateway {
    id: String @value("split_gateway")
    name: String @value("并行分支")
  }

  service_task_inventory: ServiceTask {
    id: String @value("inventory_task")
    name: String @value("库存检查")
    implementation: String @value("##JavaClass")
  }

  service_task_credit: ServiceTask {
    id: String @value("credit_task")
    name: String @value("信用检查")
    implementation: String @value("##JavaClass")
  }

  service_task_price: ServiceTask {
    id: String @value("price_task")
    name: String @value("价格计算")
    implementation: String @value("##JavaClass")
  }

  parallel_gateway_join: ParallelGateway {
    id: String @value("join_gateway")
    name: String @value("并行汇聚")
  }

  end_event: EndEvent {
    id: String @value("end_parallel")
  }
} @standard("BPMN_2.0")
```

---

## 5. 案例4：BPMN到BPEL转换

### 5.1 场景描述

**应用场景**：
将BPMN流程定义转换为BPEL可执行流程。

### 5.2 实现代码

详见 `04_Transformation.md` 第2章。

---

## 6. 案例5：BPMN数据存储与分析系统

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储BPMN流程定义和实例数据，支持流程性能分析和优化。

### 6.2 实现代码

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
