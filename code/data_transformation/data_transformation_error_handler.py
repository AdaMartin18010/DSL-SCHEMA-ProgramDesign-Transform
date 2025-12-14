"""
数据转换错误处理模块

专注于数据转换错误处理、错误恢复、错误报告
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    CRITICAL = "critical"  # 严重


class ErrorCategory(Enum):
    """错误类别"""
    VALIDATION = "validation"  # 验证错误
    TRANSFORMATION = "transformation"  # 转换错误
    EXECUTION = "execution"  # 执行错误
    RESOURCE = "resource"  # 资源错误
    NETWORK = "network"  # 网络错误
    DATA = "data"  # 数据错误


@dataclass
class TransformationError:
    """转换错误"""
    error_id: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    timestamp: datetime
    context: Dict[str, Any] = None
    stack_trace: Optional[str] = None
    recovery_action: Optional[str] = None


@dataclass
class ErrorRecoveryStrategy:
    """错误恢复策略"""
    strategy_id: str
    error_pattern: str
    recovery_action: Callable
    max_retries: int = 3
    enabled: bool = True


class DataTransformationErrorHandler:
    """
    数据转换错误处理器
    
    专注于数据转换错误处理、错误恢复、错误报告
    """
    
    def __init__(self):
        self.errors: List[TransformationError] = []
        self.recovery_strategies: Dict[str, ErrorRecoveryStrategy] = {}
        self.error_stats: Dict[str, int] = {}
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.EXECUTION) -> TransformationError:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 上下文信息
            severity: 错误严重程度
            category: 错误类别
            
        Returns:
            转换错误对象
        """
        error_id = f"error_{datetime.utcnow().timestamp()}"
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        transformation_error = TransformationError(
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            category=category,
            timestamp=datetime.utcnow(),
            context=context or {},
            stack_trace=stack_trace
        )
        
        self.errors.append(transformation_error)
        
        # 更新统计
        error_key = f"{error_type}_{category.value}"
        self.error_stats[error_key] = self.error_stats.get(error_key, 0) + 1
        
        # 尝试恢复
        recovery_action = self._try_recovery(transformation_error)
        if recovery_action:
            transformation_error.recovery_action = recovery_action
        
        # 记录日志
        log_level = self._get_log_level(severity)
        log_method = getattr(logger, log_level, logger.error)
        log_method(f"[{category.value}] {error_message}", exc_info=error)
        
        return transformation_error
    
    def _try_recovery(self, error: TransformationError) -> Optional[str]:
        """尝试恢复"""
        for strategy in self.recovery_strategies.values():
            if not strategy.enabled:
                continue
            
            # 检查错误模式匹配
            if strategy.error_pattern in error.error_type or strategy.error_pattern in error.error_message:
                try:
                    result = strategy.recovery_action(error)
                    if result:
                        return f"恢复策略 {strategy.strategy_id} 执行成功"
                except Exception as e:
                    logger.warning(f"恢复策略 {strategy.strategy_id} 执行失败: {e}")
        
        return None
    
    def _get_log_level(self, severity: ErrorSeverity) -> str:
        """获取日志级别"""
        severity_map = {
            ErrorSeverity.LOW: 'debug',
            ErrorSeverity.MEDIUM: 'warning',
            ErrorSeverity.HIGH: 'error',
            ErrorSeverity.CRITICAL: 'critical'
        }
        return severity_map.get(severity, 'error')
    
    def add_recovery_strategy(self, strategy_config: Dict[str, Any]) -> ErrorRecoveryStrategy:
        """
        添加恢复策略
        
        Args:
            strategy_config: 策略配置
            
        Returns:
            错误恢复策略对象
        """
        strategy_id = strategy_config.get('strategy_id', f"strategy_{datetime.utcnow().timestamp()}")
        
        strategy = ErrorRecoveryStrategy(
            strategy_id=strategy_id,
            error_pattern=strategy_config.get('error_pattern', ''),
            recovery_action=strategy_config['recovery_action'],
            max_retries=strategy_config.get('max_retries', 3),
            enabled=strategy_config.get('enabled', True)
        )
        
        self.recovery_strategies[strategy_id] = strategy
        return strategy
    
    def get_error_summary(self, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取错误摘要
        
        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            错误摘要
        """
        filtered_errors = self.errors
        
        if start_time:
            filtered_errors = [e for e in filtered_errors if e.timestamp >= start_time]
        
        if end_time:
            filtered_errors = [e for e in filtered_errors if e.timestamp <= end_time]
        
        # 按严重程度统计
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = sum(1 for e in filtered_errors if e.severity == severity)
        
        # 按类别统计
        category_counts = {}
        for category in ErrorCategory:
            category_counts[category.value] = sum(1 for e in filtered_errors if e.category == category)
        
        # 最近错误
        recent_errors = sorted(filtered_errors, key=lambda x: x.timestamp, reverse=True)[:10]
        
        return {
            'total_errors': len(filtered_errors),
            'severity_counts': severity_counts,
            'category_counts': category_counts,
            'error_stats': self.error_stats,
            'recent_errors': [
                {
                    'error_id': e.error_id,
                    'error_type': e.error_type,
                    'error_message': e.error_message,
                    'severity': e.severity.value,
                    'category': e.category.value,
                    'timestamp': e.timestamp.isoformat(),
                    'recovery_action': e.recovery_action
                }
                for e in recent_errors
            ]
        }


def main():
    """主函数 - 示例用法"""
    error_handler = DataTransformationErrorHandler()
    
    # 定义恢复策略
    def retry_recovery(error: TransformationError) -> bool:
        return True
    
    error_handler.add_recovery_strategy({
        'error_pattern': 'ValueError',
        'recovery_action': retry_recovery
    })
    
    # 处理错误
    try:
        raise ValueError("示例错误")
    except Exception as e:
        error = error_handler.handle_error(e, severity=ErrorSeverity.MEDIUM)
        print(f"错误已处理: {error.error_id}")


if __name__ == '__main__':
    main()








