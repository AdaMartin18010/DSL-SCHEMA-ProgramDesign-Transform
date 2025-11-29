# Ansible Schema转换体系

## 📑 目录

- [Ansible Schema转换体系](#ansible-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Ansible到Terraform转换](#2-ansible到terraform转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Ansible到Kubernetes转换](#3-ansible到kubernetes转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. Ansible到Docker转换](#4-ansible到docker转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. Ansible数据存储与分析](#6-ansible数据存储与分析)
    - [6.1 PostgreSQL Ansible数据存储](#61-postgresql-ansible数据存储)
    - [6.2 Ansible数据分析查询](#62-ansible数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

---

## 1. 转换体系概述

Ansible Schema转换体系支持Ansible Playbook与其他配置格式之间的转换。

### 1.1 转换目标

1. **Ansible到Terraform转换**：Ansible Playbook转换为Terraform配置
2. **Ansible到Kubernetes转换**：Ansible Playbook转换为Kubernetes资源
3. **Ansible到Docker转换**：Ansible Playbook转换为Docker配置
4. **Schema到数据库转换**：Ansible Schema定义到PostgreSQL存储

---

## 2. Ansible到Terraform转换

### 2.1 转换规则

**资源映射规则**：

- Ansible任务 → Terraform资源
- Ansible变量 → Terraform变量
- Ansible角色 → Terraform模块
- Ansible Playbook → Terraform配置

### 2.2 完整转换实现

**Ansible到Terraform转换器**：

```python
#!/usr/bin/env python3
"""
Ansible到Terraform转换器
"""

import yaml
from typing import Dict, List, Any, Optional

class AnsibleToTerraformConverter:
    """Ansible到Terraform转换器"""

    def __init__(self):
        self.terraform_resources = []
        self.terraform_variables = []
        self.module_mapping = {}

    def convert(self, playbook_file: str) -> str:
        """转换Ansible Playbook为Terraform配置"""
        with open(playbook_file, 'r') as f:
            playbook = yaml.safe_load(f)

        # 处理多个play
        if isinstance(playbook, list):
            for play in playbook:
                self._convert_play(play)
        else:
            self._convert_play(playbook)

        # 生成Terraform配置
        return self._generate_terraform_config()

    def _convert_play(self, play: Dict):
        """转换单个play"""
        # 转换变量
        vars_dict = play.get('vars', {})
        for var_name, var_value in vars_dict.items():
            self.terraform_variables.append({
                'name': var_name,
                'type': self._infer_type(var_value),
                'default': var_value
            })

        # 转换任务
        tasks = play.get('tasks', [])
        for task in tasks:
            terraform_resource = self._convert_task(task)
            if terraform_resource:
                self.terraform_resources.append(terraform_resource)

        # 转换角色
        roles = play.get('roles', [])
        for role in roles:
            if isinstance(role, dict):
                role_name = role.get('role', '')
            else:
                role_name = role
            self._convert_role(role_name)

    def _convert_task(self, task: Dict) -> Optional[Dict]:
        """转换Ansible任务为Terraform资源"""
        # 获取任务模块
        module = None
        module_args = {}

        for key, value in task.items():
            if key not in ['name', 'when', 'loop', 'register']:
                module = key
                if isinstance(value, dict):
                    module_args = value
                else:
                    module_args = {'value': value}
                break

        if not module:
            return None

        # 映射模块到Terraform资源
        terraform_resource = self._map_module_to_terraform(module, module_args)
        return terraform_resource

    def _map_module_to_terraform(self, module: str, module_args: Dict) -> Optional[Dict]:
        """映射Ansible模块到Terraform资源"""
        mapping = {
            'ec2_instance': self._convert_ec2_instance,
            's3_bucket': self._convert_s3_bucket,
            'rds_instance': self._convert_rds_instance,
            'iam_role': self._convert_iam_role,
        }

        # 尝试直接映射
        if module in mapping:
            return mapping[module](module_args)

        # 通用映射
        return self._convert_generic_module(module, module_args)

    def _convert_ec2_instance(self, args: Dict) -> Dict:
        """转换EC2实例任务"""
        return {
            'type': 'aws_instance',
            'name': args.get('name', 'instance').lower().replace('-', '_'),
            'properties': {
                'ami': args.get('image_id', ''),
                'instance_type': args.get('instance_type', 't2.micro'),
                'tags': args.get('tags', {})
            }
        }

    def _convert_s3_bucket(self, args: Dict) -> Dict:
        """转换S3存储桶任务"""
        return {
            'type': 'aws_s3_bucket',
            'name': args.get('name', 'bucket').lower().replace('-', '_'),
            'properties': {
                'bucket': args.get('name', ''),
                'tags': args.get('tags', {})
            }
        }

    def _convert_rds_instance(self, args: Dict) -> Dict:
        """转换RDS实例任务"""
        return {
            'type': 'aws_db_instance',
            'name': args.get('name', 'db').lower().replace('-', '_'),
            'properties': {
                'identifier': args.get('db_instance_identifier', ''),
                'engine': args.get('engine', 'mysql'),
                'instance_class': args.get('db_instance_class', 'db.t2.micro'),
                'allocated_storage': args.get('allocated_storage', 20),
                'username': args.get('master_username', 'admin'),
                'password': args.get('master_user_password', '')
            }
        }

    def _convert_iam_role(self, args: Dict) -> Dict:
        """转换IAM角色任务"""
        return {
            'type': 'aws_iam_role',
            'name': args.get('name', 'role').lower().replace('-', '_'),
            'properties': {
                'name': args.get('name', ''),
                'assume_role_policy': args.get('assume_role_policy_document', '')
            }
        }

    def _convert_generic_module(self, module: str, args: Dict) -> Optional[Dict]:
        """通用模块转换"""
        # 对于无法直接映射的模块，返回None或创建通用资源
        return None

    def _convert_role(self, role_name: str):
        """转换Ansible角色为Terraform模块"""
        # 角色可以转换为Terraform模块
        self.module_mapping[role_name] = f'module.{role_name}'

    def _infer_type(self, value: Any) -> str:
        """推断变量类型"""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'number'
        elif isinstance(value, list):
            return 'list(string)'
        elif isinstance(value, dict):
            return 'map(string)'
        else:
            return 'string'

    def _generate_terraform_config(self) -> str:
        """生成Terraform配置"""
        config = []

        # 变量
        for var in self.terraform_variables:
            config.append(f'variable "{var["name"]}" {{')
            config.append(f'  type = {var["type"]}')
            if var.get('default') is not None:
                default = var['default']
                if isinstance(default, str):
                    config.append(f'  default = "{default}"')
                else:
                    config.append(f'  default = {default}')
            config.append('}')
            config.append('')

        # 资源
        for resource in self.terraform_resources:
            config.append(f'resource "{resource["type"]}" "{resource["name"]}" {{')
            for key, value in resource['properties'].items():
                if isinstance(value, str):
                    config.append(f'  {key} = "{value}"')
                elif isinstance(value, dict):
                    config.append(f'  {key} = {{')
                    for k, v in value.items():
                        config.append(f'    {k} = "{v}"')
                    config.append('  }')
                else:
                    config.append(f'  {key} = {value}')
            config.append('}')
            config.append('')

        return '\n'.join(config)

# 使用示例
if __name__ == '__main__':
    converter = AnsibleToTerraformConverter()

    # 示例Ansible Playbook
    playbook = {
        'hosts': 'localhost',
        'vars': {
            'instance_type': 't2.micro',
            'ami_id': 'ami-12345678'
        },
        'tasks': [
            {
                'name': 'Create EC2 instance',
                'ec2_instance': {
                    'name': 'my-instance',
                    'image_id': '{{ ami_id }}',
                    'instance_type': '{{ instance_type }}',
                    'tags': {
                        'Name': 'MyInstance'
                    }
                }
            },
            {
                'name': 'Create S3 bucket',
                's3_bucket': {
                    'name': 'my-bucket',
                    'tags': {
                        'Environment': 'Production'
                    }
                }
            }
        ]
    }

    # 写入临时文件
    with open('/tmp/playbook.yaml', 'w') as f:
        yaml.dump(playbook, f)

    # 转换
    terraform_config = converter.convert('/tmp/playbook.yaml')
    print(terraform_config)
```

---

## 3. Ansible到Kubernetes转换

### 3.1 转换规则

**资源映射规则**：

- Ansible Kubernetes任务 → Kubernetes资源
- Ansible配置 → Kubernetes ConfigMap/Secret
- Ansible部署任务 → Kubernetes Deployment

### 3.2 转换实现

**Ansible到Kubernetes转换器**：

```python
class AnsibleToKubernetesConverter:
    """Ansible到Kubernetes转换器"""

    def convert(self, playbook_file: str) -> List[Dict]:
        """转换Ansible Playbook为Kubernetes资源"""
        import yaml

        with open(playbook_file, 'r') as f:
            playbook = yaml.safe_load(f)

        k8s_resources = []

        # 处理play
        plays = playbook if isinstance(playbook, list) else [playbook]
        for play in plays:
            tasks = play.get('tasks', [])
            for task in tasks:
                k8s_resource = self._convert_task_to_k8s(task)
                if k8s_resource:
                    k8s_resources.append(k8s_resource)

        return k8s_resources

    def _convert_task_to_k8s(self, task: Dict) -> Optional[Dict]:
        """转换任务为Kubernetes资源"""
        # 检查是否是Kubernetes相关任务
        if 'k8s' in task or 'kubernetes' in task:
            module = 'k8s' if 'k8s' in task else 'kubernetes'
            module_args = task.get(module, {})
            return self._convert_k8s_task(module_args)

        # 检查是否是部署任务
        elif 'deploy' in task or 'docker_container' in task:
            return self._convert_deploy_task(task)

        return None

    def _convert_k8s_task(self, module_args: Dict) -> Dict:
        """转换Kubernetes任务"""
        kind = module_args.get('kind', 'Deployment')
        name = module_args.get('name', 'app')
        definition = module_args.get('definition', {})

        return {
            'apiVersion': definition.get('apiVersion', 'apps/v1'),
            'kind': kind,
            'metadata': definition.get('metadata', {'name': name}),
            'spec': definition.get('spec', {})
        }

    def _convert_deploy_task(self, task: Dict) -> Dict:
        """转换部署任务为Kubernetes Deployment"""
        # 从Docker容器任务提取信息
        container_task = task.get('docker_container', {})

        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': container_task.get('name', 'app')
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {
                        'app': container_task.get('name', 'app')
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': container_task.get('name', 'app')
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': container_task.get('name', 'app'),
                            'image': container_task.get('image', ''),
                            'ports': [{'containerPort': p} for p in container_task.get('ports', [])]
                        }]
                    }
                }
            }
        }

        return deployment
```

---

## 4. Ansible到Docker转换

### 4.1 转换规则

**资源映射规则**：

- Ansible Docker任务 → Dockerfile指令
- Ansible配置 → Docker Compose配置
- Ansible安装任务 → Dockerfile RUN指令

### 4.2 转换实现

**Ansible到Docker转换器**：

```python
class AnsibleToDockerConverter:
    """Ansible到Docker转换器"""

    def convert(self, playbook_file: str) -> str:
        """转换Ansible Playbook为Dockerfile"""
        import yaml

        with open(playbook_file, 'r') as f:
            playbook = yaml.safe_load(f)

        dockerfile_lines = []

        # 处理play
        plays = playbook if isinstance(playbook, list) else [playbook]
        for play in plays:
            # 基础镜像
            base_image = play.get('vars', {}).get('base_image', 'ubuntu:latest')
            dockerfile_lines.append(f'FROM {base_image}')
            dockerfile_lines.append('')

            # 转换任务
            tasks = play.get('tasks', [])
            for task in tasks:
                dockerfile_instruction = self._convert_task_to_dockerfile(task)
                if dockerfile_instruction:
                    dockerfile_lines.append(dockerfile_instruction)

        return '\n'.join(dockerfile_lines)

    def _convert_task_to_dockerfile(self, task: Dict) -> Optional[str]:
        """转换任务为Dockerfile指令"""
        # 安装包
        if 'apt' in task:
            packages = task['apt'].get('name', [])
            if isinstance(packages, str):
                packages = [packages]
            return f"RUN apt-get update && apt-get install -y {' '.join(packages)}"

        elif 'yum' in task:
            packages = task['yum'].get('name', [])
            if isinstance(packages, str):
                packages = [packages]
            return f"RUN yum install -y {' '.join(packages)}"

        # 复制文件
        elif 'copy' in task:
            copy_args = task['copy']
            src = copy_args.get('src', '')
            dest = copy_args.get('dest', '')
            return f"COPY {src} {dest}"

        # 设置环境变量
        elif 'set_fact' in task or 'lineinfile' in task:
            # 处理环境变量设置
            return None

        # 运行命令
        elif 'command' in task:
            cmd = task['command']
            if isinstance(cmd, str):
                return f"RUN {cmd}"
            elif isinstance(cmd, dict):
                return f"RUN {cmd.get('cmd', '')}"

        return None
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有Ansible任务都已转换
- 所有变量都已映射
- 所有角色都已处理

**一致性验证**：

- 任务模块一致性
- 变量值一致性
- 依赖关系一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 资源行为一致
- 配置值一致

### 5.2 验证实现

**转换验证器**：

```python
class AnsibleConversionValidator:
    """Ansible转换验证器"""

    def validate(self, playbook_file: str, target_config: str) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(playbook_file, target_config),
            'consistency': self._validate_consistency(playbook_file, target_config),
            'equivalence': self._validate_equivalence(playbook_file, target_config)
        }
        return results
```

---

## 6. Ansible数据存储与分析

### 6.1 PostgreSQL Ansible数据存储

**Ansible数据存储方案**：

```python
import psycopg2
import json

class AnsibleDataStore:
    """Ansible数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Ansible数据存储表"""
        with self.conn.cursor() as cur:
            # Playbook定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ansible_playbooks (
                    id SERIAL PRIMARY KEY,
                    playbook_name VARCHAR(255) NOT NULL UNIQUE,
                    playbook_content TEXT NOT NULL,
                    ansible_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 任务定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ansible_tasks (
                    id SERIAL PRIMARY KEY,
                    playbook_id INTEGER REFERENCES ansible_playbooks(id),
                    task_name VARCHAR(255) NOT NULL,
                    module VARCHAR(255) NOT NULL,
                    module_args JSONB,
                    task_order INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 角色定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ansible_roles (
                    id SERIAL PRIMARY KEY,
                    role_name VARCHAR(255) NOT NULL UNIQUE,
                    role_content JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
```

### 6.2 Ansible数据分析查询

**分析查询示例**：

```python
def analyze_ansible_usage(db_config: Dict):
    """分析Ansible使用情况"""
    store = AnsibleDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询模块使用统计
        cur.execute("""
            SELECT
                module,
                COUNT(*) as usage_count
            FROM ansible_tasks
            GROUP BY module
            ORDER BY usage_count DESC
        """)

        return cur.fetchall()
```

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理Ansible Playbook**：
   - 移除未使用的任务
   - 标准化命名
   - 验证Playbook正确性

2. **备份数据**：
   - 备份Ansible Playbook
   - 备份角色和变量
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心任务
   - 再转换依赖任务
   - 最后转换角色和变量

2. **验证转换结果**：
   - 检查任务完整性
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

- **ansible2terraform**：Ansible到Terraform转换工具
- **ansible2kubernetes**：Ansible到Kubernetes转换工具

### 8.2 参考资源

- [Ansible文档](https://docs.ansible.com/)
- [Terraform文档](https://www.terraform.io/docs/)
- [Kubernetes文档](https://kubernetes.io/docs/)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
