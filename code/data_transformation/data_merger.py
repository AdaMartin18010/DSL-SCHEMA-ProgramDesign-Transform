"""
数据合并模块

专注于数据合并、数据连接、数据关联
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MergeType(Enum):
    """合并类型"""
    INNER = "inner"  # 内连接
    LEFT = "left"  # 左连接
    RIGHT = "right"  # 右连接
    OUTER = "outer"  # 外连接
    UNION = "union"  # 并集
    INTERSECTION = "intersection"  # 交集
    CONCATENATE = "concatenate"  # 拼接


@dataclass
class MergeConfig:
    """合并配置"""
    merge_type: MergeType
    key_fields: List[str]  # 用于连接的键字段
    how: Optional[str] = None  # 连接方式（left_on, right_on）
    suffixes: tuple = ('_x', '_y')  # 重复字段后缀


@dataclass
class MergeResult:
    """合并结果"""
    merge_id: str
    records_merged: int
    merge_time: float
    success: bool
    data: List[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = None


class DataMerger:
    """
    数据合并器
    
    专注于数据合并、数据连接、数据关联
    """
    
    def __init__(self):
        self.merge_history: List[MergeResult] = []
    
    def merge(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
             config: MergeConfig) -> MergeResult:
        """
        合并数据
        
        Args:
            left_data: 左侧数据
            right_data: 右侧数据
            config: 合并配置
            
        Returns:
            合并结果
        """
        merge_id = f"merge_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        try:
            if config.merge_type == MergeType.INNER:
                merged_data = self._inner_join(left_data, right_data, config)
            elif config.merge_type == MergeType.LEFT:
                merged_data = self._left_join(left_data, right_data, config)
            elif config.merge_type == MergeType.RIGHT:
                merged_data = self._right_join(left_data, right_data, config)
            elif config.merge_type == MergeType.OUTER:
                merged_data = self._outer_join(left_data, right_data, config)
            elif config.merge_type == MergeType.UNION:
                merged_data = self._union(left_data, right_data, config)
            elif config.merge_type == MergeType.INTERSECTION:
                merged_data = self._intersection(left_data, right_data, config)
            elif config.merge_type == MergeType.CONCATENATE:
                merged_data = self._concatenate(left_data, right_data)
            else:
                merged_data = self._inner_join(left_data, right_data, config)
            
            end_time = datetime.utcnow()
            merge_time = (end_time - start_time).total_seconds()
            
            result = MergeResult(
                merge_id=merge_id,
                records_merged=len(merged_data),
                merge_time=merge_time,
                success=True,
                data=merged_data
            )
            
            self.merge_history.append(result)
            return result
        
        except Exception as e:
            logger.error(f"合并失败: {e}")
            end_time = datetime.utcnow()
            merge_time = (end_time - start_time).total_seconds()
            
            result = MergeResult(
                merge_id=merge_id,
                records_merged=0,
                merge_time=merge_time,
                success=False,
                errors=[{'error': str(e)}]
            )
            
            self.merge_history.append(result)
            return result
    
    def _inner_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
                   config: MergeConfig) -> List[Dict[str, Any]]:
        """内连接"""
        # 构建右侧索引
        right_index = {}
        for record in right_data:
            key = tuple(record.get(f) for f in config.key_fields)
            if key not in right_index:
                right_index[key] = []
            right_index[key].append(record)
        
        # 合并
        merged_data = []
        for left_record in left_data:
            key = tuple(left_record.get(f) for f in config.key_fields)
            if key in right_index:
                for right_record in right_index[key]:
                    merged_record = self._merge_records(left_record, right_record, config)
                    merged_data.append(merged_record)
        
        return merged_data
    
    def _left_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
                   config: MergeConfig) -> List[Dict[str, Any]]:
        """左连接"""
        # 构建右侧索引
        right_index = {}
        for record in right_data:
            key = tuple(record.get(f) for f in config.key_fields)
            if key not in right_index:
                right_index[key] = []
            right_index[key].append(record)
        
        # 合并
        merged_data = []
        for left_record in left_data:
            key = tuple(left_record.get(f) for f in config.key_fields)
            if key in right_index:
                for right_record in right_index[key]:
                    merged_record = self._merge_records(left_record, right_record, config)
                    merged_data.append(merged_record)
            else:
                # 左连接：保留左侧记录
                merged_data.append(left_record.copy())
        
        return merged_data
    
    def _right_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
                   config: MergeConfig) -> List[Dict[str, Any]]:
        """右连接"""
        # 构建左侧索引
        left_index = {}
        for record in left_data:
            key = tuple(record.get(f) for f in config.key_fields)
            if key not in left_index:
                left_index[key] = []
            left_index[key].append(record)
        
        # 合并
        merged_data = []
        for right_record in right_data:
            key = tuple(right_record.get(f) for f in config.key_fields)
            if key in left_index:
                for left_record in left_index[key]:
                    merged_record = self._merge_records(left_record, right_record, config)
                    merged_data.append(merged_record)
            else:
                # 右连接：保留右侧记录
                merged_data.append(right_record.copy())
        
        return merged_data
    
    def _outer_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
                   config: MergeConfig) -> List[Dict[str, Any]]:
        """外连接"""
        # 先做左连接
        left_merged = self._left_join(left_data, right_data, config)
        
        # 找出右侧独有的记录
        left_keys = {tuple(r.get(f) for f in config.key_fields) for r in left_data}
        right_only = [
            r for r in right_data
            if tuple(r.get(f) for f in config.key_fields) not in left_keys
        ]
        
        # 合并
        merged_data = left_merged + right_only
        return merged_data
    
    def _union(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
              config: MergeConfig) -> List[Dict[str, Any]]:
        """并集"""
        # 使用键字段去重
        seen = set()
        merged_data = []
        
        for record in left_data + right_data:
            key = tuple(record.get(f) for f in config.key_fields)
            if key not in seen:
                seen.add(key)
                merged_data.append(record)
        
        return merged_data
    
    def _intersection(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]],
                     config: MergeConfig) -> List[Dict[str, Any]]:
        """交集"""
        # 构建右侧键集合
        right_keys = {tuple(r.get(f) for f in config.key_fields) for r in right_data}
        
        # 找出左侧也在右侧的记录
        merged_data = [
            r for r in left_data
            if tuple(r.get(f) for f in config.key_fields) in right_keys
        ]
        
        return merged_data
    
    def _concatenate(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """拼接"""
        return left_data + right_data
    
    def _merge_records(self, left_record: Dict[str, Any], right_record: Dict[str, Any],
                      config: MergeConfig) -> Dict[str, Any]:
        """合并两条记录"""
        merged = left_record.copy()
        
        # 处理重复字段
        for key, value in right_record.items():
            if key in merged and key not in config.key_fields:
                # 添加后缀
                merged[key + config.suffixes[1]] = value
            else:
                merged[key] = value
        
        return merged
    
    def get_merge_stats(self) -> Dict[str, Any]:
        """
        获取合并统计
        
        Returns:
            合并统计
        """
        total_merges = len(self.merge_history)
        successful_merges = sum(1 for m in self.merge_history if m.success)
        total_records = sum(m.records_merged for m in self.merge_history)
        
        if total_merges > 0:
            avg_time = sum(m.merge_time for m in self.merge_history) / total_merges
        else:
            avg_time = 0.0
        
        return {
            'total_merges': total_merges,
            'successful_merges': successful_merges,
            'failed_merges': total_merges - successful_merges,
            'total_records_merged': total_records,
            'success_rate': (successful_merges / total_merges * 100) if total_merges > 0 else 0.0,
            'average_merge_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    merger = DataMerger()
    
    # 合并数据
    left_data = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    right_data = [{'id': 1, 'age': 25}, {'id': 3, 'age': 30}]
    
    config = MergeConfig(
        merge_type=MergeType.INNER,
        key_fields=['id']
    )
    
    result = merger.merge(left_data, right_data, config)
    print(f"合并结果: 成功={result.success}, 合并记录数={result.records_merged}")


if __name__ == '__main__':
    main()
