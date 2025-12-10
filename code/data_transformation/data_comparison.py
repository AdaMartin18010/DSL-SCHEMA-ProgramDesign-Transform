"""
数据对比模块

专注于数据对比、差异分析、数据比较
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ComparisonType(Enum):
    """对比类型"""
    FIELD_BY_FIELD = "field_by_field"  # 字段级对比
    RECORD_BY_RECORD = "record_by_record"  # 记录级对比
    SCHEMA = "schema"  # Schema对比
    STATISTICAL = "statistical"  # 统计对比


class DifferenceType(Enum):
    """差异类型"""
    ADDED = "added"  # 新增
    REMOVED = "removed"  # 删除
    MODIFIED = "modified"  # 修改
    UNCHANGED = "unchanged"  # 未变化


@dataclass
class ComparisonResult:
    """对比结果"""
    comparison_id: str
    comparison_type: ComparisonType
    differences: List[Dict[str, Any]]
    summary: Dict[str, Any]
    comparison_time: float


class DataComparison:
    """
    数据对比器
    
    专注于数据对比、差异分析、数据比较
    """
    
    def __init__(self):
        self.comparison_history: List[ComparisonResult] = []
    
    def compare(self, data1: List[Dict[str, Any]], data2: List[Dict[str, Any]],
               comparison_type: ComparisonType = ComparisonType.RECORD_BY_RECORD,
               key_fields: Optional[List[str]] = None) -> ComparisonResult:
        """
        对比数据
        
        Args:
            data1: 数据1
            data2: 数据2
            comparison_type: 对比类型
            key_fields: 关键字段列表（用于记录匹配）
            
        Returns:
            对比结果
        """
        comparison_id = f"compare_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        if comparison_type == ComparisonType.FIELD_BY_FIELD:
            differences, summary = self._compare_field_by_field(data1, data2)
        elif comparison_type == ComparisonType.RECORD_BY_RECORD:
            differences, summary = self._compare_record_by_record(data1, data2, key_fields)
        elif comparison_type == ComparisonType.SCHEMA:
            differences, summary = self._compare_schema(data1, data2)
        elif comparison_type == ComparisonType.STATISTICAL:
            differences, summary = self._compare_statistical(data1, data2)
        else:
            differences, summary = self._compare_record_by_record(data1, data2, key_fields)
        
        end_time = datetime.utcnow()
        comparison_time = (end_time - start_time).total_seconds()
        
        result = ComparisonResult(
            comparison_id=comparison_id,
            comparison_type=comparison_type,
            differences=differences,
            summary=summary,
            comparison_time=comparison_time
        )
        
        self.comparison_history.append(result)
        return result
    
    def _compare_field_by_field(self, data1: List[Dict[str, Any]],
                               data2: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """字段级对比"""
        differences = []
        
        # 获取所有字段
        all_fields = set()
        for record in data1 + data2:
            all_fields.update(record.keys())
        
        # 对比每个字段
        for field in all_fields:
            values1 = [r.get(field) for r in data1 if field in r]
            values2 = [r.get(field) for r in data2 if field in r]
            
            if set(values1) != set(values2):
                differences.append({
                    'type': DifferenceType.MODIFIED.value,
                    'field': field,
                    'data1_values': list(set(values1)),
                    'data2_values': list(set(values2))
                })
        
        summary = {
            'total_fields': len(all_fields),
            'different_fields': len(differences),
            'same_fields': len(all_fields) - len(differences)
        }
        
        return differences, summary
    
    def _compare_record_by_record(self, data1: List[Dict[str, Any]],
                                 data2: List[Dict[str, Any]],
                                 key_fields: Optional[List[str]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """记录级对比"""
        differences = []
        
        if key_fields:
            # 使用关键字段匹配
            index1 = {tuple(r.get(f) for f in key_fields): r for r in data1}
            index2 = {tuple(r.get(f) for f in key_fields): r for r in data2}
            
            all_keys = set(index1.keys()) | set(index2.keys())
            
            for key in all_keys:
                record1 = index1.get(key)
                record2 = index2.get(key)
                
                if record1 is None:
                    differences.append({
                        'type': DifferenceType.ADDED.value,
                        'key': key,
                        'record': record2
                    })
                elif record2 is None:
                    differences.append({
                        'type': DifferenceType.REMOVED.value,
                        'key': key,
                        'record': record1
                    })
                elif record1 != record2:
                    # 找出具体差异
                    field_diffs = {}
                    all_fields = set(record1.keys()) | set(record2.keys())
                    for field in all_fields:
                        val1 = record1.get(field)
                        val2 = record2.get(field)
                        if val1 != val2:
                            field_diffs[field] = {'old': val1, 'new': val2}
                    
                    differences.append({
                        'type': DifferenceType.MODIFIED.value,
                        'key': key,
                        'field_differences': field_diffs
                    })
        else:
            # 简单对比
            set1 = {str(r) for r in data1}
            set2 = {str(r) for r in data2}
            
            added = set2 - set1
            removed = set1 - set2
            
            for record_str in added:
                differences.append({
                    'type': DifferenceType.ADDED.value,
                    'record': record_str
                })
            
            for record_str in removed:
                differences.append({
                    'type': DifferenceType.REMOVED.value,
                    'record': record_str
                })
        
        summary = {
            'data1_count': len(data1),
            'data2_count': len(data2),
            'added_count': sum(1 for d in differences if d['type'] == DifferenceType.ADDED.value),
            'removed_count': sum(1 for d in differences if d['type'] == DifferenceType.REMOVED.value),
            'modified_count': sum(1 for d in differences if d['type'] == DifferenceType.MODIFIED.value)
        }
        
        return differences, summary
    
    def _compare_schema(self, data1: List[Dict[str, Any]],
                       data2: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Schema对比"""
        schema1 = set(data1[0].keys()) if data1 else set()
        schema2 = set(data2[0].keys()) if data2 else set()
        
        differences = []
        
        added_fields = schema2 - schema1
        removed_fields = schema1 - schema2
        
        for field in added_fields:
            differences.append({
                'type': DifferenceType.ADDED.value,
                'field': field
            })
        
        for field in removed_fields:
            differences.append({
                'type': DifferenceType.REMOVED.value,
                'field': field
            })
        
        summary = {
            'schema1_fields': len(schema1),
            'schema2_fields': len(schema2),
            'common_fields': len(schema1 & schema2),
            'added_fields': len(added_fields),
            'removed_fields': len(removed_fields)
        }
        
        return differences, summary
    
    def _compare_statistical(self, data1: List[Dict[str, Any]],
                            data2: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """统计对比"""
        differences = []
        
        # 简单统计对比
        stats1 = {
            'count': len(data1),
            'fields': set(data1[0].keys()) if data1 else set()
        }
        stats2 = {
            'count': len(data2),
            'fields': set(data2[0].keys()) if data2 else set()
        }
        
        if stats1['count'] != stats2['count']:
            differences.append({
                'type': DifferenceType.MODIFIED.value,
                'metric': 'count',
                'data1_value': stats1['count'],
                'data2_value': stats2['count']
            })
        
        if stats1['fields'] != stats2['fields']:
            differences.append({
                'type': DifferenceType.MODIFIED.value,
                'metric': 'fields',
                'data1_value': list(stats1['fields']),
                'data2_value': list(stats2['fields'])
            })
        
        summary = {
            'data1_count': stats1['count'],
            'data2_count': stats2['count'],
            'count_difference': abs(stats1['count'] - stats2['count']),
            'field_difference': len(stats1['fields'] ^ stats2['fields'])
        }
        
        return differences, summary
    
    def get_comparison_stats(self) -> Dict[str, Any]:
        """
        获取对比统计
        
        Returns:
            对比统计
        """
        total_comparisons = len(self.comparison_history)
        
        if total_comparisons == 0:
            return {'total_comparisons': 0}
        
        type_counts = {}
        for result in self.comparison_history:
            comp_type = result.comparison_type.value
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        total_differences = sum(len(r.differences) for r in self.comparison_history)
        
        return {
            'total_comparisons': total_comparisons,
            'type_counts': type_counts,
            'total_differences': total_differences,
            'average_differences': total_differences / total_comparisons if total_comparisons > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    comparison = DataComparison()
    
    # 对比数据
    data1 = [{'id': 1, 'name': 'Alice', 'age': 25}]
    data2 = [{'id': 1, 'name': 'Alice', 'age': 26}]
    
    result = comparison.compare(data1, data2, ComparisonType.RECORD_BY_RECORD, ['id'])
    print(f"对比结果: 差异数={len(result.differences)}")


if __name__ == '__main__':
    main()
