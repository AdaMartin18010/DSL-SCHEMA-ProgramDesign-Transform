"""
AI驱动的Schema转换系统

使用AI模型进行Schema转换，支持多种AI模型和提示工程
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AIModel(Enum):
    """AI模型"""
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    GEMINI_PRO = "gemini-pro"
    CUSTOM = "custom"


class PromptStrategy(Enum):
    """提示策略"""
    ZERO_SHOT = "zero_shot"  # 零样本
    FEW_SHOT = "few_shot"  # 少样本
    CHAIN_OF_THOUGHT = "chain_of_thought"  # 链式思考
    VERIFICATION_FEEDBACK = "verification_feedback"  # 验证反馈


@dataclass
class TransformationRequest:
    """转换请求"""
    request_id: str
    source_schema: Dict[str, Any]
    source_format: str
    target_format: str
    ai_model: AIModel
    prompt_strategy: PromptStrategy
    requirements: List[str] = None
    examples: List[Dict[str, Any]] = None
    timestamp: datetime = None


@dataclass
class TransformationResult:
    """转换结果"""
    result_id: str
    request_id: str
    target_schema: Dict[str, Any]
    confidence: float
    execution_time: float
    model_used: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = None


@dataclass
class PromptTemplate:
    """提示模板"""
    template_id: str
    template_name: str
    source_format: str
    target_format: str
    template: str
    strategy: PromptStrategy
    examples: List[Dict[str, Any]] = None
    created_at: datetime = None


class AIDrivenTransformation:
    """AI驱动的Schema转换系统"""
    
    def __init__(self):
        """初始化AI驱动转换系统"""
        self.models: Dict[str, Any] = {}  # AI模型实例
        self.prompt_templates: Dict[str, PromptTemplate] = {}
        self.transformation_history: List[TransformationResult] = []
        self.ai_config: Dict[str, Any] = {}
    
    def register_model(
        self,
        model: AIModel,
        model_instance: Any,
        config: Dict[str, Any] = None
    ):
        """注册AI模型"""
        self.models[model.value] = {
            "instance": model_instance,
            "config": config or {}
        }
        logger.info(f"注册AI模型: {model.value}")
    
    def create_prompt_template(
        self,
        template_name: str,
        source_format: str,
        target_format: str,
        template: str,
        strategy: PromptStrategy,
        examples: List[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """创建提示模板"""
        template_id = f"template_{hash(template_name) % 10000:04d}"
        
        prompt_template = PromptTemplate(
            template_id=template_id,
            template_name=template_name,
            source_format=source_format,
            target_format=target_format,
            template=template,
            strategy=strategy,
            examples=examples or [],
            created_at=datetime.now()
        )
        
        self.prompt_templates[template_id] = prompt_template
        logger.info(f"创建提示模板: {template_name} ({template_id})")
        
        return prompt_template
    
    def transform_with_ai(
        self,
        source_schema: Dict[str, Any],
        source_format: str,
        target_format: str,
        ai_model: AIModel = AIModel.GPT_4,
        prompt_strategy: PromptStrategy = PromptStrategy.FEW_SHOT,
        requirements: List[str] = None,
        examples: List[Dict[str, Any]] = None
    ) -> TransformationResult:
        """使用AI进行转换"""
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        # 创建转换请求
        request = TransformationRequest(
            request_id=request_id,
            source_schema=source_schema,
            source_format=source_format,
            target_format=target_format,
            ai_model=ai_model,
            prompt_strategy=prompt_strategy,
            requirements=requirements or [],
            examples=examples or [],
            timestamp=start_time
        )
        
        try:
            # 生成提示
            prompt = self._generate_prompt(request)
            
            # 调用AI模型
            if ai_model.value not in self.models:
                raise ValueError(f"AI模型未注册: {ai_model.value}")
            
            model_info = self.models[ai_model.value]
            model_instance = model_info["instance"]
            
            # 执行转换（简化实现）
            target_schema = self._call_ai_model(
                model_instance, prompt, model_info["config"]
            )
            
            # 验证结果
            confidence = self._calculate_confidence(source_schema, target_schema)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = TransformationResult(
                result_id=f"result_{request_id}",
                request_id=request_id,
                target_schema=target_schema,
                confidence=confidence,
                execution_time=execution_time,
                model_used=ai_model.value,
                success=True,
                timestamp=datetime.now()
            )
            
            self.transformation_history.append(result)
            logger.info(f"AI转换完成: {request_id} - 置信度: {confidence:.2%}")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = TransformationResult(
                result_id=f"result_{request_id}",
                request_id=request_id,
                target_schema={},
                confidence=0.0,
                execution_time=execution_time,
                model_used=ai_model.value,
                success=False,
                error=str(e),
                timestamp=datetime.now()
            )
            
            self.transformation_history.append(result)
            logger.error(f"AI转换失败: {request_id} - {str(e)}")
            
            return result
    
    def _generate_prompt(self, request: TransformationRequest) -> str:
        """生成提示"""
        # 查找或创建提示模板
        template = self._find_template(
            request.source_format, request.target_format, request.prompt_strategy
        )
        
        if template:
            prompt = template.template.format(
                source_format=request.source_format,
                target_format=request.target_format,
                schema_content=self._format_schema(request.source_schema),
                requirements="\n".join(f"- {req}" for req in request.requirements),
                examples=self._format_examples(request.examples or template.examples)
            )
        else:
            # 使用默认模板
            prompt = self._default_prompt_template(request)
        
        return prompt
    
    def _find_template(
        self,
        source_format: str,
        target_format: str,
        strategy: PromptStrategy
    ) -> Optional[PromptTemplate]:
        """查找提示模板"""
        for template in self.prompt_templates.values():
            if (template.source_format == source_format and
                template.target_format == target_format and
                template.strategy == strategy):
                return template
        return None
    
    def _default_prompt_template(self, request: TransformationRequest) -> str:
        """默认提示模板"""
        return f"""你是一个Schema转换专家。请将以下{request.source_format}转换为{request.target_format}：

