"""
统一API网关

整合所有8个核心服务的API接口
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Optional, Dict, Any
import os

app = FastAPI(
    title="DSL Schema统一API网关",
    version="1.0.0",
    description="统一访问所有核心服务的API接口"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服务配置
SERVICES = {
    "multimodal_kg": {
        "url": os.getenv("MULTIMODAL_KG_URL", "http://localhost:8000"),
        "name": "多模态知识图谱",
        "health": "/api/v1/health"
    },
    "temporal_kg": {
        "url": os.getenv("TEMPORAL_KG_URL", "http://localhost:8001"),
        "name": "时序知识图谱",
        "health": "/api/v1/health"
    },
    "llm_reasoning": {
        "url": os.getenv("LLM_REASONING_URL", "http://localhost:8002"),
        "name": "LLM推理引擎",
        "health": "/api/v1/health"
    },
    "usl": {
        "url": os.getenv("USL_URL", "http://localhost:8003"),
        "name": "统一Schema语言",
        "health": "/api/v1/health"
    },
    "hierarchical_kg": {
        "url": os.getenv("HIERARCHICAL_KG_URL", "http://localhost:8004"),
        "name": "层次化知识表示",
        "health": "/api/v1/health"
    },
    "knowledge_chain": {
        "url": os.getenv("KNOWLEDGE_CHAIN_URL", "http://localhost:8005"),
        "name": "知识链方法",
        "health": "/api/v1/health"
    },
    "explainable_reasoning": {
        "url": os.getenv("EXPLAINABLE_REASONING_URL", "http://localhost:8006"),
        "name": "可解释性推理",
        "health": "/api/v1/health"
    },
    "schema_versioning": {
        "url": os.getenv("SCHEMA_VERSIONING_URL", "http://localhost:8007"),
        "name": "Schema版本管理",
        "health": "/api/v1/health"
    }
}


async def forward_request(service_name: str, path: str, method: str = "GET",
                         data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    转发请求到指定服务
    
    Args:
        service_name: 服务名称
        path: 请求路径
        method: HTTP方法
        data: 请求数据
        
    Returns:
        响应数据
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")
    
    service = SERVICES[service_name]
    url = f"{service['url']}{path}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                raise HTTPException(status_code=405, detail=f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"服务 {service_name} 请求失败: {str(e)}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "DSL Schema统一API网关",
        "version": "1.0.0",
        "services": {name: info["name"] for name, info in SERVICES.items()}
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    health_status = {}
    
    for service_name, service_info in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_info['url']}{service_info['health']}")
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_info['url']
                }
        except Exception as e:
            health_status[service_name] = {
                "status": "unhealthy",
                "error": str(e),
                "url": service_info['url']
            }
    
    all_healthy = all(status["status"] == "healthy" for status in health_status.values())
    
    return {
        "gateway": "healthy",
        "services": health_status,
        "overall": "healthy" if all_healthy else "degraded"
    }


@app.get("/api/v1/services")
async def list_services():
    """列出所有服务"""
    return {
        "services": [
            {
                "name": name,
                "display_name": info["name"],
                "url": info["url"],
                "health_endpoint": info["health"]
            }
            for name, info in SERVICES.items()
        ]
    }


@app.api_route("/api/v1/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service_name: str, path: str, request: Request):
    """代理请求到指定服务"""
    method = request.method
    data = None
    
    if method in ["POST", "PUT"]:
        try:
            data = await request.json()
        except:
            pass
    
    result = await forward_request(service_name, f"/api/v1/{path}", method, data)
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
