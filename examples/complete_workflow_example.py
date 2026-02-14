#!/usr/bin/env python3
"""
DSL Schema 完整工作流示例

展示从Schema定义到代码生成的完整流程
"""

import json
from typing import Dict, Any


def example_1_basic_schema_creation():
    """示例1: 创建基本Schema"""
    print("=" * 60)
    print("示例1: 创建基本Schema")
    print("=" * 60)
    
    # 定义一个简单的用户Schema
    user_schema = {
        "schema_name": "UserSchema",
        "version": "1.0.0",
        "description": "用户实体Schema定义",
        "fields": [
            {
                "name": "id",
                "type": "Integer",
                "constraints": {
                    "required": True,
                    "primary_key": True
                }
            },
            {
                "name": "username",
                "type": "String",
                "constraints": {
                    "required": True,
                    "minLength": 3,
                    "maxLength": 50,
                    "pattern": "^[a-zA-Z0-9_]+$"
                }
            },
            {
                "name": "email",
                "type": "String",
                "constraints": {
                    "required": True,
                    "format": "email"
                }
            },
            {
                "name": "age",
                "type": "Integer",
                "constraints": {
                    "min": 0,
                    "max": 150
                }
            }
        ]
    }
    
    print(f"创建Schema: {user_schema['schema_name']}")
    print(f"字段数量: {len(user_schema['fields'])}")
    print(f"版本: {user_schema['version']}")
    print("\nSchema定义:")
    print(json.dumps(user_schema, indent=2, ensure_ascii=False))
    
    return user_schema


def example_2_schema_transformation(schema: Dict[str, Any]):
    """示例2: Schema转换"""
    print("\n" + "=" * 60)
    print("示例2: Schema转换为JSON Schema")
    print("=" * 60)
    
    # 转换为JSON Schema格式
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": schema["schema_name"],
        "description": schema["description"],
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for field in schema["fields"]:
        field_name = field["name"]
        field_type = field["type"]
        constraints = field.get("constraints", {})
        
        # 类型映射
        type_mapping = {
            "String": "string",
            "Integer": "integer",
            "Float": "number",
            "Boolean": "boolean",
            "Date": "string"
        }
        
        json_schema["properties"][field_name] = {
            "type": type_mapping.get(field_type, "string")
        }
        
        # 添加约束
        if "minLength" in constraints:
            json_schema["properties"][field_name]["minLength"] = constraints["minLength"]
        if "maxLength" in constraints:
            json_schema["properties"][field_name]["maxLength"] = constraints["maxLength"]
        if "pattern" in constraints:
            json_schema["properties"][field_name]["pattern"] = constraints["pattern"]
        if "min" in constraints:
            json_schema["properties"][field_name]["minimum"] = constraints["min"]
        if "max" in constraints:
            json_schema["properties"][field_name]["maximum"] = constraints["max"]
        if "format" in constraints:
            json_schema["properties"][field_name]["format"] = constraints["format"]
        
        # 必填字段
        if constraints.get("required"):
            json_schema["required"].append(field_name)
    
    print("转换后的JSON Schema:")
    print(json.dumps(json_schema, indent=2, ensure_ascii=False))
    
    return json_schema


