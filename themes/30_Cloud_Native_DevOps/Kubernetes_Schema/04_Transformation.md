# Kubernetes Schema转换体系

## 📑 目录

- [Kubernetes Schema转换体系](#kubernetes-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Kubernetes到Helm转换](#2-kubernetes到helm转换)
  - [3. Kubernetes到Terraform转换](#3-kubernetes到terraform转换)
  - [4. Kubernetes到Docker Compose转换](#4-kubernetes到docker-compose转换)
  - [5. 转换验证](#5-转换验证)
  - [6. Kubernetes数据存储与分析](#6-kubernetes数据存储与分析)
    - [6.1 PostgreSQL Kubernetes数据存储](#61-postgresql-kubernetes数据存储)
    - [6.2 Kubernetes数据分析查询](#62-kubernetes数据分析查询)

---

## 1. 转换体系概述

Kubernetes Schema转换体系支持Kubernetes资源与其他配置格式之间的转换。

### 1.1 转换目标

1. **Kubernetes到Helm转换**：Kubernetes资源转换为Helm Chart
2. **Kubernetes到Terraform转换**：Kubernetes资源转换为Terraform配置
3. **Kubernetes到Docker Compose转换**：Kubernetes资源转换为Docker Compose配置
4. **Schema到数据库转换**：Kubernetes Schema定义到PostgreSQL存储

---

## 2. Kubernetes到Helm转换

**转换规则**：

- Kubernetes资源 → Helm模板
- Kubernetes配置 → Helm Values

**转换示例**：

```python
def kubernetes_to_helm(k8s_resource: dict) -> dict:
    """将Kubernetes资源转换为Helm模板"""
    helm_template = {
        "apiVersion": k8s_resource["apiVersion"],
        "kind": k8s_resource["kind"],
        "metadata": {
            "name": "{{ .Values.name }}",
            "namespace": "{{ .Values.namespace }}"
        },
        "spec": convert_spec_to_helm_values(k8s_resource["spec"])
    }
    return helm_template
```

---

## 3. Kubernetes到Terraform转换

**转换规则**：

- Kubernetes资源 → Terraform资源
- Kubernetes配置 → Terraform变量

---

## 4. Kubernetes到Docker Compose转换

**转换规则**：

- Kubernetes Pod → Docker Compose服务
- Kubernetes Service → Docker Compose网络

---

## 5. 转换验证

验证转换的资源完整性、配置一致性和功能等价性。

---

## 6. Kubernetes数据存储与分析

### 6.1 PostgreSQL Kubernetes数据存储

**Kubernetes数据存储方案**：

```python
import psycopg2
import json
from datetime import datetime

class KubernetesDataStore:
    """Kubernetes数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Kubernetes数据存储表"""
        with self.conn.cursor() as cur:
            # 资源定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kubernetes_resources (
                    id SERIAL PRIMARY KEY,
                    cluster_name VARCHAR(255) NOT NULL,
                    namespace VARCHAR(255),
                    api_version VARCHAR(50) NOT NULL,
                    kind VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    resource_definition JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cluster_name, namespace, api_version, kind, name)
                )
            """)

            # 资源事件表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kubernetes_events (
                    id SERIAL PRIMARY KEY,
                    resource_id INTEGER REFERENCES kubernetes_resources(id),
                    event_type VARCHAR(50) NOT NULL,
                    event_message TEXT,
                    event_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def store_resource(self, cluster_name: str, namespace: str,
                      api_version: str, kind: str, name: str,
                      resource_definition: dict):
        """存储Kubernetes资源定义"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO kubernetes_resources
                (cluster_name, namespace, api_version, kind, name, resource_definition)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (cluster_name, namespace, api_version, kind, name)
                DO UPDATE SET
                    resource_definition = EXCLUDED.resource_definition,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (cluster_name, namespace, api_version, kind, name,
                  json.dumps(resource_definition)))

            return cur.fetchone()[0]
```

### 6.2 Kubernetes数据分析查询

**分析查询示例**：

```python
def analyze_kubernetes_resources(db_config: Dict):
    """分析Kubernetes资源使用情况"""
    store = KubernetesDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询资源类型统计
        cur.execute("""
            SELECT
                kind,
                COUNT(*) as resource_count,
                COUNT(DISTINCT namespace) as namespace_count
            FROM kubernetes_resources
            GROUP BY kind
            ORDER BY resource_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
