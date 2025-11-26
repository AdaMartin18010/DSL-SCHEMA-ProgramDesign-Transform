# XBRL Schema概述

## 📑 目录

- [XBRL Schema概述](#xbrl-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 XBRL Schema定义](#11-xbrl-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 XBRL Schema定义](#21-xbrl-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. XBRL Schema元素](#3-xbrl-schema元素)
    - [3.1 XBRL分类标准Schema](#31-xbrl分类标准schema)
    - [3.2 XBRL实例文档Schema](#32-xbrl实例文档schema)
    - [3.3 XBRL链接库Schema](#33-xbrl链接库schema)
  - [4. 标准对标](#4-标准对标)
  - [5. 应用场景](#5-应用场景)

---

## 1. 核心结论

**企业财务报告领域存在标准化的XBRL Schema体系**。

### 1.1 XBRL Schema定义

```text
XBRL_Schema = (Taxonomy ⊕ Instance_Document ⊕ Linkbases) × XBRL_Profile
```

### 1.2 标准依据

- **XBRL 2.1**：XBRL核心规范
- **XBRL GL**：XBRL全球账本
- **IFRS Taxonomy**：IFRS分类标准

---

## 2. 概念定义

### 2.1 XBRL Schema定义

**XBRL Schema**是描述可扩展商业报告语言（XBRL）数据结构的形式化规范，包括分类标准、实例文档、链接库等模块。

### 2.2 核心特征

1. **标准化**：基于XBRL 2.1、XBRL GL、IFRS Taxonomy标准
2. **可扩展性**：支持自定义分类标准
3. **可验证性**：支持XBRL验证
4. **形式化**：数学形式化定义

### 2.3 Schema分类

- **分类标准Schema**：分类元素、链接库、标签、引用
- **实例文档Schema**：上下文元素、单位元素、事实元素、脚注元素
- **链接库Schema**：标签链接库、引用链接库、计算链接库、定义链接库、展示链接库

---

## 3. XBRL Schema元素

### 3.1 XBRL分类标准Schema

**定义**：描述XBRL分类标准的数据结构。

**包含内容**：

- **分类元素（Taxonomy Element）**：元素代码、元素名称、元素类型、元素属性
- **链接库（Linkbase）**：标签链接库、引用链接库、计算链接库、定义链接库、展示链接库
- **标签（Label）**：标签语言、标签文本、标签角色
- **引用（Reference）**：引用标准、引用章节、引用段落

### 3.2 XBRL实例文档Schema

**定义**：描述XBRL实例文档的数据结构。

**包含内容**：

- **上下文元素（Context Element）**：实体标识符、期间、场景
- **单位元素（Unit Element）**：度量单位、货币单位
- **事实元素（Fact Element）**：事实值、上下文引用、单位引用
- **脚注元素（Footnote Element）**：脚注文本、脚注链接

### 3.3 XBRL链接库Schema

**定义**：描述XBRL链接库的数据结构。

**包含内容**：

- **标签链接库（Label Linkbase）**：元素标签、标签语言、标签角色
- **引用链接库（Reference Linkbase）**：元素引用、引用标准、引用章节
- **计算链接库（Calculation Linkbase）**：计算关系、计算权重、计算顺序
- **定义链接库（Definition Linkbase）**：定义关系、定义角色
- **展示链接库（Presentation Linkbase）**：展示关系、展示顺序、展示标签

---

## 4. 标准对标

### 4.1 XBRL核心规范

- **XBRL 2.1**：XBRL核心规范
  - 实例文档结构、分类标准结构、链接库结构

### 4.2 XBRL全球账本

- **XBRL GL**：XBRL全球账本
  - 总账数据的XBRL表示、多币种支持、多会计准则支持

### 4.3 IFRS分类标准

- **IFRS Taxonomy**：IFRS分类标准
  - IFRS财务报表元素的XBRL表示、支持IFRS 18等最新标准

---

## 5. 应用场景

### 5.1 财务报告标准化

- 标准化财务报告：基于XBRL生成标准化财务报告
- 监管报告：向监管机构提交XBRL格式的财务报告
- 财务数据交换：企业间财务数据交换

### 5.2 财务报告验证

- XBRL验证：验证XBRL实例文档的正确性
- 分类标准验证：验证分类标准的正确性
- 链接库验证：验证链接库的正确性

### 5.3 财务报告分析

- 财务数据分析：基于XBRL数据进行财务分析
- 财务报告对比：对比不同企业的财务报告
- 财务报告挖掘：挖掘财务报告中的信息

---

**参考文档**：

- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
