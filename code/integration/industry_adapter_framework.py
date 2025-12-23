"""
跨行业Schema转换适配器框架

支持不同行业Schema之间的转换
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IndustryType(Enum):
    """行业类型"""
    FINANCE = "finance"  # 金融
    HEALTHCARE = "healthcare"  # 医疗
    IOT = "iot"  # 物联网
    MANUFACTURING = "manufacturing"  # 制造业
    RETAIL = "retail"  # 零售
    ENERGY = "energy"  # 能源
    TRANSPORTATION = "transportation"  # 交通
    EDUCATION = "education"  # 教育


class SchemaFormat(Enum):
    """Schema格式"""
    OPENAPI = "openapi"
    ASYNCAPI = "asyncapi"
    IOT = "iot"
    SWIFT = "swift"
    FHIR = "fhir"
    EDI = "edi"
    CUSTOM = "custom"


@dataclass
class IndustryAdapter:
    """行业适配器"""
    adapter_id: str
    industry_type: IndustryType
    source_format: SchemaFormat
    target_format: SchemaFormat
    to_universal_func: Callable
    from_universal_func: Callable
    validate_func: Callable
    enabled: bool = True
    created_at: datetime = None


@dataclass
class ConversionRule:
    """转换规则"""
    rule_id: str
    rule_name: str
    rule_type: str  # type_mapping, semantic, constraint, format
    source_pattern: Dict[str, Any]
    target_pattern: Dict[str, Any]
    conditions: Dict[str, Any] = None
    priority: int = 0
    enabled: bool = True
    created_at: datetime = None


class IndustryAdapterFramework:
    """行业适配器框架"""
    
    def __init__(self):
        """初始化行业适配器框架"""
        self.adapters: Dict[str, IndustryAdapter] = {}
        self.rules: Dict[str, ConversionRule] = {}
        self.rule_library: Dict[str, List[str]] = {}  # rule_type -> rule_ids
        self.framework_config: Dict[str, Any] = {}
    
    def register_adapter(
        self,
        industry_type: IndustryType,
        source_format: SchemaFormat,
        target_format: SchemaFormat,
        to_universal_func: Callable,
        from_universal_func: Callable,
        validate_func: Callable
    ) -> IndustryAdapter:
        """注册行业适配器"""
        adapter_id = f"adapter_{industry_type.value}_{source_format.value}_to_{target_format.value}"
        
        adapter = IndustryAdapter(
            adapter_id=adapter_id,
            industry_type=industry_type,
            source_format=source_format,
            target_format=target_format,
            to_universal_func=to_universal_func,
            from_universal_func=from_universal_func,
            validate_func=validate_func,
            created_at=datetime.now()
        )
        
        self.adapters[adapter_id] = adapter
        logger.info(f"注册行业适配器: {adapter_id}")
        
        return adapter
    
    def add_conversion_rule(
        self,
        rule_name: str,
        rule_type: str,
        source_pattern: Dict[str, Any],
        target_pattern: Dict[str, Any],
        conditions: Dict[str, Any] = None,
        priority: int = 0
    ) -> ConversionRule:
        """添加转换规则"""
        rule_id = f"rule_{hash(rule_name) % 10000:04d}"
        
        rule = ConversionRule(
            rule_id=rule_id,
            rule_name=rule_name,
            rule_type=rule_type,
            source_pattern=source_pattern,
            target_pattern=target_pattern,
            conditions=conditions or {},
            priority=priority,
            created_at=datetime.now()
        )
        
        self.rules[rule_id] = rule
        
        # 添加到规则库
        if rule_type not in self.rule_library:
            self.rule_library[rule_type] = []
        self.rule_library[rule_type].append(rule_id)
        
        logger.info(f"添加转换规则: {rule_name} ({rule_id})")
        
        return rule
    
    def convert_between_industries(
        self,
        source_schema: Dict[str, Any],
        source_industry: IndustryType,
        source_format: SchemaFormat,
        target_industry: IndustryType,
        target_format: SchemaFormat
    ) -> Dict[str, Any]:
        """跨行业转换"""
        # 步骤1：源行业 -> 通用Schema
        source_adapter_id = f"adapter_{source_industry.value}_{source_format.value}_to_openapi"
        if source_adapter_id not in self.adapters:
            raise ValueError(f"源适配器不存在: {source_adapter_id}")
        
        source_adapter = self.adapters[source_adapter_id]
        
        # 验证源Schema
        if not source_adapter.validate_func(source_schema):
            raise ValueError("源Schema验证失败")
        
        # 转换为通用Schema
        universal_schema = source_adapter.to_universal_func(source_schema)
        
        # 步骤2：通用Schema -> 目标行业
        target_adapter_id = f"adapter_{target_industry.value}_openapi_to_{target_format.value}"
        if target_adapter_id not in self.adapters:
            raise ValueError(f"目标适配器不存在: {target_adapter_id}")
        
        target_adapter = self.adapters[target_adapter_id]
        
        # 从通用Schema转换
        target_schema = target_adapter.from_universal_func(universal_schema)
        
        logger.info(
            f"跨行业转换完成: {source_industry.value} -> {target_industry.value}"
        )
        
        return target_schema
    
    def apply_conversion_rules(
        self,
        schema: Dict[str, Any],
        rule_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """应用转换规则"""
        result_schema = schema.copy()
        
        # 获取适用的规则
        applicable_rules = []
        if rule_type:
            rule_ids = self.rule_library.get(rule_type, [])
        else:
            rule_ids = list(self.rules.keys())
        
        for rule_id in rule_ids:
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                if rule.enabled and self._rule_matches(rule, result_schema):
                    applicable_rules.append(rule)
        
        # 按优先级排序
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        # 应用规则
        for rule in applicable_rules:
            result_schema = self._apply_rule(rule, result_schema)
        
        return result_schema
    
    def _rule_matches(self, rule: ConversionRule, schema: Dict[str, Any]) -> bool:
        """检查规则是否匹配"""
        # 简化实现：检查源模式是否匹配
        return self._pattern_matches(rule.source_pattern, schema)
    
    def _pattern_matches(self, pattern: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """检查模式是否匹配"""
        # 简化实现
        for key, value in pattern.items():
            if key not in schema:
                return False
            if isinstance(value, dict) and isinstance(schema[key], dict):
                if not self._pattern_matches(value, schema[key]):
                    return False
            elif value != schema[key]:
                return False
        return True
    
    def _apply_rule(self, rule: ConversionRule, schema: Dict[str, Any]) -> Dict[str, Any]:
        """应用规则"""
        # 简化实现：直接替换匹配的部分
        result = schema.copy()
        
        # 查找匹配的位置并应用目标模式
        self._replace_pattern(result, rule.source_pattern, rule.target_pattern)
        
        return result
    
    def _replace_pattern(
        self,
        obj: Dict[str, Any],
        source_pattern: Dict[str, Any],
        target_pattern: Dict[str, Any]
    ):
        """替换模式"""
        # 简化实现
        for key, value in source_pattern.items():
            if key in obj:
                if isinstance(value, dict) and isinstance(obj[key], dict):
                    self._replace_pattern(obj[key], value, target_pattern.get(key, {}))
                elif key in target_pattern:
                    obj[key] = target_pattern[key]
    
    def get_adapter_list(self) -> List[Dict[str, Any]]:
        """获取适配器列表"""
        return [
            {
                "adapter_id": adapter.adapter_id,
                "industry_type": adapter.industry_type.value,
                "source_format": adapter.source_format.value,
                "target_format": adapter.target_format.value,
                "enabled": adapter.enabled
            }
            for adapter in self.adapters.values()
        ]
    
    def get_rule_library_summary(self) -> Dict[str, Any]:
        """获取规则库摘要"""
        return {
            "total_rules": len(self.rules),
            "rules_by_type": {
                rule_type: len(rule_ids)
                for rule_type, rule_ids in self.rule_library.items()
            },
            "enabled_rules": len([
                r for r in self.rules.values() if r.enabled
            ])
        }
