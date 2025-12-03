"""
可解释性推理REST API

基于FastAPI实现REST API接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
from .storage import ExplainableReasoningStorage
from .rule_engine import RuleBasedReasoning
from .path_recorder import ReasoningPathRecorder
from .explanation import ReasoningExplanation
from .visualization import ReasoningVisualization

app = FastAPI(title="可解释性推理API", version="1.0.0")

# 初始化组件
storage = ExplainableReasoningStorage()
rule_engine = RuleBasedReasoning(storage)
path_recorder = ReasoningPathRecorder(storage)
explanation = ReasoningExplanation(storage)
visualization = ReasoningVisualization()


# 请求模型
class ReasoningRequest(BaseModel):
    query: str
    facts: Dict[str, Any]
    rules: Optional[List[Dict[str, Any]]] = None


class RuleRequest(BaseModel):
    rule_id: str
    name: str
    rule_type: str
    condition: Dict[str, Any]
    conclusion: Dict[str, Any]
    confidence: int = 80
    priority: int = 0


# 响应模型
class ReasoningResponse(BaseModel):
    result: Dict[str, Any]
    reasoning_path: Dict[str, Any]
    explanation: Dict[str, Any]
    visualization: Dict[str, Any]
    query_time: float


@app.post("/api/v1/explainable-reasoning/rule/add")
async def add_rule(request: RuleRequest):
    """添加推理规则"""
    success = storage.add_rule(
        rule_id=request.rule_id,
        name=request.name,
        rule_type=request.rule_type,
        condition=request.condition,
        conclusion=request.conclusion,
        confidence=request.confidence,
        priority=request.priority
    )
    
    if success:
        return {"status": "success", "rule_id": request.rule_id}
    else:
        raise HTTPException(status_code=500, detail="添加规则失败")


@app.post("/api/v1/explainable-reasoning/reason", response_model=ReasoningResponse)
async def explainable_reasoning(request: ReasoningRequest):
    """可解释性推理"""
    start_time = time.time()
    
    # 开始记录推理路径
    path_id = path_recorder.start_recording(request.query)
    
    # 执行推理
    result = rule_engine.reason(
        query=request.query,
        facts=request.facts,
        rules=request.rules
    )
    
    # 记录推理步骤（简化实现）
    path_recorder.record_step(
        step_type='rule_application',
        input_data=request.facts,
        output_data=result,
        explanation='应用规则进行推理'
    )
    
    # 完成记录
    path_recorder.finish_recording(
        result=result,
        rules_applied=result.get('rules_applied', []),
        confidence=int(result.get('confidence', 0))
    )
    
    # 获取推理路径
    reasoning_path = path_recorder.get_path(path_id)
    
    # 生成解释
    explanation_result = explanation.explain_result(result, reasoning_path or {})
    
    # 生成可视化
    vis_data = visualization.generate_graph_data(reasoning_path or {})
    
    query_time = time.time() - start_time
    
    return ReasoningResponse(
        result=result,
        reasoning_path=reasoning_path or {},
        explanation=explanation_result,
        visualization=vis_data,
        query_time=query_time
    )


@app.get("/api/v1/explainable-reasoning/path/{path_id}")
async def get_reasoning_path(path_id: str):
    """获取推理路径"""
    path = path_recorder.get_path(path_id)
    
    if path:
        return {
            'path': path,
            'visualization': visualization.generate_graph_data(path),
            'text_explanation': visualization.generate_text_explanation(path)
        }
    else:
        raise HTTPException(status_code=404, detail="推理路径不存在")


@app.get("/api/v1/explainable-reasoning/rules")
async def get_all_rules():
    """获取所有规则"""
    rules = storage.get_all_rules()
    return {"rules": rules, "count": len(rules)}


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
