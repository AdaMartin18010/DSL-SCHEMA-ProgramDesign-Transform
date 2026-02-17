#!/usr/bin/env python3
"""
Collaborative Schema Editor
===========================

实时协作Schema编辑器，支持：
- 多人实时编辑
- 变更冲突解决
- 版本合并
- 操作历史
- 实时同步

Version: 2.3.0
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict


class OperationType(Enum):
    """操作类型"""
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    MOVE = "move"


class ConflictResolutionStrategy(Enum):
    """冲突解决策略"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    MANUAL = "manual"


@dataclass
class Operation:
    """操作记录"""
    id: str
    type: OperationType
    path: str
    value: Any
    old_value: Any = None
    user_id: str = ""
    timestamp: float = field(default_factory=time.time)
    version: int = 0


@dataclass
class ChangeEvent:
    """变更事件"""
    operation: Operation
    acknowledged: bool = False
    applied: bool = False


@dataclass
class UserCursor:
    """用户光标位置"""
    user_id: str
    user_name: str
    path: str
    color: str = "#000000"
    last_activity: float = field(default_factory=time.time)


class CollaborativeDocument:
    """协作文档"""
    
    def __init__(self, doc_id: str, initial_content: Dict = None):
        self.doc_id = doc_id
        self.content = initial_content or {}
        self.version = 0
        self.operations: List[Operation] = []
        self.users: Dict[str, UserCursor] = {}
        self.conflict_resolution = ConflictResolutionStrategy.LAST_WRITE_WINS
        self.lock = False
    
    def apply_operation(self, operation: Operation) -> Tuple[bool, Optional[str]]:
        """
        应用操作
        
        Returns:
            (成功, 错误信息)
        """
        if self.lock:
            return False, "Document is locked"
        
        try:
            # 检查冲突
            conflicts = self._detect_conflicts(operation)
            if conflicts:
                resolved = self._resolve_conflicts(operation, conflicts)
                if not resolved:
                    return False, "Conflict detected and could not be resolved"
            
            # 应用操作
            self._execute_operation(operation)
            
            # 记录操作
            self.operations.append(operation)
            self.version += 1
            operation.version = self.version
            
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    def _detect_conflicts(self, new_op: Operation) -> List[Operation]:
        """检测冲突的操作"""
        conflicts = []
        
        for op in self.operations:
            # 检查是否同一路径的并发修改
            if op.path == new_op.path and op.user_id != new_op.user_id:
                # 检查时间是否接近 (5秒内)
                if abs(op.timestamp - new_op.timestamp) < 5:
                    conflicts.append(op)
        
        return conflicts
    
    def _resolve_conflicts(self, new_op: Operation, 
                          conflicts: List[Operation]) -> bool:
        """解决冲突"""
        if not conflicts:
            return True
        
        if self.conflict_resolution == ConflictResolutionStrategy.LAST_WRITE_WINS:
            # 保留最新的操作
            return True
        
        elif self.conflict_resolution == ConflictResolutionStrategy.FIRST_WRITE_WINS:
            # 保留最早的操作
            return False
        
        elif self.conflict_resolution == ConflictResolutionStrategy.MERGE:
            # 尝试合并
            if len(conflicts) == 1:
                return self._merge_operations(new_op, conflicts[0])
            return False
        
        else:  # MANUAL
            # 标记冲突，等待人工解决
            return False
    
    def _merge_operations(self, op1: Operation, op2: Operation) -> bool:
        """合并两个操作"""
        # 简化实现：只有更新不同类型字段时才合并
        if op1.type == OperationType.UPDATE and op2.type == OperationType.UPDATE:
            if isinstance(op1.value, dict) and isinstance(op2.value, dict):
                # 合并字典
                merged = {**op2.value, **op1.value}
                op1.value = merged
                return True
        return False
    
    def _execute_operation(self, operation: Operation):
        """执行操作"""
        path_parts = operation.path.split(".")
        current = self.content
        
        # 导航到父节点
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        key = path_parts[-1]
        
        if operation.type == OperationType.INSERT:
            current[key] = operation.value
        
        elif operation.type == OperationType.UPDATE:
            if key in current:
                operation.old_value = current[key]
            current[key] = operation.value
        
        elif operation.type == OperationType.DELETE:
            if key in current:
                operation.old_value = current[key]
                del current[key]
    
    def get_diff_since(self, version: int) -> List[Operation]:
        """获取指定版本之后的变更"""
        return [op for op in self.operations if op.version > version]
    
    def undo(self, user_id: str) -> Optional[Operation]:
        """撤销用户的最后一个操作"""
        user_ops = [op for op in reversed(self.operations) if op.user_id == user_id]
        
        if not user_ops:
            return None
        
        last_op = user_ops[0]
        
        # 创建反向操作
        if last_op.type == OperationType.INSERT:
            reverse_op = Operation(
                id=str(uuid.uuid4()),
                type=OperationType.DELETE,
                path=last_op.path,
                value=None,
                user_id=user_id
            )
        elif last_op.type == OperationType.DELETE:
            reverse_op = Operation(
                id=str(uuid.uuid4()),
                type=OperationType.INSERT,
                path=last_op.path,
                value=last_op.old_value,
                user_id=user_id
            )
        else:  # UPDATE
            reverse_op = Operation(
                id=str(uuid.uuid4()),
                type=OperationType.UPDATE,
                path=last_op.path,
                value=last_op.old_value,
                user_id=user_id
            )
        
        self.apply_operation(reverse_op)
        return reverse_op


