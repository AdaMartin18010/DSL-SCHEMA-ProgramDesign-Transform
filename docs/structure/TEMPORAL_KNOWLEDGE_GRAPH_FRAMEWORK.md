# 时序知识图谱框架

## 📑 目录

- [时序知识图谱框架](#时序知识图谱框架)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 框架定义](#2-框架定义)
    - [2.1 形式化定义](#21-形式化定义)
    - [2.2 时间表示](#22-时间表示)
  - [3. 时间表示](#3-时间表示)
    - [3.1 时间戳](#31-时间戳)
    - [3.2 时间区间](#32-时间区间)
    - [3.3 时间演化](#33-时间演化)
  - [4. 数据结构设计](#4-数据结构设计)
    - [4.1 时序实体数据结构](#41-时序实体数据结构)
    - [4.2 时序关系数据结构](#42-时序关系数据结构)
    - [4.3 版本历史数据结构](#43-版本历史数据结构)
  - [5. 时间推理算法](#5-时间推理算法)
    - [5.1 时间一致性推理](#51-时间一致性推理)
    - [5.2 时间演化推理](#52-时间演化推理)
    - [5.3 时间查询推理](#53-时间查询推理)
  - [6. 查询接口设计](#6-查询接口设计)
    - [6.1 时间点查询](#61-时间点查询)
    - [6.2 时间区间查询](#62-时间区间查询)
    - [6.3 时间演化查询](#63-时间演化查询)
  - [7. 实现方案](#7-实现方案)
    - [7.1 PostgreSQL存储](#71-postgresql存储)
    - [7.2 时间查询优化](#72-时间查询优化)
  - [8. 应用场景](#8-应用场景)
    - [8.1 Schema版本管理](#81-schema版本管理)
    - [8.2 Schema变更追踪](#82-schema变更追踪)
    - [8.3 时间序列分析](#83-时间序列分析)

---

## 1. 概述

**时序知识图谱（Temporal Knowledge Graph）**是在传统知识图谱基础上，引入**时间维度**的知识表示方法，支持时间演化追踪和时间推理。

**核心创新**：

- 支持时间戳和时间区间
- 时间演化追踪
- 时间推理算法
- 时间查询接口

**权威来源**：Know-Evolve、RE-NET、TComplEx等时序知识图谱研究

---

## 2. 框架定义

### 2.1 形式化定义

**定义1（时序知识图谱）**：

```text
Temporal_KG = (E, R, A, T, H)
```

其中：

- `E`：实体集合（Entities）
- `R`：关系集合（Relations）
- `A`：属性集合（Attributes）
- `T`：时间集合（Time）
- `H`：历史集合（History）

### 2.2 时间表示

**时间表示类型**：

1. **时间戳**（Timestamp）：
   - `t ∈ T`：具体时间点

2. **时间区间**（Time Interval）：
   - `[t_start, t_end]`：时间区间

3. **时间序列**（Time Series）：
   - `T = {t₁, t₂, ..., tₙ}`：时间序列

---

## 3. 时间表示

### 3.1 时间戳

**定义**：具体的时间点

**表示方式**：

- **ISO 8601格式**：`2024-01-21T12:00:00Z`
- **Unix时间戳**：`1705843200`
- **相对时间**：`now()`, `yesterday()`, `last_week()`

### 3.2 时间区间

**定义**：时间范围

**表示方式**：

```text
[t_start, t_end]
```

其中：

- `t_start`：开始时间
- `t_end`：结束时间（可为∞表示持续有效）

### 3.3 时间演化

**定义**：实体和关系随时间的变化

**演化类型**：

1. **创建**（Creation）：
   - `created_at`：创建时间

2. **更新**（Update）：
   - `updated_at`：更新时间
   - `version_history`：版本历史

3. **删除**（Deletion）：
   - `deleted_at`：删除时间

4. **变更**（Change）：
   - `change_log`：变更日志

---

## 4. 数据结构设计

### 4.1 时序实体数据结构

```typescript
interface TemporalEntity {
  id: string;                    // 实体ID
  name: string;                  // 实体名称
  type: string;                  // 实体类型

  // 时间信息
  temporal: {
    created_at: Date;            // 创建时间
    updated_at: Date;             // 更新时间
    deleted_at?: Date;            // 删除时间（可选）
    valid_from: Date;            // 有效开始时间
    valid_to?: Date;              // 有效结束时间（可选，∞表示持续有效）
  };

  // 版本历史
  versions: TemporalEntityVersion[];

  // 变更日志
  change_log: ChangeLogEntry[];
}
```

### 4.2 时序关系数据结构

```typescript
interface TemporalRelation {
  id: string;                    // 关系ID
  source: string;                // 源实体ID
  target: string;                // 目标实体ID
  type: string;                  // 关系类型

  // 时间信息
  temporal: {
    created_at: Date;            // 创建时间
    updated_at: Date;             // 更新时间
    valid_from: Date;            // 有效开始时间
    valid_to?: Date;              // 有效结束时间
  };

  // 关系权重（可能随时间变化）
  weight_history: WeightHistoryEntry[];
}
```

### 4.3 版本历史数据结构

```typescript
interface TemporalEntityVersion {
  version: string;               // 版本号
  timestamp: Date;               // 版本时间
  changes: {
    field: string;               // 变更字段
    old_value: any;               // 旧值
    new_value: any;               // 新值
  }[];
  snapshot: any;                  // 版本快照
}
```

---

## 5. 时间推理算法

### 5.1 时间一致性推理

**定义**：确保时间信息的一致性

**规则**：

1. **创建时间规则**：

   ```text
   created_at(e) ≤ updated_at(e)
   ```

2. **有效时间规则**：

   ```text
   valid_from(e) ≤ valid_to(e)
   ```

3. **关系时间规则**：

   ```text
   valid_from(r) ≥ max(valid_from(source(e)), valid_from(target(e)))
   ```

### 5.2 时间演化推理

**定义**：推理实体和关系的时间演化

**推理类型**：

1. **版本演化**：
   - 从版本历史推理演化路径
   - 预测未来版本

2. **关系演化**：
   - 从关系历史推理关系变化
   - 预测关系未来状态

### 5.3 时间查询推理

**定义**：根据时间条件推理相关实体和关系

**查询类型**：

1. **时间点查询**：

   ```cypher
   MATCH (e:Entity)
   WHERE e.temporal.valid_from <= $time
     AND (e.temporal.valid_to IS NULL OR e.temporal.valid_to >= $time)
   RETURN e
   ```

2. **时间区间查询**：

   ```cypher
   MATCH (e:Entity)
   WHERE e.temporal.valid_from <= $time_end
     AND (e.temporal.valid_to IS NULL OR e.temporal.valid_to >= $time_start)
   RETURN e
   ```

3. **时间演化查询**：

   ```cypher
   MATCH (e:Entity)-[v:VERSION]->(v_next:VERSION)
   WHERE v.timestamp >= $time_start
     AND v.timestamp <= $time_end
   RETURN e, v, v_next
   ```

---

## 6. 查询接口设计

### 6.1 时间点查询

**接口**：

```typescript
interface TemporalQuery {
  time: Date;                    // 查询时间点
  entity_id?: string;            // 实体ID（可选）
  relation_type?: string;        // 关系类型（可选）
}
```

**示例**：

```typescript
// 查询2024-01-21的所有有效Schema
const query: TemporalQuery = {
  time: new Date('2024-01-21'),
  entity_id: 'schema_001'
};
```

### 6.2 时间区间查询

**接口**：

```typescript
interface TemporalRangeQuery {
  time_start: Date;              // 开始时间
  time_end: Date;                // 结束时间
  entity_id?: string;
  relation_type?: string;
}
```

### 6.3 时间演化查询

**接口**：

```typescript
interface TemporalEvolutionQuery {
  entity_id: string;             // 实体ID
  time_start?: Date;              // 开始时间（可选）
  time_end?: Date;                // 结束时间（可选）
}
```

---

## 7. 实现方案

### 7.1 PostgreSQL存储

```sql
-- 时序实体表
CREATE TABLE temporal_entities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP
);

-- 版本历史表
CREATE TABLE entity_versions (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES temporal_entities(id),
    version VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    snapshot JSONB,
    UNIQUE(entity_id, version)
);

-- 变更日志表
CREATE TABLE change_logs (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES temporal_entities(id),
    timestamp TIMESTAMP NOT NULL,
    field VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    change_type VARCHAR(20) NOT NULL  -- CREATE, UPDATE, DELETE
);

-- 时序关系表
CREATE TABLE temporal_relations (
    id VARCHAR(50) PRIMARY KEY,
    source VARCHAR(50) REFERENCES temporal_entities(id),
    target VARCHAR(50) REFERENCES temporal_entities(id),
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP
);

-- 索引
CREATE INDEX idx_temporal_entities_valid_time
  ON temporal_entities(valid_from, valid_to);
CREATE INDEX idx_temporal_relations_valid_time
  ON temporal_relations(valid_from, valid_to);
CREATE INDEX idx_change_logs_timestamp
  ON change_logs(timestamp);
```

### 7.2 时间查询优化

**优化策略**：

1. **时间索引**：在`valid_from`和`valid_to`字段上创建索引
2. **分区表**：按时间分区存储历史数据
3. **物化视图**：为常用时间查询创建物化视图

---

## 8. 应用场景

### 8.1 Schema版本管理

**场景**：追踪Schema的版本演化

**流程**：

1. Schema创建时记录`created_at`
2. Schema更新时记录`updated_at`和版本历史
3. 查询特定时间点的Schema版本
4. 分析Schema演化趋势

### 8.2 Schema变更追踪

**场景**：追踪Schema的变更历史

**流程**：

1. 记录每次变更的详细信息
2. 查询变更日志
3. 分析变更影响
4. 支持回滚到历史版本

### 8.3 时间序列分析

**场景**：分析Schema随时间的变化趋势

**流程**：

1. 提取时间序列数据
2. 分析变化趋势
3. 预测未来变化
4. 优化Schema设计

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
