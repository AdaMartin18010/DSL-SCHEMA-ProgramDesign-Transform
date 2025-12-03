"""
推理结果解释

生成推理结果的解释说明
"""

from typing import Dict, Any, List


class ReasoningExplanation:
    """推理结果解释器"""
    
    def __init__(self, storage):
        """
        初始化解释器
        
        Args:
            storage: 可解释性推理存储管理器
        """
        self.storage = storage
    
    def explain_result(self, reasoning_result: Dict[str, Any],
                      reasoning_path: Dict[str, Any]) -> Dict[str, Any]:
        """
        解释推理结果
        
        Args:
            reasoning_result: 推理结果
            reasoning_path: 推理路径
            
        Returns:
            解释字典
        """
        explanation = {
            'summary': self._generate_summary(reasoning_result, reasoning_path),
            'steps': self._explain_steps(reasoning_path.get('steps', [])),
            'rules': self._explain_rules(reasoning_path.get('rules_applied', [])),
            'confidence': self._explain_confidence(reasoning_result.get('confidence', 0))
        }
        
        return explanation
    
    def _generate_summary(self, result: Dict[str, Any],
                         path: Dict[str, Any]) -> str:
        """生成总结"""
        query = path.get('query', '')
        conclusions = result.get('conclusions', [])
        rules_count = len(path.get('rules_applied', []))
        
        summary = f"对于查询'{query}'，应用了{rules_count}条规则，"
        summary += f"得出{len(conclusions)}个结论。"
        
        return summary
    
    def _explain_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解释推理步骤"""
        explanations = []
        
        for i, step in enumerate(steps, 1):
            explanation = {
                'step_number': i,
                'type': step.get('type', 'unknown'),
                'description': self._describe_step(step),
                'explanation': step.get('explanation', '')
            }
            explanations.append(explanation)
        
        return explanations
    
    def _explain_rules(self, rule_ids: List[str]) -> List[Dict[str, Any]]:
        """解释应用的规则"""
        rules = self.storage.get_all_rules()
        rule_dict = {r['rule_id']: r for r in rules}
        
        explanations = []
        for rule_id in rule_ids:
            if rule_id in rule_dict:
                rule = rule_dict[rule_id]
                explanations.append({
                    'rule_id': rule_id,
                    'name': rule.get('name', 'Unknown Rule'),
                    'description': f"应用规则：{rule.get('name')}"
                })
        
        return explanations
    
    def _explain_confidence(self, confidence: float) -> str:
        """解释置信度"""
        if confidence >= 80:
            return f"高置信度（{confidence}%），结果可靠"
        elif confidence >= 60:
            return f"中等置信度（{confidence}%），结果较为可靠"
        else:
            return f"低置信度（{confidence}%），结果需要进一步验证"
    
    def _describe_step(self, step: Dict[str, Any]) -> str:
        """描述推理步骤"""
        step_type = step.get('type', 'unknown')
        
        if step_type == 'rule_application':
            return f"应用规则：{step.get('rule_id', 'unknown')}"
        elif step_type == 'fact_retrieval':
            return "检索事实"
        elif step_type == 'inference':
            return "执行推理"
        else:
            return f"执行{step_type}操作"
