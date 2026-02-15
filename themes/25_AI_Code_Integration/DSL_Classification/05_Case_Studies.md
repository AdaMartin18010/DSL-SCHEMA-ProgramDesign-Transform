# DSL分类实践案例

## 📑 目录

- [DSL分类实践案例](#dsl分类实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：云原生企业配置DSL应用系统](#2-案例1云原生企业配置dsl应用系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)
  - [3. 案例2：数据平台查询DSL应用系统](#3-案例2数据平台查询dsl应用系统)
    - [3.1 业务背景](#31-业务背景)
    - [3.2 技术挑战](#32-技术挑战)
    - [3.3 解决方案](#33-解决方案)
    - [3.4 完整代码实现](#34-完整代码实现)
    - [3.5 效果评估](#35-效果评估)
  - [4. 案例3：智能制造转换DSL应用系统](#4-案例3智能制造转换dsl应用系统)
    - [4.1 业务背景](#41-业务背景)
    - [4.2 技术挑战](#42-技术挑战)
    - [4.3 解决方案](#43-解决方案)
    - [4.4 完整代码实现](#44-完整代码实现)
    - [4.5 效果评估](#45-效果评估)

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

## 2. 案例1：云原生企业配置DSL应用系统

### 2.1 业务背景

**企业背景**：
某云原生技术公司（服务50+企业客户，管理1000+微服务实例）需要构建配置DSL应用系统，使用YAML配置DSL管理微服务配置，支持环境变量替换和配置验证，提高配置管理效率和准确性。

**业务痛点**：

1. **配置管理分散**：微服务配置分散在100+个Git仓库中，版本混乱，难以追踪变更历史
2. **环境差异处理困难**：开发、测试、生产环境配置差异大，人工维护容易出错，环境切换耗时2小时以上
3. **配置验证不足**：缺乏统一的配置验证机制，60%的配置错误在部署后才发现，平均修复时间4小时
4. **配置更新效率低**：单次配置更新需要修改多个文件，涉及5-10个服务，平均耗时3天
5. **安全合规风险**：敏感信息（密码、密钥）硬编码在配置中，存在严重安全隐患，合规审计难以通过

**业务目标**：

1. **统一配置管理**：建立集中式配置管理平台，配置查找时间从2小时缩短至5分钟
2. **自动化环境差异处理**：实现环境配置的自动切换，切换时间从2小时缩短至5分钟
3. **增强配置验证**：实现部署前100%配置验证，配置错误在部署前发现率达99%
4. **提高配置更新效率**：单次配置更新时间从3天缩短至30分钟
5. **加强安全合规**：敏感信息全部加密存储，100%通过安全合规审计

### 2.2 技术挑战

1. **配置模型设计**：设计统一的配置数据模型，支持多种微服务框架（Spring Cloud、Dubbo、Istio等）
2. **环境变量替换**：实现复杂的环境变量替换逻辑，支持嵌套变量、条件变量和动态计算
3. **配置验证引擎**：构建多维度验证引擎，包括语法验证、语义验证、依赖验证和安全验证
4. **配置版本管理**：实现配置的版本控制、变更审计和快速回滚能力
5. **敏感信息管理**：建立安全的密钥管理机制，支持多种加密算法和密钥轮换

### 2.3 解决方案

**使用YAML定义服务配置，支持环境变量替换和配置验证**：

采用分层架构：
- **配置定义层**：使用YAML DSL定义配置结构和约束
- **模板引擎层**：实现环境变量替换和动态渲染
- **验证引擎层**：多维度验证配置的正确性
- **执行层**：对接K8s、Consul等配置中心

### 2.4 完整代码实现

**配置DSL应用系统Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
DSL分类Schema实现 - 云原生配置DSL系统
支持环境变量替换、配置验证、敏感信息管理
"""

from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import yaml
import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
import copy

class ConfigValueType(Enum):
    """配置值类型"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    LIST = "list"
    MAP = "map"
    SECRET = "secret"
    REFERENCE = "reference"

class Environment(Enum):
    """环境类型"""
    DEVELOPMENT = "dev"
    TESTING = "test"
    STAGING = "staging"
    PRODUCTION = "prod"

@dataclass
class ConfigSchema:
    """配置Schema定义"""
    name: str
    value_type: ConfigValueType
    required: bool = True
    default: Any = None
    description: str = ""
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    sensitive: bool = False

@dataclass
class ConfigValue:
    """配置值"""
    key: str
    value: Any
    value_type: ConfigValueType
    source: str = ""
    is_secret: bool = False

class SecretManager:
    """密钥管理器"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.getenv("CONFIG_ENCRYPTION_KEY", "default-key")
        self.secrets: Dict[str, str] = {}
        self._load_secrets()
    
    def _load_secrets(self):
        """加载密钥（实际项目中应从安全存储加载）"""
        # 模拟从Vault加载
        self.secrets = {
            "database.password": "encrypted:xxx",
            "api.key": "encrypted:yyy",
            "jwt.secret": "encrypted:zzz"
        }
    
    def get_secret(self, key: str) -> Optional[str]:
        """获取密钥"""
        return self.secrets.get(key)
    
    def mask_secret(self, value: str) -> str:
        """脱敏显示"""
        if len(value) <= 4:
            return "****"
        return value[:2] + "****" + value[-2:]

class EnvironmentVariableResolver:
    """环境变量解析器"""
    
    # 变量引用模式: ${VAR} 或 ${VAR:-default} 或 ${VAR:?error}
    VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.builtins = self._load_builtins()
    
    def _load_builtins(self) -> Dict[str, str]:
        """加载内置变量"""
        return {
            "ENV": self.environment.value,
            "ENV_UPPER": self.environment.value.upper(),
            "TIMESTAMP": datetime.now().isoformat(),
            "DATE": datetime.now().strftime("%Y-%m-%d"),
            "RANDOM": lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        }
    
    def resolve(self, value: Any, context: Optional[Dict] = None) -> Any:
        """解析变量"""
        if isinstance(value, str):
            return self._resolve_string(value, context or {})
        elif isinstance(value, dict):
            return {k: self.resolve(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.resolve(item, context) for item in value]
        return value
    
    def _resolve_string(self, value: str, context: Dict) -> str:
        """解析字符串中的变量"""
        def replace_var(match):
            var_expr = match.group(1)
            
            # 处理默认值语法: VAR:-default
            if ':-' in var_expr:
                var_name, default = var_expr.split(':-', 1)
                var_value = self._get_variable(var_name.strip(), context)
                return var_value if var_value else default
            
            # 处理错误语法: VAR:?error
            if ':?' in var_expr:
                var_name, error_msg = var_expr.split(':?', 1)
                var_value = self._get_variable(var_name.strip(), context)
                if not var_value:
                    raise ValueError(f"Required variable {var_name} not set: {error_msg}")
                return var_value
            
            # 简单变量
            return self._get_variable(var_expr.strip(), context)
        
        return self.VAR_PATTERN.sub(replace_var, value)
    
    def _get_variable(self, name: str, context: Dict) -> str:
        """获取变量值"""
        # 优先级: context > environment > builtins
        if name in context:
            value = context[name]
            return str(value() if callable(value) else value)
        
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value
        
        if name in self.builtins:
            value = self.builtins[name]
            return str(value() if callable(value) else value)
        
        return ""

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.rules: Dict[str, Callable[[Any], Optional[str]]] = {
            "required": self._validate_required,
            "type": self._validate_type,
            "min": self._validate_min,
            "max": self._validate_max,
            "pattern": self._validate_pattern,
            "enum": self._validate_enum,
            "custom": self._validate_custom
        }
    
    def validate(self, config: Dict[str, Any], schema: Dict[str, ConfigSchema]) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        # 检查必需字段
        for key, field_schema in schema.items():
            if field_schema.required and key not in config:
                errors.append(f"Missing required field: {key}")
                continue
            
            if key in config:
                value = config[key]
                
                # 类型验证
                type_error = self._validate_type_value(value, field_schema.value_type)
                if type_error:
                    errors.append(f"Field '{key}': {type_error}")
                
                # 规则验证
                for rule in field_schema.validation_rules:
                    rule_type = rule.get("type")
                    if rule_type in self.rules:
                        error = self.rules[rule_type](value, rule)
                        if error:
                            errors.append(f"Field '{key}': {error}")
        
        # 检查未知字段
        known_fields = set(schema.keys())
        unknown_fields = set(config.keys()) - known_fields
        if unknown_fields:
            errors.append(f"Unknown fields: {unknown_fields}")
        
        return len(errors) == 0, errors
    
    def _validate_required(self, value: Any, rule: Dict) -> Optional[str]:
        if value is None or value == "":
            return "Value is required"
        return None
    
    def _validate_type(self, value: Any, rule: Dict) -> Optional[str]:
        expected_type = rule.get("value")
        # 类型验证在validate方法中处理
        return None
    
    def _validate_min(self, value: Any, rule: Dict) -> Optional[str]:
        min_val = rule.get("value")
        try:
            if float(value) < float(min_val):
                return f"Value {value} is less than minimum {min_val}"
        except (ValueError, TypeError):
            return f"Cannot compare value with minimum"
        return None
    
    def _validate_max(self, value: Any, rule: Dict) -> Optional[str]:
        max_val = rule.get("value")
        try:
            if float(value) > float(max_val):
                return f"Value {value} is greater than maximum {max_val}"
        except (ValueError, TypeError):
            return f"Cannot compare value with maximum"
        return None
    
    def _validate_pattern(self, value: Any, rule: Dict) -> Optional[str]:
        pattern = rule.get("value")
        if not re.match(pattern, str(value)):
            return f"Value does not match pattern: {pattern}"
        return None
    
    def _validate_enum(self, value: Any, rule: Dict) -> Optional[str]:
        allowed = rule.get("value", [])
        if value not in allowed:
            return f"Value must be one of: {allowed}"
        return None
    
    def _validate_custom(self, value: Any, rule: Dict) -> Optional[str]:
        validator = rule.get("validator")
        if callable(validator):
            return validator(value)
        return None
    
    def _validate_type_value(self, value: Any, expected_type: ConfigValueType) -> Optional[str]:
        """验证值类型"""
        type_checks = {
            ConfigValueType.STRING: lambda v: isinstance(v, str),
            ConfigValueType.INTEGER: lambda v: isinstance(v, int) or (isinstance(v, str) and v.isdigit()),
            ConfigValueType.BOOLEAN: lambda v: isinstance(v, bool) or str(v).lower() in ("true", "false", "yes", "no", "1", "0"),
            ConfigValueType.LIST: lambda v: isinstance(v, list),
            ConfigValueType.MAP: lambda v: isinstance(v, dict),
        }
        
        if expected_type in type_checks:
            if not type_checks[expected_type](value):
                return f"Expected type {expected_type.value}, got {type(value).__name__}"
        
        return None

@dataclass
class ConfigDSLProcessor:
    """配置DSL处理器"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.var_resolver = EnvironmentVariableResolver(environment)
        self.validator = ConfigValidator()
        self.secret_manager = SecretManager()
        self.config_history: List[Dict] = []
    
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return yaml.safe_load(content)
    
    def process_config(self, config: Dict, schema: Optional[Dict[str, ConfigSchema]] = None,
                       context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理配置"""
        result = {
            "config": None,
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "metadata": {
                "environment": self.environment.value,
                "processed_at": datetime.now().isoformat()
            }
        }
        
        try:
            # 深拷贝配置
            processed_config = copy.deepcopy(config)
            
            # 环境变量替换
            processed_config = self.var_resolver.resolve(processed_config, context)
            
            # 处理敏感信息
            processed_config = self._process_secrets(processed_config)
            
            # Schema验证
            if schema:
                is_valid, errors = self.validator.validate(processed_config, schema)
                result["is_valid"] = is_valid
                result["errors"] = errors
                if not is_valid:
                    return result
            else:
                result["is_valid"] = True
            
            result["config"] = processed_config
            
            # 记录历史
            self.config_history.append({
                "timestamp": datetime.now().isoformat(),
                "environment": self.environment.value,
                "config_hash": hashlib.md5(json.dumps(processed_config, sort_keys=True).encode()).hexdigest()[:16]
            })
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    def _process_secrets(self, config: Dict) -> Dict:
        """处理敏感信息"""
        secret_keywords = ['password', 'secret', 'key', 'token', 'credential', 'auth']
        
        def process_value(key: str, value: Any) -> Any:
            if isinstance(value, str):
                # 检查是否为敏感字段
                is_secret = any(kw in key.lower() for kw in secret_keywords)
                if is_secret and value.startswith("${SECRET:"):
                    # 从密钥管理器获取
                    secret_key = value[9:-1]  # 提取 ${SECRET:key} 中的 key
                    secret_value = self.secret_manager.get_secret(secret_key)
                    return secret_value if secret_value else value
            elif isinstance(value, dict):
                return {k: process_value(k, v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value("", item) for item in value]
            return value
        
        return process_value("", config)
    
    def generate_diff(self, old_config: Dict, new_config: Dict) -> Dict[str, Any]:
        """生成配置差异"""
        diff = {
            "added": {},
            "removed": {},
            "modified": {},
            "unchanged": {}
        }
        
        old_keys = set(old_config.keys())
        new_keys = set(new_config.keys())
        
        # 新增的键
        for key in new_keys - old_keys:
            diff["added"][key] = new_config[key]
        
        # 删除的键
        for key in old_keys - new_keys:
            diff["removed"][key] = old_config[key]
        
        # 修改和未变的键
        for key in old_keys & new_keys:
            if old_config[key] != new_config[key]:
                diff["modified"][key] = {
                    "old": old_config[key],
                    "new": new_config[key]
                }
            else:
                diff["unchanged"][key] = new_config[key]
        
        return diff

# 使用示例
if __name__ == '__main__':
    # 设置环境变量
    os.environ['DATABASE_HOST'] = 'postgres.prod.internal'
    os.environ['DATABASE_PORT'] = '5432'
    os.environ['CACHE_HOST'] = 'redis.prod.internal'
    
    # 创建配置Schema
    config_schema = {
        "app_name": ConfigSchema("app_name", ConfigValueType.STRING, required=True),
        "version": ConfigSchema("version", ConfigValueType.STRING, required=True),
        "database": ConfigSchema("database", ConfigValueType.MAP, required=True),
        "cache": ConfigSchema("cache", ConfigValueType.MAP, required=False),
        "feature_flags": ConfigSchema("feature_flags", ConfigValueType.LIST, required=False),
    }
    
    # 创建配置DSL处理器
    processor = ConfigDSLProcessor(Environment.PRODUCTION)
    
    # 示例配置
    config = {
        "app_name": "payment-service",
        "version": "${VERSION:-1.0.0}",
        "environment": "${ENV}",
        "database": {
            "host": "${DATABASE_HOST}",
            "port": "${DATABASE_PORT}",
            "username": "${DATABASE_USER:-app_user}",
            "password": "${SECRET:database.password}",
            "pool_size": 20
        },
        "cache": {
            "host": "${CACHE_HOST}",
            "port": 6379,
            "ttl": 3600
        },
        "feature_flags": ["new_payment_flow", "enhanced_logging"],
        "metadata": {
            "deployed_at": "${TIMESTAMP}"
        }
    }
    
    # 处理配置
    result = processor.process_config(config, config_schema, {"VERSION": "2.1.0"})
    
    print("=== 配置处理结果 ===")
    print(f"验证结果: {'通过' if result['is_valid'] else '失败'}")
    if result['errors']:
        print(f"错误: {result['errors']}")
    print(f"处理后配置:\n{json.dumps(result['config'], indent=2, ensure_ascii=False)}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 配置查找时间 | 2小时 | 5分钟 | 96%缩短 |
| 环境切换时间 | 2小时 | 5分钟 | 96%缩短 |
| 配置错误发现率 | 40% | 99% | 59%提升 |
| 配置更新周期 | 3天 | 30分钟 | 98%缩短 |
| 安全合规通过率 | 65% | 100% | 35%提升 |
| 配置管理效率 | 低 | 高 | 显著提升 |

**业务价值（ROI分析）**：

1. **人力成本节约**：
   - 配置管理人员从8人减少到2人
   - 年度人力成本节约：约240万元

2. **故障损失减少**：
   - 配置错误导致的故障减少80%
   - 年度故障损失减少：约150万元

3. **合规成本降低**：
   - 安全合规审计一次性通过
   - 年度合规成本节约：约50万元

4. **投资回报率**：
   - 系统开发投入：约100万元
   - 年度总收益：约440万元
   - **ROI = 340%**

---

## 3. 案例2：数据平台查询DSL应用系统

### 3.1 业务背景

**企业背景**：
某大数据平台公司（日处理数据量100TB，服务100+企业客户）需要构建查询DSL应用系统，使用专用查询DSL构建灵活的API查询接口，支持客户端自定义查询字段，提高API的灵活性和效率。

**业务痛点**：

1. **API灵活性不足**：传统RESTful API返回固定字段，客户端经常需要多个API组合才能获取所需数据
2. **数据获取效率低**：平均需要3-5次API调用才能获取完整数据，响应时间长达5-10秒
3. **字段选择困难**：API返回大量无用字段，带宽浪费严重，移动端用户体验差
4. **版本管理困难**：每次字段变更都需要发布API新版本，版本膨胀严重（已有50+版本）
5. **查询性能不可控**：复杂查询没有限制机制，经常导致数据库负载过高，影响其他服务

**业务目标**：

1. **提高API灵活性**：支持客户端自定义查询字段，单个API满足90%的查询需求
2. **提高数据获取效率**：将平均API调用次数从3-5次减少至1次，响应时间降至1秒内
3. **支持字段选择**：只返回客户端需要的字段，带宽使用减少70%
4. **简化版本管理**：通过Schema演进替代API版本发布，版本数量减少80%
5. **控制查询性能**：实现查询复杂度分析和自动优化，数据库负载降低50%

### 3.2 技术挑战

1. **查询语言设计**：设计直观的查询DSL，支持嵌套查询、聚合、过滤、排序等复杂操作
2. **查询解析与优化**：实现查询解析器，自动分析查询复杂度并优化执行计划
3. **字段权限控制**：实现细粒度的字段级权限控制，确保数据安全
4. **性能监控与限制**：实时监控查询性能，对慢查询自动限流和告警
5. **多数据源集成**：支持关系型数据库、NoSQL、数据仓库等多种数据源的统一查询

### 3.3 解决方案

**使用专用查询DSL定义查询接口，支持客户端自定义查询字段**：

采用类似GraphQL的设计理念，但针对大数据场景优化：
- **查询语言层**：设计简洁的JSON-based查询DSL
- **解析执行层**：解析查询并生成优化的执行计划
- **数据访问层**：对接多种数据源，统一数据访问接口
- **权限控制层**：实现字段级权限控制

### 3.4 完整代码实现

```python
#!/usr/bin/env python3
"""
查询DSL应用系统 - 数据平台专用
支持自定义字段查询、聚合、过滤、排序
"""

from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime

class QueryOperator(Enum):
    """查询操作符"""
    EQ = "eq"           # 等于
    NE = "ne"           # 不等于
    GT = "gt"           # 大于
    GTE = "gte"         # 大于等于
    LT = "lt"           # 小于
    LTE = "lte"         # 小于等于
    IN = "in"           # 在列表中
    NIN = "nin"         # 不在列表中
    LIKE = "like"       # 模糊匹配
    BETWEEN = "between" # 范围
    EXISTS = "exists"   # 存在

class AggregateOperator(Enum):
    """聚合操作符"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    GROUP_BY = "groupBy"

class SortOrder(Enum):
    """排序顺序"""
    ASC = "asc"
    DESC = "desc"

@dataclass
class FieldDefinition:
    """字段定义"""
    name: str
    field_type: str
    description: str = ""
    nullable: bool = True
    default: Any = None
    permissions: List[str] = field(default_factory=list)

@dataclass
class QueryFilter:
    """查询过滤条件"""
    field: str
    operator: QueryOperator
    value: Any

@dataclass
class QuerySort:
    """查询排序"""
    field: str
    order: SortOrder = SortOrder.ASC

@dataclass
class QueryAggregate:
    """查询聚合"""
    operator: AggregateOperator
    field: str
    alias: str = ""

class QueryPermissionChecker:
    """查询权限检查器"""
    
    def __init__(self, user_roles: List[str]):
        self.user_roles = set(user_roles)
    
    def can_access_field(self, field: FieldDefinition) -> bool:
        """检查是否可以访问字段"""
        if not field.permissions:
            return True
        return bool(self.user_roles & set(field.permissions))
    
    def filter_fields(self, fields: List[FieldDefinition], 
                      requested_fields: List[str]) -> List[str]:
        """过滤有权限的字段"""
        allowed = []
        field_map = {f.name: f for f in fields}
        
        for field_name in requested_fields:
            if field_name in field_map:
                if self.can_access_field(field_map[field_name]):
                    allowed.append(field_name)
            else:
                # 嵌套字段
                base_field = field_name.split('.')[0]
                if base_field in field_map:
                    if self.can_access_field(field_map[base_field]):
                        allowed.append(field_name)
        
        return allowed

class QueryParser:
    """查询解析器"""
    
    def __init__(self, schema: Dict[str, FieldDefinition]):
        self.schema = schema
    
    def parse(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """解析查询"""
        parsed = {
            "fields": [],
            "filters": [],
            "sorts": [],
            "aggregates": [],
            "pagination": {},
            "joins": [],
            "errors": []
        }
        
        # 解析字段
        if "fields" in query:
            parsed["fields"] = self._parse_fields(query["fields"])
        
        # 解析过滤条件
        if "where" in query:
            parsed["filters"] = self._parse_filters(query["where"])
        
        # 解析排序
        if "orderBy" in query:
            parsed["sorts"] = self._parse_order_by(query["orderBy"])
        
        # 解析聚合
        if "aggregate" in query:
            parsed["aggregates"] = self._parse_aggregates(query["aggregate"])
        
        # 解析分页
        if "pagination" in query:
            parsed["pagination"] = self._parse_pagination(query["pagination"])
        
        # 解析关联
        if "include" in query:
            parsed["joins"] = self._parse_includes(query["include"])
        
        return parsed
    
    def _parse_fields(self, fields: Any) -> List[str]:
        """解析字段列表"""
        if isinstance(fields, str):
            return [f.strip() for f in fields.split(",")]
        elif isinstance(fields, list):
            return fields
        return ["*"]  # 默认返回所有字段
    
    def _parse_filters(self, where: Dict[str, Any]) -> List[QueryFilter]:
        """解析过滤条件"""
        filters = []
        
        for field, condition in where.items():
            if isinstance(condition, dict):
                # 复杂条件: {"age": {"gte": 18}}
                for op_str, value in condition.items():
                    try:
                        op = QueryOperator(op_str)
                        filters.append(QueryFilter(field, op, value))
                    except ValueError:
                        pass
            else:
                # 简单条件: {"status": "active"}
                filters.append(QueryFilter(field, QueryOperator.EQ, condition))
        
        return filters
    
    def _parse_order_by(self, order_by: Any) -> List[QuerySort]:
        """解析排序"""
        sorts = []
        
        if isinstance(order_by, str):
            # "createdAt desc, name asc"
            for part in order_by.split(","):
                parts = part.strip().split()
                field = parts[0]
                order = SortOrder.DESC if len(parts) > 1 and parts[1].lower() == "desc" else SortOrder.ASC
                sorts.append(QuerySort(field, order))
        elif isinstance(order_by, dict):
            # {"createdAt": "desc", "name": "asc"}
            for field, order_str in order_by.items():
                order = SortOrder(order_str.lower())
                sorts.append(QuerySort(field, order))
        elif isinstance(order_by, list):
            # ["createdAt", "-name"]
            for item in order_by:
                if isinstance(item, str):
                    if item.startswith("-"):
                        sorts.append(QuerySort(item[1:], SortOrder.DESC))
                    else:
                        sorts.append(QuerySort(item, SortOrder.ASC))
        
        return sorts
    
    def _parse_aggregates(self, aggregate: Dict[str, Any]) -> List[QueryAggregate]:
        """解析聚合"""
        aggregates = []
        
        for alias, config in aggregate.items():
            if isinstance(config, dict):
                op = config.get("op", "count")
                field = config.get("field", "*")
            else:
                # 简写: {"total": "count"}
                op = config
                field = "*"
            
            try:
                aggregates.append(QueryAggregate(AggregateOperator(op), field, alias))
            except ValueError:
                pass
        
        return aggregates
    
    def _parse_pagination(self, pagination: Dict[str, Any]) -> Dict[str, int]:
        """解析分页"""
        return {
            "page": pagination.get("page", 1),
            "pageSize": min(pagination.get("pageSize", 20), 1000)  # 限制最大页大小
        }
    
    def _parse_includes(self, includes: Any) -> List[Dict]:
        """解析关联查询"""
        joins = []
        
        if isinstance(includes, str):
            includes = [i.strip() for i in includes.split(",")]
        
        if isinstance(includes, list):
            for inc in includes:
                if isinstance(inc, str):
                    joins.append({"relation": inc, "fields": ["*"]})
                elif isinstance(inc, dict):
                    joins.append(inc)
        
        return joins

class QueryOptimizer:
    """查询优化器"""
    
    def analyze_complexity(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """分析查询复杂度"""
        complexity = {
            "score": 0,
            "level": "low",  # low, medium, high, critical
            "factors": []
        }
        
        score = 0
        
        # 字段数量
        field_count = len(parsed_query.get("fields", []))
        if field_count > 50:
            score += 20
            complexity["factors"].append(f"字段数量过多: {field_count}")
        elif field_count > 20:
            score += 10
        
        # 关联查询
        join_count = len(parsed_query.get("joins", []))
        if join_count > 3:
            score += 30
            complexity["factors"].append(f"关联查询过多: {join_count}")
        elif join_count > 1:
            score += 15
        
        # 聚合操作
        agg_count = len(parsed_query.get("aggregates", []))
        if agg_count > 5:
            score += 25
            complexity["factors"].append(f"聚合操作过多: {agg_count}")
        
        # 分页大小
        page_size = parsed_query.get("pagination", {}).get("pageSize", 20)
        if page_size > 500:
            score += 20
            complexity["factors"].append(f"分页大小过大: {page_size}")
        
        # 复杂过滤
        filter_count = len(parsed_query.get("filters", []))
        if filter_count > 10:
            score += 15
            complexity["factors"].append(f"过滤条件过多: {filter_count}")
        
        complexity["score"] = score
        
        if score >= 60:
            complexity["level"] = "critical"
        elif score >= 40:
            complexity["level"] = "high"
        elif score >= 20:
            complexity["level"] = "medium"
        
        return complexity
    
    def suggest_optimizations(self, parsed_query: Dict[str, Any]) -> List[str]:
        """建议优化方案"""
        suggestions = []
        
        # 字段选择优化
        if "*" in parsed_query.get("fields", []):
            suggestions.append("建议使用具体字段列表替代'*'，减少数据传输")
        
        # 关联优化
        if len(parsed_query.get("joins", [])) > 2:
            suggestions.append("关联查询较多，建议考虑数据反规范化或缓存")
        
        # 分页优化
        page_size = parsed_query.get("pagination", {}).get("pageSize", 20)
        if page_size > 100:
            suggestions.append(f"分页大小{page_size}较大，建议使用游标分页")
        
        return suggestions

class DataPlatformQueryDSL:
    """数据平台查询DSL"""
    
    def __init__(self, schema: Dict[str, FieldDefinition], user_roles: List[str] = None):
        self.schema = schema
        self.parser = QueryParser(schema)
        self.optimizer = QueryOptimizer()
        self.permission_checker = QueryPermissionChecker(user_roles or ["user"])
        self.query_history: List[Dict] = []
    
    def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """执行查询"""
        result = {
            "data": None,
            "metadata": {
                "query_time": datetime.now().isoformat(),
                "execution_time_ms": 0,
                "complexity": None,
                "warnings": []
            },
            "errors": []
        }
        
        try:
            # 解析查询
            parsed = self.parser.parse(query)
            
            # 检查权限
            requested_fields = parsed["fields"]
            allowed_fields = self.permission_checker.filter_fields(
                list(self.schema.values()), requested_fields
            )
            
            # 检查是否有无权访问的字段
            unauthorized = set(requested_fields) - set(allowed_fields)
            if unauthorized:
                result["errors"].append(f"无权访问字段: {unauthorized}")
                return result
            
            parsed["fields"] = allowed_fields
            
            # 分析复杂度
            complexity = self.optimizer.analyze_complexity(parsed)
            result["metadata"]["complexity"] = complexity
            
            if complexity["level"] == "critical":
                result["errors"].append(f"查询复杂度过高，拒绝执行: {complexity['factors']}")
                return result
            elif complexity["level"] == "high":
                result["metadata"]["warnings"].append("查询复杂度较高，可能影响性能")
            
            # 获取优化建议
            suggestions = self.optimizer.suggest_optimizations(parsed)
            result["metadata"]["suggestions"] = suggestions
            
            # 模拟查询执行
            result["data"] = self._mock_execute(parsed)
            
            # 记录查询历史
            self.query_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "complexity": complexity["score"]
            })
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    def _mock_execute(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """模拟查询执行"""
        # 这里应该是实际的数据查询逻辑
        return {
            "records": [],
            "total": 0,
            "page": parsed.get("pagination", {}).get("page", 1),
            "pageSize": parsed.get("pagination", {}).get("pageSize", 20)
        }
    
    def generate_sql(self, parsed: Dict[str, Any], table_name: str = "data") -> str:
        """生成SQL（示例）"""
        # SELECT
        fields = ", ".join(parsed["fields"]) if parsed["fields"] else "*"
        
        # FROM
        sql = f"SELECT {fields} FROM {table_name}"
        
        # WHERE
        if parsed["filters"]:
            conditions = []
            for f in parsed["filters"]:
                if f.operator == QueryOperator.EQ:
                    conditions.append(f"{f.field} = '{f.value}'")
                elif f.operator == QueryOperator.GT:
                    conditions.append(f"{f.field} > {f.value}")
                # ... 其他操作符
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        # ORDER BY
        if parsed["sorts"]:
            orders = [f"{s.field} {s.order.value}" for s in parsed["sorts"]]
            sql += " ORDER BY " + ", ".join(orders)
        
        # LIMIT
        if parsed["pagination"]:
            page = parsed["pagination"]["page"]
            page_size = parsed["pagination"]["pageSize"]
            offset = (page - 1) * page_size
            sql += f" LIMIT {page_size} OFFSET {offset}"
        
        return sql

# 使用示例
if __name__ == '__main__':
    # 定义Schema
    schema = {
        "id": FieldDefinition("id", "string", "唯一标识", permissions=["admin", "user"]),
        "name": FieldDefinition("name", "string", "名称", permissions=["admin", "user"]),
        "email": FieldDefinition("email", "string", "邮箱", permissions=["admin"]),
        "age": FieldDefinition("age", "integer", "年龄", permissions=["admin", "user"]),
        "salary": FieldDefinition("salary", "decimal", "薪资", permissions=["admin"]),
        "department": FieldDefinition("department", "object", "部门", permissions=["admin", "user"]),
        "createdAt": FieldDefinition("createdAt", "datetime", "创建时间", permissions=["admin", "user"]),
    }
    
    # 创建查询DSL
    query_dsl = DataPlatformQueryDSL(schema, user_roles=["user"])
    
    # 示例查询1: 简单查询
    query1 = {
        "fields": ["id", "name", "age"],
        "where": {"age": {"gte": 18}},
        "orderBy": "createdAt desc",
        "pagination": {"page": 1, "pageSize": 10}
    }
    
    print("=== 查询1: 简单查询 ===")
    result1 = query_dsl.execute(query1)
    print(f"复杂度: {result1['metadata']['complexity']}")
    print(f"错误: {result1['errors']}")
    
    # 示例查询2: 复杂查询（包含无权访问字段）
    query2 = {
        "fields": ["id", "name", "email", "salary"],  # email和salary需要admin权限
        "where": {
            "age": {"gte": 25, "lte": 40},
            "department.name": "Engineering"
        },
        "include": ["department", "manager"],
        "aggregate": {
            "avg_salary": {"op": "avg", "field": "salary"}
        },
        "pagination": {"page": 1, "pageSize": 100}
    }
    
    print("\n=== 查询2: 复杂查询 ===")
    result2 = query_dsl.execute(query2)
    print(f"错误: {result2['errors']}")
    if not result2['errors']:
        print(f"复杂度: {result2['metadata']['complexity']}")
        print(f"建议: {result2['metadata'].get('suggestions', [])}")
```

### 3.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 平均API调用次数 | 3-5次 | 1次 | 80%减少 |
| API响应时间 | 5-10秒 | 800毫秒 | 92%缩短 |
| 带宽使用 | 基准 | 减少70% | 70%降低 |
| API版本数量 | 50+ | 8 | 84%减少 |
| 数据库负载 | 基准 | 降低50% | 50%降低 |
| 开发效率 | 低 | 高 | 显著提升 |

**业务价值（ROI分析）**：

1. **基础设施成本节约**：
   - 带宽成本减少70%
   - 服务器资源减少40%
   - 年度成本节约：约300万元

2. **开发效率提升**：
   - 新功能开发时间减少50%
   - 维护成本降低60%
   - 年度开发成本节约：约200万元

3. **用户体验提升**：
   - 客户满意度提升20%
   - 客户流失率降低15%
   - 年度收入增加：约500万元

4. **投资回报率**：
   - 系统开发投入：约150万元
   - 年度总收益：约1000万元
   - **ROI = 567%**

---

## 4. 案例3：智能制造转换DSL应用系统

### 4.1 业务背景

**企业背景**：
某智能制造企业（拥有10+智能工厂，日生产产品100万件）需要构建转换DSL应用系统，实现生产数据在不同系统间的自动转换，支持MES、ERP、WMS系统的数据互通。

**业务痛点**：

1. **数据格式不一致**：不同系统使用不同的数据格式和编码，人工转换错误率高达20%
2. **转换逻辑分散**：转换逻辑散落在各处，难以维护和复用，修改一个转换规则需要修改10+处代码
3. **实时性不足**：数据同步延迟长达1小时，影响生产决策的及时性
4. **转换质量难以保证**：缺乏统一的转换验证机制，数据质量问题频发
5. **扩展性差**：新增系统对接需要2-3周开发周期，无法满足快速迭代的业务需求

**业务目标**：

1. **统一数据格式**：建立统一的转换DSL，数据转换错误率降至1%以下
2. **集中转换逻辑**：所有转换规则集中管理，维护成本降低80%
3. **提升实时性**：数据同步延迟从1小时降低至30秒内
4. **保证转换质量**：实现100%转换验证，数据质量提升至99.9%
5. **提高扩展性**：新系统对接时间从2-3周缩短至2-3天

### 4.2 技术挑战

1. **多协议支持**：支持多种工业协议（OPC UA、Modbus、MQTT等）的数据接入
2. **复杂转换逻辑**：支持条件转换、聚合、拆分、关联等复杂操作
3. **高吞吐量处理**：支持每秒10万+条数据的实时转换
4. **容错与恢复**：转换失败时的容错处理和自动恢复机制
5. **可视化编排**：提供可视化的转换规则编排界面

### 4.3 解决方案

**使用专用转换DSL定义数据转换规则，支持可视化编排**：

- 设计声明式转换DSL，支持复杂转换逻辑
- 实现高性能转换引擎
- 提供转换规则的可视化编排工具

### 4.4 完整代码实现

```python
#!/usr/bin/env python3
"""
智能制造转换DSL应用系统
支持生产数据在不同系统间的自动转换
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime
import hashlib

class TransformOperator(Enum):
    """转换操作符"""
    MAP = "map"                    # 字段映射
    FILTER = "filter"              # 过滤
    AGGREGATE = "aggregate"        # 聚合
    SPLIT = "split"                # 拆分
    JOIN = "join"                  # 关联
    SCRIPT = "script"              # 自定义脚本
    CONDITIONAL = "conditional"    # 条件转换
    LOOKUP = "lookup"              # 查表
    ENRICH = "enrich"              # 数据增强

class DataType(Enum):
    """数据类型"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    OBJECT = "object"
    ARRAY = "array"

@dataclass
class FieldMapping:
    """字段映射"""
    source: str
    target: str
    transform: Optional[str] = None
    data_type: DataType = DataType.STRING
    default_value: Any = None

@dataclass
class TransformRule:
    """转换规则"""
    name: str
    operator: TransformOperator
    config: Dict[str, Any]
    description: str = ""
    enabled: bool = True

class ExpressionEvaluator:
    """表达式求值器"""
    
    def __init__(self):
        self.builtins = {
            "now": lambda: datetime.now().isoformat(),
            "today": lambda: datetime.now().strftime("%Y-%m-%d"),
            "uuid": lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:16],
            "upper": lambda s: str(s).upper(),
            "lower": lambda s: str(s).lower(),
            "trim": lambda s: str(s).strip(),
            "substr": lambda s, start, end: str(s)[start:end],
            "concat": lambda *args: "".join(str(a) for a in args),
            "add": lambda a, b: float(a) + float(b),
            "sub": lambda a, b: float(a) - float(b),
            "mul": lambda a, b: float(a) * float(b),
            "div": lambda a, b: float(a) / float(b) if float(b) != 0 else 0,
        }
    
    def evaluate(self, expression: str, context: Dict[str, Any]) -> Any:
        """求值表达式"""
        # 简单实现: 替换变量引用
        def replace_var(match):
            var_path = match.group(1)
            return str(self._get_value_by_path(context, var_path, ""))
        
        # 替换 ${var} 格式
        result = re.sub(r'\$\{([^}]+)\}', replace_var, expression)
        
        # 处理内置函数调用
        if result.startswith("${") and result.endswith("}"):
            func_expr = result[2:-1]
            return self._evaluate_function(func_expr, context)
        
        return result
    
    def _get_value_by_path(self, obj: Any, path: str, default: Any = None) -> Any:
        """通过路径获取值"""
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, default)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if 0 <= idx < len(current) else default
            else:
                return default
            
            if current is None:
                return default
        
        return current
    
    def _evaluate_function(self, expr: str, context: Dict[str, Any]) -> Any:
        """求值函数调用"""
        # 解析函数调用: func(arg1, arg2, ...)
        match = re.match(r'(\w+)\s*\((.*)\)', expr)
        if not match:
            return expr
        
        func_name = match.group(1)
        args_str = match.group(2)
        
        # 解析参数
        args = []
        if args_str.strip():
            # 简单解析，实际应用中需要更健壮的解析
            for arg in args_str.split(","):
                arg = arg.strip()
                if arg.startswith("'") and arg.endswith("'"):
                    args.append(arg[1:-1])
                elif arg.startswith('"') and arg.endswith('"'):
                    args.append(arg[1:-1])
                elif arg in self.builtins:
                    args.append(self.builtins[arg]())
                else:
                    # 从context获取
                    args.append(self._get_value_by_path(context, arg, arg))
        
        if func_name in self.builtins:
            return self.builtins[func_name](*args)
        
        return expr

class TransformEngine:
    """转换引擎"""
    
    def __init__(self):
        self.evaluator = ExpressionEvaluator()
        self.rules: List[TransformRule] = []
        self.lookup_tables: Dict[str, Dict] = {}
    
    def add_rule(self, rule: TransformRule):
        """添加转换规则"""
        self.rules.append(rule)
    
    def register_lookup_table(self, name: str, data: Dict):
        """注册查表数据"""
        self.lookup_tables[name] = data
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行转换"""
        result = {"input": data, "output": {}, "logs": [], "errors": []}
        
        current_data = data.copy()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                if rule.operator == TransformOperator.MAP:
                    current_data = self._apply_map(current_data, rule.config)
                elif rule.operator == TransformOperator.FILTER:
                    if not self._apply_filter(current_data, rule.config):
                        result["logs"].append(f"数据被规则 '{rule.name}' 过滤")
                        return result
                elif rule.operator == TransformOperator.AGGREGATE:
                    current_data = self._apply_aggregate(current_data, rule.config)
                elif rule.operator == TransformOperator.CONDITIONAL:
                    current_data = self._apply_conditional(current_data, rule.config)
                elif rule.operator == TransformOperator.LOOKUP:
                    current_data = self._apply_lookup(current_data, rule.config)
                elif rule.operator == TransformOperator.SCRIPT:
                    current_data = self._apply_script(current_data, rule.config)
                
                result["logs"].append(f"规则 '{rule.name}' 执行成功")
                
            except Exception as e:
                result["errors"].append(f"规则 '{rule.name}' 执行失败: {str(e)}")
                break
        
        result["output"] = current_data
        return result
    
    def _apply_map(self, data: Dict, config: Dict) -> Dict:
        """应用字段映射"""
        mappings = config.get("mappings", [])
        result = {}
        
        for mapping in mappings:
            source = mapping.get("source")
            target = mapping.get("target")
            transform = mapping.get("transform")
            default = mapping.get("default")
            
            # 获取源值
            if isinstance(source, str):
                value = self.evaluator._get_value_by_path(data, source, default)
            else:
                value = source
            
            # 应用转换
            if transform and value is not None:
                value = self.evaluator.evaluate(transform, {**data, "_value": value})
            
            # 设置目标值
            self._set_value_by_path(result, target, value)
        
        return result
    
    def _apply_filter(self, data: Dict, config: Dict) -> bool:
        """应用过滤条件"""
        condition = config.get("condition", "")
        return bool(self.evaluator.evaluate(condition, data))
    
    def _apply_aggregate(self, data: Dict, config: Dict) -> Dict:
        """应用聚合"""
        group_by = config.get("groupBy", [])
        aggregations = config.get("aggregations", [])
        
        # 这里简化处理，实际应该支持列表数据的分组聚合
        result = data.copy()
        
        for agg in aggregations:
            op = agg.get("op")
            field = agg.get("field")
            alias = agg.get("alias", f"{op}_{field}")
            
            # 简化的聚合逻辑
            if op == "count":
                result[alias] = 1
            elif op == "sum":
                result[alias] = self.evaluator._get_value_by_path(data, field, 0)
        
        return result
    
    def _apply_conditional(self, data: Dict, config: Dict) -> Dict:
        """应用条件转换"""
        conditions = config.get("conditions", [])
        
        for condition in conditions:
            if self._apply_filter(data, {"condition": condition.get("if", "true")}):
                return self._apply_map(data, {"mappings": condition.get("then", [])})
        
        # 默认情况
        default = config.get("default", [])
        return self._apply_map(data, {"mappings": default})
    
    def _apply_lookup(self, data: Dict, config: Dict) -> Dict:
        """应用查表"""
        table_name = config.get("table")
        source_field = config.get("sourceField")
        target_field = config.get("targetField")
        
        table = self.lookup_tables.get(table_name, {})
        key = self.evaluator._get_value_by_path(data, source_field)
        value = table.get(key)
        
        result = data.copy()
        self._set_value_by_path(result, target_field, value)
        
        return result
    
    def _apply_script(self, data: Dict, config: Dict) -> Dict:
        """应用自定义脚本（简化版）"""
        # 实际应用中应该使用安全的脚本引擎
        script = config.get("code", "")
        result = data.copy()
        
        # 示例: 简单的字段计算
        if "multiply" in script:
            # ${field1} * ${field2}
            match = re.search(r'\$\{(\w+)\}\s*\*\s*\$\{(\w+)\}', script)
            if match:
                f1, f2 = match.groups()
                v1 = float(self.evaluator._get_value_by_path(data, f1, 0))
                v2 = float(self.evaluator._get_value_by_path(data, f2, 0))
                result["calculated"] = v1 * v2
        
        return result
    
    def _set_value_by_path(self, obj: Dict, path: str, value: Any):
        """通过路径设置值"""
        parts = path.split(".")
        current = obj
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value

class ManufacturingTransformDSL:
    """智能制造转换DSL"""
    
    def __init__(self):
        self.engine = TransformEngine()
        self.rule_definitions: List[Dict] = []
    
    def define_mapping(self, source_system: str, target_system: str, 
                       mappings: List[Dict]) -> TransformRule:
        """定义系统间映射"""
        rule = TransformRule(
            name=f"{source_system}_to_{target_system}",
            operator=TransformOperator.MAP,
            config={"mappings": mappings},
            description=f"从{source_system}到{target_system}的数据映射"
        )
        self.engine.add_rule(rule)
        self.rule_definitions.append({
            "type": "mapping",
            "source": source_system,
            "target": target_system,
            "rule": rule
        })
        return rule
    
    def define_filter(self, name: str, condition: str) -> TransformRule:
        """定义过滤规则"""
        rule = TransformRule(
            name=name,
            operator=TransformOperator.FILTER,
            config={"condition": condition}
        )
        self.engine.add_rule(rule)
        return rule
    
    def register_code_mapping(self, code_type: str, mappings: Dict[str, str]):
        """注册代码映射表"""
        self.engine.register_lookup_table(code_type, mappings)
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行转换"""
        return self.engine.transform(data)
    
    def validate(self, sample_data: List[Dict]) -> Dict[str, Any]:
        """验证转换规则"""
        results = []
        errors = []
        
        for data in sample_data:
            result = self.transform(data)
            results.append(result)
            errors.extend(result.get("errors", []))
        
        return {
            "total_samples": len(sample_data),
            "successful": len([r for r in results if not r.get("errors")]),
            "failed": len([r for r in results if r.get("errors")]),
            "errors": errors,
            "sample_results": results[:3]  # 只返回前3个结果作为示例
        }
    
    def export_rules(self) -> str:
        """导出规则为JSON"""
        return json.dumps({
            "rules": [
                {
                    "name": r.name,
                    "operator": r.operator.value,
                    "config": r.config,
                    "description": r.description,
                    "enabled": r.enabled
                }
                for r in self.engine.rules
            ]
        }, indent=2, ensure_ascii=False)

# 使用示例
if __name__ == '__main__':
    # 创建转换DSL
    dsl = ManufacturingTransformDSL()
    
    # 注册代码映射表
    dsl.register_code_mapping("product_type", {
        "P001": "电子产品",
        "P002": "机械零件",
        "P003": "化工原料"
    })
    
    dsl.register_code_mapping("status_code", {
        "0": "待生产",
        "1": "生产中",
        "2": "已完成",
        "3": "异常"
    })
    
    # 定义MES到ERP的数据映射
    dsl.define_mapping(
        source_system="MES",
        target_system="ERP",
        mappings=[
            {"source": "work_order_id", "target": "order_no"},
            {"source": "product_code", "target": "product_id"},
            {"source": "product_name", "target": "product_name"},
            {"source": "planned_qty", "target": "quantity", "data_type": "integer"},
            {"source": "actual_qty", "target": "completed_qty", "data_type": "integer"},
            {"source": "start_time", "target": "production_start", "data_type": "datetime"},
            {"source": "end_time", "target": "production_end", "data_type": "datetime"},
            {"source": "operator_id", "target": "operator"},
            {"source": "status", "target": "order_status", "transform": "${status_code[status]}"},
            {"source": "now", "target": "sync_timestamp", "transform": "${now()}"}
        ]
    )
    
    # 定义过滤规则：只同步已完成或异常状态的订单
    dsl.define_filter("status_filter", "${status} == '2' || ${status} == '3'")
    
    # 示例数据
    mes_data = {
        "work_order_id": "WO2024001",
        "product_code": "P001",
        "product_name": "智能控制器",
        "planned_qty": 1000,
        "actual_qty": 980,
        "start_time": "2024-01-15T08:00:00",
        "end_time": "2024-01-15T16:30:00",
        "operator_id": "OP001",
        "status": "2"
    }
    
    print("=== 智能制造转换DSL示例 ===")
    print(f"\n输入数据 (MES): {json.dumps(mes_data, indent=2, ensure_ascii=False)}")
    
    # 执行转换
    result = dsl.transform(mes_data)
    print(f"\n转换结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 导出规则
    print(f"\n导出规则:\n{dsl.export_rules()}")
```

### 4.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 数据转换错误率 | 20% | 0.5% | 98%降低 |
| 规则维护成本 | 高 | 低 | 80%降低 |
| 数据同步延迟 | 1小时 | 15秒 | 99.6%缩短 |
| 数据质量 | 90% | 99.9% | 10%提升 |
| 新系统对接时间 | 2-3周 | 2-3天 | 85%缩短 |
| 转换吞吐量 | 1K/s | 100K/s | 100倍提升 |

**业务价值（ROI分析）**：

1. **生产效率提升**：
   - 数据实时同步，生产决策响应时间缩短95%
   - 生产异常发现时间从2小时缩短至5分钟
   - 年度生产效率提升价值：约800万元

2. **质量成本降低**：
   - 数据质量问题减少95%
   - 返工和废品减少，年度节约：约300万元

3. **IT成本节约**：
   - 系统维护人力减少60%
   - 新系统集成成本降低85%
   - 年度IT成本节约：约200万元

4. **投资回报率**：
   - 系统开发投入：约120万元
   - 年度总收益：约1300万元
   - **ROI = 983%**

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 分类体系
- `03_Standards.md` - 典型示例
- `04_Transformation.md` - 最佳实践

**创建时间**：2025-01-21
**最后更新**：2025-02-15
