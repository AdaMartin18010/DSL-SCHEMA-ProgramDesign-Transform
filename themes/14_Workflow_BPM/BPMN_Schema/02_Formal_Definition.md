# BPMN Schema形式化定义

## 📑 目录

- [BPMN Schema形式化定义](#bpmn-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 流程定义Schema](#2-流程定义schema)
  - [3. 任务Schema](#3-任务schema)
  - [4. 网关Schema](#4-网关schema)
  - [5. 事件Schema](#5-事件schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)

---

## 1. 形式化模型

**定义1（BPMN Schema）**：
BPMN Schema是一个四元组：

```text
BPMN_Schema = (Process_Definition, Task, Gateway, Event)
```

其中：

- `Process_Definition`：流程定义Schema
- `Task`：任务Schema
- `Gateway`：网关Schema
- `Event`：事件Schema

---

## 2. 流程定义Schema

**定义2（流程定义Schema）**：

```text
Process_Definition_Schema = (ID, Name, Participants, Variables, Elements)
```

**形式化DSL定义**：

```dsl
schema ProcessDefinition {
  id: String @required @unique
  name: String @required
  version: String @default("1.0")

  participants: List<Participant> {
    id: String @required
    name: String @required
    type: Enum { Process, Lane, Pool }
  }

  variables: Map<String, Variable> {
    name: String @required
    type: DataType @required
    default_value: Optional<Any>
  }

  elements: List<FlowElement> {
    id: String @required @unique
    name: Optional<String>
    type: FlowElementType @required
  }

  start_event: StartEvent @required
  end_events: List<EndEvent] @required
} @standard("BPMN_2.0")
```

---

## 3. 任务Schema

**定义3（任务Schema）**：

```text
Task_Schema = (User_Task | Service_Task | Script_Task | Business_Rule_Task)
```

**形式化DSL定义**：

```dsl
schema Task {
  id: String @required
  name: String @required
  type: Enum { UserTask, ServiceTask, ScriptTask, BusinessRuleTask } @required

  // 用户任务
  user_task: Optional<UserTask] {
    assignee: Optional<String>
    candidate_users: List<String>
    candidate_groups: List<String>
    due_date: Optional<DateTime>
    priority: Optional<Int] @range(0, 100)
  }

  // 服务任务
  service_task: Optional<ServiceTask] {
    implementation: String @required
    operation_ref: Optional<String]
    input_variables: Map<String, String>
    output_variables: Map<String, String>
  }

  // 脚本任务
  script_task: Optional<ScriptTask] {
    script_format: String @required
    script: String @required
  }

  // 业务规则任务
  business_rule_task: Optional<BusinessRuleTask] {
    decision_ref: Optional<String]
    input_variables: Map<String, String>
    output_variables: Map<String, String]
  }

  incoming_flows: List<String]
  outgoing_flows: List<String]
} @standard("BPMN_2.0")
```

---

## 4. 网关Schema

**定义4（网关Schema）**：

```text
Gateway_Schema = (Exclusive_Gateway | Parallel_Gateway | Inclusive_Gateway | Event_Gateway)
```

**形式化DSL定义**：

```dsl
schema Gateway {
  id: String @required
  name: Optional<String>
  type: Enum { Exclusive, Parallel, Inclusive, Event } @required

  // 排他网关
  exclusive_gateway: Optional<ExclusiveGateway] {
    default_flow: Optional<String]
    sequence_flows: List<SequenceFlow] {
      id: String @required
      condition_expression: Optional<String]
      target_ref: String @required
    }
  }

  // 并行网关
  parallel_gateway: Optional<ParallelGateway] {
    sequence_flows: List<SequenceFlow] @required
  }

  // 包容网关
  inclusive_gateway: Optional<InclusiveGateway] {
    default_flow: Optional<String]
    sequence_flows: List<SequenceFlow] {
      id: String @required
      condition_expression: Optional<String]
      target_ref: String @required
    }
  }

  incoming_flows: List<String] @required
  outgoing_flows: List<String] @required
} @standard("BPMN_2.0")
```

---

## 5. 事件Schema

**定义5（事件Schema）**：

```text
Event_Schema = (Start_Event | End_Event | Intermediate_Event | Boundary_Event)
```

**形式化DSL定义**：

```dsl
schema Event {
  id: String @required
  name: Optional<String>
  type: Enum { Start, End, Intermediate, Boundary } @required

  // 开始事件
  start_event: Optional<StartEvent] {
    trigger: Enum { None, Message, Timer, Signal, Error }
    event_definitions: List<EventDefinition]
  }

  // 结束事件
  end_event: Optional<EndEvent] {
    result: Enum { None, Message, Signal, Error, Terminate }
    event_definitions: List<EventDefinition]
  }

  // 中间事件
  intermediate_event: Optional<IntermediateEvent] {
    trigger: Enum { Message, Timer, Signal, Error, Escalation }
    event_definitions: List<EventDefinition]
  }

  // 边界事件
  boundary_event: Optional<BoundaryEvent] {
    attached_to_ref: String @required
    cancel_activity: Boolean @default(true)
    trigger: Enum { Message, Timer, Signal, Error, Escalation }
    event_definitions: List<EventDefinition]
  }

  incoming_flows: List<String]
  outgoing_flows: List<String]
} @standard("BPMN_2.0")
```

---

## 6. 类型系统

**定义6（BPMN数据类型）**：

```text
BPMN_Data_Type = Process_Definition | Task | Gateway | Event | Sequence_Flow | Data_Object
```

**基本类型定义**：

```dsl
type SequenceFlow {
  id: String @required
  source_ref: String @required
  target_ref: String @required
  condition_expression: Optional<String>
}

type DataObject {
  id: String @required
  name: Optional<String>
  data_state: Optional<String>
  item_subject_ref: Optional<String]
}

type DataType {
  name: String @required
  structure_ref: Optional<String>
  is_collection: Boolean @default(false)
}
```

---

## 7. 约束规则

**约束1（流程完整性）**：

```text
∀ process ∈ Process_Definition:
  has_start_event(process)
  ∧ has_end_event(process)
  ∧ all_elements_connected(process)
```

**约束2（网关平衡）**：

```text
∀ gateway ∈ Gateway:
  count_incoming_flows(gateway) ≥ 1
  ∧ count_outgoing_flows(gateway) ≥ 1
  ∧ (gateway.type = Parallel → all_outgoing_executed(gateway))
```

**约束3（事件有效性）**：

```text
∀ event ∈ Event:
  (event.type = Start → count_incoming_flows(event) = 0)
  ∧ (event.type = End → count_outgoing_flows(event) = 0)
```

---

## 8. 转换函数

**函数1（BPMN到BPEL转换）**：

```text
convert_bpmn_to_bpel: BPMN_Process → BPEL_Process
```

**函数2（BPMN到XPDL转换）**：

```text
convert_bpmn_to_xpdl: BPMN_Process → XPDL_Process
```

**函数3（流程验证）**：

```text
validate_process: BPMN_Process → ValidationResult
```

---

## 9. 形式化定理

### 9.1 流程可达性定理

**定理1（流程可达性）**：

```text
∀ process ∈ BPMN_Process:
  start_event ∈ process.elements
  → ∃ path: start_event → end_event
```

### 9.2 转换正确性定理

**定理2（BPMN到BPEL转换正确性）**：

```text
∀ bpmn_process ∈ BPMN_Process:
  bpel_process = convert_bpmn_to_bpel(bpmn_process)
  → behavioral_equivalent(bpmn_process, bpel_process)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
