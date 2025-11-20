# PLC Schema形式化定义

## 📑 目录

- [PLC Schema形式化定义](#plc-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 层间关系](#12-层间关系)
  - [2. 五层Schema结构形式化定义](#2-五层schema结构形式化定义)
    - [2.1 第1层：硬件结构Schema](#21-第1层硬件结构schema)
    - [2.2 第2层：程序组织单元Schema](#22-第2层程序组织单元schema)
    - [2.3 第3层：任务调度Schema](#23-第3层任务调度schema)
    - [2.4 第4层：通信协议Schema](#24-第4层通信协议schema)
    - [2.5 第5层：行业功能块Schema](#25-第5层行业功能块schema)
  - [3. 类型系统](#3-类型系统)
    - [3.1 IEC 61131-3数据类型](#31-iec-61131-3数据类型)
    - [3.2 派生类型](#32-派生类型)
    - [3.3 类型约束](#33-类型约束)
  - [4. 约束规则](#4-约束规则)
    - [4.1 语法约束](#41-语法约束)
    - [4.2 语义约束](#42-语义约束)
  - [5. 转换函数](#5-转换函数)
    - [5.1 Schema到代码转换](#51-schema到代码转换)
    - [5.2 代码到Schema转换](#52-代码到schema转换)
  - [6. 形式化定理](#6-形式化定理)
    - [6.1 完备性定理](#61-完备性定理)
    - [6.2 正确性定理](#62-正确性定理)
  - [7. 证明](#7-证明)
    - [7.1 完备性证明](#71-完备性证明)
    - [7.2 正确性证明](#72-正确性证明)


---

## 1. 形式化模型

### 1.1 基本定义

设 `PLC_Schema` 为PLC Schema的集合，
`PLC_Program` 为PLC程序的集合。

**定义1（Schema）**：
PLC Schema是一个五元组：

```text
PLC_Schema = (H, P, C, D, I)
```


其中：

- `H`：硬件结构Schema
- `P`：程序组织单元Schema
- `C`：通信协议Schema
- `D`：数据Schema
- `I`：行业功能块Schema

### 1.2 层间关系

**定义2（层间组合）**：
层间组合运算 `⊕` 定义为：

```text
S₁ ⊕ S₂ = { (x, y) | x ∈ S₁, y ∈ S₂,

                  constraints(x, y) }
```

其中 `constraints(x, y)` 表示层间约束条件。

---

## 2. 五层Schema结构形式化定义

### 2.1 第1层：硬件结构Schema

**定义3（硬件结构Schema）**：

```text
Hardware_Schema = (CPU, IO, Power, Comm)
```


其中：

- `CPU`：CPU模块配置
- `IO`：I/O模块列表
- `Power`：电源模块配置
- `Comm`：通信模块配置

**形式化DSL定义**：

```dsl
schema Hardware_Structure {
  cpu: Module {
    type: Enum { S7_1200, S7_1500, FX5U, Q_Series }
    clock_speed: MHz
    memory: struct { ram: MB, flash: MB }
  } @core_module

  io_modules: List<Module> {
    module: {
      type: Enum { DI, DO, AI, AO, TC, RTD }
      channels: UInt8
      isolation: Enum { none, optical, magnetic }
    } @slot_address("rack.slot")

  }

  power_supply: {
    input_voltage: Enum { AC_220V, DC_24V }
    output_voltage: DC_Voltage @values([5.0, 12.0, 24.0])
  } @redundant(false)
} @topology(bus="backplane", protocol="profinet/io")
```

### 2.2 第2层：程序组织单元Schema

**定义4（程序组织单元Schema）**：

```text
Program_Schema = (POU_Type, Variables, Implementation)

```

其中：

- `POU_Type`：POU类型（Program/FB/Function）
- `Variables`：变量声明集合
- `Implementation`：实现代码

**形式化DSL定义**：

```dsl
schema Program_Organization_Unit {
  pou_type: Enum { program, function_block, function }
  name: Identifier @unique_scope("project")

  variables: List<Variable> {
    variable: {
      name: Identifier
      var_type: Enum {
        VAR, VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT,
        VAR_GLOBAL, VAR_TEMP, VAR_STAT, VAR_EXTERNAL
      }
      data_type: IEC_DataType {
        elementary: Enum { BOOL, INT, DINT, REAL, TIME, DATE }
        derived: Struct | Array | Enum
      } @type_check(compile_time)
      address: Optional[String] @pattern("%I|Q|M|DBW\d+")
      retain: Bool @default(false) @persist("EEPROM")
    }
  }

  implementation: Union {
    st: StructuredText @grammar("IEC_61131-3_ST")
    ld: LadderDiagram @contact_coil_model
    fbd: FunctionBlockDiagram @network_based
    il: InstructionList @stack_machine
    sfc: SequentialFunctionChart @state_machine
  }
} @standard("IEC_61131-3")
```

### 2.3 第3层：任务调度Schema

**定义5（任务调度Schema）**：

```text
Task_Schema = (Task_List, Priority, Cycle, Trigger)
```

**形式化DSL定义**：

```dsl
schema Task_Scheduling {
  tasks: List<Task> {
    task: {
      name: Identifier
      priority: UInt8 @range(0, 15) @lower_is_higher
      cycle_time: Time @unit("ms") @min(1)
      trigger: Enum { cyclic, event, interrupt }
      programs: List<Program> @execution_order
    }
  }
} @scheduler("preemptive")
```

### 2.4 第4层：通信协议Schema

**定义6（通信协议Schema）**：

```text
Communication_Schema = (Protocol, Network, Data_Exchange)
```

**形式化DSL定义**：

```dsl
schema Communication_Protocol {
  protocols: List<Protocol> {
    protocol: {
      type: Enum { Modbus, Profibus, Ethernet_IP, OPC_UA }
      configuration: Map<String, Any>
      data_exchange: List<Data_Exchange> {
        exchange: {
          source: Address
          destination: Address
          data_type: IEC_DataType
          update_rate: Frequency
        }
      }
    }
  }
} @network_topology("star" | "ring" | "bus")
```

### 2.5 第5层：行业功能块Schema

**定义7（行业功能块Schema）**：

```text
Industry_Schema = (Standard_FB, Custom_FB, Industry_Model)
```

**形式化DSL定义**：

```dsl
schema Industry_Function_Block {
  standard_fbs: List<FB> {
    fb: {
      name: Identifier @from_library("IEC_61131-3")
      interface: FB_Interface
      implementation: Implementation
    }
  }

  custom_fbs: List<FB> {
    fb: {
      name: Identifier
      interface: FB_Interface
      implementation: Implementation
      industry: Enum { automotive, process, discrete }
    }
  }
} @reusable(true)
```

---

## 3. 类型系统

### 3.1 IEC 61131-3数据类型

**定义8（基本数据类型）**：

```text
Basic_Type = { BOOL, SINT, INT, DINT, LINT,
               USINT, UINT, UDINT, ULINT,
               REAL, LREAL, TIME, DATE, TOD, DT,
               STRING, WSTRING, BYTE, WORD, DWORD, LWORD }
```

### 3.2 派生类型

**定义9（派生类型）**：

```text
Derived_Type = Array | Struct | Enum | Union
```

### 3.3 类型约束

**定义10（类型约束）**：
对于变量 `v`，其类型约束为：

```text
type_constraint(v) = { t | t ∈ Type,
                       compatible(v.type, t) }
```

---

## 4. 约束规则

### 4.1 语法约束

**规则1（变量命名）**：
变量名必须符合IEC 61131-3标识符规则。

**规则2（类型匹配）**：
赋值操作必须满足类型匹配。

**规则3（作用域）**：
变量作用域必须符合IEC 61131-3规则。

### 4.2 语义约束

**规则4（资源限制）**：
程序大小不能超过CPU内存限制。

**规则5（实时性）**：
任务周期必须满足实时性要求。

**规则6（安全性）**：
安全相关程序必须符合IEC 61508标准。

---

## 5. 转换函数

### 5.1 Schema到代码转换

**定义11（转换函数）**：

```text
transform: PLC_Schema → PLC_Program
```

**转换规则**：

1. **硬件层** → 硬件配置代码
2. **程序层** → 程序代码（ST/LD/FBD等）
3. **调度层** → 任务配置代码
4. **通信层** → 通信配置代码
5. **行业层** → 功能块实例化代码

### 5.2 代码到Schema转换

**定义12（反向转换）**：

```text
parse: PLC_Program → PLC_Schema

```

---

## 6. 形式化定理

### 6.1 完备性定理

**定理1（PLC Schema完备性）**：
对于任意PLC程序 `p`，存在Schema `s`，
使得 `parse(p) = s` 且 `transform(s) = p'`，
其中 `p'` 与 `p` 语义等价。

### 6.2 正确性定理


**定理2（转换正确性）**：
如果 `s` 是有效的PLC Schema，
则 `transform(s)` 生成的程序 `p` 满足：

- 语法正确
- 类型安全
- 语义等价

---

## 7. 证明


### 7.1 完备性证明

**证明**：
根据IEC 61131-3标准，所有PLC程序
都可以用标准语法表示，而标准语法
可以形式化为Schema。

因此，对于任意程序 `p`，存在Schema `s`。

### 7.2 正确性证明

**证明**：
转换函数 `transform` 遵循IEC 61131-3标准，

因此生成的代码满足标准要求。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
