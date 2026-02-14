"""
推理路径记录

记录推理过程中的所有步骤
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from .storage import ExplainableReasoningStorage


class ReasoningPathRecorder:
    """推理路径记录器"""
    
    def __init__(self, storage: ExplainableReasoningStorage):
        """
        初始化记录器
        
        Args:
            storage: 可解释性推理存储管理器
        """
        self.storage = storage
        self.current_path_id = None
        self.steps = []
    
    def start_recording(self, query: str) -> str:
        """
        开始记录推理路径
        
        Args:
            query: 查询问题
            
        Returns:
            路径ID
        """
        self.current_path_id = f"path_{uuid.uuid4().hex[:16]}"
        self.steps = []
        self.query = query
        return self.current_path_id
    
    def record_step(self, step_type: str, input_data: Dict[str, Any],
                   output_data: Dict[str, Any], rule_id: Optional[str] = None,
                   explanation: Optional[str] = None):
        """
        记录推理步骤
        
        Args:
            step_type: 步骤类型
            input_data: 输入数据
            output_data: 输出数据
            rule_id: 应用的规则ID
            explanation: 解释说明
        """
        step = {
            'type': step_type,
            'input': input_data,
            'output': output_data,
            'rule_id': rule_id,
            'explanation': explanation,
            'timestamp': datetime.now().isoformat()
        }
        self.steps.append(step)
    
    def finish_recording(self, result: Dict[str, Any], rules_applied: List[str],
                        confidence: int) -> bool:
        """
        完成记录并保存
        
        Args:
            result: 推理结果
            rules_applied: 应用的规则列表
            confidence: 置信度
            
        Returns:
            是否成功
        """
        if not self.current_path_id:
            return False
        
        success = self.storage.save_reasoning_path(
            path_id=self.current_path_id,
            query=self.query,
            result=result,
            steps=self.steps,
            rules_applied=rules_applied,
            confidence=confidence
        )
        
        # 重置
        self.current_path_id = None
        self.steps = []
        
        return success
    
    def get_path(self, path_id: str) -> Optional[Dict[str, Any]]:
        """获取推理路径"""
        return self.storage.get_reasoning_path(path_id)
