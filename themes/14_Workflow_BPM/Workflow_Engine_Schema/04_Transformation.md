# Workflow Engine Schema转换体系

## 📑 目录

- [Workflow Engine Schema转换体系](#workflow-engine-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. BPMN到工作流引擎转换](#2-bpmn到工作流引擎转换)
  - [3. 工作流引擎到XPDL转换](#3-工作流引擎到xpdl转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. Workflow Engine数据存储与分析](#6-workflow-engine数据存储与分析)
    - [6.1 PostgreSQL Workflow Engine数据存储](#61-postgresql-workflow-engine数据存储)
    - [6.2 Workflow Engine数据分析查询](#62-workflow-engine数据分析查询)

---

## 1. 转换体系概述

Workflow Engine Schema转换体系支持BPMN到
工作流引擎转换、工作流引擎到XPDL转换，以及
工作流引擎数据存储。

### 1.1 转换目标

1. **BPMN到工作流引擎转换**：BPMN流程定义到工作流引擎格式
2. **工作流引擎到XPDL转换**：工作流引擎定义到XPDL格式
3. **流程到数据库转换**：工作流引擎数据到PostgreSQL存储

---

## 2. BPMN到工作流引擎转换

**转换规则**：

- BPMN流程 → 工作流引擎流程定义
- BPMN任务 → 工作流引擎任务定义
- BPMN网关 → 工作流引擎网关定义

**转换示例**：

```python
def convert_bpmn_to_workflow_engine(bpmn_process: BPMNProcess) -> WorkflowDefinition:
    """将BPMN流程转换为工作流引擎定义"""
    workflow_def = WorkflowDefinition()

    # 转换流程基本信息
    workflow_def.process_definition.process_id = bpmn_process.id
    workflow_def.process_definition.process_name = bpmn_process.name
    workflow_def.process_definition.process_key = bpmn_process.id
    workflow_def.process_definition.version = 1

    # 转换流程元素
    for element in bpmn_process.elements:
        process_element = ProcessElement()
        process_element.element_id = element.id
        process_element.element_name = element.name
        process_element.element_type = convert_element_type(element.type)
        workflow_def.process_elements.append(process_element)

    # 转换流程变量
    for var_name, var_def in bpmn_process.variables.items():
        process_var = ProcessVariable()
        process_var.variable_name = var_name
        process_var.variable_type = var_def.type
        process_var.default_value = var_def.default_value
        workflow_def.process_variables.append(process_var)

    return workflow_def
```

---

## 3. 工作流引擎到XPDL转换

**转换规则**：

- 工作流引擎流程定义 → XPDL工作流
- 工作流引擎任务 → XPDL活动
- 工作流引擎网关 → XPDL路由

**转换示例**：

```python
def convert_workflow_engine_to_xpdl(workflow_def: WorkflowDefinition) -> XPDLWorkflow:
    """将工作流引擎定义转换为XPDL工作流"""
    xpdl = XPDLWorkflow()

    # 转换工作流基本信息
    xpdl.workflow_process.id = workflow_def.process_definition.process_id
    xpdl.workflow_process.name = workflow_def.process_definition.process_name

    # 转换活动
    for element in workflow_def.process_elements:
        if element.element_type in ['UserTask', 'ServiceTask']:
            activity = XPDLActivity()
            activity.id = element.element_id
            activity.name = element.element_name
            activity.activity_type = convert_activity_type(element.element_type)
            xpdl.workflow_process.activities.append(activity)

    # 转换转移
    for element in workflow_def.process_elements:
        if element.element_type == 'SequenceFlow':
            transition = XPDLTransition()
            transition.id = element.element_id
            transition.from_activity = element.source_ref
            transition.to_activity = element.target_ref
            xpdl.workflow_process.transitions.append(transition)

    return xpdl
```

---

## 4. 转换工具

- **Activiti Modeler**：Activiti流程建模和转换工具
- **Camunda Modeler**：Camunda流程建模和转换工具
- **jBPM Designer**：jBPM流程设计和转换工具
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的流程完整性、行为等价性和可执行性。

---

## 6. Workflow Engine数据存储与分析

### 6.1 PostgreSQL Workflow Engine数据存储

**Workflow Engine数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

class WorkflowEngineStorage:
    """Workflow Engine数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建Workflow Engine数据表"""
        # 流程定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_process_definitions (
                id VARCHAR(64) PRIMARY KEY,
                process_id VARCHAR(255) NOT NULL,
                process_name VARCHAR(255) NOT NULL,
                process_key VARCHAR(255) NOT NULL,
                version INTEGER NOT NULL,
                category VARCHAR(255),
                deployment_id VARCHAR(64) NOT NULL,
                resource_name VARCHAR(4000),
                diagram_resource_name VARCHAR(4000),
                is_suspended BOOLEAN DEFAULT FALSE,
                tenant_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(process_key, version)
            )
        """)

        # 流程实例表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_process_instances (
                id VARCHAR(64) PRIMARY KEY,
                process_definition_id VARCHAR(64) NOT NULL,
                process_definition_key VARCHAR(255) NOT NULL,
                business_key VARCHAR(255),
                parent_instance_id VARCHAR(64),
                root_process_instance_id VARCHAR(64),
                status VARCHAR(50) NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                start_user_id VARCHAR(255),
                start_activity_id VARCHAR(255),
                delete_reason VARCHAR(4000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 执行状态表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_execution_states (
                id VARCHAR(64) PRIMARY KEY,
                process_instance_id VARCHAR(64) NOT NULL,
                parent_execution_id VARCHAR(64),
                activity_id VARCHAR(255),
                activity_name VARCHAR(255),
                is_active BOOLEAN NOT NULL,
                is_concurrent BOOLEAN DEFAULT FALSE,
                is_scope BOOLEAN DEFAULT FALSE,
                suspension_state INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 任务实例表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_task_instances (
                id VARCHAR(64) PRIMARY KEY,
                process_instance_id VARCHAR(64) NOT NULL,
                execution_id VARCHAR(64),
                process_definition_id VARCHAR(64),
                process_definition_key VARCHAR(255),
                task_definition_key VARCHAR(255),
                name VARCHAR(255),
                assignee VARCHAR(255),
                owner VARCHAR(255),
                delegation_state VARCHAR(20),
                priority INTEGER DEFAULT 50,
                create_time TIMESTAMP NOT NULL,
                due_date TIMESTAMP,
                category VARCHAR(255),
                suspension_state INTEGER DEFAULT 1,
                tenant_id VARCHAR(255),
                form_key VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 执行历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_execution_history (
                id VARCHAR(64) PRIMARY KEY,
                process_instance_id VARCHAR(64) NOT NULL,
                execution_id VARCHAR(64) NOT NULL,
                activity_instance_id VARCHAR(64),
                activity_id VARCHAR(255),
                activity_name VARCHAR(255),
                activity_type VARCHAR(50) NOT NULL,
                task_id VARCHAR(64),
                assignee VARCHAR(255),
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_ms BIGINT,
                delete_reason VARCHAR(4000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 执行变量表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_execution_variables (
                id VARCHAR(64) PRIMARY KEY,
                process_instance_id VARCHAR(64) NOT NULL,
                execution_id VARCHAR(64),
                task_id VARCHAR(64),
                variable_name VARCHAR(255) NOT NULL,
                variable_type VARCHAR(255),
                variable_value TEXT,
                byte_array_id VARCHAR(64),
                double_value NUMERIC(18, 2),
                long_value BIGINT,
                text_value TEXT,
                text_value2 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(process_instance_id, execution_id, task_id, variable_name)
            )
        """)

        # 任务调度表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_task_schedules (
                id SERIAL PRIMARY KEY,
                task_definition_key VARCHAR(255) NOT NULL,
                assignment_type VARCHAR(50) NOT NULL,
                assignee VARCHAR(255),
                candidate_users JSONB,
                candidate_groups JSONB,
                priority INTEGER DEFAULT 50,
                scheduling_strategy VARCHAR(50),
                max_concurrent_tasks INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Workflow Engine统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_engine_statistics (
                id SERIAL PRIMARY KEY,
                statistic_type VARCHAR(50) NOT NULL,
                process_definition_key VARCHAR(255),
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(statistic_type, process_definition_key, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_instances_status
            ON workflow_process_instances(status, start_time DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_instances_assignee
            ON workflow_task_instances(assignee, create_time DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_history_instance
            ON workflow_execution_history(process_instance_id, start_time DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_variables_instance
            ON workflow_execution_variables(process_instance_id, variable_name)
        """)

        self.conn.commit()

    def store_process_definition(self, process_id: str, process_name: str,
                                 process_key: str, version: int,
                                 deployment_id: str, resource_name: str,
                                 diagram_resource_name: str = None,
                                 category: str = None, tenant_id: str = None):
        """存储流程定义"""
        self.cur.execute("""
            INSERT INTO workflow_process_definitions
            (id, process_id, process_name, process_key, version, category,
             deployment_id, resource_name, diagram_resource_name, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (process_key, version) DO UPDATE
            SET process_name = EXCLUDED.process_name,
                deployment_id = EXCLUDED.deployment_id,
                resource_name = EXCLUDED.resource_name,
                diagram_resource_name = EXCLUDED.diagram_resource_name,
                updated_at = CURRENT_TIMESTAMP
        """, (process_id, process_id, process_name, process_key, version,
              category, deployment_id, resource_name, diagram_resource_name, tenant_id))
        self.conn.commit()

    def calculate_process_statistics(self, process_definition_key: str,
                                    time_window: datetime):
        """计算流程统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_instances,
                COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'Active' THEN 1 END) as active,
                COUNT(CASE WHEN status = 'Suspended' THEN 1 END) as suspended,
                AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration,
                MIN(EXTRACT(EPOCH FROM (end_time - start_time))) as min_duration,
                MAX(EXTRACT(EPOCH FROM (end_time - start_time))) as max_duration
            FROM workflow_process_instances
            WHERE process_definition_key = %s AND start_time >= %s
        """, (process_definition_key, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 任务统计
        self.cur.execute("""
            SELECT
                task_definition_key,
                COUNT(*) as task_count,
                AVG(EXTRACT(EPOCH FROM (updated_at - create_time))) as avg_processing_time,
                COUNT(CASE WHEN assignee IS NOT NULL THEN 1 END) as assigned_count
            FROM workflow_task_instances
            WHERE process_definition_key = %s AND create_time >= %s
            GROUP BY task_definition_key
        """, (process_definition_key, time_window))

        task_stats = []
        for row in self.cur.fetchall():
            task_stats.append({
                'task_definition_key': row[0],
                'task_count': row[1],
                'avg_processing_time': row[2],
                'assigned_count': row[3]
            })

        stats['task_statistics'] = task_stats

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO workflow_engine_statistics
            (statistic_type, process_definition_key, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (statistic_type, process_definition_key, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, ('process_performance', process_definition_key, time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 Workflow Engine数据分析查询

**查询示例**：

```python
# 查询流程实例
storage.cur.execute("""
    SELECT id, process_definition_key, status, start_time, end_time
    FROM workflow_process_instances
    WHERE process_definition_key = %s AND start_time >= %s
    ORDER BY start_time DESC
""", (process_definition_key, start_time))

# 查询任务分配统计
storage.cur.execute("""
    SELECT assignee, COUNT(*) as task_count,
           AVG(EXTRACT(EPOCH FROM (updated_at - create_time))) as avg_time
    FROM workflow_task_instances
    WHERE create_time >= %s AND assignee IS NOT NULL
    GROUP BY assignee
    ORDER BY task_count DESC
""", (start_time,))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
