"""
数据转换链模块

专注于数据转换链、转换流程编排、转换任务调度
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ChainStatus(Enum):
    """链状态"""
    PENDING = "pending"  # 待处理
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    PAUSED = "paused"  # 已暂停


@dataclass
class TransformationStep:
    """转换步骤"""
    step_id: str
    step_name: str
    transformer: Callable
    config: Dict[str, Any] = None
    enabled: bool = True


@dataclass
class TransformationChain:
    """转换链"""
    chain_id: str
    chain_name: str
    steps: List[TransformationStep]
    status: ChainStatus
    created_at: datetime


@dataclass
class ChainExecutionResult:
    """链执行结果"""
    chain_id: str
    execution_id: str
    status: ChainStatus
    steps_executed: int
    execution_time: float
    data: List[Dict[str, Any]]
    errors: List[Dict[str, Any]] = None


class DataTransformationChain:
    """
    数据转换链
    
    专注于数据转换链、转换流程编排、转换任务调度
    """
    
    def __init__(self):
        self.chains: Dict[str, TransformationChain] = {}
        self.execution_history: List[ChainExecutionResult] = []
    
    def create_chain(self, chain_config: Dict[str, Any]) -> TransformationChain:
        """
        创建转换链
        
        Args:
            chain_config: 链配置
            
        Returns:
            转换链对象
        """
        chain_id = chain_config.get('chain_id', f"chain_{datetime.utcnow().timestamp()}")
        
        steps = []
        for step_config in chain_config.get('steps', []):
            step = TransformationStep(
                step_id=step_config.get('step_id', f"step_{datetime.utcnow().timestamp()}"),
                step_name=step_config.get('step_name', ''),
                transformer=step_config['transformer'],
                config=step_config.get('config', {}),
                enabled=step_config.get('enabled', True)
            )
            steps.append(step)
        
        chain = TransformationChain(
            chain_id=chain_id,
            chain_name=chain_config.get('chain_name', ''),
            steps=steps,
            status=ChainStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.chains[chain_id] = chain
        return chain
    
    def execute_chain(self, chain_id: str, data: List[Dict[str, Any]]) -> ChainExecutionResult:
        """
        执行转换链
        
        Args:
            chain_id: 链ID
            data: 数据列表
            
        Returns:
            链执行结果
        """
        if chain_id not in self.chains:
            raise ValueError(f"转换链不存在: {chain_id}")
        
        chain = self.chains[chain_id]
        chain.status = ChainStatus.RUNNING
        
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        current_data = data.copy()
        steps_executed = 0
        errors = []
        
        try:
            for step in chain.steps:
                if not step.enabled:
                    continue
                
                try:
                    # 执行转换步骤
                    if step.config:
                        current_data = step.transformer(current_data, **step.config)
                    else:
                        current_data = step.transformer(current_data)
                    
                    steps_executed += 1
                
                except Exception as e:
                    logger.error(f"步骤执行失败: {step.step_name}, 错误: {e}")
                    errors.append({
                        'step_id': step.step_id,
                        'step_name': step.step_name,
                        'error': str(e)
                    })
                    # 根据配置决定是否继续
                    if step.config.get('stop_on_error', True):
                        chain.status = ChainStatus.FAILED
                        break
            
            if chain.status != ChainStatus.FAILED:
                chain.status = ChainStatus.COMPLETED
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            result = ChainExecutionResult(
                chain_id=chain_id,
                execution_id=execution_id,
                status=chain.status,
                steps_executed=steps_executed,
                execution_time=execution_time,
                data=current_data,
                errors=errors if errors else None
            )
            
            self.execution_history.append(result)
            return result
        
        except Exception as e:
            logger.error(f"链执行失败: {chain_id}, 错误: {e}")
            chain.status = ChainStatus.FAILED
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            result = ChainExecutionResult(
                chain_id=chain_id,
                execution_id=execution_id,
                status=ChainStatus.FAILED,
                steps_executed=steps_executed,
                execution_time=execution_time,
                data=current_data,
                errors=[{'error': str(e)}]
            )
            
            self.execution_history.append(result)
            return result
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """
        获取链统计
        
        Returns:
            链统计
        """
        total_chains = len(self.chains)
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e.status == ChainStatus.COMPLETED)
        
        if total_executions > 0:
            avg_time = sum(e.execution_time for e in self.execution_history) / total_executions
        else:
            avg_time = 0.0
        
        return {
            'total_chains': total_chains,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': total_executions - successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0.0,
            'average_execution_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    chain_manager = DataTransformationChain()
    
    # 定义转换函数
    def trim_data(data):
        return [{'name': r.get('name', '').strip()} for r in data]
    
    def uppercase_data(data):
        return [{'name': r.get('name', '').upper()} for r in data]
    
    # 创建转换链
    chain = chain_manager.create_chain({
        'chain_name': '数据清理链',
        'steps': [
            {'step_name': '去除空白', 'transformer': trim_data},
            {'step_name': '转大写', 'transformer': uppercase_data}
        ]
    })
    
    # 执行链
    data = [{'name': '  alice  '}, {'name': '  bob  '}]
    result = chain_manager.execute_chain(chain.chain_id, data)
    print(f"链执行结果: 状态={result.status.value}, 步骤数={result.steps_executed}")


if __name__ == '__main__':
    main()
