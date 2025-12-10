"""
数据安全模块

专注于数据加密、数据脱敏、访问控制、安全审计
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """安全级别"""
    PUBLIC = "public"  # 公开
    INTERNAL = "internal"  # 内部
    CONFIDENTIAL = "confidential"  # 机密
    SECRET = "secret"  # 秘密


class MaskingType(Enum):
    """脱敏类型"""
    FULL = "full"  # 完全脱敏
    PARTIAL = "partial"  # 部分脱敏
    HASH = "hash"  # 哈希脱敏
    REPLACE = "replace"  # 替换脱敏


@dataclass
class SecurityRule:
    """安全规则"""
    rule_id: str
    field: str
    security_level: SecurityLevel
    masking_type: Optional[MaskingType] = None
    masking_config: Optional[Dict[str, Any]] = None


@dataclass
class AccessControl:
    """访问控制"""
    user_id: str
    resource: str
    permissions: List[str]
    expires_at: Optional[datetime] = None


class DataSecurity:
    """
    数据安全器
    
    专注于数据加密、数据脱敏、访问控制、安全审计
    """
    
    def __init__(self):
        self.security_rules: Dict[str, SecurityRule] = {}
        self.access_controls: Dict[str, AccessControl] = {}
        self.security_logs: List[Dict[str, Any]] = []
    
    def add_security_rule(self, rule_config: Dict[str, Any]) -> SecurityRule:
        """
        添加安全规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            安全规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = SecurityRule(
            rule_id=rule_id,
            field=rule_config['field'],
            security_level=SecurityLevel(rule_config.get('security_level', 'internal')),
            masking_type=MaskingType(rule_config.get('masking_type', 'partial')) if rule_config.get('masking_type') else None,
            masking_config=rule_config.get('masking_config', {})
        )
        
        self.security_rules[rule_id] = rule
        return rule
    
    def mask_data(self, data: Dict[str, Any], rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        脱敏数据
        
        Args:
            data: 数据字典
            rule_ids: 规则ID列表（可选）
            
        Returns:
            脱敏后的数据
        """
        masked_data = data.copy()
        
        rules_to_apply = rule_ids if rule_ids else list(self.security_rules.values())
        
        for rule in rules_to_apply:
            if isinstance(rule, str):
                rule = self.security_rules.get(rule)
                if not rule:
                    continue
            
            if rule.field in masked_data:
                masked_data[rule.field] = self._apply_masking(
                    masked_data[rule.field],
                    rule.masking_type or MaskingType.PARTIAL,
                    rule.masking_config or {}
                )
        
        return masked_data
    
    def _apply_masking(self, value: Any, masking_type: MaskingType,
                      config: Dict[str, Any]) -> Any:
        """应用脱敏"""
        if value is None:
            return None
        
        value_str = str(value)
        
        if masking_type == MaskingType.FULL:
            # 完全脱敏
            return '*' * len(value_str)
        
        elif masking_type == MaskingType.PARTIAL:
            # 部分脱敏
            if len(value_str) <= 2:
                return '*' * len(value_str)
            elif len(value_str) <= 4:
                return value_str[0] + '*' * (len(value_str) - 1)
            else:
                visible_start = config.get('visible_start', 1)
                visible_end = config.get('visible_end', 1)
                return (
                    value_str[:visible_start] +
                    '*' * (len(value_str) - visible_start - visible_end) +
                    value_str[-visible_end:]
                )
        
        elif masking_type == MaskingType.HASH:
            # 哈希脱敏
            return hashlib.md5(value_str.encode()).hexdigest()[:8]
        
        elif masking_type == MaskingType.REPLACE:
            # 替换脱敏
            replacement = config.get('replacement', '***')
            return replacement
        
        return value
    
    def check_access(self, user_id: str, resource: str, permission: str) -> bool:
        """
        检查访问权限
        
        Args:
            user_id: 用户ID
            resource: 资源
            permission: 权限
            
        Returns:
            是否有权限
        """
        access_key = f"{user_id}:{resource}"
        
        if access_key not in self.access_controls:
            return False
        
        access_control = self.access_controls[access_key]
        
        # 检查过期时间
        if access_control.expires_at and access_control.expires_at < datetime.utcnow():
            return False
        
        # 检查权限
        return permission in access_control.permissions or 'all' in access_control.permissions
    
    def grant_access(self, user_id: str, resource: str, permissions: List[str],
                    expires_at: Optional[datetime] = None) -> AccessControl:
        """
        授予访问权限
        
        Args:
            user_id: 用户ID
            resource: 资源
            permissions: 权限列表
            expires_at: 过期时间
            
        Returns:
            访问控制对象
        """
        access_key = f"{user_id}:{resource}"
        
        access_control = AccessControl(
            user_id=user_id,
            resource=resource,
            permissions=permissions,
            expires_at=expires_at
        )
        
        self.access_controls[access_key] = access_control
        
        # 记录日志
        self._log_security_event('grant_access', {
            'user_id': user_id,
            'resource': resource,
            'permissions': permissions
        })
        
        return access_control
    
    def revoke_access(self, user_id: str, resource: str) -> bool:
        """
        撤销访问权限
        
        Args:
            user_id: 用户ID
            resource: 资源
            
        Returns:
            是否成功
        """
        access_key = f"{user_id}:{resource}"
        
        if access_key in self.access_controls:
            del self.access_controls[access_key]
            
            # 记录日志
            self._log_security_event('revoke_access', {
                'user_id': user_id,
                'resource': resource
            })
            
            return True
        
        return False
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """记录安全事件"""
        log_entry = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        self.security_logs.append(log_entry)
    
    def get_security_summary(self) -> Dict[str, Any]:
        """
        获取安全摘要
        
        Returns:
            安全摘要
        """
        return {
            'total_rules': len(self.security_rules),
            'total_access_controls': len(self.access_controls),
            'total_security_events': len(self.security_logs),
            'recent_events': self.security_logs[-10:] if self.security_logs else []
        }


def main():
    """主函数 - 示例用法"""
    security = DataSecurity()
    
    # 添加安全规则
    rule = security.add_security_rule({
        'field': 'phone',
        'security_level': 'confidential',
        'masking_type': 'partial',
        'masking_config': {'visible_start': 3, 'visible_end': 4}
    })
    
    # 脱敏数据
    data = {'name': 'Alice', 'phone': '13812345678'}
    masked = security.mask_data(data, [rule.rule_id])
    print(f"脱敏结果: {masked}")


if __name__ == '__main__':
    main()
