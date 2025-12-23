"""
LLM推理引擎REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import time
from .llm_interface import OpenAILLM, AnthropicLLM, LLMInterface
from .chain_builder import ReasoningChainBuilder
from .validator import ResultValidator

app = FastAPI(title="LLM推理引擎API", version="1.0.0")

# 初始化组件（简化实现，实际应该从配置读取）
llm: Optional[LLMInterface] = None
kg_processor = None  # 知识图谱处理器
chain_builder: Optional[ReasoningChainBuilder] = None
validator: Optional[ResultValidator] = None


class KnowledgeGraphProcessor:
    """知识图谱处理器（简化实现）"""
    
    def __init__(self):
        """初始化知识图谱处理器"""
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: List[Dict[str, Any]] = []
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def search_entities(self, query: str) -> List[Dict[str, Any]]:
        """搜索实体"""
        results = []
        query_lower = query.lower()
        for entity_id, entity in self.entities.items():
            if query_lower in str(entity).lower():
                results.append(entity)
        return results
    
    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取相关实体"""
        related_ids = set()
        for relation in self.relations:
            if relation.get("source") == entity_id:
                related_ids.add(relation.get("target"))
            elif relation.get("target") == entity_id:
                related_ids.add(relation.get("source"))
        
        return [self.entities[eid] for eid in related_ids if eid in self.entities]
    
    def add_entity(self, entity_id: str, entity_data: Dict[str, Any]):
        """添加实体"""
        self.entities[entity_id] = entity_data
    
    def add_relation(self, source: str, target: str, relation_type: str, data: Dict[str, Any] = None):
        """添加关系"""
        self.relations.append({
            "source": source,
            "target": target,
            "type": relation_type,
            "data": data or {}
        })


def initialize_llm(provider: str = "openai"):
    """初始化LLM"""
    global llm, kg_processor, chain_builder, validator
    
    # 初始化知识图谱处理器
    kg_processor = KnowledgeGraphProcessor()
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请设置OPENAI_API_KEY环境变量")
        llm = OpenAILLM(api_key=api_key, model="gpt-4")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("请设置ANTHROPIC_API_KEY环境变量")
        llm = AnthropicLLM(api_key=api_key)
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
    
    chain_builder = ReasoningChainBuilder(kg_processor, llm)
    validator = ResultValidator(kg_processor)


# 请求模型
class ReasoningRequest(BaseModel):
    query: str
    max_steps: int = 5
    llm_model: str = "gpt-4"
    context: Optional[Dict[str, Any]] = None


class ReasoningResponse(BaseModel):
    answer: str
    reasoning_chain: List[Dict[str, Any]]
    confidence: float
    sources: List[str]
    query_time: float
    validation: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    try:
        initialize_llm("openai")
    except Exception as e:
        print(f"LLM初始化失败: {e}")


@app.post("/api/v1/llm-reasoning/query", response_model=ReasoningResponse)
async def llm_reasoning_query(request: ReasoningRequest):
    """LLM推理查询接口"""
    if not llm:
        raise HTTPException(status_code=500, detail="LLM未初始化")
    
    start_time = time.time()
    
    # 构建推理链
    reasoning_chain = chain_builder.build_reasoning_chain(
        request.query, request.max_steps
    )
    
    # 获取最终推理结果
    if reasoning_chain:
        last_step = reasoning_chain[-1]
        if last_step['type'] == 'llm_reasoning':
            result = last_step['result']
            
            # 验证结果
            from .llm_interface import ReasoningResult
            reasoning_result = ReasoningResult(**result)
            validation = validator.validate_result(reasoning_result, request.context or {})
            
            query_time = time.time() - start_time
            
            return ReasoningResponse(
                answer=reasoning_result.answer,
                reasoning_chain=reasoning_chain,
                confidence=reasoning_result.confidence,
                sources=reasoning_result.sources,
                query_time=query_time,
                validation=validation
            )
    
    raise HTTPException(status_code=500, detail="推理失败")


@app.post("/api/v1/llm-reasoning/embed")
async def embed_text(text: str):
    """文本嵌入接口"""
    if not llm:
        raise HTTPException(status_code=500, detail="LLM未初始化")
    
    try:
        embedding = llm.embed(text)
        return {"embedding": embedding, "dimension": len(embedding)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"嵌入失败: {str(e)}")


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "llm_initialized": llm is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
