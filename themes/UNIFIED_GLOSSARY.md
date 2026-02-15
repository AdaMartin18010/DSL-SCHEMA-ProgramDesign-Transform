# DSL Schema项目统一术语表

**版本**: v1.0
**创建日期**: 2026-02-15
**适用范围**: Themes 01-05及后续所有主题

---

## 📑 目录

- [1. 术语表概述](#1-术语表概述)
- [2. 核心术语定义](#2-核心术语定义)
- [3. 按主题分类术语](#3-按主题分类术语)
  - [3.1 工业自动化术语](#31-工业自动化术语)
  - [3.2 物联网术语](#32-物联网术语)
  - [3.3 物理设备术语](#33-物理设备术语)
  - [3.4 编程转换术语](#34-编程转换术语)
  - [3.5 DSL理论术语](#35-dsl理论术语)
- [4. 术语关系本体](#4-术语关系本体)
- [5. 多语言对照](#5-多语言对照)
- [6. 版本历史](#6-版本历史)

---

## 1. 术语表概述

本文档提供DSL Schema转换项目中的统一术语定义，确保：

- 跨主题术语一致性
- 概念边界清晰
- 形式化定义精确
- 国际标准对齐

---

## 2. 核心术语定义

### 2.1 Schema (模式/架构)

**定义**:
描述系统结构、行为、约束的形式化规范，用于定义数据组织方式和交互规则。

**形式化定义**:

```
Schema = (Structure, Behavior, Constraints, Semantics)

其中:
- Structure: 元素组成和层次关系
- Behavior: 动态行为和状态转换
- Constraints: 约束规则和验证条件
- Semantics: 语义解释和含义
```

**统一用法**:

- ✅ 使用"Schema"（首字母大写）
- ❌ 避免"模式"、"架构"混用

**来源**: 源自数据库Schema概念，扩展至通用系统建模

---

### 2.2 DSL (Domain-Specific Language，领域特定语言)

**定义**:
针对特定应用领域设计的计算机语言，与通用编程语言(GPL)相对。

**分类**:

```
DSL
├── 外部DSL (External DSL)
│   └── 独立语法和解析器 (如SQL、Regex)
└── 内部DSL (Internal DSL)
    └── 嵌入宿主语言 (如LINQ、RSpec)
```

**统一用法**:

- ✅ 使用"DSL"缩写
- ✅ 全称"领域特定语言"
- ❌ 避免"专用语言"等变体

---

### 2.3 转换 (Transformation)

**定义**:
将源Schema或模型转换为目标Schema或模型的过程，保持语义等价性或明确映射关系。

**形式化定义**:

```
Transformation: Source → Target
∀s ∈ Source: ∃t ∈ Target : transform(s) = t ∧ semantically_related(s, t)
```

**相关术语**:

- **转换规则** (Transformation Rule): 定义转换的映射规则
- **转换函数** (Transform Function): 实现转换的数学函数
- **双向转换** (Bidirectional Transformation): 支持正向和反向转换

---

### 2.4 形式化 (Formalization)

**定义**:
使用严格的数学符号和逻辑规则定义概念、系统和过程，消除歧义。

**层次**:

```
形式化程度
├── 自然语言描述 (非形式化)
├── 结构化描述 (半形式化)
├── 数学符号定义 (形式化)
└── 机器可验证证明 (严格形式化)
```

---

### 2.5 七维转换 (Seven-Dimensional Transformation)

**定义**:
本项目提出的Schema转换分析框架，从七个维度分析转换问题。

**七维定义**:

| 维度 | 英文 | 定义 | 示例 |
|------|------|------|------|
| 类型映射 | Type Mapping | 数据类型之间的转换规则 | INT → int32_t |
| 内存布局 | Memory Layout | 数据在存储中的组织结构 | 结构体对齐、位域 |
| 控制流 | Control Flow | 执行顺序和流程控制 | 循环、条件、任务调度 |
| 错误模型 | Error Model | 异常处理和错误传播 | errno、Result<T,E> |
| 并发原语 | Concurrency Primitives | 并行和同步机制 | Mutex、Channel、Task |
| 二进制编码 | Binary Encoding | 数据序列化编码 | Protobuf、CBOR、ASN.1 |
| 安全边界 | Security Boundary | 访问控制和安全隔离 | Capability、沙箱、JWT |

**统一用法**:

- ✅ 使用"七维转换"
- ✅ 英文"Seven-Dimensional Transformation"
- ❌ 避免"7D转换"等简写

---

## 3. 按主题分类术语

### 3.1 工业自动化术语

#### PLC (Programmable Logic Controller，可编程逻辑控制器)

**定义**:
专为工业环境设计的数字运算操作电子系统，用于控制机械设备和过程。

**Schema层次**:

```
PLC Schema（五层结构）
├── 硬件层 (Hardware Layer) - 物理设备配置
├── 程序层 (Program Layer) - 程序组织单元(POU)
├── 调度层 (Scheduling Layer) - 任务调度配置
├── 通信层 (Communication Layer) - 通信协议配置
└── 行业层 (Industry Layer) - 行业特定功能块
```

**统一用法**:

- ✅ 使用"PLC"
- ✅ 五层结构描述统一使用上述层次名称

---

#### POU (Program Organization Unit，程序组织单元)

**定义**:
IEC 61131-3标准中的基本编程单元，包括Program、Function Block和Function三种类型。

**类型对比**:

| 类型 | 实例化 | 持久状态 | 适用场景 |
|------|--------|---------|---------|
| Program | 是 | 是 | 主程序单元 |
| Function Block | 是 | 是 | 可复用功能块 |
| Function | 否 | 否 | 纯计算函数 |

---

#### CAN (Controller Area Network，控制器局域网)

**定义**:
ISO 11898标准定义的串行通信协议，用于汽车和工业自动化领域。

**Schema层次**:

```
CAN Schema（三层结构）
├── 物理层 (Physical Layer) - ISO 11898-2/3
├── 数据链路层 (Data Link Layer) - ISO 11898-1
└── 应用层 (Application Layer) - DBC/CANopen/J1939
```

**统一用法**:

- ✅ 使用"CAN"
- ✅ 三层结构描述统一使用上述层次名称

---

### 3.2 物联网术语

#### IoT Schema（五维结构）

**定义**:
描述物联网设备的五维形式化规范。

**五维定义**:

```
IoT Schema = Physical ⊕ Communication ⊕ Parameter ⊕ Control ⊕ Security

其中:
- Physical: 物理接口与电气特性
- Communication: 通信协议与数据链路
- Parameter: 传感器参数与元数据
- Control: 控制与配置
- Security: 安全与合规
```

**统一用法**:

- ✅ 使用"五维结构"
- ✅ 五维名称统一使用上述定义
- ❌ 避免"五层"（与PLC Schema混淆）

---

#### 智能传感器 (Smart Sensor)

**定义**:
具备信号处理、自诊断、网络通信能力的传感器，符合IEEE 1451标准。

**特征**:

- TEDS (Transducer Electronic Data Sheet) - 传感器电子数据表
- 即插即用 (Plug and Play) 能力
- 网络通信接口

---

### 3.3 物理设备术语

#### 数字孪生 (Digital Twin)

**定义**:
物理设备或系统的虚拟映射，实现实时同步、预测分析和优化控制。

**Schema要素**:

```
Digital Twin Schema
├── 几何模型 (Geometric Model) - 3D CAD模型
├── 物理模型 (Physical Model) - 物理特性仿真
├── 行为模型 (Behavioral Model) - 运行行为模拟
├── 规则模型 (Rule Model) - 约束和规则
└── 数据接口 (Data Interface) - 实时数据交换
```

**标准对齐**:

- ISO/IEC 23247:2021 - 数字孪生参考架构
- IEC 63278-1:2024 - 数字孪生系统
- GB/T 43441.1 - 数字孪生通用要求

---

#### 物理设备Schema（五维结构）

**定义**:
描述物理设备特性的五维形式化规范。

**五维定义**:

```
Physical Device Schema = Electrical ⊕ Mechanical ⊕ Thermal ⊕ Functional ⊕ Safety

其中:
- Electrical: 电气特性（电压、电流、功率、绝缘）
- Mechanical: 机械特性（结构、运动、材料、精度）
- Thermal: 热学特性（温度、热传导、热容量）
- Functional: 功能特性（性能、接口、协议）
- Safety: 安全特性（等级、认证、合规）
```

**统一用法**:

- ✅ 使用"五维结构"
- ✅ 五维名称统一使用上述定义

---

### 3.4 编程转换术语

#### 代码生成 (Code Generation)

**定义**:
根据Schema定义自动生成可执行代码的过程。

**流程**:

```
Schema定义 → 解析 → 中间表示(IR) → 转换 → 代码模板 → 目标代码
```

**相关术语**:

- **模板引擎** (Template Engine): Mustache、Jinja2、Handlebars
- **中间表示** (Intermediate Representation, IR): 抽象的代码表示形式

---

#### MDA (Model Driven Architecture，模型驱动架构)

**定义**:
OMG提出的软件开发方法，通过模型驱动代码生成。

**三层模型**:

```
MDA层次
├── CIM (Computation Independent Model) - 计算无关模型
├── PIM (Platform Independent Model) - 平台无关模型
└── PSM (Platform Specific Model) - 平台特定模型
```

**转换关系**:

- CIM → PIM: 业务分析
- PIM → PSM: 平台映射
- PSM → Code: 代码生成

---

### 3.5 DSL理论术语

#### 信息熵 (Information Entropy)

**定义**:
度量信息不确定性的量度，由香农提出。

**公式**:

```
H(X) = -Σ P(x) log₂ P(x)

其中:
- X: 随机变量
- P(x): 事件x发生的概率
```

**在Schema转换中的应用**:

- 度量Schema的信息量
- 评估转换过程中的信息损失

---

#### 形式语言 (Formal Language)

**定义**:
由形式文法生成的符号串集合。

**乔姆斯基层次**:

```
形式语言层次
├── 0型: 无限制文法 (图灵可识别)
├── 1型: 上下文有关文法
├── 2型: 上下文无关文法
└── 3型: 正则文法
```

**Schema应用**:

- 定义Schema的语法结构
- 验证Schema的合法性

---

#### 知识图谱 (Knowledge Graph)

**定义**:
用图结构表示知识的数据结构，包含实体、关系和属性。

**形式化定义**:

```
Knowledge Graph = (Entities, Relations, Attributes, Triples)

其中:
- Entities: 实体集合
- Relations: 关系集合
- Attributes: 属性集合
- Triples: {(subject, predicate, object)} 三元组集合
```

**标准对齐**:

- W3C RDF - 资源描述框架
- W3C OWL - Web本体语言
- ISO/IEC 21838 - 顶层本体标准

---

## 4. 术语关系本体

### 4.1 概念层次结构

```
概念本体
├── Schema
│   ├── PLC Schema (五层)
│   ├── IoT Schema (五维)
│   ├── Physical Device Schema (五维)
│   └── Communication Schema
├── DSL
│   ├── External DSL
│   └── Internal DSL
├── Transformation
│   ├── Type Mapping
│   ├── Memory Layout
│   ├── Control Flow
│   ├── Error Model
│   ├── Concurrency Primitives
│   ├── Binary Encoding
│   └── Security Boundary
└── Theory Foundation
    ├── Information Theory
    ├── Formal Language Theory
    ├── Type Theory
    └── Category Theory
```

### 4.2 术语关联矩阵

| 术语 | 相关术语 | 关系类型 |
|------|---------|---------|
| Schema | DSL | implements |
| PLC Schema | IEC 61131-3 | conforms_to |
| IoT Schema | IEEE 1451 | conforms_to |
| Transformation | Code Generation | is_a |
| MDA | PIM/PSM | includes |
| Knowledge Graph | RDF/OWL | represented_by |

---

## 5. 多语言对照

### 5.1 中英文对照

| 英文 | 中文 | 备注 |
|------|------|------|
| Schema | 模式/架构 | 优先使用"Schema" |
| DSL | 领域特定语言 | 也可用"专用领域语言" |
| Transformation | 转换 | 避免"变换" |
| Formalization | 形式化 | - |
| Program Organization Unit | 程序组织单元 | 缩写POU |
| Function Block | 功能块 | - |
| Digital Twin | 数字孪生 | - |
| Knowledge Graph | 知识图谱 | - |

### 5.2 缩写对照

| 缩写 | 全称 | 中文 |
|------|------|------|
| PLC | Programmable Logic Controller | 可编程逻辑控制器 |
| POU | Program Organization Unit | 程序组织单元 |
| CAN | Controller Area Network | 控制器局域网 |
| IoT | Internet of Things | 物联网 |
| DSL | Domain-Specific Language | 领域特定语言 |
| MDA | Model Driven Architecture | 模型驱动架构 |
| RDF | Resource Description Framework | 资源描述框架 |
| OWL | Web Ontology Language | Web本体语言 |
| OPC UA | OPC Unified Architecture | OPC统一架构 |

---

## 6. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-02-15 | 初始版本，包含Themes 01-05核心术语 | DSL Schema团队 |

---

## 附录

### 附录A: 术语使用检查清单

在编写文档时，请检查：

- [ ] 使用本文档定义的术语
- [ ] 保持术语一致性（不混用同义词）
- [ ] 首次出现时使用全称+缩写
- [ ] 引用相关标准术语时对齐标准定义

### 附录B: 术语扩展流程

新增术语的流程：

1. 检查现有术语表，确保无重复
2. 提供形式化定义（如可能）
3. 说明与现有术语的关系
4. 提供多语言对照
5. 提交术语委员会审核

---

**维护者**: DSL Schema研究团队
**审核周期**: 每季度审查更新
**反馈渠道**: 项目Issue跟踪系统
