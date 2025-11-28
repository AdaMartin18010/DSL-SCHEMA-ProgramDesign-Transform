# Helm Schema转换体系

## 📑 目录

- [Helm Schema转换体系](#helm-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. Helm到Kubernetes转换](#2-helm到kubernetes转换)
  - [3. Kubernetes到Helm转换](#3-kubernetes到helm转换)
  - [4. Helm到Terraform转换](#4-helm到terraform转换)
  - [5. 转换验证](#5-转换验证)
  - [6. Helm数据存储与分析](#6-helm数据存储与分析)
    - [6.1 PostgreSQL Helm数据存储](#61-postgresql-helm数据存储)
    - [6.2 Helm数据分析查询](#62-helm数据分析查询)

---

## 1. 转换体系概述

Helm Schema转换体系支持Helm Chart与其他配置格式之间的转换。

### 1.1 转换目标

1. **Helm到Kubernetes转换**：Helm Chart渲染为Kubernetes资源
2. **Kubernetes到Helm转换**：Kubernetes资源转换为Helm Chart
3. **Helm到Terraform转换**：Helm Chart转换为Terraform配置
4. **Schema到数据库转换**：Helm Schema定义到PostgreSQL存储

---

## 2. Helm到Kubernetes转换

**转换规则**：
- Helm模板 + Values → Kubernetes资源
- Helm Chart → Kubernetes资源集合

**转换示例**：

```python
def helm_to_kubernetes(chart_path: str, values: dict = None) -> list:
    """将Helm Chart渲染为Kubernetes资源"""
    import subprocess
    import yaml

    # 使用helm template命令渲染
    cmd = ["helm", "template", chart_path]
    if values:
        cmd.extend(["--values", values_file])

    result = subprocess.run(cmd, capture_output=True, text=True)
    resources = yaml.safe_load_all(result.stdout)
    return list(resources)
```

---

## 3. Kubernetes到Helm转换

**转换规则**：
- Kubernetes资源 → Helm模板
- Kubernetes配置 → Helm Values

---

## 4. Helm到Terraform转换

**转换规则**：
- Helm Chart → Terraform资源
- Helm Values → Terraform变量

---

## 5. 转换验证

验证转换的Chart完整性、模板有效性和资源一致性。

---

## 6. Helm数据存储与分析

### 6.1 PostgreSQL Helm数据存储

**Helm数据存储方案**：

```python
import psycopg2
import json

class HelmDataStore:
    """Helm数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Helm数据存储表"""
        with self.conn.cursor() as cur:
            # Chart定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS helm_charts (
                    id SERIAL PRIMARY KEY,
                    chart_name VARCHAR(255) NOT NULL UNIQUE,
                    chart_version VARCHAR(50) NOT NULL,
                    chart_metadata JSONB NOT NULL,
                    chart_path VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chart_name, chart_version)
                )
            """)

            # Values定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS helm_values (
                    id SERIAL PRIMARY KEY,
                    chart_id INTEGER REFERENCES helm_charts(id),
                    values_name VARCHAR(255),
                    values_definition JSONB NOT NULL,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Release表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS helm_releases (
                    id SERIAL PRIMARY KEY,
                    chart_id INTEGER REFERENCES helm_charts(id),
                    release_name VARCHAR(255) NOT NULL,
                    namespace VARCHAR(255),
                    values_id INTEGER REFERENCES helm_values(id),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(release_name, namespace)
                )
            """)

            self.conn.commit()
```

### 6.2 Helm数据分析查询

**分析查询示例**：

```python
def analyze_helm_usage(db_config: Dict):
    """分析Helm使用情况"""
    store = HelmDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询Chart使用统计
        cur.execute("""
            SELECT
                hc.chart_name,
                hc.chart_version,
                COUNT(hr.id) as release_count
            FROM helm_charts hc
            LEFT JOIN helm_releases hr ON hc.id = hr.chart_id
            GROUP BY hc.id, hc.chart_name, hc.chart_version
            ORDER BY release_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
