#!/usr/bin/env python3
"""
AI Schema Assistant
===================

AI辅助Schema设计工具，提供：
- 自然语言到Schema的生成
- Schema优化建议
- 智能补全
- 错误诊断和修复建议
- 最佳实践推荐

Version: 2.3.0
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


@dataclass
class AISuggestion:
    """AI建议"""
    type: str  # 'generation', 'optimization', 'fix', 'completion'
    message: str
    confidence: float  # 0-1
    suggested_code: Optional[Dict] = None
    explanation: str = ""


class AISchemaAssistant:
    """AI Schema助手"""
    
    def __init__(self):
        self.pattern_library = self._load_pattern_library()
        self.best_practices = self._load_best_practices()
    
    def _load_pattern_library(self) -> Dict:
        """加载模式库"""
        return {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "username": {"type": "string", "minLength": 3, "maxLength": 50},
                    "email": {"type": "string", "format": "email"},
                    "createdAt": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "username", "email"]
            },
            "product": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string", "minLength": 1},
                    "price": {"type": "number", "minimum": 0},
                    "currency": {"type": "string", "enum": ["USD", "EUR", "CNY"]}
                },
                "required": ["id", "name", "price"]
            },
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "postalCode": {"type": "string"},
                    "country": {"type": "string", "pattern": "^[A-Z]{2}$"}
                }
            }
        }
    
    def _load_best_practices(self) -> List[Dict]:
        """加载最佳实践"""
        return [
            {
                "check": "missing_description",
                "message": "建议添加description字段以提高可读性",
                "severity": "info"
            },
            {
                "check": "missing_examples",
                "message": "建议添加examples以展示预期数据",
                "severity": "info"
            },
            {
                "check": "weak_string_constraints",
                "message": "字符串字段建议添加minLength/maxLength约束",
                "severity": "warning"
            },
            {
                "check": "no_required_fields",
                "message": "对象建议定义required字段",
                "severity": "warning"
            }
        ]
    
    def generate_from_description(self, description: str) -> AISuggestion:
        """
        从自然语言描述生成Schema
        
        Args:
            description: 自然语言描述，如"用户资料，包含姓名、邮箱和年龄"
        
        Returns:
            AISuggestion: 生成的Schema建议
        """
        # 解析描述中的实体和属性
        entities = self._extract_entities(description)
        
        # 根据实体类型选择模式
        if "用户" in description or "user" in description.lower():
            base_schema = self.pattern_library["user"].copy()
        elif "产品" in description or "product" in description.lower():
            base_schema = self.pattern_library["product"].copy()
        elif "地址" in description or "address" in description.lower():
            base_schema = self.pattern_library["address"].copy()
        else:
            base_schema = {"type": "object", "properties": {}}
        
        # 根据描述中的属性进行定制
        schema = self._customize_schema(base_schema, description)
        
        return AISuggestion(
            type="generation",
            message=f"基于描述生成的Schema: {description[:50]}...",
            confidence=0.85,
            suggested_code=schema,
            explanation="根据自然语言描述，使用模式匹配和关键词提取生成的Schema"
        )
    
    def _extract_entities(self, description: str) -> List[str]:
        """从描述中提取实体"""
        # 简单的实体提取
        entities = []
        keywords = ["用户", "产品", "订单", "地址", "user", "product", "order", "address"]
        
        for keyword in keywords:
            if keyword in description.lower():
                entities.append(keyword)
        
        return entities
    
    def _customize_schema(self, schema: Dict, description: str) -> Dict:
        """根据描述定制Schema"""
        # 添加描述中提到的额外字段
        if "年龄" in description or "age" in description.lower():
            if "properties" not in schema:
                schema["properties"] = {}
            schema["properties"]["age"] = {
                "type": "integer",
                "minimum": 0,
                "maximum": 150,
                "description": "年龄"
            }
        
        if "电话" in description or "phone" in description.lower():
            if "properties" not in schema:
                schema["properties"] = {}
            schema["properties"]["phone"] = {
                "type": "string",
                "pattern": "^\\+?[1-9]\\d{1,14}$",
                "description": "电话号码"
            }
        
        return schema
    
    def suggest_optimizations(self, schema: Dict) -> List[AISuggestion]:
        """
        建议Schema优化
        
        Args:
            schema: 待优化的Schema
        
        Returns:
            List[AISuggestion]: 优化建议列表
        """
        suggestions = []
        
        for practice in self.best_practices:
            result = self._check_practice(schema, practice)
            if result:
                suggestions.append(result)
        
        # 检查特定模式
        string_fields = self._find_string_fields(schema)
        for field_path in string_fields:
            field = self._get_field_by_path(schema, field_path)
            if "minLength" not in field and "maxLength" not in field:
                suggestions.append(AISuggestion(
                    type="optimization",
                    message=f"字段 '{field_path}' 建议添加长度约束",
                    confidence=0.75,
                    suggested_code={"minLength": 1, "maxLength": 255},
                    explanation="无约束的字符串可能导致安全问题或数据质量下降"
                ))
        
        return suggestions
    
    def _check_practice(self, schema: Dict, practice: Dict) -> Optional[AISuggestion]:
        """检查单个最佳实践"""
        check_type = practice["check"]
        
        if check_type == "missing_description":
            if "description" not in schema:
                return AISuggestion(
                    type="optimization",
                    message=practice["message"],
                    confidence=0.9,
                    explanation="描述帮助其他开发者理解Schema的用途"
                )
        
        elif check_type == "missing_examples":
            if "examples" not in schema:
                return AISuggestion(
                    type="optimization",
                    message=practice["message"],
                    confidence=0.8
                )
        
        elif check_type == "no_required_fields":
            if schema.get("type") == "object" and "required" not in schema:
                return AISuggestion(
                    type="optimization",
                    message=practice["message"],
                    confidence=0.85,
                    explanation="明确哪些字段是必需的可以提高数据质量"
                )
        
        return None
    
    def _find_string_fields(self, schema: Dict, path: str = "") -> List[str]:
        """找到所有字符串字段"""
        fields = []
        
        if isinstance(schema, dict):
            if schema.get("type") == "string":
                fields.append(path)
            
            if "properties" in schema:
                for key, value in schema["properties"].items():
                    new_path = f"{path}.{key}" if path else key
                    fields.extend(self._find_string_fields(value, new_path))
        
        return fields
    
    def _get_field_by_path(self, schema: Dict, path: str) -> Dict:
        """通过路径获取字段"""
        parts = path.split(".")
        current = schema
        
        for part in parts:
            if "properties" in current and part in current["properties"]:
                current = current["properties"][part]
            else:
                return {}
        
        return current
    
    def diagnose_errors(self, schema: Dict, validation_errors: List[str]) -> List[AISuggestion]:
        """
        诊断错误并提供修复建议
        
        Args:
            schema: 有错误的Schema
            validation_errors: 验证错误列表
        
        Returns:
            List[AISuggestion]: 修复建议
        """
        suggestions = []
        
        for error in validation_errors:
            if "Circular reference" in error:
                suggestions.append(AISuggestion(
                    type="fix",
                    message="检测到循环引用",
                    confidence=0.95,
                    explanation="循环引用会导致无限递归，建议使用ID引用或重构模型",
                    suggested_code={"use_id_reference": True}
                ))
            
            elif "Invalid type" in error:
                suggestions.append(AISuggestion(
                    type="fix",
                    message="类型定义错误",
                    confidence=0.9,
                    explanation="使用JSON Schema标准类型: string, number, integer, boolean, array, object, null"
                ))
            
            elif "minimum > maximum" in error:
                suggestions.append(AISuggestion(
                    type="fix",
                    message="数值范围错误",
                    confidence=0.95,
                    explanation="minimum应该小于或等于maximum"
                ))
        
        return suggestions
    
    def smart_completion(self, schema: Dict, cursor_path: str) -> AISuggestion:
        """
        智能补全
        
        Args:
            schema: 当前Schema
            cursor_path: 光标位置
        
        Returns:
            AISuggestion: 补全建议
        """
        # 根据上下文推断可能的补全
        parent_path = ".".join(cursor_path.split(".")[:-1])
        parent = self._get_field_by_path(schema, parent_path) if parent_path else schema
        
        if isinstance(parent, dict):
            if "type" not in parent:
                return AISuggestion(
                    type="completion",
                    message="补全类型定义",
                    confidence=0.8,
                    suggested_code={"type": "object"},
                    explanation="根据上下文推断为对象类型"
                )
            
            if parent.get("type") == "object" and "properties" not in parent:
                return AISuggestion(
                    type="completion",
                    message="添加properties",
                    confidence=0.9,
                    suggested_code={"properties": {}},
                    explanation="对象类型应该定义properties"
                )
        
        return AISuggestion(
            type="completion",
            message="继续编辑",
            confidence=0.5
        )
    
    def chat(self, message: str, context: Dict = None) -> str:
        """
        对话式交互
        
        Args:
            message: 用户消息
            context: 对话上下文
        
        Returns:
            str: AI回复
        """
        # 简单的关键词响应
        message_lower = message.lower()
        
        if "生成" in message or "create" in message_lower:
            return "我可以帮您生成Schema。请描述您需要的结构，例如：'创建一个用户资料Schema，包含姓名、邮箱和年龄'"
        
        elif "优化" in message or "optimize" in message_lower:
            return "我可以帮您优化现有Schema。请提供您的Schema，我将分析并给出改进建议。"
        
        elif "错误" in message or "error" in message_lower:
            return "请提供您的Schema和遇到的错误信息，我将帮您诊断问题并提供修复建议。"
        
        else:
            return "我是AI Schema助手。我可以帮您：\n1. 从自然语言描述生成Schema\n2. 优化现有Schema\n3. 诊断和修复错误\n4. 提供智能补全建议\n\n请问有什么可以帮您的？"


def main():
    """示例用法"""
    assistant = AISchemaAssistant()
    
    # 示例1: 从描述生成Schema
    print("=" * 60)
    print("示例1: 从自然语言生成Schema")
    print("=" * 60)
    
    description = "用户资料，包含姓名、邮箱、年龄和电话号码"
    suggestion = assistant.generate_from_description(description)
    
    print(f"描述: {description}")
    print(f"建议: {suggestion.message}")
    print(f"置信度: {suggestion.confidence}")
    print(f"生成的Schema:")
    print(json.dumps(suggestion.suggested_code, indent=2, ensure_ascii=False))
    
    # 示例2: 优化建议
    print("\n" + "=" * 60)
    print("示例2: Schema优化建议")
    print("=" * 60)
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        }
    }
    
    suggestions = assistant.suggest_optimizations(schema)
    
    print("输入Schema:")
    print(json.dumps(schema, indent=2))
    print(f"\n找到 {len(suggestions)} 个优化建议:")
    
    for i, sugg in enumerate(suggestions, 1):
        print(f"{i}. [{sugg.type}] {sugg.message}")
        if sugg.explanation:
            print(f"   解释: {sugg.explanation}")
    
    # 示例3: 错误诊断
    print("\n" + "=" * 60)
    print("示例3: 错误诊断")
    print("=" * 60)
    
    errors = ["Invalid type: 'interger' (should be 'integer')"]
    fix_suggestions = assistant.diagnose_errors({}, errors)
    
    print(f"错误: {errors[0]}")
    print(f"建议: {fix_suggestions[0].message}")
    print(f"解释: {fix_suggestions[0].explanation}")
    
    # 示例4: 对话
    print("\n" + "=" * 60)
    print("示例4: AI对话")
    print("=" * 60)
    
    user_message = "我想优化我的Schema"
    response = assistant.chat(user_message)
    
    print(f"用户: {user_message}")
    print(f"AI: {response}")


if __name__ == "__main__":
    main()
