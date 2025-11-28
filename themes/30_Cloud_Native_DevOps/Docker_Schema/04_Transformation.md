# Docker Schema转换体系

## 📑 目录

- [Docker Schema转换体系](#docker-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Docker到Kubernetes转换](#2-docker到kubernetes转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Docker Compose到Kubernetes转换](#3-docker-compose到kubernetes转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 完整转换实现](#32-完整转换实现)
  - [4. Docker到Helm转换](#4-docker到helm转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. Docker数据存储与分析](#6-docker数据存储与分析)
    - [6.1 PostgreSQL Docker数据存储](#61-postgresql-docker数据存储)
    - [6.2 Docker数据分析查询](#62-docker数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

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

### 2.1 转换规则

**资源映射规则**：

- Docker容器 → Kubernetes Pod/Deployment
- Docker镜像 → Kubernetes容器镜像
- Docker网络 → Kubernetes Service
- Docker卷 → Kubernetes Volume/PersistentVolumeClaim
- Docker环境变量 → Kubernetes ConfigMap/Secret

### 2.2 完整转换实现

**Docker到Kubernetes转换器**：

```python
#!/usr/bin/env python3
"""
Docker到Kubernetes转换器
"""

import yaml
import json
from typing import Dict, List, Any, Optional
import re

class DockerToKubernetesConverter:
    """Docker到Kubernetes转换器"""

    def __init__(self):
        self.k8s_resources = []

    def convert_dockerfile(self, dockerfile_path: str) -> List[Dict]:
        """从Dockerfile转换为Kubernetes资源"""
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()

        # 解析Dockerfile
        dockerfile_info = self._parse_dockerfile(dockerfile_content)

        # 创建Deployment
        deployment = self._create_deployment_from_dockerfile(dockerfile_info)
        self.k8s_resources.append(deployment)

        # 创建Service（如果需要）
        if dockerfile_info.get('expose_ports'):
            service = self._create_service_from_dockerfile(dockerfile_info)
            self.k8s_resources.append(service)

        return self.k8s_resources

    def _parse_dockerfile(self, content: str) -> Dict:
        """解析Dockerfile"""
        info = {
            'base_image': None,
            'workdir': None,
            'expose_ports': [],
            'env_vars': {},
            'volumes': [],
            'cmd': None,
            'entrypoint': None
        }

        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # FROM指令
            if line.upper().startswith('FROM'):
                match = re.match(r'FROM\s+(.+)', line, re.IGNORECASE)
                if match:
                    info['base_image'] = match.group(1).split()[0]

            # EXPOSE指令
            elif line.upper().startswith('EXPOSE'):
                match = re.match(r'EXPOSE\s+(.+)', line, re.IGNORECASE)
                if match:
                    ports = match.group(1).split()
                    info['expose_ports'].extend([int(p) for p in ports])

            # ENV指令
            elif line.upper().startswith('ENV'):
                match = re.match(r'ENV\s+(.+?)\s+(.+)', line, re.IGNORECASE)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip('"\'')
                    info['env_vars'][key] = value

            # WORKDIR指令
            elif line.upper().startswith('WORKDIR'):
                match = re.match(r'WORKDIR\s+(.+)', line, re.IGNORECASE)
                if match:
                    info['workdir'] = match.group(1)

            # VOLUME指令
            elif line.upper().startswith('VOLUME'):
                match = re.match(r'VOLUME\s+\[(.+)\]', line, re.IGNORECASE)
                if match:
                    volumes = [v.strip(' "\'') for v in match.group(1).split(',')]
                    info['volumes'].extend(volumes)

            # CMD指令
            elif line.upper().startswith('CMD'):
                match = re.match(r'CMD\s+(.+)', line, re.IGNORECASE)
                if match:
                    info['cmd'] = match.group(1)

            # ENTRYPOINT指令
            elif line.upper().startswith('ENTRYPOINT'):
                match = re.match(r'ENTRYPOINT\s+(.+)', line, re.IGNORECASE)
                if match:
                    info['entrypoint'] = match.group(1)

        return info

    def _create_deployment_from_dockerfile(self, dockerfile_info: Dict) -> Dict:
        """从Dockerfile信息创建Deployment"""
        app_name = 'app'  # 默认名称

        containers = [{
            'name': app_name,
            'image': dockerfile_info.get('base_image', 'nginx:latest'),
            'ports': [{'containerPort': port} for port in dockerfile_info.get('expose_ports', [8080])],
            'env': [{'name': k, 'value': v} for k, v in dockerfile_info.get('env_vars', {}).items()],
            'workingDir': dockerfile_info.get('workdir'),
            'command': self._parse_command(dockerfile_info.get('entrypoint')),
            'args': self._parse_command(dockerfile_info.get('cmd'))
        }]

        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': app_name,
                'labels': {
                    'app': app_name
                }
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {
                        'app': app_name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': app_name
                        }
                    },
                    'spec': {
                        'containers': containers
                    }
                }
            }
        }

        return deployment

    def _create_service_from_dockerfile(self, dockerfile_info: Dict) -> Dict:
        """从Dockerfile信息创建Service"""
        app_name = 'app'
        ports = dockerfile_info.get('expose_ports', [8080])

        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f'{app_name}-service',
                'labels': {
                    'app': app_name
                }
            },
            'spec': {
                'type': 'ClusterIP',
                'selector': {
                    'app': app_name
                },
                'ports': [{
                    'port': port,
                    'targetPort': port,
                    'protocol': 'TCP'
                } for port in ports]
            }
        }

        return service

    def _parse_command(self, command_str: Optional[str]) -> Optional[List[str]]:
        """解析命令字符串"""
        if not command_str:
            return None

        # 处理JSON格式
        if command_str.startswith('['):
            try:
                return json.loads(command_str)
            except:
                pass

        # 处理字符串格式
        return command_str.split()

# 使用示例
if __name__ == '__main__':
    converter = DockerToKubernetesConverter()

    # 示例Dockerfile
    dockerfile_content = """
FROM python:3.9-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
"""

    # 写入临时文件
    with open('/tmp/Dockerfile', 'w') as f:
        f.write(dockerfile_content)

    # 转换
    k8s_resources = converter.convert_dockerfile('/tmp/Dockerfile')

    # 输出YAML
    for resource in k8s_resources:
        print(yaml.dump(resource, default_flow_style=False))
        print('---')
```

---

## 3. Docker Compose到Kubernetes转换

### 3.1 转换规则

**资源映射规则**：

- Docker Compose服务 → Kubernetes Deployment
- Docker Compose网络 → Kubernetes Service
- Docker Compose卷 → Kubernetes PersistentVolumeClaim
- Docker Compose依赖 → Kubernetes InitContainer

### 3.2 完整转换实现

**Docker Compose到Kubernetes转换器**：

```python
class DockerComposeToKubernetesConverter:
    """Docker Compose到Kubernetes转换器"""

    def convert(self, compose_file: str) -> List[Dict]:
        """转换Docker Compose文件为Kubernetes资源"""
        with open(compose_file, 'r') as f:
            compose_config = yaml.safe_load(f)

        services = compose_config.get('services', {})
        networks = compose_config.get('networks', {})
        volumes = compose_config.get('volumes', {})

        k8s_resources = []

        # 转换每个服务
        for service_name, service_config in services.items():
            # 创建Deployment
            deployment = self._create_deployment(service_name, service_config)
            k8s_resources.append(deployment)

            # 创建Service
            if service_config.get('ports'):
                service = self._create_service(service_name, service_config)
                k8s_resources.append(service)

            # 创建ConfigMap（环境变量）
            if service_config.get('environment'):
                configmap = self._create_configmap(service_name, service_config)
                k8s_resources.append(configmap)

        # 创建PersistentVolumeClaim（卷）
        for volume_name, volume_config in volumes.items():
            pvc = self._create_pvc(volume_name, volume_config)
            k8s_resources.append(pvc)

        return k8s_resources

    def _create_deployment(self, service_name: str, service_config: Dict) -> Dict:
        """创建Deployment"""
        containers = [{
            'name': service_name,
            'image': service_config.get('image', ''),
            'ports': [{'containerPort': p.split(':')[1] if ':' in str(p) else p}
                     for p in service_config.get('ports', [])],
            'env': [{'name': k, 'value': str(v)}
                   for k, v in service_config.get('environment', {}).items()],
            'volumeMounts': [{'name': v.split(':')[0], 'mountPath': v.split(':')[1]}
                           for v in service_config.get('volumes', []) if ':' in v]
        }]

        volumes = []
        for vol in service_config.get('volumes', []):
            if ':' in vol:
                vol_name = vol.split(':')[0]
                volumes.append({'name': vol_name, 'persistentVolumeClaim': {'claimName': vol_name}})

        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {'name': service_name},
            'spec': {
                'replicas': service_config.get('deploy', {}).get('replicas', 1),
                'selector': {'matchLabels': {'app': service_name}},
                'template': {
                    'metadata': {'labels': {'app': service_name}},
                    'spec': {
                        'containers': containers,
                        'volumes': volumes
                    }
                }
            }
        }

    def _create_service(self, service_name: str, service_config: Dict) -> Dict:
        """创建Service"""
        ports = []
        for port in service_config.get('ports', []):
            if isinstance(port, str) and ':' in port:
                host_port, container_port = port.split(':')
                ports.append({
                    'port': int(host_port),
                    'targetPort': int(container_port),
                    'protocol': 'TCP'
                })
            else:
                ports.append({
                    'port': int(port),
                    'targetPort': int(port),
                    'protocol': 'TCP'
                })

        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {'name': f'{service_name}-service'},
            'spec': {
                'type': 'ClusterIP',
                'selector': {'app': service_name},
                'ports': ports
            }
        }

    def _create_configmap(self, service_name: str, service_config: Dict) -> Dict:
        """创建ConfigMap"""
        return {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {'name': f'{service_name}-config'},
            'data': {k: str(v) for k, v in service_config.get('environment', {}).items()}
        }

    def _create_pvc(self, volume_name: str, volume_config: Dict) -> Dict:
        """创建PersistentVolumeClaim"""
        return {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {'name': volume_name},
            'spec': {
                'accessModes': ['ReadWriteOnce'],
                'resources': {
                    'requests': {
                        'storage': volume_config.get('driver_opts', {}).get('size', '10Gi')
                    }
                }
            }
        }
```

---

## 4. Docker到Helm转换

### 4.1 转换规则

**资源映射规则**：

- Docker配置 → Helm Chart模板
- Docker环境变量 → Helm Values
- Docker端口 → Helm Values

### 4.2 转换实现

**Docker到Helm转换器**：

```python
class DockerToHelmConverter:
    """Docker到Helm转换器"""

    def convert(self, dockerfile_path: str, chart_name: str) -> Dict:
        """转换Dockerfile为Helm Chart"""
        # 解析Dockerfile
        dockerfile_info = self._parse_dockerfile(dockerfile_path)

        # 创建Chart.yaml
        chart_yaml = {
            'apiVersion': 'v2',
            'name': chart_name,
            'description': f'Helm chart for {chart_name}',
            'type': 'application',
            'version': '0.1.0',
            'appVersion': dockerfile_info.get('base_image', '1.0.0')
        }

        # 创建values.yaml
        values_yaml = {
            'image': {
                'repository': dockerfile_info.get('base_image', '').split(':')[0],
                'tag': dockerfile_info.get('base_image', '').split(':')[1] if ':' in dockerfile_info.get('base_image', '') else 'latest'
            },
            'service': {
                'type': 'ClusterIP',
                'port': dockerfile_info.get('expose_ports', [8080])[0]
            },
            'env': dockerfile_info.get('env_vars', {}),
            'replicaCount': 1
        }

        # 创建Deployment模板
        deployment_template = self._create_deployment_template(chart_name, dockerfile_info)

        return {
            'Chart.yaml': chart_yaml,
            'values.yaml': values_yaml,
            'templates/deployment.yaml': deployment_template
        }

    def _create_deployment_template(self, chart_name: str, dockerfile_info: Dict) -> Dict:
        """创建Deployment模板"""
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': "{{ include \"%s.fullname\" . }}" % chart_name,
                'labels': "{{- include \"%s.labels\" . | nindent 4 }}" % chart_name
            },
            'spec': {
                'replicas': "{{ .Values.replicaCount }}",
                'selector': {
                    'matchLabels': "{{- include \"%s.selectorLabels\" . | nindent 6 }}" % chart_name
                },
                'template': {
                    'metadata': {
                        'labels': "{{- include \"%s.selectorLabels\" . | nindent 8 }}" % chart_name
                    },
                    'spec': {
                        'containers': [{
                            'name': chart_name,
                            'image': "{{ .Values.image.repository }}:{{ .Values.image.tag }}",
                            'ports': [{
                                'containerPort': "{{ .Values.service.port }}"
                            }],
                            'env': [
                                {'name': k, 'value': "{{ .Values.env.%s }}" % k}
                                for k in dockerfile_info.get('env_vars', {}).keys()
                            ]
                        }]
                    }
                }
            }
        }
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有Docker配置都已转换
- 所有端口都已映射
- 所有环境变量都已转换

**一致性验证**：

- 镜像配置一致性
- 端口映射一致性
- 环境变量一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 网络配置一致
- 存储配置一致

### 5.2 验证实现

**转换验证器**：

```python
class DockerConversionValidator:
    """Docker转换验证器"""

    def validate(self, source_config: Dict, target_resources: List[Dict]) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(source_config, target_resources),
            'consistency': self._validate_consistency(source_config, target_resources),
            'equivalence': self._validate_equivalence(source_config, target_resources)
        }
        return results
```

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

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理Docker配置**：
   - 移除未使用的服务
   - 标准化命名
   - 验证配置正确性

2. **备份数据**：
   - 备份Docker配置
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心服务
   - 再转换依赖服务
   - 最后转换网络和存储

2. **验证转换结果**：
   - 检查资源完整性
   - 验证配置映射
   - 测试功能等价性

### 7.3 转换后优化

1. **优化配置**：
   - 调整资源限制
   - 优化网络配置
   - 添加健康检查

2. **测试和验证**：
   - 在测试环境验证
   - 逐步迁移生产环境
   - 监控资源状态

## 8. 转换工具和资源

### 8.1 转换工具

- **kompose**：Docker Compose到Kubernetes转换工具
- **docker2k8s**：Docker到Kubernetes转换工具

### 8.2 参考资源

- [Docker文档](https://docs.docker.com/)
- [Kubernetes文档](https://kubernetes.io/docs/)
- [Kompose文档](https://kompose.io/)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
