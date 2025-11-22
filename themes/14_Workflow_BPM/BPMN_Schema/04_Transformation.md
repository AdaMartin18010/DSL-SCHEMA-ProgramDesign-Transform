# BPMN Schema转换体系

## 📑 目录

- [BPMN Schema转换体系](#bpmn-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. BPMN到BPEL转换](#2-bpmn到bpel转换)
  - [3. BPMN到XPDL转换](#3-bpmn到xpdl转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. BPMN数据存储与分析](#6-bpmn数据存储与分析)
    - [6.1 PostgreSQL BPMN数据存储](#61-postgresql-bpmn数据存储)
    - [6.2 BPMN数据分析查询](#62-bpmn数据分析查询)

---

## 1. 转换体系概述

BPMN Schema转换体系支持BPMN、BPEL、
XPDL之间的转换，以及流程执行数据存储。

### 1.1 转换目标

1. **BPMN到BPEL转换**：业务流程模型到可执行流程
2. **BPMN到XPDL转换**：BPMN到工作流定义语言
3. **流程到数据库转换**：BPMN流程到PostgreSQL存储

---

## 2. BPMN到BPEL转换

**转换规则**：

- BPMN流程 → BPEL流程
- BPMN任务 → BPEL活动
- BPMN网关 → BPEL控制流
- BPMN事件 → BPEL事件处理

**转换示例**：

```python
def convert_bpmn_to_bpel(bpmn_process: BPMNProcess) -> BPELProcess:
    """将BPMN流程转换为BPEL流程"""
    bpel = BPELProcess()

    # 转换流程基本信息
    bpel.name = bpmn_process.name
    bpel.target_namespace = bpmn_process.namespace

    # 转换流程变量
    for var in bpmn_process.variables:
        bpel.variables.append(convert_variable(var))

    # 转换流程元素
    bpel.sequence = convert_flow_elements(bpmn_process.elements)

    return bpel

def convert_flow_elements(elements: List[FlowElement]) -> Sequence:
    """转换流程元素为BPEL序列"""
    sequence = Sequence()

    for element in elements:
        if isinstance(element, Task):
            sequence.activities.append(convert_task(element))
        elif isinstance(element, Gateway):
            sequence.activities.append(convert_gateway(element))
        elif isinstance(element, Event):
            sequence.activities.append(convert_event(element))

    return sequence
```

---

## 3. BPMN到XPDL转换

**转换规则**：

- BPMN流程 → XPDL工作流
- BPMN任务 → XPDL活动
- BPMN网关 → XPDL路由
- BPMN事件 → XPDL事件

**转换示例**：

```python
def convert_bpmn_to_xpdl(bpmn_process: BPMNProcess) -> XPDLWorkflow:
    """将BPMN流程转换为XPDL工作流"""
    xpdl = XPDLWorkflow()

    # 转换工作流基本信息
    xpdl.workflow_process.id = bpmn_process.id
    xpdl.workflow_process.name = bpmn_process.name

    # 转换活动
    for element in bpmn_process.elements:
        if isinstance(element, Task):
            activity = XPDLActivity()
            activity.id = element.id
            activity.name = element.name
            activity.activity_type = convert_task_type(element.type)
            xpdl.workflow_process.activities.append(activity)

    # 转换转移
    for flow in bpmn_process.sequence_flows:
        transition = XPDLTransition()
        transition.id = flow.id
        transition.from_activity = flow.source_ref
        transition.to_activity = flow.target_ref
        xpdl.workflow_process.transitions.append(transition)

    return xpdl
```

---

## 4. 转换工具

- **Camunda Modeler**：BPMN建模和转换工具
- **Activiti Designer**：BPMN设计和转换工具
- **jBPM**：业务流程管理平台
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的流程完整性、行为等价性和可执行性。

---

## 6. BPMN数据存储与分析

### 6.1 PostgreSQL BPMN数据存储

**BPMN数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class BPMNStorage:
    """BPMN数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建BPMN数据表"""
        # 流程定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS process_definitions (
                id SERIAL PRIMARY KEY,
                process_id VARCHAR(200) UNIQUE NOT NULL,
                process_name VARCHAR(200) NOT NULL,
                version VARCHAR(50),
                bpmn_xml TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 流程实例表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS process_instances (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(200) UNIQUE NOT NULL,
                process_id VARCHAR(200) NOT NULL,
                business_key VARCHAR(200),
                status VARCHAR(50) NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                variables JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 任务实例表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS task_instances (
                id BIGSERIAL PRIMARY KEY,
                task_id VARCHAR(200) UNIQUE NOT NULL,
                instance_id VARCHAR(200) NOT NULL,
                task_name VARCHAR(200) NOT NULL,
                task_type VARCHAR(50) NOT NULL,
                assignee VARCHAR(200),
                candidate_users JSONB,
                candidate_groups JSONB,
                status VARCHAR(50) NOT NULL,
                due_date TIMESTAMP,
                priority INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # 流程执行历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(200) NOT NULL,
                element_id VARCHAR(200) NOT NULL,
                element_type VARCHAR(50) NOT NULL,
                action VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                duration_ms BIGINT,
                variables JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 流程统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS process_statistics (
                id SERIAL PRIMARY KEY,
                process_id VARCHAR(200) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(process_id, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_instances_status
            ON process_instances(status, created_at DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_instances_assignee
            ON task_instances(assignee, status)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_history_instance
            ON execution_history(instance_id, timestamp DESC)
        """)

        self.conn.commit()

    def store_process_definition(self, process_id: str, process_name: str,
                                 bpmn_xml: str, version: str = "1.0",
                                 metadata: Dict = None):
        """存储流程定义"""
        self.cur.execute("""
            INSERT INTO process_definitions
            (process_id, process_name, version, bpmn_xml, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (process_id) DO UPDATE
            SET process_name = EXCLUDED.process_name,
                version = EXCLUDED.version,
                bpmn_xml = EXCLUDED.bpmn_xml,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP
        """, (process_id, process_name, version, bpmn_xml,
              json.dumps(metadata or {})))
        self.conn.commit()

    def calculate_process_statistics(self, process_id: str,
                                    time_window: datetime):
        """计算流程统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_instances,
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'RUNNING' THEN 1 END) as running,
                COUNT(CASE WHEN status = 'SUSPENDED' THEN 1 END) as suspended,
                AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration,
                MIN(EXTRACT(EPOCH FROM (end_time - start_time))) as min_duration,
                MAX(EXTRACT(EPOCH FROM (end_time - start_time))) as max_duration
            FROM process_instances
            WHERE process_id = %s AND created_at >= %s
        """, (process_id, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO process_statistics
            (process_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (process_id, statistic_type, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, (process_id, "performance", time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 BPMN数据分析查询

**查询示例**：

```python
# 查询流程实例
storage.cur.execute("""
    SELECT instance_id, status, start_time, end_time
    FROM process_instances
    WHERE process_id = %s AND created_at >= %s
    ORDER BY created_at DESC
""", (process_id, start_time))

# 查询任务分配统计
storage.cur.execute("""
    SELECT assignee, COUNT(*) as task_count
    FROM task_instances
    WHERE status = 'COMPLETED' AND completed_at >= %s
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
