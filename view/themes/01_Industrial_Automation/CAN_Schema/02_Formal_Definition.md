# CAN协议Schema形式化定义

## 📑 目录

- [CAN协议Schema形式化定义](#can协议schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 层间关系](#12-层间关系)
  - [2. 三层Schema结构形式化定义](#2-三层schema结构形式化定义)
    - [2.1 物理层Schema](#21-物理层schema)
    - [2.2 数据链路层Schema](#22-数据链路层schema)
    - [2.3 应用层Schema](#23-应用层schema)
  - [3. DBC文件形式化定义](#3-dbc文件形式化定义)
  - [4. 类型系统](#4-类型系统)
  - [5. 约束规则](#5-约束规则)
  - [6. 转换函数](#6-转换函数)
  - [7. 形式化定理](#7-形式化定理)
  - [8. 证明](#8-证明)

---

## 1. 形式化模型

### 1.1 基本定义

设 `CAN_Schema` 为CAN Schema的集合，
`CAN_Frame` 为CAN帧的集合。

**定义1（CAN Schema）**：
CAN Schema是一个三元组：

```text
CAN_Schema = (P, D, A)
```

其中：
- `P`：物理层Schema
- `D`：数据链路层Schema
- `A`：应用层Schema

### 1.2 层间关系

**定义2（层间组合）**：
层间组合运算 `⊕` 定义为：

```text
P ⊕ D ⊕ A = { (p, d, a) | p ∈ P, d ∈ D, a ∈ A,
                      constraints(p, d, a) }
```

其中 `constraints(p, d, a)` 表示层间约束条件。

---

## 2. 三层Schema结构形式化定义

### 2.1 物理层Schema

**定义3（物理层Schema）**：

```text
Physical_Schema = (Voltage, BaudRate, Termination, Topology)
```

**形式化DSL定义**：

```dsl
schema PhysicalLayer {
  can_h: Voltage @range(2.5V, 3.3V)
  can_l: Voltage @range(1.5V, 2.0V)
  diff_threshold: Enum {
    dominant: 2.3V,
    recessive: 0.6V
  }
  baud_rate: Enum {
    CAN_2_0: Range[5kbps, 1Mbps],
    CAN_FD: Range[500kbps, 12Mbps]
  }
  termination: Resistor @value(120Ω) @tolerance(±5%)
  topology: Enum { linear, star, ring }
} @hardware(spec="ISO_11898_2")
```

### 2.2 数据链路层Schema

**定义4（数据链路层Schema）**：

```text
DataLink_Schema = (Frame_Structure, Arbitration, Error_Detection)
```

**形式化DSL定义**：

```dsl
schema DataFrame {
  sof: Bit @const(0)
  arbitration: struct {
    id: UInt11 @priority("lower_is_higher")
    rtr: Bit @default(0)
    ide: Bit @const(0)
  }
  control: struct {
    dlc: UInt4 @range(0, 8)
    brs: Bit @can_fd_only
  }
  data: Bytes @length(dlc) @max(8)
  crc: UInt15 @computed(prefix_bits)
  ack: struct {
    slot: Bit @default(1)
    delimiter: Bit @const(1)
  }
  eof: Bit[7] @const(0x7F)
} @protocol(iso="11898_1", bit_stuffing=true)
```

### 2.3 应用层Schema

**定义5（应用层Schema）**：

```text
Application_Schema = (Message_Definition, Signal_Definition, Node_Definition)
```

**形式化DSL定义（DBC格式）**：

```dsl
schema DBC_Application {
  messages: List<Message> {
    message: {
      id: UInt29 @unique
      name: Identifier
      dlc: UInt4 @range(0, 8)
      transmitter: NodeRef
      signals: List<Signal> {
        signal: {
          name: Identifier
          start_bit: UInt8
          bit_length: UInt8
          byte_order: Enum { Motorola, Intel }
          value_type: Enum { Signed, Unsigned }
          factor: Float64
          offset: Float64
          min: Float64
          max: Float64
          unit: String
          receivers: List<NodeRef>
        }
      }
    }
  }
} @format(vector_dbc)
```

---

## 3. DBC文件形式化定义

### 3.1 DBC文件结构

**定义6（DBC文件）**：

```text
DBC_File = (Version, BaudRate, Nodes, Messages, Signals, Attributes)
```

### 3.2 DBC语法形式化

**BNF语法定义**：

```bnf
<dbc_file> ::= <version> <ns> <bs> <nodes> <messages> <signals> <attributes>

<version> ::= "VERSION" <string>
<ns> ::= "NS_" <symbol_list>
<bs> ::= "BS_:" <baudrate>
<nodes> ::= "BU_:" <node_list>
<messages> ::= "BO_" <message_id> <message_name> ":" <dlc> <transmitter> <signal_list>
<signals> ::= "SG_" <signal_name> <signal_def> ":" <start_bit> "|" <length> "@" <byte_order> <value_type> "(" <factor> "," <offset> ")" "[" <min> "|" <max> "]" <unit> <receiver_list>
```

---

## 4. 类型系统

### 4.1 CAN数据类型

**定义7（CAN数据类型）**：

```text
CAN_Type = { BOOL, UINT8, UINT16, UINT32, INT8, INT16, INT32, FLOAT32, FLOAT64 }
```

### 4.2 信号类型

**定义8（信号类型）**：

```text
Signal_Type = (Name, StartBit, Length, ByteOrder, ValueType, Factor, Offset, Min, Max, Unit)
```

---

## 5. 约束规则

### 5.1 物理层约束

**规则1（电压约束）**：
CAN_H和CAN_L电压必须满足ISO 11898-2规范。

**规则2（终端电阻）**：
总线两端必须各有一个120Ω终端电阻。

### 5.2 数据链路层约束

**规则3（帧长度）**：
标准帧长度为44-108位，扩展帧长度为64-128位。

**规则4（位填充）**：
连续5个相同位后必须插入补码位。

**规则5（CRC校验）**：
CRC必须正确，否则帧被丢弃。

### 5.3 应用层约束

**规则6（消息ID唯一性）**：
同一网络中消息ID必须唯一。

**规则7（信号范围）**：
信号值必须在min和max范围内。

---

## 6. 转换函数

### 6.1 DBC到代码转换

**定义9（转换函数）**：

```text
transform: DBC_Schema → Code
```

**转换规则**：

1. **消息定义** → 结构体定义
2. **信号定义** → 结构体字段
3. **编码规则** → 解析函数

### 6.2 代码到DBC转换

**定义10（反向转换）**：

```text
parse: Code → DBC_Schema
```

---

## 7. 形式化定理

### 7.1 完备性定理

**定理1（CAN Schema完备性）**：
对于任意CAN网络配置，存在Schema `s`，
使得网络行为可以由 `s` 完全描述。

### 7.2 正确性定理

**定理2（转换正确性）**：
如果 `s` 是有效的CAN Schema，
则 `transform(s)` 生成的代码满足：
- 帧结构正确
- 信号解析正确
- 编码解码正确

---

## 8. 证明

### 8.1 完备性证明

**证明**：
根据ISO 11898标准，所有CAN网络配置
都可以用标准格式表示，而标准格式
可以形式化为Schema。

因此，对于任意网络配置，存在Schema `s`。

### 8.2 正确性证明

**证明**：
转换函数 `transform` 遵循ISO 11898标准
和DBC文件格式，因此生成的代码满足标准要求。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
