#!/usr/bin/env python3
"""
Schema Template Manager
=======================

Schema模板管理器，提供：
- 模板库管理
- 模板继承
- 参数化模板
- 模板版本控制
- 模板验证

Version: 2.3.0
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime


@dataclass
class Template:
    """模板定义"""
    id: str
    name: str
    description: str
    category: str
    schema: Dict
    parameters: List[Dict]
    parent: Optional[str] = None
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


@dataclass
class TemplateInstance:
    """模板实例"""
    template_id: str
    parameters: Dict[str, Any]
    generated_schema: Dict
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SchemaTemplateManager:
    """Schema模板管理器"""
    
    def __init__(self, template_dir: str = None):
        self.templates: Dict[str, Template] = {}
        self.instances: List[TemplateInstance] = []
        self.template_dir = Path(template_dir) if template_dir else None
        
        # 注册内置模板
        self._register_builtin_templates()
    
    def _register_builtin_templates(self):
        """注册内置模板"""
        builtin_templates = [
            Template(
                id="rest-api-response",
                name="REST API Response",
                description="Standard REST API response format",
                category="api",
                schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "data": {"type": "object"},
                        "error": {
                            "type": ["object", "null"],
                            "properties": {
                                "code": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string", "format": "date-time"},
                                "requestId": {"type": "string"}
                            }
                        }
                    },
                    "required": ["success"]
                },
                parameters=[
                    {"name": "include_pagination", "type": "boolean", "default": False},
                    {"name": "data_schema", "type": "object", "default": {}}
                ]
            ),
            Template(
                id="paginated-list",
                name="Paginated List",
                description="Paginated list response with items",
                category="data",
                schema={
                    "type": "object",
                    "properties": {
                        "items": {"type": "array"},
                        "pagination": {
                            "type": "object",
                            "properties": {
                                "page": {"type": "integer", "minimum": 1},
                                "pageSize": {"type": "integer", "minimum": 1},
                                "totalPages": {"type": "integer"},
                                "totalItems": {"type": "integer"}
                            }
                        }
                    },
                    "required": ["items", "pagination"]
                },
                parameters=[
                    {"name": "item_schema", "type": "object", "required": True},
                    {"name": "max_page_size", "type": "integer", "default": 100}
                ]
            ),
            Template(
                id="entity-base",
                name="Entity Base",
                description="Base schema for entities with audit fields",
                category="entity",
                schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "createdAt": {"type": "string", "format": "date-time"},
                        "updatedAt": {"type": "string", "format": "date-time"},
                        "createdBy": {"type": "string"},
                        "updatedBy": {"type": "string"},
                        "version": {"type": "integer", "minimum": 1}
                    },
                    "required": ["id"]
                },
                parameters=[
                    {"name": "include_version", "type": "boolean", "default": True},
                    {"name": "include_audit", "type": "boolean", "default": True}
                ]
            ),
            Template(
                id="user-profile",
                name="User Profile",
                description="User profile schema",
                category="entity",
                parent="entity-base",
                schema={
                    "allOf": [
                        {"$ref": "#/$template/entity-base"},
                        {
                            "type": "object",
                            "properties": {
                                "username": {"type": "string", "minLength": 3},
                                "email": {"type": "string", "format": "email"},
                                "displayName": {"type": "string"},
                                "avatar": {"type": "string", "format": "uri"},
                                "status": {"type": "string", "enum": ["active", "inactive", "suspended"]}
                            },
                            "required": ["username", "email"]
                        }
                    ]
                },
                parameters=[
                    {"name": "username_min_length", "type": "integer", "default": 3},
                    {"name": "require_email_verification", "type": "boolean", "default": False}
                ]
            )
        ]
        
        for template in builtin_templates:
            self.register_template(template)
    
    def register_template(self, template: Template):
        """注册模板"""
        self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: str = None, 
                      tags: List[str] = None) -> List[Template]:
        """
        列出模板
        
        Args:
            category: 按类别过滤
            tags: 按标签过滤
        
        Returns:
            List[Template]: 模板列表
        """
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        return templates
    
    def instantiate(self, template_id: str, parameters: Dict[str, Any] = None) -> Dict:
        """
        实例化模板
        
        Args:
            template_id: 模板ID
            parameters: 参数值
        
        Returns:
            Dict: 生成的Schema
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        parameters = parameters or {}
        
        # 处理继承
        schema = self._resolve_inheritance(template)
        
        # 应用参数
        schema = self._apply_parameters(schema, parameters, template.parameters)
        
        # 记录实例
        instance = TemplateInstance(
            template_id=template_id,
            parameters=parameters,
            generated_schema=schema
        )
        self.instances.append(instance)
        
        return schema
    
    def _resolve_inheritance(self, template: Template) -> Dict:
        """解析模板继承"""
        if not template.parent:
            return template.schema.copy()
        
        parent = self.get_template(template.parent)
        if not parent:
            return template.schema.copy()
        
        # 递归解析父模板
        parent_schema = self._resolve_inheritance(parent)
        
        # 合并子模板
        return self._merge_schemas(parent_schema, template.schema)
    
    def _merge_schemas(self, parent: Dict, child: Dict) -> Dict:
        """合并父Schema和子Schema"""
        result = parent.copy()
        
        for key, value in child.items():
            if key == "allOf":
                # 处理allOf合并
                if "allOf" not in result:
                    result["allOf"] = []
                result["allOf"].extend(value)
            elif key == "properties" and key in result:
                # 合并属性
                result[key] = {**result[key], **value}
            elif isinstance(value, dict) and isinstance(result.get(key), dict):
                # 递归合并
                result[key] = self._merge_schemas(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_parameters(self, schema: Dict, values: Dict, 
                         parameters: List[Dict]) -> Dict:
        """应用参数到Schema"""
        schema_str = json.dumps(schema)
        
        # 构建完整参数（包含默认值）
        full_params = {}
        for param in parameters:
            param_name = param["name"]
            if param_name in values:
                full_params[param_name] = values[param_name]
            elif "default" in param:
                full_params[param_name] = param["default"]
            elif param.get("required"):
                raise ValueError(f"Required parameter not provided: {param_name}")
        
        # 替换参数占位符
        for param_name, param_value in full_params.items():
            placeholder = f"{{{{params.{param_name}}}}}"
            if placeholder in schema_str:
                schema_str = schema_str.replace(placeholder, json.dumps(param_value))
        
        # 处理条件逻辑
        schema_str = self._process_conditionals(schema_str, full_params)
        
        return json.loads(schema_str)
    
    def _process_conditionals(self, schema_str: str, params: Dict) -> str:
        """处理条件逻辑"""
        # 简单实现：处理 {{#if param}}...{{/if}} 结构
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_if(match):
            param_name = match.group(1)
            content = match.group(2)
            
            if params.get(param_name):
                return content
            return ""
        
        return re.sub(pattern, replace_if, schema_str, flags=re.DOTALL)
    
    def create_template(self, name: str, base_schema: Dict,
                       parameters: List[Dict] = None,
                       category: str = "custom",
                       parent: str = None) -> Template:
        """
        从现有Schema创建模板
        
        Args:
            name: 模板名称
            base_schema: 基础Schema
            parameters: 参数定义
            category: 类别
            parent: 父模板ID
        
        Returns:
            Template: 创建的模板
        """
        template_id = name.lower().replace(" ", "-")
        
        template = Template(
            id=template_id,
            name=name,
            description=f"Custom template: {name}",
            category=category,
            schema=base_schema,
            parameters=parameters or [],
            parent=parent
        )
        
        self.register_template(template)
        return template
    
    def export_template(self, template_id: str, format: str = "json") -> str:
        """
        导出模板
        
        Args:
            template_id: 模板ID
            format: 导出格式 (json, yaml)
        
        Returns:
            str: 导出的模板内容
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        if format == "json":
            return json.dumps({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "version": template.version,
                "schema": template.schema,
                "parameters": template.parameters,
                "parent": template.parent,
                "tags": template.tags
            }, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_template(self, content: str, format: str = "json") -> Template:
        """
        导入模板
        
        Args:
            content: 模板内容
            format: 格式
        
        Returns:
            Template: 导入的模板
        """
        if format == "json":
            data = json.loads(content)
            template = Template(**data)
            self.register_template(template)
            return template
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_usage_stats(self) -> Dict:
        """获取模板使用统计"""
        stats = {
            "total_templates": len(self.templates),
            "total_instances": len(self.instances),
            "by_category": {},
            "popular_templates": []
        }
        
        # 按类别统计
        for template in self.templates.values():
            cat = template.category
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        
        # 统计模板实例化次数
        instance_counts = {}
        for inst in self.instances:
            tid = inst.template_id
            instance_counts[tid] = instance_counts.get(tid, 0) + 1
        
        # 热门模板
        sorted_templates = sorted(instance_counts.items(), key=lambda x: x[1], reverse=True)
        stats["popular_templates"] = sorted_templates[:5]
        
        return stats


def main():
    """示例用法"""
    manager = SchemaTemplateManager()
    
    print("=" * 60)
    print("Schema模板管理器")
    print("=" * 60)
    
    # 列出可用模板
    print("\n可用模板:")
    for template in manager.list_templates():
        print(f"  - [{template.category}] {template.name} ({template.id})")
    
    # 实例化模板
    print("\n" + "=" * 60)
    print("实例化模板: REST API Response")
    print("=" * 60)
    
    schema = manager.instantiate("rest-api-response", {
        "include_pagination": True,
        "data_schema": {"type": "object", "properties": {"id": {"type": "string"}}}
    })
    
    print(json.dumps(schema, indent=2, ensure_ascii=False))
    
    # 实例化带继承的模板
    print("\n" + "=" * 60)
    print("实例化模板: User Profile (继承自 Entity Base)")
    print("=" * 60)
    
    schema = manager.instantiate("user-profile", {
        "username_min_length": 5
    })
    
    print(json.dumps(schema, indent=2, ensure_ascii=False))
    
    # 创建自定义模板
    print("\n" + "=" * 60)
    print("创建自定义模板")
    print("=" * 60)
    
    template = manager.create_template(
        name="Product",
        base_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
                "category": {"type": "string"}
            },
            "required": ["name", "price"]
        },
        parameters=[
            {"name": "currency", "type": "string", "default": "USD"}
        ],
        category="ecommerce"
    )
    
    print(f"创建模板: {template.name} (ID: {template.id})")
    
    # 获取统计
    print("\n" + "=" * 60)
    print("使用统计")
    print("=" * 60)
    
    stats = manager.get_usage_stats()
    print(f"总模板数: {stats['total_templates']}")
    print(f"总实例数: {stats['total_instances']}")
    print(f"按类别分布: {stats['by_category']}")


if __name__ == "__main__":
    main()
