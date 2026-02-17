#!/usr/bin/env python3
"""
Hierarchy Mapping Engine
========================

层次映射引擎，用于：
- 执行层次间模型转换
- 验证映射正确性
- 保持语义等价性
- 生成映射轨迹

Version: 2.2.0
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from pathlib import Path


T = TypeVar('T')
R = TypeVar('R')


class MappingLevel(Enum):
    """映射层次"""
    L1_FOUNDATION = 1      # 基础层: 集合论、类型论
    L2_META_MODEL = 2      # 元模型层: JSON Schema、OWL
    L3_DATA_MODEL = 3      # 数据模型层: 领域模型
    L4_SERVICE_MODEL = 4   # 服务模型层: API、消息
    L5_APPLICATION = 5     # 应用模型层: 业务应用


class MappingDirection(Enum):
    """映射方向"""
    UP = "up"           # 抽象化
    DOWN = "down"       # 具体化
    HORIZONTAL = "h"    # 同级转换


@dataclass
class MappingRule:
    """映射规则"""
    name: str
    source_level: MappingLevel
    target_level: MappingLevel
    condition: Callable[[Any], bool]
    transform: Callable[[Any], Any]
    preserves: List[str] = field(default_factory=list)


@dataclass
class MappingResult:
    """映射结果"""
    success: bool
    source: Any
    target: Optional[Any] = None
    trace: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    preservation_checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class HierarchyMappingEngine:
    """层次映射引擎"""
    
    def __init__(self):
        self.rules: Dict[tuple, List[MappingRule]] = {}
        self.mappings: List[MappingResult] = []
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认映射规则"""
        # L1 → L2: 基础到元模型
        self.register_rule(MappingRule(
            name="set_to_schema_type",
            source_level=MappingLevel.L1_FOUNDATION,
            target_level=MappingLevel.L2_META_MODEL,
            condition=lambda x: isinstance(x, set),
            transform=self._set_to_schema_type,
            preserves=["cardinality", "membership"]
        ))
        
        self.register_rule(MappingRule(
            name="function_to_property",
            source_level=MappingLevel.L1_FOUNDATION,
            target_level=MappingLevel.L2_META_MODEL,
            condition=lambda x: callable(x),
            transform=self._function_to_property,
            preserves=["typing", "domain", "codomain"]
        ))
        
        # L2 → L3: 元模型到数据模型
        self.register_rule(MappingRule(
            name="json_schema_to_ontology",
            source_level=MappingLevel.L2_META_MODEL,
            target_level=MappingLevel.L3_DATA_MODEL,
            condition=lambda x: isinstance(x, dict) and "type" in x,
            transform=self._json_schema_to_ontology,
            preserves=["structure", "constraints"]
        ))
        
        self.register_rule(MappingRule(
            name="owl_class_to_entity",
            source_level=MappingLevel.L2_META_MODEL,
            target_level=MappingLevel.L3_DATA_MODEL,
            condition=lambda x: isinstance(x, dict) and "owl:Class" in str(x),
            transform=self._owl_class_to_entity,
            preserves=["inheritance", "properties"]
        ))
        
        # L3 → L4: 数据模型到服务模型
        self.register_rule(MappingRule(
            name="entity_to_api_resource",
            source_level=MappingLevel.L3_DATA_MODEL,
            target_level=MappingLevel.L4_SERVICE_MODEL,
            condition=lambda x: isinstance(x, dict) and "entity" in str(x).lower(),
            transform=self._entity_to_api_resource,
            preserves=["identity", "attributes"]
        ))
        
        # L4 → L5: 服务模型到应用模型
        self.register_rule(MappingRule(
            name="api_to_ui_component",
            source_level=MappingLevel.L4_SERVICE_MODEL,
            target_level=MappingLevel.L5_APPLICATION,
            condition=lambda x: isinstance(x, dict) and "endpoint" in x,
            transform=self._api_to_ui_component,
            preserves=["functionality", "data_flow"]
        ))
    
    def register_rule(self, rule: MappingRule):
        """注册映射规则"""
        key = (rule.source_level, rule.target_level)
        if key not in self.rules:
            self.rules[key] = []
        self.rules[key].append(rule)
    
    def map(self, source: Any, source_level: MappingLevel, 
            target_level: MappingLevel) -> MappingResult:
        """
        执行层次映射
        
        Args:
            source: 源模型
            source_level: 源层次
            target_level: 目标层次
        
        Returns:
            MappingResult: 映射结果
        """
        trace = [f"Start: {source_level.name} → {target_level.name}"]
        
        # 检查是否需要多级映射
        if abs(target_level.value - source_level.value) > 1:
            return self._multi_step_map(source, source_level, target_level)
        
        # 查找适用的规则
        key = (source_level, target_level)
        if key not in self.rules:
            return MappingResult(
                success=False,
                source=source,
                trace=trace + ["No mapping rules found"],
                issues=[f"No rules from {source_level.name} to {target_level.name}"]
            )
        
        # 尝试应用规则
        for rule in self.rules[key]:
            if rule.condition(source):
                try:
                    target = rule.transform(source)
                    result = MappingResult(
                        success=True,
                        source=source,
                        target=target,
                        trace=trace + [f"Applied: {rule.name}"]
                    )
                    self.mappings.append(result)
                    return result
                except Exception as e:
                    trace.append(f"Failed: {rule.name} - {e}")
        
        return MappingResult(
            success=False,
            source=source,
            trace=trace,
            issues=["No applicable rule found"]
        )
    
    def _multi_step_map(self, source: Any, source_level: MappingLevel,
                       target_level: MappingLevel) -> MappingResult:
        """多级映射"""
        current = source
        current_level = source_level
        trace = [f"Multi-step: {source_level.name} → {target_level.name}"]
        
        step = 1 if target_level.value > source_level.value else -1
        
        while current_level != target_level:
            next_level = MappingLevel(current_level.value + step)
            result = self.map(current, current_level, next_level)
            
            if not result.success:
                return MappingResult(
                    success=False,
                    source=source,
                    trace=trace + result.trace,
                    issues=result.issues
                )
            
            trace.extend(result.trace)
            current = result.target
            current_level = next_level
        
        return MappingResult(
            success=True,
            source=source,
            target=current,
            trace=trace
        )
    
    # 转换函数实现
    def _set_to_schema_type(self, s: set) -> Dict:
        """集合 → JSON Schema数组类型"""
        return {
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
            "minItems": 0,
            "maxItems": len(s) if len(s) < 100 else None,
            "_source": f"Set({s})"
        }
    
    def _function_to_property(self, f: Callable) -> Dict:
        """函数 → Schema属性"""
        import inspect
        sig = inspect.signature(f)
        
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "object",
                    "properties": {
                        name: {"type": "any"}
                        for name, param in sig.parameters.items()
                    }
                },
                "output": {"type": "any"}
            },
            "_function": f.__name__
        }
    
    def _json_schema_to_ontology(self, schema: Dict) -> Dict:
        """JSON Schema → OWL本体"""
        owl = {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            },
            "@type": "owl:Class"
        }
        
        if "properties" in schema:
            owl["rdfs:subClassOf"] = []
            for prop_name, prop_schema in schema["properties"].items():
                restriction = {
                    "@type": "owl:Restriction",
                    "owl:onProperty": f":{prop_name}",
                    "owl:cardinality": 1 if prop_name in schema.get("required", []) else "0..1"
                }
                owl["rdfs:subClassOf"].append(restriction)
        
        return owl
    
    def _owl_class_to_entity(self, owl: Dict) -> Dict:
        """OWL类 → 领域实体"""
        return {
            "entityType": owl.get("rdfs:label", "UnnamedEntity"),
            "attributes": [],
            "relationships": [],
            "_ontology": owl
        }
    
    def _entity_to_api_resource(self, entity: Dict) -> Dict:
        """实体 → API资源"""
        entity_name = entity.get("entityType", "Entity")
        
        return {
            "resource": entity_name.lower(),
            "endpoints": {
                "GET": f"/{entity_name.lower()}/{{id}}",
                "POST": f"/{entity_name.lower()}",
                "PUT": f"/{entity_name.lower()}/{{id}}",
                "DELETE": f"/{entity_name.lower()}/{{id}}"
            },
            "schema": entity.get("attributes", {})
        }
    
    def _api_to_ui_component(self, api: Dict) -> Dict:
        """API → UI组件"""
        resource = api.get("resource", "item")
        
        return {
            "component": f"{resource.title()}Manager",
            "type": "CRUDComponent",
            "props": {
                "apiBase": f"/{resource}",
                "operations": list(api.get("endpoints", {}).keys())
            },
            "ui": {
                "listView": True,
                "detailView": True,
                "editForm": True
            }
        }
    
    def validate_mapping(self, mapping: MappingResult, 
                        expected_preservations: List[str]) -> ValidationResult:
        """验证映射的正确性"""
        checks = {}
        errors = []
        
        for prop in expected_preservations:
            # 简化的属性保持检查
            preserved = self._check_property_preservation(
                mapping.source, mapping.target, prop
            )
            checks[prop] = preserved
            
            if not preserved:
                errors.append(f"Property '{prop}' not preserved")
        
        return ValidationResult(
            valid=len(errors) == 0,
            preservation_checks=checks,
            errors=errors
        )
    
    def _check_property_preservation(self, source: Any, target: Any, 
                                    property_name: str) -> bool:
        """检查属性保持"""
        # 简化的实现
        source_json = json.dumps(source, sort_keys=True, default=str)
        target_json = json.dumps(target, sort_keys=True, default=str)
        
        # 如果源包含某关键信息，目标也应该包含
        return len(target_json) >= len(source_json) * 0.5
    
    def export_mappings(self, filepath: str):
        """导出所有映射记录"""
        data = [
            {
                "success": m.success,
                "source": str(m.source)[:100],
                "target": str(m.target)[:100] if m.target else None,
                "trace": m.trace
            }
            for m in self.mappings
        ]
        
        Path(filepath).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


