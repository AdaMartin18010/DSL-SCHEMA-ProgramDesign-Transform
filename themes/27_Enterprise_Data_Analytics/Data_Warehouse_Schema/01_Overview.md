# 数据仓库Schema概述

## 📑 目录

- [数据仓库Schema概述](#数据仓库schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 数据仓库Schema定义](#11-数据仓库schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 数据仓库Schema定义](#21-数据仓库schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. 数据仓库Schema元素](#3-数据仓库schema元素)
    - [3.1 星型模式Schema](#31-星型模式schema)
    - [3.2 雪花模式Schema](#32-雪花模式schema)
    - [3.3 Data Vault Schema](#33-data-vault-schema)
    - [3.4 数据仓库元数据Schema](#34-数据仓库元数据schema)
  - [4. 标准对标](#4-标准对标)
  - [5. 应用场景](#5-应用场景)

---

## 1. 核心结论

**企业数据仓库领域存在标准化的数据仓库Schema体系**。

### 1.1 数据仓库Schema定义

```text
Data_Warehouse_Schema = (Star_Schema ⊕ Snowflake_Schema
                         ⊕ Data_Vault_Schema ⊕ Metadata_Schema) × DW_Profile
```

### 1.2 标准依据

- **Kimball维度建模**：星型模式、雪花模式
- **Data Vault 2.0**：数据仓库建模方法
- **Inmon企业信息工厂**：规范化数据仓库

---

## 2. 概念定义

### 2.1 数据仓库Schema定义

**数据仓库Schema**是描述企业数据仓库数据结构的形式化规范，包括星型模式、雪花模式、Data Vault模式、元数据等模块。

### 2.2 核心特征

1. **标准化**：基于Kimball、Data Vault、Inmon标准
2. **可扩展性**：支持数据仓库扩展和演进
3. **历史性**：支持历史数据存储和查询
4. **形式化**：数学形式化定义

### 2.3 Schema分类

- **星型模式Schema**：事实表、维度表、维度层次
- **雪花模式Schema**：规范化维度表、维度层次结构
- **Data Vault Schema**：Hub、Link、Satellite
- **元数据Schema**：数据字典、数据血缘、数据质量

---

## 3. 数据仓库Schema元素

### 3.1 星型模式Schema

**定义**：描述Kimball星型模式的数据结构。

**包含内容**：

- **事实表（Fact Table）**：事实表名称、度量值、维度键
- **维度表（Dimension Table）**：维度表名称、维度属性、维度层次
- **维度层次（Dimension Hierarchy）**：层次结构、层次级别、层次关系

### 3.2 雪花模式Schema

**定义**：描述雪花模式的数据结构。

**包含内容**：

- **规范化维度表（Normalized Dimension Table）**：规范化维度表结构
- **维度层次结构（Dimension Hierarchy Structure）**：多级维度层次
- **维度关系（Dimension Relationship）**：维度表之间的关联关系

### 3.3 Data Vault Schema

**定义**：描述Data Vault模式的数据结构。

**包含内容**：

- **Hub（中心表）**：业务键、Hub名称、加载时间戳
- **Link（链接表）**：关联关系、Link名称、加载时间戳
- **Satellite（卫星表）**：描述性属性、Satellite名称、加载时间戳、有效期间

### 3.4 数据仓库元数据Schema

**定义**：描述数据仓库元数据的数据结构。

**包含内容**：

- **数据字典（Data Dictionary）**：表定义、字段定义、数据类型
- **数据血缘（Data Lineage）**：数据来源、数据流向、数据转换
- **数据质量（Data Quality）**：质量指标、质量检查、质量报告

---

## 4. 标准对标

### 4.1 Kimball维度建模标准

- **Kimball维度建模**：星型模式、雪花模式
  - 事实表、维度表、维度层次

### 4.2 Data Vault标准

- **Data Vault 2.0**：数据仓库建模方法
  - Hub、Link、Satellite、加载时间戳

### 4.3 Inmon企业信息工厂标准

- **Inmon企业信息工厂**：规范化数据仓库
  - 规范化数据模型、数据仓库架构

---

## 5. 应用场景

### 5.1 数据仓库设计

- 星型模式设计：基于Kimball方法设计星型模式数据仓库
- Data Vault设计：基于Data Vault方法设计数据仓库
- 混合模式设计：结合多种模式设计数据仓库

### 5.2 数据仓库实施

- ETL开发：开发数据提取、转换、加载流程
- 数据质量：实施数据质量监控和改进
- 性能优化：优化数据仓库查询性能

### 5.3 数据仓库应用

- 报表生成：基于数据仓库生成业务报表
- OLAP分析：基于数据仓库进行OLAP分析
- 数据挖掘：基于数据仓库进行数据挖掘

---

**参考文档**：

- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
