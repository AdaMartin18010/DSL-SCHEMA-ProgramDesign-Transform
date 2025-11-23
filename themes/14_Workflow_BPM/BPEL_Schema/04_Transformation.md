# BPEL Schema转换体系

## 📑 目录

- [BPEL Schema转换体系](#bpel-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. BPMN到BPEL转换](#2-bpmn到bpel转换)
  - [3. BPEL到WSDL生成](#3-bpel到wsdl生成)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. BPEL数据存储与分析](#6-bpel数据存储与分析)
    - [6.1 PostgreSQL BPEL数据存储](#61-postgresql-bpel数据存储)
    - [6.2 BPEL数据分析查询](#62-bpel数据分析查询)

---

## 1. 转换体系概述

BPEL Schema转换体系支持BPMN到BPEL转换、
BPEL到WSDL生成，以及流程执行数据存储。

### 1.1 转换目标

1. **BPMN到BPEL转换**：业务流程模型到可执行流程
2. **BPEL到WSDL生成**：BPEL流程到Web服务描述
3. **流程到数据库转换**：BPEL流程到PostgreSQL存储

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

    # 转换合作伙伴链接
    for participant in bpmn_process.participants:
        partner_link = PartnerLink()
        partner_link.name = participant.id
        partner_link.partner_link_type = f"{participant.id}Type"
        bpel.partner_links.append(partner_link)

    # 转换流程变量
    for var in bpmn_process.variables:
        bpel_var = Variable()
        bpel_var.name = var.name
        bpel_var.message_type = var.type
        bpel.variables.append(bpel_var)

    # 转换流程活动
    bpel.activities = convert_flow_elements(bpmn_process.elements)

    return bpel

def convert_flow_elements(elements: List[FlowElement]) -> Activity:
    """转换流程元素为BPEL活动"""
    if len(elements) == 1:
        return convert_single_element(elements[0])

    # 多个元素转换为序列
    sequence = Sequence()
    for element in elements:
        sequence.activities.append(convert_single_element(element))
    return sequence

def convert_single_element(element: FlowElement) -> Activity:
    """转换单个流程元素"""
    if isinstance(element, UserTask):
        # 用户任务转换为接收和回复
        receive = Receive()
        receive.partner_link = element.assignee
        receive.operation = f"{element.id}Operation"
        receive.variable = f"{element.id}Input"

        reply = Reply()
        reply.partner_link = element.assignee
        reply.operation = f"{element.id}Operation"
        reply.variable = f"{element.id}Output"

        sequence = Sequence()
        sequence.activities.append(receive)
        sequence.activities.append(reply)
        return sequence

    elif isinstance(element, ServiceTask):
        # 服务任务转换为调用
        invoke = Invoke()
        invoke.partner_link = element.implementation
        invoke.operation = element.operation_ref
        invoke.input_variable = f"{element.id}Input"
        invoke.output_variable = f"{element.id}Output"
        return invoke

    elif isinstance(element, ExclusiveGateway):
        # 排他网关转换为选择
        if_activity = If()
        if_activity.condition = element.sequence_flows[0].condition_expression
        if_activity.then = convert_flow_elements([element.sequence_flows[0].target_ref])
        if len(element.sequence_flows) > 1:
            if_activity.else_activity = convert_flow_elements([element.sequence_flows[1].target_ref])
        return if_activity

    elif isinstance(element, ParallelGateway):
        # 并行网关转换为流
        flow = Flow()
        for seq_flow in element.outgoing_flows:
            flow.activities.append(convert_flow_elements([seq_flow.target_ref]))
        return flow

    return Empty()
```

---

## 3. BPEL到WSDL生成

**生成规则**：

- BPEL流程 → WSDL定义
- BPEL合作伙伴链接 → WSDL端口类型
- BPEL操作 → WSDL操作

**生成示例**：

```python
def generate_wsdl_from_bpel(bpel_process: BPELProcess) -> WSDLDefinition:
    """从BPEL流程生成WSDL定义"""
    wsdl = WSDLDefinition()
    wsdl.target_namespace = bpel_process.target_namespace

    # 生成端口类型
    for partner_link in bpel_process.partner_links:
        port_type = PortType()
        port_type.name = f"{partner_link.name}PortType"

        # 查找相关的接收和回复活动
        for activity in find_activities(bpel_process.activities):
            if isinstance(activity, Receive) and activity.partner_link == partner_link.name:
                operation = Operation()
                operation.name = activity.operation
                operation.input = Message()
                operation.input.message = activity.variable
                port_type.operations.append(operation)

            elif isinstance(activity, Reply) and activity.partner_link == partner_link.name:
                # 查找对应的操作并添加输出
                for op in port_type.operations:
                    if op.name == activity.operation:
                        op.output = Message()
                        op.output.message = activity.variable

        wsdl.port_types.append(port_type)

    return wsdl
```

---

## 4. 转换工具

- **Apache ODE**：BPEL执行引擎和转换工具
- **ActiveVOS**：BPEL设计和转换工具
- **Oracle BPEL Process Manager**：Oracle BPEL平台
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的流程完整性、行为等价性和可执行性。

---

## 6. BPEL数据存储与分析

### 6.1 PostgreSQL BPEL数据存储

**BPEL数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class BPELStorage:
    """BPEL数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建BPEL数据表"""
        # 流程定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bpel_process_definitions (
                id SERIAL PRIMARY KEY,
                process_id VARCHAR(200) UNIQUE NOT NULL,
                process_name VARCHAR(200) NOT NULL,
                target_namespace VARCHAR(500),
                bpel_xml TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 流程实例表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bpel_process_instances (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(200) UNIQUE NOT NULL,
                process_id VARCHAR(200) NOT NULL,
                status VARCHAR(50) NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                variables JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 活动执行历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bpel_activity_execution (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(200) NOT NULL,
                activity_id VARCHAR(200) NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                input_data JSONB,
                output_data JSONB,
                fault_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 服务调用记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bpel_service_calls (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(200) NOT NULL,
                activity_id VARCHAR(200) NOT NULL,
                partner_link VARCHAR(200) NOT NULL,
                operation VARCHAR(200) NOT NULL,
                call_type VARCHAR(50) NOT NULL,
                request_data JSONB,
                response_data JSONB,
                duration_ms BIGINT,
                status VARCHAR(50),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 流程统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bpel_process_statistics (
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
            CREATE INDEX IF NOT EXISTS idx_bpel_instances_status
            ON bpel_process_instances(status, created_at DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_bpel_activity_instance
            ON bpel_activity_execution(instance_id, start_time DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_bpel_service_calls_partner
            ON bpel_service_calls(partner_link, operation, created_at DESC)
        """)

        self.conn.commit()

    def store_process_definition(self, process_id: str, process_name: str,
                                 bpel_xml: str, target_namespace: str = None,
                                 metadata: Dict = None):
        """存储流程定义"""
        self.cur.execute("""
            INSERT INTO bpel_process_definitions
            (process_id, process_name, target_namespace, bpel_xml, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (process_id) DO UPDATE
            SET process_name = EXCLUDED.process_name,
                target_namespace = EXCLUDED.target_namespace,
                bpel_xml = EXCLUDED.bpel_xml,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP
        """, (process_id, process_name, target_namespace, bpel_xml,
              json.dumps(metadata or {})))
        self.conn.commit()

    def record_service_call(self, instance_id: str, activity_id: str,
                           partner_link: str, operation: str,
                           call_type: str, request_data: Dict,
                           response_data: Dict = None, duration_ms: int = None,
                           status: str = "SUCCESS", error_message: str = None):
        """记录服务调用"""
        self.cur.execute("""
            INSERT INTO bpel_service_calls
            (instance_id, activity_id, partner_link, operation, call_type,
             request_data, response_data, duration_ms, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s)
        """, (instance_id, activity_id, partner_link, operation, call_type,
              json.dumps(request_data), json.dumps(response_data or {}),
              duration_ms, status, error_message))
        self.conn.commit()

    def calculate_process_statistics(self, process_id: str,
                                    time_window: datetime):
        """计算流程统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_instances,
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'RUNNING' THEN 1 END) as running,
                COUNT(CASE WHEN status = 'FAULTED' THEN 1 END) as faulted,
                AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration,
                MIN(EXTRACT(EPOCH FROM (end_time - start_time))) as min_duration,
                MAX(EXTRACT(EPOCH FROM (end_time - start_time))) as max_duration
            FROM bpel_process_instances
            WHERE process_id = %s AND created_at >= %s
        """, (process_id, time_window))

        stats = dict(zip([desc[0] for desc in self.cur.description],
                         self.cur.fetchone()))

        # 服务调用统计
        self.cur.execute("""
            SELECT
                partner_link,
                operation,
                COUNT(*) as call_count,
                AVG(duration_ms) as avg_duration_ms,
                COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as success_count,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_count
            FROM bpel_service_calls
            WHERE instance_id IN (
                SELECT instance_id FROM bpel_process_instances
                WHERE process_id = %s AND created_at >= %s
            )
            GROUP BY partner_link, operation
        """, (process_id, time_window))

        service_stats = []
        for row in self.cur.fetchall():
            service_stats.append({
                'partner_link': row[0],
                'operation': row[1],
                'call_count': row[2],
                'avg_duration_ms': row[3],
                'success_count': row[4],
                'failed_count': row[5]
            })

        stats['service_calls'] = service_stats

        # 存储统计信息
        self.cur.execute("""
            INSERT INTO bpel_process_statistics
            (process_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (process_id, statistic_type, time_window)
            DO UPDATE SET statistics = EXCLUDED.statistics
        """, (process_id, "performance", time_window, json.dumps(stats)))
        self.conn.commit()

        return stats
```

### 6.2 BPEL数据分析查询

**查询示例**：

```python
# 查询流程实例
storage.cur.execute("""
    SELECT instance_id, status, start_time, end_time
    FROM bpel_process_instances
    WHERE process_id = %s AND created_at >= %s
    ORDER BY created_at DESC
""", (process_id, start_time))

# 查询服务调用统计
storage.cur.execute("""
    SELECT partner_link, operation, COUNT(*) as call_count,
           AVG(duration_ms) as avg_duration
    FROM bpel_service_calls
    WHERE created_at >= %s
    GROUP BY partner_link, operation
    ORDER BY call_count DESC
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
