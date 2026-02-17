# Schema设计最佳实践指南

## 概述

本文档提供DSL Schema设计的最佳实践，帮助设计人员创建高质量、可维护、可扩展的Schema。

---

## 设计原则

### 1. 清晰性原则 (Clarity)

**原则**: Schema应该清晰易懂，无需额外文档即可理解。

**实践**:
- 使用有意义的命名
- 添加描述性注释
- 保持结构扁平（避免过度嵌套）

```json
// ❌ 不好的设计
{
  "f1": "John",
  "f2": 30
}

// ✅ 好的设计
{
  "firstName": "John",
  "age": 30,
  "description": "用户基本信息"
}
```

### 2. 一致性原则 (Consistency)

**原则**: 在整个Schema中保持命名约定、数据类型和结构的一致性。

**实践**:
- 统一命名风格（camelCase, snake_case, PascalCase）
- 统一日期时间格式
- 统一空值处理方式

```json
// ❌ 不一致
{
  "userName": "john",
  "email_address": "john@example.com",
  "PhoneNumber": "1234567890"
}

// ✅ 一致 (camelCase)
{
  "userName": "john",
  "emailAddress": "john@example.com",
  "phoneNumber": "1234567890"
}
```

### 3. 可扩展性原则 (Extensibility)

**原则**: Schema应该易于扩展，不影响现有数据。

**实践**:
- 使用额外的属性（additionalProperties）
- 预留扩展字段
- 使用版本控制

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "metadata": {
      "type": "object",
      "description": "扩展元数据字段"
    }
  },
  "additionalProperties": true
}
```

### 4. 健壮性原则 (Robustness)

**原则**: Schema应该能够处理异常数据，不轻易崩溃。

**实践**:
- 使用合理的默认值
- 设置适当的约束（min, max, pattern）
- 处理可选字段

```json
{
  "type": "object",
  "properties": {
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150,
      "default": 0
    },
    "email": {
      "type": "string",
      "format": "email",
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    }
  }
}
```

---

## 命名规范

### 通用规则

| 类型 | 规范 | 示例 |
|------|------|------|
| 属性名 | camelCase | `firstName`, `emailAddress` |
| 类型名 | PascalCase | `User`, `OrderItem` |
| 常量/枚举 | UPPER_SNAKE_CASE | `STATUS_ACTIVE`, `TYPE_PREMIUM` |
| 文件名 | kebab-case | `user-schema.json` |
| 数据库字段 | snake_case | `created_at`, `user_id` |

### 语义命名

**推荐**:
```yaml
# 使用动作性动词
isActive: boolean      # 状态标识
hasPermission: boolean # 权限标识
shouldNotify: boolean  # 行为标识

# 使用具体名词
emailAddress: string   # 具体说明是地址
phoneNumber: string    # 具体说明是号码
createdAt: datetime    # 具体说明是时间点
```

**避免**:
```yaml
# 避免模糊命名
status: string         # 太泛
data: object          # 太泛
value: any            # 太泛

# 避免缩写
fn: string            # 不清晰
addr: string          # 不清晰
cnt: integer          # 不清晰
```

---

## 类型设计

### 基础类型选择

| 场景 | 推荐类型 | 说明 |
|------|----------|------|
| ID标识 | string | 避免整数溢出问题 |
| 金额 | string (decimal) | 避免浮点精度问题 |
| 日期 | string (date/date-time) | ISO 8601格式 |
| 枚举 | string + enum | 明确取值范围 |
| 大文本 | string | 设置maxLength |
| 二进制 | string (base64) | 明确编码方式 |

### 复杂类型设计

**对象设计**:
```json
{
  "type": "object",
  "properties": {
    "address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"},
        "country": {
          "type": "string",
          "enum": ["CN", "US", "JP", "..."]
        }
      },
      "required": ["street", "city", "country"]
    }
  }
}
```

**数组设计**:
```json
{
  "type": "object",
  "properties": {
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 50
      },
      "maxItems": 20,
      "uniqueItems": true
    }
  }
}
```

---

## 验证规则

### 常用约束

```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 20,
      "pattern": "^[a-zA-Z0-9_]+$"
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "website": {
      "type": "string",
      "format": "uri"
    },
    "score": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "multipleOf": 0.5
    }
  },
  "required": ["username", "email"]
}
```

### 自定义验证

```python
from jsonschema import validate, Draft7Validator, FormatChecker

# 自定义格式检查器
custom_format_checker = FormatChecker()

@custom_format_checker.checks('phone', raises=ValueError)
def check_phone(instance):
    """验证手机号格式"""
    import re
    if not re.match(r'^1[3-9]\d{9}$', instance):
        raise ValueError(f"Invalid phone number: {instance}")
    return True

# 使用自定义验证
schema = {
    "type": "object",
    "properties": {
        "phone": {
            "type": "string",
            "format": "phone"
        }
    }
}

validator = Draft7Validator(schema, format_checker=custom_format_checker)
```

---

## 版本管理

### 版本策略

**语义化版本 (SemVer)**:
```
MAJOR.MINOR.PATCH
```

- **MAJOR**: 不兼容的Schema变更
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的问题修复

### 版本标识

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://api.example.com/schemas/user/v2.1.0.json",
  "title": "User Schema",
  "version": "2.1.0",
  "description": "用户数据模型 v2.1.0"
}
```

