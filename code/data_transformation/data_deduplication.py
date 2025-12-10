"""
数据去重模块

专注于数据去重、重复检测、数据清洗
"""

from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class DeduplicationMethod(Enum):
    """去重方法"""
    EXACT = "exact"  # 精确匹配
    FUZZY = "fuzzy"  # 模糊匹配
    SIMILARITY = "similarity"  # 相似度匹配
    HASH = "hash"  # 哈希匹配


@dataclass
class DuplicateGroup:
    """重复组"""
    group_id: str
    records: List[Dict[str, Any]]
    similarity_score: float = 1.0
    representative_record: Optional[Dict[str, Any]] = None


class DataDeduplication:
    """
    数据去重器
    
    专注于数据去重、重复检测、数据清洗
    """
    
    def __init__(self):
        self.duplicate_groups: Dict[str, DuplicateGroup] = {}
    
    def find_duplicates(self, data: List[Dict[str, Any]],
                       key_fields: Optional[List[str]] = None,
                       method: DeduplicationMethod = DeduplicationMethod.EXACT) -> List[DuplicateGroup]:
        """
        查找重复记录
        
        Args:
            data: 数据列表
            key_fields: 关键字段列表（可选）
            method: 去重方法
            
        Returns:
            重复组列表
        """
        if method == DeduplicationMethod.EXACT:
            return self._find_exact_duplicates(data, key_fields)
        elif method == DeduplicationMethod.HASH:
            return self._find_hash_duplicates(data, key_fields)
        elif method == DeduplicationMethod.FUZZY:
            return self._find_fuzzy_duplicates(data, key_fields)
        elif method == DeduplicationMethod.SIMILARITY:
            return self._find_similarity_duplicates(data, key_fields)
        else:
            raise ValueError(f"不支持的去重方法: {method}")
    
    def _find_exact_duplicates(self, data: List[Dict[str, Any]],
                               key_fields: Optional[List[str]]) -> List[DuplicateGroup]:
        """查找精确重复"""
        groups = {}
        
        for i, record in enumerate(data):
            if key_fields:
                # 使用关键字段构建键
                key = self._build_key(record, key_fields)
            else:
                # 使用所有字段构建键
                key = self._build_record_key(record)
            
            if key:
                if key not in groups:
                    groups[key] = []
                groups[key].append((i, record))
        
        # 构建重复组
        duplicate_groups = []
        for key, records in groups.items():
            if len(records) > 1:
                group_id = f"group_{len(duplicate_groups)}"
                group = DuplicateGroup(
                    group_id=group_id,
                    records=[r[1] for r in records],
                    representative_record=records[0][1]  # 使用第一个记录作为代表
                )
                duplicate_groups.append(group)
                self.duplicate_groups[group_id] = group
        
        return duplicate_groups
    
    def _find_hash_duplicates(self, data: List[Dict[str, Any]],
                             key_fields: Optional[List[str]]) -> List[DuplicateGroup]:
        """查找哈希重复"""
        groups = {}
        
        for i, record in enumerate(data):
            if key_fields:
                key = self._build_key(record, key_fields)
            else:
                key = self._build_record_key(record)
            
            if key:
                # 计算哈希值
                hash_value = hashlib.md5(key.encode()).hexdigest()
                
                if hash_value not in groups:
                    groups[hash_value] = []
                groups[hash_value].append((i, record))
        
        # 构建重复组
        duplicate_groups = []
        for hash_value, records in groups.items():
            if len(records) > 1:
                group_id = f"group_{len(duplicate_groups)}"
                group = DuplicateGroup(
                    group_id=group_id,
                    records=[r[1] for r in records],
                    representative_record=records[0][1]
                )
                duplicate_groups.append(group)
                self.duplicate_groups[group_id] = group
        
        return duplicate_groups
    
    def _find_fuzzy_duplicates(self, data: List[Dict[str, Any]],
                              key_fields: Optional[List[str]]) -> List[DuplicateGroup]:
        """查找模糊重复"""
        # 简化实现：基于精确匹配
        return self._find_exact_duplicates(data, key_fields)
    
    def _find_similarity_duplicates(self, data: List[Dict[str, Any]],
                                   key_fields: Optional[List[str]],
                                   threshold: float = 0.8) -> List[DuplicateGroup]:
        """查找相似度重复"""
        # 简化实现：基于精确匹配
        return self._find_exact_duplicates(data, key_fields)
    
    def _build_key(self, record: Dict[str, Any], key_fields: List[str]) -> Optional[str]:
        """构建键"""
        key_parts = []
        for field in key_fields:
            if field in record:
                key_parts.append(str(record[field]))
            else:
                return None
        
        return '|'.join(key_parts)
    
    def _build_record_key(self, record: Dict[str, Any]) -> str:
        """构建记录键"""
        sorted_items = sorted(record.items())
        key_parts = [f"{k}:{v}" for k, v in sorted_items]
        return '|'.join(key_parts)
    
    def remove_duplicates(self, data: List[Dict[str, Any]],
                         key_fields: Optional[List[str]] = None,
                         method: DeduplicationMethod = DeduplicationMethod.EXACT,
                         keep: str = 'first') -> List[Dict[str, Any]]:
        """
        移除重复记录
        
        Args:
            data: 数据列表
            key_fields: 关键字段列表（可选）
            method: 去重方法
            keep: 保留策略（'first', 'last', 'all'）
            
        Returns:
            去重后的数据列表
        """
        if keep == 'all':
            return data
        
        seen = set()
        result = []
        
        for record in data:
            if key_fields:
                key = self._build_key(record, key_fields)
            else:
                key = self._build_record_key(record)
            
            if key and key not in seen:
                seen.add(key)
                result.append(record)
            elif not key:
                # 关键字段缺失，保留记录
                result.append(record)
        
        return result
    
    def merge_duplicates(self, duplicate_group: DuplicateGroup,
                        merge_strategy: Callable[[List[Dict[str, Any]]], Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并重复记录
        
        Args:
            duplicate_group: 重复组
            merge_strategy: 合并策略函数
            
        Returns:
            合并后的记录
        """
        try:
            merged_record = merge_strategy(duplicate_group.records)
            return merged_record
        except Exception as e:
            logger.error(f"合并重复记录失败: {e}")
            return duplicate_group.representative_record or duplicate_group.records[0]
    
    def get_deduplication_stats(self, duplicate_groups: List[DuplicateGroup]) -> Dict[str, Any]:
        """
        获取去重统计
        
        Args:
            duplicate_groups: 重复组列表
            
        Returns:
            去重统计
        """
        total_duplicates = sum(len(group.records) for group in duplicate_groups)
        total_groups = len(duplicate_groups)
        total_unique = sum(1 for group in duplicate_groups)
        
        return {
            'total_duplicate_groups': total_groups,
            'total_duplicate_records': total_duplicates,
            'total_unique_records': total_unique,
            'average_group_size': total_duplicates / total_groups if total_groups > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    deduplication = DataDeduplication()
    
    # 查找重复
    data = [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': 30},
        {'id': 1, 'name': 'Alice', 'age': 25},  # 重复
        {'id': 3, 'name': 'Charlie', 'age': 35}
    ]
    
    duplicates = deduplication.find_duplicates(data, key_fields=['id'])
    print(f"找到 {len(duplicates)} 个重复组")
    
    # 移除重复
    cleaned_data = deduplication.remove_duplicates(data, key_fields=['id'], keep='first')
    print(f"去重后记录数: {len(cleaned_data)}")


if __name__ == '__main__':
    main()
