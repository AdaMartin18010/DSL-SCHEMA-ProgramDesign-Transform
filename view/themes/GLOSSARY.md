# 术语表和缩写表

## 📑 目录

- [术语表和缩写表](#术语表和缩写表)
  - [📑 目录](#-目录)
  - [1. 核心术语](#1-核心术语)
    - [1.1 Schema相关](#11-schema相关)
    - [1.2 转换相关](#12-转换相关)
  - [2. 标准组织缩写](#2-标准组织缩写)
  - [3. 技术术语](#3-技术术语)
    - [3.1 工业自动化](#31-工业自动化)
    - [3.2 物联网](#32-物联网)
    - [3.3 知识图谱](#33-知识图谱)
  - [4. 协议和标准缩写](#4-协议和标准缩写)
    - [4.1 通信协议](#41-通信协议)
    - [4.2 标准编号](#42-标准编号)
  - [5. 技术概念](#5-技术概念)
    - [5.1 形式化方法](#51-形式化方法)
    - [5.2 信息论](#52-信息论)
    - [5.3 形式语言理论](#53-形式语言理论)
    - [5.4 数字孪生](#54-数字孪生)
  - [6. 数学符号](#6-数学符号)
    - [6.1 集合运算](#61-集合运算)
    - [6.2 函数和映射](#62-函数和映射)
    - [6.3 逻辑运算](#63-逻辑运算)
  - [7. 文档类型缩写](#7-文档类型缩写)
  - [8. 相关文档](#8-相关文档)

---

## 1. 核心术语

### 1.1 Schema相关

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| Schema | Schema | 描述系统结构、行为、约束的形式化规范 | [项目总览](./README.md) |
| DSL Schema | Domain-Specific Language Schema | 领域特定语言的Schema定义 | [DSL理论](./05_DSL_Theory/README.md) |
| 物理Schema | Physical Schema | 描述物理设备特性的Schema | [物理设备](./03_Physical_Device/README.md) |
| 数字孪生Schema | Digital Twin Schema | 数字孪生系统的Schema定义 | [数字孪生](./03_Physical_Device/Digital_Twin/README.md) |
| 知识图谱Schema | Knowledge Graph Schema | 知识图谱的Schema定义 | [知识图谱](./05_DSL_Theory/Knowledge_Graph/README.md) |

### 1.2 转换相关

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| Schema转换 | Schema Transformation | 将一种Schema转换为另一种Schema的过程 | [转换体系](./README.md#3-文档体系) |
| 形式化转换 | Formal Transformation | 基于数学形式化定义的转换 | [形式化定义](./README.md#32-文档结构) |
| 类型映射 | Type Mapping | 数据类型之间的映射关系 | [编程转换](./04_Programming_Conversion/README.md) |
| 语义等价 | Semantic Equivalence | 转换前后语义等价性 | [形式语言理论](./05_DSL_Theory/Formal_Language_Theory/README.md) |

---

## 2. 标准组织缩写

| 缩写 | 全称 | 中文名称 | 相关标准 |
|------|------|----------|----------|
| IEC | International Electrotechnical Commission | 国际电工委员会 | [IEC 61131-3](./01_Industrial_Automation/PLC_Schema/03_Standards.md#21-iec-61131-3), [IEC 63278](./03_Physical_Device/Digital_Twin/03_Standards.md#22-iec-63278) |
| ISO | International Organization for Standardization | 国际标准化组织 | [ISO 11898](./01_Industrial_Automation/CAN_Schema/03_Standards.md), [ISO/IEC 23247](./03_Physical_Device/Digital_Twin/03_Standards.md#21-isoiec-23247) |
| W3C | World Wide Web Consortium | 万维网联盟 | [W3C RDF](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#21-w3c-rdf), [W3C OWL](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#22-w3c-owl) |
| GB/T | 国家标准/推荐性标准 | 中国国家标准 | [GB/T 33008.1-2016](./01_Industrial_Automation/PLC_Schema/03_Standards.md#32-gbt-330081-2016), [GB/T 41479-2022](./03_Physical_Device/Digital_Twin/03_Standards.md#31-gbt-41479-2022) |
| IEEE | Institute of Electrical and Electronics Engineers | 电气和电子工程师协会 | [IEEE 802.11](./02_IoT_Schema/Communication_Schema/03_Standards.md), [IEEE 802.15.4](./02_IoT_Schema/Communication_Schema/03_Standards.md) |

---

## 3. 技术术语

### 3.1 工业自动化

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| PLC | Programmable Logic Controller | 可编程逻辑控制器 | [PLC Schema](./01_Industrial_Automation/PLC_Schema/README.md) |
| CAN | Controller Area Network | 控制器局域网 | [CAN Schema](./01_Industrial_Automation/CAN_Schema/README.md) |
| POU | Program Organization Unit | 程序组织单元 | [PLC Schema形式化定义](./01_Industrial_Automation/PLC_Schema/02_Formal_Definition.md) |
| FB | Function Block | 功能块 | [PLC Schema形式化定义](./01_Industrial_Automation/PLC_Schema/02_Formal_Definition.md) |

### 3.2 物联网

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| IoT | Internet of Things | 物联网 | [IoT Schema](./02_IoT_Schema/README.md) |
| MQTT | Message Queuing Telemetry Transport | 消息队列遥测传输协议 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |
| CoAP | Constrained Application Protocol | 受限应用协议 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |
| OPC UA | OPC Unified Architecture | OPC统一架构 | [通信Schema标准](./02_IoT_Schema/Communication_Schema/03_Standards.md) |

### 3.3 知识图谱

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| RDF | Resource Description Framework | 资源描述框架 | [知识图谱标准](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#21-w3c-rdf) |
| OWL | Web Ontology Language | Web本体语言 | [知识图谱标准](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#22-w3c-owl) |
| JSON-LD | JSON for Linking Data | JSON链接数据 | [知识图谱标准](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#32-json-ld) |
| SPARQL | SPARQL Protocol and RDF Query Language | SPARQL协议和RDF查询语言 | [知识图谱转换](./05_DSL_Theory/Knowledge_Graph/04_Transformation.md) |

---

## 4. 协议和标准缩写

### 4.1 通信协议

| 缩写 | 全称 | 中文名称 | 相关文档 |
|------|------|----------|----------|
| CAN | Controller Area Network | 控制器局域网 | [CAN Schema](./01_Industrial_Automation/CAN_Schema/README.md) |
| Modbus | Modbus Protocol | Modbus协议 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |
| Profibus | Process Field Bus | 过程现场总线 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |
| MQTT | Message Queuing Telemetry Transport | 消息队列遥测传输 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |
| CoAP | Constrained Application Protocol | 受限应用协议 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |
| OPC UA | OPC Unified Architecture | OPC统一架构 | [通信Schema](./02_IoT_Schema/Communication_Schema/README.md) |

### 4.2 标准编号

| 标准编号 | 标准名称 | 相关文档 |
|---------|---------|----------|
| IEC 61131-3 | 可编程控制器编程语言标准 | [PLC Schema标准](./01_Industrial_Automation/PLC_Schema/03_Standards.md#21-iec-61131-3) |
| ISO 11898 | 道路车辆控制器局域网标准 | [CAN Schema标准](./01_Industrial_Automation/CAN_Schema/03_Standards.md) |
| IEC 61850 | 变电站通信标准 | [通信Schema标准](./02_IoT_Schema/Communication_Schema/03_Standards.md) |
| ISO/IEC 23247 | 数字孪生参考架构 | [数字孪生标准](./03_Physical_Device/Digital_Twin/03_Standards.md#21-isoiec-23247) |
| IEC 63278 | 数字孪生系统标准 | [数字孪生标准](./03_Physical_Device/Digital_Twin/03_Standards.md#22-iec-63278) |
| GB/T 33008.1-2016 | 可编程控制器编程语言标准 | [PLC Schema标准](./01_Industrial_Automation/PLC_Schema/03_Standards.md#32-gbt-330081-2016) |
| GB/T 41479-2022 | 数字孪生系统通用要求 | [数字孪生标准](./03_Physical_Device/Digital_Twin/03_Standards.md#31-gbt-41479-2022) |
| GB/T 34068-2017 | 物联网总体技术智能传感器接口规范 | [传感器Schema标准](./02_IoT_Schema/Sensor_Schema/03_Standards.md) |

---

## 5. 技术概念

### 5.1 形式化方法

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| 形式化定义 | Formal Definition | 基于数学的形式化定义 | [形式化定义文档](./README.md#32-文档结构) |
| 形式化证明 | Formal Proof | 基于数学逻辑的证明 | [形式化证明](./README.md#32-文档结构) |
| 类型系统 | Type System | 类型定义和类型检查系统 | [形式化定义](./README.md#32-文档结构) |
| 约束规则 | Constraint Rules | 约束条件和规则 | [形式化定义](./README.md#32-文档结构) |

### 5.2 信息论

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| 信息熵 | Information Entropy | 信息的不确定性度量 | [信息论分析](./05_DSL_Theory/Information_Theory/README.md) |
| 互信息 | Mutual Information | 两个变量的相关性 | [信息论分析](./05_DSL_Theory/Information_Theory/README.md) |
| 信道容量 | Channel Capacity | 信道的最大传输速率 | [信息论分析](./05_DSL_Theory/Information_Theory/README.md) |
| 信息损失 | Information Loss | 转换过程中的信息损失 | [信息论分析](./05_DSL_Theory/Information_Theory/README.md) |

### 5.3 形式语言理论

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| 形式文法 | Formal Grammar | 定义语言的语法规则 | [形式语言理论](./05_DSL_Theory/Formal_Language_Theory/README.md) |
| 语法分析 | Parsing | 分析字符串是否符合语法 | [形式语言理论](./05_DSL_Theory/Formal_Language_Theory/README.md) |
| 语义模型 | Semantic Model | 定义语言的语义 | [形式语言理论](./05_DSL_Theory/Formal_Language_Theory/README.md) |
| 转换理论 | Transformation Theory | Schema转换的理论基础 | [形式语言理论](./05_DSL_Theory/Formal_Language_Theory/README.md) |

### 5.4 数字孪生

| 术语 | 英文 | 定义 | 相关文档 |
|------|------|------|----------|
| 数字孪生 | Digital Twin | 物理设备的数字化表示 | [数字孪生](./03_Physical_Device/Digital_Twin/README.md) |
| 物理映射 | Physical Mapping | 物理到数字的映射 | [数字孪生概述](./03_Physical_Device/Digital_Twin/01_Overview.md) |
| 实时同步 | Real-time Synchronization | 物理与数字的实时同步 | [数字孪生概述](./03_Physical_Device/Digital_Twin/01_Overview.md) |
| 预测分析 | Predictive Analytics | 基于数字模型的预测分析 | [数字孪生概述](./03_Physical_Device/Digital_Twin/01_Overview.md) |

---

## 6. 数学符号

### 6.1 集合运算

| 符号 | 名称 | 定义 | 示例 |
|------|------|------|------|
| `⊕` | 组合运算 | 层间或组件组合 | `S₁ ⊕ S₂` |
| `×` | 笛卡尔积 | 多个维度的组合 | `A × B` |
| `∈` | 属于 | 元素属于集合 | `x ∈ S` |
| `∀` | 全称量词 | 对于所有 | `∀ x ∈ S` |
| `∃` | 存在量词 | 存在 | `∃ x ∈ S` |
| `⇒` | 蕴含 | 如果...则... | `P ⇒ Q` |
| `≡` | 等价 | 等价关系 | `A ≡ B` |

### 6.2 函数和映射

| 符号 | 名称 | 定义 | 示例 |
|------|------|------|------|
| `→` | 映射 | 从...到... | `f: A → B` |
| `↦` | 映射到 | 映射到 | `x ↦ f(x)` |
| `∘` | 复合 | 函数复合 | `f ∘ g` |

### 6.3 逻辑运算

| 符号 | 名称 | 定义 | 示例 |
|------|------|------|------|
| `∧` | 逻辑与 | 且 | `P ∧ Q` |
| `∨` | 逻辑或 | 或 | `P ∨ Q` |
| `¬` | 逻辑非 | 非 | `¬P` |
| `⊢` | 推导 | 可推导 | `Γ ⊢ φ` |

---

## 7. 文档类型缩写

| 缩写 | 全称 | 说明 | 示例 |
|------|------|------|------|
| Overview | Overview | 概述文档 | `01_Overview.md` |
| Formal | Formal Definition | 形式化定义 | `02_Formal_Definition.md` |
| Standards | Standards | 标准对标 | `03_Standards.md` |
| Transform | Transformation | 转换体系 | `04_Transformation.md` |
| Case | Case Studies | 实践案例 | `05_Case_Studies.md` |

---

## 8. 相关文档

- [项目总览](./README.md)
- [快速参考指南](./QUICK_REFERENCE.md)
- [文档索引](./DOCUMENT_INDEX.md)
- [项目完成总结](./PROJECT_COMPLETION_SUMMARY.md)

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
