"""
LLM接口抽象

支持多种LLM提供商（OpenAI、Claude等）
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ReasoningResult(BaseModel):
    """推理结果模型"""
    answer: str
    reasoning_steps: List[Dict[str, Any]]
    confidence: float
    sources: List[str]


class LLMInterface(ABC):
    """LLM接口抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        生成嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        pass
    
    @abstractmethod
    def reason(self, query: str, context: Dict[str, Any]) -> ReasoningResult:
        """
        执行推理
        
        Args:
            query: 查询问题
            context: 上下文信息
            
        Returns:
            推理结果
        """
        pass


class OpenAILLM(LLMInterface):
    """OpenAI LLM实现"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        初始化OpenAI LLM
        
        Args:
            api_key: OpenAI API密钥
            model: 模型名称（gpt-4, gpt-3.5-turbo等）
        """
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        return response.choices[0].message.content
    
    def embed(self, text: str) -> List[float]:
        """生成嵌入向量"""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    def reason(self, query: str, context: Dict[str, Any]) -> ReasoningResult:
        """执行推理"""
        # 构建提示词
        prompt = self._build_reasoning_prompt(query, context)
        
        # 调用LLM
        response = self.generate(prompt, temperature=0.7)
        
        # 解析结果
        return self._parse_reasoning_result(response, context)
    
    def _build_reasoning_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """构建推理提示词"""
        prompt = f"""基于以下上下文信息，回答查询问题。

上下文信息：
{self._format_context(context)}

查询问题：{query}

请提供详细的推理过程和答案。"""
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文"""
        formatted = []
        if 'entities' in context:
            formatted.append(f"相关实体：{context['entities']}")
        if 'relations' in context:
            formatted.append(f"相关关系：{context['relations']}")
        if 'subgraph' in context:
            formatted.append(f"子图信息：{context['subgraph']}")
        return "\n".join(formatted)
    
    def _parse_reasoning_result(self, response: str, context: Dict[str, Any]) -> ReasoningResult:
        """解析推理结果"""
        # 简化实现：提取答案和推理步骤
        lines = response.split('\n')
        answer = lines[0] if lines else response
        
        reasoning_steps = []
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                reasoning_steps.append({
                    'step': i,
                    'content': line.strip()
                })
        
        # 计算置信度（简化实现）
        confidence = min(0.9, 0.5 + len(reasoning_steps) * 0.1)
        
        # 提取来源
        sources = context.get('sources', [])
        
        return ReasoningResult(
            answer=answer,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            sources=sources
        )


class AnthropicLLM(LLMInterface):
    """Anthropic Claude LLM实现"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """
        初始化Anthropic LLM
        
        Args:
            api_key: Anthropic API密钥
            model: 模型名称
        """
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("请安装anthropic库: pip install anthropic")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        return message.content[0].text
    
    def embed(self, text: str) -> List[float]:
        """生成嵌入向量（Claude不支持嵌入，使用OpenAI）"""
        # Claude不支持嵌入，这里返回空向量或使用OpenAI
        raise NotImplementedError("Claude不支持嵌入，请使用OpenAI")
    
    def reason(self, query: str, context: Dict[str, Any]) -> ReasoningResult:
        """执行推理"""
        # 构建提示词
        prompt = self._build_reasoning_prompt(query, context)
        
        # 调用LLM
        response = self.generate(prompt)
        
        # 解析结果
        return self._parse_reasoning_result(response, context)
    
    def _build_reasoning_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """构建推理提示词"""
        prompt = f"""基于以下上下文信息，回答查询问题。

上下文信息：
{self._format_context(context)}

查询问题：{query}

请提供详细的推理过程和答案。"""
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文"""
        formatted = []
        if 'entities' in context:
            formatted.append(f"相关实体：{context['entities']}")
        if 'relations' in context:
            formatted.append(f"相关关系：{context['relations']}")
        return "\n".join(formatted)
    
    def _parse_reasoning_result(self, response: str, context: Dict[str, Any]) -> ReasoningResult:
        """解析推理结果"""
        lines = response.split('\n')
        answer = lines[0] if lines else response
        
        reasoning_steps = []
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                reasoning_steps.append({
                    'step': i,
                    'content': line.strip()
                })
        
        confidence = min(0.9, 0.5 + len(reasoning_steps) * 0.1)
        sources = context.get('sources', [])
        
        return ReasoningResult(
            answer=answer,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            sources=sources
        )
