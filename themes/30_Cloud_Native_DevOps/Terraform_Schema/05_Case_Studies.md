# Terraform Schema实践案例

## 📑 目录

- [Terraform Schema实践案例](#terraform-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：多云基础设施即代码平台](#2-案例1多云基础设施即代码平台)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估与ROI](#26-效果评估与roi)

---

## 2. 案例1：多云基础设施即代码平台

### 2.1 企业背景

**企业概况**：
"环球科技"（化名）是全球化企业，业务覆盖AWS、阿里云、腾讯云三大云平台，管理超过2000台云服务器，日均基础设施变更是50+次。

### 2.2 业务痛点

1. **手动配置错误率高**：人工配置错误率达15%，影响业务稳定
2. **环境不一致**：开发、测试、生产环境配置不一致
3. **变更追溯困难**：无法追踪配置变更历史，问题定位难
4. **多云管理复杂**：三个云平台使用不同工具，管理分散
5. **成本不透明**：资源使用分散，成本难以统一管理

### 2.3 业务目标

1. 实现100%基础设施即代码
2. 确保所有环境配置一致
3. 完整的变更历史和审计
4. 统一多云管理界面
5. 成本可视化，降低30%云支出

### 2.4 技术挑战

1. **多云抽象层**：统一不同云平台的资源模型
2. **状态管理**：多团队协作的状态锁定和版本控制
3. **模块复用**：构建可复用的基础设施模块
4. **安全合规**：敏感数据加密和访问控制
5. **成本控制**：资源使用监控和优化建议

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
Terraform Schema完整实现
环球科技多云基础设施即代码平台
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import hcl2


class CloudProvider(str, Enum):
    """云提供商"""
    AWS = "aws"
    ALICLOUD = "alicloud"
    TENCENTCLOUD = "tencentcloud"
    AZURE = "azurerm"
    GCP = "google"


class ResourceType(str, Enum):
    """资源类型"""
    VPC = "vpc"
    SUBNET = "subnet"
    INSTANCE = "instance"
    RDS = "rds"
    LB = "lb"
    OSS = "oss"
    K8S = "kubernetes"


@dataclass
class TerraformVariable:
    """Terraform变量"""
    name: str
    description: str
    type: str = "string"
    default: Any = None
    sensitive: bool = False
    
    def to_hcl(self) -> str:
        """转换为HCL"""
        hcl = f'variable "{self.name}" {{\n'
        hcl += f'  description = "{self.description}"\n'
        hcl += f'  type        = {self.type}\n'
        if self.default is not None:
            if isinstance(self.default, str):
                hcl += f'  default     = "{self.default}"\n'
            else:
                hcl += f'  default     = {self.default}\n'
        if self.sensitive:
            hcl += '  sensitive   = true\n'
        hcl += '}\n'
        return hcl


@dataclass
class TerraformResource:
    """Terraform资源"""
    resource_type: str
    name: str
    provider: CloudProvider
    properties: Dict = field(default_factory=dict)
    
    def to_hcl(self) -> str:
        """转换为HCL"""
        hcl = f'resource "{self.resource_type}" "{self.name}" {{\n'
        for key, value in self.properties.items():
            hcl += f'  {key} = {self._format_value(value)}\n'
        hcl += '}\n'
        return hcl
    
    def _format_value(self, value: Any) -> str:
        """格式化值"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (list, dict)):
            return json.dumps(value)
        return str(value)


@dataclass
class TerraformModule:
    """Terraform模块"""
    name: str
    source: str
    version: Optional[str] = None
    variables: Dict = field(default_factory=dict)
    
    def to_hcl(self) -> str:
        """转换为HCL"""
        hcl = f'module "{self.name}" {{\n'
        hcl += f'  source = "{self.source}"\n'
        if self.version:
            hcl += f'  version = "{self.version}"\n'
        for key, value in self.variables.items():
            hcl += f'  {key} = {self._format_value(value)}\n'
        hcl += '}\n'
        return hcl
    
    def _format_value(self, value: Any) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, dict):
            return json.dumps(value)
        return str(value)


class TerraformGenerator:
    """Terraform代码生成器"""
    
    def __init__(self, project_name: str, provider: CloudProvider):
        self.project_name = project_name
        self.provider = provider
        self.variables: List[TerraformVariable] = []
        self.resources: List[TerraformResource] = []
        self.modules: List[TerraformModule] = []
        self.outputs: Dict = {}
    
    def add_variable(self, variable: TerraformVariable):
        """添加变量"""
        self.variables.append(variable)
        return self
    
    def add_resource(self, resource: TerraformResource):
        """添加资源"""
        self.resources.append(resource)
        return self
    
    def add_module(self, module: TerraformModule):
        """添加模块"""
        self.modules.append(module)
        return self
    
    def add_output(self, name: str, value: str, description: str = ""):
        """添加输出"""
        self.outputs[name] = {"value": value, "description": description}
        return self
    
    def generate_provider_config(self) -> str:
        """生成Provider配置"""
        configs = {
            CloudProvider.AWS: '''
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "{project}/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "{project}"
      ManagedBy   = "Terraform"
    }
  }
}
''',
            CloudProvider.ALICLOUD: '''
terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.200"
    }
  }
}

provider "alicloud" {
  region = var.region
}
'''
        }
        return configs.get(self.provider, "").format(project=self.project_name)
    
    def generate(self) -> str:
        """生成完整Terraform配置"""
        result = self.generate_provider_config()
        result += "\n"
        
        # 变量
        for var in self.variables:
            result += var.to_hcl() + "\n"
        
        # 模块
        for module in self.modules:
            result += module.to_hcl() + "\n"
        
        # 资源
        for resource in self.resources:
            result += resource.to_hcl() + "\n"
        
        # 输出
        if self.outputs:
            for name, output in self.outputs.items():
                result += f'output "{name}" {{\n'
                result += f'  description = "{output.get("description", "")}"\n'
                result += f'  value       = {output["value"]}\n'
                result += '}\n\n'
        
        return result


class MultiCloudManager:
    """多云管理器"""
    
    def __init__(self):
        self.environments: Dict[str, TerraformGenerator] = {}
    
    def create_environment(self, name: str, provider: CloudProvider):
        """创建环境"""
        generator = TerraformGenerator(name, provider)
        self.environments[name] = generator
        return generator
    
    def generate_multi_cloud_vpc(self) -> Dict[str, str]:
        """生成多云VPC配置"""
        configs = {}
        
        # AWS VPC
        aws_gen = self.create_environment("aws-prod", CloudProvider.AWS)
        aws_gen.add_variable(TerraformVariable(
            name="aws_region",
            description="AWS Region",
            default="us-east-1"
        )).add_variable(TerraformVariable(
            name="environment",
            description="Environment name",
            default="production"
        )).add_resource(TerraformResource(
            resource_type="aws_vpc",
            name="main",
            provider=CloudProvider.AWS,
            properties={
                "cidr_block": "10.0.0.0/16",
                "enable_dns_hostnames": True,
                "enable_dns_support": True,
                "tags": {"Name": "main-vpc"}
            }
        )).add_output("vpc_id", "aws_vpc.main.id", "VPC ID")
        
        configs["aws"] = aws_gen.generate()
        
        # 阿里云 VPC
        ali_gen = self.create_environment("aliyun-prod", CloudProvider.ALICLOUD)
        ali_gen.add_variable(TerraformVariable(
            name="region",
            description="Alicloud Region",
            default="cn-shanghai"
        )).add_resource(TerraformResource(
            resource_type="alicloud_vpc",
            name="main",
            provider=CloudProvider.ALICLOUD,
            properties={
                "vpc_name": "main-vpc",
                "cidr_block": "10.0.0.0/16"
            }
        )).add_output("vpc_id", "alicloud_vpc.main.id", "VPC ID")
        
        configs["aliyun"] = ali_gen.generate()
        
        return configs


# 使用示例
def main():
    print("=" * 60)
    print("【环球科技Terraform多云基础设施平台】")
    print("=" * 60)
    
    # 创建多云管理器
    manager = MultiCloudManager()
    configs = manager.generate_multi_cloud_vpc()
    
    for cloud, config in configs.items():
        print(f"\n☁️  {cloud.upper()} 配置:")
        print("-" * 40)
        print(config[:1500])
        print("...")
    
    print("\n📊 基础设施即代码效果:")
    print("-" * 40)
    print("指标              | 改进前  | 改进后   | 提升")
    print("-" * 40)
    print("环境创建时间      | 数天    | 30分钟   | 99%")
    print("配置错误率        | 15%     | <1%      | 93%")
    print("环境一致性        | 60%     | 100%     | 67%")
    print("变更追溯          | 无      | 完整     | 100%")
    print("云成本优化        | 基准    | -35%     | 35%")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
```

### 2.6 效果评估与ROI

| 指标 | 改进前 | 改进后 | 提升幅度 |
|------|--------|--------|----------|
| 环境创建时间 | 数天 | 30分钟 | 99%提升 |
| 配置错误率 | 15% | <1% | 93%降低 |
| 环境一致性 | 60% | 100% | 67%提升 |
| 变更追溯 | 无 | 完整 | 100% |
| 云成本 | 基准 | -35% | 35%节省 |

**ROI计算**：

```
项目投资：380万元
年度收益：1,680万元
  - 云成本节省：980万元
  - 效率提升：420万元
  - 故障减少收益：280万元

第一年ROI = (1,680 - 380) / 380 = 342%
```

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
