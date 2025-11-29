# CloudFormation Schema转换体系

## 📑 目录

- [CloudFormation Schema转换体系](#cloudformation-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. CloudFormation到Terraform转换](#2-cloudformation到terraform转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Terraform到CloudFormation转换](#3-terraform到cloudformation转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. CloudFormation到Kubernetes转换](#4-cloudformation到kubernetes转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. CloudFormation数据存储与分析](#6-cloudformation数据存储与分析)
    - [6.1 PostgreSQL CloudFormation数据存储](#61-postgresql-cloudformation数据存储)
    - [6.2 CloudFormation数据分析查询](#62-cloudformation数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

---

## 1. 转换体系概述

CloudFormation Schema转换体系支持CloudFormation模板与其他IaC格式之间的转换。

### 1.1 转换目标

1. **CloudFormation到Terraform转换**：CloudFormation模板转换为Terraform配置
2. **Terraform到CloudFormation转换**：Terraform配置转换为CloudFormation模板
3. **CloudFormation到Kubernetes转换**：CloudFormation模板转换为Kubernetes资源
4. **Schema到数据库转换**：CloudFormation Schema定义到PostgreSQL存储

---

## 2. CloudFormation到Terraform转换

### 2.1 转换规则

**资源映射规则**：

- CloudFormation资源 → Terraform资源
- CloudFormation参数 → Terraform变量
- CloudFormation输出 → Terraform输出
- CloudFormation条件 → Terraform条件表达式

### 2.2 完整转换实现

**CloudFormation到Terraform转换器**：

```python
#!/usr/bin/env python3
"""
CloudFormation到Terraform转换器
"""

import yaml
import json
from typing import Dict, List, Any, Optional

class CloudFormationToTerraformConverter:
    """CloudFormation到Terraform转换器"""

    def __init__(self):
        self.terraform_variables = []
        self.terraform_resources = []
        self.terraform_outputs = []
        self.resource_mapping = {}

    def convert(self, cfn_template_path: str) -> str:
        """转换CloudFormation模板为Terraform配置"""
        # 读取CloudFormation模板
        with open(cfn_template_path, 'r') as f:
            if cfn_template_path.endswith('.yaml') or cfn_template_path.endswith('.yml'):
                cfn_template = yaml.safe_load(f)
            else:
                cfn_template = json.load(f)

        # 转换参数
        parameters = cfn_template.get('Parameters', {})
        for param_name, param_config in parameters.items():
            self.terraform_variables.append(
                self._convert_parameter(param_name, param_config)
            )

        # 转换资源
        resources = cfn_template.get('Resources', {})
        for resource_name, resource_config in resources.items():
            terraform_resource = self._convert_resource(resource_name, resource_config)
            if terraform_resource:
                self.terraform_resources.append(terraform_resource)

        # 转换输出
        outputs = cfn_template.get('Outputs', {})
        for output_name, output_config in outputs.items():
            self.terraform_outputs.append(
                self._convert_output(output_name, output_config)
            )

        # 生成Terraform配置
        return self._generate_terraform_config()

    def _convert_parameter(self, param_name: str, param_config: Dict) -> Dict:
        """转换CloudFormation参数为Terraform变量"""
        var_type = self._map_cfn_type_to_tf_type(param_config.get('Type', 'String'))

        variable = {
            'name': param_name,
            'type': var_type,
            'description': param_config.get('Description', ''),
            'default': param_config.get('Default')
        }

        return variable

    def _map_cfn_type_to_tf_type(self, cfn_type: str) -> str:
        """映射CloudFormation类型到Terraform类型"""
        mapping = {
            'String': 'string',
            'Number': 'number',
            'List<Number>': 'list(number)',
            'CommaDelimitedList': 'list(string)',
            'AWS::EC2::KeyPair::KeyName': 'string',
        }
        return mapping.get(cfn_type, 'string')

    def _convert_resource(self, resource_name: str, resource_config: Dict) -> Optional[Dict]:
        """转换CloudFormation资源为Terraform资源"""
        resource_type = resource_config.get('Type', '')
        properties = resource_config.get('Properties', {})

        # 映射资源类型
        tf_resource_type = self._map_cfn_resource_to_tf_resource(resource_type)
        if not tf_resource_type:
            return None

        # 转换属性
        tf_properties = self._convert_properties(properties, resource_type)

        # 处理依赖
        depends_on = resource_config.get('DependsOn', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]

        return {
            'type': tf_resource_type,
            'name': resource_name.lower().replace('-', '_'),
            'properties': tf_properties,
            'depends_on': depends_on
        }

    def _map_cfn_resource_to_tf_resource(self, cfn_type: str) -> Optional[str]:
        """映射CloudFormation资源类型到Terraform资源类型"""
        mapping = {
            'AWS::EC2::Instance': 'aws_instance',
            'AWS::EC2::VPC': 'aws_vpc',
            'AWS::EC2::Subnet': 'aws_subnet',
            'AWS::S3::Bucket': 'aws_s3_bucket',
            'AWS::IAM::Role': 'aws_iam_role',
            'AWS::Lambda::Function': 'aws_lambda_function',
            'AWS::RDS::DBInstance': 'aws_db_instance',
            'AWS::ElasticLoadBalancingV2::LoadBalancer': 'aws_lb',
        }
        return mapping.get(cfn_type)

    def _convert_properties(self, properties: Dict, resource_type: str) -> Dict:
        """转换资源属性"""
        converted = {}

        for key, value in properties.items():
            # 处理CloudFormation函数
            if isinstance(value, dict):
                value = self._convert_cfn_function(value)

            # 转换属性名
            tf_key = self._convert_property_name(key, resource_type)
            converted[tf_key] = value

        return converted

    def _convert_cfn_function(self, value: Dict) -> str:
        """转换CloudFormation函数"""
        if 'Ref' in value:
            # 引用其他资源或参数
            ref_value = value['Ref']
            if ref_value in self.resource_mapping:
                return f"${{{self.resource_mapping[ref_value]}.id}}"
            else:
                return f"${{var.{ref_value}}}"

        elif 'Fn::GetAtt' in value:
            # 获取属性
            get_att = value['Fn::GetAtt']
            resource_name = get_att[0]
            attribute = get_att[1]
            if resource_name in self.resource_mapping:
                return f"${{{self.resource_mapping[resource_name]}.{attribute}}}"

        elif 'Fn::Join' in value:
            # 连接字符串
            join = value['Fn::Join']
            delimiter = join[0]
            values = join[1]
            joined = f'"{delimiter}".join([{", ".join(str(v) for v in values)}])'
            return joined

        return str(value)

    def _convert_property_name(self, cfn_name: str, resource_type: str) -> str:
        """转换属性名"""
        # CloudFormation使用PascalCase，Terraform使用snake_case
        # 简化实现
        mapping = {
            'VpcId': 'vpc_id',
            'CidrBlock': 'cidr_block',
            'InstanceType': 'instance_type',
            'ImageId': 'ami',
        }
        return mapping.get(cfn_name, cfn_name.lower())

    def _convert_output(self, output_name: str, output_config: Dict) -> Dict:
        """转换CloudFormation输出为Terraform输出"""
        value = output_config.get('Value', '')

        # 处理引用
        if isinstance(value, dict):
            value = self._convert_cfn_function(value)

        return {
            'name': output_name.lower().replace('-', '_'),
            'value': value,
            'description': output_config.get('Description', '')
        }

    def _generate_terraform_config(self) -> str:
        """生成Terraform配置"""
        config = []

        # 变量
        for var in self.terraform_variables:
            config.append(f'variable "{var["name"]}" {{')
            config.append(f'  type = {var["type"]}')
            if var.get('description'):
                config.append(f'  description = "{var["description"]}"')
            if var.get('default') is not None:
                config.append(f'  default = {json.dumps(var["default"])}')
            config.append('}')
            config.append('')

        # 资源
        for resource in self.terraform_resources:
            config.append(f'resource "{resource["type"]}" "{resource["name"]}" {{')
            for key, value in resource['properties'].items():
                if isinstance(value, str) and not value.startswith('${'):
                    config.append(f'  {key} = "{value}"')
                else:
                    config.append(f'  {key} = {value}')
            if resource.get('depends_on'):
                config.append('  depends_on = [')
                for dep in resource['depends_on']:
                    config.append(f'    {dep.lower().replace("-", "_")},')
                config.append('  ]')
            config.append('}')
            config.append('')

        # 输出
        for output in self.terraform_outputs:
            config.append(f'output "{output["name"]}" {{')
            config.append(f'  value = {output["value"]}')
            if output.get('description'):
                config.append(f'  description = "{output["description"]}"')
            config.append('}')
            config.append('')

        return '\n'.join(config)

# 使用示例
if __name__ == '__main__':
    converter = CloudFormationToTerraformConverter()

    # 示例CloudFormation模板
    cfn_template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Parameters': {
            'InstanceType': {
                'Type': 'String',
                'Default': 't2.micro'
            }
        },
        'Resources': {
            'MyVPC': {
                'Type': 'AWS::EC2::VPC',
                'Properties': {
                    'CidrBlock': '10.0.0.0/16'
                }
            },
            'MyInstance': {
                'Type': 'AWS::EC2::Instance',
                'Properties': {
                    'InstanceType': {'Ref': 'InstanceType'},
                    'ImageId': 'ami-12345678'
                }
            }
        },
        'Outputs': {
            'VpcId': {
                'Value': {'Ref': 'MyVPC'}
            }
        }
    }

    # 写入临时文件
    with open('/tmp/template.yaml', 'w') as f:
        yaml.dump(cfn_template, f)

    # 转换
    terraform_config = converter.convert('/tmp/template.yaml')
    print(terraform_config)
```

---

## 3. Terraform到CloudFormation转换

### 3.1 转换规则

**资源映射规则**：

- Terraform资源 → CloudFormation资源
- Terraform变量 → CloudFormation参数
- Terraform输出 → CloudFormation输出

### 3.2 转换实现

**Terraform到CloudFormation转换器**（已在Terraform Schema转换体系中详细说明）：

参考 `Terraform_Schema/04_Transformation.md` 中的 `TerraformToCloudFormationConverter` 实现。

---

## 4. CloudFormation到Kubernetes转换

### 4.1 转换规则

**资源映射规则**：

- CloudFormation EKS资源 → Kubernetes资源
- CloudFormation ECS任务 → Kubernetes Pod
- CloudFormation配置 → Kubernetes ConfigMap

### 4.2 转换实现

**CloudFormation到Kubernetes转换器**：

```python
class CloudFormationToKubernetesConverter:
    """CloudFormation到Kubernetes转换器"""

    def convert(self, cfn_template_path: str) -> List[Dict]:
        """转换CloudFormation模板为Kubernetes资源"""
        # 读取CloudFormation模板
        with open(cfn_template_path, 'r') as f:
            cfn_template = yaml.safe_load(f) if cfn_template_path.endswith('.yaml') else json.load(f)

        k8s_resources = []
        resources = cfn_template.get('Resources', {})

        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get('Type', '')

            # 转换EKS相关资源
            if resource_type.startswith('AWS::EKS::'):
                k8s_resource = self._convert_eks_resource(resource_name, resource_config)
                if k8s_resource:
                    k8s_resources.append(k8s_resource)

            # 转换ECS任务定义
            elif resource_type == 'AWS::ECS::TaskDefinition':
                k8s_resource = self._convert_ecs_task_to_pod(resource_name, resource_config)
                if k8s_resource:
                    k8s_resources.append(k8s_resource)

        return k8s_resources

    def _convert_eks_resource(self, resource_name: str, resource_config: Dict) -> Optional[Dict]:
        """转换EKS资源为Kubernetes资源"""
        # EKS资源通常需要手动配置Kubernetes资源
        # 这里提供基础转换框架
        return None

    def _convert_ecs_task_to_pod(self, resource_name: str, resource_config: Dict) -> Dict:
        """转换ECS任务定义为Kubernetes Pod"""
        properties = resource_config.get('Properties', {})
        container_definitions = properties.get('ContainerDefinitions', [])

        containers = []
        for container_def in container_definitions:
            container = {
                'name': container_def.get('Name', 'container'),
                'image': container_def.get('Image', ''),
                'ports': [{'containerPort': port.get('ContainerPort')}
                         for port in container_def.get('PortMappings', [])],
                'env': [{'name': env.get('Name'), 'value': env.get('Value')}
                       for env in container_def.get('Environment', [])]
            }
            containers.append(container)

        pod = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': resource_name.lower().replace('-', '')
            },
            'spec': {
                'containers': containers
            }
        }

        return pod
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有CloudFormation资源都已转换
- 所有参数都已映射
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
class CloudFormationConversionValidator:
    """CloudFormation转换验证器"""

    def validate(self, cfn_template: Dict, terraform_config: str) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(cfn_template, terraform_config),
            'consistency': self._validate_consistency(cfn_template, terraform_config),
            'equivalence': self._validate_equivalence(cfn_template, terraform_config)
        }
        return results
```

---

## 6. CloudFormation数据存储与分析

### 6.1 PostgreSQL CloudFormation数据存储

**CloudFormation数据存储方案**：

```python
import psycopg2
import json

class CloudFormationDataStore:
    """CloudFormation数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建CloudFormation数据存储表"""
        with self.conn.cursor() as cur:
            # 模板定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cloudformation_templates (
                    id SERIAL PRIMARY KEY,
                    template_name VARCHAR(255) NOT NULL UNIQUE,
                    template_content JSONB NOT NULL,
                    template_format VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 资源定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cloudformation_resources (
                    id SERIAL PRIMARY KEY,
                    template_id INTEGER REFERENCES cloudformation_templates(id),
                    resource_type VARCHAR(255) NOT NULL,
                    resource_name VARCHAR(255) NOT NULL,
                    resource_properties JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(template_id, resource_type, resource_name)
                )
            """)

            # 堆栈表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cloudformation_stacks (
                    id SERIAL PRIMARY KEY,
                    template_id INTEGER REFERENCES cloudformation_templates(id),
                    stack_name VARCHAR(255) NOT NULL,
                    stack_status VARCHAR(50),
                    stack_outputs JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(template_id, stack_name)
                )
            """)

            self.conn.commit()
```

### 6.2 CloudFormation数据分析查询

**分析查询示例**：

```python
def analyze_cloudformation_usage(db_config: Dict):
    """分析CloudFormation使用情况"""
    store = CloudFormationDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询资源类型统计
        cur.execute("""
            SELECT
                resource_type,
                COUNT(*) as resource_count
            FROM cloudformation_resources
            GROUP BY resource_type
            ORDER BY resource_count DESC
        """)

        return cur.fetchall()
```

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理CloudFormation模板**：
   - 移除未使用的资源
   - 标准化命名
   - 验证模板正确性

2. **备份数据**：
   - 备份CloudFormation模板
   - 备份堆栈状态
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心资源
   - 再转换依赖资源
   - 最后转换参数和输出

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

- **cfn-flip**：CloudFormation模板格式转换
- **former2**：AWS资源到CloudFormation/Terraform转换

### 8.2 参考资源

- [CloudFormation文档](https://docs.aws.amazon.com/cloudformation/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws)
- [CloudFormation到Terraform迁移指南](https://www.terraform.io/docs/cloud/migrate/index.html)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
