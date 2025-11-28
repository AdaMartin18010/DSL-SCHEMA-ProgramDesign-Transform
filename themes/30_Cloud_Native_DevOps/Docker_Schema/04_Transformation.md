# Docker Schema转换体系

## 📑 目录

- [Docker Schema转换体系](#docker-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Docker到Kubernetes转换](#2-docker到kubernetes转换)
  - [3. Docker Compose到Kubernetes转换](#3-docker-compose到kubernetes转换)
  - [4. Docker到Helm转换](#4-docker到helm转换)
  - [5. 转换验证](#5-转换验证)
  - [6. Docker数据存储与分析](#6-docker数据存储与分析)
    - [6.1 PostgreSQL Docker数据存储](#61-postgresql-docker数据存储)
    - [6.2 Docker数据分析查询](#62-docker数据分析查询)

---

## 1. 转换体系概述

Docker Schema转换体系支持Docker配置与其他容器编排格式之间的转换。

### 1.1 转换目标

1. **Docker到Kubernetes转换**：Docker配置转换为Kubernetes资源
2. **Docker Compose到Kubernetes转换**：Docker Compose配置转换为Kubernetes资源
3. **Docker到Helm转换**：Docker配置转换为Helm Chart
4. **Schema到数据库转换**：Docker Schema定义到PostgreSQL存储

---

## 2. Docker到Kubernetes转换

**转换规则**：

- Docker容器 → Kubernetes Pod
- Docker镜像 → Kubernetes容器镜像
- Docker网络 → Kubernetes Service

**转换示例**：

```python
def docker_to_kubernetes(dockerfile: str, docker_compose: dict = None) -> dict:
    """将Docker配置转换为Kubernetes资源"""
    if docker_compose:
        return convert_compose_to_kubernetes(docker_compose)
    else:
        return convert_dockerfile_to_kubernetes(dockerfile)
```

---

## 3. Docker Compose到Kubernetes转换

**转换规则**：

- Docker Compose服务 → Kubernetes Deployment
- Docker Compose网络 → Kubernetes Service
- Docker Compose卷 → Kubernetes Volume

---

## 4. Docker到Helm转换

**转换规则**：

- Docker配置 → Helm Chart模板
- Docker环境变量 → Helm Values

---

## 5. 转换验证

验证转换的配置完整性、资源一致性和功能等价性。

---

## 6. Docker数据存储与分析

### 6.1 PostgreSQL Docker数据存储

**Docker数据存储方案**：

```python
import psycopg2
import json

class DockerDataStore:
    """Docker数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Docker数据存储表"""
        with self.conn.cursor() as cur:
            # Dockerfile定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dockerfiles (
                    id SERIAL PRIMARY KEY,
                    dockerfile_name VARCHAR(255) NOT NULL UNIQUE,
                    dockerfile_content TEXT NOT NULL,
                    base_image VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Docker Compose定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS docker_composes (
                    id SERIAL PRIMARY KEY,
                    compose_name VARCHAR(255) NOT NULL UNIQUE,
                    compose_definition JSONB NOT NULL,
                    version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Docker镜像表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS docker_images (
                    id SERIAL PRIMARY KEY,
                    image_name VARCHAR(255) NOT NULL,
                    image_tag VARCHAR(50),
                    image_id VARCHAR(255),
                    size_bytes BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(image_name, image_tag)
                )
            """)

            self.conn.commit()
```

### 6.2 Docker数据分析查询

**分析查询示例**：

```python
def analyze_docker_usage(db_config: Dict):
    """分析Docker使用情况"""
    store = DockerDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询镜像使用统计
        cur.execute("""
            SELECT
                image_name,
                COUNT(*) as usage_count,
                SUM(size_bytes) as total_size
            FROM docker_images
            GROUP BY image_name
            ORDER BY usage_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
