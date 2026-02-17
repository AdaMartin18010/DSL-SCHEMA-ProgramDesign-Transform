#!/usr/bin/env python3
"""
Documentation Generator
=======================

文档生成工具，提供：
- 自动生成API文档
- Schema文档生成
- Markdown/HTML导出
- 交互式文档
- 变更日志

Version: 2.3.0
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class DocSection:
    """文档章节"""
    title: str
    content: str
    level: int = 1
    subsections: List['DocSection'] = field(default_factory=list)


@dataclass
class APIDoc:
    """API文档"""
    endpoint: str
    method: str
    summary: str
    description: str
    parameters: List[Dict]
    request_schema: Optional[Dict]
    response_schema: Optional[Dict]
    examples: Dict[str, Any]


class DocumentationGenerator:
    """文档生成器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载文档模板"""
        return {
            "schema_doc": """# {title}

## 概述

{description}

## Schema定义

```json
{schema_json}
```

## 属性说明

{properties_table}

## 示例

### 有效示例

```json
{valid_examples}
```

### 无效示例

```json
{invalid_examples}
```

## 使用场景

{usage_scenarios}

## 相关Schema

{related_schemas}

---
*生成时间: {generated_at}*
""",
            "api_doc": """# {title}

## {method} {endpoint}

{description}

### 请求参数

{parameters_table}

### 请求体

```json
{request_schema}
```

### 响应

```json
{response_schema}
```

### 示例请求

```bash
{curl_example}
```

### 响应示例

```json
{response_example}
```

## 错误码

{error_codes}

---
*最后更新: {updated_at}*
""",
            "changelog": """# 变更日志

## 版本历史

{version_history}

## 最新变更

{latest_changes}

## 即将废弃

{deprecations}

