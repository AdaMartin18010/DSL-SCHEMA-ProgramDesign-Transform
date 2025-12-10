"""
数据对账模块

专注于数据一致性检查、数据对账、数据差异分析
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReconciliationType(Enum):
    """对账类型"""
    FIELD_LEVEL = "field_level"  # 字段级对账
    RECORD_LEVEL = "record_level"  # 记录级对账
    AGGREGATE_LEVEL = "aggregate_level"  # 聚合级对账


class DifferenceType(Enum):
    """差异类型"""
    MISSING = "missing"  # 缺失
    EXTRA = "extra"  # 多余
    MISMATCH = "mismatch"  # 不匹配
    DUPLICATE = "duplicate"  # 重复


@dataclass
class ReconciliationResult:
    """对账结果"""
    reconciliation_id: str
    source_count: int
    target_count: int
    matched_count: int
    differences: List[Dict[str, Any]]
    created_at: datetime


@dataclass
class Difference:
    """差异"""
    difference_id: str
    difference_type: DifferenceType
    field: Optional[str] = None
    source_value: Any = None
    target_value: Any = None
    record_id: Optional[str] = None
    description: Optional[str] = None


class DataReconciliation:
    """
    数据对账器
    
    专注于数据一致性检查、数据对账、数据差异分析
    """
    
    def __init__(self):
        self.reconciliations: Dict[str, ReconciliationResult] = {}
    
    def reconcile(self, source_data: List[Dict[str, Any]],
                 target_data: List[Dict[str, Any]],
                 key_fields: List[str],
                 reconciliation_type: ReconciliationType = ReconciliationType.RECORD_LEVEL) -> ReconciliationResult:
        """
        对账数据
        
        Args:
            source_data: 源数据列表
            target_data: 目标数据列表
            key_fields: 关键字段列表（用于匹配记录）
            reconciliation_type: 对账类型
            
        Returns:
            对账结果
        """
        reconciliation_id = f"recon_{datetime.utcnow().timestamp()}"
        
        if reconciliation_type == ReconciliationType.RECORD_LEVEL:
            return self._reconcile_records(source_data, target_data, key_fields, reconciliation_id)
        elif reconciliation_type == ReconciliationType.FIELD_LEVEL:
            return self._reconcile_fields(source_data, target_data, key_fields, reconciliation_id)
        elif reconciliation_type == ReconciliationType.AGGREGATE_LEVEL:
            return self._reconcile_aggregates(source_data, target_data, key_fields, reconciliation_id)
        else:
            raise ValueError(f"不支持的对账类型: {reconciliation_type}")
    
    def _reconcile_records(self, source_data: List[Dict[str, Any]],
                          target_data: List[Dict[str, Any]],
                          key_fields: List[str],
                          reconciliation_id: str) -> ReconciliationResult:
        """记录级对账"""
        # 构建索引
        source_index = self._build_index(source_data, key_fields)
        target_index = self._build_index(target_data, key_fields)
        
        differences = []
        matched_count = 0
        
        # 检查源数据中的记录
        for key, source_record in source_index.items():
            if key in target_index:
                # 记录存在，检查字段是否匹配
                target_record = target_index[key]
                field_diffs = self._compare_records(source_record, target_record, key_fields)
                if field_diffs:
                    differences.extend(field_diffs)
                else:
                    matched_count += 1
            else:
                # 源数据中存在但目标数据中不存在
                differences.append({
                    'difference_type': DifferenceType.MISSING.value,
                    'record_id': key,
                    'source_value': source_record,
                    'target_value': None,
                    'description': f'记录在目标数据中缺失'
                })
        
        # 检查目标数据中的额外记录
        for key, target_record in target_index.items():
            if key not in source_index:
                differences.append({
                    'difference_type': DifferenceType.EXTRA.value,
                    'record_id': key,
                    'source_value': None,
                    'target_value': target_record,
                    'description': f'记录在源数据中不存在'
                })
        
        result = ReconciliationResult(
            reconciliation_id=reconciliation_id,
            source_count=len(source_data),
            target_count=len(target_data),
            matched_count=matched_count,
            differences=differences,
            created_at=datetime.utcnow()
        )
        
        self.reconciliations[reconciliation_id] = result
        return result
    
    def _reconcile_fields(self, source_data: List[Dict[str, Any]],
                         target_data: List[Dict[str, Any]],
                         key_fields: List[str],
                         reconciliation_id: str) -> ReconciliationResult:
        """字段级对账"""
        # 简化实现：基于记录级对账
        return self._reconcile_records(source_data, target_data, key_fields, reconciliation_id)
    
    def _reconcile_aggregates(self, source_data: List[Dict[str, Any]],
                             target_data: List[Dict[str, Any]],
                             key_fields: List[str],
                             reconciliation_id: str) -> ReconciliationResult:
        """聚合级对账"""
        # 计算聚合值
        source_aggregate = self._calculate_aggregate(source_data)
        target_aggregate = self._calculate_aggregate(target_data)
        
        differences = []
        
        # 比较聚合值
        for field, source_value in source_aggregate.items():
            target_value = target_aggregate.get(field)
            if source_value != target_value:
                differences.append({
                    'difference_type': DifferenceType.MISMATCH.value,
                    'field': field,
                    'source_value': source_value,
                    'target_value': target_value,
                    'description': f'聚合值不匹配: {field}'
                })
        
        matched_count = len(source_aggregate) - len(differences)
        
        result = ReconciliationResult(
            reconciliation_id=reconciliation_id,
            source_count=len(source_data),
            target_count=len(target_data),
            matched_count=matched_count,
            differences=differences,
            created_at=datetime.utcnow()
        )
        
        self.reconciliations[reconciliation_id] = result
        return result
    
    def _build_index(self, data: List[Dict[str, Any]], key_fields: List[str]) -> Dict[str, Dict[str, Any]]:
        """构建索引"""
        index = {}
        
        for record in data:
            key = self._build_key(record, key_fields)
            if key:
                index[key] = record
        
        return index
    
    def _build_key(self, record: Dict[str, Any], key_fields: List[str]) -> Optional[str]:
        """构建键"""
        key_parts = []
        for field in key_fields:
            if field in record:
                key_parts.append(str(record[field]))
            else:
                return None  # 关键字段缺失
        
        return '|'.join(key_parts)
    
    def _compare_records(self, source_record: Dict[str, Any],
                        target_record: Dict[str, Any],
                        key_fields: List[str]) -> List[Dict[str, Any]]:
        """比较记录"""
        differences = []
        
        # 获取所有字段
        all_fields = set(source_record.keys()) | set(target_record.keys())
        
        for field in all_fields:
            if field in key_fields:
                continue  # 跳过关键字段
            
            source_value = source_record.get(field)
            target_value = target_record.get(field)
            
            if source_value != target_value:
                differences.append({
                    'difference_type': DifferenceType.MISMATCH.value,
                    'field': field,
                    'source_value': source_value,
                    'target_value': target_value,
                    'description': f'字段 {field} 值不匹配'
                })
        
        return differences
    
    def _calculate_aggregate(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算聚合值"""
        if not data:
            return {}
        
        # 获取所有数值字段
        numeric_fields = []
        for record in data:
            for field, value in record.items():
                if isinstance(value, (int, float)) and field not in numeric_fields:
                    numeric_fields.append(field)
        
        aggregates = {}
        
        for field in numeric_fields:
            values = [record.get(field) for record in data if field in record and isinstance(record[field], (int, float))]
            if values:
                aggregates[f'{field}_sum'] = sum(values)
                aggregates[f'{field}_avg'] = sum(values) / len(values)
                aggregates[f'{field}_min'] = min(values)
                aggregates[f'{field}_max'] = max(values)
                aggregates[f'{field}_count'] = len(values)
        
        return aggregates
    
    def find_duplicates(self, data: List[Dict[str, Any]], key_fields: List[str]) -> List[Dict[str, Any]]:
        """
        查找重复记录
        
        Args:
            data: 数据列表
            key_fields: 关键字段列表
            
        Returns:
            重复记录列表
        """
        seen = {}
        duplicates = []
        
        for i, record in enumerate(data):
            key = self._build_key(record, key_fields)
            if key:
                if key in seen:
                    duplicates.append({
                        'record_id': key,
                        'first_index': seen[key],
                        'duplicate_index': i,
                        'record': record
                    })
                else:
                    seen[key] = i
        
        return duplicates
    
    def get_reconciliation_summary(self, reconciliation_id: str) -> Dict[str, Any]:
        """
        获取对账摘要
        
        Args:
            reconciliation_id: 对账ID
            
        Returns:
            对账摘要
        """
        if reconciliation_id not in self.reconciliations:
            return {'error': '对账结果不存在'}
        
        result = self.reconciliations[reconciliation_id]
        
        error_count = sum(1 for d in result.differences if d.get('difference_type') == DifferenceType.MISSING.value)
        mismatch_count = sum(1 for d in result.differences if d.get('difference_type') == DifferenceType.MISMATCH.value)
        extra_count = sum(1 for d in result.differences if d.get('difference_type') == DifferenceType.EXTRA.value)
        
        match_rate = (result.matched_count / max(result.source_count, result.target_count) * 100) if max(result.source_count, result.target_count) > 0 else 0.0
        
        return {
            'reconciliation_id': reconciliation_id,
            'source_count': result.source_count,
            'target_count': result.target_count,
            'matched_count': result.matched_count,
            'match_rate': match_rate,
            'total_differences': len(result.differences),
            'error_count': error_count,
            'mismatch_count': mismatch_count,
            'extra_count': extra_count,
            'created_at': result.created_at.isoformat()
        }


def main():
    """主函数 - 示例用法"""
    reconciliation = DataReconciliation()
    
    # 对账数据
    source_data = [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': 30}
    ]
    
    target_data = [
        {'id': 1, 'name': 'Alice', 'age': 26},
        {'id': 2, 'name': 'Bob', 'age': 30},
        {'id': 3, 'name': 'Charlie', 'age': 35}
    ]
    
    result = reconciliation.reconcile(
        source_data,
        target_data,
        key_fields=['id'],
        reconciliation_type=ReconciliationType.RECORD_LEVEL
    )
    
    summary = reconciliation.get_reconciliation_summary(result.reconciliation_id)
    print(f"对账摘要: {summary}")


if __name__ == '__main__':
    main()