class CollaborationManager:
    """协作管理器"""
    
    def __init__(self):
        self.documents: Dict[str, CollaborativeDocument] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> doc_id
    
    def create_document(self, doc_id: str, initial_content: Dict = None) -> CollaborativeDocument:
        """创建协作文档"""
        doc = CollaborativeDocument(doc_id, initial_content)
        self.documents[doc_id] = doc
        return doc
    
    def join_document(self, doc_id: str, user_id: str, user_name: str) -> Optional[CollaborativeDocument]:
        """用户加入文档"""
        if doc_id not in self.documents:
            return None
        
        doc = self.documents[doc_id]
        self.user_sessions[user_id] = doc_id
        
        # 添加用户光标
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
        color = colors[len(doc.users) % len(colors)]
        
        doc.users[user_id] = UserCursor(
            user_id=user_id,
            user_name=user_name,
            path="$",
            color=color
        )
        
        return doc
    
    def leave_document(self, user_id: str):
        """用户离开文档"""
        if user_id not in self.user_sessions:
            return
        
        doc_id = self.user_sessions[user_id]
        if doc_id in self.documents:
            doc = self.documents[doc_id]
            if user_id in doc.users:
                del doc.users[user_id]
        
        del self.user_sessions[user_id]
    
    def update_cursor(self, user_id: str, path: str):
        """更新用户光标位置"""
        if user_id not in self.user_sessions:
            return
        
        doc_id = self.user_sessions[user_id]
        doc = self.documents.get(doc_id)
        
        if doc and user_id in doc.users:
            doc.users[user_id].path = path
            doc.users[user_id].last_activity = time.time()
    
    def broadcast_operation(self, doc_id: str, operation: Operation) -> List[str]:
        """广播操作给其他用户"""
        if doc_id not in self.documents:
            return []
        
        doc = self.documents[doc_id]
        
        # 应用操作
        success, error = doc.apply_operation(operation)
        
        if not success:
            return []
        
        # 返回需要接收此操作的其他用户
        other_users = [uid for uid in doc.users.keys() if uid != operation.user_id]
        return other_users
    
    def get_active_users(self, doc_id: str) -> List[UserCursor]:
        """获取文档的活跃用户"""
        if doc_id not in self.documents:
            return []
        
        doc = self.documents[doc_id]
        current_time = time.time()
        
        # 过滤掉不活跃的用户（5分钟无活动）
        active_users = [
            user for user in doc.users.values()
            if current_time - user.last_activity < 300
        ]
        
        return active_users
    
    def merge_documents(self, doc_id1: str, doc_id2: str, 
                       strategy: ConflictResolutionStrategy = None) -> Optional[CollaborativeDocument]:
        """合并两个文档"""
        if doc_id1 not in self.documents or doc_id2 not in self.documents:
            return None
        
        doc1 = self.documents[doc_id1]
        doc2 = self.documents[doc_id2]
        
        # 创建新文档
        merged_id = f"merged_{doc_id1}_{doc_id2}"
        merged_doc = CollaborativeDocument(merged_id, doc1.content.copy())
        
        if strategy:
            merged_doc.conflict_resolution = strategy
        
        # 应用doc2的操作
        for op in doc2.operations:
            new_op = Operation(
                id=str(uuid.uuid4()),
                type=op.type,
                path=op.path,
                value=op.value,
                old_value=op.old_value,
                user_id=op.user_id
            )
            merged_doc.apply_operation(new_op)
        
        self.documents[merged_id] = merged_doc
        return merged_doc


def main():
    """示例用法"""
    manager = CollaborationManager()
    
    # 创建文档
    print("=" * 60)
    print("创建协作文档")
    print("=" * 60)
    
    initial_schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    
    doc = manager.create_document("doc-001", initial_schema)
    print(f"文档创建: {doc.doc_id}")
    print(f"初始内容: {json.dumps(doc.content, indent=2)}")
    
    # 用户加入
    print("\n" + "=" * 60)
    print("用户加入协作")
    print("=" * 60)
    
    doc = manager.join_document("doc-001", "user-001", "Alice")
    doc = manager.join_document("doc-001", "user-002", "Bob")
    
    print(f"活跃用户: {len(doc.users)}")
    for user in doc.users.values():
        print(f"  - {user.user_name} (颜色: {user.color})")
    
    # 用户1执行操作
    print("\n" + "=" * 60)
    print("Alice 添加字段")
    print("=" * 60)
    
    op1 = Operation(
        id=str(uuid.uuid4()),
        type=OperationType.INSERT,
        path="properties.email",
        value={"type": "string", "format": "email"},
        user_id="user-001"
    )
    
    manager.broadcast_operation("doc-001", op1)
    print(f"操作应用成功，当前版本: {doc.version}")
    print(f"内容: {json.dumps(doc.content, indent=2)}")
    
    # 用户2执行操作
    print("\n" + "=" * 60)
    print("Bob 添加字段")
    print("=" * 60)
    
    op2 = Operation(
        id=str(uuid.uuid4()),
        type=OperationType.INSERT,
        path="properties.age",
        value={"type": "integer", "minimum": 0},
        user_id="user-002"
    )
    
    manager.broadcast_operation("doc-001", op2)
    print(f"操作应用成功，当前版本: {doc.version}")
    print(f"内容: {json.dumps(doc.content, indent=2)}")
    
    # 查看操作历史
    print("\n" + "=" * 60)
    print("操作历史")
    print("=" * 60)
    
    for op in doc.operations:
        print(f"v{op.version}: {op.user_id} {op.type.value} {op.path}")
    
    # 撤销操作
    print("\n" + "=" * 60)
    print("Alice 撤销最后一个操作")
    print("=" * 60)
    
    undo_op = doc.undo("user-001")
    if undo_op:
        print(f"撤销操作: {undo_op.type.value} {undo_op.path}")
        print(f"当前版本: {doc.version}")
        print(f"内容: {json.dumps(doc.content, indent=2)}")


if __name__ == "__main__":
    main()
