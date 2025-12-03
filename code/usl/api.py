"""
USL REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
from .parser import USLParser
from .validator import USLValidator
from .converter import USLToOpenAPIConverter, USLToJSONSchemaConverter

app = FastAPI(title="统一Schema语言API", version="1.0.0")

# 初始化组件
parser = USLParser()


# 请求模型
class ParseRequest(BaseModel):
    usl_code: str


class ConvertRequest(BaseModel):
    usl_code: str
    target_format: str  # 'openapi', 'json_schema'


# 响应模型
class ParseResponse(BaseModel):
    ast: Dict[str, Any]
    parse_time: float


class ValidateResponse(BaseModel):
    valid: bool
    errors: list
    warnings: list
    validation_time: float


class ConvertResponse(BaseModel):
    result: Dict[str, Any]
    convert_time: float


@app.post("/api/v1/usl/parse", response_model=ParseResponse)
async def parse_usl(request: ParseRequest):
    """解析USL代码"""
    start_time = time.time()
    
    try:
        ast = parser.parse(request.usl_code)
        parse_time = time.time() - start_time
        
        return ParseResponse(
            ast=ast,
            parse_time=parse_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败: {str(e)}")


@app.post("/api/v1/usl/validate", response_model=ValidateResponse)
async def validate_usl(request: ParseRequest):
    """验证USL代码"""
    start_time = time.time()
    
    try:
        # 先解析
        ast = parser.parse(request.usl_code)
        
        # 再验证
        validator = USLValidator(ast)
        validation_result = validator.validate()
        
        validation_time = time.time() - start_time
        
        return ValidateResponse(
            valid=validation_result['valid'],
            errors=validation_result['errors'],
            warnings=validation_result['warnings'],
            validation_time=validation_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"验证失败: {str(e)}")


@app.post("/api/v1/usl/convert", response_model=ConvertResponse)
async def convert_usl(request: ConvertRequest):
    """转换USL到其他格式"""
    start_time = time.time()
    
    try:
        # 先解析
        ast = parser.parse(request.usl_code)
        
        # 转换
        if request.target_format == 'openapi':
            converter = USLToOpenAPIConverter(ast)
            result = converter.convert()
        elif request.target_format == 'json_schema':
            converter = USLToJSONSchemaConverter(ast)
            result = converter.convert()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的转换格式: {request.target_format}"
            )
        
        convert_time = time.time() - start_time
        
        return ConvertResponse(
            result=result,
            convert_time=convert_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"转换失败: {str(e)}")


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
