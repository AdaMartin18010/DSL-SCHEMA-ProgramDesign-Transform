"""
数据审计模块

专注于数据审计、变更追踪、审计日志
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """审计操作"""
    CREATE = "create"  # 创建
    READ = "read"  # 读取
    UPDATE = "update"  # 更新
    DELETE = "delete"  # 删除
    EXPORT = "export"  # 导出
    IMPORT = "import"  # 导入


class AuditLevel(Enum):
    """审计级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditLog:
    """审计日志"""
    log_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    level: AuditLevel = AuditLevel.INFO
    metadata: Dict[str, Any] = None


class DataAudit:
    """
    数据审计器
    
    专注于数据审计、变更追踪、审计日志
    """
    
    def __init__(self):
        self.audit_logs: List[AuditLog] = []
        self.audit_config: Dict[str, Any] = {
            'enabled': True,
            'retention_days': 365
        }
    
    def log_action(self, action: AuditAction, resource_type: str, resource_id: str,
                  user_id: Optional[str] = None, ip_address: Optional[str] = None,
                  old_value: Optional[Dict[str, Any]] = None,
                  new_value: Optional[Dict[str, Any]] = None,
                  level: AuditLevel = AuditLevel.INFO,
                  metadata: Optional[Dict[str, Any]] = None) -> AuditLog:
        """
        记录审计日志
        
        Args:
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            user_id: 用户ID
            ip_address: IP地址
            old_value: 旧值
            new_value: 新值
            level: 审计级别
            metadata: 元数据
            
        Returns:
            审计日志对象
        """
        if not self.audit_config.get('enabled', True):
            return None
        
        log_id = f"audit_{datetime.utcnow().timestamp()}"
        
        # 计算变更
        changes = None
        if old_value is not None and new_value is not None:
            changes = self._calculate_changes(old_value, new_value)
        
        log = AuditLog(
            log_id=log_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address=ip_address,
            old_value=old_value,
            new_value=new_value,
            changes=changes,
            timestamp=datetime.utcnow(),
            level=level,
            metadata=metadata or {}
        )
        
        self.audit_logs.append(log)
        return log
    
    def _calculate_changes(self, old_value: Dict[str, Any],
                          new_value: Dict[str, Any]) -> Dict[str, Any]:
        """计算变更"""
        changes = {
            'added': {},
            'removed': {},
            'modified': {}
        }
        
        all_fields = set(old_value.keys()) | set(new_value.keys())
        
        for field in all_fields:
            old_val = old_value.get(field)
            new_val = new_value.get(field)
            
            if field not in old_value:
                changes['added'][field] = new_val
            elif field not in new_value:
                changes['removed'][field] = old_val
            elif old_val != new_val:
                changes['modified'][field] = {
                    'old': old_val,
                    'new': new_val
                }
        
        return changes
    
    def query_audit_logs(self, resource_type: Optional[str] = None,
                        resource_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        action: Optional[AuditAction] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[AuditLog]:
        """
        查询审计日志
        
        Args:
            resource_type: 资源类型（可选）
            resource_id: 资源ID（可选）
            user_id: 用户ID（可选）
            action: 操作类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 限制数量
            
        Returns:
            审计日志列表
        """
        logs = self.audit_logs
        
        # 过滤
        if resource_type:
            logs = [l for l in logs if l.resource_type == resource_type]
        
        if resource_id:
            logs = [l for l in logs if l.resource_id == resource_id]
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if action:
            logs = [l for l in logs if l.action == action]
        
        if start_time:
            logs = [l for l in logs if l.timestamp >= start_time]
        
        if end_time:
            logs = [l for l in logs if l.timestamp <= end_time]
        
        # 按时间排序
        logs.sort(key=lambda l: l.timestamp, reverse=True)
        
        return logs[:limit]
    
    def get_resource_history(self, resource_type: str, resource_id: str) -> List[AuditLog]:
        """
        获取资源历史
        
        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            
        Returns:
            审计日志列表
        """
        return self.query_audit_logs(resource_type=resource_type, resource_id=resource_id)
    
    def get_user_activity(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """
        获取用户活动
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            审计日志列表
        """
        return self.query_audit_logs(user_id=user_id, limit=limit)
    
    def get_audit_summary(self, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取审计摘要
        
        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            审计摘要
        """
        logs = self.audit_logs
        
        if start_time:
            logs = [l for l in logs if l.timestamp >= start_time]
        
        if end_time:
            logs = [l for l in logs if l.timestamp <= end_time]
        
        action_counts = {}
        user_counts = {}
        resource_type_counts = {}
        
        for log in logs:
            action_counts[log.action.value] = action_counts.get(log.action.value, 0) + 1
            if log.user_id:
                user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1
            resource_type_counts[log.resource_type] = resource_type_counts.get(log.resource_type, 0) + 1
        
        return {
            'total_logs': len(logs),
            'action_counts': action_counts,
            'user_counts': user_counts,
            'resource_type_counts': resource_type_counts,
            'start_time': start_time.isoformat() if start_time else None,
            'end_time': end_time.isoformat() if end_time else None
        }


def main():
    """主函数 - 示例用法"""
    audit = DataAudit()
    
    # 记录审计日志
    log = audit.log_action(
        action=AuditAction.UPDATE,
        resource_type='user',
        resource_id='user_1',
        user_id='admin',
        old_value={'name': 'Alice', 'age': 25},
        new_value={'name': 'Alice', 'age': 26}
    )
    
    print(f"审计日志: {log.log_id}, 操作={log.action.value}")
    
    # 查询审计日志
    logs = audit.query_audit_logs(resource_type='user', resource_id='user_1')
    print(f"查询结果: {len(logs)} 条日志")


if __name__ == '__main__':
    main()
