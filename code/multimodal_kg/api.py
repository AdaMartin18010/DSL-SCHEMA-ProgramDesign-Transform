"""
多模态知识图谱REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
from .text_processor import TextModalityProcessor
from .image_processor import ImageModalityProcessor
from .fusion import MultimodalFusion
from .storage import MultimodalKGStorage

app = FastAPI(title="多模态知识图谱API", version="1.0.0")

# 初始化组件
storage = MultimodalKGStorage()
text_processor = TextModalityProcessor(storage=storage)
image_processor = ImageModalityProcessor(storage=storage)
fusion = MultimodalFusion()


# 请求模型
class TextProcessRequest(BaseModel):
    entity_id: str
    content: str
    content_type: str = "schema_doc"
    metadata: Optional[Dict[str, Any]] = None


class ImageProcessRequest(BaseModel):
    entity_id: str
    image_url: str
    image_type: str = "schema_diagram"
    metadata: Optional[Dict[str, Any]] = None


class MultimodalQueryRequest(BaseModel):
    query_text: Optional[str] = None
    query_image_url: Optional[str] = None
    modality: str = "multimodal"  # 'text', 'image', 'multimodal'
    top_k: int = 10
    fusion_weights: Optional[Dict[str, float]] = None


# 响应模型
class MultimodalQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    query_time: float


@app.post("/api/v1/multimodal/text/process")
async def process_text(request: TextProcessRequest):
    """处理文本并存储"""
    success = text_processor.process_text(
        entity_id=request.entity_id,
        content=request.content,
        content_type=request.content_type,
        metadata=request.metadata
    )
    
    if success:
        return {"status": "success", "entity_id": request.entity_id}
    else:
        raise HTTPException(status_code=500, detail="处理文本失败")


@app.post("/api/v1/multimodal/image/process")
async def process_image(request: ImageProcessRequest):
    """处理图像并存储"""
    success = image_processor.process_image(
        entity_id=request.entity_id,
        image_url=request.image_url,
        image_type=request.image_type,
        metadata=request.metadata
    )
    
    if success:
        return {"status": "success", "entity_id": request.entity_id}
    else:
        raise HTTPException(status_code=500, detail="处理图像失败")


@app.post("/api/v1/multimodal/search", response_model=MultimodalQueryResponse)
async def multimodal_search(request: MultimodalQueryRequest):
    """多模态查询接口"""
    start_time = time.time()
    results = []
    
    if request.modality == 'text' and request.query_text:
        # 文本查询
        results = text_processor.search_similar(
            request.query_text, request.top_k
        )
    
    elif request.modality == 'image' and request.query_image_url:
        # 图像查询
        results = image_processor.search_similar(
            request.query_image_url, request.top_k
        )
    
    elif request.modality == 'multimodal':
        # 多模态融合查询
        if request.query_text and request.query_image_url:
            # 获取文本和图像嵌入
            text_emb = text_processor.model.encode(request.query_text)
            query_image = image_processor.load_image(request.query_image_url)
            image_emb = image_processor.get_embedding(query_image)
            
            # 融合权重
            weights = request.fusion_weights or {'text': 0.5, 'image': 0.5}
            fused_emb = fusion.fuse(
                text_emb, image_emb,
                weights['text'], weights['image']
            )
            
            # 使用融合向量查询
            results = storage.search_fused_similar(
                fused_emb.tolist(), request.top_k
            )
    
    query_time = time.time() - start_time
    
    return MultimodalQueryResponse(
        results=results,
        query_time=query_time
    )


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
