"""
数据转换权限管理模块

专注于数据转换权限管理、访问控制、角色管理
"""

from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class PermissionType(Enum):
    """权限类型"""
    READ = "read"  # 读取
    WRITE = "write"  # 写入
    DELETE = "delete"  # 删除
    EXECUTE = "execute"  # 执行
    ADMIN = "admin"  # 管理
    APPROVE = "approve"  # 审批
    AUDIT = "audit"  # 审计


class ResourceType(Enum):
    """资源类型"""
    TRANSFORMATION = "transformation"  # 转换
    DATA = "data"  # 数据
    SCHEMA = "schema"  # Schema
    CONFIG = "config"  # 配置
    WORKFLOW = "workflow"  # 工作流
    TEMPLATE = "template"  # 模板
    REPORT = "report"  # 报告


class AccessLevel(Enum):
    """访问级别"""
    NONE = "none"  # 无访问权限
    READ_ONLY = "read_only"  # 只读
    READ_WRITE = "read_write"  # 读写
    FULL_ACCESS = "full_access"  # 完全访问


class RoleType(Enum):
    """角色类型"""
    ADMIN = "admin"  # 管理员
    OPERATOR = "operator"  # 操作员
    VIEWER = "viewer"  # 查看者
    AUDITOR = "auditor"  # 审计员
    CUSTOM = "custom"  # 自定义


@dataclass
class Permission:
    """权限"""
    permission_id: str
    permission_name: str
    permission_type: PermissionType
    resource_type: ResourceType
    resource_id: Optional[str] = None
    conditions: Dict[str, Any] = None


@dataclass
class Role:
    """角色"""
    role_id: str
    role_name: str
    role_type: RoleType
    permissions: List[str]  # Permission IDs
    description: str = ""
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class User:
    """用户"""
    user_id: str
    username: str
    email: str
    roles: List[str]  # Role IDs
    permissions: List[str] = None  # Direct Permission IDs
    active: bool = True
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class AccessRequest:
    """访问请求"""
    request_id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission_type: PermissionType
    timestamp: datetime
    status: str = "pending"  # pending, approved, denied
    approver_id: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class AccessLog:
    """访问日志"""
    log_id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission_type: PermissionType
    action: str
    timestamp: datetime
    result: str  # allowed, denied
    details: Dict[str, Any] = None


