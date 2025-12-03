"""
版本控制

实现Schema版本管理
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import semver
from .storage import SchemaVersioningStorage


class SchemaVersionControl:
    """Schema版本控制器"""
    
    def __init__(self, storage: SchemaVersioningStorage):
        """
        初始化版本控制器
        
        Args:
            storage: Schema版本管理存储管理器
        """
        self.storage = storage
    
    def create_version(self, schema_id: str, schema_content: Dict[str, Any],
                      version: Optional[str] = None,
                      changelog: Optional[str] = None) -> Optional[str]:
        """
        创建新版本
        
        Args:
            schema_id: Schema ID
            schema_content: Schema内容
            version: 版本号（如果为None，则自动生成）
            changelog: 变更日志
            
        Returns:
            版本号（如果成功）
        """
        # 如果没有指定版本号，自动生成
        if version is None:
            current_version = self.storage.get_current_version(schema_id)
            if current_version:
                # 递增版本号
                current_ver = current_version['version']
                try:
                    # 尝试解析语义化版本
                    ver = semver.VersionInfo.parse(current_ver)
                    version = str(ver.bump_patch())  # 递增补丁版本
                except:
                    # 如果不是语义化版本，简单递增
                    version = f"{current_ver}.1"
            else:
                version = "1.0.0"
        
        # 创建版本
        success = self.storage.create_version(
            schema_id=schema_id,
            version=version,
            schema_content=schema_content,
            changelog=changelog
        )
        
        return version if success else None
    
    def get_version(self, schema_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取版本
        
        Args:
            schema_id: Schema ID
            version: 版本号（如果为None，则获取当前版本）
            
        Returns:
            版本信息（如果存在）
        """
        if version is None:
            return self.storage.get_current_version(schema_id)
        else:
            # 获取指定版本（需要扩展storage方法）
            return None
    
    def list_versions(self, schema_id: str) -> List[Dict[str, Any]]:
        """
        列出所有版本
        
        Args:
            schema_id: Schema ID
            
        Returns:
            版本列表
        """
        return self.storage.get_version_history(schema_id)
    
    def compare_versions(self, schema_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        比较两个版本
        
        Args:
            schema_id: Schema ID
            version1: 版本1
            version2: 版本2
            
        Returns:
            比较结果
        """
        # 获取两个版本的内容
        v1_content = self.get_version(schema_id, version1)
        v2_content = self.get_version(schema_id, version2)
        
        if not v1_content or not v2_content:
            return {'error': '版本不存在'}
        
        # 比较内容（简化实现）
        differences = self._compare_content(
            v1_content.get('schema_content', {}),
            v2_content.get('schema_content', {})
        )
        
        return {
            'version1': version1,
            'version2': version2,
            'differences': differences
        }
    
    def _compare_content(self, content1: Dict[str, Any],
                        content2: Dict[str, Any]) -> Dict[str, Any]:
        """比较内容"""
        differences = {
            'added': [],
            'removed': [],
            'modified': []
        }
        
        # 简化实现：比较键
        keys1 = set(content1.keys())
        keys2 = set(content2.keys())
        
        differences['added'] = list(keys2 - keys1)
        differences['removed'] = list(keys1 - keys2)
        
        # 比较共同键的值
        common_keys = keys1 & keys2
        for key in common_keys:
            if content1[key] != content2[key]:
                differences['modified'].append(key)
        
        return differences
