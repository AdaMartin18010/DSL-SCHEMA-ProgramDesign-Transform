# Kubernetes Schema转换体系

## 📑 目录

- [Kubernetes Schema转换体系](#kubernetes-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Kubernetes到Helm转换](#2-kubernetes到helm转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Kubernetes到Terraform转换](#3-kubernetes到terraform转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. Kubernetes到Docker Compose转换](#4-kubernetes到docker-compose转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. Kubernetes数据存储与分析](#6-kubernetes数据存储与分析)
    - [6.1 PostgreSQL Kubernetes数据存储](#61-postgresql-kubernetes数据存储)
    - [6.2 Kubernetes数据分析查询](#62-kubernetes数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

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

### 2.1 转换规则

**资源映射规则**：

- Kubernetes资源 → Helm模板文件
- 硬编码值 → Helm Values变量
- 资源名称 → Helm模板函数

### 2.2 完整转换实现

**Kubernetes到Helm转换器**：

```python
#!/usr/bin/env python3
"""
Kubernetes到Helm转换器
"""

import yaml
import json
from typing import Dict, List, Any
from pathlib import Path

class KubernetesToHelmConverter:
    """Kubernetes到Helm转换器"""

    def __init__(self, chart_name: str):
        self.chart_name = chart_name
        self.values = {}
        self.templates = []

    def convert_resources(self, k8s_resources: List[Dict]) -> Dict:
        """转换Kubernetes资源为Helm Chart"""
        # 创建Chart.yaml
        chart_yaml = self._create_chart_yaml()

        # 转换资源为模板
        for resource in k8s_resources:
            template = self._convert_resource_to_template(resource)
            self.templates.append(template)

        # 创建values.yaml
        values_yaml = self._create_values_yaml()

        return {
            'Chart.yaml': chart_yaml,
            'values.yaml': values_yaml,
            'templates': self.templates
        }

    def _create_chart_yaml(self) -> Dict:
        """创建Chart.yaml"""
        return {
            'apiVersion': 'v2',
            'name': self.chart_name,
            'description': f'A Helm chart for {self.chart_name}',
            'type': 'application',
            'version': '0.1.0',
            'appVersion': '1.0.0'
        }

    def _convert_resource_to_template(self, resource: Dict) -> Dict:
        """转换Kubernetes资源为Helm模板"""
        template = {
            'apiVersion': resource['apiVersion'],
            'kind': resource['kind'],
            'metadata': self._convert_metadata(resource.get('metadata', {})),
        }

        if 'spec' in resource:
            template['spec'] = self._convert_spec(resource['spec'], resource['kind'])

        return template

    def _convert_metadata(self, metadata: Dict) -> Dict:
        """转换元数据"""
        converted = {}

        # 名称使用模板函数
        if 'name' in metadata:
            converted['name'] = "{{ include \"%s.fullname\" . }}" % self.chart_name

        # 命名空间使用Values
        if 'namespace' in metadata:
            converted['namespace'] = "{{ .Values.namespace }}"
            self.values['namespace'] = metadata['namespace']

        # 标签
        if 'labels' in metadata:
            converted['labels'] = {
                "{{- include \"%s.labels\" . | nindent 4 }}" % self.chart_name: None
            }

        # 注解
        if 'annotations' in metadata:
            converted['annotations'] = metadata['annotations']

        return converted

    def _convert_spec(self, spec: Dict, kind: str) -> Dict:
        """转换spec"""
        converted = {}

        if kind == 'Deployment':
            converted = self._convert_deployment_spec(spec)
        elif kind == 'Service':
            converted = self._convert_service_spec(spec)
        elif kind == 'ConfigMap':
            converted = self._convert_configmap_spec(spec)
        else:
            # 通用转换
            converted = self._convert_generic_spec(spec)

        return converted

    def _convert_deployment_spec(self, spec: Dict) -> Dict:
        """转换Deployment spec"""
        converted = {}

        # 副本数
        if 'replicas' in spec:
            converted['replicas'] = "{{ .Values.replicaCount }}"
            self.values['replicaCount'] = spec['replicas']

        # 选择器
        if 'selector' in spec:
            converted['selector'] = {
                'matchLabels': {
                    "{{- include \"%s.selectorLabels\" . | nindent 6 }}" % self.chart_name: None
                }
            }

        # Pod模板
        if 'template' in spec:
            converted['template'] = self._convert_pod_template(spec['template'])

        return converted

    def _convert_pod_template(self, template: Dict) -> Dict:
        """转换Pod模板"""
        converted = {
            'metadata': self._convert_metadata(template.get('metadata', {}))
        }

        if 'spec' in template:
            pod_spec = {}

            # 容器
            if 'containers' in template['spec']:
                pod_spec['containers'] = self._convert_containers(
                    template['spec']['containers']
                )

            # 资源限制
            if 'resources' in template['spec']:
                pod_spec['resources'] = template['spec']['resources']

            converted['spec'] = pod_spec

        return converted

    def _convert_containers(self, containers: List[Dict]) -> List[Dict]:
        """转换容器"""
        converted = []

        for i, container in enumerate(containers):
            container_template = {
                'name': container.get('name', f'container-{i}'),
                'image': "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
            }

            # 设置默认值
            if 'image' in container:
                image_parts = container['image'].split(':')
                if 'image' not in self.values:
                    self.values['image'] = {}
                self.values['image']['repository'] = image_parts[0]
                if len(image_parts) > 1:
                    self.values['image']['tag'] = image_parts[1]

            # 端口
            if 'ports' in container:
                container_template['ports'] = container['ports']

            # 环境变量
            if 'env' in container:
                container_template['env'] = self._convert_env_vars(container['env'])

            # 资源
            if 'resources' in container:
                container_template['resources'] = container['resources']

            converted.append(container_template)

        return converted

    def _convert_env_vars(self, env_vars: List[Dict]) -> List[Dict]:
        """转换环境变量"""
        converted = []

        for env_var in env_vars:
            if 'value' in env_var:
                # 直接值
                converted.append(env_var)
            elif 'valueFrom' in env_var:
                # 从ConfigMap或Secret引用
                converted.append(env_var)

        return converted

    def _convert_service_spec(self, spec: Dict) -> Dict:
        """转换Service spec"""
        converted = {}

        if 'type' in spec:
            converted['type'] = "{{ .Values.service.type }}"
            self.values['service'] = {'type': spec['type']}

        if 'ports' in spec:
            converted['ports'] = spec['ports']
            if 'service' not in self.values:
                self.values['service'] = {}
            self.values['service']['ports'] = spec['ports']

        if 'selector' in spec:
            converted['selector'] = {
                "{{- include \"%s.selectorLabels\" . | nindent 4 }}" % self.chart_name: None
            }

        return converted

    def _convert_configmap_spec(self, spec: Dict) -> Dict:
        """转换ConfigMap spec"""
        converted = {}

        if 'data' in spec:
            converted['data'] = spec['data']

        return converted

    def _convert_generic_spec(self, spec: Dict) -> Dict:
        """通用spec转换"""
        return spec

    def _create_values_yaml(self) -> Dict:
        """创建values.yaml"""
        return self.values

# 使用示例
if __name__ == '__main__':
    converter = KubernetesToHelmConverter('my-app')

    # Kubernetes资源示例
    k8s_resources = [
        {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'my-app',
                'namespace': 'default'
            },
            'spec': {
                'replicas': 3,
                'selector': {
                    'matchLabels': {
                        'app': 'my-app'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'my-app'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'my-app',
                            'image': 'my-app:1.0.0',
                            'ports': [{
                                'containerPort': 8080
                            }]
                        }]
                    }
                }
            }
        }
    ]

    # 转换
    helm_chart = converter.convert_resources(k8s_resources)

    # 输出
    print("Chart.yaml:")
    print(yaml.dump(helm_chart['Chart.yaml']))
    print("\nvalues.yaml:")
    print(yaml.dump(helm_chart['values.yaml']))
    print("\nTemplates:")
    for template in helm_chart['templates']:
        print(yaml.dump(template))
        print('---')
```

---

## 3. Kubernetes到Terraform转换

### 3.1 转换规则

**资源映射规则**：

- Kubernetes资源 → Terraform `kubernetes_*`资源
- Kubernetes配置 → Terraform变量和输出

### 3.2 转换实现

**Kubernetes到Terraform转换器**：

```python
class KubernetesToTerraformConverter:
    """Kubernetes到Terraform转换器"""

    def convert(self, k8s_resource: Dict) -> str:
        """转换Kubernetes资源为Terraform配置"""
        resource_type = self._get_terraform_resource_type(
            k8s_resource['apiVersion'], k8s_resource['kind']
        )

        resource_name = k8s_resource['metadata']['name'].replace('-', '_')

        tf_config = f"""
resource "{resource_type}" "{resource_name}" {{
  metadata {{
    name      = "{k8s_resource['metadata']['name']}"
    namespace = "{k8s_resource['metadata'].get('namespace', 'default')}"
  }}

  spec {{
    {self._convert_spec_to_hcl(k8s_resource.get('spec', {}))}
  }}
}}
"""
        return tf_config

    def _get_terraform_resource_type(self, api_version: str, kind: str) -> str:
        """获取Terraform资源类型"""
        mapping = {
            ('apps/v1', 'Deployment'): 'kubernetes_deployment',
            ('v1', 'Service'): 'kubernetes_service',
            ('v1', 'ConfigMap'): 'kubernetes_config_map',
            ('v1', 'Secret'): 'kubernetes_secret',
        }
        return mapping.get((api_version, kind), 'kubernetes_manifest')
```

---

## 4. Kubernetes到Docker Compose转换

### 4.1 转换规则

**资源映射规则**：

- Kubernetes Pod → Docker Compose服务
- Kubernetes Service → Docker Compose网络和端口映射
- Kubernetes ConfigMap → Docker Compose环境变量

### 4.2 转换实现

**Kubernetes到Docker Compose转换器**：

```python
class KubernetesToDockerComposeConverter:
    """Kubernetes到Docker Compose转换器"""

    def convert(self, k8s_resources: List[Dict]) -> Dict:
        """转换Kubernetes资源为Docker Compose配置"""
        compose_config = {
            'version': '3.8',
            'services': {},
            'networks': {
                'default': {}
            }
        }

        for resource in k8s_resources:
            if resource['kind'] == 'Pod':
                service = self._convert_pod_to_service(resource)
                compose_config['services'][service['name']] = service

        return compose_config

    def _convert_pod_to_service(self, pod: Dict) -> Dict:
        """转换Pod为Docker Compose服务"""
        spec = pod['spec']
        containers = spec.get('containers', [])

        if not containers:
            return {}

        container = containers[0]
        service = {
            'image': container.get('image', ''),
            'ports': [],
            'environment': []
        }

        # 端口映射
        for port in container.get('ports', []):
            service['ports'].append(f"{port.get('containerPort', 8080)}:{port.get('containerPort', 8080)}")

        # 环境变量
        for env in container.get('env', []):
            if 'value' in env:
                service['environment'].append(f"{env['name']}={env['value']}")

        return service
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有资源都已转换
- 所有配置都已映射
- 所有依赖关系都已处理

**一致性验证**：

- 资源属性一致性
- 配置值一致性
- 依赖关系一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 资源行为一致
- 网络和存储配置一致

### 5.2 验证实现

**转换验证器**：

```python
class KubernetesConversionValidator:
    """Kubernetes转换验证器"""

    def validate(self, source_resources: List[Dict],
                target_config: Dict) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(source_resources, target_config),
            'consistency': self._validate_consistency(source_resources, target_config),
            'equivalence': self._validate_equivalence(source_resources, target_config)
        }
        return results
```

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

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理Kubernetes资源**：
   - 移除未使用的资源
   - 标准化命名
   - 验证资源正确性

2. **备份数据**：
   - 备份Kubernetes配置
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心资源
   - 再转换依赖资源
   - 最后转换配置

2. **验证转换结果**：
   - 检查资源完整性
   - 验证配置映射
   - 测试功能等价性

### 7.3 转换后优化

1. **优化配置**：
   - 参数化配置值
   - 优化资源组织
   - 添加文档

2. **测试和验证**：
   - 在测试环境验证
   - 逐步迁移生产环境
   - 监控资源状态

## 8. 转换工具和资源

### 8.1 转换工具

- **kompose**：Kubernetes到Docker Compose转换
- **helmify**：Kubernetes到Helm转换
- **kube2terraform**：Kubernetes到Terraform转换

### 8.2 参考资源

- [Kubernetes文档](https://kubernetes.io/docs/)
- [Helm文档](https://helm.sh/docs/)
- [Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
