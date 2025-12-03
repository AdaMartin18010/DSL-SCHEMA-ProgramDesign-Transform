# 计算社会科学Schema转换体系

## 📑 目录

- [计算社会科学Schema转换体系](#计算社会科学schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. NetworkX转换](#3-networkx转换)
  - [4. Gephi转换](#4-gephi转换)
  - [5. PostgreSQL存储](#5-postgresql存储)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)

---

## 1. 转换体系概述

计算社会科学Schema转换体系支持**计算社会科学数据到各种格式的转换**，包括NetworkX、Gephi、PostgreSQL等格式。

**转换目标**：

- NetworkX Graph
- Gephi格式
- GraphML格式
- PostgreSQL数据库
- JSON格式

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 |
|---------|--------|----------|------------|----------|------------|
| **CSS → NetworkX** | CSS_Schema | NetworkX Graph | ⭐⭐ | ✅ 良好 | 高 |
| **CSS → Gephi** | CSS_Schema | Gephi Format | ⭐⭐⭐ | ✅ 良好 | 高 |
| **CSS → GraphML** | CSS_Schema | GraphML | ⭐⭐ | ✅ 良好 | 高 |
| **CSS → PostgreSQL** | CSS_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 |

---

## 3. NetworkX转换

### 3.1 CSS → NetworkX转换

**转换函数**：

```text
to_networkx: Social_Network → NetworkX_Graph
```

**转换示例**：

```python
import networkx as nx

def to_networkx(social_network: SocialNetwork) -> nx.Graph:
    """转换为NetworkX图"""
    G = nx.Graph() if social_network.properties.directed == False else nx.DiGraph()

    # 添加节点
    for node in social_network.nodes:
        G.add_node(node.node_id, **node.attributes)

    # 添加边
    for edge in social_network.edges:
        G.add_edge(edge.source, edge.target,
                  weight=edge.weight, **edge.attributes)

    return G
```

---

## 4. Gephi转换

### 4.1 CSS → Gephi转换

**转换函数**：

```text
to_gephi: Social_Network → Gephi_Format
```

**转换示例**：

```python
def to_gephi(social_network: SocialNetwork) -> str:
    """转换为Gephi格式"""
    gephi_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    gephi_xml += '<graphml>\n'
    # 添加节点和边定义
    # ...
    return gephi_xml
```

---

## 5. PostgreSQL存储

### 5.1 数据库Schema设计

```sql
CREATE TABLE social_networks (
    id VARCHAR(50) PRIMARY KEY,
    network_type VARCHAR(50),
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE network_nodes (
    id VARCHAR(50) PRIMARY KEY,
    network_id VARCHAR(50) REFERENCES social_networks(id),
    node_type VARCHAR(50),
    attributes JSONB
);

CREATE TABLE network_edges (
    id VARCHAR(50) PRIMARY KEY,
    network_id VARCHAR(50) REFERENCES social_networks(id),
    source VARCHAR(50),
    target VARCHAR(50),
    edge_type VARCHAR(50),
    weight FLOAT,
    attributes JSONB
);
```

---

## 6. 转换工具

### 6.1 开源工具

- **NetworkX**：Python网络分析库
- **Gephi**：网络可视化工具
- **igraph**：网络分析库

---

## 7. 转换验证

### 7.1 网络完整性验证

**验证方法**：

1. 验证节点和边的完整性
2. 验证网络属性一致性
3. 验证数据格式正确性

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
