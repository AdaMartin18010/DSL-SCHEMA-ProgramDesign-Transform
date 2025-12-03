"""
时序知识图谱REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import time
from .storage import TemporalKGStorage
from .evolution import TemporalEvolutionTracker
from .reasoning import TemporalReasoning

app = FastAPI(title="时序知识图谱API", version="1.0.0")

# 初始化组件
storage = TemporalKGStorage()
evolution_tracker = TemporalEvolutionTracker(storage)
reasoning = TemporalReasoning(storage)


# 请求模型
class TemporalEntityRequest(BaseModel):
    entity_id: str
    entity_type: str
    valid_from: datetime
    valid_to: Optional[datetime] = None
    properties: Optional[Dict[str, Any]] = None


class TemporalQueryRequest(BaseModel):
    entity_id: Optional[str] = None
    query_time: datetime
    relation_type: Optional[str] = None
    time_range: Optional[Dict[str, datetime]] = None


class EvolutionTrackRequest(BaseModel):
    entity_id: str
    start_time: datetime
    end_time: datetime


# 响应模型
class TemporalQueryResponse(BaseModel):
    entities: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    query_time: float


@app.post("/api/v1/temporal/entity/add")
async def add_entity(request: TemporalEntityRequest):
    """添加时序实体"""
    success = storage.add_entity(
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        valid_from=request.valid_from,
        valid_to=request.valid_to,
        properties=request.properties
    )
    
    if success:
        return {"status": "success", "entity_id": request.entity_id}
    else:
        raise HTTPException(status_code=500, detail="添加实体失败")


@app.post("/api/v1/temporal/entity/update")
async def update_entity(entity_id: str, new_properties: Dict[str, Any],
                       update_time: datetime):
    """更新实体（创建新版本）"""
    success = storage.update_entity(
        entity_id=entity_id,
        new_properties=new_properties,
        update_time=update_time
    )
    
    if success:
        return {"status": "success", "entity_id": entity_id}
    else:
        raise HTTPException(status_code=500, detail="更新实体失败")


@app.post("/api/v1/temporal/query", response_model=TemporalQueryResponse)
async def temporal_query(request: TemporalQueryRequest):
    """时间查询接口"""
    start_time = time.time()
    entities = []
    relations = []
    
    if request.entity_id:
        # 查询特定实体在时间点的状态
        entity = storage.get_entity_at_time(
            request.entity_id, request.query_time
        )
        if entity:
            entities.append(entity)
    
    if request.time_range:
        # 时间区间查询（待实现）
        pass
    
    query_time = time.time() - start_time
    
    return TemporalQueryResponse(
        entities=entities,
        relations=relations,
        query_time=query_time
    )


@app.post("/api/v1/temporal/evolution/track")
async def track_evolution(request: EvolutionTrackRequest):
    """追踪实体演化"""
    evolution = evolution_tracker.track_entity_evolution(
        entity_id=request.entity_id,
        start_time=request.start_time,
        end_time=request.end_time
    )
    
    return {"entity_id": request.entity_id, "evolution": evolution}


@app.post("/api/v1/temporal/reasoning/infer")
async def infer_temporal_relations(entity1_id: str, entity2_id: str,
                                  query_time: datetime):
    """推理时间关系"""
    relations = reasoning.infer_temporal_relations(
        entity1_id=entity1_id,
        entity2_id=entity2_id,
        query_time=query_time
    )
    
    if relations:
        return {"relations": relations}
    else:
        raise HTTPException(status_code=404, detail="无法推理时间关系")


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
