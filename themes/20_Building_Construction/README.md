# 建筑与施工Schema主题

## 📑 目录

- [建筑与施工Schema主题](#建筑与施工schema主题)
  - [📑 目录](#-目录)
  - [1. 主题概述](#1-主题概述)
    - [1.1 主题范围](#11-主题范围)
    - [1.2 核心价值](#12-核心价值)
  - [2. 核心概念](#2-核心概念)
    - [2.1 Schema定义](#21-schema定义)
    - [2.2 建筑信息模型结构](#22-建筑信息模型结构)
  - [3. 子主题结构](#3-子主题结构)
    - [3.1 BIM Schema子主题](#31-bim-schema子主题)
  - [4. 标准对标](#4-标准对标)
    - [4.1 国际标准](#41-国际标准)
    - [4.2 行业标准](#42-行业标准)
  - [5. 应用场景](#5-应用场景)

---

## 1. 主题概述

建筑与施工Schema主题涵盖**建筑信息模型（BIM）**的标准化Schema体系，是建筑设计、施工管理和运维管理的基础。

### 1.1 主题范围

- **BIM Schema**：建筑信息模型Schema，包括建筑设计、施工管理、运维管理、IFC数据

### 1.2 核心价值

- **标准化**：基于ISO 16739、ISO/IEC 19650等国际标准
- **全生命周期**：支持建筑设计、施工、运维全生命周期管理
- **形式化**：数学形式化定义
- **互操作性**：支持IFC数据交换和互操作

---

## 2. 核心概念

### 2.1 Schema定义

**建筑与施工Schema**定义为：
**描述建筑信息模型的形式化规范**。

### 2.2 建筑信息模型结构

```text
BIM_Schema = (Design_Schema ⊕ Construction_Schema ⊕ Operation_Schema
            ⊕ IFC_Data_Schema) × BIM_Profile
```

---

## 3. 子主题结构

### 3.1 BIM Schema子主题

- `BIM_Schema/01_Overview.md` - 概述与核心概念
- `BIM_Schema/02_Formal_Definition.md` - 形式化定义
- `BIM_Schema/03_Standards.md` - 标准对标
- `BIM_Schema/04_Transformation.md` - 转换体系
- `BIM_Schema/05_Case_Studies.md` - 实践案例

---

## 4. 标准对标

### 4.1 国际标准

- **ISO 16739**：工业基础类（IFC）数据共享标准
- **ISO/IEC 19650**：建筑和土木工程信息组织和数字化标准
- **ISO 12006**：建筑信息分类标准

### 4.2 行业标准

- **gbXML**：绿色建筑XML标准
- **COBie**：建筑运营信息交换标准
- **IFC**：工业基础类标准

---

## 5. 应用场景

- 建筑设计
- 施工管理
- 运维管理
- BIM数据存储与分析
- 建筑信息交换

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21

**相关文档**：

- `../README.md` - 主题总览
- `../DOCUMENT_INDEX.md` - 完整文档索引

**统一逻辑框架**：

- `../../structure/FRAMEWORK_QUICK_START.md` ⭐推荐 - 快速入门指南
- `../../structure/UNIFIED_LOGIC_FRAMEWORK.md` - 统一逻辑框架与形式理论
- `../../structure/GLOBAL_THEME_RELATIONSHIP_ANALYSIS.md` - 全局主题关系梳理
- `../../PROJECT_DIRECTORY_INTEGRATION.md` ⭐新增 - 三大目录整合说明
- `../../PROJECT_NAVIGATION.md` ⭐新增 - 项目全局导航地图
