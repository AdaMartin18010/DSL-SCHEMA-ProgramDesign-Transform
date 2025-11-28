# Terraform Schema转换体系

## 📑 目录

- [Terraform Schema转换体系](#terraform-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Terraform到CloudFormation转换](#2-terraform到cloudformation转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Terraform到Pulumi转换](#3-terraform到pulumi转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. Terraform到Kubernetes转换](#4-terraform到kubernetes转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 转换实现](#42-转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. Terraform数据存储与分析](#6-terraform数据存储与分析)
    - [6.1 PostgreSQL Terraform数据存储](#61-postgresql-terraform数据存储)
    - [6.2 Terraform数据分析查询](#62-terraform数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

---

## 1. 转换体系概述

Terraform Schema转换体系支持Terraform配置与其他IaC格式之间的转换。

### 1.1 转换目标

1. **Terraform到CloudFormation转换**：Terraform配置转换为CloudFormation模板
2. **Terraform到Pulumi转换**：Terraform配置转换为Pulumi程序
3. **Terraform到Kubernetes转换**：Terraform配置转换为Kubernetes资源
4. **Schema到数据库转换**：Terraform Schema定义到PostgreSQL存储

---

## 2. Terraform到CloudFormation转换

### 2.1 转换规则

**资源映射规则**：

| Terraform资源 | CloudFormation资源 | 映射说明 |
|--------------|-------------------|---------|
| `aws_vpc` | `AWS::EC2::VPC` | 直接映射 |
| `aws_subnet` | `AWS::EC2::Subnet` | 直接映射 |
| `aws_instance` | `AWS::EC2::Instance` | 直接映射 |
| `aws_s3_bucket` | `AWS::S3::Bucket` | 直接映射 |

**变量映射规则**：

- Terraform变量 → CloudFormation参数
- 变量类型映射（string、number、bool、list、map）
- 默认值映射

**输出映射规则**：

- Terraform输出 → CloudFormation输出
- 输出值表达式转换

### 2.2 完整转换实现

**Terraform到CloudFormation转换器**：

```python
#!/usr/bin/env python3
"""
Terraform到CloudFormation转换器
"""

import json
import hcl2
from typing import Dict, List, Any, Optional
from pathlib import Path

class TerraformToCloudFormationConverter:
    """Terraform到CloudFormation转换器"""

    # 资源类型映射表
    RESOURCE_MAPPING = {
        'aws_vpc': 'AWS::EC2::VPC',
        'aws_subnet': 'AWS::EC2::Subnet',
        'aws_internet_gateway': 'AWS::EC2::InternetGateway',
        'aws_route_table': 'AWS::EC2::RouteTable',
        'aws_security_group': 'AWS::EC2::SecurityGroup',
        'aws_instance': 'AWS::EC2::Instance',
        'aws_s3_bucket': 'AWS::S3::Bucket',
        'aws_iam_role': 'AWS::IAM::Role',
        'aws_iam_policy': 'AWS::IAM::Policy',
        'aws_lambda_function': 'AWS::Lambda::Function',
        'aws_api_gateway_rest_api': 'AWS::ApiGateway::RestApi',
    }

    # 属性映射表
    ATTRIBUTE_MAPPING = {
        'aws_vpc': {
            'cidr_block': 'CidrBlock',
            'enable_dns_hostnames': 'EnableDnsHostnames',
            'enable_dns_support': 'EnableDnsSupport',
            'tags': 'Tags'
        },
        'aws_subnet': {
            'vpc_id': 'VpcId',
            'cidr_block': 'CidrBlock',
            'availability_zone': 'AvailabilityZone',
            'map_public_ip_on_launch': 'MapPublicIpOnLaunch',
            'tags': 'Tags'
        }
    }

    def __init__(self):
        self.tf_config = {}
        self.cfn_template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Generated from Terraform",
            "Parameters": {},
            "Resources": {},
            "Outputs": {}
        }

    def convert(self, tf_file: str) -> Dict[str, Any]:
        """转换Terraform配置为CloudFormation模板"""
        # 解析Terraform文件
        self.tf_config = self._parse_terraform_file(tf_file)

        # 转换变量
        self._convert_variables()

        # 转换资源
        self._convert_resources()

        # 转换输出
        self._convert_outputs()

        return self.cfn_template

    def _parse_terraform_file(self, tf_file: str) -> Dict:
        """解析Terraform文件"""
        with open(tf_file, 'r') as f:
            return hcl2.load(f)

    def _convert_variables(self):
        """转换Terraform变量为CloudFormation参数"""
        variables = self.tf_config.get('variable', {})

        for var_name, var_config in variables.items():
            param = {
                "Type": self._map_terraform_type_to_cfn_type(
                    var_config.get('type', 'string')
                ),
                "Description": var_config.get('description', '')
            }

            # 添加默认值
            if 'default' in var_config:
                param["Default"] = var_config['default']

            self.cfn_template["Parameters"][var_name] = param

    def _convert_resources(self):
        """转换Terraform资源为CloudFormation资源"""
        resources = self.tf_config.get('resource', {})

        for resource_type, resource_instances in resources.items():
            for resource_name, resource_config in resource_instances.items():
                cfn_resource_type = self.RESOURCE_MAPPING.get(resource_type)
                if not cfn_resource_type:
                    print(f"Warning: No mapping for resource type {resource_type}")
                    continue

                cfn_resource = {
                    "Type": cfn_resource_type,
                    "Properties": self._convert_resource_properties(
                        resource_type, resource_config
                    )
                }

                # 添加DependsOn
                if 'depends_on' in resource_config:
                    cfn_resource["DependsOn"] = [
                        self._get_cfn_logical_id(dep)
                        for dep in resource_config['depends_on']
                    ]

                # 添加DeletionPolicy
                if 'lifecycle' in resource_config:
                    lifecycle = resource_config['lifecycle']
                    if lifecycle.get('prevent_destroy'):
                        cfn_resource["DeletionPolicy"] = "Retain"

                logical_id = self._get_cfn_logical_id(f"{resource_type}.{resource_name}")
                self.cfn_template["Resources"][logical_id] = cfn_resource

    def _convert_resource_properties(self, resource_type: str,
                                    resource_config: Dict) -> Dict:
        """转换资源属性"""
        properties = {}
        attribute_mapping = self.ATTRIBUTE_MAPPING.get(resource_type, {})

        for tf_key, tf_value in resource_config.items():
            if tf_key in ['depends_on', 'lifecycle', 'count', 'for_each']:
                continue

            # 使用映射表或直接使用键名
            cfn_key = attribute_mapping.get(tf_key, self._to_pascal_case(tf_key))
            properties[cfn_key] = self._convert_value(tf_value)

        return properties

    def _convert_value(self, value: Any) -> Any:
        """转换值（处理引用、函数等）"""
        if isinstance(value, str):
            # 处理Terraform引用
            if value.startswith('${'):
                return self._convert_terraform_expression(value)
            return value
        elif isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_value(item) for item in value]
        else:
            return value

    def _convert_terraform_expression(self, expr: str) -> Any:
        """转换Terraform表达式为CloudFormation引用"""
        # 简化实现，实际应使用完整的表达式解析器
        if 'var.' in expr:
            # 变量引用 -> CloudFormation参数引用
            var_name = expr.split('var.')[1].split('}')[0]
            return {"Ref": var_name}
        elif 'resource.' in expr:
            # 资源引用 -> CloudFormation资源引用
            # 例如: ${aws_vpc.main.id} -> !GetAtt VpcMain.Id
            parts = expr.split('.')
            if len(parts) >= 3:
                resource_type = parts[1]
                resource_name = parts[2]
                attribute = parts[3] if len(parts) > 3 else 'id'
                logical_id = self._get_cfn_logical_id(f"{resource_type}.{resource_name}")
                return {"Fn::GetAtt": [logical_id, self._to_pascal_case(attribute)]}
        elif 'data.' in expr:
            # 数据源引用（需要特殊处理）
            pass

        return expr

    def _convert_outputs(self):
        """转换Terraform输出为CloudFormation输出"""
        outputs = self.tf_config.get('output', {})

        for output_name, output_config in outputs.items():
            cfn_output = {
                "Description": output_config.get('description', ''),
                "Value": self._convert_value(output_config.get('value', ''))
            }

            # 添加Export
            if output_config.get('export'):
                cfn_output["Export"] = {
                    "Name": output_config['export'].get('name', output_name)
                }

            self.cfn_template["Outputs"][output_name] = cfn_output

    def _map_terraform_type_to_cfn_type(self, tf_type: str) -> str:
        """映射Terraform类型到CloudFormation类型"""
        type_mapping = {
            'string': 'String',
            'number': 'Number',
            'bool': 'String',  # CloudFormation使用String表示布尔值
            'list': 'CommaDelimitedList',
            'map': 'String'  # 需要特殊处理
        }
        return type_mapping.get(tf_type, 'String')

    def _get_cfn_logical_id(self, tf_resource_id: str) -> str:
        """生成CloudFormation逻辑ID"""
        # 例如: aws_vpc.main -> VpcMain
        parts = tf_resource_id.split('.')
        if len(parts) == 2:
            resource_type = parts[0].replace('aws_', '')
            resource_name = parts[1]
            return f"{self._to_pascal_case(resource_type)}{self._to_pascal_case(resource_name)}"
        return self._to_pascal_case(tf_resource_id.replace('.', ''))

    def _to_pascal_case(self, s: str) -> str:
        """转换为PascalCase"""
        return ''.join(word.capitalize() for word in s.split('_'))

# 使用示例
if __name__ == '__main__':
    converter = TerraformToCloudFormationConverter()

    # 转换Terraform配置
    cfn_template = converter.convert('main.tf')

    # 输出CloudFormation模板
    print(json.dumps(cfn_template, indent=2))

    # 保存到文件
    with open('template.yaml', 'w') as f:
        json.dump(cfn_template, f, indent=2)
```

---

## 3. Terraform到Pulumi转换

### 3.1 转换规则

**资源映射规则**：

- Terraform资源 → Pulumi资源类
- Terraform变量 → Pulumi配置
- Terraform输出 → Pulumi输出

### 3.2 转换实现

**Terraform到Pulumi转换器（Python）**：

```python
def terraform_to_pulumi(tf_file: str, language: str = 'python') -> str:
    """将Terraform配置转换为Pulumi程序"""
    tf_config = parse_terraform_file(tf_file)

    if language == 'python':
        return generate_pulumi_python(tf_config)
    elif language == 'typescript':
        return generate_pulumi_typescript(tf_config)
    else:
        raise ValueError(f"Unsupported language: {language}")

def generate_pulumi_python(tf_config: Dict) -> str:
    """生成Pulumi Python代码"""
    code = "import pulumi\n"
    code += "import pulumi_aws as aws\n\n"

    # 转换资源
    resources = tf_config.get('resource', {})
    for resource_type, instances in resources.items():
        for name, config in instances.items():
            provider = resource_type.split('_')[0]  # aws, azure, etc.
            resource_class = resource_type.replace(f"{provider}_", "").title()
            code += f"{name} = aws.{resource_class}('{name}',\n"
            for key, value in config.items():
                code += f"    {key}={format_pulumi_value(value)},\n"
            code += ")\n\n"

    return code
```

---

## 4. Terraform到Kubernetes转换

### 4.1 转换规则

**资源映射规则**：

- `kubernetes_deployment` → `Deployment`
- `kubernetes_service` → `Service`
- `kubernetes_config_map` → `ConfigMap`
- `kubernetes_secret` → `Secret`

### 4.2 转换实现

**Terraform Kubernetes资源到YAML转换**：

```python
def terraform_kubernetes_to_yaml(tf_file: str) -> List[str]:
    """将Terraform Kubernetes资源转换为YAML"""
    tf_config = parse_terraform_file(tf_file)
    yaml_resources = []

    resources = tf_config.get('resource', {})
    for resource_type, instances in resources.items():
        if resource_type.startswith('kubernetes_'):
            for name, config in instances.items():
                k8s_resource = convert_to_kubernetes_resource(
                    resource_type, name, config
                )
                yaml_resources.append(yaml.dump(k8s_resource))

    return yaml_resources
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有资源都已转换
- 所有变量都已映射
- 所有输出都已转换

**一致性验证**：

- 资源属性一致性
- 依赖关系一致性
- 引用关系一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 资源行为一致
- 输出值一致

### 5.2 验证实现

**转换验证器**：

```python
class ConversionValidator:
    """转换验证器"""

    def validate(self, tf_config: Dict, cfn_template: Dict) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(tf_config, cfn_template),
            'consistency': self._validate_consistency(tf_config, cfn_template),
            'equivalence': self._validate_equivalence(tf_config, cfn_template)
        }
        return results

    def _validate_completeness(self, tf_config: Dict, cfn_template: Dict) -> bool:
        """验证完整性"""
        tf_resources = self._get_all_resources(tf_config)
        cfn_resources = cfn_template.get('Resources', {})

        # 检查所有资源都已转换
        for tf_resource in tf_resources:
            if not self._is_resource_converted(tf_resource, cfn_resources):
                return False

        return True

    def _validate_consistency(self, tf_config: Dict, cfn_template: Dict) -> bool:
        """验证一致性"""
        # 实现一致性检查逻辑
        return True

    def _validate_equivalence(self, tf_config: Dict, cfn_template: Dict) -> bool:
        """验证功能等价性"""
        # 实现等价性检查逻辑
        return True
```

---

## 6. Terraform数据存储与分析

### 6.1 PostgreSQL Terraform数据存储

**Terraform数据存储方案**：

```python
import psycopg2
import json

class TerraformDataStore:
    """Terraform数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Terraform数据存储表"""
        with self.conn.cursor() as cur:
            # 配置定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS terraform_configs (
                    id SERIAL PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL UNIQUE,
                    config_content TEXT NOT NULL,
                    terraform_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 资源定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS terraform_resources (
                    id SERIAL PRIMARY KEY,
                    config_id INTEGER REFERENCES terraform_configs(id),
                    resource_type VARCHAR(255) NOT NULL,
                    resource_name VARCHAR(255) NOT NULL,
                    resource_config JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(config_id, resource_type, resource_name)
                )
            """)

            # 状态表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS terraform_states (
                    id SERIAL PRIMARY KEY,
                    config_id INTEGER REFERENCES terraform_configs(id),
                    state_version VARCHAR(50),
                    state_content JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
```

### 6.2 Terraform数据分析查询

**分析查询示例**：

```python
def analyze_terraform_usage(db_config: Dict):
    """分析Terraform使用情况"""
    store = TerraformDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询资源类型统计
        cur.execute("""
            SELECT
                resource_type,
                COUNT(*) as resource_count
            FROM terraform_resources
            GROUP BY resource_type
            ORDER BY resource_count DESC
        """)

        return cur.fetchall()
```

---

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理Terraform配置**：
   - 移除未使用的资源
   - 简化复杂表达式
   - 标准化命名

2. **验证Terraform配置**：
   - 运行`terraform validate`
   - 运行`terraform plan`
   - 检查所有资源

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心资源
   - 再转换依赖资源
   - 最后转换输出

2. **验证转换结果**：
   - 检查资源完整性
   - 验证属性映射
   - 测试功能等价性

### 7.3 转换后优化

1. **优化CloudFormation模板**：
   - 添加参数验证
   - 优化资源依赖
   - 添加标签和元数据

2. **测试和验证**：
   - 使用CloudFormation验证工具
   - 在测试环境部署
   - 验证功能正确性

## 8. 转换工具和资源

### 8.1 转换工具

- **cfn-include**：CloudFormation到Terraform转换
- **terraform2cloudformation**：Terraform到CloudFormation转换
- **pulumi-terraform**：Terraform到Pulumi转换

### 8.2 参考资源

- [Terraform文档](https://www.terraform.io/docs)
- [CloudFormation文档](https://docs.aws.amazon.com/cloudformation/)
- [Pulumi文档](https://www.pulumi.com/docs/)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
