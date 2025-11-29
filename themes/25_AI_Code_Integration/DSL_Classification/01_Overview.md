# DSL分类与典型示例概述

## 📑 目录

- [DSL分类与典型示例概述](#dsl分类与典型示例概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 DSL分类定义](#11-dsl分类定义)
  - [2. DSL分类体系](#2-dsl分类体系)
    - [2.1 按应用领域分类](#21-按应用领域分类)
    - [2.2 按实现方式分类](#22-按实现方式分类)
    - [2.3 按语法形式分类](#23-按语法形式分类)
  - [3. 典型示例](#3-典型示例)
    - [3.1 配置DSL](#31-配置dsl)
    - [3.2 查询DSL](#32-查询dsl)
    - [3.3 建模DSL](#33-建模dsl)
    - [3.4 领域DSL](#34-领域dsl)
  - [4. 应用场景](#4-应用场景)

---

## 1. 核心结论

**DSL存在系统化的分类体系，各类型DSL都有典型示例和最佳实践**。

### 1.1 DSL分类定义

```text
DSL_Classification = (Application_Domain_DSL ⊕ Configuration_DSL
                     ⊕ Query_DSL ⊕ Modeling_DSL) × DSL_Profile
```

---

## 2. DSL分类体系

### 2.1 按应用领域分类

- **领域特定语言（Domain-Specific Language）**：针对特定领域的语言
- **配置语言（Configuration Language）**：用于配置系统的语言
- **查询语言（Query Language）**：用于数据查询的语言
- **建模语言（Modeling Language）**：用于系统建模的语言

### 2.2 按实现方式分类

- **外部DSL（External DSL）**：独立于宿主语言的DSL
- **内部DSL（Internal DSL）**：嵌入在宿主语言中的DSL
- **混合DSL（Hybrid DSL）**：结合外部和内部DSL的特点

### 2.3 按语法形式分类

- **文本DSL**：基于文本的DSL
- **图形DSL**：基于图形的DSL
- **表格DSL**：基于表格的DSL

---

## 3. 典型示例

### 3.1 配置DSL

- **YAML**：YAML Ain't Markup Language
- **JSON Schema**：JSON数据验证规范
- **TOML**：Tom's Obvious Minimal Language

### 3.2 查询DSL

- **SQL**：结构化查询语言
- **GraphQL**：Graph查询语言
- **SPARQL**：SPARQL Protocol and RDF Query Language

### 3.3 建模DSL

- **UML**：统一建模语言
- **BPMN**：业务流程建模符号
- **SysML**：系统建模语言

### 3.4 领域DSL

- **EDIFACT**：电子数据交换标准
- **HL7**：医疗信息交换标准
- **SWIFT**：金融报文标准

---

## 4. 应用场景

- 系统配置管理
- 数据查询和分析
- 系统建模和设计
- 领域特定应用

---

**参考文档**：

- `02_Formal_Definition.md` - 分类体系
- `03_Standards.md` - 典型示例
- `04_Transformation.md` - 最佳实践
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
