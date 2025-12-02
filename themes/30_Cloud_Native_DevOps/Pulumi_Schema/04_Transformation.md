# Pulumi Schema转换体系

## 📑 目录

- [Pulumi Schema转换体系](#pulumi-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Pulumi到Terraform转换](#2-pulumi到terraform转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Terraform到Pulumi转换](#3-terraform到pulumi转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. Pulumi到Kubernetes转换](#4-pulumi到kubernetes转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. Pulumi数据存储与分析](#6-pulumi数据存储与分析)
    - [6.1 PostgreSQL Pulumi数据存储](#61-postgresql-pulumi数据存储)
    - [6.2 Pulumi数据分析查询](#62-pulumi数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

---

## 1. 转换体系概述

Pulumi Schema转换体系支持Pulumi程序与其他IaC格式之间的转换。

### 1.1 转换目标

1. **Pulumi到Terraform转换**：Pulumi程序转换为Terraform配置
2. **Terraform到Pulumi转换**：Terraform配置转换为Pulumi程序
3. **Pulumi到Kubernetes转换**：Pulumi程序转换为Kubernetes资源
4. **Schema到数据库转换**：Pulumi Schema定义到PostgreSQL存储

---

## 2. Pulumi到Terraform转换

### 2.1 转换规则

**资源映射规则**：

- Pulumi资源 → Terraform资源
- Pulumi配置 → Terraform变量
- Pulumi输出 → Terraform输出
- Pulumi堆栈配置 → Terraform变量文件

### 2.2 完整转换实现

**Pulumi到Terraform转换器**：

```python
#!/usr/bin/env python3
"""
Pulumi到Terraform转换器
"""

import ast
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class PulumiToTerraformConverter:
    """Pulumi到Terraform转换器"""

    def __init__(self):
        self.terraform_resources = []
        self.terraform_variables = []
        self.terraform_outputs = []

    def convert(self, pulumi_program_path: str, language: str = "python") -> str:
        """转换Pulumi程序为Terraform配置"""
        if language == "python":
            return self._convert_python(pulumi_program_path)
        elif language == "typescript":
            return self._convert_typescript(pulumi_program_path)
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _convert_python(self, program_path: str) -> str:
        """转换Python Pulumi程序"""
        with open(program_path, 'r') as f:
            code = f.read()

        # 解析Python代码
        tree = ast.parse(code)

        # 提取资源定义
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                resource = self._extract_resource(node)
                if resource:
                    self.terraform_resources.append(resource)

            elif isinstance(node, ast.Assign):
                # 提取配置变量
                var = self._extract_variable(node)
                if var:
                    self.terraform_variables.append(var)

                # 提取输出
                output = self._extract_output(node)
                if output:
                    self.terraform_outputs.append(output)

        # 生成Terraform配置
        return self._generate_terraform_config()

    def _extract_resource(self, node: ast.Call) -> Optional[Dict]:
        """提取Pulumi资源定义"""
        if not isinstance(node.func, ast.Attribute):
            return None

        # 检查是否是Pulumi资源创建
        if not node.func.attr in ['Resource', 'ComponentResource']:
            return None

        # 提取资源类型和名称
        resource_type = self._get_resource_type(node)
        resource_name = self._get_resource_name(node)
        resource_props = self._get_resource_properties(node)

        if resource_type and resource_name:
            return {
                'type': self._map_pulumi_to_terraform_type(resource_type),
                'name': resource_name,
                'properties': resource_props
            }

        return None

    def _get_resource_type(self, node: ast.Call) -> Optional[str]:
        """获取资源类型"""
        if node.args and isinstance(node.args[0], ast.Str):
            return node.args[0].s
        return None

    def _get_resource_name(self, node: ast.Call) -> Optional[str]:
        """获取资源名称"""
        if len(node.args) > 1 and isinstance(node.args[1], ast.Str):
            return node.args[1].s
        return None

    def _get_resource_properties(self, node: ast.Call) -> Dict:
        """获取资源属性"""
        props = {}
        for keyword in node.keywords:
            if isinstance(keyword.value, (ast.Str, ast.Num)):
                props[keyword.arg] = ast.literal_eval(keyword.value)
        return props

    def _map_pulumi_to_terraform_type(self, pulumi_type: str) -> str:
        """映射Pulumi资源类型到Terraform资源类型"""
        mapping = {
            'aws:ec2/instance:Instance': 'aws_instance',
            'aws:s3/bucket:Bucket': 'aws_s3_bucket',
            'aws:ec2/vpc:Vpc': 'aws_vpc',
            'kubernetes:apps/v1:Deployment': 'kubernetes_deployment',
            'kubernetes:core/v1:Service': 'kubernetes_service',
        }
        return mapping.get(pulumi_type, pulumi_type.replace(':', '_').lower())

    def _extract_variable(self, node: ast.Assign) -> Optional[Dict]:
        """提取变量定义"""
        # 简化实现
        return None

    def _extract_output(self, node: ast.Assign) -> Optional[Dict]:
        """提取输出定义"""
        # 检查是否是pulumi.export
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr == 'export':
                    return {
                        'name': node.targets[0].id if isinstance(node.targets[0], ast.Name) else None,
                        'value': self._extract_value(node.value)
                    }
        return None

    def _extract_value(self, node: ast.Call) -> str:
        """提取值"""
        if node.args:
            return str(ast.literal_eval(node.args[0]))
        return ""

    def _convert_typescript(self, program_path: str) -> str:
        """转换TypeScript Pulumi程序"""
        # TypeScript转换实现
        # 可以使用TypeScript解析器
        pass

    def _generate_terraform_config(self) -> str:
        """生成Terraform配置"""
        config = []

        # 变量
        if self.terraform_variables:
            config.append("variable \"variables\" {")
            config.append("  type = map(string)")
            config.append("  default = {}")
            config.append("}")
            config.append("")

        # 资源
        for resource in self.terraform_resources:
            config.append(f"resource \"{resource['type']}\" \"{resource['name']}\" {{")
            for key, value in resource['properties'].items():
                if isinstance(value, str):
                    config.append(f"  {key} = \"{value}\"")
                else:
                    config.append(f"  {key} = {value}")
            config.append("}")
            config.append("")

        # 输出
        for output in self.terraform_outputs:
            if output['name']:
                config.append(f"output \"{output['name']}\" {{")
                config.append(f"  value = {output['value']}")
                config.append("}")
                config.append("")

        return "\n".join(config)

# 使用示例
if __name__ == '__main__':
    converter = PulumiToTerraformConverter()

    # 示例Pulumi Python程序
    pulumi_code = """
import pulumi
import pulumi_aws as aws

# 创建VPC
vpc = aws.ec2.Vpc("main-vpc",
    cidr_block="10.0.0.0/16",
    tags={"Name": "main-vpc"}
)

# 创建子网
subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    tags={"Name": "public-subnet"}
)

# 输出
pulumi.export("vpc_id", vpc.id)
"""

    # 写入临时文件
    with open('/tmp/__main__.py', 'w') as f:
        f.write(pulumi_code)

    # 转换
    terraform_config = converter.convert('/tmp/__main__.py', 'python')
    print(terraform_config)
```

---

## 3. Terraform到Pulumi转换

### 3.1 转换规则

**资源映射规则**：

- Terraform资源 → Pulumi资源
- Terraform变量 → Pulumi配置
- Terraform输出 → Pulumi输出

### 3.2 转换实现

**Terraform到Pulumi转换器**：

```python
class TerraformToPulumiConverter:
    """Terraform到Pulumi转换器"""

    def convert(self, terraform_file: str, language: str = "python") -> str:
        """转换Terraform配置为Pulumi程序"""
        import hcl2

        with open(terraform_file, 'r') as f:
            tf_config = hcl2.load(f)

        if language == "python":
            return self._generate_python_code(tf_config)
        elif language == "typescript":
            return self._generate_typescript_code(tf_config)
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _generate_python_code(self, tf_config: Dict) -> str:
        """生成Python Pulumi代码"""
        lines = ["import pulumi", "import pulumi_aws as aws", ""]

        # 转换资源
        resources = tf_config.get('resource', {})
        for resource_type, resource_instances in resources.items():
            for instance_name, instance_config in resource_instances.items():
                pulumi_type = self._map_terraform_to_pulumi_type(resource_type)
                lines.append(f"{instance_name} = {pulumi_type}(\"{instance_name}\",")
                for key, value in instance_config.items():
                    if isinstance(value, str):
                        lines.append(f"    {key}=\"{value}\",")
                    else:
                        lines.append(f"    {key}={value},")
                lines.append(")")
                lines.append("")

        # 转换输出
        outputs = tf_config.get('output', {})
        for output_name, output_config in outputs.items():
            value = output_config.get('value', '')
            lines.append(f"pulumi.export(\"{output_name}\", {value})")

        return "\n".join(lines)

    def _map_terraform_to_pulumi_type(self, tf_type: str) -> str:
        """映射Terraform资源类型到Pulumi类型"""
        mapping = {
            'aws_instance': 'aws.ec2.Instance',
            'aws_s3_bucket': 'aws.s3.Bucket',
            'aws_vpc': 'aws.ec2.Vpc',
        }
        return mapping.get(tf_type, tf_type)
```

---

## 4. Pulumi到Kubernetes转换

### 4.1 转换规则

**资源映射规则**：

- Pulumi Kubernetes资源 → Kubernetes YAML
- Pulumi程序 → Kubernetes资源清单

### 4.2 转换实现

**Pulumi到Kubernetes转换器**：

```python
class PulumiToKubernetesConverter:
    """Pulumi到Kubernetes转换器"""

    def convert(self, pulumi_program_path: str) -> List[Dict]:
        """转换Pulumi程序为Kubernetes资源"""
        import yaml

        # 运行pulumi preview获取资源定义
        # 或者解析Pulumi程序提取Kubernetes资源

        k8s_resources = []

        # 解析Pulumi程序
        resources = self._parse_pulumi_program(pulumi_program_path)

        # 过滤Kubernetes资源
        for resource in resources:
            if resource['type'].startswith('kubernetes:'):
                k8s_resource = self._convert_to_k8s_resource(resource)
                k8s_resources.append(k8s_resource)

        return k8s_resources

    def _parse_pulumi_program(self, program_path: str) -> List[Dict]:
        """解析Pulumi程序"""
        # 实现解析逻辑
        return []

    def _convert_to_k8s_resource(self, pulumi_resource: Dict) -> Dict:
        """转换Pulumi资源为Kubernetes资源"""
        # 提取Kubernetes资源定义
        props = pulumi_resource.get('properties', {})

        # 构建Kubernetes资源
        k8s_resource = {
            'apiVersion': props.get('apiVersion'),
            'kind': props.get('kind'),
            'metadata': props.get('metadata', {}),
            'spec': props.get('spec', {})
        }

        return k8s_resource
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有Pulumi资源都已转换
- 所有配置都已映射
- 所有输出都已转换

**一致性验证**：

- 资源类型一致性
- 资源配置一致性
- 依赖关系一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 资源行为一致
- 配置值一致

### 5.2 验证实现

**转换验证器**：

```python
class PulumiConversionValidator:
    """Pulumi转换验证器"""

    def validate(self, source_program: str, target_config: str) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(source_program, target_config),
            'consistency': self._validate_consistency(source_program, target_config),
            'equivalence': self._validate_equivalence(source_program, target_config)
        }
        return results
```

---

## 6. Pulumi数据存储与分析

### 6.1 PostgreSQL Pulumi数据存储

**Pulumi数据存储方案**：

```python
import psycopg2
import json

class PulumiDataStore:
    """Pulumi数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Pulumi数据存储表"""
        with self.conn.cursor() as cur:
            # 程序定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pulumi_programs (
                    id SERIAL PRIMARY KEY,
                    program_name VARCHAR(255) NOT NULL UNIQUE,
                    program_language VARCHAR(50) NOT NULL,
                    program_content TEXT NOT NULL,
                    pulumi_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 资源定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pulumi_resources (
                    id SERIAL PRIMARY KEY,
                    program_id INTEGER REFERENCES pulumi_programs(id),
                    resource_type VARCHAR(255) NOT NULL,
                    resource_name VARCHAR(255) NOT NULL,
                    resource_config JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(program_id, resource_type, resource_name)
                )
            """)

            # 堆栈表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pulumi_stacks (
                    id SERIAL PRIMARY KEY,
                    program_id INTEGER REFERENCES pulumi_programs(id),
                    stack_name VARCHAR(255) NOT NULL,
                    stack_state JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(program_id, stack_name)
                )
            """)

            self.conn.commit()
```

### 6.2 Pulumi数据分析查询

**分析查询示例**：

```python
def analyze_pulumi_usage(db_config: Dict):
    """分析Pulumi使用情况"""
    store = PulumiDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询资源类型统计
        cur.execute("""
            SELECT
                resource_type,
                COUNT(*) as resource_count
            FROM pulumi_resources
            GROUP BY resource_type
            ORDER BY resource_count DESC
        """)

        return cur.fetchall()
```

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理Pulumi程序**：
   - 移除未使用的资源
   - 标准化命名
   - 验证程序正确性

2. **备份数据**：
   - 备份Pulumi程序
   - 备份堆栈状态
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心资源
   - 再转换依赖资源
   - 最后转换配置和输出

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

- **pulumi convert**：Pulumi官方转换工具
- **tf2pulumi**：Terraform到Pulumi转换工具

### 8.2 参考资源

- [Pulumi文档](https://www.pulumi.com/docs/)
- [Terraform文档](https://www.terraform.io/docs/)
- [Pulumi转换指南](https://www.pulumi.com/docs/guides/adopting/)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
