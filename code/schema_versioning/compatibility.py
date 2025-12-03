"""
兼容性检查

检查Schema版本间的兼容性
"""

from typing import Dict, Any, Optional
from .storage import SchemaVersioningStorage
from .version_control import SchemaVersionControl


class CompatibilityChecker:
    """兼容性检查器"""
    
    def __init__(self, storage: SchemaVersioningStorage):
        """
        初始化兼容性检查器
        
        Args:
            storage: Schema版本管理存储管理器
        """
        self.storage = storage
        self.version_control = SchemaVersionControl(storage)
    
    def check_compatibility(self, schema_id: str, from_version: str,
                           to_version: str) -> Dict[str, Any]:
        """
        检查兼容性
        
        Args:
            schema_id: Schema ID
            from_version: 源版本
            to_version: 目标版本
            
        Returns:
            兼容性报告
        """
        # 比较两个版本
        comparison = self.version_control.compare_versions(
            schema_id, from_version, to_version
        )
        
        if 'error' in comparison:
            return comparison
        
        differences = comparison.get('differences', {})
        
        # 分析兼容性
        is_compatible = self._analyze_compatibility(differences)
        breaking_changes = self._identify_breaking_changes(differences)
        
        return {
            'schema_id': schema_id,
            'from_version': from_version,
            'to_version': to_version,
            'is_compatible': is_compatible,
            'compatibility_level': self._get_compatibility_level(is_compatible, breaking_changes),
            'breaking_changes': breaking_changes,
            'differences': differences
        }
    
    def _analyze_compatibility(self, differences: Dict[str, Any]) -> int:
        """
        分析兼容性
        
        Returns:
            0: 不兼容, 1: 兼容, 2: 部分兼容
        """
        # 如果有删除，不兼容
        if differences.get('removed'):
            return 0
        
        # 如果有修改，部分兼容
        if differences.get('modified'):
            return 2
        
        # 如果只有添加，兼容
        if differences.get('added') and not differences.get('removed') and not differences.get('modified'):
            return 1
        
        return 1  # 默认兼容
    
    def _identify_breaking_changes(self, differences: Dict[str, Any]) -> List[str]:
        """识别破坏性变更"""
        breaking_changes = []
        
        # 删除的字段是破坏性变更
        if differences.get('removed'):
            breaking_changes.extend([f"删除字段: {field}" for field in differences['removed']])
        
        # 修改的字段可能是破坏性变更
        if differences.get('modified'):
            breaking_changes.extend([f"修改字段: {field}" for field in differences['modified']])
        
        return breaking_changes
    
    def _get_compatibility_level(self, is_compatible: int,
                                 breaking_changes: List[str]) -> str:
        """获取兼容性级别"""
        if is_compatible == 0:
            return 'incompatible'
        elif is_compatible == 2 or breaking_changes:
            return 'partially_compatible'
        else:
            return 'compatible'
