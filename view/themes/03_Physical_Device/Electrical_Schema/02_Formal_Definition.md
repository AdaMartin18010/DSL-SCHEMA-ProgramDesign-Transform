# 物理设备电气Schema形式化定义

## 📑 目录

- [物理设备电气Schema形式化定义](#物理设备电气schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 电气特性关系](#12-电气特性关系)
  - [2. 电气特性Schema形式化定义](#2-电气特性schema形式化定义)
    - [2.1 电压特性Schema](#21-电压特性schema)
    - [2.2 电流特性Schema](#22-电流特性schema)
    - [2.3 功率特性Schema](#23-功率特性schema)
    - [2.4 绝缘特性Schema](#24-绝缘特性schema)
  - [3. 类型系统](#3-类型系统)
    - [3.1 基本数据类型](#31-基本数据类型)
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

设 `Electrical_Schema` 为物理设备电气Schema的集合，
`Electrical_Property` 为电气特性的集合。

**定义1（Schema）**：
物理设备电气Schema是一个四元组：

```text
Electrical_Schema = (Voltage, Current, Power, Insulation)
```

其中：

- `Voltage`：电压特性Schema
- `Current`：电流特性Schema
- `Power`：功率特性Schema
- `Insulation`：绝缘特性Schema

### 1.2 电气特性关系

**定义2（特性组合）**：
特性组合运算 `⊕` 定义为：

```text
P₁ ⊕ P₂ = { (x, y) | x ∈ P₁, y ∈ P₂,
                  electrical_constraints(x, y) }
```

其中 `electrical_constraints(x, y)` 表示电气特性约束条件。

---

## 2. 电气特性Schema形式化定义

### 2.1 电压特性Schema

**定义3（电压特性Schema）**：

```text
Voltage_Schema = (Rated, Range, Tolerance, Protection)
```

其中：

- `Rated`：额定电压
- `Range`：电压范围
- `Tolerance`：电压容差
- `Protection`：过压保护

**形式化DSL定义**：

```dsl
schema VoltageCharacteristics {
  rated_voltage: Float64 @unit("V") @required
  voltage_range: Range {
    min: Float64 @unit("V")
    max: Float64 @unit("V")
  }
  tolerance: Float64 @unit("%") @default(±5.0)
  overvoltage_protection: {
    threshold: Float64 @unit("V")
    response_time: Duration @unit("ms") @max(100)
    protection_type: Enum { shutdown, current_limit, voltage_clamp }
  }
} @standard("IEC_60335-1")
```

### 2.2 电流特性Schema

**定义4（电流特性Schema）**：

```text
Current_Schema = (Rated, Range, Protection, Leakage)
```

其中：

- `Rated`：额定电流
- `Range`：电流范围
- `Protection`：过流保护
- `Leakage`：漏电流

**形式化DSL定义**：

```dsl
schema CurrentCharacteristics {
  rated_current: Float64 @unit("A") @required
  current_range: Range {
    min: Float64 @unit("A")
    max: Float64 @unit("A")
  }
  overcurrent_protection: {
    threshold: Float64 @unit("A")
    response_time: Duration @unit("ms") @max(50)
    protection_type: Enum { fuse, circuit_breaker, electronic }
  }
  leakage_current: {
    max_value: Float64 @unit("mA") @max(0.5) @standard("IEC_60335-1")
    measurement_method: Enum { direct, indirect }
  }
} @standard("IEC_60335-1")
```

### 2.3 功率特性Schema

**定义5（功率特性Schema）**：

```text
Power_Schema = (Rated, Range, Efficiency, PowerFactor)
```

其中：

- `Rated`：额定功率
- `Range`：功率范围
- `Efficiency`：效率
- `PowerFactor`：功率因数

**形式化DSL定义**：

```dsl
schema PowerCharacteristics {
  rated_power: Float64 @unit("W") @required
  power_range: Range {
    min: Float64 @unit("W")
    max: Float64 @unit("W")
  }
  efficiency: {
    nominal: Float64 @unit("%") @min(0) @max(100)
    measurement_conditions: {
      load: Float64 @unit("%") @default(100)
      temperature: Float64 @unit("°C") @default(25)
    }
  }
  power_factor: {
    nominal: Float64 @min(0) @max(1)
    correction: Optional<Bool> @default(false)
  }
} @standard("IEC_60335-1")
```

### 2.4 绝缘特性Schema

**定义6（绝缘特性Schema）**：

```text
Insulation_Schema = (Class, Resistance, Withstand, Creepage)
```

其中：

- `Class`：绝缘等级
- `Resistance`：绝缘电阻
- `Withstand`：耐压测试
- `Creepage`：爬电距离

**形式化DSL定义**：

```dsl
schema InsulationCharacteristics {
  insulation_class: Enum { Class_I, Class_II, Class_III } @required
  insulation_resistance: {
    min_value: Float64 @unit("MΩ") @min(2.0) @standard("IEC_60335-1")
    measurement_voltage: Float64 @unit("V") @default(500)
  }
  dielectric_withstand: {
    test_voltage: Float64 @unit("V") @required
    duration: Duration @unit("s") @default(60)
    test_frequency: Float64 @unit("Hz") @default(50)
  }
  creepage_distance: {
    min_value: Float64 @unit("mm") @required
    pollution_degree: Enum { 1, 2, 3, 4 } @default(2)
  }
  clearance_distance: {
    min_value: Float64 @unit("mm") @required
    overvoltage_category: Enum { I, II, III, IV } @default(II)
  }
} @standard("IEC_60335-1")
```

---

## 3. 类型系统

### 3.1 基本数据类型

**定义7（基本数据类型）**：

```text
Basic_Type = { FLOAT, INT, BOOL, STRING, ENUM, DURATION }
```

### 3.2 派生类型

**定义8（派生类型）**：

```text
Derived_Type = Range | Protection | Measurement
```

### 3.3 类型约束

**定义9（类型约束）**：
对于电气参数 `p`，其类型约束为：

```text
electrical_type_constraint(p) = { t | t ∈ Electrical_Type,
                                     safety_level(p) ≥ safety_level(t) }
```

---

## 4. 约束规则

### 4.1 语法约束

**规则1（单位一致性）**：
所有电气参数必须使用标准单位。

**规则2（范围限制）**：
参数值必须在定义范围内。

**规则3（安全等级）**：
安全相关参数必须符合安全等级要求。

### 4.2 语义约束

**规则4（功率关系）**：
功率、电压、电流必须满足 `P = U × I`。

**规则5（安全要求）**：
绝缘特性必须满足安全标准要求。

**规则6（保护协调）**：
保护装置必须协调配合。

---

## 5. 转换函数

### 5.1 Schema到代码转换

**定义10（转换函数）**：

```text
transform: Electrical_Schema → Electrical_Code
```

**转换规则**：

1. **电压特性** → 电压监测代码
2. **电流特性** → 电流监测代码
3. **功率特性** → 功率计算代码
4. **绝缘特性** → 绝缘测试代码

### 5.2 代码到Schema转换

**定义11（反向转换）**：

```text
parse: Electrical_Code → Electrical_Schema
```

---

## 6. 形式化定理

### 6.1 完备性定理

**定理1（电气Schema完备性）**：
对于任意物理设备电气特性 `e`，存在Schema `s`，
使得 `parse(e) = s` 且 `transform(s) = e'`，
其中 `e'` 与 `e` 语义等价。

### 6.2 正确性定理

**定理2（转换正确性）**：
如果 `s` 是有效的电气Schema，
则 `transform(s)` 生成的代码 `c` 满足：

- 语法正确
- 类型安全
- 符合安全标准

---

## 7. 证明

### 7.1 完备性证明

**证明**：
根据IEC 60335-1、GB/T 19903等标准，所有物理设备
电气特性都可以用标准语法表示，而标准语法
可以形式化为Schema。

因此，对于任意电气特性 `e`，存在Schema `s`。

### 7.2 正确性证明

**证明**：
转换函数 `transform` 遵循相关标准，
因此生成的代码满足标准要求。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
