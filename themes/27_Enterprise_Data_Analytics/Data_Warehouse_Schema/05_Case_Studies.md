# 数据仓库Schema实践案例

## 📑 目录

- [数据仓库Schema实践案例](#数据仓库schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业级星型模式数据仓库系统](#2-案例1企业级星型模式数据仓库系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)
  - [3. 案例2：Data Vault数据仓库设计](#3-案例2data-vault数据仓库设计)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：数据仓库到SQL转换](#4-案例3数据仓库到sql转换)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：数据血缘追溯系统](#5-案例4数据血缘追溯系统)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：数据仓库数据存储与分析系统](#6-案例5数据仓库数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供数据仓库Schema在实际应用中的实践案例。

---

## 2. 案例1：企业级星型模式数据仓库系统

### 2.1 业务背景

**企业背景**：
某零售公司需要构建数据仓库，支持销售数据分析、多维度分析和历史数据查询，为业务决策提供数据支持。

**业务痛点**：

1. **数据分散**：数据分散在不同系统中
2. **分析困难**：难以进行多维度分析
3. **历史数据缺失**：缺乏历史数据查询能力
4. **性能问题**：OLTP系统不适合分析查询

**业务目标**：

- 集中数据存储
- 支持多维度分析
- 支持历史数据查询
- 提高分析性能

### 2.2 技术挑战

1. **星型模式设计**：设计合理的星型模式
2. **维度建模**：设计维度表结构
3. **事实表设计**：设计事实表和度量
4. **ETL流程**：构建ETL流程

### 2.3 解决方案

**使用Schema定义星型模式数据仓库系统**：

### 2.4 完整代码实现

**星型模式数据仓库Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
星型模式数据仓库Schema实现
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

class FactTableType(str, Enum):
    """事实表类型"""
    TRANSACTION = "Transaction"
    SNAPSHOT = "Snapshot"
    ACCUMULATING = "Accumulating"

class MeasureType(str, Enum):
    """度量类型"""
    SUM = "Sum"
    AVG = "Average"
    COUNT = "Count"
    MIN = "Min"
    MAX = "Max"

@dataclass
class Measure:
    """度量"""
    measure_name: str
    measure_type: MeasureType
    data_type: str
    aggregation_function: str
    description: Optional[str] = None

@dataclass
class DimensionKey:
    """维度键"""
    dimension_table_id: str
    foreign_key_name: str

@dataclass
class FactTable:
    """事实表"""
    fact_table_id: str
    fact_table_name: str
    fact_table_type: FactTableType
    measures: List[Measure] = field(default_factory=list)
    dimension_keys: List[DimensionKey] = field(default_factory=list)
    grain: str = ""
    partition_key: Optional[str] = None

@dataclass
class DimensionAttribute:
    """维度属性"""
    attribute_name: str
    attribute_type: str
    data_type: str
    is_required: bool = True
    description: Optional[str] = None

@dataclass
class DimensionTable:
    """维度表"""
    dimension_table_id: str
    dimension_table_name: str
    dimension_type: str
    attributes: List[DimensionAttribute] = field(default_factory=list)
    primary_key: str = ""
    slow_changing_type: str = "Type1"

@dataclass
class StarSchemaDataWarehouse:
    """星型模式数据仓库"""
    warehouse_id: str
    warehouse_name: str
    fact_tables: List[FactTable] = field(default_factory=list)
    dimension_tables: List[DimensionTable] = field(default_factory=list)

    def add_fact_table(self, fact_table: FactTable):
        """添加事实表"""
        self.fact_tables.append(fact_table)

    def add_dimension_table(self, dimension_table: DimensionTable):
        """添加维度表"""
        self.dimension_tables.append(dimension_table)

    def get_fact_table(self, fact_table_id: str) -> Optional[FactTable]:
        """获取事实表"""
        for ft in self.fact_tables:
            if ft.fact_table_id == fact_table_id:
                return ft
        return None

    def get_dimension_table(self, dimension_table_id: str) -> Optional[DimensionTable]:
        """获取维度表"""
        for dt in self.dimension_tables:
            if dt.dimension_table_id == dimension_table_id:
                return dt
        return None

# 使用示例
if __name__ == '__main__':
    # 创建星型模式数据仓库
    warehouse = StarSchemaDataWarehouse(
        warehouse_id="DW-001",
        warehouse_name="销售数据仓库"
    )

    # 创建产品维度表
    product_dimension = DimensionTable(
        dimension_table_id="DIM-PRODUCT",
        dimension_table_name="dim_product",
        dimension_type="Product",
        primary_key="product_id",
        attributes=[
            DimensionAttribute("product_id", "Surrogate_Key", "Integer"),
            DimensionAttribute("product_name", "Descriptive", "String"),
            DimensionAttribute("product_category", "Hierarchical", "String"),
            DimensionAttribute("product_brand", "Descriptive", "String")
        ]
    )
    warehouse.add_dimension_table(product_dimension)

    # 创建时间维度表
    time_dimension = DimensionTable(
        dimension_table_id="DIM-TIME",
        dimension_table_name="dim_time",
        dimension_type="Time",
        primary_key="time_id",
        attributes=[
            DimensionAttribute("time_id", "Surrogate_Key", "Integer"),
            DimensionAttribute("date", "Descriptive", "Date"),
            DimensionAttribute("year", "Hierarchical", "Integer"),
            DimensionAttribute("quarter", "Hierarchical", "Integer"),
            DimensionAttribute("month", "Hierarchical", "Integer"),
            DimensionAttribute("day", "Hierarchical", "Integer")
        ]
    )
    warehouse.add_dimension_table(time_dimension)

    # 创建客户维度表
    customer_dimension = DimensionTable(
        dimension_table_id="DIM-CUSTOMER",
        dimension_table_name="dim_customer",
        dimension_type="Customer",
        primary_key="customer_id",
        attributes=[
            DimensionAttribute("customer_id", "Surrogate_Key", "Integer"),
            DimensionAttribute("customer_name", "Descriptive", "String"),
            DimensionAttribute("customer_segment", "Hierarchical", "String"),
            DimensionAttribute("customer_region", "Hierarchical", "String")
        ]
    )
    warehouse.add_dimension_table(customer_dimension)

    # 创建销售事实表
    sales_fact = FactTable(
        fact_table_id="FACT-SALES",
        fact_table_name="fact_sales",
        fact_table_type=FactTableType.TRANSACTION,
        grain="One row per sales transaction",
        measures=[
            Measure("sales_amount", MeasureType.SUM, "Decimal", "SUM"),
            Measure("sales_quantity", MeasureType.SUM, "Integer", "SUM"),
            Measure("sales_cost", MeasureType.SUM, "Decimal", "SUM")
        ],
        dimension_keys=[
            DimensionKey("DIM-PRODUCT", "product_id"),
            DimensionKey("DIM-TIME", "time_id"),
            DimensionKey("DIM-CUSTOMER", "customer_id")
        ]
    )
    warehouse.add_fact_table(sales_fact)

    print(f"数据仓库: {warehouse.warehouse_name}")
    print(f"事实表数量: {len(warehouse.fact_tables)}")
    print(f"维度表数量: {len(warehouse.dimension_tables)}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 查询性能 | 慢 | 快 | 10x提升 |
| 数据集中度 | 分散 | 集中 | 100% |
| 多维度分析能力 | 低 | 高 | 显著提升 |
| 历史数据查询 | 不支持 | 支持 | 100% |

**业务价值**：

1. **数据集中**：集中数据存储
2. **分析能力提升**：支持多维度分析
3. **历史数据支持**：支持历史数据查询
4. **性能提升**：提高分析查询性能

**经验教训**：

1. 星型模式设计很重要
2. 维度建模需要仔细设计
3. 事实表粒度需要合理
4. ETL流程需要优化

**参考案例**：

- [Kimball数据仓库方法](https://www.kimballgroup.com/)
- [星型模式设计最佳实践](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)

---

## 3. 案例2：Data Vault数据仓库设计

### 3.1 场景描述

**应用场景**：
基于Data Vault 2.0方法设计数据仓库，包括Hub、Link、Satellite结构。

**业务需求**：

- 支持历史数据追踪
- 支持数据源追踪
- 支持灵活的数据模型

### 3.2 Schema定义

**Data Vault数据仓库Schema**：

```dsl
schema DataVaultDataWarehouse {
  hubs: List<Hub> {
    customer_hub: Hub {
      hub_id: String @value("HUB-CUSTOMER")
      hub_name: String @value("hub_customer")
      business_key: String @value("customer_code")
      business_key_data_type: Enum @value("String")
      load_date: Date @value("2025-01-21")
      record_source: String @value("CRM_SYSTEM")
    }
  }

  links: List<Link> {
    customer_order_link: Link {
      link_id: String @value("LINK-CUSTOMER-ORDER")
      link_name: String @value("link_customer_order")
      hub_keys: List<String> {
        "HUB-CUSTOMER"
        "HUB-ORDER"
      }
      link_type: Enum @value("Transaction")
      load_date: Date @value("2025-01-21")
      record_source: String @value("ORDER_SYSTEM")
    }
  }

  satellites: List<Satellite> {
    customer_satellite: Satellite {
      satellite_id: String @value("SAT-CUSTOMER")
      satellite_name: String @value("sat_customer")
      parent_id: String @value("HUB-CUSTOMER")
      parent_type: Enum @value("Hub")
      descriptive_attributes: List<SatelliteAttribute> {
        customer_name: SatelliteAttribute {
          attribute_name: String @value("customer_name")
          attribute_type: Enum @value("String")
        }
        customer_address: SatelliteAttribute {
          attribute_name: String @value("customer_address")
          attribute_type: Enum @value("String")
        }
      }
      load_date: Date @value("2025-01-21")
      effective_date: Date @value("2025-01-21")
      record_source: String @value("CRM_SYSTEM")
    }
  }
}
```

---

## 4. 案例3：数据仓库到SQL转换

### 4.1 场景描述

**应用场景**：
将数据仓库Schema转换为SQL DDL语句，用于创建数据仓库表结构。

**业务需求**：

- 支持自动生成SQL DDL
- 支持多数据库平台
- 支持表结构验证

### 4.2 实现代码

```python
def convert_dw_to_sql_ddl(dw_data: DataWarehouseSchema) -> List[str]:
    """将数据仓库Schema转换为SQL DDL语句"""
    ddl_statements = []

    # 转换维度表
    for dimension_table in dw_data.star_schema.dimension_tables:
        ddl = f"CREATE TABLE {dimension_table.dimension_table_name} (\n"

        # 主键
        primary_key = dimension_table.primary_key
        ddl += f"    {primary_key} INTEGER PRIMARY KEY,\n"

        # 属性
        for attribute in dimension_table.attributes:
            if attribute.attribute_name != primary_key:
                ddl += f"    {attribute.attribute_name} {map_data_type_to_sql(attribute.data_type)}"
                if not attribute.is_required:
                    ddl += " NULL"
                ddl += ",\n"

        ddl = ddl.rstrip(",\n") + "\n);"
        ddl_statements.append(ddl)

    # 转换事实表
    for fact_table in dw_data.star_schema.fact_tables:
        ddl = f"CREATE TABLE {fact_table.fact_table_name} (\n"

        # 度量
        for measure in fact_table.measures:
            ddl += f"    {measure.measure_name} {map_data_type_to_sql(measure.data_type)} NOT NULL,\n"

        # 维度键
        for dimension_key in fact_table.dimension_keys:
            ddl += f"    {dimension_key.foreign_key_name} INTEGER NOT NULL,\n"

        # 外键约束
        ddl = ddl.rstrip(",\n") + ",\n"
        for dimension_key in fact_table.dimension_keys:
            dimension_table = get_dimension_table(dimension_key.dimension_table_id)
            ddl += f"    FOREIGN KEY ({dimension_key.foreign_key_name}) REFERENCES {dimension_table.dimension_table_name}({dimension_table.primary_key}),\n"

        ddl = ddl.rstrip(",\n") + "\n);"
        ddl_statements.append(ddl)

    return ddl_statements
```

---

## 5. 案例4：数据血缘追溯系统

### 5.1 场景描述

**应用场景**：
数据血缘追溯系统，追踪数据从源系统到目标系统的完整路径。

**业务需求**：

- 支持数据血缘可视化
- 支持影响分析
- 支持数据追溯

### 5.2 实现代码

```python
def trace_data_lineage(dw_data: DataWarehouseSchema, target_table: str) -> List[LineagePath]:
    """追溯数据血缘"""
    lineage_paths = []

    # 查找目标表
    target_node = find_node_by_name(dw_data.metadata.data_lineage, target_table)

    if target_node:
        # 递归查找上游节点
        def find_upstream_nodes(node: LineageNode, path: List[LineageNode]):
            if node.node_type == "Source":
                lineage_paths.append(LineagePath(nodes=path + [node]))
            else:
                # 查找上游边
                upstream_edges = [edge for edge in dw_data.metadata.data_lineage.lineage_edges
                                 if edge.to_node_id == node.node_id]

                for edge in upstream_edges:
                    upstream_node = find_node_by_id(dw_data.metadata.data_lineage, edge.from_node_id)
                    if upstream_node and upstream_node not in path:
                        find_upstream_nodes(upstream_node, path + [node])

        find_upstream_nodes(target_node, [])

    return lineage_paths

def analyze_impact(dw_data: DataWarehouseSchema, source_table: str) -> List[LineagePath]:
    """分析影响范围"""
    impact_paths = []

    # 查找源表
    source_node = find_node_by_name(dw_data.metadata.data_lineage, source_table)

    if source_node:
        # 递归查找下游节点
        def find_downstream_nodes(node: LineageNode, path: List[LineageNode]):
            # 查找下游边
            downstream_edges = [edge for edge in dw_data.metadata.data_lineage.lineage_edges
                               if edge.from_node_id == node.node_id]

            if not downstream_edges:
                impact_paths.append(LineagePath(nodes=path + [node]))
            else:
                for edge in downstream_edges:
                    downstream_node = find_node_by_id(dw_data.metadata.data_lineage, edge.to_node_id)
                    if downstream_node and downstream_node not in path:
                        find_downstream_nodes(downstream_node, path + [node])

        find_downstream_nodes(source_node, [])

    return impact_paths
```

---

## 6. 案例5：数据仓库数据存储与分析系统

### 6.1 场景描述

**应用场景**：
数据仓库数据存储与分析系统，支持元数据存储、查询、分析。

**业务需求**：

- 支持元数据存储
- 支持元数据查询和分析
- 支持数据质量监控

### 6.2 实现代码

```python
def store_dw_metadata(dw_data: DataWarehouseSchema, conn):
    """存储数据仓库元数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储事实表元数据
    for fact_table in dw_data.star_schema.fact_tables:
        cursor.execute("""
            INSERT INTO fact_table_metadata
            (fact_table_id, fact_table_name, fact_table_type, grain, partition_key)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (fact_table_id) DO UPDATE SET
            fact_table_name = EXCLUDED.fact_table_name,
            fact_table_type = EXCLUDED.fact_table_type,
            grain = EXCLUDED.grain,
            partition_key = EXCLUDED.partition_key,
            updated_at = CURRENT_TIMESTAMP
        """, (fact_table.fact_table_id, fact_table.fact_table_name,
              fact_table.fact_table_type, fact_table.grain, fact_table.partition_key))

        # 存储度量元数据
        for measure in fact_table.measures:
            cursor.execute("""
                INSERT INTO measure_metadata
                (measure_id, fact_table_id, measure_name, measure_type, data_type, aggregation_function)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (measure_id) DO UPDATE SET
                measure_name = EXCLUDED.measure_name,
                measure_type = EXCLUDED.measure_type,
                data_type = EXCLUDED.data_type,
                aggregation_function = EXCLUDED.aggregation_function
            """, (measure.measure_id, fact_table.fact_table_id,
                  measure.measure_name, measure.measure_type,
                  measure.data_type, measure.aggregation_function))

    # 存储维度表元数据
    for dimension_table in dw_data.star_schema.dimension_tables:
        cursor.execute("""
            INSERT INTO dimension_table_metadata
            (dimension_table_id, dimension_table_name, dimension_type, primary_key, slow_changing_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (dimension_table_id) DO UPDATE SET
            dimension_table_name = EXCLUDED.dimension_table_name,
            dimension_type = EXCLUDED.dimension_type,
            primary_key = EXCLUDED.primary_key,
            slow_changing_type = EXCLUDED.slow_changing_type,
            updated_at = CURRENT_TIMESTAMP
        """, (dimension_table.dimension_table_id, dimension_table.dimension_table_name,
              dimension_table.dimension_type, dimension_table.primary_key,
              dimension_table.slow_changing_type))

        # 存储维度属性元数据
        for attribute in dimension_table.attributes:
            cursor.execute("""
                INSERT INTO dimension_attribute_metadata
                (attribute_id, dimension_table_id, attribute_name, attribute_type, data_type, is_required)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (attribute_id) DO UPDATE SET
                attribute_name = EXCLUDED.attribute_name,
                attribute_type = EXCLUDED.attribute_type,
                data_type = EXCLUDED.data_type,
                is_required = EXCLUDED.is_required
            """, (attribute.attribute_id, dimension_table.dimension_table_id,
                  attribute.attribute_name, attribute.attribute_type,
                  attribute.data_type, attribute.is_required))

    # 存储数据血缘
    for edge in dw_data.metadata.data_lineage.lineage_edges:
        cursor.execute("""
            INSERT INTO data_lineage
            (lineage_id, from_node_id, to_node_id, transformation_rule, data_flow_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (lineage_id) DO UPDATE SET
            transformation_rule = EXCLUDED.transformation_rule,
            data_flow_type = EXCLUDED.data_flow_type
        """, (edge.edge_id, edge.from_node_id, edge.to_node_id,
              edge.transformation_rule, edge.data_flow_type))

    conn.commit()

def generate_dw_report(conn):
    """生成数据仓库报表"""
    cursor = conn.cursor()

    # 查询事实表汇总
    cursor.execute("""
        SELECT
            ftm.fact_table_name,
            ftm.fact_table_type,
            COUNT(mm.measure_id) as measure_count
        FROM fact_table_metadata ftm
        LEFT JOIN measure_metadata mm ON ftm.fact_table_id = mm.fact_table_id
        GROUP BY ftm.fact_table_id, ftm.fact_table_name, ftm.fact_table_type
        ORDER BY ftm.fact_table_name
    """)

    fact_table_report = cursor.fetchall()

    # 查询维度表汇总
    cursor.execute("""
        SELECT
            dtm.dimension_table_name,
            dtm.dimension_type,
            COUNT(dam.attribute_id) as attribute_count
        FROM dimension_table_metadata dtm
        LEFT JOIN dimension_attribute_metadata dam ON dtm.dimension_table_id = dam.dimension_table_id
        GROUP BY dtm.dimension_table_id, dtm.dimension_table_name, dtm.dimension_type
        ORDER BY dtm.dimension_table_name
    """)

    dimension_table_report = cursor.fetchall()

    return {
        "fact_table_report": fact_table_report,
        "dimension_table_report": dimension_table_report
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