---
*此日志自动生成于 {generated_at}*
"""
        }
    
    def generate_schema_doc(self, schema: Dict, 
                           title: str = None,
                           description: str = None) -> str:
        """
        生成Schema文档
        
        Args:
            schema: JSON Schema
            title: 文档标题
            description: 文档描述
        
        Returns:
            str: Markdown格式的文档
        """
        schema_title = title or schema.get("title", "Schema Documentation")
        schema_desc = description or schema.get("description", 
                                               "自动生成的Schema文档")
        
        # 生成属性表格
        properties_table = self._generate_properties_table(schema)
        
        # 生成示例
        valid_examples = self._generate_valid_examples(schema)
        invalid_examples = self._generate_invalid_examples(schema)
        
        # 使用场景
        usage_scenarios = self._infer_usage_scenarios(schema)
        
        # 相关Schema
        related_schemas = self._find_related_schemas(schema)
        
        return self.templates["schema_doc"].format(
            title=schema_title,
            description=schema_desc,
            schema_json=json.dumps(schema, indent=2, ensure_ascii=False),
            properties_table=properties_table,
            valid_examples=json.dumps(valid_examples, indent=2, ensure_ascii=False),
            invalid_examples=json.dumps(invalid_examples, indent=2, ensure_ascii=False),
            usage_scenarios=usage_scenarios,
            related_schemas=related_schemas,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _generate_properties_table(self, schema: Dict, prefix: str = "") -> str:
        """生成属性说明表格"""
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        if not properties:
            return "此Schema没有定义属性。"
        
        lines = ["| 属性名 | 类型 | 必需 | 描述 | 约束 |", 
                 "|--------|------|------|------|------|"]
        
        for prop_name, prop_schema in properties.items():
            is_required = "✓" if prop_name in required else ""
            prop_type = prop_schema.get("type", "any")
            prop_desc = prop_schema.get("description", "")
            
            # 收集约束
            constraints = []
            if "minimum" in prop_schema:
                constraints.append(f"min: {prop_schema['minimum']}")
            if "maximum" in prop_schema:
                constraints.append(f"max: {prop_schema['maximum']}")
            if "minLength" in prop_schema:
                constraints.append(f"minLen: {prop_schema['minLength']}")
            if "maxLength" in prop_schema:
                constraints.append(f"maxLen: {prop_schema['maxLength']}")
            if "enum" in prop_schema:
                constraints.append(f"enum: {prop_schema['enum']}")
            if "pattern" in prop_schema:
                constraints.append(f"pattern: {prop_schema['pattern'][:20]}...")
            
            constraint_str = ", ".join(constraints) if constraints else "-"
            
            lines.append(f"| {prefix}{prop_name} | {prop_type} | {is_required} | {prop_desc} | {constraint_str} |")
            
            # 递归处理嵌套对象
            if prop_schema.get("type") == "object" and "properties" in prop_schema:
                nested_table = self._generate_properties_table(prop_schema, f"{prefix}{prop_name}.")
                # 提取表格行（跳过表头）
                nested_rows = nested_table.split("\n")[2:]
                lines.extend(nested_rows)
        
        return "\n".join(lines)
    
    def _generate_valid_examples(self, schema: Dict) -> List[Dict]:
        """生成有效示例"""
        examples = schema.get("examples", [])
        
        if examples:
            return examples[:3]  # 最多返回3个示例
        
        # 自动生成示例
        return [self._generate_example_from_schema(schema, valid=True)]
    
    def _generate_invalid_examples(self, schema: Dict) -> List[Dict]:
        """生成无效示例（用于展示约束）"""
        return [self._generate_example_from_schema(schema, valid=False)]
    
    def _generate_example_from_schema(self, schema: Dict, valid: bool = True) -> Any:
        """根据Schema生成示例"""
        if not valid:
            # 生成违反约束的示例
            return self._generate_invalid_example(schema)
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            example = {}
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required or valid:
                    example[prop_name] = self._generate_example_from_schema(prop_schema, valid)
            
            return example
        
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            return [self._generate_example_from_schema(items_schema, valid)]
        
        elif schema_type == "string"::
            if "format" in schema:
                format_map = {
                    "email": "user@example.com",
                    "date-time": datetime.now().isoformat(),
                    "uri": "https://example.com",
                    "uuid": "550e8400-e29b-41d4-a716-446655440000"
                }
                return format_map.get(schema["format"], "string")
            return "example string"
        
        elif schema_type == "integer":
            return schema.get("minimum", 0) + 1
        
        elif schema_type == "number":
            return schema.get("minimum", 0.0) + 1.5
        
        elif schema_type == "boolean":
            return True
        
        return None
    
    def _generate_invalid_example(self, schema: Dict) -> Any:
        """生成无效示例"""
        schema_type = schema.get("type", "object")
        
        if schema_type == "string":
            if "minLength" in schema:
                return ""  # 空字符串违反minLength
            if "pattern" in schema:
                return "invalid"
            if "format" == "email":
                return "not-an-email"
        
        elif schema_type == "integer":
            if "minimum" in schema:
                return schema["minimum"] - 1
            if "maximum" in schema:
                return schema["maximum"] + 1
        
        return None
    
    def _infer_usage_scenarios(self, schema: Dict) -> str:
        """推断使用场景"""
        scenarios = []
        schema_str = json.dumps(schema).lower()
        
        if "user" in schema_str or "email" in schema_str:
            scenarios.append("- 用户注册和资料管理")
        if "product" in schema_str or "price" in schema_str:
            scenarios.append("- 电商产品信息管理")
        if "order" in schema_str or "payment" in schema_str:
            scenarios.append("- 订单处理和支付系统")
        if "event" in schema_str or "log" in schema_str:
            scenarios.append("- 事件记录和审计日志")
        if "api" in schema_str or "response" in schema_str:
            scenarios.append("- API响应格式定义")
        
        return "\n".join(scenarios) if scenarios else "- 通用数据验证"
    
    def _find_related_schemas(self, schema: Dict) -> str:
        """查找相关Schema"""
        refs = []
        schema_str = json.dumps(schema)
        
        # 提取$ref引用
        ref_pattern = r'"\$ref":\s*"([^"]+)"'
        matches = re.findall(ref_pattern, schema_str)
        
        for ref in set(matches):
            refs.append(f"- `{ref}`")
        
        return "\n".join(refs) if refs else "无相关Schema引用"
    
    def generate_api_doc(self, api_spec: Dict) -> str:
        """生成API文档"""
        title = api_spec.get("title", "API Documentation")
        endpoint = api_spec.get("endpoint", "/")
        method = api_spec.get("method", "GET").upper()
        description = api_spec.get("description", "")
        
        # 参数表格
        params = api_spec.get("parameters", [])
        params_table = self._generate_params_table(params)
        
        # Schema
        request_schema = api_spec.get("requestSchema", {})
        response_schema = api_spec.get("responseSchema", {})
        
        # 示例
        curl_example = self._generate_curl_example(api_spec)
        response_example = api_spec.get("examples", {}).get("response", {})
        
        # 错误码
        error_codes = self._generate_error_codes(api_spec)
        
        return self.templates["api_doc"].format(
            title=title,
            method=method,
            endpoint=endpoint,
            description=description,
            parameters_table=params_table,
            request_schema=json.dumps(request_schema, indent=2, ensure_ascii=False),
            response_schema=json.dumps(response_schema, indent=2, ensure_ascii=False),
            curl_example=curl_example,
            response_example=json.dumps(response_example, indent=2, ensure_ascii=False),
            error_codes=error_codes,
            updated_at=datetime.now().strftime("%Y-%m-%d")
        )
    
    def _generate_params_table(self, params: List[Dict]) -> str:
        """生成参数表格"""
        if not params:
            return "无参数"
        
        lines = ["| 参数名 | 位置 | 类型 | 必需 | 描述 |",
                 "|--------|------|------|------|------|"]
        
        for param in params:
            lines.append(
                f"| {param.get('name', '-')} | {param.get('in', '-')} | "
                f"{param.get('schema', {}).get('type', '-')} | "
                f"{'✓' if param.get('required') else ''} | "
                f"{param.get('description', '-')} |"
            )
        
        return "\n".join(lines)
    
    def _generate_curl_example(self, api_spec: Dict) -> str:
        """生成cURL示例"""
        method = api_spec.get("method", "GET").upper()
        endpoint = api_spec.get("endpoint", "/")
        base_url = api_spec.get("baseUrl", "https://api.example.com")
        
        cmd = f"curl -X {method} '{base_url}{endpoint}'"
        
        if method in ["POST", "PUT", "PATCH"]:
            example_body = api_spec.get("examples", {}).get("request", {})
            cmd += f" \\\n  -H 'Content-Type: application/json' \\\n  -d '{json.dumps(example_body)}'"
        
        return cmd
    
    def _generate_error_codes(self, api_spec: Dict) -> str:
        """生成错误码说明"""
        responses = api_spec.get("responses", {})
        
        lines = ["| 状态码 | 描述 | 场景 |",
                 "|--------|------|------|"]
        
        for code, info in responses.items():
            if code.startswith("4") or code.startswith("5"):
                lines.append(f"| {code} | {info.get('description', '-')} | {info.get('scenario', '-')} |")
        
        return "\n".join(lines) if len(lines) > 2 else "| 400 | 请求参数错误 | 输入验证失败 |\n| 500 | 服务器内部错误 | 系统异常 |"
    
    def generate_changelog(self, versions: List[Dict]) -> str:
        """生成变更日志"""
        version_history = []
        latest_changes = []
        deprecations = []
        
        for version in versions:
            ver_num = version.get("version", "0.0.0")
            date = version.get("date", "Unknown")
            changes = version.get("changes", [])
            
            version_history.append(f"\n### {ver_num} ({date})\n")
            for change in changes:
                change_type = change.get("type", "changed")
                desc = change.get("description", "")
                version_history.append(f"- **{change_type}**: {desc}")
                
                if change_type == "deprecated":
                    deprecations.append(f"- {ver_num}: {desc}")
        
        if versions:
            latest = versions[0]
            latest_changes = [f"- {c.get('description', '')}" 
                            for c in latest.get("changes", [])]
        
        return self.templates["changelog"].format(
            version_history="\n".join(version_history),
            latest_changes="\n".join(latest_changes) if latest_changes else "无最新变更",
            deprecations="\n".join(deprecations) if deprecations else "无即将废弃的功能",
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def export_to_html(self, markdown_content: str, 
                      title: str = "Documentation") -> str:
        """将Markdown导出为HTML"""
        # 简化实现，实际可使用markdown库
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; }}
        pre {{ background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        pre code {{ background: none; padding: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f4f4f4; font-weight: 600; }}
    </style>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>"""
        return html_template