def example_3_code_generation(schema: Dict[str, Any]):
    """示例3: 代码生成"""
    print("\n" + "=" * 60)
    print("示例3: 生成Python代码")
    print("=" * 60)
    
    # 生成Python类
    class_name = schema["schema_name"]
    
    code_lines = [
        f"class {class_name}:",
        f'    \"\"\"',
        f'    {schema["description"]}',
        f'    版本: {schema["version"]}',
        f'    \"\"\"',
        "",
        "    def __init__(self, **kwargs):"
    ]
    
    for field in schema["fields"]:
        field_name = field["name"]
        constraints = field.get("constraints", {})
        default = "None"
        
        if field["type"] == "Integer":
            default = "0"
        elif field["type"] == "String":
            default = '""'
        elif field["type"] == "Boolean":
            default = "False"
        
        code_lines.append(f"        self.{field_name} = kwargs.get('{field_name}', {default})")
    
    code_lines.extend([
        "",
        "    def validate(self) -> bool:",
        '        """验证数据有效性"""',
        "        errors = []",
    ])
    
    for field in schema["fields"]:
        field_name = field["name"]
        constraints = field.get("constraints", {})
        
        if constraints.get("required"):
            code_lines.append(f"        if self.{field_name} is None:")
            code_lines.append(f'            errors.append("{field_name} is required")')
        
        if "minLength" in constraints:
            code_lines.append(f"        if self.{field_name} and len(self.{field_name}) < {constraints['minLength']}:")
            code_lines.append(f'            errors.append("{field_name} too short")')
        
        if "maxLength" in constraints:
            code_lines.append(f"        if self.{field_name} and len(self.{field_name}) > {constraints['maxLength']}:")
            code_lines.append(f'            errors.append("{field_name} too long")')
    
    code_lines.extend([
        "",
        "        if errors:",
        "            raise ValueError(f\"Validation failed: {errors}\")",
        "        return True",
        "",
        "    def to_dict(self) -> dict:",
        '        """转换为字典"""',
        "        return {"
    ])
    
    for i, field in enumerate(schema["fields"]):
        field_name = field["name"]
        comma = "," if i < len(schema["fields"]) - 1 else ""
        code_lines.append(f"            '{field_name}': self.{field_name}{comma}")
    
    code_lines.append("        }")
    
    generated_code = "\n".join(code_lines)
    print("生成的Python代码:")
    print(generated_code)
    
    return generated_code


def example_4_schema_validation():
    """示例4: Schema验证"""
    print("\n" + "=" * 60)
    print("示例4: 使用生成的类")
    print("=" * 60)
    
    # 动态执行生成的代码
    code = '''
class UserSchema:
    """用户实体Schema定义"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0)
        self.username = kwargs.get('username', "")
        self.email = kwargs.get('email', "")
        self.age = kwargs.get('age', 0)
    
    def validate(self) -> bool:
        """验证数据有效性"""
        errors = []
        if self.id is None or self.id == 0:
            errors.append("id is required")
        if not self.username:
            errors.append("username is required")
        if len(self.username) < 3:
            errors.append("username too short")
        if not self.email:
            errors.append("email is required")
        if errors:
            raise ValueError(f"Validation failed: {errors}")
        return True
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age
        }
    
    def __repr__(self):
        return f"UserSchema(id={self.id}, username='{self.username}', email='{self.email}')"
'''
    
    exec(code, globals())
    
    # 创建实例
    user1 = UserSchema(id=1, username="john_doe", email="john@example.com", age=30)
    print(f"创建用户: {user1}")
    
    # 验证
    try:
        user1.validate()
        print("✅ 验证通过")
    except ValueError as e:
        print(f"❌ 验证失败: {e}")
    
    # 转换为字典
    user_dict = user1.to_dict()
    print(f"字典格式: {user_dict}")
    
    # 验证失败的例子
    print("\n测试验证失败场景:")
    user2 = UserSchema(id=0, username="ab", email="")
    try:
        user2.validate()
        print("✅ 验证通过")
    except ValueError as e:
        print(f"❌ 验证失败 (预期): {e}")


def example_5_schema_evolution():
    """示例5: Schema演进"""
    print("\n" + "=" * 60)
    print("示例5: Schema版本演进")
    print("=" * 60)
    
    # v1.0 Schema
    schema_v1 = {
        "version": "1.0.0",
        "fields": ["id", "username", "email"]
    }
    
    # v2.0 Schema (添加字段)
    schema_v2 = {
        "version": "2.0.0",
        "fields": ["id", "username", "email", "phone", "address"],
        "migrations": [
            {
                "from": "1.0.0",
                "to": "2.0.0",
                "changes": [
                    {"type": "add", "field": "phone", "default": None},
                    {"type": "add", "field": "address", "default": None}
                ]
            }
        ]
    }
    
    print(f"v1 Schema字段: {schema_v1['fields']}")
    print(f"v2 Schema字段: {schema_v2['fields']}")
    print("\n迁移步骤:")
    for migration in schema_v2["migrations"]:
        print(f"  {migration['from']} -> {migration['to']}")
        for change in migration["changes"]:
            print(f"    + 添加字段: {change['field']}")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "DSL Schema 完整工作流示例".center(56) + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    # 运行示例
    schema = example_1_basic_schema_creation()
    json_schema = example_2_schema_transformation(schema)
    python_code = example_3_code_generation(schema)
    example_4_schema_validation()
    example_5_schema_evolution()
    
    print("\n" + "=" * 60)
    print("所有示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
