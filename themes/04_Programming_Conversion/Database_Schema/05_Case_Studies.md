# 数据库Schema实践案例

## 📑 目录

- [数据库Schema实践案例](#数据库schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：SQLite到PostgreSQL迁移](#2-案例1sqlite到postgresql迁移)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema转换](#22-schema转换)
  - [3. 案例2：Schema版本管理](#3-案例2schema版本管理)
    - [3.1 场景描述](#31-场景描述)
  - [4. 案例3：数据库Schema自动生成](#4-案例3数据库schema自动生成)
    - [4.1 场景描述](#41-场景描述)

---

## 1. 案例概述

本文档提供数据库Schema在实际应用中的实践案例。

---

## 2. 案例1：SQLite到PostgreSQL迁移

### 2.1 场景描述

**应用场景**：
将移动应用的SQLite数据库迁移到
PostgreSQL服务器数据库。

### 2.2 Schema转换

**SQLite Schema**：

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at INTEGER
);
```

**PostgreSQL Schema**：

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. 案例2：Schema版本管理

### 3.1 场景描述

**应用场景**：
使用Schema版本管理工具管理数据库Schema变更。

---

## 4. 案例3：数据库Schema自动生成

### 4.1 场景描述

**应用场景**：
从Schema定义自动生成SQL DDL语句。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
