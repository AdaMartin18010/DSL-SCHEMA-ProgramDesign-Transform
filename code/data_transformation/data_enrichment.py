"""
数据丰富化模块

专注于数据增强、数据补全、数据关联
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EnrichmentType(Enum):
    """丰富化类型"""
    LOOKUP = "lookup"  # 查找
    JOIN = "join"  # 关联
    CALCULATE = "calculate"  # 计算
    TRANSFORM = "transform"  # 转换
    EXTERNAL_API = "external_api"  # 外部API


@dataclass
class EnrichmentRule:
    """丰富化规则"""
    rule_id: str
    enrichment_type: EnrichmentType
    source_field: str
    target_field: str
    rule_config: Dict[str, Any]
    enabled: bool = True


class DataEnrichment:
    """
    数据丰富化器
    
    专注于数据增强、数据补全、数据关联
    """
    
    def __init__(self):
        self.rules: Dict[str, EnrichmentRule] = {}
        self.lookup_tables: Dict[str, Dict[str, Any]] = {}
        self.external_apis: Dict[str, Callable] = {}
    
    def add_rule(self, rule_config: Dict[str, Any]) -> EnrichmentRule:
        """
        添加丰富化规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            丰富化规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = EnrichmentRule(
            rule_id=rule_id,
            enrichment_type=EnrichmentType(rule_config.get('enrichment_type', 'lookup')),
            source_field=rule_config['source_field'],
            target_field=rule_config.get('target_field', rule_config['source_field']),
            rule_config=rule_config.get('rule_config', {}),
            enabled=rule_config.get('enabled', True)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def register_lookup_table(self, table_id: str, lookup_data: Dict[str, Any]):
        """
        注册查找表
        
        Args:
            table_id: 表ID
            lookup_data: 查找数据（键值对）
        """
        self.lookup_tables[table_id] = lookup_data
    
    def register_external_api(self, api_id: str, api_func: Callable):
        """
        注册外部API
        
        Args:
            api_id: API ID
            api_func: API函数
        """
        self.external_apis[api_id] = api_func
    
    def enrich_data(self, data: Dict[str, Any],
                   rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        丰富化数据
        
        Args:
            data: 数据字典
            rule_ids: 规则ID列表（可选，默认使用所有规则）
            
        Returns:
            丰富化后的数据
        """
        enriched_data = data.copy()
        
        # 确定要使用的规则
        rules_to_use = rule_ids if rule_ids else list(self.rules.keys())
        
        for rule_id in rules_to_use:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            
            if not rule.enabled:
                continue
            
            # 获取源字段值
            source_value = enriched_data.get(rule.source_field)
            
            if source_value is None:
                continue
            
            # 执行丰富化
            enriched_value = self._apply_enrichment(source_value, rule)
            
            if enriched_value is not None:
                enriched_data[rule.target_field] = enriched_value
        
        return enriched_data
    
    def _apply_enrichment(self, value: Any, rule: EnrichmentRule) -> Any:
        """应用丰富化规则"""
        enrichment_type = rule.enrichment_type
        config = rule.rule_config
        
        if enrichment_type == EnrichmentType.LOOKUP:
            # 查找表丰富化
            table_id = config.get('lookup_table')
            if table_id and table_id in self.lookup_tables:
                lookup_table = self.lookup_tables[table_id]
                return lookup_table.get(value)
            return None
        
        elif enrichment_type == EnrichmentType.JOIN:
            # 关联丰富化
            join_table_id = config.get('join_table')
            join_key = config.get('join_key', rule.source_field)
            
            if join_table_id and join_table_id in self.lookup_tables:
                join_table = self.lookup_tables[join_table_id]
                if isinstance(join_table, dict):
                    return join_table.get(value)
                elif isinstance(join_table, list):
                    # 列表查找
                    for item in join_table:
                        if isinstance(item, dict) and item.get(join_key) == value:
                            return item
            return None
        
        elif enrichment_type == EnrichmentType.CALCULATE:
            # 计算丰富化
            formula = config.get('formula')
            if formula and callable(formula):
                try:
                    return formula(value)
                except Exception as e:
                    logger.warning(f"计算丰富化失败: {e}")
            return None
        
        elif enrichment_type == EnrichmentType.TRANSFORM:
            # 转换丰富化
            transform_func = config.get('transform')
            if transform_func and callable(transform_func):
                try:
                    return transform_func(value)
                except Exception as e:
                    logger.warning(f"转换丰富化失败: {e}")
            return None
        
        elif enrichment_type == EnrichmentType.EXTERNAL_API:
            # 外部API丰富化
            api_id = config.get('api_id')
            if api_id and api_id in self.external_apis:
                api_func = self.external_apis[api_id]
                try:
                    return api_func(value)
                except Exception as e:
                    logger.warning(f"外部API丰富化失败: {e}")
            return None
        
        return None
    
    def batch_enrich(self, data_list: List[Dict[str, Any]],
                    rule_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        批量丰富化数据
        
        Args:
            data_list: 数据列表
            rule_ids: 规则ID列表（可选）
            
        Returns:
            丰富化后的数据列表
        """
        enriched_list = []
        
        for data in data_list:
            enriched_data = self.enrich_data(data, rule_ids)
            enriched_list.append(enriched_data)
        
        return enriched_list
    
    def complete_missing_fields(self, data: Dict[str, Any],
                               completion_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        补全缺失字段
        
        Args:
            data: 数据字典
            completion_rules: 补全规则列表
            
        Returns:
            补全后的数据
        """
        completed_data = data.copy()
        
        for rule in completion_rules:
            field = rule.get('field')
            completion_type = rule.get('type', 'default')
            
            if field in completed_data and completed_data[field] is not None:
                continue  # 字段已存在，跳过
            
            if completion_type == 'default':
                # 使用默认值
                completed_data[field] = rule.get('default_value')
            
            elif completion_type == 'lookup':
                # 使用查找表
                lookup_table_id = rule.get('lookup_table')
                lookup_key = rule.get('lookup_key')
                
                if lookup_table_id and lookup_table_id in self.lookup_tables:
                    lookup_table = self.lookup_tables[lookup_table_id]
                    if lookup_key and lookup_key in data:
                        key_value = data[lookup_key]
                        if isinstance(lookup_table, dict):
                            completed_data[field] = lookup_table.get(key_value)
            
            elif completion_type == 'calculate':
                # 使用计算
                formula = rule.get('formula')
                if formula and callable(formula):
                    try:
                        completed_data[field] = formula(data)
                    except Exception as e:
                        logger.warning(f"计算补全失败: {e}")
        
        return completed_data


def main():
    """主函数 - 示例用法"""
    enrichment = DataEnrichment()
    
    # 注册查找表
    enrichment.register_lookup_table('country_codes', {
        'CN': 'China',
        'US': 'United States',
        'JP': 'Japan'
    })
    
    # 添加丰富化规则
    rule = enrichment.add_rule({
        'source_field': 'country_code',
        'target_field': 'country_name',
        'enrichment_type': 'lookup',
        'rule_config': {
            'lookup_table': 'country_codes'
        }
    })
    
    # 丰富化数据
    data = {
        'country_code': 'CN',
        'city': 'Beijing'
    }
    
    enriched_data = enrichment.enrich_data(data, [rule.rule_id])
    print(f"丰富化后的数据: {enriched_data}")


if __name__ == '__main__':
    main()
