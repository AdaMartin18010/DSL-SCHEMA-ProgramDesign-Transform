"""
数据转换日志模块

专注于数据转换日志、日志管理、日志分析
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """日志类别"""
    TRANSFORMATION = "transformation"  # 转换日志
    VALIDATION = "validation"  # 验证日志
    EXECUTION = "execution"  # 执行日志
    ERROR = "error"  # 错误日志
    PERFORMANCE = "performance"  # 性能日志


@dataclass
class TransformationLog:
    """转换日志"""
    log_id: str
    level: LogLevel
    category: LogCategory
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = None


class DataTransformationLogger:
    """
    数据转换日志器
    
    专注于数据转换日志、日志管理、日志分析
    """
    
    def __init__(self, max_logs: int = 10000):
        self.max_logs = max_logs
        self.logs: List[TransformationLog] = []
    
    def log(self, level: LogLevel, category: LogCategory, message: str,
           metadata: Optional[Dict[str, Any]] = None) -> TransformationLog:
        """
        记录日志
        
        Args:
            level: 日志级别
            category: 日志类别
            message: 日志消息
            metadata: 元数据
            
        Returns:
            转换日志对象
        """
        log_id = f"log_{datetime.utcnow().timestamp()}"
        
        log = TransformationLog(
            log_id=log_id,
            level=level,
            category=category,
            message=message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.logs.append(log)
        
        # 限制日志数量
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # 同时输出到标准日志
        log_method = getattr(logger, level.value, logger.info)
        log_method(f"[{category.value}] {message}")
        
        return log
    
    def get_logs(self, level: Optional[LogLevel] = None,
                category: Optional[LogCategory] = None,
                start_time: Optional[datetime] = None,
                end_time: Optional[datetime] = None,
                limit: int = 100) -> List[TransformationLog]:
        """
        获取日志
        
        Args:
            level: 日志级别（可选）
            category: 日志类别（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 限制数量
            
        Returns:
            日志列表
        """
        filtered_logs = self.logs
        
        if level:
            filtered_logs = [l for l in filtered_logs if l.level == level]
        
        if category:
            filtered_logs = [l for l in filtered_logs if l.category == category]
        
        if start_time:
            filtered_logs = [l for l in filtered_logs if l.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [l for l in filtered_logs if l.timestamp <= end_time]
        
        return sorted(filtered_logs, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_log_summary(self) -> Dict[str, Any]:
        """
        获取日志摘要
        
        Returns:
            日志摘要
        """
        total_logs = len(self.logs)
        
        # 按级别统计
        level_counts = {}
        for level in LogLevel:
            level_counts[level.value] = sum(1 for l in self.logs if l.level == level)
        
        # 按类别统计
        category_counts = {}
        for category in LogCategory:
            category_counts[category.value] = sum(1 for l in self.logs if l.category == category)
        
        # 错误日志
        error_logs = [l for l in self.logs if l.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        
        return {
            'total_logs': total_logs,
            'level_counts': level_counts,
            'category_counts': category_counts,
            'error_count': len(error_logs),
            'recent_errors': [
                {
                    'log_id': l.log_id,
                    'message': l.message,
                    'timestamp': l.timestamp.isoformat()
                }
                for l in error_logs[-10:]
            ]
        }
    
    def export_logs(self, file_path: str, filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        导出日志
        
        Args:
            file_path: 文件路径
            filters: 过滤条件（可选）
            
        Returns:
            是否成功
        """
        try:
            logs_to_export = self.logs
            
            if filters:
                if 'level' in filters:
                    logs_to_export = [l for l in logs_to_export if l.level.value == filters['level']]
                if 'category' in filters:
                    logs_to_export = [l for l in logs_to_export if l.category.value == filters['category']]
            
            log_data = [
                {
                    'log_id': l.log_id,
                    'level': l.level.value,
                    'category': l.category.value,
                    'message': l.message,
                    'timestamp': l.timestamp.isoformat(),
                    'metadata': l.metadata
                }
                for l in logs_to_export
            ]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"导出日志失败: {e}")
            return False


def main():
    """主函数 - 示例用法"""
    logger_instance = DataTransformationLogger()
    
    # 记录日志
    log = logger_instance.log(LogLevel.INFO, LogCategory.TRANSFORMATION, "转换开始")
    print(f"日志已记录: {log.log_id}")


if __name__ == '__main__':
    main()
