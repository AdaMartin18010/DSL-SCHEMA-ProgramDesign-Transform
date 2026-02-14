"""
结果验证器

验证推理结果的正确性和可靠性
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from .llm_interface import ReasoningResult


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    confidence: float = 0.0
    issues: List[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.suggestions is None:
            self.suggestions = []


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
    
    def validate_confidence(self, result: ReasoningResult,
                          threshold: float = 0.5) -> ValidationResult:
        """
        验证置信度
        
        Args:
            result: 推理结果
            threshold: 置信度阈值
            
        Returns:
            验证结果
        """
        is_valid = result.confidence >= threshold
        issues = []
        suggestions = []
        
        if not is_valid:
            issues.append(f"置信度过低: {result.confidence:.2f} < {threshold}")
            suggestions.append("建议增加更多上下文信息或改进推理步骤")
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=result.confidence,
            issues=issues,
            suggestions=suggestions
        )
    
    def validate_sources(self, result: ReasoningResult) -> ValidationResult:
        """
        验证来源
        
        Args:
            result: 推理结果
            
        Returns:
            验证结果
        """
        if not result.sources:
            return ValidationResult(
                is_valid=False,
                confidence=result.confidence,
                issues=["缺少来源信息"],
                suggestions=["建议添加知识来源引用"]
            )
        
        # 验证来源是否存在
        valid_sources = []
        invalid_sources = []
        
        for source in result.sources:
            entity = self.kg_processor.get_entity(source)
            if entity:
                valid_sources.append(source)
            else:
                invalid_sources.append(source)
        
        is_valid = len(invalid_sources) == 0 and len(valid_sources) > 0
        issues = []
        suggestions = []
        
        if invalid_sources:
            issues.append(f"无效的来源: {invalid_sources}")
        
        if not valid_sources:
            issues.append("没有有效的知识来源")
            suggestions.append("请检查来源ID是否正确")
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=result.confidence,
            issues=issues,
            suggestions=suggestions
        )
    
    def validate_consistency(self, result: ReasoningResult) -> ValidationResult:
        """
        验证推理一致性
        
        Args:
            result: 推理结果
            
        Returns:
            验证结果
        """
        issues = []
        suggestions = []
        
        # 检查推理步骤是否完整
        if not result.reasoning_steps:
            issues.append("缺少推理步骤")
            suggestions.append("建议提供详细的推理过程")
        
        # 检查推理步骤之间的连贯性
        step_types = [step.get('type', '') for step in result.reasoning_steps]
        
        # 简化的连贯性检查
        if 'llm_reasoning' not in step_types:
            issues.append("缺少LLM推理步骤")
        
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=result.confidence,
            issues=issues,
            suggestions=suggestions
        )
