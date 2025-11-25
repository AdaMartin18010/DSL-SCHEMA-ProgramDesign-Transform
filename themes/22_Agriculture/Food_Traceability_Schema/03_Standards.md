# 农产品追溯Schema标准对标

## 📑 目录

- [农产品追溯Schema标准对标](#农产品追溯schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. GS1标准](#2-gs1标准)
    - [2.1 GS1概述](#21-gs1概述)
  - [3. EPCIS标准](#3-epcis标准)
    - [3.1 EPCIS概述](#31-epcis概述)
  - [4. ISO 22005标准](#4-iso-22005标准)
    - [4.1 ISO 22005概述](#41-iso-22005概述)
  - [5. 标准对比矩阵](#5-标准对比矩阵)

---

## 1. 标准体系概述

农产品追溯Schema标准体系分为三个层次：

1. **GS1标准**：全球标准1标准
2. **EPCIS标准**：EPC信息服务
3. **ISO 22005标准**：饲料和食品链的可追溯性

---

## 2. GS1标准

### 2.1 GS1概述

**标准名称**：Global Standards 1 (GS1)

**核心内容**：

- **GTIN**：全球贸易项目代码
- **GLN**：全球位置码
- **EPCIS**：EPC信息服务

**Schema支持**：完整支持

**参考链接**：[GS1官网](https://www.gs1.org/)

---

## 3. EPCIS标准

### 3.1 EPCIS概述

**标准名称**：EPC Information Services (EPCIS)

**核心内容**：

- **事件类型**：ObjectEvent、AggregationEvent、TransactionEvent、TransformationEvent
- **追溯事件**：生产、加工、运输、存储、零售事件

**Schema支持**：完整支持

---

## 4. ISO 22005标准

### 4.1 ISO 22005概述

**标准名称**：Traceability in the feed and food chain

**核心内容**：

- **追溯系统**：饲料和食品链追溯系统
- **追溯要求**：追溯系统要求和验证

**Schema支持**：完整支持

---

## 5. 标准对比矩阵

| 标准 | 应用领域 | 数据格式 | Schema支持 |
|------|---------|---------|-----------|
| **GS1** | 产品标识 | GTIN、GLN | ✅ 完整支持 |
| **EPCIS** | 追溯事件 | XML、JSON | ✅ 完整支持 |
| **ISO 22005** | 追溯系统 | 文档 | ✅ 完整支持 |

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
