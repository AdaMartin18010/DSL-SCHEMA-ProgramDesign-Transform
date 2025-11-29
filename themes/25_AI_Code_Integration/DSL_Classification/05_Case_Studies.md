# DSL分类实践案例

## 📑 目录

- [DSL分类实践案例](#dsl分类实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：配置DSL应用](#2-案例1配置dsl应用)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 实现示例](#22-实现示例)
  - [3. 案例2：查询DSL应用](#3-案例2查询dsl应用)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现示例](#32-实现示例)

---

## 1. 案例概述

本文档提供DSL分类在实际企业应用中的实践案例，涵盖配置DSL、查询DSL、转换DSL等真实场景。

**案例类型**：

1. **配置DSL应用系统**：使用YAML配置DSL管理微服务配置
2. **查询DSL应用系统**：使用GraphQL查询DSL构建API查询接口
3. **转换DSL应用系统**：DSL转换工具
4. **DSL分类管理系统**：DSL分类和管理
5. **DSL数据存储与分析系统**：DSL数据分析和监控

**参考企业案例**：
- **YAML配置DSL**：Docker Compose、Kubernetes配置
- **GraphQL查询DSL**：GraphQL查询语言

---

## 2. 案例1：企业配置DSL应用系统

### 2.1 业务背景

**企业背景**：
某微服务架构企业需要构建配置DSL应用系统，使用YAML配置DSL管理微服务配置，支持环境变量替换和配置验证，提高配置管理效率和准确性。

**业务痛点**：
1. **配置管理分散**：微服务配置管理分散
2. **环境差异处理困难**：不同环境配置差异处理困难
3. **配置验证不足**：配置验证不足
4. **配置更新效率低**：配置更新效率低

**业务目标**：
- 统一配置管理
- 简化环境差异处理
- 增强配置验证
- 提高配置更新效率

### 2.2 技术挑战

1. **配置模型设计**：设计配置数据模型
2. **环境变量替换**：实现环境变量替换
3. **配置验证**：实现配置验证
4. **配置管理**：实现配置管理

### 2.3 解决方案

**使用YAML定义服务配置，支持环境变量替换和配置验证**：

### 2.4 完整代码实现

**配置DSL应用系统Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
DSL分类Schema实现
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import yaml
import os
import re

@dataclass
class ServiceConfig:
    """服务配置"""
    service_name: str
    image: str
    ports: List[Dict[str, Any]] = field(default_factory=list)
    environment: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)

@dataclass
class ConfigDSLProcessor:
    """配置DSL处理器"""
    
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def replace_env_variables(self, config: Dict) -> Dict:
        """替换环境变量"""
        config_str = yaml.dump(config)
        
        # 替换 ${VAR} 格式的环境变量
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        config_str = re.sub(r'\$\{([^}]+)\}', replace_var, config_str)
        
        return yaml.safe_load(config_str)
    
    def validate_config(self, config: Dict) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        if 'services' not in config:
            errors.append("Missing 'services' section")
            return False, errors
        
        services = config['services']
        for service_name, service_config in services.items():
            if 'image' not in service_config:
                errors.append(f"Service '{service_name}' missing 'image'")
            
            if 'ports' in service_config:
                for port in service_config['ports']:
                    if isinstance(port, str):
                        if ':' not in port:
                            errors.append(f"Service '{service_name}' invalid port format: {port}")
        
        return len(errors) == 0, errors
    
    def process_config(self, config_file: str) -> Dict:
        """处理配置文件"""
        # 加载配置
        config = self.load_config(config_file)
        
        # 替换环境变量
        config = self.replace_env_variables(config)
        
        # 验证配置
        is_valid, errors = self.validate_config(config)
        if not is_valid:
            raise ValueError(f"Configuration validation failed: {errors}")
        
        return config

# 使用示例
if __name__ == '__main__':
    # 设置环境变量
    os.environ['DATABASE_URL'] = 'postgresql://localhost:5432/mydb'
    os.environ['REDIS_URL'] = 'redis://localhost:6379'
    
    # 创建配置DSL处理器
    processor = ConfigDSLProcessor()
    
    # 创建配置文件内容
    config_content = """
services:
  api:
    image: myapp/api:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - database
      - redis
  database:
    image: postgres:14
    ports:
      - "5432:5432"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
"""
    
    # 写入临时文件
    with open('docker-compose.yml', 'w') as f:
        f.write(config_content)
    
    # 处理配置
    try:
        processed_config = processor.process_config('docker-compose.yml')
        print(f"处理后的配置: {processed_config}")
    except ValueError as e:
        print(f"配置验证失败: {e}")
```

---

## 3. 案例2：查询DSL应用

### 3.1 场景描述

**业务背景**：
使用GraphQL查询DSL构建灵活的API查询接口。

**解决方案**：
使用GraphQL定义查询接口，支持客户端自定义查询字段。

### 3.2 实现示例

```graphql
type Query {
  users(filter: UserFilter): [User]
  user(id: ID!): User
}

type User {
  id: ID!
  name: String!
  email: String!
  orders: [Order]
}
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Classification_System.md` - 分类体系
- `03_Typical_Examples.md` - 典型示例
- `04_Best_Practices.md` - 最佳实践

**创建时间**：2025-01-21
**最后更新**：2025-01-21
