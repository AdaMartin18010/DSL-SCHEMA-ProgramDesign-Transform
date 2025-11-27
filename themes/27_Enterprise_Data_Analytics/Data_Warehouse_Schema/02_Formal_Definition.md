# 数据仓库Schema形式化定义

## 📑 目录

- [数据仓库Schema形式化定义](#数据仓库schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 星型模式Schema](#2-星型模式schema)
  - [3. 雪花模式Schema](#3-雪花模式schema)
  - [4. Data Vault Schema](#4-data-vault-schema)
  - [5. 数据仓库元数据Schema](#5-数据仓库元数据schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 数据仓库完整性定理](#91-数据仓库完整性定理)
    - [9.2 维度层次一致性定理](#92-维度层次一致性定理)
    - [9.3 数据血缘追溯定理](#93-数据血缘追溯定理)

---

## 1. 形式化模型

**定义1（数据仓库Schema）**：
数据仓库Schema是一个四元组：

```text
Data_Warehouse_Schema = (Star_Schema, Snowflake_Schema,
                         Data_Vault_Schema, Metadata_Schema)
```

其中：

- `Star_Schema`：星型模式Schema
- `Snowflake_Schema`：雪花模式Schema
- `Data_Vault_Schema`：Data Vault模式Schema
- `Metadata_Schema`：元数据Schema

---

## 2. 星型模式Schema

**定义2（星型模式Schema）**：

```text
Star_Schema = (Fact_Table, Dimension_Tables, Dimension_Hierarchies)
```

**形式化DSL定义**：

```dsl
schema StarSchema {
  fact_tables: List<FactTable> {
    fact_table_id: String @required @unique
    fact_table_name: String @required
    fact_table_type: Enum { Transaction, Snapshot, Accumulating } @required
    measures: List<Measure> {
      measure_id: String @required @unique
      measure_name: String @required
      measure_type: Enum { Sum, Count, Average, Min, Max, Distinct_Count } @required
      data_type: Enum { Integer, Decimal, String, Date, Boolean } @required
      aggregation_function: String @required
    }
    dimension_keys: List<DimensionKey> {
      dimension_key_id: String @required @unique
      dimension_table_id: String @required
      foreign_key_name: String @required
    }
    grain: String @required
    partition_key: Optional<String>
  }

  dimension_tables: List<DimensionTable> {
    dimension_table_id: String @required @unique
    dimension_table_name: String @required
    dimension_type: Enum { Time, Geography, Product, Customer, Other } @required
    attributes: List<DimensionAttribute> {
      attribute_id: String @required @unique
      attribute_name: String @required
      attribute_type: Enum { Natural_Key, Surrogate_Key, Descriptive, Hierarchical } @required
      data_type: Enum { Integer, Decimal, String, Date, Boolean } @required
      is_required: Boolean @default(true)
    }
    primary_key: String @required
    slow_changing_type: Enum { Type1, Type2, Type3 } @default("Type1")
  }

  dimension_hierarchies: List<DimensionHierarchy> {
    hierarchy_id: String @required @unique
    dimension_table_id: String @required
    hierarchy_name: String @required
    hierarchy_levels: List<HierarchyLevel> {
      level_id: String @required @unique
      level_name: String @required
      level_number: Int @range(1, 10) @required
      attribute_id: String @required
    }
    is_balanced: Boolean @default(true)
  }
} @standard("Kimball")
```

---

## 3. 雪花模式Schema

**定义3（雪花模式Schema）**：

```text
Snowflake_Schema = (Normalized_Dimension_Tables, Dimension_Hierarchies, Dimension_Relationships)
```

**形式化DSL定义**：

```dsl
schema SnowflakeSchema {
  normalized_dimension_tables: List<NormalizedDimensionTable> {
    dimension_table_id: String @required @unique
    dimension_table_name: String @required
    normalization_level: Int @range(1, 5) @default(3)
    attributes: List<DimensionAttribute> {
      attribute_id: String @required @unique
      attribute_name: String @required
      attribute_type: Enum { Natural_Key, Surrogate_Key, Descriptive, Foreign_Key } @required
      data_type: Enum { Integer, Decimal, String, Date, Boolean } @required
      foreign_key_table: Optional<String>
      foreign_key_column: Optional<String>
    }
    primary_key: String @required
    foreign_keys: List<ForeignKey> {
      foreign_key_id: String @required @unique
      foreign_key_name: String @required
      referenced_table: String @required
      referenced_column: String @required
    }
  }

  dimension_hierarchies: List<DimensionHierarchy> {
    hierarchy_id: String @required @unique
    hierarchy_name: String @required
    hierarchy_structure: List<HierarchyNode> {
      node_id: String @required @unique
      node_name: String @required
      parent_node_id: Optional<String>
      dimension_table_id: String @required
      level_number: Int @range(1, 10) @required
    }
    is_balanced: Boolean @default(true)
  }

  dimension_relationships: List<DimensionRelationship> {
    relationship_id: String @required @unique
    from_dimension_table_id: String @required
    to_dimension_table_id: String @required
    relationship_type: Enum { One_to_One, One_to_Many, Many_to_Many } @required
    join_condition: String @required
  }
} @standard("Kimball")
```

---

## 4. Data Vault Schema

**定义4（Data Vault Schema）**：

```text
Data_Vault_Schema = (Hubs, Links, Satellites)
```

**形式化DSL定义**：

```dsl
schema DataVault {
  hubs: List<Hub> {
    hub_id: String @required @unique
    hub_name: String @required
    business_key: String @required
    business_key_data_type: Enum { String, Integer, Decimal, Date } @required
    load_date: Date @required
    record_source: String @required
  }

  links: List<Link> {
    link_id: String @required @unique
    link_name: String @required
    hub_keys: List<String> @required @min_size(2)
    link_type: Enum { Transaction, Hierarchy, Reference } @required
    load_date: Date @required
    record_source: String @required
  }

  satellites: List<Satellite> {
    satellite_id: String @required @unique
    satellite_name: String @required
    parent_id: String @required
    parent_type: Enum { Hub, Link } @required
    descriptive_attributes: List<SatelliteAttribute> {
      attribute_id: String @required @unique
      attribute_name: String @required
      attribute_type: Enum { String, Integer, Decimal, Date, Boolean, JSON } @required
      is_required: Boolean @default(false)
    }
    load_date: Date @required
    effective_date: Date @required
    end_date: Optional<Date>
    record_source: String @required
    hash_key: String @required
  }
} @standard("DataVault2.0")
```

---

## 5. 数据仓库元数据Schema

**定义5（数据仓库元数据Schema）**：

```text
Metadata_Schema = (Data_Dictionary, Data_Lineage, Data_Quality)
```

**形式化DSL定义**：

```dsl
schema Metadata {
  data_dictionary: DataDictionary {
    tables: List<TableDefinition> {
      table_id: String @required @unique
      table_name: String @required
      table_type: Enum { Fact, Dimension, Hub, Link, Satellite } @required
      schema_name: String @required
      columns: List<ColumnDefinition> {
        column_id: String @required @unique
        column_name: String @required
        data_type: Enum { Integer, Decimal, String, Date, Boolean, JSON } @required
        is_nullable: Boolean @default(true)
        is_primary_key: Boolean @default(false)
        is_foreign_key: Boolean @default(false)
        default_value: Optional<String>
        description: Optional<String>
      }
      description: Optional<String>
    }
  }

  data_lineage: DataLineage {
    lineage_nodes: List<LineageNode> {
      node_id: String @required @unique
      node_name: String @required
      node_type: Enum { Source, Transformation, Target } @required
      node_location: String @required
    }
    lineage_edges: List<LineageEdge> {
      edge_id: String @required @unique
      from_node_id: String @required
      to_node_id: String @required
      transformation_rule: Optional<String>
      data_flow_type: Enum { Direct, Transform, Aggregate } @required
    }
  }

  data_quality: DataQuality {
    quality_metrics: List<QualityMetric> {
      metric_id: String @required @unique
      table_id: String @required
      metric_name: String @required
      metric_type: Enum { Completeness, Accuracy, Consistency, Timeliness, Validity } @required
      metric_value: Decimal @range(0, 100)
      threshold: Decimal @range(0, 100) @default(90)
      is_passed: Boolean @computed("metric_value >= threshold")
      check_date: Date @required
    }
    quality_checks: List<QualityCheck> {
      check_id: String @required @unique
      table_id: String @required
      check_rule: String @required
      check_result: Enum { Pass, Fail, Warning } @required
      check_date: Date @required
      error_count: Integer @default(0)
    }
  }
} @standard("Metadata")
```

---

## 6. 类型系统

**类型定义**：

```dsl
type TableID = String @pattern("^TBL-[0-9]{8}$")
type ColumnID = String @pattern("^COL-[0-9]{8}$")
type Decimal = Float @precision(18, 2) @range(0, null)
type Date = DateTime @format("YYYY-MM-DD")
type Percentage = Float @range(0, 100) @precision(5, 2)
```

---

## 7. 约束规则

**约束1（事实表完整性约束）**：

```text
∀fact_table ∈ Fact_Tables:
  fact_table.measures.size() > 0
  ∧ fact_table.dimension_keys.size() > 0
  ∧ ∀dimension_key ∈ fact_table.dimension_keys:
    ∃dimension_table: dimension_table.dimension_table_id == dimension_key.dimension_table_id
```

**约束2（维度层次一致性约束）**：

```text
∀hierarchy ∈ Dimension_Hierarchies:
  hierarchy.hierarchy_levels.size() > 1
  ∧ ∀level ∈ hierarchy.hierarchy_levels:
    level.level_number < hierarchy.hierarchy_levels.size()
    ∧ (level.level_number > 1 → ∃parent_level: parent_level.level_number == level.level_number - 1)
```

**约束3（Data Vault完整性约束）**：

```text
∀satellite ∈ Satellites:
  satellite.parent_type == "Hub" → ∃hub: hub.hub_id == satellite.parent_id
  ∧ satellite.parent_type == "Link" → ∃link: link.link_id == satellite.parent_id
  ∧ satellite.effective_date <= satellite.end_date (if end_date is not null)
```

---

## 8. 转换函数

**转换函数1（星型模式到SQL）**：

```text
f_Star_to_SQL: Star_Schema → SQL_Schema

f_Star_to_SQL(star) = {
  create_table: {
    table_name: star.fact_table_name
    columns: star.measures + star.dimension_keys
    foreign_keys: star.dimension_keys.map(key => {
      foreign_key: key.foreign_key_name
      references: dimension_table.primary_key
    })
  }
}
```

**转换函数2（Data Vault到星型模式）**：

```text
f_DataVault_to_Star: Data_Vault_Schema → Star_Schema

f_DataVault_to_Star(dv) = {
  fact_table: {
    fact_table_name: dv.link.link_name
    measures: dv.satellites.descriptive_attributes
    dimension_keys: dv.hubs.business_key
  }
}
```

---

## 9. 形式化定理

### 9.1 数据仓库完整性定理

**定理1（数据仓库完整性）**：

对于任意事实表，事实表必须包含至少一个度量和一个维度键：

```text
∀fact_table ∈ Fact_Tables:
  fact_table.measures.size() > 0
  ∧ fact_table.dimension_keys.size() > 0
```

**证明**：

由约束1和类型系统定义，数据仓库完整性满足上述条件。

### 9.2 维度层次一致性定理

**定理2（维度层次一致性）**：

对于任意维度层次，层次级别必须连续且有序：

```text
∀hierarchy ∈ Dimension_Hierarchies:
  hierarchy.hierarchy_levels.size() > 1
  ∧ ∀level ∈ hierarchy.hierarchy_levels:
    level.level_number < hierarchy.hierarchy_levels.size()
```

**证明**：

由约束2和类型系统定义，维度层次一致性满足上述条件。

### 9.3 数据血缘追溯定理

**定理3（数据血缘追溯）**：

对于任意数据血缘节点，存在从源节点到目标节点的路径：

```text
∀target_node ∈ Lineage_Nodes:
  target_node.node_type == "Target"
  → ∃path: path.from_node.node_type == "Source"
    ∧ path.to_node == target_node
    ∧ ∀edge ∈ path.edges: edge.from_node == previous_edge.to_node
```

**证明**：

由数据血缘定义和图论原理，数据血缘追溯满足上述条件。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
