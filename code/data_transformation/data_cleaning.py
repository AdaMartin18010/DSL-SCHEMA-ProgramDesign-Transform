"""
数据清理模块

专注于数据清理、数据清洗、异常值处理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class CleaningOperation(Enum):
    """清理操作"""
    TRIM = "trim"  # 去除空白
    REMOVE_DUPLICATES = "remove_duplicates"  # 去重
    REMOVE_NULLS = "remove_nulls"  # 去除空值
    REMOVE_OUTLIERS = "remove_outliers"  # 去除异常值
    NORMALIZE = "normalize"  # 规范化
    STANDARDIZE = "standardize"  # 标准化
    REMOVE_SPECIAL_CHARS = "remove_special_chars"  # 去除特殊字符


@dataclass
class CleaningRule:
    """清理规则"""
    rule_id: str
    operation: CleaningOperation
    field: Optional[str] = None
    config: Dict[str, Any] = None


@dataclass
class CleaningResult:
    """清理结果"""
    cleaning_id: str
    original_count: int
    cleaned_count: int
    removed_count: int
    cleaning_time: float
    data: List[Dict[str, Any]]
    statistics: Dict[str, Any] = None


class DataCleaning:
    """
    数据清理器
    
    专注于数据清理、数据清洗、异常值处理
    """
    
    def __init__(self):
        self.cleaning_history: List[CleaningResult] = []
    
    def clean(self, data: List[Dict[str, Any]], rules: List[CleaningRule]) -> CleaningResult:
        """
        清理数据
        
        Args:
            data: 数据列表
            rules: 清理规则列表
            
        Returns:
            清理结果
        """
        cleaning_id = f"clean_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        original_count = len(data)
        cleaned_data = data.copy()
        
        for rule in rules:
            cleaned_data = self._apply_cleaning_rule(cleaned_data, rule)
        
        end_time = datetime.utcnow()
        cleaning_time = (end_time - start_time).total_seconds()
        
        removed_count = original_count - len(cleaned_data)
        
        result = CleaningResult(
            cleaning_id=cleaning_id,
            original_count=original_count,
            cleaned_count=len(cleaned_data),
            removed_count=removed_count,
            cleaning_time=cleaning_time,
            data=cleaned_data,
            statistics=self._calculate_statistics(cleaned_data)
        )
        
        self.cleaning_history.append(result)
        return result
    
    def _apply_cleaning_rule(self, data: List[Dict[str, Any]], rule: CleaningRule) -> List[Dict[str, Any]]:
        """应用清理规则"""
        operation = rule.operation
        field = rule.field
        config = rule.config or {}
        
        if operation == CleaningOperation.TRIM:
            return self._trim_data(data, field)
        elif operation == CleaningOperation.REMOVE_DUPLICATES:
            return self._remove_duplicates(data, field)
        elif operation == CleaningOperation.REMOVE_NULLS:
            return self._remove_nulls(data, field)
        elif operation == CleaningOperation.REMOVE_OUTLIERS:
            return self._remove_outliers(data, field, config)
        elif operation == CleaningOperation.NORMALIZE:
            return self._normalize_data(data, field)
        elif operation == CleaningOperation.REMOVE_SPECIAL_CHARS:
            return self._remove_special_chars(data, field, config)
        else:
            return data
    
    def _trim_data(self, data: List[Dict[str, Any]], field: Optional[str]) -> List[Dict[str, Any]]:
        """去除空白"""
        cleaned = []
        for record in data:
            cleaned_record = record.copy()
            if field:
                if field in cleaned_record and isinstance(cleaned_record[field], str):
                    cleaned_record[field] = cleaned_record[field].strip()
            else:
                for key, value in cleaned_record.items():
                    if isinstance(value, str):
                        cleaned_record[key] = value.strip()
            cleaned.append(cleaned_record)
        return cleaned
    
    def _remove_duplicates(self, data: List[Dict[str, Any]], field: Optional[str]) -> List[Dict[str, Any]]:
        """去重"""
        seen = set()
        cleaned = []
        
        for record in data:
            if field:
                key = record.get(field)
            else:
                key = tuple(sorted(record.items()))
            
            if key not in seen:
                seen.add(key)
                cleaned.append(record)
        
        return cleaned
    
    def _remove_nulls(self, data: List[Dict[str, Any]], field: Optional[str]) -> List[Dict[str, Any]]:
        """去除空值"""
        if field:
            return [r for r in data if r.get(field) is not None]
        else:
            return [r for r in data if any(v is not None for v in r.values())]
    
    def _remove_outliers(self, data: List[Dict[str, Any]], field: Optional[str],
                        config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """去除异常值"""
        if not field:
            return data
        
        values = [r.get(field) for r in data if isinstance(r.get(field), (int, float))]
        if not values:
            return data
        
        # 使用IQR方法
        q1 = sorted(values)[len(values) // 4]
        q3 = sorted(values)[3 * len(values) // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [
            r for r in data
            if not isinstance(r.get(field), (int, float)) or
            (lower_bound <= r.get(field) <= upper_bound)
        ]
    
    def _normalize_data(self, data: List[Dict[str, Any]], field: Optional[str]) -> List[Dict[str, Any]]:
        """规范化数据（简化实现）"""
        # 简化实现：只处理字符串转小写
        cleaned = []
        for record in data:
            cleaned_record = record.copy()
            if field:
                if field in cleaned_record and isinstance(cleaned_record[field], str):
                    cleaned_record[field] = cleaned_record[field].lower()
            else:
                for key, value in cleaned_record.items():
                    if isinstance(value, str):
                        cleaned_record[key] = value.lower()
            cleaned.append(cleaned_record)
        return cleaned
    
    def _remove_special_chars(self, data: List[Dict[str, Any]], field: Optional[str],
                             config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """去除特殊字符"""
        pattern = config.get('pattern', r'[^\w\s]')
        cleaned = []
        for record in data:
            cleaned_record = record.copy()
            if field:
                if field in cleaned_record and isinstance(cleaned_record[field], str):
                    cleaned_record[field] = re.sub(pattern, '', cleaned_record[field])
            else:
                for key, value in cleaned_record.items():
                    if isinstance(value, str):
                        cleaned_record[key] = re.sub(pattern, '', value)
            cleaned.append(cleaned_record)
        return cleaned
    
    def _calculate_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算统计信息"""
        if not data:
            return {}
        
        return {
            'total_records': len(data),
            'fields': list(data[0].keys()) if data else []
        }
    
    def get_cleaning_stats(self) -> Dict[str, Any]:
        """
        获取清理统计
        
        Returns:
            清理统计
        """
        total_cleanings = len(self.cleaning_history)
        total_removed = sum(r.removed_count for r in self.cleaning_history)
        total_original = sum(r.original_count for r in self.cleaning_history)
        
        if total_cleanings > 0:
            avg_time = sum(r.cleaning_time for r in self.cleaning_history) / total_cleanings
        else:
            avg_time = 0.0
        
        return {
            'total_cleanings': total_cleanings,
            'total_removed': total_removed,
            'total_original': total_original,
            'removal_rate': (total_removed / total_original * 100) if total_original > 0 else 0.0,
            'average_cleaning_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    cleaning = DataCleaning()
    
    # 清理数据
    data = [
        {'id': 1, 'name': '  Alice  ', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': None},
        {'id': 1, 'name': 'Alice', 'age': 25}  # 重复
    ]
    
    rules = [
        CleaningRule('rule1', CleaningOperation.TRIM, 'name'),
        CleaningRule('rule2', CleaningOperation.REMOVE_NULLS, 'age'),
        CleaningRule('rule3', CleaningOperation.REMOVE_DUPLICATES, 'id')
    ]
    
    result = cleaning.clean(data, rules)
    print(f"清理结果: 原始={result.original_count}, 清理后={result.cleaned_count}, 移除={result.removed_count}")


if __name__ == '__main__':
    main()
