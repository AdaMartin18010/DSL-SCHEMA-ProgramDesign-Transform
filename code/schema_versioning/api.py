"""
Schema版本管理REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
from .storage import SchemaVersioningStorage
from .version_control import SchemaVersionControl
from .evolution_tracker import SchemaEvolutionTracker
from .compatibility import CompatibilityChecker
from .migration import SchemaMigrationTool

app = FastAPI(title="Schema版本管理API", version="1.0.0")

# 初始化组件
storage = SchemaVersioningStorage()
version_control = SchemaVersionControl(storage)
evolution_tracker = SchemaEvolutionTracker(storage)
compatibility_checker = CompatibilityChecker(storage)
migration_tool = SchemaMigrationTool(storage)


# 请求模型
class CreateVersionRequest(BaseModel):
    schema_id: str
    schema_content: Dict[str, Any]
    version: Optional[str] = None
    changelog: Optional[str] = None


class MigrationRequest(BaseModel):
    schema_id: str
    from_version: str
    to_version: str
    data: Dict[str, Any]


class CompatibilityCheckRequest(BaseModel):
    schema_id: str
    from_version: str
    to_version: str


# 响应模型
class CompatibilityResponse(BaseModel):
    is_compatible: int
    compatibility_level: str
    breaking_changes: list
    differences: Dict[str, Any]
    query_time: float


@app.post("/api/v1/schema-versioning/version/create")
async def create_version(request: CreateVersionRequest):
    """创建Schema版本"""
    version = version_control.create_version(
        schema_id=request.schema_id,
        schema_content=request.schema_content,
        version=request.version,
        changelog=request.changelog
    )
    
    if version:
        return {"status": "success", "version": version}
    else:
        raise HTTPException(status_code=500, detail="创建版本失败")


@app.get("/api/v1/schema-versioning/version/{schema_id}")
async def get_current_version(schema_id: str):
    """获取当前版本"""
    version = version_control.get_version(schema_id)
    
    if version:
        return version
    else:
        raise HTTPException(status_code=404, detail="Schema不存在")


@app.get("/api/v1/schema-versioning/versions/{schema_id}")
async def list_versions(schema_id: str):
    """列出所有版本"""
    versions = version_control.list_versions(schema_id)
    return {"schema_id": schema_id, "versions": versions, "count": len(versions)}


@app.post("/api/v1/schema-versioning/compatibility/check", response_model=CompatibilityResponse)
async def check_compatibility(request: CompatibilityCheckRequest):
    """检查兼容性"""
    start_time = time.time()
    
    result = compatibility_checker.check_compatibility(
        schema_id=request.schema_id,
        from_version=request.from_version,
        to_version=request.to_version
    )
    
    query_time = time.time() - start_time
    
    return CompatibilityResponse(
        is_compatible=result.get('is_compatible', 0),
        compatibility_level=result.get('compatibility_level', 'unknown'),
        breaking_changes=result.get('breaking_changes', []),
        differences=result.get('differences', {}),
        query_time=query_time
    )


@app.post("/api/v1/schema-versioning/migration/migrate")
async def migrate_schema(request: MigrationRequest):
    """执行Schema迁移"""
    result = migration_tool.migrate(
        schema_id=request.schema_id,
        from_version=request.from_version,
        to_version=request.to_version,
        data=request.data
    )
    
    if result.get('success'):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get('error', '迁移失败'))


@app.get("/api/v1/schema-versioning/migration/script/{schema_id}")
async def get_migration_script(schema_id: str, from_version: str, to_version: str):
    """获取迁移脚本"""
    script = migration_tool.generate_migration_script(
        schema_id=schema_id,
        from_version=from_version,
        to_version=to_version
    )
    
    return {"script": script}


@app.get("/api/v1/schema-versioning/evolution/{schema_id}")
async def get_evolution_history(schema_id: str):
    """获取演化历史"""
    history = evolution_tracker.get_evolution_history(schema_id)
    return {"schema_id": schema_id, "evolution_history": history}


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
