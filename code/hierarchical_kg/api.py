"""
层次化知识表示REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
from .storage import HierarchicalKGStorage
from .abstraction import KnowledgeAbstraction
from .reasoning import HierarchicalReasoning
from .query import HierarchicalQuery

app = FastAPI(title="层次化知识表示API", version="1.0.0")

# 初始化组件
storage = HierarchicalKGStorage()
abstraction = KnowledgeAbstraction(storage)
reasoning = HierarchicalReasoning(storage)
query = HierarchicalQuery(storage)


# 请求模型
class EntityRequest(BaseModel):
    entity_id: str
    name: str
    level: int
    abstraction_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None


class AbstractionRequest(BaseModel):
    instance_ids: List[str]  # 用于实例到模式抽象
    pattern_ids: Optional[List[str]] = None  # 用于模式到概念抽象


class ReasoningRequest(BaseModel):
    entity_id: str
    reasoning_type: str  # 'bottom_up', 'top_down', 'cross_layer'
    target_level: Optional[int] = None


# 响应模型
class ReasoningResponse(BaseModel):
    reasoning_path: List[Dict[str, Any]]
    query_time: float


@app.post("/api/v1/hierarchical/entity/add")
async def add_entity(request: EntityRequest):
    """添加层次化实体"""
    success = storage.add_entity(
        entity_id=request.entity_id,
        name=request.name,
        level=request.level,
        abstraction_id=request.abstraction_id,
        content=request.content,
        properties=request.properties
    )
    
    if success:
        return {"status": "success", "entity_id": request.entity_id}
    else:
        raise HTTPException(status_code=500, detail="添加实体失败")


@app.post("/api/v1/hierarchical/abstraction/instances-to-pattern")
async def abstract_instances_to_pattern(request: AbstractionRequest):
    """将实例抽象为模式"""
    pattern = abstraction.abstract_instances_to_pattern(request.instance_ids)
    
    if pattern:
        return {"status": "success", "pattern": pattern}
    else:
        raise HTTPException(status_code=500, detail="抽象失败")


@app.post("/api/v1/hierarchical/abstraction/patterns-to-concept")
async def abstract_patterns_to_concept(request: AbstractionRequest):
    """将模式抽象为概念"""
    if not request.pattern_ids:
        raise HTTPException(status_code=400, detail="需要提供pattern_ids")
    
    concept = abstraction.abstract_patterns_to_concept(request.pattern_ids)
    
    if concept:
        return {"status": "success", "concept": concept}
    else:
        raise HTTPException(status_code=500, detail="抽象失败")


@app.post("/api/v1/hierarchical/reasoning", response_model=ReasoningResponse)
async def hierarchical_reasoning(request: ReasoningRequest):
    """层次化推理"""
    start_time = time.time()
    
    if request.reasoning_type == 'bottom_up':
        reasoning_path = reasoning.bottom_up_reasoning(request.entity_id)
    elif request.reasoning_type == 'top_down':
        reasoning_path = reasoning.top_down_reasoning(request.entity_id)
    elif request.reasoning_type == 'cross_layer':
        if request.target_level is None:
            raise HTTPException(status_code=400, detail="需要提供target_level")
        reasoning_path = reasoning.cross_layer_reasoning(
            request.entity_id, request.target_level
        )
    else:
        raise HTTPException(status_code=400, detail="不支持的推理类型")
    
    query_time = time.time() - start_time
    
    return ReasoningResponse(
        reasoning_path=reasoning_path,
        query_time=query_time
    )


@app.get("/api/v1/hierarchical/query/level/{level}")
async def query_by_level(level: int, filters: Optional[Dict[str, Any]] = None):
    """按层次查询"""
    entities = query.query_by_level(level, filters)
    return {"level": level, "entities": entities, "count": len(entities)}


@app.get("/api/v1/hierarchical/query/hierarchy/{entity_id}")
async def query_hierarchy(entity_id: str):
    """查询抽象层次结构"""
    hierarchy = query.query_abstraction_hierarchy(entity_id)
    return hierarchy


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
