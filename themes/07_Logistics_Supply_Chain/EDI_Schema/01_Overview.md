# EDI Schema概述

## 📑 目录

- [EDI Schema概述](#edi-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 EDI Schema定义](#11-edi-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 EDI Schema定义](#21-edi-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. EDI标准Schema](#3-edi标准schema)
    - [3.1 EDI X12 Schema](#31-edi-x12-schema)
    - [3.2 EDIFACT Schema](#32-edifact-schema)
    - [3.3 EDI消息类型](#33-edi消息类型)
  - [4. 标准对标](#4-标准对标)
    - [4.1 EDI标准](#41-edi标准)
    - [4.2 相关标准](#42-相关标准)
  - [5. 应用场景](#5-应用场景)
    - [5.1 供应链管理](#51-供应链管理)
    - [5.2 物流管理](#52-物流管理)
    - [5.3 订单处理](#53-订单处理)
    - [5.4 EDI数据存储与分析](#54-edi数据存储与分析)
  - [6. 思维导图](#6-思维导图)

---

## 1. 核心结论

**物流供应链存在强制性的EDI Schema体系**。

### 1.1 EDI Schema定义

```text
EDI_Schema = (EDI_X12 ⊕ EDIFACT) × Business_Profile
```

### 1.2 标准依据

- **EDI X12**：美国国家标准协会EDI X12标准
- **EDIFACT**：联合国EDI标准（Electronic Data Interchange For Administration, Commerce and Transport）
- **ANSI X12**：美国国家标准协会X12标准
- **UN/EDIFACT**：联合国行政、商业和运输电子数据交换标准

---

## 2. 概念定义

### 2.1 EDI Schema定义

**EDI Schema**是描述电子数据交换（Electronic Data Interchange）
的形式化规范，包括EDI X12、EDIFACT等标准格式。

### 2.2 核心特征

1. **标准化**：基于EDI X12、EDIFACT等国际标准
2. **结构化**：标准化的消息结构和数据格式
3. **互操作性**：支持不同系统间的数据交换
4. **形式化**：数学形式化定义

### 2.3 Schema分类

- **EDI X12 Schema**：美国EDI X12标准
- **EDIFACT Schema**：联合国EDIFACT标准

---

## 3. EDI标准Schema

### 3.1 EDI X12 Schema

**定义**：描述EDI X12标准的数据结构。

**包含内容**：

- **交易集（Transaction Sets）**：850（采购订单）、855（采购订单确认）、856（发货通知）、810（发票）等
- **段（Segments）**：ST（交易集头）、SE（交易集尾）、BEG（开始段）、N1（名称段）等
- **元素（Elements）**：数据元素定义和格式

**常用交易集**：

- **850**：采购订单（Purchase Order）
- **855**：采购订单确认（Purchase Order Acknowledgment）
- **856**：发货通知（Ship Notice/Manifest）
- **810**：发票（Invoice）
- **997**：功能确认（Functional Acknowledgment）

### 3.2 EDIFACT Schema

**定义**：描述EDIFACT标准的数据结构。

**包含内容**：

- **消息（Messages）**：ORDERS（订单）、DESADV（发货通知）、INVOIC（发票）等
- **段组（Segment Groups）**：消息结构定义
- **段（Segments）**：UNH（消息头）、UNT（消息尾）、BGM（开始消息段）等
- **数据元素（Data Elements）**：数据元素定义和格式

**常用消息**：

- **ORDERS**：订单（Purchase Order Message）
- **DESADV**：发货通知（Despatch Advice Message）
- **INVOIC**：发票（Invoice Message）
- **APERAK**：应用错误和确认（Application Error and Acknowledgement Message）

### 3.3 EDI消息类型

**订单处理流程**：

1. **850/ORDERS**：采购订单
2. **855/ORDERS**：采购订单确认
3. **856/DESADV**：发货通知
4. **810/INVOIC**：发票
5. **820/REMADV**：汇款通知

---

## 4. 标准对标

### 4.1 EDI标准

- **EDI X12标准**：美国国家标准协会EDI X12标准
- **EDIFACT标准**：联合国行政、商业和运输电子数据交换标准
- **ANSI X12标准**：美国国家标准协会X12标准
- **UN/EDIFACT标准**：联合国EDIFACT标准

### 4.2 相关标准

- **ISO 9735**：EDIFACT应用级语法规则
- **ISO 7372**：贸易数据元目录
- **GS1 EDI标准**：GS1 EDI标准

---

## 5. 应用场景

### 5.1 供应链管理

- 订单管理
- 库存管理
- 供应商管理

### 5.2 物流管理

- 发货通知
- 运输管理
- 配送管理

### 5.3 订单处理

- 订单接收
- 订单确认
- 订单履行

### 5.4 EDI数据存储与分析

**数据库存储应用场景**：

- **PostgreSQL EDI数据存储**：
  - EDI消息存储（消息头、消息体、消息尾）
  - EDI交易集存储（交易集头、交易集尾、段数据）
  - EDI段存储（段标识、段数据、段位置）
  - EDI元素存储（元素标识、元素值、元素格式）
  - EDI统计信息存储（消息统计、交易集统计、错误统计）

**应用价值**：

- 高效存储大规模EDI消息和交易数据
- 支持供应链数据分析和报表生成
- 提供EDI消息追溯和审计功能
- 支持EDI数据挖掘和分析

---

## 6. 思维导图

```text
EDI Schema
│
├─ EDI X12（美国标准）
│   ├─ 交易集（Transaction Sets）
│   │   ├─ 850（采购订单）
│   │   ├─ 855（采购订单确认）
│   │   ├─ 856（发货通知）
│   │   ├─ 810（发票）
│   │   └─ 997（功能确认）
│   ├─ 段（Segments）
│   │   ├─ ST（交易集头）
│   │   ├─ SE（交易集尾）
│   │   ├─ BEG（开始段）
│   │   └─ N1（名称段）
│   └─ 元素（Elements）
│
└─ EDIFACT（联合国标准）
    ├─ 消息（Messages）
    │   ├─ ORDERS（订单）
    │   ├─ DESADV（发货通知）
    │   ├─ INVOIC（发票）
    │   └─ APERAK（应用错误和确认）
    ├─ 段组（Segment Groups）
    ├─ 段（Segments）
    │   ├─ UNH（消息头）
    │   ├─ UNT（消息尾）
    │   └─ BGM（开始消息段）
    └─ 数据元素（Data Elements）
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标

**创建时间**：2025-01-21
**最后更新**：2025-01-21

