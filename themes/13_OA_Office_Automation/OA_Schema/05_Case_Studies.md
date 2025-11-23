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

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
