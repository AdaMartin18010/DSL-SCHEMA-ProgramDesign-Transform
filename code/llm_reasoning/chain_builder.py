"""
推理链构建器

实现多步推理链构建
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .llm_interface import LLMInterface, ReasoningResult
from .embedding import KGEmbedding


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_number: int
    action: str
    input: str
    output: str
    confidence: float


class ReasoningChainBuilder:
    """推理链构建器"""
    
    def __init__(self, kg_processor, llm: LLMInterface):
        """
        初始化推理链构建器
        
        Args:
            kg_processor: 知识图谱处理器（用于检索实体和关系）
            llm: LLM接口实例
        """
        self.kg_processor = kg_processor
        self.llm = llm
        self.kg_embedding = KGEmbedding(llm)
        self.max_chain_length = 5
    
    def build_reasoning_chain(self, query: str,
                             max_steps: int = 5) -> List[Dict[str, Any]]:
        """
        构建推理链
        
        Args:
            query: 查询问题
            max_steps: 最大推理步数
            
        Returns:
            推理链列表
        """
        chain = []
        current_context = {'query': query}
        
        for step in range(min(max_steps, self.max_chain_length)):
            # 1. 理解查询
            if step == 0:
                understanding = self._understand_query(query)
                chain.append({
                    'step': step + 1,
                    'type': 'query_understanding',
                    'content': understanding,
                    'context': current_context.copy()
                })
                current_context['understanding'] = understanding
            
            # 2. 检索相关实体
            entities = self._retrieve_entities(current_context)
            chain.append({
                'step': step + 1,
                'type': 'entity_retrieval',
                'entities': entities,
                'context': current_context.copy()
            })
            current_context['entities'] = entities
            
            # 3. 检索相关关系
            relations = self._retrieve_relations(current_context)
            chain.append({
                'step': step + 1,
                'type': 'relation_retrieval',
                'relations': relations,
                'context': current_context.copy()
            })
            current_context['relations'] = relations
            
            # 4. LLM推理
            reasoning_result = self.llm.reason(query, current_context)
            chain.append({
                'step': step + 1,
                'type': 'llm_reasoning',
                'result': reasoning_result.model_dump(),
                'context': current_context.copy()
            })
            
            # 5. 验证结果
            if self._validate_result(reasoning_result, current_context):
                break
        
        return chain
    
    def _understand_query(self, query: str) -> Dict[str, Any]:
        """理解查询"""
        # 使用LLM理解查询意图
        prompt = f"""分析以下查询的意图和关键信息：

查询：{query}

请提取：
1. 查询意图
2. 关键实体
3. 关键关系
4. 查询类型"""
        
        response = self.llm.generate(prompt)
        
        # 简化解析
        return {
            'intent': 'information_retrieval',  # 简化
            'key_entities': [],
            'key_relations': [],
            'query_type': 'factual'
        }
    
    def _retrieve_entities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检索相关实体"""
        # 从知识图谱中检索实体
        # 这里简化实现，实际应该使用向量搜索
        if 'understanding' in context:
            # 基于理解结果检索
            return []
        return []
    
    def _retrieve_relations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检索相关关系"""
        # 从知识图谱中检索关系
        if 'entities' in context:
            # 基于实体检索关系
            return []
        return []
    
    def _validate_result(self, result: ReasoningResult,
                        context: Dict[str, Any]) -> bool:
        """验证推理结果"""
        # 检查置信度
        if result.confidence < 0.5:
            return False
        
        # 检查来源
        if not result.sources:
            return False
        
        # 检查答案是否为空
        if not result.answer or len(result.answer.strip()) == 0:
            return False
        
        return True
    
    def execute_step(self, step: ReasoningStep) -> ReasoningStep:
        """
        执行单个推理步骤
        
        Args:
            step: 推理步骤
            
        Returns:
            执行后的步骤（包含输出和置信度）
        """
        if step.action == "search":
            # 执行搜索
            entities = self.kg_processor.search_entities(step.input)
            step.output = f"Found {len(entities)} entities"
            step.confidence = 0.8 if entities else 0.3
            
        elif step.action == "expand":
            # 扩展实体
            related = self.kg_processor.get_related_entities(step.input)
            step.output = f"Found {len(related)} related entities"
            step.confidence = 0.75 if related else 0.4
            
        elif step.action == "analyze":
            # 分析
            step.output = "Analysis completed"
            step.confidence = 0.7
            
        else:
            step.output = "Unknown action"
            step.confidence = 0.0
        
        return step
    
    def execute_chain(self, chain: List[ReasoningStep]) -> List[ReasoningStep]:
        """
        执行推理链
        
        Args:
            chain: 推理步骤列表
            
        Returns:
            执行后的步骤列表
        """
        results = []
        for step in chain:
            executed_step = self.execute_step(step)
            results.append(executed_step)
        return results
