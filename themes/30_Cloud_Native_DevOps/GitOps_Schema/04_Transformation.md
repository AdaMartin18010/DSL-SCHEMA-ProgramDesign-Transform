# GitOps Schema转换体系

## 📑 目录

- [GitOps Schema转换体系](#gitops-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ArgoCD到Flux转换](#2-argocd到flux转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Flux到ArgoCD转换](#3-flux到argocd转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. GitOps到Kubernetes转换](#4-gitops到kubernetes转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. GitOps数据存储与分析](#6-gitops数据存储与分析)
    - [6.1 PostgreSQL GitOps数据存储](#61-postgresql-gitops数据存储)
    - [6.2 GitOps数据分析查询](#62-gitops数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

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

### 2.1 转换规则

**资源映射规则**：

| ArgoCD资源 | Flux资源 | 映射说明 |
|-----------|---------|---------|
| `Application` | `GitRepository` + `Kustomization` | 拆分应用为源和同步 |
| `ApplicationSet` | `GitRepository` + 多个`Kustomization` | 批量转换 |
| `Project` | `Kustomization`策略 | 通过策略实现 |

**同步策略映射**：

- ArgoCD自动同步 → Flux自动同步（interval）
- ArgoCD手动同步 → Flux手动同步
- ArgoCD同步选项 → Flux同步选项

### 2.2 完整转换实现

**ArgoCD到Flux转换器**：

```python
#!/usr/bin/env python3
"""
ArgoCD到Flux转换器
"""

import yaml
import json
from typing import Dict, List, Any, Optional

class ArgoCDToFluxConverter:
    """ArgoCD到Flux转换器"""

    def __init__(self):
        self.flux_resources = []

    def convert_application(self, argocd_app: Dict) -> List[Dict]:
        """转换ArgoCD Application为Flux资源"""
        app_name = argocd_app['metadata']['name']
        app_namespace = argocd_app['metadata'].get('namespace', 'argocd')
        spec = argocd_app['spec']
        source = spec['source']
        destination = spec['destination']

        # 创建GitRepository
        git_repo = self._create_git_repository(
            app_name, source, app_namespace
        )

        # 创建Kustomization
        kustomization = self._create_kustomization(
            app_name, source, destination, spec, app_namespace
        )

        return [git_repo, kustomization]

    def convert_application_set(self, argocd_appset: Dict) -> List[Dict]:
        """转换ArgoCD ApplicationSet为Flux资源"""
        resources = []
        appset_name = argocd_appset['metadata']['name']
        spec = argocd_appset['spec']
        generators = spec.get('generators', [])
        template = spec.get('template', {})

        for generator in generators:
            if generator.get('list'):
                # List生成器
                for item in generator['list']['elements']:
                    app_name = f"{appset_name}-{item.get('cluster', 'default')}"
                    # 创建GitRepository和Kustomization
                    resources.extend(self._create_resources_from_template(
                        app_name, template, item
                    ))
            elif generator.get('git'):
                # Git生成器
                git_gen = generator['git']
                git_repo = self._create_git_repository(
                    f"{appset_name}-git",
                    {
                        'repoURL': git_gen['repoURL'],
                        'targetRevision': git_gen.get('revision', 'HEAD'),
                        'path': git_gen.get('directories', [{}])[0].get('path', '.')
                    },
                    'flux-system'
                )
                resources.append(git_repo)

        return resources

    def _create_git_repository(self, name: str, source: Dict,
                              namespace: str = 'flux-system') -> Dict:
        """创建Flux GitRepository资源"""
        git_repo = {
            'apiVersion': 'source.toolkit.fluxcd.io/v1beta2',
            'kind': 'GitRepository',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'url': source['repoURL'],
                'interval': '1m',
                'ref': {}
            }
        }

        # 设置引用
        target_revision = source.get('targetRevision', 'HEAD')
        if target_revision.startswith('refs/heads/'):
            git_repo['spec']['ref']['branch'] = target_revision.replace('refs/heads/', '')
        elif target_revision.startswith('refs/tags/'):
            git_repo['spec']['ref']['tag'] = target_revision.replace('refs/tags/', '')
        else:
            git_repo['spec']['ref']['branch'] = target_revision

        # 添加认证（如果存在）
        if 'credentials' in source:
            git_repo['spec']['secretRef'] = {
                'name': f"{name}-credentials"
            }

        return git_repo

    def _create_kustomization(self, name: str, source: Dict,
                             destination: Dict, spec: Dict,
                             namespace: str = 'flux-system') -> Dict:
        """创建Flux Kustomization资源"""
        kustomization = {
            'apiVersion': 'kustomize.toolkit.fluxcd.io/v1',
            'kind': 'Kustomization',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'interval': '5m',
                'path': source.get('path', '.'),
                'prune': False,
                'sourceRef': {
                    'kind': 'GitRepository',
                    'name': name
                },
                'targetNamespace': destination.get('namespace', 'default')
            }
        }

        # 同步策略
        sync_policy = spec.get('syncPolicy', {})
        if sync_policy.get('automated'):
            automated = sync_policy['automated']
            kustomization['spec']['prune'] = automated.get('prune', False)
            kustomization['spec']['interval'] = '1m'  # 自动同步

        # 同步选项
        sync_options = sync_policy.get('syncOptions', [])
        if 'CreateNamespace=true' in sync_options:
            kustomization['spec']['targetNamespace'] = destination.get('namespace', 'default')

        # 健康检查
        if sync_policy.get('syncOptions'):
            health_checks = []
            for option in sync_policy['syncOptions']:
                if option.startswith('HealthCheck='):
                    health_checks.append(option.split('=')[1])
            if health_checks:
                kustomization['spec']['healthChecks'] = health_checks

        return kustomization

    def _create_resources_from_template(self, name: str, template: Dict,
                                       params: Dict) -> List[Dict]:
        """从模板创建资源"""
        # 简化实现
        return []

# 使用示例
if __name__ == '__main__':
    converter = ArgoCDToFluxConverter()

    # ArgoCD Application示例
    argocd_app = {
        'apiVersion': 'argoproj.io/v1alpha1',
        'kind': 'Application',
        'metadata': {
            'name': 'my-app',
            'namespace': 'argocd'
        },
        'spec': {
            'project': 'default',
            'source': {
                'repoURL': 'https://github.com/example/my-app',
                'targetRevision': 'HEAD',
                'path': 'k8s'
            },
            'destination': {
                'server': 'https://kubernetes.default.svc',
                'namespace': 'production'
            },
            'syncPolicy': {
                'automated': {
                    'prune': True,
                    'selfHeal': True
                }
            }
        }
    }

    # 转换
    flux_resources = converter.convert_application(argocd_app)

    # 输出YAML
    for resource in flux_resources:
        print(yaml.dump(resource, default_flow_style=False))
        print('---')
```

---

## 3. Flux到ArgoCD转换

### 3.1 转换规则

**资源映射规则**：

- Flux `GitRepository` + `Kustomization` → ArgoCD `Application`
- Flux `HelmRelease` → ArgoCD `Application`（Helm源）
- Flux同步策略 → ArgoCD同步策略

### 3.2 转换实现

**Flux到ArgoCD转换器**：

```python
class FluxToArgoCDConverter:
    """Flux到ArgoCD转换器"""

    def convert(self, git_repo: Dict, kustomization: Dict) -> Dict:
        """转换Flux资源为ArgoCD Application"""
        app_name = kustomization['metadata']['name']

        argocd_app = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'Application',
            'metadata': {
                'name': app_name,
                'namespace': 'argocd'
            },
            'spec': {
                'project': 'default',
                'source': {
                    'repoURL': git_repo['spec']['url'],
                    'targetRevision': self._get_revision(git_repo),
                    'path': kustomization['spec'].get('path', '.')
                },
                'destination': {
                    'server': 'https://kubernetes.default.svc',
                    'namespace': kustomization['spec'].get('targetNamespace', 'default')
                },
                'syncPolicy': self._convert_sync_policy(kustomization)
            }
        }

        return argocd_app

    def _get_revision(self, git_repo: Dict) -> str:
        """获取Git引用"""
        ref = git_repo['spec'].get('ref', {})
        if 'branch' in ref:
            return ref['branch']
        elif 'tag' in ref:
            return ref['tag']
        return 'HEAD'

    def _convert_sync_policy(self, kustomization: Dict) -> Dict:
        """转换同步策略"""
        spec = kustomization['spec']
        interval = spec.get('interval', '5m')

        sync_policy = {}
        if interval == '1m':  # 自动同步
            sync_policy['automated'] = {
                'prune': spec.get('prune', False),
                'selfHeal': True
            }

        return sync_policy
```

---

## 4. GitOps到Kubernetes转换

### 4.1 转换规则

**资源映射规则**：

- GitOps应用配置 → Kubernetes资源（通过Git仓库）
- GitOps同步策略 → Kubernetes资源状态

### 4.2 转换实现

**GitOps到Kubernetes资源转换**：

```python
def gitops_to_kubernetes(git_repo_url: str, path: str) -> List[Dict]:
    """从GitOps配置生成Kubernetes资源"""
    # 克隆Git仓库
    # 读取指定路径的Kubernetes资源
    # 返回资源列表
    pass
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有应用都已转换
- 所有源配置都已映射
- 所有同步策略都已转换

**一致性验证**：

- 同步策略一致性
- 源配置一致性
- 目标配置一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 同步行为一致
- 健康检查一致

### 5.2 验证实现

**转换验证器**：

```python
class GitOpsConversionValidator:
    """GitOps转换验证器"""

    def validate(self, source_config: Dict, target_config: Dict) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(source_config, target_config),
            'consistency': self._validate_consistency(source_config, target_config),
            'equivalence': self._validate_equivalence(source_config, target_config)
        }
        return results
```

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

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理配置**：
   - 移除未使用的应用
   - 标准化命名
   - 验证配置正确性

2. **备份数据**：
   - 备份ArgoCD配置
   - 备份Flux配置
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换测试环境
   - 验证转换结果
   - 再转换生产环境

2. **验证转换结果**：
   - 检查资源完整性
   - 验证同步策略
   - 测试功能等价性

### 7.3 转换后优化

1. **优化配置**：
   - 调整同步策略
   - 优化资源组织
   - 添加监控和告警

2. **测试和验证**：
   - 在测试环境验证
   - 逐步迁移生产环境
   - 监控同步状态

## 8. 转换工具和资源

### 8.1 转换工具

- **argocd-to-flux**：ArgoCD到Flux转换工具
- **flux-to-argocd**：Flux到ArgoCD转换工具

### 8.2 参考资源

- [ArgoCD文档](https://argo-cd.readthedocs.io/)
- [Flux文档](https://fluxcd.io/)
- [GitOps转换指南](https://www.weave.works/technologies/gitops/)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