class DataTransformationAuthorization:
    """数据转换权限管理器"""
    
    def __init__(self):
        """初始化权限管理器"""
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.access_requests: List[AccessRequest] = []
        self.access_logs: List[AccessLog] = []
        self.authorization_config: Dict[str, Any] = {}
    
    def create_permission(
        self,
        permission_name: str,
        permission_type: PermissionType,
        resource_type: ResourceType,
        resource_id: Optional[str] = None,
        conditions: Dict[str, Any] = None
    ) -> Permission:
        """创建权限"""
        permission_id = f"perm_{hashlib.md5(f'{permission_name}_{permission_type.value}_{resource_type.value}'.encode()).hexdigest()[:8]}"
        
        permission = Permission(
            permission_id=permission_id,
            permission_name=permission_name,
            permission_type=permission_type,
            resource_type=resource_type,
            resource_id=resource_id,
            conditions=conditions or {}
        )
        
        self.permissions[permission_id] = permission
        logger.info(f"创建权限: {permission_name} ({permission_id})")
        
        return permission
    
    def create_role(
        self,
        role_name: str,
        role_type: RoleType,
        permissions: List[str],
        description: str = ""
    ) -> Role:
        """创建角色"""
        role_id = f"role_{hashlib.md5(f'{role_name}_{role_type.value}'.encode()).hexdigest()[:8]}"
        
        # 验证权限是否存在
        for perm_id in permissions:
            if perm_id not in self.permissions:
                raise ValueError(f"权限不存在: {perm_id}")
        
        role = Role(
            role_id=role_id,
            role_name=role_name,
            role_type=role_type,
            permissions=permissions,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.roles[role_id] = role
        logger.info(f"创建角色: {role_name} ({role_id})")
        
        return role
    
    def create_user(
        self,
        username: str,
        email: str,
        roles: List[str],
        permissions: List[str] = None
    ) -> User:
        """创建用户"""
        user_id = f"user_{hashlib.md5(username.encode()).hexdigest()[:8]}"
        
        # 验证角色是否存在
        for role_id in roles:
            if role_id not in self.roles:
                raise ValueError(f"角色不存在: {role_id}")
        
        # 验证直接权限是否存在
        if permissions:
            for perm_id in permissions:
                if perm_id not in self.permissions:
                    raise ValueError(f"权限不存在: {perm_id}")
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=permissions or [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.users[user_id] = user
        logger.info(f"创建用户: {username} ({user_id})")
        
        return user
    
    def check_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        permission_type: PermissionType,
        context: Dict[str, Any] = None
    ) -> bool:
        """检查权限"""
        if user_id not in self.users:
            logger.warning(f"用户不存在: {user_id}")
            self._log_access(user_id, resource_type, resource_id, permission_type, "check", "denied", {"reason": "user_not_found"})
            return False
        
        user = self.users[user_id]
        
        if not user.active:
            logger.warning(f"用户未激活: {user_id}")
            self._log_access(user_id, resource_type, resource_id, permission_type, "check", "denied", {"reason": "user_inactive"})
            return False
        
        # 获取用户的所有权限
        user_permissions = self._get_user_permissions(user_id)
        
        # 检查是否有匹配的权限
        for perm_id in user_permissions:
            permission = self.permissions[perm_id]
            
            if (permission.permission_type == permission_type and
                permission.resource_type == resource_type and
                (permission.resource_id is None or permission.resource_id == resource_id)):
                
                # 检查条件
                if self._check_conditions(permission.conditions, context):
                    self._log_access(user_id, resource_type, resource_id, permission_type, "check", "allowed", context)
                    return True
        
        logger.warning(f"权限检查失败: {user_id} - {permission_type.value} - {resource_type.value}")
        self._log_access(user_id, resource_type, resource_id, permission_type, "check", "denied", context)
        return False
    
    def _get_user_permissions(self, user_id: str) -> Set[str]:
        """获取用户的所有权限"""
        user = self.users[user_id]
        permissions = set(user.permissions or [])
        
        # 从角色获取权限
        for role_id in user.roles:
            if role_id in self.roles:
                role = self.roles[role_id]
                permissions.update(role.permissions)
        
        return permissions
    
    def _check_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> bool:
        """检查条件"""
        if not conditions:
            return True
        
        if not context:
            return False
        
        # 这里应该实现实际的条件检查逻辑
        # 例如：时间限制、IP限制、数据范围限制等
        return True
    
    def _log_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        permission_type: PermissionType,
        action: str,
        result: str,
        details: Dict[str, Any] = None
    ):
        """记录访问日志"""
        log_id = f"log_{hashlib.md5(f'{user_id}_{resource_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        log = AccessLog(
            log_id=log_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_type=permission_type,
            action=action,
            timestamp=datetime.now(),
            result=result,
            details=details or {}
        )
        
        self.access_logs.append(log)
    
    def request_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        permission_type: PermissionType,
        reason: Optional[str] = None
    ) -> AccessRequest:
        """请求访问权限"""
        request_id = f"req_{hashlib.md5(f'{user_id}_{resource_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        request = AccessRequest(
            request_id=request_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_type=permission_type,
            timestamp=datetime.now(),
            status="pending",
            reason=reason
        )
        
        self.access_requests.append(request)
        logger.info(f"创建访问请求: {request_id}")
        
        return request
    
    def approve_access_request(
        self,
        request_id: str,
        approver_id: str,
        grant_permission: bool = True
    ) -> AccessRequest:
        """审批访问请求"""
        request = next(
            (r for r in self.access_requests if r.request_id == request_id),
            None
        )
        
        if not request:
            raise ValueError(f"访问请求不存在: {request_id}")
        
        if request.status != "pending":
            raise ValueError(f"访问请求状态不正确: {request.status}")
        
        if grant_permission:
            # 授予临时权限
            self._grant_temporary_permission(
                request.user_id,
                request.resource_type,
                request.resource_id,
                request.permission_type
            )
            request.status = "approved"
        else:
            request.status = "denied"
        
        request.approver_id = approver_id
        logger.info(f"审批访问请求: {request_id} - {request.status}")
        
        return request
    
    def _grant_temporary_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        permission_type: PermissionType
    ):
        """授予临时权限"""
        # 创建临时权限
        temp_permission = self.create_permission(
            permission_name=f"临时权限-{user_id}-{resource_id}",
            permission_type=permission_type,
            resource_type=resource_type,
            resource_id=resource_id,
            conditions={"temporary": True, "expires_at": (datetime.now() + timedelta(days=1)).isoformat()}
        )
        
        # 将权限添加到用户
        if user_id in self.users:
            user = self.users[user_id]
            if user.permissions is None:
                user.permissions = []
            user.permissions.append(temp_permission.permission_id)
            logger.info(f"授予临时权限: {user_id} - {temp_permission.permission_id}")
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """获取用户的权限列表"""
        if user_id not in self.users:
            return []
        
        permission_ids = self._get_user_permissions(user_id)
        return [
            self.permissions[perm_id]
            for perm_id in permission_ids
            if perm_id in self.permissions
        ]
    
    def get_access_logs(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AccessLog]:
        """获取访问日志"""
        logs = self.access_logs
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if resource_type:
            logs = [l for l in logs if l.resource_type == resource_type]
        
        if start_time:
            logs = [l for l in logs if l.timestamp >= start_time]
        
        if end_time:
            logs = [l for l in logs if l.timestamp <= end_time]
        
        return logs
    
    def get_authorization_summary(self) -> Dict[str, Any]:
        """获取权限管理摘要"""
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.active])
        
        total_permissions = len(self.permissions)
        total_roles = len(self.roles)
        
        allowed_access = len([l for l in self.access_logs if l.result == "allowed"])
        denied_access = len([l for l in self.access_logs if l.result == "denied"])
        
        pending_requests = len([r for r in self.access_requests if r.status == "pending"])
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_permissions": total_permissions,
            "total_roles": total_roles,
            "allowed_access": allowed_access,
            "denied_access": denied_access,
            "access_success_rate": allowed_access / (allowed_access + denied_access) if (allowed_access + denied_access) > 0 else 0,
            "pending_requests": pending_requests
        }
    
    def update_user_roles(
        self,
        user_id: str,
        roles: List[str]
    ) -> User:
        """更新用户角色"""
        if user_id not in self.users:
            raise ValueError(f"用户不存在: {user_id}")
        
        # 验证角色是否存在
        for role_id in roles:
            if role_id not in self.roles:
                raise ValueError(f"角色不存在: {role_id}")
        
        user = self.users[user_id]
        user.roles = roles
        user.updated_at = datetime.now()
        
        logger.info(f"更新用户角色: {user_id}")
        
        return user
    
    def update_role_permissions(
        self,
        role_id: str,
        permissions: List[str]
    ) -> Role:
        """更新角色权限"""
        if role_id not in self.roles:
            raise ValueError(f"角色不存在: {role_id}")
        
        # 验证权限是否存在
        for perm_id in permissions:
            if perm_id not in self.permissions:
                raise ValueError(f"权限不存在: {perm_id}")
        
        role = self.roles[role_id]
        role.permissions = permissions
        role.updated_at = datetime.now()
        
        logger.info(f"更新角色权限: {role_id}")
        
        return role
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if user_id not in self.users:
            return False
        
        del self.users[user_id]
        logger.info(f"删除用户: {user_id}")
        
        return True
    
    def delete_role(self, role_id: str) -> bool:
        """删除角色"""
        if role_id not in self.roles:
            return False
        
        # 检查是否有用户使用此角色
        users_with_role = [
            u for u in self.users.values()
            if role_id in u.roles
        ]
        
        if users_with_role:
            raise ValueError(f"无法删除角色，仍有用户使用: {role_id}")
        
        del self.roles[role_id]
        logger.info(f"删除角色: {role_id}")
        
        return True


