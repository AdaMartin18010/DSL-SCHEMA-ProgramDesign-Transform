# CAD Schema标准对标

## 📑 目录

- [CAD Schema标准对标](#cad-schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. ISO 10303 (STEP)标准](#2-iso-10303-step标准)
    - [2.1 STEP概述](#21-step概述)
    - [2.2 主要应用协议](#22-主要应用协议)
      - [AP 203: Configuration Controlled Design](#ap-203-configuration-controlled-design)
      - [AP 214: Core Data for Automotive Mechanical Design Process](#ap-214-core-data-for-automotive-mechanical-design-process)
      - [AP 242: Managed Model Based 3D Engineering](#ap-242-managed-model-based-3d-engineering)
      - [AP 238: Application Interpreted Model for Computerized Numerical Controllers](#ap-238-application-interpreted-model-for-computerized-numerical-controllers)
  - [3. ISO 14649 (STEP-NC)标准](#3-iso-14649-step-nc标准)
  - [4. ISO 16792 (MBD)标准](#4-iso-16792-mbd标准)
  - [5. 其他CAD相关标准](#5-其他cad相关标准)
    - [5.1 ISO 13584 (零件库)](#51-iso-13584-零件库)
    - [5.2 ISO 22745 (技术词典)](#52-iso-22745-技术词典)
    - [5.3 ISO 6983 (G-Code)](#53-iso-6983-g-code)
  - [6. 国家标准](#6-国家标准)
    - [6.1 GB/T 16656](#61-gbt-16656)
    - [6.2 GB/T 24734](#62-gbt-24734)
    - [6.3 GB/T 26099](#63-gbt-26099)
  - [7. 标准对比矩阵](#7-标准对比矩阵)
  - [8. 标准发展趋势](#8-标准发展趋势)
    - [8.1 2024-2025年趋势](#81-2024-2025年趋势)
      - [8.1.1 基于模型的定义（MBD）](#811-基于模型的定义mbd)
      - [8.1.2 数字孪生集成](#812-数字孪生集成)
      - [8.1.3 增材制造支持](#813-增材制造支持)
    - [8.2 2025-2026年展望](#82-2025-2026年展望)
      - [8.2.1 AI辅助设计](#821-ai辅助设计)
      - [8.2.2 云原生CAD](#822-云原生cad)

---

## 1. 标准体系概述

CAD Schema标准体系分为四个层次：

1. **国际标准**：ISO STEP系列标准
2. **国家标准**：GB/T等同采用ISO标准
3. **行业标准**：各行业CAD标准
4. **厂商标准**：CAD软件厂商标准

---

## 2. ISO 10303 (STEP)标准

### 2.1 STEP概述

**标准名称**：
Industrial automation systems and integration — Product data representation and exchange

**核心内容**：

- **产品数据模型**：完整的产品数据表示
- **几何表示**：ISO 10303-42几何和拓扑表示
- **材料属性**：材料属性和特性
- **公差标注**：几何公差和尺寸公差
- **产品结构**：产品配置和结构

**Schema支持**：完整支持

**最新版本**：ISO 10303:2021

**参考链接**：
[ISO官网](https://www.iso.org/)

### 2.2 主要应用协议

#### AP 203: Configuration Controlled Design

**应用领域**：配置控制设计

**核心内容**：

- 3D几何模型
- 产品结构
- 配置管理
- 版本控制

**Schema支持**：完整支持

#### AP 214: Core Data for Automotive Mechanical Design Process

**应用领域**：汽车机械设计

**核心内容**：

- 汽车零部件设计
- 装配关系
- 材料属性
- 表面处理

**Schema支持**：完整支持

#### AP 242: Managed Model Based 3D Engineering

**应用领域**：基于模型的定义（MBD）

**核心内容**：

- 3D模型
- PMI（产品制造信息）
- 标注和公差
- 语义标注

**Schema支持**：完整支持

**最新版本**：ISO 10303-242:2020

#### AP 238: Application Interpreted Model for Computerized Numerical Controllers

**应用领域**：CNC数控

**核心内容**：

- 加工特征
- 刀具路径
- 加工参数
- NC程序

**Schema支持**：完整支持

---

## 3. ISO 14649 (STEP-NC)标准

**标准名称**：
Industrial automation systems and integration — Physical device control — Data model for computerized numerical controllers

**核心内容**：

- **加工特征**：加工特征定义
- **加工操作**：加工操作定义
- **刀具定义**：刀具和刀具路径
- **NC程序**：NC程序生成

**Schema支持**：完整支持

**最新版本**：ISO 14649:2023

**参考链接**：
[ISO官网](https://www.iso.org/)

---

## 4. ISO 16792 (MBD)标准

**标准名称**：
Technical product documentation — Digital product definition data practices

**核心内容**：

- **3D模型**：3D模型作为主定义
- **PMI**：产品制造信息
- **标注**：尺寸、公差、表面粗糙度
- **语义标注**：语义化标注

**Schema支持**：完整支持

**最新版本**：ISO 16792:2021

**参考链接**：
[ISO官网](https://www.iso.org/)

---

## 5. 其他CAD相关标准

### 5.1 ISO 13584 (零件库)

**标准名称**：
Industrial automation systems and integration — Parts library

**核心内容**：

- **零件库**：标准零件库定义
- **特征类**：零件特征类和属性
- **目录系统**：零件目录系统

**Schema支持**：完整支持

### 5.2 ISO 22745 (技术词典)

**标准名称**：
Industrial automation systems and integration — Open technical dictionaries and their application to master data

**核心内容**：

- **技术词典**：开放技术词典
- **术语定义**：术语和定义
- **主数据**：主数据管理

**Schema支持**：完整支持

### 5.3 ISO 6983 (G-Code)

**标准名称**：
Numerical control of machines — Program format and definition of address words

**核心内容**：

- **G-Code格式**：NC程序格式
- **地址字**：地址字定义
- **程序结构**：程序结构定义

**Schema支持**：基本支持

---

## 6. 国家标准

### 6.1 GB/T 16656

**标准名称**：
产品数据交换标准（等同ISO 10303）

**核心内容**：

- 等同采用ISO 10303标准
- 产品数据表示和交换
- 几何和拓扑表示

**Schema支持**：完整支持

### 6.2 GB/T 24734

**标准名称**：
技术产品文件数字化产品定义数据通则

**核心内容**：

- 数字化产品定义
- 3D模型定义
- PMI定义

**Schema支持**：完整支持

### 6.3 GB/T 26099

**标准名称**：
机械产品数字化定义规范

**核心内容**：

- 机械产品数字化定义
- 设计规范
- 制造规范

**Schema支持**：完整支持

---

## 7. 标准对比矩阵

| 标准 | 组织 | Schema支持 | 几何模型 | 结构设计 | 机构设计 | 装配 | 工程图 | 应用场景 |
|------|------|-----------|---------|---------|---------|------|--------|---------|
| **ISO 10303-242** | ISO | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ✅ | ✅ | ✅ | MBD |
| **ISO 10303-203** | ISO | ⭐⭐⭐⭐⭐ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ | 配置控制 |
| **ISO 10303-214** | ISO | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ✅ | ✅ | ✅ | 汽车设计 |
| **ISO 14649** | ISO | ⭐⭐⭐⭐ | ✅ | ❌ | ❌ | ✅ | ❌ | 数控编程 |
| **ISO 16792** | ISO | ⭐⭐⭐⭐⭐ | ✅ | ❌ | ❌ | ❌ | ✅ | MBD |
| **GB/T 16656** | 中国 | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ✅ | ✅ | ✅ | 产品数据交换 |

**说明**：

- ✅：完全支持
- ⚠️：部分支持
- ❌：不支持

---

## 8. 标准发展趋势

### 8.1 2024-2025年趋势

#### 8.1.1 基于模型的定义（MBD）

- **趋势**：从2D图纸向3D模型转变
- **影响**：需要完整的MBD Schema定义
- **标准**：ISO 10303-242、ISO 16792

#### 8.1.2 数字孪生集成

- **趋势**：CAD数据与数字孪生集成
- **影响**：需要实时数据同步Schema
- **标准**：IEC 63278数字孪生标准

#### 8.1.3 增材制造支持

- **趋势**：3D打印和增材制造标准完善
- **影响**：需要增材制造Schema定义
- **标准**：ISO/ASTM 52900

### 8.2 2025-2026年展望

#### 8.2.1 AI辅助设计

- **趋势**：AI辅助CAD设计
- **影响**：需要AI可理解的Schema定义
- **标准**：新兴标准制定中

#### 8.2.2 云原生CAD

- **趋势**：CAD系统云化
- **影响**：需要云原生数据格式
- **标准**：新兴标准制定中

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
