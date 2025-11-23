# EDI Schema标准对标

## 📑 目录

- [EDI Schema标准对标](#edi-schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. EDI X12标准](#2-edi-x12标准)
    - [2.1 EDI X12概述](#21-edi-x12概述)
    - [2.2 EDI X12交易集](#22-edi-x12交易集)
    - [2.3 EDI X12版本](#23-edi-x12版本)
  - [3. EDIFACT标准](#3-edifact标准)
    - [3.1 EDIFACT概述](#31-edifact概述)
    - [3.2 EDIFACT消息类型](#32-edifact消息类型)
    - [3.3 EDIFACT版本](#33-edifact版本)
  - [4. 相关标准](#4-相关标准)
    - [4.1 ISO标准](#41-iso标准)
    - [4.2 行业标准](#42-行业标准)
  - [5. 标准对比矩阵](#5-标准对比矩阵)
  - [6. 标准发展趋势](#6-标准发展趋势)

---

## 1. 标准体系概述

EDI Schema标准体系分为三个层次：

1. **EDI X12标准**：美国国家标准协会EDI X12标准
2. **EDIFACT标准**：联合国行政、商业和运输电子数据交换标准
3. **ISO标准**：国际标准化组织制定的相关标准

---

## 2. EDI X12标准

### 2.1 EDI X12概述

**标准名称**：
Electronic Data Interchange (EDI) X12 Standards

**核心内容**：

- **交易集（Transaction Sets）**：标准化的业务交易格式
- **段（Segments）**：数据段定义
- **元素（Elements）**：数据元素定义
- **交换控制结构**：ISA/GS/ST交换控制结构

**Schema支持**：完整支持

**最新版本**：EDI X12 Version 006010（持续更新）

**参考链接**：
[X12官网](https://www.x12.org/)

**标准文档**：

- EDI X12 Standards
- EDI X12 Implementation Guides
- EDI X12 Transaction Set Standards

---

### 2.2 EDI X12交易集

**常用交易集**：

| 交易集代码 | 名称 | 描述 |
|-----------|------|------|
| 850 | Purchase Order | 采购订单 |
| 855 | Purchase Order Acknowledgment | 采购订单确认 |
| 856 | Ship Notice/Manifest | 发货通知 |
| 810 | Invoice | 发票 |
| 820 | Payment Order/Remittance Advice | 汇款通知 |
| 997 | Functional Acknowledgment | 功能确认 |
| 846 | Inventory Inquiry/Advice | 库存查询/通知 |
| 940 | Warehouse Shipping Order | 仓库发货订单 |
| 945 | Warehouse Shipping Advice | 仓库发货通知 |

**Schema映射**：

```text
EDI_X12_Standard → EDI_X12_Schema
```

---

### 2.3 EDI X12版本

**版本历史**：

- **Version 004010**：2006年发布
- **Version 005010**：2012年发布
- **Version 006010**：最新版本

**版本特点**：

- 向后兼容性
- 新增交易集支持
- 增强数据验证

---

## 3. EDIFACT标准

### 3.1 EDIFACT概述

**标准名称**：
Electronic Data Interchange For Administration, Commerce and Transport (EDIFACT)

**核心内容**：

- **消息（Messages）**：标准化的业务消息格式
- **段组（Segment Groups）**：消息结构定义
- **段（Segments）**：数据段定义
- **数据元素（Data Elements）**：数据元素定义

**Schema支持**：完整支持

**最新版本**：EDIFACT D.23A（持续更新）

**参考链接**：
[UN/EDIFACT官网](https://www.unece.org/cefact/)

**标准文档**：

- UN/EDIFACT Directory
- UN/EDIFACT Syntax Rules
- UN/EDIFACT Message Implementation Guidelines

---

### 3.2 EDIFACT消息类型

**常用消息**：

| 消息代码 | 名称 | 描述 |
|---------|------|------|
| ORDERS | Purchase Order Message | 订单消息 |
| ORDRSP | Purchase Order Response Message | 订单响应消息 |
| DESADV | Despatch Advice Message | 发货通知消息 |
| INVOIC | Invoice Message | 发票消息 |
| REMADV | Remittance Advice Message | 汇款通知消息 |
| APERAK | Application Error and Acknowledgement Message | 应用错误和确认消息 |
| INVRPT | Inventory Report Message | 库存报告消息 |
| RECADV | Receiving Advice Message | 收货通知消息 |

**Schema映射**：

```text
EDIFACT_Standard → EDIFACT_Schema
```

---

### 3.3 EDIFACT版本

**版本历史**：

- **D.96A**：1996年发布
- **D.01B**：2001年发布
- **D.23A**：最新版本

**版本特点**：

- 国际化支持
- 增强消息类型
- 改进数据验证

---

## 4. 相关标准

### 4.1 ISO标准

#### ISO 9735

**标准名称**：
Electronic data interchange for administration, commerce and transport (EDIFACT) — Application level syntax rules

**核心内容**：

- EDIFACT应用级语法规则
- 消息结构定义
- 数据元素格式定义

**与EDI关系**：EDIFACT标准基于ISO 9735

**参考链接**：
[ISO官网](https://www.iso.org/)

---

#### ISO 7372

**标准名称**：
Trade data interchange — Trade data elements directory

**核心内容**：

- 贸易数据元目录
- 数据元素定义
- 数据元素格式

**与EDI关系**：EDI数据元素参考ISO 7372

---

### 4.2 行业标准

#### GS1 EDI标准

**标准名称**：
GS1 EDI Standards

**核心内容**：

- GS1 EDI消息格式
- GS1标识符集成
- 供应链EDI标准

**与EDI关系**：GS1 EDI基于EDIFACT和EDI X12

---

## 5. 标准对比矩阵

| 标准类型 | 标准名称 | 覆盖范围 | Schema支持 | 优先级 |
|---------|---------|---------|-----------|--------|
| EDI标准 | EDI X12 | 美国EDI标准 | ✅ 完整支持 | P0 |
| EDI标准 | EDIFACT | 国际EDI标准 | ✅ 完整支持 | P0 |
| ISO标准 | ISO 9735 | EDIFACT语法规则 | ✅ 参考支持 | P1 |
| ISO标准 | ISO 7372 | 贸易数据元目录 | ✅ 参考支持 | P1 |
| 行业标准 | GS1 EDI | GS1 EDI标准 | ✅ 参考支持 | P2 |

---

## 6. 标准发展趋势

### 6.1 EDI标准发展趋势

1. **数字化转型**：EDI标准向数字化转型，支持API集成
2. **云服务**：EDI标准支持云服务部署
3. **实时处理**：EDI标准支持实时消息处理
4. **安全性增强**：EDI标准增强安全性和加密支持

### 6.2 标准演进方向

1. **标准化**：EDI标准持续标准化和规范化
2. **国际化**：EDI标准向国际化方向发展
3. **智能化**：EDI标准向智能化方向发展
4. **API化**：EDI标准向RESTful API方向发展

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
