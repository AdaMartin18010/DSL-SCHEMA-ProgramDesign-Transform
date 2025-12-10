"""
数据拆分模块

专注于数据拆分、数据分割、数据分组
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SplitStrategy(Enum):
    """拆分策略"""
    BY_SIZE = "by_size"  # 按大小拆分
    BY_COUNT = "by_count"  # 按数量拆分
    BY_FIELD = "by_field"  # 按字段拆分
    BY_CONDITION = "by_condition"  # 按条件拆分
    BY_PERCENTAGE = "by_percentage"  # 按百分比拆分


@dataclass
class SplitConfig:
    """拆分配置"""
    strategy: SplitStrategy
    size: Optional[int] = None  # 每个分块的大小
    count: Optional[int] = None  # 分块数量
    field: Optional[str] = None  # 拆分字段
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None  # 拆分条件
    percentages: Optional[List[float]] = None  # 百分比列表


@dataclass
class SplitResult:
    """拆分结果"""
    split_id: str
    chunks: List[List[Dict[str, Any]]]
    split_time: float
    success: bool
    errors: List[Dict[str, Any]] = None


class DataSplitter:
    """
    数据拆分器
    
    专注于数据拆分、数据分割、数据分组
    """
    
    def __init__(self):
        self.split_history: List[SplitResult] = []
    
    def split(self, data: List[Dict[str, Any]], config: SplitConfig) -> SplitResult:
        """
        拆分数据
        
        Args:
            data: 数据列表
            config: 拆分配置
            
        Returns:
            拆分结果
        """
        split_id = f"split_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        try:
            if config.strategy == SplitStrategy.BY_SIZE:
                chunks = self._split_by_size(data, config)
            elif config.strategy == SplitStrategy.BY_COUNT:
                chunks = self._split_by_count(data, config)
            elif config.strategy == SplitStrategy.BY_FIELD:
                chunks = self._split_by_field(data, config)
            elif config.strategy == SplitStrategy.BY_CONDITION:
                chunks = self._split_by_condition(data, config)
            elif config.strategy == SplitStrategy.BY_PERCENTAGE:
                chunks = self._split_by_percentage(data, config)
            else:
                chunks = self._split_by_size(data, config)
            
            end_time = datetime.utcnow()
            split_time = (end_time - start_time).total_seconds()
            
            result = SplitResult(
                split_id=split_id,
                chunks=chunks,
                split_time=split_time,
                success=True
            )
            
            self.split_history.append(result)
            return result
        
        except Exception as e:
            logger.error(f"拆分失败: {e}")
            end_time = datetime.utcnow()
            split_time = (end_time - start_time).total_seconds()
            
            result = SplitResult(
                split_id=split_id,
                chunks=[],
                split_time=split_time,
                success=False,
                errors=[{'error': str(e)}]
            )
            
            self.split_history.append(result)
            return result
    
    def _split_by_size(self, data: List[Dict[str, Any]], config: SplitConfig) -> List[List[Dict[str, Any]]]:
        """按大小拆分"""
        size = config.size or 1000
        chunks = []
        
        for i in range(0, len(data), size):
            chunks.append(data[i:i + size])
        
        return chunks
    
    def _split_by_count(self, data: List[Dict[str, Any]], config: SplitConfig) -> List[List[Dict[str, Any]]]:
        """按数量拆分"""
        count = config.count or 10
        size = len(data) // count
        if len(data) % count > 0:
            size += 1
        
        chunks = []
        for i in range(0, len(data), size):
            chunks.append(data[i:i + size])
        
        return chunks
    
    def _split_by_field(self, data: List[Dict[str, Any]], config: SplitConfig) -> List[List[Dict[str, Any]]]:
        """按字段拆分"""
        if not config.field:
            return [data]
        
        # 按字段值分组
        groups = {}
        for record in data:
            field_value = record.get(config.field)
            if field_value not in groups:
                groups[field_value] = []
            groups[field_value].append(record)
        
        return list(groups.values())
    
    def _split_by_condition(self, data: List[Dict[str, Any]], config: SplitConfig) -> List[List[Dict[str, Any]]]:
        """按条件拆分"""
        if not config.condition:
            return [data]
        
        true_chunk = []
        false_chunk = []
        
        for record in data:
            if config.condition(record):
                true_chunk.append(record)
            else:
                false_chunk.append(record)
        
        return [true_chunk, false_chunk] if true_chunk and false_chunk else [data]
    
    def _split_by_percentage(self, data: List[Dict[str, Any]], config: SplitConfig) -> List[List[Dict[str, Any]]]:
        """按百分比拆分"""
        if not config.percentages:
            return [data]
        
        # 验证百分比总和
        total_percentage = sum(config.percentages)
        if total_percentage > 1.0:
            raise ValueError("百分比总和不能超过1.0")
        
        chunks = []
        start_index = 0
        
        for percentage in config.percentages:
            end_index = start_index + int(len(data) * percentage)
            chunks.append(data[start_index:end_index])
            start_index = end_index
        
        # 处理剩余数据
        if start_index < len(data):
            chunks[-1].extend(data[start_index:])
        
        return chunks
    
    def get_split_stats(self) -> Dict[str, Any]:
        """
        获取拆分统计
        
        Returns:
            拆分统计
        """
        total_splits = len(self.split_history)
        successful_splits = sum(1 for s in self.split_history if s.success)
        total_chunks = sum(len(s.chunks) for s in self.split_history)
        
        if total_splits > 0:
            avg_time = sum(s.split_time for s in self.split_history) / total_splits
        else:
            avg_time = 0.0
        
        return {
            'total_splits': total_splits,
            'successful_splits': successful_splits,
            'failed_splits': total_splits - successful_splits,
            'total_chunks': total_chunks,
            'success_rate': (successful_splits / total_splits * 100) if total_splits > 0 else 0.0,
            'average_split_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    splitter = DataSplitter()
    
    # 拆分数据
    data = [{'id': i, 'value': i * 2} for i in range(100)]
    
    config = SplitConfig(
        strategy=SplitStrategy.BY_SIZE,
        size=25
    )
    
    result = splitter.split(data, config)
    print(f"拆分结果: 成功={result.success}, 分块数={len(result.chunks)}")


if __name__ == '__main__':
    main()
