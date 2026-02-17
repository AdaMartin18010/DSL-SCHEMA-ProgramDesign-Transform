# PLC Schema标准对标

## 📑 目录

- [PLC Schema标准对标](#plc-schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
    - [1.1 标准关系](#11-标准关系)
  - [2. 国际标准](#2-国际标准)
    - [2.1 IEC 61131-3:2025](#21-iec-61131-32025)
      - [2.1.1 IEC 61131-3:2025 详细Schema映射](#211-iec-61131-32025-详细schema映射)
      - [2.1.2 厂商适配状态追踪](#212-厂商适配状态追踪)
    - [2.2 IEC 61499:2012](#22-iec-614992012)
    - [2.3 ISO/IEC 14977:1996](#23-isoiec-149771996)
  - [3. 国家标准](#3-国家标准)
    - [3.1 GB/T 15969.3-2017](#31-gbt-159693-2017)
    - [3.2 GB/T 19582-2008](#32-gbt-19582-2008)
    - [3.3 GB/T 20540-2006](#33-gbt-20540-2006)
  - [4. 行业标准](#4-行业标准)
    - [4.1 PLCopen](#41-plcopen)
      - [4.1.1 XML格式标准](#411-xml格式标准)
      - [4.1.2 运动控制标准](#412-运动控制标准)
      - [4.1.3 安全标准](#413-安全标准)
    - [4.2 OPC Foundation](#42-opc-foundation)
  - [5. 厂商标准](#5-厂商标准)
    - [5.1 西门子（Siemens）](#51-西门子siemens)
    - [5.2 施耐德（Schneider）](#52-施耐德schneider)
    - [5.3 三菱（Mitsubishi）](#53-三菱mitsubishi)
  - [6. 标准对比矩阵](#6-标准对比矩阵)
    - [6.1 标准对比表](#61-标准对比表)
    - [6.2 Schema特性对比](#62-schema特性对比)
    - [6.3 工具链支持对比](#63-工具链支持对比)
  - [7. 标准发展趋势](#7-标准发展趋势)
    - [7.1 2024-2025年趋势](#71-2024-2025年趋势)
      - [7.1.1 云原生支持](#711-云原生支持)
      - [7.1.2 AI集成](#712-ai集成)
      - [7.1.3 数字孪生](#713-数字孪生)
    - [7.2 标准化方向](#72-标准化方向)
    - [7.3 2025-2026年展望](#73-2025-2026年展望)
      - [7.3.1 IEC 61131-3第四版已发布](#731-iec-61131-3第四版已发布)
      - [7.3.2 边缘计算集成](#732-边缘计算集成)
      - [7.3.3 安全增强](#733-安全增强)
  - [8. 参考文献](#8-参考文献)
    - [8.1 标准文档](#81-标准文档)
    - [8.2 在线资源](#82-在线资源)
    - [8.3 学术文献](#83-学术文献)
    - [8.4 技术社区](#84-技术社区)

---

## 1. 标准体系概述

PLC Schema标准体系分为四个层次：

1. **国际标准**：IEC、ISO等国际组织制定
2. **国家标准**：各国标准化组织制定
3. **行业标准**：行业组织制定
4. **厂商标准**：设备厂商制定

### 1.1 标准关系

```text
国际标准（IEC/ISO）
    ↓
国家标准（GB/T等）
    ↓
行业标准（PLCopen等）
    ↓
厂商标准（Siemens/ABB等）
```

---

## 2. 国际标准

### 2.1 IEC 61131-3:2025

**标准名称**：
Programmable controllers - Part 3: Programming languages (Edition 4.0)

**发布信息**：

- **版本**：Edition 4.0（第四版）
- **发布日期**：2025年5月22日
- **ISBN**：9782832704363
- **页数**：518页
- **稳定性日期**：2027年

**核心内容**：

- **4种编程语言**（⚠️ IL语言已在第四版中移除）：
  - ~~IL（Instruction List）~~ - **第四版已删除**
  - LD（Ladder Diagram）- 梯形图
  - FBD（Function Block Diagram）- 功能块图
  - ST（Structured Text）- 结构化文本
  - SFC（Sequential Function Chart）- 顺序功能图

- **新增特性（第四版）**：
  - **UTF-8字符串支持**：新增USTRING和UCHAR数据类型
  - **并发同步机制**：第6.9章新增互斥锁(Mutex)和信号量(Semaphore)
  - **属性(Property)**：支持类/功能块/接口的属性定义
  - **字符串函数增强**：LEN_MAX, LEN_CODE_UNIT
  - **字符代码表示**：`${十六进制}`格式支持任意Unicode字符
  - **数据类型转换**：STRING/ARRAY_OF_BYTE双向转换
  - **隐式转换扩展**：STRING_TO_WSTRING和CHAR_TO_WCHAR改为隐式转换

- **数据类型系统**：
  - 基本数据类型（BOOL、INT、REAL等）
  - 派生数据类型（Array、Struct等）
  - 新增USTRING、UCHAR支持Unicode

- **程序组织单元（POU）**：
  - Program
  - Function Block
  - Function

**Schema体现**：
IEC 61131-3明确定义了程序结构、数据类型、变量声明等Schema要素。

**与第三版(2013)的主要差异**：

| 特性 | 第三版(2013) | 第四版(2025) | Schema影响 |
|------|-------------|-------------|-----------|
| 编程语言 | 5种（含IL） | 4种（IL已移除） | 需移除IL相关Schema定义 |
| UTF-8支持 | 无 | 新增USTRING/UCHAR | 需扩展字符串类型Schema |
| 并发同步 | 无 | 新增Mutex/Semaphore | 需新增同步原语Schema |
| 面向对象 | 有限 | 增强Property支持 | **需新增Property Schema** |
| 字符串转换 | 显式 | 部分隐式 | 需更新类型转换规则 |
| 字符表示 | 单字节 | Unicode支持 | 需更新字符编码Schema |

#### 2.1.1 IEC 61131-3:2025 详细Schema映射

**新增Property定义Schema**（第四版核心新增）：

```dsl
schema Property_Definition {
  name: Identifier
  type: DataType

  getter: FunctionBlock {
    inputs: []
    outputs: [{ name: "VALUE", type: Property.type }]
    implementation: ST_Code
  }

  setter: Optional[FunctionBlock] {
    inputs: [{ name: "VALUE", type: Property.type }]
    outputs: []
    implementation: ST_Code
    validation: Optional[Validation_Logic]
  }

  access_level: Enum { public, protected, private }

  metadata: {
    description: Optional[String]
    unit: Optional[String]
    range: Optional[Range]
  }
} @applies_to { class, function_block, interface }
```

**并发同步机制Schema**（第6.9章）：

```dsl
schema Synchronization_Primitives {
  mutexes: List[Mutex] {
    mutex: {
      name: Identifier
      priority_ceiling: Optional[UInt8]
      owner: Optional[Task_ID]
      state: Enum { unlocked, locked }
    }
  }

  semaphores: List[Semaphore] {
    semaphore: {
      name: Identifier
      initial_count: UInt8
      max_count: UInt8
      current_count: UInt8
      waiting_queue: List[Task_ID]
    }
  }
} @standard("IEC_61131-3_2025_Section_6.9")
```

**USTRING/UCHAR类型Schema**：

```dsl
schema Unicode_String_Types {
  ustring: {
    encoding: "UTF-8"
    max_code_units: UInt32
    characters: List[Unicode_Character]
    byte_length: UInt32
  }

  uchar: {
    encoding: "UTF-8"
    code_point: UInt32  // Unicode码点
    code_units: UInt8   // UTF-8编码单元数(1-4)
  }
} @conversion_rules {
  implicit: ["CHAR_TO_WCHAR", "STRING_TO_WSTRING"],
  explicit: ["WSTRING_TO_STRING", "UCHAR_TO_CHAR"]
}
```

#### 2.1.2 厂商适配状态追踪

| 厂商 | 工具 | IEC 61131-3:2025适配状态 | 预计完成时间 | 主要限制 |
|------|------|------------------------|-------------|---------|
| **Siemens** | TIA Portal V19 | ⚠️ 适配中 | 2025-Q3 | USTRING部分支持 |
| **Siemens** | TIA Portal V20 | ✅ 计划完整支持 | 2025-Q4 | - |
| **CODESYS** | V3.5 SP20 | ⚠️ 适配中 | 2025-Q2 | Mutex/Semaphore实验性 |
| **Beckhoff** | TwinCAT 3.1.4026 | ⚠️ 适配中 | 2025-Q2 | Property支持有限 |
| **Schneider** | EcoStruxure | ⚠️ 评估中 | 2026 | - |
| **Mitsubishi** | GX Works3 | ⚠️ 评估中 | 2026 | - |

**Schema迁移建议**：

1. 新开发项目建议使用第四版Schema
2. 现有项目迁移需评估工具支持度
3. 避免使用已删除的IL语言
4. 利用Property机制封装复杂数据访问

**参考链接**：

- [IEC官方](https://webstore.iec.ch/en/publication/68533)
- [技术对比](https://stefanhenneken.net/2025/06/11/iec-61131-3-comparison-of-edition-3-and-edition-4/)

### 2.2 IEC 61499:2012

**标准名称**：Function blocks

**核心内容**：

- **分布式控制系统模型**
- **事件驱动架构**
- **功能块网络**

**与IEC 61131-3的关系**：
互补关系，IEC 61499面向分布式系统，IEC 61131-3面向单机系统。

**Schema体现**：
定义了功能块的接口和连接Schema。

**最新版本**：Edition 2.0 (2012)

**参考链接**：

- [IEC官网](https://webstore.iec.ch/publication/4553)

### 2.3 ISO/IEC 14977:1996

**标准名称**：Extended BNF

**核心内容**：
定义扩展巴科斯-瑙尔范式（EBNF），用于描述编程语言语法。

**Schema应用**：
可用于定义PLC编程语言的语法Schema。

---

## 3. 国家标准

### 3.1 GB/T 15969.3-2017

**标准名称**：
可编程序控制器 第3部分：编程语言

**核心内容**：

- **等同采用IEC 61131-3:2013**
- **XML Schema定义**：
  明确采用XML Schema定义PLC程序交互格式
- **中文术语规范**

**Schema技术实现**：
标准附录中提供了XML Schema定义文件。

**状态**：现行有效

**注意**：

- ~~GB/T 33008.1-2016~~ 是**网络安全**标准，不是编程语言标准
- 由于IEC 61131-3:2025刚发布，中国国家标准尚未更新对应版本

**参考链接**：
[国家标准全文公开系统](http://openstd.samr.gov.cn/)

### 3.2 GB/T 19582-2008

**标准名称**：基于Modbus协议的工业自动化网络规范

**核心内容**：

- **Modbus RTU协议**
- **Modbus TCP协议**
- **数据模型定义**

**Schema应用**：
定义了Modbus通信的Schema结构。

### 3.3 GB/T 20540-2006

**标准名称**：Profibus规范

**核心内容**：

- **Profibus DP协议**
- **Profibus PA协议**
- **GSD文件格式**

**Schema应用**：
GSD文件本质上是设备Schema的描述文件。

---

## 4. 行业标准

### 4.1 PLCopen

**组织**：PLCopen国际组织

**核心标准**：

#### 4.1.1 XML格式标准

- **PLCopen XML v2.01** / **IEC 61131-10:2019**：
  - 定义PLC程序的XML交换格式
  - 2019年起成为IEC国际标准
  - 提供完整的XSD Schema定义

#### 4.1.2 运动控制标准

- **PLCopen Part 1**：运动控制功能块库
- **PLCopen Part 2**：扩展运动控制
- **PLCopen Part 3**：用户指南

#### 4.1.3 安全标准

- **PLCopen Safety**：
  安全相关功能块定义

**影响**：
被主流PLC工具厂商广泛采用。

**参考链接**：
[PLCopen官网](https://www.plcopen.org/)

### 4.2 OPC Foundation

**组织**：OPC Foundation

**相关标准**：

- **OPC UA**：
  统一架构，支持信息模型Schema
- **OPC UA Companion Specifications**：
  行业特定的信息模型

**Schema应用**：
OPC UA定义了完整的信息模型Schema体系。

---

## 5. 厂商标准

### 5.1 西门子（Siemens）

**标准格式**：

- **TIA Portal项目格式**：
  基于XML的项目文件格式
- **S7程序格式**：
  支持多种程序格式

**Schema特点**：

- 完整的硬件配置Schema
- 程序组织单元Schema
- 通信配置Schema

### 5.2 施耐德（Schneider）

**标准格式**：

- **Unity Pro项目格式**
- **Modicon程序格式**

**Schema特点**：

- 支持IEC 61131-3标准
- 扩展了行业特定功能块

### 5.3 三菱（Mitsubishi）

**标准格式**：

- **GX Works项目格式**
- **MELSEC程序格式**

**Schema特点**：

- 支持IEC 61131-3标准
- 日本工业标准（JIS）兼容

---

## 6. 标准对比矩阵

### 6.1 标准对比表

| 标准类型 | 标准名称 | Schema支持 | XML格式 | 工具支持 | 成熟度 |
|---------|---------|-----------|---------|---------|-------|
| **国际标准** | IEC 61131-3:2025 | ✅ 完整 | ✅ PLCopen | ⭐⭐⭐⭐⭐ | 高 |
| **国际标准** | IEC 61499 | ✅ 完整 | ✅ 部分 | ⭐⭐⭐ | 中 |
| **国家标准** | GB/T 15969.3-2017 | ✅ 完整 | ✅ 是 | ⭐⭐⭐⭐ | 高 |
| **行业标准** | PLCopen XML v2.01 | ✅ 完整 | ✅ 是 | ⭐⭐⭐⭐⭐ | 高 |
| **行业标准** | OPC UA | ✅ 完整 | ✅ 是 | ⭐⭐⭐⭐⭐ | 高 |
| **厂商标准** | Siemens TIA | ✅ 完整 | ✅ 是 | ⭐⭐⭐⭐⭐ | 高 |
| **厂商标准** | Schneider Unity | ✅ 完整 | ⚠️ 部分 | ⭐⭐⭐⭐ | 中 |
| **厂商标准** | Mitsubishi GX | ✅ 完整 | ⚠️ 部分 | ⭐⭐⭐⭐ | 中 |
| **厂商标准** | ABB Automation | ✅ 完整 | ⚠️ 部分 | ⭐⭐⭐⭐ | 中 |
| **厂商标准** | Rockwell RSLogix | ✅ 完整 | ⚠️ 部分 | ⭐⭐⭐⭐ | 中 |

**说明**：

- ✅：完全支持
- ⚠️：部分支持
- ⭐：工具支持程度（1-5星）

### 6.2 Schema特性对比

| 标准 | 数据类型 | 程序结构 | 函数块 | 变量声明 | 扩展性 | Unicode支持 |
|------|---------|---------|--------|---------|--------|------------|
| **IEC 61131-3:2025** | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ⚠️ 有限 | ✅ USTRING |
| **IEC 61499** | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 强 | ⚠️ 部分 |
| **PLCopen XML** | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 强 | ✅ 是 |
| **OPC UA** | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ✅ 完整 | ✅ 强 | ✅ 是 |

### 6.3 工具链支持对比

| 工具 | IEC 61131-3:2025 | IEC 61499 | PLCopen XML | 代码生成 | 验证功能 |
|------|-----------------|-----------|-------------|---------|---------|
| **CODESYS** | ⚠️ 适配中 | ✅ 完整 | ✅ 完整 | ✅ 多语言 | ✅ 强 |
| **TwinCAT** | ⚠️ 适配中 | ⚠️ 部分 | ✅ 完整 | ✅ 多语言 | ✅ 强 |
| **Siemens TIA** | ⚠️ 适配中 | ❌ 无 | ⚠️ 部分 | ✅ 部分 | ✅ 强 |
| **Schneider Unity** | ⚠️ 适配中 | ❌ 无 | ⚠️ 部分 | ⚠️ 部分 | ⚠️ 中 |
| **OpenPLC** | ⚠️ 适配中 | ❌ 无 | ⚠️ 部分 | ✅ 部分 | ⚠️ 中 |

---

## 7. 标准发展趋势

### 7.1 2024-2025年趋势

#### 7.1.1 云原生支持

- **趋势**：PLC程序向云端迁移
- **影响**：需要新的Schema定义
- **标准**：IEC 61499扩展

#### 7.1.2 AI集成

- **趋势**：AI功能块集成到PLC
- **影响**：需要AI模型Schema
- **标准**：新兴标准制定中

#### 7.1.3 数字孪生

- **趋势**：PLC与数字孪生集成
- **影响**：需要同步Schema
- **标准**：IEC 63278-1:2024（数字孪生标准）

### 7.2 标准化方向

1. **统一性**：推动跨厂商Schema统一
2. **互操作性**：增强不同平台互操作
3. **可扩展性**：支持行业特定扩展
4. **安全性**：加强安全相关Schema定义
5. **国际化**：增强Unicode和多语言支持

### 7.3 2025-2026年展望

#### 7.3.1 IEC 61131-3第四版已发布

- **状态**：✅ **IEC 61131-3:2025已正式发布（2025-05-22）**
- **主要变更**：
  - IL语言正式移除
  - UTF-8字符串支持（USTRING/UCHAR）
  - 并发同步机制（Mutex/Semaphore）
  - 属性(Property)支持
- **Schema需求**：需要更新编程语言Schema以支持新特性
- **工具适配**：主流工具正在适配第四版

#### 7.3.2 边缘计算集成

- **趋势**：PLC与边缘计算深度融合
- **影响**：需要边缘计算Schema定义
- **标准**：IEC 63278边缘计算标准

#### 7.3.3 安全增强

- **趋势**：IEC 62443安全标准集成
- **影响**：需要安全认证Schema
- **标准**：IEC 62443工业网络安全

---

## 8. 参考文献

### 8.1 标准文档

- IEC 61131-3:2025 Programmable controllers - Part 3: Programming languages (Edition 4.0)
- IEC 61499-1:2012 Function blocks - Part 1: Architecture
- IEC 61131-10:2019 PLCopen XML format
- GB/T 15969.3-2017 可编程序控制器 第3部分：编程语言
- GB/T 19582-2008 基于Modbus协议的工业自动化网络规范
- GB/T 20540-2006 Profibus规范

### 8.2 在线资源

- [IEC官网](https://www.iec.ch/)
- [PLCopen官网](https://www.plcopen.org/)
- [OPC Foundation](https://opcfoundation.org/)
- [国家标准全文公开系统](http://openstd.samr.gov.cn/)
- [IEC 61131-3第四版技术对比](https://stefanhenneken.net/2025/06/11/iec-61131-3-comparison-of-edition-3-and-edition-4/)

### 8.3 学术文献

- PLC Schema形式化方法研究
- IEC 61131-3:2025标准分析与应用
- XML Schema在PLC程序交换中的应用
- IEC 61499分布式控制系统研究
- OPC UA在工业4.0中的应用

### 8.4 技术社区

- **PLCopen**：<https://www.plcopen.org/>
- **IEC官网**：<https://www.iec.ch/>
- **OPC Foundation**：<https://opcfoundation.org/>
- **CODESYS**：<https://www.codesys.com/>
- **GitHub PLC工具**：<https://github.com/PLCnext/plcnext>

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2026-02-15（对齐IEC 61131-3:2025、更新GB/T引用、更新PLCopen XML版本）

**更新说明**：

- ✅ 更新IEC 61131-3至2025第四版，详细记录主要变更
- ✅ 更正GB/T引用：GB/T 15969.3-2017为编程语言标准，GB/T 33008.1-2016为网络安全标准
- ✅ 更新PLCopen XML至v2.01 / IEC 61131-10:2019
- ✅ 添加第四版与第三版对比表
- ✅ 更新工具链支持状态（标注适配中）
