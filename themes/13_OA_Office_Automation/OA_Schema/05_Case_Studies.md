# 办公自动化Schema实践案例

## 📑 目录

- [办公自动化Schema实践案例](#办公自动化schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：文档管理系统和版本控制](#2-案例1文档管理系统和版本控制)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：请假审批流程管理](#3-案例2请假审批流程管理)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：任务管理系统](#4-案例3任务管理系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：文档格式批量转换](#5-案例4文档格式批量转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：OA数据分析和报表](#6-案例5oa数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)
    - [6.3 数据分析示例](#63-数据分析示例)
  - [7. 案例6：文档协作编辑（多人同时编辑）](#7-案例6文档协作编辑多人同时编辑)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：复杂审批流程（多级审批）](#8-案例7复杂审批流程多级审批)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：文档版本对比](#9-案例8文档版本对比)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 实现代码](#92-实现代码)
  - [10. 案例9：流程效率分析](#10-案例9流程效率分析)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 实现代码](#102-实现代码)
  - [11. 案例10：知识库管理](#11-案例10知识库管理)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)
  - [12. 案例11：文档智能分析系统](#12-案例11文档智能分析系统)
    - [12.1 场景描述](#121-场景描述)
    - [12.2 Schema定义](#122-schema定义)
    - [12.3 实现代码](#123-实现代码)
  - [13. 案例12：流程自动化系统](#13-案例12流程自动化系统)
    - [13.1 场景描述](#131-场景描述)
    - [13.2 Schema定义](#132-schema定义)
    - [13.3 实现代码](#133-实现代码)
  - [14. 案例13：协作效率分析系统](#14-案例13协作效率分析系统)
    - [14.1 场景描述](#141-场景描述)
    - [14.2 Schema定义](#142-schema定义)
    - [14.3 实现代码](#143-实现代码)

---

## 1. 案例概述

本文档提供办公自动化Schema在实际应用中的实践案例。

---

## 2. 案例1：文档管理系统和版本控制

### 2.1 场景描述

**业务背景**：
企业需要管理大量文档，支持版本控制、权限管理和文档检索功能。
文档需要支持ODF和OOXML格式，并能在这两种格式之间转换。

**技术挑战**：

- 需要实现文档版本控制
- 需要管理文档权限
- 需要支持文档格式转换
- 需要实现文档全文检索

**解决方案**：
使用DocumentVersionManager实现文档版本控制，使用ODFToOOXMLConverter
实现文档格式转换。

### 2.2 Schema定义

详见第2.2节原始定义。

### 2.3 实现代码

**完整的文档管理系统实现**：

```python
from oa_storage import OAStorage
from document_version_manager import DocumentVersionManager
from odf_to_ooxml_converter import ODFToOOXMLConverter
from datetime import datetime

# 初始化存储和组件
storage = OAStorage("postgresql://user:pass@localhost/oa")
version_manager = DocumentVersionManager(storage)
converter = ODFToOOXMLConverter()

# 创建文档
document_data = {
    "document_id": "DOC20250121001",
    "document_title": "项目计划书",
    "document_type": "Word",
    "author": "张三",
    "file_path": "/documents/project/plan.odt",
    "file_size": 102400,
    "mime_type": "application/vnd.oasis.opendocument.text",
    "current_version": 1
}

# 存储文档
doc_id = storage.store_document(document_data)
print(f"Created document: {doc_id}")

# 创建版本1
version1 = version_manager.create_version(
    "DOC20250121001",
    "张三",
    "/documents/project/plan_v1.odt",
    "初始版本"
)
print(f"Created version 1: {version1}")

# 创建版本2
version2 = version_manager.create_version(
    "DOC20250121001",
    "李四",
    "/documents/project/plan_v2.odt",
    "添加项目预算"
)
print(f"Created version 2: {version2}")

# 查询版本历史
history = version_manager.get_version_history("DOC20250121001")
print(f"\nVersion history:")
for version in history:
    print(f"  Version {version['version_number']}: {version['version_author']} - {version['version_comment']}")

# 转换ODF到OOXML
ooxml_path = converter.convert_document("/documents/project/plan.odt")
if ooxml_path:
    print(f"\nConverted to OOXML: {ooxml_path}")

    # 创建OOXML版本
    version3 = version_manager.create_version(
        "DOC20250121001",
        "张三",
        ooxml_path,
        "转换为DOCX格式"
    )
    print(f"Created version 3 (OOXML): {version3}")

# 恢复版本1
restored = version_manager.restore_version("DOC20250121001", 1)
if restored:
    print("\nRestored version 1")
```

---

## 3. 案例2：请假审批流程管理

### 3.1 场景描述

**业务背景**：
企业需要实现请假审批流程，支持多级审批、流程跟踪和审批历史查询。
流程需要支持BPMN标准定义，并能灵活配置审批节点。

**技术挑战**：

- 需要实现工作流引擎
- 需要支持多级审批
- 需要流程状态跟踪
- 需要审批历史记录

**解决方案**：
使用WorkflowEngine实现BPMN工作流引擎，支持流程定义、启动和审批。

### 3.2 Schema定义

详见第3.2节原始定义。

### 3.3 实现代码

**完整的请假审批流程实现**：

```python
from workflow_engine import WorkflowEngine
from oa_storage import OAStorage
from datetime import datetime

# 初始化工作流引擎和存储
storage = OAStorage("postgresql://user:pass@localhost/oa")
workflow_engine = WorkflowEngine(storage)

# 定义请假审批流程
leave_process_definition = {
    "process_id": "LEAVE_PROCESS",
    "process_name": "请假审批流程",
    "process_type": "Leave",
    "process_definition": {
        "process_version": 1,
        "process_nodes": [
            {
                "node_id": "NODE001",
                "node_name": "提交申请",
                "node_type": "Start",
                "node_order": 1
            },
            {
                "node_id": "NODE002",
                "node_name": "部门经理审批",
                "node_type": "Approval",
                "approver": "部门经理",
                "node_order": 2
            },
            {
                "node_id": "NODE003",
                "node_name": "HR审批",
                "node_type": "Approval",
                "approver": "HR",
                "node_order": 3
            },
            {
                "node_id": "NODE004",
                "node_name": "完成",
                "node_type": "End",
                "node_order": 4
            }
        ]
    }
}

# 注册流程定义
workflow_engine.define_process("LEAVE_PROCESS", leave_process_definition)

# 启动流程实例
process_data = {
    "leave_type": "年假",
    "start_date": "2025-02-01",
    "end_date": "2025-02-05",
    "days": 5,
    "reason": "个人事务"
}

instance_id = workflow_engine.start_process(
    "LEAVE_PROCESS",
    "张三",
    process_data
)
print(f"Started process instance: {instance_id}")

# 查询流程状态
status = workflow_engine.get_process_status(instance_id)
print(f"\nProcess status: {status['current_status']}")
print(f"Current node: {status['current_node']}")

# 部门经理审批
workflow_engine.approve_node(
    instance_id,
    "部门经理",
    "Approved",
    "同意请假申请"
)

# 查询更新后的状态
status = workflow_engine.get_process_status(instance_id)
print(f"\nAfter department manager approval:")
print(f"  Status: {status['current_status']}")
print(f"  Current node: {status['current_node']}")

# HR审批
workflow_engine.approve_node(
    instance_id,
    "HR",
    "Approved",
    "审批通过"
)

# 查询最终状态
status = workflow_engine.get_process_status(instance_id)
print(f"\nFinal status: {status['current_status']}")

# 查询审批历史
history = storage.get_process_approval_history(instance_id)
print(f"\nApproval history:")
for record in history:
    print(f"  {record['node_id']}: {record['approver']} - {record['approval_result']} - {record['approval_time']}")
```

---

## 4. 案例3：任务管理系统

### 4.1 场景描述

**业务背景**：
企业需要管理项目任务，支持任务分配、状态跟踪、优先级管理和工作量统计。

**技术挑战**：

- 需要任务分配和跟踪
- 需要优先级管理
- 需要工作量统计
- 需要任务提醒

**解决方案**：
使用OAStorage存储任务数据，实现任务管理和统计功能。

### 4.2 Schema定义

详见第4.2节原始定义。

### 4.3 实现代码

**完整的任务管理系统实现**：

```python
from oa_storage import OAStorage
from datetime import datetime, timedelta

# 初始化存储
storage = OAStorage("postgresql://user:pass@localhost/oa")

# 创建任务
task_data = {
    "task_id": "TASK20250121001",
    "task_title": "完成项目文档",
    "task_description": "编写项目需求文档和技术方案",
    "assignee": "李四",
    "assigner": "张三",
    "task_status": "Todo",
    "priority": "High",
    "due_date": datetime.now() + timedelta(days=5)
}

task_id = storage.store_task(task_data)
print(f"Created task: {task_id}")

# 更新任务状态
storage.update_task_status("TASK20250121001", "InProgress")
print("Updated task status to InProgress")

# 查询任务统计
task_stats = storage.get_task_statistics(assignee="李四", days=30)
print(f"\nTask statistics for 李四:")
for status, stats in task_stats.items():
    print(f"  {status}: {stats['count']} tasks, {stats['overdue_count']} overdue")

# 查询用户工作量
workload = storage.get_user_workload("李四", days=7)
print(f"\nWorkload for 李四 (7 days):")
print(f"  Tasks: {workload['tasks']}")
print(f"  Approvals: {workload['approvals']}")
```

---

## 5. 案例4：文档格式批量转换

### 5.1 场景描述

**业务背景**：
企业需要将大量ODF文档批量转换为OOXML格式，以便与Microsoft Office系统集成。

**技术挑战**：

- 需要批量转换文档
- 需要保持文档格式
- 需要转换进度跟踪
- 需要错误处理

**解决方案**：
使用ODFToOOXMLConverter实现批量文档转换。

### 5.2 实现代码

**批量文档转换实现**：

```python
from odf_to_ooxml_converter import ODFToOOXMLConverter
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
converter = ODFToOOXMLConverter()

# 批量转换ODF文档
odf_directory = Path("/documents/odf")
output_directory = Path("/documents/ooxml")
output_directory.mkdir(exist_ok=True)

odf_files = list(odf_directory.glob("*.odt")) + \
            list(odf_directory.glob("*.ods")) + \
            list(odf_directory.glob("*.odp"))

print(f"Found {len(odf_files)} ODF files to convert")

success_count = 0
failed_count = 0

for odf_file in odf_files:
    try:
        output_path = output_directory / odf_file.with_suffix(
            converter._get_ooxml_extension(odf_file.suffix)
        ).name

        result = converter.convert_document(str(odf_file), str(output_path))
        if result:
            success_count += 1
            print(f"✓ Converted: {odf_file.name} -> {output_path.name}")
        else:
            failed_count += 1
            print(f"✗ Failed: {odf_file.name}")
    except Exception as e:
        failed_count += 1
        print(f"✗ Error converting {odf_file.name}: {e}")

print(f"\nConversion complete:")
print(f"  Success: {success_count}")
print(f"  Failed: {failed_count}")
```

---

## 6. 案例5：OA数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储办公自动化数据，支持文档统计、流程分析和用户工作量统计。

### 6.2 实现代码

详见 `04_Transformation.md` 第7章。

### 6.3 数据分析示例

**OA数据分析查询**：

```python
from oa_storage import OAStorage
from datetime import datetime, timedelta

storage = OAStorage("postgresql://user:pass@localhost/oa")

# 查询文档统计
doc_stats = storage.get_document_statistics(datetime.now() - timedelta(days=30))
print("Document Statistics (30 days):")
for stat in doc_stats:
    print(f"  {stat['document_type']}: {stat['count']} documents, "
          f"Total size: {stat['total_size']/1024/1024:.2f}MB")

# 查询流程审批统计
process_stats = storage.get_process_statistics(days=30)
print("\nProcess Statistics (30 days):")
for stat in process_stats:
    print(f"  {stat['process_type']} - {stat['current_status']}: "
          f"{stat['count']} processes, Avg: {stat['avg_hours']:.2f} hours")

# 查询用户工作量
workload = storage.get_user_workload("张三", days=7)
print(f"\nWorkload for 张三 (7 days):")
print(f"  Tasks: {workload['tasks']}")
print(f"  Approvals: {workload['approvals']}")
```

---

## 7. 案例6：文档协作编辑（多人同时编辑）

### 7.1 场景描述

**业务背景**：
企业需要支持多人同时编辑同一文档，实现实时协作编辑功能。
多个用户可以在同一文档的不同部分进行编辑，系统需要跟踪每个用户的编辑操作，并记录协作历史。

**技术挑战**：

- 需要实现文档锁定机制（段落/章节级别）
- 需要跟踪每个用户的编辑操作
- 需要处理编辑冲突
- 需要记录协作历史

**解决方案**：
使用文档协作记录表跟踪每个用户的编辑操作，实现段落级别的锁定机制，支持多人同时编辑。

### 7.2 Schema定义

**文档协作编辑Schema**：

```json
{
  "document_id": "DOC001",
  "collaboration_mode": "concurrent",
  "active_users": [
    {
      "user_id": "user001",
      "user_name": "张三",
      "editing_sections": ["section1", "section2"],
      "last_activity": "2025-01-21T10:30:00Z"
    },
    {
      "user_id": "user002",
      "user_name": "李四",
      "editing_sections": ["section3"],
      "last_activity": "2025-01-21T10:25:00Z"
    }
  ],
  "lock_rules": {
    "lock_level": "paragraph",
    "auto_unlock_minutes": 30
  }
}
```

### 7.3 实现代码

**完整的文档协作编辑实现**：

```python
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from oa_storage import OAStorage
from document_version_manager import DocumentVersionManager

logger = logging.getLogger(__name__)

class DocumentCollaborationManager:
    """文档协作管理器"""

    def __init__(self, storage: OAStorage):
        self.storage = storage
        self.active_sessions: Dict[str, Dict] = {}
        self.locked_sections: Dict[str, Dict] = {}

    def start_editing_session(self, document_id: str, user_id: str,
                              section_id: str = None) -> bool:
        """开始编辑会话"""
        # 检查权限
        if not self.storage.check_document_permission(document_id, user_id, "write"):
            logger.warning(f"User {user_id} does not have write permission for {document_id}")
            return False

        # 检查段落是否被锁定
        if section_id:
            if self._is_section_locked(document_id, section_id, user_id):
                logger.warning(f"Section {section_id} is locked by another user")
                return False
            self._lock_section(document_id, section_id, user_id)

        # 记录协作操作
        self.storage.store_collaboration_record(
            document_id,
            user_id,
            "start_editing",
            f"Started editing session",
            {"section_id": section_id}
        )

        # 更新活动会话
        session_key = f"{document_id}_{user_id}"
        self.active_sessions[session_key] = {
            "document_id": document_id,
            "user_id": user_id,
            "section_id": section_id,
            "start_time": datetime.now(),
            "last_activity": datetime.now()
        }

        logger.info(f"User {user_id} started editing session for {document_id}")
        return True

    def save_edit(self, document_id: str, user_id: str, section_id: str,
                  content: str, change_description: str = None):
        """保存编辑"""
        # 记录编辑操作
        self.storage.store_collaboration_record(
            document_id,
            user_id,
            "edit",
            change_description or "Edited content",
            {
                "section_id": section_id,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat()
            }
        )

        # 更新活动会话
        session_key = f"{document_id}_{user_id}"
        if session_key in self.active_sessions:
            self.active_sessions[session_key]["last_activity"] = datetime.now()

        logger.info(f"User {user_id} saved edit for {document_id}, section {section_id}")

    def end_editing_session(self, document_id: str, user_id: str):
        """结束编辑会话"""
        session_key = f"{document_id}_{user_id}"
        if session_key in self.active_sessions:
            session = self.active_sessions[session_key]
            section_id = session.get("section_id")

            # 解锁段落
            if section_id:
                self._unlock_section(document_id, section_id, user_id)

            # 记录协作操作
            self.storage.store_collaboration_record(
                document_id,
                user_id,
                "end_editing",
                "Ended editing session",
                {
                    "duration_minutes": (datetime.now() - session["start_time"]).total_seconds() / 60
                }
            )

            del self.active_sessions[session_key]
            logger.info(f"User {user_id} ended editing session for {document_id}")

    def get_active_collaborators(self, document_id: str) -> List[Dict]:
        """获取活动协作者"""
        collaborators = []
        for session_key, session in self.active_sessions.items():
            if session["document_id"] == document_id:
                collaborators.append({
                    "user_id": session["user_id"],
                    "section_id": session.get("section_id"),
                    "last_activity": session["last_activity"]
                })
        return collaborators

    def get_collaboration_history(self, document_id: str, limit: int = 100) -> List[Dict]:
        """获取协作历史"""
        return self.storage.get_collaboration_history(document_id, limit)

    def _is_section_locked(self, document_id: str, section_id: str, user_id: str) -> bool:
        """检查段落是否被锁定"""
        lock_key = f"{document_id}_{section_id}"
        if lock_key in self.locked_sections:
            lock_info = self.locked_sections[lock_key]
            # 检查是否是自己锁定的
            if lock_info["user_id"] == user_id:
                return False
            # 检查锁定是否过期（30分钟）
            if datetime.now() - lock_info["lock_time"] > timedelta(minutes=30):
                del self.locked_sections[lock_key]
                return False
            return True
        return False

    def _lock_section(self, document_id: str, section_id: str, user_id: str):
        """锁定段落"""
        lock_key = f"{document_id}_{section_id}"
        self.locked_sections[lock_key] = {
            "document_id": document_id,
            "section_id": section_id,
            "user_id": user_id,
            "lock_time": datetime.now()
        }

    def _unlock_section(self, document_id: str, section_id: str, user_id: str):
        """解锁段落"""
        lock_key = f"{document_id}_{section_id}"
        if lock_key in self.locked_sections:
            if self.locked_sections[lock_key]["user_id"] == user_id:
                del self.locked_sections[lock_key]

async def collaborative_editing_example():
    """文档协作编辑示例"""
    storage = OAStorage("postgresql://user:pass@localhost/oa")
    collab_manager = DocumentCollaborationManager(storage)

    document_id = "DOC001"

    # 授予权限
    storage.grant_document_permission(document_id, "user001", "write", "admin")
    storage.grant_document_permission(document_id, "user002", "write", "admin")

    # 用户1开始编辑
    print("User 1 starting editing session...")
    collab_manager.start_editing_session(document_id, "user001", "section1")

    # 用户2开始编辑（不同段落）
    print("User 2 starting editing session...")
    collab_manager.start_editing_session(document_id, "user002", "section2")

    # 保存编辑
    collab_manager.save_edit(document_id, "user001", "section1", "Updated content", "Added introduction")
    collab_manager.save_edit(document_id, "user002", "section2", "Updated content", "Added conclusion")

    # 获取活动协作者
    collaborators = collab_manager.get_active_collaborators(document_id)
    print(f"\nActive collaborators: {len(collaborators)}")
    for collab in collaborators:
        print(f"  User: {collab['user_id']}, Section: {collab['section_id']}")

    # 获取协作历史
    history = collab_manager.get_collaboration_history(document_id)
    print(f"\nCollaboration history: {len(history)} records")
    for record in history[:5]:
        print(f"  {record['user_id']}: {record['action_type']} at {record['action_time']}")

    # 结束编辑会话
    collab_manager.end_editing_session(document_id, "user001")
    collab_manager.end_editing_session(document_id, "user002")

    storage.close()

if __name__ == "__main__":
    asyncio.run(collaborative_editing_example())
```

---

## 8. 案例7：复杂审批流程（多级审批）

### 8.1 场景描述

**业务背景**：
企业需要实现复杂的多级审批流程，例如采购审批需要经过部门经理、财务经理、总经理三级审批。每个审批节点可能有不同的审批规则和条件。

**技术挑战**：

- 需要支持多级审批流程
- 需要支持条件分支（根据金额决定审批路径）
- 需要支持并行审批（多个审批人同时审批）
- 需要支持审批退回和重新提交

**解决方案**：
使用BPMN流程定义描述复杂审批流程，通过工作流引擎执行流程，支持条件分支和并行审批。

### 8.2 Schema定义

**复杂审批流程Schema**：

```json
{
  "process_id": "purchase_approval",
  "process_name": "采购审批流程",
  "process_type": "MultiLevelApproval",
  "process_definition": {
    "process_nodes": [
      {
        "node_id": "start",
        "node_name": "开始",
        "node_type": "Start",
        "node_order": 1
      },
      {
        "node_id": "dept_manager",
        "node_name": "部门经理审批",
        "node_type": "Approval",
        "node_order": 2,
        "assignee": "dept_manager",
        "condition": null
      },
      {
        "node_id": "gateway_amount",
        "node_name": "金额判断",
        "node_type": "Gateway",
        "node_order": 3,
        "condition": "amount > 10000"
      },
      {
        "node_id": "finance_manager",
        "node_name": "财务经理审批",
        "node_type": "Approval",
        "node_order": 4,
        "assignee": "finance_manager",
        "condition": "amount > 10000"
      },
      {
        "node_id": "general_manager",
        "node_name": "总经理审批",
        "node_type": "Approval",
        "node_order": 5,
        "assignee": "general_manager",
        "condition": "amount > 50000"
      },
      {
        "node_id": "end",
        "node_name": "结束",
        "node_type": "End",
        "node_order": 6
      }
    ]
  }
}
```

### 8.3 实现代码

**完整的复杂审批流程实现**：

```python
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from workflow_engine import WorkflowEngine, ProcessStatus
from oa_storage import OAStorage

logger = logging.getLogger(__name__)

class MultiLevelApprovalProcess:
    """多级审批流程"""

    def __init__(self, workflow_engine: WorkflowEngine, storage: OAStorage):
        self.workflow_engine = workflow_engine
        self.storage = storage

    def define_purchase_approval_process(self):
        """定义采购审批流程"""
        process_definition = {
            "process_id": "purchase_approval",
            "process_name": "采购审批流程",
            "process_type": "MultiLevelApproval",
            "process_definition": {
                "process_nodes": [
                    {
                        "node_id": "start",
                        "node_name": "开始",
                        "node_type": "Start",
                        "node_order": 1
                    },
                    {
                        "node_id": "dept_manager",
                        "node_name": "部门经理审批",
                        "node_type": "Approval",
                        "node_order": 2,
                        "assignee": "dept_manager"
                    },
                    {
                        "node_id": "gateway_amount",
                        "node_name": "金额判断网关",
                        "node_type": "Gateway",
                        "node_order": 3
                    },
                    {
                        "node_id": "finance_manager",
                        "node_name": "财务经理审批",
                        "node_type": "Approval",
                        "node_order": 4,
                        "assignee": "finance_manager",
                        "condition": "amount > 10000"
                    },
                    {
                        "node_id": "general_manager",
                        "node_name": "总经理审批",
                        "node_type": "Approval",
                        "node_order": 5,
                        "assignee": "general_manager",
                        "condition": "amount > 50000"
                    },
                    {
                        "node_id": "end",
                        "node_name": "结束",
                        "node_type": "End",
                        "node_order": 6
                    }
                ]
            }
        }

        self.workflow_engine.define_process("purchase_approval", process_definition)
        logger.info("Defined purchase approval process")

    def start_purchase_approval(self, submitter: str, amount: float,
                               purchase_items: List[Dict]) -> str:
        """启动采购审批"""
        process_data = {
            "amount": amount,
            "purchase_items": purchase_items,
            "submitter": submitter
        }

        instance_id = self.workflow_engine.start_process(
            "purchase_approval",
            submitter,
            process_data
        )

        logger.info(f"Started purchase approval process: {instance_id}")
        return instance_id

    def approve_with_condition(self, instance_id: str, approver: str,
                              approval_result: str, comment: str = ""):
        """条件审批"""
        process = self.workflow_engine.get_process_status(instance_id)
        if not process:
            raise ValueError(f"Process instance not found: {instance_id}")

        process_data = process.get("process_data", {})
        amount = process_data.get("amount", 0)

        # 审批当前节点
        self.workflow_engine.approve_node(instance_id, approver, approval_result, comment)

        if approval_result == "Approved":
            # 根据金额决定下一个节点
            current_node = process.get("current_node")
            definition = self.workflow_engine.process_definitions[process["process_id"]]

            # 获取下一个节点（考虑条件）
            next_node = self._get_next_node_with_condition(
                definition, current_node, amount
            )

            if next_node:
                # 更新当前节点
                process["current_node"] = next_node["node_id"]
                # 分配任务
                if next_node.get("assignee"):
                    self.workflow_engine.assign_task(
                        instance_id,
                        next_node["node_id"],
                        next_node["assignee"]
                    )

    def _get_next_node_with_condition(self, definition: Dict, current_node_id: str,
                                     amount: float) -> Optional[Dict]:
        """根据条件获取下一个节点"""
        nodes = definition.get("process_definition", {}).get("process_nodes", [])
        current_node = None

        for node in nodes:
            if node.get("node_id") == current_node_id:
                current_node = node
                break

        if not current_node:
            return None

        current_order = current_node.get("node_order", 0)

        # 查找下一个节点
        for node in nodes:
            node_order = node.get("node_order", 0)
            if node_order > current_order:
                # 检查条件
                condition = node.get("condition")
                if condition:
                    if condition == "amount > 10000" and amount <= 10000:
                        continue
                    if condition == "amount > 50000" and amount <= 50000:
                        continue
                return node

        return None

async def multi_level_approval_example():
    """多级审批流程示例"""
    storage = OAStorage("postgresql://user:pass@localhost/oa")
    workflow_engine = WorkflowEngine(storage)
    approval_process = MultiLevelApprovalProcess(workflow_engine, storage)

    # 定义流程
    approval_process.define_purchase_approval_process()

    # 启动审批流程（金额15000，需要财务经理审批）
    instance_id = approval_process.start_purchase_approval(
        "user001",
        15000.0,
        [{"item": "办公用品", "quantity": 100}]
    )

    print(f"Started approval process: {instance_id}")

    # 部门经理审批
    print("\nDepartment manager approving...")
    approval_process.approve_with_condition(
        instance_id,
        "dept_manager",
        "Approved",
        "同意采购"
    )

    # 财务经理审批（因为金额>10000）
    print("\nFinance manager approving...")
    approval_process.approve_with_condition(
        instance_id,
        "finance_manager",
        "Approved",
        "同意采购"
    )

    # 检查流程状态
    status = workflow_engine.get_process_status(instance_id)
    print(f"\nProcess status: {status['current_status']}")
    print(f"Current node: {status['current_node']}")

    storage.close()

if __name__ == "__main__":
    asyncio.run(multi_level_approval_example())
```

---

## 9. 案例8：文档版本对比

### 9.1 场景描述

**业务背景**：
企业需要对比文档的不同版本，查看版本之间的差异，了解文档的变更历史。这对于文档审查和版本管理非常重要。

**技术挑战**：

- 需要提取文档内容
- 需要对比两个版本的差异
- 需要高亮显示变更内容
- 需要生成对比报告

**解决方案**：
使用文档内容表存储文档的文本内容，实现版本对比算法，生成差异报告。

### 9.2 实现代码

**完整的文档版本对比实现**：

```python
import difflib
from typing import List, Dict, Tuple
from oa_storage import OAStorage
from document_version_manager import DocumentVersionManager

class DocumentVersionComparator:
    """文档版本对比器"""

    def __init__(self, storage: OAStorage):
        self.storage = storage

    def compare_versions(self, document_id: str, version1: int, version2: int) -> Dict:
        """对比两个版本"""
        # 获取版本内容
        content1 = self._get_version_content(document_id, version1)
        content2 = self._get_version_content(document_id, version2)

        if not content1 or not content2:
            return {"error": "Version content not found"}

        # 对比内容
        diff = self._compute_diff(content1, content2)

        return {
            "document_id": document_id,
            "version1": version1,
            "version2": version2,
            "diff": diff,
            "statistics": self._compute_statistics(diff)
        }

    def _get_version_content(self, document_id: str, version: int) -> Optional[str]:
        """获取版本内容"""
        self.storage.cur.execute("""
            SELECT content_text FROM document_contents
            WHERE document_id = %s AND version_number = %s
        """, (document_id, version))
        result = self.storage.cur.fetchone()
        return result[0] if result else None

    def _compute_diff(self, content1: str, content2: str) -> List[Dict]:
        """计算差异"""
        lines1 = content1.splitlines(keepends=True)
        lines2 = content2.splitlines(keepends=True)

        diff = difflib.unified_diff(
            lines1, lines2,
            lineterm='',
            n=3
        )

        diff_list = []
        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                continue
            elif line.startswith('@@'):
                diff_list.append({"type": "header", "content": line})
            elif line.startswith('-'):
                diff_list.append({"type": "deleted", "content": line[1:]})
            elif line.startswith('+'):
                diff_list.append({"type": "added", "content": line[1:]})
            else:
                diff_list.append({"type": "unchanged", "content": line})

        return diff_list

    def _compute_statistics(self, diff: List[Dict]) -> Dict:
        """计算统计信息"""
        stats = {
            "added_lines": 0,
            "deleted_lines": 0,
            "unchanged_lines": 0,
            "total_changes": 0
        }

        for item in diff:
            if item["type"] == "added":
                stats["added_lines"] += 1
                stats["total_changes"] += 1
            elif item["type"] == "deleted":
                stats["deleted_lines"] += 1
                stats["total_changes"] += 1
            elif item["type"] == "unchanged":
                stats["unchanged_lines"] += 1

        return stats

    def generate_diff_report(self, document_id: str, version1: int, version2: int) -> str:
        """生成差异报告"""
        comparison = self.compare_versions(document_id, version1, version2)

        report = f"Document Version Comparison Report\n"
        report += f"{'='*50}\n\n"
        report += f"Document ID: {comparison['document_id']}\n"
        report += f"Version {comparison['version1']} vs Version {comparison['version2']}\n\n"

        stats = comparison['statistics']
        report += f"Statistics:\n"
        report += f"  Added lines: {stats['added_lines']}\n"
        report += f"  Deleted lines: {stats['deleted_lines']}\n"
        report += f"  Unchanged lines: {stats['unchanged_lines']}\n"
        report += f"  Total changes: {stats['total_changes']}\n\n"

        report += f"Differences:\n"
        report += f"{'-'*50}\n"

        for item in comparison['diff']:
            if item['type'] == 'added':
                report += f"+ {item['content']}"
            elif item['type'] == 'deleted':
                report += f"- {item['content']}"
            elif item['type'] == 'header':
                report += f"{item['content']}\n"

        return report

def version_comparison_example():
    """文档版本对比示例"""
    storage = OAStorage("postgresql://user:pass@localhost/oa")
    comparator = DocumentVersionComparator(storage)

    document_id = "DOC001"

    # 对比版本1和版本2
    comparison = comparator.compare_versions(document_id, 1, 2)
    print("Version Comparison:")
    print(f"  Added lines: {comparison['statistics']['added_lines']}")
    print(f"  Deleted lines: {comparison['statistics']['deleted_lines']}")

    # 生成差异报告
    report = comparator.generate_diff_report(document_id, 1, 2)
    print("\nDiff Report:")
    print(report)

    storage.close()

if __name__ == "__main__":
    version_comparison_example()
```

---

## 10. 案例9：流程效率分析

### 10.1 场景描述

**业务背景**：
企业需要分析审批流程的效率，找出流程瓶颈，优化流程设计。通过分析流程的执行时间、各节点的处理时间、审批通过率等指标，帮助企业改进流程效率。

**技术挑战**：

- 需要收集流程执行数据
- 需要计算流程性能指标
- 需要识别流程瓶颈
- 需要生成分析报告

**解决方案**：
使用流程监控器收集流程执行数据，计算性能指标，生成流程效率分析报告。

### 10.2 实现代码

**完整的流程效率分析实现**：

```python
from typing import Dict, List
from datetime import datetime, timedelta
from process_monitor import ProcessMonitor
from workflow_engine import WorkflowEngine
from oa_storage import OAStorage

class ProcessEfficiencyAnalyzer:
    """流程效率分析器"""

    def __init__(self, process_monitor: ProcessMonitor):
        self.process_monitor = process_monitor

    def analyze_process_efficiency(self, process_id: str,
                                  start_date: datetime = None,
                                  end_date: datetime = None) -> Dict:
        """分析流程效率"""
        # 获取性能指标
        metrics = self.process_monitor.get_process_performance_metrics(
            process_id, start_date, end_date
        )

        # 获取流程统计
        stats = self.process_monitor.workflow_engine.get_process_statistics(
            process_id, start_date, end_date
        )

        # 分析瓶颈节点
        bottlenecks = self._identify_bottlenecks(process_id, start_date, end_date)

        return {
            "process_id": process_id,
            "metrics": metrics,
            "statistics": stats,
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_recommendations(metrics, bottlenecks)
        }

    def _identify_bottlenecks(self, process_id: str,
                             start_date: datetime = None,
                             end_date: datetime = None) -> List[Dict]:
        """识别流程瓶颈"""
        # 这里需要查询各节点的平均处理时间
        # 简化实现，实际需要从数据库查询节点处理时间
        bottlenecks = []

        # 示例：假设某些节点处理时间较长
        # 实际实现需要从task_assignments表查询数据

        return bottlenecks

    def _generate_recommendations(self, metrics: Dict, bottlenecks: List[Dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        if metrics.get("average_duration_hours", 0) > 24:
            recommendations.append("流程平均处理时间超过24小时，建议优化流程设计")

        if metrics.get("rejection_rate", 0) > 0.3:
            recommendations.append("流程拒绝率超过30%，建议检查审批条件设置")

        if metrics.get("completion_rate", 0) < 0.7:
            recommendations.append("流程完成率低于70%，建议检查流程设计")

        return recommendations

    def generate_efficiency_report(self, process_id: str,
                                   start_date: datetime = None,
                                   end_date: datetime = None) -> str:
        """生成效率分析报告"""
        analysis = self.analyze_process_efficiency(process_id, start_date, end_date)

        report = f"Process Efficiency Analysis Report\n"
        report += f"{'='*60}\n\n"
        report += f"Process ID: {analysis['process_id']}\n"
        if start_date:
            report += f"Start Date: {start_date.strftime('%Y-%m-%d')}\n"
        if end_date:
            report += f"End Date: {end_date.strftime('%Y-%m-%d')}\n"
        report += f"\n"

        metrics = analysis['metrics']
        report += f"Performance Metrics:\n"
        report += f"  Total Processes: {metrics['total_processes']}\n"
        report += f"  Completion Rate: {metrics['completion_rate']*100:.1f}%\n"
        report += f"  Rejection Rate: {metrics['rejection_rate']*100:.1f}%\n"
        report += f"  Average Duration: {metrics['average_duration_hours']:.2f} hours\n"
        report += f"  Throughput: {metrics['throughput_per_day']:.2f} processes/day\n"
        report += f"\n"

        stats = analysis['statistics']
        report += f"Statistics:\n"
        report += f"  Completed: {stats['completed_processes']}\n"
        report += f"  In Progress: {stats['in_progress_processes']}\n"
        report += f"  Rejected: {stats['rejected_processes']}\n"
        report += f"\n"

        recommendations = analysis['recommendations']
        if recommendations:
            report += f"Recommendations:\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"  {i}. {rec}\n"

        return report

def process_efficiency_analysis_example():
    """流程效率分析示例"""
    storage = OAStorage("postgresql://user:pass@localhost/oa")
    workflow_engine = WorkflowEngine(storage)
    process_monitor = ProcessMonitor(workflow_engine, storage)
    analyzer = ProcessEfficiencyAnalyzer(process_monitor)

    process_id = "purchase_approval"
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    # 分析流程效率
    analysis = analyzer.analyze_process_efficiency(
        process_id, start_date, end_date
    )

    print("Process Efficiency Analysis:")
    print(f"  Completion Rate: {analysis['metrics']['completion_rate']*100:.1f}%")
    print(f"  Average Duration: {analysis['metrics']['average_duration_hours']:.2f} hours")

    # 生成报告
    report = analyzer.generate_efficiency_report(
        process_id, start_date, end_date
    )
    print("\nEfficiency Report:")
    print(report)

    storage.close()

if __name__ == "__main__":
    process_efficiency_analysis_example()
```

---

## 11. 案例10：知识库管理

### 11.1 场景描述

**业务背景**：
企业需要建立知识库系统，管理企业文档、经验总结、最佳实践等知识资产。知识库需要支持分类管理、标签管理、全文检索、权限控制等功能。

**技术挑战**：

- 需要实现知识分类体系
- 需要支持标签管理
- 需要实现全文检索
- 需要支持知识推荐

**解决方案**：
使用文档内容表的全文索引实现知识检索，使用分类和标签管理知识组织，实现知识推荐算法。

### 11.2 Schema定义

**知识库管理Schema**：

```json
{
  "knowledge_base_id": "KB001",
  "knowledge_base_name": "企业知识库",
  "categories": [
    {
      "category_id": "CAT001",
      "category_name": "技术文档",
      "parent_category": null,
      "description": "技术相关文档"
    },
    {
      "category_id": "CAT002",
      "category_name": "业务流程",
      "parent_category": null,
      "description": "业务流程文档"
    }
  ],
  "tags": [
    {"tag_id": "TAG001", "tag_name": "Python"},
    {"tag_id": "TAG002", "tag_name": "数据库"},
    {"tag_id": "TAG003", "tag_name": "审批流程"}
  ]
}
```

### 11.3 实现代码

**完整的知识库管理实现**：

```python
from typing import Dict, List, Optional
from oa_storage import OAStorage

class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, storage: OAStorage):
        self.storage = storage

    def create_category(self, category_id: str, category_name: str,
                       parent_category: str = None, description: str = None):
        """创建知识分类"""
        self.storage.cur.execute("""
            INSERT INTO knowledge_categories (
                category_id, category_name, parent_category, description
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (category_id) DO UPDATE SET
                category_name = EXCLUDED.category_name,
                parent_category = EXCLUDED.parent_category,
                description = EXCLUDED.description
        """, (category_id, category_name, parent_category, description))
        self.storage.conn.commit()

    def add_document_to_knowledge_base(self, document_id: str, category_id: str,
                                      tags: List[str] = None):
        """添加文档到知识库"""
        # 关联文档和分类
        self.storage.cur.execute("""
            INSERT INTO knowledge_documents (
                document_id, category_id
            ) VALUES (%s, %s)
            ON CONFLICT (document_id) DO UPDATE SET
                category_id = EXCLUDED.category_id
        """, (document_id, category_id))

        # 添加标签
        if tags:
            for tag in tags:
                self.storage.cur.execute("""
                    INSERT INTO document_tags (
                        document_id, tag_name
                    ) VALUES (%s, %s)
                    ON CONFLICT (document_id, tag_name) DO NOTHING
                """, (document_id, tag))

        self.storage.conn.commit()

    def search_knowledge(self, query: str, category_id: str = None,
                        tags: List[str] = None, limit: int = 20) -> List[Dict]:
        """搜索知识"""
        # 全文搜索
        results = self.storage.search_documents_fulltext(query, limit)

        # 过滤分类
        if category_id:
            results = [r for r in results if self._document_in_category(r['document_id'], category_id)]

        # 过滤标签
        if tags:
            filtered_results = []
            for result in results:
                doc_tags = self._get_document_tags(result['document_id'])
                if any(tag in doc_tags for tag in tags):
                    filtered_results.append(result)
            results = filtered_results

        return results

    def recommend_knowledge(self, document_id: str, limit: int = 5) -> List[Dict]:
        """推荐相关知识"""
        # 获取文档的标签和分类
        doc_tags = self._get_document_tags(document_id)
        doc_category = self._get_document_category(document_id)

        # 查找相同标签或分类的文档
        recommendations = []

        if doc_tags:
            for tag in doc_tags:
                similar_docs = self.search_knowledge("", tags=[tag], limit=limit)
                for doc in similar_docs:
                    if doc['document_id'] != document_id:
                        recommendations.append(doc)

        if doc_category:
            category_docs = self._get_documents_in_category(doc_category, limit)
            for doc in category_docs:
                if doc['document_id'] != document_id:
                    recommendations.append(doc)

        # 去重并按相关性排序
        unique_recommendations = {}
        for rec in recommendations:
            doc_id = rec['document_id']
            if doc_id not in unique_recommendations:
                unique_recommendations[doc_id] = rec

        return list(unique_recommendations.values())[:limit]

    def _document_in_category(self, document_id: str, category_id: str) -> bool:
        """检查文档是否在指定分类"""
        self.storage.cur.execute("""
            SELECT COUNT(*) FROM knowledge_documents
            WHERE document_id = %s AND category_id = %s
        """, (document_id, category_id))
        return self.storage.cur.fetchone()[0] > 0

    def _get_document_tags(self, document_id: str) -> List[str]:
        """获取文档标签"""
        self.storage.cur.execute("""
            SELECT tag_name FROM document_tags
            WHERE document_id = %s
        """, (document_id,))
        return [row[0] for row in self.storage.cur.fetchall()]

    def _get_document_category(self, document_id: str) -> Optional[str]:
        """获取文档分类"""
        self.storage.cur.execute("""
            SELECT category_id FROM knowledge_documents
            WHERE document_id = %s
        """, (document_id,))
        result = self.storage.cur.fetchone()
        return result[0] if result else None

    def _get_documents_in_category(self, category_id: str, limit: int) -> List[Dict]:
        """获取分类下的文档"""
        self.storage.cur.execute("""
            SELECT d.document_id, d.document_title, d.document_type
            FROM documents d
            JOIN knowledge_documents kd ON d.document_id = kd.document_id
            WHERE kd.category_id = %s
            ORDER BY d.created_at DESC
            LIMIT %s
        """, (category_id, limit))

        return [
            {
                "document_id": row[0],
                "document_title": row[1],
                "document_type": row[2]
            }
            for row in self.storage.cur.fetchall()
        ]

def knowledge_base_example():
    """知识库管理示例"""
    storage = OAStorage("postgresql://user:pass@localhost/oa")
    kb_manager = KnowledgeBaseManager(storage)

    # 创建分类
    kb_manager.create_category("CAT001", "技术文档", None, "技术相关文档")
    kb_manager.create_category("CAT002", "业务流程", None, "业务流程文档")

    # 添加文档到知识库
    kb_manager.add_document_to_knowledge_base(
        "DOC001",
        "CAT001",
        ["Python", "数据库"]
    )

    # 搜索知识
    results = kb_manager.search_knowledge("Python", category_id="CAT001")
    print(f"Found {len(results)} documents")
    for result in results:
        print(f"  {result['document_title']}")

    # 推荐相关知识
    recommendations = kb_manager.recommend_knowledge("DOC001")
    print(f"\nRecommended documents: {len(recommendations)}")
    for rec in recommendations:
        print(f"  {rec['document_title']}")

    storage.close()

if __name__ == "__main__":
    knowledge_base_example()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

---

## 12. 案例11：文档智能分析系统

### 12.1 场景描述

**业务背景**：
文档智能分析系统使用AI技术分析文档内容，
提取关键信息、生成摘要、识别主题，提高文档处理效率。

**技术挑战**：

- 需要文档内容解析
- 需要AI文本分析
- 需要信息提取
- 需要摘要生成

**解决方案**：
使用OA_Schema定义文档分析结构，
使用AI模型进行文档分析，
使用OAStorage存储分析结果。

### 12.2 Schema定义

**文档智能分析Schema**：

```dsl
schema DocumentIntelligentAnalysis {
  analysis_session_id: String @value("DOC-ANALYSIS-20250121-001") @required
  document_id: String @value("DOC-001") @required
  analysis_time: DateTime @value("2025-01-21T10:00:00") @required

  document_info: {
    title: String @value("项目计划书")
    document_type: Enum { Word } @value(Word)
    word_count: Integer @value(5000)
    page_count: Integer @value(10)
  } @required

  ai_analysis: {
    summary: String @value("本文档描述了2025年Q1项目计划...")
    key_topics: [String] @value(["项目管理", "资源分配", "时间规划"])
    key_entities: [
      {
        entity_type: String @value("Person")
        entity_name: String @value("张三")
        mention_count: Integer @value(5)
      }
    ]
    sentiment: Enum { Neutral } @value(Neutral)
    language: String @value("zh-CN")
  } @required

  extracted_information: {
    dates: [Date] @value(["2025-01-21", "2025-03-31"])
    deadlines: [Date] @value(["2025-03-31"])
    budget_info: {
      total_budget: Decimal @value(1000000.0)
      currency: String @value("RMB")
    }
    action_items: [
      {
        item: String @value("完成需求分析")
        assignee: String @value("张三")
        due_date: Date @value("2025-02-15")
      }
    ]
  } @required
} @standard("ODF/OOXML")
```

### 12.3 实现代码

```python
from oa_storage import OAStorage
from datetime import datetime

def document_intelligent_analysis():
    """文档智能分析系统示例"""
    storage = OAStorage("postgresql://user:password@localhost/oa_db")

    # 文档信息
    document_info = {
        "document_id": "DOC-001",
        "title": "项目计划书",
        "document_type": "Word",
        "word_count": 5000,
        "page_count": 10
    }

    # AI文档分析（简化示例）
    def analyze_document(document_id, content):
        """AI文档分析"""
        # 生成摘要（简化示例）
        summary = "本文档描述了2025年Q1项目计划，包括项目目标、资源分配、时间规划等内容。"

        # 提取关键主题
        key_topics = ["项目管理", "资源分配", "时间规划"]

        # 提取关键实体
        key_entities = [
            {
                "entity_type": "Person",
                "entity_name": "张三",
                "mention_count": 5
            }
        ]

        # 情感分析
        sentiment = "Neutral"

        # 提取信息
        extracted_info = {
            "dates": ["2025-01-21", "2025-03-31"],
            "deadlines": ["2025-03-31"],
            "budget_info": {
                "total_budget": 1000000.0,
                "currency": "RMB"
            },
            "action_items": [
                {
                    "item": "完成需求分析",
                    "assignee": "张三",
                    "due_date": "2025-02-15"
                }
            ]
        }

        return {
            "summary": summary,
            "key_topics": key_topics,
            "key_entities": key_entities,
            "sentiment": sentiment,
            "language": "zh-CN",
            "extracted_information": extracted_info
        }

    # 执行文档分析
    content = "..."  # 文档内容
    ai_analysis = analyze_document(document_info["document_id"], content)

    # 存储分析结果
    analysis_data = {
        "analysis_session_id": "DOC-ANALYSIS-20250121-001",
        "document_id": document_info["document_id"],
        "analysis_time": datetime.now(),
        "document_title": document_info["title"],
        "document_type": document_info["document_type"],
        "word_count": document_info["word_count"],
        "summary": ai_analysis["summary"],
        "key_topics": ai_analysis["key_topics"],
        "key_entities": ai_analysis["key_entities"],
        "sentiment": ai_analysis["sentiment"],
        "extracted_dates": ai_analysis["extracted_information"]["dates"],
        "extracted_deadlines": ai_analysis["extracted_information"]["deadlines"],
        "budget_total": ai_analysis["extracted_information"]["budget_info"]["total_budget"],
        "action_items": ai_analysis["extracted_information"]["action_items"]
    }

    # 存储到数据库
    analysis_id = storage.store_document_analysis(analysis_data)
    print(f"Document analysis stored: {analysis_id}")

    print(f"\nDocument Intelligent Analysis Results:")
    print(f"  Document: {document_info['title']}")
    print(f"  Summary: {ai_analysis['summary'][:100]}...")
    print(f"  Key topics: {', '.join(ai_analysis['key_topics'])}")
    print(f"  Key entities: {len(ai_analysis['key_entities'])}")
    print(f"  Action items: {len(ai_analysis['extracted_information']['action_items'])}")

    return analysis_data

if __name__ == "__main__":
    document_intelligent_analysis()
```

---

## 13. 案例12：流程自动化系统

### 13.1 场景描述

**业务背景**：
流程自动化系统自动执行重复性业务流程，
例如自动审批、自动通知、自动数据同步等。

**技术挑战**：

- 需要流程规则定义
- 需要条件判断
- 需要自动执行
- 需要执行监控

**解决方案**：
使用OA_Schema定义流程自动化规则，
使用BPMN引擎执行自动化流程，
使用OAStorage存储自动化数据。

### 13.2 Schema定义

**流程自动化Schema**：

```dsl
schema ProcessAutomation {
  automation_id: String @value("AUTO-PROC-20250121-001") @required
  automation_name: String @value("自动审批流程") @required
  process_id: String @value("PROC-001") @required

  automation_rules: [
    {
      rule_id: String @value("RULE-001")
      rule_name: String @value("金额自动审批")
      condition: {
        field: String @value("amount")
        operator: Enum { LessThan } @value(LessThan)
        value: Decimal @value(10000.0)
      }
      action: {
        action_type: Enum { AutoApprove } @value(AutoApprove)
        approver: String @value("SYSTEM")
        notification: Boolean @value(true)
      }
    }
  ] @required

  automation_status: {
    status: Enum { Active } @value(Active)
    execution_count: Integer @value(50)
    success_rate: Decimal @value(0.98) @range(0.0, 1.0)
    last_executed: DateTime @value("2025-01-21T10:00:00")
  } @required
} @standard("BPMN")
```

### 13.3 实现代码

```python
from oa_storage import OAStorage
from datetime import datetime

def process_automation_system():
    """流程自动化系统示例"""
    storage = OAStorage("postgresql://user:password@localhost/oa_db")

    # 自动化规则
    automation_rules = [
        {
            "rule_id": "RULE-001",
            "rule_name": "金额自动审批",
            "condition": {
                "field": "amount",
                "operator": "LessThan",
                "value": 10000.0
            },
            "action": {
                "action_type": "AutoApprove",
                "approver": "SYSTEM",
                "notification": True
            }
        }
    ]

    # 检查自动化条件
    def check_automation_condition(rule, process_data):
        """检查自动化条件"""
        field_value = process_data.get(rule["condition"]["field"])
        operator = rule["condition"]["operator"]
        threshold = rule["condition"]["value"]

        if operator == "LessThan":
            return field_value < threshold
        elif operator == "GreaterThan":
            return field_value > threshold
        elif operator == "Equals":
            return field_value == threshold
        return False

    # 执行自动化动作
    def execute_automation_action(rule, process_id):
        """执行自动化动作"""
        action_type = rule["action"]["action_type"]

        if action_type == "AutoApprove":
            # 自动审批
            storage.approve_process(process_id, rule["action"]["approver"])

            # 发送通知
            if rule["action"]["notification"]:
                storage.send_notification(process_id, "流程已自动审批")

            return True
        return False

    # 处理流程
    process_data = {
        "process_id": "PROC-001",
        "amount": 5000.0,
        "applicant": "USER-001"
    }

    # 检查并执行自动化
    for rule in automation_rules:
        if check_automation_condition(rule, process_data):
            print(f"Automation rule triggered: {rule['rule_name']}")
            result = execute_automation_action(rule, process_data["process_id"])

            if result:
                # 记录自动化执行
                automation_data = {
                    "automation_id": "AUTO-PROC-20250121-001",
                    "automation_name": "自动审批流程",
                    "process_id": process_data["process_id"],
                    "rule_id": rule["rule_id"],
                    "execution_time": datetime.now(),
                    "status": "Success"
                }

                storage.store_automation_event(automation_data)
                print(f"Automation executed successfully")

    return automation_data

if __name__ == "__main__":
    process_automation_system()
```

---

## 14. 案例13：协作效率分析系统

### 14.1 场景描述

**业务背景**：
协作效率分析系统分析团队协作数据，
评估协作效率，识别协作瓶颈，提供优化建议。

**技术挑战**：

- 需要协作数据收集
- 需要效率指标计算
- 需要瓶颈识别
- 需要优化建议生成

**解决方案**：
使用OA_Schema整合协作数据，
使用数据分析算法进行效率分析，
使用OAStorage存储分析结果。

### 14.2 Schema定义

**协作效率分析Schema**：

```dsl
schema CollaborationEfficiencyAnalysis {
  analysis_session_id: String @value("COLLAB-ANALYSIS-20250121-001") @required
  team_id: String @value("TEAM-001") @required
  analysis_period: {
    start_date: Date @value("2025-01-01")
    end_date: Date @value("2025-01-21")
  } @required

  collaboration_metrics: {
    total_collaborations: Integer @value(150)
    average_response_time: Decimal @value(2.5) @unit("hours")
    collaboration_frequency: Decimal @value(7.1) @unit("per day")
    document_sharing_count: Integer @value(80)
    meeting_count: Integer @value(25)
    average_meeting_duration: Decimal @value(45.0) @unit("minutes")
  } @required

  efficiency_analysis: {
    overall_efficiency_score: Decimal @value(0.78) @range(0.0, 1.0)
    efficiency_level: Enum { Good } @value(Good)
    bottlenecks: [
      {
        bottleneck_type: String @value("Slow response time")
        severity: Enum { Medium } @value(Medium)
        impact: String @value("影响任务完成速度")
      }
    ]
    recommendations: [
      {
        recommendation: String @value("优化响应时间")
        priority: Enum { High } @value(High)
        expected_improvement: Decimal @value(0.15)
      }
    ]
  } @required
} @standard("BPMN")
```

### 14.3 实现代码

```python
from oa_storage import OAStorage
from datetime import datetime, date, timedelta

def collaboration_efficiency_analysis():
    """协作效率分析系统示例"""
    storage = OAStorage("postgresql://user:password@localhost/oa_db")

    # 协作指标数据
    team_id = "TEAM-001"
    start_date = date(2025, 1, 1)
    end_date = date(2025, 1, 21)

    collaboration_metrics = {
        "total_collaborations": 150,
        "average_response_time": 2.5,  # hours
        "collaboration_frequency": 7.1,  # per day
        "document_sharing_count": 80,
        "meeting_count": 25,
        "average_meeting_duration": 45.0  # minutes
    }

    # 效率分析算法
    def analyze_efficiency(metrics):
        """分析协作效率"""
        efficiency_score = 0.0
        bottlenecks = []
        recommendations = []

        # 响应时间评分
        if metrics["average_response_time"] <= 1.0:
            response_score = 1.0
        elif metrics["average_response_time"] <= 2.0:
            response_score = 0.8
        else:
            response_score = 0.6
            bottlenecks.append({
                "bottleneck_type": "Slow response time",
                "severity": "Medium",
                "impact": "影响任务完成速度"
            })
            recommendations.append({
                "recommendation": "优化响应时间",
                "priority": "High",
                "expected_improvement": 0.15
            })

        # 协作频率评分
        if metrics["collaboration_frequency"] >= 10:
            frequency_score = 1.0
        elif metrics["collaboration_frequency"] >= 5:
            frequency_score = 0.8
        else:
            frequency_score = 0.6

        # 会议效率评分
        if metrics["average_meeting_duration"] <= 30:
            meeting_score = 1.0
        elif metrics["average_meeting_duration"] <= 60:
            meeting_score = 0.8
        else:
            meeting_score = 0.6
            bottlenecks.append({
                "bottleneck_type": "Long meeting duration",
                "severity": "Low",
                "impact": "影响时间利用效率"
            })
            recommendations.append({
                "recommendation": "优化会议时长",
                "priority": "Medium",
                "expected_improvement": 0.10
            })

        # 综合效率评分
        efficiency_score = (
            response_score * 0.4 +
            frequency_score * 0.3 +
            meeting_score * 0.3
        )

        # 确定效率等级
        if efficiency_score >= 0.8:
            efficiency_level = "Excellent"
        elif efficiency_score >= 0.7:
            efficiency_level = "Good"
        elif efficiency_score >= 0.6:
            efficiency_level = "Fair"
        else:
            efficiency_level = "Poor"

        return {
            "overall_efficiency_score": efficiency_score,
            "efficiency_level": efficiency_level,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations
        }

    # 执行效率分析
    efficiency_analysis = analyze_efficiency(collaboration_metrics)

    # 存储分析结果
    analysis_data = {
        "analysis_session_id": "COLLAB-ANALYSIS-20250121-001",
        "team_id": team_id,
        "analysis_start_date": start_date,
        "analysis_end_date": end_date,
        "total_collaborations": collaboration_metrics["total_collaborations"],
        "average_response_time": collaboration_metrics["average_response_time"],
        "collaboration_frequency": collaboration_metrics["collaboration_frequency"],
        "document_sharing_count": collaboration_metrics["document_sharing_count"],
        "meeting_count": collaboration_metrics["meeting_count"],
        "average_meeting_duration": collaboration_metrics["average_meeting_duration"],
        "overall_efficiency_score": efficiency_analysis["overall_efficiency_score"],
        "efficiency_level": efficiency_analysis["efficiency_level"],
        "bottlenecks": efficiency_analysis["bottlenecks"],
        "recommendations": efficiency_analysis["recommendations"]
    }

    # 存储到数据库
    analysis_id = storage.store_collaboration_analysis(analysis_data)
    print(f"Collaboration efficiency analysis stored: {analysis_id}")

    print(f"\nCollaboration Efficiency Analysis:")
    print(f"  Team: {team_id}")
    print(f"  Overall efficiency score: {efficiency_analysis['overall_efficiency_score']:.2f}")
    print(f"  Efficiency level: {efficiency_analysis['efficiency_level']}")
    print(f"  Bottlenecks: {len(efficiency_analysis['bottlenecks'])}")
    print(f"  Recommendations: {len(efficiency_analysis['recommendations'])}")

    return analysis_data

if __name__ == "__main__":
    collaboration_efficiency_analysis()
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