### 兼容性处理

```python
class SchemaVersionManager:
    """Schema版本管理器"""
    
    def __init__(self):
        self.schemas = {}
        self.migrations = {}
    
    def register_schema(self, name: str, version: str, schema: dict):
        """注册Schema"""
        if name not in self.schemas:
            self.schemas[name] = {}
        self.schemas[name][version] = schema
    
    def register_migration(self, name: str, from_ver: str, to_ver: str, migrate_fn):
        """注册迁移函数"""
        key = f"{name}:{from_ver}->{to_ver}"
        self.migrations[key] = migrate_fn
    
    def migrate(self, data: dict, name: str, from_ver: str, to_ver: str) -> dict:
        """迁移数据"""
        key = f"{name}:{from_ver}->{to_ver}"
        
        if key in self.migrations:
            return self.migrations[key](data)
        
        # 尝试逐步迁移
        versions = self._get_version_path(name, from_ver, to_ver)
        for i in range(len(versions) - 1):
            step_key = f"{name}:{versions[i]}->{versions[i+1]}"
            if step_key in self.migrations:
                data = self.migrations[step_key](data)
        
        return data
```

---

## 安全考虑

### 输入验证

```python
import bleach
from html import escape

def sanitize_string(value: str) -> str:
    """清理字符串输入"""
    # 去除HTML标签
    cleaned = bleach.clean(value, tags=[], strip=True)
    # HTML实体编码
    return escape(cleaned)

# 在验证时使用
def validate_and_sanitize(data: dict, schema: dict) -> dict:
    """验证并清理数据"""
    # 首先验证Schema
    validate(instance=data, schema=schema)
    
    # 清理字符串字段
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = sanitize_string(value)
    
    return data
```

### 敏感数据处理

```json
{
  "type": "object",
  "properties": {
    "password": {
      "type": "string",
      "minLength": 8,
      "format": "password",
      "writeOnly": true
    },
    "ssn": {
      "type": "string",
      "pattern": "^\\d{3}-\\d{2}-\\d{4}$",
      "description": "敏感数据，需要加密存储"
    }
  }
}
```

---

## 性能优化

### Schema优化技巧

1. **减少嵌套层级**: 尽量保持层级在3层以内
2. **避免大数组**: 限制数组最大长度
3. **使用合适的数据类型**: 避免使用any类型
4. **缓存验证结果**: 对重复数据进行缓存

```python
from functools import lru_cache
import jsonschema

class OptimizedValidator:
    """优化的Schema验证器"""
    
    def __init__(self, schema: dict):
        self.schema = schema
        self.validator = jsonschema.Draft7Validator(schema)
    
    @lru_cache(maxsize=1000)
    def validate(self, data_hash: int) -> bool:
        """验证数据（使用缓存）"""
        # 实际实现需要处理hash冲突
        pass
```

---

## 文档生成

### 自动生成文档

```python
def generate_schema_documentation(schema: dict) -> str:
    """从Schema生成Markdown文档"""
    doc = []
    
    # 标题
    doc.append(f"# {schema.get('title', 'Schema Documentation')}\n")
    
    # 描述
    if 'description' in schema:
        doc.append(f"{schema['description']}\n")
    
    # 版本
    if 'version' in schema:
        doc.append(f"**Version**: {schema['version']}\n")
    
    # 属性文档
    doc.append("## Properties\n")
    
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    
    for prop_name, prop_schema in properties.items():
        is_required = prop_name in required
        doc.append(f"### {prop_name}{' (required)' if is_required else ''}\n")
        
        if 'description' in prop_schema:
            doc.append(f"{prop_schema['description']}\n")
        
        doc.append(f"- **Type**: {prop_schema.get('type', 'any')}")
        
        if 'enum' in prop_schema:
            doc.append(f"- **Enum**: {', '.join(map(str, prop_schema['enum']))}")
        
        if 'minimum' in prop_schema or 'maximum' in prop_schema:
            constraints = []
            if 'minimum' in prop_schema:
                constraints.append(f"min: {prop_schema['minimum']}")
            if 'maximum' in prop_schema:
                constraints.append(f"max: {prop_schema['maximum']}")
            doc.append(f"- **Constraints**: {', '.join(constraints)}")
        
        if 'default' in prop_schema:
            doc.append(f"- **Default**: {prop_schema['default']}")
        
        doc.append("")
    
    return '\n'.join(doc)
```

---

## 检查清单

### Schema设计检查

- [ ] 命名是否符合规范
- [ ] 是否添加了描述信息
- [ ] 是否设置了适当的约束
- [ ] 是否处理了可选字段
- [ ] 是否考虑了扩展性
- [ ] 是否添加了版本信息
- [ ] 是否处理了敏感数据
- [ ] 是否进行了性能优化

### 验证检查

- [ ] Schema自身是否有效
- [ ] 示例数据是否通过验证
- [ ] 边界条件是否处理
- [ ] 错误信息是否清晰
- [ ] 是否测试了兼容性

---

**创建时间**: 2026-02-17  
**维护者**: DSL Schema研究团队