源Schema：
{self._format_schema(request.source_schema)}

要求：
{chr(10).join(f"- {req}" for req in request.requirements) if request.requirements else "- 保持语义等价性\n- 保持类型安全\n- 保持约束完整性"}

请输出转换后的Schema。"""
    
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """格式化Schema"""
        import json
        return json.dumps(schema, indent=2, ensure_ascii=False)
    
    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """格式化示例"""
        if not examples:
            return ""
        
        formatted = "\n示例：\n"
        for i, example in enumerate(examples, 1):
            formatted += f"\n示例{i}：\n"
            formatted += f"源：{self._format_schema(example.get('source', {}))}\n"
            formatted += f"目标：{self._format_schema(example.get('target', {}))}\n"
        
        return formatted
    
    def _call_ai_model(
        self,
        model_instance: Any,
        prompt: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用AI模型"""
        # 这里应该实现实际的AI模型调用
        # 简化实现：返回模拟结果
        logger.debug(f"调用AI模型: {prompt[:100]}...")
        
        # 模拟AI转换结果
        return {
            "type": "object",
            "properties": {},
            "description": "AI转换结果（模拟）"
        }
    
    def _calculate_confidence(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        # 简化实现：基于结构相似度
        source_keys = set(self._extract_keys(source_schema))
        target_keys = set(self._extract_keys(target_schema))
        
        if not source_keys and not target_keys:
            return 1.0
        
        similarity = len(source_keys & target_keys) / len(source_keys | target_keys)
        return similarity if (source_keys | target_keys) else 0.0
    
    def _extract_keys(self, schema: Dict[str, Any]) -> List[str]:
        """提取键"""
        keys = []
        
        def traverse(obj: Any):
            if isinstance(obj, dict):
                keys.extend(obj.keys())
                for value in obj.values():
                    traverse(value)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)
        
        traverse(schema)
        return keys
    
    def ensemble_transformation(
        self,
        source_schema: Dict[str, Any],
        source_format: str,
        target_format: str,
        models: List[AIModel] = None,
        voting_strategy: str = "majority"
    ) -> TransformationResult:
        """集成转换（多模型投票）"""
        if models is None:
            models = [AIModel.GPT_4, AIModel.CLAUDE_3_OPUS]
        
        results = []
        for model in models:
            try:
                result = self.transform_with_ai(
                    source_schema, source_format, target_format, model
                )
                if result.success:
                    results.append(result)
            except Exception as e:
                logger.error(f"模型 {model.value} 转换失败: {str(e)}")
        
        if not results:
            raise Exception("所有模型转换都失败")
        
        # 投票选择最佳结果
        if voting_strategy == "majority":
            # 选择置信度最高的
            best_result = max(results, key=lambda r: r.confidence)
        elif voting_strategy == "average":
            # 合并结果并取平均
            best_result = self._merge_results(results)
        else:
            best_result = results[0]
        
        return best_result
    
    def _merge_results(self, results: List[TransformationResult]) -> TransformationResult:
        """合并结果"""
        # 简化实现：返回第一个结果
        if not results:
            raise ValueError("结果列表为空")
        
        avg_confidence = sum(r.confidence for r in results) / len(results)
        avg_time = sum(r.execution_time for r in results) / len(results)
        
        merged = results[0]
        merged.confidence = avg_confidence
        merged.execution_time = avg_time
        
        return merged
    
    def get_transformation_statistics(self) -> Dict[str, Any]:
        """获取转换统计信息"""
        total_transformations = len(self.transformation_history)
        
        if total_transformations == 0:
            return {
                "total_transformations": 0,
                "success_rate": 0.0,
                "average_confidence": 0.0
            }
        
        successful = len([r for r in self.transformation_history if r.success])
        avg_confidence = sum(
            r.confidence for r in self.transformation_history if r.success
        ) / successful if successful > 0 else 0.0
        
        model_usage = {}
        for result in self.transformation_history:
            model = result.model_used
            model_usage[model] = model_usage.get(model, 0) + 1
        
        return {
            "total_transformations": total_transformations,
            "successful_transformations": successful,
            "failed_transformations": total_transformations - successful,
            "success_rate": successful / total_transformations,
            "average_confidence": avg_confidence,
            "model_usage": model_usage,
            "average_execution_time": sum(
                r.execution_time for r in self.transformation_history
            ) / total_transformations
        }