class AuthorizationAuditor:
    """权限审计器"""
    
    def __init__(self, authorization_manager: DataTransformationAuthorization):
        """初始化权限审计器"""
        self.authorization_manager = authorization_manager
    
    def audit_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """审计用户权限"""
        if user_id not in self.authorization_manager.users:
            raise ValueError(f"用户不存在: {user_id}")
        
        user = self.authorization_manager.users[user_id]
        permissions = self.authorization_manager.get_user_permissions(user_id)
        
        # 分析权限
        permissions_by_type = {}
        permissions_by_resource = {}
        
        for perm in permissions:
            perm_type = perm.permission_type.value
            resource_type = perm.resource_type.value
            
            permissions_by_type[perm_type] = permissions_by_type.get(perm_type, 0) + 1
            permissions_by_resource[resource_type] = permissions_by_resource.get(resource_type, 0) + 1
        
        return {
            "user_id": user_id,
            "username": user.username,
            "roles": user.roles,
            "total_permissions": len(permissions),
            "permissions_by_type": permissions_by_type,
            "permissions_by_resource": permissions_by_resource,
            "permissions": [
                {
                    "permission_id": p.permission_id,
                    "permission_name": p.permission_name,
                    "permission_type": p.permission_type.value,
                    "resource_type": p.resource_type.value,
                    "resource_id": p.resource_id
                }
                for p in permissions
            ]
        }
    
    def audit_access_patterns(self) -> Dict[str, Any]:
        """审计访问模式"""
        logs = self.authorization_manager.access_logs
        
        # 统计访问模式
        access_by_user = {}
        access_by_resource = {}
        access_by_permission = {}
        
        for log in logs:
            access_by_user[log.user_id] = access_by_user.get(log.user_id, 0) + 1
            resource_key = f"{log.resource_type.value}:{log.resource_id}"
            access_by_resource[resource_key] = access_by_resource.get(resource_key, 0) + 1
            access_by_permission[log.permission_type.value] = access_by_permission.get(log.permission_type.value, 0) + 1
        
        return {
            "audit_time": datetime.now(),
            "total_access_logs": len(logs),
            "access_by_user": access_by_user,
            "access_by_resource": access_by_resource,
            "access_by_permission": access_by_permission,
            "top_users": sorted(
                access_by_user.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "top_resources": sorted(
                access_by_resource.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def audit_security_issues(self) -> Dict[str, Any]:
        """审计安全问题"""
        issues = []
        
        # 检查未激活用户
        inactive_users = [
            u for u in self.authorization_manager.users.values()
            if not u.active
        ]
        
        if inactive_users:
            issues.append({
                "type": "inactive_users",
                "count": len(inactive_users),
                "users": [u.user_id for u in inactive_users]
            })
        
        # 检查无权限用户
        users_without_permissions = [
            u for u in self.authorization_manager.users.values()
            if not u.roles and not u.permissions
        ]
        
        if users_without_permissions:
            issues.append({
                "type": "users_without_permissions",
                "count": len(users_without_permissions),
                "users": [u.user_id for u in users_without_permissions]
            })
        
        # 检查被拒绝的访问
        denied_access = [
            l for l in self.authorization_manager.access_logs
            if l.result == "denied"
        ]
        
        if denied_access:
            issues.append({
                "type": "denied_access",
                "count": len(denied_access),
                "recent_denials": [
                    {
                        "user_id": l.user_id,
                        "resource": f"{l.resource_type.value}:{l.resource_id}",
                        "timestamp": l.timestamp.isoformat()
                    }
                    for l in denied_access[-10:]
                ]
            })
        
        return {
            "audit_time": datetime.now(),
            "issues": issues,
            "issue_count": len(issues)
        }
