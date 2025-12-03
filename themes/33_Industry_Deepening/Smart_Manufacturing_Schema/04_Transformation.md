# 智能制造Schema转换体系

## 📑 目录

- [智能制造Schema转换体系](#智能制造schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. OPC UA转换](#3-opc-ua转换)
  - [4. MES转换](#4-mes转换)
  - [5. ERP转换](#5-erp转换)
  - [6. PostgreSQL存储](#6-postgresql存储)
  - [7. 转换工具](#7-转换工具)
  - [8. 转换验证](#8-转换验证)

---

## 1. 转换体系概述

智能制造Schema转换体系支持**智能制造数据到各种格式的转换**，包括OPC UA、MES、ERP、PostgreSQL等格式。

**转换目标**：

- OPC UA格式
- MES系统格式
- ERP系统格式
- PostgreSQL数据库
- JSON格式

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 | 推荐工具 |
|---------|--------|----------|------------|----------|------------|----------|
| **Smart_Manufacturing → OPC UA** | Smart_Manufacturing_Schema | OPC UA NodeSet | ⭐⭐⭐ | ✅ 良好 | 高 | OPC UA SDK |
| **Smart_Manufacturing → MES** | Smart_Manufacturing_Schema | MES Format | ⭐⭐⭐⭐ | ✅ 良好 | 高 | MES API |
| **Smart_Manufacturing → ERP** | Smart_Manufacturing_Schema | ERP Format | ⭐⭐⭐⭐ | ✅ 良好 | 高 | ERP API |
| **Smart_Manufacturing → PostgreSQL** | Smart_Manufacturing_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 | PostgreSQL转换器 |
| **Smart_Manufacturing → JSON** | Smart_Manufacturing_Schema | JSON Schema | ⭐⭐ | ✅ 良好 | 高 | JSON转换器 |

---

## 3. OPC UA转换

### 3.1 Smart_Manufacturing → OPC UA转换

**转换函数**：

```text
to_opcua: Industry_4_0_Schema → OPC_UA_NodeSet
```

**转换规则**：

```text
to_opcua(schema) =
  create_device_nodes(schema.devices) +
  create_data_nodes(schema.data) +
  create_method_nodes(schema.intelligence)
```

**转换示例**：

**输入（Smart_Manufacturing_Schema）**：

```dsl
device CNC_Machine {
  device_id: "CNC_001"
  device_status: {
    operational: true
    performance: { oee: 0.85, efficiency: 0.92 }
  }
  communication: {
    protocol_type: OPC_UA
    ip_address: "192.168.1.100"
  }
}
```

**输出（OPC UA NodeSet XML）**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<UANodeSet xmlns="http://opcfoundation.org/UA/2011/03/UANodeSet.xsd">
  <Aliases>
    <Alias Alias="Boolean">i=1</Alias>
    <Alias Alias="Float">i=10</Alias>
  </Aliases>
  <UANode NodeId="ns=2;s=CNC_001" BrowseName="CNC_001">
    <DisplayName>CNC Machine 001</DisplayName>
    <References>
      <Reference ReferenceType="HasTypeDefinition">i=58</Reference>
      <Reference ReferenceType="Organizes" IsForward="false">i=85</Reference>
    </References>
  </UANode>
  <UAVariable NodeId="ns=2;s=CNC_001.Operational"
              BrowseName="Operational"
              DataType="Boolean"
              ParentNodeId="ns=2;s=CNC_001">
    <DisplayName>Operational Status</DisplayName>
    <Value>
      <uax:Boolean>true</uax:Boolean>
    </Value>
  </UAVariable>
  <UAVariable NodeId="ns=2;s=CNC_001.OEE"
              BrowseName="OEE"
              DataType="Float"
              ParentNodeId="ns=2;s=CNC_001">
    <DisplayName>Overall Equipment Effectiveness</DisplayName>
    <Value>
      <uax:Float>0.85</uax:Float>
    </Value>
  </UAVariable>
</UANodeSet>
```

**Python实现**：

```python
from opcua import ua, Server

class SmartManufacturingToOPCUA:
    """智能制造到OPC UA转换器"""

    def __init__(self):
        self.server = Server()
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840")
        self.namespace = self.server.register_namespace("SmartManufacturing")

    def convert_device(self, device: ManufacturingDevice):
        """转换设备到OPC UA节点"""
        # 创建设备对象节点
        device_node = self.server.get_objects_node().add_object(
            ua.NodeId(device.device_id, self.namespace),
            device.device_id
        )

        # 添加状态变量
        operational_var = device_node.add_variable(
            ua.NodeId(f"{device.device_id}.Operational", self.namespace),
            "Operational",
            device.device_status.operational
        )
        operational_var.set_writable()

        # 添加OEE变量
        oee_var = device_node.add_variable(
            ua.NodeId(f"{device.device_id}.OEE", self.namespace),
            "OEE",
            device.device_status.performance.oee
        )
        oee_var.set_writable()

        return device_node
```

---

## 4. MES转换

### 4.1 Smart_Manufacturing → MES转换

**转换函数**：

```text
to_mes: Digital_Factory_Schema → MES_Format
```

**转换规则**：

```text
to_mes(schema) =
  convert_production_plan(schema.production_plan) +
  convert_quality_control(schema.quality_control) +
  convert_resource_allocation(schema.resource_allocation)
```

**转换示例**：

**输入（Digital_Factory_Schema）**：

```dsl
production_plan Production_Plan {
  plan_id: "PLAN_001"
  production_schedule: {
    schedule_items: [
      {
        order_id: "ORDER_001"
        product_id: "PROD_001"
        quantity: 1000
        start_time: "2024-01-22T08:00:00Z"
        end_time: "2024-01-22T16:00:00Z"
        assigned_line: "LINE_001"
      }
    ]
  }
}
```

**输出（MES API调用）**：

```python
import requests

def to_mes(production_plan: ProductionPlan) -> dict:
    """转换为MES格式"""
    mes_payload = {
        "plan_id": production_plan.plan_id,
        "schedule": [
            {
                "order_id": item.order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "start_time": item.start_time.isoformat(),
                "end_time": item.end_time.isoformat(),
                "production_line": item.assigned_line
            }
            for item in production_plan.production_schedule.schedule_items
        ]
    }

    # 发送到MES系统
    response = requests.post(
        "https://mes.example.com/api/production-plans",
        json=mes_payload,
        headers={"Authorization": "Bearer <token>"}
    )
    return response.json()
```

---

## 5. ERP转换

### 5.1 Smart_Manufacturing → ERP转换

**转换函数**：

```text
to_erp: Industry_4_0_Schema → ERP_Format
```

**转换规则**：

```text
to_erp(schema) =
  convert_production_orders(schema.data.production_orders) +
  convert_inventory_data(schema.data.inventory) +
  convert_quality_data(schema.data.quality_data)
```

**转换示例**：

**SAP集成**：

```python
from pyrfc import Connection

class SmartManufacturingToSAP:
    """智能制造到SAP转换器"""

    def __init__(self, sap_config: dict):
        self.conn = Connection(**sap_config)

    def create_production_order(self, order: ProductionOrder):
        """创建SAP生产订单"""
        result = self.conn.call(
            'BAPI_PRODORD_CREATE',
            ORDERID=order.order_id,
            MATERIAL=order.product_id,
            TARGET_QUANTITY=order.quantity,
            START_DATE=order.start_date.isoformat(),
            END_DATE=order.end_date.isoformat()
        )
        return result
```

---

## 6. PostgreSQL存储

### 6.1 数据库Schema设计

```sql
-- 设备表
CREATE TABLE manufacturing_devices (
    device_id VARCHAR(50) PRIMARY KEY,
    device_type VARCHAR(50) NOT NULL,
    factory_id VARCHAR(50),
    line_id VARCHAR(50),
    station_id VARCHAR(50),
    device_status JSONB,
    device_capabilities JSONB,
    communication_config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_devices_factory_id ON manufacturing_devices(factory_id);
CREATE INDEX idx_devices_type ON manufacturing_devices(device_type);

-- 生产订单表
CREATE TABLE production_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(20),
    priority VARCHAR(20),
    assigned_line VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_status ON production_orders(status);
CREATE INDEX idx_orders_dates ON production_orders(start_date, end_date);

-- 生产进度表
CREATE TABLE production_progress (
    progress_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES production_orders(order_id),
    completed_quantity INTEGER DEFAULT 0,
    progress_percentage FLOAT @range(0, 100),
    current_station VARCHAR(50),
    estimated_completion TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 质量检验表
CREATE TABLE quality_inspections (
    inspection_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES production_orders(order_id),
    product_id VARCHAR(50),
    inspection_type VARCHAR(50),
    inspection_date TIMESTAMP,
    inspector VARCHAR(100),
    results JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 预测维护表
CREATE TABLE predictive_maintenance (
    maintenance_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES manufacturing_devices(device_id),
    prediction_date TIMESTAMP,
    predicted_failure_date TIMESTAMP,
    remaining_useful_life INTERVAL,
    failure_probability FLOAT @range(0, 1),
    confidence FLOAT @range(0, 1),
    maintenance_task_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_predictive_maintenance_device_id
  ON predictive_maintenance(device_id);
CREATE INDEX idx_predictive_maintenance_prediction_date
  ON predictive_maintenance(prediction_date);

-- 维护任务表
CREATE TABLE maintenance_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES manufacturing_devices(device_id),
    task_type VARCHAR(50),
    scheduled_date TIMESTAMP,
    estimated_duration INTERVAL,
    estimated_cost JSONB,
    status VARCHAR(20),
    assigned_technician VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 数据存储示例

**存储生产订单**：

```sql
INSERT INTO production_orders (
    order_id, product_id, quantity, start_date, end_date,
    status, priority, assigned_line
)
VALUES (
    'ORDER_001',
    'PROD_001',
    1000,
    '2024-01-22 08:00:00',
    '2024-01-22 16:00:00',
    'in_progress',
    'high',
    'LINE_001'
);

-- 存储生产进度
INSERT INTO production_progress (
    order_id, completed_quantity, progress_percentage,
    current_station, estimated_completion
)
VALUES (
    'ORDER_001',
    750,
    75.0,
    'STATION_003',
    '2024-01-22 14:00:00'
);
```

---

## 7. 转换工具

### 7.1 开源工具

**OPC UA工具**：

- **opcua-asyncio**：Python OPC UA库
- **node-opcua**：Node.js OPC UA库
- **UA-.NETStandard**：.NET OPC UA库

**MES工具**：

- **MES API客户端**：各MES系统提供的API
- **REST API**：标准REST接口

**ERP工具**：

- **pyrfc**：Python SAP RFC库
- **ERP API**：各ERP系统提供的API

### 7.2 自定义转换器

**转换器实现**：

```python
class SmartManufacturingTransformer:
    def to_opcua(self, schema: SmartManufacturingSchema) -> str:
        """转换为OPC UA格式"""
        # 构建OPC UA节点集
        nodeset = self.build_opcua_nodeset(schema)
        return nodeset.to_xml()

    def to_mes(self, schema: DigitalFactorySchema) -> dict:
        """转换为MES格式"""
        mes_data = {
            'production_plan': self.convert_production_plan(
                schema.production_plan
            ),
            'quality_control': self.convert_quality_control(
                schema.quality_control
            )
        }
        return mes_data

    def to_erp(self, schema: Industry4_0Schema) -> dict:
        """转换为ERP格式"""
        erp_data = {
            'production_orders': [
                self.convert_production_order(order)
                for order in schema.data.production_orders
            ]
        }
        return erp_data
```

---

## 8. 转换验证

### 8.1 OPC UA验证

**验证方法**：

1. 验证节点集XML语法
2. 验证节点引用完整性
3. 验证数据类型正确性

**验证工具**：

```python
from opcua import ua, Server

def validate_opcua_nodeset(nodeset_xml: str) -> bool:
    """验证OPC UA节点集"""
    try:
        server = Server()
        server.import_xml(nodeset_xml)
        # 验证节点完整性
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False
```

### 8.2 MES数据验证

**验证方法**：

1. 验证生产计划可行性
2. 验证资源分配合理性
3. 验证数据格式正确性

### 8.3 数据一致性验证

**验证方法**：

1. 验证设备状态一致性
2. 验证生产数据一致性
3. 验证质量数据完整性

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
