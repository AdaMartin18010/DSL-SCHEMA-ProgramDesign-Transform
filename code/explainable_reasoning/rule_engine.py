"""
基于规则的推理引擎

实现规则匹配和推理
"""

from typing import List, Dict, Any, Optional
from .storage import ExplainableReasoningStorage


class RuleBasedReasoning:
    """基于规则的推理引擎"""
    
    def __init__(self, storage):
        """
        初始化推理引擎
        
        Args:
            storage: 可解释性推理存储管理器
        """
        self.storage = storage
    
    def apply_rule(self, rule: Dict[str, Any], facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        应用规则
        
        Args:
            rule: 规则字典
            facts: 事实字典
            
        Returns:
            推理结果（如果规则匹配）
        """
        # 检查条件是否满足
        if self._check_condition(rule.get('condition', {}), facts):
            # 生成结论
            conclusion = self._generate_conclusion(rule.get('conclusion', {}), facts)
            return {
                'rule_id': rule.get('rule_id'),
                'conclusion': conclusion,
                'confidence': rule.get('confidence', 80)
            }
        return None
    
    def reason(self, query: str, facts: Dict[str, Any],
              rules: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        执行推理
        
        Args:
            query: 查询问题
            facts: 事实字典
            rules: 规则列表（如果为None，则从存储中获取）
            
        Returns:
            推理结果
        """
        if rules is None:
            rules = self.storage.get_all_rules()
        
        # 按优先级排序规则
        sorted_rules = sorted(rules, key=lambda r: r.get('priority', 0), reverse=True)
        
        applied_rules = []
        conclusions = []
        
        for rule in sorted_rules:
            result = self.apply_rule(rule, facts)
            if result:
                applied_rules.append(rule.get('rule_id'))
                conclusions.append(result)
        
        return {
            'query': query,
            'conclusions': conclusions,
            'rules_applied': applied_rules,
            'confidence': self._compute_confidence(conclusions)
        }
    
    def _check_condition(self, condition: Dict[str, Any], facts: Dict[str, Any]) -> bool:
        """检查条件是否满足"""
        # 简化实现：检查所有条件是否在facts中
        for key, value in condition.items():
            if key not in facts or facts[key] != value:
                return False
        return True
    
    def _generate_conclusion(self, conclusion: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
        """生成结论"""
        # 简化实现：直接返回结论模板
        return conclusion
    
    def _compute_confidence(self, conclusions: List[Dict[str, Any]]) -> float:
        """计算总体置信度"""
        if not conclusions:
            return 0.0
        
        confidences = [c.get('confidence', 0) for c in conclusions]
        return sum(confidences) / len(confidences) if confidences else 0.0
