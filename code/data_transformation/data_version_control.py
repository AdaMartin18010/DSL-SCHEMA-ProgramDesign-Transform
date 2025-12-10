"""
数据版本控制模块

专注于数据版本管理、版本比较、版本回滚
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """版本状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 活跃
    ARCHIVED = "archived"  # 已归档
    DELETED = "deleted"  # 已删除


@dataclass
class DataVersion:
    """数据版本"""
    version_id: str
    data_id: str
    version_number: str
    data: Dict[str, Any]
    checksum: str
    status: VersionStatus
    created_at: datetime
    created_by: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class VersionDiff:
    """版本差异"""
    version1_id: str
    version2_id: str
    differences: List[Dict[str, Any]]
    added_fields: List[str]
    removed_fields: List[str]
    modified_fields: List[str]


class DataVersionControl:
    """
    数据版本控制器
    
    专注于数据版本管理、版本比较、版本回滚
    """
    
    def __init__(self):
        self.versions: Dict[str, List[DataVersion]] = {}  # data_id -> versions
        self.version_index: Dict[str, DataVersion] = {}  # version_id -> version
    
    def create_version(self, data_id: str, data: Dict[str, Any],
                      version_number: Optional[str] = None,
                      created_by: Optional[str] = None,
                      description: Optional[str] = None) -> DataVersion:
        """
        创建数据版本
        
        Args:
            data_id: 数据ID
            data: 数据
            version_number: 版本号（可选，自动生成）
            created_by: 创建者
            description: 描述
            
        Returns:
            数据版本对象
        """
        if version_number is None:
            # 自动生成版本号
            if data_id in self.versions:
                existing_versions = self.versions[data_id]
                version_number = f"{len(existing_versions) + 1}.0.0"
            else:
                version_number = "1.0.0"
        
        # 计算校验和
        data_json = json.dumps(data, sort_keys=True)
        checksum = hashlib.md5(data_json.encode()).hexdigest()
        
        version_id = f"version_{data_id}_{version_number}_{datetime.utcnow().timestamp()}"
        
        version = DataVersion(
            version_id=version_id,
            data_id=data_id,
            version_number=version_number,
            data=data,
            checksum=checksum,
            status=VersionStatus.DRAFT,
            created_at=datetime.utcnow(),
            created_by=created_by,
            description=description
        )
        
        if data_id not in self.versions:
            self.versions[data_id] = []
        
        self.versions[data_id].append(version)
        self.version_index[version_id] = version
        
        return version
    
    def get_version(self, version_id: str) -> Optional[DataVersion]:
        """
        获取版本
        
        Args:
            version_id: 版本ID
            
        Returns:
            数据版本对象
        """
        return self.version_index.get(version_id)
    
    def list_versions(self, data_id: str) -> List[DataVersion]:
        """
        列出数据的所有版本
        
        Args:
            data_id: 数据ID
            
        Returns:
            版本列表
        """
        if data_id not in self.versions:
            return []
        
        versions = self.versions[data_id]
        # 按创建时间排序
        versions.sort(key=lambda v: v.created_at, reverse=True)
        return versions
    
    def get_latest_version(self, data_id: str) -> Optional[DataVersion]:
        """
        获取最新版本
        
        Args:
            data_id: 数据ID
            
        Returns:
            最新版本
        """
        versions = self.list_versions(data_id)
        return versions[0] if versions else None
    
    def compare_versions(self, version1_id: str, version2_id: str) -> VersionDiff:
        """
        比较两个版本
        
        Args:
            version1_id: 版本1 ID
            version2_id: 版本2 ID
            
        Returns:
            版本差异
        """
        version1 = self.get_version(version1_id)
        version2 = self.get_version(version2_id)
        
        if not version1 or not version2:
            raise ValueError("版本不存在")
        
        data1 = version1.data
        data2 = version2.data
        
        # 找出差异
        differences = []
        added_fields = []
        removed_fields = []
        modified_fields = []
        
        all_fields = set(data1.keys()) | set(data2.keys())
        
        for field in all_fields:
            value1 = data1.get(field)
            value2 = data2.get(field)
            
            if field not in data1:
                added_fields.append(field)
                differences.append({
                    'field': field,
                    'type': 'added',
                    'old_value': None,
                    'new_value': value2
                })
            elif field not in data2:
                removed_fields.append(field)
                differences.append({
                    'field': field,
                    'type': 'removed',
                    'old_value': value1,
                    'new_value': None
                })
            elif value1 != value2:
                modified_fields.append(field)
                differences.append({
                    'field': field,
                    'type': 'modified',
                    'old_value': value1,
                    'new_value': value2
                })
        
        return VersionDiff(
            version1_id=version1_id,
            version2_id=version2_id,
            differences=differences,
            added_fields=added_fields,
            removed_fields=removed_fields,
            modified_fields=modified_fields
        )
    
    def rollback_to_version(self, data_id: str, version_id: str) -> DataVersion:
        """
        回滚到指定版本
        
        Args:
            data_id: 数据ID
            version_id: 版本ID
            
        Returns:
            回滚后的版本
        """
        target_version = self.get_version(version_id)
        
        if not target_version:
            raise ValueError(f"版本不存在: {version_id}")
        
        if target_version.data_id != data_id:
            raise ValueError(f"版本不属于该数据: {data_id}")
        
        # 创建新版本（回滚版本）
        rollback_version = self.create_version(
            data_id,
            target_version.data,
            version_number=f"rollback_{target_version.version_number}",
            description=f"回滚到版本 {target_version.version_number}"
        )
        
        rollback_version.status = VersionStatus.ACTIVE
        
        # 将之前的版本标记为已归档
        for version in self.versions[data_id]:
            if version.version_id != rollback_version.version_id:
                if version.status == VersionStatus.ACTIVE:
                    version.status = VersionStatus.ARCHIVED
        
        return rollback_version
    
    def set_version_status(self, version_id: str, status: VersionStatus) -> bool:
        """
        设置版本状态
        
        Args:
            version_id: 版本ID
            status: 状态
            
        Returns:
            是否成功
        """
        version = self.get_version(version_id)
        if not version:
            return False
        
        version.status = status
        return True
    
    def get_version_history(self, data_id: str) -> List[Dict[str, Any]]:
        """
        获取版本历史
        
        Args:
            data_id: 数据ID
            
        Returns:
            版本历史列表
        """
        versions = self.list_versions(data_id)
        
        return [
            {
                'version_id': v.version_id,
                'version_number': v.version_number,
                'status': v.status.value,
                'created_at': v.created_at.isoformat(),
                'created_by': v.created_by,
                'description': v.description,
                'checksum': v.checksum[:16] + '...'  # 只显示前16个字符
            }
            for v in versions
        ]


def main():
    """主函数 - 示例用法"""
    vc = DataVersionControl()
    
    # 创建版本
    data = {'id': 1, 'name': 'Alice', 'age': 25}
    version1 = vc.create_version('data_1', data, version_number='1.0.0')
    print(f"创建版本: {version1.version_number}")
    
    # 更新数据并创建新版本
    data['age'] = 26
    version2 = vc.create_version('data_1', data, version_number='1.1.0')
    print(f"创建版本: {version2.version_number}")
    
    # 比较版本
    diff = vc.compare_versions(version1.version_id, version2.version_id)
    print(f"版本差异: {len(diff.modified_fields)} 个字段被修改")


if __name__ == '__main__':
    main()
