"""
数据一致性模块

专注于数据一致性检查、一致性保证、一致性修复
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConsistencyLevel(Enum):
    """一致性级别"""
    STRONG = "strong"  # 强一致性
    EVENTUAL = "eventual"  # 最终一致性
    WEAK = "weak"  # 弱一致性


class ConsistencyViolation(Enum):
    """一致性违反类型"""
    DUPLICATE = "duplicate"  # 重复
    MISSING = "missing"  # 缺失
    MISMATCH = "mismatch"  # 不匹配
    ORPHAN = "orphan"  # 孤儿记录
    REFERENCE_INTEGRITY = "reference_integrity"  # 引用完整性


@dataclass
class ConsistencyCheck:
    """一致性检查"""
    check_id: str
    check_type: str
    source: str
    target: Optional[str] = None
    constraints: Dict[str, Any] = None


@dataclass
class ConsistencyResult:
    """一致性结果"""
    check_id: str
    consistent: bool
    violations: List[Dict[str, Any]] = None
    checked_at: datetime = None


class DataConsistency:
    """
    数据一致性检查器
    
    专注于数据一致性检查、一致性保证、一致性修复
    """
    
    def __init__(self):
        self.checks: Dict[str, ConsistencyCheck] = {}
        self.check_results: List[ConsistencyResult] = []
        self.data_stores: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_data_store(self, store_id: str, data: List[Dict[str, Any]]):
        """
        注册数据存储
        
        Args:
            store_id: 存储ID
            data: 数据列表
        """
        self.data_stores[store_id] = data
    
    def create_check(self, check_config: Dict[str, Any]) -> ConsistencyCheck:
        """
        创建一致性检查
        
        Args:
            check_config: 检查配置
            
        Returns:
            一致性检查对象
        """
        check_id = check_config.get('check_id', f"check_{datetime.utcnow().timestamp()}")
        
        check = ConsistencyCheck(
            check_id=check_id,
            check_type=check_config.get('check_type', 'duplicate'),
            source=check_config['source'],
            target=check_config.get('target'),
            constraints=check_config.get('constraints', {})
        )
        
        self.checks[check_id] = check
        return check
    
    def check_consistency(self, check_id: str) -> ConsistencyResult:
        """
        检查一致性
        
        Args:
            check_id: 检查ID
            
        Returns:
            一致性结果
        """
        if check_id not in self.checks:
            raise ValueError(f"检查不存在: {check_id}")
        
        check = self.checks[check_id]
        
        if check.source not in self.data_stores:
            raise ValueError(f"数据存储不存在: {check.source}")
        
        source_data = self.data_stores[check.source]
        target_data = self.data_stores.get(check.target) if check.target else None
        
        violations = []
        
        # 根据检查类型执行检查
        if check.check_type == 'duplicate':
            violations = self._check_duplicates(source_data, check.constraints)
        elif check.check_type == 'missing':
            violations = self._check_missing(source_data, check.constraints)
        elif check.check_type == 'mismatch':
            if target_data:
                violations = self._check_mismatch(source_data, target_data, check.constraints)
        elif check.check_type == 'orphan':
            violations = self._check_orphans(source_data, check.constraints)
        elif check.check_type == 'reference_integrity':
            violations = self._check_reference_integrity(source_data, check.constraints)
        
        result = ConsistencyResult(
            check_id=check_id,
            consistent=len(violations) == 0,
            violations=violations,
            checked_at=datetime.utcnow()
        )
        
        self.check_results.append(result)
        return result
    
    def _check_duplicates(self, data: List[Dict[str, Any]],
                         constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查重复"""
        violations = []
        key_fields = constraints.get('key_fields', [])
        
        if not key_fields:
            return violations
        
        seen = {}
        for i, record in enumerate(data):
            key = tuple(record.get(f) for f in key_fields)
            
            if key in seen:
                violations.append({
                    'type': ConsistencyViolation.DUPLICATE.value,
                    'record_index': i,
                    'duplicate_of': seen[key],
                    'key': key,
                    'message': f'记录 {i} 与记录 {seen[key]} 重复'
                })
            else:
                seen[key] = i
        
        return violations
    
    def _check_missing(self, data: List[Dict[str, Any]],
                      constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查缺失"""
        violations = []
        required_fields = constraints.get('required_fields', [])
        
        for i, record in enumerate(data):
            missing_fields = [f for f in required_fields if f not in record or record[f] is None]
            if missing_fields:
                violations.append({
                    'type': ConsistencyViolation.MISSING.value,
                    'record_index': i,
                    'missing_fields': missing_fields,
                    'message': f'记录 {i} 缺少必需字段: {missing_fields}'
                })
        
        return violations
    
    def _check_mismatch(self, source_data: List[Dict[str, Any]],
                       target_data: List[Dict[str, Any]],
                       constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查不匹配"""
        violations = []
        key_fields = constraints.get('key_fields', [])
        compare_fields = constraints.get('compare_fields', [])
        
        # 构建索引
        target_index = {}
        for record in target_data:
            key = tuple(record.get(f) for f in key_fields)
            target_index[key] = record
        
        # 检查源数据
        for i, source_record in enumerate(source_data):
            key = tuple(source_record.get(f) for f in key_fields)
            
            if key in target_index:
                target_record = target_index[key]
                
                for field in compare_fields:
                    source_value = source_record.get(field)
                    target_value = target_record.get(field)
                    
                    if source_value != target_value:
                        violations.append({
                            'type': ConsistencyViolation.MISMATCH.value,
                            'record_index': i,
                            'field': field,
                            'source_value': source_value,
                            'target_value': target_value,
                            'message': f'记录 {i} 字段 {field} 不匹配'
                        })
        
        return violations
    
    def _check_orphans(self, data: List[Dict[str, Any]],
                      constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查孤儿记录"""
        violations = []
        foreign_key_field = constraints.get('foreign_key_field')
        reference_store = constraints.get('reference_store')
        
        if not foreign_key_field or not reference_store:
            return violations
        
        if reference_store not in self.data_stores:
            return violations
        
        reference_data = self.data_stores[reference_store]
        reference_keys = {record.get('id') for record in reference_data}
        
        for i, record in enumerate(data):
            fk_value = record.get(foreign_key_field)
            if fk_value and fk_value not in reference_keys:
                violations.append({
                    'type': ConsistencyViolation.ORPHAN.value,
                    'record_index': i,
                    'foreign_key_field': foreign_key_field,
                    'foreign_key_value': fk_value,
                    'message': f'记录 {i} 的外键 {foreign_key_field}={fk_value} 在引用表中不存在'
                })
        
        return violations
    
    def _check_reference_integrity(self, data: List[Dict[str, Any]],
                                  constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查引用完整性"""
        # 使用孤儿检查来实现引用完整性检查
        return self._check_orphans(data, constraints)
    
    def fix_violations(self, check_id: str, fix_strategy: Callable[[Dict[str, Any]], Any]) -> Dict[str, Any]:
        """
        修复一致性违反
        
        Args:
            check_id: 检查ID
            fix_strategy: 修复策略函数
            
        Returns:
            修复结果
        """
        if check_id not in self.checks:
            return {'error': '检查不存在'}
        
        check = self.checks[check_id]
        
        # 获取最新的检查结果
        latest_result = None
        for result in reversed(self.check_results):
            if result.check_id == check_id:
                latest_result = result
                break
        
        if not latest_result or latest_result.consistent:
            return {'message': '没有需要修复的违反'}
        
        fixed_count = 0
        
        for violation in latest_result.violations:
            try:
                fix_strategy(violation)
                fixed_count += 1
            except Exception as e:
                logger.error(f"修复失败: {violation}, 错误: {e}")
        
        return {
            'check_id': check_id,
            'total_violations': len(latest_result.violations),
            'fixed_count': fixed_count,
            'remaining_count': len(latest_result.violations) - fixed_count
        }
    
    def get_consistency_stats(self) -> Dict[str, Any]:
        """
        获取一致性统计
        
        Returns:
            一致性统计
        """
        total_checks = len(self.check_results)
        consistent_checks = sum(1 for r in self.check_results if r.consistent)
        total_violations = sum(len(r.violations or []) for r in self.check_results)
        
        return {
            'total_checks': total_checks,
            'consistent_checks': consistent_checks,
            'inconsistent_checks': total_checks - consistent_checks,
            'total_violations': total_violations,
            'consistency_rate': (consistent_checks / total_checks * 100) if total_checks > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    consistency = DataConsistency()
    
    # 注册数据存储
    consistency.register_data_store('users', [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': 30},
        {'id': 1, 'name': 'Alice', 'age': 25}  # 重复
    ])
    
    # 创建检查
    check = consistency.create_check({
        'check_type': 'duplicate',
        'source': 'users',
        'constraints': {
            'key_fields': ['id']
        }
    })
    
    # 检查一致性
    result = consistency.check_consistency(check.check_id)
    print(f"一致性检查: 一致={result.consistent}, 违反数={len(result.violations or [])}")


if __name__ == '__main__':
    main()
