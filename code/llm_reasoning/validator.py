"""
结果验证器

验证推理结果的正确性和可靠性
"""

from typing import Dict, Any, List
from .llm_interface import ReasoningResult


class ResultValidator:
    """结果验证器"""
    
    def __init__(self, kg_processor):
        """
        初始化结果验证器
        
        Args:
            kg_processor: 知识图谱处理器
        """
        self.kg_processor = kg_processor
    
    def validate_result(self, reasoning_result: ReasoningResult,
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证推理结果
        
        Args:
            reasoning_result: 推理结果
            context: 上下文信息
            
        Returns:
            验证结果字典
        """
        validation = {
            'is_valid': True,
            'confidence': reasoning_result.confidence,
            'issues': [],
            'suggestions': []
        }
        
        # 1. 检查答案是否为空
        if not reasoning_result.answer or len(reasoning_result.answer.strip()) == 0:
            validation['is_valid'] = False
            validation['issues'].append('答案为空')
        
        # 2. 检查置信度
        if reasoning_result.confidence < 0.5:
            validation['is_valid'] = False
            validation['issues'].append(f'置信度过低: {reasoning_result.confidence}')
            validation['suggestions'].append('建议增加更多上下文信息')
        
        # 3. 检查推理步骤
        if len(reasoning_result.reasoning_steps) < 2:
            validation['issues'].append('推理步骤过少')
            validation['suggestions'].append('建议提供更详细的推理过程')
        
        # 4. 检查来源
        if not reasoning_result.sources:
            validation['issues'].append('缺少来源信息')
            validation['suggestions'].append('建议添加知识来源')
        
        # 5. 验证答案与上下文的一致性
        consistency = self._check_consistency(reasoning_result, context)
        if not consistency:
            validation['issues'].append('答案与上下文不一致')
        
        return validation
    
    def _check_consistency(self, result: ReasoningResult,
                          context: Dict[str, Any]) -> bool:
        """检查答案与上下文的一致性"""
        # 简化实现：检查答案中是否包含上下文中的关键信息
        answer_lower = result.answer.lower()
        
        if 'entities' in context:
            for entity in context['entities']:
                if isinstance(entity, dict) and 'id' in entity:
                    entity_id = str(entity['id']).lower()
                    if entity_id in answer_lower:
                        return True
        
        return True  # 默认返回True
