# 数据库Schema标准对标

## 📑 目录

- [数据库Schema标准对标](#数据库schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. SQL标准](#2-sql标准)
    - [2.1 SQL:2016](#21-sql2016)
    - [2.2 SQL:2011](#22-sql2011)
    - [2.3 SQL:2008](#23-sql2008)
  - [3. SQLite标准](#3-sqlite标准)
  - [4. PostgreSQL标准](#4-postgresql标准)
  - [5. 其他数据库标准](#5-其他数据库标准)
  - [6. 标准对比矩阵](#6-标准对比矩阵)

---

## 1. 标准体系概述

数据库Schema标准体系分为三个层次：

1. **国际标准**：ISO/IEC SQL标准
2. **实现标准**：SQLite、PostgreSQL等
3. **扩展标准**：PostGIS、TimescaleDB等

---

## 2. SQL标准

### 2.1 SQL:2016

**标准名称**：ISO/IEC 9075:2016

**核心内容**：

- **数据类型**：标准SQL数据类型
- **DDL**：数据定义语言
- **DML**：数据操作语言
- **DCL**：数据控制语言
- **JSON支持**：JSON数据类型和函数

**Schema支持**：完整支持

**状态**：ISO/IEC标准

### 2.2 SQL:2011

**标准名称**：ISO/IEC 9075:2011

**核心内容**：

- **时态表**：时态数据支持
- **窗口函数**：窗口函数增强

**Schema支持**：完整支持

### 2.3 SQL:2008

**标准名称**：ISO/IEC 9075:2008

**核心内容**：

- **MERGE语句**：MERGE操作
- **TRUNCATE语句**：TRUNCATE操作

**Schema支持**：完整支持

---

## 3. SQLite标准

**标准名称**：SQLite 3.x

**核心内容**：

- **数据类型**：NULL、INTEGER、REAL、TEXT、BLOB
- **约束**：PRIMARY KEY、FOREIGN KEY、UNIQUE、CHECK
- **索引**：B-tree索引
- **触发器**：触发器支持
- **视图**：视图支持

**Schema支持**：完整支持

**状态**：自包含数据库标准

---

## 4. PostgreSQL标准

**标准名称**：PostgreSQL 15+

**核心内容**：

- **数据类型**：丰富的数据类型（JSONB、数组、范围类型等）
- **索引**：B-tree、Hash、GiST、GIN、BRIN等
- **约束**：PRIMARY KEY、FOREIGN KEY、UNIQUE、CHECK、EXCLUDE
- **视图**：视图、物化视图
- **函数**：PL/pgSQL、PL/Python等
- **扩展**：PostGIS、TimescaleDB等

**Schema支持**：完整支持

**状态**：开源数据库标准

---

## 5. 其他数据库标准

- **MySQL**：MySQL 8.0+
- **SQL Server**：SQL Server 2022
- **Oracle**：Oracle Database 23c

---

## 6. 标准对比矩阵

| 标准 | 组织 | Schema支持 | 状态 | 应用场景 |
|------|------|-----------|------|---------|
| **SQL:2016** | ISO/IEC | ⭐⭐⭐⭐⭐ | 标准 | 通用SQL |
| **SQLite 3** | SQLite | ⭐⭐⭐⭐ | 活跃 | 嵌入式应用 |
| **PostgreSQL 15** | PostgreSQL | ⭐⭐⭐⭐⭐ | 活跃 | 企业应用 |
| **MySQL 8** | Oracle | ⭐⭐⭐⭐ | 活跃 | Web应用 |
| **SQL Server 2022** | Microsoft | ⭐⭐⭐⭐ | 活跃 | 企业应用 |

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
