# IEC61850 Schema概述

## 📑 目录

- [IEC61850 Schema概述](#iec61850-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 IEC61850 Schema定义](#11-iec61850-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 IEC61850 Schema定义](#21-iec61850-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. IEC61850要素Schema](#3-iec61850要素schema)
    - [3.1 逻辑节点Schema](#31-逻辑节点schema)
    - [3.2 数据对象Schema](#32-数据对象schema)
    - [3.3 服务Schema](#33-服务schema)
  - [4. 标准对标](#4-标准对标)
    - [4.1 国际标准](#41-国际标准)
    - [4.2 行业标准](#42-行业标准)
  - [5. 应用场景](#5-应用场景)
    - [5.1 变电站自动化](#51-变电站自动化)
    - [5.2 智能电网管理](#52-智能电网管理)
    - [5.3 电力设备监控](#53-电力设备监控)
    - [5.4 IEC61850数据存储与分析](#54-iec61850数据存储与分析)
  - [6. 思维导图](#6-思维导图)

---

## 1. 核心结论

**电力系统存在标准化的IEC61850 Schema体系**。

### 1.1 IEC61850 Schema定义

```text
IEC61850_Schema = (Logical_Node_Schema ⊕ Data_Object_Schema
                  ⊕ Service_Schema ⊕ SCL_Schema) × IEC61850_Profile
```

### 1.2 标准依据

- **IEC 61850**：变电站通信网络和系统标准
- **IEC 61970**：能源管理系统应用程序接口标准
- **IEC 61968**：配电管理系统接口标准

---

## 2. 概念定义

### 2.1 IEC61850 Schema定义

**IEC61850 Schema**是描述电力系统
数据结构的形式化规范，包括逻辑节点、数据对象、
服务、SCL配置等。

### 2.2 核心特征

1. **标准化**：基于IEC 61850等国际标准
2. **互操作性**：支持不同厂商设备互操作
3. **实时性**：支持实时数据采集和控制
4. **形式化**：数学形式化定义
5. **可扩展性**：支持自定义逻辑节点和数据对象

### 2.3 Schema分类

- **逻辑节点Schema**：逻辑节点定义、逻辑节点类型
- **数据对象Schema**：数据对象定义、数据属性定义
- **服务Schema**：MMS服务、GOOSE服务、SMV服务
- **SCL Schema**：系统配置语言、IED配置、通信配置

---

## 3. IEC61850要素Schema

### 3.1 逻辑节点Schema

**定义**：描述逻辑节点的数据结构。

**核心要素**：

- **逻辑节点类**：LNClass（如XCBR、MMXU、PTRC）
- **逻辑节点实例**：LNInstance（如XCBR1、MMXU1）
- **逻辑节点名称**：LNName（如XCBR1、MMXU1）
- **逻辑节点描述**：Desc（逻辑节点描述信息）

### 3.2 数据对象Schema

**定义**：描述数据对象的数据结构。

**核心要素**：

- **数据对象类**：DOClass（如Pos、St、Op）
- **数据对象实例**：DOInstance（如Pos、St、Op）
- **数据属性**：DA（如Pos.stVal、St.stVal）
- **数据属性类型**：DAType（如BOOLEAN、INT32、FLOAT32）

### 3.3 服务Schema

**定义**：描述IEC61850服务的结构。

**核心要素**：

- **MMS服务**：Manufacturing Message Specification服务
- **GOOSE服务**：Generic Object Oriented Substation Event
- **SMV服务**：Sampled Measured Values
- **服务接口**：Service Interface（如GetDirectory、Read、Write）

---

## 4. 标准对标

### 4.1 国际标准

- **IEC 61850**：变电站通信网络和系统标准
  - Part 6：配置描述语言
  - Part 7-1：基本通信结构
  - Part 7-2：抽象通信服务接口
  - Part 7-3：公共数据类
  - Part 7-4：兼容逻辑节点类和数据类
- **IEC 61970**：能源管理系统应用程序接口标准
- **IEC 61968**：配电管理系统接口标准

### 4.2 行业标准

- **IEEE 1547**：分布式资源与电力系统互连标准
- **IEC 61400**：风力发电机组标准
- **IEC 61727**：光伏系统并网标准

---

## 5. 应用场景

### 5.1 变电站自动化

**应用场景**：
使用IEC61850标准实现变电站自动化，
包括设备监控、保护控制、数据采集等。

**技术要点**：

- 逻辑节点建模
- GOOSE通信
- SMV采样值传输
- SCL配置管理

### 5.2 智能电网管理

**应用场景**：
使用IEC61850标准实现智能电网管理，
包括电网监控、负荷管理、故障诊断等。

**技术要点**：

- 数据模型标准化
- 服务接口标准化
- 实时数据采集
- 历史数据分析

### 5.3 电力设备监控

**应用场景**：
使用IEC61850标准实现电力设备监控，
包括设备状态监测、故障预警、维护管理等。

**技术要点**：

- 设备数据模型
- 状态监测数据
- 故障诊断算法
- 维护计划管理

### 5.4 IEC61850数据存储与分析

**应用场景**：
使用PostgreSQL存储IEC61850数据，
支持数据查询、分析和报表生成。

**技术要点**：

- 逻辑节点数据存储
- 数据对象数据存储
- 服务调用记录存储
- 数据分析和报表

---

## 6. 思维导图

```text
IEC61850_Schema
├── Logical_Node_Schema
│   ├── LNClass
│   ├── LNInstance
│   └── LNName
├── Data_Object_Schema
│   ├── DOClass
│   ├── DOInstance
│   └── DA
├── Service_Schema
│   ├── MMS_Service
│   ├── GOOSE_Service
│   └── SMV_Service
└── SCL_Schema
    ├── IED_Config
    ├── Communication_Config
    └── Data_Model_Config
```

---

**参考文档**：

- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
