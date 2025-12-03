"""
知识链方法REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
from .storage import KnowledgeChainStorage
from .extraction import LowLevelKnowledgeExtractor
from .abstraction import HighLevelConceptAbstraction
from .builder import KnowledgeChainBuilder
from .reasoning import KnowledgeChainReasoning

app = FastAPI(title="知识链方法API", version="1.0.0")

# 初始化组件
storage = KnowledgeChainStorage()
extractor = LowLevelKnowledgeExtractor(storage)
abstraction = HighLevelConceptAbstraction(storage)
builder = KnowledgeChainBuilder(storage)
reasoning = KnowledgeChainReasoning(storage)


# 请求模型
class BuildChainRequest(BaseModel):
    schema_doc: Dict[str, Any]
    chain_name: str


class ReasoningRequest(BaseModel):
    chain_id: str
    reasoning_type: str  # 'bottom_up', 'top_down'


# 响应模型
class ReasoningResponse(BaseModel):
    reasoning_path: List[Dict[str, Any]]
    query_time: float


@app.post("/api/v1/knowledge-chain/build")
async def build_chain(request: BuildChainRequest):
    """构建知识链"""
    chain = builder.build_chain(request.schema_doc, request.chain_name)
    
    if chain:
        return {"status": "success", "chain": chain}
    else:
        raise HTTPException(status_code=500, detail="构建知识链失败")


@app.post("/api/v1/knowledge-chain/reasoning", response_model=ReasoningResponse)
async def knowledge_chain_reasoning(request: ReasoningRequest):
    """知识链推理"""
    start_time = time.time()
    
    if request.reasoning_type == 'bottom_up':
        reasoning_path = reasoning.bottom_up_reasoning(request.chain_id)
    elif request.reasoning_type == 'top_down':
        reasoning_path = reasoning.top_down_reasoning(request.chain_id)
    else:
        raise HTTPException(status_code=400, detail="不支持的推理类型")
    
    query_time = time.time() - start_time
    
    return ReasoningResponse(
        reasoning_path=reasoning_path,
        query_time=query_time
    )


@app.get("/api/v1/knowledge-chain/{chain_id}")
async def get_chain(chain_id: str):
    """获取知识链"""
    chain = storage.get_chain(chain_id)
    
    if chain:
        return chain
    else:
        raise HTTPException(status_code=404, detail="知识链不存在")


@app.get("/api/v1/knowledge-chain/nodes/level/{level}")
async def get_nodes_by_level(level: int):
    """获取指定层次的节点"""
    nodes = storage.get_nodes_by_level(level)
    return {"level": level, "nodes": nodes, "count": len(nodes)}


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
