"""
数据管道模块

专注于数据管道构建、执行、监控
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """管道状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class StepType(Enum):
    """步骤类型"""
    EXTRACT = "extract"  # 提取
    TRANSFORM = "transform"  # 转换
    LOAD = "load"  # 加载
    VALIDATE = "validate"  # 验证
    FILTER = "filter"  # 过滤


@dataclass
class PipelineStep:
    """管道步骤"""
    step_id: str
    step_type: StepType
    name: str
    processor: Callable
    config: Dict[str, Any] = None
    enabled: bool = True


@dataclass
class Pipeline:
    """数据管道"""
    pipeline_id: str
    name: str
    steps: List[PipelineStep]
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: datetime = None


class DataPipeline:
    """
    数据管道构建器
    
    专注于数据管道构建、执行、监控
    """
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def create_pipeline(self, name: str, steps: List[Dict[str, Any]]) -> Pipeline:
        """
        创建数据管道
        
        Args:
            name: 管道名称
            steps: 步骤配置列表
            
        Returns:
            管道对象
        """
        pipeline_id = f"pipeline_{datetime.utcnow().timestamp()}"
        
        pipeline_steps = []
        for step_config in steps:
            step = PipelineStep(
                step_id=step_config.get('step_id', f"step_{len(pipeline_steps)}"),
                step_type=StepType(step_config.get('step_type', 'transform')),
                name=step_config.get('name', ''),
                processor=step_config['processor'],
                config=step_config.get('config', {}),
                enabled=step_config.get('enabled', True)
            )
            pipeline_steps.append(step)
        
        pipeline = Pipeline(
            pipeline_id=pipeline_id,
            name=name,
            steps=pipeline_steps,
            created_at=datetime.utcnow()
        )
        
        self.pipelines[pipeline_id] = pipeline
        return pipeline
    
    def execute_pipeline(self, pipeline_id: str, input_data: Any) -> Dict[str, Any]:
        """
        执行数据管道
        
        Args:
            pipeline_id: 管道ID
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        if pipeline_id not in self.pipelines:
            return {
                'success': False,
                'error': f'管道不存在: {pipeline_id}'
            }
        
        pipeline = self.pipelines[pipeline_id]
        pipeline.status = PipelineStatus.RUNNING
        
        current_data = input_data
        step_results = []
        
        try:
            for step in pipeline.steps:
                if not step.enabled:
                    continue
                
                # 执行步骤
                step_start_time = datetime.utcnow()
                
                try:
                    if step.config:
                        result = step.processor(current_data, **step.config)
                    else:
                        result = step.processor(current_data)
                    
                    step_end_time = datetime.utcnow()
                    step_duration = (step_end_time - step_start_time).total_seconds()
                    
                    step_results.append({
                        'step_id': step.step_id,
                        'step_name': step.name,
                        'step_type': step.step_type.value,
                        'success': True,
                        'duration': step_duration,
                        'output_size': len(str(result)) if result else 0
                    })
                    
                    current_data = result
                
                except Exception as e:
                    logger.error(f"步骤执行失败: {step.step_id}, 错误: {e}")
                    step_results.append({
                        'step_id': step.step_id,
                        'step_name': step.name,
                        'step_type': step.step_type.value,
                        'success': False,
                        'error': str(e)
                    })
                    
                    pipeline.status = PipelineStatus.FAILED
                    break
            
            if pipeline.status == PipelineStatus.RUNNING:
                pipeline.status = PipelineStatus.COMPLETED
            
            execution_result = {
                'success': pipeline.status == PipelineStatus.COMPLETED,
                'pipeline_id': pipeline_id,
                'status': pipeline.status.value,
                'step_results': step_results,
                'output_data': current_data,
                'execution_time': sum(s.get('duration', 0) for s in step_results)
            }
            
            self.execution_history.append(execution_result)
            return execution_result
        
        except Exception as e:
            logger.error(f"管道执行失败: {pipeline_id}, 错误: {e}")
            pipeline.status = PipelineStatus.FAILED
            
            return {
                'success': False,
                'pipeline_id': pipeline_id,
                'error': str(e)
            }
    
    def add_step(self, pipeline_id: str, step_config: Dict[str, Any]) -> bool:
        """
        添加步骤到管道
        
        Args:
            pipeline_id: 管道ID
            step_config: 步骤配置
            
        Returns:
            是否成功
        """
        if pipeline_id not in self.pipelines:
            return False
        
        pipeline = self.pipelines[pipeline_id]
        
        step = PipelineStep(
            step_id=step_config.get('step_id', f"step_{len(pipeline.steps)}"),
            step_type=StepType(step_config.get('step_type', 'transform')),
            name=step_config.get('name', ''),
            processor=step_config['processor'],
            config=step_config.get('config', {}),
            enabled=step_config.get('enabled', True)
        )
        
        pipeline.steps.append(step)
        return True
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """
        获取管道状态
        
        Args:
            pipeline_id: 管道ID
            
        Returns:
            管道状态
        """
        if pipeline_id not in self.pipelines:
            return {'error': '管道不存在'}
        
        pipeline = self.pipelines[pipeline_id]
        
        return {
            'pipeline_id': pipeline_id,
            'name': pipeline.name,
            'status': pipeline.status.value,
            'step_count': len(pipeline.steps),
            'enabled_steps': sum(1 for s in pipeline.steps if s.enabled),
            'created_at': pipeline.created_at.isoformat() if pipeline.created_at else None
        }
    
    def get_execution_history(self, pipeline_id: Optional[str] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取执行历史
        
        Args:
            pipeline_id: 管道ID（可选）
            limit: 限制数量
            
        Returns:
            执行历史列表
        """
        history = self.execution_history
        
        if pipeline_id:
            history = [h for h in history if h.get('pipeline_id') == pipeline_id]
        
        # 按时间排序（最新的在前）
        history.sort(key=lambda h: h.get('execution_time', 0), reverse=True)
        
        return history[:limit]


def main():
    """主函数 - 示例用法"""
    pipeline_builder = DataPipeline()
    
    # 定义步骤
    def extract_step(data):
        return {'raw_data': data}
    
    def transform_step(data):
        data['processed'] = True
        return data
    
    def load_step(data):
        return data
    
    # 创建管道
    pipeline = pipeline_builder.create_pipeline('test_pipeline', [
        {
            'step_type': 'extract',
            'name': '提取数据',
            'processor': extract_step
        },
        {
            'step_type': 'transform',
            'name': '转换数据',
            'processor': transform_step
        },
        {
            'step_type': 'load',
            'name': '加载数据',
            'processor': load_step
        }
    ])
    
    # 执行管道
    result = pipeline_builder.execute_pipeline(pipeline.pipeline_id, 'input_data')
    print(f"管道执行结果: {result['success']}")


if __name__ == '__main__':
    main()
