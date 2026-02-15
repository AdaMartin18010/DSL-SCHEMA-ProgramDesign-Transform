# 办公自动化Schema实践案例

## 📑 目录

- [办公自动化Schema实践案例](#办公自动化schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：TechCorp集团智能OA系统](#2-案例1techcorp集团智能oa系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估与ROI](#27-效果评估与roi)
  - [3. 案例2：智能文档管理系统](#3-案例2智能文档管理系统)
    - [3.1 企业背景](#31-企业背景)
    - [3.2 业务痛点](#32-业务痛点)
    - [3.3 业务目标](#33-业务目标)
    - [3.4 技术挑战](#34-技术挑战)
    - [3.5 完整实现代码](#35-完整实现代码)
    - [3.6 效果评估与ROI](#36-效果评估与roi)
  - [4. 案例3：流程自动化引擎](#4-案例3流程自动化引擎)
    - [4.1 企业背景](#41-企业背景)
    - [4.2 业务痛点](#42-业务痛点)
    - [4.3 业务目标](#43-业务目标)
    - [4.4 技术挑战](#44-技术挑战)
    - [4.5 完整实现代码](#45-完整实现代码)
    - [4.6 效果评估与ROI](#46-效果评估与roi)

---

## 1. 案例概述

本文档提供办公自动化Schema在实际企业应用中的实践案例，涵盖智能OA系统、文档管理、流程自动化等核心场景。

**案例类型**：

1. **智能OA系统**：集成多种办公功能的统一平台
2. **智能文档管理**：文档版本控制、权限管理、智能检索
3. **流程自动化引擎**：BPMN工作流、审批流程自动化

**参考标准**：

- **ODF标准**：OpenDocument Format
- **OOXML标准**：Office Open XML
- **BPMN 2.0**：业务流程模型和标记法

---

## 2. 案例1：TechCorp集团智能OA系统

### 2.1 企业背景

**TechCorp集团**是一家跨国科技企业，拥有员工15,000人，分布在全球20个国家的50个办公室。集团需要统一的OA系统来支撑日常办公、协同工作和业务审批。

- **成立时间**：2005年
- **员工规模**：15,000人
- **全球办公室**：50个
- **日处理流程**：5,000+个审批流程
- **文档存储量**：50TB+
- **原OA系统**：分散的多个系统，数据孤岛严重

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **系统分散** | 严重 | 使用8个不同系统，员工需要在多个系统间切换，效率低下 |
| 2 | **流程审批慢** | 严重 | 平均审批周期5天，紧急流程无法快速响应，影响业务进展 |
| 3 | **文档管理混乱** | 严重 | 文档版本混乱，年均发生30+次重要文档误用事件 |
| 4 | **移动办公支持差** | 高 | 移动端功能有限，远程办公员工体验差 |
| 5 | **数据孤岛** | 高 | HR、财务、项目系统数据不互通，需要重复录入 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 系统整合度 | 20% | 95% | 12个月 |
| 2 | 平均审批周期 | 5天 | <1天 | 9个月 |
| 3 | 文档版本准确率 | 70% | 99% | 6个月 |
| 4 | 移动办公覆盖率 | 30% | 90% | 9个月 |
| 5 | 员工满意度 | 55% | 85% | 12个月 |

### 2.4 技术挑战

1. **多租户架构**：需要支持全球50个办公室的独立配置，同时保持统一的数据标准和流程规范

2. **高并发处理**：工作日高峰时段同时在线用户超过8,000人，日活跃用户12,000人，要求系统具备高并发处理能力

3. **复杂审批路由**：需要支持条件分支、会签、转办、催办、超时处理等复杂审批逻辑

4. **文档格式兼容**：需要支持ODF、OOXML、PDF等格式的互转和在线预览，兼容多种办公软件

5. **全球数据合规**：需要满足GDPR、中国网络安全法等数据合规要求，支持数据本地化存储

### 2.5 解决方案

**智能OA系统架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                     应用服务层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
│  │ 审批中心 │ │ 文档中心 │ │ 日程中心 │ │ 会议管理      │ │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
│  │ 考勤管理 │ │ 任务协作 │ │ 知识库   │ │ 即时通讯      │ │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     核心服务层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
│  │ 流程引擎 │ │ 文档引擎 │ │ 消息引擎 │ │ 搜索服务      │ │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     数据存储层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
│  │ 关系数据库│ │ 文档存储 │ │ 缓存     │ │ 对象存储      │ │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.6 完整实现代码

```python
#!/usr/bin/env python3
"""
TechCorp集团智能OA系统 - 核心实现
集成审批、文档、日程、任务等功能
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """审批状态"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalAction(Enum):
    """审批动作"""
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    TRANSFER = "transfer"
    RETURN = "return"


class DocumentStatus(Enum):
    """文档状态"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class TaskStatus(Enum):
    """任务状态"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class User:
    """用户"""
    user_id: str
    username: str
    email: str
    department: str
    title: str
    manager_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "department": self.department,
            "title": self.title,
            "manager_id": self.manager_id,
            "roles": self.roles
        }


@dataclass
class ApprovalStep:
    """审批步骤"""
    step_id: str
    step_order: int
    approver_id: Optional[str]
    approver_role: Optional[str]
    status: ApprovalStatus
    action: Optional[ApprovalAction] = None
    comment: str = ""
    action_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_order": self.step_order,
            "approver_id": self.approver_id,
            "approver_role": self.approver_role,
            "status": self.status.value,
            "action": self.action.value if self.action else None,
            "comment": self.comment,
            "action_time": self.action_time.isoformat() if self.action_time else None
        }


@dataclass
class ApprovalProcess:
    """审批流程"""
    process_id: str
    process_type: str
    title: str
    submitter_id: str
    current_step: int = 0
    status: ApprovalStatus = ApprovalStatus.DRAFT
    steps: List[ApprovalStep] = field(default_factory=list)
    form_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_id": self.process_id,
            "process_type": self.process_type,
            "title": self.title,
            "submitter_id": self.submitter_id,
            "current_step": self.current_step,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "form_data": self.form_data,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class Document:
    """文档"""
    document_id: str
    title: str
    document_type: str
    owner_id: str
    content: str = ""
    version: int = 1
    status: DocumentStatus = DocumentStatus.ACTIVE
    parent_version_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    collaborators: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "document_type": self.document_type,
            "owner_id": self.owner_id,
            "version": self.version,
            "status": self.status.value,
            "parent_version_id": self.parent_version_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "collaborators": self.collaborators,
            "tags": self.tags
        }


@dataclass
class Task:
    """任务"""
    task_id: str
    title: str
    description: str
    creator_id: str
    assignee_id: str
    status: TaskStatus = TaskStatus.TODO
    priority: int = 3  # 1-5, 5最高
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "creator_id": self.creator_id,
            "assignee_id": self.assignee_id,
            "status": self.status.value,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }


class OASystem:
    """OA系统核心"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.approval_processes: Dict[str, ApprovalProcess] = {}
        self.documents: Dict[str, Document] = {}
        self.tasks: Dict[str, Task] = {}
        
        # 文档版本历史
        self.document_versions: Dict[str, List[str]] = defaultdict(list)
        
        # 统计
        self.stats = {
            "total_approvals": 0,
            "avg_approval_hours": 0,
            "total_documents": 0,
            "total_tasks": 0
        }
        
        logger.info("OA System initialized")
    
    def register_user(self, user: User):
        """注册用户"""
        self.users[user.user_id] = user
    
    def create_approval_process(self, process_type: str, title: str,
                               submitter_id: str, form_data: Dict[str, Any],
                               workflow_definition: List[Dict]) -> str:
        """创建审批流程"""
        process_id = f"APR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # 创建审批步骤
        steps = []
        for i, step_def in enumerate(workflow_definition):
            step = ApprovalStep(
                step_id=f"{process_id}-STEP{i+1}",
                step_order=i + 1,
                approver_id=step_def.get("approver_id"),
                approver_role=step_def.get("approver_role"),
                status=ApprovalStatus.PENDING if i == 0 else ApprovalStatus.DRAFT
            )
            steps.append(step)
        
        process = ApprovalProcess(
            process_id=process_id,
            process_type=process_type,
            title=title,
            submitter_id=submitter_id,
            steps=steps,
            form_data=form_data,
            status=ApprovalStatus.PENDING
        )
        
        self.approval_processes[process_id] = process
        self.stats["total_approvals"] += 1
        
        logger.info(f"Created approval process: {process_id}")
        return process_id
    
    def process_approval(self, process_id: str, step_id: str,
                        approver_id: str, action: ApprovalAction,
                        comment: str = "") -> bool:
        """处理审批"""
        if process_id not in self.approval_processes:
            return False
        
        process = self.approval_processes[process_id]
        
        # 找到当前步骤
        current_step = None
        for step in process.steps:
            if step.step_id == step_id and step.status == ApprovalStatus.PENDING:
                current_step = step
                break
        
        if not current_step:
            return False
        
        # 更新步骤
        current_step.approver_id = approver_id
        current_step.action = action
        current_step.comment = comment
        current_step.action_time = datetime.now()
        
        if action == ApprovalAction.APPROVE:
            current_step.status = ApprovalStatus.APPROVED
            
            # 进入下一步
            if process.current_step < len(process.steps) - 1:
                process.current_step += 1
                next_step = process.steps[process.current_step]
                next_step.status = ApprovalStatus.PENDING
            else:
                # 流程完成
                process.status = ApprovalStatus.APPROVED
                process.completed_at = datetime.now()
                
                # 计算审批时间
                duration = (process.completed_at - process.created_at).total_seconds() / 3600
                n = self.stats["total_approvals"]
                self.stats["avg_approval_hours"] = (
                    self.stats["avg_approval_hours"] * (n-1) + duration
                ) / n
                
                logger.info(f"Approval process {process_id} completed in {duration:.2f} hours")
                
        elif action == ApprovalAction.REJECT:
            current_step.status = ApprovalStatus.REJECTED
            process.status = ApprovalStatus.REJECTED
            process.completed_at = datetime.now()
            
        elif action == ApprovalAction.RETURN:
            # 退回上一步或申请人
            current_step.status = ApprovalStatus.DRAFT
            if process.current_step > 0:
                process.current_step -= 1
                prev_step = process.steps[process.current_step]
                prev_step.status = ApprovalStatus.PENDING
                prev_step.action = None
                prev_step.comment = ""
                prev_step.action_time = None
        
        return True
    
    def create_document(self, title: str, document_type: str,
                       owner_id: str, content: str = "",
                       tags: List[str] = None) -> str:
        """创建文档"""
        document_id = f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        doc = Document(
            document_id=document_id,
            title=title,
            document_type=document_type,
            owner_id=owner_id,
            content=content,
            tags=tags or []
        )
        
        self.documents[document_id] = doc
        self.document_versions[document_id].append(document_id)
        self.stats["total_documents"] += 1
        
        logger.info(f"Created document: {document_id}")
        return document_id
    
    def create_document_version(self, document_id: str, new_content: str,
                               editor_id: str) -> Optional[str]:
        """创建文档新版本"""
        if document_id not in self.documents:
            return None
        
        original = self.documents[document_id]
        
        # 创建新版本
        new_doc_id = f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        new_doc = Document(
            document_id=new_doc_id,
            title=original.title,
            document_type=original.document_type,
            owner_id=original.owner_id,
            content=new_content,
            version=original.version + 1,
            parent_version_id=document_id,
            collaborators=original.collaborators,
            tags=original.tags
        )
        
        self.documents[new_doc_id] = new_doc
        
        # 更新版本链
        root_id = self._get_root_document_id(document_id)
        self.document_versions[root_id].append(new_doc_id)
        
        logger.info(f"Created document version: {new_doc_id} (from {document_id})")
        return new_doc_id
    
    def _get_root_document_id(self, document_id: str) -> str:
        """获取文档根版本ID"""
        doc = self.documents.get(document_id)
        if doc and doc.parent_version_id:
            return self._get_root_document_id(doc.parent_version_id)
        return document_id
    
    def get_document_history(self, document_id: str) -> List[Dict]:
        """获取文档版本历史"""
        root_id = self._get_root_document_id(document_id)
        version_ids = self.document_versions.get(root_id, [])
        
        return [self.documents[vid].to_dict() for vid in version_ids if vid in self.documents]
    
    def create_task(self, title: str, description: str, creator_id: str,
                   assignee_id: str, due_date: datetime = None,
                   priority: int = 3, tags: List[str] = None) -> str:
        """创建任务"""
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            creator_id=creator_id,
            assignee_id=assignee_id,
            due_date=due_date,
            priority=priority,
            tags=tags or []
        )
        
        self.tasks[task_id] = task
        self.stats["total_tasks"] += 1
        
        logger.info(f"Created task: {task_id}")
        return task_id
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """更新任务状态"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = status
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
        
        return True
    
    def get_user_tasks(self, user_id: str, status: TaskStatus = None) -> List[Dict]:
        """获取用户任务列表"""
        tasks = [
            task.to_dict() for task in self.tasks.values()
            if task.assignee_id == user_id
        ]
        
        if status:
            tasks = [t for t in tasks if t["status"] == status.value]
        
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)
    
    def get_user_approvals(self, user_id: str, pending_only: bool = True) -> List[Dict]:
        """获取用户待办审批"""
        approvals = []
        
        for process in self.approval_processes.values():
            if pending_only and process.status != ApprovalStatus.PENDING:
                continue
            
            # 检查是否是当前步骤的审批人
            if process.current_step < len(process.steps):
                current_step = process.steps[process.current_step]
                if (current_step.status == ApprovalStatus.PENDING and
                    (current_step.approver_id == user_id or
                     self._user_has_role(user_id, current_step.approver_role))):
                    approvals.append(process.to_dict())
        
        return approvals
    
    def _user_has_role(self, user_id: str, role: str) -> bool:
        """检查用户是否具有指定角色"""
        if not role or user_id not in self.users:
            return False
        return role in self.users[user_id].roles
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        # 计算各状态任务数量
        task_status_count = defaultdict(int)
        for task in self.tasks.values():
            task_status_count[task.status.value] += 1
        
        # 计算各状态审批数量
        approval_status_count = defaultdict(int)
        for proc in self.approval_processes.values():
            approval_status_count[proc.status.value] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "users": len(self.users),
            "documents": len(self.documents),
            "tasks": {
                "total": len(self.tasks),
                "by_status": dict(task_status_count)
            },
            "approvals": {
                "total": len(self.approval_processes),
                "by_status": dict(approval_status_count),
                "avg_processing_hours": self.stats["avg_approval_hours"]
            }
        }


def main():
    """演示OA系统"""
    oa = OASystem()
    
    # 注册用户
    users = [
        User("U001", "zhangsan", "zhangsan@techcorp.com", "研发部", "经理", roles=["manager"]),
        User("U002", "lisi", "lisi@techcorp.com", "研发部", "工程师", manager_id="U001"),
        User("U003", "wangwu", "wangwu@techcorp.com", "财务部", "总监", roles=["director", "finance_approver"]),
    ]
    for user in users:
        oa.register_user(user)
    
    # 创建审批流程（请假申请）
    workflow = [
        {"approver_role": "manager"},  # 部门经理审批
        {"approver_role": "hr_approver"}  # HR审批
    ]
    
    process_id = oa.create_approval_process(
        process_type="leave_request",
        title="张三请假申请",
        submitter_id="U002",
        form_data={
            "leave_type": "annual",
            "start_date": "2025-03-01",
            "end_date": "2025-03-05",
            "days": 5,
            "reason": "个人事务"
        },
        workflow_definition=workflow
    )
    
    # 经理审批
    oa.process_approval(
        process_id=process_id,
        step_id=oa.approval_processes[process_id].steps[0].step_id,
        approver_id="U001",
        action=ApprovalAction.APPROVE,
        comment="同意请假"
    )
    
    # 创建文档
    doc_id = oa.create_document(
        title="项目计划书",
        document_type="project_plan",
        owner_id="U002",
        content="项目背景...",
        tags=["project", "planning"]
    )
    
    # 创建文档版本
    oa.create_document_version(doc_id, "项目背景...\n\n项目目标...", "U002")
    
    # 创建任务
    task_id = oa.create_task(
        title="完成需求分析文档",
        description="根据客户反馈完善需求分析",
        creator_id="U001",
        assignee_id="U002",
        due_date=datetime.now() + timedelta(days=7),
        priority=4
    )
    
    # 系统统计
    stats = oa.get_system_stats()
    print("OA System Stats:")
    print(json.dumps(stats, indent=2))
    
    # 用户待办
    user_tasks = oa.get_user_tasks("U002")
    print(f"\nUser U002 tasks: {len(user_tasks)}")
    
    # 文档历史
    history = oa.get_document_history(doc_id)
    print(f"\nDocument {doc_id} history: {len(history)} versions")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估与ROI

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 系统整合度 | 20% | 94% | +74% |
| 平均审批周期 | 5天 | 0.8天 | -84% |
| 文档版本准确率 | 70% | 99.5% | +29% |
| 移动办公覆盖率 | 30% | 88% | +58% |
| 员工满意度 | 55% | 87% | +32% |

#### ROI计算

**投资成本**：
- 系统开发：1,500万元
- 实施部署：500万元
- **总投资**：2,000万元

**年度收益**：
- 效率提升：3,000万元
- 人力成本节省：1,500万元
- 错误减少：500万元
- **年度总收益**：5,000万元

**ROI分析**：
- 投资回收期：4.8个月
- 3年ROI：650%

---

## 3. 案例2：智能文档管理系统

### 3.1 企业背景

**某律师事务所**拥有300名律师，年均处理案件10,000件，产生文档超过100万份，对文档管理的专业性和安全性要求极高。

- **员工规模**：300人
- **年处理案件**：10,000件
- **文档数量**：100万+份
- **日新增文档**：500+份

### 3.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **文档检索困难** | 严重 | 查找历史案例平均需30分钟，严重影响工作效率 |
| 2 | **版本控制混乱** | 严重 | 合同多版本并行，年均发生15次版本误用 |
| 3 | **权限管理粗放** | 高 | 无法精确控制文档访问权限，存在泄密风险 |
| 4 | **协作效率低** | 高 | 多人协作编辑冲突频繁，需要频繁合并 |
| 5 | **合规审计困难** | 中 | 无法完整追踪文档访问和修改记录 |

### 3.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 文档检索时间 | 30分钟 | <30秒 | 6个月 |
| 2 | 版本控制准确率 | 60% | 99.9% | 6个月 |
| 3 | 权限控制粒度 | 文件级 | 段落级 | 12个月 |
| 4 | 协作冲突率 | 20% | <1% | 9个月 |
| 5 | 审计追踪完整率 | 40% | 100% | 6个月 |

### 3.4 技术挑战

1. **全文检索性能**：100万文档的全文索引，要求检索响应时间<1秒

2. **细粒度权限控制**：需要支持基于角色、部门、项目的多维权限，以及文档内段落级权限

3. **实时协作编辑**：需要支持多人实时协作，OT算法处理冲突，延迟<100ms

4. **版本分支管理**：法律文档需要支持分支版本（如合同的不同谈判版本），类似Git的版本管理

5. **审计日志完整性**：需要记录所有文档操作，支持不可篡改的审计追踪

### 3.5 完整实现代码

```python
#!/usr/bin/env python3
"""
智能文档管理系统 - 核心实现
支持版本控制、细粒度权限、全文检索
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Permission(Enum):
    """权限类型"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


class DocumentOperation(Enum):
    """文档操作"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SHARE = "share"
    VERSION = "version"


@dataclass
class PermissionRule:
    """权限规则"""
    user_id: Optional[str]
    role: Optional[str]
    department: Optional[str]
    permissions: Set[Permission] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role,
            "department": self.department,
            "permissions": [p.value for p in self.permissions]
        }


@dataclass
class DocumentVersion:
    """文档版本"""
    version_id: str
    document_id: str
    version_number: int
    content: str
    checksum: str
    created_by: str
    created_at: datetime
    comment: str = ""
    parent_versions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "document_id": self.document_id,
            "version_number": self.version_number,
            "checksum": self.checksum,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "comment": self.comment,
            "parent_versions": self.parent_versions
        }


@dataclass
class AuditLog:
    """审计日志"""
    log_id: str
    document_id: str
    user_id: str
    operation: DocumentOperation
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "operation": self.operation.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }


class DocumentManager:
    """文档管理器"""
    
    def __init__(self):
        # 文档存储
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.document_versions: Dict[str, List[DocumentVersion]] = defaultdict(list)
        
        # 权限管理
        self.permissions: Dict[str, List[PermissionRule]] = defaultdict(list)
        
        # 全文索引 (简化的倒排索引)
        self.index: Dict[str, Set[str]] = defaultdict(set)
        
        # 审计日志
        self.audit_logs: List[AuditLog] = []
        
        # 用户角色信息
        self.user_roles: Dict[str, Dict] = {}
        
        logger.info("Document Manager initialized")
    
    def register_user(self, user_id: str, roles: List[str], department: str):
        """注册用户"""
        self.user_roles[user_id] = {
            "roles": roles,
            "department": department
        }
    
    def create_document(self, document_id: str, title: str, content: str,
                       owner_id: str, metadata: Dict[str, Any] = None) -> bool:
        """创建文档"""
        # 检查权限
        if not self._check_permission(None, owner_id, Permission.WRITE):
            logger.warning(f"User {owner_id} does not have permission to create documents")
            return False
        
        # 创建文档
        self.documents[document_id] = {
            "document_id": document_id,
            "title": title,
            "current_version": 0,
            "owner_id": owner_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # 创建初始版本
        version = DocumentVersion(
            version_id=f"{document_id}-V1",
            document_id=document_id,
            version_number=1,
            content=content,
            checksum=hashlib.sha256(content.encode()).hexdigest(),
            created_by=owner_id,
            created_at=datetime.now(),
            comment="Initial version"
        )
        self.document_versions[document_id].append(version)
        self.documents[document_id]["current_version"] = 1
        
        # 建立索引
        self._index_document(document_id, content)
        
        # 审计日志
        self._log_operation(document_id, owner_id, DocumentOperation.CREATE,
                          {"title": title})
        
        logger.info(f"Created document: {document_id}")
        return True
    
    def update_document(self, document_id: str, new_content: str,
                       user_id: str, comment: str = "") -> bool:
        """更新文档"""
        if document_id not in self.documents:
            return False
        
        # 检查权限
        if not self._check_permission(document_id, user_id, Permission.WRITE):
            logger.warning(f"User {user_id} does not have write permission")
            return False
        
        # 创建新版本
        versions = self.document_versions[document_id]
        new_version_number = len(versions) + 1
        
        version = DocumentVersion(
            version_id=f"{document_id}-V{new_version_number}",
            document_id=document_id,
            version_number=new_version_number,
            content=new_content,
            checksum=hashlib.sha256(new_content.encode()).hexdigest(),
            created_by=user_id,
            created_at=datetime.now(),
            comment=comment,
            parent_versions=[versions[-1].version_id] if versions else []
        )
        
        versions.append(version)
        self.documents[document_id]["current_version"] = new_version_number
        
        # 更新索引
        self._index_document(document_id, new_content)
        
        # 审计日志
        self._log_operation(document_id, user_id, DocumentOperation.UPDATE,
                          {"version": new_version_number, "comment": comment})
        
        logger.info(f"Updated document: {document_id} to version {new_version_number}")
        return True
    
    def get_document(self, document_id: str, user_id: str,
                    version_number: int = None) -> Optional[Dict]:
        """获取文档"""
        if document_id not in self.documents:
            return None
        
        # 检查权限
        if not self._check_permission(document_id, user_id, Permission.READ):
            logger.warning(f"User {user_id} does not have read permission")
            return None
        
        # 审计日志
        self._log_operation(document_id, user_id, DocumentOperation.READ,
                          {"version": version_number})
        
        # 获取指定版本或最新版本
        versions = self.document_versions[document_id]
        if version_number:
            for v in versions:
                if v.version_number == version_number:
                    return {
                        **self.documents[document_id],
                        "content": v.content,
                        "version": v.to_dict()
                    }
            return None
        else:
            latest = versions[-1] if versions else None
            if latest:
                return {
                    **self.documents[document_id],
                    "content": latest.content,
                    "version": latest.to_dict()
                }
            return None
    
    def _check_permission(self, document_id: Optional[str], user_id: str,
                         permission: Permission) -> bool:
        """检查权限"""
        if document_id is None or document_id not in self.permissions:
            # 创建权限检查
            return True
        
        user_info = self.user_roles.get(user_id, {})
        user_roles = user_info.get("roles", [])
        user_dept = user_info.get("department", "")
        
        # 检查权限规则
        for rule in self.permissions[document_id]:
            # 用户匹配
            if rule.user_id and rule.user_id == user_id:
                return permission in rule.permissions
            
            # 角色匹配
            if rule.role and rule.role in user_roles:
                return permission in rule.permissions
            
            # 部门匹配
            if rule.department and rule.department == user_dept:
                return permission in rule.permissions
        
        return False
    
    def set_permission(self, document_id: str, rule: PermissionRule):
        """设置权限"""
        self.permissions[document_id].append(rule)
    
    def search_documents(self, query: str, user_id: str) -> List[Dict]:
        """搜索文档"""
        # 简单的分词搜索
        terms = query.lower().split()
        matching_docs = set()
        
        for term in terms:
            if term in self.index:
                if not matching_docs:
                    matching_docs = self.index[term].copy()
                else:
                    matching_docs &= self.index[term]
        
        results = []
        for doc_id in matching_docs:
            # 检查读取权限
            if self._check_permission(doc_id, user_id, Permission.READ):
                doc = self.documents[doc_id]
                results.append({
                    "document_id": doc_id,
                    "title": doc["title"],
                    "owner_id": doc["owner_id"],
                    "current_version": doc["current_version"]
                })
        
        return results
    
    def _index_document(self, document_id: str, content: str):
        """建立文档索引"""
        # 从旧索引中移除
        for term_docs in self.index.values():
            term_docs.discard(document_id)
        
        # 添加新索引
        terms = set(content.lower().split())
        for term in terms:
            self.index[term].add(document_id)
    
    def _log_operation(self, document_id: str, user_id: str,
                      operation: DocumentOperation, details: Dict):
        """记录操作日志"""
        log = AuditLog(
            log_id=f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            document_id=document_id,
            user_id=user_id,
            operation=operation,
            timestamp=datetime.now(),
            details=details
        )
        self.audit_logs.append(log)
    
    def get_version_history(self, document_id: str) -> List[Dict]:
        """获取版本历史"""
        versions = self.document_versions.get(document_id, [])
        return [v.to_dict() for v in versions]
    
    def compare_versions(self, document_id: str, version1: int,
                        version2: int) -> Dict[str, Any]:
        """比较两个版本"""
        versions = self.document_versions.get(document_id, [])
        
        v1_content = None
        v2_content = None
        
        for v in versions:
            if v.version_number == version1:
                v1_content = v.content
            if v.version_number == version2:
                v2_content = v.content
        
        if v1_content is None or v2_content is None:
            return {"error": "Version not found"}
        
        # 简单的行级比较
        v1_lines = v1_content.split('\n')
        v2_lines = v2_content.split('\n')
        
        diff = {
            "version1": version1,
            "version2": version2,
            "added_lines": [],
            "removed_lines": [],
            "modified_lines": []
        }
        
        max_lines = max(len(v1_lines), len(v2_lines))
        for i in range(max_lines):
            line1 = v1_lines[i] if i < len(v1_lines) else None
            line2 = v2_lines[i] if i < len(v2_lines) else None
            
            if line1 is None:
                diff["added_lines"].append({"line": i+1, "content": line2})
            elif line2 is None:
                diff["removed_lines"].append({"line": i+1, "content": line1})
            elif line1 != line2:
                diff["modified_lines"].append({
                    "line": i+1,
                    "old": line1,
                    "new": line2
                })
        
        return diff


def main():
    """演示文档管理"""
    dm = DocumentManager()
    
    # 注册用户
    dm.register_user("U001", ["admin"], "Legal")
    dm.register_user("U002", ["lawyer"], "Legal")
    dm.register_user("U003", ["paralegal"], "Legal")
    
    # 创建文档
    doc_id = "DOC-001"
    content = """
    CONTRACT AGREEMENT
    
    Party A: Company X
    Party B: Company Y
    
    Terms and Conditions:
    1. Payment terms: Net 30
    2. Delivery: FOB Shanghai
    3. Warranty: 12 months
    """
    
    dm.create_document(doc_id, "Service Contract Template", content, "U001")
    
    # 设置权限
    dm.set_permission(doc_id, PermissionRule(
        user_id=None,
        role="lawyer",
        department="Legal",
        permissions={Permission.READ, Permission.WRITE}
    ))
    
    # 更新文档
    new_content = content + "\n4. Confidentiality: Both parties agree..."
    dm.update_document(doc_id, new_content, "U002", "Added confidentiality clause")
    
    # 搜索
    results = dm.search_documents("contract agreement", "U002")
    print(f"Search results: {len(results)}")
    for r in results:
        print(f"  - {r['title']}")
    
    # 版本历史
    history = dm.get_version_history(doc_id)
    print(f"\nVersion history: {len(history)} versions")
    
    # 版本比较
    diff = dm.compare_versions(doc_id, 1, 2)
    print(f"\nVersion comparison:")
    print(json.dumps(diff, indent=2))


if __name__ == "__main__":
    main()
```

### 3.6 效果评估与ROI

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 文档检索时间 | 30分钟 | 5秒 | -99.7% |
| 版本控制准确率 | 60% | 99.9% | +40% |
| 协作冲突率 | 20% | 0.5% | -97.5% |
| 审计追踪完整率 | 40% | 100% | +60% |
| 文档安全事件 | 5次/年 | 0次 | -100% |

#### ROI计算

**投资成本**：
- 系统开发：300万元
- 数据迁移：50万元
- **总投资**：350万元

**年度收益**：
- 效率提升：800万元
- 风险减少：200万元
- **年度总收益**：1,000万元

**ROI分析**：
- 投资回收期：4.2个月
- 3年ROI：757%

---

## 4. 案例3：流程自动化引擎

### 4.1 企业背景

**某大型制造企业**拥有50个工厂，10,000名员工，年均处理审批流程20万个，涉及采购、生产、人事、财务等多个业务领域。

- **工厂数量**：50个
- **员工规模**：10,000人
- **年处理流程**：20万个
- **流程类型**：30+种

### 4.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **流程设计复杂** | 严重 | 新流程上线需2个月，无法快速响应业务变化 |
| 2 | **流程执行不透明** | 严重 | 流程卡在某个环节，无法及时发现和催办 |
| 3 | **跨系统集成难** | 高 | 流程与ERP、CRM系统脱节，需要重复录入 |
| 4 | **数据分析缺失** | 高 | 无法分析流程瓶颈，无法持续优化 |
| 5 | **移动审批体验差** | 中 | 移动端功能简陋，审批体验差 |

### 4.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 新流程上线时间 | 2个月 | <1周 | 9个月 |
| 2 | 流程可视化覆盖率 | 30% | 100% | 6个月 |
| 3 | 系统集成率 | 20% | 90% | 12个月 |
| 4 | 流程优化周期 | 6个月 | <1个月 | 9个月 |
| 5 | 移动端使用率 | 25% | 80% | 6个月 |

### 4.4 技术挑战

1. **可视化流程设计器**：需要支持拖拽式流程设计，支持BPMN 2.0标准

2. **动态流程执行**：需要支持会签、转办、跳转、回退等复杂流程模式

3. **高性能流程引擎**：需要支持日处理10万+流程实例，响应时间<100ms

4. **规则引擎集成**：需要支持复杂的业务规则判断，动态决定流程走向

5. **分布式事务**：需要保证跨系统集成的数据一致性

### 4.5 完整实现代码

```python
#!/usr/bin/env python3
"""
流程自动化引擎 - 核心实现
支持BPMN流程、规则引擎、跨系统集成
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeType(Enum):
    """节点类型"""
    START = "start"
    END = "end"
    TASK = "task"
    GATEWAY = "gateway"
    EVENT = "event"


class TaskType(Enum):
    """任务类型"""
    USER_TASK = "user_task"
    SERVICE_TASK = "service_task"
    SCRIPT_TASK = "script_task"


class GatewayType(Enum):
    """网关类型"""
    EXCLUSIVE = "exclusive"  # 排他网关
    PARALLEL = "parallel"    # 并行网关
    INCLUSIVE = "inclusive"  # 包容网关


class ProcessStatus(Enum):
    """流程状态"""
    RUNNING = "running"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"


@dataclass
class FlowNode:
    """流程节点"""
    node_id: str
    node_type: NodeType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    outgoing: List[str] = field(default_factory=list)
    incoming: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "properties": self.properties,
            "outgoing": self.outgoing,
            "incoming": self.incoming
        }


@dataclass
class ProcessDefinition:
    """流程定义"""
    definition_id: str
    name: str
    version: int
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    start_node: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "definition_id": self.definition_id,
            "name": self.name,
            "version": self.version,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "start_node": self.start_node
        }


@dataclass
class ProcessInstance:
    """流程实例"""
    instance_id: str
    definition_id: str
    status: ProcessStatus
    variables: Dict[str, Any] = field(default_factory=dict)
    current_nodes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "definition_id": self.definition_id,
            "status": self.status.value,
            "variables": self.variables,
            "current_nodes": self.current_nodes,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class TaskInstance:
    """任务实例"""
    task_id: str
    instance_id: str
    node_id: str
    task_type: TaskType
    assignee: Optional[str]
    status: TaskStatus
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    form_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "instance_id": self.instance_id,
            "node_id": self.node_id,
            "task_type": self.task_type.value,
            "assignee": self.assignee,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class ProcessEngine:
    """流程引擎"""
    
    def __init__(self):
        self.process_definitions: Dict[str, ProcessDefinition] = {}
        self.process_instances: Dict[str, ProcessInstance] = {}
        self.task_instances: Dict[str, TaskInstance] = {}
        
        # 任务处理器
        self.task_handlers: Dict[TaskType, Callable] = {}
        
        # 规则引擎（简化版）
        self.rules: List[Dict] = []
        
        # 统计
        self.stats = {
            "total_instances": 0,
            "completed_instances": 0,
            "avg_duration_seconds": 0
        }
        
        logger.info("Process Engine initialized")
    
    def register_process_definition(self, definition: ProcessDefinition):
        """注册流程定义"""
        self.process_definitions[definition.definition_id] = definition
        logger.info(f"Registered process definition: {definition.name}")
    
    def start_process(self, definition_id: str,
                     variables: Dict[str, Any] = None) -> Optional[str]:
        """启动流程"""
        if definition_id not in self.process_definitions:
            return None
        
        definition = self.process_definitions[definition_id]
        
        instance_id = f"INST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        instance = ProcessInstance(
            instance_id=instance_id,
            definition_id=definition_id,
            status=ProcessStatus.RUNNING,
            variables=variables or {},
            current_nodes=[definition.start_node]
        )
        
        self.process_instances[instance_id] = instance
        self.stats["total_instances"] += 1
        
        # 激活起始节点
        self._activate_node(instance_id, definition.start_node)
        
        logger.info(f"Started process instance: {instance_id}")
        return instance_id
    
    def _activate_node(self, instance_id: str, node_id: str):
        """激活节点"""
        instance = self.process_instances[instance_id]
        definition = self.process_definitions[instance.definition_id]
        node = definition.nodes[node_id]
        
        if node.node_type == NodeType.TASK:
            # 创建任务
            task_type = TaskType(node.properties.get("task_type", "user_task"))
            task = TaskInstance(
                task_id=f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                instance_id=instance_id,
                node_id=node_id,
                task_type=task_type,
                assignee=node.properties.get("assignee"),
                status=TaskStatus.PENDING
            )
            self.task_instances[task.task_id] = task
            
            logger.info(f"Created task: {task.task_id} for node {node_id}")
            
        elif node.node_type == NodeType.GATEWAY:
            # 执行网关逻辑
            self._execute_gateway(instance_id, node_id)
            
        elif node.node_type == NodeType.END:
            # 结束流程
            instance.status = ProcessStatus.COMPLETED
            instance.completed_at = datetime.now()
            instance.current_nodes = []
            
            duration = (instance.completed_at - instance.created_at).total_seconds()
            self.stats["completed_instances"] += 1
            n = self.stats["completed_instances"]
            self.stats["avg_duration_seconds"] = (
                self.stats["avg_duration_seconds"] * (n-1) + duration
            ) / n
            
            logger.info(f"Process {instance_id} completed in {duration:.2f} seconds")
    
    def _execute_gateway(self, instance_id: str, node_id: str):
        """执行网关"""
        instance = self.process_instances[instance_id]
        definition = self.process_definitions[instance.definition_id]
        node = definition.nodes[node_id]
        
        gateway_type = GatewayType(node.properties.get("gateway_type", "exclusive"))
        
        if gateway_type == GatewayType.EXCLUSIVE:
            # 排他网关：选择第一个满足条件的分支
            for next_node_id in node.outgoing:
                if self._evaluate_condition(instance_id, node_id, next_node_id):
                    self._transition(instance_id, node_id, next_node_id)
                    break
                    
        elif gateway_type == GatewayType.PARALLEL:
            # 并行网关：所有分支并行执行
            for next_node_id in node.outgoing:
                self._transition(instance_id, node_id, next_node_id)
    
    def _evaluate_condition(self, instance_id: str,
                           from_node: str, to_node: str) -> bool:
        """评估条件"""
        instance = self.process_instances[instance_id]
        
        # 简化的条件评估
        # 实际应该解析和执行条件表达式
        return True
    
    def _transition(self, instance_id: str, from_node: str, to_node: str):
        """流程流转"""
        instance = self.process_instances[instance_id]
        
        # 移除当前节点
        if from_node in instance.current_nodes:
            instance.current_nodes.remove(from_node)
        
        # 添加新节点
        instance.current_nodes.append(to_node)
        
        # 激活新节点
        self._activate_node(instance_id, to_node)
    
    def complete_task(self, task_id: str, assignee: str,
                     form_data: Dict[str, Any] = None) -> bool:
        """完成任务"""
        if task_id not in self.task_instances:
            return False
        
        task = self.task_instances[task_id]
        
        # 检查分配
        if task.assignee and task.assignee != assignee:
            logger.warning(f"Task {task_id} is assigned to {task.assignee}, not {assignee}")
            return False
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.form_data = form_data or {}
        
        # 更新流程变量
        instance = self.process_instances[task.instance_id]
        instance.variables.update(form_data or {})
        
        # 流转到下一个节点
        definition = self.process_definitions[instance.definition_id]
        node = definition.nodes[task.node_id]
        
        for next_node_id in node.outgoing:
            self._transition(task.instance_id, task.node_id, next_node_id)
        
        logger.info(f"Completed task: {task_id}")
        return True
    
    def get_user_tasks(self, user_id: str) -> List[Dict]:
        """获取用户任务"""
        tasks = [
            task.to_dict() for task in self.task_instances.values()
            if task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]
            and (task.assignee == user_id or task.assignee is None)
        ]
        return tasks
    
    def get_process_status(self, instance_id: str) -> Optional[Dict]:
        """获取流程状态"""
        if instance_id not in self.process_instances:
            return None
        
        instance = self.process_instances[instance_id]
        definition = self.process_definitions[instance.definition_id]
        
        # 获取当前节点的详细信息
        current_nodes_info = []
        for node_id in instance.current_nodes:
            if node_id in definition.nodes:
                node = definition.nodes[node_id]
                current_nodes_info.append({
                    "node_id": node_id,
                    "name": node.name,
                    "type": node.node_type.value
                })
        
        return {
            **instance.to_dict(),
            "current_nodes_detail": current_nodes_info,
            "tasks": [
                t.to_dict() for t in self.task_instances.values()
                if t.instance_id == instance_id and t.status != TaskStatus.COMPLETED
            ]
        }
    
    def create_simple_approval_process(self, definition_id: str, name: str,
                                      approvers: List[str]) -> ProcessDefinition:
        """创建简单审批流程"""
        definition = ProcessDefinition(
            definition_id=definition_id,
            name=name,
            version=1
        )
        
        # 开始节点
        start = FlowNode(
            node_id="start",
            node_type=NodeType.START,
            name="Start",
            outgoing=["task1"]
        )
        definition.nodes["start"] = start
        definition.start_node = "start"
        
        # 审批任务节点
        prev_node = "start"
        for i, approver in enumerate(approvers):
            task_id = f"task{i+1}"
            task = FlowNode(
                node_id=task_id,
                node_type=NodeType.TASK,
                name=f"Approval {i+1}",
                properties={
                    "task_type": "user_task",
                    "assignee": approver
                },
                incoming=[prev_node],
                outgoing=[f"task{i+2}" if i < len(approvers) - 1 else "end"]
            )
            definition.nodes[task_id] = task
            prev_node = task_id
        
        # 结束节点
        end = FlowNode(
            node_id="end",
            node_type=NodeType.END,
            name="End",
            incoming=[prev_node]
        )
        definition.nodes["end"] = end
        
        self.register_process_definition(definition)
        return definition


def main():
    """演示流程引擎"""
    engine = ProcessEngine()
    
    # 创建审批流程定义
    engine.create_simple_approval_process(
        definition_id="purchase-approval",
        name="采购审批流程",
        approvers=["manager", "finance", "director"]
    )
    
    # 启动流程
    instance_id = engine.start_process(
        "purchase-approval",
        variables={
            "amount": 50000,
            "item": "服务器设备",
            "requester": "IT部门"
        }
    )
    
    print(f"Started process: {instance_id}")
    
    # 查看流程状态
    status = engine.get_process_status(instance_id)
    print(f"\nProcess status:")
    print(json.dumps(status, indent=2))
    
    # 获取待办任务
    tasks = engine.get_user_tasks("manager")
    print(f"\nManager's tasks: {len(tasks)}")
    
    # 完成第一个任务
    if tasks:
        engine.complete_task(
            tasks[0]["task_id"],
            "manager",
            {"approved": True, "comment": "同意采购"}
        )
    
    # 再次查看状态
    status = engine.get_process_status(instance_id)
    print(f"\nUpdated process status:")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
```

### 4.6 效果评估与ROI

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 新流程上线时间 | 2个月 | 3天 | -95% |
| 流程可视化覆盖率 | 30% | 100% | +70% |
| 系统集成率 | 20% | 88% | +68% |
| 流程优化周期 | 6个月 | 2周 | -92% |
| 移动端使用率 | 25% | 82% | +57% |

#### ROI计算

**投资成本**：
- 系统开发：800万元
- 集成实施：400万元
- **总投资**：1,200万元

**年度收益**：
- 效率提升：2,000万元
- 人力节省：600万元
- 错误减少：300万元
- **年度总收益**：2,900万元

**ROI分析**：
- 投资回收期：5个月
- 3年ROI：625%

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
