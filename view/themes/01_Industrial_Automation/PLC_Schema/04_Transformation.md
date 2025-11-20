# PLC Schema转换体系

## 📑 目录

- [PLC Schema转换体系](#plc-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换方向](#11-转换方向)
    - [1.2 转换维度](#12-转换维度)
  - [2. 七维转换矩阵](#2-七维转换矩阵)
    - [2.1 转换矩阵定义](#21-转换矩阵定义)
    - [2.2 详细转换规则](#22-详细转换规则)
      - [2.2.1 类型映射](#221-类型映射)
      - [2.2.2 内存布局](#222-内存布局)
      - [2.2.3 控制流](#223-控制流)
  - [3. Schema到代码转换](#3-schema到代码转换)
    - [3.1 转换函数定义](#31-转换函数定义)
    - [3.2 转换步骤](#32-转换步骤)
      - [步骤1：硬件层转换](#步骤1硬件层转换)
      - [步骤2：程序层转换](#步骤2程序层转换)
      - [步骤3：调度层转换](#步骤3调度层转换)
      - [步骤4：通信层转换](#步骤4通信层转换)
      - [步骤5：行业层转换](#步骤5行业层转换)
    - [3.3 转换示例](#33-转换示例)
  - [4. 代码到Schema转换](#4-代码到schema转换)
    - [4.1 解析函数定义](#41-解析函数定义)
    - [4.2 解析步骤](#42-解析步骤)
      - [步骤1：语法分析](#步骤1语法分析)
      - [步骤2：语义分析](#步骤2语义分析)
      - [步骤3：Schema生成](#步骤3schema生成)
    - [4.3 解析示例](#43-解析示例)
  - [5. Schema到Schema转换](#5-schema到schema转换)
    - [5.1 转换场景](#51-转换场景)
    - [5.2 转换规则](#52-转换规则)
      - [5.2.1 XML到JSON转换](#521-xml到json转换)
      - [5.2.2 跨标准转换](#522-跨标准转换)
  - [6. 转换工具链](#6-转换工具链)
    - [6.1 开源工具](#61-开源工具)
      - [6.1.1 CODESYS](#611-codesys)
      - [6.1.2 OpenPLC](#612-openplc)
    - [6.2 商业工具](#62-商业工具)
      - [6.2.1 西门子TIA Portal](#621-西门子tia-portal)
      - [6.2.2 施耐德Unity Pro](#622-施耐德unity-pro)
    - [6.3 工具对比](#63-工具对比)
  - [7. 转换验证](#7-转换验证)
    - [7.1 验证方法](#71-验证方法)
      - [7.1.1 语法验证](#711-语法验证)
      - [7.1.2 语义验证](#712-语义验证)
      - [7.1.3 等价性验证](#713-等价性验证)
    - [7.2 验证工具](#72-验证工具)
  - [8. 实践案例](#8-实践案例)
    - [8.1 案例1：西门子S7-1200项目导出](#81-案例1西门子s7-1200项目导出)
    - [8.2 案例2：跨平台程序转换](#82-案例2跨平台程序转换)

---

## 1. 转换体系概述

PLC Schema转换体系支持多维度、多方向的转换：

### 1.1 转换方向

1. **Schema → 代码**：
   从Schema生成PLC程序代码
2. **代码 → Schema**：
   从PLC程序代码解析生成Schema
3. **Schema → Schema**：
   不同Schema格式之间的转换

### 1.2 转换维度

支持**七维转换**：

1. **类型映射**
2. **内存布局**
3. **控制流**
4. **错误模型**
5. **并发原语**
6. **二进制编码**
7. **安全边界**

---

## 2. 七维转换矩阵

### 2.1 转换矩阵定义

| 转换维度 | Schema层 | PLC代码层 | 转换规则 |
|---------|---------|----------|---------|
| **类型映射** | IEC数据类型 | 变量声明 | 直接映射 |
| **内存布局** | 变量地址 | 内存分配 | 地址映射 |
| **控制流** | 任务调度 | 程序执行 | 调度映射 |
| **错误模型** | 错误定义 | 异常处理 | 错误映射 |
| **并发原语** | 任务并行 | 多任务执行 | 并发映射 |
| **二进制编码** | 数据类型 | 字节编码 | 编码映射 |
| **安全边界** | 安全等级 | 安全机制 | 安全映射 |

### 2.2 详细转换规则

#### 2.2.1 类型映射

**Schema类型** → **PLC代码类型**：

```text
BOOL → VAR BOOL
INT → VAR INT
REAL → VAR REAL
TIME → VAR TIME
STRING → VAR STRING
Array[INT, 10] → VAR ARRAY[1..10] OF INT
Struct → VAR TYPE_NAME
```

#### 2.2.2 内存布局

**Schema地址** → **PLC内存地址**：

```text
%I0.0 → Input Image Bit 0.0
%Q0.0 → Output Image Bit 0.0
%M0.0 → Memory Bit 0.0
%DB1.DBX0.0 → Data Block 1 Bit 0.0
```

#### 2.2.3 控制流

**Schema任务** → **PLC程序执行**：

```text
Task(cycle=10ms) → OB1 (Main Program)
Task(cycle=100ms) → OB35 (Cyclic Interrupt)
Task(event=interrupt) → OB40 (Hardware Interrupt)
```

---

## 3. Schema到代码转换

### 3.1 转换函数定义

**定义**：

```text
transform: PLC_Schema → PLC_Program
```

### 3.2 转换步骤

#### 步骤1：硬件层转换

```text
Hardware_Schema → Hardware_Configuration
```

**转换规则**：

- CPU模块 → CPU配置代码
- I/O模块 → I/O配置代码
- 电源模块 → 电源配置代码
- 通信模块 → 通信配置代码

#### 步骤2：程序层转换

```text
Program_Schema → Program_Code
```

**转换规则**：

- POU定义 → 程序/功能块/函数代码
- 变量声明 → 变量声明代码
- 实现代码 → 程序逻辑代码

#### 步骤3：调度层转换

```text
Task_Schema → Task_Configuration
```

**转换规则**：

- 任务定义 → 任务配置代码
- 优先级设置 → 优先级配置
- 执行周期 → 周期设置

#### 步骤4：通信层转换

```text
Communication_Schema → Communication_Configuration
```

**转换规则**：

- 协议配置 → 通信配置代码
- 数据交换 → 数据映射代码

#### 步骤5：行业层转换

```text
Industry_Schema → Function_Block_Instantiation
```

**转换规则**：

- 功能块定义 → 功能块实例化代码

### 3.3 转换示例

**Schema定义**：

```dsl
schema Example_Program {
  program Main {
    variables {
      input: VAR_INPUT BOOL
      output: VAR_OUTPUT BOOL
    }
    implementation {
      st: "output := input;"
    }
  }
}
```

**转换后的ST代码**：

```st
PROGRAM Main
VAR_INPUT
  input: BOOL;
END_VAR
VAR_OUTPUT
  output: BOOL;
END_VAR

output := input;
END_PROGRAM
```

---

## 4. 代码到Schema转换

### 4.1 解析函数定义

**定义**：

```text
parse: PLC_Program → PLC_Schema
```

### 4.2 解析步骤

#### 步骤1：语法分析

- 词法分析：识别关键字、标识符等
- 语法分析：构建抽象语法树（AST）

#### 步骤2：语义分析

- 类型检查：验证类型正确性
- 作用域分析：确定变量作用域
- 引用解析：解析变量和函数引用

#### 步骤3：Schema生成

- 从AST生成Schema结构
- 提取类型信息
- 提取控制流信息

### 4.3 解析示例

**ST代码**：

```st
PROGRAM Main
VAR_INPUT
  input: BOOL;
END_VAR
VAR_OUTPUT
  output: BOOL;
END_VAR

output := input;
END_PROGRAM
```

**解析后的Schema**：

```dsl
schema Example_Program {
  program Main {
    variables {
      input: VAR_INPUT BOOL
      output: VAR_OUTPUT BOOL
    }
    implementation {
      st: "output := input;"
    }
  }
}
```

---

## 5. Schema到Schema转换

### 5.1 转换场景

1. **XML Schema ↔ JSON Schema**
2. **PLCopen XML ↔ 厂商XML**
3. **IEC 61131-3 Schema ↔ IEC 61499 Schema**

### 5.2 转换规则

#### 5.2.1 XML到JSON转换

**规则**：

- XML元素 → JSON对象
- XML属性 → JSON属性
- XML文本 → JSON值

#### 5.2.2 跨标准转换

**IEC 61131-3 → IEC 61499**：

- Program → Composite Function Block
- Function Block → Basic Function Block
- Function → Service Interface Function Block

---

## 6. 转换工具链

### 6.1 开源工具

#### 6.1.1 CODESYS

- **功能**：支持IEC 61131-3标准
- **Schema支持**：XML导入/导出
- **语言**：多种编程语言支持

#### 6.1.2 OpenPLC

- **功能**：开源PLC运行时
- **Schema支持**：部分支持
- **特点**：跨平台支持

### 6.2 商业工具

#### 6.2.1 西门子TIA Portal

- **功能**：完整PLC开发环境
- **Schema支持**：XML项目格式
- **特点**：S7系列完整支持

#### 6.2.2 施耐德Unity Pro

- **功能**：Modicon PLC开发
- **Schema支持**：XML格式支持
- **特点**：过程控制优化

### 6.3 工具对比

| 工具 | Schema支持 | XML格式 | 跨平台 | 开源 |
|-----|-----------|---------|--------|------|
| **CODESYS** | ✅ 完整 | ✅ 是 | ✅ 是 | ⚠️ 部分 |
| **OpenPLC** | ⚠️ 部分 | ⚠️ 部分 | ✅ 是 | ✅ 是 |
| **TIA Portal** | ✅ 完整 | ✅ 是 | ❌ 否 | ❌ 否 |
| **Unity Pro** | ✅ 完整 | ⚠️ 部分 | ❌ 否 | ❌ 否 |

---

## 7. 转换验证

### 7.1 验证方法

#### 7.1.1 语法验证

- **XML Schema验证**：使用XSD验证
- **JSON Schema验证**：使用JSON Schema验证器

#### 7.1.2 语义验证

- **类型检查**：验证类型正确性
- **约束检查**：验证约束条件
- **引用检查**：验证引用完整性

#### 7.1.3 等价性验证

- **双向转换**：Schema → Code → Schema
- **语义等价**：验证语义一致性

### 7.2 验证工具

- **XML验证器**：xmllint、XMLSpy
- **JSON验证器**：ajv、jsonschema
- **PLC验证器**：各厂商编译工具

---

## 8. 实践案例

### 8.1 案例1：西门子S7-1200项目导出

**场景**：将TIA Portal项目导出为XML格式

**步骤**：

1. 在TIA Portal中打开项目
2. 选择"导出"功能
3. 选择XML格式
4. 生成XML文件

**结果**：获得完整的PLC Schema XML文件

### 8.2 案例2：跨平台程序转换

**场景**：将CODESYS程序转换为TIA Portal格式

**步骤**：

1. 从CODESYS导出XML
2. 解析XML Schema
3. 转换为TIA Portal Schema
4. 导入TIA Portal

**挑战**：厂商特定扩展的兼容性

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