def main():
    """示例用法"""
    engine = HierarchyMappingEngine()
    
    # 示例1: 集合 → Schema → 本体
    test_set = {"user", "admin", "guest"}
    
    result = engine.map(test_set, MappingLevel.L1_FOUNDATION, MappingLevel.L2_META_MODEL)
    print("=" * 60)
    print("示例1: 集合 → Schema")
    print(f"成功: {result.success}")
    print(f"轨迹: {' -> '.join(result.trace)}")
    if result.target:
        print(f"结果: {json.dumps(result.target, indent=2)[:200]}...")
    
    # 示例2: JSON Schema → OWL
    test_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    result = engine.map(test_schema, MappingLevel.L2_META_MODEL, MappingLevel.L3_DATA_MODEL)
    print("\n" + "=" * 60)
    print("示例2: JSON Schema → OWL")
    print(f"成功: {result.success}")
    print(f"轨迹: {' -> '.join(result.trace)}")
    if result.target:
        print(f"结果: {json.dumps(result.target, indent=2)[:300]}...")
    
    # 示例3: 多级映射
    result = engine.map(test_schema, MappingLevel.L2_META_MODEL, MappingLevel.L5_APPLICATION)
    print("\n" + "=" * 60)
    print("示例3: JSON Schema → Application (多级)")
    print(f"成功: {result.success}")
    print(f"轨迹:")
    for t in result.trace:
        print(f"  {t}")
    
    # 导出
    engine.export_mappings("hierarchy_mappings.json")
    print("\n✅ 映射记录已导出到: hierarchy_mappings.json")


if __name__ == "__main__":
    main()
