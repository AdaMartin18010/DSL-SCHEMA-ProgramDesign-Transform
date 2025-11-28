# GitOps Schema转换体系

## 📑 目录

- [GitOps Schema转换体系](#gitops-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ArgoCD到Flux转换](#2-argocd到flux转换)
  - [3. Flux到ArgoCD转换](#3-flux到argocd转换)
  - [4. GitOps到Kubernetes转换](#4-gitops到kubernetes转换)
  - [5. 转换验证](#5-转换验证)
  - [6. GitOps数据存储与分析](#6-gitops数据存储与分析)
    - [6.1 PostgreSQL GitOps数据存储](#61-postgresql-gitops数据存储)
    - [6.2 GitOps数据分析查询](#62-gitops数据分析查询)

---

## 1. 转换体系概述

GitOps Schema转换体系支持不同GitOps工具之间的转换。

### 1.1 转换目标

1. **ArgoCD到Flux转换**：ArgoCD应用转换为Flux配置
2. **Flux到ArgoCD转换**：Flux配置转换为ArgoCD应用
3. **GitOps到Kubernetes转换**：GitOps配置转换为Kubernetes资源
4. **Schema到数据库转换**：GitOps Schema定义到PostgreSQL存储

---

## 2. ArgoCD到Flux转换

**转换规则**：

- ArgoCD Application → Flux GitRepository + Kustomization
- ArgoCD同步策略 → Flux同步策略
- ArgoCD源配置 → Flux源配置

**转换示例**：

```python
def argocd_to_flux(argocd_app: dict) -> dict:
    """将ArgoCD应用转换为Flux配置"""
    flux_config = {
        "git_repository": {
            "apiVersion": "source.toolkit.fluxcd.io/v1beta1",
            "kind": "GitRepository",
            "metadata": {
                "name": argocd_app["metadata"]["name"],
                "namespace": "flux-system"
            },
            "spec": {
                "url": argocd_app["spec"]["source"]["repoURL"],
                "ref": {
                    "branch": argocd_app["spec"]["source"].get("targetRevision", "HEAD")
                },
                "interval": "1m"
            }
        },
        "kustomization": {
            "apiVersion": "kustomize.toolkit.fluxcd.io/v1beta2",
            "kind": "Kustomization",
            "metadata": {
                "name": argocd_app["metadata"]["name"],
                "namespace": "flux-system"
            },
            "spec": {
                "interval": "5m",
                "path": argocd_app["spec"]["source"]["path"],
                "prune": argocd_app["spec"]["syncPolicy"]["automated"].get("prune", False),
                "sourceRef": {
                    "kind": "GitRepository",
                    "name": argocd_app["metadata"]["name"]
                },
                "targetNamespace": argocd_app["spec"]["destination"]["namespace"]
            }
        }
    }
    return flux_config
```

---

## 3. Flux到ArgoCD转换

**转换规则**：

- Flux GitRepository + Kustomization → ArgoCD Application
- Flux同步策略 → ArgoCD同步策略

---

## 4. GitOps到Kubernetes转换

**转换规则**：

- GitOps应用配置 → Kubernetes资源
- GitOps同步策略 → Kubernetes配置

---

## 5. 转换验证

验证转换的配置完整性、同步策略一致性和功能等价性。

---

## 6. GitOps数据存储与分析

### 6.1 PostgreSQL GitOps数据存储

**GitOps数据存储方案**：

```python
import psycopg2
import json

class GitOpsDataStore:
    """GitOps数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建GitOps数据存储表"""
        with self.conn.cursor() as cur:
            # ArgoCD应用表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS argocd_applications (
                    id SERIAL PRIMARY KEY,
                    app_name VARCHAR(255) NOT NULL UNIQUE,
                    app_namespace VARCHAR(255) DEFAULT 'argocd',
                    app_definition JSONB NOT NULL,
                    sync_status VARCHAR(50),
                    health_status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Flux配置表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flux_configs (
                    id SERIAL PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL UNIQUE,
                    config_type VARCHAR(50) NOT NULL,
                    config_namespace VARCHAR(255) DEFAULT 'flux-system',
                    config_definition JSONB NOT NULL,
                    sync_status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Git仓库表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS git_repositories (
                    id SERIAL PRIMARY KEY,
                    repo_url VARCHAR(500) NOT NULL UNIQUE,
                    repo_branch VARCHAR(255),
                    repo_path VARCHAR(500),
                    authentication_config JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
```

### 6.2 GitOps数据分析查询

**分析查询示例**：

```python
def analyze_gitops_usage(db_config: Dict):
    """分析GitOps使用情况"""
    store = GitOpsDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询应用同步状态统计
        cur.execute("""
            SELECT
                sync_status,
                COUNT(*) as app_count
            FROM argocd_applications
            GROUP BY sync_status
            ORDER BY app_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