def main():
    """示例用法"""
    generator = DocumentationGenerator()
    
    # 示例1: Schema文档
    print("=" * 60)
    print("生成Schema文档")
    print("=" * 60)
    
    schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "$id": "user",
        "title": "User Profile Schema",
        "type": "object",
        "description": "用户资料数据模型",
        "properties": {
            "id": {
                "type": "string",
                "description": "用户唯一标识"
            },
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 50,
                "description": "用户名"
            },
            "email": {
                "type": "string",
                "format": "email",
                "description": "邮箱地址"
            },
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 150,
                "description": "年龄"
            }
        },
        "required": ["id", "username", "email"],
        "examples": [
            {
                "id": "user-001",
                "username": "alice",
                "email": "alice@example.com",
                "age": 30
            }
        ]
    }
    
    doc = generator.generate_schema_doc(schema)
    print(doc[:1500] + "...")
    
    # 示例2: 变更日志
    print("\n" + "=" * 60)
    print("生成变更日志")
    print("=" * 60)
    
    versions = [
        {
            "version": "2.0.0",
            "date": "2025-01-15",
            "changes": [
                {"type": "added", "description": "新增age字段"},
                {"type": "changed", "description": "username最小长度从1改为3"},
                {"type": "deprecated", "description": "nickname字段将在3.0.0移除"}
            ]
        },
        {
            "version": "1.0.0",
            "date": "2024-12-01",
            "changes": [
                {"type": "added", "description": "初始版本发布"}
            ]
        }
    ]
    
    changelog = generator.generate_changelog(versions)
    print(changelog)


if __name__ == "__main__":
    main()
